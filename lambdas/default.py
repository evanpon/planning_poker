from utilities import send_to_connection

def execute(event, context):
    message = {
        "message": "No route found for that action."
    }
    send_to_connection(event, message)
    return {
        "statusCode": 404
    }