import os
import time
import requests
import re # Metin temizliği için en garanti yöntem

# --- AYARLAR ---
# ARTIK KLASÖR YOLU GİRMENE GEREK YOK.
# BU SCRİPT HANGİ KLASÖRDEYSE ORADAKİ DOSYALARI DÜZELTİR.
BEKLEME_SURESI = 0.5 
# ---------------

def kesin_cozum():
    # Scriptin çalıştığı klasörü otomatik al
    mevcut_klasor = os.getcwd()
    
    print(f"Script şu klasörde çalışıyor: {mevcut_klasor}")
    print("Buradaki .lua dosyaları taranıyor...\n")

    files = [f for f in os.listdir(mevcut_klasor) if f.endswith(".lua")]
    
    if not files:
        print("HATA: Bu klasörde hiç .lua dosyası yok!")
        return

    for dosya_adi in files:
        tam_yol = os.path.join(mevcut_klasor, dosya_adi)
        app_id = dosya_adi.replace(".lua", "")

        # Dosya adı sayı değilse (örn: ayy.py veya settings.lua) atla
        if not app_id.isdigit():
            continue

        try:
            # 1. DOSYAYI OKU
            with open(tam_yol, "r", encoding="utf-8", errors="ignore") as f:
                icerik = f.read()

            # 2. TEMİZLİK (REGEX İLE KESİN ÇÖZÜM)
            # (?m) -> Multiline modu
            # ^.*?setManifestid.*$ -> İçinde setManifestid geçen tüm satırı bul
            # re.sub ile bunları siliyoruz.
            
            # Önce setManifestid satırlarını siliyoruz (Büyük küçük harf fark etmeksizin)
            yeni_icerik = re.sub(r'(?i)^.*?setmanifestid.*$', '', icerik, flags=re.MULTILINE)
            
            # Eski scriptten kalan yorum satırlarını siliyoruz (-- Yeni DLC...)
            yeni_icerik = re.sub(r'(?i)^.*?yeni dlc eklendi.*$', '', yeni_icerik, flags=re.MULTILINE)
            
            # Boş satırları temizle (Arka arkaya gelen boşlukları teke indir)
            # Satır satır bölüp boş olanları eliyoruz
            satirlar = [s.strip() for s in yeni_icerik.splitlines() if s.strip()]
            
            # Şu an elimizde tertemiz, sıkıştırılmış kodlar var.
            # Bunları string'e çevirelim
            temiz_metin = "\n".join(satirlar)

            # 3. STEAM'DEN DLC ÇEK
            yeni_dlc_listesi = []
            try:
                url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&filters=basic,dlc"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if str(app_id) in data and data[str(app_id)]['success']:
                        oyun_verisi = data[str(app_id)]['data']
                        if 'dlc' in oyun_verisi:
                            for dlc_id in oyun_verisi['dlc']:
                                # Eğer dosyanın içinde bu ID yoksa ekle
                                if str(dlc_id) not in temiz_metin:
                                    yeni_dlc_listesi.append(dlc_id)
            except Exception as api_err:
                print(f"Steam Hatası ({dosya_adi}): {api_err}")

            # 4. KAYDETME (ÜZERİNE YAZMA)
            with open(tam_yol, "w", encoding="utf-8") as f:
                f.write(temiz_metin)
                
                # Eğer yeni DLC varsa en alta ekle
                if yeni_dlc_listesi:
                    f.write("\n") # Bir alt satıra in
                    # DLC'leri alt alta yaz
                    dlc_blogu = "\n".join([f"addappid({dlc})" for dlc in yeni_dlc_listesi])
                    f.write(dlc_blogu)
                    print(f"[OK] {dosya_adi} -> Temizlendi ve {len(yeni_dlc_listesi)} DLC eklendi.")
                else:
                    print(f"[OK] {dosya_adi} -> Sadece temizlendi (Yeni DLC yok).")

            time.sleep(BEKLEME_SURESI)

        except Exception as e:
            print(f"HATA ({dosya_adi}): {e}")

    print("\n--- İŞLEM TAMAMLANDI ---")
    input("Çıkmak için Enter'a bas...")

if __name__ == "__main__":
    kesin_cozum()