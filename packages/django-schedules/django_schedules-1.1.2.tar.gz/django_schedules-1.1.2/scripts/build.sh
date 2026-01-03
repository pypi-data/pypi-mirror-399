#!/bin/bash

set -euxo pipefail

cd "$(dirname "$0")/.."

uv build

# strip non-deterministic things
strip-nondeterminism ./dist/*
for f in ./dist/*.tar.gz; do
    tmp=$(mktemp -d)

    tar -xzf "${f}" --directory="${tmp}"

    root=$(basename "${f/.tar.gz/}")

    rm "${f}"

    tar \
        --sort=name \
        --owner=root:0 \
        --group=root:0 \
        --mtime='UTC 2019-01-01' \
        -czf "${f}" \
        --directory="${tmp}" \
        "${root}"

    rm -rf "$tmp"
done

if [ "$1" == "--publish" ]; then
    # see uv config in pyproject.toml
    uv publish --username=__token__
    read -p "Have you commited everything before we tag the commit?"
    VERSION=$(uv version --short)
    git tag -m "${VERSION}" "${VERSION}"
fi
