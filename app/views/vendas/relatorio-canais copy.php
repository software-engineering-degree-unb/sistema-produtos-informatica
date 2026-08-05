<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Relatório de Vendas por Canal</title>
    <link rel="icon" type="image/x-icon" href="../public/assets/img/icon.ico">
    <link href="../public/assets/css/relatorio-vendas.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
</head>
<body class="loggedin">
    <nav class="navtop">
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
        <h2>Relatório de Vendas por Canal</h2>
        
        <div class="filter-container">
            <form action="" method="GET" class="filter-form">
                <input type="hidden" name="controller" value="compra">
                <input type="hidden" name="action" value="relatorioVendasPorCanal">
                
                <div class="filter-group">
                    <label for="dataInicial">Data Inicial:</label>
                    <input type="date" id="dataInicial" name="dataInicial" value="<?php echo htmlspecialchars($filtros['dataInicial'] ?? ''); ?>">
                </div>
                
                <div class="filter-group">
                    <label for="dataFinal">Data Final:</label>
                    <input type="date" id="dataFinal" name="dataFinal" value="<?php echo htmlspecialchars($filtros['dataFinal'] ?? ''); ?>">
                </div>
                
                <div class="filter-group">
                    <label for="canal">Canal:</label>
                    <select id="canal" name="canal">
                        <option value="">Todos os canais</option>
                        <?php foreach ($canais as $canal): ?>
                            <option value="<?php echo htmlspecialchars($canal); ?>" <?php echo ($filtros['canal'] == $canal) ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($canal); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="filter-buttons">
                    <button type="submit" class="btn btn-primary">Filtrar</button>
                    <a href="../public/index.php?controller=compra&action=relatorioVendasPorCanal" class="btn btn-secondary">Limpar Filtros</a>
                </div>
            </form>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-label">Total de Vendas</div>
                <div class="stat-value"><?php echo number_format($totais['totalCompras'] ?? 0, 0, ',', '.'); ?></div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Valor Total (R$)</div>
                <div class="stat-value"><?php echo number_format($totais['valorTotal'] ?? 0, 2, ',', '.'); ?></div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Média por Venda (R$)</div>
                <div class="stat-value"><?php echo number_format($totais['mediaValor'] ?? 0, 2, ',', '.'); ?></div>
            </div>
        </div>
        
        <?php if (empty($vendasPorCanal)): ?>
            <div class="no-results">
                <p>Nenhuma venda encontrada com os filtros selecionados.</p>
            </div>
        <?php else: ?>
            <div class="table-responsive">
                <table class="vendas-table">
                    <thead>
                        <tr>
                            <th>Canal de Venda</th>
                            <th>Total de Vendas</th>
                            <th>Valor Total (R$)</th>
                            <th>Ticket Médio (R$)</th>
                            <th>% do Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($vendasPorCanal as $canal): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($canal['canalVenda'] ?? 'Não especificado'); ?></td>
                                <td><?php echo number_format($canal['totalCompras'], 0, ',', '.'); ?></td>
                                <td>R$ <?php echo number_format($canal['valorTotal'], 2, ',', '.'); ?></td>
                                <td>R$ <?php echo number_format($canal['mediaValor'], 2, ',', '.'); ?></td>
                                <td>
                                    <?php 
                                    $percentual = ($totais['valorTotal'] > 0) ? 
                                        ($canal['valorTotal'] / $totais['valorTotal']) * 100 : 0;
                                    echo number_format($percentual, 2, ',', '.') . '%'; 
                                    ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Verificar se as datas são válidas
            const dataInicialInput = document.getElementById('dataInicial');
            const dataFinalInput = document.getElementById('dataFinal');
            
            document.querySelector('form').addEventListener('submit', function(e) {
                const dataInicial = new Date(dataInicialInput.value);
                const dataFinal = new Date(dataFinalInput.value);
                
                if (dataInicialInput.value && dataFinalInput.value && dataFinal < dataInicial) {
                    e.preventDefault();
                    alert('A data final não pode ser anterior à data inicial.');
                }
            });
        });
    </script>
</body>
</html>