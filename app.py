import json
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import requests


class AkilliAsistanApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Akıllı Asistan v1.0")
    self.root.geometry("650 x 500")

    # Veri Dosyaları
    self.cards_file = "flashcards.json"
    self.cards = self.load_data(self.cards_file)

    # Sekme Yapısı (Notebook)
    self.notebook = ttk.Notebook(self.root)
    self.notebook.pack(expand=True, fill="both")

    # Sekmeler
    self.create_flashcard_tab()
    self.create_ai_chat_tab()

  # --- VERİ İŞLEMLERİ ---
  def load_data(self, filename):
    if os.path.exists(filename):
      try:
        with open(filename, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception:
        return []
    return []

  def save_data(self, filename, data):
    with open(filename, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)

  # --- SEKMELER ---
  def create_flashcard_tab(self):
    tab = ttk.Frame(self.notebook)
    self.notebook.add(tab, text="Öğrenme Kartları")

    # Kart Ekleme Alanı
    lbl_q = ttk.Label(tab, text="Soru / Kavram:")
    lbl_q.pack(anchor="w", padx=10, pady=(10, 0))

    self.entry_q = ttk.Entry(tab, width=50)
    self.entry_q.pack(fill="x", padx=10, pady=2)

    lbl_a = ttk.Label(tab, text="Cevap / Açıklama:")
    lbl_a.pack(anchor="w", padx=10, pady=(5, 0))

    self.entry_a = ttk.Entry(tab, width=50)
    self.entry_a.pack(fill="x", padx=10, pady=2)

    btn_add = ttk.Button(tab, text="Kart Ekle", command=self.add_card)
    btn_add.pack(padx=10, pady=10)

    # Kart Listesi
    self.card_listbox = tk.Listbox(tab, height=10)
    self.card_listbox.pack(fill="both", expand=True, padx=10, pady=5)
    self.update_card_listbox()

  def create_ai_chat_tab(self):
    tab = ttk.Frame(self.notebook)
    self.notebook.add(tab, text="Çevrim Dışı AI Sohbet")

    # Sohbet Geçmişi Gösterim Alanı
    self.chat_display = tk.Text(
        tab, state="disabled", wrap="word", bg="#f4f4f4", font=("Arial", 10)
    )
    self.chat_display.pack(expand=True, fill="both", padx=10, pady=10)

    # Mesaj Yazma Alanı ve Gönder Butonu
    input_frame = ttk.Frame(tab)
    input_frame.pack(fill="x", padx=10, pady=(0, 10))

    self.msg_entry = ttk.Entry(input_frame)
    self.msg_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))
    self.msg_entry.bind("<Return>", lambda event: self.send_ai_message_thread())

    btn_send = ttk.Button(
        input_frame, text="Gönder", command=self.send_ai_message_thread
    )
    btn_send.pack(side="right")

  # --- MANTIKSAL FONKSİYONLAR ---
  def add_card(self):
    q = self.entry_q.get().strip()
    a = self.entry_a.get().strip()

    if not q or not a:
      messagebox.showwarning("Eksik Bilgi", "Lütfen hem soru hem cevap girin.")
      return

    self.cards.append({"question": q, "answer": a})
    self.save_data(self.cards_file, self.cards)
    self.update_card_listbox()

    self.entry_q.delete(0, tk.END)
    self.entry_a.delete(0, tk.END)

  def update_card_listbox(self):
    self.card_listbox.delete(0, tk.END)
    for idx, card in enumerate(self.cards, start=1):
      self.card_listbox.insert(
          tk.END, f"{idx}. Soru: {card['question']} | Cevap: {card['answer']}"
      )

  # --- AI SOHBET FONKSİYONLARI ---
  def send_ai_message_thread(self):
    # Arayüz donmasın diye AI isteğini ayrı bir thread'de çalıştırıyoruz
    threading.Thread(target=self.send_ai_message, daemon=True).start()

  def send_ai_message(self):
    user_text = self.msg_entry.get().strip()
    if not user_text:
      return

    self.append_to_chat(f"Siz: {user_text}\n")
    self.msg_entry.delete(0, tk.END)

    try:
      # Yerel bilgisayarda çalışan Ollama servisine çevrim dışı istek gönderimi
      response = requests.post(
          "http://localhost:11434/api/generate",
          json={
              "model": "phi3",  # İsteğe bağlı yerel model adı (llama3, phi3 vb.)
              "prompt": user_text,
              "stream": False,
          },
          timeout=10,
      )

      if response.status_code == 200:
        ai_reply = response.json().get("response", "Yanıt alınamadı.")
        self.append_to_chat(f"Yapay Zeka: {ai_reply}\n\n")
      else:
        self.append_to_chat(
            "Yapay Zeka: Sunucu yanıt verdi ancak model yüklenemedi.\n\n"
        )

    except requests.exceptions.RequestException:
      self.append_to_chat(
          "Yapay Zeka (Çevrim Dışı): Şu anda bilgisayarınızda bir AI"
          " servisi (ör. Ollama) çalışmıyor. Sohbet edebilmek için arkaplanda"
          " yerel AI servisini başlatmalısınız.\n\n"
      )

  def append_to_chat(self, text):
    self.chat_display.config(state="normal")
    self.chat_display.insert(tk.END, text)
    self.chat_display.config(state="disabled")
    self.chat_display.see(tk.END)


if __name__ == "__main__":
  root = tk.Tk()
  app = AkilliAsistanApp(root)
  root.mainloop()
