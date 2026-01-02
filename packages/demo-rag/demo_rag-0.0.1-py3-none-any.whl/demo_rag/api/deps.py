from fastapi import Request, HTTPException, Depends


def authenticate(request: Request) -> bool:
    """
    Verify the provided token against the expected token.
    """
    token = request.headers.get("Token")
    user_db = request.app.state.user_db

    if token not in user_db.keys():
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token") 

    return user_db[token]

def authorize(user_info = Depends(authenticate)):
    """
    Authorize the user based on their role.
    """
    if user_info.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this resource")
    return True

