import yaml
from pathml.slide import Slide
from pathml.analysis import Analysis
from pathml.processor import Processor
from pathml.models.tissuedetector import tissueDetector
import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize


def test_model(request):
    rootdir = request.config.rootdir
    assert (rootdir / "configs" / "cfgtest.yaml").exists()
    testcfg = yaml.safe_load(open(rootdir / "configs" / "cfgtest.yaml", "r"))
    testslide = testcfg["wsipath"]
    pathmlSlide = Slide(testslide, level=2).setTileProperties(tileSize=224)
    tissueForegroundSlide = Slide(testslide, level=3).setTileProperties(tileSize=448, tileOverlap=0.5)
    tmpProcessor = Processor(tissueForegroundSlide)
    tissueForegroundTmp = tmpProcessor.applyModel(tissueDetector(), batch_size=20, predictionKey='tissue_detector').adoptKeyFromTileDictionary(upsampleFactor=4)

    predictionMap = np.zeros([tissueForegroundTmp.numTilesInY, tissueForegroundTmp.numTilesInX,3])
    for address in tissueForegroundTmp.iterateTiles():
        if 'tissue_detector' in tissueForegroundTmp.tileDictionary[address]:
            predictionMap[address[1], address[0], :] = tissueForegroundTmp.tileDictionary[address]['tissue_detector']

    predictionMap2 = np.zeros([pathmlSlide.numTilesInY, pathmlSlide.numTilesInX])
    predictionMap1res = resize(predictionMap, predictionMap2.shape, order=0, anti_aliasing=False)
    for address in pathmlSlide.iterateTiles():
        pathmlSlide.tileDictionary[address].update({'tissueLevel': predictionMap1res[address[1], address[0]][2]})



