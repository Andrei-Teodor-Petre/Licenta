from typing import final
import psycopg2
from psycopg2 import pool
from configparser import ConfigParser
import subprocess
import cv2

from Models.Video import Video

class DBWrapper:

	def __init__(self):
		self.connPool = psycopg2.pool.SimpleConnectionPool(1,20,database="andreipetre", user='postgres', password='password', host='127.0.0.1', port='5432', options='-c search_path=vsapp,public')

	def connect(self):
		try:
			print('Connecting to the PostgreSQL database...')
			self.open()
			
			# execute a statement
			print('PostgreSQL database version:')
			self.cursor.execute('SELECT version()')

			# display the PostgreSQL database server version
			db_version = self.cursor.fetchone()
			print(db_version)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if self.conn is not None:
				self.close()
				print('Database connection closed.')

	def open(self):
			self.conn = self.connPool.getconn()
			self.cursor = self.conn.cursor()

	def close(self):
		self.cursor.close()
		self.connPool.putconn(self.conn)

	def get_users(self):
		try:
			self.open()
			self.cursor.execute(''' SELECT * FROM "Users"; ''')
			result = self.cursor.fetchall()
			self.conn.commit()
			return result
		finally:
			self.close()


	def get_videos(self):
		try:
			self.open()
			self.cursor.execute(''' SELECT * FROM "Videos" left join "Thumbnails" on "Thumbnails"."Id" = "Videos"."IdThumbnail"; ''')
			result = self.cursor.fetchall()
			self.conn.commit()
			return result
		finally:
			self.close()


	def get_video(self, IdVideo:int):
		try:
			self.open()
			self.cursor.execute('SELECT * FROM "Videos" left join "Thumbnails" on "Thumbnails"."Id" = "Videos"."IdThumbnail" where "Videos"."Id" = '+str(IdVideo))
			result = self.cursor.fetchone()
			return result
		finally:
			self.close()


	def get_available_videos(self):
		images_ids_dict = []
		videos = self.get_videos()
		print(videos)
		for i in range(len(videos)):
			images_ids_dict.append( Video(videos[i][0], videos[i][6],videos[i][10]).__dict__)

		return images_ids_dict

	def create_thumbnail(self, video_id:str):
		#on upload this will call the ffmpeg library function and create a thumbnail for the video
		video_address = '/Users/andreipetre/VSapp/Videos/'+video_id+'.mp4'
		image_address = '/Users/andreipetre/VSapp/Thumbnails/'+video_id+'.jpeg'
		subprocess.call(['ffmpeg', '-y', '-i', video_address, '-ss', '00:00:00.000', '-vframes', '1', image_address])
	


	def get_thumbnail(self, IdThumbnail:int):
		try:
			self.open()
			self.cursor.execute('SELECT * FROM "Thumbnails" where "Thumbnails"."Id" = '+str(IdThumbnail))
			result = self.cursor.fetchone()
			return result
		finally:
			self.close()

	def get_video_address(self, IdVideo:int) -> str:
		video = self.get_video(IdVideo)
		return video[1]
	def get_thumbnail_address(self, IdThumbnail:int):
		return self.get_thumbnail(IdThumbnail)[1]


db = DBWrapper()

# #db.drop_test_table()
# db.connect()

# video = db.get_video(1)
# print(video[1])

# videos = db.get_available_videos()
# print(videos)






