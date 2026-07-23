"""MonaDrive internationalization — Chinese (zh) / English (en) string tables."""

_translations = {
    "en": {
        "app.title": "MonaDrive",
        "app.tagline": "Private cloud storage powered by GitHub",

        "login.oauth_hint": (
            "Register an OAuth App at github.com/settings/developers\n"
            "Set callback URL to http://127.0.0.1/callback"
        ),
        "login.client_id": "Client ID",
        "login.client_secret": "Client Secret",
        "login.signin": "Sign in with GitHub",
        "login.remember": "Remember me",
        "login.waiting": "Waiting for authorization...",
        "login.browser_opened": "Browser opened -- complete authorization there",
        "login.missing_creds": "Enter both Client ID and Client Secret",
        "login.success": "Signed in",
        "login.failed": "Failed: {}",

        "dash.repo": "Repository",
        "dash.repo_name": "Repository name",
        "dash.repo_placeholder": "e.g. my-monadrive-files",
        "dash.folder": "Local folder",
        "dash.folder_placeholder": "Select a folder...",
        "dash.browse": "Browse",
        "dash.initialize": "Initialize",
        "dash.setup_title": "Configure your repository",
        "dash.pull": "Pull",
        "dash.push": "Push",
        "dash.working": "Working...",
        "dash.log": "Log",
        "dash.logout": "Log out",
        "dash.not_init": "Not initialized",
        "dash.status_modified": "{} modified",
        "dash.status_new": "{} new",
        "dash.status_clean": "No local changes",
        "dash.status_behind": "{} commits behind remote",
        "dash.status_offline": "Remote unreachable",
        "dash.signed_in": "Signed in as {}",
        "dash.init_failed": "Init failed: {}",
        "dash.reconnected": "Reconnected to local repository",
        "dash.connecting": "Connecting to remote repository...",
        "dash.reconnect_failed": "Reconnect failed: {}",
        "dash.reinit": "Switch / Re-initialize",
        "dash.avatar_reinit": "Click to reconfigure repository",
        "dash.avatar_back": "Click to go back to main",
        "dash.remote_gone": "Remote repository has been deleted. Please re-initialize.",
        "dash.cloned": "Cloned to {}",
        "dash.repo_created": "Repository: {}",
        "dash.repos": "Repositories",
        "dash.new_repo": "+ New Repository",
        "dash.new_repo_name": "Repository name:",
        "dash.new_repo_private": "Private",
        "dash.loading_repos": "Loading repositories...",
        "dash.rename_repo": "Rename Repository",
        "dash.delete_repo": "Delete Repository",
        "dash.confirm_delete_repo": 'Delete "{0}"?\nThis cannot be undone.',
        "dash.push_result": "Pushed  {}",
        "dash.click_to_cancel": "Click to cancel",
        "dash.sync_cancelled": "Sync cancelled",
        "dash.nothing_push": "Nothing to push",
        "dash.scanning": "Scanning for large files...",
        "dash.pull_result": "Pulled:\n{}",
        "dash.uptodate": "Up to date",
        "dash.sync_failed": "Sync failed: {}",
        "dash.sync_failed_short": "Sync failed",
        "dash.pulling": "Pulling...",
        "dash.pushing": "Pushing...",
        "dash.initializing": "Initializing repository...",
        "dash.files": "Files",
        "dash.open_folder": "Open Folder",
        "dash.add_file": "Add File",
        "dash.adding_files": "Copying files...",
        "dash.adding_folder": "Copying folder...",
        "dash.add_file": "Add File",
        "dash.adding_files": "Copying files...",
        "dash.adding_folder": "Copying folder...",
        "dash.add_folder": "New Folder",
        "dash.new_folder_name": "Folder name:",
        "dash.folder_copied": "Copied folder {}",
        "dash.rename_file": "Rename",
        "dash.select_file": "Select file(s) to add",
        "dash.select_file_first": "Select a file first",
        "dash.new_name": "New name:",
        "dash.confirm_delete": "Delete {}?",
        "dash.confirm_delete_title": "Confirm delete",
        "dash.files_added": "Added {} file(s)",
        "dash.folders_added": "Added {} folder(s)",
        "dash.file_deleted": "Deleted {}",
        "dash.delete_denied": "Could not delete {}.\nThe file may be open in another application.",
        "dash.file_renamed": "Renamed {} to {}",
        "dash.confirm_logout": "This will remove the stored GitHub token.\nLocal files will not be deleted.",
        "dash.confirm_logout_title": "Confirm logout",
        "dash.error": "Error",
        "dash.enter_name": "Enter a repository name",
        "dash.select_folder": "Select a local folder",
        "dash.setup_failed": "Setup failed:\n{}",
        "dash.lfs_title": "Large files detected",
        "dash.cannot_push": "These files exceed GitHub limit (100 MB) and will not be pushed:",

        "help.title": "MonaDrive Help",
        "help.body": (
            "MonaDrive syncs local folders to your private GitHub repositories.\n\n"
            "Setup:\n"
            "  1. Register a GitHub OAuth App at github.com/settings/developers\n"
            "  2. Enter Client ID and Secret in the login screen\n"
            "  3. Sign in with GitHub to authorize\n"
            "  4. Create a repo from the sidebar (+), choose private or public\n"
            "  5. Pick any local folder (even non-empty) and click Initialize\n\n"
            "Usage:\n"
            "  - Edit files directly in File Explorer, then click Push to upload\n"
            "  - Click Pull to overwrite local files with remote version\n"
            "  - Status bar shows local ahead/behind remote commit counts\n"
            "  - Drag files or folders onto the window to add them\n"
            "  - Hover over files or repos to reveal rename/delete buttons\n"
            "  - Initializing does NOT auto-pull from remote\n"
            "  - Git is auto-downloaded on first launch if not installed\n\n"
            "Font: Monocraft by IdreesInc (github.com/IdreesInc/Monocraft)\n"
            "License: MIT"
        ),
        "tooltip.back": "Back",
        "tooltip.root": "Root",
        "tooltip.help": "Help",
        "tooltip.language": "Language",
        "tooltip.refresh": "Refresh",
        "tooltip.theme": "Theme",
        "tray.show": "Show MonaDrive",
        "tray.quit": "Quit",
    },
    "zh": {
        "app.title": "MonaDrive",
        "app.tagline": "GitHub 驱动的私有云盘",

        "login.oauth_hint": (
            "在 github.com/settings/developers 注册 OAuth App\n"
            "回调地址设为 http://127.0.0.1/callback"
        ),
        "login.client_id": "Client ID",
        "login.client_secret": "Client Secret",
        "login.signin": "使用 GitHub 账号登录",
        "login.remember": "记住我",
        "login.waiting": "正在等待授权...",
        "login.browser_opened": "浏览器已打开 -- 请在浏览器中完成授权",
        "login.missing_creds": "请填写 Client ID 和 Client Secret",
        "login.success": "登录成功",
        "login.failed": "登录失败: {}",

        "dash.repo": "仓库设置",
        "dash.repo_name": "仓库名称",
        "dash.repo_placeholder": "例如: my-monadrive-files",
        "dash.folder": "本地文件夹",
        "dash.folder_placeholder": "选择本地同步文件夹...",
        "dash.browse": "浏览",
        "dash.initialize": "初始化",
        "dash.setup_title": "配置你的仓库",
        "dash.pull": "拉取",
        "dash.push": "推送",
        "dash.add_file": "添加文件",
        "dash.adding_files": "正在复制文件...",
        "dash.adding_folder": "正在复制文件夹...",
        "dash.add_folder": "新建文件夹",
        "dash.new_folder_name": "文件夹名称:",
        "dash.folder_copied": "已复制文件夹 {}",
        "dash.working": "同步中...",
        "dash.log": "操作日志",
        "dash.logout": "登出",
        "dash.not_init": "尚未初始化",
        "dash.status_modified": "{} 个已修改",
        "dash.status_new": "{} 个新文件",
        "dash.status_clean": "无本地变更",
        "dash.status_behind": "{} 个远程提交待拉取",
        "dash.status_offline": "远端不可达",
        "dash.signed_in": "已登录: {}",
        "dash.repos": "仓库列表",
        "dash.new_repo_name": "仓库名称:",
        "dash.new_repo_private": "私有",
        "dash.loading_repos": "加载仓库列表...",
        "dash.rename_repo": "重命名仓库",
        "dash.delete_repo": "删除仓库",
        "dash.confirm_delete_repo": '确定删除 "{0}"？\n此操作不可撤销。',
        "dash.init_failed": "初始化失败: {}",
        "dash.reconnected": "已重新连接到本地仓库",
        "dash.avatar_reinit": "点击重新配置仓库",
        "dash.avatar_back": "点击返回主界面",
        "dash.connecting": "正在连接远程仓库...",
        "dash.reinit": "切换 / 重新初始化",
        "dash.reconnect_failed": "重连失败: {}",
        "dash.remote_gone": "远程仓库已被删除，请重新初始化。",
        "dash.cloned": "已克隆到 {}",
        "dash.repo_created": "仓库: {}",
        "dash.push_result": "推送成功  {}",
        "dash.click_to_cancel": "点击取消",
        "dash.sync_cancelled": "同步已取消",
        "dash.nothing_push": "无变更",
        "dash.scanning": "正在扫描大文件...",
        "dash.pull_result": "拉取完成:\n{}",
        "dash.uptodate": "已是最新",
        "dash.sync_failed": "同步失败: {}",
        "dash.sync_failed_short": "同步失败",
        "dash.pulling": "正在拉取...",
        "dash.pushing": "正在推送...",
        "dash.initializing": "正在初始化仓库...",
        "dash.files": "文件管理",
        "dash.open_folder": "打开文件夹",
        "dash.add_file": "添加",
        "dash.delete_file": "删除",
        "dash.rename_file": "重命名",
        "dash.select_file": "选择要添加的文件",
        "dash.select_file_first": "请先选择一个文件",
        "dash.new_name": "新名称:",
        "dash.confirm_delete": "确认删除 {}?",
        "dash.confirm_delete_title": "确认删除",
        "dash.files_added": "已添加 {} 个文件",
        "dash.folders_added": "已添加 {} 个文件夹",
        "dash.file_deleted": "已删除 {}",
        "dash.delete_denied": "无法删除 {}。\n文件可能正在其他应用中使用。",
        "dash.file_renamed": "已将 {} 重命名为 {}",
        "dash.confirm_logout": "登出将清除本地存储的 GitHub 令牌。\n本地文件不会被删除。",
        "dash.confirm_logout_title": "确认登出",
        "dash.error": "错误",
        "dash.enter_name": "请输入仓库名称",
        "dash.select_folder": "请选择本地同步文件夹",
        "dash.setup_failed": "初始化仓库失败:\n{}",
        "dash.lfs_title": "检测到大文件",
        "dash.cannot_push": "以下文件超过 GitHub 限制 (100 MB) 无法推送:",
        "help.body": (
            "MonaDrive 将本地文件夹同步到您的私有 GitHub 仓库。\n\n"
            "设置:\n"
            "  1. 在 github.com/settings/developers 注册 OAuth App\n"
            "  2. 在登录界面输入 Client ID 和 Secret\n"
            "  3. 使用 GitHub 账号登录授权\n"
            "  4. 从侧边栏新建仓库（+），可选私有或公开\n"
            "  5. 选择本地文件夹（已有文件也可以），点击初始化\n\n"
            "使用:\n"
            "  - 直接在文件管理器中修改文件，点击推送即可上传\n"
            "  - 点击拉取从远端覆盖本地文件\n"
            "  - 状态栏实时显示本地领先/落后远端提交数\n"
            "  - 拖放文件或文件夹到窗口即可添加\n"
            "  - 悬停文件或仓库可显示重命名/删除按钮\n"
            "  - 点击加载动画可取消正在进行的同步\n"
            "  - 初始化不会自动拉取远端文件\n"
            "  - 点击头像/用户名切换仓库\n"
            "  - 首次启动若未安装 Git 会自动下载\n\n"
            "字体: Monocraft by IdreesInc (github.com/IdreesInc/Monocraft)\n"
            "许可: MIT"
        ),
        "tooltip.back": "返回",
        "tooltip.root": "根目录",
        "tooltip.help": "帮助",
        "tooltip.refresh": "刷新",
        "tooltip.theme": "主题",
        "tray.show": "显示 MonaDrive",
        "tray.quit": "退出",
    },
}

_current_lang = "zh"


def t(key: str, *args) -> str:
    s = _translations.get(_current_lang, {}).get(key)
    if s is None:
        s = _translations["en"].get(key, key)
    if args:
        return s.format(*args)
    return s


def set_language(lang: str):
    global _current_lang
    if lang in _translations:
        _current_lang = lang


def get_language() -> str:
    return _current_lang
