import os
import requests
from datetime import datetime

output_file = "master.m3u"

# Hapus file master.m3u lama agar selalu fresh
if os.path.exists(output_file):
    os.remove(output_file)

# Informasi repository GitHub sumber (sesuai gambar: B-inal-123/bein-s)
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
                print(f"Membaca file: {file_name}")
                
                file_content = requests.get(download_url).text
                lines = file_content.splitlines()
                
                # Salin isi file M3U sumber secara utuh ke dalam master.m3u
                for line in lines:
                    cleaned_line = line.strip()
                    # Abaikan baris header #EXTM3U bawaan dari file pecahan agar tidak duplikat
                    if cleaned_line and not cleaned_line.startswith("#EXTM3U"):
                        outfile.write(cleaned_line + "\n")
                
                outfile.write("\n")
                
    print("Playlist berhasil digabungkan dengan format yang benar!")
else:
    print(f"Gagal mengakses repository sumber. Status code: {response.status_code}")
