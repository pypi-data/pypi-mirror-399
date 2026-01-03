"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9336],{

/***/ 59336
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   solr: () => (/* binding */ solr)
/* harmony export */ });
var isStringChar = /[^\s\|\!\+\-\*\?\~\^\&\:\(\)\[\]\{\}\"\\]/;
var isOperatorChar = /[\|\!\+\-\*\?\~\^\&]/;
var isOperatorString = /^(OR|AND|NOT|TO)$/;
function isNumber(word) {
  return parseFloat(word).toString() === word;
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      next;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) break;
      escaped = !escaped && next == "\\";
    }
    if (!escaped) state.tokenize = tokenBase;
    return "string";
  };
}
function tokenOperator(operator) {
  return function (stream, state) {
    if (operator == "|") stream.eat(/\|/);else if (operator == "&") stream.eat(/\&/);
    state.tokenize = tokenBase;
    return "operator";
  };
}
function tokenWord(ch) {
  return function (stream, state) {
    var word = ch;
    while ((ch = stream.peek()) && ch.match(isStringChar) != null) {
      word += stream.next();
    }
    state.tokenize = tokenBase;
    if (isOperatorString.test(word)) return "operator";else if (isNumber(word)) return "number";else if (stream.peek() == ":") return "propertyName";else return "string";
  };
}
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == '"') state.tokenize = tokenString(ch);else if (isOperatorChar.test(ch)) state.tokenize = tokenOperator(ch);else if (isStringChar.test(ch)) state.tokenize = tokenWord(ch);
  return state.tokenize != tokenBase ? state.tokenize(stream, state) : null;
}
const solr = {
  name: "solr",
  startState: function () {
    return {
      tokenize: tokenBase
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return state.tokenize(stream, state);
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTMzNi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvc29sci5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgaXNTdHJpbmdDaGFyID0gL1teXFxzXFx8XFwhXFwrXFwtXFwqXFw/XFx+XFxeXFwmXFw6XFwoXFwpXFxbXFxdXFx7XFx9XFxcIlxcXFxdLztcbnZhciBpc09wZXJhdG9yQ2hhciA9IC9bXFx8XFwhXFwrXFwtXFwqXFw/XFx+XFxeXFwmXS87XG52YXIgaXNPcGVyYXRvclN0cmluZyA9IC9eKE9SfEFORHxOT1R8VE8pJC87XG5mdW5jdGlvbiBpc051bWJlcih3b3JkKSB7XG4gIHJldHVybiBwYXJzZUZsb2F0KHdvcmQpLnRvU3RyaW5nKCkgPT09IHdvcmQ7XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhxdW90ZSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgbmV4dDtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkgYnJlYWs7XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKCFlc2NhcGVkKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfTtcbn1cbmZ1bmN0aW9uIHRva2VuT3BlcmF0b3Iob3BlcmF0b3IpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKG9wZXJhdG9yID09IFwifFwiKSBzdHJlYW0uZWF0KC9cXHwvKTtlbHNlIGlmIChvcGVyYXRvciA9PSBcIiZcIikgc3RyZWFtLmVhdCgvXFwmLyk7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfTtcbn1cbmZ1bmN0aW9uIHRva2VuV29yZChjaCkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgd29yZCA9IGNoO1xuICAgIHdoaWxlICgoY2ggPSBzdHJlYW0ucGVlaygpKSAmJiBjaC5tYXRjaChpc1N0cmluZ0NoYXIpICE9IG51bGwpIHtcbiAgICAgIHdvcmQgKz0gc3RyZWFtLm5leHQoKTtcbiAgICB9XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgaWYgKGlzT3BlcmF0b3JTdHJpbmcudGVzdCh3b3JkKSkgcmV0dXJuIFwib3BlcmF0b3JcIjtlbHNlIGlmIChpc051bWJlcih3b3JkKSkgcmV0dXJuIFwibnVtYmVyXCI7ZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PSBcIjpcIikgcmV0dXJuIFwicHJvcGVydHlOYW1lXCI7ZWxzZSByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfTtcbn1cbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSAnXCInKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtlbHNlIGlmIChpc09wZXJhdG9yQ2hhci50ZXN0KGNoKSkgc3RhdGUudG9rZW5pemUgPSB0b2tlbk9wZXJhdG9yKGNoKTtlbHNlIGlmIChpc1N0cmluZ0NoYXIudGVzdChjaCkpIHN0YXRlLnRva2VuaXplID0gdG9rZW5Xb3JkKGNoKTtcbiAgcmV0dXJuIHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSA/IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpIDogbnVsbDtcbn1cbmV4cG9ydCBjb25zdCBzb2xyID0ge1xuICBuYW1lOiBcInNvbHJcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==