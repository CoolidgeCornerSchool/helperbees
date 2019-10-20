#!/bin/bash
BASE_URL='https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/user'
usage() {
  echo "Usage: $0 -a" 1>&2
  exit 1
}
aflag=''
while getopts 'a' flag; do
  case "${flag}" in
    a) aflag='true' ;;
    *) usage ;;
  esac
done
if [[ ! -z "${aflag}" ]]; then
  for i in `util/kid-ids.sh`; do
    echo "deleting $i"
    curl -X DELETE $BASE_URL/$i
  done
fi
