#!/bin/bash
BASE_URL='https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/offer'
usage() {
  echo "Usage: $0 -i <offer_id>" 1>&2
  exit 1
}
iflag=''
OFFER_ID=''
while getopts ':i:' flag; do
  case "${flag}" in
    i) OFFER_ID="${OPTARG}" ;;
    *) usage ;;
  esac
done
if [[ ! -z "${OFFER_ID}" ]]; then
  curl -s -X DELETE $BASE_URL/${OFFER_ID}
fi
