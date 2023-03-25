# 探针使用

## 探针交互

- 容器中配置探针后，kubelet 会按指定配置对 pod 进行健康检查

## 探针种类

- 存活探针：决定什么时候重启 容器。如：pod 运行正常，但容器内进程启动时需要的依赖条件异常<db、nfs> 导致启动时夯住。 
- 就绪探针：决定是否将 pod 相关 service 的 endpoint 摘除。容器运行且进程启动正常才算就绪
- 启动探针：决定容器的启动机制，以及容器启动后进行存活探针/就绪探针的检查。如容器启动耗时较长

## 探针检查结果

- Success：通过检查
- Failure：未通过检查
- Unknown：探测失败，不会采取任何行动

## 探针编写层级

- Pod:  .spec.contaiers.livenessProbe
- Pod:  .spec.contaiers.readinessProbe
- Pod:  .spec.contaiers.startupProbe

## 探针检查方法

- exec：相当于 command / shell 进行检查，支持 **initialDelaySeconds** / **periodSeconds**

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    labels:
      test: liveness
    name: liveness-exec
  spec:
    containers:
    - name: liveness
      image: registry.k8s.io/busybox
      args:
      - /bin/sh
      - -c
      - touch /tmp/healthy; sleep 30; rm -f /tmp/healthy; sleep 600
      livenessProbe:
        exec:
          command:
          - cat
          - /tmp/healthy
        initialDelaySeconds: 5
        periodSeconds: 5
  ```

- httpGet：相当于 http 请求，支持  **initialDelaySeconds** / **periodSeconds** / **Headers** / **port: .ports.name**

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    labels:
      test: liveness
    name: liveness-http
  spec:
    containers:
    - name: liveness
      image: registry.k8s.io/liveness
      args:
      - /server
      livenessProbe:
        httpGet:
          path: /healthz
          port: 8080
          httpHeaders:
          - name: Custom-Header
            value: Awesome
        initialDelaySeconds: 3
        periodSeconds: 3
  ```

- tcpSocket: 相当于 telnet 某个端口(kubelet 建立套接字链接)，支持  **initialDelaySeconds** / **periodSeconds** / **Headers** / **port: .spec.containers.ports.name**

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: goproxy
    labels:
      app: goproxy
  spec:
    containers:
    - name: goproxy
      image: registry.k8s.io/goproxy:0.1
      ports:
      - containerPort: 8080
      readinessProbe:
        tcpSocket:
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 10
      livenessProbe:
        tcpSocket:
          port: 8080
        initialDelaySeconds: 15
        periodSeconds: 20
  
  --- port 支持使用 ports.name
  ports:
  - name: liveness-port
    containerPort: 8080
    hostPort: 8080
  
  livenessProbe:
    httpGet:
      path: /healthz
      port: liveness-port
  ```

- grpc：首先应用要支持该方法，且 grpc 的话，pod 中必须要定义 .spec.containers.ports 字段

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: etcd-with-grpc
  spec:
    containers:
    - name: etcd
      image: registry.k8s.io/etcd:3.5.1-0
      command: [ "/usr/local/bin/etcd", "--data-dir",  "/var/lib/etcd", "--listen-client-urls", "http://0.0.0.0:2379", "--advertise-client-urls", "http://127.0.0.1:2379", "--log-level", "debug"]
      ports:
      - containerPort: 2379
      livenessProbe:
        grpc:
          port: 2379
        initialDelaySeconds: 10
  ```

- 启动探针、存活探针使用

  ```yaml
  ports:
  - name: liveness-port
    containerPort: 8080
    hostPort: 8080
  
  livenessProbe:
    httpGet:
      path: /healthz
      port: liveness-port
    failureThreshold: 1
    periodSeconds: 10
  
  startupProbe:
    httpGet:
      path: /healthz
      port: liveness-port
    failureThreshold: 30 #次数
    periodSeconds: 10
    
  - startupProbe 检查通过时，才会执行所配置的存活探针和就绪探针。
  - startupProbe 探测配置建议：failureThreshold * periodSeconds（案例是5m，后执行就绪检查）
  ```



## [探针配置](https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

## [Pod 生命周期](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-lifecycle/#container-probes)
