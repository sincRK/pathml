import openphi
import pyvips

import numpy as np

# Type conversion numpy, pyvips
dtype_to_format = {
    'uint8': 'uchar',
    'int8': 'char',
    'uint16': 'ushort',
    'int16': 'short',
    'uint32': 'uint',
    'int32': 'int',
    'float32': 'float',
    'float64': 'double',
    'complex64': 'complex',
    'complex128': 'dpcomplex',
}


# Load a .isyntax file as pyvips Image object
# Using openphi https://academic.oup.com/bioinformatics/article/37/21/3995/6343446?login=true
def open_isyntax(path_to_file, level):

    # Only handle .isyntax files. The .tiff or .ndpi or other supported formats should be handled outside of this function
    # Use pyvips.Image.new_from_file()
    assert path_to_file.split(".")[-1] == "isyntax", f"The specified file at {path_to_file} is not .isyntax"

    # Open WSI
    wsi = openphi.OpenPhi(path_to_file)

    # Convert to numpy and then from numpy to pyvips
    num_arr = openphi_to_numpy(wsi, level)
    py_img = numpy_to_pyvips(num_arr)

    # Did the conversion work?
    assert isinstance(py_img, pyvips.vimage.Image), "Conversion did not return a pyvips.vimage.Image object"
    return py_img


# Convert an openphi slide to RGB numpy array
def openphi_to_numpy(openphi_slide, level):

    # Get RGB pixels as PIL Image
    rgb = openphi_slide.read_region((0, 0), level, openphi_slide.level_dimensions[level])

    # Convert to numpy array
    num_arr = np.asarray(rgb)

    return num_arr


# Convert a numpy RGB array to pyvips Image
def numpy_to_pyvips(numpy_slide):

    # Get dimensions
    height, width, bands = numpy_slide.shape

    # Flatten
    linear = numpy_slide.reshape(width * height * bands)

    # Fill pyvips.vimage.Image object and reshape
    vi = pyvips.Image.new_from_memory(linear.data, width, height, bands, dtype_to_format[str(numpy_slide.dtype)])

    return vi


def get_best_downsample_level(slide, downsample_factor):
    pass
