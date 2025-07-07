#!/usr/bin/env bash

projects=(
    comma-cli
    # dev-toolbox
    # direct-deps
    k6
    lambda-dev-server
    # log-tool
    # persistent-cache-decorator
    # record-replay-compare
    # runtool
    # typedfzf
    # uv-to-pipfile
    # workflows
)

for project in "${projects[@]}"; do
    project_dir="${HOME}/dev/github.com/FlavioAmurrioCS/$project"
    echo "Processing $project"
    # uv run --script update.py "$project_dir"
    # git -C "$project_dir" pull
    git -C "$project_dir" branch | grep '^\*'
    # echo "${project_dir}"
done
