"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3881],{

/***/ 53881
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   yacas: () => (/* binding */ yacas)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var bodiedOps = words("Assert BackQuote D Defun Deriv For ForEach FromFile " + "FromString Function Integrate InverseTaylor Limit " + "LocalSymbols Macro MacroRule MacroRulePattern " + "NIntegrate Rule RulePattern Subst TD TExplicitSum " + "TSum Taylor Taylor1 Taylor2 Taylor3 ToFile " + "ToStdout ToString TraceRule Until While");

// patterns
var pFloatForm = "(?:(?:\\.\\d+|\\d+\\.\\d*|\\d+)(?:[eE][+-]?\\d+)?)";
var pIdentifier = "(?:[a-zA-Z\\$'][a-zA-Z0-9\\$']*)";

// regular expressions
var reFloatForm = new RegExp(pFloatForm);
var reIdentifier = new RegExp(pIdentifier);
var rePattern = new RegExp(pIdentifier + "?_" + pIdentifier);
var reFunctionLike = new RegExp(pIdentifier + "\\s*\\(");
function tokenBase(stream, state) {
  var ch;

  // get next character
  ch = stream.next();

  // string
  if (ch === '"') {
    state.tokenize = tokenString;
    return state.tokenize(stream, state);
  }

  // comment
  if (ch === '/') {
    if (stream.eat('*')) {
      state.tokenize = tokenComment;
      return state.tokenize(stream, state);
    }
    if (stream.eat("/")) {
      stream.skipToEnd();
      return "comment";
    }
  }

  // go back one character
  stream.backUp(1);

  // update scope info
  var m = stream.match(/^(\w+)\s*\(/, false);
  if (m !== null && bodiedOps.hasOwnProperty(m[1])) state.scopes.push('bodied');
  var scope = currentScope(state);
  if (scope === 'bodied' && ch === '[') state.scopes.pop();
  if (ch === '[' || ch === '{' || ch === '(') state.scopes.push(ch);
  scope = currentScope(state);
  if (scope === '[' && ch === ']' || scope === '{' && ch === '}' || scope === '(' && ch === ')') state.scopes.pop();
  if (ch === ';') {
    while (scope === 'bodied') {
      state.scopes.pop();
      scope = currentScope(state);
    }
  }

  // look for ordered rules
  if (stream.match(/\d+ *#/, true, false)) {
    return 'qualifier';
  }

  // look for numbers
  if (stream.match(reFloatForm, true, false)) {
    return 'number';
  }

  // look for placeholders
  if (stream.match(rePattern, true, false)) {
    return 'variableName.special';
  }

  // match all braces separately
  if (stream.match(/(?:\[|\]|{|}|\(|\))/, true, false)) {
    return 'bracket';
  }

  // literals looking like function calls
  if (stream.match(reFunctionLike, true, false)) {
    stream.backUp(1);
    return 'variableName.function';
  }

  // all other identifiers
  if (stream.match(reIdentifier, true, false)) {
    return 'variable';
  }

  // operators; note that operators like @@ or /; are matched separately for each symbol.
  if (stream.match(/(?:\\|\+|\-|\*|\/|,|;|\.|:|@|~|=|>|<|&|\||_|`|'|\^|\?|!|%|#)/, true, false)) {
    return 'operator';
  }

  // everything else is an error
  return 'error';
}
function tokenString(stream, state) {
  var next,
    end = false,
    escaped = false;
  while ((next = stream.next()) != null) {
    if (next === '"' && !escaped) {
      end = true;
      break;
    }
    escaped = !escaped && next === '\\';
  }
  if (end && !escaped) {
    state.tokenize = tokenBase;
  }
  return 'string';
}
;
function tokenComment(stream, state) {
  var prev, next;
  while ((next = stream.next()) != null) {
    if (prev === '*' && next === '/') {
      state.tokenize = tokenBase;
      break;
    }
    prev = next;
  }
  return 'comment';
}
function currentScope(state) {
  var scope = null;
  if (state.scopes.length > 0) scope = state.scopes[state.scopes.length - 1];
  return scope;
}
const yacas = {
  name: "yacas",
  startState: function () {
    return {
      tokenize: tokenBase,
      scopes: []
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return state.tokenize(stream, state);
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize !== tokenBase && state.tokenize !== null) return null;
    var delta = 0;
    if (textAfter === ']' || textAfter === '];' || textAfter === '}' || textAfter === '};' || textAfter === ');') delta = -1;
    return (state.scopes.length + delta) * cx.unit;
  },
  languageData: {
    electricInput: /[{}\[\]()\;]/,
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzg4MS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUveWFjYXMuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZHMoc3RyKSB7XG4gIHZhciBvYmogPSB7fSxcbiAgICB3b3JkcyA9IHN0ci5zcGxpdChcIiBcIik7XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgd29yZHMubGVuZ3RoOyArK2kpIG9ialt3b3Jkc1tpXV0gPSB0cnVlO1xuICByZXR1cm4gb2JqO1xufVxudmFyIGJvZGllZE9wcyA9IHdvcmRzKFwiQXNzZXJ0IEJhY2tRdW90ZSBEIERlZnVuIERlcml2IEZvciBGb3JFYWNoIEZyb21GaWxlIFwiICsgXCJGcm9tU3RyaW5nIEZ1bmN0aW9uIEludGVncmF0ZSBJbnZlcnNlVGF5bG9yIExpbWl0IFwiICsgXCJMb2NhbFN5bWJvbHMgTWFjcm8gTWFjcm9SdWxlIE1hY3JvUnVsZVBhdHRlcm4gXCIgKyBcIk5JbnRlZ3JhdGUgUnVsZSBSdWxlUGF0dGVybiBTdWJzdCBURCBURXhwbGljaXRTdW0gXCIgKyBcIlRTdW0gVGF5bG9yIFRheWxvcjEgVGF5bG9yMiBUYXlsb3IzIFRvRmlsZSBcIiArIFwiVG9TdGRvdXQgVG9TdHJpbmcgVHJhY2VSdWxlIFVudGlsIFdoaWxlXCIpO1xuXG4vLyBwYXR0ZXJuc1xudmFyIHBGbG9hdEZvcm0gPSBcIig/Oig/OlxcXFwuXFxcXGQrfFxcXFxkK1xcXFwuXFxcXGQqfFxcXFxkKykoPzpbZUVdWystXT9cXFxcZCspPylcIjtcbnZhciBwSWRlbnRpZmllciA9IFwiKD86W2EtekEtWlxcXFwkJ11bYS16QS1aMC05XFxcXCQnXSopXCI7XG5cbi8vIHJlZ3VsYXIgZXhwcmVzc2lvbnNcbnZhciByZUZsb2F0Rm9ybSA9IG5ldyBSZWdFeHAocEZsb2F0Rm9ybSk7XG52YXIgcmVJZGVudGlmaWVyID0gbmV3IFJlZ0V4cChwSWRlbnRpZmllcik7XG52YXIgcmVQYXR0ZXJuID0gbmV3IFJlZ0V4cChwSWRlbnRpZmllciArIFwiP19cIiArIHBJZGVudGlmaWVyKTtcbnZhciByZUZ1bmN0aW9uTGlrZSA9IG5ldyBSZWdFeHAocElkZW50aWZpZXIgKyBcIlxcXFxzKlxcXFwoXCIpO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoO1xuXG4gIC8vIGdldCBuZXh0IGNoYXJhY3RlclxuICBjaCA9IHN0cmVhbS5uZXh0KCk7XG5cbiAgLy8gc3RyaW5nXG4gIGlmIChjaCA9PT0gJ1wiJykge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmc7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG5cbiAgLy8gY29tbWVudFxuICBpZiAoY2ggPT09ICcvJykge1xuICAgIGlmIChzdHJlYW0uZWF0KCcqJykpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Db21tZW50O1xuICAgICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gIH1cblxuICAvLyBnbyBiYWNrIG9uZSBjaGFyYWN0ZXJcbiAgc3RyZWFtLmJhY2tVcCgxKTtcblxuICAvLyB1cGRhdGUgc2NvcGUgaW5mb1xuICB2YXIgbSA9IHN0cmVhbS5tYXRjaCgvXihcXHcrKVxccypcXCgvLCBmYWxzZSk7XG4gIGlmIChtICE9PSBudWxsICYmIGJvZGllZE9wcy5oYXNPd25Qcm9wZXJ0eShtWzFdKSkgc3RhdGUuc2NvcGVzLnB1c2goJ2JvZGllZCcpO1xuICB2YXIgc2NvcGUgPSBjdXJyZW50U2NvcGUoc3RhdGUpO1xuICBpZiAoc2NvcGUgPT09ICdib2RpZWQnICYmIGNoID09PSAnWycpIHN0YXRlLnNjb3Blcy5wb3AoKTtcbiAgaWYgKGNoID09PSAnWycgfHwgY2ggPT09ICd7JyB8fCBjaCA9PT0gJygnKSBzdGF0ZS5zY29wZXMucHVzaChjaCk7XG4gIHNjb3BlID0gY3VycmVudFNjb3BlKHN0YXRlKTtcbiAgaWYgKHNjb3BlID09PSAnWycgJiYgY2ggPT09ICddJyB8fCBzY29wZSA9PT0gJ3snICYmIGNoID09PSAnfScgfHwgc2NvcGUgPT09ICcoJyAmJiBjaCA9PT0gJyknKSBzdGF0ZS5zY29wZXMucG9wKCk7XG4gIGlmIChjaCA9PT0gJzsnKSB7XG4gICAgd2hpbGUgKHNjb3BlID09PSAnYm9kaWVkJykge1xuICAgICAgc3RhdGUuc2NvcGVzLnBvcCgpO1xuICAgICAgc2NvcGUgPSBjdXJyZW50U2NvcGUoc3RhdGUpO1xuICAgIH1cbiAgfVxuXG4gIC8vIGxvb2sgZm9yIG9yZGVyZWQgcnVsZXNcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXFxkKyAqIy8sIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAncXVhbGlmaWVyJztcbiAgfVxuXG4gIC8vIGxvb2sgZm9yIG51bWJlcnNcbiAgaWYgKHN0cmVhbS5tYXRjaChyZUZsb2F0Rm9ybSwgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICdudW1iZXInO1xuICB9XG5cbiAgLy8gbG9vayBmb3IgcGxhY2Vob2xkZXJzXG4gIGlmIChzdHJlYW0ubWF0Y2gocmVQYXR0ZXJuLCB0cnVlLCBmYWxzZSkpIHtcbiAgICByZXR1cm4gJ3ZhcmlhYmxlTmFtZS5zcGVjaWFsJztcbiAgfVxuXG4gIC8vIG1hdGNoIGFsbCBicmFjZXMgc2VwYXJhdGVseVxuICBpZiAoc3RyZWFtLm1hdGNoKC8oPzpcXFt8XFxdfHt8fXxcXCh8XFwpKS8sIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAnYnJhY2tldCc7XG4gIH1cblxuICAvLyBsaXRlcmFscyBsb29raW5nIGxpa2UgZnVuY3Rpb24gY2FsbHNcbiAgaWYgKHN0cmVhbS5tYXRjaChyZUZ1bmN0aW9uTGlrZSwgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICByZXR1cm4gJ3ZhcmlhYmxlTmFtZS5mdW5jdGlvbic7XG4gIH1cblxuICAvLyBhbGwgb3RoZXIgaWRlbnRpZmllcnNcbiAgaWYgKHN0cmVhbS5tYXRjaChyZUlkZW50aWZpZXIsIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAndmFyaWFibGUnO1xuICB9XG5cbiAgLy8gb3BlcmF0b3JzOyBub3RlIHRoYXQgb3BlcmF0b3JzIGxpa2UgQEAgb3IgLzsgYXJlIG1hdGNoZWQgc2VwYXJhdGVseSBmb3IgZWFjaCBzeW1ib2wuXG4gIGlmIChzdHJlYW0ubWF0Y2goLyg/OlxcXFx8XFwrfFxcLXxcXCp8XFwvfCx8O3xcXC58OnxAfH58PXw+fDx8JnxcXHx8X3xgfCd8XFxefFxcP3whfCV8IykvLCB0cnVlLCBmYWxzZSkpIHtcbiAgICByZXR1cm4gJ29wZXJhdG9yJztcbiAgfVxuXG4gIC8vIGV2ZXJ5dGhpbmcgZWxzZSBpcyBhbiBlcnJvclxuICByZXR1cm4gJ2Vycm9yJztcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG5leHQsXG4gICAgZW5kID0gZmFsc2UsXG4gICAgZXNjYXBlZCA9IGZhbHNlO1xuICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgaWYgKG5leHQgPT09ICdcIicgJiYgIWVzY2FwZWQpIHtcbiAgICAgIGVuZCA9IHRydWU7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIG5leHQgPT09ICdcXFxcJztcbiAgfVxuICBpZiAoZW5kICYmICFlc2NhcGVkKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gIH1cbiAgcmV0dXJuICdzdHJpbmcnO1xufVxuO1xuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIHByZXYsIG5leHQ7XG4gIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAocHJldiA9PT0gJyonICYmIG5leHQgPT09ICcvJykge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgcHJldiA9IG5leHQ7XG4gIH1cbiAgcmV0dXJuICdjb21tZW50Jztcbn1cbmZ1bmN0aW9uIGN1cnJlbnRTY29wZShzdGF0ZSkge1xuICB2YXIgc2NvcGUgPSBudWxsO1xuICBpZiAoc3RhdGUuc2NvcGVzLmxlbmd0aCA+IDApIHNjb3BlID0gc3RhdGUuc2NvcGVzW3N0YXRlLnNjb3Blcy5sZW5ndGggLSAxXTtcbiAgcmV0dXJuIHNjb3BlO1xufVxuZXhwb3J0IGNvbnN0IHlhY2FzID0ge1xuICBuYW1lOiBcInlhY2FzXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IHRva2VuQmFzZSxcbiAgICAgIHNjb3BlczogW11cbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICBpZiAoc3RhdGUudG9rZW5pemUgIT09IHRva2VuQmFzZSAmJiBzdGF0ZS50b2tlbml6ZSAhPT0gbnVsbCkgcmV0dXJuIG51bGw7XG4gICAgdmFyIGRlbHRhID0gMDtcbiAgICBpZiAodGV4dEFmdGVyID09PSAnXScgfHwgdGV4dEFmdGVyID09PSAnXTsnIHx8IHRleHRBZnRlciA9PT0gJ30nIHx8IHRleHRBZnRlciA9PT0gJ307JyB8fCB0ZXh0QWZ0ZXIgPT09ICcpOycpIGRlbHRhID0gLTE7XG4gICAgcmV0dXJuIChzdGF0ZS5zY29wZXMubGVuZ3RoICsgZGVsdGEpICogY3gudW5pdDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgZWxlY3RyaWNJbnB1dDogL1t7fVxcW1xcXSgpXFw7XS8sXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIvL1wiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=