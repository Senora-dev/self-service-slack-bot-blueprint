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

# Now, you can access each modal.json content by the variable name
# For example, if you have a directory 'example', you can access it as 'example'
# print(example)  # This will print the content of modal.json in the 'example' folder

# To create the main menu
# Inside blocks.py
main_menu = []

# Process all action_data
for action_name, modal_content in action_data.items():
    if isinstance(modal_content, list):
        for block in modal_content:
            title = "Default Title"  # Default title if none exists
            if block.get("type") == "header" and "text" in block:
                title = block["text"].get("text", "No Title")
            elif block.get("type") == "input" and "label" in block:
                title = block["label"].get("text", "No Title")

            unique_block_id = f"{action_name}_block"

            # Check if the block already exists in main_menu
            block_exists = False
            for existing_block in main_menu:
                if existing_block['block_id'] == unique_block_id:
                    block_exists = True
                    break

            # If the block doesn't exist, add it to the main_menu
            if not block_exists:
                main_menu.append({
                    "type": "input",
                    "block_id": unique_block_id,  # Unique block_id
                    "element": {
                        "type": "static_select",
                        "action_id": "initial_choice_action",
                        "placeholder": {"type": "plain_text", "text": "Choose an action"},
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": title,
                                },
                                "value": action_name,
                            }],
                    },
                    "label": {"type": "plain_text", "text": "Select an action"},
                })

# Print the result to check if the content was added correctly
print(f"Main menu blocks after processing: {main_menu}")
print(f"Action data: {action_data}")
print(action_data['example'])
