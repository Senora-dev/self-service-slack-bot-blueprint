from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from aws_lambda_powertools.utilities import parameters
import os 

class SlackNotifier:
    def __init__(self, slack_token: str):
        # Initialize Slack client
        self.client = WebClient(token=slack_token)

    def send_update(self, thread_ts: str, message: str, channel: str):
        """Send an update to the user in Slack within a thread."""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                thread_ts=thread_ts  # Send within the specified thread
            )
            return response
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            return None

    def send_direct_message(self, user_id: str, message: str):
        """Send a direct message (DM) to a user on Slack and return thread_ts of the DM."""
        try:
            # Open a DM channel with the user
            dm_channel = self.client.conversations_open(users=user_id)['channel']['id']
            
            # Send message to the DM channel
            response = self.client.chat_postMessage(
                channel=dm_channel,
                text=message
            )
            # Return the thread_ts (ts of the DM message)
            return response['ts']
        except SlackApiError as e:
            print(f"Error sending direct message: {e.response['error']}")
            return None


def lambda_handler(event, context):
    slack_tokens_secret = parameters.get_secret(os.environ["SLACK_SECRET_TOKEN"], transform="json")
    slack_token = slack_tokens_secret["slack_bot_token"]
    slack_notifier = SlackNotifier(slack_token)
    if event["type"] == "in-thread":
        thread_ts = event["thread_ts"]
        dm_channel = event["dm_channel"]
        message = event["message"]
        response = slack_notifier.send_update(thread_ts,message,dm_channel)
    elif event["type"] == "direct-message":
        user_id = event["user_id"]
        message = event["message"]
        response = slack_notifier.send_direct_message(user_id,message)
    return response