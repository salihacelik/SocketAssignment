import socket
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

# Backend dosyalarını import ediyoruz
from sender import PacketLogic, NetworkClient
from middleman import NoiseLogic
from receiver import ReceiverServer

class NetworkAssignmentApp(ttk.Window):
    def __init__(self):
    
        super().__init__(title="Socket Assignment - Error Detection", themename="darkly", size=(1250, 700))
        
        self.parsed_packet = {} 
        
        self.setup_ui()
        
        # Serverları Başlat
        # 1. Middleman (Dinleyici)
        threading.Thread(target=self.run_middleman_listener, daemon=True).start()
        
        # 2. Receiver (Alıcı Sınıfı)
        self.receiver = ReceiverServer(5001, self.on_receiver_callback)
        self.receiver.start()

    def setup_ui(self):
        
        lbl_title = ttk.Label(self, text="VERİ İLETİŞİMİ & HATA DENETİM SİMÜLATÖRÜ", font=("Impact", 22), bootstyle="inverse-light")
        lbl_title.pack(pady=15)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # ==========================================
        # SOL PANEL: CLIENT 1 (SENDER) - YEŞİL
        # ==========================================
        f_sender = ttk.Labelframe(main_frame, text=" 1. CLIENT 1: SENDER ", bootstyle="success", padding=15)
        f_sender.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        ttk.Label(f_sender, text="Gönderilecek Metin:", bootstyle="success").pack(anchor=W)
        self.txt_sender = ttk.Entry(f_sender, font=("Consolas", 11))
        self.txt_sender.insert(0, "HELLO")
        self.txt_sender.pack(fill=X, pady=5)

        ttk.Label(f_sender, text="Hata Denetim Yöntemi:", bootstyle="success").pack(anchor=W, pady=(15,0))
        self.cmb_method = ttk.Combobox(f_sender, state="readonly", bootstyle="success", values=PacketLogic.get_algo_list())
        self.cmb_method.current(2) # CRC-32 Varsayılan
        self.cmb_method.pack(fill=X, pady=5)

        ttk.Button(f_sender, text="PAKET OLUŞTUR VE GÖNDER >", command=self.send_packet, bootstyle="success-outline").pack(fill=X, pady=25)
        
        self.lbl_sender_log = ttk.Label(f_sender, text="Hazır.", font=("Consolas", 9), wraplength=250, bootstyle="secondary")
        self.lbl_sender_log.pack(side=BOTTOM, pady=10)

        # ==========================================
        # ORTA PANEL: MIDDLEMAN (SERVER) - KIRMIZI
        # ==========================================
        f_middle = ttk.Labelframe(main_frame, text=" 2. SERVER: DATA CORRUPTOR ", bootstyle="danger", padding=15)
        f_middle.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        ttk.Label(f_middle, text="Gelen Ham Paket:", bootstyle="danger").pack(anchor=W)
        self.lbl_mid_raw = ttk.Label(f_middle, text="-", font=("Consolas", 9), bootstyle="secondary")
        self.lbl_mid_raw.pack(fill=X, pady=5)

        ttk.Label(f_middle, text="Müdahale Edilecek Veri (Payload):", bootstyle="warning").pack(anchor=W, pady=(15,0))
        self.ent_mid_payload = ttk.Entry(f_middle, font=("Consolas", 14, "bold"), justify=CENTER, bootstyle="danger")
        self.ent_mid_payload.pack(fill=X, pady=5)

        ttk.Label(f_middle, text="Hata Enjeksiyon Yöntemleri:", bootstyle="danger").pack(anchor=W, pady=(10, 5))
        
        btn_frame = ttk.Frame(f_middle)
        btn_frame.pack(fill=X)

        # Hata listesi (Backend fonksiyon adlarıyla uyumlu stringler)
        errors = [
            ("1. Bit Flip", "Bit Flip"), ("2. Substitution", "Substitution"),
            ("3. Deletion", "Deletion"), ("4. Insertion", "Insertion"),
            ("5. Swapping", "Swapping"), ("6. Multi Flip", "Multi Flip"),
        ]

        # 2 Sütunlu Izgara
        for i, (label, mode) in enumerate(errors):
            btn = ttk.Button(btn_frame, text=label, command=lambda m=mode: self.inject_error(m), bootstyle="danger-outline")
            btn.grid(row=i//2, column=i%2, padx=3, pady=3, sticky="ew")
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # Burst Error (Büyük Buton)
        ttk.Button(f_middle, text="7. BURST ERROR (3-8 Char)", command=lambda: self.inject_error("Burst Error"), bootstyle="danger").pack(fill=X, pady=10)

        ttk.Button(f_middle, text="CLIENT 2'YE İLET >>", command=self.forward_packet, bootstyle="danger").pack(fill=X, pady=15)
        
        self.lbl_mid_status = ttk.Label(f_middle, text="Dinliyor (Port 5000)...", font=("Arial", 9), bootstyle="secondary")
        self.lbl_mid_status.pack(side=BOTTOM)

        # ==========================================
        # SAĞ PANEL: CLIENT 2 (RECEIVER) - MAVİ
        # ==========================================
        f_rec = ttk.Labelframe(main_frame, text=" 3. CLIENT 2: RECEIVER ", bootstyle="info", padding=15)
        f_rec.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        self.txt_rec_log = ttk.Text(f_rec, height=15, width=30, font=("Consolas", 10))
        self.txt_rec_log.pack(fill=BOTH, expand=True, pady=5)
        
        self.lbl_rec_result = ttk.Label(f_rec, text="SONUÇ: -", font=("Impact", 18), bootstyle="secondary-inverse", anchor=CENTER)
        self.lbl_rec_result.pack(fill=X, pady=10, ipady=10)

    # ======================================================
    # MANTIK FONKSİYONLARI (BACKEND İLE HABERLEŞME)
    # ======================================================

    def send_packet(self):
        """SENDER: Paketi oluştur ve yolla"""
        data = self.txt_sender.get()
        method = self.cmb_method.get()
        
        if "|" in data:
            messagebox.showerror("Hata", "'|' karakteri kullanılamaz.")
            return

        # Backend'den paket üret
        packet_str, checksum = PacketLogic.create_packet_string(data, method)
        
        # Gönder
        success, msg = NetworkClient.send_data("localhost", 5000, packet_str)
        
        if success:
            self.lbl_sender_log.config(text=f"Giden: {packet_str}\nChecksum: {checksum}\nDurum: ✔ Server'a İletildi", bootstyle="success")
        else:
            self.lbl_sender_log.config(text=f"Hata: {msg}", bootstyle="danger")

    def run_middleman_listener(self):
        """SERVER: Dinleme döngüsü"""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            srv.bind(("0.0.0.0", 5000))
            srv.listen(1)
            while True:
                conn, _ = srv.accept()
                data = conn.recv(4096).decode('utf-8')
                conn.close()
                if data:
                    self.after(0, lambda d=data: self.on_packet_arrived(d))
        except Exception as e:
            print(f"Server Hatası: {e}")

    def on_packet_arrived(self, raw_packet):
        """SERVER: Paket geldiğinde arayüzü doldur"""
        data, method, control = NoiseLogic._split_packet(raw_packet)
        self.parsed_packet = {"data": data, "method": method, "control": control}
        
        self.ent_mid_payload.delete(0, END)
        self.ent_mid_payload.insert(0, data)
        self.lbl_mid_raw.config(text=f"{raw_packet[:30]}...")
        self.lbl_mid_status.config(text="⚠ PAKET YAKALANDI. Müdahale Bekleniyor.", bootstyle="warning")

    def inject_error(self, mode):
        """SERVER: Hata enjeksiyonu (Server Backend kullanır)"""
        current_text = self.ent_mid_payload.get()
        new_text = current_text

        # Backend fonksiyonlarını çağır
        if mode == "Bit Flip": new_text = NoiseLogic.inject_bit_flip(current_text)
        elif mode == "Substitution": new_text = NoiseLogic.inject_char_substitution(current_text)
        elif mode == "Deletion": new_text = NoiseLogic.inject_char_deletion(current_text)
        elif mode == "Insertion": new_text = NoiseLogic.inject_char_insertion(current_text)
        elif mode == "Swapping": new_text = NoiseLogic.inject_char_swapping(current_text)
        elif mode == "Multi Flip": new_text = NoiseLogic.inject_multiple_bit_flips(current_text)
        elif mode == "Burst Error": new_text = NoiseLogic.inject_burst_error(current_text)

        self.ent_mid_payload.delete(0, END)
        self.ent_mid_payload.insert(0, new_text)

    def forward_packet(self):
        """SERVER: Paketi Client 2'ye ilet"""
        if not self.parsed_packet: return
        
        final_data = self.ent_mid_payload.get()
        method = self.parsed_packet.get("method", "Unknown")
        control = self.parsed_packet.get("control", "00")
        
        packet_to_send = f"{final_data}|{method}|{control}"
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 5001))
                s.sendall(packet_to_send.encode('utf-8'))
            self.lbl_mid_status.config(text="✔ Paket Client 2'ye yollandı.", bootstyle="success")
            
            # Ekranı temizle
            self.parsed_packet = {}
            self.ent_mid_payload.delete(0, END)
            self.lbl_mid_raw.config(text="-")
        except:
            messagebox.showerror("Hata", "Client 2 (Port 5001) bulunamadı.")

    def on_receiver_callback(self, result):
        """RECEIVER: Sonucu ekrana bas"""
        self.after(0, lambda: self.update_receiver_ui(result))

    def update_receiver_ui(self, result):
        status = result["status"]
        style = "success-inverse" if status == "DATA CORRECT" else "danger-inverse"
        icon = "✔" if status == "DATA CORRECT" else "✖"
        
        log = f"--- PAKET ALINDI ---\n"
        log += f"Gelen Veri: {result['data']}\n"
        log += f"Yöntem    : {result['method']}\n"
        log += f"Gelen Kod : {result['sent_crc']}\n"
        log += f"Hesaplanan: {result['calc_crc']}\n"
        log += f"SONUÇ     : {status}\n\n"
        
        self.txt_rec_log.insert(END, log)
        self.txt_rec_log.see(END)
        self.lbl_rec_result.config(text=f"{icon} {status}", bootstyle=style)

if __name__ == "__main__":
    app = NetworkAssignmentApp()
    app.mainloop()