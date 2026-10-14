import urllib.request
import urllib.error
import re

# Daftar sumber playlist yang ingin digabungkan
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/countries/id.m3u",       # Sumber channel Indonesia
    "https://iptv-org.github.io/iptv/categories/sport.m3u"   # Sumber channel Sports Global
]

OUTPUT_FILE = "master_active.m3u"

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
    if any(k in meta_lower for k in ["rodja", "makkah", "religi", "islam", "quran", "surau", "muhammad", "tv 9", "tv9", "religious"]):
        return "Religious"
    # Deteksi Olahraga (termasuk dari playlist sport global)
    elif any(k in meta_lower for k in ["sport", "sports", "olahraga", "bein", "tvriseven", "soccer", "bola", "espn", "eurosport", "fox sport", "tnt sports"]):
        return "Sports"
    # Deteksi Berita
    elif any(k in meta_lower for k in ["news", "berita", "cnn", "cnbc", "metro", "al jazeera", "bbc news"]):
        return "News"
    # Deteksi Nasional / Daerah / Umum
    elif any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans", "kompas", "rtv", "banjar", "banten", "jambi", "tvri", "inews", "gtv", "mentari", "moji"]):
        return "Nasional"
    else:
        return "Entertainment"

category_mapping = {
    "Nasional": "Nasional",
    "News": "News",
    "Sports": "Sports",
    "Religious": "Religious",
    "Entertainment": "Entertainment"
}

# Proses setiap sumber playlist
for source_url in SOURCE_URLS:
    print(f"Mengunduh dari sumber: {source_url} ...")
    try:
        response = urllib.request.urlopen(source_url)
        playlist_data = response.read().decode("utf-8")
    except Exception as e:
        print(f"Gagal mengunduh {source_url}: {e}")
        continue

    lines = playlist_data.splitlines()

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
                
                # Jika link berasal langsung dari playlist sport, pastikan masuk kategori Sports
                if "categories/sport.m3u" in source_url:
                    cat = "Sports"

                target_cat = category_mapping[cat]
                
                # Timpa group-title agar rapi
                if 'group-title="' in meta:
                    meta = re.sub(r'group-title="[^"]*"', f'group-title="{target_cat}"', meta)
                else:
                    meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{target_cat}"')
                    
                channel_entry = f"{meta}\n{url}\n"
                if channel_entry not in categorized_channels[cat]:  # Hindari duplikat
                    categorized_channels[cat].append(channel_entry)
            
            i += 2
        else:
            i += 1

# Susun hasil akhir ke file M3U gabungan
final_output = ["#EXTM3U\n"]
for cat in ["Nasional", "News", "Sports", "Religious", "Entertainment"]:
    if categorized_channels[cat]:
        final_output.extend(categorized_channels[cat])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print("Penggabungan dan penyortiran playlist selesai!")
