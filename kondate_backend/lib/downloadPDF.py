import os.path
import io
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import boto3

SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVERID = "1im_gziXlaEhKo4dW58fRinHsQCEmJWh1"
SERVICEACCOUNT = "swapdrive.json"

BUCKET_NAME = "kondate-pdf"


s3 = boto3.resource("s3")
upload_bucket = s3.Bucket(BUCKET_NAME)

def strnow():
    return datetime.now().strftime("%Y%m%d%H%M")

# @return: PDFbinary んで次それwithで処理します！
def downloadPDF():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists("token.json"):
    #     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             "credentials.json", SCOPES
    #         )
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open("token.json", "w") as token:
    #         token.write(creds.to_json())

    creds = service_account.Credentials.from_service_account_file(SERVICEACCOUNT, scopes = SCOPES)

    try:
        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        query = f"'{DRIVERID}' in parents and name starts with '寮食堂献立表' and trashed = false"

        results = service.files().list(
            q=query,
            pageSize=100,  # 必要に応じて変更可能
            fields="nextPageToken, files(id, name, mimeType, createdTime)"
        ).execute()
        items = results.get("files", [])

        if not items:
            print("No files found.")
            return
        
        time = []
        Id = []
        print("Files:")
        for item in items:
            print(f"{item['name']} ({item['id']}) created at {item['createdTime']}")
            t = datetime.fromisoformat(item["createdTime"])
            Id.append(item["id"])
            time.append(t)

        recent = max(time)
        FILEID = Id[time.index(recent)]

        request = service.files().get_media(fileId=FILEID)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

        # with open("output.pdf", "wb") as f:
        #     f.write(file.getvalue())

        # FILENAME = strnow()
        # upload_bucket.put_object(
        #     Key = FILENAME + ".pdf",
        #     Body = file.getvalue()
        # )

        return file

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")