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
        <title>Login</title>
        <link rel="icon" type="image/x-icon" href="../public/assets/img/icon.ico">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.1/css/all.css">
        <link href="../public/assets/css/login.css" rel="stylesheet" type="text/css">
    </head>
    <body class="authenticate">
        <?php if (isset($_GET['error'])): ?>
            <div class="error-animation fade-out">
                <div class="container">
                    <div class="svg-box">
                        <svg class="circular red-stroke">
                            <circle class="path" cx="75" cy="75" r="50" fill="none" stroke-width="5" stroke-miterlimit="10"/>
                        </svg>
                        <svg class="cross red-stroke">
                            <g transform="matrix(0.79961,8.65821e-32,8.39584e-32,0.79961,-502.652,-204.518)">
                                <path class="first-line" d="M634.087,300.805L673.361,261.53" fill="none"/>
                            </g>
                            <g transform="matrix(-1.28587e-16,-0.79961,0.79961,-1.28587e-16,-204.752,543.031)">
                                <path class="second-line" d="M634.087,300.805L673.361,261.53"/>
                            </g>
                        </svg>
                    </div>
                </div>
            </div>
            <script>
                setTimeout(function() {
                    const errorAnimation = document.querySelector('.error-animation');
                    errorAnimation.classList.add('hidden'); 

                    setTimeout(function() {
                        window.location.href = "../public/index.php?controller=auth&action=login"; 
                    }, 1000); 
                }, 2000); 
            </script>
        <?php endif; ?>
        <?php if (isset($_GET['timeout'])): ?>
            <div id="timeoutModal" class="timeout-modal">
                <div class="timeout-modal-content">
                    <h2>Sessão Expirada</h2>
                    <p>Sua sessão expirou. Por favor, faça login novamente.</p>
                    <button class="timeout-modal-close" onclick="redirectToLogin()">OK</button>
                </div>
            </div>

            <script>
                document.getElementById('timeoutModal').style.display = 'flex';

                function redirectToLogin() {
                    window.location.href = "../public/index.php?controller=auth&action=login";
                }
            </script>
        <?php endif; ?>
        <div class="login">
            <h1>Login - Loja</h1>
            <img src="../public/assets/img/logo1.png" alt="Evo Sistemas Inteligentes">
            <form action="../public/index.php?controller=auth&action=login" method="post">
                <label for="username">
                    <i class="fas fa-user"></i>
                </label>
                <input type="text" name="username" placeholder="Login" id="username" maxlength="20" required>
                <label for="password">
                    <i class="fas fa-lock"></i>
                </label>
                <input type="password" name="password" placeholder="Senha" id="password" maxlength="100" required>
                <input type="submit" value="Login">
            </form>
        </div>
    </body>
</html>