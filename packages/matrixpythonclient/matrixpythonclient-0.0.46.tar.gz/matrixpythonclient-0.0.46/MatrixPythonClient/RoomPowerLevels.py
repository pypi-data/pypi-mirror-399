# Contains my code relating to room powerlevels

def get_trusted_private_chat_power_levels(creator_user_ids):
    if len(creator_user_ids) == 0:
        raise Exception("No users specified")
    retVal = {
        "ban": 100,
        "events": {
            # "m.room.avatar": 100,
            # "m.room.canonical_alias": 100,
            # "m.room.encryption": 100,
            # "m.room.history_visibility": 100,
            # "m.room.message": 100,
            # "m.room.name": 100,
            # "m.room.power_levels": 100,
            # "m.room.server_acl": 100,
            # "m.room.tombstone": 100,
            # "m.room.topic": 100,
        },
        "invite": 100,
        "kick": 100,
        "notifications": {
            "room": 100
        },
        "redact": 100,
        "events_default": 100,
        "state_default": 100,
        "users_default": 0,
        "users": {
        },
    }
    for creator_user_id in creator_user_ids:
        retVal["users"][creator_user_id] = 100
    return retVal