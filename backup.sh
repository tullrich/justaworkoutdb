#!/bin/bash

scp wwwhost@fitness.tullrich.com:/tmp/justaworkout.db ./backup/justaworkout.db
cp ./backup/justaworkout.db ./backup/justaworkout$(date "+_%Y_%m_%d.db")