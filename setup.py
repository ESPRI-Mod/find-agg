from setuptools import setup, find_packages

setup(name='findagg',
      version='0.6.0',
      description='CMIP5 aggregation discovery upon local TDS IPSL-ESGF datanode or CICLAD filesystem.',
      author='Levavasseur Guillaume',
      author_email='glipsl@ipsl.jussieu.fr',
      url='https://github.com/Prodiguer/cmip5-find-agg',
      packages=find_packages(),
      include_package_data=True,
      plateforms=['Unix'],
      install_requires=['requests>=2.7.0',
                        'jsonschema>=2.5.1'],
      entry_points={'console_scripts': ['find_agg=findagg.findagg:main']},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: System Administrators',
                   'Natural Language :: English',
                   'Operating System :: Unix',
                   'Programming Language :: Python :: 2.5',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Software Development :: Build Tools']
      )
