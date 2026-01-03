# Contians snycing logic
#  the main client will init this when first needed
#  currently I have only implemented it to run on demand
#  and all it does is collect room invites
#  this is kept against the LOGIN SESSION
import json

class ClientSync():
    client = None
    current_rooms_data = None
    last_synced = None

    def __init__(self, client):
        self.client = client
        self.current_rooms_data = {}
        self.last_synced = None

    def sync(self, login_session):
        # always syncs - can be called manually to force
        response = self.client.sendGetRequest(
            url="/_matrix/client/v3/sync",
            loginSession=login_session
        )
        if response.status_code != 200:
            raise Exception("Error getting sync")
        responseDict = json.loads(response.text)
        if "rooms" in responseDict:
            if "invite" in responseDict["rooms"]:
                self.current_rooms_data["invite"] = responseDict["rooms"]["invite"]

    def _syncIfNeeded(self, login_session):
        # simple logic - just sync if it hasn't been done before
        if self.last_synced is None:
            self.sync(login_session=login_session)

    def get_current_invites(self, login_session):
        self._syncIfNeeded(login_session=login_session)
        if "invite" in self.current_rooms_data:
            return self.current_rooms_data["invite"]
        return {}

    def get_current_direct_room_ids_invited_to(self, login_session):
        my_user_id = self.client.whoami(login_session)["user_id"]
        retVal = {}
        # self._syncIfNeeded(login_session=login_session) not needed get current invites does this
        for roomId in self.get_current_invites(login_session=login_session).keys():
            inviter = None
            is_direct = False
            for event in self.current_rooms_data["invite"][roomId]["invite_state"]["events"]:
                if event["type"] == "m.room.member":
                    if event["state_key"] == my_user_id:
                        if "is_direct" in event["content"]:
                            if event["content"]["is_direct"]:
                                is_direct = True
                    else:
                        inviter = event["state_key"]
                if inviter is not None:
                    if is_direct:
                        retVal[roomId] = inviter
        return retVal
