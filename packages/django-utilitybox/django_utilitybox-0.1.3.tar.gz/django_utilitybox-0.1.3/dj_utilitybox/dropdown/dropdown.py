from rest_framework import serializers as sr
from django.db.models import Model, F, Q, Value, CharField
from django.db.models.functions import Concat, Coalesce, Cast
from typing import Type
from termcolor import cprint
from rest_framework.views import APIView
from dj_utilitybox.filters import generator as gf
from dj_utilitybox.views.base import GetBase

class DropdownSr(sr.Serializer):
    id = sr.IntegerField()
    _name = sr.CharField()

class GenericDropdown(GetBase):
    """
        params:
            name_fields: Concatenacion de campos para mostrar si no se tiene un name
            name: filtro por coincidencia
        kwargs:
            model: modelo a filtrar
    """
    #?  Goal List
    serializer_class = DropdownSr
    ordering = "_name"
    page_size = 100
    list_view = True
    
    dict_model: dict
    default_name_field = "name"
    
    @staticmethod
    def build_concat(fields: list[str], separator: str = " ") -> F | Concat:
        """
        Crea una expresión ORM que concatena campos heterogéneos.
        Convierte todo a texto con Cast para evitar errores de tipo.
        """
        if not fields:
            raise ValueError("Debes pasar al menos un campo para concatenar.")

        exprs = [
            Coalesce(Cast(F(f), CharField()), Value(""), output_field=CharField())
            for f in fields
        ]

        # Si solo hay un campo, devuelve directamente la conversión
        if len(exprs) == 1:
            return exprs[0]

        # Intercalar separadores
        final_expr = []
        for i, e in enumerate(exprs):
            final_expr.append(e)
            if i < len(exprs) - 1:
                final_expr.append(Value(separator, output_field=CharField()))

        return Concat(*final_expr, output_field=CharField())
    
    def models_dict(self, model_name: str):
        return self.dict_model.get(model_name)
        
    def get_queryset(self, *args, **kwargs):
        qp = self.request.GET
        name_fields = qp.get('name_fields', self.default_name_field)
        name_fields = str(name_fields).split(',') if name_fields else [self.default_name_field]
        
        model_name = self.kwargs.get('model')
        self.model: Type[Model]  = self.models_dict(model_name)
        
        filters = self.get_filters()
        
        return (
            self.model.objects
            .annotate(
                _name = self.build_concat(name_fields)
            )
            .order_by("-id")
            .only('id')
            .filter(filters)
        )
    
    def active_filter(self):
        if hasattr(self.model, 'active'):
            return Q(active=True)
        return Q()
        
    def get_filters(self):
        qp = self.request.GET
        filter = [
            {'field': '_name', 'value': 'name', 'lookfield': 'icontains'},
        ]
        return gf.generate_filter(
            list_filter=filter,
            data=qp,
            list_q=[
                self.active_filter()
            ]
        )