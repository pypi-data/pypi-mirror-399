"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1887],{

/***/ 91887
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   cypher: () => (/* binding */ cypher)
/* harmony export */ });
var wordRegexp = function (words) {
  return new RegExp("^(?:" + words.join("|") + ")$", "i");
};
var tokenBase = function (stream /*, state*/) {
  curPunc = null;
  var ch = stream.next();
  if (ch === '"') {
    stream.match(/^.*?"/);
    return "string";
  }
  if (ch === "'") {
    stream.match(/^.*?'/);
    return "string";
  }
  if (/[{}\(\),\.;\[\]]/.test(ch)) {
    curPunc = ch;
    return "punctuation";
  } else if (ch === "/" && stream.eat("/")) {
    stream.skipToEnd();
    return "comment";
  } else if (operatorChars.test(ch)) {
    stream.eatWhile(operatorChars);
    return null;
  } else {
    stream.eatWhile(/[_\w\d]/);
    if (stream.eat(":")) {
      stream.eatWhile(/[\w\d_\-]/);
      return "atom";
    }
    var word = stream.current();
    if (funcs.test(word)) return "builtin";
    if (preds.test(word)) return "def";
    if (keywords.test(word) || systemKeywords.test(word)) return "keyword";
    return "variable";
  }
};
var pushContext = function (state, type, col) {
  return state.context = {
    prev: state.context,
    indent: state.indent,
    col: col,
    type: type
  };
};
var popContext = function (state) {
  state.indent = state.context.indent;
  return state.context = state.context.prev;
};
var curPunc;
var funcs = wordRegexp(["abs", "acos", "allShortestPaths", "asin", "atan", "atan2", "avg", "ceil", "coalesce", "collect", "cos", "cot", "count", "degrees", "e", "endnode", "exp", "extract", "filter", "floor", "haversin", "head", "id", "keys", "labels", "last", "left", "length", "log", "log10", "lower", "ltrim", "max", "min", "node", "nodes", "percentileCont", "percentileDisc", "pi", "radians", "rand", "range", "reduce", "rel", "relationship", "relationships", "replace", "reverse", "right", "round", "rtrim", "shortestPath", "sign", "sin", "size", "split", "sqrt", "startnode", "stdev", "stdevp", "str", "substring", "sum", "tail", "tan", "timestamp", "toFloat", "toInt", "toString", "trim", "type", "upper"]);
var preds = wordRegexp(["all", "and", "any", "contains", "exists", "has", "in", "none", "not", "or", "single", "xor"]);
var keywords = wordRegexp(["as", "asc", "ascending", "assert", "by", "case", "commit", "constraint", "create", "csv", "cypher", "delete", "desc", "descending", "detach", "distinct", "drop", "else", "end", "ends", "explain", "false", "fieldterminator", "foreach", "from", "headers", "in", "index", "is", "join", "limit", "load", "match", "merge", "null", "on", "optional", "order", "periodic", "profile", "remove", "return", "scan", "set", "skip", "start", "starts", "then", "true", "union", "unique", "unwind", "using", "when", "where", "with", "call", "yield"]);
var systemKeywords = wordRegexp(["access", "active", "assign", "all", "alter", "as", "catalog", "change", "copy", "create", "constraint", "constraints", "current", "database", "databases", "dbms", "default", "deny", "drop", "element", "elements", "exists", "from", "grant", "graph", "graphs", "if", "index", "indexes", "label", "labels", "management", "match", "name", "names", "new", "node", "nodes", "not", "of", "on", "or", "password", "populated", "privileges", "property", "read", "relationship", "relationships", "remove", "replace", "required", "revoke", "role", "roles", "set", "show", "start", "status", "stop", "suspended", "to", "traverse", "type", "types", "user", "users", "with", "write"]);
var operatorChars = /[*+\-<>=&|~%^]/;
const cypher = {
  name: "cypher",
  startState: function () {
    return {
      tokenize: tokenBase,
      context: null,
      indent: 0,
      col: 0
    };
  },
  token: function (stream, state) {
    if (stream.sol()) {
      if (state.context && state.context.align == null) {
        state.context.align = false;
      }
      state.indent = stream.indentation();
    }
    if (stream.eatSpace()) {
      return null;
    }
    var style = state.tokenize(stream, state);
    if (style !== "comment" && state.context && state.context.align == null && state.context.type !== "pattern") {
      state.context.align = true;
    }
    if (curPunc === "(") {
      pushContext(state, ")", stream.column());
    } else if (curPunc === "[") {
      pushContext(state, "]", stream.column());
    } else if (curPunc === "{") {
      pushContext(state, "}", stream.column());
    } else if (/[\]\}\)]/.test(curPunc)) {
      while (state.context && state.context.type === "pattern") {
        popContext(state);
      }
      if (state.context && curPunc === state.context.type) {
        popContext(state);
      }
    } else if (curPunc === "." && state.context && state.context.type === "pattern") {
      popContext(state);
    } else if (/atom|string|variable/.test(style) && state.context) {
      if (/[\}\]]/.test(state.context.type)) {
        pushContext(state, "pattern", stream.column());
      } else if (state.context.type === "pattern" && !state.context.align) {
        state.context.align = true;
        state.context.col = stream.column();
      }
    }
    return style;
  },
  indent: function (state, textAfter, cx) {
    var firstChar = textAfter && textAfter.charAt(0);
    var context = state.context;
    if (/[\]\}]/.test(firstChar)) {
      while (context && context.type === "pattern") {
        context = context.prev;
      }
    }
    var closing = context && firstChar === context.type;
    if (!context) return 0;
    if (context.type === "keywords") return null;
    if (context.align) return context.col + (closing ? 0 : 1);
    return context.indent + (closing ? 0 : cx.unit);
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTg4Ny5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvY3lwaGVyLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciB3b3JkUmVnZXhwID0gZnVuY3Rpb24gKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXig/OlwiICsgd29yZHMuam9pbihcInxcIikgKyBcIikkXCIsIFwiaVwiKTtcbn07XG52YXIgdG9rZW5CYXNlID0gZnVuY3Rpb24gKHN0cmVhbSAvKiwgc3RhdGUqLykge1xuICBjdXJQdW5jID0gbnVsbDtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGNoID09PSAnXCInKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9eLio/XCIvKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfVxuICBpZiAoY2ggPT09IFwiJ1wiKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9eLio/Jy8pO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9XG4gIGlmICgvW3t9XFwoXFwpLFxcLjtcXFtcXF1dLy50ZXN0KGNoKSkge1xuICAgIGN1clB1bmMgPSBjaDtcbiAgICByZXR1cm4gXCJwdW5jdHVhdGlvblwiO1xuICB9IGVsc2UgaWYgKGNoID09PSBcIi9cIiAmJiBzdHJlYW0uZWF0KFwiL1wiKSkge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAob3BlcmF0b3JDaGFycy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShvcGVyYXRvckNoYXJzKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfSBlbHNlIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tfXFx3XFxkXS8pO1xuICAgIGlmIChzdHJlYW0uZWF0KFwiOlwiKSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFxkX1xcLV0vKTtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9XG4gICAgdmFyIHdvcmQgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgIGlmIChmdW5jcy50ZXN0KHdvcmQpKSByZXR1cm4gXCJidWlsdGluXCI7XG4gICAgaWYgKHByZWRzLnRlc3Qod29yZCkpIHJldHVybiBcImRlZlwiO1xuICAgIGlmIChrZXl3b3Jkcy50ZXN0KHdvcmQpIHx8IHN5c3RlbUtleXdvcmRzLnRlc3Qod29yZCkpIHJldHVybiBcImtleXdvcmRcIjtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9XG59O1xudmFyIHB1c2hDb250ZXh0ID0gZnVuY3Rpb24gKHN0YXRlLCB0eXBlLCBjb2wpIHtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSB7XG4gICAgcHJldjogc3RhdGUuY29udGV4dCxcbiAgICBpbmRlbnQ6IHN0YXRlLmluZGVudCxcbiAgICBjb2w6IGNvbCxcbiAgICB0eXBlOiB0eXBlXG4gIH07XG59O1xudmFyIHBvcENvbnRleHQgPSBmdW5jdGlvbiAoc3RhdGUpIHtcbiAgc3RhdGUuaW5kZW50ID0gc3RhdGUuY29udGV4dC5pbmRlbnQ7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gc3RhdGUuY29udGV4dC5wcmV2O1xufTtcbnZhciBjdXJQdW5jO1xudmFyIGZ1bmNzID0gd29yZFJlZ2V4cChbXCJhYnNcIiwgXCJhY29zXCIsIFwiYWxsU2hvcnRlc3RQYXRoc1wiLCBcImFzaW5cIiwgXCJhdGFuXCIsIFwiYXRhbjJcIiwgXCJhdmdcIiwgXCJjZWlsXCIsIFwiY29hbGVzY2VcIiwgXCJjb2xsZWN0XCIsIFwiY29zXCIsIFwiY290XCIsIFwiY291bnRcIiwgXCJkZWdyZWVzXCIsIFwiZVwiLCBcImVuZG5vZGVcIiwgXCJleHBcIiwgXCJleHRyYWN0XCIsIFwiZmlsdGVyXCIsIFwiZmxvb3JcIiwgXCJoYXZlcnNpblwiLCBcImhlYWRcIiwgXCJpZFwiLCBcImtleXNcIiwgXCJsYWJlbHNcIiwgXCJsYXN0XCIsIFwibGVmdFwiLCBcImxlbmd0aFwiLCBcImxvZ1wiLCBcImxvZzEwXCIsIFwibG93ZXJcIiwgXCJsdHJpbVwiLCBcIm1heFwiLCBcIm1pblwiLCBcIm5vZGVcIiwgXCJub2Rlc1wiLCBcInBlcmNlbnRpbGVDb250XCIsIFwicGVyY2VudGlsZURpc2NcIiwgXCJwaVwiLCBcInJhZGlhbnNcIiwgXCJyYW5kXCIsIFwicmFuZ2VcIiwgXCJyZWR1Y2VcIiwgXCJyZWxcIiwgXCJyZWxhdGlvbnNoaXBcIiwgXCJyZWxhdGlvbnNoaXBzXCIsIFwicmVwbGFjZVwiLCBcInJldmVyc2VcIiwgXCJyaWdodFwiLCBcInJvdW5kXCIsIFwicnRyaW1cIiwgXCJzaG9ydGVzdFBhdGhcIiwgXCJzaWduXCIsIFwic2luXCIsIFwic2l6ZVwiLCBcInNwbGl0XCIsIFwic3FydFwiLCBcInN0YXJ0bm9kZVwiLCBcInN0ZGV2XCIsIFwic3RkZXZwXCIsIFwic3RyXCIsIFwic3Vic3RyaW5nXCIsIFwic3VtXCIsIFwidGFpbFwiLCBcInRhblwiLCBcInRpbWVzdGFtcFwiLCBcInRvRmxvYXRcIiwgXCJ0b0ludFwiLCBcInRvU3RyaW5nXCIsIFwidHJpbVwiLCBcInR5cGVcIiwgXCJ1cHBlclwiXSk7XG52YXIgcHJlZHMgPSB3b3JkUmVnZXhwKFtcImFsbFwiLCBcImFuZFwiLCBcImFueVwiLCBcImNvbnRhaW5zXCIsIFwiZXhpc3RzXCIsIFwiaGFzXCIsIFwiaW5cIiwgXCJub25lXCIsIFwibm90XCIsIFwib3JcIiwgXCJzaW5nbGVcIiwgXCJ4b3JcIl0pO1xudmFyIGtleXdvcmRzID0gd29yZFJlZ2V4cChbXCJhc1wiLCBcImFzY1wiLCBcImFzY2VuZGluZ1wiLCBcImFzc2VydFwiLCBcImJ5XCIsIFwiY2FzZVwiLCBcImNvbW1pdFwiLCBcImNvbnN0cmFpbnRcIiwgXCJjcmVhdGVcIiwgXCJjc3ZcIiwgXCJjeXBoZXJcIiwgXCJkZWxldGVcIiwgXCJkZXNjXCIsIFwiZGVzY2VuZGluZ1wiLCBcImRldGFjaFwiLCBcImRpc3RpbmN0XCIsIFwiZHJvcFwiLCBcImVsc2VcIiwgXCJlbmRcIiwgXCJlbmRzXCIsIFwiZXhwbGFpblwiLCBcImZhbHNlXCIsIFwiZmllbGR0ZXJtaW5hdG9yXCIsIFwiZm9yZWFjaFwiLCBcImZyb21cIiwgXCJoZWFkZXJzXCIsIFwiaW5cIiwgXCJpbmRleFwiLCBcImlzXCIsIFwiam9pblwiLCBcImxpbWl0XCIsIFwibG9hZFwiLCBcIm1hdGNoXCIsIFwibWVyZ2VcIiwgXCJudWxsXCIsIFwib25cIiwgXCJvcHRpb25hbFwiLCBcIm9yZGVyXCIsIFwicGVyaW9kaWNcIiwgXCJwcm9maWxlXCIsIFwicmVtb3ZlXCIsIFwicmV0dXJuXCIsIFwic2NhblwiLCBcInNldFwiLCBcInNraXBcIiwgXCJzdGFydFwiLCBcInN0YXJ0c1wiLCBcInRoZW5cIiwgXCJ0cnVlXCIsIFwidW5pb25cIiwgXCJ1bmlxdWVcIiwgXCJ1bndpbmRcIiwgXCJ1c2luZ1wiLCBcIndoZW5cIiwgXCJ3aGVyZVwiLCBcIndpdGhcIiwgXCJjYWxsXCIsIFwieWllbGRcIl0pO1xudmFyIHN5c3RlbUtleXdvcmRzID0gd29yZFJlZ2V4cChbXCJhY2Nlc3NcIiwgXCJhY3RpdmVcIiwgXCJhc3NpZ25cIiwgXCJhbGxcIiwgXCJhbHRlclwiLCBcImFzXCIsIFwiY2F0YWxvZ1wiLCBcImNoYW5nZVwiLCBcImNvcHlcIiwgXCJjcmVhdGVcIiwgXCJjb25zdHJhaW50XCIsIFwiY29uc3RyYWludHNcIiwgXCJjdXJyZW50XCIsIFwiZGF0YWJhc2VcIiwgXCJkYXRhYmFzZXNcIiwgXCJkYm1zXCIsIFwiZGVmYXVsdFwiLCBcImRlbnlcIiwgXCJkcm9wXCIsIFwiZWxlbWVudFwiLCBcImVsZW1lbnRzXCIsIFwiZXhpc3RzXCIsIFwiZnJvbVwiLCBcImdyYW50XCIsIFwiZ3JhcGhcIiwgXCJncmFwaHNcIiwgXCJpZlwiLCBcImluZGV4XCIsIFwiaW5kZXhlc1wiLCBcImxhYmVsXCIsIFwibGFiZWxzXCIsIFwibWFuYWdlbWVudFwiLCBcIm1hdGNoXCIsIFwibmFtZVwiLCBcIm5hbWVzXCIsIFwibmV3XCIsIFwibm9kZVwiLCBcIm5vZGVzXCIsIFwibm90XCIsIFwib2ZcIiwgXCJvblwiLCBcIm9yXCIsIFwicGFzc3dvcmRcIiwgXCJwb3B1bGF0ZWRcIiwgXCJwcml2aWxlZ2VzXCIsIFwicHJvcGVydHlcIiwgXCJyZWFkXCIsIFwicmVsYXRpb25zaGlwXCIsIFwicmVsYXRpb25zaGlwc1wiLCBcInJlbW92ZVwiLCBcInJlcGxhY2VcIiwgXCJyZXF1aXJlZFwiLCBcInJldm9rZVwiLCBcInJvbGVcIiwgXCJyb2xlc1wiLCBcInNldFwiLCBcInNob3dcIiwgXCJzdGFydFwiLCBcInN0YXR1c1wiLCBcInN0b3BcIiwgXCJzdXNwZW5kZWRcIiwgXCJ0b1wiLCBcInRyYXZlcnNlXCIsIFwidHlwZVwiLCBcInR5cGVzXCIsIFwidXNlclwiLCBcInVzZXJzXCIsIFwid2l0aFwiLCBcIndyaXRlXCJdKTtcbnZhciBvcGVyYXRvckNoYXJzID0gL1sqK1xcLTw+PSZ8fiVeXS87XG5leHBvcnQgY29uc3QgY3lwaGVyID0ge1xuICBuYW1lOiBcImN5cGhlclwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBjb250ZXh0OiBudWxsLFxuICAgICAgaW5kZW50OiAwLFxuICAgICAgY29sOiAwXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgaWYgKHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC5hbGlnbiA9PSBudWxsKSB7XG4gICAgICAgIHN0YXRlLmNvbnRleHQuYWxpZ24gPSBmYWxzZTtcbiAgICAgIH1cbiAgICAgIHN0YXRlLmluZGVudCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3R5bGUgIT09IFwiY29tbWVudFwiICYmIHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC5hbGlnbiA9PSBudWxsICYmIHN0YXRlLmNvbnRleHQudHlwZSAhPT0gXCJwYXR0ZXJuXCIpIHtcbiAgICAgIHN0YXRlLmNvbnRleHQuYWxpZ24gPSB0cnVlO1xuICAgIH1cbiAgICBpZiAoY3VyUHVuYyA9PT0gXCIoXCIpIHtcbiAgICAgIHB1c2hDb250ZXh0KHN0YXRlLCBcIilcIiwgc3RyZWFtLmNvbHVtbigpKTtcbiAgICB9IGVsc2UgaWYgKGN1clB1bmMgPT09IFwiW1wiKSB7XG4gICAgICBwdXNoQ29udGV4dChzdGF0ZSwgXCJdXCIsIHN0cmVhbS5jb2x1bW4oKSk7XG4gICAgfSBlbHNlIGlmIChjdXJQdW5jID09PSBcIntcIikge1xuICAgICAgcHVzaENvbnRleHQoc3RhdGUsIFwifVwiLCBzdHJlYW0uY29sdW1uKCkpO1xuICAgIH0gZWxzZSBpZiAoL1tcXF1cXH1cXCldLy50ZXN0KGN1clB1bmMpKSB7XG4gICAgICB3aGlsZSAoc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LnR5cGUgPT09IFwicGF0dGVyblwiKSB7XG4gICAgICAgIHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgfVxuICAgICAgaWYgKHN0YXRlLmNvbnRleHQgJiYgY3VyUHVuYyA9PT0gc3RhdGUuY29udGV4dC50eXBlKSB7XG4gICAgICAgIHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PT0gXCIuXCIgJiYgc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LnR5cGUgPT09IFwicGF0dGVyblwiKSB7XG4gICAgICBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICB9IGVsc2UgaWYgKC9hdG9tfHN0cmluZ3x2YXJpYWJsZS8udGVzdChzdHlsZSkgJiYgc3RhdGUuY29udGV4dCkge1xuICAgICAgaWYgKC9bXFx9XFxdXS8udGVzdChzdGF0ZS5jb250ZXh0LnR5cGUpKSB7XG4gICAgICAgIHB1c2hDb250ZXh0KHN0YXRlLCBcInBhdHRlcm5cIiwgc3RyZWFtLmNvbHVtbigpKTtcbiAgICAgIH0gZWxzZSBpZiAoc3RhdGUuY29udGV4dC50eXBlID09PSBcInBhdHRlcm5cIiAmJiAhc3RhdGUuY29udGV4dC5hbGlnbikge1xuICAgICAgICBzdGF0ZS5jb250ZXh0LmFsaWduID0gdHJ1ZTtcbiAgICAgICAgc3RhdGUuY29udGV4dC5jb2wgPSBzdHJlYW0uY29sdW1uKCk7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICB2YXIgZmlyc3RDaGFyID0gdGV4dEFmdGVyICYmIHRleHRBZnRlci5jaGFyQXQoMCk7XG4gICAgdmFyIGNvbnRleHQgPSBzdGF0ZS5jb250ZXh0O1xuICAgIGlmICgvW1xcXVxcfV0vLnRlc3QoZmlyc3RDaGFyKSkge1xuICAgICAgd2hpbGUgKGNvbnRleHQgJiYgY29udGV4dC50eXBlID09PSBcInBhdHRlcm5cIikge1xuICAgICAgICBjb250ZXh0ID0gY29udGV4dC5wcmV2O1xuICAgICAgfVxuICAgIH1cbiAgICB2YXIgY2xvc2luZyA9IGNvbnRleHQgJiYgZmlyc3RDaGFyID09PSBjb250ZXh0LnR5cGU7XG4gICAgaWYgKCFjb250ZXh0KSByZXR1cm4gMDtcbiAgICBpZiAoY29udGV4dC50eXBlID09PSBcImtleXdvcmRzXCIpIHJldHVybiBudWxsO1xuICAgIGlmIChjb250ZXh0LmFsaWduKSByZXR1cm4gY29udGV4dC5jb2wgKyAoY2xvc2luZyA/IDAgOiAxKTtcbiAgICByZXR1cm4gY29udGV4dC5pbmRlbnQgKyAoY2xvc2luZyA/IDAgOiBjeC51bml0KTtcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9