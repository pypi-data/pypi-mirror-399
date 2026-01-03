"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5912],{

/***/ 45912
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   modelica: () => (/* binding */ modelica)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = words("algorithm and annotation assert block break class connect connector constant constrainedby der discrete each else elseif elsewhen encapsulated end enumeration equation expandable extends external false final flow for function if import impure in initial inner input loop model not operator or outer output package parameter partial protected public pure record redeclare replaceable return stream then true type when while within");
var builtin = words("abs acos actualStream asin atan atan2 cardinality ceil cos cosh delay div edge exp floor getInstanceName homotopy inStream integer log log10 mod pre reinit rem semiLinear sign sin sinh spatialDistribution sqrt tan tanh");
var atoms = words("Real Boolean Integer String");
var completions = [].concat(Object.keys(keywords), Object.keys(builtin), Object.keys(atoms));
var isSingleOperatorChar = /[;=\(:\),{}.*<>+\-\/^\[\]]/;
var isDoubleOperatorChar = /(:=|<=|>=|==|<>|\.\+|\.\-|\.\*|\.\/|\.\^)/;
var isDigit = /[0-9]/;
var isNonDigit = /[_a-zA-Z]/;
function tokenLineComment(stream, state) {
  stream.skipToEnd();
  state.tokenize = null;
  return "comment";
}
function tokenBlockComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (maybeEnd && ch == "/") {
      state.tokenize = null;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function tokenString(stream, state) {
  var escaped = false,
    ch;
  while ((ch = stream.next()) != null) {
    if (ch == '"' && !escaped) {
      state.tokenize = null;
      state.sol = false;
      break;
    }
    escaped = !escaped && ch == "\\";
  }
  return "string";
}
function tokenIdent(stream, state) {
  stream.eatWhile(isDigit);
  while (stream.eat(isDigit) || stream.eat(isNonDigit)) {}
  var cur = stream.current();
  if (state.sol && (cur == "package" || cur == "model" || cur == "when" || cur == "connector")) state.level++;else if (state.sol && cur == "end" && state.level > 0) state.level--;
  state.tokenize = null;
  state.sol = false;
  if (keywords.propertyIsEnumerable(cur)) return "keyword";else if (builtin.propertyIsEnumerable(cur)) return "builtin";else if (atoms.propertyIsEnumerable(cur)) return "atom";else return "variable";
}
function tokenQIdent(stream, state) {
  while (stream.eat(/[^']/)) {}
  state.tokenize = null;
  state.sol = false;
  if (stream.eat("'")) return "variable";else return "error";
}
function tokenUnsignedNumber(stream, state) {
  stream.eatWhile(isDigit);
  if (stream.eat('.')) {
    stream.eatWhile(isDigit);
  }
  if (stream.eat('e') || stream.eat('E')) {
    if (!stream.eat('-')) stream.eat('+');
    stream.eatWhile(isDigit);
  }
  state.tokenize = null;
  state.sol = false;
  return "number";
}

// Interface
const modelica = {
  name: "modelica",
  startState: function () {
    return {
      tokenize: null,
      level: 0,
      sol: true
    };
  },
  token: function (stream, state) {
    if (state.tokenize != null) {
      return state.tokenize(stream, state);
    }
    if (stream.sol()) {
      state.sol = true;
    }

    // WHITESPACE
    if (stream.eatSpace()) {
      state.tokenize = null;
      return null;
    }
    var ch = stream.next();

    // LINECOMMENT
    if (ch == '/' && stream.eat('/')) {
      state.tokenize = tokenLineComment;
    }
    // BLOCKCOMMENT
    else if (ch == '/' && stream.eat('*')) {
      state.tokenize = tokenBlockComment;
    }
    // TWO SYMBOL TOKENS
    else if (isDoubleOperatorChar.test(ch + stream.peek())) {
      stream.next();
      state.tokenize = null;
      return "operator";
    }
    // SINGLE SYMBOL TOKENS
    else if (isSingleOperatorChar.test(ch)) {
      state.tokenize = null;
      return "operator";
    }
    // IDENT
    else if (isNonDigit.test(ch)) {
      state.tokenize = tokenIdent;
    }
    // Q-IDENT
    else if (ch == "'" && stream.peek() && stream.peek() != "'") {
      state.tokenize = tokenQIdent;
    }
    // STRING
    else if (ch == '"') {
      state.tokenize = tokenString;
    }
    // UNSIGNED_NUMBER
    else if (isDigit.test(ch)) {
      state.tokenize = tokenUnsignedNumber;
    }
    // ERROR
    else {
      state.tokenize = null;
      return "error";
    }
    return state.tokenize(stream, state);
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != null) return null;
    var level = state.level;
    if (/(algorithm)/.test(textAfter)) level--;
    if (/(equation)/.test(textAfter)) level--;
    if (/(initial algorithm)/.test(textAfter)) level--;
    if (/(initial equation)/.test(textAfter)) level--;
    if (/(end)/.test(textAfter)) level--;
    if (level > 0) return cx.unit * level;else return 0;
  },
  languageData: {
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    },
    autocomplete: completions
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTkxMi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9tb2RlbGljYS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiIFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBvYmo7XG59XG52YXIga2V5d29yZHMgPSB3b3JkcyhcImFsZ29yaXRobSBhbmQgYW5ub3RhdGlvbiBhc3NlcnQgYmxvY2sgYnJlYWsgY2xhc3MgY29ubmVjdCBjb25uZWN0b3IgY29uc3RhbnQgY29uc3RyYWluZWRieSBkZXIgZGlzY3JldGUgZWFjaCBlbHNlIGVsc2VpZiBlbHNld2hlbiBlbmNhcHN1bGF0ZWQgZW5kIGVudW1lcmF0aW9uIGVxdWF0aW9uIGV4cGFuZGFibGUgZXh0ZW5kcyBleHRlcm5hbCBmYWxzZSBmaW5hbCBmbG93IGZvciBmdW5jdGlvbiBpZiBpbXBvcnQgaW1wdXJlIGluIGluaXRpYWwgaW5uZXIgaW5wdXQgbG9vcCBtb2RlbCBub3Qgb3BlcmF0b3Igb3Igb3V0ZXIgb3V0cHV0IHBhY2thZ2UgcGFyYW1ldGVyIHBhcnRpYWwgcHJvdGVjdGVkIHB1YmxpYyBwdXJlIHJlY29yZCByZWRlY2xhcmUgcmVwbGFjZWFibGUgcmV0dXJuIHN0cmVhbSB0aGVuIHRydWUgdHlwZSB3aGVuIHdoaWxlIHdpdGhpblwiKTtcbnZhciBidWlsdGluID0gd29yZHMoXCJhYnMgYWNvcyBhY3R1YWxTdHJlYW0gYXNpbiBhdGFuIGF0YW4yIGNhcmRpbmFsaXR5IGNlaWwgY29zIGNvc2ggZGVsYXkgZGl2IGVkZ2UgZXhwIGZsb29yIGdldEluc3RhbmNlTmFtZSBob21vdG9weSBpblN0cmVhbSBpbnRlZ2VyIGxvZyBsb2cxMCBtb2QgcHJlIHJlaW5pdCByZW0gc2VtaUxpbmVhciBzaWduIHNpbiBzaW5oIHNwYXRpYWxEaXN0cmlidXRpb24gc3FydCB0YW4gdGFuaFwiKTtcbnZhciBhdG9tcyA9IHdvcmRzKFwiUmVhbCBCb29sZWFuIEludGVnZXIgU3RyaW5nXCIpO1xudmFyIGNvbXBsZXRpb25zID0gW10uY29uY2F0KE9iamVjdC5rZXlzKGtleXdvcmRzKSwgT2JqZWN0LmtleXMoYnVpbHRpbiksIE9iamVjdC5rZXlzKGF0b21zKSk7XG52YXIgaXNTaW5nbGVPcGVyYXRvckNoYXIgPSAvWzs9XFwoOlxcKSx7fS4qPD4rXFwtXFwvXlxcW1xcXV0vO1xudmFyIGlzRG91YmxlT3BlcmF0b3JDaGFyID0gLyg6PXw8PXw+PXw9PXw8PnxcXC5cXCt8XFwuXFwtfFxcLlxcKnxcXC5cXC98XFwuXFxeKS87XG52YXIgaXNEaWdpdCA9IC9bMC05XS87XG52YXIgaXNOb25EaWdpdCA9IC9bX2EtekEtWl0vO1xuZnVuY3Rpb24gdG9rZW5MaW5lQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5mdW5jdGlvbiB0b2tlbkJsb2NrQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKG1heWJlRW5kICYmIGNoID09IFwiL1wiKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbWF5YmVFbmQgPSBjaCA9PSBcIipcIjtcbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlICgoY2ggPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgaWYgKGNoID09ICdcIicgJiYgIWVzY2FwZWQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIHN0YXRlLnNvbCA9IGZhbHNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBjaCA9PSBcIlxcXFxcIjtcbiAgfVxuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cbmZ1bmN0aW9uIHRva2VuSWRlbnQoc3RyZWFtLCBzdGF0ZSkge1xuICBzdHJlYW0uZWF0V2hpbGUoaXNEaWdpdCk7XG4gIHdoaWxlIChzdHJlYW0uZWF0KGlzRGlnaXQpIHx8IHN0cmVhbS5lYXQoaXNOb25EaWdpdCkpIHt9XG4gIHZhciBjdXIgPSBzdHJlYW0uY3VycmVudCgpO1xuICBpZiAoc3RhdGUuc29sICYmIChjdXIgPT0gXCJwYWNrYWdlXCIgfHwgY3VyID09IFwibW9kZWxcIiB8fCBjdXIgPT0gXCJ3aGVuXCIgfHwgY3VyID09IFwiY29ubmVjdG9yXCIpKSBzdGF0ZS5sZXZlbCsrO2Vsc2UgaWYgKHN0YXRlLnNvbCAmJiBjdXIgPT0gXCJlbmRcIiAmJiBzdGF0ZS5sZXZlbCA+IDApIHN0YXRlLmxldmVsLS07XG4gIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgc3RhdGUuc29sID0gZmFsc2U7XG4gIGlmIChrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSByZXR1cm4gXCJrZXl3b3JkXCI7ZWxzZSBpZiAoYnVpbHRpbi5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSByZXR1cm4gXCJidWlsdGluXCI7ZWxzZSBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO2Vsc2UgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cbmZ1bmN0aW9uIHRva2VuUUlkZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgd2hpbGUgKHN0cmVhbS5lYXQoL1teJ10vKSkge31cbiAgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICBzdGF0ZS5zb2wgPSBmYWxzZTtcbiAgaWYgKHN0cmVhbS5lYXQoXCInXCIpKSByZXR1cm4gXCJ2YXJpYWJsZVwiO2Vsc2UgcmV0dXJuIFwiZXJyb3JcIjtcbn1cbmZ1bmN0aW9uIHRva2VuVW5zaWduZWROdW1iZXIoc3RyZWFtLCBzdGF0ZSkge1xuICBzdHJlYW0uZWF0V2hpbGUoaXNEaWdpdCk7XG4gIGlmIChzdHJlYW0uZWF0KCcuJykpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNEaWdpdCk7XG4gIH1cbiAgaWYgKHN0cmVhbS5lYXQoJ2UnKSB8fCBzdHJlYW0uZWF0KCdFJykpIHtcbiAgICBpZiAoIXN0cmVhbS5lYXQoJy0nKSkgc3RyZWFtLmVhdCgnKycpO1xuICAgIHN0cmVhbS5lYXRXaGlsZShpc0RpZ2l0KTtcbiAgfVxuICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gIHN0YXRlLnNvbCA9IGZhbHNlO1xuICByZXR1cm4gXCJudW1iZXJcIjtcbn1cblxuLy8gSW50ZXJmYWNlXG5leHBvcnQgY29uc3QgbW9kZWxpY2EgPSB7XG4gIG5hbWU6IFwibW9kZWxpY2FcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogbnVsbCxcbiAgICAgIGxldmVsOiAwLFxuICAgICAgc29sOiB0cnVlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0YXRlLnRva2VuaXplICE9IG51bGwpIHtcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgc3RhdGUuc29sID0gdHJ1ZTtcbiAgICB9XG5cbiAgICAvLyBXSElURVNQQUNFXG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICB9XG4gICAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcblxuICAgIC8vIExJTkVDT01NRU5UXG4gICAgaWYgKGNoID09ICcvJyAmJiBzdHJlYW0uZWF0KCcvJykpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5MaW5lQ29tbWVudDtcbiAgICB9XG4gICAgLy8gQkxPQ0tDT01NRU5UXG4gICAgZWxzZSBpZiAoY2ggPT0gJy8nICYmIHN0cmVhbS5lYXQoJyonKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJsb2NrQ29tbWVudDtcbiAgICB9XG4gICAgLy8gVFdPIFNZTUJPTCBUT0tFTlNcbiAgICBlbHNlIGlmIChpc0RvdWJsZU9wZXJhdG9yQ2hhci50ZXN0KGNoICsgc3RyZWFtLnBlZWsoKSkpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgIH1cbiAgICAvLyBTSU5HTEUgU1lNQk9MIFRPS0VOU1xuICAgIGVsc2UgaWYgKGlzU2luZ2xlT3BlcmF0b3JDaGFyLnRlc3QoY2gpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgIH1cbiAgICAvLyBJREVOVFxuICAgIGVsc2UgaWYgKGlzTm9uRGlnaXQudGVzdChjaCkpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5JZGVudDtcbiAgICB9XG4gICAgLy8gUS1JREVOVFxuICAgIGVsc2UgaWYgKGNoID09IFwiJ1wiICYmIHN0cmVhbS5wZWVrKCkgJiYgc3RyZWFtLnBlZWsoKSAhPSBcIidcIikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblFJZGVudDtcbiAgICB9XG4gICAgLy8gU1RSSU5HXG4gICAgZWxzZSBpZiAoY2ggPT0gJ1wiJykge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZztcbiAgICB9XG4gICAgLy8gVU5TSUdORURfTlVNQkVSXG4gICAgZWxzZSBpZiAoaXNEaWdpdC50ZXN0KGNoKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblVuc2lnbmVkTnVtYmVyO1xuICAgIH1cbiAgICAvLyBFUlJPUlxuICAgIGVsc2Uge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgICAgcmV0dXJuIFwiZXJyb3JcIjtcbiAgICB9XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgIGlmIChzdGF0ZS50b2tlbml6ZSAhPSBudWxsKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgbGV2ZWwgPSBzdGF0ZS5sZXZlbDtcbiAgICBpZiAoLyhhbGdvcml0aG0pLy50ZXN0KHRleHRBZnRlcikpIGxldmVsLS07XG4gICAgaWYgKC8oZXF1YXRpb24pLy50ZXN0KHRleHRBZnRlcikpIGxldmVsLS07XG4gICAgaWYgKC8oaW5pdGlhbCBhbGdvcml0aG0pLy50ZXN0KHRleHRBZnRlcikpIGxldmVsLS07XG4gICAgaWYgKC8oaW5pdGlhbCBlcXVhdGlvbikvLnRlc3QodGV4dEFmdGVyKSkgbGV2ZWwtLTtcbiAgICBpZiAoLyhlbmQpLy50ZXN0KHRleHRBZnRlcikpIGxldmVsLS07XG4gICAgaWYgKGxldmVsID4gMCkgcmV0dXJuIGN4LnVuaXQgKiBsZXZlbDtlbHNlIHJldHVybiAwO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIi8vXCIsXG4gICAgICBibG9jazoge1xuICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgIH1cbiAgICB9LFxuICAgIGF1dG9jb21wbGV0ZTogY29tcGxldGlvbnNcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9