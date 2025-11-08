from django import forms
from .models import Empresa, PeriodoContable
from .models import ImportedFile

class SeleccionAnalisisForm(forms.Form):
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.none(),
        empty_label="Seleccione una empresa",
        widget=forms.Select(attrs={'class': 'form-select-modern form-select'})
    )
    
    periodo = forms.ModelChoiceField(
        queryset=PeriodoContable.objects.none(),
        empty_label="Seleccione un periodo",
        widget=forms.Select(attrs={'class': 'form-select-modern form-select'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['empresa'].queryset = Empresa.objects.filter(usuario=user)
        if self.fields['empresa'].queryset.exists():
            empresa = self.fields['empresa'].queryset.first()
            self.fields['periodo'].queryset = PeriodoContable.objects.filter(empresa=empresa)
            
class companyForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'ruc', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-modern'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control-modern', 'rows': 3}),
        }

class periodoForm(forms.ModelForm):
    class Meta:
        model = PeriodoContable
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'es_actual']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control-modern'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control-modern', 'type': 'date'}),
            'es_actual': forms.CheckboxInput(attrs={'class': 'form-check-input-modern'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['es_actual'].required = False
        
class financialAnalysisForm(forms.Form):
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.none(),
        empty_label="Seleccione una empresa",
        widget=forms.Select(attrs={'class': 'form-select-modern form-select'})
    )
    
    periodo_inicio = forms.ModelChoiceField(
        queryset=PeriodoContable.objects.none(),
        empty_label="Seleccione el periodo de inicio",
        widget=forms.Select(attrs={'class': 'form-select-modern form-select'})
    )
    
    periodo_fin = forms.ModelChoiceField(
        queryset=PeriodoContable.objects.none(),
        empty_label="Seleccione el periodo de fin",
        widget=forms.Select(attrs={'class': 'form-select-modern form-select'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['empresa'].queryset = Empresa.objects.filter(usuario=user)
        if self.fields['empresa'].queryset.exists():
            empresa = self.fields['empresa'].queryset.first()
            self.fields['periodo_inicio'].queryset = PeriodoContable.objects.filter(empresa=empresa)
            self.fields['periodo_fin'].queryset = PeriodoContable.objects.filter(empresa=empresa)
            
class FileImportForm(forms.Form):
    class Meta:
        model = ImportedFile
        fields = ['file_type', 'period', 'report_type', 'file']
        widgets = {
            'file_type': forms.Select(attrs={'class': 'form-control-modern'}),
            'period': forms.Select(attrs={'class': 'form-control-modern'}),
            'report_type': forms.Select(attrs={'class': 'form-control-modern'}),
            'file': forms.FileInput(attrs={'class': 'file-input'}),
        }
