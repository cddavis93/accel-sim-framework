source ./gpu-app-collection/src/setup_environment
source ./gpu-simulator/setup_environment.sh

#./util/job_launching/run_simulations.py -B light-gcn -C A100-SASS -T ./hw_run/traces/device-2/12.8/ -N lgcn_A100-SASS
./util/job_launching/run_simulations.py -B light-gcn -C A100_bypass -T ./hw_run/traces/device-2/12.8/ -N lgcn_A100-bypass

#./util/job_launching/monitor_func_test.py -v -N lgcn_A100-SASS
./util/job_launching/monitor_func_test.py -v -N lgcn_A100-bypass

#./util/job_launching/get_stats.py -k -K -s util/job_launching/stats/stats_all.yml -N lgcn_A100-SASS | tee stats_lgcn_A100_SASS-per-kernel-instance.csv
./util/job_launching/get_stats.py -k -K -s util/job_launching/stats/stats_all.yml -N lgcn_A100-bypass | tee stats_lgcn_A100-bypass-per-kernel-instance.csv