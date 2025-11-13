from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    ruc = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre

class PeriodoContable(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    es_actual = models.BooleanField(default=False)

    class Meta:
        unique_together = ['empresa', 'nombre']
        verbose_name = "Periodo Contable"
        verbose_name_plural = "Periodos Contables"

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

class CuentaContable(models.Model):
    TIPO_CUENTA_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('PASIVO', 'Pasivo'),
        ('PATRIMONIO', 'Patrimonio'),
        ('INGRESO', 'Ingreso'),
        ('COSTO', 'Costo'),
        ('GASTO', 'Gasto'),
    ]
    
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES)
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    nivel = models.IntegerField(default=1)
    es_total = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class BalanceGeneral(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Balance General"
        verbose_name_plural = "Balances Generales"
        unique_together = ['periodo', 'cuenta']

    def __str__(self):
        return f"{self.cuenta.nombre} - {self.periodo.nombre}"

class EstadoResultados(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Estado de Resultados"
        verbose_name_plural = "Estados de Resultados"
        unique_together = ['periodo', 'cuenta']

    def __str__(self):
        return f"{self.cuenta.nombre} - {self.periodo.nombre}"

class AnalisisVertical(models.Model):
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor_absoluto = models.DecimalField(max_digits=15, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=8, decimal_places=4)  # 100.0000%
    tipo_estado = models.CharField(max_length=20, choices=[('BALANCE', 'Balance'), ('RESULTADOS', 'Resultados')])
    fecha_calculo = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Análisis Vertical"
        verbose_name_plural = "Análisis Verticales"
        unique_together = ['periodo', 'cuenta', 'tipo_estado']

    def __str__(self):
        return f"AV {self.cuenta.nombre} - {self.periodo.nombre}"

class AnalisisHorizontal(models.Model):
    cuenta = models.ForeignKey(CuentaContable, on_delete=models.CASCADE)
    valor_periodo_base = models.DecimalField(max_digits=15, decimal_places=2)
    valor_periodo_comparativo = models.DecimalField(max_digits=15, decimal_places=2)
    variacion_absoluta = models.DecimalField(max_digits=15, decimal_places=2)
    variacion_porcentual = models.DecimalField(max_digits=8, decimal_places=4)  # 100.0000%
    tipo_estado = models.CharField(max_length=20, choices=[('BALANCE', 'Balance'), ('RESULTADOS', 'Resultados')])
    fecha_calculo = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Análisis Horizontal"
        verbose_name_plural = "Análisis Horizontales"
        unique_together = ['cuenta', 'tipo_estado']

    def __str__(self):
        return f"AH {self.cuenta.nombre}"

