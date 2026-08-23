# верхний фрейм: название, логи(в отдельном окне), помощь(readme.md), настройки(отдельное окно, возможно просто откроет файл настроек)
# средний фрейм: список профилей(можно листать и кликать на профили), список ссылок(можно листать, список зависит от нажатого профиля)
# нижний фрейм: кнопка "скачать всё"

import tkinter as tk
from api import Api

def main():
    # главное окно, его название, размеры, и цвет
    root = tk.Tk()
    root.title("Smarty Music Downloader")
    root.geometry("800x400")
    root.configure(bg="#0c0c0c")

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

    # средний фрейм (занимает оставшееся место)
    mid_frame = tk.Frame(root, bg="#0c0c0c")
    mid_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

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
        cursor="hand2",
        command=lambda: print("Скачивание... (заглушка)")
    )

    btn.pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()