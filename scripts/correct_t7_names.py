import os 

video_source_path = '/data/torch/ltc/datasets/2kporn/rgb/t7/'
video_classes = ["NonPorn","Porn"]

for video_class in video_classes:
	t7_dir = os.path.join(video_source_path, video_class)

	for root, dirs, files in os.walk(t7_dir):
		#print "Now in root %s" %root
		for file in files:
			if 'mp4' not in file:
				if 'vPorn' in file:
					new_name = file[:14] + '.mp4' + file[14:]
				else:
					new_name = file[:17] + '.mp4' + file[17:]
				print "new_name : %s" % new_name
				print "name : %s" % file
				os.rename(root + "/" + file, root + "/" + new_name)
