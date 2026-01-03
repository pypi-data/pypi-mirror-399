import os
from setuptools import setup, find_packages


setup(name="ifhir",
      version="0.2",
      description="Library and command line tools for inspecting FHIR server's discoverble endpoints.",
      long_description="""ifhir.py takes in a FHIR server base URL and queries its discoverable endpoints, printing them to standard out. It can also be used as a library to fetch and parse the discoverable endpoints from a FHIR server.""",
      author="Alan Viars",
      author_email="alan@transparenthealth.org",
      url="https://github.com/transparenthealth/inspectorfhir",
      download_url="https://github.com/transparenthealth/inspectorfhir/tarball/master",
      install_requires=[ 'requests', 'certifi'],
      packages=['ifhir',],
      include_package_data=True,
      scripts=['ifhir/ifhir.py', ]
      )
