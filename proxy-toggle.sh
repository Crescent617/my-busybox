#!/bin/bash

if [[ -n $http_proxy ]]; then
  echo 'disable http_proxy'
  unset http_proxy
  unset https_proxy
  unset no_proxy
else
  echo 'enable http_proxy'
  proxy='http://localhost:7890'
  export http_proxy=$proxy
  export https_proxy=$proxy
  export no_proxy="localhost, 127.0.0.1, ::1"
fi
