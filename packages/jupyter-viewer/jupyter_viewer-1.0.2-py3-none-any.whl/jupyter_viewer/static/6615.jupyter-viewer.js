"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6615],{

/***/ 26615
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   julia: () => (/* binding */ julia)
/* harmony export */ });
function wordRegexp(words, end, pre) {
  if (typeof pre === "undefined") pre = "";
  if (typeof end === "undefined") {
    end = "\\b";
  }
  return new RegExp("^" + pre + "((" + words.join(")|(") + "))" + end);
}
var octChar = "\\\\[0-7]{1,3}";
var hexChar = "\\\\x[A-Fa-f0-9]{1,2}";
var sChar = "\\\\[abefnrtv0%?'\"\\\\]";
var uChar = "([^\\u0027\\u005C\\uD800-\\uDFFF]|[\\uD800-\\uDFFF][\\uDC00-\\uDFFF])";
var asciiOperatorsList = ["[<>]:", "[<>=]=", "<<=?", ">>>?=?", "=>", "--?>", "<--[->]?", "\\/\\/", "\\.{2,3}", "[\\.\\\\%*+\\-<>!\\/^|&]=?", "\\?", "\\$", "~", ":"];
var operators = wordRegexp(["[<>]:", "[<>=]=", "[!=]==", "<<=?", ">>>?=?", "=>?", "--?>", "<--[->]?", "\\/\\/", "[\\\\%*+\\-<>!\\/^|&\\u00F7\\u22BB]=?", "\\?", "\\$", "~", ":", "\\u00D7", "\\u2208", "\\u2209", "\\u220B", "\\u220C", "\\u2218", "\\u221A", "\\u221B", "\\u2229", "\\u222A", "\\u2260", "\\u2264", "\\u2265", "\\u2286", "\\u2288", "\\u228A", "\\u22C5", "\\b(in|isa)\\b(?!\.?\\()"], "");
var delimiters = /^[;,()[\]{}]/;
var identifiers = /^[_A-Za-z\u00A1-\u2217\u2219-\uFFFF][\w\u00A1-\u2217\u2219-\uFFFF]*!*/;
var chars = wordRegexp([octChar, hexChar, sChar, uChar], "'");
var openersList = ["begin", "function", "type", "struct", "immutable", "let", "macro", "for", "while", "quote", "if", "else", "elseif", "try", "finally", "catch", "do"];
var closersList = ["end", "else", "elseif", "catch", "finally"];
var keywordsList = ["if", "else", "elseif", "while", "for", "begin", "let", "end", "do", "try", "catch", "finally", "return", "break", "continue", "global", "local", "const", "export", "import", "importall", "using", "function", "where", "macro", "module", "baremodule", "struct", "type", "mutable", "immutable", "quote", "typealias", "abstract", "primitive", "bitstype"];
var builtinsList = ["true", "false", "nothing", "NaN", "Inf"];
var openers = wordRegexp(openersList);
var closers = wordRegexp(closersList);
var keywords = wordRegexp(keywordsList);
var builtins = wordRegexp(builtinsList);
var macro = /^@[_A-Za-z\u00A1-\uFFFF][\w\u00A1-\uFFFF]*!*/;
var symbol = /^:[_A-Za-z\u00A1-\uFFFF][\w\u00A1-\uFFFF]*!*/;
var stringPrefixes = /^(`|([_A-Za-z\u00A1-\uFFFF]*"("")?))/;
var macroOperators = wordRegexp(asciiOperatorsList, "", "@");
var symbolOperators = wordRegexp(asciiOperatorsList, "", ":");
function inArray(state) {
  return state.nestedArrays > 0;
}
function inGenerator(state) {
  return state.nestedGenerators > 0;
}
function currentScope(state, n) {
  if (typeof n === "undefined") {
    n = 0;
  }
  if (state.scopes.length <= n) {
    return null;
  }
  return state.scopes[state.scopes.length - (n + 1)];
}

// tokenizers
function tokenBase(stream, state) {
  // Handle multiline comments
  if (stream.match('#=', false)) {
    state.tokenize = tokenComment;
    return state.tokenize(stream, state);
  }

  // Handle scope changes
  var leavingExpr = state.leavingExpr;
  if (stream.sol()) {
    leavingExpr = false;
  }
  state.leavingExpr = false;
  if (leavingExpr) {
    if (stream.match(/^'+/)) {
      return "operator";
    }
  }
  if (stream.match(/\.{4,}/)) {
    return "error";
  } else if (stream.match(/\.{1,3}/)) {
    return "operator";
  }
  if (stream.eatSpace()) {
    return null;
  }
  var ch = stream.peek();

  // Handle single line comments
  if (ch === '#') {
    stream.skipToEnd();
    return "comment";
  }
  if (ch === '[') {
    state.scopes.push('[');
    state.nestedArrays++;
  }
  if (ch === '(') {
    state.scopes.push('(');
    state.nestedGenerators++;
  }
  if (inArray(state) && ch === ']') {
    while (state.scopes.length && currentScope(state) !== "[") {
      state.scopes.pop();
    }
    state.scopes.pop();
    state.nestedArrays--;
    state.leavingExpr = true;
  }
  if (inGenerator(state) && ch === ')') {
    while (state.scopes.length && currentScope(state) !== "(") {
      state.scopes.pop();
    }
    state.scopes.pop();
    state.nestedGenerators--;
    state.leavingExpr = true;
  }
  if (inArray(state)) {
    if (state.lastToken == "end" && stream.match(':')) {
      return "operator";
    }
    if (stream.match('end')) {
      return "number";
    }
  }
  var match;
  if (match = stream.match(openers, false)) {
    state.scopes.push(match[0]);
  }
  if (stream.match(closers, false)) {
    state.scopes.pop();
  }

  // Handle type annotations
  if (stream.match(/^::(?![:\$])/)) {
    state.tokenize = tokenAnnotation;
    return state.tokenize(stream, state);
  }

  // Handle symbols
  if (!leavingExpr && (stream.match(symbol) || stream.match(symbolOperators))) {
    return "builtin";
  }

  // Handle parametric types
  //if (stream.match(/^{[^}]*}(?=\()/)) {
  //  return "builtin";
  //}

  // Handle operators and Delimiters
  if (stream.match(operators)) {
    return "operator";
  }

  // Handle Number Literals
  if (stream.match(/^\.?\d/, false)) {
    var imMatcher = RegExp(/^im\b/);
    var numberLiteral = false;
    if (stream.match(/^0x\.[0-9a-f_]+p[\+\-]?[_\d]+/i)) {
      numberLiteral = true;
    }
    // Integers
    if (stream.match(/^0x[0-9a-f_]+/i)) {
      numberLiteral = true;
    } // Hex
    if (stream.match(/^0b[01_]+/i)) {
      numberLiteral = true;
    } // Binary
    if (stream.match(/^0o[0-7_]+/i)) {
      numberLiteral = true;
    } // Octal
    // Floats
    if (stream.match(/^(?:(?:\d[_\d]*)?\.(?!\.)(?:\d[_\d]*)?|\d[_\d]*\.(?!\.)(?:\d[_\d]*))?([Eef][\+\-]?[_\d]+)?/i)) {
      numberLiteral = true;
    }
    if (stream.match(/^\d[_\d]*(e[\+\-]?\d+)?/i)) {
      numberLiteral = true;
    } // Decimal
    if (numberLiteral) {
      // Integer literals may be "long"
      stream.match(imMatcher);
      state.leavingExpr = true;
      return "number";
    }
  }

  // Handle Chars
  if (stream.match("'")) {
    state.tokenize = tokenChar;
    return state.tokenize(stream, state);
  }

  // Handle Strings
  if (stream.match(stringPrefixes)) {
    state.tokenize = tokenStringFactory(stream.current());
    return state.tokenize(stream, state);
  }
  if (stream.match(macro) || stream.match(macroOperators)) {
    return "meta";
  }
  if (stream.match(delimiters)) {
    return null;
  }
  if (stream.match(keywords)) {
    return "keyword";
  }
  if (stream.match(builtins)) {
    return "builtin";
  }
  var isDefinition = state.isDefinition || state.lastToken == "function" || state.lastToken == "macro" || state.lastToken == "type" || state.lastToken == "struct" || state.lastToken == "immutable";
  if (stream.match(identifiers)) {
    if (isDefinition) {
      if (stream.peek() === '.') {
        state.isDefinition = true;
        return "variable";
      }
      state.isDefinition = false;
      return "def";
    }
    state.leavingExpr = true;
    return "variable";
  }

  // Handle non-detected items
  stream.next();
  return "error";
}
function tokenAnnotation(stream, state) {
  stream.match(/.*?(?=[,;{}()=\s]|$)/);
  if (stream.match('{')) {
    state.nestedParameters++;
  } else if (stream.match('}') && state.nestedParameters > 0) {
    state.nestedParameters--;
  }
  if (state.nestedParameters > 0) {
    stream.match(/.*?(?={|})/) || stream.next();
  } else if (state.nestedParameters == 0) {
    state.tokenize = tokenBase;
  }
  return "builtin";
}
function tokenComment(stream, state) {
  if (stream.match('#=')) {
    state.nestedComments++;
  }
  if (!stream.match(/.*?(?=(#=|=#))/)) {
    stream.skipToEnd();
  }
  if (stream.match('=#')) {
    state.nestedComments--;
    if (state.nestedComments == 0) state.tokenize = tokenBase;
  }
  return "comment";
}
function tokenChar(stream, state) {
  var isChar = false,
    match;
  if (stream.match(chars)) {
    isChar = true;
  } else if (match = stream.match(/\\u([a-f0-9]{1,4})(?=')/i)) {
    var value = parseInt(match[1], 16);
    if (value <= 55295 || value >= 57344) {
      // (U+0,U+D7FF), (U+E000,U+FFFF)
      isChar = true;
      stream.next();
    }
  } else if (match = stream.match(/\\U([A-Fa-f0-9]{5,8})(?=')/)) {
    var value = parseInt(match[1], 16);
    if (value <= 1114111) {
      // U+10FFFF
      isChar = true;
      stream.next();
    }
  }
  if (isChar) {
    state.leavingExpr = true;
    state.tokenize = tokenBase;
    return "string";
  }
  if (!stream.match(/^[^']+(?=')/)) {
    stream.skipToEnd();
  }
  if (stream.match("'")) {
    state.tokenize = tokenBase;
  }
  return "error";
}
function tokenStringFactory(delimiter) {
  if (delimiter.substr(-3) === '"""') {
    delimiter = '"""';
  } else if (delimiter.substr(-1) === '"') {
    delimiter = '"';
  }
  function tokenString(stream, state) {
    if (stream.eat('\\')) {
      stream.next();
    } else if (stream.match(delimiter)) {
      state.tokenize = tokenBase;
      state.leavingExpr = true;
      return "string";
    } else {
      stream.eat(/[`"]/);
    }
    stream.eatWhile(/[^\\`"]/);
    return "string";
  }
  return tokenString;
}
const julia = {
  name: "julia",
  startState: function () {
    return {
      tokenize: tokenBase,
      scopes: [],
      lastToken: null,
      leavingExpr: false,
      isDefinition: false,
      nestedArrays: 0,
      nestedComments: 0,
      nestedGenerators: 0,
      nestedParameters: 0,
      firstParenPos: -1
    };
  },
  token: function (stream, state) {
    var style = state.tokenize(stream, state);
    var current = stream.current();
    if (current && style) {
      state.lastToken = current;
    }
    return style;
  },
  indent: function (state, textAfter, cx) {
    var delta = 0;
    if (textAfter === ']' || textAfter === ')' || /^end\b/.test(textAfter) || /^else/.test(textAfter) || /^catch\b/.test(textAfter) || /^elseif\b/.test(textAfter) || /^finally/.test(textAfter)) {
      delta = -1;
    }
    return (state.scopes.length + delta) * cx.unit;
  },
  languageData: {
    indentOnInput: /^\s*(end|else|catch|finally)\b$/,
    commentTokens: {
      line: "#",
      block: {
        open: "#=",
        close: "=#"
      }
    },
    closeBrackets: {
      brackets: ["(", "[", "{", '"']
    },
    autocomplete: keywordsList.concat(builtinsList)
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjYxNS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvanVsaWEuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZFJlZ2V4cCh3b3JkcywgZW5kLCBwcmUpIHtcbiAgaWYgKHR5cGVvZiBwcmUgPT09IFwidW5kZWZpbmVkXCIpIHByZSA9IFwiXCI7XG4gIGlmICh0eXBlb2YgZW5kID09PSBcInVuZGVmaW5lZFwiKSB7XG4gICAgZW5kID0gXCJcXFxcYlwiO1xuICB9XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXlwiICsgcHJlICsgXCIoKFwiICsgd29yZHMuam9pbihcIil8KFwiKSArIFwiKSlcIiArIGVuZCk7XG59XG52YXIgb2N0Q2hhciA9IFwiXFxcXFxcXFxbMC03XXsxLDN9XCI7XG52YXIgaGV4Q2hhciA9IFwiXFxcXFxcXFx4W0EtRmEtZjAtOV17MSwyfVwiO1xudmFyIHNDaGFyID0gXCJcXFxcXFxcXFthYmVmbnJ0djAlPydcXFwiXFxcXFxcXFxdXCI7XG52YXIgdUNoYXIgPSBcIihbXlxcXFx1MDAyN1xcXFx1MDA1Q1xcXFx1RDgwMC1cXFxcdURGRkZdfFtcXFxcdUQ4MDAtXFxcXHVERkZGXVtcXFxcdURDMDAtXFxcXHVERkZGXSlcIjtcbnZhciBhc2NpaU9wZXJhdG9yc0xpc3QgPSBbXCJbPD5dOlwiLCBcIls8Pj1dPVwiLCBcIjw8PT9cIiwgXCI+Pj4/PT9cIiwgXCI9PlwiLCBcIi0tPz5cIiwgXCI8LS1bLT5dP1wiLCBcIlxcXFwvXFxcXC9cIiwgXCJcXFxcLnsyLDN9XCIsIFwiW1xcXFwuXFxcXFxcXFwlKitcXFxcLTw+IVxcXFwvXnwmXT0/XCIsIFwiXFxcXD9cIiwgXCJcXFxcJFwiLCBcIn5cIiwgXCI6XCJdO1xudmFyIG9wZXJhdG9ycyA9IHdvcmRSZWdleHAoW1wiWzw+XTpcIiwgXCJbPD49XT1cIiwgXCJbIT1dPT1cIiwgXCI8PD0/XCIsIFwiPj4+Pz0/XCIsIFwiPT4/XCIsIFwiLS0/PlwiLCBcIjwtLVstPl0/XCIsIFwiXFxcXC9cXFxcL1wiLCBcIltcXFxcXFxcXCUqK1xcXFwtPD4hXFxcXC9efCZcXFxcdTAwRjdcXFxcdTIyQkJdPT9cIiwgXCJcXFxcP1wiLCBcIlxcXFwkXCIsIFwiflwiLCBcIjpcIiwgXCJcXFxcdTAwRDdcIiwgXCJcXFxcdTIyMDhcIiwgXCJcXFxcdTIyMDlcIiwgXCJcXFxcdTIyMEJcIiwgXCJcXFxcdTIyMENcIiwgXCJcXFxcdTIyMThcIiwgXCJcXFxcdTIyMUFcIiwgXCJcXFxcdTIyMUJcIiwgXCJcXFxcdTIyMjlcIiwgXCJcXFxcdTIyMkFcIiwgXCJcXFxcdTIyNjBcIiwgXCJcXFxcdTIyNjRcIiwgXCJcXFxcdTIyNjVcIiwgXCJcXFxcdTIyODZcIiwgXCJcXFxcdTIyODhcIiwgXCJcXFxcdTIyOEFcIiwgXCJcXFxcdTIyQzVcIiwgXCJcXFxcYihpbnxpc2EpXFxcXGIoPyFcXC4/XFxcXCgpXCJdLCBcIlwiKTtcbnZhciBkZWxpbWl0ZXJzID0gL15bOywoKVtcXF17fV0vO1xudmFyIGlkZW50aWZpZXJzID0gL15bX0EtWmEtelxcdTAwQTEtXFx1MjIxN1xcdTIyMTktXFx1RkZGRl1bXFx3XFx1MDBBMS1cXHUyMjE3XFx1MjIxOS1cXHVGRkZGXSohKi87XG52YXIgY2hhcnMgPSB3b3JkUmVnZXhwKFtvY3RDaGFyLCBoZXhDaGFyLCBzQ2hhciwgdUNoYXJdLCBcIidcIik7XG52YXIgb3BlbmVyc0xpc3QgPSBbXCJiZWdpblwiLCBcImZ1bmN0aW9uXCIsIFwidHlwZVwiLCBcInN0cnVjdFwiLCBcImltbXV0YWJsZVwiLCBcImxldFwiLCBcIm1hY3JvXCIsIFwiZm9yXCIsIFwid2hpbGVcIiwgXCJxdW90ZVwiLCBcImlmXCIsIFwiZWxzZVwiLCBcImVsc2VpZlwiLCBcInRyeVwiLCBcImZpbmFsbHlcIiwgXCJjYXRjaFwiLCBcImRvXCJdO1xudmFyIGNsb3NlcnNMaXN0ID0gW1wiZW5kXCIsIFwiZWxzZVwiLCBcImVsc2VpZlwiLCBcImNhdGNoXCIsIFwiZmluYWxseVwiXTtcbnZhciBrZXl3b3Jkc0xpc3QgPSBbXCJpZlwiLCBcImVsc2VcIiwgXCJlbHNlaWZcIiwgXCJ3aGlsZVwiLCBcImZvclwiLCBcImJlZ2luXCIsIFwibGV0XCIsIFwiZW5kXCIsIFwiZG9cIiwgXCJ0cnlcIiwgXCJjYXRjaFwiLCBcImZpbmFsbHlcIiwgXCJyZXR1cm5cIiwgXCJicmVha1wiLCBcImNvbnRpbnVlXCIsIFwiZ2xvYmFsXCIsIFwibG9jYWxcIiwgXCJjb25zdFwiLCBcImV4cG9ydFwiLCBcImltcG9ydFwiLCBcImltcG9ydGFsbFwiLCBcInVzaW5nXCIsIFwiZnVuY3Rpb25cIiwgXCJ3aGVyZVwiLCBcIm1hY3JvXCIsIFwibW9kdWxlXCIsIFwiYmFyZW1vZHVsZVwiLCBcInN0cnVjdFwiLCBcInR5cGVcIiwgXCJtdXRhYmxlXCIsIFwiaW1tdXRhYmxlXCIsIFwicXVvdGVcIiwgXCJ0eXBlYWxpYXNcIiwgXCJhYnN0cmFjdFwiLCBcInByaW1pdGl2ZVwiLCBcImJpdHN0eXBlXCJdO1xudmFyIGJ1aWx0aW5zTGlzdCA9IFtcInRydWVcIiwgXCJmYWxzZVwiLCBcIm5vdGhpbmdcIiwgXCJOYU5cIiwgXCJJbmZcIl07XG52YXIgb3BlbmVycyA9IHdvcmRSZWdleHAob3BlbmVyc0xpc3QpO1xudmFyIGNsb3NlcnMgPSB3b3JkUmVnZXhwKGNsb3NlcnNMaXN0KTtcbnZhciBrZXl3b3JkcyA9IHdvcmRSZWdleHAoa2V5d29yZHNMaXN0KTtcbnZhciBidWlsdGlucyA9IHdvcmRSZWdleHAoYnVpbHRpbnNMaXN0KTtcbnZhciBtYWNybyA9IC9eQFtfQS1aYS16XFx1MDBBMS1cXHVGRkZGXVtcXHdcXHUwMEExLVxcdUZGRkZdKiEqLztcbnZhciBzeW1ib2wgPSAvXjpbX0EtWmEtelxcdTAwQTEtXFx1RkZGRl1bXFx3XFx1MDBBMS1cXHVGRkZGXSohKi87XG52YXIgc3RyaW5nUHJlZml4ZXMgPSAvXihgfChbX0EtWmEtelxcdTAwQTEtXFx1RkZGRl0qXCIoXCJcIik/KSkvO1xudmFyIG1hY3JvT3BlcmF0b3JzID0gd29yZFJlZ2V4cChhc2NpaU9wZXJhdG9yc0xpc3QsIFwiXCIsIFwiQFwiKTtcbnZhciBzeW1ib2xPcGVyYXRvcnMgPSB3b3JkUmVnZXhwKGFzY2lpT3BlcmF0b3JzTGlzdCwgXCJcIiwgXCI6XCIpO1xuZnVuY3Rpb24gaW5BcnJheShzdGF0ZSkge1xuICByZXR1cm4gc3RhdGUubmVzdGVkQXJyYXlzID4gMDtcbn1cbmZ1bmN0aW9uIGluR2VuZXJhdG9yKHN0YXRlKSB7XG4gIHJldHVybiBzdGF0ZS5uZXN0ZWRHZW5lcmF0b3JzID4gMDtcbn1cbmZ1bmN0aW9uIGN1cnJlbnRTY29wZShzdGF0ZSwgbikge1xuICBpZiAodHlwZW9mIG4gPT09IFwidW5kZWZpbmVkXCIpIHtcbiAgICBuID0gMDtcbiAgfVxuICBpZiAoc3RhdGUuc2NvcGVzLmxlbmd0aCA8PSBuKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgcmV0dXJuIHN0YXRlLnNjb3Blc1tzdGF0ZS5zY29wZXMubGVuZ3RoIC0gKG4gKyAxKV07XG59XG5cbi8vIHRva2VuaXplcnNcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIC8vIEhhbmRsZSBtdWx0aWxpbmUgY29tbWVudHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgnIz0nLCBmYWxzZSkpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ29tbWVudDtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cblxuICAvLyBIYW5kbGUgc2NvcGUgY2hhbmdlc1xuICB2YXIgbGVhdmluZ0V4cHIgPSBzdGF0ZS5sZWF2aW5nRXhwcjtcbiAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgIGxlYXZpbmdFeHByID0gZmFsc2U7XG4gIH1cbiAgc3RhdGUubGVhdmluZ0V4cHIgPSBmYWxzZTtcbiAgaWYgKGxlYXZpbmdFeHByKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXicrLykpIHtcbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfVxuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goL1xcLns0LH0vKSkge1xuICAgIHJldHVybiBcImVycm9yXCI7XG4gIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9cXC57MSwzfS8pKSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpO1xuXG4gIC8vIEhhbmRsZSBzaW5nbGUgbGluZSBjb21tZW50c1xuICBpZiAoY2ggPT09ICcjJykge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKGNoID09PSAnWycpIHtcbiAgICBzdGF0ZS5zY29wZXMucHVzaCgnWycpO1xuICAgIHN0YXRlLm5lc3RlZEFycmF5cysrO1xuICB9XG4gIGlmIChjaCA9PT0gJygnKSB7XG4gICAgc3RhdGUuc2NvcGVzLnB1c2goJygnKTtcbiAgICBzdGF0ZS5uZXN0ZWRHZW5lcmF0b3JzKys7XG4gIH1cbiAgaWYgKGluQXJyYXkoc3RhdGUpICYmIGNoID09PSAnXScpIHtcbiAgICB3aGlsZSAoc3RhdGUuc2NvcGVzLmxlbmd0aCAmJiBjdXJyZW50U2NvcGUoc3RhdGUpICE9PSBcIltcIikge1xuICAgICAgc3RhdGUuc2NvcGVzLnBvcCgpO1xuICAgIH1cbiAgICBzdGF0ZS5zY29wZXMucG9wKCk7XG4gICAgc3RhdGUubmVzdGVkQXJyYXlzLS07XG4gICAgc3RhdGUubGVhdmluZ0V4cHIgPSB0cnVlO1xuICB9XG4gIGlmIChpbkdlbmVyYXRvcihzdGF0ZSkgJiYgY2ggPT09ICcpJykge1xuICAgIHdoaWxlIChzdGF0ZS5zY29wZXMubGVuZ3RoICYmIGN1cnJlbnRTY29wZShzdGF0ZSkgIT09IFwiKFwiKSB7XG4gICAgICBzdGF0ZS5zY29wZXMucG9wKCk7XG4gICAgfVxuICAgIHN0YXRlLnNjb3Blcy5wb3AoKTtcbiAgICBzdGF0ZS5uZXN0ZWRHZW5lcmF0b3JzLS07XG4gICAgc3RhdGUubGVhdmluZ0V4cHIgPSB0cnVlO1xuICB9XG4gIGlmIChpbkFycmF5KHN0YXRlKSkge1xuICAgIGlmIChzdGF0ZS5sYXN0VG9rZW4gPT0gXCJlbmRcIiAmJiBzdHJlYW0ubWF0Y2goJzonKSkge1xuICAgICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgnZW5kJykpIHtcbiAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgIH1cbiAgfVxuICB2YXIgbWF0Y2g7XG4gIGlmIChtYXRjaCA9IHN0cmVhbS5tYXRjaChvcGVuZXJzLCBmYWxzZSkpIHtcbiAgICBzdGF0ZS5zY29wZXMucHVzaChtYXRjaFswXSk7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChjbG9zZXJzLCBmYWxzZSkpIHtcbiAgICBzdGF0ZS5zY29wZXMucG9wKCk7XG4gIH1cblxuICAvLyBIYW5kbGUgdHlwZSBhbm5vdGF0aW9uc1xuICBpZiAoc3RyZWFtLm1hdGNoKC9eOjooPyFbOlxcJF0pLykpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQW5ub3RhdGlvbjtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cblxuICAvLyBIYW5kbGUgc3ltYm9sc1xuICBpZiAoIWxlYXZpbmdFeHByICYmIChzdHJlYW0ubWF0Y2goc3ltYm9sKSB8fCBzdHJlYW0ubWF0Y2goc3ltYm9sT3BlcmF0b3JzKSkpIHtcbiAgICByZXR1cm4gXCJidWlsdGluXCI7XG4gIH1cblxuICAvLyBIYW5kbGUgcGFyYW1ldHJpYyB0eXBlc1xuICAvL2lmIChzdHJlYW0ubWF0Y2goL157W159XSp9KD89XFwoKS8pKSB7XG4gIC8vICByZXR1cm4gXCJidWlsdGluXCI7XG4gIC8vfVxuXG4gIC8vIEhhbmRsZSBvcGVyYXRvcnMgYW5kIERlbGltaXRlcnNcbiAgaWYgKHN0cmVhbS5tYXRjaChvcGVyYXRvcnMpKSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuXG4gIC8vIEhhbmRsZSBOdW1iZXIgTGl0ZXJhbHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXlxcLj9cXGQvLCBmYWxzZSkpIHtcbiAgICB2YXIgaW1NYXRjaGVyID0gUmVnRXhwKC9eaW1cXGIvKTtcbiAgICB2YXIgbnVtYmVyTGl0ZXJhbCA9IGZhbHNlO1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL14weFxcLlswLTlhLWZfXStwW1xcK1xcLV0/W19cXGRdKy9pKSkge1xuICAgICAgbnVtYmVyTGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIC8vIEludGVnZXJzXG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXjB4WzAtOWEtZl9dKy9pKSkge1xuICAgICAgbnVtYmVyTGl0ZXJhbCA9IHRydWU7XG4gICAgfSAvLyBIZXhcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eMGJbMDFfXSsvaSkpIHtcbiAgICAgIG51bWJlckxpdGVyYWwgPSB0cnVlO1xuICAgIH0gLy8gQmluYXJ5XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXjBvWzAtN19dKy9pKSkge1xuICAgICAgbnVtYmVyTGl0ZXJhbCA9IHRydWU7XG4gICAgfSAvLyBPY3RhbFxuICAgIC8vIEZsb2F0c1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL14oPzooPzpcXGRbX1xcZF0qKT9cXC4oPyFcXC4pKD86XFxkW19cXGRdKik/fFxcZFtfXFxkXSpcXC4oPyFcXC4pKD86XFxkW19cXGRdKikpPyhbRWVmXVtcXCtcXC1dP1tfXFxkXSspPy9pKSkge1xuICAgICAgbnVtYmVyTGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goL15cXGRbX1xcZF0qKGVbXFwrXFwtXT9cXGQrKT8vaSkpIHtcbiAgICAgIG51bWJlckxpdGVyYWwgPSB0cnVlO1xuICAgIH0gLy8gRGVjaW1hbFxuICAgIGlmIChudW1iZXJMaXRlcmFsKSB7XG4gICAgICAvLyBJbnRlZ2VyIGxpdGVyYWxzIG1heSBiZSBcImxvbmdcIlxuICAgICAgc3RyZWFtLm1hdGNoKGltTWF0Y2hlcik7XG4gICAgICBzdGF0ZS5sZWF2aW5nRXhwciA9IHRydWU7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gIH1cblxuICAvLyBIYW5kbGUgQ2hhcnNcbiAgaWYgKHN0cmVhbS5tYXRjaChcIidcIikpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ2hhcjtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cblxuICAvLyBIYW5kbGUgU3RyaW5nc1xuICBpZiAoc3RyZWFtLm1hdGNoKHN0cmluZ1ByZWZpeGVzKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmdGYWN0b3J5KHN0cmVhbS5jdXJyZW50KCkpO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKG1hY3JvKSB8fCBzdHJlYW0ubWF0Y2gobWFjcm9PcGVyYXRvcnMpKSB7XG4gICAgcmV0dXJuIFwibWV0YVwiO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goZGVsaW1pdGVycykpIHtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGtleXdvcmRzKSkge1xuICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGJ1aWx0aW5zKSkge1xuICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgfVxuICB2YXIgaXNEZWZpbml0aW9uID0gc3RhdGUuaXNEZWZpbml0aW9uIHx8IHN0YXRlLmxhc3RUb2tlbiA9PSBcImZ1bmN0aW9uXCIgfHwgc3RhdGUubGFzdFRva2VuID09IFwibWFjcm9cIiB8fCBzdGF0ZS5sYXN0VG9rZW4gPT0gXCJ0eXBlXCIgfHwgc3RhdGUubGFzdFRva2VuID09IFwic3RydWN0XCIgfHwgc3RhdGUubGFzdFRva2VuID09IFwiaW1tdXRhYmxlXCI7XG4gIGlmIChzdHJlYW0ubWF0Y2goaWRlbnRpZmllcnMpKSB7XG4gICAgaWYgKGlzRGVmaW5pdGlvbikge1xuICAgICAgaWYgKHN0cmVhbS5wZWVrKCkgPT09ICcuJykge1xuICAgICAgICBzdGF0ZS5pc0RlZmluaXRpb24gPSB0cnVlO1xuICAgICAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICAgICAgfVxuICAgICAgc3RhdGUuaXNEZWZpbml0aW9uID0gZmFsc2U7XG4gICAgICByZXR1cm4gXCJkZWZcIjtcbiAgICB9XG4gICAgc3RhdGUubGVhdmluZ0V4cHIgPSB0cnVlO1xuICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gIH1cblxuICAvLyBIYW5kbGUgbm9uLWRldGVjdGVkIGl0ZW1zXG4gIHN0cmVhbS5uZXh0KCk7XG4gIHJldHVybiBcImVycm9yXCI7XG59XG5mdW5jdGlvbiB0b2tlbkFubm90YXRpb24oc3RyZWFtLCBzdGF0ZSkge1xuICBzdHJlYW0ubWF0Y2goLy4qPyg/PVssO3t9KCk9XFxzXXwkKS8pO1xuICBpZiAoc3RyZWFtLm1hdGNoKCd7JykpIHtcbiAgICBzdGF0ZS5uZXN0ZWRQYXJhbWV0ZXJzKys7XG4gIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKCd9JykgJiYgc3RhdGUubmVzdGVkUGFyYW1ldGVycyA+IDApIHtcbiAgICBzdGF0ZS5uZXN0ZWRQYXJhbWV0ZXJzLS07XG4gIH1cbiAgaWYgKHN0YXRlLm5lc3RlZFBhcmFtZXRlcnMgPiAwKSB7XG4gICAgc3RyZWFtLm1hdGNoKC8uKj8oPz17fH0pLykgfHwgc3RyZWFtLm5leHQoKTtcbiAgfSBlbHNlIGlmIChzdGF0ZS5uZXN0ZWRQYXJhbWV0ZXJzID09IDApIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgfVxuICByZXR1cm4gXCJidWlsdGluXCI7XG59XG5mdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKCcjPScpKSB7XG4gICAgc3RhdGUubmVzdGVkQ29tbWVudHMrKztcbiAgfVxuICBpZiAoIXN0cmVhbS5tYXRjaCgvLio/KD89KCM9fD0jKSkvKSkge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKCc9IycpKSB7XG4gICAgc3RhdGUubmVzdGVkQ29tbWVudHMtLTtcbiAgICBpZiAoc3RhdGUubmVzdGVkQ29tbWVudHMgPT0gMCkgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5DaGFyKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGlzQ2hhciA9IGZhbHNlLFxuICAgIG1hdGNoO1xuICBpZiAoc3RyZWFtLm1hdGNoKGNoYXJzKSkge1xuICAgIGlzQ2hhciA9IHRydWU7XG4gIH0gZWxzZSBpZiAobWF0Y2ggPSBzdHJlYW0ubWF0Y2goL1xcXFx1KFthLWYwLTldezEsNH0pKD89JykvaSkpIHtcbiAgICB2YXIgdmFsdWUgPSBwYXJzZUludChtYXRjaFsxXSwgMTYpO1xuICAgIGlmICh2YWx1ZSA8PSA1NTI5NSB8fCB2YWx1ZSA+PSA1NzM0NCkge1xuICAgICAgLy8gKFUrMCxVK0Q3RkYpLCAoVStFMDAwLFUrRkZGRilcbiAgICAgIGlzQ2hhciA9IHRydWU7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgfSBlbHNlIGlmIChtYXRjaCA9IHN0cmVhbS5tYXRjaCgvXFxcXFUoW0EtRmEtZjAtOV17NSw4fSkoPz0nKS8pKSB7XG4gICAgdmFyIHZhbHVlID0gcGFyc2VJbnQobWF0Y2hbMV0sIDE2KTtcbiAgICBpZiAodmFsdWUgPD0gMTExNDExMSkge1xuICAgICAgLy8gVSsxMEZGRkZcbiAgICAgIGlzQ2hhciA9IHRydWU7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgfVxuICBpZiAoaXNDaGFyKSB7XG4gICAgc3RhdGUubGVhdmluZ0V4cHIgPSB0cnVlO1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9XG4gIGlmICghc3RyZWFtLm1hdGNoKC9eW14nXSsoPz0nKS8pKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goXCInXCIpKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gIH1cbiAgcmV0dXJuIFwiZXJyb3JcIjtcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nRmFjdG9yeShkZWxpbWl0ZXIpIHtcbiAgaWYgKGRlbGltaXRlci5zdWJzdHIoLTMpID09PSAnXCJcIlwiJykge1xuICAgIGRlbGltaXRlciA9ICdcIlwiXCInO1xuICB9IGVsc2UgaWYgKGRlbGltaXRlci5zdWJzdHIoLTEpID09PSAnXCInKSB7XG4gICAgZGVsaW1pdGVyID0gJ1wiJztcbiAgfVxuICBmdW5jdGlvbiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoJ1xcXFwnKSkge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaChkZWxpbWl0ZXIpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIHN0YXRlLmxlYXZpbmdFeHByID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdHJlYW0uZWF0KC9bYFwiXS8pO1xuICAgIH1cbiAgICBzdHJlYW0uZWF0V2hpbGUoL1teXFxcXGBcIl0vKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfVxuICByZXR1cm4gdG9rZW5TdHJpbmc7XG59XG5leHBvcnQgY29uc3QganVsaWEgPSB7XG4gIG5hbWU6IFwianVsaWFcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgc2NvcGVzOiBbXSxcbiAgICAgIGxhc3RUb2tlbjogbnVsbCxcbiAgICAgIGxlYXZpbmdFeHByOiBmYWxzZSxcbiAgICAgIGlzRGVmaW5pdGlvbjogZmFsc2UsXG4gICAgICBuZXN0ZWRBcnJheXM6IDAsXG4gICAgICBuZXN0ZWRDb21tZW50czogMCxcbiAgICAgIG5lc3RlZEdlbmVyYXRvcnM6IDAsXG4gICAgICBuZXN0ZWRQYXJhbWV0ZXJzOiAwLFxuICAgICAgZmlyc3RQYXJlblBvczogLTFcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB2YXIgY3VycmVudCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgaWYgKGN1cnJlbnQgJiYgc3R5bGUpIHtcbiAgICAgIHN0YXRlLmxhc3RUb2tlbiA9IGN1cnJlbnQ7XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICB2YXIgZGVsdGEgPSAwO1xuICAgIGlmICh0ZXh0QWZ0ZXIgPT09ICddJyB8fCB0ZXh0QWZ0ZXIgPT09ICcpJyB8fCAvXmVuZFxcYi8udGVzdCh0ZXh0QWZ0ZXIpIHx8IC9eZWxzZS8udGVzdCh0ZXh0QWZ0ZXIpIHx8IC9eY2F0Y2hcXGIvLnRlc3QodGV4dEFmdGVyKSB8fCAvXmVsc2VpZlxcYi8udGVzdCh0ZXh0QWZ0ZXIpIHx8IC9eZmluYWxseS8udGVzdCh0ZXh0QWZ0ZXIpKSB7XG4gICAgICBkZWx0YSA9IC0xO1xuICAgIH1cbiAgICByZXR1cm4gKHN0YXRlLnNjb3Blcy5sZW5ndGggKyBkZWx0YSkgKiBjeC51bml0O1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccyooZW5kfGVsc2V8Y2F0Y2h8ZmluYWxseSlcXGIkLyxcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIiNcIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiIz1cIixcbiAgICAgICAgY2xvc2U6IFwiPSNcIlxuICAgICAgfVxuICAgIH0sXG4gICAgY2xvc2VCcmFja2V0czoge1xuICAgICAgYnJhY2tldHM6IFtcIihcIiwgXCJbXCIsIFwie1wiLCAnXCInXVxuICAgIH0sXG4gICAgYXV0b2NvbXBsZXRlOiBrZXl3b3Jkc0xpc3QuY29uY2F0KGJ1aWx0aW5zTGlzdClcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9