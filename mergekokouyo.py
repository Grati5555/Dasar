import urllib.request
import re
from datetime import datetime

# URL Google Drive sumber mentah
SOURCE_URL = "https://drive.google.com/uc?id=11SCMxGrXt4ECr1N0PXqtu26zSNYkKEYm"

# Daftar kategori dasar yang tetap diizinkan
ALLOWED_GROUPS = [
    "CHAMPIONS LEAGUE",
    "LOKAL",
    "SPORTS",
    "OLAHRAGA",
    "LIVE FEED SPORT",
    "UEFA NATIONS LEAGUE",
    "BRI LIGA 1",
    "PREMIER LEAGUE",
    "KOKOUYO",
    "PILIHAN KOKOUYO"
]

def get_dynamic_live_group():
    """Menghasilkan string tanggal dinamis sesuai format di file (Contoh: LIVE 14-OKT-26)"""
    now = datetime.now()
    # Mengambil format tanggal, bulan dalam 3 huruf kapital (OKT, NOV, dll), dan 2 digit tahun
    months_id = {
        1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MEI", 6: "JUN",
        7: "JUL", 8: "AGU", 9: "SEP", 10: "OKT", 11: "NOV", 12: "DES"
    }
    day = now.strftime("%d")
    month = months_id[now.month]
    year = now.strftime("%y")
    
    # Menghasilkan contoh: "LIVE 14-OKT-26"
    return f"LIVE {day}-{month}-{year}"

def clean_text(text):
    """Mengganti semua kata koko / kokouyo menjadi Test secara case-insensitive"""
    cleaned = text
    patterns = [r"kokouyo", r"koko"]
    for pattern in patterns:
        cleaned = re.sub(pattern, "Test", cleaned, flags=re.IGNORECASE)
    return cleaned

def generate_playlist():
    print("Mengambil data playlist dari sumber...")
    req = urllib.request.Request(
        SOURCE_URL, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    # Ambil kategori live hari ini secara otomatis
    today_live_group = get_dynamic_live_group()
    print(f"Kategori Live Hari Ini yang Dicari: {today_live_group}")
    
    # Gabungkan target group dasar dengan kategori live hari ini
    current_allowed_groups = ALLOWED_GROUPS + [today_live_group]
    
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')

    lines = content.splitlines()
    filtered_lines = ["#EXTM3U"]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("#EXTINF"):
            matched = False
            upper_line = line.upper()
            for group in current_allowed_groups:
                if group in upper_line:
                    matched = True
                    break
            
            if matched:
                cleaned_line = clean_text(line)
                
                # Jika baris ini adalah bagian dari kategori LIVE harian, 
                # kita juga bisa merapikan teks tanggalnya jika diperlukan, 
                # atau biarkan tampil sesuai sumber aslinya.
                filtered_lines.append(cleaned_line)
                i += 1
                while i < len(lines) and (lines[i].startswith("#") and not lines[i].startswith("#EXTINF")):
                    filtered_lines.append(clean_text(lines[i]))
                    i += 1
                if i < len(lines):
                    filtered_lines.append(lines[i])
        i += 1

    # Disimpan dengan nama file MasterKokoUyo.m3u
    output_filename = "MasterKokoUyo.m3u"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    print(f"Playlist berhasil diperbarui dengan kategori {today_live_group}!")

if __name__ == "__main__":
    generate_playlist()
