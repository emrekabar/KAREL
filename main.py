import customtkinter as ctk
import ctypes
from tkinter import messagebox
import json
import os
import sys
import threading
import datetime
from otomasyon import raporu_cek_ve_gonder

# Görev çubuğu ikonu için Windows uygulama kimliği
try:
    myappid = 'karel.vardiya.otomasyon.v2'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
AYAR_DOSYASI = "ayarlar.json"

# EXE içine gömülen dosyaları bulmak için gereken  fonksiyon
def kaynak_yolu(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class VardiyaBotu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KAREL")
        self.geometry("450x380")
        self.resizable(False, False)
        
        # ---  İKON YÜKLEME ---
        ikon_yolu = kaynak_yolu("uygulama_logosu.ico")
        if os.path.exists(ikon_yolu):
            self.iconbitmap(ikon_yolu)
            self.after(200, lambda: self.iconbitmap(ikon_yolu))
        
        # Varsayılan Ayarlar
        self.ayarlar = {
            "tarayici": "Edge",
            "mesaj_metni": "Vardiya raporu ektedir.",
            "whatsapp_sohbet": "Grup Adi",
            "zaman_araligi": 60 # Varsayılan 60 dakika
        }
        self.ayarlari_yukle()
        self.sistem_aktif = False
        self.hedef_zaman = None
        
        self.arayuzu_olustur()

    def ayarlari_yukle(self):
        if os.path.exists(AYAR_DOSYASI):
            with open(AYAR_DOSYASI, "r", encoding="utf-8") as f:
                yuklenen = json.load(f)
                for k, v in self.ayarlar.items():
                    if k not in yuklenen: yuklenen[k] = v
                self.ayarlar = yuklenen

    def ayarlari_kaydet(self):
        with open(AYAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(self.ayarlar, f, ensure_ascii=False, indent=4)

    def arayuzu_olustur(self):
        ctk.CTkLabel(self, text="Vardiya Kontrol Paneli", font=("Roboto", 22, "bold")).pack(pady=15)
        
        self.lbl_durum = ctk.CTkLabel(self, text="Durum: Bekliyor...", font=("Roboto", 14), text_color="gray")
        self.lbl_durum.pack(pady=0)

        # SAYAÇ ETİKETİ
        self.lbl_sayac = ctk.CTkLabel(self, text="", font=("Roboto", 16, "bold"), text_color="#f39c12")
        self.lbl_sayac.pack(pady=5)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.btn_baslat = ctk.CTkButton(btn_frame, text="Sistemi Başlat", fg_color="#2ecc71", hover_color="#27ae60", text_color="white", command=self.sistemi_baslat)
        self.btn_baslat.grid(row=0, column=0, padx=10)

        self.btn_durdur = ctk.CTkButton(btn_frame, text="Durdur", fg_color="#e74c3c", hover_color="#c0392b", 
                                        text_color="white", text_color_disabled="white", 
                                        state="disabled", command=self.sistemi_durdur)
        self.btn_durdur.grid(row=0, column=1, padx=10)

        self.btn_test = ctk.CTkButton(self, text="🚀 Hemen Gönder (Test Et)", fg_color="#f39c12", hover_color="#e67e22", text_color="white", width=310, command=self.manuel_test_baslat)
        self.btn_test.pack(pady=10)

        ctk.CTkButton(self, text="⚙ Ayarları Düzenle", fg_color="transparent", border_width=1, text_color="white", command=self.ayarlar_penceresi_ac).pack(side="bottom", pady=20)

    def ayarlar_penceresi_ac(self):
        ap = ctk.CTkToplevel(self)
        ap.title("Sistem Ayarları")
        ap.geometry("400x420")
        ap.attributes("-topmost", True)
        ap.resizable(False, False)

        ctk.CTkLabel(ap, text="Tarayıcı:").pack(pady=(10, 0))
        self.tar_sec = ctk.CTkComboBox(ap, values=["Edge", "Chrome"], width=250)
        self.tar_sec.set(self.ayarlar.get("tarayici", "Edge"))
        self.tar_sec.pack(pady=5)

        ctk.CTkLabel(ap, text="WhatsApp Mesaj Notu:").pack(pady=(5, 0))
        self.mes_gir = ctk.CTkEntry(ap, width=250)
        self.mes_gir.insert(0, self.ayarlar.get("mesaj_metni", ""))
        self.mes_gir.pack(pady=5)

        ctk.CTkLabel(ap, text="WhatsApp Sohbet Adı:").pack(pady=(5, 0))
        self.soh_gir = ctk.CTkEntry(ap, width=250)
        self.soh_gir.insert(0, self.ayarlar.get("whatsapp_sohbet", ""))
        self.soh_gir.pack(pady=5)

        ctk.CTkLabel(ap, text="Gönderim Aralığı (Dakika):").pack(pady=(5, 0))
        self.sure_gir = ctk.CTkEntry(ap, width=250)
        self.sure_gir.insert(0, str(self.ayarlar.get("zaman_araligi", 60)))
        self.sure_gir.pack(pady=5)

        def kaydet():
            try:
                dakika = int(self.sure_gir.get())
            except ValueError:
                dakika = 60 # Harf girilirse varsayılan 60 olsun
            
            self.ayarlar.update({"tarayici": self.tar_sec.get(), "mesaj_metni": self.mes_gir.get(), "whatsapp_sohbet": self.soh_gir.get(), "zaman_araligi": dakika})
            self.ayarlari_kaydet()
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi.")
            
            # Eğer sistem aktifken ayar değiştirilirse sayacı yeni ayara göre hemen güncelle
            if self.sistem_aktif:
                self.hedef_zaman = self.hedef_zamani_hesapla()
            
            ap.destroy()

        ctk.CTkButton(ap, text="💾 Kaydet", command=kaydet).pack(pady=20)

    # --- BİLGİSAYAR SAATİNE SENKRONİZASYON ALGORİTMASI ---
    def hedef_zamani_hesapla(self):
        simdi = datetime.datetime.now()
        aralik = int(self.ayarlar.get("zaman_araligi", 60))
        if aralik <= 0: aralik = 60
        
        # İçinde bulunduğumuz saatin tam başını bul (Örn: 14:35 ise 14:00:00 yapar)
        saat_basi = simdi.replace(minute=0, second=0, microsecond=0)
        
        # Şu anki dakikayı aralığa bölüp 1 ekleyerek bir sonraki katsayıyı buluyoruz.
        sonraki_dilim_katsayisi = (simdi.minute // aralik) + 1
        eklenecek_dakika = sonraki_dilim_katsayisi * aralik
        
        yeni_hedef = saat_basi + datetime.timedelta(minutes=eklenecek_dakika)
        return yeni_hedef

    def islem_yurut(self):
        try:
            raporu_cek_ve_gonder(self.ayarlar)
        except Exception as e:
            print(f"Hata detayı: {e}")
        finally:
            # test butonu her zaman tekrar basılabilir hale gelir.
            self.btn_test.configure(state="normal")
            if self.sistem_aktif:
                self.lbl_durum.configure(text="Durum: Aktif (Bekleniyor)", text_color="#2ecc71")
            else:
                self.lbl_durum.configure(text="Durum: Bekliyor...", text_color="gray")

    def manuel_test_baslat(self):
        self.lbl_durum.configure(text="Durum: Test işlemi yapılıyor...", text_color="#f39c12")
        self.btn_test.configure(state="disabled")
        threading.Thread(target=self.islem_yurut, daemon=True).start()

    def sistemi_baslat(self):
        self.sistem_aktif = True
        self.lbl_durum.configure(text="Durum: Aktif (Saat başına senkronize)", text_color="#2ecc71")
        self.btn_baslat.configure(state="disabled")
        self.btn_durdur.configure(state="normal")
        
        # Matematiksel olarak bir sonraki saat dilimini hesapla
        self.hedef_zaman = self.hedef_zamani_hesapla()
        self.sayaci_guncelle()

    def sistemi_durdur(self):
        self.sistem_aktif = False
        self.hedef_zaman = None
        self.lbl_durum.configure(text="Durum: Durduruldu", text_color="#e74c3c")
        self.lbl_sayac.configure(text="")
        self.btn_baslat.configure(state="normal")
        self.btn_durdur.configure(state="disabled")

    def sayaci_guncelle(self):
        if not self.sistem_aktif or not self.hedef_zaman: return

        simdi = datetime.datetime.now()
        kalan = self.hedef_zaman - simdi

        # Zamanı geldiyse tetikle
        if kalan.total_seconds() <= 0:
            self.lbl_sayac.configure(text="Rapor gönderiliyor...")
            threading.Thread(target=self.islem_yurut, daemon=True).start()
            # İşlem bittikten sonra bir sonraki saat dilimini tekrar hesapla
            self.hedef_zaman = self.hedef_zamani_hesapla()
        else:
            # Ekranda Geri Sayımı Göster
            saat, kalan_sn = divmod(int(kalan.total_seconds()), 3600)
            dk, sn = divmod(kalan_sn, 60)
            
            if saat > 0:
                self.lbl_sayac.configure(text=f"Sonraki gönderime: {saat:02d} sa {dk:02d} dk {sn:02d} sn")
            else:
                self.lbl_sayac.configure(text=f"Sonraki gönderime: {dk:02d} dk {sn:02d} sn")
        
        # Her 1 saniyede bir kendini tekrar çağır 
        self.after(1000, self.sayaci_guncelle)

if __name__ == "__main__":
    VardiyaBotu().mainloop()