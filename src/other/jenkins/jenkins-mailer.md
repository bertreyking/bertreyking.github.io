# Jenkins 邮件通知

## 系统管理员邮箱配置

- 配置文件 `jenkins.model.JenkinsLocationConfiguration.xml`

```shell
<?xml version='1.1' encoding='UTF-8'?>
<jenkins.model.JenkinsLocationConfiguration>
  <adminAddress>xxx管理系统 &lt;xxx@163.com&gt;</adminAddress>
  <jenkinsUrl>http://xxx-jenkins:80/</jenkinsUrl>
```

## 邮件通知配置

- 配置文件 `hudson.tasks.Mailer.xml`
  - 下面的配置邮箱是侧免密配置，不需要认证，其它环境不一定适配，可以到 jenkins > 系统管理 > 邮件通知中更改即可

```shell
<?xml version='1.1' encoding='UTF-8'?>
<hudson.tasks.Mailer_-DescriptorImpl plugin="mailer@457.v3f72cb_e015e5">
  <defaultSuffix>@163.com</defaultSuffix>
  <replyToAddress>no-reply@k8s.io</replyToAddress>
  <smtpHost>smtp.163.com</smtpHost>
  <useSsl>false</useSsl>
  <useTls>false</useTls>
  <smtpPort>25</smtpPort>
  <charset>UTF-8</charset>
```

