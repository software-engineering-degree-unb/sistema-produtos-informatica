document.addEventListener('DOMContentLoaded', function() {

    // ################################################## MODAL INFORMATIVO E CARROSSEL DE IMAGENS
    
    const infoModal = document.getElementById("infoModal");
    const infoIcon = document.getElementById("infoIcon");
    const closeModalButtons = document.querySelectorAll("#closeModal, #closeModalButton");

    function toggleInfoModal(show) {
        infoModal.classList.toggle("show", show);
        infoModal.style.display = show ? "block" : "none";
    }

    infoIcon?.addEventListener('click', () => toggleInfoModal(true));
    closeModalButtons.forEach(btn => btn?.addEventListener('click', () => toggleInfoModal(false)));

    const productCarousels = {};
    
    document.querySelectorAll('.equipment-card').forEach(card => {
        const productId = card.dataset.productId;
        productCarousels[productId] = {
            currentImageIndex: 0,
            images: JSON.parse(card.dataset.images)
        };
        
        const navButtons = `
            <div class="carousel-nav">
                <button class="carousel-prev" onclick="changeImage('${productId}', -1)">
                    <i class="fa-solid fa-chevron-left"></i>
                </button>
                <span class="image-counter"></span>
                <button class="carousel-next" onclick="changeImage('${productId}', 1)">
                    <i class="fa-solid fa-chevron-right"></i>
                </button>
            </div>
        `;
        card.querySelector('.image-container').insertAdjacentHTML('beforeend', navButtons);
        updateCardImage(productId);
    });
    
    const productModal = document.getElementById('productDetailsModal');
    const modalClose = productModal?.querySelector('.details-modal-close');
    let currentModalProduct = null;
    
    document.querySelectorAll('.equipment-image, .equipment-name').forEach(element => {
        element.addEventListener('click', function() {
            const card = this.closest('.equipment-card');
            const productId = card.dataset.productId;
            openProductModal(productId);
        });
    });

    window.openProductModal = function(productId) {
        currentModalProduct = productId;
        const card = document.querySelector(`[data-product-id="${productId}"]`);
        const productData = JSON.parse(card.dataset.fullDetails);
        const images = JSON.parse(card.dataset.images);
        
        const modal = document.getElementById('productDetailsModal');
        modal.querySelector('.details-modal-title').innerHTML = `${productData.nomeProduto} (COD. ${productData.codigoProduto})`;
        modal.querySelector('.details-modal-description').innerHTML = `<strong>Descrição: </strong> ${productData.descricaoProduto}`;
        modal.querySelector('.details-modal-price').innerHTML = `<strong>Valor: </strong> R$ ${productData.valorProduto}`;
        
        updateModalImage(0);
        modal.style.display = 'block';
    };

    modalClose?.addEventListener('click', () => {
        productModal.style.display = 'none';
        currentModalProduct = null;
    });

    window.onclick = function(event) {
        if (event.target === infoModal) {
            toggleInfoModal(false);
        }
        if (event.target === productModal) {
            productModal.style.display = 'none';
            currentModalProduct = null;
        }
        if (event.target === cartModal) {
            cartModal.style.display = 'none';
        }
    };
    
    window.changeModalImage = function(direction) {
        if (!currentModalProduct) return;
        const images = JSON.parse(document.querySelector(`[data-product-id="${currentModalProduct}"]`).dataset.images);
        let currentIndex = parseInt(productModal.querySelector('.details-modal-image').dataset.currentIndex);
        currentIndex = (currentIndex + direction + images.length) % images.length;
        updateModalImage(currentIndex);
    };
    
    function updateModalImage(index) {
        if (!currentModalProduct) return;
        const images = JSON.parse(document.querySelector(`[data-product-id="${currentModalProduct}"]`).dataset.images);
        const modalImage = productModal.querySelector('.details-modal-image');
        modalImage.src = `data:image/jpeg;base64,${images[index].imagemProduto}`;
        modalImage.alt = images[index].titulo || 'Imagem do produto';
        modalImage.dataset.currentIndex = index;
        
        productModal.querySelector('.image-counter').textContent = `${index + 1}/${images.length}`;
    }
    
    window.changeImage = function(productId, direction) {
        const carousel = productCarousels[productId];
        carousel.currentImageIndex = (carousel.currentImageIndex + direction + carousel.images.length) % carousel.images.length;
        updateCardImage(productId);
    };
    
    function updateCardImage(productId) {
        const card = document.querySelector(`[data-product-id="${productId}"]`);
        const carousel = productCarousels[productId];
        const currentImage = carousel.images[carousel.currentImageIndex];
        
        const img = card.querySelector('.equipment-image');
        img.src = `data:image/jpeg;base64,${currentImage.imagemProduto}`;
        img.alt = currentImage.titulo || 'Imagem do produto';
        card.querySelector('.image-title').textContent = currentImage.titulo || '';
        card.querySelector('.image-counter').textContent = `${carousel.currentImageIndex + 1}/${carousel.images.length}`;
    }

    // ################################################## SISTEMA DE CARRINHO DE COMPRAS

    // Inicialização do carrinho
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    updateCartCounter();

    // Modal do carrinho
    const cartModal = document.getElementById('cartModal');
    const viewCartBtn = document.getElementById('viewCartBtn');
    const closeCartBtn = cartModal?.querySelector('.cart-modal-close');
    const clearCartBtn = document.getElementById('clearCartBtn');
    const checkoutBtn = document.getElementById('checkoutBtn');

    // Eventos do modal
    viewCartBtn?.addEventListener('click', function() {
        renderCartItems();
        cartModal.style.display = 'block';
    });

    closeCartBtn?.addEventListener('click', function() {
        cartModal.style.display = 'none';
    });

    clearCartBtn?.addEventListener('click', function() {
        if (confirm('Tem certeza que deseja limpar o carrinho?')) {
            cart = [];
            saveCart();
            updateCartCounter();
            renderCartItems();
        }
    });

    checkoutBtn?.addEventListener('click', function() {
        if (cart.length === 0) {
            alert('Seu carrinho está vazio!');
            return;
        }
        
        // Enviar dados do carrinho para o servidor
        fetch('/compra/finalizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                itens: cart
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Compra finalizada com sucesso!');
                cart = [];
                saveCart();
                updateCartCounter();
                renderCartItems();
                cartModal.style.display = 'none';
            } else {
                alert('Erro ao finalizar compra: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao finalizar a compra. Tente novamente.');
        });
    });

    // Função para adicionar item ao carrinho
    window.addToCart = function(productId) {
        const card = document.querySelector(`[data-product-id="${productId}"]`);
        if (!card) return;
        
        const productData = JSON.parse(card.dataset.fullDetails);
        const images = JSON.parse(card.dataset.images);
        
        // Converter valor do produto para número corretamente
        let price;
        if (typeof productData.valorProduto === 'string') {
            // Se for string, substituir vírgula por ponto
            price = parseFloat(productData.valorProduto.replace(',', '.'));
        } else {
            // Se for número, usar diretamente
            price = parseFloat(productData.valorProduto);
        }
        
        // Verificar se o produto já está no carrinho
        const existingItem = cart.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
            showToast(`Quantidade de ${productData.nomeProduto} atualizada!`);
        } else {
            cart.push({
                id: productId,
                name: productData.nomeProduto,
                price: price,
                image: images.length > 0 ? images[0].imagemProduto : null,
                code: productData.codigoProduto,
                quantity: 1
            });
            showToast(`${productData.nomeProduto} adicionado ao carrinho!`);
        }
        
        saveCart();
        updateCartCounter();
        animateCartButton();
    };

    // Função para remover item do carrinho
    window.removeFromCart = function(productId) {
        cart = cart.filter(item => item.id !== productId);
        saveCart();
        updateCartCounter();
        renderCartItems();
    };

    // Função para atualizar a quantidade de um item
    window.updateQuantity = function(productId, change) {
        const item = cart.find(item => item.id === productId);
        if (item) {
            item.quantity += change;
            
            if (item.quantity <= 0) {
                removeFromCart(productId);
            } else {
                saveCart();
                renderCartItems();
            }
        }
    };

    // Função para salvar o carrinho no localStorage
    function saveCart() {
        localStorage.setItem('cart', JSON.stringify(cart));
    }

    // Função para atualizar o contador de itens no carrinho
    function updateCartCounter() {
        const counter = document.getElementById('cartCounter');
        if (!counter) return;
        
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        counter.textContent = totalItems;
        
        if (totalItems > 0) {
            counter.style.display = 'inline-flex';
        } else {
            counter.style.display = 'none';
        }
    }

    // Função para renderizar itens do carrinho no modal
    function renderCartItems() {
        const cartItems = document.getElementById('cartItems');
        if (!cartItems) return;
        
        cartItems.innerHTML = '';
        
        if (cart.length === 0) {
            cartItems.innerHTML = '<p class="empty-cart">Seu carrinho está vazio</p>';
            document.getElementById('cartTotal').textContent = 'R$ 0,00';
            return;
        }
        
        let total = 0;
        
        cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;
            
            const itemElement = document.createElement('div');
            itemElement.className = 'cart-item';
            itemElement.innerHTML = `
                <img class="cart-item-image" src="data:image/jpeg;base64,${item.image}" alt="${item.name}" onerror="this.src='/assets/img/no-image.jpg'">
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-code">Código: ${item.code}</div>
                    <div class="cart-item-price">R$ ${item.price.toFixed(2).replace('.', ',')}</div>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-control">
                        <button class="quantity-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
                        <span class="quantity-value">${item.quantity}</span>
                        <button class="quantity-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                    </div>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            cartItems.appendChild(itemElement);
        });
        
        document.getElementById('cartTotal').textContent = `R$ ${total.toFixed(2).replace('.', ',')}`;
    }

    // Animação do botão do carrinho quando um item é adicionado
    function animateCartButton() {
        const button = document.getElementById('viewCartBtn');
        if (!button) return;
        
        button.classList.add('animate-pulse');
        setTimeout(() => {
            button.classList.remove('animate-pulse');
        }, 1000);
    }

    // Função para exibir notificação de toast
    function showToast(message) {
        // Verificar se já existe um toast
        let toast = document.querySelector('.toast');
        
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            document.body.appendChild(toast);
        }
        
        // Adiciona o estilo CSS inline para o toast
        toast.style.position = 'fixed';
        toast.style.bottom = '100px';
        toast.style.right = '30px';
        toast.style.backgroundColor = '#0f2566';
        toast.style.color = 'white';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '4px';
        toast.style.zIndex = '1000';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        toast.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        
        toast.textContent = message;
        
        // Anima a entrada do toast
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Remove o toast após 3 segundos
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            
            // Remove o elemento do DOM após a animação
            setTimeout(() => {
                if (toast.parentNode) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // Adicionar CSS de animação para o botão do carrinho
    document.head.insertAdjacentHTML('beforeend', `
    <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .animate-pulse {
            animation: pulse 0.5s ease-in-out;
        }
    </style>
    `);
});