import os
import sys

from jinja2 import Environment, FileSystemLoader
import argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='')
parser.add_argument('input_folder', type=str)
parser.add_argument('output_folder', type=str)

args = parser.parse_args()
input_folder = args.input_folder 
output_folder = args.output_folder

print(os.listdir(input_folder))

mylist = []

j2_env = Environment(loader=FileSystemLoader(THIS_DIR),trim_blocks=True)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_content_path = os.path.join(output_folder,'output.yml')
if os.path.exists(output_content_path):
    raise IOError('File exists, not running remaining code! {}'.format(output_content_path))

output_html_path = os.path.join(output_folder,'index.html')
with open(output_html_path,'w') as f:
    html_content = j2_env.get_template(os.path.join(THIS_DIR,'template.html')).render(mylist)
    f.write(html_content)

