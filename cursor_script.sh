#!/usr/bin/env bash

source ./gpu-simulator/setup_environment.sh 
export CUDA_INSTALL_PATH=/usr/local/cuda-12.1
export PATH=$CUDA_INSTALL_PATH/bin:$PATH
./gpu-simulator/bin/debug/accel-sim.out -config ./sim_run_12.8/vectoradd/NO_ARGS/A100/gpgpusim.config -trace ./sim_run_12.8/vectoradd/NO_ARGS/A100/traces/kernelslist.g