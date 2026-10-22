#!/usr/bin/env python3
"""按组绑定执行 GitHub CLI 与 HTTPS 远端 Git；不保存任务或认证状态。"""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tomllib
from urllib.parse import urlparse


BINDINGS = {
    "decision": ("CODEX_DECISION_ASSISTANT_CONFIG", "codex-decision-assistant"),
    "research": ("CODEX_STRATEGY_RESEARCH_CONFIG", "codex-strategy-research"),
    "development": ("CODEX_GOVERNANCE_CONFIG", "codex-governance"),
}


class IdentityError(RuntimeError):
    pass


def binding_path(group, environ=None):
    env = os.environ if environ is None else environ
    variable, directory = BINDINGS[group]
    override = env.get(variable, "").strip()
    base = Path(env.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return Path(override) if override else base / directory / "local.toml"


class GroupGitHub:
    def __init__(self, group, environ=None):
        self.group = group
        env = dict(os.environ if environ is None else environ)
        try:
            with binding_path(group, env).open("rb") as stream:
                binding = tomllib.load(stream)["github"][group]
            self.login = binding["login"]
            directory = Path(binding["config_dir"])
        except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
            raise IdentityError(f"{group} 的私有身份绑定缺失或不可读") from exc
        if not isinstance(self.login, str) or not self.login.strip():
            raise IdentityError(f"{group} 缺少预期登录名")
        if not directory.is_absolute() or not directory.is_dir():
            raise IdentityError(f"{group} 的 config_dir 必须是可用的绝对目录")
        for key in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"):
            env.pop(key, None)
        env["GH_CONFIG_DIR"] = str(directory)
        env["GH_HOST"] = "github.com"
        env["GH_PROMPT_DISABLED"] = "1"
        self.env = env

    def verify(self):
        result = subprocess.run(
            ["gh", "api", "user", "--hostname", "github.com", "--jq", ".login"],
            env=self.env, capture_output=True, text=True, check=False,
        )
        if result.returncode or result.stdout.strip() != self.login:
            raise IdentityError(f"{self.group} 登录名核验失败，已停止相关操作")

    def gh(self, args, **kwargs):
        if not args or args[0] in {"auth", "config", "alias", "extension"}:
            raise IdentityError("此入口不管理认证、配置、别名或扩展")
        if self.group == "development" and args[:2] == ["pr", "create"]:
            raise IdentityError("开发组须将 PR 材料交实际签发组创建")
        self.verify()
        return subprocess.run(["gh", *args], env=self.env, check=False, **kwargs)

    def git(self, worktree, remote, operation, args, git_options=(), **kwargs):
        """选项、远端与引用分别传递，保持 Git 原生参数顺序。"""
        if self.group != "development":
            raise IdentityError("业务远端 Git 交付归开发组；签发组只创建 PR")
        if operation not in {"fetch", "push", "ls-remote"}:
            raise IdentityError("此入口仅执行 fetch、push、ls-remote")
        self.verify()
        env = self.env.copy()
        # 环境注入的 Git 配置不得覆盖本次绑定凭据助手。
        for key in list(env):
            if key.startswith("GIT_CONFIG_"):
                env.pop(key)
        env.pop("GIT_ASKPASS", None)
        env.pop("SSH_ASKPASS", None)
        env["GIT_TERMINAL_PROMPT"] = "0"
        base = ["git", "-C", str(worktree)]
        query = [*base, "remote", "get-url"]
        if operation == "push":
            query.append("--push")
        result = subprocess.run([*query, "--all", remote], env=env, capture_output=True, text=True)
        urls = result.stdout.splitlines()
        if result.returncode or not urls:
            raise IdentityError("无法解析准确远端")
        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname != "github.com" or parsed.username or parsed.password:
                raise IdentityError("远端不是可核验身份的 GitHub HTTPS 地址，请报告传输缺口")
        # 只读配置名，不读取可能包含凭据的请求头正文；禁止旧认证头绕过绑定助手。
        headers = subprocess.run(
            [*base, "config", "--name-only", "--get-regexp", r"^http\..*extraheader$"],
            env=env, capture_output=True, text=True,
        )
        if headers.returncode not in {0, 1}:
            raise IdentityError("无法核对 Git 认证请求头配置名")
        overrides = [arg for key in dict.fromkeys(headers.stdout.splitlines()) for arg in ("-c", f"{key}=")]
        command = [
            *base, "-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
            "-c", "core.askPass=", *overrides,
            operation, *git_options, remote, *args,
        ]
        return subprocess.run(command, env=env, check=False, **kwargs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", required=True, choices=BINDINGS)
    subs = parser.add_subparsers(dest="tool", required=True)
    subs.add_parser("check")
    gh = subs.add_parser("gh")
    gh.add_argument("args", nargs=argparse.REMAINDER)
    git = subs.add_parser("git")
    git.add_argument("--worktree", required=True)
    git.add_argument("--remote", required=True)
    git.add_argument("--option", action="append", default=[], help="放在远端前的 Git 选项，可重复；用 --option=--flag")
    git.add_argument("operation", choices=("fetch", "push", "ls-remote"))
    git.add_argument("args", nargs=argparse.REMAINDER)
    options = parser.parse_args(argv)
    args = getattr(options, "args", [])
    if args[:1] == ["--"]:
        args = args[1:]
    try:
        identity = GroupGitHub(options.group)
        if options.tool == "check":
            identity.verify()
            print(f"{options.group} 身份核验通过")
            return 0
        result = identity.gh(args) if options.tool == "gh" else identity.git(
            options.worktree, options.remote, options.operation, args, git_options=options.option,
        )
        return result.returncode
    except (IdentityError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
