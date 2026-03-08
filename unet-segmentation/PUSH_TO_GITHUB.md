# 推送到新 GitHub 仓库

本地已做成独立仓库并完成首次提交，远程已设为：`https://github.com/bistuwangqiyuan/unet-segmentation.git`。

## 你需要做的（仅一次）

1. **在 GitHub 上新建仓库**
   - 打开 https://github.com/new
   - **Repository name** 填：`unet-segmentation`（或你想要的名称）
   - 选择 **Public**
   - **不要**勾选 “Add a README file” / “Add .gitignore”
   - 直接点 **Create repository**

2. **若仓库名或用户名不同，请改远程地址**
   ```bash
   cd "c:\Users\wangqiyuan\project\cursor\超声结题\soundsofts\unet-segmentation"
   git remote set-url origin https://github.com/你的用户名/你的仓库名.git
   ```

3. **推送到 GitHub**
   ```bash
   cd "c:\Users\wangqiyuan\project\cursor\超声结题\soundsofts\unet-segmentation"
   git push -u origin main
   ```
   按提示登录或使用 Personal Access Token 即可。

完成以上步骤后，本项目会出现在你的 GitHub 账号下作为独立仓库。
