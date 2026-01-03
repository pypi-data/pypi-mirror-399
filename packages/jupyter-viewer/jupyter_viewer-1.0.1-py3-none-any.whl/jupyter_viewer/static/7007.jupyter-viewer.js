"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7007],{

/***/ 51466
(module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   A: () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(74608);
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(87249);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

.jp-Terminal {
  min-width: 240px;
  min-height: 120px;
}

.jp-Terminal-body {
  padding: 8px;
}

[data-term-theme='inherit'] .xterm .xterm-screen canvas {
  border: 1px solid var(--jp-layout-color0);
}

[data-term-theme='light'] .xterm .xterm-screen canvas {
  border: 1px solid #fff;
}

[data-term-theme='dark'] .xterm .xterm-screen canvas {
  border: 1px solid #000;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 86739
(module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   A: () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(74608);
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(87249);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/**
 * Copyright (c) 2014 The xterm.js authors. All rights reserved.
 * Copyright (c) 2012-2013, Christopher Jeffrey (MIT License)
 * https://github.com/chjj/term.js
 * @license MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 * Originally forked from (with the author's permission):
 *   Fabrice Bellard's javascript vt100 for jslinux:
 *   http://bellard.org/jslinux/
 *   Copyright (c) 2011 Fabrice Bellard
 *   The original design remains. The terminal itself
 *   has been extended to include xterm CSI codes, among
 *   other features.
 */

/**
 *  Default styles for xterm.js
 */

.xterm {
    cursor: text;
    position: relative;
    user-select: none;
    -ms-user-select: none;
    -webkit-user-select: none;
}

.xterm.focus,
.xterm:focus {
    outline: none;
}

.xterm .xterm-helpers {
    position: absolute;
    top: 0;
    /**
     * The z-index of the helpers must be higher than the canvases in order for
     * IMEs to appear on top.
     */
    z-index: 5;
}

.xterm .xterm-helper-textarea {
    padding: 0;
    border: 0;
    margin: 0;
    /* Move textarea out of the screen to the far left, so that the cursor is not visible */
    position: absolute;
    opacity: 0;
    left: -9999em;
    top: 0;
    width: 0;
    height: 0;
    z-index: -5;
    /** Prevent wrapping so the IME appears against the textarea at the correct position */
    white-space: nowrap;
    overflow: hidden;
    resize: none;
}

.xterm .composition-view {
    /* TODO: Composition position got messed up somewhere */
    background: #000;
    color: #FFF;
    display: none;
    position: absolute;
    white-space: nowrap;
    z-index: 1;
}

.xterm .composition-view.active {
    display: block;
}

.xterm .xterm-viewport {
    /* On OS X this is required in order for the scroll bar to appear fully opaque */
    background-color: #000;
    overflow-y: scroll;
    cursor: default;
    position: absolute;
    right: 0;
    left: 0;
    top: 0;
    bottom: 0;
}

.xterm .xterm-screen {
    position: relative;
}

.xterm .xterm-screen canvas {
    position: absolute;
    left: 0;
    top: 0;
}

.xterm .xterm-scroll-area {
    visibility: hidden;
}

.xterm-char-measure-element {
    display: inline-block;
    visibility: hidden;
    position: absolute;
    top: 0;
    left: -9999em;
    line-height: normal;
}

.xterm.enable-mouse-events {
    /* When mouse events are enabled (eg. tmux), revert to the standard pointer cursor */
    cursor: default;
}

.xterm.xterm-cursor-pointer,
.xterm .xterm-cursor-pointer {
    cursor: pointer;
}

.xterm.column-select.focus {
    /* Column selection mode */
    cursor: crosshair;
}

.xterm .xterm-accessibility:not(.debug),
.xterm .xterm-message {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    right: 0;
    z-index: 10;
    color: transparent;
    pointer-events: none;
}

.xterm .xterm-accessibility-tree:not(.debug) *::selection {
  color: transparent;
}

.xterm .xterm-accessibility-tree {
  user-select: text;
  white-space: pre;
}

.xterm .live-region {
    position: absolute;
    left: -9999px;
    width: 1px;
    height: 1px;
    overflow: hidden;
}

.xterm-dim {
    /* Dim should not apply to background, so the opacity of the foreground color is applied
     * explicitly in the generated class and reset to 1 here */
    opacity: 1 !important;
}

.xterm-underline-1 { text-decoration: underline; }
.xterm-underline-2 { text-decoration: double underline; }
.xterm-underline-3 { text-decoration: wavy underline; }
.xterm-underline-4 { text-decoration: dotted underline; }
.xterm-underline-5 { text-decoration: dashed underline; }

.xterm-overline {
    text-decoration: overline;
}

.xterm-overline.xterm-underline-1 { text-decoration: overline underline; }
.xterm-overline.xterm-underline-2 { text-decoration: overline double underline; }
.xterm-overline.xterm-underline-3 { text-decoration: overline wavy underline; }
.xterm-overline.xterm-underline-4 { text-decoration: overline dotted underline; }
.xterm-overline.xterm-underline-5 { text-decoration: overline dashed underline; }

.xterm-strikethrough {
    text-decoration: line-through;
}

.xterm-screen .xterm-decoration-container .xterm-decoration {
	z-index: 6;
	position: absolute;
}

.xterm-screen .xterm-decoration-container .xterm-decoration.xterm-decoration-top-layer {
	z-index: 7;
}

.xterm-decoration-overview-ruler {
    z-index: 8;
    position: absolute;
    top: 0;
    right: 0;
    pointer-events: none;
}

.xterm-decoration-top {
    z-index: 2;
    position: relative;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 97007
(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {


// EXTERNAL MODULE: ./node_modules/@lumino/widgets/style/index.js + 1 modules
var style = __webpack_require__(47214);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/apputils/style/index.js + 1 modules
var apputils_style = __webpack_require__(84940);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js
var injectStylesIntoStyleTag = __webpack_require__(85072);
var injectStylesIntoStyleTag_default = /*#__PURE__*/__webpack_require__.n(injectStylesIntoStyleTag);
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/@xterm/xterm/css/xterm.css
var xterm = __webpack_require__(86739);
;// ./node_modules/@xterm/xterm/css/xterm.css

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = injectStylesIntoStyleTag_default()(xterm/* default */.A, options);



/* harmony default export */ const css_xterm = (xterm/* default */.A.locals || {});
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/@jupyterlab/terminal/style/base.css
var base = __webpack_require__(51466);
;// ./node_modules/@jupyterlab/terminal/style/base.css

            

var base_options = {};

base_options.insert = "head";
base_options.singleton = false;

var base_update = injectStylesIntoStyleTag_default()(base/* default */.A, base_options);



/* harmony default export */ const style_base = (base/* default */.A.locals || {});
;// ./node_modules/@jupyterlab/terminal/style/index.js
/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/* This file was auto-generated by ensurePackage() in @jupyterlab/buildutils */





/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzAwNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7Ozs7Ozs7QUNoQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNqT0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL3Rlcm1pbmFsL3N0eWxlL2Jhc2UuY3NzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQHh0ZXJtL3h0ZXJtL2Nzcy94dGVybS5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AeHRlcm0veHRlcm0vY3NzL3h0ZXJtLmNzcz81YzMzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGp1cHl0ZXJsYWIvdGVybWluYWwvc3R5bGUvYmFzZS5jc3M/ZjA5NiIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL3Rlcm1pbmFsL3N0eWxlL2luZGV4LmpzIl0sInNvdXJjZXNDb250ZW50IjpbIi8vIEltcG9ydHNcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9ub1NvdXJjZU1hcHMuanNcIjtcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL2FwaS5qc1wiO1xudmFyIF9fX0NTU19MT0FERVJfRVhQT1JUX19fID0gX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fKF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18pO1xuLy8gTW9kdWxlXG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5wdXNoKFttb2R1bGUuaWQsIGAvKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxufCBEaXN0cmlidXRlZCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIE1vZGlmaWVkIEJTRCBMaWNlbnNlLlxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4uanAtVGVybWluYWwge1xuICBtaW4td2lkdGg6IDI0MHB4O1xuICBtaW4taGVpZ2h0OiAxMjBweDtcbn1cblxuLmpwLVRlcm1pbmFsLWJvZHkge1xuICBwYWRkaW5nOiA4cHg7XG59XG5cbltkYXRhLXRlcm0tdGhlbWU9J2luaGVyaXQnXSAueHRlcm0gLnh0ZXJtLXNjcmVlbiBjYW52YXMge1xuICBib3JkZXI6IDFweCBzb2xpZCB2YXIoLS1qcC1sYXlvdXQtY29sb3IwKTtcbn1cblxuW2RhdGEtdGVybS10aGVtZT0nbGlnaHQnXSAueHRlcm0gLnh0ZXJtLXNjcmVlbiBjYW52YXMge1xuICBib3JkZXI6IDFweCBzb2xpZCAjZmZmO1xufVxuXG5bZGF0YS10ZXJtLXRoZW1lPSdkYXJrJ10gLnh0ZXJtIC54dGVybS1zY3JlZW4gY2FudmFzIHtcbiAgYm9yZGVyOiAxcHggc29saWQgIzAwMDtcbn1cbmAsIFwiXCJdKTtcbi8vIEV4cG9ydHNcbmV4cG9ydCBkZWZhdWx0IF9fX0NTU19MT0FERVJfRVhQT1JUX19fO1xuIiwiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qKlxuICogQ29weXJpZ2h0IChjKSAyMDE0IFRoZSB4dGVybS5qcyBhdXRob3JzLiBBbGwgcmlnaHRzIHJlc2VydmVkLlxuICogQ29weXJpZ2h0IChjKSAyMDEyLTIwMTMsIENocmlzdG9waGVyIEplZmZyZXkgKE1JVCBMaWNlbnNlKVxuICogaHR0cHM6Ly9naXRodWIuY29tL2NoamovdGVybS5qc1xuICogQGxpY2Vuc2UgTUlUXG4gKlxuICogUGVybWlzc2lvbiBpcyBoZXJlYnkgZ3JhbnRlZCwgZnJlZSBvZiBjaGFyZ2UsIHRvIGFueSBwZXJzb24gb2J0YWluaW5nIGEgY29weVxuICogb2YgdGhpcyBzb2Z0d2FyZSBhbmQgYXNzb2NpYXRlZCBkb2N1bWVudGF0aW9uIGZpbGVzICh0aGUgXCJTb2Z0d2FyZVwiKSwgdG8gZGVhbFxuICogaW4gdGhlIFNvZnR3YXJlIHdpdGhvdXQgcmVzdHJpY3Rpb24sIGluY2x1ZGluZyB3aXRob3V0IGxpbWl0YXRpb24gdGhlIHJpZ2h0c1xuICogdG8gdXNlLCBjb3B5LCBtb2RpZnksIG1lcmdlLCBwdWJsaXNoLCBkaXN0cmlidXRlLCBzdWJsaWNlbnNlLCBhbmQvb3Igc2VsbFxuICogY29waWVzIG9mIHRoZSBTb2Z0d2FyZSwgYW5kIHRvIHBlcm1pdCBwZXJzb25zIHRvIHdob20gdGhlIFNvZnR3YXJlIGlzXG4gKiBmdXJuaXNoZWQgdG8gZG8gc28sIHN1YmplY3QgdG8gdGhlIGZvbGxvd2luZyBjb25kaXRpb25zOlxuICpcbiAqIFRoZSBhYm92ZSBjb3B5cmlnaHQgbm90aWNlIGFuZCB0aGlzIHBlcm1pc3Npb24gbm90aWNlIHNoYWxsIGJlIGluY2x1ZGVkIGluXG4gKiBhbGwgY29waWVzIG9yIHN1YnN0YW50aWFsIHBvcnRpb25zIG9mIHRoZSBTb2Z0d2FyZS5cbiAqXG4gKiBUSEUgU09GVFdBUkUgSVMgUFJPVklERUQgXCJBUyBJU1wiLCBXSVRIT1VUIFdBUlJBTlRZIE9GIEFOWSBLSU5ELCBFWFBSRVNTIE9SXG4gKiBJTVBMSUVELCBJTkNMVURJTkcgQlVUIE5PVCBMSU1JVEVEIFRPIFRIRSBXQVJSQU5USUVTIE9GIE1FUkNIQU5UQUJJTElUWSxcbiAqIEZJVE5FU1MgRk9SIEEgUEFSVElDVUxBUiBQVVJQT1NFIEFORCBOT05JTkZSSU5HRU1FTlQuIElOIE5PIEVWRU5UIFNIQUxMIFRIRVxuICogQVVUSE9SUyBPUiBDT1BZUklHSFQgSE9MREVSUyBCRSBMSUFCTEUgRk9SIEFOWSBDTEFJTSwgREFNQUdFUyBPUiBPVEhFUlxuICogTElBQklMSVRZLCBXSEVUSEVSIElOIEFOIEFDVElPTiBPRiBDT05UUkFDVCwgVE9SVCBPUiBPVEhFUldJU0UsIEFSSVNJTkcgRlJPTSxcbiAqIE9VVCBPRiBPUiBJTiBDT05ORUNUSU9OIFdJVEggVEhFIFNPRlRXQVJFIE9SIFRIRSBVU0UgT1IgT1RIRVIgREVBTElOR1MgSU5cbiAqIFRIRSBTT0ZUV0FSRS5cbiAqXG4gKiBPcmlnaW5hbGx5IGZvcmtlZCBmcm9tICh3aXRoIHRoZSBhdXRob3IncyBwZXJtaXNzaW9uKTpcbiAqICAgRmFicmljZSBCZWxsYXJkJ3MgamF2YXNjcmlwdCB2dDEwMCBmb3IganNsaW51eDpcbiAqICAgaHR0cDovL2JlbGxhcmQub3JnL2pzbGludXgvXG4gKiAgIENvcHlyaWdodCAoYykgMjAxMSBGYWJyaWNlIEJlbGxhcmRcbiAqICAgVGhlIG9yaWdpbmFsIGRlc2lnbiByZW1haW5zLiBUaGUgdGVybWluYWwgaXRzZWxmXG4gKiAgIGhhcyBiZWVuIGV4dGVuZGVkIHRvIGluY2x1ZGUgeHRlcm0gQ1NJIGNvZGVzLCBhbW9uZ1xuICogICBvdGhlciBmZWF0dXJlcy5cbiAqL1xuXG4vKipcbiAqICBEZWZhdWx0IHN0eWxlcyBmb3IgeHRlcm0uanNcbiAqL1xuXG4ueHRlcm0ge1xuICAgIGN1cnNvcjogdGV4dDtcbiAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG4gICAgdXNlci1zZWxlY3Q6IG5vbmU7XG4gICAgLW1zLXVzZXItc2VsZWN0OiBub25lO1xuICAgIC13ZWJraXQtdXNlci1zZWxlY3Q6IG5vbmU7XG59XG5cbi54dGVybS5mb2N1cyxcbi54dGVybTpmb2N1cyB7XG4gICAgb3V0bGluZTogbm9uZTtcbn1cblxuLnh0ZXJtIC54dGVybS1oZWxwZXJzIHtcbiAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gICAgdG9wOiAwO1xuICAgIC8qKlxuICAgICAqIFRoZSB6LWluZGV4IG9mIHRoZSBoZWxwZXJzIG11c3QgYmUgaGlnaGVyIHRoYW4gdGhlIGNhbnZhc2VzIGluIG9yZGVyIGZvclxuICAgICAqIElNRXMgdG8gYXBwZWFyIG9uIHRvcC5cbiAgICAgKi9cbiAgICB6LWluZGV4OiA1O1xufVxuXG4ueHRlcm0gLnh0ZXJtLWhlbHBlci10ZXh0YXJlYSB7XG4gICAgcGFkZGluZzogMDtcbiAgICBib3JkZXI6IDA7XG4gICAgbWFyZ2luOiAwO1xuICAgIC8qIE1vdmUgdGV4dGFyZWEgb3V0IG9mIHRoZSBzY3JlZW4gdG8gdGhlIGZhciBsZWZ0LCBzbyB0aGF0IHRoZSBjdXJzb3IgaXMgbm90IHZpc2libGUgKi9cbiAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gICAgb3BhY2l0eTogMDtcbiAgICBsZWZ0OiAtOTk5OWVtO1xuICAgIHRvcDogMDtcbiAgICB3aWR0aDogMDtcbiAgICBoZWlnaHQ6IDA7XG4gICAgei1pbmRleDogLTU7XG4gICAgLyoqIFByZXZlbnQgd3JhcHBpbmcgc28gdGhlIElNRSBhcHBlYXJzIGFnYWluc3QgdGhlIHRleHRhcmVhIGF0IHRoZSBjb3JyZWN0IHBvc2l0aW9uICovXG4gICAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbiAgICBvdmVyZmxvdzogaGlkZGVuO1xuICAgIHJlc2l6ZTogbm9uZTtcbn1cblxuLnh0ZXJtIC5jb21wb3NpdGlvbi12aWV3IHtcbiAgICAvKiBUT0RPOiBDb21wb3NpdGlvbiBwb3NpdGlvbiBnb3QgbWVzc2VkIHVwIHNvbWV3aGVyZSAqL1xuICAgIGJhY2tncm91bmQ6ICMwMDA7XG4gICAgY29sb3I6ICNGRkY7XG4gICAgZGlzcGxheTogbm9uZTtcbiAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gICAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbiAgICB6LWluZGV4OiAxO1xufVxuXG4ueHRlcm0gLmNvbXBvc2l0aW9uLXZpZXcuYWN0aXZlIHtcbiAgICBkaXNwbGF5OiBibG9jaztcbn1cblxuLnh0ZXJtIC54dGVybS12aWV3cG9ydCB7XG4gICAgLyogT24gT1MgWCB0aGlzIGlzIHJlcXVpcmVkIGluIG9yZGVyIGZvciB0aGUgc2Nyb2xsIGJhciB0byBhcHBlYXIgZnVsbHkgb3BhcXVlICovXG4gICAgYmFja2dyb3VuZC1jb2xvcjogIzAwMDtcbiAgICBvdmVyZmxvdy15OiBzY3JvbGw7XG4gICAgY3Vyc29yOiBkZWZhdWx0O1xuICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICByaWdodDogMDtcbiAgICBsZWZ0OiAwO1xuICAgIHRvcDogMDtcbiAgICBib3R0b206IDA7XG59XG5cbi54dGVybSAueHRlcm0tc2NyZWVuIHtcbiAgICBwb3NpdGlvbjogcmVsYXRpdmU7XG59XG5cbi54dGVybSAueHRlcm0tc2NyZWVuIGNhbnZhcyB7XG4gICAgcG9zaXRpb246IGFic29sdXRlO1xuICAgIGxlZnQ6IDA7XG4gICAgdG9wOiAwO1xufVxuXG4ueHRlcm0gLnh0ZXJtLXNjcm9sbC1hcmVhIHtcbiAgICB2aXNpYmlsaXR5OiBoaWRkZW47XG59XG5cbi54dGVybS1jaGFyLW1lYXN1cmUtZWxlbWVudCB7XG4gICAgZGlzcGxheTogaW5saW5lLWJsb2NrO1xuICAgIHZpc2liaWxpdHk6IGhpZGRlbjtcbiAgICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gICAgdG9wOiAwO1xuICAgIGxlZnQ6IC05OTk5ZW07XG4gICAgbGluZS1oZWlnaHQ6IG5vcm1hbDtcbn1cblxuLnh0ZXJtLmVuYWJsZS1tb3VzZS1ldmVudHMge1xuICAgIC8qIFdoZW4gbW91c2UgZXZlbnRzIGFyZSBlbmFibGVkIChlZy4gdG11eCksIHJldmVydCB0byB0aGUgc3RhbmRhcmQgcG9pbnRlciBjdXJzb3IgKi9cbiAgICBjdXJzb3I6IGRlZmF1bHQ7XG59XG5cbi54dGVybS54dGVybS1jdXJzb3ItcG9pbnRlcixcbi54dGVybSAueHRlcm0tY3Vyc29yLXBvaW50ZXIge1xuICAgIGN1cnNvcjogcG9pbnRlcjtcbn1cblxuLnh0ZXJtLmNvbHVtbi1zZWxlY3QuZm9jdXMge1xuICAgIC8qIENvbHVtbiBzZWxlY3Rpb24gbW9kZSAqL1xuICAgIGN1cnNvcjogY3Jvc3NoYWlyO1xufVxuXG4ueHRlcm0gLnh0ZXJtLWFjY2Vzc2liaWxpdHk6bm90KC5kZWJ1ZyksXG4ueHRlcm0gLnh0ZXJtLW1lc3NhZ2Uge1xuICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICBsZWZ0OiAwO1xuICAgIHRvcDogMDtcbiAgICBib3R0b206IDA7XG4gICAgcmlnaHQ6IDA7XG4gICAgei1pbmRleDogMTA7XG4gICAgY29sb3I6IHRyYW5zcGFyZW50O1xuICAgIHBvaW50ZXItZXZlbnRzOiBub25lO1xufVxuXG4ueHRlcm0gLnh0ZXJtLWFjY2Vzc2liaWxpdHktdHJlZTpub3QoLmRlYnVnKSAqOjpzZWxlY3Rpb24ge1xuICBjb2xvcjogdHJhbnNwYXJlbnQ7XG59XG5cbi54dGVybSAueHRlcm0tYWNjZXNzaWJpbGl0eS10cmVlIHtcbiAgdXNlci1zZWxlY3Q6IHRleHQ7XG4gIHdoaXRlLXNwYWNlOiBwcmU7XG59XG5cbi54dGVybSAubGl2ZS1yZWdpb24ge1xuICAgIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgICBsZWZ0OiAtOTk5OXB4O1xuICAgIHdpZHRoOiAxcHg7XG4gICAgaGVpZ2h0OiAxcHg7XG4gICAgb3ZlcmZsb3c6IGhpZGRlbjtcbn1cblxuLnh0ZXJtLWRpbSB7XG4gICAgLyogRGltIHNob3VsZCBub3QgYXBwbHkgdG8gYmFja2dyb3VuZCwgc28gdGhlIG9wYWNpdHkgb2YgdGhlIGZvcmVncm91bmQgY29sb3IgaXMgYXBwbGllZFxuICAgICAqIGV4cGxpY2l0bHkgaW4gdGhlIGdlbmVyYXRlZCBjbGFzcyBhbmQgcmVzZXQgdG8gMSBoZXJlICovXG4gICAgb3BhY2l0eTogMSAhaW1wb3J0YW50O1xufVxuXG4ueHRlcm0tdW5kZXJsaW5lLTEgeyB0ZXh0LWRlY29yYXRpb246IHVuZGVybGluZTsgfVxuLnh0ZXJtLXVuZGVybGluZS0yIHsgdGV4dC1kZWNvcmF0aW9uOiBkb3VibGUgdW5kZXJsaW5lOyB9XG4ueHRlcm0tdW5kZXJsaW5lLTMgeyB0ZXh0LWRlY29yYXRpb246IHdhdnkgdW5kZXJsaW5lOyB9XG4ueHRlcm0tdW5kZXJsaW5lLTQgeyB0ZXh0LWRlY29yYXRpb246IGRvdHRlZCB1bmRlcmxpbmU7IH1cbi54dGVybS11bmRlcmxpbmUtNSB7IHRleHQtZGVjb3JhdGlvbjogZGFzaGVkIHVuZGVybGluZTsgfVxuXG4ueHRlcm0tb3ZlcmxpbmUge1xuICAgIHRleHQtZGVjb3JhdGlvbjogb3ZlcmxpbmU7XG59XG5cbi54dGVybS1vdmVybGluZS54dGVybS11bmRlcmxpbmUtMSB7IHRleHQtZGVjb3JhdGlvbjogb3ZlcmxpbmUgdW5kZXJsaW5lOyB9XG4ueHRlcm0tb3ZlcmxpbmUueHRlcm0tdW5kZXJsaW5lLTIgeyB0ZXh0LWRlY29yYXRpb246IG92ZXJsaW5lIGRvdWJsZSB1bmRlcmxpbmU7IH1cbi54dGVybS1vdmVybGluZS54dGVybS11bmRlcmxpbmUtMyB7IHRleHQtZGVjb3JhdGlvbjogb3ZlcmxpbmUgd2F2eSB1bmRlcmxpbmU7IH1cbi54dGVybS1vdmVybGluZS54dGVybS11bmRlcmxpbmUtNCB7IHRleHQtZGVjb3JhdGlvbjogb3ZlcmxpbmUgZG90dGVkIHVuZGVybGluZTsgfVxuLnh0ZXJtLW92ZXJsaW5lLnh0ZXJtLXVuZGVybGluZS01IHsgdGV4dC1kZWNvcmF0aW9uOiBvdmVybGluZSBkYXNoZWQgdW5kZXJsaW5lOyB9XG5cbi54dGVybS1zdHJpa2V0aHJvdWdoIHtcbiAgICB0ZXh0LWRlY29yYXRpb246IGxpbmUtdGhyb3VnaDtcbn1cblxuLnh0ZXJtLXNjcmVlbiAueHRlcm0tZGVjb3JhdGlvbi1jb250YWluZXIgLnh0ZXJtLWRlY29yYXRpb24ge1xuXHR6LWluZGV4OiA2O1xuXHRwb3NpdGlvbjogYWJzb2x1dGU7XG59XG5cbi54dGVybS1zY3JlZW4gLnh0ZXJtLWRlY29yYXRpb24tY29udGFpbmVyIC54dGVybS1kZWNvcmF0aW9uLnh0ZXJtLWRlY29yYXRpb24tdG9wLWxheWVyIHtcblx0ei1pbmRleDogNztcbn1cblxuLnh0ZXJtLWRlY29yYXRpb24tb3ZlcnZpZXctcnVsZXIge1xuICAgIHotaW5kZXg6IDg7XG4gICAgcG9zaXRpb246IGFic29sdXRlO1xuICAgIHRvcDogMDtcbiAgICByaWdodDogMDtcbiAgICBwb2ludGVyLWV2ZW50czogbm9uZTtcbn1cblxuLnh0ZXJtLWRlY29yYXRpb24tdG9wIHtcbiAgICB6LWluZGV4OiAyO1xuICAgIHBvc2l0aW9uOiByZWxhdGl2ZTtcbn1cbmAsIFwiXCJdKTtcbi8vIEV4cG9ydHNcbmV4cG9ydCBkZWZhdWx0IF9fX0NTU19MT0FERVJfRVhQT1JUX19fO1xuIiwiaW1wb3J0IGFwaSBmcm9tIFwiIS4uLy4uLy4uL3N0eWxlLWxvYWRlci9kaXN0L3J1bnRpbWUvaW5qZWN0U3R5bGVzSW50b1N0eWxlVGFnLmpzXCI7XG4gICAgICAgICAgICBpbXBvcnQgY29udGVudCBmcm9tIFwiISEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4veHRlcm0uY3NzXCI7XG5cbnZhciBvcHRpb25zID0ge307XG5cbm9wdGlvbnMuaW5zZXJ0ID0gXCJoZWFkXCI7XG5vcHRpb25zLnNpbmdsZXRvbiA9IGZhbHNlO1xuXG52YXIgdXBkYXRlID0gYXBpKGNvbnRlbnQsIG9wdGlvbnMpO1xuXG5cblxuZXhwb3J0IGRlZmF1bHQgY29udGVudC5sb2NhbHMgfHwge307IiwiaW1wb3J0IGFwaSBmcm9tIFwiIS4uLy4uLy4uL3N0eWxlLWxvYWRlci9kaXN0L3J1bnRpbWUvaW5qZWN0U3R5bGVzSW50b1N0eWxlVGFnLmpzXCI7XG4gICAgICAgICAgICBpbXBvcnQgY29udGVudCBmcm9tIFwiISEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vYmFzZS5jc3NcIjtcblxudmFyIG9wdGlvbnMgPSB7fTtcblxub3B0aW9ucy5pbnNlcnQgPSBcImhlYWRcIjtcbm9wdGlvbnMuc2luZ2xldG9uID0gZmFsc2U7XG5cbnZhciB1cGRhdGUgPSBhcGkoY29udGVudCwgb3B0aW9ucyk7XG5cblxuXG5leHBvcnQgZGVmYXVsdCBjb250ZW50LmxvY2FscyB8fCB7fTsiLCIvKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxufCBEaXN0cmlidXRlZCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIE1vZGlmaWVkIEJTRCBMaWNlbnNlLlxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKiBUaGlzIGZpbGUgd2FzIGF1dG8tZ2VuZXJhdGVkIGJ5IGVuc3VyZVBhY2thZ2UoKSBpbiBAanVweXRlcmxhYi9idWlsZHV0aWxzICovXG5pbXBvcnQgJ0BsdW1pbm8vd2lkZ2V0cy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BqdXB5dGVybGFiL2FwcHV0aWxzL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQHh0ZXJtL3h0ZXJtL2Nzcy94dGVybS5jc3MnO1xuaW1wb3J0ICcuL2Jhc2UuY3NzJzsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9