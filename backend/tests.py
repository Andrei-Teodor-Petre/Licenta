import unittest
import utils
import subprocess
from constants import BASE_PATH
from PIL import Image


class TestThumbnailMethods(unittest.TestCase):


	def test_create_thumbnail(self):
		#on upload this will call the ffmpeg library function and create a thumbnail for the video

		video_addr = f""f"{BASE_PATH}/Videos/video-{str(1)}.mov"
		image_address = f"{BASE_PATH}/Thumbnails/thumbnail-{str(1)}.jpeg"
		subprocess.call(['ffmpeg', '-y', '-i', video_addr, '-ss', '00:00:00.000', '-vframes', '1', image_address])
		thumbnail = Image.open(image_address)
		self.assertEqual((f"/Thumbnails/thumbnail-{str(1)}.jpeg", thumbnail.width, thumbnail.height), utils.create_thumbnail(video_addr,1))

	# def test_upper(self):
	# 	self.assertEqual('foo'.upper(), 'FOO')

	# def test_isupper(self):
	# 	self.assertTrue('FOO'.isupper())
	# 	self.assertFalse('Foo'.isupper())

	# def test_split(self):
	# 	s = 'hello world'
	# 	self.assertEqual(s.split(), ['hello', 'world'])
	# 	# check that s.split fails when the separator is not a string
	# 	with self.assertRaises(TypeError):
	# 		s.split(2)

if __name__ == '__main__':
	unittest.main()