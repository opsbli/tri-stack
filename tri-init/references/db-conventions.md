# 数据库规范（租户 / 审计 / 逻辑删除）

> 本文件定义 tri-init 在检测到代码生成器时，须提取并写入 project-profile 的数据库规范。
> **目的**：确保 tri-coding 产出的 design.md 中，数据表设计严格遵循项目已有的字段规范。

---

## RuoYi-Vue-Plus 5.x 规范（从 ops-pilot 实测提取）

### 审计字段（`BaseEntity.java`）

所有业务表 MUST 包含以下审计字段：

| 字段名 | Java 类型 | 数据库类型 | 说明 |
|---|---|---|---|
| `create_dept` | `Long` | `BIGINT` | 创建部门 |
| `create_by` | `Long` | `BIGINT` | 创建者 |
| `create_time` | `Date` | `DATETIME` | 创建时间 |
| `update_by` | `Long` | `BIGINT` | 更新者 |
| `update_time` | `Date` | `DATETIME` | 更新时间 |

### 租户字段（`TenantEntity.java` extends BaseEntity）

多租户表 MUST 额外包含：

| 字段名 | Java 类型 | 数据库类型 | 说明 |
|---|---|---|---|
| `tenant_id` | `String` | `VARCHAR(20)` | 租户ID |

### 逻辑删除字段

启用逻辑删除的表 MUST 包含：

| 字段名 | Java 类型 | 数据库类型 | 说明 |
|---|---|---|---|
| `del_flag` | `String` | `CHAR(1)` | 删除标志（0=存在 1=删除） |

### 标准表模板

```sql
CREATE TABLE {table_name} (
    id              BIGINT       NOT NULL                COMMENT '主键ID',
    tenant_id       VARCHAR(20)  DEFAULT '000000'        COMMENT '租户编号',
    -- 业务字段 --
    create_dept     BIGINT                               COMMENT '创建部门',
    create_by       BIGINT                               COMMENT '创建者',
    create_time     DATETIME                             COMMENT '创建时间',
    update_by       BIGINT                               COMMENT '更新者',
    update_time     DATETIME                             COMMENT '更新时间',
    del_flag        CHAR(1)      DEFAULT '0'             COMMENT '删除标志（0存在 1删除）',
    PRIMARY KEY (id)
) ENGINE=InnoDB COMMENT='{table_comment}';
```

---

## 通用规范（非 RuoYi 项目）

无代码生成器时，使用以下通用规范：

| 字段名 | 类型 | 说明 |
|---|---|---|
| `id` | `BIGINT` / `UUID` | 主键 |
| `created_at` | `TIMESTAMP` | 创建时间 |
| `updated_at` | `TIMESTAMP` | 更新时间 |
| `deleted_at` | `TIMESTAMP` | 软删除时间（可选） |

---

## 检测到新规范时的处理

如果目标项目的代码生成器使用不同的字段命名或类型，tri-init MUST：

1. 从项目的 `BaseEntity.java`（或等价基类）中**提取实际字段名与类型**
2. 将提取结果写入 project-profile.json 的 `db_conventions` 区
3. tri-coding 门② 产出的 design.md 中，数据表设计 MUST 遵循该规范
