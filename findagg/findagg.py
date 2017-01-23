#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: CMIP5 aggregation discovery upon local TDS IPSL-ESGF datanode or CICLAD filesystem.

"""

# Module imports
import argparse
import logging
import os
import textwrap
from argparse import HelpFormatter
from datetime import datetime
from glob import glob
from itertools import product, ifilterfalse
from json import load
from multiprocessing.dummy import Pool as ThreadPool

import requests
from jsonschema import validate

# Program version
__version__ = 'v{0} {1}'.format('0.6.0', datetime(year=2017, month=1, day=17).strftime("%Y-%d-%m"))

# THREDDS server root url
THREDDS_ROOT = 'http://esgf-local.ipsl.upmc.fr/thredds/dodsC/cmip5.output'

# THREDDS aggregation html file extension
THREDDS_AGGREGATION_HTML_EXT = '1.aggregation.1.html'

# THREDDS aggregation html file extension
XML_AGGREGATION_EXT = '.xml'

# Filesystem CMIP5 root folder
CMIP5 = '/prodigfs/project/CMIP5/output'

# Project
PROJECT = 'cmip5'

# Filesystem CMIP5 xml root folder
XML_ROOT = '/prodigfs/project/CMIP5/output'

# Latest file version literal
LATEST = 'latest'

# Throttle upon number of threads to spawn
THREAD_POOL_SIZE = 1

# Aggregation status
COMPLETE = 'COMPLETE'
INCOMPLETE = 'INCOMPLETE'
NONE = 'NONE'


class MultilineFormatter(HelpFormatter):
    """
    Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __init__(self, prog):
        # Overload the HelpFormatter class.
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _fill_text(self, text, width, indent):
        # Rewrites the _fill_text method to support multiline description.
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text

    def _split_lines(self, text, width):
        # Rewrites the _split_lines method to support multiline helps.
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text


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
    | *self*.agg_file    | *str*         | Output file for available aggregations |
    +--------------------+---------------+----------------------------------------+
    | *self*.pool        | *pool object* | Pool of workers (from multithreading)  |
    +--------------------+---------------+----------------------------------------+
    | *self*.urls        | *list*        | URLs list to call                      |
    +--------------------+---------------+----------------------------------------+
    | *self*.variables   | *list*        | Variables from request                 |
    +--------------------+---------------+----------------------------------------+
    | *self*.verbose     | *boolean*     | True if verbose mode                   |
    +--------------------+---------------+----------------------------------------+
    | *self*.miss_file   | *boolean*     | True if output missing data            |
    +--------------------+---------------+----------------------------------------+

    :param ArgumentParser args: Parsed command-line arguments
    :returns: The processing context
    :rtype: *ProcessingContext*
    :raises Error: If no ``--tds`` or ``--xml`` flag is set
    :raises Error: If the ``--inter`` option is set without both of ``--tds`` and ``--xml`` flags

    """

    def __init__(self, args, requirements):
        init_logging(args.log)
        self.ensembles = requirements['ensembles']
        self.experiments = requirements['experiments']
        self.institute = None
        self.institutes = map(InstituteInfo, os.listdir(CMIP5))
        self.model = None
        self.agg_file = args.agg
        self.pool = ThreadPool(THREAD_POOL_SIZE)
        self.urls = None
        self.variables = requirements['variables']
        self.verbose = args.v
        self.miss_file = args.miss


def get_args():
    """
    Returns parsed command-line arguments. See ``find_agg -h`` for full description.

    :returns: The corresponding ``argparse`` Namespace
    :rtype: *ArgumentParser*

    """
    parser = argparse.ArgumentParser(
        prog='find_agg',
        description="""
        Find CMIP5 aggregations according to requirements|n
        upon local IPSL-ESGF datanode (THREDDS server) or into CICLAD filesystem.|n|n

        The default values are displayed next to the corresponding flags.|n|n

        See full documentation and references on http://prodiguer.github.io/find-agg/.
        """,
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog="""
        Developed by:|n
        Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)|n
        Greenslade, M., (UPMC/IPSL - momipsl@ipsl.jussieu.fr)
        """)
    parser.add_argument(
        'inputfile',
        nargs='?',
        type=argparse.FileType('r'),
        help="""Path of the JSON template with the requirements of the request.""")
    parser.add_argument(
        '--agg',
        nargs='?',
        metavar='$PWD/aggregations.list',
        type=str,
        const='{0}/aggregations.list'.format(os.getcwd()),
        help="""
        Output file with available aggregations list.""")
    parser.add_argument(
        '--miss',
        nargs='?',
        metavar='$PWD/missing_data.list',
        type=str,
        const='{0}/missing_data.list'.format(os.getcwd()),
        help="""Output file with the list of missing data.""")
    parser.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        nargs='?',
        const=os.getcwd(),
        help="""
        Logfile directory.|n
        An existing logfile can be submitted.|n
        If not, standard output is used.
        """)
    parser.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    parser.add_argument(
        '-h', '--help',
        action='help',
        help="""Show this help message and exit.""")
    parser.add_argument(
        '-V',
        action='version',
        version='%(prog)s ({0})'.format(__version__),
        help="""Program version""")
    return parser.parse_args()


def init_logging(log, level='INFO'):
    """
    Initiates the logging configuration (output, date/message formatting).
    If a directory is submitted the logfile name is unique and formatted as follows:
    ``name-YYYYMMDD-HHMMSS-JOBID.log``If ``None`` the standard output is used.

    :param str log: The logfile name or directory.
    :param str level: The log level.

    """
    log_fmt = '%(asctime)s %(levelname)s %(message)s'
    log_date_fmt = '%Y/%m/%d %I:%M:%S %p'
    log_levels = {'CRITICAL': logging.CRITICAL,
                  'ERROR': logging.ERROR,
                  'WARNING': logging.WARNING,
                  'INFO': logging.INFO,
                  'DEBUG': logging.DEBUG,
                  'NOTSET': logging.NOTSET}
    logging.getLogger("requests").setLevel(logging.CRITICAL)  # Disables logging message from request library
    if log:
        if os.path.isfile(log):
            logging.basicConfig(filename=log,
                                level=log_levels[level],
                                format=log_fmt,
                                datefmt=log_date_fmt)
        else:
            logfile = 'findagg-{0}-{1}.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S"),
                                                   os.getpid())
            if not os.path.isdir(log):
                os.makedirs(log)
            logging.basicConfig(filename=os.path.join(log, logfile),
                                level=log_levels[level],
                                format=log_fmt,
                                datefmt=log_date_fmt)
    else:
        logging.basicConfig(level=log_levels[level],
                            format=log_fmt,
                            datefmt=log_date_fmt)


def get_requirements(path):
    """
    Loads the requirements from the JSON template.

    :param str path: The path of the JSON file with requirements
    :returns: The user requirements
    :rtype: *json*
    :raises Error: If the JSON file parsing fails

    """
    try:
        return validate_requirements(load(path))
    except:
        raise Exception('{0} is not a valid JSON file'.format(path))


def validate_requirements(json):
    """
    Validate the requirements against the JSON schema.

    :param json json: The JSON data to validate
    :returns: The validated JSON data
    :rtype: *json*
    :raises Error: If the JSON file is invalid

    """
    with open('{0}/template.json'.format(os.path.dirname(os.path.abspath(__file__)))) as f:
        schema = load(f)
    try:
        validate(json, schema)
        return json
    except:
        raise Exception('Requirements have invalid format')


def get_ensembles_list(ctx):
    """
    Returns the ensembles list given an institute and a model.

    :param ProcessingContext ctx: The processing context
    :returns: The ensembles list without duplicates
    :rtype: *list*

    """
    ensembles = []
    for experiment in ctx.experiments:
        for variable in ctx.variables:
            path = list()
            path.append(CMIP5)
            path.append(ctx.institute.name)
            path.append(ctx.model)
            path.append(experiment)
            path += ctx.variables[variable]
            for ensemble in ctx.ensembles:
                ensembles += [os.path.basename(p) for p in glob('/'.join(path) + '/' + ensemble)]
    return list(set(ensembles))


def get_aggregation_urls(ctx):
    """
    Yields the aggregations urls for testing.

    :param ProcessingContext ctx: The processing context
    :returns: An iterator on rebuild urls
    :rtype: *iter*

    """
    for experiment, ensemble in product(ctx.experiments, get_ensembles_list(ctx)):
        for variable in ctx.variables:
            url = [THREDDS_ROOT, ctx.institute.name, ctx.model, experiment]
            url += ctx.variables[variable]
            url.append(ensemble)
            url.append(variable)
            url.append(THREDDS_AGGREGATION_HTML_EXT)
            yield '.'.join(url)


def get_aggregation_xmls(ctx):
    """
    Like :func:`get_aggregation_urls`, but returns an iterator on rebuild xml paths.

    :param ProcessingContext ctx: The processing context
    :returns: An iterator on rebuild xml paths
    :rtype: *iter*

    """
    for experiment, ensemble in product(ctx.experiments, get_ensembles_list(ctx)):
        for variable in ctx.variables:
            xml_dir = [XML_ROOT, ctx.institute.name, ctx.model, experiment]
            xml_dir += ctx.variables[variable]
            xml_dir.append(ensemble)
            xml_dir.append(LATEST)
            xml_dir.append(variable)
            xml_dir = os.path.join(*xml_dir)
            xml_name = [variable, ctx.variables[variable][2], ctx.model, experiment, ensemble]
            xml_name = '{0}{1}'.format('_'.join(xml_name), XML_AGGREGATION_EXT)
            yield os.path.join(xml_dir, xml_name)


def test_url(url):
    """
    Tests an url response.

    :param str url: The url to test
    :returns: True if the aggregation url exists
    :rtype: *boolean*
    :raises Error: If an HTTP request fails

    """
    try:
        r = requests.head(url, timeout=1)
        return r.status_code == requests.codes.ok
    except:
        return False


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

    :param ProcessingContext ctx: The processing context
    :returns: True if all aggregation urls exist
    :rtype: *boolean*

    """
    urls = ctx.pool.map(test_url, get_aggregation_urls(ctx))
    if not any(urls):
        return NONE
    elif all(urls):
        return COMPLETE
    else:
        return INCOMPLETE


def all_xmls_exist(ctx):
    """
    Like :func:`all_urls_exist`, but returns a flag indicating whether all xml paths exist or not.

    :param ProcessingContext ctx: The processing context
    :returns: True if all xml aggregation exist
    :rtype: *boolean*

    """
    xmls = ctx.pool.map(test_xml, get_aggregation_xmls(ctx))
    if not any(xmls):
        return NONE
    elif all(xmls):
        return COMPLETE
    else:
        return INCOMPLETE


def write_urls(ctx):
    """
    Writes all available aggregations into output file.

    :param ProcessingContext ctx: The processing context

    """
    if ctx.agg_file:
        with open(ctx.agg_file, 'a+') as f:
            for url in get_aggregation_urls(ctx):
                f.write('{0}\n'.format(url.replace('.html', '')))


def write_xmls(ctx):
    """
    Like :func:`write_urls`, but writes available xml paths into the output file.

    :param ProcessingContext ctx: The processing context

    """
    if ctx.agg_file:
        with open(ctx.agg_file, 'a+') as f:
            for xml in get_aggregation_xmls(ctx):
                f.write('{0}\n'.format(xml))


def url2path(url):
    """
    Converts an aggregation url into a file path.

    :param str url: The url to convert
    :returns: The corresponding path on filesystem
    :rtype: *str*

    """
    path = [CMIP5]
    path.extend(url.split('.')[5:12])
    path.append(LATEST)
    path.append(url.split('.')[12])
    return os.path.join(*path)


def get_missing_tree(url):
    """
    Returns the master missing tree where the data should be.

    :param str url: The url to convert using :func:`url2path`
    :returns: The child tree where data should be on the filesystem
    :rtype: *str*

    """
    path = url2path(url)
    if not os.path.exists(path):
        child = path
        while not os.path.exists(path):
            child = path
            path = os.path.dirname(path)
        return child


def get_missing_data(ctx):
    """
    Writes the sorted list of missing data.

    :param ProcessingContext ctx: The processing context

    """
    data = filter(lambda m: m is not None, ctx.pool.map(get_missing_tree, get_aggregation_urls(ctx)))
    for data in set(sorted(data)):
        if ctx.miss_file:
            with open(ctx.miss_file, 'a+') as f:
                f.write('{0}\n'.format(data))


def get_missing_urls(ctx):
    """
    Like :func:`get_missing_data`, but writes the sorted list of missing aggregations urls.

    :param ProcessingContext ctx: The processing context

    """
    urls = ifilterfalse(test_url, get_aggregation_urls(ctx))
    for url in set(sorted(urls)):
        if ctx.miss_file:
            with open(ctx.miss_file, 'a+') as f:
                f.write('{0}\n'.format(url))


def get_missing_xmls(ctx):
    """
    Like :func:`get_missing_urls`, but writes the sorted list of missing xml paths.

    :param ProcessingContext ctx: The processing context

    """
    xmls = ifilterfalse(test_xml, get_aggregation_xmls(ctx))
    for xml in set(sorted(xmls)):
        if ctx.miss_file:
            with open(ctx.miss_file, 'a+') as f:
                f.write('{0}\n'.format(xml))


def main():
    """
    Main process that\:
     * Instantiates processing context,
     * Tests all THREDDS aggregations URL,
     * Tests all XML aggregations paths,
     * Checks if data exist when aggregation is missing,
     * Prints or logs the search results.

    """
    # Initialise processing context
    args = get_args()
    ctx = ProcessingContext(args, get_requirements(args.inputfile))
    logging.info('==> Searching for aggregations...')
    logging.info('+{0}+'.format('-'.center(52, '-')))
    logging.info('|{0}|{1}|{2}|'.format('MODEL'.center(20), 'OpenDAP'.center(15), 'CDAT'.center(15)))
    logging.info('+{0}+'.format('='.center(52, '=')))
    for ctx.institute in ctx.institutes:
        for ctx.model in ctx.institute.models:
            xmls_status = all_xmls_exist(ctx)
            urls_status = all_urls_exist(ctx)
            logging.info('| {0}| {1}| {2}|'.format(ctx.model.ljust(19), urls_status.ljust(14), xmls_status.ljust(14)))
            if urls_status is COMPLETE:
                write_urls(ctx)
            else:
                get_missing_urls(ctx)
            if xmls_status is COMPLETE:
                write_xmls(ctx)
            else:
                get_missing_xmls(ctx)
            if urls_status is not COMPLETE or xmls_status is not COMPLETE:
                get_missing_data(ctx)
    # Close thread pool
    ctx.pool.close()
    ctx.pool.join()
    logging.info('+{0}+'.format('-'.center(52, '-')))
    logging.info('==> Search complete.')


# Main entry point for stand-alone call.
if __name__ == "__main__":
    main()
