from distutils.core import setup
 
setup(
    name='Boxley',
    version='0.1.4',
    packages=['boxley', ],
    description='Sync files to Dropbox from the command line.',
    # long_description=open('README.md').read(),
    author='Dakota St. Laurent',
    author_email='d.h.stlaurent@gmail.com',
    install_requires=['dropbox'],
    entry_points={
        'console_scripts': [
            'boxley = boxley.main:main',
        ]
    }
)
