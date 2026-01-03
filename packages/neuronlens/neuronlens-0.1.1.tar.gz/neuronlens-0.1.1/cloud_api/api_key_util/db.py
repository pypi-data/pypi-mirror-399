"""
Database connection and API key validation utilities.
Uses direct PostgreSQL connection via psycopg2.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional
import logging
import hashlib
import base64

logger = logging.getLogger(__name__)

def hash_api_key(api_key: str) -> str:
    """Hash API key using SHA256 and base64 URL-safe encoding."""
    sha = hashlib.sha256(api_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(sha).decode("utf-8").rstrip("=")

def get_db_connection():
    """Get PostgreSQL database connection from DATABASE_URL environment variable."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key against the database.
    
    Checks:
    - Key exists in apikey table
    - enabled field is True
    - expiresAt is None or in the future
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    try:
        # Hash the API key before comparing with database
        hashed_key = hash_api_key(api_key)
        
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Query the apikey table (mapped from Prisma schema)
                # Note: Database stores hashed keys, so we compare hashed values
                cur.execute("""
                    SELECT key, enabled, "expiresAt"
                    FROM apikey
                    WHERE key = %s
                """, (hashed_key,))
                
                result = cur.fetchone()
                
                if not result:
                    logger.debug(f"API key not found: {api_key[:10]}...")
                    return False
                
                # Check if enabled
                if not result.get('enabled', False):
                    logger.debug(f"API key is disabled: {api_key[:10]}...")
                    return False
                
                # Check expiration if set
                expires_at = result.get('expiresAt')
                if expires_at:
                    # Compare with current time (PostgreSQL returns timezone-aware datetimes)
                    # Convert to naive datetime if needed for comparison
                    if expires_at.tzinfo:
                        now = datetime.now(expires_at.tzinfo)
                    else:
                        now = datetime.utcnow()
                    if expires_at < now:
                        logger.debug(f"API key has expired: {api_key[:10]}...")
                        return False
                
                logger.debug(f"API key validated successfully: {api_key[:10]}...")
                return True
                
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        # In case of database error, fail securely (deny access)
        return False


