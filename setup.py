import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='SimpleWebFileBrowser',
    version='0.0.1',
    author='Yap Yee King',
    author_email='yeeking.yap2@3ds.com',
    description=('A simple web file browser with flask, gevent and Jinja2'),
    keywords='SimpleWebFileBrowser',
    url='https://github.com/kingkingyyk/SimpleWebFileBrowser.git',
    packages=find_packages(),
    install_requires=read('requirements.txt').splitlines(),
    long_description=read('README.md'),
    classifiers=['Development Status :: Release',
                 'Topic :: Utilities'],
    package_data={'' : ['templates/*.html']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['SimpleWebFileBrowser=filebrowser.cli:main'],
    }
)