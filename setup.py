from setuptools import setup, find_packages

version = '0.1.5'

setup(
    name='gites.proprio',
    version=version,
    description="",
    long_description=open("CHANGES.txt").read(),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Programming Language :: Python",
      ],
    keywords='',
    author='',
    author_email='',
    url='https://github.com/gitesdewallonie/gites.proprio',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['gites'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'five.grok',
        'gites.core',
        'gites.db',
        'micawber',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
