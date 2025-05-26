-- Insert additional product types
INSERT INTO tipoProduto (descricao) VALUES
('Processador'),
('Placa de Vídeo'),
('SSD'),
('HD'),
('Gabinete'),
('Fonte'),
('Mouse'),
('Teclado'),
('Monitor'),
('Cooler'),
('Notebook'),
('Headset'),
('Webcam'),
('Hub USB'),
('Roteador'),
('Impressora'),
('Tablet'),
('Smartphone');



-- Insert products with appropriate visibility and type
INSERT INTO produto (idVisibilidadeProduto, nomeProduto, codigoProduto, idTipoProduto, valorProduto, descricaoProduto) VALUES
(1, 'Placa-Mãe ASUS ROG Strix B550', 'PM-B550-ASUS', 1, 1299.90, 'Placa-mãe ASUS ROG Strix B550 para processadores AMD Ryzen'),
(1, 'Memória RAM Corsair 8GB DDR4', 'RAM-COR-8GB', 2, 249.90, 'Memória RAM Corsair Vengeance LPX 8GB DDR4 3200MHz'),
(1, 'Memória RAM Kingston 16GB DDR4', 'RAM-KIN-16GB', 2, 399.90, 'Memória RAM Kingston Fury 16GB DDR4 3600MHz'),
(1, 'Memória RAM Notebook Crucial 8GB', 'RAM-NB-CRU-8GB', 3, 219.90, 'Memória RAM Crucial 8GB DDR4 2666MHz para notebook'),
(1, 'Processador AMD Ryzen 5 5600X', 'CPU-AMD-5600X', 4, 1499.90, 'Processador AMD Ryzen 5 5600X 3.7GHz (4.6GHz Max Boost) 6-Core'),
(1, 'Processador Intel Core i7-12700K', 'CPU-INT-12700K', 4, 2699.90, 'Processador Intel Core i7-12700K 12ª Geração 3.6GHz (5.0GHz Max Boost)'),
(1, 'Placa de Vídeo NVIDIA RTX 3060', 'GPU-NV-3060', 5, 2499.90, 'Placa de Vídeo NVIDIA GeForce RTX 3060 12GB GDDR6'),
(1, 'Placa de Vídeo AMD RX 6700 XT', 'GPU-AMD-6700XT', 5, 2799.90, 'Placa de Vídeo AMD Radeon RX 6700 XT 12GB GDDR6'),
(1, 'SSD Samsung 970 EVO 500GB', 'SSD-SAM-500', 6, 499.90, 'SSD NVMe Samsung 970 EVO 500GB M.2'),
(1, 'SSD Kingston A2000 1TB', 'SSD-KIN-1TB', 6, 699.90, 'SSD NVMe Kingston A2000 1TB M.2'),
(1, 'HD Seagate Barracuda 2TB', 'HD-SEA-2TB', 7, 379.90, 'HD Seagate Barracuda 2TB 7200RPM SATA 3'),
(1, 'Gabinete Corsair iCUE 4000X', 'GAB-COR-4000X', 8, 899.90, 'Gabinete Corsair iCUE 4000X RGB Mid-Tower ATX'),
(1, 'Gabinete NZXT H510', 'GAB-NZXT-H510', 8, 699.90, 'Gabinete NZXT H510 Mid-Tower ATX'),
(1, 'Fonte Corsair RM750x 750W', 'FON-COR-750X', 9, 799.90, 'Fonte Corsair RM750x 750W 80 Plus Gold Modular'),
(1, 'Fonte EVGA 600W 80 Plus', 'FON-EVGA-600W', 9, 399.90, 'Fonte EVGA 600W 80 Plus White'),
(1, 'Mouse Logitech G Pro X Superlight', 'MS-LOG-PROX', 10, 699.90, 'Mouse Gamer Logitech G Pro X Superlight Wireless'),
(1, 'Mouse Razer DeathAdder V2', 'MS-RZ-DAV2', 10, 349.90, 'Mouse Gamer Razer DeathAdder V2 20000 DPI'),
(1, 'Teclado Logitech G Pro', 'TEC-LOG-GPRO', 11, 799.90, 'Teclado Mecânico Logitech G Pro RGB GX Blue'),
(1, 'Teclado Redragon Kumara K552', 'TEC-RD-K552', 11, 299.90, 'Teclado Mecânico Redragon Kumara K552 RGB'),
(1, 'Monitor LG Ultragear 27" 144Hz', 'MON-LG-27-144', 12, 1799.90, 'Monitor Gamer LG Ultragear 27" 144Hz 1ms IPS Full HD'),
(1, 'Monitor Samsung Odyssey G5 32"', 'MON-SAM-32-G5', 12, 2499.90, 'Monitor Curvo Samsung Odyssey G5 32" 144Hz 1ms QHD'),
(1, 'Cooler Master Hyper 212', 'COO-CM-H212', 13, 199.90, 'Cooler para Processador Cooler Master Hyper 212'),
(1, 'Water Cooler Corsair H100i', 'COO-COR-H100I', 13, 899.90, 'Water Cooler Corsair H100i RGB PRO XT 240mm'),
(1, 'Notebook Dell G15', 'NB-DELL-G15', 14, 5999.90, 'Notebook Gamer Dell G15 15.6" i5-11400H 8GB 512GB SSD RTX 3050'),
(1, 'Notebook Lenovo Legion 5', 'NB-LEN-LEG5', 14, 7499.90, 'Notebook Gamer Lenovo Legion 5 15.6" Ryzen 7 16GB 512GB SSD RTX 3060'),
(1, 'Headset HyperX Cloud II', 'HS-HX-CLOUD2', 15, 599.90, 'Headset Gamer HyperX Cloud II 7.1 Surround'),
(1, 'Headset Logitech G Pro X', 'HS-LOG-PROX', 15, 899.90, 'Headset Gamer Logitech G Pro X 7.1 Surround'),
(1, 'Webcam Logitech C920s Pro', 'WC-LOG-C920S', 16, 499.90, 'Webcam Logitech C920s Pro Full HD 1080p'),
(1, 'Webcam Razer Kiyo Pro', 'WC-RZ-KIYO-PRO', 16, 899.90, 'Webcam Razer Kiyo Pro Full HD 1080p 60FPS'),
(1, 'Hub USB TP-Link 7 Portas', 'HUB-TPL-7P', 17, 79.90, 'Hub USB 3.0 TP-Link 7 Portas com Fonte'),
(1, 'Hub USB Anker 4 Portas', 'HUB-ANK-4P', 17, 129.90, 'Hub USB-C Anker 4 Portas para MacBook'),
(1, 'Roteador TP-Link Archer C80', 'ROT-TPL-C80', 18, 299.90, 'Roteador Wi-Fi TP-Link Archer C80 AC1900 Dual Band'),
(1, 'Roteador ASUS RT-AX82U', 'ROT-ASUS-AX82U', 18, 1299.90, 'Roteador Wi-Fi 6 ASUS RT-AX82U AX5400 Dual Band'),
(1, 'Impressora HP LaserJet M428fdw', 'IMP-HP-M428', 19, 2999.90, 'Impressora Multifuncional HP LaserJet Pro M428fdw'),
(2, 'Placa-Mãe ASUS TUF B450-PRO', 'PM-B450-TUF', 1, 899.90, 'Placa-mãe ASUS TUF B450-PRO para processadores AMD Ryzen'),
(2, 'Processador AMD Ryzen 3 3300X', 'CPU-AMD-3300X', 4, 899.90, 'Processador AMD Ryzen 3 3300X 3.8GHz (4.3GHz Max Boost) 4-Core'),
(2, 'Placa de Vídeo NVIDIA GTX 1660', 'GPU-NV-1660', 5, 1799.90, 'Placa de Vídeo NVIDIA GeForce GTX 1660 6GB GDDR5'),
(2, 'SSD WD Blue 250GB', 'SSD-WD-250', 6, 299.90, 'SSD SATA WD Blue 250GB 2.5"'),
(2, 'HD WD Purple 4TB', 'HD-WD-4TB', 7, 699.90, 'HD WD Purple 4TB 5400RPM SATA 3 para vigilância');


-- Insert normal users (customers)
INSERT INTO usuario (nome, documento, idSituacaoUsuario) VALUES
('João Silva', '12345678901', 1),
('Maria Santos', '23456789012', 1),
('Pedro Oliveira', '34567890123', 1),
('Ana Costa', '45678901234', 1),
('Carlos Pereira', '56789012345', 1),
('Luciana Almeida', '67890123456', 1),
('Roberto Martins', '78901234567', 1),
('Fernanda Lima', '89012345678', 1),
('Ricardo Souza', '90123456789', 1),
('Patrícia Ferreira', '01234567890', 1),
('Eduardo Ribeiro', '10293847560', 1),
('Juliana Gomes', '20394857610', 1),
('Gustavo Santos', '30495867120', 1),
('Camila Rodrigues', '40596877230', 1),
('Felipe Costa', '50697887340', 1),
('Amanda Alves', '60798897450', 1),
('Lucas Pereira', '70899807560', 1),
('Daniela Martins', '80900817670', 1),
('Marcelo Lima', '90011827780', 1),
('Beatriz Ferreira', '10123836890', 1),
('Rodrigo Carvalho', '11223344556', 1),
('Mariana Silva', '22334455667', 1),
('Victor Oliveira', '33445566778', 1),
('Isabela Costa', '44556677889', 1),
('Henrique Santos', '55667788990', 1);

-- Insert admin users
INSERT INTO usuario (nome, documento, idSituacaoUsuario) VALUES
('Gerente Vendas', '66778899001', 1),
('Supervisor TI', '77889900112', 1);

-- Insert login credentials for normal users
-- Note: Using $2a$10$z5y3iSLFfTeg/cui.YN29OujBx5bLAbku3QMCyn40uVIPhi1xzJq2 as default password hash (from your existing admin user)
-- SQL query to insert logins for these users
INSERT INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario)
SELECT idUsuario, 
       CONCAT('user', idUsuario), 
       '$2a$10$z5y3iSLFfTeg/cui.YN29OujBx5bLAbku3QMCyn40uVIPhi1xzJq2',
       1, -- regular user type
       1  -- active status
FROM usuario
WHERE idUsuario > 2 AND idUsuario <= 27; -- Skip existing admin and user

-- Insert login credentials for new admin users
INSERT INTO login (idUsuario, login, senha, idTipoLogin, idSituacaoUsuario)
VALUES 
(28, 'gerente', '$2a$10$z5y3iSLFfTeg/cui.YN29OujBx5bLAbku3QMCyn40uVIPhi1xzJq2', 2, 1),
(29, 'supervisor', '$2a$10$z5y3iSLFfTeg/cui.YN29OujBx5bLAbku3QMCyn40uVIPhi1xzJq2', 2, 1);



-- Insert address data for users
INSERT INTO endereco (idUsuario, cep, uf, municipio, rua, numero, complemento) VALUES
(3, '01310-200', 'SP', 'São Paulo', 'Av. Paulista', '1000', 'Apto 123'),
(4, '22021-001', 'RJ', 'Rio de Janeiro', 'Av. Atlântica', '500', 'Bloco B Apto 45'),
(5, '30130-110', 'MG', 'Belo Horizonte', 'Av. Afonso Pena', '1500', 'Sala 302'),
(6, '80530-000', 'PR', 'Curitiba', 'Rua XV de Novembro', '700', 'Casa 2'),
(7, '90619-900', 'RS', 'Porto Alegre', 'Av. Ipiranga', '6681', NULL),
(8, '71503-505', 'DF', 'Brasília', 'SQN 104', '205', 'Bloco A Apto 101'),
(9, '69067-001', 'AM', 'Manaus', 'Av. Djalma Batista', '1661', NULL),
(10, '40026-010', 'BA', 'Salvador', 'Av. Sete de Setembro', '1234', 'Apto 56'),
(11, '51021-001', 'PE', 'Recife', 'Av. Boa Viagem', '100', NULL),
(12, '60115-282', 'CE', 'Fortaleza', 'Av. Beira Mar', '3000', 'Apto 1402'),
(13, '66053-000', 'PA', 'Belém', 'Av. Presidente Vargas', '800', NULL),
(14, '59020-100', 'RN', 'Natal', 'Av. Senador Salgado Filho', '123', 'Casa 5'),
(15, '29055-131', 'ES', 'Vitória', 'Av. Nossa Senhora da Penha', '356', 'Sala 1001'),
(16, '57037-030', 'AL', 'Maceió', 'Av. Fernandes Lima', '100', NULL),
(17, '49015-100', 'SE', 'Aracaju', 'Av. Barão de Maruim', '500', 'Apto 303'),
(18, '74115-010', 'GO', 'Goiânia', 'Av. 85', '300', 'Quadra 10 Lote 20'),
(19, '78005-000', 'MT', 'Cuiabá', 'Av. Isaac Póvoas', '1000', NULL),
(20, '79002-010', 'MS', 'Campo Grande', 'Av. Afonso Pena', '3500', 'Sala 205'),
(21, '05508-000', 'SP', 'São Paulo', 'Rua do Matão', '1010', 'Prédio A'),
(22, '22250-040', 'RJ', 'Rio de Janeiro', 'Rua Humaitá', '275', 'Apto 602'),
(23, '70070-150', 'DF', 'Brasília', 'Esplanada dos Ministérios', 'Bl K', 'Sala 101'),
(24, '91330-001', 'RS', 'Porto Alegre', 'Av. Protásio Alves', '2300', NULL),
(25, '13083-970', 'SP', 'Campinas', 'Cidade Universitária', '500', 'Bloco C'),
(26, '88040-900', 'SC', 'Florianópolis', 'Rua Lauro Linhares', '2123', 'Sala 503'),
(27, '60175-047', 'CE', 'Fortaleza', 'Av. Santos Dumont', '1789', 'Torre B Sala 1201');