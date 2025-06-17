#!/bin/bash
"""
Create lifecycle rule template, expiring logs by year add 5 years more date to delete logs. 
"""
BUCKET="prd-log-groups-cloudwatch"
OUTPUT="lifecicle_template.txt"
> "$OUTPUT"  # Clear the file before starting

NOW_PLUS_5H=$(date -u -d "+5 hours" +"%Y-%m-%dT%H:%M:%S.000Z")

SERVICES=$(aws s3api list-objects-v2 \
  --bucket "$BUCKET" \
  --prefix "ecs/" \
  --delimiter "/" \
  --query "CommonPrefixes[].Prefix" \
  --output text)

for SERVICE in $SERVICES; do
  YEARS=$(aws s3api list-objects-v2 \
    --bucket "$BUCKET" \
    --prefix "$SERVICE" \
    --delimiter "/" \
    --query "CommonPrefixes[].Prefix" \
    --output text)
  for YEAR_PATH in $YEARS; do
    # Extract year (assumes path like ecs/service/2020/)
    YEAR=$(echo "$YEAR_PATH" | awk -F'/' '{print $(NF-1)}')
    if [[ "$YEAR" =~ ^[0-9]{4}$ ]]; then
      if (( YEAR <= 2020 )); then
        EXPIRATION_DATE="$NOW_PLUS_5H"
      else
        EXPIRATION_YEAR=$((YEAR + 5))
        EXPIRATION_DATE="${EXPIRATION_YEAR}-12-31T23:59:59.000Z"
      fi
      cat <<EOF >> "$OUTPUT"
{
  "ID": "expire-$YEAR_PATH",
  "Prefix": "$YEAR_PATH",
  "Status": "Enabled",
  "Expiration": {
    "Date": "$EXPIRATION_DATE"
  }
},
EOF
    fi
  done
done
