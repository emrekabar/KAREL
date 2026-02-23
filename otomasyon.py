import pyautogui
import time
import io
import os
import pygetwindow as gw
import win32clipboard
import ctypes

# DPI ayarlarını Windows ile senkronize et (Koordinat kaymasını önler)
try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

def panoya_resim_kopyala(clip_type, data):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
    finally:
        # Pano her zaman kapatılmalı, yoksa ikinci kez açılmaz
        win32clipboard.CloseClipboard()

def raporu_cek_ve_gonder(ayarlar):
    wp_sohbet = ayarlar.get("whatsapp_sohbet")
    mesaj_metni = ayarlar.get("mesaj_metni", "")
    tarayici_adi = ayarlar.get("tarayici", "Edge")

    try:
        pencereler = [w for w in gw.getWindowsWithTitle(tarayici_adi) if w.visible]
        if not pencereler:
            print(f"❌ {tarayici_adi} bulunamadı!")
            return
        
        browser = pencereler[0]
        browser.activate()
        browser.maximize()
        time.sleep(1.5)

        # 1. Rapor Sekmesini Yenile
        pyautogui.hotkey('ctrl', '1')
        time.sleep(0.5)
        pyautogui.press('f5')
        time.sleep(8) 
        x = max(0, browser.left + 8)
        y = max(0, browser.top + 8)
        w = browser.width - 16
        h = browser.height - 16

        # SADECE PENCEREYİ ÇEK
        img = pyautogui.screenshot(region=(x, y, w, h))
        
        if not os.path.exists("temp"): os.makedirs("temp")
        img.save(os.path.join("temp", "son_rapor.png"))

        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        panoya_resim_kopyala(win32clipboard.CF_DIB, data)

        # 3. WhatsApp Gönderim
        pyautogui.hotkey('ctrl', '2')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'alt', '/')
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.5)
        
        pyautogui.write(wp_sohbet, interval=0.1)
        time.sleep(4) 
        pyautogui.press('down')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(3) 
        
        if mesaj_metni:
            pyautogui.write(mesaj_metni, interval=0.05)
            time.sleep(1)
        
        pyautogui.press('enter')
        print("✅ Gönderim başarılı.")

    except Exception as e:
        print(f"❌ Hata: {e}")