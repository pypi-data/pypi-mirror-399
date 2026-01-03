from setuptools import setup, find_packages

VERSION = "1.0.3"

setup(
    name="easyttuimenus",  
    version=VERSION,
    description="Write simple UI for your code in seconds in a unified way using Easy TTUI Menus",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="sarcasticDweller",
    packages=find_packages(),
    python_requires=">=3.6",
)