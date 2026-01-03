#!/usr/bin/env bash
set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure


LCM_MSGS_DIR=$(pwd)
LCM_GEN_DIR=../lcm


cd $LCM_GEN_DIR/build/lcmgen
make
cd $LCM_MSGS_DIR
cp $LCM_GEN_DIR/build/lcmgen/lcm-gen .
rm -r python_lcm_msgs/lcm_msgs/
./lcm_batch_processor.sh -v -p lcm_files -o python_lcm_msgs/lcm_msgs/ > /dev/null 2>/dev/null
python python_lcm_msgs/fix_imports.py 2>&1 > /dev/null
git checkout python_lcm_msgs/lcm_msgs/__init__.py > /dev/null 2>&1 > /dev/null
echo "Regenerated python lcm messages"

