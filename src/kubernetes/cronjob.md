# [Cron](https://kubernetes.io/zh-cn/docs/concepts/workloads/controllers/cron-jobs/)Job、[Job](https://kubernetes.io/zh-cn/docs/concepts/workloads/controllers/job/) 资源示例

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello
spec:
  suspend: true # 挂起 cronjob，不会影响已经开始的任务
  schedule: "* * * * *" # 每分钟执行一次
  successfulJobsHistoryLimit: 2 # 保留历史成功数量
  failedJobsHistoryLimit: 3 # 保留历史失败数量
  jobTemplate: # kind: job
    spec:
      suspend: true # 挂起 job (true 时运行中 pod 被终止，恢复时 activeDeadlineSeconds 也会重新计时)
      completions: 5  default: 1 # 完成次数
      parallelism: 2  default: 1 # 并行个数
      backoffLimit: 2 default: 6 # 重试次数 (重启时间按指数曾长<10、20、30>.最多6m)
      activeDeadlineSeconds: 20 # job 最大的生命周期，时间到停止所有相关 pod (Job 状态更新为 type: Failed、reason: DeadlineExceeded)
      template:
        spec:
          containers:
          - name: hello
            image: busybox:1.28
            imagePullPolicy: IfNotPresent
            command:
            - /bin/sh
            - -c
            - date; echo Hello from the Kubernetes cluster
          restartPolicy: OnFailure # 控制 pod 异常时的动作,重启、异常重启、从不重启

- 有关时区问题如果 cronjob 没有明确指定，那么就按照 kube-controller-manger 指定的时区
```

