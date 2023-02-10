from exif import Image
import os, sys
import subprocess
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from pymediainfo import MediaInfo
import filedate

#import cv2

folder_dir = os.path.dirname(os.path.abspath(__file__))



# Returns file type
def get_file_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return 'Image'
    elif file_extension in ['.mp4', '.mkv', '.avi', '.mov', '.wmv']:
        return 'Video'
    else:
        return 'Unknown'
    
# get date and time info
def extract_datetime(file_name):
    date_time = None
    
    # WIN_20211231_02_57_26_Pro.jpg
    # <name>_<Year><Month><Day>_<Hour>_<Min>_<Sec>
    datetime_pattern  = re.compile(r"\w+_(\d{4})(\d{2})(\d{2})_(\d{2})_(\d{2})_(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:])
    
    
    # Vıd 20210829 233847-1.m4v
    # <name> <Year><Month><Day> <Hour><Min><Sec>
    datetime_pattern = re.compile(r"\w+ (\d{4})(\d{2})(\d{2}) (\d{2})(\d{2})(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:])
    
    
    # VID_20221227_154514.mp4
    # <name>_<Year><Month><Day>_<Hour><Min><Sec>
    datetime_pattern = re.compile(r"\w+_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:])
    
    
    # video_2022-07-01_14-10-56.mp4
    # <name>_<Year>-<Month>-<Day>_<Hour>-<Min>-<Sec>
    datetime_pattern = re.compile(r"\w+_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:])    
    
    
    # Screenshot_2022-12-25-19-39-55-096_com.whatsapp.jpg
    # <name>_<Year>-<Month>-<Day>-<Hour>-<Min>-<Sec>
    datetime_pattern = re.compile(r"\w+_(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:]) 
        
        
    # 2017-01-20 18.17.33.jpg
    # <Year>-<Month>-<Day> <Hour>.<Min>.<Sec>
    datetime_pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}).(\d{2}).(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:]) 
        
          
    # VID-20221217-WA0059.mp4
    # <name>-<Year><Month><Day>
    date_pattern = re.compile(r"\w+-(\d{4})(\d{2})(\d{2})")
    date_match = date_pattern.search(file_name)
    if date_match:
        date_time = "-".join(date_match.groups()) + " 00:00:00"


    return date_time  

#-----------------------------------------------------------------------------------------------------------------------------------

# Iterates every file under dir and call the func for image and video
def print_directory_contents(path):
    df = pd.DataFrame(columns=['dir', 'type', 'name', 'date_time'])
    
    for child in os.listdir(path):
        child_path = os.path.join(path, child)
        if os.path.isdir(child_path):
            print_directory_contents(child_path)
        else:
            
            type = get_file_type(child_path)
            name = os.path.basename(child_path)
            date_time = extract_datetime(child_path)
            
            file_create_and_mod_time_change(child_path, date_time)
            
            #print(child_path + "\t \t" + type)
            
            df = df.append({'dir': child_path,'type': type, 'name': name, 'date_time': date_time}, ignore_index=True)
            
            if type is 'Image':
                image_datetime_change(child_path)
            elif type is 'Video':
                video_datetime_change(child_path)
                
    print(df)


def file_create_and_mod_time_change(child_path, date_time):
    try:
        a_file = filedate.File(child_path)
        a_file.set(
            created = date_time,
            modified = date_time,
            accessed = date_time
        )
        filedate.File(child_path)
    
    except:
        print("FAIL")
    



def image_datetime_change(child_path):
    with open(child_path, 'rb') as img_file:
        img = Image(img_file)

        ctime = os.path.getctime(child_path)
        created_time = datetime.datetime.fromtimestamp(ctime)
        
        #print(created_time.strftime("%Y:%m:%d %H:%M:%S"))
        img.datetime            = created_time.strftime("%Y:%m:%d %H:%M:%S")
        img.datetime_original   = created_time.strftime("%Y:%m:%d %H:%M:%S")
        img.datetime_digitized  = created_time.strftime("%Y:%m:%d %H:%M:%S")
        
        
    with open(child_path, 'wb') as new_image_file:
        new_image_file.write(img.get_file())
        
        
        

def video_datetime_change(filename):
    
    ctime = os.path.getctime(filename)
    ctime = datetime.datetime.fromtimestamp(ctime)
    ctime = ctime.strftime("%Y:%m:%d %H:%M:%S")
    filename = filename.replace(" ", "\" \"")
    
    com = ["CreateDate", "ModifyDate", "TrackCreateDate", "TrackModifyDate", "MediaCreateDate", "MediaModifyDate"]
    
    for co in com:
        commandd = 'exiftool "-'+ co +'='+str(ctime)+'" '+ filename
        os.system('"' + commandd + '"')
    


    


print_directory_contents(folder_dir)









  
