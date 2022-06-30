from crypt import methods
from email.header import Header
from http.client import OK
import io
import os
import re
from flask import Flask, Response, flash, redirect, request, jsonify as flask_jsonnify, make_response,url_for,abort
from flask import render_template, request, Blueprint, current_app, send_file
from matplotlib.image import thumbnail
from DBWrapper import DBWrapper
from werkzeug.utils import secure_filename
import json
from constants import BASE_PATH, MASTER_PASSWORD

from PIL import Image
import subprocess
import base64

import uuid

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

####################### USERS #######################

@app.route("/users")
def get_users():
	#this needs to be rewritten -> into some auth 
	return db.get_users()

@app.route("/connect", methods=['POST'])
def connect():
	username = request.form['username']
	user_pass = request.form['password']
	server_password = request.form['server_password']

	if server_password != MASTER_PASSWORD :
		Response("Bad server password", 500)
	
	user = db.get_user_by_name(username=username)
	if user != None:
		#if username role > 3 then check the user admin password
		if user.role >= 3:
			if(user.password == user_pass):
				return json.dumps(user.__dict__)
			else:
				return Response("Bad user password", 500)
		else:
			return json.dumps(user.__dict__)
	elif username != '':
		#add user
		index = db.get_table_index("Users")
		#generate uuid token
		user_token = uuid.uuid4().hex
		db.add_user(index + 1,username,user_pass, user_token)

		user = db.get_user_by_name(username=username)
		return json.dumps(user.__dict__)
	else:
		return Response("Unknown user", 500)





####################### VIDEOS + THUMBNAILS #######################

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
		vid_lib = db.get_videos_by_tag(id_tag)
		return json.dumps(vid_lib)
	else:
		vid_lib = db.get_network_videos(id_user)
		return json.dumps(vid_lib)

@app.route('/get_thumbnail/<IdImage>')
def get_thumbnail(IdImage):
	filename = db.get_thumbnail_address(IdImage)
	return send_file(filename, mimetype='image/gif')


@app.route('/up_video', methods=['POST'])
def upload_video():
	index = db.get_table_index("Videos")
	index = index+1

	user = request.form['user']
	token = request.form['Authorization']


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

	user_id = db.get_username_id(user)
	db.save_video(index,f"Videos/video-{str(index)}.mov", user_id, duration, width, height, f"/get_video/{str(index)}", thumbnail_id, data_size )

	#save to file structure
	fh = open(videoAddress, "wb")
	fh.write(upload)
	fh.close()

	return Response(None, 200)

@app.route('/update_video_tags/<id_video>/<id_user>', methods=['POST'])
def update_video_tags(id_video: int, id_user: int):

	outdated_video_tags_list = db.get_tags_for_video(id_video)
	outdated_tags = {}
	for tag in outdated_video_tags_list:
		outdated_tags[int(tag['id'])] = tag['value']
	new_tags = {}
	for key, val in request.form.items():
		#first add all the tags that don't exist
		id_tag = db.get_tag_id(val)
		if id_tag == None:
			#create new tag
			id_new_tag = db.add_tag(val)
			new_tags[id_new_tag] = val
		elif id_tag in outdated_tags.keys():
			del outdated_tags[id_tag]
		else:
			new_tags[key] = val		
	#at this point in outdated_video_tags there are the tags that have been removed
	for id_tag, _ in outdated_tags.items():
		db.remove_tag_association(id_tag,id_video)

	for key, val in new_tags.items():
		db.add_tag_association(val, id_video)

	video_tags = db.get_tags_for_video(id_video)
	return json.dumps(video_tags)
	
def handle_video_thumbnail(index, videoAddress) -> int:
	(thumbnail_address_db,width,height) = create_thumbnail(videoAddress, index)
	thumbnail_id = db.save_thumbnail(index, thumbnail_address_db, f"/get_thumbnail/{index}" )

	return (thumbnail_id,width,height)

@app.route('/delete_video/<id_video>')
def delete_video(id_video):
	try:

		video = db.get_video(id_video)
		id_thumbnail = video[0]
		video_address = video[1]
		thumbnail_address = video[11]

		#video_tags = db.get_tags_for_video(id_video)

		#set the on delete cascade for this
		# for tag in video_tags:
		# 	db.remove_tag_association(tag['id'],id_video)
		tags = db.get_tags_for_video(id_video)
		

		db.delete_video(id_thumbnail=id_thumbnail)
		os.remove(f'{BASE_PATH}/{video_address}')
		os.remove(f'{BASE_PATH}{thumbnail_address}')


		for tag in tags:
			db.check_remove_tag(tag['id'])

		return Response(None, 200)
	except Exception as err:
		print(err)
		return Response(None, 500)
	





####################### TAGS #######################

@app.route('/get_tags')
def get_tags():
	tags_dict = db.get_tags()
	return json.dumps(tags_dict)




####################### IMAGES #######################


@app.route('/get_images')
def get_images_library():
	img_lib = db.get_network_images(1)
	return json.dumps(img_lib)

# @app.route('/get_image/<IdImage>')
# def get_image(IdImage):
# 	filename = f"{imagesPath}/image-{IdImage}"
# 	return send_file(filename, mimetype='image/gif')



@app.route('/up_image', methods=['POST'])
def upload_image():
	index = db.get_table_index("Images") + 1

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



@app.route('/delete_image/<id_image>')
def delete_image(id_image):
	image_path = f"{BASE_PATH}{db.get_image_address(id)}"
	os.remove(image_path)

	db.delete_image()




	

