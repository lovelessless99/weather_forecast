# from PIL import Image
from time import time
from tqdm import tqdm
from crawler.crawler import init_directory
from collections import Counter
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
        for row in tqdm(image):
            dim = []
            for pixel in row:
                if tuple(pixel) in palette_dict:
                    dim.append(palette_dict[tuple(pixel)])

                elif tuple(pixel) == tuple([229, 229, 229]):
                    dim.append(0)
                else:
                    dim.append(-1)
            numeric.append(dim)
        
        x , y = 2234, 3374
        x_move, y_move = 1331, 86
        invalid_bar = np.repeat(-1, x_move*y_move)
        invalid_bar = np.reshape(invalid_bar, (x_move, y_move))
        numeric = np.array(numeric).astype(int)
        numeric[ x : x+x_move , y: y+y_move] = invalid_bar
        np.savetxt(output_name, numeric, fmt='%i', delimiter=',')
        
    @staticmethod 
    @timing
    def filter(image ,color_set, output_name):
        init_directory(os.path.dirname(output_name))
        filter_ans = []
        black_pixel = np.array([0, 0, 0]).astype('uint8')
        white_pixel = np.array([255, 255, 255]).astype('uint8')
        
        for i in tqdm(image):
            dim = []
            for pixel in i:
                if tuple(pixel) in color_set:
                    dim.append(pixel)
                elif tuple(pixel) == tuple([229, 229, 229]):
                    dim.append(white_pixel)
                else:
                    dim.append(black_pixel)
            filter_ans.append(dim)
        
        filter_ans = np.array(filter_ans).astype('uint8')
        
        x , y = 2234, 3374
        x_move, y_move = 1331, 86
        black = np.repeat(0, x_move*y_move*3)
        black = np.reshape(black, (x_move, y_move, 3))
        filter_ans[ x : x+x_move , y: y+y_move] = black

        cv2.imwrite(output_name, np.array(filter_ans))


    @staticmethod
    def split_image_block(image, n):
        blocks = []
        for i in tqdm(range(3, 3597, n)):
            for j in range(3, 3597, n):
                blocks.append(np.array(image[i: i+n , j: j+n]))
        return np.array(blocks)

    @staticmethod
    def sampling(block_image, size, outputfile):
        n = size
        target_size = (3600 // n) - 1
        new_image = []
        for block in block_image:
            tmp = block.flatten()
            # all is invalid value (-1) 
            if len(tmp[tmp>=0]) == 0:
                new_image.append(-1)
            else:
                frequency = Counter(tmp)

                # check if the most frequency value is valid
                if frequency.most_common(1)[0][0] == -1:
                    new_image.append(frequency.most_common(2)[1][0])
                else:
                    new_image.append(frequency.most_common(1)[0][0])
        
        new_image = np.array(new_image).reshape(target_size, target_size)

        invalid = np.where(new_image == -1)
        invalid = [ (i, j) for i, j in zip(invalid[0], invalid[1])] 
        new_image = preProcessing.interpolate(new_image, invalid)

        np.savetxt(outputfile, new_image, fmt='%i', delimiter=',')

    @staticmethod
    def groups(invalid_arr, cluster):
        all_group = []

        for key in invalid_arr:
            points, size = invalid_arr[key]['points'], invalid_arr[key]['size']
            pointset = set(points)
            current = 0
            
            while current < size:
                group = []
                i = 0
                group.append(points[current])
                i += 1
                while True:
                    next = (points[current][0], points[current][1] + i) if cluster == 'x' else (points[current][0] + i, points[current][1])
                    if next in pointset:
                        group.append(next)
                        i += 1
                    else:
                        break
                all_group.append(group)
                current += i
        return all_group

    @staticmethod
    def cal_weight(dbzmatrix, groups, types):
        all_weight = []
        # observepoint = {(292, 212), (293, 212), (293, 213), (294, 210), (294, 211), (294, 212), (294, 213), (295, 212)}
        
        for group in groups:
            weight = []
            start = (group[0][1] - 1) if types == 'x'  else (group[0][0] - 1)
            end =   (group[-1][1] + 1) if types == 'x' else (group[-1][0] + 1)
            front = dbzmatrix[group[0][0] , start ] if types == 'x'  else dbzmatrix[start, group[0][1]]
            rear  = dbzmatrix[group[-1][0], end ] if types == 'x' else dbzmatrix[end, group[-1][1] ]
    
            front = 10**(front/10)     
            rear  = 10**(rear/10) 

            size = len(group) + 1
            for idx, element in enumerate(group):
                # weight_front = (idx + 1) / size
                # weight_rear  = (size - (idx + 1))  / size
                weight_front =  (size - (idx + 1)) / size
                weight_rear  =  (idx + 1) / size
                weight_total = (front * weight_front + rear * weight_rear)

                # if element in observepoint:
                    # print("front = {}, rear = {}".format(front, rear))
                    # print("front(exp) = {}, front_weight = {}, rear(exp) = {}, rear_weight = {}".format(front, weight_front, rear,
                    #                                                                     weight_rear))
                    # print("{} 的 {} = {}".format(element, types, weight_total))
                # total = int(10 * np.log10(weight_total)) if weight_total != 0 else 0
                weight.append(weight_total)
            all_weight.append(weight)
        return all_weight

    @staticmethod
    def interpolate(dbzmatrix, index):

        invalid_dic_x = {}
        invalid_dic_y = {}
        
        for x, y in index:
            if x not in invalid_dic_x:
                invalid_dic_x[x] = {
                    'size' : 0,
                    'points' : []
                }

            if y not in invalid_dic_y:
                invalid_dic_y[y] = {
                    'size' : 0,
                    'points' : []
                }

            invalid_dic_x[x]['points'].append((x, y))
            invalid_dic_x[x]['size'] += 1

            invalid_dic_y[y]['points'].append((x, y))
            invalid_dic_y[y]['size'] += 1

        all_groups_x = preProcessing.groups(invalid_dic_x, 'x')
        all_groups_y = preProcessing.groups(invalid_dic_y, 'y')

        all_weight_x = preProcessing.cal_weight(dbzmatrix, all_groups_x, 'x')
        all_weight_y = preProcessing.cal_weight(dbzmatrix, all_groups_y, 'y')
        
        weight_dic = { key : 0 for key in index}
        for group, weights in zip(all_groups_x, all_weight_x):
            for point, weight in zip(group, weights):
                weight_dic[point] += weight

        
        for group, weights in zip(all_groups_y, all_weight_y):
            for point, weight in zip(group, weights):
                weight_dic[point] += weight

        for key, value in weight_dic.items():
            # weight_dic[key] = int (value / 2 + 0.5)  # 四捨五入
            weight_dic[key] = value / 2
            weight_dic[key] = int(10 * np.log10(weight_dic[key])) if weight_dic[key] >= 1.0 else 0
            dbzmatrix[key] = weight_dic[key] 
        
        return dbzmatrix

    @staticmethod
    def convert2image(inputFile, outputFileName):
        dbz = np.loadtxt(inputFile, delimiter=",", dtype="int")
        dic_map = json.load(open("preprocessing/palette.json", "r"))
        image = []
        for row in dbz:
            tmp = []
            for element in row:
                if str(element) in dic_map:
                    tmp.append(dic_map[str(element)])

                # invalid value ----> black
                else:
                    tmp.append([0, 0, 0])
            image.append(tmp)
        image = np.array(image, dtype="uint8")
        cv2.imwrite(outputFileName, image)

    
    

