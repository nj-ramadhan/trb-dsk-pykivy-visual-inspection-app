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

dt_user = ""
dt_no_antrian = ""
dt_no_reg = ""
dt_no_uji = ""
dt_nama = ""
dt_jenis_kendaraan = ""

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
            self.screen_manager.current = 'screen_main'

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

        try:
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
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
            toast(toast_msg)   

class ScreenMain(MDScreen):   
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        global mydb, db_antrian
        global flag_conn_stat, flag_play
        global count_starting, count_get_data

        Clock.schedule_once(self.delayed_init, 1)

        flag_conn_stat = False
        flag_play = False

        count_starting = COUNT_STARTING
        count_get_data = COUNT_ACQUISITION

        try:
            mydb = mysql.connector.connect(host = DB_HOST,user = DB_USER,password = DB_PASSWORD,database = DB_NAME)

        except Exception as e:
            toast_msg = f'Error Initiate Database: {e}'
            toast(toast_msg)                      

    def delayed_init(self, dt):
        Clock.schedule_interval(self.regular_update_display, 1)
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
            screen_gate_control = self.screen_manager.get_screen('screen_gate_control')
            screen_play_detect = self.screen_manager.get_screen('screen_play_detect')

            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_home.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_home.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_login.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_login.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_gate_control.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_gate_control.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_play_detect.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_play_detect.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_no_antrian.text = str(dt_no_antrian)
            self.ids.lb_no_reg.text = str(dt_no_reg)
            self.ids.lb_no_uji.text = str(dt_no_uji)
            self.ids.lb_nama.text = str(dt_nama)
            self.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            screen_gate_control.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_gate_control.ids.lb_no_reg.text = str(dt_no_reg)
            screen_gate_control.ids.lb_no_uji.text = str(dt_no_uji)
            screen_gate_control.ids.lb_nama.text = str(dt_nama)
            screen_gate_control.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            screen_play_detect.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_play_detect.ids.lb_no_reg.text = str(dt_no_reg)
            screen_play_detect.ids.lb_no_uji.text = str(dt_no_uji)
            screen_play_detect.ids.lb_nama.text = str(dt_nama)
            screen_play_detect.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

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
            screen_gate_control.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'
            screen_play_detect.ids.lb_operator.text = f'Login Sebagai: {dt_user}' if dt_user != '' else 'Silahkan Login'

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
        global flag_play

        if(not flag_play):
            Clock.schedule_interval(self.regular_get_data, 1)
            self.open_screen_gate_control()
            flag_play = True

    def open_screen_gate_control(self):
        self.screen_manager.current = 'screen_gate_control'

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
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
            toast(toast_msg)   

class ScreenGateControl(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenGateControl, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        # Clock.schedule_interval(self.update_frame, 1)
        
    def delayed_init(self, dt):
        pass

    def exec_gate_open(self):
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

    def exec_gate_close(self):
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

    def exec_gate_stop(self):
        global flag_conn_stat

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3072, False, slave=1) #M0
                modbus_client.write_coil(3073, False, slave=1) #M1
                modbus_client.close()
        except:
            toast("error send exec_gate_stop data to PLC Slave") 

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
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
            toast(toast_msg)   

class ScreenPlayDetect(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenPlayDetect, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, 2)
        # Clock.schedule_interval(self.update_frame, 1)
        
    def delayed_init(self, dt):
        pass

    def exec_gate_open(self):
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

    def exec_gate_close(self):
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

    def exec_gate_stop(self):
        global flag_conn_stat

        try:
            if flag_conn_stat:
                modbus_client.connect()
                modbus_client.write_coil(3072, False, slave=1) #M0
                modbus_client.write_coil(3073, False, slave=1) #M1
                modbus_client.close()
        except:
            toast("error send exec_gate_stop data to PLC Slave") 

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

    def open_screen_gate_control(self):
        self.screen_manager.current = 'screen_gate_control'

    def exec_back(self):
        self.open_screen_gate_control()

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
            self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'Error Navigate to Realtime CCTV Streaming Screen: {e}'
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

        theme_font_styles.append('Display')
        self.theme_cls.font_styles["Display"] = [
            "Orbitron-Regular", 72, False, 0.15]       
        
        Window.fullscreen = 'auto'
        # Window.borderless = False
        # Window.size = 900, 1440
        # Window.size = 450, 720
        # Window.allow_screensaver = True

        Builder.load_file('main.kv')
        return RootScreen()

if __name__ == '__main__':
    PlayDetectorApp().run()