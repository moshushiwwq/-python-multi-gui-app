import sys , re , uuid
print('已导入: sys, re ,uuid模块')
import subprocess
print('已导入: subprocess模块')
import time
print('已导入: time模块')
import shutil
print('已导入: shutil模块')
import hashlib
print('已导入: hashlib模块')
import pickle
print('已导入: pickle模块')
import os
print('已导入: os模块')
import aiohttp
print('已导入: aiohttp模块')
import asyncio
print('已导入: asyncio模块')
import random
print('已导入: random模块')
from urllib.parse import urljoin, urlparse
print('已导入: urljoin, urlparse from urllib.parse')
import requests
print('已导入: requests库')
from bs4 import BeautifulSoup
print('已导入: BeautifulSoup from bs4')
from PyQt5.QtWidgets import (QApplication , QMainWindow , QWidget , QVBoxLayout ,
                             QHBoxLayout , QLabel , QLineEdit , QPushButton ,
                             QProgressBar , QTextEdit , QFileDialog , QMessageBox , QTreeWidget ,
                             QTreeWidgetItem , QGroupBox , QFrame , QDialog , QFormLayout , QListWidget ,
                             QListWidgetItem , QSpinBox , QSizePolicy , QComboBox , QCheckBox , QTreeView , QTabWidget ,
                             QSplitter)
print('已导入: QtWidget组件 from PyQt5.QtWidgets')
from PyQt5.QtGui import QPalette , QBrush , QPixmap , QFont , QColor , QIcon , QStandardItem , QStandardItemModel , \
    QTextCursor

print('已导入: QtGui组件 from PyQt5.QtGui')
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSettings, QPropertyAnimation, \
    QPoint, QEasingCurve ,QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView , QWebEnginePage ,  QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineCookieStore
print('已导入: QtCore组件 from PyQt5.QtCore')

# 设置中文字体支持
font = QFont()
font.setFamily("SimHei")


# 哈希加密函数
def hash_string(string):
    return hashlib.sha256(string.encode()).hexdigest()

# 保存用户信息
def save_users_info(users_info):
    with open('usr_info.pickle', 'wb') as usr_file:
        pickle.dump(users_info, usr_file)

# 加载用户信息
def load_users_info():
    try:
        with open('usr_info.pickle', 'rb') as usr_file:
            return pickle.load(usr_file)
    except FileNotFoundError:
        return {}

# 自定义对话框类
class CustomDialog(QDialog) :

    def __init__(self , message , title="系统" , button_text="进入" ,animation_type="slide" , opacity=0.9 , parent=None) :
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog |Qt.WindowTitleHint |Qt.WindowCloseButtonHint
        )

        self.animation_type = animation_type
        self.animation = None
        self.target_width = 300
        self.target_height = 180
        self.opacity = opacity  # 存储透明度值供动画使用

        # 获取父窗口位置并设置对话框位置
        if parent :
            parent_geometry = parent.geometry()
            self.target_x = parent_geometry.left() + (parent_geometry.width() - self.target_width) // 2
            self.target_y = parent_geometry.top() + (parent_geometry.height() - self.target_height) // 3
        else :
            screen_geometry = QApplication.primaryScreen().geometry()
            self.target_x = (screen_geometry.width() - self.target_width) // 2
            self.target_y = (screen_geometry.height() - self.target_height) // 2

        self.start_x = self.target_x
        self.start_y = self.target_y - 50

        # 创建内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
                font-size: 18px;
                padding: 10px;
            }
        """)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10 , 10 , 10 , 10)
        main_layout.addWidget(self.content_widget)

        # 对话框整体半透明，内容容器不透明
        self.setWindowOpacity(0 if animation_type == "fade" else opacity)

        # 设置内容布局
        content_layout = QVBoxLayout(self.content_widget)

        # 消息标签
        label = QLabel(message)
        font = QFont()
        font.setFamily("SimHei")
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)

        # 确认按钮
        ok_button = QPushButton(button_text)
        ok_button.setFont(font)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                padding: 10px;
                min-width: 100px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        ok_button.clicked.connect(self.close_with_animation)
        content_layout.addWidget(ok_button , alignment = Qt.AlignCenter)

        # 设置对话框样式表（保留圆角）
        self.setStyleSheet("""
            QDialog {
                border-radius: 15px;
            }
        """)

        # 关键修改1：初始化时立即设置透明度，而非通过动画延迟设置
        self.setWindowOpacity(0 if animation_type == "fade" else opacity)

        # 初始化位置和大小
        if self.animation_type == "slide" :
            self.setGeometry(self.start_x , self.start_y , self.target_width , self.target_height)
        else :
            self.setGeometry(self.target_x , self.target_y , self.target_width , self.target_height)

        # 启动动画（无需延迟）
        self.start_animation()

    def start_animation(self) :
        if self.animation_type == "slide" :
            self.animation = QPropertyAnimation(self , b"pos")
            self.animation.setStartValue(QPoint(self.start_x , self.start_y))
            self.animation.setEndValue(QPoint(self.target_x , self.target_y))
        else :
            self.animation = QPropertyAnimation(self , b"windowOpacity")
            self.animation.setStartValue(0)
            # 关键修改2：淡出动画的最终透明度使用用户设置的opacity值
            self.animation.setEndValue(self.opacity)

        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def close_with_animation(self) :
        if self.animation_type == "slide" :
            self.animation = QPropertyAnimation(self , b"pos")
            self.animation.setStartValue(QPoint(self.target_x , self.target_y))
            self.animation.setEndValue(QPoint(self.target_x , self.target_y - 50))
        else :
            self.animation = QPropertyAnimation(self , b"windowOpacity")
            self.animation.setStartValue(self.opacity)
            self.animation.setEndValue(0)

        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.finished.connect(self.accept)
        self.animation.start()

# 主窗口类
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.current_user = None
        self.is_admin = False
        self.username_label = None
        self.password_label = None
        self.background_pixmap = QPixmap("down.png")

        self.init_ui()

    # 设置主窗口
    def init_ui(self):
        self.setWindowTitle("登录系统")
        self.setGeometry(50, 50, 600, 600)
        self.setFont(font)

        # 使用QPalette设置背景图（不影响子控件）
        palette = self.palette()
        palette.setBrush(QPalette.Window , QBrush(self.background_pixmap.scaled(self.size() , Qt.IgnoreAspectRatio , Qt.SmoothTransformation)))
        self.setPalette(palette)

        # 窗口大小变化时重绘背景
        self.setAutoFillBackground(True)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 登录界面
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.9); /* 半透明白色 */
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #cccccc;
        """)
        form_layout = QVBoxLayout(form_frame)

        # 账号和密码输入
        credentials_layout = QVBoxLayout()

        username_layout = QHBoxLayout()
        self.username_label = QLabel("账号：")
        self.username_label.setFont(font)
        self.username_label.setStyleSheet("color: #333333;")
        self.username_input = QLineEdit()
        self.username_input.setFont(font)
        self.username_input.setStyleSheet("""
            QLineEdit {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
            color: #333333;
            }
            /* 焦点状态样式 */
             QLineEdit:focus {
            border: 1px solid #4a86e8;  
            background-color: #f9f9f9;  
            selection-background-color: #a6c9e2;  
            selection-color: black;  
            outline: none;  
            }
        """)
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)
        credentials_layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        self.password_label = QLabel("密码：")
        self.password_label.setFont(font)
        self.password_label.setStyleSheet("color: #333333;")
        self.password_input = QLineEdit()
        self.password_input.setFont(font)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
            color: #333333;
            }
            /* 焦点状态样式 */
             QLineEdit:focus {
            border: 1px solid #4a86e8;  
            background-color: #f9f9f9;  
            selection-background-color: #a6c9e2;  
            selection-color: black;  
            outline: none;  
            }
        """)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)
        credentials_layout.addLayout(password_layout)

        form_layout.addLayout(credentials_layout)

        # 按钮
        buttons_layout = QHBoxLayout()

        login_button = QPushButton("登录")
        login_button.setFont(font)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        login_button.clicked.connect(self.usr_log_in)
        buttons_layout.addWidget(login_button)

        manager_button = QPushButton("管理")
        manager_button.setFont(font)
        manager_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
           }
           QPushButton:pressed {
               background-color: #0a69b7;
           }
        """)
        manager_button.clicked.connect(self.usr_manager)
        buttons_layout.addWidget(manager_button)

        quit_button = QPushButton("退出")
        quit_button.setFont(font)
        quit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        quit_button.clicked.connect(self.usr_sign_quit)
        buttons_layout.addWidget(quit_button)

        form_layout.addLayout(buttons_layout)

        main_layout.addWidget(form_frame)
        main_layout.setAlignment(form_frame, Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 处理窗口大小变化事件
        self.resizeEvent = self._resize_event

    # 窗口大小变化时调整背景图
    def _resize_event(self, event):
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("down.png").scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)
        return super().resizeEvent(event)

     #登录界面
    def usr_log_in(self):
        usr_name = self.username_input.text()
        user_pwd = self.password_input.text()
        hashed_usr_name = hash_string(usr_name)
        hashed_usr_pwd = hash_string(user_pwd)
        users_info = load_users_info()
        self.username_label.setStyleSheet("color: #333333;")
        self.password_label.setStyleSheet("color: #333333;")

        # 用户为第一次登录
        if not users_info:
            # 第一个登录的用户为管理员
            users_info[hashed_usr_name] = {
                'hashed_pwd': hashed_usr_pwd,
                'username': usr_name,
                'register_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'is_admin': True
            }
            save_users_info(users_info)
            self.is_admin = True
            self.username_label.setStyleSheet("color: green;")
            self.password_label.setStyleSheet("color: green;")
            dialog = CustomDialog(f"用户\"{usr_name}\"欢迎登录，你是管理员",title = "欢迎",button_text = '进入系统',parent = self)
            dialog.exec_()

        # 用户名在列表中
        elif hashed_usr_name in users_info:
            #用户名在列表中
            if hashed_usr_pwd == users_info[hashed_usr_name]['hashed_pwd']:
                #密码在列表中
                self.is_admin = users_info[hashed_usr_name].get('is_admin', False)
                self.username_label.setStyleSheet("color: green;")
                self.password_label.setStyleSheet("color: green;")
                dialog = CustomDialog(f"用户\"{usr_name}\"欢迎登录", title = "欢迎" ,button_text = '进入系统',parent = self)
                dialog.exec_()
            elif user_pwd == '' :
                # 密码不在列表中(且为空)
                self.password_label.setStyleSheet("color: orange;")
                dialog = CustomDialog("未输入密码" , title = "错误" , button_text = "知道了",parent = self)
                dialog.exec_()
                return
            else:
                #密码不在列表中(且不为空)
                self.password_label.setStyleSheet("color: red;")
                dialog = CustomDialog("密码错误" , title = "错误" , button_text = "知道了",parent = self)
                dialog.exec_()
                return

        # 用户名和密码都没有填写
        elif usr_name == '' and user_pwd == '':
            self.username_label.setStyleSheet("color: orange;")
            self.password_label.setStyleSheet("color: orange;")
            dialog = CustomDialog("请填写用户名和密码" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()
            return

        # 用户名没有填写
        elif usr_name == '':
            self.username_label.setStyleSheet("color: orange;")
            dialog = CustomDialog("未输入用户名" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()
            return

        #还没注册的用户
        else:
            self.username_label.setStyleSheet("color: orange;")
            self.password_label.setStyleSheet("color: orange;")
            dialog = CustomDialog("你还没注册，是否联系管理员注册？",title = "欢迎" , button_text = "好的",parent = self)
            dialog.exec_()
            return

        self.current_user = usr_name
        self.hide()
        self.menu_window = MenuWindow(self)
        self.menu_window.show()

    #管理界面
    def usr_manager(self) :
        # 从主窗口获取已输入的用户名和密码
        usr_name = self.username_input.text()
        user_pwd = self.password_input.text()

        # 验证输入是否为空
        if not usr_name or not user_pwd :
            dialog = CustomDialog("请先在主窗口输入用户名和密码" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()
            return

        hashed_usr_name = hash_string(usr_name)
        hashed_usr_pwd = hash_string(user_pwd)
        users_info = load_users_info()

        # 验证用户是否存在
        if hashed_usr_name not in users_info :
            dialog = CustomDialog("用户不存在" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()
            return

        stored_user = users_info[hashed_usr_name]

        # 检查是否为字典类型
        if not isinstance(stored_user , dict) :
            dialog = CustomDialog("用户数据结构损坏，请检查" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()
            return

        # 验证密码和管理员权限
        if hashed_usr_pwd == stored_user['hashed_pwd'] :
            if stored_user.get('is_admin' , False) :
                self.show_admin_interface()  # 显示管理界面
            else :
                self.username_label.setStyleSheet("color:orange;")
                dialog = CustomDialog("该用户不是管理员" , title = "错误" , button_text = "知道了",parent = self)
                dialog.exec_()
        else :
            self.password_label.setStyleSheet("color:red;")
            dialog = CustomDialog("密码错误" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()

    #显示管理员界面
    def show_admin_interface(self):
        self.admin_window = AdminWindow(self)
        self.admin_window.show()

    #退出界面
    def usr_sign_quit(self):
        self.close()

# 菜单窗口类
class MenuWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        if self.parent.is_admin:
            self.setGeometry(50, 50, 800,900)
        else:
            self.setGeometry(50, 50, 400, 300)

        self.setWindowTitle("菜单")
        self.setFont(font)

        background_pixmap = QPixmap("down.png")  # 请替换为实际的背景图片文件名
        palette = self.palette()
        palette.setBrush(QPalette.Window ,
                         QBrush(background_pixmap.scaled(self.size() , Qt.IgnoreAspectRatio , Qt.SmoothTransformation)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 按钮
        button_style = """
        QPushButton {
            background-color: rgba(255, 255, 255, 0.8);
            color: #333333;
            font-size: 16px;
            padding: 15px;
            min-width: 200px;
            border: none;
            border-radius: 10px;
            margin: 10px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.9);
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 1);
        }
        """

        news_button = QPushButton("百度热搜")
        news_button.setFont(font)
        news_button.setStyleSheet(button_style)
        news_button.clicked.connect(self.show_news_in_window)
        main_layout.addWidget(news_button)

        if self.parent.is_admin:
            novel_button = QPushButton("小说下载")
            novel_button.setFont(font)
            novel_button.setStyleSheet(button_style)
            novel_button.clicked.connect(self.quick_download_txt)
            main_layout.addWidget(novel_button)

            music_button = QPushButton("浏览器")
            music_button.setFont(font)
            music_button.setStyleSheet(button_style)
            music_button.clicked.connect(self.a_BrowserWindow_example)
            main_layout.addWidget(music_button)

            button4 = QPushButton("音视频下载")
            button4.setFont(font)
            button4.setStyleSheet(button_style)
            button4.clicked.connect(self.music_video_download)
            main_layout.addWidget(button4)

        # 退出按钮
        quit_button = QPushButton("退出")
        quit_button.setFont(font)
        quit_button.setStyleSheet(button_style)
        quit_button.clicked.connect(self.usr_sign_quit)
        main_layout.addWidget(quit_button)

        # 添加伸缩项，使按钮居中显示
        main_layout.addStretch()

    # 显示百度热搜窗口
    def show_news_in_window(self):
        self.news_window = NewsWindow(self)
        self.news_window.show()

    # 显示小说下载窗口
    def quick_download_txt(self):
        self.novel_window = NovelDownloadWindow(self)
        self.novel_window.show()

    # 显示浏览器窗口
    def a_BrowserWindow_example(self):
        self.a_BrowserWindow = BrowserWindow(self)
        self.a_BrowserWindow.show()

    # 显示视频下载窗口
    def music_video_download(self):
        self.music_video_window = VideoDownloadWindow(self)
        self.music_video_window.show()

    # 显示退出窗口
    def usr_sign_quit(self):
        self.parent.show()
        self.close()

# 管理员窗口类
class AdminWindow(QMainWindow) :

    def __init__(self , parent=None) :
        super().__init__(parent)
        self.parent = parent
        self.font = QFont("SimHei" , 10)  # 确保中文字体正常显示
        self.init_ui()
        # 设置窗口位置在上一个窗口的左上角
        if parent and parent.isVisible() :
            parent_pos = parent.pos()
            self.move(parent_pos)

    def init_ui(self) :
        self.setGeometry(50, 50, 600, 600)
        self.setWindowTitle("用户管理系统")
        self.setFont(self.font)

        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15 , 15 , 15 , 15)
        main_layout.setSpacing(15)

        # 用户列表
        self.user_tree = QTreeWidget()
        self.user_tree.setFont(self.font)
        self.user_tree.setHeaderLabels(["用户名" , "注册时间"])

        # 美化用户列表
        self.user_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 5px;
                alternate-background-color: #f9f9f9;
            }
            QTreeWidget::item {
                height: 30px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                padding: 4px;
                font-weight: bold;
                border-radius: 4px;
            }
        """)

        self.user_tree.setAlternatingRowColors(True)
        self.user_tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.user_tree.setSelectionMode(QTreeWidget.SingleSelection)

        self.load_users()
        main_layout.addWidget(self.user_tree)

        # 按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        delete_button = QPushButton("删除用户")
        delete_button.setStyleSheet("""
            QPushButton {
            background-color: #f44336;
                color: white;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        delete_button.clicked.connect(self.delete_user)
        buttons_layout.addWidget(delete_button)

        add_button = QPushButton("增加用户")
        add_button.setStyleSheet("""
            QPushButton {
            background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        add_button.clicked.connect(self.add_user)
        buttons_layout.addWidget(add_button)

        main_layout.addLayout(buttons_layout)

    def load_users(self) :
        self.user_tree.clear()
        users_info = load_users_info()

        for hashed_name , info in users_info.items() :
            if hasattr(self.parent , 'current_user') and info['username'] != self.parent.current_user :
                item = QTreeWidgetItem([info['username'] , info['register_time']])
                self.user_tree.addTopLevelItem(item)

    def delete_user(self) :
        selected_items = self.user_tree.selectedItems()
        if not selected_items :
            dialog = CustomDialog("请先选择要删除的用户" , title = "提示" , button_text = "知道了",parent = self)
            dialog.exec_()
            return

        username = selected_items[0].text(0)
        hashed_username = hash_string(username)

        users_info = load_users_info()
        if hashed_username in users_info :
            del users_info[hashed_username]
            save_users_info(users_info)
            self.load_users()
            dialog = CustomDialog(f"用户 {username} 已删除" , title = "提示" , button_text = "知道了",parent = self)
            dialog.exec_()
        else :
            dialog = CustomDialog(f"用户 {username} 不存在" , title = "错误" , button_text = "知道了",parent = self)
            dialog.exec_()

    def add_user(self) :
        self.add_user_window = AddUserWindow(self)
        # 使对话框在显示时自动居中
        self.add_user_window.move(self.geometry().center() - self.add_user_window.rect().center())
        result = self.add_user_window.exec_()
        if result :  # 如果对话框接受（点击了创建用户）
            self.load_users()  # 刷新用户列表

# 添加用户窗口类
class AddUserWindow(QDialog) :
    def __init__(self , parent=None) :
        super().__init__(parent)
        self.setWindowTitle("添加新用户")
        self.setWindowModality(Qt.WindowModal)  # 使对话框独立但阻塞父窗口

        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)

        layout = QFormLayout(self)

        # 用户名输入
        self.username_edit = QLineEdit()
        layout.addRow("用户名:" , self.username_edit)

        # 密码输入
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("密码:" , self.password_edit)

        # 确认密码输入
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("确认密码:" , self.confirm_password_edit)

        # 按钮布局
        buttons_layout = QHBoxLayout()

        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        create_button = QPushButton("创建用户")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        create_button.clicked.connect(self.create_user)
        buttons_layout.addWidget(create_button)

        layout.addRow(buttons_layout)

    def create_user(self) :
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not username :
            dialog = CustomDialog( "用户名不能为空" , title = "输入错误" , button_text = '知道了',parent = self)
            dialog.exec_()
            return

        if password != confirm_password :
            dialog = CustomDialog("两次输入的密码不一致" , title = "输入错误" , button_text = '知道了',parent = self)
            dialog.exec_()
            return

        # 处理用户创建逻辑
        hashed_username = hash_string(username)

        users_info = load_users_info()
        if hashed_username in users_info :
            dialog = CustomDialog("该用户名已存在" , title =  "创建失败" , button_text = '知道了',parent = self)
            dialog.exec_()
            return

        # 添加新用户信息
        users_info[hashed_username] = {
            "username" : username ,
            "register_time" : time.strftime("%Y-%m-%d %H:%M:%S"),  # 实际应该使用当前时间
            "password" : hash_string(password)
        }

        save_users_info(users_info)
        dialog = CustomDialog(f"用户 {username} 创建成功" , title = "创建成功", button_text = '知道了',parent = self)
        dialog.exec_()
        self.accept()

# 百度热搜窗口类
class NewsWindow(QWidget) :

    def __init__(self , parent=None) :
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.Window)
        self.font = QFont("SimHei" , 10)  # 确保中文字体正常显示
        self.init_ui()
        # 设置窗口位置在上一个窗口的左上角
        if parent and parent.isVisible() :
            parent_pos = parent.pos()
            self.move(parent_pos)

    def init_ui(self) :
        self.setGeometry(50 , 50 , 800 , 900)
        self.setWindowTitle("百度热搜")
        self.setFont(self.font)

        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15 , 15 , 15 , 15)
        main_layout.setSpacing(15)

        # 标题区域
        title_label = QLabel("百度实时热搜")
        title_label.setFont(QFont("SimHei" , 16 , QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title_label)

        # 刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #025aa5;
            }
        """)
        refresh_button.setFixedWidth(100)
        refresh_button.clicked.connect(self.load_news)
        main_layout.addWidget(refresh_button , alignment = Qt.AlignCenter)

        # 热搜列表区域
        self.news_list = QListWidget()
        self.news_list.setFont(self.font)
        self.news_list.setSpacing(5)
        self.news_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 8px;
                min-height: 30px;
            }
            QListWidget::item:selected {
                background-color: #e0f7fa;
                color: #333;
            }
        """)
        main_layout.addWidget(self.news_list)

        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666;")
        main_layout.addWidget(self.status_label , alignment = Qt.AlignLeft)

        # 加载百度热搜
        self.load_news()

    def load_news(self) :
        self.status_label.setText("正在加载热搜数据...")
        self.news_list.clear()

        url = 'https://top.baidu.com/board?tab=realtime'
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36'}

        try :
            # 显示加载动画
            loading_item = QListWidgetItem("数据加载中，请稍候...")
            loading_item.setTextAlignment(Qt.AlignCenter)
            self.news_list.addItem(loading_item)

            response = requests.get(url , headers = headers , timeout = 10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text , 'lxml')
            news_items = soup.find_all('div' , class_ = 'content_1YWBm')
            hot_number = soup.find_all('div' , class_ = 'hot-index_1Bl1a')
            count = 0
            for i in hot_number:
                hot_number[count] = hot_number[count].text
                count += 1

            self.news_list.clear()

            if not news_items :
                no_data_item = QListWidgetItem("无热搜数据")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                no_data_item.setForeground(QColor(150 , 150 , 150))
                self.news_list.addItem(no_data_item)
                self.status_label.setText("加载完成，未获取到数据")
                return

            # 处理前100条热搜
            for i , item in enumerate(news_items[:100]) :
                # 数据提取保持不变
                if i >= len(hot_number) :
                    hot = "热度数据缺失"
                else :
                    hot = hot_number[i]

                try :
                    title = item.find('div' , class_ = 'c-single-text-ellipsis').text.strip()
                except AttributeError :
                    title = f"热搜标题 {i + 1}"

                # 创建自定义项
                list_item = QListWidgetItem()
                self.news_list.addItem(list_item)

                # 创建自定义widget
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(5 , 5 , 5 , 5)
                layout.setSpacing(10)

                # 排名标签 - 恢复颜色并优化样式
                rank_label = QLabel(f"{i + 1}")
                rank_label.setAlignment(Qt.AlignCenter)
                rank_label.setFixedSize(48 , 28)  # 保持足够大小

                # 根据排名设置不同的背景色
                if i < 3 :  # 前三名
                    rank_label.setStyleSheet(f"""
                        QLabel {{
                            background-color: {"#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32"};
                            color: white;
                            font: bold 14px "SimHei";
                            border-radius: 14px;
                        }}
                    """)
                else :  # 其他排名
                    rank_label.setStyleSheet("""
                        QLabel {
                            background-color: #e0e0e0;
                            color: #333;
                            font: 14px "SimHei";
                            border-radius: 14px;
                        }
                    """)

                # 标题标签
                title_label = QLabel(title)
                title_label.setWordWrap(True)
                title_label.setStyleSheet("color: #333; font: 16px 'SimHei';")

                # 热度标签 - 恢复热度颜色分级
                hot_label = QLabel(hot)
                hot_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                hot_label.setFixedWidth(100)

                # 恢复热度文本颜色分级
                hot_value = hot.replace(',' , '')
                try :
                    hot_num = int(hot_value)
                    if hot_num > 7000000 :
                        hot_label.setStyleSheet("color: #e53935; font: bold 16px 'SimHei';")
                    elif hot_num > 6000000 :
                        hot_label.setStyleSheet("color: #f4511e; font: bold 16px 'SimHei';")
                    elif hot_num > 5000000 :
                        hot_label.setStyleSheet("color: #fb8c00; font: bold 16px 'SimHei';")
                    else :
                        hot_label.setStyleSheet("color: #757575; font: 16px 'SimHei';")
                except :
                    hot_label.setStyleSheet("color: #757575; font: 16px 'SimHei';")

                # 添加到布局
                layout.addWidget(rank_label)
                layout.addWidget(title_label , 1)
                layout.addWidget(hot_label)

                # 统一行高
                row_height = 50
                widget.setMinimumHeight(row_height)
                widget.setMaximumHeight(row_height)
                list_item.setSizeHint(widget.sizeHint())

                # 设置widget到item
                self.news_list.setItemWidget(list_item , widget)

            self.status_label.setText(f"加载完成，共 {len(news_items[:100])} 条热搜")

        except Exception as e :
            error_item = QListWidgetItem(f"爬取新闻出错：{str(e)}")
            error_item.setTextAlignment(Qt.AlignCenter)
            error_item.setForeground(QColor(255 , 0 , 0))
            self.news_list.addItem(error_item)
            self.status_label.setText("加载失败")

# 小说下载线程，处理耗时的下载操作
class DownloadThread(QThread) :
    """
    小说下载线程类，继承自QThread，用于在后台处理小说章节的下载操作，
    避免阻塞主线程UI响应。通过信号与主线程通信，传递进度、日志和完成状态。
    """

    # 定义信号：进度更新（传递进度百分比）
    progress_updated = pyqtSignal(int)
    # 定义信号：消息更新（传递日志文本）
    message_received = pyqtSignal(str)
    # 定义信号：下载完成（传递成功状态和结果消息）
    download_completed = pyqtSignal(bool , str)

    """
        初始化下载线程

        Args:
            start_url (str): 小说起始章节的URL
            tag (str): 用于定位章节内容的HTML标签（如'div'、'p'等）
            attr_dict (dict): 章节内容标签的属性字典（如{'class': 'content'}）
            file_path (str): 小说保存的完整文件路径
            total_chapters (int, optional): 总章节数，用于精确计算进度。默认None（自动估算）
        """
    def __init__(self , start_url , tag , attr_dict ,choose_dict, file_path , total_chapters=None) :
        super().__init__()
        self.start_url = start_url  # 起始下载URL
        self.tag = tag  # 章节内容HTML标签
        self.attr_dict = attr_dict  # attr标签属性字典
        self.choose_dict = choose_dict  # choose标签属性字典
        self.file_path = file_path  # 保存文件路径
        self.total_chapters = total_chapters  # 总章节数（可选）
        self.stop_requested = False  # 停止请求标志（控制线程退出）
        self.current_chapter = 0  # 当前下载的章节数

    """
     线程执行入口函数，实现小说章节的循环下载逻辑：
     1. 从起始URL开始，依次下载每个章节内容
     2. 解析页面找到章节内容并写入文件
     3. 自动查找下一章链接，继续下载直到完成或被停止
     4. 通过信号实时反馈进度和状态
     """
    def run(self) :
        """
        线程执行入口函数，实现小说章节的循环下载逻辑：
        1. 从起始URL开始，依次下载每个章节内容
        2. 解析页面找到章节内容并写入文件
        3. 自动查找下一章链接，继续下载直到完成或被停止
        4. 通过信号实时反馈进度和状态
        """
        try :
            self.message_received.emit("开始下载小说...")
            url = self.start_url  # 初始化当前URL为起始URL

            # 打开文件准备写入（使用utf-8编码避免中文乱码）
            with open(self.file_path , 'w' , encoding = 'utf-8') as f :
                # 循环下载：当前URL有效且未收到停止请求时继续
                while url and not self.stop_requested :
                    c=0
                    wait_time = random.randint(10,20)/10
                    self.current_chapter += 1  # 章节计数递增

                    # 计算并发送进度
                    if self.total_chapters :
                        # 已知总章节数时，按实际比例计算进度（0-100）
                        progress = min(100 , int(self.current_chapter / self.total_chapters * 100))
                    else :
                        # 未知总章节数时，用当前章节数估算进度（最高99%，避免提前显示完成）
                        progress = min(99 , int(self.current_chapter / max(1 , self.current_chapter) * 100))
                    self.progress_updated.emit(progress)

                    # 发送当前下载状态日志
                    self.message_received.emit(f"正在下载第 {self.current_chapter} 章: {url}")

                    # 发送HTTP请求获取章节页面
                    response = requests.get(url)
                    # 自动识别页面编码，避免中文乱码
                    response.encoding = response.apparent_encoding
                    # 解析HTML内容
                    soup = BeautifulSoup(response.text , 'html.parser')

                    # 定位章节内容（根据指定的标签和属性）
                    content = soup.find(self.tag , self.attr_dict)
                    if content :
                        # 提取文本内容并写入文件，章节间添加空行分隔
                        chapter_text = content.get_text()
                        f.write(chapter_text + '\n\n')
                        self.message_received.emit(f"成功下载第 {self.current_chapter} 章")
                    else :
                        # 未找到内容时记录警告日志
                        self.message_received.emit(f"未找到第 {self.current_chapter} 章内容: {url}")

                    # 查找下一章链接
                    next_link = None
                    # 可能的"下一章"文本集合（支持多语言和符号）
                    next_texts = self.choose_dict
                    for next_text in next_texts :
                        # 精确匹配链接文本
                        next_link_element = soup.find('a' , string = next_text)
                        if next_link_element :
                            # 拼接相对URL为绝对URL
                            next_link = urljoin(url , next_link_element.get('href'))
                            break

                    # 如果未找到精确匹配的下一章链接，尝试模糊匹配
                    if not next_link :
                        # 获取所有<a>标签逐一检查
                        next_link_elements = soup.find_all('a')
                        for element in next_link_elements :
                            # 模糊匹配包含"下一章"或"next"的链接
                            if '下一章' in element.get_text() or 'next' in element.get_text().lower() :
                                next_link = urljoin(url , element.get('href'))
                                break

                    # 更新下一章URL，准备下一轮循环
                    url = next_link
                    # 延迟1-2秒，避免请求过于频繁被服务器拦截
                    self.message_received.emit(f"正在延迟请求{wait_time}秒")
                    time.sleep(wait_time)

            # 循环结束后判断退出原因
            if not self.stop_requested :
                # 正常完成下载
                self.download_completed.emit(True , f"小说下载完成！共下载 {self.current_chapter} 章")
            else :
                # 被用户停止下载
                self.download_completed.emit(False , "下载已取消")

        except Exception as e :
            # 下载过程中发生异常，发送失败信号
            self.download_completed.emit(False , f"下载失败: {str(e)}")

    """
    请求停止下载操作。
    通过设置停止标志位，让run()方法中的循环正常退出，避免线程强制终止导致的资源泄露。
    """
    def stop(self) :
        self.stop_requested = True

# 小说下载器的主窗口类，负责提供用户界面和控制下载流程
class NovelDownloadWindow(QWidget) :

    """初始化小说下载窗口"""
    def __init__(self , parent=None) :
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("小说下载器")
        self.setMinimumSize(800 , 900)
        self.init_ui()

        # 设置窗口位置在上一个窗口的左上角
        if parent and parent.isVisible() :
            parent_pos = parent.pos()
            self.move(parent_pos)

        # 加载保存的设置
        self.load_settings()
        self.download_thread = None

        # 美化UI
        self.setup_styles()

    """设置美化的UI样式，使用Qt样式表设置各控件的外观"""
    def setup_styles(self) :
       # 设置应用整体样式
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei";
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QProgressBar {
                border: 1px solid #aaa;
                border-radius: 4px;
                text-align: center;
                height: 24px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 1px;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                font-weight: bold;
                color: #333;
            }
        """)

        # 设置进度条颜色为绿色
        palette = self.progress_bar.palette()
        palette.setColor(palette.Highlight , QColor(76 , 175 , 80))  # 绿色
        self.progress_bar.setPalette(palette)

    """初始化用户界面，创建并布局所有UI控件"""
    def init_ui(self) :

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15 , 15 , 15 , 15)
        main_layout.setSpacing(15)

        # 创建输入区域组
        input_group = QGroupBox("下载设置")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)

        # 使用表单布局组织输入控件
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(12)

        # URL 输入框 - 用于输入小说起始页URL
        self.url_input = QLineEdit()
        form_layout.addRow("小说起始 URL:" , self.url_input)

        # 标签输入框 - 用于指定小说章节内容的HTML标签
        self.tag_input = QLineEdit()
        form_layout.addRow("章节内容标签:" , self.tag_input)

        # 属性输入框 - 用于指定章节内容标签的属性
        self.attr_input = QLineEdit()
        form_layout.addRow("章节内容属性:" , self.attr_input)

        # 选择器输入框 - 用于指定章节下一章按钮标签
        self.choose_input = QLineEdit()
        form_layout.addRow("章节下一章按钮文字:" , self.choose_input)

        # 保存路径选择
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        form_layout.addRow("保存路径:" , path_layout)

        # 文件名设置
        self.filename_input = QLineEdit()
        self.filename_input.setText("小说.txt")
        form_layout.addRow("保存文件名:" , self.filename_input)

        # 总章节数设置 - 设置为0表示自动估算总章节数
        self.total_chapters_input = QSpinBox()
        self.total_chapters_input.setRange(0 , 9999)
        self.total_chapters_input.setSuffix(" 章")
        self.total_chapters_input.setToolTip("设置为0表示自动估算总章节数")
        form_layout.addRow("总章节数:" , self.total_chapters_input)

        input_layout.addLayout(form_layout)

        # 保存设置按钮
        save_settings_button = QPushButton("保存设置")
        save_settings_button.setIcon(QIcon.fromTheme("document-save"))
        save_settings_button.clicked.connect(self.save_settings)
        input_layout.addWidget(save_settings_button)

        main_layout.addWidget(input_group)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.download_button = QPushButton("开始下载")
        self.download_button.setIcon(QIcon.fromTheme("download"))
        self.download_button.setMinimumHeight(40)
        self.download_button.clicked.connect(self.start_download)

        self.stop_button = QPushButton("停止下载")
        self.stop_button.setIcon(QIcon.fromTheme("process-stop"))
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_download)

        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        # 进度条 - 显示下载进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("准备中...")
        main_layout.addWidget(self.progress_bar)

        # 日志显示框 - 显示下载过程中的信息和错误
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("下载日志将显示在这里...")
        # 设置较小的字体
        font = QFont()
        font.setPointSize(9)
        self.log_display.setFont(font)
        # 设置日志区域为可拉伸
        self.log_display.setSizePolicy(QSizePolicy.Expanding , QSizePolicy.Expanding)
        main_layout.addWidget(self.log_display)

        self.setLayout(main_layout)

    """浏览并选择保存路径，打开文件对话框让用户选择保存目录"""
    def browse_path(self) :

        path = QFileDialog.getExistingDirectory(self , "选择保存目录")
        if path :
            self.path_input.setText(path)

    """保存用户设置到本地配置文件，包括URL、标签、属性等下载参数"""
    def save_settings(self) :

        settings = QSettings("MyCompany" , "NovelDownloader")
        settings.setValue("url" , self.url_input.text())
        settings.setValue("tag" , self.tag_input.text())
        settings.setValue("attr" , self.attr_input.text())
        settings.setValue("choose" , self.choose_input.text())
        settings.setValue("save_path" , self.path_input.text())
        settings.setValue("filename" , self.filename_input.text())
        settings.setValue("total_chapters" , self.total_chapters_input.value())
        dialog = CustomDialog("设置已保存" , title = "成功" , button_text = "OK" , parent = self)
        dialog.exec_()

    """从本地配置文件加载保存的用户设置"""
    def load_settings(self) :

        settings = QSettings("MyCompany" , "NovelDownloader")
        self.url_input.setText(settings.value("url" , ""))
        self.tag_input.setText(settings.value("tag" , ""))
        self.attr_input.setText(settings.value("attr" , ""))
        self.choose_input.setText(settings.value("choose" , ""))
        self.path_input.setText(settings.value("save_path" , os.getcwd()))
        self.filename_input.setText(settings.value("filename" , "小说.txt"))
        self.total_chapters_input.setValue(int(settings.value("total_chapters" , 0)))

    """
    开始下载小说，验证用户输入，初始化下载参数，创建并启动下载线程

    步骤：
    1. 获取并验证用户输入的参数
    2. 准备保存路径和文件
    3. 解析HTML属性
    4. 禁用下载按钮，启用停止按钮
    5. 创建并启动下载线程
    """
    def start_download(self) :
        url = self.url_input.text()
        tag = self.tag_input.text()
        attr = self.attr_input.text()
        choose = self.choose_input.text()
        save_path = self.path_input.text()
        filename = self.filename_input.text()
        total_chapters = self.total_chapters_input.value()

        total_chapters = total_chapters if total_chapters > 0 else None

        if not url or not tag or not attr :
            dialog = CustomDialog("请输入完整的 URL、标签和属性信息" , title = "警告" , button_text = "知道了" ,
                                  parent = self)
            dialog.exec_()
            return

        if not save_path or not filename :
            dialog = CustomDialog("请设置保存路径和文件名" , title = "警告" , button_text = "知道了" , parent = self)
            dialog.exec_()
            return

        try :
            # 确保保存路径存在
            if not os.path.exists(save_path) :
                os.makedirs(save_path)

            # 完整文件路径
            self.full_file_path = os.path.join(save_path , filename)

            # 解析attr属性为字典
            attr_dict = {}
            if '=' in attr :
                parts = attr.split('=')
                attr_dict[parts[0].strip()] = parts[1].strip()

            # 解析choose属性为列表
            choose_dict = []
            # 先处理英文逗号，若存在则拆分
            if ',' in choose :
                parts = choose.split(',')
            # 再处理中文逗号，若存在则拆分
            elif '，' in choose :
                parts = choose.split('，')
            else :
                # 若没有逗号，将整个字符串作为单个元素
                parts = [choose]
            # 去除每个元素的前后空格，添加到列表
            choose_list = [part.strip() for part in parts]

            # 禁用下载按钮，启用停止按钮，重置进度条和日志
            self.download_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("准备下载...")
            self.log_display.clear()

            # 创建并启动下载线程
            self.download_thread = DownloadThread(url , tag , attr_dict ,choose_dict, self.full_file_path , total_chapters)
            self.download_thread.progress_updated.connect(self.update_progress)
            self.download_thread.message_received.connect(self.append_log)
            self.download_thread.download_completed.connect(self.download_finished)

            # 启动线程
            self.download_thread.start()

            self.append_log("开始准备下载...")
            if total_chapters :
                self.append_log(f"已设置总章节数: {total_chapters}")
            else :
                self.append_log("未设置总章节数，将使用估算进度")
            self.append_log(f"文件将保存至: {self.full_file_path}")

        except Exception as e :
            self.append_log(f"初始化下载时出错: {str(e)}")
            self.download_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    """停止下载操作，向下载线程发送停止信号并禁用停止按钮"""
    def stop_download(self) :

        if self.download_thread and self.download_thread.isRunning() :
            self.append_log("正在停止下载...")
            self.download_thread.stop()
            # 禁用停止按钮，防止重复点击
            self.stop_button.setEnabled(False)

    """
    更新进度条显示
    Args:
        value: 进度值(0-100)
    """
    def update_progress(self , value) :

        self.progress_bar.setValue(value)
        if value < 100 :
            self.progress_bar.setFormat(f"下载中: {value}%")
        else :
            self.progress_bar.setFormat("下载完成!")

    """
     添加日志信息到日志显示框，并自动滚动到底部
      Args:
         message: 要添加的日志消息
     """
    def append_log(self , message) :

        self.log_display.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        # 自动滚动到底部
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    """
    下载完成后的处理函数，重置UI状态并显示结果对话框
    Args:
        success: 下载是否成功的布尔值
        message: 下载完成消息
    """
    def download_finished(self , success , message) :

        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100 if success else 0)
        self.append_log(message)

        if success :
            dialog = CustomDialog(f"{message}\n文件已保存至: {self.full_file_path}" , title = "成功" ,
                                  button_text = "OK" , parent = self)
            dialog.exec_()
        else :
            dialog = CustomDialog(message , title = "失败" , button_text = "知道了" , parent = self)
            dialog.exec_()

# 浏览器资源下载线程，处理各类资源的后台下载任务
class ResourceDownloadThread(QThread) :
    """资源下载线程，处理各类资源的后台下载任务"""
    progress_updated = pyqtSignal(int)
    message_received = pyqtSignal(str)
    download_completed = pyqtSignal(bool , str)

    def __init__(self , url , save_path , file_name=None) :
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.file_name = file_name
        self.stop_requested = False
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

    def run(self) :
        try :
            # 创建保存目录
            if not os.path.exists(self.save_path) :
                os.makedirs(self.save_path)

            # 确定文件名
            if not self.file_name :
                parsed_url = urlparse(self.url)
                self.file_name = os.path.basename(parsed_url.path)
                if not self.file_name :
                    self.file_name = f"download_{int(time.time())}"

            # 处理重复文件
            file_path = os.path.join(self.save_path , self.file_name)
            counter = 1
            while os.path.exists(file_path) :
                name , ext = os.path.splitext(self.file_name)
                self.file_name = f"{name}_{counter}{ext}"
                file_path = os.path.join(self.save_path , self.file_name)
                counter += 1

            # 获取文件大小
            try :
                head_response = self.session.head(self.url , allow_redirects = True , timeout = 10)
                total_size = int(head_response.headers.get('content-length' , 0))
            except :
                total_size = 0

            self.message_received.emit(f"开始下载: {self.file_name}")
            self.message_received.emit(f"保存路径: {file_path}")

            # 开始下载
            response = self.session.get(self.url , stream = True , allow_redirects = True , timeout = 30)
            response.raise_for_status()

            downloaded_size = 0
            chunk_size = 8192

            with open(file_path , 'wb') as f :
                for chunk in response.iter_content(chunk_size = chunk_size) :
                    if self.stop_requested :
                        if os.path.exists(file_path) :
                            os.remove(file_path)
                        self.download_completed.emit(False , "下载已取消")
                        return
                    if chunk :
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0 :
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
                        else :
                            # 未知文件大小，每下载1MB更新一次进度
                            if downloaded_size % (1024 * 1024) < chunk_size :
                                self.progress_updated.emit(min(99 , int(downloaded_size / (1024 * 1024))))

            # 验证文件完整性
            if total_size > 0 and os.path.getsize(file_path) != total_size :
                self.message_received.emit(
                    f"警告: 文件大小不匹配（预期: {total_size}, 实际: {os.path.getsize(file_path)}）")

            self.progress_updated.emit(100)
            self.download_completed.emit(True , f"下载完成: {file_path}")

        except Exception as e :
            self.download_completed.emit(False , f"下载失败: {str(e)}")

    def stop(self) :
        self.stop_requested = True

# 浏览器资源解析线程，负责提取网页中的各类资源链接
class ResourceParser(QThread) :
    """资源解析线程，负责提取网页中的各类资源链接"""
    parsing_finished = pyqtSignal(dict)
    message_received = pyqtSignal(str)

    def __init__(self , url , html_content) :
        super().__init__()
        self.url = url
        self.html_content = html_content

    def run(self) :
        try :
            self.message_received.emit("开始解析页面资源...")
            soup = BeautifulSoup(self.html_content , 'html.parser')
            resources = {
                'images' : [] ,
                'videos' : [] ,
                'audios' : [] ,
                'links' : [] ,
                'scripts' : [] ,
                'styles' : []
            }

            # 提取图片资源
            for img in soup.find_all('img') :
                for attr in ['src' , 'data-src' , 'srcset'] :
                    if img.get(attr) :
                        src = img[attr].split()[0] if attr == 'srcset' else img[attr]
                        img_url = urljoin(self.url , src)
                        if img_url not in resources['images'] :
                            resources['images'].append(img_url)

            # 提取视频资源
            for video in soup.find_all('video') :
                for attr in ['src' , 'data-src'] :
                    if video.get(attr) :
                        video_url = urljoin(self.url , video[attr])
                        if video_url not in resources['videos'] :
                            resources['videos'].append(video_url)
            for source in soup.find_all('source') :
                if source.get('src') and 'video' in source.get('type' , '') :
                    video_url = urljoin(self.url , source['src'])
                    if video_url not in resources['videos'] :
                        resources['videos'].append(video_url)

            # 提取音频资源
            for audio in soup.find_all('audio') :
                for attr in ['src' , 'data-src'] :
                    if audio.get(attr) :
                        audio_url = urljoin(self.url , audio[attr])
                        if audio_url not in resources['audios'] :
                            resources['audios'].append(audio_url)
            for source in soup.find_all('source') :
                if source.get('src') and 'audio' in source.get('type' , '') :
                    audio_url = urljoin(self.url , source['src'])
                    if audio_url not in resources['audios'] :
                        resources['audios'].append(audio_url)

            # 提取普通链接
            for link in soup.find_all('a') :
                if link.get('href') and not link.get('href' , '#').startswith('#') :
                    link_url = urljoin(self.url , link['href'])
                    if link_url not in resources['links'] :
                        resources['links'].append(link_url)

            # 提取脚本资源
            for script in soup.find_all('script') :
                if script.get('src') :
                    script_url = urljoin(self.url , script['src'])
                    if script_url not in resources['scripts'] :
                        resources['scripts'].append(script_url)

            # 提取样式资源
            for style in soup.find_all('link' , rel = 'stylesheet') :
                if style.get('href') :
                    style_url = urljoin(self.url , style['href'])
                    if style_url not in resources['styles'] :
                        resources['styles'].append(style_url)

            self.message_received.emit(
                f"资源解析完成: 图片{len(resources['images'])}个, 视频{len(resources['videos'])}个, 音频{len(resources['audios'])}个")
            self.parsing_finished.emit(resources)

        except Exception as e :
            self.message_received.emit(f"资源解析失败: {str(e)}")
            self.parsing_finished.emit({})

# 简易浏览器主窗口
class BrowserWindow(QWidget) :
    """简易浏览器主窗口"""

    def __init__(self , parent=None) :
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("简易浏览器 - 资源提取与下载")
        self.setMinimumSize(1200 , 800)

        # 初始化变量
        self.download_thread = None
        self.parser_thread = None
        self.history = []
        self.history_index = -1
        self.current_url = ""
        self.default_download_path = os.path.join(os.path.expanduser("~") , "Downloads")

        # 初始化UI
        self.init_ui()
        # 设置窗口位置在上一个窗口的左上角
        if parent and parent.isVisible() :
            parent_pos = parent.pos()
            self.move(parent_pos)
        self.load_settings()
        self.setup_styles()

    def init_ui(self) :
        # 主布局
        main_layout = QVBoxLayout(self)

        # 导航栏
        nav_layout = QHBoxLayout()

        self.back_btn = QPushButton("后退")
        self.back_btn.clicked.connect(self.go_back)
        self.forward_btn = QPushButton("前进")
        self.forward_btn.clicked.connect(self.go_forward)
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_page)
        self.home_btn = QPushButton("主页")
        self.home_btn.clicked.connect(self.go_home)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate)

        self.go_btn = QPushButton("前往")
        self.go_btn.clicked.connect(self.navigate)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.url_bar , 1)
        nav_layout.addWidget(self.go_btn)

        main_layout.addLayout(nav_layout)

        # 主内容区（拆分窗口）
        splitter = QSplitter(Qt.Vertical)

        # 网页视图
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("https://www.baidu.com"))
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.web_view.loadFinished.connect(self.on_page_loaded)

        # 资源面板
        resource_panel = QGroupBox("页面资源")
        resource_layout = QVBoxLayout()

        self.resource_tabs = QTabWidget()
        self.image_list = QListWidget()
        self.video_list = QListWidget()
        self.audio_list = QListWidget()
        self.link_list = QListWidget()
        self.script_list = QListWidget()
        self.style_list = QListWidget()

        self.resource_tabs.addTab(self.image_list , "图片")
        self.resource_tabs.addTab(self.video_list , "视频")
        self.resource_tabs.addTab(self.audio_list , "音频")
        self.resource_tabs.addTab(self.link_list , "链接")
        self.resource_tabs.addTab(self.script_list , "脚本")
        self.resource_tabs.addTab(self.style_list , "样式")

        # 下载设置
        download_layout = QFormLayout()
        self.download_path = QLineEdit()
        self.browse_download_btn = QPushButton("浏览...")
        self.browse_download_btn.clicked.connect(self.choose_download_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.download_path)
        path_layout.addWidget(self.browse_download_btn)
        download_layout.addRow("下载路径:" , path_layout)

        # 日志区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(100)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        resource_layout.addWidget(self.resource_tabs)
        resource_layout.addLayout(download_layout)
        resource_layout.addWidget(self.progress_bar)
        resource_layout.addWidget(self.log_display)
        resource_panel.setLayout(resource_layout)

        # 添加到拆分窗口
        splitter.addWidget(self.web_view)
        splitter.addWidget(resource_panel)
        splitter.setSizes([600 , 400])  # 设置初始大小比例

        main_layout.addWidget(splitter)

    def setup_styles(self) :
        """设置界面样式"""
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", sans-serif;
                font-size: 13px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                padding: 5px 10px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QProgressBar {
                height: 18px;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 3px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
            QTabBar::tab {
                padding: 6px 12px;
                border: 1px solid #ccc;
                margin-right: 2px;
                border-bottom-color: #ccc;
            }
            QTabBar::tab:selected {
                border-bottom-color: white;
                background-color: white;
                font-weight: bold;
            }
        """)

        # 设置日志字体
        font = QFont()
        font.setPointSize(10)
        self.log_display.setFont(font)

    def navigate(self) :
        """导航到URL栏中的地址"""
        url = self.url_bar.text().strip()
        if not url.startswith(('http://' , 'https://')) :
            url = f'http://{url}'
        self.web_view.setUrl(QUrl(url))

    def update_url_bar(self , qurl) :
        """更新URL栏显示"""
        self.url_bar.setText(qurl.toString())
        self.current_url = qurl.toString()

        # 更新历史记录
        if self.history and self.history[-1] == self.current_url :
            return
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_url)
        self.history_index = len(self.history) - 1
        self.update_nav_buttons()

    def on_page_loaded(self , success) :
        """页面加载完成后执行"""
        if success :
            self.log(f"页面加载完成: {self.current_url}")
            # 获取页面内容并解析资源
            self.web_view.page().toHtml(self.parse_page_resources)
        else :
            self.log(f"页面加载失败: {self.current_url}")
        self.progress_bar.setValue(0)

    def parse_page_resources(self , html) :
        """解析页面资源"""
        # 停止当前可能的解析线程
        if self.parser_thread and self.parser_thread.isRunning() :
            self.parser_thread.terminate()

        # 启动新的解析线程
        self.parser_thread = ResourceParser(self.current_url , html)
        self.parser_thread.parsing_finished.connect(self.display_resources)
        self.parser_thread.message_received.connect(self.log)
        self.parser_thread.start()

    def display_resources(self , resources) :
        """显示解析到的资源"""
        # 清空现有列表
        self.image_list.clear()
        self.video_list.clear()
        self.audio_list.clear()
        self.link_list.clear()
        self.script_list.clear()
        self.style_list.clear()

        # 添加资源到对应列表
        self.add_resources_to_list(self.image_list , resources['images'] , 'image')
        self.add_resources_to_list(self.video_list , resources['videos'] , 'video')
        self.add_resources_to_list(self.audio_list , resources['audios'] , 'audio')
        self.add_resources_to_list(self.link_list , resources['links'] , 'link')
        self.add_resources_to_list(self.script_list , resources['scripts'] , 'script')
        self.add_resources_to_list(self.style_list , resources['styles'] , 'style')

        self.log(f"资源解析完成 - 图片: {len(resources['images'])}, 视频: {len(resources['videos'])}, "
                 f"音频: {len(resources['audios'])}, 链接: {len(resources['links'])}")

    def add_resources_to_list(self , list_widget , resources , resource_type) :
        """将资源添加到列表控件"""
        for url in resources :
            item_widget = QWidget()
            layout = QHBoxLayout(item_widget)
            layout.setContentsMargins(2 , 2 , 2 , 2)

            # 显示URL（过长时截断）
            display_text = url if len(url) < 80 else f"{url[:77]}..."
            label = QLabel(display_text)
            label.setToolTip(url)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

            # 下载按钮
            download_btn = QPushButton("下载")
            download_btn.setMinimumWidth(60)
            download_btn.clicked.connect(lambda checked , u=url : self.download_resource(u))

            layout.addWidget(label , 1)
            layout.addWidget(download_btn)

            # 添加到列表
            list_item = QListWidgetItem(list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            list_widget.addItem(list_item)
            list_widget.setItemWidget(list_item , item_widget)

    def download_resource(self , url) :
        """下载指定资源"""
        if not url :
            self.log("无效的资源URL")
            return

        # 确定下载路径
        download_path = self.download_path.text().strip() or self.default_download_path

        # 停止当前可能的下载
        if self.download_thread and self.download_thread.isRunning() :
            self.download_thread.stop()
            self.download_thread.wait()

        # 启动下载线程
        file_name = os.path.basename(urlparse(url).path)
        self.download_thread = ResourceDownloadThread(url , download_path , file_name)
        self.download_thread.progress_updated.connect(self.progress_bar.setValue)
        self.download_thread.message_received.connect(self.log)
        self.download_thread.download_completed.connect(self.on_download_complete)
        self.download_thread.start()

    def on_download_complete(self , success , message) :
        """下载完成回调"""
        self.log(message)
        self.progress_bar.setValue(0)
        if success :
            QMessageBox.information(self , "下载完成" , message)

    def log(self , message) :
        """添加日志信息"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def go_back(self) :
        """后退"""
        if self.history_index > 0 :
            self.history_index -= 1
            self.web_view.setUrl(QUrl(self.history[self.history_index]))
            self.update_nav_buttons()

    def go_forward(self) :
        """前进"""
        if self.history_index < len(self.history) - 1 :
            self.history_index += 1
            self.web_view.setUrl(QUrl(self.history[self.history_index]))
            self.update_nav_buttons()

    def refresh_page(self) :
        """刷新当前页面"""
        self.web_view.reload()

    def go_home(self) :
        """回到主页"""
        self.web_view.setUrl(QUrl("https://www.baidu.com"))

    def update_nav_buttons(self) :
        """更新导航按钮状态"""
        self.back_btn.setEnabled(self.history_index > 0)
        self.forward_btn.setEnabled(self.history_index < len(self.history) - 1)

    def choose_download_path(self) :
        """选择下载路径"""
        path = QFileDialog.getExistingDirectory(self , "选择下载路径" , self.default_download_path)
        if path :
            self.download_path.setText(path)
            self.default_download_path = path

    def load_settings(self) :
        """加载保存的设置"""
        settings = QSettings("SimpleBrowser" , "Settings")
        self.download_path.setText(settings.value("download_path" , self.default_download_path))
        home_page = settings.value("home_page" , "https://www.baidu.com")
        self.web_view.setUrl(QUrl(home_page))

    def save_settings(self) :
        """保存设置"""
        settings = QSettings("SimpleBrowser" , "Settings")
        settings.setValue("download_path" , self.download_path.text())
        settings.setValue("home_page" , self.url_bar.text())

    def closeEvent(self , event) :
        """窗口关闭时保存设置"""
        self.save_settings()
        event.accept()

# 自定义ComboBox，可精确控制下拉列表高度
class FixedHeightComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setView(QTreeView())  # 使用树状视图

    def showPopup(self):
        """重写显示下拉列表的方法，设置固定高度"""
        super().showPopup()
        tree_view = self.view()
        tree_view.setFixedHeight(400)  # 强制设置为400px高度
        tree_view.setMinimumHeight(400)  # 确保至少400px
        tree_view.setMaximumHeight(400)  # 确保不超过400px

# 基础下载线程类
class VideoDownloadThread(QThread):
    """基础下载线程类"""
    progress_updated = pyqtSignal(int)
    message_received = pyqtSignal(str)
    download_completed = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True
        self.message_received.emit("正在停止下载...")

# M3U8 下载线程类
class M3U8VideoDownloadThread(VideoDownloadThread):
    """m3u8下载线程"""

    def __init__(self, url, save_path, ffmpeg_path, convert_to_mp4=True, file_name=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.ffmpeg_path = ffmpeg_path
        self.convert_to_mp4 = convert_to_mp4
        self.file_name = file_name
        self.total_segments = 0
        self.downloaded_segments = 0
        self.process = None  # 存储子进程引用

    @staticmethod
    def find_ffmpeg():
        """自动查找系统中的ffmpeg"""
        try:
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                return os.path.abspath(ffmpeg_path)

            if sys.platform.startswith('win'):
                paths = os.environ['PATH'].split(';')
                for path in paths:
                    ffmpeg_exe = os.path.join(path, 'ffmpeg.exe')
                    if os.path.exists(ffmpeg_exe) and os.path.isfile(ffmpeg_exe):
                        return os.path.abspath(ffmpeg_exe)
                return "ffmpeg.exe"
            else:
                common_paths = [
                    '/usr/bin/ffmpeg',
                    '/usr/local/bin/ffmpeg',
                    '/opt/homebrew/bin/ffmpeg',
                    '/usr/local/Cellar/ffmpeg/*/bin/ffmpeg'
                ]
                for path in common_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        return os.path.abspath(path)
                return "ffmpeg"
        except Exception as e:
            return "ffmpeg"

    def parse_m3u8(self, m3u8_content, base_url):
        """解析m3u8内容获取TS片段"""
        lines = m3u8_content.split('\n')
        segments = []

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#EXTINF:') or line.startswith('#EXT-X-KEY:'):
                try:
                    if i + 1 < len(lines):
                        ts_url = lines[i + 1].strip()
                        if not ts_url.startswith('http') and not ts_url.startswith('#'):
                            ts_url = urljoin(base_url, ts_url)
                        segments.append(ts_url)
                except Exception as e:
                    self.message_received.emit(f"解析m3u8出错: {str(e)}")

        return segments

    def merge_ts_files(self, ts_files, output_path):
        """合并TS文件"""
        if not ts_files:
            return False

        # 限制列表文件路径长度，防止过长路径导致问题
        max_path_length = 255
        if len(output_path) > max_path_length:
            self.message_received.emit(f"警告: 输出路径过长，可能导致合并失败")

        list_file = os.path.splitext(output_path)[0] + ".txt"

        # 确保列表文件路径有效
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for ts_file in ts_files:
                    # 检查每个片段路径长度
                    if len(ts_file) > max_path_length:
                        self.message_received.emit(f"警告: 片段路径过长: {ts_file[:50]}...")
                    f.write(f"file '{ts_file}'\n")
        except Exception as e:
            self.message_received.emit(f"创建列表文件失败: {str(e)}")
            return False

        self.message_received.emit("开始合并视频片段...")
        cmd = [
            self.ffmpeg_path,
            '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
        ]

        if self.convert_to_mp4:
            cmd.extend(['-c:v', 'copy', '-c:a', 'copy', output_path])
        else:
            cmd.extend(['-c', 'copy', output_path])

        try:
            self.progress_updated.emit(95)

            # 使用更安全的方式启动子进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith('win') else 0
            )

            for line in self.process.stdout:
                if self.stop_requested:
                    self.terminate_process()  # 使用安全的进程终止方法
                    return False
                if "frame=" in line:
                    self.message_received.emit(f"合并中: {line.strip()}")

            self.process.wait()

            if os.path.exists(list_file):
                os.remove(list_file)

            return self.process.returncode == 0

        except Exception as e:
            self.message_received.emit(f"合并出错: {str(e)}")
            return False
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)
            self.process = None  # 清理进程引用

    def terminate_process(self):
        """安全终止子进程"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)  # 等待5秒
            except Exception as e:
                self.message_received.emit(f"终止进程失败: {str(e)}")
                try:
                    self.process.kill()  # 强制终止
                except:
                    pass
            finally:
                self.process = None

    def run(self):
        """线程主执行函数"""
        try:
            # 生成随机临时目录
            temp_dir = os.path.join(os.getenv('TEMP', '/tmp'), f"m3u8_temp_{uuid.uuid4().hex}")
            os.makedirs(temp_dir, exist_ok=True)

            # 生成输出文件名
            if not self.file_name:
                # 从URL中提取文件名或生成随机名称
                base_name = urlparse(self.url).path.split('/')[-1]
                if not base_name or len(base_name) < 3:
                    base_name = f"video_{int(time.time())}"
                file_name = f"{os.path.splitext(base_name)[0]}.mp4" if self.convert_to_mp4 else base_name
            else:
                file_name = self.file_name
                # 确保文件名有正确的扩展名
                if self.convert_to_mp4 and not file_name.lower().endswith('.mp4'):
                    file_name += '.mp4'

            output_path = os.path.join(self.save_path, file_name)

            # 确保保存目录存在
            os.makedirs(self.save_path, exist_ok=True)

            # 解析M3U8文件获取片段列表
            segments = self.parse_m3u8_file(self.url)
            if not segments:
                self.download_completed.emit(False, "无法解析M3U8文件或没有可用片段")
                return

            self.total_segments = len(segments)
            self.message_received.emit(f"找到 {self.total_segments} 个视频片段")

            # 下载所有片段
            files = self.download_ts_segments(segments, temp_dir)

            if not files or self.stop_requested:
                if self.stop_requested:
                    self.download_completed.emit(False, "下载已取消")
                else:
                    self.download_completed.emit(False, "片段下载失败")
                return

            success = self.merge_ts_files(files, output_path)

            if success:
                self.progress_updated.emit(100)
                self.download_completed.emit(True, f"下载完成，保存至: {output_path}")
            else:
                self.download_completed.emit(False, "合并失败")

        except Exception as e:
            self.message_received.emit(f"致命错误: {str(e)}")
            self.download_completed.emit(False, f"处理出错: {str(e)}")
        finally:
            # 确保临时文件清理，无论成功或失败
            if os.path.exists(temp_dir):
                self.cleanup_temp_dir(temp_dir)

    def cleanup_temp_dir(self, temp_dir):
        """安全清理临时目录"""
        try:
            # 先尝试删除文件
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    self.message_received.emit(f"删除临时文件失败: {file} - {str(e)}")

            # 然后删除目录
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                self.message_received.emit(f"删除临时目录失败: {str(e)}")
        except Exception as e:
            self.message_received.emit(f"清理临时文件时出错: {str(e)}")

# 直接下载线程 - 用于MP4、FLV、F4V、WebM等格式
class DirectVideoDownloadThread(VideoDownloadThread):
    """直接下载线程 - 用于MP4、FLV、F4V、WebM等格式"""

    def __init__(self, url, save_path, file_name=None, expected_ext=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.file_name = file_name
        self.expected_ext = expected_ext

    def run(self):
        """线程主执行函数"""
        try:
            self.message_received.emit(f"开始处理地址: {self.url}")

            # 确保保存目录存在
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)

            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            # 尝试从URL提取文件名和扩展名
            url_basename = os.path.basename(urlparse(self.url).path).split('?')[0].split('#')[0]
            if '.' in url_basename:
                url_name, url_ext = os.path.splitext(url_basename)
                url_ext = url_ext[1:].lower()  # 移除点并转为小写
            else:
                url_name = url_basename
                url_ext = ""

            # 确定最终扩展名
            ext = self.expected_ext or url_ext or "mp4"

            # 确定最终文件名
            output_filename = self.file_name or f"video_{timestamp}.{ext}"
            output_path = os.path.join(self.save_path, output_filename)

            # 检查文件是否已存在
            counter = 1
            while os.path.exists(output_path):
                name, ext = os.path.splitext(output_filename)
                output_filename = f"{name}_{counter}{ext}"
                output_path = os.path.join(self.save_path, output_filename)
                counter += 1

            # 开始下载
            self.message_received.emit(f"开始下载至: {output_path}")
            session = requests.Session()
            session.max_redirects = 30

            try:
                # 获取文件大小
                head_response = session.head(self.url, allow_redirects=True, timeout=15)
                head_response.raise_for_status()
                file_size = int(head_response.headers.get('content-length', 0))
                final_url = head_response.url
            except Exception as e:
                self.message_received.emit(f"HEAD请求失败，尝试直接下载: {str(e)}")
                get_response = session.get(self.url, stream=True, allow_redirects=True, timeout=15)
                get_response.raise_for_status()
                file_size = int(get_response.headers.get('content-length', 0))
                final_url = get_response.url
                get_response.close()

            # 检查断点续传
            resume_pos = 0
            if os.path.exists(output_path):
                resume_pos = os.path.getsize(output_path)
                if file_size > 0 and resume_pos >= file_size:
                    self.download_completed.emit(True, f"文件已存在: {output_path}")
                    return
                elif file_size > 0:
                    self.message_received.emit(f"检测到部分文件，将从 {resume_pos} 字节继续下载")

            # 开始下载
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'

            response = session.get(final_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()

            mode = 'ab' if resume_pos > 0 else 'wb'
            downloaded_size = resume_pos
            chunk_size = 8192

            with open(output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.stop_requested:
                        response.close()
                        self.download_completed.emit(False, "下载已取消")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if file_size > 0:
                            progress = int((downloaded_size / file_size) * 100)
                            self.progress_updated.emit(progress)
                            if progress % 10 == 0:
                                self.message_received.emit(f"已下载 {downloaded_size}/{file_size} 字节 ({progress}%)")
                        else:
                            self.message_received.emit(f"已下载 {downloaded_size} 字节")

            # 验证文件大小
            if file_size > 0 and os.path.getsize(output_path) != file_size:
                self.message_received.emit(f"警告: 下载文件大小与预期不符 ({os.path.getsize(output_path)}/{file_size})")

            self.progress_updated.emit(100)
            self.download_completed.emit(True, f"下载完成，保存至: {output_path}")

        except Exception as e:
            self.download_completed.emit(False, f"下载失败: {str(e)}")

# 音频下载线程 - 用于MP3、WMA、WAV、M4A等格式
class AudioVideoDownloadThread(VideoDownloadThread):
    """音频下载线程 - 用于MP3、WMA、WAV、M4A等格式"""

    def __init__(self, url, save_path, ffmpeg_path, file_name=None, expected_ext=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.ffmpeg_path = ffmpeg_path
        self.file_name = file_name
        self.expected_ext = expected_ext

    def run(self):
        """线程主执行函数"""
        try:
            self.message_received.emit(f"开始处理音频地址: {self.url}")

            # 确保保存目录存在
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)

            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            # 尝试从URL提取文件名和扩展名
            url_basename = os.path.basename(urlparse(self.url).path).split('?')[0].split('#')[0]
            if '.' in url_basename:
                url_name, url_ext = os.path.splitext(url_basename)
                url_ext = url_ext[1:].lower()  # 移除点并转为小写
            else:
                url_name = url_basename
                url_ext = ""

            # 确定最终扩展名
            ext = self.expected_ext or url_ext or "mp3"

            # 确定最终文件名
            output_filename = self.file_name or f"audio_{timestamp}.{ext}"
            output_path = os.path.join(self.save_path, output_filename)

            # 检查文件是否已存在
            counter = 1
            while os.path.exists(output_path):
                name, ext = os.path.splitext(output_filename)
                output_filename = f"{name}_{counter}{ext}"
                output_path = os.path.join(self.save_path, output_filename)
                counter += 1

            # 开始下载
            self.message_received.emit(f"开始下载至: {output_path}")
            session = requests.Session()
            session.max_redirects = 30

            try:
                # 获取文件大小
                head_response = session.head(self.url, allow_redirects=True, timeout=15)
                head_response.raise_for_status()
                file_size = int(head_response.headers.get('content-length', 0))
                final_url = head_response.url
            except Exception as e:
                self.message_received.emit(f"HEAD请求失败，尝试直接下载: {str(e)}")
                get_response = session.get(self.url, stream=True, allow_redirects=True, timeout=15)
                get_response.raise_for_status()
                file_size = int(get_response.headers.get('content-length', 0))
                final_url = get_response.url
                get_response.close()

            # 检查断点续传
            resume_pos = 0
            if os.path.exists(output_path):
                resume_pos = os.path.getsize(output_path)
                if file_size > 0 and resume_pos >= file_size:
                    self.download_completed.emit(True, f"文件已存在: {output_path}")
                    return
                elif file_size > 0:
                    self.message_received.emit(f"检测到部分文件，将从 {resume_pos} 字节继续下载")

            # 开始下载
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'

            response = session.get(final_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()

            mode = 'ab' if resume_pos > 0 else 'wb'
            downloaded_size = resume_pos
            chunk_size = 8192

            with open(output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.stop_requested:
                        response.close()
                        self.download_completed.emit(False, "下载已取消")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if file_size > 0:
                            progress = int((downloaded_size / file_size) * 100)
                            self.progress_updated.emit(progress)
                            if progress % 10 == 0:
                                self.message_received.emit(f"已下载 {downloaded_size}/{file_size} 字节 ({progress}%)")
                        else:
                            self.message_received.emit(f"已下载 {downloaded_size} 字节")

            # 验证文件大小
            if file_size > 0 and os.path.getsize(output_path) != file_size:
                self.message_received.emit(f"警告: 下载文件大小与预期不符 ({os.path.getsize(output_path)}/{file_size})")

            # 如果是需要转换的格式，使用FFmpeg转换
            if self.ffmpeg_path and ext not in ['mp3', 'wav']:
                self.message_received.emit("开始转换音频格式...")
                converted_path = os.path.splitext(output_path)[0] + ".mp3"
                cmd = [
                    self.ffmpeg_path,
                    '-y',
                    '-i', output_path,
                    '-vn',
                    '-c:a', 'libmp3lame',
                    '-q:a', '2',
                    converted_path
                ]

                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )

                    for line in process.stdout:
                        if self.stop_requested:
                            process.terminate()
                            self.download_completed.emit(False, "转换已取消")
                            return

                    process.wait()

                    if process.returncode == 0:
                        os.remove(output_path)  # 删除原始文件
                        output_path = converted_path
                        self.message_received.emit("音频格式转换完成")
                    else:
                        self.message_received.emit(f"格式转换失败，保留原始文件")

                except Exception as e:
                    self.message_received.emit(f"格式转换出错: {str(e)}")

            self.progress_updated.emit(100)
            self.download_completed.emit(True, f"下载完成，保存至: {output_path}")

        except Exception as e:
            self.download_completed.emit(False, f"下载失败: {str(e)}")

# 自适应下载线程 - 用于HLS、DASH等格式
class AdaptiveVideoDownloadThread(VideoDownloadThread):
    """自适应下载线程 - 用于HLS、DASH等格式"""

    def __init__(self, url, save_path, ffmpeg_path, file_name=None, format_type=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.ffmpeg_path = ffmpeg_path
        self.file_name = file_name
        self.format_type = format_type or "mp4"

    def run(self):
        """线程主执行函数"""
        try:
            self.message_received.emit(f"开始处理自适应流地址: {self.url}")

            # 验证FFmpeg
            try:
                subprocess.run(
                    [self.ffmpeg_path, '-version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as e:
                self.download_completed.emit(False, f"FFmpeg不可用: {str(e)}")
                return

            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_filename = self.file_name or f"video_{timestamp}.{self.format_type}"
            output_path = os.path.join(self.save_path, output_filename)

            self.message_received.emit(f"开始使用FFmpeg下载...")

            # 使用FFmpeg直接下载自适应流
            cmd = [
                self.ffmpeg_path,
                '-y',
                '-i', self.url,
                '-c', 'copy',
                output_path
            ]

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )

                while process.poll() is None:
                    if self.stop_requested:
                        process.terminate()
                        self.download_completed.emit(False, "下载已取消")
                        return
                    time.sleep(0.5)

                if process.returncode == 0:
                    self.progress_updated.emit(100)
                    self.download_completed.emit(True, f"下载完成，保存至: {output_path}")
                else:
                    self.download_completed.emit(False, f"下载失败，FFmpeg返回代码: {process.returncode}")

            except Exception as e:
                self.download_completed.emit(False, f"下载出错: {str(e)}")

        except Exception as e:
            self.download_completed.emit(False, f"处理出错: {str(e)}")

# 新增：图片下载线程类
class ImageDownloadThread(VideoDownloadThread):
    """图片下载线程"""

    def __init__(self, url, save_path, file_name=None, expected_ext=None):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.file_name = file_name
        self.expected_ext = expected_ext

    def run(self):
        """线程主执行函数"""
        try:
            self.message_received.emit(f"开始处理图片地址: {self.url}")

            # 确保保存目录存在
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)

            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")

            # 尝试从URL提取文件名和扩展名
            url_basename = os.path.basename(urlparse(self.url).path).split('?')[0].split('#')[0]
            if '.' in url_basename:
                url_name, url_ext = os.path.splitext(url_basename)
                url_ext = url_ext[1:].lower()  # 移除点并转为小写
            else:
                url_name = url_basename
                url_ext = ""

            # 确定最终扩展名
            ext = self.expected_ext or url_ext or "jpg"

            # 常见图片格式映射
            image_formats = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"]
            if ext not in image_formats:
                ext = "jpg"  # 默认为JPG

            # 确定最终文件名
            output_filename = self.file_name or f"image_{timestamp}.{ext}"
            output_path = os.path.join(self.save_path, output_filename)

            # 检查文件是否已存在
            counter = 1
            while os.path.exists(output_path):
                name, ext = os.path.splitext(output_filename)
                output_filename = f"{name}_{counter}{ext}"
                output_path = os.path.join(self.save_path, output_filename)
                counter += 1

            # 开始下载
            self.message_received.emit(f"开始下载至: {output_path}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }

            try:
                # 发送HEAD请求获取内容类型
                head_response = requests.head(self.url, headers=headers, timeout=15)
                head_response.raise_for_status()

                content_type = head_response.headers.get('content-type', '').lower()
                if 'image' not in content_type:
                    self.download_completed.emit(False, f"URL指向的不是图片类型: {content_type}")
                    return

                # 尝试从Content-Type确定扩展名
                if not ext and 'content-type' in head_response.headers:
                    content_type = head_response.headers['content-type'].lower()
                    if 'jpeg' in content_type:
                        ext = 'jpg'
                    elif 'png' in content_type:
                        ext = 'png'
                    elif 'gif' in content_type:
                        ext = 'gif'
                    elif 'webp' in content_type:
                        ext = 'webp'
                    elif 'svg' in content_type:
                        ext = 'svg'
                    elif 'bmp' in content_type:
                        ext = 'bmp'
                    elif 'tiff' in content_type:
                        ext = 'tiff'

                # 如果扩展名无效，使用从Content-Type确定的扩展名
                if ext not in image_formats and 'content-type' in head_response.headers:
                    output_filename = f"image_{timestamp}.{ext}"
                    output_path = os.path.join(self.save_path, output_filename)

                # 获取文件大小
                file_size = int(head_response.headers.get('content-length', 0))

            except Exception as e:
                self.message_received.emit(f"HEAD请求失败，直接下载: {str(e)}")
                file_size = 0

            # 开始下载
            try:
                response = requests.get(self.url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    downloaded_size = 0
                    chunk_size = 8192

                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if self.stop_requested:
                            response.close()
                            self.download_completed.emit(False, "下载已取消")
                            return
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if file_size > 0:
                                progress = int((downloaded_size / file_size) * 100)
                                self.progress_updated.emit(progress)
                                if progress % 10 == 0:
                                    self.message_received.emit(
                                        f"已下载 {downloaded_size}/{file_size} 字节 ({progress}%)")
                            else:
                                self.message_received.emit(f"已下载 {downloaded_size} 字节")

                # 验证文件大小
                if file_size > 0 and os.path.getsize(output_path) != file_size:
                    self.message_received.emit(
                        f"警告: 下载文件大小与预期不符 ({os.path.getsize(output_path)}/{file_size})")

                self.progress_updated.emit(100)
                self.download_completed.emit(True, f"图片下载完成，保存至: {output_path}")

            except Exception as e:
                self.download_completed.emit(False, f"图片下载失败: {str(e)}")

        except Exception as e:
            self.download_completed.emit(False, f"处理出错: {str(e)}")

# 视频下载器主窗口类
class VideoDownloadWindow(QWidget):
    """视频下载器主窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.Window)
        self.VIDEO_OUTPUT_DIR = "video_output"
        self.MUSIC_OUTPUT_DIR = "music_output"
        self.IMAGE_OUTPUT_DIR = "image_output"  # 新增图片输出目录
        self.ensure_output_dirs_exist()
        self.init_ui()
        self.load_settings()
        self.download_thread = None  # 初始化下载线程变量
        # 设置窗口位置在上一个窗口的左上角
        if parent and parent.isVisible():
            parent_pos = parent.pos()
            self.move(parent_pos)

    def ensure_output_dirs_exist(self):
        """确保默认输出目录存在"""
        if not os.path.exists(self.VIDEO_OUTPUT_DIR):
            os.makedirs(self.VIDEO_OUTPUT_DIR)
        if not os.path.exists(self.MUSIC_OUTPUT_DIR):
            os.makedirs(self.MUSIC_OUTPUT_DIR)
        if not os.path.exists(self.IMAGE_OUTPUT_DIR):  # 新增图片目录检查
            os.makedirs(self.IMAGE_OUTPUT_DIR)

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("多功能下载器")  # 标题改为更通用的名称
        self.setMinimumSize(800, 900)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 设置区域
        settings_group = QGroupBox("下载设置")
        settings_layout = QFormLayout()
        settings_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        settings_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        settings_layout.setSpacing(10)

        # URL输入
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入视频、音频或图片URL")  # 更新提示文本
        settings_layout.addRow("URL:", self.url_input)

        # 美化的格式选择器
        format_layout = QHBoxLayout()
        self.format_combo = FixedHeightComboBox()  # 使用自定义ComboBox
        self.format_combo.setMinimumWidth(250)

        # 添加视频格式分组
        video_group = QStandardItem("视频格式")
        video_group.setFlags(Qt.ItemIsEnabled)  # 分组项不可选
        video_formats = [
            "MP4", "FLV", "F4V", "WebM", "MOV", "MKV",
            "AVI", "WMV", "ASF", "DIVX", "MPEG4", "OGV"
        ]

        # 添加音频格式分组
        audio_group = QStandardItem("音频格式")
        audio_group.setFlags(Qt.ItemIsEnabled)
        audio_formats = [
            "MP3", "WMA", "WAV", "M4A", "AAC", "OGG", "OPUS", "WEBA"
        ]

        # 添加图片格式分组（新增）
        image_group = QStandardItem("图片格式")
        image_group.setFlags(Qt.ItemIsEnabled)
        image_formats = [
            "JPG", "PNG", "GIF", "BMP", "WebP", "SVG", "TIFF"
        ]

        # 添加流媒体格式分组
        stream_group = QStandardItem("流媒体格式")
        stream_group.setFlags(Qt.ItemIsEnabled)
        stream_formats = [
            "M3U8", "HLS", "M3U", "MPD"
        ]

        # 创建模型并添加分组
        model = QStandardItemModel()
        model.insertRow(0, QStandardItem("自动检测"))
        model.appendRow(video_group)
        for fmt in video_formats:
            item = QStandardItem(fmt)
            video_group.appendRow(item)

        model.appendRow(audio_group)
        for fmt in audio_formats:
            item = QStandardItem(fmt)
            audio_group.appendRow(item)

        # 添加图片格式
        model.appendRow(image_group)
        for fmt in image_formats:
            item = QStandardItem(fmt)
            image_group.appendRow(item)

        model.appendRow(stream_group)
        for fmt in stream_formats:
            item = QStandardItem(fmt)
            stream_group.appendRow(item)

        self.format_combo.setModel(model)
        self.format_combo.setCurrentIndex(0)  # 默认选中自动检测

        # 增强树状图视觉效果
        self.format_combo.setView(QTreeView())
        tree_view = self.format_combo.view()
        tree_view.setHeaderHidden(True)  # 确保表头被隐藏
        tree_view.setIndentation(15)

        # 设置样式表（移除max-height限制）
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                border-left: 1px solid #ccc;
                border-radius: 0 4px 4px 0;
            }
            QTreeView {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
            }
            QTreeView::item {
                height: 22px;
                border-radius: 2px;
            }
            QTreeView::item:selected {
                background-color: #E6F2FF;
                color: #2196F3;
            }
            QTreeView::item:hover:!selected {
                background-color: #F0F0F0;
            }
            QTreeView::item:has-children {
                font-weight: bold;
                color: #555;
            }
        """)

        format_layout.addWidget(QLabel("格式:"))
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        settings_layout.addRow("", format_layout)

        # 文件名
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("留空则自动生成")
        settings_layout.addRow("文件名:", self.filename_input)

        # FFmpeg路径
        ffmpeg_layout = QHBoxLayout()
        self.ffmpeg_input = QLineEdit()
        ffmpeg_browse_btn = QPushButton("浏览...")
        ffmpeg_browse_btn.clicked.connect(self.browse_ffmpeg)
        ffmpeg_layout.addWidget(self.ffmpeg_input)
        ffmpeg_layout.addWidget(ffmpeg_browse_btn)
        settings_layout.addRow("FFmpeg路径:", ffmpeg_layout)

        # 保存路径
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        path_browse_btn = QPushButton("浏览...")
        path_browse_btn.clicked.connect(self.browse_save_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_browse_btn)
        settings_layout.addRow("视频保存路径:", path_layout)

        # 新增：音乐保存路径
        music_path_layout = QHBoxLayout()
        self.music_path_input = QLineEdit()
        music_browse_btn = QPushButton("浏览...")
        music_browse_btn.clicked.connect(self.browse_music_save_path)
        music_path_layout.addWidget(self.music_path_input)
        music_path_layout.addWidget(music_browse_btn)
        settings_layout.addRow("音乐保存路径:", music_path_layout)

        # 新增：图片保存路径
        image_path_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setText(self.IMAGE_OUTPUT_DIR)  # 设置默认图片路径
        image_browse_btn = QPushButton("浏览...")
        image_browse_btn.clicked.connect(self.browse_image_save_path)
        image_path_layout.addWidget(self.image_path_input)
        image_path_layout.addWidget(image_browse_btn)
        settings_layout.addRow("图片保存路径:", image_path_layout)

        # 转换选项
        self.convert_checkbox = QCheckBox("转换为MP4/MP3格式")
        self.convert_checkbox.setChecked(True)
        settings_layout.addRow("格式设置:", self.convert_checkbox)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("开始下载")
        self.download_btn.clicked.connect(self.start_download)
        self.stop_btn = QPushButton("停止下载")
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        self.save_settings_btn = QPushButton("保存设置")
        self.save_settings_btn.clicked.connect(self.save_settings)

        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.save_settings_btn)
        settings_layout.addRow("", btn_layout)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # 公共日志和进度区域
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("准备就绪")
        progress_layout.addWidget(self.progress_bar)

        log_group = QGroupBox("下载日志")
        log_layout = QVBoxLayout()
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        font = QFont()
        font.setPointSize(9)
        self.log_display.setFont(font)
        log_layout.addWidget(self.log_display)
        log_group.setLayout(log_layout)
        progress_layout.addWidget(log_group)

        main_layout.addLayout(progress_layout)

        self.setLayout(main_layout)
        self.setup_styles()

    def setup_styles(self):
        """设置界面样式"""
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei", sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                transition: all 0.2s;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                box-shadow: 0 0 5px rgba(33, 150, 243, 0.5);
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                transition: all 0.2s;
            }
            QPushButton:hover {
                background-color: #0b7dda;
                transform: translateY(-1px);
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                transform: translateY(0);
                box-shadow: none;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
                cursor: not-allowed;
            }
            QProgressBar {
                height: 24px;
                border-radius: 4px;
                text-align: center;
                border: 1px solid #ccc;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
                transition: width 0.3s ease;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                border-left: 1px solid #ccc;
                border-radius: 0 4px 4px 0;
            }
            QComboBox::down-arrow {
                image: url(:/icons/down_arrow.png);
                width: 16px;
                height: 16px;
            }
            QTreeView {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
            }
            QTreeView::item {
                height: 22px;
                border-radius: 2px;
            }
            QTreeView::item:selected {
                background-color: #E6F2FF;
                color: #2196F3;
            }
            QTreeView::item:hover:!selected {
                background-color: #F0F0F0;
            }
            QTreeView::item:has-children {
                font-weight: bold;
                color: #555;
            }
        """)

    def browse_ffmpeg(self):
        filter_str = "可执行文件 (*.exe);;所有文件 (*)" if sys.platform.startswith('win') else "所有文件 (*)"
        path, _ = QFileDialog.getOpenFileName(self, "选择FFmpeg", "", filter_str)
        if path:
            self.ffmpeg_input.setText(path)

    def browse_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择视频保存目录")
        if path:
            self.path_input.setText(path)

    def browse_music_save_path(self):
        """浏览并设置音乐保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择音乐保存目录")
        if path:
            self.music_path_input.setText(path)

    def browse_image_save_path(self):
        """浏览并设置图片保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择图片保存目录")
        if path:
            self.image_path_input.setText(path)

    def start_download(self):
        url = self.url_input.text().strip()
        ffmpeg_path = self.ffmpeg_input.text().strip()
        save_path = self.path_input.text().strip()
        file_name = self.filename_input.text().strip()
        selected_format = self.format_combo.currentText().lower()
        convert_to_mp4 = self.convert_checkbox.isChecked()

        if not url:
            dialog = CustomDialog("请输入URL", title="输入错误", button_text='知道了', parent=self)
            dialog.exec_()
            return

        # 根据格式决定保存位置
        detected_format = self.detect_format(url)
        format_to_use = selected_format if selected_format != "自动检测" else detected_format

        # 改进的格式检测（新增）
        if format_to_use == "unknown":
            # 尝试通过HEAD请求检测内容类型
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                }
                response = requests.head(url, headers=headers, timeout=10)
                content_type = response.headers.get('content-type', '').lower()

                if 'video' in content_type:
                    format_to_use = "mp4"
                elif 'audio' in content_type:
                    format_to_use = "mp3"
                elif 'image' in content_type:
                    format_to_use = "jpg"
                else:
                    format_to_use = "unknown"
            except Exception as e:
                self.append_log(f"自动检测失败: {str(e)}")

        # 如果用户没有指定保存路径，使用默认的分类保存路径
        if not save_path:
            if format_to_use in ["mp3", "wma", "wav", "m4a", "aac", "ogg", "opus", "weba"]:
                save_path = self.music_path_input.text() or self.MUSIC_OUTPUT_DIR
            elif format_to_use in ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"]:  # 新增图片判断
                save_path = self.image_path_input.text() or self.IMAGE_OUTPUT_DIR
            else:
                save_path = self.path_input.text() or self.VIDEO_OUTPUT_DIR

        # 确保保存目录存在
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
            except Exception as e:
                QMessageBox.warning(self, "路径错误", f"无法创建保存目录: {str(e)}")
                return

        # 检查FFmpeg是否需要
        if format_to_use in ["m3u8", "hls", "mpd", "m3u", "webm", "ogg", "ogv", "aac", "opus", "weba"]:
            if not ffmpeg_path or not os.path.exists(ffmpeg_path):
                auto_ffmpeg = M3U8VideoDownloadThread.find_ffmpeg()
                if os.path.exists(auto_ffmpeg):
                    self.ffmpeg_input.setText(auto_ffmpeg)
                    ffmpeg_path = auto_ffmpeg
                else:
                    QMessageBox.warning(self, "配置错误", "处理此格式需要FFmpeg，请设置有效的FFmpeg路径")
                    return

        self.save_settings()

        # 根据格式选择合适的下载线程（改进）
        if format_to_use in ["m3u8", "hls", "m3u"]:
            self.download_thread = M3U8VideoDownloadThread(
                url=url,
                save_path=save_path,
                ffmpeg_path=ffmpeg_path,
                convert_to_mp4=convert_to_mp4,
                file_name=file_name
            )
        elif format_to_use in ["mpd"]:
            self.download_thread = AdaptiveVideoDownloadThread(
                url=url,
                save_path=save_path,
                ffmpeg_path=ffmpeg_path,
                file_name=file_name,
                format_type="mp4"
            )
        elif format_to_use in ["mp3", "wma", "wav", "m4a", "aac", "opus", "weba"]:
            self.download_thread = AudioVideoDownloadThread(
                url=url,
                save_path=save_path,
                ffmpeg_path=ffmpeg_path,
                file_name=file_name,
                expected_ext=format_to_use
            )
        elif format_to_use in ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"]:  # 新增图片下载
            self.download_thread = ImageDownloadThread(
                url=url,
                save_path=save_path,
                file_name=file_name,
                expected_ext=format_to_use
            )
        else:
            # 默认为直接下载（改进了MP4的处理）
            self.download_thread = DirectVideoDownloadThread(
                url=url,
                save_path=save_path,
                file_name=file_name,
                expected_ext=format_to_use
            )

        # 统一的信号连接和线程启动逻辑
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.message_received.connect(self.append_log)
        self.download_thread.download_completed.connect(self.download_finished)

        self.download_thread.start()
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_download(self):
        """安全停止下载线程"""
        if self.download_thread and self.download_thread.isRunning():
            self.append_log("正在停止下载线程...")
            self.download_thread.stop()
            # 等待线程结束
            if not self.download_thread.wait(5000):  # 等待5秒
                self.append_log("下载线程未能及时停止，强制终止")
                self.download_thread.terminate()
                self.download_thread.wait()  # 确保线程已停止
            self.download_thread = None
            self.stop_btn.setEnabled(False)

    def disconnect_signals(self):
        """断开所有线程信号连接"""
        if self.download_thread:
            try:
                self.download_thread.progress_updated.disconnect()
                self.download_thread.message_received.disconnect()
                self.download_thread.download_completed.disconnect()
            except Exception as e:
                # 忽略已断开的信号
                pass

    def download_finished(self, success, message):
        self.append_log(message)
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if success:
            self.progress_bar.setFormat("下载完成")
            QMessageBox.information(self, "成功", message)
            # 清空输入框，准备下一次下载
            self.url_input.clear()
            self.append_log("等待下一次下载...")
        else:
            self.progress_bar.setFormat("下载失败")
            QMessageBox.warning(self, "失败", message)

        self.download_thread = None

    def save_settings(self):
        """保存设置到配置文件"""
        settings = QSettings("VideoDownloader", "GeneralSettings")
        settings.setValue("ffmpeg_path", self.ffmpeg_input.text())
        settings.setValue("video_save_path", self.path_input.text())
        settings.setValue("music_save_path", self.music_path_input.text())
        settings.setValue("image_save_path", self.image_path_input.text())  # 新增图片路径保存
        settings.setValue("convert_to_mp4", self.convert_checkbox.isChecked())
        settings.setValue("last_format", self.format_combo.currentText())
        self.append_log("设置已保存")

    def load_settings(self):
        """从配置文件加载设置"""
        settings = QSettings("VideoDownloader", "GeneralSettings")
        self.ffmpeg_input.setText(settings.value("ffmpeg_path", ""))
        self.path_input.setText(settings.value("video_save_path", ""))
        self.music_path_input.setText(settings.value("music_save_path", ""))
        self.image_path_input.setText(settings.value("image_save_path", ""))
        convert_to_mp4 = settings.value("convert_to_mp4", True, type=bool)
        self.convert_checkbox.setChecked(convert_to_mp4)

        last_format = settings.value("last_format", "自动检测")
        format_index = self.format_combo.findText(last_format)
        if format_index >= 0:
            self.format_combo.setCurrentIndex(format_index)

        self.append_log("设置已加载")

    def detect_format(self, url):
        """尝试从URL检测格式"""
        url = url.lower()
        video_formats = ["mp4", "flv", "f4v", "webm", "mov", "mkv", "avi", "wmv", "asf", "divx", "mpeg4",
                         "ogv"]
        audio_formats = ["mp3", "wma", "wav", "m4a", "aac", "ogg", "opus", "weba"]
        image_formats = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"]
        stream_formats = ["m3u8", "hls", "m3u", "mpd"]

        # 检查是否是流媒体格式
        for fmt in stream_formats:
            if f".{fmt}" in url or f"{fmt}?" in url or f"{fmt}=" in url:
                return fmt

        # 检查是否是视频格式
        for fmt in video_formats:
            if f".{fmt}" in url or f"{fmt}?" in url or f"{fmt}=" in url:
                return fmt

        # 检查是否是音频格式
        for fmt in audio_formats:
            if f".{fmt}" in url or f"{fmt}?" in url or f"{fmt}=" in url:
                return fmt

        # 检查是否是图片格式
        for fmt in image_formats:
            if f".{fmt}" in url or f"{fmt}?" in url or f"{fmt}=" in url:
                return fmt

        # 检查常见的流媒体服务
        if "youtube.com" in url or "youtu.be" in url:
            return "mp4"
        elif "vimeo.com" in url:
            return "mp4"
        elif "dailymotion.com" in url:
            return "mp4"
        elif "bilibili.com" in url or "b23.tv" in url:
            return "flv"
        elif "tiktok.com" in url or "douyin.com" in url:
            return "mp4"
        elif "soundcloud.com" in url:
            return "mp3"
        elif "spotify.com" in url:
            return "mp3"
        elif "pinterest.com" in url or "imgur.com" in url or "unsplash.com" in url:
            return "jpg"

        return "unknown"

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")

    def append_log(self , message) :
        """添加日志信息"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_display.insertPlainText(log_entry)
        # 自动滚动到底部
        self.log_display.moveCursor(QTextCursor.End)

# 主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 确保中文显示正常
    font = QFont("SimHei")
    app.setFont(font)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())