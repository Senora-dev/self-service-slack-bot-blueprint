# 🚀 Actions Folder

This folder contains all the self-service actions for the Slack bot. Each action is represented by a folder that contains the necessary files to define the behavior of the action in both Slack and AWS CodeBuild.

## How to Add a New Action

To add a new action to the system, follow these steps:

1. **Create a Folder for the Action**  
   Under the `./actions` directory, create a new folder with the name of the action (without spaces). Remember that this name will be used as:
   - The folder name in S3.
   - The CodeBuild project name.
   - The variable name in the Python code of the Slack bot.

2. **Add `modal.json`**  
   - Inside the newly created action folder, create a `modal.json` file.  
   - This file defines the modal that will be shown to the user when they invoke the action.  
   - To generate a beautiful form for the modal, you can use [Blocks Kit by Slack](https://api.slack.com/tools/block-kit-builder).

3. **Add `buildspec.yaml`**  
   - The `buildspec.yaml` file is responsible for defining the "backend" of the action.  
   - This file contains the commands that will be executed by the corresponding AWS CodeBuild project when the action is triggered.  
   - Make sure to define the necessary build steps in this file.

---

### Example Folder Structure
```bash
actions/ 
├── example_action/ 
│ ├── modal.json 
│ ├── buildspec.yaml 
├── another_action/ 
│ ├── modal.json 
│ ├── buildspec.yaml
```

---

If you have any questions or need help with the structure of `modal.json` or `buildspec.yaml`, feel free to ask for assistance!

[Senora.dev](https://Senora.dev) 💜
