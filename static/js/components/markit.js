let markit = {};

let _ = {};

_.equals = function (as, bs) {
    if (as === bs) return true;
    if (as.size !== bs.size) return false;
    for (let a of as) if (!bs.has(a)) return false;
    return true;
};

markit.elements = {};

markit.onclick = function (e) {
};

markit.onselect = function (e) {
};

markit.onload = function (e) {
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

markit.load = function (element, text) {
    let id = element.getAttribute('data-id');

    markit.elements[id] = {
        'id': id,
        'annotations': [],
        'element': element,
    };

    function update() {
        let ranges = [];
        let selection = markit.getSelection(element);
        if (selection[0] !== selection[1]) {
            ranges.push([selection[0], selection[1] - 1, 0, 0]);
            markit.onselect({
                'document': id,
                'span': [selection[0], selection[1] - selection[0]]
            })
        } else {
            markit.onselect({
                'document': id,
                'span': null
            })
        }
        markit.elements[id].annotations.forEach(annotation => {
            ranges.push([annotation.span[0], annotation.span[1], 1, annotation]);
        });
        let points = {};
        for (let j = 0; j < ranges.length; j++) {
            let range = ranges[j];
            for (let i = range[0]; i < range[1] + 1; i++) {
                if (!(i in points)) {
                    points[i] = new Set();
                }
                if (!((i + 1) in points)) {
                    points[i + 1] = new Set();
                }
                points[i].add(j);
            }
        }
        let ordered = {};
        let prvPoint = null;
        let keys = [];
        let orderedKeys = Object.keys(points).sort((a, b) => a - b);
        for (let i = 0; i < orderedKeys.length; i++) {
            let key = orderedKeys[i];
            let point = points[key];
            if (prvPoint !== null) {
                if (!(_.equals(point, prvPoint))) {
                    ordered[key] = point;
                    keys.push(key);
                }
            } else {
                ordered[key] = point;
                keys.push(key);
            }
            prvPoint = point;
        }
        let htmlText = text;
        let prefix, temp, suffix;
        for (let i = keys.length - 1; i > 0; i--) {
            let point = Array.from(ordered[keys[i - 1]]);
            prefix = htmlText.substr(0, keys[i - 1]);
            temp = htmlText.substr(keys[i - 1], keys[i] - keys[i - 1]);
            suffix = htmlText.substr(keys[i]);
            let annotations = [];
            let type = null;
            let styles = '';
            for (let k = 0; k < point.length; k++) {
                if (ranges[point[k]][2] !== 0 && type !== 'highlight') {
                    type = 'annotation';
                    let annotation = ranges[point[k]][3];
                    styles = 'style="';
                    if (typeof annotation.color !== 'undefined') {
                        styles += 'background:' + annotation.color + ';'
                    }
                    styles += 'cursor:pointer' + '"';
                    annotations.push(annotation.id);
                } else {
                    type = 'highlight';
                    styles = ''
                }
            }
            if (point.length > 0) {
                let events = ' onclick="markit.onclick([' + annotations + '])" ';
                temp = '<mark class="' + type + '" ' + events + styles + '>' + temp + '</mark>';
            }
            htmlText = prefix + temp + suffix;
        }
        $(element).html(htmlText);
    }

    markit.elements[id].annotations.push = function () {
        Array.prototype.push.apply(this, arguments);
        update();
    };

    update();

    $(element).on('click', () => {
        update();
    });

    markit.onload(id);
};

$(function () {
    $('div.markit[onload]').trigger('onload');
});
