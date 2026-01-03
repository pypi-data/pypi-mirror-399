"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9102],{

/***/ 29102
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   stylus: () => (/* binding */ stylus)
/* harmony export */ });
// developer.mozilla.org/en-US/docs/Web/HTML/Element
var tagKeywords_ = ["a", "abbr", "address", "area", "article", "aside", "audio", "b", "base", "bdi", "bdo", "bgsound", "blockquote", "body", "br", "button", "canvas", "caption", "cite", "code", "col", "colgroup", "data", "datalist", "dd", "del", "details", "dfn", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "iframe", "img", "input", "ins", "kbd", "keygen", "label", "legend", "li", "link", "main", "map", "mark", "marquee", "menu", "menuitem", "meta", "meter", "nav", "nobr", "noframes", "noscript", "object", "ol", "optgroup", "option", "output", "p", "param", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "script", "section", "select", "small", "source", "span", "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "textarea", "tfoot", "th", "thead", "time", "tr", "track", "u", "ul", "var", "video"];

// github.com/codemirror/CodeMirror/blob/master/mode/css/css.js
// Note, "url-prefix" should precede "url" in order to match correctly in documentTypesRegexp
var documentTypes_ = ["domain", "regexp", "url-prefix", "url"];
var mediaTypes_ = ["all", "aural", "braille", "handheld", "print", "projection", "screen", "tty", "tv", "embossed"];
var mediaFeatures_ = ["width", "min-width", "max-width", "height", "min-height", "max-height", "device-width", "min-device-width", "max-device-width", "device-height", "min-device-height", "max-device-height", "aspect-ratio", "min-aspect-ratio", "max-aspect-ratio", "device-aspect-ratio", "min-device-aspect-ratio", "max-device-aspect-ratio", "color", "min-color", "max-color", "color-index", "min-color-index", "max-color-index", "monochrome", "min-monochrome", "max-monochrome", "resolution", "min-resolution", "max-resolution", "scan", "grid", "dynamic-range", "video-dynamic-range"];
var propertyKeywords_ = ["align-content", "align-items", "align-self", "alignment-adjust", "alignment-baseline", "anchor-point", "animation", "animation-delay", "animation-direction", "animation-duration", "animation-fill-mode", "animation-iteration-count", "animation-name", "animation-play-state", "animation-timing-function", "appearance", "azimuth", "backface-visibility", "background", "background-attachment", "background-clip", "background-color", "background-image", "background-origin", "background-position", "background-repeat", "background-size", "baseline-shift", "binding", "bleed", "bookmark-label", "bookmark-level", "bookmark-state", "bookmark-target", "border", "border-bottom", "border-bottom-color", "border-bottom-left-radius", "border-bottom-right-radius", "border-bottom-style", "border-bottom-width", "border-collapse", "border-color", "border-image", "border-image-outset", "border-image-repeat", "border-image-slice", "border-image-source", "border-image-width", "border-left", "border-left-color", "border-left-style", "border-left-width", "border-radius", "border-right", "border-right-color", "border-right-style", "border-right-width", "border-spacing", "border-style", "border-top", "border-top-color", "border-top-left-radius", "border-top-right-radius", "border-top-style", "border-top-width", "border-width", "bottom", "box-decoration-break", "box-shadow", "box-sizing", "break-after", "break-before", "break-inside", "caption-side", "clear", "clip", "color", "color-profile", "column-count", "column-fill", "column-gap", "column-rule", "column-rule-color", "column-rule-style", "column-rule-width", "column-span", "column-width", "columns", "content", "counter-increment", "counter-reset", "crop", "cue", "cue-after", "cue-before", "cursor", "direction", "display", "dominant-baseline", "drop-initial-after-adjust", "drop-initial-after-align", "drop-initial-before-adjust", "drop-initial-before-align", "drop-initial-size", "drop-initial-value", "elevation", "empty-cells", "fit", "fit-position", "flex", "flex-basis", "flex-direction", "flex-flow", "flex-grow", "flex-shrink", "flex-wrap", "float", "float-offset", "flow-from", "flow-into", "font", "font-feature-settings", "font-family", "font-kerning", "font-language-override", "font-size", "font-size-adjust", "font-stretch", "font-style", "font-synthesis", "font-variant", "font-variant-alternates", "font-variant-caps", "font-variant-east-asian", "font-variant-ligatures", "font-variant-numeric", "font-variant-position", "font-weight", "grid", "grid-area", "grid-auto-columns", "grid-auto-flow", "grid-auto-position", "grid-auto-rows", "grid-column", "grid-column-end", "grid-column-start", "grid-row", "grid-row-end", "grid-row-start", "grid-template", "grid-template-areas", "grid-template-columns", "grid-template-rows", "hanging-punctuation", "height", "hyphens", "icon", "image-orientation", "image-rendering", "image-resolution", "inline-box-align", "justify-content", "left", "letter-spacing", "line-break", "line-height", "line-stacking", "line-stacking-ruby", "line-stacking-shift", "line-stacking-strategy", "list-style", "list-style-image", "list-style-position", "list-style-type", "margin", "margin-bottom", "margin-left", "margin-right", "margin-top", "marker-offset", "marks", "marquee-direction", "marquee-loop", "marquee-play-count", "marquee-speed", "marquee-style", "max-height", "max-width", "min-height", "min-width", "move-to", "nav-down", "nav-index", "nav-left", "nav-right", "nav-up", "object-fit", "object-position", "opacity", "order", "orphans", "outline", "outline-color", "outline-offset", "outline-style", "outline-width", "overflow", "overflow-style", "overflow-wrap", "overflow-x", "overflow-y", "padding", "padding-bottom", "padding-left", "padding-right", "padding-top", "page", "page-break-after", "page-break-before", "page-break-inside", "page-policy", "pause", "pause-after", "pause-before", "perspective", "perspective-origin", "pitch", "pitch-range", "play-during", "position", "presentation-level", "punctuation-trim", "quotes", "region-break-after", "region-break-before", "region-break-inside", "region-fragment", "rendering-intent", "resize", "rest", "rest-after", "rest-before", "richness", "right", "rotation", "rotation-point", "ruby-align", "ruby-overhang", "ruby-position", "ruby-span", "shape-image-threshold", "shape-inside", "shape-margin", "shape-outside", "size", "speak", "speak-as", "speak-header", "speak-numeral", "speak-punctuation", "speech-rate", "stress", "string-set", "tab-size", "table-layout", "target", "target-name", "target-new", "target-position", "text-align", "text-align-last", "text-decoration", "text-decoration-color", "text-decoration-line", "text-decoration-skip", "text-decoration-style", "text-emphasis", "text-emphasis-color", "text-emphasis-position", "text-emphasis-style", "text-height", "text-indent", "text-justify", "text-outline", "text-overflow", "text-shadow", "text-size-adjust", "text-space-collapse", "text-transform", "text-underline-position", "text-wrap", "top", "transform", "transform-origin", "transform-style", "transition", "transition-delay", "transition-duration", "transition-property", "transition-timing-function", "unicode-bidi", "vertical-align", "visibility", "voice-balance", "voice-duration", "voice-family", "voice-pitch", "voice-range", "voice-rate", "voice-stress", "voice-volume", "volume", "white-space", "widows", "width", "will-change", "word-break", "word-spacing", "word-wrap", "z-index", "clip-path", "clip-rule", "mask", "enable-background", "filter", "flood-color", "flood-opacity", "lighting-color", "stop-color", "stop-opacity", "pointer-events", "color-interpolation", "color-interpolation-filters", "color-rendering", "fill", "fill-opacity", "fill-rule", "image-rendering", "marker", "marker-end", "marker-mid", "marker-start", "shape-rendering", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "text-rendering", "baseline-shift", "dominant-baseline", "glyph-orientation-horizontal", "glyph-orientation-vertical", "text-anchor", "writing-mode", "font-smoothing", "osx-font-smoothing"];
var nonStandardPropertyKeywords_ = ["scrollbar-arrow-color", "scrollbar-base-color", "scrollbar-dark-shadow-color", "scrollbar-face-color", "scrollbar-highlight-color", "scrollbar-shadow-color", "scrollbar-3d-light-color", "scrollbar-track-color", "shape-inside", "searchfield-cancel-button", "searchfield-decoration", "searchfield-results-button", "searchfield-results-decoration", "zoom"];
var fontProperties_ = ["font-family", "src", "unicode-range", "font-variant", "font-feature-settings", "font-stretch", "font-weight", "font-style"];
var colorKeywords_ = ["aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanchedalmond", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod", "gray", "grey", "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple", "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "snow", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow", "yellowgreen"];
var valueKeywords_ = ["above", "absolute", "activeborder", "additive", "activecaption", "afar", "after-white-space", "ahead", "alias", "all", "all-scroll", "alphabetic", "alternate", "always", "amharic", "amharic-abegede", "antialiased", "appworkspace", "arabic-indic", "armenian", "asterisks", "attr", "auto", "avoid", "avoid-column", "avoid-page", "avoid-region", "background", "backwards", "baseline", "below", "bidi-override", "binary", "bengali", "blink", "block", "block-axis", "bold", "bolder", "border", "border-box", "both", "bottom", "break", "break-all", "break-word", "bullets", "button", "buttonface", "buttonhighlight", "buttonshadow", "buttontext", "calc", "cambodian", "capitalize", "caps-lock-indicator", "caption", "captiontext", "caret", "cell", "center", "checkbox", "circle", "cjk-decimal", "cjk-earthly-branch", "cjk-heavenly-stem", "cjk-ideographic", "clear", "clip", "close-quote", "col-resize", "collapse", "column", "compact", "condensed", "conic-gradient", "contain", "content", "contents", "content-box", "context-menu", "continuous", "copy", "counter", "counters", "cover", "crop", "cross", "crosshair", "currentcolor", "cursive", "cyclic", "dashed", "decimal", "decimal-leading-zero", "default", "default-button", "destination-atop", "destination-in", "destination-out", "destination-over", "devanagari", "disc", "discard", "disclosure-closed", "disclosure-open", "document", "dot-dash", "dot-dot-dash", "dotted", "double", "down", "e-resize", "ease", "ease-in", "ease-in-out", "ease-out", "element", "ellipse", "ellipsis", "embed", "end", "ethiopic", "ethiopic-abegede", "ethiopic-abegede-am-et", "ethiopic-abegede-gez", "ethiopic-abegede-ti-er", "ethiopic-abegede-ti-et", "ethiopic-halehame-aa-er", "ethiopic-halehame-aa-et", "ethiopic-halehame-am-et", "ethiopic-halehame-gez", "ethiopic-halehame-om-et", "ethiopic-halehame-sid-et", "ethiopic-halehame-so-et", "ethiopic-halehame-ti-er", "ethiopic-halehame-ti-et", "ethiopic-halehame-tig", "ethiopic-numeric", "ew-resize", "expanded", "extends", "extra-condensed", "extra-expanded", "fantasy", "fast", "fill", "fixed", "flat", "flex", "footnotes", "forwards", "from", "geometricPrecision", "georgian", "graytext", "groove", "gujarati", "gurmukhi", "hand", "hangul", "hangul-consonant", "hebrew", "help", "hidden", "hide", "high", "higher", "highlight", "highlighttext", "hiragana", "hiragana-iroha", "horizontal", "hsl", "hsla", "icon", "ignore", "inactiveborder", "inactivecaption", "inactivecaptiontext", "infinite", "infobackground", "infotext", "inherit", "initial", "inline", "inline-axis", "inline-block", "inline-flex", "inline-table", "inset", "inside", "intrinsic", "invert", "italic", "japanese-formal", "japanese-informal", "justify", "kannada", "katakana", "katakana-iroha", "keep-all", "khmer", "korean-hangul-formal", "korean-hanja-formal", "korean-hanja-informal", "landscape", "lao", "large", "larger", "left", "level", "lighter", "line-through", "linear", "linear-gradient", "lines", "list-item", "listbox", "listitem", "local", "logical", "loud", "lower", "lower-alpha", "lower-armenian", "lower-greek", "lower-hexadecimal", "lower-latin", "lower-norwegian", "lower-roman", "lowercase", "ltr", "malayalam", "match", "matrix", "matrix3d", "media-play-button", "media-slider", "media-sliderthumb", "media-volume-slider", "media-volume-sliderthumb", "medium", "menu", "menulist", "menulist-button", "menutext", "message-box", "middle", "min-intrinsic", "mix", "mongolian", "monospace", "move", "multiple", "myanmar", "n-resize", "narrower", "ne-resize", "nesw-resize", "no-close-quote", "no-drop", "no-open-quote", "no-repeat", "none", "normal", "not-allowed", "nowrap", "ns-resize", "numbers", "numeric", "nw-resize", "nwse-resize", "oblique", "octal", "open-quote", "optimizeLegibility", "optimizeSpeed", "oriya", "oromo", "outset", "outside", "outside-shape", "overlay", "overline", "padding", "padding-box", "painted", "page", "paused", "persian", "perspective", "plus-darker", "plus-lighter", "pointer", "polygon", "portrait", "pre", "pre-line", "pre-wrap", "preserve-3d", "progress", "push-button", "radial-gradient", "radio", "read-only", "read-write", "read-write-plaintext-only", "rectangle", "region", "relative", "repeat", "repeating-linear-gradient", "repeating-radial-gradient", "repeating-conic-gradient", "repeat-x", "repeat-y", "reset", "reverse", "rgb", "rgba", "ridge", "right", "rotate", "rotate3d", "rotateX", "rotateY", "rotateZ", "round", "row-resize", "rtl", "run-in", "running", "s-resize", "sans-serif", "scale", "scale3d", "scaleX", "scaleY", "scaleZ", "scroll", "scrollbar", "scroll-position", "se-resize", "searchfield", "searchfield-cancel-button", "searchfield-decoration", "searchfield-results-button", "searchfield-results-decoration", "semi-condensed", "semi-expanded", "separate", "serif", "show", "sidama", "simp-chinese-formal", "simp-chinese-informal", "single", "skew", "skewX", "skewY", "skip-white-space", "slide", "slider-horizontal", "slider-vertical", "sliderthumb-horizontal", "sliderthumb-vertical", "slow", "small", "small-caps", "small-caption", "smaller", "solid", "somali", "source-atop", "source-in", "source-out", "source-over", "space", "spell-out", "square", "square-button", "standard", "start", "static", "status-bar", "stretch", "stroke", "sub", "subpixel-antialiased", "super", "sw-resize", "symbolic", "symbols", "table", "table-caption", "table-cell", "table-column", "table-column-group", "table-footer-group", "table-header-group", "table-row", "table-row-group", "tamil", "telugu", "text", "text-bottom", "text-top", "textarea", "textfield", "thai", "thick", "thin", "threeddarkshadow", "threedface", "threedhighlight", "threedlightshadow", "threedshadow", "tibetan", "tigre", "tigrinya-er", "tigrinya-er-abegede", "tigrinya-et", "tigrinya-et-abegede", "to", "top", "trad-chinese-formal", "trad-chinese-informal", "translate", "translate3d", "translateX", "translateY", "translateZ", "transparent", "ultra-condensed", "ultra-expanded", "underline", "up", "upper-alpha", "upper-armenian", "upper-greek", "upper-hexadecimal", "upper-latin", "upper-norwegian", "upper-roman", "uppercase", "urdu", "url", "var", "vertical", "vertical-text", "visible", "visibleFill", "visiblePainted", "visibleStroke", "visual", "w-resize", "wait", "wave", "wider", "window", "windowframe", "windowtext", "words", "x-large", "x-small", "xor", "xx-large", "xx-small", "bicubic", "optimizespeed", "grayscale", "row", "row-reverse", "wrap", "wrap-reverse", "column-reverse", "flex-start", "flex-end", "space-between", "space-around", "unset"];
var wordOperatorKeywords_ = ["in", "and", "or", "not", "is not", "is a", "is", "isnt", "defined", "if unless"],
  blockKeywords_ = ["for", "if", "else", "unless", "from", "to"],
  commonAtoms_ = ["null", "true", "false", "href", "title", "type", "not-allowed", "readonly", "disabled"],
  commonDef_ = ["@font-face", "@keyframes", "@media", "@viewport", "@page", "@host", "@supports", "@block", "@css"];
var hintWords = tagKeywords_.concat(documentTypes_, mediaTypes_, mediaFeatures_, propertyKeywords_, nonStandardPropertyKeywords_, colorKeywords_, valueKeywords_, fontProperties_, wordOperatorKeywords_, blockKeywords_, commonAtoms_, commonDef_);
function wordRegexp(words) {
  words = words.sort(function (a, b) {
    return b > a;
  });
  return new RegExp("^((" + words.join(")|(") + "))\\b");
}
function keySet(array) {
  var keys = {};
  for (var i = 0; i < array.length; ++i) keys[array[i]] = true;
  return keys;
}
function escapeRegExp(text) {
  return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
}
var tagKeywords = keySet(tagKeywords_),
  tagVariablesRegexp = /^(a|b|i|s|col|em)$/i,
  propertyKeywords = keySet(propertyKeywords_),
  nonStandardPropertyKeywords = keySet(nonStandardPropertyKeywords_),
  valueKeywords = keySet(valueKeywords_),
  colorKeywords = keySet(colorKeywords_),
  documentTypes = keySet(documentTypes_),
  documentTypesRegexp = wordRegexp(documentTypes_),
  mediaFeatures = keySet(mediaFeatures_),
  mediaTypes = keySet(mediaTypes_),
  fontProperties = keySet(fontProperties_),
  operatorsRegexp = /^\s*([.]{2,3}|&&|\|\||\*\*|[?!=:]?=|[-+*\/%<>]=?|\?:|\~)/,
  wordOperatorKeywordsRegexp = wordRegexp(wordOperatorKeywords_),
  blockKeywords = keySet(blockKeywords_),
  vendorPrefixesRegexp = new RegExp(/^\-(moz|ms|o|webkit)-/i),
  commonAtoms = keySet(commonAtoms_),
  firstWordMatch = "",
  states = {},
  ch,
  style,
  type,
  override;

/**
 * Tokenizers
 */
function tokenBase(stream, state) {
  firstWordMatch = stream.string.match(/(^[\w-]+\s*=\s*$)|(^\s*[\w-]+\s*=\s*[\w-])|(^\s*(\.|#|@|\$|\&|\[|\d|\+|::?|\{|\>|~|\/)?\s*[\w-]*([a-z0-9-]|\*|\/\*)(\(|,)?)/);
  state.context.line.firstWord = firstWordMatch ? firstWordMatch[0].replace(/^\s*/, "") : "";
  state.context.line.indent = stream.indentation();
  ch = stream.peek();

  // Line comment
  if (stream.match("//")) {
    stream.skipToEnd();
    return ["comment", "comment"];
  }
  // Block comment
  if (stream.match("/*")) {
    state.tokenize = tokenCComment;
    return tokenCComment(stream, state);
  }
  // String
  if (ch == "\"" || ch == "'") {
    stream.next();
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  // Def
  if (ch == "@") {
    stream.next();
    stream.eatWhile(/[\w\\-]/);
    return ["def", stream.current()];
  }
  // ID selector or Hex color
  if (ch == "#") {
    stream.next();
    // Hex color
    if (stream.match(/^[0-9a-f]{3}([0-9a-f]([0-9a-f]{2}){0,2})?\b(?!-)/i)) {
      return ["atom", "atom"];
    }
    // ID selector
    if (stream.match(/^[a-z][\w-]*/i)) {
      return ["builtin", "hash"];
    }
  }
  // Vendor prefixes
  if (stream.match(vendorPrefixesRegexp)) {
    return ["meta", "vendor-prefixes"];
  }
  // Numbers
  if (stream.match(/^-?[0-9]?\.?[0-9]/)) {
    stream.eatWhile(/[a-z%]/i);
    return ["number", "unit"];
  }
  // !important|optional
  if (ch == "!") {
    stream.next();
    return [stream.match(/^(important|optional)/i) ? "keyword" : "operator", "important"];
  }
  // Class
  if (ch == "." && stream.match(/^\.[a-z][\w-]*/i)) {
    return ["qualifier", "qualifier"];
  }
  // url url-prefix domain regexp
  if (stream.match(documentTypesRegexp)) {
    if (stream.peek() == "(") state.tokenize = tokenParenthesized;
    return ["property", "word"];
  }
  // Mixins / Functions
  if (stream.match(/^[a-z][\w-]*\(/i)) {
    stream.backUp(1);
    return ["keyword", "mixin"];
  }
  // Block mixins
  if (stream.match(/^(\+|-)[a-z][\w-]*\(/i)) {
    stream.backUp(1);
    return ["keyword", "block-mixin"];
  }
  // Parent Reference BEM naming
  if (stream.string.match(/^\s*&/) && stream.match(/^[-_]+[a-z][\w-]*/)) {
    return ["qualifier", "qualifier"];
  }
  // / Root Reference & Parent Reference
  if (stream.match(/^(\/|&)(-|_|:|\.|#|[a-z])/)) {
    stream.backUp(1);
    return ["variableName.special", "reference"];
  }
  if (stream.match(/^&{1}\s*$/)) {
    return ["variableName.special", "reference"];
  }
  // Word operator
  if (stream.match(wordOperatorKeywordsRegexp)) {
    return ["operator", "operator"];
  }
  // Word
  if (stream.match(/^\$?[-_]*[a-z0-9]+[\w-]*/i)) {
    // Variable
    if (stream.match(/^(\.|\[)[\w-\'\"\]]+/i, false)) {
      if (!wordIsTag(stream.current())) {
        stream.match('.');
        return ["variable", "variable-name"];
      }
    }
    return ["variable", "word"];
  }
  // Operators
  if (stream.match(operatorsRegexp)) {
    return ["operator", stream.current()];
  }
  // Delimiters
  if (/[:;,{}\[\]\(\)]/.test(ch)) {
    stream.next();
    return [null, ch];
  }
  // Non-detected items
  stream.next();
  return [null, null];
}

/**
 * Token comment
 */
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

/**
 * Token string
 */
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
    return ["string", "string"];
  };
}

/**
 * Token parenthesized
 */
function tokenParenthesized(stream, state) {
  stream.next(); // Must be "("
  if (!stream.match(/\s*[\"\')]/, false)) state.tokenize = tokenString(")");else state.tokenize = null;
  return [null, "("];
}

/**
 * Context management
 */
function Context(type, indent, prev, line) {
  this.type = type;
  this.indent = indent;
  this.prev = prev;
  this.line = line || {
    firstWord: "",
    indent: 0
  };
}
function pushContext(state, stream, type, indent) {
  indent = indent >= 0 ? indent : stream.indentUnit;
  state.context = new Context(type, stream.indentation() + indent, state.context);
  return type;
}
function popContext(state, stream, currentIndent) {
  var contextIndent = state.context.indent - stream.indentUnit;
  currentIndent = currentIndent || false;
  state.context = state.context.prev;
  if (currentIndent) state.context.indent = contextIndent;
  return state.context.type;
}
function pass(type, stream, state) {
  return states[state.context.type](type, stream, state);
}
function popAndPass(type, stream, state, n) {
  for (var i = n || 1; i > 0; i--) state.context = state.context.prev;
  return pass(type, stream, state);
}

/**
 * Parser
 */
function wordIsTag(word) {
  return word.toLowerCase() in tagKeywords;
}
function wordIsProperty(word) {
  word = word.toLowerCase();
  return word in propertyKeywords || word in fontProperties;
}
function wordIsBlock(word) {
  return word.toLowerCase() in blockKeywords;
}
function wordIsVendorPrefix(word) {
  return word.toLowerCase().match(vendorPrefixesRegexp);
}
function wordAsValue(word) {
  var wordLC = word.toLowerCase();
  var override = "variable";
  if (wordIsTag(word)) override = "tag";else if (wordIsBlock(word)) override = "block-keyword";else if (wordIsProperty(word)) override = "property";else if (wordLC in valueKeywords || wordLC in commonAtoms) override = "atom";else if (wordLC == "return" || wordLC in colorKeywords) override = "keyword";

  // Font family
  else if (word.match(/^[A-Z]/)) override = "string";
  return override;
}
function typeIsBlock(type, stream) {
  return endOfLine(stream) && (type == "{" || type == "]" || type == "hash" || type == "qualifier") || type == "block-mixin";
}
function typeIsInterpolation(type, stream) {
  return type == "{" && stream.match(/^\s*\$?[\w-]+/i, false);
}
function typeIsPseudo(type, stream) {
  return type == ":" && stream.match(/^[a-z-]+/, false);
}
function startOfLine(stream) {
  return stream.sol() || stream.string.match(new RegExp("^\\s*" + escapeRegExp(stream.current())));
}
function endOfLine(stream) {
  return stream.eol() || stream.match(/^\s*$/, false);
}
function firstWordOfLine(line) {
  var re = /^\s*[-_]*[a-z0-9]+[\w-]*/i;
  var result = typeof line == "string" ? line.match(re) : line.string.match(re);
  return result ? result[0].replace(/^\s*/, "") : "";
}

/**
 * Block
 */
states.block = function (type, stream, state) {
  if (type == "comment" && startOfLine(stream) || type == "," && endOfLine(stream) || type == "mixin") {
    return pushContext(state, stream, "block", 0);
  }
  if (typeIsInterpolation(type, stream)) {
    return pushContext(state, stream, "interpolation");
  }
  if (endOfLine(stream) && type == "]") {
    if (!/^\s*(\.|#|:|\[|\*|&)/.test(stream.string) && !wordIsTag(firstWordOfLine(stream))) {
      return pushContext(state, stream, "block", 0);
    }
  }
  if (typeIsBlock(type, stream)) {
    return pushContext(state, stream, "block");
  }
  if (type == "}" && endOfLine(stream)) {
    return pushContext(state, stream, "block", 0);
  }
  if (type == "variable-name") {
    if (stream.string.match(/^\s?\$[\w-\.\[\]\'\"]+$/) || wordIsBlock(firstWordOfLine(stream))) {
      return pushContext(state, stream, "variableName");
    } else {
      return pushContext(state, stream, "variableName", 0);
    }
  }
  if (type == "=") {
    if (!endOfLine(stream) && !wordIsBlock(firstWordOfLine(stream))) {
      return pushContext(state, stream, "block", 0);
    }
    return pushContext(state, stream, "block");
  }
  if (type == "*") {
    if (endOfLine(stream) || stream.match(/\s*(,|\.|#|\[|:|{)/, false)) {
      override = "tag";
      return pushContext(state, stream, "block");
    }
  }
  if (typeIsPseudo(type, stream)) {
    return pushContext(state, stream, "pseudo");
  }
  if (/@(font-face|media|supports|(-moz-)?document)/.test(type)) {
    return pushContext(state, stream, endOfLine(stream) ? "block" : "atBlock");
  }
  if (/@(-(moz|ms|o|webkit)-)?keyframes$/.test(type)) {
    return pushContext(state, stream, "keyframes");
  }
  if (/@extends?/.test(type)) {
    return pushContext(state, stream, "extend", 0);
  }
  if (type && type.charAt(0) == "@") {
    // Property Lookup
    if (stream.indentation() > 0 && wordIsProperty(stream.current().slice(1))) {
      override = "variable";
      return "block";
    }
    if (/(@import|@require|@charset)/.test(type)) {
      return pushContext(state, stream, "block", 0);
    }
    return pushContext(state, stream, "block");
  }
  if (type == "reference" && endOfLine(stream)) {
    return pushContext(state, stream, "block");
  }
  if (type == "(") {
    return pushContext(state, stream, "parens");
  }
  if (type == "vendor-prefixes") {
    return pushContext(state, stream, "vendorPrefixes");
  }
  if (type == "word") {
    var word = stream.current();
    override = wordAsValue(word);
    if (override == "property") {
      if (startOfLine(stream)) {
        return pushContext(state, stream, "block", 0);
      } else {
        override = "atom";
        return "block";
      }
    }
    if (override == "tag") {
      // tag is a css value
      if (/embed|menu|pre|progress|sub|table/.test(word)) {
        if (wordIsProperty(firstWordOfLine(stream))) {
          override = "atom";
          return "block";
        }
      }

      // tag is an attribute
      if (stream.string.match(new RegExp("\\[\\s*" + word + "|" + word + "\\s*\\]"))) {
        override = "atom";
        return "block";
      }

      // tag is a variable
      if (tagVariablesRegexp.test(word)) {
        if (startOfLine(stream) && stream.string.match(/=/) || !startOfLine(stream) && !stream.string.match(/^(\s*\.|#|\&|\[|\/|>|\*)/) && !wordIsTag(firstWordOfLine(stream))) {
          override = "variable";
          if (wordIsBlock(firstWordOfLine(stream))) return "block";
          return pushContext(state, stream, "block", 0);
        }
      }
      if (endOfLine(stream)) return pushContext(state, stream, "block");
    }
    if (override == "block-keyword") {
      override = "keyword";

      // Postfix conditionals
      if (stream.current(/(if|unless)/) && !startOfLine(stream)) {
        return "block";
      }
      return pushContext(state, stream, "block");
    }
    if (word == "return") return pushContext(state, stream, "block", 0);

    // Placeholder selector
    if (override == "variable" && stream.string.match(/^\s?\$[\w-\.\[\]\'\"]+$/)) {
      return pushContext(state, stream, "block");
    }
  }
  return state.context.type;
};

/**
 * Parens
 */
states.parens = function (type, stream, state) {
  if (type == "(") return pushContext(state, stream, "parens");
  if (type == ")") {
    if (state.context.prev.type == "parens") {
      return popContext(state, stream);
    }
    if (stream.string.match(/^[a-z][\w-]*\(/i) && endOfLine(stream) || wordIsBlock(firstWordOfLine(stream)) || /(\.|#|:|\[|\*|&|>|~|\+|\/)/.test(firstWordOfLine(stream)) || !stream.string.match(/^-?[a-z][\w-\.\[\]\'\"]*\s*=/) && wordIsTag(firstWordOfLine(stream))) {
      return pushContext(state, stream, "block");
    }
    if (stream.string.match(/^[\$-]?[a-z][\w-\.\[\]\'\"]*\s*=/) || stream.string.match(/^\s*(\(|\)|[0-9])/) || stream.string.match(/^\s+[a-z][\w-]*\(/i) || stream.string.match(/^\s+[\$-]?[a-z]/i)) {
      return pushContext(state, stream, "block", 0);
    }
    if (endOfLine(stream)) return pushContext(state, stream, "block");else return pushContext(state, stream, "block", 0);
  }
  if (type && type.charAt(0) == "@" && wordIsProperty(stream.current().slice(1))) {
    override = "variable";
  }
  if (type == "word") {
    var word = stream.current();
    override = wordAsValue(word);
    if (override == "tag" && tagVariablesRegexp.test(word)) {
      override = "variable";
    }
    if (override == "property" || word == "to") override = "atom";
  }
  if (type == "variable-name") {
    return pushContext(state, stream, "variableName");
  }
  if (typeIsPseudo(type, stream)) {
    return pushContext(state, stream, "pseudo");
  }
  return state.context.type;
};

/**
 * Vendor prefixes
 */
states.vendorPrefixes = function (type, stream, state) {
  if (type == "word") {
    override = "property";
    return pushContext(state, stream, "block", 0);
  }
  return popContext(state, stream);
};

/**
 * Pseudo
 */
states.pseudo = function (type, stream, state) {
  if (!wordIsProperty(firstWordOfLine(stream.string))) {
    stream.match(/^[a-z-]+/);
    override = "variableName.special";
    if (endOfLine(stream)) return pushContext(state, stream, "block");
    return popContext(state, stream);
  }
  return popAndPass(type, stream, state);
};

/**
 * atBlock
 */
states.atBlock = function (type, stream, state) {
  if (type == "(") return pushContext(state, stream, "atBlock_parens");
  if (typeIsBlock(type, stream)) {
    return pushContext(state, stream, "block");
  }
  if (typeIsInterpolation(type, stream)) {
    return pushContext(state, stream, "interpolation");
  }
  if (type == "word") {
    var word = stream.current().toLowerCase();
    if (/^(only|not|and|or)$/.test(word)) override = "keyword";else if (documentTypes.hasOwnProperty(word)) override = "tag";else if (mediaTypes.hasOwnProperty(word)) override = "attribute";else if (mediaFeatures.hasOwnProperty(word)) override = "property";else if (nonStandardPropertyKeywords.hasOwnProperty(word)) override = "string.special";else override = wordAsValue(stream.current());
    if (override == "tag" && endOfLine(stream)) {
      return pushContext(state, stream, "block");
    }
  }
  if (type == "operator" && /^(not|and|or)$/.test(stream.current())) {
    override = "keyword";
  }
  return state.context.type;
};
states.atBlock_parens = function (type, stream, state) {
  if (type == "{" || type == "}") return state.context.type;
  if (type == ")") {
    if (endOfLine(stream)) return pushContext(state, stream, "block");else return pushContext(state, stream, "atBlock");
  }
  if (type == "word") {
    var word = stream.current().toLowerCase();
    override = wordAsValue(word);
    if (/^(max|min)/.test(word)) override = "property";
    if (override == "tag") {
      tagVariablesRegexp.test(word) ? override = "variable" : override = "atom";
    }
    return state.context.type;
  }
  return states.atBlock(type, stream, state);
};

/**
 * Keyframes
 */
states.keyframes = function (type, stream, state) {
  if (stream.indentation() == "0" && (type == "}" && startOfLine(stream) || type == "]" || type == "hash" || type == "qualifier" || wordIsTag(stream.current()))) {
    return popAndPass(type, stream, state);
  }
  if (type == "{") return pushContext(state, stream, "keyframes");
  if (type == "}") {
    if (startOfLine(stream)) return popContext(state, stream, true);else return pushContext(state, stream, "keyframes");
  }
  if (type == "unit" && /^[0-9]+\%$/.test(stream.current())) {
    return pushContext(state, stream, "keyframes");
  }
  if (type == "word") {
    override = wordAsValue(stream.current());
    if (override == "block-keyword") {
      override = "keyword";
      return pushContext(state, stream, "keyframes");
    }
  }
  if (/@(font-face|media|supports|(-moz-)?document)/.test(type)) {
    return pushContext(state, stream, endOfLine(stream) ? "block" : "atBlock");
  }
  if (type == "mixin") {
    return pushContext(state, stream, "block", 0);
  }
  return state.context.type;
};

/**
 * Interpolation
 */
states.interpolation = function (type, stream, state) {
  if (type == "{") popContext(state, stream) && pushContext(state, stream, "block");
  if (type == "}") {
    if (stream.string.match(/^\s*(\.|#|:|\[|\*|&|>|~|\+|\/)/i) || stream.string.match(/^\s*[a-z]/i) && wordIsTag(firstWordOfLine(stream))) {
      return pushContext(state, stream, "block");
    }
    if (!stream.string.match(/^(\{|\s*\&)/) || stream.match(/\s*[\w-]/, false)) {
      return pushContext(state, stream, "block", 0);
    }
    return pushContext(state, stream, "block");
  }
  if (type == "variable-name") {
    return pushContext(state, stream, "variableName", 0);
  }
  if (type == "word") {
    override = wordAsValue(stream.current());
    if (override == "tag") override = "atom";
  }
  return state.context.type;
};

/**
 * Extend/s
 */
states.extend = function (type, stream, state) {
  if (type == "[" || type == "=") return "extend";
  if (type == "]") return popContext(state, stream);
  if (type == "word") {
    override = wordAsValue(stream.current());
    return "extend";
  }
  return popContext(state, stream);
};

/**
 * Variable name
 */
states.variableName = function (type, stream, state) {
  if (type == "string" || type == "[" || type == "]" || stream.current().match(/^(\.|\$)/)) {
    if (stream.current().match(/^\.[\w-]+/i)) override = "variable";
    return "variableName";
  }
  return popAndPass(type, stream, state);
};
const stylus = {
  name: "stylus",
  startState: function () {
    return {
      tokenize: null,
      state: "block",
      context: new Context("block", 0, null)
    };
  },
  token: function (stream, state) {
    if (!state.tokenize && stream.eatSpace()) return null;
    style = (state.tokenize || tokenBase)(stream, state);
    if (style && typeof style == "object") {
      type = style[1];
      style = style[0];
    }
    override = style;
    state.state = states[state.state](type, stream, state);
    return override;
  },
  indent: function (state, textAfter, iCx) {
    var cx = state.context,
      ch = textAfter && textAfter.charAt(0),
      indent = cx.indent,
      lineFirstWord = firstWordOfLine(textAfter),
      lineIndent = cx.line.indent,
      prevLineFirstWord = state.context.prev ? state.context.prev.line.firstWord : "",
      prevLineIndent = state.context.prev ? state.context.prev.line.indent : lineIndent;
    if (cx.prev && (ch == "}" && (cx.type == "block" || cx.type == "atBlock" || cx.type == "keyframes") || ch == ")" && (cx.type == "parens" || cx.type == "atBlock_parens") || ch == "{" && cx.type == "at")) {
      indent = cx.indent - iCx.unit;
    } else if (!/(\})/.test(ch)) {
      if (/@|\$|\d/.test(ch) || /^\{/.test(textAfter) || /^\s*\/(\/|\*)/.test(textAfter) || /^\s*\/\*/.test(prevLineFirstWord) || /^\s*[\w-\.\[\]\'\"]+\s*(\?|:|\+)?=/i.test(textAfter) || /^(\+|-)?[a-z][\w-]*\(/i.test(textAfter) || /^return/.test(textAfter) || wordIsBlock(lineFirstWord)) {
        indent = lineIndent;
      } else if (/(\.|#|:|\[|\*|&|>|~|\+|\/)/.test(ch) || wordIsTag(lineFirstWord)) {
        if (/\,\s*$/.test(prevLineFirstWord)) {
          indent = prevLineIndent;
        } else if (/(\.|#|:|\[|\*|&|>|~|\+|\/)/.test(prevLineFirstWord) || wordIsTag(prevLineFirstWord)) {
          indent = lineIndent <= prevLineIndent ? prevLineIndent : prevLineIndent + iCx.unit;
        } else {
          indent = lineIndent;
        }
      } else if (!/,\s*$/.test(textAfter) && (wordIsVendorPrefix(lineFirstWord) || wordIsProperty(lineFirstWord))) {
        if (wordIsBlock(prevLineFirstWord)) {
          indent = lineIndent <= prevLineIndent ? prevLineIndent : prevLineIndent + iCx.unit;
        } else if (/^\{/.test(prevLineFirstWord)) {
          indent = lineIndent <= prevLineIndent ? lineIndent : prevLineIndent + iCx.unit;
        } else if (wordIsVendorPrefix(prevLineFirstWord) || wordIsProperty(prevLineFirstWord)) {
          indent = lineIndent >= prevLineIndent ? prevLineIndent : lineIndent;
        } else if (/^(\.|#|:|\[|\*|&|@|\+|\-|>|~|\/)/.test(prevLineFirstWord) || /=\s*$/.test(prevLineFirstWord) || wordIsTag(prevLineFirstWord) || /^\$[\w-\.\[\]\'\"]/.test(prevLineFirstWord)) {
          indent = prevLineIndent + iCx.unit;
        } else {
          indent = lineIndent;
        }
      }
    }
    return indent;
  },
  languageData: {
    indentOnInput: /^\s*\}$/,
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    },
    autocomplete: hintWords
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTEwMi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9zdHlsdXMuanMiXSwic291cmNlc0NvbnRlbnQiOlsiLy8gZGV2ZWxvcGVyLm1vemlsbGEub3JnL2VuLVVTL2RvY3MvV2ViL0hUTUwvRWxlbWVudFxudmFyIHRhZ0tleXdvcmRzXyA9IFtcImFcIiwgXCJhYmJyXCIsIFwiYWRkcmVzc1wiLCBcImFyZWFcIiwgXCJhcnRpY2xlXCIsIFwiYXNpZGVcIiwgXCJhdWRpb1wiLCBcImJcIiwgXCJiYXNlXCIsIFwiYmRpXCIsIFwiYmRvXCIsIFwiYmdzb3VuZFwiLCBcImJsb2NrcXVvdGVcIiwgXCJib2R5XCIsIFwiYnJcIiwgXCJidXR0b25cIiwgXCJjYW52YXNcIiwgXCJjYXB0aW9uXCIsIFwiY2l0ZVwiLCBcImNvZGVcIiwgXCJjb2xcIiwgXCJjb2xncm91cFwiLCBcImRhdGFcIiwgXCJkYXRhbGlzdFwiLCBcImRkXCIsIFwiZGVsXCIsIFwiZGV0YWlsc1wiLCBcImRmblwiLCBcImRpdlwiLCBcImRsXCIsIFwiZHRcIiwgXCJlbVwiLCBcImVtYmVkXCIsIFwiZmllbGRzZXRcIiwgXCJmaWdjYXB0aW9uXCIsIFwiZmlndXJlXCIsIFwiZm9vdGVyXCIsIFwiZm9ybVwiLCBcImgxXCIsIFwiaDJcIiwgXCJoM1wiLCBcImg0XCIsIFwiaDVcIiwgXCJoNlwiLCBcImhlYWRcIiwgXCJoZWFkZXJcIiwgXCJoZ3JvdXBcIiwgXCJoclwiLCBcImh0bWxcIiwgXCJpXCIsIFwiaWZyYW1lXCIsIFwiaW1nXCIsIFwiaW5wdXRcIiwgXCJpbnNcIiwgXCJrYmRcIiwgXCJrZXlnZW5cIiwgXCJsYWJlbFwiLCBcImxlZ2VuZFwiLCBcImxpXCIsIFwibGlua1wiLCBcIm1haW5cIiwgXCJtYXBcIiwgXCJtYXJrXCIsIFwibWFycXVlZVwiLCBcIm1lbnVcIiwgXCJtZW51aXRlbVwiLCBcIm1ldGFcIiwgXCJtZXRlclwiLCBcIm5hdlwiLCBcIm5vYnJcIiwgXCJub2ZyYW1lc1wiLCBcIm5vc2NyaXB0XCIsIFwib2JqZWN0XCIsIFwib2xcIiwgXCJvcHRncm91cFwiLCBcIm9wdGlvblwiLCBcIm91dHB1dFwiLCBcInBcIiwgXCJwYXJhbVwiLCBcInByZVwiLCBcInByb2dyZXNzXCIsIFwicVwiLCBcInJwXCIsIFwicnRcIiwgXCJydWJ5XCIsIFwic1wiLCBcInNhbXBcIiwgXCJzY3JpcHRcIiwgXCJzZWN0aW9uXCIsIFwic2VsZWN0XCIsIFwic21hbGxcIiwgXCJzb3VyY2VcIiwgXCJzcGFuXCIsIFwic3Ryb25nXCIsIFwic3R5bGVcIiwgXCJzdWJcIiwgXCJzdW1tYXJ5XCIsIFwic3VwXCIsIFwidGFibGVcIiwgXCJ0Ym9keVwiLCBcInRkXCIsIFwidGV4dGFyZWFcIiwgXCJ0Zm9vdFwiLCBcInRoXCIsIFwidGhlYWRcIiwgXCJ0aW1lXCIsIFwidHJcIiwgXCJ0cmFja1wiLCBcInVcIiwgXCJ1bFwiLCBcInZhclwiLCBcInZpZGVvXCJdO1xuXG4vLyBnaXRodWIuY29tL2NvZGVtaXJyb3IvQ29kZU1pcnJvci9ibG9iL21hc3Rlci9tb2RlL2Nzcy9jc3MuanNcbi8vIE5vdGUsIFwidXJsLXByZWZpeFwiIHNob3VsZCBwcmVjZWRlIFwidXJsXCIgaW4gb3JkZXIgdG8gbWF0Y2ggY29ycmVjdGx5IGluIGRvY3VtZW50VHlwZXNSZWdleHBcbnZhciBkb2N1bWVudFR5cGVzXyA9IFtcImRvbWFpblwiLCBcInJlZ2V4cFwiLCBcInVybC1wcmVmaXhcIiwgXCJ1cmxcIl07XG52YXIgbWVkaWFUeXBlc18gPSBbXCJhbGxcIiwgXCJhdXJhbFwiLCBcImJyYWlsbGVcIiwgXCJoYW5kaGVsZFwiLCBcInByaW50XCIsIFwicHJvamVjdGlvblwiLCBcInNjcmVlblwiLCBcInR0eVwiLCBcInR2XCIsIFwiZW1ib3NzZWRcIl07XG52YXIgbWVkaWFGZWF0dXJlc18gPSBbXCJ3aWR0aFwiLCBcIm1pbi13aWR0aFwiLCBcIm1heC13aWR0aFwiLCBcImhlaWdodFwiLCBcIm1pbi1oZWlnaHRcIiwgXCJtYXgtaGVpZ2h0XCIsIFwiZGV2aWNlLXdpZHRoXCIsIFwibWluLWRldmljZS13aWR0aFwiLCBcIm1heC1kZXZpY2Utd2lkdGhcIiwgXCJkZXZpY2UtaGVpZ2h0XCIsIFwibWluLWRldmljZS1oZWlnaHRcIiwgXCJtYXgtZGV2aWNlLWhlaWdodFwiLCBcImFzcGVjdC1yYXRpb1wiLCBcIm1pbi1hc3BlY3QtcmF0aW9cIiwgXCJtYXgtYXNwZWN0LXJhdGlvXCIsIFwiZGV2aWNlLWFzcGVjdC1yYXRpb1wiLCBcIm1pbi1kZXZpY2UtYXNwZWN0LXJhdGlvXCIsIFwibWF4LWRldmljZS1hc3BlY3QtcmF0aW9cIiwgXCJjb2xvclwiLCBcIm1pbi1jb2xvclwiLCBcIm1heC1jb2xvclwiLCBcImNvbG9yLWluZGV4XCIsIFwibWluLWNvbG9yLWluZGV4XCIsIFwibWF4LWNvbG9yLWluZGV4XCIsIFwibW9ub2Nocm9tZVwiLCBcIm1pbi1tb25vY2hyb21lXCIsIFwibWF4LW1vbm9jaHJvbWVcIiwgXCJyZXNvbHV0aW9uXCIsIFwibWluLXJlc29sdXRpb25cIiwgXCJtYXgtcmVzb2x1dGlvblwiLCBcInNjYW5cIiwgXCJncmlkXCIsIFwiZHluYW1pYy1yYW5nZVwiLCBcInZpZGVvLWR5bmFtaWMtcmFuZ2VcIl07XG52YXIgcHJvcGVydHlLZXl3b3Jkc18gPSBbXCJhbGlnbi1jb250ZW50XCIsIFwiYWxpZ24taXRlbXNcIiwgXCJhbGlnbi1zZWxmXCIsIFwiYWxpZ25tZW50LWFkanVzdFwiLCBcImFsaWdubWVudC1iYXNlbGluZVwiLCBcImFuY2hvci1wb2ludFwiLCBcImFuaW1hdGlvblwiLCBcImFuaW1hdGlvbi1kZWxheVwiLCBcImFuaW1hdGlvbi1kaXJlY3Rpb25cIiwgXCJhbmltYXRpb24tZHVyYXRpb25cIiwgXCJhbmltYXRpb24tZmlsbC1tb2RlXCIsIFwiYW5pbWF0aW9uLWl0ZXJhdGlvbi1jb3VudFwiLCBcImFuaW1hdGlvbi1uYW1lXCIsIFwiYW5pbWF0aW9uLXBsYXktc3RhdGVcIiwgXCJhbmltYXRpb24tdGltaW5nLWZ1bmN0aW9uXCIsIFwiYXBwZWFyYW5jZVwiLCBcImF6aW11dGhcIiwgXCJiYWNrZmFjZS12aXNpYmlsaXR5XCIsIFwiYmFja2dyb3VuZFwiLCBcImJhY2tncm91bmQtYXR0YWNobWVudFwiLCBcImJhY2tncm91bmQtY2xpcFwiLCBcImJhY2tncm91bmQtY29sb3JcIiwgXCJiYWNrZ3JvdW5kLWltYWdlXCIsIFwiYmFja2dyb3VuZC1vcmlnaW5cIiwgXCJiYWNrZ3JvdW5kLXBvc2l0aW9uXCIsIFwiYmFja2dyb3VuZC1yZXBlYXRcIiwgXCJiYWNrZ3JvdW5kLXNpemVcIiwgXCJiYXNlbGluZS1zaGlmdFwiLCBcImJpbmRpbmdcIiwgXCJibGVlZFwiLCBcImJvb2ttYXJrLWxhYmVsXCIsIFwiYm9va21hcmstbGV2ZWxcIiwgXCJib29rbWFyay1zdGF0ZVwiLCBcImJvb2ttYXJrLXRhcmdldFwiLCBcImJvcmRlclwiLCBcImJvcmRlci1ib3R0b21cIiwgXCJib3JkZXItYm90dG9tLWNvbG9yXCIsIFwiYm9yZGVyLWJvdHRvbS1sZWZ0LXJhZGl1c1wiLCBcImJvcmRlci1ib3R0b20tcmlnaHQtcmFkaXVzXCIsIFwiYm9yZGVyLWJvdHRvbS1zdHlsZVwiLCBcImJvcmRlci1ib3R0b20td2lkdGhcIiwgXCJib3JkZXItY29sbGFwc2VcIiwgXCJib3JkZXItY29sb3JcIiwgXCJib3JkZXItaW1hZ2VcIiwgXCJib3JkZXItaW1hZ2Utb3V0c2V0XCIsIFwiYm9yZGVyLWltYWdlLXJlcGVhdFwiLCBcImJvcmRlci1pbWFnZS1zbGljZVwiLCBcImJvcmRlci1pbWFnZS1zb3VyY2VcIiwgXCJib3JkZXItaW1hZ2Utd2lkdGhcIiwgXCJib3JkZXItbGVmdFwiLCBcImJvcmRlci1sZWZ0LWNvbG9yXCIsIFwiYm9yZGVyLWxlZnQtc3R5bGVcIiwgXCJib3JkZXItbGVmdC13aWR0aFwiLCBcImJvcmRlci1yYWRpdXNcIiwgXCJib3JkZXItcmlnaHRcIiwgXCJib3JkZXItcmlnaHQtY29sb3JcIiwgXCJib3JkZXItcmlnaHQtc3R5bGVcIiwgXCJib3JkZXItcmlnaHQtd2lkdGhcIiwgXCJib3JkZXItc3BhY2luZ1wiLCBcImJvcmRlci1zdHlsZVwiLCBcImJvcmRlci10b3BcIiwgXCJib3JkZXItdG9wLWNvbG9yXCIsIFwiYm9yZGVyLXRvcC1sZWZ0LXJhZGl1c1wiLCBcImJvcmRlci10b3AtcmlnaHQtcmFkaXVzXCIsIFwiYm9yZGVyLXRvcC1zdHlsZVwiLCBcImJvcmRlci10b3Atd2lkdGhcIiwgXCJib3JkZXItd2lkdGhcIiwgXCJib3R0b21cIiwgXCJib3gtZGVjb3JhdGlvbi1icmVha1wiLCBcImJveC1zaGFkb3dcIiwgXCJib3gtc2l6aW5nXCIsIFwiYnJlYWstYWZ0ZXJcIiwgXCJicmVhay1iZWZvcmVcIiwgXCJicmVhay1pbnNpZGVcIiwgXCJjYXB0aW9uLXNpZGVcIiwgXCJjbGVhclwiLCBcImNsaXBcIiwgXCJjb2xvclwiLCBcImNvbG9yLXByb2ZpbGVcIiwgXCJjb2x1bW4tY291bnRcIiwgXCJjb2x1bW4tZmlsbFwiLCBcImNvbHVtbi1nYXBcIiwgXCJjb2x1bW4tcnVsZVwiLCBcImNvbHVtbi1ydWxlLWNvbG9yXCIsIFwiY29sdW1uLXJ1bGUtc3R5bGVcIiwgXCJjb2x1bW4tcnVsZS13aWR0aFwiLCBcImNvbHVtbi1zcGFuXCIsIFwiY29sdW1uLXdpZHRoXCIsIFwiY29sdW1uc1wiLCBcImNvbnRlbnRcIiwgXCJjb3VudGVyLWluY3JlbWVudFwiLCBcImNvdW50ZXItcmVzZXRcIiwgXCJjcm9wXCIsIFwiY3VlXCIsIFwiY3VlLWFmdGVyXCIsIFwiY3VlLWJlZm9yZVwiLCBcImN1cnNvclwiLCBcImRpcmVjdGlvblwiLCBcImRpc3BsYXlcIiwgXCJkb21pbmFudC1iYXNlbGluZVwiLCBcImRyb3AtaW5pdGlhbC1hZnRlci1hZGp1c3RcIiwgXCJkcm9wLWluaXRpYWwtYWZ0ZXItYWxpZ25cIiwgXCJkcm9wLWluaXRpYWwtYmVmb3JlLWFkanVzdFwiLCBcImRyb3AtaW5pdGlhbC1iZWZvcmUtYWxpZ25cIiwgXCJkcm9wLWluaXRpYWwtc2l6ZVwiLCBcImRyb3AtaW5pdGlhbC12YWx1ZVwiLCBcImVsZXZhdGlvblwiLCBcImVtcHR5LWNlbGxzXCIsIFwiZml0XCIsIFwiZml0LXBvc2l0aW9uXCIsIFwiZmxleFwiLCBcImZsZXgtYmFzaXNcIiwgXCJmbGV4LWRpcmVjdGlvblwiLCBcImZsZXgtZmxvd1wiLCBcImZsZXgtZ3Jvd1wiLCBcImZsZXgtc2hyaW5rXCIsIFwiZmxleC13cmFwXCIsIFwiZmxvYXRcIiwgXCJmbG9hdC1vZmZzZXRcIiwgXCJmbG93LWZyb21cIiwgXCJmbG93LWludG9cIiwgXCJmb250XCIsIFwiZm9udC1mZWF0dXJlLXNldHRpbmdzXCIsIFwiZm9udC1mYW1pbHlcIiwgXCJmb250LWtlcm5pbmdcIiwgXCJmb250LWxhbmd1YWdlLW92ZXJyaWRlXCIsIFwiZm9udC1zaXplXCIsIFwiZm9udC1zaXplLWFkanVzdFwiLCBcImZvbnQtc3RyZXRjaFwiLCBcImZvbnQtc3R5bGVcIiwgXCJmb250LXN5bnRoZXNpc1wiLCBcImZvbnQtdmFyaWFudFwiLCBcImZvbnQtdmFyaWFudC1hbHRlcm5hdGVzXCIsIFwiZm9udC12YXJpYW50LWNhcHNcIiwgXCJmb250LXZhcmlhbnQtZWFzdC1hc2lhblwiLCBcImZvbnQtdmFyaWFudC1saWdhdHVyZXNcIiwgXCJmb250LXZhcmlhbnQtbnVtZXJpY1wiLCBcImZvbnQtdmFyaWFudC1wb3NpdGlvblwiLCBcImZvbnQtd2VpZ2h0XCIsIFwiZ3JpZFwiLCBcImdyaWQtYXJlYVwiLCBcImdyaWQtYXV0by1jb2x1bW5zXCIsIFwiZ3JpZC1hdXRvLWZsb3dcIiwgXCJncmlkLWF1dG8tcG9zaXRpb25cIiwgXCJncmlkLWF1dG8tcm93c1wiLCBcImdyaWQtY29sdW1uXCIsIFwiZ3JpZC1jb2x1bW4tZW5kXCIsIFwiZ3JpZC1jb2x1bW4tc3RhcnRcIiwgXCJncmlkLXJvd1wiLCBcImdyaWQtcm93LWVuZFwiLCBcImdyaWQtcm93LXN0YXJ0XCIsIFwiZ3JpZC10ZW1wbGF0ZVwiLCBcImdyaWQtdGVtcGxhdGUtYXJlYXNcIiwgXCJncmlkLXRlbXBsYXRlLWNvbHVtbnNcIiwgXCJncmlkLXRlbXBsYXRlLXJvd3NcIiwgXCJoYW5naW5nLXB1bmN0dWF0aW9uXCIsIFwiaGVpZ2h0XCIsIFwiaHlwaGVuc1wiLCBcImljb25cIiwgXCJpbWFnZS1vcmllbnRhdGlvblwiLCBcImltYWdlLXJlbmRlcmluZ1wiLCBcImltYWdlLXJlc29sdXRpb25cIiwgXCJpbmxpbmUtYm94LWFsaWduXCIsIFwianVzdGlmeS1jb250ZW50XCIsIFwibGVmdFwiLCBcImxldHRlci1zcGFjaW5nXCIsIFwibGluZS1icmVha1wiLCBcImxpbmUtaGVpZ2h0XCIsIFwibGluZS1zdGFja2luZ1wiLCBcImxpbmUtc3RhY2tpbmctcnVieVwiLCBcImxpbmUtc3RhY2tpbmctc2hpZnRcIiwgXCJsaW5lLXN0YWNraW5nLXN0cmF0ZWd5XCIsIFwibGlzdC1zdHlsZVwiLCBcImxpc3Qtc3R5bGUtaW1hZ2VcIiwgXCJsaXN0LXN0eWxlLXBvc2l0aW9uXCIsIFwibGlzdC1zdHlsZS10eXBlXCIsIFwibWFyZ2luXCIsIFwibWFyZ2luLWJvdHRvbVwiLCBcIm1hcmdpbi1sZWZ0XCIsIFwibWFyZ2luLXJpZ2h0XCIsIFwibWFyZ2luLXRvcFwiLCBcIm1hcmtlci1vZmZzZXRcIiwgXCJtYXJrc1wiLCBcIm1hcnF1ZWUtZGlyZWN0aW9uXCIsIFwibWFycXVlZS1sb29wXCIsIFwibWFycXVlZS1wbGF5LWNvdW50XCIsIFwibWFycXVlZS1zcGVlZFwiLCBcIm1hcnF1ZWUtc3R5bGVcIiwgXCJtYXgtaGVpZ2h0XCIsIFwibWF4LXdpZHRoXCIsIFwibWluLWhlaWdodFwiLCBcIm1pbi13aWR0aFwiLCBcIm1vdmUtdG9cIiwgXCJuYXYtZG93blwiLCBcIm5hdi1pbmRleFwiLCBcIm5hdi1sZWZ0XCIsIFwibmF2LXJpZ2h0XCIsIFwibmF2LXVwXCIsIFwib2JqZWN0LWZpdFwiLCBcIm9iamVjdC1wb3NpdGlvblwiLCBcIm9wYWNpdHlcIiwgXCJvcmRlclwiLCBcIm9ycGhhbnNcIiwgXCJvdXRsaW5lXCIsIFwib3V0bGluZS1jb2xvclwiLCBcIm91dGxpbmUtb2Zmc2V0XCIsIFwib3V0bGluZS1zdHlsZVwiLCBcIm91dGxpbmUtd2lkdGhcIiwgXCJvdmVyZmxvd1wiLCBcIm92ZXJmbG93LXN0eWxlXCIsIFwib3ZlcmZsb3ctd3JhcFwiLCBcIm92ZXJmbG93LXhcIiwgXCJvdmVyZmxvdy15XCIsIFwicGFkZGluZ1wiLCBcInBhZGRpbmctYm90dG9tXCIsIFwicGFkZGluZy1sZWZ0XCIsIFwicGFkZGluZy1yaWdodFwiLCBcInBhZGRpbmctdG9wXCIsIFwicGFnZVwiLCBcInBhZ2UtYnJlYWstYWZ0ZXJcIiwgXCJwYWdlLWJyZWFrLWJlZm9yZVwiLCBcInBhZ2UtYnJlYWstaW5zaWRlXCIsIFwicGFnZS1wb2xpY3lcIiwgXCJwYXVzZVwiLCBcInBhdXNlLWFmdGVyXCIsIFwicGF1c2UtYmVmb3JlXCIsIFwicGVyc3BlY3RpdmVcIiwgXCJwZXJzcGVjdGl2ZS1vcmlnaW5cIiwgXCJwaXRjaFwiLCBcInBpdGNoLXJhbmdlXCIsIFwicGxheS1kdXJpbmdcIiwgXCJwb3NpdGlvblwiLCBcInByZXNlbnRhdGlvbi1sZXZlbFwiLCBcInB1bmN0dWF0aW9uLXRyaW1cIiwgXCJxdW90ZXNcIiwgXCJyZWdpb24tYnJlYWstYWZ0ZXJcIiwgXCJyZWdpb24tYnJlYWstYmVmb3JlXCIsIFwicmVnaW9uLWJyZWFrLWluc2lkZVwiLCBcInJlZ2lvbi1mcmFnbWVudFwiLCBcInJlbmRlcmluZy1pbnRlbnRcIiwgXCJyZXNpemVcIiwgXCJyZXN0XCIsIFwicmVzdC1hZnRlclwiLCBcInJlc3QtYmVmb3JlXCIsIFwicmljaG5lc3NcIiwgXCJyaWdodFwiLCBcInJvdGF0aW9uXCIsIFwicm90YXRpb24tcG9pbnRcIiwgXCJydWJ5LWFsaWduXCIsIFwicnVieS1vdmVyaGFuZ1wiLCBcInJ1YnktcG9zaXRpb25cIiwgXCJydWJ5LXNwYW5cIiwgXCJzaGFwZS1pbWFnZS10aHJlc2hvbGRcIiwgXCJzaGFwZS1pbnNpZGVcIiwgXCJzaGFwZS1tYXJnaW5cIiwgXCJzaGFwZS1vdXRzaWRlXCIsIFwic2l6ZVwiLCBcInNwZWFrXCIsIFwic3BlYWstYXNcIiwgXCJzcGVhay1oZWFkZXJcIiwgXCJzcGVhay1udW1lcmFsXCIsIFwic3BlYWstcHVuY3R1YXRpb25cIiwgXCJzcGVlY2gtcmF0ZVwiLCBcInN0cmVzc1wiLCBcInN0cmluZy1zZXRcIiwgXCJ0YWItc2l6ZVwiLCBcInRhYmxlLWxheW91dFwiLCBcInRhcmdldFwiLCBcInRhcmdldC1uYW1lXCIsIFwidGFyZ2V0LW5ld1wiLCBcInRhcmdldC1wb3NpdGlvblwiLCBcInRleHQtYWxpZ25cIiwgXCJ0ZXh0LWFsaWduLWxhc3RcIiwgXCJ0ZXh0LWRlY29yYXRpb25cIiwgXCJ0ZXh0LWRlY29yYXRpb24tY29sb3JcIiwgXCJ0ZXh0LWRlY29yYXRpb24tbGluZVwiLCBcInRleHQtZGVjb3JhdGlvbi1za2lwXCIsIFwidGV4dC1kZWNvcmF0aW9uLXN0eWxlXCIsIFwidGV4dC1lbXBoYXNpc1wiLCBcInRleHQtZW1waGFzaXMtY29sb3JcIiwgXCJ0ZXh0LWVtcGhhc2lzLXBvc2l0aW9uXCIsIFwidGV4dC1lbXBoYXNpcy1zdHlsZVwiLCBcInRleHQtaGVpZ2h0XCIsIFwidGV4dC1pbmRlbnRcIiwgXCJ0ZXh0LWp1c3RpZnlcIiwgXCJ0ZXh0LW91dGxpbmVcIiwgXCJ0ZXh0LW92ZXJmbG93XCIsIFwidGV4dC1zaGFkb3dcIiwgXCJ0ZXh0LXNpemUtYWRqdXN0XCIsIFwidGV4dC1zcGFjZS1jb2xsYXBzZVwiLCBcInRleHQtdHJhbnNmb3JtXCIsIFwidGV4dC11bmRlcmxpbmUtcG9zaXRpb25cIiwgXCJ0ZXh0LXdyYXBcIiwgXCJ0b3BcIiwgXCJ0cmFuc2Zvcm1cIiwgXCJ0cmFuc2Zvcm0tb3JpZ2luXCIsIFwidHJhbnNmb3JtLXN0eWxlXCIsIFwidHJhbnNpdGlvblwiLCBcInRyYW5zaXRpb24tZGVsYXlcIiwgXCJ0cmFuc2l0aW9uLWR1cmF0aW9uXCIsIFwidHJhbnNpdGlvbi1wcm9wZXJ0eVwiLCBcInRyYW5zaXRpb24tdGltaW5nLWZ1bmN0aW9uXCIsIFwidW5pY29kZS1iaWRpXCIsIFwidmVydGljYWwtYWxpZ25cIiwgXCJ2aXNpYmlsaXR5XCIsIFwidm9pY2UtYmFsYW5jZVwiLCBcInZvaWNlLWR1cmF0aW9uXCIsIFwidm9pY2UtZmFtaWx5XCIsIFwidm9pY2UtcGl0Y2hcIiwgXCJ2b2ljZS1yYW5nZVwiLCBcInZvaWNlLXJhdGVcIiwgXCJ2b2ljZS1zdHJlc3NcIiwgXCJ2b2ljZS12b2x1bWVcIiwgXCJ2b2x1bWVcIiwgXCJ3aGl0ZS1zcGFjZVwiLCBcIndpZG93c1wiLCBcIndpZHRoXCIsIFwid2lsbC1jaGFuZ2VcIiwgXCJ3b3JkLWJyZWFrXCIsIFwid29yZC1zcGFjaW5nXCIsIFwid29yZC13cmFwXCIsIFwiei1pbmRleFwiLCBcImNsaXAtcGF0aFwiLCBcImNsaXAtcnVsZVwiLCBcIm1hc2tcIiwgXCJlbmFibGUtYmFja2dyb3VuZFwiLCBcImZpbHRlclwiLCBcImZsb29kLWNvbG9yXCIsIFwiZmxvb2Qtb3BhY2l0eVwiLCBcImxpZ2h0aW5nLWNvbG9yXCIsIFwic3RvcC1jb2xvclwiLCBcInN0b3Atb3BhY2l0eVwiLCBcInBvaW50ZXItZXZlbnRzXCIsIFwiY29sb3ItaW50ZXJwb2xhdGlvblwiLCBcImNvbG9yLWludGVycG9sYXRpb24tZmlsdGVyc1wiLCBcImNvbG9yLXJlbmRlcmluZ1wiLCBcImZpbGxcIiwgXCJmaWxsLW9wYWNpdHlcIiwgXCJmaWxsLXJ1bGVcIiwgXCJpbWFnZS1yZW5kZXJpbmdcIiwgXCJtYXJrZXJcIiwgXCJtYXJrZXItZW5kXCIsIFwibWFya2VyLW1pZFwiLCBcIm1hcmtlci1zdGFydFwiLCBcInNoYXBlLXJlbmRlcmluZ1wiLCBcInN0cm9rZVwiLCBcInN0cm9rZS1kYXNoYXJyYXlcIiwgXCJzdHJva2UtZGFzaG9mZnNldFwiLCBcInN0cm9rZS1saW5lY2FwXCIsIFwic3Ryb2tlLWxpbmVqb2luXCIsIFwic3Ryb2tlLW1pdGVybGltaXRcIiwgXCJzdHJva2Utb3BhY2l0eVwiLCBcInN0cm9rZS13aWR0aFwiLCBcInRleHQtcmVuZGVyaW5nXCIsIFwiYmFzZWxpbmUtc2hpZnRcIiwgXCJkb21pbmFudC1iYXNlbGluZVwiLCBcImdseXBoLW9yaWVudGF0aW9uLWhvcml6b250YWxcIiwgXCJnbHlwaC1vcmllbnRhdGlvbi12ZXJ0aWNhbFwiLCBcInRleHQtYW5jaG9yXCIsIFwid3JpdGluZy1tb2RlXCIsIFwiZm9udC1zbW9vdGhpbmdcIiwgXCJvc3gtZm9udC1zbW9vdGhpbmdcIl07XG52YXIgbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzXyA9IFtcInNjcm9sbGJhci1hcnJvdy1jb2xvclwiLCBcInNjcm9sbGJhci1iYXNlLWNvbG9yXCIsIFwic2Nyb2xsYmFyLWRhcmstc2hhZG93LWNvbG9yXCIsIFwic2Nyb2xsYmFyLWZhY2UtY29sb3JcIiwgXCJzY3JvbGxiYXItaGlnaGxpZ2h0LWNvbG9yXCIsIFwic2Nyb2xsYmFyLXNoYWRvdy1jb2xvclwiLCBcInNjcm9sbGJhci0zZC1saWdodC1jb2xvclwiLCBcInNjcm9sbGJhci10cmFjay1jb2xvclwiLCBcInNoYXBlLWluc2lkZVwiLCBcInNlYXJjaGZpZWxkLWNhbmNlbC1idXR0b25cIiwgXCJzZWFyY2hmaWVsZC1kZWNvcmF0aW9uXCIsIFwic2VhcmNoZmllbGQtcmVzdWx0cy1idXR0b25cIiwgXCJzZWFyY2hmaWVsZC1yZXN1bHRzLWRlY29yYXRpb25cIiwgXCJ6b29tXCJdO1xudmFyIGZvbnRQcm9wZXJ0aWVzXyA9IFtcImZvbnQtZmFtaWx5XCIsIFwic3JjXCIsIFwidW5pY29kZS1yYW5nZVwiLCBcImZvbnQtdmFyaWFudFwiLCBcImZvbnQtZmVhdHVyZS1zZXR0aW5nc1wiLCBcImZvbnQtc3RyZXRjaFwiLCBcImZvbnQtd2VpZ2h0XCIsIFwiZm9udC1zdHlsZVwiXTtcbnZhciBjb2xvcktleXdvcmRzXyA9IFtcImFsaWNlYmx1ZVwiLCBcImFudGlxdWV3aGl0ZVwiLCBcImFxdWFcIiwgXCJhcXVhbWFyaW5lXCIsIFwiYXp1cmVcIiwgXCJiZWlnZVwiLCBcImJpc3F1ZVwiLCBcImJsYWNrXCIsIFwiYmxhbmNoZWRhbG1vbmRcIiwgXCJibHVlXCIsIFwiYmx1ZXZpb2xldFwiLCBcImJyb3duXCIsIFwiYnVybHl3b29kXCIsIFwiY2FkZXRibHVlXCIsIFwiY2hhcnRyZXVzZVwiLCBcImNob2NvbGF0ZVwiLCBcImNvcmFsXCIsIFwiY29ybmZsb3dlcmJsdWVcIiwgXCJjb3Juc2lsa1wiLCBcImNyaW1zb25cIiwgXCJjeWFuXCIsIFwiZGFya2JsdWVcIiwgXCJkYXJrY3lhblwiLCBcImRhcmtnb2xkZW5yb2RcIiwgXCJkYXJrZ3JheVwiLCBcImRhcmtncmVlblwiLCBcImRhcmtraGFraVwiLCBcImRhcmttYWdlbnRhXCIsIFwiZGFya29saXZlZ3JlZW5cIiwgXCJkYXJrb3JhbmdlXCIsIFwiZGFya29yY2hpZFwiLCBcImRhcmtyZWRcIiwgXCJkYXJrc2FsbW9uXCIsIFwiZGFya3NlYWdyZWVuXCIsIFwiZGFya3NsYXRlYmx1ZVwiLCBcImRhcmtzbGF0ZWdyYXlcIiwgXCJkYXJrdHVycXVvaXNlXCIsIFwiZGFya3Zpb2xldFwiLCBcImRlZXBwaW5rXCIsIFwiZGVlcHNreWJsdWVcIiwgXCJkaW1ncmF5XCIsIFwiZG9kZ2VyYmx1ZVwiLCBcImZpcmVicmlja1wiLCBcImZsb3JhbHdoaXRlXCIsIFwiZm9yZXN0Z3JlZW5cIiwgXCJmdWNoc2lhXCIsIFwiZ2FpbnNib3JvXCIsIFwiZ2hvc3R3aGl0ZVwiLCBcImdvbGRcIiwgXCJnb2xkZW5yb2RcIiwgXCJncmF5XCIsIFwiZ3JleVwiLCBcImdyZWVuXCIsIFwiZ3JlZW55ZWxsb3dcIiwgXCJob25leWRld1wiLCBcImhvdHBpbmtcIiwgXCJpbmRpYW5yZWRcIiwgXCJpbmRpZ29cIiwgXCJpdm9yeVwiLCBcImtoYWtpXCIsIFwibGF2ZW5kZXJcIiwgXCJsYXZlbmRlcmJsdXNoXCIsIFwibGF3bmdyZWVuXCIsIFwibGVtb25jaGlmZm9uXCIsIFwibGlnaHRibHVlXCIsIFwibGlnaHRjb3JhbFwiLCBcImxpZ2h0Y3lhblwiLCBcImxpZ2h0Z29sZGVucm9keWVsbG93XCIsIFwibGlnaHRncmF5XCIsIFwibGlnaHRncmVlblwiLCBcImxpZ2h0cGlua1wiLCBcImxpZ2h0c2FsbW9uXCIsIFwibGlnaHRzZWFncmVlblwiLCBcImxpZ2h0c2t5Ymx1ZVwiLCBcImxpZ2h0c2xhdGVncmF5XCIsIFwibGlnaHRzdGVlbGJsdWVcIiwgXCJsaWdodHllbGxvd1wiLCBcImxpbWVcIiwgXCJsaW1lZ3JlZW5cIiwgXCJsaW5lblwiLCBcIm1hZ2VudGFcIiwgXCJtYXJvb25cIiwgXCJtZWRpdW1hcXVhbWFyaW5lXCIsIFwibWVkaXVtYmx1ZVwiLCBcIm1lZGl1bW9yY2hpZFwiLCBcIm1lZGl1bXB1cnBsZVwiLCBcIm1lZGl1bXNlYWdyZWVuXCIsIFwibWVkaXVtc2xhdGVibHVlXCIsIFwibWVkaXVtc3ByaW5nZ3JlZW5cIiwgXCJtZWRpdW10dXJxdW9pc2VcIiwgXCJtZWRpdW12aW9sZXRyZWRcIiwgXCJtaWRuaWdodGJsdWVcIiwgXCJtaW50Y3JlYW1cIiwgXCJtaXN0eXJvc2VcIiwgXCJtb2NjYXNpblwiLCBcIm5hdmFqb3doaXRlXCIsIFwibmF2eVwiLCBcIm9sZGxhY2VcIiwgXCJvbGl2ZVwiLCBcIm9saXZlZHJhYlwiLCBcIm9yYW5nZVwiLCBcIm9yYW5nZXJlZFwiLCBcIm9yY2hpZFwiLCBcInBhbGVnb2xkZW5yb2RcIiwgXCJwYWxlZ3JlZW5cIiwgXCJwYWxldHVycXVvaXNlXCIsIFwicGFsZXZpb2xldHJlZFwiLCBcInBhcGF5YXdoaXBcIiwgXCJwZWFjaHB1ZmZcIiwgXCJwZXJ1XCIsIFwicGlua1wiLCBcInBsdW1cIiwgXCJwb3dkZXJibHVlXCIsIFwicHVycGxlXCIsIFwicmViZWNjYXB1cnBsZVwiLCBcInJlZFwiLCBcInJvc3licm93blwiLCBcInJveWFsYmx1ZVwiLCBcInNhZGRsZWJyb3duXCIsIFwic2FsbW9uXCIsIFwic2FuZHlicm93blwiLCBcInNlYWdyZWVuXCIsIFwic2Vhc2hlbGxcIiwgXCJzaWVubmFcIiwgXCJzaWx2ZXJcIiwgXCJza3libHVlXCIsIFwic2xhdGVibHVlXCIsIFwic2xhdGVncmF5XCIsIFwic25vd1wiLCBcInNwcmluZ2dyZWVuXCIsIFwic3RlZWxibHVlXCIsIFwidGFuXCIsIFwidGVhbFwiLCBcInRoaXN0bGVcIiwgXCJ0b21hdG9cIiwgXCJ0dXJxdW9pc2VcIiwgXCJ2aW9sZXRcIiwgXCJ3aGVhdFwiLCBcIndoaXRlXCIsIFwid2hpdGVzbW9rZVwiLCBcInllbGxvd1wiLCBcInllbGxvd2dyZWVuXCJdO1xudmFyIHZhbHVlS2V5d29yZHNfID0gW1wiYWJvdmVcIiwgXCJhYnNvbHV0ZVwiLCBcImFjdGl2ZWJvcmRlclwiLCBcImFkZGl0aXZlXCIsIFwiYWN0aXZlY2FwdGlvblwiLCBcImFmYXJcIiwgXCJhZnRlci13aGl0ZS1zcGFjZVwiLCBcImFoZWFkXCIsIFwiYWxpYXNcIiwgXCJhbGxcIiwgXCJhbGwtc2Nyb2xsXCIsIFwiYWxwaGFiZXRpY1wiLCBcImFsdGVybmF0ZVwiLCBcImFsd2F5c1wiLCBcImFtaGFyaWNcIiwgXCJhbWhhcmljLWFiZWdlZGVcIiwgXCJhbnRpYWxpYXNlZFwiLCBcImFwcHdvcmtzcGFjZVwiLCBcImFyYWJpYy1pbmRpY1wiLCBcImFybWVuaWFuXCIsIFwiYXN0ZXJpc2tzXCIsIFwiYXR0clwiLCBcImF1dG9cIiwgXCJhdm9pZFwiLCBcImF2b2lkLWNvbHVtblwiLCBcImF2b2lkLXBhZ2VcIiwgXCJhdm9pZC1yZWdpb25cIiwgXCJiYWNrZ3JvdW5kXCIsIFwiYmFja3dhcmRzXCIsIFwiYmFzZWxpbmVcIiwgXCJiZWxvd1wiLCBcImJpZGktb3ZlcnJpZGVcIiwgXCJiaW5hcnlcIiwgXCJiZW5nYWxpXCIsIFwiYmxpbmtcIiwgXCJibG9ja1wiLCBcImJsb2NrLWF4aXNcIiwgXCJib2xkXCIsIFwiYm9sZGVyXCIsIFwiYm9yZGVyXCIsIFwiYm9yZGVyLWJveFwiLCBcImJvdGhcIiwgXCJib3R0b21cIiwgXCJicmVha1wiLCBcImJyZWFrLWFsbFwiLCBcImJyZWFrLXdvcmRcIiwgXCJidWxsZXRzXCIsIFwiYnV0dG9uXCIsIFwiYnV0dG9uZmFjZVwiLCBcImJ1dHRvbmhpZ2hsaWdodFwiLCBcImJ1dHRvbnNoYWRvd1wiLCBcImJ1dHRvbnRleHRcIiwgXCJjYWxjXCIsIFwiY2FtYm9kaWFuXCIsIFwiY2FwaXRhbGl6ZVwiLCBcImNhcHMtbG9jay1pbmRpY2F0b3JcIiwgXCJjYXB0aW9uXCIsIFwiY2FwdGlvbnRleHRcIiwgXCJjYXJldFwiLCBcImNlbGxcIiwgXCJjZW50ZXJcIiwgXCJjaGVja2JveFwiLCBcImNpcmNsZVwiLCBcImNqay1kZWNpbWFsXCIsIFwiY2prLWVhcnRobHktYnJhbmNoXCIsIFwiY2prLWhlYXZlbmx5LXN0ZW1cIiwgXCJjamstaWRlb2dyYXBoaWNcIiwgXCJjbGVhclwiLCBcImNsaXBcIiwgXCJjbG9zZS1xdW90ZVwiLCBcImNvbC1yZXNpemVcIiwgXCJjb2xsYXBzZVwiLCBcImNvbHVtblwiLCBcImNvbXBhY3RcIiwgXCJjb25kZW5zZWRcIiwgXCJjb25pYy1ncmFkaWVudFwiLCBcImNvbnRhaW5cIiwgXCJjb250ZW50XCIsIFwiY29udGVudHNcIiwgXCJjb250ZW50LWJveFwiLCBcImNvbnRleHQtbWVudVwiLCBcImNvbnRpbnVvdXNcIiwgXCJjb3B5XCIsIFwiY291bnRlclwiLCBcImNvdW50ZXJzXCIsIFwiY292ZXJcIiwgXCJjcm9wXCIsIFwiY3Jvc3NcIiwgXCJjcm9zc2hhaXJcIiwgXCJjdXJyZW50Y29sb3JcIiwgXCJjdXJzaXZlXCIsIFwiY3ljbGljXCIsIFwiZGFzaGVkXCIsIFwiZGVjaW1hbFwiLCBcImRlY2ltYWwtbGVhZGluZy16ZXJvXCIsIFwiZGVmYXVsdFwiLCBcImRlZmF1bHQtYnV0dG9uXCIsIFwiZGVzdGluYXRpb24tYXRvcFwiLCBcImRlc3RpbmF0aW9uLWluXCIsIFwiZGVzdGluYXRpb24tb3V0XCIsIFwiZGVzdGluYXRpb24tb3ZlclwiLCBcImRldmFuYWdhcmlcIiwgXCJkaXNjXCIsIFwiZGlzY2FyZFwiLCBcImRpc2Nsb3N1cmUtY2xvc2VkXCIsIFwiZGlzY2xvc3VyZS1vcGVuXCIsIFwiZG9jdW1lbnRcIiwgXCJkb3QtZGFzaFwiLCBcImRvdC1kb3QtZGFzaFwiLCBcImRvdHRlZFwiLCBcImRvdWJsZVwiLCBcImRvd25cIiwgXCJlLXJlc2l6ZVwiLCBcImVhc2VcIiwgXCJlYXNlLWluXCIsIFwiZWFzZS1pbi1vdXRcIiwgXCJlYXNlLW91dFwiLCBcImVsZW1lbnRcIiwgXCJlbGxpcHNlXCIsIFwiZWxsaXBzaXNcIiwgXCJlbWJlZFwiLCBcImVuZFwiLCBcImV0aGlvcGljXCIsIFwiZXRoaW9waWMtYWJlZ2VkZVwiLCBcImV0aGlvcGljLWFiZWdlZGUtYW0tZXRcIiwgXCJldGhpb3BpYy1hYmVnZWRlLWdlelwiLCBcImV0aGlvcGljLWFiZWdlZGUtdGktZXJcIiwgXCJldGhpb3BpYy1hYmVnZWRlLXRpLWV0XCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtYWEtZXJcIiwgXCJldGhpb3BpYy1oYWxlaGFtZS1hYS1ldFwiLCBcImV0aGlvcGljLWhhbGVoYW1lLWFtLWV0XCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtZ2V6XCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtb20tZXRcIiwgXCJldGhpb3BpYy1oYWxlaGFtZS1zaWQtZXRcIiwgXCJldGhpb3BpYy1oYWxlaGFtZS1zby1ldFwiLCBcImV0aGlvcGljLWhhbGVoYW1lLXRpLWVyXCIsIFwiZXRoaW9waWMtaGFsZWhhbWUtdGktZXRcIiwgXCJldGhpb3BpYy1oYWxlaGFtZS10aWdcIiwgXCJldGhpb3BpYy1udW1lcmljXCIsIFwiZXctcmVzaXplXCIsIFwiZXhwYW5kZWRcIiwgXCJleHRlbmRzXCIsIFwiZXh0cmEtY29uZGVuc2VkXCIsIFwiZXh0cmEtZXhwYW5kZWRcIiwgXCJmYW50YXN5XCIsIFwiZmFzdFwiLCBcImZpbGxcIiwgXCJmaXhlZFwiLCBcImZsYXRcIiwgXCJmbGV4XCIsIFwiZm9vdG5vdGVzXCIsIFwiZm9yd2FyZHNcIiwgXCJmcm9tXCIsIFwiZ2VvbWV0cmljUHJlY2lzaW9uXCIsIFwiZ2VvcmdpYW5cIiwgXCJncmF5dGV4dFwiLCBcImdyb292ZVwiLCBcImd1amFyYXRpXCIsIFwiZ3VybXVraGlcIiwgXCJoYW5kXCIsIFwiaGFuZ3VsXCIsIFwiaGFuZ3VsLWNvbnNvbmFudFwiLCBcImhlYnJld1wiLCBcImhlbHBcIiwgXCJoaWRkZW5cIiwgXCJoaWRlXCIsIFwiaGlnaFwiLCBcImhpZ2hlclwiLCBcImhpZ2hsaWdodFwiLCBcImhpZ2hsaWdodHRleHRcIiwgXCJoaXJhZ2FuYVwiLCBcImhpcmFnYW5hLWlyb2hhXCIsIFwiaG9yaXpvbnRhbFwiLCBcImhzbFwiLCBcImhzbGFcIiwgXCJpY29uXCIsIFwiaWdub3JlXCIsIFwiaW5hY3RpdmVib3JkZXJcIiwgXCJpbmFjdGl2ZWNhcHRpb25cIiwgXCJpbmFjdGl2ZWNhcHRpb250ZXh0XCIsIFwiaW5maW5pdGVcIiwgXCJpbmZvYmFja2dyb3VuZFwiLCBcImluZm90ZXh0XCIsIFwiaW5oZXJpdFwiLCBcImluaXRpYWxcIiwgXCJpbmxpbmVcIiwgXCJpbmxpbmUtYXhpc1wiLCBcImlubGluZS1ibG9ja1wiLCBcImlubGluZS1mbGV4XCIsIFwiaW5saW5lLXRhYmxlXCIsIFwiaW5zZXRcIiwgXCJpbnNpZGVcIiwgXCJpbnRyaW5zaWNcIiwgXCJpbnZlcnRcIiwgXCJpdGFsaWNcIiwgXCJqYXBhbmVzZS1mb3JtYWxcIiwgXCJqYXBhbmVzZS1pbmZvcm1hbFwiLCBcImp1c3RpZnlcIiwgXCJrYW5uYWRhXCIsIFwia2F0YWthbmFcIiwgXCJrYXRha2FuYS1pcm9oYVwiLCBcImtlZXAtYWxsXCIsIFwia2htZXJcIiwgXCJrb3JlYW4taGFuZ3VsLWZvcm1hbFwiLCBcImtvcmVhbi1oYW5qYS1mb3JtYWxcIiwgXCJrb3JlYW4taGFuamEtaW5mb3JtYWxcIiwgXCJsYW5kc2NhcGVcIiwgXCJsYW9cIiwgXCJsYXJnZVwiLCBcImxhcmdlclwiLCBcImxlZnRcIiwgXCJsZXZlbFwiLCBcImxpZ2h0ZXJcIiwgXCJsaW5lLXRocm91Z2hcIiwgXCJsaW5lYXJcIiwgXCJsaW5lYXItZ3JhZGllbnRcIiwgXCJsaW5lc1wiLCBcImxpc3QtaXRlbVwiLCBcImxpc3Rib3hcIiwgXCJsaXN0aXRlbVwiLCBcImxvY2FsXCIsIFwibG9naWNhbFwiLCBcImxvdWRcIiwgXCJsb3dlclwiLCBcImxvd2VyLWFscGhhXCIsIFwibG93ZXItYXJtZW5pYW5cIiwgXCJsb3dlci1ncmVla1wiLCBcImxvd2VyLWhleGFkZWNpbWFsXCIsIFwibG93ZXItbGF0aW5cIiwgXCJsb3dlci1ub3J3ZWdpYW5cIiwgXCJsb3dlci1yb21hblwiLCBcImxvd2VyY2FzZVwiLCBcImx0clwiLCBcIm1hbGF5YWxhbVwiLCBcIm1hdGNoXCIsIFwibWF0cml4XCIsIFwibWF0cml4M2RcIiwgXCJtZWRpYS1wbGF5LWJ1dHRvblwiLCBcIm1lZGlhLXNsaWRlclwiLCBcIm1lZGlhLXNsaWRlcnRodW1iXCIsIFwibWVkaWEtdm9sdW1lLXNsaWRlclwiLCBcIm1lZGlhLXZvbHVtZS1zbGlkZXJ0aHVtYlwiLCBcIm1lZGl1bVwiLCBcIm1lbnVcIiwgXCJtZW51bGlzdFwiLCBcIm1lbnVsaXN0LWJ1dHRvblwiLCBcIm1lbnV0ZXh0XCIsIFwibWVzc2FnZS1ib3hcIiwgXCJtaWRkbGVcIiwgXCJtaW4taW50cmluc2ljXCIsIFwibWl4XCIsIFwibW9uZ29saWFuXCIsIFwibW9ub3NwYWNlXCIsIFwibW92ZVwiLCBcIm11bHRpcGxlXCIsIFwibXlhbm1hclwiLCBcIm4tcmVzaXplXCIsIFwibmFycm93ZXJcIiwgXCJuZS1yZXNpemVcIiwgXCJuZXN3LXJlc2l6ZVwiLCBcIm5vLWNsb3NlLXF1b3RlXCIsIFwibm8tZHJvcFwiLCBcIm5vLW9wZW4tcXVvdGVcIiwgXCJuby1yZXBlYXRcIiwgXCJub25lXCIsIFwibm9ybWFsXCIsIFwibm90LWFsbG93ZWRcIiwgXCJub3dyYXBcIiwgXCJucy1yZXNpemVcIiwgXCJudW1iZXJzXCIsIFwibnVtZXJpY1wiLCBcIm53LXJlc2l6ZVwiLCBcIm53c2UtcmVzaXplXCIsIFwib2JsaXF1ZVwiLCBcIm9jdGFsXCIsIFwib3Blbi1xdW90ZVwiLCBcIm9wdGltaXplTGVnaWJpbGl0eVwiLCBcIm9wdGltaXplU3BlZWRcIiwgXCJvcml5YVwiLCBcIm9yb21vXCIsIFwib3V0c2V0XCIsIFwib3V0c2lkZVwiLCBcIm91dHNpZGUtc2hhcGVcIiwgXCJvdmVybGF5XCIsIFwib3ZlcmxpbmVcIiwgXCJwYWRkaW5nXCIsIFwicGFkZGluZy1ib3hcIiwgXCJwYWludGVkXCIsIFwicGFnZVwiLCBcInBhdXNlZFwiLCBcInBlcnNpYW5cIiwgXCJwZXJzcGVjdGl2ZVwiLCBcInBsdXMtZGFya2VyXCIsIFwicGx1cy1saWdodGVyXCIsIFwicG9pbnRlclwiLCBcInBvbHlnb25cIiwgXCJwb3J0cmFpdFwiLCBcInByZVwiLCBcInByZS1saW5lXCIsIFwicHJlLXdyYXBcIiwgXCJwcmVzZXJ2ZS0zZFwiLCBcInByb2dyZXNzXCIsIFwicHVzaC1idXR0b25cIiwgXCJyYWRpYWwtZ3JhZGllbnRcIiwgXCJyYWRpb1wiLCBcInJlYWQtb25seVwiLCBcInJlYWQtd3JpdGVcIiwgXCJyZWFkLXdyaXRlLXBsYWludGV4dC1vbmx5XCIsIFwicmVjdGFuZ2xlXCIsIFwicmVnaW9uXCIsIFwicmVsYXRpdmVcIiwgXCJyZXBlYXRcIiwgXCJyZXBlYXRpbmctbGluZWFyLWdyYWRpZW50XCIsIFwicmVwZWF0aW5nLXJhZGlhbC1ncmFkaWVudFwiLCBcInJlcGVhdGluZy1jb25pYy1ncmFkaWVudFwiLCBcInJlcGVhdC14XCIsIFwicmVwZWF0LXlcIiwgXCJyZXNldFwiLCBcInJldmVyc2VcIiwgXCJyZ2JcIiwgXCJyZ2JhXCIsIFwicmlkZ2VcIiwgXCJyaWdodFwiLCBcInJvdGF0ZVwiLCBcInJvdGF0ZTNkXCIsIFwicm90YXRlWFwiLCBcInJvdGF0ZVlcIiwgXCJyb3RhdGVaXCIsIFwicm91bmRcIiwgXCJyb3ctcmVzaXplXCIsIFwicnRsXCIsIFwicnVuLWluXCIsIFwicnVubmluZ1wiLCBcInMtcmVzaXplXCIsIFwic2Fucy1zZXJpZlwiLCBcInNjYWxlXCIsIFwic2NhbGUzZFwiLCBcInNjYWxlWFwiLCBcInNjYWxlWVwiLCBcInNjYWxlWlwiLCBcInNjcm9sbFwiLCBcInNjcm9sbGJhclwiLCBcInNjcm9sbC1wb3NpdGlvblwiLCBcInNlLXJlc2l6ZVwiLCBcInNlYXJjaGZpZWxkXCIsIFwic2VhcmNoZmllbGQtY2FuY2VsLWJ1dHRvblwiLCBcInNlYXJjaGZpZWxkLWRlY29yYXRpb25cIiwgXCJzZWFyY2hmaWVsZC1yZXN1bHRzLWJ1dHRvblwiLCBcInNlYXJjaGZpZWxkLXJlc3VsdHMtZGVjb3JhdGlvblwiLCBcInNlbWktY29uZGVuc2VkXCIsIFwic2VtaS1leHBhbmRlZFwiLCBcInNlcGFyYXRlXCIsIFwic2VyaWZcIiwgXCJzaG93XCIsIFwic2lkYW1hXCIsIFwic2ltcC1jaGluZXNlLWZvcm1hbFwiLCBcInNpbXAtY2hpbmVzZS1pbmZvcm1hbFwiLCBcInNpbmdsZVwiLCBcInNrZXdcIiwgXCJza2V3WFwiLCBcInNrZXdZXCIsIFwic2tpcC13aGl0ZS1zcGFjZVwiLCBcInNsaWRlXCIsIFwic2xpZGVyLWhvcml6b250YWxcIiwgXCJzbGlkZXItdmVydGljYWxcIiwgXCJzbGlkZXJ0aHVtYi1ob3Jpem9udGFsXCIsIFwic2xpZGVydGh1bWItdmVydGljYWxcIiwgXCJzbG93XCIsIFwic21hbGxcIiwgXCJzbWFsbC1jYXBzXCIsIFwic21hbGwtY2FwdGlvblwiLCBcInNtYWxsZXJcIiwgXCJzb2xpZFwiLCBcInNvbWFsaVwiLCBcInNvdXJjZS1hdG9wXCIsIFwic291cmNlLWluXCIsIFwic291cmNlLW91dFwiLCBcInNvdXJjZS1vdmVyXCIsIFwic3BhY2VcIiwgXCJzcGVsbC1vdXRcIiwgXCJzcXVhcmVcIiwgXCJzcXVhcmUtYnV0dG9uXCIsIFwic3RhbmRhcmRcIiwgXCJzdGFydFwiLCBcInN0YXRpY1wiLCBcInN0YXR1cy1iYXJcIiwgXCJzdHJldGNoXCIsIFwic3Ryb2tlXCIsIFwic3ViXCIsIFwic3VicGl4ZWwtYW50aWFsaWFzZWRcIiwgXCJzdXBlclwiLCBcInN3LXJlc2l6ZVwiLCBcInN5bWJvbGljXCIsIFwic3ltYm9sc1wiLCBcInRhYmxlXCIsIFwidGFibGUtY2FwdGlvblwiLCBcInRhYmxlLWNlbGxcIiwgXCJ0YWJsZS1jb2x1bW5cIiwgXCJ0YWJsZS1jb2x1bW4tZ3JvdXBcIiwgXCJ0YWJsZS1mb290ZXItZ3JvdXBcIiwgXCJ0YWJsZS1oZWFkZXItZ3JvdXBcIiwgXCJ0YWJsZS1yb3dcIiwgXCJ0YWJsZS1yb3ctZ3JvdXBcIiwgXCJ0YW1pbFwiLCBcInRlbHVndVwiLCBcInRleHRcIiwgXCJ0ZXh0LWJvdHRvbVwiLCBcInRleHQtdG9wXCIsIFwidGV4dGFyZWFcIiwgXCJ0ZXh0ZmllbGRcIiwgXCJ0aGFpXCIsIFwidGhpY2tcIiwgXCJ0aGluXCIsIFwidGhyZWVkZGFya3NoYWRvd1wiLCBcInRocmVlZGZhY2VcIiwgXCJ0aHJlZWRoaWdobGlnaHRcIiwgXCJ0aHJlZWRsaWdodHNoYWRvd1wiLCBcInRocmVlZHNoYWRvd1wiLCBcInRpYmV0YW5cIiwgXCJ0aWdyZVwiLCBcInRpZ3JpbnlhLWVyXCIsIFwidGlncmlueWEtZXItYWJlZ2VkZVwiLCBcInRpZ3JpbnlhLWV0XCIsIFwidGlncmlueWEtZXQtYWJlZ2VkZVwiLCBcInRvXCIsIFwidG9wXCIsIFwidHJhZC1jaGluZXNlLWZvcm1hbFwiLCBcInRyYWQtY2hpbmVzZS1pbmZvcm1hbFwiLCBcInRyYW5zbGF0ZVwiLCBcInRyYW5zbGF0ZTNkXCIsIFwidHJhbnNsYXRlWFwiLCBcInRyYW5zbGF0ZVlcIiwgXCJ0cmFuc2xhdGVaXCIsIFwidHJhbnNwYXJlbnRcIiwgXCJ1bHRyYS1jb25kZW5zZWRcIiwgXCJ1bHRyYS1leHBhbmRlZFwiLCBcInVuZGVybGluZVwiLCBcInVwXCIsIFwidXBwZXItYWxwaGFcIiwgXCJ1cHBlci1hcm1lbmlhblwiLCBcInVwcGVyLWdyZWVrXCIsIFwidXBwZXItaGV4YWRlY2ltYWxcIiwgXCJ1cHBlci1sYXRpblwiLCBcInVwcGVyLW5vcndlZ2lhblwiLCBcInVwcGVyLXJvbWFuXCIsIFwidXBwZXJjYXNlXCIsIFwidXJkdVwiLCBcInVybFwiLCBcInZhclwiLCBcInZlcnRpY2FsXCIsIFwidmVydGljYWwtdGV4dFwiLCBcInZpc2libGVcIiwgXCJ2aXNpYmxlRmlsbFwiLCBcInZpc2libGVQYWludGVkXCIsIFwidmlzaWJsZVN0cm9rZVwiLCBcInZpc3VhbFwiLCBcInctcmVzaXplXCIsIFwid2FpdFwiLCBcIndhdmVcIiwgXCJ3aWRlclwiLCBcIndpbmRvd1wiLCBcIndpbmRvd2ZyYW1lXCIsIFwid2luZG93dGV4dFwiLCBcIndvcmRzXCIsIFwieC1sYXJnZVwiLCBcIngtc21hbGxcIiwgXCJ4b3JcIiwgXCJ4eC1sYXJnZVwiLCBcInh4LXNtYWxsXCIsIFwiYmljdWJpY1wiLCBcIm9wdGltaXplc3BlZWRcIiwgXCJncmF5c2NhbGVcIiwgXCJyb3dcIiwgXCJyb3ctcmV2ZXJzZVwiLCBcIndyYXBcIiwgXCJ3cmFwLXJldmVyc2VcIiwgXCJjb2x1bW4tcmV2ZXJzZVwiLCBcImZsZXgtc3RhcnRcIiwgXCJmbGV4LWVuZFwiLCBcInNwYWNlLWJldHdlZW5cIiwgXCJzcGFjZS1hcm91bmRcIiwgXCJ1bnNldFwiXTtcbnZhciB3b3JkT3BlcmF0b3JLZXl3b3Jkc18gPSBbXCJpblwiLCBcImFuZFwiLCBcIm9yXCIsIFwibm90XCIsIFwiaXMgbm90XCIsIFwiaXMgYVwiLCBcImlzXCIsIFwiaXNudFwiLCBcImRlZmluZWRcIiwgXCJpZiB1bmxlc3NcIl0sXG4gIGJsb2NrS2V5d29yZHNfID0gW1wiZm9yXCIsIFwiaWZcIiwgXCJlbHNlXCIsIFwidW5sZXNzXCIsIFwiZnJvbVwiLCBcInRvXCJdLFxuICBjb21tb25BdG9tc18gPSBbXCJudWxsXCIsIFwidHJ1ZVwiLCBcImZhbHNlXCIsIFwiaHJlZlwiLCBcInRpdGxlXCIsIFwidHlwZVwiLCBcIm5vdC1hbGxvd2VkXCIsIFwicmVhZG9ubHlcIiwgXCJkaXNhYmxlZFwiXSxcbiAgY29tbW9uRGVmXyA9IFtcIkBmb250LWZhY2VcIiwgXCJAa2V5ZnJhbWVzXCIsIFwiQG1lZGlhXCIsIFwiQHZpZXdwb3J0XCIsIFwiQHBhZ2VcIiwgXCJAaG9zdFwiLCBcIkBzdXBwb3J0c1wiLCBcIkBibG9ja1wiLCBcIkBjc3NcIl07XG52YXIgaGludFdvcmRzID0gdGFnS2V5d29yZHNfLmNvbmNhdChkb2N1bWVudFR5cGVzXywgbWVkaWFUeXBlc18sIG1lZGlhRmVhdHVyZXNfLCBwcm9wZXJ0eUtleXdvcmRzXywgbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzXywgY29sb3JLZXl3b3Jkc18sIHZhbHVlS2V5d29yZHNfLCBmb250UHJvcGVydGllc18sIHdvcmRPcGVyYXRvcktleXdvcmRzXywgYmxvY2tLZXl3b3Jkc18sIGNvbW1vbkF0b21zXywgY29tbW9uRGVmXyk7XG5mdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHdvcmRzID0gd29yZHMuc29ydChmdW5jdGlvbiAoYSwgYikge1xuICAgIHJldHVybiBiID4gYTtcbiAgfSk7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIpO1xufVxuZnVuY3Rpb24ga2V5U2V0KGFycmF5KSB7XG4gIHZhciBrZXlzID0ge307XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgYXJyYXkubGVuZ3RoOyArK2kpIGtleXNbYXJyYXlbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIGtleXM7XG59XG5mdW5jdGlvbiBlc2NhcGVSZWdFeHAodGV4dCkge1xuICByZXR1cm4gdGV4dC5yZXBsYWNlKC9bLVtcXF17fSgpKis/LixcXFxcXiR8I1xcc10vZywgXCJcXFxcJCZcIik7XG59XG52YXIgdGFnS2V5d29yZHMgPSBrZXlTZXQodGFnS2V5d29yZHNfKSxcbiAgdGFnVmFyaWFibGVzUmVnZXhwID0gL14oYXxifGl8c3xjb2x8ZW0pJC9pLFxuICBwcm9wZXJ0eUtleXdvcmRzID0ga2V5U2V0KHByb3BlcnR5S2V5d29yZHNfKSxcbiAgbm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzID0ga2V5U2V0KG5vblN0YW5kYXJkUHJvcGVydHlLZXl3b3Jkc18pLFxuICB2YWx1ZUtleXdvcmRzID0ga2V5U2V0KHZhbHVlS2V5d29yZHNfKSxcbiAgY29sb3JLZXl3b3JkcyA9IGtleVNldChjb2xvcktleXdvcmRzXyksXG4gIGRvY3VtZW50VHlwZXMgPSBrZXlTZXQoZG9jdW1lbnRUeXBlc18pLFxuICBkb2N1bWVudFR5cGVzUmVnZXhwID0gd29yZFJlZ2V4cChkb2N1bWVudFR5cGVzXyksXG4gIG1lZGlhRmVhdHVyZXMgPSBrZXlTZXQobWVkaWFGZWF0dXJlc18pLFxuICBtZWRpYVR5cGVzID0ga2V5U2V0KG1lZGlhVHlwZXNfKSxcbiAgZm9udFByb3BlcnRpZXMgPSBrZXlTZXQoZm9udFByb3BlcnRpZXNfKSxcbiAgb3BlcmF0b3JzUmVnZXhwID0gL15cXHMqKFsuXXsyLDN9fCYmfFxcfFxcfHxcXCpcXCp8Wz8hPTpdPz18Wy0rKlxcLyU8Pl09P3xcXD86fFxcfikvLFxuICB3b3JkT3BlcmF0b3JLZXl3b3Jkc1JlZ2V4cCA9IHdvcmRSZWdleHAod29yZE9wZXJhdG9yS2V5d29yZHNfKSxcbiAgYmxvY2tLZXl3b3JkcyA9IGtleVNldChibG9ja0tleXdvcmRzXyksXG4gIHZlbmRvclByZWZpeGVzUmVnZXhwID0gbmV3IFJlZ0V4cCgvXlxcLShtb3p8bXN8b3x3ZWJraXQpLS9pKSxcbiAgY29tbW9uQXRvbXMgPSBrZXlTZXQoY29tbW9uQXRvbXNfKSxcbiAgZmlyc3RXb3JkTWF0Y2ggPSBcIlwiLFxuICBzdGF0ZXMgPSB7fSxcbiAgY2gsXG4gIHN0eWxlLFxuICB0eXBlLFxuICBvdmVycmlkZTtcblxuLyoqXG4gKiBUb2tlbml6ZXJzXG4gKi9cbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIGZpcnN0V29yZE1hdGNoID0gc3RyZWFtLnN0cmluZy5tYXRjaCgvKF5bXFx3LV0rXFxzKj1cXHMqJCl8KF5cXHMqW1xcdy1dK1xccyo9XFxzKltcXHctXSl8KF5cXHMqKFxcLnwjfEB8XFwkfFxcJnxcXFt8XFxkfFxcK3w6Oj98XFx7fFxcPnx+fFxcLyk/XFxzKltcXHctXSooW2EtejAtOS1dfFxcKnxcXC9cXCopKFxcKHwsKT8pLyk7XG4gIHN0YXRlLmNvbnRleHQubGluZS5maXJzdFdvcmQgPSBmaXJzdFdvcmRNYXRjaCA/IGZpcnN0V29yZE1hdGNoWzBdLnJlcGxhY2UoL15cXHMqLywgXCJcIikgOiBcIlwiO1xuICBzdGF0ZS5jb250ZXh0LmxpbmUuaW5kZW50ID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gIGNoID0gc3RyZWFtLnBlZWsoKTtcblxuICAvLyBMaW5lIGNvbW1lbnRcbiAgaWYgKHN0cmVhbS5tYXRjaChcIi8vXCIpKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBbXCJjb21tZW50XCIsIFwiY29tbWVudFwiXTtcbiAgfVxuICAvLyBCbG9jayBjb21tZW50XG4gIGlmIChzdHJlYW0ubWF0Y2goXCIvKlwiKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5DQ29tbWVudDtcbiAgICByZXR1cm4gdG9rZW5DQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICAvLyBTdHJpbmdcbiAgaWYgKGNoID09IFwiXFxcIlwiIHx8IGNoID09IFwiJ1wiKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgLy8gRGVmXG4gIGlmIChjaCA9PSBcIkBcIikge1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFxcXC1dLyk7XG4gICAgcmV0dXJuIFtcImRlZlwiLCBzdHJlYW0uY3VycmVudCgpXTtcbiAgfVxuICAvLyBJRCBzZWxlY3RvciBvciBIZXggY29sb3JcbiAgaWYgKGNoID09IFwiI1wiKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICAvLyBIZXggY29sb3JcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eWzAtOWEtZl17M30oWzAtOWEtZl0oWzAtOWEtZl17Mn0pezAsMn0pP1xcYig/IS0pL2kpKSB7XG4gICAgICByZXR1cm4gW1wiYXRvbVwiLCBcImF0b21cIl07XG4gICAgfVxuICAgIC8vIElEIHNlbGVjdG9yXG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXlthLXpdW1xcdy1dKi9pKSkge1xuICAgICAgcmV0dXJuIFtcImJ1aWx0aW5cIiwgXCJoYXNoXCJdO1xuICAgIH1cbiAgfVxuICAvLyBWZW5kb3IgcHJlZml4ZXNcbiAgaWYgKHN0cmVhbS5tYXRjaCh2ZW5kb3JQcmVmaXhlc1JlZ2V4cCkpIHtcbiAgICByZXR1cm4gW1wibWV0YVwiLCBcInZlbmRvci1wcmVmaXhlc1wiXTtcbiAgfVxuICAvLyBOdW1iZXJzXG4gIGlmIChzdHJlYW0ubWF0Y2goL14tP1swLTldP1xcLj9bMC05XS8pKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bYS16JV0vaSk7XG4gICAgcmV0dXJuIFtcIm51bWJlclwiLCBcInVuaXRcIl07XG4gIH1cbiAgLy8gIWltcG9ydGFudHxvcHRpb25hbFxuICBpZiAoY2ggPT0gXCIhXCIpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBbc3RyZWFtLm1hdGNoKC9eKGltcG9ydGFudHxvcHRpb25hbCkvaSkgPyBcImtleXdvcmRcIiA6IFwib3BlcmF0b3JcIiwgXCJpbXBvcnRhbnRcIl07XG4gIH1cbiAgLy8gQ2xhc3NcbiAgaWYgKGNoID09IFwiLlwiICYmIHN0cmVhbS5tYXRjaCgvXlxcLlthLXpdW1xcdy1dKi9pKSkge1xuICAgIHJldHVybiBbXCJxdWFsaWZpZXJcIiwgXCJxdWFsaWZpZXJcIl07XG4gIH1cbiAgLy8gdXJsIHVybC1wcmVmaXggZG9tYWluIHJlZ2V4cFxuICBpZiAoc3RyZWFtLm1hdGNoKGRvY3VtZW50VHlwZXNSZWdleHApKSB7XG4gICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gXCIoXCIpIHN0YXRlLnRva2VuaXplID0gdG9rZW5QYXJlbnRoZXNpemVkO1xuICAgIHJldHVybiBbXCJwcm9wZXJ0eVwiLCBcIndvcmRcIl07XG4gIH1cbiAgLy8gTWl4aW5zIC8gRnVuY3Rpb25zXG4gIGlmIChzdHJlYW0ubWF0Y2goL15bYS16XVtcXHctXSpcXCgvaSkpIHtcbiAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgIHJldHVybiBbXCJrZXl3b3JkXCIsIFwibWl4aW5cIl07XG4gIH1cbiAgLy8gQmxvY2sgbWl4aW5zXG4gIGlmIChzdHJlYW0ubWF0Y2goL14oXFwrfC0pW2Etel1bXFx3LV0qXFwoL2kpKSB7XG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICByZXR1cm4gW1wia2V5d29yZFwiLCBcImJsb2NrLW1peGluXCJdO1xuICB9XG4gIC8vIFBhcmVudCBSZWZlcmVuY2UgQkVNIG5hbWluZ1xuICBpZiAoc3RyZWFtLnN0cmluZy5tYXRjaCgvXlxccyomLykgJiYgc3RyZWFtLm1hdGNoKC9eWy1fXStbYS16XVtcXHctXSovKSkge1xuICAgIHJldHVybiBbXCJxdWFsaWZpZXJcIiwgXCJxdWFsaWZpZXJcIl07XG4gIH1cbiAgLy8gLyBSb290IFJlZmVyZW5jZSAmIFBhcmVudCBSZWZlcmVuY2VcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXihcXC98JikoLXxffDp8XFwufCN8W2Etel0pLykpIHtcbiAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgIHJldHVybiBbXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiLCBcInJlZmVyZW5jZVwiXTtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKC9eJnsxfVxccyokLykpIHtcbiAgICByZXR1cm4gW1widmFyaWFibGVOYW1lLnNwZWNpYWxcIiwgXCJyZWZlcmVuY2VcIl07XG4gIH1cbiAgLy8gV29yZCBvcGVyYXRvclxuICBpZiAoc3RyZWFtLm1hdGNoKHdvcmRPcGVyYXRvcktleXdvcmRzUmVnZXhwKSkge1xuICAgIHJldHVybiBbXCJvcGVyYXRvclwiLCBcIm9wZXJhdG9yXCJdO1xuICB9XG4gIC8vIFdvcmRcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXlxcJD9bLV9dKlthLXowLTldK1tcXHctXSovaSkpIHtcbiAgICAvLyBWYXJpYWJsZVxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14oXFwufFxcWylbXFx3LVxcJ1xcXCJcXF1dKy9pLCBmYWxzZSkpIHtcbiAgICAgIGlmICghd29yZElzVGFnKHN0cmVhbS5jdXJyZW50KCkpKSB7XG4gICAgICAgIHN0cmVhbS5tYXRjaCgnLicpO1xuICAgICAgICByZXR1cm4gW1widmFyaWFibGVcIiwgXCJ2YXJpYWJsZS1uYW1lXCJdO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gW1widmFyaWFibGVcIiwgXCJ3b3JkXCJdO1xuICB9XG4gIC8vIE9wZXJhdG9yc1xuICBpZiAoc3RyZWFtLm1hdGNoKG9wZXJhdG9yc1JlZ2V4cCkpIHtcbiAgICByZXR1cm4gW1wib3BlcmF0b3JcIiwgc3RyZWFtLmN1cnJlbnQoKV07XG4gIH1cbiAgLy8gRGVsaW1pdGVyc1xuICBpZiAoL1s6Oyx7fVxcW1xcXVxcKFxcKV0vLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gW251bGwsIGNoXTtcbiAgfVxuICAvLyBOb24tZGV0ZWN0ZWQgaXRlbXNcbiAgc3RyZWFtLm5leHQoKTtcbiAgcmV0dXJuIFtudWxsLCBudWxsXTtcbn1cblxuLyoqXG4gKiBUb2tlbiBjb21tZW50XG4gKi9cbmZ1bmN0aW9uIHRva2VuQ0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAobWF5YmVFbmQgJiYgY2ggPT0gXCIvXCIpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBbXCJjb21tZW50XCIsIFwiY29tbWVudFwiXTtcbn1cblxuLyoqXG4gKiBUb2tlbiBzdHJpbmdcbiAqL1xuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlICgoY2ggPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAoY2ggPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgaWYgKHF1b3RlID09IFwiKVwiKSBzdHJlYW0uYmFja1VwKDEpO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBjaCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKGNoID09IHF1b3RlIHx8ICFlc2NhcGVkICYmIHF1b3RlICE9IFwiKVwiKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgcmV0dXJuIFtcInN0cmluZ1wiLCBcInN0cmluZ1wiXTtcbiAgfTtcbn1cblxuLyoqXG4gKiBUb2tlbiBwYXJlbnRoZXNpemVkXG4gKi9cbmZ1bmN0aW9uIHRva2VuUGFyZW50aGVzaXplZChzdHJlYW0sIHN0YXRlKSB7XG4gIHN0cmVhbS5uZXh0KCk7IC8vIE11c3QgYmUgXCIoXCJcbiAgaWYgKCFzdHJlYW0ubWF0Y2goL1xccypbXFxcIlxcJyldLywgZmFsc2UpKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKFwiKVwiKTtlbHNlIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgcmV0dXJuIFtudWxsLCBcIihcIl07XG59XG5cbi8qKlxuICogQ29udGV4dCBtYW5hZ2VtZW50XG4gKi9cbmZ1bmN0aW9uIENvbnRleHQodHlwZSwgaW5kZW50LCBwcmV2LCBsaW5lKSB7XG4gIHRoaXMudHlwZSA9IHR5cGU7XG4gIHRoaXMuaW5kZW50ID0gaW5kZW50O1xuICB0aGlzLnByZXYgPSBwcmV2O1xuICB0aGlzLmxpbmUgPSBsaW5lIHx8IHtcbiAgICBmaXJzdFdvcmQ6IFwiXCIsXG4gICAgaW5kZW50OiAwXG4gIH07XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCB0eXBlLCBpbmRlbnQpIHtcbiAgaW5kZW50ID0gaW5kZW50ID49IDAgPyBpbmRlbnQgOiBzdHJlYW0uaW5kZW50VW5pdDtcbiAgc3RhdGUuY29udGV4dCA9IG5ldyBDb250ZXh0KHR5cGUsIHN0cmVhbS5pbmRlbnRhdGlvbigpICsgaW5kZW50LCBzdGF0ZS5jb250ZXh0KTtcbiAgcmV0dXJuIHR5cGU7XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KHN0YXRlLCBzdHJlYW0sIGN1cnJlbnRJbmRlbnQpIHtcbiAgdmFyIGNvbnRleHRJbmRlbnQgPSBzdGF0ZS5jb250ZXh0LmluZGVudCAtIHN0cmVhbS5pbmRlbnRVbml0O1xuICBjdXJyZW50SW5kZW50ID0gY3VycmVudEluZGVudCB8fCBmYWxzZTtcbiAgc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbiAgaWYgKGN1cnJlbnRJbmRlbnQpIHN0YXRlLmNvbnRleHQuaW5kZW50ID0gY29udGV4dEluZGVudDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQudHlwZTtcbn1cbmZ1bmN0aW9uIHBhc3ModHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICByZXR1cm4gc3RhdGVzW3N0YXRlLmNvbnRleHQudHlwZV0odHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG59XG5mdW5jdGlvbiBwb3BBbmRQYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUsIG4pIHtcbiAgZm9yICh2YXIgaSA9IG4gfHwgMTsgaSA+IDA7IGktLSkgc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbiAgcmV0dXJuIHBhc3ModHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG59XG5cbi8qKlxuICogUGFyc2VyXG4gKi9cbmZ1bmN0aW9uIHdvcmRJc1RhZyh3b3JkKSB7XG4gIHJldHVybiB3b3JkLnRvTG93ZXJDYXNlKCkgaW4gdGFnS2V5d29yZHM7XG59XG5mdW5jdGlvbiB3b3JkSXNQcm9wZXJ0eSh3b3JkKSB7XG4gIHdvcmQgPSB3b3JkLnRvTG93ZXJDYXNlKCk7XG4gIHJldHVybiB3b3JkIGluIHByb3BlcnR5S2V5d29yZHMgfHwgd29yZCBpbiBmb250UHJvcGVydGllcztcbn1cbmZ1bmN0aW9uIHdvcmRJc0Jsb2NrKHdvcmQpIHtcbiAgcmV0dXJuIHdvcmQudG9Mb3dlckNhc2UoKSBpbiBibG9ja0tleXdvcmRzO1xufVxuZnVuY3Rpb24gd29yZElzVmVuZG9yUHJlZml4KHdvcmQpIHtcbiAgcmV0dXJuIHdvcmQudG9Mb3dlckNhc2UoKS5tYXRjaCh2ZW5kb3JQcmVmaXhlc1JlZ2V4cCk7XG59XG5mdW5jdGlvbiB3b3JkQXNWYWx1ZSh3b3JkKSB7XG4gIHZhciB3b3JkTEMgPSB3b3JkLnRvTG93ZXJDYXNlKCk7XG4gIHZhciBvdmVycmlkZSA9IFwidmFyaWFibGVcIjtcbiAgaWYgKHdvcmRJc1RhZyh3b3JkKSkgb3ZlcnJpZGUgPSBcInRhZ1wiO2Vsc2UgaWYgKHdvcmRJc0Jsb2NrKHdvcmQpKSBvdmVycmlkZSA9IFwiYmxvY2sta2V5d29yZFwiO2Vsc2UgaWYgKHdvcmRJc1Byb3BlcnR5KHdvcmQpKSBvdmVycmlkZSA9IFwicHJvcGVydHlcIjtlbHNlIGlmICh3b3JkTEMgaW4gdmFsdWVLZXl3b3JkcyB8fCB3b3JkTEMgaW4gY29tbW9uQXRvbXMpIG92ZXJyaWRlID0gXCJhdG9tXCI7ZWxzZSBpZiAod29yZExDID09IFwicmV0dXJuXCIgfHwgd29yZExDIGluIGNvbG9yS2V5d29yZHMpIG92ZXJyaWRlID0gXCJrZXl3b3JkXCI7XG5cbiAgLy8gRm9udCBmYW1pbHlcbiAgZWxzZSBpZiAod29yZC5tYXRjaCgvXltBLVpdLykpIG92ZXJyaWRlID0gXCJzdHJpbmdcIjtcbiAgcmV0dXJuIG92ZXJyaWRlO1xufVxuZnVuY3Rpb24gdHlwZUlzQmxvY2sodHlwZSwgc3RyZWFtKSB7XG4gIHJldHVybiBlbmRPZkxpbmUoc3RyZWFtKSAmJiAodHlwZSA9PSBcIntcIiB8fCB0eXBlID09IFwiXVwiIHx8IHR5cGUgPT0gXCJoYXNoXCIgfHwgdHlwZSA9PSBcInF1YWxpZmllclwiKSB8fCB0eXBlID09IFwiYmxvY2stbWl4aW5cIjtcbn1cbmZ1bmN0aW9uIHR5cGVJc0ludGVycG9sYXRpb24odHlwZSwgc3RyZWFtKSB7XG4gIHJldHVybiB0eXBlID09IFwie1wiICYmIHN0cmVhbS5tYXRjaCgvXlxccypcXCQ/W1xcdy1dKy9pLCBmYWxzZSk7XG59XG5mdW5jdGlvbiB0eXBlSXNQc2V1ZG8odHlwZSwgc3RyZWFtKSB7XG4gIHJldHVybiB0eXBlID09IFwiOlwiICYmIHN0cmVhbS5tYXRjaCgvXlthLXotXSsvLCBmYWxzZSk7XG59XG5mdW5jdGlvbiBzdGFydE9mTGluZShzdHJlYW0pIHtcbiAgcmV0dXJuIHN0cmVhbS5zb2woKSB8fCBzdHJlYW0uc3RyaW5nLm1hdGNoKG5ldyBSZWdFeHAoXCJeXFxcXHMqXCIgKyBlc2NhcGVSZWdFeHAoc3RyZWFtLmN1cnJlbnQoKSkpKTtcbn1cbmZ1bmN0aW9uIGVuZE9mTGluZShzdHJlYW0pIHtcbiAgcmV0dXJuIHN0cmVhbS5lb2woKSB8fCBzdHJlYW0ubWF0Y2goL15cXHMqJC8sIGZhbHNlKTtcbn1cbmZ1bmN0aW9uIGZpcnN0V29yZE9mTGluZShsaW5lKSB7XG4gIHZhciByZSA9IC9eXFxzKlstX10qW2EtejAtOV0rW1xcdy1dKi9pO1xuICB2YXIgcmVzdWx0ID0gdHlwZW9mIGxpbmUgPT0gXCJzdHJpbmdcIiA/IGxpbmUubWF0Y2gocmUpIDogbGluZS5zdHJpbmcubWF0Y2gocmUpO1xuICByZXR1cm4gcmVzdWx0ID8gcmVzdWx0WzBdLnJlcGxhY2UoL15cXHMqLywgXCJcIikgOiBcIlwiO1xufVxuXG4vKipcbiAqIEJsb2NrXG4gKi9cbnN0YXRlcy5ibG9jayA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gIGlmICh0eXBlID09IFwiY29tbWVudFwiICYmIHN0YXJ0T2ZMaW5lKHN0cmVhbSkgfHwgdHlwZSA9PSBcIixcIiAmJiBlbmRPZkxpbmUoc3RyZWFtKSB8fCB0eXBlID09IFwibWl4aW5cIikge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIsIDApO1xuICB9XG4gIGlmICh0eXBlSXNJbnRlcnBvbGF0aW9uKHR5cGUsIHN0cmVhbSkpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJpbnRlcnBvbGF0aW9uXCIpO1xuICB9XG4gIGlmIChlbmRPZkxpbmUoc3RyZWFtKSAmJiB0eXBlID09IFwiXVwiKSB7XG4gICAgaWYgKCEvXlxccyooXFwufCN8OnxcXFt8XFwqfCYpLy50ZXN0KHN0cmVhbS5zdHJpbmcpICYmICF3b3JkSXNUYWcoZmlyc3RXb3JkT2ZMaW5lKHN0cmVhbSkpKSB7XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiLCAwKTtcbiAgICB9XG4gIH1cbiAgaWYgKHR5cGVJc0Jsb2NrKHR5cGUsIHN0cmVhbSkpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcIn1cIiAmJiBlbmRPZkxpbmUoc3RyZWFtKSkge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIsIDApO1xuICB9XG4gIGlmICh0eXBlID09IFwidmFyaWFibGUtbmFtZVwiKSB7XG4gICAgaWYgKHN0cmVhbS5zdHJpbmcubWF0Y2goL15cXHM/XFwkW1xcdy1cXC5cXFtcXF1cXCdcXFwiXSskLykgfHwgd29yZElzQmxvY2soZmlyc3RXb3JkT2ZMaW5lKHN0cmVhbSkpKSB7XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJ2YXJpYWJsZU5hbWVcIik7XG4gICAgfSBlbHNlIHtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcInZhcmlhYmxlTmFtZVwiLCAwKTtcbiAgICB9XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCI9XCIpIHtcbiAgICBpZiAoIWVuZE9mTGluZShzdHJlYW0pICYmICF3b3JkSXNCbG9jayhmaXJzdFdvcmRPZkxpbmUoc3RyZWFtKSkpIHtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIsIDApO1xuICAgIH1cbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcIipcIikge1xuICAgIGlmIChlbmRPZkxpbmUoc3RyZWFtKSB8fCBzdHJlYW0ubWF0Y2goL1xccyooLHxcXC58I3xcXFt8Onx7KS8sIGZhbHNlKSkge1xuICAgICAgb3ZlcnJpZGUgPSBcInRhZ1wiO1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYmxvY2tcIik7XG4gICAgfVxuICB9XG4gIGlmICh0eXBlSXNQc2V1ZG8odHlwZSwgc3RyZWFtKSkge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcInBzZXVkb1wiKTtcbiAgfVxuICBpZiAoL0AoZm9udC1mYWNlfG1lZGlhfHN1cHBvcnRzfCgtbW96LSk/ZG9jdW1lbnQpLy50ZXN0KHR5cGUpKSB7XG4gICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIGVuZE9mTGluZShzdHJlYW0pID8gXCJibG9ja1wiIDogXCJhdEJsb2NrXCIpO1xuICB9XG4gIGlmICgvQCgtKG1venxtc3xvfHdlYmtpdCktKT9rZXlmcmFtZXMkLy50ZXN0KHR5cGUpKSB7XG4gICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwia2V5ZnJhbWVzXCIpO1xuICB9XG4gIGlmICgvQGV4dGVuZHM/Ly50ZXN0KHR5cGUpKSB7XG4gICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiZXh0ZW5kXCIsIDApO1xuICB9XG4gIGlmICh0eXBlICYmIHR5cGUuY2hhckF0KDApID09IFwiQFwiKSB7XG4gICAgLy8gUHJvcGVydHkgTG9va3VwXG4gICAgaWYgKHN0cmVhbS5pbmRlbnRhdGlvbigpID4gMCAmJiB3b3JkSXNQcm9wZXJ0eShzdHJlYW0uY3VycmVudCgpLnNsaWNlKDEpKSkge1xuICAgICAgb3ZlcnJpZGUgPSBcInZhcmlhYmxlXCI7XG4gICAgICByZXR1cm4gXCJibG9ja1wiO1xuICAgIH1cbiAgICBpZiAoLyhAaW1wb3J0fEByZXF1aXJlfEBjaGFyc2V0KS8udGVzdCh0eXBlKSkge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYmxvY2tcIiwgMCk7XG4gICAgfVxuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIpO1xuICB9XG4gIGlmICh0eXBlID09IFwicmVmZXJlbmNlXCIgJiYgZW5kT2ZMaW5lKHN0cmVhbSkpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcIihcIikge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcInBhcmVuc1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcInZlbmRvci1wcmVmaXhlc1wiKSB7XG4gICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwidmVuZG9yUHJlZml4ZXNcIik7XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIHtcbiAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgb3ZlcnJpZGUgPSB3b3JkQXNWYWx1ZSh3b3JkKTtcbiAgICBpZiAob3ZlcnJpZGUgPT0gXCJwcm9wZXJ0eVwiKSB7XG4gICAgICBpZiAoc3RhcnRPZkxpbmUoc3RyZWFtKSkge1xuICAgICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiLCAwKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIG92ZXJyaWRlID0gXCJhdG9tXCI7XG4gICAgICAgIHJldHVybiBcImJsb2NrXCI7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChvdmVycmlkZSA9PSBcInRhZ1wiKSB7XG4gICAgICAvLyB0YWcgaXMgYSBjc3MgdmFsdWVcbiAgICAgIGlmICgvZW1iZWR8bWVudXxwcmV8cHJvZ3Jlc3N8c3VifHRhYmxlLy50ZXN0KHdvcmQpKSB7XG4gICAgICAgIGlmICh3b3JkSXNQcm9wZXJ0eShmaXJzdFdvcmRPZkxpbmUoc3RyZWFtKSkpIHtcbiAgICAgICAgICBvdmVycmlkZSA9IFwiYXRvbVwiO1xuICAgICAgICAgIHJldHVybiBcImJsb2NrXCI7XG4gICAgICAgIH1cbiAgICAgIH1cblxuICAgICAgLy8gdGFnIGlzIGFuIGF0dHJpYnV0ZVxuICAgICAgaWYgKHN0cmVhbS5zdHJpbmcubWF0Y2gobmV3IFJlZ0V4cChcIlxcXFxbXFxcXHMqXCIgKyB3b3JkICsgXCJ8XCIgKyB3b3JkICsgXCJcXFxccypcXFxcXVwiKSkpIHtcbiAgICAgICAgb3ZlcnJpZGUgPSBcImF0b21cIjtcbiAgICAgICAgcmV0dXJuIFwiYmxvY2tcIjtcbiAgICAgIH1cblxuICAgICAgLy8gdGFnIGlzIGEgdmFyaWFibGVcbiAgICAgIGlmICh0YWdWYXJpYWJsZXNSZWdleHAudGVzdCh3b3JkKSkge1xuICAgICAgICBpZiAoc3RhcnRPZkxpbmUoc3RyZWFtKSAmJiBzdHJlYW0uc3RyaW5nLm1hdGNoKC89LykgfHwgIXN0YXJ0T2ZMaW5lKHN0cmVhbSkgJiYgIXN0cmVhbS5zdHJpbmcubWF0Y2goL14oXFxzKlxcLnwjfFxcJnxcXFt8XFwvfD58XFwqKS8pICYmICF3b3JkSXNUYWcoZmlyc3RXb3JkT2ZMaW5lKHN0cmVhbSkpKSB7XG4gICAgICAgICAgb3ZlcnJpZGUgPSBcInZhcmlhYmxlXCI7XG4gICAgICAgICAgaWYgKHdvcmRJc0Jsb2NrKGZpcnN0V29yZE9mTGluZShzdHJlYW0pKSkgcmV0dXJuIFwiYmxvY2tcIjtcbiAgICAgICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiLCAwKTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgaWYgKGVuZE9mTGluZShzdHJlYW0pKSByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgICB9XG4gICAgaWYgKG92ZXJyaWRlID09IFwiYmxvY2sta2V5d29yZFwiKSB7XG4gICAgICBvdmVycmlkZSA9IFwia2V5d29yZFwiO1xuXG4gICAgICAvLyBQb3N0Zml4IGNvbmRpdGlvbmFsc1xuICAgICAgaWYgKHN0cmVhbS5jdXJyZW50KC8oaWZ8dW5sZXNzKS8pICYmICFzdGFydE9mTGluZShzdHJlYW0pKSB7XG4gICAgICAgIHJldHVybiBcImJsb2NrXCI7XG4gICAgICB9XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgICB9XG4gICAgaWYgKHdvcmQgPT0gXCJyZXR1cm5cIikgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYmxvY2tcIiwgMCk7XG5cbiAgICAvLyBQbGFjZWhvbGRlciBzZWxlY3RvclxuICAgIGlmIChvdmVycmlkZSA9PSBcInZhcmlhYmxlXCIgJiYgc3RyZWFtLnN0cmluZy5tYXRjaCgvXlxccz9cXCRbXFx3LVxcLlxcW1xcXVxcJ1xcXCJdKyQvKSkge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYmxvY2tcIik7XG4gICAgfVxuICB9XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG59O1xuXG4vKipcbiAqIFBhcmVuc1xuICovXG5zdGF0ZXMucGFyZW5zID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcInBhcmVuc1wiKTtcbiAgaWYgKHR5cGUgPT0gXCIpXCIpIHtcbiAgICBpZiAoc3RhdGUuY29udGV4dC5wcmV2LnR5cGUgPT0gXCJwYXJlbnNcIikge1xuICAgICAgcmV0dXJuIHBvcENvbnRleHQoc3RhdGUsIHN0cmVhbSk7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uc3RyaW5nLm1hdGNoKC9eW2Etel1bXFx3LV0qXFwoL2kpICYmIGVuZE9mTGluZShzdHJlYW0pIHx8IHdvcmRJc0Jsb2NrKGZpcnN0V29yZE9mTGluZShzdHJlYW0pKSB8fCAvKFxcLnwjfDp8XFxbfFxcKnwmfD58fnxcXCt8XFwvKS8udGVzdChmaXJzdFdvcmRPZkxpbmUoc3RyZWFtKSkgfHwgIXN0cmVhbS5zdHJpbmcubWF0Y2goL14tP1thLXpdW1xcdy1cXC5cXFtcXF1cXCdcXFwiXSpcXHMqPS8pICYmIHdvcmRJc1RhZyhmaXJzdFdvcmRPZkxpbmUoc3RyZWFtKSkpIHtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLnN0cmluZy5tYXRjaCgvXltcXCQtXT9bYS16XVtcXHctXFwuXFxbXFxdXFwnXFxcIl0qXFxzKj0vKSB8fCBzdHJlYW0uc3RyaW5nLm1hdGNoKC9eXFxzKihcXCh8XFwpfFswLTldKS8pIHx8IHN0cmVhbS5zdHJpbmcubWF0Y2goL15cXHMrW2Etel1bXFx3LV0qXFwoL2kpIHx8IHN0cmVhbS5zdHJpbmcubWF0Y2goL15cXHMrW1xcJC1dP1thLXpdL2kpKSB7XG4gICAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiLCAwKTtcbiAgICB9XG4gICAgaWYgKGVuZE9mTGluZShzdHJlYW0pKSByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtlbHNlIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIsIDApO1xuICB9XG4gIGlmICh0eXBlICYmIHR5cGUuY2hhckF0KDApID09IFwiQFwiICYmIHdvcmRJc1Byb3BlcnR5KHN0cmVhbS5jdXJyZW50KCkuc2xpY2UoMSkpKSB7XG4gICAgb3ZlcnJpZGUgPSBcInZhcmlhYmxlXCI7XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIHtcbiAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgb3ZlcnJpZGUgPSB3b3JkQXNWYWx1ZSh3b3JkKTtcbiAgICBpZiAob3ZlcnJpZGUgPT0gXCJ0YWdcIiAmJiB0YWdWYXJpYWJsZXNSZWdleHAudGVzdCh3b3JkKSkge1xuICAgICAgb3ZlcnJpZGUgPSBcInZhcmlhYmxlXCI7XG4gICAgfVxuICAgIGlmIChvdmVycmlkZSA9PSBcInByb3BlcnR5XCIgfHwgd29yZCA9PSBcInRvXCIpIG92ZXJyaWRlID0gXCJhdG9tXCI7XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZS1uYW1lXCIpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJ2YXJpYWJsZU5hbWVcIik7XG4gIH1cbiAgaWYgKHR5cGVJc1BzZXVkbyh0eXBlLCBzdHJlYW0pKSB7XG4gICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwicHNldWRvXCIpO1xuICB9XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG59O1xuXG4vKipcbiAqIFZlbmRvciBwcmVmaXhlc1xuICovXG5zdGF0ZXMudmVuZG9yUHJlZml4ZXMgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAodHlwZSA9PSBcIndvcmRcIikge1xuICAgIG92ZXJyaWRlID0gXCJwcm9wZXJ0eVwiO1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIsIDApO1xuICB9XG4gIHJldHVybiBwb3BDb250ZXh0KHN0YXRlLCBzdHJlYW0pO1xufTtcblxuLyoqXG4gKiBQc2V1ZG9cbiAqL1xuc3RhdGVzLnBzZXVkbyA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gIGlmICghd29yZElzUHJvcGVydHkoZmlyc3RXb3JkT2ZMaW5lKHN0cmVhbS5zdHJpbmcpKSkge1xuICAgIHN0cmVhbS5tYXRjaCgvXlthLXotXSsvKTtcbiAgICBvdmVycmlkZSA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICBpZiAoZW5kT2ZMaW5lKHN0cmVhbSkpIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIpO1xuICAgIHJldHVybiBwb3BDb250ZXh0KHN0YXRlLCBzdHJlYW0pO1xuICB9XG4gIHJldHVybiBwb3BBbmRQYXNzKHR5cGUsIHN0cmVhbSwgc3RhdGUpO1xufTtcblxuLyoqXG4gKiBhdEJsb2NrXG4gKi9cbnN0YXRlcy5hdEJsb2NrID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImF0QmxvY2tfcGFyZW5zXCIpO1xuICBpZiAodHlwZUlzQmxvY2sodHlwZSwgc3RyZWFtKSkge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIpO1xuICB9XG4gIGlmICh0eXBlSXNJbnRlcnBvbGF0aW9uKHR5cGUsIHN0cmVhbSkpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJpbnRlcnBvbGF0aW9uXCIpO1xuICB9XG4gIGlmICh0eXBlID09IFwid29yZFwiKSB7XG4gICAgdmFyIHdvcmQgPSBzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCk7XG4gICAgaWYgKC9eKG9ubHl8bm90fGFuZHxvcikkLy50ZXN0KHdvcmQpKSBvdmVycmlkZSA9IFwia2V5d29yZFwiO2Vsc2UgaWYgKGRvY3VtZW50VHlwZXMuaGFzT3duUHJvcGVydHkod29yZCkpIG92ZXJyaWRlID0gXCJ0YWdcIjtlbHNlIGlmIChtZWRpYVR5cGVzLmhhc093blByb3BlcnR5KHdvcmQpKSBvdmVycmlkZSA9IFwiYXR0cmlidXRlXCI7ZWxzZSBpZiAobWVkaWFGZWF0dXJlcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSkgb3ZlcnJpZGUgPSBcInByb3BlcnR5XCI7ZWxzZSBpZiAobm9uU3RhbmRhcmRQcm9wZXJ0eUtleXdvcmRzLmhhc093blByb3BlcnR5KHdvcmQpKSBvdmVycmlkZSA9IFwic3RyaW5nLnNwZWNpYWxcIjtlbHNlIG92ZXJyaWRlID0gd29yZEFzVmFsdWUoc3RyZWFtLmN1cnJlbnQoKSk7XG4gICAgaWYgKG92ZXJyaWRlID09IFwidGFnXCIgJiYgZW5kT2ZMaW5lKHN0cmVhbSkpIHtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIpO1xuICAgIH1cbiAgfVxuICBpZiAodHlwZSA9PSBcIm9wZXJhdG9yXCIgJiYgL14obm90fGFuZHxvcikkLy50ZXN0KHN0cmVhbS5jdXJyZW50KCkpKSB7XG4gICAgb3ZlcnJpZGUgPSBcImtleXdvcmRcIjtcbiAgfVxuICByZXR1cm4gc3RhdGUuY29udGV4dC50eXBlO1xufTtcbnN0YXRlcy5hdEJsb2NrX3BhcmVucyA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gIGlmICh0eXBlID09IFwie1wiIHx8IHR5cGUgPT0gXCJ9XCIpIHJldHVybiBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIGlmICh0eXBlID09IFwiKVwiKSB7XG4gICAgaWYgKGVuZE9mTGluZShzdHJlYW0pKSByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtlbHNlIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImF0QmxvY2tcIik7XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIHtcbiAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCkudG9Mb3dlckNhc2UoKTtcbiAgICBvdmVycmlkZSA9IHdvcmRBc1ZhbHVlKHdvcmQpO1xuICAgIGlmICgvXihtYXh8bWluKS8udGVzdCh3b3JkKSkgb3ZlcnJpZGUgPSBcInByb3BlcnR5XCI7XG4gICAgaWYgKG92ZXJyaWRlID09IFwidGFnXCIpIHtcbiAgICAgIHRhZ1ZhcmlhYmxlc1JlZ2V4cC50ZXN0KHdvcmQpID8gb3ZlcnJpZGUgPSBcInZhcmlhYmxlXCIgOiBvdmVycmlkZSA9IFwiYXRvbVwiO1xuICAgIH1cbiAgICByZXR1cm4gc3RhdGUuY29udGV4dC50eXBlO1xuICB9XG4gIHJldHVybiBzdGF0ZXMuYXRCbG9jayh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbn07XG5cbi8qKlxuICogS2V5ZnJhbWVzXG4gKi9cbnN0YXRlcy5rZXlmcmFtZXMgPSBmdW5jdGlvbiAodHlwZSwgc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLmluZGVudGF0aW9uKCkgPT0gXCIwXCIgJiYgKHR5cGUgPT0gXCJ9XCIgJiYgc3RhcnRPZkxpbmUoc3RyZWFtKSB8fCB0eXBlID09IFwiXVwiIHx8IHR5cGUgPT0gXCJoYXNoXCIgfHwgdHlwZSA9PSBcInF1YWxpZmllclwiIHx8IHdvcmRJc1RhZyhzdHJlYW0uY3VycmVudCgpKSkpIHtcbiAgICByZXR1cm4gcG9wQW5kUGFzcyh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcIntcIikgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwia2V5ZnJhbWVzXCIpO1xuICBpZiAodHlwZSA9PSBcIn1cIikge1xuICAgIGlmIChzdGFydE9mTGluZShzdHJlYW0pKSByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSwgc3RyZWFtLCB0cnVlKTtlbHNlIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImtleWZyYW1lc1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcInVuaXRcIiAmJiAvXlswLTldK1xcJSQvLnRlc3Qoc3RyZWFtLmN1cnJlbnQoKSkpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJrZXlmcmFtZXNcIik7XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCJ3b3JkXCIpIHtcbiAgICBvdmVycmlkZSA9IHdvcmRBc1ZhbHVlKHN0cmVhbS5jdXJyZW50KCkpO1xuICAgIGlmIChvdmVycmlkZSA9PSBcImJsb2NrLWtleXdvcmRcIikge1xuICAgICAgb3ZlcnJpZGUgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImtleWZyYW1lc1wiKTtcbiAgICB9XG4gIH1cbiAgaWYgKC9AKGZvbnQtZmFjZXxtZWRpYXxzdXBwb3J0c3woLW1vei0pP2RvY3VtZW50KS8udGVzdCh0eXBlKSkge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBlbmRPZkxpbmUoc3RyZWFtKSA/IFwiYmxvY2tcIiA6IFwiYXRCbG9ja1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcIm1peGluXCIpIHtcbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiLCAwKTtcbiAgfVxuICByZXR1cm4gc3RhdGUuY29udGV4dC50eXBlO1xufTtcblxuLyoqXG4gKiBJbnRlcnBvbGF0aW9uXG4gKi9cbnN0YXRlcy5pbnRlcnBvbGF0aW9uID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHR5cGUgPT0gXCJ7XCIpIHBvcENvbnRleHQoc3RhdGUsIHN0cmVhbSkgJiYgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgaWYgKHR5cGUgPT0gXCJ9XCIpIHtcbiAgICBpZiAoc3RyZWFtLnN0cmluZy5tYXRjaCgvXlxccyooXFwufCN8OnxcXFt8XFwqfCZ8Pnx+fFxcK3xcXC8pL2kpIHx8IHN0cmVhbS5zdHJpbmcubWF0Y2goL15cXHMqW2Etel0vaSkgJiYgd29yZElzVGFnKGZpcnN0V29yZE9mTGluZShzdHJlYW0pKSkge1xuICAgICAgcmV0dXJuIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0sIFwiYmxvY2tcIik7XG4gICAgfVxuICAgIGlmICghc3RyZWFtLnN0cmluZy5tYXRjaCgvXihcXHt8XFxzKlxcJikvKSB8fCBzdHJlYW0ubWF0Y2goL1xccypbXFx3LV0vLCBmYWxzZSkpIHtcbiAgICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcImJsb2NrXCIsIDApO1xuICAgIH1cbiAgICByZXR1cm4gcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbSwgXCJibG9ja1wiKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcInZhcmlhYmxlLW5hbWVcIikge1xuICAgIHJldHVybiBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLCBcInZhcmlhYmxlTmFtZVwiLCAwKTtcbiAgfVxuICBpZiAodHlwZSA9PSBcIndvcmRcIikge1xuICAgIG92ZXJyaWRlID0gd29yZEFzVmFsdWUoc3RyZWFtLmN1cnJlbnQoKSk7XG4gICAgaWYgKG92ZXJyaWRlID09IFwidGFnXCIpIG92ZXJyaWRlID0gXCJhdG9tXCI7XG4gIH1cbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQudHlwZTtcbn07XG5cbi8qKlxuICogRXh0ZW5kL3NcbiAqL1xuc3RhdGVzLmV4dGVuZCA9IGZ1bmN0aW9uICh0eXBlLCBzdHJlYW0sIHN0YXRlKSB7XG4gIGlmICh0eXBlID09IFwiW1wiIHx8IHR5cGUgPT0gXCI9XCIpIHJldHVybiBcImV4dGVuZFwiO1xuICBpZiAodHlwZSA9PSBcIl1cIikgcmV0dXJuIHBvcENvbnRleHQoc3RhdGUsIHN0cmVhbSk7XG4gIGlmICh0eXBlID09IFwid29yZFwiKSB7XG4gICAgb3ZlcnJpZGUgPSB3b3JkQXNWYWx1ZShzdHJlYW0uY3VycmVudCgpKTtcbiAgICByZXR1cm4gXCJleHRlbmRcIjtcbiAgfVxuICByZXR1cm4gcG9wQ29udGV4dChzdGF0ZSwgc3RyZWFtKTtcbn07XG5cbi8qKlxuICogVmFyaWFibGUgbmFtZVxuICovXG5zdGF0ZXMudmFyaWFibGVOYW1lID0gZnVuY3Rpb24gKHR5cGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHR5cGUgPT0gXCJzdHJpbmdcIiB8fCB0eXBlID09IFwiW1wiIHx8IHR5cGUgPT0gXCJdXCIgfHwgc3RyZWFtLmN1cnJlbnQoKS5tYXRjaCgvXihcXC58XFwkKS8pKSB7XG4gICAgaWYgKHN0cmVhbS5jdXJyZW50KCkubWF0Y2goL15cXC5bXFx3LV0rL2kpKSBvdmVycmlkZSA9IFwidmFyaWFibGVcIjtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZU5hbWVcIjtcbiAgfVxuICByZXR1cm4gcG9wQW5kUGFzcyh0eXBlLCBzdHJlYW0sIHN0YXRlKTtcbn07XG5leHBvcnQgY29uc3Qgc3R5bHVzID0ge1xuICBuYW1lOiBcInN0eWx1c1wiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBudWxsLFxuICAgICAgc3RhdGU6IFwiYmxvY2tcIixcbiAgICAgIGNvbnRleHQ6IG5ldyBDb250ZXh0KFwiYmxvY2tcIiwgMCwgbnVsbClcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoIXN0YXRlLnRva2VuaXplICYmIHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSAmJiB0eXBlb2Ygc3R5bGUgPT0gXCJvYmplY3RcIikge1xuICAgICAgdHlwZSA9IHN0eWxlWzFdO1xuICAgICAgc3R5bGUgPSBzdHlsZVswXTtcbiAgICB9XG4gICAgb3ZlcnJpZGUgPSBzdHlsZTtcbiAgICBzdGF0ZS5zdGF0ZSA9IHN0YXRlc1tzdGF0ZS5zdGF0ZV0odHlwZSwgc3RyZWFtLCBzdGF0ZSk7XG4gICAgcmV0dXJuIG92ZXJyaWRlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBpQ3gpIHtcbiAgICB2YXIgY3ggPSBzdGF0ZS5jb250ZXh0LFxuICAgICAgY2ggPSB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKSxcbiAgICAgIGluZGVudCA9IGN4LmluZGVudCxcbiAgICAgIGxpbmVGaXJzdFdvcmQgPSBmaXJzdFdvcmRPZkxpbmUodGV4dEFmdGVyKSxcbiAgICAgIGxpbmVJbmRlbnQgPSBjeC5saW5lLmluZGVudCxcbiAgICAgIHByZXZMaW5lRmlyc3RXb3JkID0gc3RhdGUuY29udGV4dC5wcmV2ID8gc3RhdGUuY29udGV4dC5wcmV2LmxpbmUuZmlyc3RXb3JkIDogXCJcIixcbiAgICAgIHByZXZMaW5lSW5kZW50ID0gc3RhdGUuY29udGV4dC5wcmV2ID8gc3RhdGUuY29udGV4dC5wcmV2LmxpbmUuaW5kZW50IDogbGluZUluZGVudDtcbiAgICBpZiAoY3gucHJldiAmJiAoY2ggPT0gXCJ9XCIgJiYgKGN4LnR5cGUgPT0gXCJibG9ja1wiIHx8IGN4LnR5cGUgPT0gXCJhdEJsb2NrXCIgfHwgY3gudHlwZSA9PSBcImtleWZyYW1lc1wiKSB8fCBjaCA9PSBcIilcIiAmJiAoY3gudHlwZSA9PSBcInBhcmVuc1wiIHx8IGN4LnR5cGUgPT0gXCJhdEJsb2NrX3BhcmVuc1wiKSB8fCBjaCA9PSBcIntcIiAmJiBjeC50eXBlID09IFwiYXRcIikpIHtcbiAgICAgIGluZGVudCA9IGN4LmluZGVudCAtIGlDeC51bml0O1xuICAgIH0gZWxzZSBpZiAoIS8oXFx9KS8udGVzdChjaCkpIHtcbiAgICAgIGlmICgvQHxcXCR8XFxkLy50ZXN0KGNoKSB8fCAvXlxcey8udGVzdCh0ZXh0QWZ0ZXIpIHx8IC9eXFxzKlxcLyhcXC98XFwqKS8udGVzdCh0ZXh0QWZ0ZXIpIHx8IC9eXFxzKlxcL1xcKi8udGVzdChwcmV2TGluZUZpcnN0V29yZCkgfHwgL15cXHMqW1xcdy1cXC5cXFtcXF1cXCdcXFwiXStcXHMqKFxcP3w6fFxcKyk/PS9pLnRlc3QodGV4dEFmdGVyKSB8fCAvXihcXCt8LSk/W2Etel1bXFx3LV0qXFwoL2kudGVzdCh0ZXh0QWZ0ZXIpIHx8IC9ecmV0dXJuLy50ZXN0KHRleHRBZnRlcikgfHwgd29yZElzQmxvY2sobGluZUZpcnN0V29yZCkpIHtcbiAgICAgICAgaW5kZW50ID0gbGluZUluZGVudDtcbiAgICAgIH0gZWxzZSBpZiAoLyhcXC58I3w6fFxcW3xcXCp8Jnw+fH58XFwrfFxcLykvLnRlc3QoY2gpIHx8IHdvcmRJc1RhZyhsaW5lRmlyc3RXb3JkKSkge1xuICAgICAgICBpZiAoL1xcLFxccyokLy50ZXN0KHByZXZMaW5lRmlyc3RXb3JkKSkge1xuICAgICAgICAgIGluZGVudCA9IHByZXZMaW5lSW5kZW50O1xuICAgICAgICB9IGVsc2UgaWYgKC8oXFwufCN8OnxcXFt8XFwqfCZ8Pnx+fFxcK3xcXC8pLy50ZXN0KHByZXZMaW5lRmlyc3RXb3JkKSB8fCB3b3JkSXNUYWcocHJldkxpbmVGaXJzdFdvcmQpKSB7XG4gICAgICAgICAgaW5kZW50ID0gbGluZUluZGVudCA8PSBwcmV2TGluZUluZGVudCA/IHByZXZMaW5lSW5kZW50IDogcHJldkxpbmVJbmRlbnQgKyBpQ3gudW5pdDtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICBpbmRlbnQgPSBsaW5lSW5kZW50O1xuICAgICAgICB9XG4gICAgICB9IGVsc2UgaWYgKCEvLFxccyokLy50ZXN0KHRleHRBZnRlcikgJiYgKHdvcmRJc1ZlbmRvclByZWZpeChsaW5lRmlyc3RXb3JkKSB8fCB3b3JkSXNQcm9wZXJ0eShsaW5lRmlyc3RXb3JkKSkpIHtcbiAgICAgICAgaWYgKHdvcmRJc0Jsb2NrKHByZXZMaW5lRmlyc3RXb3JkKSkge1xuICAgICAgICAgIGluZGVudCA9IGxpbmVJbmRlbnQgPD0gcHJldkxpbmVJbmRlbnQgPyBwcmV2TGluZUluZGVudCA6IHByZXZMaW5lSW5kZW50ICsgaUN4LnVuaXQ7XG4gICAgICAgIH0gZWxzZSBpZiAoL15cXHsvLnRlc3QocHJldkxpbmVGaXJzdFdvcmQpKSB7XG4gICAgICAgICAgaW5kZW50ID0gbGluZUluZGVudCA8PSBwcmV2TGluZUluZGVudCA/IGxpbmVJbmRlbnQgOiBwcmV2TGluZUluZGVudCArIGlDeC51bml0O1xuICAgICAgICB9IGVsc2UgaWYgKHdvcmRJc1ZlbmRvclByZWZpeChwcmV2TGluZUZpcnN0V29yZCkgfHwgd29yZElzUHJvcGVydHkocHJldkxpbmVGaXJzdFdvcmQpKSB7XG4gICAgICAgICAgaW5kZW50ID0gbGluZUluZGVudCA+PSBwcmV2TGluZUluZGVudCA/IHByZXZMaW5lSW5kZW50IDogbGluZUluZGVudDtcbiAgICAgICAgfSBlbHNlIGlmICgvXihcXC58I3w6fFxcW3xcXCp8JnxAfFxcK3xcXC18Pnx+fFxcLykvLnRlc3QocHJldkxpbmVGaXJzdFdvcmQpIHx8IC89XFxzKiQvLnRlc3QocHJldkxpbmVGaXJzdFdvcmQpIHx8IHdvcmRJc1RhZyhwcmV2TGluZUZpcnN0V29yZCkgfHwgL15cXCRbXFx3LVxcLlxcW1xcXVxcJ1xcXCJdLy50ZXN0KHByZXZMaW5lRmlyc3RXb3JkKSkge1xuICAgICAgICAgIGluZGVudCA9IHByZXZMaW5lSW5kZW50ICsgaUN4LnVuaXQ7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgaW5kZW50ID0gbGluZUluZGVudDtcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gaW5kZW50O1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypcXH0kLyxcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIi8vXCIsXG4gICAgICBibG9jazoge1xuICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgIH1cbiAgICB9LFxuICAgIGF1dG9jb21wbGV0ZTogaGludFdvcmRzXG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==