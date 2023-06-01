from pathml.slide import Slide
import os
import csv
import pickle
import argparse


def findWSI(path_to_wsi):
	all_files = []
	for folder in os.listdir(path_to_wsi):
		if os.path.isdir(os.path.join(path_to_wsi, folder)):
			for subfolder in os.listdir(os.path.join(path_to_wsi, folder)):
				if os.path.isdir(os.path.join(path_to_wsi, folder, subfolder)):
					files = [
						os.path.join(path_to_wsi, folder, subfolder, name) 
						for name in os.listdir(os.path.join(path_to_wsi, folder, subfolder))
						if os.path.isfile(os.path.join(path_to_wsi, folder, subfolder, name))
					]
				else:
					files = [
						os.path.join(path_to_wsi, folder, name) 
						for name in os.listdir(os.path.join(path_to_wsi, folder))
						if os.path.isfile(os.path.join(path_to_wsi, folder, name))
					]
					if len(files) >= 5: all_files += files
					break
				if len(files) >= 5:
					all_files += files

	return all_files


def writeTiles(path_to_slide, level=3, tilesize=224, writeMILdict=True, args=None):
	s = Slide(path_to_slide, level=level).setTileProperties(tileSize=tilesize)
	s.detectTissue(
		numWorkers=0, 
		tissueDetectionLevel=2, 
		modelStateDictPath="/home/tobechanged/mirrored_folder/pathml/pathml/models/deep-tissue-detector_densenet_state-dict.pt",
	)
	s.detectForeground()
	mil_dict_update = {
		"slides" : path_to_slide, 
		"grid"   : [], 
		"targets": os.path.dirname(path_to_slide).split(os.sep)[-1], 
		"mult"   : 1, 
		"level"  : level,
	}
	for address in s.iterateTiles():
		slide_dict_entry = s.tileDictionary[address]
		if slide_dict_entry["tissueLevel"] >= 0.95:
			s.saveTile(
				address, 
				os.path.splitext(os.path.basename(path_to_slide))[0] + str(address[0]) + "_" + str(address[1]) + ".jpg[Q=95]",
				folder=setupOutputFolder(path_to_slide, args)
			)
			mil_dict_update["grid"].append((slide_dict_entry["x"] * 2**level, slide_dict_entry["y"] * 2**level))

	return mil_dict_update


def setupOutputFolder(path_to_slide, args=None):
	output_folder = os.path.dirname(os.path.join(args.path_output, "tiles", os.path.dirname(path_to_slide.split(args.path_to_wsi)[1])[1:]))
	os.makedirs(output_folder, exist_ok=True)
	return output_folder


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--path_to_wsi", type=str, default="/mnt/hd12tb/Laaff_slides", help="Folder of the the wsi files")
	parser.add_argument("--path_output", type=str, default="/mnt/hd12tb/Laaff_slides", help="Folder where the tiles are written to")
	args = parser.parse_args()
	all_wsi = findWSI(args.path_to_wsi)
	print(all_wsi)
	with open(os.path.join(args.path_output, "all_wsi.csv"), "w", newline="") as file:
		wr = csv.writer(file, quoting=csv.QUOTE_ALL)
		wr.writerow(all_wsi)
	# sample_slide = next(filter(lambda x: "isyntax" in x, all_wsi))
	# print(sample_slide)
	mil_dict = {
		"slides" : [], 
		"grid"   : [], 
		"targets": [], 
		"mult"   : [], 
		"level"  : [],
	}
	for sample_slide in all_wsi:
		print(sample_slide)
		mil_dict_update = writeTiles(sample_slide, args=args)
		# print(mil_dict_update)
		for k in mil_dict.keys():
			mil_dict[k].append(mil_dict_update[k])
	print(mil_dict)
	with open(os.path.join(args.path_output, "mil_dict.pkl"), "wb") as file:
		pickle.dump(mil_dict, file)

















#s = Slide(path_to_wsi, level = level).setTileProperties(tileSize = tilesize)
#
#""" 
#def detectTissue(self, tissueDetectionLevel=1, tissueDetectionTileSize=512, 
#tissueDetectionTileOverlap=0, tissueDetectionUpsampleFactor=4, batchSize=20, numWorkers=16, 
#overwriteExistingTissueDetection=False, 
#modelStateDictPath='../pathml/pathml/models/deep-tissue-detector_densenet_state-dict.pt', architecture='densenet'):
#"""
#
#
#"""
#example tile in tiledictionary:
#(90, 34): {'x': 20160, 'y': 7616, 'width': 224, 'height': 224, 'artifactLevel': 0.018563736230134964, 'backgroundLevel': 0.9799959063529968, 'tissueLevel': 0.0014402945525944233, 'foregroundLevel': 100.0, 'foregroundOtsu': False, 'foregroundTriangle': False},
#"""
#
#
#s.detectTissue(numWorkers=0,)
#s.detectForeground()
#
#s.iterateTiles()
#s.saveTile()
