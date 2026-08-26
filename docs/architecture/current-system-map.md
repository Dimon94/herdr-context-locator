# Current System Map

Status: current

本文件描述 Herdr Context Locator 当前可验证的模块、状态所有权、外部 seam 和运行入口。产品范围归 repo://docs/product/mvp.md。

## 当前事实

- 运行形态：Herdr 0.8.2+ plugin action。
- 技术栈：Python 3 标准库。
- 支持平台：macOS、Linux。
- 公开入口：`dimon.context-locator.copy-focused-context`。
- 运行文件：repo://scripts/copy_context_locator.py。
- 插件配置：repo://herdr-plugin.toml。
- 持久状态：无。
- CI：repo://.github/workflows/ci.yml。

## 端到端链路

```text
Herdr action context
  -> Context Locator Action
  -> herdr agent get <pane-id>
  -> validated Agent Session metadata
  -> deterministic Context Locator
  -> host clipboard command
  -> Herdr notification
  -> Receiving Agent
  -> agent-native session store
```

Context Locator Action 在 clipboard write 成功前不报告成功。Receiving Agent 的读取行为不在插件进程内；复制指令定义它应读取的正式来源。

## Ownership

| Module / system | Owns | Does not own | Public interface | Verification |
| --- | --- | --- | --- | --- |
| Context Locator Action | 调用上下文校验、metadata 一致性、定位指令渲染、clipboard write 与通知顺序 | transcript、会话生命周期、持久状态 | manifest action `copy-focused-context` | repo://tests/test_plugin_action.py |
| Herdr | Pane 到 Agent Session 的实时映射与 `agent get` JSON | Agent 原生 transcript | `herdr agent get <pane-id>` | 本机 action smoke test |
| Agent-native session store | Canonical Session Context | Herdr Pane 与系统剪贴板 | Session Reference 对应的原生记录 | 跨会话验收 |
| Host clipboard | 最近一次成功写入的 Context Locator | 会话内容与长期保存 | `pbcopy` / `wl-copy` / `xclip` / `xsel` | action contract test |

依赖方向：

```text
Herdr manifest -> Context Locator Action -> Herdr CLI
                                      \-> host clipboard
Receiving Agent -> Herdr CLI or Fallback Metadata -> agent-native session store
```

## 不变量

- 插件只复制 Context Locator，不读取或复制 transcript。
- Session Reference 的 owner 是 Herdr 与 Agent 原生会话存储；插件只捕获只读快照。
- 返回 Pane、Agent kind 或 Session Reference 不一致时 fail-close。
- Clipboard write 完成后才显示 `copied to clipboard`。
- 来源会话默认只读。
- Pane Screen Output 不作为完整会话来源。

## 外部 seam

### Herdr invocation environment

Action 从 `HERDR_PANE_ID` 读取 Pane Locator；缺失时读取 `HERDR_PLUGIN_CONTEXT_JSON.focused_pane_id`。两个入口都必须解析出非空 Pane Locator。

### Herdr agent metadata

`herdr agent get` 必须返回与请求 Pane 一致的 Agent info。Agent kind、Session Reference 的 agent/kind/source/value 及工作目录必须完整，且 Agent kind 必须一致。

### Clipboard

macOS 使用 `pbcopy`。Linux 依次发现 `wl-copy`、`xclip`、`xsel`。不存在可用命令或写入失败时不报告成功。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/copy_context_locator.py
```

公开动作测试通过 fake executable 穿过完整进程边界。真实跨会话验收步骤见 repo://docs/product/mvp.md「验收」。

## PROTOCOL

改变顶层链路、模块职责、状态 owner 或外部 seam 时同步：

- repo://CONTEXT.md；
- repo://docs/product/mvp.md；
- repo://AGENTS.md `<project>`；
- repo://herdr-plugin.toml；
- repo://scripts/copy_context_locator.py 文件合同；
- repo://tests/test_plugin_action.py。
