import os
import sys

from jinja2 import Environment, FileSystemLoader
import argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='')
parser.add_argument('input_folder', type=str)
parser.add_argument('output_folder', type=str)
parser.add_argument('-f','--force', type=str, choices=['True','False'],default='False')

args = parser.parse_args()
input_folder = args.input_folder 
output_folder = args.output_folder
force = eval(args.force)

# custom logic for visualization
import SimpleITK as sitk
import yaml
from scipy.misc import imsave
import numpy as np

def read(fpath):
    reader= sitk.ImageFileReader()
    reader.SetFileName(fpath)
    img = reader.Execute()
    arr = sitk.GetArrayFromImage(img)    
    spacing = img.GetSpacing()
    origin = img.GetOrigin()
    direction = img.GetDirection()    
    return arr,spacing,origin,direction

static_folder = os.path.join(output_folder,'static')
if not os.path.exists(static_folder):
    os.makedirs(static_folder)
print('ok')
mylist = []
for filename in [x for x in os.listdir(input_folder) if x.endswith('.mhd')]:
    print(filename)
    file_path = os.path.join(input_folder,filename)
    arr,spacing,origin,direction=read(file_path)
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
    sagittal_0_path = os.path.join(static_folder,filename+'_sagittal_0.png')
    imsave(sagittal_0_path,sagittal_0)
    
    sagittal_1 = arr[:,:,int(2*(mid_z*2/3))].squeeze()
    sagittal_1_path = os.path.join(static_folder,filename+'_sagittal_1.png')
    imsave(sagittal_1_path,sagittal_1)
    
    axial = arr[:,mid_y,:].squeeze()
    axial_path = os.path.join(static_folder,filename+'_axial.png')
    imsave(axial_path,axial)

    coronal = arr[mid_x,:,:].squeeze()
    coronal_path = os.path.join(static_folder,filename+'_coronal.png')
    imsave(coronal_path,coronal)
    
    mylist.append(dict(
        file_path=file_path,
        axial_path=axial_path,
        coronal_path=coronal_path,
        sagittal_0_path=sagittal_0_path,
        sagittal_1_path=sagittal_1_path,
    ))
    break
print(mylist,'(*(***')
output_content_path = os.path.join(output_folder,'output.yml')
if os.path.exists(output_content_path) and force is False:
    raise IOError('File exists, not running remaining code! {}'.format(output_content_path))

with open(output_content_path,'w') as f:
    f.write(yaml.dump(mylist))

j2_env = Environment(loader=FileSystemLoader(THIS_DIR),trim_blocks=True)    
output_html_path = os.path.join(output_folder,'index.html')
with open(output_html_path,'w') as f:
<<<<<<< HEAD
    html_content = j2_env.get_template('template.html').render(mylist=mylist)
=======
    html_content = j2_env.get_template(os.path.join(THIS_DIR,'template.html')).render(mylist)
>>>>>>> 5422896b0d14b25bc499123fbc7b9e8b03ee3f84
    f.write(html_content)

