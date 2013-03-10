#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup Script
"""


import os
from distutils.core import setup
from distutils.core import Extension

from tupan import version
from tupan.lib import cffi_wrap

try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except:
    cmdclass = {}


package_data = {}
package_data['tupan.analysis'] = [os.path.join('textures', '*.png')]
package_data['tupan.lib'] = [os.path.join('src', '*.c'),
                               os.path.join('src', '*.h'),
                               os.path.join('src', '*.cl')]


long_description = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()


classifiers = """
Development Status :: 1 - Planning
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Programming Language :: C
Programming Language :: Python
Topic :: Scientific/Engineering
"""


setup(
    name='Tupan',
    version=version.VERSION,
    author='Guilherme G. Ferrari',
    author_email='gg.ferrari@gmail.com',
    description="A Python Toolkit for Astrophysical N-Body Simulations.",
    packages=['tupan',
              'tupan.analysis',
              'tupan.ics',
              'tupan.integrator',
              'tupan.io',
              'tupan.lib',
              'tupan.lib.utils',
              'tupan.particles',
              'tupan.tests',
             ],
    ext_modules=cffi_wrap.get_extensions(),
    package_data=package_data,
    scripts=['bin/tupan'],
    url='http://github.com/GuilhermeFerrari/Tupan',
    cmdclass=cmdclass,
    license='MIT License',
    long_description=long_description,
    classifiers=[c for c in classifiers.split('\n') if c],
)


########## end of file ##########
