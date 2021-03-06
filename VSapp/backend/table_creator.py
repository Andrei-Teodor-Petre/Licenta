
from DBWrapper import DBWrapper

def create_tables(cursor):
	
	cursor.execute(
		'''
			CREATE SCHEMA IF NOT EXISTS vsapp AUTHORIZATION postgres;
			set search_path = vsapp;

			-- vsapp."Tags" definition

			-- Drop table

			-- DROP TABLE vsapp."Tags";

			CREATE TABLE vsapp."Tags" (
				"Id" int4 NOT NULL,
				"Value" varchar NOT NULL,
				CONSTRAINT "Tags_pkey" PRIMARY KEY ("Id")
			);


			-- vsapp."Thumbnails" definition

			-- Drop table

			-- DROP TABLE vsapp."Thumbnails";

			CREATE TABLE vsapp."Thumbnails" (
				"Id" int4 NOT NULL,
				"ThumbnailAddress" varchar NOT NULL,
				"ThumbnailUrl" varchar NOT NULL,
				CONSTRAINT "Thumbnails_pkey" PRIMARY KEY ("Id")
			);


			-- vsapp."Users" definition

			-- Drop table

			-- DROP TABLE vsapp."Users";

			CREATE TABLE vsapp."Users" (
				"Id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY,
				"Username" varchar NOT NULL,
				"Password" varchar NOT NULL,
				"Email" varchar NOT NULL,
				"Role" int2 NOT NULL DEFAULT 0,
				"Token" varchar NULL,
				CONSTRAINT "PK_Users" PRIMARY KEY ("Id")
			);


			-- vsapp."Images" definition

			-- Drop table

			-- DROP TABLE vsapp."Images";

			CREATE TABLE vsapp."Images" (
				"Id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY,
				"ImageAddress" varchar NOT NULL,
				"IdUser" int4 NOT NULL,
				"Height" int4 NOT NULL,
				"Width" int4 NOT NULL,
				"URL" varchar NOT NULL,
				CONSTRAINT "PK" PRIMARY KEY ("Id"),
				CONSTRAINT "FK_users" FOREIGN KEY ("IdUser") REFERENCES vsapp."Users"("Id")
			);


			-- vsapp."Videos" definition

			-- Drop table

			-- DROP TABLE vsapp."Videos";

			CREATE TABLE vsapp."Videos" (
				"Id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY,
				"VideoAddress" varchar NOT NULL,
				"IdUser" int4 NOT NULL,
				"Duration" int4 NOT NULL,
				"Height" int4 NOT NULL,
				"Width" int4 NOT NULL,
				"URL" varchar NULL,
				"IdThumbnail" int4 NULL,
				"Size" float8 NULL,
				"DateAdded" date NULL,
				CONSTRAINT "Assets_pkey" PRIMARY KEY ("Id"),
				CONSTRAINT "FK_Thumbnail" FOREIGN KEY ("IdThumbnail") REFERENCES vsapp."Thumbnails"("Id") ON DELETE CASCADE,
				CONSTRAINT "Videos_IdUser_fkey" FOREIGN KEY ("IdUser") REFERENCES vsapp."Users"("Id")
			);


			-- vsapp."VideoTagsAssociations" definition

			-- Drop table

			-- DROP TABLE vsapp."VideoTagsAssociations";

			CREATE TABLE vsapp."VideoTagsAssociations" (
				"Id" int4 NOT NULL,
				"IdVideo" int4 NOT NULL,
				"IdTag" int4 NOT NULL,
				CONSTRAINT "PK_VTAssociations" PRIMARY KEY ("Id") INCLUDE ("IdVideo", "IdTag"),
				CONSTRAINT "FK_Tags" FOREIGN KEY ("IdTag") REFERENCES vsapp."Tags"("Id") ON DELETE CASCADE,
				CONSTRAINT "FK_Videos" FOREIGN KEY ("IdVideo") REFERENCES vsapp."Videos"("Id") ON DELETE CASCADE
			);
		'''
	)

db = DBWrapper()

(conn, cursor) = db.open()

try:
	create_tables(cursor)
finally:
	db.close()


