from os import listdir
from os.path import isfile, exists, join, splitext
from ntpath import basename

def num_of_files(dir, extension=None):
    if not exists(dir):
        return 0
    
    return len(list_files(dir, extension))

def list_files(dir, extension=None):
    if not exists(dir):
        return []
    
    def matches_criteria(path):
        full_path = join(dir, path)

        if not isfile(full_path):
            return False
        
        if (extension != None):
            splitted = splitext(full_path)
            return splitted[1] == extension
        else:
            return True
    
    return [join(dir, path) for path in listdir(dir) if matches_criteria(path)]

def get_base_name(file):
    base_name = basename(file)
    splitted = splitext(base_name)
    return splitted[0]
