import base64
import struct
import hashlib
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# Eigene Exception-Klassen für sauberes Error-Handling
class DecryptionError(Exception):
    """Wird geworfen, wenn die Entschlüsselung fehlschlägt (z.B. falsches Passwort)."""
    pass

class InvalidDataError(Exception):
    """Wird geworfen, wenn die Eingabedaten (Base64/XML) ungültig sind."""
    pass

class FileZillaDecryptor:
    # Konstanten
    KEY_SIZE = 32
    SALT_SIZE = 32
    GCM_IV_SIZE = 12
    GCM_TAG_SIZE = 16
    PBKDF2_ITERATIONS = 100000

    @staticmethod
    def _robust_base64_decode(s: str) -> bytes:
        """Interner Helper: Bereinigt Base64 und korrigiert Padding."""
        if not s:
            return b""
        s = s.strip().replace(" ", "").replace("\n", "").replace("\r", "")
        missing_padding = len(s) % 4
        if missing_padding:
            s += '=' * (4 - missing_padding)

        try:
            return base64.b64decode(s)
        except Exception as e:
            raise InvalidDataError(f"Ungültiges Base64 Format: {e}")

    @classmethod
    def _derive_private_key(cls, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=cls.PBKDF2_ITERATIONS,
        )
        key = bytearray(kdf.derive(password.encode('utf-8')))
        # Key Clamping (X25519 Anforderung)
        key[0] &= 248
        key[31] &= 127
        key[31] |= 64
        return bytes(key)

    @staticmethod
    def _hash_accumulator(parts):
        h = hashlib.sha256()
        for part in parts:
            if isinstance(part, int):
                h.update(struct.pack('>B', part))
            else:
                h.update(part)
        return h.digest()

    @classmethod
    def decrypt(cls, master_password: str, xml_pubkey: str, xml_pass: str) -> str:
        """
        Hauptfunktion zum Entschlüsseln.

        :param master_password: Das Master-Passwort des Users.
        :param xml_pubkey: Der Inhalt des <pubkey> Tags.
        :param xml_pass: Der Inhalt des <Pass> Tags (verschlüsselt).
        :return: Das entschlüsselte Passwort als String.
        :raises InvalidDataError: Bei ungültigen Eingabedaten.
        :raises DecryptionError: Bei falschem Master-Passwort.
        """
        try:
            # 1. Base64 Inputs bereinigen
            stored_pub_blob = cls._robust_base64_decode(xml_pubkey)
            cipher_blob = cls._robust_base64_decode(xml_pass)

            expected_pub_len = cls.KEY_SIZE + cls.SALT_SIZE
            if len(stored_pub_blob) != expected_pub_len:
                raise InvalidDataError(f"PubKey Länge ungültig. Erwartet: {expected_pub_len}, Bekommen: {len(stored_pub_blob)}")

            my_salt = stored_pub_blob[cls.KEY_SIZE:]
            stored_public_key = stored_pub_blob[:cls.KEY_SIZE]

            # 2. Key Derivation
            my_priv_bytes = cls._derive_private_key(master_password, my_salt)

            # 3. Blob Parsing
            overhead = cls.KEY_SIZE + cls.SALT_SIZE + cls.GCM_TAG_SIZE
            if len(cipher_blob) < overhead:
                raise InvalidDataError("Ciphertext zu kurz (beschädigt?).")

            ephemeral_key_bytes = cipher_blob[:cls.KEY_SIZE]
            ephemeral_salt = cipher_blob[cls.KEY_SIZE : cls.KEY_SIZE + cls.SALT_SIZE]
            encrypted_data = cipher_blob[cls.KEY_SIZE + cls.SALT_SIZE : -cls.GCM_TAG_SIZE]
            tag = cipher_blob[-cls.GCM_TAG_SIZE:]

            # 4. ECDH Shared Secret
            my_priv = x25519.X25519PrivateKey.from_private_bytes(my_priv_bytes)
            ephemeral_pub = x25519.X25519PublicKey.from_public_bytes(ephemeral_key_bytes)
            shared_secret = my_priv.exchange(ephemeral_pub)

            # 5. Ableiten von AES Key und IV
            aes_key = cls._hash_accumulator([
                ephemeral_salt, 0, shared_secret, ephemeral_key_bytes, stored_public_key, my_salt
            ])

            iv_hash = cls._hash_accumulator([
                ephemeral_salt, 2, shared_secret, ephemeral_key_bytes, stored_public_key, my_salt
            ])
            iv = iv_hash[:cls.GCM_IV_SIZE]

            # 6. Entschlüsselung
            aesgcm = AESGCM(aes_key)
            plaintext = aesgcm.decrypt(iv, encrypted_data + tag, None)

            return plaintext.decode('utf-8')

        except InvalidTag:
            # Das ist der Indikator für "Falsches Passwort" bei AES-GCM
            raise DecryptionError("Entschlüsselung fehlgeschlagen. Vermutlich falsches Master-Passwort.")
        except (ValueError, IndexError) as e:
            raise InvalidDataError(f"Verarbeitungsfehler: {str(e)}")
