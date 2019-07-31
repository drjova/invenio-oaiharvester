# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test for utilities used by OAI harvester."""

from __future__ import absolute_import, print_function

import re

import responses
from click.testing import CliRunner

from invenio_oaiharvester.cli import harvest


@responses.activate
def test_cli_harvest_idents(script_info, sample_record_xml, tmpdir):
    """Test create user CLI."""
    responses.add(
        responses.GET,
        'http://export.arxiv.org/oai2',
        body=sample_record_xml,
        content_type='text/xml'
    )

    runner = CliRunner()
    result = runner.invoke(
        harvest,
        ['-u', 'http://export.arxiv.org/oai2',
         '-m', 'arXiv',
         '-i', 'oai:arXiv.org:1507.03011'],
        obj=script_info
    )
    assert result.exit_code == 0

    # Cannot use dates and identifiers
    result = runner.invoke(
        harvest,
        ['-u', 'http://export.arxiv.org/oai2',
         '-m', 'arXiv',
         '-f', '2015-01-17',
         '-i', 'oai:arXiv.org:1507.03011'],
        obj=script_info
    )
    assert result.exit_code != 0

    # Queue it
    result = runner.invoke(
        harvest,
        ['-u', 'http://export.arxiv.org/oai2',
         '-m', 'arXiv',
         '-i', 'oai:arXiv.org:1507.03011',
         '--enqueue'],
        obj=script_info
    )
    assert result.exit_code == 0

    # Save it directory
    result = runner.invoke(
        harvest,
        ['-u', 'http://export.arxiv.org/oai2',
         '-m', 'arXiv',
         '-i', 'oai:arXiv.org:1507.03011',
         '-d', tmpdir.dirname],
        obj=script_info
    )
    assert result.exit_code == 0

    # Missing URL
    result = runner.invoke(
        harvest,
        ['-m', 'arXiv',
         '-i', 'oai:arXiv.org:1507.03011'],
        obj=script_info
    )
    assert result.exit_code != 0


@responses.activate
def test_cli_harvest_list(script_info, sample_empty_set):
    """Test create user CLI."""
    responses.add(
        responses.GET,
        re.compile(r'http?://export.arxiv.org/oai2.*set=physics.*'),
        body=sample_empty_set,
        content_type='text/xml'
    )

    runner = CliRunner()
    result = runner.invoke(
        harvest,
        ['-u', 'http://export.arxiv.org/oai2',
         '-m', 'arXiv',
         '-s', 'physics',
         '-f', '2015-01-17',
         '-t', '2015-01-17',
         '-e', 'utf-8'],
        obj=script_info
    )
    assert result.exit_code == 0

    # Queue it
    result = runner.invoke(
        harvest,
        ['-u', 'http://export.arxiv.org/oai2',
         '-m', 'arXiv',
         '-s', 'physics',
         '-f', '2015-01-17',
         '-t', '2015-01-17',
         '--enqueue'],
        obj=script_info
    )
    assert result.exit_code == 0
