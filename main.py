import pytesseract
import pyautogui
from PIL import Image
import time

import threading
import pynput
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Укажите путь к исполняемому файлу tesseract, если он не в PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Инициализация контроллеров
keyboard_controller = KeyboardController()
mouse_controller = MouseController()

running = False  # Флаг, который отслеживает состояние работы функции
thread = None  # Глобальная переменная для хранения текущего потока

# Основная функция для работы с изображениями и текстом
def check_for_text_in_screenshot():
    # Сделать скриншот области экрана по центру
    screen_width, screen_height = pyautogui.size()
    left = (screen_width // 2) - 100
    top = (screen_height // 2) - 100
    width = 200
    height = 150
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    # Преобразование скриншота в формат, который можно использовать для OCR
    screenshot = screenshot.convert('RGB')

    # Использование pytesseract для извлечения текста из изображения
    text = pytesseract.image_to_string(screenshot, lang='eng')
    
    return "OPEN DOOR" in text

# Функция для ввода числа с задержкой
def type_number(number_str):
    for char in number_str:
        if not running:
            return  # Прерываем ввод числа, если `running` стало False
        keyboard_controller.press(char)
        time.sleep(0.1)
        keyboard_controller.release(char)

# Основная функция для чтения и ввода чисел
def read_and_type_numbers(log_widget, last_number_widget):
    global running
    try:
        with open("num.txt", "r") as file:
            numbers = file.readlines()

        if not numbers:
            log_widget.insert(tk.END, "Файл пуст.\n")
            return

        while numbers and running:
            # Делать скриншот и проверять наличие текста
            if check_for_text_in_screenshot():
                number = numbers.pop(0).strip()
                
                if not running:
                    break  # Прерываем цикл, если `running` стало False

                # Логирование процесса
                log_widget.insert(tk.END, f"Обнаружено 'OPEN DOOR'. Ввод числа: {number}\n")
                last_number_widget.delete(1.0, tk.END)
                last_number_widget.insert(tk.END, number)
                
                # Удерживаем клавишу 'E'
                keyboard_controller.press('e')
                time.sleep(0.5)

                if not running:
                    keyboard_controller.release('e')
                    break

                # Перемещение курсора вниз и немного влево
                mouse_controller.move(90, 150)
                time.sleep(0.5)
                
                if not running:
                    break

                # Нажатие ЛКМ
                mouse_controller.click(Button.left)
                time.sleep(0.5)

                if not running:
                    break

                # Отпускаем клавишу 'E'
                keyboard_controller.release('e')
                
                # Ввод числа
                type_number(number)
                
                # Перезаписываем файл с оставшимися числами
                with open("num.txt", "w") as file:
                    file.writelines(numbers)
                
                # Логирование
                log_widget.insert(tk.END, "Число введено.\n")
                time.sleep(1)
            else:
                log_widget.insert(tk.END, "Фраза 'OPEN DOOR' не найдена. Ожидание 1 сек.\n")
                time.sleep(1)

    except FileNotFoundError:
        log_widget.insert(tk.END, "Файл num.txt не найден.\n")
    finally:
        running = False  # Остановка скрипта после завершения

# Функция для запуска/остановки потока
def toggle_reading(log_widget, last_number_widget):
    global running, thread
    if running:
        running = False
        log_widget.insert(tk.END, "Процесс остановлен.\n")
    else:
        running = True
        log_widget.insert(tk.END, "Процесс запущен.\n")
        thread = threading.Thread(target=read_and_type_numbers, args=(log_widget, last_number_widget))
        thread.start()

# Создание GUI
def create_gui():
    # Основное окно
    root = tk.Tk()
    root.title("Automation Tool")

    # Поле для логов
    log_label = tk.Label(root, text="Логи:")
    log_label.pack()

    log_widget = ScrolledText(root, width=50, height=10)
    log_widget.pack()

    # Поле для последнего числа
    last_number_label = tk.Label(root, text="Последнее введенное число:")
    last_number_label.pack()

    last_number_widget = tk.Text(root, width=20, height=1)
    last_number_widget.pack()

    # Кнопки запуска и остановки
    start_button = tk.Button(root, text="Запустить скрипт", command=lambda: toggle_reading(log_widget, last_number_widget))
    start_button.pack(side=tk.LEFT, padx=20, pady=20)

    stop_button = tk.Button(root, text="Остановить скрипт", command=lambda: toggle_reading(log_widget, last_number_widget))
    stop_button.pack(side=tk.LEFT, padx=20, pady=20)

    # Запуск окна
    root.mainloop()

# Запуск GUI
create_gui()