# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务日志服务库

Authors: fubo
Date: 2025/06/30 23:59:59
"""
import sys
import re
import redis
import logging
from logging.handlers import TimedRotatingFileHandler


class MCPLogger:
    class RedisHandler(logging.Handler):
        def __init__(self, host: str, port: int, db: int, password: str, prefix: str='logging', id_filter: str=""):
            super().__init__()
            self.redis_conn = redis.StrictRedis(host=host, port=port, db=db, password=password)
            self.prefix = prefix
            self.id_filter = id_filter

        def emit(self, record):
            message = self.format(record)
            if self.id_filter == "":
                self.redis_conn.lpush(self.prefix, message)
                return None

            session_ids = re.findall(self.id_filter, record.message)
            if len(session_ids) == 0:
                return None
            else:
                self.redis_conn.lpush(f"{self.prefix}:{session_ids[0]}", message)

    @staticmethod
    def set_log(
            logging_log_file: str = "",
            logging_backup_count=0,
            logging_output_type="console",
            logging_redis_host="",
            logging_redis_port=0,
            logging_redis_db=0,
            logging_redis_password="",
            logging_redis_prefix="",
            logging_redis_session_id_filter=""
    ):
        """
        设置日志
        :param logging_log_file: 日志文件名
        :param logging_backup_count: 日志保留数
        :param logging_output_type: 日志输出类型（console、file、redis）
        :param logging_redis_host: redis host
        :param logging_redis_port: redis port
        :param logging_redis_db: redis db
        :param logging_redis_password: redis password
        :param logging_redis_prefix: redis key前缀
        :param logging_redis_session_id_filter: redis session id
        :return: 队列中无数据情况下，返回空字符串
        """
        log_format = "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"

        if logging_output_type == "console":
            logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stderr)
            return

        if logging_output_type == "file":
            log_file_handler = TimedRotatingFileHandler(
                filename=logging_log_file, when="D", interval=1, backupCount=logging_backup_count
            )
            log_file_handler.setFormatter(logging.Formatter(log_format))
            logging.basicConfig(level=logging.INFO, handlers=[log_file_handler, logging.StreamHandler()])
            return

        if logging_output_type == "redis":
            logging.basicConfig(
                level=logging.INFO, format=log_format,
                handlers=[
                    MCPLogger.RedisHandler(
                        host=logging_redis_host,
                        port=logging_redis_port,
                        db=logging_redis_db,
                        password=logging_redis_password,
                        prefix=logging_redis_prefix,
                        id_filter=logging_redis_session_id_filter
                    ),
                    logging.StreamHandler()
                ]
            )
            return

        logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stderr)