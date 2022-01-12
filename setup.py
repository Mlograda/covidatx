
from distutils.core import setup

setup(
    name='covidatx',         # How you named your package folder (MyLib)
    packages=['covidatx'],   # Chose the same as "name"
    version='0.1.7',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='MIT',
    # Give a short description about your library
    description="provides a class to retrieve data from the UK government's API, and 24 plotting functions to visualize the data.",
    # Type in your name
    author='G McMullen-Klein, M Lograda, TJG Lassale, JG Tignol',
    author_email='logradamadjda@gmail.com',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://github.com/Mlograda/covidatx',
    # I explain this later on
    download_url='https://github.com/Mlograda/covidatx/archive/refs/tags/v0.1.7.tar.gz',
    # Keywords that define your package best
    keywords=['Covid19', 'Data visualization'],
    include_package_data=True,
    package_data={'': ['geo_data/*.*']},
    install_requires=[
        'geopandas',
        'matplotlib',
        'pandas',
        'seaborn'
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
