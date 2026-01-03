from setuptools import setup, find_packages

setup(
    name="AbzarAmar",              
    version="0.1.0",                  
    description="Simple statistics functions",
    long_description=open("README.txt").read(),
    long_description_content_type="text/plain",
    author="NEGAR MANSOURI",
    packages=find_packages(),       
    python_requires=">=3.6",
)
