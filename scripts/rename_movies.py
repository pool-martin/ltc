#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create_splits.py
#  
#  Copyright 2017 Joao Paulo Martin <joao.paulo.pmartin@gmail.com>
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
Create Splits to be used in torch scheme. 
- Authors: Joao Paulo Martin (joao.paulo.pmartin@gmail.com) 
''' 

import argparse, os, time
from joblib import Parallel, delayed  
import multiprocessing
from subprocess import call

validation = ['vNonPorn000482', 'vNonPorn000381', 'vNonPorn000194', 'vPorn000361', 'vNonPorn000982', 'vPorn000659', 'vNonPorn000160', 'vNonPorn000837', 'vPorn000429', 'vNonPorn000127', 'vNonPorn000445', 'vNonPorn000188', 'vNonPorn000836', 'vNonPorn000670', 'vPorn000825', 'vNonPorn001000', 'vPorn000491', 'vNonPorn000221', 'vNonPorn000264', 'vPorn000312', 'vNonPorn000076', 'vPorn000916', 'vNonPorn000378', 'vNonPorn000224', 'vNonPorn000570', 'vPorn000466', 'vNonPorn000532', 'vNonPorn000216', 'vNonPorn000108', 'vPorn000794', 'vNonPorn000001', 'vPorn000228', 'vPorn000739', 'vPorn000147', 'vNonPorn000443', 'vPorn000291', 'vNonPorn000794', 'vPorn000615', 'vNonPorn000299', 'vNonPorn000011', 'vPorn000880', 'vNonPorn000040', 'vNonPorn000280', 'vPorn000539', 'vPorn000723', 'vPorn000321', 'vPorn000884', 'vNonPorn000924', 'vPorn000069', 'vPorn000329', 'vPorn000257', 'vPorn000102', 'vNonPorn000828', 'vPorn000450', 'vPorn000135', 'vPorn000918', 'vPorn000635', 'vPorn000574', 'vPorn000049', 'vNonPorn000267', 'vPorn000680', 'vNonPorn000999', 'vPorn000083', 'vPorn000641', 'vNonPorn000710', 'vNonPorn000513', 'vPorn000311', 'vPorn000942', 'vNonPorn000257', 'vPorn000516', 'vNonPorn000336', 'vNonPorn000727', 'vPorn000935', 'vPorn000512', 'vPorn000582', 'vNonPorn000614', 'vPorn000957', 'vPorn000900', 'vNonPorn000770', 'vNonPorn000498', 'vNonPorn000460', 'vPorn000682', 'vNonPorn000525', 'vPorn000422', 'vPorn000085', 'vPorn000362', 'vPorn000917', 'vNonPorn000477', 'vPorn000579', 'vNonPorn000082', 'vNonPorn000247', 'vPorn000463', 'vNonPorn000239', 'vNonPorn000580', 'vNonPorn000489', 'vPorn000372', 'vNonPorn000543', 'vNonPorn000475', 'vPorn000416', 'vPorn000390']

def load_args():
	ap = argparse.ArgumentParser(description='Extract rgb frames from video list.')
	ap.add_argument('-i', '--data-set-path',
					dest='videos_path',
					help='path to the folder of videos.',
					type=str, required=False)
	ap.add_argument('-o', '--output-path',
					dest='output_path',
					help='path to output the extracted frames.',
					type=str, required=False)
##	ap.add_argument('-s', '--rescale',
##					dest='rescale_format',
##					help='WxH to rescale the image',
##					type=str, required=False, default = "")
#	ap.add_argument('-cc', '--cpu-count',
#					dest='cpu_count',
#					help='quantity of cpu threads to open.',
#					type=int, required=False, default=0)
#					
	args = ap.parse_args()
	
	print args
	
	return args


def ffmpeg_extract_frames(video_path, walked_tree, args):

	video_name = os.path.basename(video_path).split('.')[0]
	if video_name not in validation:
		return
	video_dir = os.path.join(args.output_path, walked_tree, video_name)
	if not os.path.isdir(video_dir):
		os.makedirs(video_dir) 

	balanced_frame_rate = args.output_frame_rate
	if args.class_to_balance and args.class_to_balance in video_name:
		output_frame_rate = int(args.output_frame_rate) * args.balance_rate
		balanced_frame_rate = str(output_frame_rate)

	command = "ffmpeg -i " + video_path + " -r " + balanced_frame_rate
#	if args.rescale_format:
#		command = command + " -s " + args.rescale_format
#	if "tif" in args.output_format:
#		command = command + " -pix_fmt rgb24 -vcodec tiff  " + os.path.join(video_dir, video_name + ".%7d." + args.output_frame_rate + "." + args.output_format)
#	else:
#		command = command + " " + os.path.join(video_dir, video_name + ".%7d." + args.output_frame_rate + "." + args.output_format)
	print command

	call(command, shell=True)
	#set_localization_flag(video_path, video_dir, video_name, args)
#	set_localization_flag("/DL/2kporn/videos/" + video_name , "/data/dsc_middle/1_s/" + video_name, video_name, args)

def opencv_extract_frames(video_path, walked_tree, args):

	video_name = os.path.basename(video_path).split('.')[0]

	video_dir = os.path.join(args.output_path, walked_tree, video_name)
	if not os.path.isdir(video_dir):
		os.makedirs(video_dir) 

	command = "/workspace/LTC/flow_toolbox/flow_video -o " + video_dir + " " + video_path 
	print(command)

	call(command, shell=True)
	#set_localization_flag(video_path, video_dir, video_name, args)
#	set_localization_flag("/DL/2kporn/videos/" + video_name , "/data/dsc_middle/1_s/" + video_name, video_name, args)

def set_localization_flag(video_source_path, video_dir, video_name, args):
	label_file = os.path.dirname(video_source_path) + "/../etf/" + video_name + ".etf"
	#print label_file
	#print "video dir %s " % video_dir
	labels = get_localization_labels(label_file)
	#print "video file : %s | labels %s" % (label_file, labels)
	
	for root, dirs, files in os.walk(video_dir):
		#print "Now in root %s" %root
		for file in files:
			#print "file :%s" % file
			#file name before change = vNonPorn000775.0000011.1.tif = VideoName.FrameCount.FrameRate2Extract.tif
			file_data = file.split('.')
			#Calc Localization flag:
			if video_name[:5] == 'vPorn':
				frame_number = file_data[1]
				frame_rate = file_data[2]
				#frame_rate = '1'
				position = float(frame_number) / float(frame_rate)
				localization_flag = define_localization_label(labels, position)
				
			else:
				localization_flag = 0
		#if file.endswith(args.output_format):
			#file name after change = vNonPorn000775.0000011.1.1.tif = VideoName.FrameCount.FrameRate2Extract.localization_flag.tif
			new_name = "%s.%s.%s.%d.%s" % (file_data[0], file_data[1], file_data[2], localization_flag, file_data[3])
			#new_name = "%s.%s.%s.%d.%s.%s" % (file_data[0], file_data[1], "1", localization_flag, "tif", "dsc")
			#print "new_name : %s" % new_name
			#print "new_name : %s/%s" % (root, new_name)
			os.rename(root + "/" + file, root + "/" + new_name)
	

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

import glob, os

def rename(dir, pattern, titlePattern):
    for pathAndFilename in glob.iglob(os.path.join(dir, pattern)):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        os.rename(pathAndFilename, 
                  os.path.join(dir, titlePattern % title + ext))

def create_splits(folder, cpu_count, args):
	files, file_paths, directories, directory_paths = get_dir_content(folder)
	if file_paths:

		print "Extract from " + folder
		
		rename(folder, r'*.t7', r'%s.avi')

	if directory_paths:
		for dir_path in directory_paths:
			create_splits(dir_path, cpu_count, args)

		
def main():
	args = load_args()
	
	print '> Ceate splits from videos -', time.asctime( time.localtime(time.time()) )
	
#	cpu_count = multiprocessing.cpu_count()
	cpu_count = 6
#	if args.cpu_count != 0:
#		cpu_count = args.cpu_count
	
	create_splits(r'/data/torch/ltc/datasets/UCF101/flow/t7/', cpu_count, args)
	
	print '\n> Ceate splits  from videos done -', time.asctime( time.localtime(time.time()) )
	
	return 0


if __name__ == '__main__':
	main()
