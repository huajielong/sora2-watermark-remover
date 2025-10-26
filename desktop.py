"""
Sora2水印清除器桌面应用

这是一个基于PyQt5的桌面GUI应用，提供用户友好的界面来移除Sora2生成视频中的水印
功能与Web版本相同，包括视频选择、预览、水印移除和结果保存
"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QMessageBox,
    QFrame, QSizePolicy, QLineEdit, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal


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
        self.input_path = None  # 当前处理的视频路径
        self.output_path = None  # 输出目录
        self.video_queue = []  # 视频处理队列
        self.current_video_index = 0  # 当前处理视频索引
        self.current_output_path = None  # 当前视频输出路径


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
        
        subtitle_label = QLabel("一键批量轻松移除Sora2水印")
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
        
        # 输出路径选择
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.select_output_directory)
        output_layout = QHBoxLayout()
        output_label = QLabel("输出路径:")
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.browse_btn)
        main_layout.addLayout(output_layout)

        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        
        # 创建输入视频预览区域
        self.video_list_widget = QListWidget()
        self.video_list_widget.setMinimumHeight(300)
        self.video_list_widget.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.video_list_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.video_list_widget.addItem("未选择视频文件")
        main_layout.addWidget(self.video_list_widget)
        
        # 创建移除水印按钮
        self.process_button = QPushButton("🚀 移除水印")
        self.process_button.setFont(QFont("SimHei", 14, QFont.Bold))
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_video)
        main_layout.addWidget(self.process_button)
        
        # 创建总进度标签
        self.total_progress_label = QLabel("总进度: 0/0")
        self.total_progress_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.total_progress_label)
        
        # 创建进度条和状态文本
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
    
    def find_common_path(self, paths):
        """查找多个路径的公共目录"""
        if not paths:
            return None
        
        # 从第一个路径开始
        common_path = paths[0].parent
        
        for path in paths[1:]:
            # 比较当前公共路径和下一个路径的父目录
            while not path.parent.is_relative_to(common_path):
                common_path = common_path.parent
                
                # 如果已经到达根目录，停止查找
                if common_path == common_path.parent:
                    return None
        
        return common_path

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_path = Path(directory)
            self.output_path_edit.setText(directory)
    
    def select_video(self):
        """选择视频文件"""
        # 打开文件对话框，支持多选
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件", "", 
            "视频文件 (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_paths:
            # 转换为Path对象列表
            self.video_queue = [Path(fp) for fp in file_paths]
            self.current_video_index = 0
            
            # 找出公共路径
            common_path = self.find_common_path(self.video_queue)
            
            if common_path:
                self.output_path = common_path
            else:
                # 没有公共路径，使用最后一个视频的路径
                self.output_path = self.video_queue[-1].parent
                QMessageBox.information(
                    self, "提示", 
                    f"未找到公共输出路径，已默认使用最后一个视频的路径：\n{self.output_path}"
                )
            
            self.output_path_edit.setText(str(self.output_path))
            
            # 显示选中的视频文件列表
            self.video_list_widget.clear()
            for video_path in self.video_queue:
                display_path = self.truncate_path(str(video_path))
                item = QListWidgetItem(display_path)
                item.setData(Qt.UserRole, str(video_path))  # 存储完整路径
                self.video_list_widget.addItem(item)
            
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
        """开始处理视频队列"""
        if not self.video_queue or not self.Sora2_wm:
            return
        
        # 禁用按钮，显示进度条
        self.process_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # 更新总进度标签
        self.update_total_progress()
        
        # 开始处理第一个视频
        self.process_next_video()
    
    def update_progress(self, progress):
        """更新进度条和状态文本"""
        self.progress_bar.setValue(progress)
        
        if progress < 50:
            self.status_label.setText(f"🔍 检测水印中...")
        elif progress < 95:
            self.status_label.setText(f"🧹 移除水印中...")
        else:
            self.status_label.setText(f"🎵 合并音频中...")
    
    def truncate_path(self, path, max_length=50):
        """截断过长路径，保留文件名，中间用...代替"""
        if len(path) <= max_length:
            return path
        
        path_obj = Path(path)
        filename = path_obj.name
        parent_path = str(path_obj.parent)
        
        # 计算需要保留的父路径长度
        available_length = max_length - len(filename) - 3  # 3 是 "..." 的长度
        if available_length <= 0:
            return filename  # 如果文件名本身就很长，只显示文件名
        
        return f"{parent_path[:available_length]}...{filename}"

    def process_next_video(self):
        """处理队列中的下一个视频"""
        if self.current_video_index >= len(self.video_queue):
            # 所有视频处理完成
            self.all_videos_processed()
            return
        
        # 获取当前要处理的视频
        self.input_path = self.video_queue[self.current_video_index]
        
        # 设置输出文件路径
        output_filename = f"{self.input_path.stem}_cleaned{self.input_path.suffix}"
        self.current_output_path = self.output_path / output_filename
        
        # 更新状态标签
        self.status_label.setText(
            f"正在处理: {self.input_path.name}\n🔍 检测水印中..."
        )
        self.status_label.setVisible(True)
        
        # 创建并启动处理线程
        self.processing_thread = ProcessingThread(
            self.Sora2_wm, self.input_path, self.current_output_path
        )
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.finished.connect(self.video_processed)
        self.processing_thread.error.connect(self.processing_error)
        self.processing_thread.start()



    def video_processed(self, output_path):
        """单个视频处理完成"""
        # 更新当前视频索引
        self.current_video_index += 1
        
        # 高亮已处理完成的视频
        if self.current_video_index - 1 < self.video_list_widget.count():
            item = self.video_list_widget.item(self.current_video_index - 1)
            if item:
                item.setForeground(QColor('#87CEEB'))  # 浅蓝色
        
        # 更新总进度
        self.update_total_progress()
        
        # 处理下一个视频
        self.process_next_video()

    def all_videos_processed(self):
        """所有视频处理完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✅ 所有 {len(self.video_queue)} 个视频处理完成!")
        
        # 启用处理按钮
        self.process_button.setEnabled(True)

    def update_total_progress(self):
        """更新总进度显示"""
        total = len(self.video_queue)
        processed = self.current_video_index
        self.total_progress_label.setText(f"总进度: {processed}/{total}")
        
    def processing_error(self, error_message):
        """处理出错时的回调函数"""
        # 更新UI状态
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.process_button.setEnabled(True)
        
        # 显示错误消息
        QMessageBox.critical(
            self, "处理失败", 
            f"处理视频时出错: {error_message}"
        )
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
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