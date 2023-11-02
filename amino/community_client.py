
from .models.objects import profile
from .helpers import exceptions
from .client import Client
from .helpers.generators import timezone

from json import dumps, loads

from uuid import UUID
from os import urandom
from typing import BinaryIO, Union
from binascii import hexlify
from time import time as timestamp
from json_minify import json_minify
from base64 import b64encode

class CommunityClient(Client):

	"""
	***Community params***
		[!] Use any of the options to define a community
		[!!] One of the parameters is required

		int *comId* - Community ID
		str *community_link* - Community link
		str *aminoId* - community amino ID

	***account params***
		[!] Specify the profile parameter or after initializing the CommunityClient, log in to your account
		[!] CommunityClient(comId=123456).login(email="email", password="password")

		objects.profile *profile* - account profile (Client.login(email="email", password="password") -> objects.profile)

	***server settings***
		str *language* - Language for response from the server (Default: "en")
		str *user_agent* - user agent (Default: "Apple iPhone12,1 iOS v15.5 Main/3.12.2")
		bool *auto_user_agent* - Does each request generate a new user agent? (Default: False)
		str *deviceId* - device id (Default: None)
		bool *auto_device* - Does each request generate a new deviceId? (Default: False)
		str *certificate_path* - path to certificates (Default: None)
		dict *proxies* - proxies (Default: None)

	***socket settings***
		bool *socket_enabled* - Launch socket? (Default: True)
		bool *socket_debug* - Track the stages of a socket's operation? (Default: False)
		bool *socket_trace* - socket trace (Default: False)
		list *socket_whitelist_communities* - By passing a list of communities the socket will respond only to them (Default: None),
		bool *socket_old_message_mode* - The socket first writes all messages in a separate thread, and basically takes them from a list (Default: False)

	"""

	def __init__(self, comId: int = None, community_link: str = None, aminoId: str = None, profile: profile = None, language: str = "en", user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", auto_user_agent:  bool = False, deviceId: str = None, auto_device: bool = False, socket_enabled: bool = True, socket_debug: bool = False, socket_trace: bool = False, socket_whitelist_communities: list = None, socket_old_message_mode: bool = False, proxies: dict = None, certificate_path = None):
		Client.__init__(self, language=language, user_agent=user_agent, auto_user_agent=auto_user_agent, deviceId=deviceId, auto_device=auto_device, socket_enabled=socket_enabled, socket_debug=socket_debug, socket_trace=socket_trace, socket_whitelist_communities=socket_whitelist_communities, socket_old_message_mode=socket_old_message_mode, proxies=proxies, certificate_path=certificate_path)
		if profile:self.profile=profile

		if comId:
			self.comId=comId
		elif community_link:
			self.comId=self.get_from_link(community_link).comId
		elif aminoId:
			self.comId=self.get_from_link(f"http://aminoapps.com/c/{aminoId}").comId
		else:
			raise exceptions.NoCommunity("Provide a link to the community, comId or aminoId.")


#ACCOUNT=============================


	def check_in(self, tz: int = None) -> int:
		data = dumps({
			"timezone": tz if tz else timezone(),
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def repair_check_in(self, method: int = 1) -> int:
		#1 Coins
		#2 Amino+

		data = dumps({
			"timestamp": int(timestamp() * 1000),
			"repairMethod": str(method)
		})
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in/repair", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def lottery(self, tz: int = None) -> dict:
		data = dumps({
			"timezone": tz if tz else timezone(),
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/check-in/lottery", data=data, headers=self.get_headers(data=data))
		return response.json()["lotteryLog"]



	def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, chatRequestPrivilege: str = None, imageList: list = None, backgroundImage: str = None, backgroundColor: str = None, titles: list = None, defaultBubbleId: str = None) -> int:
		
		mediaList = list()
		data = {"timestamp": int(timestamp() * 1000)}

		if imageList is not None:
			for image, caption  in imageList:
				mediaList.append([100, self.upload_media(image, "image"), caption])
			data["mediaList"] = mediaList


		if nickname: data["nickname"] = nickname
		if icon: data["icon"] = self.upload_media(icon, "image")
		if content: data["content"] = content
		if chatRequestPrivilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
		if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

		if titles:
			_titles = list
			for titles, colors in titles:
				_titles.append({"title": titles, "color": colors})
			data["extensions"] = {"customTitles": _titles}
		data = dumps(data)

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True) -> int:


		data = dumps({"frameId": avatarId,
				"applyToAll": 1 if applyToAll is True else 0,
				"timestamp": int(timestamp() * 1000)
				})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/avatar-frame/apply", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def check_notifications(self) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/notification/checked", headers=self.get_headers())
		return response.status_code


	def delete_notification(self, notificationId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/notification/{notificationId}", headers=self.get_headers())
		return response.status_code


	def clear_notifications(self) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/notification", headers=self.get_headers())
		return response.status_code


	def get_notifications(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}", headers=self.get_headers())
		return response.json()["notificationList"]


	def get_notices(self, start: int = 0, size: int = 25):


		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}", headers=self.get_headers())
		return response.json()["noticeList"]


	def promotion(self, noticeId: str, type: str = "accept") -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/notice/{noticeId}/{type}", headers=self.get_headers())
		return response.status_code


	def send_active_obj(self, startTime: int = None, endTime: int = None, optInAdsFlags: int = 2147483647, tz: int = None, timers: list = None, timestamp: int = int(timestamp() * 1000)) -> int: 
		data = {"userActiveTimeChunkList": [{"start": startTime, "end": endTime}], "timestamp": timestamp, "optInAdsFlags": optInAdsFlags, "timezone": tz if tz else timezone()} 
		if timers: data["userActiveTimeChunkList"] = timers 
		data = json_minify(dumps(data))  

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/community/stats/user-active-time", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def online_status(self, status: str) -> int:

		if status.lower() not in ("on", "off"): raise exceptions.WrongType(status)
		data = dumps({
			"onlineStatus": 1 if status.lower() == "on" else 2,
			"duration": 86400,
			"timestamp": int(timestamp() * 1000)
		})
	
		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", data=data, headers=self.get_headers(data=data))
		return response.status_code

#COINS=============================

	def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None) -> int:

		if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))


		data = {
			"coins": coins,
			"tippingContext": {"transactionId": transactionId},
			"timestamp": int(timestamp() * 1000)
		}

		if blogId is not None: url = f"/x{self.comId}/s/blog/{blogId}/tipping"
		elif chatId is not None: url = f"/x{self.comId}/s/chat/thread/{chatId}/tipping"
		elif objectId is not None:
			data["objectId"] = objectId
			data["objectType"] = 2
			url = f"/x{self.comId}/s/tipping"
		else: raise exceptions.SpecifyType()

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=url, data=data, headers=self.get_headers(data=data))
		return response.status_code


	def thank_tip(self, chatId: str, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank", headers=self.get_headers())
		return response.status_code


	def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
		if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

		data = dumps({
			"paymentContext": {
				"transactionId": transactionId,
				"isAutoRenew": autoRenew
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/influencer/{userId}/subscribe", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def purchase(self, objectId: str, objectType: int, aminoPlus: bool = True, autoRenew: bool = False) -> int:
		data = dumps({'objectId': objectId,
				'objectType': objectType,
				'v': 1,
				"timestamp": int(timestamp() * 1000),
				"paymentContext": {
					'discountStatus': 1 if aminoPlus is True else 0,
					'discountValue': 1,
					'isAutoRenew': autoRenew
					}
				})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/store/purchase", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def get_store_chat_bubbles(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}", headers=self.get_headers()).json()
		del response["api:message"], response["api:statuscode"], response["api:duration"], response["api:timestamp"]
		return response

	def get_store_stickers(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}", headers=self.get_headers()).json()
		del response["api:message"], response["api:statuscode"], response["api:duration"], response["api:timestamp"]
		return response



#STICKERS=============================

	def get_sticker_pack_info(self, sticker_pack_id: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true", headers=self.get_headers())
		return response.json()["stickerCollection"]

	def get_sticker_packs(self) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection", headers=self.get_headers())
		return response.json()["stickerCollection"]

	def get_community_stickers(self) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/sticker-collection?type=community-shared", headers=self.get_headers())
		return response.json()

	def get_sticker_collection(self, collectionId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true", headers=self.get_headers())
		return response.json()["stickerCollection"]



#USERS=============================

	def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25) -> dict:

		if type.lower() not in ("recent", "banned", "featured", "leaders", "curators"):raise exceptions.WrongType(type)
		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile?type={type.lower()}&start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_online_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_online_favorite_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_user_info(self, userId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}", headers=self.get_headers())
		return response.json()["userProfile"]


	def get_user_following(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_user_followers(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_user_visitors(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_user_checkins(self, userId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/check-in/stats/{userId}?timezone={timezone()}", headers=self.get_headers())
		return response.json()


	def get_user_achievements(self, userId: str) -> dict:
	
		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/achievements", headers=self.get_headers())
		return response.json()["achievements"]


	def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}/achievements", headers=self.get_headers())
		return response.json()


	def add_to_favorites(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-group/quick-access/{userId}", headers=self.get_headers())
		return response.status_code

	def follow(self, userId: Union[str, list]) -> int:

		if isinstance(userId, str):
			response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/member", headers=self.get_headers())
		elif isinstance(userId, list):
			data = dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
			response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/joined", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.WrongType(userId)
		return response.status_code

	def unfollow(self, userId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}", headers=self.get_headers())
		return response.status_code


	def block(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/block/{userId}", headers=self.get_headers())
		return response.status_code


	def unblock(self, userId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/block/{userId}", headers=self.get_headers())
		return response.status_code


	def visit(self, userId: str) -> int:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/user-profile/{userId}?action=visit", headers=self.get_headers())
		return response.status_code

	def get_leaderboard_info(self, type: str, start: int = 0, size: int = 25) -> dict:

		if "24" in type or "hour" in type: rankingType=1
		elif "7" in type or "day" in type: rankingType=2
		elif "rep" in type: rankingType=3
		elif "check" in type: rankingType=4
		elif "quiz" in type: rankingType=5
		else: raise exceptions.WrongType(type)

		response = self.make_request(method="GET", endpoint=f"/g/s-x{self.comId}/community/leaderboard?rankingType={rankingType}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]


	def get_blocked_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_blocker_users(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.get_headers())
		return response.json()["blockerUidList"]


	def search_users(self, nickname: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"{self.api}/s/user-profile?type=name&q={nickname}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["userProfileList"]

	def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, chatId: str = None, start: int = 0, size: int = 25) -> dict:

		if blogId or quizId:part=f"blog/{quizId if quizId else blogId}"
		elif wikiId:part=f"item/{wikiId}"
		elif chatId:part=f"chat/thread/{chatId}"
		elif fileId:part=f"shared-folder/files/{fileId}"
		else: raise exceptions.SpecifyType()

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/{part}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.get_headers())
		return response.json()

	def get_chat_users(self, chatId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.get_headers())
		return response.json()["memberList"]


#CHAT=============================

	def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False) -> dict:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType(type(userId))

		data = {
			"title": title,
			"inviteeUids": userIds,
			"initialMessageContent": message,
			"content": content,
			"timestamp": int(timestamp() * 1000)
		}

		if isGlobal is True: data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"
		else: data["type"] = 0
		if publishToGlobal is True: data["publishToGlobal"] = 1
		else: data["publishToGlobal"] = 0

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread", data=data, headers=self.get_headers(data=data))
		return response.json()["thread"]


	def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None, icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None, coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None, fansOnly: bool = None) -> list:
		#TODO
		pass


	def invite_to_chat(self, userId: Union[str, list], chatId: str) -> int:

		if isinstance(userId, str): userIds = [userId]
		elif isinstance(userId, list): userIds = userId
		else: raise exceptions.WrongType(type(userId))

		data = dumps({
			"uids": userIds,
			"timestamp": int(timestamp() * 1000)
		})
		

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/invite", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def join_chat(self, chatId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers(content_type="application/x-www-form-urlencoded"))
		return response.status_code

	def leave_chat(self, chatId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.get_headers())
		return response.status_code

		
	def delete_chat(self, chatId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}", headers=self.get_headers())
		return response.status_code

	def get_chat_threads(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.get_headers())
		return response.json()["threadList"]

	def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["threadList"]


	def get_chat_thread(self, chatId: str):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}", headers=self.get_headers())
		return response.json()["thread"]


	def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"+ f"&pageToken={pageToken}" if pageToken else '', headers=self.get_headers())
		return response.json()


	def get_message_info(self, chatId: str, messageId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers()).json()
		return response["message"]


	def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None) -> int:

		if message is not None and file is None and mentionUserIds is not None:
			message = message.replace("<@", "‎‏").replace("@>", "‬‭")

		mentions = []
		if mentionUserIds:
			for mention_uid in mentionUserIds:
				mentions.append({"uid": mention_uid})

		if embedImage:
			embedImage = [[100, self.upload_media(embedImage, "image"), None]]

		data = {
			"type": messageType,
			"content": message,
			"clientRefId": int(timestamp() / 10 % 1000000000),
			"attachedObject": {
				"objectId": embedId,
				"objectType": embedType,
				"link": embedLink,
				"title": embedTitle,
				"content": embedContent,
				"mediaList": embedImage
			},
			"extensions": {"mentionedArray": mentions},
			"timestamp": int(timestamp() * 1000)
		}

		if replyTo: data["replyMessageId"] = replyTo

		if stickerId:
			data["content"] = None
			data["stickerId"] = stickerId
			data["type"] = 3

		if file:
			data["content"] = None
			if fileType == "audio":
				data["type"] = 2
				data["mediaType"] = 110

			elif fileType == "image":
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = "image/jpg"
				data["mediaUhqEnabled"] = True

			elif fileType == "gif":
				data["mediaType"] = 100
				data["mediaUploadValueContentType"] = "image/gif"
				data["mediaUhqEnabled"] = True

			else: raise exceptions.SpecifyType

			data["mediaUploadValue"] = b64encode(file.read()).decode()

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message", data=data, headers=self.get_headers(data=data))
		return response.status_code



	def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None) -> int:

		data = {
			"adminOpName": 102,
			"timestamp": int(timestamp() * 1000)
		}
		if asStaff and reason:data["adminOpNote"] = {"content": reason}
		data = dumps(data)

		if not asStaff:response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.get_headers())
		else:response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", data=data, headers=self.get_headers(data=data))
		return response.status_code



	def send_embed(self, link: str, image: BinaryIO, message: str, chatId: str) -> int:
		data = dumps({
			"type": 0,
			"content": message,
			"extensions": {
				"linkSnippetList": [{
					"link": link,
					"mediaType": 100,
					"mediaUploadValue": b64encode(image.read()).decode(),
					"mediaUploadValueContentType": "image/png"
				}]
			},
				"clientRefId": int(timestamp() / 10 % 100000000),
				"timestamp": int(timestamp() * 1000),
				"attachedObject": None
		})
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/message", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def mark_as_read(self, chatId: str, messageId: str) -> int:

		data = dumps({
			"messageId": messageId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def transfer_host(self, chatId: str, userIds: list) -> int:
		data = dumps({
			"uidList": userIds,
			"timestamp": int(timestamp() * 1000)
		})


		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code


	def accept_host(self, chatId: str, requestId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code


	def kick(self, userId: str, chatId: str, allowRejoin: bool = True) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={1 if allowRejoin else 0}", headers=self.get_headers())
		return response.status_code



	def invite_to_vc(self, chatId: str, userId: str) -> int:

		data = dumps({"uid": userId})
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def change_vc_permission(self, chatId: str, permission: int) -> int:

		data = dumps({
			"vvChatJoinType": permission,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", headers=self.get_headers())
		return response.status_code


	def get_vc_reputation_info(self, chatId: str) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.get_headers())
		return response.json()

	def claim_vc_reputation(self, chatId: str) -> dict:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.get_headers())
		return response.json()



	def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False) -> int:
		data = dumps({
			"applyToAll": 1 if applyToAll is True else 0,
			"bubbleId": bubbleId,
			"threadId": chatId,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/chat/thread/apply-bubble", data=data, headers=self.get_headers(data=data))
		return response.json()




#BLOGS AND ECT=============================


	def post_blog(self, title: str, content: str, imageList: list = None, captionList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None, crash: bool = False) -> int:
		mediaList = []

		if captionList is not None and imageList is not None:
			for image, caption in zip(imageList, captionList):
				mediaList.append([100, self.upload_media(image, "image"), caption])

		else:
			if imageList is not None:
				for image in imageList:
					print(self.upload_media(image, "image"))
					mediaList.append([100, self.upload_media(image, "image"), None])

		data = {
			"address": None,
			"content": content,
			"title": title,
			"mediaList": mediaList,
			"extensions": extensions,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "GlobalComposeMenu",
			"timestamp": int(timestamp() * 1000)
		}
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList
		data = dumps(data)
		
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog", data=data, headers=self.get_headers(data=data))
		return response.json()

	def post_wiki(self, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, fansOnly: bool = False) -> int:
		mediaList = []

		for image in imageList:
			mediaList.append([100, self.upload_media(image, "image"), None])

		data = {
			"label": title,
			"content": content,
			"mediaList": mediaList,
			"eventSource": "GlobalComposeMenu",
			"timestamp": int(timestamp() * 1000)
		}
		if icon: data["icon"] = icon
		if keywords: data["keywords"] = keywords
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		data = dumps(data)

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/item", data=data, headers=self.get_headers(data=data))
		return response.json()


	def edit_blog(self, blogId: str, title: str = None, content: str = None, imageList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False) -> int:
		mediaList = []

		for image in imageList:
			mediaList.append([100, self.upload_media(image, "image"), None])

		data = {
			"address": None,
			"mediaList": mediaList,
			"latitude": 0,
			"longitude": 0,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		}
		if title: data["title"] = title
		if content: data["content"] = content
		if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
		if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
		if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList
		data = dumps(data)

		response = self.make_request(method="POST", endpoint=f"/s/blog/{blogId}", data=data, headers=self.get_headers(data=data))
		return response.json()


	def delete_blog(self, blogId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/blog/{blogId}", headers=self.get_headers())
		return response.json()


	def delete_wiki(self, wikiId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/item/{wikiId}", headers=self.get_headers())
		return response.json()

	def repost_blog(self, content: str = None, blogId: str = None, wikiId: str = None) -> int:

		if blogId is None and  wikiId is None: raise exceptions.SpecifyType()
		data = dumps({
			"content": content,
			"refObjectId": blogId if blogId else wikiId,
			"refObjectType": 1 if blogId else 2,
			"type": 2,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/blog", data=data, headers=self.get_headers(data=data))
		return response.json()


	def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, asGuest: bool = False) -> int:

		data = {
			"flagType": flagType,
			"message": reason,
			"timestamp": int(timestamp() * 1000)
		}
		if userId:
			data["objectId"] = userId
			data["objectType"] = 0
		elif blogId:
			data["objectId"] = blogId
			data["objectType"] = 1
		elif wikiId:
			data["objectId"] = wikiId
			data["objectType"] = 2
		else: raise exceptions.SpecifyType

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/{'g-flag' if asGuest else 'flag'}", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None) -> dict:


		if fileId:part=f"shared-folder/files/{fileId}"
		elif blogId or quizId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/{part}", headers=self.get_headers()).json()
		return response.get("file", response)


	def get_comments(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25):

		if sorting.lower() not in ("newest", "oldest", "vote"): raise exceptions.WrongType(sorting)
		if fileId:part=f"shared-folder/files/{fileId}"
		elif blogId or quizId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		elif userId:part=f"user-profile/{userId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/{part}/comment?sort={sorting}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["commentList"]

	def get_saved_blogs(self, start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/bookmark?start={start}&size={size}", headers=self.get_headers())
		return response.json()["bookmarkList"]



	def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):
	
		response = self.make_request(method="GET", endpoint=f"x{self.comId}/s/feed/blog-all?pagingType=t&{ f'pageToken={pageToken}' if pageToken else f'start={start}'}&size={size}", headers=self.get_headers())
		return response.json()

	def get_blog_categories(self, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/blog-category?size={size}", headers=self.get_headers())
		return response.json()["blogCategoryList"]


	def get_blogs_by_category(self, categoryId: str,start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}", headers=self.get_headers())
		return response.json()["blogList"]

	def get_recent_wiki_items(self, start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}", headers=self.get_headers())
		return response.json()["itemList"]

	def get_wiki_categories(self, start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/item-category?start={start}&size={size}", headers=self.get_headers())
		return response.json()["itemCategoryList"]


	def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/item-category/{categoryId}?start={start}&size={size}", headers=self.get_headers())
		return response.json()


	def get_shared_folder_info(self):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/shared-folder/stats", headers=self.get_headers())
		return response.json()["stats"]

	def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["fileList"]


	def comment(self, message: str = None, stickerId: str = None, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False) -> int:

		data = {
			"content": message,
			"stickerId": stickerId,
			"type": 0,
			"timestamp": int(timestamp() * 1000)
		}
		if replyTo: data["respondTo"] = replyTo
		if userId:
			data["eventSource"] = "UserProfileView"
			part=f"user-profile/{userId}"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			part=f"blog/{blogId}"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/{part}/{'g-comment' if isGuest else 'comment'}", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		if userId:part=f"user-profile/{userId}"
		elif blogId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/{part}/g-comment/{commentId}", headers=self.get_headers())
		return response.status_code


	def vote_poll(self, blogId: str, optionId: str) -> int:
		data = dumps({
			"value": 1,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		})
		

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None) -> int:

		data = {
			"value": 4,
			"timestamp": int(timestamp() * 1000)
		}

		if blogId:
			if isinstance(blogId, str):
				data["eventSource"] = "UserProfileView"
				data = dumps(data)
				response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/g-vote?cv=1.2", data=data, headers=self.get_headers(data=data))
			elif isinstance(blogId, list):
				data["targetIdList"] = blogId
				data = dumps(data)
				response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/feed/g-vote", data=data, headers=self.get_headers(data=data))
			else: raise exceptions.WrongType(type(blogId))

		elif wikiId:
			data["eventSource"] = "PostDetailView"
			data = dumps(data)
			response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/item/{wikiId}/g-vote?cv=1.2", data=data, headers=self.get_headers(data=data))
		else: raise exceptions.SpecifyType()
		return response.status_code


	def unlike_blog(self, blogId: str = None, wikiId: str = None) -> int:

		if blogId: url=f"/x{self.comId}s/blog/{blogId}/g-vote?eventSource=UserProfileView"
		elif wikiId: url=f"/x{self.comId}/s/item/{wikiId}/g-vote?eventSource=PostDetailView"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="POST", endpoint=url, headers=self.get_headers())
		response.status_code

	def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		data = {
			"value": 1,
			"timestamp": int(timestamp() * 1000)
		}
		if userId:
			data["eventSource"] = "UserProfileView"
			part=f"user-profile/{userId}"
		elif blogId:
			data["eventSource"] = "PostDetailView"
			part=f"blog/{blogId}"
		elif wikiId:
			data["eventSource"] = "PostDetailView"
			part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		data = dumps(data)
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/{part}/comment/{commentId}/g-vote?cv=1.2&value=1", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None) -> int:

		if userId:part=f"user-profile/{userId}"
		elif blogId:part=f"blog/{blogId}"
		elif wikiId:part=f"item/{wikiId}"
		else: raise exceptions.SpecifyType

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/{part}/comment/{commentId}/g-vote?eventSource={'UserProfileView' if userId else 'PostDetailView'}", headers=self.get_headers())
		return response.status_code

	def upvote_comment(self, blogId: str, commentId: str) -> int:
		data = dumps({
			"value": 1,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def downvote_comment(self, blogId: str, commentId: str) -> int:
		data = dumps({
			"value": -1,
			"eventSource": "PostDetailView",
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def unvote_comment(self, blogId: str, commentId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView", headers=self.get_headers())
		return response.status_code


	def play_quiz_raw(self, quizId: str, quizAnswerList: list, quizMode: int = 0) -> int:
		data = dumps({
			"mode": quizMode,
			"quizAnswerList": quizAnswerList,
			"timestamp": int(timestamp() * 1000)
		})
		
		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/blog/{quizId}/quiz/result", data=data, headers=self.get_headers(data=data))
		return response.status_code


	def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = 0) -> int:
		
		quizAnswerList = []
		for question, answer in zip(questionIdsList, answerIdsList):
			part = dumps({
				"optIdList": [answer],
				"quizQuestionId": question,
				"timeSpent": 0.0
			})
			quizAnswerList.append(loads(part))
		return self.play_quiz_raw(quizId=quizId, quizAnswerList=quizAnswerList, quizMode=quizMode)

	def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}", headers=self.get_headers())
		return response.json()


#STAFF=============================

	def edit_community(self, name: str = None, description: str = None, aminoId: str = None, primaryLanguage: str = None, themePackUrl: str = None) -> int:
		data = {"timestamp": int(timestamp() * 1000)}

		if name is not None: data["name"] = name
		if description is not None: data["content"] = description
		if aminoId is not None: data["endpoint"] = aminoId
		if primaryLanguage is not None: data["primaryLanguage"] = primaryLanguage
		if themePackUrl is not None: data["themePackUrl"] = themePackUrl
		data = dumps(data)

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/community/settings", data=data, headers=self.get_headers(data=data))
		return response.status_code
	
	def upload_themepack(self, file: BinaryIO) -> dict:

		response = self.make_request(method="POST", endpoint=f"/s/media/upload/target/community-theme-pack", data=file.read(), headers=self.get_headers(data=file.read()))
		return response.json()


	def get_moderation_history(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, size: int = 25):


		if userId: part=f"?objectId={userId}&objectType=0&"
		elif blogId: part=f"?objectId={blogId}&objectType=1&"
		elif quizId: part=f"?objectId={quizId}&objectType=1&"
		elif wikiId: part=f"?objectId={wikiId}&objectType=2&"
		elif fileId: part=f"?objectId={fileId}&objectType=109&"
		else: part=f"?"

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/admin/operation{part}pagingType=t&size={size}", headers=self.get_headers())
		return response.json()["adminLogList"]



	def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}", headers=self.get_headers())
		return response.json()["communityInvitationList"]

	def generate_invite_code(self, duration: int = 0, force: bool = True) -> dict:
		data = dumps({
			"duration": duration,
			"force": force,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/g/s-x{self.comId}/community/invitation", data=data, headers=self.get_headers(data=data))
		return response.json()["communityInvitation"]


	def delete_invite_code(self, inviteId: str) -> int:

		response = self.make_request(method="DELETE", endpoint=f"/g/s-x{self.comId}/community/invitation/{inviteId}", headers=self.get_headers())
		return response.status_code


	def get_join_requests(self, start: int = 0, size: int = 25) -> dict:

		response = self.make_request(method="GET", endpoint=f"/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}", headers=self.get_headers())
		return response.status_code

	def accept_join_request(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/community/membership-request/{userId}/accept", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code

	def reject_join_request(self, userId: str):

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/community/membership-request/{userId}/reject", data=dumps({}), headers=self.get_headers(data=dumps({})))
		return response.status_code


	def edit_titles(self, userId: str, titles: list) -> dict:

		_titles = list()
		for titles, colors in titles:
			_titles.append({"title": titles, "color": colors})

		data = dumps({
			"adminOpName": 207,
			"adminOpValue": {
				"titles": _titles
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/admin", data=data, headers=self.get_headers(data=data))
		return response.json()


	def ban(self, userId: str, reason: str, banType: int = None) -> dict:

		data = dumps({
			"reasonType": banType,
			"note": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/ban", data=data, headers=self.get_headers(data=data))
		return response.json()


	def unban(self, userId: str, reason: str) -> dict:
		data = dumps({
			"note": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/unban", data=data, headers=self.get_headers(data=data))
		return response.json()


	def hide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None) -> dict:

		data = {
			"adminOpNote": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		}
		if userId:data["adminOpName"] = 18
		else:
			data["adminOpName"] = 110
			data["adminOpValue"] = 9
		data = dumps(data)		

		if userId:part = f"user-profile/{userId}"
		elif blogId or quizId:part = f"blog/{blogId or quizId}"
		elif wikiId:part = f"item/{wikiId}"
		elif chatId:part = f"chat/thread/{chatId}"
		elif fileId:part = f"shared-folder/files/{fileId}"
		else: raise exceptions.SpecifyType()

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/{part}/admin", data=data, headers=self.get_headers(data=data))
		return response.json()


	def unhide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None) -> dict:

		data = {
			"adminOpNote": {
				"content": reason
			},
			"timestamp": int(timestamp() * 1000)
		}
		if userId:data["adminOpName"] = 19
		else:
			data["adminOpName"] = 110
			data["adminOpValue"] = 0
		data = dumps(data)		

		if userId:part = f"user-profile/{userId}"
		elif blogId or quizId:part = f"blog/{blogId or quizId}"
		elif wikiId:part = f"item/{wikiId}"
		elif chatId:part = f"chat/thread/{chatId}"
		elif fileId:part = f"shared-folder/files/{fileId}"
		else: raise exceptions.SpecifyType()

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/{part}/admin", data=data, headers=self.get_headers(data=data))
		return response.json()


	def increase_rank(self, userId: str, rank: str) -> int:
		rank = rank.lower().replace("agent", "transfer-agent")
		if rank.lower() not in ("transfer-agent", "leader", "curator"):raise exceptions.WrongType(rank)

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/user-profile/{userId}/{rank}", headers=self.get_headers())
		return response.status_code

	def add_influencer(self, userId: str, monthlyFee: int) -> int:
		data = dumps({
			"monthlyFee": monthlyFee,
			"timestamp": int(timestamp() * 1000)
		})

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/influencer/{userId}", data=data, headers=self.get_headers(data=data))
		return response.status_code

	def remove_influencer(self, userId: str) -> int:

		response = self.make_request(method="POST", endpoint=f"/x{self.comId}/s/influencer/{userId}", headers=self.get_headers())
		return response.status_code


	def delete_community(self, email: str, password: str, verificationCode: str) -> int:

		deviceId = self.deviceId
		data = dumps({
			"secret": f"0 {password}",
			"validationContext": {
				"data": {
					"code": verificationCode
				},
				"type": 1,
				"identity": email
			},
			"deviceID": deviceId
		})

		response = self.make_request(method="POST", endpoint=f"/g/s-x{self.comId}/community/delete-request", data=data, headers=self.get_headers(data=data, deviceId=deviceId))
		return response.status_code




#OTHER=============================

	def get_live_layer(self) -> dict:

		response = self.make_request(method="GET", endpoint=f"/s/live-layer/homepage?v=2", headers=self.get_headers())
		return response.json()["liveLayerList"]