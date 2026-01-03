from setuptools import setup

setup(
    name="link-domain",
    version="1.0.0",
    packages=["linkdomain"],
    entry_points={
        "console_scripts": [
            "link-domain=linkdomain.__main__:main",
        ],
    },
    python_requires=">=3.8",
)
