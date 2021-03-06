#!/bin/sh
prettier --parser html --write testing.html
prettier --parser html --write signup.html
prettier --parser html --write admin.html
prettier --parser html --write index.html
prettier --parser html --write photos.html
prettier --parser babel --write assets/js/testing.js
prettier --parser babel --write assets/js/signup.js
prettier --parser babel --write assets/js/admin.js
prettier --parser babel --write assets/js/index.js
