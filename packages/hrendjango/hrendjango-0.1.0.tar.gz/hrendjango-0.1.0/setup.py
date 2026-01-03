from pip_setuptools import setup, find_packages, requirements, clean

clean()
setup(
    name='hrendjango',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    author="Маг Ильяс DOMA (MagIlyasDOMA)",
    author_email='magilyas.doma.09@list.ru',
    python_requires='>=3.10',
    install_requires=requirements(),
    description='Global add-on to Django',
    license='MIT',
    url='https://github.com/MagIlyasDOMA/hrendjango',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
