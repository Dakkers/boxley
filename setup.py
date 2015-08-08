from distutils.core import setup
 
setup(
    name='Boxley',
    version='0.1.5',
    packages=['boxley'],
    description='Sync files to Dropbox using a git-like CLI.',
    author='Dakota St. Laurent',
    author_email='d.h.stlaurent@gmail.com',
    install_requires=['dropbox'],
    entry_points={
        'console_scripts': [
            'boxley = boxley.main:main',
        ]
    },
    extras_require={
        'test': ['pytest']
    }
)
