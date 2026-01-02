from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PDatainstaller",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="مكتبة Python لتحميل وتنفيذ الملفات",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PDatainstaller",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.7",
    install_requires=[],
    include_package_data=True,
)

