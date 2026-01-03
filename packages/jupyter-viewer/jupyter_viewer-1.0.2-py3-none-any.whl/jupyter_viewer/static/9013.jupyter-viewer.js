"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9013],{

/***/ 99013
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   troff: () => (/* binding */ troff)
/* harmony export */ });
var words = {};
function tokenBase(stream) {
  if (stream.eatSpace()) return null;
  var sol = stream.sol();
  var ch = stream.next();
  if (ch === '\\') {
    if (stream.match('fB') || stream.match('fR') || stream.match('fI') || stream.match('u') || stream.match('d') || stream.match('%') || stream.match('&')) {
      return 'string';
    }
    if (stream.match('m[')) {
      stream.skipTo(']');
      stream.next();
      return 'string';
    }
    if (stream.match('s+') || stream.match('s-')) {
      stream.eatWhile(/[\d-]/);
      return 'string';
    }
    if (stream.match('\(') || stream.match('*\(')) {
      stream.eatWhile(/[\w-]/);
      return 'string';
    }
    return 'string';
  }
  if (sol && (ch === '.' || ch === '\'')) {
    if (stream.eat('\\') && stream.eat('\"')) {
      stream.skipToEnd();
      return 'comment';
    }
  }
  if (sol && ch === '.') {
    if (stream.match('B ') || stream.match('I ') || stream.match('R ')) {
      return 'attribute';
    }
    if (stream.match('TH ') || stream.match('SH ') || stream.match('SS ') || stream.match('HP ')) {
      stream.skipToEnd();
      return 'quote';
    }
    if (stream.match(/[A-Z]/) && stream.match(/[A-Z]/) || stream.match(/[a-z]/) && stream.match(/[a-z]/)) {
      return 'attribute';
    }
  }
  stream.eatWhile(/[\w-]/);
  var cur = stream.current();
  return words.hasOwnProperty(cur) ? words[cur] : null;
}
function tokenize(stream, state) {
  return (state.tokens[0] || tokenBase)(stream, state);
}
;
const troff = {
  name: "troff",
  startState: function () {
    return {
      tokens: []
    };
  },
  token: function (stream, state) {
    return tokenize(stream, state);
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTAxMy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdHJvZmYuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIHdvcmRzID0ge307XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtKSB7XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gIHZhciBzb2wgPSBzdHJlYW0uc29sKCk7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PT0gJ1xcXFwnKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgnZkInKSB8fCBzdHJlYW0ubWF0Y2goJ2ZSJykgfHwgc3RyZWFtLm1hdGNoKCdmSScpIHx8IHN0cmVhbS5tYXRjaCgndScpIHx8IHN0cmVhbS5tYXRjaCgnZCcpIHx8IHN0cmVhbS5tYXRjaCgnJScpIHx8IHN0cmVhbS5tYXRjaCgnJicpKSB7XG4gICAgICByZXR1cm4gJ3N0cmluZyc7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goJ21bJykpIHtcbiAgICAgIHN0cmVhbS5za2lwVG8oJ10nKTtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICByZXR1cm4gJ3N0cmluZyc7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goJ3MrJykgfHwgc3RyZWFtLm1hdGNoKCdzLScpKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXGQtXS8pO1xuICAgICAgcmV0dXJuICdzdHJpbmcnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKCdcXCgnKSB8fCBzdHJlYW0ubWF0Y2goJypcXCgnKSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3LV0vKTtcbiAgICAgIHJldHVybiAnc3RyaW5nJztcbiAgICB9XG4gICAgcmV0dXJuICdzdHJpbmcnO1xuICB9XG4gIGlmIChzb2wgJiYgKGNoID09PSAnLicgfHwgY2ggPT09ICdcXCcnKSkge1xuICAgIGlmIChzdHJlYW0uZWF0KCdcXFxcJykgJiYgc3RyZWFtLmVhdCgnXFxcIicpKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gJ2NvbW1lbnQnO1xuICAgIH1cbiAgfVxuICBpZiAoc29sICYmIGNoID09PSAnLicpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKCdCICcpIHx8IHN0cmVhbS5tYXRjaCgnSSAnKSB8fCBzdHJlYW0ubWF0Y2goJ1IgJykpIHtcbiAgICAgIHJldHVybiAnYXR0cmlidXRlJztcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgnVEggJykgfHwgc3RyZWFtLm1hdGNoKCdTSCAnKSB8fCBzdHJlYW0ubWF0Y2goJ1NTICcpIHx8IHN0cmVhbS5tYXRjaCgnSFAgJykpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiAncXVvdGUnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9bQS1aXS8pICYmIHN0cmVhbS5tYXRjaCgvW0EtWl0vKSB8fCBzdHJlYW0ubWF0Y2goL1thLXpdLykgJiYgc3RyZWFtLm1hdGNoKC9bYS16XS8pKSB7XG4gICAgICByZXR1cm4gJ2F0dHJpYnV0ZSc7XG4gICAgfVxuICB9XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcdy1dLyk7XG4gIHZhciBjdXIgPSBzdHJlYW0uY3VycmVudCgpO1xuICByZXR1cm4gd29yZHMuaGFzT3duUHJvcGVydHkoY3VyKSA/IHdvcmRzW2N1cl0gOiBudWxsO1xufVxuZnVuY3Rpb24gdG9rZW5pemUoc3RyZWFtLCBzdGF0ZSkge1xuICByZXR1cm4gKHN0YXRlLnRva2Vuc1swXSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xufVxuO1xuZXhwb3J0IGNvbnN0IHRyb2ZmID0ge1xuICBuYW1lOiBcInRyb2ZmXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5zOiBbXVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9