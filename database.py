"""
Firebase Realtime Database - REST API ile Online Veritabanı
Tüm bilgisayarlar aynı verilere erişir ve anlık senkronize olur.
"""

import requests
from datetime import datetime
import json

# ============================================================
# FIREBASE AYARLARI - BU KISMI KENDİ BİLGİLERİNİZLE DEĞİŞTİRİN
# ============================================================
# Firebase Console > Project Settings > General > Your apps > Web app
# Realtime Database URL'sini buraya yazın (sonunda .json olmadan)

FIREBASE_DATABASE_URL = "https://ant-koli-kar-hesaplama-default-rtdb.europe-west1.firebasedatabase.app"

# Örnek: "https://antkoli-kar-hesaplama-default-rtdb.europe-west1.firebasedatabase.app"
# ============================================================


def firebase_get(path):
    """Firebase'den veri okur"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/{path}.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Firebase okuma hatası: {e}")
        return None


def firebase_set(path, data):
    """Firebase'e veri yazar (üzerine yazar)"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/{path}.json"
        response = requests.put(url, json=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Firebase yazma hatası: {e}")
        return False


def firebase_push(path, data):
    """Firebase'e yeni veri ekler (benzersiz ID ile)"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/{path}.json"
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            return response.json().get('name')  # Benzersiz ID döner
        return None
    except Exception as e:
        print(f"❌ Firebase ekleme hatası: {e}")
        return None


def firebase_update(path, data):
    """Firebase'deki veriyi günceller"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/{path}.json"
        response = requests.patch(url, json=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Firebase güncelleme hatası: {e}")
        return False


def firebase_delete(path):
    """Firebase'den veri siler"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/{path}.json"
        response = requests.delete(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Firebase silme hatası: {e}")
        return False


def test_connection():
    """Firebase bağlantısını test eder"""
    try:
        url = f"{FIREBASE_DATABASE_URL}/.json?shallow=true"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False


def init_db():
    """Veritabanını başlatır ve bağlantıyı test eder"""
    if "YOUR-PROJECT-ID" in FIREBASE_DATABASE_URL:
        print("⚠️ Firebase URL ayarlanmamış! database.py dosyasını düzenleyin.")
        return False
    
    if not test_connection():
        print("❌ Firebase'e bağlanılamadı! İnternet bağlantınızı ve URL'yi kontrol edin.")
        return False
    
    print("✅ Firebase bağlantısı başarılı!")
    
    # Ayarları kontrol et, yoksa oluştur
    ayarlar = firebase_get("ayarlar")
    if not ayarlar:
        varsayilan_ayarlar = {
            "aylik_kira": 0,
            "personel": 0,
            "muhtelif": 0,
            "elektrik": 0,
            "yemek": 0,
            "sgk": 0,
            "yakit": 0,
            "tutkal": 0,
            "boya": 0,
            "baglama_ipi": 0,
            "muhtasar": 0,
            "gecici_vergi": 0,
            "muhasebe": 0
        }
        firebase_set("ayarlar", varsayilan_ayarlar)
        print("✅ Varsayılan ayarlar oluşturuldu.")
    
    return True


# Aylık gider kalemleri listesi
AYLIK_GIDERLER = [
    ("aylik_kira", "🏠 Kira (aylık)"),
    ("personel", "👷 Personel (aylık)"),
    ("muhtelif", "📦 Muhtelif Giderler (aylık)"),
    ("elektrik", "💡 Elektrik (aylık)"),
    ("yemek", "🍽️Yemek (aylık)"),
    ("sgk", "🏥 SGK (aylık)"),
    ("yakit", "⛽ Yakıt (aylık)"),
    ("tutkal", "🧴 Tutkal (aylık)"),
    ("boya", "🎨 Boya (aylık)"),
    ("baglama_ipi", "🧵 Bağlama İpi (aylık)"),
    ("muhtasar", "📋 Muhtasar (aylık)"),
    ("gecici_vergi", "💰 Geçici Vergi (aylık)"),
    ("muhasebe", "📊 Muhasebe (aylık)")
]

def get_aylik_giderler():
    """Tüm aylık giderleri getirir"""
    ayarlar = firebase_get("ayarlar")
    if ayarlar:
        giderler = {}
        for key, label in AYLIK_GIDERLER:
            giderler[key] = float(ayarlar.get(key, 0))
        return giderler
    return {key: 0 for key, label in AYLIK_GIDERLER}


def get_aylik_kira():
    """Aylık kira tutarını getirir (geriye uyumluluk için)"""
    giderler = get_aylik_giderler()
    return giderler.get("aylik_kira", 0)


def get_toplam_aylik_gider():
    """Toplam aylık gideri hesaplar"""
    giderler = get_aylik_giderler()
    return sum(giderler.values())


def set_aylik_giderler(giderler_dict):
    """Tüm aylık giderleri günceller"""
    return firebase_update("ayarlar", giderler_dict)


def set_aylik_kira(kira):
    """Aylık kira tutarını günceller (geriye uyumluluk için)"""
    return firebase_update("ayarlar", {"aylik_kira": kira})


def satis_ekle(firma_adi, malzeme_gideri, toplam_satis_tutari, satis_suresi_gun, 
               kira_gideri, uzerine_kar, net_kar, kar_yuzdesi, notlar='', ulke='TR'):
    """Yeni satış kaydı ekler"""
    yeni_satis = {
        "firma_adi": firma_adi,
        "malzeme_gideri": malzeme_gideri,
        "toplam_satis_tutari": toplam_satis_tutari,
        "satis_suresi_gun": satis_suresi_gun,
        "kira_gideri": kira_gideri,
        "uzerine_kar": uzerine_kar,
        "net_kar": net_kar,
        "kar_yuzdesi": kar_yuzdesi,
        "notlar": notlar,
        "ulke": ulke,
        "tarih": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    
    satis_id = firebase_push("satislar", yeni_satis)
    if satis_id:
        print(f"✅ Satış eklendi: {satis_id}")
    return satis_id


def tum_satislari_getir():
    """Tüm satış kayıtlarını getirir"""
    satislar = firebase_get("satislar")
    
    if not satislar:
        return []
    
    satis_listesi = []
    for satis_id, satis_data in satislar.items():
        if satis_data:  # None olmayan kayıtlar
            satis_data['id'] = satis_id
            satis_listesi.append(satis_data)
    
    # Tarihe göre sırala (en yeni en üstte)
    satis_listesi.sort(key=lambda x: x.get('tarih', ''), reverse=True)
    return satis_listesi


def satis_sil(satis_id):
    """Satış kaydını siler"""
    if firebase_delete(f"satislar/{satis_id}"):
        print(f"✅ Satış silindi: {satis_id}")
        return True
    return False


def istatistikleri_getir():
    """Genel istatistikleri hesaplar"""
    satislar = tum_satislari_getir()
    
    if not satislar:
        return {
            'toplam_satis': 0,
            'toplam_kar': 0,
            'ortalama_kar_yuzdesi': 0,
            'toplam_ciro': 0
        }
    
    toplam_satis = len(satislar)
    toplam_kar = sum(s.get('net_kar', 0) for s in satislar)
    toplam_ciro = sum(s.get('toplam_satis_tutari', 0) for s in satislar)
    ortalama_kar_yuzdesi = sum(s.get('kar_yuzdesi', 0) for s in satislar) / toplam_satis if toplam_satis > 0 else 0
    
    return {
        'toplam_satis': toplam_satis,
        'toplam_kar': toplam_kar,
        'ortalama_kar_yuzdesi': ortalama_kar_yuzdesi,
        'toplam_ciro': toplam_ciro
    }


# ==================== FİRMA YÖNETİMİ ====================

def tum_firmalari_getir():
    """Tüm kayıtlı firmaları getirir (benzersiz firma adları)"""
    satislar = tum_satislari_getir()
    
    if not satislar:
        return []
    
    # Firma adlarını ve istatistiklerini topla
    firmalar = {}
    for satis in satislar:
        firma_adi = satis.get('firma_adi', '').strip()
        ulke = satis.get('ulke', 'TR')
        
        if not firma_adi:
            continue
        
        # Firma adını normalize et (büyük harfe çevir karşılaştırma için)
        firma_key = firma_adi.lower()
        
        if firma_key not in firmalar:
            firmalar[firma_key] = {
                'firma_adi': firma_adi,  # Orijinal yazım
                'ulke': ulke,
                'toplam_satis': 0,
                'toplam_ciro': 0,
                'toplam_kar': 0
            }
        
        # İstatistikleri güncelle
        firmalar[firma_key]['toplam_satis'] += 1
        firmalar[firma_key]['toplam_ciro'] += satis.get('toplam_satis_tutari', 0)
        firmalar[firma_key]['toplam_kar'] += satis.get('net_kar', 0)
    
    # Liste olarak döndür ve satış sayısına göre sırala
    firma_listesi = list(firmalar.values())
    firma_listesi.sort(key=lambda x: x['toplam_satis'], reverse=True)
    
    return firma_listesi


def firma_ara(arama_terimi):
    """Firma adına göre arama yapar (autocomplete için)"""
    if not arama_terimi or len(arama_terimi) < 1:
        return []
    
    firmalar = tum_firmalari_getir()
    arama = arama_terimi.lower()
    
    # Eşleşen firmaları bul
    eslesen = []
    for firma in firmalar:
        if arama in firma['firma_adi'].lower():
            eslesen.append(firma)
    
    # En fazla 10 öneri döndür
    return eslesen[:10]


def firma_istatistikleri_getir(firma_adi):
    """Belirli bir firmanın detaylı istatistiklerini getirir"""
    satislar = tum_satislari_getir()
    
    if not satislar:
        return None
    
    firma_key = firma_adi.lower()
    firma_satislari = [s for s in satislar if s.get('firma_adi', '').lower() == firma_key]
    
    if not firma_satislari:
        return None
    
    return {
        'firma_adi': firma_adi,
        'toplam_satis': len(firma_satislari),
        'toplam_ciro': sum(s.get('toplam_satis_tutari', 0) for s in firma_satislari),
        'toplam_kar': sum(s.get('net_kar', 0) for s in firma_satislari),
        'ortalama_kar_yuzdesi': sum(s.get('kar_yuzdesi', 0) for s in firma_satislari) / len(firma_satislari),
        'satislar': firma_satislari
    }


def ulke_firma_sayisi_getir():
    """Her ülkedeki benzersiz firma sayısını döndürür (harita için)"""
    satislar = tum_satislari_getir()
    
    if not satislar:
        return {}
    
    ulke_firmalar = {}  # ulke -> set(firma_adlari)
    ulke_cirolar = {}   # ulke -> toplam_ciro
    
    for satis in satislar:
        ulke = satis.get('ulke', 'TR')
        firma_adi = satis.get('firma_adi', '').strip().lower()
        ciro = satis.get('toplam_satis_tutari', 0)
        
        if not firma_adi:
            continue
        
        if ulke not in ulke_firmalar:
            ulke_firmalar[ulke] = set()
            ulke_cirolar[ulke] = 0
        
        ulke_firmalar[ulke].add(firma_adi)
        ulke_cirolar[ulke] += ciro
    
    # Sonuçları döndür
    sonuc = {}
    for ulke in ulke_firmalar:
        sonuc[ulke] = {
            'firma_sayisi': len(ulke_firmalar[ulke]),
            'toplam_ciro': ulke_cirolar[ulke]
        }
    
    return sonuc
