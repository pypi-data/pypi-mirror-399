"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3546],{

/***/ 14181
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

/*
The following CSS variables define the main, public API for styling JupyterLab.
These variables should be used by all plugins wherever possible. In other
words, plugins should not define custom colors, sizes, etc unless absolutely
necessary. This enables users to change the visual theme of JupyterLab
by changing these variables.

Many variables appear in an ordered sequence (0,1,2,3). These sequences
are designed to work well together, so for example, \`--jp-border-color1\` should
be used with \`--jp-layout-color1\`. The numbers have the following meanings:

* 0: super-primary, reserved for special emphasis
* 1: primary, most important under normal situations
* 2: secondary, next most important under normal situations
* 3: tertiary, next most important under normal situations

Throughout JupyterLab, we are mostly following principles from Google's
Material Design when selecting colors. We are not, however, following
all of MD as it is not optimized for dense, information rich UIs.
*/

:root {
  /* Elevation
   *
   * We style box-shadows using Material Design's idea of elevation. These particular numbers are taken from here:
   *
   * https://github.com/material-components/material-components-web
   * https://material-components-web.appspot.com/elevation.html
   */

  /* The dark theme shadows need a bit of work, but this will probably also require work on the core layout
   * colors used in the theme as well. */
  --jp-shadow-base-lightness: 32;
  --jp-shadow-umbra-color: rgba(
    var(--jp-shadow-base-lightness),
    var(--jp-shadow-base-lightness),
    var(--jp-shadow-base-lightness),
    0.2
  );
  --jp-shadow-penumbra-color: rgba(
    var(--jp-shadow-base-lightness),
    var(--jp-shadow-base-lightness),
    var(--jp-shadow-base-lightness),
    0.14
  );
  --jp-shadow-ambient-color: rgba(
    var(--jp-shadow-base-lightness),
    var(--jp-shadow-base-lightness),
    var(--jp-shadow-base-lightness),
    0.12
  );
  --jp-elevation-z0: none;
  --jp-elevation-z1: 0 2px 1px -1px var(--jp-shadow-umbra-color),
    0 1px 1px 0 var(--jp-shadow-penumbra-color),
    0 1px 3px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z2: 0 3px 1px -2px var(--jp-shadow-umbra-color),
    0 2px 2px 0 var(--jp-shadow-penumbra-color),
    0 1px 5px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z4: 0 2px 4px -1px var(--jp-shadow-umbra-color),
    0 4px 5px 0 var(--jp-shadow-penumbra-color),
    0 1px 10px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z6: 0 3px 5px -1px var(--jp-shadow-umbra-color),
    0 6px 10px 0 var(--jp-shadow-penumbra-color),
    0 1px 18px 0 var(--jp-shadow-ambient-color);
  --jp-elevation-z8: 0 5px 5px -3px var(--jp-shadow-umbra-color),
    0 8px 10px 1px var(--jp-shadow-penumbra-color),
    0 3px 14px 2px var(--jp-shadow-ambient-color);
  --jp-elevation-z12: 0 7px 8px -4px var(--jp-shadow-umbra-color),
    0 12px 17px 2px var(--jp-shadow-penumbra-color),
    0 5px 22px 4px var(--jp-shadow-ambient-color);
  --jp-elevation-z16: 0 8px 10px -5px var(--jp-shadow-umbra-color),
    0 16px 24px 2px var(--jp-shadow-penumbra-color),
    0 6px 30px 5px var(--jp-shadow-ambient-color);
  --jp-elevation-z20: 0 10px 13px -6px var(--jp-shadow-umbra-color),
    0 20px 31px 3px var(--jp-shadow-penumbra-color),
    0 8px 38px 7px var(--jp-shadow-ambient-color);
  --jp-elevation-z24: 0 11px 15px -7px var(--jp-shadow-umbra-color),
    0 24px 38px 3px var(--jp-shadow-penumbra-color),
    0 9px 46px 8px var(--jp-shadow-ambient-color);

  /* shortcut buttons
   *
   * The following css variables are used to specify the visual
   * styling of the keyboard shortcut buttons
   */

  --jp-shortcuts-button-background: var(--jp-brand-color2);
  --jp-shortcuts-button-hover-background: var(--jp-brand-color1);

  /* Borders
   *
   * The following variables, specify the visual styling of borders in JupyterLab.
   */

  --jp-border-width: 1px;
  --jp-border-color0: var(--md-grey-700, #616161);
  --jp-border-color1: var(--md-grey-700, #616161);
  --jp-border-color2: var(--md-grey-800, #424242);
  --jp-border-color3: var(--md-grey-900, #212121);
  --jp-inverse-border-color: var(--md-grey-600, #757575);
  --jp-border-radius: 2px;

  /* UI Fonts
   *
   * The UI font CSS variables are used for the typography all of the JupyterLab
   * user interface elements that are not directly user generated content.
   *
   * The font sizing here is done assuming that the body font size of --jp-ui-font-size1
   * is applied to a parent element. When children elements, such as headings, are sized
   * in em all things will be computed relative to that body size.
   */

  --jp-ui-font-scale-factor: 1.2;
  --jp-ui-font-size0: 0.83333em;
  --jp-ui-font-size1: 13px; /* Base font size */
  --jp-ui-font-size2: 1.2em;
  --jp-ui-font-size3: 1.44em;
  --jp-ui-font-family: system-ui, -apple-system, blinkmacsystemfont, 'Segoe UI',
    helvetica, arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji',
    'Segoe UI Symbol';

  /*
   * Use these font colors against the corresponding main layout colors.
   * In a light theme, these go from dark to light.
   */

  /* Defaults use Material Design specification */
  --jp-ui-font-color0: rgba(255, 255, 255, 1);
  --jp-ui-font-color1: rgba(255, 255, 255, 0.87);
  --jp-ui-font-color2: rgba(255, 255, 255, 0.54);
  --jp-ui-font-color3: rgba(255, 255, 255, 0.38);

  /*
   * Use these against the brand/accent/warn/error colors.
   * These will typically go from light to darker, in both a dark and light theme.
   */

  --jp-ui-inverse-font-color0: rgba(0, 0, 0, 1);
  --jp-ui-inverse-font-color1: rgba(0, 0, 0, 0.8);
  --jp-ui-inverse-font-color2: rgba(0, 0, 0, 0.5);
  --jp-ui-inverse-font-color3: rgba(0, 0, 0, 0.3);

  /* Content Fonts
   *
   * Content font variables are used for typography of user generated content.
   *
   * The font sizing here is done assuming that the body font size of --jp-content-font-size1
   * is applied to a parent element. When children elements, such as headings, are sized
   * in em all things will be computed relative to that body size.
   */

  --jp-content-line-height: 1.6;
  --jp-content-font-scale-factor: 1.2;
  --jp-content-font-size0: 0.83333em;
  --jp-content-font-size1: 14px; /* Base font size */
  --jp-content-font-size2: 1.2em;
  --jp-content-font-size3: 1.44em;
  --jp-content-font-size4: 1.728em;
  --jp-content-font-size5: 2.0736em;

  /* This gives a magnification of about 125% in presentation mode over normal. */
  --jp-content-presentation-font-size1: 17px;
  --jp-content-heading-line-height: 1;
  --jp-content-heading-margin-top: 1.2em;
  --jp-content-heading-margin-bottom: 0.8em;
  --jp-content-heading-font-weight: 500;

  /* Defaults use Material Design specification */
  --jp-content-font-color0: rgba(255, 255, 255, 1);
  --jp-content-font-color1: rgba(255, 255, 255, 1);
  --jp-content-font-color2: rgba(255, 255, 255, 0.7);
  --jp-content-font-color3: rgba(255, 255, 255, 0.5);
  --jp-content-link-color: var(--md-blue-300, #64b5f6);
  --jp-content-link-visited-color: var(--md-purple-300, #ba68c8);
  --jp-content-link-hover-color: var(--md-blue-400, #42a5f5);
  --jp-content-font-family: system-ui, -apple-system, blinkmacsystemfont,
    'Segoe UI', helvetica, arial, sans-serif, 'Apple Color Emoji',
    'Segoe UI Emoji', 'Segoe UI Symbol';

  /*
   * Code Fonts
   *
   * Code font variables are used for typography of code and other monospaces content.
   */

  --jp-code-font-size: 13px;
  --jp-code-line-height: 1.3077; /* 17px for 13px base */
  --jp-code-padding: 5px; /* 5px for 13px base, codemirror highlighting needs integer px value */
  --jp-code-font-family-default: menlo, consolas, 'DejaVu Sans Mono', monospace;
  --jp-code-font-family: var(--jp-code-font-family-default);

  /* This gives a magnification of about 125% in presentation mode over normal. */
  --jp-code-presentation-font-size: 16px;

  /* may need to tweak cursor width if you change font size */
  --jp-code-cursor-width0: 1.4px;
  --jp-code-cursor-width1: 2px;
  --jp-code-cursor-width2: 4px;

  /* Layout
   *
   * The following are the main layout colors use in JupyterLab. In a light
   * theme these would go from light to dark.
   */

  --jp-layout-color0: #111;
  --jp-layout-color1: var(--md-grey-900, #212121);
  --jp-layout-color2: var(--md-grey-800, #424242);
  --jp-layout-color3: var(--md-grey-700, #616161);
  --jp-layout-color4: var(--md-grey-600, #757575);

  /* Inverse Layout
   *
   * The following are the inverse layout colors use in JupyterLab. In a light
   * theme these would go from dark to light.
   */

  --jp-inverse-layout-color0: white;
  --jp-inverse-layout-color1: white;
  --jp-inverse-layout-color2: var(--md-grey-200, #eee);
  --jp-inverse-layout-color3: var(--md-grey-400, #bdbdbd);
  --jp-inverse-layout-color4: var(--md-grey-600, #757575);

  /* Brand/accent */

  --jp-brand-color0: var(--md-blue-700, #1976d2);
  --jp-brand-color1: var(--md-blue-500, #2196f3);
  --jp-brand-color2: var(--md-blue-300, #64b5f6);
  --jp-brand-color3: var(--md-blue-100, #bbdefb);
  --jp-brand-color4: var(--md-blue-50, #e3f2fd);
  --jp-accent-color0: var(--md-green-700, #388e3c);
  --jp-accent-color1: var(--md-green-500, #4caf50);
  --jp-accent-color2: var(--md-green-300, #81c784);
  --jp-accent-color3: var(--md-green-100, #c8e6c9);

  /* State colors (warn, error, success, info) */

  --jp-warn-color0: var(--md-orange-700, #f57c00);
  --jp-warn-color1: var(--md-orange-500, #ff9800);
  --jp-warn-color2: var(--md-orange-300, #ffb74d);
  --jp-warn-color3: var(--md-orange-100, #ffe0b2);
  --jp-error-color0: var(--md-red-700, #d32f2f);
  --jp-error-color1: var(--md-red-500, #f44336);
  --jp-error-color2: var(--md-red-300, #e57373);
  --jp-error-color3: var(--md-red-100, #ffcdd2);
  --jp-success-color0: var(--md-green-700, #388e3c);
  --jp-success-color1: var(--md-green-500, #4caf50);
  --jp-success-color2: var(--md-green-300, #81c784);
  --jp-success-color3: var(--md-green-100, #c8e6c9);
  --jp-info-color0: var(--md-cyan-700, #0097a7);
  --jp-info-color1: var(--md-cyan-500, #00bcd4);
  --jp-info-color2: var(--md-cyan-300, #4dd0e1);
  --jp-info-color3: var(--md-cyan-100, #b2ebf2);

  /* Cell specific styles */

  --jp-cell-padding: 5px;
  --jp-cell-collapser-width: 8px;
  --jp-cell-collapser-min-height: 20px;
  --jp-cell-collapser-not-active-hover-opacity: 0.6;
  --jp-cell-editor-background: var(--jp-layout-color1);
  --jp-cell-editor-border-color: var(--md-grey-700, #616161);
  --jp-cell-editor-box-shadow: inset 0 0 2px var(--md-blue-300, #64b5f6);
  --jp-cell-editor-active-background: var(--jp-layout-color0);
  --jp-cell-editor-active-border-color: var(--jp-brand-color1);
  --jp-cell-prompt-width: 64px;
  --jp-cell-prompt-font-family: var(--jp-code-font-family-default);
  --jp-cell-prompt-letter-spacing: 0;
  --jp-cell-prompt-opacity: 1;
  --jp-cell-prompt-not-active-opacity: 1;
  --jp-cell-prompt-not-active-font-color: var(--md-grey-300, #e0e0e0);

  /* A custom blend of MD grey and blue 600
   * See https://meyerweb.com/eric/tools/color-blend/#546E7A:1E88E5:5:hex */
  --jp-cell-inprompt-font-color: #307fc1;

  /* A custom blend of MD grey and orange 600
   * https://meyerweb.com/eric/tools/color-blend/#546E7A:F4511E:5:hex */
  --jp-cell-outprompt-font-color: #bf5b3d;

  /* Notebook specific styles */

  --jp-notebook-padding: 10px;
  --jp-notebook-select-background: var(--jp-layout-color1);
  --jp-notebook-multiselected-color: rgba(33, 150, 243, 0.24);

  /* The scroll padding is calculated to fill enough space at the bottom of the
  notebook to show one single-line cell (with appropriate padding) at the top
  when the notebook is scrolled all the way to the bottom. We also subtract one
  pixel so that no scrollbar appears if we have just one single-line cell in the
  notebook. This padding is to enable a 'scroll past end' feature in a notebook.
  */
  --jp-notebook-scroll-padding: calc(
    100% - var(--jp-code-font-size) * var(--jp-code-line-height) -
      var(--jp-code-padding) - var(--jp-cell-padding) - 1px
  );

  /* The scroll padding is calculated to provide enough space at the bottom of
     a text editor to allow the last line of code to be positioned at the top
     of the viewport when the editor is scrolled all the way down. We also
     subtract one pixel to avoid showing a scrollbar when the file contains
     only a single line. This padding enables a 'scroll past end' feature in
     text editors. */
  --jp-editor-scroll-padding: calc(
    100% - var(--jp-code-font-size) * var(--jp-code-line-height) -
      var(--jp-code-padding) - 1px
  );

  /* Rendermime styles */

  --jp-rendermime-error-background: rgba(244, 67, 54, 0.28);
  --jp-rendermime-table-row-background: var(--md-grey-900, #212121);
  --jp-rendermime-table-row-hover-background: rgba(3, 169, 244, 0.2);

  /* Dialog specific styles */

  --jp-dialog-background: rgba(0, 0, 0, 0.6);

  /* Console specific styles */

  --jp-console-padding: 10px;

  /* Toolbar specific styles */

  --jp-toolbar-border-color: var(--jp-border-color2);
  --jp-toolbar-micro-height: 8px;
  --jp-toolbar-background: var(--jp-layout-color1);
  --jp-toolbar-box-shadow: 0 0 2px 0 rgba(0, 0, 0, 0.8);
  --jp-toolbar-header-margin: 4px 4px 0 4px;
  --jp-toolbar-active-background: var(--jp-layout-color0);

  /* Statusbar specific styles */

  --jp-statusbar-height: 24px;

  /* Input field styles */

  --jp-input-box-shadow: inset 0 0 2px var(--md-blue-300, #64b5f6);
  --jp-input-active-background: var(--jp-layout-color0);
  --jp-input-hover-background: var(--jp-layout-color2);
  --jp-input-background: var(--md-grey-800, #424242);
  --jp-input-border-color: var(--jp-inverse-border-color);
  --jp-input-active-border-color: var(--jp-brand-color1);
  --jp-input-active-box-shadow-color: rgba(19, 124, 189, 0.3);

  /* General editor styles */

  --jp-editor-selected-background: var(--jp-layout-color2);
  --jp-editor-selected-focused-background: rgba(33, 150, 243, 0.24);
  --jp-editor-cursor-color: var(--jp-ui-font-color0);

  /* Code mirror specific styles */

  --jp-mirror-editor-keyword-color: var(--md-green-500, #4caf50);
  --jp-mirror-editor-atom-color: var(--md-blue-300, #64b5f6);
  --jp-mirror-editor-number-color: var(--md-green-400, #66bb6a);
  --jp-mirror-editor-def-color: var(--md-blue-600, #1e88e5);
  --jp-mirror-editor-variable-color: var(--md-grey-300, #e0e0e0);
  --jp-mirror-editor-variable-2-color: var(--md-blue-500, #2196f3);
  --jp-mirror-editor-variable-3-color: var(--md-green-600, #43a047);
  --jp-mirror-editor-punctuation-color: var(--md-blue-400, #42a5f5);
  --jp-mirror-editor-property-color: var(--md-blue-400, #42a5f5);
  --jp-mirror-editor-operator-color: #d48fff;
  --jp-mirror-editor-comment-color: #408080;
  --jp-mirror-editor-string-color: #ff7070;
  --jp-mirror-editor-string-2-color: var(--md-purple-300, #ba68c8);
  --jp-mirror-editor-meta-color: #a2f;
  --jp-mirror-editor-qualifier-color: #555;
  --jp-mirror-editor-builtin-color: var(--md-green-600, #43a047);
  --jp-mirror-editor-bracket-color: #997;
  --jp-mirror-editor-tag-color: var(--md-green-700, #388e3c);
  --jp-mirror-editor-attribute-color: var(--md-blue-700, #1976d2);
  --jp-mirror-editor-header-color: var(--md-blue-500, #2196f3);
  --jp-mirror-editor-quote-color: var(--md-green-300, #81c784);
  --jp-mirror-editor-link-color: var(--md-blue-700, #1976d2);
  --jp-mirror-editor-error-color: #f00;
  --jp-mirror-editor-hr-color: #999;

  /*
    RTC user specific colors.
    These colors are used for the cursor, username in the editor,
    and the icon of the user.
  */

  --jp-collaborator-color1: #ad4a00;
  --jp-collaborator-color2: #7b6a00;
  --jp-collaborator-color3: #007e00;
  --jp-collaborator-color4: #008772;
  --jp-collaborator-color5: #0079b9;
  --jp-collaborator-color6: #8b45c6;
  --jp-collaborator-color7: #be208b;

  /* Vega extension styles */

  --jp-vega-background: var(--md-grey-400, #bdbdbd);

  /* Sidebar-related styles */

  --jp-sidebar-min-width: 250px;

  /* Search-related styles */

  --jp-search-toggle-off-opacity: 0.6;
  --jp-search-toggle-hover-opacity: 0.8;
  --jp-search-toggle-on-opacity: 1;
  --jp-search-selected-match-background-color: rgb(255, 225, 0);
  --jp-search-selected-match-color: black;
  --jp-search-unselected-match-background-color: var(
    --jp-inverse-layout-color0
  );
  --jp-search-unselected-match-color: var(--jp-ui-inverse-font-color0);

  /* scrollbar related styles. Supports every browser except Edge. */

  /* colors based on JetBrain's Darcula theme */

  --jp-scrollbar-background-color: #3f4244;
  --jp-scrollbar-thumb-color: 88, 96, 97; /* need to specify thumb color as an RGB triplet */
  --jp-scrollbar-endpad: 3px; /* the minimum gap between the thumb and the ends of a scrollbar */

  /* hacks for setting the thumb shape. These do nothing in Firefox */

  --jp-scrollbar-thumb-margin: 3.5px; /* the space in between the sides of the thumb and the track */
  --jp-scrollbar-thumb-radius: 9px; /* set to a large-ish value for rounded endcaps on the thumb */

  /* Icon colors that work well with light or dark backgrounds */
  --jp-icon-contrast-color0: var(--md-purple-600, #8e24aa);
  --jp-icon-contrast-color1: var(--md-green-600, #43a047);
  --jp-icon-contrast-color2: var(--md-pink-600, #d81b60);
  --jp-icon-contrast-color3: var(--md-blue-600, #1e88e5);

  /* Button colors */
  --jp-accept-color-normal: var(--md-blue-700, #1976d2);
  --jp-accept-color-hover: var(--md-blue-800, #1565c0);
  --jp-accept-color-active: var(--md-blue-900, #0d47a1);
  --jp-warn-color-normal: var(--md-red-700, #d32f2f);
  --jp-warn-color-hover: var(--md-red-800, #c62828);
  --jp-warn-color-active: var(--md-red-900, #b71c1c);
  --jp-reject-color-normal: var(--md-grey-600, #757575);
  --jp-reject-color-hover: var(--md-grey-700, #616161);
  --jp-reject-color-active: var(--md-grey-800, #424242);

  /* File or activity icons and switch semantic variables */
  --jp-jupyter-icon-color: #f37626;
  --jp-notebook-icon-color: #f37626;
  --jp-json-icon-color: var(--md-orange-500, #ff9800);
  --jp-console-icon-background-color: var(--md-blue-500, #2196f3);
  --jp-console-icon-color: white;
  --jp-terminal-icon-background-color: var(--md-grey-200, #eee);
  --jp-terminal-icon-color: var(--md-grey-800, #424242);
  --jp-text-editor-icon-color: var(--md-grey-200, #eee);
  --jp-inspector-icon-color: var(--md-grey-200, #eee);
  --jp-switch-color: var(--md-grey-400, #bdbdbd);
  --jp-switch-true-position-color: var(--md-orange-700, #f57c00);
}

/* Completer specific styles */

.jp-Completer {
  --jp-completer-type-background0: transparent;
  --jp-completer-type-background1: #1f77b4;
  --jp-completer-type-background2: #ff7f0e;
  --jp-completer-type-background3: #2ca02c;
  --jp-completer-type-background4: #d62728;
  --jp-completer-type-background5: #9467bd;
  --jp-completer-type-background6: #8c564b;
  --jp-completer-type-background7: #e377c2;
  --jp-completer-type-background8: #7f7f7f;
  --jp-completer-type-background9: #bcbd22;
  --jp-completer-type-background10: #17becf;
}
`, ""]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 63546
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(85072);
/* harmony import */ var _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_cjs_js_variables_css_raw__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(14181);

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_css_loader_dist_cjs_js_variables_css_raw__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .A, options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_css_loader_dist_cjs_js_variables_css_raw__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .A.locals || {});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzU0Ni5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7Ozs7OztBQ25lQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGp1cHl0ZXJsYWIvdGhlbWUtZGFyay1leHRlbnNpb24vc3R5bGUvdmFyaWFibGVzLmNzcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL3RoZW1lLWRhcmstZXh0ZW5zaW9uL3N0eWxlL3ZhcmlhYmxlcy5jc3M/ODNiNyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBJbXBvcnRzXG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvbm9Tb3VyY2VNYXBzLmpzXCI7XG5pbXBvcnQgX19fQ1NTX0xPQURFUl9BUElfSU1QT1JUX19fIGZyb20gXCIuLi8uLi8uLi9jc3MtbG9hZGVyL2Rpc3QvcnVudGltZS9hcGkuanNcIjtcbnZhciBfX19DU1NfTE9BREVSX0VYUE9SVF9fXyA9IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyhfX19DU1NfTE9BREVSX0FQSV9OT19TT1VSQ0VNQVBfSU1QT1JUX19fKTtcbi8vIE1vZHVsZVxuX19fQ1NTX0xPQURFUl9FWFBPUlRfX18ucHVzaChbbW9kdWxlLmlkLCBgLyotLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLVxufCBDb3B5cmlnaHQgKGMpIEp1cHl0ZXIgRGV2ZWxvcG1lbnQgVGVhbS5cbnwgRGlzdHJpYnV0ZWQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBNb2RpZmllZCBCU0QgTGljZW5zZS5cbnwtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tKi9cblxuLypcblRoZSBmb2xsb3dpbmcgQ1NTIHZhcmlhYmxlcyBkZWZpbmUgdGhlIG1haW4sIHB1YmxpYyBBUEkgZm9yIHN0eWxpbmcgSnVweXRlckxhYi5cblRoZXNlIHZhcmlhYmxlcyBzaG91bGQgYmUgdXNlZCBieSBhbGwgcGx1Z2lucyB3aGVyZXZlciBwb3NzaWJsZS4gSW4gb3RoZXJcbndvcmRzLCBwbHVnaW5zIHNob3VsZCBub3QgZGVmaW5lIGN1c3RvbSBjb2xvcnMsIHNpemVzLCBldGMgdW5sZXNzIGFic29sdXRlbHlcbm5lY2Vzc2FyeS4gVGhpcyBlbmFibGVzIHVzZXJzIHRvIGNoYW5nZSB0aGUgdmlzdWFsIHRoZW1lIG9mIEp1cHl0ZXJMYWJcbmJ5IGNoYW5naW5nIHRoZXNlIHZhcmlhYmxlcy5cblxuTWFueSB2YXJpYWJsZXMgYXBwZWFyIGluIGFuIG9yZGVyZWQgc2VxdWVuY2UgKDAsMSwyLDMpLiBUaGVzZSBzZXF1ZW5jZXNcbmFyZSBkZXNpZ25lZCB0byB3b3JrIHdlbGwgdG9nZXRoZXIsIHNvIGZvciBleGFtcGxlLCBcXGAtLWpwLWJvcmRlci1jb2xvcjFcXGAgc2hvdWxkXG5iZSB1c2VkIHdpdGggXFxgLS1qcC1sYXlvdXQtY29sb3IxXFxgLiBUaGUgbnVtYmVycyBoYXZlIHRoZSBmb2xsb3dpbmcgbWVhbmluZ3M6XG5cbiogMDogc3VwZXItcHJpbWFyeSwgcmVzZXJ2ZWQgZm9yIHNwZWNpYWwgZW1waGFzaXNcbiogMTogcHJpbWFyeSwgbW9zdCBpbXBvcnRhbnQgdW5kZXIgbm9ybWFsIHNpdHVhdGlvbnNcbiogMjogc2Vjb25kYXJ5LCBuZXh0IG1vc3QgaW1wb3J0YW50IHVuZGVyIG5vcm1hbCBzaXR1YXRpb25zXG4qIDM6IHRlcnRpYXJ5LCBuZXh0IG1vc3QgaW1wb3J0YW50IHVuZGVyIG5vcm1hbCBzaXR1YXRpb25zXG5cblRocm91Z2hvdXQgSnVweXRlckxhYiwgd2UgYXJlIG1vc3RseSBmb2xsb3dpbmcgcHJpbmNpcGxlcyBmcm9tIEdvb2dsZSdzXG5NYXRlcmlhbCBEZXNpZ24gd2hlbiBzZWxlY3RpbmcgY29sb3JzLiBXZSBhcmUgbm90LCBob3dldmVyLCBmb2xsb3dpbmdcbmFsbCBvZiBNRCBhcyBpdCBpcyBub3Qgb3B0aW1pemVkIGZvciBkZW5zZSwgaW5mb3JtYXRpb24gcmljaCBVSXMuXG4qL1xuXG46cm9vdCB7XG4gIC8qIEVsZXZhdGlvblxuICAgKlxuICAgKiBXZSBzdHlsZSBib3gtc2hhZG93cyB1c2luZyBNYXRlcmlhbCBEZXNpZ24ncyBpZGVhIG9mIGVsZXZhdGlvbi4gVGhlc2UgcGFydGljdWxhciBudW1iZXJzIGFyZSB0YWtlbiBmcm9tIGhlcmU6XG4gICAqXG4gICAqIGh0dHBzOi8vZ2l0aHViLmNvbS9tYXRlcmlhbC1jb21wb25lbnRzL21hdGVyaWFsLWNvbXBvbmVudHMtd2ViXG4gICAqIGh0dHBzOi8vbWF0ZXJpYWwtY29tcG9uZW50cy13ZWIuYXBwc3BvdC5jb20vZWxldmF0aW9uLmh0bWxcbiAgICovXG5cbiAgLyogVGhlIGRhcmsgdGhlbWUgc2hhZG93cyBuZWVkIGEgYml0IG9mIHdvcmssIGJ1dCB0aGlzIHdpbGwgcHJvYmFibHkgYWxzbyByZXF1aXJlIHdvcmsgb24gdGhlIGNvcmUgbGF5b3V0XG4gICAqIGNvbG9ycyB1c2VkIGluIHRoZSB0aGVtZSBhcyB3ZWxsLiAqL1xuICAtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzczogMzI7XG4gIC0tanAtc2hhZG93LXVtYnJhLWNvbG9yOiByZ2JhKFxuICAgIHZhcigtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzcyksXG4gICAgdmFyKC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzKSxcbiAgICB2YXIoLS1qcC1zaGFkb3ctYmFzZS1saWdodG5lc3MpLFxuICAgIDAuMlxuICApO1xuICAtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvcjogcmdiYShcbiAgICB2YXIoLS1qcC1zaGFkb3ctYmFzZS1saWdodG5lc3MpLFxuICAgIHZhcigtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzcyksXG4gICAgdmFyKC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzKSxcbiAgICAwLjE0XG4gICk7XG4gIC0tanAtc2hhZG93LWFtYmllbnQtY29sb3I6IHJnYmEoXG4gICAgdmFyKC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzKSxcbiAgICB2YXIoLS1qcC1zaGFkb3ctYmFzZS1saWdodG5lc3MpLFxuICAgIHZhcigtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzcyksXG4gICAgMC4xMlxuICApO1xuICAtLWpwLWVsZXZhdGlvbi16MDogbm9uZTtcbiAgLS1qcC1lbGV2YXRpb24tejE6IDAgMnB4IDFweCAtMXB4IHZhcigtLWpwLXNoYWRvdy11bWJyYS1jb2xvciksXG4gICAgMCAxcHggMXB4IDAgdmFyKC0tanAtc2hhZG93LXBlbnVtYnJhLWNvbG9yKSxcbiAgICAwIDFweCAzcHggMCB2YXIoLS1qcC1zaGFkb3ctYW1iaWVudC1jb2xvcik7XG4gIC0tanAtZWxldmF0aW9uLXoyOiAwIDNweCAxcHggLTJweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgMnB4IDJweCAwIHZhcigtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvciksXG4gICAgMCAxcHggNXB4IDAgdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16NDogMCAycHggNHB4IC0xcHggdmFyKC0tanAtc2hhZG93LXVtYnJhLWNvbG9yKSxcbiAgICAwIDRweCA1cHggMCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgMXB4IDEwcHggMCB2YXIoLS1qcC1zaGFkb3ctYW1iaWVudC1jb2xvcik7XG4gIC0tanAtZWxldmF0aW9uLXo2OiAwIDNweCA1cHggLTFweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgNnB4IDEwcHggMCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgMXB4IDE4cHggMCB2YXIoLS1qcC1zaGFkb3ctYW1iaWVudC1jb2xvcik7XG4gIC0tanAtZWxldmF0aW9uLXo4OiAwIDVweCA1cHggLTNweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgOHB4IDEwcHggMXB4IHZhcigtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvciksXG4gICAgMCAzcHggMTRweCAycHggdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16MTI6IDAgN3B4IDhweCAtNHB4IHZhcigtLWpwLXNoYWRvdy11bWJyYS1jb2xvciksXG4gICAgMCAxMnB4IDE3cHggMnB4IHZhcigtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvciksXG4gICAgMCA1cHggMjJweCA0cHggdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16MTY6IDAgOHB4IDEwcHggLTVweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgMTZweCAyNHB4IDJweCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgNnB4IDMwcHggNXB4IHZhcigtLWpwLXNoYWRvdy1hbWJpZW50LWNvbG9yKTtcbiAgLS1qcC1lbGV2YXRpb24tejIwOiAwIDEwcHggMTNweCAtNnB4IHZhcigtLWpwLXNoYWRvdy11bWJyYS1jb2xvciksXG4gICAgMCAyMHB4IDMxcHggM3B4IHZhcigtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvciksXG4gICAgMCA4cHggMzhweCA3cHggdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16MjQ6IDAgMTFweCAxNXB4IC03cHggdmFyKC0tanAtc2hhZG93LXVtYnJhLWNvbG9yKSxcbiAgICAwIDI0cHggMzhweCAzcHggdmFyKC0tanAtc2hhZG93LXBlbnVtYnJhLWNvbG9yKSxcbiAgICAwIDlweCA0NnB4IDhweCB2YXIoLS1qcC1zaGFkb3ctYW1iaWVudC1jb2xvcik7XG5cbiAgLyogc2hvcnRjdXQgYnV0dG9uc1xuICAgKlxuICAgKiBUaGUgZm9sbG93aW5nIGNzcyB2YXJpYWJsZXMgYXJlIHVzZWQgdG8gc3BlY2lmeSB0aGUgdmlzdWFsXG4gICAqIHN0eWxpbmcgb2YgdGhlIGtleWJvYXJkIHNob3J0Y3V0IGJ1dHRvbnNcbiAgICovXG5cbiAgLS1qcC1zaG9ydGN1dHMtYnV0dG9uLWJhY2tncm91bmQ6IHZhcigtLWpwLWJyYW5kLWNvbG9yMik7XG4gIC0tanAtc2hvcnRjdXRzLWJ1dHRvbi1ob3Zlci1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1icmFuZC1jb2xvcjEpO1xuXG4gIC8qIEJvcmRlcnNcbiAgICpcbiAgICogVGhlIGZvbGxvd2luZyB2YXJpYWJsZXMsIHNwZWNpZnkgdGhlIHZpc3VhbCBzdHlsaW5nIG9mIGJvcmRlcnMgaW4gSnVweXRlckxhYi5cbiAgICovXG5cbiAgLS1qcC1ib3JkZXItd2lkdGg6IDFweDtcbiAgLS1qcC1ib3JkZXItY29sb3IwOiB2YXIoLS1tZC1ncmV5LTcwMCwgIzYxNjE2MSk7XG4gIC0tanAtYm9yZGVyLWNvbG9yMTogdmFyKC0tbWQtZ3JleS03MDAsICM2MTYxNjEpO1xuICAtLWpwLWJvcmRlci1jb2xvcjI6IHZhcigtLW1kLWdyZXktODAwLCAjNDI0MjQyKTtcbiAgLS1qcC1ib3JkZXItY29sb3IzOiB2YXIoLS1tZC1ncmV5LTkwMCwgIzIxMjEyMSk7XG4gIC0tanAtaW52ZXJzZS1ib3JkZXItY29sb3I6IHZhcigtLW1kLWdyZXktNjAwLCAjNzU3NTc1KTtcbiAgLS1qcC1ib3JkZXItcmFkaXVzOiAycHg7XG5cbiAgLyogVUkgRm9udHNcbiAgICpcbiAgICogVGhlIFVJIGZvbnQgQ1NTIHZhcmlhYmxlcyBhcmUgdXNlZCBmb3IgdGhlIHR5cG9ncmFwaHkgYWxsIG9mIHRoZSBKdXB5dGVyTGFiXG4gICAqIHVzZXIgaW50ZXJmYWNlIGVsZW1lbnRzIHRoYXQgYXJlIG5vdCBkaXJlY3RseSB1c2VyIGdlbmVyYXRlZCBjb250ZW50LlxuICAgKlxuICAgKiBUaGUgZm9udCBzaXppbmcgaGVyZSBpcyBkb25lIGFzc3VtaW5nIHRoYXQgdGhlIGJvZHkgZm9udCBzaXplIG9mIC0tanAtdWktZm9udC1zaXplMVxuICAgKiBpcyBhcHBsaWVkIHRvIGEgcGFyZW50IGVsZW1lbnQuIFdoZW4gY2hpbGRyZW4gZWxlbWVudHMsIHN1Y2ggYXMgaGVhZGluZ3MsIGFyZSBzaXplZFxuICAgKiBpbiBlbSBhbGwgdGhpbmdzIHdpbGwgYmUgY29tcHV0ZWQgcmVsYXRpdmUgdG8gdGhhdCBib2R5IHNpemUuXG4gICAqL1xuXG4gIC0tanAtdWktZm9udC1zY2FsZS1mYWN0b3I6IDEuMjtcbiAgLS1qcC11aS1mb250LXNpemUwOiAwLjgzMzMzZW07XG4gIC0tanAtdWktZm9udC1zaXplMTogMTNweDsgLyogQmFzZSBmb250IHNpemUgKi9cbiAgLS1qcC11aS1mb250LXNpemUyOiAxLjJlbTtcbiAgLS1qcC11aS1mb250LXNpemUzOiAxLjQ0ZW07XG4gIC0tanAtdWktZm9udC1mYW1pbHk6IHN5c3RlbS11aSwgLWFwcGxlLXN5c3RlbSwgYmxpbmttYWNzeXN0ZW1mb250LCAnU2Vnb2UgVUknLFxuICAgIGhlbHZldGljYSwgYXJpYWwsIHNhbnMtc2VyaWYsICdBcHBsZSBDb2xvciBFbW9qaScsICdTZWdvZSBVSSBFbW9qaScsXG4gICAgJ1NlZ29lIFVJIFN5bWJvbCc7XG5cbiAgLypcbiAgICogVXNlIHRoZXNlIGZvbnQgY29sb3JzIGFnYWluc3QgdGhlIGNvcnJlc3BvbmRpbmcgbWFpbiBsYXlvdXQgY29sb3JzLlxuICAgKiBJbiBhIGxpZ2h0IHRoZW1lLCB0aGVzZSBnbyBmcm9tIGRhcmsgdG8gbGlnaHQuXG4gICAqL1xuXG4gIC8qIERlZmF1bHRzIHVzZSBNYXRlcmlhbCBEZXNpZ24gc3BlY2lmaWNhdGlvbiAqL1xuICAtLWpwLXVpLWZvbnQtY29sb3IwOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDEpO1xuICAtLWpwLXVpLWZvbnQtY29sb3IxOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDAuODcpO1xuICAtLWpwLXVpLWZvbnQtY29sb3IyOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDAuNTQpO1xuICAtLWpwLXVpLWZvbnQtY29sb3IzOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMzgpO1xuXG4gIC8qXG4gICAqIFVzZSB0aGVzZSBhZ2FpbnN0IHRoZSBicmFuZC9hY2NlbnQvd2Fybi9lcnJvciBjb2xvcnMuXG4gICAqIFRoZXNlIHdpbGwgdHlwaWNhbGx5IGdvIGZyb20gbGlnaHQgdG8gZGFya2VyLCBpbiBib3RoIGEgZGFyayBhbmQgbGlnaHQgdGhlbWUuXG4gICAqL1xuXG4gIC0tanAtdWktaW52ZXJzZS1mb250LWNvbG9yMDogcmdiYSgwLCAwLCAwLCAxKTtcbiAgLS1qcC11aS1pbnZlcnNlLWZvbnQtY29sb3IxOiByZ2JhKDAsIDAsIDAsIDAuOCk7XG4gIC0tanAtdWktaW52ZXJzZS1mb250LWNvbG9yMjogcmdiYSgwLCAwLCAwLCAwLjUpO1xuICAtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjM6IHJnYmEoMCwgMCwgMCwgMC4zKTtcblxuICAvKiBDb250ZW50IEZvbnRzXG4gICAqXG4gICAqIENvbnRlbnQgZm9udCB2YXJpYWJsZXMgYXJlIHVzZWQgZm9yIHR5cG9ncmFwaHkgb2YgdXNlciBnZW5lcmF0ZWQgY29udGVudC5cbiAgICpcbiAgICogVGhlIGZvbnQgc2l6aW5nIGhlcmUgaXMgZG9uZSBhc3N1bWluZyB0aGF0IHRoZSBib2R5IGZvbnQgc2l6ZSBvZiAtLWpwLWNvbnRlbnQtZm9udC1zaXplMVxuICAgKiBpcyBhcHBsaWVkIHRvIGEgcGFyZW50IGVsZW1lbnQuIFdoZW4gY2hpbGRyZW4gZWxlbWVudHMsIHN1Y2ggYXMgaGVhZGluZ3MsIGFyZSBzaXplZFxuICAgKiBpbiBlbSBhbGwgdGhpbmdzIHdpbGwgYmUgY29tcHV0ZWQgcmVsYXRpdmUgdG8gdGhhdCBib2R5IHNpemUuXG4gICAqL1xuXG4gIC0tanAtY29udGVudC1saW5lLWhlaWdodDogMS42O1xuICAtLWpwLWNvbnRlbnQtZm9udC1zY2FsZS1mYWN0b3I6IDEuMjtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTA6IDAuODMzMzNlbTtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTE6IDE0cHg7IC8qIEJhc2UgZm9udCBzaXplICovXG4gIC0tanAtY29udGVudC1mb250LXNpemUyOiAxLjJlbTtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTM6IDEuNDRlbTtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTQ6IDEuNzI4ZW07XG4gIC0tanAtY29udGVudC1mb250LXNpemU1OiAyLjA3MzZlbTtcblxuICAvKiBUaGlzIGdpdmVzIGEgbWFnbmlmaWNhdGlvbiBvZiBhYm91dCAxMjUlIGluIHByZXNlbnRhdGlvbiBtb2RlIG92ZXIgbm9ybWFsLiAqL1xuICAtLWpwLWNvbnRlbnQtcHJlc2VudGF0aW9uLWZvbnQtc2l6ZTE6IDE3cHg7XG4gIC0tanAtY29udGVudC1oZWFkaW5nLWxpbmUtaGVpZ2h0OiAxO1xuICAtLWpwLWNvbnRlbnQtaGVhZGluZy1tYXJnaW4tdG9wOiAxLjJlbTtcbiAgLS1qcC1jb250ZW50LWhlYWRpbmctbWFyZ2luLWJvdHRvbTogMC44ZW07XG4gIC0tanAtY29udGVudC1oZWFkaW5nLWZvbnQtd2VpZ2h0OiA1MDA7XG5cbiAgLyogRGVmYXVsdHMgdXNlIE1hdGVyaWFsIERlc2lnbiBzcGVjaWZpY2F0aW9uICovXG4gIC0tanAtY29udGVudC1mb250LWNvbG9yMDogcmdiYSgyNTUsIDI1NSwgMjU1LCAxKTtcbiAgLS1qcC1jb250ZW50LWZvbnQtY29sb3IxOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDEpO1xuICAtLWpwLWNvbnRlbnQtZm9udC1jb2xvcjI6IHJnYmEoMjU1LCAyNTUsIDI1NSwgMC43KTtcbiAgLS1qcC1jb250ZW50LWZvbnQtY29sb3IzOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDAuNSk7XG4gIC0tanAtY29udGVudC1saW5rLWNvbG9yOiB2YXIoLS1tZC1ibHVlLTMwMCwgIzY0YjVmNik7XG4gIC0tanAtY29udGVudC1saW5rLXZpc2l0ZWQtY29sb3I6IHZhcigtLW1kLXB1cnBsZS0zMDAsICNiYTY4YzgpO1xuICAtLWpwLWNvbnRlbnQtbGluay1ob3Zlci1jb2xvcjogdmFyKC0tbWQtYmx1ZS00MDAsICM0MmE1ZjUpO1xuICAtLWpwLWNvbnRlbnQtZm9udC1mYW1pbHk6IHN5c3RlbS11aSwgLWFwcGxlLXN5c3RlbSwgYmxpbmttYWNzeXN0ZW1mb250LFxuICAgICdTZWdvZSBVSScsIGhlbHZldGljYSwgYXJpYWwsIHNhbnMtc2VyaWYsICdBcHBsZSBDb2xvciBFbW9qaScsXG4gICAgJ1NlZ29lIFVJIEVtb2ppJywgJ1NlZ29lIFVJIFN5bWJvbCc7XG5cbiAgLypcbiAgICogQ29kZSBGb250c1xuICAgKlxuICAgKiBDb2RlIGZvbnQgdmFyaWFibGVzIGFyZSB1c2VkIGZvciB0eXBvZ3JhcGh5IG9mIGNvZGUgYW5kIG90aGVyIG1vbm9zcGFjZXMgY29udGVudC5cbiAgICovXG5cbiAgLS1qcC1jb2RlLWZvbnQtc2l6ZTogMTNweDtcbiAgLS1qcC1jb2RlLWxpbmUtaGVpZ2h0OiAxLjMwNzc7IC8qIDE3cHggZm9yIDEzcHggYmFzZSAqL1xuICAtLWpwLWNvZGUtcGFkZGluZzogNXB4OyAvKiA1cHggZm9yIDEzcHggYmFzZSwgY29kZW1pcnJvciBoaWdobGlnaHRpbmcgbmVlZHMgaW50ZWdlciBweCB2YWx1ZSAqL1xuICAtLWpwLWNvZGUtZm9udC1mYW1pbHktZGVmYXVsdDogbWVubG8sIGNvbnNvbGFzLCAnRGVqYVZ1IFNhbnMgTW9ubycsIG1vbm9zcGFjZTtcbiAgLS1qcC1jb2RlLWZvbnQtZmFtaWx5OiB2YXIoLS1qcC1jb2RlLWZvbnQtZmFtaWx5LWRlZmF1bHQpO1xuXG4gIC8qIFRoaXMgZ2l2ZXMgYSBtYWduaWZpY2F0aW9uIG9mIGFib3V0IDEyNSUgaW4gcHJlc2VudGF0aW9uIG1vZGUgb3ZlciBub3JtYWwuICovXG4gIC0tanAtY29kZS1wcmVzZW50YXRpb24tZm9udC1zaXplOiAxNnB4O1xuXG4gIC8qIG1heSBuZWVkIHRvIHR3ZWFrIGN1cnNvciB3aWR0aCBpZiB5b3UgY2hhbmdlIGZvbnQgc2l6ZSAqL1xuICAtLWpwLWNvZGUtY3Vyc29yLXdpZHRoMDogMS40cHg7XG4gIC0tanAtY29kZS1jdXJzb3Itd2lkdGgxOiAycHg7XG4gIC0tanAtY29kZS1jdXJzb3Itd2lkdGgyOiA0cHg7XG5cbiAgLyogTGF5b3V0XG4gICAqXG4gICAqIFRoZSBmb2xsb3dpbmcgYXJlIHRoZSBtYWluIGxheW91dCBjb2xvcnMgdXNlIGluIEp1cHl0ZXJMYWIuIEluIGEgbGlnaHRcbiAgICogdGhlbWUgdGhlc2Ugd291bGQgZ28gZnJvbSBsaWdodCB0byBkYXJrLlxuICAgKi9cblxuICAtLWpwLWxheW91dC1jb2xvcjA6ICMxMTE7XG4gIC0tanAtbGF5b3V0LWNvbG9yMTogdmFyKC0tbWQtZ3JleS05MDAsICMyMTIxMjEpO1xuICAtLWpwLWxheW91dC1jb2xvcjI6IHZhcigtLW1kLWdyZXktODAwLCAjNDI0MjQyKTtcbiAgLS1qcC1sYXlvdXQtY29sb3IzOiB2YXIoLS1tZC1ncmV5LTcwMCwgIzYxNjE2MSk7XG4gIC0tanAtbGF5b3V0LWNvbG9yNDogdmFyKC0tbWQtZ3JleS02MDAsICM3NTc1NzUpO1xuXG4gIC8qIEludmVyc2UgTGF5b3V0XG4gICAqXG4gICAqIFRoZSBmb2xsb3dpbmcgYXJlIHRoZSBpbnZlcnNlIGxheW91dCBjb2xvcnMgdXNlIGluIEp1cHl0ZXJMYWIuIEluIGEgbGlnaHRcbiAgICogdGhlbWUgdGhlc2Ugd291bGQgZ28gZnJvbSBkYXJrIHRvIGxpZ2h0LlxuICAgKi9cblxuICAtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yMDogd2hpdGU7XG4gIC0tanAtaW52ZXJzZS1sYXlvdXQtY29sb3IxOiB3aGl0ZTtcbiAgLS1qcC1pbnZlcnNlLWxheW91dC1jb2xvcjI6IHZhcigtLW1kLWdyZXktMjAwLCAjZWVlKTtcbiAgLS1qcC1pbnZlcnNlLWxheW91dC1jb2xvcjM6IHZhcigtLW1kLWdyZXktNDAwLCAjYmRiZGJkKTtcbiAgLS1qcC1pbnZlcnNlLWxheW91dC1jb2xvcjQ6IHZhcigtLW1kLWdyZXktNjAwLCAjNzU3NTc1KTtcblxuICAvKiBCcmFuZC9hY2NlbnQgKi9cblxuICAtLWpwLWJyYW5kLWNvbG9yMDogdmFyKC0tbWQtYmx1ZS03MDAsICMxOTc2ZDIpO1xuICAtLWpwLWJyYW5kLWNvbG9yMTogdmFyKC0tbWQtYmx1ZS01MDAsICMyMTk2ZjMpO1xuICAtLWpwLWJyYW5kLWNvbG9yMjogdmFyKC0tbWQtYmx1ZS0zMDAsICM2NGI1ZjYpO1xuICAtLWpwLWJyYW5kLWNvbG9yMzogdmFyKC0tbWQtYmx1ZS0xMDAsICNiYmRlZmIpO1xuICAtLWpwLWJyYW5kLWNvbG9yNDogdmFyKC0tbWQtYmx1ZS01MCwgI2UzZjJmZCk7XG4gIC0tanAtYWNjZW50LWNvbG9yMDogdmFyKC0tbWQtZ3JlZW4tNzAwLCAjMzg4ZTNjKTtcbiAgLS1qcC1hY2NlbnQtY29sb3IxOiB2YXIoLS1tZC1ncmVlbi01MDAsICM0Y2FmNTApO1xuICAtLWpwLWFjY2VudC1jb2xvcjI6IHZhcigtLW1kLWdyZWVuLTMwMCwgIzgxYzc4NCk7XG4gIC0tanAtYWNjZW50LWNvbG9yMzogdmFyKC0tbWQtZ3JlZW4tMTAwLCAjYzhlNmM5KTtcblxuICAvKiBTdGF0ZSBjb2xvcnMgKHdhcm4sIGVycm9yLCBzdWNjZXNzLCBpbmZvKSAqL1xuXG4gIC0tanAtd2Fybi1jb2xvcjA6IHZhcigtLW1kLW9yYW5nZS03MDAsICNmNTdjMDApO1xuICAtLWpwLXdhcm4tY29sb3IxOiB2YXIoLS1tZC1vcmFuZ2UtNTAwLCAjZmY5ODAwKTtcbiAgLS1qcC13YXJuLWNvbG9yMjogdmFyKC0tbWQtb3JhbmdlLTMwMCwgI2ZmYjc0ZCk7XG4gIC0tanAtd2Fybi1jb2xvcjM6IHZhcigtLW1kLW9yYW5nZS0xMDAsICNmZmUwYjIpO1xuICAtLWpwLWVycm9yLWNvbG9yMDogdmFyKC0tbWQtcmVkLTcwMCwgI2QzMmYyZik7XG4gIC0tanAtZXJyb3ItY29sb3IxOiB2YXIoLS1tZC1yZWQtNTAwLCAjZjQ0MzM2KTtcbiAgLS1qcC1lcnJvci1jb2xvcjI6IHZhcigtLW1kLXJlZC0zMDAsICNlNTczNzMpO1xuICAtLWpwLWVycm9yLWNvbG9yMzogdmFyKC0tbWQtcmVkLTEwMCwgI2ZmY2RkMik7XG4gIC0tanAtc3VjY2Vzcy1jb2xvcjA6IHZhcigtLW1kLWdyZWVuLTcwMCwgIzM4OGUzYyk7XG4gIC0tanAtc3VjY2Vzcy1jb2xvcjE6IHZhcigtLW1kLWdyZWVuLTUwMCwgIzRjYWY1MCk7XG4gIC0tanAtc3VjY2Vzcy1jb2xvcjI6IHZhcigtLW1kLWdyZWVuLTMwMCwgIzgxYzc4NCk7XG4gIC0tanAtc3VjY2Vzcy1jb2xvcjM6IHZhcigtLW1kLWdyZWVuLTEwMCwgI2M4ZTZjOSk7XG4gIC0tanAtaW5mby1jb2xvcjA6IHZhcigtLW1kLWN5YW4tNzAwLCAjMDA5N2E3KTtcbiAgLS1qcC1pbmZvLWNvbG9yMTogdmFyKC0tbWQtY3lhbi01MDAsICMwMGJjZDQpO1xuICAtLWpwLWluZm8tY29sb3IyOiB2YXIoLS1tZC1jeWFuLTMwMCwgIzRkZDBlMSk7XG4gIC0tanAtaW5mby1jb2xvcjM6IHZhcigtLW1kLWN5YW4tMTAwLCAjYjJlYmYyKTtcblxuICAvKiBDZWxsIHNwZWNpZmljIHN0eWxlcyAqL1xuXG4gIC0tanAtY2VsbC1wYWRkaW5nOiA1cHg7XG4gIC0tanAtY2VsbC1jb2xsYXBzZXItd2lkdGg6IDhweDtcbiAgLS1qcC1jZWxsLWNvbGxhcHNlci1taW4taGVpZ2h0OiAyMHB4O1xuICAtLWpwLWNlbGwtY29sbGFwc2VyLW5vdC1hY3RpdmUtaG92ZXItb3BhY2l0eTogMC42O1xuICAtLWpwLWNlbGwtZWRpdG9yLWJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICAtLWpwLWNlbGwtZWRpdG9yLWJvcmRlci1jb2xvcjogdmFyKC0tbWQtZ3JleS03MDAsICM2MTYxNjEpO1xuICAtLWpwLWNlbGwtZWRpdG9yLWJveC1zaGFkb3c6IGluc2V0IDAgMCAycHggdmFyKC0tbWQtYmx1ZS0zMDAsICM2NGI1ZjYpO1xuICAtLWpwLWNlbGwtZWRpdG9yLWFjdGl2ZS1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IwKTtcbiAgLS1qcC1jZWxsLWVkaXRvci1hY3RpdmUtYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1icmFuZC1jb2xvcjEpO1xuICAtLWpwLWNlbGwtcHJvbXB0LXdpZHRoOiA2NHB4O1xuICAtLWpwLWNlbGwtcHJvbXB0LWZvbnQtZmFtaWx5OiB2YXIoLS1qcC1jb2RlLWZvbnQtZmFtaWx5LWRlZmF1bHQpO1xuICAtLWpwLWNlbGwtcHJvbXB0LWxldHRlci1zcGFjaW5nOiAwO1xuICAtLWpwLWNlbGwtcHJvbXB0LW9wYWNpdHk6IDE7XG4gIC0tanAtY2VsbC1wcm9tcHQtbm90LWFjdGl2ZS1vcGFjaXR5OiAxO1xuICAtLWpwLWNlbGwtcHJvbXB0LW5vdC1hY3RpdmUtZm9udC1jb2xvcjogdmFyKC0tbWQtZ3JleS0zMDAsICNlMGUwZTApO1xuXG4gIC8qIEEgY3VzdG9tIGJsZW5kIG9mIE1EIGdyZXkgYW5kIGJsdWUgNjAwXG4gICAqIFNlZSBodHRwczovL21leWVyd2ViLmNvbS9lcmljL3Rvb2xzL2NvbG9yLWJsZW5kLyM1NDZFN0E6MUU4OEU1OjU6aGV4ICovXG4gIC0tanAtY2VsbC1pbnByb21wdC1mb250LWNvbG9yOiAjMzA3ZmMxO1xuXG4gIC8qIEEgY3VzdG9tIGJsZW5kIG9mIE1EIGdyZXkgYW5kIG9yYW5nZSA2MDBcbiAgICogaHR0cHM6Ly9tZXllcndlYi5jb20vZXJpYy90b29scy9jb2xvci1ibGVuZC8jNTQ2RTdBOkY0NTExRTo1OmhleCAqL1xuICAtLWpwLWNlbGwtb3V0cHJvbXB0LWZvbnQtY29sb3I6ICNiZjViM2Q7XG5cbiAgLyogTm90ZWJvb2sgc3BlY2lmaWMgc3R5bGVzICovXG5cbiAgLS1qcC1ub3RlYm9vay1wYWRkaW5nOiAxMHB4O1xuICAtLWpwLW5vdGVib29rLXNlbGVjdC1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IxKTtcbiAgLS1qcC1ub3RlYm9vay1tdWx0aXNlbGVjdGVkLWNvbG9yOiByZ2JhKDMzLCAxNTAsIDI0MywgMC4yNCk7XG5cbiAgLyogVGhlIHNjcm9sbCBwYWRkaW5nIGlzIGNhbGN1bGF0ZWQgdG8gZmlsbCBlbm91Z2ggc3BhY2UgYXQgdGhlIGJvdHRvbSBvZiB0aGVcbiAgbm90ZWJvb2sgdG8gc2hvdyBvbmUgc2luZ2xlLWxpbmUgY2VsbCAod2l0aCBhcHByb3ByaWF0ZSBwYWRkaW5nKSBhdCB0aGUgdG9wXG4gIHdoZW4gdGhlIG5vdGVib29rIGlzIHNjcm9sbGVkIGFsbCB0aGUgd2F5IHRvIHRoZSBib3R0b20uIFdlIGFsc28gc3VidHJhY3Qgb25lXG4gIHBpeGVsIHNvIHRoYXQgbm8gc2Nyb2xsYmFyIGFwcGVhcnMgaWYgd2UgaGF2ZSBqdXN0IG9uZSBzaW5nbGUtbGluZSBjZWxsIGluIHRoZVxuICBub3RlYm9vay4gVGhpcyBwYWRkaW5nIGlzIHRvIGVuYWJsZSBhICdzY3JvbGwgcGFzdCBlbmQnIGZlYXR1cmUgaW4gYSBub3RlYm9vay5cbiAgKi9cbiAgLS1qcC1ub3RlYm9vay1zY3JvbGwtcGFkZGluZzogY2FsYyhcbiAgICAxMDAlIC0gdmFyKC0tanAtY29kZS1mb250LXNpemUpICogdmFyKC0tanAtY29kZS1saW5lLWhlaWdodCkgLVxuICAgICAgdmFyKC0tanAtY29kZS1wYWRkaW5nKSAtIHZhcigtLWpwLWNlbGwtcGFkZGluZykgLSAxcHhcbiAgKTtcblxuICAvKiBUaGUgc2Nyb2xsIHBhZGRpbmcgaXMgY2FsY3VsYXRlZCB0byBwcm92aWRlIGVub3VnaCBzcGFjZSBhdCB0aGUgYm90dG9tIG9mXG4gICAgIGEgdGV4dCBlZGl0b3IgdG8gYWxsb3cgdGhlIGxhc3QgbGluZSBvZiBjb2RlIHRvIGJlIHBvc2l0aW9uZWQgYXQgdGhlIHRvcFxuICAgICBvZiB0aGUgdmlld3BvcnQgd2hlbiB0aGUgZWRpdG9yIGlzIHNjcm9sbGVkIGFsbCB0aGUgd2F5IGRvd24uIFdlIGFsc29cbiAgICAgc3VidHJhY3Qgb25lIHBpeGVsIHRvIGF2b2lkIHNob3dpbmcgYSBzY3JvbGxiYXIgd2hlbiB0aGUgZmlsZSBjb250YWluc1xuICAgICBvbmx5IGEgc2luZ2xlIGxpbmUuIFRoaXMgcGFkZGluZyBlbmFibGVzIGEgJ3Njcm9sbCBwYXN0IGVuZCcgZmVhdHVyZSBpblxuICAgICB0ZXh0IGVkaXRvcnMuICovXG4gIC0tanAtZWRpdG9yLXNjcm9sbC1wYWRkaW5nOiBjYWxjKFxuICAgIDEwMCUgLSB2YXIoLS1qcC1jb2RlLWZvbnQtc2l6ZSkgKiB2YXIoLS1qcC1jb2RlLWxpbmUtaGVpZ2h0KSAtXG4gICAgICB2YXIoLS1qcC1jb2RlLXBhZGRpbmcpIC0gMXB4XG4gICk7XG5cbiAgLyogUmVuZGVybWltZSBzdHlsZXMgKi9cblxuICAtLWpwLXJlbmRlcm1pbWUtZXJyb3ItYmFja2dyb3VuZDogcmdiYSgyNDQsIDY3LCA1NCwgMC4yOCk7XG4gIC0tanAtcmVuZGVybWltZS10YWJsZS1yb3ctYmFja2dyb3VuZDogdmFyKC0tbWQtZ3JleS05MDAsICMyMTIxMjEpO1xuICAtLWpwLXJlbmRlcm1pbWUtdGFibGUtcm93LWhvdmVyLWJhY2tncm91bmQ6IHJnYmEoMywgMTY5LCAyNDQsIDAuMik7XG5cbiAgLyogRGlhbG9nIHNwZWNpZmljIHN0eWxlcyAqL1xuXG4gIC0tanAtZGlhbG9nLWJhY2tncm91bmQ6IHJnYmEoMCwgMCwgMCwgMC42KTtcblxuICAvKiBDb25zb2xlIHNwZWNpZmljIHN0eWxlcyAqL1xuXG4gIC0tanAtY29uc29sZS1wYWRkaW5nOiAxMHB4O1xuXG4gIC8qIFRvb2xiYXIgc3BlY2lmaWMgc3R5bGVzICovXG5cbiAgLS1qcC10b29sYmFyLWJvcmRlci1jb2xvcjogdmFyKC0tanAtYm9yZGVyLWNvbG9yMik7XG4gIC0tanAtdG9vbGJhci1taWNyby1oZWlnaHQ6IDhweDtcbiAgLS1qcC10b29sYmFyLWJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICAtLWpwLXRvb2xiYXItYm94LXNoYWRvdzogMCAwIDJweCAwIHJnYmEoMCwgMCwgMCwgMC44KTtcbiAgLS1qcC10b29sYmFyLWhlYWRlci1tYXJnaW46IDRweCA0cHggMCA0cHg7XG4gIC0tanAtdG9vbGJhci1hY3RpdmUtYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMCk7XG5cbiAgLyogU3RhdHVzYmFyIHNwZWNpZmljIHN0eWxlcyAqL1xuXG4gIC0tanAtc3RhdHVzYmFyLWhlaWdodDogMjRweDtcblxuICAvKiBJbnB1dCBmaWVsZCBzdHlsZXMgKi9cblxuICAtLWpwLWlucHV0LWJveC1zaGFkb3c6IGluc2V0IDAgMCAycHggdmFyKC0tbWQtYmx1ZS0zMDAsICM2NGI1ZjYpO1xuICAtLWpwLWlucHV0LWFjdGl2ZS1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IwKTtcbiAgLS1qcC1pbnB1dC1ob3Zlci1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IyKTtcbiAgLS1qcC1pbnB1dC1iYWNrZ3JvdW5kOiB2YXIoLS1tZC1ncmV5LTgwMCwgIzQyNDI0Mik7XG4gIC0tanAtaW5wdXQtYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1pbnZlcnNlLWJvcmRlci1jb2xvcik7XG4gIC0tanAtaW5wdXQtYWN0aXZlLWJvcmRlci1jb2xvcjogdmFyKC0tanAtYnJhbmQtY29sb3IxKTtcbiAgLS1qcC1pbnB1dC1hY3RpdmUtYm94LXNoYWRvdy1jb2xvcjogcmdiYSgxOSwgMTI0LCAxODksIDAuMyk7XG5cbiAgLyogR2VuZXJhbCBlZGl0b3Igc3R5bGVzICovXG5cbiAgLS1qcC1lZGl0b3Itc2VsZWN0ZWQtYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMik7XG4gIC0tanAtZWRpdG9yLXNlbGVjdGVkLWZvY3VzZWQtYmFja2dyb3VuZDogcmdiYSgzMywgMTUwLCAyNDMsIDAuMjQpO1xuICAtLWpwLWVkaXRvci1jdXJzb3ItY29sb3I6IHZhcigtLWpwLXVpLWZvbnQtY29sb3IwKTtcblxuICAvKiBDb2RlIG1pcnJvciBzcGVjaWZpYyBzdHlsZXMgKi9cblxuICAtLWpwLW1pcnJvci1lZGl0b3Ita2V5d29yZC1jb2xvcjogdmFyKC0tbWQtZ3JlZW4tNTAwLCAjNGNhZjUwKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWF0b20tY29sb3I6IHZhcigtLW1kLWJsdWUtMzAwLCAjNjRiNWY2KTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLW51bWJlci1jb2xvcjogdmFyKC0tbWQtZ3JlZW4tNDAwLCAjNjZiYjZhKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWRlZi1jb2xvcjogdmFyKC0tbWQtYmx1ZS02MDAsICMxZTg4ZTUpO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItdmFyaWFibGUtY29sb3I6IHZhcigtLW1kLWdyZXktMzAwLCAjZTBlMGUwKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXZhcmlhYmxlLTItY29sb3I6IHZhcigtLW1kLWJsdWUtNTAwLCAjMjE5NmYzKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXZhcmlhYmxlLTMtY29sb3I6IHZhcigtLW1kLWdyZWVuLTYwMCwgIzQzYTA0Nyk7XG4gIC0tanAtbWlycm9yLWVkaXRvci1wdW5jdHVhdGlvbi1jb2xvcjogdmFyKC0tbWQtYmx1ZS00MDAsICM0MmE1ZjUpO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItcHJvcGVydHktY29sb3I6IHZhcigtLW1kLWJsdWUtNDAwLCAjNDJhNWY1KTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLW9wZXJhdG9yLWNvbG9yOiAjZDQ4ZmZmO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItY29tbWVudC1jb2xvcjogIzQwODA4MDtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXN0cmluZy1jb2xvcjogI2ZmNzA3MDtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXN0cmluZy0yLWNvbG9yOiB2YXIoLS1tZC1wdXJwbGUtMzAwLCAjYmE2OGM4KTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLW1ldGEtY29sb3I6ICNhMmY7XG4gIC0tanAtbWlycm9yLWVkaXRvci1xdWFsaWZpZXItY29sb3I6ICM1NTU7XG4gIC0tanAtbWlycm9yLWVkaXRvci1idWlsdGluLWNvbG9yOiB2YXIoLS1tZC1ncmVlbi02MDAsICM0M2EwNDcpO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItYnJhY2tldC1jb2xvcjogIzk5NztcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXRhZy1jb2xvcjogdmFyKC0tbWQtZ3JlZW4tNzAwLCAjMzg4ZTNjKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWF0dHJpYnV0ZS1jb2xvcjogdmFyKC0tbWQtYmx1ZS03MDAsICMxOTc2ZDIpO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItaGVhZGVyLWNvbG9yOiB2YXIoLS1tZC1ibHVlLTUwMCwgIzIxOTZmMyk7XG4gIC0tanAtbWlycm9yLWVkaXRvci1xdW90ZS1jb2xvcjogdmFyKC0tbWQtZ3JlZW4tMzAwLCAjODFjNzg0KTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWxpbmstY29sb3I6IHZhcigtLW1kLWJsdWUtNzAwLCAjMTk3NmQyKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWVycm9yLWNvbG9yOiAjZjAwO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItaHItY29sb3I6ICM5OTk7XG5cbiAgLypcbiAgICBSVEMgdXNlciBzcGVjaWZpYyBjb2xvcnMuXG4gICAgVGhlc2UgY29sb3JzIGFyZSB1c2VkIGZvciB0aGUgY3Vyc29yLCB1c2VybmFtZSBpbiB0aGUgZWRpdG9yLFxuICAgIGFuZCB0aGUgaWNvbiBvZiB0aGUgdXNlci5cbiAgKi9cblxuICAtLWpwLWNvbGxhYm9yYXRvci1jb2xvcjE6ICNhZDRhMDA7XG4gIC0tanAtY29sbGFib3JhdG9yLWNvbG9yMjogIzdiNmEwMDtcbiAgLS1qcC1jb2xsYWJvcmF0b3ItY29sb3IzOiAjMDA3ZTAwO1xuICAtLWpwLWNvbGxhYm9yYXRvci1jb2xvcjQ6ICMwMDg3NzI7XG4gIC0tanAtY29sbGFib3JhdG9yLWNvbG9yNTogIzAwNzliOTtcbiAgLS1qcC1jb2xsYWJvcmF0b3ItY29sb3I2OiAjOGI0NWM2O1xuICAtLWpwLWNvbGxhYm9yYXRvci1jb2xvcjc6ICNiZTIwOGI7XG5cbiAgLyogVmVnYSBleHRlbnNpb24gc3R5bGVzICovXG5cbiAgLS1qcC12ZWdhLWJhY2tncm91bmQ6IHZhcigtLW1kLWdyZXktNDAwLCAjYmRiZGJkKTtcblxuICAvKiBTaWRlYmFyLXJlbGF0ZWQgc3R5bGVzICovXG5cbiAgLS1qcC1zaWRlYmFyLW1pbi13aWR0aDogMjUwcHg7XG5cbiAgLyogU2VhcmNoLXJlbGF0ZWQgc3R5bGVzICovXG5cbiAgLS1qcC1zZWFyY2gtdG9nZ2xlLW9mZi1vcGFjaXR5OiAwLjY7XG4gIC0tanAtc2VhcmNoLXRvZ2dsZS1ob3Zlci1vcGFjaXR5OiAwLjg7XG4gIC0tanAtc2VhcmNoLXRvZ2dsZS1vbi1vcGFjaXR5OiAxO1xuICAtLWpwLXNlYXJjaC1zZWxlY3RlZC1tYXRjaC1iYWNrZ3JvdW5kLWNvbG9yOiByZ2IoMjU1LCAyMjUsIDApO1xuICAtLWpwLXNlYXJjaC1zZWxlY3RlZC1tYXRjaC1jb2xvcjogYmxhY2s7XG4gIC0tanAtc2VhcmNoLXVuc2VsZWN0ZWQtbWF0Y2gtYmFja2dyb3VuZC1jb2xvcjogdmFyKFxuICAgIC0tanAtaW52ZXJzZS1sYXlvdXQtY29sb3IwXG4gICk7XG4gIC0tanAtc2VhcmNoLXVuc2VsZWN0ZWQtbWF0Y2gtY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xuXG4gIC8qIHNjcm9sbGJhciByZWxhdGVkIHN0eWxlcy4gU3VwcG9ydHMgZXZlcnkgYnJvd3NlciBleGNlcHQgRWRnZS4gKi9cblxuICAvKiBjb2xvcnMgYmFzZWQgb24gSmV0QnJhaW4ncyBEYXJjdWxhIHRoZW1lICovXG5cbiAgLS1qcC1zY3JvbGxiYXItYmFja2dyb3VuZC1jb2xvcjogIzNmNDI0NDtcbiAgLS1qcC1zY3JvbGxiYXItdGh1bWItY29sb3I6IDg4LCA5NiwgOTc7IC8qIG5lZWQgdG8gc3BlY2lmeSB0aHVtYiBjb2xvciBhcyBhbiBSR0IgdHJpcGxldCAqL1xuICAtLWpwLXNjcm9sbGJhci1lbmRwYWQ6IDNweDsgLyogdGhlIG1pbmltdW0gZ2FwIGJldHdlZW4gdGhlIHRodW1iIGFuZCB0aGUgZW5kcyBvZiBhIHNjcm9sbGJhciAqL1xuXG4gIC8qIGhhY2tzIGZvciBzZXR0aW5nIHRoZSB0aHVtYiBzaGFwZS4gVGhlc2UgZG8gbm90aGluZyBpbiBGaXJlZm94ICovXG5cbiAgLS1qcC1zY3JvbGxiYXItdGh1bWItbWFyZ2luOiAzLjVweDsgLyogdGhlIHNwYWNlIGluIGJldHdlZW4gdGhlIHNpZGVzIG9mIHRoZSB0aHVtYiBhbmQgdGhlIHRyYWNrICovXG4gIC0tanAtc2Nyb2xsYmFyLXRodW1iLXJhZGl1czogOXB4OyAvKiBzZXQgdG8gYSBsYXJnZS1pc2ggdmFsdWUgZm9yIHJvdW5kZWQgZW5kY2FwcyBvbiB0aGUgdGh1bWIgKi9cblxuICAvKiBJY29uIGNvbG9ycyB0aGF0IHdvcmsgd2VsbCB3aXRoIGxpZ2h0IG9yIGRhcmsgYmFja2dyb3VuZHMgKi9cbiAgLS1qcC1pY29uLWNvbnRyYXN0LWNvbG9yMDogdmFyKC0tbWQtcHVycGxlLTYwMCwgIzhlMjRhYSk7XG4gIC0tanAtaWNvbi1jb250cmFzdC1jb2xvcjE6IHZhcigtLW1kLWdyZWVuLTYwMCwgIzQzYTA0Nyk7XG4gIC0tanAtaWNvbi1jb250cmFzdC1jb2xvcjI6IHZhcigtLW1kLXBpbmstNjAwLCAjZDgxYjYwKTtcbiAgLS1qcC1pY29uLWNvbnRyYXN0LWNvbG9yMzogdmFyKC0tbWQtYmx1ZS02MDAsICMxZTg4ZTUpO1xuXG4gIC8qIEJ1dHRvbiBjb2xvcnMgKi9cbiAgLS1qcC1hY2NlcHQtY29sb3Itbm9ybWFsOiB2YXIoLS1tZC1ibHVlLTcwMCwgIzE5NzZkMik7XG4gIC0tanAtYWNjZXB0LWNvbG9yLWhvdmVyOiB2YXIoLS1tZC1ibHVlLTgwMCwgIzE1NjVjMCk7XG4gIC0tanAtYWNjZXB0LWNvbG9yLWFjdGl2ZTogdmFyKC0tbWQtYmx1ZS05MDAsICMwZDQ3YTEpO1xuICAtLWpwLXdhcm4tY29sb3Itbm9ybWFsOiB2YXIoLS1tZC1yZWQtNzAwLCAjZDMyZjJmKTtcbiAgLS1qcC13YXJuLWNvbG9yLWhvdmVyOiB2YXIoLS1tZC1yZWQtODAwLCAjYzYyODI4KTtcbiAgLS1qcC13YXJuLWNvbG9yLWFjdGl2ZTogdmFyKC0tbWQtcmVkLTkwMCwgI2I3MWMxYyk7XG4gIC0tanAtcmVqZWN0LWNvbG9yLW5vcm1hbDogdmFyKC0tbWQtZ3JleS02MDAsICM3NTc1NzUpO1xuICAtLWpwLXJlamVjdC1jb2xvci1ob3ZlcjogdmFyKC0tbWQtZ3JleS03MDAsICM2MTYxNjEpO1xuICAtLWpwLXJlamVjdC1jb2xvci1hY3RpdmU6IHZhcigtLW1kLWdyZXktODAwLCAjNDI0MjQyKTtcblxuICAvKiBGaWxlIG9yIGFjdGl2aXR5IGljb25zIGFuZCBzd2l0Y2ggc2VtYW50aWMgdmFyaWFibGVzICovXG4gIC0tanAtanVweXRlci1pY29uLWNvbG9yOiAjZjM3NjI2O1xuICAtLWpwLW5vdGVib29rLWljb24tY29sb3I6ICNmMzc2MjY7XG4gIC0tanAtanNvbi1pY29uLWNvbG9yOiB2YXIoLS1tZC1vcmFuZ2UtNTAwLCAjZmY5ODAwKTtcbiAgLS1qcC1jb25zb2xlLWljb24tYmFja2dyb3VuZC1jb2xvcjogdmFyKC0tbWQtYmx1ZS01MDAsICMyMTk2ZjMpO1xuICAtLWpwLWNvbnNvbGUtaWNvbi1jb2xvcjogd2hpdGU7XG4gIC0tanAtdGVybWluYWwtaWNvbi1iYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1tZC1ncmV5LTIwMCwgI2VlZSk7XG4gIC0tanAtdGVybWluYWwtaWNvbi1jb2xvcjogdmFyKC0tbWQtZ3JleS04MDAsICM0MjQyNDIpO1xuICAtLWpwLXRleHQtZWRpdG9yLWljb24tY29sb3I6IHZhcigtLW1kLWdyZXktMjAwLCAjZWVlKTtcbiAgLS1qcC1pbnNwZWN0b3ItaWNvbi1jb2xvcjogdmFyKC0tbWQtZ3JleS0yMDAsICNlZWUpO1xuICAtLWpwLXN3aXRjaC1jb2xvcjogdmFyKC0tbWQtZ3JleS00MDAsICNiZGJkYmQpO1xuICAtLWpwLXN3aXRjaC10cnVlLXBvc2l0aW9uLWNvbG9yOiB2YXIoLS1tZC1vcmFuZ2UtNzAwLCAjZjU3YzAwKTtcbn1cblxuLyogQ29tcGxldGVyIHNwZWNpZmljIHN0eWxlcyAqL1xuXG4uanAtQ29tcGxldGVyIHtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kMDogdHJhbnNwYXJlbnQ7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDE6ICMxZjc3YjQ7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDI6ICNmZjdmMGU7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDM6ICMyY2EwMmM7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDQ6ICNkNjI3Mjg7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDU6ICM5NDY3YmQ7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDY6ICM4YzU2NGI7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDc6ICNlMzc3YzI7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDg6ICM3ZjdmN2Y7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDk6ICNiY2JkMjI7XG4gIC0tanAtY29tcGxldGVyLXR5cGUtYmFja2dyb3VuZDEwOiAjMTdiZWNmO1xufVxuYCwgXCJcIl0pO1xuLy8gRXhwb3J0c1xuZXhwb3J0IGRlZmF1bHQgX19fQ1NTX0xPQURFUl9FWFBPUlRfX187XG4iLCJpbXBvcnQgYXBpIGZyb20gXCIhLi4vLi4vLi4vc3R5bGUtbG9hZGVyL2Rpc3QvcnVudGltZS9pbmplY3RTdHlsZXNJbnRvU3R5bGVUYWcuanNcIjtcbiAgICAgICAgICAgIGltcG9ydCBjb250ZW50IGZyb20gXCIhIS4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9janMuanMhLi92YXJpYWJsZXMuY3NzP3Jhd1wiO1xuXG52YXIgb3B0aW9ucyA9IHt9O1xuXG5vcHRpb25zLmluc2VydCA9IFwiaGVhZFwiO1xub3B0aW9ucy5zaW5nbGV0b24gPSBmYWxzZTtcblxudmFyIHVwZGF0ZSA9IGFwaShjb250ZW50LCBvcHRpb25zKTtcblxuXG5cbmV4cG9ydCBkZWZhdWx0IGNvbnRlbnQubG9jYWxzIHx8IHt9OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=