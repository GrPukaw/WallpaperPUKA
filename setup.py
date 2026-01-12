from setuptools import setup, find_packages

setup(
    name="wallpaperpuka",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "opencv-python>=4.5.0",
        "Pillow>=8.0.0",
        "pywin32>=300",
    ],
    entry_points={
        "console_scripts": [
            "wallpaperpuka=wallpaperpuka.main:main",
        ],
        "gui_scripts": [
            "wallpaperpuka-gui=wallpaperpuka.main:main",
        ],
    },
)
