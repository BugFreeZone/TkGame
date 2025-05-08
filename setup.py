from setuptools import setup, find_packages

setup(
    name="TkGame",
    version="1.0.0",
    description="Простая игровая библиотека на базе tkinter",
    author="BugFreeZone",
    author_email="r96177385@gmail.com",
    url="https://github.com/BugFreeZone/TkGame",
    packages=find_packages(),
    install_requires=[
        "playsound>=1.2.2",
        "Pillow>=9.0.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    include_package_data=True,
)
