"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[8383],{

/***/ 28383
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   eiffel: () => (/* binding */ eiffel)
/* harmony export */ });
function wordObj(words) {
  var o = {};
  for (var i = 0, e = words.length; i < e; ++i) o[words[i]] = true;
  return o;
}
var keywords = wordObj(['note', 'across', 'when', 'variant', 'until', 'unique', 'undefine', 'then', 'strip', 'select', 'retry', 'rescue', 'require', 'rename', 'reference', 'redefine', 'prefix', 'once', 'old', 'obsolete', 'loop', 'local', 'like', 'is', 'inspect', 'infix', 'include', 'if', 'frozen', 'from', 'external', 'export', 'ensure', 'end', 'elseif', 'else', 'do', 'creation', 'create', 'check', 'alias', 'agent', 'separate', 'invariant', 'inherit', 'indexing', 'feature', 'expanded', 'deferred', 'class', 'Void', 'True', 'Result', 'Precursor', 'False', 'Current', 'create', 'attached', 'detachable', 'as', 'and', 'implies', 'not', 'or']);
var operators = wordObj([":=", "and then", "and", "or", "<<", ">>"]);
function chain(newtok, stream, state) {
  state.tokenize.push(newtok);
  return newtok(stream, state);
}
function tokenBase(stream, state) {
  if (stream.eatSpace()) return null;
  var ch = stream.next();
  if (ch == '"' || ch == "'") {
    return chain(readQuoted(ch, "string"), stream, state);
  } else if (ch == "-" && stream.eat("-")) {
    stream.skipToEnd();
    return "comment";
  } else if (ch == ":" && stream.eat("=")) {
    return "operator";
  } else if (/[0-9]/.test(ch)) {
    stream.eatWhile(/[xXbBCc0-9\.]/);
    stream.eat(/[\?\!]/);
    return "variable";
  } else if (/[a-zA-Z_0-9]/.test(ch)) {
    stream.eatWhile(/[a-zA-Z_0-9]/);
    stream.eat(/[\?\!]/);
    return "variable";
  } else if (/[=+\-\/*^%<>~]/.test(ch)) {
    stream.eatWhile(/[=+\-\/*^%<>~]/);
    return "operator";
  } else {
    return null;
  }
}
function readQuoted(quote, style, unescaped) {
  return function (stream, state) {
    var escaped = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch == quote && (unescaped || !escaped)) {
        state.tokenize.pop();
        break;
      }
      escaped = !escaped && ch == "%";
    }
    return style;
  };
}
const eiffel = {
  name: "eiffel",
  startState: function () {
    return {
      tokenize: [tokenBase]
    };
  },
  token: function (stream, state) {
    var style = state.tokenize[state.tokenize.length - 1](stream, state);
    if (style == "variable") {
      var word = stream.current();
      style = keywords.propertyIsEnumerable(stream.current()) ? "keyword" : operators.propertyIsEnumerable(stream.current()) ? "operator" : /^[A-Z][A-Z_0-9]*$/g.test(word) ? "tag" : /^0[bB][0-1]+$/g.test(word) ? "number" : /^0[cC][0-7]+$/g.test(word) ? "number" : /^0[xX][a-fA-F0-9]+$/g.test(word) ? "number" : /^([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)$/g.test(word) ? "number" : /^[0-9]+$/g.test(word) ? "number" : "variable";
    }
    return style;
  },
  languageData: {
    commentTokens: {
      line: "--"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiODM4My5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9laWZmZWwuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZE9iaih3b3Jkcykge1xuICB2YXIgbyA9IHt9O1xuICBmb3IgKHZhciBpID0gMCwgZSA9IHdvcmRzLmxlbmd0aDsgaSA8IGU7ICsraSkgb1t3b3Jkc1tpXV0gPSB0cnVlO1xuICByZXR1cm4gbztcbn1cbnZhciBrZXl3b3JkcyA9IHdvcmRPYmooWydub3RlJywgJ2Fjcm9zcycsICd3aGVuJywgJ3ZhcmlhbnQnLCAndW50aWwnLCAndW5pcXVlJywgJ3VuZGVmaW5lJywgJ3RoZW4nLCAnc3RyaXAnLCAnc2VsZWN0JywgJ3JldHJ5JywgJ3Jlc2N1ZScsICdyZXF1aXJlJywgJ3JlbmFtZScsICdyZWZlcmVuY2UnLCAncmVkZWZpbmUnLCAncHJlZml4JywgJ29uY2UnLCAnb2xkJywgJ29ic29sZXRlJywgJ2xvb3AnLCAnbG9jYWwnLCAnbGlrZScsICdpcycsICdpbnNwZWN0JywgJ2luZml4JywgJ2luY2x1ZGUnLCAnaWYnLCAnZnJvemVuJywgJ2Zyb20nLCAnZXh0ZXJuYWwnLCAnZXhwb3J0JywgJ2Vuc3VyZScsICdlbmQnLCAnZWxzZWlmJywgJ2Vsc2UnLCAnZG8nLCAnY3JlYXRpb24nLCAnY3JlYXRlJywgJ2NoZWNrJywgJ2FsaWFzJywgJ2FnZW50JywgJ3NlcGFyYXRlJywgJ2ludmFyaWFudCcsICdpbmhlcml0JywgJ2luZGV4aW5nJywgJ2ZlYXR1cmUnLCAnZXhwYW5kZWQnLCAnZGVmZXJyZWQnLCAnY2xhc3MnLCAnVm9pZCcsICdUcnVlJywgJ1Jlc3VsdCcsICdQcmVjdXJzb3InLCAnRmFsc2UnLCAnQ3VycmVudCcsICdjcmVhdGUnLCAnYXR0YWNoZWQnLCAnZGV0YWNoYWJsZScsICdhcycsICdhbmQnLCAnaW1wbGllcycsICdub3QnLCAnb3InXSk7XG52YXIgb3BlcmF0b3JzID0gd29yZE9iaihbXCI6PVwiLCBcImFuZCB0aGVuXCIsIFwiYW5kXCIsIFwib3JcIiwgXCI8PFwiLCBcIj4+XCJdKTtcbmZ1bmN0aW9uIGNoYWluKG5ld3Rvaywgc3RyZWFtLCBzdGF0ZSkge1xuICBzdGF0ZS50b2tlbml6ZS5wdXNoKG5ld3Rvayk7XG4gIHJldHVybiBuZXd0b2soc3RyZWFtLCBzdGF0ZSk7XG59XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoY2ggPT0gJ1wiJyB8fCBjaCA9PSBcIidcIikge1xuICAgIHJldHVybiBjaGFpbihyZWFkUXVvdGVkKGNoLCBcInN0cmluZ1wiKSwgc3RyZWFtLCBzdGF0ZSk7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCItXCIgJiYgc3RyZWFtLmVhdChcIi1cIikpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiOlwiICYmIHN0cmVhbS5lYXQoXCI9XCIpKSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfSBlbHNlIGlmICgvWzAtOV0vLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9beFhiQkNjMC05XFwuXS8pO1xuICAgIHN0cmVhbS5lYXQoL1tcXD9cXCFdLyk7XG4gICAgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgfSBlbHNlIGlmICgvW2EtekEtWl8wLTldLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW2EtekEtWl8wLTldLyk7XG4gICAgc3RyZWFtLmVhdCgvW1xcP1xcIV0vKTtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9IGVsc2UgaWYgKC9bPStcXC1cXC8qXiU8Pn5dLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvWz0rXFwtXFwvKl4lPD5+XS8pO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH0gZWxzZSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbn1cbmZ1bmN0aW9uIHJlYWRRdW90ZWQocXVvdGUsIHN0eWxlLCB1bmVzY2FwZWQpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlICgoY2ggPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAoY2ggPT0gcXVvdGUgJiYgKHVuZXNjYXBlZCB8fCAhZXNjYXBlZCkpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIGNoID09IFwiJVwiO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH07XG59XG5leHBvcnQgY29uc3QgZWlmZmVsID0ge1xuICBuYW1lOiBcImVpZmZlbFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBbdG9rZW5CYXNlXVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBzdHlsZSA9IHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICAgIHN0eWxlID0ga2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUoc3RyZWFtLmN1cnJlbnQoKSkgPyBcImtleXdvcmRcIiA6IG9wZXJhdG9ycy5wcm9wZXJ0eUlzRW51bWVyYWJsZShzdHJlYW0uY3VycmVudCgpKSA/IFwib3BlcmF0b3JcIiA6IC9eW0EtWl1bQS1aXzAtOV0qJC9nLnRlc3Qod29yZCkgPyBcInRhZ1wiIDogL14wW2JCXVswLTFdKyQvZy50ZXN0KHdvcmQpID8gXCJudW1iZXJcIiA6IC9eMFtjQ11bMC03XSskL2cudGVzdCh3b3JkKSA/IFwibnVtYmVyXCIgOiAvXjBbeFhdW2EtZkEtRjAtOV0rJC9nLnRlc3Qod29yZCkgPyBcIm51bWJlclwiIDogL14oWzAtOV0rXFwuWzAtOV0qKXwoWzAtOV0qXFwuWzAtOV0rKSQvZy50ZXN0KHdvcmQpID8gXCJudW1iZXJcIiA6IC9eWzAtOV0rJC9nLnRlc3Qod29yZCkgPyBcIm51bWJlclwiIDogXCJ2YXJpYWJsZVwiO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiLS1cIlxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9