# -- coding: utf-8 --
import socket
import random
import threading

# ======================================================
# KATMAN 1: MANTIK (LOGIC) - HATA ENJEKSİYONU
# PDF Kaynak: [34-52]
# ======================================================
class NoiseLogic:
    @staticmethod
    def _split_packet(packet_str):
        parts = packet_str.split('|')
        if len(parts) >= 3:
            return parts[0], parts[1], parts[2]
        return packet_str, "", ""

    @staticmethod
    def inject_bit_flip(text):
        """ 1. Bit Flip: Rastgele bir biti ters çevirir [cite: 36] """
        if not text: return text
        b_data = bytearray(text, 'utf-8')
        idx = random.randint(0, len(b_data) - 1)
        mask = 1 << random.randint(0, 7)
        b_data[idx] ^= mask
        return b_data.decode('utf-8', errors='replace')

    @staticmethod
    def inject_multiple_bit_flips(text):
        """ 6. Multiple Bit Flips: Birden fazla biti bozar  """
        if not text: return text
        # 2 ile 4 arasında rastgele sayıda bit flip uygula
        count = random.randint(2, 4)
        temp_text = text
        for _ in range(count):
            temp_text = NoiseLogic.inject_bit_flip(temp_text)
        return temp_text

    @staticmethod
    def inject_char_substitution(text):
        """ 2. Character Substitution [cite: 38] """
        if not text: return text
        idx = random.randint(0, len(text) - 1)
        new_char = chr(random.randint(65, 90)) 
        return text[:idx] + new_char + text[idx+1:]

    @staticmethod
    def inject_char_deletion(text):
        """ 3. Character Deletion [cite: 40] """
        if len(text) < 2: return text
        idx = random.randint(0, len(text) - 1)
        return text[:idx] + text[idx+1:]

    @staticmethod
    def inject_char_insertion(text):
        """ 4. Random Character Insertion [cite: 43] """
        if not text: return "X"
        idx = random.randint(0, len(text))
        new_char = chr(random.randint(65, 90))
        return text[:idx] + new_char + text[idx:]

    @staticmethod
    def inject_char_swapping(text):
        """ 5. Character Swapping: Yan yana iki harfi değiştirir  """
        if len(text) < 2: return text
        idx = random.randint(0, len(text) - 2)
        # String immutable olduğu için listeye çevirip değiştiriyoruz
        chars = list(text)
        chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
        return "".join(chars)

    @staticmethod
    def inject_burst_error(text):
        """ 7. Burst Error: 3-8 karakterlik diziyi bozar [cite: 51] """
        if len(text) < 3: return NoiseLogic.inject_bit_flip(text)
        
        burst_len = random.randint(3, min(8, len(text)))
        start_idx = random.randint(0, len(text) - burst_len)
        
        corrupted_segment = "".join(chr(random.randint(33, 126)) for _ in range(burst_len))
        return text[:start_idx] + corrupted_segment + text[start_idx+burst_len:]

    @staticmethod
    def process_packet(raw_packet, mode_name):
        try:
            data, method, checksum = NoiseLogic._split_packet(raw_packet)
            if not method: return raw_packet

            # Hata Yöntemleri Haritası
            modes = {
                "No Error": lambda x: x,
                "Bit Flip": NoiseLogic.inject_bit_flip,
                "Multi Flip": NoiseLogic.inject_multiple_bit_flips, # YENİ
                "Substitution": NoiseLogic.inject_char_substitution,
                "Deletion": NoiseLogic.inject_char_deletion,
                "Insertion": NoiseLogic.inject_char_insertion,
                "Swapping": NoiseLogic.inject_char_swapping,       # YENİ
                "Burst Error": NoiseLogic.inject_burst_error
            }
            
            func = modes.get(mode_name, lambda x: x)
            corrupted_data = func(data)

            return f"{corrupted_data}|{method}|{checksum}"

        except Exception as e:
            print(f"Packet Processing Error: {e}")
            return raw_packet