---
name: codex-stage-orchestrator
description: 仅在用户显式调用 codex-stage-orchestrator 并在已接入仓库提出明确开发需求时，编排当前 Issue 的规划、实现、正式 Review、合并与收尾。仅提及、询问或修改 Skill 及启动 Profile 不启用闭环；不自动选择下一任务。
---

# Codex 单任务或单阶段编排

## 启动边界

先确认目标仓库根 `AGENTS.md` 已接入，且用户在当前消息中显式调用本 Skill 并给出明确开发需求。
显式调用是 `$codex-stage-orchestrator` 或明确要求“使用 codex-stage-orchestrator”。
未显式调用或用户明确禁止时，按普通任务授权处理，不执行治理身份核验、Issue 查询或角色派生。
同一已授权任务的澄清与继续执行沿用原授权；新任务或下一阶段需重新显式调用。
`agents/openai.yaml` 保持 `policy.allow_implicit_invocation: false`。

确认启用后，先通过工具只读定位本机绑定：非空的 `CODEX_GOVERNANCE_CONFIG` 指定文件，否则读取
`${XDG_CONFIG_HOME:-$HOME/.config}/codex-governance/local.toml`。这是供代理读取的普通 TOML，不是
Codex 原生配置层。通过 `paths.source_root` 定位治理源，读取 `github.controller` 的 `config_dir` 与 `login`。
取得绑定后立即以该目录内联执行 `gh api user --jq .login` 并核对预期登录名；路径按 shell 规则引用。
绑定目录覆盖继承值，绑定缺失、目录不可用或身份不符时停止相关治理工作。后续认证命令内联同一目录，
不切换全局账号，不读取或复制认证材料。除解析绑定所必需的本地操作外，核验通过前不开展其他任务工作。配置与身份细则见治理规范第四节。

## 读取与执行

主会话读取 `paths.source_root` 下的[治理规范](../../governance/codex-development-governance.md)，按第三节读取适用工程原则、
第五节恢复真实状态、第六节完成当前 Issue 闭环；需要操作步骤时读取
[编排程序](references/stage-procedure.md)，清理前必须读取其第五节。

- 只有主会话定位或创建当前仓库唯一匹配的 Issue；下游角色接收准确 Issue，不自行发现任务。
- 顺序使用 `scope-planner -> implementer -> reviewer`，同一共享路径只有一个实现者。主会话回读证据，
  核验批准与返工依据；`CHANGES_REQUESTED` 按规范分流，新提交重新审查。
- 规划按规范细化需求、验收场景与最小任务；实施和 PR 审查双向核对要求、实现、证据及新增行为的依据。
  主会话交付 Issue 中本轮分配任务，未经批准的建议不混入执行范围。
- 公开证据使用仓库相对路径，准确工作树绝对路径保留在私有交接中；发布边界按规范第三节执行。
- 工程原则适用于规划、实现和审查。依据与发现写入现有范围说明、PR 和 Review，不增设证明或状态账本。
- 命令权限不扩大角色职责、GitHub 身份、任务范围或破坏性授权；规划与审查角色保持被审对象只读。
- 合并只针对已获正式批准且没有阻塞的精确头提交，不使用管理员绕过；清理完成后才关闭当前 Issue
  或推进其中已批准任务。阶段实施与收尾完成后，交同一审查角色核对组合结果；主会话记录阶段结论，
  审查通过后关闭阶段并更新上层 Issue，然后停止。

完整授权与例外以治理规范第七节及编排程序的清理条件为准。不得创建、选择、激活或签发下一阶段，
不使用 `/goal`、后台轮询或其他治理工具的运行机制。
