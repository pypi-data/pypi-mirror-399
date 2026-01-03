"""
Validate auth from event.
"""
import json
import os
import base64
import jwt
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from optikka_design_data_layer.logger import logger
from optikka_design_data_layer.errors import AuthValidationError


secrets_client = boto3.client("secretsmanager")
jwt_secret_cache = None  # Cache for JWT secret to avoid repeated retrievals

def get_jwt_secret(jwt_secret_arn: str) -> str:
    """
    Retrieve the JWT secret from AWS Secrets Manager or use a dummy secret
    for local development.

    Args:
        jwt_secret_arn (str): The ARN of the secret in AWS Secrets Manager.

    Returns:
        str: The JWT secret string.
    """
    global jwt_secret_cache
    if jwt_secret_cache is None:
        # Use dummy secret for local development
        if os.getenv("AWS_SAM_LOCAL") == "true":
            jwt_secret_cache = "dummy-jwt-secret-for-local-development-only"
        else:
            response = secrets_client.get_secret_value(SecretId=jwt_secret_arn)
            jwt_secret_cache = response["SecretString"]
    return jwt_secret_cache

class AuthValidator:
    """Validator for authentication headers using AWS Secret Manager"""

    def __init__(
        self,
        header_key: str = "Authorization",
        jwt_secret_arn: str = "",
        jwt_algorithm: str = "",
        jwt_audience: str = "",
        jwt_issuer: str = "",
    ) -> None:
        """
        Initialize the auth validator
        
        Args:
            header_key: Name of the header to validate (default: "Authorization")
            jwt_secret_arn: ARN of the JWT secret in AWS Secrets Manager
            jwt_algorithm: Algorithm used to sign the JWT
            jwt_audience: Audience of the JWT
            jwt_issuer: Issuer of the JWT
        """
        self.header_key = header_key
        self.jwt_secret_arn = jwt_secret_arn
        self.jwt_algorithm = jwt_algorithm
        self.jwt_audience = jwt_audience
        self.jwt_issuer = jwt_issuer

    def validate_auth_header(self, event: Dict[str, Any]) -> bool:
        """
        Validate that the auth header exists and matches the expected value
        
        Args:
            event: Lambda event payload
            
        Returns:
            True if auth header is valid, False otherwise
            
        Raises:
            AuthValidationError: If validation fails due to configuration issues
        """
        try:
            # Extract headers from the event
            headers = self._extract_headers(event)
            if not headers:
                logger.warning("No headers found in event")
                return False

            # Check if the required header exists
            if self.header_key.lower() not in [key.lower() for key in headers.keys()]:
                logger.warning(f"Required header '{self.header_key}' not found in event")
                return False

            headers_lower = {key.lower(): value for key, value in headers.items()}
            # Get the actual auth value from the event
            token = headers_lower[self.header_key.lower()]
            token = token.replace("Bearer ", "")
            payload = self._validate_token(
                token,
            )
            if payload is None:
                logger.warning("Invalid token")
                return False
            return True

        except AuthValidationError as e:
            # Re-raise AuthValidationError as-is
            raise AuthValidationError(f"Auth validation error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during auth validation: {str(e)}")
            raise AuthValidationError(f"Unexpected error during auth validation: {str(e)}") from e

    def _extract_headers(self, event: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract headers from Lambda event
        
        Args:
            event: Lambda event payload
            
        Returns:
            Dictionary of headers
        """
        headers = {}

        # Handle API Gateway events
        if 'headers' in event:
            headers = event['headers']
        elif 'requestContext' in event and 'http' in event.get('requestContext', {}):
            # API Gateway v2 format
            headers = event.get('headers', {})
        elif 'Records' in event:
            # SQS/SNS events might have headers in a different format
            # This is a simplified version - adjust based on your specific event structure
            headers = {}

        # Convert header keys to lowercase for case-insensitive comparison
        return {k.lower(): v for k, v in headers.items()}

    def get_auth_header_value(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Get the auth header value from the event
        
        Args:
            event: Lambda event payload
            
        Returns:
            The auth header value if present, None otherwise
        """
        headers = self._extract_headers(event)
        return headers.get(self.header_key.lower())

    def _validate_token(
        self,
        token: str,
    ) -> dict | None:
        """
        Validate and decode a JWT token.

        Args:
            self: The instance of the class.
            token (str): The JWT token to validate.

        Returns:
            dict | None: The decoded payload if valid, otherwise None.
        """
        try:
            jwt_secret = get_jwt_secret(self.jwt_secret_arn)
            jwt_payload = jwt.decode(
                token, key=jwt_secret, algorithms=[self.jwt_algorithm], audience=self.jwt_audience, issuer=self.jwt_issuer
            )
            return jwt_payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


def validate_auth_from_event(
        event: Dict[str, Any],
        header_key: str = "Authorization",
        jwt_secret_arn: str = "",
        jwt_algorithm: str = "",
        jwt_audience: str = "",
        jwt_issuer: str = "",
    ) -> bool:
    """
    Convenience function to validate auth header from Lambda event
    
    Args:
        event: Lambda event payload
        jwt_secret_arn: ARN of the JWT secret in AWS Secrets Manager
        jwt_algorithm: Algorithm used to sign the JWT
        jwt_audience: Audience of the JWT
        jwt_issuer: Issuer of the JWT
        header_key: Name of the header to validate (default: "Authorization")        
    Returns:
        True if auth header is valid, False otherwise
        
    Raises:
        AuthValidationError: If validation fails due to configuration issues
    """
    validator = AuthValidator(
        header_key=header_key,
        jwt_secret_arn=jwt_secret_arn,
        jwt_algorithm=jwt_algorithm,
        jwt_audience=jwt_audience,
        jwt_issuer=jwt_issuer,
    )
    return validator.validate_auth_header(
        event,
    )
