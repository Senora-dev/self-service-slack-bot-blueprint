import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_sdk.errors import SlackApiError
from aws_lambda_powertools.utilities import parameters
import boto3
import json
from aws_lambda_powertools import Logger
from slack_bolt.middleware.request_verification import RequestVerification
from blocks import main_menu, action_data

logger = Logger()

# Initialize your app with the bot token and signing secret
SLACK_TOKENS = parameters.get_secret(os.environ["SLACK_SECRET_TOKEN"], transform="json")
app = App(
    token=SLACK_TOKENS["slack_bot_token"],
    signing_secret=SLACK_TOKENS["slack_signing_secret"],
    logger=logger,
)

app.use(RequestVerification(signing_secret=SLACK_TOKENS["slack_signing_secret"]))

@app.command("/senora")
def open_modal(ack, body, client):
    trigger_id = body["trigger_id"]
    modal_view = {
        "type": "modal",
        "callback_id": "initial_modal",
        "title": {"type": "plain_text", "text": "Select Action"},
        "blocks": main_menu,
        "submit": {"type": "plain_text", "text": "Next"},
        "close": {"type": "plain_text", "text": "Cancel"},
    }
    client.views_open(trigger_id=trigger_id, view=modal_view)
    ack()

@app.view("initial_modal")
def handle_initial_modal_submission(ack, body, client, logger):
    
    # Extract the selected value safely
    values = body.get("view", {}).get("state", {}).get("values", {})
    action_name = next(iter(values)).replace("_block","") 
    choice_block_key = action_name+"_block"
    choice_block = values.get(choice_block_key, {})
    choice_action = choice_block.get("initial_choice_action", {})
    if "selected_option" in choice_action:
        selected_option = choice_action["selected_option"]["value"]
    else:
        logger.error("No selected option found in initial_choice_action")
        return
    callback_id = "updated_modal"
    #if selected_option == "example":
    #    blocks = action_data['example']
    blocks = action_data[selected_option]

    logger.info("blocks:")
    logger.info(blocks)

    new_view = {
        "type": "modal",
        "callback_id": callback_id,
        "title": {"type": "plain_text", "text": "Updated Form"},
        "blocks": blocks,
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
    }

    ack(response_action="update", view=new_view)


@app.view("updated_modal")
def handle_updated_modal_submission(ack, body, client, logger):
    logger.info(body)
    print("INSIDE-UPDATED_MODAL")
    action_name = body['view']['blocks'][0]['block_id'].replace("_block_id","")
    # Execute the relevant CodeBuild by uploading to S3 a file:
    try:
        execute_action(action_name,body)
        # Send confirmation message to the user
        logger.info("body:")
        logger.info(body)
        user_id = body['user']['id']
        response_message = "We have received your request and are processing it now. We will update you once it is finished :)"
        client.chat_postMessage(channel=user_id, text=response_message) 
    except Exception as err:
        logger.error(err)
        user_id = body['user']['id']
        response_message = "There is an error :( please contact your amazing DevOps team."
        client.chat_postMessage(channel=user_id, text=response_message)  
        raise 

    logger.info(f"Sent payload to SNS: {body}")
    ack()

 #---- Mention Listener ----#
@app.event("app_mention")
def event_test(body, say):
    logger.debug(f"app_mention event received: {body}")
    user = body["event"]["user"]
    say(f"Hello <@{user}>!")


# ---- Listener for direct messages ---- #
@app.event("message")
def handle_dm_events(body, client):
    event = body.get("event", {})
    if (
        event.get("channel_type") == "im"
    ):  # Check if the message is in a direct message channel
        user_id = event["user"]
        logger.debug(f"Direct message received from user {user_id}")

        response_message = "Sorry, I'm still not ready for talks, working on modals."

        try:
            response = client.chat_postMessage(channel=user_id, text=response_message)
            logger.debug(f"Message post response: {response}")
        except SlackApiError as e:
            logger.error(f"Error posting message: {e.response['error']}")


# -------- Home Tab -------- #
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # Call views.publish with the built-in client
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            # Home tabs must be enabled in your app configuration
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome home, <@" + event["user"] + "> :house:*",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Learn how home tabs can be more useful and interactive <https://api.slack.com/surfaces/tabs/using|*in the documentation*>.",
                        },
                    },
                ],
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

def execute_action(codebuild_project_name,request_body):
    trigger_id = request_body['trigger_id']
    codebuild_client = boto3.client('codebuild')

    build_params = {
        'REQUEST_BODY': json.dumps(request_body),
        'TRIGGER_ID': trigger_id
    }

    response = codebuild_client.start_build(
    projectName=codebuild_project_name,
    environmentVariablesOverride=[
        {
            'name': key,
            'value': value,
            'type': 'PLAINTEXT'
        }
        for key, value in build_params.items()
        ]
    )

# -------- Create a SlackRequestHandler and assign the app -------- #
handler = SlackRequestHandler(app)


# -------- Lambda Handler -------- #
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    response = handler.handle(event, context)
    logger.info(f"Response: {response}")
    return response