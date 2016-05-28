#!/usr/bin/env python
from setuptools import find_packages, setup

from v2 import v2


conf = dict(name='arx',
            author='Jason Dusek',
            author_email='jason.dusek@gmail.com',
            url='https://github.com/drcloud/arx',
            version=v2.from_git().from_file().from_default().imprint().version,
            install_requires=['awscli',
                              'boto3',
                              'click',
                              'enum34',
                              'magiclog',
                              'ptpython',
                              'pytz',
                              'pyyaml',
                              'schematics',
                              'sh',
                              'six',
                              'tzlocal',
                              'uritools',
                              'v2'],
            setup_requires=['pytest-runner', 'setuptools', 'v2'],
            tests_require=['flake8', 'pytest', 'tox'],
            description='Arx, a task manifest format.',
            packages=find_packages(),
            package_data={'arx.test': ['*.yaml']},
            entry_points={'console_scripts': ['arx = arx.__main__:main']},
            classifiers=['Environment :: Console',
                         'Intended Audience :: Developers',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: Unix',
                         'Operating System :: POSIX',
                         'Programming Language :: Python',
                         'Topic :: System',
                         'Topic :: System :: Systems Administration',
                         'Topic :: Software Development',
                         'Development Status :: 4 - Beta'])


if __name__ == '__main__':
    setup(**conf)
