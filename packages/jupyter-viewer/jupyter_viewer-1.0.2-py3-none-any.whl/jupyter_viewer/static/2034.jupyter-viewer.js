"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2034],{

/***/ 10035
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

  --jp-shadow-base-lightness: 0;
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

  /* Borders
   *
   * The following variables, specify the visual styling of borders in JupyterLab.
   */

  --jp-border-width: 1px;
  --jp-border-color0: var(--md-grey-400, #bdbdbd);
  --jp-border-color1: var(--md-grey-400, #bdbdbd);
  --jp-border-color2: var(--md-grey-300, #e0e0e0);
  --jp-border-color3: var(--md-grey-200, #eee);
  --jp-inverse-border-color: var(--md-grey-600, #757575);
  --jp-border-radius: 2px;

  /* shortcut buttons
   *
   * The following css variables are used to specify the visual
   * styling of the keyboard shortcut buttons
   */
  --jp-shortcuts-button-background: var(--jp-brand-color3);
  --jp-shortcuts-button-hover-background: var(--jp-brand-color2);

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
  --jp-ui-font-color0: rgba(0, 0, 0, 1);
  --jp-ui-font-color1: rgba(0, 0, 0, 0.87);
  --jp-ui-font-color2: rgba(0, 0, 0, 0.54);
  --jp-ui-font-color3: rgba(0, 0, 0, 0.38);

  /*
   * Use these against the brand/accent/warn/error colors.
   * These will typically go from light to darker, in both a dark and light theme.
   */

  --jp-ui-inverse-font-color0: rgba(255, 255, 255, 1);
  --jp-ui-inverse-font-color1: rgba(255, 255, 255, 1);
  --jp-ui-inverse-font-color2: rgba(255, 255, 255, 0.7);
  --jp-ui-inverse-font-color3: rgba(255, 255, 255, 0.5);

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
  --jp-content-font-color0: rgba(0, 0, 0, 1);
  --jp-content-font-color1: rgba(0, 0, 0, 0.87);
  --jp-content-font-color2: rgba(0, 0, 0, 0.54);
  --jp-content-font-color3: rgba(0, 0, 0, 0.38);
  --jp-content-link-color: var(--md-blue-900, #0d47a1);
  --jp-content-link-visited-color: var(--md-purple-700, #7b1fa2);
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

  --jp-layout-color0: white;
  --jp-layout-color1: white;
  --jp-layout-color2: var(--md-grey-200, #eee);
  --jp-layout-color3: var(--md-grey-400, #bdbdbd);
  --jp-layout-color4: var(--md-grey-600, #757575);

  /* Inverse Layout
   *
   * The following are the inverse layout colors use in JupyterLab. In a light
   * theme these would go from dark to light.
   */

  --jp-inverse-layout-color0: #111;
  --jp-inverse-layout-color1: var(--md-grey-900, #212121);
  --jp-inverse-layout-color2: var(--md-grey-800, #424242);
  --jp-inverse-layout-color3: var(--md-grey-700, #616161);
  --jp-inverse-layout-color4: var(--md-grey-600, #757575);

  /* Brand/accent */

  --jp-brand-color0: var(--md-blue-900, #0d47a1);
  --jp-brand-color1: var(--md-blue-700, #1976d2);
  --jp-brand-color2: var(--md-blue-300, #64b5f6);
  --jp-brand-color3: var(--md-blue-100, #bbdefb);
  --jp-brand-color4: var(--md-blue-50, #e3f2fd);
  --jp-accent-color0: var(--md-green-900, #1b5e20);
  --jp-accent-color1: var(--md-green-700, #388e3c);
  --jp-accent-color2: var(--md-green-300, #81c784);
  --jp-accent-color3: var(--md-green-100, #c8e6c9);

  /* State colors (warn, error, success, info) */

  --jp-warn-color0: var(--md-orange-900, #e65100);
  --jp-warn-color1: var(--md-orange-700, #f57c00);
  --jp-warn-color2: var(--md-orange-300, #ffb74d);
  --jp-warn-color3: var(--md-orange-100, #ffe0b2);
  --jp-error-color0: var(--md-red-900, #b71c1c);
  --jp-error-color1: var(--md-red-700, #d32f2f);
  --jp-error-color2: var(--md-red-300, #e57373);
  --jp-error-color3: var(--md-red-100, #ffcdd2);
  --jp-success-color0: var(--md-green-900, #1b5e20);
  --jp-success-color1: var(--md-green-700, #388e3c);
  --jp-success-color2: var(--md-green-300, #81c784);
  --jp-success-color3: var(--md-green-100, #c8e6c9);
  --jp-info-color0: var(--md-cyan-900, #006064);
  --jp-info-color1: var(--md-cyan-700, #0097a7);
  --jp-info-color2: var(--md-cyan-300, #4dd0e1);
  --jp-info-color3: var(--md-cyan-100, #b2ebf2);

  /* Cell specific styles */

  --jp-cell-padding: 5px;
  --jp-cell-collapser-width: 8px;
  --jp-cell-collapser-min-height: 20px;
  --jp-cell-collapser-not-active-hover-opacity: 0.6;
  --jp-cell-editor-background: var(--md-grey-100, #f5f5f5);
  --jp-cell-editor-border-color: var(--md-grey-300, #e0e0e0);
  --jp-cell-editor-box-shadow: inset 0 0 2px var(--md-blue-300, #64b5f6);
  --jp-cell-editor-active-background: var(--jp-layout-color0);
  --jp-cell-editor-active-border-color: var(--jp-brand-color1);
  --jp-cell-prompt-width: 64px;
  --jp-cell-prompt-font-family: var(--jp-code-font-family-default);
  --jp-cell-prompt-letter-spacing: 0;
  --jp-cell-prompt-opacity: 1;
  --jp-cell-prompt-not-active-opacity: 0.5;
  --jp-cell-prompt-not-active-font-color: var(--md-grey-700, #616161);

  /* A custom blend of MD grey and blue 600
   * See https://meyerweb.com/eric/tools/color-blend/#546E7A:1E88E5:5:hex */
  --jp-cell-inprompt-font-color: #307fc1;

  /* A custom blend of MD grey and orange 600
   * https://meyerweb.com/eric/tools/color-blend/#546E7A:F4511E:5:hex */
  --jp-cell-outprompt-font-color: #bf5b3d;

  /* Notebook specific styles */

  --jp-notebook-padding: 10px;
  --jp-notebook-select-background: var(--jp-layout-color1);
  --jp-notebook-multiselected-color: var(--md-blue-50, #e3f2fd);

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

  --jp-rendermime-error-background: #fdd;
  --jp-rendermime-table-row-background: var(--md-grey-100, #cfd8dc);
  --jp-rendermime-table-row-hover-background: var(--md-light-blue-50, #e1f5fe);

  /* Dialog specific styles */

  --jp-dialog-background: rgba(0, 0, 0, 0.25);

  /* Console specific styles */

  --jp-console-padding: 10px;

  /* Toolbar specific styles */

  --jp-toolbar-border-color: var(--jp-border-color1);
  --jp-toolbar-micro-height: 8px;
  --jp-toolbar-background: var(--jp-layout-color1);
  --jp-toolbar-box-shadow: 0 0 2px 0 rgba(0, 0, 0, 0.24);
  --jp-toolbar-header-margin: 4px 4px 0 4px;
  --jp-toolbar-active-background: var(--md-grey-300, #90a4ae);

  /* Statusbar specific styles */

  --jp-statusbar-height: 24px;

  /* Input field styles */

  --jp-input-box-shadow: inset 0 0 2px var(--md-blue-300, #64b5f6);
  --jp-input-active-background: var(--jp-layout-color1);
  --jp-input-hover-background: var(--jp-layout-color1);
  --jp-input-background: var(--md-grey-100, #f5f5f5);
  --jp-input-border-color: var(--jp-inverse-border-color);
  --jp-input-active-border-color: var(--jp-brand-color1);
  --jp-input-active-box-shadow-color: rgba(19, 124, 189, 0.3);

  /* General editor styles */

  --jp-editor-selected-background: #d9d9d9;
  --jp-editor-selected-focused-background: #d7d4f0;
  --jp-editor-cursor-color: var(--jp-ui-font-color0);

  /* Code mirror specific styles */

  --jp-mirror-editor-keyword-color: #008000;
  --jp-mirror-editor-atom-color: #88f;
  --jp-mirror-editor-number-color: #080;
  --jp-mirror-editor-def-color: #00f;
  --jp-mirror-editor-variable-color: var(--md-grey-900, #212121);
  --jp-mirror-editor-variable-2-color: rgb(0, 54, 109);
  --jp-mirror-editor-variable-3-color: #085;
  --jp-mirror-editor-punctuation-color: #05a;
  --jp-mirror-editor-property-color: #05a;
  --jp-mirror-editor-operator-color: #7800c2;
  --jp-mirror-editor-comment-color: #408080;
  --jp-mirror-editor-string-color: #ba2121;
  --jp-mirror-editor-string-2-color: #708;
  --jp-mirror-editor-meta-color: #a2f;
  --jp-mirror-editor-qualifier-color: #555;
  --jp-mirror-editor-builtin-color: #008000;
  --jp-mirror-editor-bracket-color: #997;
  --jp-mirror-editor-tag-color: #170;
  --jp-mirror-editor-attribute-color: #00c;
  --jp-mirror-editor-header-color: blue;
  --jp-mirror-editor-quote-color: #090;
  --jp-mirror-editor-link-color: #00c;
  --jp-mirror-editor-error-color: #f00;
  --jp-mirror-editor-hr-color: #999;

  /*
    RTC user specific colors.
    These colors are used for the cursor, username in the editor,
    and the icon of the user.
  */

  --jp-collaborator-color1: #ffad8e;
  --jp-collaborator-color2: #dac83d;
  --jp-collaborator-color3: #72dd76;
  --jp-collaborator-color4: #00e4d0;
  --jp-collaborator-color5: #45d4ff;
  --jp-collaborator-color6: #e2b1ff;
  --jp-collaborator-color7: #ff9de6;

  /* Vega extension styles */

  --jp-vega-background: white;

  /* Sidebar-related styles */

  --jp-sidebar-min-width: 250px;

  /* Search-related styles */

  --jp-search-toggle-off-opacity: 0.5;
  --jp-search-toggle-hover-opacity: 0.8;
  --jp-search-toggle-on-opacity: 1;
  --jp-search-selected-match-background-color: rgb(245, 200, 0);
  --jp-search-selected-match-color: black;
  --jp-search-unselected-match-background-color: var(
    --jp-inverse-layout-color0
  );
  --jp-search-unselected-match-color: var(--jp-ui-inverse-font-color0);

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
  --jp-json-icon-color: var(--md-orange-700, #f57c00);
  --jp-console-icon-background-color: var(--md-blue-700, #1976d2);
  --jp-console-icon-color: white;
  --jp-terminal-icon-background-color: var(--md-grey-800, #424242);
  --jp-terminal-icon-color: var(--md-grey-200, #eee);
  --jp-text-editor-icon-color: var(--md-grey-700, #616161);
  --jp-inspector-icon-color: var(--md-grey-700, #616161);
  --jp-switch-color: var(--md-grey-400, #bdbdbd);
  --jp-switch-true-position-color: var(--md-orange-900, #e65100);
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

/***/ 92034
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(85072);
/* harmony import */ var _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _css_loader_dist_cjs_js_variables_css_raw__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(10035);

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_css_loader_dist_cjs_js_variables_css_raw__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .A, options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_css_loader_dist_cjs_js_variables_css_raw__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .A.locals || {});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjAzNC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7Ozs7Ozs7Ozs7O0FDbGRBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AanVweXRlcmxhYi90aGVtZS1saWdodC1leHRlbnNpb24vc3R5bGUvdmFyaWFibGVzLmNzcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0BqdXB5dGVybGFiL3RoZW1lLWxpZ2h0LWV4dGVuc2lvbi9zdHlsZS92YXJpYWJsZXMuY3NzP2I0ZjMiXSwic291cmNlc0NvbnRlbnQiOlsiLy8gSW1wb3J0c1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX05PX1NPVVJDRU1BUF9JTVBPUlRfX18gZnJvbSBcIi4uLy4uLy4uL2Nzcy1sb2FkZXIvZGlzdC9ydW50aW1lL25vU291cmNlTWFwcy5qc1wiO1xuaW1wb3J0IF9fX0NTU19MT0FERVJfQVBJX0lNUE9SVF9fXyBmcm9tIFwiLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L3J1bnRpbWUvYXBpLmpzXCI7XG52YXIgX19fQ1NTX0xPQURFUl9FWFBPUlRfX18gPSBfX19DU1NfTE9BREVSX0FQSV9JTVBPUlRfX18oX19fQ1NTX0xPQURFUl9BUElfTk9fU09VUkNFTUFQX0lNUE9SVF9fXyk7XG4vLyBNb2R1bGVcbl9fX0NTU19MT0FERVJfRVhQT1JUX19fLnB1c2goW21vZHVsZS5pZCwgYC8qLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS1cbnwgQ29weXJpZ2h0IChjKSBKdXB5dGVyIERldmVsb3BtZW50IFRlYW0uXG58IERpc3RyaWJ1dGVkIHVuZGVyIHRoZSB0ZXJtcyBvZiB0aGUgTW9kaWZpZWQgQlNEIExpY2Vuc2UuXG58LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSovXG5cbi8qXG5UaGUgZm9sbG93aW5nIENTUyB2YXJpYWJsZXMgZGVmaW5lIHRoZSBtYWluLCBwdWJsaWMgQVBJIGZvciBzdHlsaW5nIEp1cHl0ZXJMYWIuXG5UaGVzZSB2YXJpYWJsZXMgc2hvdWxkIGJlIHVzZWQgYnkgYWxsIHBsdWdpbnMgd2hlcmV2ZXIgcG9zc2libGUuIEluIG90aGVyXG53b3JkcywgcGx1Z2lucyBzaG91bGQgbm90IGRlZmluZSBjdXN0b20gY29sb3JzLCBzaXplcywgZXRjIHVubGVzcyBhYnNvbHV0ZWx5XG5uZWNlc3NhcnkuIFRoaXMgZW5hYmxlcyB1c2VycyB0byBjaGFuZ2UgdGhlIHZpc3VhbCB0aGVtZSBvZiBKdXB5dGVyTGFiXG5ieSBjaGFuZ2luZyB0aGVzZSB2YXJpYWJsZXMuXG5cbk1hbnkgdmFyaWFibGVzIGFwcGVhciBpbiBhbiBvcmRlcmVkIHNlcXVlbmNlICgwLDEsMiwzKS4gVGhlc2Ugc2VxdWVuY2VzXG5hcmUgZGVzaWduZWQgdG8gd29yayB3ZWxsIHRvZ2V0aGVyLCBzbyBmb3IgZXhhbXBsZSwgXFxgLS1qcC1ib3JkZXItY29sb3IxXFxgIHNob3VsZFxuYmUgdXNlZCB3aXRoIFxcYC0tanAtbGF5b3V0LWNvbG9yMVxcYC4gVGhlIG51bWJlcnMgaGF2ZSB0aGUgZm9sbG93aW5nIG1lYW5pbmdzOlxuXG4qIDA6IHN1cGVyLXByaW1hcnksIHJlc2VydmVkIGZvciBzcGVjaWFsIGVtcGhhc2lzXG4qIDE6IHByaW1hcnksIG1vc3QgaW1wb3J0YW50IHVuZGVyIG5vcm1hbCBzaXR1YXRpb25zXG4qIDI6IHNlY29uZGFyeSwgbmV4dCBtb3N0IGltcG9ydGFudCB1bmRlciBub3JtYWwgc2l0dWF0aW9uc1xuKiAzOiB0ZXJ0aWFyeSwgbmV4dCBtb3N0IGltcG9ydGFudCB1bmRlciBub3JtYWwgc2l0dWF0aW9uc1xuXG5UaHJvdWdob3V0IEp1cHl0ZXJMYWIsIHdlIGFyZSBtb3N0bHkgZm9sbG93aW5nIHByaW5jaXBsZXMgZnJvbSBHb29nbGUnc1xuTWF0ZXJpYWwgRGVzaWduIHdoZW4gc2VsZWN0aW5nIGNvbG9ycy4gV2UgYXJlIG5vdCwgaG93ZXZlciwgZm9sbG93aW5nXG5hbGwgb2YgTUQgYXMgaXQgaXMgbm90IG9wdGltaXplZCBmb3IgZGVuc2UsIGluZm9ybWF0aW9uIHJpY2ggVUlzLlxuKi9cblxuOnJvb3Qge1xuICAvKiBFbGV2YXRpb25cbiAgICpcbiAgICogV2Ugc3R5bGUgYm94LXNoYWRvd3MgdXNpbmcgTWF0ZXJpYWwgRGVzaWduJ3MgaWRlYSBvZiBlbGV2YXRpb24uIFRoZXNlIHBhcnRpY3VsYXIgbnVtYmVycyBhcmUgdGFrZW4gZnJvbSBoZXJlOlxuICAgKlxuICAgKiBodHRwczovL2dpdGh1Yi5jb20vbWF0ZXJpYWwtY29tcG9uZW50cy9tYXRlcmlhbC1jb21wb25lbnRzLXdlYlxuICAgKiBodHRwczovL21hdGVyaWFsLWNvbXBvbmVudHMtd2ViLmFwcHNwb3QuY29tL2VsZXZhdGlvbi5odG1sXG4gICAqL1xuXG4gIC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzOiAwO1xuICAtLWpwLXNoYWRvdy11bWJyYS1jb2xvcjogcmdiYShcbiAgICB2YXIoLS1qcC1zaGFkb3ctYmFzZS1saWdodG5lc3MpLFxuICAgIHZhcigtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzcyksXG4gICAgdmFyKC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzKSxcbiAgICAwLjJcbiAgKTtcbiAgLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3I6IHJnYmEoXG4gICAgdmFyKC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzKSxcbiAgICB2YXIoLS1qcC1zaGFkb3ctYmFzZS1saWdodG5lc3MpLFxuICAgIHZhcigtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzcyksXG4gICAgMC4xNFxuICApO1xuICAtLWpwLXNoYWRvdy1hbWJpZW50LWNvbG9yOiByZ2JhKFxuICAgIHZhcigtLWpwLXNoYWRvdy1iYXNlLWxpZ2h0bmVzcyksXG4gICAgdmFyKC0tanAtc2hhZG93LWJhc2UtbGlnaHRuZXNzKSxcbiAgICB2YXIoLS1qcC1zaGFkb3ctYmFzZS1saWdodG5lc3MpLFxuICAgIDAuMTJcbiAgKTtcbiAgLS1qcC1lbGV2YXRpb24tejA6IG5vbmU7XG4gIC0tanAtZWxldmF0aW9uLXoxOiAwIDJweCAxcHggLTFweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgMXB4IDFweCAwIHZhcigtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvciksXG4gICAgMCAxcHggM3B4IDAgdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16MjogMCAzcHggMXB4IC0ycHggdmFyKC0tanAtc2hhZG93LXVtYnJhLWNvbG9yKSxcbiAgICAwIDJweCAycHggMCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgMXB4IDVweCAwIHZhcigtLWpwLXNoYWRvdy1hbWJpZW50LWNvbG9yKTtcbiAgLS1qcC1lbGV2YXRpb24tejQ6IDAgMnB4IDRweCAtMXB4IHZhcigtLWpwLXNoYWRvdy11bWJyYS1jb2xvciksXG4gICAgMCA0cHggNXB4IDAgdmFyKC0tanAtc2hhZG93LXBlbnVtYnJhLWNvbG9yKSxcbiAgICAwIDFweCAxMHB4IDAgdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16NjogMCAzcHggNXB4IC0xcHggdmFyKC0tanAtc2hhZG93LXVtYnJhLWNvbG9yKSxcbiAgICAwIDZweCAxMHB4IDAgdmFyKC0tanAtc2hhZG93LXBlbnVtYnJhLWNvbG9yKSxcbiAgICAwIDFweCAxOHB4IDAgdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuICAtLWpwLWVsZXZhdGlvbi16ODogMCA1cHggNXB4IC0zcHggdmFyKC0tanAtc2hhZG93LXVtYnJhLWNvbG9yKSxcbiAgICAwIDhweCAxMHB4IDFweCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgM3B4IDE0cHggMnB4IHZhcigtLWpwLXNoYWRvdy1hbWJpZW50LWNvbG9yKTtcbiAgLS1qcC1lbGV2YXRpb24tejEyOiAwIDdweCA4cHggLTRweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgMTJweCAxN3B4IDJweCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgNXB4IDIycHggNHB4IHZhcigtLWpwLXNoYWRvdy1hbWJpZW50LWNvbG9yKTtcbiAgLS1qcC1lbGV2YXRpb24tejE2OiAwIDhweCAxMHB4IC01cHggdmFyKC0tanAtc2hhZG93LXVtYnJhLWNvbG9yKSxcbiAgICAwIDE2cHggMjRweCAycHggdmFyKC0tanAtc2hhZG93LXBlbnVtYnJhLWNvbG9yKSxcbiAgICAwIDZweCAzMHB4IDVweCB2YXIoLS1qcC1zaGFkb3ctYW1iaWVudC1jb2xvcik7XG4gIC0tanAtZWxldmF0aW9uLXoyMDogMCAxMHB4IDEzcHggLTZweCB2YXIoLS1qcC1zaGFkb3ctdW1icmEtY29sb3IpLFxuICAgIDAgMjBweCAzMXB4IDNweCB2YXIoLS1qcC1zaGFkb3ctcGVudW1icmEtY29sb3IpLFxuICAgIDAgOHB4IDM4cHggN3B4IHZhcigtLWpwLXNoYWRvdy1hbWJpZW50LWNvbG9yKTtcbiAgLS1qcC1lbGV2YXRpb24tejI0OiAwIDExcHggMTVweCAtN3B4IHZhcigtLWpwLXNoYWRvdy11bWJyYS1jb2xvciksXG4gICAgMCAyNHB4IDM4cHggM3B4IHZhcigtLWpwLXNoYWRvdy1wZW51bWJyYS1jb2xvciksXG4gICAgMCA5cHggNDZweCA4cHggdmFyKC0tanAtc2hhZG93LWFtYmllbnQtY29sb3IpO1xuXG4gIC8qIEJvcmRlcnNcbiAgICpcbiAgICogVGhlIGZvbGxvd2luZyB2YXJpYWJsZXMsIHNwZWNpZnkgdGhlIHZpc3VhbCBzdHlsaW5nIG9mIGJvcmRlcnMgaW4gSnVweXRlckxhYi5cbiAgICovXG5cbiAgLS1qcC1ib3JkZXItd2lkdGg6IDFweDtcbiAgLS1qcC1ib3JkZXItY29sb3IwOiB2YXIoLS1tZC1ncmV5LTQwMCwgI2JkYmRiZCk7XG4gIC0tanAtYm9yZGVyLWNvbG9yMTogdmFyKC0tbWQtZ3JleS00MDAsICNiZGJkYmQpO1xuICAtLWpwLWJvcmRlci1jb2xvcjI6IHZhcigtLW1kLWdyZXktMzAwLCAjZTBlMGUwKTtcbiAgLS1qcC1ib3JkZXItY29sb3IzOiB2YXIoLS1tZC1ncmV5LTIwMCwgI2VlZSk7XG4gIC0tanAtaW52ZXJzZS1ib3JkZXItY29sb3I6IHZhcigtLW1kLWdyZXktNjAwLCAjNzU3NTc1KTtcbiAgLS1qcC1ib3JkZXItcmFkaXVzOiAycHg7XG5cbiAgLyogc2hvcnRjdXQgYnV0dG9uc1xuICAgKlxuICAgKiBUaGUgZm9sbG93aW5nIGNzcyB2YXJpYWJsZXMgYXJlIHVzZWQgdG8gc3BlY2lmeSB0aGUgdmlzdWFsXG4gICAqIHN0eWxpbmcgb2YgdGhlIGtleWJvYXJkIHNob3J0Y3V0IGJ1dHRvbnNcbiAgICovXG4gIC0tanAtc2hvcnRjdXRzLWJ1dHRvbi1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1icmFuZC1jb2xvcjMpO1xuICAtLWpwLXNob3J0Y3V0cy1idXR0b24taG92ZXItYmFja2dyb3VuZDogdmFyKC0tanAtYnJhbmQtY29sb3IyKTtcblxuICAvKiBVSSBGb250c1xuICAgKlxuICAgKiBUaGUgVUkgZm9udCBDU1MgdmFyaWFibGVzIGFyZSB1c2VkIGZvciB0aGUgdHlwb2dyYXBoeSBhbGwgb2YgdGhlIEp1cHl0ZXJMYWJcbiAgICogdXNlciBpbnRlcmZhY2UgZWxlbWVudHMgdGhhdCBhcmUgbm90IGRpcmVjdGx5IHVzZXIgZ2VuZXJhdGVkIGNvbnRlbnQuXG4gICAqXG4gICAqIFRoZSBmb250IHNpemluZyBoZXJlIGlzIGRvbmUgYXNzdW1pbmcgdGhhdCB0aGUgYm9keSBmb250IHNpemUgb2YgLS1qcC11aS1mb250LXNpemUxXG4gICAqIGlzIGFwcGxpZWQgdG8gYSBwYXJlbnQgZWxlbWVudC4gV2hlbiBjaGlsZHJlbiBlbGVtZW50cywgc3VjaCBhcyBoZWFkaW5ncywgYXJlIHNpemVkXG4gICAqIGluIGVtIGFsbCB0aGluZ3Mgd2lsbCBiZSBjb21wdXRlZCByZWxhdGl2ZSB0byB0aGF0IGJvZHkgc2l6ZS5cbiAgICovXG5cbiAgLS1qcC11aS1mb250LXNjYWxlLWZhY3RvcjogMS4yO1xuICAtLWpwLXVpLWZvbnQtc2l6ZTA6IDAuODMzMzNlbTtcbiAgLS1qcC11aS1mb250LXNpemUxOiAxM3B4OyAvKiBCYXNlIGZvbnQgc2l6ZSAqL1xuICAtLWpwLXVpLWZvbnQtc2l6ZTI6IDEuMmVtO1xuICAtLWpwLXVpLWZvbnQtc2l6ZTM6IDEuNDRlbTtcbiAgLS1qcC11aS1mb250LWZhbWlseTogc3lzdGVtLXVpLCAtYXBwbGUtc3lzdGVtLCBibGlua21hY3N5c3RlbWZvbnQsICdTZWdvZSBVSScsXG4gICAgaGVsdmV0aWNhLCBhcmlhbCwgc2Fucy1zZXJpZiwgJ0FwcGxlIENvbG9yIEVtb2ppJywgJ1NlZ29lIFVJIEVtb2ppJyxcbiAgICAnU2Vnb2UgVUkgU3ltYm9sJztcblxuICAvKlxuICAgKiBVc2UgdGhlc2UgZm9udCBjb2xvcnMgYWdhaW5zdCB0aGUgY29ycmVzcG9uZGluZyBtYWluIGxheW91dCBjb2xvcnMuXG4gICAqIEluIGEgbGlnaHQgdGhlbWUsIHRoZXNlIGdvIGZyb20gZGFyayB0byBsaWdodC5cbiAgICovXG5cbiAgLyogRGVmYXVsdHMgdXNlIE1hdGVyaWFsIERlc2lnbiBzcGVjaWZpY2F0aW9uICovXG4gIC0tanAtdWktZm9udC1jb2xvcjA6IHJnYmEoMCwgMCwgMCwgMSk7XG4gIC0tanAtdWktZm9udC1jb2xvcjE6IHJnYmEoMCwgMCwgMCwgMC44Nyk7XG4gIC0tanAtdWktZm9udC1jb2xvcjI6IHJnYmEoMCwgMCwgMCwgMC41NCk7XG4gIC0tanAtdWktZm9udC1jb2xvcjM6IHJnYmEoMCwgMCwgMCwgMC4zOCk7XG5cbiAgLypcbiAgICogVXNlIHRoZXNlIGFnYWluc3QgdGhlIGJyYW5kL2FjY2VudC93YXJuL2Vycm9yIGNvbG9ycy5cbiAgICogVGhlc2Ugd2lsbCB0eXBpY2FsbHkgZ28gZnJvbSBsaWdodCB0byBkYXJrZXIsIGluIGJvdGggYSBkYXJrIGFuZCBsaWdodCB0aGVtZS5cbiAgICovXG5cbiAgLS1qcC11aS1pbnZlcnNlLWZvbnQtY29sb3IwOiByZ2JhKDI1NSwgMjU1LCAyNTUsIDEpO1xuICAtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjE6IHJnYmEoMjU1LCAyNTUsIDI1NSwgMSk7XG4gIC0tanAtdWktaW52ZXJzZS1mb250LWNvbG9yMjogcmdiYSgyNTUsIDI1NSwgMjU1LCAwLjcpO1xuICAtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjM6IHJnYmEoMjU1LCAyNTUsIDI1NSwgMC41KTtcblxuICAvKiBDb250ZW50IEZvbnRzXG4gICAqXG4gICAqIENvbnRlbnQgZm9udCB2YXJpYWJsZXMgYXJlIHVzZWQgZm9yIHR5cG9ncmFwaHkgb2YgdXNlciBnZW5lcmF0ZWQgY29udGVudC5cbiAgICpcbiAgICogVGhlIGZvbnQgc2l6aW5nIGhlcmUgaXMgZG9uZSBhc3N1bWluZyB0aGF0IHRoZSBib2R5IGZvbnQgc2l6ZSBvZiAtLWpwLWNvbnRlbnQtZm9udC1zaXplMVxuICAgKiBpcyBhcHBsaWVkIHRvIGEgcGFyZW50IGVsZW1lbnQuIFdoZW4gY2hpbGRyZW4gZWxlbWVudHMsIHN1Y2ggYXMgaGVhZGluZ3MsIGFyZSBzaXplZFxuICAgKiBpbiBlbSBhbGwgdGhpbmdzIHdpbGwgYmUgY29tcHV0ZWQgcmVsYXRpdmUgdG8gdGhhdCBib2R5IHNpemUuXG4gICAqL1xuXG4gIC0tanAtY29udGVudC1saW5lLWhlaWdodDogMS42O1xuICAtLWpwLWNvbnRlbnQtZm9udC1zY2FsZS1mYWN0b3I6IDEuMjtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTA6IDAuODMzMzNlbTtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTE6IDE0cHg7IC8qIEJhc2UgZm9udCBzaXplICovXG4gIC0tanAtY29udGVudC1mb250LXNpemUyOiAxLjJlbTtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTM6IDEuNDRlbTtcbiAgLS1qcC1jb250ZW50LWZvbnQtc2l6ZTQ6IDEuNzI4ZW07XG4gIC0tanAtY29udGVudC1mb250LXNpemU1OiAyLjA3MzZlbTtcblxuICAvKiBUaGlzIGdpdmVzIGEgbWFnbmlmaWNhdGlvbiBvZiBhYm91dCAxMjUlIGluIHByZXNlbnRhdGlvbiBtb2RlIG92ZXIgbm9ybWFsLiAqL1xuICAtLWpwLWNvbnRlbnQtcHJlc2VudGF0aW9uLWZvbnQtc2l6ZTE6IDE3cHg7XG4gIC0tanAtY29udGVudC1oZWFkaW5nLWxpbmUtaGVpZ2h0OiAxO1xuICAtLWpwLWNvbnRlbnQtaGVhZGluZy1tYXJnaW4tdG9wOiAxLjJlbTtcbiAgLS1qcC1jb250ZW50LWhlYWRpbmctbWFyZ2luLWJvdHRvbTogMC44ZW07XG4gIC0tanAtY29udGVudC1oZWFkaW5nLWZvbnQtd2VpZ2h0OiA1MDA7XG5cbiAgLyogRGVmYXVsdHMgdXNlIE1hdGVyaWFsIERlc2lnbiBzcGVjaWZpY2F0aW9uICovXG4gIC0tanAtY29udGVudC1mb250LWNvbG9yMDogcmdiYSgwLCAwLCAwLCAxKTtcbiAgLS1qcC1jb250ZW50LWZvbnQtY29sb3IxOiByZ2JhKDAsIDAsIDAsIDAuODcpO1xuICAtLWpwLWNvbnRlbnQtZm9udC1jb2xvcjI6IHJnYmEoMCwgMCwgMCwgMC41NCk7XG4gIC0tanAtY29udGVudC1mb250LWNvbG9yMzogcmdiYSgwLCAwLCAwLCAwLjM4KTtcbiAgLS1qcC1jb250ZW50LWxpbmstY29sb3I6IHZhcigtLW1kLWJsdWUtOTAwLCAjMGQ0N2ExKTtcbiAgLS1qcC1jb250ZW50LWxpbmstdmlzaXRlZC1jb2xvcjogdmFyKC0tbWQtcHVycGxlLTcwMCwgIzdiMWZhMik7XG4gIC0tanAtY29udGVudC1mb250LWZhbWlseTogc3lzdGVtLXVpLCAtYXBwbGUtc3lzdGVtLCBibGlua21hY3N5c3RlbWZvbnQsXG4gICAgJ1NlZ29lIFVJJywgaGVsdmV0aWNhLCBhcmlhbCwgc2Fucy1zZXJpZiwgJ0FwcGxlIENvbG9yIEVtb2ppJyxcbiAgICAnU2Vnb2UgVUkgRW1vamknLCAnU2Vnb2UgVUkgU3ltYm9sJztcblxuICAvKlxuICAgKiBDb2RlIEZvbnRzXG4gICAqXG4gICAqIENvZGUgZm9udCB2YXJpYWJsZXMgYXJlIHVzZWQgZm9yIHR5cG9ncmFwaHkgb2YgY29kZSBhbmQgb3RoZXIgbW9ub3NwYWNlcyBjb250ZW50LlxuICAgKi9cblxuICAtLWpwLWNvZGUtZm9udC1zaXplOiAxM3B4O1xuICAtLWpwLWNvZGUtbGluZS1oZWlnaHQ6IDEuMzA3NzsgLyogMTdweCBmb3IgMTNweCBiYXNlICovXG4gIC0tanAtY29kZS1wYWRkaW5nOiA1cHg7IC8qIDVweCBmb3IgMTNweCBiYXNlLCBjb2RlbWlycm9yIGhpZ2hsaWdodGluZyBuZWVkcyBpbnRlZ2VyIHB4IHZhbHVlICovXG4gIC0tanAtY29kZS1mb250LWZhbWlseS1kZWZhdWx0OiBtZW5sbywgY29uc29sYXMsICdEZWphVnUgU2FucyBNb25vJywgbW9ub3NwYWNlO1xuICAtLWpwLWNvZGUtZm9udC1mYW1pbHk6IHZhcigtLWpwLWNvZGUtZm9udC1mYW1pbHktZGVmYXVsdCk7XG5cbiAgLyogVGhpcyBnaXZlcyBhIG1hZ25pZmljYXRpb24gb2YgYWJvdXQgMTI1JSBpbiBwcmVzZW50YXRpb24gbW9kZSBvdmVyIG5vcm1hbC4gKi9cbiAgLS1qcC1jb2RlLXByZXNlbnRhdGlvbi1mb250LXNpemU6IDE2cHg7XG5cbiAgLyogbWF5IG5lZWQgdG8gdHdlYWsgY3Vyc29yIHdpZHRoIGlmIHlvdSBjaGFuZ2UgZm9udCBzaXplICovXG4gIC0tanAtY29kZS1jdXJzb3Itd2lkdGgwOiAxLjRweDtcbiAgLS1qcC1jb2RlLWN1cnNvci13aWR0aDE6IDJweDtcbiAgLS1qcC1jb2RlLWN1cnNvci13aWR0aDI6IDRweDtcblxuICAvKiBMYXlvdXRcbiAgICpcbiAgICogVGhlIGZvbGxvd2luZyBhcmUgdGhlIG1haW4gbGF5b3V0IGNvbG9ycyB1c2UgaW4gSnVweXRlckxhYi4gSW4gYSBsaWdodFxuICAgKiB0aGVtZSB0aGVzZSB3b3VsZCBnbyBmcm9tIGxpZ2h0IHRvIGRhcmsuXG4gICAqL1xuXG4gIC0tanAtbGF5b3V0LWNvbG9yMDogd2hpdGU7XG4gIC0tanAtbGF5b3V0LWNvbG9yMTogd2hpdGU7XG4gIC0tanAtbGF5b3V0LWNvbG9yMjogdmFyKC0tbWQtZ3JleS0yMDAsICNlZWUpO1xuICAtLWpwLWxheW91dC1jb2xvcjM6IHZhcigtLW1kLWdyZXktNDAwLCAjYmRiZGJkKTtcbiAgLS1qcC1sYXlvdXQtY29sb3I0OiB2YXIoLS1tZC1ncmV5LTYwMCwgIzc1NzU3NSk7XG5cbiAgLyogSW52ZXJzZSBMYXlvdXRcbiAgICpcbiAgICogVGhlIGZvbGxvd2luZyBhcmUgdGhlIGludmVyc2UgbGF5b3V0IGNvbG9ycyB1c2UgaW4gSnVweXRlckxhYi4gSW4gYSBsaWdodFxuICAgKiB0aGVtZSB0aGVzZSB3b3VsZCBnbyBmcm9tIGRhcmsgdG8gbGlnaHQuXG4gICAqL1xuXG4gIC0tanAtaW52ZXJzZS1sYXlvdXQtY29sb3IwOiAjMTExO1xuICAtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yMTogdmFyKC0tbWQtZ3JleS05MDAsICMyMTIxMjEpO1xuICAtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yMjogdmFyKC0tbWQtZ3JleS04MDAsICM0MjQyNDIpO1xuICAtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yMzogdmFyKC0tbWQtZ3JleS03MDAsICM2MTYxNjEpO1xuICAtLWpwLWludmVyc2UtbGF5b3V0LWNvbG9yNDogdmFyKC0tbWQtZ3JleS02MDAsICM3NTc1NzUpO1xuXG4gIC8qIEJyYW5kL2FjY2VudCAqL1xuXG4gIC0tanAtYnJhbmQtY29sb3IwOiB2YXIoLS1tZC1ibHVlLTkwMCwgIzBkNDdhMSk7XG4gIC0tanAtYnJhbmQtY29sb3IxOiB2YXIoLS1tZC1ibHVlLTcwMCwgIzE5NzZkMik7XG4gIC0tanAtYnJhbmQtY29sb3IyOiB2YXIoLS1tZC1ibHVlLTMwMCwgIzY0YjVmNik7XG4gIC0tanAtYnJhbmQtY29sb3IzOiB2YXIoLS1tZC1ibHVlLTEwMCwgI2JiZGVmYik7XG4gIC0tanAtYnJhbmQtY29sb3I0OiB2YXIoLS1tZC1ibHVlLTUwLCAjZTNmMmZkKTtcbiAgLS1qcC1hY2NlbnQtY29sb3IwOiB2YXIoLS1tZC1ncmVlbi05MDAsICMxYjVlMjApO1xuICAtLWpwLWFjY2VudC1jb2xvcjE6IHZhcigtLW1kLWdyZWVuLTcwMCwgIzM4OGUzYyk7XG4gIC0tanAtYWNjZW50LWNvbG9yMjogdmFyKC0tbWQtZ3JlZW4tMzAwLCAjODFjNzg0KTtcbiAgLS1qcC1hY2NlbnQtY29sb3IzOiB2YXIoLS1tZC1ncmVlbi0xMDAsICNjOGU2YzkpO1xuXG4gIC8qIFN0YXRlIGNvbG9ycyAod2FybiwgZXJyb3IsIHN1Y2Nlc3MsIGluZm8pICovXG5cbiAgLS1qcC13YXJuLWNvbG9yMDogdmFyKC0tbWQtb3JhbmdlLTkwMCwgI2U2NTEwMCk7XG4gIC0tanAtd2Fybi1jb2xvcjE6IHZhcigtLW1kLW9yYW5nZS03MDAsICNmNTdjMDApO1xuICAtLWpwLXdhcm4tY29sb3IyOiB2YXIoLS1tZC1vcmFuZ2UtMzAwLCAjZmZiNzRkKTtcbiAgLS1qcC13YXJuLWNvbG9yMzogdmFyKC0tbWQtb3JhbmdlLTEwMCwgI2ZmZTBiMik7XG4gIC0tanAtZXJyb3ItY29sb3IwOiB2YXIoLS1tZC1yZWQtOTAwLCAjYjcxYzFjKTtcbiAgLS1qcC1lcnJvci1jb2xvcjE6IHZhcigtLW1kLXJlZC03MDAsICNkMzJmMmYpO1xuICAtLWpwLWVycm9yLWNvbG9yMjogdmFyKC0tbWQtcmVkLTMwMCwgI2U1NzM3Myk7XG4gIC0tanAtZXJyb3ItY29sb3IzOiB2YXIoLS1tZC1yZWQtMTAwLCAjZmZjZGQyKTtcbiAgLS1qcC1zdWNjZXNzLWNvbG9yMDogdmFyKC0tbWQtZ3JlZW4tOTAwLCAjMWI1ZTIwKTtcbiAgLS1qcC1zdWNjZXNzLWNvbG9yMTogdmFyKC0tbWQtZ3JlZW4tNzAwLCAjMzg4ZTNjKTtcbiAgLS1qcC1zdWNjZXNzLWNvbG9yMjogdmFyKC0tbWQtZ3JlZW4tMzAwLCAjODFjNzg0KTtcbiAgLS1qcC1zdWNjZXNzLWNvbG9yMzogdmFyKC0tbWQtZ3JlZW4tMTAwLCAjYzhlNmM5KTtcbiAgLS1qcC1pbmZvLWNvbG9yMDogdmFyKC0tbWQtY3lhbi05MDAsICMwMDYwNjQpO1xuICAtLWpwLWluZm8tY29sb3IxOiB2YXIoLS1tZC1jeWFuLTcwMCwgIzAwOTdhNyk7XG4gIC0tanAtaW5mby1jb2xvcjI6IHZhcigtLW1kLWN5YW4tMzAwLCAjNGRkMGUxKTtcbiAgLS1qcC1pbmZvLWNvbG9yMzogdmFyKC0tbWQtY3lhbi0xMDAsICNiMmViZjIpO1xuXG4gIC8qIENlbGwgc3BlY2lmaWMgc3R5bGVzICovXG5cbiAgLS1qcC1jZWxsLXBhZGRpbmc6IDVweDtcbiAgLS1qcC1jZWxsLWNvbGxhcHNlci13aWR0aDogOHB4O1xuICAtLWpwLWNlbGwtY29sbGFwc2VyLW1pbi1oZWlnaHQ6IDIwcHg7XG4gIC0tanAtY2VsbC1jb2xsYXBzZXItbm90LWFjdGl2ZS1ob3Zlci1vcGFjaXR5OiAwLjY7XG4gIC0tanAtY2VsbC1lZGl0b3ItYmFja2dyb3VuZDogdmFyKC0tbWQtZ3JleS0xMDAsICNmNWY1ZjUpO1xuICAtLWpwLWNlbGwtZWRpdG9yLWJvcmRlci1jb2xvcjogdmFyKC0tbWQtZ3JleS0zMDAsICNlMGUwZTApO1xuICAtLWpwLWNlbGwtZWRpdG9yLWJveC1zaGFkb3c6IGluc2V0IDAgMCAycHggdmFyKC0tbWQtYmx1ZS0zMDAsICM2NGI1ZjYpO1xuICAtLWpwLWNlbGwtZWRpdG9yLWFjdGl2ZS1iYWNrZ3JvdW5kOiB2YXIoLS1qcC1sYXlvdXQtY29sb3IwKTtcbiAgLS1qcC1jZWxsLWVkaXRvci1hY3RpdmUtYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1icmFuZC1jb2xvcjEpO1xuICAtLWpwLWNlbGwtcHJvbXB0LXdpZHRoOiA2NHB4O1xuICAtLWpwLWNlbGwtcHJvbXB0LWZvbnQtZmFtaWx5OiB2YXIoLS1qcC1jb2RlLWZvbnQtZmFtaWx5LWRlZmF1bHQpO1xuICAtLWpwLWNlbGwtcHJvbXB0LWxldHRlci1zcGFjaW5nOiAwO1xuICAtLWpwLWNlbGwtcHJvbXB0LW9wYWNpdHk6IDE7XG4gIC0tanAtY2VsbC1wcm9tcHQtbm90LWFjdGl2ZS1vcGFjaXR5OiAwLjU7XG4gIC0tanAtY2VsbC1wcm9tcHQtbm90LWFjdGl2ZS1mb250LWNvbG9yOiB2YXIoLS1tZC1ncmV5LTcwMCwgIzYxNjE2MSk7XG5cbiAgLyogQSBjdXN0b20gYmxlbmQgb2YgTUQgZ3JleSBhbmQgYmx1ZSA2MDBcbiAgICogU2VlIGh0dHBzOi8vbWV5ZXJ3ZWIuY29tL2VyaWMvdG9vbHMvY29sb3ItYmxlbmQvIzU0NkU3QToxRTg4RTU6NTpoZXggKi9cbiAgLS1qcC1jZWxsLWlucHJvbXB0LWZvbnQtY29sb3I6ICMzMDdmYzE7XG5cbiAgLyogQSBjdXN0b20gYmxlbmQgb2YgTUQgZ3JleSBhbmQgb3JhbmdlIDYwMFxuICAgKiBodHRwczovL21leWVyd2ViLmNvbS9lcmljL3Rvb2xzL2NvbG9yLWJsZW5kLyM1NDZFN0E6RjQ1MTFFOjU6aGV4ICovXG4gIC0tanAtY2VsbC1vdXRwcm9tcHQtZm9udC1jb2xvcjogI2JmNWIzZDtcblxuICAvKiBOb3RlYm9vayBzcGVjaWZpYyBzdHlsZXMgKi9cblxuICAtLWpwLW5vdGVib29rLXBhZGRpbmc6IDEwcHg7XG4gIC0tanAtbm90ZWJvb2stc2VsZWN0LWJhY2tncm91bmQ6IHZhcigtLWpwLWxheW91dC1jb2xvcjEpO1xuICAtLWpwLW5vdGVib29rLW11bHRpc2VsZWN0ZWQtY29sb3I6IHZhcigtLW1kLWJsdWUtNTAsICNlM2YyZmQpO1xuXG4gIC8qIFRoZSBzY3JvbGwgcGFkZGluZyBpcyBjYWxjdWxhdGVkIHRvIGZpbGwgZW5vdWdoIHNwYWNlIGF0IHRoZSBib3R0b20gb2YgdGhlXG4gIG5vdGVib29rIHRvIHNob3cgb25lIHNpbmdsZS1saW5lIGNlbGwgKHdpdGggYXBwcm9wcmlhdGUgcGFkZGluZykgYXQgdGhlIHRvcFxuICB3aGVuIHRoZSBub3RlYm9vayBpcyBzY3JvbGxlZCBhbGwgdGhlIHdheSB0byB0aGUgYm90dG9tLiBXZSBhbHNvIHN1YnRyYWN0IG9uZVxuICBwaXhlbCBzbyB0aGF0IG5vIHNjcm9sbGJhciBhcHBlYXJzIGlmIHdlIGhhdmUganVzdCBvbmUgc2luZ2xlLWxpbmUgY2VsbCBpbiB0aGVcbiAgbm90ZWJvb2suIFRoaXMgcGFkZGluZyBpcyB0byBlbmFibGUgYSAnc2Nyb2xsIHBhc3QgZW5kJyBmZWF0dXJlIGluIGEgbm90ZWJvb2suXG4gICovXG4gIC0tanAtbm90ZWJvb2stc2Nyb2xsLXBhZGRpbmc6IGNhbGMoXG4gICAgMTAwJSAtIHZhcigtLWpwLWNvZGUtZm9udC1zaXplKSAqIHZhcigtLWpwLWNvZGUtbGluZS1oZWlnaHQpIC1cbiAgICAgIHZhcigtLWpwLWNvZGUtcGFkZGluZykgLSB2YXIoLS1qcC1jZWxsLXBhZGRpbmcpIC0gMXB4XG4gICk7XG5cbiAgLyogVGhlIHNjcm9sbCBwYWRkaW5nIGlzIGNhbGN1bGF0ZWQgdG8gcHJvdmlkZSBlbm91Z2ggc3BhY2UgYXQgdGhlIGJvdHRvbSBvZlxuICAgICBhIHRleHQgZWRpdG9yIHRvIGFsbG93IHRoZSBsYXN0IGxpbmUgb2YgY29kZSB0byBiZSBwb3NpdGlvbmVkIGF0IHRoZSB0b3BcbiAgICAgb2YgdGhlIHZpZXdwb3J0IHdoZW4gdGhlIGVkaXRvciBpcyBzY3JvbGxlZCBhbGwgdGhlIHdheSBkb3duLiBXZSBhbHNvXG4gICAgIHN1YnRyYWN0IG9uZSBwaXhlbCB0byBhdm9pZCBzaG93aW5nIGEgc2Nyb2xsYmFyIHdoZW4gdGhlIGZpbGUgY29udGFpbnNcbiAgICAgb25seSBhIHNpbmdsZSBsaW5lLiBUaGlzIHBhZGRpbmcgZW5hYmxlcyBhICdzY3JvbGwgcGFzdCBlbmQnIGZlYXR1cmUgaW5cbiAgICAgdGV4dCBlZGl0b3JzLiAqL1xuICAtLWpwLWVkaXRvci1zY3JvbGwtcGFkZGluZzogY2FsYyhcbiAgICAxMDAlIC0gdmFyKC0tanAtY29kZS1mb250LXNpemUpICogdmFyKC0tanAtY29kZS1saW5lLWhlaWdodCkgLVxuICAgICAgdmFyKC0tanAtY29kZS1wYWRkaW5nKSAtIDFweFxuICApO1xuXG4gIC8qIFJlbmRlcm1pbWUgc3R5bGVzICovXG5cbiAgLS1qcC1yZW5kZXJtaW1lLWVycm9yLWJhY2tncm91bmQ6ICNmZGQ7XG4gIC0tanAtcmVuZGVybWltZS10YWJsZS1yb3ctYmFja2dyb3VuZDogdmFyKC0tbWQtZ3JleS0xMDAsICNjZmQ4ZGMpO1xuICAtLWpwLXJlbmRlcm1pbWUtdGFibGUtcm93LWhvdmVyLWJhY2tncm91bmQ6IHZhcigtLW1kLWxpZ2h0LWJsdWUtNTAsICNlMWY1ZmUpO1xuXG4gIC8qIERpYWxvZyBzcGVjaWZpYyBzdHlsZXMgKi9cblxuICAtLWpwLWRpYWxvZy1iYWNrZ3JvdW5kOiByZ2JhKDAsIDAsIDAsIDAuMjUpO1xuXG4gIC8qIENvbnNvbGUgc3BlY2lmaWMgc3R5bGVzICovXG5cbiAgLS1qcC1jb25zb2xlLXBhZGRpbmc6IDEwcHg7XG5cbiAgLyogVG9vbGJhciBzcGVjaWZpYyBzdHlsZXMgKi9cblxuICAtLWpwLXRvb2xiYXItYm9yZGVyLWNvbG9yOiB2YXIoLS1qcC1ib3JkZXItY29sb3IxKTtcbiAgLS1qcC10b29sYmFyLW1pY3JvLWhlaWdodDogOHB4O1xuICAtLWpwLXRvb2xiYXItYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMSk7XG4gIC0tanAtdG9vbGJhci1ib3gtc2hhZG93OiAwIDAgMnB4IDAgcmdiYSgwLCAwLCAwLCAwLjI0KTtcbiAgLS1qcC10b29sYmFyLWhlYWRlci1tYXJnaW46IDRweCA0cHggMCA0cHg7XG4gIC0tanAtdG9vbGJhci1hY3RpdmUtYmFja2dyb3VuZDogdmFyKC0tbWQtZ3JleS0zMDAsICM5MGE0YWUpO1xuXG4gIC8qIFN0YXR1c2JhciBzcGVjaWZpYyBzdHlsZXMgKi9cblxuICAtLWpwLXN0YXR1c2Jhci1oZWlnaHQ6IDI0cHg7XG5cbiAgLyogSW5wdXQgZmllbGQgc3R5bGVzICovXG5cbiAgLS1qcC1pbnB1dC1ib3gtc2hhZG93OiBpbnNldCAwIDAgMnB4IHZhcigtLW1kLWJsdWUtMzAwLCAjNjRiNWY2KTtcbiAgLS1qcC1pbnB1dC1hY3RpdmUtYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMSk7XG4gIC0tanAtaW5wdXQtaG92ZXItYmFja2dyb3VuZDogdmFyKC0tanAtbGF5b3V0LWNvbG9yMSk7XG4gIC0tanAtaW5wdXQtYmFja2dyb3VuZDogdmFyKC0tbWQtZ3JleS0xMDAsICNmNWY1ZjUpO1xuICAtLWpwLWlucHV0LWJvcmRlci1jb2xvcjogdmFyKC0tanAtaW52ZXJzZS1ib3JkZXItY29sb3IpO1xuICAtLWpwLWlucHV0LWFjdGl2ZS1ib3JkZXItY29sb3I6IHZhcigtLWpwLWJyYW5kLWNvbG9yMSk7XG4gIC0tanAtaW5wdXQtYWN0aXZlLWJveC1zaGFkb3ctY29sb3I6IHJnYmEoMTksIDEyNCwgMTg5LCAwLjMpO1xuXG4gIC8qIEdlbmVyYWwgZWRpdG9yIHN0eWxlcyAqL1xuXG4gIC0tanAtZWRpdG9yLXNlbGVjdGVkLWJhY2tncm91bmQ6ICNkOWQ5ZDk7XG4gIC0tanAtZWRpdG9yLXNlbGVjdGVkLWZvY3VzZWQtYmFja2dyb3VuZDogI2Q3ZDRmMDtcbiAgLS1qcC1lZGl0b3ItY3Vyc29yLWNvbG9yOiB2YXIoLS1qcC11aS1mb250LWNvbG9yMCk7XG5cbiAgLyogQ29kZSBtaXJyb3Igc3BlY2lmaWMgc3R5bGVzICovXG5cbiAgLS1qcC1taXJyb3ItZWRpdG9yLWtleXdvcmQtY29sb3I6ICMwMDgwMDA7XG4gIC0tanAtbWlycm9yLWVkaXRvci1hdG9tLWNvbG9yOiAjODhmO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItbnVtYmVyLWNvbG9yOiAjMDgwO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItZGVmLWNvbG9yOiAjMDBmO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItdmFyaWFibGUtY29sb3I6IHZhcigtLW1kLWdyZXktOTAwLCAjMjEyMTIxKTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXZhcmlhYmxlLTItY29sb3I6IHJnYigwLCA1NCwgMTA5KTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXZhcmlhYmxlLTMtY29sb3I6ICMwODU7XG4gIC0tanAtbWlycm9yLWVkaXRvci1wdW5jdHVhdGlvbi1jb2xvcjogIzA1YTtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLXByb3BlcnR5LWNvbG9yOiAjMDVhO1xuICAtLWpwLW1pcnJvci1lZGl0b3Itb3BlcmF0b3ItY29sb3I6ICM3ODAwYzI7XG4gIC0tanAtbWlycm9yLWVkaXRvci1jb21tZW50LWNvbG9yOiAjNDA4MDgwO1xuICAtLWpwLW1pcnJvci1lZGl0b3Itc3RyaW5nLWNvbG9yOiAjYmEyMTIxO1xuICAtLWpwLW1pcnJvci1lZGl0b3Itc3RyaW5nLTItY29sb3I6ICM3MDg7XG4gIC0tanAtbWlycm9yLWVkaXRvci1tZXRhLWNvbG9yOiAjYTJmO1xuICAtLWpwLW1pcnJvci1lZGl0b3ItcXVhbGlmaWVyLWNvbG9yOiAjNTU1O1xuICAtLWpwLW1pcnJvci1lZGl0b3ItYnVpbHRpbi1jb2xvcjogIzAwODAwMDtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWJyYWNrZXQtY29sb3I6ICM5OTc7XG4gIC0tanAtbWlycm9yLWVkaXRvci10YWctY29sb3I6ICMxNzA7XG4gIC0tanAtbWlycm9yLWVkaXRvci1hdHRyaWJ1dGUtY29sb3I6ICMwMGM7XG4gIC0tanAtbWlycm9yLWVkaXRvci1oZWFkZXItY29sb3I6IGJsdWU7XG4gIC0tanAtbWlycm9yLWVkaXRvci1xdW90ZS1jb2xvcjogIzA5MDtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWxpbmstY29sb3I6ICMwMGM7XG4gIC0tanAtbWlycm9yLWVkaXRvci1lcnJvci1jb2xvcjogI2YwMDtcbiAgLS1qcC1taXJyb3ItZWRpdG9yLWhyLWNvbG9yOiAjOTk5O1xuXG4gIC8qXG4gICAgUlRDIHVzZXIgc3BlY2lmaWMgY29sb3JzLlxuICAgIFRoZXNlIGNvbG9ycyBhcmUgdXNlZCBmb3IgdGhlIGN1cnNvciwgdXNlcm5hbWUgaW4gdGhlIGVkaXRvcixcbiAgICBhbmQgdGhlIGljb24gb2YgdGhlIHVzZXIuXG4gICovXG5cbiAgLS1qcC1jb2xsYWJvcmF0b3ItY29sb3IxOiAjZmZhZDhlO1xuICAtLWpwLWNvbGxhYm9yYXRvci1jb2xvcjI6ICNkYWM4M2Q7XG4gIC0tanAtY29sbGFib3JhdG9yLWNvbG9yMzogIzcyZGQ3NjtcbiAgLS1qcC1jb2xsYWJvcmF0b3ItY29sb3I0OiAjMDBlNGQwO1xuICAtLWpwLWNvbGxhYm9yYXRvci1jb2xvcjU6ICM0NWQ0ZmY7XG4gIC0tanAtY29sbGFib3JhdG9yLWNvbG9yNjogI2UyYjFmZjtcbiAgLS1qcC1jb2xsYWJvcmF0b3ItY29sb3I3OiAjZmY5ZGU2O1xuXG4gIC8qIFZlZ2EgZXh0ZW5zaW9uIHN0eWxlcyAqL1xuXG4gIC0tanAtdmVnYS1iYWNrZ3JvdW5kOiB3aGl0ZTtcblxuICAvKiBTaWRlYmFyLXJlbGF0ZWQgc3R5bGVzICovXG5cbiAgLS1qcC1zaWRlYmFyLW1pbi13aWR0aDogMjUwcHg7XG5cbiAgLyogU2VhcmNoLXJlbGF0ZWQgc3R5bGVzICovXG5cbiAgLS1qcC1zZWFyY2gtdG9nZ2xlLW9mZi1vcGFjaXR5OiAwLjU7XG4gIC0tanAtc2VhcmNoLXRvZ2dsZS1ob3Zlci1vcGFjaXR5OiAwLjg7XG4gIC0tanAtc2VhcmNoLXRvZ2dsZS1vbi1vcGFjaXR5OiAxO1xuICAtLWpwLXNlYXJjaC1zZWxlY3RlZC1tYXRjaC1iYWNrZ3JvdW5kLWNvbG9yOiByZ2IoMjQ1LCAyMDAsIDApO1xuICAtLWpwLXNlYXJjaC1zZWxlY3RlZC1tYXRjaC1jb2xvcjogYmxhY2s7XG4gIC0tanAtc2VhcmNoLXVuc2VsZWN0ZWQtbWF0Y2gtYmFja2dyb3VuZC1jb2xvcjogdmFyKFxuICAgIC0tanAtaW52ZXJzZS1sYXlvdXQtY29sb3IwXG4gICk7XG4gIC0tanAtc2VhcmNoLXVuc2VsZWN0ZWQtbWF0Y2gtY29sb3I6IHZhcigtLWpwLXVpLWludmVyc2UtZm9udC1jb2xvcjApO1xuXG4gIC8qIEljb24gY29sb3JzIHRoYXQgd29yayB3ZWxsIHdpdGggbGlnaHQgb3IgZGFyayBiYWNrZ3JvdW5kcyAqL1xuICAtLWpwLWljb24tY29udHJhc3QtY29sb3IwOiB2YXIoLS1tZC1wdXJwbGUtNjAwLCAjOGUyNGFhKTtcbiAgLS1qcC1pY29uLWNvbnRyYXN0LWNvbG9yMTogdmFyKC0tbWQtZ3JlZW4tNjAwLCAjNDNhMDQ3KTtcbiAgLS1qcC1pY29uLWNvbnRyYXN0LWNvbG9yMjogdmFyKC0tbWQtcGluay02MDAsICNkODFiNjApO1xuICAtLWpwLWljb24tY29udHJhc3QtY29sb3IzOiB2YXIoLS1tZC1ibHVlLTYwMCwgIzFlODhlNSk7XG5cbiAgLyogQnV0dG9uIGNvbG9ycyAqL1xuICAtLWpwLWFjY2VwdC1jb2xvci1ub3JtYWw6IHZhcigtLW1kLWJsdWUtNzAwLCAjMTk3NmQyKTtcbiAgLS1qcC1hY2NlcHQtY29sb3ItaG92ZXI6IHZhcigtLW1kLWJsdWUtODAwLCAjMTU2NWMwKTtcbiAgLS1qcC1hY2NlcHQtY29sb3ItYWN0aXZlOiB2YXIoLS1tZC1ibHVlLTkwMCwgIzBkNDdhMSk7XG4gIC0tanAtd2Fybi1jb2xvci1ub3JtYWw6IHZhcigtLW1kLXJlZC03MDAsICNkMzJmMmYpO1xuICAtLWpwLXdhcm4tY29sb3ItaG92ZXI6IHZhcigtLW1kLXJlZC04MDAsICNjNjI4MjgpO1xuICAtLWpwLXdhcm4tY29sb3ItYWN0aXZlOiB2YXIoLS1tZC1yZWQtOTAwLCAjYjcxYzFjKTtcbiAgLS1qcC1yZWplY3QtY29sb3Itbm9ybWFsOiB2YXIoLS1tZC1ncmV5LTYwMCwgIzc1NzU3NSk7XG4gIC0tanAtcmVqZWN0LWNvbG9yLWhvdmVyOiB2YXIoLS1tZC1ncmV5LTcwMCwgIzYxNjE2MSk7XG4gIC0tanAtcmVqZWN0LWNvbG9yLWFjdGl2ZTogdmFyKC0tbWQtZ3JleS04MDAsICM0MjQyNDIpO1xuXG4gIC8qIEZpbGUgb3IgYWN0aXZpdHkgaWNvbnMgYW5kIHN3aXRjaCBzZW1hbnRpYyB2YXJpYWJsZXMgKi9cbiAgLS1qcC1qdXB5dGVyLWljb24tY29sb3I6ICNmMzc2MjY7XG4gIC0tanAtbm90ZWJvb2staWNvbi1jb2xvcjogI2YzNzYyNjtcbiAgLS1qcC1qc29uLWljb24tY29sb3I6IHZhcigtLW1kLW9yYW5nZS03MDAsICNmNTdjMDApO1xuICAtLWpwLWNvbnNvbGUtaWNvbi1iYWNrZ3JvdW5kLWNvbG9yOiB2YXIoLS1tZC1ibHVlLTcwMCwgIzE5NzZkMik7XG4gIC0tanAtY29uc29sZS1pY29uLWNvbG9yOiB3aGl0ZTtcbiAgLS1qcC10ZXJtaW5hbC1pY29uLWJhY2tncm91bmQtY29sb3I6IHZhcigtLW1kLWdyZXktODAwLCAjNDI0MjQyKTtcbiAgLS1qcC10ZXJtaW5hbC1pY29uLWNvbG9yOiB2YXIoLS1tZC1ncmV5LTIwMCwgI2VlZSk7XG4gIC0tanAtdGV4dC1lZGl0b3ItaWNvbi1jb2xvcjogdmFyKC0tbWQtZ3JleS03MDAsICM2MTYxNjEpO1xuICAtLWpwLWluc3BlY3Rvci1pY29uLWNvbG9yOiB2YXIoLS1tZC1ncmV5LTcwMCwgIzYxNjE2MSk7XG4gIC0tanAtc3dpdGNoLWNvbG9yOiB2YXIoLS1tZC1ncmV5LTQwMCwgI2JkYmRiZCk7XG4gIC0tanAtc3dpdGNoLXRydWUtcG9zaXRpb24tY29sb3I6IHZhcigtLW1kLW9yYW5nZS05MDAsICNlNjUxMDApO1xufVxuXG4vKiBDb21wbGV0ZXIgc3BlY2lmaWMgc3R5bGVzICovXG5cbi5qcC1Db21wbGV0ZXIge1xuICAtLWpwLWNvbXBsZXRlci10eXBlLWJhY2tncm91bmQwOiB0cmFuc3BhcmVudDtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kMTogIzFmNzdiNDtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kMjogI2ZmN2YwZTtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kMzogIzJjYTAyYztcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kNDogI2Q2MjcyODtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kNTogIzk0NjdiZDtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kNjogIzhjNTY0YjtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kNzogI2UzNzdjMjtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kODogIzdmN2Y3ZjtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kOTogI2JjYmQyMjtcbiAgLS1qcC1jb21wbGV0ZXItdHlwZS1iYWNrZ3JvdW5kMTA6ICMxN2JlY2Y7XG59XG5gLCBcIlwiXSk7XG4vLyBFeHBvcnRzXG5leHBvcnQgZGVmYXVsdCBfX19DU1NfTE9BREVSX0VYUE9SVF9fXztcbiIsImltcG9ydCBhcGkgZnJvbSBcIiEuLi8uLi8uLi9zdHlsZS1sb2FkZXIvZGlzdC9ydW50aW1lL2luamVjdFN0eWxlc0ludG9TdHlsZVRhZy5qc1wiO1xuICAgICAgICAgICAgaW1wb3J0IGNvbnRlbnQgZnJvbSBcIiEhLi4vLi4vLi4vY3NzLWxvYWRlci9kaXN0L2Nqcy5qcyEuL3ZhcmlhYmxlcy5jc3M/cmF3XCI7XG5cbnZhciBvcHRpb25zID0ge307XG5cbm9wdGlvbnMuaW5zZXJ0ID0gXCJoZWFkXCI7XG5vcHRpb25zLnNpbmdsZXRvbiA9IGZhbHNlO1xuXG52YXIgdXBkYXRlID0gYXBpKGNvbnRlbnQsIG9wdGlvbnMpO1xuXG5cblxuZXhwb3J0IGRlZmF1bHQgY29udGVudC5sb2NhbHMgfHwge307Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==