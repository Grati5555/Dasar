import urllib.request
import re

# URL Google Drive sumber mentah
SOURCE_URL = "https://drive.google.com/uc?id=11SCMxGrXt4ECr1N0PXqtu26zSNYkKEYm"

# Daftar target kategori yang BOLEH masuk ke playlist (VOD dan kategori lain otomatis dibuang)
ALLOWED_GROUPS = [
    "CHAMPIONS LEAGUE",
    "LOKAL",
    "SPORTS",
    "OLAHRAGA",
    "LIVE FEED SPORT",
    "UEFA NATIONS LEAGUE",
    "BRI LIGA 1",
    "PREMIER LEAGUE",
    "KOKOUYO",        # Agar kategori pilihan KokoUyo ikut tersaring
    "PILIHAN KOKOUYO" # Mengantisipasi variasi nama grup
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
    filtered_lines = ["#EXTM3U"]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("#EXTINF"):
            # Cek apakah baris ini masuk ke dalam kategori yang diizinkan
            matched = False
            upper_line = line.upper()
            for group in ALLOWED_GROUPS:
                if group in upper_line:
                    matched = True
                    break
            
            if matched:
                # Bersihkan baris EXTINF dari kata koko/kokouyo (termasuk pada group-title)
                cleaned_line = clean_text(line)
                
                filtered_lines.append(cleaned_line)
                i += 1
                # Ambil baris tambahan pendukung seperti #EXTVLCOPT / #KODIPROP di bawahnya
                while i < len(lines) and (lines[i].startswith("#") and not lines[i].startswith("#EXTINF")):
                    filtered_lines.append(clean_text(lines[i]))
                    i += 1
                # Ambil URL stream
                if i < len(lines):
                    filtered_lines.append(lines[i])
        i += 1

    # Disimpan dengan nama file MasterKokoUyo.m3u
    output_filename = "MasterKokoUyo.m3u"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    print(f"Playlist berhasil dibersihkan dan difilter! Disimpan ke {output_filename}")

if __name__ == "__main__":
    generate_playlist()
