import os
import threading
from functools import partial
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    StringProperty, NumericProperty, ListProperty,
    BooleanProperty, DictProperty, ObjectProperty
)
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

# --- Try to import yt-dlp ---
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("WARNING: yt-dlp not found. Install with: pip install yt-dlp")

# --- Set a standard mobile window size ---
Window.size = (375, 812) # Emulates an iPhone X/11/12 screen

#<--- KIVY DESIGN LANGUAGE (KVLANG) --->
# This string contains the UI design. It's cleaner and more maintainable
# than defining the UI entirely in Python.
KV_STRING = """
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import Clock kivy.clock.Clock

#<--- THEME DEFINITION --- >
# Define theme colors and fonts that can be reused throughout the app
[Variables]:
    # Colors
    &theme_primary_bg: get_color_from_hex('#121212')
    &theme_secondary_bg: get_color_from_hex('#1E1E1E')
    &theme_card_bg: get_color_from_hex('#2A2A2A')
    &theme_accent: get_color_from_hex('#E53935') # Vibrant Red
    &theme_accent_light: get_color_from_hex('#EF5350')
    &theme_text_primary: get_color_from_hex('#FFFFFF')
    &theme_text_secondary: get_color_from_hex('#B0B0B0')
    &theme_success: get_color_from_hex('#4CAF50')
    &theme_warning: get_color_from_hex('#FFC107')
    &theme_error: get_color_from_hex('#F44336')
    &theme_disabled: get_color_from_hex('#424242')

    # Metrics
    &radius_normal: [dp(16),]
    &radius_small: [dp(12),]
    &padding_normal: dp(20)
    &spacing_normal: dp(15)

#<--- CUSTOM WIDGETS --- >
<DownloadCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(90)
    padding: dp(10)
    spacing: root.spacing_normal
    canvas.before:
        Color:
            rgba: root.theme_card_bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: root.radius_small

    AsyncImage:
        source: root.thumbnail
        size_hint_x: None
        width: dp(100)
        radius: root.radius_small
        allow_stretch: True
        keep_ratio: False

    BoxLayout:
        orientation: 'vertical'
        spacing: dp(5)
        Label:
            text: root.title
            font_size: sp(15)
            color: root.theme_text_primary
            halign: 'left'
            valign: 'top'
            text_size: self.size
            shorten: True
            shorten_from: 'right'
            ellipsis_options: {'color':root.theme_accent,'underline':False}

        BoxLayout:
            size_hint_y: None
            height: dp(24)
            spacing: dp(8)
            ProgressBar:
                id: progress_bar
                max: 100
                value: root.progress
                size_hint_y: None
                height: dp(8)
                pos_hint: {'center_y': 0.5}
                canvas:
                    Clear
                    # Background
                    Color:
                        rgba: root.theme_secondary_bg
                    RoundedRectangle:
                        pos: self.x, self.center_y - dp(4)
                        size: self.width, dp(8)
                        radius: [dp(4),]
                    # Progress
                    Color:
                        rgba: root.theme_success if root.progress == 100 else root.theme_accent
                    RoundedRectangle:
                        pos: self.x, self.center_y - dp(4)
                        size: self.width * (self.value / self.max), dp(8)
                        radius: [dp(4),]

            Label:
                text: f"{int(root.progress)}%"
                font_size: sp(12)
                color: root.theme_text_secondary
                size_hint_x: None
                width: dp(40)

    BoxLayout:
        size_hint_x: None
        width: dp(80)
        orientation: 'vertical'
        padding: [0, dp(5), 0, dp(5)]

        Label:
            text: root.status.capitalize()
            font_size: sp(12)
            color: (root.theme_success if root.status == 'completed' else \
                    root.theme_warning if root.status == 'downloading' else \
                    root.theme_error if root.status == 'error' else \
                    root.theme_text_secondary)
            bold: True
        
        Label:
            text: root.speed
            font_size: sp(11)
            color: root.theme_text_secondary


<NavButton@ButtonBehavior+BoxLayout>:
    orientation: 'vertical'
    group: 'nav'
    screen_name: ''
    icon: ''
    label: ''
    is_active: False
    
    on_press:
        app.switch_screen(self.screen_name)

    Label:
        id: icon
        text: self.parent.icon
        font_name: 'fonts/MaterialIcons-Regular.ttf' # Using Material Design Icons
        font_size: sp(26)
        color: root.theme_accent if self.parent.is_active else root.theme_text_secondary
    Label:
        id: label
        text: self.parent.label
        font_size: sp(10)
        color: root.theme_accent if self.parent.is_active else root.theme_text_secondary


<ProButton@ButtonBehavior+FloatLayout>:
    text: ''
    font_size: sp(16)
    bg_color: root.theme_accent
    ripple_color: root.theme_accent_light
    radius: root.radius_normal
    on_press: self.do_ripple_effect(args[0])

    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius
    Label:
        text: root.text
        font_size: root.font_size
        bold: True
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

    def do_ripple_effect(self, touch):
        ripple = FloatLayout()
        with ripple.canvas:
            Color(rgba=self.ripple_color + [0.5])
            self.ripple_circle = Ellipse(pos=(touch.pos[0] - dp(5), touch.pos[1] - dp(5)), size=(dp(10), dp(10)))
        self.add_widget(ripple)
        anim = Animation(size=(self.width*2, self.width*2), pos=(self.x - self.width, self.y - self.width), t='out_quad', duration=0.5)
        anim.bind(on_complete=lambda *args: self.remove_widget(ripple))
        anim.start(self.ripple_circle)

#<--- MAIN APP LAYOUT --- >
FloatLayout:
    canvas.before:
        Color:
            rgba: root.theme_primary_bg
        Rectangle:
            pos: self.pos
            size: self.size

    # --- Header ---
    BoxLayout:
        id: header
        orientation: 'horizontal'
        size_hint: 1, 0.12
        pos_hint: {'top': 1}
        padding: [root.padding_normal, 0]
        canvas.before:
            Color:
                rgba: root.theme_secondary_bg
            Rectangle:
                pos: self.pos
                size: self.size
        
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: "TORRO"
                font_size: sp(32)
                bold: True
                color: root.theme_accent
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            Label:
                text: " Professional Video Downloader"
                font_size: sp(12)
                color: root.theme_text_secondary
                halign: 'left'
                valign: 'top'
                text_size: self.size

    # --- Screen Manager for different pages ---
    ScreenManager:
        id: screen_manager
        pos_hint: {'top': 0.88} # Below the header
        size_hint: 1, 0.78 # Above the navbar
        transition: Factory.FadeTransition(duration=0.2)

        Screen:
            name: 'home'
            BoxLayout:
                orientation: 'vertical'
                padding: root.padding_normal
                spacing: root.spacing_normal

                # URL Input Area
                BoxLayout:
                    size_hint_y: None
                    height: dp(55)
                    canvas.before:
                        Color:
                            rgba: root.theme_secondary_bg
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: root.radius_normal
                    TextInput:
                        id: url_input
                        hint_text: "Paste video URL here..."
                        background_color: [0,0,0,0]
                        foreground_color: root.theme_text_primary
                        cursor_color: root.theme_accent
                        font_size: sp(16)
                        padding: [dp(15), (self.height - self.font_size)/2]
                        multiline: False
                    Button:
                        text: 'DOWNLOAD'
                        size_hint_x: None
                        width: dp(120)
                        background_color: [0,0,0,0]
                        on_press: app.start_download_from_input(url_input.text)
                        canvas.before:
                            Color:
                                rgba: root.theme_accent
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: root.radius_normal

                # Active Downloads Preview
                Label:
                    text: "Active Downloads"
                    font_size: sp(20)
                    bold: True
                    size_hint_y: None
                    height: dp(30)
                    halign: 'left'
                    text_size: self.size
                    color: root.theme_text_primary

                RecycleView:
                    id: home_rv
                    data: app.get_active_downloads()
                    viewclass: 'DownloadCard'
                    RecycleBoxLayout:
                        default_size: None, dp(90)
                        default_size_hint: 1, None
                        size_hint_y: None
                        height: self.minimum_height
                        orientation: 'vertical'
                        spacing: root.spacing_normal
        
        Screen:
            name: 'downloads'
            BoxLayout:
                orientation: 'vertical'
                padding: root.padding_normal
                spacing: root.spacing_normal

                Label:
                    text: "Download History"
                    font_size: sp(20)
                    bold: True
                    size_hint_y: None
                    height: dp(30)
                    halign: 'left'
                    text_size: self.size
                    color: root.theme_text_primary

                RecycleView:
                    id: downloads_rv
                    data: app.downloads_data
                    viewclass: 'DownloadCard'
                    RecycleBoxLayout:
                        default_size: None, dp(90)
                        default_size_hint: 1, None
                        size_hint_y: None
                        height: self.minimum_height
                        orientation: 'vertical'
                        spacing: root.spacing_normal
        
        Screen:
            name: 'settings'
            BoxLayout:
                padding: root.padding_normal
                Label:
                    text: "Settings Screen - Coming Soon!"
                    font_size: sp(20)
                    color: root.theme_text_secondary

    # --- Bottom Navigation ---
    BoxLayout:
        id: bottom_nav
        size_hint: 1, 0.1
        pos_hint: {'y': 0}
        padding: [dp(10), 0]
        canvas.before:
            Color:
                rgba: root.theme_secondary_bg
            Rectangle:
                pos: self.pos
                size: self.size
        
        NavButton:
            screen_name: 'home'
            icon: '\\ue88a' # Home icon
            label: 'Home'
            is_active: app.current_screen == 'home'
        NavButton:
            screen_name: 'downloads'
            icon: '\\ue2c4' # Download icon
            label: 'Downloads'
            is_active: app.current_screen == 'downloads'
        NavButton:
            screen_name: 'settings'
            icon: '\\ue8b8' # Settings icon
            label: 'Settings'
            is_active: app.current_screen == 'settings'

"""

#<--- PYTHON LOGIC --->

class DownloadManager:
    """ Manages the yt-dlp download process in a separate thread. """
    def __init__(self, app_instance):
        self.app = app_instance
        self.download_folder = "Torro_Downloads"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def run_download(self, download_item):
        """ The function that will run in a separate thread. """
        try:
            ydl_opts = {
                'outtmpl': os.path.join(self.download_folder, '%(title)s [%(height)sp].%(ext)s'),
                'progress_hooks': [partial(self.progress_hook, download_item['id'])],
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'noplaylist': True,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First, extract info to get title and thumbnail
                info = ydl.extract_info(download_item['url'], download=False)
                title = info.get('title', 'Unknown Title')
                thumbnail = info.get('thumbnail', '')
                
                # Schedule UI update on main thread
                Clock.schedule_once(lambda dt: self.app.update_download_info(download_item['id'], title, thumbnail))
                
                # Now, start the actual download
                ydl.download([download_item['url']])

        except Exception as e:
            error_message = str(e).split(':')[-1].strip()
            Clock.schedule_once(lambda dt: self.app.update_download_status(download_item['id'], 'error', error_message))
            print(f"Error downloading {download_item['url']}: {e}")

    def progress_hook(self, download_id, d):
        """ yt-dlp hook to capture download progress. """
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                progress = (d['downloaded_bytes'] / total_bytes) * 100
                speed = d.get('speed')
                speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else ""
                
                # Schedule UI update on main thread to avoid crashes
                Clock.schedule_once(lambda dt: self.app.update_download_progress(download_id, progress, speed_str))
        
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.app.update_download_status(download_id, 'completed', 'Finished'))

class DownloadCard(RecycleDataViewBehavior, BoxLayout):
    """ The View Class for an item in the RecycleView. """
    index = None
    title = StringProperty("Fetching title...")
    status = StringProperty("queued")
    progress = NumericProperty(0)
    thumbnail = StringProperty('https://via.placeholder.com/150.png?text=TORRO')
    speed = StringProperty("")
    
    # Re-use theme variables from KV
    theme_card_bg = ListProperty(get_color_from_hex('#2A2A2A'))
    theme_secondary_bg = ListProperty(get_color_from_hex('#1E1E1E'))
    theme_text_primary = ListProperty(get_color_from_hex('#FFFFFF'))
    theme_text_secondary = ListProperty(get_color_from_hex('#B0B0B0'))
    theme_accent = ListProperty(get_color_from_hex('#E53935'))
    theme_success = ListProperty(get_color_from_hex('#4CAF50'))
    theme_warning = ListProperty(get_color_from_hex('#FFC107'))
    theme_error = ListProperty(get_color_from_hex('#F44336'))
    radius_small = ListProperty([dp(12),])
    spacing_normal = NumericProperty(dp(15))

    def refresh_view_attrs(self, rv, index, data):
        """ Catches the ViewHolder behavior and re-assigns attributes. """
        self.index = index
        for key, value in data.items():
            setattr(self, key, value)
        return super(DownloadCard, self).refresh_view_attrs(rv, index, data)

class TorroApp(App):
    # --- App Properties ---
    current_screen = StringProperty("home")
    downloads_data = ListProperty([]) # This will drive the RecycleView

    def build(self):
        self.title = "TORRO Video Downloader"
        self.download_manager = DownloadManager(self)
        # Load the UI from the KV_STRING
        return Builder.load_string(KV_STRING)

    def switch_screen(self, screen_name):
        self.root.ids.screen_manager.current = screen_name
        self.current_screen = screen_name

    def start_download_from_input(self, url):
        url = url.strip()
        if not url:
            # Simple feedback, could be a toast notification
            print("URL cannot be empty")
            return
        
        if not YT_DLP_AVAILABLE:
            print("Cannot start download, yt-dlp is not available.")
            return

        download_id = str(len(self.downloads_data))
        new_download = {
            'id': download_id,
            'url': url,
            'title': "Fetching details...",
            'thumbnail': 'https://via.placeholder.com/150.png?text=QUEUED',
            'status': 'queued',
            'progress': 0,
            'speed': ''
        }
        
        # Prepend to list so it appears at the top
        self.downloads_data.insert(0, new_download)
        
        # Clear the input field
        self.root.ids.url_input.text = ""
        
        # Start download in a background thread
        threading.Thread(target=self.download_manager.run_download, args=(new_download,), daemon=True).start()

    # --- Methods to update the UI from other threads ---
    def find_download_index(self, download_id):
        for i, item in enumerate(self.downloads_data):
            if item['id'] == download_id:
                return i
        return -1

    def update_download_info(self, download_id, title, thumbnail):
        index = self.find_download_index(download_id)
        if index != -1:
            self.downloads_data[index]['title'] = title
            self.downloads_data[index]['thumbnail'] = thumbnail
            self.downloads_data[index]['status'] = 'downloading'
            self.refresh_recycle_views()

    def update_download_progress(self, download_id, progress, speed):
        index = self.find_download_index(download_id)
        if index != -1:
            self.downloads_data[index]['progress'] = progress
            self.downloads_data[index]['speed'] = speed
            # No full refresh needed, Kivy properties handle this
            self.root.ids.home_rv.refresh_from_data()
            self.root.ids.downloads_rv.refresh_from_data()


    def update_download_status(self, download_id, status, message=""):
        index = self.find_download_index(download_id)
        if index != -1:
            self.downloads_data[index]['status'] = status
            if status == 'completed':
                self.downloads_data[index]['progress'] = 100
                self.downloads_data[index]['speed'] = '✅'
            elif status == 'error':
                 self.downloads_data[index]['speed'] = '❌'
                 self.downloads_data[index]['title'] = f"Error: {message}"
            self.refresh_recycle_views()

    def get_active_downloads(self):
        """ Filters downloads for the home screen view. """
        return [d for d in self.downloads_data if d['status'] in ['downloading', 'queued', 'error']]

    def refresh_recycle_views(self):
        """ Force refresh data in both RecycleViews. """
        self.root.ids.home_rv.data = self.get_active_downloads()
        self.root.ids.downloads_rv.data = self.downloads_data
        self.root.ids.home_rv.refresh_from_data()
        self.root.ids.downloads_rv.refresh_from_data()

if __name__ == '__main__':
    TorroApp().run()
