import urllib.request
import urllib.error
import re

# 1. Ambil playlist publik (contoh: channel Indonesia dari IPTV-org)
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/id.m3u"
OUTPUT_FILE = "master_active.m3u"

print("Mengunduh playlist publik...")
try:
    response = urllib.request.urlopen(SOURCE_URL)
    playlist_data = response.read().decode("utf-8")
except Exception as e:
    print(f"Gagal mengunduh playlist: {e}")
    exit(1)

lines = playlist_data.splitlines()
active_channels = []

print("Memeriksa status keaktifan link (ini mungkin butuh beberapa saat)...")

i = 0
while i < len(lines):
    line = lines[i].strip()
    
    # Cek jika baris adalah metadata #EXTINF
    if line.startswith("#EXTINF"):
        meta = line
        url = lines[i+1].strip() if i+1 < len(lines) else ""
        
        # Validasi sederhana apakah URL bisa diakses
        is_active = False
        if url.startswith("http"):
            try:
                # Menggunakan request dengan timeout agar tidak macet terlalu lama
                req = urllib.request.Request(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                # Cukup gunakan method pembuka kecil atau head
                with urllib.request.urlopen(req, timeout=3) as res:
                    if res.status < 400:
                        is_active = True
            except Exception:
                is_active = False
        
        # Jika aktif, masukkan ke daftar
        if is_active:
            active_channels.append(f"{meta}\n{url}\n")
            print(f"[AKTIF] {url}")
        else:
            print(f"[MATI/DILEWATI] {url}")
            
        i += 2
    else:
        i += 1

# 2. Simpan hasil saringan ke file master baru
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n" + "".join(active_channels))

print(f"\nSelesai! Total channel aktif yang disimpan: {len(active_channels)}")
