# Copyright (C) 2021, Camilo Hincapié Gutiérrez
# This file is part of CDSLIB.
#
# CDSLIB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CDSLIB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#
#This package is authored by:
#Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
#Ian Mejía (https://github.com/IanMejia)
#Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
#Nicole Rivera (https://github.com/nicolerivera1)
#Carolina Rojas Duque (https://github.com/carolinarojasd)
#and the conceptual contributions about epidemiology of
#Lina Marcela Ruiz Galvis (mailto:lina.ruiz2@udea.edu.co).
#
#Other remarkably contributors to this work were
#Alejandro Campillo (https://www.linkedin.com/in/alucardcampillo/)
#Daniel Alfonso Montoya (https://www.linkedin.com/in/daniel-montoya-ds/).


from setuptools import find_packages, setup


with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='cdslib_agents',
    version='0.0.2',
    maintainer='Developers of the CDS team of FEnFiSDi group',
    maintainer_email='grupofenfisdi@udea.edu.co',
    description='Contagious diseases simulation using Agent-Based Models',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fenfisdi/cdslib_agents',
    author='Camilo Hincapié Gutiérrez',
    author_email='camilo.hincapie@udea.edu.co',
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries'
        ],
    test_suite='pytest',
    packages=find_packages(exclude='__pycache__'),
    keywords=[
        'Complex Systems',
        'Computation',
        'Epidemiology',
        'Nonlinear dynamics',
        'Agent Based Models'
        ],
    python_requires='>=3.9',
    install_requires=[
        'numpy>=1.20.2',
        'scipy>=1.6.3',
        'pandas>=1.2.4',
        'scikit-learn>=0.24.2',
        'pydantic>=1.8.2',
        'munch>=2.5.0'
        ],
    setup_requires=['wheel'],
    zip_safe=False
    )
