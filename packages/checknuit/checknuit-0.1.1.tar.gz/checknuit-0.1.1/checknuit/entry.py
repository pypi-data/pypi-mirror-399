from checknuit.web import send_post
from checknuit.utils import is_nuit_valid

def check_nuit(nuit: str) -> dict:
    is_valid: False
    user_data: dict = {}

    request_response = send_post(nuit)

    response = is_nuit_valid(request_response)
    
    return response
