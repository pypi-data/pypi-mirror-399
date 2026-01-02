# Python Workflow Plugin Framework - 架构设计

## 概述

Python Workflow Plugin Framework 是一个轻量级的插件开发框架，旨在简化基于 gRPC 的插件开发流程。

## 设计目标

1. **简单易用** - 开发者只需关注业务逻辑
2. **类型安全** - 完整的类型提示支持
3. **可扩展** - 提供多个扩展点
4. **标准化** - 统一的接口和约定
5. **可观测** - 内置日志和追踪支持

## 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Your Plugin                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  get_plugin_metadata()                            │  │
│  │  execute()                                        │  │
│  │  health_check() [optional]                        │  │
│  │  test_credentials() [optional]                    │  │
│  │  on_init() [optional]                             │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │         BasePluginService (Framework)             │  │
│  │  • gRPC 服务实现                                   │  │
│  │  • 参数解析                                        │  │
│  │  • 错误处理                                        │  │
│  │  • 日志管理                                        │  │
│  │  • 上下文提取                                      │  │
│  └───────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │              gRPC Server                          │  │
│  │  • NodePluginService                              │  │
│  │  • Reflection API                                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────────┐
│              Workflow Engine (Go)                       │
│  • 调用插件                                             │
│  • 传递参数                                             │
│  • 处理结果                                             │
└─────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. BasePluginService

基础插件服务类，提供：

- **gRPC 服务实现**
  - `GetMetadata()` - 获取插件元数据
  - `Init()` - 初始化插件
  - `Run()` - 执行插件（流式）
  - `TestSecret()` - 测试凭证
  - `HealthCheck()` - 健康检查

- **辅助功能**
  - Protobuf 类型转换
  - 上下文信息提取
  - 日志管理
  - 错误处理

### 2. 抽象方法

子类必须实现：

```python
@abstractmethod
def get_plugin_metadata(self) -> Dict[str, Any]:
    """返回插件元数据"""
    pass

@abstractmethod
def execute(
    self,
    parameters: Dict[str, Any],
    parent_output: Dict[str, Any],
    global_vars: Dict[str, Any],
    context: Dict[str, Any]
) -> Iterator[Dict[str, Any]]:
    """执行插件逻辑"""
    pass
```

### 3. 可选钩子

子类可以覆盖：

```python
def health_check(self) -> tuple[bool, str]:
    """自定义健康检查"""
    pass

def test_credentials(self, credentials: Dict[str, Any]) -> tuple[bool, str]:
    """验证凭证"""
    pass

def on_init(self, node_config: Dict[str, Any], workflow_entity: Dict[str, Any]):
    """初始化回调"""
    pass
```

## 数据流

### 1. 初始化流程

```
Workflow Engine
    ↓ Init(node_json, workflow_entity_json)
BasePluginService.Init()
    ↓ 解析 JSON
    ↓ 调用 on_init()
Your Plugin.on_init()
    ↓ 初始化资源
    ↓ 返回 InitResponse
Workflow Engine
```

### 2. 执行流程

```
Workflow Engine
    ↓ Run(parameters, parent_output, global_vars)
BasePluginService.Run()
    ↓ 提取上下文
    ↓ 转换参数
    ↓ 调用 execute()
Your Plugin.execute()
    ↓ yield {"type": "log", ...}
    ↓ yield {"type": "result", ...}
BasePluginService.Run()
    ↓ 转换为 RunResponse
    ↓ 流式返回
Workflow Engine
```

### 3. 输出类型

```python
# 日志消息
{"type": "log", "message": "Processing..."}
    ↓
RunResponse(type=LOG, log_message="Processing...")

# 结果
{"type": "result", "data": {...}, "branch_index": 0}
    ↓
RunResponse(type=RESULT, result_json="{...}", branch_index=0)

# 错误
{"type": "error", "message": "Error occurred"}
    ↓
RunResponse(type=ERROR, error="Error occurred")
```

## 上下文传递

### gRPC Metadata → Context Dict

```
gRPC Metadata:
  traceparent: 00-trace_id-span_id-00
  x-node-name: my_node
  x-workflow-name: my_workflow
  x-trace-id: custom_trace_id

    ↓ _extract_context()

Context Dict:
{
  "trace_id": "trace_id",
  "span_id": "span_id",
  "node_name": "my_node",
  "workflow_name": "my_workflow",
  ...
}
```

## 类型转换

### Protobuf Value → Python

```
protobuf Value {
  string_value: "hello"
}
    ↓ _convert_proto_value_to_python()
Python: "hello"

protobuf Value {
  map_value: {
    "key": {string_value: "value"}
  }
}
    ↓ _convert_proto_value_to_python()
Python: {"key": "value"}
```

## 错误处理策略

### 1. 参数验证错误

```python
if not parameters.get("required_param"):
    yield {"type": "error", "message": "Missing required_param"}
    return
```

### 2. 业务逻辑错误

```python
try:
    result = self._process_data(parameters)
    yield {"type": "result", "data": result}
except ValueError as e:
    yield {"type": "error", "message": f"Invalid input: {e}"}
```

### 3. 系统错误

```python
try:
    # 插件执行
    for output in self.execute(...):
        yield output
except Exception as e:
    logger.error(f"Execution failed: {e}")
    yield RunResponse(type=ERROR, error=str(e))
```

## 日志层次

```
DEBUG   - 详细的调试信息
INFO    - 一般信息（默认）
WARNING - 警告信息
ERROR   - 错误信息
```

## 扩展点

### 1. 自定义日志格式

```python
class MyPlugin(BasePluginService):
    def _setup_logger(self):
        logger = super()._setup_logger()
        # 自定义日志格式
        return logger
```

### 2. 自定义初始化

```python
def on_init(self, node_config, workflow_entity):
    self.db = self._connect_to_database()
    self.cache = self._init_cache()
```

### 3. 自定义健康检查

```python
def health_check(self):
    if not self.db.is_connected():
        return False, "Database not connected"
    return True, "All systems operational"
```

## 性能考虑

### 1. 流式输出

使用生成器避免内存占用：

```python
def execute(self, ...):
    for item in large_dataset:
        yield {"type": "log", "message": f"Processing {item}"}
        # 处理 item
```

### 2. 连接复用

在 `on_init()` 中初始化连接：

```python
def on_init(self, node_config, workflow_entity):
    self.session = requests.Session()  # 复用 HTTP 连接
```

### 3. 资源清理

虽然框架没有显式的清理钩子，但可以使用上下文管理器：

```python
def execute(self, ...):
    with self._get_resource() as resource:
        # 使用 resource
        pass
```

## 安全考虑

### 1. 参数验证

始终验证输入参数：

```python
def execute(self, parameters, ...):
    url = parameters.get("url")
    if not self._is_valid_url(url):
        yield {"type": "error", "message": "Invalid URL"}
        return
```

### 2. 凭证处理

不要在日志中打印敏感信息：

```python
def test_credentials(self, credentials):
    api_key = credentials.get("api_key")
    # ❌ self.logger.info(f"Testing key: {api_key}")
    # ✅ self.logger.info("Testing API key...")
```

### 3. 错误信息

不要暴露内部实现细节：

```python
except Exception as e:
    # ❌ yield {"type": "error", "message": str(e)}
    # ✅ yield {"type": "error", "message": "Processing failed"}
    self.logger.error(f"Internal error: {e}")
```

## 测试策略

### 1. 单元测试

测试单个方法：

```python
def test_metadata():
    plugin = MyPlugin()
    metadata = plugin.get_plugin_metadata()
    assert metadata["kind"] == "my_plugin"
```

### 2. 集成测试

测试完整流程：

```python
def test_execute():
    plugin = MyPlugin()
    results = list(plugin.execute(params, {}, {}, context))
    assert any(r["type"] == "result" for r in results)
```

### 3. 端到端测试

使用 grpcurl 或工作流引擎测试。

## 最佳实践

1. **保持简单** - 一个插件做一件事
2. **提供反馈** - 使用日志消息报告进度
3. **处理错误** - 优雅地处理所有错误情况
4. **文档化** - 清晰的参数描述
5. **可测试** - 编写单元测试
6. **可观测** - 添加适当的日志

## 未来改进

- [ ] 异步支持（async/await）
- [ ] 插件生命周期管理
- [ ] 内置指标收集
- [ ] 配置验证
- [ ] 插件热重载
