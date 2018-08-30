import argparse
import pickle
import sys
import numpy as np

def count_feats(file):
	with open(file) as f:
		total_feats = sum(1 for _ in f)
	return total_feats

def load_args():
	ap = argparse.ArgumentParser(description='Extract rgb frames from video list.')
	ap.add_argument('-i', '--input-file',
					dest='input_file',
					help='file with feats from torch.',
					type=str, required=False, default='/home/jp/DL/2kporn/folds')
	ap.add_argument('-o', '--output-file',
					dest='output_file',
					help='file to output the pickle output file.',
					type=str, required=False)
	args = ap.parse_args()
	
	print args
	
	return args

def main():
	args = load_args()
	
	feature_size = 2048
	num_samples = count_feats(args.input_file)
	print 'num_outputs', num_samples
	outfile = open(args.output_file, 'w') if args.output_file else sys.stdout
	pickle.dump([num_samples, feature_size], outfile)
	features = np.empty([feature_size], dtype=np.float)

	with open(args.input_file, 'r') as f:
		for line in f:
			#'p %s i %d l %d s %s f %s\n'
			row = line.split(' ')
			image_id = row[1].split('/')[-1][:-4]
			label = int(row[5]) - 1
			feats = line[line.find(' f ')+3: -1]
			features = np.array(map(float, feats.split('  ')))
#			print features
#			print 'line'
#			print line
#			print 'image_id'
#			print image_id
#			print 'label'
#			print label
#			print 'feats'
#			print feats
#			sys.exit()

			pickle.dump([image_id, label, features], outfile)

if __name__ == '__main__':
	main()
