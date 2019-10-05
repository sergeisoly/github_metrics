#!/bin/bash

repos=('opencv/opencv' 'opencv/CVAT' 'opencv/open_model_zoo' 'opencv/openvino_training_extensions' 'opencv/dldt')

for repo in in "${repos[@]}"; do
    python github_metrics.py -repo "$repo" 
done