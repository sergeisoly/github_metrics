#!/bin/bash

declare -a repos=("opencv/opencv" "opencv/cvat" "opencv/open_model_zoo" "opencv/openvino_training_extensions" "opencv/dldt")

for repo in ${repos[@]}; do
    python3 github_metrics.py -repo "$repo"
done