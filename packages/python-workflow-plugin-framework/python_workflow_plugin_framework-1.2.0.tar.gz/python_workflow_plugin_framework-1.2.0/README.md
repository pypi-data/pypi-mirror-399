# Python Workflow Plugin Framework

一个简化 Python 工作流插件开发的通用框架，让你专注于业务逻辑而不是 gRPC 样板代码。

## 项目链接

- **GitHub**: [https://github.com/mytoolzone/python-workflow-plugin-framework](https://github.com/mytoolzone/python-workflow-plugin-framework)
- **PyPI**: [https://pypi.org/project/python-workflow-plugin-framework](https://pypi.org/project/python-workflow-plugin-framework)

## 特性

- ✅ **简单易用**：只需实现 2 个核心方法即可创建插件
- 🔄 **自动处理**：gRPC 通信、日志、错误处理、上下文提取
- 📊 **内置追踪**：自动提取 W3C Trace Context 和自定义 metadata
- 🎯 **类型安全**：完整的类型提示支持
- 📝 **Go glog 兼容**：使用 glog-python，与 Go 服务日志格式一致
- 🔌 **可扩展**：提供多个可选的钩子方法

## 快速开始

### 1. 创建你的插件

```python
#!/usr/bin/env python3
from typing import Dict, Any, Iterator
from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin

class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
    
    def get_plugin_metadata(self) -> Dict[str, Any]:
        """定义插件元数据和参数"""
        return {
            "kind": "my_plugin",
            "node_type": "Node",
            "description": "My awesome plugin",
            "version": "1.0.0",
            "parameters": [
                {
                    "name": "input_text",
                    "type": "string",
                    "description": "Input text",
                    "required": True,
                    "default_value": ""
                }
            ]
        }
    
    def execute(
        self,
        parameters: Dict[str, Any],
        parent_output: Dict[str, Any],
        global_vars: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """执行插件逻辑"""
        
        # 获取参数
        text = parameters.get("input_text", "")
        
        # 发送日志
        yield {"type": "log", "message": f"Processing: {text}"}
        
        # 执行业务逻辑
        result = text.upper()
        
        # 返回结果
        yield {
            "type": "result",
            "data": {
                "output": result,
                "length": len(result)
            }
        }

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    plugin = MyPlugin()
    serve_plugin(plugin, port)
```

### 2. 运行插件

```bash
python my_plugin.py 50052
```

## 核心概念

### 必须实现的方法

#### 1. `get_plugin_metadata()` 

定义插件的元数据和参数：

```python
def get_plugin_metadata(self) -> Dict[str, Any]:
    return {
        "kind": "plugin_type",           # 插件类型标识
        "node_type": "Node",             # 节点类型
        "description": "Plugin desc",    # 描述
        "version": "1.0.0",              # 版本号
        "credential_type": "",           # 可选：凭证类型
        "parameters": [                  # 参数定义
            {
                "name": "param_name",
                "type": "string",        # string, int, double, bool
                "description": "Param description",
                "required": True,
                "default_value": "default"
            }
        ]
    }
```

#### 2. `execute()`

执行插件的核心逻辑（生成器函数）：

```python
def execute(
    self,
    parameters: Dict[str, Any],      # 节点参数
    parent_output: Dict[str, Any],   # 父节点输出
    global_vars: Dict[str, Any],     # 全局变量
    context: Dict[str, Any]          # 上下文（trace_id, node_name 等）
) -> Iterator[Dict[str, Any]]:
    
    # 发送日志消息
    yield {"type": "log", "message": "Processing..."}
    
    # 返回结果
    yield {
        "type": "result",
        "data": {"key": "value"},
        "branch_index": 0  # 可选，默认 0
    }
    
    # 或返回错误
    yield {"type": "error", "message": "Something went wrong"}
```

### 可选方法（可以覆盖）

#### 1. `health_check()`

自定义健康检查：

```python
def health_check(self) -> tuple[bool, str]:
    try:
        # 检查依赖服务
        # ...
        return True, "✅ Service is healthy"
    except Exception as e:
        return False, f"❌ Health check failed: {e}"
```

#### 2. `test_credentials()`

测试凭证有效性：

```python
def test_credentials(self, credentials: Dict[str, Any]) -> tuple[bool, str]:
    api_key = credentials.get("api_key")
    if self._validate_api_key(api_key):
        return True, "✅ Credentials valid"
    return False, "❌ Invalid API key"
```

#### 3. `on_init()`

初始化回调：

```python
def on_init(self, node_config: Dict[str, Any], workflow_entity: Optional[Dict[str, Any]]):
    # 初始化资源、连接等
    self.db_connection = self._connect_to_db()
```

## 上下文信息

`execute()` 方法的 `context` 参数包含：

```python
{
    "trace_id": "...",              # W3C Trace ID
    "span_id": "...",               # W3C Span ID
    "node_name": "...",             # 节点名称
    "node_type": "...",             # 节点类型
    "workflow_name": "...",         # 工作流名称
    "workflow_instance_id": "..."   # 工作流实例 ID
}
```

## 输出类型

### 日志消息

```python
yield {"type": "log", "message": "Processing data..."}
```

### 结果

```python
yield {
    "type": "result",
    "data": {
        "result": "output data",
        "metadata": {...}
    },
    "branch_index": 0  # 可选
}
```

### 错误

```python
yield {"type": "error", "message": "Error description"}
```

## 完整示例

查看以下示例：

1. **example_plugin.py** - 简单的文本处理插件
2. **langchain_ollama_plugin.py** - LangChain + Ollama 集成
3. **demo.py** - 插件演示脚本，展示所有自定义插件的功能

## 自定义插件

框架包含以下四个自定义插件，位于 `my_plugins/` 目录：

### 1. LangChain Memory Plugin
- **功能**：LangChain 记忆组件集成
- **类型**：`langchain_memory_python`
- **支持的记忆类型**：buffer、summary、window

### 2. Mobile ADB Plugin  
- **功能**：移动设备 ADB 控制
- **类型**：`mobile_adb_python`
- **支持的操作**：click、swipe、input_text、screenshot

### 3. Desktop Screenshot Plugin
- **功能**：桌面截图功能
- **类型**：`desktop_screenshot_python`
- **支持的操作**：fullscreen、region、delay

### 4. Playwright Browser Plugin
- **功能**：Playwright 浏览器自动化
- **类型**：`playwright_browser_python`
- **支持的操作**：navigate、click、fill、screenshot、extract_text

## 项目结构

```
plugins/python-plugin-framework/
├── base_plugin.py                 # 框架核心
├── example_plugin.py              # 示例插件
├── langchain_ollama_plugin.py     # LangChain 插件
├── demo.py                        # 插件演示脚本
├── test_framework.py              # 测试框架
├── README.md                      # 本文档
├── requirements.txt               # 基础依赖
├── config/
│   └── plugins.yaml               # 插件配置文件
└── my_plugins/                    # 自定义插件目录
    ├── langchain_memory/          # LangChain Memory 插件
    ├── mobile_adb/               # Mobile ADB 插件
    ├── desktop_screenshot/        # Desktop Screenshot 插件
    └── playwright_browser/        # Playwright Browser 插件
        ├── *.py                   # 插件代码
        ├── Makefile               # 构建脚本
        ├── requirements.txt       # 插件依赖
        └── test_*.py              # 测试文件
```

## 依赖

基础框架依赖：

```txt
grpcio>=1.60.0
grpcio-reflection>=1.60.0
protobuf>=4.25.0
glog-python==1.0.0  # Go glog 兼容的日志库
```

将你的插件特定依赖添加到自己的 `requirements.txt`。

## 日志系统

框架使用 `glog-python`，与 Go glog 格式完全兼容：

```python
# 简单日志
self.logger.info("Processing started")

# 格式化日志
self.logger.infof("Processing %d items", count)

# 带 trace_id 的日志
logger = self.logger.with_field(trace_id, "")
logger.info("Request completed")

# 错误日志
self.logger.with_error(e).error("Processing failed")
```

**日志格式：**
```
[2025-11-15 17:10:29.461] [info] [PluginName] file.py:10 [trace_id] [Node name] Message
```

详见 [GLOG_USAGE.md](GLOG_USAGE.md)

## 最佳实践

### 1. 参数验证

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 验证必需参数
    if not parameters.get("required_param"):
        yield {"type": "error", "message": "Missing required_param"}
        return
    
    # 验证参数类型
    try:
        value = int(parameters.get("number_param"))
    except ValueError:
        yield {"type": "error", "message": "number_param must be an integer"}
        return
```

### 2. 错误处理

```python
def execute(self, parameters, parent_output, global_vars, context):
    try:
        # 业务逻辑
        result = self._process_data(parameters)
        yield {"type": "result", "data": result}
    except ValueError as e:
        yield {"type": "error", "message": f"Invalid input: {e}"}
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        yield {"type": "error", "message": f"Processing failed: {e}"}
```

### 3. 进度反馈

```python
def execute(self, parameters, parent_output, global_vars, context):
    items = parameters.get("items", [])
    total = len(items)
    
    for i, item in enumerate(items):
        yield {"type": "log", "message": f"Processing {i+1}/{total}..."}
        # 处理 item
    
    yield {"type": "result", "data": {"processed": total}}
```

### 4. 流式输出

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 适合长时间运行的任务
    for chunk in self._stream_process(parameters):
        yield {"type": "log", "message": f"Chunk: {chunk}"}
    
    yield {"type": "result", "data": {"status": "completed"}}
```

## 调试

启用详细日志：

```python
import logging

class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
        self.logger.setLevel(logging.DEBUG)  # 启用 DEBUG 日志
```

## 常见问题

### Q: 如何访问父节点的输出？

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 父节点的输出在 parent_output 中
    previous_result = parent_output.get("result")
    yield {"type": "log", "message": f"Previous: {previous_result}"}
```

### Q: 如何使用全局变量？

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 全局变量在 global_vars 中
    api_key = global_vars.get("api_key")
    base_url = global_vars.get("base_url")
```

### Q: 如何返回多个分支？

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 分支 0
    yield {
        "type": "result",
        "data": {"branch": "success"},
        "branch_index": 0
    }
    
    # 分支 1
    yield {
        "type": "result",
        "data": {"branch": "alternative"},
        "branch_index": 1
    }
```

## 测试

每个插件都包含完整的单元测试和 Mock 测试。

### 运行所有测试

```bash
# 运行所有插件的测试
python3 demo.py --tests
```

### 运行单个插件的测试

```bash
# 运行 LangChain Memory 插件测试
python3 my_plugins/langchain_memory/test_langchain_memory_plugin.py

# 运行 Mobile ADB 插件测试  
python3 my_plugins/mobile_adb/test_mobile_adb_plugin.py

# 运行 Desktop Screenshot 插件测试
python3 my_plugins/desktop_screenshot/test_desktop_screenshot_plugin.py

# 运行 Playwright Browser 插件测试
python3 my_plugins/playwright_browser/test_playwright_browser_plugin.py
```

### 测试方法

测试使用 Python `unittest` 框架和 `unittest.mock` 进行 Mock 测试：

- **单元测试**：测试插件的核心功能
- **Mock 测试**：模拟外部依赖（如 ADB、浏览器、记忆组件）
- **健康检查测试**：测试插件的健康状态检查

## 演示

运行演示脚本，展示所有插件的基本功能：

```bash
# 运行插件演示
python3 demo.py --demo

# 运行演示和测试
python3 demo.py --all
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

MIT
