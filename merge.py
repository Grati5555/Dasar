import glob

# Nama file hasil penggabungan akhir
output_file = "master.m3u"

# Cari semua file berformat .m3u atau .m3u8 di repository (kecuali master.m3u)
read_files = [f for f in glob.glob("*.m3u*") if f != output_file]

with open(output_file, "w", encoding="utf-8") as outfile:
    # Tulis header wajib M3U di baris paling atas
    outfile.write("#EXTM3U\n")
    
    for f in read_files:
        with open(f, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Cek apakah baris dimulai dengan #EXTINF (info channel)
                if line.startswith("#EXTINF:"):
                    # Tulis baris #EXTINF ke master.m3u
                    outfile.write(lines[i])
                    
                    # Cari baris berikutnya yang merupakan URL link siaran langsung
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        # Lewati jika baris kosong atau masih berupa tag konfigurasi lain
                        if next_line and not next_line.startswith("#"):
                            outfile.write(lines[j]) # Tulis URL link channel
                            break
                        j += 1
                    i = j # Lanjutkan perulangan setelah URL ditemukan
                i += 1
        
        # Berikan spasi antar file sumber agar rapi
        outfile.write("\n")

print("Playlist berhasil digabungkan dengan menyaring baris #EXTINF dan URL saja.")
