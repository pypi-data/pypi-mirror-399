"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2982],{

/***/ 12982
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   d: () => (/* binding */ d)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var blockKeywordsStr = "body catch class do else enum for foreach foreach_reverse if in interface mixin " + "out scope struct switch try union unittest version while with";
const parserConfig = {
  keywords: words("abstract alias align asm assert auto break case cast cdouble cent cfloat const continue " + "debug default delegate delete deprecated export extern final finally function goto immutable " + "import inout invariant is lazy macro module new nothrow override package pragma private " + "protected public pure ref return shared short static super synchronized template this " + "throw typedef typeid typeof volatile __FILE__ __LINE__ __gshared __traits __vector __parameters " + blockKeywordsStr),
  blockKeywords: words(blockKeywordsStr),
  builtin: words("bool byte char creal dchar double float idouble ifloat int ireal long real short ubyte " + "ucent uint ulong ushort wchar wstring void size_t sizediff_t"),
  atoms: words("exit failure success true false null"),
  hooks: {
    "@": function (stream, _state) {
      stream.eatWhile(/[\w\$_]/);
      return "meta";
    }
  }
};
var statementIndentUnit = parserConfig.statementIndentUnit,
  keywords = parserConfig.keywords,
  builtin = parserConfig.builtin,
  blockKeywords = parserConfig.blockKeywords,
  atoms = parserConfig.atoms,
  hooks = parserConfig.hooks,
  multiLineStrings = parserConfig.multiLineStrings;
var isOperatorChar = /[+\-*&%=<>!?|\/]/;
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (hooks[ch]) {
    var result = hooks[ch](stream, state);
    if (result !== false) return result;
  }
  if (ch == '"' || ch == "'" || ch == "`") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
    curPunc = ch;
    return null;
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  if (ch == "/") {
    if (stream.eat("+")) {
      state.tokenize = tokenNestedComment;
      return tokenNestedComment(stream, state);
    }
    if (stream.eat("*")) {
      state.tokenize = tokenComment;
      return tokenComment(stream, state);
    }
    if (stream.eat("/")) {
      stream.skipToEnd();
      return "comment";
    }
  }
  if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  stream.eatWhile(/[\w\$_\xa1-\uffff]/);
  var cur = stream.current();
  if (keywords.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "keyword";
  }
  if (builtin.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "builtin";
  }
  if (atoms.propertyIsEnumerable(cur)) return "atom";
  return "variable";
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        end = true;
        break;
      }
      escaped = !escaped && next == "\\";
    }
    if (end || !(escaped || multiLineStrings)) state.tokenize = null;
    return "string";
  };
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = null;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function tokenNestedComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = null;
      break;
    }
    maybeEnd = ch == "+";
  }
  return "comment";
}
function Context(indented, column, type, align, prev) {
  this.indented = indented;
  this.column = column;
  this.type = type;
  this.align = align;
  this.prev = prev;
}
function pushContext(state, col, type) {
  var indent = state.indented;
  if (state.context && state.context.type == "statement") indent = state.context.indented;
  return state.context = new Context(indent, col, type, null, state.context);
}
function popContext(state) {
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

// Interface

const d = {
  name: "d",
  startState: function (indentUnit) {
    return {
      tokenize: null,
      context: new Context(-indentUnit, 0, "top", false),
      indented: 0,
      startOfLine: true
    };
  },
  token: function (stream, state) {
    var ctx = state.context;
    if (stream.sol()) {
      if (ctx.align == null) ctx.align = false;
      state.indented = stream.indentation();
      state.startOfLine = true;
    }
    if (stream.eatSpace()) return null;
    curPunc = null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment" || style == "meta") return style;
    if (ctx.align == null) ctx.align = true;
    if ((curPunc == ";" || curPunc == ":" || curPunc == ",") && ctx.type == "statement") popContext(state);else if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "}") {
      while (ctx.type == "statement") ctx = popContext(state);
      if (ctx.type == "}") ctx = popContext(state);
      while (ctx.type == "statement") ctx = popContext(state);
    } else if (curPunc == ctx.type) popContext(state);else if ((ctx.type == "}" || ctx.type == "top") && curPunc != ';' || ctx.type == "statement" && curPunc == "newstatement") pushContext(state, stream.column(), "statement");
    state.startOfLine = false;
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != tokenBase && state.tokenize != null) return null;
    var ctx = state.context,
      firstChar = textAfter && textAfter.charAt(0);
    if (ctx.type == "statement" && firstChar == "}") ctx = ctx.prev;
    var closing = firstChar == ctx.type;
    if (ctx.type == "statement") return ctx.indented + (firstChar == "{" ? 0 : statementIndentUnit || cx.unit);else if (ctx.align) return ctx.column + (closing ? 0 : 1);else return ctx.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjk4Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2QuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZHMoc3RyKSB7XG4gIHZhciBvYmogPSB7fSxcbiAgICB3b3JkcyA9IHN0ci5zcGxpdChcIiBcIik7XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgd29yZHMubGVuZ3RoOyArK2kpIG9ialt3b3Jkc1tpXV0gPSB0cnVlO1xuICByZXR1cm4gb2JqO1xufVxudmFyIGJsb2NrS2V5d29yZHNTdHIgPSBcImJvZHkgY2F0Y2ggY2xhc3MgZG8gZWxzZSBlbnVtIGZvciBmb3JlYWNoIGZvcmVhY2hfcmV2ZXJzZSBpZiBpbiBpbnRlcmZhY2UgbWl4aW4gXCIgKyBcIm91dCBzY29wZSBzdHJ1Y3Qgc3dpdGNoIHRyeSB1bmlvbiB1bml0dGVzdCB2ZXJzaW9uIHdoaWxlIHdpdGhcIjtcbmNvbnN0IHBhcnNlckNvbmZpZyA9IHtcbiAga2V5d29yZHM6IHdvcmRzKFwiYWJzdHJhY3QgYWxpYXMgYWxpZ24gYXNtIGFzc2VydCBhdXRvIGJyZWFrIGNhc2UgY2FzdCBjZG91YmxlIGNlbnQgY2Zsb2F0IGNvbnN0IGNvbnRpbnVlIFwiICsgXCJkZWJ1ZyBkZWZhdWx0IGRlbGVnYXRlIGRlbGV0ZSBkZXByZWNhdGVkIGV4cG9ydCBleHRlcm4gZmluYWwgZmluYWxseSBmdW5jdGlvbiBnb3RvIGltbXV0YWJsZSBcIiArIFwiaW1wb3J0IGlub3V0IGludmFyaWFudCBpcyBsYXp5IG1hY3JvIG1vZHVsZSBuZXcgbm90aHJvdyBvdmVycmlkZSBwYWNrYWdlIHByYWdtYSBwcml2YXRlIFwiICsgXCJwcm90ZWN0ZWQgcHVibGljIHB1cmUgcmVmIHJldHVybiBzaGFyZWQgc2hvcnQgc3RhdGljIHN1cGVyIHN5bmNocm9uaXplZCB0ZW1wbGF0ZSB0aGlzIFwiICsgXCJ0aHJvdyB0eXBlZGVmIHR5cGVpZCB0eXBlb2Ygdm9sYXRpbGUgX19GSUxFX18gX19MSU5FX18gX19nc2hhcmVkIF9fdHJhaXRzIF9fdmVjdG9yIF9fcGFyYW1ldGVycyBcIiArIGJsb2NrS2V5d29yZHNTdHIpLFxuICBibG9ja0tleXdvcmRzOiB3b3JkcyhibG9ja0tleXdvcmRzU3RyKSxcbiAgYnVpbHRpbjogd29yZHMoXCJib29sIGJ5dGUgY2hhciBjcmVhbCBkY2hhciBkb3VibGUgZmxvYXQgaWRvdWJsZSBpZmxvYXQgaW50IGlyZWFsIGxvbmcgcmVhbCBzaG9ydCB1Ynl0ZSBcIiArIFwidWNlbnQgdWludCB1bG9uZyB1c2hvcnQgd2NoYXIgd3N0cmluZyB2b2lkIHNpemVfdCBzaXplZGlmZl90XCIpLFxuICBhdG9tczogd29yZHMoXCJleGl0IGZhaWx1cmUgc3VjY2VzcyB0cnVlIGZhbHNlIG51bGxcIiksXG4gIGhvb2tzOiB7XG4gICAgXCJAXCI6IGZ1bmN0aW9uIChzdHJlYW0sIF9zdGF0ZSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9XG4gIH1cbn07XG52YXIgc3RhdGVtZW50SW5kZW50VW5pdCA9IHBhcnNlckNvbmZpZy5zdGF0ZW1lbnRJbmRlbnRVbml0LFxuICBrZXl3b3JkcyA9IHBhcnNlckNvbmZpZy5rZXl3b3JkcyxcbiAgYnVpbHRpbiA9IHBhcnNlckNvbmZpZy5idWlsdGluLFxuICBibG9ja0tleXdvcmRzID0gcGFyc2VyQ29uZmlnLmJsb2NrS2V5d29yZHMsXG4gIGF0b21zID0gcGFyc2VyQ29uZmlnLmF0b21zLFxuICBob29rcyA9IHBhcnNlckNvbmZpZy5ob29rcyxcbiAgbXVsdGlMaW5lU3RyaW5ncyA9IHBhcnNlckNvbmZpZy5tdWx0aUxpbmVTdHJpbmdzO1xudmFyIGlzT3BlcmF0b3JDaGFyID0gL1srXFwtKiYlPTw+IT98XFwvXS87XG52YXIgY3VyUHVuYztcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChob29rc1tjaF0pIHtcbiAgICB2YXIgcmVzdWx0ID0gaG9va3NbY2hdKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChyZXN1bHQgIT09IGZhbHNlKSByZXR1cm4gcmVzdWx0O1xuICB9XG4gIGlmIChjaCA9PSAnXCInIHx8IGNoID09IFwiJ1wiIHx8IGNoID09IFwiYFwiKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmICgvW1xcW1xcXXt9XFwoXFwpLDtcXDpcXC5dLy50ZXN0KGNoKSkge1xuICAgIGN1clB1bmMgPSBjaDtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXC5dLyk7XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgaWYgKGNoID09IFwiL1wiKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCIrXCIpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuTmVzdGVkQ29tbWVudDtcbiAgICAgIHJldHVybiB0b2tlbk5lc3RlZENvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnQ7XG4gICAgICByZXR1cm4gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gIH1cbiAgaWYgKGlzT3BlcmF0b3JDaGFyLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKGlzT3BlcmF0b3JDaGFyKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF9cXHhhMS1cXHVmZmZmXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHtcbiAgICBpZiAoYmxvY2tLZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSBjdXJQdW5jID0gXCJuZXdzdGF0ZW1lbnRcIjtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cbiAgaWYgKGJ1aWx0aW4ucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkge1xuICAgIGlmIChibG9ja0tleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIGN1clB1bmMgPSBcIm5ld3N0YXRlbWVudFwiO1xuICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgfVxuICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQsXG4gICAgICBlbmQgPSBmYWxzZTtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoZW5kIHx8ICEoZXNjYXBlZCB8fCBtdWx0aUxpbmVTdHJpbmdzKSkgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIvXCIgJiYgbWF5YmVFbmQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cbmZ1bmN0aW9uIHRva2VuTmVzdGVkQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiL1wiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbWF5YmVFbmQgPSBjaCA9PSBcIitcIjtcbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5mdW5jdGlvbiBDb250ZXh0KGluZGVudGVkLCBjb2x1bW4sIHR5cGUsIGFsaWduLCBwcmV2KSB7XG4gIHRoaXMuaW5kZW50ZWQgPSBpbmRlbnRlZDtcbiAgdGhpcy5jb2x1bW4gPSBjb2x1bW47XG4gIHRoaXMudHlwZSA9IHR5cGU7XG4gIHRoaXMuYWxpZ24gPSBhbGlnbjtcbiAgdGhpcy5wcmV2ID0gcHJldjtcbn1cbmZ1bmN0aW9uIHB1c2hDb250ZXh0KHN0YXRlLCBjb2wsIHR5cGUpIHtcbiAgdmFyIGluZGVudCA9IHN0YXRlLmluZGVudGVkO1xuICBpZiAoc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgaW5kZW50ID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBuZXcgQ29udGV4dChpbmRlbnQsIGNvbCwgdHlwZSwgbnVsbCwgc3RhdGUuY29udGV4dCk7XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KHN0YXRlKSB7XG4gIHZhciB0ID0gc3RhdGUuY29udGV4dC50eXBlO1xuICBpZiAodCA9PSBcIilcIiB8fCB0ID09IFwiXVwiIHx8IHQgPT0gXCJ9XCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG59XG5cbi8vIEludGVyZmFjZVxuXG5leHBvcnQgY29uc3QgZCA9IHtcbiAgbmFtZTogXCJkXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uIChpbmRlbnRVbml0KSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBudWxsLFxuICAgICAgY29udGV4dDogbmV3IENvbnRleHQoLWluZGVudFVuaXQsIDAsIFwidG9wXCIsIGZhbHNlKSxcbiAgICAgIGluZGVudGVkOiAwLFxuICAgICAgc3RhcnRPZkxpbmU6IHRydWVcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY3R4ID0gc3RhdGUuY29udGV4dDtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBpZiAoY3R4LmFsaWduID09IG51bGwpIGN0eC5hbGlnbiA9IGZhbHNlO1xuICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gdHJ1ZTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICBjdXJQdW5jID0gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSAoc3RhdGUudG9rZW5pemUgfHwgdG9rZW5CYXNlKShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3R5bGUgPT0gXCJjb21tZW50XCIgfHwgc3R5bGUgPT0gXCJtZXRhXCIpIHJldHVybiBzdHlsZTtcbiAgICBpZiAoY3R4LmFsaWduID09IG51bGwpIGN0eC5hbGlnbiA9IHRydWU7XG4gICAgaWYgKChjdXJQdW5jID09IFwiO1wiIHx8IGN1clB1bmMgPT0gXCI6XCIgfHwgY3VyUHVuYyA9PSBcIixcIikgJiYgY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIntcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJ9XCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJbXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiXVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwiKFwiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIilcIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIn1cIikge1xuICAgICAgd2hpbGUgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIGN0eCA9IHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgaWYgKGN0eC50eXBlID09IFwifVwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICB9IGVsc2UgaWYgKGN1clB1bmMgPT0gY3R4LnR5cGUpIHBvcENvbnRleHQoc3RhdGUpO2Vsc2UgaWYgKChjdHgudHlwZSA9PSBcIn1cIiB8fCBjdHgudHlwZSA9PSBcInRvcFwiKSAmJiBjdXJQdW5jICE9ICc7JyB8fCBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmIGN1clB1bmMgPT0gXCJuZXdzdGF0ZW1lbnRcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJzdGF0ZW1lbnRcIik7XG4gICAgc3RhdGUuc3RhcnRPZkxpbmUgPSBmYWxzZTtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgaWYgKHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSAmJiBzdGF0ZS50b2tlbml6ZSAhPSBudWxsKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgY3R4ID0gc3RhdGUuY29udGV4dCxcbiAgICAgIGZpcnN0Q2hhciA9IHRleHRBZnRlciAmJiB0ZXh0QWZ0ZXIuY2hhckF0KDApO1xuICAgIGlmIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmIGZpcnN0Q2hhciA9PSBcIn1cIikgY3R4ID0gY3R4LnByZXY7XG4gICAgdmFyIGNsb3NpbmcgPSBmaXJzdENoYXIgPT0gY3R4LnR5cGU7XG4gICAgaWYgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIHJldHVybiBjdHguaW5kZW50ZWQgKyAoZmlyc3RDaGFyID09IFwie1wiID8gMCA6IHN0YXRlbWVudEluZGVudFVuaXQgfHwgY3gudW5pdCk7ZWxzZSBpZiAoY3R4LmFsaWduKSByZXR1cm4gY3R4LmNvbHVtbiArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChjbG9zaW5nID8gMCA6IGN4LnVuaXQpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypbe31dJC8sXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIvL1wiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=