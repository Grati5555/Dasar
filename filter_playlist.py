import urllib.request
import urllib.error
import re

# Daftar sumber playlist yang benar (menggunakan sports.m3u)
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/countries/id.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u"
]

OUTPUT_FILE = "master_active.m3u"

categorized_channels = {
    "Nasional": [],
    "News": [],
    "Sports": [],
    "Religious": [],
    "Entertainment": []
}

def detect_category(meta_line, source_url):
    meta_lower = meta_line.lower()
    
    # Jika sumbernya dari playlist sports.m3u, langsung masukkan ke Sports
    if "categories/sports.m3u" in source_url:
        return "Sports"
        
    if any(k in meta_lower for k in ["rodja", "makkah", "religi", "islam", "quran", "surau", "muhammad", "tv 9", "tv9", "religious"]):
        return "Religious"
    elif any(k in meta_lower for k in ["sport", "sports", "olahraga", "bein", "tvriseven", "soccer", "bola", "espn", "eurosport", "fox sport", "tnt sports"]):
        return "Sports"
    elif any(k in meta_lower for k in ["news", "berita", "cnn", "cnbc", "metro", "al jazeera", "bbc news"]):
        return "News"
    elif any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans", "kompas", "rtv", "banjar", "banten", "jambi", "tvri", "inews", "gtv", "mentari", "moji"]):
        return "Nasional"
    else:
        return "Entertainment"

print("Mulai mengunduh dan memproses playlist...")

for source_url in SOURCE_URLS:
    print(f"Mengakses sumber: {source_url}")
    try:
        req_source = urllib.request.Request(
            source_url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req_source, timeout=10) as response:
            playlist_data = response.read().decode("utf-8")
    except Exception as e:
        print(f"Gagal mengunduh {source_url}: {e}")
        continue

    lines = playlist_data.splitlines()
    print(f"Total baris terbaca dari sumber: {len(lines)}")

    i = 0
    added_count = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            meta = line
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            
            # Validasi link (untuk kategori sports global, kita longgarkan pengecekannya agar tidak mudah gagal)
            is_active = False
            if url.startswith("http"):
                if "categories/sports.m3u" in source_url:
                    # Langsung anggap aktif untuk list olahraga global yang sering memblokir automated HTTP ping
                    is_active = True 
                else:
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
                cat = detect_category(meta, source_url)
                
                # Format ulang group-title
                if 'group-title="' in meta:
                    meta = re.sub(r'group-title="[^"]*"', f'group-title="{cat}"', meta)
                else:
                    meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{cat}"')
                    
                channel_entry = f"{meta}\n{url}\n"
                if channel_entry not in categorized_channels[cat]:
                    categorized_channels[cat].append(channel_entry)
                    added_count += 1
            
            i += 2
        else:
            i += 1
    print(f"Berhasil menambahkan {added_count} channel aktif dari sumber ini.")

# Simpan hasil akhir
final_output = ["#EXTM3U\n"]
total_all = 0
for cat in ["Nasional", "News", "Sports", "Religious", "Entertainment"]:
    if categorized_channels[cat]:
        final_output.extend(categorized_channels[cat])
        print(f"Kategori {cat}: {len(categorized_channels[cat])} channel")
        total_all += len(categorized_channels[cat])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print(f"\nSelesai! Total keseluruhan channel aktif: {total_all}")
