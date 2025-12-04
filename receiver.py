# -- coding: utf-8 --
import socket
import json
import zlib
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ----------------------------------
#  VALIDATION LOGIC
# ----------------------------------
# Must match Sender's logic exactly
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

VALIDATORS = {
    "Simple Parity": calc_parity,
    "CRC-32": calc_crc32,
    "Sum Checksum": calc_checksum,
    "Hamming Code": calc_hamming
}

# ----------------------------------
#  LISTENER
# ----------------------------------
def start_listener():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("localhost", 6000)) # Listen on 6000
    srv.listen(1)
    
    btn_connect.config(state="disabled", text="Running...")
    
    def listener_loop():
        while True:
            conn, addr = srv.accept()
            data = conn.recv(4096)
            conn.close()
            
            if data:
                process_packet(data)
    
    threading.Thread(target=listener_loop, daemon=True).start()

def process_packet(raw_json):
    try:
        packet = json.loads(raw_json.decode('utf-8'))
        
        payload = packet.get("payload", "")
        algo = packet.get("algorithm", "")
        received_hash = packet.get("checksum", "")
        
        # Recalculate
        func = VALIDATORS.get(algo)
        calculated_hash = func(payload) if func else "??"
        
        is_valid = (received_hash == calculated_hash)
        
        # Update UI (Must be done on main thread usually, but ttk handles simple updates)
        update_ui(payload, algo, received_hash, calculated_hash, is_valid)
        
    except json.JSONDecodeError:
        print("Invalid Packet Format")

def update_ui(data, algo, remote_hash, local_hash, valid):
    # Clear fields
    ent_data.delete(0, END)
    ent_data.insert(0, data)
    
    ent_algo.delete(0, END)
    ent_algo.insert(0, algo)
    
    ent_rem.delete(0, END)
    ent_rem.insert(0, remote_hash)
    
    ent_loc.delete(0, END)
    ent_loc.insert(0, local_hash)
    
    if valid:
        lbl_result.config(text="INTEGRITY VERIFIED", bootstyle="success", font=("Arial", 14, "bold"))
    else:
        lbl_result.config(text="DATA CORRUPTION DETECTED", bootstyle="danger", font=("Arial", 14, "bold"))

# ----------------------------------
#  GUI
# ----------------------------------
root = ttk.Window(title="RECEIVER NODE", themename="solar", size=(600, 500))

# Top
frame_head = ttk.Frame(root, padding=20)
frame_head.pack(fill=X)
btn_connect = ttk.Button(frame_head, text="Open Port 6000", command=start_listener, bootstyle="primary")
btn_connect.pack(side=RIGHT)
ttk.Label(frame_head, text="Receiver Analysis", font=("Helvetica", 18)).pack(side=LEFT)

# Dashboard
frame_dash = ttk.Frame(root, padding=20)
frame_dash.pack(fill=BOTH, expand=True)

# Grid Layout for Fields
ttk.Label(frame_dash, text="Incoming Payload:", bootstyle="info").grid(row=0, column=0, sticky=W, pady=5)
ent_data = ttk.Entry(frame_dash, width=50)
ent_data.grid(row=0, column=1, pady=5)

ttk.Label(frame_dash, text="Algorithm Used:", bootstyle="info").grid(row=1, column=0, sticky=W, pady=5)
ent_algo = ttk.Entry(frame_dash, width=50)
ent_algo.grid(row=1, column=1, pady=5)

ttk.Separator(frame_dash, orient=HORIZONTAL).grid(row=2, column=0, columnspan=2, sticky="ew", pady=15)

ttk.Label(frame_dash, text="Expected Hash:", bootstyle="secondary").grid(row=3, column=0, sticky=W, pady=5)
ent_rem = ttk.Entry(frame_dash, width=50)
ent_rem.grid(row=3, column=1, pady=5)

ttk.Label(frame_dash, text="Calculated Hash:", bootstyle="warning").grid(row=4, column=0, sticky=W, pady=5)
ent_loc = ttk.Entry(frame_dash, width=50)
ent_loc.grid(row=4, column=1, pady=5)

# Big Result Label
lbl_result = ttk.Label(root, text="WAITING FOR PACKET...", font=("Arial", 12), anchor="center")
lbl_result.pack(fill=X, pady=20)

root.mainloop()