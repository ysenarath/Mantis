markit = {};

markit.verbose = true;

markit.onselectionchange = (e) => {
    if (markit.verbose) console.log('MarkIt Selection Changed! ' + 'span = ' + e.span + ' element = ' + e.innerHTML);
};

markit.onmousedown = (e) => {
    if (markit.verbose) console.log('MarkIt Element Mouse Down! ' + ' element = ' + e.innerHTML);
};

markit.getSelection = (element) => {
    let selected;
    let prefix = '';
    if (window.getSelection) {
        let selection = window.getSelection();
        if (selection.rangeCount > 0) {
            let range = selection.getRangeAt(0);
            let preSelectionRange = range.cloneRange();
            preSelectionRange.selectNodeContents(element);
            preSelectionRange.setEnd(range.startContainer, range.startOffset);
            prefix = preSelectionRange.toString();
        }
        selected = selection.toString();
    } else if (document.selection && document.selection.type !== "Control") {
        let range = document.selection.createRange();
        selected = range.text
        // TODO: update prefix here (IE browser)
    }
    return [prefix.length, prefix.length + selected.length];
};

markit.load = (element) => {
    $(element).on('mouseup', () => {
        let selection = markit.getSelection(element);
        if (selection[0] !== selection[1]) {
            let e = {'element': element, 'span': [selection[0], selection[1] - selection[0]]};
            markit.onselectionchange(e);
        } else {
            let e = {'element': element, 'span': null};
            markit.onselectionchange(e);
        }
    });
    $(element).on('mousedown', () => {
        markit.onmousedown({'element': element})
    });
};
