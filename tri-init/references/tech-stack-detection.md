# 技术栈检测规则表

> 本文件是 `tri-init` 技术栈检测的规则单一事实源。
> `scripts/project-scan.py` 按此表逐项检测，新增规则在此追加。

| # | 检测目标 | 特征文件（存在即命中） | 提取内容 |
|---|---|---|---|
| 1 | Java / Maven | `pom.xml` | `<java.version>`、`<groupId>`、`<artifactId>`、`<modules>` |
| 2 | Java / Gradle | `build.gradle` / `build.gradle.kts` | `sourceCompatibility`、依赖 |
| 3 | Spring Boot | `pom.xml` 含 `spring-boot-starter` | Boot 版本、已启用 starter 列表 |
| 4 | RuoYi 框架 | 目录含 `ruoyi-*` 模块 | RuoYi 版本、模块清单、代码生成器 |
| 5 | TypeScript | `tsconfig.json` | TS 版本、编译选项 |
| 6 | Vite | `vite.config.ts` / `vite.config.js` | Vite 版本、插件 |
| 7 | Vue | `package.json` 含 `"vue"` | Vue 版本、UI 库 |
| 8 | React | `package.json` 含 `"react"` | React 版本、UI 库 |
| 9 | Element Plus | `package.json` 含 `element-plus` | 版本 |
| 10 | Ant Design | `package.json` 含 `ant-design` | 版本 |
| 11 | UnoCSS / Tailwind | `package.json` 含 `unocss` / `tailwindcss` | 版本 |
| 12 | Pinia / Vuex | `package.json` 含 `pinia` / `vuex` | 版本 |
| 13 | Go | `go.mod` | Go 版本、框架 |
| 14 | Python | `requirements.txt` / `pyproject.toml` | Python 版本、框架 |
| 15 | Node.js | `package.json` | Node 版本、包管理器（npm/yarn/pnpm） |
| 16 | Docker | `Dockerfile` / `docker-compose.yml` | 基础镜像 |
| 17 | CI/CD | `Jenkinsfile` / `.github/workflows/` | CI 工具 |
