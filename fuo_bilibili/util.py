def rsa_encrypt(text: str, public_key: str) -> str:
    """
    RSA公钥加密
    :param text:
    :param public_key:
    :return:
    """
    import base64
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_v1_5
    key = RSA.import_key(public_key.encode())
    encrypted = PKCS1_v1_5.new(key).encrypt(text.encode())
    return base64.b64encode(encrypted).decode()
