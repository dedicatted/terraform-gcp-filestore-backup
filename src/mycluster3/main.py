import google.cloud.filestore
import google.auth.transport.requests
from google.auth.transport.requests import AuthorizedSession
import google.auth
import time
import requests
import json
import os

# Backup environment variables
PROJECT_ID = 'PROJECT_NAME'
SOURCE_INSTANCE_ZONE = 'INSTANCE_ZONE'
SOURCE_INSTANCE_NAME = 'INSTANCE_NAME'
SOURCE_FILE_SHARE_NAME = 'volumes'
BACKUP_REGION = 'YOUR_REGION'

# Trigger Backup creation
credentials, project = google.auth.default()
request = google.auth.transport.requests.Request()
credentials.refresh(request)
authed_session = AuthorizedSession(credentials)


def get_backup_id():
    return "mycluster1-" + time.strftime("%Y%m%d-%H%M%S")


# Defining backup id variable
backup_name = get_backup_id()


# Function for Slack notifications with checking for needed environment variable
def message_to_clack():
    slack_url = os.getenv('SLACK_URL', default=None)
    if slack_url is None:
        print('There is no environment SLACK_URL set.')
        print('SLACK_URL value is: ' + slack_url)
        return "Variable SLACK_URL is not set."
    payload = {"text": ":x: Filestore Incident\nBackup " + backup_name + " has been not created.\nPlease check it "
                                                                         "immediately."}
    webhook = slack_url
    return requests.post(webhook, json.dumps(payload))


def create_backup(request):
    trigger_run_url = "https://file.googleapis.com/v1beta1/projects/{}/locations/{}/backups?backupId={}".format(
        PROJECT_ID, BACKUP_REGION, backup_name)
    headers = {
        'Content-Type': 'application/json'
    }
    post_data = {
        "description": "my new backup",
        "source_instance": "projects/{}/locations/{}/instances/{}".format(PROJECT_ID, SOURCE_INSTANCE_ZONE,
                                                                          SOURCE_INSTANCE_NAME),
        "source_file_share": "{}".format(SOURCE_FILE_SHARE_NAME)
    }
    print("Making a request to " + trigger_run_url)
    r = authed_session.post(url=trigger_run_url, headers=headers, data=json.dumps(post_data))
    data = r.json()
    print(data)
    if r.status_code == requests.codes.ok:
        print(str(r.status_code) + ": The backup is uploading in the background.")
    else:
        raise RuntimeError(data['error'])

    # Short pause until the backup will be available in Filestore
    time.sleep(30)

    # Backup check section

    # Create a client
    client = google.cloud.filestore.CloudFilestoreManagerClient(credentials=credentials)

    # Initialize request argument(s)
    request_filestore = google.cloud.filestore.GetBackupRequest(
        name="projects/{}/locations/{}/backups/{}".format(PROJECT_ID, BACKUP_REGION, backup_name))

    try:
        # Make the request
        response = client.get_backup(request=request_filestore)
        # Handle the response and get backup state
        backup_state = str(response.state)
        backup_state = backup_state.replace('State.', '')

        # Loop function to pause backup check part of script when it's on "CREATING" state.
        # Checking every 30 seconds.
        # Loop will be skipped once backup state will be changed to different one.
        # For example: READY/STATE_UNSPECIFIED/FINALIZING/etc
        while backup_state == "CREATING":
            print("Backup in state CREATING, waiting...")
            time.sleep(10)
            # Make the request again
            response = client.get_backup(request=request_filestore)
            # Handle the response and get backup state
            backup_state = str(response.state)
            backup_state = backup_state.replace('State.', '')
            if backup_state == "READY":
                continue

        # Same for backups is "FINALIZING" state.
        while backup_state == "FINALIZING":
            print("Backup in state FINALIZING, waiting...")
            time.sleep(10)
            # Make the request again
            response = client.get_backup(request=request_filestore)
            # Handle the response and get backup state
            backup_state = str(response.state)
            backup_state = backup_state.replace('State.', '')
            if backup_state == "READY":
                continue

        # Check state of created backup
        if backup_state == "READY":
            print(
                "Backup has been created successfully!\nBackup ID: " + backup_name + "\nBackup State: " + backup_state)
            return backup_state
        elif backup_state == "STATE_UNSPECIFIED":
            print("Backup state is STATE_UNSPECIFIED.\nPlease check it.\nSend message to slack...\n")
            print(message_to_clack())
            print("Exit.")
            return backup_state
    except:
        print("Backup has been not found in Google Filestore.\nPlease check it.")
        print('Backup ID: ' + backup_name)
        print(message_to_clack())
        print("Exit.")
