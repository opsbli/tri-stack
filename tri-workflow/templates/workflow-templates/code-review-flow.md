# 代码审查流水线模板

> 模板 ID：`code-review-flow`
> 适用场景：PR 提交 → 自动审查 → 人工审查 → CI 校验 → 合并
> 核心节点：PR 创建 → 自动审查 → 人工审查 → CI 校验 → 合并 → 通知

## 模板定义

```yaml
workflow_name: <项目名>-code-review
workflow_type: code-review-flow
template_id: code-review-flow
template_confidence: 100

nodes:
  - id: pr_created
    name: PR 创建
    type: auto
    role: { type: system, target: github/gitlab }
    action: 监听 PR 创建事件
    inputs: []
    outputs:
      - { name: pr_info, type: object, description: PR 信息（标题/描述/分支/文件变更） }
    depends_on: []

  - id: auto_review
    name: 自动代码审查
    type: auto
    role: { type: skill, target: tri-review, version: ">=1.0.0" }
    action: AI 自动审查代码，检查规范/安全/性能
    inputs:
      - { name: pr_info, type: object, source: pr_created.outputs.pr_info, required: true }
    outputs:
      - { name: review_result, type: object, description: 审查结果（问题列表/严重程度/建议） }
      - { name: review_passed, type: boolean, description: 是否通过自动审查 }
    sla: { expected_duration: 3m, timeout: 10m, unit: m }
    depends_on: [pr_created]

  - id: ci_check
    name: CI 自动化校验
    type: auto
    role: { type: system, target: github-actions }
    action: 运行 CI 流水线（构建+测试+安全扫描）
    inputs:
      - { name: pr_info, type: object, source: pr_created.outputs.pr_info, required: true }
    outputs:
      - { name: ci_result, type: object, description: CI 校验结果 }
      - { name: ci_passed, type: boolean, description: 是否通过 CI }
    sla: { expected_duration: 10m, timeout: 30m, unit: m }
    retry: { max_attempts: 2, interval: 120s, backoff: fixed, on_failure: abort }
    depends_on: [pr_created]

  - id: human_review
    name: 人工代码审查
    type: manual
    action: 指定 Reviewer 进行人工审查
    inputs:
      - { name: auto_review_result, type: object, source: auto_review.outputs.review_result, required: true }
    outputs:
      - { name: human_review_result, type: object, description: 人工审查意见 }
      - { name: approved, type: boolean, description: 是否通过 }
    sla: { expected_duration: 4h, timeout: 24h, unit: h }
    depends_on: [auto_review, ci_check]

  - id: merge_check
    name: 合并条件判断
    type: condition
    conditions:
      - { expression: "review_passed == true && ci_passed == true && approved == true", target_node: merge_pr }
      - { expression: "review_passed == false || ci_passed == false || approved == false", target_node: request_changes }
    depends_on: [human_review]

  - id: merge_pr
    name: 自动合并
    type: auto
    role: { type: system, target: github/gitlab }
    action: 自动合并 PR 到目标分支
    inputs:
      - { name: pr_info, type: object, source: pr_created.outputs.pr_info, required: true }
    outputs:
      - { name: merge_result, type: object, description: 合并结果 }
    sla: { expected_duration: 30s, timeout: 2m, unit: m }
    depends_on: [merge_check]

  - id: request_changes
    name: 请求修改
    type: notification
    notification:
      channel: 飞书
      template: review-changes-requested
      recipients: [<PR 作者>]
    depends_on: [merge_check]

  - id: notify_done
    name: 通知完成
    type: notification
    notification:
      channel: 飞书
      template: review-complete
      recipients: [<团队群>]
    depends_on: [merge_pr]

edges:
  - { from: pr_created, to: auto_review, condition: always }
  - { from: pr_created, to: ci_check, condition: always }
  - { from: auto_review, to: human_review, condition: always }
  - { from: ci_check, to: human_review, condition: always }
  - { from: human_review, to: merge_check, condition: always }
  - { from: merge_check, to: merge_pr, condition: "review_passed == true && ci_passed == true && approved == true" }
  - { from: merge_check, to: request_changes, condition: "review_passed == false || ci_passed == false || approved == false" }
  - { from: merge_pr, to: notify_done, condition: always }

triggers:
  type: event
  detail: PR 创建或更新时触发

global:
  error_handling:
    strategy: stop
  notifications:
    on_start: false
    on_complete: true
    on_failure: true
```

## 可定制参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| 项目名 | — | 必填 |
| 自动审查 Skill | tri-review | 代码审查 Skill |
| Reviewer | — | 指定的人工 Reviewer |
| PR 平台 | GitHub | GitHub/GitLab |
| 通知渠道 | 飞书 | 飞书/Slack/邮件 |
| 审查超时 | 24h | 人工审查超时时间 |