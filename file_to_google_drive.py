#!/usr/bin/env python

"""
Utility for uploading all csv files in current directory to Google Drive
also creates file with shared links to that files

Before you should install Pydrive with pip or conda and
create client_secrets.json file to get access to your Dribe account.
Instruction: https://pythonhosted.org/PyDrive/quickstart.html
"""

import glob
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# access the drive
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# file to save links of files
drive_links = open('files_drive_links.txt', "w+")
for file in glob.glob("*.csv"):
    print(file)
    with open(file, "r") as f:
        fn = os.path.basename(f.name)
        file_drive = drive.CreateFile({'title': fn})
        file_drive.SetContentString(f.read())
    file_drive.Upload()
    permission = file_drive.InsertPermission({
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader'})
    link = file_drive['alternateLink']
    drive_links.write(f"{fn} link: {link}\n")
    print(f"The file: {fn} has been uploaded")
drive_links.close()

print("All files have been uploaded")
