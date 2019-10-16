from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from multiprocessing import Process, Pool
from selenium import webdriver

import requests
import time
import os

def init_directory(directory): 
    if not os.path.exists(directory):
        os.makedirs(directory)


class weatherCrawler:
    
    @staticmethod
    def satellite():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        browser = webdriver.Chrome(chrome_options=chrome_options)

        browser.get("https://www.cwb.gov.tw/V8/C/W/OBS_Sat.html")
        browser.find_element_by_xpath("//input[@id='area2']/following-sibling::i[1]").click()
        
        directory = ["VisibleLight", "Color", "Tone", "BlackWhite", "RealColor"] 
        title     = ["顯示可見光", "顯示彩色", "顯示色調強化", "顯示黑白", "顯示真實色"]
        modes     = [ browser.find_element_by_xpath("//a[@title='{}']".format(i)) for i in title]
    
        datatime  = browser.find_element_by_class_name("zoomtime").text		
        print("{0}:".format(datatime))

        for mode, targetDir in zip(modes, directory):
            mode.click()
            image_url  = browser.find_element_by_xpath("//img[@alt='衛星雲圖']").get_attribute("src")
            image_data = requests.get(image_url,timeout=10).content
            image_name = image_url[image_url.find("-")+1:] 
            filename = "images/satellite/{0}/{1}".format(targetDir, image_name)
            init_directory( os.path.dirname(filename) )
            with open(filename, 'wb') as handler:
                handler.write(image_data)
                print("{0}: {1} saved successfully!".format(targetDir, image_name))
        
        browser.close()
    
    @staticmethod
    def radar():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        browser = webdriver.Chrome(chrome_options=chrome_options)

        browser.get('https://www.cwb.gov.tw/V8/C/W/OBS_Radar.html')
        browser.find_element_by_xpath("//input[@type='radio'][@name='area'][@value='1']/following-sibling::i[1]").click()
        datatime   = browser.find_element_by_class_name("zoomtime").text
        image_url  = browser.find_element_by_xpath("//img[@alt='雷達回波']").get_attribute("src")
        image_data = requests.get(image_url,timeout=10).content
        image_name = image_url[image_url.rfind("_")+1:]
        filename = "images/radar/{}".format(image_name)
        init_directory( os.path.dirname(filename) )
        with open(filename, 'wb') as handler:
            handler.write(image_data)
            print("radar: {0} saved successfully!".format(image_name))
        browser.close()

        return filename

if __name__ == "__main__":
    
    while True:
        try:
            weatherCrawler.radar()
            weatherCrawler.satellite()
        except:
            pass
        time.sleep(180)
