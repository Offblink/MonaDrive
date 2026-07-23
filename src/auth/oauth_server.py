"""GitHub OAuth 本地回调服务器。

流程:
1. 验证 CLIENT_ID 已配置
2. 启动本地 HTTP 服务器 (随机端口)
3. 打开浏览器到 GitHub 授权页
4. 等待回调 -> 收到 authorization code
5. 用 code 换取 access token (带 PKCE + redirect_uri)
6. 存储 token 并返回成功页面
"""

import hashlib
import http.server
import logging
import secrets
import threading
import urllib.parse
import webbrowser
from http import HTTPStatus

import requests

from . import REDIRECT_HOST, REDIRECT_PORT, TOKEN_URL, get_github_config
from .token_store import store_token

logger = logging.getLogger(__name__)

_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>MonaDrive - 授权成功</title>
<style>
  body { font-family: -apple-system, Segoe UI, sans-serif; display: flex;
         justify-content: center; align-items: center; min-height: 100vh;
         margin: 0; background: #0d1117; color: #c9d1d9; }
  .box { text-align: center; padding: 48px; border: 1px solid #30363d;
         border-radius: 12px; background: #161b22; }
  h1 { color: #58a6ff; }
  p { color: #8b949e; }
</style></head>
<body><div class="box">
  <h1>授权成功</h1>
  <p>您可以关闭此页面，返回 MonaDrive 应用。</p>
</div></body></html>"""

_ERROR_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>MonaDrive - 授权失败</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, sans-serif; display: flex;
         justify-content: center; align-items: center; min-height: 100vh;
         margin: 0; background: #0d1117; color: #c9d1d9; }}
  .box {{ text-align: center; padding: 48px; border: 1px solid #30363d;
         border-radius: 12px; background: #161b22; }}
  h1 {{ color: #f85149; }}
</style></head>
<body><div class="box">
  <h1>授权失败</h1>
  <p>{error}</p>
</div></body></html>"""


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """处理 GitHub OAuth 回调请求。"""

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/callback":
            code = params.get("code", [None])[0]
            error = params.get("error", [None])[0]
            state = params.get("state", [None])[0]

            # CSRF check
            expected_state = getattr(self.server, "state", None)
            if expected_state and state != expected_state:
                self._respond_error("CSRF 验证失败，请重试")
                self.server.result = ("error", "CSRF 验证失败")
                self.server.done.set()
                return

            if error:
                desc = params.get("error_description", [error])[0]
                self._respond_error(desc)
                self.server.result = ("error", desc)
                self.server.done.set()
                return

            if code:
                token = self._exchange_code(code)
                if token:
                    store_token(token)
                    self._respond_success()
                    self.server.result = ("success", token)
                else:
                    self._respond_error("令牌交换失败，请检查 CLIENT_ID/SECRET 配置")
                    self.server.result = ("error", "令牌交换失败")
                self.server.done.set()
                return

            self._respond_error("无效的回调参数")
            self.server.result = ("error", "无效的回调参数")
            self.server.done.set()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _exchange_code(self, code: str) -> str | None:
        """用 authorization code 换取 access token。"""
        try:
            cfg = get_github_config()
            data = {
                "client_id": cfg.get("client_id", ""),
                "client_secret": cfg.get("client_secret", ""),
                "code": code,
                "redirect_uri": getattr(self.server, "redirect_uri", ""),
            }
            code_verifier = getattr(self.server, "code_verifier", None)
            if code_verifier:
                data["code_verifier"] = code_verifier

            resp = requests.post(
                TOKEN_URL,
                headers={"Accept": "application/json"},
                data=data,
                timeout=15,
            )
            result = resp.json()
            if "error" in result:
                logger.error("Token exchange error: %s", result)
                return None
            return result.get("access_token")
        except Exception:
            logger.exception("Token exchange failed")
            return None

    def _respond_success(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(_SUCCESS_HTML.encode("utf-8"))

    def _respond_error(self, msg: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(_ERROR_HTML.format(error=msg).encode("utf-8"))

    def log_message(self, format, *args):
        pass  # 静默日志


class OAuthServer:
    """OAuth 回调服务器 — 一次性使用，收到回调后自动停止。"""

    def __init__(self):
        self._thread: threading.Thread | None = None
        self._server: http.server.HTTPServer | None = None
        self.port: int = 0

    def _validate_config(self):
        """验证 OAuth 配置是否就绪。"""
        cfg = get_github_config()
        if not cfg.get("client_id") or not cfg.get("client_secret"):
            raise RuntimeError(
                "GitHub OAuth 尚未配置。\n\n"
                "请在应用登录界面输入 Client ID 和 Client Secret。\n"
                "详见 README.md 中的注册步骤。"
            )

    def start(self) -> str:
        """启动服务器，打开浏览器，阻塞等待授权完成。

        Returns:
            token 字符串，或失败时 raise RuntimeError。
        """
        self._validate_config()

        # PKCE: 生成 code_verifier 和 code_challenge
        code_verifier = secrets.token_urlsafe(64)[:128]  # 43-128 chars
        code_challenge = hashlib.sha256(
            code_verifier.encode("ascii")
        ).digest()
        code_challenge_b64 = (
            urllib.parse.quote(
                __import__("base64").urlsafe_b64encode(code_challenge).rstrip(b"="),
                safe="",
            )
        )

        # CSRF state
        state = secrets.token_urlsafe(32)

        self._server = http.server.HTTPServer(
            (REDIRECT_HOST, REDIRECT_PORT), _CallbackHandler
        )
        self.port = self._server.socket.getsockname()[1]

        redirect_uri = f"http://{REDIRECT_HOST}:{self.port}/callback"
        self._server.redirect_uri = redirect_uri
        self._server.state = state
        self._server.code_verifier = code_verifier
        self._server.done = threading.Event()
        self._server.result = None

        # 启动服务线程
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

        client_id = get_github_config().get("client_id", "")
        params = urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "repo delete_repo",
            "state": state,
            "code_challenge": code_challenge_b64,
            "code_challenge_method": "S256",
        })
        auth_url = f"https://github.com/login/oauth/authorize?{params}"
        logger.info("Opening auth URL: %s", auth_url)

        if not webbrowser.open(auth_url):
            self.stop()
            raise RuntimeError(
                "无法打开浏览器。\n\n"
                "请手动访问以下链接完成授权:\n"
                f"{auth_url}"
            )

        # 等待回调 (最多 5 分钟)
        if not self._server.done.wait(timeout=300):
            self.stop()
            raise RuntimeError("授权超时，请重试")

        status, value = self._server.result
        if status == "error":
            raise RuntimeError(value)
        return value

    def stop(self) -> None:
        """停止服务器。"""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
