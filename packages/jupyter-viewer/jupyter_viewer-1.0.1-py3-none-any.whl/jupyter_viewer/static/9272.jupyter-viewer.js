"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9272],{

/***/ 19272
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ruby: () => (/* binding */ ruby)
/* harmony export */ });
function wordObj(words) {
  var o = {};
  for (var i = 0, e = words.length; i < e; ++i) o[words[i]] = true;
  return o;
}
var keywordList = ["alias", "and", "BEGIN", "begin", "break", "case", "class", "def", "defined?", "do", "else", "elsif", "END", "end", "ensure", "false", "for", "if", "in", "module", "next", "not", "or", "redo", "rescue", "retry", "return", "self", "super", "then", "true", "undef", "unless", "until", "when", "while", "yield", "nil", "raise", "throw", "catch", "fail", "loop", "callcc", "caller", "lambda", "proc", "public", "protected", "private", "require", "load", "require_relative", "extend", "autoload", "__END__", "__FILE__", "__LINE__", "__dir__"],
  keywords = wordObj(keywordList);
var indentWords = wordObj(["def", "class", "case", "for", "while", "until", "module", "catch", "loop", "proc", "begin"]);
var dedentWords = wordObj(["end", "until"]);
var opening = {
  "[": "]",
  "{": "}",
  "(": ")"
};
var closing = {
  "]": "[",
  "}": "{",
  ")": "("
};
var curPunc;
function chain(newtok, stream, state) {
  state.tokenize.push(newtok);
  return newtok(stream, state);
}
function tokenBase(stream, state) {
  if (stream.sol() && stream.match("=begin") && stream.eol()) {
    state.tokenize.push(readBlockComment);
    return "comment";
  }
  if (stream.eatSpace()) return null;
  var ch = stream.next(),
    m;
  if (ch == "`" || ch == "'" || ch == '"') {
    return chain(readQuoted(ch, "string", ch == '"' || ch == "`"), stream, state);
  } else if (ch == "/") {
    if (regexpAhead(stream)) return chain(readQuoted(ch, "string.special", true), stream, state);else return "operator";
  } else if (ch == "%") {
    var style = "string",
      embed = true;
    if (stream.eat("s")) style = "atom";else if (stream.eat(/[WQ]/)) style = "string";else if (stream.eat(/[r]/)) style = "string.special";else if (stream.eat(/[wxq]/)) {
      style = "string";
      embed = false;
    }
    var delim = stream.eat(/[^\w\s=]/);
    if (!delim) return "operator";
    if (opening.propertyIsEnumerable(delim)) delim = opening[delim];
    return chain(readQuoted(delim, style, embed, true), stream, state);
  } else if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  } else if (ch == "<" && (m = stream.match(/^<([-~])[\`\"\']?([a-zA-Z_?]\w*)[\`\"\']?(?:;|$)/))) {
    return chain(readHereDoc(m[2], m[1]), stream, state);
  } else if (ch == "0") {
    if (stream.eat("x")) stream.eatWhile(/[\da-fA-F]/);else if (stream.eat("b")) stream.eatWhile(/[01]/);else stream.eatWhile(/[0-7]/);
    return "number";
  } else if (/\d/.test(ch)) {
    stream.match(/^[\d_]*(?:\.[\d_]+)?(?:[eE][+\-]?[\d_]+)?/);
    return "number";
  } else if (ch == "?") {
    while (stream.match(/^\\[CM]-/)) {}
    if (stream.eat("\\")) stream.eatWhile(/\w/);else stream.next();
    return "string";
  } else if (ch == ":") {
    if (stream.eat("'")) return chain(readQuoted("'", "atom", false), stream, state);
    if (stream.eat('"')) return chain(readQuoted('"', "atom", true), stream, state);

    // :> :>> :< :<< are valid symbols
    if (stream.eat(/[\<\>]/)) {
      stream.eat(/[\<\>]/);
      return "atom";
    }

    // :+ :- :/ :* :| :& :! are valid symbols
    if (stream.eat(/[\+\-\*\/\&\|\:\!]/)) {
      return "atom";
    }

    // Symbols can't start by a digit
    if (stream.eat(/[a-zA-Z$@_\xa1-\uffff]/)) {
      stream.eatWhile(/[\w$\xa1-\uffff]/);
      // Only one ? ! = is allowed and only as the last character
      stream.eat(/[\?\!\=]/);
      return "atom";
    }
    return "operator";
  } else if (ch == "@" && stream.match(/^@?[a-zA-Z_\xa1-\uffff]/)) {
    stream.eat("@");
    stream.eatWhile(/[\w\xa1-\uffff]/);
    return "propertyName";
  } else if (ch == "$") {
    if (stream.eat(/[a-zA-Z_]/)) {
      stream.eatWhile(/[\w]/);
    } else if (stream.eat(/\d/)) {
      stream.eat(/\d/);
    } else {
      stream.next(); // Must be a special global like $: or $!
    }
    return "variableName.special";
  } else if (/[a-zA-Z_\xa1-\uffff]/.test(ch)) {
    stream.eatWhile(/[\w\xa1-\uffff]/);
    stream.eat(/[\?\!]/);
    if (stream.eat(":")) return "atom";
    return "variable";
  } else if (ch == "|" && (state.varList || state.lastTok == "{" || state.lastTok == "do")) {
    curPunc = "|";
    return null;
  } else if (/[\(\)\[\]{}\\;]/.test(ch)) {
    curPunc = ch;
    return null;
  } else if (ch == "-" && stream.eat(">")) {
    return "operator";
  } else if (/[=+\-\/*:\.^%<>~|]/.test(ch)) {
    var more = stream.eatWhile(/[=+\-\/*:\.^%<>~|]/);
    if (ch == "." && !more) curPunc = ".";
    return "operator";
  } else {
    return null;
  }
}
function regexpAhead(stream) {
  var start = stream.pos,
    depth = 0,
    next,
    found = false,
    escaped = false;
  while ((next = stream.next()) != null) {
    if (!escaped) {
      if ("[{(".indexOf(next) > -1) {
        depth++;
      } else if ("]})".indexOf(next) > -1) {
        depth--;
        if (depth < 0) break;
      } else if (next == "/" && depth == 0) {
        found = true;
        break;
      }
      escaped = next == "\\";
    } else {
      escaped = false;
    }
  }
  stream.backUp(stream.pos - start);
  return found;
}
function tokenBaseUntilBrace(depth) {
  if (!depth) depth = 1;
  return function (stream, state) {
    if (stream.peek() == "}") {
      if (depth == 1) {
        state.tokenize.pop();
        return state.tokenize[state.tokenize.length - 1](stream, state);
      } else {
        state.tokenize[state.tokenize.length - 1] = tokenBaseUntilBrace(depth - 1);
      }
    } else if (stream.peek() == "{") {
      state.tokenize[state.tokenize.length - 1] = tokenBaseUntilBrace(depth + 1);
    }
    return tokenBase(stream, state);
  };
}
function tokenBaseOnce() {
  var alreadyCalled = false;
  return function (stream, state) {
    if (alreadyCalled) {
      state.tokenize.pop();
      return state.tokenize[state.tokenize.length - 1](stream, state);
    }
    alreadyCalled = true;
    return tokenBase(stream, state);
  };
}
function readQuoted(quote, style, embed, unescaped) {
  return function (stream, state) {
    var escaped = false,
      ch;
    if (state.context.type === 'read-quoted-paused') {
      state.context = state.context.prev;
      stream.eat("}");
    }
    while ((ch = stream.next()) != null) {
      if (ch == quote && (unescaped || !escaped)) {
        state.tokenize.pop();
        break;
      }
      if (embed && ch == "#" && !escaped) {
        if (stream.eat("{")) {
          if (quote == "}") {
            state.context = {
              prev: state.context,
              type: 'read-quoted-paused'
            };
          }
          state.tokenize.push(tokenBaseUntilBrace());
          break;
        } else if (/[@\$]/.test(stream.peek())) {
          state.tokenize.push(tokenBaseOnce());
          break;
        }
      }
      escaped = !escaped && ch == "\\";
    }
    return style;
  };
}
function readHereDoc(phrase, mayIndent) {
  return function (stream, state) {
    if (mayIndent) stream.eatSpace();
    if (stream.match(phrase)) state.tokenize.pop();else stream.skipToEnd();
    return "string";
  };
}
function readBlockComment(stream, state) {
  if (stream.sol() && stream.match("=end") && stream.eol()) state.tokenize.pop();
  stream.skipToEnd();
  return "comment";
}
const ruby = {
  name: "ruby",
  startState: function (indentUnit) {
    return {
      tokenize: [tokenBase],
      indented: 0,
      context: {
        type: "top",
        indented: -indentUnit
      },
      continuedLine: false,
      lastTok: null,
      varList: false
    };
  },
  token: function (stream, state) {
    curPunc = null;
    if (stream.sol()) state.indented = stream.indentation();
    var style = state.tokenize[state.tokenize.length - 1](stream, state),
      kwtype;
    var thisTok = curPunc;
    if (style == "variable") {
      var word = stream.current();
      style = state.lastTok == "." ? "property" : keywords.propertyIsEnumerable(stream.current()) ? "keyword" : /^[A-Z]/.test(word) ? "tag" : state.lastTok == "def" || state.lastTok == "class" || state.varList ? "def" : "variable";
      if (style == "keyword") {
        thisTok = word;
        if (indentWords.propertyIsEnumerable(word)) kwtype = "indent";else if (dedentWords.propertyIsEnumerable(word)) kwtype = "dedent";else if ((word == "if" || word == "unless") && stream.column() == stream.indentation()) kwtype = "indent";else if (word == "do" && state.context.indented < state.indented) kwtype = "indent";
      }
    }
    if (curPunc || style && style != "comment") state.lastTok = thisTok;
    if (curPunc == "|") state.varList = !state.varList;
    if (kwtype == "indent" || /[\(\[\{]/.test(curPunc)) state.context = {
      prev: state.context,
      type: curPunc || style,
      indented: state.indented
    };else if ((kwtype == "dedent" || /[\)\]\}]/.test(curPunc)) && state.context.prev) state.context = state.context.prev;
    if (stream.eol()) state.continuedLine = curPunc == "\\" || style == "operator";
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize[state.tokenize.length - 1] != tokenBase) return null;
    var firstChar = textAfter && textAfter.charAt(0);
    var ct = state.context;
    var closed = ct.type == closing[firstChar] || ct.type == "keyword" && /^(?:end|until|else|elsif|when|rescue)\b/.test(textAfter);
    return ct.indented + (closed ? 0 : cx.unit) + (state.continuedLine ? cx.unit : 0);
  },
  languageData: {
    indentOnInput: /^\s*(?:end|rescue|elsif|else|\})$/,
    commentTokens: {
      line: "#"
    },
    autocomplete: keywordList
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTI3Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3J1YnkuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZE9iaih3b3Jkcykge1xuICB2YXIgbyA9IHt9O1xuICBmb3IgKHZhciBpID0gMCwgZSA9IHdvcmRzLmxlbmd0aDsgaSA8IGU7ICsraSkgb1t3b3Jkc1tpXV0gPSB0cnVlO1xuICByZXR1cm4gbztcbn1cbnZhciBrZXl3b3JkTGlzdCA9IFtcImFsaWFzXCIsIFwiYW5kXCIsIFwiQkVHSU5cIiwgXCJiZWdpblwiLCBcImJyZWFrXCIsIFwiY2FzZVwiLCBcImNsYXNzXCIsIFwiZGVmXCIsIFwiZGVmaW5lZD9cIiwgXCJkb1wiLCBcImVsc2VcIiwgXCJlbHNpZlwiLCBcIkVORFwiLCBcImVuZFwiLCBcImVuc3VyZVwiLCBcImZhbHNlXCIsIFwiZm9yXCIsIFwiaWZcIiwgXCJpblwiLCBcIm1vZHVsZVwiLCBcIm5leHRcIiwgXCJub3RcIiwgXCJvclwiLCBcInJlZG9cIiwgXCJyZXNjdWVcIiwgXCJyZXRyeVwiLCBcInJldHVyblwiLCBcInNlbGZcIiwgXCJzdXBlclwiLCBcInRoZW5cIiwgXCJ0cnVlXCIsIFwidW5kZWZcIiwgXCJ1bmxlc3NcIiwgXCJ1bnRpbFwiLCBcIndoZW5cIiwgXCJ3aGlsZVwiLCBcInlpZWxkXCIsIFwibmlsXCIsIFwicmFpc2VcIiwgXCJ0aHJvd1wiLCBcImNhdGNoXCIsIFwiZmFpbFwiLCBcImxvb3BcIiwgXCJjYWxsY2NcIiwgXCJjYWxsZXJcIiwgXCJsYW1iZGFcIiwgXCJwcm9jXCIsIFwicHVibGljXCIsIFwicHJvdGVjdGVkXCIsIFwicHJpdmF0ZVwiLCBcInJlcXVpcmVcIiwgXCJsb2FkXCIsIFwicmVxdWlyZV9yZWxhdGl2ZVwiLCBcImV4dGVuZFwiLCBcImF1dG9sb2FkXCIsIFwiX19FTkRfX1wiLCBcIl9fRklMRV9fXCIsIFwiX19MSU5FX19cIiwgXCJfX2Rpcl9fXCJdLFxuICBrZXl3b3JkcyA9IHdvcmRPYmooa2V5d29yZExpc3QpO1xudmFyIGluZGVudFdvcmRzID0gd29yZE9iaihbXCJkZWZcIiwgXCJjbGFzc1wiLCBcImNhc2VcIiwgXCJmb3JcIiwgXCJ3aGlsZVwiLCBcInVudGlsXCIsIFwibW9kdWxlXCIsIFwiY2F0Y2hcIiwgXCJsb29wXCIsIFwicHJvY1wiLCBcImJlZ2luXCJdKTtcbnZhciBkZWRlbnRXb3JkcyA9IHdvcmRPYmooW1wiZW5kXCIsIFwidW50aWxcIl0pO1xudmFyIG9wZW5pbmcgPSB7XG4gIFwiW1wiOiBcIl1cIixcbiAgXCJ7XCI6IFwifVwiLFxuICBcIihcIjogXCIpXCJcbn07XG52YXIgY2xvc2luZyA9IHtcbiAgXCJdXCI6IFwiW1wiLFxuICBcIn1cIjogXCJ7XCIsXG4gIFwiKVwiOiBcIihcIlxufTtcbnZhciBjdXJQdW5jO1xuZnVuY3Rpb24gY2hhaW4obmV3dG9rLCBzdHJlYW0sIHN0YXRlKSB7XG4gIHN0YXRlLnRva2VuaXplLnB1c2gobmV3dG9rKTtcbiAgcmV0dXJuIG5ld3RvayhzdHJlYW0sIHN0YXRlKTtcbn1cbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uc29sKCkgJiYgc3RyZWFtLm1hdGNoKFwiPWJlZ2luXCIpICYmIHN0cmVhbS5lb2woKSkge1xuICAgIHN0YXRlLnRva2VuaXplLnB1c2gocmVhZEJsb2NrQ29tbWVudCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCksXG4gICAgbTtcbiAgaWYgKGNoID09IFwiYFwiIHx8IGNoID09IFwiJ1wiIHx8IGNoID09ICdcIicpIHtcbiAgICByZXR1cm4gY2hhaW4ocmVhZFF1b3RlZChjaCwgXCJzdHJpbmdcIiwgY2ggPT0gJ1wiJyB8fCBjaCA9PSBcImBcIiksIHN0cmVhbSwgc3RhdGUpO1xuICB9IGVsc2UgaWYgKGNoID09IFwiL1wiKSB7XG4gICAgaWYgKHJlZ2V4cEFoZWFkKHN0cmVhbSkpIHJldHVybiBjaGFpbihyZWFkUXVvdGVkKGNoLCBcInN0cmluZy5zcGVjaWFsXCIsIHRydWUpLCBzdHJlYW0sIHN0YXRlKTtlbHNlIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIlXCIpIHtcbiAgICB2YXIgc3R5bGUgPSBcInN0cmluZ1wiLFxuICAgICAgZW1iZWQgPSB0cnVlO1xuICAgIGlmIChzdHJlYW0uZWF0KFwic1wiKSkgc3R5bGUgPSBcImF0b21cIjtlbHNlIGlmIChzdHJlYW0uZWF0KC9bV1FdLykpIHN0eWxlID0gXCJzdHJpbmdcIjtlbHNlIGlmIChzdHJlYW0uZWF0KC9bcl0vKSkgc3R5bGUgPSBcInN0cmluZy5zcGVjaWFsXCI7ZWxzZSBpZiAoc3RyZWFtLmVhdCgvW3d4cV0vKSkge1xuICAgICAgc3R5bGUgPSBcInN0cmluZ1wiO1xuICAgICAgZW1iZWQgPSBmYWxzZTtcbiAgICB9XG4gICAgdmFyIGRlbGltID0gc3RyZWFtLmVhdCgvW15cXHdcXHM9XS8pO1xuICAgIGlmICghZGVsaW0pIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgaWYgKG9wZW5pbmcucHJvcGVydHlJc0VudW1lcmFibGUoZGVsaW0pKSBkZWxpbSA9IG9wZW5pbmdbZGVsaW1dO1xuICAgIHJldHVybiBjaGFpbihyZWFkUXVvdGVkKGRlbGltLCBzdHlsZSwgZW1iZWQsIHRydWUpLCBzdHJlYW0sIHN0YXRlKTtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIiNcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI8XCIgJiYgKG0gPSBzdHJlYW0ubWF0Y2goL148KFstfl0pW1xcYFxcXCJcXCddPyhbYS16QS1aXz9dXFx3KilbXFxgXFxcIlxcJ10/KD86O3wkKS8pKSkge1xuICAgIHJldHVybiBjaGFpbihyZWFkSGVyZURvYyhtWzJdLCBtWzFdKSwgc3RyZWFtLCBzdGF0ZSk7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIwXCIpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChcInhcIikpIHN0cmVhbS5lYXRXaGlsZSgvW1xcZGEtZkEtRl0vKTtlbHNlIGlmIChzdHJlYW0uZWF0KFwiYlwiKSkgc3RyZWFtLmVhdFdoaWxlKC9bMDFdLyk7ZWxzZSBzdHJlYW0uZWF0V2hpbGUoL1swLTddLyk7XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH0gZWxzZSBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0ubWF0Y2goL15bXFxkX10qKD86XFwuW1xcZF9dKyk/KD86W2VFXVsrXFwtXT9bXFxkX10rKT8vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIj9cIikge1xuICAgIHdoaWxlIChzdHJlYW0ubWF0Y2goL15cXFxcW0NNXS0vKSkge31cbiAgICBpZiAoc3RyZWFtLmVhdChcIlxcXFxcIikpIHN0cmVhbS5lYXRXaGlsZSgvXFx3Lyk7ZWxzZSBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiOlwiKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCInXCIpKSByZXR1cm4gY2hhaW4ocmVhZFF1b3RlZChcIidcIiwgXCJhdG9tXCIsIGZhbHNlKSwgc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0cmVhbS5lYXQoJ1wiJykpIHJldHVybiBjaGFpbihyZWFkUXVvdGVkKCdcIicsIFwiYXRvbVwiLCB0cnVlKSwgc3RyZWFtLCBzdGF0ZSk7XG5cbiAgICAvLyA6PiA6Pj4gOjwgOjw8IGFyZSB2YWxpZCBzeW1ib2xzXG4gICAgaWYgKHN0cmVhbS5lYXQoL1tcXDxcXD5dLykpIHtcbiAgICAgIHN0cmVhbS5lYXQoL1tcXDxcXD5dLyk7XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgfVxuXG4gICAgLy8gOisgOi0gOi8gOiogOnwgOiYgOiEgYXJlIHZhbGlkIHN5bWJvbHNcbiAgICBpZiAoc3RyZWFtLmVhdCgvW1xcK1xcLVxcKlxcL1xcJlxcfFxcOlxcIV0vKSkge1xuICAgICAgcmV0dXJuIFwiYXRvbVwiO1xuICAgIH1cblxuICAgIC8vIFN5bWJvbHMgY2FuJ3Qgc3RhcnQgYnkgYSBkaWdpdFxuICAgIGlmIChzdHJlYW0uZWF0KC9bYS16QS1aJEBfXFx4YTEtXFx1ZmZmZl0vKSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3JFxceGExLVxcdWZmZmZdLyk7XG4gICAgICAvLyBPbmx5IG9uZSA/ICEgPSBpcyBhbGxvd2VkIGFuZCBvbmx5IGFzIHRoZSBsYXN0IGNoYXJhY3RlclxuICAgICAgc3RyZWFtLmVhdCgvW1xcP1xcIVxcPV0vKTtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIkBcIiAmJiBzdHJlYW0ubWF0Y2goL15AP1thLXpBLVpfXFx4YTEtXFx1ZmZmZl0vKSkge1xuICAgIHN0cmVhbS5lYXQoXCJAXCIpO1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xceGExLVxcdWZmZmZdLyk7XG4gICAgcmV0dXJuIFwicHJvcGVydHlOYW1lXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIkXCIpIHtcbiAgICBpZiAoc3RyZWFtLmVhdCgvW2EtekEtWl9dLykpIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd10vKTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXQoL1xcZC8pKSB7XG4gICAgICBzdHJlYW0uZWF0KC9cXGQvKTtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLm5leHQoKTsgLy8gTXVzdCBiZSBhIHNwZWNpYWwgZ2xvYmFsIGxpa2UgJDogb3IgJCFcbiAgICB9XG4gICAgcmV0dXJuIFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgfSBlbHNlIGlmICgvW2EtekEtWl9cXHhhMS1cXHVmZmZmXS8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXHhhMS1cXHVmZmZmXS8pO1xuICAgIHN0cmVhbS5lYXQoL1tcXD9cXCFdLyk7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCI6XCIpKSByZXR1cm4gXCJhdG9tXCI7XG4gICAgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcInxcIiAmJiAoc3RhdGUudmFyTGlzdCB8fCBzdGF0ZS5sYXN0VG9rID09IFwie1wiIHx8IHN0YXRlLmxhc3RUb2sgPT0gXCJkb1wiKSkge1xuICAgIGN1clB1bmMgPSBcInxcIjtcbiAgICByZXR1cm4gbnVsbDtcbiAgfSBlbHNlIGlmICgvW1xcKFxcKVxcW1xcXXt9XFxcXDtdLy50ZXN0KGNoKSkge1xuICAgIGN1clB1bmMgPSBjaDtcbiAgICByZXR1cm4gbnVsbDtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIi1cIiAmJiBzdHJlYW0uZWF0KFwiPlwiKSkge1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH0gZWxzZSBpZiAoL1s9K1xcLVxcLyo6XFwuXiU8Pn58XS8udGVzdChjaCkpIHtcbiAgICB2YXIgbW9yZSA9IHN0cmVhbS5lYXRXaGlsZSgvWz0rXFwtXFwvKjpcXC5eJTw+fnxdLyk7XG4gICAgaWYgKGNoID09IFwiLlwiICYmICFtb3JlKSBjdXJQdW5jID0gXCIuXCI7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfSBlbHNlIHtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxufVxuZnVuY3Rpb24gcmVnZXhwQWhlYWQoc3RyZWFtKSB7XG4gIHZhciBzdGFydCA9IHN0cmVhbS5wb3MsXG4gICAgZGVwdGggPSAwLFxuICAgIG5leHQsXG4gICAgZm91bmQgPSBmYWxzZSxcbiAgICBlc2NhcGVkID0gZmFsc2U7XG4gIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAoIWVzY2FwZWQpIHtcbiAgICAgIGlmIChcIlt7KFwiLmluZGV4T2YobmV4dCkgPiAtMSkge1xuICAgICAgICBkZXB0aCsrO1xuICAgICAgfSBlbHNlIGlmIChcIl19KVwiLmluZGV4T2YobmV4dCkgPiAtMSkge1xuICAgICAgICBkZXB0aC0tO1xuICAgICAgICBpZiAoZGVwdGggPCAwKSBicmVhaztcbiAgICAgIH0gZWxzZSBpZiAobmV4dCA9PSBcIi9cIiAmJiBkZXB0aCA9PSAwKSB7XG4gICAgICAgIGZvdW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9IGVsc2Uge1xuICAgICAgZXNjYXBlZCA9IGZhbHNlO1xuICAgIH1cbiAgfVxuICBzdHJlYW0uYmFja1VwKHN0cmVhbS5wb3MgLSBzdGFydCk7XG4gIHJldHVybiBmb3VuZDtcbn1cbmZ1bmN0aW9uIHRva2VuQmFzZVVudGlsQnJhY2UoZGVwdGgpIHtcbiAgaWYgKCFkZXB0aCkgZGVwdGggPSAxO1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PSBcIn1cIikge1xuICAgICAgaWYgKGRlcHRoID09IDEpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gICAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZVtzdGF0ZS50b2tlbml6ZS5sZW5ndGggLSAxXShzdHJlYW0sIHN0YXRlKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdID0gdG9rZW5CYXNlVW50aWxCcmFjZShkZXB0aCAtIDEpO1xuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PSBcIntcIikge1xuICAgICAgc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0gPSB0b2tlbkJhc2VVbnRpbEJyYWNlKGRlcHRoICsgMSk7XG4gICAgfVxuICAgIHJldHVybiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSk7XG4gIH07XG59XG5mdW5jdGlvbiB0b2tlbkJhc2VPbmNlKCkge1xuICB2YXIgYWxyZWFkeUNhbGxlZCA9IGZhbHNlO1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoYWxyZWFkeUNhbGxlZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0oc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICAgIGFscmVhZHlDYWxsZWQgPSB0cnVlO1xuICAgIHJldHVybiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSk7XG4gIH07XG59XG5mdW5jdGlvbiByZWFkUXVvdGVkKHF1b3RlLCBzdHlsZSwgZW1iZWQsIHVuZXNjYXBlZCkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgY2g7XG4gICAgaWYgKHN0YXRlLmNvbnRleHQudHlwZSA9PT0gJ3JlYWQtcXVvdGVkLXBhdXNlZCcpIHtcbiAgICAgIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG4gICAgICBzdHJlYW0uZWF0KFwifVwiKTtcbiAgICB9XG4gICAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmIChjaCA9PSBxdW90ZSAmJiAodW5lc2NhcGVkIHx8ICFlc2NhcGVkKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBpZiAoZW1iZWQgJiYgY2ggPT0gXCIjXCIgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgaWYgKHN0cmVhbS5lYXQoXCJ7XCIpKSB7XG4gICAgICAgICAgaWYgKHF1b3RlID09IFwifVwiKSB7XG4gICAgICAgICAgICBzdGF0ZS5jb250ZXh0ID0ge1xuICAgICAgICAgICAgICBwcmV2OiBzdGF0ZS5jb250ZXh0LFxuICAgICAgICAgICAgICB0eXBlOiAncmVhZC1xdW90ZWQtcGF1c2VkJ1xuICAgICAgICAgICAgfTtcbiAgICAgICAgICB9XG4gICAgICAgICAgc3RhdGUudG9rZW5pemUucHVzaCh0b2tlbkJhc2VVbnRpbEJyYWNlKCkpO1xuICAgICAgICAgIGJyZWFrO1xuICAgICAgICB9IGVsc2UgaWYgKC9bQFxcJF0vLnRlc3Qoc3RyZWFtLnBlZWsoKSkpIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZS5wdXNoKHRva2VuQmFzZU9uY2UoKSk7XG4gICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBjaCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9O1xufVxuZnVuY3Rpb24gcmVhZEhlcmVEb2MocGhyYXNlLCBtYXlJbmRlbnQpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKG1heUluZGVudCkgc3RyZWFtLmVhdFNwYWNlKCk7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChwaHJhc2UpKSBzdGF0ZS50b2tlbml6ZS5wb3AoKTtlbHNlIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfTtcbn1cbmZ1bmN0aW9uIHJlYWRCbG9ja0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLnNvbCgpICYmIHN0cmVhbS5tYXRjaChcIj1lbmRcIikgJiYgc3RyZWFtLmVvbCgpKSBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5leHBvcnQgY29uc3QgcnVieSA9IHtcbiAgbmFtZTogXCJydWJ5XCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uIChpbmRlbnRVbml0KSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBbdG9rZW5CYXNlXSxcbiAgICAgIGluZGVudGVkOiAwLFxuICAgICAgY29udGV4dDoge1xuICAgICAgICB0eXBlOiBcInRvcFwiLFxuICAgICAgICBpbmRlbnRlZDogLWluZGVudFVuaXRcbiAgICAgIH0sXG4gICAgICBjb250aW51ZWRMaW5lOiBmYWxzZSxcbiAgICAgIGxhc3RUb2s6IG51bGwsXG4gICAgICB2YXJMaXN0OiBmYWxzZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGN1clB1bmMgPSBudWxsO1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHN0YXRlLmluZGVudGVkID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0oc3RyZWFtLCBzdGF0ZSksXG4gICAgICBrd3R5cGU7XG4gICAgdmFyIHRoaXNUb2sgPSBjdXJQdW5jO1xuICAgIGlmIChzdHlsZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICAgIHN0eWxlID0gc3RhdGUubGFzdFRvayA9PSBcIi5cIiA/IFwicHJvcGVydHlcIiA6IGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHN0cmVhbS5jdXJyZW50KCkpID8gXCJrZXl3b3JkXCIgOiAvXltBLVpdLy50ZXN0KHdvcmQpID8gXCJ0YWdcIiA6IHN0YXRlLmxhc3RUb2sgPT0gXCJkZWZcIiB8fCBzdGF0ZS5sYXN0VG9rID09IFwiY2xhc3NcIiB8fCBzdGF0ZS52YXJMaXN0ID8gXCJkZWZcIiA6IFwidmFyaWFibGVcIjtcbiAgICAgIGlmIChzdHlsZSA9PSBcImtleXdvcmRcIikge1xuICAgICAgICB0aGlzVG9rID0gd29yZDtcbiAgICAgICAgaWYgKGluZGVudFdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHdvcmQpKSBrd3R5cGUgPSBcImluZGVudFwiO2Vsc2UgaWYgKGRlZGVudFdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHdvcmQpKSBrd3R5cGUgPSBcImRlZGVudFwiO2Vsc2UgaWYgKCh3b3JkID09IFwiaWZcIiB8fCB3b3JkID09IFwidW5sZXNzXCIpICYmIHN0cmVhbS5jb2x1bW4oKSA9PSBzdHJlYW0uaW5kZW50YXRpb24oKSkga3d0eXBlID0gXCJpbmRlbnRcIjtlbHNlIGlmICh3b3JkID09IFwiZG9cIiAmJiBzdGF0ZS5jb250ZXh0LmluZGVudGVkIDwgc3RhdGUuaW5kZW50ZWQpIGt3dHlwZSA9IFwiaW5kZW50XCI7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChjdXJQdW5jIHx8IHN0eWxlICYmIHN0eWxlICE9IFwiY29tbWVudFwiKSBzdGF0ZS5sYXN0VG9rID0gdGhpc1RvaztcbiAgICBpZiAoY3VyUHVuYyA9PSBcInxcIikgc3RhdGUudmFyTGlzdCA9ICFzdGF0ZS52YXJMaXN0O1xuICAgIGlmIChrd3R5cGUgPT0gXCJpbmRlbnRcIiB8fCAvW1xcKFxcW1xce10vLnRlc3QoY3VyUHVuYykpIHN0YXRlLmNvbnRleHQgPSB7XG4gICAgICBwcmV2OiBzdGF0ZS5jb250ZXh0LFxuICAgICAgdHlwZTogY3VyUHVuYyB8fCBzdHlsZSxcbiAgICAgIGluZGVudGVkOiBzdGF0ZS5pbmRlbnRlZFxuICAgIH07ZWxzZSBpZiAoKGt3dHlwZSA9PSBcImRlZGVudFwiIHx8IC9bXFwpXFxdXFx9XS8udGVzdChjdXJQdW5jKSkgJiYgc3RhdGUuY29udGV4dC5wcmV2KSBzdGF0ZS5jb250ZXh0ID0gc3RhdGUuY29udGV4dC5wcmV2O1xuICAgIGlmIChzdHJlYW0uZW9sKCkpIHN0YXRlLmNvbnRpbnVlZExpbmUgPSBjdXJQdW5jID09IFwiXFxcXFwiIHx8IHN0eWxlID09IFwib3BlcmF0b3JcIjtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgaWYgKHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdICE9IHRva2VuQmFzZSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIGZpcnN0Q2hhciA9IHRleHRBZnRlciAmJiB0ZXh0QWZ0ZXIuY2hhckF0KDApO1xuICAgIHZhciBjdCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgdmFyIGNsb3NlZCA9IGN0LnR5cGUgPT0gY2xvc2luZ1tmaXJzdENoYXJdIHx8IGN0LnR5cGUgPT0gXCJrZXl3b3JkXCIgJiYgL14oPzplbmR8dW50aWx8ZWxzZXxlbHNpZnx3aGVufHJlc2N1ZSlcXGIvLnRlc3QodGV4dEFmdGVyKTtcbiAgICByZXR1cm4gY3QuaW5kZW50ZWQgKyAoY2xvc2VkID8gMCA6IGN4LnVuaXQpICsgKHN0YXRlLmNvbnRpbnVlZExpbmUgPyBjeC51bml0IDogMCk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGluZGVudE9uSW5wdXQ6IC9eXFxzKig/OmVuZHxyZXNjdWV8ZWxzaWZ8ZWxzZXxcXH0pJC8sXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIjXCJcbiAgICB9LFxuICAgIGF1dG9jb21wbGV0ZToga2V5d29yZExpc3RcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9