import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from pymongo.errors import BulkWriteError

from .database_connector import DatabaseConnector
from .ml_recommendation_generator import MLRecommendationGenerator

logger = logging.getLogger(__name__)

class MLMongoDBLoader:
    """Batch processing service to load ML recommendations from DW to MongoDB"""
    
    def __init__(self, 
                 db_connector: DatabaseConnector,
                 mongo_host: str = "localhost",
                 mongo_port: int = 27017,
                 mongo_database: str = "askdata_mongo",
                 mongo_username: str = None,
                 mongo_password: str = None):
        
        self.db = db_connector
        self.ml_generator = MLRecommendationGenerator(db_connector)
        
        # MongoDB connection parameters
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.mongo_database = mongo_database
        self.mongo_username = mongo_username
        self.mongo_password = mongo_password
        
        # Processing configuration
        self.batch_size = 100
        self.max_workers = 4
        self.collection_name = "ml_recommendations"  # Separate from rule-based
        
        # Progress tracking
        self.processed_count = 0
        self.failed_count = 0
        self.lock = threading.Lock()
        
    def setup_ml_model(self, sample_size: int = 5000) -> bool:
        """Setup and train the ML recommendation model"""
        logger.info("Setting up ML recommendation model...")
        
        success = self.ml_generator.build_similarity_model(sample_size)
        if success:
            stats = self.ml_generator.get_model_stats()
            logger.info(f"ML Model ready: {stats}")
        
        return success
    
    def run_batch_processing(self, 
                           limit_customers: Optional[int] = None,
                           skip_existing: bool = True) -> Dict:
        """Run complete batch processing pipeline"""
        
        start_time = time.time()
        logger.info("🚀 Starting ML batch processing pipeline...")
        
        try:
            # 1. Connect to MongoDB
            if not self._connect_mongodb():
                return {"error": "Failed to connect to MongoDB"}
            
            # 2. Setup ML model if not already done
            if not self.ml_generator._models_ready():
                logger.info("ML model not ready, building...")
                if not self.setup_ml_model():
                    return {"error": "Failed to setup ML model"}
            
            # 3. Get customer list for processing
            customers_to_process = self._get_customers_for_processing(
                limit_customers, skip_existing
            )
            
            if not customers_to_process:
                return {"error": "No customers to process"}
            
            logger.info(f"Processing {len(customers_to_process)} customers...")
            
            # 4. Process in parallel batches
            results = self._process_customers_parallel(customers_to_process)
            
            # 5. Create indexes for performance
            self._create_mongodb_indexes()
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Return summary
            summary = {
                "total_customers": len(customers_to_process),
                "successfully_processed": self.processed_count,
                "failed": self.failed_count,
                "processing_time_seconds": round(processing_time, 2),
                "customers_per_second": round(len(customers_to_process) / processing_time, 2),
                "collection": self.collection_name,
                "ml_model_stats": self.ml_generator.get_model_stats()
            }
            
            logger.info(f"✅ Batch processing completed: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return {"error": str(e)}
        
        finally:
            self.db.close_mongodb()
    
    def _connect_mongodb(self) -> bool:
        """Connect to MongoDB for batch loading"""
        return self.db.connect_mongodb(
            host=self.mongo_host,
            port=self.mongo_port,
            database=self.mongo_database,
            username=self.mongo_username,
            password=self.mongo_password
        )
    
    def _get_customers_for_processing(self, 
                                    limit: Optional[int], 
                                    skip_existing: bool) -> List[str]:
        """Get list of customer IDs to process"""
        
        # Ensure DW connection
        if self.db.current_source != 'dw':
            self.db.connect('dw')
        
        # Get total customer count
        total_customers = self.db.get_dw_customer_count()
        logger.info(f"Total active customers in DW: {total_customers}")
        
        # Get customers in batches
        customers = []
        offset = 0
        batch_size = 1000
        
        while len(customers) < (limit or total_customers):
            batch_df = self.db.get_dw_batch_customers(batch_size, offset)
            
            if batch_df.empty:
                break
            
            batch_customers = batch_df['customer_id'].tolist()
            
            # Filter existing if requested
            if skip_existing:
                batch_customers = self._filter_existing_customers(batch_customers)
            
            customers.extend(batch_customers)
            offset += batch_size
            
            # Respect limit
            if limit and len(customers) >= limit:
                customers = customers[:limit]
                break
        
        return customers
    
    def _filter_existing_customers(self, customer_ids: List[str]) -> List[str]:
        """Filter out customers who already have ML recommendations"""
        try:
            collection = self.db.get_mongo_collection(self.collection_name)
            
            # Find existing customer IDs
            existing_customers = collection.find(
                {"customer_id": {"$in": customer_ids}},
                {"customer_id": 1}
            )
            
            existing_ids = {doc["customer_id"] for doc in existing_customers}
            
            # Return only customers without existing recommendations
            filtered = [cid for cid in customer_ids if cid not in existing_ids]
            
            logger.info(f"Filtered {len(customer_ids) - len(filtered)} existing customers")
            return filtered
            
        except Exception as e:
            logger.warning(f"Error filtering existing customers: {e}")
            return customer_ids  # Return all if filtering fails
    
    def _process_customers_parallel(self, customer_ids: List[str]) -> List[Dict]:
        """Process customers in parallel using ThreadPoolExecutor"""
        
        self.processed_count = 0
        self.failed_count = 0
        
        # Split into batches
        batches = [customer_ids[i:i + self.batch_size] 
                  for i in range(0, len(customer_ids), self.batch_size)]
        
        logger.info(f"Processing {len(batches)} batches with {self.max_workers} workers")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(self._process_customer_batch, batch): batch 
                for batch in batches
            }
            
            # Process completed batches
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                    
                    logger.info(f"Completed batch of {len(batch)} customers. "
                              f"Progress: {self.processed_count}/{len(customer_ids)}")
                    
                except Exception as e:
                    logger.error(f"Batch processing failed: {e}")
                    with self.lock:
                        self.failed_count += len(batch)
        
        return results
    
    def _process_customer_batch(self, customer_ids: List[str]) -> List[Dict]:
        """Process a batch of customers"""
        batch_results = []
        
        for customer_id in customer_ids:
            try:
                # Generate ML recommendation
                recommendation = self.ml_generator.generate_recommendations(customer_id)
                
                if recommendation:
                    # Save to MongoDB
                    if self._save_recommendation_to_mongo(recommendation):
                        batch_results.append(recommendation)
                        
                        with self.lock:
                            self.processed_count += 1
                    else:
                        with self.lock:
                            self.failed_count += 1
                else:
                    logger.warning(f"No recommendation generated for customer {customer_id}")
                    with self.lock:
                        self.failed_count += 1
                        
            except Exception as e:
                logger.error(f"Error processing customer {customer_id}: {e}")
                with self.lock:
                    self.failed_count += 1
        
        return batch_results
    
    def _save_recommendation_to_mongo(self, recommendation: Dict) -> bool:
        """Save individual recommendation to MongoDB"""
        try:
            collection = self.db.get_mongo_collection(self.collection_name)
            
            # Upsert (update if exists, insert if not)
            result = collection.replace_one(
                {"customer_id": recommendation["customer_id"]},
                recommendation,
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving recommendation to MongoDB: {e}")
            return False
    
    def _create_mongodb_indexes(self):
        """Create indexes for optimal query performance"""
        try:
            collection = self.db.get_mongo_collection(self.collection_name)
            
            # Create indexes
            indexes_to_create = [
                ("customer_id", 1),  # Primary lookup
                ("created_at", -1),  # Time-based queries
                ("algorithm_type", 1),  # Algorithm filtering
                ("customer_profile.credit_score", 1),  # Credit score queries
                ("customer_profile.risk_category", 1),  # Risk category queries
                ("recommendations.product_type", 1),  # Product type filtering
                ("recommendations.score", -1)  # Score-based sorting
            ]
            
            for index_spec in indexes_to_create:
                try:
                    collection.create_index([index_spec])
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")
    
    def update_single_customer(self, customer_id: str) -> Optional[Dict]:
        """Update ML recommendations for a single customer"""
        try:
            # Connect to MongoDB if not connected
            if not hasattr(self.db, 'mongo_db') or self.db.mongo_db is None:
                if not self._connect_mongodb():
                    return None
            
            # Ensure ML model is ready
            if not self.ml_generator._models_ready():
                logger.warning("ML model not ready for single customer update")
                return None
            
            # Generate recommendation
            recommendation = self.ml_generator.generate_recommendations(customer_id)
            
            if recommendation:
                # Save to MongoDB
                if self._save_recommendation_to_mongo(recommendation):
                    logger.info(f"Updated ML recommendations for customer {customer_id}")
                    return recommendation
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating single customer {customer_id}: {e}")
            return None
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        try:
            if not hasattr(self.db, 'mongo_db') or self.db.mongo_db is None:
                return {"error": "MongoDB not connected"}
            
            collection = self.db.get_mongo_collection(self.collection_name)
            
            # Count total documents
            total_recommendations = collection.count_documents({})
            
            # Count by algorithm type
            ml_count = collection.count_documents({"algorithm_type": "ml_similarity"})
            
            # Latest update time
            latest_doc = collection.find_one(
                sort=[("created_at", -1)],
                projection={"created_at": 1}
            )
            
            latest_update = latest_doc["created_at"] if latest_doc else None
            
            return {
                "total_ml_recommendations": ml_count,
                "total_recommendations": total_recommendations,
                "latest_update": latest_update,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {"error": str(e)}
    
    def cleanup_old_recommendations(self, days_old: int = 30) -> Dict:
        """Clean up old ML recommendations"""
        try:
            if not hasattr(self.db, 'mongo_db') or self.db.mongo_db is None:
                if not self._connect_mongodb():
                    return {"error": "Could not connect to MongoDB"}
            
            collection = self.db.get_mongo_collection(self.collection_name)
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - pd.Timedelta(days=days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            # Delete old recommendations
            result = collection.delete_many({
                "created_at": {"$lt": cutoff_iso},
                "algorithm_type": "ml_similarity"
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old ML recommendations")
            
            return {
                "deleted_count": result.deleted_count,
                "cutoff_date": cutoff_iso
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old recommendations: {e}")
            return {"error": str(e)}
