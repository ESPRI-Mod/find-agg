#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: CMIP5 aggregation discovery upon local TDS IPSL-ESGF datanode or CICLAD filesystem.

"""

# Module imports
import os
import argparse
import requests
import logging
from argparse import RawTextHelpFormatter
from glob import glob
from itertools import product, ifilterfalse
from json import load
from urlparse import urlparse
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool


# Program version
__version__ = '{0} {1}-{2}-{3}'.format('v0.5', '2015', '07', '06')

# THREDDS server root url
THREDDS_ROOT = 'http://esgf-local.ipsl.fr/thredds/dodsC/cmip5.merge'

# THREDDS aggregation html file extension
THREDDS_AGGREGATION_HTML_EXT = '1.aggregation.1.html'

# THREDDS aggregation html file extension
XML_AGGREGATION_EXT = 'latest.xml'

# Filesystem CMIP5 root folder
CMIP5 = '/prodigfs/esg/CMIP5/merge'

# Project
PROJECT = 'cmip5'

# Filesystem CMIP5 xml root folder
XML_ROOT = '/prodigfs/esg/xml/CMIP5'

# Latest file version literal
LATEST = 'latest'

# Throttle upon number of threads to spawn
THREAD_POOL_SIZE = 4


class InstituteInfo(object):
    """
    Gives the list of models from an institute regarding to the DRS.

    :param str name: The institute to process
    :returns: The models from the institute
    :rtype: *list*

    """
    def __init__(self, name):
        self.name = name
        self.models = os.listdir(os.path.join(CMIP5, name))


class ProcessingContext(object):
    """
    Encapsulates the following processing context/information for main process:

    +--------------------+---------------+----------------------------------------+
    | Attribute          | Type          | Description                            |
    +====================+===============+========================================+
    | *self*.ensembles   | *list*        | Ensembles from request                 |
    +--------------------+---------------+----------------------------------------+
    | *self*.experiments | *list*        | Experiments from request               |
    +--------------------+---------------+----------------------------------------+
    | *self*.institute   | *str*         | Institute in process                   |
    +--------------------+---------------+----------------------------------------+
    | *self*.institutes  | *list*        | institutes from a directory            |
    +--------------------+---------------+----------------------------------------+
    | *self*.model       | *str*         | Model in process                       |
    +--------------------+---------------+----------------------------------------+
    | *self*.outputfile  | *str*         | Output file for available aggregations |
    +--------------------+---------------+----------------------------------------+
    | *self*.pool        | *pool object* | Pool of workers (from multithreading)  |
    +--------------------+---------------+----------------------------------------+
    | *self*.urls        | *list*        | URLs list to call                      |
    +--------------------+---------------+----------------------------------------+
    | *self*.variables   | *list*        | Variables from request                 |
    +--------------------+---------------+----------------------------------------+
    | *self*.verbose     | *boolean*     | True if verbose mode                   |
    +--------------------+---------------+----------------------------------------+
    | *self*.miss        | *boolean*     | True if output missing data            |
    +--------------------+---------------+----------------------------------------+
    | *self*.xml         | *boolean*     | True to scan XML aggregations          |
    +--------------------+---------------+----------------------------------------+
    | *self*.tds         | *boolean*     | True to scan THREDDS aggregations      |
    +--------------------+---------------+----------------------------------------+
    | *self*.inter       | *boolean*     | True to scan both aggregations types   |
    +--------------------+---------------+----------------------------------------+

    :param dict args: Parsed command-line arguments
    :returns: The processing context
    :rtype: *dict*
    :raises Error: If no ``--tds`` or ``--xml`` flag is set
    :raises Error: If the ``--inter`` option is set without both of ``--tds`` and ``--xml`` flags

    """
    def __init__(self, args, requirements):
        init_logging(args.logdir)
        self.ensembles = requirements['ensembles']
        self.experiments = requirements['experiments']
        self.institute = None
        self.institutes = map(InstituteInfo, os.listdir(CMIP5))
        self.model = None
        self.outputfile = args.outputfile
        self.pool = ThreadPool(THREAD_POOL_SIZE)
        self.urls = None
        self.variables = requirements['variables']
        self.verbose = args.verbose
        self.miss = args.missing
        self.xml = args.xml
        self.tds = args.tds
        if not self.xml and not self.tds:
            raise Exception('One of --tds or --xml options must be given')
        self.inter = args.inter
        if self.inter and not (self.xml and self.tds):
            raise Exception('--inter option required both --tds and --xml options')


def get_args():
    """
    Returns parsed command-line arguments. See ``find_agg -h`` for full description.

    """
    parser = argparse.ArgumentParser(
        description="""Find CMIP5 aggregations according to requirements\nupon local IPSL-ESGF datanode (THREDDS server) or into CICLAD filesystem.""",
        formatter_class=RawTextHelpFormatter,
        add_help=False,
        epilog="""Developed by Levavasseur, G., and Greenslade, M., (CNRS/IPSL)""")
    parser.add_argument(
        'inputfile',
        nargs='?',
        type=argparse.FileType('r'),
        help="""Path of the JSON template with the requirements of the request\n(a template can be found in {0}/requirements.json).\n\n""".format(os.path.dirname(os.path.abspath(__file__))))
    parser.add_argument(
        '-h', '--help',
        action="help",
        help="""Show this help message and exit.\n\n""")
    parser.add_argument(
        '--tds',
        action='store_true',
        default=False,
        help="""Search THREDDS aggregations from ESG-F local node.\n\n""")
    parser.add_argument(
        '--xml',
        action='store_true',
        default=False,
        help="""Search XML aggregations from CDAT (cdscan).\n\n""")
    parser.add_argument(
        '-i', '--inter',
        action='store_true',
        default=False,
        help="""Intersection between XML and THREDDS aggregations results\n(required --xml and --tds, default is union of results).\n\n""")
    parser.add_argument(
        '-o', '--outputfile',
        nargs='?',
        type=str,
        const='{0}/aggregations.list'.format(os.getcwd()),
        help="""Outputfile with available aggregations list\n(default is '{0}/aggregations.list').\n\n""".format(os.getcwd()))
    parser.add_argument(
        '-m', '--missing',
        nargs='?',
        type=str,
        const='{0}/missing_data.list'.format(os.getcwd()),
        help="""Outputfile with the list of missing data\n(default is '{0}/missing_data.list').\n\n""".format(os.getcwd()))
    parser.add_argument(
        '-l', '--logdir',
        type=str,
        nargs='?',
        const=os.getcwd(),
        help="""Logfile directory (default is working directory).\nIf not, standard output is used.\n\n""")
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        default=False,
        help="""Shows missing data\n(default only shows available models).\n\n""")
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(prog)s ({0})'.format(__version__),
        help="""Program version""")
    return parser.parse_args()


def init_logging(logdir):
    """
    Initiates the logging configuration (output, message formatting). In the case of a logfile, the logfile name is unique and formatted as follows:
    name-YYYYMMDD-HHMMSS-PID.log

    :param str logdir: The relative or absolute logfile directory. If ``None`` the standard output is used.

    """
    logging.getLogger("requests").setLevel(logging.CRITICAL)  # Disables logging message from request library
    if logdir:
        name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
        logfile = '{0}-{1}-{2}.log'.format(name, datetime.now().strftime("%Y%m%d-%H%M%S"), os.getpid())
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logging.basicConfig(filename=os.path.join(logdir, logfile),
                            level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(message)s')


def get_requirements(path):
    """
    Loads the requierements from the JSON template.

    :param str path: The path of the JSON file with requirements
    :returns: The configuration information
    :rtype: *dict*
    :raises Error: If the JSON file parsing fails

    """
    try:
        return load(path)
    except:
        raise Exception('{0} is not a valid JSON file'.format(path))


def get_ensembles_list(ctx):
    """
    Returns the ensembles list given an institute and a model.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)
    :returns: The ensembles list without duplicates
    :rtype: *list*

    """
    ensembles = []
    for experiment in ctx.experiments:
        for variable in ctx.variables:
            path = []
            path.append(CMIP5)
            path.append(ctx.institute.name)
            path.append(ctx.model)
            path.append(experiment)
            path += ctx.variables[variable]
            for ensemble in ctx.ensembles:
                ensembles += [os.path.basename(p) for p in glob('/'.join(path)+'/'+ensemble)]
    return list(set(ensembles))


def get_aggregation_urls(ctx):
    """
    Yields the aggregations urls for testing.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)
    :returns: An iterator on rebuild urls
    :rtype: *iter*

    """
    for experiment, ensemble in product(ctx.experiments, get_ensembles_list(ctx)):
        for variable in ctx.variables:
            url = [THREDDS_ROOT]
            url.append(ctx.institute.name)
            url.append(ctx.model)
            url.append(experiment)
            url += ctx.variables[variable]
            url.append(ensemble)
            url.append(variable)
            url.append(THREDDS_AGGREGATION_HTML_EXT)
            yield '.'.join(url)


def get_aggregation_xmls(ctx):
    """
    Like :func:`get_aggregation_urls`, but returns an iterator on rebuild xml paths.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)
    :returns: An iterator on rebuild xml paths
    :rtype: *iter*

    """
    for experiment, ensemble in product(ctx.experiments, get_ensembles_list(ctx)):
        for variable in ctx.variables:
            xml = os.path.join(XML_ROOT, experiment)
            xml = os.path.join(xml, ctx.variables[variable][1])
            xml = os.path.join(xml, ctx.variables[variable][0])
            xml = os.path.join(xml, variable)
            xml = [os.path.join(xml, PROJECT)]
            xml.append(ctx.model)
            xml.append(experiment)
            xml.append(ensemble)
            xml += ctx.variables[variable]
            xml.append(variable)
            xml.append(XML_AGGREGATION_EXT)
            yield '.'.join(xml)


def test_url(url):
    """
    Tests an url response.

    :param str url: The url to test
    :returns: True if the aggregation url exists
    :rtype: *boolean*
    :raises Error: If an HTTP request fails

    """
    try:
        r = requests.head(url)
        return r.status_code == requests.codes.ok
    except:
        logging.exception('An URL test fails:')


def test_xml(xml):
    """
    Like :func:`test_url`, but tests if an xml path exists.

    :param str xml: The xml path to test
    :returns: True if the xml aggregation exists
    :rtype: *boolean*

    """
    return os.path.isfile(xml)


def all_urls_exist(ctx):
    """
    Returns a flag indicating whether all urls exist or not.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)
    :returns: True if all aggregation urls exist
    :rtype: *boolean*

    """
    urls = ctx.pool.map(test_url, get_aggregation_urls(ctx))
    return False if not urls else all(urls)


def all_xmls_exist(ctx):
    """
    Like :func:`all_urls_exist`, but returns a flag indicating whether all xml paths exist or not.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)
    :returns: True if all xml aggregation exist
    :rtype: *boolean*

    """
    xmls = ctx.pool.map(test_xml, get_aggregation_xmls(ctx))
    return False if not xmls else all(xmls)


def write_urls(ctx):
    """
    Writes all available aggregations into output file.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)

    """
    logging.info('All THREDDS aggregations available for {0}'.format(ctx.model))
    if ctx.outputfile:
        with open(ctx.outputfile, 'a+') as f:
            for url in get_aggregation_urls(ctx):
                f.write('{0}\n'.format(url.replace('.html', '')))


def write_xmls(ctx):
    """
    Like :func:`write_urls`, but writes available xml paths into the output file.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)

    """
    logging.info('All XML aggregations available for {0}'.format(ctx.model))
    if ctx.outputfile:
        with open(ctx.outputfile, 'a+') as f:
            for xml in get_aggregation_xmls(ctx):
                f.write('{0}\n'.format(xml))


def url2path(url):
    """
    Converts an aggregation url into a file path.

    :param str url: The url to convert
    :returns: The corresponding path on filesystem
    :rtype: *str*

    """
    path = CMIP5
    for element in url.split('.')[4:11]:
        path = os.path.join(path, element)
    path = os.path.join(path, LATEST)
    path = os.path.join(path, url.split('.')[11])
    return path


def get_missing_tree(url):
    """
    Returns the master missing tree where the data should be.

    :param str url: The url to convert using :func:`url2path`
    :returns: The child tree where data should be on the filesystem
    :rtype: *str*

    """
    path = url2path(url)
    if not os.path.exists(path):
        while not os.path.exists(path):
            child = path
            path = os.path.dirname(path)
        return child


def get_missing_data(ctx):
    """
    Writes the sorted list of missing data.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)

    """
    data = filter(lambda m: m is not None, ctx.pool.map(get_missing_tree, get_aggregation_urls(ctx)))
    for data in set(sorted(data)):
        if ctx.verbose:
            logging.warning('{0} does not exist on filesystem'.format(data.replace(CMIP5, '.')))
        if ctx.miss:
            with open(ctx.miss, 'a+') as f:
                f.write('{0}\n'.format(data))


def get_missing_urls(ctx):
    """
    Like :func:`get_missing_data`, but writes the sorted list of missing aggregations urls.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)

    """
    urls = ifilterfalse(test_url, get_aggregation_urls(ctx))
    for url in set(sorted(urls)):
        if ctx.verbose:
            logging.warning('{0} not available on THREDDS catalog'.format(os.path.splitext(os.path.basename(url))[0]))
        if ctx.miss:
            with open(ctx.miss, 'a+') as f:
                f.write('{0}\n'.format(url))


def get_missing_xmls(ctx):
    """
    Like :func:`get_missing_urls`, but writes the sorted list of missing xml paths.

    :param dict ctx: The processing context (as a :func:`ProcessingContext` class instance)

    """
    xmls = ifilterfalse(test_xml, get_aggregation_xmls(ctx))
    for xml in set(sorted(xmls)):
        if ctx.verbose:
            logging.warning('{0} not available in {1}'.format(os.path.basename(xml), XML_ROOT))
        if ctx.miss:
            with open(ctx.miss, 'a+') as f:
                f.write('{0}\n'.format(xml))


def main():
    """
    Main process that\:
     * Instanciates processing context,
     * Tests all THREDDS aggregations URL,
     * Tests all XML aggregations paths,
     * Checks if data exist when aggregation is missing,
     * Prints or logs the search results.

    """
    # Initialise processing context
    args = get_args()
    ctx = ProcessingContext(args, get_requirements(args.inputfile))
    if ctx.tds and ctx.xml:
        logging.info('==> Starting search on {url.scheme}://{url.netloc}/ and in {0}'.format(XML_ROOT, url=urlparse(THREDDS_ROOT)))
    elif ctx.tds:
        logging.info('==> Starting search on {url.scheme}://{url.netloc}/'.format(url=urlparse(THREDDS_ROOT)))
    elif ctx.xml:
        logging.info('==> Starting search in {0}'.format(XML_ROOT))
    for ctx.institute in ctx.institutes:
        for ctx.model in ctx.institute.models:
            if ctx.inter:
                if all_xmls_exist(ctx) and all_urls_exist(ctx):
                    write_urls(ctx)
                    write_xmls(ctx)
                else:
                    get_missing_urls(ctx)
                    get_missing_xmls(ctx)
                    get_missing_data(ctx)
            else:
                check_data = False
                if ctx.tds:
                    if all_urls_exist(ctx):
                        write_urls(ctx)
                    else:
                        get_missing_urls(ctx)
                        check_data = True
                if ctx.xml:
                    if all_xmls_exist(ctx):
                        write_xmls(ctx)
                    else:
                        get_missing_xmls(ctx)
                        check_data = True
                if check_data:
                    get_missing_data(ctx)
    # Close thread pool
    ctx.pool.close()
    ctx.pool.join()
    logging.info('==> Search complete.')


# Main entry point for stand-alone call.
if __name__ == "__main__":
    main()
