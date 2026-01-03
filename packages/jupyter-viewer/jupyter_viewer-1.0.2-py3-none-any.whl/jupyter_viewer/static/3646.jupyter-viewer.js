"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3646],{

/***/ 63646
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   cython: () => (/* binding */ cython)
/* harmony export */ });
/* unused harmony exports mkPython, python */
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b");
}
var wordOperators = wordRegexp(["and", "or", "not", "is"]);
var commonKeywords = ["as", "assert", "break", "class", "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "lambda", "pass", "raise", "return", "try", "while", "with", "yield", "in", "False", "True"];
var commonBuiltins = ["abs", "all", "any", "bin", "bool", "bytearray", "callable", "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir", "divmod", "enumerate", "eval", "filter", "float", "format", "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance", "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview", "min", "next", "object", "oct", "open", "ord", "pow", "property", "range", "repr", "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__", "NotImplemented", "Ellipsis", "__debug__"];
function top(state) {
  return state.scopes[state.scopes.length - 1];
}
function mkPython(parserConf) {
  var ERRORCLASS = "error";
  var delimiters = parserConf.delimiters || parserConf.singleDelimiters || /^[\(\)\[\]\{\}@,:`=;\.\\]/;
  //               (Backwards-compatibility with old, cumbersome config system)
  var operators = [parserConf.singleOperators, parserConf.doubleOperators, parserConf.doubleDelimiters, parserConf.tripleDelimiters, parserConf.operators || /^([-+*/%\/&|^]=?|[<>=]+|\/\/=?|\*\*=?|!=|[~!@]|\.\.\.)/];
  for (var i = 0; i < operators.length; i++) if (!operators[i]) operators.splice(i--, 1);
  var hangingIndent = parserConf.hangingIndent;
  var myKeywords = commonKeywords,
    myBuiltins = commonBuiltins;
  if (parserConf.extra_keywords != undefined) myKeywords = myKeywords.concat(parserConf.extra_keywords);
  if (parserConf.extra_builtins != undefined) myBuiltins = myBuiltins.concat(parserConf.extra_builtins);
  var py3 = !(parserConf.version && Number(parserConf.version) < 3);
  if (py3) {
    // since http://legacy.python.org/dev/peps/pep-0465/ @ is also an operator
    var identifiers = parserConf.identifiers || /^[_A-Za-z\u00A1-\uFFFF][_A-Za-z0-9\u00A1-\uFFFF]*/;
    myKeywords = myKeywords.concat(["nonlocal", "None", "aiter", "anext", "async", "await", "breakpoint", "match", "case"]);
    myBuiltins = myBuiltins.concat(["ascii", "bytes", "exec", "print"]);
    var stringPrefixes = new RegExp("^(([rbuf]|(br)|(rb)|(fr)|(rf))?('{3}|\"{3}|['\"]))", "i");
  } else {
    var identifiers = parserConf.identifiers || /^[_A-Za-z][_A-Za-z0-9]*/;
    myKeywords = myKeywords.concat(["exec", "print"]);
    myBuiltins = myBuiltins.concat(["apply", "basestring", "buffer", "cmp", "coerce", "execfile", "file", "intern", "long", "raw_input", "reduce", "reload", "unichr", "unicode", "xrange", "None"]);
    var stringPrefixes = new RegExp("^(([rubf]|(ur)|(br))?('{3}|\"{3}|['\"]))", "i");
  }
  var keywords = wordRegexp(myKeywords);
  var builtins = wordRegexp(myBuiltins);

  // tokenizers
  function tokenBase(stream, state) {
    var sol = stream.sol() && state.lastToken != "\\";
    if (sol) state.indent = stream.indentation();
    // Handle scope changes
    if (sol && top(state).type == "py") {
      var scopeOffset = top(state).offset;
      if (stream.eatSpace()) {
        var lineOffset = stream.indentation();
        if (lineOffset > scopeOffset) pushPyScope(stream, state);else if (lineOffset < scopeOffset && dedent(stream, state) && stream.peek() != "#") state.errorToken = true;
        return null;
      } else {
        var style = tokenBaseInner(stream, state);
        if (scopeOffset > 0 && dedent(stream, state)) style += " " + ERRORCLASS;
        return style;
      }
    }
    return tokenBaseInner(stream, state);
  }
  function tokenBaseInner(stream, state, inFormat) {
    if (stream.eatSpace()) return null;

    // Handle Comments
    if (!inFormat && stream.match(/^#.*/)) return "comment";

    // Handle Number Literals
    if (stream.match(/^[0-9\.]/, false)) {
      var floatLiteral = false;
      // Floats
      if (stream.match(/^[\d_]*\.\d+(e[\+\-]?\d+)?/i)) {
        floatLiteral = true;
      }
      if (stream.match(/^[\d_]+\.\d*/)) {
        floatLiteral = true;
      }
      if (stream.match(/^\.\d+/)) {
        floatLiteral = true;
      }
      if (floatLiteral) {
        // Float literals may be "imaginary"
        stream.eat(/J/i);
        return "number";
      }
      // Integers
      var intLiteral = false;
      // Hex
      if (stream.match(/^0x[0-9a-f_]+/i)) intLiteral = true;
      // Binary
      if (stream.match(/^0b[01_]+/i)) intLiteral = true;
      // Octal
      if (stream.match(/^0o[0-7_]+/i)) intLiteral = true;
      // Decimal
      if (stream.match(/^[1-9][\d_]*(e[\+\-]?[\d_]+)?/)) {
        // Decimal literals may be "imaginary"
        stream.eat(/J/i);
        // TODO - Can you have imaginary longs?
        intLiteral = true;
      }
      // Zero by itself with no other piece of number.
      if (stream.match(/^0(?![\dx])/i)) intLiteral = true;
      if (intLiteral) {
        // Integer literals may be "long"
        stream.eat(/L/i);
        return "number";
      }
    }

    // Handle Strings
    if (stream.match(stringPrefixes)) {
      var isFmtString = stream.current().toLowerCase().indexOf('f') !== -1;
      if (!isFmtString) {
        state.tokenize = tokenStringFactory(stream.current(), state.tokenize);
        return state.tokenize(stream, state);
      } else {
        state.tokenize = formatStringFactory(stream.current(), state.tokenize);
        return state.tokenize(stream, state);
      }
    }
    for (var i = 0; i < operators.length; i++) if (stream.match(operators[i])) return "operator";
    if (stream.match(delimiters)) return "punctuation";
    if (state.lastToken == "." && stream.match(identifiers)) return "property";
    if (stream.match(keywords) || stream.match(wordOperators)) return "keyword";
    if (stream.match(builtins)) return "builtin";
    if (stream.match(/^(self|cls)\b/)) return "self";
    if (stream.match(identifiers)) {
      if (state.lastToken == "def" || state.lastToken == "class") return "def";
      return "variable";
    }

    // Handle non-detected items
    stream.next();
    return inFormat ? null : ERRORCLASS;
  }
  function formatStringFactory(delimiter, tokenOuter) {
    while ("rubf".indexOf(delimiter.charAt(0).toLowerCase()) >= 0) delimiter = delimiter.substr(1);
    var singleline = delimiter.length == 1;
    var OUTCLASS = "string";
    function tokenNestedExpr(depth) {
      return function (stream, state) {
        var inner = tokenBaseInner(stream, state, true);
        if (inner == "punctuation") {
          if (stream.current() == "{") {
            state.tokenize = tokenNestedExpr(depth + 1);
          } else if (stream.current() == "}") {
            if (depth > 1) state.tokenize = tokenNestedExpr(depth - 1);else state.tokenize = tokenString;
          }
        }
        return inner;
      };
    }
    function tokenString(stream, state) {
      while (!stream.eol()) {
        stream.eatWhile(/[^'"\{\}\\]/);
        if (stream.eat("\\")) {
          stream.next();
          if (singleline && stream.eol()) return OUTCLASS;
        } else if (stream.match(delimiter)) {
          state.tokenize = tokenOuter;
          return OUTCLASS;
        } else if (stream.match('{{')) {
          // ignore {{ in f-str
          return OUTCLASS;
        } else if (stream.match('{', false)) {
          // switch to nested mode
          state.tokenize = tokenNestedExpr(0);
          if (stream.current()) return OUTCLASS;else return state.tokenize(stream, state);
        } else if (stream.match('}}')) {
          return OUTCLASS;
        } else if (stream.match('}')) {
          // single } in f-string is an error
          return ERRORCLASS;
        } else {
          stream.eat(/['"]/);
        }
      }
      if (singleline) {
        if (parserConf.singleLineStringErrors) return ERRORCLASS;else state.tokenize = tokenOuter;
      }
      return OUTCLASS;
    }
    tokenString.isString = true;
    return tokenString;
  }
  function tokenStringFactory(delimiter, tokenOuter) {
    while ("rubf".indexOf(delimiter.charAt(0).toLowerCase()) >= 0) delimiter = delimiter.substr(1);
    var singleline = delimiter.length == 1;
    var OUTCLASS = "string";
    function tokenString(stream, state) {
      while (!stream.eol()) {
        stream.eatWhile(/[^'"\\]/);
        if (stream.eat("\\")) {
          stream.next();
          if (singleline && stream.eol()) return OUTCLASS;
        } else if (stream.match(delimiter)) {
          state.tokenize = tokenOuter;
          return OUTCLASS;
        } else {
          stream.eat(/['"]/);
        }
      }
      if (singleline) {
        if (parserConf.singleLineStringErrors) return ERRORCLASS;else state.tokenize = tokenOuter;
      }
      return OUTCLASS;
    }
    tokenString.isString = true;
    return tokenString;
  }
  function pushPyScope(stream, state) {
    while (top(state).type != "py") state.scopes.pop();
    state.scopes.push({
      offset: top(state).offset + stream.indentUnit,
      type: "py",
      align: null
    });
  }
  function pushBracketScope(stream, state, type) {
    var align = stream.match(/^[\s\[\{\(]*(?:#|$)/, false) ? null : stream.column() + 1;
    state.scopes.push({
      offset: state.indent + (hangingIndent || stream.indentUnit),
      type: type,
      align: align
    });
  }
  function dedent(stream, state) {
    var indented = stream.indentation();
    while (state.scopes.length > 1 && top(state).offset > indented) {
      if (top(state).type != "py") return true;
      state.scopes.pop();
    }
    return top(state).offset != indented;
  }
  function tokenLexer(stream, state) {
    if (stream.sol()) {
      state.beginningOfLine = true;
      state.dedent = false;
    }
    var style = state.tokenize(stream, state);
    var current = stream.current();

    // Handle decorators
    if (state.beginningOfLine && current == "@") return stream.match(identifiers, false) ? "meta" : py3 ? "operator" : ERRORCLASS;
    if (/\S/.test(current)) state.beginningOfLine = false;
    if ((style == "variable" || style == "builtin") && state.lastToken == "meta") style = "meta";

    // Handle scope changes.
    if (current == "pass" || current == "return") state.dedent = true;
    if (current == "lambda") state.lambda = true;
    if (current == ":" && !state.lambda && top(state).type == "py" && stream.match(/^\s*(?:#|$)/, false)) pushPyScope(stream, state);
    if (current.length == 1 && !/string|comment/.test(style)) {
      var delimiter_index = "[({".indexOf(current);
      if (delimiter_index != -1) pushBracketScope(stream, state, "])}".slice(delimiter_index, delimiter_index + 1));
      delimiter_index = "])}".indexOf(current);
      if (delimiter_index != -1) {
        if (top(state).type == current) state.indent = state.scopes.pop().offset - (hangingIndent || stream.indentUnit);else return ERRORCLASS;
      }
    }
    if (state.dedent && stream.eol() && top(state).type == "py" && state.scopes.length > 1) state.scopes.pop();
    return style;
  }
  return {
    name: "python",
    startState: function () {
      return {
        tokenize: tokenBase,
        scopes: [{
          offset: 0,
          type: "py",
          align: null
        }],
        indent: 0,
        lastToken: null,
        lambda: false,
        dedent: 0
      };
    },
    token: function (stream, state) {
      var addErr = state.errorToken;
      if (addErr) state.errorToken = false;
      var style = tokenLexer(stream, state);
      if (style && style != "comment") state.lastToken = style == "keyword" || style == "punctuation" ? stream.current() : style;
      if (style == "punctuation") style = null;
      if (stream.eol() && state.lambda) state.lambda = false;
      return addErr ? ERRORCLASS : style;
    },
    indent: function (state, textAfter, cx) {
      if (state.tokenize != tokenBase) return state.tokenize.isString ? null : 0;
      var scope = top(state);
      var closing = scope.type == textAfter.charAt(0) || scope.type == "py" && !state.dedent && /^(else:|elif |except |finally:)/.test(textAfter);
      if (scope.align != null) return scope.align - (closing ? 1 : 0);else return scope.offset - (closing ? hangingIndent || cx.unit : 0);
    },
    languageData: {
      autocomplete: commonKeywords.concat(commonBuiltins).concat(["exec", "print"]),
      indentOnInput: /^\s*([\}\]\)]|else:|elif |except |finally:)$/,
      commentTokens: {
        line: "#"
      },
      closeBrackets: {
        brackets: ["(", "[", "{", "'", '"', "'''", '"""']
      }
    }
  };
}
;
var words = function (str) {
  return str.split(" ");
};
const python = mkPython({});
const cython = mkPython({
  extra_keywords: words("by cdef cimport cpdef ctypedef enum except " + "extern gil include nogil property public " + "readonly struct union DEF IF ELIF ELSE")
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzY0Ni5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3B5dGhvbi5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIpO1xufVxudmFyIHdvcmRPcGVyYXRvcnMgPSB3b3JkUmVnZXhwKFtcImFuZFwiLCBcIm9yXCIsIFwibm90XCIsIFwiaXNcIl0pO1xudmFyIGNvbW1vbktleXdvcmRzID0gW1wiYXNcIiwgXCJhc3NlcnRcIiwgXCJicmVha1wiLCBcImNsYXNzXCIsIFwiY29udGludWVcIiwgXCJkZWZcIiwgXCJkZWxcIiwgXCJlbGlmXCIsIFwiZWxzZVwiLCBcImV4Y2VwdFwiLCBcImZpbmFsbHlcIiwgXCJmb3JcIiwgXCJmcm9tXCIsIFwiZ2xvYmFsXCIsIFwiaWZcIiwgXCJpbXBvcnRcIiwgXCJsYW1iZGFcIiwgXCJwYXNzXCIsIFwicmFpc2VcIiwgXCJyZXR1cm5cIiwgXCJ0cnlcIiwgXCJ3aGlsZVwiLCBcIndpdGhcIiwgXCJ5aWVsZFwiLCBcImluXCIsIFwiRmFsc2VcIiwgXCJUcnVlXCJdO1xudmFyIGNvbW1vbkJ1aWx0aW5zID0gW1wiYWJzXCIsIFwiYWxsXCIsIFwiYW55XCIsIFwiYmluXCIsIFwiYm9vbFwiLCBcImJ5dGVhcnJheVwiLCBcImNhbGxhYmxlXCIsIFwiY2hyXCIsIFwiY2xhc3NtZXRob2RcIiwgXCJjb21waWxlXCIsIFwiY29tcGxleFwiLCBcImRlbGF0dHJcIiwgXCJkaWN0XCIsIFwiZGlyXCIsIFwiZGl2bW9kXCIsIFwiZW51bWVyYXRlXCIsIFwiZXZhbFwiLCBcImZpbHRlclwiLCBcImZsb2F0XCIsIFwiZm9ybWF0XCIsIFwiZnJvemVuc2V0XCIsIFwiZ2V0YXR0clwiLCBcImdsb2JhbHNcIiwgXCJoYXNhdHRyXCIsIFwiaGFzaFwiLCBcImhlbHBcIiwgXCJoZXhcIiwgXCJpZFwiLCBcImlucHV0XCIsIFwiaW50XCIsIFwiaXNpbnN0YW5jZVwiLCBcImlzc3ViY2xhc3NcIiwgXCJpdGVyXCIsIFwibGVuXCIsIFwibGlzdFwiLCBcImxvY2Fsc1wiLCBcIm1hcFwiLCBcIm1heFwiLCBcIm1lbW9yeXZpZXdcIiwgXCJtaW5cIiwgXCJuZXh0XCIsIFwib2JqZWN0XCIsIFwib2N0XCIsIFwib3BlblwiLCBcIm9yZFwiLCBcInBvd1wiLCBcInByb3BlcnR5XCIsIFwicmFuZ2VcIiwgXCJyZXByXCIsIFwicmV2ZXJzZWRcIiwgXCJyb3VuZFwiLCBcInNldFwiLCBcInNldGF0dHJcIiwgXCJzbGljZVwiLCBcInNvcnRlZFwiLCBcInN0YXRpY21ldGhvZFwiLCBcInN0clwiLCBcInN1bVwiLCBcInN1cGVyXCIsIFwidHVwbGVcIiwgXCJ0eXBlXCIsIFwidmFyc1wiLCBcInppcFwiLCBcIl9faW1wb3J0X19cIiwgXCJOb3RJbXBsZW1lbnRlZFwiLCBcIkVsbGlwc2lzXCIsIFwiX19kZWJ1Z19fXCJdO1xuZnVuY3Rpb24gdG9wKHN0YXRlKSB7XG4gIHJldHVybiBzdGF0ZS5zY29wZXNbc3RhdGUuc2NvcGVzLmxlbmd0aCAtIDFdO1xufVxuZXhwb3J0IGZ1bmN0aW9uIG1rUHl0aG9uKHBhcnNlckNvbmYpIHtcbiAgdmFyIEVSUk9SQ0xBU1MgPSBcImVycm9yXCI7XG4gIHZhciBkZWxpbWl0ZXJzID0gcGFyc2VyQ29uZi5kZWxpbWl0ZXJzIHx8IHBhcnNlckNvbmYuc2luZ2xlRGVsaW1pdGVycyB8fCAvXltcXChcXClcXFtcXF1cXHtcXH1ALDpgPTtcXC5cXFxcXS87XG4gIC8vICAgICAgICAgICAgICAgKEJhY2t3YXJkcy1jb21wYXRpYmlsaXR5IHdpdGggb2xkLCBjdW1iZXJzb21lIGNvbmZpZyBzeXN0ZW0pXG4gIHZhciBvcGVyYXRvcnMgPSBbcGFyc2VyQ29uZi5zaW5nbGVPcGVyYXRvcnMsIHBhcnNlckNvbmYuZG91YmxlT3BlcmF0b3JzLCBwYXJzZXJDb25mLmRvdWJsZURlbGltaXRlcnMsIHBhcnNlckNvbmYudHJpcGxlRGVsaW1pdGVycywgcGFyc2VyQ29uZi5vcGVyYXRvcnMgfHwgL14oWy0rKi8lXFwvJnxeXT0/fFs8Pj1dK3xcXC9cXC89P3xcXCpcXCo9P3whPXxbfiFAXXxcXC5cXC5cXC4pL107XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgb3BlcmF0b3JzLmxlbmd0aDsgaSsrKSBpZiAoIW9wZXJhdG9yc1tpXSkgb3BlcmF0b3JzLnNwbGljZShpLS0sIDEpO1xuICB2YXIgaGFuZ2luZ0luZGVudCA9IHBhcnNlckNvbmYuaGFuZ2luZ0luZGVudDtcbiAgdmFyIG15S2V5d29yZHMgPSBjb21tb25LZXl3b3JkcyxcbiAgICBteUJ1aWx0aW5zID0gY29tbW9uQnVpbHRpbnM7XG4gIGlmIChwYXJzZXJDb25mLmV4dHJhX2tleXdvcmRzICE9IHVuZGVmaW5lZCkgbXlLZXl3b3JkcyA9IG15S2V5d29yZHMuY29uY2F0KHBhcnNlckNvbmYuZXh0cmFfa2V5d29yZHMpO1xuICBpZiAocGFyc2VyQ29uZi5leHRyYV9idWlsdGlucyAhPSB1bmRlZmluZWQpIG15QnVpbHRpbnMgPSBteUJ1aWx0aW5zLmNvbmNhdChwYXJzZXJDb25mLmV4dHJhX2J1aWx0aW5zKTtcbiAgdmFyIHB5MyA9ICEocGFyc2VyQ29uZi52ZXJzaW9uICYmIE51bWJlcihwYXJzZXJDb25mLnZlcnNpb24pIDwgMyk7XG4gIGlmIChweTMpIHtcbiAgICAvLyBzaW5jZSBodHRwOi8vbGVnYWN5LnB5dGhvbi5vcmcvZGV2L3BlcHMvcGVwLTA0NjUvIEAgaXMgYWxzbyBhbiBvcGVyYXRvclxuICAgIHZhciBpZGVudGlmaWVycyA9IHBhcnNlckNvbmYuaWRlbnRpZmllcnMgfHwgL15bX0EtWmEtelxcdTAwQTEtXFx1RkZGRl1bX0EtWmEtejAtOVxcdTAwQTEtXFx1RkZGRl0qLztcbiAgICBteUtleXdvcmRzID0gbXlLZXl3b3Jkcy5jb25jYXQoW1wibm9ubG9jYWxcIiwgXCJOb25lXCIsIFwiYWl0ZXJcIiwgXCJhbmV4dFwiLCBcImFzeW5jXCIsIFwiYXdhaXRcIiwgXCJicmVha3BvaW50XCIsIFwibWF0Y2hcIiwgXCJjYXNlXCJdKTtcbiAgICBteUJ1aWx0aW5zID0gbXlCdWlsdGlucy5jb25jYXQoW1wiYXNjaWlcIiwgXCJieXRlc1wiLCBcImV4ZWNcIiwgXCJwcmludFwiXSk7XG4gICAgdmFyIHN0cmluZ1ByZWZpeGVzID0gbmV3IFJlZ0V4cChcIl4oKFtyYnVmXXwoYnIpfChyYil8KGZyKXwocmYpKT8oJ3szfXxcXFwiezN9fFsnXFxcIl0pKVwiLCBcImlcIik7XG4gIH0gZWxzZSB7XG4gICAgdmFyIGlkZW50aWZpZXJzID0gcGFyc2VyQ29uZi5pZGVudGlmaWVycyB8fCAvXltfQS1aYS16XVtfQS1aYS16MC05XSovO1xuICAgIG15S2V5d29yZHMgPSBteUtleXdvcmRzLmNvbmNhdChbXCJleGVjXCIsIFwicHJpbnRcIl0pO1xuICAgIG15QnVpbHRpbnMgPSBteUJ1aWx0aW5zLmNvbmNhdChbXCJhcHBseVwiLCBcImJhc2VzdHJpbmdcIiwgXCJidWZmZXJcIiwgXCJjbXBcIiwgXCJjb2VyY2VcIiwgXCJleGVjZmlsZVwiLCBcImZpbGVcIiwgXCJpbnRlcm5cIiwgXCJsb25nXCIsIFwicmF3X2lucHV0XCIsIFwicmVkdWNlXCIsIFwicmVsb2FkXCIsIFwidW5pY2hyXCIsIFwidW5pY29kZVwiLCBcInhyYW5nZVwiLCBcIk5vbmVcIl0pO1xuICAgIHZhciBzdHJpbmdQcmVmaXhlcyA9IG5ldyBSZWdFeHAoXCJeKChbcnViZl18KHVyKXwoYnIpKT8oJ3szfXxcXFwiezN9fFsnXFxcIl0pKVwiLCBcImlcIik7XG4gIH1cbiAgdmFyIGtleXdvcmRzID0gd29yZFJlZ2V4cChteUtleXdvcmRzKTtcbiAgdmFyIGJ1aWx0aW5zID0gd29yZFJlZ2V4cChteUJ1aWx0aW5zKTtcblxuICAvLyB0b2tlbml6ZXJzXG4gIGZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIHNvbCA9IHN0cmVhbS5zb2woKSAmJiBzdGF0ZS5sYXN0VG9rZW4gIT0gXCJcXFxcXCI7XG4gICAgaWYgKHNvbCkgc3RhdGUuaW5kZW50ID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgLy8gSGFuZGxlIHNjb3BlIGNoYW5nZXNcbiAgICBpZiAoc29sICYmIHRvcChzdGF0ZSkudHlwZSA9PSBcInB5XCIpIHtcbiAgICAgIHZhciBzY29wZU9mZnNldCA9IHRvcChzdGF0ZSkub2Zmc2V0O1xuICAgICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICAgIHZhciBsaW5lT2Zmc2V0ID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgICAgIGlmIChsaW5lT2Zmc2V0ID4gc2NvcGVPZmZzZXQpIHB1c2hQeVNjb3BlKHN0cmVhbSwgc3RhdGUpO2Vsc2UgaWYgKGxpbmVPZmZzZXQgPCBzY29wZU9mZnNldCAmJiBkZWRlbnQoc3RyZWFtLCBzdGF0ZSkgJiYgc3RyZWFtLnBlZWsoKSAhPSBcIiNcIikgc3RhdGUuZXJyb3JUb2tlbiA9IHRydWU7XG4gICAgICAgIHJldHVybiBudWxsO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdmFyIHN0eWxlID0gdG9rZW5CYXNlSW5uZXIoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICAgIGlmIChzY29wZU9mZnNldCA+IDAgJiYgZGVkZW50KHN0cmVhbSwgc3RhdGUpKSBzdHlsZSArPSBcIiBcIiArIEVSUk9SQ0xBU1M7XG4gICAgICAgIHJldHVybiBzdHlsZTtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIHRva2VuQmFzZUlubmVyKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuQmFzZUlubmVyKHN0cmVhbSwgc3RhdGUsIGluRm9ybWF0KSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcblxuICAgIC8vIEhhbmRsZSBDb21tZW50c1xuICAgIGlmICghaW5Gb3JtYXQgJiYgc3RyZWFtLm1hdGNoKC9eIy4qLykpIHJldHVybiBcImNvbW1lbnRcIjtcblxuICAgIC8vIEhhbmRsZSBOdW1iZXIgTGl0ZXJhbHNcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eWzAtOVxcLl0vLCBmYWxzZSkpIHtcbiAgICAgIHZhciBmbG9hdExpdGVyYWwgPSBmYWxzZTtcbiAgICAgIC8vIEZsb2F0c1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXltcXGRfXSpcXC5cXGQrKGVbXFwrXFwtXT9cXGQrKT8vaSkpIHtcbiAgICAgICAgZmxvYXRMaXRlcmFsID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL15bXFxkX10rXFwuXFxkKi8pKSB7XG4gICAgICAgIGZsb2F0TGl0ZXJhbCA9IHRydWU7XG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eXFwuXFxkKy8pKSB7XG4gICAgICAgIGZsb2F0TGl0ZXJhbCA9IHRydWU7XG4gICAgICB9XG4gICAgICBpZiAoZmxvYXRMaXRlcmFsKSB7XG4gICAgICAgIC8vIEZsb2F0IGxpdGVyYWxzIG1heSBiZSBcImltYWdpbmFyeVwiXG4gICAgICAgIHN0cmVhbS5lYXQoL0ovaSk7XG4gICAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgICAgfVxuICAgICAgLy8gSW50ZWdlcnNcbiAgICAgIHZhciBpbnRMaXRlcmFsID0gZmFsc2U7XG4gICAgICAvLyBIZXhcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14weFswLTlhLWZfXSsvaSkpIGludExpdGVyYWwgPSB0cnVlO1xuICAgICAgLy8gQmluYXJ5XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eMGJbMDFfXSsvaSkpIGludExpdGVyYWwgPSB0cnVlO1xuICAgICAgLy8gT2N0YWxcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14wb1swLTdfXSsvaSkpIGludExpdGVyYWwgPSB0cnVlO1xuICAgICAgLy8gRGVjaW1hbFxuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXlsxLTldW1xcZF9dKihlW1xcK1xcLV0/W1xcZF9dKyk/LykpIHtcbiAgICAgICAgLy8gRGVjaW1hbCBsaXRlcmFscyBtYXkgYmUgXCJpbWFnaW5hcnlcIlxuICAgICAgICBzdHJlYW0uZWF0KC9KL2kpO1xuICAgICAgICAvLyBUT0RPIC0gQ2FuIHlvdSBoYXZlIGltYWdpbmFyeSBsb25ncz9cbiAgICAgICAgaW50TGl0ZXJhbCA9IHRydWU7XG4gICAgICB9XG4gICAgICAvLyBaZXJvIGJ5IGl0c2VsZiB3aXRoIG5vIG90aGVyIHBpZWNlIG9mIG51bWJlci5cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14wKD8hW1xcZHhdKS9pKSkgaW50TGl0ZXJhbCA9IHRydWU7XG4gICAgICBpZiAoaW50TGl0ZXJhbCkge1xuICAgICAgICAvLyBJbnRlZ2VyIGxpdGVyYWxzIG1heSBiZSBcImxvbmdcIlxuICAgICAgICBzdHJlYW0uZWF0KC9ML2kpO1xuICAgICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICAgIH1cbiAgICB9XG5cbiAgICAvLyBIYW5kbGUgU3RyaW5nc1xuICAgIGlmIChzdHJlYW0ubWF0Y2goc3RyaW5nUHJlZml4ZXMpKSB7XG4gICAgICB2YXIgaXNGbXRTdHJpbmcgPSBzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCkuaW5kZXhPZignZicpICE9PSAtMTtcbiAgICAgIGlmICghaXNGbXRTdHJpbmcpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZ0ZhY3Rvcnkoc3RyZWFtLmN1cnJlbnQoKSwgc3RhdGUudG9rZW5pemUpO1xuICAgICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IGZvcm1hdFN0cmluZ0ZhY3Rvcnkoc3RyZWFtLmN1cnJlbnQoKSwgc3RhdGUudG9rZW5pemUpO1xuICAgICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgfVxuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgb3BlcmF0b3JzLmxlbmd0aDsgaSsrKSBpZiAoc3RyZWFtLm1hdGNoKG9wZXJhdG9yc1tpXSkpIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChkZWxpbWl0ZXJzKSkgcmV0dXJuIFwicHVuY3R1YXRpb25cIjtcbiAgICBpZiAoc3RhdGUubGFzdFRva2VuID09IFwiLlwiICYmIHN0cmVhbS5tYXRjaChpZGVudGlmaWVycykpIHJldHVybiBcInByb3BlcnR5XCI7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChrZXl3b3JkcykgfHwgc3RyZWFtLm1hdGNoKHdvcmRPcGVyYXRvcnMpKSByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChidWlsdGlucykpIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eKHNlbGZ8Y2xzKVxcYi8pKSByZXR1cm4gXCJzZWxmXCI7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChpZGVudGlmaWVycykpIHtcbiAgICAgIGlmIChzdGF0ZS5sYXN0VG9rZW4gPT0gXCJkZWZcIiB8fCBzdGF0ZS5sYXN0VG9rZW4gPT0gXCJjbGFzc1wiKSByZXR1cm4gXCJkZWZcIjtcbiAgICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gICAgfVxuXG4gICAgLy8gSGFuZGxlIG5vbi1kZXRlY3RlZCBpdGVtc1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgcmV0dXJuIGluRm9ybWF0ID8gbnVsbCA6IEVSUk9SQ0xBU1M7XG4gIH1cbiAgZnVuY3Rpb24gZm9ybWF0U3RyaW5nRmFjdG9yeShkZWxpbWl0ZXIsIHRva2VuT3V0ZXIpIHtcbiAgICB3aGlsZSAoXCJydWJmXCIuaW5kZXhPZihkZWxpbWl0ZXIuY2hhckF0KDApLnRvTG93ZXJDYXNlKCkpID49IDApIGRlbGltaXRlciA9IGRlbGltaXRlci5zdWJzdHIoMSk7XG4gICAgdmFyIHNpbmdsZWxpbmUgPSBkZWxpbWl0ZXIubGVuZ3RoID09IDE7XG4gICAgdmFyIE9VVENMQVNTID0gXCJzdHJpbmdcIjtcbiAgICBmdW5jdGlvbiB0b2tlbk5lc3RlZEV4cHIoZGVwdGgpIHtcbiAgICAgIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgICB2YXIgaW5uZXIgPSB0b2tlbkJhc2VJbm5lcihzdHJlYW0sIHN0YXRlLCB0cnVlKTtcbiAgICAgICAgaWYgKGlubmVyID09IFwicHVuY3R1YXRpb25cIikge1xuICAgICAgICAgIGlmIChzdHJlYW0uY3VycmVudCgpID09IFwie1wiKSB7XG4gICAgICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuTmVzdGVkRXhwcihkZXB0aCArIDEpO1xuICAgICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLmN1cnJlbnQoKSA9PSBcIn1cIikge1xuICAgICAgICAgICAgaWYgKGRlcHRoID4gMSkgc3RhdGUudG9rZW5pemUgPSB0b2tlbk5lc3RlZEV4cHIoZGVwdGggLSAxKTtlbHNlIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmc7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHJldHVybiBpbm5lcjtcbiAgICAgIH07XG4gICAgfVxuICAgIGZ1bmN0aW9uIHRva2VuU3RyaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW14nXCJcXHtcXH1cXFxcXS8pO1xuICAgICAgICBpZiAoc3RyZWFtLmVhdChcIlxcXFxcIikpIHtcbiAgICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICAgIGlmIChzaW5nbGVsaW5lICYmIHN0cmVhbS5lb2woKSkgcmV0dXJuIE9VVENMQVNTO1xuICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaChkZWxpbWl0ZXIpKSB7XG4gICAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbk91dGVyO1xuICAgICAgICAgIHJldHVybiBPVVRDTEFTUztcbiAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goJ3t7JykpIHtcbiAgICAgICAgICAvLyBpZ25vcmUge3sgaW4gZi1zdHJcbiAgICAgICAgICByZXR1cm4gT1VUQ0xBU1M7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKCd7JywgZmFsc2UpKSB7XG4gICAgICAgICAgLy8gc3dpdGNoIHRvIG5lc3RlZCBtb2RlXG4gICAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbk5lc3RlZEV4cHIoMCk7XG4gICAgICAgICAgaWYgKHN0cmVhbS5jdXJyZW50KCkpIHJldHVybiBPVVRDTEFTUztlbHNlIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goJ319JykpIHtcbiAgICAgICAgICByZXR1cm4gT1VUQ0xBU1M7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKCd9JykpIHtcbiAgICAgICAgICAvLyBzaW5nbGUgfSBpbiBmLXN0cmluZyBpcyBhbiBlcnJvclxuICAgICAgICAgIHJldHVybiBFUlJPUkNMQVNTO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHN0cmVhbS5lYXQoL1snXCJdLyk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIGlmIChzaW5nbGVsaW5lKSB7XG4gICAgICAgIGlmIChwYXJzZXJDb25mLnNpbmdsZUxpbmVTdHJpbmdFcnJvcnMpIHJldHVybiBFUlJPUkNMQVNTO2Vsc2Ugc3RhdGUudG9rZW5pemUgPSB0b2tlbk91dGVyO1xuICAgICAgfVxuICAgICAgcmV0dXJuIE9VVENMQVNTO1xuICAgIH1cbiAgICB0b2tlblN0cmluZy5pc1N0cmluZyA9IHRydWU7XG4gICAgcmV0dXJuIHRva2VuU3RyaW5nO1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuU3RyaW5nRmFjdG9yeShkZWxpbWl0ZXIsIHRva2VuT3V0ZXIpIHtcbiAgICB3aGlsZSAoXCJydWJmXCIuaW5kZXhPZihkZWxpbWl0ZXIuY2hhckF0KDApLnRvTG93ZXJDYXNlKCkpID49IDApIGRlbGltaXRlciA9IGRlbGltaXRlci5zdWJzdHIoMSk7XG4gICAgdmFyIHNpbmdsZWxpbmUgPSBkZWxpbWl0ZXIubGVuZ3RoID09IDE7XG4gICAgdmFyIE9VVENMQVNTID0gXCJzdHJpbmdcIjtcbiAgICBmdW5jdGlvbiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB3aGlsZSAoIXN0cmVhbS5lb2woKSkge1xuICAgICAgICBzdHJlYW0uZWF0V2hpbGUoL1teJ1wiXFxcXF0vKTtcbiAgICAgICAgaWYgKHN0cmVhbS5lYXQoXCJcXFxcXCIpKSB7XG4gICAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgICBpZiAoc2luZ2xlbGluZSAmJiBzdHJlYW0uZW9sKCkpIHJldHVybiBPVVRDTEFTUztcbiAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goZGVsaW1pdGVyKSkge1xuICAgICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5PdXRlcjtcbiAgICAgICAgICByZXR1cm4gT1VUQ0xBU1M7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgc3RyZWFtLmVhdCgvWydcIl0vKTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgaWYgKHNpbmdsZWxpbmUpIHtcbiAgICAgICAgaWYgKHBhcnNlckNvbmYuc2luZ2xlTGluZVN0cmluZ0Vycm9ycykgcmV0dXJuIEVSUk9SQ0xBU1M7ZWxzZSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuT3V0ZXI7XG4gICAgICB9XG4gICAgICByZXR1cm4gT1VUQ0xBU1M7XG4gICAgfVxuICAgIHRva2VuU3RyaW5nLmlzU3RyaW5nID0gdHJ1ZTtcbiAgICByZXR1cm4gdG9rZW5TdHJpbmc7XG4gIH1cbiAgZnVuY3Rpb24gcHVzaFB5U2NvcGUoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlICh0b3Aoc3RhdGUpLnR5cGUgIT0gXCJweVwiKSBzdGF0ZS5zY29wZXMucG9wKCk7XG4gICAgc3RhdGUuc2NvcGVzLnB1c2goe1xuICAgICAgb2Zmc2V0OiB0b3Aoc3RhdGUpLm9mZnNldCArIHN0cmVhbS5pbmRlbnRVbml0LFxuICAgICAgdHlwZTogXCJweVwiLFxuICAgICAgYWxpZ246IG51bGxcbiAgICB9KTtcbiAgfVxuICBmdW5jdGlvbiBwdXNoQnJhY2tldFNjb3BlKHN0cmVhbSwgc3RhdGUsIHR5cGUpIHtcbiAgICB2YXIgYWxpZ24gPSBzdHJlYW0ubWF0Y2goL15bXFxzXFxbXFx7XFwoXSooPzojfCQpLywgZmFsc2UpID8gbnVsbCA6IHN0cmVhbS5jb2x1bW4oKSArIDE7XG4gICAgc3RhdGUuc2NvcGVzLnB1c2goe1xuICAgICAgb2Zmc2V0OiBzdGF0ZS5pbmRlbnQgKyAoaGFuZ2luZ0luZGVudCB8fCBzdHJlYW0uaW5kZW50VW5pdCksXG4gICAgICB0eXBlOiB0eXBlLFxuICAgICAgYWxpZ246IGFsaWduXG4gICAgfSk7XG4gIH1cbiAgZnVuY3Rpb24gZGVkZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICB3aGlsZSAoc3RhdGUuc2NvcGVzLmxlbmd0aCA+IDEgJiYgdG9wKHN0YXRlKS5vZmZzZXQgPiBpbmRlbnRlZCkge1xuICAgICAgaWYgKHRvcChzdGF0ZSkudHlwZSAhPSBcInB5XCIpIHJldHVybiB0cnVlO1xuICAgICAgc3RhdGUuc2NvcGVzLnBvcCgpO1xuICAgIH1cbiAgICByZXR1cm4gdG9wKHN0YXRlKS5vZmZzZXQgIT0gaW5kZW50ZWQ7XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5MZXhlcihzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgc3RhdGUuYmVnaW5uaW5nT2ZMaW5lID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmRlZGVudCA9IGZhbHNlO1xuICAgIH1cbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB2YXIgY3VycmVudCA9IHN0cmVhbS5jdXJyZW50KCk7XG5cbiAgICAvLyBIYW5kbGUgZGVjb3JhdG9yc1xuICAgIGlmIChzdGF0ZS5iZWdpbm5pbmdPZkxpbmUgJiYgY3VycmVudCA9PSBcIkBcIikgcmV0dXJuIHN0cmVhbS5tYXRjaChpZGVudGlmaWVycywgZmFsc2UpID8gXCJtZXRhXCIgOiBweTMgPyBcIm9wZXJhdG9yXCIgOiBFUlJPUkNMQVNTO1xuICAgIGlmICgvXFxTLy50ZXN0KGN1cnJlbnQpKSBzdGF0ZS5iZWdpbm5pbmdPZkxpbmUgPSBmYWxzZTtcbiAgICBpZiAoKHN0eWxlID09IFwidmFyaWFibGVcIiB8fCBzdHlsZSA9PSBcImJ1aWx0aW5cIikgJiYgc3RhdGUubGFzdFRva2VuID09IFwibWV0YVwiKSBzdHlsZSA9IFwibWV0YVwiO1xuXG4gICAgLy8gSGFuZGxlIHNjb3BlIGNoYW5nZXMuXG4gICAgaWYgKGN1cnJlbnQgPT0gXCJwYXNzXCIgfHwgY3VycmVudCA9PSBcInJldHVyblwiKSBzdGF0ZS5kZWRlbnQgPSB0cnVlO1xuICAgIGlmIChjdXJyZW50ID09IFwibGFtYmRhXCIpIHN0YXRlLmxhbWJkYSA9IHRydWU7XG4gICAgaWYgKGN1cnJlbnQgPT0gXCI6XCIgJiYgIXN0YXRlLmxhbWJkYSAmJiB0b3Aoc3RhdGUpLnR5cGUgPT0gXCJweVwiICYmIHN0cmVhbS5tYXRjaCgvXlxccyooPzojfCQpLywgZmFsc2UpKSBwdXNoUHlTY29wZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoY3VycmVudC5sZW5ndGggPT0gMSAmJiAhL3N0cmluZ3xjb21tZW50Ly50ZXN0KHN0eWxlKSkge1xuICAgICAgdmFyIGRlbGltaXRlcl9pbmRleCA9IFwiWyh7XCIuaW5kZXhPZihjdXJyZW50KTtcbiAgICAgIGlmIChkZWxpbWl0ZXJfaW5kZXggIT0gLTEpIHB1c2hCcmFja2V0U2NvcGUoc3RyZWFtLCBzdGF0ZSwgXCJdKX1cIi5zbGljZShkZWxpbWl0ZXJfaW5kZXgsIGRlbGltaXRlcl9pbmRleCArIDEpKTtcbiAgICAgIGRlbGltaXRlcl9pbmRleCA9IFwiXSl9XCIuaW5kZXhPZihjdXJyZW50KTtcbiAgICAgIGlmIChkZWxpbWl0ZXJfaW5kZXggIT0gLTEpIHtcbiAgICAgICAgaWYgKHRvcChzdGF0ZSkudHlwZSA9PSBjdXJyZW50KSBzdGF0ZS5pbmRlbnQgPSBzdGF0ZS5zY29wZXMucG9wKCkub2Zmc2V0IC0gKGhhbmdpbmdJbmRlbnQgfHwgc3RyZWFtLmluZGVudFVuaXQpO2Vsc2UgcmV0dXJuIEVSUk9SQ0xBU1M7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChzdGF0ZS5kZWRlbnQgJiYgc3RyZWFtLmVvbCgpICYmIHRvcChzdGF0ZSkudHlwZSA9PSBcInB5XCIgJiYgc3RhdGUuc2NvcGVzLmxlbmd0aCA+IDEpIHN0YXRlLnNjb3Blcy5wb3AoKTtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH1cbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBcInB5dGhvblwiLFxuICAgIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICAgIHNjb3BlczogW3tcbiAgICAgICAgICBvZmZzZXQ6IDAsXG4gICAgICAgICAgdHlwZTogXCJweVwiLFxuICAgICAgICAgIGFsaWduOiBudWxsXG4gICAgICAgIH1dLFxuICAgICAgICBpbmRlbnQ6IDAsXG4gICAgICAgIGxhc3RUb2tlbjogbnVsbCxcbiAgICAgICAgbGFtYmRhOiBmYWxzZSxcbiAgICAgICAgZGVkZW50OiAwXG4gICAgICB9O1xuICAgIH0sXG4gICAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgYWRkRXJyID0gc3RhdGUuZXJyb3JUb2tlbjtcbiAgICAgIGlmIChhZGRFcnIpIHN0YXRlLmVycm9yVG9rZW4gPSBmYWxzZTtcbiAgICAgIHZhciBzdHlsZSA9IHRva2VuTGV4ZXIoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICBpZiAoc3R5bGUgJiYgc3R5bGUgIT0gXCJjb21tZW50XCIpIHN0YXRlLmxhc3RUb2tlbiA9IHN0eWxlID09IFwia2V5d29yZFwiIHx8IHN0eWxlID09IFwicHVuY3R1YXRpb25cIiA/IHN0cmVhbS5jdXJyZW50KCkgOiBzdHlsZTtcbiAgICAgIGlmIChzdHlsZSA9PSBcInB1bmN0dWF0aW9uXCIpIHN0eWxlID0gbnVsbDtcbiAgICAgIGlmIChzdHJlYW0uZW9sKCkgJiYgc3RhdGUubGFtYmRhKSBzdGF0ZS5sYW1iZGEgPSBmYWxzZTtcbiAgICAgIHJldHVybiBhZGRFcnIgPyBFUlJPUkNMQVNTIDogc3R5bGU7XG4gICAgfSxcbiAgICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgICAgaWYgKHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSkgcmV0dXJuIHN0YXRlLnRva2VuaXplLmlzU3RyaW5nID8gbnVsbCA6IDA7XG4gICAgICB2YXIgc2NvcGUgPSB0b3Aoc3RhdGUpO1xuICAgICAgdmFyIGNsb3NpbmcgPSBzY29wZS50eXBlID09IHRleHRBZnRlci5jaGFyQXQoMCkgfHwgc2NvcGUudHlwZSA9PSBcInB5XCIgJiYgIXN0YXRlLmRlZGVudCAmJiAvXihlbHNlOnxlbGlmIHxleGNlcHQgfGZpbmFsbHk6KS8udGVzdCh0ZXh0QWZ0ZXIpO1xuICAgICAgaWYgKHNjb3BlLmFsaWduICE9IG51bGwpIHJldHVybiBzY29wZS5hbGlnbiAtIChjbG9zaW5nID8gMSA6IDApO2Vsc2UgcmV0dXJuIHNjb3BlLm9mZnNldCAtIChjbG9zaW5nID8gaGFuZ2luZ0luZGVudCB8fCBjeC51bml0IDogMCk7XG4gICAgfSxcbiAgICBsYW5ndWFnZURhdGE6IHtcbiAgICAgIGF1dG9jb21wbGV0ZTogY29tbW9uS2V5d29yZHMuY29uY2F0KGNvbW1vbkJ1aWx0aW5zKS5jb25jYXQoW1wiZXhlY1wiLCBcInByaW50XCJdKSxcbiAgICAgIGluZGVudE9uSW5wdXQ6IC9eXFxzKihbXFx9XFxdXFwpXXxlbHNlOnxlbGlmIHxleGNlcHQgfGZpbmFsbHk6KSQvLFxuICAgICAgY29tbWVudFRva2Vuczoge1xuICAgICAgICBsaW5lOiBcIiNcIlxuICAgICAgfSxcbiAgICAgIGNsb3NlQnJhY2tldHM6IHtcbiAgICAgICAgYnJhY2tldHM6IFtcIihcIiwgXCJbXCIsIFwie1wiLCBcIidcIiwgJ1wiJywgXCInJydcIiwgJ1wiXCJcIiddXG4gICAgICB9XG4gICAgfVxuICB9O1xufVxuO1xudmFyIHdvcmRzID0gZnVuY3Rpb24gKHN0cikge1xuICByZXR1cm4gc3RyLnNwbGl0KFwiIFwiKTtcbn07XG5leHBvcnQgY29uc3QgcHl0aG9uID0gbWtQeXRob24oe30pO1xuZXhwb3J0IGNvbnN0IGN5dGhvbiA9IG1rUHl0aG9uKHtcbiAgZXh0cmFfa2V5d29yZHM6IHdvcmRzKFwiYnkgY2RlZiBjaW1wb3J0IGNwZGVmIGN0eXBlZGVmIGVudW0gZXhjZXB0IFwiICsgXCJleHRlcm4gZ2lsIGluY2x1ZGUgbm9naWwgcHJvcGVydHkgcHVibGljIFwiICsgXCJyZWFkb25seSBzdHJ1Y3QgdW5pb24gREVGIElGIEVMSUYgRUxTRVwiKVxufSk7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==