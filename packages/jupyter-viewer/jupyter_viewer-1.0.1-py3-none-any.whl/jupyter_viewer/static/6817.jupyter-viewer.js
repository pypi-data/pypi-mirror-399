"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6817],{

/***/ 6817
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   sparql: () => (/* binding */ sparql)
/* harmony export */ });
var curPunc;
function wordRegexp(words) {
  return new RegExp("^(?:" + words.join("|") + ")$", "i");
}
var ops = wordRegexp(["str", "lang", "langmatches", "datatype", "bound", "sameterm", "isiri", "isuri", "iri", "uri", "bnode", "count", "sum", "min", "max", "avg", "sample", "group_concat", "rand", "abs", "ceil", "floor", "round", "concat", "substr", "strlen", "replace", "ucase", "lcase", "encode_for_uri", "contains", "strstarts", "strends", "strbefore", "strafter", "year", "month", "day", "hours", "minutes", "seconds", "timezone", "tz", "now", "uuid", "struuid", "md5", "sha1", "sha256", "sha384", "sha512", "coalesce", "if", "strlang", "strdt", "isnumeric", "regex", "exists", "isblank", "isliteral", "a", "bind"]);
var keywords = wordRegexp(["base", "prefix", "select", "distinct", "reduced", "construct", "describe", "ask", "from", "named", "where", "order", "limit", "offset", "filter", "optional", "graph", "by", "asc", "desc", "as", "having", "undef", "values", "group", "minus", "in", "not", "service", "silent", "using", "insert", "delete", "union", "true", "false", "with", "data", "copy", "to", "move", "add", "create", "drop", "clear", "load", "into"]);
var operatorChars = /[*+\-<>=&|\^\/!\?]/;
var PN_CHARS = "[A-Za-z_\\-0-9]";
var PREFIX_START = new RegExp("[A-Za-z]");
var PREFIX_REMAINDER = new RegExp("((" + PN_CHARS + "|\\.)*(" + PN_CHARS + "))?:");
function tokenBase(stream, state) {
  var ch = stream.next();
  curPunc = null;
  if (ch == "$" || ch == "?") {
    if (ch == "?" && stream.match(/\s/, false)) {
      return "operator";
    }
    stream.match(/^[A-Za-z0-9_\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][A-Za-z0-9_\u00B7\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u037D\u037F-\u1FFF\u200C-\u200D\u203F-\u2040\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD]*/);
    return "variableName.local";
  } else if (ch == "<" && !stream.match(/^[\s\u00a0=]/, false)) {
    stream.match(/^[^\s\u00a0>]*>?/);
    return "atom";
  } else if (ch == "\"" || ch == "'") {
    state.tokenize = tokenLiteral(ch);
    return state.tokenize(stream, state);
  } else if (/[{}\(\),\.;\[\]]/.test(ch)) {
    curPunc = ch;
    return "bracket";
  } else if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  } else if (operatorChars.test(ch)) {
    return "operator";
  } else if (ch == ":") {
    eatPnLocal(stream);
    return "atom";
  } else if (ch == "@") {
    stream.eatWhile(/[a-z\d\-]/i);
    return "meta";
  } else if (PREFIX_START.test(ch) && stream.match(PREFIX_REMAINDER)) {
    eatPnLocal(stream);
    return "atom";
  }
  stream.eatWhile(/[_\w\d]/);
  var word = stream.current();
  if (ops.test(word)) return "builtin";else if (keywords.test(word)) return "keyword";else return "variable";
}
function eatPnLocal(stream) {
  stream.match(/(\.(?=[\w_\-\\%])|[:\w_-]|\\[-\\_~.!$&'()*+,;=/?#@%]|%[a-f\d][a-f\d])+/i);
}
function tokenLiteral(quote) {
  return function (stream, state) {
    var escaped = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch == quote && !escaped) {
        state.tokenize = tokenBase;
        break;
      }
      escaped = !escaped && ch == "\\";
    }
    return "string";
  };
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
const sparql = {
  name: "sparql",
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
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    if (style != "comment" && state.context && state.context.align == null && state.context.type != "pattern") {
      state.context.align = true;
    }
    if (curPunc == "(") pushContext(state, ")", stream.column());else if (curPunc == "[") pushContext(state, "]", stream.column());else if (curPunc == "{") pushContext(state, "}", stream.column());else if (/[\]\}\)]/.test(curPunc)) {
      while (state.context && state.context.type == "pattern") popContext(state);
      if (state.context && curPunc == state.context.type) {
        popContext(state);
        if (curPunc == "}" && state.context && state.context.type == "pattern") popContext(state);
      }
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
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjgxNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3NwYXJxbC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgY3VyUHVuYztcbmZ1bmN0aW9uIHdvcmRSZWdleHAod29yZHMpIHtcbiAgcmV0dXJuIG5ldyBSZWdFeHAoXCJeKD86XCIgKyB3b3Jkcy5qb2luKFwifFwiKSArIFwiKSRcIiwgXCJpXCIpO1xufVxudmFyIG9wcyA9IHdvcmRSZWdleHAoW1wic3RyXCIsIFwibGFuZ1wiLCBcImxhbmdtYXRjaGVzXCIsIFwiZGF0YXR5cGVcIiwgXCJib3VuZFwiLCBcInNhbWV0ZXJtXCIsIFwiaXNpcmlcIiwgXCJpc3VyaVwiLCBcImlyaVwiLCBcInVyaVwiLCBcImJub2RlXCIsIFwiY291bnRcIiwgXCJzdW1cIiwgXCJtaW5cIiwgXCJtYXhcIiwgXCJhdmdcIiwgXCJzYW1wbGVcIiwgXCJncm91cF9jb25jYXRcIiwgXCJyYW5kXCIsIFwiYWJzXCIsIFwiY2VpbFwiLCBcImZsb29yXCIsIFwicm91bmRcIiwgXCJjb25jYXRcIiwgXCJzdWJzdHJcIiwgXCJzdHJsZW5cIiwgXCJyZXBsYWNlXCIsIFwidWNhc2VcIiwgXCJsY2FzZVwiLCBcImVuY29kZV9mb3JfdXJpXCIsIFwiY29udGFpbnNcIiwgXCJzdHJzdGFydHNcIiwgXCJzdHJlbmRzXCIsIFwic3RyYmVmb3JlXCIsIFwic3RyYWZ0ZXJcIiwgXCJ5ZWFyXCIsIFwibW9udGhcIiwgXCJkYXlcIiwgXCJob3Vyc1wiLCBcIm1pbnV0ZXNcIiwgXCJzZWNvbmRzXCIsIFwidGltZXpvbmVcIiwgXCJ0elwiLCBcIm5vd1wiLCBcInV1aWRcIiwgXCJzdHJ1dWlkXCIsIFwibWQ1XCIsIFwic2hhMVwiLCBcInNoYTI1NlwiLCBcInNoYTM4NFwiLCBcInNoYTUxMlwiLCBcImNvYWxlc2NlXCIsIFwiaWZcIiwgXCJzdHJsYW5nXCIsIFwic3RyZHRcIiwgXCJpc251bWVyaWNcIiwgXCJyZWdleFwiLCBcImV4aXN0c1wiLCBcImlzYmxhbmtcIiwgXCJpc2xpdGVyYWxcIiwgXCJhXCIsIFwiYmluZFwiXSk7XG52YXIga2V5d29yZHMgPSB3b3JkUmVnZXhwKFtcImJhc2VcIiwgXCJwcmVmaXhcIiwgXCJzZWxlY3RcIiwgXCJkaXN0aW5jdFwiLCBcInJlZHVjZWRcIiwgXCJjb25zdHJ1Y3RcIiwgXCJkZXNjcmliZVwiLCBcImFza1wiLCBcImZyb21cIiwgXCJuYW1lZFwiLCBcIndoZXJlXCIsIFwib3JkZXJcIiwgXCJsaW1pdFwiLCBcIm9mZnNldFwiLCBcImZpbHRlclwiLCBcIm9wdGlvbmFsXCIsIFwiZ3JhcGhcIiwgXCJieVwiLCBcImFzY1wiLCBcImRlc2NcIiwgXCJhc1wiLCBcImhhdmluZ1wiLCBcInVuZGVmXCIsIFwidmFsdWVzXCIsIFwiZ3JvdXBcIiwgXCJtaW51c1wiLCBcImluXCIsIFwibm90XCIsIFwic2VydmljZVwiLCBcInNpbGVudFwiLCBcInVzaW5nXCIsIFwiaW5zZXJ0XCIsIFwiZGVsZXRlXCIsIFwidW5pb25cIiwgXCJ0cnVlXCIsIFwiZmFsc2VcIiwgXCJ3aXRoXCIsIFwiZGF0YVwiLCBcImNvcHlcIiwgXCJ0b1wiLCBcIm1vdmVcIiwgXCJhZGRcIiwgXCJjcmVhdGVcIiwgXCJkcm9wXCIsIFwiY2xlYXJcIiwgXCJsb2FkXCIsIFwiaW50b1wiXSk7XG52YXIgb3BlcmF0b3JDaGFycyA9IC9bKitcXC08Pj0mfFxcXlxcLyFcXD9dLztcbnZhciBQTl9DSEFSUyA9IFwiW0EtWmEtel9cXFxcLTAtOV1cIjtcbnZhciBQUkVGSVhfU1RBUlQgPSBuZXcgUmVnRXhwKFwiW0EtWmEtel1cIik7XG52YXIgUFJFRklYX1JFTUFJTkRFUiA9IG5ldyBSZWdFeHAoXCIoKFwiICsgUE5fQ0hBUlMgKyBcInxcXFxcLikqKFwiICsgUE5fQ0hBUlMgKyBcIikpPzpcIik7XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBjdXJQdW5jID0gbnVsbDtcbiAgaWYgKGNoID09IFwiJFwiIHx8IGNoID09IFwiP1wiKSB7XG4gICAgaWYgKGNoID09IFwiP1wiICYmIHN0cmVhbS5tYXRjaCgvXFxzLywgZmFsc2UpKSB7XG4gICAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgIH1cbiAgICBzdHJlYW0ubWF0Y2goL15bQS1aYS16MC05X1xcdTAwQzAtXFx1MDBENlxcdTAwRDgtXFx1MDBGNlxcdTAwRjgtXFx1MDJGRlxcdTAzNzAtXFx1MDM3RFxcdTAzN0YtXFx1MUZGRlxcdTIwMEMtXFx1MjAwRFxcdTIwNzAtXFx1MjE4RlxcdTJDMDAtXFx1MkZFRlxcdTMwMDEtXFx1RDdGRlxcdUY5MDAtXFx1RkRDRlxcdUZERjAtXFx1RkZGRF1bQS1aYS16MC05X1xcdTAwQjdcXHUwMEMwLVxcdTAwRDZcXHUwMEQ4LVxcdTAwRjZcXHUwMEY4LVxcdTAzN0RcXHUwMzdGLVxcdTFGRkZcXHUyMDBDLVxcdTIwMERcXHUyMDNGLVxcdTIwNDBcXHUyMDcwLVxcdTIxOEZcXHUyQzAwLVxcdTJGRUZcXHUzMDAxLVxcdUQ3RkZcXHVGOTAwLVxcdUZEQ0ZcXHVGREYwLVxcdUZGRkRdKi8pO1xuICAgIHJldHVybiBcInZhcmlhYmxlTmFtZS5sb2NhbFwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiPFwiICYmICFzdHJlYW0ubWF0Y2goL15bXFxzXFx1MDBhMD1dLywgZmFsc2UpKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9eW15cXHNcXHUwMGEwPl0qPj8vKTtcbiAgICByZXR1cm4gXCJhdG9tXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCJcXFwiXCIgfHwgY2ggPT0gXCInXCIpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuTGl0ZXJhbChjaCk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9IGVsc2UgaWYgKC9be31cXChcXCksXFwuO1xcW1xcXV0vLnRlc3QoY2gpKSB7XG4gICAgY3VyUHVuYyA9IGNoO1xuICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIiNcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAob3BlcmF0b3JDaGFycy50ZXN0KGNoKSkge1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI6XCIpIHtcbiAgICBlYXRQbkxvY2FsKHN0cmVhbSk7XG4gICAgcmV0dXJuIFwiYXRvbVwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiQFwiKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bYS16XFxkXFwtXS9pKTtcbiAgICByZXR1cm4gXCJtZXRhXCI7XG4gIH0gZWxzZSBpZiAoUFJFRklYX1NUQVJULnRlc3QoY2gpICYmIHN0cmVhbS5tYXRjaChQUkVGSVhfUkVNQUlOREVSKSkge1xuICAgIGVhdFBuTG9jYWwoc3RyZWFtKTtcbiAgICByZXR1cm4gXCJhdG9tXCI7XG4gIH1cbiAgc3RyZWFtLmVhdFdoaWxlKC9bX1xcd1xcZF0vKTtcbiAgdmFyIHdvcmQgPSBzdHJlYW0uY3VycmVudCgpO1xuICBpZiAob3BzLnRlc3Qod29yZCkpIHJldHVybiBcImJ1aWx0aW5cIjtlbHNlIGlmIChrZXl3b3Jkcy50ZXN0KHdvcmQpKSByZXR1cm4gXCJrZXl3b3JkXCI7ZWxzZSByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gZWF0UG5Mb2NhbChzdHJlYW0pIHtcbiAgc3RyZWFtLm1hdGNoKC8oXFwuKD89W1xcd19cXC1cXFxcJV0pfFs6XFx3Xy1dfFxcXFxbLVxcXFxffi4hJCYnKCkqKyw7PS8/I0AlXXwlW2EtZlxcZF1bYS1mXFxkXSkrL2kpO1xufVxuZnVuY3Rpb24gdG9rZW5MaXRlcmFsKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBjaDtcbiAgICB3aGlsZSAoKGNoID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKGNoID09IHF1b3RlICYmICFlc2NhcGVkKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBjaCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgdHlwZSwgY29sKSB7XG4gIHN0YXRlLmNvbnRleHQgPSB7XG4gICAgcHJldjogc3RhdGUuY29udGV4dCxcbiAgICBpbmRlbnQ6IHN0YXRlLmluZGVudCxcbiAgICBjb2w6IGNvbCxcbiAgICB0eXBlOiB0eXBlXG4gIH07XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KHN0YXRlKSB7XG4gIHN0YXRlLmluZGVudCA9IHN0YXRlLmNvbnRleHQuaW5kZW50O1xuICBzdGF0ZS5jb250ZXh0ID0gc3RhdGUuY29udGV4dC5wcmV2O1xufVxuZXhwb3J0IGNvbnN0IHNwYXJxbCA9IHtcbiAgbmFtZTogXCJzcGFycWxcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgY29udGV4dDogbnVsbCxcbiAgICAgIGluZGVudDogMCxcbiAgICAgIGNvbDogMFxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIGlmIChzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQuYWxpZ24gPT0gbnVsbCkgc3RhdGUuY29udGV4dC5hbGlnbiA9IGZhbHNlO1xuICAgICAgc3RhdGUuaW5kZW50ID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0eWxlICE9IFwiY29tbWVudFwiICYmIHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC5hbGlnbiA9PSBudWxsICYmIHN0YXRlLmNvbnRleHQudHlwZSAhPSBcInBhdHRlcm5cIikge1xuICAgICAgc3RhdGUuY29udGV4dC5hbGlnbiA9IHRydWU7XG4gICAgfVxuICAgIGlmIChjdXJQdW5jID09IFwiKFwiKSBwdXNoQ29udGV4dChzdGF0ZSwgXCIpXCIsIHN0cmVhbS5jb2x1bW4oKSk7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIltcIikgcHVzaENvbnRleHQoc3RhdGUsIFwiXVwiLCBzdHJlYW0uY29sdW1uKCkpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJ7XCIpIHB1c2hDb250ZXh0KHN0YXRlLCBcIn1cIiwgc3RyZWFtLmNvbHVtbigpKTtlbHNlIGlmICgvW1xcXVxcfVxcKV0vLnRlc3QoY3VyUHVuYykpIHtcbiAgICAgIHdoaWxlIChzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICBpZiAoc3RhdGUuY29udGV4dCAmJiBjdXJQdW5jID09IHN0YXRlLmNvbnRleHQudHlwZSkge1xuICAgICAgICBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgICAgaWYgKGN1clB1bmMgPT0gXCJ9XCIgJiYgc3RhdGUuY29udGV4dCAmJiBzdGF0ZS5jb250ZXh0LnR5cGUgPT0gXCJwYXR0ZXJuXCIpIHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBcIi5cIiAmJiBzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoL2F0b218c3RyaW5nfHZhcmlhYmxlLy50ZXN0KHN0eWxlKSAmJiBzdGF0ZS5jb250ZXh0KSB7XG4gICAgICBpZiAoL1tcXH1cXF1dLy50ZXN0KHN0YXRlLmNvbnRleHQudHlwZSkpIHB1c2hDb250ZXh0KHN0YXRlLCBcInBhdHRlcm5cIiwgc3RyZWFtLmNvbHVtbigpKTtlbHNlIGlmIChzdGF0ZS5jb250ZXh0LnR5cGUgPT0gXCJwYXR0ZXJuXCIgJiYgIXN0YXRlLmNvbnRleHQuYWxpZ24pIHtcbiAgICAgICAgc3RhdGUuY29udGV4dC5hbGlnbiA9IHRydWU7XG4gICAgICAgIHN0YXRlLmNvbnRleHQuY29sID0gc3RyZWFtLmNvbHVtbigpO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgdmFyIGZpcnN0Q2hhciA9IHRleHRBZnRlciAmJiB0ZXh0QWZ0ZXIuY2hhckF0KDApO1xuICAgIHZhciBjb250ZXh0ID0gc3RhdGUuY29udGV4dDtcbiAgICBpZiAoL1tcXF1cXH1dLy50ZXN0KGZpcnN0Q2hhcikpIHdoaWxlIChjb250ZXh0ICYmIGNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgY29udGV4dCA9IGNvbnRleHQucHJldjtcbiAgICB2YXIgY2xvc2luZyA9IGNvbnRleHQgJiYgZmlyc3RDaGFyID09IGNvbnRleHQudHlwZTtcbiAgICBpZiAoIWNvbnRleHQpIHJldHVybiAwO2Vsc2UgaWYgKGNvbnRleHQudHlwZSA9PSBcInBhdHRlcm5cIikgcmV0dXJuIGNvbnRleHQuY29sO2Vsc2UgaWYgKGNvbnRleHQuYWxpZ24pIHJldHVybiBjb250ZXh0LmNvbCArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGNvbnRleHQuaW5kZW50ICsgKGNsb3NpbmcgPyAwIDogY3gudW5pdCk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=