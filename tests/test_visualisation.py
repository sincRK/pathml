import yaml
from pathml.slide import Slide
from pathml.analysis import Analysis
import matplotlib.pyplot as plt


def test_analysis(request):
    rootdir = request.config.rootdir
    assert (rootdir / "configs" / "cfgtest.yaml").exists()
    testcfg = yaml.safe_load(open(rootdir / "configs" / "cfgtest.yaml", "r"))
    demoPath = testcfg["wsipath"]
    demoSlide = Slide(demoPath, level=3).setTileProperties(tileSize=400)
    demoSlide.detectForeground(threshold="otsu")
    tiledictionary = demoSlide.tileDictionary
    print(tiledictionary)
    testAnalysis = Analysis(tiledictionary)
    foreground=testAnalysis.generateForegroundMap()

    plt.figure()
    plt.imshow(foreground,vmin=0, vmax=1,cmap='gray')
    plt.title('Foreground')
    plt.show(block=False)
