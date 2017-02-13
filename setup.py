from setuptools import setup, find_packages

requires = [
    'Flask',
    'Flask-Migrate',
    'Flask-Script',
    'Flask-SQLAlchemy',
    'PyMySQL',
    'python-dateutil',
    'requests',
]

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
