import os
import requests
from datetime import datetime

output_file = "eropa.m3u"

# Hapus file output lama agar selalu fresh
if os.path.exists(output_file):
    os.remove(output_file)

# Informasi repository sumber yang baru (B-inal-123/s-eropa)
owner = "B-inal-123"
repo = "s-eropa"
api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

print(f"Mengambil daftar file dari repository {owner}/{repo}...")
response = requests.get(api_url)

if response.status_code == 200:
    files = response.json()
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("#EXTM3U\n")
        outfile.write(f"# Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Saring file berformat .m3u atau .m3u8
        for file in files:
            file_name = file["name"]
            if file_name.endswith((".m3u", ".m3u8")) and file_name != output_file:
                download_url = file["download_url"]
                channel_name = os.path.splitext(file_name)[0]
                
                outfile.write(f'#EXTINF:-1, {channel_name}\n')
                outfile.write(f'{download_url}\n')
                
    print("Playlist eropa.m3u berhasil dibuat!")
else:
    print(f"Gagal mengakses repository sumber. Status code: {response.status_code}")
