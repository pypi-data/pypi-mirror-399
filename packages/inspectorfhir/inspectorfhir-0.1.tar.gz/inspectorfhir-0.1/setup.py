import os
from setuptools import setup, find_packages


setup(name="inspectorfhir",
      version="0.1",
      description="Library and command line tools for inspecting FHIR server's discoverble endpoints.",
      long_description="""inspectorfhir.ifhir takes in a FHIR server base URL and queries its discoverable endpoints, printing them to standard out. It can also be used as a library to fetch and parse the discoverable endpoints from a FHIR server.""",
      author="Alan Viars",
      author_email="alan@transparenthealth.org",
      url="https://github.com/transparenthealth/inspectorfhir",
      download_url="https://github.com/transparenthealth/inspectorfhir/tarball/master",
      install_requires=[ 'requests', 'certifi'],
      packages=['inspectorfhir',],
      include_package_data=True,
      scripts=['inspectorfhir/ifhir.py', ]
      )
