class Video():
	def __init__ (self,id, url, thumbnailUrl, duration):
		self.id = id
		self.url = url
		self.thumbnail = thumbnailUrl
		self.duration = duration

class Image():
	def __init__(self, id, url):
		self.id = id
		self.url = url