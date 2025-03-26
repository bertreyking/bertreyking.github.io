# master 分支修改推送至 dev 分支

- 本意是修改 dev 分支的 code，修改完成后，发现 clone 错了分支，于是才会有后面的步骤

你可以按照以下步骤操作：

1. **确认当前分支**（你可能在 `main` 或 `master`）：

   ```bash
   git branch
   ```

   如果当前在 `main`，你需要切换到 `dev`。

2. **切换到 `dev` 分支**（如果本地没有 `dev` 分支，需要先创建并追踪远程分支）：

   ```bash
   git checkout -b dev origin/dev
   ```

   或者，如果本地已有 `dev` 分支：

   ```bash
   git checkout dev
   git pull origin dev  # 确保是最新的
   ```

3. **将修改从 `main` 复制到 `dev`**： 如果你的修改已经提交，但还在 `main` 分支，可以使用 `cherry-pick`：# 我的还没 commit，直接后的后面的步骤

   ```bash
   git checkout dev
   git cherry-pick <commit-id>
   ```

   或者如果你还没有 commit，直接用 `stash` 临时保存后切换：

   ```bash
   git stash
   git checkout dev
   git stash pop
   ```

4. **推送到远程 `dev` 分支**：

   ```bash
   git add .
   git commit -m "你的提交信息"
   git push origin dev
   ```

这样，你的修改就被提交到 `dev` 分支，而不会影响 `main` 分支。