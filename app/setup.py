import setuptools

setuptools.setup(
    name='xkcdref',
    version='2.0.1',
    author='Jeremy Simpson',
    description='xkcdref app',
    license='MIT',
    classifiers=[
        'Framework :: Flask',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'runsite-xkcdref = xkcdref.runserver:run'
        ]
    },
    install_requires=[
        'Flask',
        'simplejson',
        'gevent',
        'redis',
        'coloredlogs',
    ],
    include_package_data=True,
    zip_safe=False,
)
