"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5737],{

/***/ 45737
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   q: () => (/* binding */ q)
/* harmony export */ });
var curPunc,
  keywords = buildRE(["abs", "acos", "aj", "aj0", "all", "and", "any", "asc", "asin", "asof", "atan", "attr", "avg", "avgs", "bin", "by", "ceiling", "cols", "cor", "cos", "count", "cov", "cross", "csv", "cut", "delete", "deltas", "desc", "dev", "differ", "distinct", "div", "do", "each", "ej", "enlist", "eval", "except", "exec", "exit", "exp", "fby", "fills", "first", "fkeys", "flip", "floor", "from", "get", "getenv", "group", "gtime", "hclose", "hcount", "hdel", "hopen", "hsym", "iasc", "idesc", "if", "ij", "in", "insert", "inter", "inv", "key", "keys", "last", "like", "list", "lj", "load", "log", "lower", "lsq", "ltime", "ltrim", "mavg", "max", "maxs", "mcount", "md5", "mdev", "med", "meta", "min", "mins", "mmax", "mmin", "mmu", "mod", "msum", "neg", "next", "not", "null", "or", "over", "parse", "peach", "pj", "plist", "prd", "prds", "prev", "prior", "rand", "rank", "ratios", "raze", "read0", "read1", "reciprocal", "reverse", "rload", "rotate", "rsave", "rtrim", "save", "scan", "select", "set", "setenv", "show", "signum", "sin", "sqrt", "ss", "ssr", "string", "sublist", "sum", "sums", "sv", "system", "tables", "tan", "til", "trim", "txf", "type", "uj", "ungroup", "union", "update", "upper", "upsert", "value", "var", "view", "views", "vs", "wavg", "where", "where", "while", "within", "wj", "wj1", "wsum", "xasc", "xbar", "xcol", "xcols", "xdesc", "xexp", "xgroup", "xkey", "xlog", "xprev", "xrank"]),
  E = /[|/&^!+:\\\-*%$=~#;@><,?_\'\"\[\(\]\)\s{}]/;
function buildRE(w) {
  return new RegExp("^(" + w.join("|") + ")$");
}
function tokenBase(stream, state) {
  var sol = stream.sol(),
    c = stream.next();
  curPunc = null;
  if (sol) if (c == "/") return (state.tokenize = tokenLineComment)(stream, state);else if (c == "\\") {
    if (stream.eol() || /\s/.test(stream.peek())) return stream.skipToEnd(), /^\\\s*$/.test(stream.current()) ? (state.tokenize = tokenCommentToEOF)(stream) : state.tokenize = tokenBase, "comment";else return state.tokenize = tokenBase, "builtin";
  }
  if (/\s/.test(c)) return stream.peek() == "/" ? (stream.skipToEnd(), "comment") : "null";
  if (c == '"') return (state.tokenize = tokenString)(stream, state);
  if (c == '`') return stream.eatWhile(/[A-Za-z\d_:\/.]/), "macroName";
  if ("." == c && /\d/.test(stream.peek()) || /\d/.test(c)) {
    var t = null;
    stream.backUp(1);
    if (stream.match(/^\d{4}\.\d{2}(m|\.\d{2}([DT](\d{2}(:\d{2}(:\d{2}(\.\d{1,9})?)?)?)?)?)/) || stream.match(/^\d+D(\d{2}(:\d{2}(:\d{2}(\.\d{1,9})?)?)?)/) || stream.match(/^\d{2}:\d{2}(:\d{2}(\.\d{1,9})?)?/) || stream.match(/^\d+[ptuv]{1}/)) t = "temporal";else if (stream.match(/^0[NwW]{1}/) || stream.match(/^0x[\da-fA-F]*/) || stream.match(/^[01]+[b]{1}/) || stream.match(/^\d+[chijn]{1}/) || stream.match(/-?\d*(\.\d*)?(e[+\-]?\d+)?(e|f)?/)) t = "number";
    return t && (!(c = stream.peek()) || E.test(c)) ? t : (stream.next(), "error");
  }
  if (/[A-Za-z]|\./.test(c)) return stream.eatWhile(/[A-Za-z._\d]/), keywords.test(stream.current()) ? "keyword" : "variable";
  if (/[|/&^!+:\\\-*%$=~#;@><\.,?_\']/.test(c)) return null;
  if (/[{}\(\[\]\)]/.test(c)) return null;
  return "error";
}
function tokenLineComment(stream, state) {
  return stream.skipToEnd(), /^\/\s*$/.test(stream.current()) ? (state.tokenize = tokenBlockComment)(stream, state) : state.tokenize = tokenBase, "comment";
}
function tokenBlockComment(stream, state) {
  var f = stream.sol() && stream.peek() == "\\";
  stream.skipToEnd();
  if (f && /^\\\s*$/.test(stream.current())) state.tokenize = tokenBase;
  return "comment";
}
function tokenCommentToEOF(stream) {
  return stream.skipToEnd(), "comment";
}
function tokenString(stream, state) {
  var escaped = false,
    next,
    end = false;
  while (next = stream.next()) {
    if (next == "\"" && !escaped) {
      end = true;
      break;
    }
    escaped = !escaped && next == "\\";
  }
  if (end) state.tokenize = tokenBase;
  return "string";
}
function pushContext(state, type, col) {
  state.context = {
    prev: state.context,
    indent: state.indent,
    col: col,
    type: type
  };
}
function popContext(state) {
  state.indent = state.context.indent;
  state.context = state.context.prev;
}
const q = {
  name: "q",
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
      if (state.context && state.context.align == null) state.context.align = false;
      state.indent = stream.indentation();
    }
    //if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    if (style != "comment" && state.context && state.context.align == null && state.context.type != "pattern") {
      state.context.align = true;
    }
    if (curPunc == "(") pushContext(state, ")", stream.column());else if (curPunc == "[") pushContext(state, "]", stream.column());else if (curPunc == "{") pushContext(state, "}", stream.column());else if (/[\]\}\)]/.test(curPunc)) {
      while (state.context && state.context.type == "pattern") popContext(state);
      if (state.context && curPunc == state.context.type) popContext(state);
    } else if (curPunc == "." && state.context && state.context.type == "pattern") popContext(state);else if (/atom|string|variable/.test(style) && state.context) {
      if (/[\}\]]/.test(state.context.type)) pushContext(state, "pattern", stream.column());else if (state.context.type == "pattern" && !state.context.align) {
        state.context.align = true;
        state.context.col = stream.column();
      }
    }
    return style;
  },
  indent: function (state, textAfter, cx) {
    var firstChar = textAfter && textAfter.charAt(0);
    var context = state.context;
    if (/[\]\}]/.test(firstChar)) while (context && context.type == "pattern") context = context.prev;
    var closing = context && firstChar == context.type;
    if (!context) return 0;else if (context.type == "pattern") return context.col;else if (context.align) return context.col + (closing ? 0 : 1);else return context.indent + (closing ? 0 : cx.unit);
  },
  languageData: {
    commentTokens: {
      line: "/"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTczNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvcS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgY3VyUHVuYyxcbiAga2V5d29yZHMgPSBidWlsZFJFKFtcImFic1wiLCBcImFjb3NcIiwgXCJhalwiLCBcImFqMFwiLCBcImFsbFwiLCBcImFuZFwiLCBcImFueVwiLCBcImFzY1wiLCBcImFzaW5cIiwgXCJhc29mXCIsIFwiYXRhblwiLCBcImF0dHJcIiwgXCJhdmdcIiwgXCJhdmdzXCIsIFwiYmluXCIsIFwiYnlcIiwgXCJjZWlsaW5nXCIsIFwiY29sc1wiLCBcImNvclwiLCBcImNvc1wiLCBcImNvdW50XCIsIFwiY292XCIsIFwiY3Jvc3NcIiwgXCJjc3ZcIiwgXCJjdXRcIiwgXCJkZWxldGVcIiwgXCJkZWx0YXNcIiwgXCJkZXNjXCIsIFwiZGV2XCIsIFwiZGlmZmVyXCIsIFwiZGlzdGluY3RcIiwgXCJkaXZcIiwgXCJkb1wiLCBcImVhY2hcIiwgXCJlalwiLCBcImVubGlzdFwiLCBcImV2YWxcIiwgXCJleGNlcHRcIiwgXCJleGVjXCIsIFwiZXhpdFwiLCBcImV4cFwiLCBcImZieVwiLCBcImZpbGxzXCIsIFwiZmlyc3RcIiwgXCJma2V5c1wiLCBcImZsaXBcIiwgXCJmbG9vclwiLCBcImZyb21cIiwgXCJnZXRcIiwgXCJnZXRlbnZcIiwgXCJncm91cFwiLCBcImd0aW1lXCIsIFwiaGNsb3NlXCIsIFwiaGNvdW50XCIsIFwiaGRlbFwiLCBcImhvcGVuXCIsIFwiaHN5bVwiLCBcImlhc2NcIiwgXCJpZGVzY1wiLCBcImlmXCIsIFwiaWpcIiwgXCJpblwiLCBcImluc2VydFwiLCBcImludGVyXCIsIFwiaW52XCIsIFwia2V5XCIsIFwia2V5c1wiLCBcImxhc3RcIiwgXCJsaWtlXCIsIFwibGlzdFwiLCBcImxqXCIsIFwibG9hZFwiLCBcImxvZ1wiLCBcImxvd2VyXCIsIFwibHNxXCIsIFwibHRpbWVcIiwgXCJsdHJpbVwiLCBcIm1hdmdcIiwgXCJtYXhcIiwgXCJtYXhzXCIsIFwibWNvdW50XCIsIFwibWQ1XCIsIFwibWRldlwiLCBcIm1lZFwiLCBcIm1ldGFcIiwgXCJtaW5cIiwgXCJtaW5zXCIsIFwibW1heFwiLCBcIm1taW5cIiwgXCJtbXVcIiwgXCJtb2RcIiwgXCJtc3VtXCIsIFwibmVnXCIsIFwibmV4dFwiLCBcIm5vdFwiLCBcIm51bGxcIiwgXCJvclwiLCBcIm92ZXJcIiwgXCJwYXJzZVwiLCBcInBlYWNoXCIsIFwicGpcIiwgXCJwbGlzdFwiLCBcInByZFwiLCBcInByZHNcIiwgXCJwcmV2XCIsIFwicHJpb3JcIiwgXCJyYW5kXCIsIFwicmFua1wiLCBcInJhdGlvc1wiLCBcInJhemVcIiwgXCJyZWFkMFwiLCBcInJlYWQxXCIsIFwicmVjaXByb2NhbFwiLCBcInJldmVyc2VcIiwgXCJybG9hZFwiLCBcInJvdGF0ZVwiLCBcInJzYXZlXCIsIFwicnRyaW1cIiwgXCJzYXZlXCIsIFwic2NhblwiLCBcInNlbGVjdFwiLCBcInNldFwiLCBcInNldGVudlwiLCBcInNob3dcIiwgXCJzaWdudW1cIiwgXCJzaW5cIiwgXCJzcXJ0XCIsIFwic3NcIiwgXCJzc3JcIiwgXCJzdHJpbmdcIiwgXCJzdWJsaXN0XCIsIFwic3VtXCIsIFwic3Vtc1wiLCBcInN2XCIsIFwic3lzdGVtXCIsIFwidGFibGVzXCIsIFwidGFuXCIsIFwidGlsXCIsIFwidHJpbVwiLCBcInR4ZlwiLCBcInR5cGVcIiwgXCJ1alwiLCBcInVuZ3JvdXBcIiwgXCJ1bmlvblwiLCBcInVwZGF0ZVwiLCBcInVwcGVyXCIsIFwidXBzZXJ0XCIsIFwidmFsdWVcIiwgXCJ2YXJcIiwgXCJ2aWV3XCIsIFwidmlld3NcIiwgXCJ2c1wiLCBcIndhdmdcIiwgXCJ3aGVyZVwiLCBcIndoZXJlXCIsIFwid2hpbGVcIiwgXCJ3aXRoaW5cIiwgXCJ3alwiLCBcIndqMVwiLCBcIndzdW1cIiwgXCJ4YXNjXCIsIFwieGJhclwiLCBcInhjb2xcIiwgXCJ4Y29sc1wiLCBcInhkZXNjXCIsIFwieGV4cFwiLCBcInhncm91cFwiLCBcInhrZXlcIiwgXCJ4bG9nXCIsIFwieHByZXZcIiwgXCJ4cmFua1wiXSksXG4gIEUgPSAvW3wvJl4hKzpcXFxcXFwtKiUkPX4jO0A+PCw/X1xcJ1xcXCJcXFtcXChcXF1cXClcXHN7fV0vO1xuZnVuY3Rpb24gYnVpbGRSRSh3KSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXihcIiArIHcuam9pbihcInxcIikgKyBcIikkXCIpO1xufVxuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIHNvbCA9IHN0cmVhbS5zb2woKSxcbiAgICBjID0gc3RyZWFtLm5leHQoKTtcbiAgY3VyUHVuYyA9IG51bGw7XG4gIGlmIChzb2wpIGlmIChjID09IFwiL1wiKSByZXR1cm4gKHN0YXRlLnRva2VuaXplID0gdG9rZW5MaW5lQ29tbWVudCkoc3RyZWFtLCBzdGF0ZSk7ZWxzZSBpZiAoYyA9PSBcIlxcXFxcIikge1xuICAgIGlmIChzdHJlYW0uZW9sKCkgfHwgL1xccy8udGVzdChzdHJlYW0ucGVlaygpKSkgcmV0dXJuIHN0cmVhbS5za2lwVG9FbmQoKSwgL15cXFxcXFxzKiQvLnRlc3Qoc3RyZWFtLmN1cnJlbnQoKSkgPyAoc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnRUb0VPRikoc3RyZWFtKSA6IHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlLCBcImNvbW1lbnRcIjtlbHNlIHJldHVybiBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZSwgXCJidWlsdGluXCI7XG4gIH1cbiAgaWYgKC9cXHMvLnRlc3QoYykpIHJldHVybiBzdHJlYW0ucGVlaygpID09IFwiL1wiID8gKHN0cmVhbS5za2lwVG9FbmQoKSwgXCJjb21tZW50XCIpIDogXCJudWxsXCI7XG4gIGlmIChjID09ICdcIicpIHJldHVybiAoc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZykoc3RyZWFtLCBzdGF0ZSk7XG4gIGlmIChjID09ICdgJykgcmV0dXJuIHN0cmVhbS5lYXRXaGlsZSgvW0EtWmEtelxcZF86XFwvLl0vKSwgXCJtYWNyb05hbWVcIjtcbiAgaWYgKFwiLlwiID09IGMgJiYgL1xcZC8udGVzdChzdHJlYW0ucGVlaygpKSB8fCAvXFxkLy50ZXN0KGMpKSB7XG4gICAgdmFyIHQgPSBudWxsO1xuICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXlxcZHs0fVxcLlxcZHsyfShtfFxcLlxcZHsyfShbRFRdKFxcZHsyfSg6XFxkezJ9KDpcXGR7Mn0oXFwuXFxkezEsOX0pPyk/KT8pPyk/KS8pIHx8IHN0cmVhbS5tYXRjaCgvXlxcZCtEKFxcZHsyfSg6XFxkezJ9KDpcXGR7Mn0oXFwuXFxkezEsOX0pPyk/KT8pLykgfHwgc3RyZWFtLm1hdGNoKC9eXFxkezJ9OlxcZHsyfSg6XFxkezJ9KFxcLlxcZHsxLDl9KT8pPy8pIHx8IHN0cmVhbS5tYXRjaCgvXlxcZCtbcHR1dl17MX0vKSkgdCA9IFwidGVtcG9yYWxcIjtlbHNlIGlmIChzdHJlYW0ubWF0Y2goL14wW053V117MX0vKSB8fCBzdHJlYW0ubWF0Y2goL14weFtcXGRhLWZBLUZdKi8pIHx8IHN0cmVhbS5tYXRjaCgvXlswMV0rW2JdezF9LykgfHwgc3RyZWFtLm1hdGNoKC9eXFxkK1tjaGlqbl17MX0vKSB8fCBzdHJlYW0ubWF0Y2goLy0/XFxkKihcXC5cXGQqKT8oZVsrXFwtXT9cXGQrKT8oZXxmKT8vKSkgdCA9IFwibnVtYmVyXCI7XG4gICAgcmV0dXJuIHQgJiYgKCEoYyA9IHN0cmVhbS5wZWVrKCkpIHx8IEUudGVzdChjKSkgPyB0IDogKHN0cmVhbS5uZXh0KCksIFwiZXJyb3JcIik7XG4gIH1cbiAgaWYgKC9bQS1aYS16XXxcXC4vLnRlc3QoYykpIHJldHVybiBzdHJlYW0uZWF0V2hpbGUoL1tBLVphLXouX1xcZF0vKSwga2V5d29yZHMudGVzdChzdHJlYW0uY3VycmVudCgpKSA/IFwia2V5d29yZFwiIDogXCJ2YXJpYWJsZVwiO1xuICBpZiAoL1t8LyZeISs6XFxcXFxcLSolJD1+IztAPjxcXC4sP19cXCddLy50ZXN0KGMpKSByZXR1cm4gbnVsbDtcbiAgaWYgKC9be31cXChcXFtcXF1cXCldLy50ZXN0KGMpKSByZXR1cm4gbnVsbDtcbiAgcmV0dXJuIFwiZXJyb3JcIjtcbn1cbmZ1bmN0aW9uIHRva2VuTGluZUNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICByZXR1cm4gc3RyZWFtLnNraXBUb0VuZCgpLCAvXlxcL1xccyokLy50ZXN0KHN0cmVhbS5jdXJyZW50KCkpID8gKHN0YXRlLnRva2VuaXplID0gdG9rZW5CbG9ja0NvbW1lbnQpKHN0cmVhbSwgc3RhdGUpIDogc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2UsIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5CbG9ja0NvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgZiA9IHN0cmVhbS5zb2woKSAmJiBzdHJlYW0ucGVlaygpID09IFwiXFxcXFwiO1xuICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIGlmIChmICYmIC9eXFxcXFxccyokLy50ZXN0KHN0cmVhbS5jdXJyZW50KCkpKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50VG9FT0Yoc3RyZWFtKSB7XG4gIHJldHVybiBzdHJlYW0uc2tpcFRvRW5kKCksIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgIG5leHQsXG4gICAgZW5kID0gZmFsc2U7XG4gIHdoaWxlIChuZXh0ID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChuZXh0ID09IFwiXFxcIlwiICYmICFlc2NhcGVkKSB7XG4gICAgICBlbmQgPSB0cnVlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICB9XG4gIGlmIChlbmQpIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cbmZ1bmN0aW9uIHB1c2hDb250ZXh0KHN0YXRlLCB0eXBlLCBjb2wpIHtcbiAgc3RhdGUuY29udGV4dCA9IHtcbiAgICBwcmV2OiBzdGF0ZS5jb250ZXh0LFxuICAgIGluZGVudDogc3RhdGUuaW5kZW50LFxuICAgIGNvbDogY29sLFxuICAgIHR5cGU6IHR5cGVcbiAgfTtcbn1cbmZ1bmN0aW9uIHBvcENvbnRleHQoc3RhdGUpIHtcbiAgc3RhdGUuaW5kZW50ID0gc3RhdGUuY29udGV4dC5pbmRlbnQ7XG4gIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG59XG5leHBvcnQgY29uc3QgcSA9IHtcbiAgbmFtZTogXCJxXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IHRva2VuQmFzZSxcbiAgICAgIGNvbnRleHQ6IG51bGwsXG4gICAgICBpbmRlbnQ6IDAsXG4gICAgICBjb2w6IDBcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBpZiAoc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LmFsaWduID09IG51bGwpIHN0YXRlLmNvbnRleHQuYWxpZ24gPSBmYWxzZTtcbiAgICAgIHN0YXRlLmluZGVudCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgIH1cbiAgICAvL2lmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0eWxlICE9IFwiY29tbWVudFwiICYmIHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC5hbGlnbiA9PSBudWxsICYmIHN0YXRlLmNvbnRleHQudHlwZSAhPSBcInBhdHRlcm5cIikge1xuICAgICAgc3RhdGUuY29udGV4dC5hbGlnbiA9IHRydWU7XG4gICAgfVxuICAgIGlmIChjdXJQdW5jID09IFwiKFwiKSBwdXNoQ29udGV4dChzdGF0ZSwgXCIpXCIsIHN0cmVhbS5jb2x1bW4oKSk7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIltcIikgcHVzaENvbnRleHQoc3RhdGUsIFwiXVwiLCBzdHJlYW0uY29sdW1uKCkpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJ7XCIpIHB1c2hDb250ZXh0KHN0YXRlLCBcIn1cIiwgc3RyZWFtLmNvbHVtbigpKTtlbHNlIGlmICgvW1xcXVxcfVxcKV0vLnRlc3QoY3VyUHVuYykpIHtcbiAgICAgIHdoaWxlIChzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICBpZiAoc3RhdGUuY29udGV4dCAmJiBjdXJQdW5jID09IHN0YXRlLmNvbnRleHQudHlwZSkgcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChjdXJQdW5jID09IFwiLlwiICYmIHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC50eXBlID09IFwicGF0dGVyblwiKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmICgvYXRvbXxzdHJpbmd8dmFyaWFibGUvLnRlc3Qoc3R5bGUpICYmIHN0YXRlLmNvbnRleHQpIHtcbiAgICAgIGlmICgvW1xcfVxcXV0vLnRlc3Qoc3RhdGUuY29udGV4dC50eXBlKSkgcHVzaENvbnRleHQoc3RhdGUsIFwicGF0dGVyblwiLCBzdHJlYW0uY29sdW1uKCkpO2Vsc2UgaWYgKHN0YXRlLmNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIiAmJiAhc3RhdGUuY29udGV4dC5hbGlnbikge1xuICAgICAgICBzdGF0ZS5jb250ZXh0LmFsaWduID0gdHJ1ZTtcbiAgICAgICAgc3RhdGUuY29udGV4dC5jb2wgPSBzdHJlYW0uY29sdW1uKCk7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICB2YXIgZmlyc3RDaGFyID0gdGV4dEFmdGVyICYmIHRleHRBZnRlci5jaGFyQXQoMCk7XG4gICAgdmFyIGNvbnRleHQgPSBzdGF0ZS5jb250ZXh0O1xuICAgIGlmICgvW1xcXVxcfV0vLnRlc3QoZmlyc3RDaGFyKSkgd2hpbGUgKGNvbnRleHQgJiYgY29udGV4dC50eXBlID09IFwicGF0dGVyblwiKSBjb250ZXh0ID0gY29udGV4dC5wcmV2O1xuICAgIHZhciBjbG9zaW5nID0gY29udGV4dCAmJiBmaXJzdENoYXIgPT0gY29udGV4dC50eXBlO1xuICAgIGlmICghY29udGV4dCkgcmV0dXJuIDA7ZWxzZSBpZiAoY29udGV4dC50eXBlID09IFwicGF0dGVyblwiKSByZXR1cm4gY29udGV4dC5jb2w7ZWxzZSBpZiAoY29udGV4dC5hbGlnbikgcmV0dXJuIGNvbnRleHQuY29sICsgKGNsb3NpbmcgPyAwIDogMSk7ZWxzZSByZXR1cm4gY29udGV4dC5pbmRlbnQgKyAoY2xvc2luZyA/IDAgOiBjeC51bml0KTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIvXCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==