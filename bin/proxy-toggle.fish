#!/usr/bin/env fish

set default_proxy 'http://localhost:7890'
set proxy (set -q MY_PROXY; and echo $MY_PROXY; or echo $default_proxy)

if set -q http_proxy
    echo 'disable http_proxy'
    set -e http_proxy
    set -e https_proxy
    set -e no_proxy

    set -e HTTP_PROXY
    set -e HTTPS_PROXY
    set -e NO_PROXY
else
    echo 'enable http_proxy'

    set -gx http_proxy $proxy
    set -gx https_proxy $proxy
    set -gx no_proxy 'localhost, 127.0.0.1, ::1'

    set -gx HTTP_PROXY $proxy
    set -gx HTTPS_PROXY $proxy
    set -gx NO_PROXY 'localhost, 127.0.0.1, ::1'
end
