"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[210],{

/***/ 90210
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   go: () => (/* binding */ go)
/* harmony export */ });
var keywords = {
  "break": true,
  "case": true,
  "chan": true,
  "const": true,
  "continue": true,
  "default": true,
  "defer": true,
  "else": true,
  "fallthrough": true,
  "for": true,
  "func": true,
  "go": true,
  "goto": true,
  "if": true,
  "import": true,
  "interface": true,
  "map": true,
  "package": true,
  "range": true,
  "return": true,
  "select": true,
  "struct": true,
  "switch": true,
  "type": true,
  "var": true,
  "bool": true,
  "byte": true,
  "complex64": true,
  "complex128": true,
  "float32": true,
  "float64": true,
  "int8": true,
  "int16": true,
  "int32": true,
  "int64": true,
  "string": true,
  "uint8": true,
  "uint16": true,
  "uint32": true,
  "uint64": true,
  "int": true,
  "uint": true,
  "uintptr": true,
  "error": true,
  "rune": true,
  "any": true,
  "comparable": true
};
var atoms = {
  "true": true,
  "false": true,
  "iota": true,
  "nil": true,
  "append": true,
  "cap": true,
  "close": true,
  "complex": true,
  "copy": true,
  "delete": true,
  "imag": true,
  "len": true,
  "make": true,
  "new": true,
  "panic": true,
  "print": true,
  "println": true,
  "real": true,
  "recover": true
};
var isOperatorChar = /[+\-*&^%:=<>!|\/]/;
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == '"' || ch == "'" || ch == "`") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\d\.]/.test(ch)) {
    if (ch == ".") {
      stream.match(/^[0-9]+([eE][\-+]?[0-9]+)?/);
    } else if (ch == "0") {
      stream.match(/^[xX][0-9a-fA-F]+/) || stream.match(/^0[0-7]+/);
    } else {
      stream.match(/^[0-9]*\.?[0-9]*([eE][\-+]?[0-9]+)?/);
    }
    return "number";
  }
  if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
    curPunc = ch;
    return null;
  }
  if (ch == "/") {
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
    if (cur == "case" || cur == "default") curPunc = "case";
    return "keyword";
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
      escaped = !escaped && quote != "`" && next == "\\";
    }
    if (end || !(escaped || quote == "`")) state.tokenize = tokenBase;
    return "string";
  };
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "*";
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
  return state.context = new Context(state.indented, col, type, null, state.context);
}
function popContext(state) {
  if (!state.context.prev) return;
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

// Interface

const go = {
  name: "go",
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
      if (ctx.type == "case") ctx.type = "}";
    }
    if (stream.eatSpace()) return null;
    curPunc = null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment") return style;
    if (ctx.align == null) ctx.align = true;
    if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "case") ctx.type = "case";else if (curPunc == "}" && ctx.type == "}") popContext(state);else if (curPunc == ctx.type) popContext(state);
    state.startOfLine = false;
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != tokenBase && state.tokenize != null) return null;
    var ctx = state.context,
      firstChar = textAfter && textAfter.charAt(0);
    if (ctx.type == "case" && /^(?:case|default)\b/.test(textAfter)) return ctx.indented;
    var closing = firstChar == ctx.type;
    if (ctx.align) return ctx.column + (closing ? 0 : 1);else return ctx.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    indentOnInput: /^\s([{}]|case |default\s*:)$/,
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjEwLmp1cHl0ZXItdmlld2VyLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9nby5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIga2V5d29yZHMgPSB7XG4gIFwiYnJlYWtcIjogdHJ1ZSxcbiAgXCJjYXNlXCI6IHRydWUsXG4gIFwiY2hhblwiOiB0cnVlLFxuICBcImNvbnN0XCI6IHRydWUsXG4gIFwiY29udGludWVcIjogdHJ1ZSxcbiAgXCJkZWZhdWx0XCI6IHRydWUsXG4gIFwiZGVmZXJcIjogdHJ1ZSxcbiAgXCJlbHNlXCI6IHRydWUsXG4gIFwiZmFsbHRocm91Z2hcIjogdHJ1ZSxcbiAgXCJmb3JcIjogdHJ1ZSxcbiAgXCJmdW5jXCI6IHRydWUsXG4gIFwiZ29cIjogdHJ1ZSxcbiAgXCJnb3RvXCI6IHRydWUsXG4gIFwiaWZcIjogdHJ1ZSxcbiAgXCJpbXBvcnRcIjogdHJ1ZSxcbiAgXCJpbnRlcmZhY2VcIjogdHJ1ZSxcbiAgXCJtYXBcIjogdHJ1ZSxcbiAgXCJwYWNrYWdlXCI6IHRydWUsXG4gIFwicmFuZ2VcIjogdHJ1ZSxcbiAgXCJyZXR1cm5cIjogdHJ1ZSxcbiAgXCJzZWxlY3RcIjogdHJ1ZSxcbiAgXCJzdHJ1Y3RcIjogdHJ1ZSxcbiAgXCJzd2l0Y2hcIjogdHJ1ZSxcbiAgXCJ0eXBlXCI6IHRydWUsXG4gIFwidmFyXCI6IHRydWUsXG4gIFwiYm9vbFwiOiB0cnVlLFxuICBcImJ5dGVcIjogdHJ1ZSxcbiAgXCJjb21wbGV4NjRcIjogdHJ1ZSxcbiAgXCJjb21wbGV4MTI4XCI6IHRydWUsXG4gIFwiZmxvYXQzMlwiOiB0cnVlLFxuICBcImZsb2F0NjRcIjogdHJ1ZSxcbiAgXCJpbnQ4XCI6IHRydWUsXG4gIFwiaW50MTZcIjogdHJ1ZSxcbiAgXCJpbnQzMlwiOiB0cnVlLFxuICBcImludDY0XCI6IHRydWUsXG4gIFwic3RyaW5nXCI6IHRydWUsXG4gIFwidWludDhcIjogdHJ1ZSxcbiAgXCJ1aW50MTZcIjogdHJ1ZSxcbiAgXCJ1aW50MzJcIjogdHJ1ZSxcbiAgXCJ1aW50NjRcIjogdHJ1ZSxcbiAgXCJpbnRcIjogdHJ1ZSxcbiAgXCJ1aW50XCI6IHRydWUsXG4gIFwidWludHB0clwiOiB0cnVlLFxuICBcImVycm9yXCI6IHRydWUsXG4gIFwicnVuZVwiOiB0cnVlLFxuICBcImFueVwiOiB0cnVlLFxuICBcImNvbXBhcmFibGVcIjogdHJ1ZVxufTtcbnZhciBhdG9tcyA9IHtcbiAgXCJ0cnVlXCI6IHRydWUsXG4gIFwiZmFsc2VcIjogdHJ1ZSxcbiAgXCJpb3RhXCI6IHRydWUsXG4gIFwibmlsXCI6IHRydWUsXG4gIFwiYXBwZW5kXCI6IHRydWUsXG4gIFwiY2FwXCI6IHRydWUsXG4gIFwiY2xvc2VcIjogdHJ1ZSxcbiAgXCJjb21wbGV4XCI6IHRydWUsXG4gIFwiY29weVwiOiB0cnVlLFxuICBcImRlbGV0ZVwiOiB0cnVlLFxuICBcImltYWdcIjogdHJ1ZSxcbiAgXCJsZW5cIjogdHJ1ZSxcbiAgXCJtYWtlXCI6IHRydWUsXG4gIFwibmV3XCI6IHRydWUsXG4gIFwicGFuaWNcIjogdHJ1ZSxcbiAgXCJwcmludFwiOiB0cnVlLFxuICBcInByaW50bG5cIjogdHJ1ZSxcbiAgXCJyZWFsXCI6IHRydWUsXG4gIFwicmVjb3ZlclwiOiB0cnVlXG59O1xudmFyIGlzT3BlcmF0b3JDaGFyID0gL1srXFwtKiZeJTo9PD4hfFxcL10vO1xudmFyIGN1clB1bmM7XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoY2ggPT0gJ1wiJyB8fCBjaCA9PSBcIidcIiB8fCBjaCA9PSBcImBcIikge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmcoY2gpO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoL1tcXGRcXC5dLy50ZXN0KGNoKSkge1xuICAgIGlmIChjaCA9PSBcIi5cIikge1xuICAgICAgc3RyZWFtLm1hdGNoKC9eWzAtOV0rKFtlRV1bXFwtK10/WzAtOV0rKT8vKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiMFwiKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15beFhdWzAtOWEtZkEtRl0rLykgfHwgc3RyZWFtLm1hdGNoKC9eMFswLTddKy8pO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15bMC05XSpcXC4/WzAtOV0qKFtlRV1bXFwtK10/WzAtOV0rKT8vKTtcbiAgICB9XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgaWYgKC9bXFxbXFxde31cXChcXCksO1xcOlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgY3VyUHVuYyA9IGNoO1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmIChjaCA9PSBcIi9cIikge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnQ7XG4gICAgICByZXR1cm4gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gIH1cbiAgaWYgKGlzT3BlcmF0b3JDaGFyLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKGlzT3BlcmF0b3JDaGFyKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF9cXHhhMS1cXHVmZmZmXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHtcbiAgICBpZiAoY3VyID09IFwiY2FzZVwiIHx8IGN1ciA9PSBcImRlZmF1bHRcIikgY3VyUHVuYyA9IFwiY2FzZVwiO1xuICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgfVxuICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQsXG4gICAgICBlbmQgPSBmYWxzZTtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBxdW90ZSAhPSBcImBcIiAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoZW5kIHx8ICEoZXNjYXBlZCB8fCBxdW90ZSA9PSBcImBcIikpIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIvXCIgJiYgbWF5YmVFbmQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gQ29udGV4dChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBhbGlnbiwgcHJldikge1xuICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMucHJldiA9IHByZXY7XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlKSB7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoc3RhdGUuaW5kZW50ZWQsIGNvbCwgdHlwZSwgbnVsbCwgc3RhdGUuY29udGV4dCk7XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KHN0YXRlKSB7XG4gIGlmICghc3RhdGUuY29udGV4dC5wcmV2KSByZXR1cm47XG4gIHZhciB0ID0gc3RhdGUuY29udGV4dC50eXBlO1xuICBpZiAodCA9PSBcIilcIiB8fCB0ID09IFwiXVwiIHx8IHQgPT0gXCJ9XCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG59XG5cbi8vIEludGVyZmFjZVxuXG5leHBvcnQgY29uc3QgZ28gPSB7XG4gIG5hbWU6IFwiZ29cIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKGluZGVudFVuaXQpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IG51bGwsXG4gICAgICBjb250ZXh0OiBuZXcgQ29udGV4dCgtaW5kZW50VW5pdCwgMCwgXCJ0b3BcIiwgZmFsc2UpLFxuICAgICAgaW5kZW50ZWQ6IDAsXG4gICAgICBzdGFydE9mTGluZTogdHJ1ZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0O1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gZmFsc2U7XG4gICAgICBzdGF0ZS5pbmRlbnRlZCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgICAgaWYgKGN0eC50eXBlID09IFwiY2FzZVwiKSBjdHgudHlwZSA9IFwifVwiO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIGN1clB1bmMgPSBudWxsO1xuICAgIHZhciBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PSBcImNvbW1lbnRcIikgcmV0dXJuIHN0eWxlO1xuICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gdHJ1ZTtcbiAgICBpZiAoY3VyUHVuYyA9PSBcIntcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJ9XCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJbXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiXVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwiKFwiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIilcIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcImNhc2VcIikgY3R4LnR5cGUgPSBcImNhc2VcIjtlbHNlIGlmIChjdXJQdW5jID09IFwifVwiICYmIGN0eC50eXBlID09IFwifVwiKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmIChjdXJQdW5jID09IGN0eC50eXBlKSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICBzdGF0ZS5zdGFydE9mTGluZSA9IGZhbHNlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICBpZiAoc3RhdGUudG9rZW5pemUgIT0gdG9rZW5CYXNlICYmIHN0YXRlLnRva2VuaXplICE9IG51bGwpIHJldHVybiBudWxsO1xuICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0LFxuICAgICAgZmlyc3RDaGFyID0gdGV4dEFmdGVyICYmIHRleHRBZnRlci5jaGFyQXQoMCk7XG4gICAgaWYgKGN0eC50eXBlID09IFwiY2FzZVwiICYmIC9eKD86Y2FzZXxkZWZhdWx0KVxcYi8udGVzdCh0ZXh0QWZ0ZXIpKSByZXR1cm4gY3R4LmluZGVudGVkO1xuICAgIHZhciBjbG9zaW5nID0gZmlyc3RDaGFyID09IGN0eC50eXBlO1xuICAgIGlmIChjdHguYWxpZ24pIHJldHVybiBjdHguY29sdW1uICsgKGNsb3NpbmcgPyAwIDogMSk7ZWxzZSByZXR1cm4gY3R4LmluZGVudGVkICsgKGNsb3NpbmcgPyAwIDogY3gudW5pdCk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGluZGVudE9uSW5wdXQ6IC9eXFxzKFt7fV18Y2FzZSB8ZGVmYXVsdFxccyo6KSQvLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiLy9cIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiLypcIixcbiAgICAgICAgY2xvc2U6IFwiKi9cIlxuICAgICAgfVxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9