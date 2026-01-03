"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1208,9448],{

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

/***/ 29448
(__unused_webpack_module, __unused_webpack___webpack_exports__, __webpack_require__) {


// EXTERNAL MODULE: ./node_modules/@lumino/widgets/style/index.js + 1 modules
var style = __webpack_require__(47214);
// EXTERNAL MODULE: ./node_modules/@jupyterlab/apputils/style/index.js + 1 modules
var apputils_style = __webpack_require__(84940);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js
var injectStylesIntoStyleTag = __webpack_require__(85072);
var injectStylesIntoStyleTag_default = /*#__PURE__*/__webpack_require__.n(injectStylesIntoStyleTag);
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/@jupyterlab/rendermime/style/base.css
var base = __webpack_require__(30354);
;// ./node_modules/@jupyterlab/rendermime/style/base.css

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = injectStylesIntoStyleTag_default()(base/* default */.A, options);



/* harmony default export */ const style_base = (base/* default */.A.locals || {});
;// ./node_modules/@jupyterlab/rendermime/style/index.js
/*-----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/* This file was auto-generated by ensurePackage() in @jupyterlab/buildutils */




/***/ },

/***/ 30354
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
| RenderedText
|----------------------------------------------------------------------------*/

:root {
  /* This is the padding value to fill the gaps between lines containing spans with background color. */
  --jp-private-code-span-padding: calc(
    (var(--jp-code-line-height) - 1) * var(--jp-code-font-size) / 2
  );
}

.jp-RenderedText {
  text-align: left;
  padding-left: var(--jp-code-padding);
  line-height: var(--jp-code-line-height);
  font-family: var(--jp-code-font-family);
}

.jp-ThemedContainer .jp-RenderedText pre,
.jp-ThemedContainer .jp-RenderedJavaScript pre,
.jp-ThemedContainer .jp-RenderedHTMLCommon pre {
  color: var(--jp-content-font-color1);
  font-size: var(--jp-code-font-size);
  border: none;
  margin: 0;
  padding: 0;
}

.jp-RenderedText pre a[href]:link {
  text-decoration: none;
  color: var(--jp-content-link-color);
}

.jp-RenderedText pre a[href]:hover {
  text-decoration: underline;
  color: var(--jp-content-link-hover-color, var(--jp-content-link-color));
}

.jp-RenderedText pre a[href]:visited {
  text-decoration: none;
  color: var(--jp-content-link-visited-color, var(--jp-content-link-color));
}

/* console foregrounds and backgrounds */
.jp-RenderedText pre .ansi-black-fg {
  color: #3e424d;
}

.jp-RenderedText pre .ansi-red-fg {
  color: #e75c58;
}

.jp-RenderedText pre .ansi-green-fg {
  color: #00a250;
}

.jp-RenderedText pre .ansi-yellow-fg {
  color: #ddb62b;
}

.jp-RenderedText pre .ansi-blue-fg {
  color: #208ffb;
}

.jp-RenderedText pre .ansi-magenta-fg {
  color: #d160c4;
}

.jp-RenderedText pre .ansi-cyan-fg {
  color: #60c6c8;
}

.jp-RenderedText pre .ansi-white-fg {
  color: #c5c1b4;
}

.jp-RenderedText pre .ansi-black-bg {
  background-color: #3e424d;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-red-bg {
  background-color: #e75c58;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-green-bg {
  background-color: #00a250;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-yellow-bg {
  background-color: #ddb62b;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-blue-bg {
  background-color: #208ffb;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-magenta-bg {
  background-color: #d160c4;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-cyan-bg {
  background-color: #60c6c8;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-white-bg {
  background-color: #c5c1b4;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-black-intense-fg {
  color: #282c36;
}

.jp-RenderedText pre .ansi-red-intense-fg {
  color: #b22b31;
}

.jp-RenderedText pre .ansi-green-intense-fg {
  color: #007427;
}

.jp-RenderedText pre .ansi-yellow-intense-fg {
  color: #b27d12;
}

.jp-RenderedText pre .ansi-blue-intense-fg {
  color: #0065ca;
}

.jp-RenderedText pre .ansi-magenta-intense-fg {
  color: #a03196;
}

.jp-RenderedText pre .ansi-cyan-intense-fg {
  color: #258f8f;
}

.jp-RenderedText pre .ansi-white-intense-fg {
  color: #a1a6b2;
}

.jp-RenderedText pre .ansi-black-intense-bg {
  background-color: #282c36;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-red-intense-bg {
  background-color: #b22b31;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-green-intense-bg {
  background-color: #007427;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-yellow-intense-bg {
  background-color: #b27d12;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-blue-intense-bg {
  background-color: #0065ca;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-magenta-intense-bg {
  background-color: #a03196;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-cyan-intense-bg {
  background-color: #258f8f;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-white-intense-bg {
  background-color: #a1a6b2;
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-default-inverse-fg {
  color: var(--jp-ui-inverse-font-color0);
}

.jp-RenderedText pre .ansi-default-inverse-bg {
  background-color: var(--jp-inverse-layout-color0);
  padding: var(--jp-private-code-span-padding) 0;
}

.jp-RenderedText pre .ansi-bold {
  font-weight: bold;
}

.jp-RenderedText pre .ansi-underline {
  text-decoration: underline;
}

.jp-RenderedText[data-mime-type='application/vnd.jupyter.stderr'] {
  background: var(--jp-rendermime-error-background);
  padding-top: var(--jp-code-padding);
}

/* fix illegible yellow text with yellow background in exception stacktrace */
.jp-RenderedText pre .ansi-yellow-bg.ansi-yellow-fg {
  color: black;
}

/*-----------------------------------------------------------------------------
| RenderedLatex
|----------------------------------------------------------------------------*/

.jp-RenderedLatex {
  color: var(--jp-content-font-color1);
  font-size: var(--jp-content-font-size1);
  line-height: var(--jp-content-line-height);
}

/* Left-justify outputs.*/
.jp-OutputArea-output.jp-RenderedLatex {
  padding: var(--jp-code-padding);
  text-align: left;
}

/*-----------------------------------------------------------------------------
| RenderedHTML
|----------------------------------------------------------------------------*/

.jp-RenderedHTMLCommon {
  color: var(--jp-content-font-color1);
  font-family: var(--jp-content-font-family);
  font-size: var(--jp-content-font-size1);
  line-height: var(--jp-content-line-height);

  /* Give a bit more R padding on Markdown text to keep line lengths reasonable */
  padding-right: 20px;
}

.jp-RenderedHTMLCommon em {
  font-style: italic;
}

.jp-RenderedHTMLCommon strong {
  font-weight: bold;
}

.jp-RenderedHTMLCommon u {
  text-decoration: underline;
}

.jp-RenderedHTMLCommon a:link {
  text-decoration: none;
  color: var(--jp-content-link-color);
}

.jp-RenderedHTMLCommon a:hover {
  text-decoration: underline;
  color: var(--jp-content-link-hover-color, var(--jp-content-link-color));
}

.jp-RenderedHTMLCommon a:visited {
  text-decoration: none;
  color: var(--jp-content-link-visited-color, var(--jp-content-link-color));
}

/* Headings */

.jp-RenderedHTMLCommon h1,
.jp-RenderedHTMLCommon h2,
.jp-RenderedHTMLCommon h3,
.jp-RenderedHTMLCommon h4,
.jp-RenderedHTMLCommon h5,
.jp-RenderedHTMLCommon h6 {
  line-height: var(--jp-content-heading-line-height);
  font-weight: var(--jp-content-heading-font-weight);
  font-style: normal;
  margin: var(--jp-content-heading-margin-top) 0
    var(--jp-content-heading-margin-bottom) 0;
  scroll-margin-top: var(--jp-content-heading-margin-top);
}

.jp-RenderedHTMLCommon h1:first-child,
.jp-RenderedHTMLCommon h2:first-child,
.jp-RenderedHTMLCommon h3:first-child,
.jp-RenderedHTMLCommon h4:first-child,
.jp-RenderedHTMLCommon h5:first-child,
.jp-RenderedHTMLCommon h6:first-child {
  margin-top: calc(0.5 * var(--jp-content-heading-margin-top));
  scroll-margin-top: calc(0.5 * var(--jp-content-heading-margin-top));
}

.jp-RenderedHTMLCommon h1:last-child,
.jp-RenderedHTMLCommon h2:last-child,
.jp-RenderedHTMLCommon h3:last-child,
.jp-RenderedHTMLCommon h4:last-child,
.jp-RenderedHTMLCommon h5:last-child,
.jp-RenderedHTMLCommon h6:last-child {
  margin-bottom: calc(0.5 * var(--jp-content-heading-margin-bottom));
}

.jp-RenderedHTMLCommon h1 {
  font-size: var(--jp-content-font-size5);
}

.jp-RenderedHTMLCommon h2 {
  font-size: var(--jp-content-font-size4);
}

.jp-RenderedHTMLCommon h3 {
  font-size: var(--jp-content-font-size3);
}

.jp-RenderedHTMLCommon h4 {
  font-size: var(--jp-content-font-size2);
}

.jp-RenderedHTMLCommon h5 {
  font-size: var(--jp-content-font-size1);
}

.jp-RenderedHTMLCommon h6 {
  font-size: var(--jp-content-font-size0);
}

/* Lists */

/* stylelint-disable selector-max-type, selector-max-compound-selectors */

.jp-RenderedHTMLCommon ul:not(.list-inline),
.jp-RenderedHTMLCommon ol:not(.list-inline) {
  padding-left: 2em;
}

.jp-RenderedHTMLCommon ul {
  list-style: disc;
}

.jp-RenderedHTMLCommon ul ul {
  list-style: square;
}

.jp-RenderedHTMLCommon ul ul ul {
  list-style: circle;
}

.jp-RenderedHTMLCommon ol {
  list-style: decimal;
}

.jp-RenderedHTMLCommon ol ol {
  list-style: upper-alpha;
}

.jp-RenderedHTMLCommon ol ol ol {
  list-style: lower-alpha;
}

.jp-RenderedHTMLCommon ol ol ol ol {
  list-style: lower-roman;
}

.jp-RenderedHTMLCommon ol ol ol ol ol {
  list-style: decimal;
}

.jp-RenderedHTMLCommon ol,
.jp-RenderedHTMLCommon ul {
  margin-bottom: 1em;
}

.jp-RenderedHTMLCommon ul ul,
.jp-RenderedHTMLCommon ul ol,
.jp-RenderedHTMLCommon ol ul,
.jp-RenderedHTMLCommon ol ol {
  margin-bottom: 0;
}

/* stylelint-enable selector-max-type, selector-max-compound-selectors */

.jp-RenderedHTMLCommon hr {
  color: var(--jp-border-color2);
  background-color: var(--jp-border-color1);
  margin-top: 1em;
  margin-bottom: 1em;
}

.jp-ThemedContainer .jp-RenderedHTMLCommon > pre {
  margin: 1.5em 2em;
}

.jp-ThemedContainer .jp-RenderedHTMLCommon pre,
.jp-ThemedContainer .jp-RenderedHTMLCommon code {
  border: 0;
  background-color: var(--jp-layout-color0);
  color: var(--jp-content-font-color1);
  font-family: var(--jp-code-font-family);
  font-size: inherit;
  line-height: var(--jp-code-line-height);
  padding: 0;
  white-space: pre-wrap;
}

.jp-ThemedContainer .jp-RenderedHTMLCommon :not(pre) > code {
  background-color: var(--jp-layout-color2);
  padding: 1px 5px;
}

/* Tables */

.jp-RenderedHTMLCommon table {
  border-collapse: collapse;
  border-spacing: 0;
  border: none;
  color: var(--jp-ui-font-color1);
  font-size: var(--jp-ui-font-size1);
  table-layout: fixed;
  margin-left: auto;
  margin-bottom: 1em;
  margin-right: auto;
}

.jp-RenderedHTMLCommon thead {
  border-bottom: var(--jp-border-width) solid var(--jp-border-color1);
  vertical-align: bottom;
}

.jp-RenderedHTMLCommon td,
.jp-RenderedHTMLCommon th,
.jp-RenderedHTMLCommon tr {
  vertical-align: middle;
  padding: 0.5em;
  line-height: normal;
  white-space: normal;
  max-width: none;
  border: none;
}

.jp-RenderedMarkdown.jp-RenderedHTMLCommon td,
.jp-RenderedMarkdown.jp-RenderedHTMLCommon th {
  max-width: none;
}

:not(.jp-RenderedMarkdown).jp-RenderedHTMLCommon td,
:not(.jp-RenderedMarkdown).jp-RenderedHTMLCommon th,
:not(.jp-RenderedMarkdown).jp-RenderedHTMLCommon tr {
  text-align: right;
}

.jp-RenderedHTMLCommon th {
  font-weight: bold;
}

.jp-RenderedHTMLCommon tbody tr:nth-child(odd) {
  background: var(--jp-layout-color0);
}

.jp-RenderedHTMLCommon tbody tr:nth-child(even) {
  background: var(--jp-rendermime-table-row-background);
}

.jp-RenderedHTMLCommon tbody tr:hover {
  background: var(--jp-rendermime-table-row-hover-background);
}

.jp-RenderedHTMLCommon p {
  text-align: left;
  margin: 0;
  margin-bottom: 1em;
}

.jp-RenderedHTMLCommon img {
  -moz-force-broken-image-icon: 1;
}

/* Restrict to direct children as other images could be nested in other content. */
.jp-RenderedHTMLCommon > img {
  display: block;
  margin-left: 0;
  margin-right: 0;
  margin-bottom: 1em;
}

/* Change color behind transparent images if they need it... */
[data-jp-theme-light='false'] .jp-RenderedImage img.jp-needs-light-background {
  background-color: var(--jp-inverse-layout-color1);
}

[data-jp-theme-light='true'] .jp-RenderedImage img.jp-needs-dark-background {
  background-color: var(--jp-inverse-layout-color1);
}

.jp-RenderedHTMLCommon img,
.jp-RenderedImage img,
.jp-RenderedHTMLCommon svg,
.jp-RenderedSVG svg {
  max-width: 100%;
  height: auto;
}

.jp-RenderedHTMLCommon img.jp-mod-unconfined,
.jp-RenderedImage img.jp-mod-unconfined,
.jp-RenderedHTMLCommon svg.jp-mod-unconfined,
.jp-RenderedSVG svg.jp-mod-unconfined {
  max-width: none;
}

.jp-RenderedHTMLCommon .alert {
  padding: var(--jp-notebook-padding);
  border: var(--jp-border-width) solid transparent;
  border-radius: var(--jp-border-radius);
  margin-bottom: 1em;
}

.jp-RenderedHTMLCommon .alert-info {
  color: var(--jp-info-color0);
  background-color: var(--jp-info-color3);
  border-color: var(--jp-info-color2);
}

.jp-RenderedHTMLCommon .alert-info hr {
  border-color: var(--jp-info-color3);
}

.jp-RenderedHTMLCommon .alert-info > p:last-child,
.jp-RenderedHTMLCommon .alert-info > ul:last-child {
  margin-bottom: 0;
}

.jp-RenderedHTMLCommon .alert-warning {
  color: var(--jp-warn-color0);
  background-color: var(--jp-warn-color3);
  border-color: var(--jp-warn-color2);
}

.jp-RenderedHTMLCommon .alert-warning hr {
  border-color: var(--jp-warn-color3);
}

.jp-RenderedHTMLCommon .alert-warning > p:last-child,
.jp-RenderedHTMLCommon .alert-warning > ul:last-child {
  margin-bottom: 0;
}

.jp-RenderedHTMLCommon .alert-success {
  color: var(--jp-success-color0);
  background-color: var(--jp-success-color3);
  border-color: var(--jp-success-color2);
}

.jp-RenderedHTMLCommon .alert-success hr {
  border-color: var(--jp-success-color3);
}

.jp-RenderedHTMLCommon .alert-success > p:last-child,
.jp-RenderedHTMLCommon .alert-success > ul:last-child {
  margin-bottom: 0;
}

.jp-RenderedHTMLCommon .alert-danger {
  color: var(--jp-error-color0);
  background-color: var(--jp-error-color3);
  border-color: var(--jp-error-color2);
}

.jp-RenderedHTMLCommon .alert-danger hr {
  border-color: var(--jp-error-color3);
}

.jp-RenderedHTMLCommon .alert-danger > p:last-child,
.jp-RenderedHTMLCommon .alert-danger > ul:last-child {
  margin-bottom: 0;
}

.jp-RenderedHTMLCommon blockquote {
  margin: 1em 2em;
  padding: 0 1em;
  border-left: 5px solid var(--jp-border-color2);
}

a.jp-InternalAnchorLink {
  visibility: hidden;
  margin-left: 8px;
  color: var(--md-blue-800, #1565c0);
}

h1:hover .jp-InternalAnchorLink,
h2:hover .jp-InternalAnchorLink,
h3:hover .jp-InternalAnchorLink,
h4:hover .jp-InternalAnchorLink,
h5:hover .jp-InternalAnchorLink,
h6:hover .jp-InternalAnchorLink {
  visibility: visible;
}

.jp-ThemedContainer .jp-RenderedHTMLCommon kbd {
  background-color: var(--jp-rendermime-table-row-background);
  border: 1px solid var(--jp-border-color0);
  border-bottom-color: var(--jp-border-color2);
  border-radius: 3px;
  box-shadow: inset 0 -1px 0 rgba(0, 0, 0, 0.25);
  display: inline-block;
  font-size: var(--jp-ui-font-size0);
  line-height: 1em;
  padding: 0.2em 0.5em;
}

/* Most direct children of .jp-RenderedHTMLCommon have a margin-bottom of 1.0.
 * At the bottom of cells this is a bit too much as there is also spacing
 * between cells. Going all the way to 0 gets too tight between markdown and
 * code cells.
 */
.jp-RenderedHTMLCommon > *:last-child {
  margin-bottom: 0.5em;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


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





/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTIwOC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQzdWQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7Ozs7Ozs7QUNQQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O0FDem5CQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNaQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL291dHB1dGFyZWEvc3R5bGUvYmFzZS5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9yZW5kZXJtaW1lL3N0eWxlL2Jhc2UuY3NzP2MxODQiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi9yZW5kZXJtaW1lL3N0eWxlL2luZGV4LmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGp1cHl0ZXJsYWIvcmVuZGVybWltZS9zdHlsZS9iYXNlLmNzcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL291dHB1dGFyZWEvc3R5bGUvYmFzZS5jc3M/Y2M0NyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL291dHB1dGFyZWEvc3R5bGUvaW5kZXguanMiXSwic291cmNlc0NvbnRlbnQiOlsiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgTWFpbiBPdXRwdXRBcmVhXG58IE91dHB1dEFyZWEgaGFzIGEgbGlzdCBvZiBPdXRwdXRzXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi5qcC1PdXRwdXRBcmVhIHtcbiAgb3ZlcmZsb3cteTogYXV0bztcbn1cblxuLmpwLU91dHB1dEFyZWEtY2hpbGQge1xuICBkaXNwbGF5OiBmbGV4O1xuICBmbGV4LWRpcmVjdGlvbjogcm93O1xuICB3aWR0aDogMTAwJTtcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcbn1cblxuLmpwLU91dHB1dFByb21wdCB7XG4gIHdpZHRoOiB2YXIoLS1qcC1jZWxsLXByb21wdC13aWR0aCk7XG4gIGZsZXg6IDAgMCB2YXIoLS1qcC1jZWxsLXByb21wdC13aWR0aCk7XG4gIGNvbG9yOiB2YXIoLS1qcC1jZWxsLW91dHByb21wdC1mb250LWNvbG9yKTtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLWNlbGwtcHJvbXB0LWZvbnQtZmFtaWx5KTtcbiAgcGFkZGluZzogdmFyKC0tanAtY29kZS1wYWRkaW5nKTtcbiAgbGV0dGVyLXNwYWNpbmc6IHZhcigtLWpwLWNlbGwtcHJvbXB0LWxldHRlci1zcGFjaW5nKTtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLWNvZGUtbGluZS1oZWlnaHQpO1xuICBmb250LXNpemU6IHZhcigtLWpwLWNvZGUtZm9udC1zaXplKTtcbiAgYm9yZGVyOiB2YXIoLS1qcC1ib3JkZXItd2lkdGgpIHNvbGlkIHRyYW5zcGFyZW50O1xuICBvcGFjaXR5OiB2YXIoLS1qcC1jZWxsLXByb21wdC1vcGFjaXR5KTtcblxuICAvKiBSaWdodCBhbGlnbiBwcm9tcHQgdGV4dCwgZG9uJ3Qgd3JhcCB0byBoYW5kbGUgbGFyZ2UgcHJvbXB0IG51bWJlcnMgKi9cbiAgdGV4dC1hbGlnbjogcmlnaHQ7XG4gIHdoaXRlLXNwYWNlOiBub3dyYXA7XG4gIG92ZXJmbG93OiBoaWRkZW47XG4gIHRleHQtb3ZlcmZsb3c6IGVsbGlwc2lzO1xuXG4gIC8qIERpc2FibGUgdGV4dCBzZWxlY3Rpb24gKi9cbiAgLXdlYmtpdC11c2VyLXNlbGVjdDogbm9uZTtcbiAgLW1vei11c2VyLXNlbGVjdDogbm9uZTtcbiAgLW1zLXVzZXItc2VsZWN0OiBub25lO1xuICB1c2VyLXNlbGVjdDogbm9uZTtcbn1cblxuLmpwLU91dHB1dEFyZWEtb3V0cHV0IHtcbiAgd2lkdGg6IDEwMCU7XG4gIGhlaWdodDogYXV0bztcbiAgb3ZlcmZsb3c6IGF1dG87XG4gIHVzZXItc2VsZWN0OiB0ZXh0O1xuICAtbW96LXVzZXItc2VsZWN0OiB0ZXh0O1xuICAtd2Via2l0LXVzZXItc2VsZWN0OiB0ZXh0O1xuICAtbXMtdXNlci1zZWxlY3Q6IHRleHQ7XG59XG5cbi5qcC1PdXRwdXRBcmVhIC5qcC1SZW5kZXJlZFRleHQge1xuICBwYWRkaW5nLWxlZnQ6IDFjaDtcbn1cblxuLyoqXG4gKiBQcm9tcHQgb3ZlcmxheS5cbiAqL1xuXG4uanAtT3V0cHV0QXJlYS1wcm9tcHRPdmVybGF5IHtcbiAgcG9zaXRpb246IGFic29sdXRlO1xuICB0b3A6IDA7XG4gIHdpZHRoOiB2YXIoLS1qcC1jZWxsLXByb21wdC13aWR0aCk7XG4gIGhlaWdodDogMTAwJTtcbiAgb3BhY2l0eTogMC41O1xuICBkaXNwbGF5OiBmbGV4O1xuICBhbGlnbi1pdGVtczogY2VudGVyO1xuICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjtcbn1cblxuLmpwLU91dHB1dEFyZWEtcHJvbXB0T3ZlcmxheSAuanAtaWNvbi1vdXRwdXQge1xuICBkaXNwbGF5OiBub25lO1xufVxuXG4uanAtT3V0cHV0QXJlYS1wcm9tcHRPdmVybGF5OmhvdmVyIC5qcC1pY29uLW91dHB1dCB7XG4gIGRpc3BsYXk6IGluaXRpYWw7XG59XG5cbi5qcC1PdXRwdXRBcmVhLXByb21wdE92ZXJsYXk6aG92ZXIge1xuICBiYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IyKTtcbiAgYm94LXNoYWRvdzogaW5zZXQgMCAwIDFweCB2YXIoLS1qcC1pbnZlcnNlLWxheW91dC1jb2xvcjApO1xufVxuXG4uanAtT3V0cHV0QXJlYS1jaGlsZCAuanAtT3V0cHV0QXJlYS1vdXRwdXQge1xuICBmbGV4LWdyb3c6IDE7XG4gIGZsZXgtc2hyaW5rOiAxO1xufVxuXG4vKipcbiAqIElzb2xhdGVkIG91dHB1dC5cbiAqL1xuLmpwLU91dHB1dEFyZWEtb3V0cHV0LmpwLW1vZC1pc29sYXRlZCB7XG4gIHdpZHRoOiAxMDAlO1xuICBkaXNwbGF5OiBibG9jaztcbn1cblxuLypcbldoZW4gZHJhZyBldmVudHMgb2NjdXIsIFxcYGxtLW1vZC1vdmVycmlkZS1jdXJzb3JcXGAgaXMgYWRkZWQgdG8gdGhlIGJvZHkuXG5CZWNhdXNlIGlmcmFtZXMgc3RlYWwgYWxsIGN1cnNvciBldmVudHMsIHRoZSBmb2xsb3dpbmcgdHdvIHJ1bGVzIGFyZSBuZWNlc3NhcnlcbnRvIHN1cHByZXNzIHBvaW50ZXIgZXZlbnRzIHdoaWxlIHJlc2l6ZSBkcmFncyBhcmUgb2NjdXJyaW5nLiBUaGVyZSBtYXkgYmUgYVxuYmV0dGVyIHNvbHV0aW9uIHRvIHRoaXMgcHJvYmxlbS5cbiovXG5ib2R5LmxtLW1vZC1vdmVycmlkZS1jdXJzb3IgLmpwLU91dHB1dEFyZWEtb3V0cHV0LmpwLW1vZC1pc29sYXRlZCB7XG4gIHBvc2l0aW9uOiByZWxhdGl2ZTtcbn1cblxuYm9keS5sbS1tb2Qtb3ZlcnJpZGUtY3Vyc29yIC5qcC1PdXRwdXRBcmVhLW91dHB1dC5qcC1tb2QtaXNvbGF0ZWQ6OmJlZm9yZSB7XG4gIGNvbnRlbnQ6ICcnO1xuICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gIHRvcDogMDtcbiAgbGVmdDogMDtcbiAgcmlnaHQ6IDA7XG4gIGJvdHRvbTogMDtcbiAgYmFja2dyb3VuZDogdHJhbnNwYXJlbnQ7XG59XG5cbi8qIHByZSAqL1xuXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQgcHJlIHtcbiAgYm9yZGVyOiBub25lO1xuICBtYXJnaW46IDA7XG4gIHBhZGRpbmc6IDA7XG4gIG92ZXJmbG93LXg6IGF1dG87XG4gIG92ZXJmbG93LXk6IGF1dG87XG4gIHdvcmQtYnJlYWs6IGJyZWFrLWFsbDtcbiAgd29yZC13cmFwOiBicmVhay13b3JkO1xuICB3aGl0ZS1zcGFjZTogcHJlLXdyYXA7XG59XG5cbi8qIHRhYmxlcyAqL1xuXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQuanAtUmVuZGVyZWRIVE1MQ29tbW9uIHRhYmxlIHtcbiAgbWFyZ2luLWxlZnQ6IDA7XG4gIG1hcmdpbi1yaWdodDogMDtcbn1cblxuLyogZGVzY3JpcHRpb24gbGlzdHMgKi9cblxuLmpwLU91dHB1dEFyZWEtb3V0cHV0IGRsLFxuLmpwLU91dHB1dEFyZWEtb3V0cHV0IGR0LFxuLmpwLU91dHB1dEFyZWEtb3V0cHV0IGRkIHtcbiAgZGlzcGxheTogYmxvY2s7XG59XG5cbi5qcC1PdXRwdXRBcmVhLW91dHB1dCBkbCB7XG4gIHdpZHRoOiAxMDAlO1xuICBvdmVyZmxvdzogaGlkZGVuO1xuICBwYWRkaW5nOiAwO1xuICBtYXJnaW46IDA7XG59XG5cbi5qcC1PdXRwdXRBcmVhLW91dHB1dCBkdCB7XG4gIGZvbnQtd2VpZ2h0OiBib2xkO1xuICBmbG9hdDogbGVmdDtcbiAgd2lkdGg6IDIwJTtcbiAgcGFkZGluZzogMDtcbiAgbWFyZ2luOiAwO1xufVxuXG4uanAtT3V0cHV0QXJlYS1vdXRwdXQgZGQge1xuICBmbG9hdDogbGVmdDtcbiAgd2lkdGg6IDgwJTtcbiAgcGFkZGluZzogMDtcbiAgbWFyZ2luOiAwO1xufVxuXG4uanAtVHJpbW1lZE91dHB1dHMtYnV0dG9uIHtcbiAgZGlzcGxheTogaW5saW5lLWZsZXg7XG4gIGFsaWduLWl0ZW1zOiBjZW50ZXI7XG4gIGp1c3RpZnktY29udGVudDogY2VudGVyO1xuICB3aWR0aDogMTAwJTtcbiAgcGFkZGluZzogdmFyKC0tanAtZmxhdC1idXR0b24tcGFkZGluZyk7XG4gIG1hcmdpbjogOHB4IDA7XG4gIG1pbi1oZWlnaHQ6IHZhcigtLWpwLWZsYXQtYnV0dG9uLWhlaWdodCk7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtdWktZm9udC1zaXplMSk7XG4gIGZvbnQtZmFtaWx5OiB2YXIoLS1qcC11aS1mb250LWZhbWlseSk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICBib3JkZXI6IDFweCBzb2xpZCB2YXIoLS1qcC1ib3JkZXItY29sb3IyKTtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWZvbnQtY29sb3IxKTtcbiAgY3Vyc29yOiBwb2ludGVyO1xufVxuXG4uanAtVHJpbW1lZE91dHB1dHMtYnV0dG9uOmhvdmVyIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMik7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG59XG5cbi5qcC1UcmltbWVkT3V0cHV0cy1idXR0b246YWN0aXZlIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMyk7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG59XG5cbi5qcC1UcmltbWVkT3V0cHV0cy1idXR0b246Zm9jdXMtdmlzaWJsZSB7XG4gIG91dGxpbmU6IDFweCBzb2xpZCB2YXIoLS1qcC1icmFuZC1jb2xvcjEpO1xuICBvdXRsaW5lLW9mZnNldDogLTFweDtcbn1cblxuLyogSGlkZSB0aGUgZ3V0dGVyIGluIGNhc2Ugb2ZcbiAqICAtIG5lc3RlZCBvdXRwdXQgYXJlYXMgKGUuZy4gaW4gdGhlIGNhc2Ugb2Ygb3V0cHV0IHdpZGdldHMpXG4gKiAgLSBtaXJyb3JlZCBvdXRwdXQgYXJlYXNcbiAqL1xuLmpwLU91dHB1dEFyZWEgLmpwLU91dHB1dEFyZWEgLmpwLU91dHB1dEFyZWEtcHJvbXB0IHtcbiAgZGlzcGxheTogbm9uZTtcbn1cblxuLyogSGlkZSBlbXB0eSBsaW5lcyBpbiB0aGUgb3V0cHV0IGFyZWEsIGZvciBpbnN0YW5jZSBkdWUgdG8gY2xlYXJlZCB3aWRnZXRzICovXG4uanAtT3V0cHV0QXJlYS1wcm9tcHQ6ZW1wdHkge1xuICBwYWRkaW5nOiAwO1xuICBib3JkZXI6IDA7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgZXhlY3V0ZVJlc3VsdCBpcyBhZGRlZCB0byBhbnkgT3V0cHV0LXJlc3VsdCBmb3IgdGhlIGRpc3BsYXkgb2YgdGhlIG9iamVjdFxufCByZXR1cm5lZCBieSBhIGNlbGxcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLU91dHB1dEFyZWEtb3V0cHV0LmpwLU91dHB1dEFyZWEtZXhlY3V0ZVJlc3VsdCB7XG4gIG1hcmdpbi1sZWZ0OiAwO1xuICB3aWR0aDogMTAwJTtcbiAgZmxleDogMSAxIGF1dG87XG59XG5cbi8qIFRleHQgb3V0cHV0IHdpdGggdGhlIE91dFtdIHByb21wdCBuZWVkcyBhIHRvcCBwYWRkaW5nIHRvIG1hdGNoIHRoZVxuICogYWxpZ25tZW50IG9mIHRoZSBPdXRbXSBwcm9tcHQgaXRzZWxmLlxuICovXG4uanAtT3V0cHV0QXJlYS1leGVjdXRlUmVzdWx0IC5qcC1SZW5kZXJlZFRleHQuanAtT3V0cHV0QXJlYS1vdXRwdXQge1xuICBwYWRkaW5nLXRvcDogdmFyKC0tanAtY29kZS1wYWRkaW5nKTtcbiAgYm9yZGVyLXRvcDogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSBzb2xpZCB0cmFuc3BhcmVudDtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBUaGUgU3RkaW4gb3V0cHV0XG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi5qcC1TdGRpbi1wcm9tcHQge1xuICBjb2xvcjogdmFyKC0tanAtY29udGVudC1mb250LWNvbG9yMCk7XG4gIHBhZGRpbmctcmlnaHQ6IHZhcigtLWpwLWNvZGUtcGFkZGluZyk7XG4gIHZlcnRpY2FsLWFsaWduOiBiYXNlbGluZTtcbiAgZmxleDogMCAwIGF1dG87XG59XG5cbi5qcC1TdGRpbi1pbnB1dCB7XG4gIGZvbnQtZmFtaWx5OiB2YXIoLS1qcC1jb2RlLWZvbnQtZmFtaWx5KTtcbiAgZm9udC1zaXplOiBpbmhlcml0O1xuICBjb2xvcjogaW5oZXJpdDtcbiAgYmFja2dyb3VuZC1jb2xvcjogaW5oZXJpdDtcbiAgd2lkdGg6IDQyJTtcbiAgbWluLXdpZHRoOiAyMDBweDtcblxuICAvKiBtYWtlIHN1cmUgaW5wdXQgYmFzZWxpbmUgYWxpZ25zIHdpdGggcHJvbXB0ICovXG4gIHZlcnRpY2FsLWFsaWduOiBiYXNlbGluZTtcblxuICAvKiBwYWRkaW5nICsgbWFyZ2luID0gMC41ZW0gYmV0d2VlbiBwcm9tcHQgYW5kIGN1cnNvciAqL1xuICBwYWRkaW5nOiAwIDAuMjVlbTtcbiAgbWFyZ2luOiAwIDAuMjVlbTtcbiAgZmxleDogMCAwIDcwJTtcbn1cblxuLmpwLVN0ZGluLWlucHV0OjpwbGFjZWhvbGRlciB7XG4gIG9wYWNpdHk6IDA7XG59XG5cbi5qcC1TdGRpbi1pbnB1dDpmb2N1cyB7XG4gIGJveC1zaGFkb3c6IG5vbmU7XG59XG5cbi5qcC1TdGRpbi1pbnB1dDpmb2N1czo6cGxhY2Vob2xkZXIge1xuICBvcGFjaXR5OiAxO1xufVxuXG4uanAtT3V0cHV0QXJlYS1zdGRpbi1oaWRpbmcge1xuICAvKiBzb2Z0LWhpZGUgdGhlIG91dHB1dCwgcHJlc2VydmluZyBmb2N1cyAqL1xuICBvcGFjaXR5OiAwO1xuICBoZWlnaHQ6IDA7XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgT3V0cHV0IEFyZWEgVmlld1xufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4uanAtTGlua2VkT3V0cHV0VmlldyAuanAtT3V0cHV0QXJlYSB7XG4gIGhlaWdodDogMTAwJTtcbiAgZGlzcGxheTogYmxvY2s7XG59XG5cbi5qcC1MaW5rZWRPdXRwdXRWaWV3IC5qcC1PdXRwdXRBcmVhLWNoaWxkOm9ubHktY2hpbGQge1xuICBoZWlnaHQ6IDEwMCU7XG59XG5cbi5qcC1MaW5rZWRPdXRwdXRWaWV3IC5qcC1PdXRwdXRBcmVhLW91dHB1dDpvbmx5LWNoaWxkIHtcbiAgaGVpZ2h0OiAxMDAlO1xufVxuXG4vKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IFByaW50aW5nXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbkBtZWRpYSBwcmludCB7XG4gIC5qcC1PdXRwdXRBcmVhLWNoaWxkIHtcbiAgICBkaXNwbGF5OiB0YWJsZTtcbiAgICB0YWJsZS1sYXlvdXQ6IGZpeGVkO1xuICAgIGJyZWFrLWluc2lkZTogYXZvaWQtcGFnZTtcbiAgfVxuXG4gIC5qcC1PdXRwdXRBcmVhLXByb21wdCB7XG4gICAgZGlzcGxheTogdGFibGUtY2VsbDtcbiAgICB2ZXJ0aWNhbC1hbGlnbjogdG9wO1xuICB9XG5cbiAgLmpwLU91dHB1dEFyZWEtb3V0cHV0IHtcbiAgICBkaXNwbGF5OiB0YWJsZS1jZWxsO1xuICB9XG59XG5cbi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgTW9iaWxlXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5AbWVkaWEgb25seSBzY3JlZW4gYW5kICh3aWR0aCA8PSA3NjBweCkge1xuICAuanAtT3V0cHV0QXJlYS1jaGlsZCB7XG4gICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgfVxuXG4gIC5qcC1PdXRwdXRQcm9tcHQge1xuICAgIGZsZXg6IDAgMCBhdXRvO1xuICAgIHRleHQtYWxpZ246IGxlZnQ7XG4gIH1cblxuICAuanAtT3V0cHV0QXJlYS1wcm9tcHRPdmVybGF5IHtcbiAgICBkaXNwbGF5OiBub25lO1xuICB9XG59XG5cbi8qIFRyaW1tZWQgb3V0cHV0cyBjb250YWluZXIgKi9cbi5qcC1UcmltbWVkT3V0cHV0cyB7XG4gIC8qIExlZnQtYWxpZ24gdGhlIGJ1dHRvbiB3aXRoaW4gdGhlIG91dHB1dCBhcmVhICovXG4gIHRleHQtYWxpZ246IGxlZnQ7XG59XG5gLCBcIlwiXSk7XG4vLyBFeHBvcnRzXG5leHBvcnQgZGVmYXVsdCBfX19DU1NfTE9BREVSX0VYUE9SVF9fXztcbiIsImltcG9ydCBhcGkgZnJvbSBcIiEuLi8uLi8uLi9zdHlsZS1sb2FkZXIvZGlzdC9ydW50aW1lL2luamVjdFN0eWxlc0ludG9TdHlsZVRhZy5qc1wiO1xuICAgICAgICAgICAgaW1wb3J0IGNvbnRlbnQgZnJvbSBcIiEhLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L2Nqcy5qcyEuL2Jhc2UuY3NzXCI7XG5cbnZhciBvcHRpb25zID0ge307XG5cbm9wdGlvbnMuaW5zZXJ0ID0gXCJoZWFkXCI7XG5vcHRpb25zLnNpbmdsZXRvbiA9IGZhbHNlO1xuXG52YXIgdXBkYXRlID0gYXBpKGNvbnRlbnQsIG9wdGlvbnMpO1xuXG5cblxuZXhwb3J0IGRlZmF1bHQgY29udGVudC5sb2NhbHMgfHwge307IiwiLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb3B5cmlnaHQgKGMpIEp1cHl0ZXIgRGV2ZWxvcG1lbnQgVGVhbS5cbnwgRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLyogVGhpcyBmaWxlIHdhcyBhdXRvLWdlbmVyYXRlZCBieSBlbnN1cmVQYWNrYWdlKCkgaW4gQGp1cHl0ZXJsYWIvYnVpbGR1dGlscyAqL1xuaW1wb3J0ICdAbHVtaW5vL3dpZGdldHMvc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9hcHB1dGlscy9zdHlsZS9pbmRleC5qcyc7XG5pbXBvcnQgJy4vYmFzZS5jc3MnOyIsIi8vIEltcG9ydHNcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9ub1NvdXJjZU1hcHMuanNcIjtcbmltcG9ydCBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL2FwaS5qc1wiO1xudmFyIF9fX0NTU19MT0FERVJfRVhQT1JUX19fID0gX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fKF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18pO1xuLy8gTW9kdWxlXG5fX19DU1NfTE9BREVSX0VYUE9SVF9fXy5wdXNoKFttb2R1bGUuaWQsIGAvKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxufCBEaXN0cmlidXRlZCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIE1vZGlmaWVkIEJTRCBMaWNlbnNlLlxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG4vKi0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tXG58IFJlbmRlcmVkVGV4dFxufC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0qL1xuXG46cm9vdCB7XG4gIC8qIFRoaXMgaXMgdGhlIHBhZGRpbmcgdmFsdWUgdG8gZmlsbCB0aGUgZ2FwcyBiZXR3ZWVuIGxpbmVzIGNvbnRhaW5pbmcgc3BhbnMgd2l0aCBiYWNrZ3JvdW5kIGNvbG9yLiAqL1xuICAtLWpwLXByaXZhdGUtY29kZS1zcGFuLXBhZGRpbmc6IGNhbGMoXG4gICAgKHZhcigtLWpwLWNvZGUtbGluZS1oZWlnaHQpIC0gMSkgKiB2YXIoLS1qcC1jb2RlLWZvbnQtc2l6ZSkgLyAyXG4gICk7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQge1xuICB0ZXh0LWFsaWduOiBsZWZ0O1xuICBwYWRkaW5nLWxlZnQ6IHZhcigtLWpwLWNvZGUtcGFkZGluZyk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC1jb2RlLWxpbmUtaGVpZ2h0KTtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLWNvZGUtZm9udC1mYW1pbHkpO1xufVxuXG4uanAtVGhlbWVkQ29udGFpbmVyIC5qcC1SZW5kZXJlZFRleHQgcHJlLFxuLmpwLVRoZW1lZENvbnRhaW5lciAuanAtUmVuZGVyZWRKYXZhU2NyaXB0IHByZSxcbi5qcC1UaGVtZWRDb250YWluZXIgLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBwcmUge1xuICBjb2xvcjogdmFyKC0tanAtY29udGVudC1mb250LWNvbG9yMSk7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29kZS1mb250LXNpemUpO1xuICBib3JkZXI6IG5vbmU7XG4gIG1hcmdpbjogMDtcbiAgcGFkZGluZzogMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgYVtocmVmXTpsaW5rIHtcbiAgdGV4dC1kZWNvcmF0aW9uOiBub25lO1xuICBjb2xvcjogdmFyKC0tanAtY29udGVudC1saW5rLWNvbG9yKTtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgYVtocmVmXTpob3ZlciB7XG4gIHRleHQtZGVjb3JhdGlvbjogdW5kZXJsaW5lO1xuICBjb2xvcjogdmFyKC0tanAtY29udGVudC1saW5rLWhvdmVyLWNvbG9yLCB2YXIoLS1qcC1jb250ZW50LWxpbmstY29sb3IpKTtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgYVtocmVmXTp2aXNpdGVkIHtcbiAgdGV4dC1kZWNvcmF0aW9uOiBub25lO1xuICBjb2xvcjogdmFyKC0tanAtY29udGVudC1saW5rLXZpc2l0ZWQtY29sb3IsIHZhcigtLWpwLWNvbnRlbnQtbGluay1jb2xvcikpO1xufVxuXG4vKiBjb25zb2xlIGZvcmVncm91bmRzIGFuZCBiYWNrZ3JvdW5kcyAqL1xuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktYmxhY2stZmcge1xuICBjb2xvcjogIzNlNDI0ZDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktcmVkLWZnIHtcbiAgY29sb3I6ICNlNzVjNTg7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLWdyZWVuLWZnIHtcbiAgY29sb3I6ICMwMGEyNTA7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLXllbGxvdy1mZyB7XG4gIGNvbG9yOiAjZGRiNjJiO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ibHVlLWZnIHtcbiAgY29sb3I6ICMyMDhmZmI7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLW1hZ2VudGEtZmcge1xuICBjb2xvcjogI2QxNjBjNDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktY3lhbi1mZyB7XG4gIGNvbG9yOiAjNjBjNmM4O1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS13aGl0ZS1mZyB7XG4gIGNvbG9yOiAjYzVjMWI0O1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ibGFjay1iZyB7XG4gIGJhY2tncm91bmQtY29sb3I6ICMzZTQyNGQ7XG4gIHBhZGRpbmc6IHZhcigtLWpwLXByaXZhdGUtY29kZS1zcGFuLXBhZGRpbmcpIDA7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLXJlZC1iZyB7XG4gIGJhY2tncm91bmQtY29sb3I6ICNlNzVjNTg7XG4gIHBhZGRpbmc6IHZhcigtLWpwLXByaXZhdGUtY29kZS1zcGFuLXBhZGRpbmcpIDA7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLWdyZWVuLWJnIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogIzAwYTI1MDtcbiAgcGFkZGluZzogdmFyKC0tanAtcHJpdmF0ZS1jb2RlLXNwYW4tcGFkZGluZykgMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2kteWVsbG93LWJnIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogI2RkYjYyYjtcbiAgcGFkZGluZzogdmFyKC0tanAtcHJpdmF0ZS1jb2RlLXNwYW4tcGFkZGluZykgMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktYmx1ZS1iZyB7XG4gIGJhY2tncm91bmQtY29sb3I6ICMyMDhmZmI7XG4gIHBhZGRpbmc6IHZhcigtLWpwLXByaXZhdGUtY29kZS1zcGFuLXBhZGRpbmcpIDA7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLW1hZ2VudGEtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjZDE2MGM0O1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1jeWFuLWJnIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogIzYwYzZjODtcbiAgcGFkZGluZzogdmFyKC0tanAtcHJpdmF0ZS1jb2RlLXNwYW4tcGFkZGluZykgMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktd2hpdGUtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjYzVjMWI0O1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ibGFjay1pbnRlbnNlLWZnIHtcbiAgY29sb3I6ICMyODJjMzY7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLXJlZC1pbnRlbnNlLWZnIHtcbiAgY29sb3I6ICNiMjJiMzE7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLWdyZWVuLWludGVuc2UtZmcge1xuICBjb2xvcjogIzAwNzQyNztcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2kteWVsbG93LWludGVuc2UtZmcge1xuICBjb2xvcjogI2IyN2QxMjtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktYmx1ZS1pbnRlbnNlLWZnIHtcbiAgY29sb3I6ICMwMDY1Y2E7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLW1hZ2VudGEtaW50ZW5zZS1mZyB7XG4gIGNvbG9yOiAjYTAzMTk2O1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1jeWFuLWludGVuc2UtZmcge1xuICBjb2xvcjogIzI1OGY4Zjtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktd2hpdGUtaW50ZW5zZS1mZyB7XG4gIGNvbG9yOiAjYTFhNmIyO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ibGFjay1pbnRlbnNlLWJnIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogIzI4MmMzNjtcbiAgcGFkZGluZzogdmFyKC0tanAtcHJpdmF0ZS1jb2RlLXNwYW4tcGFkZGluZykgMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktcmVkLWludGVuc2UtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjYjIyYjMxO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ncmVlbi1pbnRlbnNlLWJnIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogIzAwNzQyNztcbiAgcGFkZGluZzogdmFyKC0tanAtcHJpdmF0ZS1jb2RlLXNwYW4tcGFkZGluZykgMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2kteWVsbG93LWludGVuc2UtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjYjI3ZDEyO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ibHVlLWludGVuc2UtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjMDA2NWNhO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1tYWdlbnRhLWludGVuc2UtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjYTAzMTk2O1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1jeWFuLWludGVuc2UtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjU4ZjhmO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS13aGl0ZS1pbnRlbnNlLWJnIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogI2ExYTZiMjtcbiAgcGFkZGluZzogdmFyKC0tanAtcHJpdmF0ZS1jb2RlLXNwYW4tcGFkZGluZykgMDtcbn1cblxuLmpwLVJlbmRlcmVkVGV4dCBwcmUgLmFuc2ktZGVmYXVsdC1pbnZlcnNlLWZnIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1kZWZhdWx0LWludmVyc2UtYmcge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1pbnZlcnNlLWxheW91dC1jb2xvcjApO1xuICBwYWRkaW5nOiB2YXIoLS1qcC1wcml2YXRlLWNvZGUtc3Bhbi1wYWRkaW5nKSAwO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0IHByZSAuYW5zaS1ib2xkIHtcbiAgZm9udC13ZWlnaHQ6IGJvbGQ7XG59XG5cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLXVuZGVybGluZSB7XG4gIHRleHQtZGVjb3JhdGlvbjogdW5kZXJsaW5lO1xufVxuXG4uanAtUmVuZGVyZWRUZXh0W2RhdGEtbWltZS10eXBlPSdhcHBsaWNhdGlvbi92bmQuanVweXRlci5zdGRlcnInXSB7XG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLXJlbmRlcm1pbWUtZXJyb3ItYmFja2dyb3VuZCk7XG4gIHBhZGRpbmctdG9wOiB2YXIoLS1qcC1jb2RlLXBhZGRpbmcpO1xufVxuXG4vKiBmaXggaWxsZWdpYmxlIHllbGxvdyB0ZXh0IHdpdGggeWVsbG93IGJhY2tncm91bmQgaW4gZXhjZXB0aW9uIHN0YWNrdHJhY2UgKi9cbi5qcC1SZW5kZXJlZFRleHQgcHJlIC5hbnNpLXllbGxvdy1iZy5hbnNpLXllbGxvdy1mZyB7XG4gIGNvbG9yOiBibGFjaztcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBSZW5kZXJlZExhdGV4XG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi5qcC1SZW5kZXJlZExhdGV4IHtcbiAgY29sb3I6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1jb2xvcjEpO1xuICBmb250LXNpemU6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1zaXplMSk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC1jb250ZW50LWxpbmUtaGVpZ2h0KTtcbn1cblxuLyogTGVmdC1qdXN0aWZ5IG91dHB1dHMuKi9cbi5qcC1PdXRwdXRBcmVhLW91dHB1dC5qcC1SZW5kZXJlZExhdGV4IHtcbiAgcGFkZGluZzogdmFyKC0tanAtY29kZS1wYWRkaW5nKTtcbiAgdGV4dC1hbGlnbjogbGVmdDtcbn1cblxuLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBSZW5kZXJlZEhUTUxcbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB7XG4gIGNvbG9yOiB2YXIoLS1qcC1jb250ZW50LWZvbnQtY29sb3IxKTtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1mYW1pbHkpO1xuICBmb250LXNpemU6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1zaXplMSk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC1jb250ZW50LWxpbmUtaGVpZ2h0KTtcblxuICAvKiBHaXZlIGEgYml0IG1vcmUgUiBwYWRkaW5nIG9uIE1hcmtkb3duIHRleHQgdG8ga2VlcCBsaW5lIGxlbmd0aHMgcmVhc29uYWJsZSAqL1xuICBwYWRkaW5nLXJpZ2h0OiAyMHB4O1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIGVtIHtcbiAgZm9udC1zdHlsZTogaXRhbGljO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHN0cm9uZyB7XG4gIGZvbnQtd2VpZ2h0OiBib2xkO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHUge1xuICB0ZXh0LWRlY29yYXRpb246IHVuZGVybGluZTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBhOmxpbmsge1xuICB0ZXh0LWRlY29yYXRpb246IG5vbmU7XG4gIGNvbG9yOiB2YXIoLS1qcC1jb250ZW50LWxpbmstY29sb3IpO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIGE6aG92ZXIge1xuICB0ZXh0LWRlY29yYXRpb246IHVuZGVybGluZTtcbiAgY29sb3I6IHZhcigtLWpwLWNvbnRlbnQtbGluay1ob3Zlci1jb2xvciwgdmFyKC0tanAtY29udGVudC1saW5rLWNvbG9yKSk7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gYTp2aXNpdGVkIHtcbiAgdGV4dC1kZWNvcmF0aW9uOiBub25lO1xuICBjb2xvcjogdmFyKC0tanAtY29udGVudC1saW5rLXZpc2l0ZWQtY29sb3IsIHZhcigtLWpwLWNvbnRlbnQtbGluay1jb2xvcikpO1xufVxuXG4vKiBIZWFkaW5ncyAqL1xuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIGgxLFxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoMixcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDMsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIGg0LFxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoNSxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDYge1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtY29udGVudC1oZWFkaW5nLWxpbmUtaGVpZ2h0KTtcbiAgZm9udC13ZWlnaHQ6IHZhcigtLWpwLWNvbnRlbnQtaGVhZGluZy1mb250LXdlaWdodCk7XG4gIGZvbnQtc3R5bGU6IG5vcm1hbDtcbiAgbWFyZ2luOiB2YXIoLS1qcC1jb250ZW50LWhlYWRpbmctbWFyZ2luLXRvcCkgMFxuICAgIHZhcigtLWpwLWNvbnRlbnQtaGVhZGluZy1tYXJnaW4tYm90dG9tKSAwO1xuICBzY3JvbGwtbWFyZ2luLXRvcDogdmFyKC0tanAtY29udGVudC1oZWFkaW5nLW1hcmdpbi10b3ApO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIGgxOmZpcnN0LWNoaWxkLFxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoMjpmaXJzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDM6Zmlyc3QtY2hpbGQsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIGg0OmZpcnN0LWNoaWxkLFxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoNTpmaXJzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDY6Zmlyc3QtY2hpbGQge1xuICBtYXJnaW4tdG9wOiBjYWxjKDAuNSAqIHZhcigtLWpwLWNvbnRlbnQtaGVhZGluZy1tYXJnaW4tdG9wKSk7XG4gIHNjcm9sbC1tYXJnaW4tdG9wOiBjYWxjKDAuNSAqIHZhcigtLWpwLWNvbnRlbnQtaGVhZGluZy1tYXJnaW4tdG9wKSk7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDE6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDI6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDM6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDQ6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDU6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaDY6bGFzdC1jaGlsZCB7XG4gIG1hcmdpbi1ib3R0b206IGNhbGMoMC41ICogdmFyKC0tanAtY29udGVudC1oZWFkaW5nLW1hcmdpbi1ib3R0b20pKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoMSB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemU1KTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoMiB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemU0KTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoMyB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemUzKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoNCB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemUyKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoNSB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemUxKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBoNiB7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtY29udGVudC1mb250LXNpemUwKTtcbn1cblxuLyogTGlzdHMgKi9cblxuLyogc3R5bGVsaW50LWRpc2FibGUgc2VsZWN0b3ItbWF4LXR5cGUsIHNlbGVjdG9yLW1heC1jb21wb3VuZC1zZWxlY3RvcnMgKi9cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB1bDpub3QoLmxpc3QtaW5saW5lKSxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gb2w6bm90KC5saXN0LWlubGluZSkge1xuICBwYWRkaW5nLWxlZnQ6IDJlbTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB1bCB7XG4gIGxpc3Qtc3R5bGU6IGRpc2M7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdWwgdWwge1xuICBsaXN0LXN0eWxlOiBzcXVhcmU7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdWwgdWwgdWwge1xuICBsaXN0LXN0eWxlOiBjaXJjbGU7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gb2wge1xuICBsaXN0LXN0eWxlOiBkZWNpbWFsO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIG9sIG9sIHtcbiAgbGlzdC1zdHlsZTogdXBwZXItYWxwaGE7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gb2wgb2wgb2wge1xuICBsaXN0LXN0eWxlOiBsb3dlci1hbHBoYTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBvbCBvbCBvbCBvbCB7XG4gIGxpc3Qtc3R5bGU6IGxvd2VyLXJvbWFuO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIG9sIG9sIG9sIG9sIG9sIHtcbiAgbGlzdC1zdHlsZTogZGVjaW1hbDtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBvbCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdWwge1xuICBtYXJnaW4tYm90dG9tOiAxZW07XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdWwgdWwsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHVsIG9sLFxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBvbCB1bCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gb2wgb2wge1xuICBtYXJnaW4tYm90dG9tOiAwO1xufVxuXG4vKiBzdHlsZWxpbnQtZW5hYmxlIHNlbGVjdG9yLW1heC10eXBlLCBzZWxlY3Rvci1tYXgtY29tcG91bmQtc2VsZWN0b3JzICovXG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaHIge1xuICBjb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMik7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWJvcmRlci1jb2xvcjEpO1xuICBtYXJnaW4tdG9wOiAxZW07XG4gIG1hcmdpbi1ib3R0b206IDFlbTtcbn1cblxuLmpwLVRoZW1lZENvbnRhaW5lciAuanAtUmVuZGVyZWRIVE1MQ29tbW9uID4gcHJlIHtcbiAgbWFyZ2luOiAxLjVlbSAyZW07XG59XG5cbi5qcC1UaGVtZWRDb250YWluZXIgLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBwcmUsXG4uanAtVGhlbWVkQ29udGFpbmVyIC5qcC1SZW5kZXJlZEhUTUxDb21tb24gY29kZSB7XG4gIGJvcmRlcjogMDtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMCk7XG4gIGNvbG9yOiB2YXIoLS1qcC1jb250ZW50LWZvbnQtY29sb3IxKTtcbiAgZm9udC1mYW1pbHk6IHZhcigtLWpwLWNvZGUtZm9udC1mYW1pbHkpO1xuICBmb250LXNpemU6IGluaGVyaXQ7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC1jb2RlLWxpbmUtaGVpZ2h0KTtcbiAgcGFkZGluZzogMDtcbiAgd2hpdGUtc3BhY2U6IHByZS13cmFwO1xufVxuXG4uanAtVGhlbWVkQ29udGFpbmVyIC5qcC1SZW5kZXJlZEhUTUxDb21tb24gOm5vdChwcmUpID4gY29kZSB7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjIpO1xuICBwYWRkaW5nOiAxcHggNXB4O1xufVxuXG4vKiBUYWJsZXMgKi9cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB0YWJsZSB7XG4gIGJvcmRlci1jb2xsYXBzZTogY29sbGFwc2U7XG4gIGJvcmRlci1zcGFjaW5nOiAwO1xuICBib3JkZXI6IG5vbmU7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMSk7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtdWktZm9udC1zaXplMSk7XG4gIHRhYmxlLWxheW91dDogZml4ZWQ7XG4gIG1hcmdpbi1sZWZ0OiBhdXRvO1xuICBtYXJnaW4tYm90dG9tOiAxZW07XG4gIG1hcmdpbi1yaWdodDogYXV0bztcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB0aGVhZCB7XG4gIGJvcmRlci1ib3R0b206IHZhcigtLWpwLWJvcmRlci13aWR0aCkgc29saWQgdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG4gIHZlcnRpY2FsLWFsaWduOiBib3R0b207XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdGQsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHRoLFxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB0ciB7XG4gIHZlcnRpY2FsLWFsaWduOiBtaWRkbGU7XG4gIHBhZGRpbmc6IDAuNWVtO1xuICBsaW5lLWhlaWdodDogbm9ybWFsO1xuICB3aGl0ZS1zcGFjZTogbm9ybWFsO1xuICBtYXgtd2lkdGg6IG5vbmU7XG4gIGJvcmRlcjogbm9uZTtcbn1cblxuLmpwLVJlbmRlcmVkTWFya2Rvd24uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHRkLFxuLmpwLVJlbmRlcmVkTWFya2Rvd24uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHRoIHtcbiAgbWF4LXdpZHRoOiBub25lO1xufVxuXG46bm90KC5qcC1SZW5kZXJlZE1hcmtkb3duKS5qcC1SZW5kZXJlZEhUTUxDb21tb24gdGQsXG46bm90KC5qcC1SZW5kZXJlZE1hcmtkb3duKS5qcC1SZW5kZXJlZEhUTUxDb21tb24gdGgsXG46bm90KC5qcC1SZW5kZXJlZE1hcmtkb3duKS5qcC1SZW5kZXJlZEhUTUxDb21tb24gdHIge1xuICB0ZXh0LWFsaWduOiByaWdodDtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiB0aCB7XG4gIGZvbnQtd2VpZ2h0OiBib2xkO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHRib2R5IHRyOm50aC1jaGlsZChvZGQpIHtcbiAgYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMCk7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdGJvZHkgdHI6bnRoLWNoaWxkKGV2ZW4pIHtcbiAgYmFja2dyb3VuZDogdmFyKC0tanAtcmVuZGVybWltZS10YWJsZS1yb3ctYmFja2dyb3VuZCk7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gdGJvZHkgdHI6aG92ZXIge1xuICBiYWNrZ3JvdW5kOiB2YXIoLS1qcC1yZW5kZXJtaW1lLXRhYmxlLXJvdy1ob3Zlci1iYWNrZ3JvdW5kKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBwIHtcbiAgdGV4dC1hbGlnbjogbGVmdDtcbiAgbWFyZ2luOiAwO1xuICBtYXJnaW4tYm90dG9tOiAxZW07XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gaW1nIHtcbiAgLW1vei1mb3JjZS1icm9rZW4taW1hZ2UtaWNvbjogMTtcbn1cblxuLyogUmVzdHJpY3QgdG8gZGlyZWN0IGNoaWxkcmVuIGFzIG90aGVyIGltYWdlcyBjb3VsZCBiZSBuZXN0ZWQgaW4gb3RoZXIgY29udGVudC4gKi9cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gPiBpbWcge1xuICBkaXNwbGF5OiBibG9jaztcbiAgbWFyZ2luLWxlZnQ6IDA7XG4gIG1hcmdpbi1yaWdodDogMDtcbiAgbWFyZ2luLWJvdHRvbTogMWVtO1xufVxuXG4vKiBDaGFuZ2UgY29sb3IgYmVoaW5kIHRyYW5zcGFyZW50IGltYWdlcyBpZiB0aGV5IG5lZWQgaXQuLi4gKi9cbltkYXRhLWpwLXRoZW1lLWxpZ2h0PSdmYWxzZSddIC5qcC1SZW5kZXJlZEltYWdlIGltZy5qcC1uZWVkcy1saWdodC1iYWNrZ3JvdW5kIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtaW52ZXJzZS1sYXlvdXQtY29sb3IxKTtcbn1cblxuW2RhdGEtanAtdGhlbWUtbGlnaHQ9J3RydWUnXSAuanAtUmVuZGVyZWRJbWFnZSBpbWcuanAtbmVlZHMtZGFyay1iYWNrZ3JvdW5kIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtaW52ZXJzZS1sYXlvdXQtY29sb3IxKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBpbWcsXG4uanAtUmVuZGVyZWRJbWFnZSBpbWcsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHN2Zyxcbi5qcC1SZW5kZXJlZFNWRyBzdmcge1xuICBtYXgtd2lkdGg6IDEwMCU7XG4gIGhlaWdodDogYXV0bztcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBpbWcuanAtbW9kLXVuY29uZmluZWQsXG4uanAtUmVuZGVyZWRJbWFnZSBpbWcuanAtbW9kLXVuY29uZmluZWQsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIHN2Zy5qcC1tb2QtdW5jb25maW5lZCxcbi5qcC1SZW5kZXJlZFNWRyBzdmcuanAtbW9kLXVuY29uZmluZWQge1xuICBtYXgtd2lkdGg6IG5vbmU7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0IHtcbiAgcGFkZGluZzogdmFyKC0tanAtbm90ZWJvb2stcGFkZGluZyk7XG4gIGJvcmRlcjogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSBzb2xpZCB0cmFuc3BhcmVudDtcbiAgYm9yZGVyLXJhZGl1czogdmFyKC0tanAtYm9yZGVyLXJhZGl1cyk7XG4gIG1hcmdpbi1ib3R0b206IDFlbTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtaW5mbyB7XG4gIGNvbG9yOiB2YXIoLS1qcC1pbmZvLWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWluZm8tY29sb3IzKTtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1pbmZvLWNvbG9yMik7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0LWluZm8gaHIge1xuICBib3JkZXItY29sb3I6IHZhcigtLWpwLWluZm8tY29sb3IzKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtaW5mbyA+IHA6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0LWluZm8gPiB1bDpsYXN0LWNoaWxkIHtcbiAgbWFyZ2luLWJvdHRvbTogMDtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtd2FybmluZyB7XG4gIGNvbG9yOiB2YXIoLS1qcC13YXJuLWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXdhcm4tY29sb3IzKTtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC13YXJuLWNvbG9yMik7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0LXdhcm5pbmcgaHIge1xuICBib3JkZXItY29sb3I6IHZhcigtLWpwLXdhcm4tY29sb3IzKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtd2FybmluZyA+IHA6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0LXdhcm5pbmcgPiB1bDpsYXN0LWNoaWxkIHtcbiAgbWFyZ2luLWJvdHRvbTogMDtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtc3VjY2VzcyB7XG4gIGNvbG9yOiB2YXIoLS1qcC1zdWNjZXNzLWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXN1Y2Nlc3MtY29sb3IzKTtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1zdWNjZXNzLWNvbG9yMik7XG59XG5cbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0LXN1Y2Nlc3MgaHIge1xuICBib3JkZXItY29sb3I6IHZhcigtLWpwLXN1Y2Nlc3MtY29sb3IzKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtc3VjY2VzcyA+IHA6bGFzdC1jaGlsZCxcbi5qcC1SZW5kZXJlZEhUTUxDb21tb24gLmFsZXJ0LXN1Y2Nlc3MgPiB1bDpsYXN0LWNoaWxkIHtcbiAgbWFyZ2luLWJvdHRvbTogMDtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtZGFuZ2VyIHtcbiAgY29sb3I6IHZhcigtLWpwLWVycm9yLWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWVycm9yLWNvbG9yMyk7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtZXJyb3ItY29sb3IyKTtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiAuYWxlcnQtZGFuZ2VyIGhyIHtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1lcnJvci1jb2xvcjMpO1xufVxuXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIC5hbGVydC1kYW5nZXIgPiBwOmxhc3QtY2hpbGQsXG4uanAtUmVuZGVyZWRIVE1MQ29tbW9uIC5hbGVydC1kYW5nZXIgPiB1bDpsYXN0LWNoaWxkIHtcbiAgbWFyZ2luLWJvdHRvbTogMDtcbn1cblxuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBibG9ja3F1b3RlIHtcbiAgbWFyZ2luOiAxZW0gMmVtO1xuICBwYWRkaW5nOiAwIDFlbTtcbiAgYm9yZGVyLWxlZnQ6IDVweCBzb2xpZCB2YXIoLS1qcC1ib3JkZXItY29sb3IyKTtcbn1cblxuYS5qcC1JbnRlcm5hbEFuY2hvckxpbmsge1xuICB2aXNpYmlsaXR5OiBoaWRkZW47XG4gIG1hcmdpbi1sZWZ0OiA4cHg7XG4gIGNvbG9yOiB2YXIoLS1tZC1ibHVlLTgwMCwgIzE1NjVjMCk7XG59XG5cbmgxOmhvdmVyIC5qcC1JbnRlcm5hbEFuY2hvckxpbmssXG5oMjpob3ZlciAuanAtSW50ZXJuYWxBbmNob3JMaW5rLFxuaDM6aG92ZXIgLmpwLUludGVybmFsQW5jaG9yTGluayxcbmg0OmhvdmVyIC5qcC1JbnRlcm5hbEFuY2hvckxpbmssXG5oNTpob3ZlciAuanAtSW50ZXJuYWxBbmNob3JMaW5rLFxuaDY6aG92ZXIgLmpwLUludGVybmFsQW5jaG9yTGluayB7XG4gIHZpc2liaWxpdHk6IHZpc2libGU7XG59XG5cbi5qcC1UaGVtZWRDb250YWluZXIgLmpwLVJlbmRlcmVkSFRNTENvbW1vbiBrYmQge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1yZW5kZXJtaW1lLXRhYmxlLXJvdy1iYWNrZ3JvdW5kKTtcbiAgYm9yZGVyOiAxcHggc29saWQgdmFyKC0tanAtYm9yZGVyLWNvbG9yMCk7XG4gIGJvcmRlci1ib3R0b20tY29sb3I6IHZhcigtLWpwLWJvcmRlci1jb2xvcjIpO1xuICBib3JkZXItcmFkaXVzOiAzcHg7XG4gIGJveC1zaGFkb3c6IGluc2V0IDAgLTFweCAwIHJnYmEoMCwgMCwgMCwgMC4yNSk7XG4gIGRpc3BsYXk6IGlubGluZS1ibG9jaztcbiAgZm9udC1zaXplOiB2YXIoLS1qcC11aS1mb250LXNpemUwKTtcbiAgbGluZS1oZWlnaHQ6IDFlbTtcbiAgcGFkZGluZzogMC4yZW0gMC41ZW07XG59XG5cbi8qIE1vc3QgZGlyZWN0IGNoaWxkcmVuIG9mIC5qcC1SZW5kZXJlZEhUTUxDb21tb24gaGF2ZSBhIG1hcmdpbi1ib3R0b20gb2YgMS4wLlxuICogQXQgdGhlIGJvdHRvbSBvZiBjZWxscyB0aGlzIGlzIGEgYml0IHRvbyBtdWNoIGFzIHRoZXJlIGlzIGFsc28gc3BhY2luZ1xuICogYmV0d2VlbiBjZWxscy4gR29pbmcgYWxsIHRoZSB3YXkgdG8gMCBnZXRzIHRvbyB0aWdodCBiZXR3ZWVuIG1hcmtkb3duIGFuZFxuICogY29kZSBjZWxscy5cbiAqL1xuLmpwLVJlbmRlcmVkSFRNTENvbW1vbiA+ICo6bGFzdC1jaGlsZCB7XG4gIG1hcmdpbi1ib3R0b206IDAuNWVtO1xufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCJpbXBvcnQgYXBpIGZyb20gXCIhLi4vLi4vLi4vc3R5bGUtbG9hZGVyL2Rpc3QvcnVudGltZS9pbmplY3RTdHlsZXNJbnRvU3R5bGVUYWcuanNcIjtcbiAgICAgICAgICAgIGltcG9ydCBjb250ZW50IGZyb20gXCIhIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi9iYXNlLmNzc1wiO1xuXG52YXIgb3B0aW9ucyA9IHt9O1xuXG5vcHRpb25zLmluc2VydCA9IFwiaGVhZFwiO1xub3B0aW9ucy5zaW5nbGV0b24gPSBmYWxzZTtcblxudmFyIHVwZGF0ZSA9IGFwaShjb250ZW50LCBvcHRpb25zKTtcblxuXG5cbmV4cG9ydCBkZWZhdWx0IGNvbnRlbnQubG9jYWxzIHx8IHt9OyIsIi8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qIFRoaXMgZmlsZSB3YXMgYXV0by1nZW5lcmF0ZWQgYnkgZW5zdXJlUGFja2FnZSgpIGluIEBqdXB5dGVybGFiL2J1aWxkdXRpbHMgKi9cbmltcG9ydCAnQGx1bWluby93aWRnZXRzL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnQGp1cHl0ZXJsYWIvYXBwdXRpbHMvc3R5bGUvaW5kZXguanMnO1xuaW1wb3J0ICdAanVweXRlcmxhYi9yZW5kZXJtaW1lL3N0eWxlL2luZGV4LmpzJztcbmltcG9ydCAnLi9iYXNlLmNzcyc7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==