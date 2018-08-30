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
Find videos with issues in extraction. 
- Authors: Joao Paulo Martin (joao.paulo.pmartin@gmail.com) 
''' 

import argparse, os, time
import cv2
from joblib import Parallel, delayed  
import multiprocessing
from subprocess import call


def load_args():
	ap = argparse.ArgumentParser(description='Find videos with issues in extraction.')
	ap.add_argument('-i', '--data-set-path',
					dest='videos_path',
					help='path to the videos dataset dir.',
					type=str, required=True)
	ap.add_argument('-xi', '--extracted-path',
					dest='extracted_path',
					help='path to the extracted dataset dir.',
					type=str, required=True)
	args = ap.parse_args()
	print args
	return args

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

def opencv_findDefectiveExtraction(video_path, walked_tree, args):

	video_name = os.path.basename(video_path).split('.')[0]



	etf_time = os.path.dirname(video_path) + "/../etf/" + video_name + ".etf"
	etf_frame = os.path.dirname(video_path) + "/../etf_frame/" + video_name + ".etf"
	video_fps = os.path.dirname(video_path) + "/../video_fps/" + video_name + ".etf"
	video_dir = os.path.join(args.extracted_path, video_name)
	video_dir_flow = video_dir.replace('rgb', 'flow')

	count_dir = len([name for name in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, name))])
	count_dir_flow = len([name for name in os.listdir(video_dir_flow) if os.path.isfile(os.path.join(video_dir_flow, name))])
	count_dir_flow = (count_dir_flow - 1)/2 

	print "video path %s " % video_path

	cap = cv2.VideoCapture(video_path)
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	fps =  int(cap.get(cv2.CAP_PROP_FPS))
	cap.set(cv2.CAP_PROP_POS_FRAMES,length-1); #Set index to last frame
	read_duration = float(cap.get(cv2.CAP_PROP_POS_MSEC))
	cap.release()
	
	calc_duration = (length * 1000)/fps
	
	labels = get_localization_labels(etf_time)
	
	etf_duration = (labels[0][1][0] + labels[0][1][1]) * 1000
	
	
	print video_fps
	with open(video_fps, "r") as f:
		saved_fps = f.read()

	if len(saved_fps):
		saved_fps = int(saved_fps)
	else:
		saved_fps = 0
	
	if abs(length - count_dir) > 4:
		print "video %s | frames divergence CAP_PROP_FRAME_COUNT [%d] count_dir [%d]" % (video_name, length, count_dir)

	if abs(fps != saved_fps) > 1 :
		print "video %s | frames divergence CAP_PROP_FPS [%d] saved_fps [%d]" % (video_name, fps, saved_fps)
		
	if (abs(etf_duration - calc_duration) > 100):
		print "video %s | duration divergence CAP_PROP_POS_MSEC [%d] calc_duration [%d]" % (video_name, read_duration, calc_duration)
	if abs(count_dir - count_dir_flow) > 4:
		print "video %s | flow_rgb_divergence count_dir [%d] count_dir_flow [%d]" % (video_name, count_dir, count_dir_flow)

#	if (abs(read_duration - etf_duration) > 100):
#		print "video %s | duration divergence CAP_PROP_POS_MSEC [%d] etf_duration [%d]" % (video_name, read_duration, etf_duration)


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



def findDefectiveExtraction(folder, cpu_count, args):

	files, file_paths, directories, directory_paths = get_dir_content(folder)
	if file_paths:
		numjobs = min(len(file_paths), cpu_count)
		print "verifying from " + folder + ", using",numjobs,"threads."
		
		Parallel(n_jobs=numjobs, verbose=10)(delayed(opencv_findDefectiveExtraction)(file_path, folder[len(args.videos_path)+1:], args) for file_path in file_paths)

	if directory_paths:
		for dir_path in directory_paths:
			findDefectiveExtraction(dir_path, cpu_count, args)


def main():
	args = load_args()

	print '> Verifying videos extraction -', time.asctime( time.localtime(time.time()) )

	cpu_count = multiprocessing.cpu_count()
	cpu_count = 10
	findDefectiveExtraction(args.videos_path, cpu_count, args)
	print '\n> Verifying videos extraction done -', time.asctime( time.localtime(time.time()) )
	return 0


if __name__ == '__main__':
	main()
