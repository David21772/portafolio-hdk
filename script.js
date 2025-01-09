//La validación del formulário con javascript es considerada un desafío extra, no es obligatório realizar esta validación para realizar su entrega

// Selecciona el botón y la imagen
const showSignatureButton = document.getElementById('showSignatureButton');
const signatureImage = document.getElementById('signatureImage');

// Añade un evento al botón
showSignatureButton.addEventListener('click', () => {
    // Si la imagen está oculta, se muestra; si está visible, se oculta
    if (signatureImage.style.display === 'none') {
        signatureImage.style.display = 'block';
        showSignatureButton.textContent = 'Ocultar Firma'; // Cambia el texto del botón
    } else {
        signatureImage.style.display = 'none';
        showSignatureButton.textContent = 'Mostrar Firma'; // Cambia el texto del botón
    }
});
