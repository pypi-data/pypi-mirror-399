"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1379],{

/***/ 1379
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   textile: () => (/* binding */ textile)
/* harmony export */ });
var TOKEN_STYLES = {
  addition: "inserted",
  attributes: "propertyName",
  bold: "strong",
  cite: "keyword",
  code: "monospace",
  definitionList: "list",
  deletion: "deleted",
  div: "punctuation",
  em: "emphasis",
  footnote: "variable",
  footCite: "qualifier",
  header: "heading",
  html: "comment",
  image: "atom",
  italic: "emphasis",
  link: "link",
  linkDefinition: "link",
  list1: "list",
  list2: "list.special",
  list3: "list",
  notextile: "string.special",
  pre: "operator",
  p: "content",
  quote: "bracket",
  span: "quote",
  specialChar: "character",
  strong: "strong",
  sub: "content.special",
  sup: "content.special",
  table: "variableName.special",
  tableHeading: "operator"
};
function startNewLine(stream, state) {
  state.mode = Modes.newLayout;
  state.tableHeading = false;
  if (state.layoutType === "definitionList" && state.spanningLayout && stream.match(RE("definitionListEnd"), false)) state.spanningLayout = false;
}
function handlePhraseModifier(stream, state, ch) {
  if (ch === "_") {
    if (stream.eat("_")) return togglePhraseModifier(stream, state, "italic", /__/, 2);else return togglePhraseModifier(stream, state, "em", /_/, 1);
  }
  if (ch === "*") {
    if (stream.eat("*")) {
      return togglePhraseModifier(stream, state, "bold", /\*\*/, 2);
    }
    return togglePhraseModifier(stream, state, "strong", /\*/, 1);
  }
  if (ch === "[") {
    if (stream.match(/\d+\]/)) state.footCite = true;
    return tokenStyles(state);
  }
  if (ch === "(") {
    var spec = stream.match(/^(r|tm|c)\)/);
    if (spec) return TOKEN_STYLES.specialChar;
  }
  if (ch === "<" && stream.match(/(\w+)[^>]+>[^<]+<\/\1>/)) return TOKEN_STYLES.html;
  if (ch === "?" && stream.eat("?")) return togglePhraseModifier(stream, state, "cite", /\?\?/, 2);
  if (ch === "=" && stream.eat("=")) return togglePhraseModifier(stream, state, "notextile", /==/, 2);
  if (ch === "-" && !stream.eat("-")) return togglePhraseModifier(stream, state, "deletion", /-/, 1);
  if (ch === "+") return togglePhraseModifier(stream, state, "addition", /\+/, 1);
  if (ch === "~") return togglePhraseModifier(stream, state, "sub", /~/, 1);
  if (ch === "^") return togglePhraseModifier(stream, state, "sup", /\^/, 1);
  if (ch === "%") return togglePhraseModifier(stream, state, "span", /%/, 1);
  if (ch === "@") return togglePhraseModifier(stream, state, "code", /@/, 1);
  if (ch === "!") {
    var type = togglePhraseModifier(stream, state, "image", /(?:\([^\)]+\))?!/, 1);
    stream.match(/^:\S+/); // optional Url portion
    return type;
  }
  return tokenStyles(state);
}
function togglePhraseModifier(stream, state, phraseModifier, closeRE, openSize) {
  var charBefore = stream.pos > openSize ? stream.string.charAt(stream.pos - openSize - 1) : null;
  var charAfter = stream.peek();
  if (state[phraseModifier]) {
    if ((!charAfter || /\W/.test(charAfter)) && charBefore && /\S/.test(charBefore)) {
      var type = tokenStyles(state);
      state[phraseModifier] = false;
      return type;
    }
  } else if ((!charBefore || /\W/.test(charBefore)) && charAfter && /\S/.test(charAfter) && stream.match(new RegExp("^.*\\S" + closeRE.source + "(?:\\W|$)"), false)) {
    state[phraseModifier] = true;
    state.mode = Modes.attributes;
  }
  return tokenStyles(state);
}
;
function tokenStyles(state) {
  var disabled = textileDisabled(state);
  if (disabled) return disabled;
  var styles = [];
  if (state.layoutType) styles.push(TOKEN_STYLES[state.layoutType]);
  styles = styles.concat(activeStyles(state, "addition", "bold", "cite", "code", "deletion", "em", "footCite", "image", "italic", "link", "span", "strong", "sub", "sup", "table", "tableHeading"));
  if (state.layoutType === "header") styles.push(TOKEN_STYLES.header + "-" + state.header);
  return styles.length ? styles.join(" ") : null;
}
function textileDisabled(state) {
  var type = state.layoutType;
  switch (type) {
    case "notextile":
    case "code":
    case "pre":
      return TOKEN_STYLES[type];
    default:
      if (state.notextile) return TOKEN_STYLES.notextile + (type ? " " + TOKEN_STYLES[type] : "");
      return null;
  }
}
function activeStyles(state) {
  var styles = [];
  for (var i = 1; i < arguments.length; ++i) {
    if (state[arguments[i]]) styles.push(TOKEN_STYLES[arguments[i]]);
  }
  return styles;
}
function blankLine(state) {
  var spanningLayout = state.spanningLayout,
    type = state.layoutType;
  for (var key in state) if (state.hasOwnProperty(key)) delete state[key];
  state.mode = Modes.newLayout;
  if (spanningLayout) {
    state.layoutType = type;
    state.spanningLayout = true;
  }
}
var REs = {
  cache: {},
  single: {
    bc: "bc",
    bq: "bq",
    definitionList: /- .*?:=+/,
    definitionListEnd: /.*=:\s*$/,
    div: "div",
    drawTable: /\|.*\|/,
    foot: /fn\d+/,
    header: /h[1-6]/,
    html: /\s*<(?:\/)?(\w+)(?:[^>]+)?>(?:[^<]+<\/\1>)?/,
    link: /[^"]+":\S/,
    linkDefinition: /\[[^\s\]]+\]\S+/,
    list: /(?:#+|\*+)/,
    notextile: "notextile",
    para: "p",
    pre: "pre",
    table: "table",
    tableCellAttributes: /[\/\\]\d+/,
    tableHeading: /\|_\./,
    tableText: /[^"_\*\[\(\?\+~\^%@|-]+/,
    text: /[^!"_=\*\[\(<\?\+~\^%@-]+/
  },
  attributes: {
    align: /(?:<>|<|>|=)/,
    selector: /\([^\(][^\)]+\)/,
    lang: /\[[^\[\]]+\]/,
    pad: /(?:\(+|\)+){1,2}/,
    css: /\{[^\}]+\}/
  },
  createRe: function (name) {
    switch (name) {
      case "drawTable":
        return REs.makeRe("^", REs.single.drawTable, "$");
      case "html":
        return REs.makeRe("^", REs.single.html, "(?:", REs.single.html, ")*", "$");
      case "linkDefinition":
        return REs.makeRe("^", REs.single.linkDefinition, "$");
      case "listLayout":
        return REs.makeRe("^", REs.single.list, RE("allAttributes"), "*\\s+");
      case "tableCellAttributes":
        return REs.makeRe("^", REs.choiceRe(REs.single.tableCellAttributes, RE("allAttributes")), "+\\.");
      case "type":
        return REs.makeRe("^", RE("allTypes"));
      case "typeLayout":
        return REs.makeRe("^", RE("allTypes"), RE("allAttributes"), "*\\.\\.?", "(\\s+|$)");
      case "attributes":
        return REs.makeRe("^", RE("allAttributes"), "+");
      case "allTypes":
        return REs.choiceRe(REs.single.div, REs.single.foot, REs.single.header, REs.single.bc, REs.single.bq, REs.single.notextile, REs.single.pre, REs.single.table, REs.single.para);
      case "allAttributes":
        return REs.choiceRe(REs.attributes.selector, REs.attributes.css, REs.attributes.lang, REs.attributes.align, REs.attributes.pad);
      default:
        return REs.makeRe("^", REs.single[name]);
    }
  },
  makeRe: function () {
    var pattern = "";
    for (var i = 0; i < arguments.length; ++i) {
      var arg = arguments[i];
      pattern += typeof arg === "string" ? arg : arg.source;
    }
    return new RegExp(pattern);
  },
  choiceRe: function () {
    var parts = [arguments[0]];
    for (var i = 1; i < arguments.length; ++i) {
      parts[i * 2 - 1] = "|";
      parts[i * 2] = arguments[i];
    }
    parts.unshift("(?:");
    parts.push(")");
    return REs.makeRe.apply(null, parts);
  }
};
function RE(name) {
  return REs.cache[name] || (REs.cache[name] = REs.createRe(name));
}
var Modes = {
  newLayout: function (stream, state) {
    if (stream.match(RE("typeLayout"), false)) {
      state.spanningLayout = false;
      return (state.mode = Modes.blockType)(stream, state);
    }
    var newMode;
    if (!textileDisabled(state)) {
      if (stream.match(RE("listLayout"), false)) newMode = Modes.list;else if (stream.match(RE("drawTable"), false)) newMode = Modes.table;else if (stream.match(RE("linkDefinition"), false)) newMode = Modes.linkDefinition;else if (stream.match(RE("definitionList"))) newMode = Modes.definitionList;else if (stream.match(RE("html"), false)) newMode = Modes.html;
    }
    return (state.mode = newMode || Modes.text)(stream, state);
  },
  blockType: function (stream, state) {
    var match, type;
    state.layoutType = null;
    if (match = stream.match(RE("type"))) type = match[0];else return (state.mode = Modes.text)(stream, state);
    if (match = type.match(RE("header"))) {
      state.layoutType = "header";
      state.header = parseInt(match[0][1]);
    } else if (type.match(RE("bq"))) {
      state.layoutType = "quote";
    } else if (type.match(RE("bc"))) {
      state.layoutType = "code";
    } else if (type.match(RE("foot"))) {
      state.layoutType = "footnote";
    } else if (type.match(RE("notextile"))) {
      state.layoutType = "notextile";
    } else if (type.match(RE("pre"))) {
      state.layoutType = "pre";
    } else if (type.match(RE("div"))) {
      state.layoutType = "div";
    } else if (type.match(RE("table"))) {
      state.layoutType = "table";
    }
    state.mode = Modes.attributes;
    return tokenStyles(state);
  },
  text: function (stream, state) {
    if (stream.match(RE("text"))) return tokenStyles(state);
    var ch = stream.next();
    if (ch === '"') return (state.mode = Modes.link)(stream, state);
    return handlePhraseModifier(stream, state, ch);
  },
  attributes: function (stream, state) {
    state.mode = Modes.layoutLength;
    if (stream.match(RE("attributes"))) return TOKEN_STYLES.attributes;else return tokenStyles(state);
  },
  layoutLength: function (stream, state) {
    if (stream.eat(".") && stream.eat(".")) state.spanningLayout = true;
    state.mode = Modes.text;
    return tokenStyles(state);
  },
  list: function (stream, state) {
    var match = stream.match(RE("list"));
    state.listDepth = match[0].length;
    var listMod = (state.listDepth - 1) % 3;
    if (!listMod) state.layoutType = "list1";else if (listMod === 1) state.layoutType = "list2";else state.layoutType = "list3";
    state.mode = Modes.attributes;
    return tokenStyles(state);
  },
  link: function (stream, state) {
    state.mode = Modes.text;
    if (stream.match(RE("link"))) {
      stream.match(/\S+/);
      return TOKEN_STYLES.link;
    }
    return tokenStyles(state);
  },
  linkDefinition: function (stream) {
    stream.skipToEnd();
    return TOKEN_STYLES.linkDefinition;
  },
  definitionList: function (stream, state) {
    stream.match(RE("definitionList"));
    state.layoutType = "definitionList";
    if (stream.match(/\s*$/)) state.spanningLayout = true;else state.mode = Modes.attributes;
    return tokenStyles(state);
  },
  html: function (stream) {
    stream.skipToEnd();
    return TOKEN_STYLES.html;
  },
  table: function (stream, state) {
    state.layoutType = "table";
    return (state.mode = Modes.tableCell)(stream, state);
  },
  tableCell: function (stream, state) {
    if (stream.match(RE("tableHeading"))) state.tableHeading = true;else stream.eat("|");
    state.mode = Modes.tableCellAttributes;
    return tokenStyles(state);
  },
  tableCellAttributes: function (stream, state) {
    state.mode = Modes.tableText;
    if (stream.match(RE("tableCellAttributes"))) return TOKEN_STYLES.attributes;else return tokenStyles(state);
  },
  tableText: function (stream, state) {
    if (stream.match(RE("tableText"))) return tokenStyles(state);
    if (stream.peek() === "|") {
      // end of cell
      state.mode = Modes.tableCell;
      return tokenStyles(state);
    }
    return handlePhraseModifier(stream, state, stream.next());
  }
};
const textile = {
  name: "textile",
  startState: function () {
    return {
      mode: Modes.newLayout
    };
  },
  token: function (stream, state) {
    if (stream.sol()) startNewLine(stream, state);
    return state.mode(stream, state);
  },
  blankLine: blankLine
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTM3OS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS90ZXh0aWxlLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBUT0tFTl9TVFlMRVMgPSB7XG4gIGFkZGl0aW9uOiBcImluc2VydGVkXCIsXG4gIGF0dHJpYnV0ZXM6IFwicHJvcGVydHlOYW1lXCIsXG4gIGJvbGQ6IFwic3Ryb25nXCIsXG4gIGNpdGU6IFwia2V5d29yZFwiLFxuICBjb2RlOiBcIm1vbm9zcGFjZVwiLFxuICBkZWZpbml0aW9uTGlzdDogXCJsaXN0XCIsXG4gIGRlbGV0aW9uOiBcImRlbGV0ZWRcIixcbiAgZGl2OiBcInB1bmN0dWF0aW9uXCIsXG4gIGVtOiBcImVtcGhhc2lzXCIsXG4gIGZvb3Rub3RlOiBcInZhcmlhYmxlXCIsXG4gIGZvb3RDaXRlOiBcInF1YWxpZmllclwiLFxuICBoZWFkZXI6IFwiaGVhZGluZ1wiLFxuICBodG1sOiBcImNvbW1lbnRcIixcbiAgaW1hZ2U6IFwiYXRvbVwiLFxuICBpdGFsaWM6IFwiZW1waGFzaXNcIixcbiAgbGluazogXCJsaW5rXCIsXG4gIGxpbmtEZWZpbml0aW9uOiBcImxpbmtcIixcbiAgbGlzdDE6IFwibGlzdFwiLFxuICBsaXN0MjogXCJsaXN0LnNwZWNpYWxcIixcbiAgbGlzdDM6IFwibGlzdFwiLFxuICBub3RleHRpbGU6IFwic3RyaW5nLnNwZWNpYWxcIixcbiAgcHJlOiBcIm9wZXJhdG9yXCIsXG4gIHA6IFwiY29udGVudFwiLFxuICBxdW90ZTogXCJicmFja2V0XCIsXG4gIHNwYW46IFwicXVvdGVcIixcbiAgc3BlY2lhbENoYXI6IFwiY2hhcmFjdGVyXCIsXG4gIHN0cm9uZzogXCJzdHJvbmdcIixcbiAgc3ViOiBcImNvbnRlbnQuc3BlY2lhbFwiLFxuICBzdXA6IFwiY29udGVudC5zcGVjaWFsXCIsXG4gIHRhYmxlOiBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCIsXG4gIHRhYmxlSGVhZGluZzogXCJvcGVyYXRvclwiXG59O1xuZnVuY3Rpb24gc3RhcnROZXdMaW5lKHN0cmVhbSwgc3RhdGUpIHtcbiAgc3RhdGUubW9kZSA9IE1vZGVzLm5ld0xheW91dDtcbiAgc3RhdGUudGFibGVIZWFkaW5nID0gZmFsc2U7XG4gIGlmIChzdGF0ZS5sYXlvdXRUeXBlID09PSBcImRlZmluaXRpb25MaXN0XCIgJiYgc3RhdGUuc3Bhbm5pbmdMYXlvdXQgJiYgc3RyZWFtLm1hdGNoKFJFKFwiZGVmaW5pdGlvbkxpc3RFbmRcIiksIGZhbHNlKSkgc3RhdGUuc3Bhbm5pbmdMYXlvdXQgPSBmYWxzZTtcbn1cbmZ1bmN0aW9uIGhhbmRsZVBocmFzZU1vZGlmaWVyKHN0cmVhbSwgc3RhdGUsIGNoKSB7XG4gIGlmIChjaCA9PT0gXCJfXCIpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChcIl9cIikpIHJldHVybiB0b2dnbGVQaHJhc2VNb2RpZmllcihzdHJlYW0sIHN0YXRlLCBcIml0YWxpY1wiLCAvX18vLCAyKTtlbHNlIHJldHVybiB0b2dnbGVQaHJhc2VNb2RpZmllcihzdHJlYW0sIHN0YXRlLCBcImVtXCIsIC9fLywgMSk7XG4gIH1cbiAgaWYgKGNoID09PSBcIipcIikge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgcmV0dXJuIHRvZ2dsZVBocmFzZU1vZGlmaWVyKHN0cmVhbSwgc3RhdGUsIFwiYm9sZFwiLCAvXFwqXFwqLywgMik7XG4gICAgfVxuICAgIHJldHVybiB0b2dnbGVQaHJhc2VNb2RpZmllcihzdHJlYW0sIHN0YXRlLCBcInN0cm9uZ1wiLCAvXFwqLywgMSk7XG4gIH1cbiAgaWYgKGNoID09PSBcIltcIikge1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL1xcZCtcXF0vKSkgc3RhdGUuZm9vdENpdGUgPSB0cnVlO1xuICAgIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG4gIH1cbiAgaWYgKGNoID09PSBcIihcIikge1xuICAgIHZhciBzcGVjID0gc3RyZWFtLm1hdGNoKC9eKHJ8dG18YylcXCkvKTtcbiAgICBpZiAoc3BlYykgcmV0dXJuIFRPS0VOX1NUWUxFUy5zcGVjaWFsQ2hhcjtcbiAgfVxuICBpZiAoY2ggPT09IFwiPFwiICYmIHN0cmVhbS5tYXRjaCgvKFxcdyspW14+XSs+W148XSs8XFwvXFwxPi8pKSByZXR1cm4gVE9LRU5fU1RZTEVTLmh0bWw7XG4gIGlmIChjaCA9PT0gXCI/XCIgJiYgc3RyZWFtLmVhdChcIj9cIikpIHJldHVybiB0b2dnbGVQaHJhc2VNb2RpZmllcihzdHJlYW0sIHN0YXRlLCBcImNpdGVcIiwgL1xcP1xcPy8sIDIpO1xuICBpZiAoY2ggPT09IFwiPVwiICYmIHN0cmVhbS5lYXQoXCI9XCIpKSByZXR1cm4gdG9nZ2xlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgXCJub3RleHRpbGVcIiwgLz09LywgMik7XG4gIGlmIChjaCA9PT0gXCItXCIgJiYgIXN0cmVhbS5lYXQoXCItXCIpKSByZXR1cm4gdG9nZ2xlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgXCJkZWxldGlvblwiLCAvLS8sIDEpO1xuICBpZiAoY2ggPT09IFwiK1wiKSByZXR1cm4gdG9nZ2xlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgXCJhZGRpdGlvblwiLCAvXFwrLywgMSk7XG4gIGlmIChjaCA9PT0gXCJ+XCIpIHJldHVybiB0b2dnbGVQaHJhc2VNb2RpZmllcihzdHJlYW0sIHN0YXRlLCBcInN1YlwiLCAvfi8sIDEpO1xuICBpZiAoY2ggPT09IFwiXlwiKSByZXR1cm4gdG9nZ2xlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgXCJzdXBcIiwgL1xcXi8sIDEpO1xuICBpZiAoY2ggPT09IFwiJVwiKSByZXR1cm4gdG9nZ2xlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgXCJzcGFuXCIsIC8lLywgMSk7XG4gIGlmIChjaCA9PT0gXCJAXCIpIHJldHVybiB0b2dnbGVQaHJhc2VNb2RpZmllcihzdHJlYW0sIHN0YXRlLCBcImNvZGVcIiwgL0AvLCAxKTtcbiAgaWYgKGNoID09PSBcIiFcIikge1xuICAgIHZhciB0eXBlID0gdG9nZ2xlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgXCJpbWFnZVwiLCAvKD86XFwoW15cXCldK1xcKSk/IS8sIDEpO1xuICAgIHN0cmVhbS5tYXRjaCgvXjpcXFMrLyk7IC8vIG9wdGlvbmFsIFVybCBwb3J0aW9uXG4gICAgcmV0dXJuIHR5cGU7XG4gIH1cbiAgcmV0dXJuIHRva2VuU3R5bGVzKHN0YXRlKTtcbn1cbmZ1bmN0aW9uIHRvZ2dsZVBocmFzZU1vZGlmaWVyKHN0cmVhbSwgc3RhdGUsIHBocmFzZU1vZGlmaWVyLCBjbG9zZVJFLCBvcGVuU2l6ZSkge1xuICB2YXIgY2hhckJlZm9yZSA9IHN0cmVhbS5wb3MgPiBvcGVuU2l6ZSA/IHN0cmVhbS5zdHJpbmcuY2hhckF0KHN0cmVhbS5wb3MgLSBvcGVuU2l6ZSAtIDEpIDogbnVsbDtcbiAgdmFyIGNoYXJBZnRlciA9IHN0cmVhbS5wZWVrKCk7XG4gIGlmIChzdGF0ZVtwaHJhc2VNb2RpZmllcl0pIHtcbiAgICBpZiAoKCFjaGFyQWZ0ZXIgfHwgL1xcVy8udGVzdChjaGFyQWZ0ZXIpKSAmJiBjaGFyQmVmb3JlICYmIC9cXFMvLnRlc3QoY2hhckJlZm9yZSkpIHtcbiAgICAgIHZhciB0eXBlID0gdG9rZW5TdHlsZXMoc3RhdGUpO1xuICAgICAgc3RhdGVbcGhyYXNlTW9kaWZpZXJdID0gZmFsc2U7XG4gICAgICByZXR1cm4gdHlwZTtcbiAgICB9XG4gIH0gZWxzZSBpZiAoKCFjaGFyQmVmb3JlIHx8IC9cXFcvLnRlc3QoY2hhckJlZm9yZSkpICYmIGNoYXJBZnRlciAmJiAvXFxTLy50ZXN0KGNoYXJBZnRlcikgJiYgc3RyZWFtLm1hdGNoKG5ldyBSZWdFeHAoXCJeLipcXFxcU1wiICsgY2xvc2VSRS5zb3VyY2UgKyBcIig/OlxcXFxXfCQpXCIpLCBmYWxzZSkpIHtcbiAgICBzdGF0ZVtwaHJhc2VNb2RpZmllcl0gPSB0cnVlO1xuICAgIHN0YXRlLm1vZGUgPSBNb2Rlcy5hdHRyaWJ1dGVzO1xuICB9XG4gIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG59XG47XG5mdW5jdGlvbiB0b2tlblN0eWxlcyhzdGF0ZSkge1xuICB2YXIgZGlzYWJsZWQgPSB0ZXh0aWxlRGlzYWJsZWQoc3RhdGUpO1xuICBpZiAoZGlzYWJsZWQpIHJldHVybiBkaXNhYmxlZDtcbiAgdmFyIHN0eWxlcyA9IFtdO1xuICBpZiAoc3RhdGUubGF5b3V0VHlwZSkgc3R5bGVzLnB1c2goVE9LRU5fU1RZTEVTW3N0YXRlLmxheW91dFR5cGVdKTtcbiAgc3R5bGVzID0gc3R5bGVzLmNvbmNhdChhY3RpdmVTdHlsZXMoc3RhdGUsIFwiYWRkaXRpb25cIiwgXCJib2xkXCIsIFwiY2l0ZVwiLCBcImNvZGVcIiwgXCJkZWxldGlvblwiLCBcImVtXCIsIFwiZm9vdENpdGVcIiwgXCJpbWFnZVwiLCBcIml0YWxpY1wiLCBcImxpbmtcIiwgXCJzcGFuXCIsIFwic3Ryb25nXCIsIFwic3ViXCIsIFwic3VwXCIsIFwidGFibGVcIiwgXCJ0YWJsZUhlYWRpbmdcIikpO1xuICBpZiAoc3RhdGUubGF5b3V0VHlwZSA9PT0gXCJoZWFkZXJcIikgc3R5bGVzLnB1c2goVE9LRU5fU1RZTEVTLmhlYWRlciArIFwiLVwiICsgc3RhdGUuaGVhZGVyKTtcbiAgcmV0dXJuIHN0eWxlcy5sZW5ndGggPyBzdHlsZXMuam9pbihcIiBcIikgOiBudWxsO1xufVxuZnVuY3Rpb24gdGV4dGlsZURpc2FibGVkKHN0YXRlKSB7XG4gIHZhciB0eXBlID0gc3RhdGUubGF5b3V0VHlwZTtcbiAgc3dpdGNoICh0eXBlKSB7XG4gICAgY2FzZSBcIm5vdGV4dGlsZVwiOlxuICAgIGNhc2UgXCJjb2RlXCI6XG4gICAgY2FzZSBcInByZVwiOlxuICAgICAgcmV0dXJuIFRPS0VOX1NUWUxFU1t0eXBlXTtcbiAgICBkZWZhdWx0OlxuICAgICAgaWYgKHN0YXRlLm5vdGV4dGlsZSkgcmV0dXJuIFRPS0VOX1NUWUxFUy5ub3RleHRpbGUgKyAodHlwZSA/IFwiIFwiICsgVE9LRU5fU1RZTEVTW3R5cGVdIDogXCJcIik7XG4gICAgICByZXR1cm4gbnVsbDtcbiAgfVxufVxuZnVuY3Rpb24gYWN0aXZlU3R5bGVzKHN0YXRlKSB7XG4gIHZhciBzdHlsZXMgPSBbXTtcbiAgZm9yICh2YXIgaSA9IDE7IGkgPCBhcmd1bWVudHMubGVuZ3RoOyArK2kpIHtcbiAgICBpZiAoc3RhdGVbYXJndW1lbnRzW2ldXSkgc3R5bGVzLnB1c2goVE9LRU5fU1RZTEVTW2FyZ3VtZW50c1tpXV0pO1xuICB9XG4gIHJldHVybiBzdHlsZXM7XG59XG5mdW5jdGlvbiBibGFua0xpbmUoc3RhdGUpIHtcbiAgdmFyIHNwYW5uaW5nTGF5b3V0ID0gc3RhdGUuc3Bhbm5pbmdMYXlvdXQsXG4gICAgdHlwZSA9IHN0YXRlLmxheW91dFR5cGU7XG4gIGZvciAodmFyIGtleSBpbiBzdGF0ZSkgaWYgKHN0YXRlLmhhc093blByb3BlcnR5KGtleSkpIGRlbGV0ZSBzdGF0ZVtrZXldO1xuICBzdGF0ZS5tb2RlID0gTW9kZXMubmV3TGF5b3V0O1xuICBpZiAoc3Bhbm5pbmdMYXlvdXQpIHtcbiAgICBzdGF0ZS5sYXlvdXRUeXBlID0gdHlwZTtcbiAgICBzdGF0ZS5zcGFubmluZ0xheW91dCA9IHRydWU7XG4gIH1cbn1cbnZhciBSRXMgPSB7XG4gIGNhY2hlOiB7fSxcbiAgc2luZ2xlOiB7XG4gICAgYmM6IFwiYmNcIixcbiAgICBicTogXCJicVwiLFxuICAgIGRlZmluaXRpb25MaXN0OiAvLSAuKj86PSsvLFxuICAgIGRlZmluaXRpb25MaXN0RW5kOiAvLio9OlxccyokLyxcbiAgICBkaXY6IFwiZGl2XCIsXG4gICAgZHJhd1RhYmxlOiAvXFx8LipcXHwvLFxuICAgIGZvb3Q6IC9mblxcZCsvLFxuICAgIGhlYWRlcjogL2hbMS02XS8sXG4gICAgaHRtbDogL1xccyo8KD86XFwvKT8oXFx3KykoPzpbXj5dKyk/Pig/OltePF0rPFxcL1xcMT4pPy8sXG4gICAgbGluazogL1teXCJdK1wiOlxcUy8sXG4gICAgbGlua0RlZmluaXRpb246IC9cXFtbXlxcc1xcXV0rXFxdXFxTKy8sXG4gICAgbGlzdDogLyg/OiMrfFxcKispLyxcbiAgICBub3RleHRpbGU6IFwibm90ZXh0aWxlXCIsXG4gICAgcGFyYTogXCJwXCIsXG4gICAgcHJlOiBcInByZVwiLFxuICAgIHRhYmxlOiBcInRhYmxlXCIsXG4gICAgdGFibGVDZWxsQXR0cmlidXRlczogL1tcXC9cXFxcXVxcZCsvLFxuICAgIHRhYmxlSGVhZGluZzogL1xcfF9cXC4vLFxuICAgIHRhYmxlVGV4dDogL1teXCJfXFwqXFxbXFwoXFw/XFwrflxcXiVAfC1dKy8sXG4gICAgdGV4dDogL1teIVwiXz1cXCpcXFtcXCg8XFw/XFwrflxcXiVALV0rL1xuICB9LFxuICBhdHRyaWJ1dGVzOiB7XG4gICAgYWxpZ246IC8oPzo8Pnw8fD58PSkvLFxuICAgIHNlbGVjdG9yOiAvXFwoW15cXChdW15cXCldK1xcKS8sXG4gICAgbGFuZzogL1xcW1teXFxbXFxdXStcXF0vLFxuICAgIHBhZDogLyg/OlxcKCt8XFwpKyl7MSwyfS8sXG4gICAgY3NzOiAvXFx7W15cXH1dK1xcfS9cbiAgfSxcbiAgY3JlYXRlUmU6IGZ1bmN0aW9uIChuYW1lKSB7XG4gICAgc3dpdGNoIChuYW1lKSB7XG4gICAgICBjYXNlIFwiZHJhd1RhYmxlXCI6XG4gICAgICAgIHJldHVybiBSRXMubWFrZVJlKFwiXlwiLCBSRXMuc2luZ2xlLmRyYXdUYWJsZSwgXCIkXCIpO1xuICAgICAgY2FzZSBcImh0bWxcIjpcbiAgICAgICAgcmV0dXJuIFJFcy5tYWtlUmUoXCJeXCIsIFJFcy5zaW5nbGUuaHRtbCwgXCIoPzpcIiwgUkVzLnNpbmdsZS5odG1sLCBcIikqXCIsIFwiJFwiKTtcbiAgICAgIGNhc2UgXCJsaW5rRGVmaW5pdGlvblwiOlxuICAgICAgICByZXR1cm4gUkVzLm1ha2VSZShcIl5cIiwgUkVzLnNpbmdsZS5saW5rRGVmaW5pdGlvbiwgXCIkXCIpO1xuICAgICAgY2FzZSBcImxpc3RMYXlvdXRcIjpcbiAgICAgICAgcmV0dXJuIFJFcy5tYWtlUmUoXCJeXCIsIFJFcy5zaW5nbGUubGlzdCwgUkUoXCJhbGxBdHRyaWJ1dGVzXCIpLCBcIipcXFxccytcIik7XG4gICAgICBjYXNlIFwidGFibGVDZWxsQXR0cmlidXRlc1wiOlxuICAgICAgICByZXR1cm4gUkVzLm1ha2VSZShcIl5cIiwgUkVzLmNob2ljZVJlKFJFcy5zaW5nbGUudGFibGVDZWxsQXR0cmlidXRlcywgUkUoXCJhbGxBdHRyaWJ1dGVzXCIpKSwgXCIrXFxcXC5cIik7XG4gICAgICBjYXNlIFwidHlwZVwiOlxuICAgICAgICByZXR1cm4gUkVzLm1ha2VSZShcIl5cIiwgUkUoXCJhbGxUeXBlc1wiKSk7XG4gICAgICBjYXNlIFwidHlwZUxheW91dFwiOlxuICAgICAgICByZXR1cm4gUkVzLm1ha2VSZShcIl5cIiwgUkUoXCJhbGxUeXBlc1wiKSwgUkUoXCJhbGxBdHRyaWJ1dGVzXCIpLCBcIipcXFxcLlxcXFwuP1wiLCBcIihcXFxccyt8JClcIik7XG4gICAgICBjYXNlIFwiYXR0cmlidXRlc1wiOlxuICAgICAgICByZXR1cm4gUkVzLm1ha2VSZShcIl5cIiwgUkUoXCJhbGxBdHRyaWJ1dGVzXCIpLCBcIitcIik7XG4gICAgICBjYXNlIFwiYWxsVHlwZXNcIjpcbiAgICAgICAgcmV0dXJuIFJFcy5jaG9pY2VSZShSRXMuc2luZ2xlLmRpdiwgUkVzLnNpbmdsZS5mb290LCBSRXMuc2luZ2xlLmhlYWRlciwgUkVzLnNpbmdsZS5iYywgUkVzLnNpbmdsZS5icSwgUkVzLnNpbmdsZS5ub3RleHRpbGUsIFJFcy5zaW5nbGUucHJlLCBSRXMuc2luZ2xlLnRhYmxlLCBSRXMuc2luZ2xlLnBhcmEpO1xuICAgICAgY2FzZSBcImFsbEF0dHJpYnV0ZXNcIjpcbiAgICAgICAgcmV0dXJuIFJFcy5jaG9pY2VSZShSRXMuYXR0cmlidXRlcy5zZWxlY3RvciwgUkVzLmF0dHJpYnV0ZXMuY3NzLCBSRXMuYXR0cmlidXRlcy5sYW5nLCBSRXMuYXR0cmlidXRlcy5hbGlnbiwgUkVzLmF0dHJpYnV0ZXMucGFkKTtcbiAgICAgIGRlZmF1bHQ6XG4gICAgICAgIHJldHVybiBSRXMubWFrZVJlKFwiXlwiLCBSRXMuc2luZ2xlW25hbWVdKTtcbiAgICB9XG4gIH0sXG4gIG1ha2VSZTogZnVuY3Rpb24gKCkge1xuICAgIHZhciBwYXR0ZXJuID0gXCJcIjtcbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IGFyZ3VtZW50cy5sZW5ndGg7ICsraSkge1xuICAgICAgdmFyIGFyZyA9IGFyZ3VtZW50c1tpXTtcbiAgICAgIHBhdHRlcm4gKz0gdHlwZW9mIGFyZyA9PT0gXCJzdHJpbmdcIiA/IGFyZyA6IGFyZy5zb3VyY2U7XG4gICAgfVxuICAgIHJldHVybiBuZXcgUmVnRXhwKHBhdHRlcm4pO1xuICB9LFxuICBjaG9pY2VSZTogZnVuY3Rpb24gKCkge1xuICAgIHZhciBwYXJ0cyA9IFthcmd1bWVudHNbMF1dO1xuICAgIGZvciAodmFyIGkgPSAxOyBpIDwgYXJndW1lbnRzLmxlbmd0aDsgKytpKSB7XG4gICAgICBwYXJ0c1tpICogMiAtIDFdID0gXCJ8XCI7XG4gICAgICBwYXJ0c1tpICogMl0gPSBhcmd1bWVudHNbaV07XG4gICAgfVxuICAgIHBhcnRzLnVuc2hpZnQoXCIoPzpcIik7XG4gICAgcGFydHMucHVzaChcIilcIik7XG4gICAgcmV0dXJuIFJFcy5tYWtlUmUuYXBwbHkobnVsbCwgcGFydHMpO1xuICB9XG59O1xuZnVuY3Rpb24gUkUobmFtZSkge1xuICByZXR1cm4gUkVzLmNhY2hlW25hbWVdIHx8IChSRXMuY2FjaGVbbmFtZV0gPSBSRXMuY3JlYXRlUmUobmFtZSkpO1xufVxudmFyIE1vZGVzID0ge1xuICBuZXdMYXlvdXQ6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChSRShcInR5cGVMYXlvdXRcIiksIGZhbHNlKSkge1xuICAgICAgc3RhdGUuc3Bhbm5pbmdMYXlvdXQgPSBmYWxzZTtcbiAgICAgIHJldHVybiAoc3RhdGUubW9kZSA9IE1vZGVzLmJsb2NrVHlwZSkoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICAgIHZhciBuZXdNb2RlO1xuICAgIGlmICghdGV4dGlsZURpc2FibGVkKHN0YXRlKSkge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaChSRShcImxpc3RMYXlvdXRcIiksIGZhbHNlKSkgbmV3TW9kZSA9IE1vZGVzLmxpc3Q7ZWxzZSBpZiAoc3RyZWFtLm1hdGNoKFJFKFwiZHJhd1RhYmxlXCIpLCBmYWxzZSkpIG5ld01vZGUgPSBNb2Rlcy50YWJsZTtlbHNlIGlmIChzdHJlYW0ubWF0Y2goUkUoXCJsaW5rRGVmaW5pdGlvblwiKSwgZmFsc2UpKSBuZXdNb2RlID0gTW9kZXMubGlua0RlZmluaXRpb247ZWxzZSBpZiAoc3RyZWFtLm1hdGNoKFJFKFwiZGVmaW5pdGlvbkxpc3RcIikpKSBuZXdNb2RlID0gTW9kZXMuZGVmaW5pdGlvbkxpc3Q7ZWxzZSBpZiAoc3RyZWFtLm1hdGNoKFJFKFwiaHRtbFwiKSwgZmFsc2UpKSBuZXdNb2RlID0gTW9kZXMuaHRtbDtcbiAgICB9XG4gICAgcmV0dXJuIChzdGF0ZS5tb2RlID0gbmV3TW9kZSB8fCBNb2Rlcy50ZXh0KShzdHJlYW0sIHN0YXRlKTtcbiAgfSxcbiAgYmxvY2tUeXBlOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBtYXRjaCwgdHlwZTtcbiAgICBzdGF0ZS5sYXlvdXRUeXBlID0gbnVsbDtcbiAgICBpZiAobWF0Y2ggPSBzdHJlYW0ubWF0Y2goUkUoXCJ0eXBlXCIpKSkgdHlwZSA9IG1hdGNoWzBdO2Vsc2UgcmV0dXJuIChzdGF0ZS5tb2RlID0gTW9kZXMudGV4dCkoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKG1hdGNoID0gdHlwZS5tYXRjaChSRShcImhlYWRlclwiKSkpIHtcbiAgICAgIHN0YXRlLmxheW91dFR5cGUgPSBcImhlYWRlclwiO1xuICAgICAgc3RhdGUuaGVhZGVyID0gcGFyc2VJbnQobWF0Y2hbMF1bMV0pO1xuICAgIH0gZWxzZSBpZiAodHlwZS5tYXRjaChSRShcImJxXCIpKSkge1xuICAgICAgc3RhdGUubGF5b3V0VHlwZSA9IFwicXVvdGVcIjtcbiAgICB9IGVsc2UgaWYgKHR5cGUubWF0Y2goUkUoXCJiY1wiKSkpIHtcbiAgICAgIHN0YXRlLmxheW91dFR5cGUgPSBcImNvZGVcIjtcbiAgICB9IGVsc2UgaWYgKHR5cGUubWF0Y2goUkUoXCJmb290XCIpKSkge1xuICAgICAgc3RhdGUubGF5b3V0VHlwZSA9IFwiZm9vdG5vdGVcIjtcbiAgICB9IGVsc2UgaWYgKHR5cGUubWF0Y2goUkUoXCJub3RleHRpbGVcIikpKSB7XG4gICAgICBzdGF0ZS5sYXlvdXRUeXBlID0gXCJub3RleHRpbGVcIjtcbiAgICB9IGVsc2UgaWYgKHR5cGUubWF0Y2goUkUoXCJwcmVcIikpKSB7XG4gICAgICBzdGF0ZS5sYXlvdXRUeXBlID0gXCJwcmVcIjtcbiAgICB9IGVsc2UgaWYgKHR5cGUubWF0Y2goUkUoXCJkaXZcIikpKSB7XG4gICAgICBzdGF0ZS5sYXlvdXRUeXBlID0gXCJkaXZcIjtcbiAgICB9IGVsc2UgaWYgKHR5cGUubWF0Y2goUkUoXCJ0YWJsZVwiKSkpIHtcbiAgICAgIHN0YXRlLmxheW91dFR5cGUgPSBcInRhYmxlXCI7XG4gICAgfVxuICAgIHN0YXRlLm1vZGUgPSBNb2Rlcy5hdHRyaWJ1dGVzO1xuICAgIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG4gIH0sXG4gIHRleHQ6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChSRShcInRleHRcIikpKSByZXR1cm4gdG9rZW5TdHlsZXMoc3RhdGUpO1xuICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgaWYgKGNoID09PSAnXCInKSByZXR1cm4gKHN0YXRlLm1vZGUgPSBNb2Rlcy5saW5rKShzdHJlYW0sIHN0YXRlKTtcbiAgICByZXR1cm4gaGFuZGxlUGhyYXNlTW9kaWZpZXIoc3RyZWFtLCBzdGF0ZSwgY2gpO1xuICB9LFxuICBhdHRyaWJ1dGVzOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHN0YXRlLm1vZGUgPSBNb2Rlcy5sYXlvdXRMZW5ndGg7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChSRShcImF0dHJpYnV0ZXNcIikpKSByZXR1cm4gVE9LRU5fU1RZTEVTLmF0dHJpYnV0ZXM7ZWxzZSByZXR1cm4gdG9rZW5TdHlsZXMoc3RhdGUpO1xuICB9LFxuICBsYXlvdXRMZW5ndGg6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCIuXCIpICYmIHN0cmVhbS5lYXQoXCIuXCIpKSBzdGF0ZS5zcGFubmluZ0xheW91dCA9IHRydWU7XG4gICAgc3RhdGUubW9kZSA9IE1vZGVzLnRleHQ7XG4gICAgcmV0dXJuIHRva2VuU3R5bGVzKHN0YXRlKTtcbiAgfSxcbiAgbGlzdDogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgbWF0Y2ggPSBzdHJlYW0ubWF0Y2goUkUoXCJsaXN0XCIpKTtcbiAgICBzdGF0ZS5saXN0RGVwdGggPSBtYXRjaFswXS5sZW5ndGg7XG4gICAgdmFyIGxpc3RNb2QgPSAoc3RhdGUubGlzdERlcHRoIC0gMSkgJSAzO1xuICAgIGlmICghbGlzdE1vZCkgc3RhdGUubGF5b3V0VHlwZSA9IFwibGlzdDFcIjtlbHNlIGlmIChsaXN0TW9kID09PSAxKSBzdGF0ZS5sYXlvdXRUeXBlID0gXCJsaXN0MlwiO2Vsc2Ugc3RhdGUubGF5b3V0VHlwZSA9IFwibGlzdDNcIjtcbiAgICBzdGF0ZS5tb2RlID0gTW9kZXMuYXR0cmlidXRlcztcbiAgICByZXR1cm4gdG9rZW5TdHlsZXMoc3RhdGUpO1xuICB9LFxuICBsaW5rOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHN0YXRlLm1vZGUgPSBNb2Rlcy50ZXh0O1xuICAgIGlmIChzdHJlYW0ubWF0Y2goUkUoXCJsaW5rXCIpKSkge1xuICAgICAgc3RyZWFtLm1hdGNoKC9cXFMrLyk7XG4gICAgICByZXR1cm4gVE9LRU5fU1RZTEVTLmxpbms7XG4gICAgfVxuICAgIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG4gIH0sXG4gIGxpbmtEZWZpbml0aW9uOiBmdW5jdGlvbiAoc3RyZWFtKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBUT0tFTl9TVFlMRVMubGlua0RlZmluaXRpb247XG4gIH0sXG4gIGRlZmluaXRpb25MaXN0OiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHN0cmVhbS5tYXRjaChSRShcImRlZmluaXRpb25MaXN0XCIpKTtcbiAgICBzdGF0ZS5sYXlvdXRUeXBlID0gXCJkZWZpbml0aW9uTGlzdFwiO1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL1xccyokLykpIHN0YXRlLnNwYW5uaW5nTGF5b3V0ID0gdHJ1ZTtlbHNlIHN0YXRlLm1vZGUgPSBNb2Rlcy5hdHRyaWJ1dGVzO1xuICAgIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG4gIH0sXG4gIGh0bWw6IGZ1bmN0aW9uIChzdHJlYW0pIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFRPS0VOX1NUWUxFUy5odG1sO1xuICB9LFxuICB0YWJsZTogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBzdGF0ZS5sYXlvdXRUeXBlID0gXCJ0YWJsZVwiO1xuICAgIHJldHVybiAoc3RhdGUubW9kZSA9IE1vZGVzLnRhYmxlQ2VsbCkoc3RyZWFtLCBzdGF0ZSk7XG4gIH0sXG4gIHRhYmxlQ2VsbDogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKFJFKFwidGFibGVIZWFkaW5nXCIpKSkgc3RhdGUudGFibGVIZWFkaW5nID0gdHJ1ZTtlbHNlIHN0cmVhbS5lYXQoXCJ8XCIpO1xuICAgIHN0YXRlLm1vZGUgPSBNb2Rlcy50YWJsZUNlbGxBdHRyaWJ1dGVzO1xuICAgIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG4gIH0sXG4gIHRhYmxlQ2VsbEF0dHJpYnV0ZXM6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgc3RhdGUubW9kZSA9IE1vZGVzLnRhYmxlVGV4dDtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKFJFKFwidGFibGVDZWxsQXR0cmlidXRlc1wiKSkpIHJldHVybiBUT0tFTl9TVFlMRVMuYXR0cmlidXRlcztlbHNlIHJldHVybiB0b2tlblN0eWxlcyhzdGF0ZSk7XG4gIH0sXG4gIHRhYmxlVGV4dDogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKFJFKFwidGFibGVUZXh0XCIpKSkgcmV0dXJuIHRva2VuU3R5bGVzKHN0YXRlKTtcbiAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gXCJ8XCIpIHtcbiAgICAgIC8vIGVuZCBvZiBjZWxsXG4gICAgICBzdGF0ZS5tb2RlID0gTW9kZXMudGFibGVDZWxsO1xuICAgICAgcmV0dXJuIHRva2VuU3R5bGVzKHN0YXRlKTtcbiAgICB9XG4gICAgcmV0dXJuIGhhbmRsZVBocmFzZU1vZGlmaWVyKHN0cmVhbSwgc3RhdGUsIHN0cmVhbS5uZXh0KCkpO1xuICB9XG59O1xuZXhwb3J0IGNvbnN0IHRleHRpbGUgPSB7XG4gIG5hbWU6IFwidGV4dGlsZVwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIG1vZGU6IE1vZGVzLm5ld0xheW91dFxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHN0YXJ0TmV3TGluZShzdHJlYW0sIHN0YXRlKTtcbiAgICByZXR1cm4gc3RhdGUubW9kZShzdHJlYW0sIHN0YXRlKTtcbiAgfSxcbiAgYmxhbmtMaW5lOiBibGFua0xpbmVcbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==