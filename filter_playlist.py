import urllib.request
import urllib.error
import re

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

# Kamus untuk mengelompokkan kategori
categorized_channels = {
    "Nasional": [],
    "Berita": [],
    "Olah Raga": [],
    "Religi": [],
    "Entertainment & Lainnya": []
}

def detect_category(meta_line):
    meta_lower = meta_line.lower()
    
    # Deteksi berdasarkan group-title atau kata kunci di metadata
    if any(k in meta_lower for k in ["news", "berita", "cnn", "cnbc", "metro"]):
        return "Berita"
    elif any(k in meta_lower for k in ["sport", "sports", "olahraga", "bein", "eurosport", "tvriseven"]):
        return "Olah Raga"
    elif any(k in meta_lower for k in ["religi", "islam", "dakwah", "makkah", "rodja", "quran"]):
        return "Religi"
    elif any(k in meta_lower for k in ["nasional", "general", "rcti", "sCTV", "indosiar", "antv", "trans"]):
        return "Nasional"
    else:
        return "Entertainment & Lainnya"

print("Memeriksa keaktifan link dan menyusun ulang kategori...")

i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith("#EXTINF"):
        meta = line
        url = lines[i+1].strip() if i+1 < len(lines) else ""
        
        # Validasi keaktifan link
        is_active = False
        if url.startswith("http"):
            try:
                req = urllib.request.Request(
                    url, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                )
                with urllib.request.urlopen(req, timeout=3) as res:
                    if res.status < 400:
                        is_active = True
            except Exception:
                is_active = False
        
        if is_active:
            # Tentukan kategori dan perbarui tag group-title agar rapi di aplikasi IPTV
            cat = detect_category(meta)
            
            # Ganti atau tambahkan group-title sesuai kategori yang diinginkan
            if 'group-title="' in meta:
                meta = re.sub(r'group-title="[^"]*"]', f'group-title="{cat}"', meta)
            else:
                meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{cat}"')
                
            categorized_channels[cat].append(f"{meta}\n{url}\n")
            print(f"[AKTIF - {cat}] {url}")
        else:
            print(f"[MATI] {url}")
            
        i += 2
    else:
        i += 1

# Susun kembali urutan kategori ke dalam file final
final_output = ["#EXTM3U\n"]
preferred_order = ["Nasional", "Berita", "Olah Raga", "Religi", "Entertainment & Lainnya"]

for cat in preferred_order:
    if categorized_channels[cat]:
        # Tambahkan komentar pemisah kategori di dalam file M3U (opsional, dibaca rapi oleh sebagian player)
        final_output.append(f"\n# -----------------------------------------\n")
        final_output.append(f"# KATEGORI: {cat}\n")
        final_output.append(f"# -----------------------------------------\n")
        final_output.extend(categorized_channels[cat])

# Simpan hasil akhir
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print("\nPlaylist berhasil disaring dan dikelompokkan ulang!")
