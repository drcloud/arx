#!/usr/bin/env python

from datetime import datetime
import os
from setuptools import setup
from subprocess import check_output, CalledProcessError


def version():
    from_file, from_git = None, None
    receipt = 'arx/VERSION'
    default = datetime.utcnow().strftime('%Y%m%d') + '+src'
    if os.path.exists('.git'):
        try:
            branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
            branch = branch.strip()
            tag = check_output(['git', 'describe'])
            dotted = tag.strip().replace('-', '.', 1).split('-')[0]
            from_git = dotted + ('' if branch == 'master' else '+' + branch)
        except CalledProcessError:
            pass
    if os.path.exists(receipt):
        with open(receipt) as h:
            txt = h.read().strip()
            if txt != '':
                from_file = txt
    version = from_git or from_file or default
    with open(receipt, 'w+') as h:
        h.write(version + '\n')
    return version


conf = dict(name='arx',
            version=version(),
            install_requires=['awscli',
                              'boto3',
                              'click',
                              'enum34',
                              'ptpython',
                              'pytz',
                              'sh',
                              'six',
                              'tzlocal',
                              'uritools'],
            setup_requires=['pytest-runner', 'setuptools'],
            tests_require=['flake8', 'pytest', 'tox'],
            description='Arx, a task manifest format.',
            packages=['arx', 'arx.sources', 'arx.sources.test'],
            package_data={'arx': ['VERSION']},
            entry_points={'console_scripts': ['arx = arx.__main__:main']},
            classifiers=['Environment :: Console',
                         'Intended Audience :: Developers',
                         'Operating System :: Unix',
                         'Operating System :: POSIX',
                         'Programming Language :: Python',
                         'Topic :: System',
                         'Topic :: System :: Systems Administration',
                         'Topic :: Software Development',
                         'Development Status :: 4 - Beta'])


if __name__ == '__main__':
    setup(**conf)
