import argparse
import logging as log
import os
import shutil
from datetime import datetime
from PIL import Image

log.getLogger().setLevel(log.INFO)
parser = argparse.ArgumentParser(
    description='This is a script for organizing photos by date')
parser.add_argument(
    '-s', '--src', help='the directory you want to organize', nargs='?', default=os.getcwd())
args = parser.parse_args()

path = args.src

#image extensions
image_extensions = ['heic', 'jpg', 'jpeg', 'png', 'gif', 'tiff']

# Ignored extensions
exts = ['.py']
ignore_dirs = ['.git', '.venv', 'organized-iamges']

# Directory structure for moving images
dir_format = '%Y/%b/%d'

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


def is_image(image_file):
    splits = image_file.split('.')

    if splits[-1] in image_extensions:
        return True
    return False


def ignore_files(path_file):
    if os.path.splitext(path_file)[1] in exts:
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
    img = Image.open(path)
    exif_date = img._getexif()

    # Get image date from EXIF if exist.
    try:
        image_date = datetime.strptime(
            exif_date[36867], '%Y:%m:%d %H:%M:%S')
        image_date = image_date.strftime(dir_format)
    except:
        image_date = convert_date(os.path.getctime(path), dir_format)
    return image_date


def file_dates(path):
    for root, dirs, files in os.walk(path):
        if any(e in root.split('/') for e in ignore_dirs):
            continue
        log.info(f'{root}')
        for filename in files:
            file_path = os.path.join(root, filename)
            # if is_image(filename):
            #     try:
            #         image_date = get_image_date(file_path)

            #         new_path = os.path.join(path, orgnized_images, image_date)
            #         if not os.path.isdir(new_path):
            #             os.makedirs(new_path)
            #             log.info(f'path {new_path} created.')

            #         moved_path = os.path.join(new_path, filename)
            #         if file_path == moved_path:
            #             continue
            #         if not check_duplicate_file(file_path, moved_path):
            #             if not os.path.exists(moved_path):
            #                 shutil.move(file_path, new_path)
            #                 log.info(f'{file_path} moved to {new_path}')
            #             else:
            #                 shutil.move(file_path,
            #                             os.path.join(new_path, convert_date(os.path.getctime(file_path), '%Y-%m-%d') +
            #                                          os.path.splitext(file_path)[1]))
            #         else:
            #             shutil.move(file_path, duplicate_dir)

            #     except Exception as err:
            #         print(err)

            # else:
            #     try:
            #         exist_path = os.path.join(need_review, filename)
            #         if file_path == exist_path:
            #             continue
            #         if not ignore_files(file_path):
            #             if not check_duplicate_file(file_path, exist_path):
            #                 shutil.move(file_path, need_review)
            #             else:
            #                 shutil.move(file_path, duplicate_dir)
            #     except:
            #         pass


file_dates(path)
