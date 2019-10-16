from crawler.crawler import weatherCrawler, init_directory
from preprocessing.preprocessing import preProcessing

import numpy as np
import json
import time
import cv2
import os

if __name__ == "__main__":
    
    # preprocessing color palette
    palette_dict = json.load(open("preprocessing/palette.json", "r"))
    color_set = { tuple(np.array(value).astype('uint8')) for key, value in palette_dict.items() }
    palette_dict = {tuple(v) : int(k) for k, v in palette_dict.items()}
    init_directory("preprocess/remove_grid/")
    init_directory("preprocess/numeric/")


    while True:
        try:
            filename = weatherCrawler.radar()
            filename_noPath = os.path.basename(filename)
            filename_noPath = filename_noPath[:filename_noPath.find(".")]

            weatherCrawler.satellite()
            image = cv2.imread(filename)
            preProcessing.filter(image, color_set, "preprocess/remove_grid/{}.png".format(filename_noPath))
            preProcessing.color2numeric(image, palette_dict, "preprocess/numeric/{}".format(filename_noPath))

        except:
            pass
        time.sleep(180)