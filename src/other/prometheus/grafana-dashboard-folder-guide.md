# Grafana Operator（integreatly.org/v1alpha1）创建 Dashboard 指定目录说明

## 1. 背景

在 Kubernetes 环境中，如果通过 Grafana Operator 管理
Dashboard，通常使用：

``` yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
```

该方式通过 Kubernetes CR（Custom Resource）声明式管理 Grafana
Dashboard。

默认情况下，如果不指定目录，Dashboard 通常会进入 Grafana 默认目录。

`integreatly.org/v1alpha1` 版本可以通过 `spec.customFolderName` 指定
Dashboard 所属 Folder。

------------------------------------------------------------------------

## 2. 指定 Dashboard 目录

示例：

``` yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard

metadata:
  name: insight-grafana-dashboard-redis-instance
  namespace: insight-system
  labels:
    operator.insight.io/managed-by: insight

spec:
  customFolderName: "Middleware"

  json: |-
    {
      "title": "Redis Instance Dashboard",
      "uid": "redis-instance",
      "schemaVersion": 39,
      "version": 1,
      "panels": []
    }
```

创建后 Grafana 目录结构：

    Dashboards
    └── Middleware
        └── Redis Instance Dashboard

------------------------------------------------------------------------

## 3. 多级目录

Grafana 支持通过 `/` 创建多级目录：

``` yaml
spec:
  customFolderName: "Middleware/Redis"
```

效果：

    Dashboards

    └── Middleware
        └── Redis
            └── Redis Instance Dashboard

------------------------------------------------------------------------

## 4. 使用 ConfigMap 管理 Dashboard JSON

生产环境推荐将 Dashboard JSON 独立保存到 ConfigMap。

### ConfigMap

``` yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: redis-dashboard-json
  namespace: insight-system

data:
  redis-dashboard.json: |-
    {
      "title": "Redis Instance Dashboard",
      "uid": "redis-instance",
      "panels": []
    }
```

### GrafanaDashboard

``` yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard

metadata:
  name: redis-instance-dashboard
  namespace: insight-system

spec:
  customFolderName: "Middleware/Redis"

  configMapRef:
    name: redis-dashboard-json
    key: redis-dashboard.json
```

------------------------------------------------------------------------

## 5. 验证配置

查看 Dashboard CR：

``` bash
kubectl get grafanadashboard \
-n insight-system \
redis-instance-dashboard -o yaml
```

确认：

``` yaml
spec:
  customFolderName: Middleware/Redis
```

------------------------------------------------------------------------

查看 Grafana Operator 日志：

``` bash
kubectl logs -n <operator-namespace> \
deployment/grafana-operator
```

------------------------------------------------------------------------

## 6. 常见问题

### 6.1 Dashboard 仍然显示在 General

检查字段位置。

正确：

``` yaml
spec:
  customFolderName: "Redis"

  json: |-
```

错误：

``` yaml
json:
  customFolderName: Redis
```

------------------------------------------------------------------------

### 6.2 JSON 中配置 Folder 是否有效

无效：

``` json
{
  "title": "Redis Dashboard",
  "folder": "Redis"
}
```

原因：

Dashboard JSON 只负责 Dashboard 内容，例如：

-   Panel
-   Query
-   Variable
-   Annotation

Folder 属于 Grafana 元数据，由 Operator 创建 Dashboard 时处理。

------------------------------------------------------------------------

### 6.3 修改目录后没有变化

如果 Dashboard 已经存在，修改：

``` yaml
customFolderName
```

可能不会移动已有 Dashboard。

建议删除后重新创建：

``` bash
kubectl delete grafanadashboard \
redis-instance-dashboard \
-n insight-system
```

然后：

``` bash
kubectl apply -f dashboard.yaml
```

------------------------------------------------------------------------

## 7. 检查 CRD 是否支持

查看字段：

``` bash
kubectl explain grafanadashboard.spec
```

或者：

``` bash
kubectl get crd grafanadashboards.integreatly.org -o yaml \
| grep customFolderName
```

如果输出：

    customFolderName

表示当前版本支持。

------------------------------------------------------------------------

## 8. 推荐目录规划

    Grafana

    ├── Kubernetes
    │   ├── Cluster
    │   ├── Node
    │   ├── Pod
    │   └── Ingress
    │
    ├── Middleware
    │   ├── Redis
    │   ├── MySQL
    │   ├── Kafka
    │   └── Elasticsearch
    │
    ├── Business
    │   ├── EC
    │   └── Delivery
    │
    └── Network
        ├── Zabbix
        └── NPM

示例：

``` yaml
spec:
  customFolderName: "Middleware/MySQL"
```

------------------------------------------------------------------------

## 9. 总结

  需求                  配置
  --------------------- --------------------------------------
  指定 Dashboard 目录   `spec.customFolderName`
  一级目录              `customFolderName: Redis`
  多级目录              `customFolderName: Middleware/Redis`
  JSON 中配置 Folder    不支持
  生产环境推荐          ConfigMap + GrafanaDashboard

对于：

``` yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
```

直接增加：

``` yaml
spec:
  customFolderName: "Middleware/Redis"
```

即可实现 Dashboard 自动归档到指定 Grafana Folder。
