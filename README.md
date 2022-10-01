# maya-pipeline-distributable-template

gTools is a pipeline distributable that is source control friendly and not restrained to a specific path  
To install simply drag and drop the install.py into your maya and it will create a .mod file pointing to your pipeline location  

__How it works:__  
The pipeline uses a bootloader to run various modules, starting with the core module (currently "gTools" in this template)  
To add more modules start by copying the startup template file and adding your boot functions and imports from there.  
