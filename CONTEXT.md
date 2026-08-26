# Herdr Context Locator Context

本文件只保存项目统一语言。产品范围与验收标准归 repo://docs/product/mvp.md。

## 使用规则

- 代码、测试、issue 和文档使用本文件定义的 canonical term。
- 一个概念只保留一个名称。
- 新概念必须有需求、运行证据或 accepted ADR 支持。

## 已确认词汇

**Source Agent Session（来源 Agent 会话）**
: 用户希望另一个 Agent 读取的原始 Coding Agent 会话。它的原生会话存储拥有正式记录。
_Avoid_: 来源 Pane、终端窗口、scrollback。

**Receiving Agent（接收 Agent）**
: 接收 Context Locator，并据此读取来源 Agent 会话的 Agent。它只读来源会话，除非用户另行授权。
_Avoid_: 目标 Pane、自动恢复器。

**Canonical Session Context（正式会话上下文）**
: Source Agent Session 在对应 Agent 原生会话存储中的完整记录。
_Avoid_: Pane Screen Output、摘要、缓存副本。

**Pane Locator**
: Herdr 为当前 Pane 提供的实时标识。它用于查询当前 Pane 承载的 Agent Session，但不保存会话内容。
_Avoid_: Session ID、持久会话地址。

**Session Reference**
: Herdr 报告的 Agent 原生会话引用。它可以是路径或 opaque ID，用于定位 Canonical Session Context。
_Avoid_: transcript、Pane ID、恢复命令。

**Fallback Metadata**
: 复制时捕获的 Agent kind、Pane Locator、Session Reference 与工作目录。Pane Locator 失效或指向不同会话时，Receiving Agent 使用它继续定位。
_Avoid_: transcript 备份、插件状态。

**Context Locator**
: 插件写入剪贴板的单段英文指令。它包含 Pane Locator 和 Fallback Metadata，指导 Receiving Agent 定位 Canonical Session Context。
_Avoid_: context copy、handoff summary、resume command。

**Pane Screen Output**
: Pane 当前可见内容与 Herdr 保留的 scrollback。它只用于诊断，不能代表 Canonical Session Context。
_Avoid_: transcript、完整会话。
