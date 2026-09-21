import base64
import os
from Client import Client


def exibir_menu():
    print("\n===== MENU =====")
    print("1 - Somar")
    print("2 - Subtrair")
    print("3 - Multiplicar")
    print("4 - Enviar Imagem")
    print("0 - Encerrar Conexão")
    print("Formato: opcao;valor1;valor2  (ex: 1;2;3)")
    print("Para imagem: 4;caminho/da/imagem.png")


def preparar_mensagem(entrada):
    partes = entrada.split(";")
    opcao = partes[0].strip()

    if opcao == "4":
        if len(partes) < 2 or not partes[1].strip():
            print("Informe o caminho da imagem. Ex: 4;caminho/imagem.png")
            return None

        caminho = partes[1].strip()
        if not os.path.isfile(caminho):
            print(f"Arquivo não encontrado: {caminho}")
            return None

        try:
            with open(caminho, "rb") as f:
                # b64encode não insere quebras de linha no resultado,
                # então é seguro para um protocolo baseado em linhas.
                dados_b64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None

        nome_arquivo = os.path.basename(caminho)
        return f"4;{nome_arquivo};{dados_b64}"

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
        if mensagem is None:
            # Erro de validação (arquivo não encontrado, formato
            # inválido etc.) — volta a pedir uma entrada, sem gastar
            # uma ida e volta com o servidor.
            continue

        if client.enviar_mensagem(mensagem):
            resposta = client.receber_resposta()
            if resposta is not None:
                print(f"[Servidor] {resposta}")
            else:
                break
        else:
            break

    client.fechar()


if __name__ == "__main__":
    main()