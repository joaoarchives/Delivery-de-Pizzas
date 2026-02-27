from flask import Flask, request, jsonify  # type: ignore
from backend.pizza_system import Pizzaria, PedidoPadrao, PedidoEspecial, EstatisticasPizzaria
import json

app = Flask(__name__)
pizzaria = Pizzaria()

# === Factory Method ===
class PedidoFactory:
    @staticmethod
    def criar_pedido(tipo, nome, sabor, endereco, tempo, extras=None):
        if tipo == "padrao":
            return PedidoPadrao(sabor, endereco, tempo, nome)
        elif tipo == "especial":
            if not extras:
                raise ValueError("Pedidos especiais requerem ingredientes extras")
            return PedidoEspecial(sabor, endereco, tempo, nome, extras)
        else:
            raise ValueError("Tipo de pedido inválido")

@app.route('/api/pedidos', methods=['POST'])
def adicionar_pedido():
    data = request.json
    nome = data['nome']
    sabor = data['sabor']
    endereco = data['endereco']
    tipo = data.get('tipo', 'padrao')
    extras = data.get('extras', None)

    tempo = pizzaria.calcular_tempo_entrega(endereco)
    pedido = PedidoFactory.criar_pedido(tipo, nome, sabor, endereco, tempo, extras)
    pizzaria.adicionar_pedido(pedido)

    return jsonify({"status": "success", "preco": pedido.calcular_preco()})

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    pedidos = pizzaria.todos_pedidos.em_ordem()
    pedidos_data = [{
        "cliente": p.cliente_nome,
        "sabor": p.sabor,
        "endereco": p.endereco,
        "tempo": p.tempo_entrega
    } for p in pedidos]
    return jsonify(pedidos_data)

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    clientes_data = []
    for nome, cliente in pizzaria.clientes.items():
        pedidos = cliente.pedidos.em_ordem()
        clientes_data.append({
            "nome": nome,
            "pedidos": [{
                "sabor": p.sabor,
                "endereco": p.endereco,
                "tempo": p.tempo_entrega
            } for p in pedidos]
        })
    return jsonify(clientes_data)

@app.route('/api/pedidos/<int:tempo>', methods=['DELETE'])
def remover_pedido(tempo):
    pizzaria.remover_pedido(tempo)
    return jsonify({"status": "success"})

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    estatisticas = EstatisticasPizzaria(pizzaria)
    relatorio = estatisticas.gerar_relatorio()
    return jsonify({
        "total_clientes": relatorio["total_clientes"],
        "total_pedidos": relatorio["total_pedidos"],
        "tempo_medio": relatorio["tempo_medio"],
        "faturamento_total": relatorio["faturamento_total"]
    })

if __name__ == '__main__':
    app.run(debug=True)
