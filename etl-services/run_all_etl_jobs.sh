#!/bin/bash

# Run all ETL jobs for AskData
echo "Starting ETL jobs at $(date)"

python main.py --jobs all

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "ETL jobs completed successfully at $(date)"
else
  echo "ETL jobs failed with exit code $EXIT_CODE at $(date)"
fi

exit $EXIT_CODE
