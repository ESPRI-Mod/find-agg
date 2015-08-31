********
Synopsis
********

The `IPSL <https://www.ipsl.fr/>`_ uses an `ESG-F <http://pcmdi9.llnl.gov/>`_ datanode to publish and diffuse `CMIP5 <http://cmip-pcmdi.llnl.gov/cmip5/>`_ data located on `CICLAD <http://ciclad-web.ipsl.jussieu.fr/>`_ filesystem to its private reasearch community. This datanode could be query to find specific NetCDF files, through a `web front-end <http://esgf-local.ipsl.fr/esgf-web-fe/>`_.

Based on a `THREDDS <http://www.unidata.ucar.edu/software/thredds/current/tds/>`_ server, the `CMIP5 <http://cmip-pcmdi.llnl.gov/cmip5/>`_ files are fictitiously concacenated along time dimension throught `OpenDAP <http://www.opendap.org/>`_ URL. These aggregations avoid to deal with the files splitting depending on model and frequency over a time period.

Moreover, the `IPSL <https://www.ipsl.fr/>`_ `CMIP5 <http://cmip-pcmdi.llnl.gov/cmip5/>`_ post-processing pipeline adds `CDAT <http://uvcdat.llnl.gov/>`_ aggregations  using ``cdscan`` command-line with XML format.

``find_agg`` is a command-line tool allowing you to find and list the availale `CMIP5 <http://cmip-pcmdi.llnl.gov/cmip5/>`_ aggregations at `IPSL <https://www.ipsl.fr/>`_ in a fast and researcher-friendly way. This tool includes search over `THREDDS <http://www.unidata.ucar.edu/software/thredds/current/tds/>`_ and/or XML aggregations availables at `IPSL <https://www.ipsl.fr/>`_.


Features
++++++++

**As the logical operator AND**
  The search-API from `ESG-F front-ends <http://esgf-node.ipsl.fr/esgf-web-fe/>`_ displays the results of your request using an *OR* logical operator. For example, this means you cannot select the temperature **AND** the precitation for the same model or institute. Here, ``find_agg`` follows **ALL** your requirements. All returned models satisfy your entire request.

**Quick discovery**
  ``find_agg`` builds all possible aggregations following your request and using a combinatorial algorithm. Then, all URLs are tested using multithreading.

**Includes THREDDS and/or XML aggregations search**
  You can choose to do your research on `THREDDS <http://www.unidata.ucar.edu/software/thredds/current/tds/>`_ aggregations, XML aggregations or both. At least one option ``--tds`` or ``--xml`` must be given (see :ref:`usage`).

**Intersection between both sources**
  The search on `THREDDS <http://www.unidata.ucar.edu/software/thredds/current/tds/>`_ and/or XML aggregation could give different results with two different lists of available models. You can change this default behaviour from union to intersection of results. Consequently, the returned list of models satisfies your request both for `THREDDS <http://www.unidata.ucar.edu/software/thredds/current/tds/>`_ and XML aggregations.

**Display missing data on the filesystem**
  When an aggregation test fails, you can choose to return the list of missing data on the filesystem `CMIP5 tree <http://cmip-pcmdi.llnl.gov/cmip5/docs/cmip5_data_reference_syntax.pdf>`_. This information can be easily used to build a download request through a `SYNDA template <https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/TEMPLATE>`_.

**Save the results of your research**
  To proceed on found aggregations, you can save the list of available aggregation. It is possible to specify the path of the output files or not. ``-o/--outputfile`` option stands for the aggregation list and ``-m/--missing`` option is for the list of missing data on the filesystem (see :ref:`usage`). Both options are optionnal and can be used independently of one another.

**Useful template**
  Your request can be easily formatted using the ``requierments.json`` template. You just need to know the `CMIP5 vocabulary <http://cmip-pcmdi.llnl.gov/cmip5/data_description.html>`_ to build your request in a researcher-friendly way (see :ref:`configuration`).

**Use a logfile**
  You can initiate a logger instead of the standard output. This could be useful for automatic workflows. The logfile name is automatically defined and unique (using the the job's name, the date and the job's PID). You can define an output directory for your logs too.
