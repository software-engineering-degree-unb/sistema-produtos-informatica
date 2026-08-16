// ################################################## SCRIPT PARA MODAL LEGENDA

var modal = document.getElementById("infoModal");
var infoIcon = document.getElementById("infoIcon");
var span = document.getElementById("closeModal");
var closeModalButton = document.getElementById("closeModalButton");

infoIcon.onclick = function() {
    modal.classList.add("show");
    modal.style.display = "block"; 
}

span.onclick = function() {
    closeModal();
}

window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}

function closeModal() {
    modal.classList.remove("show");
    setTimeout(function() {
        modal.style.display = "none";
    }, 300); 
}

closeModalButton.onclick = function() {
    closeModal();
}

// ################################################## SCRIPT PARA MINIATURA DE IMAGEM

function previewImage(event) {
    const file = event.target.files[0];
    const imagePreview = document.getElementById('imagePreview');
    const thumbnail = document.getElementById('thumbnail');
    const fileName = document.getElementById('fileName');
    const removeImage = document.getElementById('removeImage');

    if (file) {
        // Código existente para preview de imagem
    }
}

// ################################################## SCRIPT PARA VALIDAR FORMULARIO

function formatarValor(input) {
    // Remove tudo que não é número
    let valor = input.value.replace(/\D/g, '');
    
    // Converte para número e divide por 100 para ter 2 casas decimais
    valor = (parseInt(valor) / 100).toFixed(2);
    
    // Limita a 9999.99
    if (parseFloat(valor) > 99999.99) {
        // Limite existente
    }
    
    // Formata para o padrão brasileiro
    valor = valor.replace('.', ',');
    
    // Adiciona R$ na frente
    input.value = valor;
}

function validarFormulario() {
    var nome = document.getElementById('nome').value.trim();
    var codigo = document.getElementById('codigo').value.trim();
    var descricao = document.getElementById('descricao').value.trim();
    var tipoProduto = document.getElementById('tipoProduto').value;
    var valor = document.getElementById('valor').value.trim();
    var imagem = document.getElementById('imagem').value;
    
    // Verifica se precisa validar valor locação

    var submitBtn = document.getElementById('submitBtn');
    if (nome && codigo && descricao && tipoProduto && valor && imagem) {
        // Habilitar botão
    } else {
        // Desabilitar botão
    }
}

// ################################################## SCRIPT PARA REMOVER IMAGEM

window.removeImage = function() {
    const fileInput = document.getElementById('imagem');
    const thumbnail = document.getElementById('thumbnail');
    const fileName = document.getElementById('fileName');
    const removeImageButton = document.getElementById('removeImage');

    fileInput.value = '';
    thumbnail.src = '';
    thumbnail.style.display = 'none';
    fileName.textContent = '';
    fileName.style.display = 'none';
    removeImageButton.style.display = 'none';

    validarFormulario();
}

// ################################################## SCRIPT PARA MODAL NOVA CATEGORIA

document.addEventListener('DOMContentLoaded', function() {
    // Referências aos elementos do modal de categoria
    const categoryModal = document.getElementById('categoryModal');
    const addCategoryBtn = document.getElementById('addCategoryBtn');
    const closeCategoryModal = document.getElementById('closeCategoryModal');
    const cancelCategoryBtn = document.getElementById('cancelCategoryBtn');
    const saveCategoryBtn = document.getElementById('saveCategoryBtn');
    const newCategoryInput = document.getElementById('newCategory');
    const categoryErrorMsg = document.getElementById('categoryErrorMsg');
    const tipoProdutoSelect = document.getElementById('tipoProduto');
    
    if (addCategoryBtn) {
        // Abrir modal
        addCategoryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            categoryModal.classList.add("show");
            categoryModal.style.display = "block";
            newCategoryInput.value = '';
            categoryErrorMsg.textContent = '';
        });
    }
    
    if (closeCategoryModal) {
        closeCategoryModal.addEventListener('click', function() {
            closeCategModal();
        });
    }
    
    if (cancelCategoryBtn) {
        cancelCategoryBtn.addEventListener('click', function() {
            closeCategModal();
        });
    }

    // Função para fechar o modal
    function closeCategModal() {
        categoryModal.classList.remove("show");
        setTimeout(function() {
            categoryModal.style.display = "none";
        }, 300);
    }

    // Fechar ao clicar fora do modal
    window.addEventListener('click', function(event) {
        if (event.target == categoryModal) {
            closeCategModal();
        }
    });

    // Salvar nova categoria
    if (saveCategoryBtn) {
        saveCategoryBtn.addEventListener('click', function() {
            const newCategory = newCategoryInput.value.trim();
            
            if (!newCategory) {
                categoryErrorMsg.textContent = 'Por favor, insira um nome para a categoria.';
                categoryErrorMsg.style.display = 'block';
                return;
            }
    
            // Enviar requisição AJAX para salvar categoria
            fetch('/produtos/tipo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'descricao=' + encodeURIComponent(newCategory)
            })
            .then(response => {
                // Clone a resposta para poder ler o texto bruto
                const responseClone = response.clone();
                
                // Tentar fazer o parse como JSON
                return response.json()
                    .catch(err => {
                        // Se falhar, mostrar o texto bruto da resposta
                        return responseClone.text().then(text => {
                            console.error('Resposta do servidor (não é JSON válido):', text);
                            throw new Error('Resposta inválida do servidor');
                        });
                    });
            })
            .then(data => {
                if (data.success) {
                    // Adicionar nova categoria ao select
                    const option = document.createElement('option');
                    option.value = data.id;
                    option.textContent = newCategory;
                    tipoProdutoSelect.appendChild(option);
                    
                    // Selecionar a nova categoria
                    tipoProdutoSelect.value = data.id;
                    
                    // Remova a chamada para validarFormulario que está causando erro
                    // validarFormulario();
                    
                    // Fechar modal
                    closeCategModal();
                } else {
                    categoryErrorMsg.textContent = data.message || 'Erro ao adicionar categoria.';
                    categoryErrorMsg.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                categoryErrorMsg.textContent = 'Erro ao processar solicitação.';
                categoryErrorMsg.style.display = 'block';
            });
        });
    }
});

// ################################################## SCRIPT PARA INICIALIZAÇÃO E EVENTOS

document.addEventListener('DOMContentLoaded', function() {
    const MAX_IMAGES = 10;
    let currentImages = 0;
    let activeFiles = new Map(); // Mapa para controlar arquivos ativos

    function updateImagePreview(files) {
        const imagePreview = document.getElementById('imagePreview');
        
        if (currentImages === 0) {
            imagePreview.innerHTML = '';
        }

        if (currentImages + files.length > MAX_IMAGES) {
            alert(`Você pode adicionar no máximo ${MAX_IMAGES} imagens.`);
            return;
        }

        Array.from(files).forEach(file => {
            if (currentImages >= MAX_IMAGES) return;

            const reader = new FileReader();
            const previewContainer = document.createElement('div');
            previewContainer.className = 'preview-item';
            
            // Usar o nome e timestamp como ID único
            const fileId = `${file.name}-${Date.now()}`;
            activeFiles.set(fileId, file);

            reader.onload = function(e) {
                previewContainer.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <span class="filename">${file.name}</span>
                    <button type="button" class="remove-image" data-file-id="${fileId}">×</button>
                `;
            };

            reader.readAsDataURL(file);
            imagePreview.appendChild(previewContainer);
            currentImages++;
        });

        updateUploadButton();
        validateForm();
    }


    // Sobrescrever o envio do formulário
    const form = document.getElementById('equipForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Debug - mostrar quantidade de arquivos ativos
        console.log('Arquivos ativos:', activeFiles.size);
        
        // Criar um novo FormData
        const formData = new FormData();
        
        // Adicionar todos os campos do formulário exceto o input file
        const formElements = this.elements;
        for (let i = 0; i < formElements.length; i++) {
            const field = formElements[i];
            if (field.type !== 'file') {
                formData.append(field.name, field.value);
            }
        }
        
        // Adicionar apenas as imagens ativas
        let imageCount = 0;
        activeFiles.forEach((file, fileId) => {
            console.log('Adicionando arquivo:', file.name); // Debug
            formData.append(`imagens[${imageCount}]`, file);
            imageCount++;
        });

        // Debug - listar todos os items no FormData
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }

        // Enviar o formulário via AJAX
        fetch(this.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(response => {
            console.log('Resposta:', response); // Debug
            if(response.includes('success=1')) {
                window.location.href = '/produtos?success=1';
            } else {
                window.location.href = '/produtos/novo?error=1';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            window.location.href = '/produtos/novo?error=1';
        });
    });

    // Evento para remover imagem
    document.getElementById('imagePreview').addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-image')) {
            const fileId = e.target.getAttribute('data-file-id');
            console.log('Removendo arquivo:', fileId); // Debug
            activeFiles.delete(fileId);
            e.target.parentElement.remove();
            currentImages--;
            updateUploadButton();
            validateForm();
        }
    });

    function updateUploadButton() {
        const uploadLabel = document.querySelector('.upload-container label');
        uploadLabel.style.display = currentImages >= MAX_IMAGES ? 'none' : 'block';
        uploadLabel.textContent = `Adicionar Imagem (${currentImages}/${MAX_IMAGES})`;
    }

    // Configura input de arquivo
    const fileInput = document.getElementById('imagens');
    fileInput.addEventListener('change', function(event) {
        updateImagePreview(event.target.files);
    });

    

// ################################################################################


    const camposValor = ['valor'];
    camposValor.forEach(campo => {
        const elemento = document.getElementById(campo);
        if (elemento) {
            // Adiciona R$ antes do campo
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            elemento.parentNode.insertBefore(wrapper, elemento);
            wrapper.appendChild(elemento);

            const prefix = document.createElement('span');
            prefix.textContent = 'R$ ';
            prefix.style.position = 'absolute';
            prefix.style.left = '8px';
            prefix.style.top = '36%';
            prefix.style.transform = 'translateY(-50%)';
            prefix.style.color = '#000';
            wrapper.insertBefore(prefix, elemento);

            // Ajusta o padding do input para acomodar o prefixo
            elemento.style.paddingLeft = '30px';

            // Adiciona eventos de formatação
            elemento.addEventListener('input', function() {
                formatarValor(this);
            });
            elemento.addEventListener('blur', function() {
                if (this.value) {
                    let valor = this.value.replace(/\D/g, '');
                    if (valor) {
                        formatarValor(this);
                    }
                }
            });
        }
    });

    // Validação do formulário
    function validateForm() {
        const requiredFields = ['nome', 'codigo', 'tipoProduto', 'valor', 'descricao'];
        const submitBtn = document.getElementById('submitBtn');
        
        const allFieldsFilled = requiredFields.every(field => {
            const element = document.getElementById(field);
            return element && element.value.trim() !== '';
        });
    
        // Remover a verificação de imagens obrigatórias
        submitBtn.disabled = !allFieldsFilled;
        submitBtn.style.backgroundColor = submitBtn.disabled ? '#85ad98' : '#0f2566';
        submitBtn.style.cursor = submitBtn.disabled ? 'not-allowed' : 'pointer';
    }

    // Adiciona listeners para validação
    document.querySelectorAll('input, select, textarea').forEach(element => {
        element.addEventListener('input', validateForm);
    });
});