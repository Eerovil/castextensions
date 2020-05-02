from setuptools import setup, find_packages


long_description = open("README.md").read()

setup(
    name="Cast Extensions",
    version="0.1",
    license="MIT",
    url="https://github.com/Eerovil/cast-extensions.git",
    author="Eero Vilpponen",
    author_email="eero@vilpponen.fi",
    description="Cast Extensions",
    long_description=long_description,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=list(val.strip() for val in open("pip-requirements.txt")),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
