
import socket
import zlib

# ======================================================
# KATMAN 1: MANTIK (LOGIC) ve ALGORİTMALAR
# ======================================================
class PacketLogic:
    @staticmethod
    def calc_simple_parity(text: str) -> str:
        val = 0
        for char in text.encode('utf-8'):
            val ^= char
        return f"{val:02X}"

    @staticmethod
    def calc_2d_parity(text: str) -> str:
        data_bytes = text.encode('utf-8')
        width = 8
        
        # Eğer veri tam 8'e bölünmüyorsa 0 ile doldur (padding)
        remainder = len(data_bytes) % width
        if remainder != 0:
            data_bytes += b'\x00' * (width - remainder)
            
        rows = [data_bytes[i:i+width] for i in range(0, len(data_bytes), width)]
        
        row_parities = []
        col_parities = [0] * width

        for row in rows:
            r_xor = 0
            for idx, byte in enumerate(row):
                r_xor ^= byte
                col_parities[idx] ^= byte
            row_parities.append(r_xor)

        # Sonuç: Satır Hex - Sütun Hex
        row_hex = "".join([f"{x:02X}" for x in row_parities])
        col_hex = "".join([f"{x:02X}" for x in col_parities])
        
        return f"{row_hex}-{col_hex}"

    @staticmethod
    def calc_crc32(text: str) -> str:
        crc = zlib.crc32(text.encode('utf-8'))
        return f"{crc & 0xFFFFFFFF:08X}"

    @staticmethod
    def calc_hamming(text: str) -> str:
        checksum_arr = []
        for char in text:
            ascii_val = ord(char)
            # Basit simülasyon: (ASCII * 7) mod 256
            check_byte = (ascii_val * 7) % 256 
            checksum_arr.append(f"{check_byte:02X}")
        return "".join(checksum_arr)

    @staticmethod
    def create_packet_string(payload, algo_name):
        algorithms = {
            "Parity (Even)": PacketLogic.calc_parity_even,
             "Parity (Odd)": PacketLogic.calc_parity_odd,
            "2D Parity": PacketLogic.calc_2d_parity,
            "CRC-32": PacketLogic.calc_crc32,
            "Hamming": PacketLogic.calc_hamming
        }
        
        func = algorithms.get(algo_name)
        # Eğer algoritma bulunamazsa varsayılan "00" ata
        checksum_val = func(payload) if func else "00"
        packet_str = f"{payload}|{algo_name}|{checksum_val}"
        
        return packet_str, checksum_val

    @staticmethod
    def get_algo_list():
        return ["Parity (Even)", "Parity (Odd)", "2D Parity", "CRC-32", "Hamming"]

# ======================================================
# KATMAN 2: AĞ (NETWORKING)
# ======================================================
class NetworkClient:
    @staticmethod
    def send_data(host, port, raw_packet_str):

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3) 
                s.connect((host, port))
                s.sendall(raw_packet_str.encode('utf-8'))
            return True, "Paket Gönderildi"
        except ConnectionRefusedError:
            return False, "HATA: Server (Port 5000) açık değil."
        except Exception as e:
            return False, f"HATA: {str(e)}"