# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

PY3 := $(shell which python3)

# Virtual Environment
VENV_DIR ?= .venv

# Extract ST2 pip version so can use same version in orquesta
ST2_BRANCH := $(shell echo $${ST2_BRANCH:-$${CIRCLE_BRANCH:-master}})
PIP_VERSION := $(shell curl --silent https://raw.githubusercontent.com/StackStorm/st2/$(ST2_BRANCH)/Makefile | grep 'PIP_VERSION ?= ' | awk '{ print $$3 }')

# Tox Environment
TOX_DIR ?= .tox

# Sphinx Document Options
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAUTO	  = sphinx-autobuild
SPHINXPROJ    = Orquesta
SOURCEDIR     = docs/source
BUILDDIR      = docs/build

# Packaging Options
PKGDISTDIR    = dist
PKGBUILDDIR   = build

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -rf $(TOX_DIR)
	rm -rf $(BUILDDIR)
	rm -rf $(PKGDISTDIR)
	rm -rf $(PKGBUILDDIR)

.PHONY: venv
venv:
	test -d $(VENV_DIR) || virtualenv -p $(PY3) $(VENV_DIR)

.PHONY: reqs
reqs: venv

	@echo "Upgrade to pip version $(PIP_VERSION)"
	$(VENV_DIR)/bin/pip install --upgrade "pip==$(PIP_VERSION)"
	$(VENV_DIR)/bin/pip install -r requirements.txt
	$(VENV_DIR)/bin/pip install -r requirements-test.txt
	$(VENV_DIR)/bin/pip install -r requirements-docs.txt
	$(VENV_DIR)/bin/python setup.py develop
	echo

.PHONY: schemas
schemas: reqs
	$(VENV_DIR)/bin/python bin/orquesta-generate-schemas

.PHONY: format
format:
	$(VENV_DIR)/bin/black orquesta bin setup.py -l 100

.PHONY: check
check:
	tox

.PHONY: docs
docs: reqs
	rm -rf $(BUILDDIR)
	. $(VENV_DIR)/bin/activate; $(SPHINXBUILD) -W -b html $(SOURCEDIR) $(BUILDDIR)/html

.PHONY: livedocs
livedocs: reqs
	rm -rf $(BUILDDIR)
	. $(VENV_DIR)/bin/activate; $(SPHINXAUTO) -H 0.0.0.0 -b html $(SOURCEDIR) $(BUILDDIR)/html

.PHONY: package
package:
	rm -rf $(PKGDISTDIR)
	rm -rf $(PKGBUILDDIR)
	$(VENV_DIR)/bin/python setup.py sdist bdist_wheel

.PHONY: publish
publish: package
	$(VENV_DIR)/bin/python -m twine upload dist/*

.PHONY: all
all: clean reqs schemas check package
