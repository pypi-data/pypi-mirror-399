"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5991],{

/***/ 5991
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   coffeeScript: () => (/* binding */ coffeeScript)
/* harmony export */ });
var ERRORCLASS = "error";
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b");
}
var operators = /^(?:->|=>|\+[+=]?|-[\-=]?|\*[\*=]?|\/[\/=]?|[=!]=|<[><]?=?|>>?=?|%=?|&=?|\|=?|\^=?|\~|!|\?|(or|and|\|\||&&|\?)=)/;
var delimiters = /^(?:[()\[\]{},:`=;]|\.\.?\.?)/;
var identifiers = /^[_A-Za-z$][_A-Za-z$0-9]*/;
var atProp = /^@[_A-Za-z$][_A-Za-z$0-9]*/;
var wordOperators = wordRegexp(["and", "or", "not", "is", "isnt", "in", "instanceof", "typeof"]);
var indentKeywords = ["for", "while", "loop", "if", "unless", "else", "switch", "try", "catch", "finally", "class"];
var commonKeywords = ["break", "by", "continue", "debugger", "delete", "do", "in", "of", "new", "return", "then", "this", "@", "throw", "when", "until", "extends"];
var keywords = wordRegexp(indentKeywords.concat(commonKeywords));
indentKeywords = wordRegexp(indentKeywords);
var stringPrefixes = /^('{3}|\"{3}|['\"])/;
var regexPrefixes = /^(\/{3}|\/)/;
var commonConstants = ["Infinity", "NaN", "undefined", "null", "true", "false", "on", "off", "yes", "no"];
var constants = wordRegexp(commonConstants);

// Tokenizers
function tokenBase(stream, state) {
  // Handle scope changes
  if (stream.sol()) {
    if (state.scope.align === null) state.scope.align = false;
    var scopeOffset = state.scope.offset;
    if (stream.eatSpace()) {
      var lineOffset = stream.indentation();
      if (lineOffset > scopeOffset && state.scope.type == "coffee") {
        return "indent";
      } else if (lineOffset < scopeOffset) {
        return "dedent";
      }
      return null;
    } else {
      if (scopeOffset > 0) {
        dedent(stream, state);
      }
    }
  }
  if (stream.eatSpace()) {
    return null;
  }
  var ch = stream.peek();

  // Handle docco title comment (single line)
  if (stream.match("####")) {
    stream.skipToEnd();
    return "comment";
  }

  // Handle multi line comments
  if (stream.match("###")) {
    state.tokenize = longComment;
    return state.tokenize(stream, state);
  }

  // Single line comment
  if (ch === "#") {
    stream.skipToEnd();
    return "comment";
  }

  // Handle number literals
  if (stream.match(/^-?[0-9\.]/, false)) {
    var floatLiteral = false;
    // Floats
    if (stream.match(/^-?\d*\.\d+(e[\+\-]?\d+)?/i)) {
      floatLiteral = true;
    }
    if (stream.match(/^-?\d+\.\d*/)) {
      floatLiteral = true;
    }
    if (stream.match(/^-?\.\d+/)) {
      floatLiteral = true;
    }
    if (floatLiteral) {
      // prevent from getting extra . on 1..
      if (stream.peek() == ".") {
        stream.backUp(1);
      }
      return "number";
    }
    // Integers
    var intLiteral = false;
    // Hex
    if (stream.match(/^-?0x[0-9a-f]+/i)) {
      intLiteral = true;
    }
    // Decimal
    if (stream.match(/^-?[1-9]\d*(e[\+\-]?\d+)?/)) {
      intLiteral = true;
    }
    // Zero by itself with no other piece of number.
    if (stream.match(/^-?0(?![\dx])/i)) {
      intLiteral = true;
    }
    if (intLiteral) {
      return "number";
    }
  }

  // Handle strings
  if (stream.match(stringPrefixes)) {
    state.tokenize = tokenFactory(stream.current(), false, "string");
    return state.tokenize(stream, state);
  }
  // Handle regex literals
  if (stream.match(regexPrefixes)) {
    if (stream.current() != "/" || stream.match(/^.*\//, false)) {
      // prevent highlight of division
      state.tokenize = tokenFactory(stream.current(), true, "string.special");
      return state.tokenize(stream, state);
    } else {
      stream.backUp(1);
    }
  }

  // Handle operators and delimiters
  if (stream.match(operators) || stream.match(wordOperators)) {
    return "operator";
  }
  if (stream.match(delimiters)) {
    return "punctuation";
  }
  if (stream.match(constants)) {
    return "atom";
  }
  if (stream.match(atProp) || state.prop && stream.match(identifiers)) {
    return "property";
  }
  if (stream.match(keywords)) {
    return "keyword";
  }
  if (stream.match(identifiers)) {
    return "variable";
  }

  // Handle non-detected items
  stream.next();
  return ERRORCLASS;
}
function tokenFactory(delimiter, singleline, outclass) {
  return function (stream, state) {
    while (!stream.eol()) {
      stream.eatWhile(/[^'"\/\\]/);
      if (stream.eat("\\")) {
        stream.next();
        if (singleline && stream.eol()) {
          return outclass;
        }
      } else if (stream.match(delimiter)) {
        state.tokenize = tokenBase;
        return outclass;
      } else {
        stream.eat(/['"\/]/);
      }
    }
    if (singleline) {
      state.tokenize = tokenBase;
    }
    return outclass;
  };
}
function longComment(stream, state) {
  while (!stream.eol()) {
    stream.eatWhile(/[^#]/);
    if (stream.match("###")) {
      state.tokenize = tokenBase;
      break;
    }
    stream.eatWhile("#");
  }
  return "comment";
}
function indent(stream, state, type = "coffee") {
  var offset = 0,
    align = false,
    alignOffset = null;
  for (var scope = state.scope; scope; scope = scope.prev) {
    if (scope.type === "coffee" || scope.type == "}") {
      offset = scope.offset + stream.indentUnit;
      break;
    }
  }
  if (type !== "coffee") {
    align = null;
    alignOffset = stream.column() + stream.current().length;
  } else if (state.scope.align) {
    state.scope.align = false;
  }
  state.scope = {
    offset: offset,
    type: type,
    prev: state.scope,
    align: align,
    alignOffset: alignOffset
  };
}
function dedent(stream, state) {
  if (!state.scope.prev) return;
  if (state.scope.type === "coffee") {
    var _indent = stream.indentation();
    var matched = false;
    for (var scope = state.scope; scope; scope = scope.prev) {
      if (_indent === scope.offset) {
        matched = true;
        break;
      }
    }
    if (!matched) {
      return true;
    }
    while (state.scope.prev && state.scope.offset !== _indent) {
      state.scope = state.scope.prev;
    }
    return false;
  } else {
    state.scope = state.scope.prev;
    return false;
  }
}
function tokenLexer(stream, state) {
  var style = state.tokenize(stream, state);
  var current = stream.current();

  // Handle scope changes.
  if (current === "return") {
    state.dedent = true;
  }
  if ((current === "->" || current === "=>") && stream.eol() || style === "indent") {
    indent(stream, state);
  }
  var delimiter_index = "[({".indexOf(current);
  if (delimiter_index !== -1) {
    indent(stream, state, "])}".slice(delimiter_index, delimiter_index + 1));
  }
  if (indentKeywords.exec(current)) {
    indent(stream, state);
  }
  if (current == "then") {
    dedent(stream, state);
  }
  if (style === "dedent") {
    if (dedent(stream, state)) {
      return ERRORCLASS;
    }
  }
  delimiter_index = "])}".indexOf(current);
  if (delimiter_index !== -1) {
    while (state.scope.type == "coffee" && state.scope.prev) state.scope = state.scope.prev;
    if (state.scope.type == current) state.scope = state.scope.prev;
  }
  if (state.dedent && stream.eol()) {
    if (state.scope.type == "coffee" && state.scope.prev) state.scope = state.scope.prev;
    state.dedent = false;
  }
  return style == "indent" || style == "dedent" ? null : style;
}
const coffeeScript = {
  name: "coffeescript",
  startState: function () {
    return {
      tokenize: tokenBase,
      scope: {
        offset: 0,
        type: "coffee",
        prev: null,
        align: false
      },
      prop: false,
      dedent: 0
    };
  },
  token: function (stream, state) {
    var fillAlign = state.scope.align === null && state.scope;
    if (fillAlign && stream.sol()) fillAlign.align = false;
    var style = tokenLexer(stream, state);
    if (style && style != "comment") {
      if (fillAlign) fillAlign.align = true;
      state.prop = style == "punctuation" && stream.current() == ".";
    }
    return style;
  },
  indent: function (state, text) {
    if (state.tokenize != tokenBase) return 0;
    var scope = state.scope;
    var closer = text && "])}".indexOf(text.charAt(0)) > -1;
    if (closer) while (scope.type == "coffee" && scope.prev) scope = scope.prev;
    var closes = closer && scope.type === text.charAt(0);
    if (scope.align) return scope.alignOffset - (closes ? 1 : 0);else return (closes ? scope.prev : scope).offset;
  },
  languageData: {
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTk5MS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9jb2ZmZWVzY3JpcHQuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIEVSUk9SQ0xBU1MgPSBcImVycm9yXCI7XG5mdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIpO1xufVxudmFyIG9wZXJhdG9ycyA9IC9eKD86LT58PT58XFwrWys9XT98LVtcXC09XT98XFwqW1xcKj1dP3xcXC9bXFwvPV0/fFs9IV09fDxbPjxdPz0/fD4+Pz0/fCU9P3wmPT98XFx8PT98XFxePT98XFx+fCF8XFw/fChvcnxhbmR8XFx8XFx8fCYmfFxcPyk9KS87XG52YXIgZGVsaW1pdGVycyA9IC9eKD86WygpXFxbXFxde30sOmA9O118XFwuXFwuP1xcLj8pLztcbnZhciBpZGVudGlmaWVycyA9IC9eW19BLVphLXokXVtfQS1aYS16JDAtOV0qLztcbnZhciBhdFByb3AgPSAvXkBbX0EtWmEteiRdW19BLVphLXokMC05XSovO1xudmFyIHdvcmRPcGVyYXRvcnMgPSB3b3JkUmVnZXhwKFtcImFuZFwiLCBcIm9yXCIsIFwibm90XCIsIFwiaXNcIiwgXCJpc250XCIsIFwiaW5cIiwgXCJpbnN0YW5jZW9mXCIsIFwidHlwZW9mXCJdKTtcbnZhciBpbmRlbnRLZXl3b3JkcyA9IFtcImZvclwiLCBcIndoaWxlXCIsIFwibG9vcFwiLCBcImlmXCIsIFwidW5sZXNzXCIsIFwiZWxzZVwiLCBcInN3aXRjaFwiLCBcInRyeVwiLCBcImNhdGNoXCIsIFwiZmluYWxseVwiLCBcImNsYXNzXCJdO1xudmFyIGNvbW1vbktleXdvcmRzID0gW1wiYnJlYWtcIiwgXCJieVwiLCBcImNvbnRpbnVlXCIsIFwiZGVidWdnZXJcIiwgXCJkZWxldGVcIiwgXCJkb1wiLCBcImluXCIsIFwib2ZcIiwgXCJuZXdcIiwgXCJyZXR1cm5cIiwgXCJ0aGVuXCIsIFwidGhpc1wiLCBcIkBcIiwgXCJ0aHJvd1wiLCBcIndoZW5cIiwgXCJ1bnRpbFwiLCBcImV4dGVuZHNcIl07XG52YXIga2V5d29yZHMgPSB3b3JkUmVnZXhwKGluZGVudEtleXdvcmRzLmNvbmNhdChjb21tb25LZXl3b3JkcykpO1xuaW5kZW50S2V5d29yZHMgPSB3b3JkUmVnZXhwKGluZGVudEtleXdvcmRzKTtcbnZhciBzdHJpbmdQcmVmaXhlcyA9IC9eKCd7M318XFxcInszfXxbJ1xcXCJdKS87XG52YXIgcmVnZXhQcmVmaXhlcyA9IC9eKFxcL3szfXxcXC8pLztcbnZhciBjb21tb25Db25zdGFudHMgPSBbXCJJbmZpbml0eVwiLCBcIk5hTlwiLCBcInVuZGVmaW5lZFwiLCBcIm51bGxcIiwgXCJ0cnVlXCIsIFwiZmFsc2VcIiwgXCJvblwiLCBcIm9mZlwiLCBcInllc1wiLCBcIm5vXCJdO1xudmFyIGNvbnN0YW50cyA9IHdvcmRSZWdleHAoY29tbW9uQ29uc3RhbnRzKTtcblxuLy8gVG9rZW5pemVyc1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgLy8gSGFuZGxlIHNjb3BlIGNoYW5nZXNcbiAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgIGlmIChzdGF0ZS5zY29wZS5hbGlnbiA9PT0gbnVsbCkgc3RhdGUuc2NvcGUuYWxpZ24gPSBmYWxzZTtcbiAgICB2YXIgc2NvcGVPZmZzZXQgPSBzdGF0ZS5zY29wZS5vZmZzZXQ7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICB2YXIgbGluZU9mZnNldCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgICAgaWYgKGxpbmVPZmZzZXQgPiBzY29wZU9mZnNldCAmJiBzdGF0ZS5zY29wZS50eXBlID09IFwiY29mZmVlXCIpIHtcbiAgICAgICAgcmV0dXJuIFwiaW5kZW50XCI7XG4gICAgICB9IGVsc2UgaWYgKGxpbmVPZmZzZXQgPCBzY29wZU9mZnNldCkge1xuICAgICAgICByZXR1cm4gXCJkZWRlbnRcIjtcbiAgICAgIH1cbiAgICAgIHJldHVybiBudWxsO1xuICAgIH0gZWxzZSB7XG4gICAgICBpZiAoc2NvcGVPZmZzZXQgPiAwKSB7XG4gICAgICAgIGRlZGVudChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIH1cbiAgICB9XG4gIH1cbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgdmFyIGNoID0gc3RyZWFtLnBlZWsoKTtcblxuICAvLyBIYW5kbGUgZG9jY28gdGl0bGUgY29tbWVudCAoc2luZ2xlIGxpbmUpXG4gIGlmIChzdHJlYW0ubWF0Y2goXCIjIyMjXCIpKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuXG4gIC8vIEhhbmRsZSBtdWx0aSBsaW5lIGNvbW1lbnRzXG4gIGlmIChzdHJlYW0ubWF0Y2goXCIjIyNcIikpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IGxvbmdDb21tZW50O1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuXG4gIC8vIFNpbmdsZSBsaW5lIGNvbW1lbnRcbiAgaWYgKGNoID09PSBcIiNcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cblxuICAvLyBIYW5kbGUgbnVtYmVyIGxpdGVyYWxzXG4gIGlmIChzdHJlYW0ubWF0Y2goL14tP1swLTlcXC5dLywgZmFsc2UpKSB7XG4gICAgdmFyIGZsb2F0TGl0ZXJhbCA9IGZhbHNlO1xuICAgIC8vIEZsb2F0c1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL14tP1xcZCpcXC5cXGQrKGVbXFwrXFwtXT9cXGQrKT8vaSkpIHtcbiAgICAgIGZsb2F0TGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14tP1xcZCtcXC5cXGQqLykpIHtcbiAgICAgIGZsb2F0TGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14tP1xcLlxcZCsvKSkge1xuICAgICAgZmxvYXRMaXRlcmFsID0gdHJ1ZTtcbiAgICB9XG4gICAgaWYgKGZsb2F0TGl0ZXJhbCkge1xuICAgICAgLy8gcHJldmVudCBmcm9tIGdldHRpbmcgZXh0cmEgLiBvbiAxLi5cbiAgICAgIGlmIChzdHJlYW0ucGVlaygpID09IFwiLlwiKSB7XG4gICAgICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgICB9XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gICAgLy8gSW50ZWdlcnNcbiAgICB2YXIgaW50TGl0ZXJhbCA9IGZhbHNlO1xuICAgIC8vIEhleFxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14tPzB4WzAtOWEtZl0rL2kpKSB7XG4gICAgICBpbnRMaXRlcmFsID0gdHJ1ZTtcbiAgICB9XG4gICAgLy8gRGVjaW1hbFxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14tP1sxLTldXFxkKihlW1xcK1xcLV0/XFxkKyk/LykpIHtcbiAgICAgIGludExpdGVyYWwgPSB0cnVlO1xuICAgIH1cbiAgICAvLyBaZXJvIGJ5IGl0c2VsZiB3aXRoIG5vIG90aGVyIHBpZWNlIG9mIG51bWJlci5cbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eLT8wKD8hW1xcZHhdKS9pKSkge1xuICAgICAgaW50TGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIGlmIChpbnRMaXRlcmFsKSB7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gIH1cblxuICAvLyBIYW5kbGUgc3RyaW5nc1xuICBpZiAoc3RyZWFtLm1hdGNoKHN0cmluZ1ByZWZpeGVzKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5GYWN0b3J5KHN0cmVhbS5jdXJyZW50KCksIGZhbHNlLCBcInN0cmluZ1wiKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgLy8gSGFuZGxlIHJlZ2V4IGxpdGVyYWxzXG4gIGlmIChzdHJlYW0ubWF0Y2gocmVnZXhQcmVmaXhlcykpIHtcbiAgICBpZiAoc3RyZWFtLmN1cnJlbnQoKSAhPSBcIi9cIiB8fCBzdHJlYW0ubWF0Y2goL14uKlxcLy8sIGZhbHNlKSkge1xuICAgICAgLy8gcHJldmVudCBoaWdobGlnaHQgb2YgZGl2aXNpb25cbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5GYWN0b3J5KHN0cmVhbS5jdXJyZW50KCksIHRydWUsIFwic3RyaW5nLnNwZWNpYWxcIik7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgfVxuICB9XG5cbiAgLy8gSGFuZGxlIG9wZXJhdG9ycyBhbmQgZGVsaW1pdGVyc1xuICBpZiAoc3RyZWFtLm1hdGNoKG9wZXJhdG9ycykgfHwgc3RyZWFtLm1hdGNoKHdvcmRPcGVyYXRvcnMpKSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGRlbGltaXRlcnMpKSB7XG4gICAgcmV0dXJuIFwicHVuY3R1YXRpb25cIjtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGNvbnN0YW50cykpIHtcbiAgICByZXR1cm4gXCJhdG9tXCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChhdFByb3ApIHx8IHN0YXRlLnByb3AgJiYgc3RyZWFtLm1hdGNoKGlkZW50aWZpZXJzKSkge1xuICAgIHJldHVybiBcInByb3BlcnR5XCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChrZXl3b3JkcykpIHtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChpZGVudGlmaWVycykpIHtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9XG5cbiAgLy8gSGFuZGxlIG5vbi1kZXRlY3RlZCBpdGVtc1xuICBzdHJlYW0ubmV4dCgpO1xuICByZXR1cm4gRVJST1JDTEFTUztcbn1cbmZ1bmN0aW9uIHRva2VuRmFjdG9yeShkZWxpbWl0ZXIsIHNpbmdsZWxpbmUsIG91dGNsYXNzKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1teJ1wiXFwvXFxcXF0vKTtcbiAgICAgIGlmIChzdHJlYW0uZWF0KFwiXFxcXFwiKSkge1xuICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICBpZiAoc2luZ2xlbGluZSAmJiBzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgICByZXR1cm4gb3V0Y2xhc3M7XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKGRlbGltaXRlcikpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICAgIHJldHVybiBvdXRjbGFzcztcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5lYXQoL1snXCJcXC9dLyk7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChzaW5nbGVsaW5lKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICB9XG4gICAgcmV0dXJuIG91dGNsYXNzO1xuICB9O1xufVxuZnVuY3Rpb24gbG9uZ0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB3aGlsZSAoIXN0cmVhbS5lb2woKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW14jXS8pO1xuICAgIGlmIChzdHJlYW0ubWF0Y2goXCIjIyNcIikpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIHN0cmVhbS5lYXRXaGlsZShcIiNcIik7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gaW5kZW50KHN0cmVhbSwgc3RhdGUsIHR5cGUgPSBcImNvZmZlZVwiKSB7XG4gIHZhciBvZmZzZXQgPSAwLFxuICAgIGFsaWduID0gZmFsc2UsXG4gICAgYWxpZ25PZmZzZXQgPSBudWxsO1xuICBmb3IgKHZhciBzY29wZSA9IHN0YXRlLnNjb3BlOyBzY29wZTsgc2NvcGUgPSBzY29wZS5wcmV2KSB7XG4gICAgaWYgKHNjb3BlLnR5cGUgPT09IFwiY29mZmVlXCIgfHwgc2NvcGUudHlwZSA9PSBcIn1cIikge1xuICAgICAgb2Zmc2V0ID0gc2NvcGUub2Zmc2V0ICsgc3RyZWFtLmluZGVudFVuaXQ7XG4gICAgICBicmVhaztcbiAgICB9XG4gIH1cbiAgaWYgKHR5cGUgIT09IFwiY29mZmVlXCIpIHtcbiAgICBhbGlnbiA9IG51bGw7XG4gICAgYWxpZ25PZmZzZXQgPSBzdHJlYW0uY29sdW1uKCkgKyBzdHJlYW0uY3VycmVudCgpLmxlbmd0aDtcbiAgfSBlbHNlIGlmIChzdGF0ZS5zY29wZS5hbGlnbikge1xuICAgIHN0YXRlLnNjb3BlLmFsaWduID0gZmFsc2U7XG4gIH1cbiAgc3RhdGUuc2NvcGUgPSB7XG4gICAgb2Zmc2V0OiBvZmZzZXQsXG4gICAgdHlwZTogdHlwZSxcbiAgICBwcmV2OiBzdGF0ZS5zY29wZSxcbiAgICBhbGlnbjogYWxpZ24sXG4gICAgYWxpZ25PZmZzZXQ6IGFsaWduT2Zmc2V0XG4gIH07XG59XG5mdW5jdGlvbiBkZWRlbnQoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoIXN0YXRlLnNjb3BlLnByZXYpIHJldHVybjtcbiAgaWYgKHN0YXRlLnNjb3BlLnR5cGUgPT09IFwiY29mZmVlXCIpIHtcbiAgICB2YXIgX2luZGVudCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgIHZhciBtYXRjaGVkID0gZmFsc2U7XG4gICAgZm9yICh2YXIgc2NvcGUgPSBzdGF0ZS5zY29wZTsgc2NvcGU7IHNjb3BlID0gc2NvcGUucHJldikge1xuICAgICAgaWYgKF9pbmRlbnQgPT09IHNjb3BlLm9mZnNldCkge1xuICAgICAgICBtYXRjaGVkID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgfVxuICAgIGlmICghbWF0Y2hlZCkge1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfVxuICAgIHdoaWxlIChzdGF0ZS5zY29wZS5wcmV2ICYmIHN0YXRlLnNjb3BlLm9mZnNldCAhPT0gX2luZGVudCkge1xuICAgICAgc3RhdGUuc2NvcGUgPSBzdGF0ZS5zY29wZS5wcmV2O1xuICAgIH1cbiAgICByZXR1cm4gZmFsc2U7XG4gIH0gZWxzZSB7XG4gICAgc3RhdGUuc2NvcGUgPSBzdGF0ZS5zY29wZS5wcmV2O1xuICAgIHJldHVybiBmYWxzZTtcbiAgfVxufVxuZnVuY3Rpb24gdG9rZW5MZXhlcihzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBzdHlsZSA9IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB2YXIgY3VycmVudCA9IHN0cmVhbS5jdXJyZW50KCk7XG5cbiAgLy8gSGFuZGxlIHNjb3BlIGNoYW5nZXMuXG4gIGlmIChjdXJyZW50ID09PSBcInJldHVyblwiKSB7XG4gICAgc3RhdGUuZGVkZW50ID0gdHJ1ZTtcbiAgfVxuICBpZiAoKGN1cnJlbnQgPT09IFwiLT5cIiB8fCBjdXJyZW50ID09PSBcIj0+XCIpICYmIHN0cmVhbS5lb2woKSB8fCBzdHlsZSA9PT0gXCJpbmRlbnRcIikge1xuICAgIGluZGVudChzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICB2YXIgZGVsaW1pdGVyX2luZGV4ID0gXCJbKHtcIi5pbmRleE9mKGN1cnJlbnQpO1xuICBpZiAoZGVsaW1pdGVyX2luZGV4ICE9PSAtMSkge1xuICAgIGluZGVudChzdHJlYW0sIHN0YXRlLCBcIl0pfVwiLnNsaWNlKGRlbGltaXRlcl9pbmRleCwgZGVsaW1pdGVyX2luZGV4ICsgMSkpO1xuICB9XG4gIGlmIChpbmRlbnRLZXl3b3Jkcy5leGVjKGN1cnJlbnQpKSB7XG4gICAgaW5kZW50KHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChjdXJyZW50ID09IFwidGhlblwiKSB7XG4gICAgZGVkZW50KHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChzdHlsZSA9PT0gXCJkZWRlbnRcIikge1xuICAgIGlmIChkZWRlbnQoc3RyZWFtLCBzdGF0ZSkpIHtcbiAgICAgIHJldHVybiBFUlJPUkNMQVNTO1xuICAgIH1cbiAgfVxuICBkZWxpbWl0ZXJfaW5kZXggPSBcIl0pfVwiLmluZGV4T2YoY3VycmVudCk7XG4gIGlmIChkZWxpbWl0ZXJfaW5kZXggIT09IC0xKSB7XG4gICAgd2hpbGUgKHN0YXRlLnNjb3BlLnR5cGUgPT0gXCJjb2ZmZWVcIiAmJiBzdGF0ZS5zY29wZS5wcmV2KSBzdGF0ZS5zY29wZSA9IHN0YXRlLnNjb3BlLnByZXY7XG4gICAgaWYgKHN0YXRlLnNjb3BlLnR5cGUgPT0gY3VycmVudCkgc3RhdGUuc2NvcGUgPSBzdGF0ZS5zY29wZS5wcmV2O1xuICB9XG4gIGlmIChzdGF0ZS5kZWRlbnQgJiYgc3RyZWFtLmVvbCgpKSB7XG4gICAgaWYgKHN0YXRlLnNjb3BlLnR5cGUgPT0gXCJjb2ZmZWVcIiAmJiBzdGF0ZS5zY29wZS5wcmV2KSBzdGF0ZS5zY29wZSA9IHN0YXRlLnNjb3BlLnByZXY7XG4gICAgc3RhdGUuZGVkZW50ID0gZmFsc2U7XG4gIH1cbiAgcmV0dXJuIHN0eWxlID09IFwiaW5kZW50XCIgfHwgc3R5bGUgPT0gXCJkZWRlbnRcIiA/IG51bGwgOiBzdHlsZTtcbn1cbmV4cG9ydCBjb25zdCBjb2ZmZWVTY3JpcHQgPSB7XG4gIG5hbWU6IFwiY29mZmVlc2NyaXB0XCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IHRva2VuQmFzZSxcbiAgICAgIHNjb3BlOiB7XG4gICAgICAgIG9mZnNldDogMCxcbiAgICAgICAgdHlwZTogXCJjb2ZmZWVcIixcbiAgICAgICAgcHJldjogbnVsbCxcbiAgICAgICAgYWxpZ246IGZhbHNlXG4gICAgICB9LFxuICAgICAgcHJvcDogZmFsc2UsXG4gICAgICBkZWRlbnQ6IDBcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZmlsbEFsaWduID0gc3RhdGUuc2NvcGUuYWxpZ24gPT09IG51bGwgJiYgc3RhdGUuc2NvcGU7XG4gICAgaWYgKGZpbGxBbGlnbiAmJiBzdHJlYW0uc29sKCkpIGZpbGxBbGlnbi5hbGlnbiA9IGZhbHNlO1xuICAgIHZhciBzdHlsZSA9IHRva2VuTGV4ZXIoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0eWxlICYmIHN0eWxlICE9IFwiY29tbWVudFwiKSB7XG4gICAgICBpZiAoZmlsbEFsaWduKSBmaWxsQWxpZ24uYWxpZ24gPSB0cnVlO1xuICAgICAgc3RhdGUucHJvcCA9IHN0eWxlID09IFwicHVuY3R1YXRpb25cIiAmJiBzdHJlYW0uY3VycmVudCgpID09IFwiLlwiO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0KSB7XG4gICAgaWYgKHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSkgcmV0dXJuIDA7XG4gICAgdmFyIHNjb3BlID0gc3RhdGUuc2NvcGU7XG4gICAgdmFyIGNsb3NlciA9IHRleHQgJiYgXCJdKX1cIi5pbmRleE9mKHRleHQuY2hhckF0KDApKSA+IC0xO1xuICAgIGlmIChjbG9zZXIpIHdoaWxlIChzY29wZS50eXBlID09IFwiY29mZmVlXCIgJiYgc2NvcGUucHJldikgc2NvcGUgPSBzY29wZS5wcmV2O1xuICAgIHZhciBjbG9zZXMgPSBjbG9zZXIgJiYgc2NvcGUudHlwZSA9PT0gdGV4dC5jaGFyQXQoMCk7XG4gICAgaWYgKHNjb3BlLmFsaWduKSByZXR1cm4gc2NvcGUuYWxpZ25PZmZzZXQgLSAoY2xvc2VzID8gMSA6IDApO2Vsc2UgcmV0dXJuIChjbG9zZXMgPyBzY29wZS5wcmV2IDogc2NvcGUpLm9mZnNldDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIjXCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==