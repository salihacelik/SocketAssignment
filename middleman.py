# -- coding: utf-8 --
import socket
import json
import random
import threading
import tkinter as tk  # EKLENDİ
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ----------------------------------
#  HATA ENJEKSİYON MANTIĞI
# ----------------------------------

def inject_bit_flip(text):
    b_data = bytearray(text, 'utf-8')
    if b_data:
        idx = random.randint(0, len(b_data) - 1)
        b_data[idx] ^= 1 
    return b_data.decode('utf-8', errors='replace')

def inject_noise(text):
    return text + random.choice(["#", "?", "!", "\0"])

def no_error(text):
    return text

ERROR_MODES = {
    "No Interference": no_error,
    "Bit Flip (1-bit)": inject_bit_flip,
    "Noise Addition": inject_noise
}

# ----------------------------------
#  SUNUCU MANTIĞI
# ----------------------------------

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(("localhost", 5000))
    except OSError:
        lbl_status.config(text="Status: PORT ERROR (Restart App)", bootstyle="danger")
        return

    server.listen(1)
    lbl_status.config(text="Status: LISTENING (Port 5000)", bootstyle="success")

    while True:
        client, addr = server.accept()
        raw_data = client.recv(4096)
        client.close()

        if not raw_data: continue

        try:
            packet = json.loads(raw_data.decode('utf-8'))
            original_payload = packet['payload']
            
            error_func = ERROR_MODES[cmb_err.get()]
            corrupted_payload = error_func(original_payload)
            
            packet['payload'] = corrupted_payload
            
            log_msg = f"Rcv: {original_payload} -> Sent: {corrupted_payload}"
            list_log.insert(0, log_msg)

            fwd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fwd_sock.connect(("localhost", 6000))
            fwd_sock.sendall(json.dumps(packet).encode('utf-8'))
            fwd_sock.close()

        except Exception as e:
            list_log.insert(0, f"Error: {e}")

def start_thread():
    threading.Thread(target=run_server, daemon=True).start()

# ----------------------------------
#  GUI
# ----------------------------------
root = ttk.Window(title="CHANNEL NOISE SIMULATOR", themename="superhero", size=(500, 400))

ttk.Label(root, text="Network Channel (Middleman)", font=("Impact", 16)).pack(pady=10)
lbl_status = ttk.Label(root, text="Status: IDLE", bootstyle="secondary")
lbl_status.pack()

frame_ctrl = ttk.Labelframe(root, text="Interference Settings", padding=10)
frame_ctrl.pack(fill=X, padx=10, pady=10)

cmb_err = ttk.Combobox(frame_ctrl, values=list(ERROR_MODES.keys()), state="readonly")
cmb_err.current(0)
cmb_err.pack(fill=X)

ttk.Button(root, text="Start Server Engine", command=start_thread, bootstyle="info").pack(pady=5)

# DÜZELTME BURADA YAPILDI:
list_log = tk.Listbox(root, bg="#2b3e50", fg="white", borderwidth=0)
list_log.pack(fill=BOTH, expand=True, padx=10, pady=10)

root.mainloop()