# nexus 初尝试

1. docker 部署 nexus

   ```shell
   docker run -d -p 8081:8081 --name nexus sonatype/nexus:oss
   ```

2. 浏览器访问
   - http://10.29.14.190:8081/nexus
3. 创建 hosted site 站点，可以当作一个文件站点使用，让用户 curl or wget 下载
   - 略，登录后 admin/admin123、[Repositories](http://10.29.14.190:8081/nexus/#) Add 添加即可

4. 上传文件

   ```shell
   mawb:Downloads kingskye$ curl -v --user 'admin:admin123' --upload-file cdap-data-paas.zip http://10.29.14.190:8081/nexus/content/sites/javarepo/cdap-data-paas.zip
   *   Trying 10.29.14.190:8081...
   * Connected to 10.29.14.190 (10.29.14.190) port 8081
   * Server auth using Basic with user 'admin'
   > PUT /nexus/content/sites/javarepo/cdap-data-paas.zip HTTP/1.1
   > Host: 10.29.14.190:8081
   > Authorization: Basic YWRtaW46YWRtaW4xMjM=
   > User-Agent: curl/8.7.1
   > Accept: */*
   > Content-Length: 200194056
   > Expect: 100-continue
   > 
   < HTTP/1.1 100 Continue
   < 
   * upload completely sent off: 200194056 bytes
   < HTTP/1.1 201 Created
   < Date: Fri, 28 Mar 2025 13:52:00 GMT
   < Server: Nexus/2.15.2-03
   < X-Frame-Options: SAMEORIGIN
   < X-Content-Type-Options: nosniff
   < Accept-Ranges: bytes
   < Content-Security-Policy: sandbox allow-forms allow-modals allow-popups allow-presentation allow-scripts allow-top-navigation
   < X-Content-Security-Policy: sandbox allow-forms allow-modals allow-popups allow-presentation allow-scripts allow-top-navigation
   < Content-Length: 0
   < 
   * Connection #0 to host 10.29.14.190 left intact
   ```

5. 查看文件
   - http://10.29.14.190:8081/nexus/content/sites/javarepo/ 浏览器访问，可以看到文件

# nexus 使用场景

- 可以配置各种源的代理
  - maven 源
  - python pip 源
  - linux 不通发行版的 sources
  - docker registry
  - site 站点