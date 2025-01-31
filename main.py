from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics.texture import Texture
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineListItem, OneLineIconListItem, BaseListItem
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.app import MDApp
import os, sys, time, datetime, numpy as np
import configparser, hashlib, mysql.connector, paramiko
import cv2
from pymodbus.client import ModbusTcpClient

colors = {
    "Red"   : {"A200": "#FF2A2A","A500": "#FF8080","A700": "#FFD5D5",},
    "Gray"  : {"200": "#CCCCCC","500": "#ECECEC","700": "#F9F9F9",},
    "Blue"  : {"200": "#4471C4","500": "#5885D8","700": "#6C99EC",},
    "Green" : {"200": "#2CA02C","500": "#2DB97F", "700": "#D5FFD5",},
    "Yellow": {"200": "#ffD42A","500": "#ffE680","700": "#fff6D5",},

    "Light" : {"StatusBar": "E0E0E0","AppBar": "#202020","Background": "#EEEEEE","CardsDialogs": "#FFFFFF","FlatButtonDown": "#CCCCCC","Text": "#000000",},
    "Dark"  : {"StatusBar": "101010","AppBar": "#E0E0E0","Background": "#111111","CardsDialogs": "#222222","FlatButtonDown": "#DDDDDD","Text": "#FFFFFF",},
}

if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(os.path.abspath(__file__))
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(app_path, 'config.ini')
print(f"Path config.ini: {config_path}")

config = configparser.ConfigParser()
config.read(config_path)

DB_HOST = config['mysql']['DB_HOST']
DB_USER = config['mysql']['DB_USER']
DB_PASSWORD = config['mysql']['DB_PASSWORD']
DB_NAME = config['mysql']['DB_NAME']
TB_DATA = config['mysql']['TB_DATA']
TB_USER = config['mysql']['TB_USER']
TB_MERK = config['mysql']['TB_MERK']
TB_BAHAN_BAKAR = config['mysql']['TB_BAHAN_BAKAR']
TB_WARNA = config['mysql']['TB_WARNA']
TB_DAFTAR_BERKALA = config['mysql']['TB_DAFTAR_BERKALA']
TB_DAFTAR_BARU = config['mysql']['TB_DAFTAR_BARU']
TB_DATA_MASTER = config['mysql']['TB_DATA_MASTER']
TB_DATA_IMAGE = config['mysql']['TB_DATA_IMAGE']
TB_KOMPONEN_UJI = config['mysql']['TB_KOMPONEN_UJI']
TB_SUBKOMPONEN_UJI = config['mysql']['TB_SUBKOMPONEN_UJI']
TB_KOMENTAR_UJI = config['mysql']['TB_KOMENTAR_UJI']
TB_UJI = config['mysql']['TB_UJI']
TB_UJI_DETAIL = config['mysql']['TB_UJI_DETAIL']

RTSP_USER = config['setting']['RTSP_USER']
RTSP_PASSWORD = config['setting']['RTSP_PASSWORD']
RTSP_IP_DISPLAY_CAM1 = config['setting']['RTSP_IP_DISPLAY_CAM1']
RTSP_IP_DISPLAY_CAM2 = config['setting']['RTSP_IP_DISPLAY_CAM2']
RTSP_IP_DISPLAY_CAM3 = config['setting']['RTSP_IP_DISPLAY_CAM3']
RTSP_IP_DISPLAY_CAM4 = config['setting']['RTSP_IP_DISPLAY_CAM4']
RTSP_IP_PIT_CAM1 = config['setting']['RTSP_IP_PIT_CAM1']
RTSP_IP_PIT_CAM2 = config['setting']['RTSP_IP_PIT_CAM2']
RTSP_IP_PIT_CAM3 = config['setting']['RTSP_IP_PIT_CAM3']
RTSP_IP_PIT_CAM4 = config['setting']['RTSP_IP_PIT_CAM4']

FTP_HOST = str(config['setting']['FTP_HOST'])
FTP_USER = str(config['setting']['FTP_USER'])
FTP_PASSWORD = str(config['setting']['FTP_PASSWORD'])

MODBUS_IP_PLC = config['setting']['MODBUS_IP_PLC']

COUNT_STARTING = 3
COUNT_ACQUISITION = 4
TIME_OUT = 500

# rtsp_url_cam1 = 'rtsp://admin:TRBintegrated202@192.168.70.64:554/Streaming/Channels/101'
rtsp_url_cam1 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_DISPLAY_CAM1}:554/Streaming/Channels/101'
rtsp_url_cam2 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_DISPLAY_CAM2}:554/Streaming/Channels/101'
rtsp_url_cam3 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_DISPLAY_CAM3}:554/Streaming/Channels/101'
rtsp_url_cam4 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_DISPLAY_CAM4}:554/Streaming/Channels/101'

rtsp_url_pit1 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_PIT_CAM1}:554/Streaming/Channels/101'
rtsp_url_pit2 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_PIT_CAM2}:554/Streaming/Channels/101'
rtsp_url_pit3 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_PIT_CAM3}:554/Streaming/Channels/101'
rtsp_url_pit4 = f'rtsp://{RTSP_USER}:{RTSP_PASSWORD}@{RTSP_IP_PIT_CAM4}:554/Streaming/Channels/101'

dt_check_flag = 0
dt_check_user = 1
dt_check_post = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))

dt_dash_pendaftaran = 0
dt_dash_belum_uji = 0
dt_dash_sudah_uji = 0

dt_check_body_flag = 0
dt_check_body_image = ""
dt_check_chassis_flag = 0
dt_check_chassis_image = ""
dt_check_engine_flag = 0
dt_check_engine_image = ""
dt_check_handle_flag = 0
dt_check_handle_image = ""
dt_check_wiper_flag = 0
dt_check_wiper_image = ""
dt_check_windshield_flag = 0
dt_check_windshield_image = ""
dt_check_headlight_flag = 0
dt_check_headlight_image = ""
dt_check_signallight_flag = 0
dt_check_signallight_image = ""

flag_no_uji = True
flag_no_pol = True
flag_chasis = True
flag_no_mesin = True
flag_jenis_kendaraan = True
flag_merk = True
flag_nama = True
flag_alamat = True

dt_foto_user = ""
dt_user = ""
dt_no_antrian = ""
dt_no_pol = ""
dt_no_uji = ""
dt_status_uji = ""
dt_nama = ""
dt_merk = ""
dt_type = ""
dt_jenis_kendaraan = ""
dt_jbb = ""
dt_bahan_bakar = ""
dt_warna = ""
dt_chasis = ""
dt_no_mesin = ""

modbus_client = ModbusTcpClient(MODBUS_IP_PLC)

flag_conn_stat = False
flag_gate = False
selected_camera = 0

class ScreenHome(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenHome, self).__init__(**kwargs)

    def on_enter(self):
        Clock.schedule_interval(self.regular_update_carousel, 3)

    def on_leave(self):
        Clock.unschedule(self.regular_update_carousel)

    def regular_update_carousel(self, dt):
        try:
            self.ids.carousel.index += 1
            
        except Exception as e:
            toast_msg = f'Error Update Display: {e}'
            toast(toast_msg)                

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)  

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)    

class ScreenLogin(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenLogin, self).__init__(**kwargs)

    def exec_cancel(self):
        try:
            self.ids.tx_username.text = ""
            self.ids.tx_password.text = ""    

        except Exception as e:
            toast_msg = f'Error Login: {e}'

    def exec_login(self):
        global mydb, db_users
        global dt_check_user, dt_user, dt_foto_user

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
            #if invalid
            if myresult == 0:
                toast('Gagal Masuk, Nama Pengguna atau Password Salah')
            #else, if valid
            else:
                toast_msg = f'Berhasil Masuk, Selamat Datang {myresult[1]}'
                toast(toast_msg)
                dt_check_user = myresult[0]
                dt_user = myresult[1]
                dt_foto_user = myresult[4]
                self.ids.tx_username.text = ""
                self.ids.tx_password.text = "" 
                self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Login: {e}'
            toast(toast_msg)        
            toast('Gagal Masuk, Nama Pengguna atau Password Salah')

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)    

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)     

class ScreenMain(MDScreen):   
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_update_display, 1)

    def on_enter(self):
        self.exec_reload_database()
        self.exec_reload_table()

    def sftp_upload_file(local_path, remote_path):
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the SFTP server
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASSWORD)
        # Open an SFTP session
        sftp = ssh.open_sftp()
        # Upload the file
        sftp.put(local_path, remote_path)
        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    def sftp_list_files(remote_path):
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the SFTP server
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASSWORD)
        # Open an SFTP session
        sftp = ssh.open_sftp()
        # List files in the remote directory
        files = sftp.listdir(remote_path)
        # Print the list of files
        for file in files:
            print(file)
        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()
        
    def sftp_make_dir(self, remote_path):
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the SFTP server
        ssh.connect(FTP_HOST, username = FTP_USER, password = FTP_PASSWORD)
        # Open an SFTP session
        sftp = ssh.open_sftp()
        try:
            sftp.chdir(remote_path)  # Test if remote_path exists
        except IOError:
            sftp.mkdir(remote_path)  # Create remote_path
            sftp.chdir(remote_path)
        sftp.close()
        ssh.close()
                
    def on_antrian_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama, dt_status_uji
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_antrian, db_merk, db_bahan_bakar, db_warna

        try:
            row = int(str(instance.id).replace("card_antrian",""))
            dt_no_antrian           = f"{db_antrian[0, row]}"
            dt_no_pol               = f"{db_antrian[1, row]}"
            dt_no_uji               = f"{db_antrian[2, row]}"
            dt_status_uji           = 'Berkala' if db_antrian[3, row] == 'B' else 'Uji Ulang' if (db_antrian[3, row]) == 'U' else 'Baru' if (db_antrian[3, row]) == 'BR' else 'Numpang Uji' if (db_antrian[3, row]) == 'NB' else 'Mutasi'
            dt_merk                 = '-' if db_antrian[4, row] == None else f"{db_merk[np.where(db_merk == db_antrian[4, row])[0][0],1]}" 
            dt_type                 = f"{db_antrian[5, row]}"
            dt_jenis_kendaraan      = f"{db_antrian[6, row]}"
            dt_jbb                  = f"{db_antrian[7, row]}"
            dt_bahan_bakar          = '-' if db_antrian[8, row] == None else f"{db_bahan_bakar[np.where(db_bahan_bakar == db_antrian[8, row])[0][0],1]}" 
            dt_warna                = '-' if db_antrian[9, row] == None else f"{db_warna[np.where(db_warna == db_antrian[9, row])[0][0],1]}" 
            dt_check_flag           = 'Lulus' if (int(db_antrian[10, i]) == 2) else 'Tidak Lulus' if (int(db_antrian[10, i]) == 1) else 'Belum Tes'
                      
            self.exec_start()

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Row: {e}'
            toast(toast_msg)   

    def regular_update_display(self, dt):
        global flag_conn_stat
        global dt_user, dt_no_antrian, dt_no_pol, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_chasis, dt_merk, dt_type, dt_no_mesin
        global dt_check_flag, dt_check_user, dt_check_post, dt_foto_user
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            screen_home = self.screen_manager.get_screen('screen_home')
            screen_login = self.screen_manager.get_screen('screen_login')
            screen_menu = self.screen_manager.get_screen('screen_menu')
            screen_inspect_pit = self.screen_manager.get_screen('screen_inspect_pit')
            screen_inspect_id = self.screen_manager.get_screen('screen_inspect_id')
            screen_inspect_visual2 = self.screen_manager.get_screen('screen_inspect_visual2')
            screen_inspect_visual = self.screen_manager.get_screen('screen_inspect_visual')
            screen_realtime_cctv = self.screen_manager.get_screen('screen_realtime_cctv')

            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_home.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_home.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_login.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_login.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_menu.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_menu.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_id.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_id.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_visual2.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_visual2.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_visual.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_visual.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_pit.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_pit.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_realtime_cctv.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_realtime_cctv.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_dash_pendaftaran.text = str(dt_dash_pendaftaran)
            self.ids.lb_dash_belum_uji.text = str(dt_dash_belum_uji)
            self.ids.lb_dash_sudah_uji.text = str(dt_dash_sudah_uji)

            screen_menu.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_menu.ids.lb_no_pol.text = str(dt_no_pol)
            screen_menu.ids.lb_no_uji.text = str(dt_no_uji)

            if(not flag_conn_stat):
                self.ids.lb_comm.color = colors['Red']['A200']
                self.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_home.ids.lb_comm.color = colors['Red']['A200']
                screen_home.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_login.ids.lb_comm.color = colors['Red']['A200']
                screen_login.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_menu.ids.lb_comm.color = colors['Red']['A200']
                screen_menu.ids.lb_comm.text = 'PLC Tidak Terhubung'

            else:
                self.ids.lb_comm.color = colors['Blue']['200']
                self.ids.lb_comm.text = 'PLC Terhubung'
                screen_home.ids.lb_comm.color = colors['Blue']['200']
                screen_home.ids.lb_comm.text = 'PLC Terhubung'
                screen_login.ids.lb_comm.color = colors['Blue']['200']
                screen_login.ids.lb_comm.text = 'PLC Terhubung'
                screen_menu.ids.lb_comm.color = colors['Blue']['200']
                screen_menu.ids.lb_comm.text = 'PLC Terhubung'
            
            self.ids.bt_new_inspect.disabled = False if dt_user != '' else True
            self.ids.bt_logout.disabled = False if dt_user != '' else True

            self.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_home.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_login.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_menu.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_id.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_visual2.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_visual.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_pit.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_realtime_cctv.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'

            if dt_user != '':
                self.ids.img_user.source = f'https://dishub.sorongkab.go.id/ujikir/foto_user/{dt_foto_user}'
                screen_home.ids.img_user.source = f'https://dishub.sorongkab.go.id/ujikir/foto_user/{dt_foto_user}'
                screen_login.ids.img_user.source = f'https://dishub.sorongkab.go.id/ujikir/foto_user/{dt_foto_user}'
            else:
                self.ids.img_user.source = 'assets/images/icon-login.png'
                screen_home.ids.img_user.source = 'assets/images/icon-login.png'
                screen_login.ids.img_user.source = 'assets/images/icon-login.png'               

        except Exception as e:
            toast_msg = f'Error Update Display: {e}'
            toast(toast_msg)                

    def regular_update_connection(self, dt):
        global flag_conn_stat

        try:
            modbus_client.connect()
            flag_conn_stat = modbus_client.connected
            modbus_client.close()     
            
        except Exception as e:
            toast_msg = f'{e}'
            toast(toast_msg)   
            flag_conn_stat = False

    def regular_get_data(self, dt):
        global side_slip_val, axle_load_l_val, axle_load_r_val, speed_val
        try:
            if flag_conn_stat:
                modbus_client.connect()
                side_slip_registers = modbus_client.read_holding_registers(1612, 1, slave=1) #V1100
                axle_load_registers = modbus_client.read_holding_registers(1712, 2, slave=1) #V1200 - V1201
                speed_registers = modbus_client.read_holding_registers(1812, 1, slave=1) #V1360
                modbus_client.close()

                side_slip_val = side_slip_registers.registers[0] / 10
                axle_load_l_val = axle_load_registers.registers[0]
                axle_load_r_val = axle_load_registers.registers[1]
                speed_val = speed_registers.registers[0]
                
        except Exception as e:
            toast_msg = f'Error GEt Data: {e}'
            toast(toast_msg)     

    def exec_reload_database(self):
        global mydb
        try:
            mydb = mysql.connector.connect(host = DB_HOST,user = DB_USER,password = DB_PASSWORD,database = DB_NAME)
        except Exception as e:
            toast_msg = f'Error Initiate Database: {e}'
            toast(toast_msg)   

    def exec_reload_table(self):
        global mydb, db_antrian, db_merk, db_bahan_bakar, db_warna
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            tb_antrian = mydb.cursor()
            tb_antrian.execute(f"SELECT noantrian, nopol, nouji, statusuji, merk, type, idjeniskendaraan, jbb, bahan_bakar, warna, check_flag FROM {TB_DATA}")
            result_tb_antrian = tb_antrian.fetchall()
            mydb.commit()
            db_antrian = np.array(result_tb_antrian).T
            db_pendaftaran = np.array(result_tb_antrian)
            dt_dash_pendaftaran = db_pendaftaran[:,10].size
            dt_dash_belum_uji = np.where(db_pendaftaran[:,10] == 0)[0].size
            dt_dash_sudah_uji = np.where(db_pendaftaran[:,10] == 1)[0].size

            tb_merk = mydb.cursor()
            tb_merk.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
            result_tb_merk = tb_merk.fetchall()
            mydb.commit()
            db_merk = np.array(result_tb_merk)

            tb_bahan_bakar = mydb.cursor()
            tb_bahan_bakar.execute(f"SELECT ID, DESCRIPTION FROM {TB_BAHAN_BAKAR}")
            result_tb_bahan_bakar = tb_bahan_bakar.fetchall()
            mydb.commit()
            db_bahan_bakar = np.array(result_tb_bahan_bakar)

            tb_warna = mydb.cursor()
            tb_warna.execute(f"SELECT id_warna, nama FROM {TB_WARNA}")
            result_tb_warna = tb_warna.fetchall()
            mydb.commit()
            db_warna = np.array(result_tb_warna)
        except Exception as e:
            toast_msg = f'Error Fetch Database: {e}'
            print(toast_msg)
        
        try:
            layout_list = self.ids.layout_list
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
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
                        MDLabel(text=f"{db_antrian[5, i]}", size_hint_x= 0.12),
                        MDLabel(text=f"{db_antrian[6, i]}", size_hint_x= 0.15),
                        MDLabel(text=f"{db_antrian[7, i]}", size_hint_x= 0.05),
                        MDLabel(text='-' if db_antrian[8, i] == None else f"{db_bahan_bakar[np.where(db_bahan_bakar == db_antrian[8, i])[0][0],1]}" , size_hint_x= 0.08),
                        MDLabel(text='-' if db_antrian[9, i] == None else f"{db_warna[np.where(db_warna == db_antrian[9, i])[0][0],1]}" , size_hint_x= 0.05),
                        MDLabel(text='Lulus' if (int(db_antrian[10, i]) == 2) else 'Tidak Lulus' if (int(db_antrian[10, i]) == 1) else 'Belum Tes', size_hint_x= 0.05),

                        ripple_behavior = True,
                        on_press = self.on_antrian_row_press,
                        padding = 20,
                        id=f"card_antrian{i}",
                        size_hint_y=None,
                        height="60dp",
                        )
                    )

        except Exception as e:
            toast_msg = f'Error Reload Table: {e}'
            print(toast_msg)

    def exec_new_inspect(self):
        try:
            self.screen_manager.current = 'screen_inspect_new'

        except Exception as e:
            toast_msg = f'Error Navigate to New Inspection Screen: {e}'
            toast(toast_msg)  

    def exec_start(self):
        global dt_check_flag, dt_no_antrian, dt_user

        if (dt_user != ''):
            if (dt_check_flag == 'Belum Tes'):
                self.open_screen_menu()
            else:
                toast(f'No. Antrian {dt_no_antrian} Sudah Tes')
        else:
            toast(f'Silahkan Login Untuk Melakukan Pengujian')
            

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_logout(self):
        global dt_user

        dt_user = ""
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)     

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)   

class ScreenMenu(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenMenu, self).__init__(**kwargs)

    def exec_barrier_open(self):
        global flag_conn_stat
        global flag_gate

        if(flag_conn_stat):
            flag_gate = True
        else:
            toast("Tidak bisa membuka Portal karena PLC tidak terhubung") 

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3072, flag_gate, slave=1) #M0
                modbus_client.close()
        except:
            toast("Error send exec_gate_open data to PLC Slave") 

    def exec_barrier_close(self):
        global flag_conn_stat
        global flag_gate

        if(flag_conn_stat):
            flag_gate = False
        else:
            toast("Tidak bisa menutup Portal karena PLC tidak terhubung") 

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3073, not flag_gate, slave=1) #M1
                modbus_client.close()
        except:
            toast("Error send exec_gate_close data to PLC Slave") 

    def exec_barrier_stop(self):
        global flag_conn_stat

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3072, False, slave=1) #M0
                modbus_client.write_coil(3073, False, slave=1) #M1
                modbus_client.close()
        except:
            toast("Error send exec_gate_stop data to PLC Slave") 

    def exec_inspect_id(self):
        try:
            self.screen_manager.current = 'screen_inspect_id'

        except Exception as e:
            toast_msg = f'Error Navigate to Identity Inspection Screen: {e}'
            toast(toast_msg) 

    def exec_capture(self):
        try:
            self.screen_manager.current = 'screen_realtime_cctv'

        except Exception as e:
            toast_msg = f'Error Navigate to Play Detect: {e}'
            toast(toast_msg)    

    def exec_inspect_visual(self):
        try:
            self.screen_manager.current = 'screen_inspect_visual'

        except Exception as e:
            toast_msg = f'Error Navigate to Visual Inspection Screen: {e}'
            toast(toast_msg)    

    def exec_inspect_visual2(self):
        try:
            self.screen_manager.current = 'screen_inspect_visual2'

        except Exception as e:
            toast_msg = f'Error Navigate to Visual Inspection Screen: {e}'
            toast(toast_msg)    

    def exec_inspect_pit(self):
        try:
            self.screen_manager.current = 'screen_inspect_pit'

        except Exception as e:
            toast_msg = f'Error Navigate to Pit Inspection Screen: {e}'
            toast(toast_msg)    

    def exec_cancel(self):
        self.screen_manager.current = 'screen_main'

class ScreenInspectNew(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenInspectNew, self).__init__(**kwargs)

    def exec_cancel(self):
        try:
            self.ids.tx_nopol.text = ""  

        except Exception as e:
            toast_msg = f'Error find data: {e}'
            toast(toast_msg) 

    def exec_register(self):
        global mydb, db_users, dt_status_uji
        global dt_check_user, dt_user, dt_foto_user
        global dt_dash_pendaftaran

        try:
            dt_nopol_find = self.ids.tx_nopol.text
            dt_nouji_find = self.ids.tx_nouji.text

            mycursor = mydb.cursor()

            if dt_nopol_find != "" and dt_nouji_find == "":
                mycursor.execute(f"SELECT NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, SUBJENIS_ID, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, DAYAMOTOR, TGL_LASTUJI, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah FROM {TB_DATA_MASTER} WHERE NOPOL = '{dt_nopol_find}' ")
            elif dt_nouji_find != "":
                mycursor.execute(f"SELECT NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, SUBJENIS_ID, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, DAYAMOTOR, TGL_LASTUJI, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah FROM {TB_DATA_MASTER} WHERE NOUJI = '{dt_nouji_find}' ")
            elif dt_nouji_find == "" and dt_nopol_find == "":
                toast("Silahkan isi Nomor Uji atau Nomor Polisi")
            myresult = mycursor.fetchone()
            mydb.commit()
            db_pendaftaran = np.array(myresult).T
            dt_no_uji = db_pendaftaran[0]
            dt_new_no_uji = db_pendaftaran[1]
            dt_no_wilayah = db_pendaftaran[2]
            dt_no_kendaraan = db_pendaftaran[3]
            dt_no_plat = db_pendaftaran[4]
            dt_nopol = db_pendaftaran[5]
            dt_nama = db_pendaftaran[6]
            dt_no_hp = db_pendaftaran[7]
            dt_alamat = db_pendaftaran[8]
            dt_izin_id = db_pendaftaran[9]
            dt_wilayah = db_pendaftaran[10]
            dt_provinsi = db_pendaftaran[11]
            dt_kabupaten_kota = db_pendaftaran[12]
            dt_kecamatan = db_pendaftaran[13]
            dt_merk_id = db_pendaftaran[14]
            dt_subjenis_id = db_pendaftaran[15]
            dt_type = db_pendaftaran[16]
            dt_tahun_buat = db_pendaftaran[17]
            dt_silinder = db_pendaftaran[18]
            dt_warna = db_pendaftaran[19]
            dt_chasis = db_pendaftaran[20]
            dt_mesin = db_pendaftaran[21]
            dt_warna_plat = db_pendaftaran[22]
            dt_bahan_bakar = db_pendaftaran[23]
            dt_jbb = db_pendaftaran[24]
            dt_daya_motor = db_pendaftaran[25]
            dt_tgl_last_uji = str(db_pendaftaran[26])
            dt_status_penerbitan = db_pendaftaran[27]
            dt_jenis_kendaraan = db_pendaftaran[28]
            dt_kode_jenis_kendaraan = db_pendaftaran[29]
            dt_kode_wilayah = db_pendaftaran[30]

            dt_tgl_baru_uji = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
            dt_new_no_antrian = dt_dash_pendaftaran + 1
            if myresult == 0:
                toast('Data tidak ditemukan di Database, membuat pendaftaran baru')
                try:
                    dt_status_uji = 'BR'
                    mycursor = mydb.cursor()
                    sql = f"INSERT INTO {TB_DAFTAR_BARU} (NOANTRIAN, NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, SUBJENIS_ID, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, DAYAMOTOR, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah, TGL_LASTUJI) VALUES ('{dt_new_no_antrian:04d}', '{dt_no_uji}','{dt_new_no_uji}','{dt_no_wilayah}','{dt_no_kendaraan}','{dt_no_plat}','{dt_nopol}','{dt_nama}','{dt_no_hp}','{dt_alamat}','{dt_izin_id}','{dt_wilayah}','{dt_provinsi}','{dt_kabupaten_kota}','{dt_kecamatan}','{dt_merk_id}','{dt_subjenis_id}','{dt_type}','{dt_tahun_buat}','{dt_silinder}','{dt_warna}','{dt_chasis}','{dt_mesin}','{dt_warna_plat}','{dt_bahan_bakar}','{dt_jbb}','{dt_daya_motor}','{dt_status_penerbitan}','{dt_jenis_kendaraan}','{dt_kode_jenis_kendaraan}','{dt_kode_wilayah}','{dt_tgl_last_uji}')"
                    mycursor.execute(sql)
                    mydb.commit()
                except Exception as e:
                    toast_msg = f'Error Create Tabel Daftar Baru: {e}'
                    toast(toast_msg)
            else:
                toast_msg = f'Berhasil Menemukan Data Nomor Polisi {myresult[5]}'
                toast(toast_msg)
                try:
                    dt_status_uji = 'B'
                    mycursor = mydb.cursor()
                    sql = f"INSERT INTO {TB_DAFTAR_BERKALA} (NOANTRIAN, NOUJI, NEW_NOUJI, NOWIL, NOKDR, PLAT, NOPOL, NAMA, NOHP, ALAMAT, ID_IZIN, WLY, PROP, KABKOT, KEC, MERK_ID, SUBJENIS_ID, TYPE, TH_BUAT, SILINDER, WARNA_KEND, CHASIS, MESIN, WARNA_PLAT, BHN_BAKAR, JBB, DAYAMOTOR, statuspenerbitan, idjeniskendaraan, kd_jnskendaraan, kodewilayah, TGL_LASTUJI) VALUES ('{dt_new_no_antrian:04d}', '{dt_no_uji}','{dt_new_no_uji}','{dt_no_wilayah}','{dt_no_kendaraan}','{dt_no_plat}','{dt_nopol}','{dt_nama}','{dt_no_hp}','{dt_alamat}','{dt_izin_id}','{dt_wilayah}','{dt_provinsi}','{dt_kabupaten_kota}','{dt_kecamatan}','{dt_merk_id}','{dt_subjenis_id}','{dt_type}','{dt_tahun_buat}','{dt_silinder}','{dt_warna}','{dt_chasis}','{dt_mesin}','{dt_warna_plat}','{dt_bahan_bakar}','{dt_jbb}','{dt_daya_motor}','{dt_status_penerbitan}','{dt_jenis_kendaraan}','{dt_kode_jenis_kendaraan}','{dt_kode_wilayah}','{dt_tgl_last_uji}')"
                    mycursor.execute(sql)
                    mydb.commit()
                except Exception as e:
                    toast_msg = f'Error Create Tabel Daftar Berkala: {e}'
                    toast(toast_msg)
            try:
                mycursor = mydb.cursor()
                sql = f"INSERT INTO {TB_DATA} (noantrian, nouji, NEW_NOUJI, nopol, merk, type, idjeniskendaraan, kd_jnskendaraan, kodewilayah, jenis, jbb, bahan_bakar, warna, statusuji, statuspenerbitan, kode_daerah, no_kendaraan, kode_huruf, tgl_daftar, user, check_flag) VALUES ('{dt_new_no_antrian:04d}','{dt_no_uji}','{dt_new_no_uji}','{dt_nopol}','{dt_merk_id}','{dt_type}','{dt_jenis_kendaraan}','{dt_kode_jenis_kendaraan}','{dt_kode_wilayah}','{dt_subjenis_id}','{dt_jbb}','{dt_bahan_bakar}','{dt_warna}','{dt_status_uji}','{dt_status_penerbitan}','{dt_no_wilayah}','{dt_no_kendaraan}','{dt_no_plat}','{dt_tgl_baru_uji}','{dt_user}','0')"
                mycursor.execute(sql)
                mydb.commit()
            except Exception as e:
                toast_msg = f'Error Create Tabel Antrian: {e}'
                toast(toast_msg)

            self.ids.tx_nopol.text = ""
            self.ids.tx_nouji.text = ""
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Tambah Pendaftaran: {e}'
            toast(toast_msg)

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)    

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)     

class ScreenInspectId(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectId, self).__init__(**kwargs)

    def on_enter(self):
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Error Execute Command from Menu Comment Callback: {e}'
            toast(toast_msg)  

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Komponen Uji Row: {e}'
            toast(toast_msg)  

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"
           
        except Exception as e:
            toast_msg = f'Error Execute Command from Table Subkomponen Uji Row: {e}'
            toast(toast_msg)  

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K01' OR kode_komponen_uji = 'K02' OR kode_komponen_uji = 'K15' OR kode_komponen_uji = 'K18' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
        except Exception as e:
            toast_msg = f'Error Fetch Table Komponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                layout_list.add_widget(
                    MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),
                        MDIconButton(id=f'bt_komponen_uji{i}', size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C"),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height="60dp",
                        )
                    )
        except Exception as e:
            toast_msg = f'Error Reload Table Komponen Uji: {e}'
            print(toast_msg)

    def exec_reload_subkomponen_uji(self, kode_komponen_uji):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Error Fetch Table Subkomponen uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.1),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height="60dp",
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)                
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Error Reload Table Sub Komponen Uji: {e}'
            print(toast_msg)

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        try:
            print(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak ada rekomendasi komentar, silahkan isi komentar sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(54),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Error Show Komentar: {e}'
            print(toast_msg)

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectVisual(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectVisual, self).__init__(**kwargs)

    def on_enter(self):
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Error Execute Command from Menu Comment Callback: {e}'
            toast(toast_msg)  

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Komponen Uji Row: {e}'
            toast(toast_msg)  

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"
           
        except Exception as e:
            toast_msg = f'Error Execute Command from Table Subkomponen Uji Row: {e}'
            toast(toast_msg)  

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K03' OR kode_komponen_uji = 'K04' OR kode_komponen_uji = 'K05' OR kode_komponen_uji = 'K06' OR kode_komponen_uji = 'K07' OR kode_komponen_uji = 'K08' OR kode_komponen_uji = 'K09' OR kode_komponen_uji = 'K14' OR kode_komponen_uji = 'K16' OR kode_komponen_uji = 'K17' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
        except Exception as e:
            toast_msg = f'Error Fetch Table Komponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                layout_list.add_widget(
                    MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),
                        MDIconButton(id=f'bt_komponen_uji{i}', size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C"),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height="60dp",
                        )
                    )
        except Exception as e:
            toast_msg = f'Error Reload Table Komponen Uji: {e}'
            print(toast_msg)

    def exec_reload_subkomponen_uji(self, kode_komponen_uji):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}'")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Error Fetch Table Subkomponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.1),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height="60dp",
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)                
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Error Reload Table Sub Komponen Uji: {e}'
            print(toast_msg)

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        try:
            print(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak ada rekomendasi komentar, silahkan isi komentar sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(54),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Error Show Komentar: {e}'
            print(toast_msg)

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectVisual2(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectVisual2, self).__init__(**kwargs)

    def on_enter(self):
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Error Execute Command from Menu Comment Callback: {e}'
            toast(toast_msg)  

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Komponen Uji Row: {e}'
            toast(toast_msg)  

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"
           
        except Exception as e:
            toast_msg = f'Error Execute Command from Table Subkomponen Uji Row: {e}'
            toast(toast_msg)  

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_komponen_uji = 'K10' OR kode_komponen_uji = 'K11' OR kode_komponen_uji = 'K12' OR kode_komponen_uji = 'K13' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
        except Exception as e:
            toast_msg = f'Error Fetch Table Komponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                layout_list.add_widget(
                    MDCard(
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),
                        MDIconButton(id=f'bt_komponen_uji{i}', size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C"),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height="60dp",
                        )
                    )

        except Exception as e:
            toast_msg = f'Error Reload Table Komponen Uji: {e}'
            print(toast_msg)

    def exec_reload_subkomponen_uji(self, kode_komponen_uji):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Error Fetch Table Subkomponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.1),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height="60dp",
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)                
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Error Reload Table Sub Komponen Uji: {e}'
            print(toast_msg)

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        try:
            print(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak ada rekomendasi komentar, silahkan isi komentar sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(54),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Error Show Komentar: {e}'
            print(toast_msg)

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenInspectPit(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectPit, self).__init__(**kwargs)

    def on_enter(self):
        self.exec_reload_komponen_uji()

    def menu_komentar_callback(self, text_item):
        global selected_row_subkomponen_uji

        try:
            self.ids[f'tx_comment{selected_row_subkomponen_uji}'].text = text_item
        except Exception as e:
            toast_msg = f'Error Execute Command from Menu Comment Callback: {e}'
            toast(toast_msg)  

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = True
            row = int(str(instance.id).replace("card_komponen_uji",""))
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Komponen Uji Row: {e}'
            toast(toast_msg)  

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji, flags_subkomponen_uji, db_subkomponen_uji
        global selected_row_subkomponen_uji, selected_kode_subkomponen_uji

        try:
            self.ids.bt_dropdown_caller.disabled = False
            row = int(str(instance.id).replace("card_subkomponen_uji",""))
            selected_row_subkomponen_uji = row
            selected_kode_subkomponen_uji = db_subkomponen_uji[0, row]
            self.reload_menu_komentar_uji(selected_kode_subkomponen_uji)

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"
           
        except Exception as e:
            toast_msg = f'Error Execute Command from Table Subkomponen Uji Row: {e}'
            toast(toast_msg)  

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI} WHERE kode_kelompok_uji = 'V2' ")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T
        except Exception as e:
            toast_msg = f'Error Fetch Table Komponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_komponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_komponen_uji
            for i in range(db_komponen_uji[0,:].size):
                layout_list.add_widget(
                    MDCard(
                        # MDLabel(text=f"{db_komponen_uji[1, i]}", size_hint_x= 0.2),
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),
                        MDIconButton(id=f'bt_komponen_uji{i}', size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C"),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = [20, 0],
                        spacing = 10,
                        id=f'card_komponen_uji{i}',
                        size_hint_y=None,
                        height="60dp",
                        )
                    )

        except Exception as e:
            toast_msg = f'Error Reload Table Komponen Uji: {e}'
            print(toast_msg)

    def exec_reload_subkomponen_uji(self, kode_komponen_uji):
        global mydb, db_subkomponen_uji
        global flags_subkomponen_uji

        try:
            tb_subkomponen_uji = mydb.cursor()
            tb_subkomponen_uji.execute(f"SELECT kode_subkomponen_uji, nama, keterangan FROM {TB_SUBKOMPONEN_UJI} WHERE kode_komponen_uji = '{kode_komponen_uji}' ")
            result_tb_subkomponen_uji = tb_subkomponen_uji.fetchall()
            mydb.commit()
            db_subkomponen_uji = np.array(result_tb_subkomponen_uji).T
            flags_subkomponen_uji = np.ones(db_subkomponen_uji[0,:].size, dtype='bool')
        except Exception as e:
            toast_msg = f'Error Fetch Table Subkomponen Uji: {e}'
            print(toast_msg)

        try:
            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)
        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.1),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.4),
                    
                    ripple_behavior = False,
                    padding = [20, 0],
                    spacing = 10,
                    id=f'card_subkomponen_uji{i}',
                    on_press = self.on_subkomponen_uji_row_press,
                    size_hint_y=None,
                    height="60dp",
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                # tx_comment = MDTextField(size_hint_x= 0.25, hint_text="Komentar",)
                # bt_comment = MDRectangleFlatIconButton(size_hint_x= 0.05, icon="pen", md_bg_color="#2CA02C")
                # bt_check = MDRectangleFlatIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C")
                tx_comment = MDTextField(size_hint_x= 0.3, hint_text="Komentar",text_color_focus= "#4471C4",hint_text_color_focus= "#4471C4",line_color_focus= "#4471C4",icon_left_color_focus= "#4471C4")
                bt_check = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C",)                
                self.ids[f'tx_comment{i}'] = tx_comment
                self.ids[f'bt_subkomponen_uji{i}'] = bt_check
                card.add_widget(tx_comment)
                card.add_widget(bt_check)

        except Exception as e:
            toast_msg = f'Error Reload Table Sub Komponen Uji: {e}'
            print(toast_msg)

    def reload_menu_komentar_uji(self, selected_kode_subkomponen_uji=""):
        try:
            print(f"reload menu komentar uji {selected_kode_subkomponen_uji}")
            tb_komentar_uji = mydb.cursor()
            tb_komentar_uji.execute(f"SELECT id, id_komponen_uji, id_subkomponen_uji, komentar FROM {TB_KOMENTAR_UJI} WHERE id_subkomponen_uji = '{selected_kode_subkomponen_uji}'")
            result_tb_komentar_uji = tb_komentar_uji.fetchall()
            mydb.commit()
            db_komentar_uji = np.array(result_tb_komentar_uji).T

            if(db_komentar_uji.size == 0 ):
                self.ids.bt_dropdown_caller.disabled = True
                toast('Tidak ada rekomendasi komentar, silahkan isi komentar sendiri')

            self.menu_komentar_uji_items = [
                {
                    "text": f"{db_komentar_uji[3,i]}",                   
                    "viewclass": "ListItem",
                    "height": dp(54),
                    "on_release": lambda x=f"{db_komentar_uji[3,i]}": self.menu_komentar_callback(x),
                } for i in range(db_komentar_uji[0,:].size)
            ]

            self.menu_komentar_uji = MDDropdownMenu(
                caller=self.ids.bt_dropdown_caller,
                items=self.menu_komentar_uji_items,
                width_mult=4,
            )

        except Exception as e:
            toast_msg = f'Error Show Komentar: {e}'
            print(toast_msg)

    def open_screen_menu(self):
        self.screen_manager.current = 'screen_menu'

    def exec_open_camera(self):
        self.screen_manager.current = 'screen_realtime_pit'

    def exec_save(self):
        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()

class ScreenRealtimeCctv(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenRealtimeCctv, self).__init__(**kwargs)

    def on_enter(self):
        db_camera_list = np.array(["Depan", "Kiri", "Kanan", "Belakang"])
        self.menu_camera_items = [
            {
                "text": f"{db_camera_list[i]}",                   
                "viewclass": "ListItem",
                "height": dp(54),
                "on_release": lambda x=i, y=db_camera_list[i]: self.menu_camera_callback(x, y),
            } for i in range(db_camera_list.size)
        ]

        self.menu_camera = MDDropdownMenu(
            caller=self.ids.bt_dropdown_caller,
            items=self.menu_camera_items,
            width_mult=4,
        )

    def on_leave(self):
        Clock.unschedule(self.update_frame)

    def menu_camera_callback(self, camera_number, camera_name):
        global selected_camera

        try:
            print(f"Selected camera number {camera_number}")
            toast(f"Kamera {camera_name} dipilih")
            selected_camera = camera_number

        except Exception as e:
            toast_msg = f'Error Execute Command from Camera List: {e}'
            toast(toast_msg)  

    def exec_play_cctv(self):
        Clock.schedule_interval(self.update_frame, 5)

    def exec_stop_cctv(self):
        Clock.unschedule(self.update_frame)

    def update_frame(self, dt):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4
        global selected_camera

        try:
            # Load the image           
            # frame = cv2.imread('assets/images/tampak-depan.png')
            rtsp_url = np.array([rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4])

            self.capture = cv2.VideoCapture(rtsp_url[selected_camera])
                         # self.capture = cv2.VideoCapture(rtsp_url_cam1)
            ret, frame = self.capture.read()
            if ret:
                # Membalik frame secara vertikal
                frame = cv2.flip(frame, 0)  # 0 untuk membalik secara vertikal

                # OpenCV menggunakan format BGR, ubah ke RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                zoom_factor = self.ids.sl_cctv_zoom.value
                zoomed = self.zoom_center(frame_rgb, zoom_factor)

                # Konversi frame menjadi texture untuk ditampilkan di Kivy
                buf = zoomed.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            self.ids.image_view_front.texture = texture

        except Exception as e:
            toast_msg = f'Error update frame: {e}'
            print(toast_msg)

    def zoom_center(self, img, zoom_factor=1.0):

        y_size = img.shape[0]
        x_size = img.shape[1]
        
        # define new boundaries
        x1 = int(0.5*x_size*(1-1/zoom_factor))
        x2 = int(x_size-0.5*x_size*(1-1/zoom_factor))
        y1 = int(0.5*y_size*(1-1/zoom_factor))
        y2 = int(y_size-0.5*y_size*(1-1/zoom_factor))

        # first crop image then scale
        img_cropped = img[y1:y2,x1:x2]
        return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)

    def exec_save(self):
        self.open_screen_main()

    def open_screen_main(self):
        self.screen_manager.current = 'screen_main'

    def exec_start(self):
        self.screen_manager.current = 'screen_inspect_pit'

    def exec_cancel(self):
        try:
            self.screen_manager.current = 'screen_menu'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        


    def exec_logout(self):
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)      

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)    

class ScreenRealtimePit(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenRealtimePit, self).__init__(**kwargs)

    def on_enter(self):
        db_camera_list = np.array(["Depan Kiri", "Depan Kanan", "Belakang Kiri", "Belakang Kanan"])
        self.menu_camera_items = [
            {
                "text": f"{db_camera_list[i]}",                   
                "viewclass": "ListItem",
                "height": dp(54),
                "on_release": lambda x=i, y=db_camera_list[i]: self.menu_camera_callback(x, y),
            } for i in range(db_camera_list.size)
        ]

        self.menu_camera = MDDropdownMenu(
            caller=self.ids.bt_dropdown_caller,
            items=self.menu_camera_items,
            width_mult=4,
        )

    def on_leave(self):
        Clock.unschedule(self.update_frame)

    def menu_camera_callback(self, camera_number, camera_name):
        global selected_camera

        try:
            print(f"Selected camera number {camera_number}")
            toast(f"Kamera {camera_name} dipilih")
            selected_camera = camera_number

        except Exception as e:
            toast_msg = f'Error Execute Command from Camera List: {e}'
            toast(toast_msg)  

    def exec_play_cctv(self):
        Clock.schedule_interval(self.update_frame, 5)

    def exec_stop_cctv(self):
        Clock.unschedule(self.update_frame)

    def update_frame(self, dt):
        global rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4
        global selected_camera

        try:
            # Load the image           
            # frame = cv2.imread('assets/images/tampak-depan.png')
            rtsp_url = np.array([rtsp_url_cam1, rtsp_url_cam2, rtsp_url_cam3, rtsp_url_cam4])

            self.capture = cv2.VideoCapture(rtsp_url[selected_camera])
                         # self.capture = cv2.VideoCapture(rtsp_url_cam1)
            ret, frame = self.capture.read()
            if ret:
                # Membalik frame secara vertikal
                frame = cv2.flip(frame, 0)  # 0 untuk membalik secara vertikal

                # OpenCV menggunakan format BGR, ubah ke RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                zoom_factor = self.ids.sl_cctv_zoom.value
                zoomed = self.zoom_center(frame_rgb, zoom_factor)

                # Konversi frame menjadi texture untuk ditampilkan di Kivy
                buf = zoomed.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            self.ids.image_view_front.texture = texture

        except Exception as e:
            toast_msg = f'Error update frame: {e}'
            print(toast_msg)

    def zoom_center(self, img, zoom_factor=1.0):

        y_size = img.shape[0]
        x_size = img.shape[1]
        
        # define new boundaries
        x1 = int(0.5*x_size*(1-1/zoom_factor))
        x2 = int(x_size-0.5*x_size*(1-1/zoom_factor))
        y1 = int(0.5*y_size*(1-1/zoom_factor))
        y2 = int(y_size-0.5*y_size*(1-1/zoom_factor))

        # first crop image then scale
        img_cropped = img[y1:y2,x1:x2]
        return cv2.resize(img_cropped, None, fx=zoom_factor, fy=zoom_factor)

    def exec_save(self):
        self.open_screen_main()

    def open_screen_main(self):
        self.screen_manager.current = 'screen_main'

    def exec_start(self):
        self.screen_manager.current = 'screen_inspect_pit'

    def exec_cancel(self):
        try:
            self.screen_manager.current = 'screen_menu'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        


    def exec_logout(self):
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        global dt_user
        try:
            if (dt_user == ""):
                self.screen_manager.current = 'screen_login'
            else:
                toast(f"Anda sudah login sebagai {dt_user}")

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)      

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)    

class ListItem(OneLineListItem):
 
# class Item(BaseListItem):    
# class Item(OneLineListItem):
    # pass        
    # left_icon = StringProperty()
    list_text = StringProperty()
    # text = StringProperty()

class RootScreen(ScreenManager):
    pass             

class VisualInspectionApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.icon = 'assets/images/logo-app.png'

        LabelBase.register(
            name="Orbitron-Regular",
            fn_regular="assets/fonts/Orbitron-Regular.ttf")
        
        LabelBase.register(
            name="Draco",
            fn_regular="assets/fonts/Draco.otf")        

        LabelBase.register(
            name="Recharge",
            fn_regular="assets/fonts/Recharge.otf") 
        
        theme_font_styles.append('Display')
        self.theme_cls.font_styles["Display"] = [
            "Orbitron-Regular", 72, False, 0.15]       

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
            "Recharge", 12, False, 0.15] 

        theme_font_styles.append('Body1')
        self.theme_cls.font_styles["Body1"] = [
            "Recharge", 12, False, 0.15] 
        
        theme_font_styles.append('Button')
        self.theme_cls.font_styles["Button"] = [
            "Recharge", 10, False, 0.15] 

        theme_font_styles.append('Caption')
        self.theme_cls.font_styles["Caption"] = [
            "Recharge", 8, False, 0.15]                                 
            
        Window.fullscreen = 'auto'
        # Window.borderless = False
        # Window.size = 1920, 1080
        # Window.allow_screensaver = True

        Builder.load_file('main.kv')
        return RootScreen()

if __name__ == '__main__':
    VisualInspectionApp().run()