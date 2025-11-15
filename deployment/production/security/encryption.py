"""
Encryption and Security Utilities
Provides encryption for sensitive data at rest and in transit
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from typing import Optional
import hashlib


class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            encryption_key: Base64-encoded encryption key. If not provided,
                          will use ENCRYPTION_KEY environment variable or generate new key
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            self.key = os.getenv('ENCRYPTION_KEY', self._generate_key()).encode()
        
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def _generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation. If None, generates new salt
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64-encoded encrypted data
        """
        if not data:
            return ""
        
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted string data
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Decrypted string
        """
        if not encrypted_data:
            return ""
        
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def encrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Encrypt a file
        
        Args:
            input_path: Path to file to encrypt
            output_path: Path to save encrypted file
        """
        with open(input_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.cipher.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, input_path: str, output_path: str) -> None:
        """
        Decrypt a file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to save decrypted file
        """
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted = self.cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hash password using SHA-256
        
        Args:
            password: Password to hash
            salt: Salt for hashing. If None, generates new salt
            
        Returns:
            Tuple of (hash, salt)
        """
        if salt is None:
            salt = os.urandom(32)
        
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return pwdhash.hex(), salt.hex()
    
    @staticmethod
    def verify_password(password: str, hash_hex: str, salt_hex: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Password to verify
            hash_hex: Hex-encoded password hash
            salt_hex: Hex-encoded salt
            
        Returns:
            True if password matches, False otherwise
        """
        salt = bytes.fromhex(salt_hex)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return pwdhash.hex() == hash_hex


class SecureConfig:
    """Manages secure configuration and secrets"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
    
    def get_database_url(self) -> str:
        """Get database URL from environment, decrypt if encrypted"""
        db_url = os.getenv('DATABASE_URL')
        encrypted_db_url = os.getenv('ENCRYPTED_DATABASE_URL')
        
        if encrypted_db_url:
            return self.encryption_manager.decrypt(encrypted_db_url)
        
        return db_url
    
    def get_api_key(self, service: str) -> str:
        """
        Get API key for service
        
        Args:
            service: Service name (e.g., 'huggingface', 'bhashini')
            
        Returns:
            API key
        """
        env_var = f"{service.upper()}_API_KEY"
        encrypted_env_var = f"ENCRYPTED_{env_var}"
        
        api_key = os.getenv(env_var)
        encrypted_api_key = os.getenv(encrypted_env_var)
        
        if encrypted_api_key:
            return self.encryption_manager.decrypt(encrypted_api_key)
        
        return api_key
    
    def encrypt_env_value(self, value: str) -> str:
        """Encrypt environment variable value"""
        return self.encryption_manager.encrypt(value)


# Singleton instance
_secure_config = None

def get_secure_config() -> SecureConfig:
    """Get singleton SecureConfig instance"""
    global _secure_config
    if _secure_config is None:
        _secure_config = SecureConfig()
    return _secure_config
