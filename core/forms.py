from django import forms
from .models import Curso, Aluno

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nome', 'duracao', 'vagas', 'inicio','fim']
        widgets = {
            'inicio': forms.DateInput(attrs={'type': 'date'}),
            'fim': forms.DateInput(attrs={'type': 'date'}),
        }

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'curso']        

class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'curso']

