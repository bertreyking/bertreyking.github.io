# VictoriaMetrics 安装

## 安装 anisible 组件

```shell
# 使用 dnf 安装 epel-release 源
dnf install epel-release

# 只手使用 dnf 包管理器，安装 ansibel
dnf install -y ansible

# 查看安装后版本
ansible --version 
ansible [core 2.14.17]
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3.9/site-packages/ansible
  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/bin/ansible
  python version = 3.9.19 (main, Sep 11 2024, 00:00:00) [GCC 11.5.0 20240719 (Red Hat 11.5.0-2)] (/usr/bin/python3)
  jinja version = 3.1.2
  libyaml = True
```

## 部署单节点模式

```shell
# 创建目录
mkdir -p /var/lib/victoria-metrics

# 配置文件
cat <<END >/etc/systemd/system/victoriametrics.service
[Unit]
Description=VictoriaMetrics service
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/bin/victoria-metrics-prod -storageDataPath=/var/lib/victoria-metrics -retentionPeriod=90d -selfScrapeInterval=10s
SyslogIdentifier=victoriametrics
Restart=always

PrivateTmp=yes
ProtectHome=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动服务
systemctl daemon-reload && sudo systemctl enable --now victoriametrics.service

# 检查服务
systemctl status victoriametrics

# victoriametriscs 内置了 ui
http://0.0.0.0:8428/vmui
```

## 部署集群模式

### vmstorage

```shell
# 创建目录
mkdir -p /var/lib/vmstorage 

# 配置文件
cat <<END >/etc/systemd/system/vmstorage.service
[Unit]
Description=VictoriaMetrics vmstorage service
After=network.target

[Service]
Type=simple
User=root
Group=root
Restart=always
ExecStart=/usr/local/bin/vmstorage-prod -retentionPeriod=90d -storageDataPath=/var/lib/vmstorage

PrivateTmp=yes
NoNewPrivileges=yes
ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动
systemctl daemon-reload && systemctl enable --now vmstorage
```

### vminstert

```shell
# 配置文件
cat << END >/etc/systemd/system/vminsert.service
[Unit]
Description=VictoriaMetrics vminsert service
After=network.target

[Service]
Type=simple
User=victoriametrics
Group=victoriametrics
Restart=always
ExecStart=/usr/local/bin/vminsert-prod -storageNode=192.168.0.110

PrivateTmp=yes
NoNewPrivileges=yes
ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动
systemctl daemon-reload && sudo systemctl enable --now vminsert.service

# 多 vmstorgae 写法
-storageNode=192.168.0.110,192.168.0.111
```

### vmselect

```shell
# 创建目录
mkdir -p /var/lib/vmselect-cache 

# 配置文件
cat << END >/etc/systemd/system/vmselect.service
[Unit]
Description=VictoriaMetrics vmselect service
After=network.target

[Service]
Type=simple
User=root
Group=root
Restart=always
ExecStart=/usr/local/bin/vmselect-prod -storageNode=192.168.0.110 -cacheDataPath=/var/lib/vmselect-cache

PrivateTmp=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动
systemctl daemon-reload && sudo systemctl enable --now vmselect.service

# vmui
http://0.0.0.0:8481/select/0/vmui
```

## 检查监听端口

```shell
[root@vmserver ~]# netstat -naltp 
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:8480            0.0.0.0:*               LISTEN      12877/vminsert-prod 
tcp        0      0 0.0.0.0:8481            0.0.0.0:*               LISTEN      12843/vmselect-prod 
tcp        0      0 0.0.0.0:8482            0.0.0.0:*               LISTEN      12529/vmstorage-pro 
tcp        0      0 0.0.0.0:8400            0.0.0.0:*               LISTEN      12529/vmstorage-pro 
tcp        0      0 0.0.0.0:8401            0.0.0.0:*               LISTEN      12529/vmstorage-pro 
```

## 部署采集器

### prometheus

```shell
# 创建目录
mkdir -p /var/lib/prometheus/rules

# 配置文件
cat << END >/etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus service
After=network.target

[Service]
Type=simple
User=root
Group=root
Restart=always
ExecStart=/usr/local/bin/prometheus --config.file="/var/lib/prometheus/prometheus.yml" --config.auto-reload-interval=30s --storage.tsdb.path="/var/lib/prometheus/data/" --storage.tsdb.retention.time=2h --web.enable-lifecycle

PrivateTmp=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动
systemctl daemon-reload && sudo systemctl enable --now prometheus.service
```

### node-exporter

- [exporter_more](https://prometheus.io/docs/instrumenting/exporters/) (windows/ipmi/smartraid/ups/jenkins/jira/confluence/ovirt/ssh/podman/powerdns/script)

```shell
# 配置文件
cat << END >/etc/systemd/system/node_exporter.service
[Unit]
Description=Node-exporter service
After=network.target

[Service]
Type=simple
User=root
Group=root
Restart=always
ExecStart=/usr/local/bin/node_exporter --web.listen-address=0.0.0.0:9100

PrivateTmp=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动
systemctl daemon-reload && systemctl enable --now node_exporter 
```

### prometheus.yml 配置文件

```shell
[root@vmserver prometheus]# cat prometheus.yml 
# my global config
global:
  scrape_interval: 15s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

  external_labels:
    env: maweibing

remote_write:
  - url: http://192.168.0.110:8480/insert/0/prometheus

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - 192.168.0.110:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  - "./rules/instance_down_status.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"
    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.
    static_configs:
      - targets: ["192.168.0.110:9090"]
  - job_name: "node-exporter"
    static_configs:
      - targets: ["192.168.0.110:9100"]
  - job_name: "ipmi-exporter"
    static_configs:
      - targets: ["192.168.0.110:9290"]
      
# 示例告警规则
[root@vmserver prometheus]# cat /var/lib/prometheus/rules/instance_down_status.yml 
groups:
- name: example
  rules:
  # Alert for any instance that is unreachable for >5 minutes.
  - alert: InstanceDown
    expr: up == 0
    for: 5m
    labels:
      severity: page
    annotations:
      summary: "Instance {{ $labels.instance }} down"
      description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes."

  # Alert for any instance that has a median request latency >1s.
  - alert: APIHighRequestLatency
    expr: api_http_request_latencies_second{quantile="0.5"} > 1
    for: 10m
    annotations:
      summary: "High request latency on {{ $labels.instance }}"
      description: "{{ $labels.instance }} has a median request latency above 1s (current value: {{ $value }}s)"
```

## 部署仪表盘

### 安装 grafana

- [grafana-rpm-download](https://grafana.com/grafana/download)
- [grafana-dashboard-download](https://grafana.com/grafana/dashboards/11074-node-exporter-for-prometheus-dashboard-en-v20201010/)

```shell
# 安装
wget -q -O gpg.key https://rpm.grafana.com/gpg.key
sudo rpm --import gpg.key
cat << END >/etc/yum.repos.d/grafana.repo
[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
END
dnf install grafana -y

# 手动下载 grafana rpm 包
wget https://dl.grafana.com/oss/release/grafana-11.4.0-1.x86_64.rpm
yum install -y grafana-11.4.0-1.x86_64.rpm 

# 查看配置文件
[root@vmserver ~]# cat /etc/sysconfig/grafana-server 
GRAFANA_USER=grafana

GRAFANA_GROUP=grafana

GRAFANA_HOME=/usr/share/grafana

LOG_DIR=/var/log/grafana

DATA_DIR=/var/lib/grafana

MAX_OPEN_FILES=10000

CONF_DIR=/etc/grafana

CONF_FILE=/etc/grafana/grafana.ini

RESTART_ON_UPGRADE=true

PLUGINS_DIR=/var/lib/grafana/plugins

PROVISIONING_CFG_DIR=/etc/grafana/provisioning

# Only used on systemd systems
PID_FILE_DIR=/var/run/grafana

# 启动 grafna
mkdir -p /var/lib/grafana
chown -R grafana:grafana /var/lib/grafana/
systemctl daemon-reload && sudo systemctl enable --now grafana-server
```

### 配置 grafana

- 首次登录需要更改密码，默认用户/密码：admin/admin
- 登录后，添加数据源：
  - http://192.168.0.110:8481/select/0/prometheus # 前面部署好的 vmselect 的地址
    - 8481: 是 vmselect
    - /select/0/prometheus: 0 是自定义的 int 型数字，多个 prometheus 时都是为 0 ？，只是在 vmstorage 里面的标识么，可以其它数字么，待研究、prometheus 就是你数据源的类型

## 告警通知

- [wechat](https://prometheus.io/docs/alerting/latest/configuration/#receiver)
- [alertmanager](https://github.com/prometheus/alertmanager)

### 安装 alertmanger

```shell
# 创建目录
mkdir -pv /var/lib/alertmanager

# 配置文件
cat << END >/etc/systemd/system/alertmanager.service
[Unit]
Description=Alertmanager service
After=network.target

[Service]
Type=simple
User=root
Group=root
Restart=always
ExecStart=/usr/local/bin/alertmanager --config.file="/var/lib/alertmanager/alertmanager.yml" --storage.path="/var/lib/alertmanager/data/" --data.retention=2h --data.maintenance-interval=15m --alerts.gc-interval=30m --web.listen-address=:9093 

PrivateTmp=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 启动
systemctl daemon-reload && systemctl enable --now alertmanager

# alertmanager 配置文件
默认的
```

### 对接企业微信

```shell
# 自行申请一个企业微信，不需要上传资质
# 然后创建群组，把想收到告警通知的人都拉进去

# alertmanger 配置文件
```

## frp 内网穿透

### frp_server

```shell
# 创建目录
mkdir -p /var/lib/proxy

# 配置文件
cat <<END >/etc/systemd/system/proxy.service
[Unit]
Description=frp_server_proxy service
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/bin/frps -c /var/lib/proxy/frps.toml
SyslogIdentifier=fprserver
Restart=always

PrivateTmp=yes
ProtectHome=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 服务配置文件
[root@cloud-sg8dm4-ip08 ~]# cat /var/lib/proxy/frps.toml 
bindPort = xxxx
```

### frp_client

```shell
# 创建目录
mkdir -p /var/lib/proxy

# 配置文件
cat <<END >/etc/systemd/system/proxy.service
[Unit]
Description=frp_server_proxy service
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/bin/frpc -c /var/lib/proxy/frpc.toml
SyslogIdentifier=fprclient
Restart=always

PrivateTmp=yes
ProtectHome=yes
NoNewPrivileges=yes

ProtectSystem=full

[Install]
WantedBy=multi-user.target
END

# 服务配置文件
[root@vmserver ~]# cat /var/lib/proxy/frpc.toml 
serverAddr = "x.x.x.x" # 具有公网节点的 ip 地址
serverPort = xxxx # prxoy 暴露的端口，client 会通过他连接 server 端

# 本机的 22 端口，然后通过 prxoy-server 端的公网 ip:60222 对外暴露
[[proxies]]
name = "ssh" # 对 server 端，暴露 ssh 服务，
type = "tcp"
localIP = "127.0.0.1"
localPort = 22 # 本机的 22 端口，
remotePort = xxxxx # 通过公网 ip 访问时的 ssh 端口

# 本机的 3000 端口，然后通过 prxoy-server 端的公网 ip:63000 对外暴露
[[proxies]]
name = "web"
type = "tcp"
localIP = "127.0.0.1"
localPort = 3000
remotePort = xxxxx
```

