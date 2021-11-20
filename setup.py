from setuptools import find_packages, setup


with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='cdslib_agents',
    version='0.0.1a2',
    maintainer='Developers of the CDS team of FEnFiSDi group',
    maintainer_email='grupofenfisdi@udea.edu.co',
    description='Contagious diseases simulation using Agent-Based Models',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fenfisdi/cdslib_agents',
    author='Camilo Hincapie Gutierrez',
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
