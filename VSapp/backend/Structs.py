class Video():
	def __init__ (self,id, url, thumbnailUrl, duration, user, width, height, size, dateAdded, tags):
		self.id = id
		self.url = url
		self.thumbnail = thumbnailUrl
		self.duration = duration
		self.user = user
		self.width = width
		self.height = height
		self.size = size
		self.dateAdded = dateAdded
		
		
		if len(tags) > 0:
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

class User:
	def __init__(self, id, username, token):
		self.id = id
		self.name = username
		self.token = token
		