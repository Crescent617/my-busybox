#!/bin/bash

word=$1

if [ -z "$word" ]; then
    echo "Usage: $0 word"
    exit 1
fi

escaped_word=$(echo $word | sed 's/ /%20/g')

res=$(curl "http://dict.youdao.com/w/eng/$escaped_word" 2>/dev/null | pup '#phrsListTab' 'text{}')

# join lines and replace multiple spaces with one space
res=$(echo "$res" | tr '\n' ' ' | sed 's/ \+/ /g')
echo "$res"
