
from rest_framework import serializers as sr
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView, Response
from typing import Type

class DynamicPagination(CursorPagination):
    page_size = 100
    ordering = '-pk'
    
class GetBase(APIView):
    #! Validar en caso que no exista
    """
        Clase base para vistas de tipo APIView que soporta dos modos:
        - Listado (list_view=True) con paginación.
        - Detalle (list_view=False) para un solo objeto.

        Atributos configurables en las subclases:
        
        - page_size (int): 
            Número máximo de registros por página en las vistas de lista. 
            Por defecto 100.

        - ordering (str): 
            Campo de ordenamiento por defecto para los resultados.
            Ejemplo: "-pk" (descendente por clave primaria).

        - list_view (bool): 
            Indica el modo de la vista.
            True  → lista con paginación.
            False → detalle de un único objeto.

        - serializer_class (Type[sr.Serializer]): 
            Clase de serializer que transformará los datos (QuerySet u objeto) 
            en la representación JSON de respuesta.
            Cada subclase debe definir el serializer correspondiente.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    page_size = 100
    ordering = "-pk"
    list_view = False
    serializer_class: Type[sr.Serializer]
    
    #? Paginador
    def get_paginator(self):
        paginator = DynamicPagination()
        paginator.page_size = self.page_size
        paginator.ordering = self.ordering
        return paginator
    
    #? Respuesta GET 
    def get(self, request, *args, **kwargs):
        if self.list_view:
            return self.list_view_method(request)
        else:
            return self.retrieve_view_method(request)
    
    #? Respuesta de List View
    def list_view_method(self, request):
        qs = self.get_queryset()
        paginator = self.get_paginator()
        page = paginator.paginate_queryset(qs, request)
        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    #? Respuesta de Retrieve (1 solo elemento)
    def retrieve_view_method(self, request):
        obj = self.get_object()
        serializer = self.serializer_class(obj, many=False)
        return Response(serializer.data)
    
    #? Modificables
    def get_queryset(self): #Listas
        """Método que debe implementar la subclase."""
        raise NotImplementedError("Debes implementar get_queryset en tu subclase.")
    
    def get_object(self): #Un solo elemento
        return self.get_queryset().first()

        
""" #? Example
class Test(GetBase):
    ordering = '-date_warranty'
    serializer_class = RescueLiteSerializer
    list_view = True
    
    def get_queryset(self):
        return (
            mr.Rescue.objects
            .filter(operative_status=mr.WARRANTY)
            .select_related("operational_user", "company")
            .prefetch_related(base.prefetch)
            .order_by("-id")
            .annotate(
                **base.payment_annotations
            )
            .values(
                *base.common_values,
                "date_warranty"
            )
        )
"""