"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5050],{

/***/ 75050
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   groovy: () => (/* binding */ groovy)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = words("abstract as assert boolean break byte case catch char class const continue def default " + "do double else enum extends final finally float for goto if implements import in " + "instanceof int interface long native new package private protected public return " + "short static strictfp super switch synchronized threadsafe throw throws trait transient " + "try void volatile while");
var blockKeywords = words("catch class def do else enum finally for if interface switch trait try while");
var standaloneKeywords = words("return break continue");
var atoms = words("null true false this");
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == '"' || ch == "'") {
    return startString(ch, stream, state);
  }
  if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
    curPunc = ch;
    return null;
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    if (stream.eat(/eE/)) {
      stream.eat(/\+\-/);
      stream.eatWhile(/\d/);
    }
    return "number";
  }
  if (ch == "/") {
    if (stream.eat("*")) {
      state.tokenize.push(tokenComment);
      return tokenComment(stream, state);
    }
    if (stream.eat("/")) {
      stream.skipToEnd();
      return "comment";
    }
    if (expectExpression(state.lastToken, false)) {
      return startString(ch, stream, state);
    }
  }
  if (ch == "-" && stream.eat(">")) {
    curPunc = "->";
    return null;
  }
  if (/[+\-*&%=<>!?|\/~]/.test(ch)) {
    stream.eatWhile(/[+\-*&%=<>|~]/);
    return "operator";
  }
  stream.eatWhile(/[\w\$_]/);
  if (ch == "@") {
    stream.eatWhile(/[\w\$_\.]/);
    return "meta";
  }
  if (state.lastToken == ".") return "property";
  if (stream.eat(":")) {
    curPunc = "proplabel";
    return "property";
  }
  var cur = stream.current();
  if (atoms.propertyIsEnumerable(cur)) {
    return "atom";
  }
  if (keywords.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";else if (standaloneKeywords.propertyIsEnumerable(cur)) curPunc = "standalone";
    return "keyword";
  }
  return "variable";
}
tokenBase.isBase = true;
function startString(quote, stream, state) {
  var tripleQuoted = false;
  if (quote != "/" && stream.eat(quote)) {
    if (stream.eat(quote)) tripleQuoted = true;else return "string";
  }
  function t(stream, state) {
    var escaped = false,
      next,
      end = !tripleQuoted;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        if (!tripleQuoted) {
          break;
        }
        if (stream.match(quote + quote)) {
          end = true;
          break;
        }
      }
      if (quote == '"' && next == "$" && !escaped) {
        if (stream.eat("{")) {
          state.tokenize.push(tokenBaseUntilBrace());
          return "string";
        } else if (stream.match(/^\w/, false)) {
          state.tokenize.push(tokenVariableDeref);
          return "string";
        }
      }
      escaped = !escaped && next == "\\";
    }
    if (end) state.tokenize.pop();
    return "string";
  }
  state.tokenize.push(t);
  return t(stream, state);
}
function tokenBaseUntilBrace() {
  var depth = 1;
  function t(stream, state) {
    if (stream.peek() == "}") {
      depth--;
      if (depth == 0) {
        state.tokenize.pop();
        return state.tokenize[state.tokenize.length - 1](stream, state);
      }
    } else if (stream.peek() == "{") {
      depth++;
    }
    return tokenBase(stream, state);
  }
  t.isBase = true;
  return t;
}
function tokenVariableDeref(stream, state) {
  var next = stream.match(/^(\.|[\w\$_]+)/);
  if (!next || !stream.match(next[0] == "." ? /^[\w$_]/ : /^\./)) state.tokenize.pop();
  if (!next) return state.tokenize[state.tokenize.length - 1](stream, state);
  return next[0] == "." ? null : "variable";
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize.pop();
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function expectExpression(last, newline) {
  return !last || last == "operator" || last == "->" || /[\.\[\{\(,;:]/.test(last) || last == "newstatement" || last == "keyword" || last == "proplabel" || last == "standalone" && !newline;
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
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

// Interface

const groovy = {
  name: "groovy",
  startState: function (indentUnit) {
    return {
      tokenize: [tokenBase],
      context: new Context(-indentUnit, 0, "top", false),
      indented: 0,
      startOfLine: true,
      lastToken: null
    };
  },
  token: function (stream, state) {
    var ctx = state.context;
    if (stream.sol()) {
      if (ctx.align == null) ctx.align = false;
      state.indented = stream.indentation();
      state.startOfLine = true;
      // Automatic semicolon insertion
      if (ctx.type == "statement" && !expectExpression(state.lastToken, true)) {
        popContext(state);
        ctx = state.context;
      }
    }
    if (stream.eatSpace()) return null;
    curPunc = null;
    var style = state.tokenize[state.tokenize.length - 1](stream, state);
    if (style == "comment") return style;
    if (ctx.align == null) ctx.align = true;
    if ((curPunc == ";" || curPunc == ":") && ctx.type == "statement") popContext(state);
    // Handle indentation for {x -> \n ... }
    else if (curPunc == "->" && ctx.type == "statement" && ctx.prev.type == "}") {
      popContext(state);
      state.context.align = false;
    } else if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "}") {
      while (ctx.type == "statement") ctx = popContext(state);
      if (ctx.type == "}") ctx = popContext(state);
      while (ctx.type == "statement") ctx = popContext(state);
    } else if (curPunc == ctx.type) popContext(state);else if (ctx.type == "}" || ctx.type == "top" || ctx.type == "statement" && curPunc == "newstatement") pushContext(state, stream.column(), "statement");
    state.startOfLine = false;
    state.lastToken = curPunc || style;
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (!state.tokenize[state.tokenize.length - 1].isBase) return null;
    var firstChar = textAfter && textAfter.charAt(0),
      ctx = state.context;
    if (ctx.type == "statement" && !expectExpression(state.lastToken, true)) ctx = ctx.prev;
    var closing = firstChar == ctx.type;
    if (ctx.type == "statement") return ctx.indented + (firstChar == "{" ? 0 : cx.unit);else if (ctx.align) return ctx.column + (closing ? 0 : 1);else return ctx.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    },
    closeBrackets: {
      brackets: ["(", "[", "{", "'", '"', "'''", '"""']
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTA1MC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZ3Jvb3Z5LmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIHdvcmRzKHN0cikge1xuICB2YXIgb2JqID0ge30sXG4gICAgd29yZHMgPSBzdHIuc3BsaXQoXCIgXCIpO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHdvcmRzLmxlbmd0aDsgKytpKSBvYmpbd29yZHNbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIG9iajtcbn1cbnZhciBrZXl3b3JkcyA9IHdvcmRzKFwiYWJzdHJhY3QgYXMgYXNzZXJ0IGJvb2xlYW4gYnJlYWsgYnl0ZSBjYXNlIGNhdGNoIGNoYXIgY2xhc3MgY29uc3QgY29udGludWUgZGVmIGRlZmF1bHQgXCIgKyBcImRvIGRvdWJsZSBlbHNlIGVudW0gZXh0ZW5kcyBmaW5hbCBmaW5hbGx5IGZsb2F0IGZvciBnb3RvIGlmIGltcGxlbWVudHMgaW1wb3J0IGluIFwiICsgXCJpbnN0YW5jZW9mIGludCBpbnRlcmZhY2UgbG9uZyBuYXRpdmUgbmV3IHBhY2thZ2UgcHJpdmF0ZSBwcm90ZWN0ZWQgcHVibGljIHJldHVybiBcIiArIFwic2hvcnQgc3RhdGljIHN0cmljdGZwIHN1cGVyIHN3aXRjaCBzeW5jaHJvbml6ZWQgdGhyZWFkc2FmZSB0aHJvdyB0aHJvd3MgdHJhaXQgdHJhbnNpZW50IFwiICsgXCJ0cnkgdm9pZCB2b2xhdGlsZSB3aGlsZVwiKTtcbnZhciBibG9ja0tleXdvcmRzID0gd29yZHMoXCJjYXRjaCBjbGFzcyBkZWYgZG8gZWxzZSBlbnVtIGZpbmFsbHkgZm9yIGlmIGludGVyZmFjZSBzd2l0Y2ggdHJhaXQgdHJ5IHdoaWxlXCIpO1xudmFyIHN0YW5kYWxvbmVLZXl3b3JkcyA9IHdvcmRzKFwicmV0dXJuIGJyZWFrIGNvbnRpbnVlXCIpO1xudmFyIGF0b21zID0gd29yZHMoXCJudWxsIHRydWUgZmFsc2UgdGhpc1wiKTtcbnZhciBjdXJQdW5jO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGNoID09ICdcIicgfHwgY2ggPT0gXCInXCIpIHtcbiAgICByZXR1cm4gc3RhcnRTdHJpbmcoY2gsIHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmICgvW1xcW1xcXXt9XFwoXFwpLDtcXDpcXC5dLy50ZXN0KGNoKSkge1xuICAgIGN1clB1bmMgPSBjaDtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXC5dLyk7XG4gICAgaWYgKHN0cmVhbS5lYXQoL2VFLykpIHtcbiAgICAgIHN0cmVhbS5lYXQoL1xcK1xcLS8pO1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9cXGQvKTtcbiAgICB9XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgaWYgKGNoID09IFwiL1wiKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCIqXCIpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZS5wdXNoKHRva2VuQ29tbWVudCk7XG4gICAgICByZXR1cm4gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKGV4cGVjdEV4cHJlc3Npb24oc3RhdGUubGFzdFRva2VuLCBmYWxzZSkpIHtcbiAgICAgIHJldHVybiBzdGFydFN0cmluZyhjaCwgc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICB9XG4gIGlmIChjaCA9PSBcIi1cIiAmJiBzdHJlYW0uZWF0KFwiPlwiKSkge1xuICAgIGN1clB1bmMgPSBcIi0+XCI7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKC9bK1xcLSomJT08PiE/fFxcL35dLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvWytcXC0qJiU9PD58fl0vKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF9dLyk7XG4gIGlmIChjaCA9PSBcIkBcIikge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF9cXC5dLyk7XG4gICAgcmV0dXJuIFwibWV0YVwiO1xuICB9XG4gIGlmIChzdGF0ZS5sYXN0VG9rZW4gPT0gXCIuXCIpIHJldHVybiBcInByb3BlcnR5XCI7XG4gIGlmIChzdHJlYW0uZWF0KFwiOlwiKSkge1xuICAgIGN1clB1bmMgPSBcInByb3BsYWJlbFwiO1xuICAgIHJldHVybiBcInByb3BlcnR5XCI7XG4gIH1cbiAgdmFyIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG4gIGlmIChhdG9tcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSB7XG4gICAgcmV0dXJuIFwiYXRvbVwiO1xuICB9XG4gIGlmIChrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSB7XG4gICAgaWYgKGJsb2NrS2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgY3VyUHVuYyA9IFwibmV3c3RhdGVtZW50XCI7ZWxzZSBpZiAoc3RhbmRhbG9uZUtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIGN1clB1bmMgPSBcInN0YW5kYWxvbmVcIjtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cbiAgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cbnRva2VuQmFzZS5pc0Jhc2UgPSB0cnVlO1xuZnVuY3Rpb24gc3RhcnRTdHJpbmcocXVvdGUsIHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIHRyaXBsZVF1b3RlZCA9IGZhbHNlO1xuICBpZiAocXVvdGUgIT0gXCIvXCIgJiYgc3RyZWFtLmVhdChxdW90ZSkpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChxdW90ZSkpIHRyaXBsZVF1b3RlZCA9IHRydWU7ZWxzZSByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfVxuICBmdW5jdGlvbiB0KHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgbmV4dCxcbiAgICAgIGVuZCA9ICF0cmlwbGVRdW90ZWQ7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgaWYgKCF0cmlwbGVRdW90ZWQpIHtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKHF1b3RlICsgcXVvdGUpKSB7XG4gICAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgaWYgKHF1b3RlID09ICdcIicgJiYgbmV4dCA9PSBcIiRcIiAmJiAhZXNjYXBlZCkge1xuICAgICAgICBpZiAoc3RyZWFtLmVhdChcIntcIikpIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZS5wdXNoKHRva2VuQmFzZVVudGlsQnJhY2UoKSk7XG4gICAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eXFx3LywgZmFsc2UpKSB7XG4gICAgICAgICAgc3RhdGUudG9rZW5pemUucHVzaCh0b2tlblZhcmlhYmxlRGVyZWYpO1xuICAgICAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKGVuZCkgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH1cbiAgc3RhdGUudG9rZW5pemUucHVzaCh0KTtcbiAgcmV0dXJuIHQoc3RyZWFtLCBzdGF0ZSk7XG59XG5mdW5jdGlvbiB0b2tlbkJhc2VVbnRpbEJyYWNlKCkge1xuICB2YXIgZGVwdGggPSAxO1xuICBmdW5jdGlvbiB0KHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PSBcIn1cIikge1xuICAgICAgZGVwdGgtLTtcbiAgICAgIGlmIChkZXB0aCA9PSAwKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplLnBvcCgpO1xuICAgICAgICByZXR1cm4gc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0oc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgfSBlbHNlIGlmIChzdHJlYW0ucGVlaygpID09IFwie1wiKSB7XG4gICAgICBkZXB0aCsrO1xuICAgIH1cbiAgICByZXR1cm4gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIHQuaXNCYXNlID0gdHJ1ZTtcbiAgcmV0dXJuIHQ7XG59XG5mdW5jdGlvbiB0b2tlblZhcmlhYmxlRGVyZWYoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbmV4dCA9IHN0cmVhbS5tYXRjaCgvXihcXC58W1xcd1xcJF9dKykvKTtcbiAgaWYgKCFuZXh0IHx8ICFzdHJlYW0ubWF0Y2gobmV4dFswXSA9PSBcIi5cIiA/IC9eW1xcdyRfXS8gOiAvXlxcLi8pKSBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgaWYgKCFuZXh0KSByZXR1cm4gc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0oc3RyZWFtLCBzdGF0ZSk7XG4gIHJldHVybiBuZXh0WzBdID09IFwiLlwiID8gbnVsbCA6IFwidmFyaWFibGVcIjtcbn1cbmZ1bmN0aW9uIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiL1wiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cbmZ1bmN0aW9uIGV4cGVjdEV4cHJlc3Npb24obGFzdCwgbmV3bGluZSkge1xuICByZXR1cm4gIWxhc3QgfHwgbGFzdCA9PSBcIm9wZXJhdG9yXCIgfHwgbGFzdCA9PSBcIi0+XCIgfHwgL1tcXC5cXFtcXHtcXCgsOzpdLy50ZXN0KGxhc3QpIHx8IGxhc3QgPT0gXCJuZXdzdGF0ZW1lbnRcIiB8fCBsYXN0ID09IFwia2V5d29yZFwiIHx8IGxhc3QgPT0gXCJwcm9wbGFiZWxcIiB8fCBsYXN0ID09IFwic3RhbmRhbG9uZVwiICYmICFuZXdsaW5lO1xufVxuZnVuY3Rpb24gQ29udGV4dChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBhbGlnbiwgcHJldikge1xuICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMucHJldiA9IHByZXY7XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlKSB7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoc3RhdGUuaW5kZW50ZWQsIGNvbCwgdHlwZSwgbnVsbCwgc3RhdGUuY29udGV4dCk7XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KHN0YXRlKSB7XG4gIHZhciB0ID0gc3RhdGUuY29udGV4dC50eXBlO1xuICBpZiAodCA9PSBcIilcIiB8fCB0ID09IFwiXVwiIHx8IHQgPT0gXCJ9XCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG59XG5cbi8vIEludGVyZmFjZVxuXG5leHBvcnQgY29uc3QgZ3Jvb3Z5ID0ge1xuICBuYW1lOiBcImdyb292eVwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogW3Rva2VuQmFzZV0sXG4gICAgICBjb250ZXh0OiBuZXcgQ29udGV4dCgtaW5kZW50VW5pdCwgMCwgXCJ0b3BcIiwgZmFsc2UpLFxuICAgICAgaW5kZW50ZWQ6IDAsXG4gICAgICBzdGFydE9mTGluZTogdHJ1ZSxcbiAgICAgIGxhc3RUb2tlbjogbnVsbFxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0O1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gZmFsc2U7XG4gICAgICBzdGF0ZS5pbmRlbnRlZCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgICAgLy8gQXV0b21hdGljIHNlbWljb2xvbiBpbnNlcnRpb25cbiAgICAgIGlmIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmICFleHBlY3RFeHByZXNzaW9uKHN0YXRlLmxhc3RUb2tlbiwgdHJ1ZSkpIHtcbiAgICAgICAgcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICAgIGN0eCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgY3VyUHVuYyA9IG51bGw7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0oc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0eWxlID09IFwiY29tbWVudFwiKSByZXR1cm4gc3R5bGU7XG4gICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSB0cnVlO1xuICAgIGlmICgoY3VyUHVuYyA9PSBcIjtcIiB8fCBjdXJQdW5jID09IFwiOlwiKSAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAvLyBIYW5kbGUgaW5kZW50YXRpb24gZm9yIHt4IC0+IFxcbiAuLi4gfVxuICAgIGVsc2UgaWYgKGN1clB1bmMgPT0gXCItPlwiICYmIGN0eC50eXBlID09IFwic3RhdGVtZW50XCIgJiYgY3R4LnByZXYudHlwZSA9PSBcIn1cIikge1xuICAgICAgcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICBzdGF0ZS5jb250ZXh0LmFsaWduID0gZmFsc2U7XG4gICAgfSBlbHNlIGlmIChjdXJQdW5jID09IFwie1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIn1cIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIltcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJdXCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCIoXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiKVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwifVwiKSB7XG4gICAgICB3aGlsZSAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICBpZiAoY3R4LnR5cGUgPT0gXCJ9XCIpIGN0eCA9IHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgd2hpbGUgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIGN0eCA9IHBvcENvbnRleHQoc3RhdGUpO1xuICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBjdHgudHlwZSkgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoY3R4LnR5cGUgPT0gXCJ9XCIgfHwgY3R4LnR5cGUgPT0gXCJ0b3BcIiB8fCBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmIGN1clB1bmMgPT0gXCJuZXdzdGF0ZW1lbnRcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJzdGF0ZW1lbnRcIik7XG4gICAgc3RhdGUuc3RhcnRPZkxpbmUgPSBmYWxzZTtcbiAgICBzdGF0ZS5sYXN0VG9rZW4gPSBjdXJQdW5jIHx8IHN0eWxlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICBpZiAoIXN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdLmlzQmFzZSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIGZpcnN0Q2hhciA9IHRleHRBZnRlciAmJiB0ZXh0QWZ0ZXIuY2hhckF0KDApLFxuICAgICAgY3R4ID0gc3RhdGUuY29udGV4dDtcbiAgICBpZiAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIiAmJiAhZXhwZWN0RXhwcmVzc2lvbihzdGF0ZS5sYXN0VG9rZW4sIHRydWUpKSBjdHggPSBjdHgucHJldjtcbiAgICB2YXIgY2xvc2luZyA9IGZpcnN0Q2hhciA9PSBjdHgudHlwZTtcbiAgICBpZiAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChmaXJzdENoYXIgPT0gXCJ7XCIgPyAwIDogY3gudW5pdCk7ZWxzZSBpZiAoY3R4LmFsaWduKSByZXR1cm4gY3R4LmNvbHVtbiArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChjbG9zaW5nID8gMCA6IGN4LnVuaXQpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypbe31dJC8sXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIvL1wiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICB9XG4gICAgfSxcbiAgICBjbG9zZUJyYWNrZXRzOiB7XG4gICAgICBicmFja2V0czogW1wiKFwiLCBcIltcIiwgXCJ7XCIsIFwiJ1wiLCAnXCInLCBcIicnJ1wiLCAnXCJcIlwiJ11cbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==