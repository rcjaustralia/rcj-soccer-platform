from setuptools import setup, find_packages
import sys

if sys.version_info < (2,7):
    raise OSError("Can't run in Python < 2.7")
elif sys.version_info > (3, 0) and sys.version_info <= (3, 3):
    raise OSError("We don't support this far back")

requires = [
    'Flask',
    'Flask-Migrate',
    'Flask-Script',
    'Flask-SQLAlchemy',
    'PyMySQL',
    'python-dateutil',
    'requests',
    'six'
]

if sys.version_info < (3, 5):
    requires.append("typing")

if sys.version_info < (3, 0):
    requires.append("bjoern")

setup(
    name='rcj-soccer',
    version='0.1.0',
    url='https://github.com/rcjaustralia/rcj-soccer-platform/',
    license='MIT',
    author='RoboCup Junior Australia',
    author_email='tristan_roberts@icloud.com',
    description='A system to manage soccer draws, refereeing, and scoring for RoboCup Junior Australia',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
