# Issue tracker

本仓的 issue 和 PR 归 GitHub 项目 `Dimon94/herdr-context-locator`：

```text
https://github.com/Dimon94/herdr-context-locator
```

## 约定

- 建、评论、关闭或打标 issue 属于远程写操作，执行前取得明确授权。
- 读取 issue 时同时检查 body、labels、linked PR 和最新评论。
- Agent 只在任务明确批准自动化时使用 `gh` 修改远程状态。
- 仓库不维护独立 GitHub API wrapper。
- CI 事实来自 GitHub Actions run 与 job log，不从 commit 或 PR 状态推断。

## 阻断与依赖

阻断语义以 issue body 的 `Blocked by: #x #y` 为准。判断解除阻断时读取每个引用 issue 的 live state。

## Wayfinding 编排

- Map：label `wayfinder:map`。
- 子 ticket：label `wayfinder:map-<issue-number>` 与一个类型 label。
- 认领：label `wayfinder:claimed`。
- Frontier：同一 map 下仍 open、未 claimed、且所有 `Blocked by` 已 closed 的 issue。

创建标签、issue、评论或关闭 issue 都需要对应远程写授权。
