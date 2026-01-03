"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[4545],{

/***/ 4545
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   gss: () => (/* binding */ gss),
/* harmony export */   less: () => (/* binding */ less),
/* harmony export */   sCSS: () => (/* binding */ sCSS)
/* harmony export */ });
/* unused harmony exports mkCSS, keywords, css */
function mkCSS(parserConfig) {
  parserConfig = {
    ...defaults,
    ...parserConfig
  };
  var inline = parserConfig.inline;
  var tokenHooks = parserConfig.tokenHooks,
    documentTypes = parserConfig.documentTypes || {},
    mediaTypes = parserConfig.mediaTypes || {},
    mediaFeatures = parserConfig.mediaFeatures || {},
    mediaValueKeywords = parserConfig.mediaValueKeywords || {},
    propertyKeywords = parserConfig.propertyKeywords || {},
    nonStandardPropertyKeywords = parserConfig.nonStandardPropertyKeywords || {},
    fontProperties = parserConfig.fontProperties || {},
    counterDescriptors = parserConfig.counterDescriptors || {},
    colorKeywords = parserConfig.colorKeywords || {},
    valueKeywords = parserConfig.valueKeywords || {},
    allowNested = parserConfig.allowNested,
    lineComment = parserConfig.lineComment,
    supportsAtComponent = parserConfig.supportsAtComponent === true,
    highlightNonStandardPropertyKeywords = parserConfig.highlightNonStandardPropertyKeywords !== false;
  var type, override;
  function ret(style, tp) {
    type = tp;
    return style;
  }

  // Tokenizers

  function tokenBase(stream, state) {
    var ch = stream.next();
    if (tokenHooks[ch]) {
      var result = tokenHooks[ch](stream, state);
      if (result !== false) return result;
    }
    if (ch == "@") {
      stream.eatWhile(/[\w\\\-]/);
      return ret("def", stream.current());
    } else if (ch == "=" || (ch == "~" || ch == "|") && stream.eat("=")) {
      return ret(null, "compare");
    } else if (ch == "\"" || ch == "'") {
      state.tokenize = tokenString(ch);
      return state.tokenize(stream, state);
    } else if (ch == "#") {
      stream.eatWhile(/[\w\\\-]/);
      return ret("atom", "hash");
    } else if (ch == "!") {
      stream.match(/^\s*\w*/);
      return ret("keyword", "important");
    } else if (/\d/.test(ch) || ch == "." && stream.eat(/\d/)) {
      stream.eatWhile(/[\w.%]/);
      return ret("number", "unit");
    } else if (ch === "-") {
      if (/[\d.]/.test(stream.peek())) {
        stream.eatWhile(/[\w.%]/);
        return ret("number", "unit");
      } else if (stream.match(/^-[\w\\\-]*/)) {
        stream.eatWhile(/[\w\\\-]/);
        if (stream.match(/^\s*:/, false)) return ret("def", "variable-definition");
        return ret("variableName", "variable");
      } else if (stream.match(/^\w+-/)) {
        return ret("meta", "meta");
      }
    } else if (/[,+>*\/]/.test(ch)) {
      return ret(null, "select-op");
    } else if (ch == "." && stream.match(/^-?[_a-z][_a-z0-9-]*/i)) {
      return ret("qualifier", "qualifier");
    } else if (/[:;{}\[\]\(\)]/.test(ch)) {
      return ret(null, ch);
    } else if (stream.match(/^[\w-.]+(?=\()/)) {
      if (/^(url(-prefix)?|domain|regexp)$/i.test(stream.current())) {
        state.tokenize = tokenParenthesized;
      }
      return ret("variableName.function", "variable");
    } else if (/[\w\\\-]/.test(ch)) {
      stream.eatWhile(/[\w\\\-]/);
      return ret("property", "word");
    } else {
      return ret(null, null);
    }
  }
  function tokenString(quote) {
    return function (stream, state) {
      var escaped = false,
        ch;
      while ((ch = stream.next()) != null) {
        if (ch == quote && !escaped) {
          if (quote == ")") stream.backUp(1);
          break;
        }
        escaped = !escaped && ch == "\\";
      }
      if (ch == quote || !escaped && quote != ")") state.tokenize = null;
      return ret("string", "string");
    };
  }
  function tokenParenthesized(stream, state) {
    stream.next(); // Must be '('
    if (!stream.match(/^\s*[\"\')]/, false)) state.tokenize = tokenString(")");else state.tokenize = null;
    return ret(null, "(");
  }

  // Context management

  function Context(type, indent, prev) {
    this.type = type;
    this.indent = indent;
    this.prev = prev;
  }
  function pushContext(state, stream, type, indent) {
    state.context = new Context(type, stream.indentation() + (indent === false ? 0 : stream.indentUnit), state.context);
    return type;
  }
  function popContext(state) {
    if (state.context.prev) state.context = state.context.prev;
    return state.context.type;
  }
  function pass(type, stream, state) {
    return states[state.context.type](type, stream, state);
  }
  function popAndPass(type, stream, state, n) {
    for (var i = n || 1; i > 0; i--) state.context = state.context.prev;
    return pass(type, stream, state);
  }

  // Parser

  function wordAsValue(stream) {
    var word = stream.current().toLowerCase();
    if (valueKeywords.hasOwnProperty(word)) override = "atom";else if (colorKeywords.hasOwnProperty(word)) override = "keyword";else override = "variable";
  }
  var states = {};
  states.top = function (type, stream, state) {
    if (type == "{") {
      return pushContext(state, stream, "block");
    } else if (type == "}" && state.context.prev) {
      return popContext(state);
    } else if (supportsAtComponent && /@component/i.test(type)) {
      return pushContext(state, stream, "atComponentBlock");
    } else if (/^@(-moz-)?document$/i.test(type)) {
      return pushContext(state, stream, "documentTypes");
    } else if (/^@(media|supports|(-moz-)?document|import)$/i.test(type)) {
      return pushContext(state, stream, "atBlock");
    } else if (/^@(font-face|counter-style)/i.test(type)) {
      state.stateArg = type;
      return "restricted_atBlock_before";
    } else if (/^@(-(moz|ms|o|webkit)-)?keyframes$/i.test(type)) {
      return "keyframes";
    } else if (type && type.charAt(0) == "@") {
      return pushContext(state, stream, "at");
    } else if (type == "hash") {
      override = "builtin";
    } else if (type == "word") {
      override = "tag";
    } else if (type == "variable-definition") {
      return "maybeprop";
    } else if (type == "interpolation") {
      return pushContext(state, stream, "interpolation");
    } else if (type == ":") {
      return "pseudo";
    } else if (allowNested && type == "(") {
      return pushContext(state, stream, "parens");
    }
    return state.context.type;
  };
  states.block = function (type, stream, state) {
    if (type == "word") {
      var word = stream.current().toLowerCase();
      if (propertyKeywords.hasOwnProperty(word)) {
        override = "property";
        return "maybeprop";
      } else if (nonStandardPropertyKeywords.hasOwnProperty(word)) {
        override = highlightNonStandardPropertyKeywords ? "string.special" : "property";
        return "maybeprop";
      } else if (allowNested) {
        override = stream.match(/^\s*:(?:\s|$)/, false) ? "property" : "tag";
        return "block";
      } else {
        override = "error";
        return "maybeprop";
      }
    } else if (type == "meta") {
      return "block";
    } else if (!allowNested && (type == "hash" || type == "qualifier")) {
      override = "error";
      return "block";
    } else {
      return states.top(type, stream, state);
    }
  };
  states.maybeprop = function (type, stream, state) {
    if (type == ":") return pushContext(state, stream, "prop");
    return pass(type, stream, state);
  };
  states.prop = function (type, stream, state) {
    if (type == ";") return popContext(state);
    if (type == "{" && allowNested) return pushContext(state, stream, "propBlock");
    if (type == "}" || type == "{") return popAndPass(type, stream, state);
    if (type == "(") return pushContext(state, stream, "parens");
    if (type == "hash" && !/^#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(stream.current())) {
      override = "error";
    } else if (type == "word") {
      wordAsValue(stream);
    } else if (type == "interpolation") {
      return pushContext(state, stream, "interpolation");
    }
    return "prop";
  };
  states.propBlock = function (type, _stream, state) {
    if (type == "}") return popContext(state);
    if (type == "word") {
      override = "property";
      return "maybeprop";
    }
    return state.context.type;
  };
  states.parens = function (type, stream, state) {
    if (type == "{" || type == "}") return popAndPass(type, stream, state);
    if (type == ")") return popContext(state);
    if (type == "(") return pushContext(state, stream, "parens");
    if (type == "interpolation") return pushContext(state, stream, "interpolation");
    if (type == "word") wordAsValue(stream);
    return "parens";
  };
  states.pseudo = function (type, stream, state) {
    if (type == "meta") return "pseudo";
    if (type == "word") {
      override = "variableName.constant";
      return state.context.type;
    }
    return pass(type, stream, state);
  };
  states.documentTypes = function (type, stream, state) {
    if (type == "word" && documentTypes.hasOwnProperty(stream.current())) {
      override = "tag";
      return state.context.type;
    } else {
      return states.atBlock(type, stream, state);
    }
  };
  states.atBlock = function (type, stream, state) {
    if (type == "(") return pushContext(state, stream, "atBlock_parens");
    if (type == "}" || type == ";") return popAndPass(type, stream, state);
    if (type == "{") return popContext(state) && pushContext(state, stream, allowNested ? "block" : "top");
    if (type == "interpolation") return pushContext(state, stream, "interpolation");
    if (type == "word") {
      var word = stream.current().toLowerCase();
      if (word == "only" || word == "not" || word == "and" || word == "or") override = "keyword";else if (mediaTypes.hasOwnProperty(word)) override = "attribute";else if (mediaFeatures.hasOwnProperty(word)) override = "property";else if (mediaValueKeywords.hasOwnProperty(word)) override = "keyword";else if (propertyKeywords.hasOwnProperty(word)) override = "property";else if (nonStandardPropertyKeywords.hasOwnProperty(word)) override = highlightNonStandardPropertyKeywords ? "string.special" : "property";else if (valueKeywords.hasOwnProperty(word)) override = "atom";else if (colorKeywords.hasOwnProperty(word)) override = "keyword";else override = "error";
    }
    return state.context.type;
  };
  states.atComponentBlock = function (type, stream, state) {
    if (type == "}") return popAndPass(type, stream, state);
    if (type == "{") return popContext(state) && pushContext(state, stream, allowNested ? "block" : "top", false);
    if (type == "word") override = "error";
    return state.context.type;
  };
  states.atBlock_parens = function (type, stream, state) {
    if (type == ")") return popContext(state);
    if (type == "{" || type == "}") return popAndPass(type, stream, state, 2);
    return states.atBlock(type, stream, state);
  };
  states.restricted_atBlock_before = function (type, stream, state) {
    if (type == "{") return pushContext(state, stream, "restricted_atBlock");
    if (type == "word" && state.stateArg == "@counter-style") {
      override = "variable";
      return "restricted_atBlock_before";
    }
    return pass(type, stream, state);
  };
  states.restricted_atBlock = function (type, stream, state) {
    if (type == "}") {
      state.stateArg = null;
      return popContext(state);
    }
    if (type == "word") {
      if (state.stateArg == "@font-face" && !fontProperties.hasOwnProperty(stream.current().toLowerCase()) || state.stateArg == "@counter-style" && !counterDescriptors.hasOwnProperty(stream.current().toLowerCase())) override = "error";else override = "property";
      return "maybeprop";
    }
    return "restricted_atBlock";
  };
  states.keyframes = function (type, stream, state) {
    if (type == "word") {
      override = "variable";
      return "keyframes";
    }
    if (type == "{") return pushContext(state, stream, "top");
    return pass(type, stream, state);
  };
  states.at = function (type, stream, state) {
    if (type == ";") return popContext(state);
    if (type == "{" || type == "}") return popAndPass(type, stream, state);
    if (type == "word") override = "tag";else if (type == "hash") override = "builtin";
    return "at";
  };
  states.interpolation = function (type, stream, state) {
    if (type == "}") return popContext(state);
    if (type == "{" || type == ";") return popAndPass(type, stream, state);
    if (type == "word") override = "variable";else if (type != "variable" && type != "(" && type != ")") override = "error";
    return "interpolation";
  };
  return {
    name: parserConfig.name,
    startState: function () {
      return {
        tokenize: null,
        state: inline ? "block" : "top",
        stateArg: null,
        context: new Context(inline ? "block" : "top", 0, null)
      };
    },
    token: function (stream, state) {
      if (!state.tokenize && stream.eatSpace()) return null;
      var style = (state.tokenize || tokenBase)(stream, state);
      if (style && typeof style == "object") {
        type = style[1];
        style = style[0];
      }
      override = style;
      if (type != "comment") state.state = states[state.state](type, stream, state);
      return override;
    },
    indent: function (state, textAfter, iCx) {
      var cx = state.context,
        ch = textAfter && textAfter.charAt(0);
      var indent = cx.indent;
      if (cx.type == "prop" && (ch == "}" || ch == ")")) cx = cx.prev;
      if (cx.prev) {
        if (ch == "}" && (cx.type == "block" || cx.type == "top" || cx.type == "interpolation" || cx.type == "restricted_atBlock")) {
          // Resume indentation from parent context.
          cx = cx.prev;
          indent = cx.indent;
        } else if (ch == ")" && (cx.type == "parens" || cx.type == "atBlock_parens") || ch == "{" && (cx.type == "at" || cx.type == "atBlock")) {
          // Dedent relative to current context.
          indent = Math.max(0, cx.indent - iCx.unit);
        }
      }
      return indent;
    },
    languageData: {
      indentOnInput: /^\s*\}$/,
      commentTokens: {
        line: lineComment,
        block: {
          open: "/*",
          close: "*/"
        }
      },
      autocomplete: allWords
    }
  };
}
;
function keySet(array) {
  var keys = {};
  for (var i = 0; i < array.length; ++i) {
    keys[array[i].toLowerCase()] = true;
  }
  return keys;
}
var documentTypes_ = ["domain", "regexp", "url", "url-prefix"],
  documentTypes = keySet(documentTypes_);
var mediaTypes_ = ["all", "aural", "braille", "handheld", "print", "projection", "screen", "tty", "tv", "embossed"],
  mediaTypes = keySet(mediaTypes_);
var mediaFeatures_ = ["width", "min-width", "max-width", "height", "min-height", "max-height", "device-width", "min-device-width", "max-device-width", "device-height", "min-device-height", "max-device-height", "aspect-ratio", "min-aspect-ratio", "max-aspect-ratio", "device-aspect-ratio", "min-device-aspect-ratio", "max-device-aspect-ratio", "color", "min-color", "max-color", "color-index", "min-color-index", "max-color-index", "monochrome", "min-monochrome", "max-monochrome", "resolution", "min-resolution", "max-resolution", "scan", "grid", "orientation", "device-pixel-ratio", "min-device-pixel-ratio", "max-device-pixel-ratio", "pointer", "any-pointer", "hover", "any-hover", "prefers-color-scheme", "dynamic-range", "video-dynamic-range"],
  mediaFeatures = keySet(mediaFeatures_);
var mediaValueKeywords_ = ["landscape", "portrait", "none", "coarse", "fine", "on-demand", "hover", "interlace", "progressive", "dark", "light", "standard", "high"],
  mediaValueKeywords = keySet(mediaValueKeywords_);
var propertyKeywords_ = ["align-content", "align-items", "align-self", "alignment-adjust", "alignment-baseline", "all", "anchor-point", "animation", "animation-delay", "animation-direction", "animation-duration", "animation-fill-mode", "animation-iteration-count", "animation-name", "animation-play-state", "animation-timing-function", "appearance", "azimuth", "backdrop-filter", "backface-visibility", "background", "background-attachment", "background-blend-mode", "background-clip", "background-color", "background-image", "background-origin", "background-position", "background-position-x", "background-position-y", "background-repeat", "background-size", "baseline-shift", "binding", "bleed", "block-size", "bookmark-label", "bookmark-level", "bookmark-state", "bookmark-target", "border", "border-bottom", "border-bottom-color", "border-bottom-left-radius", "border-bottom-right-radius", "border-bottom-style", "border-bottom-width", "border-collapse", "border-color", "border-image", "border-image-outset", "border-image-repeat", "border-image-slice", "border-image-source", "border-image-width", "border-left", "border-left-color", "border-left-style", "border-left-width", "border-radius", "border-right", "border-right-color", "border-right-style", "border-right-width", "border-spacing", "border-style", "border-top", "border-top-color", "border-top-left-radius", "border-top-right-radius", "border-top-style", "border-top-width", "border-width", "bottom", "box-decoration-break", "box-shadow", "box-sizing", "break-after", "break-before", "break-inside", "caption-side", "caret-color", "clear", "clip", "color", "color-profile", "column-count", "column-fill", "column-gap", "column-rule", "column-rule-color", "column-rule-style", "column-rule-width", "column-span", "column-width", "columns", "contain", "content", "counter-increment", "counter-reset", "crop", "cue", "cue-after", "cue-before", "cursor", "direction", "display", "dominant-baseline", "drop-initial-after-adjust", "drop-initial-after-align", "drop-initial-before-adjust", "drop-initial-before-align", "drop-initial-size", "drop-initial-value", "elevation", "empty-cells", "fit", "fit-content", "fit-position", "flex", "flex-basis", "flex-direction", "flex-flow", "flex-grow", "flex-shrink", "flex-wrap", "float", "float-offset", "flow-from", "flow-into", "font", "font-family", "font-feature-settings", "font-kerning", "font-language-override", "font-optical-sizing", "font-size", "font-size-adjust", "font-stretch", "font-style", "font-synthesis", "font-variant", "font-variant-alternates", "font-variant-caps", "font-variant-east-asian", "font-variant-ligatures", "font-variant-numeric", "font-variant-position", "font-variation-settings", "font-weight", "gap", "grid", "grid-area", "grid-auto-columns", "grid-auto-flow", "grid-auto-rows", "grid-column", "grid-column-end", "grid-column-gap", "grid-column-start", "grid-gap", "grid-row", "grid-row-end", "grid-row-gap", "grid-row-start", "grid-template", "grid-template-areas", "grid-template-columns", "grid-template-rows", "hanging-punctuation", "height", "hyphens", "icon", "image-orientation", "image-rendering", "image-resolution", "inline-box-align", "inset", "inset-block", "inset-block-end", "inset-block-start", "inset-inline", "inset-inline-end", "inset-inline-start", "isolation", "justify-content", "justify-items", "justify-self", "left", "letter-spacing", "line-break", "line-height", "line-height-step", "line-stacking", "line-stacking-ruby", "line-stacking-shift", "line-stacking-strategy", "list-style", "list-style-image", "list-style-position", "list-style-type", "margin", "margin-bottom", "margin-left", "margin-right", "margin-top", "marks", "marquee-direction", "marquee-loop", "marquee-play-count", "marquee-speed", "marquee-style", "mask-clip", "mask-composite", "mask-image", "mask-mode", "mask-origin", "mask-position", "mask-repeat", "mask-size", "mask-type", "max-block-size", "max-height", "max-inline-size", "max-width", "min-block-size", "min-height", "min-inline-size", "min-width", "mix-blend-mode", "move-to", "nav-down", "nav-index", "nav-left", "nav-right", "nav-up", "object-fit", "object-position", "offset", "offset-anchor", "offset-distance", "offset-path", "offset-position", "offset-rotate", "opacity", "order", "orphans", "outline", "outline-color", "outline-offset", "outline-style", "outline-width", "overflow", "overflow-style", "overflow-wrap", "overflow-x", "overflow-y", "padding", "padding-bottom", "padding-left", "padding-right", "padding-top", "page", "page-break-after", "page-break-before", "page-break-inside", "page-policy", "pause", "pause-after", "pause-before", "perspective", "perspective-origin", "pitch", "pitch-range", "place-content", "place-items", "place-self", "play-during", "position", "presentation-level", "punctuation-trim", "quotes", "region-break-after", "region-break-before", "region-break-inside", "region-fragment", "rendering-intent", "resize", "rest", "rest-after", "rest-before", "richness", "right", "rotate", "rotation", "rotation-point", "row-gap", "ruby-align", "ruby-overhang", "ruby-position", "ruby-span", "scale", "scroll-behavior", "scroll-margin", "scroll-margin-block", "scroll-margin-block-end", "scroll-margin-block-start", "scroll-margin-bottom", "scroll-margin-inline", "scroll-margin-inline-end", "scroll-margin-inline-start", "scroll-margin-left", "scroll-margin-right", "scroll-margin-top", "scroll-padding", "scroll-padding-block", "scroll-padding-block-end", "scroll-padding-block-start", "scroll-padding-bottom", "scroll-padding-inline", "scroll-padding-inline-end", "scroll-padding-inline-start", "scroll-padding-left", "scroll-padding-right", "scroll-padding-top", "scroll-snap-align", "scroll-snap-type", "shape-image-threshold", "shape-inside", "shape-margin", "shape-outside", "size", "speak", "speak-as", "speak-header", "speak-numeral", "speak-punctuation", "speech-rate", "stress", "string-set", "tab-size", "table-layout", "target", "target-name", "target-new", "target-position", "text-align", "text-align-last", "text-combine-upright", "text-decoration", "text-decoration-color", "text-decoration-line", "text-decoration-skip", "text-decoration-skip-ink", "text-decoration-style", "text-emphasis", "text-emphasis-color", "text-emphasis-position", "text-emphasis-style", "text-height", "text-indent", "text-justify", "text-orientation", "text-outline", "text-overflow", "text-rendering", "text-shadow", "text-size-adjust", "text-space-collapse", "text-transform", "text-underline-position", "text-wrap", "top", "touch-action", "transform", "transform-origin", "transform-style", "transition", "transition-delay", "transition-duration", "transition-property", "transition-timing-function", "translate", "unicode-bidi", "user-select", "vertical-align", "visibility", "voice-balance", "voice-duration", "voice-family", "voice-pitch", "voice-range", "voice-rate", "voice-stress", "voice-volume", "volume", "white-space", "widows", "width", "will-change", "word-break", "word-spacing", "word-wrap", "writing-mode", "z-index",
  // SVG-specific
  "clip-path", "clip-rule", "mask", "enable-background", "filter", "flood-color", "flood-opacity", "lighting-color", "stop-color", "stop-opacity", "pointer-events", "color-interpolation", "color-interpolation-filters", "color-rendering", "fill", "fill-opacity", "fill-rule", "image-rendering", "marker", "marker-end", "marker-mid", "marker-start", "paint-order", "shape-rendering", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "text-rendering", "baseline-shift", "dominant-baseline", "glyph-orientation-horizontal", "glyph-orientation-vertical", "text-anchor", "writing-mode"],
  propertyKeywords = keySet(propertyKeywords_);
var nonStandardPropertyKeywords_ = ["accent-color", "aspect-ratio", "border-block", "border-block-color", "border-block-end", "border-block-end-color", "border-block-end-style", "border-block-end-width", "border-block-start", "border-block-start-color", "border-block-start-style", "border-block-start-width", "border-block-style", "border-block-width", "border-inline", "border-inline-color", "border-inline-end", "border-inline-end-color", "border-inline-end-style", "border-inline-end-width", "border-inline-start", "border-inline-start-color", "border-inline-start-style", "border-inline-start-width", "border-inline-style", "border-inline-width", "content-visibility", "margin-block", "margin-block-end", "margin-block-start", "margin-inline", "margin-inline-end", "margin-inline-start", "overflow-anchor", "overscroll-behavior", "padding-block", "padding-block-end", "padding-block-start", "padding-inline", "padding-inline-end", "padding-inline-start", "scroll-snap-stop", "scrollbar-3d-light-color", "scrollbar-arrow-color", "scrollbar-base-color", "scrollbar-dark-shadow-color", "scrollbar-face-color", "scrollbar-highlight-color", "scrollbar-shadow-color", "scrollbar-track-color", "searchfield-cancel-button", "searchfield-decoration", "searchfield-results-button", "searchfield-results-decoration", "shape-inside", "zoom"],
  nonStandardPropertyKeywords = keySet(nonStandardPropertyKeywords_);
var fontProperties_ = ["font-display", "font-family", "src", "unicode-range", "font-variant", "font-feature-settings", "font-stretch", "font-weight", "font-style"],
  fontProperties = keySet(fontProperties_);
var counterDescriptors_ = ["additive-symbols", "fallback", "negative", "pad", "prefix", "range", "speak-as", "suffix", "symbols", "system"],
  counterDescriptors = keySet(counterDescriptors_);
var colorKeywords_ = ["aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanchedalmond", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dimgrey", "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod", "gray", "grey", "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple", "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "snow", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow", "yellowgreen"],
  colorKeywords = keySet(colorKeywords_);
var valueKeywords_ = ["above", "absolute", "activeborder", "additive", "activecaption", "afar", "after-white-space", "ahead", "alias", "all", "all-scroll", "alphabetic", "alternate", "always", "amharic", "amharic-abegede", "antialiased", "appworkspace", "arabic-indic", "armenian", "asterisks", "attr", "auto", "auto-flow", "avoid", "avoid-column", "avoid-page", "avoid-region", "axis-pan", "background", "backwards", "baseline", "below", "bidi-override", "binary", "bengali", "blink", "block", "block-axis", "blur", "bold", "bolder", "border", "border-box", "both", "bottom", "break", "break-all", "break-word", "brightness", "bullets", "button", "buttonface", "buttonhighlight", "buttonshadow", "buttontext", "calc", "cambodian", "capitalize", "caps-lock-indicator", "caption", "captiontext", "caret", "cell", "center", "checkbox", "circle", "cjk-decimal", "cjk-earthly-branch", "cjk-heavenly-stem", "cjk-ideographic", "clear", "clip", "close-quote", "col-resize", "collapse", "color", "color-burn", "color-dodge", "column", "column-reverse", "compact", "condensed", "conic-gradient", "contain", "content", "contents", "content-box", "context-menu", "continuous", "contrast", "copy", "counter", "counters", "cover", "crop", "cross", "crosshair", "cubic-bezier", "currentcolor", "cursive", "cyclic", "darken", "dashed", "decimal", "decimal-leading-zero", "default", "default-button", "dense", "destination-atop", "destination-in", "destination-out", "destination-over", "devanagari", "difference", "disc", "discard", "disclosure-closed", "disclosure-open", "document", "dot-dash", "dot-dot-dash", "dotted", "double", "down", "drop-shadow", "e-resize", "ease", "ease-in", "ease-in-out", "ease-out", "element", "ellipse", "ellipsis", "embed", "end", "ethiopic", "ethiopic-abegede", "ethiopic-abegede-am-et", "ethiopic-abegede-gez", "ethiopic-abegede-ti-er", "ethiopic-abegede-ti-et", "ethiopic-halehame-aa-er", "ethiopic-halehame-aa-et", "ethiopic-halehame-am-et", "ethiopic-halehame-gez", "ethiopic-halehame-om-et", "ethiopic-halehame-sid-et", "ethiopic-halehame-so-et", "ethiopic-halehame-ti-er", "ethiopic-halehame-ti-et", "ethiopic-halehame-tig", "ethiopic-numeric", "ew-resize", "exclusion", "expanded", "extends", "extra-condensed", "extra-expanded", "fantasy", "fast", "fill", "fill-box", "fixed", "flat", "flex", "flex-end", "flex-start", "footnotes", "forwards", "from", "geometricPrecision", "georgian", "grayscale", "graytext", "grid", "groove", "gujarati", "gurmukhi", "hand", "hangul", "hangul-consonant", "hard-light", "hebrew", "help", "hidden", "hide", "higher", "highlight", "highlighttext", "hiragana", "hiragana-iroha", "horizontal", "hsl", "hsla", "hue", "hue-rotate", "icon", "ignore", "inactiveborder", "inactivecaption", "inactivecaptiontext", "infinite", "infobackground", "infotext", "inherit", "initial", "inline", "inline-axis", "inline-block", "inline-flex", "inline-grid", "inline-table", "inset", "inside", "intrinsic", "invert", "italic", "japanese-formal", "japanese-informal", "justify", "kannada", "katakana", "katakana-iroha", "keep-all", "khmer", "korean-hangul-formal", "korean-hanja-formal", "korean-hanja-informal", "landscape", "lao", "large", "larger", "left", "level", "lighter", "lighten", "line-through", "linear", "linear-gradient", "lines", "list-item", "listbox", "listitem", "local", "logical", "loud", "lower", "lower-alpha", "lower-armenian", "lower-greek", "lower-hexadecimal", "lower-latin", "lower-norwegian", "lower-roman", "lowercase", "ltr", "luminosity", "malayalam", "manipulation", "match", "matrix", "matrix3d", "media-play-button", "media-slider", "media-sliderthumb", "media-volume-slider", "media-volume-sliderthumb", "medium", "menu", "menulist", "menulist-button", "menutext", "message-box", "middle", "min-intrinsic", "mix", "mongolian", "monospace", "move", "multiple", "multiple_mask_images", "multiply", "myanmar", "n-resize", "narrower", "ne-resize", "nesw-resize", "no-close-quote", "no-drop", "no-open-quote", "no-repeat", "none", "normal", "not-allowed", "nowrap", "ns-resize", "numbers", "numeric", "nw-resize", "nwse-resize", "oblique", "octal", "opacity", "open-quote", "optimizeLegibility", "optimizeSpeed", "oriya", "oromo", "outset", "outside", "outside-shape", "overlay", "overline", "padding", "padding-box", "painted", "page", "paused", "persian", "perspective", "pinch-zoom", "plus-darker", "plus-lighter", "pointer", "polygon", "portrait", "pre", "pre-line", "pre-wrap", "preserve-3d", "progress", "push-button", "radial-gradient", "radio", "read-only", "read-write", "read-write-plaintext-only", "rectangle", "region", "relative", "repeat", "repeating-linear-gradient", "repeating-radial-gradient", "repeating-conic-gradient", "repeat-x", "repeat-y", "reset", "reverse", "rgb", "rgba", "ridge", "right", "rotate", "rotate3d", "rotateX", "rotateY", "rotateZ", "round", "row", "row-resize", "row-reverse", "rtl", "run-in", "running", "s-resize", "sans-serif", "saturate", "saturation", "scale", "scale3d", "scaleX", "scaleY", "scaleZ", "screen", "scroll", "scrollbar", "scroll-position", "se-resize", "searchfield", "searchfield-cancel-button", "searchfield-decoration", "searchfield-results-button", "searchfield-results-decoration", "self-start", "self-end", "semi-condensed", "semi-expanded", "separate", "sepia", "serif", "show", "sidama", "simp-chinese-formal", "simp-chinese-informal", "single", "skew", "skewX", "skewY", "skip-white-space", "slide", "slider-horizontal", "slider-vertical", "sliderthumb-horizontal", "sliderthumb-vertical", "slow", "small", "small-caps", "small-caption", "smaller", "soft-light", "solid", "somali", "source-atop", "source-in", "source-out", "source-over", "space", "space-around", "space-between", "space-evenly", "spell-out", "square", "square-button", "start", "static", "status-bar", "stretch", "stroke", "stroke-box", "sub", "subpixel-antialiased", "svg_masks", "super", "sw-resize", "symbolic", "symbols", "system-ui", "table", "table-caption", "table-cell", "table-column", "table-column-group", "table-footer-group", "table-header-group", "table-row", "table-row-group", "tamil", "telugu", "text", "text-bottom", "text-top", "textarea", "textfield", "thai", "thick", "thin", "threeddarkshadow", "threedface", "threedhighlight", "threedlightshadow", "threedshadow", "tibetan", "tigre", "tigrinya-er", "tigrinya-er-abegede", "tigrinya-et", "tigrinya-et-abegede", "to", "top", "trad-chinese-formal", "trad-chinese-informal", "transform", "translate", "translate3d", "translateX", "translateY", "translateZ", "transparent", "ultra-condensed", "ultra-expanded", "underline", "unidirectional-pan", "unset", "up", "upper-alpha", "upper-armenian", "upper-greek", "upper-hexadecimal", "upper-latin", "upper-norwegian", "upper-roman", "uppercase", "urdu", "url", "var", "vertical", "vertical-text", "view-box", "visible", "visibleFill", "visiblePainted", "visibleStroke", "visual", "w-resize", "wait", "wave", "wider", "window", "windowframe", "windowtext", "words", "wrap", "wrap-reverse", "x-large", "x-small", "xor", "xx-large", "xx-small"],
  valueKeywords = keySet(valueKeywords_);
var allWords = documentTypes_.concat(mediaTypes_).concat(mediaFeatures_).concat(mediaValueKeywords_).concat(propertyKeywords_).concat(nonStandardPropertyKeywords_).concat(colorKeywords_).concat(valueKeywords_);
const keywords = {
  properties: propertyKeywords_,
  colors: colorKeywords_,
  fonts: fontProperties_,
  values: valueKeywords_,
  all: allWords
};
const defaults = {
  documentTypes: documentTypes,
  mediaTypes: mediaTypes,
  mediaFeatures: mediaFeatures,
  mediaValueKeywords: mediaValueKeywords,
  propertyKeywords: propertyKeywords,
  nonStandardPropertyKeywords: nonStandardPropertyKeywords,
  fontProperties: fontProperties,
  counterDescriptors: counterDescriptors,
  colorKeywords: colorKeywords,
  valueKeywords: valueKeywords,
  tokenHooks: {
    "/": function (stream, state) {
      if (!stream.eat("*")) return false;
      state.tokenize = tokenCComment;
      return tokenCComment(stream, state);
    }
  }
};
const css = mkCSS({
  name: "css"
});
function tokenCComment(stream, state) {
  var maybeEnd = false,
    ch;
  while ((ch = stream.next()) != null) {
    if (maybeEnd && ch == "/") {
      state.tokenize = null;
      break;
    }
    maybeEnd = ch == "*";
  }
  return ["comment", "comment"];
}
const sCSS = mkCSS({
  name: "scss",
  mediaTypes: mediaTypes,
  mediaFeatures: mediaFeatures,
  mediaValueKeywords: mediaValueKeywords,
  propertyKeywords: propertyKeywords,
  nonStandardPropertyKeywords: nonStandardPropertyKeywords,
  colorKeywords: colorKeywords,
  valueKeywords: valueKeywords,
  fontProperties: fontProperties,
  allowNested: true,
  lineComment: "//",
  tokenHooks: {
    "/": function (stream, state) {
      if (stream.eat("/")) {
        stream.skipToEnd();
        return ["comment", "comment"];
      } else if (stream.eat("*")) {
        state.tokenize = tokenCComment;
        return tokenCComment(stream, state);
      } else {
        return ["operator", "operator"];
      }
    },
    ":": function (stream) {
      if (stream.match(/^\s*\{/, false)) return [null, null];
      return false;
    },
    "$": function (stream) {
      stream.match(/^[\w-]+/);
      if (stream.match(/^\s*:/, false)) return ["def", "variable-definition"];
      return ["variableName.special", "variable"];
    },
    "#": function (stream) {
      if (!stream.eat("{")) return false;
      return [null, "interpolation"];
    }
  }
});
const less = mkCSS({
  name: "less",
  mediaTypes: mediaTypes,
  mediaFeatures: mediaFeatures,
  mediaValueKeywords: mediaValueKeywords,
  propertyKeywords: propertyKeywords,
  nonStandardPropertyKeywords: nonStandardPropertyKeywords,
  colorKeywords: colorKeywords,
  valueKeywords: valueKeywords,
  fontProperties: fontProperties,
  allowNested: true,
  lineComment: "//",
  tokenHooks: {
    "/": function (stream, state) {
      if (stream.eat("/")) {
        stream.skipToEnd();
        return ["comment", "comment"];
      } else if (stream.eat("*")) {
        state.tokenize = tokenCComment;
        return tokenCComment(stream, state);
      } else {
        return ["operator", "operator"];
      }
    },
    "@": function (stream) {
      if (stream.eat("{")) return [null, "interpolation"];
      if (stream.match(/^(charset|document|font-face|import|(-(moz|ms|o|webkit)-)?keyframes|media|namespace|page|supports)\b/i, false)) return false;
      stream.eatWhile(/[\w\\\-]/);
      if (stream.match(/^\s*:/, false)) return ["def", "variable-definition"];
      return ["variableName", "variable"];
    },
    "&": function () {
      return ["atom", "atom"];
    }
  }
});
const gss = mkCSS({
  name: "gss",
  documentTypes: documentTypes,
  mediaTypes: mediaTypes,
  mediaFeatures: mediaFeatures,
  propertyKeywords: propertyKeywords,
  nonStandardPropertyKeywords: nonStandardPropertyKeywords,
  fontProperties: fontProperties,
  counterDescriptors: counterDescriptors,
  colorKeywords: colorKeywords,
  valueKeywords: valueKeywords,
  supportsAtComponent: true,
  tokenHooks: {
    "/": function (stream, state) {
      if (!stream.eat("*")) return false;
      state.tokenize = tokenCComment;
      return tokenCComment(stream, state);
    }
  }
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNDU0NS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2Nzcy5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgZnVuY3Rpb24gbWtDU1MocGFyc2VyQ29uZmlnKSB7XG4gIHBhcnNlckNvbmZpZyA9IHtcbiAgICAuLi5kZWZhdWx0cyxcbiAgICAuLi5wYXJzZXJDb25maWdcbiAgfTtcbiAgdmFyIGlubGluZSA9IHBhcnNlckNvbmZpZy5pbmxpbmU7XG4gIHZhciB0b2tlbkhvb2tzID0gcGFyc2VyQ29uZmlnLnRva2VuSG9va3MsXG4gICAgZG9jdW1lbnRUeXBlcyA9IHBhcnNlckNvbmZpZy5kb2N1bWVudFR5cGVzIHx8IHt9LFxuICAgIG1lZGlhVHlwZXMgPSBwYXJzZXJDb25maWcubWVkaWFUeXBlcyB8fCB7fSxcbiAgICBtZWRpYUZlYXR1cmVzID0gcGFyc2VyQ29uZmlnLm1lZGlhRmVhdHVyZXMgfHwge30sXG4gICAgbWVkaWFWYWx1ZUtleXdvcmRzID0gcGFyc2VyQ29uZmlnLm1lZGlhVmFsdWVLZXl3b3JkcyB8fCB7fSxcbiAgICBwcm9wZXJ0eUtleXdvcmRzID0gcGFyc2VyQ29uZmlnLnByb3BlcnR5S2V5d29yZHMgfHwge30sXG4gICAgbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzID0gcGFyc2VyQ29uZmlnLm5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3JkcyB8fCB7fSxcbiAgICBmb250UHJvcGVydGllcyA9IHBhcnNlckNvbmZpZy5mb250UHJvcGVydGllcyB8fCB7fSxcbiAgICBjb3VudGVyRGVzY3JpcHRvcnMgPSBwYXJzZXJDb25maWcuY291bnRlckRlc2NyaXB0b3JzIHx8IHt9LFxuICAgIGNvbG9yS2V5d29yZHMgPSBwYXJzZXJDb25maWcuY29sb3JLZXl3b3JkcyB8fCB7fSxcbiAgICB2YWx1ZUtleXdvcmRzID0gcGFyc2VyQ29uZmlnLnZhbHVlS2V5d29yZHMgfHwge30sXG4gICAgYWxsb3dOZXN0ZWQgPSBwYXJzZXJDb25maWcuYWxsb3dOZXN0ZWQsXG4gICAgbGluZUNvbW1lbnQgPSBwYXJzZXJDb25maWcubGluZUNvbW1lbnQsXG4gICAgc3VwcG9ydHNBdENvbXBvbmVudCA9IHBhcnNlckNvbmZpZy5zdXBwb3J0c0F0Q29tcG9uZW50ID09PSB0cnVlLFxuICAgIGhpZ2hsaWdodE5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3JkcyA9IHBhcnNlckNvbmZpZy5oaWdobGlnaHROb25TdGFuZGFyZFByb3BlcnR5S2V5d29yZHMgIT09IGZhbHNlO1xuICB2YXIgdHlwZSwgb3ZlcnJpZGU7XG4gIGZ1bmN0aW9uIHJldChzdHlsZSwgdHApIHtcbiAgICB0eXBlID0gdHA7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9XG5cbiAgLy8gVG9rZW5pemVyc1xuXG4gIGZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgICBpZiAodG9rZW5Ib29rc1tjaF0pIHtcbiAgICAgIHZhciByZXN1bHQgPSB0b2tlbkhvb2tzW2NoXShzdHJlYW0sIHN0YXRlKTtcbiAgICAgIGlmIChyZXN1bHQgIT09IGZhbHNlKSByZXR1cm4gcmVzdWx0O1xuICAgIH1cbiAgICBpZiAoY2ggPT0gXCJAXCIpIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcXFxcXC1dLyk7XG4gICAgICByZXR1cm4gcmV0KFwiZGVmXCIsIHN0cmVhbS5jdXJyZW50KCkpO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCI9XCIgfHwgKGNoID09IFwiflwiIHx8IGNoID09IFwifFwiKSAmJiBzdHJlYW0uZWF0KFwiPVwiKSkge1xuICAgICAgcmV0dXJuIHJldChudWxsLCBcImNvbXBhcmVcIik7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBcIlxcXCJcIiB8fCBjaCA9PSBcIidcIikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBcIiNcIikge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFxcXFxcLV0vKTtcbiAgICAgIHJldHVybiByZXQoXCJhdG9tXCIsIFwiaGFzaFwiKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiIVwiKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15cXHMqXFx3Ki8pO1xuICAgICAgcmV0dXJuIHJldChcImtleXdvcmRcIiwgXCJpbXBvcnRhbnRcIik7XG4gICAgfSBlbHNlIGlmICgvXFxkLy50ZXN0KGNoKSB8fCBjaCA9PSBcIi5cIiAmJiBzdHJlYW0uZWF0KC9cXGQvKSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3LiVdLyk7XG4gICAgICByZXR1cm4gcmV0KFwibnVtYmVyXCIsIFwidW5pdFwiKTtcbiAgICB9IGVsc2UgaWYgKGNoID09PSBcIi1cIikge1xuICAgICAgaWYgKC9bXFxkLl0vLnRlc3Qoc3RyZWFtLnBlZWsoKSkpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3LiVdLyk7XG4gICAgICAgIHJldHVybiByZXQoXCJudW1iZXJcIiwgXCJ1bml0XCIpO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL14tW1xcd1xcXFxcXC1dKi8pKSB7XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcXFxcXC1dLyk7XG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goL15cXHMqOi8sIGZhbHNlKSkgcmV0dXJuIHJldChcImRlZlwiLCBcInZhcmlhYmxlLWRlZmluaXRpb25cIik7XG4gICAgICAgIHJldHVybiByZXQoXCJ2YXJpYWJsZU5hbWVcIiwgXCJ2YXJpYWJsZVwiKTtcbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eXFx3Ky0vKSkge1xuICAgICAgICByZXR1cm4gcmV0KFwibWV0YVwiLCBcIm1ldGFcIik7XG4gICAgICB9XG4gICAgfSBlbHNlIGlmICgvWywrPipcXC9dLy50ZXN0KGNoKSkge1xuICAgICAgcmV0dXJuIHJldChudWxsLCBcInNlbGVjdC1vcFwiKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiLlwiICYmIHN0cmVhbS5tYXRjaCgvXi0/W19hLXpdW19hLXowLTktXSovaSkpIHtcbiAgICAgIHJldHVybiByZXQoXCJxdWFsaWZpZXJcIiwgXCJxdWFsaWZpZXJcIik7XG4gICAgfSBlbHNlIGlmICgvWzo7e31cXFtcXF1cXChcXCldLy50ZXN0KGNoKSkge1xuICAgICAgcmV0dXJuIHJldChudWxsLCBjaCk7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL15bXFx3LS5dKyg/PVxcKCkvKSkge1xuICAgICAgaWYgKC9eKHVybCgtcHJlZml4KT98ZG9tYWlufHJlZ2V4cCkkL2kudGVzdChzdHJlYW0uY3VycmVudCgpKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuUGFyZW50aGVzaXplZDtcbiAgICAgIH1cbiAgICAgIHJldHVybiByZXQoXCJ2YXJpYWJsZU5hbWUuZnVuY3Rpb25cIiwgXCJ2YXJpYWJsZVwiKTtcbiAgICB9IGVsc2UgaWYgKC9bXFx3XFxcXFxcLV0vLnRlc3QoY2gpKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXFxcXFwtXS8pO1xuICAgICAgcmV0dXJuIHJldChcInByb3BlcnR5XCIsIFwid29yZFwiKTtcbiAgICB9IGVsc2Uge1xuICAgICAgcmV0dXJuIHJldChudWxsLCBudWxsKTtcbiAgICB9XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICAgIGNoO1xuICAgICAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgICAgaWYgKGNoID09IHF1b3RlICYmICFlc2NhcGVkKSB7XG4gICAgICAgICAgaWYgKHF1b3RlID09IFwiKVwiKSBzdHJlYW0uYmFja1VwKDEpO1xuICAgICAgICAgIGJyZWFrO1xuICAgICAgICB9XG4gICAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBjaCA9PSBcIlxcXFxcIjtcbiAgICAgIH1cbiAgICAgIGlmIChjaCA9PSBxdW90ZSB8fCAhZXNjYXBlZCAmJiBxdW90ZSAhPSBcIilcIikgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgICAgcmV0dXJuIHJldChcInN0cmluZ1wiLCBcInN0cmluZ1wiKTtcbiAgICB9O1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuUGFyZW50aGVzaXplZChzdHJlYW0sIHN0YXRlKSB7XG4gICAgc3RyZWFtLm5leHQoKTsgLy8gTXVzdCBiZSAnKCdcbiAgICBpZiAoIXN0cmVhbS5tYXRjaCgvXlxccypbXFxcIlxcJyldLywgZmFsc2UpKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKFwiKVwiKTtlbHNlIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICByZXR1cm4gcmV0KG51bGwsIFwiKFwiKTtcbiAgfVxuXG4gIC8vIENvbnRleHQgbWFuYWdlbWVudFxuXG4gIGZ1bmN0aW9uIENvbnRleHQodHlwZSwgaW5kZW50LCBwcmV2KSB7XG4gICAgdGhpcy50eXBlID0gdHlwZTtcbiAgICB0aGlzLmluZGVudCA9IGluZGVudDtcbiAgICB0aGlzLnByZXYgPSBwcmV2O1xuICB9XG4gIGZ1bmN0aW9uIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIHR5cGUsIGluZGVudCkge1xuICAgIHN0YXRlLmNvbnRleHQgPSBuZXcgQ29udGV4dCh0eXBlLCBzdHJlYW0uaW5kZW50YXRpb24oKSArIChpbmRlbnQgPT09IGZhbHNlID8gMCA6IHN0cmVhbS5pbmRlbnRVbml0KSwgc3RhdGUuY29udGV4dCk7XG4gICAgcmV0dXJuIHR5cGU7XG4gIH1cbiAgZnVuY3Rpb24gcG9wQ29udGV4dChzdGF0ZSkge1xuICAgIGlmIChzdGF0ZS5jb250ZXh0LnByZXYpIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG4gICAgcmV0dXJuIHN0YXRlLmNvbnRleHQudHlwZTtcbiAgfVxuICBmdW5jdGlvbiBwYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgICByZXR1cm4gc3RhdGVzW3N0YXRlLmNvbnRleHQudHlwZV0odHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgZnVuY3Rpb24gcG9wQW5kUGFzcyh0eXBlLCBzdHJlYW0sIHN0YXRlLCBuKSB7XG4gICAgZm9yICh2YXIgaSA9IG4gfHwgMTsgaSA+IDA7IGktLSkgc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbiAgICByZXR1cm4gcGFzcyh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbiAgfVxuXG4gIC8vIFBhcnNlclxuXG4gIGZ1bmN0aW9uIHdvcmRBc1ZhbHVlKHN0cmVhbSkge1xuICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKS50b0xvd2VyQ2FzZSgpO1xuICAgIGlmICh2YWx1ZUtleXdvcmRzLmhhc093blByb3BlcnR5KHdvcmQpKSBvdmVycmlkZSA9IFwiYXRvbVwiO2Vsc2UgaWYgKGNvbG9yS2V5d29yZHMuaGFzT3duUHJvcGVydHkod29yZCkpIG92ZXJyaWRlID0gXCJrZXl3b3JkXCI7ZWxzZSBvdmVycmlkZSA9IFwidmFyaWFibGVcIjtcbiAgfVxuICB2YXIgc3RhdGVzID0ge307XG4gIHN0YXRlcy50b3AgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwie1wiKSB7XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgICB9IGVsc2UgaWYgKHR5cGUgPT0gXCJ9XCIgJiYgc3RhdGUuY29udGV4dC5wcmV2KSB7XG4gICAgICByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChzdXBwb3J0c0F0Q29tcG9uZW50ICYmIC9AY29tcG9uZW50L2kudGVzdCh0eXBlKSkge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYXRDb21wb25lbnRCbG9ja1wiKTtcbiAgICB9IGVsc2UgaWYgKC9eQCgtbW96LSk/ZG9jdW1lbnQkL2kudGVzdCh0eXBlKSkge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiZG9jdW1lbnRUeXBlc1wiKTtcbiAgICB9IGVsc2UgaWYgKC9eQChtZWRpYXxzdXBwb3J0c3woLW1vei0pP2RvY3VtZW50fGltcG9ydCkkL2kudGVzdCh0eXBlKSkge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYXRCbG9ja1wiKTtcbiAgICB9IGVsc2UgaWYgKC9eQChmb250LWZhY2V8Y291bnRlci1zdHlsZSkvaS50ZXN0KHR5cGUpKSB7XG4gICAgICBzdGF0ZS5zdGF0ZUFyZyA9IHR5cGU7XG4gICAgICByZXR1cm4gXCJyZXN0cmljdGVkX2F0QmxvY2tfYmVmb3JlXCI7XG4gICAgfSBlbHNlIGlmICgvXkAoLShtb3p8bXN8b3x3ZWJraXQpLSk/a2V5ZnJhbWVzJC9pLnRlc3QodHlwZSkpIHtcbiAgICAgIHJldHVybiBcImtleWZyYW1lc1wiO1xuICAgIH0gZWxzZSBpZiAodHlwZSAmJiB0eXBlLmNoYXJBdCgwKSA9PSBcIkBcIikge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYXRcIik7XG4gICAgfSBlbHNlIGlmICh0eXBlID09IFwiaGFzaFwiKSB7XG4gICAgICBvdmVycmlkZSA9IFwiYnVpbHRpblwiO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcIndvcmRcIikge1xuICAgICAgb3ZlcnJpZGUgPSBcInRhZ1wiO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcInZhcmlhYmxlLWRlZmluaXRpb25cIikge1xuICAgICAgcmV0dXJuIFwibWF5YmVwcm9wXCI7XG4gICAgfSBlbHNlIGlmICh0eXBlID09IFwiaW50ZXJwb2xhdGlvblwiKSB7XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJpbnRlcnBvbGF0aW9uXCIpO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcIjpcIikge1xuICAgICAgcmV0dXJuIFwicHNldWRvXCI7XG4gICAgfSBlbHNlIGlmIChhbGxvd05lc3RlZCAmJiB0eXBlID09IFwiKFwiKSB7XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJwYXJlbnNcIik7XG4gICAgfVxuICAgIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIH07XG4gIHN0YXRlcy5ibG9jayA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIHtcbiAgICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKS50b0xvd2VyQ2FzZSgpO1xuICAgICAgaWYgKHByb3BlcnR5S2V5d29yZHMuaGFzT3duUHJvcGVydHkod29yZCkpIHtcbiAgICAgICAgb3ZlcnJpZGUgPSBcInByb3BlcnR5XCI7XG4gICAgICAgIHJldHVybiBcIm1heWJlcHJvcFwiO1xuICAgICAgfSBlbHNlIGlmIChub25TdGFuZGFyZFByb3BlcnR5S2V5d29yZHMuaGFzT3duUHJvcGVydHkod29yZCkpIHtcbiAgICAgICAgb3ZlcnJpZGUgPSBoaWdobGlnaHROb25TdGFuZGFyZFByb3BlcnR5S2V5d29yZHMgPyBcInN0cmluZy5zcGVjaWFsXCIgOiBcInByb3BlcnR5XCI7XG4gICAgICAgIHJldHVybiBcIm1heWJlcHJvcFwiO1xuICAgICAgfSBlbHNlIGlmIChhbGxvd05lc3RlZCkge1xuICAgICAgICBvdmVycmlkZSA9IHN0cmVhbS5tYXRjaCgvXlxccyo6KD86XFxzfCQpLywgZmFsc2UpID8gXCJwcm9wZXJ0eVwiIDogXCJ0YWdcIjtcbiAgICAgICAgcmV0dXJuIFwiYmxvY2tcIjtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIG92ZXJyaWRlID0gXCJlcnJvclwiO1xuICAgICAgICByZXR1cm4gXCJtYXliZXByb3BcIjtcbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKHR5cGUgPT0gXCJtZXRhXCIpIHtcbiAgICAgIHJldHVybiBcImJsb2NrXCI7XG4gICAgfSBlbHNlIGlmICghYWxsb3dOZXN0ZWQgJiYgKHR5cGUgPT0gXCJoYXNoXCIgfHwgdHlwZSA9PSBcInF1YWxpZmllclwiKSkge1xuICAgICAgb3ZlcnJpZGUgPSBcImVycm9yXCI7XG4gICAgICByZXR1cm4gXCJibG9ja1wiO1xuICAgIH0gZWxzZSB7XG4gICAgICByZXR1cm4gc3RhdGVzLnRvcCh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gIH07XG4gIHN0YXRlcy5tYXliZXByb3AgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJwcm9wXCIpO1xuICAgIHJldHVybiBwYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICB9O1xuICBzdGF0ZXMucHJvcCA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCI7XCIpIHJldHVybiBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICBpZiAodHlwZSA9PSBcIntcIiAmJiBhbGxvd05lc3RlZCkgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwicHJvcEJsb2NrXCIpO1xuICAgIGlmICh0eXBlID09IFwifVwiIHx8IHR5cGUgPT0gXCJ7XCIpIHJldHVybiBwb3BBbmRQYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJwYXJlbnNcIik7XG4gICAgaWYgKHR5cGUgPT0gXCJoYXNoXCIgJiYgIS9eIyhbMC05YS1mQS1GXXszLDR9fFswLTlhLWZBLUZdezZ9fFswLTlhLWZBLUZdezh9KSQvLnRlc3Qoc3RyZWFtLmN1cnJlbnQoKSkpIHtcbiAgICAgIG92ZXJyaWRlID0gXCJlcnJvclwiO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcIndvcmRcIikge1xuICAgICAgd29yZEFzVmFsdWUoc3RyZWFtKTtcbiAgICB9IGVsc2UgaWYgKHR5cGUgPT0gXCJpbnRlcnBvbGF0aW9uXCIpIHtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImludGVycG9sYXRpb25cIik7XG4gICAgfVxuICAgIHJldHVybiBcInByb3BcIjtcbiAgfTtcbiAgc3RhdGVzLnByb3BCbG9jayA9IGZ1bmN0aW9uICh0eXBlLCBfc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwifVwiKSByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIHtcbiAgICAgIG92ZXJyaWRlID0gXCJwcm9wZXJ0eVwiO1xuICAgICAgcmV0dXJuIFwibWF5YmVwcm9wXCI7XG4gICAgfVxuICAgIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIH07XG4gIHN0YXRlcy5wYXJlbnMgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwie1wiIHx8IHR5cGUgPT0gXCJ9XCIpIHJldHVybiBwb3BBbmRQYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmICh0eXBlID09IFwiKVwiKSByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcInBhcmVuc1wiKTtcbiAgICBpZiAodHlwZSA9PSBcImludGVycG9sYXRpb25cIikgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiaW50ZXJwb2xhdGlvblwiKTtcbiAgICBpZiAodHlwZSA9PSBcIndvcmRcIikgd29yZEFzVmFsdWUoc3RyZWFtKTtcbiAgICByZXR1cm4gXCJwYXJlbnNcIjtcbiAgfTtcbiAgc3RhdGVzLnBzZXVkbyA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJtZXRhXCIpIHJldHVybiBcInBzZXVkb1wiO1xuICAgIGlmICh0eXBlID09IFwid29yZFwiKSB7XG4gICAgICBvdmVycmlkZSA9IFwidmFyaWFibGVOYW1lLmNvbnN0YW50XCI7XG4gICAgICByZXR1cm4gc3RhdGUuY29udGV4dC50eXBlO1xuICAgIH1cbiAgICByZXR1cm4gcGFzcyh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbiAgfTtcbiAgc3RhdGVzLmRvY3VtZW50VHlwZXMgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwid29yZFwiICYmIGRvY3VtZW50VHlwZXMuaGFzT3duUHJvcGVydHkoc3RyZWFtLmN1cnJlbnQoKSkpIHtcbiAgICAgIG92ZXJyaWRlID0gXCJ0YWdcIjtcbiAgICAgIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gICAgfSBlbHNlIHtcbiAgICAgIHJldHVybiBzdGF0ZXMuYXRCbG9jayh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gIH07XG4gIHN0YXRlcy5hdEJsb2NrID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIihcIikgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYXRCbG9ja19wYXJlbnNcIik7XG4gICAgaWYgKHR5cGUgPT0gXCJ9XCIgfHwgdHlwZSA9PSBcIjtcIikgcmV0dXJuIHBvcEFuZFBhc3ModHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ7XCIpIHJldHVybiBwb3BDb250ZXh0KHN0YXRlKSAmJiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBhbGxvd05lc3RlZCA/IFwiYmxvY2tcIiA6IFwidG9wXCIpO1xuICAgIGlmICh0eXBlID09IFwiaW50ZXJwb2xhdGlvblwiKSByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJpbnRlcnBvbGF0aW9uXCIpO1xuICAgIGlmICh0eXBlID09IFwid29yZFwiKSB7XG4gICAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCkudG9Mb3dlckNhc2UoKTtcbiAgICAgIGlmICh3b3JkID09IFwib25seVwiIHx8IHdvcmQgPT0gXCJub3RcIiB8fCB3b3JkID09IFwiYW5kXCIgfHwgd29yZCA9PSBcIm9yXCIpIG92ZXJyaWRlID0gXCJrZXl3b3JkXCI7ZWxzZSBpZiAobWVkaWFUeXBlcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSkgb3ZlcnJpZGUgPSBcImF0dHJpYnV0ZVwiO2Vsc2UgaWYgKG1lZGlhRmVhdHVyZXMuaGFzT3duUHJvcGVydHkod29yZCkpIG92ZXJyaWRlID0gXCJwcm9wZXJ0eVwiO2Vsc2UgaWYgKG1lZGlhVmFsdWVLZXl3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSkgb3ZlcnJpZGUgPSBcImtleXdvcmRcIjtlbHNlIGlmIChwcm9wZXJ0eUtleXdvcmRzLmhhc093blByb3BlcnR5KHdvcmQpKSBvdmVycmlkZSA9IFwicHJvcGVydHlcIjtlbHNlIGlmIChub25TdGFuZGFyZFByb3BlcnR5S2V5d29yZHMuaGFzT3duUHJvcGVydHkod29yZCkpIG92ZXJyaWRlID0gaGlnaGxpZ2h0Tm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzID8gXCJzdHJpbmcuc3BlY2lhbFwiIDogXCJwcm9wZXJ0eVwiO2Vsc2UgaWYgKHZhbHVlS2V5d29yZHMuaGFzT3duUHJvcGVydHkod29yZCkpIG92ZXJyaWRlID0gXCJhdG9tXCI7ZWxzZSBpZiAoY29sb3JLZXl3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSkgb3ZlcnJpZGUgPSBcImtleXdvcmRcIjtlbHNlIG92ZXJyaWRlID0gXCJlcnJvclwiO1xuICAgIH1cbiAgICByZXR1cm4gc3RhdGUuY29udGV4dC50eXBlO1xuICB9O1xuICBzdGF0ZXMuYXRDb21wb25lbnRCbG9jayA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJ9XCIpIHJldHVybiBwb3BBbmRQYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmICh0eXBlID09IFwie1wiKSByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSkgJiYgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgYWxsb3dOZXN0ZWQgPyBcImJsb2NrXCIgOiBcInRvcFwiLCBmYWxzZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIG92ZXJyaWRlID0gXCJlcnJvclwiO1xuICAgIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIH07XG4gIHN0YXRlcy5hdEJsb2NrX3BhcmVucyA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCIpXCIpIHJldHVybiBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICBpZiAodHlwZSA9PSBcIntcIiB8fCB0eXBlID09IFwifVwiKSByZXR1cm4gcG9wQW5kUGFzcyh0eXBlLCBzdHJlYW0sIHN0YXRlLCAyKTtcbiAgICByZXR1cm4gc3RhdGVzLmF0QmxvY2sodHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG4gIH07XG4gIHN0YXRlcy5yZXN0cmljdGVkX2F0QmxvY2tfYmVmb3JlID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIntcIikgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwicmVzdHJpY3RlZF9hdEJsb2NrXCIpO1xuICAgIGlmICh0eXBlID09IFwid29yZFwiICYmIHN0YXRlLnN0YXRlQXJnID09IFwiQGNvdW50ZXItc3R5bGVcIikge1xuICAgICAgb3ZlcnJpZGUgPSBcInZhcmlhYmxlXCI7XG4gICAgICByZXR1cm4gXCJyZXN0cmljdGVkX2F0QmxvY2tfYmVmb3JlXCI7XG4gICAgfVxuICAgIHJldHVybiBwYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICB9O1xuICBzdGF0ZXMucmVzdHJpY3RlZF9hdEJsb2NrID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIn1cIikge1xuICAgICAgc3RhdGUuc3RhdGVBcmcgPSBudWxsO1xuICAgICAgcmV0dXJuIHBvcENvbnRleHQoc3RhdGUpO1xuICAgIH1cbiAgICBpZiAodHlwZSA9PSBcIndvcmRcIikge1xuICAgICAgaWYgKHN0YXRlLnN0YXRlQXJnID09IFwiQGZvbnQtZmFjZVwiICYmICFmb250UHJvcGVydGllcy5oYXNPd25Qcm9wZXJ0eShzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCkpIHx8IHN0YXRlLnN0YXRlQXJnID09IFwiQGNvdW50ZXItc3R5bGVcIiAmJiAhY291bnRlckRlc2NyaXB0b3JzLmhhc093blByb3BlcnR5KHN0cmVhbS5jdXJyZW50KCkudG9Mb3dlckNhc2UoKSkpIG92ZXJyaWRlID0gXCJlcnJvclwiO2Vsc2Ugb3ZlcnJpZGUgPSBcInByb3BlcnR5XCI7XG4gICAgICByZXR1cm4gXCJtYXliZXByb3BcIjtcbiAgICB9XG4gICAgcmV0dXJuIFwicmVzdHJpY3RlZF9hdEJsb2NrXCI7XG4gIH07XG4gIHN0YXRlcy5rZXlmcmFtZXMgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwid29yZFwiKSB7XG4gICAgICBvdmVycmlkZSA9IFwidmFyaWFibGVcIjtcbiAgICAgIHJldHVybiBcImtleWZyYW1lc1wiO1xuICAgIH1cbiAgICBpZiAodHlwZSA9PSBcIntcIikgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwidG9wXCIpO1xuICAgIHJldHVybiBwYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICB9O1xuICBzdGF0ZXMuYXQgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICh0eXBlID09IFwiO1wiKSByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ7XCIgfHwgdHlwZSA9PSBcIn1cIikgcmV0dXJuIHBvcEFuZFBhc3ModHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIG92ZXJyaWRlID0gXCJ0YWdcIjtlbHNlIGlmICh0eXBlID09IFwiaGFzaFwiKSBvdmVycmlkZSA9IFwiYnVpbHRpblwiO1xuICAgIHJldHVybiBcImF0XCI7XG4gIH07XG4gIHN0YXRlcy5pbnRlcnBvbGF0aW9uID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIn1cIikgcmV0dXJuIHBvcENvbnRleHQoc3RhdGUpO1xuICAgIGlmICh0eXBlID09IFwie1wiIHx8IHR5cGUgPT0gXCI7XCIpIHJldHVybiBwb3BBbmRQYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmICh0eXBlID09IFwid29yZFwiKSBvdmVycmlkZSA9IFwidmFyaWFibGVcIjtlbHNlIGlmICh0eXBlICE9IFwidmFyaWFibGVcIiAmJiB0eXBlICE9IFwiKFwiICYmIHR5cGUgIT0gXCIpXCIpIG92ZXJyaWRlID0gXCJlcnJvclwiO1xuICAgIHJldHVybiBcImludGVycG9sYXRpb25cIjtcbiAgfTtcbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBwYXJzZXJDb25maWcubmFtZSxcbiAgICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4ge1xuICAgICAgICB0b2tlbml6ZTogbnVsbCxcbiAgICAgICAgc3RhdGU6IGlubGluZSA/IFwiYmxvY2tcIiA6IFwidG9wXCIsXG4gICAgICAgIHN0YXRlQXJnOiBudWxsLFxuICAgICAgICBjb250ZXh0OiBuZXcgQ29udGV4dChpbmxpbmUgPyBcImJsb2NrXCIgOiBcInRvcFwiLCAwLCBudWxsKVxuICAgICAgfTtcbiAgICB9LFxuICAgIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgaWYgKCFzdGF0ZS50b2tlbml6ZSAmJiBzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgICB2YXIgc3R5bGUgPSAoc3RhdGUudG9rZW5pemUgfHwgdG9rZW5CYXNlKShzdHJlYW0sIHN0YXRlKTtcbiAgICAgIGlmIChzdHlsZSAmJiB0eXBlb2Ygc3R5bGUgPT0gXCJvYmplY3RcIikge1xuICAgICAgICB0eXBlID0gc3R5bGVbMV07XG4gICAgICAgIHN0eWxlID0gc3R5bGVbMF07XG4gICAgICB9XG4gICAgICBvdmVycmlkZSA9IHN0eWxlO1xuICAgICAgaWYgKHR5cGUgIT0gXCJjb21tZW50XCIpIHN0YXRlLnN0YXRlID0gc3RhdGVzW3N0YXRlLnN0YXRlXSh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbiAgICAgIHJldHVybiBvdmVycmlkZTtcbiAgICB9LFxuICAgIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGlDeCkge1xuICAgICAgdmFyIGN4ID0gc3RhdGUuY29udGV4dCxcbiAgICAgICAgY2ggPSB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKTtcbiAgICAgIHZhciBpbmRlbnQgPSBjeC5pbmRlbnQ7XG4gICAgICBpZiAoY3gudHlwZSA9PSBcInByb3BcIiAmJiAoY2ggPT0gXCJ9XCIgfHwgY2ggPT0gXCIpXCIpKSBjeCA9IGN4LnByZXY7XG4gICAgICBpZiAoY3gucHJldikge1xuICAgICAgICBpZiAoY2ggPT0gXCJ9XCIgJiYgKGN4LnR5cGUgPT0gXCJibG9ja1wiIHx8IGN4LnR5cGUgPT0gXCJ0b3BcIiB8fCBjeC50eXBlID09IFwiaW50ZXJwb2xhdGlvblwiIHx8IGN4LnR5cGUgPT0gXCJyZXN0cmljdGVkX2F0QmxvY2tcIikpIHtcbiAgICAgICAgICAvLyBSZXN1bWUgaW5kZW50YXRpb24gZnJvbSBwYXJlbnQgY29udGV4dC5cbiAgICAgICAgICBjeCA9IGN4LnByZXY7XG4gICAgICAgICAgaW5kZW50ID0gY3guaW5kZW50O1xuICAgICAgICB9IGVsc2UgaWYgKGNoID09IFwiKVwiICYmIChjeC50eXBlID09IFwicGFyZW5zXCIgfHwgY3gudHlwZSA9PSBcImF0QmxvY2tfcGFyZW5zXCIpIHx8IGNoID09IFwie1wiICYmIChjeC50eXBlID09IFwiYXRcIiB8fCBjeC50eXBlID09IFwiYXRCbG9ja1wiKSkge1xuICAgICAgICAgIC8vIERlZGVudCByZWxhdGl2ZSB0byBjdXJyZW50IGNvbnRleHQuXG4gICAgICAgICAgaW5kZW50ID0gTWF0aC5tYXgoMCwgY3guaW5kZW50IC0gaUN4LnVuaXQpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICByZXR1cm4gaW5kZW50O1xuICAgIH0sXG4gICAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgICBpbmRlbnRPbklucHV0OiAvXlxccypcXH0kLyxcbiAgICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgICAgbGluZTogbGluZUNvbW1lbnQsXG4gICAgICAgIGJsb2NrOiB7XG4gICAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgICAgfVxuICAgICAgfSxcbiAgICAgIGF1dG9jb21wbGV0ZTogYWxsV29yZHNcbiAgICB9XG4gIH07XG59XG47XG5mdW5jdGlvbiBrZXlTZXQoYXJyYXkpIHtcbiAgdmFyIGtleXMgPSB7fTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnJheS5sZW5ndGg7ICsraSkge1xuICAgIGtleXNbYXJyYXlbaV0udG9Mb3dlckNhc2UoKV0gPSB0cnVlO1xuICB9XG4gIHJldHVybiBrZXlzO1xufVxudmFyIGRvY3VtZW50VHlwZXNfID0gW1wiZG9tYWluXCIsIFwicmVnZXhwXCIsIFwidXJsXCIsIFwidXJsLXByZWZpeFwiXSxcbiAgZG9jdW1lbnRUeXBlcyA9IGtleVNldChkb2N1bWVudFR5cGVzXyk7XG52YXIgbWVkaWFUeXBlc18gPSBbXCJhbGxcIiwgXCJhdXJhbFwiLCBcImJyYWlsbGVcIiwgXCJoYW5kaGVsZFwiLCBcInByaW50XCIsIFwicHJvamVjdGlvblwiLCBcInNjcmVlblwiLCBcInR0eVwiLCBcInR2XCIsIFwiZW1ib3NzZWRcIl0sXG4gIG1lZGlhVHlwZXMgPSBrZXlTZXQobWVkaWFUeXBlc18pO1xudmFyIG1lZGlhRmVhdHVyZXNfID0gW1wid2lkdGhcIiwgXCJtaW4td2lkdGhcIiwgXCJtYXgtd2lkdGhcIiwgXCJoZWlnaHRcIiwgXCJtaW4taGVpZ2h0XCIsIFwibWF4LWhlaWdodFwiLCBcImRldmljZS13aWR0aFwiLCBcIm1pbi1kZXZpY2Utd2lkdGhcIiwgXCJtYXgtZGV2aWNlLXdpZHRoXCIsIFwiZGV2aWNlLWhlaWdodFwiLCBcIm1pbi1kZXZpY2UtaGVpZ2h0XCIsIFwibWF4LWRldmljZS1oZWlnaHRcIiwgXCJhc3BlY3QtcmF0aW9cIiwgXCJtaW4tYXNwZWN0LXJhdGlvXCIsIFwibWF4LWFzcGVjdC1yYXRpb1wiLCBcImRldmljZS1hc3BlY3QtcmF0aW9cIiwgXCJtaW4tZGV2aWNlLWFzcGVjdC1yYXRpb1wiLCBcIm1heC1kZXZpY2UtYXNwZWN0LXJhdGlvXCIsIFwiY29sb3JcIiwgXCJtaW4tY29sb3JcIiwgXCJtYXgtY29sb3JcIiwgXCJjb2xvci1pbmRleFwiLCBcIm1pbi1jb2xvci1pbmRleFwiLCBcIm1heC1jb2xvci1pbmRleFwiLCBcIm1vbm9jaHJvbWVcIiwgXCJtaW4tbW9ub2Nocm9tZVwiLCBcIm1heC1tb25vY2hyb21lXCIsIFwicmVzb2x1dGlvblwiLCBcIm1pbi1yZXNvbHV0aW9uXCIsIFwibWF4LXJlc29sdXRpb25cIiwgXCJzY2FuXCIsIFwiZ3JpZFwiLCBcIm9yaWVudGF0aW9uXCIsIFwiZGV2aWNlLXBpeGVsLXJhdGlvXCIsIFwibWluLWRldmljZS1waXhlbC1yYXRpb1wiLCBcIm1heC1kZXZpY2UtcGl4ZWwtcmF0aW9cIiwgXCJwb2ludGVyXCIsIFwiYW55LXBvaW50ZXJcIiwgXCJob3ZlclwiLCBcImFueS1ob3ZlclwiLCBcInByZWZlcnMtY29sb3Itc2NoZW1lXCIsIFwiZHluYW1pYy1yYW5nZVwiLCBcInZpZGVvLWR5bmFtaWMtcmFuZ2VcIl0sXG4gIG1lZGlhRmVhdHVyZXMgPSBrZXlTZXQobWVkaWFGZWF0dXJlc18pO1xudmFyIG1lZGlhVmFsdWVLZXl3b3Jkc18gPSBbXCJsYW5kc2NhcGVcIiwgXCJwb3J0cmFpdFwiLCBcIm5vbmVcIiwgXCJjb2Fyc2VcIiwgXCJmaW5lXCIsIFwib24tZGVtYW5kXCIsIFwiaG92ZXJcIiwgXCJpbnRlcmxhY2VcIiwgXCJwcm9ncmVzc2l2ZVwiLCBcImRhcmtcIiwgXCJsaWdodFwiLCBcInN0YW5kYXJkXCIsIFwiaGlnaFwiXSxcbiAgbWVkaWFWYWx1ZUtleXdvcmRzID0ga2V5U2V0KG1lZGlhVmFsdWVLZXl3b3Jkc18pO1xudmFyIHByb3BlcnR5S2V5d29yZHNfID0gW1wiYWxpZ24tY29udGVudFwiLCBcImFsaWduLWl0ZW1zXCIsIFwiYWxpZ24tc2VsZlwiLCBcImFsaWdubWVudC1hZGp1c3RcIiwgXCJhbGlnbm1lbnQtYmFzZWxpbmVcIiwgXCJhbGxcIiwgXCJhbmNob3ItcG9pbnRcIiwgXCJhbmltYXRpb25cIiwgXCJhbmltYXRpb24tZGVsYXlcIiwgXCJhbmltYXRpb24tZGlyZWN0aW9uXCIsIFwiYW5pbWF0aW9uLWR1cmF0aW9uXCIsIFwiYW5pbWF0aW9uLWZpbGwtbW9kZVwiLCBcImFuaW1hdGlvbi1pdGVyYXRpb24tY291bnRcIiwgXCJhbmltYXRpb24tbmFtZVwiLCBcImFuaW1hdGlvbi1wbGF5LXN0YXRlXCIsIFwiYW5pbWF0aW9uLXRpbWluZy1mdW5jdGlvblwiLCBcImFwcGVhcmFuY2VcIiwgXCJhemltdXRoXCIsIFwiYmFja2Ryb3AtZmlsdGVyXCIsIFwiYmFja2ZhY2UtdmlzaWJpbGl0eVwiLCBcImJhY2tncm91bmRcIiwgXCJiYWNrZ3JvdW5kLWF0dGFjaG1lbnRcIiwgXCJiYWNrZ3JvdW5kLWJsZW5kLW1vZGVcIiwgXCJiYWNrZ3JvdW5kLWNsaXBcIiwgXCJiYWNrZ3JvdW5kLWNvbG9yXCIsIFwiYmFja2dyb3VuZC1pbWFnZVwiLCBcImJhY2tncm91bmQtb3JpZ2luXCIsIFwiYmFja2dyb3VuZC1wb3NpdGlvblwiLCBcImJhY2tncm91bmQtcG9zaXRpb24teFwiLCBcImJhY2tncm91bmQtcG9zaXRpb24teVwiLCBcImJhY2tncm91bmQtcmVwZWF0XCIsIFwiYmFja2dyb3VuZC1zaXplXCIsIFwiYmFzZWxpbmUtc2hpZnRcIiwgXCJiaW5kaW5nXCIsIFwiYmxlZWRcIiwgXCJibG9jay1zaXplXCIsIFwiYm9va21hcmstbGFiZWxcIiwgXCJib29rbWFyay1sZXZlbFwiLCBcImJvb2ttYXJrLXN0YXRlXCIsIFwiYm9va21hcmstdGFyZ2V0XCIsIFwiYm9yZGVyXCIsIFwiYm9yZGVyLWJvdHRvbVwiLCBcImJvcmRlci1ib3R0b20tY29sb3JcIiwgXCJib3JkZXItYm90dG9tLWxlZnQtcmFkaXVzXCIsIFwiYm9yZGVyLWJvdHRvbS1yaWdodC1yYWRpdXNcIiwgXCJib3JkZXItYm90dG9tLXN0eWxlXCIsIFwiYm9yZGVyLWJvdHRvbS13aWR0aFwiLCBcImJvcmRlci1jb2xsYXBzZVwiLCBcImJvcmRlci1jb2xvclwiLCBcImJvcmRlci1pbWFnZVwiLCBcImJvcmRlci1pbWFnZS1vdXRzZXRcIiwgXCJib3JkZXItaW1hZ2UtcmVwZWF0XCIsIFwiYm9yZGVyLWltYWdlLXNsaWNlXCIsIFwiYm9yZGVyLWltYWdlLXNvdXJjZVwiLCBcImJvcmRlci1pbWFnZS13aWR0aFwiLCBcImJvcmRlci1sZWZ0XCIsIFwiYm9yZGVyLWxlZnQtY29sb3JcIiwgXCJib3JkZXItbGVmdC1zdHlsZVwiLCBcImJvcmRlci1sZWZ0LXdpZHRoXCIsIFwiYm9yZGVyLXJhZGl1c1wiLCBcImJvcmRlci1yaWdodFwiLCBcImJvcmRlci1yaWdodC1jb2xvclwiLCBcImJvcmRlci1yaWdodC1zdHlsZVwiLCBcImJvcmRlci1yaWdodC13aWR0aFwiLCBcImJvcmRlci1zcGFjaW5nXCIsIFwiYm9yZGVyLXN0eWxlXCIsIFwiYm9yZGVyLXRvcFwiLCBcImJvcmRlci10b3AtY29sb3JcIiwgXCJib3JkZXItdG9wLWxlZnQtcmFkaXVzXCIsIFwiYm9yZGVyLXRvcC1yaWdodC1yYWRpdXNcIiwgXCJib3JkZXItdG9wLXN0eWxlXCIsIFwiYm9yZGVyLXRvcC13aWR0aFwiLCBcImJvcmRlci13aWR0aFwiLCBcImJvdHRvbVwiLCBcImJveC1kZWNvcmF0aW9uLWJyZWFrXCIsIFwiYm94LXNoYWRvd1wiLCBcImJveC1zaXppbmdcIiwgXCJicmVhay1hZnRlclwiLCBcImJyZWFrLWJlZm9yZVwiLCBcImJyZWFrLWluc2lkZVwiLCBcImNhcHRpb24tc2lkZVwiLCBcImNhcmV0LWNvbG9yXCIsIFwiY2xlYXJcIiwgXCJjbGlwXCIsIFwiY29sb3JcIiwgXCJjb2xvci1wcm9maWxlXCIsIFwiY29sdW1uLWNvdW50XCIsIFwiY29sdW1uLWZpbGxcIiwgXCJjb2x1bW4tZ2FwXCIsIFwiY29sdW1uLXJ1bGVcIiwgXCJjb2x1bW4tcnVsZS1jb2xvclwiLCBcImNvbHVtbi1ydWxlLXN0eWxlXCIsIFwiY29sdW1uLXJ1bGUtd2lkdGhcIiwgXCJjb2x1bW4tc3BhblwiLCBcImNvbHVtbi13aWR0aFwiLCBcImNvbHVtbnNcIiwgXCJjb250YWluXCIsIFwiY29udGVudFwiLCBcImNvdW50ZXItaW5jcmVtZW50XCIsIFwiY291bnRlci1yZXNldFwiLCBcImNyb3BcIiwgXCJjdWVcIiwgXCJjdWUtYWZ0ZXJcIiwgXCJjdWUtYmVmb3JlXCIsIFwiY3Vyc29yXCIsIFwiZGlyZWN0aW9uXCIsIFwiZGlzcGxheVwiLCBcImRvbWluYW50LWJhc2VsaW5lXCIsIFwiZHJvcC1pbml0aWFsLWFmdGVyLWFkanVzdFwiLCBcImRyb3AtaW5pdGlhbC1hZnRlci1hbGlnblwiLCBcImRyb3AtaW5pdGlhbC1iZWZvcmUtYWRqdXN0XCIsIFwiZHJvcC1pbml0aWFsLWJlZm9yZS1hbGlnblwiLCBcImRyb3AtaW5pdGlhbC1zaXplXCIsIFwiZHJvcC1pbml0aWFsLXZhbHVlXCIsIFwiZWxldmF0aW9uXCIsIFwiZW1wdHktY2VsbHNcIiwgXCJmaXRcIiwgXCJmaXQtY29udGVudFwiLCBcImZpdC1wb3NpdGlvblwiLCBcImZsZXhcIiwgXCJmbGV4LWJhc2lzXCIsIFwiZmxleC1kaXJlY3Rpb25cIiwgXCJmbGV4LWZsb3dcIiwgXCJmbGV4LWdyb3dcIiwgXCJmbGV4LXNocmlua1wiLCBcImZsZXgtd3JhcFwiLCBcImZsb2F0XCIsIFwiZmxvYXQtb2Zmc2V0XCIsIFwiZmxvdy1mcm9tXCIsIFwiZmxvdy1pbnRvXCIsIFwiZm9udFwiLCBcImZvbnQtZmFtaWx5XCIsIFwiZm9udC1mZWF0dXJlLXNldHRpbmdzXCIsIFwiZm9udC1rZXJuaW5nXCIsIFwiZm9udC1sYW5ndWFnZS1vdmVycmlkZVwiLCBcImZvbnQtb3B0aWNhbC1zaXppbmdcIiwgXCJmb250LXNpemVcIiwgXCJmb250LXNpemUtYWRqdXN0XCIsIFwiZm9udC1zdHJldGNoXCIsIFwiZm9udC1zdHlsZVwiLCBcImZvbnQtc3ludGhlc2lzXCIsIFwiZm9udC12YXJpYW50XCIsIFwiZm9udC12YXJpYW50LWFsdGVybmF0ZXNcIiwgXCJmb250LXZhcmlhbnQtY2Fwc1wiLCBcImZvbnQtdmFyaWFudC1lYXN0LWFzaWFuXCIsIFwiZm9udC12YXJpYW50LWxpZ2F0dXJlc1wiLCBcImZvbnQtdmFyaWFudC1udW1lcmljXCIsIFwiZm9udC12YXJpYW50LXBvc2l0aW9uXCIsIFwiZm9udC12YXJpYXRpb24tc2V0dGluZ3NcIiwgXCJmb250LXdlaWdodFwiLCBcImdhcFwiLCBcImdyaWRcIiwgXCJncmlkLWFyZWFcIiwgXCJncmlkLWF1dG8tY29sdW1uc1wiLCBcImdyaWQtYXV0by1mbG93XCIsIFwiZ3JpZC1hdXRvLXJvd3NcIiwgXCJncmlkLWNvbHVtblwiLCBcImdyaWQtY29sdW1uLWVuZFwiLCBcImdyaWQtY29sdW1uLWdhcFwiLCBcImdyaWQtY29sdW1uLXN0YXJ0XCIsIFwiZ3JpZC1nYXBcIiwgXCJncmlkLXJvd1wiLCBcImdyaWQtcm93LWVuZFwiLCBcImdyaWQtcm93LWdhcFwiLCBcImdyaWQtcm93LXN0YXJ0XCIsIFwiZ3JpZC10ZW1wbGF0ZVwiLCBcImdyaWQtdGVtcGxhdGUtYXJlYXNcIiwgXCJncmlkLXRlbXBsYXRlLWNvbHVtbnNcIiwgXCJncmlkLXRlbXBsYXRlLXJvd3NcIiwgXCJoYW5naW5nLXB1bmN0dWF0aW9uXCIsIFwiaGVpZ2h0XCIsIFwiaHlwaGVuc1wiLCBcImljb25cIiwgXCJpbWFnZS1vcmllbnRhdGlvblwiLCBcImltYWdlLXJlbmRlcmluZ1wiLCBcImltYWdlLXJlc29sdXRpb25cIiwgXCJpbmxpbmUtYm94LWFsaWduXCIsIFwiaW5zZXRcIiwgXCJpbnNldC1ibG9ja1wiLCBcImluc2V0LWJsb2NrLWVuZFwiLCBcImluc2V0LWJsb2NrLXN0YXJ0XCIsIFwiaW5zZXQtaW5saW5lXCIsIFwiaW5zZXQtaW5saW5lLWVuZFwiLCBcImluc2V0LWlubGluZS1zdGFydFwiLCBcImlzb2xhdGlvblwiLCBcImp1c3RpZnktY29udGVudFwiLCBcImp1c3RpZnktaXRlbXNcIiwgXCJqdXN0aWZ5LXNlbGZcIiwgXCJsZWZ0XCIsIFwibGV0dGVyLXNwYWNpbmdcIiwgXCJsaW5lLWJyZWFrXCIsIFwibGluZS1oZWlnaHRcIiwgXCJsaW5lLWhlaWdodC1zdGVwXCIsIFwibGluZS1zdGFja2luZ1wiLCBcImxpbmUtc3RhY2tpbmctcnVieVwiLCBcImxpbmUtc3RhY2tpbmctc2hpZnRcIiwgXCJsaW5lLXN0YWNraW5nLXN0cmF0ZWd5XCIsIFwibGlzdC1zdHlsZVwiLCBcImxpc3Qtc3R5bGUtaW1hZ2VcIiwgXCJsaXN0LXN0eWxlLXBvc2l0aW9uXCIsIFwibGlzdC1zdHlsZS10eXBlXCIsIFwibWFyZ2luXCIsIFwibWFyZ2luLWJvdHRvbVwiLCBcIm1hcmdpbi1sZWZ0XCIsIFwibWFyZ2luLXJpZ2h0XCIsIFwibWFyZ2luLXRvcFwiLCBcIm1hcmtzXCIsIFwibWFycXVlZS1kaXJlY3Rpb25cIiwgXCJtYXJxdWVlLWxvb3BcIiwgXCJtYXJxdWVlLXBsYXktY291bnRcIiwgXCJtYXJxdWVlLXNwZWVkXCIsIFwibWFycXVlZS1zdHlsZVwiLCBcIm1hc2stY2xpcFwiLCBcIm1hc2stY29tcG9zaXRlXCIsIFwibWFzay1pbWFnZVwiLCBcIm1hc2stbW9kZVwiLCBcIm1hc2stb3JpZ2luXCIsIFwibWFzay1wb3NpdGlvblwiLCBcIm1hc2stcmVwZWF0XCIsIFwibWFzay1zaXplXCIsIFwibWFzay10eXBlXCIsIFwibWF4LWJsb2NrLXNpemVcIiwgXCJtYXgtaGVpZ2h0XCIsIFwibWF4LWlubGluZS1zaXplXCIsIFwibWF4LXdpZHRoXCIsIFwibWluLWJsb2NrLXNpemVcIiwgXCJtaW4taGVpZ2h0XCIsIFwibWluLWlubGluZS1zaXplXCIsIFwibWluLXdpZHRoXCIsIFwibWl4LWJsZW5kLW1vZGVcIiwgXCJtb3ZlLXRvXCIsIFwibmF2LWRvd25cIiwgXCJuYXYtaW5kZXhcIiwgXCJuYXYtbGVmdFwiLCBcIm5hdi1yaWdodFwiLCBcIm5hdi11cFwiLCBcIm9iamVjdC1maXRcIiwgXCJvYmplY3QtcG9zaXRpb25cIiwgXCJvZmZzZXRcIiwgXCJvZmZzZXQtYW5jaG9yXCIsIFwib2Zmc2V0LWRpc3RhbmNlXCIsIFwib2Zmc2V0LXBhdGhcIiwgXCJvZmZzZXQtcG9zaXRpb25cIiwgXCJvZmZzZXQtcm90YXRlXCIsIFwib3BhY2l0eVwiLCBcIm9yZGVyXCIsIFwib3JwaGFuc1wiLCBcIm91dGxpbmVcIiwgXCJvdXRsaW5lLWNvbG9yXCIsIFwib3V0bGluZS1vZmZzZXRcIiwgXCJvdXRsaW5lLXN0eWxlXCIsIFwib3V0bGluZS13aWR0aFwiLCBcIm92ZXJmbG93XCIsIFwib3ZlcmZsb3ctc3R5bGVcIiwgXCJvdmVyZmxvdy13cmFwXCIsIFwib3ZlcmZsb3cteFwiLCBcIm92ZXJmbG93LXlcIiwgXCJwYWRkaW5nXCIsIFwicGFkZGluZy1ib3R0b21cIiwgXCJwYWRkaW5nLWxlZnRcIiwgXCJwYWRkaW5nLXJpZ2h0XCIsIFwicGFkZGluZy10b3BcIiwgXCJwYWdlXCIsIFwicGFnZS1icmVhay1hZnRlclwiLCBcInBhZ2UtYnJlYWstYmVmb3JlXCIsIFwicGFnZS1icmVhay1pbnNpZGVcIiwgXCJwYWdlLXBvbGljeVwiLCBcInBhdXNlXCIsIFwicGF1c2UtYWZ0ZXJcIiwgXCJwYXVzZS1iZWZvcmVcIiwgXCJwZXJzcGVjdGl2ZVwiLCBcInBlcnNwZWN0aXZlLW9yaWdpblwiLCBcInBpdGNoXCIsIFwicGl0Y2gtcmFuZ2VcIiwgXCJwbGFjZS1jb250ZW50XCIsIFwicGxhY2UtaXRlbXNcIiwgXCJwbGFjZS1zZWxmXCIsIFwicGxheS1kdXJpbmdcIiwgXCJwb3NpdGlvblwiLCBcInByZXNlbnRhdGlvbi1sZXZlbFwiLCBcInB1bmN0dWF0aW9uLXRyaW1cIiwgXCJxdW90ZXNcIiwgXCJyZWdpb24tYnJlYWstYWZ0ZXJcIiwgXCJyZWdpb24tYnJlYWstYmVmb3JlXCIsIFwicmVnaW9uLWJyZWFrLWluc2lkZVwiLCBcInJlZ2lvbi1mcmFnbWVudFwiLCBcInJlbmRlcmluZy1pbnRlbnRcIiwgXCJyZXNpemVcIiwgXCJyZXN0XCIsIFwicmVzdC1hZnRlclwiLCBcInJlc3QtYmVmb3JlXCIsIFwicmljaG5lc3NcIiwgXCJyaWdodFwiLCBcInJvdGF0ZVwiLCBcInJvdGF0aW9uXCIsIFwicm90YXRpb24tcG9pbnRcIiwgXCJyb3ctZ2FwXCIsIFwicnVieS1hbGlnblwiLCBcInJ1Ynktb3ZlcmhhbmdcIiwgXCJydWJ5LXBvc2l0aW9uXCIsIFwicnVieS1zcGFuXCIsIFwic2NhbGVcIiwgXCJzY3JvbGwtYmVoYXZpb3JcIiwgXCJzY3JvbGwtbWFyZ2luXCIsIFwic2Nyb2xsLW1hcmdpbi1ibG9ja1wiLCBcInNjcm9sbC1tYXJnaW4tYmxvY2stZW5kXCIsIFwic2Nyb2xsLW1hcmdpbi1ibG9jay1zdGFydFwiLCBcInNjcm9sbC1tYXJnaW4tYm90dG9tXCIsIFwic2Nyb2xsLW1hcmdpbi1pbmxpbmVcIiwgXCJzY3JvbGwtbWFyZ2luLWlubGluZS1lbmRcIiwgXCJzY3JvbGwtbWFyZ2luLWlubGluZS1zdGFydFwiLCBcInNjcm9sbC1tYXJnaW4tbGVmdFwiLCBcInNjcm9sbC1tYXJnaW4tcmlnaHRcIiwgXCJzY3JvbGwtbWFyZ2luLXRvcFwiLCBcInNjcm9sbC1wYWRkaW5nXCIsIFwic2Nyb2xsLXBhZGRpbmctYmxvY2tcIiwgXCJzY3JvbGwtcGFkZGluZy1ibG9jay1lbmRcIiwgXCJzY3JvbGwtcGFkZGluZy1ibG9jay1zdGFydFwiLCBcInNjcm9sbC1wYWRkaW5nLWJvdHRvbVwiLCBcInNjcm9sbC1wYWRkaW5nLWlubGluZVwiLCBcInNjcm9sbC1wYWRkaW5nLWlubGluZS1lbmRcIiwgXCJzY3JvbGwtcGFkZGluZy1pbmxpbmUtc3RhcnRcIiwgXCJzY3JvbGwtcGFkZGluZy1sZWZ0XCIsIFwic2Nyb2xsLXBhZGRpbmctcmlnaHRcIiwgXCJzY3JvbGwtcGFkZGluZy10b3BcIiwgXCJzY3JvbGwtc25hcC1hbGlnblwiLCBcInNjcm9sbC1zbmFwLXR5cGVcIiwgXCJzaGFwZS1pbWFnZS10aHJlc2hvbGRcIiwgXCJzaGFwZS1pbnNpZGVcIiwgXCJzaGFwZS1tYXJnaW5cIiwgXCJzaGFwZS1vdXRzaWRlXCIsIFwic2l6ZVwiLCBcInNwZWFrXCIsIFwic3BlYWstYXNcIiwgXCJzcGVhay1oZWFkZXJcIiwgXCJzcGVhay1udW1lcmFsXCIsIFwic3BlYWstcHVuY3R1YXRpb25cIiwgXCJzcGVlY2gtcmF0ZVwiLCBcInN0cmVzc1wiLCBcInN0cmluZy1zZXRcIiwgXCJ0YWItc2l6ZVwiLCBcInRhYmxlLWxheW91dFwiLCBcInRhcmdldFwiLCBcInRhcmdldC1uYW1lXCIsIFwidGFyZ2V0LW5ld1wiLCBcInRhcmdldC1wb3NpdGlvblwiLCBcInRleHQtYWxpZ25cIiwgXCJ0ZXh0LWFsaWduLWxhc3RcIiwgXCJ0ZXh0LWNvbWJpbmUtdXByaWdodFwiLCBcInRleHQtZGVjb3JhdGlvblwiLCBcInRleHQtZGVjb3JhdGlvbi1jb2xvclwiLCBcInRleHQtZGVjb3JhdGlvbi1saW5lXCIsIFwidGV4dC1kZWNvcmF0aW9uLXNraXBcIiwgXCJ0ZXh0LWRlY29yYXRpb24tc2tpcC1pbmtcIiwgXCJ0ZXh0LWRlY29yYXRpb24tc3R5bGVcIiwgXCJ0ZXh0LWVtcGhhc2lzXCIsIFwidGV4dC1lbXBoYXNpcy1jb2xvclwiLCBcInRleHQtZW1waGFzaXMtcG9zaXRpb25cIiwgXCJ0ZXh0LWVtcGhhc2lzLXN0eWxlXCIsIFwidGV4dC1oZWlnaHRcIiwgXCJ0ZXh0LWluZGVudFwiLCBcInRleHQtanVzdGlmeVwiLCBcInRleHQtb3JpZW50YXRpb25cIiwgXCJ0ZXh0LW91dGxpbmVcIiwgXCJ0ZXh0LW92ZXJmbG93XCIsIFwidGV4dC1yZW5kZXJpbmdcIiwgXCJ0ZXh0LXNoYWRvd1wiLCBcInRleHQtc2l6ZS1hZGp1c3RcIiwgXCJ0ZXh0LXNwYWNlLWNvbGxhcHNlXCIsIFwidGV4dC10cmFuc2Zvcm1cIiwgXCJ0ZXh0LXVuZGVybGluZS1wb3NpdGlvblwiLCBcInRleHQtd3JhcFwiLCBcInRvcFwiLCBcInRvdWNoLWFjdGlvblwiLCBcInRyYW5zZm9ybVwiLCBcInRyYW5zZm9ybS1vcmlnaW5cIiwgXCJ0cmFuc2Zvcm0tc3R5bGVcIiwgXCJ0cmFuc2l0aW9uXCIsIFwidHJhbnNpdGlvbi1kZWxheVwiLCBcInRyYW5zaXRpb24tZHVyYXRpb25cIiwgXCJ0cmFuc2l0aW9uLXByb3BlcnR5XCIsIFwidHJhbnNpdGlvbi10aW1pbmctZnVuY3Rpb25cIiwgXCJ0cmFuc2xhdGVcIiwgXCJ1bmljb2RlLWJpZGlcIiwgXCJ1c2VyLXNlbGVjdFwiLCBcInZlcnRpY2FsLWFsaWduXCIsIFwidmlzaWJpbGl0eVwiLCBcInZvaWNlLWJhbGFuY2VcIiwgXCJ2b2ljZS1kdXJhdGlvblwiLCBcInZvaWNlLWZhbWlseVwiLCBcInZvaWNlLXBpdGNoXCIsIFwidm9pY2UtcmFuZ2VcIiwgXCJ2b2ljZS1yYXRlXCIsIFwidm9pY2Utc3RyZXNzXCIsIFwidm9pY2Utdm9sdW1lXCIsIFwidm9sdW1lXCIsIFwid2hpdGUtc3BhY2VcIiwgXCJ3aWRvd3NcIiwgXCJ3aWR0aFwiLCBcIndpbGwtY2hhbmdlXCIsIFwid29yZC1icmVha1wiLCBcIndvcmQtc3BhY2luZ1wiLCBcIndvcmQtd3JhcFwiLCBcIndyaXRpbmctbW9kZVwiLCBcInotaW5kZXhcIixcbiAgLy8gU1ZHLXNwZWNpZmljXG4gIFwiY2xpcC1wYXRoXCIsIFwiY2xpcC1ydWxlXCIsIFwibWFza1wiLCBcImVuYWJsZS1iYWNrZ3JvdW5kXCIsIFwiZmlsdGVyXCIsIFwiZmxvb2QtY29sb3JcIiwgXCJmbG9vZC1vcGFjaXR5XCIsIFwibGlnaHRpbmctY29sb3JcIiwgXCJzdG9wLWNvbG9yXCIsIFwic3RvcC1vcGFjaXR5XCIsIFwicG9pbnRlci1ldmVudHNcIiwgXCJjb2xvci1pbnRlcnBvbGF0aW9uXCIsIFwiY29sb3ItaW50ZXJwb2xhdGlvbi1maWx0ZXJzXCIsIFwiY29sb3ItcmVuZGVyaW5nXCIsIFwiZmlsbFwiLCBcImZpbGwtb3BhY2l0eVwiLCBcImZpbGwtcnVsZVwiLCBcImltYWdlLXJlbmRlcmluZ1wiLCBcIm1hcmtlclwiLCBcIm1hcmtlci1lbmRcIiwgXCJtYXJrZXItbWlkXCIsIFwibWFya2VyLXN0YXJ0XCIsIFwicGFpbnQtb3JkZXJcIiwgXCJzaGFwZS1yZW5kZXJpbmdcIiwgXCJzdHJva2VcIiwgXCJzdHJva2UtZGFzaGFycmF5XCIsIFwic3Ryb2tlLWRhc2hvZmZzZXRcIiwgXCJzdHJva2UtbGluZWNhcFwiLCBcInN0cm9rZS1saW5lam9pblwiLCBcInN0cm9rZS1taXRlcmxpbWl0XCIsIFwic3Ryb2tlLW9wYWNpdHlcIiwgXCJzdHJva2Utd2lkdGhcIiwgXCJ0ZXh0LXJlbmRlcmluZ1wiLCBcImJhc2VsaW5lLXNoaWZ0XCIsIFwiZG9taW5hbnQtYmFzZWxpbmVcIiwgXCJnbHlwaC1vcmllbnRhdGlvbi1ob3Jpem9udGFsXCIsIFwiZ2x5cGgtb3JpZW50YXRpb24tdmVydGljYWxcIiwgXCJ0ZXh0LWFuY2hvclwiLCBcIndyaXRpbmctbW9kZVwiXSxcbiAgcHJvcGVydHlLZXl3b3JkcyA9IGtleVNldChwcm9wZXJ0eUtleXdvcmRzXyk7XG52YXIgbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzXyA9IFtcImFjY2VudC1jb2xvclwiLCBcImFzcGVjdC1yYXRpb1wiLCBcImJvcmRlci1ibG9ja1wiLCBcImJvcmRlci1ibG9jay1jb2xvclwiLCBcImJvcmRlci1ibG9jay1lbmRcIiwgXCJib3JkZXItYmxvY2stZW5kLWNvbG9yXCIsIFwiYm9yZGVyLWJsb2NrLWVuZC1zdHlsZVwiLCBcImJvcmRlci1ibG9jay1lbmQtd2lkdGhcIiwgXCJib3JkZXItYmxvY2stc3RhcnRcIiwgXCJib3JkZXItYmxvY2stc3RhcnQtY29sb3JcIiwgXCJib3JkZXItYmxvY2stc3RhcnQtc3R5bGVcIiwgXCJib3JkZXItYmxvY2stc3RhcnQtd2lkdGhcIiwgXCJib3JkZXItYmxvY2stc3R5bGVcIiwgXCJib3JkZXItYmxvY2std2lkdGhcIiwgXCJib3JkZXItaW5saW5lXCIsIFwiYm9yZGVyLWlubGluZS1jb2xvclwiLCBcImJvcmRlci1pbmxpbmUtZW5kXCIsIFwiYm9yZGVyLWlubGluZS1lbmQtY29sb3JcIiwgXCJib3JkZXItaW5saW5lLWVuZC1zdHlsZVwiLCBcImJvcmRlci1pbmxpbmUtZW5kLXdpZHRoXCIsIFwiYm9yZGVyLWlubGluZS1zdGFydFwiLCBcImJvcmRlci1pbmxpbmUtc3RhcnQtY29sb3JcIiwgXCJib3JkZXItaW5saW5lLXN0YXJ0LXN0eWxlXCIsIFwiYm9yZGVyLWlubGluZS1zdGFydC13aWR0aFwiLCBcImJvcmRlci1pbmxpbmUtc3R5bGVcIiwgXCJib3JkZXItaW5saW5lLXdpZHRoXCIsIFwiY29udGVudC12aXNpYmlsaXR5XCIsIFwibWFyZ2luLWJsb2NrXCIsIFwibWFyZ2luLWJsb2NrLWVuZFwiLCBcIm1hcmdpbi1ibG9jay1zdGFydFwiLCBcIm1hcmdpbi1pbmxpbmVcIiwgXCJtYXJnaW4taW5saW5lLWVuZFwiLCBcIm1hcmdpbi1pbmxpbmUtc3RhcnRcIiwgXCJvdmVyZmxvdy1hbmNob3JcIiwgXCJvdmVyc2Nyb2xsLWJlaGF2aW9yXCIsIFwicGFkZGluZy1ibG9ja1wiLCBcInBhZGRpbmctYmxvY2stZW5kXCIsIFwicGFkZGluZy1ibG9jay1zdGFydFwiLCBcInBhZGRpbmctaW5saW5lXCIsIFwicGFkZGluZy1pbmxpbmUtZW5kXCIsIFwicGFkZGluZy1pbmxpbmUtc3RhcnRcIiwgXCJzY3JvbGwtc25hcC1zdG9wXCIsIFwic2Nyb2xsYmFyLTNkLWxpZ2h0LWNvbG9yXCIsIFwic2Nyb2xsYmFyLWFycm93LWNvbG9yXCIsIFwic2Nyb2xsYmFyLWJhc2UtY29sb3JcIiwgXCJzY3JvbGxiYXItZGFyay1zaGFkb3ctY29sb3JcIiwgXCJzY3JvbGxiYXItZmFjZS1jb2xvclwiLCBcInNjcm9sbGJhci1oaWdobGlnaHQtY29sb3JcIiwgXCJzY3JvbGxiYXItc2hhZG93LWNvbG9yXCIsIFwic2Nyb2xsYmFyLXRyYWNrLWNvbG9yXCIsIFwic2VhcmNoZmllbGQtY2FuY2VsLWJ1dHRvblwiLCBcInNlYXJjaGZpZWxkLWRlY29yYXRpb25cIiwgXCJzZWFyY2hmaWVsZC1yZXN1bHRzLWJ1dHRvblwiLCBcInNlYXJjaGZpZWxkLXJlc3VsdHMtZGVjb3JhdGlvblwiLCBcInNoYXBlLWluc2lkZVwiLCBcInpvb21cIl0sXG4gIG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3JkcyA9IGtleVNldChub25TdGFuZGFyZFByb3BlcnR5S2V5d29yZHNfKTtcbnZhciBmb250UHJvcGVydGllc18gPSBbXCJmb250LWRpc3BsYXlcIiwgXCJmb250LWZhbWlseVwiLCBcInNyY1wiLCBcInVuaWNvZGUtcmFuZ2VcIiwgXCJmb250LXZhcmlhbnRcIiwgXCJmb250LWZlYXR1cmUtc2V0dGluZ3NcIiwgXCJmb250LXN0cmV0Y2hcIiwgXCJmb250LXdlaWdodFwiLCBcImZvbnQtc3R5bGVcIl0sXG4gIGZvbnRQcm9wZXJ0aWVzID0ga2V5U2V0KGZvbnRQcm9wZXJ0aWVzXyk7XG52YXIgY291bnRlckRlc2NyaXB0b3JzXyA9IFtcImFkZGl0aXZlLXN5bWJvbHNcIiwgXCJmYWxsYmFja1wiLCBcIm5lZ2F0aXZlXCIsIFwicGFkXCIsIFwicHJlZml4XCIsIFwicmFuZ2VcIiwgXCJzcGVhay1hc1wiLCBcInN1ZmZpeFwiLCBcInN5bWJvbHNcIiwgXCJzeXN0ZW1cIl0sXG4gIGNvdW50ZXJEZXNjcmlwdG9ycyA9IGtleVNldChjb3VudGVyRGVzY3JpcHRvcnNfKTtcbnZhciBjb2xvcktleXdvcmRzXyA9IFtcImFsaWNlYmx1ZVwiLCBcImFudGlxdWV3aGl0ZVwiLCBcImFxdWFcIiwgXCJhcXVhbWFyaW5lXCIsIFwiYXp1cmVcIiwgXCJiZWlnZVwiLCBcImJpc3F1ZVwiLCBcImJsYWNrXCIsIFwiYmxhbmNoZWRhbG1vbmRcIiwgXCJibHVlXCIsIFwiYmx1ZXZpb2xldFwiLCBcImJyb3duXCIsIFwiYnVybHl3b29kXCIsIFwiY2FkZXRibHVlXCIsIFwiY2hhcnRyZXVzZVwiLCBcImNob2NvbGF0ZVwiLCBcImNvcmFsXCIsIFwiY29ybmZsb3dlcmJsdWVcIiwgXCJjb3Juc2lsa1wiLCBcImNyaW1zb25cIiwgXCJjeWFuXCIsIFwiZGFya2JsdWVcIiwgXCJkYXJrY3lhblwiLCBcImRhcmtnb2xkZW5yb2RcIiwgXCJkYXJrZ3JheVwiLCBcImRhcmtncmVlblwiLCBcImRhcmtncmV5XCIsIFwiZGFya2toYWtpXCIsIFwiZGFya21hZ2VudGFcIiwgXCJkYXJrb2xpdmVncmVlblwiLCBcImRhcmtvcmFuZ2VcIiwgXCJkYXJrb3JjaGlkXCIsIFwiZGFya3JlZFwiLCBcImRhcmtzYWxtb25cIiwgXCJkYXJrc2VhZ3JlZW5cIiwgXCJkYXJrc2xhdGVibHVlXCIsIFwiZGFya3NsYXRlZ3JheVwiLCBcImRhcmtzbGF0ZWdyZXlcIiwgXCJkYXJrdHVycXVvaXNlXCIsIFwiZGFya3Zpb2xldFwiLCBcImRlZXBwaW5rXCIsIFwiZGVlcHNreWJsdWVcIiwgXCJkaW1ncmF5XCIsIFwiZGltZ3JleVwiLCBcImRvZGdlcmJsdWVcIiwgXCJmaXJlYnJpY2tcIiwgXCJmbG9yYWx3aGl0ZVwiLCBcImZvcmVzdGdyZWVuXCIsIFwiZnVjaHNpYVwiLCBcImdhaW5zYm9yb1wiLCBcImdob3N0d2hpdGVcIiwgXCJnb2xkXCIsIFwiZ29sZGVucm9kXCIsIFwiZ3JheVwiLCBcImdyZXlcIiwgXCJncmVlblwiLCBcImdyZWVueWVsbG93XCIsIFwiaG9uZXlkZXdcIiwgXCJob3RwaW5rXCIsIFwiaW5kaWFucmVkXCIsIFwiaW5kaWdvXCIsIFwiaXZvcnlcIiwgXCJraGFraVwiLCBcImxhdmVuZGVyXCIsIFwibGF2ZW5kZXJibHVzaFwiLCBcImxhd25ncmVlblwiLCBcImxlbW9uY2hpZmZvblwiLCBcImxpZ2h0Ymx1ZVwiLCBcImxpZ2h0Y29yYWxcIiwgXCJsaWdodGN5YW5cIiwgXCJsaWdodGdvbGRlbnJvZHllbGxvd1wiLCBcImxpZ2h0Z3JheVwiLCBcImxpZ2h0Z3JlZW5cIiwgXCJsaWdodGdyZXlcIiwgXCJsaWdodHBpbmtcIiwgXCJsaWdodHNhbG1vblwiLCBcImxpZ2h0c2VhZ3JlZW5cIiwgXCJsaWdodHNreWJsdWVcIiwgXCJsaWdodHNsYXRlZ3JheVwiLCBcImxpZ2h0c2xhdGVncmV5XCIsIFwibGlnaHRzdGVlbGJsdWVcIiwgXCJsaWdodHllbGxvd1wiLCBcImxpbWVcIiwgXCJsaW1lZ3JlZW5cIiwgXCJsaW5lblwiLCBcIm1hZ2VudGFcIiwgXCJtYXJvb25cIiwgXCJtZWRpdW1hcXVhbWFyaW5lXCIsIFwibWVkaXVtYmx1ZVwiLCBcIm1lZGl1bW9yY2hpZFwiLCBcIm1lZGl1bXB1cnBsZVwiLCBcIm1lZGl1bXNlYWdyZWVuXCIsIFwibWVkaXVtc2xhdGVibHVlXCIsIFwibWVkaXVtc3ByaW5nZ3JlZW5cIiwgXCJtZWRpdW10dXJxdW9pc2VcIiwgXCJtZWRpdW12aW9sZXRyZWRcIiwgXCJtaWRuaWdodGJsdWVcIiwgXCJtaW50Y3JlYW1cIiwgXCJtaXN0eXJvc2VcIiwgXCJtb2NjYXNpblwiLCBcIm5hdmFqb3doaXRlXCIsIFwibmF2eVwiLCBcIm9sZGxhY2VcIiwgXCJvbGl2ZVwiLCBcIm9saXZlZHJhYlwiLCBcIm9yYW5nZVwiLCBcIm9yYW5nZXJlZFwiLCBcIm9yY2hpZFwiLCBcInBhbGVnb2xkZW5yb2RcIiwgXCJwYWxlZ3JlZW5cIiwgXCJwYWxldHVycXVvaXNlXCIsIFwicGFsZXZpb2xldHJlZFwiLCBcInBhcGF5YXdoaXBcIiwgXCJwZWFjaHB1ZmZcIiwgXCJwZXJ1XCIsIFwicGlua1wiLCBcInBsdW1cIiwgXCJwb3dkZXJibHVlXCIsIFwicHVycGxlXCIsIFwicmViZWNjYXB1cnBsZVwiLCBcInJlZFwiLCBcInJvc3licm93blwiLCBcInJveWFsYmx1ZVwiLCBcInNhZGRsZWJyb3duXCIsIFwic2FsbW9uXCIsIFwic2FuZHlicm93blwiLCBcInNlYWdyZWVuXCIsIFwic2Vhc2hlbGxcIiwgXCJzaWVubmFcIiwgXCJzaWx2ZXJcIiwgXCJza3libHVlXCIsIFwic2xhdGVibHVlXCIsIFwic2xhdGVncmF5XCIsIFwic2xhdGVncmV5XCIsIFwic25vd1wiLCBcInNwcmluZ2dyZWVuXCIsIFwic3RlZWxibHVlXCIsIFwidGFuXCIsIFwidGVhbFwiLCBcInRoaXN0bGVcIiwgXCJ0b21hdG9cIiwgXCJ0dXJxdW9pc2VcIiwgXCJ2aW9sZXRcIiwgXCJ3aGVhdFwiLCBcIndoaXRlXCIsIFwid2hpdGVzbW9rZVwiLCBcInllbGxvd1wiLCBcInllbGxvd2dyZWVuXCJdLFxuICBjb2xvcktleXdvcmRzID0ga2V5U2V0KGNvbG9yS2V5d29yZHNfKTtcbnZhciB2YWx1ZUtleXdvcmRzXyA9IFtcImFib3ZlXCIsIFwiYWJzb2x1dGVcIiwgXCJhY3RpdmVib3JkZXJcIiwgXCJhZGRpdGl2ZVwiLCBcImFjdGl2ZWNhcHRpb25cIiwgXCJhZmFyXCIsIFwiYWZ0ZXItd2hpdGUtc3BhY2VcIiwgXCJhaGVhZFwiLCBcImFsaWFzXCIsIFwiYWxsXCIsIFwiYWxsLXNjcm9sbFwiLCBcImFscGhhYmV0aWNcIiwgXCJhbHRlcm5hdGVcIiwgXCJhbHdheXNcIiwgXCJhbWhhcmljXCIsIFwiYW1oYXJpYy1hYmVnZWRlXCIsIFwiYW50aWFsaWFzZWRcIiwgXCJhcHB3b3Jrc3BhY2VcIiwgXCJhcmFiaWMtaW5kaWNcIiwgXCJhcm1lbmlhblwiLCBcImFzdGVyaXNrc1wiLCBcImF0dHJcIiwgXCJhdXRvXCIsIFwiYXV0by1mbG93XCIsIFwiYXZvaWRcIiwgXCJhdm9pZC1jb2x1bW5cIiwgXCJhdm9pZC1wYWdlXCIsIFwiYXZvaWQtcmVnaW9uXCIsIFwiYXhpcy1wYW5cIiwgXCJiYWNrZ3JvdW5kXCIsIFwiYmFja3dhcmRzXCIsIFwiYmFzZWxpbmVcIiwgXCJiZWxvd1wiLCBcImJpZGktb3ZlcnJpZGVcIiwgXCJiaW5hcnlcIiwgXCJiZW5nYWxpXCIsIFwiYmxpbmtcIiwgXCJibG9ja1wiLCBcImJsb2NrLWF4aXNcIiwgXCJibHVyXCIsIFwiYm9sZFwiLCBcImJvbGRlclwiLCBcImJvcmRlclwiLCBcImJvcmRlci1ib3hcIiwgXCJib3RoXCIsIFwiYm90dG9tXCIsIFwiYnJlYWtcIiwgXCJicmVhay1hbGxcIiwgXCJicmVhay13b3JkXCIsIFwiYnJpZ2h0bmVzc1wiLCBcImJ1bGxldHNcIiwgXCJidXR0b25cIiwgXCJidXR0b25mYWNlXCIsIFwiYnV0dG9uaGlnaGxpZ2h0XCIsIFwiYnV0dG9uc2hhZG93XCIsIFwiYnV0dG9udGV4dFwiLCBcImNhbGNcIiwgXCJjYW1ib2RpYW5cIiwgXCJjYXBpdGFsaXplXCIsIFwiY2Fwcy1sb2NrLWluZGljYXRvclwiLCBcImNhcHRpb25cIiwgXCJjYXB0aW9udGV4dFwiLCBcImNhcmV0XCIsIFwiY2VsbFwiLCBcImNlbnRlclwiLCBcImNoZWNrYm94XCIsIFwiY2lyY2xlXCIsIFwiY2prLWRlY2ltYWxcIiwgXCJjamstZWFydGhseS1icmFuY2hcIiwgXCJjamstaGVhdmVubHktc3RlbVwiLCBcImNqay1pZGVvZ3JhcGhpY1wiLCBcImNsZWFyXCIsIFwiY2xpcFwiLCBcImNsb3NlLXF1b3RlXCIsIFwiY29sLXJlc2l6ZVwiLCBcImNvbGxhcHNlXCIsIFwiY29sb3JcIiwgXCJjb2xvci1idXJuXCIsIFwiY29sb3ItZG9kZ2VcIiwgXCJjb2x1bW5cIiwgXCJjb2x1bW4tcmV2ZXJzZVwiLCBcImNvbXBhY3RcIiwgXCJjb25kZW5zZWRcIiwgXCJjb25pYy1ncmFkaWVudFwiLCBcImNvbnRhaW5cIiwgXCJjb250ZW50XCIsIFwiY29udGVudHNcIiwgXCJjb250ZW50LWJveFwiLCBcImNvbnRleHQtbWVudVwiLCBcImNvbnRpbnVvdXNcIiwgXCJjb250cmFzdFwiLCBcImNvcHlcIiwgXCJjb3VudGVyXCIsIFwiY291bnRlcnNcIiwgXCJjb3ZlclwiLCBcImNyb3BcIiwgXCJjcm9zc1wiLCBcImNyb3NzaGFpclwiLCBcImN1YmljLWJlemllclwiLCBcImN1cnJlbnRjb2xvclwiLCBcImN1cnNpdmVcIiwgXCJjeWNsaWNcIiwgXCJkYXJrZW5cIiwgXCJkYXNoZWRcIiwgXCJkZWNpbWFsXCIsIFwiZGVjaW1hbC1sZWFkaW5nLXplcm9cIiwgXCJkZWZhdWx0XCIsIFwiZGVmYXVsdC1idXR0b25cIiwgXCJkZW5zZVwiLCBcImRlc3RpbmF0aW9uLWF0b3BcIiwgXCJkZXN0aW5hdGlvbi1pblwiLCBcImRlc3RpbmF0aW9uLW91dFwiLCBcImRlc3RpbmF0aW9uLW92ZXJcIiwgXCJkZXZhbmFnYXJpXCIsIFwiZGlmZmVyZW5jZVwiLCBcImRpc2NcIiwgXCJkaXNjYXJkXCIsIFwiZGlzY2xvc3VyZS1jbG9zZWRcIiwgXCJkaXNjbG9zdXJlLW9wZW5cIiwgXCJkb2N1bWVudFwiLCBcImRvdC1kYXNoXCIsIFwiZG90LWRvdC1kYXNoXCIsIFwiZG90dGVkXCIsIFwiZG91YmxlXCIsIFwiZG93blwiLCBcImRyb3Atc2hhZG93XCIsIFwiZS1yZXNpemVcIiwgXCJlYXNlXCIsIFwiZWFzZS1pblwiLCBcImVhc2UtaW4tb3V0XCIsIFwiZWFzZS1vdXRcIiwgXCJlbGVtZW50XCIsIFwiZWxsaXBzZVwiLCBcImVsbGlwc2lzXCIsIFwiZW1iZWRcIiwgXCJlbmRcIiwgXCJldGhpb3BpY1wiLCBcImV0aGlvcGljLWFiZWdlZGVcIiwgXCJldGhpb3BpYy1hYmVnZWRlLWFtLWV0XCIsIFwiZXRoaW9waWMtYWJlZ2VkZS1nZXpcIiwgXCJldGhpb3BpYy1hYmVnZWRlLXRpLWVyXCIsIFwiZXRoaW9waWMtYWJlZ2VkZS10aS1ldFwiLCBcImV0aGlvcGljLWhhbGVoYW1lLWFhLWVyXCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtYWEtZXRcIiwgXCJldGhpb3BpYy1oYWxlaGFtZS1hbS1ldFwiLCBcImV0aGlvcGljLWhhbGVoYW1lLWdlelwiLCBcImV0aGlvcGljLWhhbGVoYW1lLW9tLWV0XCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtc2lkLWV0XCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtc28tZXRcIiwgXCJldGhpb3BpYy1oYWxlaGFtZS10aS1lclwiLCBcImV0aGlvcGljLWhhbGVoYW1lLXRpLWV0XCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtdGlnXCIsIFwiZXRoaW9waWMtbnVtZXJpY1wiLCBcImV3LXJlc2l6ZVwiLCBcImV4Y2x1c2lvblwiLCBcImV4cGFuZGVkXCIsIFwiZXh0ZW5kc1wiLCBcImV4dHJhLWNvbmRlbnNlZFwiLCBcImV4dHJhLWV4cGFuZGVkXCIsIFwiZmFudGFzeVwiLCBcImZhc3RcIiwgXCJmaWxsXCIsIFwiZmlsbC1ib3hcIiwgXCJmaXhlZFwiLCBcImZsYXRcIiwgXCJmbGV4XCIsIFwiZmxleC1lbmRcIiwgXCJmbGV4LXN0YXJ0XCIsIFwiZm9vdG5vdGVzXCIsIFwiZm9yd2FyZHNcIiwgXCJmcm9tXCIsIFwiZ2VvbWV0cmljUHJlY2lzaW9uXCIsIFwiZ2VvcmdpYW5cIiwgXCJncmF5c2NhbGVcIiwgXCJncmF5dGV4dFwiLCBcImdyaWRcIiwgXCJncm9vdmVcIiwgXCJndWphcmF0aVwiLCBcImd1cm11a2hpXCIsIFwiaGFuZFwiLCBcImhhbmd1bFwiLCBcImhhbmd1bC1jb25zb25hbnRcIiwgXCJoYXJkLWxpZ2h0XCIsIFwiaGVicmV3XCIsIFwiaGVscFwiLCBcImhpZGRlblwiLCBcImhpZGVcIiwgXCJoaWdoZXJcIiwgXCJoaWdobGlnaHRcIiwgXCJoaWdobGlnaHR0ZXh0XCIsIFwiaGlyYWdhbmFcIiwgXCJoaXJhZ2FuYS1pcm9oYVwiLCBcImhvcml6b250YWxcIiwgXCJoc2xcIiwgXCJoc2xhXCIsIFwiaHVlXCIsIFwiaHVlLXJvdGF0ZVwiLCBcImljb25cIiwgXCJpZ25vcmVcIiwgXCJpbmFjdGl2ZWJvcmRlclwiLCBcImluYWN0aXZlY2FwdGlvblwiLCBcImluYWN0aXZlY2FwdGlvbnRleHRcIiwgXCJpbmZpbml0ZVwiLCBcImluZm9iYWNrZ3JvdW5kXCIsIFwiaW5mb3RleHRcIiwgXCJpbmhlcml0XCIsIFwiaW5pdGlhbFwiLCBcImlubGluZVwiLCBcImlubGluZS1heGlzXCIsIFwiaW5saW5lLWJsb2NrXCIsIFwiaW5saW5lLWZsZXhcIiwgXCJpbmxpbmUtZ3JpZFwiLCBcImlubGluZS10YWJsZVwiLCBcImluc2V0XCIsIFwiaW5zaWRlXCIsIFwiaW50cmluc2ljXCIsIFwiaW52ZXJ0XCIsIFwiaXRhbGljXCIsIFwiamFwYW5lc2UtZm9ybWFsXCIsIFwiamFwYW5lc2UtaW5mb3JtYWxcIiwgXCJqdXN0aWZ5XCIsIFwia2FubmFkYVwiLCBcImthdGFrYW5hXCIsIFwia2F0YWthbmEtaXJvaGFcIiwgXCJrZWVwLWFsbFwiLCBcImtobWVyXCIsIFwia29yZWFuLWhhbmd1bC1mb3JtYWxcIiwgXCJrb3JlYW4taGFuamEtZm9ybWFsXCIsIFwia29yZWFuLWhhbmphLWluZm9ybWFsXCIsIFwibGFuZHNjYXBlXCIsIFwibGFvXCIsIFwibGFyZ2VcIiwgXCJsYXJnZXJcIiwgXCJsZWZ0XCIsIFwibGV2ZWxcIiwgXCJsaWdodGVyXCIsIFwibGlnaHRlblwiLCBcImxpbmUtdGhyb3VnaFwiLCBcImxpbmVhclwiLCBcImxpbmVhci1ncmFkaWVudFwiLCBcImxpbmVzXCIsIFwibGlzdC1pdGVtXCIsIFwibGlzdGJveFwiLCBcImxpc3RpdGVtXCIsIFwibG9jYWxcIiwgXCJsb2dpY2FsXCIsIFwibG91ZFwiLCBcImxvd2VyXCIsIFwibG93ZXItYWxwaGFcIiwgXCJsb3dlci1hcm1lbmlhblwiLCBcImxvd2VyLWdyZWVrXCIsIFwibG93ZXItaGV4YWRlY2ltYWxcIiwgXCJsb3dlci1sYXRpblwiLCBcImxvd2VyLW5vcndlZ2lhblwiLCBcImxvd2VyLXJvbWFuXCIsIFwibG93ZXJjYXNlXCIsIFwibHRyXCIsIFwibHVtaW5vc2l0eVwiLCBcIm1hbGF5YWxhbVwiLCBcIm1hbmlwdWxhdGlvblwiLCBcIm1hdGNoXCIsIFwibWF0cml4XCIsIFwibWF0cml4M2RcIiwgXCJtZWRpYS1wbGF5LWJ1dHRvblwiLCBcIm1lZGlhLXNsaWRlclwiLCBcIm1lZGlhLXNsaWRlcnRodW1iXCIsIFwibWVkaWEtdm9sdW1lLXNsaWRlclwiLCBcIm1lZGlhLXZvbHVtZS1zbGlkZXJ0aHVtYlwiLCBcIm1lZGl1bVwiLCBcIm1lbnVcIiwgXCJtZW51bGlzdFwiLCBcIm1lbnVsaXN0LWJ1dHRvblwiLCBcIm1lbnV0ZXh0XCIsIFwibWVzc2FnZS1ib3hcIiwgXCJtaWRkbGVcIiwgXCJtaW4taW50cmluc2ljXCIsIFwibWl4XCIsIFwibW9uZ29saWFuXCIsIFwibW9ub3NwYWNlXCIsIFwibW92ZVwiLCBcIm11bHRpcGxlXCIsIFwibXVsdGlwbGVfbWFza19pbWFnZXNcIiwgXCJtdWx0aXBseVwiLCBcIm15YW5tYXJcIiwgXCJuLXJlc2l6ZVwiLCBcIm5hcnJvd2VyXCIsIFwibmUtcmVzaXplXCIsIFwibmVzdy1yZXNpemVcIiwgXCJuby1jbG9zZS1xdW90ZVwiLCBcIm5vLWRyb3BcIiwgXCJuby1vcGVuLXF1b3RlXCIsIFwibm8tcmVwZWF0XCIsIFwibm9uZVwiLCBcIm5vcm1hbFwiLCBcIm5vdC1hbGxvd2VkXCIsIFwibm93cmFwXCIsIFwibnMtcmVzaXplXCIsIFwibnVtYmVyc1wiLCBcIm51bWVyaWNcIiwgXCJudy1yZXNpemVcIiwgXCJud3NlLXJlc2l6ZVwiLCBcIm9ibGlxdWVcIiwgXCJvY3RhbFwiLCBcIm9wYWNpdHlcIiwgXCJvcGVuLXF1b3RlXCIsIFwib3B0aW1pemVMZWdpYmlsaXR5XCIsIFwib3B0aW1pemVTcGVlZFwiLCBcIm9yaXlhXCIsIFwib3JvbW9cIiwgXCJvdXRzZXRcIiwgXCJvdXRzaWRlXCIsIFwib3V0c2lkZS1zaGFwZVwiLCBcIm92ZXJsYXlcIiwgXCJvdmVybGluZVwiLCBcInBhZGRpbmdcIiwgXCJwYWRkaW5nLWJveFwiLCBcInBhaW50ZWRcIiwgXCJwYWdlXCIsIFwicGF1c2VkXCIsIFwicGVyc2lhblwiLCBcInBlcnNwZWN0aXZlXCIsIFwicGluY2gtem9vbVwiLCBcInBsdXMtZGFya2VyXCIsIFwicGx1cy1saWdodGVyXCIsIFwicG9pbnRlclwiLCBcInBvbHlnb25cIiwgXCJwb3J0cmFpdFwiLCBcInByZVwiLCBcInByZS1saW5lXCIsIFwicHJlLXdyYXBcIiwgXCJwcmVzZXJ2ZS0zZFwiLCBcInByb2dyZXNzXCIsIFwicHVzaC1idXR0b25cIiwgXCJyYWRpYWwtZ3JhZGllbnRcIiwgXCJyYWRpb1wiLCBcInJlYWQtb25seVwiLCBcInJlYWQtd3JpdGVcIiwgXCJyZWFkLXdyaXRlLXBsYWludGV4dC1vbmx5XCIsIFwicmVjdGFuZ2xlXCIsIFwicmVnaW9uXCIsIFwicmVsYXRpdmVcIiwgXCJyZXBlYXRcIiwgXCJyZXBlYXRpbmctbGluZWFyLWdyYWRpZW50XCIsIFwicmVwZWF0aW5nLXJhZGlhbC1ncmFkaWVudFwiLCBcInJlcGVhdGluZy1jb25pYy1ncmFkaWVudFwiLCBcInJlcGVhdC14XCIsIFwicmVwZWF0LXlcIiwgXCJyZXNldFwiLCBcInJldmVyc2VcIiwgXCJyZ2JcIiwgXCJyZ2JhXCIsIFwicmlkZ2VcIiwgXCJyaWdodFwiLCBcInJvdGF0ZVwiLCBcInJvdGF0ZTNkXCIsIFwicm90YXRlWFwiLCBcInJvdGF0ZVlcIiwgXCJyb3RhdGVaXCIsIFwicm91bmRcIiwgXCJyb3dcIiwgXCJyb3ctcmVzaXplXCIsIFwicm93LXJldmVyc2VcIiwgXCJydGxcIiwgXCJydW4taW5cIiwgXCJydW5uaW5nXCIsIFwicy1yZXNpemVcIiwgXCJzYW5zLXNlcmlmXCIsIFwic2F0dXJhdGVcIiwgXCJzYXR1cmF0aW9uXCIsIFwic2NhbGVcIiwgXCJzY2FsZTNkXCIsIFwic2NhbGVYXCIsIFwic2NhbGVZXCIsIFwic2NhbGVaXCIsIFwic2NyZWVuXCIsIFwic2Nyb2xsXCIsIFwic2Nyb2xsYmFyXCIsIFwic2Nyb2xsLXBvc2l0aW9uXCIsIFwic2UtcmVzaXplXCIsIFwic2VhcmNoZmllbGRcIiwgXCJzZWFyY2hmaWVsZC1jYW5jZWwtYnV0dG9uXCIsIFwic2VhcmNoZmllbGQtZGVjb3JhdGlvblwiLCBcInNlYXJjaGZpZWxkLXJlc3VsdHMtYnV0dG9uXCIsIFwic2VhcmNoZmllbGQtcmVzdWx0cy1kZWNvcmF0aW9uXCIsIFwic2VsZi1zdGFydFwiLCBcInNlbGYtZW5kXCIsIFwic2VtaS1jb25kZW5zZWRcIiwgXCJzZW1pLWV4cGFuZGVkXCIsIFwic2VwYXJhdGVcIiwgXCJzZXBpYVwiLCBcInNlcmlmXCIsIFwic2hvd1wiLCBcInNpZGFtYVwiLCBcInNpbXAtY2hpbmVzZS1mb3JtYWxcIiwgXCJzaW1wLWNoaW5lc2UtaW5mb3JtYWxcIiwgXCJzaW5nbGVcIiwgXCJza2V3XCIsIFwic2tld1hcIiwgXCJza2V3WVwiLCBcInNraXAtd2hpdGUtc3BhY2VcIiwgXCJzbGlkZVwiLCBcInNsaWRlci1ob3Jpem9udGFsXCIsIFwic2xpZGVyLXZlcnRpY2FsXCIsIFwic2xpZGVydGh1bWItaG9yaXpvbnRhbFwiLCBcInNsaWRlcnRodW1iLXZlcnRpY2FsXCIsIFwic2xvd1wiLCBcInNtYWxsXCIsIFwic21hbGwtY2Fwc1wiLCBcInNtYWxsLWNhcHRpb25cIiwgXCJzbWFsbGVyXCIsIFwic29mdC1saWdodFwiLCBcInNvbGlkXCIsIFwic29tYWxpXCIsIFwic291cmNlLWF0b3BcIiwgXCJzb3VyY2UtaW5cIiwgXCJzb3VyY2Utb3V0XCIsIFwic291cmNlLW92ZXJcIiwgXCJzcGFjZVwiLCBcInNwYWNlLWFyb3VuZFwiLCBcInNwYWNlLWJldHdlZW5cIiwgXCJzcGFjZS1ldmVubHlcIiwgXCJzcGVsbC1vdXRcIiwgXCJzcXVhcmVcIiwgXCJzcXVhcmUtYnV0dG9uXCIsIFwic3RhcnRcIiwgXCJzdGF0aWNcIiwgXCJzdGF0dXMtYmFyXCIsIFwic3RyZXRjaFwiLCBcInN0cm9rZVwiLCBcInN0cm9rZS1ib3hcIiwgXCJzdWJcIiwgXCJzdWJwaXhlbC1hbnRpYWxpYXNlZFwiLCBcInN2Z19tYXNrc1wiLCBcInN1cGVyXCIsIFwic3ctcmVzaXplXCIsIFwic3ltYm9saWNcIiwgXCJzeW1ib2xzXCIsIFwic3lzdGVtLXVpXCIsIFwidGFibGVcIiwgXCJ0YWJsZS1jYXB0aW9uXCIsIFwidGFibGUtY2VsbFwiLCBcInRhYmxlLWNvbHVtblwiLCBcInRhYmxlLWNvbHVtbi1ncm91cFwiLCBcInRhYmxlLWZvb3Rlci1ncm91cFwiLCBcInRhYmxlLWhlYWRlci1ncm91cFwiLCBcInRhYmxlLXJvd1wiLCBcInRhYmxlLXJvdy1ncm91cFwiLCBcInRhbWlsXCIsIFwidGVsdWd1XCIsIFwidGV4dFwiLCBcInRleHQtYm90dG9tXCIsIFwidGV4dC10b3BcIiwgXCJ0ZXh0YXJlYVwiLCBcInRleHRmaWVsZFwiLCBcInRoYWlcIiwgXCJ0aGlja1wiLCBcInRoaW5cIiwgXCJ0aHJlZWRkYXJrc2hhZG93XCIsIFwidGhyZWVkZmFjZVwiLCBcInRocmVlZGhpZ2hsaWdodFwiLCBcInRocmVlZGxpZ2h0c2hhZG93XCIsIFwidGhyZWVkc2hhZG93XCIsIFwidGliZXRhblwiLCBcInRpZ3JlXCIsIFwidGlncmlueWEtZXJcIiwgXCJ0aWdyaW55YS1lci1hYmVnZWRlXCIsIFwidGlncmlueWEtZXRcIiwgXCJ0aWdyaW55YS1ldC1hYmVnZWRlXCIsIFwidG9cIiwgXCJ0b3BcIiwgXCJ0cmFkLWNoaW5lc2UtZm9ybWFsXCIsIFwidHJhZC1jaGluZXNlLWluZm9ybWFsXCIsIFwidHJhbnNmb3JtXCIsIFwidHJhbnNsYXRlXCIsIFwidHJhbnNsYXRlM2RcIiwgXCJ0cmFuc2xhdGVYXCIsIFwidHJhbnNsYXRlWVwiLCBcInRyYW5zbGF0ZVpcIiwgXCJ0cmFuc3BhcmVudFwiLCBcInVsdHJhLWNvbmRlbnNlZFwiLCBcInVsdHJhLWV4cGFuZGVkXCIsIFwidW5kZXJsaW5lXCIsIFwidW5pZGlyZWN0aW9uYWwtcGFuXCIsIFwidW5zZXRcIiwgXCJ1cFwiLCBcInVwcGVyLWFscGhhXCIsIFwidXBwZXItYXJtZW5pYW5cIiwgXCJ1cHBlci1ncmVla1wiLCBcInVwcGVyLWhleGFkZWNpbWFsXCIsIFwidXBwZXItbGF0aW5cIiwgXCJ1cHBlci1ub3J3ZWdpYW5cIiwgXCJ1cHBlci1yb21hblwiLCBcInVwcGVyY2FzZVwiLCBcInVyZHVcIiwgXCJ1cmxcIiwgXCJ2YXJcIiwgXCJ2ZXJ0aWNhbFwiLCBcInZlcnRpY2FsLXRleHRcIiwgXCJ2aWV3LWJveFwiLCBcInZpc2libGVcIiwgXCJ2aXNpYmxlRmlsbFwiLCBcInZpc2libGVQYWludGVkXCIsIFwidmlzaWJsZVN0cm9rZVwiLCBcInZpc3VhbFwiLCBcInctcmVzaXplXCIsIFwid2FpdFwiLCBcIndhdmVcIiwgXCJ3aWRlclwiLCBcIndpbmRvd1wiLCBcIndpbmRvd2ZyYW1lXCIsIFwid2luZG93dGV4dFwiLCBcIndvcmRzXCIsIFwid3JhcFwiLCBcIndyYXAtcmV2ZXJzZVwiLCBcIngtbGFyZ2VcIiwgXCJ4LXNtYWxsXCIsIFwieG9yXCIsIFwieHgtbGFyZ2VcIiwgXCJ4eC1zbWFsbFwiXSxcbiAgdmFsdWVLZXl3b3JkcyA9IGtleVNldCh2YWx1ZUtleXdvcmRzXyk7XG52YXIgYWxsV29yZHMgPSBkb2N1bWVudFR5cGVzXy5jb25jYXQobWVkaWFUeXBlc18pLmNvbmNhdChtZWRpYUZlYXR1cmVzXykuY29uY2F0KG1lZGlhVmFsdWVLZXl3b3Jkc18pLmNvbmNhdChwcm9wZXJ0eUtleXdvcmRzXykuY29uY2F0KG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3Jkc18pLmNvbmNhdChjb2xvcktleXdvcmRzXykuY29uY2F0KHZhbHVlS2V5d29yZHNfKTtcbmV4cG9ydCBjb25zdCBrZXl3b3JkcyA9IHtcbiAgcHJvcGVydGllczogcHJvcGVydHlLZXl3b3Jkc18sXG4gIGNvbG9yczogY29sb3JLZXl3b3Jkc18sXG4gIGZvbnRzOiBmb250UHJvcGVydGllc18sXG4gIHZhbHVlczogdmFsdWVLZXl3b3Jkc18sXG4gIGFsbDogYWxsV29yZHNcbn07XG5jb25zdCBkZWZhdWx0cyA9IHtcbiAgZG9jdW1lbnRUeXBlczogZG9jdW1lbnRUeXBlcyxcbiAgbWVkaWFUeXBlczogbWVkaWFUeXBlcyxcbiAgbWVkaWFGZWF0dXJlczogbWVkaWFGZWF0dXJlcyxcbiAgbWVkaWFWYWx1ZUtleXdvcmRzOiBtZWRpYVZhbHVlS2V5d29yZHMsXG4gIHByb3BlcnR5S2V5d29yZHM6IHByb3BlcnR5S2V5d29yZHMsXG4gIG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3Jkczogbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzLFxuICBmb250UHJvcGVydGllczogZm9udFByb3BlcnRpZXMsXG4gIGNvdW50ZXJEZXNjcmlwdG9yczogY291bnRlckRlc2NyaXB0b3JzLFxuICBjb2xvcktleXdvcmRzOiBjb2xvcktleXdvcmRzLFxuICB2YWx1ZUtleXdvcmRzOiB2YWx1ZUtleXdvcmRzLFxuICB0b2tlbkhvb2tzOiB7XG4gICAgXCIvXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoIXN0cmVhbS5lYXQoXCIqXCIpKSByZXR1cm4gZmFsc2U7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ0NvbW1lbnQ7XG4gICAgICByZXR1cm4gdG9rZW5DQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gIH1cbn07XG5leHBvcnQgY29uc3QgY3NzID0gbWtDU1Moe1xuICBuYW1lOiBcImNzc1wiXG59KTtcbmZ1bmN0aW9uIHRva2VuQ0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAobWF5YmVFbmQgJiYgY2ggPT0gXCIvXCIpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBbXCJjb21tZW50XCIsIFwiY29tbWVudFwiXTtcbn1cbmV4cG9ydCBjb25zdCBzQ1NTID0gbWtDU1Moe1xuICBuYW1lOiBcInNjc3NcIixcbiAgbWVkaWFUeXBlczogbWVkaWFUeXBlcyxcbiAgbWVkaWFGZWF0dXJlczogbWVkaWFGZWF0dXJlcyxcbiAgbWVkaWFWYWx1ZUtleXdvcmRzOiBtZWRpYVZhbHVlS2V5d29yZHMsXG4gIHByb3BlcnR5S2V5d29yZHM6IHByb3BlcnR5S2V5d29yZHMsXG4gIG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3Jkczogbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzLFxuICBjb2xvcktleXdvcmRzOiBjb2xvcktleXdvcmRzLFxuICB2YWx1ZUtleXdvcmRzOiB2YWx1ZUtleXdvcmRzLFxuICBmb250UHJvcGVydGllczogZm9udFByb3BlcnRpZXMsXG4gIGFsbG93TmVzdGVkOiB0cnVlLFxuICBsaW5lQ29tbWVudDogXCIvL1wiLFxuICB0b2tlbkhvb2tzOiB7XG4gICAgXCIvXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gW1wiY29tbWVudFwiLCBcImNvbW1lbnRcIl07XG4gICAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXQoXCIqXCIpKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5DQ29tbWVudDtcbiAgICAgICAgcmV0dXJuIHRva2VuQ0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gW1wib3BlcmF0b3JcIiwgXCJvcGVyYXRvclwiXTtcbiAgICAgIH1cbiAgICB9LFxuICAgIFwiOlwiOiBmdW5jdGlvbiAoc3RyZWFtKSB7XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eXFxzKlxcey8sIGZhbHNlKSkgcmV0dXJuIFtudWxsLCBudWxsXTtcbiAgICAgIHJldHVybiBmYWxzZTtcbiAgICB9LFxuICAgIFwiJFwiOiBmdW5jdGlvbiAoc3RyZWFtKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15bXFx3LV0rLyk7XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eXFxzKjovLCBmYWxzZSkpIHJldHVybiBbXCJkZWZcIiwgXCJ2YXJpYWJsZS1kZWZpbml0aW9uXCJdO1xuICAgICAgcmV0dXJuIFtcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCIsIFwidmFyaWFibGVcIl07XG4gICAgfSxcbiAgICBcIiNcIjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgICAgaWYgKCFzdHJlYW0uZWF0KFwie1wiKSkgcmV0dXJuIGZhbHNlO1xuICAgICAgcmV0dXJuIFtudWxsLCBcImludGVycG9sYXRpb25cIl07XG4gICAgfVxuICB9XG59KTtcbmV4cG9ydCBjb25zdCBsZXNzID0gbWtDU1Moe1xuICBuYW1lOiBcImxlc3NcIixcbiAgbWVkaWFUeXBlczogbWVkaWFUeXBlcyxcbiAgbWVkaWFGZWF0dXJlczogbWVkaWFGZWF0dXJlcyxcbiAgbWVkaWFWYWx1ZUtleXdvcmRzOiBtZWRpYVZhbHVlS2V5d29yZHMsXG4gIHByb3BlcnR5S2V5d29yZHM6IHByb3BlcnR5S2V5d29yZHMsXG4gIG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3Jkczogbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzLFxuICBjb2xvcktleXdvcmRzOiBjb2xvcktleXdvcmRzLFxuICB2YWx1ZUtleXdvcmRzOiB2YWx1ZUtleXdvcmRzLFxuICBmb250UHJvcGVydGllczogZm9udFByb3BlcnRpZXMsXG4gIGFsbG93TmVzdGVkOiB0cnVlLFxuICBsaW5lQ29tbWVudDogXCIvL1wiLFxuICB0b2tlbkhvb2tzOiB7XG4gICAgXCIvXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gW1wiY29tbWVudFwiLCBcImNvbW1lbnRcIl07XG4gICAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXQoXCIqXCIpKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5DQ29tbWVudDtcbiAgICAgICAgcmV0dXJuIHRva2VuQ0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gW1wib3BlcmF0b3JcIiwgXCJvcGVyYXRvclwiXTtcbiAgICAgIH1cbiAgICB9LFxuICAgIFwiQFwiOiBmdW5jdGlvbiAoc3RyZWFtKSB7XG4gICAgICBpZiAoc3RyZWFtLmVhdChcIntcIikpIHJldHVybiBbbnVsbCwgXCJpbnRlcnBvbGF0aW9uXCJdO1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXihjaGFyc2V0fGRvY3VtZW50fGZvbnQtZmFjZXxpbXBvcnR8KC0obW96fG1zfG98d2Via2l0KS0pP2tleWZyYW1lc3xtZWRpYXxuYW1lc3BhY2V8cGFnZXxzdXBwb3J0cylcXGIvaSwgZmFsc2UpKSByZXR1cm4gZmFsc2U7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXFxcXFwtXS8pO1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXlxccyo6LywgZmFsc2UpKSByZXR1cm4gW1wiZGVmXCIsIFwidmFyaWFibGUtZGVmaW5pdGlvblwiXTtcbiAgICAgIHJldHVybiBbXCJ2YXJpYWJsZU5hbWVcIiwgXCJ2YXJpYWJsZVwiXTtcbiAgICB9LFxuICAgIFwiJlwiOiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gW1wiYXRvbVwiLCBcImF0b21cIl07XG4gICAgfVxuICB9XG59KTtcbmV4cG9ydCBjb25zdCBnc3MgPSBta0NTUyh7XG4gIG5hbWU6IFwiZ3NzXCIsXG4gIGRvY3VtZW50VHlwZXM6IGRvY3VtZW50VHlwZXMsXG4gIG1lZGlhVHlwZXM6IG1lZGlhVHlwZXMsXG4gIG1lZGlhRmVhdHVyZXM6IG1lZGlhRmVhdHVyZXMsXG4gIHByb3BlcnR5S2V5d29yZHM6IHByb3BlcnR5S2V5d29yZHMsXG4gIG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3Jkczogbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzLFxuICBmb250UHJvcGVydGllczogZm9udFByb3BlcnRpZXMsXG4gIGNvdW50ZXJEZXNjcmlwdG9yczogY291bnRlckRlc2NyaXB0b3JzLFxuICBjb2xvcktleXdvcmRzOiBjb2xvcktleXdvcmRzLFxuICB2YWx1ZUtleXdvcmRzOiB2YWx1ZUtleXdvcmRzLFxuICBzdXBwb3J0c0F0Q29tcG9uZW50OiB0cnVlLFxuICB0b2tlbkhvb2tzOiB7XG4gICAgXCIvXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoIXN0cmVhbS5lYXQoXCIqXCIpKSByZXR1cm4gZmFsc2U7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ0NvbW1lbnQ7XG4gICAgICByZXR1cm4gdG9rZW5DQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gIH1cbn0pOyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=