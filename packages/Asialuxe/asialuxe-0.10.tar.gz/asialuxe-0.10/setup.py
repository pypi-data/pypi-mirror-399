import setuptools

setuptools.setup(
	name='Asialuxe',
	version='0.10',
	author='rodnoc',
	author_email='rodnoc@list.ru',
	description='Asialuxe API',
	packages=['Asialuxe'],
	install_requires=["requests"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)