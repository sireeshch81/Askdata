#!/usr/bin/env python

import logging
import argparse
from datetime import datetime
import sys

# Import database connections
from database import get_oltp_session, get_dw_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run a specific ETL job")
    parser.add_argument(
        "job",
        choices=["members", "credit_cards", "payment_history", "financial_health", "financial_products"],
        help="Specify which ETL job to run"
    )

    args = parser.parse_args()

    # Get database sessions
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()

    # Import the specific ETL job
    if args.job == "members":
        from etl_jobs.member_etl import extract_members, transform_members, load_members
        from etl_jobs.etl_manager import get_last_processed_id, update_tracking_record

        logger.info(f"Starting members ETL job")

        # Get last processed ID
        last_id = get_last_processed_id(dw_session, "members", "members")

        # Run ETL
        extracted_data = extract_members(oltp_session, last_id)
        if extracted_data:
            transformed_data = transform_members(extracted_data)
            records_loaded = load_members(dw_session, transformed_data)

            # Update tracking
            if records_loaded > 0:
                max_id = max(item["member_id"] for item in extracted_data)
                update_tracking_record(dw_session, "members", "members", max_id, records_loaded, "success")

            logger.info(f"Processed {records_loaded} records")
        else:
            logger.info("No new data to process")

    elif args.job == "credit_cards":
        # Similar pattern for other jobs
        from etl_jobs.credit_card_etl import extract_credit_cards, transform_credit_cards, load_credit_cards
        from etl_jobs.etl_manager import get_last_processed_id, update_tracking_record

        # Implementation follows the same pattern as members
        pass

    # Close sessions
    oltp_session.close()
    dw_session.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
