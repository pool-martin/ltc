#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  etf2frame.py
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
convert etf notation from time to frame based. 
- Authors: Joao Paulo Martin (joao.paulo.pmartin@gmail.com) 
''' 

import argparse, os, time
import cv2
from joblib import Parallel, delayed  
import multiprocessing
from subprocess import call


def load_args():
	ap = argparse.ArgumentParser(description='Extract rgb frames from video list.')
	ap.add_argument('-i', '--data-set-path',
					dest='videos_path',
					help='path to the videos dataset dir.',
					type=str, required=True)
	args = ap.parse_args()
	print args
	return args



def define_localization_label(labels, position):

	#the labels cames here sorted in reverse order.
	# so we can verify from the last of the video to the beggining if the possition \
	#fits a specific localization label in that piece of time.
	for label in labels:
		#print "label[0] %s" % label[0]
		#print "label[1] %s" % label[1]
		if position >= label[1][0]:
			if label[1][2] == 't':
				return 1
			else:
				return 0


#vPorn000235.mp4 1 296.858 4.0107 event - porn - f

def get_localization_labels(filename):
	import operator
	i = 0
	content = {}

	with open(filename) as f:
		lines = f.readlines()

	for line in lines:
		values = line.split(' ')
		content[i] = [float(values[2]), float(values[3]), values[8][:1]]
		i += 1

	sorted_labels = sorted(content.items(), key=operator.itemgetter(0), reverse = True )
	#print "sorted_labels :%s" % sorted_labels
	return sorted_labels

def mount_etf_frame(video_name, localization_flag):
	#Let try to identify blocks of '0' or '1' and create a list of something like:
	# video_name #start_frame #number_of_frames #class
	current_snippet_class = localization_flag[0]
	classes_snippets = []
	current_frame_qty = 1
#	current_snippet_qty = 1
	current_snippet_initial_position = 0  #0 based
	for i in range (1, len(localization_flag)):
		if localization_flag[i] == current_snippet_class:
			current_frame_qty = current_frame_qty + 1
		else:
			classes_snippets.append([current_snippet_initial_position, current_frame_qty, current_snippet_class])
#			current_snippet_qty = current_snippet_qty + 1
			current_snippet_class = localization_flag[i]
			current_snippet_initial_position = i
			current_frame_qty = 1
	classes_snippets.append([current_snippet_initial_position, current_frame_qty, current_snippet_class])
	
	str_snippet_classes = ""
	for i in range (len(classes_snippets)):
		str_snippet_classes = str_snippet_classes + video_name + ".mp4 " + \
		str(classes_snippets[i][0]) + " " + str(classes_snippets[i][1]) + " " + ('t' if classes_snippets[i][2] else 'f')  + "\r\n"
		#print str_snippet_classes
	
	return str_snippet_classes
	

def opencv_etf_2_frames(video_path, walked_tree, args):

	video_name = os.path.basename(video_path).split('.')[0]
#	video_dir = os.path.join(args.output_path, walked_tree, video_name)
#	if not os.path.isdir(video_dir):
#		os.makedirs(video_dir) 



	etf_time = os.path.dirname(video_path) + "/../etf/" + video_name + ".etf"
	etf_frame = os.path.dirname(video_path) + "/../etf_frame/" + video_name + ".etf"
	video_fps = os.path.dirname(video_path) + "/../video_fps/" + video_name + ".etf"
	video_length = os.path.dirname(video_path) + "/../video_length/" + video_name + ".etf"
	
	#print etf_time
	print "video path %s " % video_path
	labels = get_localization_labels(etf_time)

	#print "video file : %s | labels %s" % (etf_time, labels)

	cap = cv2.VideoCapture(video_path)
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	fps =  int(cap.get(cv2.CAP_PROP_FPS))
	cap.release()

	with open(video_fps, "w") as f:
		f.write(str(fps)) 
	with open(video_length, "w") as f:
		f.write(str(length)) 

	localization_flag = {}

	for i in range(0, length):
		#Calc Localization flag:
		position = float(i) / float(fps)
		localization_flag[i] = define_localization_label(labels, position)

	str_etf_frame = mount_etf_frame(video_name, localization_flag)
	with open(etf_frame, "w") as f:
		f.write(str_etf_frame)


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



def convertEtf2Frame(folder, cpu_count, args):

	files, file_paths, directories, directory_paths = get_dir_content(folder)
	if file_paths:
		numjobs = min(len(file_paths), cpu_count)
		print "Extract from " + folder + ", using",numjobs,"threads."
		
		Parallel(n_jobs=numjobs, verbose=10)(delayed(opencv_etf_2_frames)(file_path, folder[len(args.videos_path)+1:], args) for file_path in file_paths)

	if directory_paths:
		for dir_path in directory_paths:
			convertEtf2Frame(dir_path, cpu_count, args)


def main():
	args = load_args()

	print '> Generate frame based etf from videos -', time.asctime( time.localtime(time.time()) )

	cpu_count = multiprocessing.cpu_count()
	cpu_count = 1
	convertEtf2Frame(args.videos_path, cpu_count, args)
	print '\n> Generate frame based etf from done -', time.asctime( time.localtime(time.time()) )
	return 0


if __name__ == '__main__':
	main()
