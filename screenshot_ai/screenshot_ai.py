import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QFormLayout, QLineEdit, QSlider, QSpinBox
from PyQt5.QtCore import Qt
import pyscreenshot
from pynput import mouse
import replicate
import os
import tkinter as tk
import json
import json


class ScriptRunner(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

        with open('Screenshot-_AI\screenshot_ai\config.json') as f:
            data = json.load(f)
            self.prompt_entry.setText(data['prompt'])
            self.api_entry.setText(data['api_key'])
            self.delay_entry.setValue(int(data['delay']))
            self.opacity_slider.setValue(int(data['opacity']))
            self.height_spinbox.setValue(int(data['height']))
            self.width_spinbox.setValue(int(data['width']))
            self.y_spinbox.setValue(int(data['y']))

    def initUI(self):
        run_button = QPushButton('Start Capture', self)
        run_button.clicked.connect(self.runScript)

        self.prompt_entry = QLineEdit(self)
        self.prompt_entry.setPlaceholderText('Enter Prompt...')

        self.api_entry = QLineEdit(self)
        self.api_entry.setPlaceholderText('Enter Replicate key...')

        self.delay_entry = QSpinBox()
        self.delay_entry.setMinimum(1)
        self.delay_entry.setMaximum(120)
        self.delay_entry.setValue(20)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(95)
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setMinimum(100)
        self.height_spinbox.setMaximum(1000)
        self.height_spinbox.setValue(200)

        self.width_spinbox = QSpinBox()
        self.width_spinbox.setMinimum(100)
        self.width_spinbox.setMaximum(3000)
        self.width_spinbox.setValue(1500)

        self.y_spinbox = QSpinBox()
        self.y_spinbox.setMinimum(0)
        self.y_spinbox.setMaximum(1200)
        self.y_spinbox.setValue(0)

        quit_button = QPushButton('Quit', self)
        quit_button.clicked.connect(self.close)

        layout = QFormLayout()
        layout.addRow('Prompt:', self.prompt_entry)
        layout.addRow('Api key:', self.api_entry)
        layout.addRow('Delay:', self.delay_entry)
        layout.addRow('Opacity:', self.opacity_slider)
        layout.addRow('Height:', self.height_spinbox)
        layout.addRow('Width:', self.width_spinbox)
        layout.addRow('Y:', self.y_spinbox)
        layout.addRow(run_button)
        layout.addRow(quit_button)

        self.setLayout(layout)

        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Screenshot AI')

    def runScript(self):
        try:
            prompt_text = self.prompt_entry.text()
            api_text = self.api_entry.text()
            delay = int(self.delay_entry.text()) * 1000
            opacity = float(self.opacity_slider.value()) / 100
            H = int(self.height_spinbox.text())
            W = int(self.width_spinbox.text())
            Y = int(self.y_spinbox.text())

            def on_click(x, y, button, pressed):
                if pressed:
                    global X1
                    X1 = x
                    global Y1
                    Y1 = y

                global X2
                X2 = x
                global Y2
                Y2 = y
                print('{0} at {1}'.format(
                    'Pressed' if pressed else 'Released',
                    (x, y)))

                if not pressed:
                    return False

            with mouse.Listener(on_click=on_click) as listener:
                listener.block = True
                listener.join()

            image = pyscreenshot.grab(bbox=(X1, Y1, X2, Y2))

            image.show()

            image.save('screen.jpg')

            os.environ["REPLICATE_API_TOKEN"] = api_text

            image = open('screen.jpg', "rb")

            output = replicate.run(
                "yorickvp/llava-13b:e272157381e2a3bf12df3a8edd1f38d1dbd736bbb7437277c8b34175f8fce358",
                input={
                    "image": image,
                    "top_p": 1,
                    "prompt": prompt_text,
                    "max_tokens": 1024,
                    "temperature": 0.2
                }
            )

            root = tk.Tk()
            root.wm_attributes("-topmost", 1)
            root.lift()
            root.attributes("-alpha", 0.8)
            root.attributes("-disabled", True)

            # Récupérer la taille de l'écran
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Calculer la position
            x = int((screen_width / 2) - (W / 2))
            X = x

            # Définir la géométrie
            root.geometry(f'{W}x{H}+{X}+{Y}')

            root.overrideredirect(1)

            text_output = tk.Text(root, width=1500, height=100, bg='#151A20', font=("Helvetica", 16), padx=20, pady=20,
                                  fg='white', bd=0, )

            text_output.pack()

            def set_opacity(window, opacity):
                window.attributes('-alpha', opacity)

            def close_window():
                root.destroy()

            set_opacity(root, opacity)

            def display_prediction():
                for prediction in output:
                    text_output.insert(tk.END, prediction + " ")
                    text_output.update()
                    root.after(50)
                    root.after(delay, close_window)

            display_prediction()
            root.mainloop()

        except Exception as e:
            QMessageBox.critical(self, 'Erreur', f"Une erreur s'est produite : {str(e)}")

    def save_config(self):
        data = {}
        data['prompt'] = self.prompt_entry.text()
        data['api_key'] = self.api_entry.text()
        data['delay'] = self.delay_entry.text()
        data['opacity'] = self.opacity_slider.value()
        data['height'] = self.height_spinbox.text()
        data['width'] = self.width_spinbox.text()
        data['y'] = self.y_spinbox.text()

        with open('config.json', 'w') as f:
                    json.dump(data, f)

    def closeEvent(self, event):
                    self.save_config()
                    event.accept()


if __name__ == '__main__':
            app = QApplication(sys.argv)
            ex = ScriptRunner()
            ex.show()
            sys.exit(app.exec_())
