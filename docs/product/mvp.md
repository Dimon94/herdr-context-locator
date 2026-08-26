# Herdr Context Locator MVP 合同

本文件是 MVP 范围、边界和验收标准的唯一产品合同。README 只负责安装与使用说明。

## 产品定位

Herdr Context Locator 是面向同时使用多个 Herdr Coding Agent 的开发者的单动作插件。它把当前 Agent Pane 转换成一段可粘贴的上下文定位指令，让接收 Agent 读取来源 Agent 的正式原生会话记录。

## 用户问题

用户能看见来源 Agent 所在的 Pane，却缺少一种短、稳定且自描述的方式，让另一个会话定位该 Agent 的完整正式上下文。Pane 屏幕输出可能截断、清屏或只保留局部内容，因此不能充当完整会话。

## 第一次成功

1. 用户聚焦来源 Agent Pane。
2. 用户按 `prefix+y`。
3. Herdr 显示 `copied to clipboard` 通知。
4. 用户把唯一一段英文定位指令粘贴到接收 Agent。
5. 接收 Agent 通过实时 Pane metadata 或复制时保存的 Session Reference，读取并搜索来源 Agent 的原生会话记录。
6. 接收 Agent 能回答一个只存在于来源会话、定位指令本身不包含的问题。

## 单一交互

MVP 只有 `copy-focused-context` 动作，不显示选择器，不提供多种复制格式，也不配置输出语言。推荐按键是 `prefix+y`。

复制内容使用英文，并包含：

- Pane ID；
- Agent kind；
- Session kind；
- Session source；
- Session reference；
- Working directory；
- 优先读取 Agent 原生会话记录的指令；
- 来源会话保持只读的约束。

定位指令先要求接收 Agent 运行 `herdr agent get <pane-id>`。Pane 已关闭或已经承载不同会话时，接收 Agent 改用复制时记录的 fallback metadata。

## 状态与数据边界

- Herdr 拥有 Pane 到 Agent Session 的实时映射。
- 各 Agent 的原生会话存储拥有正式 transcript。
- 操作系统剪贴板临时持有 Context Locator。
- 插件不持久化状态，不建立 transcript 副本，不拥有会话生命周期。
- Session Reference 不是 transcript。原生记录被删除、移动或变得不可访问后，fallback 不能恢复内容。

## 成功与失败语义

只有以下条件全部满足时才写入剪贴板：

- 调用上下文包含来源 Pane；
- `herdr agent get` 返回同一个 Pane；
- Agent kind 与 Session Reference 的 Agent kind 一致；
- Session kind、source、value 与工作目录均非空；
- 本机剪贴板命令成功完成。

Metadata 校验失败时不调用 clipboard command。Clipboard command 非零退出时，动作报告失败且不报告复制成功；该外部命令是否已部分改变系统剪贴板属于操作系统工具边界。所有失败都返回非零退出码，并通过 Herdr notification 给出恢复动作。

## MVP 能力

- 从 Herdr 插件动作上下文定位聚焦 Pane。
- 读取并校验 `herdr agent get` JSON。
- 生成确定性的英文 Context Locator。
- 支持 macOS `pbcopy`，以及 Linux `wl-copy`、`xclip`、`xsel`。
- 显示 Herdr 原生成功或失败通知。
- 使用 Path 与 opaque ID 两类 Session Reference。
- 自动化测试覆盖公开动作边界。
- 真实跨会话测试证明接收 Agent 能读取来源原生 session。

## 明确排除

- 复制完整 transcript 或 Pane scrollback。
- 对上下文做摘要、索引、同步或云端上传。
- 自动创建、选择、提示或恢复目标 Agent。
- 修改或继续运行来源会话。
- 右键菜单集成。
- 格式选择弹窗、语言选择和自定义模板。
- Windows 与远程主机到本地终端的 clipboard bridge。
- 修改 Herdr 核心源码。

## 发布边界

项目以独立 MIT 开源仓库发布到 GitHub。仓库包含有效 `herdr-plugin.toml` 并使用 `herdr-plugin` topic，以满足 Herdr 插件市场收录条件。创建远程仓库、推送和发布需要单独授权。

## 验收

自动化入口：

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/copy_context_locator.py
```

真实入口：

1. 本地 link 插件并从来源 Pane 调用 action。
2. 检查剪贴板只包含 Context Locator。
3. 把原文交给一个临时接收 Agent，并附加一个来源会话历史问题。
4. 接收 Agent 必须从原生 Session Reference 报告定位证据，并返回定位指令中不存在的正确答案。
5. 测试完成后关闭测试方创建的临时 Pane。
