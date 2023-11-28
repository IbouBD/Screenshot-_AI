# Screenshot AI with Replicate

This Python script allows you to capture a screenshot, send it to OpenAI's Replicate API for text generation, and display the generated text in a Tkinter window.

## Prerequisites

Make sure you have the required Python packages installed. You can install them using the following:

```bash
pip install pyautogui pyscreenshot pynput PyQt5
```
Additionally, you need a Replicate API key. You can sign up for Replicate and obtain an API key from https://beta.replicate.ai/.

Usage
Run the script using the following command:

```bash
python script_runner.py
```
The script will open a PyQt window with input fields for the prompt, Replicate API key, and delay. Enter the required information.

Click the "Start Capture" button to capture a screenshot and generate text.

The generated text will be displayed in a Tkinter window.

Adjust the delay parameter to control how long the Tkinter window stays open.

Configuration
The script saves your prompt, Replicate API key, and delay settings in a config.json file. These settings will be loaded automatically the next time you run the script.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
OpenAI for the Replicate API.
PyQt for the GUI library.

Ia can now explain your screenshot
