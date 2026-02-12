from setuptools import setup, find_packages

setup(
    name="dexcom-menubar",
    version="1.0.0",
    description="macOS menubar app for Dexcom G7 glucose readings",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "rumps>=0.4.0",
        "requests>=2.31.0",
        "keyring>=24.3.0",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "dexcom-menubar=dexcom_menubar.app:main",
            "dexcom-setup=dexcom_menubar.setup:main",
        ],
    },
    python_requires=">=3.8",
)
