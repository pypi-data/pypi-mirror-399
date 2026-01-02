# 开始使用 Python Workflow Plugin Framework

欢迎使用 Python Plugin Framework！这个 5 分钟指南将帮助你快速上手。

## 🎯 你将学到

- ✅ 安装框架
- ✅ 运行第一个插件
- ✅ 创建自己的插件
- ✅ 测试和调试

## 📋 前置要求

- Python 3.8+
- pip
- 基础的 Python 知识

## 🚀 第一步：安装

```bash
# 使用 pip 安装框架
pip install python-workflow-plugin-framework
```

**预期输出：**
```
Successfully installed grpcio-1.60.0 grpcio-reflection-1.60.0 protobuf-4.25.0
```

## 🎮 第二步：运行示例

```bash
# 运行简单示例
python example_plugin.py 50052
```

**预期输出：**
```
============================================================
🚀 TextProcessor
============================================================
📦 Version: 1.0.0
🔗 Port: 50052
📝 Description: Simple text processing plugin
============================================================
✅ Server started successfully!
📝 Press Ctrl+C to stop...
============================================================
```

**恭喜！** 你的第一个插件已经运行了！

## 📝 第三步：创建你的插件

创建文件 `my_plugin.py`：

```python
#!/usr/bin/env python3
"""我的第一个插件"""

import sys
from typing import Dict, Any, Iterator
from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin


class MyFirstPlugin(BasePluginService):
    """我的第一个插件"""

    def __init__(self):
        super().__init__(plugin_name="MyFirstPlugin")

    def get_plugin_metadata(self) -> Dict[str, Any]:
        """定义插件信息"""
        return {
            "kind": "my_first_plugin",
            "node_type": "Node",
            "description": "这是我的第一个插件",
            "version": "1.0.0",
            "parameters": [
                {
                    "name": "message",
                    "type": "string",
                    "description": "要处理的消息",
                    "required": True,
                    "default_value": "Hello World"
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
        
        # 1. 获取参数
        message = parameters.get("message", "")
        
        # 2. 发送日志
        yield {"type": "log", "message": f"📝 收到消息: {message}"}
        
        # 3. 处理数据
        result = message.upper()
        
        # 4. 再发送一条日志
        yield {"type": "log", "message": f"✅ 处理完成"}
        
        # 5. 返回结果
        yield {
            "type": "result",
            "data": {
                "result": result,
                "original": message,
                "length": len(result)
            }
        }


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    plugin = MyFirstPlugin()
    serve_plugin(plugin, port)
```

## 🏃 第四步：运行你的插件

```bash
python my_plugin.py 50052
```

**预期输出：**
```
============================================================
🚀 MyFirstPlugin
============================================================
📦 Version: 1.0.0
🔗 Port: 50052
📝 Description: 这是我的第一个插件
============================================================
✅ Server started successfully!
============================================================
```

## 🧪 第五步：测试插件

### 方法 1：使用测试脚本

创建 `test_my_plugin.py`：

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from my_plugin import MyFirstPlugin

# 创建插件实例
plugin = MyFirstPlugin()

# 测试元数据
metadata = plugin.get_plugin_metadata()
print(f"插件类型: {metadata['kind']}")
print(f"插件版本: {metadata['version']}")

# 测试执行
parameters = {"message": "hello world"}
context = {"trace_id": "test-123", "node_name": "test"}

print("\n执行插件:")
for output in plugin.execute(parameters, {}, {}, context):
    print(f"  {output}")

print("\n✅ 测试完成!")
```

运行测试：

```bash
python test_my_plugin.py
```

### 方法 2：使用 grpcurl（需要 protobuf）

```bash
# 健康检查
grpcurl -plaintext localhost:50052 node_plugin.NodePluginService/HealthCheck

# 获取元数据
grpcurl -plaintext localhost:50052 node_plugin.NodePluginService/GetMetadata
```

## 📚 下一步学习

### 初学者路径

1. ✅ 你已经完成了基础教程！
2. 📖 阅读 [README.md](README.md) 了解更多特性
3. 👀 查看 [http_api_plugin.py](http_api_plugin.py) 学习更复杂的示例
4. 🎓 阅读 [最佳实践](#最佳实践)

### 进阶路径

1. 📖 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 理解框架设计
2. 🔧 实现自定义健康检查
3. 🔐 实现凭证验证
4. 🌊 实现流式输出

## 💡 最佳实践

### 1. 参数验证

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 验证必需参数
    message = parameters.get("message")
    if not message:
        yield {"type": "error", "message": "message 参数不能为空"}
        return
    
    # 继续处理...
```

### 2. 错误处理

```python
def execute(self, parameters, parent_output, global_vars, context):
    try:
        # 你的代码
        result = self._process(parameters)
        yield {"type": "result", "data": result}
    except ValueError as e:
        yield {"type": "error", "message": f"参数错误: {e}"}
    except Exception as e:
        self.logger.error(f"处理失败: {e}")
        yield {"type": "error", "message": "处理失败"}
```

### 3. 进度反馈

```python
def execute(self, parameters, parent_output, global_vars, context):
    items = parameters.get("items", [])
    total = len(items)
    
    for i, item in enumerate(items):
        # 报告进度
        yield {"type": "log", "message": f"处理中 {i+1}/{total}..."}
        
        # 处理 item
        self._process_item(item)
    
    yield {"type": "result", "data": {"processed": total}}
```

### 4. 使用上下文

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 获取追踪信息
    trace_id = context.get("trace_id")
    node_name = context.get("node_name")
    
    self.logger.info(f"节点 {node_name} 开始执行 (trace: {trace_id})")
    
    # 你的逻辑...
```

## 🐛 常见问题

### Q: 插件启动失败

**问题：** `ModuleNotFoundError: No module named 'base_plugin'`

**解决：**
```bash
# 确保在正确的目录
cd plugins/python-plugin-framework

# 或者设置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Q: 端口被占用

**问题：** `Address already in use`

**解决：**
```bash
# 使用不同的端口
python my_plugin.py 50053

# 或者查找并关闭占用端口的进程
lsof -i :50052
kill <PID>
```

### Q: 如何调试？

**解决：**
```python
class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
        # 启用 DEBUG 日志
        self.logger.setLevel(logging.DEBUG)
    
    def execute(self, parameters, parent_output, global_vars, context):
        # 打印所有参数
        self.logger.debug(f"Parameters: {parameters}")
        self.logger.debug(f"Context: {context}")
        # ...
```

## 🎓 学习资源

### 文档

- [README.md](README.md) - 完整 API 文档
- [QUICKSTART.md](QUICKSTART.md) - 快速入门
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - 迁移指南

### 示例

- [example_plugin.py](example_plugin.py) - 简单示例
- [http_api_plugin.py](http_api_plugin.py) - HTTP API
- [langchain_ollama_plugin.py](langchain_ollama_plugin.py) - LLM 集成

### 工具

- [test_framework.py](test_framework.py) - 测试套件
- [Makefile](Makefile) - 便捷命令

## 🎉 完成！

恭喜你完成了入门教程！你现在可以：

- ✅ 创建基础插件
- ✅ 处理参数
- ✅ 返回结果
- ✅ 处理错误
- ✅ 测试插件

**继续探索：**

1. 尝试添加更多参数
2. 实现健康检查
3. 添加流式输出
4. 集成外部 API

**需要帮助？**

- 查看文档
- 查看示例代码
- 运行测试了解框架行为

祝你开发愉快！🚀
