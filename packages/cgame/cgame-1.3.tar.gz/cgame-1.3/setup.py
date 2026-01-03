from setuptools import setup

setup(
    name="cgame",
    version="1.3",
    description="A lightweight C++/pybind11 game framework for Python (Windows only)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="M.Hassnain.K",
    author_email="muhammadhassnainkhichi@gmail.com",
    url="https://github.com/mhassnaink/cgame",
    license="zlib/libpng",
    packages=["cgame"],
    package_data={"cgame": ["*.pyd"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: zlib/libpng License",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.11",
    zip_safe=False,
)