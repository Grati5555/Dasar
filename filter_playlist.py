import urllib.request
import urllib.error
import re

SOURCE_URLS = [
    "https://iptv-org.github.io/iptv/countries/id.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/countries/sa.m3u"
]

OUTPUT_FILE = "master_active.m3u"

categorized_channels = {
    "1. Nasional (Free-to-Air Umum)": [],
    "2. Berita (News)": [],
    "3. Religiuos (Islamic & General)": [],
    "4. Sport - Indonesia": [],
    "5. Sport - Premier League & UK": [],
    "6. Sport - Champions & European Leagues": [],
    "7. Sport - Global & Other": [],
    "8. Hiburan, Film & Musik (Entertainment & Movies)": [],
    "9. Dokumenter, Sains & Gaya Hidup (Documentary & Lifestyle)": [],
    "10. Anak-anak (Kids)": [],
    "11. Lokal & Daerah (Kalimantan & Nusantara)": []
}

def detect_category(meta_line, source_url):
    meta_lower = meta_line.lower()
    
    if "countries/sa.m3u" in source_url:
        if any(k in meta_lower for k in ["quran", "sunnah", "makkah", "madinah", "saudi quran", "saudi sunnah"]):
            return "3. Religiuos (Islamic & General)"
        return None

    if "countries/id.m3u" in source_url:
        # Ditambahkan kata kunci "wafa" dan "tarim" di sini
        if any(k in meta_lower for k in ["wafa", "tarim", "rodja", "makkah", "madinah", "religi", "islam", "quran", "sunnah", "surau", "muhammad", "tv 9", "tv9", "aswaja", "al bahjah", "insan", "tvmu", "madaniah", "ahsan", "mta", "niaga"]):
            return "3. Religiuos (Islamic & General)"
        elif any(k in meta_lower for k in ["metro", "tvone", "tv one", "cnn", "cnbc", "kompas", "beritasatu", "idtv"]):
            return "2. Berita (News)"
        elif any(k in meta_lower for k in ["spotv", "bein", "soccer", "mnc sports", "champions tv", "vidio", "nba", "sport", "olahraga", "bola"]):
            return "4. Sport - Indonesia"
        elif any(k in meta_lower for k in ["banjar", "duta", "kalsel", "kaltim", "kalteng", "kalbar", "jaktv", "jak tv", "atv", "malang", "tvri kalimantan", "tvri kalsel"]):
            return "11. Lokal & Daerah (Kalimantan & Nusantara)"
        elif any(k in meta_lower for k in ["cartoon", "nickelodeon", "disney", "dreamworks", "cbeebies", "kids"]):
            return "10. Anak-anak (Kids)"
        elif any(k in meta_lower for k in ["national geographic", "discovery", "animal planet", "history", "bbc earth", "food", "travel"]):
            return "9. Dokumenter, Sains & Gaya Hidup (Documentary & Lifestyle)"
        elif any(k in meta_lower for k in ["bioskop", "zee", "drama", "hallyu", "prambors", "dewa", "movie", "entertainment"]):
            return "8. Hiburan, Film & Musik (Entertainment & Movies)"
        elif any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans tv", "trans7", "gtv", "mnc", "rtv", "net", "mdtv", "mentari", "btv"]):
            return "1. Nasional (Free-to-Air Umum)"
        else:
            return "1. Nasional (Free-to-Air Umum)"

    if "categories/sports.m3u" in source_url:
        if any(k in meta_lower for k in ["uk", "england", "premier league", "sky sports", "tnt sports", "bbc sport"]):
            return "5. Sport - Premier League & UK"
        elif any(k in meta_lower for k in ["champions", "europe", "laliga", "serie a", "bundesliga", "espn", "eurosport"]):
            return "6. Sport - Champions & European Leagues"
        elif any(k in meta_lower for k in ["id", "indonesia"]):
            return "4. Sport - Indonesia"
        else:
            return "7. Sport - Global & Other"
            
    return None

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
            
            cat = detect_category(meta, source_url)
            if cat is None:
                i += 2
                continue
                
            is_active = False
            if url.startswith("http"):
                # Jika nama channel mengandung kata "wafa" atau "tarim", langsung bypass (anggap aktif) agar tidak terbuang karena timeout
                if "categories/sports.m3u" in source_url or "countries/sa.m3u" in source_url or "wafa" in meta.lower() or "tarim" in meta.lower():
                    is_active = True  
                else:
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=3) as res:
                            if res.status < 400:
                                is_active = True
                    except Exception:
                        is_active = False
            
            if is_active:
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

final_output = ["#EXTM3U\n"]
total_all = 0
for cat in categorized_channels.keys():
    if categorized_channels[cat]:
        final_output.extend(categorized_channels[cat])
        print(f"Kategori [{cat}]: {len(categorized_channels[cat])} channel")
        total_all += len(categorized_channels[cat])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print(f"\nSelesai! Total keseluruhan channel aktif: {total_all}")
