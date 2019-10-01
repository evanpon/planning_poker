import json
import os
from utilities import handle_error, get_connection_row, update_item, get_room_members, send_to_connection


def execute(event, context):
    print("event", event)
    print("context:", context)
    # dynamodb = boto3.resource('dynamodb', region_name='us-west-2')#, endpoint_url="http://host.docker.internal:8000")

    body = json.loads(event["body"])
    room = body["room"]
    vote = body.get("vote", None)

    if vote == None:
        return handle_error("No vote found", event)

    connection_id = event["requestContext"]["connectionId"]
    user = get_connection_row(connection_id)
    if user is None:
        return handle_error("This user hasn't joined a room yet.", event)


    if user["room"] != room:
        handle_error(f'We have a mismatch. User room: {user["room"]}, message room: {room}', event)

    update_item(room, connection_id, {"vote": vote})
    connected_users = get_room_members(room)

    voting_finished = True
    for other_user in connected_users:
        other_connection_id = other_user['connection_id']
        if other_user.get("vote", None) is None:
            voting_finished = False
        message = {"room": room, "voter": user["user"], "vote": vote}
        send_to_connection(event, message, other_connection_id)

    if voting_finished:
        for u in connected_users:
            other_connection_id = u['connection_id']
            update_item(room, other_connection_id, {"vote": None})

    return {
        "statusCode": 200
    }
