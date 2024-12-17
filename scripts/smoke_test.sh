#! /bin/sh
# This script is to smoke test that the sample app works, it needs to be run after some data has been seeded
# (see setup.sh).
set -e

ENDPOINT="http://localhost:5000"
ACCEPT="Accept: application/json"
CONTENT="Content-Type: application/json"


PAGE_ONE=`curl --silent -H "$ACCEPT" -H "$CONTENT" \
    --retry-all-errors \
    --connect-timeout 5 \
    --max-time 10 \
    --retry 5 \
    --retry-delay 10 \
    --retry-max-time 60 \
    "$ENDPOINT/products?pageSize=3"`

AFTER=`echo $PAGE_ONE | jq '.next' -r`

echo $AFTER

CUSTOMER_ID=`curl --silent -H "$ACCEPT" -H "$CONTENT" "$ENDPOINT/customers/fake%40fauna.com?key=email" | jq '.id' -r`

curl --silent -H "$ACCEPT" -H "$CONTENT" -X POST "$ENDPOINT/customers/$CUSTOMER_ID/cart"

