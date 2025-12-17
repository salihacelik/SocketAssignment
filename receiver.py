# -- coding: utf-8 --
import socket
import zlib
import threading

# ======================================================
# KATMAN 1: MANTIK (LOGIC)
# ======================================================
class VerificationLogic:
    @staticmethod
    def calc_parity_even(text: str) -> str:
        ones = VerificationLogic._count_set_bits(text)
        return "01" if (ones % 2 != 0) else "00"

    @staticmethod
    def calc_parity_odd(text: str) -> str:
        
        ones = VerificationLogic._count_set_bits(text)
        return "01" if (ones % 2 == 0) else "00"
    @staticmethod
    def calc_2d_parity(text: str) -> str:
        #2D Parity Hesaplama
        data_bytes = text.encode('utf-8')
        width = 8
        remainder = len(data_bytes) % width
        if remainder != 0:
            data_bytes += b'\x00' * (width - remainder)
            
        rows = [data_bytes[i:i+width] for i in range(0, len(data_bytes), width)]
        col_parities = [0] * width
        row_parities = []

        for row in rows:
            r_xor = 0
            for idx, byte in enumerate(row):
                r_xor ^= byte
                col_parities[idx] ^= byte
            row_parities.append(r_xor)

        row_hex = "".join([f"{x:02X}" for x in row_parities])
        col_hex = "".join([f"{x:02X}" for x in col_parities])
        return f"{row_hex}-{col_hex}"

    @staticmethod
    def calc_crc32(text: str) -> str:
        #CRC-32 Hesaplama
        crc = zlib.crc32(text.encode('utf-8'))
        return f"{crc & 0xFFFFFFFF:08X}"

    @staticmethod
    def calc_hamming(text: str) -> str:
        #Hamming Simülasyonu
        checksum_arr = []
        for char in text:
            ascii_val = ord(char)
            check_byte = (ascii_val * 7) % 256 
            checksum_arr.append(f"{check_byte:02X}")
        return "".join(checksum_arr)

    @staticmethod
    def verify_packet(raw_packet):
       
        #Gelen paketi parçalar, yeniden hesaplar ve durumu raporlar.
        
        # 1. Paketi Parçala: DATA|METHOD|CHECKSUM
        try:
            parts = raw_packet.split('|')
            if len(parts) < 3:
                return {
                    "status": "INVALID FORMAT",
                    "data": raw_packet,
                    "method": "Unknown",
                    "sent_crc": "N/A",
                    "calc_crc": "N/A"
                }
            
            data = parts[0]
            method = parts[1]
            sent_checksum = parts[2]
        except:
            return {"status": "ERROR"}

        # 2. Yönteme Göre Yeniden Hesapla
        algorithms = {
            "Parity": VerificationLogic.calc_simple_parity,
            "2D Parity": VerificationLogic.calc_2d_parity,
            "CRC-32": VerificationLogic.calc_crc32,
            "Hamming": VerificationLogic.calc_hamming
        }

        func = algorithms.get(method)
        if not func:
            return {"status": "UNKNOWN METHOD", "data": data, "method": method}

        calculated_checksum = func(data)

        # 3. Karşılaştır
        # Eğer veri bozulmadıysa checksumlar EŞİT olmalıdır.
        if sent_checksum == calculated_checksum:
            status = "DATA CORRECT" 
        else:
            status = "DATA CORRUPTED" 

        return {
            "status": status,
            "data": data,
            "method": method,
            "sent_crc": sent_checksum,
            "calc_crc": calculated_checksum
        }

# ======================================================
# KATMAN 2: AĞ (NETWORKING)
# ======================================================
class ReceiverServer:
    def __init__(self, port, on_result_callback):
        self.port = port
        self.callback = on_result_callback
        self.running = False

    def start(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            srv.bind(("localhost", self.port))
            srv.listen(1)
            
            while self.running:
                try:
                    conn, addr = srv.accept()
                    data = conn.recv(4096).decode('utf-8')
                    conn.close()

                    if data:
                        # Gelen ham veriyi mantık katmanına gönder
                        result = VerificationLogic.verify_packet(data)
                        # Sonucu UI'ya bildir
                        self.callback(result)
                except Exception as e:
                    print(f"Bağlantı Hatası: {e}")
                    
        except Exception as e:
            print(f"Sunucu Başlatma Hatası (Port {self.port}): {e}")