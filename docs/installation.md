# 手动安装与本机配置

本项目提供公共规则、Skill 和配置示例。填写后的本机绑定、原生运行配置和认证材料留在仓库外；日常使用
与公共规则升级不需要修改版本化示例。当前配置接入方式在 Codex CLI `0.159.2` 上核对；使用 Git、GitHub
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

需要备份盘归档时，按模板的可选 `[[evidence_archives]]` 为每个仓库分别填写 Git 公共目录、归档根目录
和预期挂载点，字段语义见治理规范第四节。不要把某个项目的归档目录当成全局默认值；实际路径只保存在
私有绑定中。归档按工程准则第六节和编排程序第五节执行，配置目录不代表备份盘已经挂载，也不授权
清理已有备份。需要使用备份盘而发现其不可用时，按工程准则第六节立即停止当前任务并向用户汇报，
等待裁决。只需保留小型公开证据的任务不强制配置备份盘。

自定义位置时，在启动 Codex 的环境中设置 `CODEX_GOVERNANCE_CONFIG` 为该文件的实际绝对路径。
这是本项目约定的定位变量，不是 Codex 原生配置加载选项。默认位置与字段语义统一见治理规范第四节。

## 3. 安装并注册原生角色

在同一终端继续执行，将示例复制为仓库外的运行文件：

```bash
mkdir -p "$codex_config_dir/codex-governance/agents"
cp -i codex/agents/scope-planner.example.toml "$codex_config_dir/codex-governance/agents/scope-planner.toml"
cp -i codex/agents/implementer.example.toml "$codex_config_dir/codex-governance/agents/implementer.toml"
cp -i codex/agents/reviewer.example.toml "$codex_config_dir/codex-governance/agents/reviewer.toml"
```

将下列三个角色表合并进该入口实际使用的 `$codex_config_dir/config.toml`，保留其他配置；已有同名表时
更新对应字段，不重复追加。相对 `config_file` 按声明它的配置文件目录解析，多入口共用角色时见第六节。

```toml
[agents."scope-planner"]
description = "仅供用户显式启用 codex-stage-orchestrator 后的父级交接：只读澄清准确 Issue 的范围、验收与决策缺口。"
config_file = "codex-governance/agents/scope-planner.toml"

[agents.implementer]
description = "仅供用户显式启用 codex-stage-orchestrator 后的父级交接：实施准确 Issue 的已批准任务，提交、推送并维护 PR。"
config_file = "codex-governance/agents/implementer.toml"

[agents.reviewer]
description = "仅供用户显式启用 codex-stage-orchestrator 后的父级交接：只读审查待提交候选、准确 PR 或交付组合；仅对 PR 提交正式 Review。"
config_file = "codex-governance/agents/reviewer.toml"
```

当前 CLI 默认启用子代理；若已有配置显式设置 `agents.enabled = false`，使用治理时需在原表中改为
`true`。角色注册只使角色可用，不启用 GitHub 治理；三个角色只接收显式启用后由 orchestrator 交付的任务。

普通启动保留该入口已有的主会话模型、推理等级和命令权限。需要覆盖时，编辑原生 `config.toml`、可选
Profile 或对应角色 TOML 的顶层 `model`、`model_reasoning_effort` 等字段。角色权限示例沿用
`danger-full-access` 和 `never`，父会话实时权限覆盖仍会应用到子代理；这些设置不扩大任务授权或角色职责。
账号与目录仍只维护在私有绑定中，不另加角色的 `GH_CONFIG_DIR` 默认副本。

兼顾治理判断质量与执行成本时，可以在安装后的三个角色 TOML 中采用以下可选组合。表中列名对应
原生配置字段；公共模板仍默认继承安装者已有配置。

| 角色 | `model` | `model_reasoning_effort` |
|---|---|---|
| 范围规划者 `scope-planner` | `gpt-6-astra` | `high` |
| 实现者 `implementer` | `gpt-6.1-sol` | `medium` |
| 审查者 `reviewer` | `gpt-6-astra` | `xhigh` |

这是按角色职责作出的选型建议，实际效果仍需结合项目任务评估。型号能力与可用推理等级参见
[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) 和
[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) 的官方说明。

需要单独的治理启动预设时，可额外安装 Profile：

```bash
cp -i codex/runtime/codex-governance.config.example.toml "$codex_config_dir/codex-governance.config.toml"
```

该 Profile 使用顶层配置项，不放入基础配置的 `[profiles.codex-governance]` 表；示例提供
`danger-full-access`、`never` 和子代理并发上限等预设。用 `--profile codex-governance` 选择它属于可选
启动方式；普通启动的角色注册不依赖该文件。Profile 中的同名角色应指向同一组已安装文件。
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
采用 Project 时可增加 `项目看板：<Project URL>`，只填实际采用的看板；未配置时继续 Issue 闭环。
Project 不增加本机绑定字段，起点与视图建议见第七节。
已有决策记录时，可填写 `项目决策记录：<本项目已有决策 Issue 或索引的完整链接>`，或沿用当前合同和
项目文档中的引用；各目标项目分别提供自己的入口。定位、交接和适用性判断见治理规范第六节“范围规划”。

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
codex -C /绝对路径/目标仓库
```

普通启动后显式调用 `$codex-stage-orchestrator` 并给出明确需求即可，不必传入 `--profile`。
安装后用新会话核对公共规则、Skill 和角色配置来源；完整调用方式见
[README](../README.md#start)。身份核验只读取登录名，不读取认证文件。继承的 `GH_CONFIG_DIR` 即使不同，
治理命令仍必须使用本角色绑定的目录。

只核对新会话输入而不运行开发闭环时，可以在目标仓库执行：

```bash
codex debug prompt-input '仅核对规则来源和角色配置，不启用治理，不执行任务。'
```

核对输出中的目标仓库规则；同时检查该入口实际加载的基础配置、角色注册、各 `config_file` 指向的
实际文件及共享 Skill 入口。使用可选 Profile 时还须核对它的覆盖。输入中出现角色名称不能证明原生角色
已加载；输入渲染也不能证明角色已运行、真实 GitHub 闭环已经执行或旧会话已重新加载规则。
不要公开包含本机路径的完整输出。

新会话中的本机路径和配置核对结果留在私有交接中。公开 Issue、PR、Review 和附件使用仓库相对路径及
去除个人配置内容后的证据，遵守治理规范第三节。公开 GitHub 操作仍会显示实际账号身份。

## 6. 多个入口、更新与迁移

- `codex`、`codex-b`、`codex-c` 等入口按各自的 `CODEX_HOME` 加载基础 `config.toml`；未设置时使用
  `~/.codex`。先确认启动脚本或继承环境实际选择的目录，分别在三份基础配置中注册上述三个角色。
- 同一用户的多个入口共用 `~/.agents/skills/codex-stage-orchestrator`、私有绑定与公共源。角色副本也可
  只安装一组，各基础配置的 `config_file` 填写这组文件的实际绝对路径；TOML 中不写未展开的变量。
  保留各入口自己的主会话设置、认证和会话数据，不链接或复制整份基础配置与认证目录。
- 已共用可选 Profile 的入口可保留该链接；Profile 的角色路径也指向上述共用文件。真实绝对路径
  只保存在仓库外的私有配置中。角色注册与共享 Skill 均在新会话核对，旧会话不保证热加载。
- 更新公共源后，比较公共示例和已安装副本，手动合并角色指令与原生设置的变化，保留自己的模型、
  推理等级和权限覆盖。本机绑定不随公共源更新被覆盖，不将安装后的文件反向提交。
- reviewer 升级还须把必要指令合并到实际生效配置的 `agents.reviewer.config_file` 指向的已安装文件；
  仅更新公共示例不会更新该副本。共用符号链接时修改实际目标并保留链接，新会话确认读取更新后的入口。
- 从旧的个人配置版本迁移时，先在仓库外保留必要的非认证配置备份，再填写集中绑定、安装角色副本和
  更新公共规则引用。不要备份或复制认证文件，也不改动其他治理工具的目录、服务或认证材料。
- 移动公共源时，同步更新私有 `source_root` 和 Skill 链接；新会话用于确认切换生效，已运行会话可能
  仍保留旧指令。三个角色仍只接收主会话已经确定的任务，不因配置更新自行寻找任务。
- 升级至 `0.7.0` 时保留既有项目、模块、阶段 Issue 的当前合同、编号及证据，不自动关闭或迁移。
  旧阶段中的已批准任务可继续执行；其他仓库硬编码的旧规则在后续接入时定向处理。
- 回退只撤销本次公共规则差异和本次私有指令修改，保留其他配置与并行改动；不要用整份旧副本覆盖
  期间出现的新设置。符号链接共用文件时修改实际文件，保留已有链接及模型、推理等级、权限和角色绑定。

## 7. Project 接入建议

以下是选择采用 Project 时的配置建议，不是普通任务的前置条件，也不授权代理在线创建或修改看板结构。
Project 管理项目目标与范围概述、规划入口和视图；任务合同、授权及完成事实遵守
[工程准则第八节](../governance/engineering-principles.md#8-github-任务治理)，维护程序遵守
[治理规范第五节](../governance/codex-development-governance.md#五启动与恢复)。

- 以 Kanban 为起点，`Status` 建议为待办、进行中、审查中、暂停、已结束。
- 复用原生负责人、标签与父子关系，模块使用标签分类；优先级、日期和迭代字段按真实管理需要增加，
  Milestone 不作为默认要求。
- 既有 Project 使用已有明确对应的选项，不强制改名或重建字段；缺少合适选项时报告配置缺口。

| 视图 | 主要展示内容 |
|---|---|
| 执行看板 | 可执行任务及其当前状态，避免把父交付与子任务重复统计 |
| 项目总览 | 父交付、整体目标、依赖和验收结果；正式总体合同直接引用 |
| 模块工作 | 按模块标签筛选或分组的任务，可跨多个交付演进 |

主会话只关联、维护已明确指定的 Project，按实际对象读取条目和字段标识；父子关系表示组成，状态展示
进度，二者都不签发任务。只有 Issue 已关闭才把展示更新为“已结束”；取消和重复关闭不表示交付成功。
合同完整时，展示同步失败留在现有进度与交付报告中，不阻塞实施。创建 Project、修改字段结构或批量
导入须另行明确提出；本仓库的安装与规则升级本身不执行这些线上接入动作。

<a id="ocr-review"></a>

## 8. OCR 辅助审查

Open Code Review 的 `delegate` 命令提供文件筛选信息与规则解析，实际推理由当前 Codex reviewer
完成，沿用其模型及额度来源；读取规则和分析代码仍消耗 Codex 额度。无需给 OCR 配置模型端点或 API Key。
使用条件、决策核对、审查范围和复审规则统一见
[治理规范第六节“独立审查与正式 Review”](../governance/codex-development-governance.md#3-独立审查与正式-review)。

安装使用官方 CLI，本节以 `1.12.11` 核对，要求 Node.js 至少 14、Git 至少 2.41。首次安装或明确升级时执行：

```bash
npm install -g @alibaba-group/open-code-review@1.12.11
ocr --version
ocr delegate rule --help
ocr delegate preview --help
```

JSON 输出需要 OCR 至少 `1.9.0`；使用其他版本时核对这两个子命令及参数是否可用。官方 Codex 插件可以
提供可调用 Skill，但不是直接调用 CLI 的必要依赖；安装插件不代表选择了委托模式。本治理直接使用
`ocr delegate`，不调用完整 `ocr review` 或自动修复流程。安装与版本依据见
[官方插件说明](https://github.com/alibaba/open-code-review/blob/v1.12.11/plugins/open-code-review/README.md)和
[委托模式说明](https://github.com/alibaba/open-code-review/blob/v1.12.11/plugins/open-code-review/skills/open-code-review-delegate/SKILL.md)。

提交前候选没有 PR 头，不能套用下列提交范围命令。只有已核实的调用方式能够准确覆盖当前候选时才用
OCR 辅助；否则说明适用方式的缺口，按完整待提交差异及真实源码完成内容审查。不为工具提前创建提交
或 PR，也不把旧 `HEAD` 范围冒充候选。提交后使用实际 PR 范围取得适用规则，发现新问题时补审受影响
内容，复用仍适用的证据。

以下 Bash 示例用于已有 PR，其中 `review_repo` 是已交付的准确审查工作目录，`review_base_sha` 与 `review_head_sha`
来自实际 PR 的比较基准及本次审查头，不以固定分支名代替。`review_paths` 是本轮相关文件路径的数组，
由完整差异和实际影响确定。批量获取规则：

```bash
ocr delegate rule \
  --repo "$review_repo" \
  --from "$review_base_sha" --to "$review_head_sha" \
  --format json -- "${review_paths[@]}"
```

需要理解 OCR 的文件筛选结果时，使用以下命令查看 `reviewable_files`、`excluded_files` 及排除原因。
Range 模式返回的 `merge_base` 对应分支比较起点；审查 Git 差异时使用同一比较语义。

```bash
ocr delegate preview \
  --repo "$review_repo" \
  --from "$review_base_sha" --to "$review_head_sha" \
  --format json
```

OCR 默认筛选可能排除测试、夹具、生成内容和锁文件，删除文件也不会进入其主审列表；Markdown 等文件
可能没有适用的内置规则。上述结果只描述 OCR 的支持范围，不替代治理要求的完整差异审查。

读取返回规则的 `source`、`pattern` 和正文。OCR 按显式 `--rule`、项目、全局、内置的顺序取首个匹配，
自定义规则默认替换内置规则；`merge_system_rule` 仅合并内置规则，不裁定规则之间的效力。
项目规则及其引用正文从磁盘读取，`--to` 不会自动将它们固定到指定提交；使用对应审查版本的现有现场，
避免混入其他分支的规则。治理正文继续在其权威位置维护，无需复制成 `rule.json` 或另建规则状态文件。

<a id="codebase-memory"></a>

## 9. codebase-memory-mcp 接入与维护

代码检索的使用原则见[工程准则](../governance/engineering-principles.md)，角色职责和只读边界见
[治理规范](../governance/codex-development-governance.md)。本节只说明客户端配置与验证机制；接入 MCP
不启用 GitHub 治理。索引是由源码生成、可重建的缓存，不导入 Issue、Project 的合同或批准状态，也不使用
`manage_adr` 镜像项目决策。

本节依据已安装 `0.10.8` 核对，本次配置修复复用该版本；这不是对后续使用者的永久版本限制。后续升级
须单独核对索引格式、工具行为和配置副作用。安装或维护只修改明确指定的客户端，不使用会自动配置其他
客户端的通用一键安装流程。保留已有认证、模型、角色和 Profile，不复制整份基础配置。

在每个实际使用的 `CODEX_HOME/config.toml` 中合并以下配置；已有同名表时更新原表。下列路径均为
占位，替换为仓库外的实际绝对路径，不在 TOML 中保留未展开的环境变量：

```toml
[mcp_servers.codebase-memory-mcp]
command = "/绝对路径/工具目录/codebase-memory-mcp"

[mcp_servers.codebase-memory-mcp.env]
CBM_CACHE_DIR = "/绝对路径/仓库外缓存/codebase-memory-mcp"
```

`codex`、`codex-b`、`codex-c` 分别注册同一二进制构建和同一规范化缓存目录；共享 `AGENTS.md` 不会共享
MCP 配置。缓存内部按真实工作树区分项目，不把不同路径强行配置成同一个项目。该版本已有同账号共享
守护进程和项目级并发协调，无需另建锁；所有活动进程必须使用相同版本、构建、协调 ABI 和规范化缓存。
更换构建或缓存前先结束相关活动会话，再统一更新并重启，遵守
[该版本的会话协调说明](https://github.com/DeusData/codebase-memory-mcp/blob/v0.10.8/README.md#session-coordination-daemon)。

首次使用通过 `list_projects` 选择真实任务工作树，用 `index_status` 核对根目录和当前状态，并按
工程准则用 `check_index_coverage` 及当前源码核对相关路径或范围的新鲜度与解析缺口；`ready` 和
`git.head_sha` 不能证明索引对应的源码版本。确有索引准备需求时，由主会话或实现者对匹配根目录调用
`index_repository`，使用 `persistence=false`；不在每次任务或恢复时全量重建。主动新鲜度确认的时点与
刷新责任统一按治理规范第四节执行，规划者和审查者沿用其中规定的查询及回退流程。

仓库外缓存边界必须在接入生效前验证：`0.10.8` 在仓库已有 `.codebase-memory/graph.db.zst` 时，即使
`persistence=false`，后续索引仍可能刷新它；导出还可能写入 `.codebase-memory` 元数据及 Git 配置。
MCP 初始化和后台 watcher 也可能触发索引写入，不能只检查显式工具调用。先核对已有仓库内产物及自动
索引配置，不为接入擅自删除产物；无法保证被审对象不变时，规划和审查使用源码查询。依据见
[索引发布实现](https://github.com/DeusData/codebase-memory-mcp/blob/v0.10.8/src/pipeline/pipeline.c#L2492)和
[产物导出实现](https://github.com/DeusData/codebase-memory-mcp/blob/v0.10.8/src/pipeline/artifact.c#L366)。

接入验证针对以下实际失败条件，结果保留在私有交接或脱敏的现有交付证据中：

- 三个入口分别执行 MCP 列表核对并实际调用工具；仅配置可解析或 `codex mcp list` 有条目不证明可用。
- 用主工作树和一个任务工作树验证项目不会混用；源码修改后能够识别相关范围过期并确认刷新，无法
  确认时正确回退到当前源码。
- 覆盖 MCP 初始化、查询和后台刷新，确认被审工作树及 Git 配置未被写入；检查既有产物与忽略文件，
  不能只凭 `git status` 干净得出结论。工具自身的仓库外派生缓存遵守治理正文的允许范围。
- 用新会话核对三个入口、已安装角色及适用 Profile 的实际规则来源，沿用第五节的方法；工具不可用时
  能继续源码查询，不为证明配置生效而执行 GitHub 合并或另设审批流程。
