# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import re

import pytest
import responses

from invenio_oaiharvester.errors import InvenioOAIHarvesterError
from invenio_oaiharvester.signals import oaiharvest_finished
from invenio_oaiharvester.tasks import get_specific_records, \
    list_records_from_dates


@responses.activate
def test_get_specific_records(app, sample_record_xml):
    """Test that getting records via identifiers work with prefix."""
    def foo(request, records, name):
        assert len(records) == 1

    responses.add(
        responses.GET,
        'http://export.arxiv.org/oai2',
        body=sample_record_xml,
        content_type='text/xml'
    )
    oaiharvest_finished.connect(foo)
    try:
        with app.app_context():
            get_specific_records(
                'oai:arXiv.org:1507.03011',
                metadata_prefix="arXiv",
                url='http://export.arxiv.org/oai2'
            )
            # As a list of identifiers
            get_specific_records(
                ['oai:arXiv.org:1507.03011'],
                metadata_prefix="arXiv",
                url='http://export.arxiv.org/oai2'
            )
    finally:
        oaiharvest_finished.disconnect(foo)


@responses.activate
def test_list_records_from_dates(app, sample_list_xml):
    """Check harvesting of records from multiple setspecs."""
    def bar(request, records, name):
        assert len(records) == 150

    responses.add(
        responses.GET,
        re.compile(r'http?://export.arxiv.org/oai2.*set=physics.*'),
        body=sample_list_xml,
        content_type='text/xml'
    )
    oaiharvest_finished.connect(bar)
    try:
        with app.app_context():
            list_records_from_dates(
                metadata_prefix='arXiv',
                from_date='2015-01-15',
                until_date='2015-01-20',
                url='http://export.arxiv.org/oai2',
                name=None,
                setspecs='physics'
            )
    finally:
        oaiharvest_finished.disconnect(bar)
