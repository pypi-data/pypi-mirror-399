#!/usr/bin/env bash

cat >> ~/.bashrc <<EOT

### BEGIN devcontainer postCreate.sh
. ./.venv/bin/activate
### END devcontainer postCreate.sh

EOT

(
    set -x
    pip cache purge >/dev/null 2>&1
    pip install --upgrade pip setuptools -q
    pip install --upgrade uv
    uv venv --clear .venv
    uv sync --active --all-groups --link-mode=copy
)