function updateLineNumbers() {
    const textarea = document.querySelector('.code-editor-input');
    const lineNumbers = document.querySelector('.line-numbers');
    if (textarea && lineNumbers) {
        const lines = textarea.value.split('\n').length;
        lineNumbers.innerHTML = Array(lines).fill('<span></span>').map((_, i) => `<span>${i + 1}</span>`).join('');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('.code-editor-input');
    if (textarea) {
        textarea.addEventListener('input', updateLineNumbers);
        updateLineNumbers();  // Инициализация при загрузке
    }
});