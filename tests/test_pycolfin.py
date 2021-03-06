#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pycolfin
----------------------------------

Tests for `pycolfin` module.
"""
from contextlib import contextmanager
from unittest import mock, skip

from click.testing import CliRunner
from pycolfin import cli, pycolfin


class TestCOLFin:
    """
    Tests for `COLFin` class methods
    """
    @mock.patch.object(pycolfin.COLFin, 'login')
    def test_init(self, login):
        """
        When initializing a `COLFin` class, `login` should be called
        """
        valid_username = '1234-4567'
        valid_password = 'pycolfintest'
        pycolfin.COLFin(valid_username, valid_password)

        assert login.called
        assert login.call_args[0] == (valid_username, valid_password)

    @mock.patch.object(pycolfin.COLFin, 'response')
    @mock.patch.object(pycolfin.COLFin, 'login')
    def test_check_for_server_error(self, login, dummy_response):
        """
        Raise exception with message if server error was encountered when loading a page
        """
        dummy_response.status_code = 500
        valid_username = '1234-4567'
        valid_password = 'pycolfintest'
        colfin = pycolfin.COLFin(valid_username, valid_password)

        try:
            colfin.check_page_for_errors()
        except Exception:
            assert True
        else:
            assert False

    @mock.patch.object(pycolfin.COLFin, 'response')
    @mock.patch.object(pycolfin.COLFin, 'parsed')
    @mock.patch.object(pycolfin.COLFin, 'login')
    def test_check_for_session_expiration(self, login, dummy_parsed_response, dummy_response):
        """
        Raise exception with message if session expired when loading a page
        """
        dummy_response.status_code = 200
        dummy_parsed_response.text = 'Your session has timed out.'
        username = '1234-4567'
        password = 'pycolfintest'
        colfin = pycolfin.COLFin(username, password)

        try:
            colfin.check_page_for_errors()
        except Exception as e:
            assert True
        else:
            assert False

    @skip
    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pycolfin.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output


class TestValidators:
    def test_valid_user_id(self):
        """
        No exception should be raised if the user ID followed the correct format
        """
        valid_user_id = '1234-4567'
        try:
            pycolfin.validate_user_id(valid_user_id)
        except Exception as e:
            import pdb; pdb.set_trace()
            assert False
        else:
            assert True

    def test_invalid_user_id(self):
        """
        Raise exception if the user ID did not follow the correct format
        """
        invalid_user_ids = [
            '1234-45678',
            'invalid_user_id',
        ]

        for user_id in invalid_user_ids:
            try:
                pycolfin.validate_user_id(user_id)
            except Exception as e:
                assert True
            else:
                assert False
