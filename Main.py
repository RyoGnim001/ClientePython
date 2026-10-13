import base64
import binascii
import subprocess
import tempfile

import javaobj.v2 as javaobj

from Client import Client


def exibir_menu():
    print("\n===== MENU =====")
    print("1 - Somar")
    print("2 - Subtrair")
    print("3 - Multiplicar")
    print("4 - Solicitar imagem ao servidor")
    print("5 - Solicitar objeto Aluno (serializado — apenas cliente Java desserializa)")
    print("0 - Encerrar Conexão")
    print("Formato: opcao;valor1;valor2  (ex: 1;2;3)")
    print("Para imagem ou aluno: digite apenas a opção")


def preparar_mensagem(entrada):
    partes = entrada.split(";")
    opcao = partes[0].strip()

    if opcao in ("4", "5"):
        return opcao

    return entrada


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

def main():
    client = Client("127.0.0.1", 12345)
    client.conectar()

    if not client.esta_conectado():
        return

    id_linha = client.receber_linha()
    if id_linha and id_linha.startswith("__ID__"):
        meu_id = id_linha.replace("__ID__", "").strip()
        print(f"Você é o client #{meu_id}")

    boas_vindas = client.receber_linha()
    if boas_vindas:
        print(f"[Servidor] {boas_vindas}")

    exibir_menu()

    while True:
        entrada = input("\n> ").strip()

        if entrada == "0":
            client.enviar_mensagem("0")
            break

        if not entrada:
            continue

        mensagem = preparar_mensagem(entrada)
        if client.enviar_mensagem(mensagem):
            resposta = client.receber_resposta()
            if resposta is None:
                break

            opcao = entrada.split(";", 1)[0].strip()

            if opcao == "4":
                abrir_imagem_recebida(resposta)
            elif resposta.startswith("SERIALIZED;"):
                tratar_objeto_serializado(resposta)
            else:
                print(f"[Servidor] {resposta}")
        else:
            break

    client.fechar()


def abrir_imagem_recebida(resposta):
    if not resposta.startswith("OK;"):
        print(f"[Servidor] {resposta}")
        return

    dados_base64 = resposta[len("OK;"):]
    try:
        imagem = base64.b64decode(dados_base64, validate=True)
        with tempfile.NamedTemporaryFile(
            prefix="imagem-servidor-", suffix=".jpg", delete=False
        ) as arquivo:
            arquivo.write(imagem)
            caminho = arquivo.name

        subprocess.Popen(["firefox", caminho])
        print("Imagem aberta no Firefox.")
    except (ValueError, binascii.Error):
        print("O servidor enviou dados Base64 inválidos.")
    except OSError as e:
        print(f"Não foi possível salvar a imagem ou iniciar o Firefox: {e}")


if __name__ == "__main__":
    main()