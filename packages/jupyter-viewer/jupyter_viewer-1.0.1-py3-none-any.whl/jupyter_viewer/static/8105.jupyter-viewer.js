"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[8105],{

/***/ 5526
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

/*-----------------------------------------------------------------------------
| Main OutputArea
| OutputArea has a list of Outputs
|----------------------------------------------------------------------------*/

.jp-OutputArea {
  overflow-y: auto;
}

.jp-OutputArea-child {
  display: flex;
  flex-direction: row;
  width: 100%;
  overflow: hidden;
}

.jp-OutputPrompt {
  width: var(--jp-cell-prompt-width);
  flex: 0 0 var(--jp-cell-prompt-width);
  color: var(--jp-cell-outprompt-font-color);
  font-family: var(--jp-cell-prompt-font-family);
  padding: var(--jp-code-padding);
  letter-spacing: var(--jp-cell-prompt-letter-spacing);
  line-height: var(--jp-code-line-height);
  font-size: var(--jp-code-font-size);
  border: var(--jp-border-width) solid transparent;
  opacity: var(--jp-cell-prompt-opacity);

  /* Right align prompt text, don't wrap to handle large prompt numbers */
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  /* Disable text selection */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.jp-OutputArea-output {
  width: 100%;
  height: auto;
  overflow: auto;
  user-select: text;
  -moz-user-select: text;
  -webkit-user-select: text;
  -ms-user-select: text;
}

.jp-OutputArea .jp-RenderedText {
  padding-left: 1ch;
}

/**
 * Prompt overlay.
 */

.jp-OutputArea-promptOverlay {
  position: absolute;
  top: 0;
  width: var(--jp-cell-prompt-width);
  height: 100%;
  opacity: 0.5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.jp-OutputArea-promptOverlay .jp-icon-output {
  display: none;
}

.jp-OutputArea-promptOverlay:hover .jp-icon-output {
  display: initial;
}

.jp-OutputArea-promptOverlay:hover {
  background: var(--jp-layout-color2);
  box-shadow: inset 0 0 1px var(--jp-inverse-layout-color0);
}

.jp-OutputArea-child .jp-OutputArea-output {
  flex-grow: 1;
  flex-shrink: 1;
}

/**
 * Isolated output.
 */
.jp-OutputArea-output.jp-mod-isolated {
  width: 100%;
  display: block;
}

/*
When drag events occur, \`lm-mod-override-cursor\` is added to the body.
Because iframes steal all cursor events, the following two rules are necessary
to suppress pointer events while resize drags are occurring. There may be a
better solution to this problem.
*/
body.lm-mod-override-cursor .jp-OutputArea-output.jp-mod-isolated {
  position: relative;
}

body.lm-mod-override-cursor .jp-OutputArea-output.jp-mod-isolated::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
}

/* pre */

.jp-OutputArea-output pre {
  border: none;
  margin: 0;
  padding: 0;
  overflow-x: auto;
  overflow-y: auto;
  word-break: break-all;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* tables */

.jp-OutputArea-output.jp-RenderedHTMLCommon table {
  margin-left: 0;
  margin-right: 0;
}

/* description lists */

.jp-OutputArea-output dl,
.jp-OutputArea-output dt,
.jp-OutputArea-output dd {
  display: block;
}

.jp-OutputArea-output dl {
  width: 100%;
  overflow: hidden;
  padding: 0;
  margin: 0;
}

.jp-OutputArea-output dt {
  font-weight: bold;
  float: left;
  width: 20%;
  padding: 0;
  margin: 0;
}

.jp-OutputArea-output dd {
  float: left;
  width: 80%;
  padding: 0;
  margin: 0;
}

.jp-TrimmedOutputs-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: var(--jp-flat-button-padding);
  margin: 8px 0;
  min-height: var(--jp-flat-button-height);
  font-size: var(--jp-ui-font-size1);
  font-family: var(--jp-ui-font-family);
  background-color: var(--jp-layout-color1);
  border: 1px solid var(--jp-border-color2);
  color: var(--jp-ui-font-color1);
  cursor: pointer;
}

.jp-TrimmedOutputs-button:hover {
  background-color: var(--jp-layout-color2);
  border-color: var(--jp-border-color1);
}

.jp-TrimmedOutputs-button:active {
  background-color: var(--jp-layout-color3);
  border-color: var(--jp-border-color1);
}

.jp-TrimmedOutputs-button:focus-visible {
  outline: 1px solid var(--jp-brand-color1);
  outline-offset: -1px;
}

/* Hide the gutter in case of
 *  - nested output areas (e.g. in the case of output widgets)
 *  - mirrored output areas
 */
.jp-OutputArea .jp-OutputArea .jp-OutputArea-prompt {
  display: none;
}

/* Hide empty lines in the output area, for instance due to cleared widgets */
.jp-OutputArea-prompt:empty {
  padding: 0;
  border: 0;
}

/*-----------------------------------------------------------------------------
| executeResult is added to any Output-result for the display of the object
| returned by a cell
|----------------------------------------------------------------------------*/

.jp-OutputArea-output.jp-OutputArea-executeResult {
  margin-left: 0;
  width: 100%;
  flex: 1 1 auto;
}

/* Text output with the Out[] prompt needs a top padding to match the
 * alignment of the Out[] prompt itself.
 */
.jp-OutputArea-executeResult .jp-RenderedText.jp-OutputArea-output {
  padding-top: var(--jp-code-padding);
  border-top: var(--jp-border-width) solid transparent;
}

/*-----------------------------------------------------------------------------
| The Stdin output
|----------------------------------------------------------------------------*/

.jp-Stdin-prompt {
  color: var(--jp-content-font-color0);
  padding-right: var(--jp-code-padding);
  vertical-align: baseline;
  flex: 0 0 auto;
}

.jp-Stdin-input {
  font-family: var(--jp-code-font-family);
  font-size: inherit;
  color: inherit;
  background-color: inherit;
  width: 42%;
  min-width: 200px;

  /* make sure input baseline aligns with prompt */
  vertical-align: baseline;

  /* padding + margin = 0.5em between prompt and cursor */
  padding: 0 0.25em;
  margin: 0 0.25em;
  flex: 0 0 70%;
}

.jp-Stdin-input::placeholder {
  opacity: 0;
}

.jp-Stdin-input:focus {
  box-shadow: none;
}

.jp-Stdin-input:focus::placeholder {
  opacity: 1;
}

.jp-OutputArea-stdin-hiding {
  /* soft-hide the output, preserving focus */
  opacity: 0;
  height: 0;
}

/*-----------------------------------------------------------------------------
| Output Area View
|----------------------------------------------------------------------------*/

.jp-LinkedOutputView .jp-OutputArea {
  height: 100%;
  display: block;
}

.jp-LinkedOutputView .jp-OutputArea-child:only-child {
  height: 100%;
}

.jp-LinkedOutputView .jp-OutputArea-output:only-child {
  height: 100%;
}

/*-----------------------------------------------------------------------------
| Printing
|----------------------------------------------------------------------------*/

@media print {
  .jp-OutputArea-child {
    display: table;
    table-layout: fixed;
    break-inside: avoid-page;
  }

  .jp-OutputArea-prompt {
    display: table-cell;
    vertical-align: top;
  }

  .jp-OutputArea-output {
    display: table-cell;
  }
}

/*-----------------------------------------------------------------------------
| Mobile
|----------------------------------------------------------------------------*/
@media only screen and (width <= 760px) {
  .jp-OutputArea-child {
    flex-direction: column;
  }

  .jp-OutputPrompt {
    flex: 0 0 auto;
    text-align: left;
  }

  .jp-OutputArea-promptOverlay {
    display: none;
  }
}

/* Trimmed outputs container */
.jp-TrimmedOutputs {
  /* Left-align the button within the output area */
  text-align: left;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 11152
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

/*-----------------------------------------------------------------------------
| Placeholder
|----------------------------------------------------------------------------*/

.jp-Placeholder {
  display: flex;
  flex-direction: row;
  width: 100%;
}

.jp-Placeholder-prompt {
  flex: 0 0 var(--jp-cell-prompt-width);
  box-sizing: border-box;
}

.jp-Placeholder-content {
  flex: 1 1 auto;
  padding: 4px 6px;
  border: 1px solid transparent;
  border-radius: 0;
  background: none;
  box-sizing: border-box;
  cursor: pointer;
}

.jp-Placeholder-contentContainer {
  display: flex;
}

.jp-Placeholder-content:hover,
.jp-InputPlaceholder > .jp-Placeholder-content:hover {
  border-color: var(--jp-layout-color3);
}

.jp-Placeholder-content .jp-MoreHorizIcon {
  width: 32px;
  height: 16px;
  border: 1px solid transparent;
  border-radius: var(--jp-border-radius);
}

.jp-Placeholder-content .jp-MoreHorizIcon:hover {
  border: 1px solid var(--jp-border-color1);
  box-shadow: var(--jp-toolbar-box-shadow);
  background-color: var(--jp-layout-color0);
}

.jp-PlaceholderText {
  white-space: nowrap;
  overflow-x: hidden;
  color: var(--jp-inverse-layout-color3);
  font-family: var(--jp-code-font-family);
}

.jp-InputPlaceholder > .jp-Placeholder-content {
  border-color: var(--jp-cell-editor-border-color);
  background: var(--jp-cell-editor-background);
}

/*-----------------------------------------------------------------------------
| Print
|----------------------------------------------------------------------------*/
@media print {
  .jp-Placeholder {
    display: table;
    table-layout: fixed;
  }

  .jp-Placeholder-content {
    display: table-cell;
  }

  .jp-Placeholder-prompt {
    display: table-cell;
  }
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 25147
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

/*-----------------------------------------------------------------------------
| Input
|----------------------------------------------------------------------------*/

/* All input areas */
.jp-InputArea {
  display: flex;
  flex-direction: row;
  width: 100%;
  overflow: hidden;
}

.jp-InputArea-editor {
  flex: 1 1 auto;
  overflow: hidden;

  /* This is the non-active, default styling */
  border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);
  border-radius: 0;
  background: var(--jp-cell-editor-background);
}

.jp-InputPrompt {
  flex: 0 0 var(--jp-cell-prompt-width);
  width: var(--jp-cell-prompt-width);
  color: var(--jp-cell-inprompt-font-color);
  font-family: var(--jp-cell-prompt-font-family);
  padding: var(--jp-code-padding);
  letter-spacing: var(--jp-cell-prompt-letter-spacing);
  opacity: var(--jp-cell-prompt-opacity);
  line-height: var(--jp-code-line-height);
  font-size: var(--jp-code-font-size);
  border: var(--jp-border-width) solid transparent;

  /* Right align prompt text, don't wrap to handle large prompt numbers */
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  /* Disable text selection */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/*-----------------------------------------------------------------------------
| Print
|----------------------------------------------------------------------------*/
@media print {
  .jp-InputArea {
    display: table;
    table-layout: fixed;
  }

  .jp-InputArea-editor {
    display: table-cell;
    vertical-align: top;
  }

  .jp-InputPrompt {
    display: table-cell;
    vertical-align: top;
  }
}

/*-----------------------------------------------------------------------------
| Mobile
|----------------------------------------------------------------------------*/
@media only screen and (width <= 760px) {
  .jp-InputArea {
    flex-direction: column;
  }

  .jp-InputArea-editor {
    margin-left: var(--jp-code-padding);
  }

  .jp-InputPrompt {
    flex: 0 0 auto;
    text-align: left;
  }
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 30684
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

/*-----------------------------------------------------------------------------
| Header/Footer
|----------------------------------------------------------------------------*/

/* Hidden by zero height by default */
.jp-CellHeader,
.jp-CellFooter {
  height: 0;
  width: 100%;
  padding: 0;
  margin: 0;
  border: none;
  outline: none;
  background: transparent;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 35541
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

.jp-Collapser {
  flex: 0 0 var(--jp-cell-collapser-width);
  padding: 0;
  margin: 0;
  border: none;
  outline: none;
  background: transparent;
  border-radius: var(--jp-border-radius);
  opacity: 1;
}

.jp-Collapser-child {
  display: block;
  width: 100%;
  box-sizing: border-box;

  /* height: 100% doesn't work because the height of its parent is computed from content */
  position: absolute;
  top: 0;
  bottom: 0;
}

/*-----------------------------------------------------------------------------
| Printing
|----------------------------------------------------------------------------*/

/*
Hiding collapsers in print mode.

Note: input and output wrappers have "display: block" property in print mode.
*/

@media print {
  .jp-Collapser {
    display: none;
  }
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 50200
(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {


// EXTERNAL MODULE: ./node_modules/@lumino/widgets/style/index.js + 1 modules
var style = __webpack_require__(47214);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/ui-components/style/index.js + 1 modules
var ui_components_style = __webpack_require__(23893);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/apputils/style/index.js + 1 modules
var apputils_style = __webpack_require__(84940);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/rendermime/style/index.js + 1 modules
var rendermime_style = __webpack_require__(29448);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/docregistry/style/index.js + 1 modules
var docregistry_style = __webpack_require__(66954);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js
var injectStylesIntoStyleTag = __webpack_require__(85072);
var injectStylesIntoStyleTag_default = /*#__PURE__*/__webpack_require__.n(injectStylesIntoStyleTag);
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/@jupyterlab/toc/style/base.css
var base = __webpack_require__(75682);
;// ./node_modules/@jupyterlab/toc/style/base.css

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = injectStylesIntoStyleTag_default()(base/* default */.A, options);



/* harmony default export */ const style_base = (base/* default */.A.locals || {});
;// ./node_modules/@jupyterlab/toc/style/index.js
/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/* This file was auto-generated by ensurePackage() in @jupyterlab/buildutils */







/***/ },

/***/ 51208
(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {


// EXTERNAL MODULE: ./node_modules/@lumino/widgets/style/index.js + 1 modules
var style = __webpack_require__(47214);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/apputils/style/index.js + 1 modules
var apputils_style = __webpack_require__(84940);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/rendermime/style/index.js + 1 modules
var rendermime_style = __webpack_require__(29448);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js
var injectStylesIntoStyleTag = __webpack_require__(85072);
var injectStylesIntoStyleTag_default = /*#__PURE__*/__webpack_require__.n(injectStylesIntoStyleTag);
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/@jupyterlab/outputarea/style/base.css
var base = __webpack_require__(5526);
;// ./node_modules/@jupyterlab/outputarea/style/base.css

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = injectStylesIntoStyleTag_default()(base/* default */.A, options);



/* harmony default export */ const style_base = (base/* default */.A.locals || {});
;// ./node_modules/@jupyterlab/outputarea/style/index.js
/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/* This file was auto-generated by ensurePackage() in @jupyterlab/buildutils */





/***/ },

/***/ 55717
(module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   A: () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(74608);
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(87249);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _css_loader_dist_cjs_js_collapser_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(35541);
/* harmony import */ var _css_loader_dist_cjs_js_headerfooter_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(30684);
/* harmony import */ var _css_loader_dist_cjs_js_inputarea_css__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(25147);
/* harmony import */ var _css_loader_dist_cjs_js_placeholder_css__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(11152);
/* harmony import */ var _css_loader_dist_cjs_js_widget_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(60846);
// Imports







var ___CSS_LOADER_EXPORT___ = _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_collapser_css__WEBPACK_IMPORTED_MODULE_2__/* ["default"] */ .A);
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_headerfooter_css__WEBPACK_IMPORTED_MODULE_3__/* ["default"] */ .A);
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_inputarea_css__WEBPACK_IMPORTED_MODULE_4__/* ["default"] */ .A);
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_placeholder_css__WEBPACK_IMPORTED_MODULE_5__/* ["default"] */ .A);
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_widget_css__WEBPACK_IMPORTED_MODULE_6__/* ["default"] */ .A);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 60846
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

/*-----------------------------------------------------------------------------
| Private CSS variables
|----------------------------------------------------------------------------*/

:root {
  --jp-private-cell-scrolling-output-offset: 5px;
}

/*-----------------------------------------------------------------------------
| Cell
|----------------------------------------------------------------------------*/

.jp-Cell {
  padding: var(--jp-cell-padding);
  margin: 0;
  border: none;
  outline: none;
  background: transparent;
}

/*-----------------------------------------------------------------------------
| Common input/output
|----------------------------------------------------------------------------*/

.jp-Cell-inputWrapper,
.jp-Cell-outputWrapper {
  display: flex;
  flex-direction: row;
  padding: 0;
  margin: 0;

  /* Added to reveal the box-shadow on the input and output collapsers. */
  overflow: visible;
}

/* Only input/output areas inside cells */
.jp-Cell-inputArea,
.jp-Cell-outputArea {
  flex: 1 1 auto;
}

/*-----------------------------------------------------------------------------
| Collapser
|----------------------------------------------------------------------------*/

/* Make the output collapser disappear when there is not output, but do so
 * in a manner that leaves it in the layout and preserves its width.
 */
.jp-Cell.jp-mod-noOutputs .jp-Cell-outputCollapser {
  border: none !important;
  background: transparent !important;
}

.jp-Cell:not(.jp-mod-noOutputs) .jp-Cell-outputCollapser {
  min-height: var(--jp-cell-collapser-min-height);
}

/*-----------------------------------------------------------------------------
| Output
|----------------------------------------------------------------------------*/

/* Put a space between input and output when there IS output */
.jp-Cell:not(.jp-mod-noOutputs) .jp-Cell-outputWrapper {
  margin-top: 5px;
}

.jp-CodeCell.jp-mod-outputsScrolled .jp-Cell-outputArea {
  overflow-y: auto;
  max-height: 24em;
  margin-left: var(--jp-private-cell-scrolling-output-offset);
  resize: vertical;
}

.jp-CodeCell.jp-mod-outputsScrolled .jp-Cell-outputArea[style*='height'] {
  max-height: unset;
}

.jp-CodeCell.jp-mod-outputsScrolled .jp-Cell-outputArea::after {
  content: ' ';
  box-shadow: inset 0 0 6px 2px rgb(0 0 0 / 30%);
  width: 100%;
  height: 100%;
  position: sticky;
  bottom: 0;
  top: 0;
  margin-top: -50%;
  float: left;
  display: block;
  pointer-events: none;
}

.jp-CodeCell.jp-mod-outputsScrolled .jp-OutputArea-child {
  padding-top: 6px;
}

.jp-CodeCell.jp-mod-outputsScrolled .jp-OutputArea-prompt {
  width: calc(
    var(--jp-cell-prompt-width) - var(--jp-private-cell-scrolling-output-offset)
  );
  flex: 0 0
    calc(
      var(--jp-cell-prompt-width) -
        var(--jp-private-cell-scrolling-output-offset)
    );
}

.jp-CodeCell.jp-mod-outputsScrolled .jp-OutputArea-promptOverlay {
  left: calc(-1 * var(--jp-private-cell-scrolling-output-offset));
}

/*-----------------------------------------------------------------------------
| CodeCell
|----------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
| MarkdownCell
|----------------------------------------------------------------------------*/

.jp-MarkdownOutput {
  flex: 1 1 auto;
  width: 100%;
  margin-top: 0;
  margin-bottom: 0;
  padding-left: var(--jp-code-padding);
}

.jp-MarkdownOutput.jp-RenderedHTMLCommon {
  overflow: auto;
}

/* collapseHeadingButton (show always if hiddenCellsButton is _not_ shown) */
.jp-collapseHeadingButton {
  display: flex;
  min-height: var(--jp-cell-collapser-min-height);
  font-size: var(--jp-code-font-size);
  position: absolute;
  background-color: transparent;
  background-size: 25px;
  background-repeat: no-repeat;
  background-position-x: center;
  background-position-y: top;
  background-image: var(--jp-icon-caret-down);
  right: 0;
  top: 0;
  bottom: 0;
}

.jp-collapseHeadingButton.jp-mod-collapsed {
  background-image: var(--jp-icon-caret-right);
}

/*
 set the container font size to match that of content
 so that the nested collapse buttons have the right size
*/
.jp-MarkdownCell .jp-InputPrompt {
  font-size: var(--jp-content-font-size1);
}

/*
  Align collapseHeadingButton with cell top header
  The font sizes are identical to the ones in packages/rendermime/style/base.css
*/
.jp-mod-rendered .jp-collapseHeadingButton[data-heading-level='1'] {
  font-size: var(--jp-content-font-size5);
  background-position-y: calc(0.3 * var(--jp-content-font-size5));
}

.jp-mod-rendered .jp-collapseHeadingButton[data-heading-level='2'] {
  font-size: var(--jp-content-font-size4);
  background-position-y: calc(0.3 * var(--jp-content-font-size4));
}

.jp-mod-rendered .jp-collapseHeadingButton[data-heading-level='3'] {
  font-size: var(--jp-content-font-size3);
  background-position-y: calc(0.3 * var(--jp-content-font-size3));
}

.jp-mod-rendered .jp-collapseHeadingButton[data-heading-level='4'] {
  font-size: var(--jp-content-font-size2);
  background-position-y: calc(0.3 * var(--jp-content-font-size2));
}

.jp-mod-rendered .jp-collapseHeadingButton[data-heading-level='5'] {
  font-size: var(--jp-content-font-size1);
  background-position-y: top;
}

.jp-mod-rendered .jp-collapseHeadingButton[data-heading-level='6'] {
  font-size: var(--jp-content-font-size0);
  background-position-y: top;
}

/* collapseHeadingButton (show only on (hover,active) if hiddenCellsButton is shown) */
.jp-Notebook.jp-mod-showHiddenCellsButton .jp-collapseHeadingButton {
  display: none;
}

.jp-Notebook.jp-mod-showHiddenCellsButton
  :is(.jp-MarkdownCell:hover, .jp-mod-active)
  .jp-collapseHeadingButton {
  display: flex;
}

/* showHiddenCellsButton (only show if jp-mod-showHiddenCellsButton is set, which
is a consequence of the showHiddenCellsButton option in Notebook Settings)*/
.jp-Notebook.jp-mod-showHiddenCellsButton .jp-showHiddenCellsButton {
  margin-left: calc(var(--jp-cell-prompt-width) + 2 * var(--jp-code-padding));
  margin-top: var(--jp-code-padding);
  border: 1px solid var(--jp-border-color2);
  background-color: var(--jp-border-color3) !important;
  color: var(--jp-content-font-color0) !important;
  display: flex;
}

.jp-Notebook.jp-mod-showHiddenCellsButton .jp-showHiddenCellsButton:hover {
  background-color: var(--jp-border-color2) !important;
}

.jp-showHiddenCellsButton {
  display: none;
}

/*-----------------------------------------------------------------------------
| Printing
|----------------------------------------------------------------------------*/

/*
Using block instead of flex to allow the use of the break-inside CSS property for
cell outputs.
*/

@media print {
  .jp-Cell-inputWrapper,
  .jp-Cell-outputWrapper {
    display: block;
  }

  .jp-MarkdownOutput {
    display: table-cell;
  }
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 68105
(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {


// EXTERNAL MODULE: ./node_modules/@lumino/widgets/style/index.js + 1 modules
var style = __webpack_require__(47214);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/ui-components/style/index.js + 1 modules
var ui_components_style = __webpack_require__(23893);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/apputils/style/index.js + 1 modules
var apputils_style = __webpack_require__(84940);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/rendermime/style/index.js + 1 modules
var rendermime_style = __webpack_require__(29448);
;// ./node_modules/@jupyterlab/attachments/style/index.js
/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/* This file was auto-generated by ensurePackage() in @jupyterlab/buildutils */

// EXTERNAL MODULE: ./node_modules/@lumino/dragdrop/style/index.js + 1 modules
var dragdrop_style = __webpack_require__(17094);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/codeeditor/style/index.js + 1 modules
var codeeditor_style = __webpack_require__(5792);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/documentsearch/style/index.js + 1 modules
var documentsearch_style = __webpack_require__(47003);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/codemirror/style/index.js + 1 modules
var codemirror_style = __webpack_require__(97366);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/filebrowser/style/index.js + 2 modules
var filebrowser_style = __webpack_require__(18347);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/outputarea/style/index.js + 1 modules
var outputarea_style = __webpack_require__(51208);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/toc/style/index.js + 1 modules
var toc_style = __webpack_require__(50200);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js
var injectStylesIntoStyleTag = __webpack_require__(85072);
var injectStylesIntoStyleTag_default = /*#__PURE__*/__webpack_require__.n(injectStylesIntoStyleTag);
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/@jupyterlab/cells/style/base.css
var base = __webpack_require__(55717);
;// ./node_modules/@jupyterlab/cells/style/base.css

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = injectStylesIntoStyleTag_default()(base/* default */.A, options);



/* harmony default export */ const style_base = (base/* default */.A.locals || {});
;// ./node_modules/@jupyterlab/cells/style/index.js
/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/* This file was auto-generated by ensurePackage() in @jupyterlab/buildutils */














/***/ },

/***/ 75682
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

/*-----------------------------------------------------------------------------
| Table of Contents
|----------------------------------------------------------------------------*/

.jp-TableOfContents {
  display: flex;
  flex-direction: column;
  background: var(--jp-layout-color1);
  color: var(--jp-ui-font-color1);
  font-size: var(--jp-ui-font-size1);
  height: 100%;
}

.jp-TableOfContents-placeholder {
  text-align: center;
}

.jp-TableOfContents-placeholderContent {
  color: var(--jp-content-font-color2);
  padding: 8px;
}

.jp-TableOfContents-placeholderContent > h3 {
  margin-bottom: var(--jp-content-heading-margin-bottom);
}

.jp-TableOfContents .jp-SidePanel-content {
  overflow-y: auto;
}

.jp-TableOfContents-tree {
  margin: 4px;
}

.jp-TableOfContents-content {
  padding: 0;
  background-color: var(--jp-layout-color1);
}

.jp-tocItem {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.jp-tocItem-heading {
  display: flex;
  cursor: pointer;
  width: 100%;
}

.jp-tocItem-content {
  display: block;
  padding: 4px 0;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow-x: hidden;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiODEwNS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7Ozs7Ozs7Ozs7O0FDN1ZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7OztBQ3hGQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7Ozs7Ozs7Ozs7O0FDaEdBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7Ozs7Ozs7QUMzQkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQ2pEQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNWQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDUkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7OztBQ3JCQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQzlQQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7QUNMQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7OztBQ2pCQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL291dHB1dGFyZWEvc3R5bGUvYmFzZS5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9jZWxscy9zdHlsZS9wbGFjZWhvbGRlci5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9jZWxscy9zdHlsZS9pbnB1dGFyZWEuY3NzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGp1cHl0ZXJsYWIvY2VsbHMvc3R5bGUvaGVhZGVyZm9vdGVyLmNzcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL2NlbGxzL3N0eWxlL2NvbGxhcHNlci5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi90b2Mvc3R5bGUvYmFzZS5jc3M/ZWZlNCIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL3RvYy9zdHlsZS9pbmRleC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL291dHB1dGFyZWEvc3R5bGUvYmFzZS5jc3M/Y2M0NyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL291dHB1dGFyZWEvc3R5bGUvaW5kZXguanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9jZWxscy9zdHlsZS9iYXNlLmNzcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL2NlbGxzL3N0eWxlL3dpZGdldC5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9hdHRhY2htZW50cy9zdHlsZS9pbmRleC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL2NlbGxzL3N0eWxlL2Jhc2UuY3NzPzQzNzEiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9jZWxscy9zdHlsZS9pbmRleC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL3RvYy9zdHlsZS9iYXNlLmNzcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBJbXBvcnRzXG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvbm9Tb3VyY2VNYXBzLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9hcGkuanNcIjtcbnZhciBfX19DU1NfTE9BREVSX0VYUE9SVF9fXyA9IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fKTtcbi8vIE1vZHVsZVxuX19fQ1NTX0xPQURFUl9FWFBPUlRfX18ucHVzaChbbW9kdWxlLmlkLCBgLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb3B5cmlnaHQgKGMpIEp1cHl0ZXIgRGV2ZWxvcG1lbnQgVGVhbS5cbnwgRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBNYWluIE91dHB1dEFyZWFcbnwgT3V0cHV0QXJlYSBoYXMgYSBsaXN0IG9mIE91dHB1dHNcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLU91dHB1dEFyZWEge1xuICBvdmVyZmxvdy15OiBhdXRvO1xufVxuXG4uanAtT3V0cHV0QXJlYS1jaGlsZCB7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGZsZXgtZGlyZWN0aW9uOiByb3c7XG4gIHdpZHRoOiAxMDAlO1xuICBvdmVyZmxvdzogaGlkZGVuO1xufVxuXG4uanAtT3V0cHV0UHJvbXB0IHtcbiAgd2lkdGg6IHZhcigtLWpwLWNlbGwtcHJvbXB0LXdpZHRoKTtcbiAgZmxleDogMCAwIHZhcigtLWpwLWNlbGwtcHJvbXB0LXdpZHRoKTtcbiAgY29sb3I6IHZhcigtLWpwLWNlbGwtb3V0cHJvbXB0LWZvbnQtY29sb3IpO1xuICBmb250LWZhbWlseTogdmFyKC0tanAtY2VsbC1wcm9tcHQtZm9udC1mYW1pbHkpO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1jb2RlLXBhZGRpbmcpO1xuICBsZXR0ZXItc3BhY2luZzogdmFyKC0tanAtY2VsbC1wcm9tcHQtbGV0dGVyLXNwYWNpbmcpO1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtY29kZS1saW5lLWhlaWdodCk7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29kZS1mb250LXNpemUpO1xuICBib3JkZXI6IHZhcigtLWpwLWJvcmRlci13aWR0aCkgc29saWQgdHJhbnNwYXJlbnQ7XG4gIG9wYWNpdHk6IHZhcigtLWpwLWNlbGwtcHJvbXB0LW9wYWNpdHkpO1xuXG4gIC8qIFJpZ2h0IGFsaWduIHByb21wdCB0ZXh0LCBkb24ndCB3cmFwIHRvIGhhbmRsZSBsYXJnZSBwcm9tcHQgbnVtYmVycyAqL1xuICB0ZXh0LWFsaWduOiByaWdodDtcbiAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgdGV4dC1vdmVyZmxvdzogZWxsaXBzaXM7XG5cbiAgLyogRGlzYWJsZSB0ZXh0IHNlbGVjdGlvbiAqL1xuICAtd2Via2l0LXVzZXItc2VsZWN0OiBub25lO1xuICAtbW96LXVzZXItc2VsZWN0OiBub25lO1xuICAtbXMtdXNlci1zZWxlY3Q6IG5vbmU7XG4gIHVzZXItc2VsZWN0OiBub25lO1xufVxuXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQge1xuICB3aWR0aDogMTAwJTtcbiAgaGVpZ2h0OiBhdXRvO1xuICBvdmVyZmxvdzogYXV0bztcbiAgdXNlci1zZWxlY3Q6IHRleHQ7XG4gIC1tb3otdXNlci1zZWxlY3Q6IHRleHQ7XG4gIC13ZWJraXQtdXNlci1zZWxlY3Q6IHRleHQ7XG4gIC1tcy11c2VyLXNlbGVjdDogdGV4dDtcbn1cblxuLmpwLU91dHB1dEFyZWEgLmpwLVJlbmRlcmVkVGV4dCB7XG4gIHBhZGRpbmctbGVmdDogMWNoO1xufVxuXG4vKipcbiAqIFByb21wdCBvdmVybGF5LlxuICovXG5cbi5qcC1PdXRwdXRBcmVhLXByb21wdE92ZXJsYXkge1xuICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gIHRvcDogMDtcbiAgd2lkdGg6IHZhcigtLWpwLWNlbGwtcHJvbXB0LXdpZHRoKTtcbiAgaGVpZ2h0OiAxMDAlO1xuICBvcGFjaXR5OiAwLjU7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGFsaWduLWl0ZW1zOiBjZW50ZXI7XG4gIGp1c3RpZnktY29udGVudDogY2VudGVyO1xufVxuXG4uanAtT3V0cHV0QXJlYS1wcm9tcHRPdmVybGF5IC5qcC1pY29uLW91dHB1dCB7XG4gIGRpc3BsYXk6IG5vbmU7XG59XG5cbi5qcC1PdXRwdXRBcmVhLXByb21wdE92ZXJsYXk6aG92ZXIgLmpwLWljb24tb3V0cHV0IHtcbiAgZGlzcGxheTogaW5pdGlhbDtcbn1cblxuLmpwLU91dHB1dEFyZWEtcHJvbXB0T3ZlcmxheTpob3ZlciB7XG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjIpO1xuICBib3gtc2hhZG93OiBpbnNldCAwIDAgMXB4IHZhcigtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yMCk7XG59XG5cbi5qcC1PdXRwdXRBcmVhLWNoaWxkIC5qcC1PdXRwdXRBcmVhLW91dHB1dCB7XG4gIGZsZXgtZ3JvdzogMTtcbiAgZmxleC1zaHJpbms6IDE7XG59XG5cbi8qKlxuICogSXNvbGF0ZWQgb3V0cHV0LlxuICovXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQuanAtbW9kLWlzb2xhdGVkIHtcbiAgd2lkdGg6IDEwMCU7XG4gIGRpc3BsYXk6IGJsb2NrO1xufVxuXG4vKlxuV2hlbiBkcmFnIGV2ZW50cyBvY2N1ciwgXFxgbG0tbW9kLW92ZXJyaWRlLWN1cnNvclxcYCBpcyBhZGRlZCB0byB0aGUgYm9keS5cbkJlY2F1c2UgaWZyYW1lcyBzdGVhbCBhbGwgY3Vyc29yIGV2ZW50cywgdGhlIGZvbGxvd2luZyB0d28gcnVsZXMgYXJlIG5lY2Vzc2FyeVxudG8gc3VwcHJlc3MgcG9pbnRlciBldmVudHMgd2hpbGUgcmVzaXplIGRyYWdzIGFyZSBvY2N1cnJpbmcuIFRoZXJlIG1heSBiZSBhXG5iZXR0ZXIgc29sdXRpb24gdG8gdGhpcyBwcm9ibGVtLlxuKi9cbmJvZHkubG0tbW9kLW92ZXJyaWRlLWN1cnNvciAuanAtT3V0cHV0QXJlYS1vdXRwdXQuanAtbW9kLWlzb2xhdGVkIHtcbiAgcG9zaXRpb246IHJlbGF0aXZlO1xufVxuXG5ib2R5LmxtLW1vZC1vdmVycmlkZS1jdXJzb3IgLmpwLU91dHB1dEFyZWEtb3V0cHV0LmpwLW1vZC1pc29sYXRlZDo6YmVmb3JlIHtcbiAgY29udGVudDogJyc7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgdG9wOiAwO1xuICBsZWZ0OiAwO1xuICByaWdodDogMDtcbiAgYm90dG9tOiAwO1xuICBiYWNrZ3JvdW5kOiB0cmFuc3BhcmVudDtcbn1cblxuLyogcHJlICovXG5cbi5qcC1PdXRwdXRBcmVhLW91dHB1dCBwcmUge1xuICBib3JkZXI6IG5vbmU7XG4gIG1hcmdpbjogMDtcbiAgcGFkZGluZzogMDtcbiAgb3ZlcmZsb3cteDogYXV0bztcbiAgb3ZlcmZsb3cteTogYXV0bztcbiAgd29yZC1icmVhazogYnJlYWstYWxsO1xuICB3b3JkLXdyYXA6IGJyZWFrLXdvcmQ7XG4gIHdoaXRlLXNwYWNlOiBwcmUtd3JhcDtcbn1cblxuLyogdGFibGVzICovXG5cbi5qcC1PdXRwdXRBcmVhLW91dHB1dC5qcC1SZW5kZXJlZEhUTUxDb21tb24gdGFibGUge1xuICBtYXJnaW4tbGVmdDogMDtcbiAgbWFyZ2luLXJpZ2h0OiAwO1xufVxuXG4vKiBkZXNjcmlwdGlvbiBsaXN0cyAqL1xuXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQgZGwsXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQgZHQsXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQgZGQge1xuICBkaXNwbGF5OiBibG9jaztcbn1cblxuLmpwLU91dHB1dEFyZWEtb3V0cHV0IGRsIHtcbiAgd2lkdGg6IDEwMCU7XG4gIG92ZXJmbG93OiBoaWRkZW47XG4gIHBhZGRpbmc6IDA7XG4gIG1hcmdpbjogMDtcbn1cblxuLmpwLU91dHB1dEFyZWEtb3V0cHV0IGR0IHtcbiAgZm9udC13ZWlnaHQ6IGJvbGQ7XG4gIGZsb2F0OiBsZWZ0O1xuICB3aWR0aDogMjAlO1xuICBwYWRkaW5nOiAwO1xuICBtYXJnaW46IDA7XG59XG5cbi5qcC1PdXRwdXRBcmVhLW91dHB1dCBkZCB7XG4gIGZsb2F0OiBsZWZ0O1xuICB3aWR0aDogODAlO1xuICBwYWRkaW5nOiAwO1xuICBtYXJnaW46IDA7XG59XG5cbi5qcC1UcmltbWVkT3V0cHV0cy1idXR0b24ge1xuICBkaXNwbGF5OiBpbmxpbmUtZmxleDtcbiAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAganVzdGlmeS1jb250ZW50OiBjZW50ZXI7XG4gIHdpZHRoOiAxMDAlO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1mbGF0LWJ1dHRvbi1wYWRkaW5nKTtcbiAgbWFyZ2luOiA4cHggMDtcbiAgbWluLWhlaWdodDogdmFyKC0tanAtZmxhdC1idXR0b24taGVpZ2h0KTtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC11aS1mb250LXNpemUxKTtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLXVpLWZvbnQtZmFtaWx5KTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMSk7XG4gIGJvcmRlcjogMXB4IHNvbGlkIHZhcigtLWpwLWJvcmRlci1jb2xvcjIpO1xuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjEpO1xuICBjdXJzb3I6IHBvaW50ZXI7XG59XG5cbi5qcC1UcmltbWVkT3V0cHV0cy1idXR0b246aG92ZXIge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IyKTtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1ib3JkZXItY29sb3IxKTtcbn1cblxuLmpwLVRyaW1tZWRPdXRwdXRzLWJ1dHRvbjphY3RpdmUge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IzKTtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1ib3JkZXItY29sb3IxKTtcbn1cblxuLmpwLVRyaW1tZWRPdXRwdXRzLWJ1dHRvbjpmb2N1cy12aXNpYmxlIHtcbiAgb3V0bGluZTogMXB4IHNvbGlkIHZhcigtLWpwLWJyYW5kLWNvbG9yMSk7XG4gIG91dGxpbmUtb2Zmc2V0OiAtMXB4O1xufVxuXG4vKiBIaWRlIHRoZSBndXR0ZXIgaW4gY2FzZSBvZlxuICogIC0gbmVzdGVkIG91dHB1dCBhcmVhcyAoZS5nLiBpbiB0aGUgY2FzZSBvZiBvdXRwdXQgd2lkZ2V0cylcbiAqICAtIG1pcnJvcmVkIG91dHB1dCBhcmVhc1xuICovXG4uanAtT3V0cHV0QXJlYSAuanAtT3V0cHV0QXJlYSAuanAtT3V0cHV0QXJlYS1wcm9tcHQge1xuICBkaXNwbGF5OiBub25lO1xufVxuXG4vKiBIaWRlIGVtcHR5IGxpbmVzIGluIHRoZSBvdXRwdXQgYXJlYSwgZm9yIGluc3RhbmNlIGR1ZSB0byBjbGVhcmVkIHdpZGdldHMgKi9cbi5qcC1PdXRwdXRBcmVhLXByb21wdDplbXB0eSB7XG4gIHBhZGRpbmc6IDA7XG4gIGJvcmRlcjogMDtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBleGVjdXRlUmVzdWx0IGlzIGFkZGVkIHRvIGFueSBPdXRwdXQtcmVzdWx0IGZvciB0aGUgZGlzcGxheSBvZiB0aGUgb2JqZWN0XG58IHJldHVybmVkIGJ5IGEgY2VsbFxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQuanAtT3V0cHV0QXJlYS1leGVjdXRlUmVzdWx0IHtcbiAgbWFyZ2luLWxlZnQ6IDA7XG4gIHdpZHRoOiAxMDAlO1xuICBmbGV4OiAxIDEgYXV0bztcbn1cblxuLyogVGV4dCBvdXRwdXQgd2l0aCB0aGUgT3V0W10gcHJvbXB0IG5lZWRzIGEgdG9wIHBhZGRpbmcgdG8gbWF0Y2ggdGhlXG4gKiBhbGlnbm1lbnQgb2YgdGhlIE91dFtdIHByb21wdCBpdHNlbGYuXG4gKi9cbi5qcC1PdXRwdXRBcmVhLWV4ZWN1dGVSZXN1bHQgLmpwLVJlbmRlcmVkVGV4dC5qcC1PdXRwdXRBcmVhLW91dHB1dCB7XG4gIHBhZGRpbmctdG9wOiB2YXIoLS1qcC1jb2RlLXBhZGRpbmcpO1xuICBib3JkZXItdG9wOiB2YXIoLS1qcC1ib3JkZXItd2lkdGgpIHNvbGlkIHRyYW5zcGFyZW50O1xufVxuXG4vKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IFRoZSBTdGRpbiBvdXRwdXRcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLVN0ZGluLXByb21wdCB7XG4gIGNvbG9yOiB2YXIoLS1qcC1jb250ZW50LWZvbnQtY29sb3IwKTtcbiAgcGFkZGluZy1yaWdodDogdmFyKC0tanAtY29kZS1wYWRkaW5nKTtcbiAgdmVydGljYWwtYWxpZ246IGJhc2VsaW5lO1xuICBmbGV4OiAwIDAgYXV0bztcbn1cblxuLmpwLVN0ZGluLWlucHV0IHtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLWNvZGUtZm9udC1mYW1pbHkpO1xuICBmb250LXNpemU6IGluaGVyaXQ7XG4gIGNvbG9yOiBpbmhlcml0O1xuICBiYWNrZ3JvdW5kLWNvbG9yOiBpbmhlcml0O1xuICB3aWR0aDogNDIlO1xuICBtaW4td2lkdGg6IDIwMHB4O1xuXG4gIC8qIG1ha2Ugc3VyZSBpbnB1dCBiYXNlbGluZSBhbGlnbnMgd2l0aCBwcm9tcHQgKi9cbiAgdmVydGljYWwtYWxpZ246IGJhc2VsaW5lO1xuXG4gIC8qIHBhZGRpbmcgKyBtYXJnaW4gPSAwLjVlbSBiZXR3ZWVuIHByb21wdCBhbmQgY3Vyc29yICovXG4gIHBhZGRpbmc6IDAgMC4yNWVtO1xuICBtYXJnaW46IDAgMC4yNWVtO1xuICBmbGV4OiAwIDAgNzAlO1xufVxuXG4uanAtU3RkaW4taW5wdXQ6OnBsYWNlaG9sZGVyIHtcbiAgb3BhY2l0eTogMDtcbn1cblxuLmpwLVN0ZGluLWlucHV0OmZvY3VzIHtcbiAgYm94LXNoYWRvdzogbm9uZTtcbn1cblxuLmpwLVN0ZGluLWlucHV0OmZvY3VzOjpwbGFjZWhvbGRlciB7XG4gIG9wYWNpdHk6IDE7XG59XG5cbi5qcC1PdXRwdXRBcmVhLXN0ZGluLWhpZGluZyB7XG4gIC8qIHNvZnQtaGlkZSB0aGUgb3V0cHV0LCBwcmVzZXJ2aW5nIGZvY3VzICovXG4gIG9wYWNpdHk6IDA7XG4gIGhlaWdodDogMDtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBPdXRwdXQgQXJlYSBWaWV3XG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi5qcC1MaW5rZWRPdXRwdXRWaWV3IC5qcC1PdXRwdXRBcmVhIHtcbiAgaGVpZ2h0OiAxMDAlO1xuICBkaXNwbGF5OiBibG9jaztcbn1cblxuLmpwLUxpbmtlZE91dHB1dFZpZXcgLmpwLU91dHB1dEFyZWEtY2hpbGQ6b25seS1jaGlsZCB7XG4gIGhlaWdodDogMTAwJTtcbn1cblxuLmpwLUxpbmtlZE91dHB1dFZpZXcgLmpwLU91dHB1dEFyZWEtb3V0cHV0Om9ubHktY2hpbGQge1xuICBoZWlnaHQ6IDEwMCU7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgUHJpbnRpbmdcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuQG1lZGlhIHByaW50IHtcbiAgLmpwLU91dHB1dEFyZWEtY2hpbGQge1xuICAgIGRpc3BsYXk6IHRhYmxlO1xuICAgIHRhYmxlLWxheW91dDogZml4ZWQ7XG4gICAgYnJlYWstaW5zaWRlOiBhdm9pZC1wYWdlO1xuICB9XG5cbiAgLmpwLU91dHB1dEFyZWEtcHJvbXB0IHtcbiAgICBkaXNwbGF5OiB0YWJsZS1jZWxsO1xuICAgIHZlcnRpY2FsLWFsaWduOiB0b3A7XG4gIH1cblxuICAuanAtT3V0cHV0QXJlYS1vdXRwdXQge1xuICAgIGRpc3BsYXk6IHRhYmxlLWNlbGw7XG4gIH1cbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBNb2JpbGVcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cbkBtZWRpYSBvbmx5IHNjcmVlbiBhbmQgKHdpZHRoIDw9IDc2MHB4KSB7XG4gIC5qcC1PdXRwdXRBcmVhLWNoaWxkIHtcbiAgICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xuICB9XG5cbiAgLmpwLU91dHB1dFByb21wdCB7XG4gICAgZmxleDogMCAwIGF1dG87XG4gICAgdGV4dC1hbGlnbjogbGVmdDtcbiAgfVxuXG4gIC5qcC1PdXRwdXRBcmVhLXByb21wdE92ZXJsYXkge1xuICAgIGRpc3BsYXk6IG5vbmU7XG4gIH1cbn1cblxuLyogVHJpbW1lZCBvdXRwdXRzIGNvbnRhaW5lciAqL1xuLmpwLVRyaW1tZWRPdXRwdXRzIHtcbiAgLyogTGVmdC1hbGlnbiB0aGUgYnV0dG9uIHdpdGhpbiB0aGUgb3V0cHV0IGFyZWEgKi9cbiAgdGV4dC1hbGlnbjogbGVmdDtcbn1cbmAsIFwiXCJdKTtcbi8vIEV4cG9ydHNcbmV4cG9ydCBkZWZhdWx0IF9fX0NTU19MT0FERVJfRVhQT1JUX19fO1xuIiwiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgUGxhY2Vob2xkZXJcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLVBsYWNlaG9sZGVyIHtcbiAgZGlzcGxheTogZmxleDtcbiAgZmxleC1kaXJlY3Rpb246IHJvdztcbiAgd2lkdGg6IDEwMCU7XG59XG5cbi5qcC1QbGFjZWhvbGRlci1wcm9tcHQge1xuICBmbGV4OiAwIDAgdmFyKC0tanAtY2VsbC1wcm9tcHQtd2lkdGgpO1xuICBib3gtc2l6aW5nOiBib3JkZXItYm94O1xufVxuXG4uanAtUGxhY2Vob2xkZXItY29udGVudCB7XG4gIGZsZXg6IDEgMSBhdXRvO1xuICBwYWRkaW5nOiA0cHggNnB4O1xuICBib3JkZXI6IDFweCBzb2xpZCB0cmFuc3BhcmVudDtcbiAgYm9yZGVyLXJhZGl1czogMDtcbiAgYmFja2dyb3VuZDogbm9uZTtcbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgY3Vyc29yOiBwb2ludGVyO1xufVxuXG4uanAtUGxhY2Vob2xkZXItY29udGVudENvbnRhaW5lciB7XG4gIGRpc3BsYXk6IGZsZXg7XG59XG5cbi5qcC1QbGFjZWhvbGRlci1jb250ZW50OmhvdmVyLFxuLmpwLUlucHV0UGxhY2Vob2xkZXIgPiAuanAtUGxhY2Vob2xkZXItY29udGVudDpob3ZlciB7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMyk7XG59XG5cbi5qcC1QbGFjZWhvbGRlci1jb250ZW50IC5qcC1Nb3JlSG9yaXpJY29uIHtcbiAgd2lkdGg6IDMycHg7XG4gIGhlaWdodDogMTZweDtcbiAgYm9yZGVyOiAxcHggc29saWQgdHJhbnNwYXJlbnQ7XG4gIGJvcmRlci1yYWRpdXM6IHZhcigtLWpwLWJvcmRlci1yYWRpdXMpO1xufVxuXG4uanAtUGxhY2Vob2xkZXItY29udGVudCAuanAtTW9yZUhvcml6SWNvbjpob3ZlciB7XG4gIGJvcmRlcjogMXB4IHNvbGlkIHZhcigtLWpwLWJvcmRlci1jb2xvcjEpO1xuICBib3gtc2hhZG93OiB2YXIoLS1qcC10b29sYmFyLWJveC1zaGFkb3cpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IwKTtcbn1cblxuLmpwLVBsYWNlaG9sZGVyVGV4dCB7XG4gIHdoaXRlLXNwYWNlOiBub3dyYXA7XG4gIG92ZXJmbG93LXg6IGhpZGRlbjtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yMyk7XG4gIGZvbnQtZmFtaWx5OiB2YXIoLS1qcC1jb2RlLWZvbnQtZmFtaWx5KTtcbn1cblxuLmpwLUlucHV0UGxhY2Vob2xkZXIgPiAuanAtUGxhY2Vob2xkZXItY29udGVudCB7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtY2VsbC1lZGl0b3ItYm9yZGVyLWNvbG9yKTtcbiAgYmFja2dyb3VuZDogdmFyKC0tanAtY2VsbC1lZGl0b3ItYmFja2dyb3VuZCk7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgUHJpbnRcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cbkBtZWRpYSBwcmludCB7XG4gIC5qcC1QbGFjZWhvbGRlciB7XG4gICAgZGlzcGxheTogdGFibGU7XG4gICAgdGFibGUtbGF5b3V0OiBmaXhlZDtcbiAgfVxuXG4gIC5qcC1QbGFjZWhvbGRlci1jb250ZW50IHtcbiAgICBkaXNwbGF5OiB0YWJsZS1jZWxsO1xuICB9XG5cbiAgLmpwLVBsYWNlaG9sZGVyLXByb21wdCB7XG4gICAgZGlzcGxheTogdGFibGUtY2VsbDtcbiAgfVxufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCIvLyBJbXBvcnRzXG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvbm9Tb3VyY2VNYXBzLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9hcGkuanNcIjtcbnZhciBfX19DU1NfTE9BREVSX0VYUE9SVF9fXyA9IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fKTtcbi8vIE1vZHVsZVxuX19fQ1NTX0xPQURFUl9FWFBPUlRfX18ucHVzaChbbW9kdWxlLmlkLCBgLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb3B5cmlnaHQgKGMpIEp1cHl0ZXIgRGV2ZWxvcG1lbnQgVGVhbS5cbnwgRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBJbnB1dFxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKiBBbGwgaW5wdXQgYXJlYXMgKi9cbi5qcC1JbnB1dEFyZWEge1xuICBkaXNwbGF5OiBmbGV4O1xuICBmbGV4LWRpcmVjdGlvbjogcm93O1xuICB3aWR0aDogMTAwJTtcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcbn1cblxuLmpwLUlucHV0QXJlYS1lZGl0b3Ige1xuICBmbGV4OiAxIDEgYXV0bztcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcblxuICAvKiBUaGlzIGlzIHRoZSBub24tYWN0aXZlLCBkZWZhdWx0IHN0eWxpbmcgKi9cbiAgYm9yZGVyOiB2YXIoLS1qcC1ib3JkZXItd2lkdGgpIHNvbGlkIHZhcigtLWpwLWNlbGwtZWRpdG9yLWJvcmRlci1jb2xvcik7XG4gIGJvcmRlci1yYWRpdXM6IDA7XG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLWNlbGwtZWRpdG9yLWJhY2tncm91bmQpO1xufVxuXG4uanAtSW5wdXRQcm9tcHQge1xuICBmbGV4OiAwIDAgdmFyKC0tanAtY2VsbC1wcm9tcHQtd2lkdGgpO1xuICB3aWR0aDogdmFyKC0tanAtY2VsbC1wcm9tcHQtd2lkdGgpO1xuICBjb2xvcjogdmFyKC0tanAtY2VsbC1pbnByb21wdC1mb250LWNvbG9yKTtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLWNlbGwtcHJvbXB0LWZvbnQtZmFtaWx5KTtcbiAgcGFkZGluZzogdmFyKC0tanAtY29kZS1wYWRkaW5nKTtcbiAgbGV0dGVyLXNwYWNpbmc6IHZhcigtLWpwLWNlbGwtcHJvbXB0LWxldHRlci1zcGFjaW5nKTtcbiAgb3BhY2l0eTogdmFyKC0tanAtY2VsbC1wcm9tcHQtb3BhY2l0eSk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC1jb2RlLWxpbmUtaGVpZ2h0KTtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC1jb2RlLWZvbnQtc2l6ZSk7XG4gIGJvcmRlcjogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSBzb2xpZCB0cmFuc3BhcmVudDtcblxuICAvKiBSaWdodCBhbGlnbiBwcm9tcHQgdGV4dCwgZG9uJ3Qgd3JhcCB0byBoYW5kbGUgbGFyZ2UgcHJvbXB0IG51bWJlcnMgKi9cbiAgdGV4dC1hbGlnbjogcmlnaHQ7XG4gIHdoaXRlLXNwYWNlOiBub3dyYXA7XG4gIG92ZXJmbG93OiBoaWRkZW47XG4gIHRleHQtb3ZlcmZsb3c6IGVsbGlwc2lzO1xuXG4gIC8qIERpc2FibGUgdGV4dCBzZWxlY3Rpb24gKi9cbiAgLXdlYmtpdC11c2VyLXNlbGVjdDogbm9uZTtcbiAgLW1vei11c2VyLXNlbGVjdDogbm9uZTtcbiAgLW1zLXVzZXItc2VsZWN0OiBub25lO1xuICB1c2VyLXNlbGVjdDogbm9uZTtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBQcmludFxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuQG1lZGlhIHByaW50IHtcbiAgLmpwLUlucHV0QXJlYSB7XG4gICAgZGlzcGxheTogdGFibGU7XG4gICAgdGFibGUtbGF5b3V0OiBmaXhlZDtcbiAgfVxuXG4gIC5qcC1JbnB1dEFyZWEtZWRpdG9yIHtcbiAgICBkaXNwbGF5OiB0YWJsZS1jZWxsO1xuICAgIHZlcnRpY2FsLWFsaWduOiB0b3A7XG4gIH1cblxuICAuanAtSW5wdXRQcm9tcHQge1xuICAgIGRpc3BsYXk6IHRhYmxlLWNlbGw7XG4gICAgdmVydGljYWwtYWxpZ246IHRvcDtcbiAgfVxufVxuXG4vKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IE1vYmlsZVxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuQG1lZGlhIG9ubHkgc2NyZWVuIGFuZCAod2lkdGggPD0gNzYwcHgpIHtcbiAgLmpwLUlucHV0QXJlYSB7XG4gICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgfVxuXG4gIC5qcC1JbnB1dEFyZWEtZWRpdG9yIHtcbiAgICBtYXJnaW4tbGVmdDogdmFyKC0tanAtY29kZS1wYWRkaW5nKTtcbiAgfVxuXG4gIC5qcC1JbnB1dFByb21wdCB7XG4gICAgZmxleDogMCAwIGF1dG87XG4gICAgdGV4dC1hbGlnbjogbGVmdDtcbiAgfVxufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCIvLyBJbXBvcnRzXG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvbm9Tb3VyY2VNYXBzLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9hcGkuanNcIjtcbnZhciBfX19DU1NfTE9BREVSX0VYUE9SVF9fXyA9IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fKTtcbi8vIE1vZHVsZVxuX19fQ1NTX0xPQURFUl9FWFBPUlRfX18ucHVzaChbbW9kdWxlLmlkLCBgLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb3B5cmlnaHQgKGMpIEp1cHl0ZXIgRGV2ZWxvcG1lbnQgVGVhbS5cbnwgRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBIZWFkZXIvRm9vdGVyXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qIEhpZGRlbiBieSB6ZXJvIGhlaWdodCBieSBkZWZhdWx0ICovXG4uanAtQ2VsbEhlYWRlcixcbi5qcC1DZWxsRm9vdGVyIHtcbiAgaGVpZ2h0OiAwO1xuICB3aWR0aDogMTAwJTtcbiAgcGFkZGluZzogMDtcbiAgbWFyZ2luOiAwO1xuICBib3JkZXI6IG5vbmU7XG4gIG91dGxpbmU6IG5vbmU7XG4gIGJhY2tncm91bmQ6IHRyYW5zcGFyZW50O1xufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCIvLyBJbXBvcnRzXG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvbm9Tb3VyY2VNYXBzLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9hcGkuanNcIjtcbnZhciBfX19DU1NfTE9BREVSX0VYUE9SVF9fXyA9IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fKTtcbi8vIE1vZHVsZVxuX19fQ1NTX0xPQURFUl9FWFBPUlRfX18ucHVzaChbbW9kdWxlLmlkLCBgLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb3B5cmlnaHQgKGMpIEp1cHl0ZXIgRGV2ZWxvcG1lbnQgVGVhbS5cbnwgRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLUNvbGxhcHNlciB7XG4gIGZsZXg6IDAgMCB2YXIoLS1qcC1jZWxsLWNvbGxhcHNlci13aWR0aCk7XG4gIHBhZGRpbmc6IDA7XG4gIG1hcmdpbjogMDtcbiAgYm9yZGVyOiBub25lO1xuICBvdXRsaW5lOiBub25lO1xuICBiYWNrZ3JvdW5kOiB0cmFuc3BhcmVudDtcbiAgYm9yZGVyLXJhZGl1czogdmFyKC0tanAtYm9yZGVyLXJhZGl1cyk7XG4gIG9wYWNpdHk6IDE7XG59XG5cbi5qcC1Db2xsYXBzZXItY2hpbGQge1xuICBkaXNwbGF5OiBibG9jaztcbiAgd2lkdGg6IDEwMCU7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG5cbiAgLyogaGVpZ2h0OiAxMDAlIGRvZXNuJ3Qgd29yayBiZWNhdXNlIHRoZSBoZWlnaHQgb2YgaXRzIHBhcmVudCBpcyBjb21wdXRlZCBmcm9tIGNvbnRlbnQgKi9cbiAgcG9zaXRpb246IGFic29sdXRlO1xuICB0b3A6IDA7XG4gIGJvdHRvbTogMDtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBQcmludGluZ1xufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKlxuSGlkaW5nIGNvbGxhcHNlcnMgaW4gcHJpbnQgbW9kZS5cblxuTm90ZTogaW5wdXQgYW5kIG91dHB1dCB3cmFwcGVycyBoYXZlIFwiZGlzcGxheTogYmxvY2tcIiBwcm9wZXJ0eSBpbiBwcmludCBtb2RlLlxuKi9cblxuQG1lZGlhIHByaW50IHtcbiAgLmpwLUNvbGxhcHNlciB7XG4gICAgZGlzcGxheTogbm9uZTtcbiAgfVxufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCJpbXBvcnQgYXBpIGZyb20gXCIhLi4vLi4vLi4vc3R5bGUtbG9hZGVyL2Rpc3QvcnVudGltZS9pbmplY3RTdHlsZXNJbnRvU3R5bGVUYWcuanNcIjtcbiAgICAgICAgICAgIGltcG9ydCBjb250ZW50IGZyb20gXCIhIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi9iYXNlLmNzc1wiO1xuXG52YXIgb3B0aW9ucyA9IHt9O1xuXG5vcHRpb25zLmluc2VydCA9IFwiaGVhZFwiO1xub3B0aW9ucy5zaW5nbGV0b24gPSBmYWxzZTtcblxudmFyIHVwZGF0ZSA9IGFwaShjb250ZW50LCBvcHRpb25zKTtcblxuXG5cbmV4cG9ydCBkZWZhdWx0IGNvbnRlbnQubG9jYWxzIHx8IHt9OyIsIi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qIFRoaXMgZmlsZSB3YXMgYXV0by1nZW5lcmF0ZWQgYnkgZW5zdXJlUGFja2FnZSgpIGluIEBqdXB5dGVybGFiL2J1aWxkdXRpbHMgKi9cbmltcG9ydCAnQGx1bWluby93aWRnZXRzL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvdWktY29tcG9uZW50cy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BqdXB5dGVybGFiL2FwcHV0aWxzL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvcmVuZGVybWltZS9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BqdXB5dGVybGFiL2RvY3JlZ2lzdHJ5L3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnLi9iYXNlLmNzcyc7IiwiaW1wb3J0IGFwaSBmcm9tIFwiIS4uLy4uLy4uL3N0eWxlLWxvYWRlci9kaXN0L3J1bnRpbWUvaW5qZWN0U3R5bGVzSW50b1N0eWxlVGFnLmpzXCI7XG4gICAgICAgICAgICBpbXBvcnQgY29udGVudCBmcm9tIFwiISEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vYmFzZS5jc3NcIjtcblxudmFyIG9wdGlvbnMgPSB7fTtcblxub3B0aW9ucy5pbnNlcnQgPSBcImhlYWRcIjtcbm9wdGlvbnMuc2luZ2xldG9uID0gZmFsc2U7XG5cbnZhciB1cGRhdGUgPSBhcGkoY29udGVudCwgb3B0aW9ucyk7XG5cblxuXG5leHBvcnQgZGVmYXVsdCBjb250ZW50LmxvY2FscyB8fCB7fTsiLCIvKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxufCBEaXN0cmlidXRlZCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIE1vZGlmaWVkIEJTRCBMaWNlbnNlLlxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKiBUaGlzIGZpbGUgd2FzIGF1dG8tZ2VuZXJhdGVkIGJ5IGVuc3VyZVBhY2thZ2UoKSBpbiBAanVweXRlcmxhYi9idWlsZHV0aWxzICovXG5pbXBvcnQgJ0BsdW1pbm8vd2lkZ2V0cy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BqdXB5dGVybGFiL2FwcHV0aWxzL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvcmVuZGVybWltZS9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJy4vYmFzZS5jc3MnOyIsIi8vIEltcG9ydHNcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9ub1NvdXJjZU1hcHMuanNcIjtcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL2FwaS5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfMF9fXyBmcm9tIFwiLSEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vY29sbGFwc2VyLmNzc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfMV9fXyBmcm9tIFwiLSEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vaGVhZGVyZm9vdGVyLmNzc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfMl9fXyBmcm9tIFwiLSEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vaW5wdXRhcmVhLmNzc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfM19fXyBmcm9tIFwiLSEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vcGxhY2Vob2xkZXIuY3NzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BVF9SVUxFX0lNUE9SVF80X19fIGZyb20gXCItIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi93aWRnZXQuY3NzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5pKF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfMF9fXyk7XG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5pKF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfMV9fXyk7XG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5pKF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfMl9fXyk7XG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5pKF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfM19fXyk7XG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5pKF9fX0NTU19MT0FERVJfQVRfUlVMRV9JTVBPUlRfNF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5gLCBcIlwiXSk7XG4vLyBFeHBvcnRzXG5leHBvcnQgZGVmYXVsdCBfX19DU1NfTE9BREVSX0VYUE9SVF9fXztcbiIsIi8vIEltcG9ydHNcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9ub1NvdXJjZU1hcHMuanNcIjtcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL2FwaS5qc1wiO1xudmFyIF9fX0NTU19MT0FERVJfRVhQT1JUX19fID0gX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fKF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18pO1xuLy8gTW9kdWxlXG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5wdXNoKFttb2R1bGUuaWQsIGAvKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxufCBEaXN0cmlidXRlZCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIE1vZGlmaWVkIEJTRCBMaWNlbnNlLlxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IFByaXZhdGUgQ1NTIHZhcmlhYmxlc1xufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG46cm9vdCB7XG4gIC0tanAtcHJpdmF0ZS1jZWxsLXNjcm9sbGluZy1vdXRwdXQtb2Zmc2V0OiA1cHg7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ2VsbFxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4uanAtQ2VsbCB7XG4gIHBhZGRpbmc6IHZhcigtLWpwLWNlbGwtcGFkZGluZyk7XG4gIG1hcmdpbjogMDtcbiAgYm9yZGVyOiBub25lO1xuICBvdXRsaW5lOiBub25lO1xuICBiYWNrZ3JvdW5kOiB0cmFuc3BhcmVudDtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb21tb24gaW5wdXQvb3V0cHV0XG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi5qcC1DZWxsLWlucHV0V3JhcHBlcixcbi5qcC1DZWxsLW91dHB1dFdyYXBwZXIge1xuICBkaXNwbGF5OiBmbGV4O1xuICBmbGV4LWRpcmVjdGlvbjogcm93O1xuICBwYWRkaW5nOiAwO1xuICBtYXJnaW46IDA7XG5cbiAgLyogQWRkZWQgdG8gcmV2ZWFsIHRoZSBib3gtc2hhZG93IG9uIHRoZSBpbnB1dCBhbmQgb3V0cHV0IGNvbGxhcHNlcnMuICovXG4gIG92ZXJmbG93OiB2aXNpYmxlO1xufVxuXG4vKiBPbmx5IGlucHV0L291dHB1dCBhcmVhcyBpbnNpZGUgY2VsbHMgKi9cbi5qcC1DZWxsLWlucHV0QXJlYSxcbi5qcC1DZWxsLW91dHB1dEFyZWEge1xuICBmbGV4OiAxIDEgYXV0bztcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb2xsYXBzZXJcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLyogTWFrZSB0aGUgb3V0cHV0IGNvbGxhcHNlciBkaXNhcHBlYXIgd2hlbiB0aGVyZSBpcyBub3Qgb3V0cHV0LCBidXQgZG8gc29cbiAqIGluIGEgbWFubmVyIHRoYXQgbGVhdmVzIGl0IGluIHRoZSBsYXlvdXQgYW5kIHByZXNlcnZlcyBpdHMgd2lkdGguXG4gKi9cbi5qcC1DZWxsLmpwLW1vZC1ub091dHB1dHMgLmpwLUNlbGwtb3V0cHV0Q29sbGFwc2VyIHtcbiAgYm9yZGVyOiBub25lICFpbXBvcnRhbnQ7XG4gIGJhY2tncm91bmQ6IHRyYW5zcGFyZW50ICFpbXBvcnRhbnQ7XG59XG5cbi5qcC1DZWxsOm5vdCguanAtbW9kLW5vT3V0cHV0cykgLmpwLUNlbGwtb3V0cHV0Q29sbGFwc2VyIHtcbiAgbWluLWhlaWdodDogdmFyKC0tanAtY2VsbC1jb2xsYXBzZXItbWluLWhlaWdodCk7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgT3V0cHV0XG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qIFB1dCBhIHNwYWNlIGJldHdlZW4gaW5wdXQgYW5kIG91dHB1dCB3aGVuIHRoZXJlIElTIG91dHB1dCAqL1xuLmpwLUNlbGw6bm90KC5qcC1tb2Qtbm9PdXRwdXRzKSAuanAtQ2VsbC1vdXRwdXRXcmFwcGVyIHtcbiAgbWFyZ2luLXRvcDogNXB4O1xufVxuXG4uanAtQ29kZUNlbGwuanAtbW9kLW91dHB1dHNTY3JvbGxlZCAuanAtQ2VsbC1vdXRwdXRBcmVhIHtcbiAgb3ZlcmZsb3cteTogYXV0bztcbiAgbWF4LWhlaWdodDogMjRlbTtcbiAgbWFyZ2luLWxlZnQ6IHZhcigtLWpwLXByaXZhdGUtY2VsbC1zY3JvbGxpbmctb3V0cHV0LW9mZnNldCk7XG4gIHJlc2l6ZTogdmVydGljYWw7XG59XG5cbi5qcC1Db2RlQ2VsbC5qcC1tb2Qtb3V0cHV0c1Njcm9sbGVkIC5qcC1DZWxsLW91dHB1dEFyZWFbc3R5bGUqPSdoZWlnaHQnXSB7XG4gIG1heC1oZWlnaHQ6IHVuc2V0O1xufVxuXG4uanAtQ29kZUNlbGwuanAtbW9kLW91dHB1dHNTY3JvbGxlZCAuanAtQ2VsbC1vdXRwdXRBcmVhOjphZnRlciB7XG4gIGNvbnRlbnQ6ICcgJztcbiAgYm94LXNoYWRvdzogaW5zZXQgMCAwIDZweCAycHggcmdiKDAgMCAwIC8gMzAlKTtcbiAgd2lkdGg6IDEwMCU7XG4gIGhlaWdodDogMTAwJTtcbiAgcG9zaXRpb246IHN0aWNreTtcbiAgYm90dG9tOiAwO1xuICB0b3A6IDA7XG4gIG1hcmdpbi10b3A6IC01MCU7XG4gIGZsb2F0OiBsZWZ0O1xuICBkaXNwbGF5OiBibG9jaztcbiAgcG9pbnRlci1ldmVudHM6IG5vbmU7XG59XG5cbi5qcC1Db2RlQ2VsbC5qcC1tb2Qtb3V0cHV0c1Njcm9sbGVkIC5qcC1PdXRwdXRBcmVhLWNoaWxkIHtcbiAgcGFkZGluZy10b3A6IDZweDtcbn1cblxuLmpwLUNvZGVDZWxsLmpwLW1vZC1vdXRwdXRzU2Nyb2xsZWQgLmpwLU91dHB1dEFyZWEtcHJvbXB0IHtcbiAgd2lkdGg6IGNhbGMoXG4gICAgdmFyKC0tanAtY2VsbC1wcm9tcHQtd2lkdGgpIC0gdmFyKC0tanAtcHJpdmF0ZS1jZWxsLXNjcm9sbGluZy1vdXRwdXQtb2Zmc2V0KVxuICApO1xuICBmbGV4OiAwIDBcbiAgICBjYWxjKFxuICAgICAgdmFyKC0tanAtY2VsbC1wcm9tcHQtd2lkdGgpIC1cbiAgICAgICAgdmFyKC0tanAtcHJpdmF0ZS1jZWxsLXNjcm9sbGluZy1vdXRwdXQtb2Zmc2V0KVxuICAgICk7XG59XG5cbi5qcC1Db2RlQ2VsbC5qcC1tb2Qtb3V0cHV0c1Njcm9sbGVkIC5qcC1PdXRwdXRBcmVhLXByb21wdE92ZXJsYXkge1xuICBsZWZ0OiBjYWxjKC0xICogdmFyKC0tanAtcHJpdmF0ZS1jZWxsLXNjcm9sbGluZy1vdXRwdXQtb2Zmc2V0KSk7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29kZUNlbGxcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBNYXJrZG93bkNlbGxcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLU1hcmtkb3duT3V0cHV0IHtcbiAgZmxleDogMSAxIGF1dG87XG4gIHdpZHRoOiAxMDAlO1xuICBtYXJnaW4tdG9wOiAwO1xuICBtYXJnaW4tYm90dG9tOiAwO1xuICBwYWRkaW5nLWxlZnQ6IHZhcigtLWpwLWNvZGUtcGFkZGluZyk7XG59XG5cbi5qcC1NYXJrZG93bk91dHB1dC5qcC1SZW5kZXJlZEhUTUxDb21tb24ge1xuICBvdmVyZmxvdzogYXV0bztcbn1cblxuLyogY29sbGFwc2VIZWFkaW5nQnV0dG9uIChzaG93IGFsd2F5cyBpZiBoaWRkZW5DZWxsc0J1dHRvbiBpcyBfbm90XyBzaG93bikgKi9cbi5qcC1jb2xsYXBzZUhlYWRpbmdCdXR0b24ge1xuICBkaXNwbGF5OiBmbGV4O1xuICBtaW4taGVpZ2h0OiB2YXIoLS1qcC1jZWxsLWNvbGxhcHNlci1taW4taGVpZ2h0KTtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC1jb2RlLWZvbnQtc2l6ZSk7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdHJhbnNwYXJlbnQ7XG4gIGJhY2tncm91bmQtc2l6ZTogMjVweDtcbiAgYmFja2dyb3VuZC1yZXBlYXQ6IG5vLXJlcGVhdDtcbiAgYmFja2dyb3VuZC1wb3NpdGlvbi14OiBjZW50ZXI7XG4gIGJhY2tncm91bmQtcG9zaXRpb24teTogdG9wO1xuICBiYWNrZ3JvdW5kLWltYWdlOiB2YXIoLS1qcC1pY29uLWNhcmV0LWRvd24pO1xuICByaWdodDogMDtcbiAgdG9wOiAwO1xuICBib3R0b206IDA7XG59XG5cbi5qcC1jb2xsYXBzZUhlYWRpbmdCdXR0b24uanAtbW9kLWNvbGxhcHNlZCB7XG4gIGJhY2tncm91bmQtaW1hZ2U6IHZhcigtLWpwLWljb24tY2FyZXQtcmlnaHQpO1xufVxuXG4vKlxuIHNldCB0aGUgY29udGFpbmVyIGZvbnQgc2l6ZSB0byBtYXRjaCB0aGF0IG9mIGNvbnRlbnRcbiBzbyB0aGF0IHRoZSBuZXN0ZWQgY29sbGFwc2UgYnV0dG9ucyBoYXZlIHRoZSByaWdodCBzaXplXG4qL1xuLmpwLU1hcmtkb3duQ2VsbCAuanAtSW5wdXRQcm9tcHQge1xuICBmb250LXNpemU6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1zaXplMSk7XG59XG5cbi8qXG4gIEFsaWduIGNvbGxhcHNlSGVhZGluZ0J1dHRvbiB3aXRoIGNlbGwgdG9wIGhlYWRlclxuICBUaGUgZm9udCBzaXplcyBhcmUgaWRlbnRpY2FsIHRvIHRoZSBvbmVzIGluIHBhY2thZ2VzL3JlbmRlcm1pbWUvc3R5bGUvYmFzZS5jc3NcbiovXG4uanAtbW9kLXJlbmRlcmVkIC5qcC1jb2xsYXBzZUhlYWRpbmdCdXR0b25bZGF0YS1oZWFkaW5nLWxldmVsPScxJ10ge1xuICBmb250LXNpemU6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1zaXplNSk7XG4gIGJhY2tncm91bmQtcG9zaXRpb24teTogY2FsYygwLjMgKiB2YXIoLS1qcC1jb250ZW50LWZvbnQtc2l6ZTUpKTtcbn1cblxuLmpwLW1vZC1yZW5kZXJlZCAuanAtY29sbGFwc2VIZWFkaW5nQnV0dG9uW2RhdGEtaGVhZGluZy1sZXZlbD0nMiddIHtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC1jb250ZW50LWZvbnQtc2l6ZTQpO1xuICBiYWNrZ3JvdW5kLXBvc2l0aW9uLXk6IGNhbGMoMC4zICogdmFyKC0tanAtY29udGVudC1mb250LXNpemU0KSk7XG59XG5cbi5qcC1tb2QtcmVuZGVyZWQgLmpwLWNvbGxhcHNlSGVhZGluZ0J1dHRvbltkYXRhLWhlYWRpbmctbGV2ZWw9JzMnXSB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemUzKTtcbiAgYmFja2dyb3VuZC1wb3NpdGlvbi15OiBjYWxjKDAuMyAqIHZhcigtLWpwLWNvbnRlbnQtZm9udC1zaXplMykpO1xufVxuXG4uanAtbW9kLXJlbmRlcmVkIC5qcC1jb2xsYXBzZUhlYWRpbmdCdXR0b25bZGF0YS1oZWFkaW5nLWxldmVsPSc0J10ge1xuICBmb250LXNpemU6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1zaXplMik7XG4gIGJhY2tncm91bmQtcG9zaXRpb24teTogY2FsYygwLjMgKiB2YXIoLS1qcC1jb250ZW50LWZvbnQtc2l6ZTIpKTtcbn1cblxuLmpwLW1vZC1yZW5kZXJlZCAuanAtY29sbGFwc2VIZWFkaW5nQnV0dG9uW2RhdGEtaGVhZGluZy1sZXZlbD0nNSddIHtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC1jb250ZW50LWZvbnQtc2l6ZTEpO1xuICBiYWNrZ3JvdW5kLXBvc2l0aW9uLXk6IHRvcDtcbn1cblxuLmpwLW1vZC1yZW5kZXJlZCAuanAtY29sbGFwc2VIZWFkaW5nQnV0dG9uW2RhdGEtaGVhZGluZy1sZXZlbD0nNiddIHtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC1jb250ZW50LWZvbnQtc2l6ZTApO1xuICBiYWNrZ3JvdW5kLXBvc2l0aW9uLXk6IHRvcDtcbn1cblxuLyogY29sbGFwc2VIZWFkaW5nQnV0dG9uIChzaG93IG9ubHkgb24gKGhvdmVyLGFjdGl2ZSkgaWYgaGlkZGVuQ2VsbHNCdXR0b24gaXMgc2hvd24pICovXG4uanAtTm90ZWJvb2suanAtbW9kLXNob3dIaWRkZW5DZWxsc0J1dHRvbiAuanAtY29sbGFwc2VIZWFkaW5nQnV0dG9uIHtcbiAgZGlzcGxheTogbm9uZTtcbn1cblxuLmpwLU5vdGVib29rLmpwLW1vZC1zaG93SGlkZGVuQ2VsbHNCdXR0b25cbiAgOmlzKC5qcC1NYXJrZG93bkNlbGw6aG92ZXIsIC5qcC1tb2QtYWN0aXZlKVxuICAuanAtY29sbGFwc2VIZWFkaW5nQnV0dG9uIHtcbiAgZGlzcGxheTogZmxleDtcbn1cblxuLyogc2hvd0hpZGRlbkNlbGxzQnV0dG9uIChvbmx5IHNob3cgaWYganAtbW9kLXNob3dIaWRkZW5DZWxsc0J1dHRvbiBpcyBzZXQsIHdoaWNoXG5pcyBhIGNvbnNlcXVlbmNlIG9mIHRoZSBzaG93SGlkZGVuQ2VsbHNCdXR0b24gb3B0aW9uIGluIE5vdGVib29rIFNldHRpbmdzKSovXG4uanAtTm90ZWJvb2suanAtbW9kLXNob3dIaWRkZW5DZWxsc0J1dHRvbiAuanAtc2hvd0hpZGRlbkNlbGxzQnV0dG9uIHtcbiAgbWFyZ2luLWxlZnQ6IGNhbGModmFyKC0tanAtY2VsbC1wcm9tcHQtd2lkdGgpICsgMiAqIHZhcigtLWpwLWNvZGUtcGFkZGluZykpO1xuICBtYXJnaW4tdG9wOiB2YXIoLS1qcC1jb2RlLXBhZGRpbmcpO1xuICBib3JkZXI6IDFweCBzb2xpZCB2YXIoLS1qcC1ib3JkZXItY29sb3IyKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMykgIWltcG9ydGFudDtcbiAgY29sb3I6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1jb2xvcjApICFpbXBvcnRhbnQ7XG4gIGRpc3BsYXk6IGZsZXg7XG59XG5cbi5qcC1Ob3RlYm9vay5qcC1tb2Qtc2hvd0hpZGRlbkNlbGxzQnV0dG9uIC5qcC1zaG93SGlkZGVuQ2VsbHNCdXR0b246aG92ZXIge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1ib3JkZXItY29sb3IyKSAhaW1wb3J0YW50O1xufVxuXG4uanAtc2hvd0hpZGRlbkNlbGxzQnV0dG9uIHtcbiAgZGlzcGxheTogbm9uZTtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBQcmludGluZ1xufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKlxuVXNpbmcgYmxvY2sgaW5zdGVhZCBvZiBmbGV4IHRvIGFsbG93IHRoZSB1c2Ugb2YgdGhlIGJyZWFrLWluc2lkZSBDU1MgcHJvcGVydHkgZm9yXG5jZWxsIG91dHB1dHMuXG4qL1xuXG5AbWVkaWEgcHJpbnQge1xuICAuanAtQ2VsbC1pbnB1dFdyYXBwZXIsXG4gIC5qcC1DZWxsLW91dHB1dFdyYXBwZXIge1xuICAgIGRpc3BsYXk6IGJsb2NrO1xuICB9XG5cbiAgLmpwLU1hcmtkb3duT3V0cHV0IHtcbiAgICBkaXNwbGF5OiB0YWJsZS1jZWxsO1xuICB9XG59XG5gLCBcIlwiXSk7XG4vLyBFeHBvcnRzXG5leHBvcnQgZGVmYXVsdCBfX19DU1NfTE9BREVSX0VYUE9SVF9fXztcbiIsIi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qIFRoaXMgZmlsZSB3YXMgYXV0by1nZW5lcmF0ZWQgYnkgZW5zdXJlUGFja2FnZSgpIGluIEBqdXB5dGVybGFiL2J1aWxkdXRpbHMgKi9cbmltcG9ydCAnQGp1cHl0ZXJsYWIvcmVuZGVybWltZS9zdHlsZS9pbmRleC5qcyc7IiwiaW1wb3J0IGFwaSBmcm9tIFwiIS4uLy4uLy4uL3N0eWxlLWxvYWRlci9kaXN0L3J1bnRpbWUvaW5qZWN0U3R5bGVzSW50b1N0eWxlVGFnLmpzXCI7XG4gICAgICAgICAgICBpbXBvcnQgY29udGVudCBmcm9tIFwiISEuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvY2pzLmpzIS4vYmFzZS5jc3NcIjtcblxudmFyIG9wdGlvbnMgPSB7fTtcblxub3B0aW9ucy5pbnNlcnQgPSBcImhlYWRcIjtcbm9wdGlvbnMuc2luZ2xldG9uID0gZmFsc2U7XG5cbnZhciB1cGRhdGUgPSBhcGkoY29udGVudCwgb3B0aW9ucyk7XG5cblxuXG5leHBvcnQgZGVmYXVsdCBjb250ZW50LmxvY2FscyB8fCB7fTsiLCIvKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxufCBEaXN0cmlidXRlZCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIE1vZGlmaWVkIEJTRCBMaWNlbnNlLlxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKiBUaGlzIGZpbGUgd2FzIGF1dG8tZ2VuZXJhdGVkIGJ5IGVuc3VyZVBhY2thZ2UoKSBpbiBAanVweXRlcmxhYi9idWlsZHV0aWxzICovXG5pbXBvcnQgJ0BsdW1pbm8vd2lkZ2V0cy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BqdXB5dGVybGFiL3VpLWNvbXBvbmVudHMvc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9hcHB1dGlscy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BqdXB5dGVybGFiL3JlbmRlcm1pbWUvc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9hdHRhY2htZW50cy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJ0BsdW1pbm8vZHJhZ2Ryb3Avc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9jb2RlZWRpdG9yL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvZG9jdW1lbnRzZWFyY2gvc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9jb2RlbWlycm9yL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvZmlsZWJyb3dzZXIvc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9vdXRwdXRhcmVhL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvdG9jL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnLi9iYXNlLmNzcyc7IiwiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgVGFibGUgb2YgQ29udGVudHNcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLVRhYmxlT2ZDb250ZW50cyB7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGZsZXgtZGlyZWN0aW9uOiBjb2x1bW47XG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjEpO1xuICBmb250LXNpemU6IHZhcigtLWpwLXVpLWZvbnQtc2l6ZTEpO1xuICBoZWlnaHQ6IDEwMCU7XG59XG5cbi5qcC1UYWJsZU9mQ29udGVudHMtcGxhY2Vob2xkZXIge1xuICB0ZXh0LWFsaWduOiBjZW50ZXI7XG59XG5cbi5qcC1UYWJsZU9mQ29udGVudHMtcGxhY2Vob2xkZXJDb250ZW50IHtcbiAgY29sb3I6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1jb2xvcjIpO1xuICBwYWRkaW5nOiA4cHg7XG59XG5cbi5qcC1UYWJsZU9mQ29udGVudHMtcGxhY2Vob2xkZXJDb250ZW50ID4gaDMge1xuICBtYXJnaW4tYm90dG9tOiB2YXIoLS1qcC1jb250ZW50LWhlYWRpbmctbWFyZ2luLWJvdHRvbSk7XG59XG5cbi5qcC1UYWJsZU9mQ29udGVudHMgLmpwLVNpZGVQYW5lbC1jb250ZW50IHtcbiAgb3ZlcmZsb3cteTogYXV0bztcbn1cblxuLmpwLVRhYmxlT2ZDb250ZW50cy10cmVlIHtcbiAgbWFyZ2luOiA0cHg7XG59XG5cbi5qcC1UYWJsZU9mQ29udGVudHMtY29udGVudCB7XG4gIHBhZGRpbmc6IDA7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xufVxuXG4uanAtdG9jSXRlbSB7XG4gIC13ZWJraXQtdXNlci1zZWxlY3Q6IG5vbmU7XG4gIC1tb3otdXNlci1zZWxlY3Q6IG5vbmU7XG4gIC1tcy11c2VyLXNlbGVjdDogbm9uZTtcbiAgdXNlci1zZWxlY3Q6IG5vbmU7XG59XG5cbi5qcC10b2NJdGVtLWhlYWRpbmcge1xuICBkaXNwbGF5OiBmbGV4O1xuICBjdXJzb3I6IHBvaW50ZXI7XG4gIHdpZHRoOiAxMDAlO1xufVxuXG4uanAtdG9jSXRlbS1jb250ZW50IHtcbiAgZGlzcGxheTogYmxvY2s7XG4gIHBhZGRpbmc6IDRweCAwO1xuICB3aGl0ZS1zcGFjZTogbm93cmFwO1xuICB0ZXh0LW92ZXJmbG93OiBlbGxpcHNpcztcbiAgb3ZlcmZsb3cteDogaGlkZGVuO1xufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9