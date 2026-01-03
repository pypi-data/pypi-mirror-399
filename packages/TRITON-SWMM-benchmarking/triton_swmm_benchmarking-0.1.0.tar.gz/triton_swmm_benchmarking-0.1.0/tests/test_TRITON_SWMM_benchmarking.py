#!/usr/bin/env python
import pytest

"""Tests for `TRITON_SWMM_benchmarking` package."""

# from TRITON_SWMM_benchmarking import TRITON_SWMM_benchmarking


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyfeldroy/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
