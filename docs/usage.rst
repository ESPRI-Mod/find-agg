.. _usage:

*****
Usage
*****

Here is the command-line help:

.. code-block:: bash

   $> find_agg -h
   usage: findagg.py [-h] [--tds] [--xml] [-i] [-o [OUTPUTFILE]] [-m [MISSING]]
                     [-l [LOGDIR]] [-v] [-V]
                     [inputfile]

   Find CMIP5 aggregations according to requirements
   upon local IPSL-ESGF datanode (THREDDS server) or into CICLAD filesystem.

   positional arguments:
     inputfile             Path of the JSON template with the requirements of the request
                           (a template can be found in ~/anaconda/lib/python2.7/site-packages/findagg/requirements.json).

   optional arguments:
     -h, --help            Show this help message and exit.
                           
     --tds                 Search THREDDS aggregations from ESG-F local node.
                           
     --xml                 Search XML aggregations from CDAT (cdscan).
                           
     -i, --inter           Intersection between XML and THREDDS aggregations results
                           (required --xml and --tds, default is union of results).
                           
     -o [OUTPUTFILE], --outputfile [OUTPUTFILE]
                           Outputfile with available aggregations list
                           (default is working directory).
                           
     -m [MISSING], --missing [MISSING]
                           Outputfile with the list of missing data
                           (default is working directory).
                           
     -l [LOGDIR], --logdir [LOGDIR]
                           Logfile directory (default is working directory).
                           If not, standard output is used.
                           
     -v, --verbose         Shows missing data
                           (default only shows available models).
                           
     -V, --version         Program version

   Developed by Levavasseur, G., and Greenslade, M., (CNRS/IPSL)


Tutorials
---------

To find THREDDS aggregations:

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --tds -v
   ==> Starting search on http://esgf-local.ipsl.fr/
   All THREDDS aggregations available for bcc-csm1-1-m
   All THREDDS aggregations available for CanESM2
   All THREDDS aggregations available for CNRM-CM5
   [...]
   ==> Search complete.

To find XML aggregations:

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --xml -v
   ==> Starting search in /prodigfs/esg/xml/CMIP5
   All XML aggregations available for bcc-csm1-1
   All XML aggregations available for bcc-csm1-1-m
   All XML aggregations available for CanESM2
   [...]
   ==> Search complete.
