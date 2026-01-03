"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1938],{

/***/ 61938
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   turtle: () => (/* binding */ turtle)
/* harmony export */ });
var curPunc;
function wordRegexp(words) {
  return new RegExp("^(?:" + words.join("|") + ")$", "i");
}
var ops = wordRegexp([]);
var keywords = wordRegexp(["@prefix", "@base", "a"]);
var operatorChars = /[*+\-<>=&|]/;
function tokenBase(stream, state) {
  var ch = stream.next();
  curPunc = null;
  if (ch == "<" && !stream.match(/^[\s\u00a0=]/, false)) {
    stream.match(/^[^\s\u00a0>]*>?/);
    return "atom";
  } else if (ch == "\"" || ch == "'") {
    state.tokenize = tokenLiteral(ch);
    return state.tokenize(stream, state);
  } else if (/[{}\(\),\.;\[\]]/.test(ch)) {
    curPunc = ch;
    return null;
  } else if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  } else if (operatorChars.test(ch)) {
    stream.eatWhile(operatorChars);
    return null;
  } else if (ch == ":") {
    return "operator";
  } else {
    stream.eatWhile(/[_\w\d]/);
    if (stream.peek() == ":") {
      return "variableName.special";
    } else {
      var word = stream.current();
      if (keywords.test(word)) {
        return "meta";
      }
      if (ch >= "A" && ch <= "Z") {
        return "comment";
      } else {
        return "keyword";
      }
    }
    // removed by dead control flow
 var word; 
    // removed by dead control flow

  }
}
function tokenLiteral(quote) {
  return function (stream, state) {
    var escaped = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch == quote && !escaped) {
        state.tokenize = tokenBase;
        break;
      }
      escaped = !escaped && ch == "\\";
    }
    return "string";
  };
}
function pushContext(state, type, col) {
  state.context = {
    prev: state.context,
    indent: state.indent,
    col: col,
    type: type
  };
}
function popContext(state) {
  state.indent = state.context.indent;
  state.context = state.context.prev;
}
const turtle = {
  name: "turtle",
  startState: function () {
    return {
      tokenize: tokenBase,
      context: null,
      indent: 0,
      col: 0
    };
  },
  token: function (stream, state) {
    if (stream.sol()) {
      if (state.context && state.context.align == null) state.context.align = false;
      state.indent = stream.indentation();
    }
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    if (style != "comment" && state.context && state.context.align == null && state.context.type != "pattern") {
      state.context.align = true;
    }
    if (curPunc == "(") pushContext(state, ")", stream.column());else if (curPunc == "[") pushContext(state, "]", stream.column());else if (curPunc == "{") pushContext(state, "}", stream.column());else if (/[\]\}\)]/.test(curPunc)) {
      while (state.context && state.context.type == "pattern") popContext(state);
      if (state.context && curPunc == state.context.type) popContext(state);
    } else if (curPunc == "." && state.context && state.context.type == "pattern") popContext(state);else if (/atom|string|variable/.test(style) && state.context) {
      if (/[\}\]]/.test(state.context.type)) pushContext(state, "pattern", stream.column());else if (state.context.type == "pattern" && !state.context.align) {
        state.context.align = true;
        state.context.col = stream.column();
      }
    }
    return style;
  },
  indent: function (state, textAfter, cx) {
    var firstChar = textAfter && textAfter.charAt(0);
    var context = state.context;
    if (/[\]\}]/.test(firstChar)) while (context && context.type == "pattern") context = context.prev;
    var closing = context && firstChar == context.type;
    if (!context) return 0;else if (context.type == "pattern") return context.col;else if (context.align) return context.col + (closing ? 0 : 1);else return context.indent + (closing ? 0 : cx.unit);
  },
  languageData: {
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTkzOC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdHVydGxlLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBjdXJQdW5jO1xuZnVuY3Rpb24gd29yZFJlZ2V4cCh3b3Jkcykge1xuICByZXR1cm4gbmV3IFJlZ0V4cChcIl4oPzpcIiArIHdvcmRzLmpvaW4oXCJ8XCIpICsgXCIpJFwiLCBcImlcIik7XG59XG52YXIgb3BzID0gd29yZFJlZ2V4cChbXSk7XG52YXIga2V5d29yZHMgPSB3b3JkUmVnZXhwKFtcIkBwcmVmaXhcIiwgXCJAYmFzZVwiLCBcImFcIl0pO1xudmFyIG9wZXJhdG9yQ2hhcnMgPSAvWyorXFwtPD49JnxdLztcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGN1clB1bmMgPSBudWxsO1xuICBpZiAoY2ggPT0gXCI8XCIgJiYgIXN0cmVhbS5tYXRjaCgvXltcXHNcXHUwMGEwPV0vLCBmYWxzZSkpIHtcbiAgICBzdHJlYW0ubWF0Y2goL15bXlxcc1xcdTAwYTA+XSo+Py8pO1xuICAgIHJldHVybiBcImF0b21cIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIlxcXCJcIiB8fCBjaCA9PSBcIidcIikge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5MaXRlcmFsKGNoKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH0gZWxzZSBpZiAoL1t7fVxcKFxcKSxcXC47XFxbXFxdXS8udGVzdChjaCkpIHtcbiAgICBjdXJQdW5jID0gY2g7XG4gICAgcmV0dXJuIG51bGw7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9IGVsc2UgaWYgKG9wZXJhdG9yQ2hhcnMudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUob3BlcmF0b3JDaGFycyk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI6XCIpIHtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9IGVsc2Uge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW19cXHdcXGRdLyk7XG4gICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gXCI6XCIpIHtcbiAgICAgIHJldHVybiBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICAgIGlmIChrZXl3b3Jkcy50ZXN0KHdvcmQpKSB7XG4gICAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICAgIH1cbiAgICAgIGlmIChjaCA+PSBcIkFcIiAmJiBjaCA8PSBcIlpcIikge1xuICAgICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgICB9XG4gICAgfVxuICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICBpZiAob3BzLnRlc3Qod29yZCkpIHJldHVybiBudWxsO2Vsc2UgaWYgKGtleXdvcmRzLnRlc3Qod29yZCkpIHJldHVybiBcIm1ldGFcIjtlbHNlIHJldHVybiBcInZhcmlhYmxlXCI7XG4gIH1cbn1cbmZ1bmN0aW9uIHRva2VuTGl0ZXJhbChxdW90ZSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgY2g7XG4gICAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmIChjaCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgY2ggPT0gXCJcXFxcXCI7XG4gICAgfVxuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gcHVzaENvbnRleHQoc3RhdGUsIHR5cGUsIGNvbCkge1xuICBzdGF0ZS5jb250ZXh0ID0ge1xuICAgIHByZXY6IHN0YXRlLmNvbnRleHQsXG4gICAgaW5kZW50OiBzdGF0ZS5pbmRlbnQsXG4gICAgY29sOiBjb2wsXG4gICAgdHlwZTogdHlwZVxuICB9O1xufVxuZnVuY3Rpb24gcG9wQ29udGV4dChzdGF0ZSkge1xuICBzdGF0ZS5pbmRlbnQgPSBzdGF0ZS5jb250ZXh0LmluZGVudDtcbiAgc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbn1cbmV4cG9ydCBjb25zdCB0dXJ0bGUgPSB7XG4gIG5hbWU6IFwidHVydGxlXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IHRva2VuQmFzZSxcbiAgICAgIGNvbnRleHQ6IG51bGwsXG4gICAgICBpbmRlbnQ6IDAsXG4gICAgICBjb2w6IDBcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBpZiAoc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LmFsaWduID09IG51bGwpIHN0YXRlLmNvbnRleHQuYWxpZ24gPSBmYWxzZTtcbiAgICAgIHN0YXRlLmluZGVudCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIHZhciBzdHlsZSA9IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSAhPSBcImNvbW1lbnRcIiAmJiBzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQuYWxpZ24gPT0gbnVsbCAmJiBzdGF0ZS5jb250ZXh0LnR5cGUgIT0gXCJwYXR0ZXJuXCIpIHtcbiAgICAgIHN0YXRlLmNvbnRleHQuYWxpZ24gPSB0cnVlO1xuICAgIH1cbiAgICBpZiAoY3VyUHVuYyA9PSBcIihcIikgcHVzaENvbnRleHQoc3RhdGUsIFwiKVwiLCBzdHJlYW0uY29sdW1uKCkpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJbXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBcIl1cIiwgc3RyZWFtLmNvbHVtbigpKTtlbHNlIGlmIChjdXJQdW5jID09IFwie1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgXCJ9XCIsIHN0cmVhbS5jb2x1bW4oKSk7ZWxzZSBpZiAoL1tcXF1cXH1cXCldLy50ZXN0KGN1clB1bmMpKSB7XG4gICAgICB3aGlsZSAoc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LnR5cGUgPT0gXCJwYXR0ZXJuXCIpIHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgaWYgKHN0YXRlLmNvbnRleHQgJiYgY3VyUHVuYyA9PSBzdGF0ZS5jb250ZXh0LnR5cGUpIHBvcENvbnRleHQoc3RhdGUpO1xuICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBcIi5cIiAmJiBzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoL2F0b218c3RyaW5nfHZhcmlhYmxlLy50ZXN0KHN0eWxlKSAmJiBzdGF0ZS5jb250ZXh0KSB7XG4gICAgICBpZiAoL1tcXH1cXF1dLy50ZXN0KHN0YXRlLmNvbnRleHQudHlwZSkpIHB1c2hDb250ZXh0KHN0YXRlLCBcInBhdHRlcm5cIiwgc3RyZWFtLmNvbHVtbigpKTtlbHNlIGlmIChzdGF0ZS5jb250ZXh0LnR5cGUgPT0gXCJwYXR0ZXJuXCIgJiYgIXN0YXRlLmNvbnRleHQuYWxpZ24pIHtcbiAgICAgICAgc3RhdGUuY29udGV4dC5hbGlnbiA9IHRydWU7XG4gICAgICAgIHN0YXRlLmNvbnRleHQuY29sID0gc3RyZWFtLmNvbHVtbigpO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgdmFyIGZpcnN0Q2hhciA9IHRleHRBZnRlciAmJiB0ZXh0QWZ0ZXIuY2hhckF0KDApO1xuICAgIHZhciBjb250ZXh0ID0gc3RhdGUuY29udGV4dDtcbiAgICBpZiAoL1tcXF1cXH1dLy50ZXN0KGZpcnN0Q2hhcikpIHdoaWxlIChjb250ZXh0ICYmIGNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgY29udGV4dCA9IGNvbnRleHQucHJldjtcbiAgICB2YXIgY2xvc2luZyA9IGNvbnRleHQgJiYgZmlyc3RDaGFyID09IGNvbnRleHQudHlwZTtcbiAgICBpZiAoIWNvbnRleHQpIHJldHVybiAwO2Vsc2UgaWYgKGNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgcmV0dXJuIGNvbnRleHQuY29sO2Vsc2UgaWYgKGNvbnRleHQuYWxpZ24pIHJldHVybiBjb250ZXh0LmNvbCArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGNvbnRleHQuaW5kZW50ICsgKGNsb3NpbmcgPyAwIDogY3gudW5pdCk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=