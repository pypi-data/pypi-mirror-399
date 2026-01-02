import json
from typing import Optional, Any
from aws_pysdk.session import lambda_client

def lambda_invoke(function_name: str, payload: Optional[dict] = None) -> dict:
    """Invoke a Lambda function asynchronously (Event invocation type).
    
    This function triggers a Lambda execution without waiting for the response.
    
    Args:
        function_name (str): Name or ARN of the Lambda function to invoke
        payload (Optional[dict]): Dictionary payload to send to the function. Defaults to empty dict.
    
    Returns:
        dict: Response from Lambda invoke operation with StatusCode
        
    Raises:
        botocore.exceptions.ClientError: If function does not exist or access denied
        
    Example:
        >>> lambda_invoke('my-function', {'key': 'value'})
        >>> lambda_invoke('arn:aws:lambda:region:account:function:my-function', {})
    """
    payload_data = payload or {}
    
    return lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload_data).encode('utf-8')
    )

def lambda_invoke_with_response(function_name: str, payload: Optional[dict] = None) -> Optional[Any]:
    """Invoke a Lambda function synchronously and wait for response.
    
    This function triggers a Lambda execution and waits for the result.
    
    Args:
        function_name (str): Name or ARN of the Lambda function to invoke
        payload (Optional[dict]): Dictionary payload to send to the function. Defaults to empty dict.
    
    Returns:
        Optional[Any]: Parsed JSON response from the Lambda function, or None if no payload returned
        
    Raises:
        botocore.exceptions.ClientError: If function does not exist or access denied
        json.JSONDecodeError: If response payload is not valid JSON
        
    Example:
        >>> response = lambda_invoke_with_response('my-function', {'key': 'value'})
        >>> if response:
        ...     print(response)
        >>> result = lambda_invoke_with_response('arn:aws:lambda:region:account:function:my-function')
    """
    payload_data = payload or {}
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload_data).encode('utf-8')
    )
    
    if 'Payload' in response:
        payload_bytes = response['Payload'].read()
        return json.loads(payload_bytes.decode('utf-8')) if payload_bytes else None
    
    return None
