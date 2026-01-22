# map_viewer.py - Satış Haritası Görüntüleyici
import webbrowser
import os
import sys
import http.server
import socketserver
import threading

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

def start_server(directory, port):
    """HTTP sunucusu başlat"""
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def main():
    # Web dashboard yolunu bul
    if hasattr(sys, '_MEIPASS'):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dashboard_path = os.path.join(base_dir, "web-dashboard", "Fintech World Map Dashboard", "dist")
    
    if not os.path.exists(dashboard_path):
        print(f"Dashboard bulunamadı: {dashboard_path}")
        input("Çıkmak için Enter'a basın...")
        return
    
    # Sunucuyu başlat
    port = find_free_port()
    server_thread = threading.Thread(target=start_server, args=(dashboard_path, port), daemon=True)
    server_thread.start()
    
    # Tarayıcıda aç
    url = f"http://localhost:{port}/index.html"
    print(f"Harita açılıyor: {url}")
    webbrowser.open(url)
    
    # Bekle
    input("Haritayı kapatmak için Enter'a basın...")

if __name__ == "__main__":
    main()

