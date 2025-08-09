#!/usr/bin/env python3
"""
ML Batch Runner - Main orchestrator for ML-based recommendation processing
Usage: python ml_batch_runner.py [options]
"""

import argparse
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Handle both relative and absolute imports
try:
    from .database_connector import DatabaseConnector
    from .ml_mongodb_loader import MLMongoDBLoader
except ImportError:
    # Fallback for direct execution
    from database_connector import DatabaseConnector
    from ml_mongodb_loader import MLMongoDBLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'ml_batch_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

class MLBatchRunner:
    """Main orchestrator for ML recommendation batch processing"""
    
    def __init__(self):
        self.db_connector = None
        self.ml_loader = None
        
    def setup_connections(self, mongo_config: Dict[str, Any]) -> bool:
        """Setup database connections"""
        try:
            # Initialize database connector
            self.db_connector = DatabaseConnector()
            
            # Test DW connection
            if not self.db_connector.connect('dw'):
                logger.error("Failed to connect to Data Warehouse")
                return False
            
            # Initialize ML MongoDB loader
            self.ml_loader = MLMongoDBLoader(
                db_connector=self.db_connector,
                mongo_host=mongo_config.get('host', 'localhost'),
                mongo_port=mongo_config.get('port', 27017),
                mongo_database=mongo_config.get('database', 'askdata_mongo'),
                mongo_username=mongo_config.get('username'),
                mongo_password=mongo_config.get('password')
            )
            
            logger.info("✅ Database connections established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup connections: {e}")
            return False
    
    def run_full_pipeline(self, 
                         limit_customers: int = None,
                         skip_existing: bool = True,
                         ml_sample_size: int = 5000) -> Dict[str, Any]:
        """Run the complete ML recommendation pipeline"""
        
        pipeline_start = time.time()
        logger.info("🚀 Starting ML Recommendation Pipeline")
        
        try:
            # Step 1: Setup ML Model
            logger.info("📊 Step 1: Building ML similarity model...")
            if not self.ml_loader.setup_ml_model(sample_size=ml_sample_size):
                return {"error": "Failed to setup ML model", "step": "ml_model_setup"}
            
            # Step 2: Run batch processing
            logger.info("⚙️ Step 2: Running batch processing...")
            processing_results = self.ml_loader.run_batch_processing(
                limit_customers=limit_customers,
                skip_existing=skip_existing
            )
            
            # Step 3: Get final statistics
            logger.info("📈 Step 3: Collecting final statistics...")
            final_stats = self.ml_loader.get_processing_stats()
            
            # Calculate total pipeline time
            total_time = time.time() - pipeline_start
            
            # Combine results
            results = {
                "pipeline_status": "completed",
                "total_pipeline_time": round(total_time, 2),
                "processing_results": processing_results,
                "final_statistics": final_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ ML Pipeline completed in {total_time:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return {
                "pipeline_status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_incremental_update(self, customer_ids: list = None) -> Dict[str, Any]:
        """Run incremental update for specific customers"""
        try:
            if not customer_ids:
                logger.warning("No customer IDs provided for incremental update")
                return {"error": "No customer IDs provided"}
            
            logger.info(f"🔄 Running incremental update for {len(customer_ids)} customers")
            
            # Ensure ML model is ready
            if not self.ml_loader.ml_generator._models_ready():
                logger.info("ML model not ready, building...")
                if not self.ml_loader.setup_ml_model():
                    return {"error": "Failed to setup ML model"}
            
            # Process each customer
            results = []
            successful = 0
            failed = 0
            
            for customer_id in customer_ids:
                result = self.ml_loader.update_single_customer(customer_id)
                if result:
                    results.append(result)
                    successful += 1
                else:
                    failed += 1
            
            return {
                "update_status": "completed",
                "total_customers": len(customer_ids),
                "successful": successful,
                "failed": failed,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Incremental update failed: {e}")
            return {"error": str(e)}
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old recommendation data"""
        try:
            logger.info(f"🧹 Cleaning up recommendations older than {days_old} days")
            
            cleanup_results = self.ml_loader.cleanup_old_recommendations(days_old)
            
            logger.info(f"✅ Cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "connections": {
                    "dw_connected": self.db_connector.current_source == 'dw' if self.db_connector else False,
                    "mongo_connected": hasattr(self.db_connector, 'mongo_db') and self.db_connector.mongo_db is not None if self.db_connector else False
                }
            }
            
            # Get ML model status
            if self.ml_loader:
                ml_stats = self.ml_loader.ml_generator.get_model_stats()
                status["ml_model"] = ml_stats
                
                # Get processing statistics
                processing_stats = self.ml_loader.get_processing_stats()
                status["processing_stats"] = processing_stats
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    def close_connections(self):
        """Close all database connections"""
        if self.db_connector:
            self.db_connector.close()
            logger.info("Database connections closed")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='ML Recommendation Batch Processing')
    
    parser.add_argument('--mode', 
                       choices=['full', 'incremental', 'cleanup', 'status'], 
                       default='full',
                       help='Processing mode (default: full)')
    
    parser.add_argument('--limit', 
                       type=int, 
                       help='Limit number of customers to process')
    
    parser.add_argument('--skip-existing', 
                       action='store_true', 
                       default=True,
                       help='Skip customers with existing recommendations')
    
    parser.add_argument('--ml-sample-size', 
                       type=int, 
                       default=5000,
                       help='Sample size for ML model training (default: 5000)')
    
    parser.add_argument('--customer-ids', 
                       nargs='+',
                       help='Specific customer IDs for incremental update')
    
    parser.add_argument('--cleanup-days', 
                       type=int, 
                       default=30,
                       help='Days old for cleanup (default: 30)')
    
    # MongoDB configuration
    parser.add_argument('--mongo-host', 
                       default='localhost',
                       help='MongoDB host (default: localhost)')
    
    parser.add_argument('--mongo-port', 
                       type=int, 
                       default=27017,
                       help='MongoDB port (default: 27017)')
    
    parser.add_argument('--mongo-database', 
                       default='askdata_mongo',
                       help='MongoDB database (default: askdata_mongo)')
    
    parser.add_argument('--mongo-username',
                       help='MongoDB username')
    
    parser.add_argument('--mongo-password',
                       help='MongoDB password')
    
    return parser.parse_args()

def main():
    """Main execution function"""
    args = parse_arguments()
    
    logger.info(f"Starting ML Batch Runner in {args.mode} mode")
    
    # Initialize runner
    runner = MLBatchRunner()
    
    try:
        # Setup connections
        mongo_config = {
            'host': args.mongo_host,
            'port': args.mongo_port,
            'database': args.mongo_database,
            'username': args.mongo_username,
            'password': args.mongo_password
        }
        
        if not runner.setup_connections(mongo_config):
            sys.exit(1)
        
        # Execute based on mode
        if args.mode == 'full':
            results = runner.run_full_pipeline(
                limit_customers=args.limit,
                skip_existing=args.skip_existing,
                ml_sample_size=args.ml_sample_size
            )
            
        elif args.mode == 'incremental':
            results = runner.run_incremental_update(args.customer_ids)
            
        elif args.mode == 'cleanup':
            results = runner.cleanup_old_data(args.cleanup_days)
            
        elif args.mode == 'status':
            results = runner.get_system_status()
        
        # Print results
        print("\n" + "="*60)
        print("EXECUTION RESULTS")
        print("="*60)
        
        for key, value in results.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
        
        print("="*60)
        
        # Exit with appropriate code
        if "error" in results:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        runner.close_connections()

if __name__ == "__main__":
    main()
