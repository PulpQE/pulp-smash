# coding=utf-8
"""Tests that CRUD repositories."""
import unittest
from time import sleep

from requests.exceptions import HTTPError

from pulp_smash import api, config, selectors, utils
from pulp_smash.tests.pulp3.constants import REPO_PATH
from pulp_smash.tests.pulp3.pulpcore.utils import gen_repo
from pulp_smash.tests.pulp3.utils import adjust_url, get_auth, get_base_url
from pulp_smash.tests.pulp3.utils import set_up_module as setUpModule  # noqa pylint:disable=unused-import


class CRUDRepoTestCase(unittest.TestCase):
    """CRUD repositories."""

    @classmethod
    def setUpClass(cls):
        """Create class-wide variables."""
        cls.auth = get_auth()
        cls.cfg = config.get_config()
        cls.repo = {}

    def setUp(self):
        """Create an API client."""
        self.client = api.Client(self.cfg, api.code_handler)
        self.client.request_kwargs['auth'] = self.auth
        self.client.request_kwargs['url'] = adjust_url(get_base_url())

    def test_01_create_repo(self):
        """Create repository."""
        type(self).repo = self.client.post(REPO_PATH, gen_repo()).json()

    @selectors.skip_if(bool, 'repo', False)
    def test_02_read_repo(self):
        """Read a repository by its href.

        Assert that the response contains the correct repository name.
        """
        repo = self.client.get(self.repo['_href']).json()
        self.assertEqual(self.repo['name'], repo['name'])

    @selectors.skip_if(bool, 'repo', False)
    def test_02_read_repos(self):
        """Search for the repository by its name.

        Assert that just one search result is returned, and that that result
        has a correct name.
        """
        page = self.client.get(REPO_PATH, params={
            'name': self.repo['name']
        }).json()
        self.assertEqual(len(page['results']), 1)
        self.assertEqual(page['results'][0]['name'], self.repo['name'])

    @selectors.skip_if(bool, 'repo', False)
    def test_03_fully_update_name(self):
        """Update a repository's name using HTTP PUT."""
        if selectors.bug_is_untestable(3101, self.cfg.version):
            self.skipTest('https://pulp.plan.io/issues/3101')
        self.do_fully_update_attr('name')

    @selectors.skip_if(bool, 'repo', False)
    def test_03_fully_update_desc(self):
        """Update a repository's description using HTTP PUT."""
        self.do_fully_update_attr('description')

    def do_fully_update_attr(self, attr):
        """Update a repository attribute using HTTP PUT.

        :param attr: The name of the attribute to update. For example,
            "description." The attribute to update must be a string.
        """
        repo = self.client.get(self.repo['_href']).json()
        string = utils.uuid4()
        repo[attr] = string
        self.client.put(repo['_href'], repo)
        sleep(5)

        # verify the update
        repo = self.client.get(repo['_href']).json()
        self.assertEqual(string, repo[attr])

    @selectors.skip_if(bool, 'repo', False)
    def test_03_partially_update_name(self):
        """Update a repository's name using HTTP PATCH."""
        if selectors.bug_is_untestable(3101, self.cfg.version):
            self.skipTest('https://pulp.plan.io/issues/3101')
        self.do_partially_update_attr('name')

    @selectors.skip_if(bool, 'repo', False)
    def test_03_partially_update_desc(self):
        """Update a repository's description using HTTP PATCH."""
        self.do_partially_update_attr('description')

    def do_partially_update_attr(self, attr):
        """Update a repository attribute using HTTP PATCH.

        :param attr: The name of the attribute to update. For example,
            "description." The attribute to update must be a string.
        """
        string = utils.uuid4()
        self.client.patch(self.repo['_href'], {attr: string})
        sleep(5)

        # verify the update
        repo = self.client.get(self.repo['_href']).json()
        self.assertEqual(repo[attr], string)

    @selectors.skip_if(bool, 'repo', False)
    def test_04_delete_repo(self):
        """Delete a repository."""
        self.client.delete(self.repo['_href'])
        sleep(5)

        # verify the delete
        with self.assertRaises(HTTPError):
            self.client.get(self.repo['_href'])
