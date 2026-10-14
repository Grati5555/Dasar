import urllib.request
import urllib.error
import re

SOURCE_URLS = [
    "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u",
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
    
    # 1. Khusus sumber Indihome: Ambil kategori Nasional
    if "indihometv.m3u" in source_url.lower():
        if any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans tv", "trans7", "gtv", "mnc", "rtv", "net", "mdtv", "mentari", "btv", "inews", "tvri"]):
            return "1. Nasional (Free-to-Air Umum)"
        else:
            return None  # Buang non-nasional dari Indihome

    # 2. Sumber Saudi Arabia khusus Religi
    if "countries/sa.m3u" in source_url:
        if any(k in meta_lower for k in ["quran", "sunnah", "makkah", "madinah", "saudi quran", "saudi sunnah"]):
            return "3. Religiuos (Islamic & General)"
        return None

    # 3. Sumber lainnya (iptv-org)
    if any(k in meta_lower for k in ["rodja", "makkah", "madinah", "religi", "islam", "quran", "sunnah", "surau", "muhammad", "tv 9", "tv9", "aswaja", "al bahjah", "insan", "tvmu", "madaniah", "ahsan", "mta", "niaga"]):
        return "3. Religiuos (Islamic & General)"
    elif any(k in meta_lower for k in ["metro tv", "tvone", "tv one", "cnn indonesia", "cnbc indonesia", "kompas tv", "beritasatu", "idtv"]):
        return "2. Berita (News)"
    elif any(k in meta_lower for k in ["uk", "england", "premier league", "sky sports", "tnt sports", "bbc sport"]) or "categories/sports.m3u" in source_url and any(k in meta_lower for k in ["uk", "sky", "tnt"]):
        if any(k in meta_lower for k in ["champions", "laliga", "serie a", "bundesliga", "espn", "eurosport"]):
            return "6. Sport - Champions & European Leagues"
        return "5. Sport - Premier League & UK"
    elif any(k in meta_lower for k in ["champions", "europe", "laliga", "serie a", "bundesliga", "espn", "eurosport"]):
        return "6. Sport - Champions & European Leagues"
    elif any(k in meta_lower for k in ["spotv", "bein", "soccer", "mnc sports", "champions tv", "vidio", "nba", "sport", "olahraga", "bola"]):
        return "4. Sport - Indonesia"
    elif "categories/sports.m3u" in source_url:
        return "7. Sport - Global & Other"
    elif any(k in meta_lower for k in ["tvri aceh", "tvri bali", "tvri bengkulu", "tvri jambi", "tvri lampung", "tvri papua", "tvri riau", "tvri sumatera", "tvri sulawesi", "tvri kalimantan", "tvri jawa", "tvri ntt", "tvri ntb", "tvri maluku", "tvri gorontalo", "banjar", "duta", "kalsel", "kaltim", "kalteng", "kalbar", "jaktv", "jak tv", "atv", "malang", "jawa pos", "balikpapan", "bandung", "banten", "batam", "jtv", "kilisuci", "mbg", "padang", "pontv", "rri net", "stv", "tabalong"]):
        return "11. Lokal & Daerah (Kalimantan & Nusantara)"
    elif any(k in meta_lower for k in ["cartoon", "nickelodeon", "disney", "dreamworks", "cbeebies", "kids"]):
        return "10. Anak-anak (Kids)"
    elif any(k in meta_lower for k in ["national geographic", "discovery", "animal planet", "history", "bbc earth", "food", "travel"]):
        return "9. Dokumenter, Sains & Gaya Hidup (Documentary & Lifestyle)"
    elif any(k in meta_lower for k in ["bioskop", "zee", "drama", "hallyu", "prambors", "dewa", "movie", "entertainment", "big movies"]):
        return "8. Hiburan, Film & Musik (Entertainment & Movies)"
    elif any(k in meta_lower for k in ["rcti", "sctv", "indosiar", "antv", "trans tv", "trans7", "gtv", "mnc", "rtv", "net", "mdtv", "mentari", "btv", "inews", "tvri"]):
        return "1. Nasional (Free-to-Air Umum)"
    else:
        return None

print("Memperbarui dan menyaring playlist...")

for source_url in SOURCE_URLS:
    print(f"Mengakses sumber: {source_url}")
    try:
        req_source = urllib.request.Request(
            source_url, 
            headers={"User-Agent": "Mozilla/5.0"}
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
            
            # Kumpulkan baris properti tambahan (#KODIPROP, #EXTVLCOPT, dll.) dan cari baris URL aslinya (http...)
            block_lines = [meta]
            j = i + 1
            actual_url = ""
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith("#"):
                    block_lines.append(next_line)
                    j += 1
                elif next_line.startswith("http"):
                    actual_url = next_line
                    j += 1
                    break
                else:
                    j += 1
                    break

            cat = detect_category(meta, source_url)
            if cat is not None and actual_url:
                # Format ulang group-title
                if 'group-title="' in meta:
                    meta = re.sub(r'group-title="[^"]*"', f'group-title="{cat}"', meta)
                else:
                    meta = meta.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{cat}"')
                
                block_lines[0] = meta
                channel_block = "\n".join(block_lines) + f"\n{actual_url}\n"
                
                if channel_block not in categorized_channels[cat]:
                    categorized_channels[cat].append(channel_block)
                    added_count += 1
            
            i = j
        else:
            i += 1
    print(f"Berhasil menambahkan {added_count} channel.")

final_output = ["#EXTM3U\n"]
for cat in categorized_channels.keys():
    if categorized_channels[cat]:
        final_output.extend(categorized_channels[cat])

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(final_output)

print("Selesai! Playlist siap digunakan.")
