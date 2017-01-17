.. _usage:

Usage
=====

Here is the command-line help:

.. code-block:: bash

   $> find_agg -h
   usage: find_agg [--agg [$PWD/aggregations.list]] [--miss [$PWD/missing_data.list]] [--log [$PWD]]
                   [-v] [-h] [-V]
                   [inputfile]

   Find CMIP5 aggregations according to requirements
   upon local IPSL-ESGF datanode (THREDDS server) or into CICLAD filesystem.

   The default values are displayed next to the corresponding flags.

   See full documentation and references on http://prodiguer.github.io/find-agg/.

   positional arguments:
     inputfile                        Path of the JSON template with the requirements of the request.

   optional arguments:
     --agg [$PWD/aggregations.list]   Output file with available aggregations list.

     --miss [$PWD/missing_data.list]  Output file with the list of missing data.

     --log [$PWD]                     Logfile directory.
                                      An existing logfile can be submitted.
                                      If not, standard output is used.

     -v                               Verbose mode.

     -h, --help                       Show this help message and exit.

     -V                               Program version

   Developed by:
   Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)
   Greenslade, M., (UPMC/IPSL - momipsl@ipsl.jussieu.fr)


Tutorials
*********

Check aggregations status depending on a JSON request:

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json
   YYYY/MM/DD HH:MM:SS PM INFO ==> Searching for aggregations...
   YYYY/MM/DD HH:MM:SS PM INFO +----------------------------------------------------+
   YYYY/MM/DD HH:MM:SS PM INFO |       MODEL        |    OpenDAP    |      CDAT     |
   YYYY/MM/DD HH:MM:SS PM INFO +====================================================+
   YYYY/MM/DD HH:MM:SS PM INFO | ACCESS1-3          | COMPLETE      | COMPLETE      |
   YYYY/MM/DD HH:MM:SS PM INFO | ACCESS1-0          | INCOMPLETE    | COMPLETE      |
   YYYY/MM/DD HH:MM:SS PM INFO | HadGEM2-AO         | COMPLETE      | NONE          |
   YYYY/MM/DD HH:MM:SS PM INFO | CSIRO-Mk3L-1-2     | COMPLETE      | COMPLETE      |
   [...]
   YYYY/MM/DD HH:MM:SS PM INFO +----------------------------------------------------+
   YYYY/MM/DD HH:MM:SS PM INFO ==> Search complete.

Save your discovery in output files (``--agg`` for aggregation list and ``--miss`` for missing data list, both are optional):

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json --agg /path/to/aggregation.list --miss /path/to/missing_data.list
   YYYY/MM/DD HH:MM:SS PM INFO ==> Searching for aggregations...
   YYYY/MM/DD HH:MM:SS PM INFO +----------------------------------------------------+
   YYYY/MM/DD HH:MM:SS PM INFO |       MODEL        |    OpenDAP    |      CDAT     |
   YYYY/MM/DD HH:MM:SS PM INFO +====================================================+
   YYYY/MM/DD HH:MM:SS PM INFO | ACCESS1-3          | COMPLETE      | COMPLETE      |
   YYYY/MM/DD HH:MM:SS PM INFO | ACCESS1-0          | INCOMPLETE    | COMPLETE      |
   YYYY/MM/DD HH:MM:SS PM INFO | HadGEM2-AO         | COMPLETE      | NONE          |
   YYYY/MM/DD HH:MM:SS PM INFO | CSIRO-Mk3L-1-2     | COMPLETE      | COMPLETE      |
   [...]
   YYYY/MM/DD HH:MM:SS PM INFO +----------------------------------------------------+
   YYYY/MM/DD HH:MM:SS PM INFO ==> Search complete.

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

Use a logfile (the logfile directory is optional):

.. code-block:: bash

   $> find_agg /path/to/your/requirements.json -log /path/to/logfile

   $> cat /path/to/logfile/findagg-YYYYMMDD-HHMMSS-PID.log
   cat find_agg-20150707-143316-29540.log 
   YYYY/MM/DD HH:MM:SS PM INFO ==> Searching for aggregations...
   YYYY/MM/DD HH:MM:SS PM INFO +----------------------------------------------------+
   YYYY/MM/DD HH:MM:SS PM INFO |       MODEL        |    OpenDAP    |      CDAT     |
   YYYY/MM/DD HH:MM:SS PM INFO +====================================================+
   YYYY/MM/DD HH:MM:SS PM INFO | ACCESS1-3          | COMPLETE      | COMPLETE      |
   YYYY/MM/DD HH:MM:SS PM INFO | ACCESS1-0          | INCOMPLETE    | COMPLETE      |
   YYYY/MM/DD HH:MM:SS PM INFO | HadGEM2-AO         | COMPLETE      | NONE          |
   YYYY/MM/DD HH:MM:SS PM INFO | CSIRO-Mk3L-1-2     | COMPLETE      | COMPLETE      |
   [...]
   YYYY/MM/DD HH:MM:SS PM INFO +----------------------------------------------------+
   YYYY/MM/DD HH:MM:SS PM INFO ==> Search complete.
