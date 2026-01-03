"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2322],{

/***/ 42322
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   mumps: () => (/* binding */ mumps)
/* harmony export */ });
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b", "i");
}
var singleOperators = new RegExp("^[\\+\\-\\*/&#!_?\\\\<>=\\'\\[\\]]");
var doubleOperators = new RegExp("^(('=)|(<=)|(>=)|('>)|('<)|([[)|(]])|(^$))");
var singleDelimiters = new RegExp("^[\\.,:]");
var brackets = new RegExp("[()]");
var identifiers = new RegExp("^[%A-Za-z][A-Za-z0-9]*");
var commandKeywords = ["break", "close", "do", "else", "for", "goto", "halt", "hang", "if", "job", "kill", "lock", "merge", "new", "open", "quit", "read", "set", "tcommit", "trollback", "tstart", "use", "view", "write", "xecute", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "q", "r", "s", "tc", "tro", "ts", "u", "v", "w", "x"];
// The following list includes intrinsic functions _and_ special variables
var intrinsicFuncsWords = ["\\$ascii", "\\$char", "\\$data", "\\$ecode", "\\$estack", "\\$etrap", "\\$extract", "\\$find", "\\$fnumber", "\\$get", "\\$horolog", "\\$io", "\\$increment", "\\$job", "\\$justify", "\\$length", "\\$name", "\\$next", "\\$order", "\\$piece", "\\$qlength", "\\$qsubscript", "\\$query", "\\$quit", "\\$random", "\\$reverse", "\\$select", "\\$stack", "\\$test", "\\$text", "\\$translate", "\\$view", "\\$x", "\\$y", "\\$a", "\\$c", "\\$d", "\\$e", "\\$ec", "\\$es", "\\$et", "\\$f", "\\$fn", "\\$g", "\\$h", "\\$i", "\\$j", "\\$l", "\\$n", "\\$na", "\\$o", "\\$p", "\\$q", "\\$ql", "\\$qs", "\\$r", "\\$re", "\\$s", "\\$st", "\\$t", "\\$tr", "\\$v", "\\$z"];
var intrinsicFuncs = wordRegexp(intrinsicFuncsWords);
var command = wordRegexp(commandKeywords);
function tokenBase(stream, state) {
  if (stream.sol()) {
    state.label = true;
    state.commandMode = 0;
  }

  // The <space> character has meaning in MUMPS. Ignoring consecutive
  // spaces would interfere with interpreting whether the next non-space
  // character belongs to the command or argument context.

  // Examine each character and update a mode variable whose interpretation is:
  //   >0 => command    0 => argument    <0 => command post-conditional
  var ch = stream.peek();
  if (ch == " " || ch == "\t") {
    // Pre-process <space>
    state.label = false;
    if (state.commandMode == 0) state.commandMode = 1;else if (state.commandMode < 0 || state.commandMode == 2) state.commandMode = 0;
  } else if (ch != "." && state.commandMode > 0) {
    if (ch == ":") state.commandMode = -1; // SIS - Command post-conditional
    else state.commandMode = 2;
  }

  // Do not color parameter list as line tag
  if (ch === "(" || ch === "\u0009") state.label = false;

  // MUMPS comment starts with ";"
  if (ch === ";") {
    stream.skipToEnd();
    return "comment";
  }

  // Number Literals // SIS/RLM - MUMPS permits canonic number followed by concatenate operator
  if (stream.match(/^[-+]?\d+(\.\d+)?([eE][-+]?\d+)?/)) return "number";

  // Handle Strings
  if (ch == '"') {
    if (stream.skipTo('"')) {
      stream.next();
      return "string";
    } else {
      stream.skipToEnd();
      return "error";
    }
  }

  // Handle operators and Delimiters
  if (stream.match(doubleOperators) || stream.match(singleOperators)) return "operator";

  // Prevents leading "." in DO block from falling through to error
  if (stream.match(singleDelimiters)) return null;
  if (brackets.test(ch)) {
    stream.next();
    return "bracket";
  }
  if (state.commandMode > 0 && stream.match(command)) return "controlKeyword";
  if (stream.match(intrinsicFuncs)) return "builtin";
  if (stream.match(identifiers)) return "variable";

  // Detect dollar-sign when not a documented intrinsic function
  // "^" may introduce a GVN or SSVN - Color same as function
  if (ch === "$" || ch === "^") {
    stream.next();
    return "builtin";
  }

  // MUMPS Indirection
  if (ch === "@") {
    stream.next();
    return "string.special";
  }
  if (/[\w%]/.test(ch)) {
    stream.eatWhile(/[\w%]/);
    return "variable";
  }

  // Handle non-detected items
  stream.next();
  return "error";
}
const mumps = {
  name: "mumps",
  startState: function () {
    return {
      label: false,
      commandMode: 0
    };
  },
  token: function (stream, state) {
    var style = tokenBase(stream, state);
    if (state.label) return "tag";
    return style;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjMyMi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvbXVtcHMuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZFJlZ2V4cCh3b3Jkcykge1xuICByZXR1cm4gbmV3IFJlZ0V4cChcIl4oKFwiICsgd29yZHMuam9pbihcIil8KFwiKSArIFwiKSlcXFxcYlwiLCBcImlcIik7XG59XG52YXIgc2luZ2xlT3BlcmF0b3JzID0gbmV3IFJlZ0V4cChcIl5bXFxcXCtcXFxcLVxcXFwqLyYjIV8/XFxcXFxcXFw8Pj1cXFxcJ1xcXFxbXFxcXF1dXCIpO1xudmFyIGRvdWJsZU9wZXJhdG9ycyA9IG5ldyBSZWdFeHAoXCJeKCgnPSl8KDw9KXwoPj0pfCgnPil8KCc8KXwoW1spfChdXSl8KF4kKSlcIik7XG52YXIgc2luZ2xlRGVsaW1pdGVycyA9IG5ldyBSZWdFeHAoXCJeW1xcXFwuLDpdXCIpO1xudmFyIGJyYWNrZXRzID0gbmV3IFJlZ0V4cChcIlsoKV1cIik7XG52YXIgaWRlbnRpZmllcnMgPSBuZXcgUmVnRXhwKFwiXlslQS1aYS16XVtBLVphLXowLTldKlwiKTtcbnZhciBjb21tYW5kS2V5d29yZHMgPSBbXCJicmVha1wiLCBcImNsb3NlXCIsIFwiZG9cIiwgXCJlbHNlXCIsIFwiZm9yXCIsIFwiZ290b1wiLCBcImhhbHRcIiwgXCJoYW5nXCIsIFwiaWZcIiwgXCJqb2JcIiwgXCJraWxsXCIsIFwibG9ja1wiLCBcIm1lcmdlXCIsIFwibmV3XCIsIFwib3BlblwiLCBcInF1aXRcIiwgXCJyZWFkXCIsIFwic2V0XCIsIFwidGNvbW1pdFwiLCBcInRyb2xsYmFja1wiLCBcInRzdGFydFwiLCBcInVzZVwiLCBcInZpZXdcIiwgXCJ3cml0ZVwiLCBcInhlY3V0ZVwiLCBcImJcIiwgXCJjXCIsIFwiZFwiLCBcImVcIiwgXCJmXCIsIFwiZ1wiLCBcImhcIiwgXCJpXCIsIFwialwiLCBcImtcIiwgXCJsXCIsIFwibVwiLCBcIm5cIiwgXCJvXCIsIFwicVwiLCBcInJcIiwgXCJzXCIsIFwidGNcIiwgXCJ0cm9cIiwgXCJ0c1wiLCBcInVcIiwgXCJ2XCIsIFwid1wiLCBcInhcIl07XG4vLyBUaGUgZm9sbG93aW5nIGxpc3QgaW5jbHVkZXMgaW50cmluc2ljIGZ1bmN0aW9ucyBfYW5kXyBzcGVjaWFsIHZhcmlhYmxlc1xudmFyIGludHJpbnNpY0Z1bmNzV29yZHMgPSBbXCJcXFxcJGFzY2lpXCIsIFwiXFxcXCRjaGFyXCIsIFwiXFxcXCRkYXRhXCIsIFwiXFxcXCRlY29kZVwiLCBcIlxcXFwkZXN0YWNrXCIsIFwiXFxcXCRldHJhcFwiLCBcIlxcXFwkZXh0cmFjdFwiLCBcIlxcXFwkZmluZFwiLCBcIlxcXFwkZm51bWJlclwiLCBcIlxcXFwkZ2V0XCIsIFwiXFxcXCRob3JvbG9nXCIsIFwiXFxcXCRpb1wiLCBcIlxcXFwkaW5jcmVtZW50XCIsIFwiXFxcXCRqb2JcIiwgXCJcXFxcJGp1c3RpZnlcIiwgXCJcXFxcJGxlbmd0aFwiLCBcIlxcXFwkbmFtZVwiLCBcIlxcXFwkbmV4dFwiLCBcIlxcXFwkb3JkZXJcIiwgXCJcXFxcJHBpZWNlXCIsIFwiXFxcXCRxbGVuZ3RoXCIsIFwiXFxcXCRxc3Vic2NyaXB0XCIsIFwiXFxcXCRxdWVyeVwiLCBcIlxcXFwkcXVpdFwiLCBcIlxcXFwkcmFuZG9tXCIsIFwiXFxcXCRyZXZlcnNlXCIsIFwiXFxcXCRzZWxlY3RcIiwgXCJcXFxcJHN0YWNrXCIsIFwiXFxcXCR0ZXN0XCIsIFwiXFxcXCR0ZXh0XCIsIFwiXFxcXCR0cmFuc2xhdGVcIiwgXCJcXFxcJHZpZXdcIiwgXCJcXFxcJHhcIiwgXCJcXFxcJHlcIiwgXCJcXFxcJGFcIiwgXCJcXFxcJGNcIiwgXCJcXFxcJGRcIiwgXCJcXFxcJGVcIiwgXCJcXFxcJGVjXCIsIFwiXFxcXCRlc1wiLCBcIlxcXFwkZXRcIiwgXCJcXFxcJGZcIiwgXCJcXFxcJGZuXCIsIFwiXFxcXCRnXCIsIFwiXFxcXCRoXCIsIFwiXFxcXCRpXCIsIFwiXFxcXCRqXCIsIFwiXFxcXCRsXCIsIFwiXFxcXCRuXCIsIFwiXFxcXCRuYVwiLCBcIlxcXFwkb1wiLCBcIlxcXFwkcFwiLCBcIlxcXFwkcVwiLCBcIlxcXFwkcWxcIiwgXCJcXFxcJHFzXCIsIFwiXFxcXCRyXCIsIFwiXFxcXCRyZVwiLCBcIlxcXFwkc1wiLCBcIlxcXFwkc3RcIiwgXCJcXFxcJHRcIiwgXCJcXFxcJHRyXCIsIFwiXFxcXCR2XCIsIFwiXFxcXCR6XCJdO1xudmFyIGludHJpbnNpY0Z1bmNzID0gd29yZFJlZ2V4cChpbnRyaW5zaWNGdW5jc1dvcmRzKTtcbnZhciBjb21tYW5kID0gd29yZFJlZ2V4cChjb21tYW5kS2V5d29yZHMpO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgIHN0YXRlLmxhYmVsID0gdHJ1ZTtcbiAgICBzdGF0ZS5jb21tYW5kTW9kZSA9IDA7XG4gIH1cblxuICAvLyBUaGUgPHNwYWNlPiBjaGFyYWN0ZXIgaGFzIG1lYW5pbmcgaW4gTVVNUFMuIElnbm9yaW5nIGNvbnNlY3V0aXZlXG4gIC8vIHNwYWNlcyB3b3VsZCBpbnRlcmZlcmUgd2l0aCBpbnRlcnByZXRpbmcgd2hldGhlciB0aGUgbmV4dCBub24tc3BhY2VcbiAgLy8gY2hhcmFjdGVyIGJlbG9uZ3MgdG8gdGhlIGNvbW1hbmQgb3IgYXJndW1lbnQgY29udGV4dC5cblxuICAvLyBFeGFtaW5lIGVhY2ggY2hhcmFjdGVyIGFuZCB1cGRhdGUgYSBtb2RlIHZhcmlhYmxlIHdob3NlIGludGVycHJldGF0aW9uIGlzOlxuICAvLyAgID4wID0+IGNvbW1hbmQgICAgMCA9PiBhcmd1bWVudCAgICA8MCA9PiBjb21tYW5kIHBvc3QtY29uZGl0aW9uYWxcbiAgdmFyIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgaWYgKGNoID09IFwiIFwiIHx8IGNoID09IFwiXFx0XCIpIHtcbiAgICAvLyBQcmUtcHJvY2VzcyA8c3BhY2U+XG4gICAgc3RhdGUubGFiZWwgPSBmYWxzZTtcbiAgICBpZiAoc3RhdGUuY29tbWFuZE1vZGUgPT0gMCkgc3RhdGUuY29tbWFuZE1vZGUgPSAxO2Vsc2UgaWYgKHN0YXRlLmNvbW1hbmRNb2RlIDwgMCB8fCBzdGF0ZS5jb21tYW5kTW9kZSA9PSAyKSBzdGF0ZS5jb21tYW5kTW9kZSA9IDA7XG4gIH0gZWxzZSBpZiAoY2ggIT0gXCIuXCIgJiYgc3RhdGUuY29tbWFuZE1vZGUgPiAwKSB7XG4gICAgaWYgKGNoID09IFwiOlwiKSBzdGF0ZS5jb21tYW5kTW9kZSA9IC0xOyAvLyBTSVMgLSBDb21tYW5kIHBvc3QtY29uZGl0aW9uYWxcbiAgICBlbHNlIHN0YXRlLmNvbW1hbmRNb2RlID0gMjtcbiAgfVxuXG4gIC8vIERvIG5vdCBjb2xvciBwYXJhbWV0ZXIgbGlzdCBhcyBsaW5lIHRhZ1xuICBpZiAoY2ggPT09IFwiKFwiIHx8IGNoID09PSBcIlxcdTAwMDlcIikgc3RhdGUubGFiZWwgPSBmYWxzZTtcblxuICAvLyBNVU1QUyBjb21tZW50IHN0YXJ0cyB3aXRoIFwiO1wiXG4gIGlmIChjaCA9PT0gXCI7XCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG5cbiAgLy8gTnVtYmVyIExpdGVyYWxzIC8vIFNJUy9STE0gLSBNVU1QUyBwZXJtaXRzIGNhbm9uaWMgbnVtYmVyIGZvbGxvd2VkIGJ5IGNvbmNhdGVuYXRlIG9wZXJhdG9yXG4gIGlmIChzdHJlYW0ubWF0Y2goL15bLStdP1xcZCsoXFwuXFxkKyk/KFtlRV1bLStdP1xcZCspPy8pKSByZXR1cm4gXCJudW1iZXJcIjtcblxuICAvLyBIYW5kbGUgU3RyaW5nc1xuICBpZiAoY2ggPT0gJ1wiJykge1xuICAgIGlmIChzdHJlYW0uc2tpcFRvKCdcIicpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImVycm9yXCI7XG4gICAgfVxuICB9XG5cbiAgLy8gSGFuZGxlIG9wZXJhdG9ycyBhbmQgRGVsaW1pdGVyc1xuICBpZiAoc3RyZWFtLm1hdGNoKGRvdWJsZU9wZXJhdG9ycykgfHwgc3RyZWFtLm1hdGNoKHNpbmdsZU9wZXJhdG9ycykpIHJldHVybiBcIm9wZXJhdG9yXCI7XG5cbiAgLy8gUHJldmVudHMgbGVhZGluZyBcIi5cIiBpbiBETyBibG9jayBmcm9tIGZhbGxpbmcgdGhyb3VnaCB0byBlcnJvclxuICBpZiAoc3RyZWFtLm1hdGNoKHNpbmdsZURlbGltaXRlcnMpKSByZXR1cm4gbnVsbDtcbiAgaWYgKGJyYWNrZXRzLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gIH1cbiAgaWYgKHN0YXRlLmNvbW1hbmRNb2RlID4gMCAmJiBzdHJlYW0ubWF0Y2goY29tbWFuZCkpIHJldHVybiBcImNvbnRyb2xLZXl3b3JkXCI7XG4gIGlmIChzdHJlYW0ubWF0Y2goaW50cmluc2ljRnVuY3MpKSByZXR1cm4gXCJidWlsdGluXCI7XG4gIGlmIChzdHJlYW0ubWF0Y2goaWRlbnRpZmllcnMpKSByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuXG4gIC8vIERldGVjdCBkb2xsYXItc2lnbiB3aGVuIG5vdCBhIGRvY3VtZW50ZWQgaW50cmluc2ljIGZ1bmN0aW9uXG4gIC8vIFwiXlwiIG1heSBpbnRyb2R1Y2UgYSBHVk4gb3IgU1NWTiAtIENvbG9yIHNhbWUgYXMgZnVuY3Rpb25cbiAgaWYgKGNoID09PSBcIiRcIiB8fCBjaCA9PT0gXCJeXCIpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgfVxuXG4gIC8vIE1VTVBTIEluZGlyZWN0aW9uXG4gIGlmIChjaCA9PT0gXCJAXCIpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBcInN0cmluZy5zcGVjaWFsXCI7XG4gIH1cbiAgaWYgKC9bXFx3JV0vLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3JV0vKTtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9XG5cbiAgLy8gSGFuZGxlIG5vbi1kZXRlY3RlZCBpdGVtc1xuICBzdHJlYW0ubmV4dCgpO1xuICByZXR1cm4gXCJlcnJvclwiO1xufVxuZXhwb3J0IGNvbnN0IG11bXBzID0ge1xuICBuYW1lOiBcIm11bXBzXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgbGFiZWw6IGZhbHNlLFxuICAgICAgY29tbWFuZE1vZGU6IDBcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgc3R5bGUgPSB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0YXRlLmxhYmVsKSByZXR1cm4gXCJ0YWdcIjtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==