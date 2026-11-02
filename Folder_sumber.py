import os
import concurrent.futures
import requests

# Konfigurasi Direktori & File
FOLDER_SUMBER = "Sumber_PL"          # Folder tempat menyimpan file-file m3u sumber
OUTPUT_FILE = "Sumber_PL.m3u"        # File master hasil gabungan
FILE_DAFTAR_LINK = "daftar_link.txt" # File berisi daftar link mentah sumber .m3u
TIMEOUT_DETIK = 5                    # Batas waktu pengecekan link (timeout)
MAKS_WORKERS = 20                    # Jumlah thread paralel untuk pengecekan

def download_sumber_m3u():
    """Fungsi untuk mengunduh otomatis file .m3u dari daftar link."""
    if not os.path.exists(FOLDER_SUMBER):
        os.makedirs(FOLDER_SUMBER)
        
    if not os.path.exists(FILE_DAFTAR_LINK):
        print(f"File '{FILE_DAFTAR_LINK}' tidak ditemukan. Melewati tahap download otomatis.")
        return

    print("Memulai auto-update (download) file sumber .m3u...")
    with open(FILE_DAFTAR_LINK, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for index, url in enumerate(links, start=1):
        try:
            print(f"Mengunduh sumber {index}: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Beri nama file otomatis berdasarkan urutan atau ekstrak dari URL
                nama_file = f"sumber_{index}.m3u"
                path_tujuan = os.path.join(FOLDER_SUMBER, nama_file)
                with open(path_tujuan, "w", encoding="utf-8") as f_out:
                    f_out.write(response.text)
            else:
                print(f"Gagal mendownload {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"Error mendownload {url}: {e}")

def cek_link(url):
    """Fungsi untuk memeriksa apakah link streaming aktif."""
    if not url or not url.startswith("http"):
        return False
    try:
        response = requests.head(url, timeout=TIMEOUT_DETIK, allow_redirects=True)
        if response.status_code < 400:
            return True
        else:
            response = requests.get(url, timeout=TIMEOUT_DETIK, stream=True)
            return response.status_code < 400
    except:
        return False

def proses_playlist():
    # 1. Download file-file sumber terlebih dahulu secara otomatis
    download_sumber_m3u()

    if not os.path.exists(FOLDER_SUMBER):
        print(f"Folder '{FOLDER_SUMBER}' tidak ditemukan!")
        return

    print(f"\nMulai membaca file .m3u dari folder '{FOLDER_SUMBER}'...")
    
    semua_entri = []
    header_pertama = "#EXTM3U\n"
    
    daftar_file = sorted(os.listdir(FOLDER_SUMBER))
    file_m3u_ditemukan = [f for f in daftar_file if f.endswith(".m3u")]
    
    if not file_m3u_ditemukan:
        print(f"Tidak ada file .m3u ditemukan di dalam folder '{FOLDER_SUMBER}'.")
        return

    for nama_file in file_m3u_ditemukan:
        path_file = os.path.join(FOLDER_SUMBER, nama_file)
        print(f"Membaca: {nama_file}")
        
        try:
            with open(path_file, "r", encoding="utf-8", errors="ignore") as f:
                baris_baris = f.readlines()
                
                i = 0
                while i < len(baris_baris):
                    baris = baris_baris[i].strip()
                    if baris.startswith("#EXTINF:"):
                        metadata = baris_baris[i]
                        if i + 1 < len(baris_baris):
                            url_stream = baris_baris[i+1].strip()
                            semua_entri.append((metadata, url_stream))
                            i += 1
                    i += 1
        except Exception as e:
            print(f"Gagal membaca {nama_file}: {e}")

    print(f"\nTotal channel ditemukan: {len(semua_entri)}. Memulai pengecekan link aktif...")

    def verifikasi_item(item):
        metadata, url = item
        if cek_link(url):
            return item
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAKS_WORKERS) as executor:
        hasil = list(executor.map(verifikasi_item, semua_entri))
        channel_aktif = [item for item in hasil if item is not None]

    print(f"\nLink aktif tersisa: {len(channel_aktif)} dari {len(semua_entri)} channel.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        f_out.write(header_pertama)
        for metadata, url in channel_aktif:
            f_out.write(metadata)
            if not metadata.endswith("\n"):
                f_out.write("\n")
            f_out.write(url + "\n")

    print(f"\nSelesai! Playlist bersih disimpan sebagai '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    proses_playlist()
