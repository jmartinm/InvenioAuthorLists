## This file is part of Invenio.
## Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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

testdir = $(libdir)/webtest/invenio

imgdir=$(localstatedir)/www/img

test_DATA = test_bibedit_access_curator_coll.html \
            test_bibedit_access_curator_all.html \
            test_bibedit_access_curator_none.html \
            test_bibedit_basic_record_locking.html
            
img_DATA = authorlist.css \
           authorlist.colVis.css \
           authorlist.jquery-ui.custom.css \
           authorlist.dataTable.css \
           authorlist.dataTable.jquery-ui.css \
           authorlist.spreadSheet.css

EXTRA_DIST = $(doc_DATA) $(test_DATA) $(img_DATA)

CLEANFILES = *~ *.tmp
