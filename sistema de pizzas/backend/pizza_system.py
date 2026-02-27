# Atualizado: pizza_system.py com melhorias completas

import sqlite3
from abc import ABC, abstractmethod

# Conexão com banco SQLite
conn = sqlite3.connect("pizza_tree.db")
cursor = conn.cursor()

# Tabelas
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    sabor TEXT,
    endereco TEXT,
    tempo_entrega INTEGER,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)
''')

conn.commit()

# === HERANÇA PARA TIPOS DE PEDIDO ===
class PedidoBase:
    def __init__(self, sabor, endereco, tempo_entrega, cliente_nome):
        self.sabor = sabor
        self.endereco = endereco
        self.tempo_entrega = tempo_entrega
        self.cliente_nome = cliente_nome

    def calcular_preco(self):
        raise NotImplementedError("Método abstrato - deve ser implementado nas subclasses")

    def __str__(self):
        return f"{self.cliente_nome}: {self.sabor} - {self.endereco} ({self.tempo_entrega} min)"


class PedidoPadrao(PedidoBase):
    def __init__(self, sabor, endereco, tempo_entrega, cliente_nome):
        super().__init__(sabor, endereco, tempo_entrega, cliente_nome)
        self.tipo = "Padrão"

    def calcular_preco(self):
        return 35.00


class PedidoEspecial(PedidoBase):
    def __init__(self, sabor, endereco, tempo_entrega, cliente_nome, ingredientes_extras):
        super().__init__(sabor, endereco, tempo_entrega, cliente_nome)
        self.ingredientes_extras = ingredientes_extras
        self.tipo = "Especial"

    def calcular_preco(self):
        return 45.00 + (len(self.ingredientes_extras) * 2.50)


# === ÁRVORE DE PEDIDOS ===
class NoPedido:
    def __init__(self, pedido):
        self.pedido = pedido
        self.esquerda = None
        self.direita = None


class ArvorePedidos:
    def __init__(self):
        self.raiz = None

    def inserir(self, pedido):
        if self.raiz is None:
            self.raiz = NoPedido(pedido)
        else:
            self._inserir_recursivo(self.raiz, pedido)

    def _inserir_recursivo(self, no, pedido):
        if pedido.tempo_entrega < no.pedido.tempo_entrega:
            if no.esquerda is None:
                no.esquerda = NoPedido(pedido)
            else:
                self._inserir_recursivo(no.esquerda, pedido)
        else:
            if no.direita is None:
                no.direita = NoPedido(pedido)
            else:
                self._inserir_recursivo(no.direita, pedido)

    def remover(self, tempo_entrega):
        self.raiz = self._remover_recursivo(self.raiz, tempo_entrega)

    def _remover_recursivo(self, no, tempo_entrega):
        if no is None:
            return no
        if tempo_entrega < no.pedido.tempo_entrega:
            no.esquerda = self._remover_recursivo(no.esquerda, tempo_entrega)
        elif tempo_entrega > no.pedido.tempo_entrega:
            no.direita = self._remover_recursivo(no.direita, tempo_entrega)
        else:
            if no.esquerda is None:
                return no.direita
            elif no.direita is None:
                return no.esquerda
            temp = self._min_valor_no(no.direita)
            no.pedido = temp.pedido
            no.direita = self._remover_recursivo(no.direita, temp.pedido.tempo_entrega)
        return no

    def _min_valor_no(self, no):
        atual = no
        while atual.esquerda is not None:
            atual = atual.esquerda
        return atual

    def buscar(self, tempo_entrega):
        return self._buscar_recursivo(self.raiz, tempo_entrega)

    def _buscar_recursivo(self, no, tempo_entrega):
        if no is None:
            return None
        if no.pedido.tempo_entrega == tempo_entrega:
            return no.pedido
        elif tempo_entrega < no.pedido.tempo_entrega:
            return self._buscar_recursivo(no.esquerda, tempo_entrega)
        else:
            return self._buscar_recursivo(no.direita, tempo_entrega)

    def em_ordem(self):
        resultado = []
        self._em_ordem_recursivo(self.raiz, resultado)
        return resultado

    def _em_ordem_recursivo(self, no, resultado):
        if no:
            self._em_ordem_recursivo(no.esquerda, resultado)
            resultado.append(no.pedido)
            self._em_ordem_recursivo(no.direita, resultado)

    def calcular_total_pedidos(self):
        total = 0.0
        for pedido in self.em_ordem():
            if hasattr(pedido, 'calcular_preco'):
                total += pedido.calcular_preco()
        return total


# === ENCAPSULAMENTO MELHORADO PARA CLIENTES ===
class Cliente:
    def __init__(self, nome):
        self.__nome = nome
        self.__pedidos = ArvorePedidos()

    @property
    def nome(self):
        return self.__nome

    @property
    def pedidos(self):
        return self.__pedidos

    def adicionar_pedido(self, pedido):
        if not isinstance(pedido, PedidoBase):
            raise TypeError("Pedido deve ser uma instância de PedidoBase")
        self.__pedidos.inserir(pedido)

    def total_gasto(self):
        return self.__pedidos.calcular_total_pedidos()


# === CLASSE ABSTRATA PARA ESTATÍSTICAS ===
class Estatisticas(ABC):
    @abstractmethod
    def gerar_relatorio(self):
        pass


class EstatisticasPizzaria(Estatisticas):
    def __init__(self, pizzaria):
        self.pizzaria = pizzaria

    def gerar_relatorio(self):
        relatorio = {
            "total_clientes": len(self.pizzaria.clientes),
            "total_pedidos": len(self.pizzaria.todos_pedidos.em_ordem()),
            "tempo_medio": self._calcular_tempo_medio(),
            "faturamento_total": self._calcular_faturamento()
        }
        return relatorio

    def _calcular_tempo_medio(self):
        pedidos = self.pizzaria.todos_pedidos.em_ordem()
        if not pedidos:
            return 0
        return sum(p.tempo_entrega for p in pedidos) / len(pedidos)

    def _calcular_faturamento(self):
        return self.pizzaria.todos_pedidos.calcular_total_pedidos()


# === CLASSE PIZZARIA ===
class Pizzaria:
    def __init__(self):
        self.clientes = {}
        self.todos_pedidos = ArvorePedidos()

    def calcular_tempo_entrega(self, endereco):
        distancias = {
            "asa norte": 2, "asa sul": 5, "lago norte": 7,
            "lago sul": 12, "sudoeste": 10, "cruzeiro": 11,
            "noroeste": 4, "águas claras": 23, "taguatinga": 25,
            "samambaia": 30, "ceilândia": 35, "gama": 40
        }
        tempo_preparo = 15
        tempo_por_km = 2
        distancia = distancias.get(endereco.lower(), 10)
        return tempo_preparo + distancia * tempo_por_km

    def adicionar_pedido(self, nome_cliente, sabor, endereco):
        tempo = self.calcular_tempo_entrega(endereco)
        cursor.execute("SELECT id FROM clientes WHERE nome = ?", (nome_cliente,))
        cliente = cursor.fetchone()

        if cliente:
            cliente_id = cliente[0]
        else:
            cursor.execute("INSERT INTO clientes (nome) VALUES (?)", (nome_cliente,))
            cliente_id = cursor.lastrowid
            conn.commit()
            self.clientes[nome_cliente] = Cliente(nome_cliente)

        cursor.execute('''
            INSERT INTO pedidos (cliente_id, sabor, endereco, tempo_entrega)
            VALUES (?, ?, ?, ?)
        ''', (cliente_id, sabor, endereco, tempo))
        conn.commit()

        novo_pedido = PedidoPadrao(sabor, endereco, tempo, nome_cliente)

        if nome_cliente in self.clientes:
            self.clientes[nome_cliente].adicionar_pedido(novo_pedido)
        else:
            self.clientes[nome_cliente] = Cliente(nome_cliente)
            self.clientes[nome_cliente].adicionar_pedido(novo_pedido)

        self.todos_pedidos.inserir(novo_pedido)
        print(f"✅ Pedido de {sabor} adicionado para {nome_cliente} ({tempo} min).")

    def remover_pedido(self, tempo_entrega):
        pedido = self.todos_pedidos.buscar(tempo_entrega)
        if pedido and pedido.cliente_nome in self.clientes:
            self.clientes[pedido.cliente_nome].pedidos.remover(tempo_entrega)
            self.todos_pedidos.remover(tempo_entrega)
            cursor.execute("DELETE FROM pedidos WHERE tempo_entrega = ?", (tempo_entrega,))
            conn.commit()
            print(f"🗑️ Pedido removido: {pedido}")
        else:
            print("❌ Pedido não encontrado.")

    def buscar_pedido_por_tempo(self, tempo_entrega):
        pedido = self.todos_pedidos.buscar(tempo_entrega)
        if pedido:
            print(f"🔍 Pedido encontrado: {pedido}")
        else:
            print("❌ Pedido não encontrado.")

    def mostrar_estrutura(self):
        print("\n🌳 Estrutura de Pedidos por Cliente:")
        for cliente in self.clientes.values():
            print(f"\n👤 Cliente: {cliente.nome}")
            pedidos = cliente.pedidos.em_ordem()
            for i, p in enumerate(pedidos, 1):
                print(f"   🍕 Pedido {i}: {p.sabor} - {p.endereco} - ETA: {p.tempo_entrega} min")

    def mostrar_arvore_completa(self):
        print("\n🌲 Árvore Completa de Pedidos:")
        for i, p in enumerate(self.todos_pedidos.em_ordem(), 1):
            print(f"  {i}. {p}")

    def gerar_estatisticas(self):
        estatisticas = EstatisticasPizzaria(self)
        relatorio = estatisticas.gerar_relatorio()
        print("\n📊 Estatísticas:")
        print(f"Clientes: {relatorio['total_clientes']}")
        print(f"Pedidos: {relatorio['total_pedidos']}")
        print(f"Tempo médio: {relatorio['tempo_medio']:.2f} min")
        print(f"Faturamento total: R${relatorio['faturamento_total']:.2f}")


# === INTERFACE ===
pizzaria = Pizzaria()

cursor.execute("SELECT c.nome, p.sabor, p.endereco, p.tempo_entrega FROM clientes c JOIN pedidos p ON c.id = p.cliente_id")
for nome, sabor, endereco, tempo in cursor.fetchall():
    pedido = PedidoPadrao(sabor, endereco, tempo, nome)
    if nome not in pizzaria.clientes:
        pizzaria.clientes[nome] = Cliente(nome)
    pizzaria.clientes[nome].adicionar_pedido(pedido)
    pizzaria.todos_pedidos.inserir(pedido)

while True:
    print("\n🍕 Sistema de Pedidos (OOP + Árvore + SQLite)")
    print("1️⃣ Novo Pedido")
    print("2️⃣ Mostrar Pedidos por Cliente")
    print("3️⃣ Mostrar Todos os Pedidos")
    print("4️⃣ Buscar Pedido por Tempo")
    print("5️⃣ Remover Pedido")
    print("6️⃣ Estatísticas")
    print("7️⃣ Sair")

    op = input("Escolha: ")

    if op == "1":
        nome = input("Nome do cliente: ")
        sabor = input("Sabor da pizza: ")
        endereco = input("Endereço de entrega: ")
        pizzaria.adicionar_pedido(nome, sabor, endereco)
    elif op == "2":
        pizzaria.mostrar_estrutura()
    elif op == "3":
        pizzaria.mostrar_arvore_completa()
    elif op == "4":
        try:
            tempo = int(input("Tempo de entrega para buscar: "))
            pizzaria.buscar_pedido_por_tempo(tempo)
        except ValueError:
            print("❌ Valor inválido.")
    elif op == "5":
        try:
            tempo = int(input("Tempo de entrega para remover: "))
            pizzaria.remover_pedido(tempo)
        except ValueError:
            print("❌ Valor inválido.")
    elif op == "6":
        pizzaria.gerar_estatisticas()
    elif op == "7":
        print("👋 Saindo...")
        break
    else:
        print("❌ Opção inválida.")

conn.close()
 