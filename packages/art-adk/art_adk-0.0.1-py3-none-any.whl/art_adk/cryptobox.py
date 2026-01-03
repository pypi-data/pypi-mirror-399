import logging
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import RawEncoder
from nacl.utils import random
import base64
import binascii
from .exceptions import EncryptionError, DecryptionError
logger = logging.getLogger(__name__)

class CryptoBox:
    @staticmethod
    def generate_key_pair() -> dict:
        """
        Generate a new Curve25519 key pair.
        Returns a dict with Base64-encoded 'publicKey' and 'privateKey'.
        """
        try:
            # Generate key pair
            private_key = PrivateKey.generate()
            public_key = private_key.public_key
            # Encode as raw bytes, then Base64
            private_key_raw = private_key.encode(encoder=RawEncoder)
            public_key_raw = public_key.encode(encoder=RawEncoder)
            # Convert to Base64
            private_key_b64 = base64.b64encode(private_key_raw).decode('utf-8')
            public_key_b64 = base64.b64encode(public_key_raw).decode('utf-8')
            logger.debug("Encryption key pair generated - private key: %d bytes, public key: %d bytes", 
                        len(private_key_raw), len(public_key_raw))
            return {
                "publicKey": public_key_b64,
                "privateKey": private_key_b64,
            }
        except Exception as e:
            raise EncryptionError(f"Key generation failed: {str(e)}")

    @staticmethod
    async def encrypt(data: str, recipient_public_key: str, sender_private_key: str) -> str:
        """
        Encrypts a message using the recipient's public key and sender's private key.
        """
        try:
            logger.debug("ENCRYPT DEBUG:")
            logger.debug("  Data: %s", data)
            logger.debug("  Recipient public key: %s", recipient_public_key)
            logger.debug("  Sender private key: %s", sender_private_key)

            # Decode Base64 keys to raw bytes
            try:
                sender_priv_raw = base64.b64decode(sender_private_key)
                recipient_pub_raw = base64.b64decode(recipient_public_key)
            except Exception as e:
                raise
            # Validate key lengths
            if len(recipient_pub_raw) != 32 or len(sender_priv_raw) != 32:
                raise EncryptionError(f'Invalid key length: pub={len(recipient_pub_raw)}, priv={len(sender_priv_raw)}')
            # Create PyNaCl key objects from raw bytes
            try:
                sender_priv = PrivateKey(sender_priv_raw, encoder=RawEncoder)
                recipient_pub = PublicKey(recipient_pub_raw, encoder=RawEncoder)
            except Exception as e:
                raise
            # Generate nonce
            nonce = random(Box.NONCE_SIZE)  # 24 bytes            
            # Create box and encrypt
            # IMPORTANT: In PyNaCl, Box(private_key, public_key) creates a shared secret
            # that works bidirectionally
            try:
                box = Box(sender_priv, recipient_pub)
                # PyNaCl's encrypt method returns an EncryptedMessage object
                # We need just the ciphertext without the nonce
                encrypted_msg = box.encrypt(data.encode('utf-8'), nonce)
                # Extract just the ciphertext (PyNaCl prepends the nonce, so we skip it)
                ciphertext = encrypted_msg.ciphertext
            except Exception as e:
                raise
            # Concatenate nonce + ciphertext
            full_data = nonce + ciphertext
            # Return as Base64
            result = base64.b64encode(full_data).decode('utf-8')
            logger.debug("Encryption successful - result length: %d bytes", len(result))
            return result
            
        except Exception as e:
            logger.error("Encryption failed: %s", e, exc_info=True)
            raise EncryptionError(f"Encryption failed: {str(e)}")

    @staticmethod
    async def decrypt(encrypted_data: str, sender_public_key: str, recipient_private_key: str) -> str:
        """
        Decrypts an encrypted message using the sender's public key and recipient's private key.
        - This opens a box FROM sender TO recipient
        """
        try:
            logger.debug("Decrypting data with sender public key")
            # Decode Base64 keys to raw bytes
            try:
                recipient_priv_raw = base64.b64decode(recipient_private_key)
                sender_pub_raw = base64.b64decode(sender_public_key)
            except Exception as e:
                logger.error("Failed to decode keys: %s", e)
                raise
            # Validate key lengths
            if len(sender_pub_raw) != 32 or len(recipient_priv_raw) != 32:
                raise DecryptionError(f'Invalid key length: pub={len(sender_pub_raw)}, priv={len(recipient_priv_raw)}')
            
            # Create PyNaCl key objects from raw bytes
            try:
                recipient_priv = PrivateKey(recipient_priv_raw, encoder=RawEncoder)
                sender_pub = PublicKey(sender_pub_raw, encoder=RawEncoder)
            except Exception as e:
                logger.error("Failed to create key objects: %s", e)
                raise
            
            # Decode the encrypted data
            try:
                full_data = base64.b64decode(encrypted_data)
            except Exception as e:
                logger.error("Failed to decode encrypted data: %s", e)
                raise
            
            # Validate minimum length
            if len(full_data) < Box.NONCE_SIZE:
                raise DecryptionError(f'Data too short: {len(full_data)} < {Box.NONCE_SIZE}')
            
            # Extract nonce and ciphertext
            nonce = full_data[:Box.NONCE_SIZE]  # First 24 bytes
            ciphertext = full_data[Box.NONCE_SIZE:]  # Rest is ciphertext

            logger.debug("  Extracted nonce length: %d", len(nonce))
            logger.debug("  Extracted ciphertext length: %d", len(ciphertext))
            logger.debug("  Nonce (hex): %s", binascii.hexlify(nonce).decode())
            logger.debug("  Ciphertext (hex): %s", binascii.hexlify(ciphertext).decode())

            # Create box and decrypt
            # IMPORTANT: Box needs to be created with the same pair of keys
            # For decryption, we need Box(recipient_priv, sender_pub)
            try:
                box = Box(recipient_priv, sender_pub)
                plaintext = box.decrypt(ciphertext, nonce)
                result = plaintext.decode('utf-8')
                logger.debug("Decryption successful: %s", result)
                return result
            except Exception as e:
                logger.error("Box decryption failed")
                raise

        except Exception as e:
            logger.error("Decryption failed: %s", e)
            raise DecryptionError(f"Decryption failed: {str(e)}")