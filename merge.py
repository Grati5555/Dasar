import glob
import os

output_file = "master.m3u"

# Hapus file master.m3u yang lama jika ada, agar selalu dibuat baru dari awal
if os.path.exists(output_file):
    os.remove(output_file)

# Cari semua file .m3u atau .m3u8 di repository
read_files = [f for f in glob.glob("*.m3u*") if f != output_file]

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write("#EXTM3U\n")
    for f in read_files:
        with open(f, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    outfile.write(lines[i])
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            outfile.write(lines[j])
                            break
                        j += 1
                    i = j
                i += 1
        outfile.write("\n")

print("File master.m3u berhasil diperbarui dan digabung ulang.")
