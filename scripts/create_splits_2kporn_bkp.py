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

	#collecting all split1 videos
	with open('/home/jp/DL/2kporn/folds/s1_negative_training.txt') as f:
		content = f.readlines()
	with open('/home/jp/DL/2kporn/folds/s1_positive_training.txt') as f:
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

	#collecting all split1 test videos
	with open('/home/jp/DL/2kporn/folds/s1_negative_test.txt') as f:
		content = f.readlines()
	with open('/home/jp/DL/2kporn/folds/s1_positive_test.txt') as f:
		content = content + f.readlines()

	#getting the patches to each video and saving it in the right class
	for line in content:
		video_name = line.strip().split(' ')[0]

		if video_name not in validation:
			#test
			for video_class in video_classes:
				video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
				for patch in video_patches:
					command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/test/', video_class, patch[:-3])
					print command
					call(command, shell=True)
		else:
			#validation
			for video_class in video_classes:
				video_patches = get_video_patches("/home/jp/EQM/torch/ltc/datasets/2kporn/rgb/t7/", video_class, video_name)
				for patch in video_patches:
					command = "touch " + os.path.join('/home/jp/EQM/torch/ltc/datasets/2kporn/splits/split1/validation/', video_class, patch[:-3])
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
