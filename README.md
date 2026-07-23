# MonaDrive

基于 GitHub 的私有云盘 — 将本地文件夹同步到你的私有 GitHub 仓库。

## 功能

- **自动安装依赖** — 启动时检测缺失的 Python 包，自动 pip install
- **GitHub OAuth 登录** — 一键浏览器授权，无需手动创建 Token
- **多仓库侧边栏** — 新建（可选私有/公开）/重命名/删除仓库，悬停操作，↻ 刷新
- **文件管理器** — 内置侧边栏，添加/删除/重命名文件，悬停显示操作按钮，↻ 刷新
- **拖放上传** — 拖放文件或文件夹到窗口任意位置即可复制到当前目录
- **推送/拉取** — Push = 本地覆盖远端，Pull = 远端覆盖本地（含超时保护）
- **智能推送** — 即使无新变更，也会推送本地未推送的已有提交
- **提交回滚** — 推送失败自动撤销本地提交，随时可重试
- **远端检测** — 仓库被删除后自动感知，提示重新初始化
- **离线容忍** — 远端不可达时仍可浏览本地文件，网络恢复后自动同步
- **状态提示** — 实时显示本地领先/落后远端提交数
- **大文件检测** — 自动扫描 >100 MB 文件并在推送时警告排除
- **暗色/亮色主题** — 平滑渐变切换，侧边栏自适应主题
- **中英文双语** — 完整双语界面，即时切换
- **Git 自动下载** — 首次启动未安装 Git 时自动下载 Portable Git
- **安全存储** — Token 通过 keyring 存入 Windows 凭据管理器，绝不明文

## 安装

### 环境要求

- Python 3.10+
- Windows 10+
- Git（首次启动未安装会自动下载）

### 运行

```bash
python main.py
```

首次启动会自动检测并安装缺失的依赖，无需手动 `pip install`。

### 注册 GitHub OAuth 应用

1. 前往 [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. 点击 **New OAuth App**
3. 填写：
   - **Application name**：`MonaDrive`（或任意名称）
   - **Homepage URL**：`http://127.0.0.1`
   - **Authorization callback URL**：`http://127.0.0.1/callback`
4. 点击 **Register application**
5. 生成 **Client Secret**
6. 在 MonaDrive 登录界面输入 `Client ID` 和 `Client Secret`

## 使用说明

1. **登录** — 输入 OAuth 应用凭据，点击"Sign in with GitHub"
2. **选择仓库** — 侧边栏新建仓库（可选私有），或选取已有仓库，悬停可重命名/删除，↻ 刷新
3. **选择文件夹** — 指定本地目录（已有文件也可以），点击"初始化选中仓库"
4. **同步** — 直接在文件管理器中修改文件 → 点击 Push 推送到远端；点击 Pull 从远端覆盖本地
5. **状态栏** — 实时显示 "N 文件已修改" / "N 个新文件" / "本地领先 N 提交" / "落后 N 提交"

## 技术栈

| 组件 | 技术 |
|------|------|
| GUI | PyQt6 + QSS |
| Git 操作 | GitPython |
| GitHub API | PyGithub |
| Token 存储 | keyring（Windows 凭据管理器） |
| 字体 | Monocraft（像素等宽字体） |
| 国际化 | 自定义字典翻译 |

## 注意事项

- 仓库默认**私有**（可选公开）
- Token 权限：`repo`、`delete_repo`（仓库读写与删除）
- GitHub 单文件限制 100 MB，单仓库约 5 GB
- 同步操作需要稳定的网络连接
- 可在文件管理器中直接修改文件，Push 时自动检测并提交
- 初始化不会自动拉取远端文件，由用户手动选择 Push 还是 Pull
- 点击头像/用户名可切换仓库或返回主界面

## 致谢

- 字体 [Monocraft](https://github.com/IdreesInc/Monocraft) by IdreesInc — Minecraft 风格像素等宽字体

## 许可

MIT
