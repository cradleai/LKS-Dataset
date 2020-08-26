"""
This module can be used to preprocess the LKS Dataset (https://github.com/cradleai/LKS-Dataset
as described in the paper - SOS: Selective Objective Switch for Rapid Immunofluorescence Whole
Slide Image Classification (DOI: 10.1109/CVPR42600.2020.00392).

Dependencies:
This module requires the libvips image processing library which can be
downloaded from: https://libvips.github.io/libvips/

Running the Script:
To use this module, simply modify the source and target dataset path variables (lines 22 and 23)
and run the script.

Written by Sam Maksoud 26/08/2020
Permitted for reuse with acknowledgement
"""

import csv
import os
import subprocess

#Modify these variables to suit your environment.
SOURCE_DPATH = "P:/LKS/dataset" #Path to source dataset
TARGET_DPATH = "C:/workspace/prepro_lks" #Path to save preprocessed images

def clear_temp():
    """
    Vips stores alot in temp drive. Use this code to clear temp while the script is running.
    """
    clr_tmp = ["del", "/q/f/s", r"%TEMP%\*"]
    subprocess.call(clr_tmp, shell=True)
    print("Temp files are cleared")

def preprocess_image(dsplit, _class, fname):
    """
    This function will preprocess the WSI "fname"
    and store files in the directory "./TARGET_DPATH/dsplit/_class"
    """
    name = fname.replace(".tif","")
    target_dir = os.path.join(TARGET_DPATH,dsplit, _class,name)
    os.makedirs(target_dir,exist_ok=True)

    bigtif = os.path.join(SOURCE_DPATH, dsplit, fname)
    croptif = '%s/temp.tif'%TARGET_DPATH
    lowres = '%s/lowres.jpg'%target_dir
    patch_dir = '%s/highres_patches'%target_dir

    print("Center cropping %s"%name)
    vips_crop= ["vips", "smartcrop", bigtif, croptif, "40000", "40000",
                "--interesting" ,"VIPS_INTERESTING_CENTRE"]
    subprocess.call(vips_crop, shell=True)
    print("Creating lowres image for %s"%name)
    vips_resize = ["vips", "shrink", croptif, lowres, "40", "40"]
    subprocess.call(vips_resize, shell=True)
    print("Creating highres patches for %s"%name)
    vips_patch = ["vips", "dzsave", croptif, patch_dir,
                  "--suffix",".jpg[Q=100]", "--tile-size", "1000",
                  "--overlap", "0", "--depth", "one"]
    subprocess.call(vips_patch, shell=True)

    os.remove(croptif)
    os.rename("%s_files"%patch_dir, patch_dir.replace("files", "patches"))

    #clear_temp() #uncomment this line to clear temp files while running script

def main():
    """This function will parse the labels and image paths in both Train and Test sets
       and call the preprocess function for each WSI.
    """
    for dsplit in ["Train", "Test"]:
        with open(SOURCE_DPATH+"/%s_Labels.csv"%dsplit) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                fname = row[0]
                _class = row[1]
                print(os.path.join(TARGET_DPATH,_class))
                os.makedirs(os.path.join(TARGET_DPATH,_class), exist_ok=True)
                preprocess_image(dsplit, _class, fname)
                input("and??")

if __name__ == "__main__":
    main()
