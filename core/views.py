from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Curso, Aluno
from .forms import CursoForm, AlunoForm, MatriculaForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as login_django




# ---------- Login ----------
def login(request):
    if request.method == "GET":
        return render(request, 'core/login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        destino = request.POST.get('destino')  # pega o destino escolhido
        
        user = authenticate(username=username, password=senha)

        if user:
            login_django(request, user)            
            return redirect("/cursos")
        return HttpResponse("Usuário ou Senha inválidos!")


def home(request):
    return render(request, 'core/home.html')  # Página Principal


# --- CURSO ---

@login_required
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'core/lista_cursos.html', {'cursos': cursos})

@login_required
def cadastrar_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Curso cadastrado com sucesso")
            return redirect('core:lista_cursos')  # redireciona após salvar
    else:
        form = CursoForm()
    return render(request, 'core/form_curso.html', {'form': form})

@login_required
def editar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect('core:lista_cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'core/form_curso.html', {'form': form})

@login_required
def deletar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    # Verificação: curso tem alunos?
    if Aluno.objects.filter(curso=curso).exists():
        return HttpResponse("Não é possível excluir: este curso possui alunos matriculados!")

    if request.method == 'POST':
        curso.delete()
        return redirect('core:lista_cursos')

    return render(request, 'core/confirma_exclusao.html', {'objeto': curso, 'tipo': 'Curso'})


# --- ALUNO ---

@login_required
def lista_alunos(request):
    alunos = Aluno.objects.all()
    return render(request, 'core/lista_alunos.html', {'alunos': alunos})

@login_required
def cadastrar_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save(commit=False)  # ainda não salva no banco
            curso = aluno.curso  # pega o curso escolhido no formulário

            # ---- Verificação de duplicidade ----
            # supondo que email seja único por aluno
            if Aluno.objects.filter(email=aluno.email).exists():
                return HttpResponse("Aluno já cadastrado com este e-mail!")

            # ---- Verificação de vagas ----
            alunos_matriculados = Aluno.objects.filter(curso=curso).count()
            if curso.vagas is not None and alunos_matriculados >= curso.vagas:
                return HttpResponse("Não há mais vagas para este curso!")

            aluno.save()  # só salva se não for duplicado e houver vaga
            return redirect('core:lista_alunos')
        
    else:
        form = AlunoForm()

    return render(request, 'core/form_aluno.html', {'form': form})
@login_required
def editar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            return redirect('core:lista_alunos')
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'core/form_aluno.html', {'form': form})

@login_required
def deletar_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        aluno.delete()
        return redirect('core:lista_alunos')
    return render(request, 'core/confirma_exclusao.html', {'objeto': aluno, 'tipo': 'Aluno'})


# --- MATRICULAR (acesso livre) ---




def matricular_aluno(request):
    if request.method == 'POST':
        form = MatriculaForm(request.POST)
        if form.is_valid():
            matricula = form.save(commit=False)
            curso = matricula.curso

            if Aluno.objects.filter(email=matricula.email, curso=curso).exists():
                return HttpResponse("Este aluno já está matriculado neste curso!")

            alunos_matriculados = Aluno.objects.filter(curso=curso).count()
            if curso.vagas is not None and alunos_matriculados >= curso.vagas:
                return HttpResponse("Não há mais vagas para este curso!")

            matricula.save()
            messages.success(request, "Matrícula realizada com sucesso")
            return redirect('core:matricular')  # redirect após sucesso
    else:
        form = MatriculaForm()

    return render(request, 'core/matricula.html', {'form': form})
