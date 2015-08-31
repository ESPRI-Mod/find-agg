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
                           (default is '$(pwd)/aggregations.list').
                           
     -m [MISSING], --missing [MISSING]
                           Outputfile with the list of missing data
                           (default is '$(pwd)/missing_data.list').
                           
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

   $> find_agg /path/to/your/requirements.json --tds
   ==> Starting search on http://esgf-local.ipsl.fr/
   All THREDDS aggregations available for bcc-csm1-1-m
   All THREDDS aggregations available for CanESM2
   All THREDDS aggregations available for CNRM-CM5
   [...]
   ==> Search complete.

To find XML aggregations:

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --xml
   ==> Starting search in /prodigfs/esg/xml/CMIP5
   All XML aggregations available for bcc-csm1-1
   All XML aggregations available for bcc-csm1-1-m
   All XML aggregations available for CanESM2
   [...]
   ==> Search complete.

To find both XML and THREDDS aggregations:

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --tds --xml
   ==> Starting search in /prodigfs/esg/xml/CMIP5
   All XML aggregations available for bcc-csm1-1
   All XML aggregations available for bcc-csm1-1-m
   All THREDDS aggregations available for bcc-csm1-1-m
   All XML aggregations available for CanESM2
   All THREDDS aggregations available for CanESM2
   All THREDDS aggregations available for CNRM-CM5
   [...]
   ==> Search complete.

To find the intersection of available aggregations (XML *AND* THREDDS):

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --tds --xml -i
   ==> Starting search in /prodigfs/esg/xml/CMIP5
   All XML aggregations available for bcc-csm1-1-m
   All THREDDS aggregations available for bcc-csm1-1-m
   All XML aggregations available for CanESM2
   All THREDDS aggregations available for CanESM2
   [...]
   ==> Search complete.

To save your research in output files (``-o`` for aggregation list and ``-m`` for missing data list, both are optionnal):

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --xml -o /path/to/aggregation.list -m /path/to/missing_data.list
   ==> Starting search in /prodigfs/esg/xml/CMIP5
   All XML aggregations available for bcc-csm1-1
   All XML aggregations available for bcc-csm1-1-m
   All XML aggregations available for CanESM2
   [...]
   ==> Search complete.

   $> cat /path/to/aggregation.list
   /prodigfs/esg/xml/CMIP5/piControl/atmos/mon/pr/cmip5.bcc-csm1-1.piControl.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/xml/CMIP5/piControl/atmos/mon/tas/cmip5.bcc-csm1-1.piControl.r1i1p1.mon.atmos.Amon.tas.latest.xml
   /prodigfs/esg/xml/CMIP5/1pctCO2/atmos/mon/pr/cmip5.bcc-csm1-1.1pctCO2.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/xml/CMIP5/1pctCO2/atmos/mon/tas/cmip5.bcc-csm1-1.1pctCO2.r1i1p1.mon.atmos.Amon.tas.latest.xml
   /prodigfs/esg/xml/CMIP5/rcp26/atmos/mon/pr/cmip5.bcc-csm1-1.rcp26.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/xml/CMIP5/rcp26/atmos/mon/tas/cmip5.bcc-csm1-1.rcp26.r1i1p1.mon.atmos.Amon.tas.latest.xml
   [...]

   $> cat /path/to/missing_data.list
   /prodigfs/esg/xml/CMIP5/piControl/atmos/mon/tas/cmip5.CanCM4.piControl.r1i1p1.mon.atmos.Amon.tas.latest.xml
   /prodigfs/esg/xml/CMIP5/1pctCO2/atmos/mon/pr/cmip5.CanCM4.1pctCO2.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/xml/CMIP5/piControl/atmos/mon/pr/cmip5.CanCM4.piControl.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/xml/CMIP5/1pctCO2/atmos/mon/tas/cmip5.CanCM4.1pctCO2.r1i1p1.mon.atmos.Amon.tas.latest.xml
   /prodigfs/esg/xml/CMIP5/rcp85/atmos/mon/pr/cmip5.CanCM4.rcp85.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/xml/CMIP5/rcp26/atmos/mon/tas/cmip5.CanCM4.rcp26.r1i1p1.mon.atmos.Amon.tas.latest.xml
   /prodigfs/esg/xml/CMIP5/rcp85/atmos/mon/tas/cmip5.CanCM4.rcp85.r1i1p1.mon.atmos.Amon.tas.latest.xml
   /prodigfs/esg/xml/CMIP5/rcp26/atmos/mon/pr/cmip5.CanCM4.rcp26.r1i1p1.mon.atmos.Amon.pr.latest.xml
   /prodigfs/esg/CMIP5/merge/CCCma/CanCM4/rcp26
   /prodigfs/esg/CMIP5/merge/CCCma/CanCM4/piControl
   /prodigfs/esg/CMIP5/merge/CCCma/CanCM4/rcp85
   /prodigfs/esg/CMIP5/merge/CCCma/CanCM4/1pctCO2
   [...]

Use verbose mode to print missing data:

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --xml -v
   ==> Starting search in /prodigfs/esg/xml/CMIP5
   All XML aggregations available for bcc-csm1-1
   All XML aggregations available for bcc-csm1-1-m
   All XML aggregations available for CanESM2
   cmip5.CanCM4.piControl.r1i1p1.mon.atmos.Amon.tas.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.1pctCO2.r1i1p1.mon.atmos.Amon.pr.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.piControl.r1i1p1.mon.atmos.Amon.pr.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.1pctCO2.r1i1p1.mon.atmos.Amon.tas.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.rcp85.r1i1p1.mon.atmos.Amon.pr.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.rcp26.r1i1p1.mon.atmos.Amon.tas.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.rcp85.r1i1p1.mon.atmos.Amon.tas.latest.xml not available in /prodigfs/esg/xml/CMIP5
   cmip5.CanCM4.rcp26.r1i1p1.mon.atmos.Amon.pr.latest.xml not available in /prodigfs/esg/xml/CMIP5
   ./CCCma/CanCM4/rcp26 does not exist on filesystem
   ./CCCma/CanCM4/piControl does not exist on filesystem
   ./CCCma/CanCM4/rcp85 does not exist on filesystem
   ./CCCma/CanCM4/1pctCO2 does not exist on filesystem
   [...]
   ==> Search complete.

To use a logfile (the logfile directory is optionnal):

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --xml -l /path/to/logfile

   $> cat /path/to/logfile/findagg-YYYYMMDD-HHMMSS-PID.log
   cat find_agg-20150707-143316-29540.log 
   YYYY/MM/DD HH:MM:SS PM INFO ==> Starting search in /prodigfs/esg/xml/CMIP5
   YYYY/MM/DD HH:MM:SS PM INFO All XML aggregations available for bcc-csm1-1
   YYYY/MM/DD HH:MM:SS PM INFO All XML aggregations available for bcc-csm1-1-m
   YYYY/MM/DD HH:MM:SS PM INFO All XML aggregations available for CanESM2
   [...]
   YYYY/MM/DD HH:MM:SS PM INFO ==> Search complete.

