from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gaiweb",
    version="1.0.4",
    author="python_xueba",
    description="gaiweb是一个基于 Flask 的轻量级 Gemini 流式聊天本地应用 ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pythonxueba", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.0",
        "flask-cors",
        "requests",
        "beautifulsoup4",
    ],
    entry_points={
        "console_scripts": [
            "gaiweb=main",
        ],
    },
    include_package_data=True,
)