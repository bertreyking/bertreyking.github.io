# Ansible 常规使用

### 常用命令

```
ansible $hostlist -m shell -k -a 'hostname'
ansible $hostlist -m command -k -a 'hostname'
ansible $hostlist -m script -k -a /root/hostname.sh
ansible $hostlist -m copy -k -a 'src=/root/hostname.sh dest=/root/'
```

## ansible 常用模块

```
- file       # 创建文件
- shell      # 在节点中执行 shell / command
- command    # 在节点中执行 command
- copy       # 拷贝文件到节点中
- script     # 将 ansible 节点中脚本发送到被控节点并执行
- mail       # 邮件发送
- raw        # 支持管道
```

## ansible-playbook 示例

```
- hosts: cal
  gather_facts: no
  tasks:
  - name: CreateDir
    file:
      path: /root/testDir
      state: directory
    register: mk_dir
  - debug: var=mk_dir.diff.after.path
  
- register: 表示将 file模块执行的结果注入到mk_dir里面.以json格式输出
- debug:

常用参数:
- var: 将某个任务执行的输出作为变量传递给debug模块，debug会直接将其打印输出
- msg: 输出调试的消息
- verbosity：debug的级别（默认是0级，全部显示）
```
