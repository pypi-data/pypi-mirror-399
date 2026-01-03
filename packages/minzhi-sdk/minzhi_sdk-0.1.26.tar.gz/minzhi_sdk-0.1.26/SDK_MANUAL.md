# Auto Engine SDK 使用手册

本手册详细介绍了Auto Engine SDK 的所有核心组件及其方法。SDK 主要包含三个部分：
1.  **AEClient**: 用于自动化操作 Auto Engine 的数据库操作。
2.  **CmdbClient**: 用于配置管理数据库 (CMDB) 的数据交互。

---

## 1. AEClient (自动化执行客户端)

`AEClient` 提供对敏智平台数据库的增删改查 (CRUD) 操作。

**引用方式:**
```python
from minzhi import AEClient
```

**初始化:**
```python
client = AEClient(businessId="业务ID", table_name="表名")
```

### 1.1 查询方法

| 方法 | 签名 | 描述 |
| :--- | :--- | :--- |
| **selectPage** | `selectPage(current: int, pageSize: int, **kwargs) -> Result` | 分页查询数据。 |
| **selectAll** | `selectAll(fields: List[str] = [], query: Dict[str, Any] = {}, **kwargs) -> Result` | 查询满足条件的所有数据。`query` 为简单的键值对相等匹配。 |
| **getEnum** | `getEnum(enum_name: str, **kwargs) -> Result` | 获取指定枚举定义的键值对。 |

**示例:**
```python
# 分页查询
res = client.selectPage(current=1, pageSize=20)

# 查询所有 (筛选 status='active'，仅返回 id 和 name)
res = client.selectAll(fields=["id", "name"], query={"status": "active"})

# 获取枚举
enum_res = client.getEnum("device_status")
```

### 1.2 写入方法

| 方法 | 签名 | 描述 |
| :--- | :--- | :--- |
| **insertOne** | `insertOne(data: Dict[str, Any], **kwargs) -> Result` | 插入单条数据。 |
| **insertMany** | `insertMany(data: List[Dict[str, Any]], **kwargs) -> Result` | 批量插入数据。 |
| **insertOrUpdate** | `insertOrUpdate(data: Dict[str, Any], **kwargs) -> Result` | 插入或更新（根据主键判断）。 |
| **updateMany** | `updateMany(data: List[Dict[str, Any]], **kwargs) -> Result` | 批量更新数据。需要包含筛选条件。 |
| **deleteByIds** | `deleteByIds(ids: List[str], **kwargs) -> Result` | 根据 ID 列表批量删除。 |
| **delete** | `delete(fields: List[str] = [], query: Dict[str, Any] = {}, **kwargs) -> Result` | 根据条件删除数据。 |

**示例:**
```python
# 插入
client.insertOne({"name": "Server A", "ip": "1.1.1.1"})

# 批量更新 (注意结构：where 指定条件，data 指定更新内容)
# 注意：具体 updateMany 的 data 结构取决于后端实现，通常为 list of dict
# 或者是特定结构 { "where": {...}, "data": {...} }，请参考具体业务文档
client.updateMany([
    {"where": {"id": "1"}, "data": {"status": "offline"}}
])
```

### 1.3 Result 对象

所有 AEClient 方法返回 `Result` 对象，用于统一处理响应。

| 方法 | 描述 |
| :--- | :--- |
| `is_success() -> bool` | 请求是否成功 (code == 200)。 |
| `ensure_success() -> Result` | 成功则返回 self，失败则抛出异常。 |
| `get_data() -> Any` | 获取响应体数据 (`body`)。如果是枚举查询，会自动转换为 Dict。 |
| `to_json() -> str` | 将数据转换为 JSON 字符串。 |
| `count() -> int` | 获取返回数据的数量。 |
| `to_dataframe() -> pd.DataFrame` | 转换为 Pandas DataFrame (需安装 pandas)。 |
| `get_error_message() -> str` | 获取错误信息。 |

### 1.4 访问内部接口

访问Auto Engine平台内部任意接口

| 方法                                                      | 描述           |
| :-------------------------------------------------------- | :------------- |
| `platform_url(url: str, method: str, params: Ant) -> Any` | 调用内部接口。 |

**示例:**

```python
from minzhi import AEClient

# 实例化AEClient对象
ae_client = AEClient(businessId="业务ID", table_name="表名")

# 调用内部接口
body = ae_client.platform_url(
       url="http://low-code-web/logic/platform/createDnsResolutionRecords/generateOfflineChangeOrder",
       method="POST",
       params={"flowNo": "123123123"}
    )
```

### 1.5 获取脚本/接口入参

 `AEClient` 对象中的  `res` 方法，用于获取脚本/接口入参。

| 方法          | 描述                    |
| :------------ | :---------------------- |
| `res -> Dict` | 用于获取脚本/接口入参。 |

**示例:**

```python
from minzhi import AEClient

# 实例化AEClient对象
ae_client = AEClient(businessId="业务ID", table_name="表名")

# 获取脚本/接口入参
参数值 = ae_client.res.get("参数名称")
```

### 

---

## 2. CmdbClient (CMDB 客户端)

`CmdbClient` 提供与 CMDB 交互的高级功能，支持复杂的查询构建和批量导入。

**引用方式:**
```python
from minzhi import CmdbClient, QueryBuilder, QueryOperation
```

**初始化:**

```python
client = CmdbClient(
    view_id="视图ID",
    CMDB_SERVER="https://cmdb.example.com",
    APPID="应用ID",
    APPSECRET="应用密钥"
)
```

### 2.1 数据查询

#### 核心方法: `get_all_data`
```python
def get_all_data(
    startPage: int = 1,
    pageSize: int = 1000,
    queryKey: Optional[Union[Dict, List]] = None
) -> List[Dict]
```
获取所有符合条件的数据（自动翻页）。

#### 查询条件构建 (`QueryBuilder`)
推荐使用 `QueryBuilder` 构建 `queryKey`。

| 方法 | 描述 |
| :--- | :--- |
| `equal(key, value)` | 等于 |
| `like(key, value)` | 模糊匹配 |
| `greater_than(key, value)` | 大于 |
| `less_than(key, value)` | 小于 |
| `not_equal(key, value)` | 不等于 |
| `in_condition(key, value)` | 包含 (IN) |

**示例:**
```python
query = (QueryBuilder()
         .equal("status", "running")
         .like("hostname", "web-%")
         .build())

servers = client.get_all_data(queryKey=query)
```

### 2.2 数据导入

| 方法 | 描述 |
| :--- | :--- |
| `import_data(data: List[Dict]) -> Dict` | 单次批量导入数据。 |
| `thread_import_data(data: List[Dict], batch_size=100) -> bool` | 多线程分批导入数据，适合大数据量。具备重试机制。 |
