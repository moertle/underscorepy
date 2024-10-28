all:
	@#

install: all
	pip3 install --upgrade .

deb:
	@rm -rf deb_dist/
	python3 setup.py --command-packages=stdeb.command bdist_deb

dist: all
	@./setup.py sdist

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} +

distclean: clean
	@rm -rf build/ dist/ *.egg-info/
