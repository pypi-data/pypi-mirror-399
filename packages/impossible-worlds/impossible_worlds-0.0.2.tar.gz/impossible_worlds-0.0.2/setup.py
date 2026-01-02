from setuptools import setup, find_packages

setup(
    name="impossible-worlds",  # <--- یہ نام یونیک ہونا چاہیے (pip install والا نام)
    version="0.0.2",
    packages=find_packages(),
    install_requires=["requests"],
    description="My Private Ufone API Library",
    author="Nothing Is Impossible",
    author_email="marslansalfias@mail.com" 
)
