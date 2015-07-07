********
Synopsis
********

The IPSL uses an ESG-F (Earth System Grid Federation) datanode to publish and diffuse CMIP5 data located on CICLAD filesystem (``/prodigfs/esg/CMIP5/merge``) to its private reasearch community. This datanode could be query to find specific NetCDF files, through the `web front-end <http://esgf-node.ipsl.fr/esgf-web-fe/>`_.

Based on a THREDDS server, the CMIP5 files are fictitiously concacenated along time dimension throught OpenDAP URL. These aggregations avoid to deal with the files splitting depending on model and frequency over a time period.

Moreover, the IPSL CMIP5 post-processing pipeline adds CDAT aggregations  using ``cdscan`` command-line with XML format. These aggregations are located in ``/prodigfs/esg/xml/CMIP5``.

``find_agg`` is a command-line tool allowing you to find and list the availale CMIP5 aggregations at IPSL in a fast and researcher-friendly way. This tool includes search over THREDDS and/or XML aggregations availables at IPSL.


Features
++++++++

**As the logical operator AND**
  The search-API from ESG-F front-ends displays the results of your request using an *OR* logical operator. For example, this means you cannot select the temperature **AND** the precitation for the same model or institute. Here, ``find_agg`` follows **ALL** your requirements. All returned models satisfy your entire request.

**Quick discovery**
  ``find_agg`` builds all possible aggregations following your request and using a combinatorial algorithm. Then, all URLs are tested using multithreading.

**Includes THREDDS and/or XML aggregation search**
  You can choose to do your research on THREDDS aggregations, XML aggregations or both. At least one option ``--tds`` or ``--xml`` must be given (see :ref:`usage`).

**Intersection between both sources**
  The search on THREDDS and/or XML aggregation could give different results with two different lists of available models. You can change this default behaviour from union to intersection of results. Consequently, the returned model list satisfies your request both for THREDDS and XML aggregations.

**Display missing data on the filesystem**
  When an aggregation test fails, you can choosse to walk through ``/prodigfs/esg/CMIP5/merge``. This returns the list of missing data in the CMIP5 tree. This information can be easily used to build `a SYNDA template <https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/TEMPLATE>`_ making a downloading request at IPSL.

**Useful template**
  Your request can be easily formatted using the ``requierments.json`` template. You just need to know the `CMIP5 vocabulary <http://cmip-pcmdi.llnl.gov/cmip5/data_description.html>`_ to build your request in a researcher-friendly way (see :ref:`configuration`).

**Use a logfile**
  You can initiate a logger instead of the standard output. This could be useful for automatic workflows. The logfile name is automatically defined and unique (using the date and the job's PID). You can define an output directory for your logs.
