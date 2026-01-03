"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5646],{

/***/ 42525
(module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   A: () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(74608);
/* harmony import */ var _css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(87249);
/* harmony import */ var _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _css_loader_dist_cjs_js_lumino_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(93044);
/* harmony import */ var _css_loader_dist_cjs_js_nouislider_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(61446);
/* harmony import */ var _css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(25724);
/* harmony import */ var _css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_4__);
// Imports





var ___CSS_LOADER_URL_IMPORT_0___ = new URL(/* asset import */ __webpack_require__(22426), __webpack_require__.b);
var ___CSS_LOADER_EXPORT___ = _css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_css_loader_dist_runtime_noSourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_lumino_css__WEBPACK_IMPORTED_MODULE_2__/* ["default"] */ .A);
___CSS_LOADER_EXPORT___.i(_css_loader_dist_cjs_js_nouislider_css__WEBPACK_IMPORTED_MODULE_3__/* ["default"] */ .A);
var ___CSS_LOADER_URL_REPLACEMENT_0___ = _css_loader_dist_runtime_getUrl_js__WEBPACK_IMPORTED_MODULE_4___default()(___CSS_LOADER_URL_IMPORT_0___);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/* Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */

/*
 * We assume that the CSS variables in
 * https://github.com/jupyterlab/jupyterlab/blob/master/src/default-theme/variables.css
 * have been defined.
 */

:root {
  --jp-widgets-color: var(--jp-content-font-color1);
  --jp-widgets-label-color: var(--jp-widgets-color);
  --jp-widgets-readout-color: var(--jp-widgets-color);
  --jp-widgets-font-size: var(--jp-ui-font-size1);
  --jp-widgets-margin: 2px;
  --jp-widgets-inline-height: 28px;
  --jp-widgets-inline-width: 300px;
  --jp-widgets-inline-width-short: calc(
    var(--jp-widgets-inline-width) / 2 - var(--jp-widgets-margin)
  );
  --jp-widgets-inline-width-tiny: calc(
    var(--jp-widgets-inline-width-short) / 2 - var(--jp-widgets-margin)
  );
  --jp-widgets-inline-margin: 4px; /* margin between inline elements */
  --jp-widgets-inline-label-width: 80px;
  --jp-widgets-border-width: var(--jp-border-width);
  --jp-widgets-vertical-height: 200px;
  --jp-widgets-horizontal-tab-height: 24px;
  --jp-widgets-horizontal-tab-width: 144px;
  --jp-widgets-horizontal-tab-top-border: 2px;
  --jp-widgets-progress-thickness: 20px;
  --jp-widgets-container-padding: 15px;
  --jp-widgets-input-padding: 4px;
  --jp-widgets-radio-item-height-adjustment: 8px;
  --jp-widgets-radio-item-height: calc(
    var(--jp-widgets-inline-height) -
      var(--jp-widgets-radio-item-height-adjustment)
  );
  --jp-widgets-slider-track-thickness: 4px;
  --jp-widgets-slider-border-width: var(--jp-widgets-border-width);
  --jp-widgets-slider-handle-size: 16px;
  --jp-widgets-slider-handle-border-color: var(--jp-border-color1);
  --jp-widgets-slider-handle-background-color: var(--jp-layout-color1);
  --jp-widgets-slider-active-handle-color: var(--jp-brand-color1);
  --jp-widgets-menu-item-height: 24px;
  --jp-widgets-dropdown-arrow: url(${___CSS_LOADER_URL_REPLACEMENT_0___});
  --jp-widgets-input-color: var(--jp-ui-font-color1);
  --jp-widgets-input-background-color: var(--jp-layout-color1);
  --jp-widgets-input-border-color: var(--jp-border-color1);
  --jp-widgets-input-focus-border-color: var(--jp-brand-color2);
  --jp-widgets-input-border-width: var(--jp-widgets-border-width);
  --jp-widgets-disabled-opacity: 0.6;

  /* From Material Design Lite */
  --md-shadow-key-umbra-opacity: 0.2;
  --md-shadow-key-penumbra-opacity: 0.14;
  --md-shadow-ambient-shadow-opacity: 0.12;
}

.jupyter-widgets {
  margin: var(--jp-widgets-margin);
  box-sizing: border-box;
  color: var(--jp-widgets-color);
  overflow: visible;
}

.jp-Output-result > .jupyter-widgets {
  margin-left: 0;
  margin-right: 0;
}

/* vbox and hbox */

/* <DEPRECATED> */
.widget-inline-hbox, /* </DEPRECATED> */
 .jupyter-widget-inline-hbox {
  /* Horizontal widgets */
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: baseline;
}

/* <DEPRECATED> */
.widget-inline-vbox, /* </DEPRECATED> */
 .jupyter-widget-inline-vbox {
  /* Vertical Widgets */
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* <DEPRECATED> */
.widget-box, /* </DEPRECATED> */
.jupyter-widget-box {
  box-sizing: border-box;
  display: flex;
  margin: 0;
  overflow: auto;
}

/* <DEPRECATED> */
.widget-gridbox, /* </DEPRECATED> */
.jupyter-widget-gridbox {
  box-sizing: border-box;
  display: grid;
  margin: 0;
  overflow: auto;
}

/* <DEPRECATED> */
.widget-hbox, /* </DEPRECATED> */
.jupyter-widget-hbox {
  flex-direction: row;
}

/* <DEPRECATED> */
.widget-vbox, /* </DEPRECATED> */
.jupyter-widget-vbox {
  flex-direction: column;
}

/* General Tags Styling */

.jupyter-widget-tagsinput {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
  overflow: auto;

  cursor: text;
}

.jupyter-widget-tag {
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 0px;
  padding-bottom: 0px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  font-size: var(--jp-widgets-font-size);

  height: calc(var(--jp-widgets-inline-height) - 2px);
  border: 0px solid;
  line-height: calc(var(--jp-widgets-inline-height) - 2px);
  box-shadow: none;

  color: var(--jp-ui-font-color1);
  background-color: var(--jp-layout-color2);
  border-color: var(--jp-border-color2);
  border: none;
  user-select: none;

  cursor: grab;
  transition: margin-left 200ms;
  margin: 1px 1px 1px 1px;
}

.jupyter-widget-tag.mod-active {
  /* MD Lite 4dp shadow */
  box-shadow: 0 4px 5px 0 rgba(0, 0, 0, var(--md-shadow-key-penumbra-opacity)),
    0 1px 10px 0 rgba(0, 0, 0, var(--md-shadow-ambient-shadow-opacity)),
    0 2px 4px -1px rgba(0, 0, 0, var(--md-shadow-key-umbra-opacity));
  color: var(--jp-ui-font-color1);
  background-color: var(--jp-layout-color3);
}

.jupyter-widget-colortag {
  color: var(--jp-inverse-ui-font-color1);
}

.jupyter-widget-colortag.mod-active {
  color: var(--jp-inverse-ui-font-color0);
}

.jupyter-widget-taginput {
  color: var(--jp-ui-font-color0);
  background-color: var(--jp-layout-color0);

  cursor: text;
  text-align: left;
}

.jupyter-widget-taginput:focus {
  outline: none;
}

.jupyter-widget-tag-close {
  margin-left: var(--jp-widgets-inline-margin);
  padding: 2px 0px 2px 2px;
}

.jupyter-widget-tag-close:hover {
  cursor: pointer;
}

/* Tag "Primary" Styling */

.jupyter-widget-tag.mod-primary {
  color: var(--jp-inverse-ui-font-color1);
  background-color: var(--jp-brand-color1);
}

.jupyter-widget-tag.mod-primary.mod-active {
  color: var(--jp-inverse-ui-font-color0);
  background-color: var(--jp-brand-color0);
}

/* Tag "Success" Styling */

.jupyter-widget-tag.mod-success {
  color: var(--jp-inverse-ui-font-color1);
  background-color: var(--jp-success-color1);
}

.jupyter-widget-tag.mod-success.mod-active {
  color: var(--jp-inverse-ui-font-color0);
  background-color: var(--jp-success-color0);
}

/* Tag "Info" Styling */

.jupyter-widget-tag.mod-info {
  color: var(--jp-inverse-ui-font-color1);
  background-color: var(--jp-info-color1);
}

.jupyter-widget-tag.mod-info.mod-active {
  color: var(--jp-inverse-ui-font-color0);
  background-color: var(--jp-info-color0);
}

/* Tag "Warning" Styling */

.jupyter-widget-tag.mod-warning {
  color: var(--jp-inverse-ui-font-color1);
  background-color: var(--jp-warn-color1);
}

.jupyter-widget-tag.mod-warning.mod-active {
  color: var(--jp-inverse-ui-font-color0);
  background-color: var(--jp-warn-color0);
}

/* Tag "Danger" Styling */

.jupyter-widget-tag.mod-danger {
  color: var(--jp-inverse-ui-font-color1);
  background-color: var(--jp-error-color1);
}

.jupyter-widget-tag.mod-danger.mod-active {
  color: var(--jp-inverse-ui-font-color0);
  background-color: var(--jp-error-color0);
}

/* General Button Styling */

.jupyter-button {
  padding-left: 10px;
  padding-right: 10px;
  padding-top: 0px;
  padding-bottom: 0px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  font-size: var(--jp-widgets-font-size);
  cursor: pointer;

  height: var(--jp-widgets-inline-height);
  border: 0px solid;
  line-height: var(--jp-widgets-inline-height);
  box-shadow: none;

  color: var(--jp-ui-font-color1);
  background-color: var(--jp-layout-color2);
  border-color: var(--jp-border-color2);
  border: none;
  user-select: none;
}

.jupyter-button i.fa {
  margin-right: var(--jp-widgets-inline-margin);
  pointer-events: none;
}

.jupyter-button:empty:before {
  content: '\\200b'; /* zero-width space */
}

.jupyter-widgets.jupyter-button:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

.jupyter-button i.fa.center {
  margin-right: 0;
}

.jupyter-button:hover:enabled,
.jupyter-button:focus:enabled {
  /* MD Lite 2dp shadow */
  box-shadow: 0 2px 2px 0 rgba(0, 0, 0, var(--md-shadow-key-penumbra-opacity)),
    0 3px 1px -2px rgba(0, 0, 0, var(--md-shadow-key-umbra-opacity)),
    0 1px 5px 0 rgba(0, 0, 0, var(--md-shadow-ambient-shadow-opacity));
}

.jupyter-button:active,
.jupyter-button.mod-active {
  /* MD Lite 4dp shadow */
  box-shadow: 0 4px 5px 0 rgba(0, 0, 0, var(--md-shadow-key-penumbra-opacity)),
    0 1px 10px 0 rgba(0, 0, 0, var(--md-shadow-ambient-shadow-opacity)),
    0 2px 4px -1px rgba(0, 0, 0, var(--md-shadow-key-umbra-opacity));
  color: var(--jp-ui-font-color1);
  background-color: var(--jp-layout-color3);
}

.jupyter-button:focus:enabled {
  outline: 1px solid var(--jp-widgets-input-focus-border-color);
}

/* Button "Primary" Styling */

.jupyter-button.mod-primary {
  color: var(--jp-ui-inverse-font-color1);
  background-color: var(--jp-brand-color1);
}

.jupyter-button.mod-primary.mod-active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-brand-color0);
}

.jupyter-button.mod-primary:active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-brand-color0);
}

/* Button "Success" Styling */

.jupyter-button.mod-success {
  color: var(--jp-ui-inverse-font-color1);
  background-color: var(--jp-success-color1);
}

.jupyter-button.mod-success.mod-active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-success-color0);
}

.jupyter-button.mod-success:active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-success-color0);
}

/* Button "Info" Styling */

.jupyter-button.mod-info {
  color: var(--jp-ui-inverse-font-color1);
  background-color: var(--jp-info-color1);
}

.jupyter-button.mod-info.mod-active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-info-color0);
}

.jupyter-button.mod-info:active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-info-color0);
}

/* Button "Warning" Styling */

.jupyter-button.mod-warning {
  color: var(--jp-ui-inverse-font-color1);
  background-color: var(--jp-warn-color1);
}

.jupyter-button.mod-warning.mod-active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-warn-color0);
}

.jupyter-button.mod-warning:active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-warn-color0);
}

/* Button "Danger" Styling */

.jupyter-button.mod-danger {
  color: var(--jp-ui-inverse-font-color1);
  background-color: var(--jp-error-color1);
}

.jupyter-button.mod-danger.mod-active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-error-color0);
}

.jupyter-button.mod-danger:active {
  color: var(--jp-ui-inverse-font-color0);
  background-color: var(--jp-error-color0);
}

/* Widget Button, Widget Toggle Button, Widget Upload */

/* <DEPRECATED> */
.widget-button, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-toggle-button, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-upload, /* </DEPRECATED> */
.jupyter-widget-button,
.jupyter-widget-toggle-button,
.jupyter-widget-upload {
  width: var(--jp-widgets-inline-width-short);
}

/* Widget Label Styling */

/* Override Bootstrap label css */
.jupyter-widgets label {
  margin-bottom: initial;
}

/* <DEPRECATED> */
.widget-label-basic, /* </DEPRECATED> */
.jupyter-widget-label-basic {
  /* Basic Label */
  color: var(--jp-widgets-label-color);
  font-size: var(--jp-widgets-font-size);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-label, /* </DEPRECATED> */
.jupyter-widget-label {
  /* Label */
  color: var(--jp-widgets-label-color);
  font-size: var(--jp-widgets-font-size);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-inline-hbox .widget-label, /* </DEPRECATED> */
.jupyter-widget-inline-hbox .jupyter-widget-label {
  /* Horizontal Widget Label */
  color: var(--jp-widgets-label-color);
  text-align: right;
  margin-right: calc(var(--jp-widgets-inline-margin) * 2);
  width: var(--jp-widgets-inline-label-width);
  flex-shrink: 0;
}

/* <DEPRECATED> */
.widget-inline-vbox .widget-label, /* </DEPRECATED> */
.jupyter-widget-inline-vbox .jupyter-widget-label {
  /* Vertical Widget Label */
  color: var(--jp-widgets-label-color);
  text-align: center;
  line-height: var(--jp-widgets-inline-height);
}

/* Widget Readout Styling */

/* <DEPRECATED> */
.widget-readout, /* </DEPRECATED> */
.jupyter-widget-readout {
  color: var(--jp-widgets-readout-color);
  font-size: var(--jp-widgets-font-size);
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
  overflow: hidden;
  white-space: nowrap;
  text-align: center;
}

/* <DEPRECATED> */
.widget-readout.overflow, /* </DEPRECATED> */
.jupyter-widget-readout.overflow {
  /* Overflowing Readout */

  /* From Material Design Lite
        shadow-key-umbra-opacity: 0.2;
        shadow-key-penumbra-opacity: 0.14;
        shadow-ambient-shadow-opacity: 0.12;
     */
  -webkit-box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.2),
    0 3px 1px -2px rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12);

  -moz-box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.2),
    0 3px 1px -2px rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12);

  box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.2), 0 3px 1px -2px rgba(0, 0, 0, 0.14),
    0 1px 5px 0 rgba(0, 0, 0, 0.12);
}

/* <DEPRECATED> */
.widget-inline-hbox .widget-readout, /* </DEPRECATED> */
.jupyter-widget-inline-hbox .jupyter-widget-readout {
  /* Horizontal Readout */
  text-align: center;
  max-width: var(--jp-widgets-inline-width-short);
  min-width: var(--jp-widgets-inline-width-tiny);
  margin-left: var(--jp-widgets-inline-margin);
}

/* <DEPRECATED> */
.widget-inline-vbox .widget-readout, /* </DEPRECATED> */
.jupyter-widget-inline-vbox .jupyter-widget-readout {
  /* Vertical Readout */
  margin-top: var(--jp-widgets-inline-margin);
  /* as wide as the widget */
  width: inherit;
}

/* Widget Checkbox Styling */

/* <DEPRECATED> */
.widget-checkbox, /* </DEPRECATED> */
.jupyter-widget-checkbox {
  width: var(--jp-widgets-inline-width);
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-checkbox input[type='checkbox'], /* </DEPRECATED> */
.jupyter-widget-checkbox input[type='checkbox'] {
  margin: 0px calc(var(--jp-widgets-inline-margin) * 2) 0px 0px;
  line-height: var(--jp-widgets-inline-height);
  font-size: large;
  flex-grow: 1;
  flex-shrink: 0;
  align-self: center;
}

/* Widget Valid Styling */

/* <DEPRECATED> */
.widget-valid, /* </DEPRECATED> */
.jupyter-widget-valid {
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
  width: var(--jp-widgets-inline-width-short);
  font-size: var(--jp-widgets-font-size);
}

/* <DEPRECATED> */
.widget-valid i, /* </DEPRECATED> */
.jupyter-widget-valid i {
  line-height: var(--jp-widgets-inline-height);
  margin-right: var(--jp-widgets-inline-margin);
  margin-left: var(--jp-widgets-inline-margin);
}

/* <DEPRECATED> */
.widget-valid.mod-valid i, /* </DEPRECATED> */
.jupyter-widget-valid.mod-valid i {
  color: green;
}

/* <DEPRECATED> */
.widget-valid.mod-invalid i, /* </DEPRECATED> */
.jupyter-widget-valid.mod-invalid i {
  color: red;
}

/* <DEPRECATED> */
.widget-valid.mod-valid .widget-valid-readout, /* </DEPRECATED> */
.jupyter-widget-valid.mod-valid .jupyter-widget-valid-readout {
  display: none;
}

/* Widget Text and TextArea Styling */

/* <DEPRECATED> */
.widget-textarea, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text, /* </DEPRECATED> */
.jupyter-widget-textarea,
.jupyter-widget-text {
  width: var(--jp-widgets-inline-width);
}

/* <DEPRECATED> */
.widget-text input[type='text'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='number'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='password'], /* </DEPRECATED> */
.jupyter-widget-text input[type='text'],
.jupyter-widget-text input[type='number'],
.jupyter-widget-text input[type='password'] {
  height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-text input[type='text']:disabled, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='number']:disabled, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='password']:disabled, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-textarea textarea:disabled, /* </DEPRECATED> */
.jupyter-widget-text input[type='text']:disabled,
.jupyter-widget-text input[type='number']:disabled,
.jupyter-widget-text input[type='password']:disabled,
.jupyter-widget-textarea textarea:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

/* <DEPRECATED> */
.widget-text input[type='text'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='number'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='password'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-textarea textarea, /* </DEPRECATED> */
.jupyter-widget-text input[type='text'],
.jupyter-widget-text input[type='number'],
.jupyter-widget-text input[type='password'],
.jupyter-widget-textarea textarea {
  box-sizing: border-box;
  border: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
  background-color: var(--jp-widgets-input-background-color);
  color: var(--jp-widgets-input-color);
  font-size: var(--jp-widgets-font-size);
  flex-grow: 1;
  min-width: 0; /* This makes it possible for the flexbox to shrink this input */
  flex-shrink: 1;
  outline: none !important;
}

/* <DEPRECATED> */
.widget-text input[type='text'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-text input[type='password'], /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-textarea textarea, /* </DEPRECATED> */
.jupyter-widget-text input[type='text'],
.jupyter-widget-text input[type='password'],
.jupyter-widget-textarea textarea {
  padding: var(--jp-widgets-input-padding)
    calc(var(--jp-widgets-input-padding) * 2);
}

/* <DEPRECATED> */
.widget-text input[type='number'], /* </DEPRECATED> */
.jupyter-widget-text input[type='number'] {
  padding: var(--jp-widgets-input-padding) 0 var(--jp-widgets-input-padding)
    calc(var(--jp-widgets-input-padding) * 2);
}

/* <DEPRECATED> */
.widget-textarea textarea, /* </DEPRECATED> */
.jupyter-widget-textarea textarea {
  height: inherit;
  width: inherit;
}

/* <DEPRECATED> */
.widget-text input:focus, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-textarea textarea:focus, /* </DEPRECATED> */
.jupyter-widget-text input:focus,
.jupyter-widget-textarea textarea:focus {
  border-color: var(--jp-widgets-input-focus-border-color);
}

/* Horizontal Slider */
/* <DEPRECATED> */
.widget-hslider, /* </DEPRECATED> */
.jupyter-widget-hslider {
  width: var(--jp-widgets-inline-width);
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);

  /* Override the align-items baseline. This way, the description and readout
    still seem to align their baseline properly, and we don't have to have
    align-self: stretch in the .slider-container. */
  align-items: center;
}

/* <DEPRECATED> */
.widgets-slider .slider-container, /* </DEPRECATED> */
.jupyter-widgets-slider .slider-container {
  overflow: visible;
}

/* <DEPRECATED> */
.widget-hslider .slider-container, /* </DEPRECATED> */
.jupyter-widget-hslider .slider-container {
  margin-left: calc(
    var(--jp-widgets-slider-handle-size) / 2 - 2 *
      var(--jp-widgets-slider-border-width)
  );
  margin-right: calc(
    var(--jp-widgets-slider-handle-size) / 2 - 2 *
      var(--jp-widgets-slider-border-width)
  );
  flex: 1 1 var(--jp-widgets-inline-width-short);
}

/* Vertical Slider */

/* <DEPRECATED> */
.widget-vbox .widget-label, /* </DEPRECATED> */
.jupyter-widget-vbox .jupyter-widget-label {
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-vslider, /* </DEPRECATED> */
.jupyter-widget-vslider {
  /* Vertical Slider */
  height: var(--jp-widgets-vertical-height);
  width: var(--jp-widgets-inline-width-tiny);
}

/* <DEPRECATED> */
.widget-vslider .slider-container, /* </DEPRECATED> */
.jupyter-widget-vslider .slider-container {
  flex: 1 1 var(--jp-widgets-inline-width-short);
  margin-left: auto;
  margin-right: auto;
  margin-bottom: calc(
    var(--jp-widgets-slider-handle-size) / 2 - 2 *
      var(--jp-widgets-slider-border-width)
  );
  margin-top: calc(
    var(--jp-widgets-slider-handle-size) / 2 - 2 *
      var(--jp-widgets-slider-border-width)
  );
  display: flex;
  flex-direction: column;
}

/* Widget Progress Styling */

.progress-bar {
  -webkit-transition: none;
  -moz-transition: none;
  -ms-transition: none;
  -o-transition: none;
  transition: none;
}

.progress-bar {
  height: var(--jp-widgets-inline-height);
}

.progress-bar {
  background-color: var(--jp-brand-color1);
}

.progress-bar-success {
  background-color: var(--jp-success-color1);
}

.progress-bar-info {
  background-color: var(--jp-info-color1);
}

.progress-bar-warning {
  background-color: var(--jp-warn-color1);
}

.progress-bar-danger {
  background-color: var(--jp-error-color1);
}

.progress {
  background-color: var(--jp-layout-color2);
  border: none;
  box-shadow: none;
}

/* Horisontal Progress */

/* <DEPRECATED> */
.widget-hprogress, /* </DEPRECATED> */
.jupyter-widget-hprogress {
  /* Progress Bar */
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
  width: var(--jp-widgets-inline-width);
  align-items: center;
}

/* <DEPRECATED> */
.widget-hprogress .progress, /* </DEPRECATED> */
.jupyter-widget-hprogress .progress {
  flex-grow: 1;
  margin-top: var(--jp-widgets-input-padding);
  margin-bottom: var(--jp-widgets-input-padding);
  align-self: stretch;
  /* Override bootstrap style */
  height: initial;
}

/* Vertical Progress */

/* <DEPRECATED> */
.widget-vprogress, /* </DEPRECATED> */
.jupyter-widget-vprogress {
  height: var(--jp-widgets-vertical-height);
  width: var(--jp-widgets-inline-width-tiny);
}

/* <DEPRECATED> */
.widget-vprogress .progress, /* </DEPRECATED> */
.jupyter-widget-vprogress .progress {
  flex-grow: 1;
  width: var(--jp-widgets-progress-thickness);
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 0;
}

/* Select Widget Styling */

/* <DEPRECATED> */
.widget-dropdown, /* </DEPRECATED> */
.jupyter-widget-dropdown {
  height: var(--jp-widgets-inline-height);
  width: var(--jp-widgets-inline-width);
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-dropdown > select, /* </DEPRECATED> */
.jupyter-widget-dropdown > select {
  padding-right: 20px;
  border: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
  border-radius: 0;
  height: inherit;
  flex: 1 1 var(--jp-widgets-inline-width-short);
  min-width: 0; /* This makes it possible for the flexbox to shrink this input */
  box-sizing: border-box;
  outline: none !important;
  box-shadow: none;
  background-color: var(--jp-widgets-input-background-color);
  color: var(--jp-widgets-input-color);
  font-size: var(--jp-widgets-font-size);
  vertical-align: top;
  padding-left: calc(var(--jp-widgets-input-padding) * 2);
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-repeat: no-repeat;
  background-size: 20px;
  background-position: right center;
  background-image: var(--jp-widgets-dropdown-arrow);
}
/* <DEPRECATED> */
.widget-dropdown > select:focus, /* </DEPRECATED> */
.jupyter-widget-dropdown > select:focus {
  border-color: var(--jp-widgets-input-focus-border-color);
}

/* <DEPRECATED> */
.widget-dropdown > select:disabled, /* </DEPRECATED> */
.jupyter-widget-dropdown > select:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

/* To disable the dotted border in Firefox around select controls.
   See http://stackoverflow.com/a/18853002 */
/* <DEPRECATED> */
.widget-dropdown > select:-moz-focusring, /* </DEPRECATED> */
.jupyter-widget-dropdown > select:-moz-focusring {
  color: transparent;
  text-shadow: 0 0 0 #000;
}

/* Select and SelectMultiple */

/* <DEPRECATED> */
.widget-select, /* </DEPRECATED> */
.jupyter-widget-select {
  width: var(--jp-widgets-inline-width);
  line-height: var(--jp-widgets-inline-height);

  /* Because Firefox defines the baseline of a select as the bottom of the
    control, we align the entire control to the top and add padding to the
    select to get an approximate first line baseline alignment. */
  align-items: flex-start;
}

/* <DEPRECATED> */
.widget-select > select, /* </DEPRECATED> */
.jupyter-widget-select > select {
  border: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
  background-color: var(--jp-widgets-input-background-color);
  color: var(--jp-widgets-input-color);
  font-size: var(--jp-widgets-font-size);
  flex: 1 1 var(--jp-widgets-inline-width-short);
  outline: none !important;
  overflow: auto;
  height: inherit;

  /* Because Firefox defines the baseline of a select as the bottom of the
    control, we align the entire control to the top and add padding to the
    select to get an approximate first line baseline alignment. */
  padding-top: 5px;
}

/* <DEPRECATED> */
.widget-select > select:focus, /* </DEPRECATED> */
.jupyter-widget-select > select:focus {
  border-color: var(--jp-widgets-input-focus-border-color);
}

.wiget-select > select > option,
.jupyter-wiget-select > select > option {
  padding-left: var(--jp-widgets-input-padding);
  line-height: var(--jp-widgets-inline-height);
  /* line-height doesn't work on some browsers for select options */
  padding-top: calc(
    var(--jp-widgets-inline-height) - var(--jp-widgets-font-size) / 2
  );
  padding-bottom: calc(
    var(--jp-widgets-inline-height) - var(--jp-widgets-font-size) / 2
  );
}

/* Toggle Buttons Styling */

/* <DEPRECATED> */
.widget-toggle-buttons, /* </DEPRECATED> */
.jupyter-widget-toggle-buttons {
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-toggle-buttons .widget-toggle-button, /* </DEPRECATED> */
.jupyter-widget-toggle-buttons .jupyter-widget-toggle-button {
  margin-left: var(--jp-widgets-margin);
  margin-right: var(--jp-widgets-margin);
}

/* <DEPRECATED> */
.widget-toggle-buttons .jupyter-button:disabled, /* </DEPRECATED> */
.jupyter-widget-toggle-buttons .jupyter-button:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

/* Radio Buttons Styling */

/* <DEPRECATED> */
.widget-radio, /* </DEPRECATED> */
.jupyter-widget-radio {
  width: var(--jp-widgets-inline-width);
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-radio-box, /* </DEPRECATED> */
.jupyter-widget-radio-box {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  box-sizing: border-box;
  flex-grow: 1;
  margin-bottom: var(--jp-widgets-radio-item-height-adjustment);
}

/* <DEPRECATED> */
.widget-radio-box-vertical, /* </DEPRECATED> */
.jupyter-widget-radio-box-vertical {
  flex-direction: column;
}

/* <DEPRECATED> */
.widget-radio-box-horizontal, /* </DEPRECATED> */
.jupyter-widget-radio-box-horizontal {
  flex-direction: row;
}

/* <DEPRECATED> */
.widget-radio-box label, /* </DEPRECATED> */
.jupyter-widget-radio-box label {
  height: var(--jp-widgets-radio-item-height);
  line-height: var(--jp-widgets-radio-item-height);
  font-size: var(--jp-widgets-font-size);
}

.widget-radio-box-horizontal label,
.jupyter-widget-radio-box-horizontal label {
  margin: 0 calc(var(--jp-widgets-input-padding) * 2) 0 0;
}

/* <DEPRECATED> */
.widget-radio-box input, /* </DEPRECATED> */
.jupyter-widget-radio-box input {
  height: var(--jp-widgets-radio-item-height);
  line-height: var(--jp-widgets-radio-item-height);
  margin: 0 calc(var(--jp-widgets-input-padding) * 2) 0 1px;
  float: left;
}

/* Color Picker Styling */

/* <DEPRECATED> */
.widget-colorpicker, /* </DEPRECATED> */
.jupyter-widget-colorpicker {
  width: var(--jp-widgets-inline-width);
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-colorpicker > .widget-colorpicker-input, /* </DEPRECATED> */
.jupyter-widget-colorpicker > .jupyter-widget-colorpicker-input {
  flex-grow: 1;
  flex-shrink: 1;
  min-width: var(--jp-widgets-inline-width-tiny);
}

/* <DEPRECATED> */
.widget-colorpicker input[type='color'], /* </DEPRECATED> */
.jupyter-widget-colorpicker input[type='color'] {
  width: var(--jp-widgets-inline-height);
  height: var(--jp-widgets-inline-height);
  padding: 0 2px; /* make the color square actually square on Chrome on OS X */
  background: var(--jp-widgets-input-background-color);
  color: var(--jp-widgets-input-color);
  border: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
  border-left: none;
  flex-grow: 0;
  flex-shrink: 0;
  box-sizing: border-box;
  align-self: stretch;
  outline: none !important;
}

/* <DEPRECATED> */
.widget-colorpicker.concise input[type='color'], /* </DEPRECATED> */
.jupyter-widget-colorpicker.concise input[type='color'] {
  border-left: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
}

/* <DEPRECATED> */
.widget-colorpicker input[type='color']:focus, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-colorpicker input[type='text']:focus, /* </DEPRECATED> */
.jupyter-widget-colorpicker input[type='color']:focus,
.jupyter-widget-colorpicker input[type='text']:focus {
  border-color: var(--jp-widgets-input-focus-border-color);
}

/* <DEPRECATED> */
.widget-colorpicker input[type='text'], /* </DEPRECATED> */
.jupyter-widget-colorpicker input[type='text'] {
  flex-grow: 1;
  outline: none !important;
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
  background: var(--jp-widgets-input-background-color);
  color: var(--jp-widgets-input-color);
  border: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
  font-size: var(--jp-widgets-font-size);
  padding: var(--jp-widgets-input-padding)
    calc(var(--jp-widgets-input-padding) * 2);
  min-width: 0; /* This makes it possible for the flexbox to shrink this input */
  flex-shrink: 1;
  box-sizing: border-box;
}

/* <DEPRECATED> */
.widget-colorpicker input[type='text']:disabled, /* </DEPRECATED> */
.jupyter-widget-colorpicker input[type='text']:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

/* Date Picker Styling */

/* <DEPRECATED> */
.widget-datepicker, /* </DEPRECATED> */
.jupyter-widget-datepicker {
  width: var(--jp-widgets-inline-width);
  height: var(--jp-widgets-inline-height);
  line-height: var(--jp-widgets-inline-height);
}

/* <DEPRECATED> */
.widget-datepicker input[type='date'], /* </DEPRECATED> */
.jupyter-widget-datepicker input[type='date'] {
  flex-grow: 1;
  flex-shrink: 1;
  min-width: 0; /* This makes it possible for the flexbox to shrink this input */
  outline: none !important;
  height: var(--jp-widgets-inline-height);
  border: var(--jp-widgets-input-border-width) solid
    var(--jp-widgets-input-border-color);
  background-color: var(--jp-widgets-input-background-color);
  color: var(--jp-widgets-input-color);
  font-size: var(--jp-widgets-font-size);
  padding: var(--jp-widgets-input-padding)
    calc(var(--jp-widgets-input-padding) * 2);
  box-sizing: border-box;
}

/* <DEPRECATED> */
.widget-datepicker input[type='date']:focus, /* </DEPRECATED> */
.jupyter-widget-datepicker input[type='date']:focus {
  border-color: var(--jp-widgets-input-focus-border-color);
}

/* <DEPRECATED> */
.widget-datepicker input[type='date']:invalid, /* </DEPRECATED> */
.jupyter-widget-datepicker input[type='date']:invalid {
  border-color: var(--jp-warn-color1);
}

/* <DEPRECATED> */
.widget-datepicker input[type='date']:disabled, /* </DEPRECATED> */
.jupyter-widget-datepicker input[type='date']:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

/* Play Widget */

/* <DEPRECATED> */
.widget-play, /* </DEPRECATED> */
.jupyter-widget-play {
  width: var(--jp-widgets-inline-width-short);
  display: flex;
  align-items: stretch;
}

/* <DEPRECATED> */
.widget-play .jupyter-button, /* </DEPRECATED> */
.jupyter-widget-play .jupyter-button {
  flex-grow: 1;
  height: auto;
}

/* <DEPRECATED> */
.widget-play .jupyter-button:disabled, /* </DEPRECATED> */
.jupyter-widget-play .jupyter-button:disabled {
  opacity: var(--jp-widgets-disabled-opacity);
}

/* Tab Widget */

/* <DEPRECATED> */
.jupyter-widgets.widget-tab, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab {
  display: flex;
  flex-direction: column;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar {
  /* Necessary so that a tab can be shifted down to overlay the border of the box below. */
  overflow-x: visible;
  overflow-y: visible;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar > .p-TabBar-content, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar > .p-TabBar-content, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar > .lm-TabBar-content {
  /* Make sure that the tab grows from bottom up */
  align-items: flex-end;
  min-width: 0;
  min-height: 0;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .widget-tab-contents, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .widget-tab-contents {
  width: 100%;
  box-sizing: border-box;
  margin: 0;
  background: var(--jp-layout-color1);
  color: var(--jp-ui-font-color1);
  border: var(--jp-border-width) solid var(--jp-border-color1);
  padding: var(--jp-widgets-container-padding);
  flex-grow: 1;
  overflow: auto;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar {
  font: var(--jp-widgets-font-size) Helvetica, Arial, sans-serif;
  min-height: calc(
    var(--jp-widgets-horizontal-tab-height) + var(--jp-border-width)
  );
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tab, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tab {
  flex: 0 1 var(--jp-widgets-horizontal-tab-width);
  min-width: 35px;
  min-height: calc(
    var(--jp-widgets-horizontal-tab-height) + var(--jp-border-width)
  );
  line-height: var(--jp-widgets-horizontal-tab-height);
  margin-left: calc(-1 * var(--jp-border-width));
  padding: 0px 10px;
  background: var(--jp-layout-color2);
  color: var(--jp-ui-font-color2);
  border: var(--jp-border-width) solid var(--jp-border-color1);
  border-bottom: none;
  position: relative;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-current {
  color: var(--jp-ui-font-color0);
  /* We want the background to match the tab content background */
  background: var(--jp-layout-color1);
  min-height: calc(
    var(--jp-widgets-horizontal-tab-height) + 2 * var(--jp-border-width)
  );
  transform: translateY(var(--jp-border-width));
  overflow: visible;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current:before, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current:before, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-current:before {
  position: absolute;
  top: calc(-1 * var(--jp-border-width));
  left: calc(-1 * var(--jp-border-width));
  content: '';
  height: var(--jp-widgets-horizontal-tab-top-border);
  width: calc(100% + 2 * var(--jp-border-width));
  background: var(--jp-brand-color1);
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab:first-child, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tab:first-child, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tab:first-child {
  margin-left: 0;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar
  .p-TabBar-tab:hover:not(.p-mod-current),
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .p-TabBar
  .p-TabBar-tab:hover:not(.p-mod-current),
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar
  .lm-TabBar-tab:hover:not(.lm-mod-current) {
  background: var(--jp-layout-color1);
  color: var(--jp-ui-font-color1);
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar
  .p-mod-closable
  > .p-TabBar-tabCloseIcon,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
> .p-TabBar
.p-mod-closable
> .p-TabBar-tabCloseIcon,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar
  .lm-mod-closable
  > .lm-TabBar-tabCloseIcon {
  margin-left: 4px;
}

/* This font-awesome strategy may not work across FA4 and FA5, but we don't
actually support closable tabs, so it really doesn't matter */
/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar
  .p-mod-closable
  > .p-TabBar-tabCloseIcon:before,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-widget-tab
> .p-TabBar
.p-mod-closable
> .p-TabBar-tabCloseIcon:before,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar
  .lm-mod-closable
  > .lm-TabBar-tabCloseIcon:before {
  font-family: FontAwesome;
  content: '\\f00d'; /* close */
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabIcon, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabLabel, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabCloseIcon, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tabIcon, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tabLabel, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tabCloseIcon, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tabIcon,
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tabLabel,
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tabCloseIcon {
  line-height: var(--jp-widgets-horizontal-tab-height);
}

/* Accordion Widget */

.jupyter-widget-Collapse {
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.jupyter-widget-Collapse-header {
  padding: var(--jp-widgets-input-padding);
  cursor: pointer;
  color: var(--jp-ui-font-color2);
  background-color: var(--jp-layout-color2);
  border: var(--jp-widgets-border-width) solid var(--jp-border-color1);
  padding: calc(var(--jp-widgets-container-padding) * 2 / 3)
    var(--jp-widgets-container-padding);
  font-weight: bold;
}

.jupyter-widget-Collapse-header:hover {
  background-color: var(--jp-layout-color1);
  color: var(--jp-ui-font-color1);
}

.jupyter-widget-Collapse-open > .jupyter-widget-Collapse-header {
  background-color: var(--jp-layout-color1);
  color: var(--jp-ui-font-color0);
  cursor: default;
  border-bottom: none;
}

.jupyter-widget-Collapse-contents {
  padding: var(--jp-widgets-container-padding);
  background-color: var(--jp-layout-color1);
  color: var(--jp-ui-font-color1);
  border-left: var(--jp-widgets-border-width) solid var(--jp-border-color1);
  border-right: var(--jp-widgets-border-width) solid var(--jp-border-color1);
  border-bottom: var(--jp-widgets-border-width) solid var(--jp-border-color1);
  overflow: auto;
}

.jupyter-widget-Accordion {
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.jupyter-widget-Accordion .jupyter-widget-Collapse {
  margin-bottom: 0;
}

.jupyter-widget-Accordion .jupyter-widget-Collapse + .jupyter-widget-Collapse {
  margin-top: 4px;
}

/* HTML widget */

/* <DEPRECATED> */
.widget-html, /* </DEPRECATED> */
/* <DEPRECATED> */ .widget-htmlmath, /* </DEPRECATED> */
.jupyter-widget-html,
.jupyter-widget-htmlmath {
  font-size: var(--jp-widgets-font-size);
}

/* <DEPRECATED> */
.widget-html > .widget-html-content, /* </DEPRECATED> */
/* <DEPRECATED> */.widget-htmlmath > .widget-html-content, /* </DEPRECATED> */
.jupyter-widget-html > .jupyter-widget-html-content,
.jupyter-widget-htmlmath > .jupyter-widget-html-content {
  /* Fill out the area in the HTML widget */
  align-self: stretch;
  flex-grow: 1;
  flex-shrink: 1;
  /* Makes sure the baseline is still aligned with other elements */
  line-height: var(--jp-widgets-inline-height);
  /* Make it possible to have absolutely-positioned elements in the html */
  position: relative;
}

/* Image widget  */

/* <DEPRECATED> */
.widget-image, /* </DEPRECATED> */
.jupyter-widget-image {
  max-width: 100%;
  height: auto;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 61446
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
___CSS_LOADER_EXPORT___.push([module.id, `/*

The nouislider.css file is autogenerated from nouislider.less, which imports and wraps the nouislider/src/nouislider.less styles.

MIT License

Copyright (c) 2019 Léon Gersen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
/* The .widget-slider class is deprecated */
.widget-slider,
.jupyter-widget-slider {
  /* Functional styling;
 * These styles are required for noUiSlider to function.
 * You don't need to change these rules to apply your design.
 */
  /* Wrapper for all connect elements.
 */
  /* Offset direction
 */
  /* Give origins 0 height/width so they don't interfere with clicking the
 * connect elements.
 */
  /* Slider size and handle placement;
 */
  /* Styling;
 * Giving the connect element a border radius causes issues with using transform: scale
 */
  /* Handles and cursors;
 */
  /* Handle stripes;
 */
  /* Disabled state;
 */
  /* Base;
 *
 */
  /* Values;
 *
 */
  /* Markings;
 *
 */
  /* Horizontal layout;
 *
 */
  /* Vertical layout;
 *
 */
  /* Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
  /* Custom CSS for nouislider */
}
.widget-slider .noUi-target,
.jupyter-widget-slider .noUi-target,
.widget-slider .noUi-target *,
.jupyter-widget-slider .noUi-target * {
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
  -webkit-user-select: none;
  -ms-touch-action: none;
  touch-action: none;
  -ms-user-select: none;
  -moz-user-select: none;
  user-select: none;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}
.widget-slider .noUi-target,
.jupyter-widget-slider .noUi-target {
  position: relative;
}
.widget-slider .noUi-base,
.jupyter-widget-slider .noUi-base,
.widget-slider .noUi-connects,
.jupyter-widget-slider .noUi-connects {
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
}
.widget-slider .noUi-connects,
.jupyter-widget-slider .noUi-connects {
  overflow: hidden;
  z-index: 0;
}
.widget-slider .noUi-connect,
.jupyter-widget-slider .noUi-connect,
.widget-slider .noUi-origin,
.jupyter-widget-slider .noUi-origin {
  will-change: transform;
  position: absolute;
  z-index: 1;
  top: 0;
  right: 0;
  -ms-transform-origin: 0 0;
  -webkit-transform-origin: 0 0;
  -webkit-transform-style: preserve-3d;
  transform-origin: 0 0;
  transform-style: flat;
}
.widget-slider .noUi-connect,
.jupyter-widget-slider .noUi-connect {
  height: 100%;
  width: 100%;
}
.widget-slider .noUi-origin,
.jupyter-widget-slider .noUi-origin {
  height: 10%;
  width: 10%;
}
.widget-slider .noUi-txt-dir-rtl.noUi-horizontal .noUi-origin,
.jupyter-widget-slider .noUi-txt-dir-rtl.noUi-horizontal .noUi-origin {
  left: 0;
  right: auto;
}
.widget-slider .noUi-vertical .noUi-origin,
.jupyter-widget-slider .noUi-vertical .noUi-origin {
  width: 0;
}
.widget-slider .noUi-horizontal .noUi-origin,
.jupyter-widget-slider .noUi-horizontal .noUi-origin {
  height: 0;
}
.widget-slider .noUi-handle,
.jupyter-widget-slider .noUi-handle {
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  position: absolute;
}
.widget-slider .noUi-touch-area,
.jupyter-widget-slider .noUi-touch-area {
  height: 100%;
  width: 100%;
}
.widget-slider .noUi-state-tap .noUi-connect,
.jupyter-widget-slider .noUi-state-tap .noUi-connect,
.widget-slider .noUi-state-tap .noUi-origin,
.jupyter-widget-slider .noUi-state-tap .noUi-origin {
  -webkit-transition: transform 0.3s;
  transition: transform 0.3s;
}
.widget-slider .noUi-state-drag *,
.jupyter-widget-slider .noUi-state-drag * {
  cursor: inherit !important;
}
.widget-slider .noUi-horizontal,
.jupyter-widget-slider .noUi-horizontal {
  height: 18px;
}
.widget-slider .noUi-horizontal .noUi-handle,
.jupyter-widget-slider .noUi-horizontal .noUi-handle {
  width: 34px;
  height: 28px;
  right: -17px;
  top: -6px;
}
.widget-slider .noUi-vertical,
.jupyter-widget-slider .noUi-vertical {
  width: 18px;
}
.widget-slider .noUi-vertical .noUi-handle,
.jupyter-widget-slider .noUi-vertical .noUi-handle {
  width: 28px;
  height: 34px;
  right: -6px;
  top: -17px;
}
.widget-slider .noUi-txt-dir-rtl.noUi-horizontal .noUi-handle,
.jupyter-widget-slider .noUi-txt-dir-rtl.noUi-horizontal .noUi-handle {
  left: -17px;
  right: auto;
}
.widget-slider .noUi-target,
.jupyter-widget-slider .noUi-target {
  background: #FAFAFA;
  border-radius: 4px;
  border: 1px solid #D3D3D3;
  box-shadow: inset 0 1px 1px #F0F0F0, 0 3px 6px -5px #BBB;
}
.widget-slider .noUi-connects,
.jupyter-widget-slider .noUi-connects {
  border-radius: 3px;
}
.widget-slider .noUi-connect,
.jupyter-widget-slider .noUi-connect {
  background: #3FB8AF;
}
.widget-slider .noUi-draggable,
.jupyter-widget-slider .noUi-draggable {
  cursor: ew-resize;
}
.widget-slider .noUi-vertical .noUi-draggable,
.jupyter-widget-slider .noUi-vertical .noUi-draggable {
  cursor: ns-resize;
}
.widget-slider .noUi-handle,
.jupyter-widget-slider .noUi-handle {
  border: 1px solid #D9D9D9;
  border-radius: 3px;
  background: #FFF;
  cursor: default;
  box-shadow: inset 0 0 1px #FFF, inset 0 1px 7px #EBEBEB, 0 3px 6px -3px #BBB;
}
.widget-slider .noUi-active,
.jupyter-widget-slider .noUi-active {
  box-shadow: inset 0 0 1px #FFF, inset 0 1px 7px #DDD, 0 3px 6px -3px #BBB;
}
.widget-slider .noUi-handle:before,
.jupyter-widget-slider .noUi-handle:before,
.widget-slider .noUi-handle:after,
.jupyter-widget-slider .noUi-handle:after {
  content: "";
  display: block;
  position: absolute;
  height: 14px;
  width: 1px;
  background: #E8E7E6;
  left: 14px;
  top: 6px;
}
.widget-slider .noUi-handle:after,
.jupyter-widget-slider .noUi-handle:after {
  left: 17px;
}
.widget-slider .noUi-vertical .noUi-handle:before,
.jupyter-widget-slider .noUi-vertical .noUi-handle:before,
.widget-slider .noUi-vertical .noUi-handle:after,
.jupyter-widget-slider .noUi-vertical .noUi-handle:after {
  width: 14px;
  height: 1px;
  left: 6px;
  top: 14px;
}
.widget-slider .noUi-vertical .noUi-handle:after,
.jupyter-widget-slider .noUi-vertical .noUi-handle:after {
  top: 17px;
}
.widget-slider [disabled] .noUi-connect,
.jupyter-widget-slider [disabled] .noUi-connect {
  background: #B8B8B8;
}
.widget-slider [disabled].noUi-target,
.jupyter-widget-slider [disabled].noUi-target,
.widget-slider [disabled].noUi-handle,
.jupyter-widget-slider [disabled].noUi-handle,
.widget-slider [disabled] .noUi-handle,
.jupyter-widget-slider [disabled] .noUi-handle {
  cursor: not-allowed;
}
.widget-slider .noUi-pips,
.jupyter-widget-slider .noUi-pips,
.widget-slider .noUi-pips *,
.jupyter-widget-slider .noUi-pips * {
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}
.widget-slider .noUi-pips,
.jupyter-widget-slider .noUi-pips {
  position: absolute;
  color: #999;
}
.widget-slider .noUi-value,
.jupyter-widget-slider .noUi-value {
  position: absolute;
  white-space: nowrap;
  text-align: center;
}
.widget-slider .noUi-value-sub,
.jupyter-widget-slider .noUi-value-sub {
  color: #ccc;
  font-size: 10px;
}
.widget-slider .noUi-marker,
.jupyter-widget-slider .noUi-marker {
  position: absolute;
  background: #CCC;
}
.widget-slider .noUi-marker-sub,
.jupyter-widget-slider .noUi-marker-sub {
  background: #AAA;
}
.widget-slider .noUi-marker-large,
.jupyter-widget-slider .noUi-marker-large {
  background: #AAA;
}
.widget-slider .noUi-pips-horizontal,
.jupyter-widget-slider .noUi-pips-horizontal {
  padding: 10px 0;
  height: 80px;
  top: 100%;
  left: 0;
  width: 100%;
}
.widget-slider .noUi-value-horizontal,
.jupyter-widget-slider .noUi-value-horizontal {
  -webkit-transform: translate(-50%, 50%);
  transform: translate(-50%, 50%);
}
.noUi-rtl .widget-slider .noUi-value-horizontal,
.noUi-rtl .jupyter-widget-slider .noUi-value-horizontal {
  -webkit-transform: translate(50%, 50%);
  transform: translate(50%, 50%);
}
.widget-slider .noUi-marker-horizontal.noUi-marker,
.jupyter-widget-slider .noUi-marker-horizontal.noUi-marker {
  margin-left: -1px;
  width: 2px;
  height: 5px;
}
.widget-slider .noUi-marker-horizontal.noUi-marker-sub,
.jupyter-widget-slider .noUi-marker-horizontal.noUi-marker-sub {
  height: 10px;
}
.widget-slider .noUi-marker-horizontal.noUi-marker-large,
.jupyter-widget-slider .noUi-marker-horizontal.noUi-marker-large {
  height: 15px;
}
.widget-slider .noUi-pips-vertical,
.jupyter-widget-slider .noUi-pips-vertical {
  padding: 0 10px;
  height: 100%;
  top: 0;
  left: 100%;
}
.widget-slider .noUi-value-vertical,
.jupyter-widget-slider .noUi-value-vertical {
  -webkit-transform: translate(0, -50%);
  transform: translate(0, -50%);
  padding-left: 25px;
}
.noUi-rtl .widget-slider .noUi-value-vertical,
.noUi-rtl .jupyter-widget-slider .noUi-value-vertical {
  -webkit-transform: translate(0, 50%);
  transform: translate(0, 50%);
}
.widget-slider .noUi-marker-vertical.noUi-marker,
.jupyter-widget-slider .noUi-marker-vertical.noUi-marker {
  width: 5px;
  height: 2px;
  margin-top: -1px;
}
.widget-slider .noUi-marker-vertical.noUi-marker-sub,
.jupyter-widget-slider .noUi-marker-vertical.noUi-marker-sub {
  width: 10px;
}
.widget-slider .noUi-marker-vertical.noUi-marker-large,
.jupyter-widget-slider .noUi-marker-vertical.noUi-marker-large {
  width: 15px;
}
.widget-slider .noUi-tooltip,
.jupyter-widget-slider .noUi-tooltip {
  display: block;
  position: absolute;
  border: 1px solid #D9D9D9;
  border-radius: 3px;
  background: #fff;
  color: #000;
  padding: 5px;
  text-align: center;
  white-space: nowrap;
}
.widget-slider .noUi-horizontal .noUi-tooltip,
.jupyter-widget-slider .noUi-horizontal .noUi-tooltip {
  -webkit-transform: translate(-50%, 0);
  transform: translate(-50%, 0);
  left: 50%;
  bottom: 120%;
}
.widget-slider .noUi-vertical .noUi-tooltip,
.jupyter-widget-slider .noUi-vertical .noUi-tooltip {
  -webkit-transform: translate(0, -50%);
  transform: translate(0, -50%);
  top: 50%;
  right: 120%;
}
.widget-slider .noUi-horizontal .noUi-origin > .noUi-tooltip,
.jupyter-widget-slider .noUi-horizontal .noUi-origin > .noUi-tooltip {
  -webkit-transform: translate(50%, 0);
  transform: translate(50%, 0);
  left: auto;
  bottom: 10px;
}
.widget-slider .noUi-vertical .noUi-origin > .noUi-tooltip,
.jupyter-widget-slider .noUi-vertical .noUi-origin > .noUi-tooltip {
  -webkit-transform: translate(0, -18px);
  transform: translate(0, -18px);
  top: auto;
  right: 28px;
}
.widget-slider .noUi-connect,
.jupyter-widget-slider .noUi-connect {
  background: #2196f3;
}
.widget-slider .noUi-horizontal,
.jupyter-widget-slider .noUi-horizontal {
  height: var(--jp-widgets-slider-track-thickness);
}
.widget-slider .noUi-vertical,
.jupyter-widget-slider .noUi-vertical {
  width: var(--jp-widgets-slider-track-thickness);
  height: 100%;
}
.widget-slider .noUi-horizontal .noUi-handle,
.jupyter-widget-slider .noUi-horizontal .noUi-handle {
  width: var(--jp-widgets-slider-handle-size);
  height: var(--jp-widgets-slider-handle-size);
  border-radius: 50%;
  top: calc((var(--jp-widgets-slider-track-thickness) - var(--jp-widgets-slider-handle-size)) / 2);
  right: calc(var(--jp-widgets-slider-handle-size) / -2);
}
.widget-slider .noUi-vertical .noUi-handle,
.jupyter-widget-slider .noUi-vertical .noUi-handle {
  height: var(--jp-widgets-slider-handle-size);
  width: var(--jp-widgets-slider-handle-size);
  border-radius: 50%;
  right: calc((var(--jp-widgets-slider-handle-size) - var(--jp-widgets-slider-track-thickness)) / -2);
  top: calc(var(--jp-widgets-slider-handle-size) / -2);
}
.widget-slider .noUi-handle:after,
.jupyter-widget-slider .noUi-handle:after {
  content: none;
}
.widget-slider .noUi-handle:before,
.jupyter-widget-slider .noUi-handle:before {
  content: none;
}
.widget-slider .noUi-target,
.jupyter-widget-slider .noUi-target {
  background: #fafafa;
  border-radius: 4px;
  border: 1px;
  /* box-shadow: inset 0 1px 1px #F0F0F0, 0 3px 6px -5px #BBB; */
}
.widget-slider .ui-slider,
.jupyter-widget-slider .ui-slider {
  border: var(--jp-widgets-slider-border-width) solid var(--jp-layout-color3);
  background: var(--jp-layout-color3);
  box-sizing: border-box;
  position: relative;
  border-radius: 0px;
}
.widget-slider .noUi-handle,
.jupyter-widget-slider .noUi-handle {
  width: var(--jp-widgets-slider-handle-size);
  border: 1px solid #d9d9d9;
  border-radius: 3px;
  background: #fff;
  cursor: default;
  box-shadow: none;
  outline: none;
}
.widget-slider .noUi-target:not([disabled]) .noUi-handle:hover,
.jupyter-widget-slider .noUi-target:not([disabled]) .noUi-handle:hover,
.widget-slider .noUi-target:not([disabled]) .noUi-handle:focus,
.jupyter-widget-slider .noUi-target:not([disabled]) .noUi-handle:focus {
  background-color: var(--jp-widgets-slider-active-handle-color);
  border: var(--jp-widgets-slider-border-width) solid var(--jp-widgets-slider-active-handle-color);
}
.widget-slider [disabled].noUi-target,
.jupyter-widget-slider [disabled].noUi-target {
  opacity: 0.35;
}
.widget-slider .noUi-connects,
.jupyter-widget-slider .noUi-connects {
  overflow: visible;
  z-index: 0;
  background: var(--jp-layout-color3);
}
.widget-slider .noUi-vertical .noUi-connect,
.jupyter-widget-slider .noUi-vertical .noUi-connect {
  width: calc(100% + 2px);
  right: -1px;
}
.widget-slider .noUi-horizontal .noUi-connect,
.jupyter-widget-slider .noUi-horizontal .noUi-connect {
  height: calc(100% + 2px);
  top: -1px;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 75646
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(85072);
/* harmony import */ var _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_cjs_js_widgets_base_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(42525);

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_css_loader_dist_cjs_js_widgets_base_css__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .A, options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_css_loader_dist_cjs_js_widgets_base_css__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .A.locals || {});

/***/ },

/***/ 93044
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
___CSS_LOADER_EXPORT___.push([module.id, `/* This file has code derived from Lumino CSS files, as noted below. The license for this Lumino code is:

Copyright (c) 2019 Project Jupyter Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Copyright (c) 2014-2017, PhosphorJS Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 * The following section is derived from https://github.com/jupyterlab/lumino/blob/23b9d075ebc5b73ab148b6ebfc20af97f85714c4/packages/widgets/style/tabbar.css 
 * We've scoped the rules so that they are consistent with exactly our code.
 */

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar {
  display: flex;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar[data-orientation='horizontal'], /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar[data-orientation='horizontal'], /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar[data-orientation='horizontal'] {
  flex-direction: row;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar[data-orientation='vertical'], /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar[data-orientation='vertical'], /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar[data-orientation='vertical'] {
  flex-direction: column;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar > .p-TabBar-content, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar > .p-TabBar-content, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar > .lm-TabBar-content {
  margin: 0;
  padding: 0;
  display: flex;
  flex: 1 1 auto;
  list-style-type: none;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar[data-orientation='horizontal']
  > .p-TabBar-content,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
> .p-TabBar[data-orientation='horizontal']
> .p-TabBar-content,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar[data-orientation='horizontal']
  > .lm-TabBar-content {
  flex-direction: row;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar[data-orientation='vertical']
  > .p-TabBar-content,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
> .p-TabBar[data-orientation='vertical']
> .p-TabBar-content,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar[data-orientation='vertical']
  > .lm-TabBar-content {
  flex-direction: column;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tab, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tab {
  display: flex;
  flex-direction: row;
  box-sizing: border-box;
  overflow: hidden;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabIcon, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabCloseIcon, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tabIcon, /* </DEPRECATED> */
/* <DEPRECATED> */ .jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tabCloseIcon, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tabIcon,
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tabCloseIcon {
  flex: 0 0 auto;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabLabel, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tabLabel, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tabLabel {
  flex: 1 1 auto;
  overflow: hidden;
  white-space: nowrap;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab.p-mod-hidden, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar .p-TabBar-tab.p-mod-hidden, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-hidden {
  display: none !important;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab > .p-TabBar.p-mod-dragging .p-TabBar-tab, /* </DEPRECATED> */
/* <DEPRECATED> */.jupyter-widgets.jupyter-widget-tab > .p-TabBar.p-mod-dragging .p-TabBar-tab, /* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab > .lm-TabBar.lm-mod-dragging .lm-TabBar-tab {
  position: relative;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar.p-mod-dragging[data-orientation='horizontal']
  .p-TabBar-tab,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .p-TabBar.p-mod-dragging[data-orientation='horizontal']
  .p-TabBar-tab,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar.lm-mod-dragging[data-orientation='horizontal']
  .lm-TabBar-tab {
  left: 0;
  transition: left 150ms ease;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar.p-mod-dragging[data-orientation='vertical']
  .p-TabBar-tab,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
> .p-TabBar.p-mod-dragging[data-orientation='vertical']
.p-TabBar-tab,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar.lm-mod-dragging[data-orientation='vertical']
  .lm-TabBar-tab {
  top: 0;
  transition: top 150ms ease;
}

/* <DEPRECATED> */
.jupyter-widgets.widget-tab
  > .p-TabBar.p-mod-dragging
  .p-TabBar-tab.p-mod-dragging,
/* </DEPRECATED> */
/* <DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
> .p-TabBar.p-mod-dragging
.p-TabBar-tab.p-mod-dragging,
/* </DEPRECATED> */
.jupyter-widgets.jupyter-widget-tab
  > .lm-TabBar.lm-mod-dragging
  .lm-TabBar-tab.lm-mod-dragging {
  transition: none;
}

/* End tabbar.css */
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTY0Ni5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7Ozs7Ozs7QUN2NUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7Ozs7Ozs7QUM1ZUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7O0FDWkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVyLXdpZGdldHMvY29udHJvbHMvY3NzL3dpZGdldHMtYmFzZS5jc3MiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlci13aWRnZXRzL2NvbnRyb2xzL2Nzcy9ub3Vpc2xpZGVyLmNzcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVyLXdpZGdldHMvY29udHJvbHMvY3NzL3dpZGdldHMtYmFzZS5jc3M/MTI2ZiIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVyLXdpZGdldHMvY29udHJvbHMvY3NzL2x1bWluby5jc3MiXSwic291cmNlc0NvbnRlbnQiOlsiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BVF9SVUxFX0lNUE9SVF8wX19fIGZyb20gXCItIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi9sdW1pbm8uY3NzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BVF9SVUxFX0lNUE9SVF8xX19fIGZyb20gXCItIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi9ub3Vpc2xpZGVyLmNzc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfR0VUX1VSTF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL2dldFVybC5qc1wiO1xudmFyIF9fX0NTU19MT0FERVJfVVJMX0lNUE9SVF8wX19fID0gbmV3IFVSTChcImRhdGE6aW1hZ2Uvc3ZnK3htbDtiYXNlNjQsUEQ5NGJXd2dkbVZ5YzJsdmJqMGlNUzR3SWlCbGJtTnZaR2x1WnowaWRYUm1MVGdpUHo0S1BDRXRMU0JIWlc1bGNtRjBiM0k2SUVGa2IySmxJRWxzYkhWemRISmhkRzl5SURFNUxqSXVNU3dnVTFaSElFVjRjRzl5ZENCUWJIVm5MVWx1SUM0Z1UxWkhJRlpsY25OcGIyNDZJRFl1TURBZ1FuVnBiR1FnTUNrZ0lDMHRQZ284YzNabklIWmxjbk5wYjI0OUlqRXVNU0lnYVdROUlreGhlV1Z5WHpFaUlIaHRiRzV6UFNKb2RIUndPaTh2ZDNkM0xuY3pMbTl5Wnk4eU1EQXdMM04yWnlJZ2VHMXNibk02ZUd4cGJtczlJbWgwZEhBNkx5OTNkM2N1ZHpNdWIzSm5MekU1T1RrdmVHeHBibXNpSUhnOUlqQndlQ0lnZVQwaU1IQjRJZ29KSUhacFpYZENiM2c5SWpBZ01DQXhPQ0F4T0NJZ2MzUjViR1U5SW1WdVlXSnNaUzFpWVdOclozSnZkVzVrT201bGR5QXdJREFnTVRnZ01UZzdJaUI0Yld3NmMzQmhZMlU5SW5CeVpYTmxjblpsSWo0S1BITjBlV3hsSUhSNWNHVTlJblJsZUhRdlkzTnpJajRLQ1M1emREQjdabWxzYkRwdWIyNWxPMzBLUEM5emRIbHNaVDRLUEhCaGRHZ2daRDBpVFRVdU1pdzFMamxNT1N3NUxqZHNNeTQ0TFRNdU9Hd3hMaklzTVM0eWJDMDBMamtzTld3dE5DNDVMVFZNTlM0eUxEVXVPWG9pTHo0S1BIQmhkR2dnWTJ4aGMzTTlJbk4wTUNJZ1pEMGlUVEF0TUM0MmFERTRkakU0U0RCV0xUQXVObm9pTHo0S1BDOXpkbWMrQ2dcIiwgaW1wb3J0Lm1ldGEudXJsKTtcbnZhciBfX19DU1NfTE9BREVSX0VYUE9SVF9fXyA9IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fKTtcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLmkoX19fQ1NTX0xPQURFUl9BVF9SVUxFX0lNUE9SVF8wX19fKTtcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLmkoX19fQ1NTX0xPQURFUl9BVF9SVUxFX0lNUE9SVF8xX19fKTtcbnZhciBfX19DU1NfTE9BREVSX1VSTF9SRVBMQUNFTUVOVF8wX19fID0gX19fQ1NTX0xPQURFUl9HRVRfVVJMX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX1VSTF9JTVBPUlRfMF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qIENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxuICogRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbiAqL1xuXG4vKlxuICogV2UgYXNzdW1lIHRoYXQgdGhlIENTUyB2YXJpYWJsZXMgaW5cbiAqIGh0dHBzOi8vZ2l0aHViLmNvbS9qdXB5dGVybGFiL2p1cHl0ZXJsYWIvYmxvYi9tYXN0ZXIvc3JjL2RlZmF1bHQtdGhlbWUvdmFyaWFibGVzLmNzc1xuICogaGF2ZSBiZWVuIGRlZmluZWQuXG4gKi9cblxuOnJvb3Qge1xuICAtLWpwLXdpZGdldHMtY29sb3I6IHZhcigtLWpwLWNvbnRlbnQtZm9udC1jb2xvcjEpO1xuICAtLWpwLXdpZGdldHMtbGFiZWwtY29sb3I6IHZhcigtLWpwLXdpZGdldHMtY29sb3IpO1xuICAtLWpwLXdpZGdldHMtcmVhZG91dC1jb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1jb2xvcik7XG4gIC0tanAtd2lkZ2V0cy1mb250LXNpemU6IHZhcigtLWpwLXVpLWZvbnQtc2l6ZTEpO1xuICAtLWpwLXdpZGdldHMtbWFyZ2luOiAycHg7XG4gIC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0OiAyOHB4O1xuICAtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoOiAzMDBweDtcbiAgLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC1zaG9ydDogY2FsYyhcbiAgICB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aCkgLyAyIC0gdmFyKC0tanAtd2lkZ2V0cy1tYXJnaW4pXG4gICk7XG4gIC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgtdGlueTogY2FsYyhcbiAgICB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC1zaG9ydCkgLyAyIC0gdmFyKC0tanAtd2lkZ2V0cy1tYXJnaW4pXG4gICk7XG4gIC0tanAtd2lkZ2V0cy1pbmxpbmUtbWFyZ2luOiA0cHg7IC8qIG1hcmdpbiBiZXR3ZWVuIGlubGluZSBlbGVtZW50cyAqL1xuICAtLWpwLXdpZGdldHMtaW5saW5lLWxhYmVsLXdpZHRoOiA4MHB4O1xuICAtLWpwLXdpZGdldHMtYm9yZGVyLXdpZHRoOiB2YXIoLS1qcC1ib3JkZXItd2lkdGgpO1xuICAtLWpwLXdpZGdldHMtdmVydGljYWwtaGVpZ2h0OiAyMDBweDtcbiAgLS1qcC13aWRnZXRzLWhvcml6b250YWwtdGFiLWhlaWdodDogMjRweDtcbiAgLS1qcC13aWRnZXRzLWhvcml6b250YWwtdGFiLXdpZHRoOiAxNDRweDtcbiAgLS1qcC13aWRnZXRzLWhvcml6b250YWwtdGFiLXRvcC1ib3JkZXI6IDJweDtcbiAgLS1qcC13aWRnZXRzLXByb2dyZXNzLXRoaWNrbmVzczogMjBweDtcbiAgLS1qcC13aWRnZXRzLWNvbnRhaW5lci1wYWRkaW5nOiAxNXB4O1xuICAtLWpwLXdpZGdldHMtaW5wdXQtcGFkZGluZzogNHB4O1xuICAtLWpwLXdpZGdldHMtcmFkaW8taXRlbS1oZWlnaHQtYWRqdXN0bWVudDogOHB4O1xuICAtLWpwLXdpZGdldHMtcmFkaW8taXRlbS1oZWlnaHQ6IGNhbGMoXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KSAtXG4gICAgICB2YXIoLS1qcC13aWRnZXRzLXJhZGlvLWl0ZW0taGVpZ2h0LWFkanVzdG1lbnQpXG4gICk7XG4gIC0tanAtd2lkZ2V0cy1zbGlkZXItdHJhY2stdGhpY2tuZXNzOiA0cHg7XG4gIC0tanAtd2lkZ2V0cy1zbGlkZXItYm9yZGVyLXdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWJvcmRlci13aWR0aCk7XG4gIC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLXNpemU6IDE2cHg7XG4gIC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLWJvcmRlci1jb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG4gIC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLWJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICAtLWpwLXdpZGdldHMtc2xpZGVyLWFjdGl2ZS1oYW5kbGUtY29sb3I6IHZhcigtLWpwLWJyYW5kLWNvbG9yMSk7XG4gIC0tanAtd2lkZ2V0cy1tZW51LWl0ZW0taGVpZ2h0OiAyNHB4O1xuICAtLWpwLXdpZGdldHMtZHJvcGRvd24tYXJyb3c6IHVybCgke19fX0NTU19MT0FERVJfVVJMX1JFUExBQ0VNRU5UXzBfX199KTtcbiAgLS1qcC13aWRnZXRzLWlucHV0LWNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMSk7XG4gIC0tanAtd2lkZ2V0cy1pbnB1dC1iYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IxKTtcbiAgLS1qcC13aWRnZXRzLWlucHV0LWJvcmRlci1jb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG4gIC0tanAtd2lkZ2V0cy1pbnB1dC1mb2N1cy1ib3JkZXItY29sb3I6IHZhcigtLWpwLWJyYW5kLWNvbG9yMik7XG4gIC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItd2lkdGg6IHZhcigtLWpwLXdpZGdldHMtYm9yZGVyLXdpZHRoKTtcbiAgLS1qcC13aWRnZXRzLWRpc2FibGVkLW9wYWNpdHk6IDAuNjtcblxuICAvKiBGcm9tIE1hdGVyaWFsIERlc2lnbiBMaXRlICovXG4gIC0tbWQtc2hhZG93LWtleS11bWJyYS1vcGFjaXR5OiAwLjI7XG4gIC0tbWQtc2hhZG93LWtleS1wZW51bWJyYS1vcGFjaXR5OiAwLjE0O1xuICAtLW1kLXNoYWRvdy1hbWJpZW50LXNoYWRvdy1vcGFjaXR5OiAwLjEyO1xufVxuXG4uanVweXRlci13aWRnZXRzIHtcbiAgbWFyZ2luOiB2YXIoLS1qcC13aWRnZXRzLW1hcmdpbik7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG4gIGNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWNvbG9yKTtcbiAgb3ZlcmZsb3c6IHZpc2libGU7XG59XG5cbi5qcC1PdXRwdXQtcmVzdWx0ID4gLmp1cHl0ZXItd2lkZ2V0cyB7XG4gIG1hcmdpbi1sZWZ0OiAwO1xuICBtYXJnaW4tcmlnaHQ6IDA7XG59XG5cbi8qIHZib3ggYW5kIGhib3ggKi9cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWlubGluZS1oYm94LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4gLmp1cHl0ZXItd2lkZ2V0LWlubGluZS1oYm94IHtcbiAgLyogSG9yaXpvbnRhbCB3aWRnZXRzICovXG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGZsZXgtZGlyZWN0aW9uOiByb3c7XG4gIGFsaWduLWl0ZW1zOiBiYXNlbGluZTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWlubGluZS12Ym94LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4gLmp1cHl0ZXItd2lkZ2V0LWlubGluZS12Ym94IHtcbiAgLyogVmVydGljYWwgV2lkZ2V0cyAqL1xuICBib3gtc2l6aW5nOiBib3JkZXItYm94O1xuICBkaXNwbGF5OiBmbGV4O1xuICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xuICBhbGlnbi1pdGVtczogY2VudGVyO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtYm94LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtYm94IHtcbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgZGlzcGxheTogZmxleDtcbiAgbWFyZ2luOiAwO1xuICBvdmVyZmxvdzogYXV0bztcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWdyaWRib3gsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1ncmlkYm94IHtcbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgZGlzcGxheTogZ3JpZDtcbiAgbWFyZ2luOiAwO1xuICBvdmVyZmxvdzogYXV0bztcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWhib3gsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1oYm94IHtcbiAgZmxleC1kaXJlY3Rpb246IHJvdztcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXZib3gsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC12Ym94IHtcbiAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbn1cblxuLyogR2VuZXJhbCBUYWdzIFN0eWxpbmcgKi9cblxuLmp1cHl0ZXItd2lkZ2V0LXRhZ3NpbnB1dCB7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGZsZXgtZGlyZWN0aW9uOiByb3c7XG4gIGZsZXgtd3JhcDogd3JhcDtcbiAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbiAgb3ZlcmZsb3c6IGF1dG87XG5cbiAgY3Vyc29yOiB0ZXh0O1xufVxuXG4uanVweXRlci13aWRnZXQtdGFnIHtcbiAgcGFkZGluZy1sZWZ0OiAxMHB4O1xuICBwYWRkaW5nLXJpZ2h0OiAxMHB4O1xuICBwYWRkaW5nLXRvcDogMHB4O1xuICBwYWRkaW5nLWJvdHRvbTogMHB4O1xuICBkaXNwbGF5OiBpbmxpbmUtYmxvY2s7XG4gIHdoaXRlLXNwYWNlOiBub3dyYXA7XG4gIG92ZXJmbG93OiBoaWRkZW47XG4gIHRleHQtb3ZlcmZsb3c6IGVsbGlwc2lzO1xuICB0ZXh0LWFsaWduOiBjZW50ZXI7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtd2lkZ2V0cy1mb250LXNpemUpO1xuXG4gIGhlaWdodDogY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpIC0gMnB4KTtcbiAgYm9yZGVyOiAwcHggc29saWQ7XG4gIGxpbmUtaGVpZ2h0OiBjYWxjKHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCkgLSAycHgpO1xuICBib3gtc2hhZG93OiBub25lO1xuXG4gIGNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMSk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjIpO1xuICBib3JkZXItY29sb3I6IHZhcigtLWpwLWJvcmRlci1jb2xvcjIpO1xuICBib3JkZXI6IG5vbmU7XG4gIHVzZXItc2VsZWN0OiBub25lO1xuXG4gIGN1cnNvcjogZ3JhYjtcbiAgdHJhbnNpdGlvbjogbWFyZ2luLWxlZnQgMjAwbXM7XG4gIG1hcmdpbjogMXB4IDFweCAxcHggMXB4O1xufVxuXG4uanVweXRlci13aWRnZXQtdGFnLm1vZC1hY3RpdmUge1xuICAvKiBNRCBMaXRlIDRkcCBzaGFkb3cgKi9cbiAgYm94LXNoYWRvdzogMCA0cHggNXB4IDAgcmdiYSgwLCAwLCAwLCB2YXIoLS1tZC1zaGFkb3cta2V5LXBlbnVtYnJhLW9wYWNpdHkpKSxcbiAgICAwIDFweCAxMHB4IDAgcmdiYSgwLCAwLCAwLCB2YXIoLS1tZC1zaGFkb3ctYW1iaWVudC1zaGFkb3ctb3BhY2l0eSkpLFxuICAgIDAgMnB4IDRweCAtMXB4IHJnYmEoMCwgMCwgMCwgdmFyKC0tbWQtc2hhZG93LWtleS11bWJyYS1vcGFjaXR5KSk7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMSk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjMpO1xufVxuXG4uanVweXRlci13aWRnZXQtY29sb3J0YWcge1xuICBjb2xvcjogdmFyKC0tanAtaW52ZXJzZS11aS1mb250LWNvbG9yMSk7XG59XG5cbi5qdXB5dGVyLXdpZGdldC1jb2xvcnRhZy5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtdWktZm9udC1jb2xvcjApO1xufVxuXG4uanVweXRlci13aWRnZXQtdGFnaW5wdXQge1xuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IwKTtcblxuICBjdXJzb3I6IHRleHQ7XG4gIHRleHQtYWxpZ246IGxlZnQ7XG59XG5cbi5qdXB5dGVyLXdpZGdldC10YWdpbnB1dDpmb2N1cyB7XG4gIG91dGxpbmU6IG5vbmU7XG59XG5cbi5qdXB5dGVyLXdpZGdldC10YWctY2xvc2Uge1xuICBtYXJnaW4tbGVmdDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtbWFyZ2luKTtcbiAgcGFkZGluZzogMnB4IDBweCAycHggMnB4O1xufVxuXG4uanVweXRlci13aWRnZXQtdGFnLWNsb3NlOmhvdmVyIHtcbiAgY3Vyc29yOiBwb2ludGVyO1xufVxuXG4vKiBUYWcgXCJQcmltYXJ5XCIgU3R5bGluZyAqL1xuXG4uanVweXRlci13aWRnZXQtdGFnLm1vZC1wcmltYXJ5IHtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtdWktZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1icmFuZC1jb2xvcjEpO1xufVxuXG4uanVweXRlci13aWRnZXQtdGFnLm1vZC1wcmltYXJ5Lm1vZC1hY3RpdmUge1xuICBjb2xvcjogdmFyKC0tanAtaW52ZXJzZS11aS1mb250LWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWJyYW5kLWNvbG9yMCk7XG59XG5cbi8qIFRhZyBcIlN1Y2Nlc3NcIiBTdHlsaW5nICovXG5cbi5qdXB5dGVyLXdpZGdldC10YWcubW9kLXN1Y2Nlc3Mge1xuICBjb2xvcjogdmFyKC0tanAtaW52ZXJzZS11aS1mb250LWNvbG9yMSk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXN1Y2Nlc3MtY29sb3IxKTtcbn1cblxuLmp1cHl0ZXItd2lkZ2V0LXRhZy5tb2Qtc3VjY2Vzcy5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtdWktZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1zdWNjZXNzLWNvbG9yMCk7XG59XG5cbi8qIFRhZyBcIkluZm9cIiBTdHlsaW5nICovXG5cbi5qdXB5dGVyLXdpZGdldC10YWcubW9kLWluZm8ge1xuICBjb2xvcjogdmFyKC0tanAtaW52ZXJzZS11aS1mb250LWNvbG9yMSk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWluZm8tY29sb3IxKTtcbn1cblxuLmp1cHl0ZXItd2lkZ2V0LXRhZy5tb2QtaW5mby5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtdWktZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1pbmZvLWNvbG9yMCk7XG59XG5cbi8qIFRhZyBcIldhcm5pbmdcIiBTdHlsaW5nICovXG5cbi5qdXB5dGVyLXdpZGdldC10YWcubW9kLXdhcm5pbmcge1xuICBjb2xvcjogdmFyKC0tanAtaW52ZXJzZS11aS1mb250LWNvbG9yMSk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXdhcm4tY29sb3IxKTtcbn1cblxuLmp1cHl0ZXItd2lkZ2V0LXRhZy5tb2Qtd2FybmluZy5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtdWktZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC13YXJuLWNvbG9yMCk7XG59XG5cbi8qIFRhZyBcIkRhbmdlclwiIFN0eWxpbmcgKi9cblxuLmp1cHl0ZXItd2lkZ2V0LXRhZy5tb2QtZGFuZ2VyIHtcbiAgY29sb3I6IHZhcigtLWpwLWludmVyc2UtdWktZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1lcnJvci1jb2xvcjEpO1xufVxuXG4uanVweXRlci13aWRnZXQtdGFnLm1vZC1kYW5nZXIubW9kLWFjdGl2ZSB7XG4gIGNvbG9yOiB2YXIoLS1qcC1pbnZlcnNlLXVpLWZvbnQtY29sb3IwKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtZXJyb3ItY29sb3IwKTtcbn1cblxuLyogR2VuZXJhbCBCdXR0b24gU3R5bGluZyAqL1xuXG4uanVweXRlci1idXR0b24ge1xuICBwYWRkaW5nLWxlZnQ6IDEwcHg7XG4gIHBhZGRpbmctcmlnaHQ6IDEwcHg7XG4gIHBhZGRpbmctdG9wOiAwcHg7XG4gIHBhZGRpbmctYm90dG9tOiAwcHg7XG4gIGRpc3BsYXk6IGlubGluZS1ibG9jaztcbiAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgdGV4dC1vdmVyZmxvdzogZWxsaXBzaXM7XG4gIHRleHQtYWxpZ246IGNlbnRlcjtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC13aWRnZXRzLWZvbnQtc2l6ZSk7XG4gIGN1cnNvcjogcG9pbnRlcjtcblxuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGJvcmRlcjogMHB4IHNvbGlkO1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcbiAgYm94LXNoYWRvdzogbm9uZTtcblxuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IyKTtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1ib3JkZXItY29sb3IyKTtcbiAgYm9yZGVyOiBub25lO1xuICB1c2VyLXNlbGVjdDogbm9uZTtcbn1cblxuLmp1cHl0ZXItYnV0dG9uIGkuZmEge1xuICBtYXJnaW4tcmlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLW1hcmdpbik7XG4gIHBvaW50ZXItZXZlbnRzOiBub25lO1xufVxuXG4uanVweXRlci1idXR0b246ZW1wdHk6YmVmb3JlIHtcbiAgY29udGVudDogJ1xcXFwyMDBiJzsgLyogemVyby13aWR0aCBzcGFjZSAqL1xufVxuXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItYnV0dG9uOmRpc2FibGVkIHtcbiAgb3BhY2l0eTogdmFyKC0tanAtd2lkZ2V0cy1kaXNhYmxlZC1vcGFjaXR5KTtcbn1cblxuLmp1cHl0ZXItYnV0dG9uIGkuZmEuY2VudGVyIHtcbiAgbWFyZ2luLXJpZ2h0OiAwO1xufVxuXG4uanVweXRlci1idXR0b246aG92ZXI6ZW5hYmxlZCxcbi5qdXB5dGVyLWJ1dHRvbjpmb2N1czplbmFibGVkIHtcbiAgLyogTUQgTGl0ZSAyZHAgc2hhZG93ICovXG4gIGJveC1zaGFkb3c6IDAgMnB4IDJweCAwIHJnYmEoMCwgMCwgMCwgdmFyKC0tbWQtc2hhZG93LWtleS1wZW51bWJyYS1vcGFjaXR5KSksXG4gICAgMCAzcHggMXB4IC0ycHggcmdiYSgwLCAwLCAwLCB2YXIoLS1tZC1zaGFkb3cta2V5LXVtYnJhLW9wYWNpdHkpKSxcbiAgICAwIDFweCA1cHggMCByZ2JhKDAsIDAsIDAsIHZhcigtLW1kLXNoYWRvdy1hbWJpZW50LXNoYWRvdy1vcGFjaXR5KSk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbjphY3RpdmUsXG4uanVweXRlci1idXR0b24ubW9kLWFjdGl2ZSB7XG4gIC8qIE1EIExpdGUgNGRwIHNoYWRvdyAqL1xuICBib3gtc2hhZG93OiAwIDRweCA1cHggMCByZ2JhKDAsIDAsIDAsIHZhcigtLW1kLXNoYWRvdy1rZXktcGVudW1icmEtb3BhY2l0eSkpLFxuICAgIDAgMXB4IDEwcHggMCByZ2JhKDAsIDAsIDAsIHZhcigtLW1kLXNoYWRvdy1hbWJpZW50LXNoYWRvdy1vcGFjaXR5KSksXG4gICAgMCAycHggNHB4IC0xcHggcmdiYSgwLCAwLCAwLCB2YXIoLS1tZC1zaGFkb3cta2V5LXVtYnJhLW9wYWNpdHkpKTtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWZvbnQtY29sb3IxKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMyk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbjpmb2N1czplbmFibGVkIHtcbiAgb3V0bGluZTogMXB4IHNvbGlkIHZhcigtLWpwLXdpZGdldHMtaW5wdXQtZm9jdXMtYm9yZGVyLWNvbG9yKTtcbn1cblxuLyogQnV0dG9uIFwiUHJpbWFyeVwiIFN0eWxpbmcgKi9cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC1wcmltYXJ5IHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1icmFuZC1jb2xvcjEpO1xufVxuXG4uanVweXRlci1idXR0b24ubW9kLXByaW1hcnkubW9kLWFjdGl2ZSB7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1pbnZlcnNlLWZvbnQtY29sb3IwKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtYnJhbmQtY29sb3IwKTtcbn1cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC1wcmltYXJ5OmFjdGl2ZSB7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1pbnZlcnNlLWZvbnQtY29sb3IwKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtYnJhbmQtY29sb3IwKTtcbn1cblxuLyogQnV0dG9uIFwiU3VjY2Vzc1wiIFN0eWxpbmcgKi9cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC1zdWNjZXNzIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1zdWNjZXNzLWNvbG9yMSk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbi5tb2Qtc3VjY2Vzcy5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1zdWNjZXNzLWNvbG9yMCk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbi5tb2Qtc3VjY2VzczphY3RpdmUge1xuICBjb2xvcjogdmFyKC0tanAtdWktaW52ZXJzZS1mb250LWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXN1Y2Nlc3MtY29sb3IwKTtcbn1cblxuLyogQnV0dG9uIFwiSW5mb1wiIFN0eWxpbmcgKi9cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC1pbmZvIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1pbmZvLWNvbG9yMSk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbi5tb2QtaW5mby5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1pbmZvLWNvbG9yMCk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbi5tb2QtaW5mbzphY3RpdmUge1xuICBjb2xvcjogdmFyKC0tanAtdWktaW52ZXJzZS1mb250LWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWluZm8tY29sb3IwKTtcbn1cblxuLyogQnV0dG9uIFwiV2FybmluZ1wiIFN0eWxpbmcgKi9cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC13YXJuaW5nIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjEpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC13YXJuLWNvbG9yMSk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbi5tb2Qtd2FybmluZy5tb2QtYWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC13YXJuLWNvbG9yMCk7XG59XG5cbi5qdXB5dGVyLWJ1dHRvbi5tb2Qtd2FybmluZzphY3RpdmUge1xuICBjb2xvcjogdmFyKC0tanAtdWktaW52ZXJzZS1mb250LWNvbG9yMCk7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXdhcm4tY29sb3IwKTtcbn1cblxuLyogQnV0dG9uIFwiRGFuZ2VyXCIgU3R5bGluZyAqL1xuXG4uanVweXRlci1idXR0b24ubW9kLWRhbmdlciB7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1pbnZlcnNlLWZvbnQtY29sb3IxKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtZXJyb3ItY29sb3IxKTtcbn1cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC1kYW5nZXIubW9kLWFjdGl2ZSB7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1pbnZlcnNlLWZvbnQtY29sb3IwKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtZXJyb3ItY29sb3IwKTtcbn1cblxuLmp1cHl0ZXItYnV0dG9uLm1vZC1kYW5nZXI6YWN0aXZlIHtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1lcnJvci1jb2xvcjApO1xufVxuXG4vKiBXaWRnZXQgQnV0dG9uLCBXaWRnZXQgVG9nZ2xlIEJ1dHRvbiwgV2lkZ2V0IFVwbG9hZCAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtYnV0dG9uLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLndpZGdldC10b2dnbGUtYnV0dG9uLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLndpZGdldC11cGxvYWQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1idXR0b24sXG4uanVweXRlci13aWRnZXQtdG9nZ2xlLWJ1dHRvbixcbi5qdXB5dGVyLXdpZGdldC11cGxvYWQge1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgtc2hvcnQpO1xufVxuXG4vKiBXaWRnZXQgTGFiZWwgU3R5bGluZyAqL1xuXG4vKiBPdmVycmlkZSBCb290c3RyYXAgbGFiZWwgY3NzICovXG4uanVweXRlci13aWRnZXRzIGxhYmVsIHtcbiAgbWFyZ2luLWJvdHRvbTogaW5pdGlhbDtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWxhYmVsLWJhc2ljLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtbGFiZWwtYmFzaWMge1xuICAvKiBCYXNpYyBMYWJlbCAqL1xuICBjb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1sYWJlbC1jb2xvcik7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtd2lkZ2V0cy1mb250LXNpemUpO1xuICBvdmVyZmxvdzogaGlkZGVuO1xuICB0ZXh0LW92ZXJmbG93OiBlbGxpcHNpcztcbiAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1sYWJlbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWxhYmVsIHtcbiAgLyogTGFiZWwgKi9cbiAgY29sb3I6IHZhcigtLWpwLXdpZGdldHMtbGFiZWwtY29sb3IpO1xuICBmb250LXNpemU6IHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKTtcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgdGV4dC1vdmVyZmxvdzogZWxsaXBzaXM7XG4gIHdoaXRlLXNwYWNlOiBub3dyYXA7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtaW5saW5lLWhib3ggLndpZGdldC1sYWJlbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWlubGluZS1oYm94IC5qdXB5dGVyLXdpZGdldC1sYWJlbCB7XG4gIC8qIEhvcml6b250YWwgV2lkZ2V0IExhYmVsICovXG4gIGNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWxhYmVsLWNvbG9yKTtcbiAgdGV4dC1hbGlnbjogcmlnaHQ7XG4gIG1hcmdpbi1yaWdodDogY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlubGluZS1tYXJnaW4pICogMik7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1sYWJlbC13aWR0aCk7XG4gIGZsZXgtc2hyaW5rOiAwO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtaW5saW5lLXZib3ggLndpZGdldC1sYWJlbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWlubGluZS12Ym94IC5qdXB5dGVyLXdpZGdldC1sYWJlbCB7XG4gIC8qIFZlcnRpY2FsIFdpZGdldCBMYWJlbCAqL1xuICBjb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1sYWJlbC1jb2xvcik7XG4gIHRleHQtYWxpZ246IGNlbnRlcjtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG59XG5cbi8qIFdpZGdldCBSZWFkb3V0IFN0eWxpbmcgKi9cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXJlYWRvdXQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1yZWFkb3V0IHtcbiAgY29sb3I6IHZhcigtLWpwLXdpZGdldHMtcmVhZG91dC1jb2xvcik7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtd2lkZ2V0cy1mb250LXNpemUpO1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICBvdmVyZmxvdzogaGlkZGVuO1xuICB3aGl0ZS1zcGFjZTogbm93cmFwO1xuICB0ZXh0LWFsaWduOiBjZW50ZXI7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1yZWFkb3V0Lm92ZXJmbG93LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtcmVhZG91dC5vdmVyZmxvdyB7XG4gIC8qIE92ZXJmbG93aW5nIFJlYWRvdXQgKi9cblxuICAvKiBGcm9tIE1hdGVyaWFsIERlc2lnbiBMaXRlXG4gICAgICAgIHNoYWRvdy1rZXktdW1icmEtb3BhY2l0eTogMC4yO1xuICAgICAgICBzaGFkb3cta2V5LXBlbnVtYnJhLW9wYWNpdHk6IDAuMTQ7XG4gICAgICAgIHNoYWRvdy1hbWJpZW50LXNoYWRvdy1vcGFjaXR5OiAwLjEyO1xuICAgICAqL1xuICAtd2Via2l0LWJveC1zaGFkb3c6IDAgMnB4IDJweCAwIHJnYmEoMCwgMCwgMCwgMC4yKSxcbiAgICAwIDNweCAxcHggLTJweCByZ2JhKDAsIDAsIDAsIDAuMTQpLCAwIDFweCA1cHggMCByZ2JhKDAsIDAsIDAsIDAuMTIpO1xuXG4gIC1tb3otYm94LXNoYWRvdzogMCAycHggMnB4IDAgcmdiYSgwLCAwLCAwLCAwLjIpLFxuICAgIDAgM3B4IDFweCAtMnB4IHJnYmEoMCwgMCwgMCwgMC4xNCksIDAgMXB4IDVweCAwIHJnYmEoMCwgMCwgMCwgMC4xMik7XG5cbiAgYm94LXNoYWRvdzogMCAycHggMnB4IDAgcmdiYSgwLCAwLCAwLCAwLjIpLCAwIDNweCAxcHggLTJweCByZ2JhKDAsIDAsIDAsIDAuMTQpLFxuICAgIDAgMXB4IDVweCAwIHJnYmEoMCwgMCwgMCwgMC4xMik7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1pbmxpbmUtaGJveCAud2lkZ2V0LXJlYWRvdXQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1pbmxpbmUtaGJveCAuanVweXRlci13aWRnZXQtcmVhZG91dCB7XG4gIC8qIEhvcml6b250YWwgUmVhZG91dCAqL1xuICB0ZXh0LWFsaWduOiBjZW50ZXI7XG4gIG1heC13aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgtc2hvcnQpO1xuICBtaW4td2lkdGg6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoLXRpbnkpO1xuICBtYXJnaW4tbGVmdDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtbWFyZ2luKTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWlubGluZS12Ym94IC53aWRnZXQtcmVhZG91dCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWlubGluZS12Ym94IC5qdXB5dGVyLXdpZGdldC1yZWFkb3V0IHtcbiAgLyogVmVydGljYWwgUmVhZG91dCAqL1xuICBtYXJnaW4tdG9wOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1tYXJnaW4pO1xuICAvKiBhcyB3aWRlIGFzIHRoZSB3aWRnZXQgKi9cbiAgd2lkdGg6IGluaGVyaXQ7XG59XG5cbi8qIFdpZGdldCBDaGVja2JveCBTdHlsaW5nICovXG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1jaGVja2JveCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWNoZWNrYm94IHtcbiAgd2lkdGg6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoKTtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWNoZWNrYm94IGlucHV0W3R5cGU9J2NoZWNrYm94J10sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1jaGVja2JveCBpbnB1dFt0eXBlPSdjaGVja2JveCddIHtcbiAgbWFyZ2luOiAwcHggY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlubGluZS1tYXJnaW4pICogMikgMHB4IDBweDtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGZvbnQtc2l6ZTogbGFyZ2U7XG4gIGZsZXgtZ3JvdzogMTtcbiAgZmxleC1zaHJpbms6IDA7XG4gIGFsaWduLXNlbGY6IGNlbnRlcjtcbn1cblxuLyogV2lkZ2V0IFZhbGlkIFN0eWxpbmcgKi9cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXZhbGlkLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtdmFsaWQge1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgtc2hvcnQpO1xuICBmb250LXNpemU6IHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXZhbGlkIGksIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC12YWxpZCBpIHtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIG1hcmdpbi1yaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtbWFyZ2luKTtcbiAgbWFyZ2luLWxlZnQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLW1hcmdpbik7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC12YWxpZC5tb2QtdmFsaWQgaSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXZhbGlkLm1vZC12YWxpZCBpIHtcbiAgY29sb3I6IGdyZWVuO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdmFsaWQubW9kLWludmFsaWQgaSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXZhbGlkLm1vZC1pbnZhbGlkIGkge1xuICBjb2xvcjogcmVkO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdmFsaWQubW9kLXZhbGlkIC53aWRnZXQtdmFsaWQtcmVhZG91dCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXZhbGlkLm1vZC12YWxpZCAuanVweXRlci13aWRnZXQtdmFsaWQtcmVhZG91dCB7XG4gIGRpc3BsYXk6IG5vbmU7XG59XG5cbi8qIFdpZGdldCBUZXh0IGFuZCBUZXh0QXJlYSBTdHlsaW5nICovXG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC10ZXh0YXJlYSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC53aWRnZXQtdGV4dCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXRleHRhcmVhLFxuLmp1cHl0ZXItd2lkZ2V0LXRleHQge1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSd0ZXh0J10sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAud2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0nbnVtYmVyJ10sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAud2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0ncGFzc3dvcmQnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0ndGV4dCddLFxuLmp1cHl0ZXItd2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0nbnVtYmVyJ10sXG4uanVweXRlci13aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSdwYXNzd29yZCddIHtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSd0ZXh0J106ZGlzYWJsZWQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAud2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0nbnVtYmVyJ106ZGlzYWJsZWQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAud2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0ncGFzc3dvcmQnXTpkaXNhYmxlZCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC53aWRnZXQtdGV4dGFyZWEgdGV4dGFyZWE6ZGlzYWJsZWQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC10ZXh0IGlucHV0W3R5cGU9J3RleHQnXTpkaXNhYmxlZCxcbi5qdXB5dGVyLXdpZGdldC10ZXh0IGlucHV0W3R5cGU9J251bWJlciddOmRpc2FibGVkLFxuLmp1cHl0ZXItd2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0ncGFzc3dvcmQnXTpkaXNhYmxlZCxcbi5qdXB5dGVyLXdpZGdldC10ZXh0YXJlYSB0ZXh0YXJlYTpkaXNhYmxlZCB7XG4gIG9wYWNpdHk6IHZhcigtLWpwLXdpZGdldHMtZGlzYWJsZWQtb3BhY2l0eSk7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC10ZXh0IGlucHV0W3R5cGU9J3RleHQnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC53aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSdudW1iZXInXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC53aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSdwYXNzd29yZCddLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLndpZGdldC10ZXh0YXJlYSB0ZXh0YXJlYSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0ndGV4dCddLFxuLmp1cHl0ZXItd2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0nbnVtYmVyJ10sXG4uanVweXRlci13aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSdwYXNzd29yZCddLFxuLmp1cHl0ZXItd2lkZ2V0LXRleHRhcmVhIHRleHRhcmVhIHtcbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgYm9yZGVyOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJvcmRlci13aWR0aCkgc29saWRcbiAgICB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJvcmRlci1jb2xvcik7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtYmFja2dyb3VuZC1jb2xvcik7XG4gIGNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWNvbG9yKTtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC13aWRnZXRzLWZvbnQtc2l6ZSk7XG4gIGZsZXgtZ3JvdzogMTtcbiAgbWluLXdpZHRoOiAwOyAvKiBUaGlzIG1ha2VzIGl0IHBvc3NpYmxlIGZvciB0aGUgZmxleGJveCB0byBzaHJpbmsgdGhpcyBpbnB1dCAqL1xuICBmbGV4LXNocmluazogMTtcbiAgb3V0bGluZTogbm9uZSAhaW1wb3J0YW50O1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSd0ZXh0J10sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAud2lkZ2V0LXRleHQgaW5wdXRbdHlwZT0ncGFzc3dvcmQnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC53aWRnZXQtdGV4dGFyZWEgdGV4dGFyZWEsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC10ZXh0IGlucHV0W3R5cGU9J3RleHQnXSxcbi5qdXB5dGVyLXdpZGdldC10ZXh0IGlucHV0W3R5cGU9J3Bhc3N3b3JkJ10sXG4uanVweXRlci13aWRnZXQtdGV4dGFyZWEgdGV4dGFyZWEge1xuICBwYWRkaW5nOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpXG4gICAgY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpICogMik7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC10ZXh0IGlucHV0W3R5cGU9J251bWJlciddLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtdGV4dCBpbnB1dFt0eXBlPSdudW1iZXInXSB7XG4gIHBhZGRpbmc6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtcGFkZGluZykgMCB2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpXG4gICAgY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpICogMik7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC10ZXh0YXJlYSB0ZXh0YXJlYSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXRleHRhcmVhIHRleHRhcmVhIHtcbiAgaGVpZ2h0OiBpbmhlcml0O1xuICB3aWR0aDogaW5oZXJpdDtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXRleHQgaW5wdXQ6Zm9jdXMsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAud2lkZ2V0LXRleHRhcmVhIHRleHRhcmVhOmZvY3VzLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtdGV4dCBpbnB1dDpmb2N1cyxcbi5qdXB5dGVyLXdpZGdldC10ZXh0YXJlYSB0ZXh0YXJlYTpmb2N1cyB7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1mb2N1cy1ib3JkZXItY29sb3IpO1xufVxuXG4vKiBIb3Jpem9udGFsIFNsaWRlciAqL1xuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWhzbGlkZXIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1oc2xpZGVyIHtcbiAgd2lkdGg6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoKTtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcblxuICAvKiBPdmVycmlkZSB0aGUgYWxpZ24taXRlbXMgYmFzZWxpbmUuIFRoaXMgd2F5LCB0aGUgZGVzY3JpcHRpb24gYW5kIHJlYWRvdXRcbiAgICBzdGlsbCBzZWVtIHRvIGFsaWduIHRoZWlyIGJhc2VsaW5lIHByb3Blcmx5LCBhbmQgd2UgZG9uJ3QgaGF2ZSB0byBoYXZlXG4gICAgYWxpZ24tc2VsZjogc3RyZXRjaCBpbiB0aGUgLnNsaWRlci1jb250YWluZXIuICovXG4gIGFsaWduLWl0ZW1zOiBjZW50ZXI7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldHMtc2xpZGVyIC5zbGlkZXItY29udGFpbmVyLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLXNsaWRlciAuc2xpZGVyLWNvbnRhaW5lciB7XG4gIG92ZXJmbG93OiB2aXNpYmxlO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtaHNsaWRlciAuc2xpZGVyLWNvbnRhaW5lciwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWhzbGlkZXIgLnNsaWRlci1jb250YWluZXIge1xuICBtYXJnaW4tbGVmdDogY2FsYyhcbiAgICB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1oYW5kbGUtc2l6ZSkgLyAyIC0gMiAqXG4gICAgICB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1ib3JkZXItd2lkdGgpXG4gICk7XG4gIG1hcmdpbi1yaWdodDogY2FsYyhcbiAgICB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1oYW5kbGUtc2l6ZSkgLyAyIC0gMiAqXG4gICAgICB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1ib3JkZXItd2lkdGgpXG4gICk7XG4gIGZsZXg6IDEgMSB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC1zaG9ydCk7XG59XG5cbi8qIFZlcnRpY2FsIFNsaWRlciAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdmJveCAud2lkZ2V0LWxhYmVsLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtdmJveCAuanVweXRlci13aWRnZXQtbGFiZWwge1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdnNsaWRlciwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXZzbGlkZXIge1xuICAvKiBWZXJ0aWNhbCBTbGlkZXIgKi9cbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLXZlcnRpY2FsLWhlaWdodCk7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC10aW55KTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXZzbGlkZXIgLnNsaWRlci1jb250YWluZXIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC12c2xpZGVyIC5zbGlkZXItY29udGFpbmVyIHtcbiAgZmxleDogMSAxIHZhcigtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoLXNob3J0KTtcbiAgbWFyZ2luLWxlZnQ6IGF1dG87XG4gIG1hcmdpbi1yaWdodDogYXV0bztcbiAgbWFyZ2luLWJvdHRvbTogY2FsYyhcbiAgICB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1oYW5kbGUtc2l6ZSkgLyAyIC0gMiAqXG4gICAgICB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1ib3JkZXItd2lkdGgpXG4gICk7XG4gIG1hcmdpbi10b3A6IGNhbGMoXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLXNpemUpIC8gMiAtIDIgKlxuICAgICAgdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItYm9yZGVyLXdpZHRoKVxuICApO1xuICBkaXNwbGF5OiBmbGV4O1xuICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xufVxuXG4vKiBXaWRnZXQgUHJvZ3Jlc3MgU3R5bGluZyAqL1xuXG4ucHJvZ3Jlc3MtYmFyIHtcbiAgLXdlYmtpdC10cmFuc2l0aW9uOiBub25lO1xuICAtbW96LXRyYW5zaXRpb246IG5vbmU7XG4gIC1tcy10cmFuc2l0aW9uOiBub25lO1xuICAtby10cmFuc2l0aW9uOiBub25lO1xuICB0cmFuc2l0aW9uOiBub25lO1xufVxuXG4ucHJvZ3Jlc3MtYmFyIHtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4ucHJvZ3Jlc3MtYmFyIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtYnJhbmQtY29sb3IxKTtcbn1cblxuLnByb2dyZXNzLWJhci1zdWNjZXNzIHtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtc3VjY2Vzcy1jb2xvcjEpO1xufVxuXG4ucHJvZ3Jlc3MtYmFyLWluZm8ge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1pbmZvLWNvbG9yMSk7XG59XG5cbi5wcm9ncmVzcy1iYXItd2FybmluZyB7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXdhcm4tY29sb3IxKTtcbn1cblxuLnByb2dyZXNzLWJhci1kYW5nZXIge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1lcnJvci1jb2xvcjEpO1xufVxuXG4ucHJvZ3Jlc3Mge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IyKTtcbiAgYm9yZGVyOiBub25lO1xuICBib3gtc2hhZG93OiBub25lO1xufVxuXG4vKiBIb3Jpc29udGFsIFByb2dyZXNzICovXG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1ocHJvZ3Jlc3MsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1ocHJvZ3Jlc3Mge1xuICAvKiBQcm9ncmVzcyBCYXIgKi9cbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcbiAgd2lkdGg6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoKTtcbiAgYWxpZ24taXRlbXM6IGNlbnRlcjtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWhwcm9ncmVzcyAucHJvZ3Jlc3MsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1ocHJvZ3Jlc3MgLnByb2dyZXNzIHtcbiAgZmxleC1ncm93OiAxO1xuICBtYXJnaW4tdG9wOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpO1xuICBtYXJnaW4tYm90dG9tOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpO1xuICBhbGlnbi1zZWxmOiBzdHJldGNoO1xuICAvKiBPdmVycmlkZSBib290c3RyYXAgc3R5bGUgKi9cbiAgaGVpZ2h0OiBpbml0aWFsO1xufVxuXG4vKiBWZXJ0aWNhbCBQcm9ncmVzcyAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdnByb2dyZXNzLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtdnByb2dyZXNzIHtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLXZlcnRpY2FsLWhlaWdodCk7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC10aW55KTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXZwcm9ncmVzcyAucHJvZ3Jlc3MsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC12cHJvZ3Jlc3MgLnByb2dyZXNzIHtcbiAgZmxleC1ncm93OiAxO1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1wcm9ncmVzcy10aGlja25lc3MpO1xuICBtYXJnaW4tbGVmdDogYXV0bztcbiAgbWFyZ2luLXJpZ2h0OiBhdXRvO1xuICBtYXJnaW4tYm90dG9tOiAwO1xufVxuXG4vKiBTZWxlY3QgV2lkZ2V0IFN0eWxpbmcgKi9cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWRyb3Bkb3duLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtZHJvcGRvd24ge1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtZHJvcGRvd24gPiBzZWxlY3QsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1kcm9wZG93biA+IHNlbGVjdCB7XG4gIHBhZGRpbmctcmlnaHQ6IDIwcHg7XG4gIGJvcmRlcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItd2lkdGgpIHNvbGlkXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItY29sb3IpO1xuICBib3JkZXItcmFkaXVzOiAwO1xuICBoZWlnaHQ6IGluaGVyaXQ7XG4gIGZsZXg6IDEgMSB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC1zaG9ydCk7XG4gIG1pbi13aWR0aDogMDsgLyogVGhpcyBtYWtlcyBpdCBwb3NzaWJsZSBmb3IgdGhlIGZsZXhib3ggdG8gc2hyaW5rIHRoaXMgaW5wdXQgKi9cbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgb3V0bGluZTogbm9uZSAhaW1wb3J0YW50O1xuICBib3gtc2hhZG93OiBub25lO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJhY2tncm91bmQtY29sb3IpO1xuICBjb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1jb2xvcik7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtd2lkZ2V0cy1mb250LXNpemUpO1xuICB2ZXJ0aWNhbC1hbGlnbjogdG9wO1xuICBwYWRkaW5nLWxlZnQ6IGNhbGModmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1wYWRkaW5nKSAqIDIpO1xuICBhcHBlYXJhbmNlOiBub25lO1xuICAtd2Via2l0LWFwcGVhcmFuY2U6IG5vbmU7XG4gIC1tb3otYXBwZWFyYW5jZTogbm9uZTtcbiAgYmFja2dyb3VuZC1yZXBlYXQ6IG5vLXJlcGVhdDtcbiAgYmFja2dyb3VuZC1zaXplOiAyMHB4O1xuICBiYWNrZ3JvdW5kLXBvc2l0aW9uOiByaWdodCBjZW50ZXI7XG4gIGJhY2tncm91bmQtaW1hZ2U6IHZhcigtLWpwLXdpZGdldHMtZHJvcGRvd24tYXJyb3cpO1xufVxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWRyb3Bkb3duID4gc2VsZWN0OmZvY3VzLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtZHJvcGRvd24gPiBzZWxlY3Q6Zm9jdXMge1xuICBib3JkZXItY29sb3I6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtZm9jdXMtYm9yZGVyLWNvbG9yKTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWRyb3Bkb3duID4gc2VsZWN0OmRpc2FibGVkLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtZHJvcGRvd24gPiBzZWxlY3Q6ZGlzYWJsZWQge1xuICBvcGFjaXR5OiB2YXIoLS1qcC13aWRnZXRzLWRpc2FibGVkLW9wYWNpdHkpO1xufVxuXG4vKiBUbyBkaXNhYmxlIHRoZSBkb3R0ZWQgYm9yZGVyIGluIEZpcmVmb3ggYXJvdW5kIHNlbGVjdCBjb250cm9scy5cbiAgIFNlZSBodHRwOi8vc3RhY2tvdmVyZmxvdy5jb20vYS8xODg1MzAwMiAqL1xuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWRyb3Bkb3duID4gc2VsZWN0Oi1tb3otZm9jdXNyaW5nLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtZHJvcGRvd24gPiBzZWxlY3Q6LW1vei1mb2N1c3Jpbmcge1xuICBjb2xvcjogdHJhbnNwYXJlbnQ7XG4gIHRleHQtc2hhZG93OiAwIDAgMCAjMDAwO1xufVxuXG4vKiBTZWxlY3QgYW5kIFNlbGVjdE11bHRpcGxlICovXG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1zZWxlY3QsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1zZWxlY3Qge1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgpO1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcblxuICAvKiBCZWNhdXNlIEZpcmVmb3ggZGVmaW5lcyB0aGUgYmFzZWxpbmUgb2YgYSBzZWxlY3QgYXMgdGhlIGJvdHRvbSBvZiB0aGVcbiAgICBjb250cm9sLCB3ZSBhbGlnbiB0aGUgZW50aXJlIGNvbnRyb2wgdG8gdGhlIHRvcCBhbmQgYWRkIHBhZGRpbmcgdG8gdGhlXG4gICAgc2VsZWN0IHRvIGdldCBhbiBhcHByb3hpbWF0ZSBmaXJzdCBsaW5lIGJhc2VsaW5lIGFsaWdubWVudC4gKi9cbiAgYWxpZ24taXRlbXM6IGZsZXgtc3RhcnQ7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1zZWxlY3QgPiBzZWxlY3QsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1zZWxlY3QgPiBzZWxlY3Qge1xuICBib3JkZXI6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtYm9yZGVyLXdpZHRoKSBzb2xpZFxuICAgIHZhcigtLWpwLXdpZGdldHMtaW5wdXQtYm9yZGVyLWNvbG9yKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1iYWNrZ3JvdW5kLWNvbG9yKTtcbiAgY29sb3I6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtY29sb3IpO1xuICBmb250LXNpemU6IHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKTtcbiAgZmxleDogMSAxIHZhcigtLWpwLXdpZGdldHMtaW5saW5lLXdpZHRoLXNob3J0KTtcbiAgb3V0bGluZTogbm9uZSAhaW1wb3J0YW50O1xuICBvdmVyZmxvdzogYXV0bztcbiAgaGVpZ2h0OiBpbmhlcml0O1xuXG4gIC8qIEJlY2F1c2UgRmlyZWZveCBkZWZpbmVzIHRoZSBiYXNlbGluZSBvZiBhIHNlbGVjdCBhcyB0aGUgYm90dG9tIG9mIHRoZVxuICAgIGNvbnRyb2wsIHdlIGFsaWduIHRoZSBlbnRpcmUgY29udHJvbCB0byB0aGUgdG9wIGFuZCBhZGQgcGFkZGluZyB0byB0aGVcbiAgICBzZWxlY3QgdG8gZ2V0IGFuIGFwcHJveGltYXRlIGZpcnN0IGxpbmUgYmFzZWxpbmUgYWxpZ25tZW50LiAqL1xuICBwYWRkaW5nLXRvcDogNXB4O1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtc2VsZWN0ID4gc2VsZWN0OmZvY3VzLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtc2VsZWN0ID4gc2VsZWN0OmZvY3VzIHtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWZvY3VzLWJvcmRlci1jb2xvcik7XG59XG5cbi53aWdldC1zZWxlY3QgPiBzZWxlY3QgPiBvcHRpb24sXG4uanVweXRlci13aWdldC1zZWxlY3QgPiBzZWxlY3QgPiBvcHRpb24ge1xuICBwYWRkaW5nLWxlZnQ6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtcGFkZGluZyk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICAvKiBsaW5lLWhlaWdodCBkb2Vzbid0IHdvcmsgb24gc29tZSBicm93c2VycyBmb3Igc2VsZWN0IG9wdGlvbnMgKi9cbiAgcGFkZGluZy10b3A6IGNhbGMoXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KSAtIHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKSAvIDJcbiAgKTtcbiAgcGFkZGluZy1ib3R0b206IGNhbGMoXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KSAtIHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKSAvIDJcbiAgKTtcbn1cblxuLyogVG9nZ2xlIEJ1dHRvbnMgU3R5bGluZyAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdG9nZ2xlLWJ1dHRvbnMsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC10b2dnbGUtYnV0dG9ucyB7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtdG9nZ2xlLWJ1dHRvbnMgLndpZGdldC10b2dnbGUtYnV0dG9uLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtdG9nZ2xlLWJ1dHRvbnMgLmp1cHl0ZXItd2lkZ2V0LXRvZ2dsZS1idXR0b24ge1xuICBtYXJnaW4tbGVmdDogdmFyKC0tanAtd2lkZ2V0cy1tYXJnaW4pO1xuICBtYXJnaW4tcmlnaHQ6IHZhcigtLWpwLXdpZGdldHMtbWFyZ2luKTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXRvZ2dsZS1idXR0b25zIC5qdXB5dGVyLWJ1dHRvbjpkaXNhYmxlZCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXRvZ2dsZS1idXR0b25zIC5qdXB5dGVyLWJ1dHRvbjpkaXNhYmxlZCB7XG4gIG9wYWNpdHk6IHZhcigtLWpwLXdpZGdldHMtZGlzYWJsZWQtb3BhY2l0eSk7XG59XG5cbi8qIFJhZGlvIEJ1dHRvbnMgU3R5bGluZyAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtcmFkaW8sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1yYWRpbyB7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtcmFkaW8tYm94LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtcmFkaW8tYm94IHtcbiAgZGlzcGxheTogZmxleDtcbiAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgYWxpZ24taXRlbXM6IHN0cmV0Y2g7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG4gIGZsZXgtZ3JvdzogMTtcbiAgbWFyZ2luLWJvdHRvbTogdmFyKC0tanAtd2lkZ2V0cy1yYWRpby1pdGVtLWhlaWdodC1hZGp1c3RtZW50KTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXJhZGlvLWJveC12ZXJ0aWNhbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXJhZGlvLWJveC12ZXJ0aWNhbCB7XG4gIGZsZXgtZGlyZWN0aW9uOiBjb2x1bW47XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1yYWRpby1ib3gtaG9yaXpvbnRhbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXJhZGlvLWJveC1ob3Jpem9udGFsIHtcbiAgZmxleC1kaXJlY3Rpb246IHJvdztcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LXJhZGlvLWJveCBsYWJlbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LXJhZGlvLWJveCBsYWJlbCB7XG4gIGhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1yYWRpby1pdGVtLWhlaWdodCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLXJhZGlvLWl0ZW0taGVpZ2h0KTtcbiAgZm9udC1zaXplOiB2YXIoLS1qcC13aWRnZXRzLWZvbnQtc2l6ZSk7XG59XG5cbi53aWRnZXQtcmFkaW8tYm94LWhvcml6b250YWwgbGFiZWwsXG4uanVweXRlci13aWRnZXQtcmFkaW8tYm94LWhvcml6b250YWwgbGFiZWwge1xuICBtYXJnaW46IDAgY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpICogMikgMCAwO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtcmFkaW8tYm94IGlucHV0LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtcmFkaW8tYm94IGlucHV0IHtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLXJhZGlvLWl0ZW0taGVpZ2h0KTtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtcmFkaW8taXRlbS1oZWlnaHQpO1xuICBtYXJnaW46IDAgY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpICogMikgMCAxcHg7XG4gIGZsb2F0OiBsZWZ0O1xufVxuXG4vKiBDb2xvciBQaWNrZXIgU3R5bGluZyAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtY29sb3JwaWNrZXIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1jb2xvcnBpY2tlciB7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aCk7XG4gIGhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcbiAgbGluZS1oZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1jb2xvcnBpY2tlciA+IC53aWRnZXQtY29sb3JwaWNrZXItaW5wdXQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1jb2xvcnBpY2tlciA+IC5qdXB5dGVyLXdpZGdldC1jb2xvcnBpY2tlci1pbnB1dCB7XG4gIGZsZXgtZ3JvdzogMTtcbiAgZmxleC1zaHJpbms6IDE7XG4gIG1pbi13aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgtdGlueSk7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1jb2xvcnBpY2tlciBpbnB1dFt0eXBlPSdjb2xvciddLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtY29sb3JwaWNrZXIgaW5wdXRbdHlwZT0nY29sb3InXSB7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIHBhZGRpbmc6IDAgMnB4OyAvKiBtYWtlIHRoZSBjb2xvciBzcXVhcmUgYWN0dWFsbHkgc3F1YXJlIG9uIENocm9tZSBvbiBPUyBYICovXG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtYmFja2dyb3VuZC1jb2xvcik7XG4gIGNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWNvbG9yKTtcbiAgYm9yZGVyOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJvcmRlci13aWR0aCkgc29saWRcbiAgICB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJvcmRlci1jb2xvcik7XG4gIGJvcmRlci1sZWZ0OiBub25lO1xuICBmbGV4LWdyb3c6IDA7XG4gIGZsZXgtc2hyaW5rOiAwO1xuICBib3gtc2l6aW5nOiBib3JkZXItYm94O1xuICBhbGlnbi1zZWxmOiBzdHJldGNoO1xuICBvdXRsaW5lOiBub25lICFpbXBvcnRhbnQ7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1jb2xvcnBpY2tlci5jb25jaXNlIGlucHV0W3R5cGU9J2NvbG9yJ10sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1jb2xvcnBpY2tlci5jb25jaXNlIGlucHV0W3R5cGU9J2NvbG9yJ10ge1xuICBib3JkZXItbGVmdDogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItd2lkdGgpIHNvbGlkXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItY29sb3IpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtY29sb3JwaWNrZXIgaW5wdXRbdHlwZT0nY29sb3InXTpmb2N1cywgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC53aWRnZXQtY29sb3JwaWNrZXIgaW5wdXRbdHlwZT0ndGV4dCddOmZvY3VzLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtY29sb3JwaWNrZXIgaW5wdXRbdHlwZT0nY29sb3InXTpmb2N1cyxcbi5qdXB5dGVyLXdpZGdldC1jb2xvcnBpY2tlciBpbnB1dFt0eXBlPSd0ZXh0J106Zm9jdXMge1xuICBib3JkZXItY29sb3I6IHZhcigtLWpwLXdpZGdldHMtaW5wdXQtZm9jdXMtYm9yZGVyLWNvbG9yKTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWNvbG9ycGlja2VyIGlucHV0W3R5cGU9J3RleHQnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWNvbG9ycGlja2VyIGlucHV0W3R5cGU9J3RleHQnXSB7XG4gIGZsZXgtZ3JvdzogMTtcbiAgb3V0bGluZTogbm9uZSAhaW1wb3J0YW50O1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xuICBiYWNrZ3JvdW5kOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJhY2tncm91bmQtY29sb3IpO1xuICBjb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1jb2xvcik7XG4gIGJvcmRlcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItd2lkdGgpIHNvbGlkXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItY29sb3IpO1xuICBmb250LXNpemU6IHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKTtcbiAgcGFkZGluZzogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1wYWRkaW5nKVxuICAgIGNhbGModmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1wYWRkaW5nKSAqIDIpO1xuICBtaW4td2lkdGg6IDA7IC8qIFRoaXMgbWFrZXMgaXQgcG9zc2libGUgZm9yIHRoZSBmbGV4Ym94IHRvIHNocmluayB0aGlzIGlucHV0ICovXG4gIGZsZXgtc2hyaW5rOiAxO1xuICBib3gtc2l6aW5nOiBib3JkZXItYm94O1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtY29sb3JwaWNrZXIgaW5wdXRbdHlwZT0ndGV4dCddOmRpc2FibGVkLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtY29sb3JwaWNrZXIgaW5wdXRbdHlwZT0ndGV4dCddOmRpc2FibGVkIHtcbiAgb3BhY2l0eTogdmFyKC0tanAtd2lkZ2V0cy1kaXNhYmxlZC1vcGFjaXR5KTtcbn1cblxuLyogRGF0ZSBQaWNrZXIgU3R5bGluZyAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtZGF0ZXBpY2tlciwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWRhdGVwaWNrZXIge1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtd2lkdGgpO1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS1oZWlnaHQpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtZGF0ZXBpY2tlciBpbnB1dFt0eXBlPSdkYXRlJ10sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1kYXRlcGlja2VyIGlucHV0W3R5cGU9J2RhdGUnXSB7XG4gIGZsZXgtZ3JvdzogMTtcbiAgZmxleC1zaHJpbms6IDE7XG4gIG1pbi13aWR0aDogMDsgLyogVGhpcyBtYWtlcyBpdCBwb3NzaWJsZSBmb3IgdGhlIGZsZXhib3ggdG8gc2hyaW5rIHRoaXMgaW5wdXQgKi9cbiAgb3V0bGluZTogbm9uZSAhaW1wb3J0YW50O1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaW5saW5lLWhlaWdodCk7XG4gIGJvcmRlcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItd2lkdGgpIHNvbGlkXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1ib3JkZXItY29sb3IpO1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWJhY2tncm91bmQtY29sb3IpO1xuICBjb2xvcjogdmFyKC0tanAtd2lkZ2V0cy1pbnB1dC1jb2xvcik7XG4gIGZvbnQtc2l6ZTogdmFyKC0tanAtd2lkZ2V0cy1mb250LXNpemUpO1xuICBwYWRkaW5nOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpXG4gICAgY2FsYyh2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpICogMik7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1kYXRlcGlja2VyIGlucHV0W3R5cGU9J2RhdGUnXTpmb2N1cywgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWRhdGVwaWNrZXIgaW5wdXRbdHlwZT0nZGF0ZSddOmZvY3VzIHtcbiAgYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LWZvY3VzLWJvcmRlci1jb2xvcik7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1kYXRlcGlja2VyIGlucHV0W3R5cGU9J2RhdGUnXTppbnZhbGlkLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtZGF0ZXBpY2tlciBpbnB1dFt0eXBlPSdkYXRlJ106aW52YWxpZCB7XG4gIGJvcmRlci1jb2xvcjogdmFyKC0tanAtd2Fybi1jb2xvcjEpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtZGF0ZXBpY2tlciBpbnB1dFt0eXBlPSdkYXRlJ106ZGlzYWJsZWQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1kYXRlcGlja2VyIGlucHV0W3R5cGU9J2RhdGUnXTpkaXNhYmxlZCB7XG4gIG9wYWNpdHk6IHZhcigtLWpwLXdpZGdldHMtZGlzYWJsZWQtb3BhY2l0eSk7XG59XG5cbi8qIFBsYXkgV2lkZ2V0ICovXG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1wbGF5LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtcGxheSB7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLWlubGluZS13aWR0aC1zaG9ydCk7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGFsaWduLWl0ZW1zOiBzdHJldGNoO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtcGxheSAuanVweXRlci1idXR0b24sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1wbGF5IC5qdXB5dGVyLWJ1dHRvbiB7XG4gIGZsZXgtZ3JvdzogMTtcbiAgaGVpZ2h0OiBhdXRvO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi53aWRnZXQtcGxheSAuanVweXRlci1idXR0b246ZGlzYWJsZWQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldC1wbGF5IC5qdXB5dGVyLWJ1dHRvbjpkaXNhYmxlZCB7XG4gIG9wYWNpdHk6IHZhcigtLWpwLXdpZGdldHMtZGlzYWJsZWQtb3BhY2l0eSk7XG59XG5cbi8qIFRhYiBXaWRnZXQgKi9cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiIHtcbiAgZGlzcGxheTogZmxleDtcbiAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWIgPiAucC1UYWJCYXIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIge1xuICAvKiBOZWNlc3Nhcnkgc28gdGhhdCBhIHRhYiBjYW4gYmUgc2hpZnRlZCBkb3duIHRvIG92ZXJsYXkgdGhlIGJvcmRlciBvZiB0aGUgYm94IGJlbG93LiAqL1xuICBvdmVyZmxvdy14OiB2aXNpYmxlO1xuICBvdmVyZmxvdy15OiB2aXNpYmxlO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYiA+IC5wLVRhYkJhciA+IC5wLVRhYkJhci1jb250ZW50LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5wLVRhYkJhciA+IC5wLVRhYkJhci1jb250ZW50LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIgPiAubG0tVGFiQmFyLWNvbnRlbnQge1xuICAvKiBNYWtlIHN1cmUgdGhhdCB0aGUgdGFiIGdyb3dzIGZyb20gYm90dG9tIHVwICovXG4gIGFsaWduLWl0ZW1zOiBmbGV4LWVuZDtcbiAgbWluLXdpZHRoOiAwO1xuICBtaW4taGVpZ2h0OiAwO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYiA+IC53aWRnZXQtdGFiLWNvbnRlbnRzLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC53aWRnZXQtdGFiLWNvbnRlbnRzIHtcbiAgd2lkdGg6IDEwMCU7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG4gIG1hcmdpbjogMDtcbiAgYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMSk7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMSk7XG4gIGJvcmRlcjogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSBzb2xpZCB2YXIoLS1qcC1ib3JkZXItY29sb3IxKTtcbiAgcGFkZGluZzogdmFyKC0tanAtd2lkZ2V0cy1jb250YWluZXItcGFkZGluZyk7XG4gIGZsZXgtZ3JvdzogMTtcbiAgb3ZlcmZsb3c6IGF1dG87XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5wLVRhYkJhciwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAubG0tVGFiQmFyIHtcbiAgZm9udDogdmFyKC0tanAtd2lkZ2V0cy1mb250LXNpemUpIEhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWY7XG4gIG1pbi1oZWlnaHQ6IGNhbGMoXG4gICAgdmFyKC0tanAtd2lkZ2V0cy1ob3Jpem9udGFsLXRhYi1oZWlnaHQpICsgdmFyKC0tanAtYm9yZGVyLXdpZHRoKVxuICApO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYiA+IC5wLVRhYkJhciAucC1UYWJCYXItdGFiLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5wLVRhYkJhciAucC1UYWJCYXItdGFiLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIgLmxtLVRhYkJhci10YWIge1xuICBmbGV4OiAwIDEgdmFyKC0tanAtd2lkZ2V0cy1ob3Jpem9udGFsLXRhYi13aWR0aCk7XG4gIG1pbi13aWR0aDogMzVweDtcbiAgbWluLWhlaWdodDogY2FsYyhcbiAgICB2YXIoLS1qcC13aWRnZXRzLWhvcml6b250YWwtdGFiLWhlaWdodCkgKyB2YXIoLS1qcC1ib3JkZXItd2lkdGgpXG4gICk7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWhvcml6b250YWwtdGFiLWhlaWdodCk7XG4gIG1hcmdpbi1sZWZ0OiBjYWxjKC0xICogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSk7XG4gIHBhZGRpbmc6IDBweCAxMHB4O1xuICBiYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IyKTtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWZvbnQtY29sb3IyKTtcbiAgYm9yZGVyOiB2YXIoLS1qcC1ib3JkZXItd2lkdGgpIHNvbGlkIHZhcigtLWpwLWJvcmRlci1jb2xvcjEpO1xuICBib3JkZXItYm90dG9tOiBub25lO1xuICBwb3NpdGlvbjogcmVsYXRpdmU7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWIucC1tb2QtY3VycmVudCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAucC1UYWJCYXIgLnAtVGFiQmFyLXRhYi5wLW1vZC1jdXJyZW50LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIgLmxtLVRhYkJhci10YWIubG0tbW9kLWN1cnJlbnQge1xuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjApO1xuICAvKiBXZSB3YW50IHRoZSBiYWNrZ3JvdW5kIHRvIG1hdGNoIHRoZSB0YWIgY29udGVudCBiYWNrZ3JvdW5kICovXG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICBtaW4taGVpZ2h0OiBjYWxjKFxuICAgIHZhcigtLWpwLXdpZGdldHMtaG9yaXpvbnRhbC10YWItaGVpZ2h0KSArIDIgKiB2YXIoLS1qcC1ib3JkZXItd2lkdGgpXG4gICk7XG4gIHRyYW5zZm9ybTogdHJhbnNsYXRlWSh2YXIoLS1qcC1ib3JkZXItd2lkdGgpKTtcbiAgb3ZlcmZsb3c6IHZpc2libGU7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWIucC1tb2QtY3VycmVudDpiZWZvcmUsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWIucC1tb2QtY3VycmVudDpiZWZvcmUsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciAubG0tVGFiQmFyLXRhYi5sbS1tb2QtY3VycmVudDpiZWZvcmUge1xuICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gIHRvcDogY2FsYygtMSAqIHZhcigtLWpwLWJvcmRlci13aWR0aCkpO1xuICBsZWZ0OiBjYWxjKC0xICogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSk7XG4gIGNvbnRlbnQ6ICcnO1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtaG9yaXpvbnRhbC10YWItdG9wLWJvcmRlcik7XG4gIHdpZHRoOiBjYWxjKDEwMCUgKyAyICogdmFyKC0tanAtYm9yZGVyLXdpZHRoKSk7XG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLWJyYW5kLWNvbG9yMSk7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWI6Zmlyc3QtY2hpbGQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWI6Zmlyc3QtY2hpbGQsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciAubG0tVGFiQmFyLXRhYjpmaXJzdC1jaGlsZCB7XG4gIG1hcmdpbi1sZWZ0OiAwO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYlxuICA+IC5wLVRhYkJhclxuICAucC1UYWJCYXItdGFiOmhvdmVyOm5vdCgucC1tb2QtY3VycmVudCksXG4vKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiXG4gID4gLnAtVGFiQmFyXG4gIC5wLVRhYkJhci10YWI6aG92ZXI6bm90KC5wLW1vZC1jdXJyZW50KSxcbi8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiXG4gID4gLmxtLVRhYkJhclxuICAubG0tVGFiQmFyLXRhYjpob3Zlcjpub3QoLmxtLW1vZC1jdXJyZW50KSB7XG4gIGJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjEpO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYlxuICA+IC5wLVRhYkJhclxuICAucC1tb2QtY2xvc2FibGVcbiAgPiAucC1UYWJCYXItdGFiQ2xvc2VJY29uLFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuPiAucC1UYWJCYXJcbi5wLW1vZC1jbG9zYWJsZVxuPiAucC1UYWJCYXItdGFiQ2xvc2VJY29uLFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWJcbiAgPiAubG0tVGFiQmFyXG4gIC5sbS1tb2QtY2xvc2FibGVcbiAgPiAubG0tVGFiQmFyLXRhYkNsb3NlSWNvbiB7XG4gIG1hcmdpbi1sZWZ0OiA0cHg7XG59XG5cbi8qIFRoaXMgZm9udC1hd2Vzb21lIHN0cmF0ZWd5IG1heSBub3Qgd29yayBhY3Jvc3MgRkE0IGFuZCBGQTUsIGJ1dCB3ZSBkb24ndFxuYWN0dWFsbHkgc3VwcG9ydCBjbG9zYWJsZSB0YWJzLCBzbyBpdCByZWFsbHkgZG9lc24ndCBtYXR0ZXIgKi9cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiXG4gID4gLnAtVGFiQmFyXG4gIC5wLW1vZC1jbG9zYWJsZVxuICA+IC5wLVRhYkJhci10YWJDbG9zZUljb246YmVmb3JlLFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXdpZGdldC10YWJcbj4gLnAtVGFiQmFyXG4ucC1tb2QtY2xvc2FibGVcbj4gLnAtVGFiQmFyLXRhYkNsb3NlSWNvbjpiZWZvcmUsXG4vKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuICA+IC5sbS1UYWJCYXJcbiAgLmxtLW1vZC1jbG9zYWJsZVxuICA+IC5sbS1UYWJCYXItdGFiQ2xvc2VJY29uOmJlZm9yZSB7XG4gIGZvbnQtZmFtaWx5OiBGb250QXdlc29tZTtcbiAgY29udGVudDogJ1xcXFxmMDBkJzsgLyogY2xvc2UgKi9cbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWIgPiAucC1UYWJCYXIgLnAtVGFiQmFyLXRhYkljb24sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAuanVweXRlci13aWRnZXRzLndpZGdldC10YWIgPiAucC1UYWJCYXIgLnAtVGFiQmFyLXRhYkxhYmVsLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJDbG9zZUljb24sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLyAuanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5wLVRhYkJhciAucC1UYWJCYXItdGFiSWNvbiwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJMYWJlbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovIC5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJDbG9zZUljb24sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciAubG0tVGFiQmFyLXRhYkljb24sXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIgLmxtLVRhYkJhci10YWJMYWJlbCxcbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciAubG0tVGFiQmFyLXRhYkNsb3NlSWNvbiB7XG4gIGxpbmUtaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLWhvcml6b250YWwtdGFiLWhlaWdodCk7XG59XG5cbi8qIEFjY29yZGlvbiBXaWRnZXQgKi9cblxuLmp1cHl0ZXItd2lkZ2V0LUNvbGxhcHNlIHtcbiAgZGlzcGxheTogZmxleDtcbiAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgYWxpZ24taXRlbXM6IHN0cmV0Y2g7XG59XG5cbi5qdXB5dGVyLXdpZGdldC1Db2xsYXBzZS1oZWFkZXIge1xuICBwYWRkaW5nOiB2YXIoLS1qcC13aWRnZXRzLWlucHV0LXBhZGRpbmcpO1xuICBjdXJzb3I6IHBvaW50ZXI7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMik7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjIpO1xuICBib3JkZXI6IHZhcigtLWpwLXdpZGdldHMtYm9yZGVyLXdpZHRoKSBzb2xpZCB2YXIoLS1qcC1ib3JkZXItY29sb3IxKTtcbiAgcGFkZGluZzogY2FsYyh2YXIoLS1qcC13aWRnZXRzLWNvbnRhaW5lci1wYWRkaW5nKSAqIDIgLyAzKVxuICAgIHZhcigtLWpwLXdpZGdldHMtY29udGFpbmVyLXBhZGRpbmcpO1xuICBmb250LXdlaWdodDogYm9sZDtcbn1cblxuLmp1cHl0ZXItd2lkZ2V0LUNvbGxhcHNlLWhlYWRlcjpob3ZlciB7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICBjb2xvcjogdmFyKC0tanAtdWktZm9udC1jb2xvcjEpO1xufVxuXG4uanVweXRlci13aWRnZXQtQ29sbGFwc2Utb3BlbiA+IC5qdXB5dGVyLXdpZGdldC1Db2xsYXBzZS1oZWFkZXIge1xuICBiYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IxKTtcbiAgY29sb3I6IHZhcigtLWpwLXVpLWZvbnQtY29sb3IwKTtcbiAgY3Vyc29yOiBkZWZhdWx0O1xuICBib3JkZXItYm90dG9tOiBub25lO1xufVxuXG4uanVweXRlci13aWRnZXQtQ29sbGFwc2UtY29udGVudHMge1xuICBwYWRkaW5nOiB2YXIoLS1qcC13aWRnZXRzLWNvbnRhaW5lci1wYWRkaW5nKTtcbiAgYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tanAtbGF5b3V0LWNvbG9yMSk7XG4gIGNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMSk7XG4gIGJvcmRlci1sZWZ0OiB2YXIoLS1qcC13aWRnZXRzLWJvcmRlci13aWR0aCkgc29saWQgdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG4gIGJvcmRlci1yaWdodDogdmFyKC0tanAtd2lkZ2V0cy1ib3JkZXItd2lkdGgpIHNvbGlkIHZhcigtLWpwLWJvcmRlci1jb2xvcjEpO1xuICBib3JkZXItYm90dG9tOiB2YXIoLS1qcC13aWRnZXRzLWJvcmRlci13aWR0aCkgc29saWQgdmFyKC0tanAtYm9yZGVyLWNvbG9yMSk7XG4gIG92ZXJmbG93OiBhdXRvO1xufVxuXG4uanVweXRlci13aWRnZXQtQWNjb3JkaW9uIHtcbiAgZGlzcGxheTogZmxleDtcbiAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcbiAgYWxpZ24taXRlbXM6IHN0cmV0Y2g7XG59XG5cbi5qdXB5dGVyLXdpZGdldC1BY2NvcmRpb24gLmp1cHl0ZXItd2lkZ2V0LUNvbGxhcHNlIHtcbiAgbWFyZ2luLWJvdHRvbTogMDtcbn1cblxuLmp1cHl0ZXItd2lkZ2V0LUFjY29yZGlvbiAuanVweXRlci13aWRnZXQtQ29sbGFwc2UgKyAuanVweXRlci13aWRnZXQtQ29sbGFwc2Uge1xuICBtYXJnaW4tdG9wOiA0cHg7XG59XG5cbi8qIEhUTUwgd2lkZ2V0ICovXG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLndpZGdldC1odG1sLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLndpZGdldC1odG1sbWF0aCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0LWh0bWwsXG4uanVweXRlci13aWRnZXQtaHRtbG1hdGgge1xuICBmb250LXNpemU6IHZhcigtLWpwLXdpZGdldHMtZm9udC1zaXplKTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWh0bWwgPiAud2lkZ2V0LWh0bWwtY29udGVudCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovLndpZGdldC1odG1sbWF0aCA+IC53aWRnZXQtaHRtbC1jb250ZW50LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtaHRtbCA+IC5qdXB5dGVyLXdpZGdldC1odG1sLWNvbnRlbnQsXG4uanVweXRlci13aWRnZXQtaHRtbG1hdGggPiAuanVweXRlci13aWRnZXQtaHRtbC1jb250ZW50IHtcbiAgLyogRmlsbCBvdXQgdGhlIGFyZWEgaW4gdGhlIEhUTUwgd2lkZ2V0ICovXG4gIGFsaWduLXNlbGY6IHN0cmV0Y2g7XG4gIGZsZXgtZ3JvdzogMTtcbiAgZmxleC1zaHJpbms6IDE7XG4gIC8qIE1ha2VzIHN1cmUgdGhlIGJhc2VsaW5lIGlzIHN0aWxsIGFsaWduZWQgd2l0aCBvdGhlciBlbGVtZW50cyAqL1xuICBsaW5lLWhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1pbmxpbmUtaGVpZ2h0KTtcbiAgLyogTWFrZSBpdCBwb3NzaWJsZSB0byBoYXZlIGFic29sdXRlbHktcG9zaXRpb25lZCBlbGVtZW50cyBpbiB0aGUgaHRtbCAqL1xuICBwb3NpdGlvbjogcmVsYXRpdmU7XG59XG5cbi8qIEltYWdlIHdpZGdldCAgKi9cblxuLyogPERFUFJFQ0FURUQ+ICovXG4ud2lkZ2V0LWltYWdlLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXQtaW1hZ2Uge1xuICBtYXgtd2lkdGg6IDEwMCU7XG4gIGhlaWdodDogYXV0bztcbn1cbmAsIFwiXCJdKTtcbi8vIEV4cG9ydHNcbmV4cG9ydCBkZWZhdWx0IF9fX0NTU19MT0FERVJfRVhQT1JUX19fO1xuIiwiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qXG5cblRoZSBub3Vpc2xpZGVyLmNzcyBmaWxlIGlzIGF1dG9nZW5lcmF0ZWQgZnJvbSBub3Vpc2xpZGVyLmxlc3MsIHdoaWNoIGltcG9ydHMgYW5kIHdyYXBzIHRoZSBub3Vpc2xpZGVyL3NyYy9ub3Vpc2xpZGVyLmxlc3Mgc3R5bGVzLlxuXG5NSVQgTGljZW5zZVxuXG5Db3B5cmlnaHQgKGMpIDIwMTkgTMOpb24gR2Vyc2VuXG5cblBlcm1pc3Npb24gaXMgaGVyZWJ5IGdyYW50ZWQsIGZyZWUgb2YgY2hhcmdlLCB0byBhbnkgcGVyc29uIG9idGFpbmluZyBhIGNvcHkgb2YgdGhpcyBzb2Z0d2FyZSBhbmQgYXNzb2NpYXRlZCBkb2N1bWVudGF0aW9uIGZpbGVzICh0aGUgXCJTb2Z0d2FyZVwiKSwgdG8gZGVhbCBpbiB0aGUgU29mdHdhcmUgd2l0aG91dCByZXN0cmljdGlvbiwgaW5jbHVkaW5nIHdpdGhvdXQgbGltaXRhdGlvbiB0aGUgcmlnaHRzIHRvIHVzZSwgY29weSwgbW9kaWZ5LCBtZXJnZSwgcHVibGlzaCwgZGlzdHJpYnV0ZSwgc3VibGljZW5zZSwgYW5kL29yIHNlbGwgY29waWVzIG9mIHRoZSBTb2Z0d2FyZSwgYW5kIHRvIHBlcm1pdCBwZXJzb25zIHRvIHdob20gdGhlIFNvZnR3YXJlIGlzIGZ1cm5pc2hlZCB0byBkbyBzbywgc3ViamVjdCB0byB0aGUgZm9sbG93aW5nIGNvbmRpdGlvbnM6XG5cblRoZSBhYm92ZSBjb3B5cmlnaHQgbm90aWNlIGFuZCB0aGlzIHBlcm1pc3Npb24gbm90aWNlIHNoYWxsIGJlIGluY2x1ZGVkIGluIGFsbCBjb3BpZXMgb3Igc3Vic3RhbnRpYWwgcG9ydGlvbnMgb2YgdGhlIFNvZnR3YXJlLlxuXG5USEUgU09GVFdBUkUgSVMgUFJPVklERUQgXCJBUyBJU1wiLCBXSVRIT1VUIFdBUlJBTlRZIE9GIEFOWSBLSU5ELCBFWFBSRVNTIE9SIElNUExJRUQsIElOQ0xVRElORyBCVVQgTk9UIExJTUlURUQgVE8gVEhFIFdBUlJBTlRJRVMgT0YgTUVSQ0hBTlRBQklMSVRZLCBGSVRORVNTIEZPUiBBIFBBUlRJQ1VMQVIgUFVSUE9TRSBBTkQgTk9OSU5GUklOR0VNRU5ULiBJTiBOTyBFVkVOVCBTSEFMTCBUSEUgQVVUSE9SUyBPUiBDT1BZUklHSFQgSE9MREVSUyBCRSBMSUFCTEUgRk9SIEFOWSBDTEFJTSwgREFNQUdFUyBPUiBPVEhFUiBMSUFCSUxJVFksIFdIRVRIRVIgSU4gQU4gQUNUSU9OIE9GIENPTlRSQUNULCBUT1JUIE9SIE9USEVSV0lTRSwgQVJJU0lORyBGUk9NLCBPVVQgT0YgT1IgSU4gQ09OTkVDVElPTiBXSVRIIFRIRSBTT0ZUV0FSRSBPUiBUSEUgVVNFIE9SIE9USEVSIERFQUxJTkdTIElOIFRIRSBTT0ZUV0FSRS5cbiovXG4vKiBUaGUgLndpZGdldC1zbGlkZXIgY2xhc3MgaXMgZGVwcmVjYXRlZCAqL1xuLndpZGdldC1zbGlkZXIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIHtcbiAgLyogRnVuY3Rpb25hbCBzdHlsaW5nO1xuICogVGhlc2Ugc3R5bGVzIGFyZSByZXF1aXJlZCBmb3Igbm9VaVNsaWRlciB0byBmdW5jdGlvbi5cbiAqIFlvdSBkb24ndCBuZWVkIHRvIGNoYW5nZSB0aGVzZSBydWxlcyB0byBhcHBseSB5b3VyIGRlc2lnbi5cbiAqL1xuICAvKiBXcmFwcGVyIGZvciBhbGwgY29ubmVjdCBlbGVtZW50cy5cbiAqL1xuICAvKiBPZmZzZXQgZGlyZWN0aW9uXG4gKi9cbiAgLyogR2l2ZSBvcmlnaW5zIDAgaGVpZ2h0L3dpZHRoIHNvIHRoZXkgZG9uJ3QgaW50ZXJmZXJlIHdpdGggY2xpY2tpbmcgdGhlXG4gKiBjb25uZWN0IGVsZW1lbnRzLlxuICovXG4gIC8qIFNsaWRlciBzaXplIGFuZCBoYW5kbGUgcGxhY2VtZW50O1xuICovXG4gIC8qIFN0eWxpbmc7XG4gKiBHaXZpbmcgdGhlIGNvbm5lY3QgZWxlbWVudCBhIGJvcmRlciByYWRpdXMgY2F1c2VzIGlzc3VlcyB3aXRoIHVzaW5nIHRyYW5zZm9ybTogc2NhbGVcbiAqL1xuICAvKiBIYW5kbGVzIGFuZCBjdXJzb3JzO1xuICovXG4gIC8qIEhhbmRsZSBzdHJpcGVzO1xuICovXG4gIC8qIERpc2FibGVkIHN0YXRlO1xuICovXG4gIC8qIEJhc2U7XG4gKlxuICovXG4gIC8qIFZhbHVlcztcbiAqXG4gKi9cbiAgLyogTWFya2luZ3M7XG4gKlxuICovXG4gIC8qIEhvcml6b250YWwgbGF5b3V0O1xuICpcbiAqL1xuICAvKiBWZXJ0aWNhbCBsYXlvdXQ7XG4gKlxuICovXG4gIC8qIENvcHlyaWdodCAoYykgSnVweXRlciBEZXZlbG9wbWVudCBUZWFtLlxuICogRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbiAqL1xuICAvKiBDdXN0b20gQ1NTIGZvciBub3Vpc2xpZGVyICovXG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS10YXJnZXQsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldCxcbi53aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldCAqLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS10YXJnZXQgKiB7XG4gIC13ZWJraXQtdG91Y2gtY2FsbG91dDogbm9uZTtcbiAgLXdlYmtpdC10YXAtaGlnaGxpZ2h0LWNvbG9yOiByZ2JhKDAsIDAsIDAsIDApO1xuICAtd2Via2l0LXVzZXItc2VsZWN0OiBub25lO1xuICAtbXMtdG91Y2gtYWN0aW9uOiBub25lO1xuICB0b3VjaC1hY3Rpb246IG5vbmU7XG4gIC1tcy11c2VyLXNlbGVjdDogbm9uZTtcbiAgLW1vei11c2VyLXNlbGVjdDogbm9uZTtcbiAgdXNlci1zZWxlY3Q6IG5vbmU7XG4gIC1tb3otYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdGFyZ2V0IHtcbiAgcG9zaXRpb246IHJlbGF0aXZlO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktYmFzZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktYmFzZSxcbi53aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3RzLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1jb25uZWN0cyB7XG4gIHdpZHRoOiAxMDAlO1xuICBoZWlnaHQ6IDEwMCU7XG4gIHBvc2l0aW9uOiByZWxhdGl2ZTtcbiAgei1pbmRleDogMTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3RzLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1jb25uZWN0cyB7XG4gIG92ZXJmbG93OiBoaWRkZW47XG4gIHotaW5kZXg6IDA7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1jb25uZWN0LFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1jb25uZWN0LFxuLndpZGdldC1zbGlkZXIgLm5vVWktb3JpZ2luLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1vcmlnaW4ge1xuICB3aWxsLWNoYW5nZTogdHJhbnNmb3JtO1xuICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gIHotaW5kZXg6IDE7XG4gIHRvcDogMDtcbiAgcmlnaHQ6IDA7XG4gIC1tcy10cmFuc2Zvcm0tb3JpZ2luOiAwIDA7XG4gIC13ZWJraXQtdHJhbnNmb3JtLW9yaWdpbjogMCAwO1xuICAtd2Via2l0LXRyYW5zZm9ybS1zdHlsZTogcHJlc2VydmUtM2Q7XG4gIHRyYW5zZm9ybS1vcmlnaW46IDAgMDtcbiAgdHJhbnNmb3JtLXN0eWxlOiBmbGF0O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktY29ubmVjdCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktY29ubmVjdCB7XG4gIGhlaWdodDogMTAwJTtcbiAgd2lkdGg6IDEwMCU7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1vcmlnaW4sXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLW9yaWdpbiB7XG4gIGhlaWdodDogMTAlO1xuICB3aWR0aDogMTAlO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdHh0LWRpci1ydGwubm9VaS1ob3Jpem9udGFsIC5ub1VpLW9yaWdpbixcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdHh0LWRpci1ydGwubm9VaS1ob3Jpem9udGFsIC5ub1VpLW9yaWdpbiB7XG4gIGxlZnQ6IDA7XG4gIHJpZ2h0OiBhdXRvO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdmVydGljYWwgLm5vVWktb3JpZ2luLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS1vcmlnaW4ge1xuICB3aWR0aDogMDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWhvcml6b250YWwgLm5vVWktb3JpZ2luLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1ob3Jpem9udGFsIC5ub1VpLW9yaWdpbiB7XG4gIGhlaWdodDogMDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWhhbmRsZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlIHtcbiAgLXdlYmtpdC1iYWNrZmFjZS12aXNpYmlsaXR5OiBoaWRkZW47XG4gIGJhY2tmYWNlLXZpc2liaWxpdHk6IGhpZGRlbjtcbiAgcG9zaXRpb246IGFic29sdXRlO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdG91Y2gtYXJlYSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdG91Y2gtYXJlYSB7XG4gIGhlaWdodDogMTAwJTtcbiAgd2lkdGg6IDEwMCU7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1zdGF0ZS10YXAgLm5vVWktY29ubmVjdCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktc3RhdGUtdGFwIC5ub1VpLWNvbm5lY3QsXG4ud2lkZ2V0LXNsaWRlciAubm9VaS1zdGF0ZS10YXAgLm5vVWktb3JpZ2luLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1zdGF0ZS10YXAgLm5vVWktb3JpZ2luIHtcbiAgLXdlYmtpdC10cmFuc2l0aW9uOiB0cmFuc2Zvcm0gMC4zcztcbiAgdHJhbnNpdGlvbjogdHJhbnNmb3JtIDAuM3M7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1zdGF0ZS1kcmFnICosXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXN0YXRlLWRyYWcgKiB7XG4gIGN1cnNvcjogaW5oZXJpdCAhaW1wb3J0YW50O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCB7XG4gIGhlaWdodDogMThweDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWhvcml6b250YWwgLm5vVWktaGFuZGxlLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1ob3Jpem9udGFsIC5ub1VpLWhhbmRsZSB7XG4gIHdpZHRoOiAzNHB4O1xuICBoZWlnaHQ6IDI4cHg7XG4gIHJpZ2h0OiAtMTdweDtcbiAgdG9wOiAtNnB4O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdmVydGljYWwsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIHtcbiAgd2lkdGg6IDE4cHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS1oYW5kbGUsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWhhbmRsZSB7XG4gIHdpZHRoOiAyOHB4O1xuICBoZWlnaHQ6IDM0cHg7XG4gIHJpZ2h0OiAtNnB4O1xuICB0b3A6IC0xN3B4O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdHh0LWRpci1ydGwubm9VaS1ob3Jpem9udGFsIC5ub1VpLWhhbmRsZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdHh0LWRpci1ydGwubm9VaS1ob3Jpem9udGFsIC5ub1VpLWhhbmRsZSB7XG4gIGxlZnQ6IC0xN3B4O1xuICByaWdodDogYXV0bztcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdGFyZ2V0IHtcbiAgYmFja2dyb3VuZDogI0ZBRkFGQTtcbiAgYm9yZGVyLXJhZGl1czogNHB4O1xuICBib3JkZXI6IDFweCBzb2xpZCAjRDNEM0QzO1xuICBib3gtc2hhZG93OiBpbnNldCAwIDFweCAxcHggI0YwRjBGMCwgMCAzcHggNnB4IC01cHggI0JCQjtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3RzLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1jb25uZWN0cyB7XG4gIGJvcmRlci1yYWRpdXM6IDNweDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3QsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3Qge1xuICBiYWNrZ3JvdW5kOiAjM0ZCOEFGO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktZHJhZ2dhYmxlLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1kcmFnZ2FibGUge1xuICBjdXJzb3I6IGV3LXJlc2l6ZTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWRyYWdnYWJsZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdmVydGljYWwgLm5vVWktZHJhZ2dhYmxlIHtcbiAgY3Vyc29yOiBucy1yZXNpemU7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1oYW5kbGUsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLWhhbmRsZSB7XG4gIGJvcmRlcjogMXB4IHNvbGlkICNEOUQ5RDk7XG4gIGJvcmRlci1yYWRpdXM6IDNweDtcbiAgYmFja2dyb3VuZDogI0ZGRjtcbiAgY3Vyc29yOiBkZWZhdWx0O1xuICBib3gtc2hhZG93OiBpbnNldCAwIDAgMXB4ICNGRkYsIGluc2V0IDAgMXB4IDdweCAjRUJFQkVCLCAwIDNweCA2cHggLTNweCAjQkJCO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktYWN0aXZlLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1hY3RpdmUge1xuICBib3gtc2hhZG93OiBpbnNldCAwIDAgMXB4ICNGRkYsIGluc2V0IDAgMXB4IDdweCAjRERELCAwIDNweCA2cHggLTNweCAjQkJCO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmJlZm9yZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmJlZm9yZSxcbi53aWRnZXQtc2xpZGVyIC5ub1VpLWhhbmRsZTphZnRlcixcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmFmdGVyIHtcbiAgY29udGVudDogXCJcIjtcbiAgZGlzcGxheTogYmxvY2s7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgaGVpZ2h0OiAxNHB4O1xuICB3aWR0aDogMXB4O1xuICBiYWNrZ3JvdW5kOiAjRThFN0U2O1xuICBsZWZ0OiAxNHB4O1xuICB0b3A6IDZweDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWhhbmRsZTphZnRlcixcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmFmdGVyIHtcbiAgbGVmdDogMTdweDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWhhbmRsZTpiZWZvcmUsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWhhbmRsZTpiZWZvcmUsXG4ud2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS1oYW5kbGU6YWZ0ZXIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWhhbmRsZTphZnRlciB7XG4gIHdpZHRoOiAxNHB4O1xuICBoZWlnaHQ6IDFweDtcbiAgbGVmdDogNnB4O1xuICB0b3A6IDE0cHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS1oYW5kbGU6YWZ0ZXIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWhhbmRsZTphZnRlciB7XG4gIHRvcDogMTdweDtcbn1cbi53aWRnZXQtc2xpZGVyIFtkaXNhYmxlZF0gLm5vVWktY29ubmVjdCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgW2Rpc2FibGVkXSAubm9VaS1jb25uZWN0IHtcbiAgYmFja2dyb3VuZDogI0I4QjhCODtcbn1cbi53aWRnZXQtc2xpZGVyIFtkaXNhYmxlZF0ubm9VaS10YXJnZXQsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIFtkaXNhYmxlZF0ubm9VaS10YXJnZXQsXG4ud2lkZ2V0LXNsaWRlciBbZGlzYWJsZWRdLm5vVWktaGFuZGxlLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciBbZGlzYWJsZWRdLm5vVWktaGFuZGxlLFxuLndpZGdldC1zbGlkZXIgW2Rpc2FibGVkXSAubm9VaS1oYW5kbGUsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIFtkaXNhYmxlZF0gLm5vVWktaGFuZGxlIHtcbiAgY3Vyc29yOiBub3QtYWxsb3dlZDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXBpcHMsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXBpcHMsXG4ud2lkZ2V0LXNsaWRlciAubm9VaS1waXBzICosXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXBpcHMgKiB7XG4gIC1tb3otYm94LXNpemluZzogYm9yZGVyLWJveDtcbiAgYm94LXNpemluZzogYm9yZGVyLWJveDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXBpcHMsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXBpcHMge1xuICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gIGNvbG9yOiAjOTk5O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdmFsdWUsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZhbHVlIHtcbiAgcG9zaXRpb246IGFic29sdXRlO1xuICB3aGl0ZS1zcGFjZTogbm93cmFwO1xuICB0ZXh0LWFsaWduOiBjZW50ZXI7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS12YWx1ZS1zdWIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZhbHVlLXN1YiB7XG4gIGNvbG9yOiAjY2NjO1xuICBmb250LXNpemU6IDEwcHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLW1hcmtlciB7XG4gIHBvc2l0aW9uOiBhYnNvbHV0ZTtcbiAgYmFja2dyb3VuZDogI0NDQztcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLW1hcmtlci1zdWIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLW1hcmtlci1zdWIge1xuICBiYWNrZ3JvdW5kOiAjQUFBO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktbWFya2VyLWxhcmdlLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXItbGFyZ2Uge1xuICBiYWNrZ3JvdW5kOiAjQUFBO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktcGlwcy1ob3Jpem9udGFsLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1waXBzLWhvcml6b250YWwge1xuICBwYWRkaW5nOiAxMHB4IDA7XG4gIGhlaWdodDogODBweDtcbiAgdG9wOiAxMDAlO1xuICBsZWZ0OiAwO1xuICB3aWR0aDogMTAwJTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZhbHVlLWhvcml6b250YWwsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZhbHVlLWhvcml6b250YWwge1xuICAtd2Via2l0LXRyYW5zZm9ybTogdHJhbnNsYXRlKC01MCUsIDUwJSk7XG4gIHRyYW5zZm9ybTogdHJhbnNsYXRlKC01MCUsIDUwJSk7XG59XG4ubm9VaS1ydGwgLndpZGdldC1zbGlkZXIgLm5vVWktdmFsdWUtaG9yaXpvbnRhbCxcbi5ub1VpLXJ0bCAuanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZhbHVlLWhvcml6b250YWwge1xuICAtd2Via2l0LXRyYW5zZm9ybTogdHJhbnNsYXRlKDUwJSwgNTAlKTtcbiAgdHJhbnNmb3JtOiB0cmFuc2xhdGUoNTAlLCA1MCUpO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktbWFya2VyLWhvcml6b250YWwubm9VaS1tYXJrZXIsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLW1hcmtlci1ob3Jpem9udGFsLm5vVWktbWFya2VyIHtcbiAgbWFyZ2luLWxlZnQ6IC0xcHg7XG4gIHdpZHRoOiAycHg7XG4gIGhlaWdodDogNXB4O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktbWFya2VyLWhvcml6b250YWwubm9VaS1tYXJrZXItc3ViLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXItaG9yaXpvbnRhbC5ub1VpLW1hcmtlci1zdWIge1xuICBoZWlnaHQ6IDEwcHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXItaG9yaXpvbnRhbC5ub1VpLW1hcmtlci1sYXJnZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktbWFya2VyLWhvcml6b250YWwubm9VaS1tYXJrZXItbGFyZ2Uge1xuICBoZWlnaHQ6IDE1cHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1waXBzLXZlcnRpY2FsLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1waXBzLXZlcnRpY2FsIHtcbiAgcGFkZGluZzogMCAxMHB4O1xuICBoZWlnaHQ6IDEwMCU7XG4gIHRvcDogMDtcbiAgbGVmdDogMTAwJTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZhbHVlLXZlcnRpY2FsLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS12YWx1ZS12ZXJ0aWNhbCB7XG4gIC13ZWJraXQtdHJhbnNmb3JtOiB0cmFuc2xhdGUoMCwgLTUwJSk7XG4gIHRyYW5zZm9ybTogdHJhbnNsYXRlKDAsIC01MCUpO1xuICBwYWRkaW5nLWxlZnQ6IDI1cHg7XG59XG4ubm9VaS1ydGwgLndpZGdldC1zbGlkZXIgLm5vVWktdmFsdWUtdmVydGljYWwsXG4ubm9VaS1ydGwgLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS12YWx1ZS12ZXJ0aWNhbCB7XG4gIC13ZWJraXQtdHJhbnNmb3JtOiB0cmFuc2xhdGUoMCwgNTAlKTtcbiAgdHJhbnNmb3JtOiB0cmFuc2xhdGUoMCwgNTAlKTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLW1hcmtlci12ZXJ0aWNhbC5ub1VpLW1hcmtlcixcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktbWFya2VyLXZlcnRpY2FsLm5vVWktbWFya2VyIHtcbiAgd2lkdGg6IDVweDtcbiAgaGVpZ2h0OiAycHg7XG4gIG1hcmdpbi10b3A6IC0xcHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXItdmVydGljYWwubm9VaS1tYXJrZXItc3ViLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXItdmVydGljYWwubm9VaS1tYXJrZXItc3ViIHtcbiAgd2lkdGg6IDEwcHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1tYXJrZXItdmVydGljYWwubm9VaS1tYXJrZXItbGFyZ2UsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLW1hcmtlci12ZXJ0aWNhbC5ub1VpLW1hcmtlci1sYXJnZSB7XG4gIHdpZHRoOiAxNXB4O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktdG9vbHRpcCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdG9vbHRpcCB7XG4gIGRpc3BsYXk6IGJsb2NrO1xuICBwb3NpdGlvbjogYWJzb2x1dGU7XG4gIGJvcmRlcjogMXB4IHNvbGlkICNEOUQ5RDk7XG4gIGJvcmRlci1yYWRpdXM6IDNweDtcbiAgYmFja2dyb3VuZDogI2ZmZjtcbiAgY29sb3I6ICMwMDA7XG4gIHBhZGRpbmc6IDVweDtcbiAgdGV4dC1hbGlnbjogY2VudGVyO1xuICB3aGl0ZS1zcGFjZTogbm93cmFwO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCAubm9VaS10b29sdGlwLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1ob3Jpem9udGFsIC5ub1VpLXRvb2x0aXAge1xuICAtd2Via2l0LXRyYW5zZm9ybTogdHJhbnNsYXRlKC01MCUsIDApO1xuICB0cmFuc2Zvcm06IHRyYW5zbGF0ZSgtNTAlLCAwKTtcbiAgbGVmdDogNTAlO1xuICBib3R0b206IDEyMCU7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS10b29sdGlwLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS10b29sdGlwIHtcbiAgLXdlYmtpdC10cmFuc2Zvcm06IHRyYW5zbGF0ZSgwLCAtNTAlKTtcbiAgdHJhbnNmb3JtOiB0cmFuc2xhdGUoMCwgLTUwJSk7XG4gIHRvcDogNTAlO1xuICByaWdodDogMTIwJTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWhvcml6b250YWwgLm5vVWktb3JpZ2luID4gLm5vVWktdG9vbHRpcCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCAubm9VaS1vcmlnaW4gPiAubm9VaS10b29sdGlwIHtcbiAgLXdlYmtpdC10cmFuc2Zvcm06IHRyYW5zbGF0ZSg1MCUsIDApO1xuICB0cmFuc2Zvcm06IHRyYW5zbGF0ZSg1MCUsIDApO1xuICBsZWZ0OiBhdXRvO1xuICBib3R0b206IDEwcHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS1vcmlnaW4gPiAubm9VaS10b29sdGlwLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCAubm9VaS1vcmlnaW4gPiAubm9VaS10b29sdGlwIHtcbiAgLXdlYmtpdC10cmFuc2Zvcm06IHRyYW5zbGF0ZSgwLCAtMThweCk7XG4gIHRyYW5zZm9ybTogdHJhbnNsYXRlKDAsIC0xOHB4KTtcbiAgdG9wOiBhdXRvO1xuICByaWdodDogMjhweDtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3QsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3Qge1xuICBiYWNrZ3JvdW5kOiAjMjE5NmYzO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCB7XG4gIGhlaWdodDogdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItdHJhY2stdGhpY2tuZXNzKTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS12ZXJ0aWNhbCB7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci10cmFjay10aGlja25lc3MpO1xuICBoZWlnaHQ6IDEwMCU7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1ob3Jpem9udGFsIC5ub1VpLWhhbmRsZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaG9yaXpvbnRhbCAubm9VaS1oYW5kbGUge1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLXNpemUpO1xuICBoZWlnaHQ6IHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLWhhbmRsZS1zaXplKTtcbiAgYm9yZGVyLXJhZGl1czogNTAlO1xuICB0b3A6IGNhbGMoKHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLXRyYWNrLXRoaWNrbmVzcykgLSB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1oYW5kbGUtc2l6ZSkpIC8gMik7XG4gIHJpZ2h0OiBjYWxjKHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLWhhbmRsZS1zaXplKSAvIC0yKTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWhhbmRsZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktdmVydGljYWwgLm5vVWktaGFuZGxlIHtcbiAgaGVpZ2h0OiB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1oYW5kbGUtc2l6ZSk7XG4gIHdpZHRoOiB2YXIoLS1qcC13aWRnZXRzLXNsaWRlci1oYW5kbGUtc2l6ZSk7XG4gIGJvcmRlci1yYWRpdXM6IDUwJTtcbiAgcmlnaHQ6IGNhbGMoKHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLWhhbmRsZS1zaXplKSAtIHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLXRyYWNrLXRoaWNrbmVzcykpIC8gLTIpO1xuICB0b3A6IGNhbGModmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLXNpemUpIC8gLTIpO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmFmdGVyLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1oYW5kbGU6YWZ0ZXIge1xuICBjb250ZW50OiBub25lO1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmJlZm9yZSxcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlOmJlZm9yZSB7XG4gIGNvbnRlbnQ6IG5vbmU7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS10YXJnZXQsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldCB7XG4gIGJhY2tncm91bmQ6ICNmYWZhZmE7XG4gIGJvcmRlci1yYWRpdXM6IDRweDtcbiAgYm9yZGVyOiAxcHg7XG4gIC8qIGJveC1zaGFkb3c6IGluc2V0IDAgMXB4IDFweCAjRjBGMEYwLCAwIDNweCA2cHggLTVweCAjQkJCOyAqL1xufVxuLndpZGdldC1zbGlkZXIgLnVpLXNsaWRlcixcbi5qdXB5dGVyLXdpZGdldC1zbGlkZXIgLnVpLXNsaWRlciB7XG4gIGJvcmRlcjogdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItYm9yZGVyLXdpZHRoKSBzb2xpZCB2YXIoLS1qcC1sYXlvdXQtY29sb3IzKTtcbiAgYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMyk7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG4gIHBvc2l0aW9uOiByZWxhdGl2ZTtcbiAgYm9yZGVyLXJhZGl1czogMHB4O1xufVxuLndpZGdldC1zbGlkZXIgLm5vVWktaGFuZGxlLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1oYW5kbGUge1xuICB3aWR0aDogdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItaGFuZGxlLXNpemUpO1xuICBib3JkZXI6IDFweCBzb2xpZCAjZDlkOWQ5O1xuICBib3JkZXItcmFkaXVzOiAzcHg7XG4gIGJhY2tncm91bmQ6ICNmZmY7XG4gIGN1cnNvcjogZGVmYXVsdDtcbiAgYm94LXNoYWRvdzogbm9uZTtcbiAgb3V0bGluZTogbm9uZTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldDpub3QoW2Rpc2FibGVkXSkgLm5vVWktaGFuZGxlOmhvdmVyLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS10YXJnZXQ6bm90KFtkaXNhYmxlZF0pIC5ub1VpLWhhbmRsZTpob3Zlcixcbi53aWRnZXQtc2xpZGVyIC5ub1VpLXRhcmdldDpub3QoW2Rpc2FibGVkXSkgLm5vVWktaGFuZGxlOmZvY3VzLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS10YXJnZXQ6bm90KFtkaXNhYmxlZF0pIC5ub1VpLWhhbmRsZTpmb2N1cyB7XG4gIGJhY2tncm91bmQtY29sb3I6IHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLWFjdGl2ZS1oYW5kbGUtY29sb3IpO1xuICBib3JkZXI6IHZhcigtLWpwLXdpZGdldHMtc2xpZGVyLWJvcmRlci13aWR0aCkgc29saWQgdmFyKC0tanAtd2lkZ2V0cy1zbGlkZXItYWN0aXZlLWhhbmRsZS1jb2xvcik7XG59XG4ud2lkZ2V0LXNsaWRlciBbZGlzYWJsZWRdLm5vVWktdGFyZ2V0LFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciBbZGlzYWJsZWRdLm5vVWktdGFyZ2V0IHtcbiAgb3BhY2l0eTogMC4zNTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLWNvbm5lY3RzLFxuLmp1cHl0ZXItd2lkZ2V0LXNsaWRlciAubm9VaS1jb25uZWN0cyB7XG4gIG92ZXJmbG93OiB2aXNpYmxlO1xuICB6LWluZGV4OiAwO1xuICBiYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IzKTtcbn1cbi53aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWNvbm5lY3QsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLXZlcnRpY2FsIC5ub1VpLWNvbm5lY3Qge1xuICB3aWR0aDogY2FsYygxMDAlICsgMnB4KTtcbiAgcmlnaHQ6IC0xcHg7XG59XG4ud2lkZ2V0LXNsaWRlciAubm9VaS1ob3Jpem9udGFsIC5ub1VpLWNvbm5lY3QsXG4uanVweXRlci13aWRnZXQtc2xpZGVyIC5ub1VpLWhvcml6b250YWwgLm5vVWktY29ubmVjdCB7XG4gIGhlaWdodDogY2FsYygxMDAlICsgMnB4KTtcbiAgdG9wOiAtMXB4O1xufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCJpbXBvcnQgYXBpIGZyb20gXCIhLi4vLi4vLi4vc3R5bGUtbG9hZGVyL2Rpc3QvcnVudGltZS9pbmplY3RTdHlsZXNJbnRvU3R5bGVUYWcuanNcIjtcbiAgICAgICAgICAgIGltcG9ydCBjb250ZW50IGZyb20gXCIhIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi93aWRnZXRzLWJhc2UuY3NzXCI7XG5cbnZhciBvcHRpb25zID0ge307XG5cbm9wdGlvbnMuaW5zZXJ0ID0gXCJoZWFkXCI7XG5vcHRpb25zLnNpbmdsZXRvbiA9IGZhbHNlO1xuXG52YXIgdXBkYXRlID0gYXBpKGNvbnRlbnQsIG9wdGlvbnMpO1xuXG5cblxuZXhwb3J0IGRlZmF1bHQgY29udGVudC5sb2NhbHMgfHwge307IiwiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qIFRoaXMgZmlsZSBoYXMgY29kZSBkZXJpdmVkIGZyb20gTHVtaW5vIENTUyBmaWxlcywgYXMgbm90ZWQgYmVsb3cuIFRoZSBsaWNlbnNlIGZvciB0aGlzIEx1bWlubyBjb2RlIGlzOlxuXG5Db3B5cmlnaHQgKGMpIDIwMTkgUHJvamVjdCBKdXB5dGVyIENvbnRyaWJ1dG9yc1xuQWxsIHJpZ2h0cyByZXNlcnZlZC5cblxuUmVkaXN0cmlidXRpb24gYW5kIHVzZSBpbiBzb3VyY2UgYW5kIGJpbmFyeSBmb3Jtcywgd2l0aCBvciB3aXRob3V0XG5tb2RpZmljYXRpb24sIGFyZSBwZXJtaXR0ZWQgcHJvdmlkZWQgdGhhdCB0aGUgZm9sbG93aW5nIGNvbmRpdGlvbnMgYXJlIG1ldDpcblxuMS4gUmVkaXN0cmlidXRpb25zIG9mIHNvdXJjZSBjb2RlIG11c3QgcmV0YWluIHRoZSBhYm92ZSBjb3B5cmlnaHQgbm90aWNlLCB0aGlzXG4gICBsaXN0IG9mIGNvbmRpdGlvbnMgYW5kIHRoZSBmb2xsb3dpbmcgZGlzY2xhaW1lci5cblxuMi4gUmVkaXN0cmlidXRpb25zIGluIGJpbmFyeSBmb3JtIG11c3QgcmVwcm9kdWNlIHRoZSBhYm92ZSBjb3B5cmlnaHQgbm90aWNlLFxuICAgdGhpcyBsaXN0IG9mIGNvbmRpdGlvbnMgYW5kIHRoZSBmb2xsb3dpbmcgZGlzY2xhaW1lciBpbiB0aGUgZG9jdW1lbnRhdGlvblxuICAgYW5kL29yIG90aGVyIG1hdGVyaWFscyBwcm92aWRlZCB3aXRoIHRoZSBkaXN0cmlidXRpb24uXG5cbjMuIE5laXRoZXIgdGhlIG5hbWUgb2YgdGhlIGNvcHlyaWdodCBob2xkZXIgbm9yIHRoZSBuYW1lcyBvZiBpdHNcbiAgIGNvbnRyaWJ1dG9ycyBtYXkgYmUgdXNlZCB0byBlbmRvcnNlIG9yIHByb21vdGUgcHJvZHVjdHMgZGVyaXZlZCBmcm9tXG4gICB0aGlzIHNvZnR3YXJlIHdpdGhvdXQgc3BlY2lmaWMgcHJpb3Igd3JpdHRlbiBwZXJtaXNzaW9uLlxuXG5USElTIFNPRlRXQVJFIElTIFBST1ZJREVEIEJZIFRIRSBDT1BZUklHSFQgSE9MREVSUyBBTkQgQ09OVFJJQlVUT1JTIFwiQVMgSVNcIlxuQU5EIEFOWSBFWFBSRVNTIE9SIElNUExJRUQgV0FSUkFOVElFUywgSU5DTFVESU5HLCBCVVQgTk9UIExJTUlURUQgVE8sIFRIRVxuSU1QTElFRCBXQVJSQU5USUVTIE9GIE1FUkNIQU5UQUJJTElUWSBBTkQgRklUTkVTUyBGT1IgQSBQQVJUSUNVTEFSIFBVUlBPU0UgQVJFXG5ESVNDTEFJTUVELiBJTiBOTyBFVkVOVCBTSEFMTCBUSEUgQ09QWVJJR0hUIEhPTERFUiBPUiBDT05UUklCVVRPUlMgQkUgTElBQkxFXG5GT1IgQU5ZIERJUkVDVCwgSU5ESVJFQ1QsIElOQ0lERU5UQUwsIFNQRUNJQUwsIEVYRU1QTEFSWSwgT1IgQ09OU0VRVUVOVElBTFxuREFNQUdFUyAoSU5DTFVESU5HLCBCVVQgTk9UIExJTUlURUQgVE8sIFBST0NVUkVNRU5UIE9GIFNVQlNUSVRVVEUgR09PRFMgT1JcblNFUlZJQ0VTOyBMT1NTIE9GIFVTRSwgREFUQSwgT1IgUFJPRklUUzsgT1IgQlVTSU5FU1MgSU5URVJSVVBUSU9OKSBIT1dFVkVSXG5DQVVTRUQgQU5EIE9OIEFOWSBUSEVPUlkgT0YgTElBQklMSVRZLCBXSEVUSEVSIElOIENPTlRSQUNULCBTVFJJQ1QgTElBQklMSVRZLFxuT1IgVE9SVCAoSU5DTFVESU5HIE5FR0xJR0VOQ0UgT1IgT1RIRVJXSVNFKSBBUklTSU5HIElOIEFOWSBXQVkgT1VUIE9GIFRIRSBVU0Vcbk9GIFRISVMgU09GVFdBUkUsIEVWRU4gSUYgQURWSVNFRCBPRiBUSEUgUE9TU0lCSUxJVFkgT0YgU1VDSCBEQU1BR0UuXG5cblxuQ29weXJpZ2h0IChjKSAyMDE0LTIwMTcsIFBob3NwaG9ySlMgQ29udHJpYnV0b3JzXG5BbGwgcmlnaHRzIHJlc2VydmVkLlxuXG5SZWRpc3RyaWJ1dGlvbiBhbmQgdXNlIGluIHNvdXJjZSBhbmQgYmluYXJ5IGZvcm1zLCB3aXRoIG9yIHdpdGhvdXRcbm1vZGlmaWNhdGlvbiwgYXJlIHBlcm1pdHRlZCBwcm92aWRlZCB0aGF0IHRoZSBmb2xsb3dpbmcgY29uZGl0aW9ucyBhcmUgbWV0OlxuXG4qIFJlZGlzdHJpYnV0aW9ucyBvZiBzb3VyY2UgY29kZSBtdXN0IHJldGFpbiB0aGUgYWJvdmUgY29weXJpZ2h0IG5vdGljZSwgdGhpc1xuICBsaXN0IG9mIGNvbmRpdGlvbnMgYW5kIHRoZSBmb2xsb3dpbmcgZGlzY2xhaW1lci5cblxuKiBSZWRpc3RyaWJ1dGlvbnMgaW4gYmluYXJ5IGZvcm0gbXVzdCByZXByb2R1Y2UgdGhlIGFib3ZlIGNvcHlyaWdodCBub3RpY2UsXG4gIHRoaXMgbGlzdCBvZiBjb25kaXRpb25zIGFuZCB0aGUgZm9sbG93aW5nIGRpc2NsYWltZXIgaW4gdGhlIGRvY3VtZW50YXRpb25cbiAgYW5kL29yIG90aGVyIG1hdGVyaWFscyBwcm92aWRlZCB3aXRoIHRoZSBkaXN0cmlidXRpb24uXG5cbiogTmVpdGhlciB0aGUgbmFtZSBvZiB0aGUgY29weXJpZ2h0IGhvbGRlciBub3IgdGhlIG5hbWVzIG9mIGl0c1xuICBjb250cmlidXRvcnMgbWF5IGJlIHVzZWQgdG8gZW5kb3JzZSBvciBwcm9tb3RlIHByb2R1Y3RzIGRlcml2ZWQgZnJvbVxuICB0aGlzIHNvZnR3YXJlIHdpdGhvdXQgc3BlY2lmaWMgcHJpb3Igd3JpdHRlbiBwZXJtaXNzaW9uLlxuXG5USElTIFNPRlRXQVJFIElTIFBST1ZJREVEIEJZIFRIRSBDT1BZUklHSFQgSE9MREVSUyBBTkQgQ09OVFJJQlVUT1JTIFwiQVMgSVNcIlxuQU5EIEFOWSBFWFBSRVNTIE9SIElNUExJRUQgV0FSUkFOVElFUywgSU5DTFVESU5HLCBCVVQgTk9UIExJTUlURUQgVE8sIFRIRVxuSU1QTElFRCBXQVJSQU5USUVTIE9GIE1FUkNIQU5UQUJJTElUWSBBTkQgRklUTkVTUyBGT1IgQSBQQVJUSUNVTEFSIFBVUlBPU0UgQVJFXG5ESVNDTEFJTUVELiBJTiBOTyBFVkVOVCBTSEFMTCBUSEUgQ09QWVJJR0hUIEhPTERFUiBPUiBDT05UUklCVVRPUlMgQkUgTElBQkxFXG5GT1IgQU5ZIERJUkVDVCwgSU5ESVJFQ1QsIElOQ0lERU5UQUwsIFNQRUNJQUwsIEVYRU1QTEFSWSwgT1IgQ09OU0VRVUVOVElBTFxuREFNQUdFUyAoSU5DTFVESU5HLCBCVVQgTk9UIExJTUlURUQgVE8sIFBST0NVUkVNRU5UIE9GIFNVQlNUSVRVVEUgR09PRFMgT1JcblNFUlZJQ0VTOyBMT1NTIE9GIFVTRSwgREFUQSwgT1IgUFJPRklUUzsgT1IgQlVTSU5FU1MgSU5URVJSVVBUSU9OKSBIT1dFVkVSXG5DQVVTRUQgQU5EIE9OIEFOWSBUSEVPUlkgT0YgTElBQklMSVRZLCBXSEVUSEVSIElOIENPTlRSQUNULCBTVFJJQ1QgTElBQklMSVRZLFxuT1IgVE9SVCAoSU5DTFVESU5HIE5FR0xJR0VOQ0UgT1IgT1RIRVJXSVNFKSBBUklTSU5HIElOIEFOWSBXQVkgT1VUIE9GIFRIRSBVU0Vcbk9GIFRISVMgU09GVFdBUkUsIEVWRU4gSUYgQURWSVNFRCBPRiBUSEUgUE9TU0lCSUxJVFkgT0YgU1VDSCBEQU1BR0UuXG4qL1xuXG4vKlxuICogVGhlIGZvbGxvd2luZyBzZWN0aW9uIGlzIGRlcml2ZWQgZnJvbSBodHRwczovL2dpdGh1Yi5jb20vanVweXRlcmxhYi9sdW1pbm8vYmxvYi8yM2I5ZDA3NWViYzViNzNhYjE0OGI2ZWJmYzIwYWY5N2Y4NTcxNGM0L3BhY2thZ2VzL3dpZGdldHMvc3R5bGUvdGFiYmFyLmNzcyBcbiAqIFdlJ3ZlIHNjb3BlZCB0aGUgcnVsZXMgc28gdGhhdCB0aGV5IGFyZSBjb25zaXN0ZW50IHdpdGggZXhhY3RseSBvdXIgY29kZS5cbiAqL1xuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYiA+IC5wLVRhYkJhciwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAucC1UYWJCYXIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciB7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIC13ZWJraXQtdXNlci1zZWxlY3Q6IG5vbmU7XG4gIC1tb3otdXNlci1zZWxlY3Q6IG5vbmU7XG4gIC1tcy11c2VyLXNlbGVjdDogbm9uZTtcbiAgdXNlci1zZWxlY3Q6IG5vbmU7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyW2RhdGEtb3JpZW50YXRpb249J2hvcml6b250YWwnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAucC1UYWJCYXJbZGF0YS1vcmllbnRhdGlvbj0naG9yaXpvbnRhbCddLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXJbZGF0YS1vcmllbnRhdGlvbj0naG9yaXpvbnRhbCddIHtcbiAgZmxleC1kaXJlY3Rpb246IHJvdztcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWIgPiAucC1UYWJCYXJbZGF0YS1vcmllbnRhdGlvbj0ndmVydGljYWwnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAucC1UYWJCYXJbZGF0YS1vcmllbnRhdGlvbj0ndmVydGljYWwnXSwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAubG0tVGFiQmFyW2RhdGEtb3JpZW50YXRpb249J3ZlcnRpY2FsJ10ge1xuICBmbGV4LWRpcmVjdGlvbjogY29sdW1uO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYiA+IC5wLVRhYkJhciA+IC5wLVRhYkJhci1jb250ZW50LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5wLVRhYkJhciA+IC5wLVRhYkJhci1jb250ZW50LCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIgPiAubG0tVGFiQmFyLWNvbnRlbnQge1xuICBtYXJnaW46IDA7XG4gIHBhZGRpbmc6IDA7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGZsZXg6IDEgMSBhdXRvO1xuICBsaXN0LXN0eWxlLXR5cGU6IG5vbmU7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiXG4gID4gLnAtVGFiQmFyW2RhdGEtb3JpZW50YXRpb249J2hvcml6b250YWwnXVxuICA+IC5wLVRhYkJhci1jb250ZW50LFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuPiAucC1UYWJCYXJbZGF0YS1vcmllbnRhdGlvbj0naG9yaXpvbnRhbCddXG4+IC5wLVRhYkJhci1jb250ZW50LFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWJcbiAgPiAubG0tVGFiQmFyW2RhdGEtb3JpZW50YXRpb249J2hvcml6b250YWwnXVxuICA+IC5sbS1UYWJCYXItY29udGVudCB7XG4gIGZsZXgtZGlyZWN0aW9uOiByb3c7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiXG4gID4gLnAtVGFiQmFyW2RhdGEtb3JpZW50YXRpb249J3ZlcnRpY2FsJ11cbiAgPiAucC1UYWJCYXItY29udGVudCxcbi8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWJcbj4gLnAtVGFiQmFyW2RhdGEtb3JpZW50YXRpb249J3ZlcnRpY2FsJ11cbj4gLnAtVGFiQmFyLWNvbnRlbnQsXG4vKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuICA+IC5sbS1UYWJCYXJbZGF0YS1vcmllbnRhdGlvbj0ndmVydGljYWwnXVxuICA+IC5sbS1UYWJCYXItY29udGVudCB7XG4gIGZsZXgtZGlyZWN0aW9uOiBjb2x1bW47XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWIsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciAubG0tVGFiQmFyLXRhYiB7XG4gIGRpc3BsYXk6IGZsZXg7XG4gIGZsZXgtZGlyZWN0aW9uOiByb3c7XG4gIGJveC1zaXppbmc6IGJvcmRlci1ib3g7XG4gIG92ZXJmbG93OiBoaWRkZW47XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJJY29uLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJDbG9zZUljb24sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJJY29uLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi8gLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAucC1UYWJCYXIgLnAtVGFiQmFyLXRhYkNsb3NlSWNvbiwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAubG0tVGFiQmFyIC5sbS1UYWJCYXItdGFiSWNvbixcbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLmxtLVRhYkJhciAubG0tVGFiQmFyLXRhYkNsb3NlSWNvbiB7XG4gIGZsZXg6IDAgMCBhdXRvO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYiA+IC5wLVRhYkJhciAucC1UYWJCYXItdGFiTGFiZWwsIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWJMYWJlbCwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAubG0tVGFiQmFyIC5sbS1UYWJCYXItdGFiTGFiZWwge1xuICBmbGV4OiAxIDEgYXV0bztcbiAgb3ZlcmZsb3c6IGhpZGRlbjtcbiAgd2hpdGUtc3BhY2U6IG5vd3JhcDtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWIgPiAucC1UYWJCYXIgLnAtVGFiQmFyLXRhYi5wLW1vZC1oaWRkZW4sIC8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqLy5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiID4gLnAtVGFiQmFyIC5wLVRhYkJhci10YWIucC1tb2QtaGlkZGVuLCAvKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYiA+IC5sbS1UYWJCYXIgLmxtLVRhYkJhci10YWIubG0tbW9kLWhpZGRlbiB7XG4gIGRpc3BsYXk6IG5vbmUgIWltcG9ydGFudDtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWIgPiAucC1UYWJCYXIucC1tb2QtZHJhZ2dpbmcgLnAtVGFiQmFyLXRhYiwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAucC1UYWJCYXIucC1tb2QtZHJhZ2dpbmcgLnAtVGFiQmFyLXRhYiwgLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWIgPiAubG0tVGFiQmFyLmxtLW1vZC1kcmFnZ2luZyAubG0tVGFiQmFyLXRhYiB7XG4gIHBvc2l0aW9uOiByZWxhdGl2ZTtcbn1cblxuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLndpZGdldC10YWJcbiAgPiAucC1UYWJCYXIucC1tb2QtZHJhZ2dpbmdbZGF0YS1vcmllbnRhdGlvbj0naG9yaXpvbnRhbCddXG4gIC5wLVRhYkJhci10YWIsXG4vKiA8L0RFUFJFQ0FURUQ+ICovXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMuanVweXRlci13aWRnZXQtdGFiXG4gID4gLnAtVGFiQmFyLnAtbW9kLWRyYWdnaW5nW2RhdGEtb3JpZW50YXRpb249J2hvcml6b250YWwnXVxuICAucC1UYWJCYXItdGFiLFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWJcbiAgPiAubG0tVGFiQmFyLmxtLW1vZC1kcmFnZ2luZ1tkYXRhLW9yaWVudGF0aW9uPSdob3Jpem9udGFsJ11cbiAgLmxtLVRhYkJhci10YWIge1xuICBsZWZ0OiAwO1xuICB0cmFuc2l0aW9uOiBsZWZ0IDE1MG1zIGVhc2U7XG59XG5cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy53aWRnZXQtdGFiXG4gID4gLnAtVGFiQmFyLnAtbW9kLWRyYWdnaW5nW2RhdGEtb3JpZW50YXRpb249J3ZlcnRpY2FsJ11cbiAgLnAtVGFiQmFyLXRhYixcbi8qIDwvREVQUkVDQVRFRD4gKi9cbi8qIDxERVBSRUNBVEVEPiAqL1xuLmp1cHl0ZXItd2lkZ2V0cy5qdXB5dGVyLXdpZGdldC10YWJcbj4gLnAtVGFiQmFyLnAtbW9kLWRyYWdnaW5nW2RhdGEtb3JpZW50YXRpb249J3ZlcnRpY2FsJ11cbi5wLVRhYkJhci10YWIsXG4vKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuICA+IC5sbS1UYWJCYXIubG0tbW9kLWRyYWdnaW5nW2RhdGEtb3JpZW50YXRpb249J3ZlcnRpY2FsJ11cbiAgLmxtLVRhYkJhci10YWIge1xuICB0b3A6IDA7XG4gIHRyYW5zaXRpb246IHRvcCAxNTBtcyBlYXNlO1xufVxuXG4vKiA8REVQUkVDQVRFRD4gKi9cbi5qdXB5dGVyLXdpZGdldHMud2lkZ2V0LXRhYlxuICA+IC5wLVRhYkJhci5wLW1vZC1kcmFnZ2luZ1xuICAucC1UYWJCYXItdGFiLnAtbW9kLWRyYWdnaW5nLFxuLyogPC9ERVBSRUNBVEVEPiAqL1xuLyogPERFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuPiAucC1UYWJCYXIucC1tb2QtZHJhZ2dpbmdcbi5wLVRhYkJhci10YWIucC1tb2QtZHJhZ2dpbmcsXG4vKiA8L0RFUFJFQ0FURUQ+ICovXG4uanVweXRlci13aWRnZXRzLmp1cHl0ZXItd2lkZ2V0LXRhYlxuICA+IC5sbS1UYWJCYXIubG0tbW9kLWRyYWdnaW5nXG4gIC5sbS1UYWJCYXItdGFiLmxtLW1vZC1kcmFnZ2luZyB7XG4gIHRyYW5zaXRpb246IG5vbmU7XG59XG5cbi8qIEVuZCB0YWJiYXIuY3NzICovXG5gLCBcIlwiXSk7XG4vLyBFeHBvcnRzXG5leHBvcnQgZGVmYXVsdCBfX19DU1NfTE9BREVSX0VYUE9SVF9fXztcbiJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=