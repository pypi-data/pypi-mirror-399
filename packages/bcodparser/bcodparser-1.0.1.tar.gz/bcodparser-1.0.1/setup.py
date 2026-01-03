from setuptools import setup, find_packages

with open(file=r"./README.md", mode="r", encoding="utf-8") as f:
    content = f.read()
    f.close()

setup(
    include_package_data=True,
	name="bcodparser",
	version="1.0.1",
	packages=find_packages(),
	description="Allows you to decode the Bluetooth Class of Device (CoD) field and interpret major, minor, and service classes.",
	url="https://github.com/Lou-du-Poitou/bcodparser/",
	author="V / Lou du Poitou",
    author_email="v.loudupoitou@gmail.com",
    maintainer="V / Lou du Poitou",
    maintainer_email="v.loudupoitou@gmail.com",
	license="MIT",
    long_description=content,
    long_description_content_type="text/markdown",
)