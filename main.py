"""
Antkoli Kar/Zarar Hesaplama Uygulaması
Python Tkinter + CustomTkinter ile modern masaüstü GUI
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from PIL import Image
import os
import sys
import subprocess
import threading
import io
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from database import (
    init_db, get_aylik_kira, set_aylik_kira, satis_ekle,
    tum_satislari_getir, satis_sil, istatistikleri_getir, FIREBASE_DATABASE_URL,
    get_aylik_giderler, set_aylik_giderler, get_toplam_aylik_gider, AYLIK_GIDERLER,
    tum_firmalari_getir, firma_ara, firma_istatistikleri_getir
)
from updater import auto_check_updates, show_update_dialog, CURRENT_VERSION


# Global cache - veriler arka planda yüklenir
_satislar_cache = []
_firmalar_cache = []
_cache_loaded = False

def refresh_cache():
    """Cache'i arka planda yenile"""
    global _satislar_cache, _firmalar_cache, _cache_loaded
    try:
        _satislar_cache = tum_satislari_getir()
        _firmalar_cache = tum_firmalari_getir()
        _cache_loaded = True
    except:
        pass

def start_cache_refresh():
    """Cache yenilemeyi arka planda başlat"""
    threading.Thread(target=refresh_cache, daemon=True).start()


# Uygulama dizini (exe için)
if getattr(sys, 'frozen', False):
    # PyInstaller exe içindeki dosyalar için
    APP_DIR = sys._MEIPASS
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Logo dosyası yolu
LOGO_PATH = os.path.join(APP_DIR, "logo.png")

# CustomTkinter tema ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Renk paleti
COLORS = {
    'bg_dark': '#0a1628',
    'bg_card': '#132f4c',
    'bg_elevated': '#1a3a5c',
    'primary': '#0d7377',
    'primary_light': '#14a3a8',
    'accent': '#ff6b35',
    'success': '#10b981',
    'danger': '#ef4444',
    'text_primary': '#ffffff',
    'text_secondary': '#b0c4de',
    'text_muted': '#7a8ca3',
    'border': '#2a4a6a'
}

# Ülke listesi (ISO2 kodu ve isim) - ALFABETİK SIRALI
ULKELER = [
    ("US", "ABD"), ("AF", "Afganistan"), ("DE", "Almanya"), ("AO", "Angola"),
    ("AL", "Arnavutluk"), ("AR", "Arjantin"), ("AU", "Avustralya"), ("AT", "Avusturya"),
    ("AZ", "Azerbaycan"), ("AE", "BAE"), ("BH", "Bahreyn"), ("BD", "Bangladeş"),
    ("BY", "Belarus"), ("BE", "Belçika"), ("BJ", "Benin"), ("BO", "Bolivya"),
    ("BA", "Bosna Hersek"), ("BW", "Botsvana"), ("BR", "Brezilya"), ("BN", "Brunei"),
    ("BG", "Bulgaristan"), ("BF", "Burkina Faso"), ("BT", "Butan"), ("DZ", "Cezayir"),
    ("CY", "Kıbrıs"), ("CN", "Çin"), ("CZ", "Çekya"), ("DK", "Danimarka"),
    ("TL", "Doğu Timor"), ("DO", "Dominik Cum."), ("EC", "Ekvador"), ("SV", "El Salvador"),
    ("ID", "Endonezya"), ("AM", "Ermenistan"), ("EE", "Estonya"), ("ET", "Etiyopya"),
    ("MA", "Fas"), ("FJ", "Fiji"), ("CI", "Fildişi Sahili"), ("PH", "Filipinler"),
    ("FI", "Finlandiya"), ("FR", "Fransa"), ("SS", "G. Sudan"), ("ZA", "G. Afrika"),
    ("GH", "Gana"), ("GL", "Grönland"), ("GT", "Guatemala"), ("GY", "Guyana"),
    ("GE", "Gürcistan"), ("KR", "Güney Kore"), ("HT", "Haiti"), ("IN", "Hindistan"),
    ("HR", "Hırvatistan"), ("NL", "Hollanda"), ("HK", "Hong Kong"), ("HN", "Honduras"),
    ("IQ", "Irak"), ("GB", "İngiltere"), ("IR", "İran"), ("IE", "İrlanda"),
    ("IL", "İsrail"), ("ES", "İspanya"), ("SE", "İsveç"), ("CH", "İsviçre"),
    ("IT", "İtalya"), ("IS", "İzlanda"), ("JM", "Jamaika"), ("JP", "Japonya"),
    ("KH", "Kamboçya"), ("CM", "Kamerun"), ("CA", "Kanada"), ("ME", "Karadağ"),
    ("QA", "Katar"), ("KZ", "Kazakistan"), ("KE", "Kenya"), ("CG", "Kongo"),
    ("CD", "Kongo DC"), ("XK", "Kosova"), ("CR", "Kosta Rika"), ("KW", "Kuveyt"),
    ("KP", "Kuzey Kore"), ("CU", "Küba"), ("MK", "K. Makedonya"), ("KG", "Kırgızistan"),
    ("LA", "Laos"), ("LV", "Letonya"), ("LY", "Libya"), ("LT", "Litvanya"),
    ("LB", "Lübnan"), ("LU", "Lüksemburg"), ("HU", "Macaristan"), ("MG", "Madagaskar"),
    ("MY", "Malezya"), ("MV", "Maldivler"), ("ML", "Mali"), ("MT", "Malta"),
    ("MU", "Mauritius"), ("MX", "Meksika"), ("EG", "Mısır"), ("MN", "Moğolistan"),
    ("MD", "Moldova"), ("MZ", "Mozambik"), ("MM", "Myanmar"), ("NA", "Namibya"),
    ("NP", "Nepal"), ("NE", "Nijer"), ("NG", "Nijerya"), ("NI", "Nikaragua"),
    ("NO", "Norveç"), ("UZ", "Özbekistan"), ("PK", "Pakistan"), ("PA", "Panama"),
    ("PG", "Papua Y. Gine"), ("PY", "Paraguay"), ("PE", "Peru"), ("PS", "Filistin"),
    ("PL", "Polonya"), ("PT", "Portekiz"), ("RO", "Romanya"), ("RW", "Ruanda"),
    ("RU", "Rusya"), ("SA", "S. Arabistan"), ("WS", "Samoa"), ("SN", "Senegal"),
    ("RS", "Sırbistan"), ("SG", "Singapur"), ("SK", "Slovakya"), ("SI", "Slovenya"),
    ("SB", "Solomon Adaları"), ("SO", "Somali"), ("LK", "Sri Lanka"), ("SD", "Sudan"),
    ("SR", "Surinam"), ("SY", "Suriye"), ("CL", "Şili"), ("TJ", "Tacikistan"),
    ("TZ", "Tanzanya"), ("TH", "Tayland"), ("TW", "Tayvan"), ("TG", "Togo"),
    ("TO", "Tonga"), ("TT", "Trinidad Tobago"), ("TN", "Tunus"), ("TR", "Türkiye"),
    ("TM", "Türkmenistan"), ("UG", "Uganda"), ("UA", "Ukrayna"), ("OM", "Umman"),
    ("JO", "Ürdün"), ("UY", "Uruguay"), ("VU", "Vanuatu"), ("VE", "Venezuela"),
    ("VN", "Vietnam"), ("YE", "Yemen"), ("NZ", "Yeni Zelanda"), ("ZM", "Zambiya"),
    ("ZW", "Zimbabve"),
]

def format_number(number):
    """Sayıyı Türkçe formatında binlik ayraçlı yapar (125000 -> 125.000,00)"""
    if isinstance(number, (int, float)):
        # Önce 2 ondalık basamakla formatla
        formatted = f"{number:,.2f}"
        # İngilizce formatı Türkçe'ye çevir (virgül->nokta, nokta->virgül)
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
    return str(number)


class StatCard(ctk.CTkFrame):
    """İstatistik kartı widget'ı"""
    def __init__(self, parent, icon, label, value, value_color=None):
        super().__init__(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        
        # İkon
        self.icon_label = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=28),
            text_color=COLORS['primary_light']
        )
        self.icon_label.pack(pady=(15, 5))
        
        # Etiket
        self.label = ctk.CTkLabel(
            self, text=label, font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        )
        self.label.pack()
        
        # Değer
        self.value_label = ctk.CTkLabel(
            self, text=value, font=ctk.CTkFont(size=18, weight="bold"),
            text_color=value_color or COLORS['text_primary']
        )
        self.value_label.pack(pady=(5, 15))
    
    def update_value(self, value, color=None):
        self.value_label.configure(text=value)
        if color:
            self.value_label.configure(text_color=color)


class NewSaleWindow(ctk.CTkToplevel):
    """Yeni satış penceresi"""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        
        self.title("📦 Yeni Satış Ekle")
        self.geometry("550x780")
        self.configure(fg_color=COLORS['bg_dark'])
        self.resizable(False, False)
        
        # Firma cache - bir kez yükle, sonra hep kullan
        self.firma_cache = []
        self.firma_cache_loaded = False
        
        # Pencereyi ortala
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
        
        # Firmaları arka planda yükle
        self.after(100, self.load_firma_cache)
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Ana container
        main_frame = ctk.CTkScrollableFrame(
            self, fg_color=COLORS['bg_dark'],
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame, text="📦 Yeni Satış Bilgileri",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Form alanları
        # Firma Adı ve Ülke Seçimi (yan yana)
        firma_ulke_label = ctk.CTkLabel(
            main_frame, text="🏢 Firma Adı",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        firma_ulke_label.pack(fill="x", pady=(10, 5))
        
        firma_ulke_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        firma_ulke_frame.pack(fill="x")
        
        # Firma adı entry (sol taraf - %70) + Autocomplete
        firma_entry_frame = ctk.CTkFrame(firma_ulke_frame, fg_color="transparent")
        firma_entry_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.firma_adi_entry = ctk.CTkEntry(
            firma_entry_frame, placeholder_text="Firma adını girin",
            fg_color=COLORS['bg_card'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        self.firma_adi_entry.pack(fill="x")
        self.firma_adi_entry.bind("<KeyRelease>", self.on_firma_adi_change)
        self.firma_adi_entry.bind("<FocusOut>", self.hide_autocomplete)
        
        # Autocomplete listbox
        self.autocomplete_frame = ctk.CTkFrame(
            firma_entry_frame, fg_color=COLORS['bg_elevated'],
            corner_radius=8, border_width=1, border_color=COLORS['border']
        )
        self.autocomplete_listbox = tk.Listbox(
            self.autocomplete_frame,
            font=('Segoe UI', 12),
            bg=COLORS['bg_elevated'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground='white',
            borderwidth=0,
            highlightthickness=0,
            height=5
        )
        self.autocomplete_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.autocomplete_listbox.bind("<ButtonRelease-1>", self.on_autocomplete_select)
        self.autocomplete_listbox.bind("<Return>", self.on_autocomplete_select)
        
        # Başlangıçta gizle
        self.autocomplete_visible = False
        
        # Ülke seçimi dropdown (sağ taraf) - ttk.Combobox scroll destekler
        self.selected_country_code = "TR"
        ulke_isimleri = [ulke[1] for ulke in ULKELER]
        
        # ttk stil ayarları - daha büyük font ve koyu yazı
        style = ttk.Style()
        style.configure('Country.TCombobox', 
            fieldbackground='white',
            background=COLORS['primary'],
            foreground='#1a1a2e',
            arrowcolor='#1a1a2e',
            padding=12
        )
        style.map('Country.TCombobox',
            fieldbackground=[('readonly', 'white')],
            foreground=[('readonly', '#1a1a2e')]
        )
        # Dropdown listesi için de büyük font
        self.option_add('*TCombobox*Listbox.font', ('Segoe UI', 14))
        self.option_add('*TCombobox*Listbox.background', COLORS['bg_elevated'])
        self.option_add('*TCombobox*Listbox.foreground', COLORS['text_primary'])
        
        # Combobox frame (border için)
        dropdown_frame = ctk.CTkFrame(firma_ulke_frame, fg_color=COLORS['primary'], corner_radius=8)
        dropdown_frame.pack(side="right")
        
        self.ulke_var = tk.StringVar(value="Türkiye")
        self.ulke_dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.ulke_var,
            values=ulke_isimleri,
            font=('Segoe UI', 14),
            width=16,
            style='Country.TCombobox'
        )
        self.ulke_dropdown.pack(padx=2, pady=2)
        # Önce değeri ayarla, sonra readonly yap
        self.ulke_dropdown.set("Türkiye")
        self.ulke_dropdown.configure(state="readonly")
        self.ulke_dropdown.bind("<<ComboboxSelected>>", self.on_country_changed_ttk)
        
        # Toplam Satış Tutarı (Ciro)
        self.create_form_field(main_frame, "💵 Toplam Satış Tutarı(Ciro) (₺)", "toplam_satis", "0.00")
        
        # Malzeme Gideri
        self.create_form_field(main_frame, "🏭 Malzeme Gideri (₺)", "malzeme_gideri", "0.00")
        
        # Üretim Süresi (Dakika)
        self.create_form_field(main_frame, "⏱️ Kaç dakikada üretildi?", "satis_suresi", "1")
        
        # KDV Oranı
        self.create_form_field(main_frame, "💰 KDV Oranı (%)", "kdv_orani", "20")
        
        # Üzerine Koyulan Kar (Otomatik hesaplanır)
        uzerine_kar_label = ctk.CTkLabel(
            main_frame, text="📈 Üzerine Koyulan Kar (₺) - Otomatik",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        uzerine_kar_label.pack(fill="x", pady=(10, 5))
        
        self.uzerine_kar_entry = ctk.CTkEntry(
            main_frame, placeholder_text="0.00",
            fg_color=COLORS['bg_elevated'],
            border_color=COLORS['primary'],
            text_color=COLORS['success'],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=8,
            state="disabled"
        )
        self.uzerine_kar_entry.pack(fill="x")
        
        # Ciro, malzeme ve KDV alanlarına otomatik hesaplama binding'i ekle
        self.toplam_satis_entry.bind("<KeyRelease>", self.auto_calculate_kar)
        self.malzeme_gideri_entry.bind("<KeyRelease>", self.auto_calculate_kar)
        self.kdv_orani_entry.bind("<KeyRelease>", self.auto_calculate_kar)
        
        # Notlar
        notes_label = ctk.CTkLabel(
            main_frame, text="📝 Notlar (Opsiyonel)",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        notes_label.pack(fill="x", pady=(10, 5))
        
        self.notlar_entry = ctk.CTkTextbox(
            main_frame, height=60, fg_color=COLORS['bg_card'],
            border_color=COLORS['border'], border_width=1,
            text_color=COLORS['text_primary'],
            font=ctk.CTkFont(size=14)
        )
        self.notlar_entry.pack(fill="x", pady=(0, 15))
        
        # Aylık gider bilgisi
        toplam_aylik = get_toplam_aylik_gider()
        gunluk_gider = toplam_aylik / 30
        
        gider_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_card'], corner_radius=8)
        gider_frame.pack(fill="x", pady=10)
        
        gider_label = ctk.CTkLabel(
            gider_frame,
            text=f"📊 Toplam Aylık Gider: {format_number(toplam_aylik)} ₺  |  Günlük: {format_number(gunluk_gider)} ₺",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['primary_light']
        )
        gider_label.pack(pady=12)
        
        # Hesapla butonu
        calc_btn = ctk.CTkButton(
            main_frame, text="🧮 Hesapla",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color="#ff8c5a",
            height=45,
            corner_radius=10,
            command=self.calculate
        )
        calc_btn.pack(fill="x", pady=(15, 10))
        
        # Sonuç alanı
        self.result_frame = ctk.CTkFrame(
            main_frame, fg_color=COLORS['bg_elevated'],
            corner_radius=12, border_width=2,
            border_color=COLORS['border']
        )
        self.result_frame.pack(fill="x", pady=10)
        self.result_frame.pack_forget()  # Başlangıçta gizle
        
        # Sonuç başlık satırı (başlık + kaydet butonu)
        self.result_header = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        
        self.result_title = ctk.CTkLabel(
            self.result_header, text="📊 Hesaplama Sonucu",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        
        # Kaydet butonu (başlığın yanında)
        self.save_btn = ctk.CTkButton(
            self.result_header, text="💾 Satışı Kaydet",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['success'],
            hover_color="#34d399",
            width=140,
            height=35,
            corner_radius=8,
            command=self.save_sale
        )
        
        self.result_details = ctk.CTkLabel(
            self.result_frame, text="",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        
        self.result_kar = ctk.CTkLabel(
            self.result_frame, text="",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['success']
        )
        
        self.result_yuzde = ctk.CTkLabel(
            self.result_frame, text="",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_secondary']
        )
        
        # Hesaplama sonuçlarını sakla
        self.calculation_result = None
    
    def create_form_field(self, parent, label_text, field_name, placeholder=""):
        label = ctk.CTkLabel(
            parent, text=label_text,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        label.pack(fill="x", pady=(10, 5))
        
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color=COLORS['bg_card'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        entry.pack(fill="x")
        
        setattr(self, f"{field_name}_entry", entry)
    
    def on_country_changed(self, selected_name):
        """Ülke seçildiğinde kodu güncelle"""
        for code, name in ULKELER:
            if name == selected_name:
                self.selected_country_code = code
                break
    
    def on_country_changed_ttk(self, event):
        """ttk Combobox için ülke seçildiğinde kodu güncelle"""
        selected_name = self.ulke_var.get()
        for code, name in ULKELER:
            if name == selected_name:
                self.selected_country_code = code
                break
    
    def load_firma_cache(self):
        """Firmaları arka planda cache'e yükle (thread ile)"""
        def fetch():
            try:
                firmalar = tum_firmalari_getir()
                self.firma_cache = firmalar
                self.firma_cache_loaded = True
            except:
                self.firma_cache = []
                self.firma_cache_loaded = True
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def on_firma_adi_change(self, event=None):
        """Firma adı değiştiğinde autocomplete önerilerini göster"""
        arama = self.firma_adi_entry.get().strip()
        
        if len(arama) < 2:
            self.hide_autocomplete()
            return
        
        # Cache yüklenmediyse bekle
        if not self.firma_cache_loaded:
            return
        
        # Cache'den ara (hızlı, Firebase'e gitmez)
        arama_lower = arama.lower()
        oneriler = [f for f in self.firma_cache if arama_lower in f['firma_adi'].lower()][:10]
        
        if not oneriler:
            self.hide_autocomplete()
            return
        
        # Listbox'ı temizle ve doldur
        self.autocomplete_listbox.delete(0, tk.END)
        for firma in oneriler:
            display_text = f"{firma['firma_adi']} ({firma['toplam_satis']} satış)"
            self.autocomplete_listbox.insert(tk.END, display_text)
        
        # Göster
        self.show_autocomplete()
    
    def show_autocomplete(self):
        """Autocomplete listesini göster"""
        if not self.autocomplete_visible:
            self.autocomplete_frame.pack(fill="x", pady=(2, 0))
            self.autocomplete_visible = True
    
    def hide_autocomplete(self, event=None):
        """Autocomplete listesini gizle"""
        # Kısa bir gecikme ile gizle (tıklamayı yakalamak için)
        if event:
            self.after(150, self._do_hide_autocomplete)
        else:
            self._do_hide_autocomplete()
    
    def _do_hide_autocomplete(self):
        """Gerçek gizleme işlemi"""
        if self.autocomplete_visible:
            self.autocomplete_frame.pack_forget()
            self.autocomplete_visible = False
    
    def on_autocomplete_select(self, event=None):
        """Autocomplete'den bir firma seçildiğinde"""
        selection = self.autocomplete_listbox.curselection()
        if selection:
            secilen = self.autocomplete_listbox.get(selection[0])
            # "(X satış)" kısmını çıkar
            firma_adi = secilen.split(" (")[0]
            
            # Entry'ye yaz
            self.firma_adi_entry.delete(0, tk.END)
            self.firma_adi_entry.insert(0, firma_adi)
            
            # Firmanın ülkesini bul ve dropdown'u güncelle
            for firma in self.firma_cache:
                if firma['firma_adi'] == firma_adi:
                    ulke_kodu = firma.get('ulke', 'TR')
                    # Ülke kodundan ülke adını bul
                    for code, name in ULKELER:
                        if code == ulke_kodu:
                            self.ulke_var.set(name)
                            self.selected_country_code = ulke_kodu
                            break
                    break
            
            # Önerileri gizle
            self._do_hide_autocomplete()
    
    def auto_calculate_kar(self, event=None):
        """Ciro ve malzeme gideri değiştiğinde üzerine koyulan karı otomatik hesapla"""
        try:
            toplam_satis = float(self.toplam_satis_entry.get() or 0)
            malzeme_gideri = float(self.malzeme_gideri_entry.get() or 0)
            
            # Üzerine koyulan kar = Toplam satış - Malzeme gideri (KDV düşülmeden)
            uzerine_kar = toplam_satis - malzeme_gideri
            
            # Alanı güncelle
            self.uzerine_kar_entry.configure(state="normal")
            self.uzerine_kar_entry.delete(0, "end")
            self.uzerine_kar_entry.insert(0, format_number(uzerine_kar))
            self.uzerine_kar_entry.configure(state="disabled")
            
            # Renk değiştir (kar/zarar durumuna göre)
            if uzerine_kar >= 0:
                self.uzerine_kar_entry.configure(text_color=COLORS['success'])
            else:
                self.uzerine_kar_entry.configure(text_color=COLORS['danger'])
        except ValueError:
            pass  # Geçersiz değer girildiğinde sessizce geç
    
    def calculate(self):
        try:
            firma_adi = self.firma_adi_entry.get().strip()
            malzeme_gideri = float(self.malzeme_gideri_entry.get() or 0)
            toplam_satis = float(self.toplam_satis_entry.get() or 0)
            uretim_suresi_dk = int(self.satis_suresi_entry.get() or 1)  # Dakika olarak
            kdv_orani = float(self.kdv_orani_entry.get() or 20)
            
            if not firma_adi:
                messagebox.showwarning("Uyarı", "Lütfen firma adını girin!")
                return
            
            if uretim_suresi_dk < 1:
                uretim_suresi_dk = 1
            
            # KDV hesaplama (satış tutarı KDV dahil kabul edilir)
            kdv_tutari = toplam_satis * kdv_orani / (100 + kdv_orani)
            kdv_haric_satis = toplam_satis - kdv_tutari
            
            # Üzerine koyulan kar (otomatik hesaplanır)
            uzerine_kar = kdv_haric_satis - malzeme_gideri
            
            # Aylık giderlerden dakikalık gider hesaplama
            # Firma günde 10 saat çalışıyor: 30 gün × 10 saat × 60 dk = 18.000 dk/ay
            aylik_giderler = get_aylik_giderler()
            toplam_aylik_gider = sum(aylik_giderler.values())
            dakikalik_gider = toplam_aylik_gider / 18000  # Aylık çalışma dakikası
            aylik_gider_payi = dakikalik_gider * uretim_suresi_dk
            
            # Toplam gider ve kar hesaplama
            toplam_gider = malzeme_gideri + aylik_gider_payi
            net_kar = kdv_haric_satis - toplam_gider
            
            # Kar yüzdesi
            if toplam_gider > 0:
                kar_yuzdesi = ((kdv_haric_satis - toplam_gider) / toplam_gider) * 100
            else:
                kar_yuzdesi = 0 if kdv_haric_satis == 0 else 100
            
            # Seçilen ülkenin kodunu al
            ulke_kodu = self.selected_country_code
            
            # Sonuçları sakla
            self.calculation_result = {
                'firma_adi': firma_adi,
                'malzeme_gideri': malzeme_gideri,
                'toplam_satis': toplam_satis,
                'satis_suresi': uretim_suresi_dk,  # Dakika olarak kaydediyoruz
                'kira_gideri': round(aylik_gider_payi, 2),
                'kdv_orani': kdv_orani,
                'kdv_tutari': round(kdv_tutari, 2),
                'uzerine_kar': uzerine_kar,
                'toplam_gider': round(toplam_gider, 2),
                'net_kar': round(net_kar, 2),
                'kar_yuzdesi': round(kar_yuzdesi, 2),
                'notlar': self.notlar_entry.get("1.0", "end-1c"),
                'ulke': ulke_kodu
            }
            
            # Sonuç alanını göster
            self.result_frame.pack(fill="x", pady=10)
            self.result_header.pack(fill="x", padx=15, pady=(15, 10))
            self.result_title.pack(side="left")
            self.save_btn.pack(side="right")
            
            # Gider detaylarını oluştur
            gider_detay = f"Malzeme Gideri: {format_number(malzeme_gideri)} ₺\n"
            gider_detay += f"\n--- Aylık Giderler ({uretim_suresi_dk} dakikalık payı) ---\n"
            
            gider_labels = {
                'aylik_kira': 'Kira',
                'personel': 'Personel', 
                'muhtelif': 'Muhtelif',
                'elektrik': 'Elektrik',
                'yemek': 'Yemek',
                'sgk': 'SGK',
                'yakit': 'Yakıt',
                'tutkal': 'Tutkal',
                'boya': 'Boya',
                'baglama_ipi': 'Bağlama İpi',
                'muhtasar': 'Muhtasar',
                'gecici_vergi': 'Geçici Vergi',
                'muhasebe': 'Muhasebe'
            }
            
            for key, label in gider_labels.items():
                aylik_tutar = aylik_giderler.get(key, 0)
                if aylik_tutar > 0:
                    dakikalik_pay = (aylik_tutar / 18000) * uretim_suresi_dk  # Dakika bazında hesapla
                    gider_detay += f"{label}: {format_number(dakikalik_pay)} ₺\n"
            
            gider_detay += f"─────────────────────\n"
            gider_detay += f"Aylık Gider Toplamı: {format_number(aylik_gider_payi)} ₺\n"
            gider_detay += f"TOPLAM GİDER: {format_number(toplam_gider)} ₺\n"
            gider_detay += f"\n--- Satış Bilgileri ---\n"
            gider_detay += f"Satış (KDV Dahil): {format_number(toplam_satis)} ₺\n"
            gider_detay += f"KDV (%{int(kdv_orani)}): {format_number(kdv_tutari)} ₺\n"
            gider_detay += f"KDV Hariç Satış: {format_number(kdv_haric_satis)} ₺"
            
            details_text = gider_detay
            
            self.result_details.configure(text=details_text)
            self.result_details.pack(pady=5)
            
            # Kar/Zarar durumuna göre renk
            if net_kar >= 0:
                kar_color = COLORS['success']
                kar_text = f"+{format_number(net_kar)} ₺ KAR"
            else:
                kar_color = COLORS['danger']
                kar_text = f"{format_number(net_kar)} ₺ ZARAR"
            
            self.result_kar.configure(text=kar_text, text_color=kar_color)
            self.result_kar.pack(pady=10)
            
            self.result_yuzde.configure(text=f"Kar Oranı: %{kar_yuzdesi:.2f}")
            self.result_yuzde.pack(pady=(0, 15))
            
        except ValueError as e:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
    
    def save_sale(self):
        if not self.calculation_result:
            messagebox.showwarning("Uyarı", "Önce hesaplama yapmalısınız!")
            return
        
        result = self.calculation_result
        
        # Veritabanına kaydet
        satis_ekle(
            firma_adi=result['firma_adi'],
            malzeme_gideri=result['malzeme_gideri'],
            toplam_satis_tutari=result['toplam_satis'],
            satis_suresi_gun=result['satis_suresi'],
            kira_gideri=result['kira_gideri'],
            uzerine_kar=result['uzerine_kar'],
            net_kar=result['net_kar'],
            kar_yuzdesi=result['kar_yuzdesi'],
            notlar=result['notlar'],
            ulke=result['ulke']
        )
        
        messagebox.showinfo("Başarılı", "Satış kaydı başarıyla eklendi!")
        
        # Callback'i çağır ve pencereyi kapat
        if self.on_save_callback:
            self.on_save_callback()
        
        self.destroy()


class SettingsWindow(ctk.CTkToplevel):
    """Ayarlar penceresi"""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.on_save_callback = on_save_callback
        self.gider_entries = {}
        
        self.title("⚙️ Ayarlar - Aylık Giderler")
        self.geometry("450x600")
        self.configure(fg_color=COLORS['bg_dark'])
        self.resizable(False, True)
        
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Ana container
        container = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(
            container, text="⚙️ Aylık Giderler",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 10))
        
        # Açıklama
        hint_label = ctk.CTkLabel(
            container,
            text="Bu tutarlar satış süresine göre orantılı olarak kardan düşülür.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        )
        hint_label.pack(pady=(0, 15))
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            container, fg_color="transparent",
            height=400
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Mevcut giderleri al
        mevcut_giderler = get_aylik_giderler()
        
        # Gider alanları oluştur
        for key, label in AYLIK_GIDERLER:
            frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            lbl = ctk.CTkLabel(
                frame, text=label,
                font=ctk.CTkFont(size=13),
                text_color=COLORS['text_secondary'],
                width=200,
                anchor="w"
            )
            lbl.pack(side="left")
            
            entry = ctk.CTkEntry(
                frame,
                fg_color=COLORS['bg_card'],
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
                font=ctk.CTkFont(size=13),
                height=35,
                width=150,
                corner_radius=6
            )
            entry.insert(0, str(mevcut_giderler.get(key, 0)))
            entry.pack(side="right")
            
            self.gider_entries[key] = entry
        
        # Toplam gösterge
        self.toplam_label = ctk.CTkLabel(
            container,
            text=f"📊 Toplam Aylık Gider: {format_number(sum(mevcut_giderler.values()))} ₺",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary_light']
        )
        self.toplam_label.pack(pady=(15, 10))
        
        # Kaydet butonu
        save_btn = ctk.CTkButton(
            container, text="💾 Kaydet",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_light'],
            height=45,
            corner_radius=10,
            command=self.save_settings
        )
        save_btn.pack(fill="x", pady=(5, 0))
    
    def save_settings(self):
        try:
            giderler = {}
            for key, entry in self.gider_entries.items():
                giderler[key] = float(entry.get() or 0)
            
            set_aylik_giderler(giderler)
            messagebox.showinfo("Başarılı", "Aylık giderler kaydedildi!")
            
            if self.on_save_callback:
                self.on_save_callback()
            
            self.destroy()
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayılar girin!")


class SaleCard(ctk.CTkFrame):
    """Satış kartı widget'ı"""
    
    # Bayrak cache (sınıf düzeyinde paylaşımlı)
    _flag_cache = {}
    
    def __init__(self, parent, satis_data, on_delete):
        super().__init__(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        self.satis_id = satis_data['id']
        self.on_delete = on_delete
        
        # Ana içerik
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Sol taraf - Firma ve tarih
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        # Firma adı
        firma_label = ctk.CTkLabel(
            left_frame, text=f"🏢 {satis_data['firma_adi']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        firma_label.pack(anchor="w")
        
        # Tarih ve bayrak satırı
        tarih_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        tarih_row.pack(anchor="w", pady=(2, 0))
        
        tarih = satis_data['tarih'][:10] if satis_data.get('tarih') else "-"
        tarih_label = ctk.CTkLabel(
            tarih_row, text=f"📅 {tarih}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            anchor="w"
        )
        tarih_label.pack(side="left", padx=(0, 10))
        
        # Bayrak için label (tarih satırında)
        ulke_kodu = satis_data.get('ulke', 'TR')
        self.flag_label = ctk.CTkLabel(tarih_row, text="", width=24)
        self.flag_label.pack(side="left")
        
        # Bayrağı arka planda yükle
        self.load_flag(ulke_kodu)
        
        # Sağ taraf - Değerler
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y")
        
        values_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        values_frame.pack(side="left", padx=(0, 20))
        
        # Satış Tutarı
        satis_frame = ctk.CTkFrame(values_frame, fg_color="transparent")
        satis_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            satis_frame, text="Satış Tutarı",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack()
        
        ctk.CTkLabel(
            satis_frame, text=f"{format_number(satis_data['toplam_satis_tutari'])} ₺",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Net Kar/Zarar
        kar_frame = ctk.CTkFrame(values_frame, fg_color="transparent")
        kar_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            kar_frame, text="Net Kar/Zarar",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack()
        
        kar = satis_data['net_kar']
        kar_color = COLORS['success'] if kar >= 0 else COLORS['danger']
        kar_text = f"+{format_number(kar)} ₺" if kar >= 0 else f"{format_number(kar)} ₺"
        
        ctk.CTkLabel(
            kar_frame, text=kar_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=kar_color
        ).pack()
        
        # Kar Oranı
        oran_frame = ctk.CTkFrame(values_frame, fg_color="transparent")
        oran_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            oran_frame, text="Kar Oranı",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack()
        
        oran_color = COLORS['success'] if satis_data['kar_yuzdesi'] >= 0 else COLORS['danger']
        
        ctk.CTkLabel(
            oran_frame, text=f"%{satis_data['kar_yuzdesi']:.1f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=oran_color
        ).pack()
        
        # Sil butonu
        delete_btn = ctk.CTkButton(
            right_frame, text="🗑️",
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color=COLORS['danger'],
            width=40,
            height=40,
            corner_radius=8,
            command=self.delete_sale
        )
        delete_btn.pack(side="right")
    
    def load_flag(self, country_code):
        """Bayrağı yükle"""
        if country_code in SaleCard._flag_cache:
            img = SaleCard._flag_cache[country_code]
            if img:
                self.flag_label.configure(image=img, text="")
            return
        
        def fetch():
            try:
                url = f"https://flagcdn.com/w40/{country_code.lower()}.png"
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    img_data = io.BytesIO(response.content)
                    pil_image = Image.open(img_data)
                    ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(24, 16))
                    SaleCard._flag_cache[country_code] = ctk_image
                    self.after(0, lambda: self.flag_label.configure(image=ctk_image, text=""))
            except:
                SaleCard._flag_cache[country_code] = None
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def delete_sale(self):
        if messagebox.askyesno("Onay", "Bu satışı silmek istediğinizden emin misiniz?"):
            satis_sil(self.satis_id)
            if self.on_delete:
                self.on_delete()


class FirmaDetayWindow(ctk.CTkToplevel):
    """Firma detay penceresi - yıllık satış grafiği"""
    
    AY_ISIMLERI = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 
                   'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
    
    def __init__(self, parent, firma_adi):
        super().__init__(parent)
        self.firma_adi = firma_adi
        self.current_year = datetime.now().year  # Mevcut yıl
        self.selected_year = self.current_year   # Seçili yıl
        self.all_sales_data = None               # Tüm satış verileri
        
        self.title(f"📊 {firma_adi} - Satış Detayları")
        self.geometry("900x750")
        self.configure(fg_color=COLORS['bg_dark'])
        
        self.transient(parent)
        
        self.create_widgets()
        self.load_data()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Ana frame
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Başlık
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame, text=f"📊 {self.firma_adi}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(side="left")
        
        close_btn = ctk.CTkButton(
            header_frame, text="← Geri",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_light'],
            width=90,
            height=35,
            corner_radius=8,
            command=self.destroy
        )
        close_btn.pack(side="right")
        
        # Özet istatistikler
        self.stats_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        self.stats_frame.pack(fill="x", pady=(0, 15))
        
        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="Yükleniyor...",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['primary_light']
        )
        self.stats_label.pack(pady=12)
        
        # Yıl seçim alanı
        year_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        year_frame.pack(fill="x", pady=(0, 10))
        
        # Sol ok butonu
        self.prev_year_btn = ctk.CTkButton(
            year_frame, text="◀ Önceki Yıl",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_elevated'],
            width=120,
            height=35,
            corner_radius=8,
            command=self.prev_year
        )
        self.prev_year_btn.pack(side="left")
        
        # Yıl göstergesi
        self.year_label = ctk.CTkLabel(
            year_frame, text=f"📅 {self.selected_year}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.year_label.pack(side="left", expand=True)
        
        # Sağ ok butonu
        self.next_year_btn = ctk.CTkButton(
            year_frame, text="Sonraki Yıl ▶",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_elevated'],
            width=120,
            height=35,
            corner_radius=8,
            command=self.next_year
        )
        self.next_year_btn.pack(side="right")
        
        # Grafik alanı
        self.chart_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Aylık detay tablosu
        self.table_frame = ctk.CTkScrollableFrame(main_frame, fg_color=COLORS['bg_card'], corner_radius=10, height=150)
        self.table_frame.pack(fill="x")
    
    def load_data(self):
        """Firma verilerini yükle"""
        def fetch():
            try:
                data = firma_istatistikleri_getir(self.firma_adi)
                self.after(0, lambda: self.display_data(data))
            except Exception as e:
                print(f"Veri yükleme hatası: {e}")
                self.after(0, lambda: self.display_data(None))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def display_data(self, data):
        """Verileri göster"""
        if not data:
            self.stats_label.configure(text="Veri bulunamadı")
            return
        
        # Tüm satış verilerini sakla
        self.all_sales_data = data
        
        # Seçili yıl için verileri göster
        self.update_year_display()
    
    def update_year_display(self):
        """Seçili yıla göre verileri güncelle"""
        if not self.all_sales_data:
            return
        
        # Yıl etiketini güncelle
        self.year_label.configure(text=f"📅 {self.selected_year}")
        
        # Sonraki yıl butonunu kontrol et
        if self.selected_year >= self.current_year:
            self.next_year_btn.configure(state="disabled")
        else:
            self.next_year_btn.configure(state="normal")
        
        # Seçili yıla göre satışları filtrele
        yil_satislari = []
        for satis in self.all_sales_data['satislar']:
            tarih = satis.get('tarih', '')
            if not tarih:
                continue
            try:
                parts = tarih.split(' ')[0].split('-')
                if len(parts[0]) == 4:  # YYYY-MM-DD
                    yil = int(parts[0])
                else:  # DD-MM-YYYY
                    yil = int(parts[2])
                
                if yil == self.selected_year:
                    yil_satislari.append(satis)
            except:
                continue
        
        # Yıl istatistiklerini hesapla
        toplam_satis = len(yil_satislari)
        toplam_ciro = sum(s.get('toplam_satis_tutari', 0) for s in yil_satislari)
        toplam_kar = sum(s.get('net_kar', 0) for s in yil_satislari)
        ort_kar = sum(s.get('kar_yuzdesi', 0) for s in yil_satislari) / toplam_satis if toplam_satis > 0 else 0
        
        self.stats_label.configure(
            text=f"📊 {self.selected_year} Yılı: {toplam_satis} satış  |  "
                 f"💰 Ciro: {format_number(toplam_ciro)} ₺  |  "
                 f"📈 Kar: {format_number(toplam_kar)} ₺  |  "
                 f"% Ort: {ort_kar:.1f}"
        )
        
        # Aylık verileri hesapla (seçili yıl için)
        aylik_veriler = self.hesapla_aylik_veriler(yil_satislari)
        
        # Grafik oluştur
        self.create_chart(aylik_veriler)
        
        # Tablo oluştur
        self.create_table(aylik_veriler)
    
    def prev_year(self):
        """Önceki yıla git"""
        self.selected_year -= 1
        self.update_year_display()
    
    def next_year(self):
        """Sonraki yıla git"""
        if self.selected_year < self.current_year:
            self.selected_year += 1
            self.update_year_display()
    
    def hesapla_aylik_veriler(self, satislar):
        """Satışları seçili yılın aylarına göre grupla"""
        aylik = {}
        
        # Seçili yılın 12 ayı için boş değerler oluştur
        for ay in range(1, 13):
            key = f"{self.selected_year}-{ay:02d}"
            aylik[key] = {'satis': 0, 'ciro': 0, 'kar': 0}
        
        # Satışları aylara dağıt
        for satis in satislar:
            tarih = satis.get('tarih', '')
            if not tarih:
                continue
            
            try:
                # Tarih formatını kontrol et (DD-MM-YYYY veya YYYY-MM-DD)
                if '-' in tarih:
                    parts = tarih.split(' ')[0].split('-')
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        yil, ay = int(parts[0]), int(parts[1])
                    else:  # DD-MM-YYYY
                        yil, ay = int(parts[2]), int(parts[1])
                    
                    key = f"{yil}-{ay:02d}"
                    if key in aylik:
                        aylik[key]['satis'] += 1
                        aylik[key]['ciro'] += satis.get('toplam_satis_tutari', 0)
                        aylik[key]['kar'] += satis.get('net_kar', 0)
            except:
                continue
        
        # Sıralı liste olarak döndür (Ocak'tan Aralık'a)
        sonuc = []
        for ay in range(1, 13):
            key = f"{self.selected_year}-{ay:02d}"
            sonuc.append({
                'ay': self.AY_ISIMLERI[ay - 1],
                'yil': str(self.selected_year),
                'key': key,
                **aylik[key]
            })
        
        return sonuc
    
    def create_chart(self, aylik_veriler):
        """Grafik oluştur - Aylık Kar Grafiği"""
        # Eski içeriği temizle
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Figure oluştur - koyu tema
        fig = Figure(figsize=(8, 3.5), dpi=100, facecolor='#0a1628')
        ax = fig.add_subplot(111)
        
        # Arka plan rengi
        ax.set_facecolor('#0a1628')
        
        # Veri hazırla - sadece kar
        aylar = [f"{v['ay']}" for v in aylik_veriler]
        karlar = [v['kar'] for v in aylik_veriler]
        
        x = range(len(aylar))
        
        # Bar renkleri - kar pozitifse yeşil, negatifse kırmızı
        colors = ['#10b981' if k >= 0 else '#ef4444' for k in karlar]
        
        # Bar chart - kar
        bars = ax.bar(x, karlar, 0.6, color=colors, alpha=0.9, edgecolor='#1a3a5c', linewidth=1)
        
        # Eksen ayarları
        ax.set_xticks(x)
        ax.set_xticklabels(aylar, fontsize=11, color='#b0c4de', fontweight='bold')
        ax.set_ylabel('Kar (₺)', color='#10b981', fontsize=12, fontweight='bold')
        
        ax.tick_params(axis='y', labelcolor='#b0c4de', labelsize=9)
        ax.tick_params(axis='x', colors='#b0c4de')
        
        # Bar değerlerini üzerine yaz
        for bar, val in zip(bars, karlar):
            if val != 0:
                ypos = bar.get_height()
                if val >= 0:
                    va = 'bottom'
                    ypos += 50
                else:
                    va = 'top'
                    ypos -= 50
                
                text = f"{format_number(val)}"
                color = '#10b981' if val >= 0 else '#ef4444'
                ax.text(bar.get_x() + bar.get_width()/2, ypos, text,
                       ha='center', va=va, fontsize=8, color=color, fontweight='bold')
        
        # Sıfır çizgisi
        ax.axhline(y=0, color='#2a4a6a', linewidth=1, linestyle='-')
        
        # Grid - sadece yatay
        ax.grid(True, alpha=0.2, color='#2a4a6a', axis='y', linestyle='--')
        ax.set_axisbelow(True)
        
        # Başlık
        ax.set_title('📈 Aylık Kar Grafiği', fontsize=14, color='#ffffff', fontweight='bold', pad=15)
        
        # Spine gizle
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        fig.tight_layout()
        
        # Canvas oluştur ve ekle
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_table(self, aylik_veriler):
        """Aylık detay tablosu oluştur"""
        # Önce eski içeriği temizle
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Başlık satırı
        header = ctk.CTkFrame(self.table_frame, fg_color=COLORS['primary'])
        header.pack(fill="x", pady=(0, 5))
        
        # Ay, Satış, Ciro, Kar, Ort. Kar % - eşit dağılım
        ctk.CTkLabel(header, text="📅 Ay", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(side="left", expand=True, fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text="📦 Satış", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(side="left", expand=True, fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text="💰 Ciro", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(side="left", expand=True, fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text="📈 Kar", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(side="left", expand=True, fill="x", padx=10, pady=10)
        ctk.CTkLabel(header, text="% Ort. Kar", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white").pack(side="left", expand=True, fill="x", padx=10, pady=10)
        
        # Veri satırları (en yeni en üstte)
        for v in reversed(aylik_veriler):
            if v['satis'] == 0:
                continue  # Boş ayları atla
                
            row = ctk.CTkFrame(self.table_frame, fg_color=COLORS['bg_elevated'])
            row.pack(fill="x", pady=2)
            
            # Ay
            ctk.CTkLabel(
                row, text=f"{v['ay']} {v['yil']}", font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(side="left", expand=True, fill="x", padx=10, pady=10)
            
            # Satış
            ctk.CTkLabel(
                row, text=str(v['satis']), font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS['primary_light']
            ).pack(side="left", expand=True, fill="x", padx=10, pady=10)
            
            # Ciro
            ctk.CTkLabel(
                row, text=f"{format_number(v['ciro'])} ₺", font=ctk.CTkFont(size=12),
                text_color=COLORS['text_secondary']
            ).pack(side="left", expand=True, fill="x", padx=10, pady=10)
            
            # Kar
            kar_color = COLORS['success'] if v['kar'] >= 0 else COLORS['danger']
            kar_text = f"+{format_number(v['kar'])} ₺" if v['kar'] >= 0 else f"{format_number(v['kar'])} ₺"
            ctk.CTkLabel(
                row, text=kar_text, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=kar_color
            ).pack(side="left", expand=True, fill="x", padx=10, pady=10)
            
            # Ortalama Kar %
            if v['ciro'] > 0:
                kar_yuzde = (v['kar'] / v['ciro']) * 100
            else:
                kar_yuzde = 0
            yuzde_color = COLORS['success'] if kar_yuzde >= 0 else COLORS['danger']
            ctk.CTkLabel(
                row, text=f"%{kar_yuzde:.1f}", font=ctk.CTkFont(size=12, weight="bold"),
                text_color=yuzde_color
            ).pack(side="left", expand=True, fill="x", padx=10, pady=10)


class FirmaListesiWindow(ctk.CTkToplevel):
    """Firma listesi ve istatistikleri penceresi"""
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("🏢 Firma Listesi")
        self.geometry("750x600")
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Bayrak cache
        self.flag_cache = {}
        
        self.transient(parent)
        
        self.create_widgets()
        self.load_firmalar()
        self.center_window()
    
    def get_flag_image(self, country_code):
        """Ülke bayrağını indir ve CTkImage olarak döndür"""
        if country_code in self.flag_cache:
            return self.flag_cache[country_code]
        
        try:
            url = f"https://flagcdn.com/w40/{country_code.lower()}.png"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                img_data = io.BytesIO(response.content)
                pil_image = Image.open(img_data)
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(24, 16))
                self.flag_cache[country_code] = ctk_image
                return ctk_image
        except:
            pass
        
        return None
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Ana frame
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Başlık
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame, text="🏢 Firma Listesi",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(side="left")
        
        # Butonlar
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        refresh_btn = ctk.CTkButton(
            btn_frame, text="🔄 Yenile",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_elevated'],
            width=90,
            height=35,
            corner_radius=8,
            command=self.load_firmalar
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            btn_frame, text="← Geri",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_light'],
            width=90,
            height=35,
            corner_radius=8,
            command=self.destroy
        )
        close_btn.pack(side="left")
        
        # İstatistik özeti
        self.stats_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        self.stats_frame.pack(fill="x", pady=(0, 15))
        
        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['primary_light']
        )
        self.stats_label.pack(pady=12)
        
        # Firma listesi (scrollable)
        self.firma_frame = ctk.CTkScrollableFrame(
            main_frame, fg_color="transparent",
            corner_radius=0
        )
        self.firma_frame.pack(fill="both", expand=True)
        
        # Boş mesaj
        self.empty_label = ctk.CTkLabel(
            self.firma_frame,
            text="📭 Henüz firma kaydı bulunmuyor",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_muted']
        )
    
    def load_firmalar(self):
        # Mevcut içeriği temizle
        for widget in self.firma_frame.winfo_children():
            widget.destroy()
        
        # Cache varsa direkt göster
        global _firmalar_cache, _cache_loaded
        if _cache_loaded and _firmalar_cache:
            self._display_firmalar(_firmalar_cache)
            # Arka planda güncelle
            start_cache_refresh()
            return
        
        # Cache yoksa arka planda yükle
        def fetch():
            try:
                firmalar = tum_firmalari_getir()
                self.after(0, lambda: self._display_firmalar(firmalar))
            except Exception as e:
                self.after(0, lambda: self._display_firmalar([]))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def _display_firmalar(self, firmalar):
        """Firmaları göster (ana thread'de)"""
        # Mevcut içeriği temizle
        for widget in self.firma_frame.winfo_children():
            widget.destroy()
        
        if not firmalar:
            self.empty_label = ctk.CTkLabel(
                self.firma_frame,
                text="📭 Henüz firma kaydı bulunmuyor",
                font=ctk.CTkFont(size=16),
                text_color=COLORS['text_muted']
            )
            self.empty_label.pack(pady=50)
            self.stats_label.configure(text="Toplam: 0 firma")
            return
        
        # İstatistik özeti
        toplam_firma = len(firmalar)
        toplam_ciro = sum(f['toplam_ciro'] for f in firmalar)
        toplam_kar = sum(f['toplam_kar'] for f in firmalar)
        
        self.stats_label.configure(
            text=f"📊 Toplam: {toplam_firma} firma  |  "
                 f"💰 Ciro: {format_number(toplam_ciro)} ₺  |  "
                 f"📈 Kar: {format_number(toplam_kar)} ₺"
        )
        
        # Ülke adlarını al
        ulke_dict = {code: name for code, name in ULKELER}
        
        # Firma kartlarını oluştur
        for firma in firmalar:
            self.create_firma_card(firma, ulke_dict)
    
    def create_firma_card(self, firma, ulke_dict):
        """Firma kartı oluştur"""
        card = ctk.CTkFrame(self.firma_frame, fg_color=COLORS['bg_card'], corner_radius=10)
        card.pack(fill="x", pady=(0, 8))
        
        # Tıklama özelliği ekle
        firma_adi = firma['firma_adi']
        card.bind("<Button-1>", lambda e, f=firma_adi: self.open_firma_detay(f))
        card.configure(cursor="hand2")
        
        # Ana içerik
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        content.bind("<Button-1>", lambda e, f=firma_adi: self.open_firma_detay(f))
        
        # Sol - Firma adı ve ülke
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        firma_label = ctk.CTkLabel(
            left, text=f"🏢 {firma['firma_adi']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        firma_label.pack(anchor="w")
        
        # Ülke satırı (bayrak + isim)
        ulke_frame = ctk.CTkFrame(left, fg_color="transparent")
        ulke_frame.pack(anchor="w", pady=(2, 0))
        
        ulke_kodu = firma['ulke']
        ulke_adi = ulke_dict.get(ulke_kodu, ulke_kodu)
        
        # Bayrak resmi
        flag_img = self.get_flag_image(ulke_kodu)
        if flag_img:
            flag_label = ctk.CTkLabel(ulke_frame, image=flag_img, text="")
            flag_label.pack(side="left", padx=(0, 6))
        
        ulke_label = ctk.CTkLabel(
            ulke_frame, text=ulke_adi,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted'],
            anchor="w"
        )
        ulke_label.pack(side="left")
        
        # Sağ - İstatistikler
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")
        
        stats_container = ctk.CTkFrame(right, fg_color="transparent")
        stats_container.pack(side="left")
        
        # Satış sayısı
        satis_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        satis_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            satis_frame, text="Satış",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack()
        
        ctk.CTkLabel(
            satis_frame, text=str(firma['toplam_satis']),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['primary_light']
        ).pack()
        
        # Ciro
        ciro_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        ciro_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            ciro_frame, text="Ciro",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack()
        
        ctk.CTkLabel(
            ciro_frame, text=f"{format_number(firma['toplam_ciro'])} ₺",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Kar
        kar_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        kar_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            kar_frame, text="Kar",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack()
        
        kar = firma['toplam_kar']
        kar_color = COLORS['success'] if kar >= 0 else COLORS['danger']
        kar_text = f"+{format_number(kar)} ₺" if kar >= 0 else f"{format_number(kar)} ₺"
        
        ctk.CTkLabel(
            kar_frame, text=kar_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=kar_color
        ).pack()
    
    def open_firma_detay(self, firma_adi):
        """Firma detay penceresini aç"""
        FirmaDetayWindow(self, firma_adi)


class SalesHistoryWindow(ctk.CTkToplevel):
    """Geçmiş satışlar penceresi"""
    def __init__(self, parent, on_delete_callback):
        super().__init__(parent)
        self.on_delete_callback = on_delete_callback
        
        self.title("📋 Geçmiş Satışlar")
        self.geometry("700x550")
        self.configure(fg_color=COLORS['bg_dark'])
        
        self.transient(parent)
        
        self.create_widgets()
        self.load_sales()
        self.center_window()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Ana frame
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Başlık
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame, text="📋 Geçmiş Satışlar",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(side="left")
        
        # Butonlar için frame
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        refresh_btn = ctk.CTkButton(
            btn_frame, text="🔄 Yenile",
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_elevated'],
            width=90,
            height=35,
            corner_radius=8,
            command=self.refresh_all
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            btn_frame, text="← Geri",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_light'],
            width=90,
            height=35,
            corner_radius=8,
            command=self.destroy
        )
        close_btn.pack(side="left")
        
        # Satışlar listesi (scrollable)
        self.sales_frame = ctk.CTkScrollableFrame(
            main_frame, fg_color="transparent",
            corner_radius=0
        )
        self.sales_frame.pack(fill="both", expand=True)
        
        # Boş mesaj
        self.empty_label = ctk.CTkLabel(
            self.sales_frame,
            text="📭 Henüz satış kaydı bulunmuyor",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_muted']
        )
    
    def load_sales(self):
        # Mevcut kartları temizle
        for widget in self.sales_frame.winfo_children():
            widget.destroy()
        
        # Cache varsa direkt göster
        global _satislar_cache, _cache_loaded
        if _cache_loaded and _satislar_cache:
            self._display_sales(_satislar_cache)
            # Arka planda güncelle
            start_cache_refresh()
            return
        
        # Cache yoksa arka planda yükle
        def fetch():
            try:
                satislar = tum_satislari_getir()
                self.after(0, lambda: self._display_sales(satislar))
            except:
                self.after(0, lambda: self._display_sales([]))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def _display_sales(self, satislar):
        """Satışları göster (ana thread'de)"""
        # Mevcut kartları temizle
        for widget in self.sales_frame.winfo_children():
            widget.destroy()
        
        if not satislar:
            self.empty_label = ctk.CTkLabel(
                self.sales_frame,
                text="📭 Henüz satış kaydı bulunmuyor",
                font=ctk.CTkFont(size=16),
                text_color=COLORS['text_muted']
            )
            self.empty_label.pack(pady=50)
            return
        
        # Satış kartlarını oluştur
        for satis in satislar:
            card = SaleCard(self.sales_frame, satis, self.refresh_all)
            card.pack(fill="x", pady=(0, 10))
    
    def refresh_all(self):
        # Cache'i yenile ve sonra göster
        global _satislar_cache, _cache_loaded
        _cache_loaded = False
        start_cache_refresh()
        self.after(500, self.load_sales)
        if self.on_delete_callback:
            self.on_delete_callback()


class AntkolitApp(ctk.CTk):
    """Ana uygulama penceresi"""
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları
        self.title(f"📦 Ant Koli - Kar/Zarar Hesaplama v{CURRENT_VERSION}")
        self.geometry("900x650")
        self.configure(fg_color=COLORS['bg_dark'])
        self.minsize(800, 600)
        
        # Firebase veritabanını başlat
        if not init_db():
            messagebox.showwarning(
                "Bağlantı Uyarısı",
                "Firebase'e bağlanılamadı!\n\n"
                "Lütfen database.py dosyasındaki\n"
                "FIREBASE_DATABASE_URL değerini\n"
                "kendi Firebase URL'nizle değiştirin.\n\n"
                "Detaylar için README.txt dosyasına bakın."
            )
        
        self.create_widgets()
        self.update_stats()
        self.center_window()
        
        # Cache'i arka planda yükle (pencereler hızlı açılsın)
        start_cache_refresh()
        
        # Otomatik yenileme (her 30 saniyede bir)
        self.auto_refresh()
        
        # Güncelleme kontrolü (başlangıçta)
        self.after(2000, self.check_updates)  # 2 saniye sonra kontrol et
    
    def check_updates(self):
        """Güncelleme kontrolü yapar (arka planda)"""
        def check():
            try:
                update_info = auto_check_updates(FIREBASE_DATABASE_URL, silent=False)
                if update_info and update_info.get('has_update'):
                    self.after(0, lambda: show_update_dialog(update_info, parent=self))
            except Exception as e:
                print(f"Güncelleme kontrolü hatası: {e}")
        
        threading.Thread(target=check, daemon=True).start()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Logo ve başlık
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(side="left", fill="y")
        
        # Logo resmi yükle
        if os.path.exists(LOGO_PATH):
            try:
                logo_image = ctk.CTkImage(
                    light_image=Image.open(LOGO_PATH),
                    dark_image=Image.open(LOGO_PATH),
                    size=(200, 60)
                )
                logo_label = ctk.CTkLabel(
                    logo_frame, image=logo_image, text=""
                )
            except Exception as e:
                print(f"Logo yüklenemedi: {e}")
            logo_label = ctk.CTkLabel(
                logo_frame, text="📦 ANT KOLİ",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#FFD700"
            )
        else:
            logo_label = ctk.CTkLabel(
                logo_frame, text="📦 ANT KOLİ",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#FFD700"
            )
        logo_label.pack(side="left", padx=(0, 15))
        
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            title_frame, text="Kar/Zarar Hesaplama Sistemi",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_muted']
        )
        subtitle_label.pack(anchor="w", pady=20)
        
        # Sağ üst butonlar frame
        top_buttons = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_buttons.pack(side="right", pady=20)
        
        # Ayarlar butonu
        settings_btn = ctk.CTkButton(
            top_buttons, text="⚙️ Ayarlar",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_elevated'],
            border_width=1,
            border_color=COLORS['border'],
            width=120,
            height=40,
            corner_radius=10,
            command=self.open_settings
        )
        settings_btn.pack(side="right", padx=(10, 0))
        
        # Firma Listesi butonu (turkuaz)
        firma_btn = ctk.CTkButton(
            top_buttons, text="🏢",
            font=ctk.CTkFont(size=20),
            fg_color="#06b6d4",
            hover_color="#22d3ee",
            width=45,
            height=40,
            corner_radius=10,
            command=self.open_firma_listesi
        )
        firma_btn.pack(side="right", padx=(0, 8))
        
        # Dünya Haritası butonu (küçük ikon)
        map_btn = ctk.CTkButton(
            top_buttons, text="🌍",
            font=ctk.CTkFont(size=20),
            fg_color="#10b981",
            hover_color="#34d399",
            width=45,
            height=40,
            corner_radius=10,
            command=self.open_world_map
        )
        map_btn.pack(side="right", padx=(0, 8))
        
        # İstatistik kartları
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=15)
        
        # 4 istatistik kartı
        self.stat_cards = {}
        
        stats_data = [
            ("toplam_satis", "📊", "Toplam Satış", "0"),
            ("toplam_ciro", "💰", "Toplam Ciro", "0.00 ₺"),
            ("toplam_kar", "📈", "Toplam Kar", "0.00 ₺"),
            ("ort_kar", "%", "Ort. Kar Oranı", "%0.0")
        ]
        
        for i, (key, icon, label, value) in enumerate(stats_data):
            card = StatCard(stats_frame, icon, label, value)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 10, 0))
            self.stat_cards[key] = card
        
        # Ana butonlar
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=30, pady=20)
        
        # Yeni Satış butonu
        new_sale_btn = ctk.CTkButton(
            buttons_frame, text="➕ Yeni Satış",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_light'],
            height=60,
            corner_radius=12,
            command=self.open_new_sale
        )
        new_sale_btn.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Geçmiş Satışlar butonu
        history_btn = ctk.CTkButton(
            buttons_frame, text="📋 Geçmiş Satışlar",
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_elevated'],
            border_width=1,
            border_color=COLORS['border'],
            height=60,
            corner_radius=12,
            command=self.open_history
        )
        history_btn.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Bilgi kutusu
        info_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=12)
        info_frame.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        info_title = ctk.CTkLabel(
            info_frame, text="💡 Nasıl Kullanılır?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['text_primary']
        )
        info_title.pack(pady=(25, 15))
        
        info_text = """
1️⃣  İlk olarak Ayarlar'dan aylık kira tutarınızı girin
2️⃣  Yeni Satış butonuna tıklayarak satış bilgilerini girin
3️⃣  Hesapla butonuyla kar/zarar hesaplamasını görün
4️⃣  Satışı kaydedin ve geçmiş satışlardan takip edin

📌 Kira gideri, satış süresine orantılı olarak otomatik hesaplanır
📌 Tüm veriler yerel veritabanında güvenle saklanır
        """
        
        info_label = ctk.CTkLabel(
            info_frame, text=info_text,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        info_label.pack(pady=(0, 25), padx=30)
        
        # Footer
        footer_label = ctk.CTkLabel(
            self, text=f"© 2024 Ant Koli Kar/Zarar Hesaplama Sistemi | v{CURRENT_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        )
        footer_label.pack(pady=(0, 15))
    
    def update_stats(self):
        """İstatistikleri arka planda güncelle (UI donmaz)"""
        def fetch_and_update():
            try:
                stats = istatistikleri_getir()
                # UI güncellemesi ana thread'de yapılmalı
                self.after(0, lambda: self._apply_stats(stats))
            except Exception as e:
                print(f"İstatistik güncelleme hatası: {e}")
        
        # Arka planda çalıştır
        threading.Thread(target=fetch_and_update, daemon=True).start()
    
    def _apply_stats(self, stats):
        """İstatistikleri UI'a uygula (ana thread'de)"""
        try:
            self.stat_cards['toplam_satis'].update_value(str(stats['toplam_satis']))
            self.stat_cards['toplam_ciro'].update_value(f"{format_number(stats['toplam_ciro'])} ₺")
            
            # Kar rengi
            kar_color = COLORS['success'] if stats['toplam_kar'] >= 0 else COLORS['danger']
            kar_text = f"+{format_number(stats['toplam_kar'])} ₺" if stats['toplam_kar'] >= 0 else f"{format_number(stats['toplam_kar'])} ₺"
            self.stat_cards['toplam_kar'].update_value(kar_text, kar_color)
            
            self.stat_cards['ort_kar'].update_value(f"%{stats['ortalama_kar_yuzdesi']:.1f}")
        except:
            pass  # Pencere kapanmış olabilir
    
    def open_new_sale(self):
        """Yeni satış penceresini aç"""
        NewSaleWindow(self, self.update_stats)
    
    def open_settings(self):
        """Ayarlar penceresini aç"""
        SettingsWindow(self, self.update_stats)
    
    def open_history(self):
        """Geçmiş satışlar penceresini aç"""
        SalesHistoryWindow(self, self.update_stats)
    
    def open_firma_listesi(self):
        """Firma listesi penceresini aç"""
        FirmaListesiWindow(self)
    
    def open_world_map(self):
        """Dünya satış haritasını aç"""
        # Exe veya py modunda çalışıp çalışmadığını kontrol et
        if getattr(sys, 'frozen', False):
            # Exe modu - map_viewer.exe'yi çağır
            exe_dir = os.path.dirname(sys.executable)
            map_viewer_exe = os.path.join(exe_dir, "map_viewer.exe")
            
            if os.path.exists(map_viewer_exe):
                try:
                    subprocess.Popen(
                        [map_viewer_exe],
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                except Exception as e:
                    messagebox.showerror("Hata", f"Harita açılamadı: {e}")
            else:
                messagebox.showerror("Hata", "map_viewer.exe bulunamadı!\nExe dosyasının yanında olmalı.")
        else:
            # Geliştirme modu - Python ile çalıştır
            web_dir = os.path.join(APP_DIR, "web-dashboard", "Fintech World Map Dashboard")
            dist_dir = os.path.join(web_dir, "dist")
            map_viewer_path = os.path.join(APP_DIR, "map_viewer.py")
            
            if os.path.exists(os.path.join(dist_dir, "index.html")):
                try:
                    subprocess.Popen(
                        [sys.executable, map_viewer_path],
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                except Exception as e:
                    messagebox.showerror("Hata", f"Harita açılamadı: {e}")
            else:
                messagebox.showinfo(
                    "Harita Hazırlanıyor",
                    "Dünya haritası henüz hazır değil.\n\n"
                    f"cd \"{web_dir}\"\n"
                    "npm install\n"
                    "npm run build"
                )
    
    def auto_refresh(self):
        """Verileri otomatik yeniler (90 saniyede bir)"""
        self.update_stats()
        self.after(90000, self.auto_refresh)  # 90 saniye


if __name__ == "__main__":
    app = AntkolitApp()
    app.mainloop()

