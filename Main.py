import base64
import binascii
import subprocess
import tempfile
from Client import Client


def exibir_menu():
    print("\n===== MENU =====")
    print("1 - Somar")
    print("2 - Subtrair")
    print("3 - Multiplicar")
    print("4 - Solicitar imagem ao servidor")
    print("0 - Encerrar Conexão")
    print("Formato: opcao;valor1;valor2  (ex: 1;2;3)")
    print("Para imagem: digite 4")


def preparar_mensagem(entrada):
    partes = entrada.split(";")
    opcao = partes[0].strip()

    if opcao == "4":
        return "4"

    # Opções 1, 2, 3 (e qualquer outra que o servidor saiba tratar)
    return entrada


def main():
    client = Client("127.0.0.1", 12345)
    client.conectar()

    if not client.esta_conectado():
        return

    # --- Handshake inicial ---
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
            if resposta is not None:
                opcao = entrada.split(";", 1)[0].strip()
                if opcao == "4":
                    abrir_imagem_recebida(resposta)
                else:
                    print(f"[Servidor] {resposta}")
            else:
                break
        else:
            break

    client.fechar()


def abrir_imagem_recebida(resposta):
    """Decodifica a resposta Base64 e abre a imagem temporária no Firefox."""
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
