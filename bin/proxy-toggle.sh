#!/bin/bash

# example: source proxy-toggle.sh

if [[ -n $http_proxy ]]; then
  echo 'disable http_proxy'
  unset http_proxy
  unset https_proxy
  unset no_proxy

  unset HTTP_PROXY
  unset HTTPS_PROXY
  unset NO_PROXY
else
  echo 'enable http_proxy'
  proxy='http://localhost:7890'

  export http_proxy=$proxy
  export https_proxy=$proxy
  export no_proxy="localhost, 127.0.0.1, ::1"

  export HTTP_PROXY=$proxy
  export HTTPS_PROXY=$proxy
  export NO_PROXY="localhost, 127.0.0.1, ::1"
fi
