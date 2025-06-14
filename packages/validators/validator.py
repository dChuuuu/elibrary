import re

from fastapi import HTTPException, status


class EmailValidator:
    async def validate(self, email):
        pattern = r'^[a-zA-Z0-9!._%+-]+@[a-zA-Z0-9!"#$%&()*+,-./:;<=>?@^_{|}~`]+\.[a-z]{2,}$'
        is_valid = re.match(pattern, email)
        if is_valid is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Incorrect email field')



class PasswordValidator:
    async def validate(self, password):
        is_valid = {}
        is_valid['length'] = (bool(8 <= len(password) <= 19))
        is_valid['specsymbol'] = (bool(re.search(r'[!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]', password)))
        is_valid['is_lowercase'] = bool(re.search(r'[a-z]', password))
        is_valid['is_uppercase'] = bool(re.search(r'[A-Z]', password))
        if all(list(map(lambda critetia: is_valid[critetia] is True, is_valid.keys()))) is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Wrong password format. Check the requirements:'
                                       'length >= 8, length <= 18,'
                                       'any of these specsymbols: !"#$%&()*+,-./:;<=>?@[]^_{|}~`,'
                                       'at least one lowercase letter, and one uppercase letter')





