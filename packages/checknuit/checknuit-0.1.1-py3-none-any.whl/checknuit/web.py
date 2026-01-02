"""
HTTP helpers for interacting with nuit.at.gov.mz.
"""

from typing import Final

import requests
from requests.exceptions import RequestException

POST_URL: Final[str] = (
    "https://nuit.at.gov.mz/nuit/bootstrap/theme/work/Impressao_Carta.aspx"
)

HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": POST_URL,
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://nuit.at.gov.mz",
    "Connection": "keep-alive",
    "Cookie": "ASP.NET_SessionId=h3gexi32cro3olietan4cyli",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
}

PAYLOAD_TEMPLATE: Final[str] = (
    "rdOpcoes=C&txtNuit={nuit}&txtNuit_ClientState=%7B%22enabled%22%3Atrue%2C%22"
    "emptyMessage%22%3A%22%22%2C%22validationText%22%3A%22{nuit}%22%2C%22valueAs"
    "String%22%3A%22{nuit}%22%2C%22lastSetTextBoxValue%22%3A%22{nuit}%22%7D&t"
    "xtDataNascimentoTab2_ClientState=%7B%22enabled%22%3Afalse%2C%22emptyMessage%22"
    "%3A%22%22%2C%22validationText%22%3A%22%22%2C%22valueAsString%22%3A%22%22%2C%2"
    "2minDateStr%22%3A%221900-01-01-00-00-00%22%2C%22maxDateStr%22%3A%222099-12-31"
    "-00-00-00%22%2C%22lastSetTextBoxValue%22%3A%22%22%7D&cmdPesquisar=Pesquisar&_"
    "_EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=AKlokuXqq1vh4R2CW8n68L"
    "VqqKLKl55YRIixRKOTS1LkOHA%2B3myUpd5Vb5bMg%2BrRhBarvT7WZQ844Iy3srj2jguXs%2BlI1"
    "EgbtM30EVx2gMpZ7BaYZdG7gYEd2xsayVzWd6fboGdpfirR3TSU%2FR72Xb%2FPsCe9UlQRS1n5OU"
    "3L3W%2B20j3W2okM25qkm6Zc3GSu%2Fz0IcJ9IkSzBLrcvnrYpl6V%2BUcnXFqxb3vfMVjCg%2By"
    "%2F7iQ7aesdAgaeTzgZvnVKqsH%2Fd0scdxP0w%2FUqWO1Pk0aWWIwWvmBRndrGZmJzRmfyuCViq2"
    "cMAimH7Z0E3T57ane6F9suBPaKWi7w8pkd3DY8oMn1qcjtrAcEjYh9C1kn8ceSpZ5QzvXVc2XDbnm"
    "9bq3icq1htX5i3CA7fAwQ%2BlKr%2FPrRD4rorfQBF0LtIDLZNJtubC4ujk2UQxtshb0SSHkrRDE7"
    "aQhGVc6um3Xjs2ED4944OiQVLxG3WDs91KBWrXQIppGmEM44er50t6q%2FzZjvR6%2FkVp94JWthd"
    "xwbf2L2nCoyi2hWKg0lTsXpmLEBWyhT3BTYqLa67d1nB%2FT92bxQiD0pZ8QMprBwMCGfr3EBDLZ4"
    "NhkKEGwQFaGns9eyNYzfvWZ31Driqh1G8ZOBRo7Oo560V0LIEL8kVAKNQbDxb81GSCQou%2F1okdT"
    "cp8ovh89K2JKdjyettZssNskt8WAQ3pjjcn3QDiKeWI4qdg18XthfyjK3o0U5cFPn8TSX%2BEcLXn"
    "wq69cw7njzf0cB%2B2ryjFO6pCyvUxCByxvExBJUZRi9HF%2F03bsEPgCJBUxuMFMNpc%2BlF6XwH"
    "Ik1u9Tesqgpkzd72Ud0VG%2BXIJHlYBMeiDdPvKFxmiGspQZi420zOgLqN5b6Y2CknUYQvagoZLeK"
    "nznej9Wjjb33wPrToU8RJUwwkUEoFYHQ%2FdfbiLppzIdov2JMX%2Bu8j9o80hOICF2%2BO0aMCBX"
    "JpilCK%2BkPUT8ksF7KTsRszT4CI0VPAz5KLSUYNbLUkhekxpIaFSM6x1y3n44DYkbFXDNXXMVGl%"
    "2FIFrx8OJ8G7jHEkHuXko2EuJm4hvygWhX9QZHfi%2FPa7q6P2oHn%2F20eb2uGEAiICDTdwVWzUJ"
    "IMBeP8Zf%2BOZQI5bSFXe2IOw%2BEN0cge%2F6np9Qb2tnmNQIZ08sJF65iN3U%2FU3gapO3y0TSR"
    "R6b%2FcyzyRLshwllkC3o4wGJvC5Awtg6lrC8Rl8CmPdupSp85pZ46pEYEGIR8wubdZM8%2FypEHs"
    "MxTPbxWwriDEVRtI1liJpjezKaA%2B4ZGwr%2FkTlcbtKHQoO1JPOI7nz94tMiarzBliLMxyh0Qx7"
    "c6kq9TzwxhHfFgdCT0hOr45YsDVP3CL%2BrfQXbNIpJ8F1PE5hEVkJBpMTPYLxxTcUC3ANOsfvlDS"
    "DNXzaWSwTjVtwk518htic1HGZm5c45X44%2B0DC%2B26kP8hgVoRPxZ7HTnz0kkkY%2BjmPpiHpnC"
    "r%2BYY4MXzT12Q63Wd6Bxk8sWBDv13CbBlzj6ey%2BoMaQe8GfAhgvbmb06u0jf9wIG%2BA5VKlTN"
    "w6MJhx%2FH38%2F4KjpFLcURZdCWVKn%2BE3fetLjTqllKXvbay63Li4C5TM%2FI2ihfUd3YA8dVI"
    "plOeqhwKy0MU%2FGLd6MZZKqo9qZ8A%2B5eir18geDeaAyx4zCMN43eZyJHKORdJ6ZMXe1s0lE6zm"
    "R4jcgmlIhcO4w7XLLgmqE2r%2BYKW4IVc%2BIJlU7XOVHUcqD1czgHblBfbMDcMa%2FxvtnPggFjr"
    "8NvP3v0i69RybtnwUEXhHBUjwzq7qZ4Lo9npkjcH6h21F6xipU835kZVFzAqGKezbAZP72bEDFeYj"
    "AqNGO9ddPq2l51tJb467JTD%2FhwJdrBPWZslGpEA%2Flcp%2BDxEnbQuZUwSofvSTn3%2FpMwk70"
    "hmYhdabwWz22Ue%2FQQFLgnbydFnAla9mBzzxNdP4j5nG%2BR0a4SPyg5%2BVkjG3%2FZaHNqLgQ%2"
    "BzJP4M0hZ5l4aPC8xYPVT9yBG2umdsj5pZAEFhZc4iTCbkc33w3xsNoUOxx1eruP3FqhEivOHOk0W"
    "fX%2Btb419nKyr%2FNUE9Ho8uG%2FtZGr79XyNvGhpBIXUHBMJ5djbRPMBbjOGR7A2DxD3sdWGHrC"
    "sUo59sVyLn%2BqE5kyWUIrxGtd6CKDQA%2FMixPSy76GJ9SWUMikp0tD6Q%2FKXel7747nMQFVZ3D"
    "wMpxWlNBjvDnZb5W5rTCfFR1j0xePRsmRKExm4HWoXxTK3Zv8Ondid%2FTAG5TfzBANmZdGEbmvrD"
    "Y107kWKdpzcUUPrZa9HbI09lbMrGVFHzOm%2FcJoQ4oksV1aeYsBgkW%2F9AtSaCN%2B62vor2fsQ"
    "NTZsQvhT2fFFcbbxkNaXuWmOVqsZQqXrpkMhRBRMfbplH0SJmyLwoQ2dlz%2Bi3xq2SD%2BuTqOlb"
    "mX8Fybkxv%2FMk%2BQIsH5aulvkLTVXWp0pn0vUfKVCq87DMBGFimPSqz4agmjjseaFCYdPCgXDRn"
    "2r6wc6OElmnWbqSM7Mda3b0rVCzxP%2BSw%3D%3D&__VIEWSTATEGENERATOR=FFB41F3B&__PREVI"
    "OUSPAGE=ArPZbCZL2sCvITFOEcANPKV5oXnyCgWlosVyHDHskySPmSRkCNlrP45wFsJxGhfNMO18iq"
    "jKknEU1CP6Ih1qs03YC_oacz55Y7LXGo2bCCZIz7ryhAJDcsd4JmYPG6n00&__EVENTVALIDATION=4"
    "MkesSoTT18OxD0IbzVpMPMS746RGsxG4EUtJWA4tdnPXi7Ur0IGDK5dmKiy002EQs4YmUx0wAnF1R7"
    "ICaOqa0tHdOjHZZQJUNL8sY8PGuBcWQz2CVb0vDs%2Biz7ECwPxYi7ZhN0jeA0aWwZ6%2FOeEuqXg4"
    "cQK9KehTxNbJBIcgs1Fr6kY47lba6mRHBmcub8MPvUwrnjTBfqNuUi9Oq0oKbvR7ozEnHUOG17DyvD"
    "Pb0T6arKz4xs0LKL3%2BDYbm1cXIateY0svbQAmKx4EKqqHuQ%3D%3D"
)


def _build_payload(nuit: str) -> str:
    if not nuit:
        raise ValueError("nuit must be provided")
    return PAYLOAD_TEMPLATE.format(nuit=nuit)


def send_post(nuit: str) -> str:
    """
    Mirror the Firefox POST request captured from curl for the provided NUIT.
    """

    session = requests.Session()
    session.headers.update(HEADERS)
    session.get("https://nuit.at.gov.mz/", timeout=30)

    payload = _build_payload(nuit)

    try:
        response = session.post(POST_URL, data=payload, timeout=30)
        response.raise_for_status()
    except RequestException as exc:
        raise RuntimeError("Failed to POST to nuit.at.gov.mz") from exc

    return response.text
