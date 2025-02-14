
## 使用 [GitHub Pages](https://docs.github.com/en/pages/quickstart) 快速发布

参阅 [mdBook 官方安装文档](https://rust-lang.github.io/mdBook/format/theme/index.html)

- [安装](https://rust-lang.github.io/mdBook/guide/installation.html)
- [配置](https://rust-lang.github.io/mdBook/format/configuration/renderers.html#html-renderer-options)

## 建站 [参考链接](https://medium.com/medialesson/documentation-in-github-pages-with-mkdocs-readthedocs-theme-920b283215d1)

## Git [安装](https://git-scm.com/book/zh/v2/%E8%B5%B7%E6%AD%A5-%E5%AE%89%E8%A3%85-Git)、[初始化](https://git-scm.com/book/zh/v2/%E8%B5%B7%E6%AD%A5-%E5%88%9D%E6%AC%A1%E8%BF%90%E8%A1%8C-Git-%E5%89%8D%E7%9A%84%E9%85%8D%E7%BD%AE)

- [Mac 中 Git 安装与 GitHub 基本使用](https://www.jianshu.com/p/7edb6b838a2e)
- [生成新的 SSH-key 并且添加到 ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- 每年需要更新下 token，个人用户 setting 中 dev 开发创建 token，并设置某个 repo 访问权限，然后 git clone 时使用 https，git push 提交时提示输入用户密码/密码 token
- git push 报错 error: RPC failed; HTTP 400 curl 22 The requested URL returned error: 400
  ```shell
  # 设置下 http 的 buffer，再次 push 即可
  git config http.postBuffer 524288000 or git config --global http.postBuffer 157286400
  git push or git push --all
  ```
