#!/bin/bash

#def_function_collect_containers_file

v_containers_file(){

    for i in `docker ps |grep -vE "POD|dce_engine_1" |awk 'NR >1 {print $1}'`;
    do
      docker inspect $i |jq -r '[.[].State.StartedAt,.[].Name] | @tsv' |awk -F "." '{print $1,$2,$3}' |awk -F "_" '{print $1,$2,$3,$4}' |awk '{print $6,$4,$5,$1}'
    done

}

v_containers_file >>/tmp/container_info-`date +%m%d%H%M%S`

#def_env_v_containersid_file_numbers_and_checkContainers_status_info

v_consid_file=`ls -lrt /tmp/container_info* |awk '{print $9}' |tail -n2 |wc -l`

if [ $v_consid_file -lt 2 ];
then
#    exit;
    sleep 1 ; v_containers_file >>/tmp/container_info-`date +%m%d%H%M%S`
else
    v_diff1=`ls -rt /tmp/container_info* |tail -n2 |head -n1`
    v_diff2=`ls -rt /tmp/container_info* |tail -n1`
    diff $v_diff1 $v_diff2 >/dev/null 2>&1
    if [ $? -eq 0 ];
    then
        echo "all_Containers_is_ok!!!"
    else
        echo "error_Containers_list!!!"
        echo `diff $v_diff1 $v_diff2` |awk -F ">" '{print $2}'
    fi
fi
