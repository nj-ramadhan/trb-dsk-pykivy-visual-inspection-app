from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics.texture import Texture
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.datatables import MDDataTable
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.metrics import dp
from kivymd.toast import toast
import numpy as np
import time
import mysql.connector
from escpos.printer import Serial as printerSerial
import configparser
import serial.tools.list_ports as ports
import hashlib
import serial
import cv2
from pymodbus.client import ModbusTcpClient

colors = {
    "Red": {
        "A200": "#FF2A2A",
        "A500": "#FF8080",
        "A700": "#FFD5D5",
    },

    "Gray": {
        "200": "#CCCCCC",
        "500": "#ECECEC",
        "700": "#F9F9F9",
    },

    "Blue": {
        "200": "#4471C4",
        "500": "#5885D8",
        "700": "#6C99EC",
    },

    "Green": {
        "200": "#2CA02C", #41cd93
        "500": "#2DB97F",
        "700": "#D5FFD5",
    },

    "Yellow": {
        "200": "#ffD42A",
        "500": "#ffE680",
        "700": "#fff6D5",
    },

    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#EEEEEE",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },

    "Dark": {
        "StatusBar": "101010",
        "AppBar": "#E0E0E0",
        "Background": "#111111",
        "CardsDialogs": "#222222",
        "FlatButtonDown": "#DDDDDD",
    },
}

#load credentials from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
DB_HOST = config['mysql']['DB_HOST']
DB_USER = config['mysql']['DB_USER']
DB_PASSWORD = config['mysql']['DB_PASSWORD']
DB_NAME = config['mysql']['DB_NAME']
TB_WTM = config['mysql']['TB_WTM']
TB_USER = config['mysql']['TB_USER']

COM_PORT_PRINTER = config['device']['COM_PORT_PRINTER']
COM_PORT_WTM = config['device']['COM_PORT_WTM']
TIME_OUT = 500

rtsp_url_cam1 = 'rtsp://admin:TRBintegrated202@192.168.1.64:554/Streaming/Channels/101'

dt_wtm_value = 0
dt_wtm_flag = 0
dt_wtm_user = 1
dt_wtm_post = str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
dt_user = "SILAHKAN LOGIN"
dt_no_antrian = ""
dt_no_reg = ""
dt_no_uji = ""
dt_nama = ""
dt_jenis_kendaraan = ""

modbus_client = ModbusTcpClient('192.168.1.111')

flag_gate = False
side_slip_val = 0
axle_load_l_val = 0
axle_load_r_val = 0
speed_val = 0

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
        global dt_wtm_user, dt_user

        try:
            input_username = self.ids.tx_username.text
            input_password = self.ids.tx_password.text        
            # Adding salt at the last of the password
            dataBase_password = input_password
            # Encoding the password
            hashed_password = hashlib.md5(dataBase_password.encode())

            mycursor = mydb.cursor()
            mycursor.execute("SELECT id_user, nama, username, password, nama FROM users WHERE username = '"+str(input_username)+"' and password = '"+str(hashed_password.hexdigest())+"'")
            myresult = mycursor.fetchone()
            db_users = np.array(myresult).T
            #if invalid
            if myresult == 0:
                toast('Gagal Masuk, Nama Pengguna atau Password Salah')
            #else, if valid
            else:
                toast_msg = f'Berhasil Masuk, Selamat Datang {myresult[1]}'
                toast(toast_msg)
                dt_wtm_user = myresult[0]
                dt_user = myresult[1]
                self.ids.tx_username.text = ""
                self.ids.tx_password.text = "" 
                self.screen_manager.current = 'screen_main'

        except Exception as e:
            toast_msg = f'error Login: {e}'
            toast(toast_msg)        
            toast('Gagal Masuk, Nama Pengguna atau Password Salah')

class ScreenMain(MDScreen):   
    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)
        global mydb, db_antrian
        global flag_conn_stat, flag_play
        global count_starting, count_get_data

        Clock.schedule_once(self.delayed_init, 1)

        flag_conn_stat = False
        flag_play = False

        count_starting = 3
        count_get_data = 4
        try:
            mydb = mysql.connector.connect(
            host = DB_HOST,
            user = DB_USER,
            password = DB_PASSWORD,
            database = DB_NAME
            )

        except Exception as e:
            toast_msg = f'error initiate Database: {e}'
            toast(toast_msg)     
        
    def delayed_init(self, dt):
        Clock.schedule_interval(self.regular_update_connection, 5)
        Clock.schedule_interval(self.regular_get_data, 0.5)
        Clock.schedule_interval(self.regular_update_display, 0.5)
        # Clock.schedule_interval(self.regular_highspeed_display, 0.5)
        layout = self.ids.layout_table
        
        self.data_tables = MDDataTable(
            use_pagination=True,
            pagination_menu_pos="auto",
            rows_num=10,
            column_data=[
                ("No.", dp(10), self.sort_on_num),
                ("Antrian", dp(20)),
                ("No. Reg", dp(25)),
                ("No. Uji", dp(35)),
                ("Nama", dp(35)),
                ("Jenis", dp(50)),
                ("Status", dp(20)),
            ],
        )
        self.data_tables.bind(on_row_press=self.on_row_press)
        layout.add_widget(self.data_tables)
        self.exec_reload_table()


    def regular_update_connection(self, dt):
        global flag_conn_stat

        try:
            modbus_client.connect()
            flag_conn_stat = modbus_client.connected
            modbus_client.close()

            # com_ports = list(ports.comports()) # create a list of com ['COM1','COM2'] 
            # for i in com_ports:
            #     if i.name == COM_PORT_PRINTER:
            #         flag_conn_stat = True

            # printer = printerSerial(devfile = COM_PORT_PRINTER,
            #         baudrate = 38400,
            #         bytesize = 8,
            #         parity = 'N',
            #         stopbits = 1,
            #         timeout = 1.00,
            #         dsrdtr = True)    

            # wtm_device = serial.Serial()
            # wtm_device.baudrate = 115200
            # wtm_device.port = COM_PORT_WTM
            # parity=serial.PARITY_NONE,
            # stopbits=serial.STOPBITS_ONE,
            # bytesize=serial.EIGHTBITS        
            
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
            Logger.error(e)

    # def regular_highspeed_display(self, dt):
    #     try:
    #         pass           

    #     except Exception as e:
    #         Logger.error(e)


    def sort_on_num(self, data):
        try:
            return zip(*sorted(enumerate(data),key=lambda l: l[0][0]))
        except:
            toast("Error sorting data")

    def on_row_press(self, table, row):
        global dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_wtm_flag, dt_wtm_value, dt_wtm_user, dt_wtm_post

        try:
            start_index, end_index  = row.table.recycle_data[row.index]["range"]
            dt_no_antrian           = row.table.recycle_data[start_index + 1]["text"]
            dt_no_reg               = row.table.recycle_data[start_index + 2]["text"]
            dt_no_uji               = row.table.recycle_data[start_index + 3]["text"]
            dt_nama                 = row.table.recycle_data[start_index + 4]["text"]
            dt_jenis_kendaraan      = row.table.recycle_data[start_index + 5]["text"]
            dt_wtm_flag             = row.table.recycle_data[start_index + 6]["text"]

        except Exception as e:
            toast_msg = f'error update table: {e}'
            toast(toast_msg)   

    def regular_update_display(self, dt):
        global flag_conn_stat
        global dt_wtm_value, count_starting, count_get_data
        global dt_user, dt_no_antrian, dt_no_reg, dt_no_uji, dt_nama, dt_jenis_kendaraan
        global dt_wtm_flag, dt_wtm_value, dt_wtm_user, dt_wtm_post
        global side_slip_val, axle_load_l_val, axle_load_r_val, speed_val
        try:
            screen_login = self.screen_manager.get_screen('screen_login')
            screen_control = self.screen_manager.get_screen('screen_control')

            self.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            self.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_login.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_login.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))
            screen_control.ids.lb_time.text = str(time.strftime("%H:%M:%S", time.localtime()))
            screen_control.ids.lb_date.text = str(time.strftime("%d/%m/%Y", time.localtime()))

            self.ids.lb_no_antrian.text = str(dt_no_antrian)
            self.ids.lb_no_reg.text = str(dt_no_reg)
            self.ids.lb_no_uji.text = str(dt_no_uji)
            self.ids.lb_nama.text = str(dt_nama)
            self.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            screen_control.ids.lb_no_antrian.text = str(dt_no_antrian)
            screen_control.ids.lb_no_reg.text = str(dt_no_reg)
            screen_control.ids.lb_no_uji.text = str(dt_no_uji)
            screen_control.ids.lb_nama.text = str(dt_nama)
            screen_control.ids.lb_jenis_kendaraan.text = str(dt_jenis_kendaraan)

            screen_control.ids.lb_side_slip_val.text = str(side_slip_val)
            screen_control.ids.lb_axle_load_l_val.text = str(axle_load_l_val)
            screen_control.ids.lb_axle_load_r_val.text = str(axle_load_r_val)
            screen_control.ids.lb_speed_val.text = str(speed_val)


            if(dt_wtm_flag == "Belum Tes"):
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

            self.ids.lb_operator.text = dt_user
            screen_login.ids.lb_operator.text = dt_user
            screen_control.ids.lb_operator.text = dt_user

        except Exception as e:
            toast_msg = f'error update display: {e}'
            toast(toast_msg)                

    def exec_reload_table(self):
        global mydb, db_antrian
        try:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT noantrian, nopol, nouji, user, idjeniskendaraan, wtm_flag FROM tb_cekident")
            myresult = mycursor.fetchall()
            db_antrian = np.array(myresult).T

            self.data_tables.row_data=[(f"{i+1}", f"{db_antrian[0, i]}", f"{db_antrian[1, i]}", f"{db_antrian[2, i]}", f"{db_antrian[3, i]}" ,f"{db_antrian[4, i]}", 
                                        'Belum Tes' if (int(db_antrian[5, i]) == 0) else ('Lulus' if (int(db_antrian[5, i]) == 1) else 'Tidak Lulus')) 
                                        for i in range(len(db_antrian[0]))]

        except Exception as e:
            toast_msg = f'error reload table: {e}'
            print(toast_msg)

    def exec_start(self):
        global flag_play

        if(not flag_play):
            Clock.schedule_interval(self.regular_get_data, 1)
            self.open_screen_control()
            flag_play = True

            # stream.close()
            # audio.terminate()  

    def open_screen_control(self):
        self.screen_manager.current = 'screen_control'

    def exec_logout(self):
        self.screen_manager.current = 'screen_login'

class ScreenControl(MDScreen):        
    def __init__(self, **kwargs):
        super(ScreenControl, self).__init__(**kwargs)
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
        global dt_wtm_flag, dt_wtm_value, dt_wtm_user, dt_wtm_post

        self.open_screen_main()

    def open_screen_main(self):
        global flag_play        
        global count_starting, count_get_data

        screen_main = self.screen_manager.get_screen('screen_main')

        count_starting = 3
        count_get_data = 10
        flag_play = False   
        screen_main.exec_reload_table()
        self.screen_manager.current = 'screen_main'

    def exec_logout(self):
        self.screen_manager.current = 'screen_login'

class RootScreen(ScreenManager):
    pass             

class SoundLevelMeterApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.icon = 'assets/logo.png'

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
    SoundLevelMeterApp().run()