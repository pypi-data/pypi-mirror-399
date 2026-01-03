"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3614],{

/***/ 43614
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   jinja2: () => (/* binding */ jinja2)
/* harmony export */ });
var keywords = ["and", "as", "block", "endblock", "by", "cycle", "debug", "else", "elif", "extends", "filter", "endfilter", "firstof", "do", "for", "endfor", "if", "endif", "ifchanged", "endifchanged", "ifequal", "endifequal", "ifnotequal", "set", "raw", "endraw", "endifnotequal", "in", "include", "load", "not", "now", "or", "parsed", "regroup", "reversed", "spaceless", "call", "endcall", "macro", "endmacro", "endspaceless", "ssi", "templatetag", "openblock", "closeblock", "openvariable", "closevariable", "without", "context", "openbrace", "closebrace", "opencomment", "closecomment", "widthratio", "url", "with", "endwith", "get_current_language", "trans", "endtrans", "noop", "blocktrans", "endblocktrans", "get_available_languages", "get_current_language_bidi", "pluralize", "autoescape", "endautoescape"],
  operator = /^[+\-*&%=<>!?|~^]/,
  sign = /^[:\[\(\{]/,
  atom = ["true", "false"],
  number = /^(\d[+\-\*\/])?\d+(\.\d+)?/;
keywords = new RegExp("((" + keywords.join(")|(") + "))\\b");
atom = new RegExp("((" + atom.join(")|(") + "))\\b");
function tokenBase(stream, state) {
  var ch = stream.peek();

  //Comment
  if (state.incomment) {
    if (!stream.skipTo("#}")) {
      stream.skipToEnd();
    } else {
      stream.eatWhile(/\#|}/);
      state.incomment = false;
    }
    return "comment";
    //Tag
  } else if (state.intag) {
    //After operator
    if (state.operator) {
      state.operator = false;
      if (stream.match(atom)) {
        return "atom";
      }
      if (stream.match(number)) {
        return "number";
      }
    }
    //After sign
    if (state.sign) {
      state.sign = false;
      if (stream.match(atom)) {
        return "atom";
      }
      if (stream.match(number)) {
        return "number";
      }
    }
    if (state.instring) {
      if (ch == state.instring) {
        state.instring = false;
      }
      stream.next();
      return "string";
    } else if (ch == "'" || ch == '"') {
      state.instring = ch;
      stream.next();
      return "string";
    } else if (state.inbraces > 0 && ch == ")") {
      stream.next();
      state.inbraces--;
    } else if (ch == "(") {
      stream.next();
      state.inbraces++;
    } else if (state.inbrackets > 0 && ch == "]") {
      stream.next();
      state.inbrackets--;
    } else if (ch == "[") {
      stream.next();
      state.inbrackets++;
    } else if (!state.lineTag && (stream.match(state.intag + "}") || stream.eat("-") && stream.match(state.intag + "}"))) {
      state.intag = false;
      return "tag";
    } else if (stream.match(operator)) {
      state.operator = true;
      return "operator";
    } else if (stream.match(sign)) {
      state.sign = true;
    } else {
      if (stream.column() == 1 && state.lineTag && stream.match(keywords)) {
        //allow nospace after tag before the keyword
        return "keyword";
      }
      if (stream.eat(" ") || stream.sol()) {
        if (stream.match(keywords)) {
          return "keyword";
        }
        if (stream.match(atom)) {
          return "atom";
        }
        if (stream.match(number)) {
          return "number";
        }
        if (stream.sol()) {
          stream.next();
        }
      } else {
        stream.next();
      }
    }
    return "variable";
  } else if (stream.eat("{")) {
    if (stream.eat("#")) {
      state.incomment = true;
      if (!stream.skipTo("#}")) {
        stream.skipToEnd();
      } else {
        stream.eatWhile(/\#|}/);
        state.incomment = false;
      }
      return "comment";
      //Open tag
    } else if (ch = stream.eat(/\{|%/)) {
      //Cache close tag
      state.intag = ch;
      state.inbraces = 0;
      state.inbrackets = 0;
      if (ch == "{") {
        state.intag = "}";
      }
      stream.eat("-");
      return "tag";
    }
    //Line statements
  } else if (stream.eat('#')) {
    if (stream.peek() == '#') {
      stream.skipToEnd();
      return "comment";
    } else if (!stream.eol()) {
      state.intag = true;
      state.lineTag = true;
      state.inbraces = 0;
      state.inbrackets = 0;
      return "tag";
    }
  }
  stream.next();
}
;
const jinja2 = {
  name: "jinja2",
  startState: function () {
    return {
      tokenize: tokenBase,
      inbrackets: 0,
      inbraces: 0
    };
  },
  token: function (stream, state) {
    var style = state.tokenize(stream, state);
    if (stream.eol() && state.lineTag && !state.instring && state.inbraces == 0 && state.inbrackets == 0) {
      //Close line statement at the EOL
      state.intag = false;
      state.lineTag = false;
    }
    return style;
  },
  languageData: {
    commentTokens: {
      block: {
        open: "{#",
        close: "#}",
        line: "##"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzYxNC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvamluamEyLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBrZXl3b3JkcyA9IFtcImFuZFwiLCBcImFzXCIsIFwiYmxvY2tcIiwgXCJlbmRibG9ja1wiLCBcImJ5XCIsIFwiY3ljbGVcIiwgXCJkZWJ1Z1wiLCBcImVsc2VcIiwgXCJlbGlmXCIsIFwiZXh0ZW5kc1wiLCBcImZpbHRlclwiLCBcImVuZGZpbHRlclwiLCBcImZpcnN0b2ZcIiwgXCJkb1wiLCBcImZvclwiLCBcImVuZGZvclwiLCBcImlmXCIsIFwiZW5kaWZcIiwgXCJpZmNoYW5nZWRcIiwgXCJlbmRpZmNoYW5nZWRcIiwgXCJpZmVxdWFsXCIsIFwiZW5kaWZlcXVhbFwiLCBcImlmbm90ZXF1YWxcIiwgXCJzZXRcIiwgXCJyYXdcIiwgXCJlbmRyYXdcIiwgXCJlbmRpZm5vdGVxdWFsXCIsIFwiaW5cIiwgXCJpbmNsdWRlXCIsIFwibG9hZFwiLCBcIm5vdFwiLCBcIm5vd1wiLCBcIm9yXCIsIFwicGFyc2VkXCIsIFwicmVncm91cFwiLCBcInJldmVyc2VkXCIsIFwic3BhY2VsZXNzXCIsIFwiY2FsbFwiLCBcImVuZGNhbGxcIiwgXCJtYWNyb1wiLCBcImVuZG1hY3JvXCIsIFwiZW5kc3BhY2VsZXNzXCIsIFwic3NpXCIsIFwidGVtcGxhdGV0YWdcIiwgXCJvcGVuYmxvY2tcIiwgXCJjbG9zZWJsb2NrXCIsIFwib3BlbnZhcmlhYmxlXCIsIFwiY2xvc2V2YXJpYWJsZVwiLCBcIndpdGhvdXRcIiwgXCJjb250ZXh0XCIsIFwib3BlbmJyYWNlXCIsIFwiY2xvc2VicmFjZVwiLCBcIm9wZW5jb21tZW50XCIsIFwiY2xvc2Vjb21tZW50XCIsIFwid2lkdGhyYXRpb1wiLCBcInVybFwiLCBcIndpdGhcIiwgXCJlbmR3aXRoXCIsIFwiZ2V0X2N1cnJlbnRfbGFuZ3VhZ2VcIiwgXCJ0cmFuc1wiLCBcImVuZHRyYW5zXCIsIFwibm9vcFwiLCBcImJsb2NrdHJhbnNcIiwgXCJlbmRibG9ja3RyYW5zXCIsIFwiZ2V0X2F2YWlsYWJsZV9sYW5ndWFnZXNcIiwgXCJnZXRfY3VycmVudF9sYW5ndWFnZV9iaWRpXCIsIFwicGx1cmFsaXplXCIsIFwiYXV0b2VzY2FwZVwiLCBcImVuZGF1dG9lc2NhcGVcIl0sXG4gIG9wZXJhdG9yID0gL15bK1xcLSomJT08PiE/fH5eXS8sXG4gIHNpZ24gPSAvXls6XFxbXFwoXFx7XS8sXG4gIGF0b20gPSBbXCJ0cnVlXCIsIFwiZmFsc2VcIl0sXG4gIG51bWJlciA9IC9eKFxcZFsrXFwtXFwqXFwvXSk/XFxkKyhcXC5cXGQrKT8vO1xua2V5d29yZHMgPSBuZXcgUmVnRXhwKFwiKChcIiArIGtleXdvcmRzLmpvaW4oXCIpfChcIikgKyBcIikpXFxcXGJcIik7XG5hdG9tID0gbmV3IFJlZ0V4cChcIigoXCIgKyBhdG9tLmpvaW4oXCIpfChcIikgKyBcIikpXFxcXGJcIik7XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpO1xuXG4gIC8vQ29tbWVudFxuICBpZiAoc3RhdGUuaW5jb21tZW50KSB7XG4gICAgaWYgKCFzdHJlYW0uc2tpcFRvKFwiI31cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9cXCN8fS8pO1xuICAgICAgc3RhdGUuaW5jb21tZW50ID0gZmFsc2U7XG4gICAgfVxuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICAvL1RhZ1xuICB9IGVsc2UgaWYgKHN0YXRlLmludGFnKSB7XG4gICAgLy9BZnRlciBvcGVyYXRvclxuICAgIGlmIChzdGF0ZS5vcGVyYXRvcikge1xuICAgICAgc3RhdGUub3BlcmF0b3IgPSBmYWxzZTtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goYXRvbSkpIHtcbiAgICAgICAgcmV0dXJuIFwiYXRvbVwiO1xuICAgICAgfVxuICAgICAgaWYgKHN0cmVhbS5tYXRjaChudW1iZXIpKSB7XG4gICAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgICAgfVxuICAgIH1cbiAgICAvL0FmdGVyIHNpZ25cbiAgICBpZiAoc3RhdGUuc2lnbikge1xuICAgICAgc3RhdGUuc2lnbiA9IGZhbHNlO1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaChhdG9tKSkge1xuICAgICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKG51bWJlcikpIHtcbiAgICAgICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChzdGF0ZS5pbnN0cmluZykge1xuICAgICAgaWYgKGNoID09IHN0YXRlLmluc3RyaW5nKSB7XG4gICAgICAgIHN0YXRlLmluc3RyaW5nID0gZmFsc2U7XG4gICAgICB9XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBcIidcIiB8fCBjaCA9PSAnXCInKSB7XG4gICAgICBzdGF0ZS5pbnN0cmluZyA9IGNoO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIH0gZWxzZSBpZiAoc3RhdGUuaW5icmFjZXMgPiAwICYmIGNoID09IFwiKVwiKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgc3RhdGUuaW5icmFjZXMtLTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiKFwiKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgc3RhdGUuaW5icmFjZXMrKztcbiAgICB9IGVsc2UgaWYgKHN0YXRlLmluYnJhY2tldHMgPiAwICYmIGNoID09IFwiXVwiKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgc3RhdGUuaW5icmFja2V0cy0tO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCJbXCIpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS5pbmJyYWNrZXRzKys7XG4gICAgfSBlbHNlIGlmICghc3RhdGUubGluZVRhZyAmJiAoc3RyZWFtLm1hdGNoKHN0YXRlLmludGFnICsgXCJ9XCIpIHx8IHN0cmVhbS5lYXQoXCItXCIpICYmIHN0cmVhbS5tYXRjaChzdGF0ZS5pbnRhZyArIFwifVwiKSkpIHtcbiAgICAgIHN0YXRlLmludGFnID0gZmFsc2U7XG4gICAgICByZXR1cm4gXCJ0YWdcIjtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaChvcGVyYXRvcikpIHtcbiAgICAgIHN0YXRlLm9wZXJhdG9yID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goc2lnbikpIHtcbiAgICAgIHN0YXRlLnNpZ24gPSB0cnVlO1xuICAgIH0gZWxzZSB7XG4gICAgICBpZiAoc3RyZWFtLmNvbHVtbigpID09IDEgJiYgc3RhdGUubGluZVRhZyAmJiBzdHJlYW0ubWF0Y2goa2V5d29yZHMpKSB7XG4gICAgICAgIC8vYWxsb3cgbm9zcGFjZSBhZnRlciB0YWcgYmVmb3JlIHRoZSBrZXl3b3JkXG4gICAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0uZWF0KFwiIFwiKSB8fCBzdHJlYW0uc29sKCkpIHtcbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChrZXl3b3JkcykpIHtcbiAgICAgICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChhdG9tKSkge1xuICAgICAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICAgICAgfVxuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKG51bWJlcikpIHtcbiAgICAgICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICAgICAgfVxuICAgICAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIHtcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KFwie1wiKSkge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiI1wiKSkge1xuICAgICAgc3RhdGUuaW5jb21tZW50ID0gdHJ1ZTtcbiAgICAgIGlmICghc3RyZWFtLnNraXBUbyhcIiN9XCIpKSB7XG4gICAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvXFwjfH0vKTtcbiAgICAgICAgc3RhdGUuaW5jb21tZW50ID0gZmFsc2U7XG4gICAgICB9XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgICAvL09wZW4gdGFnXG4gICAgfSBlbHNlIGlmIChjaCA9IHN0cmVhbS5lYXQoL1xce3wlLykpIHtcbiAgICAgIC8vQ2FjaGUgY2xvc2UgdGFnXG4gICAgICBzdGF0ZS5pbnRhZyA9IGNoO1xuICAgICAgc3RhdGUuaW5icmFjZXMgPSAwO1xuICAgICAgc3RhdGUuaW5icmFja2V0cyA9IDA7XG4gICAgICBpZiAoY2ggPT0gXCJ7XCIpIHtcbiAgICAgICAgc3RhdGUuaW50YWcgPSBcIn1cIjtcbiAgICAgIH1cbiAgICAgIHN0cmVhbS5lYXQoXCItXCIpO1xuICAgICAgcmV0dXJuIFwidGFnXCI7XG4gICAgfVxuICAgIC8vTGluZSBzdGF0ZW1lbnRzXG4gIH0gZWxzZSBpZiAoc3RyZWFtLmVhdCgnIycpKSB7XG4gICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJyMnKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfSBlbHNlIGlmICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICBzdGF0ZS5pbnRhZyA9IHRydWU7XG4gICAgICBzdGF0ZS5saW5lVGFnID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmluYnJhY2VzID0gMDtcbiAgICAgIHN0YXRlLmluYnJhY2tldHMgPSAwO1xuICAgICAgcmV0dXJuIFwidGFnXCI7XG4gICAgfVxuICB9XG4gIHN0cmVhbS5uZXh0KCk7XG59XG47XG5leHBvcnQgY29uc3QgamluamEyID0ge1xuICBuYW1lOiBcImppbmphMlwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBpbmJyYWNrZXRzOiAwLFxuICAgICAgaW5icmFjZXM6IDBcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3RyZWFtLmVvbCgpICYmIHN0YXRlLmxpbmVUYWcgJiYgIXN0YXRlLmluc3RyaW5nICYmIHN0YXRlLmluYnJhY2VzID09IDAgJiYgc3RhdGUuaW5icmFja2V0cyA9PSAwKSB7XG4gICAgICAvL0Nsb3NlIGxpbmUgc3RhdGVtZW50IGF0IHRoZSBFT0xcbiAgICAgIHN0YXRlLmludGFnID0gZmFsc2U7XG4gICAgICBzdGF0ZS5saW5lVGFnID0gZmFsc2U7XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCJ7I1wiLFxuICAgICAgICBjbG9zZTogXCIjfVwiLFxuICAgICAgICBsaW5lOiBcIiMjXCJcbiAgICAgIH1cbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==