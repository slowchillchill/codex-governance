# 手动安装与本机配置

本项目提供公共规则、Skill 和配置示例。填写后的本机绑定、原生运行配置和认证材料留在仓库外；日常使用
与公共规则升级不需要修改版本化示例。当前配置接入方式在 Codex CLI `0.154.0` 上核对；使用 Git、GitHub
CLI 和支持独立 Profile 文件及自定义角色的 Codex CLI。

## 1. 准备公共源与账号

克隆本仓库并进入根目录。为治理准备控制账号与实现账号各自的 GitHub CLI 认证目录；已有认证目录可以
继续使用，新的认证由使用者通过 GitHub CLI 正常登录完成。不要把认证目录、令牌或配置备份复制到仓库。
账号与字段的权威定义见[治理规范第四节](../governance/codex-development-governance.md#四角色与身份)。

目标仓库需要赋予实现账号普通推送和创建 PR 的权限，控制账号需要管理 Issue、正式审查和合并的权限。
新建仓库不会自动继承另一个仓库的协作者或设置；邀请需要接受后才能作为已生效权限使用。
按当前治理清理合同，合并采用保留实现提交的合并提交方式，关闭合并后自动删除分支；其他仓库设置以
目标项目已批准要求为准。Git 远端认证也应使用相应账号；仅设置 `GH_CONFIG_DIR` 不会改变 SSH 密钥，
使用 HTTPS 时可由 GitHub CLI 的 Git 凭据助手提供对应目录中的认证。

## 2. 填写仓库外的私有绑定

下面的命令在公共源仓库根目录执行。已有目标文件时，`cp -i` 会询问是否覆盖；升级时应按第六节合并。

```bash
governance_source_dir="$(pwd -P)"
codex_config_dir="${CODEX_HOME:-$HOME/.codex}"
governance_binding_file="${CODEX_GOVERNANCE_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/codex-governance/local.toml}"
mkdir -p "$(dirname "$governance_binding_file")"
cp -i templates/local.example.toml "$governance_binding_file"
```

用编辑器打开该文件，填写 `paths.source_root` 和两个账号的 `login`、`config_dir`。把第一条命令取得的
实际目录填入 `source_root`；路径值是普通 TOML 字符串，使用实际绝对路径，不依赖变量替换或命令求值。
带空格的路径可以正常填写；在 shell 命令中使用时仍需正确引用。不要在此文件填写模型、权限或凭据。

自定义位置时，在启动 Codex 的环境中设置 `CODEX_GOVERNANCE_CONFIG` 为该文件的实际绝对路径。
这是本项目约定的定位变量，不是 Codex 原生配置加载选项。默认位置与字段语义统一见治理规范第四节。

## 3. 安装原生 Profile 与角色

在同一终端继续执行，将示例复制为仓库外的运行文件：

```bash
mkdir -p "$codex_config_dir/codex-governance/agents"
cp -i codex/runtime/codex-governance.config.example.toml "$codex_config_dir/codex-governance.config.toml"
cp -i codex/agents/scope-planner.example.toml "$codex_config_dir/codex-governance/agents/scope-planner.toml"
cp -i codex/agents/implementer.example.toml "$codex_config_dir/codex-governance/agents/implementer.toml"
cp -i codex/agents/reviewer.example.toml "$codex_config_dir/codex-governance/agents/reviewer.toml"
```

模型与推理等级默认继承已有 Codex 配置。需要覆盖时，编辑安装后的 Profile 或对应角色 TOML，在顶层
填写原生 `model`、`model_reasoning_effort` 字段。权限示例沿用本治理的 `danger-full-access` 和 `never`；
它们不扩大任务授权或角色职责。账号与目录仍只维护在私有绑定中，不另加角色的 `GH_CONFIG_DIR` 默认副本。

Profile 使用顶层配置项，不放入基础配置的 `[profiles.codex-governance]` 表。示例的 `config_file`
相对声明它的 Profile 文件解析，因此上述目录结构应保持对应。基础 `config.toml` 不需要注册治理角色。
[Codex Profile 文档](https://learn.chatgpt.com/docs/config-file/config-advanced)、
[角色配置路径说明](https://learn.chatgpt.com/docs/config-file/config-reference)

## 4. 接入 Skill 与工程规则

保持整个公共源仓库可用。先检查用户级 `~/.agents/skills/codex-stage-orchestrator` 入口：已有入口且指向
当前源目录时跳过下面的链接命令；迁移时只调整这个治理入口。仅在入口不存在时执行以下命令：

```bash
mkdir -p "$HOME/.agents/skills"
ln -s "$governance_source_dir/skills/codex-stage-orchestrator" "$HOME/.agents/skills/codex-stage-orchestrator"
```

不要只复制 `SKILL.md`，
它还使用公共规范与编排程序。`agents/openai.yaml` 保持禁止隐式调用。

将[接入片段](../templates/repository-AGENTS.fragment.md)的语义合并进目标仓库根 `AGENTS.md`，保留目标
项目自己的规则。片段通过本机绑定定位公共源，不填写真实账号或本机路径。

若希望在未接入治理的普通开发中也使用工程准则，在用户级 `AGENTS.md` 中合入以下读取说明，保留已有
个人偏好和环境边界，不把个人全局文件复制到公共仓库：

```text
通用工程规则适用于普通开发，不依赖治理 Profile 或目标仓库接入。
先通过工具读取非空 CODEX_GOVERNANCE_CONFIG 指定的本机绑定文件；未指定时读取
${XDG_CONFIG_HOME:-$HOME/.config}/codex-governance/local.toml。
只使用 paths.source_root 定位并读取 governance/engineering-principles.md。
此配置定位和规则读取不启用 GitHub 治理，不触发身份核验、Issue 查询或治理角色派生。
```

## 5. 启动与核对

```bash
codex --profile codex-governance -C /绝对路径/目标仓库
```

启动 Profile 本身不启用治理。安装后用新会话核对公共规则、Skill 和角色配置来源；显式调用方式见
[README](../README.md#start)。身份核验只读取登录名，不读取认证文件。继承的 `GH_CONFIG_DIR` 即使不同，
治理命令仍必须使用本角色绑定的目录。

新会话中的本机路径和配置核对结果留在私有交接中。公开 Issue、PR、Review 和附件使用仓库相对路径及
去除个人配置内容后的证据，遵守治理规范第三节。公开 GitHub 操作仍会显示实际账号身份。

## 6. 多个入口、更新与迁移

- 多个 `CODEX_HOME` 可以各自安装原生文件，共用同一份私有绑定和公共源。
- 如果通过符号链接共用一个 Profile，在该私有 Profile 的 `config_file` 中填写共用角色副本的实际绝对
  路径，避免不同入口的相对路径基准不同。真实路径只存在于仓库外的私有 Profile。
- 更新公共源后，比较公共示例和已安装副本，手动合并角色指令与原生设置的变化，保留自己的模型、
  推理等级和权限覆盖。本机绑定不随公共源更新被覆盖，不将安装后的文件反向提交。
- 从旧的个人配置版本迁移时，先在仓库外保留必要的非认证配置备份，再填写集中绑定、安装角色副本和
  更新公共规则引用。不要备份或复制认证文件，也不改动其他治理工具的目录、服务或认证材料。
- 移动公共源时，同步更新私有 `source_root` 和 Skill 链接；新会话用于确认切换生效，已运行会话可能
  仍保留旧指令。三个角色仍只接收主会话已经确定的任务，不因配置更新自行寻找任务。
