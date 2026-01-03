"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1171],{

/***/ 81171
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ebnf: () => (/* binding */ ebnf)
/* harmony export */ });
var commentType = {
  slash: 0,
  parenthesis: 1
};
var stateType = {
  comment: 0,
  _string: 1,
  characterClass: 2
};
const ebnf = {
  name: "ebnf",
  startState: function () {
    return {
      stringType: null,
      commentType: null,
      braced: 0,
      lhs: true,
      localState: null,
      stack: [],
      inDefinition: false
    };
  },
  token: function (stream, state) {
    if (!stream) return;

    //check for state changes
    if (state.stack.length === 0) {
      //strings
      if (stream.peek() == '"' || stream.peek() == "'") {
        state.stringType = stream.peek();
        stream.next(); // Skip quote
        state.stack.unshift(stateType._string);
      } else if (stream.match('/*')) {
        //comments starting with /*
        state.stack.unshift(stateType.comment);
        state.commentType = commentType.slash;
      } else if (stream.match('(*')) {
        //comments starting with (*
        state.stack.unshift(stateType.comment);
        state.commentType = commentType.parenthesis;
      }
    }

    //return state
    //stack has
    switch (state.stack[0]) {
      case stateType._string:
        while (state.stack[0] === stateType._string && !stream.eol()) {
          if (stream.peek() === state.stringType) {
            stream.next(); // Skip quote
            state.stack.shift(); // Clear flag
          } else if (stream.peek() === "\\") {
            stream.next();
            stream.next();
          } else {
            stream.match(/^.[^\\\"\']*/);
          }
        }
        return state.lhs ? "property" : "string";
      // Token style

      case stateType.comment:
        while (state.stack[0] === stateType.comment && !stream.eol()) {
          if (state.commentType === commentType.slash && stream.match('*/')) {
            state.stack.shift(); // Clear flag
            state.commentType = null;
          } else if (state.commentType === commentType.parenthesis && stream.match('*)')) {
            state.stack.shift(); // Clear flag
            state.commentType = null;
          } else {
            stream.match(/^.[^\*]*/);
          }
        }
        return "comment";
      case stateType.characterClass:
        while (state.stack[0] === stateType.characterClass && !stream.eol()) {
          if (!(stream.match(/^[^\]\\]+/) || stream.match('.'))) {
            state.stack.shift();
          }
        }
        return "operator";
    }
    var peek = stream.peek();

    //no stack
    switch (peek) {
      case "[":
        stream.next();
        state.stack.unshift(stateType.characterClass);
        return "bracket";
      case ":":
      case "|":
      case ";":
        stream.next();
        return "operator";
      case "%":
        if (stream.match("%%")) {
          return "header";
        } else if (stream.match(/[%][A-Za-z]+/)) {
          return "keyword";
        } else if (stream.match(/[%][}]/)) {
          return "bracket";
        }
        break;
      case "/":
        if (stream.match(/[\/][A-Za-z]+/)) {
          return "keyword";
        }
      case "\\":
        if (stream.match(/[\][a-z]+/)) {
          return "string.special";
        }
      case ".":
        if (stream.match(".")) {
          return "atom";
        }
      case "*":
      case "-":
      case "+":
      case "^":
        if (stream.match(peek)) {
          return "atom";
        }
      case "$":
        if (stream.match("$$")) {
          return "builtin";
        } else if (stream.match(/[$][0-9]+/)) {
          return "variableName.special";
        }
      case "<":
        if (stream.match(/<<[a-zA-Z_]+>>/)) {
          return "builtin";
        }
    }
    if (stream.match('//')) {
      stream.skipToEnd();
      return "comment";
    } else if (stream.match('return')) {
      return "operator";
    } else if (stream.match(/^[a-zA-Z_][a-zA-Z0-9_]*/)) {
      if (stream.match(/(?=[\(.])/)) {
        return "variable";
      } else if (stream.match(/(?=[\s\n]*[:=])/)) {
        return "def";
      }
      return "variableName.special";
    } else if (["[", "]", "(", ")"].indexOf(stream.peek()) != -1) {
      stream.next();
      return "bracket";
    } else if (!stream.eatSpace()) {
      stream.next();
    }
    return null;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTE3MS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9lYm5mLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBjb21tZW50VHlwZSA9IHtcbiAgc2xhc2g6IDAsXG4gIHBhcmVudGhlc2lzOiAxXG59O1xudmFyIHN0YXRlVHlwZSA9IHtcbiAgY29tbWVudDogMCxcbiAgX3N0cmluZzogMSxcbiAgY2hhcmFjdGVyQ2xhc3M6IDJcbn07XG5leHBvcnQgY29uc3QgZWJuZiA9IHtcbiAgbmFtZTogXCJlYm5mXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgc3RyaW5nVHlwZTogbnVsbCxcbiAgICAgIGNvbW1lbnRUeXBlOiBudWxsLFxuICAgICAgYnJhY2VkOiAwLFxuICAgICAgbGhzOiB0cnVlLFxuICAgICAgbG9jYWxTdGF0ZTogbnVsbCxcbiAgICAgIHN0YWNrOiBbXSxcbiAgICAgIGluRGVmaW5pdGlvbjogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoIXN0cmVhbSkgcmV0dXJuO1xuXG4gICAgLy9jaGVjayBmb3Igc3RhdGUgY2hhbmdlc1xuICAgIGlmIChzdGF0ZS5zdGFjay5sZW5ndGggPT09IDApIHtcbiAgICAgIC8vc3RyaW5nc1xuICAgICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJ1wiJyB8fCBzdHJlYW0ucGVlaygpID09IFwiJ1wiKSB7XG4gICAgICAgIHN0YXRlLnN0cmluZ1R5cGUgPSBzdHJlYW0ucGVlaygpO1xuICAgICAgICBzdHJlYW0ubmV4dCgpOyAvLyBTa2lwIHF1b3RlXG4gICAgICAgIHN0YXRlLnN0YWNrLnVuc2hpZnQoc3RhdGVUeXBlLl9zdHJpbmcpO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goJy8qJykpIHtcbiAgICAgICAgLy9jb21tZW50cyBzdGFydGluZyB3aXRoIC8qXG4gICAgICAgIHN0YXRlLnN0YWNrLnVuc2hpZnQoc3RhdGVUeXBlLmNvbW1lbnQpO1xuICAgICAgICBzdGF0ZS5jb21tZW50VHlwZSA9IGNvbW1lbnRUeXBlLnNsYXNoO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goJygqJykpIHtcbiAgICAgICAgLy9jb21tZW50cyBzdGFydGluZyB3aXRoICgqXG4gICAgICAgIHN0YXRlLnN0YWNrLnVuc2hpZnQoc3RhdGVUeXBlLmNvbW1lbnQpO1xuICAgICAgICBzdGF0ZS5jb21tZW50VHlwZSA9IGNvbW1lbnRUeXBlLnBhcmVudGhlc2lzO1xuICAgICAgfVxuICAgIH1cblxuICAgIC8vcmV0dXJuIHN0YXRlXG4gICAgLy9zdGFjayBoYXNcbiAgICBzd2l0Y2ggKHN0YXRlLnN0YWNrWzBdKSB7XG4gICAgICBjYXNlIHN0YXRlVHlwZS5fc3RyaW5nOlxuICAgICAgICB3aGlsZSAoc3RhdGUuc3RhY2tbMF0gPT09IHN0YXRlVHlwZS5fc3RyaW5nICYmICFzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gc3RhdGUuc3RyaW5nVHlwZSkge1xuICAgICAgICAgICAgc3RyZWFtLm5leHQoKTsgLy8gU2tpcCBxdW90ZVxuICAgICAgICAgICAgc3RhdGUuc3RhY2suc2hpZnQoKTsgLy8gQ2xlYXIgZmxhZ1xuICAgICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gXCJcXFxcXCIpIHtcbiAgICAgICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBzdHJlYW0ubWF0Y2goL14uW15cXFxcXFxcIlxcJ10qLyk7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHJldHVybiBzdGF0ZS5saHMgPyBcInByb3BlcnR5XCIgOiBcInN0cmluZ1wiO1xuICAgICAgLy8gVG9rZW4gc3R5bGVcblxuICAgICAgY2FzZSBzdGF0ZVR5cGUuY29tbWVudDpcbiAgICAgICAgd2hpbGUgKHN0YXRlLnN0YWNrWzBdID09PSBzdGF0ZVR5cGUuY29tbWVudCAmJiAhc3RyZWFtLmVvbCgpKSB7XG4gICAgICAgICAgaWYgKHN0YXRlLmNvbW1lbnRUeXBlID09PSBjb21tZW50VHlwZS5zbGFzaCAmJiBzdHJlYW0ubWF0Y2goJyovJykpIHtcbiAgICAgICAgICAgIHN0YXRlLnN0YWNrLnNoaWZ0KCk7IC8vIENsZWFyIGZsYWdcbiAgICAgICAgICAgIHN0YXRlLmNvbW1lbnRUeXBlID0gbnVsbDtcbiAgICAgICAgICB9IGVsc2UgaWYgKHN0YXRlLmNvbW1lbnRUeXBlID09PSBjb21tZW50VHlwZS5wYXJlbnRoZXNpcyAmJiBzdHJlYW0ubWF0Y2goJyopJykpIHtcbiAgICAgICAgICAgIHN0YXRlLnN0YWNrLnNoaWZ0KCk7IC8vIENsZWFyIGZsYWdcbiAgICAgICAgICAgIHN0YXRlLmNvbW1lbnRUeXBlID0gbnVsbDtcbiAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgc3RyZWFtLm1hdGNoKC9eLlteXFwqXSovKTtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgICAgY2FzZSBzdGF0ZVR5cGUuY2hhcmFjdGVyQ2xhc3M6XG4gICAgICAgIHdoaWxlIChzdGF0ZS5zdGFja1swXSA9PT0gc3RhdGVUeXBlLmNoYXJhY3RlckNsYXNzICYmICFzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgICBpZiAoIShzdHJlYW0ubWF0Y2goL15bXlxcXVxcXFxdKy8pIHx8IHN0cmVhbS5tYXRjaCgnLicpKSkge1xuICAgICAgICAgICAgc3RhdGUuc3RhY2suc2hpZnQoKTtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICB9XG4gICAgdmFyIHBlZWsgPSBzdHJlYW0ucGVlaygpO1xuXG4gICAgLy9ubyBzdGFja1xuICAgIHN3aXRjaCAocGVlaykge1xuICAgICAgY2FzZSBcIltcIjpcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgc3RhdGUuc3RhY2sudW5zaGlmdChzdGF0ZVR5cGUuY2hhcmFjdGVyQ2xhc3MpO1xuICAgICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgICBjYXNlIFwiOlwiOlxuICAgICAgY2FzZSBcInxcIjpcbiAgICAgIGNhc2UgXCI7XCI6XG4gICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgICBjYXNlIFwiJVwiOlxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKFwiJSVcIikpIHtcbiAgICAgICAgICByZXR1cm4gXCJoZWFkZXJcIjtcbiAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL1slXVtBLVphLXpdKy8pKSB7XG4gICAgICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvWyVdW31dLykpIHtcbiAgICAgICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgICAgIH1cbiAgICAgICAgYnJlYWs7XG4gICAgICBjYXNlIFwiL1wiOlxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKC9bXFwvXVtBLVphLXpdKy8pKSB7XG4gICAgICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgICAgICB9XG4gICAgICBjYXNlIFwiXFxcXFwiOlxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKC9bXFxdW2Etel0rLykpIHtcbiAgICAgICAgICByZXR1cm4gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICAgICAgICB9XG4gICAgICBjYXNlIFwiLlwiOlxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKFwiLlwiKSkge1xuICAgICAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICAgICAgfVxuICAgICAgY2FzZSBcIipcIjpcbiAgICAgIGNhc2UgXCItXCI6XG4gICAgICBjYXNlIFwiK1wiOlxuICAgICAgY2FzZSBcIl5cIjpcbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChwZWVrKSkge1xuICAgICAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICAgICAgfVxuICAgICAgY2FzZSBcIiRcIjpcbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChcIiQkXCIpKSB7XG4gICAgICAgICAgcmV0dXJuIFwiYnVpbHRpblwiO1xuICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvWyRdWzAtOV0rLykpIHtcbiAgICAgICAgICByZXR1cm4gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgICAgICB9XG4gICAgICBjYXNlIFwiPFwiOlxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKC88PFthLXpBLVpfXSs+Pi8pKSB7XG4gICAgICAgICAgcmV0dXJuIFwiYnVpbHRpblwiO1xuICAgICAgICB9XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goJy8vJykpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgncmV0dXJuJykpIHtcbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL15bYS16QS1aX11bYS16QS1aMC05X10qLykpIHtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goLyg/PVtcXCguXSkvKSkge1xuICAgICAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goLyg/PVtcXHNcXG5dKls6PV0pLykpIHtcbiAgICAgICAgcmV0dXJuIFwiZGVmXCI7XG4gICAgICB9XG4gICAgICByZXR1cm4gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIH0gZWxzZSBpZiAoW1wiW1wiLCBcIl1cIiwgXCIoXCIsIFwiKVwiXS5pbmRleE9mKHN0cmVhbS5wZWVrKCkpICE9IC0xKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgIH0gZWxzZSBpZiAoIXN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICByZXR1cm4gbnVsbDtcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9