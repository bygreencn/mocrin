###################### INFORMATION #############################
#           Dont ask! It is the Ocronator..!
# Program:  **Ocronator**
# Info:     **Python 3.6**
# Author:   **Jan Kamlah**
# Date:     **30.11.2017**

######### IMPORT ############
import configparser
from PIL import Image
import pytesseract
import argparse
import cv2 as cv2
import os
import glob as glob2
import subprocess
from multiprocessing import Process

####################### CMD-PARSER-SETTINGS ########################
def get_args():
    parser = argparse.ArgumentParser()
    #args.add_argument("-i", "--image", required=True,help="path to input image to be OCR'd")
    #args.add_argument("-p", "--preprocess", type=str, default="thresh",help="type of preprocessing to be done")
    parser.add_argument("--no-tess", action='store_true', help="Don't perfom tessract.")
    parser.add_argument("--no-ocropy", action='store_true', help="Don't perfom ocropy.")
    parser.add_argument("--tess-profile", value='default', choices=["default"], help="Don't perfom tessract.")
    parser.add_argument("--ocropy-profile", value='default', choices=["default"], help="Don't perfom ocropy.")
    args = parser.parse_args()
    return args

######### FUNCTIONS ############
def create_dir(newdir:str)->int:
    """
    Creates a new directory
    """
    if not os.path.isdir(newdir):
        try:
            os.makedirs(newdir)
            print(newdir)
        except IOError:
            print("cannot create %s directoy" % newdir)
    return 0

def start_tess(file,fp):
    create_dir(fp)
    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    text = pytesseract.image_to_string(Image.open(file), lang="deu")
    with open(fp + file.split('/')[-1] + '.txt', 'w') as output:
        output.write(text)
        # show the output images
        # cv2.imshow("Image", file)
        # cv2.imshow("Output", gray)
        # cv2.waitKey(0)
    return 0

def start_ocropy(file,fp):
    fname = file.split('/')[-1].split('.')[0]
    create_dir(fp)
    subprocess.Popen(args=["ocropus-nlbin",file,"-o"+fp+fname+"/"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg",fp+fname+"/????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-rpred","-Q 4",fp+fname+"/????/??????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-hocr",fp+fname+"/????.bin.png","-o"+fp+"/"+file.split('/')[-1]+".html"]).wait()
    return 0


################ START ################
if __name__ == "__main__":
    """
    Entrypoint: Searches for the files and parse them into the mainfunction (can be multiprocessed)
    """
    # The filespath are stored in the config.ini file.
    # And can be changed there.
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    args = get_args()
    pathx = config['DEFAULT']['allpath']
    pathxoutput = config['DEFAULT']['allpath_output']
    tess_profile = config['DEFAULT']['Tessprofile']+""
    ocropy_profile = config['DEFAULT']['Ocropyprofile']
    for filen in ['short','long']:
        for i in [1957,1961,1965,1969,1973,1976]:
            path = pathx+filen+"/"+str(i)+"/*"
            pathoutput = pathxoutput + filen + "/" + str(i) + "/"
            # Get all filenames and companynames
            files = glob2.glob(path)
            for idx, file in enumerate(files):
                if not args.no_tess:
                    print("Starts with Tesseract!")
                    p1 = Process(target=start_tess,args=[file,pathoutput+ "tess/"])
                    p1.start()
                if not args.no_ocropy:
                    print("Starts with Ocropus!")
                    p2 = Process(target=start_ocropy,args=[file,pathoutput+ "ocropy/"])
                    p2.start()
                if not args.no_tess:
                    p1.join()
                if not args.no_ocropy:
                    p2.join()
                print("Next image!")
                #start_tess(file,pathoutput+ "tess/"))
                #start_ocropy(file,pathoutput+ "ocropy/")
    print("FINISHED!")