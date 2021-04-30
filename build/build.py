import os
import shutil
from zipfile import ZipFile
from os import path
from shutil import make_archive
import sys
from pip._internal import main as pip
import boto3

folder = f'src/Lambda/'
subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]
for lambda_name in subfolders:
    build_destination = f'build/lambda_{lambda_name}'
    build_origination = f'{folder}{lambda_name}'
    print(f"Checking to see if {build_origination} exists")
    # Check if file exists
    if path.exists(build_origination):
        src = path.realpath(build_origination)
        zipdestination = path.realpath(build_destination)
        #myzipfile = ZipFile(f"{zipdestination}.zip", mode='a')
        # now put things into a ZIP archive
        print("Installing Packages")
        shutil.copytree(src,zipdestination)
        pip(["install", "-r", f"{src}/requirements.txt", "-t", f"{zipdestination}"])
        shutil.make_archive(zipdestination,"zip",zipdestination)
        shutil.rmtree(zipdestination)

folder = f'src/Lex/Slots/'
subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]
for lambda_name in subfolders:
    build_destination = f'build/lexslot_{lambda_name}'
    build_origination = f'{folder}{lambda_name}'
    print(f"Checking to see if {build_origination} exists")
    # Check if file exists
    if path.exists(build_origination):
        src = path.realpath(build_origination)
        zipdestination = path.realpath(build_destination)
        shutil.copytree(src,zipdestination)
        shutil.make_archive(zipdestination,"zip",zipdestination)
        shutil.rmtree(zipdestination)