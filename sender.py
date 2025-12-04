# -- coding: utf-8 --
import socket
import json
import zlib
import tkinter as tk  # EKLENDİ
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# ----------------------------------
#  ALGORITMALAR
# ----------------------------------

def calc_parity(text: str) -> str:
    val = 0
    for char in text.encode():
        val ^= char
    return f"{val:02X}"

def calc_crc32(text: str) -> str:
    crc = zlib.crc32(text.encode())
    return f"{crc & 0xFFFFFFFF:08X}"

def calc_checksum(text: str) -> str:
    total = sum(text.encode())
    return f"{total % 256:02X}"

def calc_hamming(text: str) -> str:
    return "HAMMING-SIMULATED" 

ALGORITHMS = {
    "Simple Parity": calc_parity,
    "CRC-32": calc_crc32,
    "Sum Checksum": calc_checksum,
    "Hamming Code": calc_hamming
}

# ----------------------------------
#  AĞ İŞLEMLERİ
# ----------------------------------

def dispatch_packet():
    data = txt_payload.get()
    algo_name = cmb_algo.get()

    if not data:
        messagebox.showwarning("Uyarı", "Veri alanı boş bırakılamaz.")
        return

    func = ALGORITHMS.get(algo_name)
    checksum_val = func(data) if func else "00"

    packet_obj = {
        "payload": data,
        "algorithm": algo_name,
        "checksum": checksum_val
    }
    
    packet_json = json.dumps(packet_obj)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 5000)) 
            s.sendall(packet_json.encode('utf-8'))
            log_display.insert(0, f"OUT >> {algo_name}: {checksum_val}")
    except ConnectionRefusedError:
        messagebox.showerror("Hata", "Sunucu (Middleman) aktif değil.")

# ----------------------------------
#  GUI TASARIMI
# ----------------------------------

root = ttk.Window(title="SENDER NODE", themename="solar", size=(600, 450))

# Başlık
frame_top = ttk.Frame(root, padding=20)
frame_top.pack(fill=X)
ttk.Label(frame_top, text="Data Transmitter", font=("Helvetica", 20, "bold"), bootstyle="warning").pack(side=LEFT)

# Giriş Alanı
frame_main = ttk.Labelframe(root, text="Packet Configuration", padding=15, bootstyle="light")
frame_main.pack(fill=X, padx=20, pady=10)

ttk.Label(frame_main, text="Payload Data:").pack(anchor=W)
txt_payload = ttk.Entry(frame_main)
txt_payload.pack(fill=X, pady=(5, 15))

ttk.Label(frame_main, text="Integrity Method:").pack(anchor=W)
cmb_algo = ttk.Combobox(frame_main, values=list(ALGORITHMS.keys()), state="readonly")
cmb_algo.current(1)
cmb_algo.pack(fill=X, pady=5)

# Butonlar
frame_action = ttk.Frame(root, padding=20)
frame_action.pack(fill=X)

btn_send = ttk.Button(frame_action, text="ENCAPSULATE & SEND", command=dispatch_packet, bootstyle="success-outline", width=25)
btn_send.pack()

# Log Alanı
ttk.Label(root, text="Transmission Log:", font=("Arial", 9)).pack(anchor=W, padx=20)
# DÜZELTME BURADA YAPILDI: ttk.ListBox yerine tk.Listbox kullanıldı
log_display = tk.Listbox(root, height=5, bg="#002b36", fg="white", borderwidth=0)
log_display.pack(fill=X, padx=20, pady=(0, 20))

root.mainloop()