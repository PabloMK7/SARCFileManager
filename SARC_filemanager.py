#SARC File Manager by PabloMK7. Credits to Gericom for all the SARC stuff.

import argparse
print("\n SARC File Manager v0.1\n------------------------\n\n")
parser = argparse.ArgumentParser(description='SARC file manager.')
parser.add_argument("sarc_file", help = "SARC file to operate with.")
parser.add_argument('-a', "--add_filename", help= 'Add file name entry.')
args = parser.parse_args()

def to_le(value, size):
	if (size == 2):
		return (((value & 0xff00) >> 8) + ((value & 0xff) << 8))
	if (size == 4):
		return (((value & 0xff000000) >> 24) + ((value & 0xff0000) >> 8) + ((value & 0xff00) << 8) + ((value & 0xff) << 24))

def to_str(value, size):
	data = ""
	i = size
	while (i > 0):
		data += chr(((value & (0xff << ((i - 1) * 8))) >> ((i - 1) * 8)))
		i-=1
	return data

def getfilestring(f, size):
	return f.read(size)
	
def getfilebytes(f, size):
	data = 0
	i = size * 2
	str = f.read(size)
	for x in str:
		data = data + ord(x) * (0x10 ** (i - 2))
		i -= 2
		if (i == 0):
			break
	return data

def getfilebytes_le(f, size):
	data = 0
	i = 0
	str = f.read(size)
	for x in str:
		data = data + ord(x) * (0x10 ** (i))
		i += 2
		if (i == size * 2):
			break
	return data
		
def calculatenamehash(name, multiplier):
	res = 0
	i = 0
	for x in name:
		res = ((ord(x) + i) + res * multiplier) & 0xFFFFFFFF
	return res
	
def addtableentry(f, sarc_filesize, hasht_offset, hasht_entries, filehash):
	if (hasht_entries == 1):
		print("WARNING: The SARC archive has only a single file inside,\ncannot detect compatibility with the tool.\n")
	else:
		f.seek(hasht_offset + 0x14)
		if (f.read(4) != "\x00\x00\x00\x00"):
			return -2
	f.seek(hasht_offset)
	currval = 0x00
	currpos = hasht_offset
	while(currpos <= (hasht_entries * 0x10) + hasht_offset):
		currval = getfilebytes_le(f, 0x4)
		if (currval > filehash):
			break
		elif (currval == filehash):
			return -1
		currpos += 0x10
		f.seek(currpos)
	f.seek(0)
	filebuff = f.read(currpos)
	filebuff += to_str(to_le(filehash,4), 4)
	filebuff += "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
	filebuff += f.read(sarc_filesize - currpos)
	f.seek(0)
	f.write(filebuff)
	f.flush()
	return currpos
	
def main():
	if (args.add_filename):
		sarc_f = open(args.sarc_file, "rb+")
		file_signature = getfilestring(sarc_f, 4)
		if (file_signature == "Yaz0"):
			print("Invalid input file: The file is yaz0 compressed,\nuse \"Every File Explorer -> Tools -> Compression -> Yaz0 -> Decompress...\"\nto decompress the sarc before proceeding.\n(You may need to compress it again after using this tool.)")
			sarc_f.close()
			return 0
		elif (file_signature != "SARC"):
			print("Invalid input file: Not a SARC file.")
			sarc_f.close()
			return 0
		sarc_headersize = getfilebytes_le(sarc_f, 0x2)
		if (getfilebytes(sarc_f, 0x2) != 0xfffe):
			print("Invalid input file: Only little endian SARCs are supported.")
			sarc_f.close()
			return 0
		sarc_filesize = getfilebytes_le(sarc_f, 0x4)
		sarc_filedataoffset = getfilebytes_le(sarc_f, 0x4)
		sarc_f.seek(sarc_headersize)
		if (getfilestring(sarc_f, 4) != "SFAT"):
			print("Invalid input file: SFAT table not found")
			sarc_f.close()
			return 0
		SFAT_headersize = getfilebytes_le(sarc_f, 0x2)
		SFAT_entrycount = getfilebytes_le(sarc_f, 0x2)
		SFAT_hashmultiplier = getfilebytes_le(sarc_f, 0x4)
		filehash = calculatenamehash(args.add_filename, SFAT_hashmultiplier)
		print("Trying to add file entry \"" + args.add_filename + "\" (0x%x)" % filehash + " to the file: \"" + args.sarc_file + "\"\n")
		addedentrypos = addtableentry(sarc_f, sarc_filesize, sarc_headersize + SFAT_headersize, SFAT_entrycount, filehash)
		if (addedentrypos == -1):
			print("File name already present in the SARC!\n")
			sarc_f.close()
			return 0
		elif (addedentrypos == -2):
			print("Invalid input file: SARCs with SFNT sections aren't supported.\n")
			sarc_f.close()
			return 0
		sarc_filedataoffset += 0x10
		SFAT_entrycount += 1
		sarc_f.seek(0,2)
		while ((sarc_f.tell() % 0x10) != 0):
			sarc_f.write("\x00")
			sarc_f.flush()
		sarc_f.write("\x00")
		sarc_f.flush()
		sarc_filesize = sarc_f.tell()
		sarc_f.seek(addedentrypos + 0x08)
		sarc_f.write(to_str(to_le((sarc_filesize - 1) - sarc_filedataoffset, 4), 4) + to_str(to_le(sarc_filesize - sarc_filedataoffset, 4), 4))
		sarc_f.seek(0x8)
		sarc_f.write(to_str(to_le(sarc_filesize, 4), 4))
		sarc_f.write(to_str(to_le(sarc_filedataoffset, 4), 4))
		sarc_f.seek(sarc_headersize + 0x6)
		sarc_f.write(to_str(to_le(SFAT_entrycount, 2), 2))
		sarc_f.close()
		print("Done!")
		
		
		
	
main()