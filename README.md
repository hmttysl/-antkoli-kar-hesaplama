# 📦 Ant Koli - Kar/Zarar Hesaplama Sistemi

Modern masaüstü uygulaması ile kolayca satış kar/zarar hesaplaması yapın.

## 🚀 Özellikler

- ✅ Detaylı kar/zarar hesaplama (KDV dahil/hariç)
- ✅ Aylık gider takibi (kira, personel, elektrik, vb.)
- ✅ Firma bazlı satış takibi
- ✅ Ülke bazlı satış haritası
- ✅ Firebase ile gerçek zamanlı veri senkronizasyonu
- ✅ Yıllık/aylık istatistikler ve grafikler
- ✅ Otomatik güncelleme sistemi

## 📁 Proje Yapısı

```
├── main.py           # Ana uygulama (CustomTkinter GUI)
├── database.py       # Firebase Realtime Database işlemleri
├── updater.py        # Otomatik güncelleme modülü
├── map_viewer.py     # Dünya haritası görüntüleyici
├── requirements.txt  # Python bağımlılıkları
├── logo.png          # Uygulama logosu
└── web-dashboard/    # React web harita dashboard'u
```

## ⚙️ Kurulum

### 1. Python Bağımlılıklarını Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Firebase Ayarları

`database.py` dosyasındaki Firebase URL'sini kendi projenizle değiştirin:

```python
FIREBASE_DATABASE_URL = "https://YOUR-PROJECT-ID.firebasedatabase.app"
```

### 3. Firebase Kuralları

Firebase Console'da Realtime Database > Rules:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

### 4. Uygulamayı Çalıştırın

```bash
python main.py
```

## 🌍 Web Harita Dashboard

Dünya haritası için web dashboard'u çalıştırmak için:

```bash
cd web-dashboard/Fintech\ World\ Map\ Dashboard
npm install
npm run build
```

## 📊 Ekran Görüntüleri

- Ana ekran: Genel istatistikler ve hızlı erişim
- Yeni Satış: Detaylı kar hesaplama formu
- Firma Listesi: Firma bazlı satış takibi
- Dünya Haritası: Ülke bazlı satış görselleştirmesi

## 🔧 Teknolojiler

- **Python** + CustomTkinter (Masaüstü GUI)
- **Firebase Realtime Database** (Bulut veritabanı)
- **React** + TypeScript (Web harita dashboard)
- **Matplotlib** (Grafikler)

## 📝 Lisans

Bu proje özel kullanım içindir.

---

© 2024-2026 Ant Koli Kar/Zarar Hesaplama Sistemi
