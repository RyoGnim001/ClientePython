import base64
import binascii

import javaobj.v2 as javaobj


def tratar_objeto_serializado(resposta):
    """
    O servidor Java envia objetos no formato nativo do Java serializados
    e codificados em Base64. Aqui, usamos a biblioteca javaobj para
    desserializar e exibir os campos do objeto Aluno.
    """
    base64_dados = resposta[len("SERIALIZED;"):]
    try:
        # 1. Decodifica o Base64 para obter os bytes serializados do Java
        bytes_serializados = base64.b64decode(base64_dados, validate=True)

        # 2. Desserializa os bytes usando javaobj
        #    O método loads() aceita diretamente os bytes.
        aluno = javaobj.loads(bytes_serializados)

        # 3. Exibe os campos do objeto.
        #    O javaobj cria um objeto Python onde os campos são acessíveis
        #    como atributos ou através do método get_field().
        print("\n[SERVIDOR] Objeto Aluno recebido e desserializado:")
        print("----------------------------------------")
        # Tenta acessar como atributo (comum na v1) ou via get_field (v2/v3)
        try:
            # Para a implementação v2, os campos são acessíveis como atributos.
            print(f"Nome:      {aluno.nome}")
            print(f"Matrícula: {aluno.matricula}")
            print(f"Curso:     {aluno.curso}")
        except AttributeError:
            # Fallback para a implementação v3, que usa get_field()
            print(f"Nome:      {aluno.get_field('nome')}")
            print(f"Matrícula: {aluno.get_field('matricula')}")
            print(f"Curso:     {aluno.get_field('curso')}")
        print("----------------------------------------")

    except (ValueError, binascii.Error) as e:
        print(f"[Servidor] Erro ao decodificar Base64: {e}")
    except Exception as e:
        # Captura erros do javaobj (ex: classe não encontrada, formato inválido)
        print(f"[Servidor] Erro ao desserializar objeto Java: {e}")