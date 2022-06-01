def get_chunk(full_path, file_size, byte1=None, byte2=None):
	start = 0
	if byte1 < file_size:
		start = byte1
	if byte2:
		length = byte2 + 1 - byte1
	else:
		length = file_size - start
	with open(full_path, 'rb') as f:
		f.seek(start)
		chunk = f.read(length)
	return chunk, start, length, file_size