import datetime
import os, sys, time
import threading

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive"
    except NameError:
        application_path = os.getcwd()
        running_mode = 'Interactive'

logger_name = f'app.log'
logger_dir = os.path.join(application_path, "logs")

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'system')

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivy.properties import StringProperty
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.app import MDApp
import cv2, numpy as np
import configparser, hashlib, mysql.connector, paramiko
from pymodbus.client import ModbusTcpClient
from fpdf import FPDF
from escpos.printer import Serial

colors = {  "Red"   : {"A200": "#FF2A2A","A500": "#FF8080","A700": "#FFD5D5",},
            "Gray"  : {"200": "#CCCCCC","500": "#ECECEC","700": "#F9F9F9",},
            "Blue"  : {"200": "#4471C4","500": "#5885D8","700": "#6C99EC",},
            "Green" : {"200": "#2CA02C","500": "#2DB97F", "700": "#D5FFD5",},
            "Yellow": {"200": "#ffD42A","500": "#ffE680","700": "#fff6D5",},
            "Light" : {"StatusBar": "E0E0E0","AppBar": "#202020","Background": "#EEEEEE","CardsDialogs": "#FFFFFF","FlatButtonDown": "#CCCCCC","Text": "#000000",},
            "Dark"  : {"StatusBar": "101010","AppBar": "#E0E0E0","Background": "#111111","CardsDialogs": "#222222","FlatButtonDown": "#DDDDDD","Text": "#FFFFFF",},
        }

config_name = 'config.ini'
config_full_path = os.path.join(application_path, config_name)
config = configparser.ConfigParser()
config.read(config_full_path)

## App Setting
APP_TITLE = config['app']['APP_TITLE']
APP_SUBTITLE = config['app']['APP_SUBTITLE']
IMG_LOGO_PEMKAB = config['app']['IMG_LOGO_PEMKAB']
IMG_LOGO_DISHUB = config['app']['IMG_LOGO_DISHUB']
LB_PEMKAB = config['app']['LB_PEMKAB']
LB_DISHUB = config['app']['LB_DISHUB']
LB_UNIT = config['app']['LB_UNIT']
LB_UNIT_ADDRESS = config['app']['LB_UNIT_ADDRESS']

## SQL Setting
DB_HOST = "194.31.53.37"
DB_USER = "Pndujikir2022!"
DB_PASSWORD = "@Kirpnd2022!"

DB_NAME = "pkbpandeglang"
TB_DATA = "tb_cekident"
TB_USER = "users"
TB_MERK = "merk"
TB_BAHAN_BAKAR = "bahanbakar"
TB_WARNA = "warna"
TB_DAFTAR_BERKALA = "temp_pendaftaranberkala"
TB_DAFTAR_BARU = "temp_pendaftaranbr"
TB_DATA_MASTER = "identkendaraan"
TB_DATA_IMAGE = "image_kendaraan"
TB_DATA_KENDARAAN = "tb_jeniskendaraan"
TB_KOMPONEN_UJI = "komponen_uji"
TB_SUBKOMPONEN_UJI = "subkomponen_uji"
TB_KOMENTAR_UJI = "komentar_uji"
TB_UJI = "uji"
TB_UJI_DETAIL = "uji_detail"

## System Setting
RTSP_USER = "admin"
RTSP_PASS = "TRBIntegrated25"

RTSP_IP_DISPLAY_CAM1 = config['setting']['RTSP_IP_DISPLAY_CAM1']
RTSP_IP_DISPLAY_CAM2 = config['setting']['RTSP_IP_DISPLAY_CAM2']
RTSP_IP_DISPLAY_CAM3 = config['setting']['RTSP_IP_DISPLAY_CAM3']
RTSP_IP_DISPLAY_CAM4 = config['setting']['RTSP_IP_DISPLAY_CAM4']
RTSP_IP_PIT_CAM1 = config['setting']['RTSP_IP_PIT_CAM1']
RTSP_IP_PIT_CAM2 = config['setting']['RTSP_IP_PIT_CAM2']
RTSP_IP_PIT_CAM3 = config['setting']['RTSP_IP_PIT_CAM3']
RTSP_IP_PIT_CAM4 = config['setting']['RTSP_IP_PIT_CAM4']

FTP_HOST = "194.31.53.37"
FTP_USER = "root"
FTP_PASS = "@D15HUBp2022!"

MODBUS_IP_PLC = config['setting']['MODBUS_IP_PLC']
MODBUS_CLIENT = ModbusTcpClient(MODBUS_IP_PLC)

class ScreenHome(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenHome, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def on_enter(self):
        Clock.schedule_interval(self.regular_update_carousel, 3)

    def on_leave(self):
        Clock.unschedule(self.regular_update_carousel)

    def regular_update_carousel(self, dt):
        try:
            self.ids.carousel.index += 1
            
        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tampilan Carousel'
            toast(toast_msg)                
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)  
            Logger.error(f"{self.name}: {toast_msg}, {e}")    

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Login'
            toast(toast_msg)  
            Logger.error(f"{self.name}: {toast_msg}, {e}")   

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

class ScreenLogin(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenLogin, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE           
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def exec_cancel(self):
        try:
            self.ids.tx_username.text = ""
            self.ids.tx_password.text = ""    

        except Exception as e:
            toast_msg = f'error Login: {e}'
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_login(self):
        global mydb, db_users
        global dt_id_user, dt_user, dt_foto_user

        screen_main = self.screen_manager.get_screen('screen_main')

        try:
            screen_main.exec_reload_database()
            input_username = self.ids.tx_username.text
            input_password = self.ids.tx_password.text        
            # Adding salt at the last of the password
            dataBase_password = input_password
            # Encoding the password
            hashed_password = hashlib.md5(dataBase_password.encode())

            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT id_user, nama, username, password, image FROM {TB_USER} WHERE username = '{input_username}' and password = '{hashed_password.hexdigest()}'")
            myresult = mycursor.fetchone()
            db_users = np.array(myresult).T
            
            if myresult is None:
                toast('Gagal Masuk, Nama Pengguna atau Password Salah')
            else:
                toast_msg = f'Berhasil Masuk, Selamat Datang {myresult[1]}'
                toast(toast_msg)
                dt_id_user = myresult[0]
                dt_user = myresult[1]
                dt_foto_user = myresult[4]
                self.ids.tx_username.text = ""
                self.ids.tx_password.text = "" 
                self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal masuk, silahkan isi nama user dan password yang sesuai'
            toast(toast_msg)  
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

class ScreenMain(MDScreen):   
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        global flag_conn_stat, flag_gate, dt_selected_camera
        global dt_user, dt_foto_user, dt_id_pendaftaran, dt_no_antri, dt_no_pol, dt_no_uji, dt_sts_uji, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna, dt_chasis, dt_no_mesin
        global dt_visual_flag, dt_id_user, dt_verified_data, dt_verified_payment
        global dt_dash_antri, dt_dash_belum_uji, dt_dash_sudah_uji
        global dt_temp_nama, dt_temp_alamat, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji
        global dt_temp_id_merk, dt_temp_type, dt_temp_jenis_kendaraan, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_bhn_bkr, dt_temp_jbb
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        flag_conn_stat = flag_gate = False
        dt_user = dt_foto_user = dt_no_antri = dt_no_pol = dt_no_uji = dt_sts_uji = dt_nama = ""
        dt_merk = dt_type = dt_jns_kend = dt_jbb = dt_bhn_bkr = dt_warna = dt_chasis = dt_no_mesin = ""
        dt_visual_flag = dt_verified_data = dt_verified_payment = 0
        dt_id_pendaftaran = 0
        dt_id_user = 1
        dt_dash_antri = dt_dash_belum_uji = dt_dash_sudah_uji = 0
        dt_selected_camera = 0

        # rtsp_url_cam1 = 'rtsp://admin:TRBintegrated202@192.168.70.64:554/Streaming/Channels/101'
        rtsp_url_cam1 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM1}:554/Streaming/Channels/101'
        rtsp_url_cam2 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM2}:554/Streaming/Channels/101'
        rtsp_url_cam3 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM3}:554/Streaming/Channels/101'
        rtsp_url_cam4 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM4}:554/Streaming/Channels/101'

        rtsp_url_pit1 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM1}:554/Streaming/Channels/101'
        rtsp_url_pit2 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM2}:554/Streaming/Channels/101'
        rtsp_url_pit3 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM3}:554/Streaming/Channels/101'
        rtsp_url_pit4 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM4}:554/Streaming/Channels/101'

        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE          
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

        Clock.schedule_interval(self.regular_update_display, 1)
        Clock.schedule_interval(self.regular_update_connection, 10)

    def on_enter(self):
        self.exec_reload_database()
        self.exec_reload_table()
                
    def regular_update_display(self, dt):
        global flag_conn_stat, db_merk, db_bahan_bakar, db_warna
        global dt_user, dt_id_pendaftaran, dt_no_antri, dt_no_pol, dt_no_uji, dt_nama, dt_jns_kend
        global dt_chasis, dt_merk, dt_type, dt_no_mesin
        global dt_visual_flag, dt_id_user, dt_foto_user, dt_verified_data, dt_verified_payment
        global dt_dash_antri, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            screen_home = self.screen_manager.get_screen('screen_home')
            screen_login = self.screen_manager.get_screen('screen_login')
            screen_menu = self.screen_manager.get_screen('screen_menu')
            screen_calibration = self.screen_manager.get_screen('screen_calibration')
            screen_add_data = self.screen_manager.get_screen('screen_add_data')
            screen_add_queue = self.screen_manager.get_screen('screen_add_queue')
            
            screen_inspect_id = self.screen_manager.get_screen('screen_inspect_id')
            screen_inspect_dimension = self.screen_manager.get_screen('screen_inspect_dimension')
            screen_inspect_visual = self.screen_manager.get_screen('screen_inspect_visual')
            screen_inspect_visual2 = self.screen_manager.get_screen('screen_inspect_visual2')
            screen_inspect_pit = self.screen_manager.get_screen('screen_inspect_pit')
            screen_realtime_cctv = self.screen_manager.get_screen('screen_realtime_cctv')
            screen_realtime_pit = self.screen_manager.get_screen('screen_realtime_pit')

            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_home.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_home.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_login.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_login.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_menu.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_menu.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_calibration.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_calibration.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_add_data.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_add_data.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_add_queue.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_add_queue.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            screen_inspect_id.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_id.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_dimension.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_dimension.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_visual.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_visual.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_visual2.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_visual2.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))            
            screen_inspect_pit.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_pit.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_realtime_cctv.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_realtime_cctv.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_realtime_pit.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_realtime_pit.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_dash_antri.text = str(dt_dash_antri)
            self.ids.lb_dash_belum_uji.text = str(dt_dash_belum_uji)
            self.ids.lb_dash_sudah_uji.text = str(dt_dash_sudah_uji)

            screen_menu.ids.bt_verify_data.disabled = True if dt_verified_data == 1 else False
            # if dt_verified_payment == 1 or dt_verified_data == 0:
            #     screen_menu.ids.bt_verify_payment.disabled = True
            # elif dt_verified_payment == 0 and dt_verified_data == 1:
            #     screen_menu.ids.bt_verify_payment.disabled = False

            if(not flag_conn_stat):
                self.ids.lb_comm.color = colors['Red']['A200']
                self.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_home.ids.lb_comm.color = colors['Red']['A200']
                screen_home.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_login.ids.lb_comm.color = colors['Red']['A200']
                screen_login.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_menu.ids.lb_comm.color = colors['Red']['A200']
                screen_menu.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_calibration.ids.lb_comm.color = colors['Red']['A200']
                screen_calibration.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_add_data.ids.lb_comm.color = colors['Red']['A200']
                screen_add_data.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_add_queue.ids.lb_comm.color = colors['Red']['A200']
                screen_add_queue.ids.lb_comm.text = 'PLC Tidak Terhubung'

            else:
                self.ids.lb_comm.color = colors['Blue']['200']
                self.ids.lb_comm.text = 'PLC Terhubung'
                screen_home.ids.lb_comm.color = colors['Blue']['200']
                screen_home.ids.lb_comm.text = 'PLC Terhubung'
                screen_login.ids.lb_comm.color = colors['Blue']['200']
                screen_login.ids.lb_comm.text = 'PLC Terhubung'
                screen_menu.ids.lb_comm.color = colors['Blue']['200']
                screen_menu.ids.lb_comm.text = 'PLC Terhubung'
                screen_calibration.ids.lb_comm.color = colors['Blue']['200']
                screen_calibration.ids.lb_comm.text = 'PLC Terhubung'
                screen_add_data.ids.lb_comm.color = colors['Blue']['200']
                screen_add_data.ids.lb_comm.text = 'PLC Terhubung'
                screen_add_queue.ids.lb_comm.color = colors['Blue']['200']
                screen_add_queue.ids.lb_comm.text = 'PLC Terhubung'
            
            self.ids.bt_calibrate.disabled = False if dt_user != '' else True
            #self.ids.bt_add_data.disabled = False if dt_user != '' else True
            #elf.ids.bt_add_queue.disabled = False if dt_user != '' else True
            self.ids.bt_logout.disabled = False if dt_user != '' else True

            self.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_home.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_login.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_menu.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_calibration.ids.lb_operator.text = f'Login Sebagai: \n{dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_add_data.ids.lb_operator.text = f'Login Sebagai: \n{dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_add_queue.ids.lb_operator.text = f'Login Sebagai: \n{dt_user}' if dt_user != '' else 'Silahkan Login'

            screen_inspect_id.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_dimension.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_visual.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_visual2.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_pit.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_realtime_cctv.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_realtime_pit.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'

            if dt_user != '':
                self.ids.img_user.source = f'https://{FTP_HOST}/system/storage/app/foto_user/{dt_foto_user}'
                screen_home.ids.img_user.source = f'https://{FTP_HOST}/system/storage/app/foto_user/{dt_foto_user}'
                screen_login.ids.img_user.source = f'https://{FTP_HOST}/system/storage/app/foto_user/{dt_foto_user}'
            else:
                self.ids.img_user.source = 'assets/images/icon-login.png'
                screen_home.ids.img_user.source = 'assets/images/icon-login.png'
                screen_login.ids.img_user.source = 'assets/images/icon-login.png'

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tampilan'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def regular_update_connection(self, dt):
        global flag_conn_stat

        try:
            MODBUS_CLIENT.connect()
            flag_conn_stat = MODBUS_CLIENT.connected
            MODBUS_CLIENT.close()
            
        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Koneksi'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  
            flag_conn_stat = False

    def unsigned_to_signed(self, val):
        if val >= 32768:
            return val - 65536
        return val

    def regular_get_data(self, dt):
        pass

    def exec_reload_database(self):
        global mydb
        try:
            mydb = mysql.connector.connect(host = DB_HOST,user = DB_USER,password = DB_PASSWORD,database = DB_NAME)
        except Exception as e:
            toast_msg = f'Gagal Menginisiasi Database'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_table(self):
        global mydb, db_antrian
        global db_merk, db_bahan_bakar, db_warna
        global dt_dash_antri, dt_dash_belum_uji, dt_dash_sudah_uji
        global window_size_x, window_size_y

        try:
            cursor = mydb.cursor()
            today = str(time.strftime("%Y-%m-%d", time.localtime()))
            delete_query = f"DELETE FROM {TB_DATA} WHERE DATE(tgl_daftar) != %s"
            cursor.execute(delete_query, (today,))
            mydb.commit()
            toast_msg = f'Berhasil menghapus data kemarin'
        except Exception as e:
            toast_msg = f'Gagal menghapus data kemarin'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

        try:
            cursor = mydb.cursor()
            cursor.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
            result_tb_merk = cursor.fetchall()
            db_merk = np.array(result_tb_merk)

            cursor.execute(f"SELECT ID, DESCRIPTION FROM {TB_BAHAN_BAKAR}")
            result_tb_bahan_bakar = cursor.fetchall()
            db_bahan_bakar = np.array(result_tb_bahan_bakar)

            cursor.execute(f"SELECT id_warna, nama FROM {TB_WARNA}")
            result_tb_warna = cursor.fetchall()
            db_warna = np.array(result_tb_warna)

            cursor.execute(f"SELECT COUNT(*) FROM {TB_DATA}")
            result = cursor.fetchone()  # Returns tuple like (123,)

            if result is None:
                dt_dash_antri = 0
                toast('Data Tabel cekident kosong')
            else:
                dt_dash_antri = result[0]

                cursor.execute(f"SELECT noantrian, nopol, nouji, statusuji, merk, type, idjeniskendaraan, jbb, berat_kosong, bahan_bakar, warna, check_flag FROM {TB_DATA} WHERE check_flag = 0")
                result_tb_antrian = cursor.fetchall()
                db_antrian = np.array(result_tb_antrian).T

                db_pendaftaran = np.array(result_tb_antrian)
                dt_dash_belum_uji = db_pendaftaran[:,0].size
                dt_dash_sudah_uji = dt_dash_antri - dt_dash_belum_uji
            
            cursor.close()

        except Exception as e:
            toast_msg = f'Gagal mengambil data antrian harian'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

        try:            
            layout_list = self.ids.layout_list
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal menghapus widget tabel'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")   
        
        try:           
            layout_list = self.ids.layout_list
            for i in range(db_antrian[0,:].size):
                layout_list.add_widget(
                    MDCard(
                        MDLabel(text=f"{db_antrian[0, i]}", size_hint_x= 0.05),
                        MDLabel(text=f"{db_antrian[1, i]}", size_hint_x= 0.07),
                        MDLabel(text=f"{db_antrian[2, i]}", size_hint_x= 0.08),
                        MDLabel(text='Berkala' if db_antrian[3, i] == 'B' else 'Uji Ulang' if (db_antrian[3, i]) == 'U' else 'Baru' if (db_antrian[3, i]) == 'BR' else 'Numpang Uji' if (db_antrian[3, i]) == 'NB' else 'Mutasi', size_hint_x= 0.07),
                        MDLabel(text='-' if db_antrian[4, i] == None else f"{db_merk[np.where(db_merk == db_antrian[4, i])[0][0],1]}" , size_hint_x= 0.08),
                        MDLabel(text=f"{db_antrian[5, i]}", size_hint_x= 0.07),
                        MDLabel(text=f"{db_antrian[6, i]}", size_hint_x= 0.15),
                        MDLabel(text=f"{db_antrian[7, i]}", size_hint_x= 0.05),
                        MDLabel(text=f"{db_antrian[8, i]}", size_hint_x= 0.05),
                        MDLabel(text='-' if db_antrian[9, i] == None else f"{db_bahan_bakar[np.where(db_bahan_bakar == db_antrian[9, i])[0][0],1]}" , size_hint_x= 0.08),
                        MDLabel(text='-' if db_antrian[10, i] == None else f"{db_warna[np.where(db_warna == db_antrian[10, i])[0][0],1]}" , size_hint_x= 0.11),
                        MDLabel(text='Lulus' if (int(db_antrian[11, i]) == 2) else 'Tidak Lulus' if (int(db_antrian[11, i]) == 1) else 'Belum Uji', size_hint_x= 0.08),

                        ripple_behavior = True,
                        on_press = self.on_antrian_row_press,
                        padding = 20,
                        id=f"card_antrian{i}",
                        size_hint_y=None,
                        height=dp(int(60 * 800 / window_size_y)),
                        )
                    )
        except Exception as e:
            toast_msg = f'Gagal reload tabel'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_antrian_row_press(self, instance):
        global mydb, db_antrian, db_merk, db_bahan_bakar, db_warna
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_sts_uji
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_brt_ksg, dt_bhn_bkr, dt_warna, dt_visual_flag
        global dt_id_user, dt_foto_user

        try:
            row = int(str(instance.id).replace("card_antrian",""))
            dt_no_antri             = db_antrian[0, row]
            dt_no_pol               = db_antrian[1, row]
            dt_no_uji               = db_antrian[2, row]
            dt_sts_uji              = db_antrian[3, row]
            dt_merk                 = db_antrian[4, row]
            dt_type                 = db_antrian[5, row]
            dt_jns_kend             = db_antrian[6, row]
            dt_jbb                  = db_antrian[7, row]
            dt_brt_ksg              = db_antrian[8, row]
            dt_bhn_bkr              = db_antrian[9, row]
            dt_warna                = db_antrian[10, row]
            dt_visual_flag          = db_antrian[11, row]

            screen_add_queue = self.screen_manager.get_screen('screen_add_queue')
            screen_add_queue.exec_fetch_master_data(dt_no_pol, dt_no_uji)

            self.exec_navigate_menu()

        except Exception as e:
            toast_msg = f'Gagal mengeksekusi perintah dari baris tabel'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def check_temp_data(self):
        global mydb, db_antrian, db_merk, db_bahan_bakar, db_warna
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama, dt_sts_uji
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global dt_visual_flag, dt_id_user, dt_foto_user, dt_verified_data, dt_verified_payment

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT NOANTRIAN, NOUJI, NOPOL, STS_SPP FROM {TB_DAFTAR_BERKALA} WHERE NOANTRIAN = '{dt_no_antri}' ")
        myresult = mycursor.fetchone()
        if myresult is None:
            toast_msg = f'Belum ada data untuk No. Antrian {dt_no_antri}, No. Uji {dt_no_uji}, Silahkan Verifikasi terlebih dahulu'
            toast(toast_msg)
            dt_verified_data = 0
            dt_verified_payment = 0
        else:
            toast_msg = f'Sudah ada data untuk No. Antrian {dt_no_antri}, No. Uji {dt_no_uji}, Silahkan lanjutkan pengujian'
            toast(toast_msg)
            dt_verified_data = 1
            dt_verified_payment = int(myresult[3]) if myresult[3] is not None else 0

    def exec_add_queue(self):
        try:
            self.screen_manager.current = 'screen_add_queue'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Tambah Inspeksi Baru'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
            
    def exec_logout(self):
        global dt_user

        dt_user = ""
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Beranda'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast_msg = f"Anda sudah login sebagai {dt_user}"
                toast(toast_msg)
                Logger.info(f"{self.name}: {toast_msg}")

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_menu(self):
        global dt_visual_flag, dt_no_antri, dt_user

        if (dt_user != ''):
            self.check_temp_data()
            # if (int(dt_visual_flag) == 0):
            if dt_visual_flag is None or int(dt_visual_flag) == 0: #dc
                self.screen_manager.current = 'screen_menu'
            else:
                toast_msg = f'No. Antrian {dt_no_antri} Sudah Tes'
                toast(toast_msg)
                Logger.info(f"{self.name}: {toast_msg}")
        else:
            toast_msg = f'Silahkan Login Untuk Melakukan Pengujian'
            toast(toast_msg)
            Logger.info(f"{self.name}: {toast_msg}")      

    def exec_navigate_calibration(self):
        global dt_user
        try:
            self.screen_manager.current = 'screen_calibration'

        except Exception as e:
            toast_msg = f'Error Navigate to Calibration Screen: {e}'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_add_data(self):
        global dt_user
        try:
            self.screen_manager.current = 'screen_add_data'

        except Exception as e:
            toast_msg = f'Error Navigate to Add Data Screen: {e}'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_add_queue(self):
        global dt_user
        try:
            self.screen_manager.current = 'screen_add_queue'

        except Exception as e:
            toast_msg = f'Error Navigate to Add Queue Screen: {e}'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

class ScreenCalibration(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenCalibration, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def on_enter(self):
        pass

    def on_leave(self):
        pass

    def exec_set_camera_front(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_DISPLAY_CAM1 = self.ids.tx_set_camera_front.text.strip()
            rtsp_url_cam1 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM1}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_front"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_set_camera_left(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_DISPLAY_CAM2 = self.ids.tx_set_camera_left.text.strip()
            rtsp_url_cam2 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM2}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_left"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_set_camera_right(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_DISPLAY_CAM3 = self.ids.tx_set_camera_right.text.strip()
            rtsp_url_cam3 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM3}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_right"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_set_camera_back(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_DISPLAY_CAM4 = self.ids.tx_set_camera_back.text.strip()
            rtsp_url_cam4 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_DISPLAY_CAM4}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_back"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def exec_set_camera_pit_front(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_PIT_CAM1 = self.ids.tx_set_camera_pit_front.text.strip()
            rtsp_url_pit1 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM1}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_pit_front"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_set_camera_pit_left(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_PIT_CAM2 = self.ids.tx_set_camera_pit_left.text.strip()
            rtsp_url_pit2 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM2}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_pit_left"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_set_camera_pit_right(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_PIT_CAM3 = self.ids.tx_set_camera_pit_right.text.strip()
            rtsp_url_pit3 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM3}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_pit_right"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_set_camera_pit_back(self):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4, rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4

        try:
            RTSP_IP_PIT_CAM4 = self.ids.tx_set_camera_pit_back.text.strip()
            rtsp_url_pit4 = f'rtsp://{RTSP_USER}:{RTSP_PASS}@{RTSP_IP_PIT_CAM4}:554/Streaming/Channels/101'

        except Exception as e:
            toast_msg = f"error set_camera_pit_back"
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

class ScreenAddData(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenAddData, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def exec_cancel(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat berpindah ke halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")  

    def on_enter(self):
        """Called when screen is entered — safe to initialize dropdowns here."""
        Clock.schedule_once(self.load_dropdowns, 0.1)  # Small delay to ensure UI is loaded

    def on_leave(self):
        """Clean up menus to avoid memory leaks or errors."""
        if hasattr(self, 'menu_merk') and self.menu_merk:
            self.menu_merk.dismiss()
            self.menu_merk = None
        if hasattr(self, 'menu_bahan_bakar') and self.menu_bahan_bakar:
            self.menu_bahan_bakar.dismiss()
            self.menu_bahan_bakar = None
        if hasattr(self, 'menu_warna') and self.menu_warna:
            self.menu_warna.dismiss()
            self.menu_warna = None

    def load_dropdowns(self, dt=None):
        """Initialize dropdown menus for Merk, Bahan Bakar, Warna."""
        try:
            # --- Merk Dropdown ---
            tb_merk = mydb.cursor()
            tb_merk.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
            result_tb_merk = tb_merk.fetchall()
            if result_tb_merk:
                self.merk_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": row[1],
                        "on_release": lambda x=row[1], id=row[0]: self.set_merk(x, id),
                    } for row in result_tb_merk
                ]
                self.menu_merk = MDDropdownMenu(
                    caller=self.ids.drop_merk,
                    items=self.merk_items,
                    width_mult=4,  # You can adjust this
                )
            else:
                self.menu_merk = None

            # --- Bahan Bakar Dropdown ---
            tb_bahan_bakar = mydb.cursor()
            tb_bahan_bakar.execute(f"SELECT ID, DESCRIPTION FROM {TB_BAHAN_BAKAR}")
            result_tb_bahan_bakar = tb_bahan_bakar.fetchall()
            if result_tb_bahan_bakar:
                self.bahan_bakar_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": row[1],
                        "on_release": lambda x=row[1], id=row[0]: self.set_bahan_bakar(x, id),
                    } for row in result_tb_bahan_bakar
                ]
                self.menu_bahan_bakar = MDDropdownMenu(
                    caller=self.ids.drop_bahan_bakar,
                    items=self.bahan_bakar_items,
                    width_mult=4,
                )
            else:
                self.menu_bahan_bakar = None

            # --- Warna Dropdown ---
            tb_warna = mydb.cursor()
            tb_warna.execute(f"SELECT id_warna, nama FROM {TB_WARNA}")
            result_tb_warna = tb_warna.fetchall()
            if result_tb_warna:
                self.warna_items = [
                    {
                        "viewclass": "OneLineListItem",
                        "text": row[1],
                        "on_release": lambda x=row[1], id=row[0]: self.set_warna(x, id),
                    } for row in result_tb_warna
                ]
                self.menu_warna = MDDropdownMenu(
                    caller=self.ids.drop_warna,
                    items=self.warna_items,
                    width_mult=4,
                )
            else:
                self.menu_warna = None

        except Exception as e:
            toast(f"Error loading dropdowns: {str(e)}")
            Logger.error(f"ScreenAddData: Failed to load dropdowns - {e}")

    # Set functions for dropdown selection
    def set_merk(self, text_item, id_item):
        self.ids.drop_merk.text = text_item
        self.ids.drop_merk.merk_id = id_item
        if self.menu_merk:
            self.menu_merk.dismiss()

    def set_bahan_bakar(self, text_item, id_item):
        self.ids.drop_bahan_bakar.text = text_item
        self.ids.drop_bahan_bakar.bahan_bakar_id = id_item
        if self.menu_bahan_bakar:
            self.menu_bahan_bakar.dismiss()

    def set_warna(self, text_item, id_item):
        self.ids.drop_warna.text = text_item
        self.ids.drop_warna.warna_id = id_item
        if self.menu_warna:
            self.menu_warna.dismiss()
        
    def exec_register(self):
        try:
            dt_temp_no_uji = self.ids.tx_nouji.text.strip()
            dt_temp_no_pol = self.ids.tx_nopol.text.strip()

            if not dt_temp_no_uji or not dt_temp_no_pol:
                toast("Nomor Uji dan Nomor Regristasi tidak boleh kosong!")
                return

            mycursor = mydb.cursor()

            check_nouji_sql = f"SELECT COUNT(*) FROM {TB_DATA_MASTER} WHERE NOUJI = %s"
            mycursor.execute(check_nouji_sql, (dt_temp_no_uji,))
            result_nouji = mycursor.fetchone()
            
            if result_nouji and result_nouji[0] > 0:
                toast("Nomor Uji ini sudah terdaftar!")
                Logger.warning(f"{self.name}: Upaya menambahkan duplikat NOUJI: {dt_temp_no_uji}")
                return 

            check_nopol_sql = f"SELECT COUNT(*) FROM {TB_DATA_MASTER} WHERE NOPOL = %s"
            mycursor.execute(check_nopol_sql, (dt_temp_no_pol,))
            result_nopol = mycursor.fetchone()

            if result_nopol and result_nopol[0] > 0:
                toast("Nomor Polisi ini sudah terdaftar!")
                Logger.warning(f"{self.name}: Upaya menambahkan duplikat NOPOL: {dt_temp_no_pol}")
                return 

            dt_temp_no_uji_new = self.ids.tx_nouji.text.strip()
            dt_temp_nama = self.ids.tx_nama.text.strip()
            dt_temp_alamat = self.ids.tx_alamat.text.strip()
            dt_temp_type = self.ids.tx_type.text.strip()
            dt_temp_jenis_kendaraan = self.ids.tx_jeniskendaraan.text.strip()
            dt_temp_jbb = self.ids.tx_jbb.text.strip()
            dt_temp_brt_ksg = self.ids.tx_beratkosong.text.strip()
            dt_temp_tgl_uji_terakhir = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))

            # self.ids.lb_temp_nama.text = f'{dt_temp_nama}'
            # self.ids.lb_temp_alamat.text = f'{dt_temp_alamat}'
            # self.ids.lb_temp_no_uji.text = f'{dt_temp_no_uji}'
            # self.ids.lb_temp_no_pol.text = f'{dt_temp_no_pol}'
            # self.ids.lb_temp_status_uji.text = 'Berkala' if dt_temp_status_uji == 'B' else 'Uji Ulang' if dt_temp_status_uji == 'U' else 'Baru' if dt_temp_status_uji == 'BR' else 'Numpang Uji' if dt_temp_status_uji == 'NB' else 'Mutasi'
            # self.ids.lb_temp_tgl_uji_terakhir.text = f'{dt_temp_tgl_uji_terakhir}'
            # self.ids.lb_temp_tgl_uji_habis.text = f'{dt_temp_tgl_uji_habis}'
            # self.ids.lb_temp_merk.text = '-' if dt_temp_id_merk == None else f"{db_merk[np.where(db_merk == dt_temp_id_merk)[0][0],1]}"
            # self.ids.lb_temp_type.text = f'{dt_temp_type}'
            # self.ids.lb_temp_jenis_kendaraan.text = f'{dt_temp_jenis_kendaraan}'
            # self.ids.lb_temp_warna.text = '-' if dt_temp_warna == None else f"{db_warna[np.where(db_warna == dt_temp_warna)[0][0],1]}"
            # self.ids.lb_temp_chasis.text = f'{dt_temp_chasis}'
            # self.ids.lb_temp_mesin.text = f'{dt_temp_mesin}'
            # self.ids.lb_temp_bahan_bakar.text = '-' if dt_temp_bhn_bkr == None else f"{db_bahan_bakar[np.where(db_bahan_bakar == dt_temp_bhn_bkr)[0][0],1]}"
            # self.ids.lb_temp_jbb.text = f'{dt_temp_jbb}'
            # self.ids.lb_temp_berat_kosong.text = f'{dt_temp_brt_ksg}'

            # Validate dropdowns have values selected
            if not hasattr(self.ids.drop_merk, 'merk_id'):
                toast("Pilih Merk!")
                return
            if not hasattr(self.ids.drop_bahan_bakar, 'bahan_bakar_id'):
                toast("Pilih Bahan Bakar!")
                return
            if not hasattr(self.ids.drop_warna, 'warna_id'):
                toast("Pilih Warna!")
                return

            dt_temp_id_merk = self.ids.drop_merk.merk_id
            dt_temp_bhn_bkr = self.ids.drop_bahan_bakar.bahan_bakar_id
            dt_temp_warna = self.ids.drop_warna.warna_id

            # Insert into database
            mycursor = mydb.cursor()
            sql = f"""
                INSERT INTO {TB_DATA_MASTER} 
                (NOUJI, NEW_NOUJI, NOPOL, NAMA, ALAMAT, MERK_ID, TYPE, idjeniskendaraan, BHN_BAKAR, JBB, BERATKOSONG, WARNA_KEND, TGL_UJI_PERDANA, TGL_UJI_TERAKHIR) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                dt_temp_no_uji,
                dt_temp_no_uji_new,
                dt_temp_no_pol,
                dt_temp_nama,
                dt_temp_alamat,
                dt_temp_id_merk,
                dt_temp_type,
                dt_temp_jenis_kendaraan,
                dt_temp_bhn_bkr,
                dt_temp_jbb,
                dt_temp_brt_ksg,
                dt_temp_warna,
                dt_temp_tgl_uji_terakhir,
                dt_temp_tgl_uji_terakhir
            )
            mycursor.execute(sql, values)
            mydb.commit()

            toast("Data berhasil didaftarkan")
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Terjadi kesalahan saat mendaftarkan data'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

class ScreenAddQueue(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenAddQueue, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    def on_enter(self):
        pass

    def on_leave(self):
        pass

    def exec_cancel(self):
        global dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_no_wilayah, dt_temp_no_kendaraan, dt_temp_no_plat, dt_temp_no_pol
        global dt_temp_nama, dt_temp_no_hp, dt_temp_alamat, dt_temp_id_izin, dt_temp_wilayah, dt_temp_provinsi, dt_temp_kabupaten_kota, dt_temp_kecamatan
        global dt_temp_id_merk, dt_temp_id_subjenis, dt_temp_type, dt_temp_tahun_buat, dt_temp_silinder, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_warna_plat
        global dt_temp_bhn_bkr, dt_temp_jbb, dt_temp_daya_motor, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji, dt_temp_status_penerbitan, dt_temp_jenis_kendaraan, dt_temp_kode_jenis_kendaraan, dt_temp_kode_wilayah

        try:
            dt_temp_no_uji = dt_temp_no_uji_new = dt_temp_no_wilayah = dt_temp_no_kendaraan = dt_temp_no_plat = dt_temp_no_pol = ""
            dt_temp_nama = dt_temp_no_hp = dt_temp_alamat = dt_temp_id_izin = dt_temp_wilayah = dt_temp_provinsi = dt_temp_kabupaten_kota = dt_temp_kecamatan = ""
            dt_temp_id_merk = dt_temp_id_subjenis = dt_temp_type = dt_temp_tahun_buat = dt_temp_silinder = dt_temp_warna = dt_temp_chasis = dt_temp_mesin = dt_temp_warna_plat = ""
            dt_temp_bhn_bkr = dt_temp_jbb = dt_temp_daya_motor = dt_temp_tgl_uji_terakhir = dt_temp_tgl_uji_habis = dt_temp_status_uji = dt_temp_status_penerbitan = dt_temp_jenis_kendaraan = dt_temp_kode_jenis_kendaraan = dt_temp_kode_wilayah = ""

            self.ids.tx_nopol.text = "" 
            self.ids.tx_nouji.text = "" 
            self.ids.lb_temp_nama.text = self.ids.lb_temp_alamat.text = ""
            self.ids.lb_temp_no_uji.text = self.ids.lb_temp_no_pol.text = self.ids.lb_temp_status_uji.text = self.ids.lb_temp_tgl_uji_terakhir.text = self.ids.lb_temp_tgl_uji_habis.text = ""
            self.ids.lb_temp_merk.text = self.ids.lb_temp_type.text = self.ids.lb_temp_jenis_kendaraan.text = self.ids.lb_temp_warna.text = ""
            self.ids.lb_temp_chasis.text = self.ids.lb_temp_mesin.text = self.ids.lb_temp_bahan_bakar.text = self.ids.lb_temp_jbb.text = ""
            self.ids.bt_register.disabled = True

            self.exec_navigate_main()
            
        except Exception as e:
            toast_msg = f'Gagal Memuat Data'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_find(self):
        global mydb, db_users, db_merk, db_bahan_bakar, db_warna
        global dt_id_user, dt_user, dt_foto_user
        global dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_no_wilayah, dt_temp_no_kendaraan, dt_temp_no_plat, dt_temp_no_pol
        global dt_temp_nama, dt_temp_no_hp, dt_temp_alamat, dt_temp_id_izin, dt_temp_wilayah, dt_temp_provinsi, dt_temp_kabupaten_kota, dt_temp_kecamatan
        global dt_temp_id_merk, dt_temp_id_subjenis, dt_temp_type, dt_temp_tahun_buat, dt_temp_silinder, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_warna_plat
        global dt_temp_bhn_bkr, dt_temp_jbb, dt_temp_daya_motor, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji, dt_temp_status_penerbitan, dt_temp_jenis_kendaraan, dt_temp_kode_jenis_kendaraan, dt_temp_kode_wilayah

        try:
            dt_find_no_pol = self.ids.tx_nopol.text
            dt_find_no_uji = self.ids.tx_nouji.text
            self.exec_fetch_master_data(dt_find_no_pol, dt_find_no_uji)

            self.ids.lb_temp_nama.text = f'{dt_temp_nama}'
            self.ids.lb_temp_alamat.text = f'{dt_temp_alamat}'
            self.ids.lb_temp_no_uji.text = f'{dt_temp_no_uji}'
            self.ids.lb_temp_no_pol.text = f'{dt_temp_no_pol}'
            self.ids.lb_temp_status_uji.text = 'Berkala' if dt_temp_status_uji == 'B' else 'Uji Ulang' if dt_temp_status_uji == 'U' else 'Baru' if dt_temp_status_uji == 'BR' else 'Numpang Uji' if dt_temp_status_uji == 'NB' else 'Mutasi'
            self.ids.lb_temp_tgl_uji_terakhir.text = f'{dt_temp_tgl_uji_terakhir}'
            self.ids.lb_temp_tgl_uji_habis.text = f'{dt_temp_tgl_uji_habis}'
            self.ids.lb_temp_merk.text = '-' if dt_temp_id_merk == None else f"{db_merk[np.where(db_merk == dt_temp_id_merk)[0][0],1]}"
            self.ids.lb_temp_type.text = f'{dt_temp_type}'
            self.ids.lb_temp_jenis_kendaraan.text = f'{dt_temp_jenis_kendaraan}'
            self.ids.lb_temp_warna.text = '-' if dt_temp_warna == None else f"{db_warna[np.where(db_warna == dt_temp_warna)[0][0],1]}"
            self.ids.lb_temp_chasis.text = f'{dt_temp_chasis}'
            self.ids.lb_temp_mesin.text = f'{dt_temp_mesin}'
            self.ids.lb_temp_bahan_bakar.text = '-' if dt_temp_bhn_bkr == None else f"{db_bahan_bakar[np.where(db_bahan_bakar == dt_temp_bhn_bkr)[0][0],1]}"
            self.ids.lb_temp_jbb.text = f'{dt_temp_jbb}'
            self.ids.lb_temp_berat_kosong.text = f'{dt_temp_brt_ksg}'
            self.ids.bt_register.disabled = False
            
        except Exception as e:
            toast_msg = f'Gagal Menemukan Data, Silahkan Isi Nomor Uji atau Nomor Polisi dengan Benar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_fetch_master_data(self, dt_find_no_pol, dt_find_no_uji):
        global mydb, db_users, db_merk, db_bahan_bakar, db_warna
        global dt_id_user, dt_user, dt_foto_user
        global dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_no_wilayah, dt_temp_no_kendaraan, dt_temp_no_plat, dt_temp_no_pol
        global dt_temp_nama, dt_temp_no_hp, dt_temp_alamat, dt_temp_id_izin, dt_temp_wilayah, dt_temp_provinsi, dt_temp_kabupaten_kota, dt_temp_kecamatan
        global dt_temp_id_merk, dt_temp_id_subjenis, dt_temp_type, dt_temp_tahun_buat, dt_temp_silinder, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_warna_plat
        global dt_temp_bhn_bkr, dt_temp_jbb, dt_temp_brt_ksg, dt_temp_daya_motor, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji, dt_temp_status_penerbitan, dt_temp_jenis_kendaraan, dt_temp_kode_jenis_kendaraan, dt_temp_kode_wilayah

        try:
            mycursor = mydb.cursor()
            if dt_find_no_pol != "" and dt_find_no_uji == "":
                mycursor.execute(f"SELECT NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, idjeniskendaraan, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, BERATKOSONG, DAYAMOTOR, TGL_UJI_TERAKHIR, STATUSUJI, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah FROM {TB_DATA_MASTER} WHERE NOPOL = '{dt_find_no_pol}' ")
            elif dt_find_no_uji != "":
                mycursor.execute(f"SELECT NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, idjeniskendaraan, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, BERATKOSONG, DAYAMOTOR, TGL_UJI_TERAKHIR, STATUSUJI, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah FROM {TB_DATA_MASTER} WHERE NOUJI = '{dt_find_no_uji}' ")
            elif dt_find_no_uji == "" and dt_find_no_pol == "":
                toast("Silahkan Isi Nomor Uji atau Nomor Polisi dengan Benar")
            myresult = mycursor.fetchone()
            mydb.commit()
            db_master_data = np.array(myresult).T

            if myresult is None:
                toast('Data Tidak Ditemukan di Database, Silahkan Ajukan Pengujian Baru')
                self.exec_cancel()
            else:
                dt_temp_no_uji = db_master_data[0]
                dt_temp_no_uji_new = db_master_data[1]
                dt_temp_no_wilayah = db_master_data[2]
                dt_temp_no_kendaraan = db_master_data[3]
                dt_temp_no_plat = db_master_data[4]
                dt_temp_no_pol = db_master_data[5]
                dt_temp_nama = db_master_data[6]
                dt_temp_no_hp = db_master_data[7]
                dt_temp_alamat = db_master_data[8]
                dt_temp_id_izin = db_master_data[9]
                dt_temp_wilayah = db_master_data[10]
                dt_temp_provinsi = db_master_data[11]
                dt_temp_kabupaten_kota = db_master_data[12]
                dt_temp_kecamatan = db_master_data[13]
                dt_temp_id_merk = db_master_data[14]
                dt_temp_id_subjenis = db_master_data[15]
                dt_temp_type = db_master_data[16]
                dt_temp_tahun_buat = db_master_data[17]
                dt_temp_silinder = db_master_data[18]
                dt_temp_warna = db_master_data[19]
                dt_temp_chasis = db_master_data[20]
                dt_temp_mesin = db_master_data[21]
                dt_temp_warna_plat = db_master_data[22]
                dt_temp_bhn_bkr = db_master_data[23]
                dt_temp_jbb = db_master_data[24]
                dt_temp_brt_ksg = db_master_data[25]
                dt_temp_daya_motor = db_master_data[26]
                
                dt_temp_status_uji = db_master_data[28]
                dt_temp_status_penerbitan = db_master_data[29]
                dt_temp_jenis_kendaraan = db_master_data[30]
                dt_temp_kode_jenis_kendaraan = db_master_data[31]
                dt_temp_kode_wilayah = db_master_data[32]

                if(db_master_data[26] is not None):
                    last_uji_date = db_master_data[27]
                else:
                    last_uji_date = datetime.datetime(1900, 1, 1)

                if(last_uji_date.month <= 6):
                    year_replaced = last_uji_date.year
                    month_replaced = last_uji_date.month + 6
                    day_replaced = last_uji_date.day
                else:
                    year_replaced = last_uji_date.year + 1
                    month_replaced = last_uji_date.month - 6
                    day_replaced = last_uji_date.day
                
                if(last_uji_date.day > 29):
                    if month_replaced == 2:
                        day_replaced = 29
                    if month_replaced == 4 or month_replaced == 6 or month_replaced == 9 or month_replaced == 11:
                        day_replaced = 30
                    
                dt_temp_tgl_uji_terakhir = str(last_uji_date.strftime('%d-%m-%Y'))
                dt_temp_tgl_uji_habis = str(last_uji_date.replace(month=month_replaced, year=year_replaced, day=day_replaced).strftime('%d-%m-%Y'))
                
        except Exception as e:
            toast_msg = f'Gagal Menemukan Data dari Database Master'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_register(self):
        global mydb, db_users, db_merk, db_bahan_bakar, db_warna
        global dt_id_user, dt_user, dt_foto_user
        global dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_no_wilayah, dt_temp_no_kendaraan, dt_temp_no_plat, dt_temp_no_pol
        global dt_temp_nama, dt_temp_no_hp, dt_temp_alamat, dt_temp_id_izin, dt_temp_wilayah, dt_temp_provinsi, dt_temp_kabupaten_kota, dt_temp_kecamatan
        global dt_temp_id_merk, dt_temp_id_subjenis, dt_temp_type, dt_temp_tahun_buat, dt_temp_silinder, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_warna_plat
        global dt_temp_bhn_bkr, dt_temp_jbb, dt_temp_brt_ksg, dt_temp_daya_motor, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji, dt_temp_status_penerbitan, dt_temp_jenis_kendaraan, dt_temp_kode_jenis_kendaraan, dt_temp_kode_wilayah

        try:
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT MAX(noantrian) FROM {TB_DATA}")
            result = mycursor.fetchone()
            last_noantrian = int(result[0]) if result[0] is not None else 0
            noantrian = f"{last_noantrian + 1:04d}"

            mycursor = mydb.cursor()
            sql = f"INSERT INTO {TB_DATA} (noantrian, nopol, nouji, NEW_NOUJI, merk, type, idjeniskendaraan, jbb, berat_kosong, warna) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (noantrian, dt_temp_no_pol, dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_id_merk, dt_temp_type, dt_temp_id_subjenis, dt_temp_jbb, dt_temp_brt_ksg, dt_temp_warna)
            mycursor.execute(sql, values)
            mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal menambah data antrian baru'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        self.exec_cancel()

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Login'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Utama'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

class ScreenMenu(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenMenu, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS

    # def on_enter(self):
    #     # Saat masuk ke layar ini, panggil fungsi untuk memulai pengambilan data di latar belakang
    #     self.start_database_reload()
        
    # def start_database_reload(self):
    #     """Memulai thread baru untuk memuat data dari database."""
    #     # Tampilkan indikator loading jika perlu (opsional)
    #     # self.ids.spinner.active = True 
    #     threading.Thread(target=self._reload_data_thread).start()

    # def _reload_data_thread(self):
    #     """
    #     Fungsi ini berjalan di background thread.
    #     Tugasnya hanya mengambil data dari database.
    #     """
    #     global db_antrian, db_merk, db_bahan_bakar, db_warna, dt_dash_antri, dt_dash_belum_uji, dt_dash_sudah_uji

    #     try:
    #         # Pastikan koneksi DB dibuat di thread ini, bukan dibagi dari thread utama
    #         mydb_thread = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    #         cursor = mydb_thread.cursor()
            
    #         # --- Proses pengambilan data Anda (sama seperti di exec_reload_table) ---
    #         cursor.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
    #         db_merk = np.array(cursor.fetchall())

    #         cursor.execute(f"SELECT ID, DESCRIPTION FROM {TB_BAHAN_BAKAR}")
    #         db_bahan_bakar = np.array(cursor.fetchall())
            
    #         cursor.execute(f"SELECT id_warna, nama FROM {TB_WARNA}")
    #         db_warna = np.array(cursor.fetchall())

    #         cursor.execute(f"SELECT COUNT(*) FROM {TB_DATA}")
    #         result_count = cursor.fetchone()
    #         dt_dash_antri = result_count[0] if result_count else 0
            
    #         cursor.execute(f"SELECT noantrian, nopol, ... FROM {TB_DATA} WHERE check_flag = 0") # Query lengkap Anda
    #         result_antrian = cursor.fetchall()
    #         db_antrian = np.array(result_antrian).T
            
    #         dt_dash_belum_uji = db_antrian.shape[1] if db_antrian.size > 0 else 0
    #         dt_dash_sudah_uji = dt_dash_antri - dt_dash_belum_uji

    #         # Data berhasil diambil, jadwalkan pembaruan UI di thread utama
    #         Clock.schedule_once(lambda dt: self.update_ui_with_data())

    #     except Exception as e:
    #         Logger.error(f"ScreenMain: Gagal memuat data di background thread: {e}")
    #         Clock.schedule_once(lambda dt: toast(f"Gagal memuat data: {e}"))
    #     finally:
    #         if 'mydb_thread' in locals() and mydb_thread.is_connected():
    #             cursor.close()
    #             mydb_thread.close()

    # def update_ui_with_data(self):
    #     """
    #     Fungsi ini dipanggil di main thread untuk memperbarui widget UI.
    #     Ini aman karena tidak ada operasi database di sini.
    #     """
    #     global db_antrian

        
    #     layout_list = self.ids.layout_list
    #     layout_list.clear_widgets()

    #     try:
    #         if db_antrian.size == 0:
    #             # Tampilkan pesan jika tidak ada antrian
    #             layout_list.add_widget(MDLabel(text="Tidak ada antrian untuk hari ini.", halign="center"))
    #             return

    #         for i in range(db_antrian[0,:].size):
    #             # --- Proses pembuatan widget MDCard Anda (sama seperti sebelumnya) ---
    #             card = MDCard(...) # Buat MDCard seperti kode Anda sebelumnya
    #             layout_list.add_widget(card)

    #     except Exception as e:
    #         toast('Gagal memperbaharui tampilan tabel')
    #         Logger.error(f"ScreenMain: Gagal update UI: {e}")

    def on_enter(self):
        global db_merk, db_bahan_bakar, db_warna
        global dt_no_antri, dt_no_pol, dt_no_uji
        global dt_temp_nama, dt_temp_alamat, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji
        global dt_temp_id_merk, dt_temp_type, dt_temp_jenis_kendaraan, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_bhn_bkr, dt_temp_jbb

        merk_text = '-'
        if dt_temp_id_merk is not None:
            try:
                indices = np.where(db_merk[:, 0].astype(str) == str(dt_temp_id_merk))[0]
                if indices.size > 0:
                    merk_text = db_merk[indices[0], 1]
                else:
                    merk_text = "ID Merk Tidak Valid"
                    Logger.warning(f"Merk ID {dt_temp_id_merk} not found in db_merk.")
            except Exception as e:
                merk_text = "Error Merk"
                Logger.error(f"Error processing merk: {e}")

        warna_text = '-'
        if dt_temp_warna is not None:
            try:
                indices = np.where(db_warna[:, 0].astype(str) == str(dt_temp_warna))[0]
                if indices.size > 0:
                    warna_text = db_warna[indices[0], 1]
                else:
                    warna_text = "ID Warna Tidak Valid"
                    Logger.warning(f"Warna ID {dt_temp_warna} not found in db_warna.")
            except Exception as e:
                warna_text = "Error Warna"
                Logger.error(f"Error processing warna: {e}")
                
        bahan_bakar_text = '-'
        if dt_temp_bhn_bkr is not None:
            try:
                indices = np.where(db_bahan_bakar[:, 0].astype(str) == str(dt_temp_bhn_bkr))[0]
                if indices.size > 0:
                    bahan_bakar_text = db_bahan_bakar[indices[0], 1]
                else:
                    bahan_bakar_text = "ID B.Bakar Tidak Valid"
                    Logger.warning(f"Bahan Bakar ID {dt_temp_bhn_bkr} not found in db_bahan_bakar.")
            except Exception as e:
                bahan_bakar_text = "Error B.Bakar"
                Logger.error(f"Error processing bahan bakar: {e}")

        self.ids.lb_no_antrian.text = str(dt_no_antri)
        self.ids.lb_no_pol.text = str(dt_no_pol)
        self.ids.lb_no_uji.text = str(dt_no_uji)
        self.ids.lb_temp_nama.text = str(dt_temp_nama) if dt_temp_nama else '-'
        self.ids.lb_temp_alamat.text = str(dt_temp_alamat) if dt_temp_alamat else '-'
        self.ids.lb_temp_status_uji.text = 'Berkala' if dt_temp_status_uji == 'B' else 'Uji Ulang' if dt_temp_status_uji == 'U' else 'Baru' if dt_temp_status_uji == 'BR' else 'Numpang Uji' if dt_temp_status_uji == 'NB' else 'Mutasi'
        self.ids.lb_temp_tgl_uji_terakhir.text = f'{dt_temp_tgl_uji_terakhir}'
        self.ids.lb_temp_tgl_uji_habis.text = f'{dt_temp_tgl_uji_habis}'
        self.ids.lb_temp_merk.text = merk_text
        self.ids.lb_temp_type.text = str(dt_temp_type) if dt_temp_type else '-'
        self.ids.lb_temp_jenis_kendaraan.text = str(dt_temp_jenis_kendaraan) if dt_temp_jenis_kendaraan else '-'
        self.ids.lb_temp_warna.text = warna_text
        self.ids.lb_temp_chasis.text = str(dt_temp_chasis) if dt_temp_chasis else '-'
        self.ids.lb_temp_mesin.text = str(dt_temp_mesin) if dt_temp_mesin else '-'
        self.ids.lb_temp_bahan_bakar.text = bahan_bakar_text
        self.ids.lb_temp_jbb.text = str(dt_temp_jbb) if dt_temp_jbb else '-'

    def exec_verify_data(self):
        global dt_id_pendaftaran, dt_no_antri, dt_verified_data, dt_verified_payment
        global dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_no_wilayah, dt_temp_no_kendaraan, dt_temp_no_plat, dt_temp_no_pol
        global dt_temp_nama, dt_temp_no_hp, dt_temp_alamat, dt_temp_id_izin, dt_temp_wilayah, dt_temp_provinsi, dt_temp_kabupaten_kota, dt_temp_kecamatan
        global dt_temp_id_merk, dt_temp_id_subjenis, dt_temp_type, dt_temp_tahun_buat, dt_temp_silinder, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_warna_plat
        global dt_temp_bhn_bkr, dt_temp_jbb, dt_temp_daya_motor, dt_temp_tgl_uji_terakhir, dt_temp_status_penerbitan, dt_temp_jenis_kendaraan, dt_temp_kode_jenis_kendaraan, dt_temp_kode_wilayah

        try:
            mycursor = mydb.cursor()
            sql = f"INSERT INTO {TB_DAFTAR_BERKALA} (ID, NOANTRIAN, NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, SUBJENIS_ID, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, DAYAMOTOR, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah, TGL_LASTUJI) VALUES ('{dt_id_pendaftaran}', '{dt_no_antri}', '{dt_temp_no_uji}','{dt_temp_no_uji_new}','{dt_temp_no_wilayah}','{dt_temp_no_kendaraan}','{dt_temp_no_plat}','{dt_temp_no_pol}','{dt_temp_nama}','{dt_temp_no_hp}','{dt_temp_alamat}','{dt_temp_id_izin}','{dt_temp_wilayah}','{dt_temp_provinsi}','{dt_temp_kabupaten_kota}','{dt_temp_kecamatan}','{dt_temp_id_merk}','{dt_temp_id_subjenis}','{dt_temp_type}','{dt_temp_tahun_buat}','{dt_temp_silinder}','{dt_temp_warna}','{dt_temp_chasis}','{dt_temp_mesin}','{dt_temp_warna_plat}','{dt_temp_bhn_bkr}','{dt_temp_jbb}','{dt_temp_daya_motor}','{dt_temp_status_penerbitan}','{dt_temp_jenis_kendaraan}','{dt_temp_kode_jenis_kendaraan}','{dt_temp_kode_wilayah}','{dt_temp_tgl_uji_terakhir}')"
            mycursor.execute(sql)
            mydb.commit()
            dt_verified_data = 1
            dt_verified_payment = 0
            toast_msg = f'Berhasil Membuat Data Pengujian di Tabel Daftar Berkala'
            toast(toast_msg)
            self.exec_verify_payment()
        except Exception as e:
            toast_msg = f'Gagal Membuat Tabel Daftar Berkala'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_verify_payment(self):
        global dt_no_antri, dt_sts_uji, dt_verified_payment
        global mydb, db_users, db_merk, db_bahan_bakar, db_warna
        global dt_id_user, dt_user, dt_foto_user
        global dt_dash_antri, dt_sts_uji
        global dt_temp_no_uji, dt_temp_no_uji_new, dt_temp_no_wilayah, dt_temp_no_kendaraan, dt_temp_no_plat, dt_temp_no_pol
        global dt_temp_nama, dt_temp_no_hp, dt_temp_alamat, dt_temp_id_izin, dt_temp_wilayah, dt_temp_provinsi, dt_temp_kabupaten_kota, dt_temp_kecamatan
        global dt_temp_id_merk, dt_temp_id_subjenis, dt_temp_type, dt_temp_tahun_buat, dt_temp_silinder, dt_temp_warna, dt_temp_chasis, dt_temp_mesin, dt_temp_warna_plat
        global dt_temp_bhn_bkr, dt_temp_jbb, dt_temp_daya_motor, dt_temp_tgl_uji_terakhir, dt_temp_tgl_uji_habis, dt_temp_status_uji, dt_temp_status_penerbitan, dt_temp_jenis_kendaraan, dt_temp_kode_jenis_kendaraan, dt_temp_kode_wilayah

        dt_tgl_baru_uji = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))

        try:
            mycursor = mydb.cursor()
            sql = f"UPDATE {TB_DAFTAR_BERKALA} SET STS_SPP = '1' WHERE NOANTRIAN = '{dt_no_antri}' "
            mycursor.execute(sql)
            mydb.commit()
            dt_verified_payment = 1
            toast_msg = f'Berhasil Memverifikasi Pembayaran'
            toast(toast_msg)
        except Exception as e:
            toast_msg = f'Gagal Memverifikasi Pembayaran'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            today = str(time.strftime("%Y-%m-%d", time.localtime()))
            make_dir_path = f'/var/www/system/storage/app/capture/{today}/{dt_sts_uji}-{dt_no_antri}'
            self.sftp_make_dir(make_dir_path)
        except Exception as e:
            toast_msg = f'Gagal Menemukan Folder Remote'
            toast(toast_msg)  
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            mycursor = mydb.cursor()
            sql = f"INSERT INTO {TB_DATA_IMAGE} (noantrian, nouji, NEW_NOUJI, nopol, idjeniskendaraan, kd_jeniskendaraan, kodewilayah, jbb, statusuji, statuspenerbitan, tgl_capture, trfstat) VALUES ('{dt_no_antri}','{dt_temp_no_uji}','{dt_temp_no_uji_new}','{dt_temp_no_pol}','{dt_temp_jenis_kendaraan}','{dt_temp_kode_jenis_kendaraan}','{dt_temp_kode_wilayah}','{dt_temp_jbb}','{dt_temp_status_uji}','{dt_temp_status_penerbitan}','{dt_tgl_baru_uji}','0')"
            mycursor.execute(sql)
            mydb.commit()
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Tabel Image Kendaraan'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        # except Exception as e:
        #     toast_msg = f'Gagal Memverifikasi Pembayaran'
        #     toast(toast_msg)
        #     Logger.error(f"{self.name}: {toast_msg}, {e}")

        try:
            tb_image = mydb.cursor()
            tb_image.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
            result_tb_image = tb_image.fetchone()
            id_image = result_tb_image[0]

            array_kode_kelompok = np.array(['V1', 'V2', 'P2P3', 'P4'])
            for i in range(array_kode_kelompok.size):
                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_UJI} (tanggal, nopol, nouji, newnouji, kode_kelompok_uji, lulus_uji, id_image) VALUES ('{dt_tgl_baru_uji}', '{dt_no_pol}','{dt_no_uji}','{dt_no_uji}','{array_kode_kelompok[i]}','1', '{id_image}' )"
                mycursor.execute(sql)
                mydb.commit()        
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Tabel Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def sftp_make_dir(self, remote_path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASS)
        sftp = ssh.open_sftp()
        try:
            sftp.chdir(remote_path)  # Test if remote_path exists
            toast(f'Direktori {remote_path} Sudah Ada')
        except IOError:
            sftp.mkdir(remote_path)  # Create remote_path
            sftp.chdir(remote_path)
            toast(f'Berhasil Membuat Direktori {remote_path}')
        sftp.close()
        ssh.close()

    def exec_barrier_open(self):
        global flag_conn_stat, flag_gate
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                if(flag_conn_stat):
                    flag_gate = True
                else:
                    toast("Tidak Bisa Membuka Portal Karena PLC Tidak Terhubung") 
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)       

            if flag_conn_stat:
                MODBUS_CLIENT.connect()
                MODBUS_CLIENT.write_coil(3072, flag_gate, slave=1) #M0
                MODBUS_CLIENT.close()
        except Exception as e:
            toast_msg = f'Gagal Mengirim Perintah BUKA PORTAL ke PLC'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_barrier_close(self):
        global flag_conn_stat, flag_gate
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                if(flag_conn_stat):
                    flag_gate = False
                else:
                    toast("Tidak Bisa Menutup Portal Karena PLC Tidak Terhubung") 
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)      

            if flag_conn_stat:
                MODBUS_CLIENT.connect()
                MODBUS_CLIENT.write_coil(3073, not flag_gate, slave=1) #M1
                MODBUS_CLIENT.close()
        except Exception as e:
            toast_msg = f'Gagal Mengirim Perintah TUTUP PORTAL ke PLC'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_barrier_stop(self):
        global flag_conn_stat

        try:
            if flag_conn_stat:
                MODBUS_CLIENT.connect()
                MODBUS_CLIENT.write_coil(3072, False, slave=1) #M0
                MODBUS_CLIENT.write_coil(3073, False, slave=1) #M1
                MODBUS_CLIENT.close()
        except Exception as e:
            toast_msg = f'Gagal Mengirim Perintah HENTIKAN PORTAL ke PLC'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_inspect_id(self):
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                self.screen_manager.current = 'screen_inspect_id'
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)                 

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Inspeksi Identitas'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_inspect_dimension(self):
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                self.screen_manager.current = 'screen_inspect_dimension'
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)                 

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Inspeksi Dimensi'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_capture(self):
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                self.screen_manager.current = 'screen_realtime_cctv'
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)         

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Pengambilan Foto Empat Sisi'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_inspect_visual(self):
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                self.screen_manager.current = 'screen_inspect_visual'
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)           

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Inspeksi Visual 1'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_inspect_visual2(self):
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                self.screen_manager.current = 'screen_inspect_visual2'
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)  

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Inspeksi Visual 2'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_inspect_pit(self):
        global dt_verified_data, dt_verified_payment

        try:
            if dt_verified_data and dt_verified_payment:
                self.screen_manager.current = 'screen_inspect_pit'
            else:
                toast_msg = f'Silahkan Verifikasi Data dan Pembayaran Terlebih Dahulu'
                toast(toast_msg)

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Inspeksi Bawah Kendaraan'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_save(self):
        try:
            mycursor = mydb.cursor()
            sql = f"UPDATE {TB_DATA} SET check_flag = '1' WHERE noantrian = '{dt_no_antri}' "
            mycursor.execute(sql)
            mydb.commit()
            toast_msg = f'Berhasil Menyimpan dan Menyelesaikan Inspeksi'
            toast(toast_msg)
        except Exception as e:
            toast_msg = f'Gagal Menyelesaikan Inspeksi'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        self.screen_manager.current = 'screen_main'

    def exec_cancel(self):
        self.screen_manager.current = 'screen_main'

class ScreenInspectId(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectId, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
    
    def on_enter(self):
        global dt_no_antri, dt_no_pol, dt_no_uji

        self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Identitas: LULUS"
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Menu Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji, flags_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            selected_row_komponen_uji = row
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_bt_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji, flags_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("bt_komponen_uji",""))
            selected_row_komponen_uji = row
            if(flags_komponen_uji[row]):
                flags_komponen_uji[row] = False
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_komponen_uji[row] = True
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Tombol Icon Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, selected_row_komponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            selected_nama_komponen_uji = db_komponen_uji[2, selected_row_komponen_uji]

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"

            if(np.all(flags_subkomponen_uji == True)):
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#2CA02C"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Identitas: LULUS"
            else:
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#FF2A2A"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Identitas: TIDAK LULUS pada komponen uji {selected_nama_komponen_uji}"
            
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji
        global flags_komponen_uji
        global window_size_x, window_size_y

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K01' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
            flags_komponen_uji = np.ones(db_komponen_uji[0,:].size, dtype='bool')
            
        except Exception as e:
            toast_msg = f'Ggaal Mengambil Data dari Tabel Komponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                card = MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height=dp(int(60 * 800 / window_size_y)),
                        )
                self.ids[f'card_komponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                bt_check = MDIconButton(
                        size_hint_x= 0.1, 
                        icon="check-bold", 
                        md_bg_color="#2CA02C",
                        on_press = self.on_komponen_uji_bt_press,
                        id=f'bt_komponen_uji{i}',
                        )         
                self.ids[f'bt_komponen_uji{i}'] = bt_check
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tabel Komponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_subkomponen_uji(self, kode_komponen_uji, default=True):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji
        global window_size_x, window_size_y

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ORDER BY urut")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            if(default):
                flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
            else:
                flags_subkomponen_uji = np.zeros(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Subkomponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height=dp(int(60 * 800 / window_size_y)),
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                if(default):
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)
                else:
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="cancel", md_bg_color="#FF2A2A",)
                                
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data Tabel Subkomponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        global window_size_x, window_size_y

        try:
            Logger.info(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak Ada Rekomendasi Komentar, Silahkan Isi Komentar Sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(int(60 * 800 / window_size_y)),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Gagal Menampilkan Rekomendasi Komentar'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        global mydb, db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, db_last_data
        global dt_no_pol, selected_row_komponen_uji

        try:
            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
            result_tb_image_kendaraan = tb_image_kendaraan.fetchone()
            mydb.commit()
            id_image = result_tb_image_kendaraan[0]

            if self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon == "cancel":
                mycursor = mydb.cursor()
                sql = f"UPDATE {TB_UJI} SET lulus_uji = '0' WHERE nopol = '{dt_no_pol}' AND id_image = '{id_image}' "
                mycursor.execute(sql)
                mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data di Database Tabel Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            tb_uji = mydb.cursor()
            tb_uji.execute(f"SELECT id_uji FROM {TB_UJI} WHERE nopol = '{dt_no_pol}' AND kode_kelompok_uji = 'V1' ORDER BY id_uji DESC LIMIT 1")
            result_tb_uji = tb_uji.fetchone()
            mydb.commit()
            id_uji = result_tb_uji[0]
            dt_selected_kode_komponen_uji = db_komponen_uji[1, selected_row_komponen_uji]

            for i in range(db_subkomponen_uji[0,:].size):                
                kode_subkomponen_uji = db_subkomponen_uji[0,i]
                comment_subkomponen_uji = self.ids[f'tx_comment{i}'].text

                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_UJI_DETAIL} (id_uji, hasil, kode_komponen_uji, kode_subkomponen_uji, keterangan) VALUES ('{id_uji}', '{int(flags_subkomponen_uji[i])}','{dt_selected_kode_komponen_uji}','{kode_subkomponen_uji}','{comment_subkomponen_uji}')"
                mycursor.execute(sql)
                mydb.commit()

            toast_msg = f'Berhasil Menyimpan Data'
            toast(toast_msg)            

            self.open_screen_menu()
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Database Tabel Uji Detail'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectDimension(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectDimension, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
    
    def on_enter(self):
        global dt_no_antri, dt_no_pol, dt_no_uji

        self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi DImensi: LULUS"
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Menu Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            selected_row_komponen_uji = row
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_bt_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji, flags_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("bt_komponen_uji",""))
            selected_row_komponen_uji = row
            if(flags_komponen_uji[row]):
                flags_komponen_uji[row] = False
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_komponen_uji[row] = True
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Tombol Icon Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, selected_row_komponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            selected_nama_komponen_uji = db_komponen_uji[2, selected_row_komponen_uji]

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"

            if(np.all(flags_subkomponen_uji == True)):
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#2CA02C"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi DImensi: LULUS"
            else:
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#FF2A2A"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi DImensi: TIDAK LULUS pada komponen uji {selected_nama_komponen_uji}"
            
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji
        global flags_komponen_uji
        global window_size_x, window_size_y

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K02' OR kode_komponen_uji = 'K15' OR kode_komponen_uji = 'K18' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
            flags_komponen_uji = np.ones(db_komponen_uji[0,:].size, dtype='bool')            
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                card = MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height=dp(int(60 * 800 / window_size_y)),
                        )
                self.ids[f'card_komponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                bt_check = MDIconButton(
                        size_hint_x= 0.1, 
                        icon="check-bold", 
                        md_bg_color="#2CA02C",
                        on_press = self.on_komponen_uji_bt_press,
                        id=f'bt_komponen_uji{i}',
                        )                     
                self.ids[f'bt_komponen_uji{i}'] = bt_check
                card.add_widget(bt_check)
                
        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_subkomponen_uji(self, kode_komponen_uji, default=True):
        global mydb, db_subkomponen_uji, dt_no_pol
        global flags_subkomponen_uji, db_last_data, dt_jns_kend
        global window_size_x, window_size_y

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, value FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ORDER BY urut")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            if(default):
                flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
            else:
                flags_subkomponen_uji = np.zeros(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Subkomponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height=dp(int(60 * 800 / window_size_y)),
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_value = MDTextField(size_hint_x= 0.2, hint_text="Data",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                tx_comment = MDTextField(size_hint_x= 0.2, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                if(default):
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)
                else:
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="cancel", md_bg_color="#FF2A2A",)                            
                self.ids[f'tx_value{i}'] = tx_value
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_value)
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            db_last_data = np.array([])
            for i in range(db_subkomponen_uji[2,:].size):
                column_name = db_subkomponen_uji[2,i]
                tb_image_kendaraan = mydb.cursor()
                tb_image_kendaraan.execute(f"SELECT {column_name} FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
                result_tb_image_kendaraan = tb_image_kendaraan.fetchone()
                mydb.commit()
                last_data = result_tb_image_kendaraan[0]
                db_last_data = np.append(db_last_data, last_data)

                self.ids[f'tx_value{i}'].text = str(last_data)
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data Terakhir dari Database Tabel Image Kendaraan'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

            try:
                toast_msg = f'Trying Reload Data from Table Jenis Kendaraan'
                Logger.info(toast_msg)

                db_last_data = np.array([])
                for i in range(db_subkomponen_uji[2,:].size):
                    column_name = db_subkomponen_uji[2,i]
                    for i in range(column_name):
                        tb_jenis_kendaraan = mydb.cursor()
                        tb_jenis_kendaraan.execute(f"SELECT {column_name[i]} FROM {TB_DATA_KENDARAAN} WHERE field = '{column_name[i]}' AND jenis = '{dt_jns_kend}' ORDER BY id DESC LIMIT 1")
                        result_tb_jenis_kendaraan = tb_jenis_kendaraan.fetchone()
                        mydb.commit()
                        last_data = result_tb_jenis_kendaraan[0]
                        db_last_data = np.append(db_last_data, last_data)

                    self.ids[f'tx_value{i}'].text = str(last_data)
            except Exception as e:
                toast_msg = f'Gagal Mengambil Data Terakhir dari Database Tabel Jenis Kendaraan'
                toast(toast_msg)
                Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        global window_size_x, window_size_y

        try:
            Logger.info(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak Ada Rekomendasi Komentar, Silahkan Isi Komentar Sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(int(60 * 800 / window_size_y)),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Gagal Menampilkan Rekomendasi Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, db_last_data
        global mydb, dt_no_pol, selected_row_komponen_uji

        try:
            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
            result_tb_image_kendaraan = tb_image_kendaraan.fetchone()
            mydb.commit()
            id_image = result_tb_image_kendaraan[0]

            for i in range(db_subkomponen_uji[2,:].size):                
                column_name = db_subkomponen_uji[2,i]
                mycursor = mydb.cursor()
                new_data = self.ids[f'tx_value{i}'].text
                sql = f"UPDATE {TB_DATA_IMAGE} SET {column_name} = '{new_data}' WHERE nopol = '{dt_no_pol}' AND id = '{id_image}' "
                mycursor.execute(sql)
                mydb.commit()

            if self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon == "cancel":
                mycursor = mydb.cursor()
                sql = f"UPDATE {TB_UJI} SET lulus_uji = '0' WHERE nopol = '{dt_no_pol}' AND id_image = '{id_image}' "
                mycursor.execute(sql)
                mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal Update Data ke Tabel Image Kendaraan dan Tabel Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            tb_uji = mydb.cursor()
            tb_uji.execute(f"SELECT id_uji FROM {TB_UJI} WHERE nopol = '{dt_no_pol}' AND kode_kelompok_uji = 'V1' ORDER BY id_uji DESC LIMIT 1")
            result_tb_uji = tb_uji.fetchone()
            mydb.commit()
            id_uji = result_tb_uji[0]
            dt_selected_kode_komponen_uji = db_komponen_uji[1, selected_row_komponen_uji]

            for i in range(db_subkomponen_uji[0,:].size):                
                kode_subkomponen_uji = db_subkomponen_uji[0,i]
                comment_subkomponen_uji = self.ids[f'tx_comment{i}'].text

                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_UJI_DETAIL} (id_uji, hasil, kode_komponen_uji, kode_subkomponen_uji, keterangan) VALUES ('{id_uji}', '{int(flags_subkomponen_uji[i])}','{dt_selected_kode_komponen_uji}','{kode_subkomponen_uji}','{comment_subkomponen_uji}')"
                mycursor.execute(sql)
                mydb.commit()

            toast_msg = f'Berhasil menyimpan data'
            toast(toast_msg)

            self.open_screen_menu()
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Tabel Uji Detail'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectVisual(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectVisual, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
    
    def on_enter(self):
        global dt_no_antri, dt_no_pol, dt_no_uji

        self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Visual 1: LULUS"
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Menu Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            selected_row_komponen_uji = row
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_bt_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji, flags_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("bt_komponen_uji",""))
            selected_row_komponen_uji = row
            if(flags_komponen_uji[row]):
                flags_komponen_uji[row] = False
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_komponen_uji[row] = True
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Tombol Icon Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, selected_row_komponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            selected_nama_komponen_uji = db_komponen_uji[2, selected_row_komponen_uji]

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"

            if(np.all(flags_subkomponen_uji == True)):
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#2CA02C"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Visual 1: LULUS"
            else:
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#FF2A2A"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Visual 1: TIDAK LULUS pada komponen uji {selected_nama_komponen_uji}"
            
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji
        global flags_komponen_uji
        global window_size_x, window_size_y

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K03' OR kode_komponen_uji = 'K04' OR kode_komponen_uji = 'K05' OR kode_komponen_uji = 'K06' OR kode_komponen_uji = 'K07' OR kode_komponen_uji = 'K08' OR kode_komponen_uji = 'K09' OR kode_komponen_uji = 'K14' OR kode_komponen_uji = 'K16' OR kode_komponen_uji = 'K17' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
            flags_komponen_uji = np.ones(db_komponen_uji[0,:].size, dtype='bool')            
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                card = MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height=dp(int(60 * 800 / window_size_y)),
                        )
                self.ids[f'card_komponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                bt_check = MDIconButton(
                        size_hint_x= 0.1, 
                        icon="check-bold", 
                        md_bg_color="#2CA02C",
                        on_press = self.on_komponen_uji_bt_press,
                        id=f'bt_komponen_uji{i}',
                        )                
                self.ids[f'bt_komponen_uji{i}'] = bt_check
                card.add_widget(bt_check)
                
        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_subkomponen_uji(self, kode_komponen_uji, default=True):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}'")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            if(default):
                flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
            else:
                flags_subkomponen_uji = np.zeros(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Subkomponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    # MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.1),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height=dp(int(60 * 800 / window_size_y)),
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                if(default):
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)
                else:
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="cancel", md_bg_color="#FF2A2A",)                           
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        global window_size_x, window_size_y

        try:
            Logger.info(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak Ada Rekomendasi Komentar, Silahkan Isi Komentar Sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(int(60 * 800 / window_size_y)),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Gagal Menampilkan Rekomendasi Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, db_last_data
        global mydb, dt_no_pol, selected_row_komponen_uji

        try:
            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
            result_tb_image_kendaraan = tb_image_kendaraan.fetchone()
            mydb.commit()
            id_image = result_tb_image_kendaraan[0]

            if self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon == "cancel":
                mycursor = mydb.cursor()
                sql = f"UPDATE {TB_UJI} SET lulus_uji = '0' WHERE nopol = '{dt_no_pol}' AND id_image = '{id_image}' "
                mycursor.execute(sql)
                mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data di Database Tabel Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            tb_uji = mydb.cursor()
            tb_uji.execute(f"SELECT id_uji FROM {TB_UJI} WHERE nopol = '{dt_no_pol}' AND kode_kelompok_uji = 'V1' ORDER BY id_uji DESC LIMIT 1")
            result_tb_uji = tb_uji.fetchone()
            mydb.commit()
            id_uji = result_tb_uji[0]
            dt_selected_kode_komponen_uji = db_komponen_uji[1, selected_row_komponen_uji]

            for i in range(db_subkomponen_uji[0,:].size):                
                kode_subkomponen_uji = db_subkomponen_uji[0,i]
                comment_subkomponen_uji = self.ids[f'tx_comment{i}'].text

                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_UJI_DETAIL} (id_uji, hasil, kode_komponen_uji, kode_subkomponen_uji, keterangan) VALUES ('{id_uji}', '{int(flags_subkomponen_uji[i])}','{dt_selected_kode_komponen_uji}','{kode_subkomponen_uji}','{comment_subkomponen_uji}')"
                mycursor.execute(sql)
                mydb.commit()

            toast_msg = f'Berhasil menyimpan data'
            toast(toast_msg)            

            self.open_screen_menu()
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Database Tabel Uji Detail'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectVisual2(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectVisual2, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
    
    def on_enter(self):
        global dt_no_antri, dt_no_pol, dt_no_uji

        self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Visual 2: LULUS"
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Menu Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            selected_row_komponen_uji = row
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_bt_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji, flags_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("bt_komponen_uji",""))
            selected_row_komponen_uji = row
            if(flags_komponen_uji[row]):
                flags_komponen_uji[row] = False
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_komponen_uji[row] = True
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Tombol Icon Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, selected_row_komponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            selected_nama_komponen_uji = db_komponen_uji[2, selected_row_komponen_uji]

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"

            if(np.all(flags_subkomponen_uji == True)):
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#2CA02C"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Visual 2: LULUS"
            else:
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#FF2A2A"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Visual 2: TIDAK LULUS pada komponen uji {selected_nama_komponen_uji}"
            
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji
        global flags_komponen_uji
        global window_size_x, window_size_y

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K10' OR kode_komponen_uji = 'K11' OR kode_komponen_uji = 'K12' OR kode_komponen_uji = 'K13' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
            flags_komponen_uji = np.ones(db_komponen_uji[0,:].size, dtype='bool')            
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                card = MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height=dp(int(60 * 800 / window_size_y)),
                        )
                self.ids[f'card_komponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                bt_check = MDIconButton(
                        size_hint_x= 0.1, 
                        icon="check-bold", 
                        md_bg_color="#2CA02C",
                        on_press = self.on_komponen_uji_bt_press,
                        id=f'bt_komponen_uji{i}',
                        )                
                self.ids[f'bt_komponen_uji{i}'] = bt_check
                card.add_widget(bt_check)
                
        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_subkomponen_uji(self, kode_komponen_uji, default=True):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji
        global window_size_x, window_size_y

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            if(default):
                flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
            else:
                flags_subkomponen_uji = np.zeros(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Subkomponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    # MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.1),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height=dp(int(60 * 800 / window_size_y)),
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                if(default):
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)
                else:
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="cancel", md_bg_color="#FF2A2A",)         
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        global window_size_x, window_size_y

        try:
            Logger.info(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak Ada Rekomendasi Komentar, Silahkan Isi Komentar Sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(int(60 * 800 / window_size_y)),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Gagal Menampilkan Rekomendasi Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, db_last_data
        global mydb, dt_no_pol, selected_row_komponen_uji

        try:
            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
            result_tb_image_kendaraan = tb_image_kendaraan.fetchone()
            mydb.commit()
            id_image = result_tb_image_kendaraan[0]

            if self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon == "cancel":
                mycursor = mydb.cursor()
                sql = f"UPDATE {TB_UJI} SET lulus_uji = '0' WHERE nopol = '{dt_no_pol}' AND id_image = '{id_image}' "
                mycursor.execute(sql)
                mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data di Database Tabel Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            tb_uji = mydb.cursor()
            tb_uji.execute(f"SELECT id_uji FROM {TB_UJI} WHERE nopol = '{dt_no_pol}' AND kode_kelompok_uji = 'V1' ORDER BY id_uji DESC LIMIT 1")
            result_tb_uji = tb_uji.fetchone()
            mydb.commit()
            id_uji = result_tb_uji[0]
            dt_selected_kode_komponen_uji = db_komponen_uji[1, selected_row_komponen_uji]

            for i in range(db_subkomponen_uji[0,:].size):                
                kode_subkomponen_uji = db_subkomponen_uji[0,i]
                comment_subkomponen_uji = self.ids[f'tx_comment{i}'].text

                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_UJI_DETAIL} (id_uji, hasil, kode_komponen_uji, kode_subkomponen_uji, keterangan) VALUES ('{id_uji}', '{int(flags_subkomponen_uji[i])}','{dt_selected_kode_komponen_uji}','{kode_subkomponen_uji}','{comment_subkomponen_uji}')"
                mycursor.execute(sql)
                mydb.commit()

            toast_msg = f'Berhasil menyimpan data'
            toast(toast_msg)      

            self.open_screen_menu()      
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Database Tabel Uji Detail'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectPit(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectPit, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE        
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
    
    def on_enter(self):
        global dt_no_antri, dt_no_pol, dt_no_uji

        self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Kolong: LULUS"
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Menu Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            selected_row_komponen_uji = row
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def on_komponen_uji_bt_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, selected_row_komponen_uji, flags_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("bt_komponen_uji",""))
            selected_row_komponen_uji = row
            if(flags_komponen_uji[row]):
                flags_komponen_uji[row] = False
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_komponen_uji[row] = True
                self.exec_reload_subkomponen_uji(db_komponen_uji[1, row], flags_komponen_uji[row])
                self.ids[f'bt_komponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{row}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Tombol Icon Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}")

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antri, dt_no_pol, dt_no_uji, dt_visual_flag, dt_nama
        global dt_merk, dt_type, dt_jns_kend, dt_jbb, dt_bhn_bkr, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, selected_row_komponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            selected_nama_komponen_uji = db_komponen_uji[2, selected_row_komponen_uji]

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"

            if(np.all(flags_subkomponen_uji == True)):
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "check-bold"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#2CA02C"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Kolong: LULUS"
            else:
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon = "cancel"
                self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].md_bg_color = "#FF2A2A"
                self.ids.lb_info.text = f"No. Antrian: {dt_no_antri}, No. Polisi: {dt_no_pol}, No. Uji: {dt_no_uji} \nStatus Inspeksi Kolong: TIDAK LULUS pada komponen uji {selected_nama_komponen_uji}"
            
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah dari Baris Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji
        global flags_komponen_uji
        global window_size_x, window_size_y

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_kelompok_uji = 'V2' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
            flags_komponen_uji = np.ones(db_komponen_uji[0,:].size, dtype='bool')            
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                card = MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height=dp(int(60 * 800 / window_size_y)),
                        )
                self.ids[f'card_komponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                bt_check = MDIconButton(
                        size_hint_x= 0.1, 
                        icon="check-bold", 
                        md_bg_color="#2CA02C",
                        on_press = self.on_komponen_uji_bt_press,
                        id=f'bt_komponen_uji{i}',
                        )               
                self.ids[f'bt_komponen_uji{i}'] = bt_check
                card.add_widget(bt_check)
                
        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Tabel Komponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_reload_subkomponen_uji(self, kode_komponen_uji, default=True):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji
        global window_size_x, window_size_y

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            if(default):
                flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
            else:
                flags_subkomponen_uji = np.zeros(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Gagal Mengambil Data dari Database Tabel Subkomponen Uji'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Gagal Menghapus Widget'
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height=dp(int(60 * 800 / window_size_y)),
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                if(default):
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)
                else:
                    bt_check = MDIconButton(size_hint_x= 0.1, icon="cancel", md_bg_color="#FF2A2A",)        
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data Tabel Subkomponen Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        global window_size_x, window_size_y

        try:
            Logger.info(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak Ada Rekomendasi Komentar, Silahkan Isi Komentar Sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(int(60 * 800 / window_size_y)),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Gagal Menampilkan Rekomendasi Komentar'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_open_camera(self):
        self.screen_manager.current = 'screen_realtime_pit'

    def exec_save(self):
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji, db_last_data
        global mydb, dt_no_pol, selected_row_komponen_uji

        try:
            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = '{dt_no_pol}' ORDER BY id DESC LIMIT 1")
            result_tb_image_kendaraan = tb_image_kendaraan.fetchone()
            mydb.commit()
            id_image = result_tb_image_kendaraan[0]

            if self.ids[f'bt_komponen_uji{selected_row_komponen_uji}'].icon == "cancel":
                mycursor = mydb.cursor()
                sql = f"UPDATE {TB_UJI} SET lulus_uji = '0' WHERE nopol = '{dt_no_pol}' AND id_image = '{id_image}' "
                mycursor.execute(sql)
                mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal Memperbaharui Data di Database Tabel Uji'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

        try:
            tb_uji = mydb.cursor()
            tb_uji.execute(f"SELECT id_uji FROM {TB_UJI} WHERE nopol = '{dt_no_pol}' AND kode_kelompok_uji = 'V1' ORDER BY id_uji DESC LIMIT 1")
            result_tb_uji = tb_uji.fetchone()
            mydb.commit()
            id_uji = result_tb_uji[0]
            dt_selected_kode_komponen_uji = db_komponen_uji[1, selected_row_komponen_uji]

            for i in range(db_subkomponen_uji[0,:].size):                
                kode_subkomponen_uji = db_subkomponen_uji[0,i]
                comment_subkomponen_uji = self.ids[f'tx_comment{i}'].text

                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_UJI_DETAIL} (id_uji, hasil, kode_komponen_uji, kode_subkomponen_uji, keterangan) VALUES ('{id_uji}', '{int(flags_subkomponen_uji[i])}','{dt_selected_kode_komponen_uji}','{kode_subkomponen_uji}','{comment_subkomponen_uji}')"
                mycursor.execute(sql)
                mydb.commit()

            toast_msg = f'Berhasil menyimpan data'
            toast(toast_msg)            

            self.open_screen_menu()
        except Exception as e:
            toast_msg = f'Gagal Menambahkan Data ke Database Tabel Uji Detail'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 
            
    def exec_cancel(self):
        self.open_screen_menu()

class ScreenRealtimeCctv(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenRealtimeCctv, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)

    def delayed_init(self, dt):
        global rtsp_url_cam_array
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4

        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
        rtsp_url_cam_array = np.array([rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4])
    
    def on_enter(self):
        global window_size_x, window_size_y

        db_camera_list = np.array(["Depan", "Kiri", "Kanan", "Belakang"])
        self.menu_camera_items = [
            {
                "text": f"{db_camera_list[i]}",                   
                "viewclass": "ListItem",
                "height": dp(int(60 * 800 / window_size_y)),
                "on_release": lambda x=i, y=db_camera_list[i]: self.menu_camera_callback(x, y),
            } for i in range(db_camera_list.size)
        ]

        self.menu_camera = MDDropdownMenu(
            caller=self.ids.bt_dropdown_caller,
            items=self.menu_camera_items,
            width_mult=4,
        )

    def on_leave(self):
        self.exec_stop_cctv()

    def menu_camera_callback(self, camera_number, camera_name):
        global dt_selected_camera

        try:
            Logger.info(f"Selected camera number {camera_number}")
            toast(f"Kamera {camera_name} dipilih")
            dt_selected_camera = camera_number

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah Dari Menu Kamera'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_play_cctv(self):
        try:
            self.capture = cv2.VideoCapture(rtsp_url_cam_array[dt_selected_camera])
            # self.capture = cv2.VideoCapture(0)
            Clock.schedule_interval(self.update_frame, 1/30)
        except:
            pass

    def exec_stop_cctv(self):
        try:
            self.capture.release()
            Clock.unschedule(self.update_frame)
        except:
            pass

    def update_frame(self, dt):
        global dt_selected_camera, dt_no_pol

        try:
            ret, frame = self.capture.read()

            if ret:
                # Membalik frame secara vertikal
                # zoom_factor = self.ids.sl_zoom.value
                # x_offs = self.ids.sl_x_offs.value
                # y_offs = self.ids.sl_y_offs.value
                # self.image_cctv = self.zoom_image(frame, zoom_factor, x_offs, y_offs)
                self.image_cctv = self.zoom_image(frame)

                frame = cv2.flip(self.image_cctv, 0)  # 0 untuk membalik secara vertikal
                # OpenCV menggunakan format BGR, ubah ke RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Konversi frame menjadi texture untuk ditampilkan di Kivy
                buf = frame_rgb.tobytes()
                # buf = frame_rgb.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

                # Update widget Image dengan texture baru
                self.ids.image_view.texture = texture
        except:
            pass

    def zoom_image(self, img, zoom_factor=1.0, x_offs=0.0, y_offs=0.0):
        y_size = img.shape[0]
        x_size = img.shape[1]
        # y_size = 600
        # x_size = 600

        # define new boundaries
        # x1 = int(x_offs * x_size)
        # x2 = int(x_size - 0.5 * x_size * (1 - 1 / zoom_factor))
        # y1 = int(y_offs * y_size)
        # y2 = int(y_size - 0.5 * y_size * (1 - 1 / zoom_factor))

        x1 = int(x_offs)
        x2 = int(x_offs + x_size)
        y1 = int(y_offs)
        y2 = int(y_offs + y_size)

        # first crop image then scale
        img_cropped = img[y1:y2, x1:x2]
        return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)

    def center_crop(self, img, crop_width=600, crop_height=600):
        h, w = img.shape[:2]
        
        # Compute center
        center_y, center_x = h // 2, w // 2
        
        # Compute crop boundaries
        start_x = max(0, center_x - crop_width // 2)
        start_y = max(0, center_y - crop_height // 2)
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        # Ensure we don't go out of bounds
        if end_x > w or end_y > h:
            raise ValueError(f"Cannot crop {crop_width}x{crop_height} from image of size {w}x{h}. Image too small.")

        return img[start_y:end_y, start_x:end_x]
    
    def sftp_upload_file(self, local_path, remote_path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASS)
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()

    def sftp_list_files(self, remote_path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASS)
        sftp = ssh.open_sftp()
        files = sftp.listdir(remote_path)
        for file in files:
            Logger.info(file)
        sftp.close()
        ssh.close()

    def exec_save(self):
        global dt_no_antri, dt_sts_uji, dt_no_pol, dt_selected_camera
        
        try:
            # Define base directory: C:\ProgramData\VIIMS
            app_data_root = os.path.join(os.environ['PROGRAMDATA'], 'VIIMS')
            # Define subdirectory: C:\ProgramData\VIIMS\assets\images
            images_dir = os.path.join(app_data_root, 'assets', 'images')
            # Create filename
            filename = f'{dt_no_pol}-{dt_selected_camera + 1}.jpg'
            local_path = os.path.join(images_dir, filename)
            # Ensure the full directory path exists
            os.makedirs(images_dir, exist_ok=True)
            if not os.access(images_dir, os.W_OK):
                raise Exception(f"No write permission in: {images_dir}")

            # Step 1: Get image dimensions
            h, w = self.image_cctv.shape[:2]  # e.g., 1080 x 1280 (height, width)
            # Desired crop size (larger than 600x600 before resize)
            crop_size = 1000
            # Check if image is big enough to crop 1000x1000
            if h < crop_size or w < crop_size:
                Logger.error(f"Gambar terlalu kecil untuk crop {crop_size}x{crop_size}")
                return            
            # Step 2: Center Crop image
            try:
                cropped_img = self.center_crop(self.image_cctv, crop_size, crop_size)
            except ValueError as e:
                Logger.error(f"{self.name}: {e}")
                return
            # Step 3: Resize cropped 1000x1000 → 600x600
            resized_img = cv2.resize(cropped_img, (600, 600), interpolation=cv2.INTER_AREA)
            # Step 4: Save with compression (JPEG quality 75)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
            success = cv2.imwrite(local_path, resized_img, encode_param)
            if not success:
                raise Exception(f"cv2.imwrite failed. Check image data or disk space.")

            # Upload via SFTP
            today = time.strftime("%Y-%m-%d", time.localtime())
            remote_path = f'/var/www/system/storage/app/capture/{today}/{dt_sts_uji}-{dt_no_antri}/{dt_no_pol}-{dt_selected_camera + 1}.jpg'
            self.sftp_upload_file(local_path, remote_path)

            # Success toast
            toast(f'Berhasil menyimpan gambar ke server')

        except Exception as e:
            toast_msg = 'Gagal Menyimpan Gambar ke Server'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, Error: {e}")
        try:
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            image_filename = f'{dt_no_pol}-{dt_selected_camera + 1}.jpg'

            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = %s ORDER BY id DESC LIMIT 1", (dt_no_pol,))
            result = tb_image_kendaraan.fetchone()
            if not result:
                raise Exception("No record found in database to update")
            last_id = result[0]

            # Build dynamic column names
            if dt_selected_camera == 0:
                tgl_col = "tgl_capture"
                gambar_col = "gambar"
            else:
                idx = dt_selected_camera + 1
                tgl_col = f"tgl_capture{idx}"
                gambar_col = f"gambar{idx}"

            # Verify columns exist in table (optional but safe)
            tb_image_kendaraan.execute(f"SHOW COLUMNS FROM {TB_DATA_IMAGE} LIKE '{tgl_col}'")
            if tb_image_kendaraan.fetchone() is None:
                raise Exception(f"Column '{tgl_col}' does not exist in {TB_DATA_IMAGE}")

            # ✅ Safe UPDATE with parameterized query
            sql = f"""
                UPDATE {TB_DATA_IMAGE} 
                SET `{tgl_col}` = %s, `{gambar_col}` = %s 
                WHERE nopol = %s AND id = %s
            """
            tb_image_kendaraan.execute(sql, (now, image_filename, dt_no_pol, last_id))
            mydb.commit()
            
        except Exception as e:
            toast_msg = f'Gagal Menyimpan Data Gambar ke Database Tabel Data Image'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_cancel(self):
        try:
            self.screen_manager.current = 'screen_menu'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

class ScreenRealtimePit(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenRealtimePit, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)
    
    def delayed_init(self, dt):
        global rtsp_url_pit_array
        global rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4
        
        self.ids.lb_title.text = APP_TITLE
        self.ids.lb_subtitle.text = APP_SUBTITLE
        self.ids.img_pemkab.source = f'assets/images/{IMG_LOGO_PEMKAB}'
        self.ids.img_dishub.source = f'assets/images/{IMG_LOGO_DISHUB}'
        self.ids.lb_pemkab.text = LB_PEMKAB
        self.ids.lb_dishub.text = LB_DISHUB
        self.ids.lb_unit.text = LB_UNIT
        self.ids.lb_unit_address.text = LB_UNIT_ADDRESS
        rtsp_url_pit_array = np.array([rtsp_url_pit1, rtsp_url_pit2, rtsp_url_pit3, rtsp_url_pit4])
    
    def on_enter(self):
        global window_size_x, window_size_y

        db_camera_list = np.array(["Depan", "Kiri", "Kanan", "Belakang"])
        self.menu_camera_items = [
            {
                "text": f"{db_camera_list[i]}",                   
                "viewclass": "ListItem",
                "height": dp(int(60 * 800 / window_size_y)),
                "on_release": lambda x=i, y=db_camera_list[i]: self.menu_camera_callback(x, y),
            } for i in range(db_camera_list.size)
        ]

        self.menu_camera = MDDropdownMenu(
            caller=self.ids.bt_dropdown_caller,
            items=self.menu_camera_items,
            width_mult=4,
        )

    def on_leave(self):
        self.exec_stop_cctv()

    def menu_camera_callback(self, camera_number, camera_name):
        global dt_selected_camera

        try:
            Logger.info(f"Selected camera number {camera_number}")
            toast(f"Kamera {camera_name} dipilih")
            dt_selected_camera = camera_number

        except Exception as e:
            toast_msg = f'Gagal Mengeksekusi Perintah Dari Menu Kamera'
            toast(toast_msg)  
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def exec_play_cctv(self):
        try:
            self.capture = cv2.VideoCapture(rtsp_url_pit_array[dt_selected_camera])
            # self.capture = cv2.VideoCapture(0)
            Clock.schedule_interval(self.update_frame, 1/30)
        except:
            pass

    def exec_stop_cctv(self):
        try:
            self.capture.release()
            Clock.unschedule(self.update_frame)
        except:
            pass

    def update_frame(self, dt):
        global dt_selected_camera, dt_no_pol

        try:
            ret, frame = self.capture.read()

            if ret:
                # Membalik frame secara vertikal
                zoom_factor = self.ids.sl_zoom.value
                x_offs = self.ids.sl_x_offs.value
                y_offs = self.ids.sl_y_offs.value
                self.image_cctv = self.zoom_image(frame, zoom_factor, x_offs, y_offs)

                frame = cv2.flip(self.image_cctv, 0)  # 0 untuk membalik secara vertikal
                # OpenCV menggunakan format BGR, ubah ke RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Konversi frame menjadi texture untuk ditampilkan di Kivy
                buf = frame_rgb.tobytes()
                # buf = frame_rgb.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

                # Update widget Image dengan texture baru
                self.ids.image_view.texture = texture
        except:
            pass

    def zoom_image(self, img, zoom_factor=1.0, x_offs=0.0, y_offs=0.0):
        y_size = img.shape[0]
        x_size = img.shape[1]
        # y_size = 600
        # x_size = 600

        # define new boundaries
        x1 = int(x_offs * x_size)
        x2 = int(x_size - 0.5 * x_size * (1 - 1 / zoom_factor))
        y1 = int(y_offs * y_size)
        y2 = int(y_size - 0.5 * y_size * (1 - 1 / zoom_factor))

        # first crop image then scale
        img_cropped = img[y1:y2, x1:x2]
        return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)

    def center_crop(self, img, crop_width=600, crop_height=600):
        h, w = img.shape[:2]
        
        # Compute center
        center_y, center_x = h // 2, w // 2
        
        # Compute crop boundaries
        start_x = max(0, center_x - crop_width // 2)
        start_y = max(0, center_y - crop_height // 2)
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        # Ensure we don't go out of bounds
        if end_x > w or end_y > h:
            raise ValueError(f"Cannot crop {crop_width}x{crop_height} from image of size {w}x{h}. Image too small.")

        return img[start_y:end_y, start_x:end_x]
        
    def sftp_upload_file(self, local_path, remote_path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASS)
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()

    def sftp_list_files(self, remote_path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASS)
        sftp = ssh.open_sftp()
        files = sftp.listdir(remote_path)
        for file in files:
            Logger.info(file)
        sftp.close()
        ssh.close()
        
    def exec_save(self):
        global dt_no_antri, dt_sts_uji, dt_no_pol, dt_selected_camera
        
        try:
            # Define base directory: C:\ProgramData\VIIMS
            app_data_root = os.path.join(os.environ['PROGRAMDATA'], 'VIIMS')
            # Define subdirectory: C:\ProgramData\VIIMS\assets\images
            images_dir = os.path.join(app_data_root, 'assets', 'images')
            # Create filename
            filename = f'{dt_no_pol}-{dt_selected_camera + 1}.jpg'
            local_path = os.path.join(images_dir, filename)
            # Ensure the full directory path exists
            os.makedirs(images_dir, exist_ok=True)
            if not os.access(images_dir, os.W_OK):
                raise Exception(f"No write permission in: {images_dir}")

            # Step 1: Get image dimensions
            h, w = self.image_cctv.shape[:2]  # e.g., 1080 x 1280 (height, width)
            # Desired crop size (larger than 600x600 before resize)
            crop_size = 1000
            # Check if image is big enough to crop 1000x1000
            if h < crop_size or w < crop_size:
                Logger.error(f"Gambar terlalu kecil untuk crop {crop_size}x{crop_size}")
                return            
            # Step 2: Center Crop image
            try:
                cropped_img = self.center_crop(self.image_cctv, crop_size, crop_size)
            except ValueError as e:
                Logger.error(f"{self.name}: {e}")
                return
            # Step 3: Resize cropped 1000x1000 → 600x600
            resized_img = cv2.resize(cropped_img, (600, 600), interpolation=cv2.INTER_AREA)
            # Step 4: Save with compression (JPEG quality 75)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
            success = cv2.imwrite(local_path, resized_img, encode_param)
            if not success:
                raise Exception(f"cv2.imwrite failed. Check image data or disk space.")

            # Upload via SFTP
            today = time.strftime("%Y-%m-%d", time.localtime())
            remote_path = f'/var/www/system/storage/app/capture/{today}/{dt_sts_uji}-{dt_no_antri}/{dt_no_pol}-pit-{dt_selected_camera + 1}.jpg'
            self.sftp_upload_file(local_path, remote_path)

            # Success toast
            toast(f'Berhasil menyimpan gambar ke server')

        except Exception as e:
            toast_msg = 'Gagal Menyimpan Gambar ke Server'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, Error: {e}")

        try:
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            image_filename = f'{dt_no_pol}-{dt_selected_camera + 1}.jpg'

            tb_image_kendaraan = mydb.cursor()
            tb_image_kendaraan.execute(f"SELECT id FROM {TB_DATA_IMAGE} WHERE nopol = %s ORDER BY id DESC LIMIT 1", (dt_no_pol,))
            result = tb_image_kendaraan.fetchone()
            if not result:
                raise Exception("No record found in database to update")
            last_id = result[0]

            # Build dynamic column names
            idx = dt_selected_camera + 5
            tgl_col = f"tgl_capture{idx}"
            gambar_col = f"gambar{idx}"

            # Verify columns exist in table (optional but safe)
            tb_image_kendaraan.execute(f"SHOW COLUMNS FROM {TB_DATA_IMAGE} LIKE '{tgl_col}'")
            if tb_image_kendaraan.fetchone() is None:
                raise Exception(f"Column '{tgl_col}' does not exist in {TB_DATA_IMAGE}")

            # Safe UPDATE with parameterized query
            sql = f"""
                UPDATE {TB_DATA_IMAGE} 
                SET `{tgl_col}` = %s, `{gambar_col}` = %s 
                WHERE nopol = %s AND id = %s
            """
            tb_image_kendaraan.execute(sql, (now, image_filename, dt_no_pol, last_id))
            mydb.commit()

        except Exception as e:
            toast_msg = f'Gagal Menyimpan Data Gambar ke Database Tabel Data Image'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_cancel(self):
        try:
            self.screen_manager.current = 'screen_menu'

        except Exception as e:
            toast_msg = f'Gagal Berpindah ke Halaman Awal'
            toast(toast_msg)
            Logger.error(f"{self.name}: {toast_msg}, {e}") 

class ListItem(OneLineListItem):
    list_text = StringProperty()

class RootScreen(ScreenManager):
    pass             

class VisualInspectionApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.on_window_resize)

    def build(self):
        global window_size_x, window_size_y
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.icon = 'assets/images/logo-load-app.png'
        window_size_y = Window.size[0]
        window_size_x = Window.size[1]
        self.set_dynamic_fonts(Window.size)

        LabelBase.register(
            name="Orbitron-Regular",
            fn_regular="assets/fonts/Orbitron-Regular.ttf")
        
        LabelBase.register(
            name="Draco",
            fn_regular="assets/fonts/Draco.otf")        

        LabelBase.register(
            name="Recharge",
            fn_regular="assets/fonts/Recharge.otf") 
        
        theme_font_styles.append('H1')
        self.theme_cls.font_styles["H1"] = [
            "Orbitron-Regular", 64, False, 0.15]       

        theme_font_styles.append('H2')
        self.theme_cls.font_styles["H2"] = [
            "Orbitron-Regular", 32, False, 0.15] 
        
        theme_font_styles.append('H4')
        self.theme_cls.font_styles["H4"] = [
            "Recharge", 30, False, 0.15] 

        theme_font_styles.append('H5')
        self.theme_cls.font_styles["H5"] = [
            "Recharge", 20, False, 0.15] 

        theme_font_styles.append('H6')
        self.theme_cls.font_styles["H6"] = [
            "Recharge", 16, False, 0.15] 

        theme_font_styles.append('Subtitle1')
        self.theme_cls.font_styles["Subtitle1"] = [
            "Recharge", 11, False, 0.15] 

        theme_font_styles.append('Body1')
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", 10, False, 0.15] 
        
        theme_font_styles.append('Button')
        self.theme_cls.font_styles["Button"] = [
            "Recharge", 9, False, 0.15] 

        theme_font_styles.append('Caption')
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", 8, False, 0.15]       
        
        Window.fullscreen = 'auto'
        Builder.load_file('main.kv')
        return RootScreen()

    def on_window_resize(self, window, width, height):
        Logger.info(f"Window size: {width}x{height}")
        self.set_dynamic_fonts((width, height))
        self.refresh_all_fonts()

    def refresh_all_fonts(self):
        # Refresh fonts for all screens in the ScreenManager
        if hasattr(self, 'root') and hasattr(self.root, 'screens'):
            for screen in self.root.screens:
                self.refresh_fonts(screen)

    def refresh_fonts(self, widget):
        from kivymd.uix.label import MDLabel
        if isinstance(widget, MDLabel):
            original_style = widget.font_style
            temp_style = "Body1" if original_style != "Body1" else "H6"
            widget.font_style = temp_style
            widget.font_style = original_style
        if hasattr(widget, 'children'):
            for child in widget.children:
                self.refresh_fonts(child)

    def set_dynamic_fonts(self, size):
        try:
            screen_size_x = Window.system_size[0]
            screen_size_y = Window.system_size[1]
        except AttributeError:
            screen_size_x = Window._get_system_size()[0]
            screen_size_y = Window._get_system_size()[1]
        font_size_l = np.array([64, 32, 30, 20, 16, 11, 10, 9, 8])
        scale = min(screen_size_x / 1920, screen_size_y / 1080)
        font_size = np.round(font_size_l * scale, 0)
        Logger.info(f"Font resized: {font_size_l} to {font_size}")
        self.theme_cls.font_styles["H1"] = [
            "Orbitron-Regular", font_size[0], False, 0.15]
        self.theme_cls.font_styles["H2"] = [
            "Orbitron-Regular", font_size[1], False, 0.15]
        self.theme_cls.font_styles["H4"] = [
            "Recharge", font_size[2], False, 0.15]
        self.theme_cls.font_styles["H5"] = [
            "Recharge", font_size[3], False, 0.15]
        self.theme_cls.font_styles["H6"] = [
            "Recharge", font_size[4], False, 0.15]
        self.theme_cls.font_styles["Subtitle1"] = [
            "Recharge", font_size[5], False, 0.15]
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", font_size[6], False, 0.15]
        self.theme_cls.font_styles["Button"] = [
            "Recharge", font_size[7], False, 0.15]
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", font_size[8], False, 0.15]       

        if hasattr(self, 'root'):
            self.refresh_fonts(self.root)

if __name__ == '__main__':
    VisualInspectionApp().run()