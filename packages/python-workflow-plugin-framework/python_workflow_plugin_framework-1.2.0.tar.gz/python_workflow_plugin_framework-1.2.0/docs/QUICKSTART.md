# Python Workflow Plugin Framework - 快速入门

5 分钟创建你的第一个插件！

## 步骤 1: 准备环境

```bash
# 安装框架
pip install python-workflow-plugin-framework

# 确保 protobuf 文件已生成
# (通常在项目根目录运行 make proto)
```

## 步骤 2: 创建插件文件

创建 `my_first_plugin.py`:

```python
#!/usr/bin/env python3
import sys
from typing import Dict, Any, Iterator
from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin

class MyFirstPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyFirstPlugin")
    
    def get_plugin_metadata(self) -> Dict[str, Any]:
        return {
            "kind": "my_first_plugin",
            "node_type": "Node",
            "description": "My first plugin using the framework",
            "version": "1.0.0",
            "parameters": [
                {
                    "name": "message",
                    "type": "string",
                    "description": "Message to process",
                    "required": True,
                    "default_value": "Hello World"
                }
            ]
        }
    
    def execute(self, parameters, parent_output, global_vars, context):
        message = parameters.get("message", "")
        
        yield {"type": "log", "message": f"📝 Processing: {message}"}
        
        result = f"Processed: {message.upper()}"
        
        yield {
            "type": "result",
            "data": {
                "result": result,
                "original": message
            }
        }

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    serve_plugin(MyFirstPlugin(), port)
```

## 步骤 3: 运行插件

```bash
chmod +x my_first_plugin.py
python my_first_plugin.py 50052
```

你应该看到：

```
============================================================
🚀 MyFirstPlugin
============================================================
📦 Version: 1.0.0
🔗 Port: 50052
📝 Description: My first plugin using the framework
📊 Log level: INFO
============================================================
✅ Server started successfully!
📝 Press Ctrl+C to stop...
============================================================
```

## 步骤 4: 测试插件

使用 grpcurl 测试：

```bash
# 获取元数据
grpcurl -plaintext localhost:50052 node_plugin.NodePluginService/GetMetadata

# 健康检查
grpcurl -plaintext localhost:50052 node_plugin.NodePluginService/HealthCheck
```

## 步骤 5: 在工作流中使用

创建工作流配置 `my_workflow.yaml`:

```yaml
name: test_my_plugin
nodes:
  - name: my_node
    type: my_first_plugin
    parameters:
      message: "Hello from workflow!"
```

## 下一步

### 添加更多参数

```python
def get_plugin_metadata(self):
    return {
        # ...
        "parameters": [
            {
                "name": "message",
                "type": "string",
                "description": "Input message",
                "required": True,
                "default_value": ""
            },
            {
                "name": "repeat",
                "type": "int",
                "description": "Number of times to repeat",
                "required": False,
                "default_value": "1"
            },
            {
                "name": "uppercase",
                "type": "string",
                "description": "Convert to uppercase",
                "required": False,
                "default_value": "true"
            }
        ]
    }
```

### 添加错误处理

```python
def execute(self, parameters, parent_output, global_vars, context):
    message = parameters.get("message", "")
    
    if not message:
        yield {"type": "error", "message": "Message cannot be empty"}
        return
    
    try:
        repeat = int(parameters.get("repeat", 1))
        if repeat < 1 or repeat > 100:
            yield {"type": "error", "message": "Repeat must be between 1 and 100"}
            return
    except ValueError:
        yield {"type": "error", "message": "Repeat must be a number"}
        return
    
    # 处理逻辑...
```

### 添加进度反馈

```python
def execute(self, parameters, parent_output, global_vars, context):
    items = parameters.get("items", [])
    total = len(items)
    
    for i, item in enumerate(items):
        progress = (i + 1) / total * 100
        yield {"type": "log", "message": f"Progress: {progress:.1f}%"}
        
        # 处理 item
        result = self._process_item(item)
    
    yield {"type": "result", "data": {"processed": total}}
```

### 添加健康检查

```python
def health_check(self) -> tuple[bool, str]:
    try:
        # 检查依赖服务
        response = requests.get("http://my-service/health", timeout=2)
        if response.status_code == 200:
            return True, "✅ Service is healthy"
        return False, f"⚠️ Service returned {response.status_code}"
    except Exception as e:
        return False, f"❌ Health check failed: {e}"
```

## 常见模式

### 1. 调用外部 API

```python
def execute(self, parameters, parent_output, global_vars, context):
    import requests
    
    url = parameters.get("url")
    yield {"type": "log", "message": f"Calling API: {url}"}
    
    response = requests.get(url)
    
    yield {
        "type": "result",
        "data": {
            "status": response.status_code,
            "body": response.json()
        }
    }
```

### 2. 文件处理

```python
def execute(self, parameters, parent_output, global_vars, context):
    file_path = parameters.get("file_path")
    
    yield {"type": "log", "message": f"Reading file: {file_path}"}
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    yield {
        "type": "result",
        "data": {
            "content": content,
            "size": len(content)
        }
    }
```

### 3. 数据转换

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 从父节点获取数据
    input_data = parent_output.get("data", [])
    
    yield {"type": "log", "message": f"Transforming {len(input_data)} items"}
    
    # 转换数据
    output_data = [self._transform(item) for item in input_data]
    
    yield {
        "type": "result",
        "data": {
            "transformed": output_data,
            "count": len(output_data)
        }
    }
```

## 示例插件

查看这些完整示例：

1. **example_plugin.py** - 文本处理
2. **http_api_plugin.py** - HTTP API 调用
3. **langchain_ollama_plugin.py** - LLM 集成

## 调试技巧

### 启用详细日志

```python
class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
        self.logger.setLevel(logging.DEBUG)
```

### 打印所有参数

```python
def execute(self, parameters, parent_output, global_vars, context):
    self.logger.debug(f"Parameters: {parameters}")
    self.logger.debug(f"Parent output: {parent_output}")
    self.logger.debug(f"Global vars: {global_vars}")
    self.logger.debug(f"Context: {context}")
```

### 使用 try-except

```python
def execute(self, parameters, parent_output, global_vars, context):
    try:
        # 你的代码
        pass
    except Exception as e:
        self.logger.error(f"Error: {e}", exc_info=True)
        yield {"type": "error", "message": str(e)}
```

## 获取帮助

- 查看 `README.md` 了解完整文档
- 查看示例插件了解最佳实践
- 检查日志输出进行调试

祝你开发愉快！🚀
