from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path

from sora2wm.server.lifespan import lifespan
from sora2wm.server.router import router


def init_app():
    """初始化FastAPI应用实例"""
    # 创建FastAPI应用，配置生命周期管理
    app = FastAPI(lifespan=lifespan)
    
    # 添加静态文件服务支持
    # 尝试查找前端静态文件目录
    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # 添加根路径路由
    @app.get("/")
    async def root():
        """根路径接口，返回API信息"""
        return {
            "message": "Sora2水印清除器API",
            "endpoints": {
                "submit_task": "/submit_remove_task",
                "get_results": "/get_results?remove_task_id=your_task_id",
                "download": "/download/your_task_id"
            }
        }
    
    # 添加Vite客户端请求的回退处理
    @app.get("/@vite/client")
    async def vite_client():
        """处理Vite客户端请求，避免404错误"""
        return {"message": "Vite客户端不可用。这是一个API服务器。"}
    
    # 添加favicon.ico路径处理，避免404错误
    @app.get("/favicon.ico")
    async def favicon():
        """处理网站图标请求，避免404错误"""
        return JSONResponse(
            content={"message": "网站图标请求已处理"},
            status_code=200
        )
    
    # 注册API路由
    app.include_router(router)
    return app
