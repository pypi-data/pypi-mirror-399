"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2284],{

/***/ 72284
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   octave: () => (/* binding */ octave)
/* harmony export */ });
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b");
}
var singleOperators = new RegExp("^[\\+\\-\\*/&|\\^~<>!@'\\\\]");
var singleDelimiters = new RegExp('^[\\(\\[\\{\\},:=;\\.]');
var doubleOperators = new RegExp("^((==)|(~=)|(<=)|(>=)|(<<)|(>>)|(\\.[\\+\\-\\*/\\^\\\\]))");
var doubleDelimiters = new RegExp("^((!=)|(\\+=)|(\\-=)|(\\*=)|(/=)|(&=)|(\\|=)|(\\^=))");
var tripleDelimiters = new RegExp("^((>>=)|(<<=))");
var expressionEnd = new RegExp("^[\\]\\)]");
var identifiers = new RegExp("^[_A-Za-z\xa1-\uffff][_A-Za-z0-9\xa1-\uffff]*");
var builtins = wordRegexp(['error', 'eval', 'function', 'abs', 'acos', 'atan', 'asin', 'cos', 'cosh', 'exp', 'log', 'prod', 'sum', 'log10', 'max', 'min', 'sign', 'sin', 'sinh', 'sqrt', 'tan', 'reshape', 'break', 'zeros', 'default', 'margin', 'round', 'ones', 'rand', 'syn', 'ceil', 'floor', 'size', 'clear', 'zeros', 'eye', 'mean', 'std', 'cov', 'det', 'eig', 'inv', 'norm', 'rank', 'trace', 'expm', 'logm', 'sqrtm', 'linspace', 'plot', 'title', 'xlabel', 'ylabel', 'legend', 'text', 'grid', 'meshgrid', 'mesh', 'num2str', 'fft', 'ifft', 'arrayfun', 'cellfun', 'input', 'fliplr', 'flipud', 'ismember']);
var keywords = wordRegexp(['return', 'case', 'switch', 'else', 'elseif', 'end', 'endif', 'endfunction', 'if', 'otherwise', 'do', 'for', 'while', 'try', 'catch', 'classdef', 'properties', 'events', 'methods', 'global', 'persistent', 'endfor', 'endwhile', 'printf', 'sprintf', 'disp', 'until', 'continue', 'pkg']);

// tokenizers
function tokenTranspose(stream, state) {
  if (!stream.sol() && stream.peek() === '\'') {
    stream.next();
    state.tokenize = tokenBase;
    return 'operator';
  }
  state.tokenize = tokenBase;
  return tokenBase(stream, state);
}
function tokenComment(stream, state) {
  if (stream.match(/^.*%}/)) {
    state.tokenize = tokenBase;
    return 'comment';
  }
  ;
  stream.skipToEnd();
  return 'comment';
}
function tokenBase(stream, state) {
  // whitespaces
  if (stream.eatSpace()) return null;

  // Handle one line Comments
  if (stream.match('%{')) {
    state.tokenize = tokenComment;
    stream.skipToEnd();
    return 'comment';
  }
  if (stream.match(/^[%#]/)) {
    stream.skipToEnd();
    return 'comment';
  }

  // Handle Number Literals
  if (stream.match(/^[0-9\.+-]/, false)) {
    if (stream.match(/^[+-]?0x[0-9a-fA-F]+[ij]?/)) {
      stream.tokenize = tokenBase;
      return 'number';
    }
    ;
    if (stream.match(/^[+-]?\d*\.\d+([EeDd][+-]?\d+)?[ij]?/)) {
      return 'number';
    }
    ;
    if (stream.match(/^[+-]?\d+([EeDd][+-]?\d+)?[ij]?/)) {
      return 'number';
    }
    ;
  }
  if (stream.match(wordRegexp(['nan', 'NaN', 'inf', 'Inf']))) {
    return 'number';
  }
  ;

  // Handle Strings
  var m = stream.match(/^"(?:[^"]|"")*("|$)/) || stream.match(/^'(?:[^']|'')*('|$)/);
  if (m) {
    return m[1] ? 'string' : "error";
  }

  // Handle words
  if (stream.match(keywords)) {
    return 'keyword';
  }
  ;
  if (stream.match(builtins)) {
    return 'builtin';
  }
  ;
  if (stream.match(identifiers)) {
    return 'variable';
  }
  ;
  if (stream.match(singleOperators) || stream.match(doubleOperators)) {
    return 'operator';
  }
  ;
  if (stream.match(singleDelimiters) || stream.match(doubleDelimiters) || stream.match(tripleDelimiters)) {
    return null;
  }
  ;
  if (stream.match(expressionEnd)) {
    state.tokenize = tokenTranspose;
    return null;
  }
  ;

  // Handle non-detected items
  stream.next();
  return 'error';
}
;
const octave = {
  name: "octave",
  startState: function () {
    return {
      tokenize: tokenBase
    };
  },
  token: function (stream, state) {
    var style = state.tokenize(stream, state);
    if (style === 'number' || style === 'variable') {
      state.tokenize = tokenTranspose;
    }
    return style;
  },
  languageData: {
    commentTokens: {
      line: "%"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjI4NC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL29jdGF2ZS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIpO1xufVxudmFyIHNpbmdsZU9wZXJhdG9ycyA9IG5ldyBSZWdFeHAoXCJeW1xcXFwrXFxcXC1cXFxcKi8mfFxcXFxefjw+IUAnXFxcXFxcXFxdXCIpO1xudmFyIHNpbmdsZURlbGltaXRlcnMgPSBuZXcgUmVnRXhwKCdeW1xcXFwoXFxcXFtcXFxce1xcXFx9LDo9O1xcXFwuXScpO1xudmFyIGRvdWJsZU9wZXJhdG9ycyA9IG5ldyBSZWdFeHAoXCJeKCg9PSl8KH49KXwoPD0pfCg+PSl8KDw8KXwoPj4pfChcXFxcLltcXFxcK1xcXFwtXFxcXCovXFxcXF5cXFxcXFxcXF0pKVwiKTtcbnZhciBkb3VibGVEZWxpbWl0ZXJzID0gbmV3IFJlZ0V4cChcIl4oKCE9KXwoXFxcXCs9KXwoXFxcXC09KXwoXFxcXCo9KXwoLz0pfCgmPSl8KFxcXFx8PSl8KFxcXFxePSkpXCIpO1xudmFyIHRyaXBsZURlbGltaXRlcnMgPSBuZXcgUmVnRXhwKFwiXigoPj49KXwoPDw9KSlcIik7XG52YXIgZXhwcmVzc2lvbkVuZCA9IG5ldyBSZWdFeHAoXCJeW1xcXFxdXFxcXCldXCIpO1xudmFyIGlkZW50aWZpZXJzID0gbmV3IFJlZ0V4cChcIl5bX0EtWmEtelxceGExLVxcdWZmZmZdW19BLVphLXowLTlcXHhhMS1cXHVmZmZmXSpcIik7XG52YXIgYnVpbHRpbnMgPSB3b3JkUmVnZXhwKFsnZXJyb3InLCAnZXZhbCcsICdmdW5jdGlvbicsICdhYnMnLCAnYWNvcycsICdhdGFuJywgJ2FzaW4nLCAnY29zJywgJ2Nvc2gnLCAnZXhwJywgJ2xvZycsICdwcm9kJywgJ3N1bScsICdsb2cxMCcsICdtYXgnLCAnbWluJywgJ3NpZ24nLCAnc2luJywgJ3NpbmgnLCAnc3FydCcsICd0YW4nLCAncmVzaGFwZScsICdicmVhaycsICd6ZXJvcycsICdkZWZhdWx0JywgJ21hcmdpbicsICdyb3VuZCcsICdvbmVzJywgJ3JhbmQnLCAnc3luJywgJ2NlaWwnLCAnZmxvb3InLCAnc2l6ZScsICdjbGVhcicsICd6ZXJvcycsICdleWUnLCAnbWVhbicsICdzdGQnLCAnY292JywgJ2RldCcsICdlaWcnLCAnaW52JywgJ25vcm0nLCAncmFuaycsICd0cmFjZScsICdleHBtJywgJ2xvZ20nLCAnc3FydG0nLCAnbGluc3BhY2UnLCAncGxvdCcsICd0aXRsZScsICd4bGFiZWwnLCAneWxhYmVsJywgJ2xlZ2VuZCcsICd0ZXh0JywgJ2dyaWQnLCAnbWVzaGdyaWQnLCAnbWVzaCcsICdudW0yc3RyJywgJ2ZmdCcsICdpZmZ0JywgJ2FycmF5ZnVuJywgJ2NlbGxmdW4nLCAnaW5wdXQnLCAnZmxpcGxyJywgJ2ZsaXB1ZCcsICdpc21lbWJlciddKTtcbnZhciBrZXl3b3JkcyA9IHdvcmRSZWdleHAoWydyZXR1cm4nLCAnY2FzZScsICdzd2l0Y2gnLCAnZWxzZScsICdlbHNlaWYnLCAnZW5kJywgJ2VuZGlmJywgJ2VuZGZ1bmN0aW9uJywgJ2lmJywgJ290aGVyd2lzZScsICdkbycsICdmb3InLCAnd2hpbGUnLCAndHJ5JywgJ2NhdGNoJywgJ2NsYXNzZGVmJywgJ3Byb3BlcnRpZXMnLCAnZXZlbnRzJywgJ21ldGhvZHMnLCAnZ2xvYmFsJywgJ3BlcnNpc3RlbnQnLCAnZW5kZm9yJywgJ2VuZHdoaWxlJywgJ3ByaW50ZicsICdzcHJpbnRmJywgJ2Rpc3AnLCAndW50aWwnLCAnY29udGludWUnLCAncGtnJ10pO1xuXG4vLyB0b2tlbml6ZXJzXG5mdW5jdGlvbiB0b2tlblRyYW5zcG9zZShzdHJlYW0sIHN0YXRlKSB7XG4gIGlmICghc3RyZWFtLnNvbCgpICYmIHN0cmVhbS5wZWVrKCkgPT09ICdcXCcnKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICByZXR1cm4gJ29wZXJhdG9yJztcbiAgfVxuICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgcmV0dXJuIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKTtcbn1cbmZ1bmN0aW9uIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL14uKiV9LykpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICByZXR1cm4gJ2NvbW1lbnQnO1xuICB9XG4gIDtcbiAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICByZXR1cm4gJ2NvbW1lbnQnO1xufVxuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgLy8gd2hpdGVzcGFjZXNcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcblxuICAvLyBIYW5kbGUgb25lIGxpbmUgQ29tbWVudHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgnJXsnKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Db21tZW50O1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gJ2NvbW1lbnQnO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goL15bJSNdLykpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuICdjb21tZW50JztcbiAgfVxuXG4gIC8vIEhhbmRsZSBOdW1iZXIgTGl0ZXJhbHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXlswLTlcXC4rLV0vLCBmYWxzZSkpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eWystXT8weFswLTlhLWZBLUZdK1tpal0/LykpIHtcbiAgICAgIHN0cmVhbS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIHJldHVybiAnbnVtYmVyJztcbiAgICB9XG4gICAgO1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL15bKy1dP1xcZCpcXC5cXGQrKFtFZURkXVsrLV0/XFxkKyk/W2lqXT8vKSkge1xuICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgIH1cbiAgICA7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXlsrLV0/XFxkKyhbRWVEZF1bKy1dP1xcZCspP1tpal0/LykpIHtcbiAgICAgIHJldHVybiAnbnVtYmVyJztcbiAgICB9XG4gICAgO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2god29yZFJlZ2V4cChbJ25hbicsICdOYU4nLCAnaW5mJywgJ0luZiddKSkpIHtcbiAgICByZXR1cm4gJ251bWJlcic7XG4gIH1cbiAgO1xuXG4gIC8vIEhhbmRsZSBTdHJpbmdzXG4gIHZhciBtID0gc3RyZWFtLm1hdGNoKC9eXCIoPzpbXlwiXXxcIlwiKSooXCJ8JCkvKSB8fCBzdHJlYW0ubWF0Y2goL14nKD86W14nXXwnJykqKCd8JCkvKTtcbiAgaWYgKG0pIHtcbiAgICByZXR1cm4gbVsxXSA/ICdzdHJpbmcnIDogXCJlcnJvclwiO1xuICB9XG5cbiAgLy8gSGFuZGxlIHdvcmRzXG4gIGlmIChzdHJlYW0ubWF0Y2goa2V5d29yZHMpKSB7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuICA7XG4gIGlmIChzdHJlYW0ubWF0Y2goYnVpbHRpbnMpKSB7XG4gICAgcmV0dXJuICdidWlsdGluJztcbiAgfVxuICA7XG4gIGlmIChzdHJlYW0ubWF0Y2goaWRlbnRpZmllcnMpKSB7XG4gICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gIH1cbiAgO1xuICBpZiAoc3RyZWFtLm1hdGNoKHNpbmdsZU9wZXJhdG9ycykgfHwgc3RyZWFtLm1hdGNoKGRvdWJsZU9wZXJhdG9ycykpIHtcbiAgICByZXR1cm4gJ29wZXJhdG9yJztcbiAgfVxuICA7XG4gIGlmIChzdHJlYW0ubWF0Y2goc2luZ2xlRGVsaW1pdGVycykgfHwgc3RyZWFtLm1hdGNoKGRvdWJsZURlbGltaXRlcnMpIHx8IHN0cmVhbS5tYXRjaCh0cmlwbGVEZWxpbWl0ZXJzKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIDtcbiAgaWYgKHN0cmVhbS5tYXRjaChleHByZXNzaW9uRW5kKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5UcmFuc3Bvc2U7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgO1xuXG4gIC8vIEhhbmRsZSBub24tZGV0ZWN0ZWQgaXRlbXNcbiAgc3RyZWFtLm5leHQoKTtcbiAgcmV0dXJuICdlcnJvcic7XG59XG47XG5leHBvcnQgY29uc3Qgb2N0YXZlID0ge1xuICBuYW1lOiBcIm9jdGF2ZVwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3R5bGUgPT09ICdudW1iZXInIHx8IHN0eWxlID09PSAndmFyaWFibGUnKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuVHJhbnNwb3NlO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiJVwiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=