import argparse
import logging as log
import os
import shutil
import time
from datetime import datetime
import hashlib


log.getLogger().setLevel(log.INFO)
parser = argparse.ArgumentParser(
    description='This is a script for organizing photos by date')
parser.add_argument(
    '-s', '--src', help='the directory you want to organize', nargs='?', default=os.getcwd())
args = parser.parse_args()

path = args.src

#organized extensions
organized_extensions = ['heic', 'jpg', 'jpeg', 'png', 'gif', 'tiff', 'tif', 'cr2', 'psd', 'mov', 'mp4']

''' Directory structure for moving images
    %Y: 4 digit
    %y: 2 digit
    %B: full name month
    %b
    %d: day 2digit
'''
dir_format = '%Y/%B'

# Create required folders
organized_images = 'organized-images'
need_review = 'needs-review'
duplicate = 'duplicate-files'

duplicate_dir = os.path.join(path, duplicate)
need_review_dir = os.path.join(path, need_review)

# Ignored extensions
ignore_dirs = ['.git', '.venv', organized_images, need_review, duplicate ]
ignore_files = ['.gitignore']

# File for saveing hashes
data_file = os.path.join(path, '.hash_data.txt')
hash_keys = []

if not os.path.isdir(need_review_dir):
    os.mkdir(need_review_dir)
    log.info("need_rewiew directory created.")


if not os.path.isdir(duplicate_dir):
    os.mkdir(duplicate_dir)
    log.info("duplicate_dir directory created.")


def load_hash_file():
    try:
        with open(data_file, 'r') as file:
            hash_keys.append(file.read().split())
    except IOError:
        hash_keys = []


def save_hash_file():
    with open(data_file, 'w') as file:
        file.writelines('%s\n' % hashes for hashes in hash_keys)


def should_organized(file_name):
    splits = file_name.split('.')

    if splits[-1].lower() in organized_extensions:
        return True
    return False


def convert_date(timestamp, format_date):
    date = datetime.utcfromtimestamp(timestamp).strftime(format_date)
    return date


def check_duplicate_file(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        if file_hash not in hash_keys:
            hash_keys.append(file_hash)
            return False
        return True

    # if os.path.exists(des_path) and src_path != des_path:
    #     if get_image_date(src_path) == get_image_date(des_path):
    #         return True
    #     else:
    #         return False
    # return False


def get_image_date(path):
    ctime = time.ctime(os.path.getmtime(path))
    image_date = datetime.strptime(ctime, '%a %b %d %H:%M:%S %Y')
    image_date = image_date.strftime(dir_format)

    return image_date


def move_to_duplicate_folder(path, date):
    duplicate_path = os.path.join(duplicate_dir, date)
    if not os.path.isdir(duplicate_path):
        os.makedirs(duplicate_path)
    shutil.move(path, duplicate_path)


def file_dates(path):
    load_hash_file()
    for root, dirs, files in os.walk(path):
        if any(e in root.split('/') for e in ignore_dirs) or any(f in files for f in ignore_files):
            continue

        for filename in files:
            file_path = os.path.join(root, filename)
            image_date = get_image_date(file_path)
            if should_organized(filename):
                try:
                    new_path = os.path.join(path, organized_images, image_date)

                    if not os.path.isdir(new_path):
                        os.makedirs(new_path)

                    moved_path = os.path.join(new_path, filename)

                    if file_path == moved_path:
                        continue

                    if not check_duplicate_file(file_path):
                        if not os.path.exists(moved_path):
                            shutil.move(file_path, new_path)
                        else:
                            shutil.move(file_path, os.path.join(new_path, \
                                    convert_date(os.path.getctime(file_path),
                                                      '%Y-%m-%d') +
                                                     os.path.splitext(file_path)[1]))
                    else:
                        move_to_duplicate_folder(file_path, image_date)

                except Exception as err:
                    print(err)

            else:
                try:
                    exist_path = os.path.join(need_review_dir, filename)
                    if file_path == exist_path:
                        continue
                    if not check_duplicate_file(file_path):
                        shutil.move(file_path, need_review_dir)
                    else:
                        move_to_duplicate_folder(file_path, image_date)
                except Exception:
                    pass


file_dates(path)
save_hash_file()
