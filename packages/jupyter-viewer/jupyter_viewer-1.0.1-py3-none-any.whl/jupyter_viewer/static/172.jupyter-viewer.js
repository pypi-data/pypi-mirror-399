"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[172],{

/***/ 10172
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   haxe: () => (/* binding */ haxe),
/* harmony export */   hxml: () => (/* binding */ hxml)
/* harmony export */ });
// Tokenizer

function kw(type) {
  return {
    type: type,
    style: "keyword"
  };
}
var A = kw("keyword a"),
  B = kw("keyword b"),
  C = kw("keyword c");
var operator = kw("operator"),
  atom = {
    type: "atom",
    style: "atom"
  },
  attribute = {
    type: "attribute",
    style: "attribute"
  };
var type = kw("typedef");
var keywords = {
  "if": A,
  "while": A,
  "else": B,
  "do": B,
  "try": B,
  "return": C,
  "break": C,
  "continue": C,
  "new": C,
  "throw": C,
  "var": kw("var"),
  "inline": attribute,
  "static": attribute,
  "using": kw("import"),
  "public": attribute,
  "private": attribute,
  "cast": kw("cast"),
  "import": kw("import"),
  "macro": kw("macro"),
  "function": kw("function"),
  "catch": kw("catch"),
  "untyped": kw("untyped"),
  "callback": kw("cb"),
  "for": kw("for"),
  "switch": kw("switch"),
  "case": kw("case"),
  "default": kw("default"),
  "in": operator,
  "never": kw("property_access"),
  "trace": kw("trace"),
  "class": type,
  "abstract": type,
  "enum": type,
  "interface": type,
  "typedef": type,
  "extends": type,
  "implements": type,
  "dynamic": type,
  "true": atom,
  "false": atom,
  "null": atom
};
var isOperatorChar = /[+\-*&%=<>!?|]/;
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}
function toUnescaped(stream, end) {
  var escaped = false,
    next;
  while ((next = stream.next()) != null) {
    if (next == end && !escaped) return true;
    escaped = !escaped && next == "\\";
  }
}

// Used as scratch variables to communicate multiple values without
// consing up tons of objects.
var type, content;
function ret(tp, style, cont) {
  type = tp;
  content = cont;
  return style;
}
function haxeTokenBase(stream, state) {
  var ch = stream.next();
  if (ch == '"' || ch == "'") {
    return chain(stream, state, haxeTokenString(ch));
  } else if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
    return ret(ch);
  } else if (ch == "0" && stream.eat(/x/i)) {
    stream.eatWhile(/[\da-f]/i);
    return ret("number", "number");
  } else if (/\d/.test(ch) || ch == "-" && stream.eat(/\d/)) {
    stream.match(/^\d*(?:\.\d*(?!\.))?(?:[eE][+\-]?\d+)?/);
    return ret("number", "number");
  } else if (state.reAllowed && ch == "~" && stream.eat(/\//)) {
    toUnescaped(stream, "/");
    stream.eatWhile(/[gimsu]/);
    return ret("regexp", "string.special");
  } else if (ch == "/") {
    if (stream.eat("*")) {
      return chain(stream, state, haxeTokenComment);
    } else if (stream.eat("/")) {
      stream.skipToEnd();
      return ret("comment", "comment");
    } else {
      stream.eatWhile(isOperatorChar);
      return ret("operator", null, stream.current());
    }
  } else if (ch == "#") {
    stream.skipToEnd();
    return ret("conditional", "meta");
  } else if (ch == "@") {
    stream.eat(/:/);
    stream.eatWhile(/[\w_]/);
    return ret("metadata", "meta");
  } else if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return ret("operator", null, stream.current());
  } else {
    var word;
    if (/[A-Z]/.test(ch)) {
      stream.eatWhile(/[\w_<>]/);
      word = stream.current();
      return ret("type", "type", word);
    } else {
      stream.eatWhile(/[\w_]/);
      var word = stream.current(),
        known = keywords.propertyIsEnumerable(word) && keywords[word];
      return known && state.kwAllowed ? ret(known.type, known.style, word) : ret("variable", "variable", word);
    }
  }
}
function haxeTokenString(quote) {
  return function (stream, state) {
    if (toUnescaped(stream, quote)) state.tokenize = haxeTokenBase;
    return ret("string", "string");
  };
}
function haxeTokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = haxeTokenBase;
      break;
    }
    maybeEnd = ch == "*";
  }
  return ret("comment", "comment");
}

// Parser

var atomicTypes = {
  "atom": true,
  "number": true,
  "variable": true,
  "string": true,
  "regexp": true
};
function HaxeLexical(indented, column, type, align, prev, info) {
  this.indented = indented;
  this.column = column;
  this.type = type;
  this.prev = prev;
  this.info = info;
  if (align != null) this.align = align;
}
function inScope(state, varname) {
  for (var v = state.localVars; v; v = v.next) if (v.name == varname) return true;
}
function parseHaxe(state, style, type, content, stream) {
  var cc = state.cc;
  // Communicate our context to the combinators.
  // (Less wasteful than consing up a hundred closures on every call.)
  cx.state = state;
  cx.stream = stream;
  cx.marked = null, cx.cc = cc;
  if (!state.lexical.hasOwnProperty("align")) state.lexical.align = true;
  while (true) {
    var combinator = cc.length ? cc.pop() : statement;
    if (combinator(type, content)) {
      while (cc.length && cc[cc.length - 1].lex) cc.pop()();
      if (cx.marked) return cx.marked;
      if (type == "variable" && inScope(state, content)) return "variableName.local";
      if (type == "variable" && imported(state, content)) return "variableName.special";
      return style;
    }
  }
}
function imported(state, typename) {
  if (/[a-z]/.test(typename.charAt(0))) return false;
  var len = state.importedtypes.length;
  for (var i = 0; i < len; i++) if (state.importedtypes[i] == typename) return true;
}
function registerimport(importname) {
  var state = cx.state;
  for (var t = state.importedtypes; t; t = t.next) if (t.name == importname) return;
  state.importedtypes = {
    name: importname,
    next: state.importedtypes
  };
}
// Combinator utils

var cx = {
  state: null,
  column: null,
  marked: null,
  cc: null
};
function pass() {
  for (var i = arguments.length - 1; i >= 0; i--) cx.cc.push(arguments[i]);
}
function cont() {
  pass.apply(null, arguments);
  return true;
}
function inList(name, list) {
  for (var v = list; v; v = v.next) if (v.name == name) return true;
  return false;
}
function register(varname) {
  var state = cx.state;
  if (state.context) {
    cx.marked = "def";
    if (inList(varname, state.localVars)) return;
    state.localVars = {
      name: varname,
      next: state.localVars
    };
  } else if (state.globalVars) {
    if (inList(varname, state.globalVars)) return;
    state.globalVars = {
      name: varname,
      next: state.globalVars
    };
  }
}

// Combinators

var defaultVars = {
  name: "this",
  next: null
};
function pushcontext() {
  if (!cx.state.context) cx.state.localVars = defaultVars;
  cx.state.context = {
    prev: cx.state.context,
    vars: cx.state.localVars
  };
}
function popcontext() {
  cx.state.localVars = cx.state.context.vars;
  cx.state.context = cx.state.context.prev;
}
popcontext.lex = true;
function pushlex(type, info) {
  var result = function () {
    var state = cx.state;
    state.lexical = new HaxeLexical(state.indented, cx.stream.column(), type, null, state.lexical, info);
  };
  result.lex = true;
  return result;
}
function poplex() {
  var state = cx.state;
  if (state.lexical.prev) {
    if (state.lexical.type == ")") state.indented = state.lexical.indented;
    state.lexical = state.lexical.prev;
  }
}
poplex.lex = true;
function expect(wanted) {
  function f(type) {
    if (type == wanted) return cont();else if (wanted == ";") return pass();else return cont(f);
  }
  return f;
}
function statement(type) {
  if (type == "@") return cont(metadef);
  if (type == "var") return cont(pushlex("vardef"), vardef1, expect(";"), poplex);
  if (type == "keyword a") return cont(pushlex("form"), expression, statement, poplex);
  if (type == "keyword b") return cont(pushlex("form"), statement, poplex);
  if (type == "{") return cont(pushlex("}"), pushcontext, block, poplex, popcontext);
  if (type == ";") return cont();
  if (type == "attribute") return cont(maybeattribute);
  if (type == "function") return cont(functiondef);
  if (type == "for") return cont(pushlex("form"), expect("("), pushlex(")"), forspec1, expect(")"), poplex, statement, poplex);
  if (type == "variable") return cont(pushlex("stat"), maybelabel);
  if (type == "switch") return cont(pushlex("form"), expression, pushlex("}", "switch"), expect("{"), block, poplex, poplex);
  if (type == "case") return cont(expression, expect(":"));
  if (type == "default") return cont(expect(":"));
  if (type == "catch") return cont(pushlex("form"), pushcontext, expect("("), funarg, expect(")"), statement, poplex, popcontext);
  if (type == "import") return cont(importdef, expect(";"));
  if (type == "typedef") return cont(typedef);
  return pass(pushlex("stat"), expression, expect(";"), poplex);
}
function expression(type) {
  if (atomicTypes.hasOwnProperty(type)) return cont(maybeoperator);
  if (type == "type") return cont(maybeoperator);
  if (type == "function") return cont(functiondef);
  if (type == "keyword c") return cont(maybeexpression);
  if (type == "(") return cont(pushlex(")"), maybeexpression, expect(")"), poplex, maybeoperator);
  if (type == "operator") return cont(expression);
  if (type == "[") return cont(pushlex("]"), commasep(maybeexpression, "]"), poplex, maybeoperator);
  if (type == "{") return cont(pushlex("}"), commasep(objprop, "}"), poplex, maybeoperator);
  return cont();
}
function maybeexpression(type) {
  if (type.match(/[;\}\)\],]/)) return pass();
  return pass(expression);
}
function maybeoperator(type, value) {
  if (type == "operator" && /\+\+|--/.test(value)) return cont(maybeoperator);
  if (type == "operator" || type == ":") return cont(expression);
  if (type == ";") return;
  if (type == "(") return cont(pushlex(")"), commasep(expression, ")"), poplex, maybeoperator);
  if (type == ".") return cont(property, maybeoperator);
  if (type == "[") return cont(pushlex("]"), expression, expect("]"), poplex, maybeoperator);
}
function maybeattribute(type) {
  if (type == "attribute") return cont(maybeattribute);
  if (type == "function") return cont(functiondef);
  if (type == "var") return cont(vardef1);
}
function metadef(type) {
  if (type == ":") return cont(metadef);
  if (type == "variable") return cont(metadef);
  if (type == "(") return cont(pushlex(")"), commasep(metaargs, ")"), poplex, statement);
}
function metaargs(type) {
  if (type == "variable") return cont();
}
function importdef(type, value) {
  if (type == "variable" && /[A-Z]/.test(value.charAt(0))) {
    registerimport(value);
    return cont();
  } else if (type == "variable" || type == "property" || type == "." || value == "*") return cont(importdef);
}
function typedef(type, value) {
  if (type == "variable" && /[A-Z]/.test(value.charAt(0))) {
    registerimport(value);
    return cont();
  } else if (type == "type" && /[A-Z]/.test(value.charAt(0))) {
    return cont();
  }
}
function maybelabel(type) {
  if (type == ":") return cont(poplex, statement);
  return pass(maybeoperator, expect(";"), poplex);
}
function property(type) {
  if (type == "variable") {
    cx.marked = "property";
    return cont();
  }
}
function objprop(type) {
  if (type == "variable") cx.marked = "property";
  if (atomicTypes.hasOwnProperty(type)) return cont(expect(":"), expression);
}
function commasep(what, end) {
  function proceed(type) {
    if (type == ",") return cont(what, proceed);
    if (type == end) return cont();
    return cont(expect(end));
  }
  return function (type) {
    if (type == end) return cont();else return pass(what, proceed);
  };
}
function block(type) {
  if (type == "}") return cont();
  return pass(statement, block);
}
function vardef1(type, value) {
  if (type == "variable") {
    register(value);
    return cont(typeuse, vardef2);
  }
  return cont();
}
function vardef2(type, value) {
  if (value == "=") return cont(expression, vardef2);
  if (type == ",") return cont(vardef1);
}
function forspec1(type, value) {
  if (type == "variable") {
    register(value);
    return cont(forin, expression);
  } else {
    return pass();
  }
}
function forin(_type, value) {
  if (value == "in") return cont();
}
function functiondef(type, value) {
  //function names starting with upper-case letters are recognised as types, so cludging them together here.
  if (type == "variable" || type == "type") {
    register(value);
    return cont(functiondef);
  }
  if (value == "new") return cont(functiondef);
  if (type == "(") return cont(pushlex(")"), pushcontext, commasep(funarg, ")"), poplex, typeuse, statement, popcontext);
}
function typeuse(type) {
  if (type == ":") return cont(typestring);
}
function typestring(type) {
  if (type == "type") return cont();
  if (type == "variable") return cont();
  if (type == "{") return cont(pushlex("}"), commasep(typeprop, "}"), poplex);
}
function typeprop(type) {
  if (type == "variable") return cont(typeuse);
}
function funarg(type, value) {
  if (type == "variable") {
    register(value);
    return cont(typeuse);
  }
}

// Interface
const haxe = {
  name: "haxe",
  startState: function (indentUnit) {
    var defaulttypes = ["Int", "Float", "String", "Void", "Std", "Bool", "Dynamic", "Array"];
    var state = {
      tokenize: haxeTokenBase,
      reAllowed: true,
      kwAllowed: true,
      cc: [],
      lexical: new HaxeLexical(-indentUnit, 0, "block", false),
      importedtypes: defaulttypes,
      context: null,
      indented: 0
    };
    return state;
  },
  token: function (stream, state) {
    if (stream.sol()) {
      if (!state.lexical.hasOwnProperty("align")) state.lexical.align = false;
      state.indented = stream.indentation();
    }
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    if (type == "comment") return style;
    state.reAllowed = !!(type == "operator" || type == "keyword c" || type.match(/^[\[{}\(,;:]$/));
    state.kwAllowed = type != '.';
    return parseHaxe(state, style, type, content, stream);
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != haxeTokenBase) return 0;
    var firstChar = textAfter && textAfter.charAt(0),
      lexical = state.lexical;
    if (lexical.type == "stat" && firstChar == "}") lexical = lexical.prev;
    var type = lexical.type,
      closing = firstChar == type;
    if (type == "vardef") return lexical.indented + 4;else if (type == "form" && firstChar == "{") return lexical.indented;else if (type == "stat" || type == "form") return lexical.indented + cx.unit;else if (lexical.info == "switch" && !closing) return lexical.indented + (/^(?:case|default)\b/.test(textAfter) ? cx.unit : 2 * cx.unit);else if (lexical.align) return lexical.column + (closing ? 0 : 1);else return lexical.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    }
  }
};
const hxml = {
  name: "hxml",
  startState: function () {
    return {
      define: false,
      inString: false
    };
  },
  token: function (stream, state) {
    var ch = stream.peek();
    var sol = stream.sol();

    ///* comments */
    if (ch == "#") {
      stream.skipToEnd();
      return "comment";
    }
    if (sol && ch == "-") {
      var style = "variable-2";
      stream.eat(/-/);
      if (stream.peek() == "-") {
        stream.eat(/-/);
        style = "keyword a";
      }
      if (stream.peek() == "D") {
        stream.eat(/[D]/);
        style = "keyword c";
        state.define = true;
      }
      stream.eatWhile(/[A-Z]/i);
      return style;
    }
    var ch = stream.peek();
    if (state.inString == false && ch == "'") {
      state.inString = true;
      stream.next();
    }
    if (state.inString == true) {
      if (stream.skipTo("'")) {} else {
        stream.skipToEnd();
      }
      if (stream.peek() == "'") {
        stream.next();
        state.inString = false;
      }
      return "string";
    }
    stream.next();
    return null;
  },
  languageData: {
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTcyLmp1cHl0ZXItdmlld2VyLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvaGF4ZS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBUb2tlbml6ZXJcblxuZnVuY3Rpb24ga3codHlwZSkge1xuICByZXR1cm4ge1xuICAgIHR5cGU6IHR5cGUsXG4gICAgc3R5bGU6IFwia2V5d29yZFwiXG4gIH07XG59XG52YXIgQSA9IGt3KFwia2V5d29yZCBhXCIpLFxuICBCID0ga3coXCJrZXl3b3JkIGJcIiksXG4gIEMgPSBrdyhcImtleXdvcmQgY1wiKTtcbnZhciBvcGVyYXRvciA9IGt3KFwib3BlcmF0b3JcIiksXG4gIGF0b20gPSB7XG4gICAgdHlwZTogXCJhdG9tXCIsXG4gICAgc3R5bGU6IFwiYXRvbVwiXG4gIH0sXG4gIGF0dHJpYnV0ZSA9IHtcbiAgICB0eXBlOiBcImF0dHJpYnV0ZVwiLFxuICAgIHN0eWxlOiBcImF0dHJpYnV0ZVwiXG4gIH07XG52YXIgdHlwZSA9IGt3KFwidHlwZWRlZlwiKTtcbnZhciBrZXl3b3JkcyA9IHtcbiAgXCJpZlwiOiBBLFxuICBcIndoaWxlXCI6IEEsXG4gIFwiZWxzZVwiOiBCLFxuICBcImRvXCI6IEIsXG4gIFwidHJ5XCI6IEIsXG4gIFwicmV0dXJuXCI6IEMsXG4gIFwiYnJlYWtcIjogQyxcbiAgXCJjb250aW51ZVwiOiBDLFxuICBcIm5ld1wiOiBDLFxuICBcInRocm93XCI6IEMsXG4gIFwidmFyXCI6IGt3KFwidmFyXCIpLFxuICBcImlubGluZVwiOiBhdHRyaWJ1dGUsXG4gIFwic3RhdGljXCI6IGF0dHJpYnV0ZSxcbiAgXCJ1c2luZ1wiOiBrdyhcImltcG9ydFwiKSxcbiAgXCJwdWJsaWNcIjogYXR0cmlidXRlLFxuICBcInByaXZhdGVcIjogYXR0cmlidXRlLFxuICBcImNhc3RcIjoga3coXCJjYXN0XCIpLFxuICBcImltcG9ydFwiOiBrdyhcImltcG9ydFwiKSxcbiAgXCJtYWNyb1wiOiBrdyhcIm1hY3JvXCIpLFxuICBcImZ1bmN0aW9uXCI6IGt3KFwiZnVuY3Rpb25cIiksXG4gIFwiY2F0Y2hcIjoga3coXCJjYXRjaFwiKSxcbiAgXCJ1bnR5cGVkXCI6IGt3KFwidW50eXBlZFwiKSxcbiAgXCJjYWxsYmFja1wiOiBrdyhcImNiXCIpLFxuICBcImZvclwiOiBrdyhcImZvclwiKSxcbiAgXCJzd2l0Y2hcIjoga3coXCJzd2l0Y2hcIiksXG4gIFwiY2FzZVwiOiBrdyhcImNhc2VcIiksXG4gIFwiZGVmYXVsdFwiOiBrdyhcImRlZmF1bHRcIiksXG4gIFwiaW5cIjogb3BlcmF0b3IsXG4gIFwibmV2ZXJcIjoga3coXCJwcm9wZXJ0eV9hY2Nlc3NcIiksXG4gIFwidHJhY2VcIjoga3coXCJ0cmFjZVwiKSxcbiAgXCJjbGFzc1wiOiB0eXBlLFxuICBcImFic3RyYWN0XCI6IHR5cGUsXG4gIFwiZW51bVwiOiB0eXBlLFxuICBcImludGVyZmFjZVwiOiB0eXBlLFxuICBcInR5cGVkZWZcIjogdHlwZSxcbiAgXCJleHRlbmRzXCI6IHR5cGUsXG4gIFwiaW1wbGVtZW50c1wiOiB0eXBlLFxuICBcImR5bmFtaWNcIjogdHlwZSxcbiAgXCJ0cnVlXCI6IGF0b20sXG4gIFwiZmFsc2VcIjogYXRvbSxcbiAgXCJudWxsXCI6IGF0b21cbn07XG52YXIgaXNPcGVyYXRvckNoYXIgPSAvWytcXC0qJiU9PD4hP3xdLztcbmZ1bmN0aW9uIGNoYWluKHN0cmVhbSwgc3RhdGUsIGYpIHtcbiAgc3RhdGUudG9rZW5pemUgPSBmO1xuICByZXR1cm4gZihzdHJlYW0sIHN0YXRlKTtcbn1cbmZ1bmN0aW9uIHRvVW5lc2NhcGVkKHN0cmVhbSwgZW5kKSB7XG4gIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgbmV4dDtcbiAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgIGlmIChuZXh0ID09IGVuZCAmJiAhZXNjYXBlZCkgcmV0dXJuIHRydWU7XG4gICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIG5leHQgPT0gXCJcXFxcXCI7XG4gIH1cbn1cblxuLy8gVXNlZCBhcyBzY3JhdGNoIHZhcmlhYmxlcyB0byBjb21tdW5pY2F0ZSBtdWx0aXBsZSB2YWx1ZXMgd2l0aG91dFxuLy8gY29uc2luZyB1cCB0b25zIG9mIG9iamVjdHMuXG52YXIgdHlwZSwgY29udGVudDtcbmZ1bmN0aW9uIHJldCh0cCwgc3R5bGUsIGNvbnQpIHtcbiAgdHlwZSA9IHRwO1xuICBjb250ZW50ID0gY29udDtcbiAgcmV0dXJuIHN0eWxlO1xufVxuZnVuY3Rpb24gaGF4ZVRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSAnXCInIHx8IGNoID09IFwiJ1wiKSB7XG4gICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIGhheGVUb2tlblN0cmluZyhjaCkpO1xuICB9IGVsc2UgaWYgKC9bXFxbXFxde31cXChcXCksO1xcOlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgcmV0dXJuIHJldChjaCk7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIwXCIgJiYgc3RyZWFtLmVhdCgveC9pKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcZGEtZl0vaSk7XG4gICAgcmV0dXJuIHJldChcIm51bWJlclwiLCBcIm51bWJlclwiKTtcbiAgfSBlbHNlIGlmICgvXFxkLy50ZXN0KGNoKSB8fCBjaCA9PSBcIi1cIiAmJiBzdHJlYW0uZWF0KC9cXGQvKSkge1xuICAgIHN0cmVhbS5tYXRjaCgvXlxcZCooPzpcXC5cXGQqKD8hXFwuKSk/KD86W2VFXVsrXFwtXT9cXGQrKT8vKTtcbiAgICByZXR1cm4gcmV0KFwibnVtYmVyXCIsIFwibnVtYmVyXCIpO1xuICB9IGVsc2UgaWYgKHN0YXRlLnJlQWxsb3dlZCAmJiBjaCA9PSBcIn5cIiAmJiBzdHJlYW0uZWF0KC9cXC8vKSkge1xuICAgIHRvVW5lc2NhcGVkKHN0cmVhbSwgXCIvXCIpO1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW2dpbXN1XS8pO1xuICAgIHJldHVybiByZXQoXCJyZWdleHBcIiwgXCJzdHJpbmcuc3BlY2lhbFwiKTtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIi9cIikge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIGhheGVUb2tlbkNvbW1lbnQpO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiByZXQoXCJjb21tZW50XCIsIFwiY29tbWVudFwiKTtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKGlzT3BlcmF0b3JDaGFyKTtcbiAgICAgIHJldHVybiByZXQoXCJvcGVyYXRvclwiLCBudWxsLCBzdHJlYW0uY3VycmVudCgpKTtcbiAgICB9XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIHJldChcImNvbmRpdGlvbmFsXCIsIFwibWV0YVwiKTtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIkBcIikge1xuICAgIHN0cmVhbS5lYXQoLzovKTtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdfXS8pO1xuICAgIHJldHVybiByZXQoXCJtZXRhZGF0YVwiLCBcIm1ldGFcIik7XG4gIH0gZWxzZSBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNPcGVyYXRvckNoYXIpO1xuICAgIHJldHVybiByZXQoXCJvcGVyYXRvclwiLCBudWxsLCBzdHJlYW0uY3VycmVudCgpKTtcbiAgfSBlbHNlIHtcbiAgICB2YXIgd29yZDtcbiAgICBpZiAoL1tBLVpdLy50ZXN0KGNoKSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3Xzw+XS8pO1xuICAgICAgd29yZCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgICByZXR1cm4gcmV0KFwidHlwZVwiLCBcInR5cGVcIiwgd29yZCk7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd19dLyk7XG4gICAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCksXG4gICAgICAgIGtub3duID0ga2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUod29yZCkgJiYga2V5d29yZHNbd29yZF07XG4gICAgICByZXR1cm4ga25vd24gJiYgc3RhdGUua3dBbGxvd2VkID8gcmV0KGtub3duLnR5cGUsIGtub3duLnN0eWxlLCB3b3JkKSA6IHJldChcInZhcmlhYmxlXCIsIFwidmFyaWFibGVcIiwgd29yZCk7XG4gICAgfVxuICB9XG59XG5mdW5jdGlvbiBoYXhlVG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHRvVW5lc2NhcGVkKHN0cmVhbSwgcXVvdGUpKSBzdGF0ZS50b2tlbml6ZSA9IGhheGVUb2tlbkJhc2U7XG4gICAgcmV0dXJuIHJldChcInN0cmluZ1wiLCBcInN0cmluZ1wiKTtcbiAgfTtcbn1cbmZ1bmN0aW9uIGhheGVUb2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSBoYXhlVG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gIH1cbiAgcmV0dXJuIHJldChcImNvbW1lbnRcIiwgXCJjb21tZW50XCIpO1xufVxuXG4vLyBQYXJzZXJcblxudmFyIGF0b21pY1R5cGVzID0ge1xuICBcImF0b21cIjogdHJ1ZSxcbiAgXCJudW1iZXJcIjogdHJ1ZSxcbiAgXCJ2YXJpYWJsZVwiOiB0cnVlLFxuICBcInN0cmluZ1wiOiB0cnVlLFxuICBcInJlZ2V4cFwiOiB0cnVlXG59O1xuZnVuY3Rpb24gSGF4ZUxleGljYWwoaW5kZW50ZWQsIGNvbHVtbiwgdHlwZSwgYWxpZ24sIHByZXYsIGluZm8pIHtcbiAgdGhpcy5pbmRlbnRlZCA9IGluZGVudGVkO1xuICB0aGlzLmNvbHVtbiA9IGNvbHVtbjtcbiAgdGhpcy50eXBlID0gdHlwZTtcbiAgdGhpcy5wcmV2ID0gcHJldjtcbiAgdGhpcy5pbmZvID0gaW5mbztcbiAgaWYgKGFsaWduICE9IG51bGwpIHRoaXMuYWxpZ24gPSBhbGlnbjtcbn1cbmZ1bmN0aW9uIGluU2NvcGUoc3RhdGUsIHZhcm5hbWUpIHtcbiAgZm9yICh2YXIgdiA9IHN0YXRlLmxvY2FsVmFyczsgdjsgdiA9IHYubmV4dCkgaWYgKHYubmFtZSA9PSB2YXJuYW1lKSByZXR1cm4gdHJ1ZTtcbn1cbmZ1bmN0aW9uIHBhcnNlSGF4ZShzdGF0ZSwgc3R5bGUsIHR5cGUsIGNvbnRlbnQsIHN0cmVhbSkge1xuICB2YXIgY2MgPSBzdGF0ZS5jYztcbiAgLy8gQ29tbXVuaWNhdGUgb3VyIGNvbnRleHQgdG8gdGhlIGNvbWJpbmF0b3JzLlxuICAvLyAoTGVzcyB3YXN0ZWZ1bCB0aGFuIGNvbnNpbmcgdXAgYSBodW5kcmVkIGNsb3N1cmVzIG9uIGV2ZXJ5IGNhbGwuKVxuICBjeC5zdGF0ZSA9IHN0YXRlO1xuICBjeC5zdHJlYW0gPSBzdHJlYW07XG4gIGN4Lm1hcmtlZCA9IG51bGwsIGN4LmNjID0gY2M7XG4gIGlmICghc3RhdGUubGV4aWNhbC5oYXNPd25Qcm9wZXJ0eShcImFsaWduXCIpKSBzdGF0ZS5sZXhpY2FsLmFsaWduID0gdHJ1ZTtcbiAgd2hpbGUgKHRydWUpIHtcbiAgICB2YXIgY29tYmluYXRvciA9IGNjLmxlbmd0aCA/IGNjLnBvcCgpIDogc3RhdGVtZW50O1xuICAgIGlmIChjb21iaW5hdG9yKHR5cGUsIGNvbnRlbnQpKSB7XG4gICAgICB3aGlsZSAoY2MubGVuZ3RoICYmIGNjW2NjLmxlbmd0aCAtIDFdLmxleCkgY2MucG9wKCkoKTtcbiAgICAgIGlmIChjeC5tYXJrZWQpIHJldHVybiBjeC5tYXJrZWQ7XG4gICAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIgJiYgaW5TY29wZShzdGF0ZSwgY29udGVudCkpIHJldHVybiBcInZhcmlhYmxlTmFtZS5sb2NhbFwiO1xuICAgICAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiICYmIGltcG9ydGVkKHN0YXRlLCBjb250ZW50KSkgcmV0dXJuIFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICAgIHJldHVybiBzdHlsZTtcbiAgICB9XG4gIH1cbn1cbmZ1bmN0aW9uIGltcG9ydGVkKHN0YXRlLCB0eXBlbmFtZSkge1xuICBpZiAoL1thLXpdLy50ZXN0KHR5cGVuYW1lLmNoYXJBdCgwKSkpIHJldHVybiBmYWxzZTtcbiAgdmFyIGxlbiA9IHN0YXRlLmltcG9ydGVkdHlwZXMubGVuZ3RoO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IGxlbjsgaSsrKSBpZiAoc3RhdGUuaW1wb3J0ZWR0eXBlc1tpXSA9PSB0eXBlbmFtZSkgcmV0dXJuIHRydWU7XG59XG5mdW5jdGlvbiByZWdpc3RlcmltcG9ydChpbXBvcnRuYW1lKSB7XG4gIHZhciBzdGF0ZSA9IGN4LnN0YXRlO1xuICBmb3IgKHZhciB0ID0gc3RhdGUuaW1wb3J0ZWR0eXBlczsgdDsgdCA9IHQubmV4dCkgaWYgKHQubmFtZSA9PSBpbXBvcnRuYW1lKSByZXR1cm47XG4gIHN0YXRlLmltcG9ydGVkdHlwZXMgPSB7XG4gICAgbmFtZTogaW1wb3J0bmFtZSxcbiAgICBuZXh0OiBzdGF0ZS5pbXBvcnRlZHR5cGVzXG4gIH07XG59XG4vLyBDb21iaW5hdG9yIHV0aWxzXG5cbnZhciBjeCA9IHtcbiAgc3RhdGU6IG51bGwsXG4gIGNvbHVtbjogbnVsbCxcbiAgbWFya2VkOiBudWxsLFxuICBjYzogbnVsbFxufTtcbmZ1bmN0aW9uIHBhc3MoKSB7XG4gIGZvciAodmFyIGkgPSBhcmd1bWVudHMubGVuZ3RoIC0gMTsgaSA+PSAwOyBpLS0pIGN4LmNjLnB1c2goYXJndW1lbnRzW2ldKTtcbn1cbmZ1bmN0aW9uIGNvbnQoKSB7XG4gIHBhc3MuYXBwbHkobnVsbCwgYXJndW1lbnRzKTtcbiAgcmV0dXJuIHRydWU7XG59XG5mdW5jdGlvbiBpbkxpc3QobmFtZSwgbGlzdCkge1xuICBmb3IgKHZhciB2ID0gbGlzdDsgdjsgdiA9IHYubmV4dCkgaWYgKHYubmFtZSA9PSBuYW1lKSByZXR1cm4gdHJ1ZTtcbiAgcmV0dXJuIGZhbHNlO1xufVxuZnVuY3Rpb24gcmVnaXN0ZXIodmFybmFtZSkge1xuICB2YXIgc3RhdGUgPSBjeC5zdGF0ZTtcbiAgaWYgKHN0YXRlLmNvbnRleHQpIHtcbiAgICBjeC5tYXJrZWQgPSBcImRlZlwiO1xuICAgIGlmIChpbkxpc3QodmFybmFtZSwgc3RhdGUubG9jYWxWYXJzKSkgcmV0dXJuO1xuICAgIHN0YXRlLmxvY2FsVmFycyA9IHtcbiAgICAgIG5hbWU6IHZhcm5hbWUsXG4gICAgICBuZXh0OiBzdGF0ZS5sb2NhbFZhcnNcbiAgICB9O1xuICB9IGVsc2UgaWYgKHN0YXRlLmdsb2JhbFZhcnMpIHtcbiAgICBpZiAoaW5MaXN0KHZhcm5hbWUsIHN0YXRlLmdsb2JhbFZhcnMpKSByZXR1cm47XG4gICAgc3RhdGUuZ2xvYmFsVmFycyA9IHtcbiAgICAgIG5hbWU6IHZhcm5hbWUsXG4gICAgICBuZXh0OiBzdGF0ZS5nbG9iYWxWYXJzXG4gICAgfTtcbiAgfVxufVxuXG4vLyBDb21iaW5hdG9yc1xuXG52YXIgZGVmYXVsdFZhcnMgPSB7XG4gIG5hbWU6IFwidGhpc1wiLFxuICBuZXh0OiBudWxsXG59O1xuZnVuY3Rpb24gcHVzaGNvbnRleHQoKSB7XG4gIGlmICghY3guc3RhdGUuY29udGV4dCkgY3guc3RhdGUubG9jYWxWYXJzID0gZGVmYXVsdFZhcnM7XG4gIGN4LnN0YXRlLmNvbnRleHQgPSB7XG4gICAgcHJldjogY3guc3RhdGUuY29udGV4dCxcbiAgICB2YXJzOiBjeC5zdGF0ZS5sb2NhbFZhcnNcbiAgfTtcbn1cbmZ1bmN0aW9uIHBvcGNvbnRleHQoKSB7XG4gIGN4LnN0YXRlLmxvY2FsVmFycyA9IGN4LnN0YXRlLmNvbnRleHQudmFycztcbiAgY3guc3RhdGUuY29udGV4dCA9IGN4LnN0YXRlLmNvbnRleHQucHJldjtcbn1cbnBvcGNvbnRleHQubGV4ID0gdHJ1ZTtcbmZ1bmN0aW9uIHB1c2hsZXgodHlwZSwgaW5mbykge1xuICB2YXIgcmVzdWx0ID0gZnVuY3Rpb24gKCkge1xuICAgIHZhciBzdGF0ZSA9IGN4LnN0YXRlO1xuICAgIHN0YXRlLmxleGljYWwgPSBuZXcgSGF4ZUxleGljYWwoc3RhdGUuaW5kZW50ZWQsIGN4LnN0cmVhbS5jb2x1bW4oKSwgdHlwZSwgbnVsbCwgc3RhdGUubGV4aWNhbCwgaW5mbyk7XG4gIH07XG4gIHJlc3VsdC5sZXggPSB0cnVlO1xuICByZXR1cm4gcmVzdWx0O1xufVxuZnVuY3Rpb24gcG9wbGV4KCkge1xuICB2YXIgc3RhdGUgPSBjeC5zdGF0ZTtcbiAgaWYgKHN0YXRlLmxleGljYWwucHJldikge1xuICAgIGlmIChzdGF0ZS5sZXhpY2FsLnR5cGUgPT0gXCIpXCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUubGV4aWNhbC5pbmRlbnRlZDtcbiAgICBzdGF0ZS5sZXhpY2FsID0gc3RhdGUubGV4aWNhbC5wcmV2O1xuICB9XG59XG5wb3BsZXgubGV4ID0gdHJ1ZTtcbmZ1bmN0aW9uIGV4cGVjdCh3YW50ZWQpIHtcbiAgZnVuY3Rpb24gZih0eXBlKSB7XG4gICAgaWYgKHR5cGUgPT0gd2FudGVkKSByZXR1cm4gY29udCgpO2Vsc2UgaWYgKHdhbnRlZCA9PSBcIjtcIikgcmV0dXJuIHBhc3MoKTtlbHNlIHJldHVybiBjb250KGYpO1xuICB9XG4gIHJldHVybiBmO1xufVxuZnVuY3Rpb24gc3RhdGVtZW50KHR5cGUpIHtcbiAgaWYgKHR5cGUgPT0gXCJAXCIpIHJldHVybiBjb250KG1ldGFkZWYpO1xuICBpZiAodHlwZSA9PSBcInZhclwiKSByZXR1cm4gY29udChwdXNobGV4KFwidmFyZGVmXCIpLCB2YXJkZWYxLCBleHBlY3QoXCI7XCIpLCBwb3BsZXgpO1xuICBpZiAodHlwZSA9PSBcImtleXdvcmQgYVwiKSByZXR1cm4gY29udChwdXNobGV4KFwiZm9ybVwiKSwgZXhwcmVzc2lvbiwgc3RhdGVtZW50LCBwb3BsZXgpO1xuICBpZiAodHlwZSA9PSBcImtleXdvcmQgYlwiKSByZXR1cm4gY29udChwdXNobGV4KFwiZm9ybVwiKSwgc3RhdGVtZW50LCBwb3BsZXgpO1xuICBpZiAodHlwZSA9PSBcIntcIikgcmV0dXJuIGNvbnQocHVzaGxleChcIn1cIiksIHB1c2hjb250ZXh0LCBibG9jaywgcG9wbGV4LCBwb3Bjb250ZXh0KTtcbiAgaWYgKHR5cGUgPT0gXCI7XCIpIHJldHVybiBjb250KCk7XG4gIGlmICh0eXBlID09IFwiYXR0cmlidXRlXCIpIHJldHVybiBjb250KG1heWJlYXR0cmlidXRlKTtcbiAgaWYgKHR5cGUgPT0gXCJmdW5jdGlvblwiKSByZXR1cm4gY29udChmdW5jdGlvbmRlZik7XG4gIGlmICh0eXBlID09IFwiZm9yXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJmb3JtXCIpLCBleHBlY3QoXCIoXCIpLCBwdXNobGV4KFwiKVwiKSwgZm9yc3BlYzEsIGV4cGVjdChcIilcIiksIHBvcGxleCwgc3RhdGVtZW50LCBwb3BsZXgpO1xuICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJzdGF0XCIpLCBtYXliZWxhYmVsKTtcbiAgaWYgKHR5cGUgPT0gXCJzd2l0Y2hcIikgcmV0dXJuIGNvbnQocHVzaGxleChcImZvcm1cIiksIGV4cHJlc3Npb24sIHB1c2hsZXgoXCJ9XCIsIFwic3dpdGNoXCIpLCBleHBlY3QoXCJ7XCIpLCBibG9jaywgcG9wbGV4LCBwb3BsZXgpO1xuICBpZiAodHlwZSA9PSBcImNhc2VcIikgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbiwgZXhwZWN0KFwiOlwiKSk7XG4gIGlmICh0eXBlID09IFwiZGVmYXVsdFwiKSByZXR1cm4gY29udChleHBlY3QoXCI6XCIpKTtcbiAgaWYgKHR5cGUgPT0gXCJjYXRjaFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiZm9ybVwiKSwgcHVzaGNvbnRleHQsIGV4cGVjdChcIihcIiksIGZ1bmFyZywgZXhwZWN0KFwiKVwiKSwgc3RhdGVtZW50LCBwb3BsZXgsIHBvcGNvbnRleHQpO1xuICBpZiAodHlwZSA9PSBcImltcG9ydFwiKSByZXR1cm4gY29udChpbXBvcnRkZWYsIGV4cGVjdChcIjtcIikpO1xuICBpZiAodHlwZSA9PSBcInR5cGVkZWZcIikgcmV0dXJuIGNvbnQodHlwZWRlZik7XG4gIHJldHVybiBwYXNzKHB1c2hsZXgoXCJzdGF0XCIpLCBleHByZXNzaW9uLCBleHBlY3QoXCI7XCIpLCBwb3BsZXgpO1xufVxuZnVuY3Rpb24gZXhwcmVzc2lvbih0eXBlKSB7XG4gIGlmIChhdG9taWNUeXBlcy5oYXNPd25Qcm9wZXJ0eSh0eXBlKSkgcmV0dXJuIGNvbnQobWF5YmVvcGVyYXRvcik7XG4gIGlmICh0eXBlID09IFwidHlwZVwiKSByZXR1cm4gY29udChtYXliZW9wZXJhdG9yKTtcbiAgaWYgKHR5cGUgPT0gXCJmdW5jdGlvblwiKSByZXR1cm4gY29udChmdW5jdGlvbmRlZik7XG4gIGlmICh0eXBlID09IFwia2V5d29yZCBjXCIpIHJldHVybiBjb250KG1heWJlZXhwcmVzc2lvbik7XG4gIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiKVwiKSwgbWF5YmVleHByZXNzaW9uLCBleHBlY3QoXCIpXCIpLCBwb3BsZXgsIG1heWJlb3BlcmF0b3IpO1xuICBpZiAodHlwZSA9PSBcIm9wZXJhdG9yXCIpIHJldHVybiBjb250KGV4cHJlc3Npb24pO1xuICBpZiAodHlwZSA9PSBcIltcIikgcmV0dXJuIGNvbnQocHVzaGxleChcIl1cIiksIGNvbW1hc2VwKG1heWJlZXhwcmVzc2lvbiwgXCJdXCIpLCBwb3BsZXgsIG1heWJlb3BlcmF0b3IpO1xuICBpZiAodHlwZSA9PSBcIntcIikgcmV0dXJuIGNvbnQocHVzaGxleChcIn1cIiksIGNvbW1hc2VwKG9ianByb3AsIFwifVwiKSwgcG9wbGV4LCBtYXliZW9wZXJhdG9yKTtcbiAgcmV0dXJuIGNvbnQoKTtcbn1cbmZ1bmN0aW9uIG1heWJlZXhwcmVzc2lvbih0eXBlKSB7XG4gIGlmICh0eXBlLm1hdGNoKC9bO1xcfVxcKVxcXSxdLykpIHJldHVybiBwYXNzKCk7XG4gIHJldHVybiBwYXNzKGV4cHJlc3Npb24pO1xufVxuZnVuY3Rpb24gbWF5YmVvcGVyYXRvcih0eXBlLCB2YWx1ZSkge1xuICBpZiAodHlwZSA9PSBcIm9wZXJhdG9yXCIgJiYgL1xcK1xcK3wtLS8udGVzdCh2YWx1ZSkpIHJldHVybiBjb250KG1heWJlb3BlcmF0b3IpO1xuICBpZiAodHlwZSA9PSBcIm9wZXJhdG9yXCIgfHwgdHlwZSA9PSBcIjpcIikgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbik7XG4gIGlmICh0eXBlID09IFwiO1wiKSByZXR1cm47XG4gIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiKVwiKSwgY29tbWFzZXAoZXhwcmVzc2lvbiwgXCIpXCIpLCBwb3BsZXgsIG1heWJlb3BlcmF0b3IpO1xuICBpZiAodHlwZSA9PSBcIi5cIikgcmV0dXJuIGNvbnQocHJvcGVydHksIG1heWJlb3BlcmF0b3IpO1xuICBpZiAodHlwZSA9PSBcIltcIikgcmV0dXJuIGNvbnQocHVzaGxleChcIl1cIiksIGV4cHJlc3Npb24sIGV4cGVjdChcIl1cIiksIHBvcGxleCwgbWF5YmVvcGVyYXRvcik7XG59XG5mdW5jdGlvbiBtYXliZWF0dHJpYnV0ZSh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwiYXR0cmlidXRlXCIpIHJldHVybiBjb250KG1heWJlYXR0cmlidXRlKTtcbiAgaWYgKHR5cGUgPT0gXCJmdW5jdGlvblwiKSByZXR1cm4gY29udChmdW5jdGlvbmRlZik7XG4gIGlmICh0eXBlID09IFwidmFyXCIpIHJldHVybiBjb250KHZhcmRlZjEpO1xufVxuZnVuY3Rpb24gbWV0YWRlZih0eXBlKSB7XG4gIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gY29udChtZXRhZGVmKTtcbiAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiKSByZXR1cm4gY29udChtZXRhZGVmKTtcbiAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCIpXCIpLCBjb21tYXNlcChtZXRhYXJncywgXCIpXCIpLCBwb3BsZXgsIHN0YXRlbWVudCk7XG59XG5mdW5jdGlvbiBtZXRhYXJncyh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwidmFyaWFibGVcIikgcmV0dXJuIGNvbnQoKTtcbn1cbmZ1bmN0aW9uIGltcG9ydGRlZih0eXBlLCB2YWx1ZSkge1xuICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIgJiYgL1tBLVpdLy50ZXN0KHZhbHVlLmNoYXJBdCgwKSkpIHtcbiAgICByZWdpc3RlcmltcG9ydCh2YWx1ZSk7XG4gICAgcmV0dXJuIGNvbnQoKTtcbiAgfSBlbHNlIGlmICh0eXBlID09IFwidmFyaWFibGVcIiB8fCB0eXBlID09IFwicHJvcGVydHlcIiB8fCB0eXBlID09IFwiLlwiIHx8IHZhbHVlID09IFwiKlwiKSByZXR1cm4gY29udChpbXBvcnRkZWYpO1xufVxuZnVuY3Rpb24gdHlwZWRlZih0eXBlLCB2YWx1ZSkge1xuICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIgJiYgL1tBLVpdLy50ZXN0KHZhbHVlLmNoYXJBdCgwKSkpIHtcbiAgICByZWdpc3RlcmltcG9ydCh2YWx1ZSk7XG4gICAgcmV0dXJuIGNvbnQoKTtcbiAgfSBlbHNlIGlmICh0eXBlID09IFwidHlwZVwiICYmIC9bQS1aXS8udGVzdCh2YWx1ZS5jaGFyQXQoMCkpKSB7XG4gICAgcmV0dXJuIGNvbnQoKTtcbiAgfVxufVxuZnVuY3Rpb24gbWF5YmVsYWJlbCh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gY29udChwb3BsZXgsIHN0YXRlbWVudCk7XG4gIHJldHVybiBwYXNzKG1heWJlb3BlcmF0b3IsIGV4cGVjdChcIjtcIiksIHBvcGxleCk7XG59XG5mdW5jdGlvbiBwcm9wZXJ0eSh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwidmFyaWFibGVcIikge1xuICAgIGN4Lm1hcmtlZCA9IFwicHJvcGVydHlcIjtcbiAgICByZXR1cm4gY29udCgpO1xuICB9XG59XG5mdW5jdGlvbiBvYmpwcm9wKHR5cGUpIHtcbiAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiKSBjeC5tYXJrZWQgPSBcInByb3BlcnR5XCI7XG4gIGlmIChhdG9taWNUeXBlcy5oYXNPd25Qcm9wZXJ0eSh0eXBlKSkgcmV0dXJuIGNvbnQoZXhwZWN0KFwiOlwiKSwgZXhwcmVzc2lvbik7XG59XG5mdW5jdGlvbiBjb21tYXNlcCh3aGF0LCBlbmQpIHtcbiAgZnVuY3Rpb24gcHJvY2VlZCh0eXBlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCIsXCIpIHJldHVybiBjb250KHdoYXQsIHByb2NlZWQpO1xuICAgIGlmICh0eXBlID09IGVuZCkgcmV0dXJuIGNvbnQoKTtcbiAgICByZXR1cm4gY29udChleHBlY3QoZW5kKSk7XG4gIH1cbiAgcmV0dXJuIGZ1bmN0aW9uICh0eXBlKSB7XG4gICAgaWYgKHR5cGUgPT0gZW5kKSByZXR1cm4gY29udCgpO2Vsc2UgcmV0dXJuIHBhc3Mod2hhdCwgcHJvY2VlZCk7XG4gIH07XG59XG5mdW5jdGlvbiBibG9jayh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwifVwiKSByZXR1cm4gY29udCgpO1xuICByZXR1cm4gcGFzcyhzdGF0ZW1lbnQsIGJsb2NrKTtcbn1cbmZ1bmN0aW9uIHZhcmRlZjEodHlwZSwgdmFsdWUpIHtcbiAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiKSB7XG4gICAgcmVnaXN0ZXIodmFsdWUpO1xuICAgIHJldHVybiBjb250KHR5cGV1c2UsIHZhcmRlZjIpO1xuICB9XG4gIHJldHVybiBjb250KCk7XG59XG5mdW5jdGlvbiB2YXJkZWYyKHR5cGUsIHZhbHVlKSB7XG4gIGlmICh2YWx1ZSA9PSBcIj1cIikgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbiwgdmFyZGVmMik7XG4gIGlmICh0eXBlID09IFwiLFwiKSByZXR1cm4gY29udCh2YXJkZWYxKTtcbn1cbmZ1bmN0aW9uIGZvcnNwZWMxKHR5cGUsIHZhbHVlKSB7XG4gIGlmICh0eXBlID09IFwidmFyaWFibGVcIikge1xuICAgIHJlZ2lzdGVyKHZhbHVlKTtcbiAgICByZXR1cm4gY29udChmb3JpbiwgZXhwcmVzc2lvbik7XG4gIH0gZWxzZSB7XG4gICAgcmV0dXJuIHBhc3MoKTtcbiAgfVxufVxuZnVuY3Rpb24gZm9yaW4oX3R5cGUsIHZhbHVlKSB7XG4gIGlmICh2YWx1ZSA9PSBcImluXCIpIHJldHVybiBjb250KCk7XG59XG5mdW5jdGlvbiBmdW5jdGlvbmRlZih0eXBlLCB2YWx1ZSkge1xuICAvL2Z1bmN0aW9uIG5hbWVzIHN0YXJ0aW5nIHdpdGggdXBwZXItY2FzZSBsZXR0ZXJzIGFyZSByZWNvZ25pc2VkIGFzIHR5cGVzLCBzbyBjbHVkZ2luZyB0aGVtIHRvZ2V0aGVyIGhlcmUuXG4gIGlmICh0eXBlID09IFwidmFyaWFibGVcIiB8fCB0eXBlID09IFwidHlwZVwiKSB7XG4gICAgcmVnaXN0ZXIodmFsdWUpO1xuICAgIHJldHVybiBjb250KGZ1bmN0aW9uZGVmKTtcbiAgfVxuICBpZiAodmFsdWUgPT0gXCJuZXdcIikgcmV0dXJuIGNvbnQoZnVuY3Rpb25kZWYpO1xuICBpZiAodHlwZSA9PSBcIihcIikgcmV0dXJuIGNvbnQocHVzaGxleChcIilcIiksIHB1c2hjb250ZXh0LCBjb21tYXNlcChmdW5hcmcsIFwiKVwiKSwgcG9wbGV4LCB0eXBldXNlLCBzdGF0ZW1lbnQsIHBvcGNvbnRleHQpO1xufVxuZnVuY3Rpb24gdHlwZXVzZSh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gY29udCh0eXBlc3RyaW5nKTtcbn1cbmZ1bmN0aW9uIHR5cGVzdHJpbmcodHlwZSkge1xuICBpZiAodHlwZSA9PSBcInR5cGVcIikgcmV0dXJuIGNvbnQoKTtcbiAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiKSByZXR1cm4gY29udCgpO1xuICBpZiAodHlwZSA9PSBcIntcIikgcmV0dXJuIGNvbnQocHVzaGxleChcIn1cIiksIGNvbW1hc2VwKHR5cGVwcm9wLCBcIn1cIiksIHBvcGxleCk7XG59XG5mdW5jdGlvbiB0eXBlcHJvcCh0eXBlKSB7XG4gIGlmICh0eXBlID09IFwidmFyaWFibGVcIikgcmV0dXJuIGNvbnQodHlwZXVzZSk7XG59XG5mdW5jdGlvbiBmdW5hcmcodHlwZSwgdmFsdWUpIHtcbiAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiKSB7XG4gICAgcmVnaXN0ZXIodmFsdWUpO1xuICAgIHJldHVybiBjb250KHR5cGV1c2UpO1xuICB9XG59XG5cbi8vIEludGVyZmFjZVxuZXhwb3J0IGNvbnN0IGhheGUgPSB7XG4gIG5hbWU6IFwiaGF4ZVwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgIHZhciBkZWZhdWx0dHlwZXMgPSBbXCJJbnRcIiwgXCJGbG9hdFwiLCBcIlN0cmluZ1wiLCBcIlZvaWRcIiwgXCJTdGRcIiwgXCJCb29sXCIsIFwiRHluYW1pY1wiLCBcIkFycmF5XCJdO1xuICAgIHZhciBzdGF0ZSA9IHtcbiAgICAgIHRva2VuaXplOiBoYXhlVG9rZW5CYXNlLFxuICAgICAgcmVBbGxvd2VkOiB0cnVlLFxuICAgICAga3dBbGxvd2VkOiB0cnVlLFxuICAgICAgY2M6IFtdLFxuICAgICAgbGV4aWNhbDogbmV3IEhheGVMZXhpY2FsKC1pbmRlbnRVbml0LCAwLCBcImJsb2NrXCIsIGZhbHNlKSxcbiAgICAgIGltcG9ydGVkdHlwZXM6IGRlZmF1bHR0eXBlcyxcbiAgICAgIGNvbnRleHQ6IG51bGwsXG4gICAgICBpbmRlbnRlZDogMFxuICAgIH07XG4gICAgcmV0dXJuIHN0YXRlO1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBpZiAoIXN0YXRlLmxleGljYWwuaGFzT3duUHJvcGVydHkoXCJhbGlnblwiKSkgc3RhdGUubGV4aWNhbC5hbGlnbiA9IGZhbHNlO1xuICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAodHlwZSA9PSBcImNvbW1lbnRcIikgcmV0dXJuIHN0eWxlO1xuICAgIHN0YXRlLnJlQWxsb3dlZCA9ICEhKHR5cGUgPT0gXCJvcGVyYXRvclwiIHx8IHR5cGUgPT0gXCJrZXl3b3JkIGNcIiB8fCB0eXBlLm1hdGNoKC9eW1xcW3t9XFwoLDs6XSQvKSk7XG4gICAgc3RhdGUua3dBbGxvd2VkID0gdHlwZSAhPSAnLic7XG4gICAgcmV0dXJuIHBhcnNlSGF4ZShzdGF0ZSwgc3R5bGUsIHR5cGUsIGNvbnRlbnQsIHN0cmVhbSk7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgaWYgKHN0YXRlLnRva2VuaXplICE9IGhheGVUb2tlbkJhc2UpIHJldHVybiAwO1xuICAgIHZhciBmaXJzdENoYXIgPSB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKSxcbiAgICAgIGxleGljYWwgPSBzdGF0ZS5sZXhpY2FsO1xuICAgIGlmIChsZXhpY2FsLnR5cGUgPT0gXCJzdGF0XCIgJiYgZmlyc3RDaGFyID09IFwifVwiKSBsZXhpY2FsID0gbGV4aWNhbC5wcmV2O1xuICAgIHZhciB0eXBlID0gbGV4aWNhbC50eXBlLFxuICAgICAgY2xvc2luZyA9IGZpcnN0Q2hhciA9PSB0eXBlO1xuICAgIGlmICh0eXBlID09IFwidmFyZGVmXCIpIHJldHVybiBsZXhpY2FsLmluZGVudGVkICsgNDtlbHNlIGlmICh0eXBlID09IFwiZm9ybVwiICYmIGZpcnN0Q2hhciA9PSBcIntcIikgcmV0dXJuIGxleGljYWwuaW5kZW50ZWQ7ZWxzZSBpZiAodHlwZSA9PSBcInN0YXRcIiB8fCB0eXBlID09IFwiZm9ybVwiKSByZXR1cm4gbGV4aWNhbC5pbmRlbnRlZCArIGN4LnVuaXQ7ZWxzZSBpZiAobGV4aWNhbC5pbmZvID09IFwic3dpdGNoXCIgJiYgIWNsb3NpbmcpIHJldHVybiBsZXhpY2FsLmluZGVudGVkICsgKC9eKD86Y2FzZXxkZWZhdWx0KVxcYi8udGVzdCh0ZXh0QWZ0ZXIpID8gY3gudW5pdCA6IDIgKiBjeC51bml0KTtlbHNlIGlmIChsZXhpY2FsLmFsaWduKSByZXR1cm4gbGV4aWNhbC5jb2x1bW4gKyAoY2xvc2luZyA/IDAgOiAxKTtlbHNlIHJldHVybiBsZXhpY2FsLmluZGVudGVkICsgKGNsb3NpbmcgPyAwIDogY3gudW5pdCk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGluZGVudE9uSW5wdXQ6IC9eXFxzKlt7fV0kLyxcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIi8vXCIsXG4gICAgICBibG9jazoge1xuICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgIH1cbiAgICB9XG4gIH1cbn07XG5leHBvcnQgY29uc3QgaHhtbCA9IHtcbiAgbmFtZTogXCJoeG1sXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgZGVmaW5lOiBmYWxzZSxcbiAgICAgIGluU3RyaW5nOiBmYWxzZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjaCA9IHN0cmVhbS5wZWVrKCk7XG4gICAgdmFyIHNvbCA9IHN0cmVhbS5zb2woKTtcblxuICAgIC8vLyogY29tbWVudHMgKi9cbiAgICBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKHNvbCAmJiBjaCA9PSBcIi1cIikge1xuICAgICAgdmFyIHN0eWxlID0gXCJ2YXJpYWJsZS0yXCI7XG4gICAgICBzdHJlYW0uZWF0KC8tLyk7XG4gICAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PSBcIi1cIikge1xuICAgICAgICBzdHJlYW0uZWF0KC8tLyk7XG4gICAgICAgIHN0eWxlID0gXCJrZXl3b3JkIGFcIjtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0ucGVlaygpID09IFwiRFwiKSB7XG4gICAgICAgIHN0cmVhbS5lYXQoL1tEXS8pO1xuICAgICAgICBzdHlsZSA9IFwia2V5d29yZCBjXCI7XG4gICAgICAgIHN0YXRlLmRlZmluZSA9IHRydWU7XG4gICAgICB9XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tBLVpdL2kpO1xuICAgICAgcmV0dXJuIHN0eWxlO1xuICAgIH1cbiAgICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpO1xuICAgIGlmIChzdGF0ZS5pblN0cmluZyA9PSBmYWxzZSAmJiBjaCA9PSBcIidcIikge1xuICAgICAgc3RhdGUuaW5TdHJpbmcgPSB0cnVlO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICB9XG4gICAgaWYgKHN0YXRlLmluU3RyaW5nID09IHRydWUpIHtcbiAgICAgIGlmIChzdHJlYW0uc2tpcFRvKFwiJ1wiKSkge30gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0ucGVlaygpID09IFwiJ1wiKSB7XG4gICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgIHN0YXRlLmluU3RyaW5nID0gZmFsc2U7XG4gICAgICB9XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIjXCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==