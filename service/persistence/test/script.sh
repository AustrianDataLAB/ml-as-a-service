#!/bin/sh

test_file="./data/corki.webp"
tmp_dir="./tmp"
tmp_file="./tmp/file"
SEP="==============================================="

echo "testing post"
curl -X POST -H "Authorization: $AUTH_TOKEN" -F "file=@$test_file" $PERSISTENCE_SERVICE_URL/data
mkdir -p $tmp_dir
echo "testing get"
curl -o $tmp_file -H "Authorization: $AUTH_TOKEN" $PERSISTENCE_SERVICE_URL/data

if diff $tmp_file $test_file > /dev/null; then
    echo "$SEP"
    echo "Files are the same - test successful"
    echo "Removing temporary files"
    echo "$SEP"
    rm -rf $tmp_dir
else
    echo "$SEP"
    echo "Files are different"
    echo "Temporary files won't be removed"
    echo "$SEP"
fi
