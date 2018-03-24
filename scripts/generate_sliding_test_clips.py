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
generate_sliding_test_clips. 
- Authors: Joao Paulo Martin (joao.paulo.pmartin@gmail.com) 
''' 

dataRoot = '/data/torch/ltc/datasets/2kporn/';
import os
import math
from subprocess import call

def get_dir_content(folder):
	video_patches = []
	for file in os.listdir(os.path.join(folder)):
		video_patches.append(file)
	return video_patches

# Loop over three splits
for split in range(1,2):
#    testDir = os.path.join(dataRoot, 'splits', 'split' + str(split), 'validation');
    testDir = os.path.join(dataRoot, 'rgb', 'jpg');
    # Loop over possible window sizes
    for W in range(16,17):
        # Loop over possible skips
        for skip in range (4, 5):
            targetDir = os.path.join(dataRoot, 'splits', 'split' + str(split), 'test_'+ str(W) + '_' + str(skip));
            
            classes = ['NonPorn','Porn']
            
            C = len(classes);
            
            for video_class in classes:
                print ('Class: ' + video_class);
                command = "mkdir -p " + os.path.join(targetDir, video_class)
                print command
                call(command, shell=True)
                videos = get_dir_content(testDir)
                for video in videos:
                    print ('Class :' + video_class + ' - Video :' + video);
                    frames = get_dir_content(os.path.join(dataRoot, 'rgb', 'jpg', video));
                    totalDuration = len(frames); # note: nFlow = nRGB -1
                    
                    nClips = int(math.ceil((totalDuration - W)/skip) + 1);
                    if(totalDuration < W):
                        nClips = 1;
                        command = "touch ''%s_%04d.mp4''" % (os.path.join(targetDir, video_class, video), 1);
                        print command
                        call(command, shell=True)
                    
                    for tt in range(1,nClips + 1):
                        command = "touch ''%s_%04d.mp4''" % (os.path.join(targetDir, video_class, video), tt);
                        print command
                        call(command, shell=True)
                    
                
            
        
    

