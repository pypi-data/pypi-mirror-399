from bs4 import BeautifulSoup


def extract_data(html_content: str) -> dict:

    ## check if there is a tag 'a' with id = GridView1_lnkNome_0
    ## if not found return empty dict {}
    ## else extract the text content of the tag
    soup = BeautifulSoup(html_content, "html.parser")
    anchor = soup.find("a", id="GridView1_lnkNome_0")
    if anchor is None:
        return {}

    ## split the text content by '-' and get the nuit(before '-') and full name(after '-')
    ## return {'nuit': nuit, 'name': name}
    text_content = anchor.get_text(strip=True)
    if "-" not in text_content:
        return {}

    nuit, name = (part.strip() for part in text_content.split("-", 1))
    if not nuit or not name:
        return {}

    return {"nuit": nuit, "name": name}


def is_nuit_valid(html_content: str) -> dict:
    ## check if there is 'div' with id='ValidationSummary1'
    soup = BeautifulSoup(html_content, "html.parser")

    ##if there is return {'is_valid': False}
    if soup.find("div", id="ValidationSummary1") is not None:
        return {"is_valid": False}

    ##else get the name and nuit using get_user_details()
    user_details = extract_data(html_content)
    if not user_details:
        return {"is_valid": False}

    ## return {'is_valid': True, 'nuit': nuit, 'name':name }
    return {"is_valid": True, "nuit": user_details["nuit"], "name": user_details["name"]}
