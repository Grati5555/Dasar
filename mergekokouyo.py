import urllib.request
import re

# URL Google Drive sumber mentah
SOURCE_URL = "https://drive.google.com/uc?id=11SCMxGrXt4ECr1N0PXqtu26zSNYkKEYm"

# Kategori yang diminta: Liga Champions, TV Nasional, Olahraga, dan Live Olahraga
TARGET_GROUPS = [
    "CHAMPIONS LEAGUE", 
    "LOKAL", 
    "SPORTS", 
    "OLAHRAGA", 
    "LIVE FEED SPORT", 
    "UEFA NATIONS LEAGUE",
    "BRI LIGA 1",
    "PREMIER LEAGUE"
]

def clean_line(line):
    """Mengganti kata Koko / Kokouyo menjadi Test di seluruh baris EXTINF"""
    cleaned = line
    # Mengganti berbagai variasi penulisan Koko / Kokouyo menjadi Test
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
            matched = False
            upper_line = line.upper()
            for group in TARGET_GROUPS:
                if group in upper_line:
                    matched = True
                    break
            
            if matched:
                # Bersihkan baris EXTINF dari kata Koko/Kokouyo (termasuk group-title)
                cleaned_line = clean_line(line)
                
                filtered_lines.append(cleaned_line)
                i += 1
                while i < len(lines) and (lines[i].startswith("#") and not lines[i].startswith("#EXTINF")):
                    filtered_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    filtered_lines.append(lines[i])
        i += 1

    # Disimpan dengan nama file MasterKokoUyo.m3u
    output_filename = "MasterKokoUyo.m3u"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    print(f"Playlist berhasil dibersihkan & diperbarui! Disimpan ke {output_filename}")

if __name__ == "__main__":
    generate_playlist()
