import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from aws_pysdk.s3 import (
    s3_write, s3_read, s3_read_to_string,
    s3_copy, s3_list_objects, s3_delete_objects
)

@pytest.fixture
def mock_s3():
    with patch('aws_pysdk.s3.s3') as mock:
        yield mock

def test_s3_write(mock_s3):
    mock_s3.put_object.return_value = {'ETag': '"123"'}
    
    response = s3_write('test-bucket', 'test.txt', 'content', 'text/plain')
    
    mock_s3.put_object.assert_called_with(
        Bucket='test-bucket',
        Key='test.txt',
        Body='content',
        ContentType='text/plain'
    )
    assert response['ETag'] == '"123"'

def test_s3_read(mock_s3):
    mock_response = {'Body': MagicMock()}
    mock_s3.get_object.return_value = mock_response
    
    response = s3_read('test-bucket', 'test.txt')
    
    mock_s3.get_object.assert_called_with(
        Bucket='test-bucket',
        Key='test.txt'
    )
    assert response == mock_response

def test_s3_read_to_string(mock_s3):
    mock_body = MagicMock()
    mock_body.read.return_value = b'test content'
    mock_s3.get_object.return_value = {'Body': mock_body}
    
    result = s3_read_to_string('test-bucket', 'test.txt')
    
    assert result == 'test content'

def test_s3_copy(mock_s3):
    mock_s3.copy_object.return_value = {'CopyObjectResult': {}}
    
    response = s3_copy('source-bucket', 'source.txt',
                      'dest-bucket', 'dest.txt')
    
    mock_s3.copy_object.assert_called_with(
        CopySource={'Bucket': 'source-bucket', 'Key': 'source.txt'},
        Bucket='dest-bucket',
        Key='dest.txt'
    )

def test_s3_list_objects(mock_s3):
    mock_s3.list_objects_v2.return_value = {
        'Contents': [
            {'Key': 'file1.txt'},
            {'Key': 'file2.txt'}
        ]
    }
    
    result = s3_list_objects('test-bucket', 'prefix/')
    
    mock_s3.list_objects_v2.assert_called_with(
        Bucket='test-bucket',
        Prefix='prefix/'
    )
    assert result == ['file1.txt', 'file2.txt']

def test_s3_delete_objects(mock_s3):
    mock_s3.delete_objects.return_value = {
        'Deleted': [{'Key': 'file1.txt'}],
        'Errors': []
    }
    
    response = s3_delete_objects('test-bucket', ['file1.txt'])
    
    mock_s3.delete_objects.assert_called_with(
        Bucket='test-bucket',
        Delete={'Objects': [{'Key': 'file1.txt'}]}
    )
    assert len(response['Deleted']) == 1
    assert len(response['Errors']) == 0

def test_s3_read_error(mock_s3):
    mock_s3.get_object.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchKey', 'Message': 'Not Found'}},
        'GetObject'
    )
    
    with pytest.raises(ClientError):
        s3_read('test-bucket', 'nonexistent.txt')