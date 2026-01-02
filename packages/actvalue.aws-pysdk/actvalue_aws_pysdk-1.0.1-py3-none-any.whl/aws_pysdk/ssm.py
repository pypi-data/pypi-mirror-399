import os
from typing import List, TypedDict
from aws_pysdk.session import ssm_provider

class ParameterConfig(TypedDict):
    name: str
    env_var_name: str
    decrypt: bool

def ssm_load_parameters(parameters_list: List[ParameterConfig]) -> None:
    """Load parameters into env variables using AWS Lambda Powertools
    
    Args:
        parameters_list: List of dictionaries with 'name', 'env_var_name' and 'decrypt' keys
    
    Example:
        >>> # Define parameters to load
        >>> params = [
        ...     {'name': '/app/lambda/function_name', 'env_var_name': 'LAMBDA_NAME', 'decrypt': False},
        ...     {'name': '/app/api/secret_key', 'env_var_name': 'API_SECRET', 'decrypt': True}
        ... ]
        >>> # Load parameters into environment variables
        >>> ssm_load_parameters(params)
        >>> # Now you can access them via os.environ
        >>> redis_url = os.environ['API_SECRET']
        >>> lambda_name = os.environ['LAMBDA_NAME']
    """

    for param in parameters_list:
        param_name = param['name']
        decrypt = param.get('decrypt', False)
        env_var_name = param['env_var_name'].upper()
        
        value = ssm_provider.get(param_name, decrypt=decrypt, max_age=-1)
        os.environ[env_var_name] = str(value) if value is not None else ''
