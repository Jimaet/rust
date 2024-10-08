import tkinter as tk
import json
import os
import pynput
import time
import pyautogui
import pytesseract
from PIL import ImageTk, Image

# Укажите путь к исполняемому файлу Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Основные переменные
actions = []
recording = False
last_time = None
current_file = None
number_checks = []  # Список для проверки последнего числа

keyboard_controller = pynput.keyboard.Controller()

# Функции для работы с json файлами
def clear_json_file(file_name):
    with open(file_name, "w") as file:
        json.dump([], file, indent=4)
    print(f"Файл {file_name} очищен.")

def save_actions(file_name):
    with open(file_name, "w") as file:
        json.dump(actions, file, indent=4)
    print(f"Запись сохранена в {file_name}.")
    reset_recording()  # Сбрасываем переменные после сохранения

def reset_recording():
    global actions, recording, last_time
    actions.clear()
    recording = False
    last_time = None

def play_actions(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            recorded_actions = json.load(file)
            if not recorded_actions:
                print(f"Файл {file_name} пуст.")
                return
            
            print(f"Проигрываю действия из файла {file_name}")
            time.sleep(2)  # Задержка 2 секунды перед началом воспроизведения
            for action in recorded_actions:
                elapsed_time = action['time']
                time.sleep(elapsed_time)  # Задержка до следующего действия

                if action['type'] == 'key_press':
                    try:
                        key = getattr(pynput.keyboard.Key, action['key'].split('.')[1]) if 'Key.' in action['key'] else action['key']
                        keyboard_controller.press(key)
                    except AttributeError:
                        keyboard_controller.press(action['key'])
                elif action['type'] == 'key_release':
                    try:
                        key = getattr(pynput.keyboard.Key, action['key'].split('.')[1]) if 'Key.' in action['key'] else action['key']
                        keyboard_controller.release(key)
                    except AttributeError:
                        keyboard_controller.release(action['key'])
            print(f"Проигрывание {file_name} завершено.")
    else:
        print(f"Файл {file_name} не существует.")

def on_key_press(key):
    global recording, current_file
    if recording:
        try:
            actions.append({'type': 'key_press', 'key': key.char, 'time': get_time()})
        except AttributeError:
            actions.append({'type': 'key_press', 'key': str(key), 'time': get_time()})

def on_key_release(key):
    global recording, current_file
    if key == pynput.keyboard.KeyCode(char='u'):
        if recording:
            save_actions(current_file)
        else:
            recording = True
            print(f"Запись началась для {current_file}.")
        return
    
    # Обработка нажатий для воспроизведения файлов
    if not recording:
        if key == pynput.keyboard.KeyCode(char='z'):
            play_actions("actions_1.json")
        elif key == pynput.keyboard.KeyCode(char='x'):
            play_actions("actions_2.json")
        elif key == pynput.keyboard.KeyCode(char='c'):
            play_actions("actions_3.json")
        elif key == pynput.keyboard.KeyCode(char='v'):
            play_actions("actions_4.json")
        elif key == pynput.keyboard.KeyCode(char='b'):
            play_actions("actions_5.json")
        elif key == pynput.keyboard.KeyCode(char='n'):
            play_actions("actions_6.json")

    if recording:
        try:
            actions.append({'type': 'key_release', 'key': key.char, 'time': get_time()})
        except AttributeError:
            actions.append({'type': 'key_release', 'key': str(key), 'time': get_time()})

def get_time():
    global last_time
    current_time = time.time()
    delay = current_time - last_time if last_time else 0
    last_time = current_time
    return delay

# Управление записью для каждого мешка
def start_recording(bag_num):
    global current_file
    current_file = f"actions_{bag_num}.json"
    print(f"Ожидание клавиши 'г' для записи в {current_file}.")

def clear_bag_file(bag_num):
    clear_json_file(f"actions_{bag_num}.json")

# Функция для захвата числа с экрана
def get_number_from_screen():
    # Координаты и размер области для скриншота
    x, y, width, height = 120,992, 50, 50 
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    # Сохранение скриншота для просмотра
    screenshot.save("screenshot.png")
    
    # Преобразование изображения в текст
    extracted_text = pytesseract.image_to_string(screenshot, lang='eng', config='--psm 6 digits')
    
    # Извлечение числа
    extracted_number = ''.join(filter(str.isdigit, extracted_text))
    return int(extracted_number) if extracted_number else None

# Функция для проверки и фиксации одинакового числа несколько раз подряд
def check_number_consistency(new_number):
    global number_checks
    number_checks.append(new_number)
    if len(number_checks) > 3:  # Храним только последние 3 значения
        number_checks.pop(0)
    
    # Если последние 3 раза было одно и то же число
    return len(set(number_checks)) == 1 and len(number_checks) == 3

# Функция для выполнения действий на основе числа
def perform_action_based_on_number():
    number = get_number_from_screen()

    if number is not None and number in range(1, 7):
        print(f"Обнаружено число: {number}")
        if check_number_consistency(number):  # Проверяем, было ли одинаковое число несколько раз
            print(f"Обнаружено стабильное число: {number}")
            
            # Перемещение курсора
            pyautogui.moveTo(138, 1015)

            # Ожидание 2 секунды перед первым кликом
            time.sleep(1)

            # Первый клик
            pyautogui.click()

            # Задержка 5 секунд перед вторым кликом
            time.sleep(3)

            # Второй клик
            pyautogui.click()
            
            # Воспроизведение соответствующего скрипта
            play_actions(f"actions_{number}.json")
    else:
        print("Число не обнаружено или выходит за пределы диапазона. Проверка продолжается.")

    # Повторная проверка через 1 секунду
    root.after(1000, perform_action_based_on_number)

# Функция для отображения скриншота в интерфейсе
def show_screenshot():
    screenshot_window = tk.Toplevel(root)
    screenshot_window.title("Скриншот")

    img = Image.open("screenshot_sleep.png")
    img = img.resize((200, 200), Image.LANCZOS)  # Увеличение или уменьшение изображения для удобства
    img_tk = ImageTk.PhotoImage(img)

    panel = tk.Label(screenshot_window, image=img_tk)
    panel.image = img_tk  # Хранить ссылку на изображение, чтобы оно не было уничтожено сборщиком мусора
    panel.pack()

# Создание интерфейса tkinter
root = tk.Tk()
root.title("Спальные мешки")

# Создание кнопок для каждого спального мешка
for i in range(1, 7):
    frame = tk.Frame(root)
    frame.pack(pady=5)

    bag_button = tk.Button(frame, text=f"Спальный мешок - {i}", command=lambda i=i: start_recording(i))
    bag_button.pack(side=tk.LEFT, padx=5)

    clear_button = tk.Button(frame, text="❌", command=lambda i=i: clear_bag_file(i))
    clear_button.pack(side=tk.LEFT)

# Кнопка для выполнения действий на основе числа
action_button = tk.Button(root, text="Выполнить действие по числу", command=perform_action_based_on_number)
action_button.pack(pady=10)

# Кнопка для просмотра скриншота
screenshot_button = tk.Button(root, text="Показать скриншот", command=show_screenshot)
screenshot_button.pack(pady=10)

# Слушатель клавиатуры для записи и воспроизведения действий
keyboard_listener = pynput.keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
keyboard_listener.start()

# Запуск tkinter
root.mainloop()
