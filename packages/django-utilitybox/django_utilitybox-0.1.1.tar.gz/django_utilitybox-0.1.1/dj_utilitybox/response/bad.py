from dj_utilitybox.response import base
from rest_framework import exceptions as rex
from rest_framework import status as st


class DynamicAPIException(rex.APIException):
    def __init__(self, detail=None, status=None):
        super().__init__(detail=detail)
        if status is not None:
            self.status_code = status
            

class BaseRaiseResponse(base.BaseResponse):
    def execute_response(self): self.raise_exception()
    
    def raise_exception(self):
        data = self.generate_exception_data()
        raise DynamicAPIException(data, status=self.status)


class CustomRaise(BaseRaiseResponse):
    def __init__(self, message: str, field='', code='', extra_params={}, status=st.HTTP_400_BAD_REQUEST):
        super().__init__(field, code=code, message=message, status=status, extra_params=extra_params)
    

class QueryParamNotFound(BaseRaiseResponse):
    def __init__(self, field: str, message='', code='', extra_params={}, status=st.HTTP_400_BAD_REQUEST):
        if not message: message = f"Queryparam '{field}' is required"
        else: message = f"{field} {message}"
        super().__init__(field, code=code, message=message, status=status, extra_params=extra_params)
        
        
class KwargNotFound(BaseRaiseResponse):
    def __init__(self, field: str, message='', code='', extra_params={}, status=st.HTTP_400_BAD_REQUEST):
        if not message: message = f"Kwarg '{field}' is required"
        else: message = f"{field} {message}"
        super().__init__(field, code=code, message=message, status=status, extra_params=extra_params)
        
        
class ModelNotFound(BaseRaiseResponse):
    def __init__(self, field: str, message='', code='', extra_params={}, status=st.HTTP_400_BAD_REQUEST):
        if not message: message = f"{field} don't exist"
        else: message = f"{field} {message}"
        super().__init__(field, code=code, message=message, status=status, extra_params=extra_params)
        

class ModelNotFound(BaseRaiseResponse):
    def __init__(self, field: str, message='', code='', extra_params={}, status=st.HTTP_400_BAD_REQUEST):
        if not message: message = f"{field} don't exist"
        else: message = f"{field} {message}"
        super().__init__(field, code=code, message=message, status=status, extra_params=extra_params)

# Cuando no viene algo en el data POST
