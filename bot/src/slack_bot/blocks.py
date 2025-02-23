import os
import json

actions_path = "./actions/"  # Path to the directories with modal.json files

# Loop through all directories in the path
action_data = {}
for dir_name in os.listdir(actions_path):
    dir_path = os.path.join(actions_path, dir_name)

    # Check if it's a directory and not a file
    if os.path.isdir(dir_path):
        modal_file_path = os.path.join(dir_path, "modal.json")

        # If modal.json exists in the directory
        if os.path.exists(modal_file_path):
            with open(modal_file_path, "r") as modal_file:
                modal_content = json.load(modal_file)
                print(f"Loaded modal.json for {dir_name}: {modal_content}")

            # Save the data in the action_data dictionary
            action_data[dir_name] = modal_content

# To create the main menu
main_menu = [
    {
        "type": "input",
        "block_id": "action_selection",
        "element": {
            "type": "static_select",
            "action_id": "initial_choice_action",
            "placeholder": {"type": "plain_text", "text": "Choose an action"},
            "options": [
                {
                    "text": {"type": "plain_text", "text": action_name},
                    "value": action_name,
                }
                for action_name in action_data.keys()
            ],
        },
        "label": {"type": "plain_text", "text": "Select an action"},
    }
]

# Print the result to check if the content was added correctly
print(f"Main menu blocks after processing: {main_menu}")
print(f"Action data: {action_data}")
