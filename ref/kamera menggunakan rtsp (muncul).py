import cv2
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class HikvisionCameraApp(App):
    def build(self):
        # URL RTSP dari kamera Hikvision
        # rtsp_url = 'rtsp://admin:polinema789@192.168.1.64:554/Streaming/Channels/101'
        rtsp_url = 'rtsp://admin:TRBintegrated202@192.168.1.64:554/Streaming/Channels/101'

        # Membuka stream video menggunakan OpenCV
        self.capture = cv2.VideoCapture(rtsp_url)

        # Membuat widget Image untuk menampilkan frame video
        self.img_widget = Image()

        # Menjalankan update frame setiap 1/30 detik (30 FPS)
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)

        return self.img_widget

    def update_frame(self, dt):
        # Membaca frame dari stream
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
            self.img_widget.texture = texture

    def on_stop(self):
        # Lepas kamera saat aplikasi berhenti
        self.capture.release()

if __name__ == '__main__':
    HikvisionCameraApp().run()
