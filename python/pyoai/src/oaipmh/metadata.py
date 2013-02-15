from lxml import etree
from lxml.etree import SubElement
from oaipmh import common

class MetadataRegistry(object):
    """A registry that contains readers and writers of metadata.

    a reader is a function that takes a chunk of (parsed) XML and
    returns a metadata object.

    a writer is a function that takes a takes a metadata object and
    produces a chunk of XML in the right format for this metadata.
    """
    def __init__(self):
        self._readers = {}
        self._writers = {}
        
    def registerReader(self, metadata_prefix, reader):
        self._readers[metadata_prefix] = reader

    def registerWriter(self, metadata_prefix, writer):
        self._writers[metadata_prefix] = writer

    def hasReader(self, metadata_prefix):
        return metadata_prefix in self._readers
    
    def hasWriter(self, metadata_prefix):
        return metadata_prefix in self._writers
    
    def readMetadata(self, metadata_prefix, element):
        """Turn XML into metadata object.

        element - element to read in

        returns - metadata object
        """
        return self._readers[metadata_prefix](element)

    def writeMetadata(self, metadata_prefix, element, metadata):
        """Write metadata as XML.
        
        element - ElementTree element to write under
        metadata - metadata object to write
        """
        self._writers[metadata_prefix](element, metadata)

global_metadata_registry = MetadataRegistry()

class Error(Exception):
    pass

class MetadataReader(object):
    """A default implementation of a reader based on fields.
    """
    def __init__(self, fields, namespaces=None):
        self._fields = fields
        self._namespaces = namespaces or {}

    def __call__(self, element):
        map = {}
        # create XPathEvaluator for this element
        xpath_evaluator = etree.XPathEvaluator(element, 
                                               namespaces=self._namespaces)
        
        e = xpath_evaluator.evaluate
        # now extra field info according to xpath expr
        for field_name, (field_type, expr) in self._fields.items():
            if field_type == 'bytes':
                value = str(e(expr))
            elif field_type == 'bytesList':
                value = [str(item) for item in e(expr)]
            elif field_type == 'text':
                # make sure we get back unicode strings instead
                # of lxml.etree._ElementUnicodeResult objects.
                value = unicode(e(expr))
            elif field_type == 'textList':
                # make sure we get back unicode strings instead
                # of lxml.etree._ElementUnicodeResult objects.
                value = [unicode(v) for v in e(expr)]
            else:
                raise Error, "Unknown field type: %s" % field_type
            map[field_name] = value
        return common.Metadata(map)

oai_dc_reader = MetadataReader(
    fields={
    'title':       ('textList', 'oai_dc:dc/dc:title/text()'),
    'creator':     ('textList', 'oai_dc:dc/dc:creator/text()'),
    'subject':     ('textList', 'oai_dc:dc/dc:subject/text()'),
    'description': ('textList', 'oai_dc:dc/dc:description/text()'),
    'publisher':   ('textList', 'oai_dc:dc/dc:publisher/text()'),
    'contributor': ('textList', 'oai_dc:dc/dc:contributor/text()'),
    'date':        ('textList', 'oai_dc:dc/dc:date/text()'),
    'type':        ('textList', 'oai_dc:dc/dc:type/text()'),
    'format':      ('textList', 'oai_dc:dc/dc:format/text()'),
    'identifier':  ('textList', 'oai_dc:dc/dc:identifier/text()'),
    'source':      ('textList', 'oai_dc:dc/dc:source/text()'),
    'language':    ('textList', 'oai_dc:dc/dc:language/text()'),
    'relation':    ('textList', 'oai_dc:dc/dc:relation/text()'),
    'coverage':    ('textList', 'oai_dc:dc/dc:coverage/text()'),
    'rights':      ('textList', 'oai_dc:dc/dc:rights/text()')
    },
    namespaces={
    'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'dc' : 'http://purl.org/dc/elements/1.1/'}
    )

oai_iso19139_reader = MetadataReader(
    fields={
    'title':       ('textList', 'gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString/text()')
    },
    namespaces={  
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gts': 'http://www.isotc211.org/2005/gts',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gml': 'http://www.opengis.net/gml',
    'geonet': 'http://www.fao.org/geonetwork'}
    )

# mets uses: xmlns="http://www.loc.gov/METS/"
# Since it is in the default namespace, we have remap each element
# into its own namespace: mets (requirement of lxml & etree)
# ORIG: mets/dmdSec/mdWrap/xmlData/mods:mods/mods:titleInfo/mods:title
# USE : mets:mets/mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:titleInfo/mods:title
oai_mets_reader = MetadataReader(
    fields={
    'title':       ('textList', 'mets:mets/mets:dmdSec/mets:mdWrap/mets:xmlData/mods:mods/mods:titleInfo/mods:title/text()')
    },
    namespaces={
    'mets': 'http://www.loc.gov/METS/',
    'mods': 'http://www.loc.gov/mods/v3'}
    )

oai_ore_reader = MetadataReader(
    fields={
    'title':       ('textList', 'atom:entry/atom:title/text()')
    },
    namespaces={  
    'atom':      'http://www.w3.org/2005/Atom',
    'ore':       'http://www.openarchives.org/ore/terms/',
    'oreatom':   'http://www.openarchives.org/ore/atom/',
    'dcterms':   'http://purl.org/dc/terms/'}
    )

oai_qdc_reader = MetadataReader(
    fields={
    'title':       ('textList', 'qdc:qualifieddc/dc:title/text()')
    },
    namespaces={  
    'dc':       'http://purl.org/dc/elements/1.1/',
    'dcterms':  'http://purl.org/dc/terms/',
    'qdc':      'http://epubs.cclrc.ac.uk/xmlns/qdc/'}
    )

oai_rdf_reader = MetadataReader(
    fields={
    'title':       ('textList', 'rdf:RDF/ow:Publication/dc:title/text()')
    },
    namespaces={
    'rdf':      'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'ow':       'http://www.ontoweb.org/ontology/1#',
    'dc':       'http://purl.org/dc/elements/1.1/',
    'ds':       'http://dspace.org/ds/elements/1.1/'}
    )
