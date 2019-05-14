'use strict';
let utils = {};

const START = 1;
const STOP = 0;

const sortedInsert = (arr, val) => {
    const l = arr.length;
    for (let i = 0; i < l; i++) {
        if (val <= arr[i]) {
            arr.splice(i, 0, val);
            return i
        }
    }
    arr.push(val);
    return l
};

utils.min = (k, v) => {
    if (k === null && v === null)
        return null;
    else if (k === null)
        return v;
    else if (v === null)
        return k;
    else
        return Math.min(v, k);
};

utils.flatten = (ranges) => {
    let l, i;

    const indexes = [];
    const ids = [];
    const types = [];

    l = ranges.length;
    for (i = 0; i < l; i++) {
        const range = ranges[i];

        const startI = sortedInsert(indexes, range[1]);
        ids.splice(startI, 0, range[0]);
        types.splice(startI, 0, START);

        const endI = sortedInsert(indexes, range[1] + range[2]);
        ids.splice(endI, 0, range[0]);
        types.splice(endI, 0, STOP)
    }

    const state = new Map();
    state.set(ids[0], true); // initial state

    l = ids.length;

    const sections = [];
    for (i = 1; i < l; i++) {
        const index = indexes[i];
        const lastIndex = indexes[i - 1];

        if (index > lastIndex) {
            sections.push([index - lastIndex, Array.from(state.keys())]);
        }
        if (types[i] === START) {
            state.set(ids[i], true)
        } else {
            state.delete(ids[i])
        }
    }

    return sections
};