from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Q
from .models import *
from decimal import Decimal
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

#DEFINICON DE VISTAS PARA AUTENTICACION LOGIN/LOGOUT
def login_view(request):
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login exitoso
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            
            # Redirigir al home
            return redirect('home')
        else:
            # Login fallido
            messages.error(request, 'Credenciales incorrectas. Por favor, inténtalo de nuevo.')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

@login_required
def home_view(request):
    return render(request, 'home.html')

#Análisis vertical
@login_required
def analisis_vertical(request):
    # Obtener empresas del usuario
    empresas = Empresa.objects.filter(usuario=request.user)
    
    # Obtener periodos de la empresa seleccionada o la primera
    empresa_seleccionada = request.GET.get('empresa')
    if empresa_seleccionada:
        empresa = get_object_or_404(Empresa, id=empresa_seleccionada, usuario=request.user)
    elif empresas.exists():
        empresa = empresas.first()
    else:
        empresa = None

    periodos = PeriodoContable.objects.filter(empresa=empresa) if empresa else PeriodoContable.objects.none()
    
    # Obtener periodo seleccionado
    periodo_seleccionado = request.GET.get('periodo')
    if periodo_seleccionado:
        periodo = get_object_or_404(PeriodoContable, id=periodo_seleccionado, empresa=empresa)
    elif periodos.exists():
        periodo = periodos.filter(es_actual=True).first() or periodos.first()
    else:
        periodo = None

    contexto = {
        'empresas': empresas,
        'empresa_seleccionada': empresa,
        'periodos': periodos,
        'periodo_seleccionado': periodo,
    }

    if periodo:
        # Calcular análisis vertical para balance general
        balance_data = calcular_analisis_vertical_balance(periodo)
        resultado_data = calcular_analisis_vertical_resultados(periodo)
        
        contexto.update({
            'balance_data': balance_data,
            'resultado_data': resultado_data,
            'metricas': calcular_metricas_financieras(periodo),
            'insights': generar_insights(periodo, balance_data, resultado_data)
        })

    return render(request, 'analisisvertical.html', contexto)

def calcular_analisis_vertical_balance(periodo):
    """Calcula el análisis vertical del balance general"""
    cuentas_balance = BalanceGeneral.objects.filter(periodo=periodo).select_related('cuenta')
    
    # Calcular totales por tipo de cuenta
    total_activos = cuentas_balance.filter(
        cuenta__tipo='ACTIVO', 
        cuenta__es_total=True
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    total_pasivos = cuentas_balance.filter(
        cuenta__tipo='PASIVO', 
        cuenta__es_total=True
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    total_patrimonio = cuentas_balance.filter(
        cuenta__tipo='PATRIMONIO', 
        cuenta__es_total=True
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
    
    total_general = total_activos

    data = {
        'activos': [],
        'pasivos': [],
        'patrimonio': [],
        'totales': {
            'activos': total_activos,
            'pasivos': total_pasivos,
            'patrimonio': total_patrimonio,
            'general': total_general
        }
    }

    # Procesar activos
    cuentas_activo = cuentas_balance.filter(cuenta__tipo='ACTIVO').order_by('orden')
    for cuenta_bg in cuentas_activo:
        if total_general > 0:
            porcentaje = (cuenta_bg.valor / total_general) * 100
        else:
            porcentaje = Decimal('0')
        
        data['activos'].append({
            'cuenta': cuenta_bg.cuenta,
            'valor': cuenta_bg.valor,
            'porcentaje': porcentaje,
            'nivel': cuenta_bg.cuenta.nivel,
            'es_total': cuenta_bg.cuenta.es_total
        })

    # Procesar pasivos y patrimonio (similar a activos)
    # ... código similar para pasivos y patrimonio ...

    return data

def calcular_analisis_vertical_resultados(periodo):
    """Calcula el análisis vertical del estado de resultados"""
    cuentas_resultados = EstadoResultados.objects.filter(periodo=periodo).select_related('cuenta')
    
    # Obtener ventas netas (base para porcentajes)
    ventas_netas = cuentas_resultados.filter(
        cuenta__tipo='INGRESO', 
        cuenta__nombre__icontains='venta'
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

    data = {
        'ingresos': [],
        'costos': [],
        'gastos': [],
        'utilidades': [],
        'ventas_netas': ventas_netas
    }

    # Procesar cuentas de resultados
    for cuenta_er in cuentas_resultados.order_by('orden'):
        if ventas_netas > 0:
            porcentaje = (cuenta_er.valor / ventas_netas) * 100
        else:
            porcentaje = Decimal('0')
        
        item = {
            'cuenta': cuenta_er.cuenta,
            'valor': cuenta_er.valor,
            'porcentaje': porcentaje,
            'nivel': cuenta_er.cuenta.nivel,
            'es_total': cuenta_er.cuenta.es_total
        }

        if cuenta_er.cuenta.tipo == 'INGRESO':
            data['ingresos'].append(item)
        elif cuenta_er.cuenta.tipo == 'COSTO':
            data['costos'].append(item)
        elif cuenta_er.cuenta.tipo == 'GASTO':
            data['gastos'].append(item)
        elif cuenta_er.cuenta.es_total:  # Utilidades
            data['utilidades'].append(item)

    return data

def calcular_metricas_financieras(periodo):
    """Calcula métricas financieras clave"""
    balance_data = calcular_analisis_vertical_balance(periodo)
    resultado_data = calcular_analisis_vertical_resultados(periodo)
    
    total_activos = balance_data['totales']['activos']
    total_pasivos = balance_data['totales']['pasivos']
    total_patrimonio = balance_data['totales']['patrimonio']
    utilidad_neta = next((item['valor'] for item in resultado_data['utilidades'] 
                         if 'net' in item['cuenta'].nombre.lower()), Decimal('0'))
    
    metricas = {}
    
    if total_activos > 0:
        metricas['roa'] = (utilidad_neta / total_activos) * 100  # Return on Assets
    
    if total_patrimonio > 0:
        metricas['roe'] = (utilidad_neta / total_patrimonio) * 100  # Return on Equity
    
    if total_pasivos + total_patrimonio > 0:
        metricas['endeudamiento'] = (total_pasivos / (total_pasivos + total_patrimonio)) * 100
    
    # Calcular razón corriente (Activo Corriente / Pasivo Corriente)
    activo_corriente = next((item['valor'] for item in balance_data['activos'] 
                           if 'corriente' in item['cuenta'].nombre.lower() and item['es_total']), Decimal('0'))
    pasivo_corriente = next((item['valor'] for item in balance_data['pasivos'] 
                           if 'corriente' in item['cuenta'].nombre.lower() and item['es_total']), Decimal('0'))
    
    if pasivo_corriente > 0:
        metricas['razon_corriente'] = activo_corriente / pasivo_corriente
    else:
        metricas['razon_corriente'] = Decimal('0')
    
    return metricas

def generar_insights(periodo, balance_data, resultado_data):
    """Genera insights automáticos basados en el análisis"""
    insights = []
    
    # Insight sobre estructura de activos
    activo_corriente_perc = next((item['porcentaje'] for item in balance_data['activos'] 
                                if 'corriente' in item['cuenta'].nombre.lower() and item['es_total']), Decimal('0'))
    
    if activo_corriente_perc < 30:
        insights.append({
            'tipo': 'warning',
            'titulo': 'Baja Liquidez',
            'mensaje': 'El activo corriente representa solo el {:.1f}% del total. Considere aumentar la liquidez.'.format(activo_corriente_perc)
        })
    elif activo_corriente_perc > 60:
        insights.append({
            'tipo': 'info',
            'titulo': 'Alta Liquidez',
            'mensaje': 'El activo corriente representa el {:.1f}% del total. Evaloque optimizar el uso de activos.'.format(activo_corriente_perc)
        })

    # Insight sobre rentabilidad
    margen_neto = next((item['porcentaje'] for item in resultado_data['utilidades'] 
                       if 'net' in item['cuenta'].nombre.lower()), Decimal('0'))
    
    if margen_neto < 5:
        insights.append({
            'tipo': 'danger',
            'titulo': 'Baja Rentabilidad',
            'mensaje': 'El margen neto es del {:.1f}%. Considere revisar costos y gastos.'.format(margen_neto)
        })
    elif margen_neto > 15:
        insights.append({
            'tipo': 'success',
            'titulo': 'Alta Rentabilidad',
            'mensaje': 'Excelente margen neto del {:.1f}%.'.format(margen_neto)
        })

    return insights

@login_required
def cargar_periodos(request):
    """Carga periodos por empresa (AJAX)"""
    empresa_id = request.GET.get('empresa_id')
    if empresa_id:
        periodos = PeriodoContable.objects.filter(empresa_id=empresa_id).values('id', 'nombre')
        return JsonResponse(list(periodos), safe=False)
    return JsonResponse([], safe=False)

@login_required
def guardar_analisis_vertical(request):
    """Guarda el análisis vertical calculado"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            periodo_id = data.get('periodo_id')
            analisis_data = data.get('analisis_data')
            
            periodo = get_object_or_404(PeriodoContable, id=periodo_id)
            
            # Guardar análisis vertical
            for item in analisis_data:
                AnalisisVertical.objects.update_or_create(
                    periodo=periodo,
                    cuenta_id=item['cuenta_id'],
                    tipo_estado=item['tipo_estado'],
                    defaults={
                        'valor_absoluto': item['valor_absoluto'],
                        'porcentaje': item['porcentaje']
                    }
                )
            
            return JsonResponse({'success': True, 'message': 'Análisis guardado correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

#Analisis horizontal (pendiente)
@login_required
def analisis_horizontal(request):
    return render(request, 'analisishorizontal.html')

#EOAF (PENDIENTE)

@login_required
def EOAF(request):
    return render(request, 'eoaf.html')

#Razones financieras (pendiente)
@login_required
def razones_financieras(request):
    return render(request, 'razones.html')

#DUPONT (pendiente)
@login_required
def dupont(request):
    return render(request, 'dupont.html')

#Metdodo Directo (pendiente)
@login_required
def metodo_directo(request):
    return render(request, 'matododirecto.html')

#Metodo Indirecto (pendiente)
@login_required
def metodo_indirecto(request):
    return render(request, 'metodoindirecto.html')

#Liquidez (pendiente)
@login_required
def liquidez(request):
    return render(request, 'liquidity.html')

#actividades pendientes
@login_required
def actividades(request):
    return render(request, 'actividad.html')

#debt pendiente
@login_required
def DEBT(request):
    return render(request, 'debt.html')

#profitability pendiente
@login_required
def profitability(request):
    return render(request, 'Profita.html')

#perfil pendiente
def perfil(request):
    return render(request, 'perfil.html')

#configuracion pendien
def configuracion(request):
    return render(request, 'config.html'),
