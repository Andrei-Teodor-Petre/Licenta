from crypt import methods
from email.header import Header
from http.client import OK
import io
import os
import re
from flask import Flask, Response, flash, redirect, request, jsonify as flask_jsonnify, make_response,url_for,abort
from flask import render_template, request, Blueprint, current_app, send_file
from DBWrapper import DBWrapper
from werkzeug.utils import secure_filename
import json
from constants import BASE_PATH, BASE_URL

from PIL import Image
import subprocess
import base64

from utils import get_chunk, create_thumbnail

app = Flask(__name__)

app.debug = True
if __name__ == "__main__":
	app.run(threaded=True)
db = DBWrapper()

videosPath = f"{BASE_PATH}/Videos"
imagesPath = f"{BASE_PATH}/Images"

class FileManager:
	def __init__(self, file):
		self.file = file

filePointer = io.TextIOWrapper

fileMgr = FileManager(filePointer)


@app.after_request
def after_request(response):
	response.headers.add('Accept-Ranges', 'bytes')
	return response

@app.route("/users")
def get_users():
	#this needs to be rewritten -> into some auth 
	return db.get_users()



@app.route('/get_video/<IdVideo>')
def get_video(IdVideo):
	IdVideo = int(IdVideo)
	video_path = db.get_video_address(IdVideo=IdVideo)
	video_size = os.stat(video_path).st_size

	range_header = request.headers.get('Range', None)
	byte1, byte2 = 0, None
	if range_header:
		match = re.search(r'(\d+)-(\d*)', range_header)
		if match != None:
			groups = match.groups()
			if groups[0]:
				byte1 = int(groups[0])
				#if this is 0 -> open the file as well and store the I/O pointer
				if byte1 == 0:
					fileMgr.file = open(video_path, 'rb')
			if groups[1]:
				byte2 = int(groups[1])
	
	chunk, start, length, file_size = get_chunk(fileMgr.file,video_size,byte1, byte2)
	resp = Response(chunk, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)

	resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
	return resp



@app.route('/get_videos/<id_user>/<id_tag>')
def get_video_library(id_user:int,id_tag:int):
	id_user = int(id_user)
	id_tag = int(id_tag)

	if id_tag != 0:
		vid_lib = db.get_videos_by_tag(id_tag, id_user)
		return json.dumps(vid_lib)
	else:
		vid_lib = db.get_network_videos(id_user)
		return json.dumps(vid_lib)

@app.route('/get_tags')
def get_tags():
	tags_dict = db.get_tags()
	return json.dumps(tags_dict)

@app.route('/get_images')
def get_images_library():
	img_lib = db.get_network_images(1)
	return json.dumps(img_lib)

@app.route('/get_image/<IdImage>')
def get_image(IdImage):
	filename = f"{imagesPath}/image-{IdImage}"
	return send_file(filename, mimetype='image/gif')

@app.route('/get_thumbnail/<IdImage>')
def get_thumbnail(IdImage):
	filename = db.get_thumbnail_address(IdImage)
	return send_file(filename, mimetype='image/gif')


@app.route('/up_video', methods=['POST'])
def upload_video():
	index = db.get_videos_index()
	index = index[0]+1

	file = request.files['file']
	upload = file.read()
	data_size = len(upload)
	mimetype = file.content_type

	videoAddress = f"{videosPath}/video-{str(index)}.mov"
	with open(videoAddress, 'wb') as f:
		f.write(upload)
		f.close()
	
	processStatus = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", videoAddress], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	duration = int(float(processStatus.stdout))
	print(duration)
	

	#save to db
	(thumbnail_id,width,height) = handle_video_thumbnail(index, videoAddress)
	db.save_video(index,f"Videos/video-{str(index)}.mov", 1, duration, width, height, f"/get_video/{str(index)}", thumbnail_id )

	#save to file structure
	fh = open(videoAddress, "wb")
	fh.write(upload)
	fh.close()

	return Response(None, 200)

@app.route('/up_image', methods=['POST'])
def upload_image():
	index = db.get_images_index()[0] + 1

	file = request.files['file']
	upload = file.read()
	data_size = len(upload)
	mimetype = file.content_type

	image = Image.open(io.BytesIO(upload))

	file_address = f"{imagesPath}/image-{str(index)}"
	
	fh = open(file_address, "wb")
	fh.write(upload)
	fh.close()

	file_address_db = f"/Images/image-{str(index)}"
	imageId = db.save_image(index,file_address_db, 1, image.width, image.height, f"/get_image/{index}")

	return Response(str(imageId), 200)

def handle_video_thumbnail(index, videoAddress) -> int:
	(thumbnail_address_db,width,height) = create_thumbnail(videoAddress, index)
	thumbnail_id = db.save_thumbnail(index, thumbnail_address_db, f"/get_thumbnail/{index}" )

	return (thumbnail_id,width,height)


@app.route('/delete_image/<id_image>')
def delete_image(id_image):
	image_path = f"{BASE_PATH}{db.get_image_address(id)}"
	os.remove(image_path)

	db.delete_image()

@app.route('/delete_video/<id_video>')
def delete_video(id_video):
	video = db.get_video(id_video)
	id_thumbnail = video[8]
	db.delete_video(id_thumbnail=id_thumbnail)

