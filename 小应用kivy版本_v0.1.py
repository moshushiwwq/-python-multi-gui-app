import sys
import re
import uuid
import subprocess
import time
import shutil
import hashlib
import pickle
import os

from kivy.uix.button import Button
import aiohttp
import asyncio
import random
from urllib.parse import urljoin , urlparse
import requests
from bs4 import BeautifulSoup
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView

Config.set('kivy' , 'default_font' , [
    'SimHei' ,
    'C:/Windows/Fonts/simhei.ttf'
])
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager , Screen , SlideTransition
from kivy.core.window import Window
from kivy.graphics import Color , Rectangle , RoundedRectangle , Line , PushMatrix , PopMatrix
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.properties import StringProperty , ObjectProperty , BooleanProperty , NumericProperty , ListProperty
from kivy.uix.treeview import TreeView , TreeViewLabel
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.togglebutton import ToggleButton

Window.clearcolor = (0.95 , 0.95 , 0.95 , 1)


# 哈希加密函数
def hash_string(string) :
    return hashlib.sha256(string.encode()).hexdigest()


# 保存用户信息
def save_users_info(users_info) :
    with open('usr_info.pickle' , 'wb') as usr_file :
        pickle.dump(users_info , usr_file)


# 加载用户信息
def load_users_info() :
    try :
        with open('usr_info.pickle' , 'rb') as usr_file :
            return pickle.load(usr_file)
    except FileNotFoundError :
        return {}


# 自定义对话框类
class CustomDialog(Popup) :
    def __init__(self , text , title , button_text , **kwargs) :
        super().__init__(**kwargs)
        self.title = title
        self.size_hint = (0.7 , 0.4)

        layout = BoxLayout(orientation = 'vertical' , padding = dp(20) , spacing = dp(15))

        # 消息内容
        content_label = Label(
            text = text ,
            font_name = 'simhei.ttf' ,
            size_hint_y = None ,
            height = dp(80)
        )
        layout.add_widget(content_label)

        # 按钮
        btn = RoundedButton(
            text = button_text ,
            background_color = (0.3 , 0.7 , 0.3 , 1) ,
            color = (1 , 1 , 1 , 1) ,
            size_hint = (1 , None) ,
            height = dp(40) ,
            radius = dp(20)
        )
        btn.bind(on_press = self.dismiss)
        layout.add_widget(btn)

        self.content = layout


# 自定义按钮类
class RoundedButton(ButtonBehavior , BoxLayout) :
    text = StringProperty('')
    background_color = ObjectProperty((1 , 1 , 1 , 1))  # 按钮背景色
    color = ObjectProperty((0 , 0 , 0 , 1))  # 文字颜色
    font_name = StringProperty('simhei.ttf')
    font_size = ObjectProperty(dp(14))
    radius = ListProperty([dp(10)])  # 圆角半径
    width_ratio = NumericProperty(0.8)  # 相对于父容器的宽度比例

    def __init__(self , **kwargs) :
        # 处理可能传入的单个radius值
        if 'radius' in kwargs :
            radius = kwargs['radius']
            if not isinstance(radius , list) :
                kwargs['radius'] = [radius]

        super().__init__(** kwargs)
        self.orientation = 'horizontal'
        self.padding = [dp(20) , dp(5)]
        self.size_hint_y = None
        self.height = dp(30)

        self.bind(parent = self._update_width , width_ratio = self._update_width)

        # 按钮背景 - 使用正确的background_color属性
        with self.canvas.before :
            # 创建颜色指令时使用self.background_color
            self.bg_color_inst = Color(*self.background_color)
            self.bg_rect = RoundedRectangle(  # 改用RoundedRectangle以支持圆角
                pos = self.pos ,
                size = self.size,
                radius=self.radius  # 直接使用radius属性
            )

        self.bind(
            pos = self.update_bg ,
            size = self.update_bg ,
            background_color = self.update_bg_color ,
            radius = self.update_radius
        )

        # 按钮文字
        self.label = Label(
            text = self.text ,
            color = self.color ,
            font_name = self.font_name ,
            font_size = self.font_size ,
            size_hint = (1 , 1) ,
            halign = 'center' ,
            valign = 'middle'
        )
        self.add_widget(self.label)

        self.bind(
            text = self.update_text ,
            color = self.update_text_color ,
            font_name = self.update_font ,
            font_size = self.update_font_size
        )

    def _update_width(self , instance , value) :
        if self.parent :
            self.width = self.parent.width * self.width_ratio

    def update_bg(self , instance , value) :
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_bg_color(self , instance , value) :
        # 修正颜色更新引用
        self.bg_color_inst.rgba = value

    def update_radius(self , instance , value) :
        # 确保radius始终是列表格式
        if isinstance(value , (int , float)) :
            self.bg_rect.radius = [value]
        else :
            self.bg_rect.radius = value

    def update_text(self , instance , value) :
        self.label.text = value

    def update_text_color(self , instance , value) :
        self.label.color = value

    def update_font(self , instance , value) :
        self.label.font_name = value

    def update_font_size(self , instance , value) :
        self.label.font_size = value


# 处理背景设置的功能类
class BackgroundSettings :
    """处理背景设置的功能类，负责保存和加载背景配置"""

    @staticmethod
    def save_background_settings(app_instance , mode , color , image_path) :
        """保存背景设置到应用实例"""
        app_instance.login_bg_mode = mode
        app_instance.login_bg_color = color
        app_instance.login_bg_image = image_path

    @staticmethod
    def load_background_settings(app_instance) :
        """从应用实例加载背景设置"""
        return {
            'mode' : getattr(app_instance , 'login_bg_mode' , 'color') ,
            'color' : getattr(app_instance , 'login_bg_color' , [0.95 , 0.95 , 0.95 , 1]) ,
            'image' : getattr(app_instance , 'login_bg_image' , "")
        }

    @staticmethod
    def apply_settings_to_screen(screen , settings) :
        """将背景设置应用到指定屏幕"""
        if hasattr(screen , 'bg_mode') :
            screen.bg_mode = settings['mode']
        if hasattr(screen , 'bg_color') :
            screen.bg_color = settings['color']
        if hasattr(screen , 'bg_image') :
            screen.bg_image = settings['image']
        if hasattr(screen , 'update_background') :
            screen.update_background(None , None)


# 独立的背景设置窗口类
class BackgroundSettingsWindow(Screen) :
    """背景设置独立窗口"""
    bg_mode = StringProperty('color')
    selected_color = ListProperty([0.95 , 0.95 , 0.95 , 1])
    image_path = StringProperty("")

    def __init__(self , **kwargs) :
        super().__init__(**kwargs)
        self.name = 'background_settings'  # 屏幕名称，用于屏幕管理器切换
        self.build_ui()

        # 加载当前设置
        app = App.get_running_app()
        current_settings = BackgroundSettings.load_background_settings(app)
        self.bg_mode = current_settings['mode']
        self.selected_color = current_settings['color']
        self.image_path = current_settings['image']

    def build_ui(self) :
        """构建背景设置窗口UI"""
        # 主布局
        main_layout = BoxLayout(orientation = 'vertical' , padding = dp(20) , spacing = dp(20))

        # 标题
        title_label = Label(
            text = "设置登录背景" ,
            font_size = dp(24) ,
            size_hint_y = None ,
            height = dp(60) ,
            halign = 'center' ,
            font_name = 'simhei.ttf' ,
            color = (0.2 , 0.2 , 0.2 , 1)
        )
        main_layout.add_widget(title_label)

        # 内容布局
        content_layout = BoxLayout(
            orientation = 'vertical' ,
            padding = dp(10) ,
            spacing = dp(20) ,
            size_hint_y = None
        )
        content_layout.bind(minimum_height = content_layout.setter('height'))

        # 模式选择
        mode_layout = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(50))
        mode_label = Label(
            text = "背景模式:" ,
            size_hint_x = 0.3 ,
            font_name = 'simhei.ttf' ,
            font_size = dp(16)
        )

        mode_box = BoxLayout(orientation = 'horizontal' , size_hint_x = 0.7 , spacing = dp(20))

        # 颜色模式按钮
        self.color_toggle = ToggleButton(
            text = "颜色" ,
            group = "bg_mode" ,
            state = 'down' if self.bg_mode == 'color' else 'normal' ,
            size_hint = (None , None) ,
            size = (dp(100) , dp(40)) ,
            font_name = 'simhei.ttf'
        )

        # 图片模式按钮
        self.image_toggle = ToggleButton(
            text = "图片" ,
            group = "bg_mode" ,
            state = 'down' if self.bg_mode == 'image' else 'normal' ,
            size_hint = (None , None) ,
            size = (dp(100) , dp(40)) ,
            font_name = 'simhei.ttf'
        )

        # 绑定模式选择
        self.color_toggle.bind(state = self.on_color_toggle_state)
        self.image_toggle.bind(state = self.on_image_toggle_state)

        mode_box.add_widget(self.color_toggle)
        mode_box.add_widget(self.image_toggle)
        mode_layout.add_widget(mode_label)
        mode_layout.add_widget(mode_box)
        content_layout.add_widget(mode_layout)

        # 颜色选择器
        color_section = BoxLayout(orientation = 'vertical' , size_hint_y = None)

        color_label = Label(
            text = "背景颜色:" ,
            size_hint_y = None ,
            height = dp(30) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(16)
        )

        color_buttons = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(50) , spacing = dp(10))
        colors = [
            (1 , 1 , 1 , 1) ,  # 白色
            (0.95 , 0.95 , 0.95 , 1) ,  # 浅灰
            (0.8 , 0.9 , 0.95 , 1) ,  # 浅蓝
            (0.95 , 0.9 , 0.8 , 1) ,  # 浅黄
            (0.9 , 0.95 , 0.8 , 1) ,  # 浅绿
            (0.95 , 0.8 , 0.8 , 1)  # 浅红
        ]

        for color in colors :
            btn = Button(
                size_hint = (None , 1) ,
                width = dp(40) ,
                background_color = color ,
                border = (0 , 0 , 0 , 0)
            )
            btn.bind(on_press = lambda x , c=color : setattr(self , 'selected_color' , c))
            color_buttons.add_widget(btn)

        color_section.add_widget(color_label)
        color_section.add_widget(color_buttons)
        content_layout.add_widget(color_section)

        # 图片选择
        image_section = BoxLayout(orientation = 'vertical' , size_hint_y = None , spacing = dp(10))

        image_label = Label(
            text = "背景图片:" ,
            size_hint_y = None ,
            height = dp(30) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(16)
        )

        image_layout = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(50))

        self.image_path_label = Label(
            text = "未选择图片" ,
            size_hint_x = 0.7 ,
            halign = 'left' ,
            valign = 'middle' ,
            font_name = 'simhei.ttf' ,
            text_size = (self.width * 0.7 , None)
        )

        select_btn = Button(
            text = "选择图片" ,
            size_hint_x = 0.3 ,
            font_name = 'simhei.ttf'
        )
        select_btn.bind(on_press = self.select_image)

        image_layout.add_widget(self.image_path_label)
        image_layout.add_widget(select_btn)

        image_section.add_widget(image_label)
        image_section.add_widget(image_layout)
        content_layout.add_widget(image_section)

        # 按钮区域
        buttons_layout = BoxLayout(
            orientation = 'horizontal' ,
            size_hint_y = None ,
            height = dp(50) ,
            spacing = dp(20)
        )

        cancel_btn = Button(
            text = "取消" ,
            size_hint_x = 0.5 ,
            background_color = (0.8 , 0.8 , 0.8 , 1) ,
            color = (0 , 0 , 0 , 1) ,
            font_name = 'simhei.ttf'
        )
        cancel_btn.bind(on_press = self.on_cancel)

        confirm_btn = Button(
            text = "确认" ,
            size_hint_x = 0.5 ,
            background_color = (0.3 , 0.7 , 0.3 , 1) ,
            color = (1 , 1 , 1 , 1) ,
            font_name = 'simhei.ttf'
        )
        confirm_btn.bind(on_press = self.on_confirm)

        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(confirm_btn)
        content_layout.add_widget(buttons_layout)

        # 添加滚动视图以适应小屏幕
        from kivy.uix.scrollview import ScrollView
        scroll_view = ScrollView(size_hint = (1 , 1))
        scroll_view.add_widget(content_layout)

        main_layout.add_widget(scroll_view)
        self.add_widget(main_layout)

        # 绑定属性更新
        self.bind(image_path = self.update_image_path_label)

    def on_color_toggle_state(self , instance , value) :
        """处理颜色模式切换"""
        if value == 'down' :
            self.bg_mode = 'color'

    def on_image_toggle_state(self , instance , value) :
        """处理图片模式切换"""
        if value == 'down' :
            self.bg_mode = 'image'

    def update_image_path_label(self , instance , value) :
        """更新图片路径显示"""
        if value :
            # 只显示文件名而不是完整路径
            import os
            self.image_path_label.text = os.path.basename(value)
        else :
            self.image_path_label.text = "未选择图片"

    def select_image(self , instance) :
        """选择背景图片"""

        def on_select(selected , popup) :
            if selected :
                self.image_path = selected[0]
            popup.dismiss()

        file_chooser = FileChooserListView()
        file_chooser.filters = ['*.png' , '*.jpg' , '*.jpeg' , '*.bmp']

        popup = Popup(
            title = "选择背景图片" ,
            content = file_chooser ,
            size_hint = (0.9 , 0.9)
        )

        select_btn = Button(text = "选择" , size_hint_y = None , height = dp(40))
        select_btn.bind(on_press = lambda x : on_select(file_chooser.selection , popup))

        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(file_chooser)
        layout.add_widget(select_btn)
        popup.content = layout

        popup.open()

    def on_confirm(self , instance) :
        """确认设置并应用"""
        # 保存设置
        app = App.get_running_app()
        BackgroundSettings.save_background_settings(app , self.bg_mode , self.selected_color , self.image_path)

        # 应用到登录界面
        if hasattr(self , 'manager') :
            login_screen = self.manager.get_screen('login') if 'login' in self.manager.screens else None
            if login_screen :
                BackgroundSettings.apply_settings_to_screen(login_screen , {
                    'mode' : self.bg_mode ,
                    'color' : self.selected_color ,
                    'image' : self.image_path
                })

            # 返回到菜单窗口
            self.manager.current = 'main_menu'

            # 显示成功提示
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            popup = Popup(
                title = "成功" ,
                content = Label(text = "登录背景设置已生效") ,
                size_hint = (0.7 , 0.4)
            )
            popup.open()

    def on_cancel(self , instance) :
        """取消设置，返回菜单"""
        if hasattr(self , 'manager') :
            self.manager.current = 'main_menu'


# 主窗口类(登录界面)
class MainWindow(Screen) :
    current_user = StringProperty(None)
    is_admin = BooleanProperty(False)
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    username_label = ObjectProperty(None)
    password_label = ObjectProperty(None)

    # 背景属性
    bg_color = ListProperty([0.95 , 0.95 , 0.95 , 1])  # 默认浅灰色背景
    bg_image = StringProperty("")  # 背景图片路径
    bg_mode = StringProperty("color")  # 背景模式: color/image

    def __init__(self , **kwargs) :
        super().__init__(**kwargs)
        self.name = 'login'
        self.build_ui()  # 调用UI构建方法

        # 从应用实例获取保存的背景设置
        app = App.get_running_app()
        settings = BackgroundSettings.load_background_settings(app)
        BackgroundSettings.apply_settings_to_screen(self , settings)

        # 绑定背景属性变化事件
        self.bind(bg_color = self.update_background)
        self.bind(bg_image = self.update_background)
        self.bind(bg_mode = self.update_background)

    def build_ui(self) :
        # 主布局使用BoxLayout确保正确布局
        main_layout = BoxLayout(orientation = 'vertical' , padding = dp(20) , spacing = dp(20))

        # 添加顶部空白区域，将登录卡片上移
        top_spacer = Widget(size_hint_y = 0.2)  # 顶部留20%空间，推动卡片上移
        main_layout.add_widget(top_spacer)

        # 登录卡片 - 上移调整
        card = BoxLayout(
            orientation = 'vertical' ,
            size_hint = (0.8 , 0.6) ,
            pos_hint = {'center_x' : 0.5 , 'center_y' : 0.65} ,  # 上移
            padding = dp(20) ,
            spacing = dp(15)
        )

        # 卡片样式
        with card.canvas.before :
            Color(1 , 1 , 1 , 0.95)
            self.card_bg = RoundedRectangle(
                pos = card.pos ,
                size = card.size ,
                radius = [dp(15)]
            )
            Color(0.9 , 0.9 , 0.9 , 1)
            self.card_border = Line(
                rounded_rectangle = (card.pos[0] , card.pos[1] , card.size[0] , card.size[1] , dp(15)) ,
                width = dp(1)
            )
        card.bind(pos = self.update_card , size = self.update_card)

        # 标题
        title_label = Label(
            text = "登录系统" ,
            font_size = dp(22) ,
            size_hint_y = None ,
            height = dp(60) ,
            halign = 'center' ,
            font_name = 'simhei.ttf' ,
            color = (0.2 , 0.2 , 0.2 , 1)
        )
        card.add_widget(title_label)

        # 用户名输入区（保持不变）
        username_layout = BoxLayout(
            orientation = 'horizontal' ,
            spacing = dp(10) ,
            size_hint_y = None ,
            height = dp(50)
        )

        self.username_label = Label(
            text = "账号：" ,
            size_hint_x = 0.2 ,
            color = (0.2 , 0.2 , 0.2 , 1) ,
            font_name = 'simhei.ttf' ,
            halign = 'right' ,
            valign = 'center'
        )

        # 用户名输入框容器（保持不变）
        username_container = BoxLayout(
            size_hint_x = 0.8 ,
            size_hint_y = None ,
            height = dp(45)
        )

        with username_container.canvas.before :
            Color(0.92 , 0.92 , 0.92 , 1)  # 淡灰色背景
            self.username_bg = RoundedRectangle(
                pos = username_container.pos ,
                size = username_container.size ,
                radius = [dp(10)]
            )
            Color(0.7 , 0.7 , 0.7 , 1)  # 边框颜色
            self.username_border = Line(
                rounded_rectangle = (username_container.pos[0] , username_container.pos[1] ,
                                     username_container.size[0] , username_container.size[1] , dp(10)) ,
                width = dp(0.8)
            )

        username_container.bind(pos = self.update_username_bg , size = self.update_username_bg)

        self.username_input = TextInput(
            size_hint = (1 , 1) ,
            padding = [dp(12) , dp(10)] ,
            multiline = False ,
            font_name = 'simhei.ttf' ,
            background_color = (0 , 0 , 0 , 0) ,  # 透明背景
            cursor_color = (0.2 , 0.2 , 0.2 , 1) ,
            hint_text = "请输入账号" ,
            hint_text_color = (0.5 , 0.5 , 0.5 , 0.7)
        )

        username_container.add_widget(self.username_input)
        username_layout.add_widget(self.username_label)
        username_layout.add_widget(username_container)
        card.add_widget(username_layout)

        # 密码输入区（保持不变）
        password_layout = BoxLayout(
            orientation = 'horizontal' ,
            spacing = dp(10) ,
            size_hint_y = None ,
            height = dp(50)
        )

        self.password_label = Label(
            text = "密码：" ,
            size_hint_x = 0.2 ,
            color = (0.2 , 0.2 , 0.2 , 1) ,
            font_name = 'simhei.ttf' ,
            halign = 'right' ,
            valign = 'center'
        )

        # 密码输入框容器（保持不变）
        password_container = BoxLayout(
            size_hint_x = 0.8 ,
            size_hint_y = None ,
            height = dp(45)
        )

        with password_container.canvas.before :
            Color(0.92 , 0.92 , 0.92 , 1)  # 淡灰色背景
            self.password_bg = RoundedRectangle(
                pos = password_container.pos ,
                size = password_container.size ,
                radius = [dp(10)]
            )
            Color(0.7 , 0.7 , 0.7 , 1)  # 边框颜色
            self.password_border = Line(
                rounded_rectangle = (password_container.pos[0] , password_container.pos[1] ,
                                     password_container.size[0] , password_container.size[1] , dp(10)) ,
                width = dp(0.8)
            )

        password_container.bind(pos = self.update_password_bg , size = self.update_password_bg)

        self.password_input = TextInput(
            size_hint = (1 , 1) ,
            padding = [dp(12) , dp(10)] ,
            password = True ,
            multiline = False ,
            font_name = 'simhei.ttf' ,
            background_color = (0 , 0 , 0 , 0) ,  # 透明背景
            cursor_color = (0.2 , 0.2 , 0.2 , 1) ,
            hint_text = "请输入密码" ,
            hint_text_color = (0.5 , 0.5 , 0.5 , 0.7)
        )

        password_container.add_widget(self.password_input)
        password_layout.add_widget(self.password_label)
        password_layout.add_widget(password_container)
        card.add_widget(password_layout)

        # 按钮区域（保持不变）
        buttons_layout = BoxLayout(
            orientation = 'horizontal' ,
            spacing = dp(15) ,
            size_hint_y = None ,
            height = dp(50)
        )

        # 登录按钮
        login_btn = RoundedButton(
            text = "登录" ,
            size_hint = (1 , 1) ,
            background_color = (0.3 , 0.7 , 0.3 , 1) ,
            color = (1 , 1 , 1 , 1) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(15) ,
            radius = dp(25)
        )
        login_btn.bind(on_press = self.usr_log_in)

        # 管理按钮
        manager_btn = RoundedButton(
            text = "管理" ,
            size_hint = (1 , 1) ,
            background_color = (0.1 , 0.4 , 0.8 , 1) ,
            color = (1 , 1 , 1 , 1) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(15) ,
            radius = dp(25)
        )
        manager_btn.bind(on_press = self.usr_manager)

        # 退出按钮
        quit_btn = RoundedButton(
            text = "退出" ,
            size_hint = (1 , 1) ,
            background_color = (0.8 , 0.2 , 0.2 , 1) ,
            color = (1 , 1 , 1 , 1) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(15) ,
            radius = dp(25)
        )
        quit_btn.bind(on_press = self.usr_sign_quit)

        buttons_layout.add_widget(login_btn)
        buttons_layout.add_widget(manager_btn)
        buttons_layout.add_widget(quit_btn)
        card.add_widget(buttons_layout)

        main_layout.add_widget(card)

        # 添加底部空白区域，平衡布局
        bottom_spacer = Widget(size_hint_y = 0.2)
        main_layout.add_widget(bottom_spacer)

        # 添加背景画布 - 关键修复：初始化颜色指令
        with self.canvas.before :
            # 初始化颜色指令并保存引用
            self.bg_color_inst = Color(*self.bg_color)
            # 创建矩形背景
            self.bg_rect = Rectangle(pos = self.pos , size = self.size)
            # 图片背景
            self.bg_image_rect = Rectangle(pos = self.pos , size = self.size , source = "")

        self.add_widget(main_layout)
        # 绑定位置和大小变化，更新背景
        self.bind(pos = self.update_bg_position , size = self.update_bg_position)

    # 更新背景位置和大小
    def update_bg_position(self , instance , value) :
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.bg_image_rect.pos = self.pos
        self.bg_image_rect.size = self.size

    # 更新背景显示 - 修复颜色更新逻辑
    def update_background(self , instance , value) :
        # 根据当前模式设置背景
        if self.bg_mode == "color" :
            # 更新颜色指令
            self.bg_color_inst.rgba = self.bg_color
            # 显示颜色背景
            self.bg_rect.size = self.size
            # 隐藏图片背景
            self.bg_image_rect.source = ""
        elif self.bg_mode == "image" and self.bg_image :
            # 调整颜色为透明
            self.bg_color_inst.rgba = (0 , 0 , 0 , 0)
            # 隐藏颜色背景
            self.bg_rect.size = (0 , 0)
            # 显示图片背景
            self.bg_image_rect.source = self.bg_image
            self.bg_image_rect.size = self.size

        # 保存设置到应用实例
        app = App.get_running_app()
        BackgroundSettings.save_background_settings(app , self.bg_mode , self.bg_color , self.bg_image)

    # 其他方法保持不变...
    def update_card(self , instance , value) :
        self.card_bg.pos = instance.pos
        self.card_bg.size = instance.size
        self.card_border.rounded_rectangle = (
            instance.pos[0] , instance.pos[1] ,
            instance.size[0] , instance.size[1] ,
            dp(15)
        )

    def update_username_bg(self , instance , value) :
        self.username_bg.pos = instance.pos
        self.username_bg.size = instance.size
        self.username_border.rounded_rectangle = (
            instance.pos[0] , instance.pos[1] ,
            instance.size[0] , instance.size[1] ,
            dp(10)
        )

    def update_password_bg(self , instance , value) :
        self.password_bg.pos = instance.pos
        self.password_bg.size = instance.size
        self.password_border.rounded_rectangle = (
            instance.pos[0] , instance.pos[1] ,
            instance.size[0] , instance.size[1] ,
            dp(10)
        )

    # 登录逻辑（保持不变）
    def usr_log_in(self , instance) :
        usr_name = self.username_input.text
        user_pwd = self.password_input.text
        hashed_usr_name = hash_string(usr_name)
        hashed_usr_pwd = hash_string(user_pwd)
        users_info = load_users_info()

        # 重置标签颜色
        self.username_label.color = (0.2 , 0.2 , 0.2 , 1)
        self.password_label.color = (0.2 , 0.2 , 0.2 , 1)

        # 用户为第一次登录
        if not users_info :
            users_info[hashed_usr_name] = {
                'hashed_pwd' : hashed_usr_pwd ,
                'username' : usr_name ,
                'register_time' : time.strftime("%Y-%m-%d %H:%M:%S") ,
                'is_admin' : True
            }
            save_users_info(users_info)
            self.is_admin = True
            self.username_label.color = (0 , 0.7 , 0 , 1)
            self.password_label.color = (0 , 0.7 , 0 , 1)

            popup = CustomDialog(f"用户\"{usr_name}\"欢迎登录，你是管理员" ,
                                 title = "欢迎" , button_text = '进入系统')
            popup.bind(on_dismiss = self.go_to_menu)
            popup.open()

        elif hashed_usr_name in users_info :
            if hashed_usr_pwd == users_info[hashed_usr_name]['hashed_pwd'] :
                self.is_admin = users_info[hashed_usr_name].get('is_admin' , False)
                self.username_label.color = (0 , 0.7 , 0 , 1)
                self.password_label.color = (0 , 0.7 , 0 , 1)

                popup = CustomDialog(f"用户\"{usr_name}\"欢迎登录" ,
                                     title = "欢迎" , button_text = '进入系统')
                popup.bind(on_dismiss = self.go_to_menu)
                popup.open()
            elif user_pwd == '' :
                self.password_label.color = (1 , 0.6 , 0 , 1)
                popup = CustomDialog("未输入密码" , title = "错误" , button_text = "知道了")
                popup.open()
                return
            else :
                self.password_label.color = (1 , 0 , 0 , 1)
                popup = CustomDialog("密码错误" , title = "错误" , button_text = "知道了")
                popup.open()
                return

        elif usr_name == '' and user_pwd == '' :
            self.username_label.color = (1 , 0.6 , 0 , 1)
            self.password_label.color = (1 , 0.6 , 0 , 1)
            popup = CustomDialog("请填写用户名和密码" , title = "错误" , button_text = "知道了")
            popup.open()
            return

        elif usr_name == '' :
            self.username_label.color = (1 , 0.6 , 0 , 1)
            popup = CustomDialog("未输入用户名" , title = "错误" , button_text = "知道了")
            popup.open()
            return

        else :
            self.username_label.color = (1 , 0.6 , 0 , 1)
            self.password_label.color = (1 , 0.6 , 0 , 1)
            popup = CustomDialog("你还没注册，是否联系管理员注册？" ,
                                 title = "欢迎" , button_text = "好的")
            popup.open()
            return

        self.current_user = usr_name

    # 优化的页面切换方法 - 目标改为main_menu
    def go_to_menu(self , instance) :
        # 辅助方法：移除所有同名屏幕（彻底清理）
        def remove_duplicate_screens() :
            if hasattr(self , 'manager') :
                # 收集所有同名屏幕
                duplicates = [screen for screen in self.manager.screens
                              if screen.name == 'main_menu']
                # 保留一个，移除其他
                if len(duplicates) > 1 :
                    for screen in duplicates[1 :] :  # 从第二个开始移除
                        self.manager.remove_widget(screen)
                # 如果有实例，更新为单例
                elif len(duplicates) == 1 :
                    MenuWindow._instance = duplicates[0]

        # 先清理重复屏幕
        remove_duplicate_screens()

        # 获取单例实例
        menu_screen = MenuWindow()

        # 确保UI已构建
        if not menu_screen.ui_built :
            menu_screen.build_ui()

        # 检查是否已在管理器中，不在则添加
        if menu_screen not in self.manager.screens :
            self.manager.add_widget(menu_screen)

        # 切换屏幕
        def switch_screen(dt) :
            if hasattr(self , 'manager') :
                original_transition = self.manager.transition
                self.manager.transition = SlideTransition(
                    direction = 'left' ,
                    duration = 0.3
                )
                self.manager.current = 'main_menu'
                Clock.schedule_once(lambda t : setattr(self.manager , 'transition' , original_transition) , 0.3)

        Clock.schedule_once(switch_screen , 0.2)

    def usr_manager(self , instance) :
        usr_name = self.username_input.text
        user_pwd = self.password_input.text

        if not usr_name or not user_pwd :
            popup = CustomDialog("请先在主窗口输入用户名和密码" , title = "错误" , button_text = "知道了")
            popup.open()
            return

        hashed_usr_name = hash_string(usr_name)
        hashed_usr_pwd = hash_string(user_pwd)
        users_info = load_users_info()

        if hashed_usr_name not in users_info :
            popup = CustomDialog("用户不存在" , title = "错误" , button_text = "知道了")
            popup.open()
            return

        stored_user = users_info[hashed_usr_name]

        if not isinstance(stored_user , dict) :
            popup = CustomDialog("用户数据结构损坏，请检查" , title = "错误" , button_text = "知道了")
            popup.open()
            return

        if hashed_usr_pwd == stored_user['hashed_pwd'] :
            if stored_user.get('is_admin' , False) :
                if hasattr(self , 'manager') :
                    self.manager.transition = SlideTransition(direction = 'left')
                    self.manager.current = 'admin'
            else :
                self.username_label.color = (1 , 0.6 , 0 , 1)
                popup = CustomDialog("该用户不是管理员" , title = "错误" , button_text = "知道了")
                popup.open()
        else :
            self.password_label.color = (1 , 0 , 0 , 1)
            popup = CustomDialog("密码错误" , title = "错误" , button_text = "知道了")
            popup.open()

    def usr_sign_quit(self , instance) :
        App.get_running_app().stop()


# 管理员窗口类
class AdminWindow(Screen) :
    user_tree = ObjectProperty(None)

    def __init__(self , **kwargs) :
        super().__init__(**kwargs)
        self.name = 'admin'
        self.build_ui()  # 添加UI构建

    def build_ui(self) :
        main_layout = BoxLayout(orientation = 'vertical' , padding = dp(15) , spacing = dp(15))

        # 标题
        title_label = Label(
            text = "用户管理" ,
            font_size = dp(20) ,
            size_hint_y = None ,
            height = dp(50) ,
            font_name = 'simhei.ttf' ,
            color = (0 , 0 , 0 , 1)
        )
        main_layout.add_widget(title_label)

        # 用户列表
        scroll_view = ScrollView()
        self.user_tree = TreeView(
            root_options = dict(text = '用户列表') ,
            hide_root = True ,
            size_hint_y = None
        )
        self.user_tree.bind(minimum_height = self.user_tree.setter('height'))
        scroll_view.add_widget(self.user_tree)
        main_layout.add_widget(scroll_view)

        # 按钮区域
        btn_layout = BoxLayout(orientation = 'horizontal' , spacing = dp(10) , size_hint_y = None , height = dp(45))
        add_btn = RoundedButton(
            text = "添加用户" ,
            font_name = 'simhei.ttf' ,
            radius = dp(20) ,
            background_color = (0.3 , 0.7 , 0.3 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        add_btn.bind(on_press = lambda x : self.add_user())

        del_btn = RoundedButton(
            text = "删除用户" ,
            font_name = 'simhei.ttf' ,
            radius = dp(20) ,
            background_color = (0.8 , 0.2 , 0.2 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        del_btn.bind(on_press = lambda x : self.delete_user())

        back_btn = RoundedButton(
            text = "返回" ,
            font_name = 'simhei.ttf' ,
            radius = dp(20) ,
            background_color = (0.6 , 0.6 , 0.6 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        back_btn.bind(on_press = lambda x : self.go_back(x))

        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(del_btn)
        btn_layout.add_widget(back_btn)
        main_layout.add_widget(btn_layout)

        self.add_widget(main_layout)

    def on_enter(self) :
        self.load_users()

    def load_users(self) :
        # 清空现有项目
        if self.user_tree :
            self.user_tree.clear_widgets()
            for node in self.user_tree.iterate_all_nodes() :
                self.user_tree.remove_node(node)

        users_info = load_users_info()
        login_screen = self.manager.get_screen('login')

        for hashed_name , info in users_info.items() :
            if hasattr(login_screen , 'current_user') and info['username'] != login_screen.current_user :
                node = TreeViewLabel(text = f"{info['username']} - {info['register_time']}" ,
                                     size_hint_y = None , height = dp(30))
                self.user_tree.add_node(node)

    def delete_user(self) :
        selected_node = self.user_tree.selected_node
        if not selected_node :
            popup = CustomDialog("请先选择要删除的用户" , title = "提示" , button_text = "知道了")
            popup.open()
            return

        # 提取用户名
        username = selected_node.text.split(" - ")[0]
        hashed_username = hash_string(username)

        users_info = load_users_info()
        if hashed_username in users_info :
            del users_info[hashed_username]
            save_users_info(users_info)
            self.load_users()
            popup = CustomDialog(f"用户 {username} 已删除" , title = "提示" , button_text = "知道了")
            popup.open()
        else :
            popup = CustomDialog(f"用户 {username} 不存在" , title = "错误" , button_text = "知道了")
            popup.open()

    def add_user(self) :
        # 创建添加用户的弹出窗口
        content = AddUserWindow(admin_window = self)
        self.popup = Popup(title = "添加新用户" , content = content ,
                           size_hint = (None , None) , size = (400 , 300))
        self.popup.open()

    def go_back(self , instance) :
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'login'


# 添加用户窗口类
class AddUserWindow(BoxLayout) :
    def __init__(self , admin_window , **kwargs) :
        self.admin_window = admin_window
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.build_ui()

    def build_ui(self) :
        # 用户名输入
        self.username_input = TextInput(
            hint_text = "请输入用户名" ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            padding = [dp(10) , 0] ,
            foreground_color = (0 , 0 , 0 , 1)
        )
        self.add_widget(self.username_input)

        # 密码输入
        self.password_input = TextInput(
            hint_text = "请输入密码" ,
            password = True ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            padding = [dp(10) , 0]
        )
        self.add_widget(self.password_input)

        # 确认密码
        self.confirm_password_input = TextInput(
            hint_text = "请确认密码" ,
            password = True ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            padding = [dp(10) , 0]
        )
        self.add_widget(self.confirm_password_input)

        # 按钮
        btn_layout = BoxLayout(orientation = 'horizontal' , spacing = dp(10) , size_hint_y = None , height = dp(45))
        cancel_btn = RoundedButton(
            text = "取消" ,
            font_name = 'simhei.ttf' ,
            radius = dp(20) ,
            background_color = (0.8 , 0.2 , 0.2 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        cancel_btn.bind(on_press = self.cancel)

        create_btn = RoundedButton(
            text = "创建" ,
            font_name = 'simhei.ttf' ,
            radius = dp(20) ,
            background_color = (0.3 , 0.7 , 0.3 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        create_btn.bind(on_press = lambda x : self.create_user())

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(create_btn)
        self.add_widget(btn_layout)

    def cancel(self , instance) :
        self.parent.parent.dismiss()

    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    confirm_password_input = ObjectProperty(None)
    admin_window = ObjectProperty(None)

    def create_user(self) :
        username = self.username_input.text.strip()
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text

        if not username :
            popup = CustomDialog("用户名不能为空" , title = "输入错误" , button_text = '知道了')
            popup.open()
            return

        if password != confirm_password :
            popup = CustomDialog("两次输入的密码不一致" , title = "输入错误" , button_text = '知道了')
            popup.open()
            return

        # 处理用户创建逻辑
        hashed_username = hash_string(username)
        users_info = load_users_info()

        if hashed_username in users_info :
            popup = CustomDialog("该用户名已存在" , title = "创建失败" , button_text = '知道了')
            popup.open()
            return

        # 添加新用户信息
        users_info[hashed_username] = {
            "username" : username ,
            "register_time" : time.strftime("%Y-%m-%d %H:%M:%S") ,
            "hashed_pwd" : hash_string(password) ,
            "is_admin" : False  # 默认为普通用户
        }

        save_users_info(users_info)
        popup = CustomDialog(f"用户 {username} 创建成功" , title = "创建成功" , button_text = '知道了')
        popup.bind(on_dismiss = self.close_dialog)
        popup.open()

    def close_dialog(self , instance) :
        self.parent.parent.dismiss()  # 关闭弹出窗口
        self.admin_window.load_users()  # 刷新用户列表


# 菜单窗口类
class MenuWindow(Screen) :
    # 单例模式实现
    _instance = None

    def __new__(cls , *args , **kwargs) :
        if cls._instance is None :
            cls._instance = super(MenuWindow , cls).__new__(cls , *args , **kwargs)
        return cls._instance

    def __init__(self , **kwargs) :
        if hasattr(self , '_initialized') :
            return

        super().__init__(**kwargs)
        self.name = 'main_menu'
        self.ui_built = False
        self.build_ui()
        self._initialized = True

    def build_ui(self) :
        if self.ui_built :
            return

        container = BoxLayout(orientation = 'vertical')

        # 滚动视图
        scroll_view = ScrollView(
            size_hint = (1 , 1) ,
            do_scroll_x = False ,
            do_scroll_y = True ,
            bar_width = dp(6)
        )

        # 内容布局
        content_layout = BoxLayout(
            orientation = 'vertical' ,
            padding = dp(20) ,
            spacing = dp(15) ,
            size_hint = (1 , None)
        )

        # 宽度绑定
        content_layout.bind(width = lambda s , w : setattr(s , 'width' , w))

        # 标题
        title_label = Label(
            text = "功能菜单" ,
            font_size = dp(22) ,
            size_hint_y = None ,
            height = dp(60) ,
            halign = 'center' ,
            font_name = 'simhei.ttf' ,
            color = (0.2 , 0.2 , 0.2 , 1)
        )
        content_layout.add_widget(title_label)

        # 按钮样式
        button_style = {
            'size_hint' : (1 , None) ,
            'height' : dp(50) ,
            'font_name' : 'simhei.ttf' ,
            'font_size' : dp(16) ,
            'color' : (1 , 1 , 1 , 1) ,
            'radius' : [dp(8)]
        }

        # 按钮列表 - 包含背景设置按钮
        buttons = [
            ("百度热搜" , (0.2 , 0.6 , 0.9 , 1) , self.show_news_in_window) ,
            ("小说下载" , (0.5 , 0.7 , 0.9 , 1) , self.quick_download_txt) ,
            ("浏览器" , (0.3 , 0.8 , 0.7 , 1) , self.a_BrowserWindow_example) ,
            ("音视频下载" , (0.9 , 0.6 , 0.3 , 1) , self.music_video_download) ,
            ("设置登录背景" , (0.6 , 0.3 , 0.8 , 1) , self.goto_background_settings) ,  # 更新此处的回调
            ("退出" , (0.9 , 0.4 , 0.4 , 1) , self.usr_sign_quit)
        ]

        # 添加按钮
        for text , color , callback in buttons :
            btn = RoundedButton(
                text = text , **button_style ,
                background_color = color
            )
            btn.bind(on_press = callback)
            content_layout.add_widget(btn)

        # 空白区域
        content_layout.add_widget(Widget(size_hint_y = None , height = dp(20)))

        # 高度绑定
        content_layout.bind(
            minimum_height = lambda s , h : setattr(s , 'height' , h)
        )

        # 组装布局
        scroll_view.add_widget(content_layout)
        container.add_widget(scroll_view)
        self.add_widget(container)

        self.ui_built = True

    def goto_background_settings(self , instance) :
        """跳转到独立的背景设置窗口"""
        if hasattr(self , 'manager') :
            # 确保背景设置窗口已添加到屏幕管理器
            if 'background_settings' not in self.manager.screen_names :
                self.manager.add_widget(BackgroundSettingsWindow())
            # 切换到背景设置窗口
            self.manager.transition.direction = 'left'
            self.manager.current = 'background_settings'

    # 菜单窗口类中的背景设置对话框修复
    def set_login_background(self , instance) :
        # 加载当前设置
        app = App.get_running_app()
        current_settings = BackgroundSettings.load_background_settings(app)

        # 创建对话框布局
        dialog_layout = BoxLayout(orientation = 'vertical' , spacing = dp(15) , padding = dp(10))

        # 模式选择 - 使用ToggleButton实现单选功能
        mode_layout = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(40))
        mode_label = Label(text = "背景模式:" , size_hint_x = 0.3)
        self.bg_mode = StringProperty(current_settings['mode'])

        mode_box = BoxLayout(orientation = 'horizontal' , size_hint_x = 0.7)

        # 使用ToggleButton并通过代码控制单选行为
        # ToggleButton使用state属性('normal'或'down')而非active
        color_toggle = ToggleButton(
            text = "颜色" ,
            group = "bg_mode" ,  # 相同group确保互斥
            state = 'down' if self.bg_mode == 'color' else 'normal'
        )
        image_toggle = ToggleButton(
            text = "图片" ,
            group = "bg_mode" ,
            state = 'down' if self.bg_mode == 'image' else 'normal'
        )

        # 绑定模式选择 - 使用state属性
        def on_color_toggle_state(instance , value) :
            if value == 'down' :  # 'down'表示选中状态
                self.bg_mode = 'color'

        def on_image_toggle_state(instance , value) :
            if value == 'down' :  # 'down'表示选中状态
                self.bg_mode = 'image'

        color_toggle.bind(state = on_color_toggle_state)
        image_toggle.bind(state = on_image_toggle_state)

        mode_box.add_widget(color_toggle)
        mode_box.add_widget(image_toggle)
        mode_layout.add_widget(mode_label)
        mode_layout.add_widget(mode_box)
        dialog_layout.add_widget(mode_layout)

        # 颜色选择器（保持不变）
        color_layout = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(40))
        color_label = Label(text = "背景颜色:" , size_hint_x = 0.3)
        self.selected_color = ListProperty(current_settings['color'])

        color_buttons = BoxLayout(orientation = 'horizontal' , size_hint_x = 0.7)
        colors = [
            (1 , 1 , 1 , 1) ,  # 白色
            (0.95 , 0.95 , 0.95 , 1) ,  # 浅灰
            (0.8 , 0.9 , 0.95 , 1) ,  # 浅蓝
            (0.95 , 0.9 , 0.8 , 1) ,  # 浅黄
            (0.9 , 0.95 , 0.8 , 1) ,  # 浅绿
            (0.95 , 0.8 , 0.8 , 1)  # 浅红
        ]

        for color in colors :
            btn = Button(size_hint = (None , 1) , width = dp(30) , background_color = color)
            btn.bind(on_press = lambda x , c=color : setattr(self , 'selected_color' , c))
            color_buttons.add_widget(btn)

        color_layout.add_widget(color_label)
        color_layout.add_widget(color_buttons)
        dialog_layout.add_widget(color_layout)

        # 图片选择（保持不变）
        image_layout = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(40))
        image_label = Label(text = "背景图片:" , size_hint_x = 0.3)
        self.image_path = StringProperty(current_settings['image'])

        select_btn = Button(text = "选择图片" , size_hint_x = 0.7)
        select_btn.bind(on_press = self.select_image)

        image_layout.add_widget(image_label)
        image_layout.add_widget(select_btn)
        dialog_layout.add_widget(image_layout)

        # 创建对话框（保持不变）
        popup = Popup(
            title = "设置登录背景" ,
            content = dialog_layout ,
            size_hint = (0.8 , 0.6) ,
            auto_dismiss = False
        )

        # 确认按钮
        confirm_btn = Button(text = "确认" , size_hint_y = None , height = dp(40))
        confirm_btn.bind(on_press = lambda x : self.apply_background_settings(popup))
        dialog_layout.add_widget(confirm_btn)

        popup.open()

    # 选择图片
    def select_image(self , instance) :
        # 实际应用中应使用平台相关的文件选择器
        # 这里简化实现
        from kivy.uix.filechooser import FileChooserListView

        def on_select(selected , popup) :
            if selected :
                self.image_path = selected[0]
            popup.dismiss()

        file_chooser = FileChooserListView()
        file_chooser.filters = ['*.png' , '*.jpg' , '*.jpeg' , '*.bmp']

        popup = Popup(
            title = "选择背景图片" ,
            content = file_chooser ,
            size_hint = (0.9 , 0.9)
        )

        select_btn = Button(text = "选择" , size_hint_y = None , height = dp(40))
        select_btn.bind(on_press = lambda x : on_select(file_chooser.selection , popup))

        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(file_chooser)
        layout.add_widget(select_btn)
        popup.content = layout

        popup.open()

    # 应用背景设置
    def apply_background_settings(self , popup) :
        # 保存设置
        app = App.get_running_app()
        BackgroundSettings.save_background_settings(app , self.bg_mode , self.selected_color , self.image_path)

        # 应用到登录界面
        login_screen = self.manager.get_screen('login') if 'login' in self.manager.screens else None
        if login_screen :
            BackgroundSettings.apply_settings_to_screen(login_screen , {
                'mode' : self.bg_mode ,
                'color' : self.selected_color ,
                'image' : self.image_path
            })

        popup.dismiss()
        # 显示成功提示
        confirm_popup = CustomDialog("登录背景设置已生效" , title = "成功" , button_text = "确定")
        confirm_popup.open()

    # 其他菜单功能
    def show_news_in_window(self , instance) :
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = 'news'

    def quick_download_txt(self , instance) :
        popup = CustomDialog("小说下载功能开发中" , title = "提示" , button_text = "知道了")
        popup.open()

    def a_BrowserWindow_example(self , instance) :
        popup = CustomDialog("浏览器功能开发中" , title = "提示" , button_text = "知道了")
        popup.open()

    def music_video_download(self , instance) :
        popup = CustomDialog("音视频下载功能开发中" , title = "提示" , button_text = "知道了")
        popup.open()

    def usr_sign_quit(self , instance) :
        if hasattr(self , 'manager') :
            self.manager.current = 'login'


# 百度热搜窗口类
class NewsWindow(Screen) :
    news_list = ObjectProperty(None)
    status_label = ObjectProperty(None)

    def __init__(self , **kwargs) :
        super().__init__(**kwargs)
        self.name = 'news'
        self.build_ui()  # 添加UI构建

    def build_ui(self) :
        main_layout = BoxLayout(orientation = 'vertical' , padding = dp(15) , spacing = dp(15))

        # 返回按钮（保持不变）
        back_btn = RoundedButton(
            text = "返回" ,
            size_hint_y = None ,
            height = dp(45) ,
            font_name = 'simhei.ttf' ,
            radius = dp(20) ,
            background_color = (0.6 , 0.6 , 0.6 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        back_btn.bind(on_press = self.go_back)
        main_layout.add_widget(back_btn)

        # 标题（保持不变）
        title_label = Label(
            text = "百度热搜" ,
            font_size = dp(20) ,
            size_hint_y = None ,
            height = dp(50) ,
            font_name = 'simhei.ttf' ,
            color = (0 , 0 , 0 , 1)
        )
        main_layout.add_widget(title_label)

        # 刷新按钮（保持不变）
        refresh_btn = RoundedButton(
            text = "刷新" ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            radius = dp(15) ,
            background_color = (0.2 , 0.6 , 0.9 , 1) ,
            color = (1 , 1 , 1 , 1)
        )
        refresh_btn.bind(on_press = lambda x : self.load_news())
        main_layout.add_widget(refresh_btn)

        # 新闻列表容器（保持不变）
        scroll_view = ScrollView()
        self.news_list = BoxLayout(orientation = 'vertical' , size_hint_y = None)
        self.news_list.bind(minimum_height = self.news_list.setter('height'))
        scroll_view.add_widget(self.news_list)
        main_layout.add_widget(scroll_view)

        # 状态标签 - 修改颜色为深蓝色
        self.status_label = Label(
            text = "准备就绪" ,
            size_hint_y = None ,
            height = dp(30) ,
            font_name = 'simhei.ttf' ,
            color = (0.1 , 0.3 , 0.8 , 1)  # 深蓝色
        )
        main_layout.add_widget(self.status_label)

        self.add_widget(main_layout)

    def on_enter(self) :
        self.load_news()

    def load_news(self) :
        # 修改状态文本颜色
        self.status_label.text = "正在加载热搜数据..."
        self.status_label.color = (0.5 , 0.5 , 0.5 , 1)  # 加载中显示灰色

        if self.news_list :
            self.news_list.clear_widgets()

        url = 'https://top.baidu.com/board?tab=realtime'
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36'
        }

        try :
            # 显示加载提示（保持不变）
            loading_label = Label(text = "数据加载中，请稍候..." , size_hint_y = None , height = dp(30))
            self.news_list.add_widget(loading_label)

            response = requests.get(url , headers = headers , timeout = 10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text , 'lxml')
            news_items = soup.find_all('div' , class_ = 'c-single-text-ellipsis')
            hot_numbers = soup.find_all('div' , class_ = 'hot-index_1Bl1a')

            # 清空加载提示
            self.news_list.clear_widgets()

            if not news_items :
                no_data_label = Label(text = "无热搜数据" , size_hint_y = None , height = dp(30) ,
                                      color = (0.6 , 0.6 , 0.6 , 1))
                self.news_list.add_widget(no_data_label)
                self.status_label.text = "加载完成，未获取到数据"
                self.status_label.color = (0.8 , 0.4 , 0 , 1)  # 无数据时显示橙色
                return

            # 处理并显示热搜数据 - 修改排名颜色
            for i , (item , number) in enumerate(zip(news_items[:100] , hot_numbers[:100])) :
                title = item.get_text(strip = True)
                hot_number = number.get_text(strip = True)

                item_layout = BoxLayout(orientation = 'horizontal' , size_hint_y = None , height = dp(40))

                # 修改排名字体颜色为深紫色
                item_layout.add_widget(Label(
                    text = f"{i + 1}." ,
                    size_hint_x = 0.1 ,
                    color = (0.5 , 0.2 , 0.8 , 1)  # 深紫色排名
                ))

                item_layout.add_widget(Label(
                    text = title ,
                    size_hint_x = 0.7 ,
                    halign = 'left' ,
                    valign = 'middle' ,
                    color = (0 , 0 , 0 , 1)  # 黑色标题
                ))

                item_layout.add_widget(Label(
                    text = hot_number ,
                    size_hint_x = 0.2 ,
                    color = (0.8 , 0 , 0 , 1)  # 红色热度
                ))

                self.news_list.add_widget(item_layout)

            # 加载完成后修改状态文本颜色为深绿色
            self.status_label.text = f"加载完成，共 {len(news_items)} 条热搜"
            self.status_label.color = (0 , 0.6 , 0.2 , 1)  # 深绿色

        except Exception as e :
            error_label = Label(text = f"加载失败: {str(e)}" , size_hint_y = None , height = dp(30) ,
                                color = (1 , 0 , 0 , 1))
            self.news_list.add_widget(error_label)
            self.status_label.text = "加载失败"
            self.status_label.color = (1 , 0 , 0 , 1)  # 错误时显示红色

    def go_back(self , instance) :
        self.manager.transition = SlideTransition(direction = 'right')
        self.manager.current = 'main_menu'


# 主应用类
class MainApp(App) :
    def build(self) :
        Window.size = (600 , 600)
        sm = ScreenManager()

        # 添加所有屏幕
        sm.add_widget(MainWindow())
        sm.add_widget(MenuWindow())
        sm.add_widget(AdminWindow())
        sm.add_widget(NewsWindow())

        return sm


if __name__ == '__main__' :
    MainApp().run()
