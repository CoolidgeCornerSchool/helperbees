#!/bin/bash
#USER_ID=$1
BASE_URL='https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/user'
usage() {
  echo "Usage: $0 -i <user_id>" 1>&2
  exit 1
}
iflag=''
USER_ID=''
while getopts ':i:' flag; do
  case "${flag}" in
    i) USER_ID="${OPTARG}" ;;
    *) usage ;;
  esac
done
if [[ ! -z "${USER_ID}" ]]; then
  curl -s $BASE_URL/${USER_ID}
fi
