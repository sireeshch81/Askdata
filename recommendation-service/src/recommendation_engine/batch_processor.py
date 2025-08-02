"""
Batch Processor - Handles batch processing of recommendations
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Handles batch processing of recommendations"""
    
    def __init__(self, db_connector, feature_calculator, recommendation_generator, output_dir: str = "output"):
        self.db = db_connector
        self.feature_calculator = feature_calculator
        self.recommendation_generator = recommendation_generator
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def get_member_ids(self, limit: int = None) -> List[int]:
        """Get list of all member IDs"""
        query = "SELECT member_id FROM members WHERE member_status = 'active' ORDER BY member_id"
        if limit:
            query += f" LIMIT {limit}"
        
        df = self.db.execute_query(query)
        return df['member_id'].tolist()
    
    def process_batch(self, member_ids: List[int], batch_number: int) -> Tuple[List[Dict], List[Dict]]:
        """Process a batch of members"""
        successful_recommendations = []
        failed_members = []
        
        logger.info(f"Processing batch {batch_number}: members {member_ids[0]}-{member_ids[-1]} ({len(member_ids)} members)")
        
        for i, member_id in enumerate(member_ids, 1):
            try:
                # Calculate features
                features = self.feature_calculator.calculate_member_features(member_id)
                
                if not features:
                    failed_members.append({
                        'member_id': member_id,
                        'error_type': 'insufficient_data',
                        'message': 'Could not calculate member features'
                    })
                    continue
                
                # Generate recommendations
                recommendations = self.recommendation_generator.generate_recommendations(features)
                
                if not recommendations:
                    failed_members.append({
                        'member_id': member_id,
                        'error_type': 'no_recommendations',
                        'message': 'No suitable products found'
                    })
                    continue
                
                # Create member recommendation record
                member_record = {
                    'member_id': member_id,
                    'member_info': {
                        'annual_income': features['annual_income'],
                        'credit_score': features['credit_score'],
                        'health_score': features['health_score'],
                        'risk_category': features['risk_category'],
                        'utilization_ratio': features['utilization_ratio']
                    },
                    'recommendations': recommendations,
                    'processing_metadata': {
                        'recommendation_method': 'Rule-based recommendations',
                        'generated_date': datetime.now().isoformat(),
                        'algorithm_version': 'v1.0',
                        'batch_number': batch_number
                    }
                }
                
                successful_recommendations.append(member_record)
                
                # Progress update
                if i % 10 == 0:
                    logger.info(f"  Batch {batch_number}: {i}/{len(member_ids)} members processed")
                    
            except Exception as e:
                logger.error(f"Error processing member {member_id}: {e}")
                failed_members.append({
                    'member_id': member_id,
                    'error_type': 'processing_error',
                    'message': str(e)
                })
        
        logger.info(f"Batch {batch_number} completed: {len(successful_recommendations)} successful, {len(failed_members)} failed")
        return successful_recommendations, failed_members
    
    def run_batch_processing(self, batch_size: int = 100, limit: int = None):
        """Run complete batch processing"""
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y_%m_%d_%H_%M_%S")
        
        logger.info("🚀 Starting Product Recommendation Batch Processing")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Get all member IDs
        member_ids = self.get_member_ids(limit)
        total_members = len(member_ids)
        total_batches = (total_members + batch_size - 1) // batch_size
        
        logger.info(f"Processing {total_members} members in {total_batches} batches")
        
        all_recommendations = []
        all_failed = []
        
        # Process in batches
        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * batch_size
            end_idx = min(start_idx + batch_size, total_members)
            batch_member_ids = member_ids[start_idx:end_idx]
            
            # Process batch
            batch_recommendations, batch_failed = self.process_batch(batch_member_ids, batch_num)
            
            all_recommendations.extend(batch_recommendations)
            all_failed.extend(batch_failed)
            
            # Update progress file
            self._update_progress(batch_num, total_batches, len(all_recommendations), len(all_failed), total_members)
        
        # Save results
        self._save_results(all_recommendations, all_failed, timestamp, start_time)
        
        logger.info("✅ Batch processing completed successfully!")
    
    def _update_progress(self, current_batch: int, total_batches: int, successful: int, failed: int, total_members: int):
        """Update progress file"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'status': 'RUNNING' if current_batch < total_batches else 'COMPLETED',
            'current_batch': f"{current_batch}/{total_batches}",
            'members_processed': f"{successful + failed}/{total_members}",
            'success_rate': f"{successful/(successful + failed)*100:.1f}%" if (successful + failed) > 0 else "0%",
            'successful_recommendations': successful,
            'failed_members': failed
        }
        
        with open(os.path.join(self.output_dir, 'progress.json'), 'w') as f:
            json.dump(progress, f, indent=2)
    
    def _save_results(self, recommendations: List[Dict], failed: List[Dict], timestamp: str, start_time: datetime):
        """Save all results to files"""
        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds()
        
        # Save successful recommendations
        if recommendations:
            rec_file = os.path.join(self.output_dir, f'recommendations_{timestamp}.json')
            with open(rec_file, 'w') as f:
                json.dump(recommendations, f, indent=2)
            logger.info(f"✅ Saved {len(recommendations)} recommendations to {rec_file}")
        
        # Save failed members
        if failed:
            failed_file = os.path.join(self.output_dir, f'failed_members_{timestamp}.json')
            with open(failed_file, 'w') as f:
                json.dump(failed, f, indent=2)
            logger.info(f"⚠️  Saved {len(failed)} failed members to {failed_file}")
        
        # Save summary
        summary = {
            'run_metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'runtime_seconds': runtime,
                'algorithm_version': 'v1.0'
            },
            'statistics': {
                'total_members_processed': len(recommendations) + len(failed),
                'successful_recommendations': len(recommendations),
                'failed_members': len(failed),
                'success_rate': f"{len(recommendations)/(len(recommendations)+len(failed))*100:.1f}%" if (len(recommendations)+len(failed)) > 0 else "0%",
                'avg_processing_time_per_member_ms': round((runtime * 1000) / (len(recommendations) + len(failed)), 2) if (len(recommendations)+len(failed)) > 0 else 0
            },
            'failure_analysis': self._analyze_failures(failed)
        }
        
        summary_file = os.path.join(self.output_dir, f'processing_summary_{timestamp}.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"📊 Saved processing summary to {summary_file}")
    
    def _analyze_failures(self, failed: List[Dict]) -> Dict:
        """Analyze failure patterns"""
        if not failed:
            return {}
        
        failure_types = {}
        for failure in failed:
            error_type = failure.get('error_type', 'unknown')
            failure_types[error_type] = failure_types.get(error_type, 0) + 1
        
        return failure_types
