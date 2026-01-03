"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[4020],{

/***/ 94020
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   spreadsheet: () => (/* binding */ spreadsheet)
/* harmony export */ });
const spreadsheet = {
  name: "spreadsheet",
  startState: function () {
    return {
      stringType: null,
      stack: []
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
        state.stack.unshift("string");
      }
    }

    //return state
    //stack has
    switch (state.stack[0]) {
      case "string":
        while (state.stack[0] === "string" && !stream.eol()) {
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
        return "string";
      case "characterClass":
        while (state.stack[0] === "characterClass" && !stream.eol()) {
          if (!(stream.match(/^[^\]\\]+/) || stream.match(/^\\./))) state.stack.shift();
        }
        return "operator";
    }
    var peek = stream.peek();

    //no stack
    switch (peek) {
      case "[":
        stream.next();
        state.stack.unshift("characterClass");
        return "bracket";
      case ":":
        stream.next();
        return "operator";
      case "\\":
        if (stream.match(/\\[a-z]+/)) return "string.special";else {
          stream.next();
          return "atom";
        }
      case ".":
      case ",":
      case ";":
      case "*":
      case "-":
      case "+":
      case "^":
      case "<":
      case "/":
      case "=":
        stream.next();
        return "atom";
      case "$":
        stream.next();
        return "builtin";
    }
    if (stream.match(/\d+/)) {
      if (stream.match(/^\w+/)) return "error";
      return "number";
    } else if (stream.match(/^[a-zA-Z_]\w*/)) {
      if (stream.match(/(?=[\(.])/, false)) return "keyword";
      return "variable";
    } else if (["[", "]", "(", ")", "{", "}"].indexOf(peek) != -1) {
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNDAyMC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3NwcmVhZHNoZWV0LmpzIl0sInNvdXJjZXNDb250ZW50IjpbImV4cG9ydCBjb25zdCBzcHJlYWRzaGVldCA9IHtcbiAgbmFtZTogXCJzcHJlYWRzaGVldFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHN0cmluZ1R5cGU6IG51bGwsXG4gICAgICBzdGFjazogW11cbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoIXN0cmVhbSkgcmV0dXJuO1xuXG4gICAgLy9jaGVjayBmb3Igc3RhdGUgY2hhbmdlc1xuICAgIGlmIChzdGF0ZS5zdGFjay5sZW5ndGggPT09IDApIHtcbiAgICAgIC8vc3RyaW5nc1xuICAgICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJ1wiJyB8fCBzdHJlYW0ucGVlaygpID09IFwiJ1wiKSB7XG4gICAgICAgIHN0YXRlLnN0cmluZ1R5cGUgPSBzdHJlYW0ucGVlaygpO1xuICAgICAgICBzdHJlYW0ubmV4dCgpOyAvLyBTa2lwIHF1b3RlXG4gICAgICAgIHN0YXRlLnN0YWNrLnVuc2hpZnQoXCJzdHJpbmdcIik7XG4gICAgICB9XG4gICAgfVxuXG4gICAgLy9yZXR1cm4gc3RhdGVcbiAgICAvL3N0YWNrIGhhc1xuICAgIHN3aXRjaCAoc3RhdGUuc3RhY2tbMF0pIHtcbiAgICAgIGNhc2UgXCJzdHJpbmdcIjpcbiAgICAgICAgd2hpbGUgKHN0YXRlLnN0YWNrWzBdID09PSBcInN0cmluZ1wiICYmICFzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gc3RhdGUuc3RyaW5nVHlwZSkge1xuICAgICAgICAgICAgc3RyZWFtLm5leHQoKTsgLy8gU2tpcCBxdW90ZVxuICAgICAgICAgICAgc3RhdGUuc3RhY2suc2hpZnQoKTsgLy8gQ2xlYXIgZmxhZ1xuICAgICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gXCJcXFxcXCIpIHtcbiAgICAgICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICBzdHJlYW0ubWF0Y2goL14uW15cXFxcXFxcIlxcJ10qLyk7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgICAgY2FzZSBcImNoYXJhY3RlckNsYXNzXCI6XG4gICAgICAgIHdoaWxlIChzdGF0ZS5zdGFja1swXSA9PT0gXCJjaGFyYWN0ZXJDbGFzc1wiICYmICFzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgICBpZiAoIShzdHJlYW0ubWF0Y2goL15bXlxcXVxcXFxdKy8pIHx8IHN0cmVhbS5tYXRjaCgvXlxcXFwuLykpKSBzdGF0ZS5zdGFjay5zaGlmdCgpO1xuICAgICAgICB9XG4gICAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfVxuICAgIHZhciBwZWVrID0gc3RyZWFtLnBlZWsoKTtcblxuICAgIC8vbm8gc3RhY2tcbiAgICBzd2l0Y2ggKHBlZWspIHtcbiAgICAgIGNhc2UgXCJbXCI6XG4gICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgIHN0YXRlLnN0YWNrLnVuc2hpZnQoXCJjaGFyYWN0ZXJDbGFzc1wiKTtcbiAgICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgICAgY2FzZSBcIjpcIjpcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICAgIGNhc2UgXCJcXFxcXCI6XG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goL1xcXFxbYS16XSsvKSkgcmV0dXJuIFwic3RyaW5nLnNwZWNpYWxcIjtlbHNlIHtcbiAgICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICAgICAgfVxuICAgICAgY2FzZSBcIi5cIjpcbiAgICAgIGNhc2UgXCIsXCI6XG4gICAgICBjYXNlIFwiO1wiOlxuICAgICAgY2FzZSBcIipcIjpcbiAgICAgIGNhc2UgXCItXCI6XG4gICAgICBjYXNlIFwiK1wiOlxuICAgICAgY2FzZSBcIl5cIjpcbiAgICAgIGNhc2UgXCI8XCI6XG4gICAgICBjYXNlIFwiL1wiOlxuICAgICAgY2FzZSBcIj1cIjpcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgcmV0dXJuIFwiYXRvbVwiO1xuICAgICAgY2FzZSBcIiRcIjpcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgcmV0dXJuIFwiYnVpbHRpblwiO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9cXGQrLykpIHtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL15cXHcrLykpIHJldHVybiBcImVycm9yXCI7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXlthLXpBLVpfXVxcdyovKSkge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvKD89W1xcKC5dKS8sIGZhbHNlKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgICB9IGVsc2UgaWYgKFtcIltcIiwgXCJdXCIsIFwiKFwiLCBcIilcIiwgXCJ7XCIsIFwifVwiXS5pbmRleE9mKHBlZWspICE9IC0xKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgIH0gZWxzZSBpZiAoIXN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICByZXR1cm4gbnVsbDtcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9