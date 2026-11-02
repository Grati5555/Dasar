import os
import re
import urllib.request

SOURCES_FILE = "sources.txt"
OUTPUT_DIR = "Sumber Indo"

def parse_and_split_m3u():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Baca daftar link sumber dari file sources.txt
    if not os.path.exists(SOURCES_FILE):
        print(f"File {SOURCES_FILE} tidak ditemukan!")
        return

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        source_urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not source_urls:
        print("Tidak ada link sumber yang ditemukan di sources.txt")
        return

    channels = {}

    # 2. Loop semua link sumber yang didaftarkan
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
                
                # Bersihkan nama channel
                match = re.search(r',([^,]+)$', extinf_line)
                raw_name = match.group(1).strip() if match else "Unknown"
                clean_name = re.sub(r'\.\d+[A-Z]+$', '', raw_name)
                safe_name = re.sub(r'[\\/*?:"<>|]', "", clean_name).strip().replace(" ", "_")
                if not safe_name:
                    safe_name = "Unknown"

                # Kumpulkan blok channel (termasuk #KODIPROP dan URL/backup)
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

                # Gabungkan link jika channel dengan nama yang sama ditemukan di sumber berbeda
                if safe_name not in channels:
                    channels[safe_name] = []
                channels[safe_name].append(block_lines)
            i += 1

    # 3. Simpan ke file M3U terpisah per channel (menggabungkan backup dari semua sumber)
    for channel_name, entries in channels.items():
        file_path = os.path.join(OUTPUT_DIR, f"{channel_name}.m3u")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for block in entries:
                for bline in block:
                    f.write(f"{bline}\n")
        print(f"Berhasil memperbarui: {channel_name}.m3u")

if __name__ == "__main__":
    parse_and_split_m3u()
