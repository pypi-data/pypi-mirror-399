
from rest_framework import status as st
from termcolor import cprint

class DifferentType(Exception):
    def __init__(self, field):
        message = f'Expected attribute of type: "{field}"'
        super().__init__(message)


class BaseResponse:
    def __init__(self, field='', code='', message='', key='status', extra_params:dict={}, status=st.HTTP_200_OK):
        """
        This Python function initializes an object with specified parameters and
        executes a response.
        
        Args:
          field: 
          code: 
          message: 
          key: 
          extra_params: 
          status: 
        """
        
        if not message: message = ''
        self.message = message
        self.field = field
        self.code = code
        self.key = key
        self.status = status
        self.extra_params = extra_params
        if not isinstance(extra_params, dict): raise DifferentType('dict')
        self.execute_response()

    def generate_exception_data(self):
        message = self.message
        data = {self.key: message}
        if self.code: data['code'] = self.code
        if self.extra_params: data.update(self.extra_params)
        return data
    
    def execute_response(self):...

    def good_response(self): ...
    
    def raise_exception(self): ...