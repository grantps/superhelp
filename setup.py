from setuptools import setup, find_packages  # @UnresolvedImport
from codecs import open
from os import path

__version__ = '1.0.10'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='superhelp',
    version=__version__,
    description='SuperHELP - Help for Humans!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/grantps/superhelp',
    license='MIT',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Developers',
      'Intended Audience :: Information Technology',
      'Intended Audience :: End Users/Desktop',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3.9',
      'Operating System :: OS Independent',
      'Topic :: Education',
      'Topic :: Software Development :: Testing',
      'Topic :: Education :: Computer Aided Instruction (CAI)',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Grant Paton-Simpson',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='grant@p-s.co.nz',
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': [
            'shelp=superhelp:shelp',  ## using argparse to allow arguments
        ]
    },
)
