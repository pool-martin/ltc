#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  get_dimensions.py
#  
#  Copyright 2018 Joao Paulo Martin <joao.paulo.pmartin@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; 
#  either version 2 of the License, or (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#  PURPOSE.  See the GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth 
#  Floor, Boston, MA 02110-1301, USA.
#  
#  

''' 
get w and h dimensions of every video in dataset. 
- Authors: Joao Paulo Martin (joao.paulo.pmartin@gmail.com) 
''' 

import argparse, os, time
import cv2
from joblib import Parallel, delayed  
import multiprocessing
from subprocess import call


def load_args():
	ap = argparse.ArgumentParser(description='get w and h dimensions of every video in dataset.')
	ap.add_argument('-i', '--data-set-path',
					dest='videos_path',
					help='path to the videos dataset dir.',
					type=str, required=True)
	args = ap.parse_args()
	print args
	return args
dimensions = []

def opencv_getDimesions(video_path, walked_tree, args):

	video_name = os.path.basename(video_path).split('.')[0]
#	video_dir = os.path.join(args.output_path, walked_tree, video_name)
#	if not os.path.isdir(video_dir):
#		os.makedirs(video_dir) 



	video_dimensions = os.path.dirname(video_path) + "/../dimensions_video/" + video_name + ".etf"

	#print etf_time
	print "video path %s " % video_dimensions


	with open(video_dimensions, "r") as f:
		dimensions.append([video_name, f.read()])


def get_dir_content(directory):

    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """

    file_paths = []  # List which will store all of the full filepaths.
    files = []  # List which will store all of the files without path.
    directory_paths = []  # List which will store all of the full folderpaths.
    directories = []  # List which will store all of the folders without path.

    # Walk the tree.
    for root, directories_, files_ in os.walk(directory):
        for filename in files_:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.
            files.append(filename)
        for directory in directories_:
            # Join the two strings in order to form the full directory_path.
            directory_path = os.path.join(root, directory)
            directory_paths.append(directory_path)  # Add it to the list.
            directories.append(directory)
        break

    return files, file_paths, directories, directory_paths  # Self-explanatory.



def getDimesions(folder, cpu_count, args):

	files, file_paths, directories, directory_paths = get_dir_content(folder)
	if file_paths:
		numjobs = min(len(file_paths), cpu_count)
		print "Extract from " + folder + ", using",numjobs,"threads."
		
		Parallel(n_jobs=numjobs, verbose=10)(delayed(opencv_getDimesions)(file_path, folder[len(args.videos_path)+1:], args) for file_path in file_paths)

	if directory_paths:
		for dir_path in directory_paths:
			getDimesions(dir_path, cpu_count, args)


def main():
	args = load_args()

	print '> Generate frame based etf from videos -', time.asctime( time.localtime(time.time()) )

	cpu_count = multiprocessing.cpu_count()
	cpu_count = 1
	getDimesions(args.videos_path, cpu_count, args)
	print '\n> Generate frame based etf from done -', time.asctime( time.localtime(time.time()) )
	
	for video in dimensions:
		print "%s;%s" % (video[0],video[1])
	return 0


if __name__ == '__main__':
	main()
