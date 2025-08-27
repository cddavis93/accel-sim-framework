source ./gpu-app-collection/src/setup_environment

export TERMINATE_UPON_LIMIT=0
export DYNAMIC_KERNEL_RANGE="1000000"

#export DYNAMIC_KERNEL_LIMIT_START=3
#export DYNAMIC_KERNEL_LIMIT_END=3


./util/tracer_nvbit/run_hw_trace.py -B ExpressGNN -D 2 -l 1