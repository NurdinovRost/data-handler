import os


extensions = ('.jpg', '.png', '.jpeg')


def recursive_descent(path):
    files = []
    list_dir = os.listdir(path)
    for obj in list_dir:
        path_obj = os.path.join(path, obj)
        if os.path.split(path_obj)[1] == ".DS_Store":
            os.remove(path_obj)
            print(f"File {path_obj} has been deleted")
        if os.path.splitext(path_obj)[1] in extensions:
            files.append(path_obj)
        elif os.path.isdir(path_obj):
            files.extend(recursive_descent(path_obj))
    return files
