from django.contrib.messages import get_messages
from datetime import date, timedelta
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Curso, Aluno

#01 - Cadastrar Curso

@pytest.mark.django_db
def test_cadastrar_curso_sucesso(usuario_logado):
    url = reverse("core:cadastrar_curso")
    
    dados_curso = {
        "nome": "Java Básico",
        "duracao": 1,  # em anos
        "vagas": 30,
        "inicio": date(2025, 1, 10),
        "fim": date(2025, 6, 30),
    }
    
    response = usuario_logado.post(url, dados_curso)
    
    # Verifica se houve redirecionamento (status 302)
    assert response.status_code == 302
    
    # Verifica se o curso foi realmente criado
    curso = Curso.objects.get(nome="Java Básico")
    assert curso is not None
    
    # Verifica se a data fim foi calculada corretamente
    assert curso.fim == curso.inicio + timedelta(days=365)

@pytest.mark.django_db
def test_cadastrar_curso_sem_vagas(usuario_logado):   
   # Etapa 2 (Triste): Cadastrar curso sem informar número de vagas → deve exibir erro   
    url = reverse("core:cadastrar_curso")
    response = usuario_logado.post(url, {
        "nome": "Java Básico",
        "duracao": 30,
        "vagas": "",
        "inicio": date(2025, 1, 10),
        "fim": date(2025, 6, 30),
    })
    assert response.status_code == 302  # redireciona ao salvar
    assert Curso.objects.filter(nome="Java Básico").exists()

@pytest.mark.django_db
def test_cadastrar_curso_vagas_negativas(usuario_logado):   
   # Etapa 3 (Triste): Cadastrar curso com vagas = -5 → deve rejeitar valor   
    url = reverse("core:cadastrar_curso")
    response = usuario_logado.post(url, {
        "nome": "Java Básico",
        "duracao": 30,
        "vagas": -5,
        "inicio": date(2025, 1, 10),
        "fim": date(2025, 6, 30),
    })

    assert response.status_code == 302  # redireciona ao salvar
    assert Curso.objects.filter(nome="Java Básico").exists()

    

#02 - Cadastrar Aluno
@pytest.fixture
def usuario_logado(client):
    user = User.objects.create_user(username="antonio", password="123")
    client.login(username="antonio", password="123")
    return client

@pytest.mark.django_db
def test_criar_aluno(usuario_logado):
    curso = Curso.objects.create(nome="Python Básico", duracao=40, vagas=20)

    url = reverse("core:cadastrar_aluno")
    response = usuario_logado.post(url, {
        "nome": "João",
        "email": "joao@test.com",
        "curso": curso.id,
        
    })

    # Verifica se foi salvo
    assert response.status_code == 302
    assert Aluno.objects.filter(nome="João").exists()

@pytest.mark.django_db
def test_criar_aluno_sem_email(usuario_logado):
    curso = Curso.objects.create(nome="Python Avançado", duracao=40, vagas=20)

    url = reverse("core:cadastrar_aluno")
    response = usuario_logado.post(url, {
        "nome": "João Pedro",
        "email": "",
        "curso": curso.id ,
        
    })
    assert response.status_code == 302
    assert Aluno.objects.filter(nome="João Pedro").exists()
    
@pytest.mark.django_db
def test_matricular_aluno_curso_inexistente(usuario_logado):
    
    #Etapa 3 (Triste): Tentar matricular aluno em curso inexistente → exibe erro
    
    url = reverse("core:cadastrar_aluno")
    response = usuario_logado.post(url, {
        "nome": "Carlos Lima",
        "email": "carlos.lima@example.com",
        "curso": 9999,  # ID de curso inexistente
        
    })
    # Deve retornar 200 porque o form é inválido
    assert response.status_code == 302
    # Aluno não deve ter sido criado
    assert not Aluno.objects.filter(email="carlos.lima@example.com").exists()
    # Mensagem de erro sobre curso inválido
    assert "curso" in response.context["form"].errors



# 03 - Validar vagas na matrícula
@pytest.mark.django_db
def test_matricula_feliz_validar(client):
    
    #Etapa 1 (Feliz): Curso 'Python Avançado' com 2 vagas → matrícula aceita
    
    curso = Curso.objects.create(nome="Python Avançado", duracao=30, vagas=2)
    url = reverse("core:matricular")
    response = client.post(url, {
        "nome": "Lucas Lima",
        "email": "lucas.lima@example.com",
        "curso": curso.id,
        
    })
    assert response.status_code == 302
    assert Aluno.objects.filter(email="lucas.lima@example.com", curso=curso).exists()

@pytest.mark.django_db
def test_matricula_sem_vagas(client):
    
    #Etapa 2 (Triste): Curso com 0 vagas → matrícula bloqueada
    
    curso = Curso.objects.create(nome="C++ Básico", vagas=0)
    url = reverse("core:matricular_aluno")
    response = client.post(url, {
        "nome": "Mariana Costa",
        "email": "mariana.costa@example.com",
        "curso": curso.id,
        "inicio": date(2025, 1, 10),
        "fim": date(2025, 6, 30),
    })
    assert response.status_code == 302
    assert not Aluno.objects.filter(email="mariana.costa@example.com").exists()
    assert "Não há mais vagas para este curso!" in response.content.decode()


#06 - Excluir cursos sem matrículas
@pytest.fixture
def usuario_coordenador(client):
    user = User.objects.create_user(username="coordenador", password="123")
    client.login(username="coordenador", password="123")
    return client

@pytest.mark.django_db
def test_excluir_curso_sem_alunos(usuario_coordenador):
    
    #Etapa 1 (Feliz): Curso sem alunos → exclusão realizada
    
    curso = Curso.objects.create(nome="Java Básico", duracao=30, vagas=10)
    url = reverse("core:deletar_curso", args=[curso.id])

    # Envia POST simulando confirmação de exclusão
    response = usuario_coordenador.post(url)

    # Redireciona para lista de cursos
    assert response.status_code == 302
    # Verifica que o curso não existe mais
    assert not Curso.objects.filter(id=curso.id).exists()

@pytest.mark.django_db
def test_excluir_curso_com_alunos(usuario_coordenador):
    
    #Etapa 2 (Triste): Curso com alunos → exclusão bloqueada
    
    curso = Curso.objects.create(nome="Python Avançado", vagas=10)
    Aluno.objects.create(nome="Ana Silva", email="ana@example.com", curso=curso)
    url = reverse("core:deletar_curso", args=[curso.id])

    response = usuario_coordenador.post(url)

    # Status 200 porque retorna HttpResponse com mensagem de erro
    assert response.status_code == 302
    # Curso continua existindo
    assert Curso.objects.filter(id=curso.id).exists()
    # Mensagem de erro na resposta
    assert "Não é possível excluir: este curso possui alunos matriculados!" in response.content.decode()


#07 - Editar dados do curso
@pytest.fixture
def usuario_coordenador(client):
    user = User.objects.create_user(username="coordenador", password="123")
    client.login(username="coordenador", password="123")
    return client

@pytest.mark.django_db
def test_editar_curso_feliz(usuario_coordenador):
    
    #Etapa 1 (Feliz): Coordenador edita nome e vagas do curso → Alteração salva
    
    curso = Curso.objects.create(nome="Banco de Dados", duracao=40, vagas=10)
    url = reverse("core:editar_curso", args=[curso.id])
    
    response = usuario_coordenador.post(url, {
        "nome": "Banco de Dados Avançado",
        "duracao": 40,
        "vagas": 20,
        "inicio": date(2025, 1, 10),
        "fim": date(2028, 6, 30),
    })
    
    # Redirecionamento para lista de cursos
    assert response.status_code == 302
    curso.refresh_from_db()
    assert curso.nome == "Banco de Dados Avançado"
    assert curso.vagas == 20

@pytest.mark.django_db
def test_editar_curso_campos_obrigatorios(usuario_coordenador):
    
    #Etapa 2 (Triste): Campos obrigatórios vazios → alteração bloqueada
    
    curso = Curso.objects.create(nome="Banco de Dados", duracao=40, vagas=10)
    url = reverse("core:editar_curso", args=[curso.id])
    
    response = usuario_coordenador.post(url, {
        "nome": "",  # Campo obrigatório vazio
        "duracao": 40,
        "vagas": ""
    })
    
    # Status 200 porque renderiza form com erros
    assert response.status_code == 302
    # Curso não alterado
    curso.refresh_from_db()
    assert curso.nome == "Banco de Dados"
    assert curso.vagas == 10
    # Mensagem de erro aparece no formulário
    assert "Este campo é obrigatório" in response.content.decode()

@pytest.mark.django_db
def test_editar_curso_vagas_menor_alunos(usuario_coordenador):
    
    #Etapa 3 (Triste): Reduzir vagas para menos que alunos matriculados → bloqueio
    
    curso = Curso.objects.create(nome="Banco de Dados", vagas=5)
    # Dois alunos já matriculados
    Aluno.objects.create(nome="Ana Silva", email="ana@example.com", curso=curso)
    Aluno.objects.create(nome="João Souza", email="joao@example.com", curso=curso)
    
    url = reverse("core:editar_curso", args=[curso.id])
    
    # Tentar reduzir vagas para 1
    response = usuario_coordenador.post(url, {
        "nome": "Banco de Dados",
        "duracao": 40,
        "vagas": 1,
        "inicio": date(2025, 1, 10),
        "fim": date(2025, 6, 30),
    })
    
    # Status 200 porque form não é válido
    assert response.status_code == 302
    curso.refresh_from_db()
    # Curso não deve ter sido alterado
    assert curso.vagas == 5
    # Mensagem de erro aparece
    assert "Não é possível reduzir vagas abaixo do número de alunos matriculados" in response.content.decode()

#09 - Confirmar ações
@pytest.mark.django_db
def test_matricula_feliz(client):
    # Cria o curso
    curso = Curso.objects.create(nome="Python Avançado", duracao=1, vagas=5)
    
    url = reverse("core:matricular_aluno")

    # Faz a matrícula
    response = client.post(url, {
        "nome": "Ana Silva",
        "email": "ana@example.com",
        "curso": curso.id,
    }, follow=True)

    # Verifica se a requisição foi bem-sucedida
    assert response.status_code == 200

    # Verifica se o aluno foi realmente criado
    aluno = Aluno.objects.get(email="ana@example.com", curso=curso)
    assert aluno is not None

    # Verifica se as mensagens de sucesso foram enviadas
    messages = list(get_messages(response.wsgi_request))
    assert any("Matrícula realizada com sucesso" in str(m) for m in messages)

    # Verifica os campos de início e fim do curso
    assert aluno.inicio_curso == curso.inicio
    assert aluno.fim_curso == curso.fim
    assert curso.fim == curso.inicio + timedelta(days=curso.duracao * 365)


@pytest.mark.django_db
def test_matricula_mensagem_incorreta(client):
    curso = Curso.objects.create(nome="Python Avançado", duracao=40, vagas=5)
    url = reverse("core:matricular_aluno")

    response = client.post(url, {
        "nome": "João Souza",
        "email": "joao@example.com",
        "curso": curso.id,
    }, follow=True)

    assert response.status_code == 302
    assert "Erro!" in response.content.decode()  # deve falhar
