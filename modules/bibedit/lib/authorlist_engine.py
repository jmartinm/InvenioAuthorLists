## This file is part of Invenio.
## Copyright (C) 2009, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Invenio Authorlist Data Conversion Engine. """

import time
import tempfile
import simplejson as json
from xml.dom.minidom import getDOMImplementation

import invenio.authorlist_config as cfg
from invenio.search_engine import get_fieldvalues
from invenio.bibedit_utils import get_record
from invenio.shellutils import run_shell_command
from invenio.config import CFG_BINDIR, CFG_TMPSHAREDDIR

def retrieve_data_from_record(recid):
    """
    Extract data from a record id in order to import it to the Author list
    interface
    """
    output = {}

    bibrecord = get_record(recid)
    # Extract authors
    try:
        #FIXME include more fine-grained exception handling
        record_main_author = bibrecord['100']
        record_authors = bibrecord['700']
        record_authors.extend((record_main_author))
    except KeyError:
        return output
    # Extract affiliations
    record_affiliations = get_fieldvalues(int(recid), '700__u')
    record_affiliations.extend(get_fieldvalues(int(recid), '100__u'))
    # Add generic information about the paper
    output.update({'collaboration': '', 'experiment_number': '', 'last_modified': int(time.time()), 'reference_ids': [], 'paper_id': '1', 'paper_title': ''})
    # Generate all the author related information
    author_list = []
    for i in xrange(len(record_authors)):
        inspire_id = [x[1] for x in record_authors[i][0][1:] if x[0] == 'i']
        if not inspire_id:
            inspire_id = ''
        else:
            inspire_id = inspire_id[0]
        author_info = [long(i+1), '', record_authors[i][0][0][1].split(',')[0],record_authors[i][0][0][1].split(',')[1], record_authors[i][0][0][1], True, [[x[1], 'Affiliated with'] for x in record_authors[i][0][1:] if x[0] == 'u'], inspire_id]
        author_list.append(author_info)

    output.update({'authors': author_list})
    # Generate all the affiliation related information
    unique_affiliations = list(set(record_affiliations))
    affiliation_list = []
    for i in xrange(len(unique_affiliations)):
        affiliation = [long(i+1), '', unique_affiliations[i], '', unique_affiliations[i], '', True, '']
        affiliation_list.append(affiliation)
    output.update( {'affiliations': affiliation_list})

    return output

class Converter(object):
    CONTENT_TYPE = 'text/plain'
    FILE_NAME = 'converted.txt'

    def __init__(self):
        raise NotImplementedError
        
    def dump(self, data):
        raise NotImplementedError
        
    def dumps(self, data):
        raise NotImplementedError
        
        
        
class NA62Latex(Converter):
    FILE_NAME = 'la.tex'
    
    def __init__(self):
        pass
        
    def dump(self, data):
        pass
        
    def dumps(self, data):
        pass

class ElsevierArticle(Converter):
    CONTENT_TYPE = 'text/plain'
    FILE_NAME = 'elsarticle.tex'

    def __init__(self):
        pass

    def dump(self, data):
        AuthorsXMLConverter = Converters.get('authorsxml')
        AuthorsXML = dumps(data, AuthorsXMLConverter)

        # write temporary file:
        tempfile.tempdir = CFG_TMPSHAREDDIR
        temp_filename = tempfile.mktemp(prefix="authorlistconvert" + \
               time.strftime("%Y%m%d%H%M%S", time.localtime()) + "_")
        open(temp_filename, 'w').write(AuthorsXML)

        # Use bibconvert for XSLT transformation
        # FIXME store xsl files in some folder and create a config
        # variable to define available templates
        template_path = '/tmp/LaTex_Type_1.xsl'
        dummy, myout, myerr = run_shell_command(cmd='%s/bibconvert -c%s < %s', \
                                                args=(CFG_BINDIR, template_path, \
                                                temp_filename))
        return myout

    def dumps(self, data):
        return self.dump(data).encode('utf-8')
        
class AuthorsXML(Converter):
    CONTENT_TYPE = 'text/xml'
    FILE_NAME = 'authors.xml'
    
    def __init__(self):
        pass
        
    def create_affiliation(self, document, parsed, organization_ids):
        affiliation = document.createElement('cal:authorAffiliation')
        
        affiliation_acronym = parsed[cfg.JSON.AFFILIATION_ACRONYM]
        affiliation_status = parsed[cfg.JSON.AFFILIATION_STATUS]
        
        affiliation.setAttribute('organizationid', 
                                 organization_ids[affiliation_acronym])
        affiliation.setAttribute('connection', affiliation_status)
        
        return affiliation
        
    def create_authors(self, document, root, parsed, organization_ids):
        parsed_authors = parsed[cfg.JSON.AUTHORS_KEY]
    
        authors = document.createElement('cal:authors')
        root.appendChild(authors)
        
        for parsed_author in parsed_authors:
            author = self.create_author(document, parsed_author, organization_ids)
            authors.appendChild(author)
        
    def create_author(self, document, parsed, organization_ids):
        author = document.createElement('foaf:Person')
        
        # paper name
        paper_name = document.createElement('cal:authorNamePaper')
        paper_name_info = parsed[cfg.JSON.PAPER_NAME]
        paper_name_text = document.createTextNode(paper_name_info)
        paper_name.appendChild(paper_name_text)
        author.appendChild(paper_name)
        
        # given name
        given_name_info = parsed[cfg.JSON.GIVEN_NAME]
        if (cfg.EMPTY.match(given_name_info) is None):
            given_name = document.createElement('foaf:givenName')
            given_name_text = document.createTextNode(given_name_info)
            given_name.appendChild(given_name_text)
            author.appendChild(given_name)
            
        # family name
        family_name_info = parsed[cfg.JSON.FAMILY_NAME]
        if (cfg.EMPTY.match(family_name_info) is None):
            family_name = document.createElement('foaf:familyName')
            family_name_text = document.createTextNode(family_name_info)
            family_name.appendChild(family_name_text)
            author.appendChild(family_name)
            
        # alive
        author_status_info = parsed[cfg.JSON.ALIVE]
        if (not author_status_info):
            author_status = document.createElement('cal:authorStatus')
            author_status_text = document.createTextNode(cfg.AuthorsXML.DECEASED)
            author_status.appendChild(author_status_text)
            author.appendChild(author_status)
            
        # collaboration
        collaboration = document.createElement('cal:authorCollaboration')
        collaboration.setAttribute('collaborationid', cfg.AuthorsXML.COLLABORATION_ID)
        author.appendChild(collaboration)
        
        # affiliations
        affiliations = document.createElement('cal:authorAffiliations')
        author.appendChild(affiliations)
        for parsed_affiliation in parsed[cfg.JSON.AFFILIATIONS]:
            affiliation = self.create_affiliation(document, parsed_affiliation, organization_ids)
            affiliations.appendChild(affiliation)
            
        # inspire id
        author_id_info = parsed[cfg.JSON.INSPIRE_ID]
        if (cfg.EMPTY.match(author_id_info) is None):
            author_ids = document.createElement('cal:authorids')
            author.appendChild(author_ids)
            
            author_id = document.createElement('cal:authorid')
            author_id.setAttribute('source', cfg.AuthorsXML.INSPIRE)
            author_id_text = document.createTextNode(author_id_info)
            author_id.appendChild(author_id_text)
            author_ids.appendChild(author_id)
        
        return author
        
    def create_collaboration(self, document, root, parsed):
        # collaborations
        collaborations = document.createElement('cal:collaborations')
        collaboration = document.createElement('cal:collaboration')
        collaboration.setAttribute('id', cfg.AuthorsXML.COLLABORATION_ID)
        collaborations.appendChild(collaboration)
        
        # name
        name = document.createElement('foaf:name')
        name_info = parsed[cfg.JSON.COLLABORATION]
        name_text = document.createTextNode(name_info)
        name.appendChild(name_text)
        collaboration.appendChild(name)
        
        # experiment number
        experiment_number_info = parsed[cfg.JSON.EXPERIMENT_NUMBER]
        if (cfg.EMPTY.match(experiment_number_info) is not None): return
        experiment_number = document.createElement('cal:experimentNumber')
        experiment_number_text = document.createTextNode(experiment_number_info)
        experiment_number.appendChild(experiment_number_text)
        root.appendChild(experiment_number)
        
    def create_document(self):
        dom = getDOMImplementation()
        document = dom.createDocument(None, 'collaborationauthorlist', None)
        root = document.documentElement
        
        root.setAttribute('xmlns:foaf', 'http://xmlns.com/foaf/0.1/')
        root.setAttribute('xmlns:cal', 'http://www.slac.stanford.edu/spires/hepnames/authors_xml/')
        
        return document, root
        
    def create_header(self, document, root, parsed):
        # creation date
        creation_date = document.createElement('cal:creationDate')
        creation_date_info = time.strftime(cfg.AuthorsXML.TIME_FORMAT)
        creation_date_text = document.createTextNode(creation_date_info)
        creation_date.appendChild(creation_date_text)
        root.appendChild(creation_date)
        
        # publication reference
        for reference_info in parsed[cfg.JSON.REFERENCE_IDS]:
            reference = document.createElement('cal:publicationReference')
            reference_text = document.createTextNode(reference_info)
            reference.appendChild(reference_text)
            root.appendChild(reference)
        
    def create_organizations(self, document, root, parsed, ids):
        parsed_organizations = parsed[cfg.JSON.AFFILIATIONS_KEY]
        
        # organizations container
        organizations = document.createElement('cal:organizations')
        root.appendChild(organizations)
        
        # create individual organizations and append them
        for parsed_organization in parsed_organizations:
            organization = self.create_organization(document, parsed_organization, ids)
            organizations.appendChild(organization)
            
    def create_organization(self, document, parsed, ids):
        acronym = parsed[cfg.JSON.ACRONYM]
        organization = document.createElement('foaf:Organization')
        organization.setAttribute('id', ids[acronym])
        
        # create the domain node if field is set
        domain_info = parsed[cfg.JSON.DOMAIN]
        if (cfg.EMPTY.match(domain_info) is None):
            domain = document.createElement('cal:orgDomain')
            domain_text = document.createTextNode(domain_info)
            domain.appendChild(domain_text)
            organization.appendChild(domain)
            
        # organization name, no presence check, already done on the client side
        name = document.createElement('foaf:name')
        name_info = parsed[cfg.JSON.NAME]
        name_text = document.createTextNode(name_info)
        name.appendChild(name_text)
        organization.appendChild(name)
        
        # inspire id
        org_name_info = parsed[cfg.JSON.SPIRES_ID]
        if ( cfg.EMPTY.match(org_name_info) is None):
            org_name = document.createElement('cal:orgName')
            org_name.setAttribute('source', cfg.AuthorsXML.SPIRES)
            org_name_text = document.createTextNode(org_name_info)
            org_name.appendChild(org_name_text)
            organization.appendChild(org_name)
            
        # membership
        org_status_info = parsed[cfg.JSON.MEMBER]
        if (not org_status_info):
            org_status_info = cfg.AuthorsXML.NONMEMBER
        else:
            org_status_info = cfg.AuthorsXML.MEMBER
        org_status = document.createElement('cal:orgStatus')
        org_status_text = document.createTextNode(org_status_info)
        org_status.appendChild(org_status_text)
        organization.appendChild(org_status)
        
        # umbrella organization/group
        group_info = parsed[cfg.JSON.UMBRELLA]
        if (cfg.EMPTY.match(group_info) is None):
            group = document.createElement('cal:group')
            group.setAttribute('with', ids[group_info])
            organizatio.appendChild(group)
        
        return organization
        
    def dump(self, data):
        parsed = json.loads(data)
        document, root = self.create_document()
        affiliations = parsed[cfg.JSON.AFFILIATIONS_KEY]
        
        organization_ids = self.generate_organization_ids(affiliations)
        
        self.create_header(document, root, parsed)
        self.create_collaboration(document, root, parsed)
        self.create_organizations(document, root, parsed, organization_ids)
        self.create_authors(document, root, parsed, organization_ids)
        
        return document
        
    def dumps(self, data):
        return self.dump(data).toprettyxml(indent = '    ', encoding = 'utf-8')
        
    def generate_organization_ids(self, organizations):
        ids = {}        
        # Map each organization acronym to an id of the kind 'o[index]'
        for index, organization in enumerate(organizations):
            acronym = organization[cfg.JSON.ACRONYM]
            ids[acronym] = cfg.AuthorsXML.ORGANIZATION_ID + str(index)
        
        return ids
        
class Converters:
    __converters__ = {'authorsxml' : AuthorsXML, 'elsevier': ElsevierArticle}
    
    @classmethod
    def get(cls, format):
        return cls.__converters__.get(format)
      
def dump(data, converter):
    return converter().dump(data)
    
def dumps(data, converter):
    return converter().dumps(data)
