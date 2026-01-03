"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3899],{

/***/ 83899
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   tiki: () => (/* binding */ tiki)
/* harmony export */ });
function inBlock(style, terminator, returnTokenizer) {
  return function (stream, state) {
    while (!stream.eol()) {
      if (stream.match(terminator)) {
        state.tokenize = inText;
        break;
      }
      stream.next();
    }
    if (returnTokenizer) state.tokenize = returnTokenizer;
    return style;
  };
}
function inLine(style) {
  return function (stream, state) {
    while (!stream.eol()) {
      stream.next();
    }
    state.tokenize = inText;
    return style;
  };
}
function inText(stream, state) {
  function chain(parser) {
    state.tokenize = parser;
    return parser(stream, state);
  }
  var sol = stream.sol();
  var ch = stream.next();

  //non start of line
  switch (ch) {
    //switch is generally much faster than if, so it is used here
    case "{":
      //plugin
      stream.eat("/");
      stream.eatSpace();
      stream.eatWhile(/[^\s\u00a0=\"\'\/?(}]/);
      state.tokenize = inPlugin;
      return "tag";
    case "_":
      //bold
      if (stream.eat("_")) return chain(inBlock("strong", "__", inText));
      break;
    case "'":
      //italics
      if (stream.eat("'")) return chain(inBlock("em", "''", inText));
      break;
    case "(":
      // Wiki Link
      if (stream.eat("(")) return chain(inBlock("link", "))", inText));
      break;
    case "[":
      // Weblink
      return chain(inBlock("url", "]", inText));
      // removed by dead control flow

    case "|":
      //table
      if (stream.eat("|")) return chain(inBlock("comment", "||"));
      break;
    case "-":
      if (stream.eat("=")) {
        //titleBar
        return chain(inBlock("header string", "=-", inText));
      } else if (stream.eat("-")) {
        //deleted
        return chain(inBlock("error tw-deleted", "--", inText));
      }
      break;
    case "=":
      //underline
      if (stream.match("==")) return chain(inBlock("tw-underline", "===", inText));
      break;
    case ":":
      if (stream.eat(":")) return chain(inBlock("comment", "::"));
      break;
    case "^":
      //box
      return chain(inBlock("tw-box", "^"));
      // removed by dead control flow

    case "~":
      //np
      if (stream.match("np~")) return chain(inBlock("meta", "~/np~"));
      break;
  }

  //start of line types
  if (sol) {
    switch (ch) {
      case "!":
        //header at start of line
        if (stream.match('!!!!!')) {
          return chain(inLine("header string"));
        } else if (stream.match('!!!!')) {
          return chain(inLine("header string"));
        } else if (stream.match('!!!')) {
          return chain(inLine("header string"));
        } else if (stream.match('!!')) {
          return chain(inLine("header string"));
        } else {
          return chain(inLine("header string"));
        }
        // removed by dead control flow

      case "*": //unordered list line item, or <li /> at start of line
      case "#": //ordered list line item, or <li /> at start of line
      case "+":
        //ordered list line item, or <li /> at start of line
        return chain(inLine("tw-listitem bracket"));
        // removed by dead control flow

    }
  }

  //stream.eatWhile(/[&{]/); was eating up plugins, turned off to act less like html and more like tiki
  return null;
}

// Return variables for tokenizers
var pluginName, type;
function inPlugin(stream, state) {
  var ch = stream.next();
  var peek = stream.peek();
  if (ch == "}") {
    state.tokenize = inText;
    //type = ch == ")" ? "endPlugin" : "selfclosePlugin"; inPlugin
    return "tag";
  } else if (ch == "(" || ch == ")") {
    return "bracket";
  } else if (ch == "=") {
    type = "equals";
    if (peek == ">") {
      stream.next();
      peek = stream.peek();
    }

    //here we detect values directly after equal character with no quotes
    if (!/[\'\"]/.test(peek)) {
      state.tokenize = inAttributeNoQuote();
    }
    //end detect values

    return "operator";
  } else if (/[\'\"]/.test(ch)) {
    state.tokenize = inAttribute(ch);
    return state.tokenize(stream, state);
  } else {
    stream.eatWhile(/[^\s\u00a0=\"\'\/?]/);
    return "keyword";
  }
}
function inAttribute(quote) {
  return function (stream, state) {
    while (!stream.eol()) {
      if (stream.next() == quote) {
        state.tokenize = inPlugin;
        break;
      }
    }
    return "string";
  };
}
function inAttributeNoQuote() {
  return function (stream, state) {
    while (!stream.eol()) {
      var ch = stream.next();
      var peek = stream.peek();
      if (ch == " " || ch == "," || /[ )}]/.test(peek)) {
        state.tokenize = inPlugin;
        break;
      }
    }
    return "string";
  };
}
var curState, setStyle;
function pass() {
  for (var i = arguments.length - 1; i >= 0; i--) curState.cc.push(arguments[i]);
}
function cont() {
  pass.apply(null, arguments);
  return true;
}
function pushContext(pluginName, startOfLine) {
  var noIndent = curState.context && curState.context.noIndent;
  curState.context = {
    prev: curState.context,
    pluginName: pluginName,
    indent: curState.indented,
    startOfLine: startOfLine,
    noIndent: noIndent
  };
}
function popContext() {
  if (curState.context) curState.context = curState.context.prev;
}
function element(type) {
  if (type == "openPlugin") {
    curState.pluginName = pluginName;
    return cont(attributes, endplugin(curState.startOfLine));
  } else if (type == "closePlugin") {
    var err = false;
    if (curState.context) {
      err = curState.context.pluginName != pluginName;
      popContext();
    } else {
      err = true;
    }
    if (err) setStyle = "error";
    return cont(endcloseplugin(err));
  } else if (type == "string") {
    if (!curState.context || curState.context.name != "!cdata") pushContext("!cdata");
    if (curState.tokenize == inText) popContext();
    return cont();
  } else return cont();
}
function endplugin(startOfLine) {
  return function (type) {
    if (type == "selfclosePlugin" || type == "endPlugin") return cont();
    if (type == "endPlugin") {
      pushContext(curState.pluginName, startOfLine);
      return cont();
    }
    return cont();
  };
}
function endcloseplugin(err) {
  return function (type) {
    if (err) setStyle = "error";
    if (type == "endPlugin") return cont();
    return pass();
  };
}
function attributes(type) {
  if (type == "keyword") {
    setStyle = "attribute";
    return cont(attributes);
  }
  if (type == "equals") return cont(attvalue, attributes);
  return pass();
}
function attvalue(type) {
  if (type == "keyword") {
    setStyle = "string";
    return cont();
  }
  if (type == "string") return cont(attvaluemaybe);
  return pass();
}
function attvaluemaybe(type) {
  if (type == "string") return cont(attvaluemaybe);else return pass();
}
const tiki = {
  name: "tiki",
  startState: function () {
    return {
      tokenize: inText,
      cc: [],
      indented: 0,
      startOfLine: true,
      pluginName: null,
      context: null
    };
  },
  token: function (stream, state) {
    if (stream.sol()) {
      state.startOfLine = true;
      state.indented = stream.indentation();
    }
    if (stream.eatSpace()) return null;
    setStyle = type = pluginName = null;
    var style = state.tokenize(stream, state);
    if ((style || type) && style != "comment") {
      curState = state;
      while (true) {
        var comb = state.cc.pop() || element;
        if (comb(type || style)) break;
      }
    }
    state.startOfLine = false;
    return setStyle || style;
  },
  indent: function (state, textAfter, cx) {
    var context = state.context;
    if (context && context.noIndent) return 0;
    if (context && /^{\//.test(textAfter)) context = context.prev;
    while (context && !context.startOfLine) context = context.prev;
    if (context) return context.indent + cx.unit;else return 0;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzg5OS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdGlraS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBpbkJsb2NrKHN0eWxlLCB0ZXJtaW5hdG9yLCByZXR1cm5Ub2tlbml6ZXIpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgd2hpbGUgKCFzdHJlYW0uZW9sKCkpIHtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2godGVybWluYXRvcikpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSBpblRleHQ7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICB9XG4gICAgaWYgKHJldHVyblRva2VuaXplcikgc3RhdGUudG9rZW5pemUgPSByZXR1cm5Ub2tlbml6ZXI7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9O1xufVxuZnVuY3Rpb24gaW5MaW5lKHN0eWxlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICBzdGF0ZS50b2tlbml6ZSA9IGluVGV4dDtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH07XG59XG5mdW5jdGlvbiBpblRleHQoc3RyZWFtLCBzdGF0ZSkge1xuICBmdW5jdGlvbiBjaGFpbihwYXJzZXIpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHBhcnNlcjtcbiAgICByZXR1cm4gcGFyc2VyKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIHZhciBzb2wgPSBzdHJlYW0uc29sKCk7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG5cbiAgLy9ub24gc3RhcnQgb2YgbGluZVxuICBzd2l0Y2ggKGNoKSB7XG4gICAgLy9zd2l0Y2ggaXMgZ2VuZXJhbGx5IG11Y2ggZmFzdGVyIHRoYW4gaWYsIHNvIGl0IGlzIHVzZWQgaGVyZVxuICAgIGNhc2UgXCJ7XCI6XG4gICAgICAvL3BsdWdpblxuICAgICAgc3RyZWFtLmVhdChcIi9cIik7XG4gICAgICBzdHJlYW0uZWF0U3BhY2UoKTtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW15cXHNcXHUwMGEwPVxcXCJcXCdcXC8/KH1dLyk7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IGluUGx1Z2luO1xuICAgICAgcmV0dXJuIFwidGFnXCI7XG4gICAgY2FzZSBcIl9cIjpcbiAgICAgIC8vYm9sZFxuICAgICAgaWYgKHN0cmVhbS5lYXQoXCJfXCIpKSByZXR1cm4gY2hhaW4oaW5CbG9jayhcInN0cm9uZ1wiLCBcIl9fXCIsIGluVGV4dCkpO1xuICAgICAgYnJlYWs7XG4gICAgY2FzZSBcIidcIjpcbiAgICAgIC8vaXRhbGljc1xuICAgICAgaWYgKHN0cmVhbS5lYXQoXCInXCIpKSByZXR1cm4gY2hhaW4oaW5CbG9jayhcImVtXCIsIFwiJydcIiwgaW5UZXh0KSk7XG4gICAgICBicmVhaztcbiAgICBjYXNlIFwiKFwiOlxuICAgICAgLy8gV2lraSBMaW5rXG4gICAgICBpZiAoc3RyZWFtLmVhdChcIihcIikpIHJldHVybiBjaGFpbihpbkJsb2NrKFwibGlua1wiLCBcIikpXCIsIGluVGV4dCkpO1xuICAgICAgYnJlYWs7XG4gICAgY2FzZSBcIltcIjpcbiAgICAgIC8vIFdlYmxpbmtcbiAgICAgIHJldHVybiBjaGFpbihpbkJsb2NrKFwidXJsXCIsIFwiXVwiLCBpblRleHQpKTtcbiAgICAgIGJyZWFrO1xuICAgIGNhc2UgXCJ8XCI6XG4gICAgICAvL3RhYmxlXG4gICAgICBpZiAoc3RyZWFtLmVhdChcInxcIikpIHJldHVybiBjaGFpbihpbkJsb2NrKFwiY29tbWVudFwiLCBcInx8XCIpKTtcbiAgICAgIGJyZWFrO1xuICAgIGNhc2UgXCItXCI6XG4gICAgICBpZiAoc3RyZWFtLmVhdChcIj1cIikpIHtcbiAgICAgICAgLy90aXRsZUJhclxuICAgICAgICByZXR1cm4gY2hhaW4oaW5CbG9jayhcImhlYWRlciBzdHJpbmdcIiwgXCI9LVwiLCBpblRleHQpKTtcbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdChcIi1cIikpIHtcbiAgICAgICAgLy9kZWxldGVkXG4gICAgICAgIHJldHVybiBjaGFpbihpbkJsb2NrKFwiZXJyb3IgdHctZGVsZXRlZFwiLCBcIi0tXCIsIGluVGV4dCkpO1xuICAgICAgfVxuICAgICAgYnJlYWs7XG4gICAgY2FzZSBcIj1cIjpcbiAgICAgIC8vdW5kZXJsaW5lXG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKFwiPT1cIikpIHJldHVybiBjaGFpbihpbkJsb2NrKFwidHctdW5kZXJsaW5lXCIsIFwiPT09XCIsIGluVGV4dCkpO1xuICAgICAgYnJlYWs7XG4gICAgY2FzZSBcIjpcIjpcbiAgICAgIGlmIChzdHJlYW0uZWF0KFwiOlwiKSkgcmV0dXJuIGNoYWluKGluQmxvY2soXCJjb21tZW50XCIsIFwiOjpcIikpO1xuICAgICAgYnJlYWs7XG4gICAgY2FzZSBcIl5cIjpcbiAgICAgIC8vYm94XG4gICAgICByZXR1cm4gY2hhaW4oaW5CbG9jayhcInR3LWJveFwiLCBcIl5cIikpO1xuICAgICAgYnJlYWs7XG4gICAgY2FzZSBcIn5cIjpcbiAgICAgIC8vbnBcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goXCJucH5cIikpIHJldHVybiBjaGFpbihpbkJsb2NrKFwibWV0YVwiLCBcIn4vbnB+XCIpKTtcbiAgICAgIGJyZWFrO1xuICB9XG5cbiAgLy9zdGFydCBvZiBsaW5lIHR5cGVzXG4gIGlmIChzb2wpIHtcbiAgICBzd2l0Y2ggKGNoKSB7XG4gICAgICBjYXNlIFwiIVwiOlxuICAgICAgICAvL2hlYWRlciBhdCBzdGFydCBvZiBsaW5lXG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goJyEhISEhJykpIHtcbiAgICAgICAgICByZXR1cm4gY2hhaW4oaW5MaW5lKFwiaGVhZGVyIHN0cmluZ1wiKSk7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKCchISEhJykpIHtcbiAgICAgICAgICByZXR1cm4gY2hhaW4oaW5MaW5lKFwiaGVhZGVyIHN0cmluZ1wiKSk7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKCchISEnKSkge1xuICAgICAgICAgIHJldHVybiBjaGFpbihpbkxpbmUoXCJoZWFkZXIgc3RyaW5nXCIpKTtcbiAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goJyEhJykpIHtcbiAgICAgICAgICByZXR1cm4gY2hhaW4oaW5MaW5lKFwiaGVhZGVyIHN0cmluZ1wiKSk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgcmV0dXJuIGNoYWluKGluTGluZShcImhlYWRlciBzdHJpbmdcIikpO1xuICAgICAgICB9XG4gICAgICAgIGJyZWFrO1xuICAgICAgY2FzZSBcIipcIjogLy91bm9yZGVyZWQgbGlzdCBsaW5lIGl0ZW0sIG9yIDxsaSAvPiBhdCBzdGFydCBvZiBsaW5lXG4gICAgICBjYXNlIFwiI1wiOiAvL29yZGVyZWQgbGlzdCBsaW5lIGl0ZW0sIG9yIDxsaSAvPiBhdCBzdGFydCBvZiBsaW5lXG4gICAgICBjYXNlIFwiK1wiOlxuICAgICAgICAvL29yZGVyZWQgbGlzdCBsaW5lIGl0ZW0sIG9yIDxsaSAvPiBhdCBzdGFydCBvZiBsaW5lXG4gICAgICAgIHJldHVybiBjaGFpbihpbkxpbmUoXCJ0dy1saXN0aXRlbSBicmFja2V0XCIpKTtcbiAgICAgICAgYnJlYWs7XG4gICAgfVxuICB9XG5cbiAgLy9zdHJlYW0uZWF0V2hpbGUoL1sme10vKTsgd2FzIGVhdGluZyB1cCBwbHVnaW5zLCB0dXJuZWQgb2ZmIHRvIGFjdCBsZXNzIGxpa2UgaHRtbCBhbmQgbW9yZSBsaWtlIHRpa2lcbiAgcmV0dXJuIG51bGw7XG59XG5cbi8vIFJldHVybiB2YXJpYWJsZXMgZm9yIHRva2VuaXplcnNcbnZhciBwbHVnaW5OYW1lLCB0eXBlO1xuZnVuY3Rpb24gaW5QbHVnaW4oc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICB2YXIgcGVlayA9IHN0cmVhbS5wZWVrKCk7XG4gIGlmIChjaCA9PSBcIn1cIikge1xuICAgIHN0YXRlLnRva2VuaXplID0gaW5UZXh0O1xuICAgIC8vdHlwZSA9IGNoID09IFwiKVwiID8gXCJlbmRQbHVnaW5cIiA6IFwic2VsZmNsb3NlUGx1Z2luXCI7IGluUGx1Z2luXG4gICAgcmV0dXJuIFwidGFnXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIoXCIgfHwgY2ggPT0gXCIpXCIpIHtcbiAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI9XCIpIHtcbiAgICB0eXBlID0gXCJlcXVhbHNcIjtcbiAgICBpZiAocGVlayA9PSBcIj5cIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHBlZWsgPSBzdHJlYW0ucGVlaygpO1xuICAgIH1cblxuICAgIC8vaGVyZSB3ZSBkZXRlY3QgdmFsdWVzIGRpcmVjdGx5IGFmdGVyIGVxdWFsIGNoYXJhY3RlciB3aXRoIG5vIHF1b3Rlc1xuICAgIGlmICghL1tcXCdcXFwiXS8udGVzdChwZWVrKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSBpbkF0dHJpYnV0ZU5vUXVvdGUoKTtcbiAgICB9XG4gICAgLy9lbmQgZGV0ZWN0IHZhbHVlc1xuXG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfSBlbHNlIGlmICgvW1xcJ1xcXCJdLy50ZXN0KGNoKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gaW5BdHRyaWJ1dGUoY2gpO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfSBlbHNlIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1teXFxzXFx1MDBhMD1cXFwiXFwnXFwvP10vKTtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cbn1cbmZ1bmN0aW9uIGluQXR0cmlidXRlKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICBpZiAoc3RyZWFtLm5leHQoKSA9PSBxdW90ZSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IGluUGx1Z2luO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5mdW5jdGlvbiBpbkF0dHJpYnV0ZU5vUXVvdGUoKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICAgICAgdmFyIHBlZWsgPSBzdHJlYW0ucGVlaygpO1xuICAgICAgaWYgKGNoID09IFwiIFwiIHx8IGNoID09IFwiLFwiIHx8IC9bICl9XS8udGVzdChwZWVrKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IGluUGx1Z2luO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG52YXIgY3VyU3RhdGUsIHNldFN0eWxlO1xuZnVuY3Rpb24gcGFzcygpIHtcbiAgZm9yICh2YXIgaSA9IGFyZ3VtZW50cy5sZW5ndGggLSAxOyBpID49IDA7IGktLSkgY3VyU3RhdGUuY2MucHVzaChhcmd1bWVudHNbaV0pO1xufVxuZnVuY3Rpb24gY29udCgpIHtcbiAgcGFzcy5hcHBseShudWxsLCBhcmd1bWVudHMpO1xuICByZXR1cm4gdHJ1ZTtcbn1cbmZ1bmN0aW9uIHB1c2hDb250ZXh0KHBsdWdpbk5hbWUsIHN0YXJ0T2ZMaW5lKSB7XG4gIHZhciBub0luZGVudCA9IGN1clN0YXRlLmNvbnRleHQgJiYgY3VyU3RhdGUuY29udGV4dC5ub0luZGVudDtcbiAgY3VyU3RhdGUuY29udGV4dCA9IHtcbiAgICBwcmV2OiBjdXJTdGF0ZS5jb250ZXh0LFxuICAgIHBsdWdpbk5hbWU6IHBsdWdpbk5hbWUsXG4gICAgaW5kZW50OiBjdXJTdGF0ZS5pbmRlbnRlZCxcbiAgICBzdGFydE9mTGluZTogc3RhcnRPZkxpbmUsXG4gICAgbm9JbmRlbnQ6IG5vSW5kZW50XG4gIH07XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KCkge1xuICBpZiAoY3VyU3RhdGUuY29udGV4dCkgY3VyU3RhdGUuY29udGV4dCA9IGN1clN0YXRlLmNvbnRleHQucHJldjtcbn1cbmZ1bmN0aW9uIGVsZW1lbnQodHlwZSkge1xuICBpZiAodHlwZSA9PSBcIm9wZW5QbHVnaW5cIikge1xuICAgIGN1clN0YXRlLnBsdWdpbk5hbWUgPSBwbHVnaW5OYW1lO1xuICAgIHJldHVybiBjb250KGF0dHJpYnV0ZXMsIGVuZHBsdWdpbihjdXJTdGF0ZS5zdGFydE9mTGluZSkpO1xuICB9IGVsc2UgaWYgKHR5cGUgPT0gXCJjbG9zZVBsdWdpblwiKSB7XG4gICAgdmFyIGVyciA9IGZhbHNlO1xuICAgIGlmIChjdXJTdGF0ZS5jb250ZXh0KSB7XG4gICAgICBlcnIgPSBjdXJTdGF0ZS5jb250ZXh0LnBsdWdpbk5hbWUgIT0gcGx1Z2luTmFtZTtcbiAgICAgIHBvcENvbnRleHQoKTtcbiAgICB9IGVsc2Uge1xuICAgICAgZXJyID0gdHJ1ZTtcbiAgICB9XG4gICAgaWYgKGVycikgc2V0U3R5bGUgPSBcImVycm9yXCI7XG4gICAgcmV0dXJuIGNvbnQoZW5kY2xvc2VwbHVnaW4oZXJyKSk7XG4gIH0gZWxzZSBpZiAodHlwZSA9PSBcInN0cmluZ1wiKSB7XG4gICAgaWYgKCFjdXJTdGF0ZS5jb250ZXh0IHx8IGN1clN0YXRlLmNvbnRleHQubmFtZSAhPSBcIiFjZGF0YVwiKSBwdXNoQ29udGV4dChcIiFjZGF0YVwiKTtcbiAgICBpZiAoY3VyU3RhdGUudG9rZW5pemUgPT0gaW5UZXh0KSBwb3BDb250ZXh0KCk7XG4gICAgcmV0dXJuIGNvbnQoKTtcbiAgfSBlbHNlIHJldHVybiBjb250KCk7XG59XG5mdW5jdGlvbiBlbmRwbHVnaW4oc3RhcnRPZkxpbmUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uICh0eXBlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJzZWxmY2xvc2VQbHVnaW5cIiB8fCB0eXBlID09IFwiZW5kUGx1Z2luXCIpIHJldHVybiBjb250KCk7XG4gICAgaWYgKHR5cGUgPT0gXCJlbmRQbHVnaW5cIikge1xuICAgICAgcHVzaENvbnRleHQoY3VyU3RhdGUucGx1Z2luTmFtZSwgc3RhcnRPZkxpbmUpO1xuICAgICAgcmV0dXJuIGNvbnQoKTtcbiAgICB9XG4gICAgcmV0dXJuIGNvbnQoKTtcbiAgfTtcbn1cbmZ1bmN0aW9uIGVuZGNsb3NlcGx1Z2luKGVycikge1xuICByZXR1cm4gZnVuY3Rpb24gKHR5cGUpIHtcbiAgICBpZiAoZXJyKSBzZXRTdHlsZSA9IFwiZXJyb3JcIjtcbiAgICBpZiAodHlwZSA9PSBcImVuZFBsdWdpblwiKSByZXR1cm4gY29udCgpO1xuICAgIHJldHVybiBwYXNzKCk7XG4gIH07XG59XG5mdW5jdGlvbiBhdHRyaWJ1dGVzKHR5cGUpIHtcbiAgaWYgKHR5cGUgPT0gXCJrZXl3b3JkXCIpIHtcbiAgICBzZXRTdHlsZSA9IFwiYXR0cmlidXRlXCI7XG4gICAgcmV0dXJuIGNvbnQoYXR0cmlidXRlcyk7XG4gIH1cbiAgaWYgKHR5cGUgPT0gXCJlcXVhbHNcIikgcmV0dXJuIGNvbnQoYXR0dmFsdWUsIGF0dHJpYnV0ZXMpO1xuICByZXR1cm4gcGFzcygpO1xufVxuZnVuY3Rpb24gYXR0dmFsdWUodHlwZSkge1xuICBpZiAodHlwZSA9PSBcImtleXdvcmRcIikge1xuICAgIHNldFN0eWxlID0gXCJzdHJpbmdcIjtcbiAgICByZXR1cm4gY29udCgpO1xuICB9XG4gIGlmICh0eXBlID09IFwic3RyaW5nXCIpIHJldHVybiBjb250KGF0dHZhbHVlbWF5YmUpO1xuICByZXR1cm4gcGFzcygpO1xufVxuZnVuY3Rpb24gYXR0dmFsdWVtYXliZSh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwic3RyaW5nXCIpIHJldHVybiBjb250KGF0dHZhbHVlbWF5YmUpO2Vsc2UgcmV0dXJuIHBhc3MoKTtcbn1cbmV4cG9ydCBjb25zdCB0aWtpID0ge1xuICBuYW1lOiBcInRpa2lcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogaW5UZXh0LFxuICAgICAgY2M6IFtdLFxuICAgICAgaW5kZW50ZWQ6IDAsXG4gICAgICBzdGFydE9mTGluZTogdHJ1ZSxcbiAgICAgIHBsdWdpbk5hbWU6IG51bGwsXG4gICAgICBjb250ZXh0OiBudWxsXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICBzZXRTdHlsZSA9IHR5cGUgPSBwbHVnaW5OYW1lID0gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoKHN0eWxlIHx8IHR5cGUpICYmIHN0eWxlICE9IFwiY29tbWVudFwiKSB7XG4gICAgICBjdXJTdGF0ZSA9IHN0YXRlO1xuICAgICAgd2hpbGUgKHRydWUpIHtcbiAgICAgICAgdmFyIGNvbWIgPSBzdGF0ZS5jYy5wb3AoKSB8fCBlbGVtZW50O1xuICAgICAgICBpZiAoY29tYih0eXBlIHx8IHN0eWxlKSkgYnJlYWs7XG4gICAgICB9XG4gICAgfVxuICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gZmFsc2U7XG4gICAgcmV0dXJuIHNldFN0eWxlIHx8IHN0eWxlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgIHZhciBjb250ZXh0ID0gc3RhdGUuY29udGV4dDtcbiAgICBpZiAoY29udGV4dCAmJiBjb250ZXh0Lm5vSW5kZW50KSByZXR1cm4gMDtcbiAgICBpZiAoY29udGV4dCAmJiAvXntcXC8vLnRlc3QodGV4dEFmdGVyKSkgY29udGV4dCA9IGNvbnRleHQucHJldjtcbiAgICB3aGlsZSAoY29udGV4dCAmJiAhY29udGV4dC5zdGFydE9mTGluZSkgY29udGV4dCA9IGNvbnRleHQucHJldjtcbiAgICBpZiAoY29udGV4dCkgcmV0dXJuIGNvbnRleHQuaW5kZW50ICsgY3gudW5pdDtlbHNlIHJldHVybiAwO1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=