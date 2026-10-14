import urllib.request
import urllib.error
import re

SOURCE_URL = "https://iptv-org.github.io/iptv/countries/id.m3u"
OUTPUT_FILE = "master_active.m3u"

print("Mengunduh playlist...")
try:
    response = urllib.request.urlopen(SOURCE_URL)
    playlist_data = response.read().decode("utf-8")
except Exception as e:
    print(f"Gagal mengunduh playlist: {e}")
    exit(1)

lines = playlist_data.splitlines()

# Kategori standar yang didukung rapi oleh aplikasi IPTV
categorized_channels = {
    "Nasional": [],
    "News": [],
    "Sports": [],
    "Religious": [],
    "Entertainment": []
}

def detect_category(meta_line):
    meta_lower = meta_line.lower()
    
    # Deteksi Religi / Islam / Dakwah
    if any(k in meta_lower for k in ["rodja", "makkah", "religi", "islam", "quran", "surau", "muhammad", "tv 9", "tv9"]):
        return "Religious"
    # Deteksi Olahraga
    elif any(k in meta_lower for k in ["sport", "sports", "olahraga", "bein", "tvriseven", "soccer", "bola"]):
        return "Sports"
    # Deteksi Berita
    elif any(k in meta_lower for k in ["news", "berita", "cnn", "cnbc", "metro"]):
        return "News"
    # Deteksi Nasional / Daerah / Umum
    elif any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans", "kompas", "rtv", "banjar", "banten", "jambi", "tvri", "inews", "gtv", "mentari", "moji"]):
        return "Nasional"
    else:
        return "Entertainment"

# Pemetaan ke nama kategori yang umum di aplikasi
category_mapping = {
    "Nasional": "Nasional",
    "News": "News",
    "Sports": "Sports",
    "Religious": "Religious",
    "Entertainment": "Entertainment"
}

print("Memproses dan menyaring channel...")

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
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=3) as res:
                    if res.status < 400:
                        is_active = True
            except Exception:
                is_active = False
        
        if is_active:
            cat = detect_category(meta)
            target_cat = category_mapping[cat]
            
            # Timpa total group-title agar sesuai kategori baru
            if 'group-title="' in meta:
                meta = re.sub(r'group-title="[^"]*"', f'group-title="{target_cat}"', meta)
            else:
                meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_cat}"')
                
            categorized_channels[cat].append(f"{meta}\n{url}\n")
        
        i += 2
    else:
        i += 1

# Susun hasil akhir ke file M3U
final_output = ["#EXTM3U\n"]
for cat in ["Nasional", "News", "Sports", "Religious", "Entertainment"]:
    if categorized_channels[cat]:
        final_output.extend(categorized_channels[cat])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print("Penyortiran kategori selesai!")
