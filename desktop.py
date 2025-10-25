"""
Sora2水印清除器桌面应用

这是一个基于PyQt5的桌面GUI应用，提供用户友好的界面来移除Sora2生成视频中的水印
功能与Web版本相同，包括视频选择、预览、水印移除和结果保存
"""

import sys
import os
import tempfile
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from sora2wm.core import Sora2WM  # 导入水印清除核心类


class ProcessingThread(QThread):
    """
    处理线程类，用于在后台运行水印移除任务
    避免UI界面在处理过程中冻结
    """
    progress_update = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, Sora2_wm, input_path, output_path):
        super().__init__()
        self.Sora2_wm = Sora2_wm
        self.input_path = input_path
        self.output_path = output_path
    
    def run(self):
        """线程运行函数，执行水印移除处理"""
        try:
            # 定义进度回调函数
            def update_progress(progress: int):
                self.progress_update.emit(progress)
            
            # 运行水印移除处理
            self.Sora2_wm.run(
                self.input_path, self.output_path, 
                progress_callback=update_progress
            )
            
            # 处理完成，发送信号
            self.finished.emit(str(self.output_path))
        except Exception as e:
            # 发生错误，发送错误信号
            self.error.emit(str(e))


class Sora2WatermarkRemoverGUI(QMainWindow):
    """
    Sora2水印清除器主窗口类
    实现整个GUI界面和用户交互逻辑
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.Sora2_wm = None  # Sora2WM实例
        self.input_path = None  # 输入视频路径
        self.output_path = None  # 输出视频路径
        self.tmp_dir = None  # 临时目录
        self.processing_thread = None  # 处理线程
    
    def init_ui(self):
        """初始化UI界面"""
        # 设置窗口标题和大小
        self.setWindowTitle("Sora2水印清除器")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建标题标签
        title_label = QLabel("🎬 Sora2水印清除器")
        title_label.setFont(QFont("SimHei", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("轻松移除Sora2生成视频中的水印")
        subtitle_label.setFont(QFont("SimHei", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 创建视频选择按钮
        select_button = QPushButton("📁 选择视频文件")
        select_button.setFont(QFont("SimHei", 12))
        select_button.clicked.connect(self.select_video)
        main_layout.addWidget(select_button)
        
        # 创建输入视频预览区域
        self.input_video_label = QLabel("未选择视频文件")
        self.input_video_label.setAlignment(Qt.AlignCenter)
        self.input_video_label.setMinimumHeight(300)
        self.input_video_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        main_layout.addWidget(self.input_video_label)
        
        # 创建移除水印按钮
        self.process_button = QPushButton("🚀 移除水印")
        self.process_button.setFont(QFont("SimHei", 14, QFont.Bold))
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_video)
        main_layout.addWidget(self.process_button)
        
        # 创建进度条和状态文本
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
        
        # 创建处理结果区域
        result_group = QVBoxLayout()
        result_title = QLabel("处理结果")
        result_title.setFont(QFont("SimHei", 16, QFont.Bold))
        result_group.addWidget(result_title)
        
        self.result_video_label = QLabel("处理后的视频将在这里显示")
        self.result_video_label.setAlignment(Qt.AlignCenter)
        self.result_video_label.setMinimumHeight(300)
        self.result_video_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        result_group.addWidget(self.result_video_label)
        
        self.save_button = QPushButton("💾 保存清除后的视频")
        self.save_button.setFont(QFont("SimHei", 12))
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_result)
        result_group.addWidget(self.save_button)
        
        main_layout.addLayout(result_group)
        
        # 创建底部信息
        footer_label = QLabel("使用 PyQt5 和 AI 制作 ❤️")
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)
    
    def select_video(self):
        """选择视频文件"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            self.input_path = Path(file_path)
            self.input_video_label.setText(f"已选择: {self.input_path.name}")
            
            # 显示视频基本信息
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
            self.input_video_label.setText(
                f"已选择: {self.input_path.name}\n文件大小: {file_size:.2f} MB"
            )
            
            # 启用处理按钮
            self.process_button.setEnabled(True)
            
            # 如果还没有初始化Sora2WM，则初始化
            if self.Sora2_wm is None:
                self.initialize_Sora2_wm()
    
    def initialize_Sora2_wm(self):
        """初始化Sora2WM模型"""
        try:
            # 显示加载提示
            self.status_label.setText("正在加载AI模型，请稍候...")
            self.status_label.setVisible(True)
            QApplication.processEvents()
            
            # 初始化水印清除器
            self.Sora2_wm = Sora2WM()
            
            # 隐藏加载提示
            self.status_label.setVisible(False)
            
            QMessageBox.information(
                self, "模型加载完成", 
                "AI模型已成功加载，可以开始处理视频了！"
            )
        except Exception as e:
            self.status_label.setVisible(False)
            QMessageBox.critical(
                self, "模型加载失败", 
                f"无法加载AI模型: {str(e)}"
            )
    
    def process_video(self):
        """处理视频，移除水印"""
        if not self.input_path or not self.Sora2_wm:
            return
        
        # 创建临时目录
        self.tmp_dir = tempfile.TemporaryDirectory()
        tmp_path = Path(self.tmp_dir.name)
        
        # 设置输出文件路径
        output_filename = f"cleaned_{self.input_path.name}"
        self.output_path = tmp_path / output_filename
        
        # 禁用按钮，显示进度条
        self.process_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("🔍 检测水印中... 0%")
        self.status_label.setVisible(True)
        
        # 创建并启动处理线程
        self.processing_thread = ProcessingThread(
            self.Sora2_wm, self.input_path, self.output_path
        )
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.finished.connect(self.processing_finished)
        self.processing_thread.error.connect(self.processing_error)
        self.processing_thread.start()
    
    def update_progress(self, progress):
        """更新进度条和状态文本"""
        self.progress_bar.setValue(progress)
        
        if progress < 50:
            self.status_label.setText(f"🔍 检测水印中... {progress}%")
        elif progress < 95:
            self.status_label.setText(f"🧹 移除水印中... {progress}%")
        else:
            self.status_label.setText(f"🎵 合并音频中... {progress}%")
    
    def processing_finished(self, output_path):
        """处理完成时的回调函数"""
        # 更新UI状态
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ 处理完成!")
        
        # 更新结果显示
        self.result_video_label.setText(f"处理完成: {Path(output_path).name}")
        
        # 启用保存按钮
        self.save_button.setEnabled(True)
        
        # 显示成功消息
        QMessageBox.information(
            self, "处理完成", 
            "视频水印已成功移除！请点击保存按钮保存结果。"
        )
    
    def processing_error(self, error_message):
        """处理出错时的回调函数"""
        # 清理临时目录
        if self.tmp_dir:
            self.tmp_dir.cleanup()
            self.tmp_dir = None
        
        # 更新UI状态
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.process_button.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(
            self, "处理失败", 
            f"处理视频时出错: {error_message}"
        )
    
    def save_result(self):
        """保存处理后的视频"""
        if not self.output_path or not self.output_path.exists():
            QMessageBox.warning(
                self, "保存失败", 
                "没有找到处理后的视频文件！"
            )
            return
        
        # 获取保存路径
        default_filename = f"cleaned_{self.input_path.name}"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存视频文件", default_filename, 
            "视频文件 (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if save_path:
            try:
                # 复制文件
                import shutil
                shutil.copy2(self.output_path, save_path)
                
                QMessageBox.information(
                    self, "保存成功", 
                    f"视频已成功保存到: {save_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "保存失败", 
                    f"保存视频时出错: {str(e)}"
                )
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        # 清理临时目录
        if self.tmp_dir:
            self.tmp_dir.cleanup()
        
        # 停止处理线程
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait()
        
        event.accept()


def main():
    """主函数，创建应用实例"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    window = Sora2WatermarkRemoverGUI()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    # 程序入口点
    main()