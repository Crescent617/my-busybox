#!/bin/bash

word=$1
if [ -z $word ]; then
    echo "Usage: $0 word"
    exit 1
fi

curl "http://dict.youdao.com/w/eng/$1" | pup '#results-contents' | lynx -stdin -dump | less
