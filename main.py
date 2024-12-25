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
from kivymd.toast import toast
from kivymd.app import MDApp
import os, sys, time, numpy as np
import configparser, hashlib, mysql.connector
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

COUNT_STARTING = 3
COUNT_ACQUISITION = 4
TIME_OUT = 500

rtsp_url_cam1 = 'rtsp://admin:TRBintegrated202@192.168.1.64:554/Streaming/Channels/101'

dt_check_flag = 0
dt_check_user = 1
dt_check_post = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))

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
dt_no_reg = ""
dt_no_uji = ""
dt_nama = ""
dt_jenis_kendaraan = ""
dt_no_pol = ""
dt_chasis = ""
dt_no_mesin = ""
dt_merk = ""

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

    def exec_navigate_realtime(self):
        try:
            self.screen_manager.current = 'screen_realtime'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
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
            mycursor.execute(f"SELECT id_user, nama, username, password, nama FROM {TB_USER} WHERE username = '"+str(input_username)+"' and password = '"+str(hashed_password.hexdigest())+"'")
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

    def exec_navigate_realtime(self):
        try:
            self.screen_manager.current = 'screen_realtime'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
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

    def on_row_press(self, instance):
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan, dt_check_flag
        global db_antrian

        try:
            row = int(str(instance.id).replace("card",""))
            dt_no_antrian           = f"{db_antrian[0, row]}"
            dt_no_reg               = f"{db_antrian[1, row]}"
            dt_no_uji               = f"{db_antrian[2, row]}"
            dt_nama                 = f"{db_antrian[3, row]}"
            dt_jenis_kendaraan      = f"{db_antrian[4, row]}"
            dt_check_flag           = 'Belum Tes' if (int(db_antrian[5, row]) == 0) else 'Sudah Tes'

        except Exception as e:
            toast_msg = f'Error Update Table: {e}'
            toast(toast_msg)   

    def regular_update_display(self, dt):
        global flag_conn_stat
        global count_starting, count_get_data
        global dt_user, dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_check_flag, dt_check_user, dt_check_post

        try:
            screen_home = self.screen_manager.get_screen('screen_home')
            screen_login = self.screen_manager.get_screen('screen_login')
            screen_realtime = self.screen_manager.get_screen('screen_realtime')
            screen_menu = self.screen_manager.get_screen('screen_menu')
            screen_play_detect = self.screen_manager.get_screen('screen_play_detect')
            screen_inspect_id = self.screen_manager.get_screen('screen_inspect_id')
            screen_inspect_visual = self.screen_manager.get_screen('screen_inspect_visual')

            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_home.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_home.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_login.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_login.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_realtime.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_realtime.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_menu.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_menu.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_play_detect.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_play_detect.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_id.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_id.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_inspect_visual.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_inspect_visual.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_no_antrian.text = str(dt_no_antrian)
            self.ids.lb_no_reg.text = str(dt_no_reg)
            self.ids.lb_no_uji.text = str(dt_no_uji)
            self.ids.lb_nama.text = str(dt_nama)
            self.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            screen_menu.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_menu.ids.lb_no_reg.text = str(dt_no_reg)
            screen_menu.ids.lb_no_uji.text = str(dt_no_uji)

            screen_play_detect.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_play_detect.ids.lb_no_reg.text = str(dt_no_reg)
            screen_play_detect.ids.lb_no_uji.text = str(dt_no_uji)
            screen_play_detect.ids.lb_nama.text = str(dt_nama)
            screen_play_detect.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            screen_inspect_id.ids.lb_no_uji.text = str(dt_no_uji)
            screen_inspect_id.ids.lb_no_pol.text = str(dt_no_reg)
            screen_inspect_id.ids.lb_chasis.text = str(dt_chasis)
            screen_inspect_id.ids.lb_no_mesin.text = str(dt_no_mesin)
            screen_inspect_id.ids.lb_merk.text = str(dt_merk)
            screen_inspect_id.ids.lb_nama.text = str(dt_nama)
            screen_inspect_id.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            if(dt_check_flag == "Belum Tes"):
                self.ids.bt_start.disabled = False
            else:
                self.ids.bt_start.disabled = True

            if(not flag_conn_stat):
                self.ids.lb_comm.color = colors['Red']['A200']
                self.ids.lb_comm.text = 'PLC Tidak Terhubung'
                screen_login.ids.lb_comm.color = colors['Red']['A200']
                screen_login.ids.lb_comm.text = 'PLC Tidak Terhubung'

            else:
                self.ids.lb_comm.color = colors['Blue']['200']
                self.ids.lb_comm.text = 'PLC Terhubung'
                screen_login.ids.lb_comm.color = colors['Blue']['200']
                screen_login.ids.lb_comm.text = 'PLC Terhubung'

            self.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_home.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_login.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_realtime.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_menu.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_play_detect.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_id.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_inspect_visual.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'

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
        global mydb, db_antrian

        try:
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT noantrian, nopol, nouji, user, idjeniskendaraan, check_flag FROM {TB_DATA}")
            myresult = mycursor.fetchall()
            mydb.commit()
            db_antrian = np.array(myresult).T

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
                        MDLabel(text=f"{i+1}", size_hint_x= 0.1),
                        MDLabel(text=f"{db_antrian[0, i]}", size_hint_x= 0.2),
                        MDLabel(text=f"{db_antrian[1, i]}", size_hint_x= 0.3),
                        MDLabel(text=f"{db_antrian[2, i]}", size_hint_x= 0.3),
                        MDLabel(text=f"{db_antrian[3, i]}", size_hint_x= 0.3),
                        MDLabel(text=f"{db_antrian[4, i]}", size_hint_x= 0.4),
                        MDLabel(text='Belum Tes' if (int(db_antrian[5, i]) == 0) else 'Sudah Tes', size_hint_x= 0.2),

                        ripple_behavior = True,
                        on_press = self.on_row_press,
                        padding = 10,
                        id=f"card{i}",
                        size_hint_y=None,
                        height="60dp",
                        )
                    )

        except Exception as e:
            toast_msg = f'Error Reload Table: {e}'
            print(toast_msg)

    def exec_start(self):
        self.open_screen_menu()
        print("button start selected")

    def open_screen_menu(self):
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

    def exec_navigate_realtime(self):
        try:
            self.screen_manager.current = 'screen_realtime'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
            toast(toast_msg)   

class ScreenRealtime(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenRealtime, self).__init__(**kwargs)
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
        global mydb, db_antrian
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
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
        self.screen_manager.current = 'screen_play_detect'

    def exec_back(self):
        self.open_screen_main()

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

    def exec_navigate_realtime(self):
        try:
            self.screen_manager.current = 'screen_realtime'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
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
            self.screen_manager.current = 'screen_play_detect'

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
            toast_msg = f'Error Navigate to Visual Inspection Screen: {e}'
            toast(toast_msg) 

    def exec_inspect_pit(self):
        try:
            self.screen_manager.current = 'screen_visual'

        except Exception as e:
            toast_msg = f'Error Navigate to Visual Inspection Screen: {e}'
            toast(toast_msg) 

    def exec_back(self):
        self.screen_manager.current = 'screen_main'

class ScreenPlayDetect(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenPlayDetect, self).__init__(**kwargs)
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
        global flag_play
        global count_starting, count_get_data
        global mydb, db_antrian
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_check_flag, dt_check_user, dt_check_post

        self.open_screen_main()

    def open_screen_realtime(self):
        self.screen_manager.current = 'screen_realtime'

    def exec_back(self):
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

    def exec_navigate_realtime(self):
        try:
            self.screen_manager.current = 'screen_realtime'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
            toast(toast_msg)   

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
        global flag_play
        global count_starting, count_get_data
        global mydb, db_antrian
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_check_flag, dt_check_user, dt_check_post

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

class ScreenInspectVisual(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenInspectVisual, self).__init__(**kwargs)
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
        global flag_play
        global count_starting, count_get_data
        global mydb, db_antrian
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_check_flag, dt_check_user, dt_check_post

        self.open_screen_menu()

    def exec_cancel(self):
        self.open_screen_menu()

    def exec_body(self):
        global flag_body

        try:
            if(flag_body):
                flag_body = False
                self.ids.bt_body.icon = "cancel"
                self.ids.bt_body.md_bg_color = "#FF2A2A"
            else:
                flag_body = True
                self.ids.bt_body.icon = "check-bold"
                self.ids.bt_body.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_roda(self):
        global flag_roda

        try:
            if(flag_roda):
                flag_roda = False
                self.ids.bt_roda.icon = "cancel"
                self.ids.bt_roda.md_bg_color = "#FF2A2A"
            else:
                flag_roda = True
                self.ids.bt_roda.icon = "check-bold"
                self.ids.bt_roda.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_spion(self):
        global flag_spion

        try:
            if(flag_spion):
                flag_spion = False
                self.ids.bt_spion.icon = "cancel"
                self.ids.bt_spion.md_bg_color = "#FF2A2A"
            else:
                flag_spion = True
                self.ids.bt_spion.icon = "check-bold"
                self.ids.bt_spion.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_penyapu(self):
        global flag_penyapu

        try:
            if(flag_penyapu):
                flag_penyapu = False
                self.ids.bt_penyapu.icon = "cancel"
                self.ids.bt_penyapu.md_bg_color = "#FF2A2A"
            else:
                flag_penyapu = True
                self.ids.bt_penyapu.icon = "check-bold"
                self.ids.bt_penyapu.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_sabuk(self):
        global flag_sabuk

        try:
            if(flag_sabuk):
                flag_sabuk = False
                self.ids.bt_sabuk.icon = "cancel"
                self.ids.bt_sabuk.md_bg_color = "#FF2A2A"
            else:
                flag_sabuk = True
                self.ids.bt_sabuk.icon = "check-bold"
                self.ids.bt_sabuk.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_bumper(self):
        global flag_bumper

        try:
            if(flag_bumper):
                flag_bumper = False
                self.ids.bt_bumper.icon = "cancel"
                self.ids.bt_bumper.md_bg_color = "#FF2A2A"
            else:
                flag_bumper = True
                self.ids.bt_bumper.icon = "check-bold"
                self.ids.bt_bumper.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_lampu(self):
        global flag_lampu

        try:
            if(flag_lampu):
                flag_lampu = False
                self.ids.bt_lampu.icon = "cancel"
                self.ids.bt_lampu.md_bg_color = "#FF2A2A"
            else:
                flag_lampu = True
                self.ids.bt_lampu.icon = "check-bold"
                self.ids.bt_lampu.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_kaca(self):
        global flag_kaca

        try:
            if(flag_kaca):
                flag_kaca = False
                self.ids.bt_kaca.icon = "cancel"
                self.ids.bt_kaca.md_bg_color = "#FF2A2A"
            else:
                flag_kaca = True
                self.ids.bt_kaca.icon = "check-bold"
                self.ids.bt_kaca.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_motor(self):
        global flag_motor

        try:
            if(flag_motor):
                flag_motor = False
                self.ids.bt_motor.icon = "cancel"
                self.ids.bt_motor.md_bg_color = "#FF2A2A"
            else:
                flag_motor = True
                self.ids.bt_motor.icon = "check-bold"
                self.ids.bt_motor.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_spakbor(self):
        global flag_spakbor

        try:
            if(flag_spakbor):
                flag_spakbor = False
                self.ids.bt_spakbor.icon = "cancel"
                self.ids.bt_spakbor.md_bg_color = "#FF2A2A"
            else:
                flag_spakbor = True
                self.ids.bt_spakbor.icon = "check-bold"
                self.ids.bt_spakbor.md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_body_sub(self, num):
        global flag_body_sub

        try:
            for i in range(flag_body_sub.size):
                if(flag_body_sub[num]):
                    flag_body_sub[num] = False
                    self.ids[f'bt_body_sub{num}'].icon = "cancel"
                    self.ids[f'bt_body_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_body_sub[num] = True
                    self.ids[f'bt_body_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_body_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_roda_sub(self, num):
        global flag_roda_sub

        try:
            for i in range(flag_roda_sub.size):
                if(flag_roda_sub[num]):
                    flag_roda_sub[num] = False
                    self.ids[f'bt_roda_sub{num}'].icon = "cancel"
                    self.ids[f'bt_roda_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_roda_sub[num] = True
                    self.ids[f'bt_roda_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_roda_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_spion_sub(self, num):
        global flag_spion_sub

        try:
            for i in range(flag_spion_sub.size):
                if(flag_spion_sub[num]):
                    flag_spion_sub[num] = False
                    self.ids[f'bt_spion_sub{num}'].icon = "cancel"
                    self.ids[f'bt_spion_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_spion_sub[num] = True
                    self.ids[f'bt_spion_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_spion_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_penyapu_sub(self, num):
        global flag_penyapu_sub

        try:
            for i in range(flag_penyapu_sub.size):
                if(flag_penyapu_sub[num]):
                    flag_penyapu_sub[num] = False
                    self.ids[f'bt_penyapu_sub{num}'].icon = "cancel"
                    self.ids[f'bt_penyapu_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_penyapu_sub[num] = True
                    self.ids[f'bt_penyapu_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_penyapu_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_sabuk_sub(self, num):
        global flag_sabuk_sub

        try:
            for i in range(flag_sabuk_sub.size):
                if(flag_sabuk_sub[num]):
                    flag_sabuk_sub[num] = False
                    self.ids[f'bt_sabuk_sub{num}'].icon = "cancel"
                    self.ids[f'bt_sabuk_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_sabuk_sub[num] = True
                    self.ids[f'bt_sabuk_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_sabuk_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_bumper_sub(self, num):
        global flag_bumper_sub

        try:
            for i in range(flag_bumper_sub.size):
                if(flag_bumper_sub[num]):
                    flag_bumper_sub[num] = False
                    self.ids[f'bt_bumper_sub{num}'].icon = "cancel"
                    self.ids[f'bt_bumper_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_bumper_sub[num] = True
                    self.ids[f'bt_bumper_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_bumper_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_kaca_sub(self, num):
        global flag_kaca_sub

        try:
            for i in range(flag_kaca_sub.size):
                if(flag_kaca_sub[num]):
                    flag_kaca_sub[num] = False
                    self.ids[f'bt_kaca_sub{num}'].icon = "cancel"
                    self.ids[f'bt_kaca_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_kaca_sub[num] = True
                    self.ids[f'bt_kaca_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_kaca_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_motor_sub(self, num):
        global flag_motor_sub

        try:
            for i in range(flag_motor_sub.size):
                if(flag_motor_sub[num]):
                    flag_motor_sub[num] = False
                    self.ids[f'bt_motor_sub{num}'].icon = "cancel"
                    self.ids[f'bt_motor_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_motor_sub[num] = True
                    self.ids[f'bt_motor_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_motor_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def exec_spakbor_sub(self, num):
        global flag_spakbor_sub

        try:
            for i in range(flag_spakbor_sub.size):
                if(flag_spakbor_sub[num]):
                    flag_spakbor_sub[num] = False
                    self.ids[f'bt_spakbor_sub{num}'].icon = "cancel"
                    self.ids[f'bt_spakbor_sub{num}'].md_bg_color = "#FF2A2A"
                else:
                    flag_spakbor_sub[num] = True
                    self.ids[f'bt_spakbor_sub{num}'].icon = "check-bold"
                    self.ids[f'bt_spakbor_sub{num}'].md_bg_color = "#2CA02C"

        except Exception as e:
            toast_msg = f'Error Visual Inspect: {e}'
            toast(toast_msg)  

    def open_sub_body(self):
        self.ids.layout_sub_body.opacity = 1
        self.ids.layout_sub_body.height = '560dp'
        self.ids.layout_sub_roda.disabled = False
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0.0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0.0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0.0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0.0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0.0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_roda(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 1
        self.ids.layout_sub_roda.height = '560dp'
        self.ids.layout_sub_roda.disabled = False
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0.0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0.0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0.0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0.0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_spion(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 1
        self.ids.layout_sub_spion.height = '560dp'
        self.ids.layout_sub_spion.disabled = False
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0.0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0.0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0.0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_penyapu(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 1
        self.ids.layout_sub_penyapu.height = '560dp'
        self.ids.layout_sub_penyapu.disabled = False
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0.0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0.0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_sabuk(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 1
        self.ids.layout_sub_sabuk.height = '560dp'
        self.ids.layout_sub_sabuk.disabled = False
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0.0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_bumper(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 1
        self.ids.layout_sub_bumper.height = '560dp'
        self.ids.layout_sub_bumper.disabled = False
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_lampu(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_kaca(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 1
        self.ids.layout_sub_kaca.height = '560dp'
        self.ids.layout_sub_kaca.disabled = False
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_motor(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 1
        self.ids.layout_sub_motor.height = '560dp'
        self.ids.layout_sub_motor.disabled = False
        self.ids.layout_sub_spakbor.opacity = 0
        self.ids.layout_sub_spakbor.height = 0.0
        self.ids.layout_sub_spakbor.disabled = True

    def open_sub_spakbor(self):
        self.ids.layout_sub_body.opacity = 0
        self.ids.layout_sub_body.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_roda.opacity = 0
        self.ids.layout_sub_roda.height = 0
        self.ids.layout_sub_roda.disabled = True
        self.ids.layout_sub_spion.opacity = 0
        self.ids.layout_sub_spion.height = 0
        self.ids.layout_sub_spion.disabled = True
        self.ids.layout_sub_penyapu.opacity = 0
        self.ids.layout_sub_penyapu.height = 0
        self.ids.layout_sub_penyapu.disabled = True
        self.ids.layout_sub_sabuk.opacity = 0
        self.ids.layout_sub_sabuk.height = 0
        self.ids.layout_sub_sabuk.disabled = True
        self.ids.layout_sub_bumper.opacity = 0
        self.ids.layout_sub_bumper.height = 0
        self.ids.layout_sub_bumper.disabled = True
        self.ids.layout_sub_kaca.opacity = 0
        self.ids.layout_sub_kaca.height = 0.0
        self.ids.layout_sub_kaca.disabled = True
        self.ids.layout_sub_motor.opacity = 0
        self.ids.layout_sub_motor.height = 0.0
        self.ids.layout_sub_motor.disabled = True
        self.ids.layout_sub_spakbor.opacity = 1
        self.ids.layout_sub_spakbor.height = '560dp'
        self.ids.layout_sub_spakbor.disabled = False

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
        # Window.size = 900, 1440
        # Window.size = 450, 720
        # Window.allow_screensaver = True

        Builder.load_file('main.kv')
        return RootScreen()

if __name__ == '__main__':
    PlayDetectorApp().run()