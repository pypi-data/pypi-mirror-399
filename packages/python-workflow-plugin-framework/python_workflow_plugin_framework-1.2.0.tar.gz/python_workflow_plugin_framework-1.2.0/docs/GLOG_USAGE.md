# glog-python 使用指南

本框架使用 `glog-python==1.0.0`，这是一个与 Go glog 兼容的 Python 日志库。

## 日志格式

### Console 格式（默认）

```
[2025-11-15 17:10:29.461] [info] [PluginName] base_plugin.py:202 [trace_id] [Node my_node] 🚀 Initializing model
```

格式说明：
- `[时间戳]` - 精确到毫秒
- `[日志级别]` - debug/info/warn/error
- `[Logger名称]` - 插件名称
- `文件名:行号` - 自动获取
- `[字段1] [字段2]` - 通过 with_field() 添加
- `消息内容` - 实际日志

## 基础使用

### 1. 简单日志

```python
# 在插件中使用 self.logger
self.logger.info("Application started")
self.logger.warn("High memory usage")
self.logger.error("Connection failed")
```

### 2. 格式化日志

```python
# 使用 %s, %d, %f 等格式化
self.logger.infof("User %s logged in", username)
self.logger.debugf("Processing %d items", count)
self.logger.errorf("Failed after %d attempts", retry_count)
```

### 3. 带字段的日志

```python
# 添加 trace_id
logger_with_trace = self.logger.with_field(trace_id, "")
logger_with_trace.info("Processing request")

# 添加多个字段
logger_with_fields = self.logger \
    .with_field(trace_id, "") \
    .with_field(f"Node {node_name}", "")
logger_with_fields.info("Request completed")
```

### 4. 错误日志

```python
try:
    result = process_data()
except Exception as e:
    # 自动包含错误堆栈
    self.logger.with_error(e).error("Processing failed")
```

## 在插件中使用

### 基础插件示例

```python
from base_plugin import BasePluginService, serve_plugin

class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
        # self.logger 已经配置好了
    
    def execute(self, parameters, parent_output, global_vars, context):
        # 简单日志
        self.logger.info("Starting execution")
        
        # 格式化日志
        value = parameters.get("value")
        self.logger.infof("Processing value: %s", value)
        
        # 带 trace_id 的日志
        trace_id = context.get("trace_id")
        logger = self.logger.with_field(trace_id, "")
        logger.info("Processing with trace")
        
        yield {"type": "result", "data": {...}}
```

### 带上下文的日志

```python
def execute(self, parameters, parent_output, global_vars, context):
    # 提取上下文信息
    trace_id = context.get("trace_id", "unknown")
    node_name = context.get("node_name", "unknown")
    
    # 创建带上下文的 logger
    ctx_logger = self.logger \
        .with_field(trace_id, "") \
        .with_field(f"Node {node_name}", "")
    
    # 所有日志都会包含这些字段
    ctx_logger.info("🚀 Starting processing")
    ctx_logger.infof("📥 Received %d parameters", len(parameters))
    
    try:
        result = self._process(parameters)
        ctx_logger.info("✅ Processing completed")
        yield {"type": "result", "data": result}
    except Exception as e:
        ctx_logger.with_error(e).error("❌ Processing failed")
        yield {"type": "error", "message": str(e)}
```

### 进度日志

```python
def execute(self, parameters, parent_output, global_vars, context):
    items = parameters.get("items", [])
    total = len(items)
    
    logger = self.logger.with_field(context.get("trace_id"), "")
    
    for i, item in enumerate(items):
        # 报告进度
        logger.infof("Processing %d/%d...", i+1, total)
        
        # 处理 item
        self._process_item(item)
    
    logger.infof("✅ Completed processing %d items", total)
    yield {"type": "result", "data": {"processed": total}}
```

## 日志级别

```python
# DEBUG - 详细调试信息
self.logger.debug("Detailed debug info")
self.logger.debugf("Value: %s", value)

# INFO - 一般信息（默认）
self.logger.info("Application started")
self.logger.infof("User %s logged in", user)

# WARN - 警告信息
self.logger.warn("High memory usage")
self.logger.warnf("Retry attempt %d", attempt)

# ERROR - 错误信息
self.logger.error("Connection failed")
self.logger.errorf("Failed after %d retries", max_retries)
```

## 高级用法

### 1. 多个字段

```python
logger = self.logger \
    .with_field(trace_id, "") \
    .with_field(f"User {user_id}", "") \
    .with_field(f"Request {request_id}", "")

logger.info("Processing request")
# 输出: [2025-11-15 17:10:29.461] [info] [MyPlugin] plugin.py:10 [trace_id] [User 123] [Request abc] Processing request
```

### 2. 条件日志

```python
def execute(self, parameters, parent_output, global_vars, context):
    logger = self.logger
    
    # 只在有 trace_id 时添加
    trace_id = context.get("trace_id")
    if trace_id and trace_id != "unknown":
        logger = logger.with_field(trace_id, "")
    
    logger.info("Processing...")
```

### 3. 错误处理

```python
def execute(self, parameters, parent_output, global_vars, context):
    logger = self.logger.with_field(context.get("trace_id"), "")
    
    try:
        result = self._risky_operation()
        logger.info("✅ Operation succeeded")
        yield {"type": "result", "data": result}
    except ValueError as e:
        logger.with_error(e).error("❌ Invalid input")
        yield {"type": "error", "message": f"Invalid input: {e}"}
    except ConnectionError as e:
        logger.with_error(e).error("❌ Connection failed")
        yield {"type": "error", "message": "Service unavailable"}
    except Exception as e:
        logger.with_error(e).error("❌ Unexpected error")
        yield {"type": "error", "message": "Internal error"}
```

## 最佳实践

### 1. 使用格式化日志

```python
# ✅ 推荐 - 使用格式化
self.logger.infof("Processing %d items for user %s", count, username)

# ❌ 不推荐 - 字符串拼接
self.logger.info(f"Processing {count} items for user {username}")
```

### 2. 添加上下文字段

```python
# ✅ 推荐 - 添加 trace_id
logger = self.logger.with_field(trace_id, "")
logger.info("Processing request")

# ❌ 不推荐 - 在消息中包含
self.logger.info(f"[{trace_id}] Processing request")
```

### 3. 使用 with_error

```python
# ✅ 推荐 - 使用 with_error
try:
    process()
except Exception as e:
    self.logger.with_error(e).error("Processing failed")

# ❌ 不推荐 - 手动格式化
except Exception as e:
    self.logger.error(f"Processing failed: {str(e)}\n{traceback.format_exc()}")
```

### 4. 结构化字段

```python
# ✅ 推荐 - 使用字段
logger = self.logger \
    .with_field(trace_id, "") \
    .with_field(f"User {user_id}", "")
logger.info("Request completed")

# ❌ 不推荐 - 在消息中包含
self.logger.info(f"[{trace_id}] [User {user_id}] Request completed")
```

## 示例输出

### 简单日志
```
[2025-11-15 17:10:29.461] [info] [MyPlugin] plugin.py:10 Application started
```

### 带 trace_id
```
[2025-11-15 17:10:29.503] [info] [MyPlugin] plugin.py:15 [59d428f7843866bd2863561f23c0c657] Processing request
```

### 带多个字段
```
[2025-11-15 17:10:30.596] [info] [MyPlugin] plugin.py:20 [59d428f7843866bd2863561f23c0c657] [Node my_node] [User 123] Request completed
```

### 错误日志
```
[2025-11-15 17:10:31.123] [error] [MyPlugin] plugin.py:25 [59d428f7843866bd2863561f23c0c657] Processing failed
error="division by zero"
Traceback (most recent call last):
  File "plugin.py", line 23, in execute
    result = 1 / 0
ZeroDivisionError: division by zero
```

## 与 Go glog 的兼容性

本库的日志格式与 Go glog 完全兼容，可以与 Go 服务的日志无缝集成：

**Go 日志：**
```
[2025-11-15 17:10:29.461] [info] [Runner] grpc_plugin_node.go:202 [59d428f7843866bd2863561f23c0c657] [Plugin langchain_ollama_python] 🚀 Initializing model
```

**Python 日志：**
```
[2025-11-15 17:10:29.503] [info] [LangChainOllama] langchain_ollama_plugin.py:85 [59d428f7843866bd2863561f23c0c657] 📤 Sending prompt to model
```

两者格式一致，便于日志聚合和分析。

## 参考

- glog-python 文档: https://pypi.org/project/glog-python/1.0.0/
- 框架文档: [README.md](README.md)
