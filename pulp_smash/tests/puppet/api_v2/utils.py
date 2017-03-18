# coding=utf-8
"""Utility functions for Puppet API tests."""
from pulp_smash import utils


def gen_repo():
    """Return a semi-random dict that used for creating a puppet repo."""
    return {
        'id': utils.uuid4(),
        'importer_config': {},
        'importer_type_id': 'puppet_importer',
        'notes': {'_repo-type': 'puppet-repo'},
    }


def gen_distributor():
    """Return a semi-random dict for use in creating a Puppet distributor."""
    return {
        'auto_publish': False,
        'distributor_config': {'serve_http': True, 'serve_https': True},
        'distributor_id': utils.uuid4(),
        'distributor_type_id': 'puppet_distributor',
    }
