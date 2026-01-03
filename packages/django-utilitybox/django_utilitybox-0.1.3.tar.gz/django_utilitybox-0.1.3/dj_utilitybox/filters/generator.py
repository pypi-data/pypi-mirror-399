
# python
import re
import operator
from typing import Literal
from functools import reduce
from dj_utilitybox.response import bad as br
# Django
from django.db.models import Q, QuerySet, Model
# DRF
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import generics as g
from rest_framework.views import status as s


or_not = Literal['or', 'and']
class FilterGenerator:
    
    def __init__(
        self, 
        data: dict = {},
        list_filter: list[dict] = [],
        list_q: list[Q] = [],
        mode: Literal['or', 'and'] = 'and',
        *args, 
        **kwargs
    ):
        self.data        = data
        self.list_filter = list_filter
        self.mode        = mode
        self.list_q      = list_q
    
    def validate_param(self, value: str, data: dict, list_value = False, bool_value=False, raise_exeption=False):
        """
            Valida que un parámetro exista en el diccionario dado y devuelve su valor.

            Args:
                value (str): El nombre de la clave que se debe buscar dentro de `data`.
                data (dict): El diccionario en el que se buscará el parámetro.
                list_value (bool, optional): Si es Verdadero, convierte el valor en una lista. 
                    El valor predeterminado es Falso.
                bool_value (bool, optional): Si es Verdadero, valida que el valor sea un booleano. 
                    El valor predeterminado es Falso.
                raise_exception (bool, optional): Si es Verdadero, lanza una excepción si el parámetro 
                    no existe. El valor predeterminado es Falso.

            Returns:
                Any: El valor asociado a `value` dentro de `data`, si existe.
        """
        
        coincidence = data.get(value)
        if not coincidence and raise_exeption: br.QueryParamNotFound(value) #! Refactor this
        if list_value and coincidence: coincidence = coincidence.split(',')
        if bool_value and coincidence: coincidence = True if coincidence.lower() in ['true', 'on'] else False
        return coincidence
    
    def q_query(self, field, value, q_not = False) ->Q:
        """
            Construye un objeto Q, con la opción de negación.

            Args:
                field (str): El nombre del campo del modelo sobre el cual aplicar el filtro.
                value (Any): El valor que se comparará contra el campo dado. 
                    Si es None o un valor falso, se devuelve un objeto Q vacío.
                q_not (bool, optional): Si es Verdadero, devuelve el objeto Q negado (~Q). 
                    El valor predeterminado es Falso.

            Returns:
                Q: Devuelve una Q.
        """

        q = Q(**{field: value}) if value else Q()
        return ~q if q_not else q
        
    def q_query_validate(
        self, field: str, data: dict, value: str=None, list_value: bool = False, 
        bool_value: bool=False, raise_exeption: bool=False, lookfield:str = None) ->Q:
        
        """
            Construye un objeto Q de Django validando primero que el parámetro exista en los datos.

            Args:
                field (str): El nombre del campo del modelo sobre el cual aplicar el filtro.
                data (dict): El diccionario desde donde se obtendrá el valor a comparar.
                value (str, optional): El nombre de la clave a buscar dentro de `data`. 
                    Si no se especifica, se usa el mismo valor de `field`.
                list_value (bool, optional): Si es Verdadero, convierte el valor obtenido en una lista.
                bool_value (bool, optional): Si es Verdadero, valida que el valor sea booleano.
                raise_exeption (bool, optional): Si es Verdadero, lanza una excepción si el parámetro 
                    no existe o no cumple con la validación.
                lookfield (str, optional): Nombre de un subcampo para aplicar búsqueda (ejemplo: `"id"` 
                    generaría `field__id`).

            Returns:
                Q: Un objeto Q de Django que representa la condición de filtro.
        """
        if not value: value=field
        if lookfield: field = f'{field}__{lookfield}'
        value = self.validate_param(value, data, list_value, bool_value, raise_exeption)
        return self.q_query(field, value)
    
    @staticmethod
    def fusion_q(*q_objects, mode: or_not='and'):
        """
            Fusiona múltiples objetos Q en una sola condición,
            utilizando el modo lógico especificado ("or" o "and").

             Args:
                q_objects (Q): Uno o más objetos Q que se van a combinar.
                mode (Literal['or', 'and']): El modo de combinación lógica.
                
            Returns:
                Q: Una única instancia de Q que representa la combinación de todas 
                las condiciones.
        """
        if not q_objects:
            return Q() 

        if mode == 'or':
            return reduce(operator.or_, q_objects)
        else:
            return reduce(operator.and_, q_objects)
    
    def generate_filter(self):
        """
            Genera un objeto Q único combinando todos los filtros configurados.

            Returns:
                Q: Una única instancia de Q que representa la combinación de todas 
            """
        q_objects = []
        for filter in self.list_filter:
            q_objects.append(self.q_query_validate(**filter, data=self.data))
            
        q_objects.extend(self.list_q)
        return self.fusion_q(*q_objects, mode=self.mode)
    
    
def generate_filter(
    list_filter: list[dict] = [], 
    data: dict = {}, 
    list_q: list[Q] = [],
    mode: or_not='and'
):
    generator = FilterGenerator(
        data = data,
        mode = mode,
        list_filter = list_filter,
        list_q=list_q
    )
    filters = generator.generate_filter()
    return filters


def test():
    data = {
        'numero_economico': 'Putos todos menos yo'
    }

    generator = FilterGenerator(
        data = data,
        mode = 'and',
        list_filter = [
            {'field': 'numero_economico', 'lookfield': 'icontains'},
            {'field': 'numero_economico', 'lookfield': 'icontains'},
        ]
    )
    filters = generator.generate_filter()
    print(filters)
    
def test2():
    rompehuevos = [Q(pene=True)]
    data = {'numero_economico': 'Putos todos menos yo'}
    list_filter = [
        {'field': 'numero_economico', "raise_exeption": True, 'lookfield': 'icontains'},
        {'field': 'numero_economico', 'lookfield': 'icontains'},
    ]
    filters = generate_filter(list_filter, data, list_q=rompehuevos)
    print(filters)

    