#!/bin/bash -x
#curl https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/offers -X POST --upload-file offer.json
curl https://pxa9qyui26.execute-api.us-east-1.amazonaws.com/dev/offer_and_user -X POST --upload-file offer.json
