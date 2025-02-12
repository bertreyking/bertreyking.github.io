# elastic 多版本部署

## eck-operator

### 部署 eck-operator

- [如何部署 operaotr ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-deploy-eck.html)
  - [crds.yaml](https://download.elastic.co/downloads/eck/2.16.1/crds.yaml)
  - [operator.yaml](https://download.elastic.co/downloads/eck/2.16.1/operator.yaml)
  - 默认部署在 elastic-system 下
  - [更多 eck-operator 知识](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-operating-eck.html)

### 部署 elastic

- [ 部署 elastic ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-deploy-elasticsearch.html)

  - [ 自定义 elastic 计算资源 ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-managing-compute-resources.html) +cpu、memory 、+jvm、+elastic config

  - [ 自定义 pod 资源 ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-customize-pods.html) + cpu、memory

    - [ node.processors ](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-threadpool.html#node.processors) # Elasticsearch 会自动检测处理器数量并根据该数量设置线程池设置，所以 elastic 要配置 cpu 的 limit，配置后 node.processors，会取用该值。如果不设置，则会使用节点的核心数

      ![cpu_process](/png/elastic-process.png)

  - [elastic 虚拟机内存](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-virtual-memory.html)

    - 默认情况下，Elasticsearch 使用内存映射 ( `mmap`) 来高效访问索引，linux 默认值太低，会导致 Elasticsearch 无法正常工作，可能会导致内存不足异常

      ```shell
      # quickstart 默认是禁用的
      node.store.allow_mmap: false # 禁用，会影响性能
      
      # 生产环境建议配置
      vm.max_map_count to 262144 # 我看产品是利用 initcontainer 设置的
      node.store.allow_mmap unset
      
      vm.max_map_count=262144 可以直接在主机上设置内核设置，也可以通过必须具有特权的专用 init 容器或专用 Daemonset 进行设置
      ```

  - [ nodeSets ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-node-configuration.html) 

    - [ es_config ](https://www.elastic.co/guide/en/elasticsearch/reference/current/settings.html)

    - elastic 有三个配置文件：[ config_format ](https://www.elastic.co/guide/en/elasticsearch/reference/current/settings.html#_config_file_format)

      - `elasticsearch.yml`用于配置 Elasticsearch

      - `jvm.options`用于配置 Elasticsearch JVM 设置

      - `log4j2.properties`用于配置 Elasticsearch 日志记录

    - [ node-role ](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-node.html#node-roles)

### 部署 logstash

- [ elastic 组件 ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-orchestrating-elastic-stack-applications.html)

## elastic 部署方式

### [ docker 方式 ](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)

### [helm 部署 elastic ](https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-stack-helm-chart.html)

### cr 方式部署 es 6.8.23

- [ 低版本参数 ](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/modules-node.html)

  ```shell
  # 不支持 node.roles 的写法，7.x 才支持，示例：
  node.master: false 
  node.data: false 
  node.ingest: true 
  ```

- [ 线程池 ](https://www.elastic.co/guide/en/elasticsearch/reference/6.8/modules-threadpool.html)

- elastic cr 编排文件示例

  ```yaml
  # 7.x 
  nodeSets:
    - config:
        node.roles:
        - data
        - master
        - ingest
        - ml # 7 才开始支持
        - data_cold
        - data_content
        - data_frozen
        - data_hot
        - data_warm
        - remote_cluster_client
        - transform
   # 6.x
   nodeSets:
    - config:
        node.master: true   # 是否作为 Master 节点
        node.data: true     # 是否存储数据
        node.ingest: true   # 是否支持 Ingest 预处理
        node.attr.data: hot
        cluster.remote.connect: false  # 是否支持 es 集群远程集群连接
        
   🛠 说明
  	1.	node.master、node.data、node.ingest 取代 node.roles
        •	node.master: true → 该节点可参与主节点选举
        •	node.data: true → 该节点可存储索引数据
        •	node.ingest: true → 该节点可用于预处理 pipeline
        •	node.ml: true → 7.x 才有 ML 角色，6.x 可以去掉
  	2.	远程集群 (remote_cluster_client) 相关设置
        •	Elasticsearch 7.x: 需要 cluster.remote.connect: true
        •	Elasticsearch 6.x: 远程集群连接在 node.data 角色的 Data 节点上进行，不需要 remote_cluster_client
  	3.	缺失的 data_hot, data_warm, data_cold, data_frozen
        •	在 7.x 及更早版本，没有 data_hot, data_warm, data_cold, data_frozen 这些角色，它们在 7.x 只是标签（node attributes），而不是角色。
        •	你可以改用 node.attr 方式标记：
        	node.attr.data: hot
        •	这样你仍然可以在 ILM（Index Lifecycle Management）策略中使用 data 节点进行分层存储。
        
  ```

- [elastic-image](https://www.docker.elastic.co/r/elasticsearch)
  1. elastic6: docker pull docker.elastic.co/elasticsearch/elasticsearch:6.8.23 # 下载 ✅
  2. elastic8: docker pull docker.elastic.co/elasticsearch/elasticsearch:8.16.3  # 下载 ✅

- elastic-6823 编排文件

  ```yaml
    apiVersion: elasticsearch.k8s.elastic.co/v1
    kind: Elasticsearch
    metadata:
      name: elastic-6822
    spec:
      version: 6.8.22
      image: 10.29.14.196/elastic.m.daocloud.io/elasticsearch/elasticsearch:6.8.22
      nodeSets:
      - name: elasticsearch
        count: 1
        volumeClaimTemplates:
          - metadata:
              name: elasticsearch-data 
            spec:
              accessModes:
              - ReadWriteOnce
              resources:
                requests:
                  storage: 30Gi
              storageClassName: nfs-csi
        config:
          node.master: true
          node.data: true
          node.ingest: true
          node.attr.data: hot
          cluster.remote.connect: false
          processors: 2
        podTemplate:
          spec:
            containers:
            - name: elasticsearch
              env:
              - name: ES_JAVA_OPTS
                value: -Xms2g -Xmx2g
              resources:
                requests:
                  memory: 4Gi
                  cpu: 1
                limits:
                  memory: 4Gi
      monitoring:
        logs: {}
        metrics: {}
      auth: {}
      http:
        service:
          metadata: {}
          spec:
            ports:
            - name: https
              port: 9200
              protocol: TCP
              targetPort: 9200
            type: ClusterIP
        tls:
          certificate: {}
  ```

- elastic-8163 cr 编排文件

  ```yaml
  apiVersion: elasticsearch.k8s.elastic.co/v1
  kind: Elasticsearch
  metadata:
    name: elastic-8163
  spec:
    version: 8.16.3
    image: 10.29.14.196/elastic.m.daocloud.io/elasticsearch/elasticsearch:8.16.3
    nodeSets:
    - name: data
      count: 3
      volumeClaimTemplates:
        - metadata:
            name: elasticsearch-data 
          spec:
            accessModes:
            - ReadWriteOnce
            resources:
              requests:
                storage: 30Gi
            storageClassName: nfs-csi
      config:
        node.roles:
        - data
        - master
        - ingest
        - ml
        - data_cold
        - data_content
        - data_frozen
        - data_hot
        - data_warm
        - remote_cluster_client
        - transform
        node.processors: 2
      podTemplate:
        spec:
          containers:
          - name: elasticsearch
            env:
            - name: ES_JAVA_OPTS
              value: -Xms2g -Xmx2g
            resources:
              requests:
                memory: 4Gi
                cpu: 1
              limits:
                memory: 4Gi
          initContainers:
          - command:
            - sh
            - -c
            - sysctl -w vm.max_map_count=262144
            name: sysctl
            resources: {}
            securityContext:
              privileged: true
              runAsUser: 0
    monitoring:
      logs: {}
      metrics: {}
    auth: {}
    http:
      service:
        metadata: {}
        spec:
          ports:
          - name: https
            port: 9200
            protocol: TCP
            targetPort: 9200
          type: ClusterIP
      tls:
        certificate: {}
  ```

## elastic-prometheus-exporter

- metrics 监控，elastic 不同版本都是通用的，替换下对应的 matchLabels 和 elastic 的 svc 地址即可

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    jobLabel: node-exporter
    operator.insight.io/managed-by: insight
    release: insight-agent
  name: elastic-8163-prometheus-exporter
  namespace: default
spec:
  endpoints:
  - bearerTokenSecret:
      key: ""
    interval: 30s
    port: prometheus
    scheme: http
    scrapeTimeout: 30s
  namespaceSelector:
    any: true
  selector:
    matchLabels:
      elasticsearch.k8s.elastic.co/exporter-cluster-name: elastic-8163
---
apiVersion: v1
kind: Service
metadata:
  labels:
    elasticsearch.k8s.elastic.co/exporter-cluster-name: elastic-8163
  name: elastic-8163-prometheus-exporter
  namespace: default
spec:
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: prometheus
    port: 9114
    protocol: TCP
    targetPort: 9114
  selector:
    elasticsearch.k8s.elastic.co/exporter-cluster-name: elastic-8163
  sessionAffinity: None
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: mcamel-elasticsearch-cluster-exporter
  name: elastic-8163-exporter
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcamel-elasticsearch-cluster-exporter
      elasticsearch.k8s.elastic.co/exporter-cluster-name: elastic-8163
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: mcamel-elasticsearch-cluster-exporter
        elasticsearch.k8s.elastic.co/exporter-cluster-name: elastic-8163
    spec:
      containers:
      - command:
        - /bin/elasticsearch_exporter
        - --es.uri=https://elastic-8163-es-http.default.svc.cluster.local:9200
        - --es.all
        - --es.ssl-skip-verify
        env:
        - name: ES_USERNAME
          value: elastic
        - name: ES_PASSWORD
          valueFrom:
            secretKeyRef:
              key: elastic
              name: elastic-8163-es-elastic-user
        image: 10.29.14.196/quay.m.daocloud.io/prometheuscommunity/elasticsearch-exporter:v1.5.0
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 3
          httpGet:
            path: /healthz
            port: 9114
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 10
        name: mcamel-elasticsearch-cluster-exporter
        ports:
        - containerPort: 9114
          name: prometheus
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          httpGet:
            path: /healthz
            port: 9114
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 10
        resources:
          limits:
            cpu: 100m
            memory: 128Mi
          requests:
            cpu: 25m
            memory: 64Mi
        securityContext:
          capabilities:
            drop:
            - SETPCAP
            - MKNOD
            - AUDIT_WRITE
            - CHOWN
            - NET_RAW
            - DAC_OVERRIDE
            - FOWNER
            - FSETID
            - KILL
            - SETGID
            - SETUID
            - NET_BIND_SERVICE
            - SYS_CHROOT
            - SETFCAP
          readOnlyRootFilesystem: true
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext:
        fsGroup: 10000
        runAsGroup: 10000
        runAsNonRoot: true
        runAsUser: 10000
      terminationGracePeriodSeconds: 30
```

## elastic 部署报错记录

- node.processors 参数错误

```shell
[2025-02-10T10:19:36,360][WARN ][o.e.b.ElasticsearchUncaughtExceptionHandler] [elastic-6822-es-elasticsearch-0] uncaught exception in thread [main]
org.elasticsearch.bootstrap.StartupException: java.lang.IllegalArgumentException: unknown setting [node.processors] please check that any required plugins are installed, or check the breaking changes documentation for removed settings
	at org.elasticsearch.bootstrap.Elasticsearch.init(Elasticsearch.java:163) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Elasticsearch.execute(Elasticsearch.java:150) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.cli.EnvironmentAwareCommand.execute(EnvironmentAwareCommand.java:86) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.cli.Command.mainWithoutErrorHandling(Command.java:124) ~[elasticsearch-cli-6.8.22.jar:6.8.22]
	at org.elasticsearch.cli.Command.main(Command.java:90) ~[elasticsearch-cli-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:116) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Elasticsearch.main(Elasticsearch.java:93) ~[elasticsearch-6.8.22.jar:6.8.22]
Caused by: java.lang.IllegalArgumentException: unknown setting [node.processors] please check that any required plugins are installed, or check the breaking changes documentation for removed settings
	at org.elasticsearch.common.settings.AbstractScopedSettings.validate(AbstractScopedSettings.java:530) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.common.settings.AbstractScopedSettings.validate(AbstractScopedSettings.java:475) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.common.settings.AbstractScopedSettings.validate(AbstractScopedSettings.java:446) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.common.settings.AbstractScopedSettings.validate(AbstractScopedSettings.java:417) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.common.settings.SettingsModule.<init>(SettingsModule.java:148) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.node.Node.<init>(Node.java:374) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.node.Node.<init>(Node.java:266) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Bootstrap$5.<init>(Bootstrap.java:212) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Bootstrap.setup(Bootstrap.java:212) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Bootstrap.init(Bootstrap.java:333) ~[elasticsearch-6.8.22.jar:6.8.22]
	at org.elasticsearch.bootstrap.Elasticsearch.init(Elasticsearch.java:159) ~[elasticsearch-6.8.22.jar:6.8.22]
	... 6 more
	
# 6.x 版本不支持这种写法，7.x 开始才支持的
- processors: 2 # 这才是 6 的写法
```

