function onInputChange() {
    let options = document.getElementsByName('options')
    if (options[options.length - 1].value !== '') {
        let optionsContainer = document.getElementById('options-container')
        let newInput = createElementFromHTML('<label><input class="form-control" type="text" name="options" autocomplete="off" onchange="onInputChange()"></label>')
        optionsContainer.appendChild(newInput)
    }
}

function createElementFromHTML(htmlString) {
    let div = document.createElement('div');
    div.innerHTML = htmlString.trim();

    // Change this to div.childNodes to support multiple top-level nodes
    return div.firstChild;
}