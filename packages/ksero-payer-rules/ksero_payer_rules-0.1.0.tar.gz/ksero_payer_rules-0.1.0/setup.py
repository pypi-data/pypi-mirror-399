from setuptools import setup, find_packages

setup(
    name="ksero-payer-rules",
    version="0.1.0",
    description="Payer-specific rules and validation for medical, dental, and vision insurance cards",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="David Ferguson",
    author_email="you@example.com",
    url="https://github.com/yourusername/ksero-payer-rules",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)