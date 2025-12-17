📡 Veri İletişimi ve Hata Denetim Simülatörü
Bu proje, Veri İletişimi (Data Communication) dersi kapsamında; verilerin ağ üzerindeki iletimini, iletim sırasında oluşabilecek gürültüleri (hataları) ve bu hataların matematiksel yöntemlerle tespit edilmesini simüle eden bir Soket Programlama (Socket Programming) uygulamasıdır.

🚀 Proje Hakkında
Bu uygulama üç ana bileşenden oluşur ve TCP/IP protokolü üzerinden haberleşir:

Client 1 (Sender): Veriyi oluşturur, seçilen algoritma (CRC, Parity vb.) ile kontrol kodunu hesaplar ve paketler.

Server (Middleman/Corruptor): Veriyi yakalar, arayüz üzerinden seçilen yöntemlerle (Bit Flip, Burst Error vb.) veriyi kasten bozar ve hedefe iletir.

Client 2 (Receiver): Gelen paketi açar, sağlamasını tekrar hesaplar ve verinin bozulup bozulmadığını tespit eder.



📂 Dosya Yapısı
ui_app.py: Uygulamanın Tek Grafik Arayüz (GUI) dosyasıdır. Tüm sistemi buradan yönetirsiniz.

sender.py: Gönderici tarafın matematiksel hesaplamalarını ve paket oluşturma mantığını içerir.

middleman.py: Hata enjeksiyon (Error Injection) algoritmalarını içerir.

receiver.py: Alıcı tarafın doğrulama ve dinleme mantığını içerir.

⚙️ Özellikler ve Algoritmalar
1. Hata Tespit Yöntemleri (Error Detection Methods)
Gönderici tarafında aşağıdaki algoritmalar simüle edilmiştir:

Parity (Even/Odd): Basit eşlik biti kontrolü.

2D Parity: Veriyi matrise dökerek satır ve sütun eşlik kontrolü.

CRC-32 (Cyclic Redundancy Check): Yaygın kullanılan güçlü bir hata tespit algoritması.

Hamming Code: Hata tespiti ve düzeltimi için simülasyon.

Internet Checksum: IP protokollerinde kullanılan checksum yöntemi.

2. Hata Enjeksiyon Yöntemleri (Error Injection)
Sunucu (Server) tarafında veri üzerinde şu bozulmalar yapılabilir:

Bit Flip: Rastgele bir bitin ters çevrilmesi (0->1, 1->0).

Character Substitution: Bir karakterin rastgele değişmesi.

Character Deletion: Rastgele bir karakterin silinmesi.

Character Insertion: Araya rastgele karakter eklenmesi.

Character Swapping: Yan yana iki karakterin yer değiştirmesi.

Multiple Bit Flips: Birden fazla bitin rastgele bozulması.

Burst Error: Ardışık 3-8 karakterlik bir veri bloğunun tamamen bozulması.

🛠️ Kurulum ve Çalıştırma
Gereksinimler
Python 3.x

ttkbootstrap kütüphanesi (Arayüz için)

Kurulum
Gerekli kütüphaneyi yükleyin:

Bash

pip install ttkbootstrap
Çalıştırma
Projeyi başlatmak için sadece main.py dosyasını çalıştırmanız yeterlidir:

Bash

python ui_app.py
Kullanım Adımları
Gönderici (Yeşil Panel):

Bir metin girin (Örn: "MERHABA").

Bir yöntem seçin (Örn: "CRC-32").

"PAKET OLUŞTUR VE GÖNDER" butonuna basın.

Sunucu/Bozucu (Kırmızı Panel):

Paket bu alana düşer.

Hata Butonlarından birine basarak veriyi bozun (İsteğe bağlı).

"CLIENT 2'YE İLET" butonuna basın.

Alıcı (Mavi Panel):

Sonuç otomatik olarak görünür.

Eğer veri bozulmuşsa "DATA CORRUPTED", sağlamsa "DATA CORRECT" yazar.

📝 Paket Yapısı
Veriler ağ üzerinde şu formatta taşınır:

Plaintext

VERI | YONTEM | KONTROL_KODU
Örnek: HELLO | CRC-32 | A1B2C3D4
Sunucu sadece VERI kısmını bozar, | ayıraçlarına ve KONTROL_KODU kısmına dokunmaz.
