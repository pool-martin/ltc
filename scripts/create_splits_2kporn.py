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

def load_args():
	ap = argparse.ArgumentParser(description='Extract rgb frames from video list.')
	ap.add_argument('-i', '--data-set-path',
					dest='videos_path',
					help='path to the folder of videos.',
					type=str, required=False, default='/home/jp/DL/2kporn/folds')
	ap.add_argument('-o', '--output-path',
					dest='output_path',
					help='path to output the extracted frames.',
					type=str, required=False)
	ap.add_argument('-s', '--split-number',
					dest='split_number',
					help='split number.',
					type=str, required=False, default='s1')
	args = ap.parse_args()
	
	print args
	
	return args

def get_video_patches(folder, video_class, video_name):
	video_patches = []
	for file in os.listdir(os.path.join(folder, video_class)):
		if video_name in file:
			video_patches.append(file)
	return video_patches
		
def create_splits(folder, args):
	#with open('/home/jp/EQM/torch/ltc/scripts/splits/classInd.txt') as f:
	#	content = f.readlines()
	content = ["1 NonPorn","2 Porn"]
	video_classes = ["NonPorn","Porn"]
	
	#creating folder to every class
	for line in content:
		split_content = line.strip().split(' ')
		command = "mkdir -p " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/train/', split_content[1])
		call(command, shell=True)
		command = "mkdir -p " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/test/', split_content[1])
		call(command, shell=True)
		command = "mkdir -p " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/validation/', split_content[1])
		call(command, shell=True)
		command = "mkdir -p " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/svm_train/', split_content[1])
		call(command, shell=True)
		command = "mkdir -p " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/svm_validation/', split_content[1])
		call(command, shell=True)

	positive_network_set = []
	negative_network_set = []
	positive_network_validation_set = []
	negative_network_validation_set = []
	positive_network_training_set = []
	negative_network_training_set = []
	positive_svm_validation_set = []
	negative_svm_validation_set = []
	positive_svm_training_set = []
	negative_svm_training_set = []

	full_dir_path = os.path.join(folder, args.split_number)
	
	###########################################
	#collecting all split1 training videos

	positive_network_training_set_path = os.path.join(full_dir_path, 'positive_network_training_set.txt')
	negative_network_training_set_path = os.path.join(full_dir_path, 'negative_network_training_set.txt')
	with open(positive_network_training_set_path) as f:
		content = f.readlines()
	with open(negative_network_training_set_path) as f:
		content = content + f.readlines()
	
	#getting the patches to each video and saving it in the right class
	for line in content:
		video_name = line.strip().split(' ')[0]
		print video_name
		#train
		for video_class in video_classes:
			video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
			for patch in video_patches:
				command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/train/', video_class, patch[:-3])
				print command
				call(command, shell=True)

	###########################################
	#collecting all split1 validation videos

	positive_network_validation_set_path = os.path.join(full_dir_path, 'positive_network_validation_set.txt')
	negative_network_validation_set_path = os.path.join(full_dir_path, 'negative_network_validation_set.txt')
	with open(positive_network_validation_set_path) as f:
		content = f.readlines()
	with open(negative_network_validation_set_path) as f:
		content = content + f.readlines()
		
		#getting the patches to each video and saving it in the right class
	for line in content:
		video_name = line.strip().split(' ')[0]
		print video_name
		#train
		for video_class in video_classes:
			video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
			for patch in video_patches:
				command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/validation/', video_class, patch[:-3])
				print command
				call(command, shell=True)
	

	###########################################
	#collecting all split1 svm training videos

	positive_svm_training_set_path = os.path.join(full_dir_path, 'positive_svm_training_set.txt')
	negative_svm_training_set_path = os.path.join(full_dir_path, 'negative_svm_training_set.txt')
	with open(positive_svm_training_set_path) as f:
		content = f.readlines()
	with open(negative_svm_training_set_path) as f:
		content = content + f.readlines()
	
	#getting the patches to each video and saving it in the right class
	for line in content:
		video_name = line.strip().split(' ')[0]
		print video_name
		#train
		for video_class in video_classes:
			video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
			for patch in video_patches:
				command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/svm_train/', video_class, patch[:-3])
				print command
				call(command, shell=True)

	###########################################
	#collecting all split1 svm validation videos

	positive_svm_validation_set_path = os.path.join(full_dir_path, 'positive_svm_validation_set.txt')
	negative_svm_validation_set_path = os.path.join(full_dir_path, 'negative_svm_validation_set.txt')
	with open(positive_svm_validation_set_path) as f:
		content = f.readlines()
	with open(negative_svm_validation_set_path) as f:
		content = content + f.readlines()
		
		#getting the patches to each video and saving it in the right class
	for line in content:
		video_name = line.strip().split(' ')[0]
		print video_name
		#train
		for video_class in video_classes:
			video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
			for patch in video_patches:
				command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/svm_validation/', video_class, patch[:-3])
				print command
				call(command, shell=True)

	###########################################
	#collecting all split1 test videos
	with open('/home/jp/DL/2kporn/folds/s1_negative_test.txt') as f:
		content = f.readlines()
	with open('/home/jp/DL/2kporn/folds/s1_positive_test.txt') as f:
		content = content + f.readlines()

	#getting the patches to each video and saving it in the right class
	for line in content:
		video_name = line.strip().split(' ')[0]
		print video_name
		#test
		for video_class in video_classes:
			video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
			for patch in video_patches:
				command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/test/', video_class, patch[:-3])
				print command
				call(command, shell=True)

def main():
	args = load_args()
	
	print '> Ceate splits from videos -', time.asctime( time.localtime(time.time()) )
	
	create_splits(args.videos_path, args)
	
	print '\n> Ceate splits  from videos done -', time.asctime( time.localtime(time.time()) )
	
	return 0


if __name__ == '__main__':
	main()
