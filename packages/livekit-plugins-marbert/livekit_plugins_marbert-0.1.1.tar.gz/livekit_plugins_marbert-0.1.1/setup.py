from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="livekit-plugins-marbert",
    version="0.1.1",
    description="Arabic End-of-Utterance detection for LiveKit using MARBERT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Azeddin Sahir",
    author_email="azdinsahir11@gmail.com",
    url="https://github.com/azeddinshr/livekit-plugins-marbert",
    packages=find_namespace_packages(include=["livekit.*"]),
    install_requires=[
        "livekit-agents>=1.3.9,<2.0.0",
        "transformers>=4.30.0,<5.0.0",
        "torch>=2.0.0,<3.0.0",
        "numpy>=1.21.0,<2.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="livekit voice-ai arabic eou turn-detection marbert nlp",
)