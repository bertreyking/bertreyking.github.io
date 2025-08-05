# gitlab 自定义 subpath

- 修改 gitlab.rb 配置文件

```yaml
vi /etc/gitlab/gitlab.rb

external_url: http://192.168.0.110:32255/gitlab # 这里配置修改下即可，或者是不是有环境变量可以替换

http://192.168.0.110:32255/gitlab
http 协议  ip地址，这个也就是后续外部访问时的IP/域名、端口 、子路径就是 /gitlab，后续 gitlab 就会以该端口对外暴露
```

