<?php
// Configure database connection
$host = 'localhost';
$db = 'sistema_produtos_informatica'; // Updated to match your DB name
$user = 'root'; // Adjust to your DB user
$pass = 'root'; // Adjust to your DB password
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
];

try {
    // Connect to database
    $pdo = new PDO($dsn, $user, $pass, $options);
    
    echo "Connected successfully. Starting data generation...\n";
    
    // Get all regular user IDs
    $stmt = $pdo->query("SELECT idUsuario FROM usuario WHERE idUsuario > 2 AND idUsuario <= 27");
    $userIds = $stmt->fetchAll(PDO::FETCH_COLUMN);
    
    // Get all product IDs and prices
    $stmt = $pdo->query("SELECT idProduto, valorProduto FROM produto");
    $products = $stmt->fetchAll();
    
    // Start date (2 years ago)
    $startDate = new DateTime();
    $startDate->modify('-2 years');
    
    // End date (today)
    $endDate = new DateTime();
    
    // Generate purchases
    $totalPurchases = 0;
    $pdo->beginTransaction();
    
    // Distribute purchases based on user activity (some users buy more than others)
    $userActivity = [];
    foreach ($userIds as $userId) {
        // Random activity level (1-10)
        $userActivity[$userId] = mt_rand(1, 10);
    }
    
    // Top 5 most active customers
    arsort($userActivity);
    $topUsers = array_keys(array_slice($userActivity, 0, 5, true));
    
    try {
        // Loop through each day in date range
        $currentDate = clone $startDate;
        while ($currentDate <= $endDate) {
            // More purchases in recent months
            $monthsAgo = $endDate->diff($currentDate)->m + ($endDate->diff($currentDate)->y * 12);
            $purchaseProbability = min(1, 1 - ($monthsAgo / 30));
            
            // Generate 0-8 purchases per day based on probability
            $purchasesPerDay = mt_rand(0, floor(8 * $purchaseProbability));
            
            for ($p = 0; $p < $purchasesPerDay; $p++) {
                // Select a user - give higher probability to top users
                if (mt_rand(1, 100) <= 40) {
                    // 40% chance to be a top user
                    $userId = $topUsers[array_rand($topUsers)];
                } else {
                    // 60% chance to be any user
                    $userId = $userIds[array_rand($userIds)];
                }
                
                // Generate random time
                $hour = mt_rand(8, 22);
                $minute = mt_rand(0, 59);
                $second = mt_rand(0, 59);
                $purchaseDate = clone $currentDate;
                $purchaseDate->setTime($hour, $minute, $second);
                
                // Number of items in this purchase (1-7)
                $itemCount = mt_rand(1, 7);
                
                // Select random products
                $selectedProducts = [];
                $availableProducts = $products;
                shuffle($availableProducts);
                
                $totalValue = 0;
                $purchaseItems = [];
                
                // Create 1-7 items for this purchase
                for ($i = 0; $i < $itemCount && !empty($availableProducts); $i++) {
                    $product = array_pop($availableProducts);
                    
                    // Random quantity (1-5)
                    $quantity = mt_rand(1, 5);
                    
                    // Calculate prices
                    $unitPrice = floatval($product['valorProduto']); // Using valorProduto instead of precoProduto
                    // Add small random variation to price
                    $unitPrice = round($unitPrice * (1 + (mt_rand(-5, 5) / 100)), 2);
                    $itemTotal = $unitPrice * $quantity;
                    
                    $purchaseItems[] = [
                        'idProduto' => $product['idProduto'],
                        'quantidade' => $quantity,
                        'valorUnitario' => $unitPrice,
                        'valorTotal' => $itemTotal
                    ];
                    
                    $totalValue += $itemTotal;
                }
                
                // Insert purchase header
                $stmt = $pdo->prepare("
                    INSERT INTO compra (idUsuario, valorTotal, dataCompra) 
                    VALUES (:idUsuario, :valorTotal, :dataCompra)
                ");
                
                $stmt->execute([
                    'idUsuario' => $userId,
                    'valorTotal' => $totalValue,
                    'dataCompra' => $purchaseDate->format('Y-m-d H:i:s')
                ]);
                
                $purchaseId = $pdo->lastInsertId();
                
                // Insert purchase items
                foreach ($purchaseItems as $item) {
                    $stmt = $pdo->prepare("
                        INSERT INTO item_compra (idCompra, idProduto, quantidade, valorUnitario, valorTotal) 
                        VALUES (:idCompra, :idProduto, :quantidade, :valorUnitario, :valorTotal)
                    ");
                    
                    $stmt->execute([
                        'idCompra' => $purchaseId,
                        'idProduto' => $item['idProduto'],
                        'quantidade' => $item['quantidade'],
                        'valorUnitario' => $item['valorUnitario'],
                        'valorTotal' => $item['valorTotal']
                    ]);
                }
                
                $totalPurchases++;
                
                // Show progress
                if ($totalPurchases % 50 == 0) {
                    echo "Generated $totalPurchases purchases so far...\n";
                }
            }
            
            // Move to next day
            $currentDate->modify('+1 day');
        }
        
        $pdo->commit();
        echo "Successfully generated $totalPurchases purchases with items.\n";
        
    } catch (Exception $e) {
        $pdo->rollBack();
        throw $e;
    }
    
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage() . "\n";
}
?>