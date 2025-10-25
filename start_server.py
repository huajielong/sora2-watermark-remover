"""
Sora2水印清除器 - 服务器启动脚本

此脚本用于启动FastAPI服务器，提供水印清除的API服务
"""

import argparse

import fire
import uvicorn
from loguru import logger

from sora2wm.configs import LOGS_PATH  # 导入日志文件路径配置
from sora2wm.server.app import init_app  # 导入FastAPI应用初始化函数

# 创建命令行参数解析器
parser = argparse.ArgumentParser(description="启动Sora2水印清除器服务器")
parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
parser.add_argument("--port", default=5344, help="服务器端口")
parser.add_argument("--workers", default=1, type=int, help="工作进程数量")
args = parser.parse_args()

# 配置日志记录器，日志文件按周轮换
logger.add(LOGS_PATH / "log_file.log", rotation="1 week")


def start_server(port=args.port, host=args.host):
    """
    启动FastAPI服务器
    
    参数:
    - port: 服务器监听端口
    - host: 服务器主机地址
    """
    # 记录服务器启动信息
    logger.info(f"服务器启动在 {host}:{port}")
    
    # 初始化FastAPI应用实例
    app = init_app()
    
    # 创建Uvicorn配置，设置主机、端口和工作进程数
    config = uvicorn.Config(app, host=host, port=port, workers=args.workers)
    
    # 创建并运行服务器
    server = uvicorn.Server(config=config)
    
    try:
        # 启动服务器，这会阻塞当前线程直到服务器关闭
        server.run()
    finally:
        # 服务器关闭时记录日志
        logger.info("服务器已关闭。")


if __name__ == "__main__":
    # 使用Fire库启动服务器函数，支持命令行参数解析和参数传递
    fire.Fire(start_server)
