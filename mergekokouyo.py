import urllib.request
import re

# URL Google Drive sumber mentah
SOURCE_URL = "https://drive.google.com/uc?id=11SCMxGrXt4ECr1N0PXqtu26zSNYkKEYm"

# Daftar kategori utama yang diizinkan (KOKOUYO dihapus agar tidak meloloskan "PLAYLIST KOKOUYO")
ALLOWED_GROUPS = [
    "CHAMPIONS LEAGUE",
    "LOKAL",
    "SPORTS",
    "OLAHRAGA",
    "LIVE FEED SPORT",
    "UEFA NATIONS LEAGUE",
    "BRI LIGA 1",
    "PREMIER LEAGUE"
]

# Daftar kategori atau teks yang WAJIB DIBUANG / DIKELUARKAN total
EXCLUDED_GROUPS = [
    "PLAYLIST KOKOUYO",
    "KOKOUYO"
]

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
    
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')

    lines = content.splitlines()
    
    # Scan file sumber untuk mendeteksi semua kategori "LIVE [Tanggal]" yang aktif/ada
    active_live_dates = set()
    date_pattern = re.compile(r'group-title="([^"]*LIVE\s+\d{2}-[A-Z]{3}-\d{2}[^"]*)"', re.IGNORECASE)
    
    for line in lines:
        if line.startswith("#EXTINF"):
            match = date_pattern.search(line)
            if match:
                group_name = match.group(1).upper()
                # Pastikan tanggal live tidak mengandung kata yang diblokir
                if not any(ex in group_name for ex in EXCLUDED_GROUPS):
                    active_live_dates.add(group_name)

    current_allowed_groups = ALLOWED_GROUPS + list(active_live_dates)

    filtered_lines = ["#EXTM3U"]
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("#EXTINF"):
            upper_line = line.upper()
            
            # 1. Cek apakah baris ini masuk dalam daftar yang HARUS DIKELUARKAN (Blokir)
            is_excluded = False
            for ex in EXCLUDED_GROUPS:
                if ex in upper_line:
                    is_excluded = True
                    break
            
            if is_excluded:
                # Lewati baris EXTINF ini beserta baris opsi/stream di bawahnya
                i += 1
                while i < len(lines) and (lines[i].startswith("#") and not lines[i].startswith("#EXTINF")):
                    i += 1
                continue

            # 2. Cek apakah masuk dalam kategori yang DIINGINKAN
            matched = False
            for group in current_allowed_groups:
                if group in upper_line:
                    matched = True
                    break
            
            if matched:
                cleaned_line = clean_text(line)
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
    print(f"Playlist berhasil diperbarui! Kategori PLAYLIST KOKOUYO berhasil dibuang.")

if __name__ == "__main__":
    generate_playlist()
