## Usage example

- Print help/usage.

```Shell
$> ./find_agg.py -h
usage: find_agg.py [-h] [-o [OUTPUTFILE]] [--tds] [--xml] [-m [MISSING]]
                   [-l [LOGDIR]] [-i] [-v] [-V]
                   [inputfile]

Find CMIP5 aggregations according to requirements
upon local IPSL-ESGF datanode (THREDDS server) or into CICLAD filesystem.

positional arguments:
  inputfile             Path of the JSON template with the requirements of the request.


optional arguments:
  -h, --help            Show this help message and exit.

  -o [OUTPUTFILE], --outputfile [OUTPUTFILE]
                        Outputfile with available aggregation list
                        (default is '{workdir}/aggregations.list').

  -m [MISSING], --missing [MISSING]
                        Outputfile with the list of missing data
                        (default is '{workdir}/missing_data.list').

  -l [LOGDIR], --logdir [LOGDIR]
                        Logfile directory (default is working directory).
                        If not, standard output is used.

  -i, --inter           Intersection between XML and THREDDS aggregations results
                        (default is union of results, required --xml and --tds).

  -v, --verbose         Shows missing data
                        (default only shows available models).

  -V, --version         Program version

Search into (at least one required):
  --tds                 THREDDS agregations.

  --xml                 XML agregations from cdscan.


Developped by Levavasseur, G., and Greenslade, M., (CNRS/IPSL)
```

- Run the script to find THREDDS aggregations:

```Shell
$> ./find_agg.py requirements.json --tds -v
Starting search on http://esgf-local.ipsl.fr/
All THREDDS aggregations available for bcc-csm1-1-m
All THREDDS aggregations available for CanESM2
All THREDDS aggregations available for CNRM-CM5
[...]
Search complete.
```
- Save XML aggregations to outfile:

```Shell
$> ./find_agg.py requirements.json --xml -v -o
Starting search in /prodigfs/esg/xml/CMIP5
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
All XML aggregations available for CNRM-CM5
[...]
Search complete.

$> cat aggregations.list
/prodigfs/esg/xml/CMIP5/piControl/atmos/mon/pr/cmip5.bcc-csm1-1.piControl.r1i1p1.mon.atmos.Amon.pr.latest.xml
/prodigfs/esg/xml/CMIP5/piControl/atmos/mon/tas/cmip5.bcc-csm1-1.piControl.r1i1p1.mon.atmos.Amon.tas.latest.xml
/prodigfs/esg/xml/CMIP5/1pctCO2/atmos/mon/pr/cmip5.bcc-csm1-1.1pctCO2.r1i1p1.mon.atmos.Amon.pr.latest.xml
[...]
```

The verbose mode displays missing aggregations or data on filesystem.

- Find intersection of all available aggregation (XML AND THREDDS) (all available models are displayed twice):

```Shell
$> ./find_agg.py requirements.json --xml --tds -i
Starting search on http://vesg3.ipsl.fr/ and in /prodigfs/esg/xml/CMIP5
All THREDDS aggregations available for bcc-csm1-1-m
All XML aggregations available for bcc-csm1-1-m
All THREDDS aggregations available for CanESM2
All XML aggregations available for CanESM2
All THREDDS aggregations available for CNRM-CM5
All XML aggregations available for CNRM-CM5
[...]
```
- You can also print missing data with ```missing_data.list``` when saved using ```-m``` option.

- Full path of output files can be given.
