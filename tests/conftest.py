import pytest
from unittest.mock import patch, Mock

# Mock data
mock_cik = '0000000000'
mock_ticker = 'ABC'
mock_form = '10-K'
mock_submission_endpoint = 'https://test.com'
mock_form_endpoint = 'https://test.com/forms'
mock_api_headers = {'User-Agent': 'test-agent'}

mock_response_data = {
    'filings': {
        'recent': {
            'form': ['10-K', '10-Q'],
            'accessionNumber': [f'{mock_cik}-21-000123', f'{mock_cik}-21-000321'],
            'primaryDocument': ['form10-k.htm', 'form10-q.htm'],
        }
    }
}


@pytest.fixture
def response(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mocker.patch('httpx.get', return_value=mock_response)
    return mock_response


@pytest.fixture
def patch_endpoints():
    with (
        patch('edgar.main.submission_endpoint', mock_submission_endpoint),
        patch('edgar.main.form_endpoint', mock_form_endpoint),
        patch('edgar.main.api_headers', mock_api_headers),
    ):
        yield
