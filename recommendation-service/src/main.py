#!/usr/bin/env python3
"""
Product Recommendation Service - Main CLI
Usage: python main.py --source oltp --batch-size 100
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from recommendation_engine.database_connector import DatabaseConnector
from recommendation_engine.feature_calculator import FeatureCalculator
from recommendation_engine.recommendation_generator import RecommendationGenerator
from recommendation_engine.batch_processor import BatchProcessor
from config.config import DEFAULT_BATCH_SIZE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("recommendation_service.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description='Product Recommendation Service')
    parser.add_argument('--source', choices=['oltp', 'dw'], default='oltp', 
                       help='Database source (default: oltp)')
    parser.add_argument('--batch-size', type=int, default=DEFAULT_BATCH_SIZE,
                       help=f'Batch size for processing (default: {DEFAULT_BATCH_SIZE})')
    parser.add_argument('--limit', type=int, 
                       help='Limit number of members to process (for testing)')
    parser.add_argument('--output-dir', default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--member-id', type=int,
                       help='Process single member (overrides batch processing)')
    
    args = parser.parse_args()
    
    # Initialize database connection
    db = DatabaseConnector()
    if not db.connect(args.source):
        logger.error("Failed to connect to database")
        sys.exit(1)
    
    try:
        if args.member_id:
            # Single member processing
            logger.info(f"Processing single member: {args.member_id}")
            
            feature_calc = FeatureCalculator(db)
            rec_gen = RecommendationGenerator(db)
            
            features = feature_calc.calculate_member_features(args.member_id)
            if features:
                recommendations = rec_gen.generate_recommendations(features)
                
                print("\n" + "="*60)
                print(f"RECOMMENDATIONS FOR MEMBER {args.member_id}")
                print("="*60)
                print(f"Annual Income: ${features['annual_income']:,.0f}")
                print(f"Credit Score: {features['credit_score']}")
                print(f"Health Score: {features['health_score']:.1f}")
                print(f"Risk Category: {features['risk_category']}")
                print(f"Utilization Ratio: {features['utilization_ratio']:.1%}")
                
                print(f"\n🎯 TOP {len(recommendations)} PRODUCT RECOMMENDATIONS:")
                for rec in recommendations:
                    status = "✅ ELIGIBLE" if rec['eligible'] else "❌ NOT ELIGIBLE"
                    print(f"\n{rec['rank']}. {rec['product_name']} ({status})")
                    print(f"   Product Type: {rec['product_type']}")
                    print(f"   Score: {rec['score']}/100")
                    print(f"   Confidence: {rec['probability']:.1%}")
                    print(f"   Reason: {rec['reasons']}")
            else:
                logger.error(f"Could not process member {args.member_id}")
        else:
            # Batch processing
            feature_calc = FeatureCalculator(db)
            rec_gen = RecommendationGenerator(db)
            processor = BatchProcessor(db, feature_calc, rec_gen, args.output_dir)
            processor.run_batch_processing(args.batch_size, args.limit)
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
