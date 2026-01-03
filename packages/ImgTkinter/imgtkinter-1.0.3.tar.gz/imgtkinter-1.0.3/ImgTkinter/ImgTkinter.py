import sys
import os
import shutil
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea, QGridLayout,
    QFrame, QFileDialog, QMessageBox, QProgressBar,
    QSplitter, QMenu, QAction, QToolButton, QHBoxLayout,
    QListWidget, QListWidgetItem, QAbstractItemView, QComboBox
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QPoint, QMimeData,
    QTimer, QSize, QEvent, QSettings
)
from PyQt5.QtGui import (
    QPixmap, QDrag, QPainter, QPen, QColor, QFont,
    QPainterPath, QBrush, QKeySequence
)
from pypinyin import lazy_pinyin


class ModernButton(QPushButton):
    """现代风格的按钮"""

    def __init__(self, text, parent=None, icon=None):
        super().__init__(text, parent)
        self.icon = icon
        self.setup_style()

    def setup_style(self):
        """设置按钮样式"""
        self.setMinimumHeight(34)
        self.setFont(QFont("Microsoft YaHei", 10))

        if self.icon:
            self.setText(f"{self.icon} {self.text()}")

        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
        """)


class SortButton(QWidget):
    """排序按钮组件"""
    sort_requested = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sort_ascending = True
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.sort_btn = QPushButton("🔄 排序⬆⬇")
        self.sort_btn.setMinimumHeight(34)
        self.sort_btn.setFont(QFont("Microsoft YaHei", 10))
        self.sort_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.sort_btn.clicked.connect(self.toggle_sort)

        self.direction_btn = QPushButton("⬇")
        self.direction_btn.setFixedSize(34, 34)
        self.direction_btn.setFont(QFont("Microsoft YaHei", 12))
        self.direction_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.direction_btn.clicked.connect(self.toggle_sort)

        layout.addWidget(self.sort_btn)

    def toggle_sort(self):
        """切换排序方向"""
        self.sort_ascending = not self.sort_ascending
        if self.sort_ascending:
            self.direction_btn.setText("⬆")
        else:
            self.direction_btn.setText("⬇")
        self.sort_requested.emit(self.sort_ascending)


class ImageLoader(QThread):
    """图片加载线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()

    def __init__(self, image_paths, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.running = True

    def run(self):
        """执行图片加载"""
        total = len(self.image_paths)

        for i, image_path in enumerate(self.image_paths):
            if not self.running:
                break

            # 更新进度
            progress = int((i + 1) / total * 100)
            self.progress.emit(progress, f"正在加载图片... ({i + 1}/{total})")

            self.msleep(10)

        self.finished.emit()

    def stop(self):
        """停止加载"""
        self.running = False


class FolderIconLoader(QThread):
    """文件夹图标加载线程"""
    icon_loaded = pyqtSignal(str, QPixmap)

    def __init__(self, folder_paths, parent=None):
        super().__init__(parent)
        self.folder_paths = folder_paths
        self.running = True

    def run(self):
        """加载文件夹图标"""
        for folder_path in self.folder_paths:
            if not self.running:
                break

            image_path = self.find_first_image(folder_path)
            pixmap = None

            if image_path and os.path.exists(image_path):
                pixmap = self.load_image_icon(image_path)

            if pixmap and not pixmap.isNull():
                self.icon_loaded.emit(folder_path, pixmap)
            else:
                pixmap = self.create_default_icon()
                self.icon_loaded.emit(folder_path, pixmap)

            self.msleep(50)

    def find_first_image(self, folder_path):
        """查找文件夹中的第一张图片"""
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')

        try:
            if os.path.exists(folder_path):
                for file in sorted(os.listdir(folder_path)):
                    if file.lower().endswith(image_extensions):
                        return os.path.join(folder_path, file)
        except:
            pass
        return None

    def load_image_icon(self, image_path):
        """加载图片作为图标"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                return pixmap.scaled(70, 50, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        except:
            pass
        return None

    def create_default_icon(self):
        """创建默认图标"""
        pixmap = QPixmap(70, 50)
        pixmap.fill(Qt.transparent)
        return pixmap


class EnlargeImageWindow(QWidget):
    """放大图片窗口（使用紫色主题 #8B5CF6）"""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.init_ui()
        self.load_image()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("查看图片")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(800, 600)

        # 设置窗口样式 - 使用紫色主题
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
            }
            QPushButton {
                background-color: #8B5CF6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #7C3AED;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: #6D28D9;
            }
            QPushButton:disabled {
                background-color: #A78BFA;
                color: #DDD6FE;
            }
            QLabel {
                color: #E5E7EB;
            }
        """)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 图片显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1f1f1f;
                border-radius: 6px;
                border: 2px solid #8B5CF6;
            }
        """)
        layout.addWidget(self.image_label)

        # 控制栏
        control_layout = QHBoxLayout()

        # 缩放控制
        self.zoom_label = QLabel("缩放: 100%")
        self.zoom_label.setFont(QFont("Microsoft YaHei", 11))
        control_layout.addWidget(self.zoom_label)

        control_layout.addStretch()

        # 缩放按钮
        self.zoom_out_btn = QPushButton("➖ 缩小")
        self.zoom_out_btn.setFixedSize(80, 32)
        self.zoom_out_btn.clicked.connect(lambda: self.adjust_zoom(0.8))

        self.reset_zoom_btn = QPushButton("🔄 重置")
        self.reset_zoom_btn.setFixedSize(80, 32)
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)

        self.zoom_in_btn = QPushButton("➕ 放大")
        self.zoom_in_btn.setFixedSize(80, 32)
        self.zoom_in_btn.clicked.connect(lambda: self.adjust_zoom(1.2))

        control_layout.addWidget(self.zoom_out_btn)
        control_layout.addWidget(self.reset_zoom_btn)
        control_layout.addWidget(self.zoom_in_btn)

        layout.addLayout(control_layout)

        # 底部信息栏
        info_layout = QHBoxLayout()

        self.info_label = QLabel()
        self.info_label.setFont(QFont("Microsoft YaHei", 10))
        info_layout.addWidget(self.info_label)

        info_layout.addStretch()

        self.close_btn = QPushButton("❌ 关闭")
        self.close_btn.setFixedSize(80, 32)
        self.close_btn.clicked.connect(self.close)
        info_layout.addWidget(self.close_btn)

        layout.addLayout(info_layout)

        # 初始化变量
        self.original_pixmap = None
        self.current_scale = 1.0
        self.max_scale = 5.0
        self.min_scale = 0.1

    def load_image(self):
        """加载图片"""
        try:
            self.original_pixmap = QPixmap(self.image_path)
            if self.original_pixmap.isNull():
                self.show_error("无法加载图片")
                return

            # 显示图片信息
            info = f"📁 文件: {os.path.basename(self.image_path)} | "
            info += f"📏 尺寸: {self.original_pixmap.width()}x{self.original_pixmap.height()} | "
            info += f"💾 大小: {os.path.getsize(self.image_path) / 1024:.1f}KB"
            self.info_label.setText(info)

            # 初始缩放以适应窗口
            self.fit_to_window()

        except Exception as e:
            self.show_error(f"加载失败: {str(e)}")

    def show_error(self, message):
        """显示错误信息"""
        self.image_label.setText(f"❌ {message}")
        self.image_label.setStyleSheet("""
            QLabel {
                color: #FCA5A5;
                font-size: 14px;
                background-color: #1f1f1f;
                border-radius: 6px;
                border: 2px solid #EF4444;
            }
        """)

    def fit_to_window(self):
        """适应窗口大小"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        label_size = self.image_label.size()
        scaled_pixmap = self.original_pixmap.scaled(
            label_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.current_scale = scaled_pixmap.width() / self.original_pixmap.width()
        self.update_zoom_label()

    def adjust_zoom(self, factor):
        """调整缩放比例"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        new_scale = self.current_scale * factor

        if new_scale < self.min_scale or new_scale > self.max_scale:
            return

        self.current_scale = new_scale
        self.apply_zoom()

    def apply_zoom(self):
        """应用当前缩放比例"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        new_width = int(self.original_pixmap.width() * self.current_scale)
        new_height = int(self.original_pixmap.height() * self.current_scale)

        scaled_pixmap = self.original_pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.update_zoom_label()

    def update_zoom_label(self):
        """更新缩放标签"""
        percentage = int(self.current_scale * 100)
        self.zoom_label.setText(f"🔍 缩放: {percentage}%")

    def reset_zoom(self):
        """重置缩放"""
        self.current_scale = 1.0
        self.apply_zoom()

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        if self.current_scale == 1.0:
            self.fit_to_window()

    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        if event.angleDelta().y() > 0:
            self.adjust_zoom(1.1)
        else:
            self.adjust_zoom(0.9)
        event.accept()

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.adjust_zoom(1.1)
        elif event.key() == Qt.Key_Minus:
            self.adjust_zoom(0.9)
        elif event.key() == Qt.Key_0:
            self.reset_zoom()
        super().keyPressEvent(event)


class ImageItem(QFrame):
    """支持多选和右键删除的图片项"""
    selection_changed = pyqtSignal(str, bool)  # 新增：选中状态改变信号

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_selected = False
        self.is_hovered = False
        self.setup_ui()
        self.load_image()

    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.NoFrame)
        self.setFixedSize(120, 120)
        self.setCursor(Qt.PointingHandCursor)

        # 初始样式
        self.update_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)

        self.image_container = QLabel()
        self.image_container.setFixedSize(90, 70)
        self.image_container.setAlignment(Qt.AlignCenter)

        filename = os.path.basename(self.image_path)
        if len(filename) > 14:
            filename = filename[:11] + "..."

        self.name_label = QLabel(filename)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumWidth(100)

        layout.addWidget(self.image_container, 0, Qt.AlignCenter)
        layout.addWidget(self.name_label)

        # 选择标记（右上角）
        self.selection_mark = QLabel("✓")
        self.selection_mark.setFixedSize(18, 18)
        self.selection_mark.setAlignment(Qt.AlignCenter)
        self.selection_mark.setStyleSheet("""
            QLabel {
                background-color: #8B5CF6;
                color: white;
                border-radius: 9px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.selection_mark.move(92, 2)
        self.selection_mark.hide()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def update_style(self):
        """根据选中状态更新样式"""
        if self.is_selected:
            style = """
                QFrame {
                    background-color: #e8f4fd;
                    border-radius: 6px;
                    border: 2px solid #8B5CF6;
                    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
                }
            """
        elif self.is_hovered:
            style = """
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 6px;
                    border: 1px solid #8B5CF6;
                    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
                }
            """
        else:
            style = """
                QFrame {
                    background-color: white;
                    border-radius: 6px;
                    border: 1px solid #e0e0e0;
                }
            """

        self.setStyleSheet(style)

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)

        if not self.is_selected:
            select_action = QAction("✅ 选中", self)
            select_action.triggered.connect(lambda: self.select_item())
        else:
            select_action = QAction("❌ 取消选中", self)
            select_action.triggered.connect(lambda: self.deselect_item())
        menu.addAction(select_action)

        menu.addSeparator()

        # 删除图片 - 不再询问确认，直接删除
        delete_action = QAction("🗑️ 删除图片", self)
        delete_action.triggered.connect(self.delete_image)
        menu.addAction(delete_action)

        rename_action = QAction("✏ 重命名", self)
        rename_action.triggered.connect(self.rename_image)
        menu.addAction(rename_action)

        view_action = QAction("👁️ 查看图片", self)
        view_action.triggered.connect(self.show_enlarged_image)
        menu.addAction(view_action)

        copy_path_action = QAction("📋 复制路径", self)
        copy_path_action.triggered.connect(self.copy_path)
        menu.addAction(copy_path_action)

        menu.exec_(self.mapToGlobal(pos))

    def select_item(self):
        """选中图片"""
        if not self.is_selected:
            self.is_selected = True
            self.selection_mark.hide()  # 始终隐藏标记，只改变样式
            self.update_style()
            self.selection_changed.emit(self.image_path, True)

    def deselect_item(self):
        """取消选中图片"""
        if self.is_selected:
            self.is_selected = False
            self.selection_mark.hide()
            self.update_style()
            self.selection_changed.emit(self.image_path, False)

    def delete_image(self):
        """直接删除图片（不再弹出确认对话框）"""
        try:
            # 直接删除，不询问确认
            os.remove(self.image_path)
            # 先移除选中状态
            if self.is_selected:
                self.deselect_item()
            # 通知主窗口更新
            self.window().on_image_deleted(self.image_path)
            # 显示临时消息，但不弹窗
            # self.window().show_temp_message(f"已删除: {os.path.basename(self.image_path)}")
        except Exception as e:
            # 只在删除失败时显示错误
            QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")

    def rename_image(self):
        """重命名图片"""
        from PyQt5.QtWidgets import QInputDialog

        current_name = os.path.basename(self.image_path)
        new_name, ok = QInputDialog.getText(
            self,
            "重命名图片",
            "输入新的文件名:",
            text=current_name
        )

        if ok and new_name and new_name != current_name:
            try:
                if '.' not in new_name:
                    ext = os.path.splitext(current_name)[1]
                    new_name += ext

                new_path = os.path.join(os.path.dirname(self.image_path), new_name)

                if os.path.exists(new_path):
                    QMessageBox.warning(self, "警告", "文件已存在")
                    return

                # 先移除旧的选中状态
                if self.is_selected:
                    self.deselect_item()

                os.rename(self.image_path, new_path)
                self.image_path = new_path

                if len(new_name) > 14:
                    new_name = new_name[:11] + "..."
                self.name_label.setText(new_name)

                self.window().on_image_renamed(self.image_path, old_path=self.image_path)

            except Exception as e:
                QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")

    def show_enlarged_image(self):
        """显示放大后的图片"""
        try:
            self.enlarge_window = EnlargeImageWindow(self.image_path)
            self.enlarge_window.show()
        except Exception as e:
            print(f"放大图片失败: {e}")

    def copy_path(self):
        """复制文件路径"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.image_path)
        # self.window().show_temp_message("路径已复制到剪贴板")

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 只能通过Shift+单击选中或取消选中
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ShiftModifier:
                if self.is_selected:
                    self.deselect_item()  # Shift+单击已选中的图片取消选中
                else:
                    self.select_item()  # Shift+单击未选中的图片选中

            self.drag_start_position = event.pos()

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件 - 放大图片"""
        if event.button() == Qt.LeftButton:
            self.show_enlarged_image()

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_hovered = True
        self.update_style()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False
        self.update_style()

    def load_image(self):
        """加载图片"""
        try:
            pixmap = QPixmap(self.image_path)
            if pixmap.isNull():
                self.show_placeholder()
            else:
                scaled_pixmap = pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                rounded_pixmap = QPixmap(scaled_pixmap.size())
                rounded_pixmap.fill(Qt.transparent)

                painter = QPainter(rounded_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)

                path = QPainterPath()
                path.addRoundedRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height(), 4, 4)
                painter.setClipPath(path)

                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()

                self.image_container.setPixmap(rounded_pixmap)

        except Exception as e:
            print(f"加载图片失败 {self.image_path}: {e}")
            self.show_placeholder()

    def show_placeholder(self):
        """显示占位符"""
        pixmap = QPixmap(80, 60)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(248, 249, 250))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 80, 60, 4, 4)

        painter.setPen(QPen(QColor(139, 92, 246), 1))
        painter.setBrush(Qt.NoBrush)

        painter.drawRect(20, 15, 40, 25)
        painter.drawLine(22, 17, 32, 27)
        painter.drawLine(32, 17, 42, 27)

        painter.setPen(QColor(127, 140, 141))
        painter.setFont(QFont("Microsoft YaHei", 7))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "图片")

        painter.end()
        self.image_container.setPixmap(pixmap)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 支持多图拖拽"""
        if not (event.buttons() & Qt.LeftButton):
            return

        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # 获取所有选中的图片
        selected_images = self.window().get_selected_images()
        if not selected_images:
            # 如果没有选中的图片，只拖拽当前图片
            selected_images = [self.image_path]
            if not self.is_selected:
                self.select_item()  # 选中当前图片

        # 创建拖拽
        drag = QDrag(self)
        mime_data = QMimeData()

        # 设置拖拽数据（多文件路径用换行分隔）
        mime_data.setText('\n'.join(selected_images))

        # 创建预览图
        pixmap = self.image_container.pixmap().copy() if self.image_container.pixmap() else QPixmap()
        if not pixmap.isNull():
            preview = QPixmap(pixmap.size())
            preview.fill(Qt.transparent)

            painter = QPainter(preview)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setOpacity(0.8)

            # 如果有多个选中，添加计数标记
            if len(selected_images) > 1:
                painter.setBrush(QColor(139, 92, 246))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(preview.rect().topRight() - QPoint(15, 15), 12, 12)

                painter.setPen(QColor("white"))
                painter.setFont(QFont("Microsoft YaHei", 8, QFont.Bold))
                painter.drawText(preview.rect().adjusted(-15, -15, 0, 0),
                                 Qt.AlignRight | Qt.AlignTop, str(len(selected_images)))

            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(139, 92, 246, 200), 2))
            painter.drawRoundedRect(pixmap.rect(), 4, 4)

            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            drag.setPixmap(preview)
            drag.setHotSpot(event.pos() - self.image_container.pos())

        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction | Qt.MoveAction)


class FolderItem(QFrame):
    """优化后的文件夹项"""

    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.is_hovered = False
        self.drag_over = False
        self.file_count = 0
        self.setup_ui()
        self.setAcceptDrops(True)
        self.update_icon_and_count()

    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.NoFrame)
        self.setFixedSize(130, 130)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        self.icon_container = QLabel()
        self.icon_container.setFixedSize(90, 70)
        self.icon_container.setAlignment(Qt.AlignCenter)

        name_count_container = QFrame()
        name_count_container.setStyleSheet("background: transparent;")
        name_layout = QVBoxLayout(name_count_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(2)

        folder_name = os.path.basename(self.folder_path)
        if len(folder_name) > 12:
            folder_name = folder_name[:9] + "..."

        self.name_label = QLabel(folder_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumWidth(110)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 10px;
                font-weight: 600;
                padding: 2px;
            }
        """)

        self.count_label = QLabel("0 个文件")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setMaximumWidth(110)
        self.count_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 9px;
                font-weight: 500;
                padding: 1px;
                background-color: #e8f4fd;
                border-radius: 3px;
                border: 1px solid #bbdefb;
            }
        """)

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.count_label)

        layout.addWidget(self.icon_container, 0, Qt.AlignCenter)
        layout.addWidget(name_count_container)

        self.update_style()

    def update_icon_and_count(self):
        """异步更新文件夹图标和文件数量"""
        self.update_file_count()
        self.show_placeholder_icon()

        if hasattr(self.window(), 'request_folder_icon'):
            self.window().request_folder_icon(self.folder_path, self)

    def show_placeholder_icon(self):
        """显示占位符图标"""
        pixmap = QPixmap(70, 50)
        pixmap.fill(QColor(240, 240, 240))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor(180, 180, 180))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "加载中...")
        painter.end()

        self.icon_container.setPixmap(pixmap)

    def update_icon_with_pixmap(self, pixmap):
        """更新图标"""
        if not pixmap or pixmap.isNull():
            self.show_default_icon()
            return

        try:
            rounded_pixmap = QPixmap(70, 50)
            rounded_pixmap.fill(Qt.transparent)

            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            path = QPainterPath()
            path.addRoundedRect(0, 0, 70, 50, 3, 3)
            painter.setClipPath(path)

            x = (70 - pixmap.width()) // 2
            y = (50 - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)

            border_color = self.get_count_color()
            painter.setPen(QPen(border_color, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(0, 0, 70, 50, 3, 3)

            painter.end()

            self.icon_container.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border-radius: 3px;
                    border: 1px solid #e0e0e0;
                }
            """)
            self.icon_container.setPixmap(rounded_pixmap)

        except Exception as e:
            print(f"更新图标失败: {e}")
            self.show_default_icon()

    def update_file_count(self):
        """更新文件数量"""
        try:
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
            count = 0

            if os.path.exists(self.folder_path):
                for file in os.listdir(self.folder_path):
                    if file.lower().endswith(image_extensions):
                        count += 1

            self.file_count = count
            self.update_count_label()

        except Exception as e:
            print(f"更新文件数量失败: {e}")
            self.count_label.setText("无法访问")
            self.count_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 9px;
                    font-weight: 500;
                    padding: 1px;
                    background-color: #fdedec;
                    border-radius: 3px;
                    border: 1px solid #f1948a;
                }
            """)

    def update_count_label(self):
        """更新计数标签"""
        count = self.file_count

        if count == 0:
            self.count_label.setText("空文件夹")
        else:
            self.count_label.setText(f"{count} 个文件")

        if count == 0:
            color = "#95a5a6"
            bg_color = "#f8f9fa"
            border_color = "#e0e0e0"
        elif count < 5:
            bg_color = "#58d68d"
            border_color = "#bbdefb"
        elif count < 10:
            bg_color = "#7dcea0"
            border_color = "#a3e9c1"
        elif count < 20:
            bg_color = "#f39c12"
            border_color = "#a3e9c1"
        elif count < 50:
            bg_color = "#48c9b0"
            border_color = "#f8c471"
        elif count < 100:
            bg_color = "#5499c7"
            border_color = "#f5b041"
        elif count < 200:
            bg_color = "#ec7063"
            border_color = "#f1948a"
        elif count < 500:
            bg_color = "#cd6155"
            border_color = "#e74c3c"
        else:
            color = "#7d3c98"
            bg_color = "#f4ecf7"
            border_color = "#bb8fce"
        color = 'black'
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 9px;
                font-weight: 500;
                padding: 1px;
                background-color: {bg_color};
                border-radius: 3px;
                border: 1px solid {border_color};
            }}
        """)

    def get_count_color(self):
        """根据文件数量获取对应的颜色"""
        count = self.file_count

        if count == 0:
            return QColor(149, 165, 166)
        elif count < 5:
            return QColor(139, 92, 246)
        elif count < 10:
            return QColor(39, 174, 96)
        elif count < 20:
            return QColor(46, 204, 113)
        elif count < 50:
            return QColor(243, 156, 18)
        elif count < 100:
            return QColor(211, 84, 0)
        elif count < 200:
            return QColor(231, 76, 60)
        elif count < 500:
            return QColor(192, 57, 43)
        else:
            return QColor(125, 60, 152)

    def show_default_icon(self):
        """显示默认文件夹图标"""
        pixmap = QPixmap(70, 50)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        folder_color = self.get_count_color()
        bg_color = QColor(folder_color.red(), folder_color.green(), folder_color.blue(), 30)

        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 70, 50, 3, 3)

        painter.setPen(QPen(folder_color, 1.5))

        folder_path = QPainterPath()
        folder_path.moveTo(15, 20)
        folder_path.lineTo(25, 15)
        folder_path.lineTo(45, 15)
        folder_path.lineTo(55, 20)
        folder_path.lineTo(55, 40)
        folder_path.lineTo(15, 40)
        folder_path.closeSubpath()

        painter.setBrush(QColor(folder_color.red(), folder_color.green(), folder_color.blue(), 30))
        painter.drawPath(folder_path)

        painter.setBrush(QColor(folder_color.red(), folder_color.green(), folder_color.blue(), 100))
        painter.drawRect(20, 18, 10, 3)

        painter.end()

        self.icon_container.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border-radius: 3px;
                border: none;
            }
        """)
        self.icon_container.setPixmap(pixmap)

    def update_style(self):
        """更新样式"""
        if self.drag_over:
            style = """
                QFrame {
                    background-color: #e1f5fe;
                    border-radius: 6px;
                    border: 2px solid #29b6f6;
                }
            """
        elif self.is_hovered:
            style = """
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 6px;
                    border: 1px solid #8B5CF6;
                    box-shadow: 0 2px 6px rgba(139, 92, 246, 0.2);
                }
            """
        else:
            style = """
                QFrame {
                    background-color: white;
                    border-radius: 6px;
                    border: 1px solid #e0e0e0;
                }
            """

        self.setStyleSheet(style)

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_hovered = True
        self.update_style()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False
        self.update_style()

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            self.drag_over = True
            self.update_style()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.drag_over = False
        self.update_style()

    def dropEvent(self, event):
        """放置事件"""
        self.drag_over = False
        self.update_style()

        if event.mimeData().hasText():
            image_paths = event.mimeData().text().split('\n')
            valid_paths = [path for path in image_paths if os.path.exists(path)]

            if valid_paths:
                # 批量移动图片
                self.window().start_move_multiple_images(valid_paths, self.folder_path)
                QTimer.singleShot(500, self.update_icon_and_count)
                event.accept()
            else:
                event.ignore()


class FileMover(QThread):
    """文件移动线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, str, bool, str)

    def __init__(self, image_path, target_folder):
        super().__init__()
        self.image_path = image_path
        self.target_folder = target_folder

    def run(self):
        """执行文件移动"""
        try:
            filename = os.path.basename(self.image_path)
            self.progress.emit(10, f"准备移动 {filename}")

            os.makedirs(self.target_folder, exist_ok=True)
            target_path = os.path.join(self.target_folder, filename)

            counter = 1
            while os.path.exists(target_path):
                name, ext = os.path.splitext(filename)
                target_path = os.path.join(self.target_folder, f"{name}_{counter}{ext}")
                counter += 1

            self.progress.emit(30, "正在复制文件...")
            shutil.copy2(self.image_path, target_path)
            self.progress.emit(70, "复制完成")

            if os.path.exists(target_path):
                os.remove(self.image_path)
                self.progress.emit(100, "移动完成")
                self.finished.emit(self.image_path, target_path, True,
                                   f"已移动到 {os.path.basename(self.target_folder)}")
            else:
                self.finished.emit(self.image_path, "", False, "文件复制失败")

        except Exception as e:
            self.finished.emit(self.image_path, "", False, f"移动失败: {str(e)}")


class BatchFileMover(QThread):
    """批量文件移动线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, list, bool, str)

    def __init__(self, image_paths, target_folder):
        super().__init__()
        self.image_paths = image_paths
        self.target_folder = target_folder
        self.results = []

    def run(self):
        """执行批量文件移动"""
        try:
            total = len(self.image_paths)
            os.makedirs(self.target_folder, exist_ok=True)

            successful_moves = []
            failed_moves = []

            for i, image_path in enumerate(self.image_paths):
                try:
                    filename = os.path.basename(image_path)
                    progress = int((i + 1) / total * 100)
                    self.progress.emit(progress, f"正在移动文件 ({i + 1}/{total}): {filename}")

                    target_path = os.path.join(self.target_folder, filename)

                    # 处理重名文件
                    counter = 1
                    base_name, ext = os.path.splitext(filename)
                    while os.path.exists(target_path):
                        target_path = os.path.join(self.target_folder, f"{base_name}_{counter}{ext}")
                        counter += 1

                    # 复制文件
                    shutil.copy2(image_path, target_path)

                    # 删除源文件
                    if os.path.exists(target_path):
                        os.remove(image_path)
                        successful_moves.append((image_path, target_path))
                    else:
                        failed_moves.append((image_path, "复制失败"))

                except Exception as e:
                    failed_moves.append((image_path, str(e)))

            if failed_moves:
                message = f"成功移动 {len(successful_moves)} 个，失败 {len(failed_moves)} 个"
                self.finished.emit(successful_moves, failed_moves, False, message)
            else:
                message = f"成功移动 {len(successful_moves)} 个文件"
                self.finished.emit(successful_moves, failed_moves, True, message)

        except Exception as e:
            self.finished.emit([], [], False, f"批量移动失败: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.source_folder = ""
        self.target_folder = ""
        self.source_images = []
        self.image_widgets = {}
        self.folder_widgets = {}
        self.sort_ascending = True
        self.need_sort = False

        # 分页相关
        self.current_page = 1
        self.page_size = 200  # 每页显示200个图片
        self.total_pages = 1

        # 异步加载相关
        self.image_loader = None
        self.folder_icon_loader = None
        self.pending_icons = {}

        # 多选相关
        self.selected_images = set()

        # 设置对象用于保存配置
        self.settings = QSettings("ImgTkinter", "ImageClassifier")

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("图片分类工具")
        self.setGeometry(100, 100, 1400, 850)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        self.create_control_panel(main_layout)
        self.create_main_content(main_layout)
        self.setup_status_bar()

    def create_control_panel(self, parent_layout):
        """创建控制面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                padding: 12px;
            }
        """)

        layout = QHBoxLayout(panel)

        left_layout = QVBoxLayout()

        source_header = QLabel("源图片文件夹")
        source_header.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        source_header.setStyleSheet("color: #8B5CF6; margin-bottom: 6px;")

        source_control = QHBoxLayout()
        self.source_btn = ModernButton("📁 选择文件夹", icon="📁")
        self.source_btn.clicked.connect(self.select_source_folder)

        # 源文件夹历史记录下拉框
        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(250)
        self.source_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                color: #2c3e50;
                padding: 6px;
                font-size: 11px;
            }
            QComboBox:hover {
                border: 1px solid #8B5CF6;
            }
            QComboBox:focus {
                border: 2px solid #8B5CF6;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #bdc3c7;
                selection-background-color: #8B5CF6;
                selection-color: white;
            }
        """)
        self.source_combo.currentTextChanged.connect(self.on_source_combo_changed)

        self.refresh_btn = ModernButton("🔄 刷新加载", icon="🔄")
        self.refresh_btn.clicked.connect(self.refresh_source_images)
        self.refresh_btn.setEnabled(False)

        self.source_label = QLabel("未选择文件夹")
        self.source_label.setWordWrap(True)
        self.source_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                background-color: #f8f9fa;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.source_label.setMinimumWidth(250)

        self.source_count_label = QLabel("0 张图片")
        self.source_count_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 11px;
                padding: 8px;
            }
        """)

        source_control.addWidget(self.source_btn)
        source_control.addWidget(self.source_combo)
        source_control.addWidget(self.refresh_btn)
        source_control.addWidget(self.source_label, 1)
        source_control.addWidget(self.source_count_label)

        left_layout.addWidget(source_header)
        left_layout.addLayout(source_control)

        layout.addLayout(left_layout, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(separator)

        right_layout = QVBoxLayout()

        target_header = QLabel("目标分类文件夹")
        target_header.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        target_header.setStyleSheet("color: #8B5CF6; margin-bottom: 6px;")

        target_control = QHBoxLayout()
        self.target_btn = ModernButton("📂 选择文件夹", icon="📂")
        self.target_btn.clicked.connect(self.select_target_folder)

        # 目标文件夹历史记录下拉框
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(250)
        self.target_combo.setStyleSheet(self.source_combo.styleSheet())
        self.target_combo.currentTextChanged.connect(self.on_target_combo_changed)

        self.sort_btn = SortButton()
        self.sort_btn.sort_requested.connect(self.apply_sorting)
        self.sort_btn.setEnabled(False)

        self.target_label = QLabel("未选择文件夹")
        self.target_label.setWordWrap(True)
        self.target_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                background-color: #f8f9fa;
                border-radius: 3px;
                padding: 8px;
                font-size: 11px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.target_label.setMinimumWidth(250)

        target_control.addWidget(self.target_btn)
        target_control.addWidget(self.target_combo)
        target_control.addWidget(self.sort_btn)
        target_control.addWidget(self.target_label, 1)

        right_layout.addWidget(target_header)
        right_layout.addLayout(target_control)

        new_folder_layout = QHBoxLayout()
        new_folder_layout.addWidget(QLabel("新建文件夹:"))

        self.new_folder_input = QLineEdit()
        self.new_folder_input.setPlaceholderText("输入文件夹名称")
        self.new_folder_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                color: #2c3e50;
                padding: 6px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #8B5CF6;
                background-color: #f8f9fa;
            }
        """)
        self.new_folder_input.setMaximumWidth(180)

        self.create_folder_btn = ModernButton("➕ 创建", icon="➕")
        self.create_folder_btn.clicked.connect(self.create_new_folder)

        new_folder_layout.addWidget(self.new_folder_input)
        new_folder_layout.addWidget(self.create_folder_btn)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索文件夹:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入文件夹名称或拼音搜索 (按空格键快速聚焦)")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                color: #2c3e50;
                padding: 6px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #8B5CF6;
                background-color: #f8f9fa;
            }
        """)
        self.search_input.setMaximumWidth(220)
        self.search_input.textChanged.connect(self.search_folders)

        self.search_btn = ModernButton("🔍 搜索", icon="🔍")
        self.search_btn.clicked.connect(self.search_folders)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addStretch()

        right_layout.addLayout(new_folder_layout)
        right_layout.addLayout(search_layout)

        layout.addLayout(right_layout, 1)

        parent_layout.addWidget(panel)

    def keyPressEvent(self, event):
        """键盘事件处理"""
        # 按空格键跳转到搜索输入框并清空内容
        if event.key() == Qt.Key_Space and not self.search_input.hasFocus():
            self.search_input.setFocus()
            self.search_input.clear()
            event.accept()
        # 按A键上一页
        elif event.key() == Qt.Key_A and self.prev_page_btn.isEnabled():
            self.prev_page()
            event.accept()
        # 按D键下一页
        elif event.key() == Qt.Key_D and self.next_page_btn.isEnabled():
            self.next_page()
            event.accept()
        else:
            super().keyPressEvent(event)

    def on_source_combo_changed(self, text):
        """源文件夹下拉框选择改变"""
        if text and os.path.exists(text):
            self.source_folder = text
            self.source_label.setText(text)
            self.refresh_btn.setEnabled(True)
            self.load_source_images()
            self.save_settings()

    def on_target_combo_changed(self, text):
        """目标文件夹下拉框选择改变"""
        if text and os.path.exists(text):
            self.target_folder = text
            self.target_label.setText(text)
            self.sort_btn.setEnabled(True)
            self.load_target_folders()
            self.save_settings()

    def load_settings(self):
        """加载设置"""
        # 加载历史文件夹记录
        source_history = self.settings.value("source_history", [])
        target_history = self.settings.value("target_history", [])

        if source_history:
            self.source_combo.addItems(source_history)
        if target_history:
            self.target_combo.addItems(target_history)

        # 加载上次使用的文件夹
        last_source = self.settings.value("last_source", "")
        last_target = self.settings.value("last_target", "")

        if last_source and os.path.exists(last_source):
            self.source_combo.setCurrentText(last_source)
            self.source_folder = last_source
            self.source_label.setText(last_source)
            self.refresh_btn.setEnabled(True)

        if last_target and os.path.exists(last_target):
            self.target_combo.setCurrentText(last_target)
            self.target_folder = last_target
            self.target_label.setText(last_target)
            self.sort_btn.setEnabled(True)

    def save_settings(self):
        """保存设置"""
        # 保存历史记录（最多保存10个）
        source_history = []
        for i in range(min(10, self.source_combo.count())):
            source_history.append(self.source_combo.itemText(i))
        self.settings.setValue("source_history", source_history)

        target_history = []
        for i in range(min(10, self.target_combo.count())):
            target_history.append(self.target_combo.itemText(i))
        self.settings.setValue("target_history", target_history)

        # 保存当前选择的文件夹
        if self.source_folder:
            self.settings.setValue("last_source", self.source_folder)
        if self.target_folder:
            self.settings.setValue("last_target", self.target_folder)

    def update_folder_history(self, combo_box, folder_path):
        """更新文件夹历史记录"""
        # 移除已存在的相同项
        index = combo_box.findText(folder_path)
        if index != -1:
            combo_box.removeItem(index)

        # 添加到最前面
        combo_box.insertItem(0, folder_path)
        combo_box.setCurrentIndex(0)

        # 限制历史记录数量（最多10个）
        if combo_box.count() > 10:
            combo_box.removeItem(10)

    def search_folders(self):
        """搜索文件夹"""
        search_text = self.search_input.text().strip()

        if not search_text:
            self.show_all_folders()
            return

        for widget in self.folder_widgets.values():
            widget.hide()

        matched_folders = []
        search_text_lower = search_text.lower()

        for folder_path, widget in self.folder_widgets.items():
            folder_name = os.path.basename(folder_path)

            if search_text in folder_name:
                matched_folders.append((folder_path, widget))
            else:
                pinyin_list = lazy_pinyin(folder_name)
                pinyin_str = ''.join(pinyin_list).lower()
                pinyin_acronym = ''.join([p[0] for p in pinyin_list]).lower()

                if (search_text_lower in pinyin_str or
                        search_text_lower in pinyin_acronym or
                        search_text_lower in folder_name.lower()):
                    matched_folders.append((folder_path, widget))

        max_cols = 9
        for i, (folder_path, widget) in enumerate(matched_folders):
            widget.show()
            row = i // max_cols
            col = i % max_cols
            self.folder_grid.removeWidget(widget)
            self.folder_grid.addWidget(widget, row, col)

        for folder_path, widget in self.folder_widgets.items():
            if (folder_path, widget) not in matched_folders:
                widget.hide()

        self.status_label.setText(f"搜索到 {len(matched_folders)} 个匹配的文件夹")

    def show_all_folders(self):
        """显示所有文件夹"""
        if self.need_sort:
            self.apply_sorting(self.sort_ascending)
        else:
            folder_items = list(self.folder_widgets.values())

            for i in reversed(range(self.folder_grid.count())):
                widget = self.folder_grid.itemAt(i).widget()
                if widget and widget in self.folder_widgets.values():
                    self.folder_grid.removeWidget(widget)

            max_cols = 9
            for i, widget in enumerate(folder_items):
                widget.show()
                row = i // max_cols
                col = i % max_cols
                self.folder_grid.addWidget(widget, row, col)

        total_count = len(self.folder_widgets)
        self.status_label.setText(f"共 {total_count} 个文件夹")

    def create_main_content(self, parent_layout):
        """创建主内容区域"""
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
            }
            QSplitter::handle:hover {
                background-color: #8B5CF6;
            }
        """)

        source_group = self.create_source_group()
        splitter.addWidget(source_group)

        target_group = self.create_target_group()
        splitter.addWidget(target_group)

        splitter.setSizes([450, 350])
        parent_layout.addWidget(splitter, 1)

    def create_source_group(self):
        """创建源图片显示区域"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()

        header = QLabel("📸 待分类图片（Shift+单击多选/取消，右键查看/删除，空格键快速搜索）， A/上一页 D/下一页")
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        header.setStyleSheet("color: #2c3e50;")
        toolbar_layout.addWidget(header)

        toolbar_layout.addStretch()

        # 多选工具栏
        self.selection_toolbar = QHBoxLayout()
        self.selection_toolbar.setSpacing(5)

        self.selection_count_label = QLabel("已选中: 0")
        self.selection_count_label.setFont(QFont("Microsoft YaHei", 10))
        self.selection_count_label.setStyleSheet("color: #8B5CF6; font-weight: bold;")
        self.selection_toolbar.addWidget(self.selection_count_label)

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setFixedSize(60, 30)
        self.select_all_btn.clicked.connect(self.select_all_images)
        self.select_all_btn.setEnabled(False)
        self.selection_toolbar.addWidget(self.select_all_btn)

        self.clear_selection_btn = QPushButton("清空")
        self.clear_selection_btn.setFixedSize(60, 30)
        self.clear_selection_btn.clicked.connect(self.clear_image_selections)
        self.clear_selection_btn.setEnabled(False)
        self.selection_toolbar.addWidget(self.clear_selection_btn)

        toolbar_layout.addLayout(self.selection_toolbar)

        toolbar_layout.addSpacing(20)

        # 分页控件
        self.page_info_label = QLabel("第 1 页 / 共 1 页")
        self.page_info_label.setFont(QFont("Microsoft YaHei", 10))
        toolbar_layout.addWidget(self.page_info_label)

        self.prev_page_btn = QPushButton("◀ 上一页")
        self.prev_page_btn.setFixedSize(80, 30)
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setEnabled(False)
        toolbar_layout.addWidget(self.prev_page_btn)

        self.next_page_btn = QPushButton("下一页 ▶")
        self.next_page_btn.setFixedSize(80, 30)
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        toolbar_layout.addWidget(self.next_page_btn)

        layout.addLayout(toolbar_layout)

        # 滚动区域
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setMinimumHeight(250)
        self.image_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #ecf0f1;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
        """)

        self.image_container = QWidget()
        self.image_grid = QGridLayout(self.image_container)
        self.image_grid.setSpacing(10)
        self.image_grid.setContentsMargins(8, 8, 8, 8)

        self.image_scroll.setWidget(self.image_container)
        layout.addWidget(self.image_scroll)

        return container

    def create_target_group(self):
        """创建目标文件夹显示区域"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QLabel("📁 分类文件夹（一行9个，显示文件数量）")
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        layout.addWidget(header)

        self.folder_scroll = QScrollArea()
        self.folder_scroll.setWidgetResizable(True)
        self.folder_scroll.setMinimumHeight(200)
        self.folder_scroll.setStyleSheet(self.image_scroll.styleSheet())

        self.folder_container = QWidget()
        self.folder_grid = QGridLayout(self.folder_container)
        self.folder_grid.setSpacing(10)
        self.folder_grid.setContentsMargins(8, 8, 8, 8)

        self.folder_scroll.setWidget(self.folder_container)
        layout.addWidget(self.folder_scroll)

        return container

    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: white;
                color: #7f8c8d;
                border-top: 1px solid #e0e0e0;
                font-size: 10px;
                padding: 4px;
            }
        """)

        self.status_label = QLabel("就绪")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_bar.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(180)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #8B5CF6;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setVisible(False)

        self.status_bar.addPermanentWidget(self.progress_bar)

    def show_temp_message(self, message, duration=3000):
        """显示临时消息"""
        self.status_label.setText(message)
        QTimer.singleShot(duration, lambda: self.status_label.setText("就绪"))

    def select_source_folder(self):
        """选择源文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            self.source_folder = folder
            self.source_label.setText(folder)
            self.refresh_btn.setEnabled(True)

            # 更新历史记录
            self.update_folder_history(self.source_combo, folder)

            self.load_source_images()
            self.save_settings()

    def refresh_source_images(self):
        """刷新加载源图片"""
        if not self.source_folder:
            return

        self.load_source_images()
        self.show_temp_message("已刷新图片列表")

    def select_target_folder(self):
        """选择目标文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if folder:
            self.target_folder = folder
            self.target_label.setText(folder)
            self.sort_btn.setEnabled(True)

            # 更新历史记录
            self.update_folder_history(self.target_combo, folder)

            self.load_target_folders()
            self.save_settings()

    def load_source_images(self):
        """异步加载源图片"""
        if not self.source_folder:
            return

        # 清空现有图片
        for widget in self.image_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        self.image_widgets.clear()
        self.selected_images.clear()

        # 重置分页状态
        self.current_page = 1
        self.total_pages = 1
        self.update_page_controls()
        self.update_selection_count()

        # 获取图片列表
        self.source_images = []
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')

        try:
            for file in sorted(os.listdir(self.source_folder)):
                if file.lower().endswith(image_extensions):
                    self.source_images.append(os.path.join(self.source_folder, file))

            # 计算总页数
            total_images = len(self.source_images)
            self.total_pages = max(1, (total_images + self.page_size - 1) // self.page_size)

            self.source_count_label.setText(f"{total_images} 张图片")
            self.status_label.setText(f"已发现 {total_images} 张图片")

            if self.source_images:
                # 直接同步加载当前页图片（不再使用异步加载）
                self.load_current_page()
            else:
                self.status_label.setText("文件夹中没有图片")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载图片: {str(e)}")

    def load_current_page(self):
        """加载当前页的图片"""
        # 清空现有图片
        for widget in self.image_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        self.image_widgets.clear()
        self.selected_images.clear()
        self.update_selection_count()

        # 清理布局
        for i in reversed(range(self.image_grid.count())):
            widget = self.image_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if not self.source_images:
            return

        # 计算当前页的图片范围
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.source_images))
        current_page_images = self.source_images[start_idx:end_idx]

        # 显示加载进度
        self.show_progress("正在加载图片...", 0)
        total_to_load = len(current_page_images)

        # 同步加载当前页图片
        for i, image_path in enumerate(current_page_images):
            # 创建图片项并添加到网格
            image_item = ImageItem(image_path, self.image_container)

            # 连接选中状态改变信号
            image_item.selection_changed.connect(self.on_image_selection_changed)

            # 计算行列位置
            col = i % 12
            row = i // 12

            # 添加到网格
            self.image_grid.addWidget(image_item, row, col)

            # 存储引用
            self.image_widgets[image_path] = image_item

            # 更新进度
            progress = int((i + 1) / total_to_load * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"正在加载图片... ({i + 1}/{total_to_load})")

            # 处理事件，保持界面响应
            QApplication.processEvents()

        # 隐藏进度条
        self.hide_progress()

        # 更新页面信息
        self.update_page_controls()

        # 更新状态
        self.status_label.setText(f"第 {self.current_page} 页，共 {len(current_page_images)} 张图片")

    def on_image_selection_changed(self, image_path, selected):
        """处理图片选中状态改变"""
        if selected:
            self.selected_images.add(image_path)
        else:
            self.selected_images.discard(image_path)

        self.update_selection_count()

    def update_page_controls(self):
        """更新分页控件状态"""
        # 更新页面信息
        self.page_info_label.setText(f"第 {self.current_page} 页 / 共 {self.total_pages} 页")

        # 更新按钮状态
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)

        # 更新多选按钮状态
        has_images = len(self.source_images) > 0
        self.select_all_btn.setEnabled(has_images)
        self.clear_selection_btn.setEnabled(has_images)

    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()

    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_current_page()

    def load_target_folders(self):
        """加载目标文件夹"""
        if not self.target_folder:
            return

        for widget in self.folder_widgets.values():
            widget.setParent(None)
        self.folder_widgets.clear()

        try:
            folders = []
            for item in sorted(os.listdir(self.target_folder)):
                item_path = os.path.join(self.target_folder, item)
                if os.path.isdir(item_path):
                    folders.append(item_path)

            max_cols = 9
            for i, folder_path in enumerate(folders):
                row = i // max_cols
                col = i % max_cols

                folder_item = FolderItem(folder_path, self)
                self.folder_grid.addWidget(folder_item, row, col)
                self.folder_widgets[folder_path] = folder_item

            self.need_sort = True
            self.status_label.setText(f"已加载 {len(folders)} 个文件夹")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载文件夹: {str(e)}")

    def apply_sorting(self, ascending):
        """应用排序"""
        self.sort_ascending = ascending

        if not self.target_folder or not self.folder_widgets:
            return

        folder_items = list(self.folder_widgets.values())

        if ascending:
            folder_items.sort(key=lambda x: x.file_count)
        else:
            folder_items.sort(key=lambda x: x.file_count, reverse=True)

        for i in reversed(range(self.folder_grid.count())):
            widget = self.folder_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, folder_item in enumerate(folder_items):
            row = i // 9
            col = i % 9
            self.folder_grid.addWidget(folder_item, row, col)

        self.need_sort = False
        sort_type = "从少到多" if ascending else "从多到少"
        self.show_temp_message(f"已按{sort_type}重新排序")

    def create_new_folder(self):
        """创建新文件夹"""
        if not self.target_folder:
            QMessageBox.warning(self, "警告", "请先选择目标文件夹")
            return

        folder_name = self.new_folder_input.text().strip()
        if not folder_name:
            QMessageBox.warning(self, "警告", "请输入文件夹名称")
            return

        folder_path = os.path.join(self.target_folder, folder_name)

        try:
            os.makedirs(folder_path, exist_ok=True)

            folder_item = FolderItem(folder_path, self)
            folder_paths = list(self.folder_widgets.keys())
            folder_paths.append(folder_path)

            for i in reversed(range(self.folder_grid.count())):
                widget = self.folder_grid.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            if not self.need_sort:
                folder_items = list(self.folder_widgets.values())
                folder_items.append(folder_item)

                if self.sort_ascending:
                    folder_items.sort(key=lambda x: x.file_count)
                else:
                    folder_items.sort(key=lambda x: x.file_count, reverse=True)

                for i, item in enumerate(folder_items):
                    row = i // 9
                    col = i % 9
                    self.folder_grid.addWidget(item, row, col)
                    self.folder_widgets[item.folder_path] = item
            else:
                folder_paths.sort()
                max_cols = 9
                for i, path in enumerate(folder_paths):
                    row = i // max_cols
                    col = i % max_cols
                    if path not in self.folder_widgets:
                        item = FolderItem(path, self)
                        self.folder_grid.addWidget(item, row, col)
                        self.folder_widgets[path] = item
                    else:
                        self.folder_grid.addWidget(self.folder_widgets[path], row, col)

            self.new_folder_input.clear()
            self.status_label.setText(f"已创建文件夹: {folder_name}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建文件夹: {str(e)}")

    # 多选相关方法
    def get_selected_images(self):
        """获取选中的图片列表"""
        return list(self.selected_images)

    def update_selection_count(self):
        """更新选中计数"""
        count = len(self.selected_images)
        self.selection_count_label.setText(f"已选中: {count}")

    def clear_image_selections(self):
        """清空所有选中"""
        for image_path in self.selected_images.copy():
            if image_path in self.image_widgets:
                self.image_widgets[image_path].deselect_item()
        self.selected_images.clear()
        self.update_selection_count()

    def select_all_images(self):
        """全选当前页图片"""
        current_page_start = (self.current_page - 1) * self.page_size
        current_page_end = min(current_page_start + self.page_size, len(self.source_images))
        current_page_images = self.source_images[current_page_start:current_page_end]

        for image_path in current_page_images:
            if image_path in self.image_widgets and not self.image_widgets[image_path].is_selected:
                self.image_widgets[image_path].select_item()

        self.update_selection_count()

    def request_folder_icon(self, folder_path, folder_item):
        """请求加载文件夹图标"""
        self.pending_icons[folder_path] = folder_item
        self.process_next_folder_icon()

    def process_next_folder_icon(self):
        """处理下一个文件夹图标"""
        if not self.pending_icons or self.folder_icon_loader:
            return

        folder_path, folder_item = list(self.pending_icons.items())[0]
        del self.pending_icons[folder_path]

        self.folder_icon_loader = FolderIconLoader([folder_path])
        self.folder_icon_loader.icon_loaded.connect(self.on_folder_icon_loaded)
        self.folder_icon_loader.finished.connect(self.on_folder_icon_loading_finished)
        self.folder_icon_loader.start()

    def on_folder_icon_loaded(self, folder_path, pixmap):
        """文件夹图标加载完成"""
        if folder_path in self.folder_widgets:
            self.folder_widgets[folder_path].update_icon_with_pixmap(pixmap)

    def on_folder_icon_loading_finished(self):
        """文件夹图标加载线程完成"""
        if self.folder_icon_loader:
            self.folder_icon_loader.deleteLater()
            self.folder_icon_loader = None

        self.process_next_folder_icon()

    def start_move_image(self, image_path, target_folder):
        """开始移动图片"""
        if not os.path.exists(image_path):
            self.status_label.setText("图片文件不存在")
            return

        if image_path in self.image_widgets:
            self.image_widgets[image_path].hide()

        self.mover = FileMover(image_path, target_folder)
        self.mover.progress.connect(self.on_move_progress)
        self.mover.finished.connect(self.on_move_finished)
        self.mover.start()

        self.status_label.setText("正在移动图片...")

    def start_move_multiple_images(self, image_paths, target_folder):
        """开始批量移动图片"""
        valid_paths = [path for path in image_paths if os.path.exists(path)]

        if not valid_paths:
            self.status_label.setText("没有有效的图片文件")
            return

        # 隐藏选中的图片
        for image_path in valid_paths:
            if image_path in self.image_widgets:
                self.image_widgets[image_path].hide()

        # 创建批量移动线程
        self.batch_mover = BatchFileMover(valid_paths, target_folder)
        self.batch_mover.progress.connect(self.on_batch_move_progress)
        self.batch_mover.finished.connect(self.on_batch_move_finished)
        self.batch_mover.start()

        self.status_label.setText(f"正在批量移动 {len(valid_paths)} 个图片...")

    def on_move_progress(self, progress, message):
        """移动进度"""
        self.show_progress(message, progress)

    def on_move_finished(self, image_path, target_path, success, message):
        """移动完成"""
        self.hide_progress()

        if success:
            if image_path in self.image_widgets:
                widget = self.image_widgets.pop(image_path)
                widget.deleteLater()

            # 从选中中移除
            if image_path in self.selected_images:
                self.selected_images.remove(image_path)
                self.update_selection_count()

            # 更新总图片数
            total_images = len(self.source_images)
            if image_path in self.source_images:
                self.source_images.remove(image_path)
                total_images = len(self.source_images)

            self.source_count_label.setText(f"{total_images} 张图片")
            self.status_label.setText(f"{message}")

            # 重新计算总页数
            self.total_pages = max(1, (total_images + self.page_size - 1) // self.page_size)

            # 如果当前页没有图片了，且不是第一页，返回上一页
            current_page_start = (self.current_page - 1) * self.page_size
            current_page_end = min(current_page_start + self.page_size, total_images)
            if current_page_start >= total_images and self.current_page > 1:
                self.current_page -= 1
                self.load_current_page()
            else:
                # 重新加载当前页
                self.load_current_page()

            # 只更新目标文件夹（不再更新所有文件夹）
            if target_path:
                folder_path = os.path.dirname(target_path)
                if folder_path in self.folder_widgets:
                    QTimer.singleShot(300, lambda: self.folder_widgets[folder_path].update_icon_and_count())
                    self.need_sort = True
        else:
            if image_path in self.image_widgets:
                self.image_widgets[image_path].show()

            self.status_label.setText(f"移动失败: {message}")

    def on_batch_move_progress(self, progress, message):
        """批量移动进度"""
        self.show_progress(message, progress)

    def on_batch_move_finished(self, successful_moves, failed_moves, success, message):
        """批量移动完成"""
        self.hide_progress()

        # 从选中中移除成功移动的图片
        for old_path, _ in successful_moves:
            if old_path in self.selected_images:
                self.selected_images.remove(old_path)

        self.update_selection_count()

        # 更新图片列表
        total_images = len(self.source_images)

        # 移除成功移动的图片
        for old_path, _ in successful_moves:
            if old_path in self.source_images:
                self.source_images.remove(old_path)
            if old_path in self.image_widgets:
                widget = self.image_widgets.pop(old_path)
                widget.deleteLater()

        # 重新计算总页数
        total_images = len(self.source_images)
        self.source_count_label.setText(f"{total_images} 张图片")
        self.total_pages = max(1, (total_images + self.page_size - 1) // self.page_size)

        # 重新加载当前页
        current_page_start = (self.current_page - 1) * self.page_size
        if current_page_start >= total_images and self.current_page > 1:
            self.current_page -= 1
        self.load_current_page()

        # 显示结果消息
        if failed_moves:
            error_details = "\n".join([f"{os.path.basename(path)}: {error}" for path, error in failed_moves])
            self.status_label.setText(f"{message} (失败: {len(failed_moves)}个)")
        else:
            self.status_label.setText(message)

        # 只更新目标文件夹（不再更新所有文件夹）
        if successful_moves and self.target_folder:
            # 获取目标文件夹路径
            target_folder = self.target_folder
            if successful_moves:
                target_folder = os.path.dirname(successful_moves[0][1])

            if target_folder in self.folder_widgets:
                QTimer.singleShot(300, lambda: self.folder_widgets[target_folder].update_icon_and_count())

    def on_image_deleted(self, image_path):
        """处理图片删除"""
        if image_path in self.image_widgets:
            widget = self.image_widgets.pop(image_path)
            widget.deleteLater()

        # 从选中中移除
        if image_path in self.selected_images:
            self.selected_images.remove(image_path)
            self.update_selection_count()

        # 更新总图片数
        total_images = len(self.source_images)
        if image_path in self.source_images:
            self.source_images.remove(image_path)
            total_images = len(self.source_images)

        self.source_count_label.setText(f"{total_images} 张图片")

        # 重新计算总页数
        self.total_pages = max(1, (total_images + self.page_size - 1) // self.page_size)

        # 如果当前页没有图片了，且不是第一页，返回上一页
        current_page_start = (self.current_page - 1) * self.page_size
        current_page_end = min(current_page_start + self.page_size, total_images)
        if current_page_start >= total_images and self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()
        else:
            # 重新加载当前页
            self.load_current_page()

    def on_image_renamed(self, new_image_path, old_path):
        """处理图片重命名"""
        if old_path in self.image_widgets:
            widget = self.image_widgets.pop(old_path)
            self.image_widgets[new_image_path] = widget

        # 更新选中列表
        if old_path in self.selected_images:
            self.selected_images.remove(old_path)
            self.selected_images.add(new_image_path)
            self.update_selection_count()

        # 更新源图片列表
        if old_path in self.source_images:
            idx = self.source_images.index(old_path)
            self.source_images[idx] = new_image_path

    def show_progress(self, message, value):
        """显示进度"""
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"{message}")

    def hide_progress(self):
        """隐藏进度"""
        self.progress_bar.setVisible(False)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()