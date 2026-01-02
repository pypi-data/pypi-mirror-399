import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import sys
from pathlib import Path
import json

# Add src to path
src_path = str(Path(__file__).parent.parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from aws_pysdk.lambda_module import lambda_invoke, lambda_invoke_with_response

@pytest.fixture
def mock_lambda():
    with patch('aws_pysdk.lambda_module.lambda_client') as mock:
        yield mock

def test_lambda_invoke(mock_lambda):
    mock_lambda.invoke.return_value = {'StatusCode': 202}
    
    response = lambda_invoke('test-function', {'key': 'value'})
    
    mock_lambda.invoke.assert_called_with(
        FunctionName='test-function',
        InvocationType='Event',
        Payload=json.dumps({'key': 'value'}).encode('utf-8')
    )
    assert response['StatusCode'] == 202

def test_lambda_invoke_no_payload(mock_lambda):
    mock_lambda.invoke.return_value = {'StatusCode': 202}
    
    response = lambda_invoke('test-function')
    
    mock_lambda.invoke.assert_called_with(
        FunctionName='test-function',
        InvocationType='Event',
        Payload=json.dumps({}).encode('utf-8')
    )
    assert response['StatusCode'] == 202

def test_lambda_invoke_with_response(mock_lambda):
    mock_payload = MagicMock()
    mock_payload.read.return_value = json.dumps({'result': 'success'}).encode('utf-8')
    mock_lambda.invoke.return_value = {
        'StatusCode': 200,
        'Payload': mock_payload
    }
    
    result = lambda_invoke_with_response('test-function', {'key': 'value'})
    
    mock_lambda.invoke.assert_called_with(
        FunctionName='test-function',
        InvocationType='RequestResponse',
        Payload=json.dumps({'key': 'value'}).encode('utf-8')
    )
    assert result == {'result': 'success'}

def test_lambda_invoke_with_response_no_payload(mock_lambda):
    mock_payload = MagicMock()
    mock_payload.read.return_value = json.dumps({'result': 'success'}).encode('utf-8')
    mock_lambda.invoke.return_value = {
        'StatusCode': 200,
        'Payload': mock_payload
    }
    
    result = lambda_invoke_with_response('test-function')
    
    mock_lambda.invoke.assert_called_with(
        FunctionName='test-function',
        InvocationType='RequestResponse',
        Payload=json.dumps({}).encode('utf-8')
    )
    assert result == {'result': 'success'}

def test_lambda_invoke_with_response_empty_payload(mock_lambda):
    mock_payload = MagicMock()
    mock_payload.read.return_value = b''
    mock_lambda.invoke.return_value = {
        'StatusCode': 200,
        'Payload': mock_payload
    }
    
    result = lambda_invoke_with_response('test-function', {'key': 'value'})
    
    assert result is None

def test_lambda_invoke_with_response_no_payload_key(mock_lambda):
    mock_lambda.invoke.return_value = {'StatusCode': 200}
    
    result = lambda_invoke_with_response('test-function', {'key': 'value'})
    
    assert result is None

def test_lambda_invoke_error(mock_lambda):
    mock_lambda.invoke.side_effect = ClientError(
        {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Function not found'}},
        'Invoke'
    )
    
    with pytest.raises(ClientError):
        lambda_invoke('nonexistent-function', {'key': 'value'})

def test_lambda_invoke_with_response_error(mock_lambda):
    mock_lambda.invoke.side_effect = ClientError(
        {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Function not found'}},
        'Invoke'
    )
    
    with pytest.raises(ClientError):
        lambda_invoke_with_response('nonexistent-function')
