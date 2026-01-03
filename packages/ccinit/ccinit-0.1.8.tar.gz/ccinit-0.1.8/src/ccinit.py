#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2026 Your Name
import os
import re
import sys
import subprocess
libraries = []
already_done = {}
files = {}
dependencies = {}
def process(text, except_if, url_arg):
    global libraries
    global files
    global dependencies
    global already_done
    open_file = open(text, "r")
    read = open_file.read()
    open_file.close()
    if text != except_if:
        already_done[text] = False
        files[text] = read
        dependencies[text] = []
    if(len(read) >= 2):
        if ((read[0]) + (read[1])) == '/*':
            asterisk = False
            integer = 2
            for character in read[2:]:
                if (character) == '*':
                    asterisk = True
                elif (character) == '/':
                    if asterisk:
                        integer -= 1
                        break
                elif (character) == '\n':
                    integer = 2
                    break
                integer += 1
            array = read[2:integer].split(" ")
            new_array = []
            old = []
            try:
                old = url_arg.split("/")
            except:
                old = []
            count = 0
            for string in array:
                if len(string) > 0:
                    if string[0] == '/':
                        count = 0
                        for character in string:
                            if character == '/':
                                count += 1
                        new_array.append( "/".join(old[:(len(old) - count)]) + string )
                    else:
                        new_array.append( string )
                        old = string.split("/") 
            for url in new_array:
                divisions = url.split("/")
                if text != except_if:
                    dependencies[text].append( divisions[len(divisions) - 1] )
                libraries.append(divisions[len(divisions) - 1])
                try:            
                    read_file = open(divisions[len(divisions) - 1], "r")
                    read_file.read()
                    read_file.close()
                    process(divisions[len(divisions) - 1], except_if, url)
                except:
                    result = subprocess.run(["wget", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    process(divisions[len(divisions) - 1], except_if, url)
def function(argument):
    global libraries
    global files
    global dependencies

    include = '#include'
    process(argument, argument, "")
    print("Dependencies:")
    for dependency in dependencies:
        if dependency != argument:
            os.remove(dependency)
        print("\t", dependency)

    read_file = open("main.c", "r")
    global already_done
    text_read_file = read_file.read()
    read_file.close()

    write_file = open("main-backup.c", "w")
    write_file.write(text_read_file)
    write_file.close() 
    write_file_2 = open("main.c", "w")
    
    where = 0
    if(len(text_read_file) >= 2):
        if ((text_read_file[0]) + (text_read_file[1])) == '/*':
            asterisk = False
            where = 2
            for character in text_read_file[2:]:
                if (character) == '*':
                    asterisk = True
                elif (character) == '/':
                    if asterisk:
                        where -= 1
                        break
                elif (character) == '\n':
                    where = 2
                    break
                where += 1
    str_ = [text_read_file[0:(where)], "*/\n"]

    includes = []
    new_boolean = True
    actual_files = []
    files[argument] = text_read_file
    files_keys = list( files.keys() )
    while new_boolean: # while not all have been added to the .c file
        file_count = len(files) - 1
        while file_count >= 0:
            boolean = False
            key = files_keys[file_count]
            if argument != key:
                for dependence in dependencies[key]:
                    if already_done[dependence] == False:
                        boolean = True
            if boolean:
                file_count -= 1
                break
            file = files[key]
            position = file.find("\n\n")
            str__ =  file[0:(position + 1)]
            if key != argument:
                actual_files.append(key)
            i = 0;
            while(i < len(str__)):
                _str = str__[i:(i + len(include))]
                if _str == include:
                    an_include = str__[(i + len(include) + 1):]
                    end = an_include.find("\n")
                    the_str = an_include[:end]
                    if the_str not in includes:
                        includes.append(the_str)
                i += 1
            already_done[key] = True
            file_count -= 1
        new_boolean = False
        for value in already_done:
            if value == False:
                new_boolean = True
    for include_item in includes:
        str_.append("#include ")
        str_.append(include_item)
        str_.append("\n")

    str_.append("\n")
    
    for key in actual_files:
        position = files[key].find("\n\n")
        str_.append( "\n" )
        str_.append( files[key][(position + 2):] )

    pos = text_read_file.find('\n/*main*/')
    text_read_file_edit = text_read_file[pos:]
    str_.append(text_read_file_edit)

    write_file_2.write("".join(str_))
    write_file_2.close()
    print("Job done.")
def main():
    if len(sys.argv) > 1:
        if sys.argv[1] != '--help':
            function(sys.argv[1])
        else:
            print("Documentation: https://github.com/codemanticism/CCinit/tree/main")
            print("ccinit -> Setups a main.c file for you in the correct format already.")
            print("ccinit main.c -> Downloads dependencies and puts it all into the file in question.")                    
    else:
        try:
            file_open = open("main.c", "r")
            file_open.read()
            file_open.close()
            
            function("main.c")
        except:
            file_write = open("main.c", "w")
            file_write.write('/**/\n//^Where the URLs go.\n/*main*/\nint main(){\n}')
            file_write.close() 
if __name__ == "__main__":
    main()
