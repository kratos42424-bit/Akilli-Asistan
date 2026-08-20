import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta

# --- VERİTABANI / DOSYA YÖNETİMİ ---
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"cards": [], "posts": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ANA UYGULAMA ---
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Akıllı Asistan - Kartlar & Sosyal Medya")
        self.geometry("700x500")
        self.data = load_data()

        # Sekme Yönetimi
        tab_control = ttk.Notebook(self)
        
        self.tab_cards = ttk.Frame(tab_control)
        self.tab_social = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_cards, text=" 🧠 Dil / Sınav Kartları ")
        tab_control.add(self.tab_social, text=" 📱 Sosyal Medya Planlayıcı ")
        tab_control.pack(expand=1, fill="both")

        self.setup_cards_tab()
        self.setup_social_tab()

    # --- KARTLAR SEKMESİ ---
    def setup_cards_tab(self):
        frame = ttk.LabelFrame(self.tab_cards, text="Yeni Kart Ekle")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Ön Yüz (Soru/Kelime):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_front = ttk.Entry(frame, width=30)
        self.entry_front.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Arka Yüz (Cevap/Anlam):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_back = ttk.Entry(frame, width=30)
        self.entry_back.grid(row=1, column=1, padx=5, pady=5)

        btn_add = ttk.Button(frame, text="Ekle", command=self.add_card)
        btn_add.grid(row=2, column=0, columnspan=2, pady=5)

        # Kart Listesi
        self.card_list = tk.Listbox(self.tab_cards, height=10)
        self.card_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_cards()

    def add_card(self):
        front = self.entry_front.get().strip()
        back = self.entry_back.get().strip()
        if front and back:
            new_card = {
                "front": front,
                "back": back,
                "interval": 1,
                "next_review": str(datetime.now().date())
            }
            self.data["cards"].append(new_card)
            save_data(self.data)
            self.entry_front.delete(0, tk.END)
            self.entry_back.delete(0, tk.END)
            self.refresh_cards()
            messagebox.showinfo("Başarılı", "Kart eklendi!")
        else:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun.")

    def refresh_cards(self):
        self.card_list.delete(0, tk.END)
        for c in self.data["cards"]:
            self.card_list.insert(tk.END, f"Soru: {c['front']} | Cevap: {c['back']} | Tekrar: {c['next_review']}")

    # --- SOSYAL MEDYA SEKMESİ ---
    def setup_social_tab(self):
        frame = ttk.LabelFrame(self.tab_social, text="Yeni Gönderi Planla")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Platform:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_platform = ttk.Combobox(frame, values=["Instagram", "X (Twitter)", "LinkedIn"])
        self.combo_platform.current(0)
        self.combo_platform.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Gönderi Metni:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_post_text = ttk.Entry(frame, width=30)
        self.entry_post_text.grid(row=1, column=1, padx=5, pady=5)

        btn_add_post = ttk.Button(frame, text="Planla", command=self.add_post)
        btn_add_post.grid(row=2, column=0, columnspan=2, pady=5)

        # Gönderi Listesi
        self.post_list = tk.Listbox(self.tab_social, height=10)
        self.post_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_posts()

    def add_post(self):
        platform = self.combo_platform.get()
        text = self.entry_post_text.get().strip()
        if text:
            new_post = {
                "platform": platform,
                "text": text,
                "status": "Planlandı",
                "date": str(datetime.now().strftime("%Y-%m-%d %H:%M"))
            }
            self.data["posts"].append(new_post)
            save_data(self.data)
            self.entry_post_text.delete(0, tk.END)
            self.refresh_posts()
            messagebox.showinfo("Başarılı", "Gönderi planlandı!")
        else:
            messagebox.showwarning("Uyarı", "Lütfen bir metin girin.")

    def refresh_posts(self):
        self.post_list.delete(0, tk.END)
        for p in self.data["posts"]:
            self.post_list.insert(tk.END, f"[{p['platform']}] {p['text']} - ({p['status']})")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()