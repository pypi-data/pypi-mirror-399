import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey


def create_encrypted_payment_token(
    card_number: str,
    base64_encoded_public_key: str,
    terminal_id: str,
    track_id: str,
    key_id: str,
) -> str:
    """Create an encrypted payment token for guest orders.

    The encrypted payment token is used to securely submit credit card
    information for guest orders (non-registered orders). It encrypts the
    sensitive card data using Best Buy's public encryption key.

    Args:
        card_number: Credit card number (digits only, no spaces or dashes)
        base64_encoded_public_key: Base64-encoded RSA public key from
            /commerce/encryptionkey endpoint
        terminal_id: Terminal ID from /commerce/encryptionkey endpoint
        track_id: Track ID from /commerce/encryptionkey endpoint
        key_id: Key ID from /commerce/encryptionkey endpoint

    Returns:
        Encrypted payment token in format "A:B:C:D" where:
        - A: RSA/OAEP encrypted (terminalId + cardNumber)
        - B: trackId
        - C: keyId
        - D: Masked card number (first 6 + zeros + last 4)

    Raises:
        ValueError: If card_number is invalid or encryption fails

    Example:
        >>> token = create_encrypted_payment_token(
        ...     card_number="5424180279791773",
        ...     base64_encoded_public_key="MIIBIjANBg...",
        ...     terminal_id="00960001",
        ...     track_id="track123",
        ...     key_id="key456"
        ... )
        >>> # Returns: "base64_encrypted_data:track123:key456:5424180000001773"
    """
    if not card_number.isdigit():
        raise ValueError("Card number must contain only digits")
    if len(card_number) < 13 or len(card_number) > 19:
        raise ValueError("Card number must be between 13 and 19 digits")
    # Part A: Encrypt terminalId + cardNumber using RSA/OAEP
    plaintext = f"{terminal_id}{card_number}"
    # Decode the base64 public key
    public_key_bytes = base64.b64decode(base64_encoded_public_key)
    # Load the public key
    public_key = serialization.load_der_public_key(
        public_key_bytes, backend=default_backend()
    )
    if not isinstance(public_key, RSAPublicKey):
        raise ValueError("Expected RSA public key for encryption")
    # Encrypt using RSA with OAEP padding
    encrypted = public_key.encrypt(
        plaintext.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    # Base64 encode the encrypted data
    encrypted_base64 = base64.b64encode(encrypted).decode("utf-8")
    # Part B: trackId (as-is)
    part_b = track_id
    # Part C: keyId (as-is)
    part_c = key_id
    # Part D: Mask card number - keep first 6 and last 4 digits, zero the rest
    masked_card = mask_card_number(card_number)
    # Concatenate all parts with ':'
    return f"{encrypted_base64}:{part_b}:{part_c}:{masked_card}"


def mask_card_number(card_number: str) -> str:
    """Mask a credit card number, keeping only first 6 and last 4 digits.

    Args:
        card_number: Credit card number (digits only)

    Returns:
        Masked card number with first 6 and last 4 digits visible

    Example:
        >>> mask_card_number("5424180279791773")
        '5424180000001773'
    """
    if not card_number.isdigit():
        raise ValueError("Card number must contain only digits")
    if len(card_number) >= 10:
        return card_number[:6] + "0" * (len(card_number) - 10) + card_number[-4:]
    else:
        return card_number[:6] + "0" * (len(card_number) - 6)
