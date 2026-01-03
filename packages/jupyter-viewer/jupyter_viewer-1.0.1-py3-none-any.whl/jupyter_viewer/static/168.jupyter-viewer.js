"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[168],{

/***/ 80168
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   http: () => (/* binding */ http)
/* harmony export */ });
function failFirstLine(stream, state) {
  stream.skipToEnd();
  state.cur = header;
  return "error";
}
function start(stream, state) {
  if (stream.match(/^HTTP\/\d\.\d/)) {
    state.cur = responseStatusCode;
    return "keyword";
  } else if (stream.match(/^[A-Z]+/) && /[ \t]/.test(stream.peek())) {
    state.cur = requestPath;
    return "keyword";
  } else {
    return failFirstLine(stream, state);
  }
}
function responseStatusCode(stream, state) {
  var code = stream.match(/^\d+/);
  if (!code) return failFirstLine(stream, state);
  state.cur = responseStatusText;
  var status = Number(code[0]);
  if (status >= 100 && status < 400) {
    return "atom";
  } else {
    return "error";
  }
}
function responseStatusText(stream, state) {
  stream.skipToEnd();
  state.cur = header;
  return null;
}
function requestPath(stream, state) {
  stream.eatWhile(/\S/);
  state.cur = requestProtocol;
  return "string.special";
}
function requestProtocol(stream, state) {
  if (stream.match(/^HTTP\/\d\.\d$/)) {
    state.cur = header;
    return "keyword";
  } else {
    return failFirstLine(stream, state);
  }
}
function header(stream) {
  if (stream.sol() && !stream.eat(/[ \t]/)) {
    if (stream.match(/^.*?:/)) {
      return "atom";
    } else {
      stream.skipToEnd();
      return "error";
    }
  } else {
    stream.skipToEnd();
    return "string";
  }
}
function body(stream) {
  stream.skipToEnd();
  return null;
}
const http = {
  name: "http",
  token: function (stream, state) {
    var cur = state.cur;
    if (cur != header && cur != body && stream.eatSpace()) return null;
    return cur(stream, state);
  },
  blankLine: function (state) {
    state.cur = body;
  },
  startState: function () {
    return {
      cur: start
    };
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTY4Lmp1cHl0ZXItdmlld2VyLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvaHR0cC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBmYWlsRmlyc3RMaW5lKHN0cmVhbSwgc3RhdGUpIHtcbiAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICBzdGF0ZS5jdXIgPSBoZWFkZXI7XG4gIHJldHVybiBcImVycm9yXCI7XG59XG5mdW5jdGlvbiBzdGFydChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL15IVFRQXFwvXFxkXFwuXFxkLykpIHtcbiAgICBzdGF0ZS5jdXIgPSByZXNwb25zZVN0YXR1c0NvZGU7XG4gICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXltBLVpdKy8pICYmIC9bIFxcdF0vLnRlc3Qoc3RyZWFtLnBlZWsoKSkpIHtcbiAgICBzdGF0ZS5jdXIgPSByZXF1ZXN0UGF0aDtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH0gZWxzZSB7XG4gICAgcmV0dXJuIGZhaWxGaXJzdExpbmUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbn1cbmZ1bmN0aW9uIHJlc3BvbnNlU3RhdHVzQ29kZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjb2RlID0gc3RyZWFtLm1hdGNoKC9eXFxkKy8pO1xuICBpZiAoIWNvZGUpIHJldHVybiBmYWlsRmlyc3RMaW5lKHN0cmVhbSwgc3RhdGUpO1xuICBzdGF0ZS5jdXIgPSByZXNwb25zZVN0YXR1c1RleHQ7XG4gIHZhciBzdGF0dXMgPSBOdW1iZXIoY29kZVswXSk7XG4gIGlmIChzdGF0dXMgPj0gMTAwICYmIHN0YXR1cyA8IDQwMCkge1xuICAgIHJldHVybiBcImF0b21cIjtcbiAgfSBlbHNlIHtcbiAgICByZXR1cm4gXCJlcnJvclwiO1xuICB9XG59XG5mdW5jdGlvbiByZXNwb25zZVN0YXR1c1RleHQoc3RyZWFtLCBzdGF0ZSkge1xuICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIHN0YXRlLmN1ciA9IGhlYWRlcjtcbiAgcmV0dXJuIG51bGw7XG59XG5mdW5jdGlvbiByZXF1ZXN0UGF0aChzdHJlYW0sIHN0YXRlKSB7XG4gIHN0cmVhbS5lYXRXaGlsZSgvXFxTLyk7XG4gIHN0YXRlLmN1ciA9IHJlcXVlc3RQcm90b2NvbDtcbiAgcmV0dXJuIFwic3RyaW5nLnNwZWNpYWxcIjtcbn1cbmZ1bmN0aW9uIHJlcXVlc3RQcm90b2NvbChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL15IVFRQXFwvXFxkXFwuXFxkJC8pKSB7XG4gICAgc3RhdGUuY3VyID0gaGVhZGVyO1xuICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgfSBlbHNlIHtcbiAgICByZXR1cm4gZmFpbEZpcnN0TGluZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxufVxuZnVuY3Rpb24gaGVhZGVyKHN0cmVhbSkge1xuICBpZiAoc3RyZWFtLnNvbCgpICYmICFzdHJlYW0uZWF0KC9bIFxcdF0vKSkge1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL14uKj86LykpIHtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuIFwiZXJyb3JcIjtcbiAgICB9XG4gIH0gZWxzZSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9XG59XG5mdW5jdGlvbiBib2R5KHN0cmVhbSkge1xuICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIHJldHVybiBudWxsO1xufVxuZXhwb3J0IGNvbnN0IGh0dHAgPSB7XG4gIG5hbWU6IFwiaHR0cFwiLFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY3VyID0gc3RhdGUuY3VyO1xuICAgIGlmIChjdXIgIT0gaGVhZGVyICYmIGN1ciAhPSBib2R5ICYmIHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICByZXR1cm4gY3VyKHN0cmVhbSwgc3RhdGUpO1xuICB9LFxuICBibGFua0xpbmU6IGZ1bmN0aW9uIChzdGF0ZSkge1xuICAgIHN0YXRlLmN1ciA9IGJvZHk7XG4gIH0sXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgY3VyOiBzdGFydFxuICAgIH07XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==