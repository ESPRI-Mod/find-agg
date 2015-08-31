.. _installation:

************
Installation
************

Usual PIP installation 
++++++++++++++++++++++

.. code-block:: bash

  pip install findagg

PIP installation from GitHub
++++++++++++++++++++++++++++

.. code-block:: bash

  pip install -e git://github.com/Prodiguer/cmip5-find-agg.git@master#egg=findagg

Installation from GitHub
++++++++++++++++++++++++

1. Create a new directory:

.. code-block:: bash

  mkdir findagg
  cd findagg

2. Clone `our GitHub project <https://github.com/Prodiguer/cmip5-find-agg>`_:

.. code-block:: bash

  git init
  git clone git@github.com:Prodiguer/cmip5-find-agg.git

3. Run the ``setup.py``:

.. code-block:: bash

  python setup.py install

4. The ``find_agg`` command-line is ready.


.. warning:: To run ``find_agg`` you have to be logged on `CICLAD cluster <http://ciclad-web.ipsl.jussieu.fr/>`_.

Dependencies
++++++++++++

``find_agg`` uses the following basic Python libraries includes in Python 2.5+. Becareful your Python environment includes:

 * `os <https://docs.python.org/2/library/os.html>`_, `glob <https://docs.python.org/2/library/glob.html>`_, `logging <https://docs.python.org/2/library/logging.html>`_
 * `argparse <https://docs.python.org/2/library/argparse.html>`_
 * `itertools <https://docs.python.org/2/library/itertools.html>`_
 * `json <https://docs.python.org/2/library/json.html>`_
 * `urlparse <https://docs.python.org/2/library/urlparse.html>`_
 * `datetime <https://docs.python.org/2/library/datetime.html>`_
 * `multiprocessing <https://docs.python.org/2/library/multiprocessing.html>`_

Please install the ``requests`` library not inclued in most Python distributions using the usual PIP command-line:

.. code-block:: bash

   pip install requests

or download and intall the `sources from PyPi <https://pypi.python.org/pypi/requests>`_:

.. code-block:: bash

  wget https://pypi.python.org/packages/source/r/requests/requests-2.7.0.tar.gz#md5=29b173fd5fa572ec0764d1fd7b527260
  tar -xzvf requests-2.7.0.tar.gz 
  cd requests-2.7.0/
  python setup.py install


