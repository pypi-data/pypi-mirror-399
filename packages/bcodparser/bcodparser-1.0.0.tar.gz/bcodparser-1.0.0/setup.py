from setuptools import setup, find_packages
 
setup(
    include_package_data=True,
	name="bcodparser",
	version="1.0.0",
	packages=find_packages(),
	description="Allows you to decode the Bluetooth Class of Device (CoD) field and interpret major, minor, and service classes.",
	url="https://github.com/Lou-du-Poitou/bcodparser/",
	author="V / Lou du Poitou",
    maintainer_email="v.loudupoitou@gmail.com",
	license="MIT",
)