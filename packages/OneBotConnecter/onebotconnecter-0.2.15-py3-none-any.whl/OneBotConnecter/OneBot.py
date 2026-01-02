#import
try:
    from OneBotConnecter.MessageType import Message, ReplyMessage, AtMessage, MessageChain
except:
    print("File [OneBotMessageType.py] missing")
    raise Exception()
from typing import Literal
import os
moduleList = ["traceback", "asyncio", "json", "websockets"]
for module in moduleList:
    try:
        exec(f"import {module}")
    except:
        os.system("pip install " + module)
        exec(f"import {module}")

#bedug function for None input
def _on_message(bot, message):
    print(message)

#机器人接口连接
class OneBot:
    _uri: str = None #机器人地址
    bot = None #连接本体
    owner: list[str] = None #机器人管理员
    botName: list[str] = None #机器人名称
    localtion: str = None #机器人地址
    nickname: str = []
    botAcc: int = None
    testMode = False #调试模式
    #构造体
    def __init__(self, uri: str, owner: list[str] = None, botName: list[str] = None, localtion: str = None, testMode = False):
        self._uri = uri
        if owner != None: self.owner = owner
        else: print("[W]: Owner input is None")
        if botName != None: self.botName = botName
        else: print("[W]: Bot Name input is None")
        if localtion != None: self.localtion = localtion.replace("\\", "/")
        else: print("[W]: Main file location input is None")
        self.testMode = testMode
    #建立连接 (WS正向)
    async def run(self, on_message: __module__ = _on_message, sleep_time: int = 1):
        while self.bot == None:
            try: self.bot = await websockets.connect(self._uri)
            except: await asyncio.sleep(1)
        if self.bot != None:
            self.bot = await websockets.connect(self._uri)
            message = await self.bot.recv()
            print(f"\n地址{self._uri}连接已完成")
            await self.get_login_info()
            print(f"机器人账号: {self.botAcc}")
            print(f"机器人名称: {self.botName}")
            if self.owner != None: print(f"机器人管理员: {self.owner}")
            if self.localtion != None: print(f"机器人根目录地址: {self.localtion}")
            print(f"开始监听机器人信息推送\n")
            while True:
                if self.bot == None:
                    try:
                        self.bot = await websockets.connect(self._uri)
                    except:
                        print("连接失败，5秒后重试\n")
                        await asyncio.sleep(5)
                if self.bot != None:
                    task = asyncio.create_task(self._receive_messages(on_message))
                    try:
                        result = task.result()
                    except Exception:
                        if self.testMode: traceback.print_exc()
                    await asyncio.sleep(sleep_time)

    #收到信息时
    async def _receive_messages(self, callback: __module__):
        try:
            message = await self.bot.recv()
            message = json.loads(message)
            try:
                if message["post_type"] != "meta_event" and self.bot != None:
                    try:
                        await callback(self, message)
                    except Exception as e:
                        traceback.print_exc()
            except:
                print(f"{message}\n")
        except websockets.exceptions.ConnectionClosed:
            print("与机器人连接已断开\n")
            self.bot = None
        except: pass
    
    #为信息发送构造数据包
    def _createDataPack(self, action: str, params: dict):
        data = {
            "action": action,
            "params": params
        }
        return json.dumps(data)
    #把数据包发送至机器人端口，并收集处理结果
    async def _sendToServer(self, action: str, params: dict):
        datapack = self._createDataPack(action, params)
        if self.testMode:print(f"数据包发送: {datapack}")
        await self.bot.send(datapack)
        try:
            callback = await self.bot.recv()
            message = json.loads(callback)
            if self.testMode: print(f"数据包返回: {message}")
            return message
        except: return None
    #调试模式开关
    async def test(self, testMode: bool = False):
        self.testMode = testMode
    # =====------API------===== #
    # ------好友----- #
    #点赞
    async def send_like(self, user_id: int, times=1):
        params = {
            "user_id": user_id,
            "times": times
        }
        callback = await self._sendToServer("send_like", params)
        return callback
    #好友列表
    async def get_friend_list(self):
        params = {}
        callback = await self._sendToServer("get_friend_list", params)
        return callback
    #好友列表（带分组）
    async def get_friends_with_category(self):
        params = {}
        callback = await self._sendToServer("get_friends_with_category", params)
        return callback
    #删除好友
    async def delete_friend(self, user_id: int):
        params = {
            "user_id": user_id
        }
        callback = await self._sendToServer("delete_friend", params)
        return callback
    #处理好友申请
    async def set_friend_add_request(self, flag: str, approve: bool, remark: str = None):
        params = {
            "flag": flag,
            "approve": approve,
            "remark": remark
        }
        callback = await self._sendToServer("set_friend_add_request", params)
        return callback
    #设置好友备注
    async def set_friend_remark(self, user_id: int, remark: str = None):
        params = {
            "user_id": user_id,
            "remark": remark
        }
        callback = await self._sendToServer("set_friend_remark", params)
        return callback
    #获取好友或群友信息
    async def get_stranger_info(self, user_id: int):
        params = {
            "user_id": user_id
        }
        callback = await self._sendToServer("get_stranger_info", params)
        return callback
    #设置个人头像
    async def set_qq_avatar(self, file: int):
        params = {
            "file": file
        }
        callback = await self._sendToServer("set_qq_avatar", params)
        return callback
    #好友戳一戳
    async def friend_poke(self, user_id: int):
        params = {
            "user_id": user_id
        }
        callback = await self._sendToServer("friend_poke", params)
        return callback
    #获取我赞过谁列表
    async def get_profile_like(self, start: int=0, count: int=20):
        params = {
            "start": start,
            "count": count
        }
        callback = await self._sendToServer("get_profile_like", params)
        return callback
    #获取谁赞过我列表
    async def get_profile_like_me(self, start: int=0, count: int=20):
        params = {
            "start": start,
            "count": count
        }
        callback = await self._sendToServer("get_profile_like_me", params)
        return callback
    #获取官方机器人QQ号范围
    async def get_robot_uin_range(self):
        params = {}
        callback = await self._sendToServer("get_robot_uin_range", params)
        return callback
    #移动好友分组
    async def set_friend_category(self, user_id: int, category_id: int):
        params = {
            "user_id": user_id,
            "category_id": category_id
        }
        callback = await self._sendToServer("set_friend_category", params)
        return callback
    #获取QQ头像
    async def get_qq_avatar(self, user_id: int):
        params = {
            "user_id": user_id
        }
        callback = await self._sendToServer("get_qq_avatar", params)
        return callback
    #获取被过滤好友请求
    async def get_doubt_friends_add_request(self, count: int):
        params = {
            "count": count
        }
        callback = await self._sendToServer("get_doubt_friends_add_request", params)
        return callback
    #处理被过滤好友请求
    async def set_doubt_friends_add_request(self, flag: str):
        params = {
            "flag": flag
        }
        callback = await self._sendToServer("set_doubt_friends_add_request", params)
        return callback
    # ------群组----- #
    #群列表
    async def get_group_list(self, no_cache: bool = False):
        params = {
            "no_cache": no_cache
        }
        callback = await self._sendToServer("get_group_list", params)
        return callback
    #群详情
    async def get_group_info(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_group_info", params)
        return callback
    #群成员列表
    async def get_group_member_list(self, group_id: int, no_cache: bool = False):
        params = {
            "group_id": group_id,
            "no_cache": no_cache
        }
        callback = await self._sendToServer("get_group_member_list", params)
        return callback
    #获取群成员信息
    async def get_group_member_info(self, group_id: int, user_id: int, no_cache: bool = False):
        params = {
            "group_id": group_id,
            "user_id": user_id,
            "no_cache": no_cache
        }
        callback = await self._sendToServer("get_group_member_info", params)
        return callback
    #群员戳一戳
    async def group_poke(self, group_id: int, user_id: int):
        params = {
            "group_id": group_id,
            "user_id": user_id
        }
        callback = await self._sendToServer("group_poke", params)
        return callback
    #获取群系统消息
    async def get_group_system_msg(self):
        params = {}
        callback = await self._sendToServer("get_group_system_msg", params)
        return callback
    #处理加群请求
    async def set_group_add_request(self, flag: str, approve: bool = True, reason: str = " "):
        params = {
            "flag": flag,
            "approve": approve,
            "reason": reason
        }
        callback = await self._sendToServer("set_group_add_request", params)
        return callback
    #退群
    async def set_group_leave(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("set_group_leave", params)
        return callback
    #设置群管理员
    async def set_group_admin(self, group_id: int, user_id: int, enable: bool):
        params = {
            "group_id": group_id,
            "user_id": user_id,
            "enable": enable
        }
        callback = await self._sendToServer("set_group_admin", params)
        return callback
    #设置群名片
    async def set_group_card(self, group_id: int, user_id: int, card: str = " "):
        params = {
            "group_id": group_id,
            "user_id": user_id,
            "card": card
        }
        callback = await self._sendToServer("set_group_card", params)
        return callback
    #群禁言
    async def set_group_ban(self, group_id: int, user_id: int, duration: int = 0):
        params = {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration
        }
        callback = await self._sendToServer("set_group_ban", params)
        return callback
    #群全体禁言
    async def set_group_whole_ban(self, group_id: int, enable: bool = False):
        params = {
            "group_id": group_id,
            "enable": enable
        }
        callback = await self._sendToServer("set_group_whole_ban", params)
        return callback
    #获取被禁言群员列表
    async def get_group_shut_list(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_group_shut_list", params)
        return callback
    #设置群名
    async def set_group_name(self, group_id: int, group_name: str):
        params = {
            "group_id": group_id,
            "group_name": group_name
        }
        callback = await self._sendToServer("set_group_name", params)
        return callback
    #批量踢出群成员
    async def batch_delete_group_member(self, group_id: int, user_ids: list[int]):
        params = {
            "group_id": group_id,
            "user_ids": user_ids
        }
        callback = await self._sendToServer("batch_delete_group_member", params)
        return callback
    #批量踢出群成员
    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool = False):
        params = {
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": reject_add_request
        }
        callback = await self._sendToServer("set_group_kick", params)
        return callback
    #设置群头衔
    async def set_group_special_title(self, group_id: int, user_id: int, special_title: str = " "):
        params = {
            "group_id": group_id,
            "user_id": user_id,
            "special_title": special_title
        }
        callback = await self._sendToServer("set_group_special_title", params)
        return callback
    #群荣誉
    async def get_group_honor_info(self, group_id: int, type: Literal["all","talkative","performer","legend","strong_newbie","emotion"] = "all"):
        params = {
            "group_id": group_id,
            "type": type
        }
        callback = await self._sendToServer("get_group_honor_info", params)
        return callback
    #获取群精华消息
    async def get_essence_msg_list(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_essence_msg_list", params)
        return callback
    #设置群精华消息
    async def get_essenset_essence_msgce_msg_list(self, message_id: int):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("set_essence_msg", params)
        return callback
    #删除群精华消息
    async def delete_essence_msg(self, message_id: int):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("delete_essence_msg", params)
        return callback
    #获取群 @全体成员 剩余次数
    async def get_group_at_all_remain(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_group_at_all_remain", params)
        return callback
    #发送群公告
    async def send_group_notice(self, group_id: int, content: str = "默认公告测试", image: str = None):
        params = {
            "group_id": group_id,
            "content": content,
            "image": image
        }
        callback = await self._sendToServer("_send_group_notice", params)
        return callback
    #获取群公告
    async def get_group_notice(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("_get_group_notice", params)
        return callback
    #群打卡
    async def send_group_sign(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("send_group_sign", params)
        return callback
    #设置群消息接收方式
    async def set_group_msg_mask(self, group_id: int, mask: Literal[1,2,3,4] = 1):
        params = {
            "group_id": group_id,
            "mask": mask
        }
        callback = await self._sendToServer("set_group_msg_mask", params)
        return callback
    #设置群备注
    async def set_group_remark(self, group_id: int, remark: str = " "):
        params = {
            "group_id": group_id,
            "remark": remark
        }
        callback = await self._sendToServer("set_group_remark", params)
        return callback
    #获取已过滤的加群通知
    async def get_group_ignore_add_request(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_group_ignore_add_request", params)
        return callback
    # ------消息----- #
    #发送私聊消息
    async def send_private_msg(self, user_id: int, message: Message):
        params = {
            "user_id": user_id,
            "message": message.returnData()
        }
        callback = await self._sendToServer("send_private_msg", params)
        return callback
    #发送群聊消息
    async def send_group_msg(self, group_id: int, message: Message):
        params = {
            "group_id": group_id,
            "message": message.returnData()
        }
        callback = await self._sendToServer("send_group_msg", params)
        return callback
    #长连接接收消息
    async def events(self):
        params = {}
        callback = await self._sendToServer("_events", params)
        return callback
    #转发单条好友消息
    async def forward_friend_single_msg(self, message_id: int, user_id: int):
        params = {
            "message_id": message_id,
            "user_id": user_id
        }
        callback = await self._sendToServer("forward_friend_single_msg", params)
        return callback
    #转发单条群消息
    async def forward_group_single_msg(self, message_id: int, group_id: int):
        params = {
            "message_id": message_id,
            "group_id": group_id
        }
        callback = await self._sendToServer("forward_group_single_msg", params)
        return callback
    #获取消息详情
    async def get_msg(self, message_id: int):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("get_msg", params)
        return callback
    #撤回消息
    async def delete_msg(self, message_id: int):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("delete_msg", params)
        return callback
    #获取消息文件详情
    async def get_file(self, file: str):
        params = {
            "file": file
        }
        callback = await self._sendToServer("get_file", params)
        return callback
    #获取消息图片详情
    async def get_image(self, file: str):
        params = {
            "file": file
        }
        callback = await self._sendToServer("get_image", params)
        return callback
    #获取消息语音详情
    async def get_record(self, file: str, out_format: str = "mp3"):
        params = {
            "file": file,
            "out_format": out_format
        }
        callback = await self._sendToServer("get_record", params)
        return callback
    #表情回应消息
    async def set_msg_emoji_like(self, message_id: int, emoji_id: int):
        params = {
            "message_id": message_id,
            "emoji_id": emoji_id
        }
        callback = await self._sendToServer("set_msg_emoji_like", params)
        return callback
    #取消消息表情回应
    async def unset_msg_emoji_like(self, message_id: int, emoji_id: int):
        params = {
            "message_id": message_id,
            "emoji_id": emoji_id
        }
        callback = await self._sendToServer("unset_msg_emoji_like", params)
        return callback
    #获取好友历史消息记录
    async def get_friend_msg_history(self, user_id: int, message_seq: int = 0, count: int = 20):
        params = {
            "user_id": user_id,
            "message_seq": message_seq,
            "count": count
        }
        callback = await self._sendToServer("get_friend_msg_history", params)
        return callback
    #获取群历史消息
    async def get_group_msg_history(self, group_id: int, message_seq: int = 0, count: int = 20):
        params = {
            "group_id": group_id,
            "message_seq": message_seq,
            "count": count
        }
        callback = await self._sendToServer("get_group_msg_history", params)
        return callback
    #获取转发消息详情
    async def get_forward_msg(self, message_id: str):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("get_forward_msg", params)
        return callback
    #标记消息已读
    async def mark_msg_as_read(self, message_id: int):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("mark_msg_as_read", params)
        return callback
    #语音消息转文字
    async def voice_msg_to_text(self, message_id: int):
        params = {
            "message_id": message_id
        }
        callback = await self._sendToServer("voice_msg_to_text", params)
        return callback
    #发送群 Ai 语音
    async def send_group_ai_record(self, character: str, group_id: int, text: str):
        params = {
            "character": character,
            "group_id": group_id,
            "text": text
        }
        callback = await self._sendToServer("send_group_ai_record", params)
        return callback
    #回复指定信息
    async def reply_to_message(self, getMessage, sendMessage):
        try:
            group_id = getMessage["group_id"]
            user_id = getMessage["user_id"]
            message_id = getMessage["message_id"]
            msg = MessageChain([ReplyMessage(message_id), AtMessage(user_id), " "])
            msg.add(sendMessage)
            callback = await self.send_group_msg(group_id, msg)
        except:
            user_id = getMessage["user_id"]
            message_id = getMessage["message_id"]
            msg = MessageChain([ReplyMessage(message_id), " "])
            msg.add(sendMessage)
            callback = await self.send_private_msg(user_id, msg)
        return callback
    # ------文件----- #
    #上传群文件
    async def upload_group_file(self, group_id: int, file: str, name: str):
        params = {
            "group_id": group_id,
            "file": file,
            "name": name
        }
        callback = await self._sendToServer("upload_group_file", params)
        return callback
    #删除群文件
    async def delete_group_file(self, group_id: int, file_id: str):
        params = {
            "group_id": group_id,
            "file_id": file_id
        }
        callback = await self._sendToServer("delete_group_file", params)
        return callback
    #移动群文件
    async def move_group_file(self, group_id: int, file_id: str, parent_directory: str, target_directory: str):
        params = {
            "group_id": group_id,
            "file_id": file_id,
            "parent_directory": parent_directory,
            "target_directory": target_directory
        }
        callback = await self._sendToServer("move_group_file", params)
        return callback
    #创建群文件文件夹
    async def create_group_file_folder(self, group_id: int, name: str):
        params = {
            "group_id": group_id,
            "name": name
        }
        callback = await self._sendToServer("create_group_file_folder", params)
        return callback
    #删除群文件文件夹
    async def delete_group_folder(self, group_id: int, folder_id: str):
        params = {
            "group_id": group_id,
            "folder_id": folder_id
        }
        callback = await self._sendToServer("delete_group_folder", params)
        return callback
    #获取群文件系统信息
    async def get_group_file_system_info(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_group_file_system_info", params)
        return callback
    #获取群根目录文件列表
    async def get_group_root_files(self, group_id: int):
        params = {
            "group_id": group_id
        }
        callback = await self._sendToServer("get_group_root_files", params)
        return callback
    #获取群子目录文件列表
    async def get_group_files_by_folder(self, group_id: int, folder_id: str):
        params = {
            "group_id": group_id,
            "folder_id": folder_id
        }
        callback = await self._sendToServer("get_group_files_by_folder", params)
        return callback
    #重命名群文件文件夹名
    async def rename_group_file_folder(self, group_id: int, folder_id: str, new_folder_name: str):
        params = {
            "group_id": group_id,
            "folder_id": folder_id,
            "new_folder_name": new_folder_name
        }
        callback = await self._sendToServer("rename_group_file_folder", params)
        return callback
    #获取群文件资源链接
    async def get_group_file_url(self, group_id: int, folder_id: str):
        params = {
            "group_id": group_id,
            "folder_id": folder_id
        }
        callback = await self._sendToServer("get_group_file_url", params)
        return callback
    #获取私聊文件资源链接
    async def get_private_file_url(self, file_id: str, user_id: int):
        params = {
            "file_id": file_id,
            "user_id": user_id
        }
        callback = await self._sendToServer("get_private_file_url", params)
        return callback
    #上传私聊文件
    async def upload_private_file(self, user_id: int, file: str, name: str):
        params = {
            "user_id": user_id,
            "file": file,
            "name": name
        }
        callback = await self._sendToServer("upload_private_file", params)
        return callback
    #上传闪传文件
    async def upload_flash_file(self, title: str, paths: list[str]):
        params = {
            "title": title,
            "paths": paths
        }
        callback = await self._sendToServer("upload_flash_file", params)
        return callback
    #下载闪传文件
    async def download_flash_file(self, share_link: str):
        params = {
            "share_link": share_link
        }
        callback = await self._sendToServer("download_flash_file", params)
        return callback
    #获取闪传文件详情
    async def get_flash_file_info(self, share_link: str):
        params = {
            "share_link": share_link
        }
        callback = await self._sendToServer("get_flash_file_info", params)
        return callback
    #下载文件到缓存目录
    async def download_file(self, url: str, name: str, headers: list[str]):
        params = {
            "url": url,
            "name": name,
            "headers": headers
        }
        callback = await self._sendToServer("download_file", params)
        return callback
    #
    #获取登录号信息
    async def get_login_info(self):
        callback = await self._sendToServer("get_login_info", {})
        self.botAcc = callback["data"]["user_id"]
        self.nickname = callback["data"]["nickname"]
        self.botName.append(self.nickname)
        return callback
