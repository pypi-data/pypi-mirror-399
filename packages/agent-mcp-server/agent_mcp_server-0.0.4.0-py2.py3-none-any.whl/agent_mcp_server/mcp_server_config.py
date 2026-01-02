from pydantic import BaseModel
from typing import List


class McpServerToolParamConfig(BaseModel):
    # 参数名
    param_name: str

    # 参数类型
    param_type: str

    # 参数描述
    param_description: str


class McpServerToolConfig(BaseModel):
    # 工具名
    tool_name: str

    # 工具功能描述
    tool_description: str

    # 工具参数列表
    tool_params: List[McpServerToolParamConfig]


class McpServerModuleConfig(BaseModel):
    # 模块名
    module_name: str

    # 模块中文名
    module_cn_name: str

    # 工具列表
    tools: List[McpServerToolConfig] = []


class McpServerConfig(BaseModel):
    # MCP服务名
    mcp_server_name: str

    # MCP中文服务名
    mcp_server_cn_name: str

    # mcp服务能力描述
    mcp_server_description: str

    # MCP协议
    transport: str = "sse"

    # 作者
    author: str

    # Host
    host: str = "0.0.0.0"

    # Port
    port: int = 8000

    # 模块列表
    modules: List[McpServerModuleConfig] = []

