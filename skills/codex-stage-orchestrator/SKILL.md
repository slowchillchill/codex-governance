---
name: codex-stage-orchestrator
description: 仅在用户显式调用 codex-stage-orchestrator 并提出明确开发需求，或已接入仓库按共同规则接受决策／研究组有效委托时，编排一个任务或父交付中已批准子任务的规划、实现、独立审查、合并与收尾。仅提及、询问或修改 Skill 及启动 Profile 不启用闭环；不选择批准范围外任务。
---

# Codex 任务与父交付编排

## 启动边界

先确认目标仓库根 `AGENTS.md` 已接入，并且用户显式调用本 Skill 给出明确开发需求，或接收流程接受已获用户授权的决策／研究组明确委托。委托必须交付准确 Issue、原授权、范围、验收、预计成本、同一阶段预算归属和固定回传入口，以结构化 Skill 输入接单；仅有材料不是委托。
显式调用是 `$codex-stage-orchestrator` 或明确要求“使用 codex-stage-orchestrator”。
未显式调用且未接受有效委托，或用户明确禁止时，按当前任务授权处理，不执行治理身份核验、Issue 查询或角色派生。
同一已授权交付的澄清与继续执行沿用原授权；范围外新任务需重新显式调用或接受新的有效委托。
研究 Skill 的启用或单纯交接材料不替代上述条件；有效直接签发按治理源 `governance/group-collaboration.md` 接收，不接管研究职责。
`agents/openai.yaml` 保持 `policy.allow_implicit_invocation: false`。

普通启动即可调用本 Skill；三个治理角色由启动时加载的原生配置注册，安装方式见
[安装说明](../../docs/installation.md#3-安装并注册原生角色)。调用 Skill 不切换 Profile、模型或命令权限。

确认启用后，先通过工具只读定位本机绑定：非空的 `CODEX_GOVERNANCE_CONFIG` 指定文件，否则读取
`${XDG_CONFIG_HOME:-$HOME/.config}/codex-governance/local.toml`。通过 `paths.source_root` 定位其下
`governance/codex-development-governance.md`，先读取“本机配置与规则定位”和“身份核验与命令归属”。
按这两节读取 `github.development`，用治理源 `scripts/group_github.py --group development check` 核验身份；全部开发角色使用同一身份。核验通过前不开展具体任务。后续平台命令都使用同一脚本，排除继承令牌并设置绑定目录。缺失或不符时停止，不切换全局账号，不借用研究／决策身份，不读取认证材料。

## 读取与执行

主会话读取同源 `governance/group-collaboration.md` 和 `paths.source_root` 下的[治理规范](../../governance/codex-development-governance.md)，按第三节读取适用工程原则。
交付边界与父交付授权以第二节为准，启动恢复与 Project 同步以第五节为准，候选审查、反馈分流、合并及
关闭条件以第六节为准。需要交接或操作步骤时读取[编排程序](references/stage-procedure.md)，清理前必须
读取其第五节；本 Skill 不另定义闭环条件。

- 委托任务回读准确 Issue 的来源、范围和预算；用户直接调用时由主会话定位或创建当前仓库唯一匹配的交付 Issue；下游角色接收本轮交付 Issue、当前执行 Issue、
  适用合同和必要 Project 引用，不自行发现任务。
- 跨路线委托区分逻辑参与者、原协作请求与实际工程签发，保留实际签发组创建 PR 和固定返回；不按账号或当前环境判断归属。公共任务复用原模块准确 Issue，确认单项主责，公共合并与各路线采用分别判断。
- 首次按 `scope-planner -> implementer -> reviewer` 顺序交接，同一共享路径只有一个实现者。主会话
  回读证据，在同一实现者和审查者之间组织必要的候选审查、返工、提交和正式 Review。
- 研究来源任务按[研究来源需求的接收与验证](../../governance/codex-development-governance.md#研究来源需求的接收与验证)
  确定工程范围，按[工程交付返回研究](../../governance/codex-development-governance.md#工程交付返回研究)交回事实；
  工程验收和研究结论各按自身合同，不自动恢复研究或关闭来源研究任务。
- 开发组验证、推送后返回仓库、基线、分支、提交及 PR 材料，由实际签发组创建 PR 并回传链接。开发组维护 PR、正式 Review、批准、合并与收尾，结果固定回签发组。
- 暂停、恢复或重新签发前核对原写入者、活动作业、未提交现场、遗留队列和剩余预算；远端由实际执行方确认，沉默不表示接受或停止。跨环境用 GitHub 来源任务交接，可访问环境再用 Agent Center；未确认停止不启动第二执行者。偏航、停滞和异常按共同规则返回事实及可选路径，不重置失败历史。
- 公开证据使用仓库相对路径，准确工作树绝对路径保留在私有交接中；发布边界按规范第三节执行。
- 按[提交前独立内容审查](../../governance/engineering-principles.md#提交前独立内容审查)处理适用候选，通过后才提交；
  候选结论不替代当前 PR 精确头的正式批准。
- 必要验证未通过时，按[验证结果与交付推进](../../governance/engineering-principles.md#验证结果与交付推进)
  停止受影响的交付动作；已有批准不能覆盖失败，恢复执行同样适用。
- 执行偏差、错误与困难按[执行偏差与异常处理](../../governance/engineering-principles.md#执行偏差与异常处理)
  查证和分流；达到停止条件时由主会话向用户汇报，角色交接或会话恢复不重新开始尝试。
- 命令权限不扩大角色职责、GitHub 身份、任务范围或破坏性授权；规划与审查角色保持被审对象只读。
  不使用管理员绕过。

完整授权与例外以治理规范第七节及编排程序的清理条件为准。不得创建、选择、激活或签发范围外任务，
不使用 `/goal`、后台轮询或其他治理工具的运行机制。
