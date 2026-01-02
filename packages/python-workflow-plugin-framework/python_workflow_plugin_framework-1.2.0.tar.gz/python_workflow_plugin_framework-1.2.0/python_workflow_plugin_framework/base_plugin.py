#!/usr/bin/env python3
"""
Python Plugin Framework - Base Plugin Class
通用的 Python 插件基类，简化插件开发
"""

import grpc
import json
import logging
import glog
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Iterator, Optional
from concurrent import futures

# gRPC 反射支持
from grpc_reflection.v1alpha import reflection

# 导入生成的 protobuf 代码
from . import node_plugin_pb2
from . import node_plugin_pb2_grpc


class BasePluginService(node_plugin_pb2_grpc.NodePluginServiceServicer, ABC):
    """
    插件服务基类
    
    子类只需要实现以下方法：
    - get_plugin_metadata(): 返回插件元数据
    - execute(): 执行插件的核心逻辑
    - health_check(): 可选，自定义健康检查
    """

    def __init__(self, plugin_name: str = "BasePlugin"):
        self.plugin_name = plugin_name
        self.node_config = None
        self.workflow_entity = None
        self.server_endpoint = None
        self.request_count = 0
        self.logger = self._setup_logger()
        self.logger.info(f"🎬 {plugin_name} initialized")

    def _setup_logger(self):
        """设置日志记录器 - 使用 glog"""
        # 创建命名的 logger
        logger = glog.default_logger().named(self.plugin_name)
        return logger

    # ==================== 抽象方法（子类必须实现） ====================

    @abstractmethod
    def get_plugin_metadata(self) -> Dict[str, Any]:
        """
        返回插件元数据
        
        Returns:
            dict: 包含以下字段的字典
                - kind: str, 插件类型标识
                - node_type: str, 节点类型
                - description: str, 插件描述
                - version: str, 版本号
                - parameters: List[Dict], 参数定义列表
                - credential_type: str, 可选，凭证类型
        """
        pass

    @abstractmethod
    def execute(
        self,
        parameters: Dict[str, Any],
        parent_output: Dict[str, Any],
        global_vars: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """
        执行插件核心逻辑（生成器函数）
        
        Args:
            parameters: 节点参数
            parent_output: 父节点输出
            global_vars: 全局变量
            context: 上下文信息（包含 trace_id, node_name 等）
        
        Yields:
            dict: 输出消息，格式为：
                - {"type": "log", "message": "日志消息"}
                - {"type": "result", "data": {...}}
                - {"type": "error", "message": "错误消息"}
        """
        pass

    # ==================== 可选方法（子类可以覆盖） ====================

    def health_check(self) -> tuple[bool, str]:
        """
        健康检查（子类可以覆盖）
        
        Returns:
            tuple: (is_healthy: bool, message: str)
        """
        return True, f"✅ {self.plugin_name} is healthy"

    def test_credentials(self, credentials: Dict[str, Any]) -> tuple[bool, str]:
        """
        测试凭证（子类可以覆盖）
        
        Args:
            credentials: 凭证信息
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        return True, "No credentials required"

    def on_init(self, node_config: Dict[str, Any], workflow_entity: Optional[Dict[str, Any]]):
        """
        初始化回调（子类可以覆盖）
        
        Args:
            node_config: 节点配置
            workflow_entity: 工作流实体
        """
        pass

    def on_stop(self, context: Dict[str, Any], reason: str, force: bool) -> tuple[bool, str]:
        """
        停止执行回调（子类可以覆盖）
        
        Args:
            context: 执行上下文
            reason: 停止原因
            force: 是否强制停止
        
        Returns:
            tuple: (success: bool, message: str)
        """
        return True, "Stopped successfully"

    def subscribe_trigger(self, consumer_group: str, filters: Dict[str, str]) -> Iterator[Dict[str, Any]]:
        """
        触发事件订阅（子类可以覆盖，仅触发器类型插件需要实现）
        
        Args:
            consumer_group: 消费组标识
            filters: 过滤条件
        
        Yields:
            dict: 触发事件，格式为：
                - {"event_id": "xxx", "source": "xxx", "payload": {...}, "trace_id": "xxx", "target_workflow": "xxx"}
        """
        # 默认实现：不产生任何事件
        return
        yield  # 使其成为生成器

    def deliver_response(self, event_id: str, body: Any, status_code: int, headers: Dict[str, str], error: str) -> tuple[bool, str]:
        """
        投递工作流同步响应（子类可以覆盖，仅需要同步响应的触发器插件需要实现）
        
        Args:
            event_id: 事件 ID
            body: 响应体
            status_code: HTTP 状态码
            headers: 响应头
            error: 错误信息
        
        Returns:
            tuple: (success: bool, error_message: str)
        """
        return True, ""

    # ==================== gRPC 服务方法实现 ====================

    def GetMetadata(self, request, context):
        """获取插件元数据"""
        self.logger.info("📋 GetMetadata called")
        try:
            metadata = self.get_plugin_metadata()
            name = metadata.get("name") or self.plugin_name
            display_name = metadata.get("display_name") or name
            description = metadata.get("description", "")
            version = metadata.get("version", "1.0.0")
            icon = metadata.get("icon", "")
            tags = metadata.get("tags") or []
            category_str = (metadata.get("category") or "CATEGORY_ACTION").upper()
            node_type_str = (metadata.get("node_type") or "NODE_TYPE_PROCESSOR").upper()
            category_enum = getattr(node_plugin_pb2.NodeCategory, category_str, node_plugin_pb2.NodeCategory.CATEGORY_ACTION)
            node_type_enum = getattr(node_plugin_pb2.NodeType, node_type_str, node_plugin_pb2.NodeType.NODE_TYPE_PROCESSOR)
            input_params_src = metadata.get("input_parameters", metadata.get("parameters", []))
            output_params_src = metadata.get("output_parameters", [])
            def _param_type_enum(t):
                m = {
                    "STRING": node_plugin_pb2.ParameterType.PARAM_TYPE_STRING,
                    "INT": node_plugin_pb2.ParameterType.PARAM_TYPE_INT,
                    "FLOAT": node_plugin_pb2.ParameterType.PARAM_TYPE_FLOAT,
                    "BOOL": node_plugin_pb2.ParameterType.PARAM_TYPE_BOOL,
                    "BYTES": node_plugin_pb2.ParameterType.PARAM_TYPE_BYTES,
                    "ARRAY": node_plugin_pb2.ParameterType.PARAM_TYPE_ARRAY,
                    "OBJECT": node_plugin_pb2.ParameterType.PARAM_TYPE_OBJECT,
                    "ENUM": node_plugin_pb2.ParameterType.PARAM_TYPE_ENUM,
                    "SECRET": node_plugin_pb2.ParameterType.PARAM_TYPE_SECRET,
                    "EXPRESSION": node_plugin_pb2.ParameterType.PARAM_TYPE_EXPRESSION,
                    "CODE": node_plugin_pb2.ParameterType.PARAM_TYPE_CODE,
                    "JSON": node_plugin_pb2.ParameterType.PARAM_TYPE_JSON,
                    "FILE": node_plugin_pb2.ParameterType.PARAM_TYPE_FILE,
                    "URL": node_plugin_pb2.ParameterType.PARAM_TYPE_URL,
                    "DATETIME": node_plugin_pb2.ParameterType.PARAM_TYPE_DATETIME,
                }
                return m.get((t or "").upper(), node_plugin_pb2.ParameterType.PARAM_TYPE_STRING)
            def _to_param_def(param):
                default = param.get("default_value", None)
                return node_plugin_pb2.ParameterDef(
                    name=param.get("name", ""),
                    display_name=param.get("display_name", param.get("name", "")),
                    description=param.get("description", ""),
                    type=_param_type_enum(param.get("type")),
                    required=bool(param.get("required", False)),
                    default_value=self._convert_python_to_proto_value(default) if default is not None else node_plugin_pb2.Value(null_value=node_plugin_pb2.NullValue.NULL_VALUE),
                    placeholder=param.get("placeholder", ""),
                    hint=param.get("hint", ""),
                )
            input_parameters = [ _to_param_def(p) for p in input_params_src ]
            output_parameters = [ _to_param_def(p) for p in output_params_src ]
            cred_type = metadata.get("credential_type", "")
            cred_def_src = metadata.get("credential_def")
            credential_def = None
            if isinstance(cred_def_src, dict):
                fields = [ _to_param_def(f) for f in cred_def_src.get("fields", []) ]
                credential_def = node_plugin_pb2.CredentialDef(
                    type=cred_def_src.get("type", cred_type),
                    display_name=cred_def_src.get("display_name", ""),
                    description=cred_def_src.get("description", ""),
                    fields=fields,
                    auth_url=cred_def_src.get("auth_url", ""),
                    token_url=cred_def_src.get("token_url", ""),
                )
            caps_src = metadata.get("capabilities", {})
            capabilities = node_plugin_pb2.PluginCapabilities(
                supports_streaming=bool(caps_src.get("supports_streaming", True)),
                supports_cancel=bool(caps_src.get("supports_cancel", False)),
                supports_retry=bool(caps_src.get("supports_retry", False)),
                supports_batch=bool(caps_src.get("supports_batch", False)),
                requires_credential=bool(caps_src.get("requires_credential", bool(cred_type))),
                max_concurrent=int(caps_src.get("max_concurrent", 10)),
                default_timeout_ms=int(caps_src.get("default_timeout_ms", 60000)),
            )
            return node_plugin_pb2.GetMetadataResponse(
                name=name,
                display_name=display_name,
                description=description,
                version=version,
                icon=icon,
                category=category_enum,
                node_type=node_type_enum,
                tags=tags,
                input_parameters=input_parameters,
                output_parameters=output_parameters,
                credential_type=cred_type,
                credential_def=credential_def if credential_def else node_plugin_pb2.CredentialDef(),
                capabilities=capabilities,
            )
        except Exception as e:
            self.logger.error(f"❌ GetMetadata failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return node_plugin_pb2.GetMetadataResponse()

    def Init(self, request, context):
        """初始化节点"""
        self.logger.info("🔧 Init called")
        try:
            nc = request.node_config
            wc = request.workflow_config
            params_dict = self._convert_proto_map_to_dict(nc.parameters) if nc and hasattr(nc, "parameters") else {}
            labels_dict = dict(nc.labels) if nc and hasattr(nc, "labels") else {}
            position = {"x": getattr(nc.position, "x", 0.0), "y": getattr(nc.position, "y", 0.0)} if nc and hasattr(nc, "position") else {"x": 0.0, "y": 0.0}
            self.node_config = {
                "id": getattr(nc, "id", ""),
                "name": getattr(nc, "name", "unknown"),
                "kind": getattr(nc, "kind", "unknown"),
                "parameters": params_dict,
                "labels": labels_dict,
                "position": position,
            }
            global_vars = self._convert_proto_map_to_dict(wc.global_vars) if wc and hasattr(wc, "global_vars") else {}
            env = dict(wc.env) if wc and hasattr(wc, "env") else {}
            self.workflow_entity = {
                "id": getattr(wc, "id", ""),
                "name": getattr(wc, "name", ""),
                "version": getattr(wc, "version", ""),
                "global_vars": global_vars,
                "env": env,
            }
            self.server_endpoint = getattr(request, "server_endpoint", "")
            if self.server_endpoint:
                self.logger.infof("   Server endpoint: %s", self.server_endpoint)
            cred = getattr(request, "credential", None)
            if cred and getattr(cred, "type", ""):
                _ = self._convert_proto_map_to_dict(cred.fields)
                self.logger.info("   Credential received")
            self.on_init(self.node_config, self.workflow_entity)
            self.logger.info("✅ Init successful")
            return node_plugin_pb2.InitResponse(success=True, error_code="", error_message="")
        except Exception as e:
            self.logger.with_error(e).error("❌ Init failed")
            return node_plugin_pb2.InitResponse(success=False, error_code="INIT_FAILED", error_message=f"Init failed: {str(e)}")

    def Run(self, request, context):
        """执行节点（流式响应）"""
        self.request_count += 1
        request_id = self.request_count
        start_time = datetime.now()
        
        # 提取上下文信息
        ctx = self._extract_context(context, request_id)
        
        # 创建带有 trace_id 和其他字段的 logger
        run_logger = self.logger.with_field(ctx['trace_id'], "")
        if ctx['node_name'] != 'unknown':
            run_logger = run_logger.with_field(f"Node {ctx['node_name']}", "")
        
        run_logger.info("=" * 60)
        run_logger.infof("🚀 Run called (Request #%d)", request_id)
        run_logger.infof("Workflow: %s , Node: %s (type: %s) ",ctx['workflow_name'],  ctx['node_name'], ctx['node_type'])
#         if ctx['workflow_instance_id']:
#             run_logger.infof("   Instance ID: %s", ctx['workflow_instance_id'])
#         run_logger.infof("🔗 Trace ID: %s", ctx['trace_id'])
        run_logger.info("=" * 60)
        
        try:
            parameters = self._convert_proto_map_to_dict(request.parameters)
            parent_output = self._convert_proto_map_to_dict(request.parent_output)
            global_vars = self._convert_proto_map_to_dict(request.global_vars)
            local_vars = self._convert_proto_map_to_dict(request.local_vars) if hasattr(request, 'local_vars') else {}
            
            # 将 local_vars 添加到 context 中
            ctx['local_vars'] = local_vars
            
            run_logger.infof("📥 Parameters: %s", list(parameters.keys()))
            run_logger.infof("   Parent output: %s", list(parent_output.keys()))
            run_logger.infof("   Global vars: %s", list(global_vars.keys()))
            run_logger.infof("   Local vars: %s", list(local_vars.keys()))
            
            # 调用子类的执行方法
            for output in self.execute(parameters, parent_output, global_vars, ctx):
                output_type = output.get("type")
                
                if output_type == "log":
                    payload = node_plugin_pb2.LogPayload(
                        level=node_plugin_pb2.LogLevel.LOG_LEVEL_INFO,
                        message=output.get("message", "")
                    )
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.ResponseType.RESPONSE_TYPE_LOG,
                        timestamp_ms=int(datetime.now().timestamp() * 1000),
                        log=payload
                    )
                elif output_type == "result":
                    result_data = output.get("data", {})
                    output_map = {}
                    for k, v in (result_data or {}).items():
                        output_map[k] = self._convert_python_to_proto_value(v)
                    res_payload = node_plugin_pb2.ResultPayload(
                        output=output_map,
                        branch_index=output.get("branch_index", 0),
                        status=node_plugin_pb2.ExecutionStatus.EXECUTION_STATUS_SUCCESS,
                        duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    )
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.ResponseType.RESPONSE_TYPE_RESULT,
                        timestamp_ms=int(datetime.now().timestamp() * 1000),
                        result=res_payload
                    )
                elif output_type == "error":
                    err_payload = node_plugin_pb2.ErrorPayload(
                        code=output.get("code", ""),
                        message=output.get("message", "Unknown error"),
                        error_type=node_plugin_pb2.ErrorType.ERROR_TYPE_INTERNAL,
                        retryable=False,
                    )
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.ResponseType.RESPONSE_TYPE_ERROR,
                        timestamp_ms=int(datetime.now().timestamp() * 1000),
                        error=err_payload
                    )
                elif output_type == "progress":
                    prog_payload = node_plugin_pb2.ProgressPayload(
                        current=int(output.get("current", 0)),
                        total=int(output.get("total", 0)),
                        message=output.get("message", ""),
                        percentage=float(output.get("percentage", 0.0)),
                    )
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.ResponseType.RESPONSE_TYPE_PROGRESS,
                        timestamp_ms=int(datetime.now().timestamp() * 1000),
                        progress=prog_payload
                    )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_logger.info("=" * 60)
            run_logger.infof("✅ Request #%d completed in %.2fs", request_id, duration)
            run_logger.info("=" * 60)
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_logger.error("=" * 60)
            run_logger.errorf("❌ Request #%d failed after %.2fs", request_id, duration)
            run_logger.with_error(e).error("   Execution error")
            run_logger.error("=" * 60)
            
            err_payload = node_plugin_pb2.ErrorPayload(
                code="EXECUTION_FAILED",
                message=f"Execution failed: {str(e)}",
                error_type=node_plugin_pb2.ErrorType.ERROR_TYPE_INTERNAL,
                retryable=False,
                stack_trace=traceback.format_exc(),
            )
            yield node_plugin_pb2.RunResponse(
                type=node_plugin_pb2.ResponseType.RESPONSE_TYPE_ERROR,
                timestamp_ms=int(datetime.now().timestamp() * 1000),
                error=err_payload
            )

    def TestCredential(self, request, context):
        """测试凭证"""
        self.logger.info("🔑 TestCredential called")
        try:
            cred = getattr(request, "credential", None)
            cred_dict = {}
            if cred:
                cred_dict = {
                    "type": getattr(cred, "type", ""),
                    "fields": self._convert_proto_map_to_dict(cred.fields),
                    "expires_at_ms": getattr(cred, "expires_at_ms", 0),
                }
            is_valid, message = self.test_credentials(cred_dict)
            self.logger.infof("   Result: %s", message)
            return node_plugin_pb2.TestCredentialResponse(success=is_valid, error_code="" if is_valid else "INVALID_CREDENTIAL", error_message="" if is_valid else message)
        except Exception as e:
            self.logger.with_error(e).error("❌ TestCredential failed")
            return node_plugin_pb2.TestCredentialResponse(success=False, error_code="ERROR", error_message=str(e))

    def HealthCheck(self, request, context):
        """健康检查"""
        self.logger.info("🏥 HealthCheck called")
        try:
            is_healthy, message = self.health_check()
            self.logger.infof("   Result: %s", message)
            status = node_plugin_pb2.HealthStatus.HEALTH_STATUS_HEALTHY if is_healthy else node_plugin_pb2.HealthStatus.HEALTH_STATUS_UNHEALTHY
            plugin_version = ""
            try:
                plugin_version = (self.get_plugin_metadata() or {}).get("version", "")
            except:
                plugin_version = ""
            return node_plugin_pb2.HealthCheckResponse(
                status=status,
                message=message,
                plugin_version=plugin_version,
                protocol_version=str(node_plugin_pb2_grpc.GRPC_GENERATED_VERSION),
                supported_features=["streaming", "grpc"],
                resource_usage=node_plugin_pb2.ResourceUsage(
                    memory_bytes=0,
                    cpu_percent=0.0,
                    goroutines=0,
                    active_connections=0,
                ),
                checked_at_ms=int(datetime.now().timestamp() * 1000),
            )
        except Exception as e:
            self.logger.with_error(e).error("❌ HealthCheck failed")
            return node_plugin_pb2.HealthCheckResponse(
                status=node_plugin_pb2.HealthStatus.HEALTH_STATUS_UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                plugin_version="",
                protocol_version=str(node_plugin_pb2_grpc.GRPC_GENERATED_VERSION),
                supported_features=["streaming", "grpc"],
                resource_usage=node_plugin_pb2.ResourceUsage(
                    memory_bytes=0,
                    cpu_percent=0.0,
                    goroutines=0,
                    active_connections=0,
                ),
                checked_at_ms=int(datetime.now().timestamp() * 1000),
            )

    def SubscribeTrigger(self, request, context):
        """触发事件订阅（流式响应）"""
        self.logger.info("📡 SubscribeTrigger called")
        try:
            consumer_group = getattr(request, "consumer_group", "")
            filters = dict(request.filters) if hasattr(request, "filters") else {}
            
            self.logger.infof("   Consumer group: %s", consumer_group)
            self.logger.infof("   Filters: %s", filters)
            
            # 调用子类的订阅方法
            for event in self.subscribe_trigger(consumer_group, filters):
                trigger_event = node_plugin_pb2.TriggerEvent(
                    event_id=event.get("event_id", ""),
                    source=event.get("source", ""),
                    payload=self._convert_python_to_proto_value(event.get("payload")),
                    trace_id=event.get("trace_id", ""),
                    target_workflow=event.get("target_workflow", ""),
                    timestamp_ms=event.get("timestamp_ms", int(datetime.now().timestamp() * 1000)),
                )
                yield trigger_event
                
        except Exception as e:
            self.logger.with_error(e).error("❌ SubscribeTrigger failed")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    def Stop(self, request, context):
        """停止执行"""
        self.logger.info("🛑 Stop called")
        try:
            # 提取执行上下文
            exec_ctx = getattr(request, "context", None)
            ctx = {}
            if exec_ctx:
                ctx = {
                    "workflow_id": getattr(exec_ctx, "workflow_id", ""),
                    "execution_id": getattr(exec_ctx, "execution_id", ""),
                    "node_id": getattr(exec_ctx, "node_id", ""),
                    "trace_id": getattr(exec_ctx, "trace_id", ""),
                    "span_id": getattr(exec_ctx, "span_id", ""),
                    "retry_count": getattr(exec_ctx, "retry_count", 0),
                    "timeout_ms": getattr(exec_ctx, "timeout_ms", 0),
                    "metadata": dict(exec_ctx.metadata) if hasattr(exec_ctx, "metadata") else {},
                }
            
            reason = getattr(request, "reason", "")
            force = getattr(request, "force", False)
            
            self.logger.infof("   Reason: %s", reason)
            self.logger.infof("   Force: %s", force)
            
            success, message = self.on_stop(ctx, reason, force)
            
            status = node_plugin_pb2.StopStatus.STOP_STATUS_STOPPED if success else node_plugin_pb2.StopStatus.STOP_STATUS_CANNOT_STOP
            
            self.logger.infof("   Result: %s", message)
            return node_plugin_pb2.StopResponse(
                success=success,
                message=message,
                status=status,
            )
        except Exception as e:
            self.logger.with_error(e).error("❌ Stop failed")
            return node_plugin_pb2.StopResponse(
                success=False,
                message=f"Stop failed: {str(e)}",
                status=node_plugin_pb2.StopStatus.STOP_STATUS_CANNOT_STOP,
            )

    def DeliverResponse(self, request, context):
        """投递工作流同步响应"""
        self.logger.info("📬 DeliverResponse called")
        try:
            event_id = getattr(request, "event_id", "")
            body = self._convert_proto_value_to_python(request.body) if hasattr(request, "body") else None
            status_code = getattr(request, "status_code", 200)
            headers = dict(request.headers) if hasattr(request, "headers") else {}
            error = getattr(request, "error", "")
            has_response = getattr(request, "has_response", False)
            
            self.logger.infof("   Event ID: %s", event_id)
            self.logger.infof("   Status code: %d", status_code)
            self.logger.infof("   Has response: %s", has_response)
            
            success, err_msg = self.deliver_response(event_id, body, status_code, headers, error)
            
            self.logger.infof("   Result: success=%s", success)
            return node_plugin_pb2.DeliverResponseResponse(
                success=success,
                error=err_msg,
            )
        except Exception as e:
            self.logger.with_error(e).error("❌ DeliverResponse failed")
            return node_plugin_pb2.DeliverResponseResponse(
                success=False,
                error=f"DeliverResponse failed: {str(e)}",
            )

    # ==================== 辅助方法 ====================

    def _decode_metadata_value(self, value: str) -> str:
        """解码metadata值"""
        import base64
        try:
            # 尝试base64解码
            decoded = base64.urlsafe_b64decode(value).decode('utf-8')
            return decoded
        except:
            # 如果解码失败，返回原始值
            return value

    def _extract_context(self, grpc_context, request_id: int) -> Dict[str, Any]:
        """从 gRPC context 中提取上下文信息"""
        ctx = {
            "trace_id": f"local-{request_id}",
            "span_id": "unknown",
            "trace_flags": "00",
            "node_name": "unknown",
            "node_type": "unknown",
            "workflow_name": "unknown",
            "workflow_instance_id": ""
        }
        
        try:
            metadata = dict(grpc_context.invocation_metadata())
            
            # W3C Trace Context
            if 'traceparent' in metadata:
                parts = metadata['traceparent'].split('-')
                if len(parts) == 4:
                    _, ctx["trace_id"], ctx["span_id"], ctx["trace_flags"] = parts
            
            # 自定义 metadata
            for key in ['x-node-name', 'x-node-type', 'x-workflow-name', 
                       'x-workflow-instance-id', 'x-trace-id']:
                metadata_key = key
                ctx_key = key.replace('x-', '').replace('-', '_')
                if metadata_key in metadata:
                    # 解码metadata值
                    ctx[ctx_key] = metadata[metadata_key]
                    if key == 'x-node-name' or key == 'x-workflow-name' :
                        ctx[ctx_key] = self._decode_metadata_value(metadata[metadata_key])
                    
        except Exception as e:
            self.logger.debugf("Could not extract metadata: %s", str(e))
        
        return ctx

    def _convert_proto_value_to_python(self, proto_value) -> Any:
        """将 protobuf Value 转换为 Python 值"""
        if proto_value is None:
            return None
            
        kind = proto_value.WhichOneof('kind')
        
        if kind == 'null_value':
            return None
        elif kind == 'string_value':
            return proto_value.string_value
        elif kind == 'int_value':
            return proto_value.int_value
        elif kind == 'double_value':
            return proto_value.double_value
        elif kind == 'bool_value':
            return proto_value.bool_value
        elif kind == 'bytes_value':
            return proto_value.bytes_value
        elif kind == 'list_value':
            return [self._convert_proto_value_to_python(v) for v in proto_value.list_value.values]
        elif kind == 'map_value':
            return {k: self._convert_proto_value_to_python(v) 
                   for k, v in proto_value.map_value.fields.items()}
        else:
            return None
    
    def _convert_proto_map_to_dict(self, proto_map) -> Dict:
        """将 protobuf map<string, Value> 转换为 Python dict"""
        return {k: self._convert_proto_value_to_python(v) for k, v in proto_map.items()}

    def _convert_python_to_proto_value(self, value):
        if value is None:
            return node_plugin_pb2.Value(null_value=node_plugin_pb2.NullValue.NULL_VALUE)
        if isinstance(value, bool):
            return node_plugin_pb2.Value(bool_value=value)
        if isinstance(value, int) and not isinstance(value, bool):
            return node_plugin_pb2.Value(int_value=value)
        if isinstance(value, float):
            return node_plugin_pb2.Value(double_value=value)
        if isinstance(value, bytes):
            return node_plugin_pb2.Value(bytes_value=value)
        if isinstance(value, str):
            return node_plugin_pb2.Value(string_value=value)
        if isinstance(value, list):
            lv = node_plugin_pb2.ListValue()
            lv.values.extend([self._convert_python_to_proto_value(v) for v in value])
            return node_plugin_pb2.Value(list_value=lv)
        if isinstance(value, dict):
            mv = node_plugin_pb2.MapValue()
            for k, v in value.items():
                mv.fields[k].CopyFrom(self._convert_python_to_proto_value(v))
            return node_plugin_pb2.Value(map_value=mv)
        return node_plugin_pb2.Value(string_value=str(value))

def serve_plugin(plugin_service: BasePluginService, port: int = 50052):
    """
    启动插件服务器
    
    Args:
        plugin_service: 插件服务实例
        port: 监听端口
    """
    logger = plugin_service.logger
    
    logger.info("=" * 60)
    logger.infof("🚀 Starting %s", plugin_service.plugin_name)
    logger.info("=" * 60)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info("   Thread pool: 10 workers")
    
    # 添加服务
    node_plugin_pb2_grpc.add_NodePluginServiceServicer_to_server(plugin_service, server)
    logger.info("   Service registered: NodePluginService")
    
    # 启用反射 API
    SERVICE_NAMES = (
        node_plugin_pb2.DESCRIPTOR.services_by_name['NodePluginService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    logger.info("   Reflection API enabled")
    
    server.add_insecure_port(f"[::]:{port}")
    logger.infof("   Listening on port: %d", port)
    
    server.start()
    
    # 获取插件元数据用于显示
    metadata = plugin_service.get_plugin_metadata()
    
    print("=" * 60)
    print(f"🚀 {plugin_service.plugin_name}")
    print("=" * 60)
    print(f"📦 Version: {metadata.get('version', '1.0.0')}")
    print(f"🔗 Port: {port}")
    print(f"📝 Description: {metadata.get('description', 'N/A')}")
    print("=" * 60)
    print("✅ Server started successfully!")
    print("📝 Press Ctrl+C to stop...")
    print("=" * 60)
    
    logger.info("✅ Server is ready to accept requests")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
        server.stop(0)
        logger.info("👋 Server stopped gracefully")
