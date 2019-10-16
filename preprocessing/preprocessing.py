# from PIL import Image
from time import time
from tqdm import tqdm
from crawler.crawler import init_directory
import numpy as np
import json
import cv2
import os

def timing(f):
    def func(*args, **kw):
        ts = time()
        f(*args, **kw)
        te = time()
        print ( 'func:%r took: %2.4f sec' % (f.__name__, te-ts) )
        #return result
    return func

class preProcessing:
    
    @staticmethod
    @timing
    def color2numeric(image ,palette_dict, output_name):
        init_directory(os.path.dirname(output_name))
        numeric = []
        for i in tqdm(image):
            dim = []
            for pixel in i:
                if tuple(pixel) in palette_dict:
                    dim.append(palette_dict[tuple(pixel)])
                else:
                    dim.append(0)
            numeric.append(dim)
        numeric = np.array(numeric).astype(int)
        np.savetxt(output_name, numeric, fmt='%i', delimiter=',')
        
    @staticmethod 
    @timing
    def filter(image ,color_set, output_name):
        init_directory(os.path.dirname(output_name))
        filter_ans = []
        white_pixel = np.array([255, 255, 255]).astype('uint8')

        for i in tqdm(image):
            dim = []
            for pixel in i:
                if tuple(pixel) in color_set:
                    dim.append(pixel)
                else:
                    dim.append(white_pixel)
            filter_ans.append(dim)
        
        filter_ans = np.array(filter_ans).astype('uint8')
        
        x , y = 2234, 3374
        x_move, y_move = 1331, 86
        white = np.repeat(255, x_move*y_move*3)
        white = np.reshape(white, (x_move, y_move, 3))
        filter_ans[ x : x+x_move , y: y+y_move] = white

        cv2.imwrite(output_name, np.array(filter_ans))



            

    
    

