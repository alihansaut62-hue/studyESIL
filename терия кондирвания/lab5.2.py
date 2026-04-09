import tkinter as tk
from tkinter import filedialog, messagebox

MARKER = b'###START###'






def hide_data(image_path, secret_path, result_path):
    with open(image_path, 'rb') as f_img:
        image_data = f_img.read()

    with open(secret_path, 'rb') as f_secret:
        secret_data = f_secret.read()

    with open(result_path, 'wb') as f_res:
        f_res.write(image_data + MARKER + secret_data)


def extract_data(stego_path, output_path):
    with open(stego_path, 'rb') as f:
        data = f.read()

    parts = data.split(MARKER)

    if len(parts) > 1:
        secret_data = parts[1]

        full_path = output_path + ".txt"

        with open(full_path, 'wb') as f_out:
            f_out.write(secret_data)

        return full_path
    else:
        return None


def clean_image(stego_path, clean_path):
    with open(stego_path, 'rb') as f:
        data = f.read()

    parts = data.split(MARKER)

    if len(parts) > 1:
        clean_data = parts[0]

        with open(clean_path, 'wb') as f_out:
            f_out.write(clean_data)

        return True
    else:
        return False






class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Стеганография (Матрешка)")
        self.root.geometry("500x350")

        self.image_path = ""
        self.secret_path = ""
        self.stego_path = ""

        # --- КНОПКИ ---
        tk.Button(root, text="Выбрать картинку", command=self.select_image).pack(pady=5)
        tk.Button(root, text="Выбрать TXT файл", command=self.select_secret).pack(pady=5)
        tk.Button(root, text="Выбрать stego-файл", command=self.select_stego).pack(pady=5)

        tk.Button(root, text="Скрыть файл", command=self.hide).pack(pady=10)
        tk.Button(root, text="Извлечь TXT", command=self.extract).pack(pady=10)
        tk.Button(root, text="Очистить картинку", command=self.clean).pack(pady=10)

        self.label = tk.Label(root, text="Готово к работе")
        self.label.pack(pady=20)






    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg")]
        )
        self.label.config(text=f"Картинка: {self.image_path}")

    def select_secret(self):
        self.secret_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        self.label.config(text=f"TXT: {self.secret_path}")

    def select_stego(self):
        self.stego_path = filedialog.askopenfilename()
        self.label.config(text=f"Stego: {self.stego_path}")






    def hide(self):
        if not self.image_path or not self.secret_path:
            messagebox.showerror("Ошибка", "Выбери картинку и TXT файл")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg")]
        )

        if save_path:
            hide_data(self.image_path, self.secret_path, save_path)
            messagebox.showinfo("OK", "TXT файл успешно скрыт")

    def extract(self):
        if not self.stego_path:
            messagebox.showerror("Ошибка", "Выбери stego-файл")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )

        if save_path:
            result = extract_data(self.stego_path, save_path)

            if result:
                messagebox.showinfo("OK", f"Файл извлечён:\n{result}")
            else:
                messagebox.showerror("Ошибка", "Секрет не найден")

    def clean(self):
        if not self.stego_path:
            messagebox.showerror("Ошибка", "Выбери stego-файл")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg")]
        )

        if save_path:
            if clean_image(self.stego_path, save_path):
                messagebox.showinfo("OK", "Картинка очищена")
            else:
                messagebox.showerror("Ошибка", "Лишних данных нет")






root = tk.Tk()
app = App(root)
root.mainloop()