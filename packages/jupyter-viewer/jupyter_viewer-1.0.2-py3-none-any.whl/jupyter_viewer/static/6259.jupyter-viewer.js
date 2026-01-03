"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6259],{

/***/ 36259
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   smalltalk: () => (/* binding */ smalltalk)
/* harmony export */ });
var specialChars = /[+\-\/\\*~<>=@%|&?!.,:;^]/;
var keywords = /true|false|nil|self|super|thisContext/;
var Context = function (tokenizer, parent) {
  this.next = tokenizer;
  this.parent = parent;
};
var Token = function (name, context, eos) {
  this.name = name;
  this.context = context;
  this.eos = eos;
};
var State = function () {
  this.context = new Context(next, null);
  this.expectVariable = true;
  this.indentation = 0;
  this.userIndentationDelta = 0;
};
State.prototype.userIndent = function (indentation, indentUnit) {
  this.userIndentationDelta = indentation > 0 ? indentation / indentUnit - this.indentation : 0;
};
var next = function (stream, context, state) {
  var token = new Token(null, context, false);
  var aChar = stream.next();
  if (aChar === '"') {
    token = nextComment(stream, new Context(nextComment, context));
  } else if (aChar === '\'') {
    token = nextString(stream, new Context(nextString, context));
  } else if (aChar === '#') {
    if (stream.peek() === '\'') {
      stream.next();
      token = nextSymbol(stream, new Context(nextSymbol, context));
    } else {
      if (stream.eatWhile(/[^\s.{}\[\]()]/)) token.name = 'string.special';else token.name = 'meta';
    }
  } else if (aChar === '$') {
    if (stream.next() === '<') {
      stream.eatWhile(/[^\s>]/);
      stream.next();
    }
    token.name = 'string.special';
  } else if (aChar === '|' && state.expectVariable) {
    token.context = new Context(nextTemporaries, context);
  } else if (/[\[\]{}()]/.test(aChar)) {
    token.name = 'bracket';
    token.eos = /[\[{(]/.test(aChar);
    if (aChar === '[') {
      state.indentation++;
    } else if (aChar === ']') {
      state.indentation = Math.max(0, state.indentation - 1);
    }
  } else if (specialChars.test(aChar)) {
    stream.eatWhile(specialChars);
    token.name = 'operator';
    token.eos = aChar !== ';'; // ; cascaded message expression
  } else if (/\d/.test(aChar)) {
    stream.eatWhile(/[\w\d]/);
    token.name = 'number';
  } else if (/[\w_]/.test(aChar)) {
    stream.eatWhile(/[\w\d_]/);
    token.name = state.expectVariable ? keywords.test(stream.current()) ? 'keyword' : 'variable' : null;
  } else {
    token.eos = state.expectVariable;
  }
  return token;
};
var nextComment = function (stream, context) {
  stream.eatWhile(/[^"]/);
  return new Token('comment', stream.eat('"') ? context.parent : context, true);
};
var nextString = function (stream, context) {
  stream.eatWhile(/[^']/);
  return new Token('string', stream.eat('\'') ? context.parent : context, false);
};
var nextSymbol = function (stream, context) {
  stream.eatWhile(/[^']/);
  return new Token('string.special', stream.eat('\'') ? context.parent : context, false);
};
var nextTemporaries = function (stream, context) {
  var token = new Token(null, context, false);
  var aChar = stream.next();
  if (aChar === '|') {
    token.context = context.parent;
    token.eos = true;
  } else {
    stream.eatWhile(/[^|]/);
    token.name = 'variable';
  }
  return token;
};
const smalltalk = {
  name: "smalltalk",
  startState: function () {
    return new State();
  },
  token: function (stream, state) {
    state.userIndent(stream.indentation(), stream.indentUnit);
    if (stream.eatSpace()) {
      return null;
    }
    var token = state.context.next(stream, state.context, state);
    state.context = token.context;
    state.expectVariable = token.eos;
    return token.name;
  },
  blankLine: function (state, indentUnit) {
    state.userIndent(0, indentUnit);
  },
  indent: function (state, textAfter, cx) {
    var i = state.context.next === next && textAfter && textAfter.charAt(0) === ']' ? -1 : state.userIndentationDelta;
    return (state.indentation + i) * cx.unit;
  },
  languageData: {
    indentOnInput: /^\s*\]$/
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjI1OS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvc21hbGx0YWxrLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBzcGVjaWFsQ2hhcnMgPSAvWytcXC1cXC9cXFxcKn48Pj1AJXwmPyEuLDo7Xl0vO1xudmFyIGtleXdvcmRzID0gL3RydWV8ZmFsc2V8bmlsfHNlbGZ8c3VwZXJ8dGhpc0NvbnRleHQvO1xudmFyIENvbnRleHQgPSBmdW5jdGlvbiAodG9rZW5pemVyLCBwYXJlbnQpIHtcbiAgdGhpcy5uZXh0ID0gdG9rZW5pemVyO1xuICB0aGlzLnBhcmVudCA9IHBhcmVudDtcbn07XG52YXIgVG9rZW4gPSBmdW5jdGlvbiAobmFtZSwgY29udGV4dCwgZW9zKSB7XG4gIHRoaXMubmFtZSA9IG5hbWU7XG4gIHRoaXMuY29udGV4dCA9IGNvbnRleHQ7XG4gIHRoaXMuZW9zID0gZW9zO1xufTtcbnZhciBTdGF0ZSA9IGZ1bmN0aW9uICgpIHtcbiAgdGhpcy5jb250ZXh0ID0gbmV3IENvbnRleHQobmV4dCwgbnVsbCk7XG4gIHRoaXMuZXhwZWN0VmFyaWFibGUgPSB0cnVlO1xuICB0aGlzLmluZGVudGF0aW9uID0gMDtcbiAgdGhpcy51c2VySW5kZW50YXRpb25EZWx0YSA9IDA7XG59O1xuU3RhdGUucHJvdG90eXBlLnVzZXJJbmRlbnQgPSBmdW5jdGlvbiAoaW5kZW50YXRpb24sIGluZGVudFVuaXQpIHtcbiAgdGhpcy51c2VySW5kZW50YXRpb25EZWx0YSA9IGluZGVudGF0aW9uID4gMCA/IGluZGVudGF0aW9uIC8gaW5kZW50VW5pdCAtIHRoaXMuaW5kZW50YXRpb24gOiAwO1xufTtcbnZhciBuZXh0ID0gZnVuY3Rpb24gKHN0cmVhbSwgY29udGV4dCwgc3RhdGUpIHtcbiAgdmFyIHRva2VuID0gbmV3IFRva2VuKG51bGwsIGNvbnRleHQsIGZhbHNlKTtcbiAgdmFyIGFDaGFyID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGFDaGFyID09PSAnXCInKSB7XG4gICAgdG9rZW4gPSBuZXh0Q29tbWVudChzdHJlYW0sIG5ldyBDb250ZXh0KG5leHRDb21tZW50LCBjb250ZXh0KSk7XG4gIH0gZWxzZSBpZiAoYUNoYXIgPT09ICdcXCcnKSB7XG4gICAgdG9rZW4gPSBuZXh0U3RyaW5nKHN0cmVhbSwgbmV3IENvbnRleHQobmV4dFN0cmluZywgY29udGV4dCkpO1xuICB9IGVsc2UgaWYgKGFDaGFyID09PSAnIycpIHtcbiAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gJ1xcJycpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICB0b2tlbiA9IG5leHRTeW1ib2woc3RyZWFtLCBuZXcgQ29udGV4dChuZXh0U3ltYm9sLCBjb250ZXh0KSk7XG4gICAgfSBlbHNlIHtcbiAgICAgIGlmIChzdHJlYW0uZWF0V2hpbGUoL1teXFxzLnt9XFxbXFxdKCldLykpIHRva2VuLm5hbWUgPSAnc3RyaW5nLnNwZWNpYWwnO2Vsc2UgdG9rZW4ubmFtZSA9ICdtZXRhJztcbiAgICB9XG4gIH0gZWxzZSBpZiAoYUNoYXIgPT09ICckJykge1xuICAgIGlmIChzdHJlYW0ubmV4dCgpID09PSAnPCcpIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW15cXHM+XS8pO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICB9XG4gICAgdG9rZW4ubmFtZSA9ICdzdHJpbmcuc3BlY2lhbCc7XG4gIH0gZWxzZSBpZiAoYUNoYXIgPT09ICd8JyAmJiBzdGF0ZS5leHBlY3RWYXJpYWJsZSkge1xuICAgIHRva2VuLmNvbnRleHQgPSBuZXcgQ29udGV4dChuZXh0VGVtcG9yYXJpZXMsIGNvbnRleHQpO1xuICB9IGVsc2UgaWYgKC9bXFxbXFxde30oKV0vLnRlc3QoYUNoYXIpKSB7XG4gICAgdG9rZW4ubmFtZSA9ICdicmFja2V0JztcbiAgICB0b2tlbi5lb3MgPSAvW1xcW3soXS8udGVzdChhQ2hhcik7XG4gICAgaWYgKGFDaGFyID09PSAnWycpIHtcbiAgICAgIHN0YXRlLmluZGVudGF0aW9uKys7XG4gICAgfSBlbHNlIGlmIChhQ2hhciA9PT0gJ10nKSB7XG4gICAgICBzdGF0ZS5pbmRlbnRhdGlvbiA9IE1hdGgubWF4KDAsIHN0YXRlLmluZGVudGF0aW9uIC0gMSk7XG4gICAgfVxuICB9IGVsc2UgaWYgKHNwZWNpYWxDaGFycy50ZXN0KGFDaGFyKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShzcGVjaWFsQ2hhcnMpO1xuICAgIHRva2VuLm5hbWUgPSAnb3BlcmF0b3InO1xuICAgIHRva2VuLmVvcyA9IGFDaGFyICE9PSAnOyc7IC8vIDsgY2FzY2FkZWQgbWVzc2FnZSBleHByZXNzaW9uXG4gIH0gZWxzZSBpZiAoL1xcZC8udGVzdChhQ2hhcikpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXGRdLyk7XG4gICAgdG9rZW4ubmFtZSA9ICdudW1iZXInO1xuICB9IGVsc2UgaWYgKC9bXFx3X10vLnRlc3QoYUNoYXIpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFxkX10vKTtcbiAgICB0b2tlbi5uYW1lID0gc3RhdGUuZXhwZWN0VmFyaWFibGUgPyBrZXl3b3Jkcy50ZXN0KHN0cmVhbS5jdXJyZW50KCkpID8gJ2tleXdvcmQnIDogJ3ZhcmlhYmxlJyA6IG51bGw7XG4gIH0gZWxzZSB7XG4gICAgdG9rZW4uZW9zID0gc3RhdGUuZXhwZWN0VmFyaWFibGU7XG4gIH1cbiAgcmV0dXJuIHRva2VuO1xufTtcbnZhciBuZXh0Q29tbWVudCA9IGZ1bmN0aW9uIChzdHJlYW0sIGNvbnRleHQpIHtcbiAgc3RyZWFtLmVhdFdoaWxlKC9bXlwiXS8pO1xuICByZXR1cm4gbmV3IFRva2VuKCdjb21tZW50Jywgc3RyZWFtLmVhdCgnXCInKSA/IGNvbnRleHQucGFyZW50IDogY29udGV4dCwgdHJ1ZSk7XG59O1xudmFyIG5leHRTdHJpbmcgPSBmdW5jdGlvbiAoc3RyZWFtLCBjb250ZXh0KSB7XG4gIHN0cmVhbS5lYXRXaGlsZSgvW14nXS8pO1xuICByZXR1cm4gbmV3IFRva2VuKCdzdHJpbmcnLCBzdHJlYW0uZWF0KCdcXCcnKSA/IGNvbnRleHQucGFyZW50IDogY29udGV4dCwgZmFsc2UpO1xufTtcbnZhciBuZXh0U3ltYm9sID0gZnVuY3Rpb24gKHN0cmVhbSwgY29udGV4dCkge1xuICBzdHJlYW0uZWF0V2hpbGUoL1teJ10vKTtcbiAgcmV0dXJuIG5ldyBUb2tlbignc3RyaW5nLnNwZWNpYWwnLCBzdHJlYW0uZWF0KCdcXCcnKSA/IGNvbnRleHQucGFyZW50IDogY29udGV4dCwgZmFsc2UpO1xufTtcbnZhciBuZXh0VGVtcG9yYXJpZXMgPSBmdW5jdGlvbiAoc3RyZWFtLCBjb250ZXh0KSB7XG4gIHZhciB0b2tlbiA9IG5ldyBUb2tlbihudWxsLCBjb250ZXh0LCBmYWxzZSk7XG4gIHZhciBhQ2hhciA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChhQ2hhciA9PT0gJ3wnKSB7XG4gICAgdG9rZW4uY29udGV4dCA9IGNvbnRleHQucGFyZW50O1xuICAgIHRva2VuLmVvcyA9IHRydWU7XG4gIH0gZWxzZSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXnxdLyk7XG4gICAgdG9rZW4ubmFtZSA9ICd2YXJpYWJsZSc7XG4gIH1cbiAgcmV0dXJuIHRva2VuO1xufTtcbmV4cG9ydCBjb25zdCBzbWFsbHRhbGsgPSB7XG4gIG5hbWU6IFwic21hbGx0YWxrXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4gbmV3IFN0YXRlKCk7XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHN0YXRlLnVzZXJJbmRlbnQoc3RyZWFtLmluZGVudGF0aW9uKCksIHN0cmVhbS5pbmRlbnRVbml0KTtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICB2YXIgdG9rZW4gPSBzdGF0ZS5jb250ZXh0Lm5leHQoc3RyZWFtLCBzdGF0ZS5jb250ZXh0LCBzdGF0ZSk7XG4gICAgc3RhdGUuY29udGV4dCA9IHRva2VuLmNvbnRleHQ7XG4gICAgc3RhdGUuZXhwZWN0VmFyaWFibGUgPSB0b2tlbi5lb3M7XG4gICAgcmV0dXJuIHRva2VuLm5hbWU7XG4gIH0sXG4gIGJsYW5rTGluZTogZnVuY3Rpb24gKHN0YXRlLCBpbmRlbnRVbml0KSB7XG4gICAgc3RhdGUudXNlckluZGVudCgwLCBpbmRlbnRVbml0KTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICB2YXIgaSA9IHN0YXRlLmNvbnRleHQubmV4dCA9PT0gbmV4dCAmJiB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKSA9PT0gJ10nID8gLTEgOiBzdGF0ZS51c2VySW5kZW50YXRpb25EZWx0YTtcbiAgICByZXR1cm4gKHN0YXRlLmluZGVudGF0aW9uICsgaSkgKiBjeC51bml0O1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypcXF0kL1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=