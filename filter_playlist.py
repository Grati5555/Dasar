import urllib.request
import urllib.error
import re

# Tambahkan sumber negara Saudi Arabia (sa.m3u) untuk Makkah & Madinah Live
SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/countries/id.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/countries/sa.m3u"  # Sumber khusus Saudi Arabia
]

OUTPUT_FILE = "master_active.m3u"

categorized_channels = {
    "Nasional": [],
    "News": [],
    "Religious": [],
    "Sports - Indonesia": [],
    "Sports - UK & Premier League": [],
    "Sports - Europe & Champions": [],
    "Sports - Global & Other": [],
    "Entertainment": []
}

def detect_category(meta_line, source_url):
    meta_lower = meta_line.lower()
    
    # Jika sumber berasal dari playlist Saudi Arabia (sa.m3u), saring khusus Makkah/Madinah/Quran/Sunnah
    if "countries/sa.m3u" in source_url:
        if any(k in meta_lower for k in ["quran", "sunnah", "makkah", "madinah", "saudi quran", "saudi sunnah"]):
            return "Religious"
        else:
            return None # Abaikan channel Saudi lain yang tidak diperlukan agar list tetap bersih
            
    if "countries/id.m3u" in source_url:
        if any(k in meta_lower for k in ["sport", "sports", "olahraga", "bein", "tvriseven", "soccer", "bola"]):
            return "Sports - Indonesia"
        elif any(k in meta_lower for k in ["rodja", "makkah", "madinah", "religi", "islam", "quran", "sunnah", "surau", "muhammad", "tv 9", "tv9", "religious"]):
            return "Religious"
        elif any(k in meta_lower for k in ["news", "berita", "cnn", "cnbc", "metro"]):
            return "News"
        elif any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans", "kompas", "rtv", "banjar", "banten", "jambi", "tvri", "inews", "gtv", "mentari", "moji"]):
            return "Nasional"
        else:
            return "Entertainment"
            
    if "categories/sports.m3u" in source_url:
        if any(k in meta_lower for k in ["uk", "england", "premier league", "sky sports", "tnt sports", "bbc sport"]):
            return "Sports - UK & Premier League"
        elif any(k in meta_lower for k in ["champions", "europe", "laliga", "serie a", "bundesliga", "espn", "eurosport"]):
            return "Sports - Europe & Champions"
        elif any(k in meta_lower for k in ["id", "indonesia"]):
            return "Sports - Indonesia"
        else:
            return "Sports - Global & Other"
            
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

    i = 0
    added_count = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            meta = line
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            
            # Deteksi kategori terlebih dahulu
            cat = detect_category(meta, source_url)
            
            # Jika dari sa.m3u dan bukan Makkah/Madinah (cat bernilai None), lewati
            if cat is None:
                i += 2
                continue
                
            is_active = False
            if url.startswith("http"):
                if "categories/sports.m3u" in source_url or "countries/sa.m3u" in source_url:
                    is_active = True  # Bypass ping untuk sumber global & saudi agar langsung masuk
                else:
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=3) as res:
                            if res.status < 400:
                                is_active = True
                    except Exception:
                        is_active = False
            
            if is_active:
                # Format ulang group-title agar rapi
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
    print(f"Berhasil menambahkan {added_count} channel dari sumber ini.")

# Susun urutan kategori akhir di file M3U
final_output = ["#EXTM3U\n"]
category_order = [
    "Nasional", 
    "News", 
    "Religious", 
    "Sports - Indonesia", 
    "Sports - UK & Premier League", 
    "Sports - Europe & Champions", 
    "Sports - Global & Other", 
    "Entertainment"
]

total_all = 0
for cat in category_order:
    if categorized_channels[cat]:
        final_output.extend(categorized_channels[cat])
        print(f"Kategori [{cat}]: {len(categorized_channels[cat])} channel")
        total_all += len(categorized_channels[cat])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print(f"\nSelesai! Total keseluruhan channel aktif: {total_all}")
