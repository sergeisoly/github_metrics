#!/bin/bash
# Script runs github_metrics.py for opencv repos
# needs every time to enter login and password


declare -a repos=("opencv/cvat" "opencv/open_model_zoo" "opencv/openvino_training_extensions" "opencv/dldt" "opencv/opencv")

for repo in ${repos[@]}; do
    python3 github_metrics.py -repo "$repo"
done