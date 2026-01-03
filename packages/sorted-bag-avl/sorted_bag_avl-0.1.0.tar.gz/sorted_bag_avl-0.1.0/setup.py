from setuptools import setup, find_packages

setup(
    name="sorted_bag_avl",  # Name on PyPI 
    version="0.1.0",
    author="Raghu Pratap Singh",
    author_email="raghupratapsinghparmar@gmail.com",
    description="A high-performance AVL-based Sorted Bag with Order Statistics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Raghu-Pratap-Singh/Sorted-Bag-AVL", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)