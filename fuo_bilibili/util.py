import json
from datetime import timedelta
from typing import Optional


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


def json_to_lrc_text(jsons: str) -> Optional[str]:
    if jsons is None or len(jsons) == 0:
        return None
    data = json.loads(jsons)
    body = data.get('body')
    if body is None or len(body) == 0:
        return None
    lrc_lines = []
    for item in body:
        from_second = int(item['from'])
        from_ms = str(item['from'] - from_second).lstrip('0')
        from_second_str = format_timedelta_to_hms(timedelta(seconds=from_second))
        lrc_lines.append(f'[{from_second_str}{from_ms}]{item["content"]}')
    return '\n'.join(lrc_lines)


if __name__ == '__main__':
    print(format_timedelta_to_hms(timedelta(seconds=127)))
