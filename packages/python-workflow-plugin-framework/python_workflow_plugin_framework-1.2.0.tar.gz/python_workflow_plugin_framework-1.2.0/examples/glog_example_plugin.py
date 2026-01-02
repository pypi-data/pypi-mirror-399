#!/usr/bin/env python3
"""
glog 日志示例插件
展示如何在插件中使用 glog-python 进行日志记录
"""

import sys
from typing import Dict, Any, Iterator
from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin


class GlogExamplePlugin(BasePluginService):
    """glog 日志示例插件"""

    def __init__(self):
        super().__init__(plugin_name="GlogExample")

    def get_plugin_metadata(self) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "kind": "glog_example",
            "node_type": "Node",
            "description": "glog logging example plugin",
            "version": "1.0.0",
            "parameters": [
                {
                    "name": "message",
                    "type": "string",
                    "description": "Message to log",
                    "required": True,
                    "default_value": "Hello, glog!"
                },
                {
                    "name": "log_level",
                    "type": "string",
                    "description": "Log level: debug, info, warn, error",
                    "required": False,
                    "default_value": "info"
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
        """执行插件逻辑，展示不同级别的日志"""
        
        message = parameters.get("message", "Hello, glog!")
        log_level = parameters.get("log_level", "info").lower()
        
        # 基本日志
        self.logger.info("Starting glog example plugin execution")
        self.logger.debug(f"Parameters: {parameters}")
        
        # 格式化日志
        self.logger.infof("Processing message: %s", message)
        self.logger.infof("Log level: %s", log_level)
        
        # 带字段的日志
        logger_with_fields = self.logger.with_field("trace_id", context.get("trace_id", "unknown"))
        logger_with_fields.infof("Message with trace_id: %s", message)
        
        # 根据参数设置日志级别
        if log_level == "debug":
            self.logger.debug("This is a DEBUG level message")
        elif log_level == "info":
            self.logger.info("This is an INFO level message")
        elif log_level == "warn":
            self.logger.warn("This is a WARN level message")
        elif log_level == "error":
            self.logger.error("This is an ERROR level message")
        else:
            self.logger.info("Unknown log level specified")
        
        # 测试不同级别的格式化日志
        self.logger.debugf("Debug message with format: %s", message)
        self.logger.infof("Info message with format: %s", message)
        self.logger.warnf("Warn message with format: %s", message)
        self.logger.errorf("Error message with format: %s", message)
        
        # 返回结果
        yield {
            "type": "result",
            "data": {
                "message": message,
                "log_level": log_level,
                "status": "completed",
                "context": context
            }
        }


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50055
    plugin = GlogExamplePlugin()
    serve_plugin(plugin, port)