# Grafana 子路径

- 在使用代理的场景下，可能会涉及到子路径的问题，因为同意域名下面不能有多个 /，否则会导致转发失败

- k8s ingress 规则中，同一个域名也会出现上面的问题，其本质是一个问题
  - 提交允许换个域名即可

# 如何配置

```ini
    # If you use reverse proxy and sub path specify full url (with sub path)
    root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana/

    # Serve Grafana from subpath specified in `root_url` setting. By default it
    is set to `false` for compatibility reasons.
    serve_from_sub_path = true
```

- /grafana/ 在这里是加入的 uri 子路径