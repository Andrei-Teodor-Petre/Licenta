import subprocess
from constants import BASE_PATH
from PIL import Image


def get_chunk(f, file_size, byte1=None, byte2=None):
	start = 0
	if byte1 < file_size:
		start = byte1
	if byte2:
		length = byte2 + 1 - byte1
	else:
		length = file_size - start
	#with open(full_path, 'rb') as f:
	f.seek(start)
	chunk = f.read(length)
	return chunk, start, length, file_size


def create_thumbnail(video_addr:str, video_id):
	#on upload this will call the ffmpeg library function and create a thumbnail for the video
	image_address = f"{BASE_PATH}/Thumbnails/thumbnail-{str(video_id)}.jpeg"
	subprocess.call(['ffmpeg', '-y', '-i', video_addr, '-ss', '00:00:00.000', '-vframes', '1', image_address])
	thumbnail = Image.open(image_address)
	return (f"/Thumbnails/thumbnail-{str(video_id)}.jpeg", thumbnail.width, thumbnail.height)

