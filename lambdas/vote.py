import json
import os
from utilities import (handle_error, get_connection_row, update_item, 
    get_room_members, send_to_connection, finish_voting_if_complete)


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

    collected_votes = []
    message = {"room": room, "user": user["user"]}
    for other_user in connected_users:
        other_connection_id = other_user['connection_id']
        vote = other_user.get("vote", None)
        if vote is not None:
            collected_votes.append({"user": other_user["user"], "vote": int(vote)})
        send_to_connection(event, message, other_connection_id)

    finish_voting_if_complete(event, room, connected_users, collected_votes)
    # if len(collected_votes) == len(connected_users):
    #     # Everyone has voted
    #     for user in connected_users:
    #         other_connection_id = user['connection_id']
    #         update_item(room, other_connection_id, {"vote": None})
    #         send_to_connection(event, collected_votes, other_connection_id)

    return {
        "statusCode": 200
    }
