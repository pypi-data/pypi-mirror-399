# Matrix client class
import PythonAPIClientBase
from .MatrixLoginSession import MatrixLoginSessionFromUsernameAndPassword, MatrixLoginSessionFromAccessToken
import json
import uuid
import hmac
import hashlib
import PythonAPIClientBase
from .Exceptions import UserAlreadyJoinedRoomException
from .RoomJoinedMembersResult import RoomJoinedMembersResult
from .RoomPowerLevels import get_trusted_private_chat_power_levels

usernameInvalidChars=" :@!"

class MatrixClient(PythonAPIClientBase.APIClientBase):
    chat_domain = None
    debug = None
    def __init__(self, chat_domain, mock=None, forceOneRequestAtATime=False, verboseLogging=PythonAPIClientBase.VerboseLoggingNullLogClass(), debug=False):
        self.debug = debug
        useBaseUrl = chat_domain
        if useBaseUrl != "MOCK":
            useBaseUrl = "https://" + useBaseUrl
        super().__init__(baseURL=useBaseUrl, mock=mock, forceOneRequestAtATime=forceOneRequestAtATime, verboseLogging=verboseLogging)
        self.chat_domain=chat_domain

    def getLoginSessionFromUsernameAndPassword(self, username, password):
        return MatrixLoginSessionFromUsernameAndPassword(client=self, username=username, password=password)

    def getLoginSessionFromAccessToken(self, user_id, access_token, device_id):
        return MatrixLoginSessionFromAccessToken(client=self, user_id=user_id, access_token=access_token, device_id=device_id)

    def get_userid_from_username(self, username):
        if not self.isValidUsername(username):
            raise Exception("Invalid user name - ", username)
        return "@" + username + ":" + self.chat_domain

    def get_shared_secret_nonce(self):
        response = self.sendGetRequest(
            url="/_synapse/admin/v1/register",
            loginSession=None
        )
        if response.status_code!=200:
            raise Exception("Error getting registration nonce")
        return json.loads(response.text)["nonce"]

    def registerNewUser(self, username, password, displayname, registration_shared_secret=None):
        if not self.isValidUsername(username):
            raise Exception("Invalid user name - ", username)

        nonce = self.get_shared_secret_nonce()
        mac_data = f"{nonce}\0{username}\0{password}\0notadmin"
        mac = hmac.new(
            registration_shared_secret.encode(),
            mac_data.encode(),
            hashlib.sha1
        ).hexdigest()

        postData={
            "nonce": nonce,
            "username": username,
            "displayname": displayname,
            "password": password,
            "admin": False,
            "mac": mac
        }
        response = self.sendPostRequest(
            "/_synapse/admin/v1/register", loginSession=None,
            data=json.dumps(postData)
        )
        if response.status_code != 200:
            # print(response.status_code)
            # print(response.text)
            return (None, None, None)
        resp = json.loads(response.text)
        return (
            resp["user_id"],
            resp["access_token"],
            resp["device_id"]
        )

    def getAllUsers(self, login_session):
        postData={
            "limit": 1
        }
        response = self.sendPostRequest(
            "/_matrix/client/v3/user_directory/search", loginSession=login_session,
            data=json.dumps(postData)
        )

        print("rs", response.text)
        print("h", response.headers)

        return [1,2,3]

    # admin_login_session = admin_login_session,
    # room_topic = room_topic,
    # room_name = room_name,
    # room_alias_name = room_alias_name,
    # invite_list = [admin_login_session.get_user_id(), login_session.get_user_id()]
    def create_room(
        self,
        login_session,
        room_topic,
        room_name,
        room_alias_name,
        invite_list,
        is_direct = False,
        power_levels = None
    ):
        # POST
        create_room_body = {
            "creation_content": {},
            "initial_state": [
                {
                    "type": "m.room.join_rules",
                    "state_key": "",
                    "content": {
                        "join_rule": "invite"
                    }
                },
                {
                    "type": "m.room.history_visibility",
                    "state_key": "",
                    "content": {
                        "history_visibility": "shared"
                    }
                },
                {
                    "type": "m.room.guest_access",
                    "state_key": "",
                    "content": {
                        "guest_access": "forbidden"
                    }
                }
            ],
            "invite": invite_list,
            "invite_3pid": [],
            "is_direct": is_direct,
            "name": room_name,
            "room_version": "11",
            "topic": room_topic,
            "visibility": "private"
        }
        if room_alias_name is not None:
            create_room_body["room_alias_name"] = room_alias_name
        if power_levels is not None:
            create_room_body["initial_state"].append({
                "type": "m.room.power_levels",
                "state_key": "",
                "content": power_levels
            })
        response = self.sendPostRequest(
            "/_matrix/client/v3/createRoom",
            loginSession=login_session,
            data=json.dumps(create_room_body)
        )
        if response.status_code != 200:
            print("ERROR")
            print("status", response.status_code)
            print("text", response.text)
            raise Exception("Error failed to create room")
        return json.loads(response.text)["room_id"]

    def invite_user_to_room(
        self,
        login_session,
        room_id,
        user_id,
        reason
    ):
        # POST
        invite_body = {
            "reason": reason,
            "user_id": user_id
        }
        response = self.sendPostRequest(
            "/_matrix/client/v3/rooms/" + room_id + "/invite",
            loginSession=login_session,
            data=json.dumps(invite_body)
        )
        if response.status_code != 200:
            if response.status_code == 403:
                try:
                    #print("Checking 403")
                    responseJson = json.loads(response.text)
                    #print("responseJson", responseJson)
                    if responseJson["errcode"] == "M_FORBIDDEN":
                        if responseJson["error"] == "user is already joined to room":
                            raise UserAlreadyJoinedRoomException("user is already joined to room")
                except:
                    pass
            print("ERROR")
            print("status", response.status_code)
            print("text", response.text)
            raise Exception("Error failed to invite user to room")
        return

    def isUsernameAvailiable(self, username):
        response = self.sendGetRequest(
            url="/_matrix/client/v3/register/available?username=" + username,
            loginSession=None
        )
        if response.status_code==200:
            return True
        return False

    def get_own_display_name(self, login_session):
        return self.get_display_name(login_session, userid=login_session.get_user_id())

    def get_display_name(self, login_session, userid):
        response = self.sendGetRequest(
            url="/_matrix/client/v3/profile/" + userid + "/displayname",
            loginSession=login_session,
        )
        if response.status_code==200:
            return json.loads(response.text)["displayname"]
        if response.status_code==404:
            return "" # no profile set or user doesn't exist
        print("Error getting display name")
        print("code:", response.status_code)
        print("text", response.text)
        raise Exception("Error getting display name")

    def update_own_display_name(self, login_session, display_name):
        return self.update_display_name(login_session=login_session, userid=login_session.get_user_id(), display_name=display_name)

    def update_display_name(self, login_session, userid, display_name, skip_not_required_check=False):
        if not skip_not_required_check:
            if display_name == self.get_display_name(login_session=login_session, userid=userid):
                return
        put_body = {
            "displayname": display_name
        }
        url_to_call = "/_matrix/client/v3/profile/" + userid + "/displayname"
        response = self.sendPutRequest(
            url=url_to_call,
            loginSession=login_session,
            data=json.dumps(put_body)
        )
        if response.status_code==200:
            return True

        if self.debug:
            print("Debug mode on - not 200 code response with call to")
            print("url_to_call", url_to_call)
            print("response.status_code", str(response.status_code))
            print("response.text", response.text)
            print("userid", userid)
            print("login_session.get_user_id()", login_session.get_user_id())
        raise Exception("Failed to change display name")

    def auto_register_user(
        self,
        admin_login_session,  # Used for room creation
        registration_shared_secret,
        username,
        displayname,
        user_password_fetch_function,
        user_password_store_function,
    ):
        #auto register a user and return a current login session
        if not self.isValidUsername(username):
            raise Exception("Invalid user name - ", username)
        # Doesn't use login_session. it will create a user than log in as that user
        login_session = None
        password = user_password_fetch_function(username=username)
        if self.isUsernameAvailiable(username=username):
            if password != None:
                raise Exception("Error - user is available but a password is stored")
            password = str(uuid.uuid4())
            (user_id, access_token, device_id) = self.registerNewUser(
                username=username,
                password=password,
                displayname=displayname,
                registration_shared_secret=registration_shared_secret
            )
            if access_token is None:
                raise Exception("Failed to register user")
            user_password_store_function(username=username, password=password)
            login_session = self.getLoginSessionFromAccessToken(user_id=user_id, access_token=access_token, device_id=device_id)
        else:
            if password == None:
                raise Exception("Error - user already created but we have no password stored")
            login_session = self.getLoginSessionFromUsernameAndPassword(username=username, password=password)

        # Creation doesn't seem to update display name so do it here
        self.update_display_name(login_session=login_session, userid=self.get_userid_from_username(username), display_name=displayname)

        return login_session

    def auto_invite_user_create_room_if_required(
        self,
        admin_login_session,
        clubchat_room_id,
        user_id,
        room_topic,
        room_name,
        room_alias_name,
        room_fetch_function,  # fetch room id's (key is clubchat_room_id)
        room_store_function,  # Store room id's
        invite_reason
    ):
        room_id = room_fetch_function(clubchat_room_id)
        if room_id is not None:
            try:
                self.invite_user_to_room(
                    login_session=admin_login_session,
                    room_id=room_id,
                    user_id=user_id,
                    reason=invite_reason
                )
            except UserAlreadyJoinedRoomException:
                # User is already in this room - we can continue
                pass
        else:
            room_id = self.create_room(
                login_session=admin_login_session,
                room_topic=room_topic,
                room_name=room_name,
                room_alias_name=room_alias_name,
                invite_list=[user_id] # no need to include admin as that is creator
            )
            room_store_function(clubchat_room_id, room_id)
        return room_id

    def auto_register_user_in_room(
        self,
        admin_login_session, # Used for room creation
        registration_shared_secret,
        username,
        displayname,
        user_password_fetch_function,
        user_password_store_function,
        clubchat_room_id,  #unique identifier of clubchat room
        room_topic,
        room_name,
        room_alias_name,
        room_fetch_function, #fetch room id's (key is clubchat_room_id)
        room_store_function, #Store room id's
        invite_reason="Join the chat"
    ):
        login_session = self.auto_register_user(
            admin_login_session=admin_login_session,  # Used for room creation
            registration_shared_secret=registration_shared_secret,
            username=username,
            displayname=displayname,
            user_password_fetch_function=user_password_fetch_function,
            user_password_store_function=user_password_store_function,
        )

        room_id = self.auto_invite_user_create_room_if_required(
            admin_login_session,
            clubchat_room_id,
            user_id=login_session.get_user_id(),
            room_topic=room_topic,
            room_name=room_name,
            room_alias_name=room_alias_name,
            room_fetch_function=room_fetch_function,
            room_store_function=room_store_function,
            invite_reason=invite_reason
        )

        return {
            "login_session": login_session, # Needed as auth token is extracted
            "room_id": room_id
        }

    def isValidUsername(self, username):
        for char in usernameInvalidChars:
            if char in username:
                return False
        if username != username.lower():
            return False
        return True

    def ensureValidUserId(self, user_id):
        if len(user_id) < 2:
            raise Exception("Invalid user_id - ", user_id)
        if user_id[0] != "@":
            raise Exception("Invalid user_id - ", user_id)

    def whoami(self, login_session, force=False):
        if not force:
            cached_result = login_session.get_whoami_cached_result()
            if cached_result is not None:
                return cached_result

        result = self.sendGetRequest(
            origin=None,
            url= "/_matrix/client/v3/account/whoami",
            params={
                "limit": 10,
                "offset": 0
            },
            loginSession=login_session,
            injectHeadersFn=None
        )

        if result.status_code != 200:
            print("Error getting whomai info")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error listing users")

        resultJson = json.loads(result.text)
        login_session.set_whoami_cached_result(resultJson)
        return resultJson

    def getAccountData(self, login_session, data_type):
        user_id = self.whoami(login_session)["user_id"]
        result = self.sendGetRequest(
            url="/_matrix/client/v3/user/" + user_id + "/account_data/" + data_type,
            loginSession=login_session
        )
        if result.status_code != 200:
            if result.status_code == 404:
                return None
            print("Error getting account data")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error getting account data")

        return json.loads(result.text)

    def setAccountData(self, login_session, data_type, data):
        user_id = self.whoami(login_session)["user_id"]
        result = self.sendPutRequest(
            url="/_matrix/client/v3/user/" + user_id + "/account_data/" + data_type,
            loginSession=login_session,
            data=json.dumps(data)
        )
        if result.status_code != 200:
            print("Error getting account data")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error getting account data")

    def getJoinedRooms(self, login_session):
        result = self.sendGetRequest(
            url="/_matrix/client/v3/joined_rooms",
            loginSession=login_session
        )
        if result.status_code != 200:
            if result.status_code == 404:
                return None
            print("Error getting room member list")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error getting room member list")

        resultJson = json.loads(result.text)
        return resultJson["joined_rooms"]

    def getRoomState(self, login_session, roomId, state):
        result = self.sendGetRequest(
            url="/_matrix/client/v3/rooms/" + roomId + "/state/" + state,
            loginSession=login_session
        )
        if result.status_code != 200:
            if result.status_code == 404:
                return None
            print("Error getting room topic")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error getting room topic")

        resultJson = json.loads(result.text)
        return resultJson

    def getRoomMembers(self, login_session, roomId):
        result = self.sendGetRequest(
            url="/_matrix/client/v3/rooms/" + roomId + "/members",
            loginSession=login_session
        )
        if result.status_code != 200:
            if result.status_code == 404:
                return None
            print("Error getting room member list")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error getting room member list")

        resultJson = json.loads(result.text)
        return RoomJoinedMembersResult(resultJson)

    def joinRoom(self, login_session, roomId):
        postData = {}
        result = self.sendPostRequest(
            url="/_matrix/client/v3/rooms/" + roomId + "/join",
            loginSession=login_session,
            data=json.dumps(postData)
        )
        if result.status_code != 200:
            if result.status_code == 404:
                return None
            print("Error joining room")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error joining room")

        resultJson = json.loads(result.text)
        return resultJson

    #POST / _matrix / client / v3 / rooms / {roomId} / kick
    def kickUserFromRoom(
        self,
        login_session,
        room_id,
        user_id,
        reason
    ):
        postData = {
            "reason": reason,
            "user_id": user_id
        }
        response = self.sendPostRequest(
            "/_matrix/client/v3/rooms/" + room_id + "/kick",
            loginSession=login_session,
            data=json.dumps(postData)
        )
        if response.status_code != 200:
            print("status", response.status_code)
            print("text", response.text)
            raise Exception("Error failed to kick user from room")
        return

    def leaveRoom(self, login_session, roomId, reason=None):
        postData = {}
        if reason is not None:
            postData["reason"] = reason
        result = self.sendPostRequest(
            url="/_matrix/client/v3/rooms/" + roomId + "/leave",
            loginSession=login_session,
            data=json.dumps(postData)
        )
        if result.status_code != 200:
            if result.status_code == 404:
                return None
            print("Error leaving room")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error leaving room")

        resultJson = json.loads(result.text)

        # Need to remove from m.direct if it is there
        self.updateDirectMappingRemoveRoomId(login_session=login_session, roomId=roomId)

        return resultJson

    def findExistingDmRoom(self, login_session, user_id, my_user_id):
        content = self.getAccountData(
            login_session=login_session,
            data_type="m.direct"
        )
        if content is not None:
            if user_id in content:
                roomIds = content[user_id]
                for roomId in roomIds:
                    # Will return the first room where the other user is invited or in the room (not leave)
                    joinedMembersFromDM = self.getRoomMembers(login_session, roomId)
                    if joinedMembersFromDM.isUserActiveOrInvited(user_id):
                        return roomId

        # # Check joinedRooms in case invite not processed
        # This check is not necessary as joined rooms are always in m.direct
        # joinedRooms = self.getJoinedRooms(login_session)
        # for roomId in joinedRooms:
        #     room_topic = self.getRoomState(
        #         login_session=login_session,
        #         roomId=roomId,
        #         state="m.room.topic"
        #     )
        #     if room_topic == "Direct Chat":
        #         joinedMembers = self.getRoomMembers(login_session, roomId)
        #         if joinedMembers.numMembers() == 2:
        #             if joinedMembers.isUserActiveOrInvited(user_id):
        #                 if joinedMembers.isUserActiveOrInvited(my_user_id):
        #                     return roomId

        invites = login_session.getSync().get_current_direct_room_ids_invited_to(login_session=login_session)
        # in the form roomId: otherUser
        #get current invites {'!wZCxd8oPmdQZ5dbx:socialchatdev.metcarob.com': '@socialdsocialsaas-socialautoconfigtestuser001:socialchatdev.metcarob.com'}
        for roomId in invites.keys():
            # found an invite - that means we should use this room
            if invites[roomId] == user_id:
                self.joinRoom(login_session=login_session, roomId=roomId)
                self.updateDirectMappingAddRoomId(login_session=login_session, userId=user_id, roomId=roomId)
                return roomId

        return None

    def updateDirectMappingAddRoomId(self, login_session, userId, roomId):
        data_type="m.direct"
        content = self.getAccountData(
            login_session=login_session,
            data_type=data_type
        )
        if content is None:
            content = {}
        if userId not in content:
            content[userId] = []
        if roomId not in content[userId]:
            content[userId].append(roomId)
        self.setAccountData(
            login_session=login_session,
            data_type=data_type,
            data=content
        )

    def updateDirectMappingRemoveRoomId(self, login_session, roomId):
        data_type="m.direct"
        content = self.getAccountData(
            login_session=login_session,
            data_type=data_type
        )
        if content is None:
            return # No content so
        userIDsToCheck = list(content.keys())

        # First: remove the roomId from all lists
        for userId in userIDsToCheck:
            if roomId in content[userId]:
                content[userId].remove(roomId)

        # Second: remove any users whose list is now empty
        for userId in userIDsToCheck:
            if len(content[userId]) == 0:
                del content[userId]

        self.setAccountData(
            login_session=login_session,
            data_type=data_type,
            data=content
        )

    def start_direct_message(self, login_session, user_id):
        self.ensureValidUserId(user_id)
        my_user_id = self.whoami(login_session)["user_id"]
        existingRoomId = self.findExistingDmRoom(login_session=login_session, user_id=user_id, my_user_id=my_user_id)
        if existingRoomId is not None:
            return existingRoomId


        roomId = self.create_room(
            login_session=login_session,
            room_topic="Direct Chat",
            room_name=user_id + ' - ' + my_user_id,
            room_alias_name=None,
            invite_list=[user_id],
            is_direct=True,
            power_levels=get_trusted_private_chat_power_levels([my_user_id, user_id])
        )
        self.updateDirectMappingAddRoomId(
          login_session=login_session,
          userId=user_id,
          roomId=roomId
        )
        return roomId

    def sendTextMessageToRoom(self, login_session, roomId, messageText):
        txn_id = str(uuid.uuid4())
        event_type = "m.room.message"
        data = {
            "msgtype": "m.text",
            "body": messageText
        }
        result = self.sendPutRequest(
            url="/_matrix/client/v3/rooms/" + roomId + "/send/" + event_type + "/" + txn_id,
            loginSession=login_session,
            data=json.dumps(data)
        )
        if result.status_code != 200:
            print("Error getting account data")
            print("status", result.status_code)
            print("response", result.text)
            raise Exception("Error getting account data")

        return json.loads(result.text)