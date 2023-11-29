import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QFormLayout, QLineEdit
from subprocess import Popen, PIPE
import pyscreenshot
from pynput import mouse
import replicate
import os
import tkinter as tk
import json


class ScriptRunner(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

        with open('Screenshot-_AI\screenshot_ai\config.json') as f:
            data = json.load(f)
            self.prompt_entry.setText(data['prompt'])
            self.api_entry.setText(data['api_key'])
            self.delay_entry.setText(data['delay'])

    def initUI(self):
            # Créer un bouton pour lancer le script
            run_button = QPushButton('Start Capture', self)
            run_button.clicked.connect(self.runScript)

            # Créer une QLineEdit pour le prompt
            self.prompt_entry = QLineEdit(self)
            self.prompt_entry.setPlaceholderText('Enter Prompt...')

            # Créer une QLineEdit pour la clé d'api
            self.api_entry = QLineEdit(self)
            self.api_entry.setPlaceholderText('Enter Replicate key...')

            self.delay_entry = QLineEdit(self)
            self.delay_entry.setPlaceholderText('duration of text (second)')

            # Créer un bouton pour quitter l'application
            quit_button = QPushButton('Quit', self)
            quit_button.clicked.connect(self.close)

            # Disposer les boutons et l'entrée du prompt verticalement
            layout = QFormLayout()
            layout.addRow('Prompt:', self.prompt_entry)
            layout.addRow('Api key:', self.api_entry)
            layout.addRow('Delay:', self.delay_entry)
            layout.addRow(run_button)
            layout.addRow(quit_button)

            self.setLayout(layout)

            # Paramètres de la fenêtre
            self.setGeometry(300, 300, 300, 150)
            self.setWindowTitle('Screenshot AI')

    def runScript(self):
            try:
                prompt_text = self.prompt_entry.text()
                api_text = self.api_entry.text()
                delay = int(self.delay_entry.text()) * 1000

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

                # To display the captured screenshot
                image.show()

                image.save("screen.jpg")

                os.environ["REPLICATE_API_TOKEN"] = api_text

                image = open("screen.jpg", "rb")

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

                # Création de la fenêtre
                root = tk.Tk()
                root.wm_attributes("-topmost", 1)
                root.lift()
                root.attributes("-alpha", 0.8)
                root.attributes("-disabled", True)

                root.minsize(1500, 200)
                root.maxsize(1500, 200)
                # Récupérer la taille de l'écran
                screen_width = root.winfo_screenwidth()  
                screen_height = root.winfo_screenheight()
                width = 1500
                height = 200

                # Calculer la position
                x = int((screen_width / 2) - (width / 2))
                y = int(screen_height - (height*3))

                # Définir la géométrie  
                root.geometry(f'{width}x{height}+{x}+{y}')

                root.overrideredirect(1)

                # Création d'un widget Text pour afficher les prédictions dans la fenêtre principale
                text_output = tk.Text(root, width=1500, height=100, bg='#151A20', font=("Helvetica", 16),padx=20, pady=20 , fg='white', bd=0,)


                text_output.pack()
                def set_opacity(window, opacity):
                    window.attributes('-alpha', opacity)

                def close_window():
                    root.destroy()

                set_opacity(root, 0.95)

                def display_prediction():
                    for prediction in output:
                        text_output.insert(tk.END, prediction + " ")
                        text_output.update()
                        root.after(50) # Attendre 1 seconde avant d'afficher la prédiction suivante
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
