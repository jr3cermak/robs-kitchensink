.. -*- restructuredtext -*-

OAIPMH
======

The oaipmh module is a Python implementation of an "Open Archives
Initiative Protocol for Metadata Harvesting" (version 2) client and
server.  The protocol is described here:

http://www.openarchives.org/OAI/openarchivesprotocol.html

Below is a simple implementation of an OAIPMH client:

>>> from oaipmh.client import Client
>>> from oaipmh.metadata import MetadataRegistry, oai_dc_reader

>>> URL = 'http://uni.edu/ir/oaipmh'

>>> registry = MetadataRegistry()
>>> registry.registerReader('oai_dc', oai_dc_reader)
>>> client = Client(URL, registry)

>>> for record in client.listRecords(metadataPrefix='oai_dc'):
>>>    print record


The pyoai package also contains a generic server implementation of the 
OAIPMH protocol, this is used as the foundation of the `MOAI Server Platform`_

.. _MOAI Server Platform: http://pypi.python.org/pypi/MOAI

The code from this repository supports additional readers:

+----------------+----------------+-----------------------------------------------------------+
| metadataPrefix | oai_*_reader   | Reference URL                                             |
+================+================+===========================================================+
| iso19139       | iso19139       | http://en.wikipedia.org/wiki/Geospatial_metadata          |
+----------------+----------------+-----------------------------------------------------------+
| mets           | mets           | http://www.loc.gov/standards/mets/                        |
+----------------+----------------+-----------------------------------------------------------+
| oai_dc         | dc             | http://www.openarchives.org/OAI/openarchivesprotocol.html |
+----------------+----------------+-----------------------------------------------------------+
| ore            | ore            | http://www.openarchives.org/ore/1.0/atom.html             |
+----------------+----------------+-----------------------------------------------------------+
| qdc            | qdc            | http://wiki.dublincore.org/index.php/User_Guide           |
+----------------+----------------+-----------------------------------------------------------+
| rdf            | rdf            | http://www.openarchives.org/ore/1.0/rdfxml.html           |
+----------------+----------------+-----------------------------------------------------------+
