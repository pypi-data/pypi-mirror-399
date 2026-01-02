import pytest
import os
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from aws_pysdk.ssm import ssm_load_parameters, ParameterConfig

@pytest.fixture
def mock_ssm_provider():
    with patch('aws_pysdk.ssm.ssm_provider') as mock:
        yield mock

@pytest.fixture
def clean_env():
    """Clean up environment variables after each test"""
    original_env = dict(os.environ)
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

def test_ssm_load_parameters_basic(mock_ssm_provider, clean_env):
    """Test basic parameter loading functionality"""
    # Mock SSM responses
    mock_ssm_provider.get.side_effect = [
        'test-lambda-name',
        'secret-api-key'
    ]
    
    parameters: list[ParameterConfig] = [
        {'name': '/app/lambda/function_name', 'env_var_name': 'LAMBDA_NAME', 'decrypt': False},
        {'name': '/app/api/secret_key', 'env_var_name': 'API_SECRET', 'decrypt': True}
    ]
    
    ssm_load_parameters(parameters)
    
    # Verify SSM calls
    assert mock_ssm_provider.get.call_count == 2
    mock_ssm_provider.get.assert_any_call('/app/lambda/function_name', decrypt=False, max_age=-1)
    mock_ssm_provider.get.assert_any_call('/app/api/secret_key', decrypt=True, max_age=-1)
    
    # Verify environment variables
    assert os.environ['LAMBDA_NAME'] == 'test-lambda-name'
    assert os.environ['API_SECRET'] == 'secret-api-key'

def test_ssm_load_parameters_with_none_value(mock_ssm_provider, clean_env):
    """Test handling of None values from SSM"""
    mock_ssm_provider.get.return_value = None
    
    parameters: list[ParameterConfig] = [
        {'name': '/app/missing/param', 'env_var_name': 'MISSING_PARAM', 'decrypt': False}
    ]
    
    ssm_load_parameters(parameters)
    
    # Should set empty string for None values
    assert os.environ['MISSING_PARAM'] == ''

def test_ssm_load_parameters_case_insensitive_env_var(mock_ssm_provider, clean_env):
    """Test that environment variable names are converted to uppercase"""
    mock_ssm_provider.get.return_value = 'test-value'
    
    parameters: list[ParameterConfig] = [
        {'name': '/app/test', 'env_var_name': 'lowercase_var', 'decrypt': False}
    ]
    
    ssm_load_parameters(parameters)
    
    # Should convert to uppercase
    assert os.environ['LOWERCASE_VAR'] == 'test-value'

def test_ssm_load_parameters_mixed_decrypt_settings(mock_ssm_provider, clean_env):
    """Test loading parameters with different decrypt settings"""
    mock_ssm_provider.get.side_effect = ['plain-value', 'encrypted-value']
    
    parameters: list[ParameterConfig] = [
        {'name': '/app/plain', 'env_var_name': 'PLAIN_VAR', 'decrypt': False},
        {'name': '/app/encrypted', 'env_var_name': 'ENCRYPTED_VAR', 'decrypt': True}
    ]
    
    ssm_load_parameters(parameters)
    
    # Verify correct decrypt parameters
    mock_ssm_provider.get.assert_any_call('/app/plain', decrypt=False, max_age=-1)
    mock_ssm_provider.get.assert_any_call('/app/encrypted', decrypt=True, max_age=-1)
    
    assert os.environ['PLAIN_VAR'] == 'plain-value'
    assert os.environ['ENCRYPTED_VAR'] == 'encrypted-value'

def test_ssm_load_parameters_numeric_value(mock_ssm_provider, clean_env):
    """Test handling of numeric values from SSM"""
    mock_ssm_provider.get.return_value = 12345
    
    parameters: list[ParameterConfig] = [
        {'name': '/app/port', 'env_var_name': 'PORT', 'decrypt': False}
    ]
    
    ssm_load_parameters(parameters)
    
    # Should convert to string
    assert os.environ['PORT'] == '12345'

def test_ssm_load_parameters_empty_list(mock_ssm_provider, clean_env):
    """Test loading empty parameter list"""
    ssm_load_parameters([])
    
    # Should not make any SSM calls
    mock_ssm_provider.get.assert_not_called()

def test_ssm_load_parameters_with_typed_dict():
    """Test that ParameterConfig TypedDict works correctly"""
    # This test verifies the type structure
    param: ParameterConfig = {
        'name': '/test/param',
        'env_var_name': 'TEST_PARAM',
        'decrypt': True
    }
    
    assert param['name'] == '/test/param'
    assert param['env_var_name'] == 'TEST_PARAM'
    assert param['decrypt'] is True
