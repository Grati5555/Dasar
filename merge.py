import os
import requests
from datetime import datetime

output_file = "master.m3u"

# Hapus file master.m3u lama agar selalu fresh
if os.path.exists(output_file):
    os.remove(output_file)

# Informasi repository GitHub sumber
owner = "B-inal-123"
repo = "bein-s"
api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

print(f"Mengambil daftar file dari repository {owner}/{repo}...")
response = requests.get(api_url)

if response.status_code == 200:
    files = response.json()
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("#EXTM3U\n")
        outfile.write(f"# Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        channel_counter = 1
        for file in files:
            file_name = file["name"]
            if file_name.endswith((".m3u", ".m3u8")) and file_name != output_file:
                download_url = file["download_url"]
                print(f"Mengunduh dan menggabung: {file_name}")
                
                file_content = requests.get(download_url).text
                lines = file_content.splitlines()
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith("#EXTINF:"):
                        # Periksa apakah ada nama channel setelah tanda koma
                        parts = line.split(",", 1)
                        if len(parts) > 1 and parts[1].strip() != "":
                            extinf_line = line
                        else:
                            # Jika nama kosong, berikan nama otomatis agar terbaca IPTV
                            extinf_line = f"{parts[0]},Channel {channel_counter}"
                            channel_counter += 1
                        
                        outfile.write(extinf_line + "\n")
                        
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j].strip()
                            if next_line and not next_line.startswith("#"):
                                outfile.write(lines[j] + "\n")
                                break
                            j += 1
                        i = j
                    i += 1
                outfile.write("\n")
                
    print("Playlist berhasil diperbaiki dan digabungkan untuk OTT Navigator!")
else:
    print(f"Gagal mengakses repository sumber. Status code: {response.status_code}")
