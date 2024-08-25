import pytest
from unittest.mock import Mock
from edgar.main import get_forms
from tests.conftest import mock_cik, mock_ticker, mock_form, mock_form_endpoint


def test_get_forms_success(response, patch_endpoints):
    result = get_forms(mock_cik, mock_ticker, mock_form)
    assert result == [
        f'{mock_form_endpoint}/{mock_cik}/{mock_cik}21000123/form10-k.htm'
    ]


def test_get_forms_no_filings(response, patch_endpoints):
    response.json.return_value = {'filings': {'recent': {}}}
    result = get_forms(mock_cik, mock_ticker, mock_form)
    assert result == []


def test_get_forms_http_error(mocker, patch_endpoints):
    mock_response = Mock()
    mock_response.status_code = 404
    mocker.patch('httpx.get', return_value=mock_response)
    with pytest.raises(AssertionError):
        get_forms(mock_cik, mock_ticker, mock_form)
