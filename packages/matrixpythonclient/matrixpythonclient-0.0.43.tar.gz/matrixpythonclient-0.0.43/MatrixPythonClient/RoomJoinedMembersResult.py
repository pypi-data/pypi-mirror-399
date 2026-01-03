
class RoomJoinedMembersResult():
    result = None

    def __init__(self, result):
        self.result = result

    def getMembershipForUser(self, user_id):
        for chunk in self.result["chunk"]:
            if chunk["state_key"] == user_id:
                return chunk
        return None

    def isUserActiveOrInvited(self, user_id):
        membershipForUser = self.getMembershipForUser(user_id)
        if membershipForUser is None:
            return False
        membership = membershipForUser["content"]["membership"]
        if membership == "join":
            return True
        if membership == "invite":
            return True
        return False

    def numMembers(self):
        return len(self.result["chunk"])