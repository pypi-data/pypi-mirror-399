function copy_inputText_to_clipboard(input) {
    input.select();
    document.execCommand('copy');
    input.setSelectionRange(input.length, input.length);
}
