#!/bin/bash

#def_clean_tmpfile

echo "" >/tmp/containersIDlist.tmp
echo "" >/tmp/zombieProclist.tmp

#def_env_list(zomibe_and_containerid)

v_containersIDlist=$(docker ps | grep -vE "POD|logclean|monitoring|dce|kube" | awk 'NR >1{print $1}')
v_zombieProclist=$(ps -A -ostat,ppid,pid,cmd | grep -e '^[Zz]' | awk '{print $2}'| sort| uniq)


#def_collect_containerINFO_function

f_containersPidlist(){

        for i in $v_containersIDlist;
        do
           docker inspect $i | jq -r '[.[].State.Pid,.[].Config.Hostname,.[].Name] | @tsv' | awk -F "_" '{print $1,$4}' | awk '{print $1,$2,$4}' >>/tmp/containersIDlist.tmp
           docker inspect $i | jq -r .[].State.Pid
        done

}

f_containersPidlist > /dev/null

#def_main_function_diff_zombiePID_and_containerID(ppid_vs_containerPID)

f_main(){

        local v_zombieProcNumbers=$(ps -A -ostat,ppid,pid,cmd | grep -e '^[Zz]' | awk '{print $2}'| sort| uniq| wc -l)

        if [ "$v_zombieProcNumbers" -gt 0 ];
        then
             echo -e "zombieProcNumbers: \033[41;37m $v_zombieProcNumbers \033[0m"
             ps -A -ostat,ppid,pid,cmd | grep -e '^[Zz]' | sort| uniq >>/tmp/zombieProclist.tmp
        else
             echo -e "\033[42;37m node_is_not_zombie_proceess!!! \033[0m"
             exit;
        fi

        for vz in $v_zombieProclist;
        do
           cat /tmp/containersIDlist.tmp | grep $vz >/dev/null
           if [ $? -eq 0 ];
           then
               cat /tmp/containersIDlist.tmp | grep $vz
           fi
        done
}

f_main
