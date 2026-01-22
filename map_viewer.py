# map_viewer.py - Satış Haritası Görüntüleyici (Uygulama İçi Pencere)
import os
import sys
import http.server
import socketserver
import threading
import webview  # pywebview

def get_resource_path(relative_path):
    """PyInstaller ile paketlenmiş dosya yolunu al"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def find_free_port():
    """Boş port bul"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Sessiz HTTP handler - log basmaz"""
    def log_message(self, format, *args):
        pass  # Logları sustur

def start_server(directory, port):
    """HTTP sunucusu başlat"""
    os.chdir(directory)
    with socketserver.TCPServer(("", port), QuietHTTPHandler) as httpd:
        httpd.serve_forever()

def main():
    # Web dashboard yolunu bul
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dashboard_path = os.path.join(base_dir, "web-dashboard", "Fintech World Map Dashboard", "dist")
    
    if not os.path.exists(dashboard_path):
        print(f"Dashboard bulunamadi: {dashboard_path}")
        # Fallback: Basit bir hata penceresi göster
        try:
            webview.create_window(
                "Hata",
                html="<html><body style='font-family:Arial;text-align:center;padding:50px;'><h2>Harita dosyaları bulunamadı!</h2><p>web-dashboard klasörünü kontrol edin.</p></body></html>",
                width=400,
                height=200
            )
            webview.start()
        except:
            pass
        return
    
    # Sunucuyu başlat
    port = find_free_port()
    server_thread = threading.Thread(target=start_server, args=(dashboard_path, port), daemon=True)
    server_thread.start()
    
    # Uygulama içi pencerede aç (pywebview)
    url = f"http://localhost:{port}/index.html"
    print(f"Harita aciliyor: {url}")
    
    # Pencere oluştur
    window = webview.create_window(
        "🌍 Dünya Satış Haritası - Ant Koli",
        url,
        width=1200,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    
    # Pencereyi başlat
    webview.start()

if __name__ == "__main__":
    main()
