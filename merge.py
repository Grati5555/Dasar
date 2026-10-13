import glob

# Nama file hasil penggabungan akhir
output_file = "master.m3u"

# Mencari semua file berformat .m3u atau .m3u8 di folder (kecuali master.m3u itu sendiri)
read_files = [f for f in glob.glob("*.m3u*") if f != output_file]

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write("#EXTM3U\n")
    for f in read_files:
        with open(f, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
            for line in lines:
                # Lewati baris #EXTM3U di setiap file agar tidak duplikat
                if not line.startswith("#EXTM3U"):
                    outfile.write(line)
        outfile.write("\n")

print("Playlist berhasil digabungkan menjadi master.m3u")
