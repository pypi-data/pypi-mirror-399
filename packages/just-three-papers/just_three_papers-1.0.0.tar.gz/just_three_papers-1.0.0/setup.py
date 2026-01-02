from setuptools import setup, find_packages

setup(
    name="just_three_papers",
    version="1.0.0",
    description="Tri-Planar Orthogonal Complex Mapping Library",
    author="Nur Rohmat Hidayatulloh",
    author_email="eroscupd@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires='>=3.8',
)