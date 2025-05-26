<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Relatório Mensal de Vendas - <?php echo $relatorio['anoSelecionado']; ?></title>
    <link rel="icon" type="image/x-icon" href="../public/assets/img/icon.ico">
    <link href="../public/assets/css/relatorio-vendas.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .year-selector {
            text-align: center;
            margin-bottom: 25px;
        }
        
        .year-selector select {
            padding: 8px 15px;
            border-radius: 4px;
            border: 1px solid #ced4da;
            margin: 0 10px;
        }
        
        .chart-container {
            margin: 30px 0;
            height: 400px;
        }
        
        .stats-yearly {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #0f2566;
        }
        
        .stats-yearly h3 {
            margin-top: 0;
            color: #0f2566;
        }
        
        .month-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .month-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            transition: transform 0.3s ease;
        }
        
        .month-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .month-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #0f2566;
            margin-bottom: 15px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        
        .month-stat {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .month-stat-label {
            color: #6c757d;
        }
        
        .month-stat-value {
            font-weight: 600;
        }
        
        .month-card.best {
            border: 2px solid #28a745;
        }
        
        .month-card.worst {
            border: 2px solid #dc3545;
        }
        
        .print-btn {
            float: right;
            margin-bottom: 20px;
        }
        
        @media print {
            .no-print {
                display: none !important;
            }
            
            .content {
                width: 100% !important;
                padding: 0 !important;
            }
            
            .chart-container {
                page-break-inside: avoid;
                page-break-after: always;
            }
            
            .month-grid {
                grid-template-columns: repeat(3, 1fr);
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
            <a href="../public/index.php?controller=profile&action=index"><i class="fas fa-user-circle"></i>Meu Perfil</a>
            <a href="../public/index.php?controller=auth&action=logout"><i class="fas fa-sign-out-alt"></i>Sair</a>
        </div>
    </nav>
    
    <div class="content">
        <h2>Relatório Mensal de Vendas - <?php echo $relatorio['anoSelecionado']; ?></h2>
        
        <button class="btn btn-primary print-btn no-print" onclick="window.print();">
            <i class="fas fa-print"></i> Imprimir Relatório
        </button>
        
        <div class="year-selector no-print">
            <form action="../public/index.php" method="GET">
                <input type="hidden" name="controller" value="compra">
                <input type="hidden" name="action" value="relatorioMensal">
                
                <label for="ano">Selecione o ano:</label>
                <select id="ano" name="ano" onchange="this.form.submit()">
                    <?php foreach ($relatorio['anosDisponiveis'] as $ano): ?>
                        <option value="<?php echo $ano; ?>" <?php echo $ano == $relatorio['anoSelecionado'] ? 'selected' : ''; ?>>
                            <?php echo $ano; ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </form>
        </div>
        
        <div class="stats-yearly">
            <h3>Resumo Anual - <?php echo $relatorio['anoSelecionado']; ?></h3>
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-label">Total de Vendas</div>
                    <div class="stat-value"><?php echo number_format($relatorio['estatisticasAnuais']['totalCompras'], 0, ',', '.'); ?></div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Valor Total (R$)</div>
                    <div class="stat-value"><?php echo number_format($relatorio['estatisticasAnuais']['valorTotal'], 2, ',', '.'); ?></div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Média por Venda (R$)</div>
                    <div class="stat-value"><?php echo number_format($relatorio['estatisticasAnuais']['valorMedio'], 2, ',', '.'); ?></div>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="vendasMensaisChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="volumeMensalChart"></canvas>
        </div>
        
        <h3>Detalhamento Mensal</h3>
        <div class="month-grid">
            <?php 
            // Encontrar melhor e pior mês
            $melhorMes = 0;
            $piorMes = 0;
            $maiorValor = 0;
            $menorValor = PHP_FLOAT_MAX;
            
            foreach ($relatorio['dadosMensais'] as $dadosMes) {
                if ($dadosMes['valorTotal'] > $maiorValor && $dadosMes['valorTotal'] > 0) {
                    $maiorValor = $dadosMes['valorTotal'];
                    $melhorMes = $dadosMes['mes'];
                }
                
                if ($dadosMes['valorTotal'] < $menorValor && $dadosMes['valorTotal'] > 0) {
                    $menorValor = $dadosMes['valorTotal'];
                    $piorMes = $dadosMes['mes'];
                }
            }
            
            foreach ($relatorio['dadosMensais'] as $dadosMes): 
                $classeMes = '';
                if ($dadosMes['mes'] == $melhorMes) $classeMes = 'best';
                if ($dadosMes['mes'] == $piorMes && $dadosMes['totalCompras'] > 0) $classeMes = 'worst';
            ?>
                <div class="month-card <?php echo $classeMes; ?>">
                    <div class="month-title"><?php echo $dadosMes['nomeMes']; ?></div>
                    
                    <div class="month-stat">
                        <div class="month-stat-label">Total de Vendas:</div>
                        <div class="month-stat-value"><?php echo number_format($dadosMes['totalCompras'], 0, ',', '.'); ?></div>
                    </div>
                    
                    <div class="month-stat">
                        <div class="month-stat-label">Valor Total:</div>
                        <div class="month-stat-value">R$ <?php echo number_format($dadosMes['valorTotal'], 2, ',', '.'); ?></div>
                    </div>
                    
                    <div class="month-stat">
                        <div class="month-stat-label">Valor Médio:</div>
                        <div class="month-stat-value">R$ <?php echo number_format($dadosMes['valorMedio'], 2, ',', '.'); ?></div>
                    </div>
                    
                    <div class="month-stat">
                        <div class="month-stat-label">Menor Venda:</div>
                        <div class="month-stat-value">R$ <?php echo $dadosMes['totalCompras'] > 0 ? number_format($dadosMes['valorMinimo'], 2, ',', '.') : '0,00'; ?></div>
                    </div>
                    
                    <div class="month-stat">
                        <div class="month-stat-label">Maior Venda:</div>
                        <div class="month-stat-value">R$ <?php echo $dadosMes['totalCompras'] > 0 ? number_format($dadosMes['valorMaximo'], 2, ',', '.') : '0,00'; ?></div>
                    </div>
                    
                    <div class="month-stat">
                        <a href="../public/index.php?controller=compra&action=relatorioVendas&dataInicial=<?php echo $relatorio['anoSelecionado']; ?>-<?php echo str_pad($dadosMes['mes'], 2, '0', STR_PAD_LEFT); ?>-01&dataFinal=<?php echo $relatorio['anoSelecionado']; ?>-<?php echo str_pad($dadosMes['mes'], 2, '0', STR_PAD_LEFT); ?>-31" class="btn btn-secondary no-print">
                            <i class="fas fa-search"></i> Ver Detalhes
                        </a>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>
    </div>
    
    <script>
        // Dados para os gráficos
        var meses = <?php echo json_encode(array_column($relatorio['dadosMensais'], 'nomeMes')); ?>;
        var valoresTotal = <?php echo json_encode(array_map(function($item) { return (float)$item['valorTotal']; }, $relatorio['dadosMensais'])); ?>;
        var quantidadesVendas = <?php echo json_encode(array_map(function($item) { return (int)$item['totalCompras']; }, $relatorio['dadosMensais'])); ?>;
        
        // Gráfico de valores mensais
        var ctxValores = document.getElementById('vendasMensaisChart').getContext('2d');
        var vendasMensaisChart = new Chart(ctxValores, {
            type: 'bar',
            data: {
                labels: meses,
                datasets: [{
                    label: 'Valor Total (R$)',
                    data: valoresTotal,
                    backgroundColor: 'rgba(15, 37, 102, 0.7)',
                    borderColor: 'rgba(15, 37, 102, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Valor Total de Vendas por Mês',
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'R$ ' + context.parsed.y.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                            }
                        }
                    }
                }
            }
        });
        
        // Gráfico de quantidade de vendas mensais
        var ctxQuantidade = document.getElementById('volumeMensalChart').getContext('2d');
        var volumeMensalChart = new Chart(ctxQuantidade, {
            type: 'line',
            data: {
                labels: meses,
                datasets: [{
                    label: 'Quantidade de Vendas',
                    data: quantidadesVendas,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.1,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
                        text: 'Quantidade de Vendas por Mês',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>