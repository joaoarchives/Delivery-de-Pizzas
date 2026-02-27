document.addEventListener('DOMContentLoaded', function() {
    
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            if (tabId === 'clientes') loadClientes();
            if (tabId === 'todos-pedidos') loadTodosPedidos('em-ordem');
            if (tabId === 'estatisticas') loadEstatisticas();
        });
    });

    document.getElementById('pedido-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nome = document.getElementById('nome').value;
        const sabor = document.getElementById('sabor').value;
        const endereco = document.getElementById('endereco').value;
        const tipo = document.getElementById('tipo-pedido').value;
        const extras = tipo === 'especial' ? 
            Array.from(document.querySelectorAll('input[name="ingrediente"]:checked')).map(el => el.value) : 
            null;
        
        fetch('http://localhost:5000/api/pedidos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nome: nome,
                sabor: sabor,
                endereco: endereco,
                tipo: tipo,
                extras: extras
            })
        })
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('pedido-result');
            resultDiv.innerHTML = `
                <div style="color: var(--success);">
                    <i class="fas fa-check-circle"></i> Pedido adicionado com sucesso!
                </div>
            `;
            pedidoForm.reset();
            document.getElementById('ingredientes-extras').style.display = 'none';

            // Reload relevant tabs
            setTimeout(() => {
                loadClientes();
                loadTodosPedidos('em-ordem');
                loadEstatisticas();
            }, 500);
        })
        .catch(error => {
            document.getElementById('pedido-result').innerHTML = `
                <div style="color: var(--danger);">
                    <i class="fas fa-exclamation-circle"></i> Erro ao adicionar pedido: ${error.message}
                </div>
            `;
        });
    });

    document.getElementById('tipo-pedido').addEventListener('change', function() {
        const extrasDiv = document.getElementById('ingredientes-extras');
        extrasDiv.style.display = this.value === 'especial' ? 'block' : 'none';
    });

    function loadClientes() {
        fetch('http://localhost:5000/api/clientes')
            .then(response => response.json())
            .then(data => {
                const clientesList = document.getElementById('clientes-list');
                let html = '';

                if (data.length === 0) {
                    html = '<p>Nenhum cliente encontrado.</p>';
                } else {
                    data.forEach(cliente => {
                        html += `
                            <div class="cliente-item">
                                <div class="cliente-nome">
                                    <span><i class="fas fa-user"></i> ${cliente.nome}</span>
                                    <span>${cliente.pedidos.length} pedido(s)</span>
                                </div>

                                ${cliente.pedidos.map(pedido => `
                                    <div class="pedido-item">
                                        <div><strong>Sabor:</strong> ${pedido.sabor}</div>
                                        <div><strong>Endereço:</strong> ${pedido.endereco}</div>
                                        <div class="tempo"><strong>Tempo:</strong> ${pedido.tempo} min</div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    });
                }

                clientesList.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('clientes-list').innerHTML = `
                    <div style="color: var(--danger);">
                        <i class="fas fa-exclamation-circle"></i> Erro ao carregar clientes.
                    </div>
                `;
            });
    }

    function loadTodosPedidos(method = 'em-ordem') {
        fetch('http://localhost:5000/api/pedidos')
            .then(response => response.json())
            .then(data => {
                const pedidosList = document.getElementById('pedidos-list');
                let html = '';

                if (data.length === 0) {
                    html = '<p>Nenhum pedido encontrado.</p>';
                } else {

                    if (method === 'em-ordem') {
                        data.sort((a, b) => a.tempo - b.tempo);
                    }
                    
                    html += `<p>Mostrando ${data.length} pedidos (${method.replace('-', ' ')}):</p>`;

                    data.forEach((pedido, index) => {
                        html += `
                            <div class="pedido-item">
                                <div><strong>#${index + 1}</strong> ${pedido.cliente}</div>
                                <div><strong>Sabor:</strong> ${pedido.sabor}</div>
                                <div><strong>Endereço:</strong> ${pedido.endereco}</div>
                                <div class="tempo"><strong>Tempo:</strong> ${pedido.tempo} min</div>
                                <button class="btn small danger" onclick="removerPedido(${pedido.tempo})">
                                    <i class="fas fa-trash"></i> Remover
                                </button>
                            </div>
                        `;
                    });
                }

                pedidosList.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('pedidos-list').innerHTML = `
                    <div style="color: var(--danger);">
                        <i class="fas fa-exclamation-circle"></i> Erro ao carregar pedidos.
                    </div>
                `;
            });
    }

    function loadEstatisticas() {
        fetch('http://localhost:5000/api/estatisticas')
            .then(response => response.json())
            .then(data => {
                document.getElementById('clientes-stats').innerHTML = `
                    <div class="stat-item">
                        <span class="stat-label">Total de Clientes:</span>
                        <span class="stat-value">${data.total_clientes || 'N/A'}</span>
                    </div>
                `;

                document.getElementById('pedidos-stats').innerHTML = `
                    <div class="stat-item">
                        <span class="stat-label">Total de Pedidos:</span>
                        <span class="stat-value">${data.total_pedidos || 'N/A'}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Pedido mais rápido:</span>
                        <span class="stat-value">${data.mais_rapido || 'N/A'} min</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Pedido mais demorado:</span>
                        <span class="stat-value">${data.mais_demorado || 'N/A'} min</span>
                    </div>
                `;

                document.getElementById('tempos-stats').innerHTML = `
                    <div class="stat-item">
                        <span class="stat-label">Tempo médio:</span>
                        <span class="stat-value">${data.tempo_medio ? data.tempo_medio.toFixed(2) : 'N/A'} min</span>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('clientes-stats').innerHTML = 'Erro ao carregar estatísticas.';
            });
    }

   
    document.getElementById('em-ordem-btn').addEventListener('click', () => loadTodosPedidos('em-ordem'));
    document.getElementById('pre-ordem-btn').addEventListener('click', () => loadTodosPedidos('pre-ordem'));
    document.getElementById('pos-ordem-btn').addEventListener('click', () => loadTodosPedidos('pos-ordem'));

    document.getElementById('search-btn').addEventListener('click', () => {
        const query = document.getElementById('cliente-search').value.toLowerCase();
        const clientes = document.querySelectorAll('.cliente-item');

        clientes.forEach(cliente => {
            const nome = cliente.querySelector('.cliente-nome span').textContent.toLowerCase();
            if (nome.includes(query)) {
                cliente.style.display = 'block';
            } else {
                cliente.style.display = 'none';
            }
        });
    });
});

function removerPedido(tempo) {
    if (confirm(`Tem certeza que deseja remover o pedido com tempo ${tempo} min?`)) {
        fetch(`http://localhost:5000/api/pedidos/${tempo}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            alert('Pedido removido com sucesso!');
            // Reload the views
            document.querySelectorAll('.tab-btn').forEach(btn => {
                if (btn.classList.contains('active')) {
                    btn.click(); // Simulate click to refresh current tab
                }
            });
        })
        .catch(error => {
            alert('Erro ao remover pedido: ' + error.message);
        });
    }
}
