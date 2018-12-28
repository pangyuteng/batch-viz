`python gen.py content.yml out_path`

where `content.yml` contains a list of mhd/nifti file paths and `out_path` is the desired output folder path.

example usage:

 - in a box that is closest to the data source.
 - run the script
 - launch jupyter notebook
 - and then browse the generated html file.
 - the `-pdf` flag will not work since lazyload is added to `template.html`
 
`python gen.py /media/external/Downloads/data/luna16.yml luna16`
