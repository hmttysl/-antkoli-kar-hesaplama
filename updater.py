"""
Otomatik Güncelleme Modülü
Firebase üzerinden güncelleme kontrolü yapar ve otomatik günceller.
"""

import requests
import os
import sys
import subprocess
import tempfile
import time
from tkinter import messagebox, Toplevel, Label, ttk
import customtkinter as ctk
import threading

# ============================================================
# VERSİYON BİLGİLERİ
# ============================================================
CURRENT_VERSION = "1.2.6"
APP_NAME = "Ant Koli Kar Hesaplama"

# Firebase üzerinden versiyon kontrolü
FIREBASE_VERSION_URL = "https://ant-koli-kar-hesaplama-default-rtdb.europe-west1.firebasedatabase.app"
# ============================================================


def get_current_version():
    """Mevcut uygulama versiyonunu döndürür"""
    return CURRENT_VERSION


def check_for_updates_firebase(firebase_url):
    """Firebase'den güncelleme kontrolü yapar"""
    try:
        response = requests.get(f"{firebase_url}/app_version.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                latest_version = data.get('version', CURRENT_VERSION)
                download_url = data.get('download_url', '')
                
                return {
                    'latest_version': latest_version,
                    'current_version': CURRENT_VERSION,
                    'download_url': download_url,
                    'release_notes': data.get('notes', ''),
                    'has_update': compare_versions(latest_version, CURRENT_VERSION) > 0
                }
    except Exception as e:
        print(f"Firebase güncelleme kontrolü hatası: {e}")
    
    return None


def compare_versions(version1, version2):
    """İki versiyonu karşılaştırır. 1: v1>v2, -1: v1<v2, 0: eşit"""
    try:
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0
    except:
        return 0


def get_exe_path():
    """Çalışan exe'nin yolunu döndürür"""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(__file__)


def download_from_google_drive(file_id, destination, progress_callback=None):
    """Google Drive'dan dosya indirir (gdown kullanarak)"""
    try:
        import gdown
        
        url = f"https://drive.google.com/uc?id={file_id}"
        
        # Progress callback için wrapper
        if progress_callback:
            progress_callback(10)  # Başladı
        
        # gdown ile indir (fuzzy=True büyük dosyalar için)
        output = gdown.download(url, destination, quiet=True, fuzzy=True)
        
        if progress_callback:
            progress_callback(100)  # Bitti
        
        if output and os.path.exists(destination):
            return destination
        else:
            return None
            
    except Exception as e:
        print(f"gdown hatası: {e}")
        # Fallback: requests ile dene
        try:
            URL = "https://drive.google.com/uc?export=download&confirm=t"
            response = requests.get(URL, params={'id': file_id}, stream=True, timeout=120)
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            return destination
        except Exception as e2:
            print(f"Fallback hatası: {e2}")
            return None


def download_update(download_url, progress_callback=None):
    """Güncellemeyi indirir ve geçici dosya yolunu döndürür"""
    try:
        # Geçici dosya oluştur
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "AntKoli_Update.exe")
        
        # Google Drive linkini işle
        if "drive.google.com" in download_url:
            if "/file/d/" in download_url:
                file_id = download_url.split("/file/d/")[1].split("/")[0].split("?")[0]
                download_from_google_drive(file_id, temp_file, progress_callback)
                
                # Dosyanın gerçekten exe olup olmadığını kontrol et
                with open(temp_file, 'rb') as f:
                    header = f.read(2)
                    if header != b'MZ':  # Windows exe dosyaları MZ ile başlar
                        print("İndirilen dosya geçerli bir exe değil!")
                        return None
                
                return temp_file
        
        # Normal URL için
        response = requests.get(download_url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        downloaded = 0
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        progress_callback(progress)
        
        return temp_file
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None


def install_update(temp_file):
    """Güncellemeyi kurar"""
    try:
        if not getattr(sys, 'frozen', False):
            # Exe değilse test modunda
            messagebox.showinfo("Test Modu", f"Güncelleme indirildi: {temp_file}")
            return True
        
        current_exe = sys.executable
        exe_dir = os.path.dirname(current_exe)
        exe_name = os.path.basename(current_exe)
        
        # Batch dosyası oluştur
        batch_content = f'''@echo off
echo Guncelleme kuruluyor, lutfen bekleyin...
timeout /t 2 /nobreak >nul
del "{current_exe}"
move "{temp_file}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
'''
        
        batch_file = os.path.join(tempfile.gettempdir(), "update_antkoli.bat")
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        # Batch dosyasını çalıştır ve programı kapat
        subprocess.Popen(
            ['cmd', '/c', batch_file],
            creationflags=subprocess.CREATE_NO_WINDOW,
            shell=True
        )
        
        return True
    except Exception as e:
        print(f"Kurulum hatası: {e}")
        return False


class UpdateDialog(ctk.CTkToplevel):
    """Güncelleme indirme penceresi"""
    def __init__(self, parent, update_info):
        super().__init__(parent)
        self.update_info = update_info
        self.download_complete = False
        
        self.title("🔄 Güncelleme")
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(fg_color='#0a1628')
        
        self.transient(parent)
        self.grab_set()
        
        # Başlık
        self.title_label = ctk.CTkLabel(
            self, 
            text="📥 Güncelleme İndiriliyor...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color='white'
        )
        self.title_label.pack(pady=(30, 10))
        
        # Versiyon bilgisi
        self.version_label = ctk.CTkLabel(
            self,
            text=f"v{update_info['current_version']} → v{update_info['latest_version']}",
            font=ctk.CTkFont(size=14),
            text_color='#b0c4de'
        )
        self.version_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=300, height=20)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        # Yüzde label
        self.percent_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=14),
            text_color='#14a3a8'
        )
        self.percent_label.pack(pady=5)
        
        # İndirmeyi başlat
        self.start_download()
        
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def update_progress(self, value):
        """Progress bar'ı günceller"""
        self.progress.set(value / 100)
        self.percent_label.configure(text=f"{int(value)}%")
        self.update()
    
    def start_download(self):
        """İndirme işlemini başlatır"""
        def download_thread():
            temp_file = download_update(
                self.update_info['download_url'],
                progress_callback=self.update_progress
            )
            
            if temp_file:
                self.after(0, lambda: self.on_download_success(temp_file))
            else:
                # İndirme başarısız - tarayıcıda aç
                self.after(0, self.on_download_failed)
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def on_download_success(self, temp_file):
        """İndirme başarılı olunca çağrılır"""
        self.title_label.configure(text="✅ İndirme Tamamlandı!")
        self.percent_label.configure(text="Kuruluyor...")
        self.update()
        
        if install_update(temp_file):
            self.download_complete = True
            self.after(500, lambda: sys.exit(0))
        else:
            messagebox.showerror("Hata", "Güncelleme kurulurken hata oluştu!")
            self.destroy()
    
    def on_download_failed(self):
        """İndirme başarısız olunca direkt tarayıcıda açar"""
        import webbrowser
        
        # Pencereyi kapat
        self.destroy()
        
        # Direkt tarayıcıda aç (sormadan)
        download_url = self.update_info.get('download_url', '')
        webbrowser.open(download_url)
        
        messagebox.showinfo(
            "📥 Güncelleme İndirme",
            "Tarayıcıda indirme sayfası açıldı.\n\n"
            "1. Sağ üstten 'İndir' butonuna tıklayın\n"
            "2. Bu uygulamayı kapatın\n"
            "3. Yeni exe'yi eskisinin yerine koyun\n"
            "4. Yeni exe'yi çalıştırın"
        )


def show_update_dialog(update_info, parent=None):
    """Güncelleme dialog'unu gösterir"""
    if not update_info or not update_info.get('has_update'):
        return False
    
    notes = update_info.get('release_notes', '')
    if notes:
        notes = f"\n\n📝 {notes}"
    
    message = f"""🎉 Yeni versiyon mevcut!

Mevcut versiyon: {update_info['current_version']}
Yeni versiyon: {update_info['latest_version']}{notes}

Şimdi güncellemek ister misiniz?
(Güncelleme otomatik indirilip kurulacak)"""
    
    result = messagebox.askyesno(
        "🔄 Güncelleme Mevcut",
        message
    )
    
    if result and update_info.get('download_url'):
        # Otomatik güncelleme başlat
        if parent:
            UpdateDialog(parent, update_info)
        else:
            # Parent yoksa basit indirme yap
            messagebox.showinfo("İndiriliyor", "Güncelleme indiriliyor, lütfen bekleyin...")
            temp_file = download_update(update_info['download_url'])
            if temp_file:
                install_update(temp_file)
                sys.exit(0)
        return True
    
    return False


def auto_check_updates(firebase_url=None, silent=False):
    """Otomatik güncelleme kontrolü (uygulama başlangıcında çağrılır)"""
    try:
        if firebase_url:
            update_info = check_for_updates_firebase(firebase_url)
            if update_info:
                return update_info
    except Exception as e:
        print(f"Güncelleme kontrolü hatası: {e}")
    
    return None
