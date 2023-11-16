import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Adw
from whakarere.widgets.main_menu import MainMenuButtonWidget
from whakarere.widgets.titlebar import WindowTitlebarWidget
import threading, time

class QrManagerPage(Adw.NavigationPage):
    def __init__(self, app_manager):
        super().__init__()
        self.set_title("Whakarere")
        self.app_manager = app_manager

        # Create TitleBar Widget
        self.window_titlebar_widget = WindowTitlebarWidget()
        self.window_titlebar_widget.set_title("Whakarere")
        self.window_titlebar_widget.set_subtitle(f"Qr Code for Session:")
        self.set_can_pop(True)

        # Create MainMenu Button Widget
        self.button_settings_menu = MainMenuButtonWidget()

        # Create QR Code Image
        self.qr_code_texture = self.app_manager.qrcode_manager.get_qr_code_texture(self.app_manager.whatsapp_manager.get_qr_code_data(self.app_manager.session_manager.get_current_session()))
        self.qr_code = Gtk.Picture()
        self.qr_code.set_paintable(self.qr_code_texture)
        
        # Create ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_width(300)
        scrolled_window.set_min_content_height(300)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.qr_code) 
        
        self.qr_code_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.qr_code_box.set_halign(Gtk.Align.CENTER)
        self.qr_code_box.set_valign(Gtk.Align.CENTER)
        self.qr_code_box.set_margin_top(10)
        self.qr_code_box.set_margin_bottom(10)
        self.qr_code_box.set_margin_start(10)
        self.qr_code_box.set_margin_end(10)
        self.qr_code_box.set_hexpand(True)
        self.qr_code_box.set_vexpand(True)  
        self.qr_code_box.append(scrolled_window)

        # Create HeaderBar
        self.page_headerbar = Adw.HeaderBar()
        self.page_headerbar.set_title_widget(self.window_titlebar_widget)
        self.page_headerbar.pack_end(self.button_settings_menu)
        
        self.page_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.page_content.append(self.page_headerbar)
        self.page_content.append(self.qr_code_box)

        self.set_child(self.page_content)

        self.check_session_status_thread = threading.Thread(target=self.check_session_status_thread, args=(self.app_manager.session_manager.get_current_session(),))
        self.check_session_status_thread.start()

    def check_session_status_thread(self, session_id):
        while not self.app_manager.whatsapp_manager.check_session_status(session_id):
            time.sleep(2)
        self.app_manager.main_window.navigation_view.pop()
        self.app_manager.main_window.session_manager_page.refresh_listview()
        time.sleep(5)