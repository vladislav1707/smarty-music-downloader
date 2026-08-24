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

import tkinter as tk
from tkinter import ttk
from api import Api

def main():
    # api
    api = Api()
    
    # главное окно, его название, размеры, и цвет
    root = tk.Tk()
    root.title("Smarty Music Downloader")
    root.geometry("800x400")
    root.configure(bg="#0c0c0c")

    # стилизация
    style = ttk.Style()
    style.theme_use("alt")

    # кастомный scrollbar
    style.configure("Custom.Vertical.TScrollbar",
        background="#0a0a0a",
        troughcolor="white",
        arrowcolor="green"
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
        bordercolor="#33ff33",
        lightcolor="#33ff33",
        darkcolor="#33ff33",
        relief="flat"
    )

    # фреймы:
    # верхний фрейм (фиксированная высота)
    top_frame = tk.Frame(root, bg="#0c0c0c", height=60)
    top_frame.pack(side="top", fill="x", pady=(5,0))

    title = tk.Label(
        top_frame,
        text="SMDownloader 3.0.0",
        fg="#33ff33",
        bg="#0c0c0c",
        font=("Courier New", 14, "bold")
    )
    
    title.pack(side="left", padx=5, pady=5)

    # фрейм прогресса (фиксированная высота)
    progress_frame = tk.Frame(root, bg="#0c0c0c", height=40)
    progress_frame.pack(side="top", fill="x", pady=(0,5))

    # спиннер и прогресс скачивания (сколько скачано и сколько осталось)
    progress_label = tk.Label(
        progress_frame,
        text="[/] 1 / 4 (25%)",
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

    # скроллбар для профилей
    profile_scrollbar = ttk.Scrollbar(
        left_panel,
        orient=tk.VERTICAL,
        style="Custom.Vertical.TScrollbar",
        command=listbox_profiles.yview
        )
    profile_scrollbar.pack(side="left",fill="y")

    # связать listbox и scrollbar
    listbox_profiles.config(yscrollcommand=profile_scrollbar.set)

    # правая панель (текст который можно листать и который зависит от правой панели)
    right_panel = tk.Frame(mid_frame, bg="#0c0c0c")
    right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    # нижний фрейм (фиксированная высота)
    bottom_frame = tk.Frame(root, bg="#0c0c0c", height=60)
    bottom_frame.pack(side="bottom", fill="x", pady=(0,5))

    # DOWNLOAD ALL button
    btn = tk.Button(
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
        cursor="hand2",
        command=lambda: print("Скачивание... (заглушка)")
    )

    btn.pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()