"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[8776],{

/***/ 78776
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   sieve: () => (/* binding */ sieve)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = words("if elsif else stop require");
var atoms = words("true false not");
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == "/" && stream.eat("*")) {
    state.tokenize = tokenCComment;
    return tokenCComment(stream, state);
  }
  if (ch === '#') {
    stream.skipToEnd();
    return "comment";
  }
  if (ch == "\"") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (ch == "(") {
    state._indent.push("(");
    // add virtual angel wings so that editor behaves...
    // ...more sane incase of broken brackets
    state._indent.push("{");
    return null;
  }
  if (ch === "{") {
    state._indent.push("{");
    return null;
  }
  if (ch == ")") {
    state._indent.pop();
    state._indent.pop();
  }
  if (ch === "}") {
    state._indent.pop();
    return null;
  }
  if (ch == ",") return null;
  if (ch == ";") return null;
  if (/[{}\(\),;]/.test(ch)) return null;

  // 1*DIGIT "K" / "M" / "G"
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\d]/);
    stream.eat(/[KkMmGg]/);
    return "number";
  }

  // ":" (ALPHA / "_") *(ALPHA / DIGIT / "_")
  if (ch == ":") {
    stream.eatWhile(/[a-zA-Z_]/);
    stream.eatWhile(/[a-zA-Z0-9_]/);
    return "operator";
  }
  stream.eatWhile(/\w/);
  var cur = stream.current();

  // "text:" *(SP / HTAB) (hash-comment / CRLF)
  // *(multiline-literal / multiline-dotstart)
  // "." CRLF
  if (cur == "text" && stream.eat(":")) {
    state.tokenize = tokenMultiLineString;
    return "string";
  }
  if (keywords.propertyIsEnumerable(cur)) return "keyword";
  if (atoms.propertyIsEnumerable(cur)) return "atom";
  return null;
}
function tokenMultiLineString(stream, state) {
  state._multiLineString = true;
  // the first line is special it may contain a comment
  if (!stream.sol()) {
    stream.eatSpace();
    if (stream.peek() == "#") {
      stream.skipToEnd();
      return "comment";
    }
    stream.skipToEnd();
    return "string";
  }
  if (stream.next() == "." && stream.eol()) {
    state._multiLineString = false;
    state.tokenize = tokenBase;
  }
  return "string";
}
function tokenCComment(stream, state) {
  var maybeEnd = false,
    ch;
  while ((ch = stream.next()) != null) {
    if (maybeEnd && ch == "/") {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch == quote && !escaped) break;
      escaped = !escaped && ch == "\\";
    }
    if (!escaped) state.tokenize = tokenBase;
    return "string";
  };
}
const sieve = {
  name: "sieve",
  startState: function (base) {
    return {
      tokenize: tokenBase,
      baseIndent: base || 0,
      _indent: []
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return (state.tokenize || tokenBase)(stream, state);
  },
  indent: function (state, _textAfter, cx) {
    var length = state._indent.length;
    if (_textAfter && _textAfter[0] == "}") length--;
    if (length < 0) length = 0;
    return length * cx.unit;
  },
  languageData: {
    indentOnInput: /^\s*\}$/
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiODc3Ni5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9zaWV2ZS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiIFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBvYmo7XG59XG52YXIga2V5d29yZHMgPSB3b3JkcyhcImlmIGVsc2lmIGVsc2Ugc3RvcCByZXF1aXJlXCIpO1xudmFyIGF0b21zID0gd29yZHMoXCJ0cnVlIGZhbHNlIG5vdFwiKTtcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSBcIi9cIiAmJiBzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5DQ29tbWVudDtcbiAgICByZXR1cm4gdG9rZW5DQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoY2ggPT09ICcjJykge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKGNoID09IFwiXFxcIlwiKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChjaCA9PSBcIihcIikge1xuICAgIHN0YXRlLl9pbmRlbnQucHVzaChcIihcIik7XG4gICAgLy8gYWRkIHZpcnR1YWwgYW5nZWwgd2luZ3Mgc28gdGhhdCBlZGl0b3IgYmVoYXZlcy4uLlxuICAgIC8vIC4uLm1vcmUgc2FuZSBpbmNhc2Ugb2YgYnJva2VuIGJyYWNrZXRzXG4gICAgc3RhdGUuX2luZGVudC5wdXNoKFwie1wiKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBpZiAoY2ggPT09IFwie1wiKSB7XG4gICAgc3RhdGUuX2luZGVudC5wdXNoKFwie1wiKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBpZiAoY2ggPT0gXCIpXCIpIHtcbiAgICBzdGF0ZS5faW5kZW50LnBvcCgpO1xuICAgIHN0YXRlLl9pbmRlbnQucG9wKCk7XG4gIH1cbiAgaWYgKGNoID09PSBcIn1cIikge1xuICAgIHN0YXRlLl9pbmRlbnQucG9wKCk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKGNoID09IFwiLFwiKSByZXR1cm4gbnVsbDtcbiAgaWYgKGNoID09IFwiO1wiKSByZXR1cm4gbnVsbDtcbiAgaWYgKC9be31cXChcXCksO10vLnRlc3QoY2gpKSByZXR1cm4gbnVsbDtcblxuICAvLyAxKkRJR0lUIFwiS1wiIC8gXCJNXCIgLyBcIkdcIlxuICBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXGRdLyk7XG4gICAgc3RyZWFtLmVhdCgvW0trTW1HZ10vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuXG4gIC8vIFwiOlwiIChBTFBIQSAvIFwiX1wiKSAqKEFMUEhBIC8gRElHSVQgLyBcIl9cIilcbiAgaWYgKGNoID09IFwiOlwiKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bYS16QS1aX10vKTtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1thLXpBLVowLTlfXS8pO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cbiAgc3RyZWFtLmVhdFdoaWxlKC9cXHcvKTtcbiAgdmFyIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG5cbiAgLy8gXCJ0ZXh0OlwiICooU1AgLyBIVEFCKSAoaGFzaC1jb21tZW50IC8gQ1JMRilcbiAgLy8gKihtdWx0aWxpbmUtbGl0ZXJhbCAvIG11bHRpbGluZS1kb3RzdGFydClcbiAgLy8gXCIuXCIgQ1JMRlxuICBpZiAoY3VyID09IFwidGV4dFwiICYmIHN0cmVhbS5lYXQoXCI6XCIpKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbk11bHRpTGluZVN0cmluZztcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfVxuICBpZiAoa2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICByZXR1cm4gbnVsbDtcbn1cbmZ1bmN0aW9uIHRva2VuTXVsdGlMaW5lU3RyaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgc3RhdGUuX211bHRpTGluZVN0cmluZyA9IHRydWU7XG4gIC8vIHRoZSBmaXJzdCBsaW5lIGlzIHNwZWNpYWwgaXQgbWF5IGNvbnRhaW4gYSBjb21tZW50XG4gIGlmICghc3RyZWFtLnNvbCgpKSB7XG4gICAgc3RyZWFtLmVhdFNwYWNlKCk7XG4gICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gXCIjXCIpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9XG4gIGlmIChzdHJlYW0ubmV4dCgpID09IFwiLlwiICYmIHN0cmVhbS5lb2woKSkge1xuICAgIHN0YXRlLl9tdWx0aUxpbmVTdHJpbmcgPSBmYWxzZTtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgfVxuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cbmZ1bmN0aW9uIHRva2VuQ0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAobWF5YmVFbmQgJiYgY2ggPT0gXCIvXCIpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlICgoY2ggPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAoY2ggPT0gcXVvdGUgJiYgIWVzY2FwZWQpIGJyZWFrO1xuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIGNoID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoIWVzY2FwZWQpIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZXhwb3J0IGNvbnN0IHNpZXZlID0ge1xuICBuYW1lOiBcInNpZXZlXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uIChiYXNlKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBiYXNlSW5kZW50OiBiYXNlIHx8IDAsXG4gICAgICBfaW5kZW50OiBbXVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgcmV0dXJuIChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgX3RleHRBZnRlciwgY3gpIHtcbiAgICB2YXIgbGVuZ3RoID0gc3RhdGUuX2luZGVudC5sZW5ndGg7XG4gICAgaWYgKF90ZXh0QWZ0ZXIgJiYgX3RleHRBZnRlclswXSA9PSBcIn1cIikgbGVuZ3RoLS07XG4gICAgaWYgKGxlbmd0aCA8IDApIGxlbmd0aCA9IDA7XG4gICAgcmV0dXJuIGxlbmd0aCAqIGN4LnVuaXQ7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGluZGVudE9uSW5wdXQ6IC9eXFxzKlxcfSQvXG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==