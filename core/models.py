from datetime import timedelta
from django.utils import timezone
from django.db import models

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    duracao = models.IntegerField(help_text="Duração em anos")
    vagas = models.IntegerField()
    inicio = models.DateField(default=timezone.now)  # gera valor automaticamente
    fim = models.DateField(null=True, blank=True)   # calculado no save()

    def save(self, *args, **kwargs):
        if self.inicio and self.duracao:
            self.fim = self.inicio + timedelta(days=self.duracao * 365)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)    

    def __str__(self):
        return f"{self.nome} ({self.email})"
    
    @property
    def inicio_curso(self):
        return self.curso.inicio
    
    @property
    def fim_curso(self):
        return self.curso.fim