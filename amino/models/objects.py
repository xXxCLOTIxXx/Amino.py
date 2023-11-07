from ..helpers.types import renamed

class ObjectCreator:
	def __init__(self, data = {}):
		self.json = self.add_standard_keys(data)

	@property
	def value(self):
		return self.json

	@property
	def type(self):
		return type(self.json)

	def get(self, key, default = None):
		if isinstance(self.json, dict):return self.json.get(key, default)
		raise Exception("Object is not a dictionary.")


	def add_standard_keys(self, data: dict):
		for i in renamed.keys():
			if i in data.keys():
				data[renamed.get(i)] = data.get(i)
		return data


	def class_wrapper(self, data):
		if isinstance(data, dict):
			return self.__class__(self.add_standard_keys(data))
		if isinstance(data, list):
			temp = list()
			for i in data:
				temp.append(self.class_wrapper(i))
			return temp

		return data


	def __getattr__(self, item: str):
		return self.class_wrapper(self.json.get(item))

	def __repr__(self):
		return repr(self.json)