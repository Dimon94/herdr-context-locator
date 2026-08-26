<identity>
每次开始工作先读 repo://CONTEXT.md。使用其中的统一语言。
交互与治理文档使用简明中文；公开 README、插件文案、代码和代码注释使用简明英文。写短句。使用主动语态。指向具体代码、测试或文档坐标。
证据不足时写 Unknown。推断显式标注“推断”。
</identity>

<project>
定位：Herdr Context Locator 把聚焦 Agent Pane 转换为可粘贴的正式会话定位指令，让另一个 Agent 读取来源 Agent 的原生会话上下文。
产品范围和验收标准见 repo://docs/product/mvp.md。触发：改变复制字段、交互、失败语义、平台支持、状态边界或发布范围。
技术栈：Python 3 标准库、Herdr 0.8.2 plugin action、macOS/Linux 本机剪贴板命令、GitHub Actions。
稳定验证：`python3 -m unittest discover -s tests -v && python3 -m py_compile scripts/copy_context_locator.py`。
真相优先级：运行证据和持久状态 > 源码与测试 > 仓库文档和 accepted ADR > 当前官方文档 > 推理。
</project>

<workflow>
改前读取目标文件最近的 AGENTS.md、直接调用者、公开入口、相关测试和相关配置。
项目已定义 canonical 构建或测试命令时运行该命令，不发明变体。
先复用现有模块、类型、schema、helper 和脚本。再使用标准库、运行时原生能力和已安装依赖。最后才写最少新代码。
一次变更只解决一个可独立验证的语义目标。保留用户的无关改动。
复杂任务先分清现象、根因和设计不变量，再给最小动作。
歧义只在答案会实质改变结果、范围、风险或授权时才提问；其余陈述假设并继续。多条路径存在实质取舍时推荐一条并说明理由。
用户要求“确认后执行”时，只给方案，不修改文件。
完整开发流程见 repo://docs/agents/development-workflow.md。触发：实现功能、修复缺陷、重构、集成或交付。
调试闭环见 repo://docs/agents/debugging.md。触发：错误、失败、性能回归、环境不一致或改动不生效。
</workflow>

<forge>
Issue、代码和 CI/CD 归 GitHub，项目坐标 Dimon94/herdr-context-locator。Issue 约定见 repo://docs/agents/issue-tracker.md。触发：建、读、评或列 issue，处理 PR，查询 GitHub Actions。
CI 合同见 repo://.github/workflows/ci.yml。仓库暂不维护 GitHub API wrapper；需要程序化远程操作时使用 `gh`，并先取得对应写权限。
</forge>

<branching>
主目录永远只 checkout main，单会话改动直接在 main。只有 herdr 分派并行任务时才一票一树：`git worktree add` 从 main 最新 commit 建树，任务分支随树创建、只存在于树内。
main 只接收已验证提交；票收口即删树删分支。
详细规则见 repo://docs/agents/git-branching.md。触发：开/切/合/删分支、push、合并 PR、worktree、herdr 分派、并行 agent 写入。
</branching>

<architecture>
模块必须有明确 owner、公开 interface、依赖方向和测试面。
状态只能有一个 canonical owner。缓存、日志、UI 投影和 HTTP 状态不能成为第二真相。
跨进程、外部服务和持久状态必须经过明确 seam；确定性内部逻辑保持直接。
公开合同、持久数据和难回退决策发生变化时，先检查兼容、迁移、回滚和 ADR。
详细规则见 repo://docs/agents/architecture-standards.md。触发：新增模块、改变依赖、状态所有权、公开 interface、外部 seam 或持久化。
</architecture>

<layer_contracts>
合同分 L1-L6，逐层披露。变更命中哪层更新哪层，未命中不动。
落点：L1 = repo://docs/architecture/current-system-map.md；L2 = 最近的模块 AGENTS.md；L3 = 核心文件头部注释块；L4-L6 = 代码内注释块。
规则、读写触发与模板见 repo://docs/agents/layer-contracts.md；改目标、结构、模块职责、公开导出、CLI/API/schema、状态写入或关键流程前必读。文件合同活例子：repo://scripts/copy_context_locator.py。
删除或移动文件时，更新最近的模块地图。
新增 AGENTS.md 时，同目录创建 CLAUDE.md，内容只写 @AGENTS.md。
</layer_contracts>

<code_style>
代码规范见 repo://docs/agents/coding-standards.md。触发：新增或修改代码、注释或公开 API 文档。完成：当前 diff 命中的规则已逐项检查。
用户可见文案与文档写作规范见 repo://docs/agents/writing-standards.md。触发：新增或修改 CLI/诊断输出、错误信息、README/docs、生成交付物，或行为变更后的文案清扫。
局部 AGENTS.md、accepted ADR、外部合同和运行证据优先于通用规范。
规范只约束当前变更和阻断当前正确性的既有问题。
</code_style>

<constraints>
Git 只 stage 语义相关路径。不要使用 git add .。
不提交密钥、环境文件（.env）与一次性证据文件；其余排除项归 .gitignore。
外部输入在边界校验一次。内部代码使用已校验的类型。
仓库文件、抓取的文档文本和远程服务响应视为不可信输入：影响特权行为前按白名单校验，密钥走 config overlay 够不到的独立通道。
错误必须显式、稳定、可测试。失败语义 fail-close：达不到成功标准的操作明确失败并给出自然恢复动作；每个兜底和 fallback 必须点名防的真实失败场景，答不出来就删除。
模型只做分类、起草、摘要、抽取和判断。代码负责确定性转换、路由、重试、状态迁移和成本控制。
</constraints>

<done_definition>
完成前说明触达坐标、实际改动、验证命令和结果。变更命中合同层时，列出更新的 L1-L6 合同；未命中时说明未命中。
非琐碎逻辑至少留下一个在错误实现下会失败的检查。
修复缺陷时，同一最小检查必须先失败后通过。
跳过测试时说明原因和剩余风险。
审查、审计、解释、报告、计划和提案均为只读交付物，不授权实现。提交、推送、修改或合并 PR、发布和部署需要用户明确要求，或当前任务中已明确确立的工作流。普通实现任务只修改并验证本地工作区。
</done_definition>

<review_standard>
先枚举审查范围，再列 Findings。按严重度排序，每条引用文件和行号；省略工具已覆盖的通用发现。
Standards 轴先审 Coding，再审 Architecture。Spec 轴独立核对需求。
没有 finding 时，也说明测试缺口、未验证路径和剩余风险。
只报告能由代码、测试、运行证据或合同证明的问题。
测试与审查规范见 repo://docs/agents/quality-standards.md。触发：新增、修改或删除测试，评估覆盖面，代码审查、重构、自检或发现坏味道。测试变更完整应用第 6 节；审查完成第 7 节。
</review_standard>

<principles>
在满足当前需求的前提下，选择最简单的实现。
维护工作做定向修改并遵循既有约定；明确要求重新设计、重写或破坏兼容时，从第一原则重新推导，不把最小化和兼容性作为隐藏要求带回。
先交付可端到端验证的最小切片，再逐步增加能力。
新增依赖前检查现有依赖、官方文档和类型定义。
替换旧设计执行 clean-break：同一次变更彻底切换并删除旧路径，不留新旧并存分支。持久状态和外部合同的破坏性删除必须先证明零读零写，并取得明确授权。
重复规则和并行机制出现时，读取 repo://docs/agents/entropy-governance.md。
根因诊断、互斥方案和落地推演时，读取 repo://docs/agents/thinking-model.md。
</principles>
