import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="acquifer",
	version="0.0.1",
	author="Laurent Thomas",
	author_email="laurent.thomas@bruker.com",
	description="Utilitary functions when working with image datasets acquired with an ACQUIFER Imaging Machine",
	long_description=long_description,
	long_description_content_type="text/markdown",
	keywords="microscopy image-processing image-analysis",
	packages=["acquifer"],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
		"Intended Audience :: Science/Research"		
	],
)