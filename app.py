"""
Sora2水印清除器主应用

这是一个基于Streamlit的Web应用，提供用户友好的界面来移除Sora2生成视频中的水印
"""

import shutil
import tempfile
from pathlib import Path

import streamlit as st

from sora2wm.core import Sora2WM  # 导入水印清除核心类


def main():
    """
    主函数，创建Streamlit Web应用界面
    
    实现功能：
    - 配置页面标题和图标
    - 加载AI模型
    - 提供文件上传和视频处理功能
    - 显示处理进度和结果
    - 提供下载选项
    """
    # 设置页面配置，包括标题、图标和布局
    st.set_page_config(
        page_title="Sora2水印清除器", page_icon="🎬", layout="centered"
    )

    st.title("🎬 Sora2水印清除器")
    st.markdown("轻松移除Sora2生成视频中的水印")

    # 初始化Sora2WM模型（使用session_state确保模型只加载一次）
    if "Sora2_wm" not in st.session_state:
        with st.spinner("加载AI模型中..."):
            # 创建并缓存水印清除器实例
            st.session_state.Sora2_wm = Sora2WM()

    st.markdown("---")

    # 文件上传组件
    uploaded_file = st.file_uploader(
        "上传您的视频",
        type=["mp4", "avi", "mov", "mkv"],
        help="选择一个视频文件来移除水印",
    )

    if uploaded_file is not None:
        # 显示已上传视频的信息和预览
        st.success(f"✅ 已上传: {uploaded_file.name}")
        st.video(uploaded_file)

        # 处理按钮
        if st.button("🚀 移除水印", type="primary", use_container_width=True):
            # 创建临时目录用于文件处理
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)

                # 保存上传的文件
                input_path = tmp_path / uploaded_file.name
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.read())

                # 定义输出文件路径
                output_path = tmp_path / f"cleaned_{uploaded_file.name}"

                try:
                    # 创建进度条和状态文本显示
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def update_progress(progress: int):
                        """更新进度条和状态文本"""
                        progress_bar.progress(progress / 100)
                        if progress < 50:
                            status_text.text(f"🔍 检测水印中... {progress}%")
                        elif progress < 95:
                            status_text.text(f"🧹 移除水印中... {progress}%")
                        else:
                            status_text.text(f"🎵 合并音频中... {progress}%")

                    # 运行水印移除处理，传入进度回调函数
                    # 此过程可能需要较长时间，取决于视频大小和计算机性能
                    st.session_state.Sora2_wm.run(
                        input_path, output_path, progress_callback=update_progress
                    )

                    # 完成进度条
                    progress_bar.progress(100)
                    status_text.text("✅ 处理完成!")

                    st.success("✅ 水印已成功移除!")

                    # 显示结果
                    st.markdown("### 结果")
                    st.video(str(output_path))

                    # 下载按钮
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="⬇️ 下载清除后的视频",
                            data=f,
                            file_name=f"cleaned_{uploaded_file.name}",
                            mime="video/mp4",
                            use_container_width=True,
                        )

                except Exception as e:
                    st.error(f"❌ 处理视频时出错: {str(e)}")

    # 页脚
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>使用 Streamlit 和 AI 制作 ❤️</p>
            <p><a href='https://github.com/linkedlist771/Sora2WatermarkRemover'>GitHub 仓库</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    # 程序入口点
    main()
