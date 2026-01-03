import requests
import json

class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://botapi.rubika.ir/v3/{token}/"
        print("Powered by Rubio Library | @RubioLib")

    def _req(self, method, data=None):
        return requests.post(self.api_url + method, headers={'Content-Type': 'application/json'}, json=data).json()

    def get_me(self):
        return self._req("getMe")

    def send_message(self, chat_id, text, reply_to_message_id=None, disable_notification=False, chat_keypad=None, inline_keypad=None, chat_keypad_type=None):
        data = {"chat_id": chat_id, "text": text, "disable_notification": disable_notification}
        if reply_to_message_id: data["reply_to_message_id"] = reply_to_message_id
        if chat_keypad: data["chat_keypad"] = chat_keypad
        if inline_keypad: data["inline_keypad"] = inline_keypad
        if chat_keypad_type: data["chat_keypad_type"] = chat_keypad_type
        return self._req("sendMessage", data)

    def send_poll(self, chat_id, question, options):
        return self._req("sendPoll", {"chat_id": chat_id, "question": question, "options": options})

    def send_location(self, chat_id, latitude, longitude, reply_to_message_id=None, disable_notification=False):
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, "disable_notification": disable_notification}
        if reply_to_message_id: data["reply_to_message_id"] = reply_to_message_id
        return self._req("sendLocation", data)

    def send_contact(self, chat_id, first_name, last_name, phone_number, reply_to_message_id=None, disable_notification=False):
        data = {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "phone_number": phone_number, "disable_notification": disable_notification}
        if reply_to_message_id: data["reply_to_message_id"] = reply_to_message_id
        return self._req("sendContact", data)

    def get_chat(self, chat_id):
        return self._req("getChat", {"chat_id": chat_id})

    def get_updates(self, limit=None, offset_id=None):
        data = {}
        if limit: data["limit"] = limit
        if offset_id: data["offset_id"] = offset_id
        return self._req("getUpdates", data)

    def forward_message(self, from_chat_id, message_id, to_chat_id, disable_notification=False):
        return self._req("forwardMessage", {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification})

    def edit_message_text(self, chat_id, message_id, text):
        return self._req("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    def edit_message_keypad(self, chat_id, message_id, inline_keypad):
        return self._req("editInlineKeypad", {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad})

    def delete_message(self, chat_id, message_id):
        return self._req("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    def set_commands(self, bot_commands):
        return self._req("setCommands", {"bot_commands": bot_commands})

    def update_bot_endpoints(self, url, type_):
        return self._req("updateBotEndpoints", {"url": url, "type": type_})

    def remove_chat_keypad(self, chat_id):
        return self._req("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Remove"})

    def set_chat_keypad(self, chat_id, chat_keypad):
        return self._req("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad})

    def get_file(self, file_id):
        return self._req("getFile", {"file_id": file_id})

    def send_file(self, chat_id, file_id, text=None, reply_to_message_id=None, disable_notification=False):
        data = {"chat_id": chat_id, "file_id": file_id, "disable_notification": disable_notification}
        if text: data["text"] = text
        if reply_to_message_id: data["reply_to_message_id"] = reply_to_message_id
        return self._req("sendFile", data)

    def request_send_file(self, type_):
        return self._req("requestSendFile", {"type": type_})

    def upload_file(self, file_path, upload_url):
        with open(file_path, 'rb') as f:
            return requests.post(upload_url, files={'file': f}).json()

    def ban_chat_member(self, chat_id, user_id):
        return self._req("banChatMember", {"chat_id": chat_id, "user_id": user_id})

    def unban_chat_member(self, chat_id, user_id):
        return self._req("unbanChatMember", {"chat_id": chat_id, "user_id": user_id})
