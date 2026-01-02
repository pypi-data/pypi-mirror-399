from setuptools import setup,find_packages

setup(
    name='Sells_Application',
    version='0.1.0',
    long_description=open('README.md').read(),
    long_description_content_type= 'text/markdown',
    author='Henry Araya',
    author_email='arayaaraya_1@hotmail.com',
    description='Package for mannaging sells',
    maintainer='Henry Araya',
    url='http://github.com/sells_application',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
      
    )

#http://pypi.org/account/register/

