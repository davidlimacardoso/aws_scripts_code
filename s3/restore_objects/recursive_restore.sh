#!/bin/bash
# Defina as variáveis
BUCKET="mongo-atlas-backups"
PREFIX="exported_snapshots/5aeb8f4896e821xxxxxxxxx/60bee66bf642ffxxxxxxxx/statement/2025-04-22T1603/1745349654/"

# Liste os objetos e inicie a restauração
aws s3api list-objects-v2 \
    --bucket "$BUCKET" \
    --prefix "$PREFIX" \
    --query "Contents[].Key" \
    --output text | tr '\t' '\n' | while read file; do
        aws s3api restore-object \
            --bucket "$BUCKET" \
            --key "$file" \
            --restore-request '{"Days":1,"GlacierJobParameters":{"Tier":"Standard"}}'
done
