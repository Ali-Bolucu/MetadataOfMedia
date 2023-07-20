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
import shutil


folder_dir = os.path.dirname(os.path.abspath(__file__))



def main():

    print("Welcome to the program!")
    print("Please select an option:")
    print("1. Name to MetaData")
    print("2. MetaData to Name")
    print("3. Set both Name and MetaData")
    print("4. Order the Files")
    print("5. Just Change Create and Modified Date")
    print("6. Set Just MetaData")
    print("7. Quit")

    choice = input("Enter your choice: ")

    if choice == '1':
        #os.system('cmd /k "cls"')
        option_one()
    elif choice == '2':
        #os.system('cmd /k "cls"')
        option_two()
    elif choice == '3':
        #os.system('cmd /k "cls"')
        option_three()
    elif choice == '4':
        #os.system('cmd /k "cls"')
        option_four()
    elif choice == '5':
        #os.system('cmd /k "cls"')
        option_five()
    elif choice == '6':
        #os.system('cmd /k "cls"')
        option_six()

    else:
        #os.system('cmd /k "cls"')
        print("Invalid choice. Please try again.")
    


def option_one():
    print("Option 1 selected")

    Name_to_MetaData(folder_dir)

def option_two():
    print("Option 2 selected")
    MetaData_to_Name(folder_dir)

def option_three():
    print("Option 3 selected")
    result = input("Enter a date and time (YYYYMMDD):")
    Set_Both(folder_dir, result)

def option_four():
    print("Option 4 selected")
    File_Order(folder_dir)
    
def option_five():
    print("Option 5 selected")
    justCreateAndModifiedDate(folder_dir)
    
def option_six():
    print("Option 6 selected")
    result = input("Enter a date and time (YYYYMMDD):")
    SetJustMetaData(folder_dir, result)



# Returns file type
def get_file_type(file_path):
    file_extension = os.path.splitext(file_path)[1]

    if file_extension in ['.jpg','.JPG','.jpeg','.JPEG',  '.png', '.gif', '.bmp']:
        return 'Image'
    elif file_extension in ['.mp4','.MP4', '.mkv', '.avi', '.mov', '.MOV', '.wmv']:
        return 'Video'
    else:
        return 'Unknown'
    

# Iterates every file under dir and call the func for image and video
def Name_to_MetaData(path):
    df = pd.DataFrame(columns=['dir', 'type', 'name', 'date_time'])
    
    for child in os.listdir(path):

        child_path = os.path.join(path, child)

        if os.path.isdir(child_path):
            Name_to_MetaData(child_path)
        else:
            type = get_file_type(child_path)
            name = os.path.basename(child_path)
            date_time = extract_datetime(child_path)

            file_create_and_mod_time_change(child_path, date_time)

            df = df.append({'dir': os.path.join(*get_last_two_folders(child_path)),'type': type, 'name': name, 'date_time': date_time}, ignore_index=True)

            if type is 'Image':
                image_datetime_change(child_path, date_time)
            elif type is 'Video':
                video_datetime_change(child_path, date_time)

    print(df)

# Iterates every file under dir and call the func for image and video
def MetaData_to_Name(path):
    df = pd.DataFrame(columns=['dir', 'type', 'Name', 'NewName'])
    
    counter1 = 0
    counter2 = 0
    
    for child in os.listdir(path):

        child_path = os.path.join(path, child)

        if os.path.isdir(child_path):
            MetaData_to_Name(child_path)        
            counter1 = 0
            counter2 = 0
    
        else:
            type = get_file_type(child_path)
            name = os.path.basename(child_path)
            file_extension = os.path.splitext(child_path)[1]
            newfilename = ""
            result = ""


            if type is 'Image':
                with open(child_path, 'rb') as img_file:
                    img = Image(img_file)
                    datetime_obj  = datetime.datetime.strptime(img.datetime, "%Y:%m:%d %H:%M:%S")

                if datetime_obj.strftime('%H:%M:%S') == '00:00:00':
                    counter1+=1
                    newfilename = "IMG_" + datetime_obj.strftime('%Y%m%d') + "_WA" + "{:04d}".format(counter1)
                    os.rename(child_path, os.path.join(path, newfilename+ file_extension))

                else:
                    newfilename = "IMG_"+ datetime_obj.strftime('%Y%m%d_%H%M%S')
                    os.rename(child_path, os.path.join(path, newfilename+ file_extension))
                        
            elif type is 'Video':
                #filename = child_path.replace(" ", "\" \"")
                command = 'exiftool -d %Y%m%d_%H%M%S -CreateDate "'+ child_path +'"'
                #print(command)     #YYYY:MM:DD HH:MM:SS±HH:MM
                result = subprocess.check_output(command).decode("utf-8").replace('\r', '').replace('\n', '')[-15:]
                timeZone = datetime.datetime.strptime("03","%H")
                result_with_timezone = datetime.datetime.strptime(result,"%Y%m%d_%H%M%S") + datetime.timedelta(hours=timeZone.hour)
                result_with_timezone = result_with_timezone.strftime('%Y%m%d_%H%M%S')
                
                if result_with_timezone[-6:] == '000000':
                    counter2+=1
                    newfilename = "VID_" + result_with_timezone[:8] + "_WA" + "{:04d}".format(counter2)
                    os.rename(child_path, os.path.join(path, newfilename+ file_extension))

                else:
                    newfilename = "VID_"+ result_with_timezone
                    os.rename(child_path, os.path.join(path, newfilename+ file_extension))
                       
        df = df.append({'dir': os.path.join(*get_last_two_folders(child_path)),'type': type, 'Name': name, 'NewName': newfilename}, ignore_index=True)
        
    print(df)

def Set_Both(path, result):
    df = pd.DataFrame(columns=['dir', 'type', 'Name', 'NewName'])

    
    counter1 = 0
    counter2 = 0

    for child in os.listdir(path):

        child_path = os.path.join(path, child)


        if os.path.isdir(child_path):
            Set_Both(child_path, result)
            
        else:
            type = get_file_type(child_path)
            name = os.path.basename(child_path)
            file_extension = os.path.splitext(child_path)[1]
            newfilename = ""
            
            result_with_timezone = str(datetime.datetime.strptime(result,"%Y%m%d"))


            if type is 'Image':
                counter1 += 1
                newfilename = "IMG_" + result + "_WA" + "{:04d}".format(counter1)
                image_datetime_change(child_path, result_with_timezone)
                os.rename(child_path, os.path.join(path, newfilename+ file_extension))
                        
            elif type is 'Video':
                counter2 += 1
                newfilename = "VID_" + result + "_WA" + "{:04d}".format(counter2)
                video_datetime_change(child_path, result_with_timezone)
                os.rename(child_path, os.path.join(path, newfilename+ file_extension))

        df = df.append({'dir': os.path.join(*get_last_two_folders(child_path)),'type': type, 'Name': name, 'NewName': newfilename}, ignore_index=True)
        
    print(df)

def File_Order(path):
    
    counter1 = 0
    counter2 = 0
    folder_path = os.path.join(path, "Ordered")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.endswith(".py")]

    for i, file_name in enumerate(file_list):
        print(f"{i+1}. {file_name}")

    while True:

        user_input  = input("\n \n==> Enter the number of the file you want to select (q Exit): ")
        if user_input  == 'q':
            break

        file_num = int(user_input)
        if 1 <= file_num <= len(file_list):
            file_path = os.path.join(path, file_list[file_num-1]) #bunun geregi yok gibi
            print(f"You have selected '{file_path}' \n")

            file_name = file_list[file_num-1]
            file_path = os.path.join(path, file_name)

            new_file_path = os.path.join(folder_path, file_name)
            shutil.move(file_path, new_file_path)


            file_list.remove(file_list[file_num-1]) # remove the selected file name from the file list

            file_extension = os.path.splitext(new_file_path)[1]
            type = get_file_type(new_file_path)
            
            date_pattern = re.compile(r"(\d{4})[\d._-]?(\d{2})[\d._-]?(\d{2})")
            date_match = date_pattern.search(file_name)
            if date_match:
                date_time = "".join(date_match.groups())

            if type is 'Image':
                counter1 += 1
                newfilename = "IMG_" + date_time + "_WA" + "{:04d}".format(counter1)
                os.rename(new_file_path, os.path.join(folder_path, newfilename+ file_extension))
                        
            elif type is 'Video':
                counter2 += 1
                newfilename = "VID_" + date_time + "_WA" + "{:04d}".format(counter2)
                os.rename(new_file_path, os.path.join(folder_path, newfilename+ file_extension))


            for i, file_name in enumerate(file_list):
                print(f"{i+1}. {file_name}")

        else:
            print("Invalid file number. Please try again.")


def justCreateAndModifiedDate(path):
    df = pd.DataFrame(columns=['dir', 'type', 'name', 'date_time'])
    
    for child in os.listdir(path):

        child_path = os.path.join(path, child)

        if os.path.isdir(child_path):
            justCreateAndModifiedDate(child_path)
        else:
            type = get_file_type(child_path)
            name = os.path.basename(child_path)
            date_time = extract_datetime(child_path)

            file_create_and_mod_time_change(child_path, date_time)

            df = df.append({'dir': os.path.join(*get_last_two_folders(child_path)),'type': type, 'name': name, 'date_time': date_time}, ignore_index=True)

    print(df)
    

def SetJustMetaData(path, result):
    df = pd.DataFrame(columns=['dir', 'type', 'Name', 'NewName'])

    
    counter1 = 0
    counter2 = 0

    for child in os.listdir(path):

        child_path = os.path.join(path, child)


        if os.path.isdir(child_path):
            SetJustMetaData(child_path, result)
            
        else:
            type = get_file_type(child_path)
            name = os.path.basename(child_path)
            file_extension = os.path.splitext(child_path)[1]
            newfilename = ""
            
            result_with_timezone = str(datetime.datetime.strptime(result,"%Y%m%d"))


            if type is 'Image':
                counter1 += 1
                newfilename = "IMG_" + result + "_WA" + "{:04d}".format(counter1)
                image_datetime_change(child_path, result_with_timezone)
                        
            elif type is 'Video':
                counter2 += 1
                newfilename = "VID_" + result + "_WA" + "{:04d}".format(counter2)
                video_datetime_change(child_path, result_with_timezone)

        df = df.append({'dir': os.path.join(*get_last_two_folders(child_path)),'type': type, 'Name': name, 'NewName': newfilename}, ignore_index=True)
        
    print(df)

def get_last_two_folders(path):
    # Split the directory path using the os module
    folders = os.path.normpath(path).split(os.sep)

    # Get the last two folder names
    if len(folders) > 1:
        return folders[-3:-1]
    else:
        return None

def image_datetime_change(child_path, tarih):
    with open(child_path, 'rb') as img_file:
        img = Image(img_file)

        #ctime = os.path.getctime(child_path)
        #created_time = datetime.datetime.fromtimestamp(ctime)
        #print(created_time)
        #print(created_time.strftime("%Y:%m:%d %H:%M:%S"))
        
        img.datetime            = tarih.replace('-',':')
        img.datetime_original   = tarih.replace('-',':')
        img.datetime_digitized  = tarih.replace('-',':')
        
        
    with open(child_path, 'wb') as new_image_file:
        new_image_file.write(img.get_file()) 

def video_datetime_change(filename, tarih):    
    timeZone = datetime.datetime.strptime("03","%H")
    result_with_timezone = datetime.datetime.strptime(tarih,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=timeZone.hour)
    result_with_timezone = result_with_timezone.strftime('%Y:%m:%d %H:%M:%S')
    
    ctime = tarih.replace('-',':')
    
    filename = filename.replace(" ", "\" \"")
    
    com1 = ["TrackCreateDate", "TrackModifyDate", "MediaCreateDate", "MediaModifyDate"]
    com2 = ["CreateDate", "ModifyDate"]
    

    for co1 in com1:
        commandd1 = 'exiftool -api QuickTimeUTC "-'+ co1 +'='+ctime+'" '+ filename
        os.system('"' + commandd1 + '"')
 
    for co2 in com2:
        commandd2 = 'exiftool -api -DateTimeOriginal+=3 "-'+ co2 +'='+result_with_timezone+'" '+ filename
        os.system('"' + commandd2 + '"')

# get date and time info
def extract_datetime(file_name):
    date_time = None

    date_pattern = re.compile(r"(\d{4})[\d._-]?(\d{2})[\d._-]?(\d{2})")
    date_match = date_pattern.search(file_name)
    if date_match:
        date_time = "-".join(date_match.groups()) + " 00:00:00"


    datetime_pattern = re.compile(r"(\d{4})[._-]?(\d{2})[._-]?(\d{2})[._-]?(\d{2})[._-]?(\d{2})[._-]?(\d{2})")
    datetime_match = datetime_pattern.search(file_name)
    if datetime_match:
        date_time = "-".join(datetime_match.groups()[:3]) + " " + ":".join(datetime_match.groups()[3:]) 

    return date_time  
    
# changes create, modified and accessed time
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
    


  



if __name__ == '__main__':
    main()