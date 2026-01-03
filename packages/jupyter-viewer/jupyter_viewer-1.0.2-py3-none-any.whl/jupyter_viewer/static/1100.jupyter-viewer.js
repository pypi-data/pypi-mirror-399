"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1100],{

/***/ 61100
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   crystal: () => (/* binding */ crystal)
/* harmony export */ });
function wordRegExp(words, end) {
  return new RegExp((end ? "" : "^") + "(?:" + words.join("|") + ")" + (end ? "$" : "\\b"));
}
function chain(tokenize, stream, state) {
  state.tokenize.push(tokenize);
  return tokenize(stream, state);
}
var operators = /^(?:[-+/%|&^]|\*\*?|[<>]{2})/;
var conditionalOperators = /^(?:[=!]~|===|<=>|[<>=!]=?|[|&]{2}|~)/;
var indexingOperators = /^(?:\[\][?=]?)/;
var anotherOperators = /^(?:\.(?:\.{2})?|->|[?:])/;
var idents = /^[a-z_\u009F-\uFFFF][a-zA-Z0-9_\u009F-\uFFFF]*/;
var types = /^[A-Z_\u009F-\uFFFF][a-zA-Z0-9_\u009F-\uFFFF]*/;
var keywords = wordRegExp(["abstract", "alias", "as", "asm", "begin", "break", "case", "class", "def", "do", "else", "elsif", "end", "ensure", "enum", "extend", "for", "fun", "if", "include", "instance_sizeof", "lib", "macro", "module", "next", "of", "out", "pointerof", "private", "protected", "rescue", "return", "require", "select", "sizeof", "struct", "super", "then", "type", "typeof", "uninitialized", "union", "unless", "until", "when", "while", "with", "yield", "__DIR__", "__END_LINE__", "__FILE__", "__LINE__"]);
var atomWords = wordRegExp(["true", "false", "nil", "self"]);
var indentKeywordsArray = ["def", "fun", "macro", "class", "module", "struct", "lib", "enum", "union", "do", "for"];
var indentKeywords = wordRegExp(indentKeywordsArray);
var indentExpressionKeywordsArray = ["if", "unless", "case", "while", "until", "begin", "then"];
var indentExpressionKeywords = wordRegExp(indentExpressionKeywordsArray);
var dedentKeywordsArray = ["end", "else", "elsif", "rescue", "ensure"];
var dedentKeywords = wordRegExp(dedentKeywordsArray);
var dedentPunctualsArray = ["\\)", "\\}", "\\]"];
var dedentPunctuals = new RegExp("^(?:" + dedentPunctualsArray.join("|") + ")$");
var nextTokenizer = {
  "def": tokenFollowIdent,
  "fun": tokenFollowIdent,
  "macro": tokenMacroDef,
  "class": tokenFollowType,
  "module": tokenFollowType,
  "struct": tokenFollowType,
  "lib": tokenFollowType,
  "enum": tokenFollowType,
  "union": tokenFollowType
};
var matching = {
  "[": "]",
  "{": "}",
  "(": ")",
  "<": ">"
};
function tokenBase(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }

  // Macros
  if (state.lastToken != "\\" && stream.match("{%", false)) {
    return chain(tokenMacro("%", "%"), stream, state);
  }
  if (state.lastToken != "\\" && stream.match("{{", false)) {
    return chain(tokenMacro("{", "}"), stream, state);
  }

  // Comments
  if (stream.peek() == "#") {
    stream.skipToEnd();
    return "comment";
  }

  // Variables and keywords
  var matched;
  if (stream.match(idents)) {
    stream.eat(/[?!]/);
    matched = stream.current();
    if (stream.eat(":")) {
      return "atom";
    } else if (state.lastToken == ".") {
      return "property";
    } else if (keywords.test(matched)) {
      if (indentKeywords.test(matched)) {
        if (!(matched == "fun" && state.blocks.indexOf("lib") >= 0) && !(matched == "def" && state.lastToken == "abstract")) {
          state.blocks.push(matched);
          state.currentIndent += 1;
        }
      } else if ((state.lastStyle == "operator" || !state.lastStyle) && indentExpressionKeywords.test(matched)) {
        state.blocks.push(matched);
        state.currentIndent += 1;
      } else if (matched == "end") {
        state.blocks.pop();
        state.currentIndent -= 1;
      }
      if (nextTokenizer.hasOwnProperty(matched)) {
        state.tokenize.push(nextTokenizer[matched]);
      }
      return "keyword";
    } else if (atomWords.test(matched)) {
      return "atom";
    }
    return "variable";
  }

  // Class variables and instance variables
  // or attributes
  if (stream.eat("@")) {
    if (stream.peek() == "[") {
      return chain(tokenNest("[", "]", "meta"), stream, state);
    }
    stream.eat("@");
    stream.match(idents) || stream.match(types);
    return "propertyName";
  }

  // Constants and types
  if (stream.match(types)) {
    return "tag";
  }

  // Symbols or ':' operator
  if (stream.eat(":")) {
    if (stream.eat("\"")) {
      return chain(tokenQuote("\"", "atom", false), stream, state);
    } else if (stream.match(idents) || stream.match(types) || stream.match(operators) || stream.match(conditionalOperators) || stream.match(indexingOperators)) {
      return "atom";
    }
    stream.eat(":");
    return "operator";
  }

  // Strings
  if (stream.eat("\"")) {
    return chain(tokenQuote("\"", "string", true), stream, state);
  }

  // Strings or regexps or macro variables or '%' operator
  if (stream.peek() == "%") {
    var style = "string";
    var embed = true;
    var delim;
    if (stream.match("%r")) {
      // Regexps
      style = "string.special";
      delim = stream.next();
    } else if (stream.match("%w")) {
      embed = false;
      delim = stream.next();
    } else if (stream.match("%q")) {
      embed = false;
      delim = stream.next();
    } else {
      if (delim = stream.match(/^%([^\w\s=])/)) {
        delim = delim[1];
      } else if (stream.match(/^%[a-zA-Z_\u009F-\uFFFF][\w\u009F-\uFFFF]*/)) {
        // Macro variables
        return "meta";
      } else if (stream.eat('%')) {
        // '%' operator
        return "operator";
      }
    }
    if (matching.hasOwnProperty(delim)) {
      delim = matching[delim];
    }
    return chain(tokenQuote(delim, style, embed), stream, state);
  }

  // Here Docs
  if (matched = stream.match(/^<<-('?)([A-Z]\w*)\1/)) {
    return chain(tokenHereDoc(matched[2], !matched[1]), stream, state);
  }

  // Characters
  if (stream.eat("'")) {
    stream.match(/^(?:[^']|\\(?:[befnrtv0'"]|[0-7]{3}|u(?:[0-9a-fA-F]{4}|\{[0-9a-fA-F]{1,6}\})))/);
    stream.eat("'");
    return "atom";
  }

  // Numbers
  if (stream.eat("0")) {
    if (stream.eat("x")) {
      stream.match(/^[0-9a-fA-F_]+/);
    } else if (stream.eat("o")) {
      stream.match(/^[0-7_]+/);
    } else if (stream.eat("b")) {
      stream.match(/^[01_]+/);
    }
    return "number";
  }
  if (stream.eat(/^\d/)) {
    stream.match(/^[\d_]*(?:\.[\d_]+)?(?:[eE][+-]?\d+)?/);
    return "number";
  }

  // Operators
  if (stream.match(operators)) {
    stream.eat("="); // Operators can follow assign symbol.
    return "operator";
  }
  if (stream.match(conditionalOperators) || stream.match(anotherOperators)) {
    return "operator";
  }

  // Parens and braces
  if (matched = stream.match(/[({[]/, false)) {
    matched = matched[0];
    return chain(tokenNest(matched, matching[matched], null), stream, state);
  }

  // Escapes
  if (stream.eat("\\")) {
    stream.next();
    return "meta";
  }
  stream.next();
  return null;
}
function tokenNest(begin, end, style, started) {
  return function (stream, state) {
    if (!started && stream.match(begin)) {
      state.tokenize[state.tokenize.length - 1] = tokenNest(begin, end, style, true);
      state.currentIndent += 1;
      return style;
    }
    var nextStyle = tokenBase(stream, state);
    if (stream.current() === end) {
      state.tokenize.pop();
      state.currentIndent -= 1;
      nextStyle = style;
    }
    return nextStyle;
  };
}
function tokenMacro(begin, end, started) {
  return function (stream, state) {
    if (!started && stream.match("{" + begin)) {
      state.currentIndent += 1;
      state.tokenize[state.tokenize.length - 1] = tokenMacro(begin, end, true);
      return "meta";
    }
    if (stream.match(end + "}")) {
      state.currentIndent -= 1;
      state.tokenize.pop();
      return "meta";
    }
    return tokenBase(stream, state);
  };
}
function tokenMacroDef(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  var matched;
  if (matched = stream.match(idents)) {
    if (matched == "def") {
      return "keyword";
    }
    stream.eat(/[?!]/);
  }
  state.tokenize.pop();
  return "def";
}
function tokenFollowIdent(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  if (stream.match(idents)) {
    stream.eat(/[!?]/);
  } else {
    stream.match(operators) || stream.match(conditionalOperators) || stream.match(indexingOperators);
  }
  state.tokenize.pop();
  return "def";
}
function tokenFollowType(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  stream.match(types);
  state.tokenize.pop();
  return "def";
}
function tokenQuote(end, style, embed) {
  return function (stream, state) {
    var escaped = false;
    while (stream.peek()) {
      if (!escaped) {
        if (stream.match("{%", false)) {
          state.tokenize.push(tokenMacro("%", "%"));
          return style;
        }
        if (stream.match("{{", false)) {
          state.tokenize.push(tokenMacro("{", "}"));
          return style;
        }
        if (embed && stream.match("#{", false)) {
          state.tokenize.push(tokenNest("#{", "}", "meta"));
          return style;
        }
        var ch = stream.next();
        if (ch == end) {
          state.tokenize.pop();
          return style;
        }
        escaped = embed && ch == "\\";
      } else {
        stream.next();
        escaped = false;
      }
    }
    return style;
  };
}
function tokenHereDoc(phrase, embed) {
  return function (stream, state) {
    if (stream.sol()) {
      stream.eatSpace();
      if (stream.match(phrase)) {
        state.tokenize.pop();
        return "string";
      }
    }
    var escaped = false;
    while (stream.peek()) {
      if (!escaped) {
        if (stream.match("{%", false)) {
          state.tokenize.push(tokenMacro("%", "%"));
          return "string";
        }
        if (stream.match("{{", false)) {
          state.tokenize.push(tokenMacro("{", "}"));
          return "string";
        }
        if (embed && stream.match("#{", false)) {
          state.tokenize.push(tokenNest("#{", "}", "meta"));
          return "string";
        }
        escaped = stream.next() == "\\" && embed;
      } else {
        stream.next();
        escaped = false;
      }
    }
    return "string";
  };
}
const crystal = {
  name: "crystal",
  startState: function () {
    return {
      tokenize: [tokenBase],
      currentIndent: 0,
      lastToken: null,
      lastStyle: null,
      blocks: []
    };
  },
  token: function (stream, state) {
    var style = state.tokenize[state.tokenize.length - 1](stream, state);
    var token = stream.current();
    if (style && style != "comment") {
      state.lastToken = token;
      state.lastStyle = style;
    }
    return style;
  },
  indent: function (state, textAfter, cx) {
    textAfter = textAfter.replace(/^\s*(?:\{%)?\s*|\s*(?:%\})?\s*$/g, "");
    if (dedentKeywords.test(textAfter) || dedentPunctuals.test(textAfter)) {
      return cx.unit * (state.currentIndent - 1);
    }
    return cx.unit * state.currentIndent;
  },
  languageData: {
    indentOnInput: wordRegExp(dedentPunctualsArray.concat(dedentKeywordsArray), true),
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTEwMC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2NyeXN0YWwuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZFJlZ0V4cCh3b3JkcywgZW5kKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKChlbmQgPyBcIlwiIDogXCJeXCIpICsgXCIoPzpcIiArIHdvcmRzLmpvaW4oXCJ8XCIpICsgXCIpXCIgKyAoZW5kID8gXCIkXCIgOiBcIlxcXFxiXCIpKTtcbn1cbmZ1bmN0aW9uIGNoYWluKHRva2VuaXplLCBzdHJlYW0sIHN0YXRlKSB7XG4gIHN0YXRlLnRva2VuaXplLnB1c2godG9rZW5pemUpO1xuICByZXR1cm4gdG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG59XG52YXIgb3BlcmF0b3JzID0gL14oPzpbLSsvJXwmXl18XFwqXFwqP3xbPD5dezJ9KS87XG52YXIgY29uZGl0aW9uYWxPcGVyYXRvcnMgPSAvXig/Ols9IV1+fD09PXw8PT58Wzw+PSFdPT98W3wmXXsyfXx+KS87XG52YXIgaW5kZXhpbmdPcGVyYXRvcnMgPSAvXig/OlxcW1xcXVs/PV0/KS87XG52YXIgYW5vdGhlck9wZXJhdG9ycyA9IC9eKD86XFwuKD86XFwuezJ9KT98LT58Wz86XSkvO1xudmFyIGlkZW50cyA9IC9eW2Etel9cXHUwMDlGLVxcdUZGRkZdW2EtekEtWjAtOV9cXHUwMDlGLVxcdUZGRkZdKi87XG52YXIgdHlwZXMgPSAvXltBLVpfXFx1MDA5Ri1cXHVGRkZGXVthLXpBLVowLTlfXFx1MDA5Ri1cXHVGRkZGXSovO1xudmFyIGtleXdvcmRzID0gd29yZFJlZ0V4cChbXCJhYnN0cmFjdFwiLCBcImFsaWFzXCIsIFwiYXNcIiwgXCJhc21cIiwgXCJiZWdpblwiLCBcImJyZWFrXCIsIFwiY2FzZVwiLCBcImNsYXNzXCIsIFwiZGVmXCIsIFwiZG9cIiwgXCJlbHNlXCIsIFwiZWxzaWZcIiwgXCJlbmRcIiwgXCJlbnN1cmVcIiwgXCJlbnVtXCIsIFwiZXh0ZW5kXCIsIFwiZm9yXCIsIFwiZnVuXCIsIFwiaWZcIiwgXCJpbmNsdWRlXCIsIFwiaW5zdGFuY2Vfc2l6ZW9mXCIsIFwibGliXCIsIFwibWFjcm9cIiwgXCJtb2R1bGVcIiwgXCJuZXh0XCIsIFwib2ZcIiwgXCJvdXRcIiwgXCJwb2ludGVyb2ZcIiwgXCJwcml2YXRlXCIsIFwicHJvdGVjdGVkXCIsIFwicmVzY3VlXCIsIFwicmV0dXJuXCIsIFwicmVxdWlyZVwiLCBcInNlbGVjdFwiLCBcInNpemVvZlwiLCBcInN0cnVjdFwiLCBcInN1cGVyXCIsIFwidGhlblwiLCBcInR5cGVcIiwgXCJ0eXBlb2ZcIiwgXCJ1bmluaXRpYWxpemVkXCIsIFwidW5pb25cIiwgXCJ1bmxlc3NcIiwgXCJ1bnRpbFwiLCBcIndoZW5cIiwgXCJ3aGlsZVwiLCBcIndpdGhcIiwgXCJ5aWVsZFwiLCBcIl9fRElSX19cIiwgXCJfX0VORF9MSU5FX19cIiwgXCJfX0ZJTEVfX1wiLCBcIl9fTElORV9fXCJdKTtcbnZhciBhdG9tV29yZHMgPSB3b3JkUmVnRXhwKFtcInRydWVcIiwgXCJmYWxzZVwiLCBcIm5pbFwiLCBcInNlbGZcIl0pO1xudmFyIGluZGVudEtleXdvcmRzQXJyYXkgPSBbXCJkZWZcIiwgXCJmdW5cIiwgXCJtYWNyb1wiLCBcImNsYXNzXCIsIFwibW9kdWxlXCIsIFwic3RydWN0XCIsIFwibGliXCIsIFwiZW51bVwiLCBcInVuaW9uXCIsIFwiZG9cIiwgXCJmb3JcIl07XG52YXIgaW5kZW50S2V5d29yZHMgPSB3b3JkUmVnRXhwKGluZGVudEtleXdvcmRzQXJyYXkpO1xudmFyIGluZGVudEV4cHJlc3Npb25LZXl3b3Jkc0FycmF5ID0gW1wiaWZcIiwgXCJ1bmxlc3NcIiwgXCJjYXNlXCIsIFwid2hpbGVcIiwgXCJ1bnRpbFwiLCBcImJlZ2luXCIsIFwidGhlblwiXTtcbnZhciBpbmRlbnRFeHByZXNzaW9uS2V5d29yZHMgPSB3b3JkUmVnRXhwKGluZGVudEV4cHJlc3Npb25LZXl3b3Jkc0FycmF5KTtcbnZhciBkZWRlbnRLZXl3b3Jkc0FycmF5ID0gW1wiZW5kXCIsIFwiZWxzZVwiLCBcImVsc2lmXCIsIFwicmVzY3VlXCIsIFwiZW5zdXJlXCJdO1xudmFyIGRlZGVudEtleXdvcmRzID0gd29yZFJlZ0V4cChkZWRlbnRLZXl3b3Jkc0FycmF5KTtcbnZhciBkZWRlbnRQdW5jdHVhbHNBcnJheSA9IFtcIlxcXFwpXCIsIFwiXFxcXH1cIiwgXCJcXFxcXVwiXTtcbnZhciBkZWRlbnRQdW5jdHVhbHMgPSBuZXcgUmVnRXhwKFwiXig/OlwiICsgZGVkZW50UHVuY3R1YWxzQXJyYXkuam9pbihcInxcIikgKyBcIikkXCIpO1xudmFyIG5leHRUb2tlbml6ZXIgPSB7XG4gIFwiZGVmXCI6IHRva2VuRm9sbG93SWRlbnQsXG4gIFwiZnVuXCI6IHRva2VuRm9sbG93SWRlbnQsXG4gIFwibWFjcm9cIjogdG9rZW5NYWNyb0RlZixcbiAgXCJjbGFzc1wiOiB0b2tlbkZvbGxvd1R5cGUsXG4gIFwibW9kdWxlXCI6IHRva2VuRm9sbG93VHlwZSxcbiAgXCJzdHJ1Y3RcIjogdG9rZW5Gb2xsb3dUeXBlLFxuICBcImxpYlwiOiB0b2tlbkZvbGxvd1R5cGUsXG4gIFwiZW51bVwiOiB0b2tlbkZvbGxvd1R5cGUsXG4gIFwidW5pb25cIjogdG9rZW5Gb2xsb3dUeXBlXG59O1xudmFyIG1hdGNoaW5nID0ge1xuICBcIltcIjogXCJdXCIsXG4gIFwie1wiOiBcIn1cIixcbiAgXCIoXCI6IFwiKVwiLFxuICBcIjxcIjogXCI+XCJcbn07XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuXG4gIC8vIE1hY3Jvc1xuICBpZiAoc3RhdGUubGFzdFRva2VuICE9IFwiXFxcXFwiICYmIHN0cmVhbS5tYXRjaChcInslXCIsIGZhbHNlKSkge1xuICAgIHJldHVybiBjaGFpbih0b2tlbk1hY3JvKFwiJVwiLCBcIiVcIiksIHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChzdGF0ZS5sYXN0VG9rZW4gIT0gXCJcXFxcXCIgJiYgc3RyZWFtLm1hdGNoKFwie3tcIiwgZmFsc2UpKSB7XG4gICAgcmV0dXJuIGNoYWluKHRva2VuTWFjcm8oXCJ7XCIsIFwifVwiKSwgc3RyZWFtLCBzdGF0ZSk7XG4gIH1cblxuICAvLyBDb21tZW50c1xuICBpZiAoc3RyZWFtLnBlZWsoKSA9PSBcIiNcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cblxuICAvLyBWYXJpYWJsZXMgYW5kIGtleXdvcmRzXG4gIHZhciBtYXRjaGVkO1xuICBpZiAoc3RyZWFtLm1hdGNoKGlkZW50cykpIHtcbiAgICBzdHJlYW0uZWF0KC9bPyFdLyk7XG4gICAgbWF0Y2hlZCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCI6XCIpKSB7XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgfSBlbHNlIGlmIChzdGF0ZS5sYXN0VG9rZW4gPT0gXCIuXCIpIHtcbiAgICAgIHJldHVybiBcInByb3BlcnR5XCI7XG4gICAgfSBlbHNlIGlmIChrZXl3b3Jkcy50ZXN0KG1hdGNoZWQpKSB7XG4gICAgICBpZiAoaW5kZW50S2V5d29yZHMudGVzdChtYXRjaGVkKSkge1xuICAgICAgICBpZiAoIShtYXRjaGVkID09IFwiZnVuXCIgJiYgc3RhdGUuYmxvY2tzLmluZGV4T2YoXCJsaWJcIikgPj0gMCkgJiYgIShtYXRjaGVkID09IFwiZGVmXCIgJiYgc3RhdGUubGFzdFRva2VuID09IFwiYWJzdHJhY3RcIikpIHtcbiAgICAgICAgICBzdGF0ZS5ibG9ja3MucHVzaChtYXRjaGVkKTtcbiAgICAgICAgICBzdGF0ZS5jdXJyZW50SW5kZW50ICs9IDE7XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSBpZiAoKHN0YXRlLmxhc3RTdHlsZSA9PSBcIm9wZXJhdG9yXCIgfHwgIXN0YXRlLmxhc3RTdHlsZSkgJiYgaW5kZW50RXhwcmVzc2lvbktleXdvcmRzLnRlc3QobWF0Y2hlZCkpIHtcbiAgICAgICAgc3RhdGUuYmxvY2tzLnB1c2gobWF0Y2hlZCk7XG4gICAgICAgIHN0YXRlLmN1cnJlbnRJbmRlbnQgKz0gMTtcbiAgICAgIH0gZWxzZSBpZiAobWF0Y2hlZCA9PSBcImVuZFwiKSB7XG4gICAgICAgIHN0YXRlLmJsb2Nrcy5wb3AoKTtcbiAgICAgICAgc3RhdGUuY3VycmVudEluZGVudCAtPSAxO1xuICAgICAgfVxuICAgICAgaWYgKG5leHRUb2tlbml6ZXIuaGFzT3duUHJvcGVydHkobWF0Y2hlZCkpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUucHVzaChuZXh0VG9rZW5pemVyW21hdGNoZWRdKTtcbiAgICAgIH1cbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9IGVsc2UgaWYgKGF0b21Xb3Jkcy50ZXN0KG1hdGNoZWQpKSB7XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgfVxuICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gIH1cblxuICAvLyBDbGFzcyB2YXJpYWJsZXMgYW5kIGluc3RhbmNlIHZhcmlhYmxlc1xuICAvLyBvciBhdHRyaWJ1dGVzXG4gIGlmIChzdHJlYW0uZWF0KFwiQFwiKSkge1xuICAgIGlmIChzdHJlYW0ucGVlaygpID09IFwiW1wiKSB7XG4gICAgICByZXR1cm4gY2hhaW4odG9rZW5OZXN0KFwiW1wiLCBcIl1cIiwgXCJtZXRhXCIpLCBzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgc3RyZWFtLmVhdChcIkBcIik7XG4gICAgc3RyZWFtLm1hdGNoKGlkZW50cykgfHwgc3RyZWFtLm1hdGNoKHR5cGVzKTtcbiAgICByZXR1cm4gXCJwcm9wZXJ0eU5hbWVcIjtcbiAgfVxuXG4gIC8vIENvbnN0YW50cyBhbmQgdHlwZXNcbiAgaWYgKHN0cmVhbS5tYXRjaCh0eXBlcykpIHtcbiAgICByZXR1cm4gXCJ0YWdcIjtcbiAgfVxuXG4gIC8vIFN5bWJvbHMgb3IgJzonIG9wZXJhdG9yXG4gIGlmIChzdHJlYW0uZWF0KFwiOlwiKSkge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiXFxcIlwiKSkge1xuICAgICAgcmV0dXJuIGNoYWluKHRva2VuUXVvdGUoXCJcXFwiXCIsIFwiYXRvbVwiLCBmYWxzZSksIHN0cmVhbSwgc3RhdGUpO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKGlkZW50cykgfHwgc3RyZWFtLm1hdGNoKHR5cGVzKSB8fCBzdHJlYW0ubWF0Y2gob3BlcmF0b3JzKSB8fCBzdHJlYW0ubWF0Y2goY29uZGl0aW9uYWxPcGVyYXRvcnMpIHx8IHN0cmVhbS5tYXRjaChpbmRleGluZ09wZXJhdG9ycykpIHtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9XG4gICAgc3RyZWFtLmVhdChcIjpcIik7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuXG4gIC8vIFN0cmluZ3NcbiAgaWYgKHN0cmVhbS5lYXQoXCJcXFwiXCIpKSB7XG4gICAgcmV0dXJuIGNoYWluKHRva2VuUXVvdGUoXCJcXFwiXCIsIFwic3RyaW5nXCIsIHRydWUpLCBzdHJlYW0sIHN0YXRlKTtcbiAgfVxuXG4gIC8vIFN0cmluZ3Mgb3IgcmVnZXhwcyBvciBtYWNybyB2YXJpYWJsZXMgb3IgJyUnIG9wZXJhdG9yXG4gIGlmIChzdHJlYW0ucGVlaygpID09IFwiJVwiKSB7XG4gICAgdmFyIHN0eWxlID0gXCJzdHJpbmdcIjtcbiAgICB2YXIgZW1iZWQgPSB0cnVlO1xuICAgIHZhciBkZWxpbTtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKFwiJXJcIikpIHtcbiAgICAgIC8vIFJlZ2V4cHNcbiAgICAgIHN0eWxlID0gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICAgICAgZGVsaW0gPSBzdHJlYW0ubmV4dCgpO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKFwiJXdcIikpIHtcbiAgICAgIGVtYmVkID0gZmFsc2U7XG4gICAgICBkZWxpbSA9IHN0cmVhbS5uZXh0KCk7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goXCIlcVwiKSkge1xuICAgICAgZW1iZWQgPSBmYWxzZTtcbiAgICAgIGRlbGltID0gc3RyZWFtLm5leHQoKTtcbiAgICB9IGVsc2Uge1xuICAgICAgaWYgKGRlbGltID0gc3RyZWFtLm1hdGNoKC9eJShbXlxcd1xccz1dKS8pKSB7XG4gICAgICAgIGRlbGltID0gZGVsaW1bMV07XG4gICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXiVbYS16QS1aX1xcdTAwOUYtXFx1RkZGRl1bXFx3XFx1MDA5Ri1cXHVGRkZGXSovKSkge1xuICAgICAgICAvLyBNYWNybyB2YXJpYWJsZXNcbiAgICAgICAgcmV0dXJuIFwibWV0YVwiO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KCclJykpIHtcbiAgICAgICAgLy8gJyUnIG9wZXJhdG9yXG4gICAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChtYXRjaGluZy5oYXNPd25Qcm9wZXJ0eShkZWxpbSkpIHtcbiAgICAgIGRlbGltID0gbWF0Y2hpbmdbZGVsaW1dO1xuICAgIH1cbiAgICByZXR1cm4gY2hhaW4odG9rZW5RdW90ZShkZWxpbSwgc3R5bGUsIGVtYmVkKSwgc3RyZWFtLCBzdGF0ZSk7XG4gIH1cblxuICAvLyBIZXJlIERvY3NcbiAgaWYgKG1hdGNoZWQgPSBzdHJlYW0ubWF0Y2goL148PC0oJz8pKFtBLVpdXFx3KilcXDEvKSkge1xuICAgIHJldHVybiBjaGFpbih0b2tlbkhlcmVEb2MobWF0Y2hlZFsyXSwgIW1hdGNoZWRbMV0pLCBzdHJlYW0sIHN0YXRlKTtcbiAgfVxuXG4gIC8vIENoYXJhY3RlcnNcbiAgaWYgKHN0cmVhbS5lYXQoXCInXCIpKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9eKD86W14nXXxcXFxcKD86W2JlZm5ydHYwJ1wiXXxbMC03XXszfXx1KD86WzAtOWEtZkEtRl17NH18XFx7WzAtOWEtZkEtRl17MSw2fVxcfSkpKS8pO1xuICAgIHN0cmVhbS5lYXQoXCInXCIpO1xuICAgIHJldHVybiBcImF0b21cIjtcbiAgfVxuXG4gIC8vIE51bWJlcnNcbiAgaWYgKHN0cmVhbS5lYXQoXCIwXCIpKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCJ4XCIpKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15bMC05YS1mQS1GX10rLyk7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KFwib1wiKSkge1xuICAgICAgc3RyZWFtLm1hdGNoKC9eWzAtN19dKy8pO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdChcImJcIikpIHtcbiAgICAgIHN0cmVhbS5tYXRjaCgvXlswMV9dKy8pO1xuICAgIH1cbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuICBpZiAoc3RyZWFtLmVhdCgvXlxcZC8pKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9eW1xcZF9dKig/OlxcLltcXGRfXSspPyg/OltlRV1bKy1dP1xcZCspPy8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9XG5cbiAgLy8gT3BlcmF0b3JzXG4gIGlmIChzdHJlYW0ubWF0Y2gob3BlcmF0b3JzKSkge1xuICAgIHN0cmVhbS5lYXQoXCI9XCIpOyAvLyBPcGVyYXRvcnMgY2FuIGZvbGxvdyBhc3NpZ24gc3ltYm9sLlxuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChjb25kaXRpb25hbE9wZXJhdG9ycykgfHwgc3RyZWFtLm1hdGNoKGFub3RoZXJPcGVyYXRvcnMpKSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuXG4gIC8vIFBhcmVucyBhbmQgYnJhY2VzXG4gIGlmIChtYXRjaGVkID0gc3RyZWFtLm1hdGNoKC9bKHtbXS8sIGZhbHNlKSkge1xuICAgIG1hdGNoZWQgPSBtYXRjaGVkWzBdO1xuICAgIHJldHVybiBjaGFpbih0b2tlbk5lc3QobWF0Y2hlZCwgbWF0Y2hpbmdbbWF0Y2hlZF0sIG51bGwpLCBzdHJlYW0sIHN0YXRlKTtcbiAgfVxuXG4gIC8vIEVzY2FwZXNcbiAgaWYgKHN0cmVhbS5lYXQoXCJcXFxcXCIpKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gXCJtZXRhXCI7XG4gIH1cbiAgc3RyZWFtLm5leHQoKTtcbiAgcmV0dXJuIG51bGw7XG59XG5mdW5jdGlvbiB0b2tlbk5lc3QoYmVnaW4sIGVuZCwgc3R5bGUsIHN0YXJ0ZWQpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKCFzdGFydGVkICYmIHN0cmVhbS5tYXRjaChiZWdpbikpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdID0gdG9rZW5OZXN0KGJlZ2luLCBlbmQsIHN0eWxlLCB0cnVlKTtcbiAgICAgIHN0YXRlLmN1cnJlbnRJbmRlbnQgKz0gMTtcbiAgICAgIHJldHVybiBzdHlsZTtcbiAgICB9XG4gICAgdmFyIG5leHRTdHlsZSA9IHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3RyZWFtLmN1cnJlbnQoKSA9PT0gZW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgIHN0YXRlLmN1cnJlbnRJbmRlbnQgLT0gMTtcbiAgICAgIG5leHRTdHlsZSA9IHN0eWxlO1xuICAgIH1cbiAgICByZXR1cm4gbmV4dFN0eWxlO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5NYWNybyhiZWdpbiwgZW5kLCBzdGFydGVkKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmICghc3RhcnRlZCAmJiBzdHJlYW0ubWF0Y2goXCJ7XCIgKyBiZWdpbikpIHtcbiAgICAgIHN0YXRlLmN1cnJlbnRJbmRlbnQgKz0gMTtcbiAgICAgIHN0YXRlLnRva2VuaXplW3N0YXRlLnRva2VuaXplLmxlbmd0aCAtIDFdID0gdG9rZW5NYWNybyhiZWdpbiwgZW5kLCB0cnVlKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChlbmQgKyBcIn1cIikpIHtcbiAgICAgIHN0YXRlLmN1cnJlbnRJbmRlbnQgLT0gMTtcbiAgICAgIHN0YXRlLnRva2VuaXplLnBvcCgpO1xuICAgICAgcmV0dXJuIFwibWV0YVwiO1xuICAgIH1cbiAgICByZXR1cm4gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5NYWNyb0RlZihzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIHZhciBtYXRjaGVkO1xuICBpZiAobWF0Y2hlZCA9IHN0cmVhbS5tYXRjaChpZGVudHMpKSB7XG4gICAgaWYgKG1hdGNoZWQgPT0gXCJkZWZcIikge1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICBzdHJlYW0uZWF0KC9bPyFdLyk7XG4gIH1cbiAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gIHJldHVybiBcImRlZlwiO1xufVxuZnVuY3Rpb24gdG9rZW5Gb2xsb3dJZGVudChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goaWRlbnRzKSkge1xuICAgIHN0cmVhbS5lYXQoL1shP10vKTtcbiAgfSBlbHNlIHtcbiAgICBzdHJlYW0ubWF0Y2gob3BlcmF0b3JzKSB8fCBzdHJlYW0ubWF0Y2goY29uZGl0aW9uYWxPcGVyYXRvcnMpIHx8IHN0cmVhbS5tYXRjaChpbmRleGluZ09wZXJhdG9ycyk7XG4gIH1cbiAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gIHJldHVybiBcImRlZlwiO1xufVxuZnVuY3Rpb24gdG9rZW5Gb2xsb3dUeXBlKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgc3RyZWFtLm1hdGNoKHR5cGVzKTtcbiAgc3RhdGUudG9rZW5pemUucG9wKCk7XG4gIHJldHVybiBcImRlZlwiO1xufVxuZnVuY3Rpb24gdG9rZW5RdW90ZShlbmQsIHN0eWxlLCBlbWJlZCkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlO1xuICAgIHdoaWxlIChzdHJlYW0ucGVlaygpKSB7XG4gICAgICBpZiAoIWVzY2FwZWQpIHtcbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChcInslXCIsIGZhbHNlKSkge1xuICAgICAgICAgIHN0YXRlLnRva2VuaXplLnB1c2godG9rZW5NYWNybyhcIiVcIiwgXCIlXCIpKTtcbiAgICAgICAgICByZXR1cm4gc3R5bGU7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChcInt7XCIsIGZhbHNlKSkge1xuICAgICAgICAgIHN0YXRlLnRva2VuaXplLnB1c2godG9rZW5NYWNybyhcIntcIiwgXCJ9XCIpKTtcbiAgICAgICAgICByZXR1cm4gc3R5bGU7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGVtYmVkICYmIHN0cmVhbS5tYXRjaChcIiN7XCIsIGZhbHNlKSkge1xuICAgICAgICAgIHN0YXRlLnRva2VuaXplLnB1c2godG9rZW5OZXN0KFwiI3tcIiwgXCJ9XCIsIFwibWV0YVwiKSk7XG4gICAgICAgICAgcmV0dXJuIHN0eWxlO1xuICAgICAgICB9XG4gICAgICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgICAgIGlmIChjaCA9PSBlbmQpIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgICAgICByZXR1cm4gc3R5bGU7XG4gICAgICAgIH1cbiAgICAgICAgZXNjYXBlZCA9IGVtYmVkICYmIGNoID09IFwiXFxcXFwiO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgZXNjYXBlZCA9IGZhbHNlO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH07XG59XG5mdW5jdGlvbiB0b2tlbkhlcmVEb2MocGhyYXNlLCBlbWJlZCkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBzdHJlYW0uZWF0U3BhY2UoKTtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2gocGhyYXNlKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZS5wb3AoKTtcbiAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICB9XG4gICAgfVxuICAgIHZhciBlc2NhcGVkID0gZmFsc2U7XG4gICAgd2hpbGUgKHN0cmVhbS5wZWVrKCkpIHtcbiAgICAgIGlmICghZXNjYXBlZCkge1xuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKFwieyVcIiwgZmFsc2UpKSB7XG4gICAgICAgICAgc3RhdGUudG9rZW5pemUucHVzaCh0b2tlbk1hY3JvKFwiJVwiLCBcIiVcIikpO1xuICAgICAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgICAgICB9XG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goXCJ7e1wiLCBmYWxzZSkpIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZS5wdXNoKHRva2VuTWFjcm8oXCJ7XCIsIFwifVwiKSk7XG4gICAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGVtYmVkICYmIHN0cmVhbS5tYXRjaChcIiN7XCIsIGZhbHNlKSkge1xuICAgICAgICAgIHN0YXRlLnRva2VuaXplLnB1c2godG9rZW5OZXN0KFwiI3tcIiwgXCJ9XCIsIFwibWV0YVwiKSk7XG4gICAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICAgIH1cbiAgICAgICAgZXNjYXBlZCA9IHN0cmVhbS5uZXh0KCkgPT0gXCJcXFxcXCIgJiYgZW1iZWQ7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICBlc2NhcGVkID0gZmFsc2U7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZXhwb3J0IGNvbnN0IGNyeXN0YWwgPSB7XG4gIG5hbWU6IFwiY3J5c3RhbFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBbdG9rZW5CYXNlXSxcbiAgICAgIGN1cnJlbnRJbmRlbnQ6IDAsXG4gICAgICBsYXN0VG9rZW46IG51bGwsXG4gICAgICBsYXN0U3R5bGU6IG51bGwsXG4gICAgICBibG9ja3M6IFtdXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemVbc3RhdGUudG9rZW5pemUubGVuZ3RoIC0gMV0oc3RyZWFtLCBzdGF0ZSk7XG4gICAgdmFyIHRva2VuID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICBpZiAoc3R5bGUgJiYgc3R5bGUgIT0gXCJjb21tZW50XCIpIHtcbiAgICAgIHN0YXRlLmxhc3RUb2tlbiA9IHRva2VuO1xuICAgICAgc3RhdGUubGFzdFN0eWxlID0gc3R5bGU7XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICB0ZXh0QWZ0ZXIgPSB0ZXh0QWZ0ZXIucmVwbGFjZSgvXlxccyooPzpcXHslKT9cXHMqfFxccyooPzolXFx9KT9cXHMqJC9nLCBcIlwiKTtcbiAgICBpZiAoZGVkZW50S2V5d29yZHMudGVzdCh0ZXh0QWZ0ZXIpIHx8IGRlZGVudFB1bmN0dWFscy50ZXN0KHRleHRBZnRlcikpIHtcbiAgICAgIHJldHVybiBjeC51bml0ICogKHN0YXRlLmN1cnJlbnRJbmRlbnQgLSAxKTtcbiAgICB9XG4gICAgcmV0dXJuIGN4LnVuaXQgKiBzdGF0ZS5jdXJyZW50SW5kZW50O1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiB3b3JkUmVnRXhwKGRlZGVudFB1bmN0dWFsc0FycmF5LmNvbmNhdChkZWRlbnRLZXl3b3Jkc0FycmF5KSwgdHJ1ZSksXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIjXCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==