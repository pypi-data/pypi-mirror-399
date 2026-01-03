"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7301],{

/***/ 7301
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   oz: () => (/* binding */ oz)
/* harmony export */ });
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b");
}
var singleOperators = /[\^@!\|<>#~\.\*\-\+\\/,=]/;
var doubleOperators = /(<-)|(:=)|(=<)|(>=)|(<=)|(<:)|(>:)|(=:)|(\\=)|(\\=:)|(!!)|(==)|(::)/;
var tripleOperators = /(:::)|(\.\.\.)|(=<:)|(>=:)/;
var middle = ["in", "then", "else", "of", "elseof", "elsecase", "elseif", "catch", "finally", "with", "require", "prepare", "import", "export", "define", "do"];
var end = ["end"];
var atoms = wordRegexp(["true", "false", "nil", "unit"]);
var commonKeywords = wordRegexp(["andthen", "at", "attr", "declare", "feat", "from", "lex", "mod", "div", "mode", "orelse", "parser", "prod", "prop", "scanner", "self", "syn", "token"]);
var openingKeywords = wordRegexp(["local", "proc", "fun", "case", "class", "if", "cond", "or", "dis", "choice", "not", "thread", "try", "raise", "lock", "for", "suchthat", "meth", "functor"]);
var middleKeywords = wordRegexp(middle);
var endKeywords = wordRegexp(end);

// Tokenizers
function tokenBase(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }

  // Brackets
  if (stream.match(/[{}]/)) {
    return "bracket";
  }

  // Special [] keyword
  if (stream.match('[]')) {
    return "keyword";
  }

  // Operators
  if (stream.match(tripleOperators) || stream.match(doubleOperators)) {
    return "operator";
  }

  // Atoms
  if (stream.match(atoms)) {
    return 'atom';
  }

  // Opening keywords
  var matched = stream.match(openingKeywords);
  if (matched) {
    if (!state.doInCurrentLine) state.currentIndent++;else state.doInCurrentLine = false;

    // Special matching for signatures
    if (matched[0] == "proc" || matched[0] == "fun") state.tokenize = tokenFunProc;else if (matched[0] == "class") state.tokenize = tokenClass;else if (matched[0] == "meth") state.tokenize = tokenMeth;
    return 'keyword';
  }

  // Middle and other keywords
  if (stream.match(middleKeywords) || stream.match(commonKeywords)) {
    return "keyword";
  }

  // End keywords
  if (stream.match(endKeywords)) {
    state.currentIndent--;
    return 'keyword';
  }

  // Eat the next char for next comparisons
  var ch = stream.next();

  // Strings
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }

  // Numbers
  if (/[~\d]/.test(ch)) {
    if (ch == "~") {
      if (!/^[0-9]/.test(stream.peek())) return null;else if (stream.next() == "0" && stream.match(/^[xX][0-9a-fA-F]+/) || stream.match(/^[0-9]*(\.[0-9]+)?([eE][~+]?[0-9]+)?/)) return "number";
    }
    if (ch == "0" && stream.match(/^[xX][0-9a-fA-F]+/) || stream.match(/^[0-9]*(\.[0-9]+)?([eE][~+]?[0-9]+)?/)) return "number";
    return null;
  }

  // Comments
  if (ch == "%") {
    stream.skipToEnd();
    return 'comment';
  } else if (ch == "/") {
    if (stream.eat("*")) {
      state.tokenize = tokenComment;
      return tokenComment(stream, state);
    }
  }

  // Single operators
  if (singleOperators.test(ch)) {
    return "operator";
  }

  // If nothing match, we skip the entire alphanumerical block
  stream.eatWhile(/\w/);
  return "variable";
}
function tokenClass(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  stream.match(/([A-Z][A-Za-z0-9_]*)|(`.+`)/);
  state.tokenize = tokenBase;
  return "type";
}
function tokenMeth(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  stream.match(/([a-zA-Z][A-Za-z0-9_]*)|(`.+`)/);
  state.tokenize = tokenBase;
  return "def";
}
function tokenFunProc(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  if (!state.hasPassedFirstStage && stream.eat("{")) {
    state.hasPassedFirstStage = true;
    return "bracket";
  } else if (state.hasPassedFirstStage) {
    stream.match(/([A-Z][A-Za-z0-9_]*)|(`.+`)|\$/);
    state.hasPassedFirstStage = false;
    state.tokenize = tokenBase;
    return "def";
  } else {
    state.tokenize = tokenBase;
    return null;
  }
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
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
      escaped = !escaped && next == "\\";
    }
    if (end || !escaped) state.tokenize = tokenBase;
    return "string";
  };
}
function buildElectricInputRegEx() {
  // Reindentation should occur on [] or on a match of any of
  // the block closing keywords, at the end of a line.
  var allClosings = middle.concat(end);
  return new RegExp("[\\[\\]]|(" + allClosings.join("|") + ")$");
}
const oz = {
  name: "oz",
  startState: function () {
    return {
      tokenize: tokenBase,
      currentIndent: 0,
      doInCurrentLine: false,
      hasPassedFirstStage: false
    };
  },
  token: function (stream, state) {
    if (stream.sol()) state.doInCurrentLine = 0;
    return state.tokenize(stream, state);
  },
  indent: function (state, textAfter, cx) {
    var trueText = textAfter.replace(/^\s+|\s+$/g, '');
    if (trueText.match(endKeywords) || trueText.match(middleKeywords) || trueText.match(/(\[])/)) return cx.unit * (state.currentIndent - 1);
    if (state.currentIndent < 0) return 0;
    return state.currentIndent * cx.unit;
  },
  languageData: {
    indentOnInut: buildElectricInputRegEx(),
    commentTokens: {
      line: "%",
      block: {
        open: "/*",
        close: "*/"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzMwMS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9vei5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIpO1xufVxudmFyIHNpbmdsZU9wZXJhdG9ycyA9IC9bXFxeQCFcXHw8PiN+XFwuXFwqXFwtXFwrXFxcXC8sPV0vO1xudmFyIGRvdWJsZU9wZXJhdG9ycyA9IC8oPC0pfCg6PSl8KD08KXwoPj0pfCg8PSl8KDw6KXwoPjopfCg9Oil8KFxcXFw9KXwoXFxcXD06KXwoISEpfCg9PSl8KDo6KS87XG52YXIgdHJpcGxlT3BlcmF0b3JzID0gLyg6OjopfChcXC5cXC5cXC4pfCg9PDopfCg+PTopLztcbnZhciBtaWRkbGUgPSBbXCJpblwiLCBcInRoZW5cIiwgXCJlbHNlXCIsIFwib2ZcIiwgXCJlbHNlb2ZcIiwgXCJlbHNlY2FzZVwiLCBcImVsc2VpZlwiLCBcImNhdGNoXCIsIFwiZmluYWxseVwiLCBcIndpdGhcIiwgXCJyZXF1aXJlXCIsIFwicHJlcGFyZVwiLCBcImltcG9ydFwiLCBcImV4cG9ydFwiLCBcImRlZmluZVwiLCBcImRvXCJdO1xudmFyIGVuZCA9IFtcImVuZFwiXTtcbnZhciBhdG9tcyA9IHdvcmRSZWdleHAoW1widHJ1ZVwiLCBcImZhbHNlXCIsIFwibmlsXCIsIFwidW5pdFwiXSk7XG52YXIgY29tbW9uS2V5d29yZHMgPSB3b3JkUmVnZXhwKFtcImFuZHRoZW5cIiwgXCJhdFwiLCBcImF0dHJcIiwgXCJkZWNsYXJlXCIsIFwiZmVhdFwiLCBcImZyb21cIiwgXCJsZXhcIiwgXCJtb2RcIiwgXCJkaXZcIiwgXCJtb2RlXCIsIFwib3JlbHNlXCIsIFwicGFyc2VyXCIsIFwicHJvZFwiLCBcInByb3BcIiwgXCJzY2FubmVyXCIsIFwic2VsZlwiLCBcInN5blwiLCBcInRva2VuXCJdKTtcbnZhciBvcGVuaW5nS2V5d29yZHMgPSB3b3JkUmVnZXhwKFtcImxvY2FsXCIsIFwicHJvY1wiLCBcImZ1blwiLCBcImNhc2VcIiwgXCJjbGFzc1wiLCBcImlmXCIsIFwiY29uZFwiLCBcIm9yXCIsIFwiZGlzXCIsIFwiY2hvaWNlXCIsIFwibm90XCIsIFwidGhyZWFkXCIsIFwidHJ5XCIsIFwicmFpc2VcIiwgXCJsb2NrXCIsIFwiZm9yXCIsIFwic3VjaHRoYXRcIiwgXCJtZXRoXCIsIFwiZnVuY3RvclwiXSk7XG52YXIgbWlkZGxlS2V5d29yZHMgPSB3b3JkUmVnZXhwKG1pZGRsZSk7XG52YXIgZW5kS2V5d29yZHMgPSB3b3JkUmVnZXhwKGVuZCk7XG5cbi8vIFRva2VuaXplcnNcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG5cbiAgLy8gQnJhY2tldHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgvW3t9XS8pKSB7XG4gICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICB9XG5cbiAgLy8gU3BlY2lhbCBbXSBrZXl3b3JkXG4gIGlmIChzdHJlYW0ubWF0Y2goJ1tdJykpIHtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cblxuICAvLyBPcGVyYXRvcnNcbiAgaWYgKHN0cmVhbS5tYXRjaCh0cmlwbGVPcGVyYXRvcnMpIHx8IHN0cmVhbS5tYXRjaChkb3VibGVPcGVyYXRvcnMpKSB7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuXG4gIC8vIEF0b21zXG4gIGlmIChzdHJlYW0ubWF0Y2goYXRvbXMpKSB7XG4gICAgcmV0dXJuICdhdG9tJztcbiAgfVxuXG4gIC8vIE9wZW5pbmcga2V5d29yZHNcbiAgdmFyIG1hdGNoZWQgPSBzdHJlYW0ubWF0Y2gob3BlbmluZ0tleXdvcmRzKTtcbiAgaWYgKG1hdGNoZWQpIHtcbiAgICBpZiAoIXN0YXRlLmRvSW5DdXJyZW50TGluZSkgc3RhdGUuY3VycmVudEluZGVudCsrO2Vsc2Ugc3RhdGUuZG9JbkN1cnJlbnRMaW5lID0gZmFsc2U7XG5cbiAgICAvLyBTcGVjaWFsIG1hdGNoaW5nIGZvciBzaWduYXR1cmVzXG4gICAgaWYgKG1hdGNoZWRbMF0gPT0gXCJwcm9jXCIgfHwgbWF0Y2hlZFswXSA9PSBcImZ1blwiKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuRnVuUHJvYztlbHNlIGlmIChtYXRjaGVkWzBdID09IFwiY2xhc3NcIikgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNsYXNzO2Vsc2UgaWYgKG1hdGNoZWRbMF0gPT0gXCJtZXRoXCIpIHN0YXRlLnRva2VuaXplID0gdG9rZW5NZXRoO1xuICAgIHJldHVybiAna2V5d29yZCc7XG4gIH1cblxuICAvLyBNaWRkbGUgYW5kIG90aGVyIGtleXdvcmRzXG4gIGlmIChzdHJlYW0ubWF0Y2gobWlkZGxlS2V5d29yZHMpIHx8IHN0cmVhbS5tYXRjaChjb21tb25LZXl3b3JkcykpIHtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cblxuICAvLyBFbmQga2V5d29yZHNcbiAgaWYgKHN0cmVhbS5tYXRjaChlbmRLZXl3b3JkcykpIHtcbiAgICBzdGF0ZS5jdXJyZW50SW5kZW50LS07XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuXG4gIC8vIEVhdCB0aGUgbmV4dCBjaGFyIGZvciBuZXh0IGNvbXBhcmlzb25zXG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG5cbiAgLy8gU3RyaW5nc1xuICBpZiAoY2ggPT0gJ1wiJyB8fCBjaCA9PSBcIidcIikge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmcoY2gpO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuXG4gIC8vIE51bWJlcnNcbiAgaWYgKC9bflxcZF0vLnRlc3QoY2gpKSB7XG4gICAgaWYgKGNoID09IFwiflwiKSB7XG4gICAgICBpZiAoIS9eWzAtOV0vLnRlc3Qoc3RyZWFtLnBlZWsoKSkpIHJldHVybiBudWxsO2Vsc2UgaWYgKHN0cmVhbS5uZXh0KCkgPT0gXCIwXCIgJiYgc3RyZWFtLm1hdGNoKC9eW3hYXVswLTlhLWZBLUZdKy8pIHx8IHN0cmVhbS5tYXRjaCgvXlswLTldKihcXC5bMC05XSspPyhbZUVdW34rXT9bMC05XSspPy8pKSByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gICAgaWYgKGNoID09IFwiMFwiICYmIHN0cmVhbS5tYXRjaCgvXlt4WF1bMC05YS1mQS1GXSsvKSB8fCBzdHJlYW0ubWF0Y2goL15bMC05XSooXFwuWzAtOV0rKT8oW2VFXVt+K10/WzAtOV0rKT8vKSkgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cblxuICAvLyBDb21tZW50c1xuICBpZiAoY2ggPT0gXCIlXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuICdjb21tZW50JztcbiAgfSBlbHNlIGlmIChjaCA9PSBcIi9cIikge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnQ7XG4gICAgICByZXR1cm4gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgIH1cbiAgfVxuXG4gIC8vIFNpbmdsZSBvcGVyYXRvcnNcbiAgaWYgKHNpbmdsZU9wZXJhdG9ycy50ZXN0KGNoKSkge1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cblxuICAvLyBJZiBub3RoaW5nIG1hdGNoLCB3ZSBza2lwIHRoZSBlbnRpcmUgYWxwaGFudW1lcmljYWwgYmxvY2tcbiAgc3RyZWFtLmVhdFdoaWxlKC9cXHcvKTtcbiAgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cbmZ1bmN0aW9uIHRva2VuQ2xhc3Moc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBzdHJlYW0ubWF0Y2goLyhbQS1aXVtBLVphLXowLTlfXSopfChgLitgKS8pO1xuICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgcmV0dXJuIFwidHlwZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5NZXRoKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgc3RyZWFtLm1hdGNoKC8oW2EtekEtWl1bQS1aYS16MC05X10qKXwoYC4rYCkvKTtcbiAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gIHJldHVybiBcImRlZlwiO1xufVxuZnVuY3Rpb24gdG9rZW5GdW5Qcm9jKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKCFzdGF0ZS5oYXNQYXNzZWRGaXJzdFN0YWdlICYmIHN0cmVhbS5lYXQoXCJ7XCIpKSB7XG4gICAgc3RhdGUuaGFzUGFzc2VkRmlyc3RTdGFnZSA9IHRydWU7XG4gICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICB9IGVsc2UgaWYgKHN0YXRlLmhhc1Bhc3NlZEZpcnN0U3RhZ2UpIHtcbiAgICBzdHJlYW0ubWF0Y2goLyhbQS1aXVtBLVphLXowLTlfXSopfChgLitgKXxcXCQvKTtcbiAgICBzdGF0ZS5oYXNQYXNzZWRGaXJzdFN0YWdlID0gZmFsc2U7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuIFwiZGVmXCI7XG4gIH0gZWxzZSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbn1cbmZ1bmN0aW9uIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiL1wiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKGVuZCB8fCAhZXNjYXBlZCkgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5mdW5jdGlvbiBidWlsZEVsZWN0cmljSW5wdXRSZWdFeCgpIHtcbiAgLy8gUmVpbmRlbnRhdGlvbiBzaG91bGQgb2NjdXIgb24gW10gb3Igb24gYSBtYXRjaCBvZiBhbnkgb2ZcbiAgLy8gdGhlIGJsb2NrIGNsb3Npbmcga2V5d29yZHMsIGF0IHRoZSBlbmQgb2YgYSBsaW5lLlxuICB2YXIgYWxsQ2xvc2luZ3MgPSBtaWRkbGUuY29uY2F0KGVuZCk7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiW1xcXFxbXFxcXF1dfChcIiArIGFsbENsb3NpbmdzLmpvaW4oXCJ8XCIpICsgXCIpJFwiKTtcbn1cbmV4cG9ydCBjb25zdCBveiA9IHtcbiAgbmFtZTogXCJvelwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBjdXJyZW50SW5kZW50OiAwLFxuICAgICAgZG9JbkN1cnJlbnRMaW5lOiBmYWxzZSxcbiAgICAgIGhhc1Bhc3NlZEZpcnN0U3RhZ2U6IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkgc3RhdGUuZG9JbkN1cnJlbnRMaW5lID0gMDtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgdmFyIHRydWVUZXh0ID0gdGV4dEFmdGVyLnJlcGxhY2UoL15cXHMrfFxccyskL2csICcnKTtcbiAgICBpZiAodHJ1ZVRleHQubWF0Y2goZW5kS2V5d29yZHMpIHx8IHRydWVUZXh0Lm1hdGNoKG1pZGRsZUtleXdvcmRzKSB8fCB0cnVlVGV4dC5tYXRjaCgvKFxcW10pLykpIHJldHVybiBjeC51bml0ICogKHN0YXRlLmN1cnJlbnRJbmRlbnQgLSAxKTtcbiAgICBpZiAoc3RhdGUuY3VycmVudEluZGVudCA8IDApIHJldHVybiAwO1xuICAgIHJldHVybiBzdGF0ZS5jdXJyZW50SW5kZW50ICogY3gudW5pdDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgaW5kZW50T25JbnV0OiBidWlsZEVsZWN0cmljSW5wdXRSZWdFeCgpLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiJVwiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=