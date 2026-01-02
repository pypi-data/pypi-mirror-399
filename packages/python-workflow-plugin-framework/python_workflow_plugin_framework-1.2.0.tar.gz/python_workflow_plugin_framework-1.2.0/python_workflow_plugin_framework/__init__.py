"""
Python Workflow Plugin Framework

一个简化 Python 工作流插件开发的通用框架。

使用示例:
    from base_plugin import BasePluginService, serve_plugin
    
    class MyPlugin(BasePluginService):
        def get_plugin_metadata(self):
            return {...}
        
        def execute(self, parameters, parent_output, global_vars, context):
            yield {"type": "result", "data": {...}}
    
    if __name__ == "__main__":
        serve_plugin(MyPlugin(), port=50052)
"""

__version__ = "1.0.0"
__author__ = "Your Team"

from .base_plugin import BasePluginService, serve_plugin

__all__ = ["BasePluginService", "serve_plugin"]
