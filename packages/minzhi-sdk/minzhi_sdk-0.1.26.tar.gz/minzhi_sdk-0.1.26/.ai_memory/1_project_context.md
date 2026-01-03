# 项目核心知识库
## 项目目标
提供敏智平台的 Python SDK，支持 AE 和 CMDB 操作。

## 核心共识
- 遵循 Semantic Versioning
- 使用 uv 管理依赖
- 代码风格遵循 PEP 8

## 技术架构
- **AEClient**: 提供数据库 CRUD 操作。
- **CmdbClient**: 负责 CMDB 交互，v0.1.14 重构引入 `QueryBuilder` 和标准化查询条件。
- **Authorization**: 处理 4A 认证与 RSA 加密。

## 开发规范
- 必须编写文档字符串 (Google Style)。
- 使用 `uv` 进行依赖管理和构建。
- 发布流程：`uv build` -> `./publish.sh test` -> `./publish.sh prod`。
