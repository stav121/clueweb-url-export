#!/bin/env python

#   Author      :   Stavros Grigoriou
#   GitHub      :   https://github.com/unix121
#   Date        :   2 December, 2017
#   Description :   Python script used to export URLs from ClueWeb09 database
#   Usage       :   python clueweb_export.py /input/directory/ /output/directory/

import gzip
import sys
import re
import urlmarker
import os
import glob
from hurry.filesize import size
import time
import json
from datetime import timedelta

# Output function
def output(  output_size , read_size , bar , time ):
    print( "\x1b[0;33;40m [%s]\x1b[0m\x1b[0;31;40m Read Size:\x1b[0m %s-- \x1b[0;31;40mOutput Size:\x1b[0m %s-- \x1b[0;31;40mTime Elapsed:\x1b[0m %s----" % ( bar, read_size, output_size, time ) , end ='\r' )

# Progress bar (basic)
def progress_bar( counter ):
    if counter < 2000:
        counter = counter + 1
        out = ">-----"
    elif counter >= 2000 and counter < 4000:
        counter = counter + 1
        out = "->----"
    elif counter >= 4000 and counter < 6000:
        counter = counter + 1
        out = "-->---"
    elif counter >= 6000 and counter < 8000:
        counter = counter + 1
        out = "--->--"
    elif counter >= 8000 and counter < 10000:
        counter = counter + 1
        out = "---->-"
    elif counter >= 10000 and counter < 12000:
        counter = counter + 1
        if counter == 11999:
            counter = 0
        out = "----->"

    return counter, out

# Progress bar (export)
def progress_bar_export( counter ):
    if counter < 5000:
        counter = counter + 1
        out = ">-----"
    elif counter >= 5000 and counter < 10000:
        counter = counter + 1
        out = "->----"
    elif counter >= 10000 and counter < 15000:
        counter = counter + 1
        out = "-->---"
    elif counter >= 15000 and counter < 20000:
        counter = counter + 1
        out = "--->--"
    elif counter >= 20000 and counter < 25000:
        counter = counter + 1
        out = "---->-"
    elif counter >= 25000 and counter < 30000:
        counter = counter + 1
        if counter == 29999:
            counter = 0
        out = "----->"

    return counter, out


if __name__=="__main__":

    # Command line argument parsing
    input_path=sys.argv[1]
    output_path=sys.argv[2]
    clueweb_version=sys.argv[3]
    source=sys.argv[4]

    # Variable initialization
    total_files = 0
    start_time = time.time()
    exported_files = []

    # Loop for every file in the folder given
    for filename in os.listdir( input_path ):

        counter = 0
        print("\x1b[0;31;40m > File: \x1b[0m%s" % input_path+filename)
        total_files = total_files + 1

        total_urls = 0
        total_read_size = 0
        loop_count = 0
        final_urls = []

        current_path = input_path + filename

        path_tok = current_path.replace("/"," ")
        path_tok = path_tok.replace("."," ")
        path_tok = path_tok.split()
        export_name = path_tok[-5]+"_"+path_tok[-4]+"_"+path_tok[-3]+".txt"
        export_name_json = path_tok[-5]+"_"+path_tok[-4]+"_"+path_tok[-3]+".json"

        exception_flag = False

        # Loop for every file
        try:
            with gzip.open( current_path , 'r' ) as f:
                # Loop for every line in the input file
                for line in f:
                    loop_count = loop_count + 1
                    total_read_size =total_read_size +  sys.getsizeof( line )
                    urls = re.findall( urlmarker.URL_REGEX, str(line) )

                    counter, bar = progress_bar( counter )

                    # Append every new URL and print output
                    for url in urls:
                        total_urls = total_urls + 1
                        final_urls.append( url )
                        output( size( sys.getsizeof( final_urls ) ), size( total_read_size ), bar, str(timedelta( seconds = time.time() - start_time) ) )
        except:
            print( "\n\x1b[0;31;40m [!] \x1b[0m Failed to read file!" )
            exception_flag=True
            pass

        if not exception_flag:
            # Print basic info
            print( "\x1b[0;33;40m [-DONE-]\x1b[0m" )
            print( "\x1b[0;33;40m > File number : \x1b[0m%d" % total_files )
            print( "\x1b[0;33;40m > Removing doubles...\x1b[0m" )

            # Remove doubles
            final_urls = set( final_urls )
            final_urls = list( final_urls )

            # More info
            print( "\x1b[0;33;40m > Total URLs: \x1b[0m%d" % total_urls )
            print( "\x1b[0;33;40m > Done! Total unique URLs: \x1b[0m%d" % len( final_urls ) )
            print( "\x1b[0;33;40m > Size:\x1b[0m %s" % size( sys.getsizeof( final_urls ) ) )

            # Export the data into JSON format
            data = {}
            data['urls'] = final_urls
            data['clueweb_version'] = clueweb_version
            data['url_count'] = str(len(final_urls))
            data['source'] = source
            ename = export_name.replace("."," ")
            ename = ename.split()
            data['exported_file'] = ename[0]
            json_data = json.dumps(data)

            with open(output_path+export_name_json, "w+" ) as out_file:
                if out_file.write( json_data ):
                    print( "\x1b[0;31;40m > Json file:\x1b[0m %s" % output_path+export_name_json )

            # Export the data in txt format
            with open(output_path+export_name, "w+" ) as out_file:
                for url in final_urls:
                    counter, ebar = progress_bar_export( counter )
                    print( "\x1b[0;34;40m [%s] Exporting the data in txt..." % ebar, end='\r' )
                    out_file.write( url + "\n" )

            print( "\x1b[0;34;40m [-DONE-]\x1b[0m" )

        # Empty the list
        final_urls = []

        if not exception_flag:
            print( "\x1b[0;34;40m > Text file: \x1b[0m%s" % output_path+export_name )

            filename = filename.replace( "." , " " )
            filename = filename.split()
            exported_files.append( filename[0] )
            exported_output = " "

            flag = True
            # Print information about the already exported files
            for file in exported_files:
                if flag == True:
                    flag = False
                    exported_output = exported_output + file
                else:
                    exported_output = exported_output + ", " + file

        print( "\n\x1b[0;31;40m------------------------------------------------------------------------------------------------------------------------\x1b[0m" )
        print( "\n\x1b[0;31;40mExported files: \x1b[0m" + exported_output )
        print( "\n\x1b[0;31;40m------------------------------------------------------------------------------------------------------------------------\x1b[0m" )
