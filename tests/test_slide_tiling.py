import pathml.utils.pyvips.preprocessing as pp
from pathlib import Path
import yaml
import argparse


def test_findWSI(request):
    rootdir = request.config.rootdir
    assert (rootdir / "configs" / "cfgtest.yaml").exists()
    testcfg = yaml.safe_load(open(rootdir / "configs" / "cfgtest.yaml", "r"))
    testslide = testcfg["wsipath"]
    
    assert testslide in pp.findWSI(Path(testslide).parent)["slides"]
    
    mil_dict = pp.writeTiles(
        testslide, 
        args=argparse.Namespace(**{"save": False, })
        )
    
    assert testslide in mil_dict["slides"]
    assert all(filter(lambda x: len(x) == 1, mil_dict))
