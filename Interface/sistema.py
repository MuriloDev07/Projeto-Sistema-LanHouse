cores = {
"vermelho":"\033[31m",
"verde":"\033[32m",
"amarelo":"\033[33m",
"azul":"\033[34m",
"roxo":"\033[35m",
"ciano":"\033[36m",
"limpa":"\033[m"
}

def leiaInt(msg):
    while True:
        try:
            n = int(input(msg))
        except(TypeError, ValueError):
            print('Digite uma entrada válida!')
        except(KeyboardInterrupt):
            print('Usuário não digitou nada.')
            return(0)
        else:
            return(n)

def linha():
    print("-" * 30)

def cabecalho(txt):
    linha()
    print(txt.center(30))
    linha()

def menu():
    opcoes = {
    "1":"Listar categorias",
    "2":"Listar produtos",
    "3":"Sair"
    }
   
    for k, v in opcoes.items():
        print(f"{cores['amarelo']}{k}{cores['limpa']} - {cores['azul']}{v}{cores['limpa']}")
    linha()

def sistema():
    cabecalho("MENU")
    menu()

    while True:
        opc = leiaInt("Sua opção: ")

        if opc in (1, 2, 3):
            return opc

        print(f"{cores["vermelho"]}Opção Inválida! Digite uma opção válida!{cores["limpa"]}")
