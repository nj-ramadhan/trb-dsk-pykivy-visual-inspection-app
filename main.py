from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.toast import toast
from kivymd.app import MDApp
import os, sys, time, numpy as np
import configparser, hashlib, mysql.connector
import cv2
from pymodbus.client import ModbusTcpClient
import weakref

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
TB_KOMPONEN_UJI = config['mysql']['TB_KOMPONEN_UJI']
TB_SUBKOMPONEN_UJI = config['mysql']['TB_SUBKOMPONEN_UJI']

COUNT_STARTING = 3
COUNT_ACQUISITION = 4
TIME_OUT = 500

rtsp_url_cam1 = 'rtsp://admin:TRBintegrated202@192.168.1.64:554/Streaming/Channels/101'

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

flag_body = True
flag_roda = True
flag_spion = True
flag_penyapu = True
flag_sabuk = True
flag_bumper = True
flag_lampu = True
flag_kaca = True
flag_motor = True
flag_spakbor = True

flag_body_sub = np.array([True,True,True,True,True,True,True])
flag_roda_sub = np.array([True,True,True,True,True,True,True])
flag_spion_sub = np.array([True,True,True,True,True,True,True])
flag_penyapu_sub = np.array([True,True,True,True,True,True,True])
flag_sabuk_sub = np.array([True,True,True,True,True,True,True])
flag_bumper_sub = np.array([True,True,True,True,True,True,True])

flag_kaca_sub = np.array([True,True,True,True,True,True,True])
flag_motor_sub = np.array([True,True,True,True,True,True,True])
flag_spakbor_sub = np.array([True,True,True,True,True,True,True])

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

modbus_client = ModbusTcpClient('192.168.1.111')

flag_gate = False

class ScreenHome(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenHome, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 1)

    def delayed_init(self, dt):
        Clock.schedule_interval(self.regular_update_display, 3)

    def regular_update_display(self, dt):
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
        try:
            self.screen_manager.current = 'screen_login'

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
            toast_msg = f'error Login: {e}'

    def exec_login(self):
        global mydb, db_users
        global dt_check_user, dt_user

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
            mycursor.execute(f"SELECT id_user, nama, username, password, nama FROM {TB_USER} WHERE username = '{input_username}' and password = '{hashed_password.hexdigest()}'")
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
                self.ids.tx_username.text = ""
                self.ids.tx_password.text = "" 
                self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'error Login: {e}'
            toast(toast_msg)        
            toast('Gagal Masuk, Nama Pengguna atau Password Salah')

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        try:
            self.screen_manager.current = 'screen_login'

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
        Clock.schedule_once(self.delayed_init, 1)                 

    def delayed_init(self, dt):
        global flag_conn_stat, flag_play
        global count_starting, count_get_data

        flag_conn_stat = False
        flag_play = False

        count_starting = COUNT_STARTING
        count_get_data = COUNT_ACQUISITION
        
        Clock.schedule_interval(self.regular_update_display, 1)
        self.exec_reload_database()
        self.exec_reload_table()

    def on_antrian_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_antrian, db_merk

        try:
            row = int(str(instance.id).replace("card_antrian",""))
            dt_no_antrian           = f"{db_antrian[0, row]}"
            dt_no_pol               = f"{db_antrian[1, row]}"
            dt_no_uji               = f"{db_antrian[2, row]}"
            dt_check_flag           = 'Belum Tes' if (int(db_antrian[3, row]) == 0) else 'Sudah Tes'
            dt_nama                 = f"{db_antrian[4, row]}"
            dt_merk                 = f"{db_merk[np.where(db_merk == db_antrian[5, row])[0][0],1]}"
            dt_type                 = f"{db_antrian[6, row]}"
            dt_jenis_kendaraan      = f"{db_antrian[7, row]}"
            dt_jbb                  = f"{db_antrian[8, row]}"
            dt_bahan_bakar          = f"{db_antrian[9, row]}"
            dt_warna                = f"{db_antrian[10, row]}"
                        
            self.exec_start()

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Row: {e}'
            toast(toast_msg)   

    def regular_update_display(self, dt):
        global flag_conn_stat
        global count_starting, count_get_data
        global dt_user, dt_no_antrian, dt_no_pol, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_chasis, dt_merk, dt_type, dt_no_mesin
        global dt_check_flag, dt_check_user, dt_check_post
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            screen_home = self.screen_manager.get_screen('screen_home')
            screen_login = self.screen_manager.get_screen('screen_login')
            screen_menu = self.screen_manager.get_screen('screen_menu')
            screen_inspect_pit = self.screen_manager.get_screen('screen_inspect_pit')
            screen_inspect_id = self.screen_manager.get_screen('screen_inspect_id')
            screen_inspect_cctv = self.screen_manager.get_screen('screen_inspect_cctv')
            screen_inspect_visual = self.screen_manager.get_screen('screen_inspect_visual')

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
            screen_inspect_cctv.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_cctv.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_visual.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_visual.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_pit.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_pit.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_dash_pendaftaran.text = str(dt_dash_pendaftaran)
            self.ids.lb_dash_belum_uji.text = str(dt_dash_belum_uji)
            self.ids.lb_dash_sudah_uji.text = str(dt_dash_sudah_uji)

            screen_menu.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_menu.ids.lb_no_pol.text = str(dt_no_pol)
            screen_menu.ids.lb_no_uji.text = str(dt_no_uji)

            screen_inspect_id.ids.lb_no_uji.text = str(dt_no_uji)
            screen_inspect_id.ids.lb_no_pol.text = str(dt_no_pol)
            screen_inspect_id.ids.lb_chasis.text = str(dt_chasis)
            screen_inspect_id.ids.lb_no_mesin.text = str(dt_no_mesin)
            screen_inspect_id.ids.lb_merk.text = str(dt_merk)
            screen_inspect_id.ids.lb_nama.text = str(dt_nama)
            screen_inspect_id.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            if(not flag_conn_stat):
                self.ids.lb_comm.color = colors['Red']['A200']
                self.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_home.ids.lb_comm.color = colors['Red']['A200']
                screen_home.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_login.ids.lb_comm.color = colors['Red']['A200']
                screen_login.ids.lb_comm.text = 'PLC Tidak Terhubung'

            else:
                self.ids.lb_comm.color = colors['Blue']['200']
                self.ids.lb_comm.text = 'PLC Terhubung'
                screen_home.ids.lb_comm.color = colors['Blue']['200']
                screen_home.ids.lb_comm.text = 'PLC Terhubung'
                screen_login.ids.lb_comm.color = colors['Blue']['200']
                screen_login.ids.lb_comm.text = 'PLC Terhubung'
            
            self.ids.bt_logout.disabled = False if dt_user != '' else True
            # self.ids.bt_start.disabled = True if dt_user == '' else True if dt_check_flag != "Belum Tes" else False

            self.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_home.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_login.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_menu.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_id.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_cctv.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_visual.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_pit.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'

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
        global mydb, db_antrian, db_merk
        global dt_dash_pendaftaran, dt_dash_belum_uji, dt_dash_sudah_uji

        try:
            tb_antrian = mydb.cursor()
            tb_antrian.execute(f"SELECT noantrian, nopol, nouji, check_flag, user, merk, type, idjeniskendaraan, jbb, bahan_bakar, warna FROM {TB_DATA}")
            result_tb_antrian = tb_antrian.fetchall()
            mydb.commit()
            db_antrian = np.array(result_tb_antrian).T
            db_pendaftaran = np.array(result_tb_antrian)
            dt_dash_pendaftaran = db_pendaftaran[:,3].size
            dt_dash_belum_uji = np.where(db_pendaftaran[:,3] == 0)[0].size
            dt_dash_sudah_uji = np.where(db_pendaftaran[:,3] == 1)[0].size

            tb_merk = mydb.cursor()
            tb_merk.execute(f"SELECT ID, DESCRIPTION FROM {TB_MERK}")
            result_tb_merk = tb_merk.fetchall()
            mydb.commit()
            db_merk = np.array(result_tb_merk)

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
                        MDLabel(text=f"{db_antrian[1, i]}", size_hint_x= 0.08),
                        MDLabel(text=f"{db_antrian[2, i]}", size_hint_x= 0.08),
                        MDLabel(text='Belum Tes' if (int(db_antrian[3, i]) == 0) else 'Sudah Tes', size_hint_x= 0.08),
                        MDLabel(text=f"{db_antrian[4, i]}", size_hint_x= 0.12),
                        MDLabel(text=f"{db_merk[np.where(db_merk == db_antrian[5, i])[0][0],1]}", size_hint_x= 0.08),
                        MDLabel(text=f"{db_antrian[6, i]}", size_hint_x= 0.05),
                        MDLabel(text=f"{db_antrian[7, i]}", size_hint_x= 0.15),
                        MDLabel(text=f"{db_antrian[8, i]}", size_hint_x= 0.05),
                        MDLabel(text=f"{db_antrian[9, i]}", size_hint_x= 0.08),
                        MDLabel(text=f"{db_antrian[10, i]}", size_hint_x= 0.08),

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
        try:
            self.screen_manager.current = 'screen_login'

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

        if(not flag_gate):
            flag_gate = True

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3072, flag_gate, slave=1) #M0
                modbus_client.close()
        except:
            toast("error send exec_gate_open data to PLC Slave") 

    def exec_barrier_close(self):
        global flag_conn_stat
        global flag_gate

        if(flag_gate):
            flag_gate = False

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3073, not flag_gate, slave=1) #M1
                modbus_client.close()
        except:
            toast("error send exec_gate_close data to PLC Slave") 

    def exec_barrier_stop(self):
        global flag_conn_stat

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3072, False, slave=1) #M0
                modbus_client.write_coil(3073, False, slave=1) #M1
                modbus_client.close()
        except:
            toast("error send exec_gate_stop data to PLC Slave") 

    def exec_capture(self):
        try:
            self.screen_manager.current = 'screen_inspect_cctv'

        except Exception as e:
            toast_msg = f'Error Navigate to Play Detect: {e}'
            toast(toast_msg)    

    def exec_inspect_visual(self):
        try:
            self.screen_manager.current = 'screen_inspect_visual'

        except Exception as e:
            toast_msg = f'Error Navigate to Visual Inspection Screen: {e}'
            toast(toast_msg)    

    def exec_inspect_id(self):
        try:
            self.screen_manager.current = 'screen_inspect_id'

        except Exception as e:
            toast_msg = f'Error Navigate to Identity Inspection Screen: {e}'
            toast(toast_msg) 

    def exec_inspect_pit(self):
        try:
            self.screen_manager.current = 'screen_inspect_pit'

        except Exception as e:
            toast_msg = f'Error Navigate to Pit Inspection Screen: {e}'
            toast(toast_msg)    

    def exec_cancel(self):
        self.screen_manager.current = 'screen_main'

class ScreenInspectId(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectId, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        
    def delayed_init(self, dt):
        pass

    def open_screen_menu(self):
        global flag_play        
        global count_starting, count_get_data

        count_starting = COUNT_STARTING
        count_get_data = COUNT_ACQUISITION
        flag_play = False   
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()

    def exec_no_uji(self):
        global flag_no_uji

        try:
            if(flag_no_uji):
                flag_no_uji = False
                self.ids.bt_no_uji.icon = "cancel"
                self.ids.bt_no_uji.md_bg_color = "#FF2A2A"
            else:
                flag_no_uji = True
                self.ids.bt_no_uji.icon = "check-bold"
                self.ids.bt_no_uji.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_no_pol(self):
        global flag_no_pol

        try:
            if(flag_no_pol):
                flag_no_pol = False
                self.ids.bt_no_pol.icon = "cancel"
                self.ids.bt_no_pol.md_bg_color = "#FF2A2A"
            else:
                flag_no_pol = True
                self.ids.bt_no_pol.icon = "check-bold"
                self.ids.bt_no_pol.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_chasis(self):
        global flag_chasis

        try:
            if(flag_chasis):
                flag_chasis = False
                self.ids.bt_chasis.icon = "cancel"
                self.ids.bt_chasis.md_bg_color = "#FF2A2A"
            else:
                flag_chasis = True
                self.ids.bt_chasis.icon = "check-bold"
                self.ids.bt_chasis.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_no_mesin(self):
        global flag_no_mesin

        try:
            if(flag_no_mesin):
                flag_no_mesin = False
                self.ids.bt_no_mesin.icon = "cancel"
                self.ids.bt_no_mesin.md_bg_color = "#FF2A2A"
            else:
                flag_no_mesin = True
                self.ids.bt_no_mesin.icon = "check-bold"
                self.ids.bt_no_mesin.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_jenis_kendaraan(self):
        global flag_jenis_kendaraan

        try:
            if(flag_jenis_kendaraan):
                flag_jenis_kendaraan = False
                self.ids.bt_jenis_kendaraan.icon = "cancel"
                self.ids.bt_jenis_kendaraan.md_bg_color = "#FF2A2A"
            else:
                flag_jenis_kendaraan = True
                self.ids.bt_jenis_kendaraan.icon = "check-bold"
                self.ids.bt_jenis_kendaraan.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_merk(self):
        global flag_merk

        try:
            if(flag_merk):
                flag_merk = False
                self.ids.bt_merk.icon = "cancel"
                self.ids.bt_merk.md_bg_color = "#FF2A2A"
            else:
                flag_merk = True
                self.ids.bt_merk.icon = "check-bold"
                self.ids.bt_merk.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_nama(self):
        global flag_nama

        try:
            if(flag_nama):
                flag_nama = False
                self.ids.bt_nama.icon = "cancel"
                self.ids.bt_nama.md_bg_color = "#FF2A2A"
            else:
                flag_nama = True
                self.ids.bt_nama.icon = "check-bold"
                self.ids.bt_nama.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

    def exec_alamat(self):
        global flag_alamat

        try:
            if(flag_alamat):
                flag_alamat = False
                self.ids.bt_alamat.icon = "cancel"
                self.ids.bt_alamat.md_bg_color = "#FF2A2A"
            else:
                flag_alamat = True
                self.ids.bt_alamat.icon = "check-bold"
                self.ids.bt_alamat.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error ID Inspect: {e}'
            toast(toast_msg)  

class ScreenInspectCctv(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectCctv, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        # Clock.schedule_interval(self.update_frame, 1)
        
    def delayed_init(self, dt):
        pass

    def update_frame(self, dt):
        global rtsp_url_cam1
        try:
            # Membaca frame dari stream
            self.capture = cv2.VideoCapture(rtsp_url_cam1)
            ret, frame = self.capture.read()

            if ret:
                # Membalik frame secara vertikal
                frame = cv2.flip(frame, 0)  # 0 untuk membalik secara vertikal

                # OpenCV menggunakan format BGR, ubah ke RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Konversi frame menjadi texture untuk ditampilkan di Kivy
                buf = frame_rgb.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

                # Update widget Image dengan texture baru
                # self.img_widget.texture = texture
                self.ids.image_view_front.texture = texture

        except Exception as e:
            toast_msg = f'error update frame: {e}'
            print(toast_msg)

    def exec_save(self):
        global flag_play
        global count_starting, count_get_data
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_check_flag, dt_check_user, dt_check_post

        self.open_screen_main()

    def open_screen_main(self):
        global flag_play        
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = COUNT_STARTING
        count_get_data = COUNT_ACQUISITION
        flag_play = False   
        screen_main.exec_reload_database()
        screen_main.exec_reload_table()
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
        try:
            self.screen_manager.current = 'screen_login'

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)    

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)    

class ScreenInspectVisual(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectVisual, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        
    def delayed_init(self, dt):
        self.exec_reload_komponen_uji()

    def on_komponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji

        try:
            row = int(str(instance.id).replace("card_komponen_uji",""))
            self.exec_reload_subkomponen_uji(db_komponen_uji[1, row])

        except Exception as e:
            toast_msg = f'Error Execute Command from Table Row: {e}'
            toast(toast_msg)  

    def on_subkomponen_uji_row_press(self, instance):
        global dt_no_antrian, dt_no_pol, dt_no_uji, dt_check_flag, dt_nama
        global dt_merk, dt_type, dt_jenis_kendaraan, dt_jbb, dt_bahan_bakar, dt_warna
        global db_komponen_uji
        global flags_subkomponen_uji

        try:
            row = int(str(instance.id).replace("card_subkomponen_uji",""))

            if(flags_subkomponen_uji[row]):
                flags_subkomponen_uji[row] = False
                self.ids[f'bt_subkomponen_uji{row}'].icon = "cancel"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#FF2A2A"
            else:
                flags_subkomponen_uji[row] = True
                self.ids[f'bt_subkomponen_uji{row}'].icon = "check-bold"
                self.ids[f'bt_subkomponen_uji{row}'].md_bg_color = "#2CA02C"
           
        except Exception as e:
            toast_msg = f'Error Execute Command from Table Row: {e}'
            toast(toast_msg)  

    def exec_reload_komponen_uji(self):
        global mydb, db_komponen_uji

        try:
            tb_komponen_uji = mydb.cursor()
            tb_komponen_uji.execute(f"SELECT kode_kelompok_uji, kode_komponen_uji, nama, keterangan FROM {TB_KOMPONEN_UJI}")
            result_tb_komponen_uji = tb_komponen_uji.fetchall()
            mydb.commit()
            db_komponen_uji = np.array(result_tb_komponen_uji).T

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
                        MDLabel(text=f"{db_komponen_uji[1, i]}", size_hint_x= 0.2),
                        MDLabel(text=f"{db_komponen_uji[2, i]}", size_hint_x= 0.7),
                        MDIconButton(id=f'bt_komponen_uji{i}', size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C"),

                        ripple_behavior = True,
                        on_press = self.on_komponen_uji_row_press,
                        padding = 20,
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

            layout_list = self.ids.layout_list_subkomponen_uji
            layout_list.clear_widgets(children=None)

        except Exception as e:
            toast_msg = f'Error Remove Widget: {e}'
            print(toast_msg)
        
        try:           
            layout_list = self.ids.layout_list_subkomponen_uji
            for i in range(db_subkomponen_uji[0,:].size):
                card = MDCard(
                    MDLabel(text=f"{db_subkomponen_uji[0, i]}", size_hint_x= 0.2),
                    MDLabel(text=f"{db_subkomponen_uji[1, i]}", size_hint_x= 0.7),
                    
                    ripple_behavior = True,
                    on_press = self.on_subkomponen_uji_row_press,
                    padding = 20,
                    id=f'card_subkomponen_uji{i}',
                    size_hint_y=None,
                    height="60dp",
                    )
                self.ids[f'card_subkomponen_uji{i}'] = card
                layout_list.add_widget(card)
                
                icon_button = MDIconButton(size_hint_x= 0.1, icon="check-bold", md_bg_color="#2CA02C")
                self.ids[f'bt_subkomponen_uji{i}'] = icon_button
                card.add_widget(icon_button)

        except Exception as e:
            toast_msg = f'Error Reload Table Sub Komponen Uji: {e}'
            print(toast_msg)

    def open_screen_menu(self):
        global flag_play        
        global count_starting, count_get_data

        count_starting = COUNT_STARTING
        count_get_data = COUNT_ACQUISITION
        flag_play = False   
        self.screen_manager.current = 'screen_menu'

    def exec_save(self):
        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()


class ScreenInspectPit(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectPit, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        # Clock.schedule_interval(self.update_frame, 1)
        
    def delayed_init(self, dt):
        pass

    def update_frame(self, dt):
        global rtsp_url_cam1
        try:
            # Membaca frame dari stream
            self.capture = cv2.VideoCapture(rtsp_url_cam1)
            ret, frame = self.capture.read()

            if ret:
                # Membalik frame secara vertikal
                frame = cv2.flip(frame, 0)  # 0 untuk membalik secara vertikal

                # OpenCV menggunakan format BGR, ubah ke RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Konversi frame menjadi texture untuk ditampilkan di Kivy
                buf = frame_rgb.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

                # Update widget Image dengan texture baru
                # self.img_widget.texture = texture
                self.ids.image_view_front.texture = texture

        except Exception as e:
            toast_msg = f'error update frame: {e}'
            print(toast_msg)

    def open_screen_main(self):
        global flag_play        
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = COUNT_STARTING
        count_get_data = COUNT_ACQUISITION
        flag_play = False   
        screen_main.exec_reload_table()
        self.screen_manager.current = 'screen_main'

    def exec_save(self):
        self.open_screen_main()

    def open_screen_inspect_cctv(self):
        self.screen_manager.current = 'screen_inspect_cctv'

    def exec_cancel(self):
        self.screen_manager.current = 'screen_menu'

    def exec_logout(self):
        self.screen_manager.current = 'screen_login'

    def exec_navigate_home(self):
        try:
            self.screen_manager.current = 'screen_home'

        except Exception as e:
            toast_msg = f'Error Navigate to Home Screen: {e}'
            toast(toast_msg)        

    def exec_navigate_login(self):
        try:
            self.screen_manager.current = 'screen_login'

        except Exception as e:
            toast_msg = f'Error Navigate to Login Screen: {e}'
            toast(toast_msg)    

    def exec_navigate_main(self):
        try:
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Main Screen: {e}'
            toast(toast_msg)   

class RootScreen(ScreenManager):
    pass             

class PlayDetectorApp(MDApp):
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
    PlayDetectorApp().run()