# Gitlab 仓库安装 (centos7.9)

## 安装 docker

1. 略，毛毛雨啦，详情参考 [Install][install]

2. docker 部署

   - 创建 repo 目录来存放 gitlab 数据

     ```shell
     mkdir /gitlab-data
     export GITLAB_HOME=/gitlab-data
     ```

   - 启动容器 [dockerhub][image]

     ```shell
     sudo docker run --detach \
       --hostname mawb.gitlab.com \
       --publish 443:443 --publish 80:80 \
       --name mawb.gitlab \
       --restart always \
       --volume $GITLAB_HOME/config:/etc/gitlab \
       --volume $GITLAB_HOME/logs:/var/log/gitlab \
       --volume $GITLAB_HOME/data:/var/opt/gitlab \
       --shm-size 256m \
       gitlab/gitlab-ce:14.8.6-ce.0
     ```


   - 初始密码

     ```shell
     docker exec -it $containerID /bin/cat /etc/gitlab/initial_root_password
     ```

3. 允许 80、443 访问，并禁止 IP 访问

   - 允许 80、443

     ```shell
     - gitlab 使用 gitlab.rb 的形式来自定义 gitlab_server 配置
     - 修改以下配置
     [root@gitlab-repo-1 data]# pwd
     /gitlab-home/data
     [root@gitlab-repo-1 data]# cat config/gitlab.rb | grep -v '^#' | grep '[a-z]'
     external_url 'https://mawb.gitlab.com'                                            # 域名访问，也可以 IP，会自动生成 nginx 配置
     nginx['custom_nginx_config'] = "include /var/opt/gitlab/nginx/conf/http.conf;"    # 自定义 nginx 配置(容器内路径)，开启 80，所以修改
     letsencrypt['enable'] = false                                                     # 禁用 letsencrypt
     letsencrypt['auto_renew'] = false                                                 # 禁用自动续签证书，这步可以不用
     ```

   - 禁止 IP 访问 [disalble_IP_access][disalble_IP_access]

     ```nginx
     - 需要在 nginx 配置文件中加入以下配置
     server {
       listen *:80 default_server;
       listen *:443 default_server;
         
       server_name _;
       return 403;
       ssl_certificate /etc/gitlab/ssl/mawb.gitlab.com.crt;
       ssl_certificate_key /etc/gitlab/ssl/mawb.gitlab.com.key;
     
     }
     ```
   - [http.conf][http]
   - [https.conf][https] 

   - 自签证书 [ssl][ssl]

   - 配置生效

     ```shell
     - 容器内查看当前服务状态
     root@10:~# gitlab-ctl status
     run: alertmanager: (pid 1753) 156934s; run: log: (pid 1092) 157346s
     run: gitaly: (pid 1824) 156918s; run: log: (pid 563) 157688s
     run: gitlab-exporter: (pid 1713) 156946s; run: log: (pid 1024) 157394s
     run: gitlab-kas: (pid 5119) 155210s; run: log: (pid 822) 157654s
     run: gitlab-workhorse: (pid 1699) 156947s; run: log: (pid 978) 157420s
     run: grafana: (pid 5137) 155209s; run: log: (pid 1486) 157047s
     run: logrotate: (pid 12675) 2906s; run: log: (pid 508) 157706s
     run: nginx: (pid 12501) 3007s; run: log: (pid 1000) 157416s
     run: postgres-exporter: (pid 1762) 156934s; run: log: (pid 1123) 157330s
     run: postgresql: (pid 595) 157673s; run: log: (pid 607) 157671s
     run: prometheus: (pid 1723) 156945s; run: log: (pid 1064) 157362s
     run: puma: (pid 5034) 155360s; run: log: (pid 922) 157449s
     run: redis: (pid 514) 157702s; run: log: (pid 525) 157699s
     run: redis-exporter: (pid 1716) 156946s; run: log: (pid 1045) 157377s
     run: sidekiq: (pid 7973) 5180s; run: log: (pid 938) 157438s
     run: sshd: (pid 32) 157754s; run: log: (pid 31) 157754s
     
     - 重新加载配置
     gitlab-ctl reconfigure
     
     - 对 ningx 的修改，也可以单独重启 nginx
     gitlab-ctl restart nginx && gitlab-ctl status nginx
     ```
   
   - 重置 root 密码
   
     ```shell
     - 进入容器内部
     root@mawb:/# gitlab-rake "gitlab:password:reset[root]"
     Enter password: 
     Confirm password: 
     Password successfully updated for user with username root.
     - 重启容器即可
     ```
   
     


[install]:https://docs.docker.com/engine/install/centos/

[image]: https://hub.docker.com/r/gitlab/gitlab-ce/tags?page=1&name=14.8.6

[ssl]: https://githubshirongxin.github.io/Gitlab%E4%BD%BF%E7%94%A8%E8%87%AA%E7%AD%BE%E5%90%8D%E8%AF%81%E4%B9%A6%E5%BC%80%E5%90%AFhttps/

[disalble_IP_access]:https://wsgzao.github.io/post/nginx-default-server/

[http]: https://raw.githubusercontent.com/bertreyking/bertreyking.github.io/main/src/other/gitlab/http.conf
[https]: https://raw.githubusercontent.com/bertreyking/bertreyking.github.io/main/src/other/gitlab/gitlab-http.conf
