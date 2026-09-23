# <中文名>（<slug>）

![version](https://img.shields.io/badge/version-1.0.0-blue) ![license](https://img.shields.io/badge/license-MIT-green)

> <一句话定位：这个 skill 做什么、用户心智是什么>

## 特性

- **<特性 1>**：<说明>
- **<特性 2>**：<说明>
- **可扩展**：<说明新增维度/规则的零改动路径>

## 安装

```bash
# 方式一：SkillHub prompt（环境支持时）
请根据 https://skillhub.cn/install/skillhub.md，安装 <slug>。

# 方式二：克隆仓库
git clone <repo-url>
```

本 skill **支持独立安装**，含上游依赖检测<两|三>态逻辑。

## 使用

<以自然语言交互为例，说明触发方式与典型链路；若依赖上游，说明上游缺失时的降级行为>

```
用户：<示例输入>
     ↓
<skill> <做了什么>
     ↓
<产出什么>
```

## 目录结构

```
<slug>/
├── SKILL.md      主入口
├── README.md     本文件
├── CHANGELOG.md  版本变更记录
├── references/   静态参考资料
├── scripts/      可执行实现
├── templates/    产物模板
└── tests/        测试用例
```

## 设计原则

1. **<原则 1>**：<说明>
2. **<原则 2>**：<说明>

## 版本

当前版本见 `SKILL.md` frontmatter 与 `CHANGELOG.md` 首条（两者 MUST 一致）。

## 许可证

MIT — 详见仓库根 `LICENSE`。
