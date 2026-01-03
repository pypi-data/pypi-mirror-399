"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9997],{

/***/ 19997
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   apl: () => (/* binding */ apl)
/* harmony export */ });
var builtInFuncs = {
  "+": ["conjugate", "add"],
  "−": ["negate", "subtract"],
  "×": ["signOf", "multiply"],
  "÷": ["reciprocal", "divide"],
  "⌈": ["ceiling", "greaterOf"],
  "⌊": ["floor", "lesserOf"],
  "∣": ["absolute", "residue"],
  "⍳": ["indexGenerate", "indexOf"],
  "?": ["roll", "deal"],
  "⋆": ["exponentiate", "toThePowerOf"],
  "⍟": ["naturalLog", "logToTheBase"],
  "○": ["piTimes", "circularFuncs"],
  "!": ["factorial", "binomial"],
  "⌹": ["matrixInverse", "matrixDivide"],
  "<": [null, "lessThan"],
  "≤": [null, "lessThanOrEqual"],
  "=": [null, "equals"],
  ">": [null, "greaterThan"],
  "≥": [null, "greaterThanOrEqual"],
  "≠": [null, "notEqual"],
  "≡": ["depth", "match"],
  "≢": [null, "notMatch"],
  "∈": ["enlist", "membership"],
  "⍷": [null, "find"],
  "∪": ["unique", "union"],
  "∩": [null, "intersection"],
  "∼": ["not", "without"],
  "∨": [null, "or"],
  "∧": [null, "and"],
  "⍱": [null, "nor"],
  "⍲": [null, "nand"],
  "⍴": ["shapeOf", "reshape"],
  ",": ["ravel", "catenate"],
  "⍪": [null, "firstAxisCatenate"],
  "⌽": ["reverse", "rotate"],
  "⊖": ["axis1Reverse", "axis1Rotate"],
  "⍉": ["transpose", null],
  "↑": ["first", "take"],
  "↓": [null, "drop"],
  "⊂": ["enclose", "partitionWithAxis"],
  "⊃": ["diclose", "pick"],
  "⌷": [null, "index"],
  "⍋": ["gradeUp", null],
  "⍒": ["gradeDown", null],
  "⊤": ["encode", null],
  "⊥": ["decode", null],
  "⍕": ["format", "formatByExample"],
  "⍎": ["execute", null],
  "⊣": ["stop", "left"],
  "⊢": ["pass", "right"]
};
var isOperator = /[\.\/⌿⍀¨⍣]/;
var isNiladic = /⍬/;
var isFunction = /[\+−×÷⌈⌊∣⍳\?⋆⍟○!⌹<≤=>≥≠≡≢∈⍷∪∩∼∨∧⍱⍲⍴,⍪⌽⊖⍉↑↓⊂⊃⌷⍋⍒⊤⊥⍕⍎⊣⊢]/;
var isArrow = /←/;
var isComment = /[⍝#].*$/;
var stringEater = function (type) {
  var prev;
  prev = false;
  return function (c) {
    prev = c;
    if (c === type) {
      return prev === "\\";
    }
    return true;
  };
};
const apl = {
  name: "apl",
  startState: function () {
    return {
      prev: false,
      func: false,
      op: false,
      string: false,
      escape: false
    };
  },
  token: function (stream, state) {
    var ch;
    if (stream.eatSpace()) {
      return null;
    }
    ch = stream.next();
    if (ch === '"' || ch === "'") {
      stream.eatWhile(stringEater(ch));
      stream.next();
      state.prev = true;
      return "string";
    }
    if (/[\[{\(]/.test(ch)) {
      state.prev = false;
      return null;
    }
    if (/[\]}\)]/.test(ch)) {
      state.prev = true;
      return null;
    }
    if (isNiladic.test(ch)) {
      state.prev = false;
      return "atom";
    }
    if (/[¯\d]/.test(ch)) {
      if (state.func) {
        state.func = false;
        state.prev = false;
      } else {
        state.prev = true;
      }
      stream.eatWhile(/[\w\.]/);
      return "number";
    }
    if (isOperator.test(ch)) {
      return "operator";
    }
    if (isArrow.test(ch)) {
      return "operator";
    }
    if (isFunction.test(ch)) {
      state.func = true;
      state.prev = false;
      return builtInFuncs[ch] ? "variableName.function.standard" : "variableName.function";
    }
    if (isComment.test(ch)) {
      stream.skipToEnd();
      return "comment";
    }
    if (ch === "∘" && stream.peek() === ".") {
      stream.next();
      return "variableName.function";
    }
    stream.eatWhile(/[\w\$_]/);
    state.prev = true;
    return "keyword";
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTk5Ny5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9hcGwuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIGJ1aWx0SW5GdW5jcyA9IHtcbiAgXCIrXCI6IFtcImNvbmp1Z2F0ZVwiLCBcImFkZFwiXSxcbiAgXCLiiJJcIjogW1wibmVnYXRlXCIsIFwic3VidHJhY3RcIl0sXG4gIFwiw5dcIjogW1wic2lnbk9mXCIsIFwibXVsdGlwbHlcIl0sXG4gIFwiw7dcIjogW1wicmVjaXByb2NhbFwiLCBcImRpdmlkZVwiXSxcbiAgXCLijIhcIjogW1wiY2VpbGluZ1wiLCBcImdyZWF0ZXJPZlwiXSxcbiAgXCLijIpcIjogW1wiZmxvb3JcIiwgXCJsZXNzZXJPZlwiXSxcbiAgXCLiiKNcIjogW1wiYWJzb2x1dGVcIiwgXCJyZXNpZHVlXCJdLFxuICBcIuKNs1wiOiBbXCJpbmRleEdlbmVyYXRlXCIsIFwiaW5kZXhPZlwiXSxcbiAgXCI/XCI6IFtcInJvbGxcIiwgXCJkZWFsXCJdLFxuICBcIuKLhlwiOiBbXCJleHBvbmVudGlhdGVcIiwgXCJ0b1RoZVBvd2VyT2ZcIl0sXG4gIFwi4o2fXCI6IFtcIm5hdHVyYWxMb2dcIiwgXCJsb2dUb1RoZUJhc2VcIl0sXG4gIFwi4peLXCI6IFtcInBpVGltZXNcIiwgXCJjaXJjdWxhckZ1bmNzXCJdLFxuICBcIiFcIjogW1wiZmFjdG9yaWFsXCIsIFwiYmlub21pYWxcIl0sXG4gIFwi4oy5XCI6IFtcIm1hdHJpeEludmVyc2VcIiwgXCJtYXRyaXhEaXZpZGVcIl0sXG4gIFwiPFwiOiBbbnVsbCwgXCJsZXNzVGhhblwiXSxcbiAgXCLiiaRcIjogW251bGwsIFwibGVzc1RoYW5PckVxdWFsXCJdLFxuICBcIj1cIjogW251bGwsIFwiZXF1YWxzXCJdLFxuICBcIj5cIjogW251bGwsIFwiZ3JlYXRlclRoYW5cIl0sXG4gIFwi4omlXCI6IFtudWxsLCBcImdyZWF0ZXJUaGFuT3JFcXVhbFwiXSxcbiAgXCLiiaBcIjogW251bGwsIFwibm90RXF1YWxcIl0sXG4gIFwi4omhXCI6IFtcImRlcHRoXCIsIFwibWF0Y2hcIl0sXG4gIFwi4omiXCI6IFtudWxsLCBcIm5vdE1hdGNoXCJdLFxuICBcIuKIiFwiOiBbXCJlbmxpc3RcIiwgXCJtZW1iZXJzaGlwXCJdLFxuICBcIuKNt1wiOiBbbnVsbCwgXCJmaW5kXCJdLFxuICBcIuKIqlwiOiBbXCJ1bmlxdWVcIiwgXCJ1bmlvblwiXSxcbiAgXCLiiKlcIjogW251bGwsIFwiaW50ZXJzZWN0aW9uXCJdLFxuICBcIuKIvFwiOiBbXCJub3RcIiwgXCJ3aXRob3V0XCJdLFxuICBcIuKIqFwiOiBbbnVsbCwgXCJvclwiXSxcbiAgXCLiiKdcIjogW251bGwsIFwiYW5kXCJdLFxuICBcIuKNsVwiOiBbbnVsbCwgXCJub3JcIl0sXG4gIFwi4o2yXCI6IFtudWxsLCBcIm5hbmRcIl0sXG4gIFwi4o20XCI6IFtcInNoYXBlT2ZcIiwgXCJyZXNoYXBlXCJdLFxuICBcIixcIjogW1wicmF2ZWxcIiwgXCJjYXRlbmF0ZVwiXSxcbiAgXCLijapcIjogW251bGwsIFwiZmlyc3RBeGlzQ2F0ZW5hdGVcIl0sXG4gIFwi4oy9XCI6IFtcInJldmVyc2VcIiwgXCJyb3RhdGVcIl0sXG4gIFwi4oqWXCI6IFtcImF4aXMxUmV2ZXJzZVwiLCBcImF4aXMxUm90YXRlXCJdLFxuICBcIuKNiVwiOiBbXCJ0cmFuc3Bvc2VcIiwgbnVsbF0sXG4gIFwi4oaRXCI6IFtcImZpcnN0XCIsIFwidGFrZVwiXSxcbiAgXCLihpNcIjogW251bGwsIFwiZHJvcFwiXSxcbiAgXCLiioJcIjogW1wiZW5jbG9zZVwiLCBcInBhcnRpdGlvbldpdGhBeGlzXCJdLFxuICBcIuKKg1wiOiBbXCJkaWNsb3NlXCIsIFwicGlja1wiXSxcbiAgXCLijLdcIjogW251bGwsIFwiaW5kZXhcIl0sXG4gIFwi4o2LXCI6IFtcImdyYWRlVXBcIiwgbnVsbF0sXG4gIFwi4o2SXCI6IFtcImdyYWRlRG93blwiLCBudWxsXSxcbiAgXCLiiqRcIjogW1wiZW5jb2RlXCIsIG51bGxdLFxuICBcIuKKpVwiOiBbXCJkZWNvZGVcIiwgbnVsbF0sXG4gIFwi4o2VXCI6IFtcImZvcm1hdFwiLCBcImZvcm1hdEJ5RXhhbXBsZVwiXSxcbiAgXCLijY5cIjogW1wiZXhlY3V0ZVwiLCBudWxsXSxcbiAgXCLiiqNcIjogW1wic3RvcFwiLCBcImxlZnRcIl0sXG4gIFwi4oqiXCI6IFtcInBhc3NcIiwgXCJyaWdodFwiXVxufTtcbnZhciBpc09wZXJhdG9yID0gL1tcXC5cXC/ijL/ijYDCqOKNo10vO1xudmFyIGlzTmlsYWRpYyA9IC/ijawvO1xudmFyIGlzRnVuY3Rpb24gPSAvW1xcK+KIksOXw7fijIjijIriiKPijbNcXD/ii4bijZ/il4sh4oy5POKJpD0+4oml4omg4omh4omi4oiI4o234oiq4oip4oi84oio4oin4o2x4o2y4o20LOKNquKMveKKluKNieKGkeKGk+KKguKKg+KMt+KNi+KNkuKKpOKKpeKNleKNjuKKo+KKol0vO1xudmFyIGlzQXJyb3cgPSAv4oaQLztcbnZhciBpc0NvbW1lbnQgPSAvW+KNnSNdLiokLztcbnZhciBzdHJpbmdFYXRlciA9IGZ1bmN0aW9uICh0eXBlKSB7XG4gIHZhciBwcmV2O1xuICBwcmV2ID0gZmFsc2U7XG4gIHJldHVybiBmdW5jdGlvbiAoYykge1xuICAgIHByZXYgPSBjO1xuICAgIGlmIChjID09PSB0eXBlKSB7XG4gICAgICByZXR1cm4gcHJldiA9PT0gXCJcXFxcXCI7XG4gICAgfVxuICAgIHJldHVybiB0cnVlO1xuICB9O1xufTtcbmV4cG9ydCBjb25zdCBhcGwgPSB7XG4gIG5hbWU6IFwiYXBsXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgcHJldjogZmFsc2UsXG4gICAgICBmdW5jOiBmYWxzZSxcbiAgICAgIG9wOiBmYWxzZSxcbiAgICAgIHN0cmluZzogZmFsc2UsXG4gICAgICBlc2NhcGU6IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoO1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoY2ggPT09ICdcIicgfHwgY2ggPT09IFwiJ1wiKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoc3RyaW5nRWF0ZXIoY2gpKTtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS5wcmV2ID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIH1cbiAgICBpZiAoL1tcXFt7XFwoXS8udGVzdChjaCkpIHtcbiAgICAgIHN0YXRlLnByZXYgPSBmYWxzZTtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICBpZiAoL1tcXF19XFwpXS8udGVzdChjaCkpIHtcbiAgICAgIHN0YXRlLnByZXYgPSB0cnVlO1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIGlmIChpc05pbGFkaWMudGVzdChjaCkpIHtcbiAgICAgIHN0YXRlLnByZXYgPSBmYWxzZTtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9XG4gICAgaWYgKC9bwq9cXGRdLy50ZXN0KGNoKSkge1xuICAgICAgaWYgKHN0YXRlLmZ1bmMpIHtcbiAgICAgICAgc3RhdGUuZnVuYyA9IGZhbHNlO1xuICAgICAgICBzdGF0ZS5wcmV2ID0gZmFsc2U7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBzdGF0ZS5wcmV2ID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLl0vKTtcbiAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgIH1cbiAgICBpZiAoaXNPcGVyYXRvci50ZXN0KGNoKSkge1xuICAgICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICB9XG4gICAgaWYgKGlzQXJyb3cudGVzdChjaCkpIHtcbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfVxuICAgIGlmIChpc0Z1bmN0aW9uLnRlc3QoY2gpKSB7XG4gICAgICBzdGF0ZS5mdW5jID0gdHJ1ZTtcbiAgICAgIHN0YXRlLnByZXYgPSBmYWxzZTtcbiAgICAgIHJldHVybiBidWlsdEluRnVuY3NbY2hdID8gXCJ2YXJpYWJsZU5hbWUuZnVuY3Rpb24uc3RhbmRhcmRcIiA6IFwidmFyaWFibGVOYW1lLmZ1bmN0aW9uXCI7XG4gICAgfVxuICAgIGlmIChpc0NvbW1lbnQudGVzdChjaCkpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKGNoID09PSBcIuKImFwiICYmIHN0cmVhbS5wZWVrKCkgPT09IFwiLlwiKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwidmFyaWFibGVOYW1lLmZ1bmN0aW9uXCI7XG4gICAgfVxuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF9dLyk7XG4gICAgc3RhdGUucHJldiA9IHRydWU7XG4gICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=