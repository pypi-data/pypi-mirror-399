# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建MCP服务工程

Authors: fubo
Date: 2025/06/30 23:59:59
"""
import os
import json
import sys
import logging
import argparse
from typing import List
from datetime import datetime
import configparser

from .mcp_server_config import McpServerConfig, McpServerToolConfig


class Operator:
    def __init__(self, config_file: str="mcp-server.json"):
        self.config_file_abs_path = os.sep.join(os.path.abspath(config_file).split(os.sep)[:-1])
        self.config_file_name = config_file.split(os.sep)[-1]
        self.config: McpServerConfig = McpServerConfig.model_validate_json(open(config_file, "r").read())
        self.date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.curr_code_path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])

    @staticmethod
    def snake2camel(name: str):
        """
        snake格式转Camel
        :param name:
        :return:
        """
        return "".join([elem.capitalize() for elem in name.split("_")])

    def create_config_file(self, config_file: str=""):
        """ 生成MCP服务配置文件 """
        if not config_file or config_file == "":
            raise ValueError("Error config_file for server config")

        if config_file.split(".")[-1] != "json":
            raise ValueError("Not a json config_file for server config")

        with open(config_file, "w") as fp:
            fp.write(
                json.dumps(
                    self.config.dict(), ensure_ascii=False, indent=4, separators=(',',':')
                )
            )

    def create_init_file(self, module_path:str):
        """
        创建module模块的init文件
        :param module_path:
        :return:
        """
        cmd_str = "cp {}__init__.py {}__init__.py".format(
            self.curr_code_path + os.sep + "template" + os.sep, module_path + os.sep
        )
        logging.info("Move __init__.py to projects {}".format(cmd_str))
        
        os.system(cmd_str)

    def create_service_file(self, module_path:str):
        """
        创建module的service文件
        :param module_path:
        :return:
        """
        with open("{}service.py.template".format(self.curr_code_path + os.sep + "template" + os.sep), "r") as fp:
            code_str = fp.read()
            code_str = code_str.replace(
                "[author]", self.config.author
            ).replace(
                "[date]", self.date_str
            )

        with open("{}service.py".format(module_path + os.sep), "w") as fp:
            fp.write(code_str)

    def create_server_file(self, module_name: str, module_cn_name:str, module_path: str, tool_str: str):
        """
        创建module的server文件
        :param module_path:
        :return:
        """
        with open("{}server.py.template".format(self.curr_code_path + os.sep + "template" + os.sep), "r") as fp:
            code_str = fp.read()
            code_str = code_str.replace(
                "[author]", self.config.author
            ).replace(
                "[date]", self.date_str
            ).replace(
                "[snake_module_name]", module_name
            ).replace(
                "[camel_module_name]", Operator.snake2camel(module_name)
            ).replace(
                "[module_cn_name]", module_cn_name
            ).replace(
                "[tools]", tool_str
            )
        
        with open("{}server.py".format(module_path + os.sep), "w") as fp:
            fp.write(code_str)

    @staticmethod
    def create_tools_str(tools: List[McpServerToolConfig]):
        """
        创建tools代码
        :param tools:
        :return:
        """
        funcs = []
        header = "    @mcp.tool()"
        func_header = "    def [function_name]([params]):"
        func_desc = '        """[function_desc]"""'
        func_body = '        return ""'
        for tool in tools:
            params = ["{}: {}".format(param.param_name, param.param_type) for param in tool.tool_params]
            descriptions = [
                "        :param {}: {}".format(
                    param.param_name, param.param_description
                ) for param in tool.tool_params
            ]
            descriptions = [
                               "",
                               "        " + tool.tool_description
                           ] + descriptions + ["        "]
            func = [
                header,
                func_header.replace(
                    "[function_name]", tool.tool_name
                ).replace(
                    "[params]", ", ".join(params)
                ),
                func_desc.replace("[function_desc]", "\n".join(descriptions)),
                func_body
            ]
            funcs.append("\n".join(func))
            funcs.append("\n")
        return "\n".join(funcs)

    def revise_pyproject_toml_file(self, mcp_server_name: str, mcp_server_description: str):
        """
        修改pyproject.toml文件
        :param mcp_server_name:
        :return:
        """
        project_path = self.config_file_abs_path + os.sep + mcp_server_name + os.sep
        conf = configparser.ConfigParser()
        conf.read("{}pyproject.toml".format(project_path), encoding='utf-8')
        conf.set("project", "dependencies", json.dumps(["fastmcp>=2.9.2","uv>=0.7.17"], ensure_ascii=False))
        conf.set("project", "version", "0.0.0")
        conf.set("project", "description", '"{}"'.format(mcp_server_description))
        conf.write(open("{}pyproject.toml".format(project_path), "w"))

    def create_main_server(
        self, host, port, mcp_server_name: str, mcp_server_cn_name: str, 
        module_camel_list: List[str], sub_modules: List[str]
    ):
        """
        挂载模块服务
        :return:
        """
        # 拷贝requirements.txt
        source_req_file = "{}requirements.txt ".format(self.curr_code_path + os.sep + "template" + os.sep)
        dest_req_file = "{}requirements.txt".format(self.config_file_abs_path + os.sep + mcp_server_name + os.sep)
        os.system("cp {} {}".format(source_req_file, dest_req_file))

        # 创建Dockerfile文件
        with open("{}Dockerfile.template".format(self.curr_code_path + os.sep + "template" + os.sep), "r") as fp:
            code_str = fp.read()
            code_str = code_str.replace(
                "[mcp_server_name]", mcp_server_name
            )
        with open("{}Dockerfile".format(self.config_file_abs_path + os.sep + mcp_server_name + os.sep), "w") as fp:
            fp.write(code_str)

        # 创建main.py文件
        with open("{}main.py.template".format(self.curr_code_path + os.sep + "template" + os.sep), "r") as fp:
            code_str = fp.read()
            code_str = code_str.replace(
                "[author]", self.config.author
            ).replace(
                "[date]", self.date_str
            ).replace(
                "[host]", host
            ).replace(
                "[port]", port
            ).replace(
                "[transport]", self.config.transport
            ).replace(
                "[import_module]", "\n".join(module_camel_list)
            ).replace(
                "[mcp_sub_server]","\n".join(sub_modules)
            ).replace(
                "[mcp_server_cn_name]", mcp_server_cn_name
            )
        with open("{}main.py".format(self.config_file_abs_path + os.sep + mcp_server_name + os.sep), "w") as fp:
            fp.write(code_str)


    def run(self):
        """创建MCP服务"""
        # 配置文件绝对路径
        os.system(
            "cd {};uv init {}".format(self.config_file_abs_path, self.config.mcp_server_name)
        )
        module_camel_list = []
        sub_modules = []
        # 创建模块文件夹
        for module in self.config.modules:
            # 生成import包代码
            module_camel_list.append(
                "from {}.server import Server as {}Server".format(
                    module.module_name, Operator.snake2camel(module.module_name)
                )
            )
            sub_modules.append(
                '    mcp.mount("{}", {}Server.mcp)'.format(
                    module.module_name, Operator.snake2camel(module.module_name)
                )
            )
            # 创建模块
            module_path = self.config_file_abs_path + os.sep + self.config.mcp_server_name + os.sep + module.module_name
            os.system("mkdir {}".format(module_path))
            self.create_init_file(module_path=module_path)
            self.create_service_file(module_path=module_path)
            # 创建工具函数
            self.create_server_file(
                module_name=module.module_name, module_cn_name=module.module_cn_name, module_path=module_path,
                tool_str=Operator.create_tools_str(module.tools)
            )

        # 创建主服务文件
        self.create_main_server(
            host=self.config.host, port=str(self.config.port),
            mcp_server_name=self.config.mcp_server_name, mcp_server_cn_name=self.config.mcp_server_cn_name,
            module_camel_list=module_camel_list, sub_modules=sub_modules
        )

        # 修改pytoml配置文件
        self.revise_pyproject_toml_file(
            mcp_server_name=self.config.mcp_server_name,
            mcp_server_description=self.config.mcp_server_description
        )



def main():
    log_format = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stderr)
    parser = argparse.ArgumentParser(description="MCP Server Creator")
    parser.add_argument("config_file", type=str, help="MCP server config file")
    parser.add_argument(
        "--generate", default=False, action='store_true', help="Generate MCP server config"
    )

    args = parser.parse_args()
    config_file = args.config_file
    for_generate = args.generate
    # for_generate = False
    # config_file = "a.json"
    if for_generate:
        # 生成配置文件
        curr_code_path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
        Operator(
            config_file=curr_code_path + os.sep + "mcp-server.json"
        ).create_config_file(config_file=config_file)
        return 0

    # 创建服务
    Operator(config_file=config_file).run()
    return 0


if __name__ == '__main__':
    main()
