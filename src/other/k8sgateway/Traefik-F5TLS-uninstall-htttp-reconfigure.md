# Traefik 由 F5 统一卸载 TLS 后改为 HTTP 的配置说明

## 1. 问题背景

当前 Kubernetes 集群使用 Traefik 作为入口控制器，原 Traefik 同时监听 HTTP 和 HTTPS，并配置了以下能力：

- `web` EntryPoint 监听 `80`；
- `websecure` EntryPoint 监听 `443`；
- 所有进入 `web:80` 的请求强制跳转到 `websecure:443`；
- Traefik 在 `websecure` 上完成 TLS 终止；
- Traefik Dashboard 通过 `IngressRoute` 对外提供访问。

后续调整为由 F5 统一管理和卸载 HTTPS 证书，F5 解密请求后，通过 HTTP 将流量转发到 Traefik。因此，Traefik 不再需要监听或处理 HTTPS，也不能继续执行 HTTP 到 HTTPS 的重定向。

目标请求链路如下：

```text
客户端 HTTPS:443
    ↓
F5：TLS 终止、证书管理
    ↓ HTTP:80
Traefik：HTTP 路由
    ↓
Kubernetes Service / Pod
```

> 对客户端来说，业务地址仍然是 `https://`；只有 F5 到 Traefik 这一段改为 HTTP。

---

## 2. 原配置存在的问题

Traefik 当前包含以下启动参数：

```yaml
- --entryPoints.web.address=:80/tcp
- --entryPoints.websecure.address=:443/tcp
- --entryPoints.web.http.redirections.entryPoint.to=:443
- --entryPoints.web.http.redirections.entryPoint.scheme=https
- --entryPoints.web.http.redirections.entryPoint.permanent=true
- --entryPoints.websecure.http.tls=true
```

其中：

- `web.http.redirections` 会把所有进入 Traefik 80 端口的请求重定向到 HTTPS；
- `websecure.http.tls=true` 表示 Traefik 在 443 入口执行 TLS 终止；
- F5 已经完成 TLS 终止后，如果仍将请求发送到 Traefik 80，Traefik又会把请求重定向回 443；
- 如果 `IngressRoute` 只绑定 `web`，请求重定向到 `websecure` 后无法匹配对应 Router，最终可能返回 Traefik 404；
- 如果 F5 的后端 Pool 只配置了 Traefik 80 端口，还可能出现重定向循环或访问异常。

因此，将证书迁移到 F5 后，需要同时取消 Traefik 的 HTTPS 重定向和 TLS 配置。

---

## 3. Traefik 启动参数修改

### 3.1 必须删除的参数

删除 HTTP 到 HTTPS 的重定向配置：

```yaml
- --entryPoints.web.http.redirections.entryPoint.to=:443
- --entryPoints.web.http.redirections.entryPoint.scheme=https
- --entryPoints.web.http.redirections.entryPoint.permanent=true
```

删除 Traefik TLS 终止配置：

```yaml
- --entryPoints.websecure.http.tls=true
```

如果确定 Traefik 以后完全不再提供 443 入口，还可以删除：

```yaml
- --entryPoints.websecure.address=:443/tcp
```

### 3.2 修改后的关键启动参数

```yaml
containers:
  - name: traefik
    args:
      - --entryPoints.metrics.address=:9100/tcp
      - --entryPoints.traefik.address=:8080/tcp
      - --entryPoints.web.address=:80/tcp

      - --api.dashboard=true
      - --ping=true

      - --metrics.prometheus=true
      - --metrics.prometheus.entrypoint=metrics

      - --providers.kubernetescrd
      - --providers.kubernetescrd.allowCrossNamespace=true
      - --providers.kubernetescrd.allowEmptyServices=true

      - --providers.kubernetesingress
      - --providers.kubernetesingress.allowEmptyServices=true
      - --providers.kubernetesingress.ingressendpoint.publishedservice=traefik/traefik

      - --providers.kubernetesgateway
      - --providers.kubernetesgateway.statusaddress.service.name=traefik
      - --providers.kubernetesgateway.statusaddress.service.namespace=traefik

      - --log.level=INFO
      - --accesslog=true
      - --accesslog.fields.defaultmode=keep
      - --accesslog.fields.headers.defaultmode=drop
```

---

## 4. Dashboard IngressRoute 修改

Dashboard 应绑定到 HTTP `web` EntryPoint，并且不能再配置 `tls`。

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: traefik-dashboard
  namespace: traefik
spec:
  entryPoints:
    - web

  routes:
    - kind: Rule
      match: >-
        Host(`traefik-uat2.dominos.com.cn`) &&
        (PathPrefix(`/dashboard`) || PathPrefix(`/api`))
      middlewares:
        - name: dashboard-auth
      services:
        - kind: TraefikService
          name: api@internal
```

不要保留以下内容：

```yaml
tls: {}
```

客户端仍通过以下 HTTPS 地址访问：

```text
https://traefik-uat2.dominos.com.cn/dashboard/
```

但 F5 转发到 Traefik 的请求为：

```text
http://<Traefik地址>:80/dashboard/
```

### Dashboard 404 注意事项

Traefik Dashboard 的标准访问路径为：

```text
/dashboard/
```

需要特别注意：

- 不能只访问域名根路径 `/`，否则 `api@internal` 可能返回 404；
- `/dashboard/` 最后的 `/` 不要省略；
- 路由规则需要同时放行 `/dashboard` 和 `/api`；
- 未携带 BasicAuth 认证信息时返回 `401 Unauthorized`，说明路由和认证中间件已经正常生效，并不是故障。

---

## 5. Helm values.yaml 修改

当前 Traefik 资源由 Helm 管理，直接修改 Deployment 或 Helm 创建的 `IngressRoute`，可能在下次 `helm upgrade` 时被覆盖，因此应优先修改原始 `values.yaml`。

### 5.1 修改前备份

```bash
helm get values traefik -n traefik -o yaml \
  > traefik-values-before-http.yaml
```

同时保存当前完整清单：

```bash
helm get manifest traefik -n traefik \
  > traefik-manifest-before-http.yaml
```

### 5.2 关闭 web 重定向和 websecure TLS

从原 `values.yaml` 中删除类似配置：

```yaml
ports:
  web:
    redirections:
      entryPoint:
        to: websecure
        scheme: https
        permanent: true
```

将端口配置调整为：

```yaml
ports:
  web:
    expose:
      default: true
    exposedPort: 80
    protocol: TCP

  websecure:
    expose:
      default: false
    tls:
      enabled: false
```

说明：

- `web` 继续提供 HTTP 80 服务；
- `websecure.expose.default=false` 表示 Service 不再暴露 443；
- `websecure.tls.enabled=false` 表示不在该 EntryPoint 上启用 TLS；
- 不同 Chart 小版本的字段可能略有差异，升级前应使用 `helm show values` 与当前 values 对比确认；
- 如果原重定向参数来自 `additionalArguments`，还需要从 `additionalArguments` 中删除对应参数。

### 5.3 Dashboard Helm 配置

```yaml
ingressRoute:
  dashboard:
    enabled: true

    entryPoints:
      - web

    matchRule: >-
      Host(`traefik-uat2.dominos.com.cn`) &&
      (PathPrefix(`/dashboard`) || PathPrefix(`/api`))

    middlewares:
      - name: dashboard-auth
        namespace: traefik

    tls: null
```

如果 Chart 对 `tls: null` 的处理不符合预期，可以直接从 Dashboard 配置中删除整个 `tls` 字段，最终以生成的 `IngressRoute` 中不存在 `spec.tls` 为准。

### 5.4 执行 Helm 升级

```bash
helm upgrade traefik traefik/traefik \
  -n traefik \
  --version 37.3.0 \
  -f values.yaml
```

> 不建议在未确认历史 values 的情况下直接使用 `--reuse-values`，否则旧的 HTTPS 重定向配置可能被继续保留。

---

## 6. Kubernetes Service 检查

检查 Traefik Service 暴露的端口：

```bash
kubectl -n traefik get svc traefik -o yaml
```

目标状态：

- 对 F5 提供 HTTP 80 或对应的 HTTP NodePort；
- 不再需要对 F5 提供 HTTPS 443；
- F5 Pool Member 指向 Traefik HTTP 端口，而不是 Traefik 443。

如果使用 NodePort，可以执行：

```bash
kubectl -n traefik get svc traefik \
  -o jsonpath='{range .spec.ports[*]}{.name}{"\t"}{.port}{"\t"}{.nodePort}{"\n"}{end}'
```

---

## 7. F5 侧配置要求

F5 建议按照以下方式配置：

| 配置项 | 建议配置 |
| --- | --- |
| Virtual Server | 监听客户端 HTTPS 443 |
| Client SSL Profile | 配置域名证书并执行 TLS 终止 |
| Pool Member | 指向 Traefik HTTP 80 或 HTTP NodePort |
| 后端协议 | HTTP |
| Host 请求头 | 保留客户端原始 Host |
| X-Forwarded-Proto | 设置为 `https` |
| X-Forwarded-For | 保留或追加客户端真实 IP |
| 健康检查 | 使用 Traefik HTTP 健康检查地址 |

F5 应向 Traefik 传递：

```http
X-Forwarded-Proto: https
X-Forwarded-For: <客户端IP>
Host: <原始访问域名>
```

`X-Forwarded-Proto: https` 非常重要。虽然 F5 到 Traefik 使用 HTTP，但客户端实际使用的是 HTTPS。缺少该请求头可能导致：

- 后端应用生成 `http://` 回调地址；
- OAuth、SSO 登录回调地址错误；
- Cookie 的 `Secure` 属性判断异常；
- 应用产生 HTTP/HTTPS 重定向循环；
- 日志中记录的原始协议不准确。

---

## 8. Traefik 信任 F5 转发头

建议 Traefik 只信任 F5 的地址，不要无条件信任所有客户端传入的 `X-Forwarded-*` 请求头。

启动参数示例：

```yaml
- --entryPoints.web.forwardedHeaders.trustedIPs=<F5地址或网段>
```

例如：

```yaml
- --entryPoints.web.forwardedHeaders.trustedIPs=10.10.10.10/32
```

如果 F5 使用 SNAT Automap，应填写 F5 访问 Traefik 时实际使用的 SNAT 地址或网段。

不建议直接配置：

```yaml
- --entryPoints.web.forwardedHeaders.insecure=true
```

因为该配置会信任任意来源传入的转发请求头，存在伪造客户端 IP 或原始协议的风险。

---

## 9. 其他业务路由检查

除了 Dashboard，还需要检查集群内其他路由是否仍然依赖 `websecure` 或 TLS。

### 9.1 检查 IngressRoute

```bash
kubectl get ingressroute -A -o json |
jq -r '
  .items[] |
  select(
    (.spec.tls != null) or
    ((.spec.entryPoints // []) | index("websecure"))
  ) |
  [.metadata.namespace, .metadata.name,
   ((.spec.entryPoints // []) | join(",")),
   (if .spec.tls == null then "no-tls" else "tls" end)] |
  @tsv'
```

需要逐个调整为：

```yaml
spec:
  entryPoints:
    - web
```

并删除：

```yaml
spec:
  tls: {}
```

### 9.2 检查标准 Ingress

```bash
kubectl get ingress -A -o json |
jq -r '
  .items[] |
  select(
    ((.spec.tls // []) | length > 0) or
    (.metadata.annotations["traefik.ingress.kubernetes.io/router.tls"] == "true") or
    (.metadata.annotations["traefik.ingress.kubernetes.io/router.entrypoints"] // "" | contains("websecure"))
  ) |
  [.metadata.namespace, .metadata.name] |
  @tsv'
```

需要根据实际情况：

- 删除 `spec.tls`；
- 删除 `traefik.ingress.kubernetes.io/router.tls: "true"`；
- 将 Router EntryPoint 修改为 `web`。

### 9.3 检查 HTTPS 重定向 Middleware

```bash
kubectl get middleware -A -o json |
jq -r '
  .items[] |
  select(.spec.redirectScheme != null) |
  [.metadata.namespace, .metadata.name,
   (.spec.redirectScheme.scheme // "")] |
  @tsv'
```

如果 Middleware 仍然将请求重定向到 HTTPS，需要确认它是否已经没有必要。通常在 F5 统一负责 HTTPS 的场景下，外部 HTTP 到 HTTPS 的跳转也应由 F5 完成，而不是由 Traefik完成。

---

## 10. 修改后验证

### 10.1 检查 Traefik 启动参数

```bash
kubectl -n traefik get deploy traefik -o json |
jq -r '
  .spec.template.spec.containers[] |
  select(.name == "traefik") |
  .args[]' |
grep -Ei 'websecure|redirection|tls'
```

不应该再出现：

```text
entryPoints.web.http.redirections
entryPoints.websecure.http.tls=true
```

如果 Helm 仍保留了一个未暴露、未启用 TLS 的 `websecure.address`，不会影响 `web` 的 HTTP 请求；如果要求彻底关闭该监听端口，再根据当前 Chart 的端口模板将整个 `websecure` EntryPoint 删除。

### 10.2 集群内部绕过 F5 验证

```bash
curl -I \
  -H 'Host: traefik-uat2.dominos.com.cn' \
  http://traefik.traefik.svc.cluster.local/dashboard/
```

预期结果：

- 返回 `401 Unauthorized`：路由已匹配，BasicAuth 正常生效；
- 携带正确认证信息后返回 `200` 或正常页面内容；
- 不应再返回指向 `https://...:443` 的 301/308 重定向。

携带 BasicAuth 验证：

```bash
curl -I \
  -u '<用户名>:<密码>' \
  -H 'Host: traefik-uat2.dominos.com.cn' \
  http://traefik.traefik.svc.cluster.local/dashboard/
```

### 10.3 通过 F5 验证

```bash
curl -kI https://traefik-uat2.dominos.com.cn/dashboard/
```

判断方式：

| 返回结果 | 含义 |
| --- | --- |
| `401 Unauthorized` | 已命中 Traefik Dashboard 和认证中间件 |
| `200 OK` | 访问正常，或已携带正确认证信息 |
| `301/308` 到 Traefik 443 | Traefik 仍残留 HTTPS 重定向配置 |
| `404 Not Found` | Host、路径或 EntryPoint 没有匹配 |
| `502/503` | F5 Pool、Traefik Service、NodePort 或后端健康状态异常 |

### 10.4 检查 Traefik 日志

```bash
kubectl -n traefik logs deploy/traefik \
  --since=10m |
grep 'traefik-uat2.dominos.com.cn'
```

重点确认：

- 请求是否进入 `web` EntryPoint；
- Host 是否保持为原始域名；
- 是否仍有 HTTPS 重定向；
- 返回状态码是 401、200、404 还是 5xx。

---

## 11. 推荐实施顺序

```text
备份 Helm values 和 manifest
    ↓
确认 F5 已配置证书和 HTTPS Virtual Server
    ↓
确认 F5 Pool 指向 Traefik HTTP 端口
    ↓
取消 Traefik 的 HTTP→HTTPS 重定向
    ↓
关闭 websecure TLS 和 443 暴露
    ↓
IngressRoute/Ingress 统一切换到 web
    ↓
集群内部验证 HTTP 路由
    ↓
通过 F5 验证客户端 HTTPS
    ↓
观察访问日志和业务回调
```

建议先在 UAT 环境验证，确认业务登录、回调、Cookie、真实客户端 IP 和访问日志正常后，再应用到生产环境。

---

## 12. 回滚方案

如果修改后出现异常，可使用修改前备份的 values 回滚：

```bash
helm upgrade traefik traefik/traefik \
  -n traefik \
  --version 37.3.0 \
  -f traefik-values-before-http.yaml
```

也可以查看 Helm 历史版本：

```bash
helm history traefik -n traefik
```

回滚到指定 Revision：

```bash
helm rollback traefik <REVISION> -n traefik
```

回滚后需要同步确认：

- Traefik 是否重新暴露 443；
- TLS 配置和证书是否恢复；
- F5 Pool 的后端协议是否与 Traefik 当前配置一致；
- 避免 F5 与 Traefik 同时进行相互冲突的重定向。

---

## 13. 最终结论

当 HTTPS 证书统一放在 F5 上时，Traefik 应作为 F5 后端的纯 HTTP 七层路由使用。改造的核心是：

1. 删除 Traefik `web` 到 `websecure` 的强制重定向；
2. 关闭 Traefik `websecure` 的 TLS 和 443 对外暴露；
3. 所有 `IngressRoute` 和 `Ingress` 统一绑定 HTTP `web` EntryPoint；
4. F5 监听客户端 443，并将解密后的 HTTP 请求转发到 Traefik 80；
5. F5 保留原始 Host，并正确传递 `X-Forwarded-Proto` 和 `X-Forwarded-For`；
6. Traefik 只信任 F5 的转发地址，避免转发请求头被伪造。

完成以上调整后，客户端继续通过 HTTPS 访问，证书由 F5 统一管理，Traefik 内部不再处理 TLS。
