from typing import Union, Optional, Literal
from botocore.client import Config
from aws_pysdk.session import session, s3

def s3_write(bucket: str, 
            key: str, 
            body: Union[bytes, str],
            content_type: Optional[str] = None,
            content_encoding: Optional[str] = None) -> dict:
    """Write an object to S3 bucket with optional content type and encoding.
    
    Args:
        bucket (str): Name of the S3 bucket
        key (str): Object key/path in the bucket
        body (Union[bytes, str]): Content to write to S3
        content_type (Optional[str]): MIME type of the content (e.g. 'text/plain')
        content_encoding (Optional[str]): Content encoding (e.g. 'gzip')
    
    Returns:
        dict: Response from S3 put_object operation
        
    Example:
        >>> s3_write('my-bucket', 'path/to/file.txt', 'Hello World', 'text/plain')
    """
    params = {
        'Bucket': bucket,
        'Key': key,
        'Body': body
    }
    
    if content_type:
        params['ContentType'] = content_type
    if content_encoding:
        params['ContentEncoding'] = content_encoding
        
    return s3.put_object(**params)

def s3_read(bucket: str, key: str) -> dict:
    """Read raw object data from S3 bucket.
    
    Args:
        bucket (str): Name of the S3 bucket
        key (str): Object key/path in the bucket
    
    Returns:
        dict: Response from S3 get_object operation including 'Body' with raw data
        
    Raises:
        botocore.exceptions.ClientError: If object does not exist or access denied
        
    Example:
        >>> response = s3_read('my-bucket', 'path/to/file.txt')
        >>> content = response['Body'].read()
    """
    return s3.get_object(Bucket=bucket, Key=key)

def s3_read_to_string(bucket: str, key: str) -> Optional[str]:
    """Read an object from S3 and decode content as UTF-8 string.
    
    Args:
        bucket (str): Name of the S3 bucket
        key (str): Object key/path in the bucket
    
    Returns:
        Optional[str]: UTF-8 decoded content of the object if successful, None if error occurs
        
    Example:
        >>> content = s3_read_to_string('my-bucket', 'path/to/file.txt')
        >>> if content:
        ...     print(content)
    """
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')
    except Exception:
        return None

def s3_copy(source_bucket: str, source_key: str,
            dest_bucket: str, dest_key: str) -> dict:
    """Copy an object from one S3 location to another.
    
    Args:
        source_bucket (str): Source bucket name
        source_key (str): Source object key
        dest_bucket (str): Destination bucket name
        dest_key (str): Destination object key
    
    Returns:
        dict: Response from S3 copy_object operation
        
    Raises:
        ValueError: If source and destination are identical
        botocore.exceptions.ClientError: If copy operation fails
        
    Example:
        >>> s3_copy('source-bucket', 'source/path.txt',
        ...         'dest-bucket', 'dest/path.txt')
    """
    if source_bucket == dest_bucket and source_key == dest_key:
        raise ValueError('Cannot copy on itself!')
    
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    return s3.copy_object(
        CopySource=copy_source,
        Bucket=dest_bucket,
        Key=dest_key
    )

def s3_list_objects(bucket: str, prefix: str = '') -> list:
    """List objects in an S3 bucket with optional prefix filter.
    
    Args:
        bucket (str): Name of the S3 bucket
        prefix (str, optional): Filter results to objects beginning with prefix. Defaults to ''.
    
    Returns:
        list: List of object keys matching the prefix
        
    Raises:
        botocore.exceptions.ClientError: If bucket does not exist or access denied
        
    Example:
        >>> # List all objects in bucket
        >>> all_objects = s3_list_objects('my-bucket')
        >>> # List objects in specific folder
        >>> folder_objects = s3_list_objects('my-bucket', 'folder/')
    """
    params = {'Bucket': bucket}
    if prefix:
        params['Prefix'] = prefix
    response = s3.list_objects_v2(**params)
    return [obj['Key'] for obj in response.get('Contents', [])]

def s3_delete_objects(bucket: str, keys: list) -> dict:
    """Delete multiple objects from an S3 bucket in a single request.
    
    Args:
        bucket (str): Name of the S3 bucket
        keys (list): List of object keys to delete
    
    Returns:
        dict: Response from S3 delete_objects operation containing 'Deleted' and 'Errors' lists
        
    Raises:
        botocore.exceptions.ClientError: If bucket does not exist or access denied
        
    Example:
        >>> # Delete multiple files
        >>> response = s3_delete_objects('my-bucket', 
        ...                             ['file1.txt', 'file2.txt'])
        >>> print(f"Deleted: {len(response['Deleted'])}")
        >>> print(f"Errors: {len(response['Errors'])}")
    """
    objects = [{'Key': key} for key in keys]
    return s3.delete_objects(
        Bucket=bucket,
        Delete={'Objects': objects}
    )

def s3_get_signed_url(
    params: dict,
    operation: Literal['READ', 'WRITE'],
    expires: int = 60
) -> str:
    """
    Generate a signed URL for S3 operations
    
    Args:
        params: Dict containing Bucket and Key (and optionally ContentType)
        operation: Either 'READ' or 'WRITE'
        expires: URL expiration time in seconds
        
    Returns:
        str: Signed URL for the requested operation

    # Example
        >>> params = {
        >>>    'Bucket': 'my-bucket',
        >>>    'Key': 'my-file.txt',
        >>>    'ContentType': 'text/plain'  # optional
        >>> }
        >>> # Get a read URL
        >>> read_url = s3_get_signed_url(params, 'READ', 3600)  # expires in 1 hour
        >>> # Get a write URL
        >>> write_url = s3_get_signed_url(params, 'WRITE', 3600)  # expires in 1 hour
    """
    # Configure the client with signing
    s3_client = session.client(
        's3',
        config=Config(signature_version='s3v4')
    )
    
    # Set the HTTP method based on operation
    client_method = 'get_object' if operation == 'READ' else 'put_object'
    
    # Generate the URL
    url_params = {
        'Bucket': params['Bucket'],
        'Key': params['Key']
    }
    
    # Add ContentType if present
    if 'ContentType' in params:
        url_params['ContentType'] = params['ContentType']
    
    url = s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params=url_params,
        ExpiresIn=expires
    )
    
    return url
