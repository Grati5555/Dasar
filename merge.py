import os
import requests
from datetime import datetime

output_file = "master.m3u"

# Hapus file master.m3u lama agar selalu fresh
if os.path.exists(output_file):
    os.remove(output_file)

# Informasi repository GitHub sumber (B-inal-123/bein-s)
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
        
        # Saring file yang berformat .m3u atau .m3u8
        for file in files:
            file_name = file["name"]
            if file_name.endswith((".m3u", ".m3u8")) and file_name != output_file:
                download_url = file["download_url"]
                # Buat nama channel bersih tanpa ekstensi file
                channel_name = os.path.splitext(file_name)[0]
                
                # Tulis format M3U yang menunjuk langsung ke URL raw file sumber
                outfile.write(f'#EXTINF:-1, {channel_name}\n')
                outfile.write(f'{download_url}\n')
                
    print("Master playlist berhasil dibuat!")
else:
    print(f"Gagal mengakses repository sumber. Status code: {response.status_code}")
