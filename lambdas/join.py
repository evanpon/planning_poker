from utilities import (send_to_connection, get_room_members, 
    store_connection_row, store_room_row, delete_all_rows_for_connection,
    notify_users)
import json

def execute(event, context):
    body = json.loads(event["body"])
    room = body["room"]
    user = body["user"]
    connection_id = event["requestContext"]["connectionId"]

    # In case this user was already in another room, clear out old rows.
    delete_all_rows_for_connection(event, connection_id)

    # We don't care about keeping the connection until they actually join a room
    store_connection_row(connection_id, {'room': room, 'user': user})

    # Now store the connection id partitioned by room for easy lookup. 
    store_room_row(room, connection_id, {"user": user})

    users = get_room_members(room)
    notify_users(event, users, f'{user} has joined {room}')

    current_votes = retrieve_current_votes(users)
    send_to_connection(event, current_votes)

    return {
        "statusCode": 200
    }

def retrieve_current_votes(users):
    data = []
    for user in users:
        voted = True if "vote" in user else False
        vote_data = {"user": user["user"], "voted": voted}
        data.append(vote_data)
    return data