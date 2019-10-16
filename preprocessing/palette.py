import numpy as np
import json
import cv2

if __name__ == "__main__":
    image = cv2.imread("colorbar_n.png")
    x, y = 0, 0
    palette = image[y:y+10, x+10: x+1120]
    color = np.unique(palette[0], axis=0)
    
    colordict = {index: i.tolist() for index,  i in enumerate(color)}
    json.dump(colordict, open("palette.json", "w"), indent=4)    
    
    
    

