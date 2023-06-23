# IM-Python-API

Python module providing utilitary functionalities when working with an ACQUIFER Imaging Machine.  
Functionalities include :  
- metadata persing from filenames  

It should work in python 2 AND 3 environment, however it will not work in jython within Fiji (no more module socket).  
In Fiji, the java package acquifer-core should be used for that purpose.  

## Installation
The package can be installed locally for test purpose using 
`pip install -e .` with e for "experimental"  
This way any change to the code is directly reflected. 