"""
Script usado para la configuracion e instalacion del paquete
"""

from setuptools import find_packages, setup


with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(name='cdslib',
      version='0.1.0',
      maintainer='Developers of the CDS team of FEnFiSDi group',
      maintainer_email='camilo.hincapie@udea.edu.co',
      description='Library for contagious diseases simulation',
      long_description=long_description,
      url='https://github.com/fenfisdi/cdslib',
      author='Camilo Hincapié Gutiérrez',
      author_email='camilo.hincapie@udea.edu.co',
      license='GNU General Public License v3 (GPLv3)',
      classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: CDSLib',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries'
      ],
      test_suite='pytest',
      packages=find_packages(exclude='__pycache__'),
      keywords=['Complex Systems', 'Computation', 'Epidemiology',
                'Nonlinear dynamics'],
      python_requires='>=3.5',
      install_requires=['numpy', 'pandas>=1.1.1', 'plotly>=4.10.0', 'scipy'],
      zip_safe=False)
