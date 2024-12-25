from selenium import webdriver  
#webdriver: The main module in Selenium to control web browsers. It allows the script to open a browser, navigate to web pages, 
# interact with elements (e.g., clicks, inputs), and retrieve data.
from selenium.webdriver.chrome.service import Service
#Service: Manages the ChromeDriver executable, which enables Selenium to communicate with the Chrome browser. 
# It specifies the driver path and ensures proper handling of the ChromeDriver process.
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
#options: Used to customize the behavior of the Chrome browser. For example:
#Running the browser headlessly (without UI).
#Setting window size or position.
#Blocking pop-ups or enabling specific features.
from selenium.webdriver.support import expected_conditions as EC
import os
import crome_webdriver
import requests 
#requests: A popular Python library for making HTTP requests. It is used here to download video files by sending requests to their 
# URLs and saving the response data.
import time
import platform
#platform: A standard library module to detect the operating system being used (e.g., Windows, macOS, Linux).
from selenium.webdriver.common.action_chains import ActionChains
#ActionChains are a way to automate low-level interactions such as mouse movements,mouse button actions, keypress, and context menu 
# interactions. This is useful for doing more complex actions like hovering over and drag and drop.



def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-minimized")

    # Detect the operating system and set the path accordingly
    if platform.system() == "Windows":
        service = Service(executable_path="driver/chromedriver.exe")
    else :  
        service = Service(executable_path="driver/chromedriver")
    

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def download_videos(url,filename):
    if not os.path.exists('videos'):  #This will check if any file name videos is present there or not 
        os.makedirs('videos') #if not present there make the file name videos in the folder to store the videos
        
    file_path = os.path.join('videos',filename) #Combines the directory path (videos) with the filename to get the full path for saving the video.
    print("ok")
    try:
        print(f"Downloading : {filename}")
        response = requests.get(url,stream=True)
        
        
        if response.status_code == 200:  #200: Indicates the request was successful, and the server is returning the video file.
            with open(file_path,'wb') as file:
                for chunk in response.iter_content(1024): #Opens the file at file_path in write-binary mode ('wb') to save the video data.
                    #Reads the response data in chunks of 1024 bytes (1 KB).
                    #Prevents loading the entire file into memory at once.
                    file.write(chunk)
                print(f"Download Complete: {file_path}")
        else:
            print(f"Failed to download : {url} ")
    except Exception as e: #Catches any unexpected errors during the download process, such as: Network interruptions,File writing issues (e.g., permission errors).
        print(f"Error Downloading {filename}:{e} ")

def close_all_popups(driver: webdriver.Chrome):
    #It will close all the unwanted popups and try to stay on the main window.
    main_window = driver.current_window_handle
    
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            driver.close()
    
    driver.switch_to.window(main_window)

def keep_clicking_until_video_plays(driver, streamtape_url):
    driver.set_window_position(500, 100)
    #driver.minimize_window()
    driver.get(streamtape_url)
    time.sleep(3) 
    
    attempts = 0
    video_found = False
    max_attempts = 100 
    while attempts < max_attempts:
        try:
          
            overlay = driver.find_element(By.CLASS_NAME, "play-overlay")
            driver.execute_script("arguments[0].click();", overlay)
            print(f"Overlay clicked on attempt {attempts+1}")

        except Exception:
            print(f"Overlay not found or already clicked on attempt {attempts+1}")

        try:
           
            play_button = driver.find_element(By.CLASS_NAME, "plyr__control--overlaid")
            driver.execute_script("arguments[0].click();", play_button)
            print(f"Play button clicked on attempt {attempts+1}")

            
            video_player = driver.find_element(By.TAG_NAME, 'video')
            
            video_url = video_player.get_attribute('src')
            
            if video_url:
                print(f"Video found and playing on attempt {attempts+1}")
                video_found = True
                break
        except Exception:
            print(f"Play button or video not found on attempt {attempts+1}")
        
        
        close_all_popups(driver)
        
        
        attempts += 1
        time.sleep(0.25) 
    
    if video_found:
        return True  
    else:
        print(f"Failed to start video after {attempts} attempts.")
        return False

def get_download_link(driver: webdriver.Chrome, streamtape_url):
    driver.set_window_position(500, 100)
    #driver.minimize_window()
    driver.get(streamtape_url)
    try:
      
        if not keep_clicking_until_video_plays(driver, streamtape_url):
            return None, None

        print(0)
        time.sleep(5)  
       
        h2_element = driver.find_element(By.TAG_NAME, "h2")
        file_name = h2_element.text.strip()
        print(f"File Name Found: {file_name}")

        video_player = driver.find_element(By.TAG_NAME, 'video')
        video_url = video_player.get_attribute('src')
        print(f"Download Link Found: {video_url}")

        return file_name, video_url

    except Exception as e:
        print(f"Error extracting file name or download link from {streamtape_url}: {e}")
        return None, None
    
def read_links_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            
            return [line.strip() for line in file.readlines() if line.strip()]
    else:
        print(f"{file_path} does not exist.")
        return []

def main():
    driver = setup_driver()
    links = read_links_from_file("links.txt")
    
    for i,link in  enumerate(links,1):
        print(f"processing {i}/{len(links)}: {link}")
        file_name,video_url = get_download_link(driver,link)
        if video_url:
            download_videos(video_url,file_name)
            
    driver.quit()
    
if __name__ == "__main__":
    crome_webdriver.setup_chromedriver()  #We will first setup the chrome webdriver to proceed further
    #The chrome webdriver installation in the device. 
    main()  #Then we will call main funtion to procced further.
    