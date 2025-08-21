from kivy.animation import Animation  # 正确的动画导入
from kivy.graphics import RoundedRectangle , Color
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import StringProperty , ObjectProperty , ListProperty , NumericProperty , BooleanProperty
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel

# 注册中文字体
LabelBase.register(name = 'SimHei' ,
                   fn_regular = 'C:/Windows/Fonts/simhei.ttf')

Builder.load_string('''
<CustomDialog>:
    size_hint: (0.8, 0.5)
    auto_dismiss: False
    title_size: '20sp'
    title_font: 'SimHei'
    title_align: 'center'
    title_color: 0, 0, 0, 1  # 黑色标题
    separator_height: 0  # 去除分隔线

    BoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        canvas.before:
            Color:
                rgba: 1, 1, 1, 1  # 白色背景
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: [15,]

        Label:
            id: content_label
            text: root.text
            font_name: 'SimHei'
            font_size: '16sp'
            size_hint_y: 0.7
            text_size: self.width, None
            halign: 'center'
            valign: 'middle'
            color: 0, 0, 0, 1  # 黑色文本

        RoundedButton:
            text: root.button_text
            size_hint_y: 0.3
            on_release: root.dismiss()
''')


# 自定义圆形按钮组件
class RoundedButton(ButtonBehavior , BoxLayout) :
    text = StringProperty('')
    background_color = ObjectProperty((0.2 , 0.6 , 1 , 1))
    color = ObjectProperty((1 , 1 , 1 , 1))
    font_name = StringProperty('SimHei')
    font_size = ObjectProperty(dp(16))
    radius = ListProperty([dp(10)])
    width_ratio = NumericProperty(0.8)

    def __init__(self , **kwargs) :
        if 'radius' in kwargs :
            radius = kwargs['radius']
            if not isinstance(radius , list) :
                kwargs['radius'] = [radius]

        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [dp(20) , dp(5)]
        self.size_hint_y = None
        self.height = dp(50)  # 增加按钮高度

        self.bind(parent = self._update_width , width_ratio = self._update_width)

        with self.canvas.before :
            self.bg_color_inst = Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos = self.pos ,
                size = self.size ,
                radius = self.radius
            )

        self.bind(
            pos = self.update_bg ,
            size = self.update_bg ,
            background_color = self.update_bg_color ,
            radius = self.update_radius
        )

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
        self.bg_color_inst.rgba = value

    def update_radius(self , instance , value) :
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


# 自定义对话框组件
class CustomDialog(Popup) :
    text = StringProperty('')
    button_text = StringProperty('')

    def __init__(self , text , title , button_text , **kwargs) :
        self.background = ''
        self.background_color = [0 , 0 , 0 , 0]
        self.title_color = [0 , 0 , 0 , 1]  # 设置标题颜色
        super(CustomDialog , self).__init__(**kwargs)
        self.text = text
        self.title = title
        self.button_text = button_text


# 自定义切换按钮组件 - 简约高级版

class StyledLabel(Label):
    """左侧标签组件"""
    active = BooleanProperty(False)
    active_color = ListProperty([0, 0, 0, 1])  # 激活时黑色
    inactive_color = ListProperty([0.5, 0.5, 0.5, 1])  # 非激活时灰色
    font_name = StringProperty('SimHei')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = dp(16)
        self.size_hint = (None, None)
        self.halign = 'left'
        self.valign = 'middle'
        self.color = self.active_color if self.active else self.inactive_color
        self.shorten = False
        self.bind(
            active=self._update_text_color,
            text=self._adjust_width
        )
        self._adjust_width()

    def _adjust_width(self, *args):
        """根据文本内容调整宽度"""
        core_label = CoreLabel(text=self.text, font_size=self.font_size, font_name=self.font_name)
        core_label.refresh()
        self.width = core_label.texture.size[0]
        self.height = core_label.texture.size[1]

    def _update_text_color(self, instance, value):
        """更新文本颜色"""
        self.color = self.active_color if self.active else self.inactive_color


class ToggleSwitch(Widget):
    """iOS风格开关组件（标签左，按钮右）"""
    active = BooleanProperty(False)
    label_text = StringProperty('选项')  # 左侧标签文本
    active_color = ListProperty([0.34, 0.73, 0.33, 1])  # 激活时绿色
    inactive_color = ListProperty([0.74, 0.74, 0.74, 1])  # 非激活时灰色
    thumb_color = ListProperty([1, 1, 1, 1])  # 白色滑块
    size = ListProperty([dp(300), dp(36)])  # 整体尺寸
    animation_duration = NumericProperty(0.2)
    thumb_size = ListProperty([dp(30), dp(30)])  # 滑块尺寸

    def __init__(self, **kwargs):
        self.register_event_type('on_state_change')
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width, self.height = self.size

        # 左侧标签
        self.label = StyledLabel(text=self.label_text)
        self.add_widget(self.label)

        # 右侧开关容器
        self.switch_container = Widget(size_hint=(None, None), size=(dp(50), self.thumb_size[1]))
        self.add_widget(self.switch_container)

        # 滑块
        self.thumb = Widget(size_hint=(None, None), size=self.thumb_size)
        self.switch_container.add_widget(self.thumb)

        self._init_canvas()

        # 绑定事件
        self.bind(
            label_text = self._update_label_text ,
            size = self._update_positions ,
            pos = self._update_positions ,
            active = self._update_positions ,
            active_color = self._update_colors ,
            inactive_color = self._update_colors ,
            thumb_color = self._update_thumb_color ,
        )
        self.bind(active = self._update_colors)  # 单独再绑定一次
        self.label.bind(size=self._update_positions)
        self._update_positions()

    def _init_canvas(self):
        """初始化画布（绘制开关背景和滑块）"""
        self.canvas.before.clear()
        with self.canvas.before:
            # 开关背景
            self.bg_color = Color(*self.inactive_color)
            self.bg_rect = RoundedRectangle(
                pos=self.switch_container.pos,
                size=self.switch_container.size,
                radius=[dp(18)]
            )
            # 滑块
            self.thumb_color_inst = Color(*self.thumb_color)
            self.thumb_rect = RoundedRectangle(
                pos=self.thumb.pos,
                size=self.thumb_size,
                radius=[dp(15)]
            )

    def _update_positions(self, *args):
        """更新所有元素位置（确保按钮在最右侧）"""
        self.width, self.height = self.size
        # 标签定位
        self.label.pos = (self.x, self.y + (self.height - self.label.height) / 2)
        self.label.active = self.active

        # 开关容器定位
        self.switch_container.size = (dp(50), self.thumb_size[1])
        self.switch_container.pos = (
            self.x + self.width - self.switch_container.width,
            self.y + (self.height - self.switch_container.height) / 2
        )

        # 背景位置
        self.bg_rect.pos = self.switch_container.pos
        self.bg_rect.size = self.switch_container.size

        # 滑块位置
        if self.active:
            thumb_x = self.switch_container.right - self.thumb_size[0] - dp(2)
        else:
            thumb_x = self.switch_container.x + dp(2)
        self.thumb.pos = (thumb_x, self.switch_container.y + (self.switch_container.height - self.thumb_size[1]) / 2)
        self.thumb_rect.pos = self.thumb.pos
        self.thumb_rect.size = self.thumb_size

    def _update_label_text(self, *args):
        """更新标签文本"""
        self.label.text = self.label_text

    def _update_colors(self, *args):
        """更新开关背景颜色"""
        self.bg_color.rgba = self.active_color if self.active else self.inactive_color

    def _update_thumb_color(self, *args):
        """更新滑块颜色"""
        self.thumb_color_inst.rgba = self.thumb_color

    def on_touch_down(self, touch):
        """点击交互"""
        # 允许点击标签或开关区域都能切换
        if self.collide_point(*touch.pos):
            if (self.label.collide_point(*touch.pos) or
                    self.switch_container.collide_point(*touch.pos)):
                self._set_active(not self.active)
                return True
        return super().on_touch_down(touch)

    def _set_active(self , value) :
        if self.active == value :
            return

        if value :
            target_x = self.switch_container.right - self.thumb_size[0] - dp(2)
        else :
            target_x = self.switch_container.x + dp(2)

        def _after_anim(*_) :
            self.active = value
            # 下面方法确保所有控件和画布同步
            self._update_positions()
            self._update_colors()
            self._update_thumb_color()
            self.label.active = value
            self.label._update_text_color(self.label , value)
            self.dispatch('on_state_change' , value)

        anim = Animation(
            x = target_x ,
            duration = self.animation_duration ,
            t = 'out_quad'
        )
        anim.bind(on_complete = _after_anim)
        anim.start(self.thumb)

    def on_state_change(self, value):
        """状态改变回调（供外部绑定）"""
        pass