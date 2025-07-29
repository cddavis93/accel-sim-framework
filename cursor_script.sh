#!/usr/bin/env bash

source ./gpu-simulator/setup_environment.sh 
./gpu-simulator/bin/release/accel-sim.out -config ./sim_run_12.8/vectoradd/NO_ARGS/A100/gpgpusim.config -trace ./sim_run_12.8/vectoradd/NO_ARGS/A100/traces/kernelslist.g