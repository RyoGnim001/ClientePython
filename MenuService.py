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