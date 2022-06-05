class Video():
	def __init__ (self,id, url, thumbnailUrl, duration, user,tags):
		self.id = id
		self.url = url
		self.thumbnail = thumbnailUrl
		self.duration = duration
		self.user = user
		
		if tags[0]['id']!= None:
			self.tags = tags
		else:
			self.tags = []

class Tag():
	def __init__ (self,id, value):
		self.id = id
		self.value = value

class Image():
	def __init__(self, id, url):
		self.id = id
		self.url = url