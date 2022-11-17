# 常用模块
- file
- shell
- command
- copy
- script
- mail
- raw
# ansible-playbook
```
示例playbook
- hosts: cal
  gather_facts: no
  tasks:
  - name: CreateDir
    file:
      path: /root/testDir
      state: directory
    register: mk_dir
  - debug: var=mk_dir.diff.after.path
  
  1. register: 表示将 file模块执行的结果注入到mk_dir里面.以json格式输出
  2. debug:
  常用参数
  var: 将某个任务执行的输出作为变量传递给debug模块，debug会直接将其打印输出
  msg: 输出调试的消息
  verbosity：debug的级别（默认是0级，全部显示）
 ```
