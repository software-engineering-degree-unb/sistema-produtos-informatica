<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Top <?php echo $resultado['filtros']['limite']; ?> Clientes</title>
    <link rel="icon" type="image/x-icon" href="../public/assets/img/icon.ico">
    <link href="../public/assets/css/relatorio-vendas.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .filter-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .filter-form {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: flex-end;
        }
        
        .filter-group {
            flex: 1;
            min-width: 200px;
        }
        
        .filter-buttons {
            display: flex;
            gap: 10px;
        }
        
        .cliente-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .cliente-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .cliente-rank {
            position: absolute;
            top: 0;
            right: 0;
            background-color: #0f2566;
            color: white;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            border-bottom-left-radius: 8px;
        }
        
        .cliente-info {
            display: flex;
            margin-bottom: 15px;
        }
        
        .cliente-avatar {
            width: 80px;
            height: 80px;
            background-color: #e9ecef;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            color: #0f2566;
            font-size: 2em;
            font-weight: bold;
        }
        
        .cliente-main {
            flex: 1;
        }
        
        .cliente-nome {
            font-size: 1.3em;
            font-weight: bold;
            color: #0f2566;
            margin-bottom: 5px;
        }
        
        .cliente-email {
            color: #6c757d;
            margin-bottom: 10px;
        }
        
        .cliente-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #0f2566;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .produtos-preferidos {
            margin-top: 15px;
        }
        
        .produtos-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 5px;
        }
        
        .produto-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            padding: 5px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        
        .produto-item-img {
            width: 30px;
            height: 30px;
            background-color: #e9ecef;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
        }
        
        .produto-item-info {
            flex: 1;
        }
        
        .produto-item-nome {
            font-weight: 500;
        }
        
        .produto-item-freq {
            font-size: 0.9em;
            color: #6c757d;
        }
        
        .resumo-container {
            margin-bottom: 30px;
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .resumo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .chart-container {
            height: 400px;
            margin-bottom: 30px;
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .clientes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .top-3 {
            border-left: 4px solid #ffc107;
        }
        
        .top-1 {
            border-left: 4px solid #28a745;
        }
        
        @media (max-width: 768px) {
            .clientes-grid {
                grid-template-columns: 1fr;
            }
            
            .filter-form {
                flex-direction: column;
            }
            
            .filter-group, .filter-buttons {
                width: 100%;
            }
        }
        
        @media print {
            .no-print {
                display: none !important;
            }
            
            .content {
                width: 100% !important;
            }
            
            .clientes-grid {
                grid-template-columns: 1fr;
            }
            
            .cliente-card {
                page-break-inside: avoid;
                box-shadow: none;
                border: 1px solid #dee2e6;
            }
            
            .chart-container {
                page-break-inside: avoid;
                page-break-after: always;
            }
        }
    </style>
</head>
<body class="loggedin">
    <nav class="navtop no-print">
        <div class="nav-left">
            <img src="../public/assets/img/logo2.png" alt="">
        </div>
        <div class="nav-right">
            <a href="../public/index.php?controller=home&action=index"><i class="fas fa-house"></i>Página Inicial</a>
            <a href="../public/index.php?controller=produto&action=listProdutos"><i class="fas fa-shopping-bag"></i>Produtos</a>
            <a href="../public/index.php?controller=compra&action=relatorioVendas"><i class="fas fa-chart-line"></i>Relatório de Vendas</a>
            <a href="../public/index.php?controller=compra&action=relatorioMensal"><i class="fas fa-calendar-alt"></i>Relatório Mensal</a>
            <a href="../public/index.php?controller=profile&action=index"><i class="fas fa-user-circle"></i>Meu Perfil</a>
            <a href="../public/index.php?controller=auth&action=logout"><i class="fas fa-sign-out-alt"></i>Sair</a>
        </div>
    </nav>
    
    <div class="content">
        <h2>Top <?php echo count($resultado['clientes']); ?> Clientes</h2>
        
        <button class="btn btn-primary no-print" style="float: right; margin-bottom: 20px;" onclick="window.print();">
            <i class="fas fa-print"></i> Imprimir Relatório
        </button>
        
        <div class="filter-container no-print">
            <form action="../public/index.php" method="GET" class="filter-form">
                <input type="hidden" name="controller" value="compra">
                <input type="hidden" name="action" value="topClientes">
                
                <div class="filter-group">
                    <label for="limit">Número de clientes:</label>
                    <select id="limit" name="limit">
                        <option value="5" <?php echo $resultado['filtros']['limite'] == 5 ? 'selected' : ''; ?>>Top 5</option>
                        <option value="10" <?php echo $resultado['filtros']['limite'] == 10 ? 'selected' : ''; ?>>Top 10</option>
                        <option value="20" <?php echo $resultado['filtros']['limite'] == 20 ? 'selected' : ''; ?>>Top 20</option>
                        <option value="50" <?php echo $resultado['filtros']['limite'] == 50 ? 'selected' : ''; ?>>Top 50</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="orderBy">Ordenar por:</label>
                    <select id="orderBy" name="orderBy">
                        <option value="valorTotal" <?php echo $resultado['filtros']['ordenacao'] == 'valorTotal' ? 'selected' : ''; ?>>Valor Total</option>
                        <option value="totalCompras" <?php echo $resultado['filtros']['ordenacao'] == 'totalCompras' ? 'selected' : ''; ?>>Número de Compras</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="periodo">Período:</label>
                    <select id="periodo" name="periodo">
                        <option value="" <?php echo $resultado['filtros']['periodo'] == '' ? 'selected' : ''; ?>>Todo o período</option>
                        <option value="mes" <?php echo $resultado['filtros']['periodo'] == 'mes' ? 'selected' : ''; ?>>Último mês</option>
                        <option value="trimestre" <?php echo $resultado['filtros']['periodo'] == 'trimestre' ? 'selected' : ''; ?>>Último trimestre</option>
                        <option value="semestre" <?php echo $resultado['filtros']['periodo'] == 'semestre' ? 'selected' : ''; ?>>Último semestre</option>
                        <option value="ano" <?php echo $resultado['filtros']['periodo'] == 'ano' ? 'selected' : ''; ?>>Último ano</option>
                    </select>
                </div>
                
                <div class="filter-buttons">
                    <button type="submit" class="btn btn-primary">Aplicar Filtros</button>
                </div>
            </form>
        </div>
        
        <div class="resumo-container">
            <h3>Resumo Geral</h3>
            <div class="resumo-grid">
                <div class="stat-box">
                    <div class="stat-value"><?php echo number_format($resultado['estatisticas']['totalClientes'], 0, ',', '.'); ?></div>
                    <div class="stat-label">Clientes Totais</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-value">R$ <?php echo number_format($resultado['estatisticas']['valorTotalGeral'], 2, ',', '.'); ?></div>
                    <div class="stat-label">Valor Total em Vendas</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-value"><?php echo number_format($resultado['estatisticas']['percentualValorTop'], 1, ',', '.'); ?>%</div>
                    <div class="stat-label">% do Valor Total Representado pelo Top</div>
                </div>
                
                <div class="stat-box">
                    <div class="stat-value"><?php echo number_format($resultado['estatisticas']['percentualComprasTop'], 1, ',', '.'); ?>%</div>
                    <div class="stat-label">% das Compras Representadas pelo Top</div>
                </div>
            </div>
        </div>
        
        <?php if (!empty($resultado['clientes'])): ?>
            <div class="chart-container">
                <canvas id="clientesChart"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="comprasChart"></canvas>
            </div>
            
            <h3>Detalhes por Cliente</h3>
            <div class="clientes-grid">
                <?php foreach ($resultado['clientes'] as $index => $cliente): 
                    $rank = $index + 1;
                    $extraClass = '';
                    if ($rank == 1) $extraClass = 'top-1';
                    else if ($rank <= 3) $extraClass = 'top-3';
                ?>
                <div class="cliente-card <?php echo $extraClass; ?>">
                    <div class="cliente-rank">#<?php echo $rank; ?></div>
                    <div class="cliente-info">
                        <div class="cliente-avatar">
                            <?php echo substr($cliente['nome'], 0, 1); ?>
                        </div>
                        <div class="cliente-main">
                            <div class="cliente-nome"><?php echo htmlspecialchars($cliente['nome']); ?></div>
                            <div class="cliente-email"><?php echo htmlspecialchars($cliente['email']); ?></div>
                        </div>
                    </div>
                    
                    <div class="cliente-stats">
                        <div class="stat-box">
                            <div class="stat-value"><?php echo number_format($cliente['totalCompras'], 0, ',', '.'); ?></div>
                            <div class="stat-label">Compras</div>
                        </div>
                        
                        <div class="stat-box">
                            <div class="stat-value">R$ <?php echo number_format($cliente['valorTotal'], 2, ',', '.'); ?></div>
                            <div class="stat-label">Valor Total</div>
                        </div>
                        
                        <div class="stat-box">
                            <div class="stat-value">R$ <?php echo number_format($cliente['mediaCompra'], 2, ',', '.'); ?></div>
                            <div class="stat-label">Média p/ Compra</div>
                        </div>
                    </div>
                    
                    <div class="cliente-history">
                        <div class="stat-label">Cliente desde: <?php echo date('d/m/Y', strtotime($cliente['primeiraCompra'])); ?></div>
                        <div class="stat-label">Última compra: <?php echo date('d/m/Y', strtotime($cliente['ultimaCompra'])); ?></div>
                    </div>
                    
                    <?php if (!empty($cliente['produtosPreferidos'])): ?>
                    <div class="produtos-preferidos">
                        <div class="produtos-title">Produtos mais comprados:</div>
                        <?php foreach ($cliente['produtosPreferidos'] as $produto): ?>
                        <div class="produto-item">
                            <div class="produto-item-img">
                                <i class="fas fa-box"></i>
                            </div>
                            <div class="produto-item-info">
                                <div class="produto-item-nome"><?php echo htmlspecialchars($produto['nomeProduto']); ?></div>
                                <div class="produto-item-freq">
                                    <?php echo $produto['frequencia']; ?> compras | 
                                    Total: <?php echo $produto['quantidadeTotal']; ?> unidades
                                </div>
                            </div>
                        </div>
                        <?php endforeach; ?>
                    </div>
                    <?php endif; ?>
                    
                    <div style="margin-top: 20px;">
                        <a href="../public/index.php?controller=compra&action=relatorioVendas&idUsuario=<?php echo $cliente['idUsuario']; ?>" class="btn btn-secondary no-print">
                            <i class="fas fa-search"></i> Ver Compras
                        </a>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="no-results">
                <p>Nenhum cliente encontrado com os filtros selecionados.</p>
            </div>
        <?php endif; ?>
    </div>
    
    <script>
        <?php if (!empty($resultado['clientes'])): ?>
        // Preparar dados para os gráficos
        var clientesNomes = <?php echo json_encode(array_column($resultado['clientes'], 'nome')); ?>;
        var clientesValores = <?php echo json_encode(array_map(function($c) { return (float)$c['valorTotal']; }, $resultado['clientes'])); ?>;
        var clientesCompras = <?php echo json_encode(array_map(function($c) { return (int)$c['totalCompras']; }, $resultado['clientes'])); ?>;
        
        // Gráfico de valor total por cliente
        var ctxValor = document.getElementById('clientesChart').getContext('2d');
        new Chart(ctxValor, {
            type: 'bar',
            data: {
                labels: clientesNomes,
                datasets: [{
                    label: 'Valor Total Gasto (R$)',
                    data: clientesValores,
                    backgroundColor: 'rgba(15, 37, 102, 0.7)',
                    borderColor: 'rgba(15, 37, 102, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: clientesNomes.length > 10 ? 'y' : 'x',
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return clientesNomes.length > 10 ? 
                                    value : 
                                    'R$ ' + value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                            }
                        }
                    },
                    x: {
                        ticks: {
                            callback: function(value) {
                                return clientesNomes.length > 10 ? 
                                    'R$ ' + value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : 
                                    value;
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Valor Total Gasto por Cliente',
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'R$ ' + context.parsed[clientesNomes.length > 10 ? 'x' : 'y'].toLocaleString('pt-BR', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                            }
                        }
                    }
                }
            }
        });
        
        // Gráfico de número de compras
        var ctxCompras = document.getElementById('comprasChart').getContext('2d');
        new Chart(ctxCompras, {
            type: 'bar',
            data: {
                labels: clientesNomes,
                datasets: [{
                    label: 'Número de Compras',
                    data: clientesCompras,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: clientesNomes.length > 10 ? 'y' : 'x',
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Número de Compras por Cliente',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
        <?php endif; ?>
    </script>
</body>
</html>