from setuptools import setup, find_packages

setup(
    name="auto-base",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "ag2>=0.1.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A thin wrapper for ag2",
    long_description="A thin wrapper that simplifies the usage of ag2 library",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/auto-base",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)