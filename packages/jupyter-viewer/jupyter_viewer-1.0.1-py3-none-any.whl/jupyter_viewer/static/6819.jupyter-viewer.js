"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6819],{

/***/ 26819
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   velocity: () => (/* binding */ velocity)
/* harmony export */ });
function parseWords(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = parseWords("#end #else #break #stop #[[ #]] " + "#{end} #{else} #{break} #{stop}");
var functions = parseWords("#if #elseif #foreach #set #include #parse #macro #define #evaluate " + "#{if} #{elseif} #{foreach} #{set} #{include} #{parse} #{macro} #{define} #{evaluate}");
var specials = parseWords("$foreach.count $foreach.hasNext $foreach.first $foreach.last $foreach.topmost $foreach.parent.count $foreach.parent.hasNext $foreach.parent.first $foreach.parent.last $foreach.parent $velocityCount $!bodyContent $bodyContent");
var isOperatorChar = /[+\-*&%=<>!?:\/|]/;
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}
function tokenBase(stream, state) {
  var beforeParams = state.beforeParams;
  state.beforeParams = false;
  var ch = stream.next();
  // start of unparsed string?
  if (ch == "'" && !state.inString && state.inParams) {
    state.lastTokenWasBuiltin = false;
    return chain(stream, state, tokenString(ch));
  }
  // start of parsed string?
  else if (ch == '"') {
    state.lastTokenWasBuiltin = false;
    if (state.inString) {
      state.inString = false;
      return "string";
    } else if (state.inParams) return chain(stream, state, tokenString(ch));
  }
  // is it one of the special signs []{}().,;? Separator?
  else if (/[\[\]{}\(\),;\.]/.test(ch)) {
    if (ch == "(" && beforeParams) state.inParams = true;else if (ch == ")") {
      state.inParams = false;
      state.lastTokenWasBuiltin = true;
    }
    return null;
  }
  // start of a number value?
  else if (/\d/.test(ch)) {
    state.lastTokenWasBuiltin = false;
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  // multi line comment?
  else if (ch == "#" && stream.eat("*")) {
    state.lastTokenWasBuiltin = false;
    return chain(stream, state, tokenComment);
  }
  // unparsed content?
  else if (ch == "#" && stream.match(/ *\[ *\[/)) {
    state.lastTokenWasBuiltin = false;
    return chain(stream, state, tokenUnparsed);
  }
  // single line comment?
  else if (ch == "#" && stream.eat("#")) {
    state.lastTokenWasBuiltin = false;
    stream.skipToEnd();
    return "comment";
  }
  // variable?
  else if (ch == "$") {
    stream.eat("!");
    stream.eatWhile(/[\w\d\$_\.{}-]/);
    // is it one of the specials?
    if (specials && specials.propertyIsEnumerable(stream.current())) {
      return "keyword";
    } else {
      state.lastTokenWasBuiltin = true;
      state.beforeParams = true;
      return "builtin";
    }
  }
  // is it a operator?
  else if (isOperatorChar.test(ch)) {
    state.lastTokenWasBuiltin = false;
    stream.eatWhile(isOperatorChar);
    return "operator";
  } else {
    // get the whole word
    stream.eatWhile(/[\w\$_{}@]/);
    var word = stream.current();
    // is it one of the listed keywords?
    if (keywords && keywords.propertyIsEnumerable(word)) return "keyword";
    // is it one of the listed functions?
    if (functions && functions.propertyIsEnumerable(word) || stream.current().match(/^#@?[a-z0-9_]+ *$/i) && stream.peek() == "(" && !(functions && functions.propertyIsEnumerable(word.toLowerCase()))) {
      state.beforeParams = true;
      state.lastTokenWasBuiltin = false;
      return "keyword";
    }
    if (state.inString) {
      state.lastTokenWasBuiltin = false;
      return "string";
    }
    if (stream.pos > word.length && stream.string.charAt(stream.pos - word.length - 1) == "." && state.lastTokenWasBuiltin) return "builtin";
    // default: just a "word"
    state.lastTokenWasBuiltin = false;
    return null;
  }
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        end = true;
        break;
      }
      if (quote == '"' && stream.peek() == '$' && !escaped) {
        state.inString = true;
        end = true;
        break;
      }
      escaped = !escaped && next == "\\";
    }
    if (end) state.tokenize = tokenBase;
    return "string";
  };
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "#" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function tokenUnparsed(stream, state) {
  var maybeEnd = 0,
    ch;
  while (ch = stream.next()) {
    if (ch == "#" && maybeEnd == 2) {
      state.tokenize = tokenBase;
      break;
    }
    if (ch == "]") maybeEnd++;else if (ch != " ") maybeEnd = 0;
  }
  return "meta";
}
// Interface

const velocity = {
  name: "velocity",
  startState: function () {
    return {
      tokenize: tokenBase,
      beforeParams: false,
      inParams: false,
      inString: false,
      lastTokenWasBuiltin: false
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return state.tokenize(stream, state);
  },
  languageData: {
    commentTokens: {
      line: "##",
      block: {
        open: "#*",
        close: "*#"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjgxOS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS92ZWxvY2l0eS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBwYXJzZVdvcmRzKHN0cikge1xuICB2YXIgb2JqID0ge30sXG4gICAgd29yZHMgPSBzdHIuc3BsaXQoXCIgXCIpO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHdvcmRzLmxlbmd0aDsgKytpKSBvYmpbd29yZHNbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIG9iajtcbn1cbnZhciBrZXl3b3JkcyA9IHBhcnNlV29yZHMoXCIjZW5kICNlbHNlICNicmVhayAjc3RvcCAjW1sgI11dIFwiICsgXCIje2VuZH0gI3tlbHNlfSAje2JyZWFrfSAje3N0b3B9XCIpO1xudmFyIGZ1bmN0aW9ucyA9IHBhcnNlV29yZHMoXCIjaWYgI2Vsc2VpZiAjZm9yZWFjaCAjc2V0ICNpbmNsdWRlICNwYXJzZSAjbWFjcm8gI2RlZmluZSAjZXZhbHVhdGUgXCIgKyBcIiN7aWZ9ICN7ZWxzZWlmfSAje2ZvcmVhY2h9ICN7c2V0fSAje2luY2x1ZGV9ICN7cGFyc2V9ICN7bWFjcm99ICN7ZGVmaW5lfSAje2V2YWx1YXRlfVwiKTtcbnZhciBzcGVjaWFscyA9IHBhcnNlV29yZHMoXCIkZm9yZWFjaC5jb3VudCAkZm9yZWFjaC5oYXNOZXh0ICRmb3JlYWNoLmZpcnN0ICRmb3JlYWNoLmxhc3QgJGZvcmVhY2gudG9wbW9zdCAkZm9yZWFjaC5wYXJlbnQuY291bnQgJGZvcmVhY2gucGFyZW50Lmhhc05leHQgJGZvcmVhY2gucGFyZW50LmZpcnN0ICRmb3JlYWNoLnBhcmVudC5sYXN0ICRmb3JlYWNoLnBhcmVudCAkdmVsb2NpdHlDb3VudCAkIWJvZHlDb250ZW50ICRib2R5Q29udGVudFwiKTtcbnZhciBpc09wZXJhdG9yQ2hhciA9IC9bK1xcLSomJT08PiE/OlxcL3xdLztcbmZ1bmN0aW9uIGNoYWluKHN0cmVhbSwgc3RhdGUsIGYpIHtcbiAgc3RhdGUudG9rZW5pemUgPSBmO1xuICByZXR1cm4gZihzdHJlYW0sIHN0YXRlKTtcbn1cbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBiZWZvcmVQYXJhbXMgPSBzdGF0ZS5iZWZvcmVQYXJhbXM7XG4gIHN0YXRlLmJlZm9yZVBhcmFtcyA9IGZhbHNlO1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICAvLyBzdGFydCBvZiB1bnBhcnNlZCBzdHJpbmc/XG4gIGlmIChjaCA9PSBcIidcIiAmJiAhc3RhdGUuaW5TdHJpbmcgJiYgc3RhdGUuaW5QYXJhbXMpIHtcbiAgICBzdGF0ZS5sYXN0VG9rZW5XYXNCdWlsdGluID0gZmFsc2U7XG4gICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHRva2VuU3RyaW5nKGNoKSk7XG4gIH1cbiAgLy8gc3RhcnQgb2YgcGFyc2VkIHN0cmluZz9cbiAgZWxzZSBpZiAoY2ggPT0gJ1wiJykge1xuICAgIHN0YXRlLmxhc3RUb2tlbldhc0J1aWx0aW4gPSBmYWxzZTtcbiAgICBpZiAoc3RhdGUuaW5TdHJpbmcpIHtcbiAgICAgIHN0YXRlLmluU3RyaW5nID0gZmFsc2U7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9IGVsc2UgaWYgKHN0YXRlLmluUGFyYW1zKSByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdG9rZW5TdHJpbmcoY2gpKTtcbiAgfVxuICAvLyBpcyBpdCBvbmUgb2YgdGhlIHNwZWNpYWwgc2lnbnMgW117fSgpLiw7PyBTZXBhcmF0b3I/XG4gIGVsc2UgaWYgKC9bXFxbXFxde31cXChcXCksO1xcLl0vLnRlc3QoY2gpKSB7XG4gICAgaWYgKGNoID09IFwiKFwiICYmIGJlZm9yZVBhcmFtcykgc3RhdGUuaW5QYXJhbXMgPSB0cnVlO2Vsc2UgaWYgKGNoID09IFwiKVwiKSB7XG4gICAgICBzdGF0ZS5pblBhcmFtcyA9IGZhbHNlO1xuICAgICAgc3RhdGUubGFzdFRva2VuV2FzQnVpbHRpbiA9IHRydWU7XG4gICAgfVxuICAgIHJldHVybiBudWxsO1xuICB9XG4gIC8vIHN0YXJ0IG9mIGEgbnVtYmVyIHZhbHVlP1xuICBlbHNlIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0YXRlLmxhc3RUb2tlbldhc0J1aWx0aW4gPSBmYWxzZTtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXC5dLyk7XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgLy8gbXVsdGkgbGluZSBjb21tZW50P1xuICBlbHNlIGlmIChjaCA9PSBcIiNcIiAmJiBzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgIHN0YXRlLmxhc3RUb2tlbldhc0J1aWx0aW4gPSBmYWxzZTtcbiAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdG9rZW5Db21tZW50KTtcbiAgfVxuICAvLyB1bnBhcnNlZCBjb250ZW50P1xuICBlbHNlIGlmIChjaCA9PSBcIiNcIiAmJiBzdHJlYW0ubWF0Y2goLyAqXFxbICpcXFsvKSkge1xuICAgIHN0YXRlLmxhc3RUb2tlbldhc0J1aWx0aW4gPSBmYWxzZTtcbiAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdG9rZW5VbnBhcnNlZCk7XG4gIH1cbiAgLy8gc2luZ2xlIGxpbmUgY29tbWVudD9cbiAgZWxzZSBpZiAoY2ggPT0gXCIjXCIgJiYgc3RyZWFtLmVhdChcIiNcIikpIHtcbiAgICBzdGF0ZS5sYXN0VG9rZW5XYXNCdWlsdGluID0gZmFsc2U7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuICAvLyB2YXJpYWJsZT9cbiAgZWxzZSBpZiAoY2ggPT0gXCIkXCIpIHtcbiAgICBzdHJlYW0uZWF0KFwiIVwiKTtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXGRcXCRfXFwue30tXS8pO1xuICAgIC8vIGlzIGl0IG9uZSBvZiB0aGUgc3BlY2lhbHM/XG4gICAgaWYgKHNwZWNpYWxzICYmIHNwZWNpYWxzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHN0cmVhbS5jdXJyZW50KCkpKSB7XG4gICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0YXRlLmxhc3RUb2tlbldhc0J1aWx0aW4gPSB0cnVlO1xuICAgICAgc3RhdGUuYmVmb3JlUGFyYW1zID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgICB9XG4gIH1cbiAgLy8gaXMgaXQgYSBvcGVyYXRvcj9cbiAgZWxzZSBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICBzdGF0ZS5sYXN0VG9rZW5XYXNCdWlsdGluID0gZmFsc2U7XG4gICAgc3RyZWFtLmVhdFdoaWxlKGlzT3BlcmF0b3JDaGFyKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9IGVsc2Uge1xuICAgIC8vIGdldCB0aGUgd2hvbGUgd29yZFxuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF97fUBdLyk7XG4gICAgdmFyIHdvcmQgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgIC8vIGlzIGl0IG9uZSBvZiB0aGUgbGlzdGVkIGtleXdvcmRzP1xuICAgIGlmIChrZXl3b3JkcyAmJiBrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIC8vIGlzIGl0IG9uZSBvZiB0aGUgbGlzdGVkIGZ1bmN0aW9ucz9cbiAgICBpZiAoZnVuY3Rpb25zICYmIGZ1bmN0aW9ucy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkKSB8fCBzdHJlYW0uY3VycmVudCgpLm1hdGNoKC9eI0A/W2EtejAtOV9dKyAqJC9pKSAmJiBzdHJlYW0ucGVlaygpID09IFwiKFwiICYmICEoZnVuY3Rpb25zICYmIGZ1bmN0aW9ucy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkLnRvTG93ZXJDYXNlKCkpKSkge1xuICAgICAgc3RhdGUuYmVmb3JlUGFyYW1zID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmxhc3RUb2tlbldhc0J1aWx0aW4gPSBmYWxzZTtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9XG4gICAgaWYgKHN0YXRlLmluU3RyaW5nKSB7XG4gICAgICBzdGF0ZS5sYXN0VG9rZW5XYXNCdWlsdGluID0gZmFsc2U7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5wb3MgPiB3b3JkLmxlbmd0aCAmJiBzdHJlYW0uc3RyaW5nLmNoYXJBdChzdHJlYW0ucG9zIC0gd29yZC5sZW5ndGggLSAxKSA9PSBcIi5cIiAmJiBzdGF0ZS5sYXN0VG9rZW5XYXNCdWlsdGluKSByZXR1cm4gXCJidWlsdGluXCI7XG4gICAgLy8gZGVmYXVsdDoganVzdCBhIFwid29yZFwiXG4gICAgc3RhdGUubGFzdFRva2VuV2FzQnVpbHRpbiA9IGZhbHNlO1xuICAgIHJldHVybiBudWxsO1xuICB9XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhxdW90ZSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgbmV4dCxcbiAgICAgIGVuZCA9IGZhbHNlO1xuICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmIChuZXh0ID09IHF1b3RlICYmICFlc2NhcGVkKSB7XG4gICAgICAgIGVuZCA9IHRydWU7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgaWYgKHF1b3RlID09ICdcIicgJiYgc3RyZWFtLnBlZWsoKSA9PSAnJCcgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgc3RhdGUuaW5TdHJpbmcgPSB0cnVlO1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoZW5kKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfTtcbn1cbmZ1bmN0aW9uIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiI1wiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cbmZ1bmN0aW9uIHRva2VuVW5wYXJzZWQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSAwLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiI1wiICYmIG1heWJlRW5kID09IDIpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIGlmIChjaCA9PSBcIl1cIikgbWF5YmVFbmQrKztlbHNlIGlmIChjaCAhPSBcIiBcIikgbWF5YmVFbmQgPSAwO1xuICB9XG4gIHJldHVybiBcIm1ldGFcIjtcbn1cbi8vIEludGVyZmFjZVxuXG5leHBvcnQgY29uc3QgdmVsb2NpdHkgPSB7XG4gIG5hbWU6IFwidmVsb2NpdHlcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgYmVmb3JlUGFyYW1zOiBmYWxzZSxcbiAgICAgIGluUGFyYW1zOiBmYWxzZSxcbiAgICAgIGluU3RyaW5nOiBmYWxzZSxcbiAgICAgIGxhc3RUb2tlbldhc0J1aWx0aW46IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiIyNcIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiIypcIixcbiAgICAgICAgY2xvc2U6IFwiKiNcIlxuICAgICAgfVxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9