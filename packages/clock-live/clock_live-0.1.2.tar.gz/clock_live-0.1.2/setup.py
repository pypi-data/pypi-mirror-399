from setuptools import setup, find_packages

setup(
    name="clock-live",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "pytz",
        "requests",
    ],
    author="TheLostIdea1",
    description="A live timezone and countdown library with auto-location.",
    long_description=open("README.md").read() if "README.md" in locals() else "Live clock library",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
