import os
import re
import urllib.request

SOURCES_FILE = "sources.txt"
OUTPUT_DIR = "Sumber Indo"
CATEGORY_DIR = "Kategori Indo"  # Direktori baru untuk output per kategori
SELECT_FILE = "select_ch.txt"
CUSTOM_PLAYLIST = "PlaylistINDOpilihan.m3u"

def parse_and_split_m3u():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    if not os.path.exists(CATEGORY_DIR):
        os.makedirs(CATEGORY_DIR)

    if not os.path.exists(SOURCES_FILE):
        print(f"File {SOURCES_FILE} tidak ditemukan!")
        return

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        source_urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not source_urls:
        print("Tidak ada link sumber yang ditemukan di sources.txt")
        return

    channels = {}
    categories = {}  # Dictionary untuk mengelompokkan entri berdasarkan kategori

    for url_idx, source_url in enumerate(source_urls, 1):
        print(f"Mengambil data dari Sumber ke-{url_idx}: {source_url}")
        req = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
        except Exception as e:
            print(f"Gagal mengambil data dari {source_url}: {e}")
            continue

        lines = content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF:"):
                extinf_line = line
                
                # Ekstrak nama channel
                match = re.search(r',([^,]+)$', extinf_line)
                raw_name = match.group(1).strip() if match else "Unknown"
                clean_name = re.sub(r'\.\d+[A-Z]+$', '', raw_name)
                safe_name = re.sub(r'[\\/*?:"<>|]', "", clean_name).strip().replace(" ", "_")
                if not safe_name:
                    safe_name = "Unknown"

                # Ekstrak kategori dari atribut group-title
                group_match = re.search(r'group-title="([^"]+)"', extinf_line, re.IGNORECASE)
                if group_match:
                    raw_category = group_match.group(1).strip()
                    safe_category = re.sub(r'[\\/*?:"<>|]', "", raw_category).strip().replace(" ", "_")
                else:
                    safe_category = "Uncategorized"

                block_lines = [extinf_line]
                i += 1
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith("#EXTINF:") or next_line.startswith("#EXTM3U"):
                        i -= 1
                        break
                    if next_line:
                        block_lines.append(next_line)
                    i += 1

                # Simpan ke dictionary channel (mempertahankan fungsi lama)
                if safe_name not in channels:
                    channels[safe_name] = []
                channels[safe_name].append(block_lines)

                # Simpan ke dictionary kategori (fitur baru)
                if safe_category not in categories:
                    categories[safe_category] = []
                categories[safe_category].append(block_lines)
            i += 1

    # 1. Simpan file M3U terpisah per channel di folder Sumber Indo (Dipertahankan)
    for channel_name, entries in channels.items():
        file_path = os.path.join(OUTPUT_DIR, f"{channel_name}.m3u")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for block in entries:
                for bline in block:
                    f.write(f"{bline}\n")

    # 1.5 Simpan file M3U terpisah per kategori di folder Kategori Indo (Fitur Baru)
    for category_name, entries in categories.items():
        cat_file_path = os.path.join(CATEGORY_DIR, f"{category_name}.m3u")
        with open(cat_file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for block in entries:
                for bline in block:
                    f.write(f"{bline}\n")
        print(f"Memperbarui kategori: {category_name}.m3u")

    # 2. Buat playlist gabungan khusus berdasarkan select_ch.txt (Dipertahankan)
    if os.path.exists(SELECT_FILE):
        with open(SELECT_FILE, "r", encoding="utf-8") as f:
            selected_names = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        if selected_names:
            with open(CUSTOM_PLAYLIST, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for name in selected_names:
                    safe_target = re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")
                    if safe_target in channels:
                        for block in channels[safe_target]:
                            for bline in block:
                                f.write(f"{bline}\n")
                        print(f"Menambahkan ke playlist pilihan: {name}")
            print(f"Berhasil memperbarui playlist custom: {CUSTOM_PLAYLIST}")

if __name__ == "__main__":
    parse_and_split_m3u()
