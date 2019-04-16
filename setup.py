import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-lti-login",
    version="0.0.2",
    auther="Ruiyang Ding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JohnDing1995/flask-lti-login",
    packages=setuptools.find_packages(),
    install_requires=[
        'flask',
        'oauthlib',
        'blinker'
     ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)