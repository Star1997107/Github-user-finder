import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Загрузка избранного
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # Поле ввода
        tk.Label(root, text="Введите имя пользователя GitHub:", font=("Arial", 12)).pack(pady=10)
        self.search_entry = tk.Entry(root, width=50, font=("Arial", 12))
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<Return>", lambda event: self.search_user())

        tk.Button(root, text="🔍 Поиск", command=self.search_user, bg="#2c3e50", fg="white", padx=10).pack(pady=5)

        # Результаты
        tk.Label(root, text="Результаты поиска:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.result_listbox = tk.Listbox(root, width=80, height=12, font=("Arial", 10))
        self.result_listbox.pack(pady=5)

        # Кнопки действий
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="⭐ Добавить в избранное", command=self.add_to_favorites, bg="#f39c12").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❤️ Показать избранное", command=self.show_favorites, bg="#e67e22").pack(side=tk.LEFT, padx=5)

        # Список избранного
        tk.Label(root, text="Избранные пользователи:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.fav_listbox = tk.Listbox(root, width=80, height=6, font=("Arial", 10))
        self.fav_listbox.pack(pady=5)
        self.refresh_fav_listbox()

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_favorites(self):
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def refresh_fav_listbox(self):
        self.fav_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.fav_listbox.insert(tk.END, f"{user['login']} — {user['html_url']}")

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            return

        url = f"https://api.github.com/users/{username}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.result_listbox.delete(0, tk.END)
                info = (
                    f"Логин: {data['login']}\n"
                    f"Имя: {data.get('name', 'Нет данных')}\n"
                    f"Репозитории: {data['public_repos']}\n"
                    f"Подписчики: {data['followers']}\n"
                    f"Профиль: {data['html_url']}"
                )
                self.result_listbox.insert(tk.END, info)
                self.current_user = data
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", "Пользователь не найден!")
            else:
                messagebox.showerror("Ошибка API", f"Код ошибки: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Ошибка соединения", str(e))

    def add_to_favorites(self):
        if not hasattr(self, 'current_user'):
            messagebox.showwarning("Нет данных", "Сначала найдите пользователя!")
            return

        user_data = {
            "login": self.current_user['login'],
            "html_url": self.current_user['html_url'],
            "name": self.current_user.get('name', ''),
            "followers": self.current_user['followers']
        }

        if any(u['login'] == user_data['login'] for u in self.favorites):
            messagebox.showinfo("Инфо", "Этот пользователь уже в избранном!")
            return

        self.favorites.append(user_data)
        self.save_favorites()
        self.refresh_fav_listbox()
        messagebox.showinfo("Успех", f"{user_data['login']} добавлен в избранное!")

    def show_favorites(self):
        if not self.favorites:
            messagebox.showinfo("Избранное", "Список избранного пуст.")
            return

        fav_window = tk.Toplevel(self.root)
        fav_window.title("Избранные пользователи")
        fav_window.geometry("500x400")

        listbox = tk.Listbox(fav_window, width=70, height=20)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        for user in self.favorites:
            listbox.insert(tk.END, f"{user['login']} — {user['html_url']} (Followers: {user['followers']})")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
