#!/bin/bash 

## -- 检查集群内 deployments 信息
# -1 获取集群内所有 deployments 副本信息
# -2 通过 -1 获取的信息，检索出副本数相等的 deployments，其表示应用恢复正常
# -3 通过 -1 获取的信息，检索出副本数不相等的 deployments，其表示应用没有恢复正常
# -4 通过 -3 获取的信息，使用 while 循环对副本数不相等的 deployment，进行恢复
# -5 重复执行 -3 检查集群内是否仍有副本数不相等的 deployments

echo "========搜集信息"
mkdir -p /tmp/{deployments_info,pod_info,node_info}-`date +%m%d%H%M`

# -1
kubectl get deploy --all-namespaces | grep -vE "dce-system|kube-system|logclean|monitoring" >/tmp/deployments_info-`date +%m%d%H%M`/all_deploy.info && echo "Coll_all_deploy_is_Done"
# -2
cat /tmp/deployments_info-`date +%m%d%H%M`/all_deploy.info | awk 'NR >1 {if($3=$6) print $1,$2,$3}' >/tmp/deployments_info-`date +%m%d%H%M`/ok_deploy.info && echo "Coll_ok_deploy_is_Done"
# -3
cat /tmp/deployments_info-`date +%m%d%H%M`/all_deploy.info | awk 'NR >1 {if($3!=$6) print $1,$2,$3}' >/tmp/deployments_info-`date +%m%d%H%M`/notok_deploy.info && echo "Coll_not_ok_deploy_is_Done"


# 通过 -3 判断集群内是否有异常的 deployment
echo " "
echo "========异常Deployments信息"
numbers=$(cat /tmp/deployments_info-`date +%m%d%H%M`/notok_deploy.info | wc -l)

if [ "$numbers" -gt 0 ];
then
        cat /tmp/deployments_info-`date +%m%d%H%M`/notok_deploy.info
else
        echo "-------all_deploy_is_ok!!!-------"
fi


# 通过 -4 、 -5 来确定是否停止异常的deployments，以及 按副本数重建 异常的 deployment--需要应用管理员告知由平台进行操作
#numbers=`cat /tmp/deployments_info-`date +%m%d%H%M`/notok_deploy.info | wc -l`
# $desnum 该变量请根据实际情况进行调整，0 就是将该 deoloyment 停止；若指定 $desnum，则会读取 notok_deploy.info 第三列值进行deployment的重建
# 
#if [ $numbers -gt 0 ];
#then
#        while read namespaces deployments desnum;
#        do
#                kubectl scale --replicas=0/$desnum deployment/$deployments -n $namespaces
#        done </tmp/deployments_info-`date +%m%d%H%M`/notok_deploy.info
#else
#    echo "all_deploy_is_ok!!!"
#fi


## -- 检查 pod 状态信息
echo " "
echo "========异常Pods信息"
error_pod=`kubectl get pods --all-namespaces  | grep -vE "Running|Com" | awk 'NR > 1' | wc -l`

if [ "$error_pod" -gt 0 ];
then
        kubectl get pods --all-namespaces  | grep -vE "Running|Com" | awk 'NR > 1' | awk '{print $1,$2}' > /tmp/pod_info-`date +%m%d%H%M`/error_pod.info
        echo "-------error_pod_info-custom-columns-------"
        while read namespaces pods;
        do
           kubectl get pod $pods -n $namespaces -o custom-columns="Tenant:.metadata.namespace,Pod:.metadata.name,Evicted:.status.reason,Events:.status.conditions[].message,ContainerEvents:.status.containerStatuses[].state.waiting.reason" | grep -v "Tenant"
        done </tmp/pod_info-`date +%m%d%H%M`/error_pod.info

        echo " "
        echo "-------error_pod_info-describe------------"
        while read namespaces pods;
        do
           echo -n $namespaces && kubectl describe pod $pods -n $namespaces | grep -A 8 Events | tail -n 1
        done </tmp/pod_info-`date +%m%d%H%M`/error_pod.info
else
        echo "-------all_pod_is_ok!!!-------"
fi


## -- 检查集群内 worker 信息
echo " "
echo "========异常节点信息"
nodenums=`kubectl get node | awk '{if($2=="NotReady") print $1,$2}' | wc -l`

if [ "$nodenums" -gt 0 ];
then
        kubectl get node | awk '{if($2=="NotReady") print $1,$2}'
else
        echo "-------all_node_is_ok!!!-------"
fi


## -- 检查集群内节点容器状态
echo " "
echo "========节点异常容器信息"
#ansible cal -m copy -a "src=/root/check_nodeContainersInfo.sh dest=/root/" >/dev/null 2>&1
#ansible cal -m shell -a "sh /root/check_nodeContainersInfo.sh"