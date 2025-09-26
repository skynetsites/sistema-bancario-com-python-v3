from abc import ABC, abstractmethod
from datetime import datetime


# ===================== CLASSES DE CLIENTE =====================
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# ===================== CLASSES DE CONTA =====================
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("Operação falhou! Valor inválido.")
            return False
        elif valor > self._saldo:
            print("Operação falhou! Saldo insuficiente.")
            return False

        self._saldo -= valor
        print(f"Saque de R$ {valor:.2f} realizado com sucesso!")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Operação falhou! Valor inválido.")
            return False

        self._saldo += valor
        print(f"Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_realizados = 0

    def sacar(self, valor):
        if valor > self._limite:
            print("Operação falhou! O valor do saque excede o limite por operação.")
            return False
        elif self._saques_realizados >= self._limite_saques:
            print("Operação falhou! Número máximo de saques atingido.")
            return False
        elif super().sacar(valor):
            self._saques_realizados += 1
            return True
        return False


# ===================== HISTÓRICO =====================
class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    def exibir(self):
        print("\n================ EXTRATO ================")
        if not self.transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for t in self.transacoes:
                print(f"{t['tipo']}: R$ {t['valor']:.2f} em {t['data']}")
        print("==========================================")


# ===================== TRANSAÇÕES =====================
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self._valor):
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self._valor):
            conta.historico.adicionar_transacao(self)


# ===================== MAIN =====================
def main():
    clientes = []
    contas = []

    while True:
        opcao = input("""
[d] Depositar
[s] Sacar
[e] Extrato
[nu] Novo Usuário
[nc] Nova Conta
[lc] Listar Contas
[q] Sair
=> """).lower()

        if opcao == "nu":
            cpf = input("CPF (somente números): ")
            if any(c.cpf == cpf for c in clientes):
                print("Já existe um usuário com esse CPF!")
                continue

            nome = input("Nome completo: ")
            data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
            endereco = input("Endereço (Logradouro, Número - Bairro - Cidade/UF): ")

            cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
            clientes.append(cliente)
            print("Usuário criado com sucesso!")

        elif opcao == "nc":
            cpf = input("CPF do usuário: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)
            if not cliente:
                print("Usuário não encontrado!")
                continue

            numero_conta = len(contas) + 1
            conta = ContaCorrente.nova_conta(cliente, numero_conta)
            contas.append(conta)
            cliente.adicionar_conta(conta)
            print("Conta criada com sucesso!")

        elif opcao == "d":
            cpf = input("Informe o CPF do cliente: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)
            if not cliente or not cliente.contas:
                print("Cliente não encontrado ou sem conta.")
                continue

            valor = float(input("Valor do depósito: "))
            transacao = Deposito(valor)
            cliente.realizar_transacao(cliente.contas[0], transacao)

        elif opcao == "s":
            cpf = input("Informe o CPF do cliente: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)
            if not cliente or not cliente.contas:
                print("Cliente não encontrado ou sem conta.")
                continue

            valor = float(input("Valor do saque: "))
            transacao = Saque(valor)
            cliente.realizar_transacao(cliente.contas[0], transacao)

        elif opcao == "e":
            cpf = input("Informe o CPF do cliente: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)
            if not cliente or not cliente.contas:
                print("Cliente não encontrado ou sem conta.")
                continue

            conta = cliente.contas[0]
            conta.historico.exibir()
            print(f"Saldo atual: R$ {conta.saldo:.2f}")

        elif opcao == "lc":
            for conta in contas:
                print("=" * 30)
                print(f"Agência: {conta.agencia}")
                print(f"C/C: {conta.numero}")
                print(f"Titular: {conta.cliente.nome}")

        elif opcao == "q":
            print("Saindo do sistema. Obrigado por utilizar nosso banco!")
            break

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()
