from setuptools import setup, find_packages

setup(
    name="torahlm",
    version="0.0.1",
    author="TorahLM",
    author_email="TorahLM.org@gmail.com",
    description="The open-source standard for reliable Torah AI.",
    long_description="Reserved for the TorahLM project.",
    long_description_content_type="text/markdown",
    url="https://github.com/TorahLM",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
