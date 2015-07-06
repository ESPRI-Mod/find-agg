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
_THREDDS_ROOT = 'http://esgf-local.ipsl.fr/thredds/dodsC/cmip5.merge'

# THREDDS aggregation html file extension
_THREDDS_AGGREGATION_HTML_EXT = '1.aggregation.1.html'

# THREDDS aggregation html file extension
_XML_AGGREGATION_EXT = 'latest.xml'

# Filesystem CMIP5 root folder
_CMIP5 = '/prodigfs/esg/CMIP5/merge'

# Project
_PROJECT = 'cmip5'

# Filesystem CMIP5 xml root folder
_XML_ROOT = '/prodigfs/esg/xml/CMIP5'

# Latest file version literal
_LATEST = 'latest'

# Throttle upon number of threads to spawn
_THREAD_POOL_SIZE = 4

# Log levels
_LEVELS = {'debug': logging.error,
           'info': logging.info,
           'warning': logging.warning,
           'error': logging.error,
           'critical': logging.critical,
           'exception': logging.exception}


class _InstituteInfo(object):
    """
    Gives the list of models from an institute regarding to the DRS.

    :param str name: The institute to process
    :returns: The models from the institute
    :rtype: *list*

    """
    def __init__(self, name):
        self.name = name
        self.models = os.listdir(os.path.join(_CMIP5, name))


class _ProcessingContext(object):
    """
    Encapsulates the following processing context/information for main process:

    +--------------------+---------------+---------------------------------------+
    | Attribute          | Type          | Description                           |
    +====================+===============+=======================================+
    | *self*.ensembles   | *list*        | Ensembles from request                |
    +--------------------+---------------+---------------------------------------+
    | *self*.experiments | *list*        | Experiments from request              |
    +--------------------+---------------+---------------------------------------+
    | *self*.institute   | *str*         | Institute in process                  |
    +--------------------+---------------+---------------------------------------+
    | *self*.institutes  | *list*        | institutes from a directory           |
    +--------------------+---------------+---------------------------------------+
    | *self*.model       | *str*         | Model in process                      |
    +--------------------+---------------+---------------------------------------+
    | *self*.outputfile  | *str*         | Output list of available aggregations |
    +--------------------+---------------+---------------------------------------+
    | *self*.pool        | *pool object* | Pool of workers (from multithreading) |
    +--------------------+---------------+---------------------------------------+
    | *self*.urls        | *list*        | URLs list to call                     |
    +--------------------+---------------+---------------------------------------+
    | *self*.variables   | *list*        | Variables from request                |
    +--------------------+---------------+---------------------------------------+
    | *self*.verbose     | *boolean*     | True if verbose mode                  |
    +--------------------+---------------+---------------------------------------+
    | *self*.miss        | *boolean*     | True if output missing data           |
    +--------------------+---------------+---------------------------------------+
    | *self*.xml         | *boolean*     | True to scan XML aggregations         |
    +--------------------+---------------+---------------------------------------+
    | *self*.tds         | *boolean*     | True to scan THREDDS aggregations     |
    +--------------------+---------------+---------------------------------------+
    | *self*.inter       | *boolean*     | True to scan both aggregations types  |
    +--------------------+---------------+---------------------------------------+

    :param dict args: Parsed command-line arguments
    :returns: The processing context
    :rtype: *dict*

    """
    def __init__(self, args, requirements):
        _init_logging(args.logdir)
        self.ensembles = requirements['ensembles']
        self.experiments = requirements['experiments']
        self.institute = None
        self.institutes = map(_InstituteInfo, os.listdir(_CMIP5))
        self.model = None
        self.outputfile = args.outputfile
        self.pool = ThreadPool(_THREAD_POOL_SIZE)
        self.urls = None
        self.variables = requirements['variables']
        self.verbose = args.verbose
        self.miss = args.missing
        self.xml = args.xml
        self.tds = args.tds
        if not self.xml and not self.tds:
            raise _Exception('One of --tds or --xml options must be given')
        self.inter = args.inter
        if self.inter and not (self.xml or self.tds):
            raise _Exception('--inter option required both --tds and --xml options')


class _Exception(Exception):
    """
    When an error is encountered, logs a message with the ``ERROR`` status.

    :param str msg: Error message to log
    :returns: The logged message with the ``ERROR`` status
    :rtype: *str*

    """
    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        print
        _log('error', self.msg)


def _get_args():
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
        help="""Path of the JSON template with the requirements of the request.\n\n""")
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
        help="""Outputfile with available aggregations list\n(default is working directory).\n\n""")
    parser.add_argument(
        '-m', '--missing',
        nargs='?',
        type=str,
        const='{0}/missing_data.list'.format(os.getcwd()),
        help="""Outputfile with the list of missing data\n(default is working directory).\n\n""")
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


def _init_logging(logdir):
    """
    Initiates the logging configuration (output, message formatting). In the case of a logfile, the logfile name is unique and formatted as follows:\n
    find_agg-YYYYMMDD-HHMMSS-PID.log

    :param str logdir: The relative or absolute logfile directory. If ``None`` the standard output is used.

    """
    logging.getLogger("requests").setLevel(logging.CRITICAL)  # Disables logging message from request library
    if logdir:
        logfile = 'find_agg-{0}-{1}.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S"), os.getpid())
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logging.basicConfig(filename=os.path.join(logdir, logfile),
                            level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(message)s')


def _log(level, msg):
    """
    Points to the log level as follows:

    +-----------+-------------------+
    | Log level | Log function      |
    +===========+===================+
    | debug     | logging.error     |
    +-----------+-------------------+
    | info      | logging.info      |
    +-----------+-------------------+
    | warning   | logging.warning   |
    +-----------+-------------------+
    | error     | logging.error     |
    +-----------+-------------------+
    | critical  | logging.critical  |
    +-----------+-------------------+
    | exception | logging.exception |
    +-----------+-------------------+

    :param str level: The log level
    :param str msg: The message to log
    :returns: A pointer to the appropriate log method
    :rtype: *dict*

    """
    return _LEVELS[level](msg)


def _get_requirements(path):
    """Returns loaded configuration information."""
    try:
        return load(path)
    except:
        raise _Exception('{0} is not a valid JSON file'.format(path))


def _get_ensembles_list(ctx):
    """Returns ensembles list given an institute and model."""
    ensembles = []
    for experiment in ctx.experiments:
        for variable in ctx.variables:
            path = []
            path.append(_CMIP5)
            path.append(ctx.institute.name)
            path.append(ctx.model)
            path.append(experiment)
            path += ctx.variables[variable]
            for ensemble in ctx.ensembles:
                ensembles += [os.path.basename(p) for p in glob('/'.join(path)+'/'+ensemble)]
    return list(set(ensembles))


def _get_aggregation_urls(ctx):
    """Yields aggregation urls for processing."""
    for experiment, ensemble in product(ctx.experiments, _get_ensembles_list(ctx)):
        for variable in ctx.variables:
            url = [_THREDDS_ROOT]
            url.append(ctx.institute.name)
            url.append(ctx.model)
            url.append(experiment)
            url += ctx.variables[variable]
            url.append(ensemble)
            url.append(variable)
            url.append(_THREDDS_AGGREGATION_HTML_EXT)
            yield '.'.join(url)


def _get_aggregation_xmls(ctx):
    """Yields aggregation xmls for processing."""
    for experiment, ensemble in product(ctx.experiments, _get_ensembles_list(ctx)):
        for variable in ctx.variables:
            xml = os.path.join(_XML_ROOT, experiment)
            xml = os.path.join(xml, ctx.variables[variable][1])
            xml = os.path.join(xml, ctx.variables[variable][0])
            xml = os.path.join(xml, variable)
            xml = [os.path.join(xml, _PROJECT)]
            xml.append(ctx.model)
            xml.append(experiment)
            xml.append(ensemble)
            xml += ctx.variables[variable]
            xml.append(variable)
            xml.append(_XML_AGGREGATION_EXT)
            yield '.'.join(xml)


def _test_url(url):
    """Returns True if an aggregation url exists."""
    r = requests.head(url)
    return r.status_code == requests.codes.ok


def _test_xml(xml):
    """Returns True if an aggregation xml exists."""
    return os.path.isfile(xml)


def _all_urls_exist(ctx):
    """Returns flag indicating whether all urls exist or not."""
    urls = ctx.pool.map(_test_url, _get_aggregation_urls(ctx))
    return False if not urls else all(urls)


def _all_xmls_exist(ctx):
    """Returns flag indicating whether all urls exist or not."""
    xmls = ctx.pool.map(_test_xml, _get_aggregation_xmls(ctx))
    return False if not xmls else all(xmls)


def _write_urls(ctx):
    """Outputs set of urls."""
    _log('info', 'All THREDDS aggregations available for {0}'.format(ctx.model))
    if ctx.outputfile:
        with open(ctx.outputfile, 'a+') as f:
            for url in _get_aggregation_urls(ctx):
                f.write('{0}\n'.format(url.replace('.html', '')))


def _write_xmls(ctx):
    """Outputs set of xmls."""
    _log('info', 'All XML aggregations available for {0}'.format(ctx.model))
    if ctx.outputfile:
        with open(ctx.outputfile, 'a+') as f:
            for xml in _get_aggregation_xmls(ctx):
                f.write('{0}\n'.format(xml))


def _url2path(url):
    """Convert an aggregation url into a file path"""
    path = _CMIP5
    for element in url.split('.')[4:11]:
        path = os.path.join(path, element)
    path = os.path.join(path, _LATEST)
    path = os.path.join(path, url.split('.')[11])
    return path


def _get_missing_tree(url):
    """Return the master missing tree where the data should be."""
    path = _url2path(url)
    if not os.path.exists(path):
        while not os.path.exists(path):
            child = path
            path = os.path.dirname(path)
        return child


def _get_missing_data(ctx):
    """Returns the sorted list of missing data."""
    data = filter(lambda m: m is not None, ctx.pool.map(_get_missing_tree, _get_aggregation_urls(ctx)))
    for data in set(sorted(data)):
        if ctx.verbose:
            _log('warning', '{0} does not exist on filesystem'.format(data.replace(_CMIP5, '.')))
        if ctx.miss:
            with open(ctx.miss, 'a+') as f:
                f.write('{0}\n'.format(data))


def _get_missing_urls(ctx):
    """Returns the sorted list of missing urls."""
    urls = ifilterfalse(_test_url, _get_aggregation_urls(ctx))
    for url in set(sorted(urls)):
        if ctx.verbose:
            _log('warning', '{0} not available on THREDDS catalog'.format(os.path.splitext(os.path.basename(url))[0]))
        if ctx.miss:
            with open(ctx.miss, 'a+') as f:
                f.write('{0}\n'.format(url))


def _get_missing_xmls(ctx):
    """Returns the sorted list of missing xmls."""
    xmls = ifilterfalse(_test_xml, _get_aggregation_xmls(ctx))
    for xml in set(sorted(xmls)):
        if ctx.verbose:
            _log('warning', '{0} not available in {1}'.format(os.path.basename(xml), _XML_ROOT))
        if ctx.miss:
            with open(ctx.miss, 'a+') as f:
                f.write('{0}\n'.format(xml))


def main(ctx):
    """
    Main entry point for stand-alone call.

    """
    for ctx.institute in ctx.institutes:
        for ctx.model in ctx.institute.models:
            if ctx.inter:
                if _all_xmls_exist(ctx) and _all_urls_exist(ctx):
                    _write_urls(ctx)
                    _write_xmls(ctx)
                else:
                    _get_missing_urls(ctx)
                    _get_missing_xmls(ctx)
                    _get_missing_data(ctx)
            else:
                check_data = False
                if ctx.tds:
                    if _all_urls_exist(ctx):
                        _write_urls(ctx)
                    else:
                        _get_missing_urls(ctx)
                        check_data = True
                if ctx.xml:
                    if _all_xmls_exist(ctx):
                        _write_xmls(ctx)
                    else:
                        _get_missing_xmls(ctx)
                        check_data = True
                if check_data:
                    _get_missing_data(ctx)
    # Close thread pool
    ctx.pool.close()
    ctx.pool.join()


# Main entry point.
if __name__ == "__main__":
    # Initialise processing context
    args = _get_args()
    ctx = _ProcessingContext(args, _get_requirements(args.inputfile))
    if ctx.tds and ctx.xml:
        _log('info', '==> Starting search on {url.scheme}://{url.netloc}/ and in {0}'.format(_XML_ROOT, url=urlparse(_THREDDS_ROOT)))
    elif ctx.tds:
        _log('info', '==> Starting search on {url.scheme}://{url.netloc}/'.format(url=urlparse(_THREDDS_ROOT)))
    elif ctx.xml:
        _log('info', '==> Starting search in {0}'.format(_XML_ROOT))
    main(ctx)
    _log('info', '==> Search complete.')
