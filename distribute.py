"""
Copyright © 2022 ascpial

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This python scripts helps you create a zip file of the resource pack, without
including source files, python scripts and documentation.

The scripts simply find all png, json (for models) and mcmeta files in the
assets folder and adds pack.mcmeta and pack.png to the archive.

The zip file is sent to the output folder (which is ignored by git), but you
can also choose to copy it to your minecraft resourcepacks folder or whatever
you want to help you test the pack.

In the future, the program will automatically detect changes and update the
pack if needed.
"""

import os
import sys
import glob
import json
import shutil
import zipfile
import argparse

ROOT_FILES = [
    "pack.png",
    "pack.mcmeta",
    "CREDITS.txt",
    "LICENCE.txt",
]
ROOT_FOLDERS = [
    "assets"
]

FILES = [
    "**/*.json",
    "**/*.mcmeta",
    "**/*.png",
]

def get_resourcepack_files(path: str) -> list:
    files = []

    for folder in ROOT_FOLDERS:
        for pattern in FILES:
            for file in glob.glob(
                os.path.join(path, folder, pattern),
                # root_dir=os.path.join(path, folder), # apparently this is not working with python 3.8
                recursive=True,
            ):
                files.append(file)
    
    for file in ROOT_FILES:
        file_path = os.path.join(path, file)
        if os.path.exists(file_path):
            files.append(file_path)
    
    return files

def create_archive(destination: str, files: list) -> zipfile.ZipFile:
    """Create a zip archive from a list of files
    destination: the path of the zip file
    files: the list of files to include in the archive
    """
    archive = zipfile.ZipFile(destination, 'w')

    for file in files:
        archive.write(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Texture pack packager',
        description='Takes the resource pack and removes all sources files',
    )
    parser.add_argument("--min", type=int, help="The minimum pack_format version to accept, crashes if not matching")
    parser.add_argument("--max", type=int, help="The maximum pack_format version to accpet, crashes if not matching")

    args = parser.parse_args()

    if args.min is not None or args.max is not None:
        pack_version = json.load(open("pack.mcmeta", 'r'))["pack"]["pack_format"]
        if args.min is not None and pack_version < args.min:
            print("The pack_format is below the minimal version required")
            sys.exit(10)
        if args.max is not None and pack_version > args.max:
            print("The pack_format is greater than the maximal version required")
            sys.exit(11)
    try:
        with open('./config.json') as file:
            configuration = json.load(file)
    except FileNotFoundError:
        configuration = {
            "folder": ".",
            "destination": "ComputerCreate.zip",
            "file_outputs": [],
        }
    files = get_resourcepack_files(configuration.get('folder', '.'))
    create_archive(
        configuration.get("destination", "output/ComputerCreate.zip"),
        files,
    )
    print(f"📄 Zip created at {configuration.get('destination', 'output/ComputerCreate.zip')}")

    for file in configuration.get('file_outputs', []):
        shutil.copy(
            configuration.get("destination", "output/ComputerCreate.zip"),
            file,
        )
        print(f"💾 File copied to {file}")

    print("✅ All done !")
