from ast import Str
from datetime import date, datetime, timezone
from pickle import NONE
from typing import final
import uuid
from matplotlib import image
import psycopg2
from psycopg2 import pool
from configparser import ConfigParser

import cv2

from Structs import Image, Tag, User, Video
from constants import BASE_PATH

class DBWrapper:

	def __init__(self):
		self.connPool = psycopg2.pool.ThreadedConnectionPool(1,8,database="andreipetre", user='postgres', password='password', host='127.0.0.1', port='5432', options='-c search_path=vsapp,public')

	def open(self):
			conn = self.connPool.getconn()
			cursor = conn.cursor()
			return (conn, cursor)

	def close(self, conn, cursor):
		cursor.close()
		self.connPool.putconn(conn)


	def get_table_index(self, table_name: Str):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				select "Id"
				from "{table_name}"
				order by "Id" desc
				limit 1;
			''')
			result = cursor.fetchone()
			return result[0]
		finally:
			self.close(conn, cursor)



####################### USERS #######################
	def get_users(self):
		(conn, cursor) = self.open()
		try:
			cursor.execute(''' SELECT * FROM "Users"; ''')
			result = cursor.fetchall()
			conn.commit()
			return result
		finally:
			self.close(conn, cursor)
	
	def get_user_by_name(self, username: Str):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' SELECT * FROM "Users" WHERE "Users"."Username" = '{username}'; ''')
			
			conn.commit()
			result = cursor.fetchone()
			if result != None:
				
				if result[5] != None: 
					token = result[5]
				else:
					token = uuid.uuid4()
					self.update_user_token(result[0],token.hex)

				return_val = User(result[0],result[1],token.hex)
				return return_val
			else:
				return None
		finally:
			self.close(conn, cursor)

	def update_user_token(self,user_id,token):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' UPDATE "Users"
                SET "Token" = '{token}'
                WHERE "Id" = {user_id}; ''')
		finally:
			self.close(conn, cursor)

	def add_user(self, index:int, username: Str, token: Str):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 				
				INSERT INTO "Users" ("Id", "Username", "Password", "Email", "Role", "Token")
				VALUES({index},'{username}','{username}','{username}', {2}, ) 
				RETURNING "Users"."Id"; 
			''')
			
			conn.commit()
			result = cursor.fetchone()
			return result[0]

		finally:
			self.close(conn, cursor)

	def get_username_id(self, username: Str):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				select "Id"
				from "Users"
				where "Users"."Username" = '{username}'
				order by "Id" desc
				limit 1;
			''')
			result = cursor.fetchone()

			if result != None:
				return result[0]
			else:
				return None
		finally:
			self.close(conn, cursor)

	def delete_user(self, username:Str):
		print(username)
		pass





####################### VIDEOS + THUMBNAILS #######################

	def get_videos(self, id_user):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				SELECT "Videos"."Id", "Videos"."URL", "Thumbnails"."ThumbnailUrl", "Duration", "Username", "Width", "Height", "Size", "DateAdded"
				FROM "Videos" 
				left join "Thumbnails" on "Thumbnails"."Id" = "Videos"."IdThumbnail"
				left join "Users" on "Users"."Id" = "Videos"."IdUser"
				--WHERE "IdUser" = {id_user}
			; ''')
			result = cursor.fetchall()
			conn.commit()
			return result
		finally:
			self.close(conn, cursor)

	def get_video_address(self, IdVideo:int) -> str:
		video = self.get_video(IdVideo)
		return f"{BASE_PATH}/{video[1]}" 

	def get_thumbnail(self, IdThumbnail:int):
		(conn, cursor) = self.open()
		try:
			cursor.execute('SELECT * FROM "Thumbnails" where "Thumbnails"."Id" = '+str(IdThumbnail))
			result = cursor.fetchone()
			return result
		finally:
			self.close(conn, cursor)

	def get_video(self, IdVideo:int):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f'''
				SELECT * FROM "Videos" 
				left join "Thumbnails" on "Thumbnails"."Id" = "Videos"."IdThumbnail" 
				where "Videos"."Id" = {str(IdVideo)}
			''')
			result = cursor.fetchone()
			return result
		finally:
			self.close(conn, cursor)

	def save_thumbnail(self, index, thumbnail_address, thumbnail_url):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f'''
			
				INSERT INTO "Thumbnails" ("Id", "ThumbnailAddress", "ThumbnailUrl")
				VALUES({index},'{thumbnail_address}','{thumbnail_url}') 
				RETURNING "Thumbnails"."Id";
			
			''' )
			conn.commit()
			result = cursor.fetchone()
			return result[0]
		finally:
			self.close(conn, cursor)

	def save_video(self, index, fileAddress, idUser, duration, width, height, url, thumbnail_id, size):
		(conn, cursor) = self.open()
		try:

			#test which one works
			dt = datetime.now(timezone.utc)
			date_added = date.today()

			cursor.execute(f'''
			
				INSERT INTO "Videos" ("Id", "VideoAddress", "IdUser", "Duration", "Height", "Width", "URL", "IdThumbnail", "Size", "DateAdded")
				VALUES({index},'{fileAddress}',{idUser}, {duration}, {height}, {width}, '{url}', {thumbnail_id}, {size}, CURRENT_TIMESTAMP) 
				RETURNING "Videos"."Id";
			
			''' )
			conn.commit()
			result = cursor.fetchone()
			return result[0]
		finally:
			self.close(conn, cursor)

	def get_network_videos(self, id_user):
		images_ids_dict = []
		videos = self.get_videos(id_user)
		for i in range(len(videos)):
			video_tags = self.get_tags_for_video(videos[i][0])
			video_date = videos[i][8].strftime("%d/%m/%Y") if videos[i][8] != None else None
			images_ids_dict.append( Video(videos[i][0], videos[i][1], videos[i][2], videos[i][3], videos[i][4], videos[i][5], videos[i][6], videos[i][7], video_date, video_tags).__dict__)

		return images_ids_dict

	def get_videos_by_tag(self, id_tag:int):
		(conn, cursor) = self.open()
		try:
			return_json = []
			cursor.execute(f'''
			SELECT "Videos"."Id", "Videos"."URL", "Thumbnails"."ThumbnailUrl", "Duration", "Username", "Width", "Height", "Size", "DateAdded"
			FROM "Videos" 
			left join "Thumbnails" on "Thumbnails"."Id" = "Videos"."IdThumbnail"
			left join "Users" on "Users"."Id" = "Videos"."IdUser"
			left join "VideoTagsAssociations" on "VideoTagsAssociations"."IdVideo" = "Videos"."Id" 
			where "VideoTagsAssociations"."IdTag" = {id_tag}''')
			result = cursor.fetchall()

			for i in range(len(result)):
				video_tags = self.get_tags_for_video(result[i][0])
				video_date = result[i][8].strftime("%d/%m/%Y") if result[i][8] != None else None
				return_json.append( Video(result[i][0], result[i][1], result[i][2], result[i][3], result[i][4], result[i][5], result[i][6], result[i][7], video_date, video_tags).__dict__)

			return return_json
		finally:
			self.close(conn, cursor)

	def delete_video(self, id_thumbnail):
		(conn, cursor) = self.open()
		try:

			#we delete the thumbnail and the delete cascade deletes the video row
			cursor.execute(f'''
			
				DELETE FROM "Thumbnails" 
				WHERE "Thumbnails"."Id" = {id_thumbnail} 
				RETURNING *;

			''' )
			conn.commit()
			result = cursor.fetchone()
			if result == None:
				return "No rows deleted"
			return result
		finally:
			self.close(conn, cursor)

####################### TAGS #######################

	def get_tags_for_video(self, id_video):
		(conn, cursor) = self.open()
		try:

			cursor.execute(f''' 
				SELECT "IdTag", "Value" FROM "Videos" 
				left join "VideoTagsAssociations" on "VideoTagsAssociations"."IdVideo" = "Videos"."Id"
				left join "Tags" on "Tags"."Id" = "VideoTagsAssociations"."IdTag"
				WHERE "Videos"."Id" = {id_video}
				ORDER BY "IdTag"
			; ''')
			result = cursor.fetchall()
			conn.commit()

			if(result[0] == (None,None)):
				return []

			video_tags = []
			for j in range(len(result)):
				video_tags.append(Tag(result[j][0], result[j][1]).__dict__)
			return video_tags
		finally:
			self.close(conn, cursor)
	
	def add_tag(self, value:Str):
		(conn, cursor) = self.open()
		try:
			index = db.get_table_index('Tags') + 1
			cursor.execute(f''' 
				INSERT INTO "Tags" ("Id", "Value")
				VALUES({index},'{value}') 
				RETURNING "Tags"."Id";
			; ''')
			result = cursor.fetchone()
			conn.commit()

			if result == None:
				return None
			return result[0]
		finally:
			self.close(conn, cursor)


	def get_tag_id(self, tag_value:Str):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				SELECT * FROM vsapp."Tags" 
				WHERE "Value" = '{tag_value}'
				ORDER BY "Id"
			; ''')
			result = cursor.fetchone()
			conn.commit()

			if result == None:
				return None
			return result[0]
		finally:
			self.close(conn, cursor)

	def add_tag_association(self,tag_value, id_video):
		id_tag = self.get_tag_id(tag_value)
		index = self.get_table_index("VideoTagsAssociations")+1

		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				INSERT INTO "VideoTagsAssociations" ("Id", "IdVideo", "IdTag")
				VALUES({index},{id_video},{id_tag}) 
				RETURNING "VideoTagsAssociations"."Id";
			; ''')
			result = cursor.fetchone()
			conn.commit()

			if result == None:
				return None
			return result[0]
		finally:
			self.close(conn, cursor)	

	def remove_tag_association(self, id_tag, id_video):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				DELETE FROM "VideoTagsAssociations"
				WHERE "IdVideo" = {id_video} and "IdTag" = {id_tag}
			; ''')
			conn.commit()
		finally:
			self.close(conn, cursor)
			self.check_remove_tag(id_tag)#when there are no more vids associated with the tag, remove it

	
	def check_remove_tag(self, id_tag):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f'''Select count(*) from "VideoTagsAssociations" where "IdTag" = {id_tag};''')
			remaning_associations_for_tag = cursor.fetchone()
			if remaning_associations_for_tag[0] == 0:
				self.remove_tag(id_tag)
		finally:
			self.close(conn, cursor)


	def remove_tag(self, id_tag):
		(conn, cursor) = self.open()
		try:
			#check if it works without adding a new index
			#index = db.get_VTA_index()
			cursor.execute(f''' 
				DELETE FROM "Tags"
				WHERE "Id" = {id_tag}
			; ''')
			conn.commit()
		finally:
			self.close(conn, cursor)	

	def get_tags(self):
		(conn, cursor) = self.open()
		try:
			return_json = []
			cursor.execute(f'''
				SELECT * FROM "Tags" 
			''')
			result = cursor.fetchall()

			for i in range(len(result)):
				return_json.append( Tag(result[i][0], result[i][1]).__dict__)

			return return_json
		finally:
			self.close(conn, cursor)	


	

####################### IMAGES #######################

	def get_images(self, id_user):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f''' 
				SELECT * FROM "Images" 
				left join "Users" on "Users"."Id" = "Images"."IdUser"
				WHERE "IdUser" = {id_user} 
				; 
			''')
			result = cursor.fetchall()
			conn.commit()
			return result
		finally:
			self.close(conn, cursor)

	def get_image_address(self, id_image:int):
		image = self.get_image(id_image)
		return f"{BASE_PATH}{image[1]}" 
	def get_thumbnail_address(self, IdThumbnail:int):
		thumbnail = self.get_thumbnail(IdThumbnail)
		return f"{BASE_PATH}{thumbnail[1]}" 



	def get_image(self, id_image:int):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f'''
				SELECT * FROM "Images"
				where "Images"."Id" = {str(id_image)}
			''')
			result = cursor.fetchone()
			return result
		finally:
			self.close(conn, cursor)	


	def get_network_images(self, id_user):
		images_ids_dict = []
		images = self.get_images(id_user)
		for i in range(len(images)):
			images_ids_dict.append( Image(images[i][0], images[i][5]).__dict__)

		return images_ids_dict

	def save_image(self, index, fileAddress, idUser, width, height, url):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f'''
			
				INSERT INTO "Images" ("Id", "ImageAddress", "IdUser", "Height", "Width", "URL")
				VALUES({index},'{fileAddress}',{idUser}, {height}, {width}, '{url}') 
				RETURNING "Images"."Id";
			
			''' )
			conn.commit()
			result = cursor.fetchone()
			return result[0]
		finally:
			self.close(conn, cursor)
	

	def delete_image(self, id_image:int):
		(conn, cursor) = self.open()
		try:
			cursor.execute(f'''
			
				DELETE FROM "Images" 
				WHERE "Images"."Id" = {id_image};
				RETURNING count(*) "Images"
			
			''' )
			conn.commit()
			result = cursor.fetchone()
			if result == None:
				return "No rows deleted"
			return result
		finally:
			self.close(conn, cursor)
		

db = DBWrapper()
#db.connPool._closeall()








