#!/usr/bin/env python3
"""
示例插件 - 展示如何使用 Python Plugin Framework
这是一个简单的文本处理插件
"""

import sys
from typing import Dict, Any, Iterator
from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin


class TextProcessorPlugin(BasePluginService):
    """文本处理插件示例"""

    def __init__(self):
        super().__init__(plugin_name="TextProcessor")

    def get_plugin_metadata(self) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "kind": "text_processor",
            "node_type": "Node",
            "description": "Simple text processing plugin (uppercase, lowercase, reverse)",
            "version": "1.0.0",
            "parameters": [
                {
                    "name": "text",
                    "type": "string",
                    "description": "Input text to process",
                    "required": True,
                    "default_value": ""
                },
                {
                    "name": "operation",
                    "type": "string",
                    "description": "Operation: uppercase, lowercase, reverse",
                    "required": True,
                    "default_value": "uppercase"
                },
                {
                    "name": "prefix",
                    "type": "string",
                    "description": "Optional prefix to add",
                    "required": False,
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
        """执行文本处理"""
        
        # 获取参数
        text = parameters.get("text", "")
        operation = parameters.get("operation", "uppercase")
        prefix = parameters.get("prefix", "")
        
        self.logger.infof("Processing text with operation: %s", operation)
        
        # 发送日志
        yield {"type": "log", "message": f"🔄 Processing: {operation}"}
        
        # 执行操作
        if operation == "uppercase":
            result = text.upper()
        elif operation == "lowercase":
            result = text.lower()
        elif operation == "reverse":
            result = text[::-1]
        else:
            yield {"type": "error", "message": f"Unknown operation: {operation}"}
            return
        
        # 添加前缀
        if prefix:
            result = prefix + result
        
        # 返回结果
        yield {
            "type": "result",
            "data": {
                "result": result,
                "original": text,
                "operation": operation,
                "length": len(result)
            }
        }


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    plugin = TextProcessorPlugin()
    serve_plugin(plugin, port)
