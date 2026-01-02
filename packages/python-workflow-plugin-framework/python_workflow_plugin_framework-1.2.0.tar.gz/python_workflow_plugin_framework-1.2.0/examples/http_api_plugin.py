#!/usr/bin/env python3
"""
HTTP API 插件示例 - 展示如何创建一个调用外部 API 的插件
"""

import sys
import requests
from typing import Dict, Any, Iterator
from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin


class HttpApiPlugin(BasePluginService):
    """HTTP API 调用插件"""

    def __init__(self):
        super().__init__(plugin_name="HttpAPI")
        self.session = None

    def get_plugin_metadata(self) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "kind": "http_api",
            "node_type": "Node",
            "description": "HTTP API client plugin with support for GET, POST, PUT, DELETE",
            "version": "1.0.0",
            "credential_type": "api_key",  # 需要 API Key
            "parameters": [
                {
                    "name": "url",
                    "type": "string",
                    "description": "API endpoint URL",
                    "required": True,
                    "default_value": ""
                },
                {
                    "name": "method",
                    "type": "string",
                    "description": "HTTP method (GET, POST, PUT, DELETE)",
                    "required": True,
                    "default_value": "GET"
                },
                {
                    "name": "headers",
                    "type": "string",
                    "description": "JSON string of headers",
                    "required": False,
                    "default_value": "{}"
                },
                {
                    "name": "body",
                    "type": "string",
                    "description": "Request body (for POST/PUT)",
                    "required": False,
                    "default_value": ""
                },
                {
                    "name": "timeout",
                    "type": "int",
                    "description": "Request timeout in seconds",
                    "required": False,
                    "default_value": "30"
                },
                {
                    "name": "verify_ssl",
                    "type": "string",
                    "description": "Verify SSL certificates",
                    "required": False,
                    "default_value": "true"
                }
            ]
        }

    def on_init(self, node_config: Dict[str, Any], workflow_entity: Dict[str, Any]):
        """初始化 HTTP session"""
        self.session = requests.Session()
        self.logger.info("HTTP session initialized")

    def execute(
        self,
        parameters: Dict[str, Any],
        parent_output: Dict[str, Any],
        global_vars: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """执行 HTTP 请求"""
        
        # 获取参数
        url = parameters.get("url", "")
        method = parameters.get("method", "GET").upper()
        headers_str = parameters.get("headers", "{}")
        body = parameters.get("body", "")
        timeout = int(parameters.get("timeout", 30))
        verify_ssl = str(parameters.get("verify_ssl", "true")).lower() == "true"
        
        # 验证参数
        if not url:
            yield {"type": "error", "message": "URL is required"}
            return
        
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            yield {"type": "error", "message": f"Unsupported method: {method}"}
            return
        
        # 解析 headers
        try:
            import json
            headers = json.loads(headers_str)
        except json.JSONDecodeError:
            yield {"type": "error", "message": "Invalid JSON in headers"}
            return
        
        # 添加追踪信息到 headers
        headers["X-Trace-Id"] = context.get("trace_id", "unknown")
        headers["X-Workflow-Name"] = context.get("workflow_name", "unknown")
        
        self.logger.infof("Making %s request to %s", method, url)
        yield {"type": "log", "message": f"🌐 {method} {url}"}
        
        # 执行请求
        try:
            if method == "GET":
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=timeout, 
                    verify=verify_ssl
                )
            elif method in ["POST", "PUT", "PATCH"]:
                response = self.session.request(
                    method,
                    url,
                    headers=headers,
                    data=body,
                    timeout=timeout,
                    verify=verify_ssl
                )
            elif method == "DELETE":
                response = self.session.delete(
                    url,
                    headers=headers,
                    timeout=timeout,
                    verify=verify_ssl
                )
            
            # 记录响应
            self.logger.infof("Response status: %d", response.status_code)
            yield {"type": "log", "message": f"✅ Status: {response.status_code}"}
            
            # 尝试解析 JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            # 返回结果
            yield {
                "type": "result",
                "data": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response_data,
                    "success": 200 <= response.status_code < 300,
                    "metadata": {
                        "url": url,
                        "method": method,
                        "elapsed_ms": response.elapsed.total_seconds() * 1000
                    }
                }
            }
            
        except requests.Timeout:
            yield {"type": "error", "message": f"Request timeout after {timeout}s"}
        except requests.ConnectionError as e:
            yield {"type": "error", "message": f"Connection error: {str(e)}"}
        except Exception as e:
            yield {"type": "error", "message": f"Request failed: {str(e)}"}

    def test_credentials(self, credentials: Dict[str, Any]) -> tuple[bool, str]:
        """测试 API Key"""
        api_key = credentials.get("api_key", "")
        if not api_key:
            return False, "API key is required"
        
        # 这里可以添加实际的验证逻辑
        # 例如：调用一个测试端点
        self.logger.info("API key validation passed")
        return True, "✅ API key is valid"

    def health_check(self) -> tuple[bool, str]:
        """健康检查"""
        if self.session is None:
            return False, "❌ HTTP session not initialized"
        return True, "✅ HTTP API plugin is healthy"


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50053
    plugin = HttpApiPlugin()
    serve_plugin(plugin, port)
