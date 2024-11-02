from lib.downloadPDF import downloadPDF
from lib.pdftocsv import pdf2csv
from lib.csvtojson import csv2json

import io
import boto3
from datetime import datetime

BUCKET_NAME = "kondate-json"
s3 = boto3.resource("s3")
upload_bucket = s3.Bucket(BUCKET_NAME)

def strnow():
    return datetime.now().strftime("%Y%m%d%H%M")

def lambda_handler(event, context):
    print("running")
    pdfbinary = downloadPDF()
    csv, date = pdf2csv(pdfbinary)
    s = csv2json(csv, date)


    upload_bucket.put_object(
        Key = date[0].replace("/", "") + ".json",
        Body = s,
        # metadata = {
        #     "start": date[0],
        #     "end": date[1]
        # }
    )

    print("Done")