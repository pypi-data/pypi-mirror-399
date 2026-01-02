from abc import ABC, abstractmethod
import random
from typing import Literal

#抽象类: 信息(发送)
class Message(ABC):
    def __init__(self): pass
    @abstractmethod
    def to_dict(self): return {}
    @abstractmethod
    def returnData(self): return []

# 文字信息
class TextMessage(Message):

    text = ""

    def __init__(self, data: str):
        if len(data) > 500:
            raise ValueError("内容过长")
        self.text = data
    
    def to_dict(self):
        msg = {
            "type": "text",
            "data": {
                "text": self.text
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 回复信息
class ReplyMessage(Message):

    message_id: int

    def __init__(self, message_id: int):
        self.message_id = message_id
    
    def to_dict(self):
        msg = {
            "type": "reply",
            "data": {
                "id": self.message_id
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 图片信息
class ImageMessage(Message):

    data: str

    def __init__(self,  data: str):
        self.data = data
    
    def to_dict(self):
        msg = {
            "type": "image",
            "data": {
                "file": self.data
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 表情信息
class EmojiMessage(Message):

    data: str

    def __init__(self,  id: str):
        self.id = id
    
    def to_dict(self):
        msg = {
            "type": "face",
            "data": {
                "id": self.id
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 语音信息
class RecordMessage(Message):

    data: str

    def __init__(self,  data: str):
        self.data = data
    
    def to_dict(self):
        msg = {
            "type": "record",
            "data": {
                "file": self.data
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 视频信息
class VideoMessage(Message):

    data: str

    def __init__(self,  data: str):
        self.data = data
    
    def to_dict(self):
        msg = {
            "type": "video",
            "data": {
                "file": self.data
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 超级表情: 骰子信息
class DiceMessage(Message):

    result: int

    def __init__(self, result: int = None):
        self.result = result
    
    def to_dict(self):
        if self.result == None:
            self.result = random.randint(1,6)
        msg = {
            "type": "dice",
            "data": {
                "result": self.result
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 超级表情: 猜拳信息
class RPSMessage(Message):

    def __init__(self): pass
    
    def to_dict(self):
        msg = {
            "type": "rps",
            "data": {}
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# QQ音乐卡片信息
class QQMusicMessage(Message):

    id: int

    def __init__(self, id: int):
        self.id = id
    
    def to_dict(self):
        msg = {
            "type": "music",
            "data": {
                "type": "qq",
                "id": self.id
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 网易云音乐卡片信息
class Music163Message(Message):

    id: int

    def __init__(self, id: int):
        self.id = id
    
    def to_dict(self):
        msg = {
            "type": "music",
            "data": {
                "type": "163",
                "id": self.id
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 自定义音乐卡片信息
class CustomMusicMessage(Message):

    url: str
    audio: str
    title: str
    image: str

    def __init__(self, url: str, audio: str, title: str, image: str):
        self.url = url
        self.audio = audio
        self.title = title
        self.image = image
    
    def to_dict(self):
        msg = {
            "type": "music",
            "data": {
                "type": "custom",
                "audio": self.url,
                "audio": self.audio,
                "title": self.title,
                "image": self.image
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 卡片信息
class PrivateCardMessage(Message):

    data: str

    def __init__(self, data: str):
        self.data = data
    
    def to_dict(self):
        msg = {
            "type": "json",
            "data": {
                "data": self.data
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 合并转发信息
class PrivateCardMessage(Message):

    data: Message

    def __init__(self, data: Message):
        self.data = data
    
    def to_dict(self):
        msg = {
            "type": "json",
            "data": {
                "content": self.data.returnData()
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# @信息
class AtMessage(Message):

    qq: str

    def __init__(self, qq: int | Literal["all"]):
        if type(qq) == int:
            qq = str(qq)
        self.qq = qq
    
    def to_dict(self):
        msg = {
            "type": "at",
            "data": {
                "qq": self.qq
            }
        }
        return msg

    def returnData(self):
        return [self.to_dict()]
    
# 信息链
class MessageChain(Message):
    
    data: list[dict]

    def __init__(self, data: list[Message|str] = []):
        temp = []
        for msg in data:
            if type(msg) == str:
                msg = TextMessage(msg)
            msg = msg.to_dict()
            temp.append(msg)
        self.data = temp

    def add(self, message):
        if type(message) == str:
            message = TextMessage(message)
        self.data.extend(message.returnData())
    
    def to_dict(self):
        return {}

    def returnData(self):
        return self.data
