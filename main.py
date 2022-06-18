from db.database import Database

produtoDAO = Database(database="LojaIng", collection="Produtos")
carrinhoDAO = Database(database="LojaIng", collection="Carrinho")
usuarioDAO = Database(database="LojaIng", collection="Usuarios")

class Produto(object):
    def __init__(self, nomeProduto, descricao, quantidade, valor, idVend):
        self.nomeProduto = nomeProduto
        self.descricao = descricao
        self.quantidade = quantidade
        self.valor = valor
        self.idVend = idVend

    def createProduto(idVend):
        nome = input("Digite o nome do produto: ")
        descricao = input("Insira uma descrição para o produto: ")
        quantidade = int(input("Insira a quantidade total do produto: "))
        valor = float(input("Digite o valor do produto com 2xCasas de precisao(0.00): "))
        produt = Produto(nomeProduto=nome, descricao=descricao, quantidade=quantidade, valor=valor, idVend=int(idVend))
        return produt

class Usuario(object):
    def __init__(self, nomeUser, sexo, senha, telefone, vendedor):
        self.nomeUser = nomeUser
        self.sexo = sexo
        self.senha = senha
        self.telefone = telefone
        self.vendedor = vendedor

    def CriarUser(op):
        nomeUser = input("Digite um nome de usuario: ")      
        auxuser = usuarioDAO.collection.find({"user.nomeUser": nomeUser})
        while len(list(auxuser)) != 0:
            print(f'Usuario "{nomeUser}" já está sendo utilizado!')
            nomeUser = input("Digite um nome de usuario: ")
            auxuser = usuarioDAO.collection.find({"user.nomeUser": nomeUser})
        user = Usuario(
            nomeUser=nomeUser, 
            senha=input("Digite uma senha: "),
            sexo=input("Digite seu sexo:\n F - Feminino\n M - Masculino \n NI - Não informar\nOpção: ").upper(),
            telefone= input("Insira seu telefone: "),
            vendedor= bool(True if op == 'S' else False)
        )
        if(op == 'S'):
            vendedor = Vendedor(
                nomeVen= input("Digite o seu nome: "),
                idVend= int(usuarioDAO.collection.find({"idVend":{"$exists": True}}).sort("idVend", -1)[0]["idVend"]+1),
                user= user
            )
            return vendedor
        elif(op == 'N'):
            cliente = Cliente(
                nomeCli= input("Digite o seu nome: "),
                endereco= input("Insira seu endereco: "),
                idCli= int(usuarioDAO.collection.find({"idCli":{"$exists": True}}).sort("idCli", -1)[0]["idCli"]+1),
                user= user
            )
            return cliente
    
    def login(user):
        useraux = list(usuarioDAO.collection.find({"user.nomeUser": user.nomeUser}))
        while len(useraux) == 0:
            print('Usuário não existe!')
            user.nomeUser = input('Digite o login: ')
            useraux = list(usuarioDAO.collection.find({"user.nomeUser": user.nomeUser}))
        
        if useraux[0]['user']['senha'] != user.senha:
            count = 3
            while useraux[0]['user']['senha'] != user.senha and count > 0:
                print('Senha incorreta')
                user.senha = input('Digite a senha: ')
                count -= 1
            if count == 0:
                print("Login falhou!")
                return None
        return useraux[0]

class Vendedor(object):
    def __init__(self, nomeVen, idVend, user):
        self.nomeVen = nomeVen
        self.idVend = idVend
        self.user = user

    def createVendedor(vendedor):
        usuarioDAO.collection.insert_one({"nomeVen": vendedor.nomeVen,
                                           "idVend": vendedor.idVend,
                                           "user": {
                                                "nomeUser": vendedor.user.nomeUser,
                                                "sexo": vendedor.user.sexo,
                                                "senha": vendedor.user.senha,
                                                "telefone": vendedor.user.telefone, 
                                                "vendedor": vendedor.user.vendedor
                                            }
                                        })
    
    def ven_to_obj(vendedor):
        user = Usuario(nomeUser=vendedor['user']['nomeUser'], senha=vendedor['user']['senha'], sexo=vendedor['user']['sexo'], telefone=vendedor['user']['telefone'], vendedor=vendedor['user']['vendedor'])
        return vendedor['nomeVen'], vendedor['idVend'], user

    def estoque(vendedor, cli):
        if cli == 0:
            nomeVen, idVend, user = Vendedor.ven_to_obj(vendedor)
            print(f"Olá Vendedora {vendedor['nomeVen']}, O que você deseja?\n 1. Inserir Produto\n 2. Ver o Estoque\n 3. Atualizar algum produto\n 4. Deletar algum produto\n 5. Sair")
            op = input("Opção: ")
            espaço()
            if op == '1':
                produto = Produto.createProduto(idVend=vendedor['idVend'])
                Estoque(nomeVen=nomeVen, idVend=idVend, user=user).InserirProduto(produto)
            elif op == '2':
                Estoque(nomeVen=nomeVen, idVend=idVend, user=user).mostrarProdutos()
            elif op == '3':
                estoque = Estoque(nomeVen=nomeVen, idVend=idVend, user=user).mostrarProdutos()
                Estoque(nomeVen=nomeVen, idVend=idVend, user=user).atualizarProduto(estoque)
            elif op == '4':
                estoque = Estoque(nomeVen=nomeVen, idVend=idVend, user=user).mostrarProdutos()
                Estoque(nomeVen=nomeVen, idVend=idVend, user=user).deletarProduto(estoque)
        elif cli == 1:
            return Estoque(nomeVen=vendedor.nomeVen, idVend=vendedor.idVend, user=vendedor.user).mostrarProdutos()
        espaço()
        if op == '5':
            return False
        return True

class Cliente(object):
    def __init__(self, nomeCli, endereco, idCli, user):
        self.nomeCli = nomeCli
        self.endereco = endereco
        self.idCli = idCli
        self.user = user

    def createCliente(cliente):
        usuarioDAO.collection.insert_one({"nomeCli": cliente.nomeCli, 
                                          "endereco": cliente.endereco,
                                          "idCli": cliente.idCli,
                                          "user": {
                                                "nomeUser": cliente.user.nomeUser,
                                                "sexo": cliente.user.sexo,
                                                "senha": cliente.user.senha,
                                                "telefone": cliente.user.telefone, 
                                                "vendedor": cliente.user.vendedor
                                            }
                                        })
        
    def atualizarPedido(cliente, ids, op):
        if op == '1':
            Carrinho(nomeCli=cliente['nomeCli'], endereco=cliente['endereco'], idCli=cliente['idCli'] ,user=cliente['user']).addItemCar(ids=ids)
        elif op == '2':
            finalizar = Carrinho(nomeCli=cliente['nomeCli'], endereco=cliente['endereco'], idCli=cliente['idCli'] ,user=cliente['user']).finalizarPedido(ids=ids)
            return finalizar
        elif op == '3':
            Carrinho(nomeCli=cliente['nomeCli'], endereco=cliente['endereco'], idCli=cliente['idCli'] ,user=cliente['user']).atualizarQuantidade(ids=ids)
        elif op == '4':
            return False
        return True

    def vendedor():
        vendedores = list(usuarioDAO.collection.find({"user.vendedor": True}))
        count = 0
        for aux in vendedores:
            count += 1
            print(f"Vedendor {count}: {aux['nomeVen']} | telefone: {aux['user']['telefone']}")
        op = int(input("Escolha o seu vendedor: "))
        return vendedores[op-1]['idVend']

class Estoque(Vendedor):
    produto = []

    def mostrarProdutos(self):
        self.produto = []
        auxprodutos = produtoDAO.collection.find({'idVend': self.idVend})
        print("Os itens do estoque são: ")
        count = 0
        for aux in auxprodutos:
            self.produto.append(aux)
            count += 1
            print(f"{count}. Produto: {aux['nomeProduto']} | Quantidade: {aux['quantidade']} | Valor: {aux['valor']} | Descrição: {aux['descricao']}")
        return self.produto

    def InserirProduto(self, produto):
        produtoDAO.collection.insert_one({"nomeProduto": produto.nomeProduto, "descricao": produto.descricao, 
                                              "quantidade": produto.quantidade,"valor": produto.valor, "idVend": produto.idVend})
        espaço()
                        
    def atualizarProduto(self, estoque):
        produto = int(input('Escolha o Produto que deseja modificar: '))
        op = input("O que deseja modificar no produtdo:\n   1.Nome\n   2.Descrição\n   3.Quantidade\n   4.Valor\nOpção: ")
        if op == '1':
            nome = input('Entre com o novo nome: ')
            print(self.idVend)
            print(estoque[produto-1]["nomeProduto"])
            print(nome)
            result = produtoDAO.collection.update_one(
                {"idVend": self.idVend, "nomeProduto": estoque[produto-1]["nomeProduto"]},
                {"$set":{"nomeProduto": nome}}
            )
        elif op == '2':
            descricao = input('Entre com a nova descrição: ')
            result = produtoDAO.collection.update_one(
                {"idVend": self.idVend, "nomeProduto": estoque[produto-1]["nomeProduto"]},
                {"$set":{"descricao": descricao}}
            )
        elif op == '3':
            quantidade = int(input('Entre com a nova quantidade: '))
            result = produtoDAO.collection.update_one(
                {"idVend": self.idVend, "nomeProduto": estoque[produto-1]["nomeProduto"]},
                {"$set":{"quantidade": quantidade}}
            )
        elif op == '4':
            valor = float(input('Entre com o novo valor: '))
            result = produtoDAO.collection.update_one(
                {"idVend": self.idVend, "nomeProduto": estoque[produto-1]["nomeProduto"]},
                {"$set":{"valor": valor}}
            )
        if result.acknowledged:
            print("Produto Atualizado!")
        else:
            print("Erro ao atualizar!\nTente novamente!")
        espaço()

    def deletarProduto(self, estoque):
        produto = int(input('Escolha o Produto que deseja deletar: '))
        result = produtoDAO.collection.delete_one({"nomeProduto": estoque[produto-1]["nomeProduto"], "idVend": self.idVend})

        if result.acknowledged:
            print("Produto Deletado!")
        else:
            print("Erro ao atualizar!\nTente novamente!")
        espaço()

class Carrinho(Cliente):
    listaCromp = []
    estoque = []

    def mostrarCarrinho(self, ids):
        print("*"*100)
        print(f"Seu carrinho contém: ")
        car = carrinhoDAO.collection.find_one({"idCar": ids[1]})
        car = car['produtos']
        count = 0
        total = 0
        for aux in car:
            print(f"{count+1}. Produto: {aux['nomeProduto']} | Quantidade: {aux['quantidade']} | Valor/un: {aux['valor']} | Valor Total: {round(aux['quantidade']*aux['valor'],2)}")
            total += round(aux['quantidade']*aux['valor'],2)
            count += 1
        print(f"Total: {total}")
        print("*"*100)
        return car

    def addItemCar(self, ids):
        self.estoque = []
        print(f"Vendedor {ids[0]}")
        vendedor = list(usuarioDAO.collection.find({"idVend": int(ids[0])}))   
        vendedor = Vendedor(
            nomeVen=vendedor[0]["nomeVen"],
            idVend=vendedor[0]["idVend"],
            user=vendedor[0]["user"]
        ) 
        self.estoque = Vendedor.estoque(vendedor=vendedor, cli=1)
        produto = int(input('Escolha o Produto que deseja comprar: '))
        quantidade = int(input('Informe a quantidade do Produto que deseja comprar: '))
        while self.estoque[produto-1]["quantidade"] < quantidade:
            print(f"Quantidade acima do estoque o mesmo possui: {self.estoque[produto-1]['quantidade']} do Produto {self.estoque[produto-1]['nomeProduto']}")
            quantidade = int(input('Informe a quantidade do Produto que deseja comprar: '))
        print(f"Carinho: {ids[1]}")
        numProd = carrinhoDAO.collection.find_one({"idCar": ids[1]})
        if len(numProd['produtos']) == 0:
            result = carrinhoDAO.collection.update_one(
                    {"idCar": ids[1]},
                    {"$set":{"produtos": [{
                        'nomeProduto': self.estoque[produto-1]['nomeProduto'],
                        'quantidade': quantidade,
                        'valor': self.estoque[produto-1]['valor']
                    }]}}
                )
        else:
            self.listaCromp = []
            index = 0
            for i in range(len(numProd['produtos'])):
                if numProd['produtos'][i]['nomeProduto'] == self.estoque[produto-1]['nomeProduto']:
                    numProd['produtos'][i]['quantidade'] += quantidade
                    index = i
                    if numProd['produtos'][i]['quantidade'] > self.estoque[produto-1]["quantidade"]:
                        print("Quantidade inválida! Necessário inserir novamente!")
                        break
                self.listaCromp.append(numProd['produtos'][i])
            if numProd['produtos'][index]['nomeProduto'] != self.estoque[produto-1]['nomeProduto']:
                produto = {
                    'nomeProduto': self.estoque[produto-1]['nomeProduto'],
                    'quantidade': quantidade,
                    'valor': self.estoque[produto-1]['valor']
                }
                self.listaCromp.append(produto)
            result = carrinhoDAO.collection.update_one(
                    {"idCar": ids[1]},
                    {"$set":{"produtos": self.listaCromp}}
                )
        if result.acknowledged:
            print("Carrinho Atualizado!")
        else:
            print("Erro ao atualizar!\nTente novamente!")
        espaço()

    def finalizarPedido(self, ids):
        car = self.mostrarCarrinho(ids)
        espaço()
        print(f"Senhor(a) {self.nomeCli} deseja finalizar o pedido(S/N)?")
        finalizar = input().upper()
        if finalizar == 'S':
            for aux in car:               
                quantidade_estoque = produtoDAO.collection.find_one({'idVend': ids[0], 'nomeProduto': aux['nomeProduto']}, {'quantidade': 1, '_id': 0})
                quantidade_carrinho = aux['quantidade']
                quantidade = quantidade_estoque['quantidade']-quantidade_carrinho
                produtoDAO.collection.update_one(
                    {"idVend": ids[0], "nomeProduto": aux['nomeProduto']},
                    {"$set":{"quantidade": int(quantidade)}}
                )
            print(f"Obrigado(a) {self.nomeCli}!")
            print("Pedido foi finalizado!\nO pedido será entrege nos próximos dias!")
            return False
        if finalizar == 'N':
            return True

    def atualizarQuantidade(self, ids):
        self.listaCromp = []
        car = self.mostrarCarrinho(ids)
        item = int(input('Escolha o Produto que deseja comprar: '))
        quantidade = int(input('Informe a nova quantidade do Produto que deseja comprar: '))
        for i, aux in zip(range(len(car)), car):
            if i == item-1:
                aux['quantidade'] = quantidade
                print(f"A quantidade do produto: {aux['nomeProduto']} foi alterado para {aux['quantidade']}, boas compras!")
            self.listaCromp.append(aux)
        carrinhoDAO.collection.update_one(
            {"idCar": ids[1]},
            {"$set":{'produtos': self.listaCromp} }           
        )

def espaço():
    print("*"*100)

def loja(user):
    espaço()
    print(f"Bem vindo!")
    loop = True
    while loop:
        if user['user']['vendedor']:
            loop = Vendedor.estoque(vendedor= user, cli=0)
        else:
            print(f"Olá {user['nomeCli']}, escolha de qual vendedor deseja comprar:")
            id = Cliente.vendedor()
            ids = [id, int(carrinhoDAO.collection.find({"idCar":{"$exists": True}}).sort("idCar", -1)[0]["idCar"]+1)]
            carrinhoDAO.collection.insert_one({
                "nomeCli": user['nomeCli'],
                "idCli": user['idCli'],
                "idCar": ids[1],
                "idVend": ids[0],
                "produtos": []
            })
            espaço()
            Cliente.atualizarPedido(cliente=user, ids=ids, op='1')
            while loop:
                op = input('Você deseja:\n 1. Continuar Comprando!\n 2. Finalizar Pedido!\n 3. Atualizar Quantidade do Produto!\nOpção: ')
                loop = Cliente.atualizarPedido(cliente=user, ids=ids, op=op)
                espaço()
                
loop = True
while loop:
    user = None
    espaço()
    op = input("Olá usuário, o que você deseja?\n 1. Entrar\n 2.Cadastrar\n 3. Sair\nOpção: ")
    if op == '1':
        useraux = Usuario(
            nomeUser= input("Digite seu usuario: "),
            senha= input("Digite sua senha: "),
            sexo= "NA",
            telefone= "NA",
            vendedor= "NA"
        )
        user = Usuario.login(user= useraux)
        espaço()
    elif op == '2':
        ven = input('Você é um vendedor(S/N)? ').upper()
        user = Usuario.CriarUser(op= ven)
        if ven == 'S':
            Vendedor.createVendedor(user)
            print('Usuário Vendedor Criado!')
        elif ven == 'N':
            Cliente.createCliente(user)
            print('Usuário Cliente Criado!')
            espaço()
        continue
    if user != None:
            loja(user)
    if user == None or op == '3':
        loop = False
        
