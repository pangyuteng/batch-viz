import os
import sys
import shutil
import argparse
import yaml
import SimpleITK as sitk
from scipy.misc import imsave
import numpy as np
from jinja2 import Environment, FileSystemLoader
import yaml

# THIS_DIR used by jinja2 to locate template.html
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BLANKGIF = os.path.join(THIS_DIR,'blank.gif')
JQUERY = os.path.join(THIS_DIR,'jquery.min.js')

# if __name__ == '__main__':

parser = argparse.ArgumentParser(description='')
parser.add_argument('input_yml', type=str)
parser.add_argument('output_folder', type=str)
parser.add_argument('-f','--force', type=str, choices=['True','False'],default='False')
parser.add_argument('-s','--skip', type=str, choices=['True','False'],default='False')
parser.add_argument('-p','--pdf', type=str, choices=['True','False'],default='False')

args = parser.parse_args()
input_yml = os.path.abspath(args.input_yml)
output_folder = os.path.abspath(args.output_folder)
force = eval(args.force)
skip = eval(args.skip)
pdf = eval(args.pdf)

# custom logic for visualization

def read(fpath):
    reader= sitk.ImageFileReader()
    reader.SetFileName(fpath)
    img = reader.Execute()
    arr = sitk.GetArrayFromImage(img)    
    spacing = img.GetSpacing()
    origin = img.GetOrigin()
    direction = img.GetDirection()    
    return arr,spacing,origin,direction

output_content_path = os.path.join(output_folder,'output.yml')
output_html_path = os.path.join(output_folder,'index.html')
output_pdf_path = os.path.join(output_folder,'index.pdf')

if os.path.exists(output_content_path) and force is False and skip is False:
    raise IOError('File exists, not running remaining code! {}'.format(output_content_path))

static_folder = os.path.join(output_folder,'static')
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

with open(input_yml,'r') as f:
    file_list = yaml.load(f.read())

if os.path.exists(os.path.abspath(file_list[0])) is False:
    folda = os.path.dirname(input_yml)
    file_list = [os.path.join(folda,x) for x in file_list]

if os.path.exists(os.path.abspath(file_list[0])) is False:
    raise IOError('cannot find files in input yml!')

if not skip:
    mylist = []
    total_n = len(file_list)
    for n,file_path in enumerate(file_list):
        filename = os.path.basename(file_path)
        print(filename,n,total_n)
        sagittal_0_path = os.path.join(static_folder,filename+'_sagittal_0.png')
        sagittal_1_path = os.path.join(static_folder,filename+'_sagittal_1.png')
        axial_path = os.path.join(static_folder,filename+'_axial.png')
        coronal_path = os.path.join(static_folder,filename+'_coronal.png')
        contrast_path = os.path.join(static_folder,filename+'_cotrast.png')
        
        arr,spacing,origin,direction=read(file_path)    
        contrast = np.copy(arr)

        contrast[contrast>200] = 0
        contrast[contrast<100] = 0
        contrast = np.sum(contrast,axis=1).squeeze()
        print(contrast.shape)
        minval = np.min(contrast)
        maxval = np.max(contrast)
        contrast = 255*(contrast-minval)/(maxval-minval)
        contrast = np.clip(contrast,0,255)
        contrast = contrast.astype(np.uint8)
        imsave(contrast_path,contrast)
        
        # lung ct window level
        level = -400.
        window = 1500.
        minval = level-(window/2.)
        maxval = level+(window/2.)
        
        arr = 255*(arr-minval)/(maxval-minval)
        arr = np.clip(arr,0,255)
        arr = arr.astype(np.uint8)
        mid_x,mid_y,mid_z = (np.array(arr.shape)/2.0).astype(int)
        
        sagittal_0 = arr[:,:,int(1*(mid_z*2/3))].squeeze()
        imsave(sagittal_0_path,sagittal_0)
        
        sagittal_1 = arr[:,:,int(2*(mid_z*2/3))].squeeze()
        imsave(sagittal_1_path,sagittal_1)
        
        axial = arr[mid_x,:,:].squeeze()
        imsave(axial_path,axial)

        coronal = arr[:,mid_y,:].squeeze()
        imsave(coronal_path,coronal)
        
        mylist.append(dict(
            file_path=file_path,
            contrast_path=os.path.relpath(contrast_path,start=output_folder),
            axial_path=os.path.relpath(axial_path,start=output_folder),
            coronal_path=os.path.relpath(coronal_path,start=output_folder),
            sagittal_0_path=os.path.relpath(sagittal_0_path,start=output_folder),
            sagittal_1_path=os.path.relpath(sagittal_1_path,start=output_folder),
        ))
else:
    with open(output_content_path,'r') as f:
        mylist = yaml.load(f.read())

# store content to yml, as done file.
if not os.path.exists(output_content_path) or force is True:
    with open(output_content_path,'w') as f:
        f.write(yaml.dump(mylist))

# render html with content via jinja
shutil.copy(BLANKGIF,os.path.join(output_folder,'blank.gif'))
shutil.copy(JQUERY,os.path.join(output_folder,'jquery.min.js'))
j2_env = Environment(loader=FileSystemLoader(THIS_DIR),trim_blocks=True)    
with open(output_html_path,'w') as f:
    html_content = j2_env.get_template('template.html').render(mylist=mylist,blankgif='blank.gif',jquery='jquery.min.js')
    f.write(html_content)

# html to pdf
if pdf:
    import subprocess
    subprocess.check_output(['wkhtmltopdf',output_html_path,output_pdf_path])