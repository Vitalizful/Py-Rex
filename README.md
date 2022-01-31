# Py-Rex

Developed by David Baudoin

Py-Rex is a Python based regular expression extractor and so much more!

How to use is :

1) Download all the files from this repository

2) Add all the text files you want the extraction to perform on inside the Py-Rex/data folder

3) Open the Py-Rex/config_recist/param_config text file

In this file at the "output_result" line you can choose for either a text file result by writing "txt", an excel file with "csv", a brat file with "ann" or any combination of the three "csv + ann + txt"

4) Open a terminal within Py-Rex folder

5) You can now launch the extraction :

 - a single file at the time with :

python transfert_CRdataToJson.py --directory config_recist --cr data/path/to/your/file.txt

- on the whole dataset with :

find data/your_folder_path/ -type f -print0 | xargs -0 -n1 python transfert_CRdataToJson.py --directory config_recist --cr

- you can also use the parallelization in order to shorten the processing time (change -P20 with the amout of CPU core available to you) :

find data/your_folder_path/ -type f -print0 | xargs -0 -n1 -P20 python transfert_CRdataToJson.py --directory config_recist --cr
