import argparse
import logging as log
import os
import shutil
import time
from datetime import datetime


log.getLogger().setLevel(log.INFO)
parser = argparse.ArgumentParser(
    description='This is a script for organizing photos by date')
parser.add_argument(
    '-s', '--src', help='the directory you want to organize', nargs='?', default=os.getcwd())
args = parser.parse_args()

path = args.src

#organized extensions
organized_extensions = ['heic', 'jpg', 'jpeg', 'png', 'gif', 'tiff', 'psd', 'mov', 'mp4']

# Ignored extensions
ignore_dirs = ['.git', '.venv', 'organized-iamges']
ignore_files = ['.gitignore']

''' Directory structure for moving images
    %Y: 4 digit 
    %y: 2 digit
    %B: full name month 
    %b
    %d: day 2digit
'''
dir_format = '%Y/%B'

orgnized_images = 'organized-images'

# Create required folders 
need_review = 'needs-review'
duplicate_dir = 'duplicate-files'

if not os.path.isdir(need_review):
    os.mkdir(need_review)
    log.info("need_rewiew directory created.")


if not os.path.isdir(duplicate_dir):
    os.mkdir(duplicate_dir)
    log.info("duplicate_dir directory created.")


def should_organized(file_name):
    splits = file_name.split('.')

    if splits[-1].lower() in organized_extensions:
        return True
    return False


def convert_date(timestamp, format_date):
    date = datetime.utcfromtimestamp(timestamp).strftime(format_date)
    return date


def check_duplicate_file(src_path, des_path):
    if os.path.exists(des_path) and src_path != des_path:
        if get_image_date(src_path) == get_image_date(des_path):
            return True
        else:
            return False
    return False


def get_image_date(path):
    ctime = time.ctime(os.path.getmtime(path))

    image_date = datetime.strptime(ctime, '%a %b %d %H:%M:%S %Y')
    image_date = image_date.strftime(dir_format)

    return image_date
    


def file_dates(path):
    for root, dirs, files in os.walk(path):

        if any(e in root.split('/') for e in ignore_dirs) or any(f in files for f in ignore_files):
            continue

        for filename in files:
            file_path = os.path.join(root, filename)

            if should_organized(filename):
                try:
                    image_date = get_image_date(file_path)
                    new_path = os.path.join(path, orgnized_images, image_date)

                    if not os.path.isdir(new_path):
                        os.makedirs(new_path)
                        log.info(f'path {new_path} created.')

                    moved_path = os.path.join(new_path, filename)

                    if file_path == moved_path:
                        continue

                    if not check_duplicate_file(file_path, moved_path):
                        if not os.path.exists(moved_path):
                            shutil.move(file_path, new_path)
                        else:
                            shutil.move(file_path,
                                        os.path.join(new_path, convert_date(os.path.getctime(file_path), '%Y-%m-%d') +
                                                     os.path.splitext(file_path)[1]))
                    else:
                        shutil.move(file_path, duplicate_dir)

                except Exception as err:
                    print(err)

            else:
                try:
                    exist_path = os.path.join(need_review, filename)
                    if file_path == exist_path:
                        continue
                    if not ignore_files(file_path):
                        if not check_duplicate_file(file_path, exist_path):
                            shutil.move(file_path, need_review)
                        else:
                            shutil.move(file_path, duplicate_dir)
                except:
                    pass


file_dates(path)
