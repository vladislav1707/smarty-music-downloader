# верхний фрейм: название, логи(в отдельном окне), помощь(readme.md), настройки(отдельное окно, возможно просто откроет файл настроек)
# фрейм прогресса: инфо(спиннер, кол-во обработанных/оставшихся ссылок, завершенность загрузки в процентах) и прогрессбар
# средний фрейм:
#       левая панель:
#               выбор профилей, при нажатии меняет содержимое правой панели
#       правая панель:
#               отображение файла sources.txt профиля(вместе с комментариями)
#               ВАЖНО: пока что profile_manager.py возвращает список ссылок без комментариев, может потребоваться
#               добавить метод для получения всего sources.txt с комментариями
# нижний фрейм: кнопка "скачать всё"

import version
import threading
import logging
import sys
import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
from api import Api

# api
api = Api()

# logging settings
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('smarty_music_downloader.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# управление блокировкой кнопки
download_thread = None
is_downloading = False

# спиннер
spinner_chars = ['|', '/', '-', '\\']
spinner_idx = 0

def main():
    # главное окно, его название, размеры, ограничение на минимальный размер, цвет и т.д.
    root = tk.Tk()
    root.title("Smarty Music Downloader")
    root.geometry("870x600")
    root.configure(bg="#0c0c0c")
    root.minsize(width=870, height=600)

    # стилизация
    style = ttk.Style()
    style.theme_use("clam")

    # кастомный scrollbar
    style.configure("Custom.Vertical.TScrollbar",
        background="#0a0a0a",
        troughcolor="grey",
        arrowcolor="#33ff33"
    )

    # настройка состояний scrollbar
    style.map("Custom.Vertical.TScrollbar",
          background=[("active", "#252525"),   # при наведении мыши
                      ("pressed", "#1a1a1a")], # при зажатии
          troughcolor=[("active", "#666666")]  # дорожка при наведении
        )
    
    # настройка прогрессбара
    style.configure("Custom.Horizontal.TProgressbar",
        background="#33ff33",
        troughcolor="#1a1a1a",
        bordercolor="white",
        lightcolor="#33ff33",
        darkcolor="#33ff33",
        relief="flat"
    )

    # фреймы:
    # верхний фрейм (фиксированная высота)
    top_frame = tk.Frame(root, bg="#0c0c0c", height=60)
    top_frame.pack(side="top", fill="x", pady=(5,0))

    # название программы и версия
    title = tk.Label(
        top_frame,
        text=f"SMDownloader {version.__version__}",
        fg="#33ff33",
        bg="#0c0c0c",
        font=("Courier New", 14, "bold")
    )
    title.pack(side="left", padx=5, pady=5)
    ToolTip(title, "Made by Mister Smarty Pants")

    # фрейм прогресса (фиксированная высота)
    progress_frame = tk.Frame(root, bg="#0c0c0c", height=40)
    progress_frame.pack(side="top", fill="x", pady=(0,5))

    # спиннер и прогресс скачивания (сколько скачано и сколько осталось)
    progress_label = tk.Label(
        progress_frame,
        text=f"[Waiting for action] 0 / {api.get_total_links_count()} (0%)",
        fg="#33ff33",
        bg="#0c0c0c",
        font=("Courier New", 10),
    )
    progress_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5,0))

    progressbar = ttk.Progressbar(
        progress_frame,
        style="Custom.Horizontal.TProgressbar",
        orient="horizontal",
        mode="determinate",
        length=300
        )
    progressbar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
    progress_frame.grid_columnconfigure(0, weight=1)

    # средний фрейм (занимает оставшееся место)
    mid_frame = tk.Frame(root, bg="#0c0c0c")
    mid_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

    # левая панель (список профилей по которым можно нажать, влияет на содержимое правой панели)
    left_panel = tk.Frame(mid_frame, bg="#0c0c0c")
    left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    # фрейм чисто под label (левый)
    left_label_frame = tk.Frame(left_panel, bg="#0c0c0c")
    left_label_frame.pack(side="top", fill="x")

    # label с надписью "profiles:"
    left_label = tk.Label(
        left_label_frame,
        text="profiles:",
        bg="#0c0c0c",
        fg="#33ff33",
        font=("Courier New", 10)
    )
    left_label.pack(side="left")
    ToolTip(left_label, api.get_setting("profiles_dir"))

    # listbox с профилями
    listbox_profiles = tk.Listbox(
        left_panel,
        bg="#1a1a1a",
        fg="#33ff33",
        selectbackground="#33ff33",
        selectforeground="#0c0c0c",
        font=("Courier New", 10),
        relief="flat"
    )
    listbox_profiles.pack(side="left", fill="both", expand=True)

    # scrollbar для профилей
    profile_scrollbar = ttk.Scrollbar(
        left_panel,
        orient=tk.VERTICAL,
        style="Custom.Vertical.TScrollbar",
        command=listbox_profiles.yview
        )
    profile_scrollbar.pack(side="right",fill="y")

    # связать listbox и scrollbar
    listbox_profiles.config(yscrollcommand=profile_scrollbar.set)
    
    # обновить список профилей
    for p in api.list_profiles():
        listbox_profiles.insert(tk.END, p)

    # правая панель (текст который можно листать и который зависит от правой панели)
    right_panel = tk.Frame(mid_frame, bg="#0c0c0c")
    right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    # фрейм чисто под label (правый)
    right_label_frame = tk.Frame(right_panel, bg="#0c0c0c")
    right_label_frame.pack(side="top", fill="x")

    # label с надписью "links:""
    right_label = tk.Label(
        right_label_frame,
        text=f"links:",
        bg="#0c0c0c",
        fg="#33ff33",
        font=("Courier New", 10)
    )
    right_label.pack(side="left")

    # текстовое поле для отображения sources.txt
    text_sources = tk.Text(
        right_panel,
        bg="#1a1a1a",
        fg="#33ff33",
        font=("Courier New", 10),
        relief="flat",
        wrap="none",
        state="disabled" # отключить редактирование, так как profile_manager.py ничего не умеет редактировать, только читать
    )
    text_sources.pack(side="left", fill="both", expand=True)

    # скроллбар для текстового поля
    text_scrollbar = ttk.Scrollbar(
        right_panel,
        orient=tk.VERTICAL,
        style="Custom.Vertical.TScrollbar",
        command=text_sources.yview
    )
    text_scrollbar.pack(side="right", fill="y")
    text_sources.config(yscrollcommand=text_scrollbar.set)

    # нижний фрейм (фиксированная высота)
    bottom_frame = tk.Frame(root, bg="#0c0c0c", height=60)
    bottom_frame.pack(side="bottom", fill="x", pady=(0,5))

    # DOWNLOAD ALL button
    DOWNLOAD_ALL_btn = tk.Button(
        bottom_frame,
        text="▶ DOWNLOAD ALL",
        bg="#1a1a1a",
        fg="#33ff33",
        activebackground="#2a2a2a",
        activeforeground="#33ff33",
        relief="flat",
        padx=20,
        pady=8,
        font=("Courier New", 10),
        cursor="hand2"
    )
    DOWNLOAD_ALL_btn.pack(side="bottom", pady=10)
    ToolTip(DOWNLOAD_ALL_btn, "hamburger", delay=9999.9)

    # обработка выбора профиля
    def on_profile_click(event):
        # получить что выделено(либо кортеж пустой, либо там выбран профиль)
        selection = listbox_profiles.curselection()
        # если пусто то выйти из функции
        if not selection:
            return
        index = selection[0]
        # получить имя профиля если он выделен
        profile_name = listbox_profiles.get(index)
        
        # временно включить редактирование
        text_sources.config(state=tk.NORMAL)
        # очистить
        text_sources.delete(1.0, tk.END)
        
        # загрузить sources.txt из профиля
        try:
            content = api.read_sources_from_profile(profile_name)
        except Exception as e:
            content = f"Reading error: {e}"

        # если content не пустой то вывести, содержимое иначе вывести предупреждение
        if content:
            text_sources.insert(tk.END, content)
        else:
            text_sources.insert(tk.END, f"WARNING: source.txt file not found in the {profile_name} profile, make sure it exists")
        
        # отключить редактироваин обратно
        text_sources.config(state=tk.DISABLED)

    # привязать событие выбора к Listbox
    listbox_profiles.bind("<<ListboxSelect>>", on_profile_click)

    # функция проверки статуса скачивания(активно или нет)
    def check_download_status():
        # указать что переменные глобальные
        global download_thread, is_downloading, spinner_idx, spinner_chars

        # если не скачивание то выйти
        if not is_downloading:
            return
        
        # если поток не рабочий то разблокировать кнопку
        if not download_thread.is_alive():
            DOWNLOAD_ALL_btn.config(state=tk.NORMAL, text="▶ DOWNLOAD ALL", cursor="hand2",)
            is_downloading = False
            progress_label.config(text="[✓] The download is complete")
            progressbar.config(value=100)
            return
        
        # обновить прогрессбар
        try:
            # получить кол-во ссылок
            downloaded = api.get_downloaded_links()
            total = api.get_total_links_count()
            # если всех ссылок больше нуля то вычислить сколько процентов ссылок скачано и вывести прогресс
            if total > 0:
                # спиннер
                spinner_char = spinner_chars[spinner_idx % len(spinner_chars)]
                spinner_idx += 1
                # расчитать проценты
                percent = int((downloaded / total) * 100)
                progress_label.config(text=f"[{spinner_char}] {downloaded} / {total} ({percent}%)")
                progressbar.config(value=percent)
            # иначе вывести неизвестно сколько процентов
            else:
                progress_label.config(text=f"[*] {downloaded} / ?")
        # обработка ошибок
        except Exception as e:
            progress_label.config(text=f"Update error: {e}")
        
        # через 500 милисекунд запланировать проверку статуса загрузки
        root.after(500, check_download_status)

    # запуск скачивания всех профилей
    def start_download():
        # указать что переменные глобальные
        global download_thread, is_downloading

        # отключить кнопку а так же обнулить прогрессбар
        DOWNLOAD_ALL_btn.config(state=tk.DISABLED, text="DOWNLOADING...", cursor="arrow")
        progressbar.config(value=0)
        
        # запустить поток для скачивания (daemon нужен чтобы при закрытии программы поток тоже закрылся)
        download_thread = threading.Thread(target=api.download_all, daemon=True)
        download_thread.start()
        # установить флаг сигнализирующий о том что сейчас идет загрузка в True
        is_downloading = True
        
        # через 100 милисекунд запланировать проверку статуса загрузки
        root.after(100, check_download_status)

    # кнопка DOWNLOAD_ALL_btn запускает функцию start_download
    DOWNLOAD_ALL_btn.config(command=start_download)

    root.mainloop()

if __name__ == "__main__":
    main()