---
name: tech-typescript
description: TypeScript 开发规范。tri-coding 在 design.md 氛围校准时按项目特征匹配加载，提供 TypeScript 特定的编码标准与质量检查。
tech_id: typescript
tech_name: TypeScript
category: language
---

# TypeScript 开发规范

> 本规范作为 tri-coding 技术栈体系的增强层，在 general.md 基底之上叠加 TypeScript 特定规范。

## 技术栈定义

TypeScript 是 JavaScript 的超集，在 JavaScript 之上叠加静态类型系统，提供编译期类型检查、现代 ES 特性与工程化能力。核心特性包括：类型注解与类型推断、泛型、联合/交叉类型、严格模式（strict）、模块系统、装饰器等，适用于需要类型安全与可维护性的中大型前端/Node.js 项目。

## 版本基线

- **TypeScript 5.0（2023）**：引入 `const` 类型参数（`<const T>`）、Stage 3 装饰器（`--experimentalDecorators` 不再必需，标准 ECMAScript 装饰器语义）、`--moduleResolution bundler`、`verbatimModuleSyntax` 取代 `importsNotUsedAsValues`/`preserveValueImports`（后者已移除）。这是破坏性变化集中的一次大版本升级
- **TypeScript 4.9（2022）**：新增 `satisfies` 操作符，允许在保留最精确推断类型的同时校验类型满足约束；`accessor` 关键字支持
- **TypeScript 5.1+（2023）**：JSX 相关改进，允许函数组件返回 `undefined`、`Promise` 不再需要 `await` 包裹即可作为返回值类型；装饰器元数据支持完善
- **TypeScript 5.2+（2023）**：完整支持 `using`/`await using` 显式资源管理（Stage 3 提案），与 `Symbol.dispose` 配合实现确定性资源释放

## 编码规范（技术特定）

### 类型系统

- **开启严格模式**：`tsconfig.json` 中启用 `strict: true`，让类型驱动 API 设计，减少运行时错误
- **禁止滥用 `any`**：类型不确定时使用 `unknown`，并通过类型守卫/断言函数收敛类型；必要时使用 `as` 断言需有明确依据
- **空值策略明确**：优先使用可选链 `?.` 与空值合并 `??`，避免无意义的非空断言 `!`
- **穷尽性检查**：对联合类型分支使用 `switch` + `never` 兜底，防止遗漏分支
- **类型即文档**：优先通过更精确的类型表达约束，减少文字解释成本
- **边界分层建模**：将"领域模型/DTO/视图模型"分层建模，避免同一类型同时承担多重语义
- **抽象克制**：泛型用于复用与约束，不为"看起来优雅"引入过度复杂的类型体操
- **运行时校验**：外部输入（HTTP、Storage、URL、IPC）必须在边界做校验，不把编译期类型当成运行时保障
- **善用 `satisfies` 操作符**（TS 4.9+）：需要同时满足"类型可被某约束校验"且"保留最精确的推断类型"时使用 `satisfies`，替代 `as` 强制断言或显式注解导致类型被宽化的场景
- **`const` 类型参数优先**（TS 5.0+）：函数/泛型推断默认按最宽类型推断（如字面量被推断为 `string`）；需要保留字面量类型时使用 `<const T>` 或在调用处 `as const`，避免在调用方反复加 `as const`
- **`enum` 与联合字面量选型**：优先使用联合字面量类型（`type Status = 'active' | 'inactive'`）保证可 tree-shaking 与零运行时开销；仅当需要运行时对象、反向映射、位标志组合时才使用 `enum`；禁止使用 `const enum`（在 `isolatedModules` 下行为不一致）
- **装饰器使用标准语义**（TS 5.0+）：新代码使用 Stage 3 标准 ECMAScript 装饰器（无需 `--experimentalDecorators`）；旧 `experimentalDecorators` 装饰器仅用于既有框架（NestJS/TypeORM 旧版）且不与新装饰器混用

### 模块与工具链

- **模块解析与 ESM/CJS 互操作**：根据运行环境选择 `moduleResolution`——Node 项目用 `nodenext` 并在 `package.json` 声明 `"type": "module"`，打包器项目（Vite/webpack/esbuild）用 `bundler`；CJS 中 `import` ESM 必须用动态 `import()`，禁止在 `.ts` 中混用 `require` 与 `import` 不一致语义
- **tsconfig 关键字段**：`target` 与运行环境最低支持对齐（浏览器按 baseline）；`module` 与 `moduleResolution` 配套设置；`lib` 与 `target` 一致并按需补充 `DOM`/`DOM.Iterable`；`paths` 用于路径别名且必须与打包器 alias 同步；启用 `verbatimModuleSyntax: true` 显式区分类型导入与值导入（`import type`）
- **工具链规范**：使用 ESLint + `@typescript-eslint` 插件（`@typescript-eslint/no-floating-promises`、`no-misused-promises` 等类型感知规则）；CI 中运行 `tsc --noEmit` 做独立类型检查，不依赖打包器旁路；`isolatedModules: true` 保证单文件可被转译工具安全处理

### 命名约定

- 变量/函数使用 `camelCase`，类型/接口/类使用 `PascalCase`，常量使用 `UPPER_SNAKE_CASE`
- 接口命名不使用 `I` 前缀（如直接用 `User` 而非 `IUser`）

### 不可变性与模块

- 优先 `const`，仅在确需重赋值时使用 `let`，禁止 `var`
- 异步处理统一使用 `async/await`，错误处理模式与项目约定保持一致
- 公共 API、复杂泛型、关键约束需提供文档注释

## 质量检查清单（技术特定）

- [ ] `tsconfig.json` 是否启用 `strict: true` 及相关严格选项
- [ ] 是否避免使用 `any`；不可避免时是否使用 `unknown` + 类型守卫收敛
- [ ] 是否避免无意义的非空断言 `!`，改用 `?.` / `??`
- [ ] 联合类型分支是否使用 `switch` + `never` 做穷尽性检查
- [ ] 外部输入是否在边界层做运行时校验
- [ ] 接口命名是否去掉 `I` 前缀
- [ ] 是否优先 `const`，禁用 `var`
- [ ] 公共 API 与复杂泛型是否提供文档注释
- [ ] 是否合理使用 `satisfies` 替代 `as` 断言以保留精确推断
- [ ] `enum` 与联合字面量选型是否合理，是否避免 `const enum`
- [ ] `moduleResolution`/`module` 是否与运行环境（Node/打包器）配套一致
- [ ] `paths` 别名是否与打包器 alias 同步；是否启用 `verbatimModuleSyntax`
- [ ] CI 是否运行 `tsc --noEmit` 独立类型检查，是否启用 `isolatedModules`
- [ ] 装饰器是否使用 Stage 3 标准语义，是否避免新旧装饰器混用

## 参考资料

- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [tsconfig 配置参考](https://www.typescriptlang.org/tsconfig)
- [Airbnb JavaScript/TypeScript 风格指南](https://github.com/airbnb/javascript)
- [TypeScript 5.0 Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html)
- [@typescript-eslint 规则](https://typescript-eslint.io/rules/)
