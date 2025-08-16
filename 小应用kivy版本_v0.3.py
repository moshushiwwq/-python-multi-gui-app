import sys
import re
import uuid
import subprocess
import time
import shutil
import hashlib
import pickle
import os

from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
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
from custom_dialog import RoundedButton , CustomDialog , ToggleSwitch
from kivy.uix.gridlayout import GridLayout

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


# 处理背景设置的功能类
class BackgroundSettings :
    """处理背景设置的功能类，负责保存和加载背景配置"""

    @staticmethod
    def save_background_settings(app_instance , mode , color , image_path) :
        """保存背景设置到应用实例"""
        app_instance.login_bg_mode = mode
        app_instance.login_bg_color = color
        app_instance.login_bg_image = image_path
        # 保存到文件
        settings = {
            'mode' : mode ,
            'color' : list(color) ,  # 将颜色转换为列表
            'image' : image_path
        }
        with open('bg_settings.pickle' , 'wb') as f :
            pickle.dump(settings , f)

    @staticmethod
    def load_background_settings(app_instance) :
        """从应用实例加载背景设置"""
        try :
            with open('bg_settings.pickle' , 'rb') as f :
                settings = pickle.load(f)
                return settings
        except (FileNotFoundError , EOFError) :
            return {
                'mode' : 'color' ,
                'color' : [0.95 , 0.95 , 0.95 , 1] ,
                'image' : ""
            }

    @staticmethod
    def apply_settings_to_screen(screen , settings) :
        """将背景设置应用到指定屏幕（增强容错性）"""
        if hasattr(screen , 'bg_mode') :
            screen.bg_mode = settings['mode']

        if hasattr(screen , 'bg_color') :
            # 确保颜色是有效的RGBA值
            try :
                color = list(settings['color'])
                if len(color) != 4 :
                    color = [0.95 , 0.95 , 0.95 , 1]
                screen.bg_color = color
            except :
                screen.bg_color = [0.95 , 0.95 , 0.95 , 1]

        if hasattr(screen , 'bg_image') :
            # 验证图片路径有效性
            image_path = settings['image']
            if image_path and not os.path.isfile(image_path) :
                screen.bg_image = ""
                screen.bg_mode = 'color'  # 自动切换到颜色模式
            else :
                screen.bg_image = image_path

        if hasattr(screen , 'update_background') :
            screen.update_background(None , None)


# 独立的背景设置窗口类（修复异常图形版本）
class BackgroundSettingsWindow(Screen) :
    bg_mode = StringProperty('color')
    selected_color = ListProperty([0.95 , 0.95 , 0.95 , 1])
    image_path = StringProperty("")

    def __init__(self , **kwargs) :
        super().__init__(**kwargs)
        self.name = 'background_settings'
        self.color_buttons = []  # 存储所有颜色按钮，便于更新标记
        self.build_ui()

        # 加载当前设置
        app = App.get_running_app()
        current_settings = BackgroundSettings.load_background_settings(app)
        # 应用加载的设置
        self._apply_loaded_settings(current_settings)

    def _apply_loaded_settings(self , settings) :
        """应用加载的设置并同步所有UI元素状态"""
        self.bg_mode = settings['mode']
        self.selected_color = settings['color']
        self.image_path = settings['image']

        self.update_mode_switches()
        self.update_color_markers()

        self.image_path_label.text = "未选择图片" if not self.image_path else os.path.basename(self.image_path)
        if self.image_path and os.path.exists(self.image_path) :
            self.image_preview.source = self.image_path
        else :
            self.image_preview.source = ""

    def build_ui(self) :
        """构建背景设置窗口UI"""
        main_scroll = ScrollView(
            size_hint = (1 , 1) ,
            bar_width = dp(8) ,
            bar_color = [0.7 , 0.7 , 0.7 , 0.8] ,
            bar_inactive_color = [0.5 , 0.5 , 0.5 , 0.5]
        )

        main_layout = BoxLayout(
            orientation = 'vertical' ,
            padding = [dp(25) , dp(25)] ,
            spacing = dp(40) ,
            size_hint = (1 , None)
        )
        main_layout.bind(minimum_height = main_layout.setter('height'))

        # 标题区域
        title_container = BoxLayout(
            size_hint_y = None ,
            height = dp(70) ,
            padding = [0 , dp(10)]
        )
        title_label = Label(
            text = "登录背景设置" ,
            font_size = dp(24) ,
            size_hint_y = None ,
            height = dp(60) ,
            halign = 'center' ,
            font_name = 'simhei.ttf' ,
            color = (0 , 0 , 0 , 1)
        )
        title_container.add_widget(title_label)
        main_layout.add_widget(title_container)

        # 分隔线
        separator = Widget(size_hint_y = None , height = dp(5))
        with separator.canvas :
            Color(0.8 , 0.8 , 0.8 , 0.5)
            separator.rect = Rectangle(pos = separator.pos , size = separator.size)

        def update_separator_pos(instance , value) :
            instance.rect.pos = instance.pos

        def update_separator_size(instance , value) :
            instance.rect.size = instance.size

        separator.bind(pos = update_separator_pos , size = update_separator_size)
        main_layout.add_widget(separator)

        # 模式选择区域
        mode_section = BoxLayout(
            orientation = 'horizontal' ,
            size_hint_y = None ,
            height = dp(100) ,  # 增加高度确保容纳
            spacing = dp(20) ,
            padding = [dp(20) , 0]
        )

        # 颜色模式开关
        self.color_mode_switch = ToggleSwitch(
            labels = ['颜色背景'] ,
            active = self.bg_mode == 'color' ,
            size = [dp(120) , dp(40)] ,
            thumb_size = [dp(20) , dp(20)]
        )
        self.color_mode_switch.bind(active = self.on_color_mode_selected)

        # 图片模式开关
        self.image_mode_switch = ToggleSwitch(
            labels = ['图片背景'] ,
            active = self.bg_mode == 'image' ,
            size = [dp(120) , dp(40)] ,
            thumb_size = [dp(20) , dp(20)]
        )
        self.image_mode_switch.bind(active = self.on_image_mode_selected)

        # 模式容器布局
        mode_container = BoxLayout(
            orientation = 'vertical' ,
            size_hint_x = None ,
            width = dp(240) ,
            size_hint_y = None ,
            spacing = dp(20)  # 增加间距
        )
        mode_container.bind(minimum_height = mode_container.setter('height'))
        mode_container.add_widget(self.color_mode_switch)
        mode_container.add_widget(self.image_mode_switch)

        mode_section.add_widget(mode_container)
        main_layout.add_widget(mode_section)

        # 颜色选择区域
        color_section = BoxLayout(
            orientation = 'vertical' ,
            size_hint_y = None ,
            height = dp(280) ,
            spacing = dp(15) ,
            padding = [dp(10) , 0]
        )
        color_label = Label(
            text = "背景颜色:" ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(18) ,
            color = (0 , 0 , 0 , 1)
        )

        color_grid_container = BoxLayout(
            size_hint_y = None ,
            padding = [dp(10) , 0] ,
            height = dp(220)
        )

        color_grid = GridLayout(
            cols = 7 ,
            rows = 3 ,
            spacing = dp(12) ,
            padding = [dp(10) , dp(10)] ,
            size_hint_y = None ,
            height = dp(200)
        )

        colors = [
            (1 , 1 , 1 , 1) , (0.95 , 0.95 , 0.95 , 1) , (0.8 , 0.9 , 0.95 , 1) , (0.95 , 0.9 , 0.8 , 1) ,
            (0.9 , 0.95 , 0.8 , 1) , (0.95 , 0.8 , 0.8 , 1) , (0.8 , 0.8 , 0.95 , 1) ,
            (0.75 , 0.75 , 0.75 , 1) , (0.6 , 0.8 , 0.9 , 1) , (0.8 , 0.6 , 0.9 , 1) , (0.9 , 0.8 , 0.6 , 1) ,
            (0.8 , 0.9 , 0.6 , 1) , (0.9 , 0.6 , 0.6 , 1) , (0.6 , 0.6 , 0.9 , 1) ,
            (0.5 , 0.5 , 0.5 , 1) , (0.4 , 0.7 , 0.9 , 1) , (0.7 , 0.4 , 0.9 , 1) , (0.9 , 0.7 , 0.4 , 1) ,
            (0.7 , 0.9 , 0.4 , 1) , (0.9 , 0.4 , 0.4 , 1) , (0.4 , 0.4 , 0.9 , 1)
        ]

        for color in colors :
            color_btn = Button(
                size_hint = (None , None) ,
                size = (dp(40) , dp(40)) ,
                background_color = color ,
                background_normal = '' ,
                border = (0 , 0 , 0 , 0)
            )

            with color_btn.canvas.before :
                Color(0 , 0 , 0 , 0.15)
                color_btn.shadow = RoundedRectangle(
                    pos = (color_btn.x + dp(2) , color_btn.y - dp(2)) ,
                    size = (color_btn.size[0] , color_btn.size[1]) ,
                    radius = [dp(8)]
                )

            with color_btn.canvas.after :
                color_btn.marker_color = Color(0 , 0 , 0 , 0)
                color_btn.marker_line = Line(
                    width = dp(2) ,
                    circle = (color_btn.center_x , color_btn.center_y , dp(11)) ,
                    close = True
                )
                color_btn.check = Line(
                    points = [] ,
                    width = dp(2) ,
                    close = False
                )

            def create_update_func(btn) :
                def update_func(instance , value) :
                    setattr(instance , 'shadow' ,
                            RoundedRectangle(
                                pos = (instance.x + dp(2) , instance.y - dp(2)) ,
                                size = instance.size ,
                                radius = [dp(8)]
                            )
                            )
                    self.update_marker_pos(instance , value)

                return update_func

            update_func = create_update_func(color_btn)
            color_btn.bind(
                pos = update_func ,
                size = update_func
            )

            color_btn.bind(on_press = lambda btn , c=color : self.select_color(btn , c))
            color_grid.add_widget(color_btn)
            self.color_buttons.append(color_btn)

        color_grid_container.add_widget(color_grid)
        color_section.add_widget(color_label)
        color_section.add_widget(color_grid_container)
        main_layout.add_widget(color_section)

        main_layout.add_widget(Widget(size_hint_y = None , height = dp(80)))

        # 图片选择区域
        image_section = BoxLayout(
            orientation = 'vertical' ,
            size_hint_y = None ,
            height = dp(400) ,
            spacing = dp(20) ,
            padding = [dp(10) , 0]
        )
        image_label = Label(
            text = "背景图片:" ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(18) ,
            color = (0 , 0 , 0 , 1)
        )

        select_btn = RoundedButton(
            text = "选择图片" ,
            size_hint_y = None ,
            height = dp(60) ,
            font_name = 'simhei.ttf' ,
            radius = dp(25) ,
            color = (1 , 1 , 1 , 1) ,
            background_color = (0.2 , 0.5 , 0.8 , 1) ,
            padding = [dp(20) , 0]
        )
        select_btn.bind(on_press = self.select_image)

        self.image_path_label = Label(
            text = "未选择图片" ,
            size_hint_y = None ,
            height = dp(40) ,
            halign = 'left' ,
            font_name = 'simhei.ttf' ,
            color = (0.3 , 0.3 , 0.3 , 1)
        )

        preview_container = BoxLayout(
            size_hint_y = None ,
            padding = [dp(10) , dp(5)] ,
            height = dp(250) ,
            orientation = 'vertical'
        )

        preview_hint = Label(
            text = "图片预览:" ,
            size_hint_y = None ,
            height = dp(30) ,
            font_name = 'simhei.ttf' ,
            font_size = dp(14) ,
            color = (0.5 , 0.5 , 0.5 , 1)
        )

        preview_frame = AnchorLayout(
            size_hint_y = None ,
            height = dp(210) ,
            padding = dp(5)
        )

        border_container = BoxLayout(
            size_hint = (1 , 1)
        )

        border_container.canvas.before.clear()
        with border_container.canvas.before :
            Color(0 , 0 , 0 , 0.1)
            border_container.shadow = RoundedRectangle(
                pos = (border_container.x - dp(2) , border_container.y - dp(2)) ,
                size = (border_container.size[0] + dp(4) , border_container.size[1] + dp(4)) ,
                radius = [dp(8)]
            )
            Color(0.9 , 0.9 , 0.9 , 1)
            border_container.border_line = RoundedRectangle(
                pos = border_container.pos ,
                size = border_container.size ,
                radius = [dp(6)]
            )

        def update_preview_border(instance , value) :
            instance.shadow.pos = (instance.x - dp(2) , instance.y - dp(2))
            instance.shadow.size = (instance.size[0] + dp(4) , instance.size[1] + dp(4))
            instance.border_line.pos = instance.pos
            instance.border_line.size = instance.size

        border_container.bind(pos = update_preview_border , size = update_preview_border)

        self.image_preview = AsyncImage(
            size_hint = (None , None) ,
            fit_mode = "contain"
        )

        border_container.add_widget(self.image_preview)
        preview_frame.add_widget(border_container)
        preview_container.add_widget(preview_hint)
        preview_container.add_widget(preview_frame)
        image_section.add_widget(image_label)
        image_section.add_widget(select_btn)
        image_section.add_widget(self.image_path_label)
        image_section.add_widget(preview_container)
        main_layout.add_widget(image_section)

        main_layout.add_widget(Widget(size_hint_y = None , height = dp(50)))

        # 按钮区域
        btn_layout = BoxLayout(
            orientation = 'horizontal' ,
            size_hint_y = None ,
            height = dp(70) ,
            spacing = dp(40) ,
            padding = [dp(20) , dp(10)]
        )

        cancel_btn = RoundedButton(
            text = "取消" ,
            size_hint_x = 0.5 ,
            background_color = (0.85 , 0.85 , 0.85 , 1) ,
            color = (0.3 , 0.3 , 0.3 , 1) ,
            font_name = 'simhei.ttf' ,
            radius = dp(25) ,
            padding = [dp(10) , 0]
        )
        cancel_btn.bind(on_press = self.go_back)

        confirm_btn = RoundedButton(
            text = "保存" ,
            size_hint_x = 0.5 ,
            background_color = (0.3 , 0.7 , 0.3 , 1) ,
            color = (1 , 1 , 1 , 1) ,
            font_name = 'simhei.ttf' ,
            radius = dp(25) ,
            padding = [dp(10) , 0]
        )
        confirm_btn.bind(on_press = self.on_confirm)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        main_layout.add_widget(btn_layout)

        main_layout.add_widget(Widget(size_hint_y = None , height = dp(30)))

        main_scroll.add_widget(main_layout)
        self.add_widget(main_scroll)

    def _sync_modes(self) :
        """同步两个开关的互斥状态"""
        active = self.bg_mode == 'color'
        self.color_mode_switch.active = active
        self.image_mode_switch.active = not active

    def update_mode_switches(self) :
        """根据当前bg_mode更新切换开关状态"""
        self.color_mode_switch.active = self.bg_mode == 'color'
        self.image_mode_switch.active = self.bg_mode == 'image'

    def _update_preview(self) :
        """更新图片预览区域"""
        if self.bg_mode == 'image' and os.path.exists(self.image_path) :
            self.image_preview.source = self.image_path
            self.image_preview.reload()
        else :
            self.image_preview.source = ""

    def on_color_mode_selected(self , instance , value) :
        if value :
            self.bg_mode = 'color'
            self._sync_modes()
            self.update_color_markers()
            self.image_preview.source = ""

    def on_image_mode_selected(self , instance , value) :
        if value :
            self.bg_mode = 'image'
            self._sync_modes()
            self._update_preview()

    def update_marker_pos(self , instance , value) :
        """更新标记的位置和大小"""
        instance.marker_line.circle = (instance.center_x , instance.center_y , dp(11))

        if instance.background_color == self.selected_color :
            center_x , center_y = instance.center_x , instance.center_y
            instance.check.points = [
                center_x - dp(6) , center_y + dp(2) ,
                center_x , center_y - dp(3) ,
                center_x + dp(6) , center_y + dp(3)
            ]
        else :
            instance.check.points = []

    def update_color_markers(self) :
        """更新所有颜色按钮的标记状态"""
        for btn in self.color_buttons :
            if btn.background_color == self.selected_color :
                btn.marker_color.rgba = (0.2 , 0.6 , 0.2 , 1)
                center_x , center_y = btn.center_x , btn.center_y
                btn.check.points = [
                    center_x - dp(6) , center_y + dp(2) ,
                    center_x , center_y - dp(3) ,
                    center_x + dp(6) , center_y + dp(3)
                ]
            else :
                btn.marker_color.rgba = (0 , 0 , 0 , 0)
                btn.check.points = []

    def select_color(self , instance , color) :
        """选择颜色并更新标记"""
        self.selected_color = color
        self.bg_mode = 'color'
        self.update_mode_switches()
        self.update_color_markers()

    def select_image(self , instance) :
        """选择背景图片"""

        def on_select(selection) :
            if selection and selection[0] :
                self.image_path = os.path.abspath(selection[0])
                self.bg_mode = 'image'
                self.update_mode_switches()
                self.image_path_label.text = os.path.basename(self.image_path)
                self.image_preview.source = self.image_path
            popup.dismiss()

        file_chooser = FileChooserListView(
            filters = ['*.png' , '*.jpg' , '*.jpeg' , '*.bmp'] ,
            path = os.path.expanduser('~')
        )

        select_btn = RoundedButton(
            text = "选择" ,
            size_hint_y = None ,
            height = dp(40) ,
            font_name = 'simhei.ttf' ,
            radius = dp(20)
        )
        select_btn.bind(on_press = lambda x : on_select(file_chooser.selection))

        main_layout = BoxLayout(orientation = 'vertical')
        main_layout.add_widget(file_chooser)
        main_layout.add_widget(select_btn)

        popup = Popup(
            title = "选择背景图片" ,
            content = main_layout ,
            size_hint = (0.9 , 0.9)
        )
        popup.open()

    def on_confirm(self , instance) :
        app = App.get_running_app()

        if self.bg_mode == 'image' :
            if not self.image_path or not os.path.isfile(self.image_path) :
                popup = CustomDialog("请选择有效的图片文件" , title = "验证错误" , button_text = "重新选择")
                popup.open()
                return

        settings = {
            'mode' : self.bg_mode ,
            'color' : self.selected_color ,
            'image' : self.image_path if self.bg_mode == 'image' else ""
        }
        BackgroundSettings.save_background_settings(app , settings['mode'] , settings['color'] , settings['image'])

        login_screen = self.manager.get_screen('login') if 'login' in self.manager.screens else None
        if login_screen :
            BackgroundSettings.apply_settings_to_screen(login_screen , settings)
            if hasattr(login_screen , 'update_background') :
                login_screen.update_background(None , None)

        self.go_back(None)

    def go_back(self , instance) :
        if hasattr(self , 'manager') :
            self.manager.transition = SlideTransition(direction = 'right')
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
        self.bg_image_widget = None  # 存储背景图片控件引用
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

        # 用户名输入区、密码输入区和按钮区域代码保持不变...
        # 用户名输入区
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

        # 用户名输入框容器
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

        # 密码输入区
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

        # 密码输入框容器
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

        # 按钮区域
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

        # 创建背景层布局，用于放置背景元素
        self.bg_layout = FloatLayout(size_hint = (1 , 1))

        # 添加背景颜色层 - 初始化为默认背景色
        with self.bg_layout.canvas.before :
            self.bg_color_inst = Color(*self.bg_color)
            self.bg_rect = Rectangle(pos = self.pos , size = self.size)

        # 添加背景图片控件（使用AsyncImage确保正确加载）
        self.bg_image_widget = AsyncImage(
            pos = self.pos ,
            size = self.size ,
            allow_stretch = True ,
            keep_ratio = False ,
            opacity = 0.0 ,  # 初始完全透明
            mipmap = True  # 启用mipmap提升渲染质量
        )
        # 绑定图片加载完成事件
        self.bg_image_widget.bind(on_load = self.on_image_loaded)
        self.bg_layout.add_widget(self.bg_image_widget)

        # 将背景层和主布局组合
        root_layout = FloatLayout()
        root_layout.add_widget(self.bg_layout)
        root_layout.add_widget(main_layout)
        self.add_widget(root_layout)

        # 绑定位置和大小变化，更新背景
        self.bind(pos = self.update_bg_position , size = self.update_bg_position)


    # 图片加载完成回调
    def on_image_loaded(self, instance):
        """图片加载完成后执行淡入动画（修正参数数量）"""
        if self.bg_mode == "image":
            # 图片加载成功，执行淡入动画
            anim = Animation(opacity=1.0, duration=0.5)
            anim.start(self.bg_image_widget)
            # 同时淡出背景色
            color_anim = Animation(rgba=(0, 0, 0, 0), duration=0.5)
            color_anim.start(self.bg_color_inst)

    # 更新背景位置和大小
    def update_bg_position(self , instance , value) :
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        if self.bg_image_widget :
            self.bg_image_widget.pos = self.pos
            self.bg_image_widget.size = self.size

    # 更新背景显示 - 改进图片显示逻辑
    def update_background(self , instance , value) :
        """更新背景显示（增强错误处理和路径验证）"""
        # 确保bg_image_widget已初始化
        if not self.bg_image_widget :
            return

        # 重置背景显示
        self.bg_color_inst.rgba = self.bg_color if self.bg_mode == "color" else (0 , 0 , 0 , 0)
        self.bg_image_widget.source = ""
        self.bg_image_widget.opacity = 0.0  # 保持透明直到加载完成

        # 图片模式处理
        if self.bg_mode == "image" and self.bg_image :
            # 验证图片文件是否存在（使用绝对路径检查）
            if os.path.isfile(self.bg_image) :
                try :
                    # 确保路径是绝对路径
                    absolute_path = os.path.abspath(self.bg_image)

                    # 设置图片源，但保持透明直到加载完成
                    self.bg_image_widget.source = absolute_path

                    # 调试信息
                    print(f"开始加载背景图片: {absolute_path}")

                except Exception as e :
                    # 图片加载失败处理
                    error_msg = f"图片加载失败: {str(e)}"
                    print(error_msg)  # 控制台输出错误
                    self._show_bg_error(error_msg)
                    self._switch_to_color_mode()
            else :
                # 图片不存在处理
                error_msg = f"图片文件不存在: {os.path.basename(self.bg_image)}"
                print(error_msg)  # 控制台输出错误
                self._show_bg_error(error_msg)
                self._switch_to_color_mode()

        # 颜色模式处理
        if self.bg_mode == "color" :
            self.bg_color_inst.rgba = self.bg_color
            self.bg_image_widget.opacity = 0.0  # 隐藏图片

        # 保存设置
        app = App.get_running_app()
        BackgroundSettings.save_background_settings(app , self.bg_mode , self.bg_color , self.bg_image)

    # 新增辅助方法
    def _show_bg_error(self , message) :
        """显示背景设置错误提示"""
        popup = CustomDialog(message , title = "背景设置错误" , button_text = "知道了")
        popup.open()

    def _switch_to_color_mode(self) :
        """切换到颜色模式并更新设置"""
        self.bg_mode = "color"
        self.bg_image = ""
        # 同步更新应用设置
        app = App.get_running_app()
        BackgroundSettings.save_background_settings(app , "color" , self.bg_color , "")

    # 其他方法保持不变
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

    # 登录逻辑
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

    # 菜单功能
    def goto_background_settings(self , instance) :
        self.manager.transition = SlideTransition(direction = 'left')
        self.manager.current = 'background_settings'

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


# 管理员窗口类
class AdminWindow(Screen):
    user_tree = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'admin'
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))

        # 标题
        title_label = Label(
            text="用户管理",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50),
            font_name='simhei.ttf',
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(title_label)

        # 用户列表
        scroll_view = ScrollView()
        self.user_tree = TreeView(
            root_options=dict(text='用户列表'),
            hide_root=True,
            size_hint_y=None
        )
        self.user_tree.bind(minimum_height=self.user_tree.setter('height'))
        scroll_view.add_widget(self.user_tree)
        main_layout.add_widget(scroll_view)

        # 按钮区域
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        add_btn = RoundedButton(
            text="添加用户",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_press=self.show_add_user_dialog)

        del_btn = RoundedButton(
            text="删除用户",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        del_btn.bind(on_press=self.delete_user)

        back_btn = RoundedButton(
            text="返回",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=lambda x: self.go_back(x))

        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(del_btn)
        btn_layout.add_widget(back_btn)
        main_layout.add_widget(btn_layout)

        self.add_widget(main_layout)
        Clock.schedule_once(lambda dt: self.load_users(), 0.1)  # 延迟加载用户数据

    def load_users(self):
        if self.user_tree:
            self.user_tree.clear_widgets()
            for node in self.user_tree.iterate_all_nodes():
                self.user_tree.remove_node(node)

        users_info = load_users_info()
        current_user = None
        
        if hasattr(self, 'manager') and 'login' in self.manager.screen_names:
            login_screen = self.manager.get_screen('login')
            if hasattr(login_screen, 'current_user'):
                current_user = login_screen.current_user

        for hashed_name, info in users_info.items():
            if current_user is None or info['username'] != current_user:
                node = TreeViewLabel(text=f"{info['username']} - {info['register_time']}",
                                     size_hint_y=None, height=dp(30),
                                     color=(0, 0, 0, 1))
                self.user_tree.add_node(node)

    def show_add_user_dialog(self, instance):
        content = AddUserWindow(self)
        popup = Popup(
            title="添加新用户",
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        content.popup = popup
        popup.open()

    def delete_user(self, instance):
        selected = self.user_tree.selected_node
        if not selected:
            popup = CustomDialog("请先选择要删除的用户", title="提示", button_text="知道了")
            popup.open()
            return

        username = selected.text.split(' - ')[0]
        users_info = load_users_info()
        
        for hashed_name, info in users_info.items():
            if info['username'] == username:
                del users_info[hashed_name]
                save_users_info(users_info)
                self.load_users()
                popup = CustomDialog(f"用户 {username} 已删除", title="成功", button_text="确定")
                popup.open()
                return

    def go_back(self, instance):
        if hasattr(self, 'manager'):
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'login'


# 添加用户窗口类
class AddUserWindow(BoxLayout):
    def __init__(self, admin_window, **kwargs):
        self.admin_window = admin_window
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.build_ui()
        
    def build_ui(self):
        # 用户名输入
        self.username_input = TextInput(
            hint_text="请输入用户名",
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            padding=[dp(10), 0],
            foreground_color=(0, 0, 0, 1)
        )
        self.add_widget(self.username_input)

        # 密码输入
        self.password_input = TextInput(
            hint_text="请输入密码",
            password=True,
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            padding=[dp(10), 0],
            foreground_color=(0, 0, 0, 1)
        )
        self.add_widget(self.password_input)

        # 确认密码
        self.confirm_password_input = TextInput(
            hint_text="请确认密码",
            password=True,
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            padding=[dp(10), 0],
            foreground_color=(0, 0, 0, 1)
        )
        self.add_widget(self.confirm_password_input)

        # 按钮
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        cancel_btn = RoundedButton(
            text="取消",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_press=self.cancel)

        create_btn = RoundedButton(
            text="创建",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        create_btn.bind(on_press=self.create_user)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(create_btn)
        self.add_widget(btn_layout)

    def cancel(self, instance):
        if hasattr(self, 'popup'):
            self.popup.dismiss()

    def create_user(self):
        username = self.username_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text

        if not username or not password:
            popup = CustomDialog("用户名和密码不能为空", title="错误", button_text="知道了")
            popup.open()
            return

        if password != confirm_password:
            popup = CustomDialog("两次输入的密码不一致", title="错误", button_text="知道了")
            popup.open()
            return

        users_info = load_users_info()
        hashed_name = hash_string(username)
        
        if hashed_name in users_info:
            popup = CustomDialog("用户已存在", title="错误", button_text="知道了")
            popup.open()
            return

        users_info[hashed_name] = {
            'hashed_pwd': hash_string(password),
            'username': username,
            'register_time': time.strftime("%Y-%m-%d %H:%M:%S"),
            'is_admin': False
        }
        save_users_info(users_info)
        
        if hasattr(self, 'popup'):
            self.popup.dismiss()
        
        if self.admin_window:
            self.admin_window.load_users()
        
        popup = CustomDialog(f"用户 {username} 创建成功", title="成功", button_text="确定")
        popup.open()

    def __init__(self, admin_window, **kwargs):
        self.admin_window = admin_window
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.build_ui()

    def build_ui(self):
        # 用户名输入
        self.username_input = TextInput(
            hint_text="请输入用户名",
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            padding=[dp(10), 0],
            foreground_color=(0, 0, 0, 1)  # 确保字体颜色为黑色
        )
        self.add_widget(self.username_input)

        # 密码输入
        self.password_input = TextInput(
            hint_text="请输入密码",
            password=True,
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            padding=[dp(10), 0],
            foreground_color=(0, 0, 0, 1)  # 确保字体颜色为黑色
        )
        self.add_widget(self.password_input)

        # 确认密码
        self.confirm_password_input = TextInput(
            hint_text="请确认密码",
            password=True,
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            padding=[dp(10), 0],
            foreground_color=(0, 0, 0, 1)  # 确保字体颜色为黑色
        )
        self.add_widget(self.confirm_password_input)

        # 按钮
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(45))
        cancel_btn = RoundedButton(
            text="取消",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_press=self.cancel)

        create_btn = RoundedButton(
            text="创建",
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        create_btn.bind(on_press=lambda x: self.create_user())

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(create_btn)
        self.add_widget(btn_layout)


# 百度热搜窗口类
class NewsWindow(Screen):
    news_list = ObjectProperty(None)
    status_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'news'
        self.build_ui()  # 添加UI构建

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))

        # 返回按钮
        back_btn = RoundedButton(
            text="返回",
            size_hint_y=None,
            height=dp(45),
            font_name='simhei.ttf',
            radius=dp(20),
            background_color=(0.6, 0.6, 0.6, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)

        # 标题
        title_label = Label(
            text="百度热搜",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50),
            font_name='simhei.ttf',
            color=(0, 0, 0, 1)
        )
        main_layout.add_widget(title_label)

        # 刷新按钮
        refresh_btn = RoundedButton(
            text="刷新",
            size_hint_y=None,
            height=dp(40),
            font_name='simhei.ttf',
            radius=dp(15),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.load_news())
        main_layout.add_widget(refresh_btn)

        # 新闻列表容器
        scroll_view = ScrollView()
        self.news_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.news_list.bind(minimum_height=self.news_list.setter('height'))
        scroll_view.add_widget(self.news_list)
        main_layout.add_widget(scroll_view)

        # 状态标签
        self.status_label = Label(
            text="准备就绪",
            size_hint_y=None,
            height=dp(30),
            font_name='simhei.ttf',
            color=(0.1, 0.3, 0.8, 1)
        )
        main_layout.add_widget(self.status_label)

        self.add_widget(main_layout)

    def on_enter(self):
        self.load_news()

    def load_news(self):
        self.status_label.text = "正在加载热搜数据..."
        self.status_label.color = (0.5, 0.5, 0.5, 1)
        
        if self.news_list:
            self.news_list.clear_widgets()

        url = 'https://top.baidu.com/board?tab=realtime'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

        try:
            loading_label = Label(
                text="数据加载中，请稍候...",
                size_hint_y=None,
                height=dp(30),
                font_name='simhei.ttf'
            )
            self.news_list.add_widget(loading_label)

            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = soup.find_all('div', class_='c-single-text-ellipsis')
            hot_numbers = soup.find_all('div', class_='hot-index_1Bl1a')

            self.news_list.clear_widgets()

            if not news_items:
                no_data_label = Label(
                    text="无热搜数据",
                    size_hint_y=None,
                    height=dp(30),
                    color=(0.6, 0.6, 0.6, 1),
                    font_name='simhei.ttf'
                )
                self.news_list.add_widget(no_data_label)
                self.status_label.text = "加载完成，未获取到数据"
                self.status_label.color = (0.8, 0.4, 0, 1)
                return

            for i, (item, number) in enumerate(zip(news_items[:100], hot_numbers[:100])):
                title = item.get_text(strip=True)
                hot_number = number.get_text(strip=True)

                item_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40)
                )

                rank_label = Label(
                    text=f"{i + 1}.",
                    size_hint_x=0.1,
                    color=(0.5, 0.2, 0.8, 1),
                    font_name='simhei.ttf'
                )

                title_label = Label(
                    text=title,
                    size_hint_x=0.7,
                    halign='left',
                    valign='middle',
                    color=(0, 0, 0, 1),
                    font_name='simhei.ttf',
                    text_size=(self.width * 0.7, None)
                )

                hot_label = Label(
                    text=hot_number,
                    size_hint_x=0.2,
                    color=(0.8, 0, 0, 1),
                    font_name='simhei.ttf'
                )

                item_layout.add_widget(rank_label)
                item_layout.add_widget(title_label)
                item_layout.add_widget(hot_label)
                self.news_list.add_widget(item_layout)

            self.status_label.text = f"加载完成，共 {len(news_items)} 条热搜"
            self.status_label.color = (0, 0.6, 0.2, 1)

        except Exception as e:
            error_label = Label(
                text=f"加载失败: {str(e)}",
                size_hint_y=None,
                height=dp(30),
                color=(1, 0, 0, 1),
                font_name='simhei.ttf'
            )
            self.news_list.add_widget(error_label)
            self.status_label.text = "加载失败"
            self.status_label.color = (1, 0, 0, 1)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
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
        sm.add_widget(BackgroundSettingsWindow())
        sm.add_widget(NewsWindow())

        return sm



if __name__ == '__main__' :
    MainApp().run()

