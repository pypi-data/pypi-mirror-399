"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3413],{

/***/ 43413
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   cmake: () => (/* binding */ cmake)
/* harmony export */ });
var variable_regex = /({)?[a-zA-Z0-9_]+(})?/;
function tokenString(stream, state) {
  var current,
    prev,
    found_var = false;
  while (!stream.eol() && (current = stream.next()) != state.pending) {
    if (current === '$' && prev != '\\' && state.pending == '"') {
      found_var = true;
      break;
    }
    prev = current;
  }
  if (found_var) {
    stream.backUp(1);
  }
  if (current == state.pending) {
    state.continueString = false;
  } else {
    state.continueString = true;
  }
  return "string";
}
function tokenize(stream, state) {
  var ch = stream.next();

  // Have we found a variable?
  if (ch === '$') {
    if (stream.match(variable_regex)) {
      return 'variableName.special';
    }
    return 'variable';
  }
  // Should we still be looking for the end of a string?
  if (state.continueString) {
    // If so, go through the loop again
    stream.backUp(1);
    return tokenString(stream, state);
  }
  // Do we just have a function on our hands?
  // In 'cmake_minimum_required (VERSION 2.8.8)', 'cmake_minimum_required' is matched
  if (stream.match(/(\s+)?\w+\(/) || stream.match(/(\s+)?\w+\ \(/)) {
    stream.backUp(1);
    return 'def';
  }
  if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  }
  // Have we found a string?
  if (ch == "'" || ch == '"') {
    // Store the type (single or double)
    state.pending = ch;
    // Perform the looping function to find the end
    return tokenString(stream, state);
  }
  if (ch == '(' || ch == ')') {
    return 'bracket';
  }
  if (ch.match(/[0-9]/)) {
    return 'number';
  }
  stream.eatWhile(/[\w-]/);
  return null;
}
const cmake = {
  name: "cmake",
  startState: function () {
    var state = {};
    state.inDefinition = false;
    state.inInclude = false;
    state.continueString = false;
    state.pending = false;
    return state;
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return tokenize(stream, state);
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzQxMy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvY21ha2UuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIHZhcmlhYmxlX3JlZ2V4ID0gLyh7KT9bYS16QS1aMC05X10rKH0pPy87XG5mdW5jdGlvbiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjdXJyZW50LFxuICAgIHByZXYsXG4gICAgZm91bmRfdmFyID0gZmFsc2U7XG4gIHdoaWxlICghc3RyZWFtLmVvbCgpICYmIChjdXJyZW50ID0gc3RyZWFtLm5leHQoKSkgIT0gc3RhdGUucGVuZGluZykge1xuICAgIGlmIChjdXJyZW50ID09PSAnJCcgJiYgcHJldiAhPSAnXFxcXCcgJiYgc3RhdGUucGVuZGluZyA9PSAnXCInKSB7XG4gICAgICBmb3VuZF92YXIgPSB0cnVlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIHByZXYgPSBjdXJyZW50O1xuICB9XG4gIGlmIChmb3VuZF92YXIpIHtcbiAgICBzdHJlYW0uYmFja1VwKDEpO1xuICB9XG4gIGlmIChjdXJyZW50ID09IHN0YXRlLnBlbmRpbmcpIHtcbiAgICBzdGF0ZS5jb250aW51ZVN0cmluZyA9IGZhbHNlO1xuICB9IGVsc2Uge1xuICAgIHN0YXRlLmNvbnRpbnVlU3RyaW5nID0gdHJ1ZTtcbiAgfVxuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cbmZ1bmN0aW9uIHRva2VuaXplKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcblxuICAvLyBIYXZlIHdlIGZvdW5kIGEgdmFyaWFibGU/XG4gIGlmIChjaCA9PT0gJyQnKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCh2YXJpYWJsZV9yZWdleCkpIHtcbiAgICAgIHJldHVybiAndmFyaWFibGVOYW1lLnNwZWNpYWwnO1xuICAgIH1cbiAgICByZXR1cm4gJ3ZhcmlhYmxlJztcbiAgfVxuICAvLyBTaG91bGQgd2Ugc3RpbGwgYmUgbG9va2luZyBmb3IgdGhlIGVuZCBvZiBhIHN0cmluZz9cbiAgaWYgKHN0YXRlLmNvbnRpbnVlU3RyaW5nKSB7XG4gICAgLy8gSWYgc28sIGdvIHRocm91Z2ggdGhlIGxvb3AgYWdhaW5cbiAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgIHJldHVybiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICAvLyBEbyB3ZSBqdXN0IGhhdmUgYSBmdW5jdGlvbiBvbiBvdXIgaGFuZHM/XG4gIC8vIEluICdjbWFrZV9taW5pbXVtX3JlcXVpcmVkIChWRVJTSU9OIDIuOC44KScsICdjbWFrZV9taW5pbXVtX3JlcXVpcmVkJyBpcyBtYXRjaGVkXG4gIGlmIChzdHJlYW0ubWF0Y2goLyhcXHMrKT9cXHcrXFwoLykgfHwgc3RyZWFtLm1hdGNoKC8oXFxzKyk/XFx3K1xcIFxcKC8pKSB7XG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICByZXR1cm4gJ2RlZic7XG4gIH1cbiAgaWYgKGNoID09IFwiI1wiKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuICAvLyBIYXZlIHdlIGZvdW5kIGEgc3RyaW5nP1xuICBpZiAoY2ggPT0gXCInXCIgfHwgY2ggPT0gJ1wiJykge1xuICAgIC8vIFN0b3JlIHRoZSB0eXBlIChzaW5nbGUgb3IgZG91YmxlKVxuICAgIHN0YXRlLnBlbmRpbmcgPSBjaDtcbiAgICAvLyBQZXJmb3JtIHRoZSBsb29waW5nIGZ1bmN0aW9uIHRvIGZpbmQgdGhlIGVuZFxuICAgIHJldHVybiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoY2ggPT0gJygnIHx8IGNoID09ICcpJykge1xuICAgIHJldHVybiAnYnJhY2tldCc7XG4gIH1cbiAgaWYgKGNoLm1hdGNoKC9bMC05XS8pKSB7XG4gICAgcmV0dXJuICdudW1iZXInO1xuICB9XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcdy1dLyk7XG4gIHJldHVybiBudWxsO1xufVxuZXhwb3J0IGNvbnN0IGNtYWtlID0ge1xuICBuYW1lOiBcImNtYWtlXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgc3RhdGUgPSB7fTtcbiAgICBzdGF0ZS5pbkRlZmluaXRpb24gPSBmYWxzZTtcbiAgICBzdGF0ZS5pbkluY2x1ZGUgPSBmYWxzZTtcbiAgICBzdGF0ZS5jb250aW51ZVN0cmluZyA9IGZhbHNlO1xuICAgIHN0YXRlLnBlbmRpbmcgPSBmYWxzZTtcbiAgICByZXR1cm4gc3RhdGU7XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgcmV0dXJuIHRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=