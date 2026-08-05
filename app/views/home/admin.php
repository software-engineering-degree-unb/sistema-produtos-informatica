<?php
function formatarCPF($cpf) {

    $cpf = preg_replace('/\D/', '', $cpf);
    
    if (strlen($cpf) === 11) {
        return substr($cpf, 0, 3) . '.' . substr($cpf, 3, 3) . '.' . substr($cpf, 6, 3) . '-' . substr($cpf, 9, 2);
    }
    return $cpf; 
}


function formatarCNPJ($cnpj) {

    $cnpj = preg_replace('/\D/', '', $cnpj);
    
    if (strlen($cnpj) === 14) {
        return substr($cnpj, 0, 2) . '.' . substr($cnpj, 2, 3) . '.' . substr($cnpj, 5, 3) . '/' . substr($cnpj, 8, 4) . '-' . substr($cnpj, 12, 2);
    } 
    return $cnpj; 
}
?>


<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Página inicial - Administrador</title>
    <link rel="icon" type="image/x-icon" href="../public/assets/img/icon.ico">
    <link href="../public/assets/css/home.css" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
</head>
<body class="loggedin">
<?php if (isset($_GET['success'])): ?>
            <div class="success-animation fade-out">
                <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                    <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none" />
                    <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
                </svg>
            </div>
            <script>
                setTimeout(function() {
                    const successAnimation = document.querySelector('.success-animation');
                    successAnimation.classList.add('hidden');

                    setTimeout(function() {
                        window.location.href = "../public/index.php?controller=home&action=index"; 
                    }, 1000); 
                }, 2000); 
            </script>
        <?php endif; ?>
        <nav class="navtop">
            <div class="nav-left">
                <img src="../public/assets/img/logo2.png" alt="">
            </div>
            <!-- <div class="nav-login-info">
                <p>
                    <?php 
                    if (isset($usuario)) {
                        $documentoUsuario = htmlspecialchars($usuario['documento']);
                        $nomeUsuario = htmlspecialchars($usuario['nome']);
                        echo "$documento - $nome";
                    }
                    ?>
                </p>
            </div> -->
            <div class="nav-right">
                <a href="../public/index.php?controller=home&action=index"><i class="fas fa-house"></i>Página Inicial</a>
                <a href="../public/index.php?controller=profile&action=index"><i class="fas fa-user-circle"></i>Meu Perfil</a>
                <a href="../public/index.php?controller=auth&action=logout"><i class="fas fa-sign-out-alt"></i>Sair</a>
            </div>
        </nav>
    
    <div class="content">
        <h2>Página Inicial - Administrador</h2>
        
        <p>Seja bem vindo!</p>
        <div class="functions">
            <h2>Funções</h2>
                <div class="function-group">
                    <a href="../public/index.php?controller=admin&action=listUsuarios" class="function">
                        <i class="fas fa-person-circle-plus"></i>
                        <p>Gerenciar Usuários</p>
                    </a>

                    
                
                    <a href="../public/index.php?controller=produto&action=listProdutos" class="function">
                        <i class="fa-solid fa-tachograph-digital"></i>
                        <p>Gerenciar Produtos</p>
                    </a>

                    
                    
                    <!-- <a href="../public/index.php?controller=admin&action=historicoAlteracoesUsuario" class="function">
                        <i class="fa-solid fa-rectangle-list"></i>
                        <p>Histórico de Alterações</p>
                    </a>
                

                    <a href="../public/index.php?controller=admin&action=historicoLogin" class="function">
                        <i class="fa-solid fa-right-to-bracket"></i>
                        <p>Histórico de Acessos</p>
                    </a> -->

                    <a href="../public/index.php?controller=compra&action=relatorioMensal" class="function">
                        <i class="fas fa-calendar-alt"></i>
                        <p>Relatório Mensal de Vendas</p>
                    </a>


                    <a href="../public/index.php?controller=compra&action=topClientes" class="function">
                        <i class="fas fa-users"></i>
                        <p>Top Clientes</p>
                    </a>


                    <a href="../public/index.php?controller=compra&action=relatorioVendasPorCanal" class="function">
                        <i class="fa-solid fa-store"></i>
                        <p>Vendas por Canal</p>
                    </a>
  
                    <!-- <a href="#"class="function" style="visibility: hidden">>
                        <p> </p>
                    </a> -->


                </div>
                </div>
                
        </div>
    </div>
</body>
</html>