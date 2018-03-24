import os 

video_source_path = '/data/torch/ltc/datasets/2kporn/flow/jpg/'

target_videos = ['vNonPorn000459','vNonPorn000690','vNonPorn000641','vNonPorn000934','vNonPorn000755','vPorn000427','vPorn000716','vPorn000419','vPorn000456','vPorn000426','vNonPorn000941','vPorn000423','vNonPorn000987','vNonPorn000424','vPorn000445','vNonPorn000797','vNonPorn000433','vNonPorn000245','vPorn000438','vNonPorn000849','vNonPorn000814','vNonPorn000421','vNonPorn000010','vNonPorn000966','vNonPorn000620','vNonPorn000434','vNonPorn000856','vPorn000459','vNonPorn000993','vNonPorn000537','vNonPorn000604','vPorn000446','vNonPorn000649','vNonPorn000853','vPorn000410','vNonPorn000449','vNonPorn000629','vPorn000416','vPorn000408','vNonPorn000426','vNonPorn000960','vNonPorn000603']

for video_name in target_videos:
	video_dir = os.path.join(video_source_path, video_name)

	for root, dirs, files in os.walk(video_dir):
		#print "Now in root %s" %root
		for file in files:
			#print "file :%s" % file
			#file name before change = vNonPorn000775.0000011.1.tif = VideoName.FrameCount.FrameRate2Extract.tif
			if '.mp_' in file:
				if 'vPorn' in file:
					new_name = file[:14] + '4' + file[14:]
				else:
					new_name = file[:17] + '4' + file[17:]
				print "new_name : %s" % new_name
#				print "name : %s" % file
				os.rename(root + "/" + file, root + "/" + new_name)
