from django.contrib import admin
from .models import *

# Register your models here.

#ANALISIS VERTICAL

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'usuario', 'fecha_creacion')
    list_filter = ('usuario', 'fecha_creacion')
    search_fields = ('nombre', 'ruc')

@admin.register(PeriodoContable)
class PeriodoContableAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa', 'fecha_inicio', 'fecha_fin', 'es_actual')
    list_filter = ('empresa', 'es_actual')
    search_fields = ('nombre', 'empresa__nombre')

@admin.register(CuentaContable)
class CuentaContableAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'nivel', 'es_total')
    list_filter = ('tipo', 'nivel')
    search_fields = ('codigo', 'nombre')

@admin.register(BalanceGeneral)
class BalanceGeneralAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'cuenta', 'valor')
    list_filter = ('periodo', 'cuenta__tipo')
    search_fields = ('cuenta__nombre', 'periodo__nombre')

@admin.register(EstadoResultados)
class EstadoResultadosAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'cuenta', 'valor')
    list_filter = ('periodo', 'cuenta__tipo')
    search_fields = ('cuenta__nombre', 'periodo__nombre')

@admin.register(AnalisisVertical)
class AnalisisVerticalAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'cuenta', 'porcentaje', 'tipo_estado', 'fecha_calculo')
    list_filter = ('periodo', 'tipo_estado', 'fecha_calculo')
    search_fields = ('cuenta__nombre', 'periodo__nombre')