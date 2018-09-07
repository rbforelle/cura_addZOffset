#!/usr/bin/python
#coding:utf-8
import os
import re
import time


def addZOffset(filename, z_offset):
    # add suffix _modifie to get output file name
    filename_output = os.path.splitext(filename)[0] + "_modifie" + os.path.splitext(filename)[1]
    print "new_file =", filename_output

    f = open(filename_output,'w')
    n = 0  # edit_line_count

    with open(filename, 'r') as file_to_read:
        lines = file_to_read.readlines() # read all lines
        for line in lines:
            result = re.search("Z(\d+.?\d*)",line)  # find Z movement such as Z0.13
            if result!=None:
                f.write(";" + line)  # if found, Comment out the original line
                z_value_new = float(result.group(1)) + z_offset  # cal new z value with z_offset
                line_new = line.replace(result.group(),"Z"+str(z_value_new))  # replace the Z movement in this line
                # f.write(";offset=" + str(z_offset) + "\n")
                f.write(line_new)
                n+=1
            else:
                f.write(line)  # if z movement not countained, write directly
    print "edit_line_count =", n
    f.close()


def checkNewFile(path, old_file_list):
    # this func compares the gcode file list in the path with old_file_list
    # list all gcode files
    files = os.listdir(path)
    new_file_list = []
    for file in files:
        if not os.path.isdir(file):
            if os.path.splitext(file)[1] == ".gcode":
                full_path = path + file  # parse full_path
                modified_time = time.ctime(os.stat(full_path).st_mtime)
                if (full_path,modified_time) not in old_file_list:
                    new_file_list.append((full_path,modified_time))
    return new_file_list


if __name__ == '__main__':
    z_offset = 0.1
    sd_card_path = "H:/"
    print "z_offset=", z_offset


    file_list = []
    files_to_process = []
    # this script is intended to process the new gcode files generated by cura
    # so at first when the program is began or the sd card is insert
    # we should get the gcode file list as init
    # if sd card is pulled out, is_init will also be set True
    is_init = True

    # check sd card file list per 1 second
    # to get and process the new generated g code files
    while True:
        try:
            if is_init:
                file_list = checkNewFile(sd_card_path, [])  # init file_list
                print "init:", file_list
                is_init = False
            else:
                files_to_process = checkNewFile(sd_card_path, file_list)
                if files_to_process.__len__() > 0:
                    time.sleep(1) # give cura some time to write g code file
                    print "files_to_process:", files_to_process
                    for file_tuple in files_to_process:
                        addZOffset(file_tuple[0], z_offset)
                    files_to_process = []
                    file_list = checkNewFile(sd_card_path, [])  # init file_list
        except:
            print "no sd card"
            is_init = True

        time.sleep(1)
