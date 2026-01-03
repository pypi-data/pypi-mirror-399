from setuptools import setup, find_packages

setup(
    name="smartscanner",
    version="0.1.0",
    author="Abhinav Prasad",
    description="Document scanning pipeline: detect, warp, deskew, enhance, export to PDF.",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "imutils",
        "Pillow",
    ],
    python_requires=">=3.8",
)