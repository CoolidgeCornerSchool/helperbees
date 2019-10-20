#!/bin/bash
OUT='assets/images/logotmp.png'
FINAL='assets/images/logo.png'
cat util/piskel/logo.piskel | jq '.piskel.layers[0]' | tr -d '\' | cut -c2-9999 | sed 's/.$//' | jq '.chunks[0].base64PNG' | tr -d '"' | cut -d, -f2 | base64 -d > $OUT
convert -flop $OUT $FINAL
rm $OUT
