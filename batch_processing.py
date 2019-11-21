from preprocessing.preprocessing import preProcessing
from crawler.crawler import init_directory
from tqdm import tqdm
import numpy as np
import json
import cv2
import os

if __name__ == "__main__":
    palette_dict = json.load(open("preprocessing/palette.json", "r"))
    color_set = { tuple(np.array(value).astype('uint8')) for key, value in palette_dict.items() }
    palette_dict = {tuple(v) : int(k) for k, v in palette_dict.items()}
    init_directory("preprocess/remove_grid/")
    init_directory("preprocess/numeric/")
    init_directory("preprocess/sampling/")
    init_directory("preprocess/sampling_image/")
    
    all_image = [i for i in os.listdir("images/radar/")]
    for filename in tqdm(all_image):
        filename_noPath = os.path.basename(filename)
        filename_noPath = filename_noPath[:filename_noPath.find(".")]
        image = cv2.imread("images/radar/" +filename)
        # preProcessing.filter(image, color_set, "preprocess/remove_grid/{}.png".format(filename_noPath))
        preProcessing.color2numeric(image, palette_dict, "preprocess/numeric/{}".format(filename_noPath))
        dbzImage = np.loadtxt("preprocess/numeric/{}".format(filename_noPath), delimiter=",", dtype="int")
        patches = preProcessing.split_image_block(dbzImage, 6)
        preProcessing.sampling(patches, 6, "preprocess/sampling/{}".format(filename_noPath))
        preProcessing.convert2image("preprocess/sampling/{}".format(filename_noPath), 
                                    "preprocess/sampling_image/{}.png".format(filename_noPath))



