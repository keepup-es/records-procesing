import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account

from google.auth.transport.requests import Request
import configparser

from email.mime.text import MIMEText
import base64

#pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def create_message(sender, to, subject, msg):
    message = MIMEText(msg)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Base 64 encode
    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    return {'raw': b64_string}
    #return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
    #try:
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    print('Message Id: %s' % message['id'] )
    return message
    #except errors.HttpError, error:print( 'An error occurred: %s' % error )

def main(mail_to):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            config = configparser.ConfigParser()
            config.read('config/config.txt')
            json_key_fle = config.get('Keepup', 'oauth_file')
            flow = InstalledAppFlow.from_client_secrets_file(json_key_fle, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Example read operation
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
    for label in labels:
        print(label['name'])

    # Example write
    msg = create_message("from@gmail.com", mail_to, "Test", "Msg1")
    send_message(service, 'me', msg)

if __name__ == '__main__':
    main("example@gmail.com")