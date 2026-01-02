#!/usr/bin/env python3
"""
LangChain + Ollama 插件 - 使用 Python Plugin Framework
"""

import sys
from typing import Dict, Any, Iterator

from python_workflow_plugin_framework.base_plugin import BasePluginService, serve_plugin

# LangChain imports
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class LangChainOllamaPlugin(BasePluginService):
    """LangChain + Ollama 插件"""

    def __init__(self):
        super().__init__(plugin_name="LangChainOllama")

    def get_plugin_metadata(self) -> Dict[str, Any]:
        """返回插件元数据"""
        return {
            "kind": "langchain_ollama_python",
            "node_type": "Node",
            "description": "LangChain v1.0 + Ollama plugin for local LLM inference",
            "version": "1.0.1",
            "parameters": [
                {
                    "name": "model",
                    "type": "string",
                    "description": "Ollama model name (e.g., llama3.2, mistral, codellama)",
                    "required": True,
                    "default_value": "llama3.2"
                },
                {
                    "name": "prompt",
                    "type": "string",
                    "description": "Prompt text or template",
                    "required": True,
                    "default_value": ""
                },
                {
                    "name": "temperature",
                    "type": "double",
                    "description": "Temperature for sampling (0.0 to 1.0)",
                    "required": False,
                    "default_value": "0.7"
                },
                {
                    "name": "max_tokens",
                    "type": "int",
                    "description": "Maximum number of tokens to generate",
                    "required": False,
                    "default_value": "512"
                },
                {
                    "name": "base_url",
                    "type": "string",
                    "description": "Ollama API base URL",
                    "required": False,
                    "default_value": "http://localhost:11434"
                },
                {
                    "name": "stream",
                    "type": "string",
                    "description": "Enable streaming output",
                    "required": False,
                    "default_value": "false"
                },
                {
                    "name": "system_message",
                    "type": "string",
                    "description": "System message for the model",
                    "required": False,
                    "default_value": ""
                },
                {
                    "name": "top_p",
                    "type": "double",
                    "description": "Top-p sampling parameter",
                    "required": False,
                    "default_value": "0.9"
                },
                {
                    "name": "top_k",
                    "type": "int",
                    "description": "Top-k sampling parameter",
                    "required": False,
                    "default_value": "40"
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
        """执行 LLM 推理"""
        
        # 获取参数
        model = parameters.get("model", "llama3.2")
        prompt_text = parameters.get("prompt", "")
        temperature = float(parameters.get("temperature", 0.7))
        max_tokens = int(parameters.get("max_tokens", 512))
        base_url = parameters.get("base_url", "http://localhost:11434")
        stream_mode = str(parameters.get("stream", "false")).lower() == "true"
        system_message = parameters.get("system_message", "")
        top_p = float(parameters.get("top_p", 0.9))
        top_k = int(parameters.get("top_k", 40))
        
        self.logger.infof("Model: %s, Temperature: %.2f, Stream: %s", model, temperature, stream_mode)
        
        if not prompt_text:
            yield {"type": "error", "message": "Prompt text is required"}
            return
        
        # 初始化 LLM
        yield {"type": "log", "message": f"🚀 Initializing Ollama model: {model}"}
        
        llm = OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=temperature,
            num_predict=max_tokens,
            top_p=top_p,
            top_k=top_k,
        )
        
        # 构建 chain
        if system_message:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", "{input}")
            ])
            chain = prompt_template | llm | StrOutputParser()
            full_prompt = {"input": prompt_text}
        else:
            chain = llm | StrOutputParser()
            full_prompt = prompt_text
        
        yield {"type": "log", "message": "📤 Sending prompt to model..."}
        
        # 执行推理
        response_text = ""
        chunk_count = 0
        
        if stream_mode:
            yield {"type": "log", "message": "📡 Streaming response..."}
            for chunk in chain.stream(full_prompt):
                chunk_count += 1
                response_text += chunk
                yield {"type": "log", "message": f"💬 {chunk}"}
        else:
            response_text = chain.invoke(full_prompt)
            if not isinstance(response_text, str):
                response_text = str(response_text)
            chunk_count = 1
            yield {"type": "log", "message": f"✅ Response received ({len(response_text)} chars)"}
        
        # 返回结果
        yield {
            "type": "result",
            "data": {
                "result": response_text,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "metadata": {
                    "response_length": len(response_text),
                    "stream_mode": stream_mode,
                    "base_url": base_url,
                    "chunk_count": chunk_count
                }
            }
        }

    def health_check(self) -> tuple[bool, str]:
        """健康检查 - 检查 Ollama 服务"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "unknown") for m in models]
                return True, f"✅ Ollama healthy. Models: {', '.join(model_names[:3])}"
            else:
                return False, "⚠️ Ollama service not responding properly"
        except Exception as e:
            return False, f"❌ Health check failed: {str(e)}"


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    plugin = LangChainOllamaPlugin()
    serve_plugin(plugin, port)
