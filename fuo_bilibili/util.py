from datetime import timedelta


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


def format_timedelta_to_hms(td: timedelta) -> str:
    ss = int(td.total_seconds())
    mm = int(ss / 60)
    ss -= mm * 60
    hh = 0
    if mm >= 60:
        hh = int(mm / 60)
        mm -= hh * 60
    result = [str(mm).zfill(2), str(ss).zfill(2)]
    if hh > 0:
        result.insert(0, str(hh).zfill(2))
    return ':'.join(result)


if __name__ == '__main__':
    print(format_timedelta_to_hms(timedelta(seconds=127)))
