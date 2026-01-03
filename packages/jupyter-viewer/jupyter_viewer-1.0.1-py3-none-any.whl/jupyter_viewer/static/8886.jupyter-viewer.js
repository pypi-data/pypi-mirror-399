"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[8886],{

/***/ 8886
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   mathematica: () => (/* binding */ mathematica)
/* harmony export */ });
// used pattern building blocks
var Identifier = '[a-zA-Z\\$][a-zA-Z0-9\\$]*';
var pBase = "(?:\\d+)";
var pFloat = "(?:\\.\\d+|\\d+\\.\\d*|\\d+)";
var pFloatBase = "(?:\\.\\w+|\\w+\\.\\w*|\\w+)";
var pPrecision = "(?:`(?:`?" + pFloat + ")?)";

// regular expressions
var reBaseForm = new RegExp('(?:' + pBase + '(?:\\^\\^' + pFloatBase + pPrecision + '?(?:\\*\\^[+-]?\\d+)?))');
var reFloatForm = new RegExp('(?:' + pFloat + pPrecision + '?(?:\\*\\^[+-]?\\d+)?)');
var reIdInContext = new RegExp('(?:`?)(?:' + Identifier + ')(?:`(?:' + Identifier + '))*(?:`?)');
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
  if (ch === '(') {
    if (stream.eat('*')) {
      state.commentLevel++;
      state.tokenize = tokenComment;
      return state.tokenize(stream, state);
    }
  }

  // go back one character
  stream.backUp(1);

  // look for numbers
  // Numbers in a baseform
  if (stream.match(reBaseForm, true, false)) {
    return 'number';
  }

  // Mathematica numbers. Floats (1.2, .2, 1.) can have optionally a precision (`float) or an accuracy definition
  // (``float). Note: while 1.2` is possible 1.2`` is not. At the end an exponent (float*^+12) can follow.
  if (stream.match(reFloatForm, true, false)) {
    return 'number';
  }

  /* In[23] and Out[34] */
  if (stream.match(/(?:In|Out)\[[0-9]*\]/, true, false)) {
    return 'atom';
  }

  // usage
  if (stream.match(/([a-zA-Z\$][a-zA-Z0-9\$]*(?:`[a-zA-Z0-9\$]+)*::usage)/, true, false)) {
    return 'meta';
  }

  // message
  if (stream.match(/([a-zA-Z\$][a-zA-Z0-9\$]*(?:`[a-zA-Z0-9\$]+)*::[a-zA-Z\$][a-zA-Z0-9\$]*):?/, true, false)) {
    return 'string.special';
  }

  // this makes a look-ahead match for something like variable:{_Integer}
  // the match is then forwarded to the mma-patterns tokenizer.
  if (stream.match(/([a-zA-Z\$][a-zA-Z0-9\$]*\s*:)(?:(?:[a-zA-Z\$][a-zA-Z0-9\$]*)|(?:[^:=>~@\^\&\*\)\[\]'\?,\|])).*/, true, false)) {
    return 'variableName.special';
  }

  // catch variables which are used together with Blank (_), BlankSequence (__) or BlankNullSequence (___)
  // Cannot start with a number, but can have numbers at any other position. Examples
  // blub__Integer, a1_, b34_Integer32
  if (stream.match(/[a-zA-Z\$][a-zA-Z0-9\$]*_+[a-zA-Z\$][a-zA-Z0-9\$]*/, true, false)) {
    return 'variableName.special';
  }
  if (stream.match(/[a-zA-Z\$][a-zA-Z0-9\$]*_+/, true, false)) {
    return 'variableName.special';
  }
  if (stream.match(/_+[a-zA-Z\$][a-zA-Z0-9\$]*/, true, false)) {
    return 'variableName.special';
  }

  // Named characters in Mathematica, like \[Gamma].
  if (stream.match(/\\\[[a-zA-Z\$][a-zA-Z0-9\$]*\]/, true, false)) {
    return 'character';
  }

  // Match all braces separately
  if (stream.match(/(?:\[|\]|{|}|\(|\))/, true, false)) {
    return 'bracket';
  }

  // Catch Slots (#, ##, #3, ##9 and the V10 named slots #name). I have never seen someone using more than one digit after #, so we match
  // only one.
  if (stream.match(/(?:#[a-zA-Z\$][a-zA-Z0-9\$]*|#+[0-9]?)/, true, false)) {
    return 'variableName.constant';
  }

  // Literals like variables, keywords, functions
  if (stream.match(reIdInContext, true, false)) {
    return 'keyword';
  }

  // operators. Note that operators like @@ or /; are matched separately for each symbol.
  if (stream.match(/(?:\\|\+|\-|\*|\/|,|;|\.|:|@|~|=|>|<|&|\||_|`|'|\^|\?|!|%)/, true, false)) {
    return 'operator';
  }

  // everything else is an error
  stream.next(); // advance the stream.
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
  while (state.commentLevel > 0 && (next = stream.next()) != null) {
    if (prev === '(' && next === '*') state.commentLevel++;
    if (prev === '*' && next === ')') state.commentLevel--;
    prev = next;
  }
  if (state.commentLevel <= 0) {
    state.tokenize = tokenBase;
  }
  return 'comment';
}
const mathematica = {
  name: "mathematica",
  startState: function () {
    return {
      tokenize: tokenBase,
      commentLevel: 0
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return state.tokenize(stream, state);
  },
  languageData: {
    commentTokens: {
      block: {
        open: "(*",
        close: "*)"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiODg4Ni5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9tYXRoZW1hdGljYS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyB1c2VkIHBhdHRlcm4gYnVpbGRpbmcgYmxvY2tzXG52YXIgSWRlbnRpZmllciA9ICdbYS16QS1aXFxcXCRdW2EtekEtWjAtOVxcXFwkXSonO1xudmFyIHBCYXNlID0gXCIoPzpcXFxcZCspXCI7XG52YXIgcEZsb2F0ID0gXCIoPzpcXFxcLlxcXFxkK3xcXFxcZCtcXFxcLlxcXFxkKnxcXFxcZCspXCI7XG52YXIgcEZsb2F0QmFzZSA9IFwiKD86XFxcXC5cXFxcdyt8XFxcXHcrXFxcXC5cXFxcdyp8XFxcXHcrKVwiO1xudmFyIHBQcmVjaXNpb24gPSBcIig/OmAoPzpgP1wiICsgcEZsb2F0ICsgXCIpPylcIjtcblxuLy8gcmVndWxhciBleHByZXNzaW9uc1xudmFyIHJlQmFzZUZvcm0gPSBuZXcgUmVnRXhwKCcoPzonICsgcEJhc2UgKyAnKD86XFxcXF5cXFxcXicgKyBwRmxvYXRCYXNlICsgcFByZWNpc2lvbiArICc/KD86XFxcXCpcXFxcXlsrLV0/XFxcXGQrKT8pKScpO1xudmFyIHJlRmxvYXRGb3JtID0gbmV3IFJlZ0V4cCgnKD86JyArIHBGbG9hdCArIHBQcmVjaXNpb24gKyAnPyg/OlxcXFwqXFxcXF5bKy1dP1xcXFxkKyk/KScpO1xudmFyIHJlSWRJbkNvbnRleHQgPSBuZXcgUmVnRXhwKCcoPzpgPykoPzonICsgSWRlbnRpZmllciArICcpKD86YCg/OicgKyBJZGVudGlmaWVyICsgJykpKig/OmA/KScpO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoO1xuXG4gIC8vIGdldCBuZXh0IGNoYXJhY3RlclxuICBjaCA9IHN0cmVhbS5uZXh0KCk7XG5cbiAgLy8gc3RyaW5nXG4gIGlmIChjaCA9PT0gJ1wiJykge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmc7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG5cbiAgLy8gY29tbWVudFxuICBpZiAoY2ggPT09ICcoJykge1xuICAgIGlmIChzdHJlYW0uZWF0KCcqJykpIHtcbiAgICAgIHN0YXRlLmNvbW1lbnRMZXZlbCsrO1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnQ7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICB9XG5cbiAgLy8gZ28gYmFjayBvbmUgY2hhcmFjdGVyXG4gIHN0cmVhbS5iYWNrVXAoMSk7XG5cbiAgLy8gbG9vayBmb3IgbnVtYmVyc1xuICAvLyBOdW1iZXJzIGluIGEgYmFzZWZvcm1cbiAgaWYgKHN0cmVhbS5tYXRjaChyZUJhc2VGb3JtLCB0cnVlLCBmYWxzZSkpIHtcbiAgICByZXR1cm4gJ251bWJlcic7XG4gIH1cblxuICAvLyBNYXRoZW1hdGljYSBudW1iZXJzLiBGbG9hdHMgKDEuMiwgLjIsIDEuKSBjYW4gaGF2ZSBvcHRpb25hbGx5IGEgcHJlY2lzaW9uIChgZmxvYXQpIG9yIGFuIGFjY3VyYWN5IGRlZmluaXRpb25cbiAgLy8gKGBgZmxvYXQpLiBOb3RlOiB3aGlsZSAxLjJgIGlzIHBvc3NpYmxlIDEuMmBgIGlzIG5vdC4gQXQgdGhlIGVuZCBhbiBleHBvbmVudCAoZmxvYXQqXisxMikgY2FuIGZvbGxvdy5cbiAgaWYgKHN0cmVhbS5tYXRjaChyZUZsb2F0Rm9ybSwgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICdudW1iZXInO1xuICB9XG5cbiAgLyogSW5bMjNdIGFuZCBPdXRbMzRdICovXG4gIGlmIChzdHJlYW0ubWF0Y2goLyg/OklufE91dClcXFtbMC05XSpcXF0vLCB0cnVlLCBmYWxzZSkpIHtcbiAgICByZXR1cm4gJ2F0b20nO1xuICB9XG5cbiAgLy8gdXNhZ2VcbiAgaWYgKHN0cmVhbS5tYXRjaCgvKFthLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qKD86YFthLXpBLVowLTlcXCRdKykqOjp1c2FnZSkvLCB0cnVlLCBmYWxzZSkpIHtcbiAgICByZXR1cm4gJ21ldGEnO1xuICB9XG5cbiAgLy8gbWVzc2FnZVxuICBpZiAoc3RyZWFtLm1hdGNoKC8oW2EtekEtWlxcJF1bYS16QS1aMC05XFwkXSooPzpgW2EtekEtWjAtOVxcJF0rKSo6OlthLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qKTo/LywgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICdzdHJpbmcuc3BlY2lhbCc7XG4gIH1cblxuICAvLyB0aGlzIG1ha2VzIGEgbG9vay1haGVhZCBtYXRjaCBmb3Igc29tZXRoaW5nIGxpa2UgdmFyaWFibGU6e19JbnRlZ2VyfVxuICAvLyB0aGUgbWF0Y2ggaXMgdGhlbiBmb3J3YXJkZWQgdG8gdGhlIG1tYS1wYXR0ZXJucyB0b2tlbml6ZXIuXG4gIGlmIChzdHJlYW0ubWF0Y2goLyhbYS16QS1aXFwkXVthLXpBLVowLTlcXCRdKlxccyo6KSg/Oig/OlthLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qKXwoPzpbXjo9Pn5AXFxeXFwmXFwqXFwpXFxbXFxdJ1xcPyxcXHxdKSkuKi8sIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAndmFyaWFibGVOYW1lLnNwZWNpYWwnO1xuICB9XG5cbiAgLy8gY2F0Y2ggdmFyaWFibGVzIHdoaWNoIGFyZSB1c2VkIHRvZ2V0aGVyIHdpdGggQmxhbmsgKF8pLCBCbGFua1NlcXVlbmNlIChfXykgb3IgQmxhbmtOdWxsU2VxdWVuY2UgKF9fXylcbiAgLy8gQ2Fubm90IHN0YXJ0IHdpdGggYSBudW1iZXIsIGJ1dCBjYW4gaGF2ZSBudW1iZXJzIGF0IGFueSBvdGhlciBwb3NpdGlvbi4gRXhhbXBsZXNcbiAgLy8gYmx1Yl9fSW50ZWdlciwgYTFfLCBiMzRfSW50ZWdlcjMyXG4gIGlmIChzdHJlYW0ubWF0Y2goL1thLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qXytbYS16QS1aXFwkXVthLXpBLVowLTlcXCRdKi8sIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAndmFyaWFibGVOYW1lLnNwZWNpYWwnO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goL1thLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qXysvLCB0cnVlLCBmYWxzZSkpIHtcbiAgICByZXR1cm4gJ3ZhcmlhYmxlTmFtZS5zcGVjaWFsJztcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKC9fK1thLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qLywgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICd2YXJpYWJsZU5hbWUuc3BlY2lhbCc7XG4gIH1cblxuICAvLyBOYW1lZCBjaGFyYWN0ZXJzIGluIE1hdGhlbWF0aWNhLCBsaWtlIFxcW0dhbW1hXS5cbiAgaWYgKHN0cmVhbS5tYXRjaCgvXFxcXFxcW1thLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qXFxdLywgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICdjaGFyYWN0ZXInO1xuICB9XG5cbiAgLy8gTWF0Y2ggYWxsIGJyYWNlcyBzZXBhcmF0ZWx5XG4gIGlmIChzdHJlYW0ubWF0Y2goLyg/OlxcW3xcXF18e3x9fFxcKHxcXCkpLywgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICdicmFja2V0JztcbiAgfVxuXG4gIC8vIENhdGNoIFNsb3RzICgjLCAjIywgIzMsICMjOSBhbmQgdGhlIFYxMCBuYW1lZCBzbG90cyAjbmFtZSkuIEkgaGF2ZSBuZXZlciBzZWVuIHNvbWVvbmUgdXNpbmcgbW9yZSB0aGFuIG9uZSBkaWdpdCBhZnRlciAjLCBzbyB3ZSBtYXRjaFxuICAvLyBvbmx5IG9uZS5cbiAgaWYgKHN0cmVhbS5tYXRjaCgvKD86I1thLXpBLVpcXCRdW2EtekEtWjAtOVxcJF0qfCMrWzAtOV0/KS8sIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAndmFyaWFibGVOYW1lLmNvbnN0YW50JztcbiAgfVxuXG4gIC8vIExpdGVyYWxzIGxpa2UgdmFyaWFibGVzLCBrZXl3b3JkcywgZnVuY3Rpb25zXG4gIGlmIChzdHJlYW0ubWF0Y2gocmVJZEluQ29udGV4dCwgdHJ1ZSwgZmFsc2UpKSB7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuXG4gIC8vIG9wZXJhdG9ycy4gTm90ZSB0aGF0IG9wZXJhdG9ycyBsaWtlIEBAIG9yIC87IGFyZSBtYXRjaGVkIHNlcGFyYXRlbHkgZm9yIGVhY2ggc3ltYm9sLlxuICBpZiAoc3RyZWFtLm1hdGNoKC8oPzpcXFxcfFxcK3xcXC18XFwqfFxcL3wsfDt8XFwufDp8QHx+fD18Pnw8fCZ8XFx8fF98YHwnfFxcXnxcXD98IXwlKS8sIHRydWUsIGZhbHNlKSkge1xuICAgIHJldHVybiAnb3BlcmF0b3InO1xuICB9XG5cbiAgLy8gZXZlcnl0aGluZyBlbHNlIGlzIGFuIGVycm9yXG4gIHN0cmVhbS5uZXh0KCk7IC8vIGFkdmFuY2UgdGhlIHN0cmVhbS5cbiAgcmV0dXJuICdlcnJvcic7XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBuZXh0LFxuICAgIGVuZCA9IGZhbHNlLFxuICAgIGVzY2FwZWQgPSBmYWxzZTtcbiAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgIGlmIChuZXh0ID09PSAnXCInICYmICFlc2NhcGVkKSB7XG4gICAgICBlbmQgPSB0cnVlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09PSAnXFxcXCc7XG4gIH1cbiAgaWYgKGVuZCAmJiAhZXNjYXBlZCkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICB9XG4gIHJldHVybiAnc3RyaW5nJztcbn1cbjtcbmZ1bmN0aW9uIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBwcmV2LCBuZXh0O1xuICB3aGlsZSAoc3RhdGUuY29tbWVudExldmVsID4gMCAmJiAobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAocHJldiA9PT0gJygnICYmIG5leHQgPT09ICcqJykgc3RhdGUuY29tbWVudExldmVsKys7XG4gICAgaWYgKHByZXYgPT09ICcqJyAmJiBuZXh0ID09PSAnKScpIHN0YXRlLmNvbW1lbnRMZXZlbC0tO1xuICAgIHByZXYgPSBuZXh0O1xuICB9XG4gIGlmIChzdGF0ZS5jb21tZW50TGV2ZWwgPD0gMCkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICB9XG4gIHJldHVybiAnY29tbWVudCc7XG59XG5leHBvcnQgY29uc3QgbWF0aGVtYXRpY2EgPSB7XG4gIG5hbWU6IFwibWF0aGVtYXRpY2FcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgY29tbWVudExldmVsOiAwXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiKCpcIixcbiAgICAgICAgY2xvc2U6IFwiKilcIlxuICAgICAgfVxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9