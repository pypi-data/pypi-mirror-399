from setuptools import setup, find_packages

setup(
    name="onedrive-upload",
    version="1.0.0",
    description="Simple OneDrive upload for company-wide access",
    author="Your Name",
    author_email="yash.edake@maxspike.in",
    packages=find_packages(),
    install_requires=[
        "msal>=1.24.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
