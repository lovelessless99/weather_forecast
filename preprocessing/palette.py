import numpy as np
import json
import cv2

if __name__ == "__main__":
    palette = json.load(open("palette.json", "r"))
    palette = {int(key)+1:value for key, value in palette.items()}
    palette[0] = [255, 255, 255]
    json.dump(palette, open("palette_new.json", "w"), indent=4)
    # image = cv2.imread("colorbar_n.png")
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # x, y = 0, 0
    # palette = image[y:y+10, x+10: x+1120]
    # color = np.unique(palette[0], axis=0)
    # # cv2.namedWindow('My Image', cv2.WINDOW_NORMAL)

    # # cv2.imshow('My Image', palette)
    # # cv2.waitKey(0)
    # # cv2.destroyAllWindows()
    # print(color)
    # colordict = {index: i.tolist() for index,  i in enumerate(color)}
    # print(colordict)
    # # json.dump(colordict, open("palette.json", "w"), indent=4)    
    
    
    

