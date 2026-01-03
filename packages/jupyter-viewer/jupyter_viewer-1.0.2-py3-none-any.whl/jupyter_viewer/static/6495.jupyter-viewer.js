"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6495],{

/***/ 96495
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   fcl: () => (/* binding */ fcl)
/* harmony export */ });
var keywords = {
  "term": true,
  "method": true,
  "accu": true,
  "rule": true,
  "then": true,
  "is": true,
  "and": true,
  "or": true,
  "if": true,
  "default": true
};
var start_blocks = {
  "var_input": true,
  "var_output": true,
  "fuzzify": true,
  "defuzzify": true,
  "function_block": true,
  "ruleblock": true
};
var end_blocks = {
  "end_ruleblock": true,
  "end_defuzzify": true,
  "end_function_block": true,
  "end_fuzzify": true,
  "end_var": true
};
var atoms = {
  "true": true,
  "false": true,
  "nan": true,
  "real": true,
  "min": true,
  "max": true,
  "cog": true,
  "cogs": true
};
var isOperatorChar = /[+\-*&^%:=<>!|\/]/;
function tokenBase(stream, state) {
  var ch = stream.next();
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
  if (ch == "/" || ch == "(") {
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
  var cur = stream.current().toLowerCase();
  if (keywords.propertyIsEnumerable(cur) || start_blocks.propertyIsEnumerable(cur) || end_blocks.propertyIsEnumerable(cur)) {
    return "keyword";
  }
  if (atoms.propertyIsEnumerable(cur)) return "atom";
  return "variable";
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if ((ch == "/" || ch == ")") && maybeEnd) {
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
  if (t == "end_block") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

// Interface

const fcl = {
  name: "fcl",
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
    }
    if (stream.eatSpace()) return null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment") return style;
    if (ctx.align == null) ctx.align = true;
    var cur = stream.current().toLowerCase();
    if (start_blocks.propertyIsEnumerable(cur)) pushContext(state, stream.column(), "end_block");else if (end_blocks.propertyIsEnumerable(cur)) popContext(state);
    state.startOfLine = false;
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != tokenBase && state.tokenize != null) return 0;
    var ctx = state.context;
    var closing = end_blocks.propertyIsEnumerable(textAfter);
    if (ctx.align) return ctx.column + (closing ? 0 : 1);else return ctx.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    commentTokens: {
      line: "//",
      block: {
        open: "(*",
        close: "*)"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjQ5NS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZmNsLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBrZXl3b3JkcyA9IHtcbiAgXCJ0ZXJtXCI6IHRydWUsXG4gIFwibWV0aG9kXCI6IHRydWUsXG4gIFwiYWNjdVwiOiB0cnVlLFxuICBcInJ1bGVcIjogdHJ1ZSxcbiAgXCJ0aGVuXCI6IHRydWUsXG4gIFwiaXNcIjogdHJ1ZSxcbiAgXCJhbmRcIjogdHJ1ZSxcbiAgXCJvclwiOiB0cnVlLFxuICBcImlmXCI6IHRydWUsXG4gIFwiZGVmYXVsdFwiOiB0cnVlXG59O1xudmFyIHN0YXJ0X2Jsb2NrcyA9IHtcbiAgXCJ2YXJfaW5wdXRcIjogdHJ1ZSxcbiAgXCJ2YXJfb3V0cHV0XCI6IHRydWUsXG4gIFwiZnV6emlmeVwiOiB0cnVlLFxuICBcImRlZnV6emlmeVwiOiB0cnVlLFxuICBcImZ1bmN0aW9uX2Jsb2NrXCI6IHRydWUsXG4gIFwicnVsZWJsb2NrXCI6IHRydWVcbn07XG52YXIgZW5kX2Jsb2NrcyA9IHtcbiAgXCJlbmRfcnVsZWJsb2NrXCI6IHRydWUsXG4gIFwiZW5kX2RlZnV6emlmeVwiOiB0cnVlLFxuICBcImVuZF9mdW5jdGlvbl9ibG9ja1wiOiB0cnVlLFxuICBcImVuZF9mdXp6aWZ5XCI6IHRydWUsXG4gIFwiZW5kX3ZhclwiOiB0cnVlXG59O1xudmFyIGF0b21zID0ge1xuICBcInRydWVcIjogdHJ1ZSxcbiAgXCJmYWxzZVwiOiB0cnVlLFxuICBcIm5hblwiOiB0cnVlLFxuICBcInJlYWxcIjogdHJ1ZSxcbiAgXCJtaW5cIjogdHJ1ZSxcbiAgXCJtYXhcIjogdHJ1ZSxcbiAgXCJjb2dcIjogdHJ1ZSxcbiAgXCJjb2dzXCI6IHRydWVcbn07XG52YXIgaXNPcGVyYXRvckNoYXIgPSAvWytcXC0qJl4lOj08PiF8XFwvXS87XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoL1tcXGRcXC5dLy50ZXN0KGNoKSkge1xuICAgIGlmIChjaCA9PSBcIi5cIikge1xuICAgICAgc3RyZWFtLm1hdGNoKC9eWzAtOV0rKFtlRV1bXFwtK10/WzAtOV0rKT8vKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiMFwiKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15beFhdWzAtOWEtZkEtRl0rLykgfHwgc3RyZWFtLm1hdGNoKC9eMFswLTddKy8pO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15bMC05XSpcXC4/WzAtOV0qKFtlRV1bXFwtK10/WzAtOV0rKT8vKTtcbiAgICB9XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgaWYgKGNoID09IFwiL1wiIHx8IGNoID09IFwiKFwiKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCIqXCIpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ29tbWVudDtcbiAgICAgIHJldHVybiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uZWF0KFwiL1wiKSkge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgIH1cbiAgfVxuICBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNPcGVyYXRvckNoYXIpO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cbiAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX1xceGExLVxcdWZmZmZdLyk7XG4gIHZhciBjdXIgPSBzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCk7XG4gIGlmIChrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpIHx8IHN0YXJ0X2Jsb2Nrcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpIHx8IGVuZF9ibG9ja3MucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkge1xuICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgfVxuICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoKGNoID09IFwiL1wiIHx8IGNoID09IFwiKVwiKSAmJiBtYXliZUVuZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbWF5YmVFbmQgPSBjaCA9PSBcIipcIjtcbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5mdW5jdGlvbiBDb250ZXh0KGluZGVudGVkLCBjb2x1bW4sIHR5cGUsIGFsaWduLCBwcmV2KSB7XG4gIHRoaXMuaW5kZW50ZWQgPSBpbmRlbnRlZDtcbiAgdGhpcy5jb2x1bW4gPSBjb2x1bW47XG4gIHRoaXMudHlwZSA9IHR5cGU7XG4gIHRoaXMuYWxpZ24gPSBhbGlnbjtcbiAgdGhpcy5wcmV2ID0gcHJldjtcbn1cbmZ1bmN0aW9uIHB1c2hDb250ZXh0KHN0YXRlLCBjb2wsIHR5cGUpIHtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBuZXcgQ29udGV4dChzdGF0ZS5pbmRlbnRlZCwgY29sLCB0eXBlLCBudWxsLCBzdGF0ZS5jb250ZXh0KTtcbn1cbmZ1bmN0aW9uIHBvcENvbnRleHQoc3RhdGUpIHtcbiAgaWYgKCFzdGF0ZS5jb250ZXh0LnByZXYpIHJldHVybjtcbiAgdmFyIHQgPSBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIGlmICh0ID09IFwiZW5kX2Jsb2NrXCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG59XG5cbi8vIEludGVyZmFjZVxuXG5leHBvcnQgY29uc3QgZmNsID0ge1xuICBuYW1lOiBcImZjbFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogbnVsbCxcbiAgICAgIGNvbnRleHQ6IG5ldyBDb250ZXh0KC1pbmRlbnRVbml0LCAwLCBcInRvcFwiLCBmYWxzZSksXG4gICAgICBpbmRlbnRlZDogMCxcbiAgICAgIHN0YXJ0T2ZMaW5lOiB0cnVlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGN0eCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSBmYWxzZTtcbiAgICAgIHN0YXRlLmluZGVudGVkID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgICBzdGF0ZS5zdGFydE9mTGluZSA9IHRydWU7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIHN0eWxlID0gKHN0YXRlLnRva2VuaXplIHx8IHRva2VuQmFzZSkoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0eWxlID09IFwiY29tbWVudFwiKSByZXR1cm4gc3R5bGU7XG4gICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSB0cnVlO1xuICAgIHZhciBjdXIgPSBzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCk7XG4gICAgaWYgKHN0YXJ0X2Jsb2Nrcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcImVuZF9ibG9ja1wiKTtlbHNlIGlmIChlbmRfYmxvY2tzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHBvcENvbnRleHQoc3RhdGUpO1xuICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gZmFsc2U7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgIGlmIChzdGF0ZS50b2tlbml6ZSAhPSB0b2tlbkJhc2UgJiYgc3RhdGUudG9rZW5pemUgIT0gbnVsbCkgcmV0dXJuIDA7XG4gICAgdmFyIGN0eCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgdmFyIGNsb3NpbmcgPSBlbmRfYmxvY2tzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHRleHRBZnRlcik7XG4gICAgaWYgKGN0eC5hbGlnbikgcmV0dXJuIGN0eC5jb2x1bW4gKyAoY2xvc2luZyA/IDAgOiAxKTtlbHNlIHJldHVybiBjdHguaW5kZW50ZWQgKyAoY2xvc2luZyA/IDAgOiBjeC51bml0KTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIvL1wiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIoKlwiLFxuICAgICAgICBjbG9zZTogXCIqKVwiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=