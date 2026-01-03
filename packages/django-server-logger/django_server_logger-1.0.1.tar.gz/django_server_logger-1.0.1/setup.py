from pip_setuptools import setup, clean, find_packages, requirements, readme

clean()
setup(
    name='django-server-logger',
    version='1.0.1',
    packages=find_packages(),
    install_requires=requirements(),
    license='MIT',
    long_description=readme(),
    long_description_content_type="text/markdown",
    python_requires='>=3.8',
    description="Running the runserver_plus command with https and logging to the console and file",
    author='Маг Ильяс DOMA (MagIlyasDOMA)',
    author_email='magilyas.doma.09@list.ru',
    url='https://github.com/magilyasdoma/django-server-logger',
    entry_points={
        'console_scripts': [
            'runserver=server_logger:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Framework :: Django :: 6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
