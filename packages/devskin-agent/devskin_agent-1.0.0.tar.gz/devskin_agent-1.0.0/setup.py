from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="devskin-agent",
    version="1.0.0",
    author="DevSkin Team",
    author_email="team@devskin.monitor",
    description="DevSkin Monitor Agent - Python Instrumentation SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devskin/devskin-monitor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "mypy>=1.7.0",
        ],
    },
    keywords="monitoring apm agent instrumentation observability tracing logging metrics",
)
