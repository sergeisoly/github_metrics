#!/usr/bin/env python

"""
Utility for uploading all csv files in current directory to Google Drive
also creates file with shared links to that files

Before runnig you should install Pydrive with pip or conda and
create client_secrets.json file to get access to your Google Drive account.
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
    file_drive = drive.CreateFile()
    file_drive.SetContentFile(file)
    file_drive.Upload()
    permission = file_drive.InsertPermission({
                        'type': 'anyone',
                        'value': 'anyone',
                        'role': 'reader'})
    link = file_drive['alternateLink']
    drive_links.write(f"{file} link: {link}\n")
    print(f"The file: {file} has been uploaded")
drive_links.close()

print("All files have been uploaded")
