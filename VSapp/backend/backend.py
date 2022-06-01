from email.header import Header
from http.client import OK
import os
import re
from flask import Flask, Response, flash, redirect, request
from flask import render_template, request, Blueprint, current_app, send_file
from DB.DBWrapper import DBWrapper
from werkzeug.utils import secure_filename
import json

from utils import get_chunk

app = Flask(__name__)

app.debug = True
if __name__ == "__main__":
	app.run(threaded=True)
db = DBWrapper()
videosPath = "/Users/andreipetre/VSapp/Videos"

@app.after_request
def after_request(response):
	response.headers.add('Accept-Ranges', 'bytes')
	return response

@app.route("/users")
def get_users():
	return db.get_users()



@app.route('/video/<IdVideo>')
def get_video(IdVideo):

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
			if groups[1]:
				byte2 = int(groups[1])
	
	chunk, start, length, file_size = get_chunk(video_path,video_size,byte1, byte2)
	resp = Response(chunk, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)

	resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
	return resp


@app.route('/get_videos')
def get_video_library():
	vid_lib = db.get_available_videos()
	return json.dumps(vid_lib)

@app.route('/get_image/<IdImage>')
def get_image(IdImage):
	filename = "/Users/andreipetre/VSapp/Images/" + IdImage + ".jpeg"
	return send_file(filename, mimetype='image/gif')

@app.route('/get_thumbnail/<IdImage>')
def get_thumbnail(IdImage):
	filename = db.get_thumbnail_address(IdImage)
	return send_file(filename, mimetype='image/gif')


@app.route('/video', methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	else:
		filename = secure_filename(file.filename)
		file.save(os.path.join(videosPath, filename))
		flash('Video successfully uploaded and displayed below')
		return Response(None, 200)



