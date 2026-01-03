"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5537],{

/***/ 35537
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   swift: () => (/* binding */ swift)
/* harmony export */ });
function wordSet(words) {
  var set = {};
  for (var i = 0; i < words.length; i++) set[words[i]] = true;
  return set;
}
var keywords = wordSet(["_", "var", "let", "actor", "class", "enum", "extension", "import", "protocol", "struct", "func", "typealias", "associatedtype", "open", "public", "internal", "fileprivate", "private", "deinit", "init", "new", "override", "self", "subscript", "super", "convenience", "dynamic", "final", "indirect", "lazy", "required", "static", "unowned", "unowned(safe)", "unowned(unsafe)", "weak", "as", "is", "break", "case", "continue", "default", "else", "fallthrough", "for", "guard", "if", "in", "repeat", "switch", "where", "while", "defer", "return", "inout", "mutating", "nonmutating", "isolated", "nonisolated", "catch", "do", "rethrows", "throw", "throws", "async", "await", "try", "didSet", "get", "set", "willSet", "assignment", "associativity", "infix", "left", "none", "operator", "postfix", "precedence", "precedencegroup", "prefix", "right", "Any", "AnyObject", "Type", "dynamicType", "Self", "Protocol", "__COLUMN__", "__FILE__", "__FUNCTION__", "__LINE__"]);
var definingKeywords = wordSet(["var", "let", "actor", "class", "enum", "extension", "import", "protocol", "struct", "func", "typealias", "associatedtype", "for"]);
var atoms = wordSet(["true", "false", "nil", "self", "super", "_"]);
var types = wordSet(["Array", "Bool", "Character", "Dictionary", "Double", "Float", "Int", "Int8", "Int16", "Int32", "Int64", "Never", "Optional", "Set", "String", "UInt8", "UInt16", "UInt32", "UInt64", "Void"]);
var operators = "+-/*%=|&<>~^?!";
var punc = ":;,.(){}[]";
var binary = /^\-?0b[01][01_]*/;
var octal = /^\-?0o[0-7][0-7_]*/;
var hexadecimal = /^\-?0x[\dA-Fa-f][\dA-Fa-f_]*(?:(?:\.[\dA-Fa-f][\dA-Fa-f_]*)?[Pp]\-?\d[\d_]*)?/;
var decimal = /^\-?\d[\d_]*(?:\.\d[\d_]*)?(?:[Ee]\-?\d[\d_]*)?/;
var identifier = /^\$\d+|(`?)[_A-Za-z][_A-Za-z$0-9]*\1/;
var property = /^\.(?:\$\d+|(`?)[_A-Za-z][_A-Za-z$0-9]*\1)/;
var instruction = /^\#[A-Za-z]+/;
var attribute = /^@(?:\$\d+|(`?)[_A-Za-z][_A-Za-z$0-9]*\1)/;
//var regexp = /^\/(?!\s)(?:\/\/)?(?:\\.|[^\/])+\//

function tokenBase(stream, state, prev) {
  if (stream.sol()) state.indented = stream.indentation();
  if (stream.eatSpace()) return null;
  var ch = stream.peek();
  if (ch == "/") {
    if (stream.match("//")) {
      stream.skipToEnd();
      return "comment";
    }
    if (stream.match("/*")) {
      state.tokenize.push(tokenComment);
      return tokenComment(stream, state);
    }
  }
  if (stream.match(instruction)) return "builtin";
  if (stream.match(attribute)) return "attribute";
  if (stream.match(binary)) return "number";
  if (stream.match(octal)) return "number";
  if (stream.match(hexadecimal)) return "number";
  if (stream.match(decimal)) return "number";
  if (stream.match(property)) return "property";
  if (operators.indexOf(ch) > -1) {
    stream.next();
    return "operator";
  }
  if (punc.indexOf(ch) > -1) {
    stream.next();
    stream.match("..");
    return "punctuation";
  }
  var stringMatch;
  if (stringMatch = stream.match(/("""|"|')/)) {
    var tokenize = tokenString.bind(null, stringMatch[0]);
    state.tokenize.push(tokenize);
    return tokenize(stream, state);
  }
  if (stream.match(identifier)) {
    var ident = stream.current();
    if (types.hasOwnProperty(ident)) return "type";
    if (atoms.hasOwnProperty(ident)) return "atom";
    if (keywords.hasOwnProperty(ident)) {
      if (definingKeywords.hasOwnProperty(ident)) state.prev = "define";
      return "keyword";
    }
    if (prev == "define") return "def";
    return "variable";
  }
  stream.next();
  return null;
}
function tokenUntilClosingParen() {
  var depth = 0;
  return function (stream, state, prev) {
    var inner = tokenBase(stream, state, prev);
    if (inner == "punctuation") {
      if (stream.current() == "(") ++depth;else if (stream.current() == ")") {
        if (depth == 0) {
          stream.backUp(1);
          state.tokenize.pop();
          return state.tokenize[state.tokenize.length - 1](stream, state);
        } else --depth;
      }
    }
    return inner;
  };
}
function tokenString(openQuote, stream, state) {
  var singleLine = openQuote.length == 1;
  var ch,
    escaped = false;
  while (ch = stream.peek()) {
    if (escaped) {
      stream.next();
      if (ch == "(") {
        state.tokenize.push(tokenUntilClosingParen());
        return "string";
      }
      escaped = false;
    } else if (stream.match(openQuote)) {
      state.tokenize.pop();
      return "string";
    } else {
      stream.next();
      escaped = ch == "\\";
    }
  }
  if (singleLine) {
    state.tokenize.pop();
  }
  return "string";
}
function tokenComment(stream, state) {
  var ch;
  while (ch = stream.next()) {
    if (ch === "/" && stream.eat("*")) {
      state.tokenize.push(tokenComment);
    } else if (ch === "*" && stream.eat("/")) {
      state.tokenize.pop();
      break;
    }
  }
  return "comment";
}
function Context(prev, align, indented) {
  this.prev = prev;
  this.align = align;
  this.indented = indented;
}
function pushContext(state, stream) {
  var align = stream.match(/^\s*($|\/[\/\*]|[)}\]])/, false) ? null : stream.column() + 1;
  state.context = new Context(state.context, align, state.indented);
}
function popContext(state) {
  if (state.context) {
    state.indented = state.context.indented;
    state.context = state.context.prev;
  }
}
const swift = {
  name: "swift",
  startState: function () {
    return {
      prev: null,
      context: null,
      indented: 0,
      tokenize: []
    };
  },
  token: function (stream, state) {
    var prev = state.prev;
    state.prev = null;
    var tokenize = state.tokenize[state.tokenize.length - 1] || tokenBase;
    var style = tokenize(stream, state, prev);
    if (!style || style == "comment") state.prev = prev;else if (!state.prev) state.prev = style;
    if (style == "punctuation") {
      var bracket = /[\(\[\{]|([\]\)\}])/.exec(stream.current());
      if (bracket) (bracket[1] ? popContext : pushContext)(state, stream);
    }
    return style;
  },
  indent: function (state, textAfter, iCx) {
    var cx = state.context;
    if (!cx) return 0;
    var closing = /^[\]\}\)]/.test(textAfter);
    if (cx.align != null) return cx.align - (closing ? 1 : 0);
    return cx.indented + (closing ? 0 : iCx.unit);
  },
  languageData: {
    indentOnInput: /^\s*[\)\}\]]$/,
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    },
    closeBrackets: {
      brackets: ["(", "[", "{", "'", '"', "`"]
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTUzNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9zd2lmdC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkU2V0KHdvcmRzKSB7XG4gIHZhciBzZXQgPSB7fTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7IGkrKykgc2V0W3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBzZXQ7XG59XG52YXIga2V5d29yZHMgPSB3b3JkU2V0KFtcIl9cIiwgXCJ2YXJcIiwgXCJsZXRcIiwgXCJhY3RvclwiLCBcImNsYXNzXCIsIFwiZW51bVwiLCBcImV4dGVuc2lvblwiLCBcImltcG9ydFwiLCBcInByb3RvY29sXCIsIFwic3RydWN0XCIsIFwiZnVuY1wiLCBcInR5cGVhbGlhc1wiLCBcImFzc29jaWF0ZWR0eXBlXCIsIFwib3BlblwiLCBcInB1YmxpY1wiLCBcImludGVybmFsXCIsIFwiZmlsZXByaXZhdGVcIiwgXCJwcml2YXRlXCIsIFwiZGVpbml0XCIsIFwiaW5pdFwiLCBcIm5ld1wiLCBcIm92ZXJyaWRlXCIsIFwic2VsZlwiLCBcInN1YnNjcmlwdFwiLCBcInN1cGVyXCIsIFwiY29udmVuaWVuY2VcIiwgXCJkeW5hbWljXCIsIFwiZmluYWxcIiwgXCJpbmRpcmVjdFwiLCBcImxhenlcIiwgXCJyZXF1aXJlZFwiLCBcInN0YXRpY1wiLCBcInVub3duZWRcIiwgXCJ1bm93bmVkKHNhZmUpXCIsIFwidW5vd25lZCh1bnNhZmUpXCIsIFwid2Vha1wiLCBcImFzXCIsIFwiaXNcIiwgXCJicmVha1wiLCBcImNhc2VcIiwgXCJjb250aW51ZVwiLCBcImRlZmF1bHRcIiwgXCJlbHNlXCIsIFwiZmFsbHRocm91Z2hcIiwgXCJmb3JcIiwgXCJndWFyZFwiLCBcImlmXCIsIFwiaW5cIiwgXCJyZXBlYXRcIiwgXCJzd2l0Y2hcIiwgXCJ3aGVyZVwiLCBcIndoaWxlXCIsIFwiZGVmZXJcIiwgXCJyZXR1cm5cIiwgXCJpbm91dFwiLCBcIm11dGF0aW5nXCIsIFwibm9ubXV0YXRpbmdcIiwgXCJpc29sYXRlZFwiLCBcIm5vbmlzb2xhdGVkXCIsIFwiY2F0Y2hcIiwgXCJkb1wiLCBcInJldGhyb3dzXCIsIFwidGhyb3dcIiwgXCJ0aHJvd3NcIiwgXCJhc3luY1wiLCBcImF3YWl0XCIsIFwidHJ5XCIsIFwiZGlkU2V0XCIsIFwiZ2V0XCIsIFwic2V0XCIsIFwid2lsbFNldFwiLCBcImFzc2lnbm1lbnRcIiwgXCJhc3NvY2lhdGl2aXR5XCIsIFwiaW5maXhcIiwgXCJsZWZ0XCIsIFwibm9uZVwiLCBcIm9wZXJhdG9yXCIsIFwicG9zdGZpeFwiLCBcInByZWNlZGVuY2VcIiwgXCJwcmVjZWRlbmNlZ3JvdXBcIiwgXCJwcmVmaXhcIiwgXCJyaWdodFwiLCBcIkFueVwiLCBcIkFueU9iamVjdFwiLCBcIlR5cGVcIiwgXCJkeW5hbWljVHlwZVwiLCBcIlNlbGZcIiwgXCJQcm90b2NvbFwiLCBcIl9fQ09MVU1OX19cIiwgXCJfX0ZJTEVfX1wiLCBcIl9fRlVOQ1RJT05fX1wiLCBcIl9fTElORV9fXCJdKTtcbnZhciBkZWZpbmluZ0tleXdvcmRzID0gd29yZFNldChbXCJ2YXJcIiwgXCJsZXRcIiwgXCJhY3RvclwiLCBcImNsYXNzXCIsIFwiZW51bVwiLCBcImV4dGVuc2lvblwiLCBcImltcG9ydFwiLCBcInByb3RvY29sXCIsIFwic3RydWN0XCIsIFwiZnVuY1wiLCBcInR5cGVhbGlhc1wiLCBcImFzc29jaWF0ZWR0eXBlXCIsIFwiZm9yXCJdKTtcbnZhciBhdG9tcyA9IHdvcmRTZXQoW1widHJ1ZVwiLCBcImZhbHNlXCIsIFwibmlsXCIsIFwic2VsZlwiLCBcInN1cGVyXCIsIFwiX1wiXSk7XG52YXIgdHlwZXMgPSB3b3JkU2V0KFtcIkFycmF5XCIsIFwiQm9vbFwiLCBcIkNoYXJhY3RlclwiLCBcIkRpY3Rpb25hcnlcIiwgXCJEb3VibGVcIiwgXCJGbG9hdFwiLCBcIkludFwiLCBcIkludDhcIiwgXCJJbnQxNlwiLCBcIkludDMyXCIsIFwiSW50NjRcIiwgXCJOZXZlclwiLCBcIk9wdGlvbmFsXCIsIFwiU2V0XCIsIFwiU3RyaW5nXCIsIFwiVUludDhcIiwgXCJVSW50MTZcIiwgXCJVSW50MzJcIiwgXCJVSW50NjRcIiwgXCJWb2lkXCJdKTtcbnZhciBvcGVyYXRvcnMgPSBcIistLyolPXwmPD5+Xj8hXCI7XG52YXIgcHVuYyA9IFwiOjssLigpe31bXVwiO1xudmFyIGJpbmFyeSA9IC9eXFwtPzBiWzAxXVswMV9dKi87XG52YXIgb2N0YWwgPSAvXlxcLT8wb1swLTddWzAtN19dKi87XG52YXIgaGV4YWRlY2ltYWwgPSAvXlxcLT8weFtcXGRBLUZhLWZdW1xcZEEtRmEtZl9dKig/Oig/OlxcLltcXGRBLUZhLWZdW1xcZEEtRmEtZl9dKik/W1BwXVxcLT9cXGRbXFxkX10qKT8vO1xudmFyIGRlY2ltYWwgPSAvXlxcLT9cXGRbXFxkX10qKD86XFwuXFxkW1xcZF9dKik/KD86W0VlXVxcLT9cXGRbXFxkX10qKT8vO1xudmFyIGlkZW50aWZpZXIgPSAvXlxcJFxcZCt8KGA/KVtfQS1aYS16XVtfQS1aYS16JDAtOV0qXFwxLztcbnZhciBwcm9wZXJ0eSA9IC9eXFwuKD86XFwkXFxkK3woYD8pW19BLVphLXpdW19BLVphLXokMC05XSpcXDEpLztcbnZhciBpbnN0cnVjdGlvbiA9IC9eXFwjW0EtWmEtel0rLztcbnZhciBhdHRyaWJ1dGUgPSAvXkAoPzpcXCRcXGQrfChgPylbX0EtWmEtel1bX0EtWmEteiQwLTldKlxcMSkvO1xuLy92YXIgcmVnZXhwID0gL15cXC8oPyFcXHMpKD86XFwvXFwvKT8oPzpcXFxcLnxbXlxcL10pK1xcLy9cblxuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUsIHByZXYpIHtcbiAgaWYgKHN0cmVhbS5zb2woKSkgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgdmFyIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgaWYgKGNoID09IFwiL1wiKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChcIi8vXCIpKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goXCIvKlwiKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUucHVzaCh0b2tlbkNvbW1lbnQpO1xuICAgICAgcmV0dXJuIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChpbnN0cnVjdGlvbikpIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgaWYgKHN0cmVhbS5tYXRjaChhdHRyaWJ1dGUpKSByZXR1cm4gXCJhdHRyaWJ1dGVcIjtcbiAgaWYgKHN0cmVhbS5tYXRjaChiaW5hcnkpKSByZXR1cm4gXCJudW1iZXJcIjtcbiAgaWYgKHN0cmVhbS5tYXRjaChvY3RhbCkpIHJldHVybiBcIm51bWJlclwiO1xuICBpZiAoc3RyZWFtLm1hdGNoKGhleGFkZWNpbWFsKSkgcmV0dXJuIFwibnVtYmVyXCI7XG4gIGlmIChzdHJlYW0ubWF0Y2goZGVjaW1hbCkpIHJldHVybiBcIm51bWJlclwiO1xuICBpZiAoc3RyZWFtLm1hdGNoKHByb3BlcnR5KSkgcmV0dXJuIFwicHJvcGVydHlcIjtcbiAgaWYgKG9wZXJhdG9ycy5pbmRleE9mKGNoKSA+IC0xKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9XG4gIGlmIChwdW5jLmluZGV4T2YoY2gpID4gLTEpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHN0cmVhbS5tYXRjaChcIi4uXCIpO1xuICAgIHJldHVybiBcInB1bmN0dWF0aW9uXCI7XG4gIH1cbiAgdmFyIHN0cmluZ01hdGNoO1xuICBpZiAoc3RyaW5nTWF0Y2ggPSBzdHJlYW0ubWF0Y2goLyhcIlwiXCJ8XCJ8JykvKSkge1xuICAgIHZhciB0b2tlbml6ZSA9IHRva2VuU3RyaW5nLmJpbmQobnVsbCwgc3RyaW5nTWF0Y2hbMF0pO1xuICAgIHN0YXRlLnRva2VuaXplLnB1c2godG9rZW5pemUpO1xuICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGlkZW50aWZpZXIpKSB7XG4gICAgdmFyIGlkZW50ID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICBpZiAodHlwZXMuaGFzT3duUHJvcGVydHkoaWRlbnQpKSByZXR1cm4gXCJ0eXBlXCI7XG4gICAgaWYgKGF0b21zLmhhc093blByb3BlcnR5KGlkZW50KSkgcmV0dXJuIFwiYXRvbVwiO1xuICAgIGlmIChrZXl3b3Jkcy5oYXNPd25Qcm9wZXJ0eShpZGVudCkpIHtcbiAgICAgIGlmIChkZWZpbmluZ0tleXdvcmRzLmhhc093blByb3BlcnR5KGlkZW50KSkgc3RhdGUucHJldiA9IFwiZGVmaW5lXCI7XG4gICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgfVxuICAgIGlmIChwcmV2ID09IFwiZGVmaW5lXCIpIHJldHVybiBcImRlZlwiO1xuICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gIH1cbiAgc3RyZWFtLm5leHQoKTtcbiAgcmV0dXJuIG51bGw7XG59XG5mdW5jdGlvbiB0b2tlblVudGlsQ2xvc2luZ1BhcmVuKCkge1xuICB2YXIgZGVwdGggPSAwO1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUsIHByZXYpIHtcbiAgICB2YXIgaW5uZXIgPSB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSwgcHJldik7XG4gICAgaWYgKGlubmVyID09IFwicHVuY3R1YXRpb25cIikge1xuICAgICAgaWYgKHN0cmVhbS5jdXJyZW50KCkgPT0gXCIoXCIpICsrZGVwdGg7ZWxzZSBpZiAoc3RyZWFtLmN1cnJlbnQoKSA9PSBcIilcIikge1xuICAgICAgICBpZiAoZGVwdGggPT0gMCkge1xuICAgICAgICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgICAgICAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gICAgICAgICAgcmV0dXJuIHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgICB9IGVsc2UgLS1kZXB0aDtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGlubmVyO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcob3BlblF1b3RlLCBzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBzaW5nbGVMaW5lID0gb3BlblF1b3RlLmxlbmd0aCA9PSAxO1xuICB2YXIgY2gsXG4gICAgZXNjYXBlZCA9IGZhbHNlO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ucGVlaygpKSB7XG4gICAgaWYgKGVzY2FwZWQpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBpZiAoY2ggPT0gXCIoXCIpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUucHVzaCh0b2tlblVudGlsQ2xvc2luZ1BhcmVuKCkpO1xuICAgICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSBmYWxzZTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaChvcGVuUXVvdGUpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgZXNjYXBlZCA9IGNoID09IFwiXFxcXFwiO1xuICAgIH1cbiAgfVxuICBpZiAoc2luZ2xlTGluZSkge1xuICAgIHN0YXRlLnRva2VuaXplLnBvcCgpO1xuICB9XG4gIHJldHVybiBcInN0cmluZ1wiO1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09PSBcIi9cIiAmJiBzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUucHVzaCh0b2tlbkNvbW1lbnQpO1xuICAgIH0gZWxzZSBpZiAoY2ggPT09IFwiKlwiICYmIHN0cmVhbS5lYXQoXCIvXCIpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5mdW5jdGlvbiBDb250ZXh0KHByZXYsIGFsaWduLCBpbmRlbnRlZCkge1xuICB0aGlzLnByZXYgPSBwcmV2O1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMuaW5kZW50ZWQgPSBpbmRlbnRlZDtcbn1cbmZ1bmN0aW9uIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0pIHtcbiAgdmFyIGFsaWduID0gc3RyZWFtLm1hdGNoKC9eXFxzKigkfFxcL1tcXC9cXCpdfFspfVxcXV0pLywgZmFsc2UpID8gbnVsbCA6IHN0cmVhbS5jb2x1bW4oKSArIDE7XG4gIHN0YXRlLmNvbnRleHQgPSBuZXcgQ29udGV4dChzdGF0ZS5jb250ZXh0LCBhbGlnbiwgc3RhdGUuaW5kZW50ZWQpO1xufVxuZnVuY3Rpb24gcG9wQ29udGV4dChzdGF0ZSkge1xuICBpZiAoc3RhdGUuY29udGV4dCkge1xuICAgIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgICBzdGF0ZS5jb250ZXh0ID0gc3RhdGUuY29udGV4dC5wcmV2O1xuICB9XG59XG5leHBvcnQgY29uc3Qgc3dpZnQgPSB7XG4gIG5hbWU6IFwic3dpZnRcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICBwcmV2OiBudWxsLFxuICAgICAgY29udGV4dDogbnVsbCxcbiAgICAgIGluZGVudGVkOiAwLFxuICAgICAgdG9rZW5pemU6IFtdXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIHByZXYgPSBzdGF0ZS5wcmV2O1xuICAgIHN0YXRlLnByZXYgPSBudWxsO1xuICAgIHZhciB0b2tlbml6ZSA9IHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdIHx8IHRva2VuQmFzZTtcbiAgICB2YXIgc3R5bGUgPSB0b2tlbml6ZShzdHJlYW0sIHN0YXRlLCBwcmV2KTtcbiAgICBpZiAoIXN0eWxlIHx8IHN0eWxlID09IFwiY29tbWVudFwiKSBzdGF0ZS5wcmV2ID0gcHJldjtlbHNlIGlmICghc3RhdGUucHJldikgc3RhdGUucHJldiA9IHN0eWxlO1xuICAgIGlmIChzdHlsZSA9PSBcInB1bmN0dWF0aW9uXCIpIHtcbiAgICAgIHZhciBicmFja2V0ID0gL1tcXChcXFtcXHtdfChbXFxdXFwpXFx9XSkvLmV4ZWMoc3RyZWFtLmN1cnJlbnQoKSk7XG4gICAgICBpZiAoYnJhY2tldCkgKGJyYWNrZXRbMV0gPyBwb3BDb250ZXh0IDogcHVzaENvbnRleHQpKHN0YXRlLCBzdHJlYW0pO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGlDeCkge1xuICAgIHZhciBjeCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgaWYgKCFjeCkgcmV0dXJuIDA7XG4gICAgdmFyIGNsb3NpbmcgPSAvXltcXF1cXH1cXCldLy50ZXN0KHRleHRBZnRlcik7XG4gICAgaWYgKGN4LmFsaWduICE9IG51bGwpIHJldHVybiBjeC5hbGlnbiAtIChjbG9zaW5nID8gMSA6IDApO1xuICAgIHJldHVybiBjeC5pbmRlbnRlZCArIChjbG9zaW5nID8gMCA6IGlDeC51bml0KTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgaW5kZW50T25JbnB1dDogL15cXHMqW1xcKVxcfVxcXV0kLyxcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIi8vXCIsXG4gICAgICBibG9jazoge1xuICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgIH1cbiAgICB9LFxuICAgIGNsb3NlQnJhY2tldHM6IHtcbiAgICAgIGJyYWNrZXRzOiBbXCIoXCIsIFwiW1wiLCBcIntcIiwgXCInXCIsICdcIicsIFwiYFwiXVxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9