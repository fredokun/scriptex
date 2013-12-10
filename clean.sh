#! /bin/sh

echo "Removing temporary files"
find ./ -name "*~" -exec rm -f {} \;

echo "Removing python cache"
find ./ -name "__pycache__" -exec rm -rf {} \;

