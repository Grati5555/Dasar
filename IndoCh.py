import os
import re
import urllib.request

# Ganti dengan Link M3U Sumber Anda di dalam tanda kutip
SOURCE_URL = "https://github.com/apistech/project/raw/refs/heads/main/IndihomeTV.m3u"
OUTPUT_DIR = "Sumber Indo"

def parse_and_split_m3u():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Gagal mengambil data: {e}")
        return

    lines = content.splitlines()
    channels = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            extinf_line = line
            match = re.search(r',(.+)$', extinf_line)
            channel_name = match.group(1).strip() if match else "Unknown"
            safe_name = re.sub(r'[\\/*?:"<>|]', "", channel_name).replace(" ", "_")

            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if not url_line.startswith("#"):
                    if safe_name not in channels:
                        channels[safe_name] = []
                    channels[safe_name].append((extinf_line, url_line))
                    i += 1
        i += 1

    for channel_name, entries in channels.items():
        file_path = os.path.join(OUTPUT_DIR, f"{channel_name}.m3u")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for extinf, url in entries:
                f.write(f"{extinf}\n{url}\n")
        print(f"Berhasil: {channel_name}.m3u")

if __name__ == "__main__":
    parse_and_split_m3u()
