#!/bin/bash

word=$1

if [ -z "$word" ]; then
    echo "Usage: $0 word"
    exit 1
fi

escaped_word=$(echo $word | sed 's/ /%20/g')
curl "http://dict.youdao.com/w/eng/$escaped_word" 2>/dev/null | pup '#results-contents' | lynx -stdin -dump | less
