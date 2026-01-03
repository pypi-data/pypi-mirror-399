
import re
import setuptools

install_requires = open("requirements.txt", "r").readlines()
packages = setuptools.find_packages(exclude=["tests"])

def read(f):
    with open(f, encoding='utf-8') as file:
        return file.read()

def version ():
    return "1.0.0"

setuptools.setup(
    name = "polympiads_statelessauth",
    version = version(),
    description = "Polympiads Framework for Stateless Auth",
    long_description = read("README.md"),
    long_description_content_type='text/markdown',
    url = "https://polympiads.github.io/statelessauth",
    install_requires = install_requires,
    author = "Polympiads",
    license = "MIT",
    packages = packages,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    project_urls={
        'About Polympiads': 'https://polympiads.ch/',
        'Source': 'https://github.com/polympiads/statelessauth'
    }
)