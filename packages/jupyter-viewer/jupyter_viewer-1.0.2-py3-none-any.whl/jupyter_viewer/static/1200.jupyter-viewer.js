"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1200],{

/***/ 61200
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   r: () => (/* binding */ r)
/* harmony export */ });
function wordObj(words) {
  var res = {};
  for (var i = 0; i < words.length; ++i) res[words[i]] = true;
  return res;
}
var commonAtoms = ["NULL", "NA", "Inf", "NaN", "NA_integer_", "NA_real_", "NA_complex_", "NA_character_", "TRUE", "FALSE"];
var commonBuiltins = ["list", "quote", "bquote", "eval", "return", "call", "parse", "deparse"];
var commonKeywords = ["if", "else", "repeat", "while", "function", "for", "in", "next", "break"];
var commonBlockKeywords = ["if", "else", "repeat", "while", "function", "for"];
var atoms = wordObj(commonAtoms);
var builtins = wordObj(commonBuiltins);
var keywords = wordObj(commonKeywords);
var blockkeywords = wordObj(commonBlockKeywords);
var opChars = /[+\-*\/^<>=!&|~$:]/;
var curPunc;
function tokenBase(stream, state) {
  curPunc = null;
  var ch = stream.next();
  if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  } else if (ch == "0" && stream.eat("x")) {
    stream.eatWhile(/[\da-f]/i);
    return "number";
  } else if (ch == "." && stream.eat(/\d/)) {
    stream.match(/\d*(?:e[+\-]?\d+)?/);
    return "number";
  } else if (/\d/.test(ch)) {
    stream.match(/\d*(?:\.\d+)?(?:e[+\-]\d+)?L?/);
    return "number";
  } else if (ch == "'" || ch == '"') {
    state.tokenize = tokenString(ch);
    return "string";
  } else if (ch == "`") {
    stream.match(/[^`]+`/);
    return "string.special";
  } else if (ch == "." && stream.match(/.(?:[.]|\d+)/)) {
    return "keyword";
  } else if (/[a-zA-Z\.]/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    var word = stream.current();
    if (atoms.propertyIsEnumerable(word)) return "atom";
    if (keywords.propertyIsEnumerable(word)) {
      // Block keywords start new blocks, except 'else if', which only starts
      // one new block for the 'if', no block for the 'else'.
      if (blockkeywords.propertyIsEnumerable(word) && !stream.match(/\s*if(\s+|$)/, false)) curPunc = "block";
      return "keyword";
    }
    if (builtins.propertyIsEnumerable(word)) return "builtin";
    return "variable";
  } else if (ch == "%") {
    if (stream.skipTo("%")) stream.next();
    return "variableName.special";
  } else if (ch == "<" && stream.eat("-") || ch == "<" && stream.match("<-") || ch == "-" && stream.match(/>>?/)) {
    return "operator";
  } else if (ch == "=" && state.ctx.argList) {
    return "operator";
  } else if (opChars.test(ch)) {
    if (ch == "$") return "operator";
    stream.eatWhile(opChars);
    return "operator";
  } else if (/[\(\){}\[\];]/.test(ch)) {
    curPunc = ch;
    if (ch == ";") return "punctuation";
    return null;
  } else {
    return null;
  }
}
function tokenString(quote) {
  return function (stream, state) {
    if (stream.eat("\\")) {
      var ch = stream.next();
      if (ch == "x") stream.match(/^[a-f0-9]{2}/i);else if ((ch == "u" || ch == "U") && stream.eat("{") && stream.skipTo("}")) stream.next();else if (ch == "u") stream.match(/^[a-f0-9]{4}/i);else if (ch == "U") stream.match(/^[a-f0-9]{8}/i);else if (/[0-7]/.test(ch)) stream.match(/^[0-7]{1,2}/);
      return "string.special";
    } else {
      var next;
      while ((next = stream.next()) != null) {
        if (next == quote) {
          state.tokenize = tokenBase;
          break;
        }
        if (next == "\\") {
          stream.backUp(1);
          break;
        }
      }
      return "string";
    }
  };
}
var ALIGN_YES = 1,
  ALIGN_NO = 2,
  BRACELESS = 4;
function push(state, type, stream) {
  state.ctx = {
    type: type,
    indent: state.indent,
    flags: 0,
    column: stream.column(),
    prev: state.ctx
  };
}
function setFlag(state, flag) {
  var ctx = state.ctx;
  state.ctx = {
    type: ctx.type,
    indent: ctx.indent,
    flags: ctx.flags | flag,
    column: ctx.column,
    prev: ctx.prev
  };
}
function pop(state) {
  state.indent = state.ctx.indent;
  state.ctx = state.ctx.prev;
}
const r = {
  name: "r",
  startState: function (indentUnit) {
    return {
      tokenize: tokenBase,
      ctx: {
        type: "top",
        indent: -indentUnit,
        flags: ALIGN_NO
      },
      indent: 0,
      afterIdent: false
    };
  },
  token: function (stream, state) {
    if (stream.sol()) {
      if ((state.ctx.flags & 3) == 0) state.ctx.flags |= ALIGN_NO;
      if (state.ctx.flags & BRACELESS) pop(state);
      state.indent = stream.indentation();
    }
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    if (style != "comment" && (state.ctx.flags & ALIGN_NO) == 0) setFlag(state, ALIGN_YES);
    if ((curPunc == ";" || curPunc == "{" || curPunc == "}") && state.ctx.type == "block") pop(state);
    if (curPunc == "{") push(state, "}", stream);else if (curPunc == "(") {
      push(state, ")", stream);
      if (state.afterIdent) state.ctx.argList = true;
    } else if (curPunc == "[") push(state, "]", stream);else if (curPunc == "block") push(state, "block", stream);else if (curPunc == state.ctx.type) pop(state);else if (state.ctx.type == "block" && style != "comment") setFlag(state, BRACELESS);
    state.afterIdent = style == "variable" || style == "keyword";
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != tokenBase) return 0;
    var firstChar = textAfter && textAfter.charAt(0),
      ctx = state.ctx,
      closing = firstChar == ctx.type;
    if (ctx.flags & BRACELESS) ctx = ctx.prev;
    if (ctx.type == "block") return ctx.indent + (firstChar == "{" ? 0 : cx.unit);else if (ctx.flags & ALIGN_YES) return ctx.column + (closing ? 0 : 1);else return ctx.indent + (closing ? 0 : cx.unit);
  },
  languageData: {
    wordChars: ".",
    commentTokens: {
      line: "#"
    },
    autocomplete: commonAtoms.concat(commonBuiltins, commonKeywords)
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTIwMC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9yLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIHdvcmRPYmood29yZHMpIHtcbiAgdmFyIHJlcyA9IHt9O1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHdvcmRzLmxlbmd0aDsgKytpKSByZXNbd29yZHNbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIHJlcztcbn1cbnZhciBjb21tb25BdG9tcyA9IFtcIk5VTExcIiwgXCJOQVwiLCBcIkluZlwiLCBcIk5hTlwiLCBcIk5BX2ludGVnZXJfXCIsIFwiTkFfcmVhbF9cIiwgXCJOQV9jb21wbGV4X1wiLCBcIk5BX2NoYXJhY3Rlcl9cIiwgXCJUUlVFXCIsIFwiRkFMU0VcIl07XG52YXIgY29tbW9uQnVpbHRpbnMgPSBbXCJsaXN0XCIsIFwicXVvdGVcIiwgXCJicXVvdGVcIiwgXCJldmFsXCIsIFwicmV0dXJuXCIsIFwiY2FsbFwiLCBcInBhcnNlXCIsIFwiZGVwYXJzZVwiXTtcbnZhciBjb21tb25LZXl3b3JkcyA9IFtcImlmXCIsIFwiZWxzZVwiLCBcInJlcGVhdFwiLCBcIndoaWxlXCIsIFwiZnVuY3Rpb25cIiwgXCJmb3JcIiwgXCJpblwiLCBcIm5leHRcIiwgXCJicmVha1wiXTtcbnZhciBjb21tb25CbG9ja0tleXdvcmRzID0gW1wiaWZcIiwgXCJlbHNlXCIsIFwicmVwZWF0XCIsIFwid2hpbGVcIiwgXCJmdW5jdGlvblwiLCBcImZvclwiXTtcbnZhciBhdG9tcyA9IHdvcmRPYmooY29tbW9uQXRvbXMpO1xudmFyIGJ1aWx0aW5zID0gd29yZE9iaihjb21tb25CdWlsdGlucyk7XG52YXIga2V5d29yZHMgPSB3b3JkT2JqKGNvbW1vbktleXdvcmRzKTtcbnZhciBibG9ja2tleXdvcmRzID0gd29yZE9iaihjb21tb25CbG9ja0tleXdvcmRzKTtcbnZhciBvcENoYXJzID0gL1srXFwtKlxcL148Pj0hJnx+JDpdLztcbnZhciBjdXJQdW5jO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgY3VyUHVuYyA9IG51bGw7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSBcIiNcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIwXCIgJiYgc3RyZWFtLmVhdChcInhcIikpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXGRhLWZdL2kpO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiLlwiICYmIHN0cmVhbS5lYXQoL1xcZC8pKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9cXGQqKD86ZVsrXFwtXT9cXGQrKT8vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfSBlbHNlIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5tYXRjaCgvXFxkKig/OlxcLlxcZCspPyg/OmVbK1xcLV1cXGQrKT9MPy8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiJ1wiIHx8IGNoID09ICdcIicpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcImBcIikge1xuICAgIHN0cmVhbS5tYXRjaCgvW15gXStgLyk7XG4gICAgcmV0dXJuIFwic3RyaW5nLnNwZWNpYWxcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIi5cIiAmJiBzdHJlYW0ubWF0Y2goLy4oPzpbLl18XFxkKykvKSkge1xuICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgfSBlbHNlIGlmICgvW2EtekEtWlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwuXS8pO1xuICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUod29yZCkpIHJldHVybiBcImF0b21cIjtcbiAgICBpZiAoa2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUod29yZCkpIHtcbiAgICAgIC8vIEJsb2NrIGtleXdvcmRzIHN0YXJ0IG5ldyBibG9ja3MsIGV4Y2VwdCAnZWxzZSBpZicsIHdoaWNoIG9ubHkgc3RhcnRzXG4gICAgICAvLyBvbmUgbmV3IGJsb2NrIGZvciB0aGUgJ2lmJywgbm8gYmxvY2sgZm9yIHRoZSAnZWxzZScuXG4gICAgICBpZiAoYmxvY2trZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkKSAmJiAhc3RyZWFtLm1hdGNoKC9cXHMqaWYoXFxzK3wkKS8sIGZhbHNlKSkgY3VyUHVuYyA9IFwiYmxvY2tcIjtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9XG4gICAgaWYgKGJ1aWx0aW5zLnByb3BlcnR5SXNFbnVtZXJhYmxlKHdvcmQpKSByZXR1cm4gXCJidWlsdGluXCI7XG4gICAgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIiVcIikge1xuICAgIGlmIChzdHJlYW0uc2tpcFRvKFwiJVwiKSkgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiPFwiICYmIHN0cmVhbS5lYXQoXCItXCIpIHx8IGNoID09IFwiPFwiICYmIHN0cmVhbS5tYXRjaChcIjwtXCIpIHx8IGNoID09IFwiLVwiICYmIHN0cmVhbS5tYXRjaCgvPj4/LykpIHtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiPVwiICYmIHN0YXRlLmN0eC5hcmdMaXN0KSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfSBlbHNlIGlmIChvcENoYXJzLnRlc3QoY2gpKSB7XG4gICAgaWYgKGNoID09IFwiJFwiKSByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgIHN0cmVhbS5lYXRXaGlsZShvcENoYXJzKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9IGVsc2UgaWYgKC9bXFwoXFwpe31cXFtcXF07XS8udGVzdChjaCkpIHtcbiAgICBjdXJQdW5jID0gY2g7XG4gICAgaWYgKGNoID09IFwiO1wiKSByZXR1cm4gXCJwdW5jdHVhdGlvblwiO1xuICAgIHJldHVybiBudWxsO1xuICB9IGVsc2Uge1xuICAgIHJldHVybiBudWxsO1xuICB9XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhxdW90ZSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChcIlxcXFxcIikpIHtcbiAgICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgICBpZiAoY2ggPT0gXCJ4XCIpIHN0cmVhbS5tYXRjaCgvXlthLWYwLTldezJ9L2kpO2Vsc2UgaWYgKChjaCA9PSBcInVcIiB8fCBjaCA9PSBcIlVcIikgJiYgc3RyZWFtLmVhdChcIntcIikgJiYgc3RyZWFtLnNraXBUbyhcIn1cIikpIHN0cmVhbS5uZXh0KCk7ZWxzZSBpZiAoY2ggPT0gXCJ1XCIpIHN0cmVhbS5tYXRjaCgvXlthLWYwLTldezR9L2kpO2Vsc2UgaWYgKGNoID09IFwiVVwiKSBzdHJlYW0ubWF0Y2goL15bYS1mMC05XXs4fS9pKTtlbHNlIGlmICgvWzAtN10vLnRlc3QoY2gpKSBzdHJlYW0ubWF0Y2goL15bMC03XXsxLDJ9Lyk7XG4gICAgICByZXR1cm4gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICAgIH0gZWxzZSB7XG4gICAgICB2YXIgbmV4dDtcbiAgICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgICAgaWYgKG5leHQgPT0gcXVvdGUpIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgICBpZiAobmV4dCA9PSBcIlxcXFxcIikge1xuICAgICAgICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIH1cbiAgfTtcbn1cbnZhciBBTElHTl9ZRVMgPSAxLFxuICBBTElHTl9OTyA9IDIsXG4gIEJSQUNFTEVTUyA9IDQ7XG5mdW5jdGlvbiBwdXNoKHN0YXRlLCB0eXBlLCBzdHJlYW0pIHtcbiAgc3RhdGUuY3R4ID0ge1xuICAgIHR5cGU6IHR5cGUsXG4gICAgaW5kZW50OiBzdGF0ZS5pbmRlbnQsXG4gICAgZmxhZ3M6IDAsXG4gICAgY29sdW1uOiBzdHJlYW0uY29sdW1uKCksXG4gICAgcHJldjogc3RhdGUuY3R4XG4gIH07XG59XG5mdW5jdGlvbiBzZXRGbGFnKHN0YXRlLCBmbGFnKSB7XG4gIHZhciBjdHggPSBzdGF0ZS5jdHg7XG4gIHN0YXRlLmN0eCA9IHtcbiAgICB0eXBlOiBjdHgudHlwZSxcbiAgICBpbmRlbnQ6IGN0eC5pbmRlbnQsXG4gICAgZmxhZ3M6IGN0eC5mbGFncyB8IGZsYWcsXG4gICAgY29sdW1uOiBjdHguY29sdW1uLFxuICAgIHByZXY6IGN0eC5wcmV2XG4gIH07XG59XG5mdW5jdGlvbiBwb3Aoc3RhdGUpIHtcbiAgc3RhdGUuaW5kZW50ID0gc3RhdGUuY3R4LmluZGVudDtcbiAgc3RhdGUuY3R4ID0gc3RhdGUuY3R4LnByZXY7XG59XG5leHBvcnQgY29uc3QgciA9IHtcbiAgbmFtZTogXCJyXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uIChpbmRlbnRVbml0KSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBjdHg6IHtcbiAgICAgICAgdHlwZTogXCJ0b3BcIixcbiAgICAgICAgaW5kZW50OiAtaW5kZW50VW5pdCxcbiAgICAgICAgZmxhZ3M6IEFMSUdOX05PXG4gICAgICB9LFxuICAgICAgaW5kZW50OiAwLFxuICAgICAgYWZ0ZXJJZGVudDogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBpZiAoKHN0YXRlLmN0eC5mbGFncyAmIDMpID09IDApIHN0YXRlLmN0eC5mbGFncyB8PSBBTElHTl9OTztcbiAgICAgIGlmIChzdGF0ZS5jdHguZmxhZ3MgJiBCUkFDRUxFU1MpIHBvcChzdGF0ZSk7XG4gICAgICBzdGF0ZS5pbmRlbnQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3R5bGUgIT0gXCJjb21tZW50XCIgJiYgKHN0YXRlLmN0eC5mbGFncyAmIEFMSUdOX05PKSA9PSAwKSBzZXRGbGFnKHN0YXRlLCBBTElHTl9ZRVMpO1xuICAgIGlmICgoY3VyUHVuYyA9PSBcIjtcIiB8fCBjdXJQdW5jID09IFwie1wiIHx8IGN1clB1bmMgPT0gXCJ9XCIpICYmIHN0YXRlLmN0eC50eXBlID09IFwiYmxvY2tcIikgcG9wKHN0YXRlKTtcbiAgICBpZiAoY3VyUHVuYyA9PSBcIntcIikgcHVzaChzdGF0ZSwgXCJ9XCIsIHN0cmVhbSk7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIihcIikge1xuICAgICAgcHVzaChzdGF0ZSwgXCIpXCIsIHN0cmVhbSk7XG4gICAgICBpZiAoc3RhdGUuYWZ0ZXJJZGVudCkgc3RhdGUuY3R4LmFyZ0xpc3QgPSB0cnVlO1xuICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBcIltcIikgcHVzaChzdGF0ZSwgXCJdXCIsIHN0cmVhbSk7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcImJsb2NrXCIpIHB1c2goc3RhdGUsIFwiYmxvY2tcIiwgc3RyZWFtKTtlbHNlIGlmIChjdXJQdW5jID09IHN0YXRlLmN0eC50eXBlKSBwb3Aoc3RhdGUpO2Vsc2UgaWYgKHN0YXRlLmN0eC50eXBlID09IFwiYmxvY2tcIiAmJiBzdHlsZSAhPSBcImNvbW1lbnRcIikgc2V0RmxhZyhzdGF0ZSwgQlJBQ0VMRVNTKTtcbiAgICBzdGF0ZS5hZnRlcklkZW50ID0gc3R5bGUgPT0gXCJ2YXJpYWJsZVwiIHx8IHN0eWxlID09IFwia2V5d29yZFwiO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICBpZiAoc3RhdGUudG9rZW5pemUgIT0gdG9rZW5CYXNlKSByZXR1cm4gMDtcbiAgICB2YXIgZmlyc3RDaGFyID0gdGV4dEFmdGVyICYmIHRleHRBZnRlci5jaGFyQXQoMCksXG4gICAgICBjdHggPSBzdGF0ZS5jdHgsXG4gICAgICBjbG9zaW5nID0gZmlyc3RDaGFyID09IGN0eC50eXBlO1xuICAgIGlmIChjdHguZmxhZ3MgJiBCUkFDRUxFU1MpIGN0eCA9IGN0eC5wcmV2O1xuICAgIGlmIChjdHgudHlwZSA9PSBcImJsb2NrXCIpIHJldHVybiBjdHguaW5kZW50ICsgKGZpcnN0Q2hhciA9PSBcIntcIiA/IDAgOiBjeC51bml0KTtlbHNlIGlmIChjdHguZmxhZ3MgJiBBTElHTl9ZRVMpIHJldHVybiBjdHguY29sdW1uICsgKGNsb3NpbmcgPyAwIDogMSk7ZWxzZSByZXR1cm4gY3R4LmluZGVudCArIChjbG9zaW5nID8gMCA6IGN4LnVuaXQpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICB3b3JkQ2hhcnM6IFwiLlwiLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiXG4gICAgfSxcbiAgICBhdXRvY29tcGxldGU6IGNvbW1vbkF0b21zLmNvbmNhdChjb21tb25CdWlsdGlucywgY29tbW9uS2V5d29yZHMpXG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==