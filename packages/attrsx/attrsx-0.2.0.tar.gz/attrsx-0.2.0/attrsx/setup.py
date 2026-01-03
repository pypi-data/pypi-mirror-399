from setuptools import setup

import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
path_to_readme = os.path.join(here, "README.md")

long_description = """# Attrsx

**attrsx – An Extension to _attrs_ for Declarative Handler Injection & Integrated Logging**

---

### 1. Purpose

`attrsx` builds on top of the `attrs` data‑class library and contributes two orthogonal capabilities that are frequently needed in service‑layer and infrastructure code:

1. **Integrated Logging** – transparent, boilerplate‑free creation of a configured `logging.Logger` for every instance.
2. **Declarative Handler Injection** – generation of lazy‑initialised *strategy* objects (“handlers”) declared via `handler_specs`.

Both features are opt‑in; if a class does not request them, `attrsx.define` behaves exactly like `attrs.define`.

---

### 2. Key Features

* **Drop-in replacement for `attrs.define`** – forwards every keyword parameter that `attrs.define` understands (`slots`, `frozen`, `kw_only`, validators, converters, …).

* **Integrated logging** – injects four fields (`logger`, `loggerLvl`, `logger_name`, `logger_format`) and wraps `__attrs_post_init__` to attaches a `logging.logger` 
    to the instance if none is present.  The logger’s name defaults to the class name; level and format are configurable per instance.

* **Declarative handler injection** – for each entry in `handler_specs={"key": HandlerClass, ...}` the decorator adds three fields  
  (`<key>_class`, `<key>_params`, `<key>_h`) plus a lazy factory method `_initialize_<key>_h()`, which calls  
  `<key>_class(**<key>_params)` the first time it is invoked.

* **Type-hint compliance** – all generated attributes are inserted into `__annotations__`, so static type-checkers recognise them.

* **Zero runtime overhead** – field and method generation is performed once, at import time; normal instance construction stays on the `attrs` fast path.


---

### 3. Underlying Pattern

The handler mechanism realises **Declarative Handler Injection** (a variant of the Strategy pattern implemented through composition and a lazy factory method). 
Configuration is expressed as data, leaving the host class agnostic of concrete strategy classes.

---

### 4. When to Use

- You need consistent, ready‑to‑use logging across many small classes.
- You want to supply interchangeable helper or strategy objects without manual glue code.
- You prefer composition over inheritance but dislike factory boilerplate.

If none of the above apply, simply continue to use `attrs.define`; the migration path is one import statement.

"""

if os.path.exists(path_to_readme):
  with codecs.open(path_to_readme, encoding="utf-8") as fh:
      long_description += fh.read()

setup(
    name="attrsx",
    packages=["attrsx"],
    install_requires=['attrs>=22.2.0'],
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Intended Audience :: Science/Research', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.9', 'Programming Language :: Python :: 3.10', 'Programming Language :: Python :: 3.11', 'Programming Language :: Python :: 3.12', 'License :: OSI Approved :: MIT License', 'Topic :: Scientific/Engineering'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Kyrylo Mordan",
    author_email="parachute.repo@gmail.com",
    description="A lightweight extension of attrs that adds extras like logging.",
    license="mit",
    url="https://kiril-mordan.github.io/reusables/attrsx/",
    keywords=['aa-paa-tool'],
    version="0.2.0",    include_package_data = True,
    package_data = {'attrsx': ['mkdocs/**/*', '.paa.tracking/version_logs.csv', '.paa.tracking/release_notes.md', '.paa.tracking/lsts_package_versions.yml', '.paa.tracking/notebook.ipynb', '.paa.tracking/package_mapping.json', '.paa.tracking/package_licenses.json', 'tests/**/*', '.paa.tracking/.paa.config', '.paa.tracking/python_modules/attrsx.py', '.paa.tracking/.paa.version']} ,
    )
