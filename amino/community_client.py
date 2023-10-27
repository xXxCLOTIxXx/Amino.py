
from .helpers.objects import profile
from .utils.exceptions import NoCommunity
from .client import Client

class LocalClient(Client):
	def __init__(self, comId: int = None, community_link: str = None, aminoId: str = None, profile: profile = None, user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", deviceId: str = None, auto_device: bool = False, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Client.__init__(self, user_agent=user_agent, deviceId=deviceId, auto_device=auto_device, socket_enabled=socket_enabled, socket_debug=socket_debug, socket_trace=socket_trace, socket_whitelist_communities=socket_whitelist_communities, socket_old_message_mode=socket_old_message_mode, proxies=proxies, certificate_path=certificate_path)
		if profile:self.profile=profile

		if comId:
			self.comId=comId
		elif community_link:
			self.comId=self.get_from_link(community_link).comId
		elif aminoId:
			self.comId=self.get_from_link(f"http://aminoapps.com/c/{aminoId}").comId
		else:
			raise NoCommunity("Provide a link to the community, comId or aminoId.")
	

	def online(self):
		self.online_list.add(self.comId)

	def offline(self):
		try:self.online_list.remove(self.comId)
		except KeyError:pass