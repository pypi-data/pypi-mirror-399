from setuptools import setup, find_packages

setup(
    name="crow-kit",
    version="0.1.0",
    description="CroW-Kit: Crowdsourced Wrapper Generation Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kallol Naha",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.5",
        "beautifulsoup4>=4.12.0",
        "flask>=2.0.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
