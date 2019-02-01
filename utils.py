import time
from os.path import basename, splitext, dirname
import ntpath

def current_time_in_millis() :
    return int(round(time.time() * 1000))

def _compute_output_path_from_file_path(file_path, extension, add_suffix = ""):
    head, tail = ntpath.split(file_path)
    tail = splitext(tail or ntpath.basename(head))[0]
    result_path = head + "/" if head else ""
    result_path+=tail+add_suffix+"."+extension
    return result_path
