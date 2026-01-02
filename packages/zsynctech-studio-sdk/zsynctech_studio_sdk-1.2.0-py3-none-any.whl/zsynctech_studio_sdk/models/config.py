from typing import Optional, List
from pydantic import BaseModel, Field
from enum import StrEnum
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class InputOutputTypes(StrEnum):
    FTP = 'FTP'
    API = 'API'
    QUEUE = 'QUEUE'


def decrypt(ciphertext: str, encryption_key: str) -> str:
    """Decrypts a Base64-encoded ciphertext string using AES-256-GCM.

    Args:
        ciphertext (str): The Base64-encoded string containing IV, authentication tag, and ciphertext.
        encryption_key (str): The hexadecimal encryption key.

    Returns:
        str: The decrypted plaintext string.
    """
    key: bytes = bytes.fromhex(encryption_key)
    data: bytes = base64.b64decode(ciphertext)

    iv: bytes = data[:12]
    auth_tag: bytes = data[12:28]
    encrypted: bytes = data[28:]

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, auth_tag),
        backend=default_backend()
    ).decryptor()

    decrypted: bytes = decryptor.update(encrypted) + decryptor.finalize()
    return decrypted.decode("utf-8")


class Credential(BaseModel):
    key: str
    value: str
    encrypted: bool


class ExecutionParameters(BaseModel):
    """Parameters received from the platform when starting an execution.

    Contains all runtime configuration and credentials needed for the robot to execute.
    """
    instanceId: str
    executionId: str
    automationName: Optional[str] = "System"
    instanceCode: Optional[str] = "System"
    clientId: Optional[str] = None
    userId: Optional[str] = "System"
    outputPath: Optional[str] = None
    inputPath: Optional[str] = None
    inputMetaData: Optional[dict] = None
    inputType: Optional[InputOutputTypes] = InputOutputTypes.FTP
    outputType: Optional[InputOutputTypes] = InputOutputTypes.FTP
    outputMetaData: Optional[dict] = None
    keepAlive: Optional[bool] = False
    keepAliveInterval: Optional[int] = 30
    credentials: Optional[List[Credential]] = None
    encryption_key: Optional[str] = Field(default=None, exclude=True, repr=False)

    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential value by key.

        If the credential is encrypted, it will be decrypted automatically.

        Args:
            key (str): The credential key (e.g., 'username', 'password').

        Returns:
            Optional[str]: The credential value (decrypted if needed) or None if not found.
        """
        if not self.credentials:
            return None

        for cred in self.credentials:
            if cred.key == key:
                if cred.encrypted and self.encryption_key:
                    return decrypt(cred.value, self.encryption_key)
                return cred.value
        return None


# Backward compatibility alias
Config = ExecutionParameters
