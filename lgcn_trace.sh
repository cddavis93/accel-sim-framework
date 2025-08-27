source ./gpu-app-collection/src/setup_environment

export TERMINATE_UPON_LIMIT=1
export DYNAMIC_KERNEL_RANGE="3"

#export DYNAMIC_KERNEL_LIMIT_START=3
#export DYNAMIC_KERNEL_LIMIT_END=3


./util/tracer_nvbit/run_hw_trace.py -B light-gcn -D 3 -t -l 1