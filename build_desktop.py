# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess
import logging
import time
import fnmatch
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_torch_paths():
    """Get PyTorch paths dynamically"""
    try:
        import torch
        torch_path = os.path.dirname(torch.__file__)
        torch_lib_path = os.path.join(torch_path, 'lib')
        return torch_path, torch_lib_path
    except Exception as e:
        logger.error(f"Error getting PyTorch paths: {e}")
        return None, None
    
# 确保关键PyTorch库被复制
def ensure_torch_libraries(torch_path, target_dir):
    # 找到torch目录
    torch_lib_path = os.path.join(torch_path, 'lib')
    if not os.path.exists(torch_lib_path):
        logger.error(f"torch lib path not found: {torch_lib_path}")
        return
    
    # 复制所有必要的torch相关文件，特别是shm.dll
    torch_dlls_to_copy = [
        'torch_cpu.dll',
        'torch_python.dll',
        'shm.dll',  # 关键文件，确保被包含
        'c10.dll',  # 必要依赖
        'fbgemm.dll',  # 可能是shm.dll的依赖
        'mkldnn.dll',  # 可能是shm.dll的依赖
    ]
    
    # 复制必要的torch dll文件
    for dll_name in torch_dlls_to_copy:
        source_path = os.path.join(torch_lib_path, dll_name)
        target_path = os.path.join(target_dir, '_internal', dll_name)
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, target_path)
                logger.info(f"Copied {dll_name} to {target_path}")
            except Exception as e:
                logger.error(f"Failed to copy {dll_name}: {e}")
        else:
            logger.warning(f"{dll_name} not found in {torch_lib_path}")
    
    # 特别检查shm.dll是否已复制到正确位置
    shm_source = os.path.join(torch_lib_path, 'shm.dll')
    if os.path.exists(shm_source):
        # 确保shm.dll也被复制到torch/lib目录
        shm_target = os.path.join(target_dir, '_internal', 'torch', 'lib', 'shm.dll')
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(shm_target), exist_ok=True)
        try:
            shutil.copy2(shm_source, shm_target)
            logger.info(f"Copied shm.dll to torch/lib directory: {shm_target}")
        except Exception as e:
            logger.error(f"Failed to copy shm.dll to torch/lib: {e}")

def copy_dlls():
    """Copy necessary DLLs for the PyQt5 application with PyTorch support"""
    logger.info("Copying necessary DLLs for PyQt5 application with PyTorch support...")
    
    # 创建必要的目录结构
    target_dir = os.path.join('dist', 'Sora2WatermarkRemover')
    internal_dir = os.path.join(target_dir, '_internal')
    resources_dir = os.path.join(internal_dir, 'resources')
    ffmpeg_dir = os.path.join(internal_dir, 'ffmpeg')
    
    # 确保关键的PyTorch库被正确复制，特别是shm.dll
    torch_path, torch_lib_path = get_torch_paths()
    if torch_path and os.path.exists(torch_path):
        logger.info(f"Ensuring PyTorch libraries are properly copied from {torch_path}")
        ensure_torch_libraries(torch_path, target_dir)
    else:
        logger.warning("PyTorch paths not found, skipping PyTorch library copying")
    
    # 确保目录存在
    os.makedirs(resources_dir, exist_ok=True)
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # 1. 复制模型文件到_internal/resources目录（保持必要功能）
    try:
        big_lama_source = os.path.join('resources', 'big-lama.pt')
        big_lama_target = os.path.join(resources_dir, 'big-lama.pt')
        if os.path.exists(big_lama_source):
            shutil.copy2(big_lama_source, big_lama_target)
            logger.info(f"Copied big-lama.pt to {resources_dir}")
        else:
            logger.warning(f"big-lama.pt not found at {big_lama_source}")
    except Exception as e:
        logger.error(f"Failed to copy big-lama.pt: {e}")
    
    try:
        best_pt_source = os.path.join('resources', 'best.pt')
        best_pt_target = os.path.join(resources_dir, 'best.pt')
        if os.path.exists(best_pt_source):
            shutil.copy2(best_pt_source, best_pt_target)
            logger.info(f"Copied best.pt to {resources_dir}")
        else:
            logger.warning(f"best.pt not found at {best_pt_source}")
    except Exception as e:
        logger.error(f"Failed to copy best.pt: {e}")
    
    # 2. 复制ffmpeg相关文件到_internal/ffmpeg目录
    try:
        ffmpeg_exe_source = os.path.join('ffmpeg', 'ffmpeg.exe')
        ffprobe_exe_source = os.path.join('ffmpeg', 'ffprobe.exe')
        
        if os.path.exists(ffmpeg_exe_source):
            shutil.copy2(ffmpeg_exe_source, os.path.join(ffmpeg_dir, 'ffmpeg.exe'))
            logger.info(f"Copied ffmpeg.exe to {ffmpeg_dir}")
        else:
            logger.warning(f"ffmpeg.exe not found at {ffmpeg_exe_source}")
        
        if os.path.exists(ffprobe_exe_source):
            shutil.copy2(ffprobe_exe_source, os.path.join(ffmpeg_dir, 'ffprobe.exe'))
            logger.info(f"Copied ffprobe.exe to {ffmpeg_dir}")
        else:
            logger.warning(f"ffprobe.exe not found at {ffprobe_exe_source}")
    except Exception as e:
        logger.error(f"Failed to copy ffmpeg files: {e}")
    
    # 获取Python安装目录和site-packages目录
    python_dir = os.path.dirname(sys.executable)
    try:
        # 获取site-packages目录
        import site
        site_packages_dir = site.getsitepackages()[0]
    except:
        site_packages_dir = os.path.join(os.path.dirname(os.path.dirname(python_dir)), 'Lib', 'site-packages')
    
    # 指定要复制的DLL目录
    dll_dirs = [
        os.path.join(python_dir, 'Library', 'bin'),
        os.path.join(python_dir, 'DLLs'),
        # PyQt5相关DLL
        os.path.join(site_packages_dir, 'PyQt5', 'Qt5', 'bin'),
        # 添加系统DLL目录
        os.environ.get('SystemRoot', '') + '\\System32',
    ]
    
    # 指定要复制的DLL文件（仅必要的VC++运行时和PyQt5核心DLL）
    # 精简DLL列表，仅包含最核心的必要组件
    dll_patterns = [
        'msvcp140.dll',
        'msvcp140_1.dll',
        'Qt5Core.dll',
        'Qt5Gui.dll',
        'Qt5Widgets.dll',
    ]
    
    # 设置目标目录
    target_dir = os.path.join('dist', 'Sora2WatermarkRemover')
    
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        logger.warning(f"Target directory {target_dir} does not exist. Creating...")
        os.makedirs(target_dir, exist_ok=True)
    
    # 复制DLL文件 - 最小化版本
    copied_dlls = []
    
    # 只在PyInstaller没有自动包含的情况下复制DLL
    for dll_dir in dll_dirs:
        if not os.path.exists(dll_dir):
            logger.warning(f"DLL directory {dll_dir} does not exist")
            continue
        
        for dll_pattern in dll_patterns:
            dll_path = os.path.join(dll_dir, dll_pattern)
            if os.path.exists(dll_path):
                try:
                    target_path = os.path.join(target_dir, dll_pattern)
                    if not os.path.exists(target_path):
                        shutil.copy2(dll_path, target_dir)
                        copied_dlls.append(dll_pattern)
                        logger.info(f"Copied {dll_pattern} to {target_dir}")
                    else:
                        logger.info(f"{dll_pattern} already exists in {target_dir}, skipping")
                except Exception as e:
                    logger.error(f"Failed to copy {dll_pattern}: {e}")
    
    # 增加清理步骤，移除不必要的大型文件，特别是CUDA相关文件
    logger.info("Cleaning up unnecessary large files, especially CUDA-related files...")
    cleanup_patterns = [
        '*.pyc',  # Python编译文件（已打包到exe中）
        '*.pyx',  # Cython源文件
        '*.h',    # 头文件
        '*.cpp',  # C++源文件
        '*.cc',   # C++源文件
        '*.c',    # C源文件
        '*.o',    # 目标文件
        '*.a',    # 静态库
        '*.pdb',  # 调试符号文件
        'test_*.py',  # 测试文件
        '__pycache__',  # Python缓存目录
    ]
    
    # 大型CUDA相关文件，这是体积的主要来源，但谨慎删除以避免依赖问题
    cuda_files_to_remove = [
        'cublas*',
        'cufft*',
        'cudnn*',
        'cusparse*',
        'torch_cuda*',
        'nvrtc*',
    ]
    
    # 为了解决shm.dll依赖问题，暂时禁用所有文件清理
    # 确保所有PyTorch依赖都被完整保留
    all_cleanup_patterns = []
    
    # 暂时禁用文件清理逻辑，确保所有依赖都被保留
    logger.info("File cleanup temporarily disabled to ensure all dependencies are preserved")
    # 跳过清理循环
    pass
    
    # 特别处理：移除重复的torch_cpu.dll文件，但保留一个副本
    logger.info("Checking for duplicate torch_cpu.dll files...")
    torch_cpu_paths = []
    for root, _, files in os.walk(target_dir):
        for file_name in files:
            if file_name == 'torch_cpu.dll':
                torch_cpu_paths.append(os.path.join(root, file_name))
    
    # 如果找到多个torch_cpu.dll文件，只保留一个
    if len(torch_cpu_paths) > 1:
        logger.info(f"Found {len(torch_cpu_paths)} torch_cpu.dll files, keeping only one")
        # 保留第一个，删除其余的
        for path in torch_cpu_paths[1:]:
            try:
                os.remove(path)
                logger.info(f"Removed duplicate torch_cpu.dll: {path}")
            except Exception as e:
                logger.warning(f"Failed to remove duplicate torch_cpu.dll {path}: {e}")
    
    # 仅复制特定的Qt5相关DLL，而不是全部
    qt5_bin_dir = os.path.join(os.path.dirname(os.path.dirname(python_dir)), 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'bin')
    if os.path.exists(qt5_bin_dir):
        # 只复制必要的Qt5插件和额外模块
        essential_qt_components = ['Qt5Network.dll', 'Qt5Svg.dll']
        
        for component in essential_qt_components:
            dll_path = os.path.join(qt5_bin_dir, component)
            if os.path.exists(dll_path):
                target_path = os.path.join(target_dir, component)
                if not os.path.exists(target_path):
                    try:
                        shutil.copy2(dll_path, target_dir)
                        copied_dlls.append(component)
                        logger.info(f"Copied essential Qt5 component: {component}")
                    except Exception as e:
                        logger.error(f"Failed to copy {component}: {e}")
    
    # 尝试复制PyTorch DLLs - 最小化版本，只复制绝对必要的组件
    try:
        torch_path, torch_lib_path = get_torch_paths()
        if torch_path and os.path.exists(torch_lib_path):
            # 最小化PyTorch DLL列表，只复制运行时必需的核心组件
            pytorch_core_dlls = ['torch_cpu.dll', 'torch_python.dll']
            
            # 仅复制最核心的PyTorch DLL
            for dll in pytorch_core_dlls:
                source_path = os.path.join(torch_lib_path, dll)
                if os.path.exists(source_path):
                    target_path = os.path.join(target_dir, dll)
                    if not os.path.exists(target_path):
                        try:
                            shutil.copy2(source_path, target_path)
                            copied_dlls.append(dll)
                            logger.info(f"Copied essential PyTorch DLL {dll} to {target_dir}")
                        except Exception as e:
                            logger.error(f"Failed to copy PyTorch core DLL {dll}: {e}")
            
            # 仅在需要时复制c10.dll
            c10_path = os.path.join(torch_lib_path, 'c10.dll')
            if os.path.exists(c10_path) and not os.path.exists(os.path.join(target_dir, 'c10.dll')):
                try:
                    shutil.copy2(c10_path, os.path.join(target_dir, 'c10.dll'))
                    copied_dlls.append('c10.dll')
                    logger.info("Copied c10.dll to target directory")
                except Exception as e:
                    logger.error(f"Failed to copy c10.dll: {e}")
    except Exception as e:
        logger.warning(f"Failed to copy PyTorch DLLs: {e}")
    
    # 创建一个启动脚本，在运行主程序前设置正确的环境变量，增强Windows 7兼容性
    launch_script_path = os.path.join(target_dir, 'launch_v2.bat')
    launch_script_content = f'''
@echo off
REM 设置当前目录和相关子目录到PATH，确保DLL能被正确找到
set PATH=%~dp0;%~dp0_internal\ffmpeg;%PATH%

REM 设置PYTHONPATH，确保Python模块能被正确找到
set PYTHONPATH=%~dp0;%PYTHONPATH%

REM 检测操作系统版本
ver | findstr /i "6.1">nul
if %errorlevel%==0 goto win7

REM Windows 10/11启动
:win10
REM 启动应用程序
echo Starting Sora2WatermarkRemover on Windows 10/11...
"%~dp0Sora2WatermarkRemover.exe"
goto end

REM Windows 7特殊启动设置
:win7
echo Starting Sora2WatermarkRemover on Windows 7...
REM 增加Windows 7兼容性设置
set __COMPAT_LAYER=WIN7RTM
"%~dp0Sora2WatermarkRemover.exe"

:end
'''
    
    try:
        with open(launch_script_path, 'w', encoding='utf-8') as f:
            f.write(launch_script_content)
        logger.info(f"Created launch script at {launch_script_path}")
    except Exception as e:
        logger.error(f"Failed to create launch script: {e}")
    
    # 创建一个README文件，说明如何正确运行程序，增加Windows 7兼容性说明
    readme_path = os.path.join(target_dir, 'README_V2.txt')
    readme_content = '''
Sora2WatermarkRemover 使用说明

兼容性：
本程序支持在 Windows 7、Windows 10 和 Windows 11 系统上运行。

使用方法：
1. 请使用 launch_v2.bat 脚本启动程序，它会自动检测操作系统版本并设置正确的环境变量
2. 程序已内置FFmpeg，无需单独安装
3. 在Windows 7系统上，程序会自动启用兼容模式

系统要求：
- Windows 7 SP1/Windows 10/Windows 11
- 建议4GB以上内存
- 支持CPU处理，有GPU可加速处理速度（Windows 10/11）

故障排除：
- 如果在Windows 7上运行失败，请确保已安装所有Windows更新和Service Pack
- 如遇VC++运行时错误，请下载并安装Microsoft Visual C++ Redistributable 2015-2022
- 如遇内存不足错误，请关闭其他应用程序后重试
'''
    
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.info(f"Created README at {readme_path}")
    except Exception as e:
        logger.error(f"Failed to create README: {e}")
    
    # 记录结果
    if copied_dlls:
        logger.info(f"Successfully copied {len(copied_dlls)} DLLs")
    else:
        logger.warning("No DLLs were copied")
    
    return len(copied_dlls) > 0

def build_with_pyinstaller():
    """Run PyInstaller with proper configuration for desktop.py with Windows 7/10/11 compatibility"""
    logger.info("Building with PyInstaller for desktop.py with Windows 7/10/11 compatibility...")
    
    # 设置PyInstaller命令，采用更简单的配置，确保依赖完整
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=Sora2WatermarkRemover",  # V2版本命名
        "--console",  # 显示控制台窗口以便调试
        "--onedir",     # 创建一个目录而不是单个文件
        "--clean",      # 清理缓存
        "--distpath=dist",
        "--workpath=build",
        "--specpath=.",
        # 使用优化但不过度优化
        "--optimize=1",  # 降低优化级别，避免文档字符串处理问题
        # 关键：确保所有依赖完整收集
        "--collect-all=torch",  # 收集所有PyTorch相关文件
        "--collect-all=sora2wm",  # 收集所有sora2wm相关文件
        "--collect-all=PyQt5",  # 基本的PyQt5依赖
        "--collect-all=transformers",  # 确保transformers库被完整收集
        "--collect-all=pydantic",  # 确保pydantic库被完整收集
        # 必要的隐藏导入
        "--hidden-import=sora2wm.core",
        "--hidden-import=sora2wm.watermark_Remover",
        "--hidden-import=sora2wm.watermark_detector",
        "--hidden-import=transformers.models.clip.modeling_clip",
        "--hidden-import=transformers.modeling_layers",
        # 确保中文正常显示
        "--noconfirm",
        "desktop.py"  # 直接使用desktop.py作为入口点
    ]
    
    # 执行PyInstaller命令
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        logger.info("PyInstaller build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"PyInstaller build failed: {e}")
        return False

def main():
    """Main function to run the build process for desktop.py with Windows 7/10/11 compatibility"""
    print("Starting build process for Sora2WatermarkRemover (desktop.py) with Windows 7/10/11 compatibility...")
    
    # Step 1: 清理之前的构建目录
    print("Cleaning previous build directories...")
    for dir_path in ['dist/Sora2WatermarkRemover', 'build']:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Removed {dir_path}")
            except Exception as e:
                print(f"Warning: Failed to remove {dir_path}: {e}")
    
    # Step 2: 使用PyInstaller构建应用
    print("Building with PyInstaller with Windows 7/10/11 compatibility options...")
    if not build_with_pyinstaller():
        print("Failed to build with PyInstaller!")
        return False
    
    # Step 3: 复制所有必要的DLL（PyQt5、VC++运行时、PyTorch等）
    print("Copying necessary DLLs for Windows 7/10/11 compatibility...")
    if not copy_dlls():
        print("Warning: No DLLs were copied, application may not work correctly")
    
    # Step 4: 确保_ffmpeg目录权限正确
    ffmpeg_dir = os.path.join('dist', 'Sora2WatermarkRemover', '_internal', 'ffmpeg')
    if os.path.exists(ffmpeg_dir):
        print(f"Ensuring proper permissions for {ffmpeg_dir}")
        # 在Windows上确保执行权限
        try:
            for exe_file in ['ffmpeg.exe', 'ffprobe.exe']:
                exe_path = os.path.join(ffmpeg_dir, exe_file)
                if os.path.exists(exe_path):
                    # 在Windows上设置文件属性为非只读
                    os.chmod(exe_path, 0o755)  # 设置执行权限
        except Exception as e:
            print(f"Warning: Failed to set permissions for ffmpeg files: {e}")
    
    print("Build process completed successfully with Windows 7/10/11 compatibility support!")
    print("Executable created at: dist/Sora2WatermarkRemover/Sora2WatermarkRemover.exe")
    print("Please use launch_v2.bat to start the application for proper environment setup.")
    
    return True

if __name__ == '__main__':
    if not main():
        sys.exit(1)
    sys.exit(0)