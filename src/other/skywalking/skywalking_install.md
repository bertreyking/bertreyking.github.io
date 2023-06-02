# Skywalking 部署

## [Docker](https://github.com/apache/skywalking/tree/master/docker)

1. 克隆项目到本地

   ```shell
   root@worker01 ~]# git clone https://github.com/apache/skywalking.git
   正克隆到 'skywalking'...
   remote: Enumerating objects: 280249, done.
   remote: Counting objects: 100% (1566/1566), done.
   remote: Compressing objects: 100% (711/711), done.
   remote: Total 280249 (delta 608), reused 1467 (delta 558), pack-reused 278683
   接收对象中: 100% (280249/280249), 164.34 MiB | 6.83 MiB/s, done.
   处理 delta 中: 100% (109846/109846), done.    
   ```

2. 修改 .env 内镜像版本并部署

   ```shell
   [root@worker01 ~]# cd skywalking/docker
   
   [root@worker01 docker]# cat .env 
   ES_VERSION=7.4.2
   OAP_IMAGE=apache/skywalking-oap-server:latest
   UI_IMAGE=apache/skywalking-ui:latest
   
   [root@worker01 docker]# docker-compose up -d   
   ```

3. 检查组件状态

   ```shell
   [root@worker01 docker]# docker-compose ps 
   NAME                IMAGE                                                     COMMAND                  SERVICE             CREATED             STATUS                        PORTS
   elasticsearch       docker.elastic.co/elasticsearch/elasticsearch-oss:7.4.2   "/usr/local/bin/dock…"   elasticsearch       2 minutes ago       Up 2 minutes (healthy)        0.0.0.0:9200->9200/tcp, :::9200->9200/tcp, 9300/tcp
   oap                 apache/skywalking-oap-server:latest                       "bash docker-entrypo…"   oap                 2 minutes ago       Up About a minute (healthy)   0.0.0.0:11800->11800/tcp, :::11800->11800/tcp, 1234/tcp, 0.0.0.0:12800->12800/tcp, :::12800->12800/tcp
   ui                  apache/skywalking-ui:latest                               "bash docker-entrypo…"   ui                  2 minutes ago       Up About a minute             0.0.0.0:8080->8080/tcp, :::8080->8080/tcp
   ```

## [Kubernetes](https://github.com/apache/skywalking-kubernetes)

1. 克隆项目到本地

   ```shell
   [root@master01 ~]# git clone https://github.com/apache/skywalking-kubernetes.git
   ```

2. 通过 --set 指定镜像版本并部署

   ```shell
   [root@master01 ~]# cd skywalking-kubernetes/
   [root@master01 skywalking-kubernetes]# helm -n skywalking install skywalking chart/skywalking --version "0.0.0-b670c41d94a82ddefcf466d54bab5c492d88d772" --set oap.image.tag=9.2.0 --set oap.storageType=elasticsearch --set ui.image.tag=9.2.0
   
   NAME: skywalking
   LAST DEPLOYED: Fri Jun  2 14:23:10 2023
   NAMESPACE: skywalking
   STATUS: deployed
   REVISION: 1
   NOTES:
   ************************************************************************
   *                                                                      *
   *                 SkyWalking Helm Chart by SkyWalking Team             *
   *                                                                      *
   ************************************************************************
   
   Thank you for installing skywalking-helm.
   
   Your release is named skywalking.
   
   Learn more, please visit https://skywalking.apache.org/
   Get the UI URL by running these commands:
     echo "Visit http://127.0.0.1:8080 to use your application"
     kubectl port-forward svc/skywalking-skywalking-helm-ui 8080:80 --namespace skywalking
   #################################################################################
   ######   WARNING: Persistence is disabled!!! You will lose your data when   #####
   ######            the SkyWalking's storage ES pod is terminated.            #####
   #################################################################################
   ```

3. 使用 NodePort 方式暴露 sky walking-ui

   ```shell
   [root@master01 skywalking-kubernetes]# kubectl get svc -n skywalking skywalking-skywalking-helm-ui -o yaml 
   apiVersion: v1
   kind: Service
   metadata:
     annotations:
       meta.helm.sh/release-name: skywalking
       meta.helm.sh/release-namespace: skywalking
     labels:
       app: skywalking
       app.kubernetes.io/managed-by: Helm
       chart: skywalking-helm-4.4.0
       component: ui
       dce.daocloud.io/app: skywalking
       heritage: Helm
       release: skywalking
     name: skywalking-skywalking-helm-ui
     namespace: skywalking
   spec:
     clusterIP: 172.31.31.202
     externalTrafficPolicy: Cluster
     ipFamily: IPv4
     ports:
     - nodePort: 37364
       port: 80
       protocol: TCP
       targetPort: 8080
     selector:
       app: skywalking
       component: ui
         release: skywalking
     sessionAffinity: None
     type: NodePort
   ```
