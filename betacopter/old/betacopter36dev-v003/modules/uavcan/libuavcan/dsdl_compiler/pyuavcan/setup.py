#!/usr/bin/env python

from distutils.core import setup

args = dict(
    name='uavcan',
    version='0.1',
    description='UAVCAN for Python',
    packages=['uavcan', 'uavcan.dsdl', 'uavcan.services', 'uavcan.monitors'],
    author='Pavel Kirienko',
    author_email='pavel.kirienko@gmail.com',
    url='http://uavcan.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=''
)

setup(**args)
