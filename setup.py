import os
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

VERSION = '0.2'

setup(
    name='Flask-JSONPages',
    version=VERSION,

    author='Mateusz Lapsa-Malawski',
    author_email='mateusz@munhitsu.com',
    url='https://github.com/munhitsu/Flask-JSONPages',

    description='Provides static pages to a Flask application based on JSON',
    long_description=open("README").read(),
    keywords=["flask","json","static"],
    license='BSD',
    platforms='any',

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],

    packages=['flask_jsonpages'],
#    namespace_packages=['flask_jsonpages'],
    include_package_data = True,
    zip_safe=False,

    install_requires=[
        'Flask',
    ],
)

