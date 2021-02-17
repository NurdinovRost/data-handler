import hashlib
from collections import defaultdict
from tqdm import tqdm
import os
import dlib
import numpy as np
import shutil


def chunk_reader(fobj, chunk_size=1024):
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed


def check_for_duplicates(paths, hash=hashlib.sha1):
    hashes_by_size = defaultdict(list)  # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
    hashes_on_1k = defaultdict(list)  # dict of (hash1k, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
    hashes_full = {}   # dict of full_file_hash: full_path_to_file_string

    for path in paths:
        try:
            full_path = os.path.realpath(path)
            file_size = os.path.getsize(full_path)
            hashes_by_size[file_size].append(full_path)
        except (OSError,):
            continue

    for size_in_bytes, files in hashes_by_size.items():
        if len(files) < 2:
            continue

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                continue

    for __, files_list in hashes_on_1k.items():
        if len(files_list) < 2:
            continue

        for filename in files_list:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:
                    print("Duplicate found: {} and {}".format(filename, duplicate))
                    os.remove(duplicate)
                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                continue


def face_detect(images, path_face, path_not_face, path_multi_face):
    if not os.path.isdir(path_face):
        os.mkdir(path_face)
    if not os.path.isdir(path_not_face):
        os.mkdir(path_not_face)
    if not os.path.isdir(path_multi_face):
        os.mkdir(path_multi_face)
    detector = dlib.get_frontal_face_detector()
    for path in tqdm(images, desc="FACE DETECT"):
        img = dlib.load_rgb_image(path)
        file_name = os.path.split(path)[-1]
        dets = detector(img, 1)
        if len(dets) == 0:
            shutil.move(path, os.path.join(path_not_face, file_name))
        elif len(dets) == 1:
            shutil.move(path, os.path.join(path_face, file_name))
        else:
            shutil.move(path, os.path.join(path_multi_face, file_name))

