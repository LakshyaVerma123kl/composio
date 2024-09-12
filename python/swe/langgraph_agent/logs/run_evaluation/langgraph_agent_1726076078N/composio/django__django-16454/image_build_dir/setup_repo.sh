#!/bin/bash
set -euxo pipefail
git clone -o origin https://github.com/django/django /testbed
chmod -R 777 /testbed
cd /testbed
git reset --hard 1250483ebf73f7a82ff820b94092c63ce4238264
git remote remove origin
source /opt/miniconda3/bin/activate
conda activate testbed
echo "Current environment: $CONDA_DEFAULT_ENV"
python -m pip install -e .
