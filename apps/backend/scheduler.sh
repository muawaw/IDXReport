#!/bin/bash
# run_all_chunks.sh

# CHANGE ALL THE PATH WHEN ON PRODUCTION
VENV_PYTHON="/path/to/your/.venv/bin/python"
MANAGE_PY="/path/to/your/django/manage.py"
CSV_PATH="/path/to/your/django/api/management/commands/list_idx.csv"

LIMIT=50

# Dynamically calculate total rows (subtract 1 for header row)
TOTAL_LINES=$(wc -l < "$CSV_PATH")
TOTAL_STOCKS=$((TOTAL_LINES - 1))

echo "Total stocks detected in CSV: $TOTAL_STOCKS"

# Loop sequentially through offset chunks
for (( offset=0; offset<TOTAL_STOCKS; offset+=LIMIT ))
do
    echo "Processing chunk: Offset $offset, Limit $LIMIT..."
    $VENV_PYTHON $MANAGE_PY get_stocks --offset $offset --limit $LIMIT --delay 1.5
    
    # Pause between chunks to allow LVE CPU/Memory limits to reset
    sleep 15
done