from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('login/',views.login, name='login'),
    path('', views.home, name='home'),
    # Curso
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('cursos/novo/', views.cadastrar_curso, name='cadastrar_curso'),
    path('cursos/<int:curso_id>/editar/', views.editar_curso, name='editar_curso'),
    path('cursos/<int:curso_id>/deletar/', views.deletar_curso, name='deletar_curso'),

    # Aluno
    path('alunos/', views.lista_alunos, name='lista_alunos'),
    path('alunos/novo/', views.cadastrar_aluno, name='cadastrar_aluno'),
    path('alunos/<int:aluno_id>/editar/', views.editar_aluno, name='editar_aluno'),
    path('alunos/<int:aluno_id>/deletar/', views.deletar_aluno, name='deletar_aluno'),

    # Matrícula pública
    path('matricular/', views.matricular_aluno, name='matricular'),
]