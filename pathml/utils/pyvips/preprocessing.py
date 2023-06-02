from pathml.slide import Slide
from typing import Dict
import os
import csv
import difflib
import pickle
import argparse


def findWSI(
	path_to_wsi: str, 
	thresh: int = 0, 
	iden: str = "".join([str(i) for i in range(10)]) + "_",
) -> Dict:
	"""
	Find all wsi at the base folder found at path_to_wsi
	Match the diagnoses from their respective paths
	Optionally exclude all diagnoses with fewer wsi than thresh
	
	Input: 
		path_to_wsi basefolder to wsi
		thresh minimum number of wsi per diagnose
		iden internal parameter to extract diagnose from path
	
	Output: {"slides": [wsi], "targets": [diagnoses]}
	"""

	assert os.path.exists(path_to_wsi), f"Path not found by function findWSI: {path_to_wsi=}"
	assert thresh >= 0, "Got negative threshold number for function findWSI"
	
	data = {"slides": [], "targets": []}
	
	for path, dirs, files in os.walk(path_to_wsi):
	
		print(f"{path=} {dirs=} {files=}")
	
		wsi = list(filter(lambda x: os.path.splitext(x)[1] == ".isyntax", files))
	
		if len(wsi):
			
			s = difflib.SequenceMatcher(None, path, wsi[0])
			match = next(filter(lambda x: x.b == 0, s.get_matching_blocks()))
			diagnose = path[match[0]:] + " "
			stop = min([i for i, e in enumerate(diagnose[match[2]:]) if e not in iden], default=0)
			diagnose = diagnose[:match[2] + stop]
	
			data["slides"].extend(list(map(lambda x: os.path.join(path, x), wsi)))
			data["targets"].extend([diagnose] * len(wsi)) 

	data["slides"] = [s for i, s in enumerate(data["slides"]) if data["targets"].count(data["targets"][i]) >= thresh]
	data["targets"] = [s for i, s in enumerate(data["targets"]) if data["targets"].count(data["targets"][i]) >= thresh]

	return data


def writeTiles(path_to_slide, level=3, tilesize=224, tile_thresh=0.95, args=None):
	s = Slide(path_to_slide, level=level).setTileProperties(tileSize=tilesize)
	s.detectTissue(
		numWorkers=0, 
		tissueDetectionLevel=2, 
	)
	s.detectForeground()
	mil_dict_update = {
		"slides": path_to_slide, 
		"grid": [], 
		"targets": os.path.dirname(path_to_slide).split(os.sep)[-1], 
		"mult": 1, 
		"level": level,
	}
	for address in s.iterateTiles():
		slide_dict_entry = s.tileDictionary[address]
		if slide_dict_entry["tissueLevel"] >= tile_thresh:
			if isinstance(args, argparse.Namespace) and args.save:
				s.saveTile(
					address, 
					os.path.splitext(os.path.basename(path_to_slide))[0] + str(address[0]) + "_" + str(address[1]) + args,
					folder=setupOutputFolder(path_to_slide, args)
				)
			mil_dict_update["grid"].append(
				(slide_dict_entry["x"] * 2**level, slide_dict_entry["y"] * 2**level)
			)

	return mil_dict_update


def setupOutputFolder(path_to_slide, args=None):
	output_folder = os.path.dirname(os.path.join(args.path_output, "tiles", os.path.dirname(path_to_slide.split(args.path_to_wsi)[1])[1:]))
	os.makedirs(output_folder, exist_ok=True)
	return output_folder


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--path_to_wsi", type=str, default="/mnt/hd12tb/Laaff_slides", help="Folder of the the wsi files")
	parser.add_argument("--path_output", type=str, default="/mnt/hd12tb/Laaff_slides", help="Folder where the tiles are written to")
	parser.add_argument("--wsi_thresh", type=int, default=0, help="Minimum number of wsi per diagnose")
	parser.add_argument("--wsi_iden", type=str, default="0123456789_", help="Chars in path name which are expected to belong to diagnose")
	parser.add_argument("--tile_size", type=int, default=224, help="Size of tile to extract")
	parser.add_argument("--tile_level", type=int, default=3, help="Level at which the tile should be extracted")
	parser.add_argument("--tile_thresh", type=float, default=0.95, help="Threshold for tissue detection")
	parser.add_argument("--store_format", type=str, default="jpg[Q=95]", help="Format in which the tiles are stored")
	parser.add_argument("--save", type=bool, default=False, help="Whether to save the tiles")

	args = parser.parse_args()

	mil_dict = {
		"slides": [], 
		"grid": [], 
		"targets": [], 
		"mult": [], 
		"level": [],
	}

	mil_dict["slides"], mil_dict["targets"] = findWSI(path_to_wsi=args.path_to_wsi, thresh=args.wsi_thresh, iden=args.wsi_iden).values()
	print(mil_dict["slides"])
	
	with open(os.path.join(args.path_output, "all_wsi.csv"), "w", newline="") as file:
		wr = csv.writer(file, quoting=csv.QUOTE_ALL)
		wr.writerow(mil_dict["slides"])
	
	# sample_slide = next(filter(lambda x: "isyntax" in x, all_wsi))
	# print(sample_slide)
	
	for sample_slide in mil_dict["slides"]:
		print(sample_slide)
		mil_dict_update = writeTiles(
			path_to_slide=sample_slide,
			level=args.tile_level,
			tilesize=args.tile_size,
			tile_thresh=args.tile_thresh,
			args=args
		)
  

		# print(mil_dict_update)
		for k in mil_dict.keys():
			if k != "slides" and k != "targets":
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
