<?php
class Compra {
    private $conn;

    public function __construct($db) {
        $this->conn = $db;
    }

    public function registrarCompra($idUsuario, $itens) {
        try {
            $this->conn->beginTransaction();
            
            // Calcular valor total da compra
            $valorTotal = 0;
            foreach ($itens as $item) {
                $valorTotal += $item['price'] * $item['quantity'];
            }
            
            // Inserir cabeçalho da compra
            $query = "INSERT INTO compra (idUsuario, valorTotal) VALUES (:idUsuario, :valorTotal)";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':idUsuario', $idUsuario, PDO::PARAM_INT);
            $stmt->bindParam(':valorTotal', $valorTotal, PDO::PARAM_STR);
            
            if (!$stmt->execute()) {
                throw new Exception("Erro ao registrar a compra");
            }
            
            $idCompra = $this->conn->lastInsertId();
            
            // Inserir itens da compra
            $queryItem = "INSERT INTO item_compra (idCompra, idProduto, quantidade, valorUnitario, valorTotal) 
                         VALUES (:idCompra, :idProduto, :quantidade, :valorUnitario, :valorTotal)";
            $stmtItem = $this->conn->prepare($queryItem);
            
            foreach ($itens as $item) {
                $idProduto = $item['id'];
                $quantidade = $item['quantity'];
                $valorUnitario = $item['price'];
                $valorItemTotal = $valorUnitario * $quantidade;
                
                $stmtItem->bindParam(':idCompra', $idCompra, PDO::PARAM_INT);
                $stmtItem->bindParam(':idProduto', $idProduto, PDO::PARAM_INT);
                $stmtItem->bindParam(':quantidade', $quantidade, PDO::PARAM_INT);
                $stmtItem->bindParam(':valorUnitario', $valorUnitario, PDO::PARAM_STR);
                $stmtItem->bindParam(':valorTotal', $valorItemTotal, PDO::PARAM_STR);
                
                if (!$stmtItem->execute()) {
                    throw new Exception("Erro ao registrar item da compra");
                }
            }
            
            $this->conn->commit();
            return [
                'success' => true,
                'idCompra' => $idCompra
            ];
            
        } catch (Exception $e) {
            $this->conn->rollBack();
            error_log("Erro ao registrar compra: " . $e->getMessage());
            return [
                'success' => false,
                'message' => $e->getMessage()
            ];
        }
    }
    
    public function listarComprasUsuario($idUsuario) {
        try {
            $query = "SELECT c.*, COUNT(ic.idItemCompra) as totalItens 
                     FROM compra c 
                     LEFT JOIN item_compra ic ON c.idCompra = ic.idCompra 
                     WHERE c.idUsuario = :idUsuario 
                     GROUP BY c.idCompra 
                     ORDER BY c.dataCompra DESC";
            
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':idUsuario', $idUsuario, PDO::PARAM_INT);
            $stmt->execute();
            
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
            
        } catch (PDOException $e) {
            error_log("Erro ao listar compras: " . $e->getMessage());
            return [];
        }
    }
    
    public function getCompraDetalhes($idCompra) {
        try {
            // Dados da compra
            $queryCompra = "SELECT c.*, u.nome as nomeUsuario 
                           FROM compra c 
                           JOIN usuario u ON c.idUsuario = u.idUsuario 
                           WHERE c.idCompra = :idCompra";
            
            $stmtCompra = $this->conn->prepare($queryCompra);
            $stmtCompra->bindParam(':idCompra', $idCompra, PDO::PARAM_INT);
            $stmtCompra->execute();
            
            $compra = $stmtCompra->fetch(PDO::FETCH_ASSOC);
            
            if (!$compra) {
                return false;
            }
            
            // Itens da compra
            $queryItens = "SELECT ic.*, p.nomeProduto, p.codigoProduto 
                          FROM item_compra ic 
                          JOIN produto p ON ic.idProduto = p.idProduto 
                          WHERE ic.idCompra = :idCompra";
            
            $stmtItens = $this->conn->prepare($queryItens);
            $stmtItens->bindParam(':idCompra', $idCompra, PDO::PARAM_INT);
            $stmtItens->execute();
            
            $compra['itens'] = $stmtItens->fetchAll(PDO::FETCH_ASSOC);
            
            return $compra;
            
        } catch (PDOException $e) {
            error_log("Erro ao buscar detalhes da compra: " . $e->getMessage());
            return false;
        }
    }





    // Adicione estas funções à classe Compra existente:

    public function listarTodasCompras($filtros = []) {
        try {
            $query = "SELECT c.*, u.nome as nomeUsuario, COUNT(ic.idItemCompra) as totalItens 
                    FROM compra c 
                    JOIN usuario u ON c.idUsuario = u.idUsuario 
                    LEFT JOIN item_compra ic ON c.idCompra = ic.idCompra 
                    WHERE 1=1";
            
            $params = [];
            
            // Filtro por data inicial
            if (!empty($filtros['dataInicial'])) {
                $query .= " AND c.dataCompra >= :dataInicial";
                $params[':dataInicial'] = $filtros['dataInicial'] . ' 00:00:00';
            }
            
            // Filtro por data final
            if (!empty($filtros['dataFinal'])) {
                $query .= " AND c.dataCompra <= :dataFinal";
                $params[':dataFinal'] = $filtros['dataFinal'] . ' 23:59:59';
            }
            
            // Filtro por usuário
            if (!empty($filtros['idUsuario'])) {
                $query .= " AND c.idUsuario = :idUsuario";
                $params[':idUsuario'] = $filtros['idUsuario'];
            }
            
            // Filtro por valor mínimo
            if (isset($filtros['valorMinimo']) && $filtros['valorMinimo'] !== '') {
                $query .= " AND c.valorTotal >= :valorMinimo";
                $params[':valorMinimo'] = str_replace(',', '.', $filtros['valorMinimo']);
            }
            
            // Filtro por valor máximo
            if (isset($filtros['valorMaximo']) && $filtros['valorMaximo'] !== '') {
                $query .= " AND c.valorTotal <= :valorMaximo";
                $params[':valorMaximo'] = str_replace(',', '.', $filtros['valorMaximo']);
            }
            
            $query .= " GROUP BY c.idCompra ORDER BY c.dataCompra DESC";
            
            // Adiciona paginação se necessário
            if (isset($filtros['page']) && isset($filtros['itemsPerPage'])) {
                $offset = ($filtros['page'] - 1) * $filtros['itemsPerPage'];
                $limit = $filtros['itemsPerPage'];
                $query .= " LIMIT :limit OFFSET :offset";
                $params[':limit'] = $limit;
                $params[':offset'] = $offset;
            }
            
            $stmt = $this->conn->prepare($query);
            
            // Bind de parâmetros
            foreach($params as $key => $value) {
                if(in_array($key, [':limit', ':offset'])) {
                    $stmt->bindValue($key, $value, PDO::PARAM_INT);
                } else {
                    $stmt->bindValue($key, $value);
                }
            }
            
            $stmt->execute();
            $compras = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            // Calcular estatísticas para o relatório
            $estatisticas = $this->calcularEstatisticasCompras($filtros);
            
            return [
                'compras' => $compras,
                'estatisticas' => $estatisticas
            ];
            
        } catch (PDOException $e) {
            error_log("Erro ao listar compras: " . $e->getMessage());
            return [
                'compras' => [],
                'estatisticas' => [
                    'totalCompras' => 0,
                    'valorTotal' => 0,
                    'mediaValor' => 0
                ]
            ];
        }
    }

    private function calcularEstatisticasCompras($filtros = []) {
        try {
            $query = "SELECT 
                        COUNT(c.idCompra) as totalCompras,
                        SUM(c.valorTotal) as valorTotal,
                        AVG(c.valorTotal) as mediaValor
                    FROM compra c 
                    WHERE 1=1";
            
            $params = [];
            
            // Filtro por data inicial
            if (!empty($filtros['dataInicial'])) {
                $query .= " AND c.dataCompra >= :dataInicial";
                $params[':dataInicial'] = $filtros['dataInicial'] . ' 00:00:00';
            }
            
            // Filtro por data final
            if (!empty($filtros['dataFinal'])) {
                $query .= " AND c.dataCompra <= :dataFinal";
                $params[':dataFinal'] = $filtros['dataFinal'] . ' 23:59:59';
            }
            
            // Filtro por usuário
            if (!empty($filtros['idUsuario'])) {
                $query .= " AND c.idUsuario = :idUsuario";
                $params[':idUsuario'] = $filtros['idUsuario'];
            }
            
            // Filtro por valor mínimo
            if (isset($filtros['valorMinimo']) && $filtros['valorMinimo'] !== '') {
                $query .= " AND c.valorTotal >= :valorMinimo";
                $params[':valorMinimo'] = str_replace(',', '.', $filtros['valorMinimo']);
            }
            
            // Filtro por valor máximo
            if (isset($filtros['valorMaximo']) && $filtros['valorMaximo'] !== '') {
                $query .= " AND c.valorTotal <= :valorMaximo";
                $params[':valorMaximo'] = str_replace(',', '.', $filtros['valorMaximo']);
            }
            
            $stmt = $this->conn->prepare($query);
            
            // Bind de parâmetros
            foreach($params as $key => $value) {
                $stmt->bindValue($key, $value);
            }
            
            $stmt->execute();
            return $stmt->fetch(PDO::FETCH_ASSOC);
            
        } catch (PDOException $e) {
            error_log("Erro ao calcular estatísticas: " . $e->getMessage());
            return [
                'totalCompras' => 0,
                'valorTotal' => 0,
                'mediaValor' => 0
            ];
        }
    }

    public function getUsuariosComCompras() {
        try {
            $query = "SELECT DISTINCT u.idUsuario, u.nome
                    FROM usuario u
                    JOIN compra c ON u.idUsuario = c.idUsuario
                    ORDER BY u.nome ASC";
            
            $stmt = $this->conn->prepare($query);
            $stmt->execute();
            
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
            
        } catch (PDOException $e) {
            error_log("Erro ao listar usuários com compras: " . $e->getMessage());
            return [];
        }
    }

    public function getRelatorioMensal($ano = null) {
        try {
            // Se não informar ano, usa o atual
            if (!$ano) {
                $ano = date('Y');
            }
            
            // Query para buscar dados mensais
            $query = "SELECT 
                        MONTH(c.dataCompra) as mes,
                        COUNT(c.idCompra) as totalCompras,
                        SUM(c.valorTotal) as valorTotal,
                        AVG(c.valorTotal) as valorMedio,
                        MIN(c.valorTotal) as valorMinimo,
                        MAX(c.valorTotal) as valorMaximo
                    FROM compra c
                    WHERE YEAR(c.dataCompra) = :ano
                    GROUP BY MONTH(c.dataCompra)
                    ORDER BY mes ASC";
            
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':ano', $ano, PDO::PARAM_INT);
            $stmt->execute();
            
            $dadosMensais = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            // Organizar dados para todos os meses do ano
            $mesesCompletos = [];
            for ($i = 1; $i <= 12; $i++) {
                $mesesCompletos[$i] = [
                    'mes' => $i,
                    'nomeMes' => $this->getNomeMes($i),
                    'totalCompras' => 0,
                    'valorTotal' => 0,
                    'valorMedio' => 0,
                    'valorMinimo' => 0,
                    'valorMaximo' => 0
                ];
            }
            
            // Preencher com dados reais
            foreach ($dadosMensais as $dados) {
                $mes = (int)$dados['mes'];
                $mesesCompletos[$mes] = [
                    'mes' => $mes,
                    'nomeMes' => $this->getNomeMes($mes),
                    'totalCompras' => $dados['totalCompras'],
                    'valorTotal' => $dados['valorTotal'],
                    'valorMedio' => $dados['valorMedio'],
                    'valorMinimo' => $dados['valorMinimo'],
                    'valorMaximo' => $dados['valorMaximo']
                ];
            }
            
            // Calcular estatísticas anuais
            $query = "SELECT 
                        COUNT(c.idCompra) as totalCompras,
                        SUM(c.valorTotal) as valorTotal,
                        AVG(c.valorTotal) as valorMedio,
                        MIN(c.valorTotal) as valorMinimo,
                        MAX(c.valorTotal) as valorMaximo
                    FROM compra c
                    WHERE YEAR(c.dataCompra) = :ano";
            
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':ano', $ano, PDO::PARAM_INT);
            $stmt->execute();
            
            $estatisticasAnuais = $stmt->fetch(PDO::FETCH_ASSOC);
            
            // Buscar anos disponíveis para seleção
            $query = "SELECT DISTINCT YEAR(dataCompra) as ano
                    FROM compra
                    ORDER BY ano DESC";
            
            $stmt = $this->conn->prepare($query);
            $stmt->execute();
            
            $anosDisponiveis = $stmt->fetchAll(PDO::FETCH_COLUMN);
            
            return [
                'dadosMensais' => array_values($mesesCompletos),
                'estatisticasAnuais' => $estatisticasAnuais,
                'anosDisponiveis' => $anosDisponiveis,
                'anoSelecionado' => $ano
            ];
            
        } catch (PDOException $e) {
            error_log("Erro ao gerar relatório mensal: " . $e->getMessage());
            return [
                'dadosMensais' => [],
                'estatisticasAnuais' => [
                    'totalCompras' => 0,
                    'valorTotal' => 0,
                    'valorMedio' => 0,
                    'valorMinimo' => 0,
                    'valorMaximo' => 0
                ],
                'anosDisponiveis' => [],
                'anoSelecionado' => $ano
            ];
        }
    }
    
    private function getNomeMes($mes) {
        $meses = [
            1 => 'Janeiro',
            2 => 'Fevereiro',
            3 => 'Março',
            4 => 'Abril',
            5 => 'Maio',
            6 => 'Junho',
            7 => 'Julho',
            8 => 'Agosto',
            9 => 'Setembro',
            10 => 'Outubro',
            11 => 'Novembro',
            12 => 'Dezembro'
        ];
        
        return $meses[$mes] ?? 'Desconhecido';
    }
    





    public function getTopClientes($limit = 10, $orderBy = 'valorTotal', $periodo = null) {
        try {
            $query = "SELECT 
                        u.idUsuario,
                        u.nome,
                        l.login as email, /* Using login field instead of email */
                        COUNT(c.idCompra) as totalCompras,
                        SUM(c.valorTotal) as valorTotal,
                        AVG(c.valorTotal) as mediaCompra,
                        MIN(c.dataCompra) as primeiraCompra,
                        MAX(c.dataCompra) as ultimaCompra
                    FROM usuario u
                    LEFT JOIN login l ON u.idUsuario = l.idUsuario /* Join with login table */
                    JOIN compra c ON u.idUsuario = c.idUsuario";
            
            $params = [];
            
            // Filtro por período (último mês, último ano, etc.)
            if ($periodo) {
                $query .= " WHERE c.dataCompra >= :dataInicio";
                
                switch ($periodo) {
                    case 'mes':
                        $params[':dataInicio'] = date('Y-m-d', strtotime('-1 month'));
                        break;
                    case 'trimestre':
                        $params[':dataInicio'] = date('Y-m-d', strtotime('-3 months'));
                        break;
                    case 'semestre':
                        $params[':dataInicio'] = date('Y-m-d', strtotime('-6 months'));
                        break;
                    case 'ano':
                        $params[':dataInicio'] = date('Y-m-d', strtotime('-1 year'));
                        break;
                }
            }
            
            $query .= " GROUP BY u.idUsuario, u.nome, l.login";
            
            // Ordenação
            if ($orderBy === 'totalCompras') {
                $query .= " ORDER BY totalCompras DESC, valorTotal DESC";
            } else {
                $query .= " ORDER BY valorTotal DESC, totalCompras DESC";
            }
            
            // Limitar número de resultados
            $query .= " LIMIT :limit";
            $params[':limit'] = $limit;
            
            $stmt = $this->conn->prepare($query);
            
            // Bind parameters
            foreach ($params as $key => $value) {
                if ($key === ':limit') {
                    $stmt->bindValue($key, $value, PDO::PARAM_INT);
                } else {
                    $stmt->bindValue($key, $value, PDO::PARAM_STR);
                }
            }
            
            $stmt->execute();
            $clientes = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            // Enhanced error checking and logging
            if (empty($clientes)) {
                error_log("Top clientes query returned no results. SQL: " . $query);
            }
            
            // Buscar dados adicionais: produtos mais comprados por cada cliente
            foreach ($clientes as &$cliente) {
                $queryProdutos = "SELECT 
                                    p.idProduto,
                                    p.nomeProduto,
                                    p.codigoProduto,
                                    COUNT(ic.idItemCompra) as frequencia,
                                    SUM(ic.quantidade) as quantidadeTotal
                                FROM item_compra ic
                                JOIN compra c ON ic.idCompra = c.idCompra
                                JOIN produto p ON ic.idProduto = p.idProduto
                                WHERE c.idUsuario = :idUsuario
                                GROUP BY p.idProduto, p.nomeProduto, p.codigoProduto
                                ORDER BY frequencia DESC
                                LIMIT 3";
                
                $stmtProdutos = $this->conn->prepare($queryProdutos);
                $stmtProdutos->bindValue(':idUsuario', $cliente['idUsuario'], PDO::PARAM_INT);
                $stmtProdutos->execute();
                $cliente['produtosPreferidos'] = $stmtProdutos->fetchAll(PDO::FETCH_ASSOC);
            }
            
            // Calcular estatísticas globais
            $queryEstatisticas = "SELECT 
                                    COUNT(DISTINCT c.idUsuario) as totalClientes,
                                    SUM(c.valorTotal) as valorTotalGeral,
                                    COUNT(c.idCompra) as totalComprasGeral,
                                    AVG(subquery.totalPorCliente) as mediaComprasPorCliente,
                                    AVG(subquery.valorPorCliente) as mediaGastoPorCliente
                                FROM compra c
                                JOIN (
                                    SELECT 
                                        idUsuario, 
                                        COUNT(idCompra) as totalPorCliente,
                                        SUM(valorTotal) as valorPorCliente
                                    FROM compra
                                    GROUP BY idUsuario
                                ) as subquery";
            
            if ($periodo) {
                $queryEstatisticas .= " WHERE c.dataCompra >= :dataInicio";
            }
            
            $stmtEstatisticas = $this->conn->prepare($queryEstatisticas);
            
            if ($periodo && isset($params[':dataInicio'])) {
                $stmtEstatisticas->bindValue(':dataInicio', $params[':dataInicio'], PDO::PARAM_STR);
            }
            
            $stmtEstatisticas->execute();
            $estatisticas = $stmtEstatisticas->fetch(PDO::FETCH_ASSOC);
            
            // Percentual que o top representa do total
            if (!empty($clientes) && $estatisticas['valorTotalGeral'] > 0) {
                $valorTotalTop = array_sum(array_column($clientes, 'valorTotal'));
                $estatisticas['percentualValorTop'] = ($valorTotalTop / $estatisticas['valorTotalGeral']) * 100;
                
                $comprasTop = array_sum(array_column($clientes, 'totalCompras'));
                $estatisticas['percentualComprasTop'] = ($comprasTop / $estatisticas['totalComprasGeral']) * 100;
            } else {
                $estatisticas['percentualValorTop'] = 0;
                $estatisticas['percentualComprasTop'] = 0;
            }
            
            return [
                'clientes' => $clientes,
                'estatisticas' => $estatisticas,
                'filtros' => [
                    'limite' => $limit,
                    'ordenacao' => $orderBy,
                    'periodo' => $periodo
                ]
            ];
            
        } catch (PDOException $e) {
            error_log("Erro ao buscar top clientes: " . $e->getMessage() . " | Query: " . $e->getTraceAsString());
            
            return [
                'clientes' => [],
                'estatisticas' => [
                    'totalClientes' => 0,
                    'valorTotalGeral' => 0,
                    'totalComprasGeral' => 0,
                    'mediaComprasPorCliente' => 0,
                    'mediaGastoPorCliente' => 0,
                    'percentualValorTop' => 0,
                    'percentualComprasTop' => 0
                ],
                'filtros' => [
                    'limite' => $limit,
                    'ordenacao' => $orderBy,
                    'periodo' => $periodo
                ]
            ];
        }
    }
}