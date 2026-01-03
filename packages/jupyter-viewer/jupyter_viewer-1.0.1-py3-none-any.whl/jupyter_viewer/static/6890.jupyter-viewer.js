"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3027,6890],{

/***/ 6890
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   pug: () => (/* binding */ pug)
/* harmony export */ });
/* harmony import */ var _javascript_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(53027);

var ATTRS_NEST = {
  '{': '}',
  '(': ')',
  '[': ']'
};
function defaultCopyState(state) {
  if (typeof state != "object") return state;
  let newState = {};
  for (let prop in state) {
    let val = state[prop];
    newState[prop] = val instanceof Array ? val.slice() : val;
  }
  return newState;
}
class State {
  constructor(indentUnit) {
    this.indentUnit = indentUnit;
    this.javaScriptLine = false;
    this.javaScriptLineExcludesColon = false;
    this.javaScriptArguments = false;
    this.javaScriptArgumentsDepth = 0;
    this.isInterpolating = false;
    this.interpolationNesting = 0;
    this.jsState = _javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.startState(indentUnit);
    this.restOfLine = '';
    this.isIncludeFiltered = false;
    this.isEach = false;
    this.lastTag = '';

    // Attributes Mode
    this.isAttrs = false;
    this.attrsNest = [];
    this.inAttributeName = true;
    this.attributeIsType = false;
    this.attrValue = '';

    // Indented Mode
    this.indentOf = Infinity;
    this.indentToken = '';
  }
  copy() {
    var res = new State(this.indentUnit);
    res.javaScriptLine = this.javaScriptLine;
    res.javaScriptLineExcludesColon = this.javaScriptLineExcludesColon;
    res.javaScriptArguments = this.javaScriptArguments;
    res.javaScriptArgumentsDepth = this.javaScriptArgumentsDepth;
    res.isInterpolating = this.isInterpolating;
    res.interpolationNesting = this.interpolationNesting;
    res.jsState = (_javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.copyState || defaultCopyState)(this.jsState);
    res.restOfLine = this.restOfLine;
    res.isIncludeFiltered = this.isIncludeFiltered;
    res.isEach = this.isEach;
    res.lastTag = this.lastTag;
    res.isAttrs = this.isAttrs;
    res.attrsNest = this.attrsNest.slice();
    res.inAttributeName = this.inAttributeName;
    res.attributeIsType = this.attributeIsType;
    res.attrValue = this.attrValue;
    res.indentOf = this.indentOf;
    res.indentToken = this.indentToken;
    return res;
  }
}
function javaScript(stream, state) {
  if (stream.sol()) {
    // if javaScriptLine was set at end of line, ignore it
    state.javaScriptLine = false;
    state.javaScriptLineExcludesColon = false;
  }
  if (state.javaScriptLine) {
    if (state.javaScriptLineExcludesColon && stream.peek() === ':') {
      state.javaScriptLine = false;
      state.javaScriptLineExcludesColon = false;
      return;
    }
    var tok = _javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.token(stream, state.jsState);
    if (stream.eol()) state.javaScriptLine = false;
    return tok || true;
  }
}
function javaScriptArguments(stream, state) {
  if (state.javaScriptArguments) {
    if (state.javaScriptArgumentsDepth === 0 && stream.peek() !== '(') {
      state.javaScriptArguments = false;
      return;
    }
    if (stream.peek() === '(') {
      state.javaScriptArgumentsDepth++;
    } else if (stream.peek() === ')') {
      state.javaScriptArgumentsDepth--;
    }
    if (state.javaScriptArgumentsDepth === 0) {
      state.javaScriptArguments = false;
      return;
    }
    var tok = _javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.token(stream, state.jsState);
    return tok || true;
  }
}
function yieldStatement(stream) {
  if (stream.match(/^yield\b/)) {
    return 'keyword';
  }
}
function doctype(stream) {
  if (stream.match(/^(?:doctype) *([^\n]+)?/)) return 'meta';
}
function interpolation(stream, state) {
  if (stream.match('#{')) {
    state.isInterpolating = true;
    state.interpolationNesting = 0;
    return 'punctuation';
  }
}
function interpolationContinued(stream, state) {
  if (state.isInterpolating) {
    if (stream.peek() === '}') {
      state.interpolationNesting--;
      if (state.interpolationNesting < 0) {
        stream.next();
        state.isInterpolating = false;
        return 'punctuation';
      }
    } else if (stream.peek() === '{') {
      state.interpolationNesting++;
    }
    return _javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.token(stream, state.jsState) || true;
  }
}
function caseStatement(stream, state) {
  if (stream.match(/^case\b/)) {
    state.javaScriptLine = true;
    return 'keyword';
  }
}
function when(stream, state) {
  if (stream.match(/^when\b/)) {
    state.javaScriptLine = true;
    state.javaScriptLineExcludesColon = true;
    return 'keyword';
  }
}
function defaultStatement(stream) {
  if (stream.match(/^default\b/)) {
    return 'keyword';
  }
}
function extendsStatement(stream, state) {
  if (stream.match(/^extends?\b/)) {
    state.restOfLine = 'string';
    return 'keyword';
  }
}
function append(stream, state) {
  if (stream.match(/^append\b/)) {
    state.restOfLine = 'variable';
    return 'keyword';
  }
}
function prepend(stream, state) {
  if (stream.match(/^prepend\b/)) {
    state.restOfLine = 'variable';
    return 'keyword';
  }
}
function block(stream, state) {
  if (stream.match(/^block\b *(?:(prepend|append)\b)?/)) {
    state.restOfLine = 'variable';
    return 'keyword';
  }
}
function include(stream, state) {
  if (stream.match(/^include\b/)) {
    state.restOfLine = 'string';
    return 'keyword';
  }
}
function includeFiltered(stream, state) {
  if (stream.match(/^include:([a-zA-Z0-9\-]+)/, false) && stream.match('include')) {
    state.isIncludeFiltered = true;
    return 'keyword';
  }
}
function includeFilteredContinued(stream, state) {
  if (state.isIncludeFiltered) {
    var tok = filter(stream, state);
    state.isIncludeFiltered = false;
    state.restOfLine = 'string';
    return tok;
  }
}
function mixin(stream, state) {
  if (stream.match(/^mixin\b/)) {
    state.javaScriptLine = true;
    return 'keyword';
  }
}
function call(stream, state) {
  if (stream.match(/^\+([-\w]+)/)) {
    if (!stream.match(/^\( *[-\w]+ *=/, false)) {
      state.javaScriptArguments = true;
      state.javaScriptArgumentsDepth = 0;
    }
    return 'variable';
  }
  if (stream.match('+#{', false)) {
    stream.next();
    state.mixinCallAfter = true;
    return interpolation(stream, state);
  }
}
function callArguments(stream, state) {
  if (state.mixinCallAfter) {
    state.mixinCallAfter = false;
    if (!stream.match(/^\( *[-\w]+ *=/, false)) {
      state.javaScriptArguments = true;
      state.javaScriptArgumentsDepth = 0;
    }
    return true;
  }
}
function conditional(stream, state) {
  if (stream.match(/^(if|unless|else if|else)\b/)) {
    state.javaScriptLine = true;
    return 'keyword';
  }
}
function each(stream, state) {
  if (stream.match(/^(- *)?(each|for)\b/)) {
    state.isEach = true;
    return 'keyword';
  }
}
function eachContinued(stream, state) {
  if (state.isEach) {
    if (stream.match(/^ in\b/)) {
      state.javaScriptLine = true;
      state.isEach = false;
      return 'keyword';
    } else if (stream.sol() || stream.eol()) {
      state.isEach = false;
    } else if (stream.next()) {
      while (!stream.match(/^ in\b/, false) && stream.next()) {}
      return 'variable';
    }
  }
}
function whileStatement(stream, state) {
  if (stream.match(/^while\b/)) {
    state.javaScriptLine = true;
    return 'keyword';
  }
}
function tag(stream, state) {
  var captures;
  if (captures = stream.match(/^(\w(?:[-:\w]*\w)?)\/?/)) {
    state.lastTag = captures[1].toLowerCase();
    return 'tag';
  }
}
function filter(stream, state) {
  if (stream.match(/^:([\w\-]+)/)) {
    setStringMode(stream, state);
    return 'atom';
  }
}
function code(stream, state) {
  if (stream.match(/^(!?=|-)/)) {
    state.javaScriptLine = true;
    return 'punctuation';
  }
}
function id(stream) {
  if (stream.match(/^#([\w-]+)/)) {
    return 'builtin';
  }
}
function className(stream) {
  if (stream.match(/^\.([\w-]+)/)) {
    return 'className';
  }
}
function attrs(stream, state) {
  if (stream.peek() == '(') {
    stream.next();
    state.isAttrs = true;
    state.attrsNest = [];
    state.inAttributeName = true;
    state.attrValue = '';
    state.attributeIsType = false;
    return 'punctuation';
  }
}
function attrsContinued(stream, state) {
  if (state.isAttrs) {
    if (ATTRS_NEST[stream.peek()]) {
      state.attrsNest.push(ATTRS_NEST[stream.peek()]);
    }
    if (state.attrsNest[state.attrsNest.length - 1] === stream.peek()) {
      state.attrsNest.pop();
    } else if (stream.eat(')')) {
      state.isAttrs = false;
      return 'punctuation';
    }
    if (state.inAttributeName && stream.match(/^[^=,\)!]+/)) {
      if (stream.peek() === '=' || stream.peek() === '!') {
        state.inAttributeName = false;
        state.jsState = _javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.startState(2);
        if (state.lastTag === 'script' && stream.current().trim().toLowerCase() === 'type') {
          state.attributeIsType = true;
        } else {
          state.attributeIsType = false;
        }
      }
      return 'attribute';
    }
    var tok = _javascript_js__WEBPACK_IMPORTED_MODULE_0__/* .javascript */ .Q2.token(stream, state.jsState);
    if (state.attrsNest.length === 0 && (tok === 'string' || tok === 'variable' || tok === 'keyword')) {
      try {
        Function('', 'var x ' + state.attrValue.replace(/,\s*$/, '').replace(/^!/, ''));
        state.inAttributeName = true;
        state.attrValue = '';
        stream.backUp(stream.current().length);
        return attrsContinued(stream, state);
      } catch (ex) {
        //not the end of an attribute
      }
    }
    state.attrValue += stream.current();
    return tok || true;
  }
}
function attributesBlock(stream, state) {
  if (stream.match(/^&attributes\b/)) {
    state.javaScriptArguments = true;
    state.javaScriptArgumentsDepth = 0;
    return 'keyword';
  }
}
function indent(stream) {
  if (stream.sol() && stream.eatSpace()) {
    return 'indent';
  }
}
function comment(stream, state) {
  if (stream.match(/^ *\/\/(-)?([^\n]*)/)) {
    state.indentOf = stream.indentation();
    state.indentToken = 'comment';
    return 'comment';
  }
}
function colon(stream) {
  if (stream.match(/^: */)) {
    return 'colon';
  }
}
function text(stream, state) {
  if (stream.match(/^(?:\| ?| )([^\n]+)/)) {
    return 'string';
  }
  if (stream.match(/^(<[^\n]*)/, false)) {
    // html string
    setStringMode(stream, state);
    stream.skipToEnd();
    return state.indentToken;
  }
}
function dot(stream, state) {
  if (stream.eat('.')) {
    setStringMode(stream, state);
    return 'dot';
  }
}
function fail(stream) {
  stream.next();
  return null;
}
function setStringMode(stream, state) {
  state.indentOf = stream.indentation();
  state.indentToken = 'string';
}
function restOfLine(stream, state) {
  if (stream.sol()) {
    // if restOfLine was set at end of line, ignore it
    state.restOfLine = '';
  }
  if (state.restOfLine) {
    stream.skipToEnd();
    var tok = state.restOfLine;
    state.restOfLine = '';
    return tok;
  }
}
function startState(indentUnit) {
  return new State(indentUnit);
}
function copyState(state) {
  return state.copy();
}
function nextToken(stream, state) {
  var tok = restOfLine(stream, state) || interpolationContinued(stream, state) || includeFilteredContinued(stream, state) || eachContinued(stream, state) || attrsContinued(stream, state) || javaScript(stream, state) || javaScriptArguments(stream, state) || callArguments(stream, state) || yieldStatement(stream) || doctype(stream) || interpolation(stream, state) || caseStatement(stream, state) || when(stream, state) || defaultStatement(stream) || extendsStatement(stream, state) || append(stream, state) || prepend(stream, state) || block(stream, state) || include(stream, state) || includeFiltered(stream, state) || mixin(stream, state) || call(stream, state) || conditional(stream, state) || each(stream, state) || whileStatement(stream, state) || tag(stream, state) || filter(stream, state) || code(stream, state) || id(stream) || className(stream) || attrs(stream, state) || attributesBlock(stream, state) || indent(stream) || text(stream, state) || comment(stream, state) || colon(stream) || dot(stream, state) || fail(stream);
  return tok === true ? null : tok;
}
const pug = {
  startState: startState,
  copyState: copyState,
  token: nextToken
};

/***/ },

/***/ 53027
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Q2: () => (/* binding */ javascript),
/* harmony export */   jsonld: () => (/* binding */ jsonld)
/* harmony export */ });
/* unused harmony exports json, typescript */
function mkJavaScript(parserConfig) {
  var statementIndent = parserConfig.statementIndent;
  var jsonldMode = parserConfig.jsonld;
  var jsonMode = parserConfig.json || jsonldMode;
  var isTS = parserConfig.typescript;
  var wordRE = parserConfig.wordCharacters || /[\w$\xa1-\uffff]/;

  // Tokenizer

  var keywords = function () {
    function kw(type) {
      return {
        type: type,
        style: "keyword"
      };
    }
    var A = kw("keyword a"),
      B = kw("keyword b"),
      C = kw("keyword c"),
      D = kw("keyword d");
    var operator = kw("operator"),
      atom = {
        type: "atom",
        style: "atom"
      };
    return {
      "if": kw("if"),
      "while": A,
      "with": A,
      "else": B,
      "do": B,
      "try": B,
      "finally": B,
      "return": D,
      "break": D,
      "continue": D,
      "new": kw("new"),
      "delete": C,
      "void": C,
      "throw": C,
      "debugger": kw("debugger"),
      "var": kw("var"),
      "const": kw("var"),
      "let": kw("var"),
      "function": kw("function"),
      "catch": kw("catch"),
      "for": kw("for"),
      "switch": kw("switch"),
      "case": kw("case"),
      "default": kw("default"),
      "in": operator,
      "typeof": operator,
      "instanceof": operator,
      "true": atom,
      "false": atom,
      "null": atom,
      "undefined": atom,
      "NaN": atom,
      "Infinity": atom,
      "this": kw("this"),
      "class": kw("class"),
      "super": kw("atom"),
      "yield": C,
      "export": kw("export"),
      "import": kw("import"),
      "extends": C,
      "await": C
    };
  }();
  var isOperatorChar = /[+\-*&%=<>!?|~^@]/;
  var isJsonldKeyword = /^@(context|id|value|language|type|container|list|set|reverse|index|base|vocab|graph)"/;
  function readRegexp(stream) {
    var escaped = false,
      next,
      inSet = false;
    while ((next = stream.next()) != null) {
      if (!escaped) {
        if (next == "/" && !inSet) return;
        if (next == "[") inSet = true;else if (inSet && next == "]") inSet = false;
      }
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
  function tokenBase(stream, state) {
    var ch = stream.next();
    if (ch == '"' || ch == "'") {
      state.tokenize = tokenString(ch);
      return state.tokenize(stream, state);
    } else if (ch == "." && stream.match(/^\d[\d_]*(?:[eE][+\-]?[\d_]+)?/)) {
      return ret("number", "number");
    } else if (ch == "." && stream.match("..")) {
      return ret("spread", "meta");
    } else if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
      return ret(ch);
    } else if (ch == "=" && stream.eat(">")) {
      return ret("=>", "operator");
    } else if (ch == "0" && stream.match(/^(?:x[\dA-Fa-f_]+|o[0-7_]+|b[01_]+)n?/)) {
      return ret("number", "number");
    } else if (/\d/.test(ch)) {
      stream.match(/^[\d_]*(?:n|(?:\.[\d_]*)?(?:[eE][+\-]?[\d_]+)?)?/);
      return ret("number", "number");
    } else if (ch == "/") {
      if (stream.eat("*")) {
        state.tokenize = tokenComment;
        return tokenComment(stream, state);
      } else if (stream.eat("/")) {
        stream.skipToEnd();
        return ret("comment", "comment");
      } else if (expressionAllowed(stream, state, 1)) {
        readRegexp(stream);
        stream.match(/^\b(([gimyus])(?![gimyus]*\2))+\b/);
        return ret("regexp", "string.special");
      } else {
        stream.eat("=");
        return ret("operator", "operator", stream.current());
      }
    } else if (ch == "`") {
      state.tokenize = tokenQuasi;
      return tokenQuasi(stream, state);
    } else if (ch == "#" && stream.peek() == "!") {
      stream.skipToEnd();
      return ret("meta", "meta");
    } else if (ch == "#" && stream.eatWhile(wordRE)) {
      return ret("variable", "property");
    } else if (ch == "<" && stream.match("!--") || ch == "-" && stream.match("->") && !/\S/.test(stream.string.slice(0, stream.start))) {
      stream.skipToEnd();
      return ret("comment", "comment");
    } else if (isOperatorChar.test(ch)) {
      if (ch != ">" || !state.lexical || state.lexical.type != ">") {
        if (stream.eat("=")) {
          if (ch == "!" || ch == "=") stream.eat("=");
        } else if (/[<>*+\-|&?]/.test(ch)) {
          stream.eat(ch);
          if (ch == ">") stream.eat(ch);
        }
      }
      if (ch == "?" && stream.eat(".")) return ret(".");
      return ret("operator", "operator", stream.current());
    } else if (wordRE.test(ch)) {
      stream.eatWhile(wordRE);
      var word = stream.current();
      if (state.lastType != ".") {
        if (keywords.propertyIsEnumerable(word)) {
          var kw = keywords[word];
          return ret(kw.type, kw.style, word);
        }
        if (word == "async" && stream.match(/^(\s|\/\*([^*]|\*(?!\/))*?\*\/)*[\[\(\w]/, false)) return ret("async", "keyword", word);
      }
      return ret("variable", "variable", word);
    }
  }
  function tokenString(quote) {
    return function (stream, state) {
      var escaped = false,
        next;
      if (jsonldMode && stream.peek() == "@" && stream.match(isJsonldKeyword)) {
        state.tokenize = tokenBase;
        return ret("jsonld-keyword", "meta");
      }
      while ((next = stream.next()) != null) {
        if (next == quote && !escaped) break;
        escaped = !escaped && next == "\\";
      }
      if (!escaped) state.tokenize = tokenBase;
      return ret("string", "string");
    };
  }
  function tokenComment(stream, state) {
    var maybeEnd = false,
      ch;
    while (ch = stream.next()) {
      if (ch == "/" && maybeEnd) {
        state.tokenize = tokenBase;
        break;
      }
      maybeEnd = ch == "*";
    }
    return ret("comment", "comment");
  }
  function tokenQuasi(stream, state) {
    var escaped = false,
      next;
    while ((next = stream.next()) != null) {
      if (!escaped && (next == "`" || next == "$" && stream.eat("{"))) {
        state.tokenize = tokenBase;
        break;
      }
      escaped = !escaped && next == "\\";
    }
    return ret("quasi", "string.special", stream.current());
  }
  var brackets = "([{}])";
  // This is a crude lookahead trick to try and notice that we're
  // parsing the argument patterns for a fat-arrow function before we
  // actually hit the arrow token. It only works if the arrow is on
  // the same line as the arguments and there's no strange noise
  // (comments) in between. Fallback is to only notice when we hit the
  // arrow, and not declare the arguments as locals for the arrow
  // body.
  function findFatArrow(stream, state) {
    if (state.fatArrowAt) state.fatArrowAt = null;
    var arrow = stream.string.indexOf("=>", stream.start);
    if (arrow < 0) return;
    if (isTS) {
      // Try to skip TypeScript return type declarations after the arguments
      var m = /:\s*(?:\w+(?:<[^>]*>|\[\])?|\{[^}]*\})\s*$/.exec(stream.string.slice(stream.start, arrow));
      if (m) arrow = m.index;
    }
    var depth = 0,
      sawSomething = false;
    for (var pos = arrow - 1; pos >= 0; --pos) {
      var ch = stream.string.charAt(pos);
      var bracket = brackets.indexOf(ch);
      if (bracket >= 0 && bracket < 3) {
        if (!depth) {
          ++pos;
          break;
        }
        if (--depth == 0) {
          if (ch == "(") sawSomething = true;
          break;
        }
      } else if (bracket >= 3 && bracket < 6) {
        ++depth;
      } else if (wordRE.test(ch)) {
        sawSomething = true;
      } else if (/["'\/`]/.test(ch)) {
        for (;; --pos) {
          if (pos == 0) return;
          var next = stream.string.charAt(pos - 1);
          if (next == ch && stream.string.charAt(pos - 2) != "\\") {
            pos--;
            break;
          }
        }
      } else if (sawSomething && !depth) {
        ++pos;
        break;
      }
    }
    if (sawSomething && !depth) state.fatArrowAt = pos;
  }

  // Parser

  var atomicTypes = {
    "atom": true,
    "number": true,
    "variable": true,
    "string": true,
    "regexp": true,
    "this": true,
    "import": true,
    "jsonld-keyword": true
  };
  function JSLexical(indented, column, type, align, prev, info) {
    this.indented = indented;
    this.column = column;
    this.type = type;
    this.prev = prev;
    this.info = info;
    if (align != null) this.align = align;
  }
  function inScope(state, varname) {
    for (var v = state.localVars; v; v = v.next) if (v.name == varname) return true;
    for (var cx = state.context; cx; cx = cx.prev) {
      for (var v = cx.vars; v; v = v.next) if (v.name == varname) return true;
    }
  }
  function parseJS(state, style, type, content, stream) {
    var cc = state.cc;
    // Communicate our context to the combinators.
    // (Less wasteful than consing up a hundred closures on every call.)
    cx.state = state;
    cx.stream = stream;
    cx.marked = null;
    cx.cc = cc;
    cx.style = style;
    if (!state.lexical.hasOwnProperty("align")) state.lexical.align = true;
    while (true) {
      var combinator = cc.length ? cc.pop() : jsonMode ? expression : statement;
      if (combinator(type, content)) {
        while (cc.length && cc[cc.length - 1].lex) cc.pop()();
        if (cx.marked) return cx.marked;
        if (type == "variable" && inScope(state, content)) return "variableName.local";
        return style;
      }
    }
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
    cx.marked = "def";
    if (state.context) {
      if (state.lexical.info == "var" && state.context && state.context.block) {
        // FIXME function decls are also not block scoped
        var newContext = registerVarScoped(varname, state.context);
        if (newContext != null) {
          state.context = newContext;
          return;
        }
      } else if (!inList(varname, state.localVars)) {
        state.localVars = new Var(varname, state.localVars);
        return;
      }
    }
    // Fall through means this is global
    if (parserConfig.globalVars && !inList(varname, state.globalVars)) state.globalVars = new Var(varname, state.globalVars);
  }
  function registerVarScoped(varname, context) {
    if (!context) {
      return null;
    } else if (context.block) {
      var inner = registerVarScoped(varname, context.prev);
      if (!inner) return null;
      if (inner == context.prev) return context;
      return new Context(inner, context.vars, true);
    } else if (inList(varname, context.vars)) {
      return context;
    } else {
      return new Context(context.prev, new Var(varname, context.vars), false);
    }
  }
  function isModifier(name) {
    return name == "public" || name == "private" || name == "protected" || name == "abstract" || name == "readonly";
  }

  // Combinators

  function Context(prev, vars, block) {
    this.prev = prev;
    this.vars = vars;
    this.block = block;
  }
  function Var(name, next) {
    this.name = name;
    this.next = next;
  }
  var defaultVars = new Var("this", new Var("arguments", null));
  function pushcontext() {
    cx.state.context = new Context(cx.state.context, cx.state.localVars, false);
    cx.state.localVars = defaultVars;
  }
  function pushblockcontext() {
    cx.state.context = new Context(cx.state.context, cx.state.localVars, true);
    cx.state.localVars = null;
  }
  pushcontext.lex = pushblockcontext.lex = true;
  function popcontext() {
    cx.state.localVars = cx.state.context.vars;
    cx.state.context = cx.state.context.prev;
  }
  popcontext.lex = true;
  function pushlex(type, info) {
    var result = function () {
      var state = cx.state,
        indent = state.indented;
      if (state.lexical.type == "stat") indent = state.lexical.indented;else for (var outer = state.lexical; outer && outer.type == ")" && outer.align; outer = outer.prev) indent = outer.indented;
      state.lexical = new JSLexical(indent, cx.stream.column(), type, null, state.lexical, info);
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
    function exp(type) {
      if (type == wanted) return cont();else if (wanted == ";" || type == "}" || type == ")" || type == "]") return pass();else return cont(exp);
    }
    ;
    return exp;
  }
  function statement(type, value) {
    if (type == "var") return cont(pushlex("vardef", value), vardef, expect(";"), poplex);
    if (type == "keyword a") return cont(pushlex("form"), parenExpr, statement, poplex);
    if (type == "keyword b") return cont(pushlex("form"), statement, poplex);
    if (type == "keyword d") return cx.stream.match(/^\s*$/, false) ? cont() : cont(pushlex("stat"), maybeexpression, expect(";"), poplex);
    if (type == "debugger") return cont(expect(";"));
    if (type == "{") return cont(pushlex("}"), pushblockcontext, block, poplex, popcontext);
    if (type == ";") return cont();
    if (type == "if") {
      if (cx.state.lexical.info == "else" && cx.state.cc[cx.state.cc.length - 1] == poplex) cx.state.cc.pop()();
      return cont(pushlex("form"), parenExpr, statement, poplex, maybeelse);
    }
    if (type == "function") return cont(functiondef);
    if (type == "for") return cont(pushlex("form"), pushblockcontext, forspec, statement, popcontext, poplex);
    if (type == "class" || isTS && value == "interface") {
      cx.marked = "keyword";
      return cont(pushlex("form", type == "class" ? type : value), className, poplex);
    }
    if (type == "variable") {
      if (isTS && value == "declare") {
        cx.marked = "keyword";
        return cont(statement);
      } else if (isTS && (value == "module" || value == "enum" || value == "type") && cx.stream.match(/^\s*\w/, false)) {
        cx.marked = "keyword";
        if (value == "enum") return cont(enumdef);else if (value == "type") return cont(typename, expect("operator"), typeexpr, expect(";"));else return cont(pushlex("form"), pattern, expect("{"), pushlex("}"), block, poplex, poplex);
      } else if (isTS && value == "namespace") {
        cx.marked = "keyword";
        return cont(pushlex("form"), expression, statement, poplex);
      } else if (isTS && value == "abstract") {
        cx.marked = "keyword";
        return cont(statement);
      } else {
        return cont(pushlex("stat"), maybelabel);
      }
    }
    if (type == "switch") return cont(pushlex("form"), parenExpr, expect("{"), pushlex("}", "switch"), pushblockcontext, block, poplex, poplex, popcontext);
    if (type == "case") return cont(expression, expect(":"));
    if (type == "default") return cont(expect(":"));
    if (type == "catch") return cont(pushlex("form"), pushcontext, maybeCatchBinding, statement, poplex, popcontext);
    if (type == "export") return cont(pushlex("stat"), afterExport, poplex);
    if (type == "import") return cont(pushlex("stat"), afterImport, poplex);
    if (type == "async") return cont(statement);
    if (value == "@") return cont(expression, statement);
    return pass(pushlex("stat"), expression, expect(";"), poplex);
  }
  function maybeCatchBinding(type) {
    if (type == "(") return cont(funarg, expect(")"));
  }
  function expression(type, value) {
    return expressionInner(type, value, false);
  }
  function expressionNoComma(type, value) {
    return expressionInner(type, value, true);
  }
  function parenExpr(type) {
    if (type != "(") return pass();
    return cont(pushlex(")"), maybeexpression, expect(")"), poplex);
  }
  function expressionInner(type, value, noComma) {
    if (cx.state.fatArrowAt == cx.stream.start) {
      var body = noComma ? arrowBodyNoComma : arrowBody;
      if (type == "(") return cont(pushcontext, pushlex(")"), commasep(funarg, ")"), poplex, expect("=>"), body, popcontext);else if (type == "variable") return pass(pushcontext, pattern, expect("=>"), body, popcontext);
    }
    var maybeop = noComma ? maybeoperatorNoComma : maybeoperatorComma;
    if (atomicTypes.hasOwnProperty(type)) return cont(maybeop);
    if (type == "function") return cont(functiondef, maybeop);
    if (type == "class" || isTS && value == "interface") {
      cx.marked = "keyword";
      return cont(pushlex("form"), classExpression, poplex);
    }
    if (type == "keyword c" || type == "async") return cont(noComma ? expressionNoComma : expression);
    if (type == "(") return cont(pushlex(")"), maybeexpression, expect(")"), poplex, maybeop);
    if (type == "operator" || type == "spread") return cont(noComma ? expressionNoComma : expression);
    if (type == "[") return cont(pushlex("]"), arrayLiteral, poplex, maybeop);
    if (type == "{") return contCommasep(objprop, "}", null, maybeop);
    if (type == "quasi") return pass(quasi, maybeop);
    if (type == "new") return cont(maybeTarget(noComma));
    return cont();
  }
  function maybeexpression(type) {
    if (type.match(/[;\}\)\],]/)) return pass();
    return pass(expression);
  }
  function maybeoperatorComma(type, value) {
    if (type == ",") return cont(maybeexpression);
    return maybeoperatorNoComma(type, value, false);
  }
  function maybeoperatorNoComma(type, value, noComma) {
    var me = noComma == false ? maybeoperatorComma : maybeoperatorNoComma;
    var expr = noComma == false ? expression : expressionNoComma;
    if (type == "=>") return cont(pushcontext, noComma ? arrowBodyNoComma : arrowBody, popcontext);
    if (type == "operator") {
      if (/\+\+|--/.test(value) || isTS && value == "!") return cont(me);
      if (isTS && value == "<" && cx.stream.match(/^([^<>]|<[^<>]*>)*>\s*\(/, false)) return cont(pushlex(">"), commasep(typeexpr, ">"), poplex, me);
      if (value == "?") return cont(expression, expect(":"), expr);
      return cont(expr);
    }
    if (type == "quasi") {
      return pass(quasi, me);
    }
    if (type == ";") return;
    if (type == "(") return contCommasep(expressionNoComma, ")", "call", me);
    if (type == ".") return cont(property, me);
    if (type == "[") return cont(pushlex("]"), maybeexpression, expect("]"), poplex, me);
    if (isTS && value == "as") {
      cx.marked = "keyword";
      return cont(typeexpr, me);
    }
    if (type == "regexp") {
      cx.state.lastType = cx.marked = "operator";
      cx.stream.backUp(cx.stream.pos - cx.stream.start - 1);
      return cont(expr);
    }
  }
  function quasi(type, value) {
    if (type != "quasi") return pass();
    if (value.slice(value.length - 2) != "${") return cont(quasi);
    return cont(maybeexpression, continueQuasi);
  }
  function continueQuasi(type) {
    if (type == "}") {
      cx.marked = "string.special";
      cx.state.tokenize = tokenQuasi;
      return cont(quasi);
    }
  }
  function arrowBody(type) {
    findFatArrow(cx.stream, cx.state);
    return pass(type == "{" ? statement : expression);
  }
  function arrowBodyNoComma(type) {
    findFatArrow(cx.stream, cx.state);
    return pass(type == "{" ? statement : expressionNoComma);
  }
  function maybeTarget(noComma) {
    return function (type) {
      if (type == ".") return cont(noComma ? targetNoComma : target);else if (type == "variable" && isTS) return cont(maybeTypeArgs, noComma ? maybeoperatorNoComma : maybeoperatorComma);else return pass(noComma ? expressionNoComma : expression);
    };
  }
  function target(_, value) {
    if (value == "target") {
      cx.marked = "keyword";
      return cont(maybeoperatorComma);
    }
  }
  function targetNoComma(_, value) {
    if (value == "target") {
      cx.marked = "keyword";
      return cont(maybeoperatorNoComma);
    }
  }
  function maybelabel(type) {
    if (type == ":") return cont(poplex, statement);
    return pass(maybeoperatorComma, expect(";"), poplex);
  }
  function property(type) {
    if (type == "variable") {
      cx.marked = "property";
      return cont();
    }
  }
  function objprop(type, value) {
    if (type == "async") {
      cx.marked = "property";
      return cont(objprop);
    } else if (type == "variable" || cx.style == "keyword") {
      cx.marked = "property";
      if (value == "get" || value == "set") return cont(getterSetter);
      var m; // Work around fat-arrow-detection complication for detecting typescript typed arrow params
      if (isTS && cx.state.fatArrowAt == cx.stream.start && (m = cx.stream.match(/^\s*:\s*/, false))) cx.state.fatArrowAt = cx.stream.pos + m[0].length;
      return cont(afterprop);
    } else if (type == "number" || type == "string") {
      cx.marked = jsonldMode ? "property" : cx.style + " property";
      return cont(afterprop);
    } else if (type == "jsonld-keyword") {
      return cont(afterprop);
    } else if (isTS && isModifier(value)) {
      cx.marked = "keyword";
      return cont(objprop);
    } else if (type == "[") {
      return cont(expression, maybetype, expect("]"), afterprop);
    } else if (type == "spread") {
      return cont(expressionNoComma, afterprop);
    } else if (value == "*") {
      cx.marked = "keyword";
      return cont(objprop);
    } else if (type == ":") {
      return pass(afterprop);
    }
  }
  function getterSetter(type) {
    if (type != "variable") return pass(afterprop);
    cx.marked = "property";
    return cont(functiondef);
  }
  function afterprop(type) {
    if (type == ":") return cont(expressionNoComma);
    if (type == "(") return pass(functiondef);
  }
  function commasep(what, end, sep) {
    function proceed(type, value) {
      if (sep ? sep.indexOf(type) > -1 : type == ",") {
        var lex = cx.state.lexical;
        if (lex.info == "call") lex.pos = (lex.pos || 0) + 1;
        return cont(function (type, value) {
          if (type == end || value == end) return pass();
          return pass(what);
        }, proceed);
      }
      if (type == end || value == end) return cont();
      if (sep && sep.indexOf(";") > -1) return pass(what);
      return cont(expect(end));
    }
    return function (type, value) {
      if (type == end || value == end) return cont();
      return pass(what, proceed);
    };
  }
  function contCommasep(what, end, info) {
    for (var i = 3; i < arguments.length; i++) cx.cc.push(arguments[i]);
    return cont(pushlex(end, info), commasep(what, end), poplex);
  }
  function block(type) {
    if (type == "}") return cont();
    return pass(statement, block);
  }
  function maybetype(type, value) {
    if (isTS) {
      if (type == ":") return cont(typeexpr);
      if (value == "?") return cont(maybetype);
    }
  }
  function maybetypeOrIn(type, value) {
    if (isTS && (type == ":" || value == "in")) return cont(typeexpr);
  }
  function mayberettype(type) {
    if (isTS && type == ":") {
      if (cx.stream.match(/^\s*\w+\s+is\b/, false)) return cont(expression, isKW, typeexpr);else return cont(typeexpr);
    }
  }
  function isKW(_, value) {
    if (value == "is") {
      cx.marked = "keyword";
      return cont();
    }
  }
  function typeexpr(type, value) {
    if (value == "keyof" || value == "typeof" || value == "infer" || value == "readonly") {
      cx.marked = "keyword";
      return cont(value == "typeof" ? expressionNoComma : typeexpr);
    }
    if (type == "variable" || value == "void") {
      cx.marked = "type";
      return cont(afterType);
    }
    if (value == "|" || value == "&") return cont(typeexpr);
    if (type == "string" || type == "number" || type == "atom") return cont(afterType);
    if (type == "[") return cont(pushlex("]"), commasep(typeexpr, "]", ","), poplex, afterType);
    if (type == "{") return cont(pushlex("}"), typeprops, poplex, afterType);
    if (type == "(") return cont(commasep(typearg, ")"), maybeReturnType, afterType);
    if (type == "<") return cont(commasep(typeexpr, ">"), typeexpr);
    if (type == "quasi") return pass(quasiType, afterType);
  }
  function maybeReturnType(type) {
    if (type == "=>") return cont(typeexpr);
  }
  function typeprops(type) {
    if (type.match(/[\}\)\]]/)) return cont();
    if (type == "," || type == ";") return cont(typeprops);
    return pass(typeprop, typeprops);
  }
  function typeprop(type, value) {
    if (type == "variable" || cx.style == "keyword") {
      cx.marked = "property";
      return cont(typeprop);
    } else if (value == "?" || type == "number" || type == "string") {
      return cont(typeprop);
    } else if (type == ":") {
      return cont(typeexpr);
    } else if (type == "[") {
      return cont(expect("variable"), maybetypeOrIn, expect("]"), typeprop);
    } else if (type == "(") {
      return pass(functiondecl, typeprop);
    } else if (!type.match(/[;\}\)\],]/)) {
      return cont();
    }
  }
  function quasiType(type, value) {
    if (type != "quasi") return pass();
    if (value.slice(value.length - 2) != "${") return cont(quasiType);
    return cont(typeexpr, continueQuasiType);
  }
  function continueQuasiType(type) {
    if (type == "}") {
      cx.marked = "string.special";
      cx.state.tokenize = tokenQuasi;
      return cont(quasiType);
    }
  }
  function typearg(type, value) {
    if (type == "variable" && cx.stream.match(/^\s*[?:]/, false) || value == "?") return cont(typearg);
    if (type == ":") return cont(typeexpr);
    if (type == "spread") return cont(typearg);
    return pass(typeexpr);
  }
  function afterType(type, value) {
    if (value == "<") return cont(pushlex(">"), commasep(typeexpr, ">"), poplex, afterType);
    if (value == "|" || type == "." || value == "&") return cont(typeexpr);
    if (type == "[") return cont(typeexpr, expect("]"), afterType);
    if (value == "extends" || value == "implements") {
      cx.marked = "keyword";
      return cont(typeexpr);
    }
    if (value == "?") return cont(typeexpr, expect(":"), typeexpr);
  }
  function maybeTypeArgs(_, value) {
    if (value == "<") return cont(pushlex(">"), commasep(typeexpr, ">"), poplex, afterType);
  }
  function typeparam() {
    return pass(typeexpr, maybeTypeDefault);
  }
  function maybeTypeDefault(_, value) {
    if (value == "=") return cont(typeexpr);
  }
  function vardef(_, value) {
    if (value == "enum") {
      cx.marked = "keyword";
      return cont(enumdef);
    }
    return pass(pattern, maybetype, maybeAssign, vardefCont);
  }
  function pattern(type, value) {
    if (isTS && isModifier(value)) {
      cx.marked = "keyword";
      return cont(pattern);
    }
    if (type == "variable") {
      register(value);
      return cont();
    }
    if (type == "spread") return cont(pattern);
    if (type == "[") return contCommasep(eltpattern, "]");
    if (type == "{") return contCommasep(proppattern, "}");
  }
  function proppattern(type, value) {
    if (type == "variable" && !cx.stream.match(/^\s*:/, false)) {
      register(value);
      return cont(maybeAssign);
    }
    if (type == "variable") cx.marked = "property";
    if (type == "spread") return cont(pattern);
    if (type == "}") return pass();
    if (type == "[") return cont(expression, expect(']'), expect(':'), proppattern);
    return cont(expect(":"), pattern, maybeAssign);
  }
  function eltpattern() {
    return pass(pattern, maybeAssign);
  }
  function maybeAssign(_type, value) {
    if (value == "=") return cont(expressionNoComma);
  }
  function vardefCont(type) {
    if (type == ",") return cont(vardef);
  }
  function maybeelse(type, value) {
    if (type == "keyword b" && value == "else") return cont(pushlex("form", "else"), statement, poplex);
  }
  function forspec(type, value) {
    if (value == "await") return cont(forspec);
    if (type == "(") return cont(pushlex(")"), forspec1, poplex);
  }
  function forspec1(type) {
    if (type == "var") return cont(vardef, forspec2);
    if (type == "variable") return cont(forspec2);
    return pass(forspec2);
  }
  function forspec2(type, value) {
    if (type == ")") return cont();
    if (type == ";") return cont(forspec2);
    if (value == "in" || value == "of") {
      cx.marked = "keyword";
      return cont(expression, forspec2);
    }
    return pass(expression, forspec2);
  }
  function functiondef(type, value) {
    if (value == "*") {
      cx.marked = "keyword";
      return cont(functiondef);
    }
    if (type == "variable") {
      register(value);
      return cont(functiondef);
    }
    if (type == "(") return cont(pushcontext, pushlex(")"), commasep(funarg, ")"), poplex, mayberettype, statement, popcontext);
    if (isTS && value == "<") return cont(pushlex(">"), commasep(typeparam, ">"), poplex, functiondef);
  }
  function functiondecl(type, value) {
    if (value == "*") {
      cx.marked = "keyword";
      return cont(functiondecl);
    }
    if (type == "variable") {
      register(value);
      return cont(functiondecl);
    }
    if (type == "(") return cont(pushcontext, pushlex(")"), commasep(funarg, ")"), poplex, mayberettype, popcontext);
    if (isTS && value == "<") return cont(pushlex(">"), commasep(typeparam, ">"), poplex, functiondecl);
  }
  function typename(type, value) {
    if (type == "keyword" || type == "variable") {
      cx.marked = "type";
      return cont(typename);
    } else if (value == "<") {
      return cont(pushlex(">"), commasep(typeparam, ">"), poplex);
    }
  }
  function funarg(type, value) {
    if (value == "@") cont(expression, funarg);
    if (type == "spread") return cont(funarg);
    if (isTS && isModifier(value)) {
      cx.marked = "keyword";
      return cont(funarg);
    }
    if (isTS && type == "this") return cont(maybetype, maybeAssign);
    return pass(pattern, maybetype, maybeAssign);
  }
  function classExpression(type, value) {
    // Class expressions may have an optional name.
    if (type == "variable") return className(type, value);
    return classNameAfter(type, value);
  }
  function className(type, value) {
    if (type == "variable") {
      register(value);
      return cont(classNameAfter);
    }
  }
  function classNameAfter(type, value) {
    if (value == "<") return cont(pushlex(">"), commasep(typeparam, ">"), poplex, classNameAfter);
    if (value == "extends" || value == "implements" || isTS && type == ",") {
      if (value == "implements") cx.marked = "keyword";
      return cont(isTS ? typeexpr : expression, classNameAfter);
    }
    if (type == "{") return cont(pushlex("}"), classBody, poplex);
  }
  function classBody(type, value) {
    if (type == "async" || type == "variable" && (value == "static" || value == "get" || value == "set" || isTS && isModifier(value)) && cx.stream.match(/^\s+#?[\w$\xa1-\uffff]/, false)) {
      cx.marked = "keyword";
      return cont(classBody);
    }
    if (type == "variable" || cx.style == "keyword") {
      cx.marked = "property";
      return cont(classfield, classBody);
    }
    if (type == "number" || type == "string") return cont(classfield, classBody);
    if (type == "[") return cont(expression, maybetype, expect("]"), classfield, classBody);
    if (value == "*") {
      cx.marked = "keyword";
      return cont(classBody);
    }
    if (isTS && type == "(") return pass(functiondecl, classBody);
    if (type == ";" || type == ",") return cont(classBody);
    if (type == "}") return cont();
    if (value == "@") return cont(expression, classBody);
  }
  function classfield(type, value) {
    if (value == "!" || value == "?") return cont(classfield);
    if (type == ":") return cont(typeexpr, maybeAssign);
    if (value == "=") return cont(expressionNoComma);
    var context = cx.state.lexical.prev,
      isInterface = context && context.info == "interface";
    return pass(isInterface ? functiondecl : functiondef);
  }
  function afterExport(type, value) {
    if (value == "*") {
      cx.marked = "keyword";
      return cont(maybeFrom, expect(";"));
    }
    if (value == "default") {
      cx.marked = "keyword";
      return cont(expression, expect(";"));
    }
    if (type == "{") return cont(commasep(exportField, "}"), maybeFrom, expect(";"));
    return pass(statement);
  }
  function exportField(type, value) {
    if (value == "as") {
      cx.marked = "keyword";
      return cont(expect("variable"));
    }
    if (type == "variable") return pass(expressionNoComma, exportField);
  }
  function afterImport(type) {
    if (type == "string") return cont();
    if (type == "(") return pass(expression);
    if (type == ".") return pass(maybeoperatorComma);
    return pass(importSpec, maybeMoreImports, maybeFrom);
  }
  function importSpec(type, value) {
    if (type == "{") return contCommasep(importSpec, "}");
    if (type == "variable") register(value);
    if (value == "*") cx.marked = "keyword";
    return cont(maybeAs);
  }
  function maybeMoreImports(type) {
    if (type == ",") return cont(importSpec, maybeMoreImports);
  }
  function maybeAs(_type, value) {
    if (value == "as") {
      cx.marked = "keyword";
      return cont(importSpec);
    }
  }
  function maybeFrom(_type, value) {
    if (value == "from") {
      cx.marked = "keyword";
      return cont(expression);
    }
  }
  function arrayLiteral(type) {
    if (type == "]") return cont();
    return pass(commasep(expressionNoComma, "]"));
  }
  function enumdef() {
    return pass(pushlex("form"), pattern, expect("{"), pushlex("}"), commasep(enummember, "}"), poplex, poplex);
  }
  function enummember() {
    return pass(pattern, maybeAssign);
  }
  function isContinuedStatement(state, textAfter) {
    return state.lastType == "operator" || state.lastType == "," || isOperatorChar.test(textAfter.charAt(0)) || /[,.]/.test(textAfter.charAt(0));
  }
  function expressionAllowed(stream, state, backUp) {
    return state.tokenize == tokenBase && /^(?:operator|sof|keyword [bcd]|case|new|export|default|spread|[\[{}\(,;:]|=>)$/.test(state.lastType) || state.lastType == "quasi" && /\{\s*$/.test(stream.string.slice(0, stream.pos - (backUp || 0)));
  }

  // Interface

  return {
    name: parserConfig.name,
    startState: function (indentUnit) {
      var state = {
        tokenize: tokenBase,
        lastType: "sof",
        cc: [],
        lexical: new JSLexical(-indentUnit, 0, "block", false),
        localVars: parserConfig.localVars,
        context: parserConfig.localVars && new Context(null, null, false),
        indented: 0
      };
      if (parserConfig.globalVars && typeof parserConfig.globalVars == "object") state.globalVars = parserConfig.globalVars;
      return state;
    },
    token: function (stream, state) {
      if (stream.sol()) {
        if (!state.lexical.hasOwnProperty("align")) state.lexical.align = false;
        state.indented = stream.indentation();
        findFatArrow(stream, state);
      }
      if (state.tokenize != tokenComment && stream.eatSpace()) return null;
      var style = state.tokenize(stream, state);
      if (type == "comment") return style;
      state.lastType = type == "operator" && (content == "++" || content == "--") ? "incdec" : type;
      return parseJS(state, style, type, content, stream);
    },
    indent: function (state, textAfter, cx) {
      if (state.tokenize == tokenComment || state.tokenize == tokenQuasi) return null;
      if (state.tokenize != tokenBase) return 0;
      var firstChar = textAfter && textAfter.charAt(0),
        lexical = state.lexical,
        top;
      // Kludge to prevent 'maybelse' from blocking lexical scope pops
      if (!/^\s*else\b/.test(textAfter)) for (var i = state.cc.length - 1; i >= 0; --i) {
        var c = state.cc[i];
        if (c == poplex) lexical = lexical.prev;else if (c != maybeelse && c != popcontext) break;
      }
      while ((lexical.type == "stat" || lexical.type == "form") && (firstChar == "}" || (top = state.cc[state.cc.length - 1]) && (top == maybeoperatorComma || top == maybeoperatorNoComma) && !/^[,\.=+\-*:?[\(]/.test(textAfter))) lexical = lexical.prev;
      if (statementIndent && lexical.type == ")" && lexical.prev.type == "stat") lexical = lexical.prev;
      var type = lexical.type,
        closing = firstChar == type;
      if (type == "vardef") return lexical.indented + (state.lastType == "operator" || state.lastType == "," ? lexical.info.length + 1 : 0);else if (type == "form" && firstChar == "{") return lexical.indented;else if (type == "form") return lexical.indented + cx.unit;else if (type == "stat") return lexical.indented + (isContinuedStatement(state, textAfter) ? statementIndent || cx.unit : 0);else if (lexical.info == "switch" && !closing && parserConfig.doubleIndentSwitch != false) return lexical.indented + (/^(?:case|default)\b/.test(textAfter) ? cx.unit : 2 * cx.unit);else if (lexical.align) return lexical.column + (closing ? 0 : 1);else return lexical.indented + (closing ? 0 : cx.unit);
    },
    languageData: {
      indentOnInput: /^\s*(?:case .*?:|default:|\{|\})$/,
      commentTokens: jsonMode ? undefined : {
        line: "//",
        block: {
          open: "/*",
          close: "*/"
        }
      },
      closeBrackets: {
        brackets: ["(", "[", "{", "'", '"', "`"]
      },
      wordChars: "$"
    }
  };
}
;
const javascript = mkJavaScript({
  name: "javascript"
});
const json = mkJavaScript({
  name: "json",
  json: true
});
const jsonld = mkJavaScript({
  name: "json",
  jsonld: true
});
const typescript = mkJavaScript({
  name: "typescript",
  typescript: true
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjg5MC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7OztBQ3haQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvcHVnLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvamF2YXNjcmlwdC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBqYXZhc2NyaXB0IH0gZnJvbSBcIi4vamF2YXNjcmlwdC5qc1wiO1xudmFyIEFUVFJTX05FU1QgPSB7XG4gICd7JzogJ30nLFxuICAnKCc6ICcpJyxcbiAgJ1snOiAnXSdcbn07XG5mdW5jdGlvbiBkZWZhdWx0Q29weVN0YXRlKHN0YXRlKSB7XG4gIGlmICh0eXBlb2Ygc3RhdGUgIT0gXCJvYmplY3RcIikgcmV0dXJuIHN0YXRlO1xuICBsZXQgbmV3U3RhdGUgPSB7fTtcbiAgZm9yIChsZXQgcHJvcCBpbiBzdGF0ZSkge1xuICAgIGxldCB2YWwgPSBzdGF0ZVtwcm9wXTtcbiAgICBuZXdTdGF0ZVtwcm9wXSA9IHZhbCBpbnN0YW5jZW9mIEFycmF5ID8gdmFsLnNsaWNlKCkgOiB2YWw7XG4gIH1cbiAgcmV0dXJuIG5ld1N0YXRlO1xufVxuY2xhc3MgU3RhdGUge1xuICBjb25zdHJ1Y3RvcihpbmRlbnRVbml0KSB7XG4gICAgdGhpcy5pbmRlbnRVbml0ID0gaW5kZW50VW5pdDtcbiAgICB0aGlzLmphdmFTY3JpcHRMaW5lID0gZmFsc2U7XG4gICAgdGhpcy5qYXZhU2NyaXB0TGluZUV4Y2x1ZGVzQ29sb24gPSBmYWxzZTtcbiAgICB0aGlzLmphdmFTY3JpcHRBcmd1bWVudHMgPSBmYWxzZTtcbiAgICB0aGlzLmphdmFTY3JpcHRBcmd1bWVudHNEZXB0aCA9IDA7XG4gICAgdGhpcy5pc0ludGVycG9sYXRpbmcgPSBmYWxzZTtcbiAgICB0aGlzLmludGVycG9sYXRpb25OZXN0aW5nID0gMDtcbiAgICB0aGlzLmpzU3RhdGUgPSBqYXZhc2NyaXB0LnN0YXJ0U3RhdGUoaW5kZW50VW5pdCk7XG4gICAgdGhpcy5yZXN0T2ZMaW5lID0gJyc7XG4gICAgdGhpcy5pc0luY2x1ZGVGaWx0ZXJlZCA9IGZhbHNlO1xuICAgIHRoaXMuaXNFYWNoID0gZmFsc2U7XG4gICAgdGhpcy5sYXN0VGFnID0gJyc7XG5cbiAgICAvLyBBdHRyaWJ1dGVzIE1vZGVcbiAgICB0aGlzLmlzQXR0cnMgPSBmYWxzZTtcbiAgICB0aGlzLmF0dHJzTmVzdCA9IFtdO1xuICAgIHRoaXMuaW5BdHRyaWJ1dGVOYW1lID0gdHJ1ZTtcbiAgICB0aGlzLmF0dHJpYnV0ZUlzVHlwZSA9IGZhbHNlO1xuICAgIHRoaXMuYXR0clZhbHVlID0gJyc7XG5cbiAgICAvLyBJbmRlbnRlZCBNb2RlXG4gICAgdGhpcy5pbmRlbnRPZiA9IEluZmluaXR5O1xuICAgIHRoaXMuaW5kZW50VG9rZW4gPSAnJztcbiAgfVxuICBjb3B5KCkge1xuICAgIHZhciByZXMgPSBuZXcgU3RhdGUodGhpcy5pbmRlbnRVbml0KTtcbiAgICByZXMuamF2YVNjcmlwdExpbmUgPSB0aGlzLmphdmFTY3JpcHRMaW5lO1xuICAgIHJlcy5qYXZhU2NyaXB0TGluZUV4Y2x1ZGVzQ29sb24gPSB0aGlzLmphdmFTY3JpcHRMaW5lRXhjbHVkZXNDb2xvbjtcbiAgICByZXMuamF2YVNjcmlwdEFyZ3VtZW50cyA9IHRoaXMuamF2YVNjcmlwdEFyZ3VtZW50cztcbiAgICByZXMuamF2YVNjcmlwdEFyZ3VtZW50c0RlcHRoID0gdGhpcy5qYXZhU2NyaXB0QXJndW1lbnRzRGVwdGg7XG4gICAgcmVzLmlzSW50ZXJwb2xhdGluZyA9IHRoaXMuaXNJbnRlcnBvbGF0aW5nO1xuICAgIHJlcy5pbnRlcnBvbGF0aW9uTmVzdGluZyA9IHRoaXMuaW50ZXJwb2xhdGlvbk5lc3Rpbmc7XG4gICAgcmVzLmpzU3RhdGUgPSAoamF2YXNjcmlwdC5jb3B5U3RhdGUgfHwgZGVmYXVsdENvcHlTdGF0ZSkodGhpcy5qc1N0YXRlKTtcbiAgICByZXMucmVzdE9mTGluZSA9IHRoaXMucmVzdE9mTGluZTtcbiAgICByZXMuaXNJbmNsdWRlRmlsdGVyZWQgPSB0aGlzLmlzSW5jbHVkZUZpbHRlcmVkO1xuICAgIHJlcy5pc0VhY2ggPSB0aGlzLmlzRWFjaDtcbiAgICByZXMubGFzdFRhZyA9IHRoaXMubGFzdFRhZztcbiAgICByZXMuaXNBdHRycyA9IHRoaXMuaXNBdHRycztcbiAgICByZXMuYXR0cnNOZXN0ID0gdGhpcy5hdHRyc05lc3Quc2xpY2UoKTtcbiAgICByZXMuaW5BdHRyaWJ1dGVOYW1lID0gdGhpcy5pbkF0dHJpYnV0ZU5hbWU7XG4gICAgcmVzLmF0dHJpYnV0ZUlzVHlwZSA9IHRoaXMuYXR0cmlidXRlSXNUeXBlO1xuICAgIHJlcy5hdHRyVmFsdWUgPSB0aGlzLmF0dHJWYWx1ZTtcbiAgICByZXMuaW5kZW50T2YgPSB0aGlzLmluZGVudE9mO1xuICAgIHJlcy5pbmRlbnRUb2tlbiA9IHRoaXMuaW5kZW50VG9rZW47XG4gICAgcmV0dXJuIHJlcztcbiAgfVxufVxuZnVuY3Rpb24gamF2YVNjcmlwdChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAvLyBpZiBqYXZhU2NyaXB0TGluZSB3YXMgc2V0IGF0IGVuZCBvZiBsaW5lLCBpZ25vcmUgaXRcbiAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IGZhbHNlO1xuICAgIHN0YXRlLmphdmFTY3JpcHRMaW5lRXhjbHVkZXNDb2xvbiA9IGZhbHNlO1xuICB9XG4gIGlmIChzdGF0ZS5qYXZhU2NyaXB0TGluZSkge1xuICAgIGlmIChzdGF0ZS5qYXZhU2NyaXB0TGluZUV4Y2x1ZGVzQ29sb24gJiYgc3RyZWFtLnBlZWsoKSA9PT0gJzonKSB7XG4gICAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IGZhbHNlO1xuICAgICAgc3RhdGUuamF2YVNjcmlwdExpbmVFeGNsdWRlc0NvbG9uID0gZmFsc2U7XG4gICAgICByZXR1cm47XG4gICAgfVxuICAgIHZhciB0b2sgPSBqYXZhc2NyaXB0LnRva2VuKHN0cmVhbSwgc3RhdGUuanNTdGF0ZSk7XG4gICAgaWYgKHN0cmVhbS5lb2woKSkgc3RhdGUuamF2YVNjcmlwdExpbmUgPSBmYWxzZTtcbiAgICByZXR1cm4gdG9rIHx8IHRydWU7XG4gIH1cbn1cbmZ1bmN0aW9uIGphdmFTY3JpcHRBcmd1bWVudHMoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RhdGUuamF2YVNjcmlwdEFyZ3VtZW50cykge1xuICAgIGlmIChzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzRGVwdGggPT09IDAgJiYgc3RyZWFtLnBlZWsoKSAhPT0gJygnKSB7XG4gICAgICBzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzID0gZmFsc2U7XG4gICAgICByZXR1cm47XG4gICAgfVxuICAgIGlmIChzdHJlYW0ucGVlaygpID09PSAnKCcpIHtcbiAgICAgIHN0YXRlLmphdmFTY3JpcHRBcmd1bWVudHNEZXB0aCsrO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gJyknKSB7XG4gICAgICBzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzRGVwdGgtLTtcbiAgICB9XG4gICAgaWYgKHN0YXRlLmphdmFTY3JpcHRBcmd1bWVudHNEZXB0aCA9PT0gMCkge1xuICAgICAgc3RhdGUuamF2YVNjcmlwdEFyZ3VtZW50cyA9IGZhbHNlO1xuICAgICAgcmV0dXJuO1xuICAgIH1cbiAgICB2YXIgdG9rID0gamF2YXNjcmlwdC50b2tlbihzdHJlYW0sIHN0YXRlLmpzU3RhdGUpO1xuICAgIHJldHVybiB0b2sgfHwgdHJ1ZTtcbiAgfVxufVxuZnVuY3Rpb24geWllbGRTdGF0ZW1lbnQoc3RyZWFtKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL155aWVsZFxcYi8pKSB7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxufVxuZnVuY3Rpb24gZG9jdHlwZShzdHJlYW0pIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXig/OmRvY3R5cGUpICooW15cXG5dKyk/LykpIHJldHVybiAnbWV0YSc7XG59XG5mdW5jdGlvbiBpbnRlcnBvbGF0aW9uKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgnI3snKSkge1xuICAgIHN0YXRlLmlzSW50ZXJwb2xhdGluZyA9IHRydWU7XG4gICAgc3RhdGUuaW50ZXJwb2xhdGlvbk5lc3RpbmcgPSAwO1xuICAgIHJldHVybiAncHVuY3R1YXRpb24nO1xuICB9XG59XG5mdW5jdGlvbiBpbnRlcnBvbGF0aW9uQ29udGludWVkKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0YXRlLmlzSW50ZXJwb2xhdGluZykge1xuICAgIGlmIChzdHJlYW0ucGVlaygpID09PSAnfScpIHtcbiAgICAgIHN0YXRlLmludGVycG9sYXRpb25OZXN0aW5nLS07XG4gICAgICBpZiAoc3RhdGUuaW50ZXJwb2xhdGlvbk5lc3RpbmcgPCAwKSB7XG4gICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgIHN0YXRlLmlzSW50ZXJwb2xhdGluZyA9IGZhbHNlO1xuICAgICAgICByZXR1cm4gJ3B1bmN0dWF0aW9uJztcbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5wZWVrKCkgPT09ICd7Jykge1xuICAgICAgc3RhdGUuaW50ZXJwb2xhdGlvbk5lc3RpbmcrKztcbiAgICB9XG4gICAgcmV0dXJuIGphdmFzY3JpcHQudG9rZW4oc3RyZWFtLCBzdGF0ZS5qc1N0YXRlKSB8fCB0cnVlO1xuICB9XG59XG5mdW5jdGlvbiBjYXNlU3RhdGVtZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXmNhc2VcXGIvKSkge1xuICAgIHN0YXRlLmphdmFTY3JpcHRMaW5lID0gdHJ1ZTtcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG59XG5mdW5jdGlvbiB3aGVuKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXndoZW5cXGIvKSkge1xuICAgIHN0YXRlLmphdmFTY3JpcHRMaW5lID0gdHJ1ZTtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZUV4Y2x1ZGVzQ29sb24gPSB0cnVlO1xuICAgIHJldHVybiAna2V5d29yZCc7XG4gIH1cbn1cbmZ1bmN0aW9uIGRlZmF1bHRTdGF0ZW1lbnQoc3RyZWFtKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL15kZWZhdWx0XFxiLykpIHtcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG59XG5mdW5jdGlvbiBleHRlbmRzU3RhdGVtZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXmV4dGVuZHM/XFxiLykpIHtcbiAgICBzdGF0ZS5yZXN0T2ZMaW5lID0gJ3N0cmluZyc7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxufVxuZnVuY3Rpb24gYXBwZW5kKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXmFwcGVuZFxcYi8pKSB7XG4gICAgc3RhdGUucmVzdE9mTGluZSA9ICd2YXJpYWJsZSc7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxufVxuZnVuY3Rpb24gcHJlcGVuZChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL15wcmVwZW5kXFxiLykpIHtcbiAgICBzdGF0ZS5yZXN0T2ZMaW5lID0gJ3ZhcmlhYmxlJztcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG59XG5mdW5jdGlvbiBibG9jayhzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL15ibG9ja1xcYiAqKD86KHByZXBlbmR8YXBwZW5kKVxcYik/LykpIHtcbiAgICBzdGF0ZS5yZXN0T2ZMaW5lID0gJ3ZhcmlhYmxlJztcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG59XG5mdW5jdGlvbiBpbmNsdWRlKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXmluY2x1ZGVcXGIvKSkge1xuICAgIHN0YXRlLnJlc3RPZkxpbmUgPSAnc3RyaW5nJztcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG59XG5mdW5jdGlvbiBpbmNsdWRlRmlsdGVyZWQoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKC9eaW5jbHVkZTooW2EtekEtWjAtOVxcLV0rKS8sIGZhbHNlKSAmJiBzdHJlYW0ubWF0Y2goJ2luY2x1ZGUnKSkge1xuICAgIHN0YXRlLmlzSW5jbHVkZUZpbHRlcmVkID0gdHJ1ZTtcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG59XG5mdW5jdGlvbiBpbmNsdWRlRmlsdGVyZWRDb250aW51ZWQoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RhdGUuaXNJbmNsdWRlRmlsdGVyZWQpIHtcbiAgICB2YXIgdG9rID0gZmlsdGVyKHN0cmVhbSwgc3RhdGUpO1xuICAgIHN0YXRlLmlzSW5jbHVkZUZpbHRlcmVkID0gZmFsc2U7XG4gICAgc3RhdGUucmVzdE9mTGluZSA9ICdzdHJpbmcnO1xuICAgIHJldHVybiB0b2s7XG4gIH1cbn1cbmZ1bmN0aW9uIG1peGluKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXm1peGluXFxiLykpIHtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IHRydWU7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxufVxuZnVuY3Rpb24gY2FsbChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL15cXCsoWy1cXHddKykvKSkge1xuICAgIGlmICghc3RyZWFtLm1hdGNoKC9eXFwoICpbLVxcd10rICo9LywgZmFsc2UpKSB7XG4gICAgICBzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmphdmFTY3JpcHRBcmd1bWVudHNEZXB0aCA9IDA7XG4gICAgfVxuICAgIHJldHVybiAndmFyaWFibGUnO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goJysjeycsIGZhbHNlKSkge1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgc3RhdGUubWl4aW5DYWxsQWZ0ZXIgPSB0cnVlO1xuICAgIHJldHVybiBpbnRlcnBvbGF0aW9uKHN0cmVhbSwgc3RhdGUpO1xuICB9XG59XG5mdW5jdGlvbiBjYWxsQXJndW1lbnRzKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0YXRlLm1peGluQ2FsbEFmdGVyKSB7XG4gICAgc3RhdGUubWl4aW5DYWxsQWZ0ZXIgPSBmYWxzZTtcbiAgICBpZiAoIXN0cmVhbS5tYXRjaCgvXlxcKCAqWy1cXHddKyAqPS8sIGZhbHNlKSkge1xuICAgICAgc3RhdGUuamF2YVNjcmlwdEFyZ3VtZW50cyA9IHRydWU7XG4gICAgICBzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzRGVwdGggPSAwO1xuICAgIH1cbiAgICByZXR1cm4gdHJ1ZTtcbiAgfVxufVxuZnVuY3Rpb24gY29uZGl0aW9uYWwoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKC9eKGlmfHVubGVzc3xlbHNlIGlmfGVsc2UpXFxiLykpIHtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IHRydWU7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxufVxuZnVuY3Rpb24gZWFjaChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL14oLSAqKT8oZWFjaHxmb3IpXFxiLykpIHtcbiAgICBzdGF0ZS5pc0VhY2ggPSB0cnVlO1xuICAgIHJldHVybiAna2V5d29yZCc7XG4gIH1cbn1cbmZ1bmN0aW9uIGVhY2hDb250aW51ZWQoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RhdGUuaXNFYWNoKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXiBpblxcYi8pKSB7XG4gICAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IHRydWU7XG4gICAgICBzdGF0ZS5pc0VhY2ggPSBmYWxzZTtcbiAgICAgIHJldHVybiAna2V5d29yZCc7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0uc29sKCkgfHwgc3RyZWFtLmVvbCgpKSB7XG4gICAgICBzdGF0ZS5pc0VhY2ggPSBmYWxzZTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5uZXh0KCkpIHtcbiAgICAgIHdoaWxlICghc3RyZWFtLm1hdGNoKC9eIGluXFxiLywgZmFsc2UpICYmIHN0cmVhbS5uZXh0KCkpIHt9XG4gICAgICByZXR1cm4gJ3ZhcmlhYmxlJztcbiAgICB9XG4gIH1cbn1cbmZ1bmN0aW9uIHdoaWxlU3RhdGVtZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXndoaWxlXFxiLykpIHtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IHRydWU7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxufVxuZnVuY3Rpb24gdGFnKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNhcHR1cmVzO1xuICBpZiAoY2FwdHVyZXMgPSBzdHJlYW0ubWF0Y2goL14oXFx3KD86Wy06XFx3XSpcXHcpPylcXC8/LykpIHtcbiAgICBzdGF0ZS5sYXN0VGFnID0gY2FwdHVyZXNbMV0udG9Mb3dlckNhc2UoKTtcbiAgICByZXR1cm4gJ3RhZyc7XG4gIH1cbn1cbmZ1bmN0aW9uIGZpbHRlcihzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL146KFtcXHdcXC1dKykvKSkge1xuICAgIHNldFN0cmluZ01vZGUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgcmV0dXJuICdhdG9tJztcbiAgfVxufVxuZnVuY3Rpb24gY29kZShzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL14oIT89fC0pLykpIHtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0TGluZSA9IHRydWU7XG4gICAgcmV0dXJuICdwdW5jdHVhdGlvbic7XG4gIH1cbn1cbmZ1bmN0aW9uIGlkKHN0cmVhbSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKC9eIyhbXFx3LV0rKS8pKSB7XG4gICAgcmV0dXJuICdidWlsdGluJztcbiAgfVxufVxuZnVuY3Rpb24gY2xhc3NOYW1lKHN0cmVhbSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKC9eXFwuKFtcXHctXSspLykpIHtcbiAgICByZXR1cm4gJ2NsYXNzTmFtZSc7XG4gIH1cbn1cbmZ1bmN0aW9uIGF0dHJzKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJygnKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICBzdGF0ZS5pc0F0dHJzID0gdHJ1ZTtcbiAgICBzdGF0ZS5hdHRyc05lc3QgPSBbXTtcbiAgICBzdGF0ZS5pbkF0dHJpYnV0ZU5hbWUgPSB0cnVlO1xuICAgIHN0YXRlLmF0dHJWYWx1ZSA9ICcnO1xuICAgIHN0YXRlLmF0dHJpYnV0ZUlzVHlwZSA9IGZhbHNlO1xuICAgIHJldHVybiAncHVuY3R1YXRpb24nO1xuICB9XG59XG5mdW5jdGlvbiBhdHRyc0NvbnRpbnVlZChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdGF0ZS5pc0F0dHJzKSB7XG4gICAgaWYgKEFUVFJTX05FU1Rbc3RyZWFtLnBlZWsoKV0pIHtcbiAgICAgIHN0YXRlLmF0dHJzTmVzdC5wdXNoKEFUVFJTX05FU1Rbc3RyZWFtLnBlZWsoKV0pO1xuICAgIH1cbiAgICBpZiAoc3RhdGUuYXR0cnNOZXN0W3N0YXRlLmF0dHJzTmVzdC5sZW5ndGggLSAxXSA9PT0gc3RyZWFtLnBlZWsoKSkge1xuICAgICAgc3RhdGUuYXR0cnNOZXN0LnBvcCgpO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdCgnKScpKSB7XG4gICAgICBzdGF0ZS5pc0F0dHJzID0gZmFsc2U7XG4gICAgICByZXR1cm4gJ3B1bmN0dWF0aW9uJztcbiAgICB9XG4gICAgaWYgKHN0YXRlLmluQXR0cmlidXRlTmFtZSAmJiBzdHJlYW0ubWF0Y2goL15bXj0sXFwpIV0rLykpIHtcbiAgICAgIGlmIChzdHJlYW0ucGVlaygpID09PSAnPScgfHwgc3RyZWFtLnBlZWsoKSA9PT0gJyEnKSB7XG4gICAgICAgIHN0YXRlLmluQXR0cmlidXRlTmFtZSA9IGZhbHNlO1xuICAgICAgICBzdGF0ZS5qc1N0YXRlID0gamF2YXNjcmlwdC5zdGFydFN0YXRlKDIpO1xuICAgICAgICBpZiAoc3RhdGUubGFzdFRhZyA9PT0gJ3NjcmlwdCcgJiYgc3RyZWFtLmN1cnJlbnQoKS50cmltKCkudG9Mb3dlckNhc2UoKSA9PT0gJ3R5cGUnKSB7XG4gICAgICAgICAgc3RhdGUuYXR0cmlidXRlSXNUeXBlID0gdHJ1ZTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICBzdGF0ZS5hdHRyaWJ1dGVJc1R5cGUgPSBmYWxzZTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgcmV0dXJuICdhdHRyaWJ1dGUnO1xuICAgIH1cbiAgICB2YXIgdG9rID0gamF2YXNjcmlwdC50b2tlbihzdHJlYW0sIHN0YXRlLmpzU3RhdGUpO1xuICAgIGlmIChzdGF0ZS5hdHRyc05lc3QubGVuZ3RoID09PSAwICYmICh0b2sgPT09ICdzdHJpbmcnIHx8IHRvayA9PT0gJ3ZhcmlhYmxlJyB8fCB0b2sgPT09ICdrZXl3b3JkJykpIHtcbiAgICAgIHRyeSB7XG4gICAgICAgIEZ1bmN0aW9uKCcnLCAndmFyIHggJyArIHN0YXRlLmF0dHJWYWx1ZS5yZXBsYWNlKC8sXFxzKiQvLCAnJykucmVwbGFjZSgvXiEvLCAnJykpO1xuICAgICAgICBzdGF0ZS5pbkF0dHJpYnV0ZU5hbWUgPSB0cnVlO1xuICAgICAgICBzdGF0ZS5hdHRyVmFsdWUgPSAnJztcbiAgICAgICAgc3RyZWFtLmJhY2tVcChzdHJlYW0uY3VycmVudCgpLmxlbmd0aCk7XG4gICAgICAgIHJldHVybiBhdHRyc0NvbnRpbnVlZChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIH0gY2F0Y2ggKGV4KSB7XG4gICAgICAgIC8vbm90IHRoZSBlbmQgb2YgYW4gYXR0cmlidXRlXG4gICAgICB9XG4gICAgfVxuICAgIHN0YXRlLmF0dHJWYWx1ZSArPSBzdHJlYW0uY3VycmVudCgpO1xuICAgIHJldHVybiB0b2sgfHwgdHJ1ZTtcbiAgfVxufVxuZnVuY3Rpb24gYXR0cmlidXRlc0Jsb2NrKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXiZhdHRyaWJ1dGVzXFxiLykpIHtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzID0gdHJ1ZTtcbiAgICBzdGF0ZS5qYXZhU2NyaXB0QXJndW1lbnRzRGVwdGggPSAwO1xuICAgIHJldHVybiAna2V5d29yZCc7XG4gIH1cbn1cbmZ1bmN0aW9uIGluZGVudChzdHJlYW0pIHtcbiAgaWYgKHN0cmVhbS5zb2woKSAmJiBzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiAnaW5kZW50JztcbiAgfVxufVxuZnVuY3Rpb24gY29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL14gKlxcL1xcLygtKT8oW15cXG5dKikvKSkge1xuICAgIHN0YXRlLmluZGVudE9mID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgc3RhdGUuaW5kZW50VG9rZW4gPSAnY29tbWVudCc7XG4gICAgcmV0dXJuICdjb21tZW50JztcbiAgfVxufVxuZnVuY3Rpb24gY29sb24oc3RyZWFtKSB7XG4gIGlmIChzdHJlYW0ubWF0Y2goL146ICovKSkge1xuICAgIHJldHVybiAnY29sb24nO1xuICB9XG59XG5mdW5jdGlvbiB0ZXh0KHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXig/OlxcfCA/fCApKFteXFxuXSspLykpIHtcbiAgICByZXR1cm4gJ3N0cmluZyc7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaCgvXig8W15cXG5dKikvLCBmYWxzZSkpIHtcbiAgICAvLyBodG1sIHN0cmluZ1xuICAgIHNldFN0cmluZ01vZGUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBzdGF0ZS5pbmRlbnRUb2tlbjtcbiAgfVxufVxuZnVuY3Rpb24gZG90KHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5lYXQoJy4nKSkge1xuICAgIHNldFN0cmluZ01vZGUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgcmV0dXJuICdkb3QnO1xuICB9XG59XG5mdW5jdGlvbiBmYWlsKHN0cmVhbSkge1xuICBzdHJlYW0ubmV4dCgpO1xuICByZXR1cm4gbnVsbDtcbn1cbmZ1bmN0aW9uIHNldFN0cmluZ01vZGUoc3RyZWFtLCBzdGF0ZSkge1xuICBzdGF0ZS5pbmRlbnRPZiA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICBzdGF0ZS5pbmRlbnRUb2tlbiA9ICdzdHJpbmcnO1xufVxuZnVuY3Rpb24gcmVzdE9mTGluZShzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAvLyBpZiByZXN0T2ZMaW5lIHdhcyBzZXQgYXQgZW5kIG9mIGxpbmUsIGlnbm9yZSBpdFxuICAgIHN0YXRlLnJlc3RPZkxpbmUgPSAnJztcbiAgfVxuICBpZiAoc3RhdGUucmVzdE9mTGluZSkge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICB2YXIgdG9rID0gc3RhdGUucmVzdE9mTGluZTtcbiAgICBzdGF0ZS5yZXN0T2ZMaW5lID0gJyc7XG4gICAgcmV0dXJuIHRvaztcbiAgfVxufVxuZnVuY3Rpb24gc3RhcnRTdGF0ZShpbmRlbnRVbml0KSB7XG4gIHJldHVybiBuZXcgU3RhdGUoaW5kZW50VW5pdCk7XG59XG5mdW5jdGlvbiBjb3B5U3RhdGUoc3RhdGUpIHtcbiAgcmV0dXJuIHN0YXRlLmNvcHkoKTtcbn1cbmZ1bmN0aW9uIG5leHRUb2tlbihzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciB0b2sgPSByZXN0T2ZMaW5lKHN0cmVhbSwgc3RhdGUpIHx8IGludGVycG9sYXRpb25Db250aW51ZWQoc3RyZWFtLCBzdGF0ZSkgfHwgaW5jbHVkZUZpbHRlcmVkQ29udGludWVkKHN0cmVhbSwgc3RhdGUpIHx8IGVhY2hDb250aW51ZWQoc3RyZWFtLCBzdGF0ZSkgfHwgYXR0cnNDb250aW51ZWQoc3RyZWFtLCBzdGF0ZSkgfHwgamF2YVNjcmlwdChzdHJlYW0sIHN0YXRlKSB8fCBqYXZhU2NyaXB0QXJndW1lbnRzKHN0cmVhbSwgc3RhdGUpIHx8IGNhbGxBcmd1bWVudHMoc3RyZWFtLCBzdGF0ZSkgfHwgeWllbGRTdGF0ZW1lbnQoc3RyZWFtKSB8fCBkb2N0eXBlKHN0cmVhbSkgfHwgaW50ZXJwb2xhdGlvbihzdHJlYW0sIHN0YXRlKSB8fCBjYXNlU3RhdGVtZW50KHN0cmVhbSwgc3RhdGUpIHx8IHdoZW4oc3RyZWFtLCBzdGF0ZSkgfHwgZGVmYXVsdFN0YXRlbWVudChzdHJlYW0pIHx8IGV4dGVuZHNTdGF0ZW1lbnQoc3RyZWFtLCBzdGF0ZSkgfHwgYXBwZW5kKHN0cmVhbSwgc3RhdGUpIHx8IHByZXBlbmQoc3RyZWFtLCBzdGF0ZSkgfHwgYmxvY2soc3RyZWFtLCBzdGF0ZSkgfHwgaW5jbHVkZShzdHJlYW0sIHN0YXRlKSB8fCBpbmNsdWRlRmlsdGVyZWQoc3RyZWFtLCBzdGF0ZSkgfHwgbWl4aW4oc3RyZWFtLCBzdGF0ZSkgfHwgY2FsbChzdHJlYW0sIHN0YXRlKSB8fCBjb25kaXRpb25hbChzdHJlYW0sIHN0YXRlKSB8fCBlYWNoKHN0cmVhbSwgc3RhdGUpIHx8IHdoaWxlU3RhdGVtZW50KHN0cmVhbSwgc3RhdGUpIHx8IHRhZyhzdHJlYW0sIHN0YXRlKSB8fCBmaWx0ZXIoc3RyZWFtLCBzdGF0ZSkgfHwgY29kZShzdHJlYW0sIHN0YXRlKSB8fCBpZChzdHJlYW0pIHx8IGNsYXNzTmFtZShzdHJlYW0pIHx8IGF0dHJzKHN0cmVhbSwgc3RhdGUpIHx8IGF0dHJpYnV0ZXNCbG9jayhzdHJlYW0sIHN0YXRlKSB8fCBpbmRlbnQoc3RyZWFtKSB8fCB0ZXh0KHN0cmVhbSwgc3RhdGUpIHx8IGNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkgfHwgY29sb24oc3RyZWFtKSB8fCBkb3Qoc3RyZWFtLCBzdGF0ZSkgfHwgZmFpbChzdHJlYW0pO1xuICByZXR1cm4gdG9rID09PSB0cnVlID8gbnVsbCA6IHRvaztcbn1cbmV4cG9ydCBjb25zdCBwdWcgPSB7XG4gIHN0YXJ0U3RhdGU6IHN0YXJ0U3RhdGUsXG4gIGNvcHlTdGF0ZTogY29weVN0YXRlLFxuICB0b2tlbjogbmV4dFRva2VuXG59OyIsImZ1bmN0aW9uIG1rSmF2YVNjcmlwdChwYXJzZXJDb25maWcpIHtcbiAgdmFyIHN0YXRlbWVudEluZGVudCA9IHBhcnNlckNvbmZpZy5zdGF0ZW1lbnRJbmRlbnQ7XG4gIHZhciBqc29ubGRNb2RlID0gcGFyc2VyQ29uZmlnLmpzb25sZDtcbiAgdmFyIGpzb25Nb2RlID0gcGFyc2VyQ29uZmlnLmpzb24gfHwganNvbmxkTW9kZTtcbiAgdmFyIGlzVFMgPSBwYXJzZXJDb25maWcudHlwZXNjcmlwdDtcbiAgdmFyIHdvcmRSRSA9IHBhcnNlckNvbmZpZy53b3JkQ2hhcmFjdGVycyB8fCAvW1xcdyRcXHhhMS1cXHVmZmZmXS87XG5cbiAgLy8gVG9rZW5pemVyXG5cbiAgdmFyIGtleXdvcmRzID0gZnVuY3Rpb24gKCkge1xuICAgIGZ1bmN0aW9uIGt3KHR5cGUpIHtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHR5cGU6IHR5cGUsXG4gICAgICAgIHN0eWxlOiBcImtleXdvcmRcIlxuICAgICAgfTtcbiAgICB9XG4gICAgdmFyIEEgPSBrdyhcImtleXdvcmQgYVwiKSxcbiAgICAgIEIgPSBrdyhcImtleXdvcmQgYlwiKSxcbiAgICAgIEMgPSBrdyhcImtleXdvcmQgY1wiKSxcbiAgICAgIEQgPSBrdyhcImtleXdvcmQgZFwiKTtcbiAgICB2YXIgb3BlcmF0b3IgPSBrdyhcIm9wZXJhdG9yXCIpLFxuICAgICAgYXRvbSA9IHtcbiAgICAgICAgdHlwZTogXCJhdG9tXCIsXG4gICAgICAgIHN0eWxlOiBcImF0b21cIlxuICAgICAgfTtcbiAgICByZXR1cm4ge1xuICAgICAgXCJpZlwiOiBrdyhcImlmXCIpLFxuICAgICAgXCJ3aGlsZVwiOiBBLFxuICAgICAgXCJ3aXRoXCI6IEEsXG4gICAgICBcImVsc2VcIjogQixcbiAgICAgIFwiZG9cIjogQixcbiAgICAgIFwidHJ5XCI6IEIsXG4gICAgICBcImZpbmFsbHlcIjogQixcbiAgICAgIFwicmV0dXJuXCI6IEQsXG4gICAgICBcImJyZWFrXCI6IEQsXG4gICAgICBcImNvbnRpbnVlXCI6IEQsXG4gICAgICBcIm5ld1wiOiBrdyhcIm5ld1wiKSxcbiAgICAgIFwiZGVsZXRlXCI6IEMsXG4gICAgICBcInZvaWRcIjogQyxcbiAgICAgIFwidGhyb3dcIjogQyxcbiAgICAgIFwiZGVidWdnZXJcIjoga3coXCJkZWJ1Z2dlclwiKSxcbiAgICAgIFwidmFyXCI6IGt3KFwidmFyXCIpLFxuICAgICAgXCJjb25zdFwiOiBrdyhcInZhclwiKSxcbiAgICAgIFwibGV0XCI6IGt3KFwidmFyXCIpLFxuICAgICAgXCJmdW5jdGlvblwiOiBrdyhcImZ1bmN0aW9uXCIpLFxuICAgICAgXCJjYXRjaFwiOiBrdyhcImNhdGNoXCIpLFxuICAgICAgXCJmb3JcIjoga3coXCJmb3JcIiksXG4gICAgICBcInN3aXRjaFwiOiBrdyhcInN3aXRjaFwiKSxcbiAgICAgIFwiY2FzZVwiOiBrdyhcImNhc2VcIiksXG4gICAgICBcImRlZmF1bHRcIjoga3coXCJkZWZhdWx0XCIpLFxuICAgICAgXCJpblwiOiBvcGVyYXRvcixcbiAgICAgIFwidHlwZW9mXCI6IG9wZXJhdG9yLFxuICAgICAgXCJpbnN0YW5jZW9mXCI6IG9wZXJhdG9yLFxuICAgICAgXCJ0cnVlXCI6IGF0b20sXG4gICAgICBcImZhbHNlXCI6IGF0b20sXG4gICAgICBcIm51bGxcIjogYXRvbSxcbiAgICAgIFwidW5kZWZpbmVkXCI6IGF0b20sXG4gICAgICBcIk5hTlwiOiBhdG9tLFxuICAgICAgXCJJbmZpbml0eVwiOiBhdG9tLFxuICAgICAgXCJ0aGlzXCI6IGt3KFwidGhpc1wiKSxcbiAgICAgIFwiY2xhc3NcIjoga3coXCJjbGFzc1wiKSxcbiAgICAgIFwic3VwZXJcIjoga3coXCJhdG9tXCIpLFxuICAgICAgXCJ5aWVsZFwiOiBDLFxuICAgICAgXCJleHBvcnRcIjoga3coXCJleHBvcnRcIiksXG4gICAgICBcImltcG9ydFwiOiBrdyhcImltcG9ydFwiKSxcbiAgICAgIFwiZXh0ZW5kc1wiOiBDLFxuICAgICAgXCJhd2FpdFwiOiBDXG4gICAgfTtcbiAgfSgpO1xuICB2YXIgaXNPcGVyYXRvckNoYXIgPSAvWytcXC0qJiU9PD4hP3x+XkBdLztcbiAgdmFyIGlzSnNvbmxkS2V5d29yZCA9IC9eQChjb250ZXh0fGlkfHZhbHVlfGxhbmd1YWdlfHR5cGV8Y29udGFpbmVyfGxpc3R8c2V0fHJldmVyc2V8aW5kZXh8YmFzZXx2b2NhYnxncmFwaClcIi87XG4gIGZ1bmN0aW9uIHJlYWRSZWdleHAoc3RyZWFtKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQsXG4gICAgICBpblNldCA9IGZhbHNlO1xuICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmICghZXNjYXBlZCkge1xuICAgICAgICBpZiAobmV4dCA9PSBcIi9cIiAmJiAhaW5TZXQpIHJldHVybjtcbiAgICAgICAgaWYgKG5leHQgPT0gXCJbXCIpIGluU2V0ID0gdHJ1ZTtlbHNlIGlmIChpblNldCAmJiBuZXh0ID09IFwiXVwiKSBpblNldCA9IGZhbHNlO1xuICAgICAgfVxuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIG5leHQgPT0gXCJcXFxcXCI7XG4gICAgfVxuICB9XG5cbiAgLy8gVXNlZCBhcyBzY3JhdGNoIHZhcmlhYmxlcyB0byBjb21tdW5pY2F0ZSBtdWx0aXBsZSB2YWx1ZXMgd2l0aG91dFxuICAvLyBjb25zaW5nIHVwIHRvbnMgb2Ygb2JqZWN0cy5cbiAgdmFyIHR5cGUsIGNvbnRlbnQ7XG4gIGZ1bmN0aW9uIHJldCh0cCwgc3R5bGUsIGNvbnQpIHtcbiAgICB0eXBlID0gdHA7XG4gICAgY29udGVudCA9IGNvbnQ7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoY2ggPT0gJ1wiJyB8fCBjaCA9PSBcIidcIikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBcIi5cIiAmJiBzdHJlYW0ubWF0Y2goL15cXGRbXFxkX10qKD86W2VFXVsrXFwtXT9bXFxkX10rKT8vKSkge1xuICAgICAgcmV0dXJuIHJldChcIm51bWJlclwiLCBcIm51bWJlclwiKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiLlwiICYmIHN0cmVhbS5tYXRjaChcIi4uXCIpKSB7XG4gICAgICByZXR1cm4gcmV0KFwic3ByZWFkXCIsIFwibWV0YVwiKTtcbiAgICB9IGVsc2UgaWYgKC9bXFxbXFxde31cXChcXCksO1xcOlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgICByZXR1cm4gcmV0KGNoKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiPVwiICYmIHN0cmVhbS5lYXQoXCI+XCIpKSB7XG4gICAgICByZXR1cm4gcmV0KFwiPT5cIiwgXCJvcGVyYXRvclwiKTtcbiAgICB9IGVsc2UgaWYgKGNoID09IFwiMFwiICYmIHN0cmVhbS5tYXRjaCgvXig/OnhbXFxkQS1GYS1mX10rfG9bMC03X10rfGJbMDFfXSspbj8vKSkge1xuICAgICAgcmV0dXJuIHJldChcIm51bWJlclwiLCBcIm51bWJlclwiKTtcbiAgICB9IGVsc2UgaWYgKC9cXGQvLnRlc3QoY2gpKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL15bXFxkX10qKD86bnwoPzpcXC5bXFxkX10qKT8oPzpbZUVdWytcXC1dP1tcXGRfXSspPyk/Lyk7XG4gICAgICByZXR1cm4gcmV0KFwibnVtYmVyXCIsIFwibnVtYmVyXCIpO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCIvXCIpIHtcbiAgICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ29tbWVudDtcbiAgICAgICAgcmV0dXJuIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gcmV0KFwiY29tbWVudFwiLCBcImNvbW1lbnRcIik7XG4gICAgICB9IGVsc2UgaWYgKGV4cHJlc3Npb25BbGxvd2VkKHN0cmVhbSwgc3RhdGUsIDEpKSB7XG4gICAgICAgIHJlYWRSZWdleHAoc3RyZWFtKTtcbiAgICAgICAgc3RyZWFtLm1hdGNoKC9eXFxiKChbZ2lteXVzXSkoPyFbZ2lteXVzXSpcXDIpKStcXGIvKTtcbiAgICAgICAgcmV0dXJuIHJldChcInJlZ2V4cFwiLCBcInN0cmluZy5zcGVjaWFsXCIpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgc3RyZWFtLmVhdChcIj1cIik7XG4gICAgICAgIHJldHVybiByZXQoXCJvcGVyYXRvclwiLCBcIm9wZXJhdG9yXCIsIHN0cmVhbS5jdXJyZW50KCkpO1xuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCJgXCIpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5RdWFzaTtcbiAgICAgIHJldHVybiB0b2tlblF1YXNpKHN0cmVhbSwgc3RhdGUpO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCIjXCIgJiYgc3RyZWFtLnBlZWsoKSA9PSBcIiFcIikge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuIHJldChcIm1ldGFcIiwgXCJtZXRhXCIpO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCIjXCIgJiYgc3RyZWFtLmVhdFdoaWxlKHdvcmRSRSkpIHtcbiAgICAgIHJldHVybiByZXQoXCJ2YXJpYWJsZVwiLCBcInByb3BlcnR5XCIpO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCI8XCIgJiYgc3RyZWFtLm1hdGNoKFwiIS0tXCIpIHx8IGNoID09IFwiLVwiICYmIHN0cmVhbS5tYXRjaChcIi0+XCIpICYmICEvXFxTLy50ZXN0KHN0cmVhbS5zdHJpbmcuc2xpY2UoMCwgc3RyZWFtLnN0YXJ0KSkpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiByZXQoXCJjb21tZW50XCIsIFwiY29tbWVudFwiKTtcbiAgICB9IGVsc2UgaWYgKGlzT3BlcmF0b3JDaGFyLnRlc3QoY2gpKSB7XG4gICAgICBpZiAoY2ggIT0gXCI+XCIgfHwgIXN0YXRlLmxleGljYWwgfHwgc3RhdGUubGV4aWNhbC50eXBlICE9IFwiPlwiKSB7XG4gICAgICAgIGlmIChzdHJlYW0uZWF0KFwiPVwiKSkge1xuICAgICAgICAgIGlmIChjaCA9PSBcIiFcIiB8fCBjaCA9PSBcIj1cIikgc3RyZWFtLmVhdChcIj1cIik7XG4gICAgICAgIH0gZWxzZSBpZiAoL1s8PiorXFwtfCY/XS8udGVzdChjaCkpIHtcbiAgICAgICAgICBzdHJlYW0uZWF0KGNoKTtcbiAgICAgICAgICBpZiAoY2ggPT0gXCI+XCIpIHN0cmVhbS5lYXQoY2gpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICBpZiAoY2ggPT0gXCI/XCIgJiYgc3RyZWFtLmVhdChcIi5cIikpIHJldHVybiByZXQoXCIuXCIpO1xuICAgICAgcmV0dXJuIHJldChcIm9wZXJhdG9yXCIsIFwib3BlcmF0b3JcIiwgc3RyZWFtLmN1cnJlbnQoKSk7XG4gICAgfSBlbHNlIGlmICh3b3JkUkUudGVzdChjaCkpIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSh3b3JkUkUpO1xuICAgICAgdmFyIHdvcmQgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgICAgaWYgKHN0YXRlLmxhc3RUeXBlICE9IFwiLlwiKSB7XG4gICAgICAgIGlmIChrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkKSkge1xuICAgICAgICAgIHZhciBrdyA9IGtleXdvcmRzW3dvcmRdO1xuICAgICAgICAgIHJldHVybiByZXQoa3cudHlwZSwga3cuc3R5bGUsIHdvcmQpO1xuICAgICAgICB9XG4gICAgICAgIGlmICh3b3JkID09IFwiYXN5bmNcIiAmJiBzdHJlYW0ubWF0Y2goL14oXFxzfFxcL1xcKihbXipdfFxcKig/IVxcLykpKj9cXCpcXC8pKltcXFtcXChcXHddLywgZmFsc2UpKSByZXR1cm4gcmV0KFwiYXN5bmNcIiwgXCJrZXl3b3JkXCIsIHdvcmQpO1xuICAgICAgfVxuICAgICAgcmV0dXJuIHJldChcInZhcmlhYmxlXCIsIFwidmFyaWFibGVcIiwgd29yZCk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gICAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgICBuZXh0O1xuICAgICAgaWYgKGpzb25sZE1vZGUgJiYgc3RyZWFtLnBlZWsoKSA9PSBcIkBcIiAmJiBzdHJlYW0ubWF0Y2goaXNKc29ubGRLZXl3b3JkKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgICAgcmV0dXJuIHJldChcImpzb25sZC1rZXl3b3JkXCIsIFwibWV0YVwiKTtcbiAgICAgIH1cbiAgICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIGJyZWFrO1xuICAgICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICAgIH1cbiAgICAgIGlmICghZXNjYXBlZCkgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICByZXR1cm4gcmV0KFwic3RyaW5nXCIsIFwic3RyaW5nXCIpO1xuICAgIH07XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICAgIGlmIChjaCA9PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICAgIH1cbiAgICByZXR1cm4gcmV0KFwiY29tbWVudFwiLCBcImNvbW1lbnRcIik7XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5RdWFzaShzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQ7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKCFlc2NhcGVkICYmIChuZXh0ID09IFwiYFwiIHx8IG5leHQgPT0gXCIkXCIgJiYgc3RyZWFtLmVhdChcIntcIikpKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICByZXR1cm4gcmV0KFwicXVhc2lcIiwgXCJzdHJpbmcuc3BlY2lhbFwiLCBzdHJlYW0uY3VycmVudCgpKTtcbiAgfVxuICB2YXIgYnJhY2tldHMgPSBcIihbe31dKVwiO1xuICAvLyBUaGlzIGlzIGEgY3J1ZGUgbG9va2FoZWFkIHRyaWNrIHRvIHRyeSBhbmQgbm90aWNlIHRoYXQgd2UncmVcbiAgLy8gcGFyc2luZyB0aGUgYXJndW1lbnQgcGF0dGVybnMgZm9yIGEgZmF0LWFycm93IGZ1bmN0aW9uIGJlZm9yZSB3ZVxuICAvLyBhY3R1YWxseSBoaXQgdGhlIGFycm93IHRva2VuLiBJdCBvbmx5IHdvcmtzIGlmIHRoZSBhcnJvdyBpcyBvblxuICAvLyB0aGUgc2FtZSBsaW5lIGFzIHRoZSBhcmd1bWVudHMgYW5kIHRoZXJlJ3Mgbm8gc3RyYW5nZSBub2lzZVxuICAvLyAoY29tbWVudHMpIGluIGJldHdlZW4uIEZhbGxiYWNrIGlzIHRvIG9ubHkgbm90aWNlIHdoZW4gd2UgaGl0IHRoZVxuICAvLyBhcnJvdywgYW5kIG5vdCBkZWNsYXJlIHRoZSBhcmd1bWVudHMgYXMgbG9jYWxzIGZvciB0aGUgYXJyb3dcbiAgLy8gYm9keS5cbiAgZnVuY3Rpb24gZmluZEZhdEFycm93KHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RhdGUuZmF0QXJyb3dBdCkgc3RhdGUuZmF0QXJyb3dBdCA9IG51bGw7XG4gICAgdmFyIGFycm93ID0gc3RyZWFtLnN0cmluZy5pbmRleE9mKFwiPT5cIiwgc3RyZWFtLnN0YXJ0KTtcbiAgICBpZiAoYXJyb3cgPCAwKSByZXR1cm47XG4gICAgaWYgKGlzVFMpIHtcbiAgICAgIC8vIFRyeSB0byBza2lwIFR5cGVTY3JpcHQgcmV0dXJuIHR5cGUgZGVjbGFyYXRpb25zIGFmdGVyIHRoZSBhcmd1bWVudHNcbiAgICAgIHZhciBtID0gLzpcXHMqKD86XFx3Kyg/OjxbXj5dKj58XFxbXFxdKT98XFx7W159XSpcXH0pXFxzKiQvLmV4ZWMoc3RyZWFtLnN0cmluZy5zbGljZShzdHJlYW0uc3RhcnQsIGFycm93KSk7XG4gICAgICBpZiAobSkgYXJyb3cgPSBtLmluZGV4O1xuICAgIH1cbiAgICB2YXIgZGVwdGggPSAwLFxuICAgICAgc2F3U29tZXRoaW5nID0gZmFsc2U7XG4gICAgZm9yICh2YXIgcG9zID0gYXJyb3cgLSAxOyBwb3MgPj0gMDsgLS1wb3MpIHtcbiAgICAgIHZhciBjaCA9IHN0cmVhbS5zdHJpbmcuY2hhckF0KHBvcyk7XG4gICAgICB2YXIgYnJhY2tldCA9IGJyYWNrZXRzLmluZGV4T2YoY2gpO1xuICAgICAgaWYgKGJyYWNrZXQgPj0gMCAmJiBicmFja2V0IDwgMykge1xuICAgICAgICBpZiAoIWRlcHRoKSB7XG4gICAgICAgICAgKytwb3M7XG4gICAgICAgICAgYnJlYWs7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKC0tZGVwdGggPT0gMCkge1xuICAgICAgICAgIGlmIChjaCA9PSBcIihcIikgc2F3U29tZXRoaW5nID0gdHJ1ZTtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIGlmIChicmFja2V0ID49IDMgJiYgYnJhY2tldCA8IDYpIHtcbiAgICAgICAgKytkZXB0aDtcbiAgICAgIH0gZWxzZSBpZiAod29yZFJFLnRlc3QoY2gpKSB7XG4gICAgICAgIHNhd1NvbWV0aGluZyA9IHRydWU7XG4gICAgICB9IGVsc2UgaWYgKC9bXCInXFwvYF0vLnRlc3QoY2gpKSB7XG4gICAgICAgIGZvciAoOzsgLS1wb3MpIHtcbiAgICAgICAgICBpZiAocG9zID09IDApIHJldHVybjtcbiAgICAgICAgICB2YXIgbmV4dCA9IHN0cmVhbS5zdHJpbmcuY2hhckF0KHBvcyAtIDEpO1xuICAgICAgICAgIGlmIChuZXh0ID09IGNoICYmIHN0cmVhbS5zdHJpbmcuY2hhckF0KHBvcyAtIDIpICE9IFwiXFxcXFwiKSB7XG4gICAgICAgICAgICBwb3MtLTtcbiAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgfSBlbHNlIGlmIChzYXdTb21ldGhpbmcgJiYgIWRlcHRoKSB7XG4gICAgICAgICsrcG9zO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICB9XG4gICAgaWYgKHNhd1NvbWV0aGluZyAmJiAhZGVwdGgpIHN0YXRlLmZhdEFycm93QXQgPSBwb3M7XG4gIH1cblxuICAvLyBQYXJzZXJcblxuICB2YXIgYXRvbWljVHlwZXMgPSB7XG4gICAgXCJhdG9tXCI6IHRydWUsXG4gICAgXCJudW1iZXJcIjogdHJ1ZSxcbiAgICBcInZhcmlhYmxlXCI6IHRydWUsXG4gICAgXCJzdHJpbmdcIjogdHJ1ZSxcbiAgICBcInJlZ2V4cFwiOiB0cnVlLFxuICAgIFwidGhpc1wiOiB0cnVlLFxuICAgIFwiaW1wb3J0XCI6IHRydWUsXG4gICAgXCJqc29ubGQta2V5d29yZFwiOiB0cnVlXG4gIH07XG4gIGZ1bmN0aW9uIEpTTGV4aWNhbChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBhbGlnbiwgcHJldiwgaW5mbykge1xuICAgIHRoaXMuaW5kZW50ZWQgPSBpbmRlbnRlZDtcbiAgICB0aGlzLmNvbHVtbiA9IGNvbHVtbjtcbiAgICB0aGlzLnR5cGUgPSB0eXBlO1xuICAgIHRoaXMucHJldiA9IHByZXY7XG4gICAgdGhpcy5pbmZvID0gaW5mbztcbiAgICBpZiAoYWxpZ24gIT0gbnVsbCkgdGhpcy5hbGlnbiA9IGFsaWduO1xuICB9XG4gIGZ1bmN0aW9uIGluU2NvcGUoc3RhdGUsIHZhcm5hbWUpIHtcbiAgICBmb3IgKHZhciB2ID0gc3RhdGUubG9jYWxWYXJzOyB2OyB2ID0gdi5uZXh0KSBpZiAodi5uYW1lID09IHZhcm5hbWUpIHJldHVybiB0cnVlO1xuICAgIGZvciAodmFyIGN4ID0gc3RhdGUuY29udGV4dDsgY3g7IGN4ID0gY3gucHJldikge1xuICAgICAgZm9yICh2YXIgdiA9IGN4LnZhcnM7IHY7IHYgPSB2Lm5leHQpIGlmICh2Lm5hbWUgPT0gdmFybmFtZSkgcmV0dXJuIHRydWU7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIHBhcnNlSlMoc3RhdGUsIHN0eWxlLCB0eXBlLCBjb250ZW50LCBzdHJlYW0pIHtcbiAgICB2YXIgY2MgPSBzdGF0ZS5jYztcbiAgICAvLyBDb21tdW5pY2F0ZSBvdXIgY29udGV4dCB0byB0aGUgY29tYmluYXRvcnMuXG4gICAgLy8gKExlc3Mgd2FzdGVmdWwgdGhhbiBjb25zaW5nIHVwIGEgaHVuZHJlZCBjbG9zdXJlcyBvbiBldmVyeSBjYWxsLilcbiAgICBjeC5zdGF0ZSA9IHN0YXRlO1xuICAgIGN4LnN0cmVhbSA9IHN0cmVhbTtcbiAgICBjeC5tYXJrZWQgPSBudWxsO1xuICAgIGN4LmNjID0gY2M7XG4gICAgY3guc3R5bGUgPSBzdHlsZTtcbiAgICBpZiAoIXN0YXRlLmxleGljYWwuaGFzT3duUHJvcGVydHkoXCJhbGlnblwiKSkgc3RhdGUubGV4aWNhbC5hbGlnbiA9IHRydWU7XG4gICAgd2hpbGUgKHRydWUpIHtcbiAgICAgIHZhciBjb21iaW5hdG9yID0gY2MubGVuZ3RoID8gY2MucG9wKCkgOiBqc29uTW9kZSA/IGV4cHJlc3Npb24gOiBzdGF0ZW1lbnQ7XG4gICAgICBpZiAoY29tYmluYXRvcih0eXBlLCBjb250ZW50KSkge1xuICAgICAgICB3aGlsZSAoY2MubGVuZ3RoICYmIGNjW2NjLmxlbmd0aCAtIDFdLmxleCkgY2MucG9wKCkoKTtcbiAgICAgICAgaWYgKGN4Lm1hcmtlZCkgcmV0dXJuIGN4Lm1hcmtlZDtcbiAgICAgICAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiICYmIGluU2NvcGUoc3RhdGUsIGNvbnRlbnQpKSByZXR1cm4gXCJ2YXJpYWJsZU5hbWUubG9jYWxcIjtcbiAgICAgICAgcmV0dXJuIHN0eWxlO1xuICAgICAgfVxuICAgIH1cbiAgfVxuXG4gIC8vIENvbWJpbmF0b3IgdXRpbHNcblxuICB2YXIgY3ggPSB7XG4gICAgc3RhdGU6IG51bGwsXG4gICAgY29sdW1uOiBudWxsLFxuICAgIG1hcmtlZDogbnVsbCxcbiAgICBjYzogbnVsbFxuICB9O1xuICBmdW5jdGlvbiBwYXNzKCkge1xuICAgIGZvciAodmFyIGkgPSBhcmd1bWVudHMubGVuZ3RoIC0gMTsgaSA+PSAwOyBpLS0pIGN4LmNjLnB1c2goYXJndW1lbnRzW2ldKTtcbiAgfVxuICBmdW5jdGlvbiBjb250KCkge1xuICAgIHBhc3MuYXBwbHkobnVsbCwgYXJndW1lbnRzKTtcbiAgICByZXR1cm4gdHJ1ZTtcbiAgfVxuICBmdW5jdGlvbiBpbkxpc3QobmFtZSwgbGlzdCkge1xuICAgIGZvciAodmFyIHYgPSBsaXN0OyB2OyB2ID0gdi5uZXh0KSBpZiAodi5uYW1lID09IG5hbWUpIHJldHVybiB0cnVlO1xuICAgIHJldHVybiBmYWxzZTtcbiAgfVxuICBmdW5jdGlvbiByZWdpc3Rlcih2YXJuYW1lKSB7XG4gICAgdmFyIHN0YXRlID0gY3guc3RhdGU7XG4gICAgY3gubWFya2VkID0gXCJkZWZcIjtcbiAgICBpZiAoc3RhdGUuY29udGV4dCkge1xuICAgICAgaWYgKHN0YXRlLmxleGljYWwuaW5mbyA9PSBcInZhclwiICYmIHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC5ibG9jaykge1xuICAgICAgICAvLyBGSVhNRSBmdW5jdGlvbiBkZWNscyBhcmUgYWxzbyBub3QgYmxvY2sgc2NvcGVkXG4gICAgICAgIHZhciBuZXdDb250ZXh0ID0gcmVnaXN0ZXJWYXJTY29wZWQodmFybmFtZSwgc3RhdGUuY29udGV4dCk7XG4gICAgICAgIGlmIChuZXdDb250ZXh0ICE9IG51bGwpIHtcbiAgICAgICAgICBzdGF0ZS5jb250ZXh0ID0gbmV3Q29udGV4dDtcbiAgICAgICAgICByZXR1cm47XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSBpZiAoIWluTGlzdCh2YXJuYW1lLCBzdGF0ZS5sb2NhbFZhcnMpKSB7XG4gICAgICAgIHN0YXRlLmxvY2FsVmFycyA9IG5ldyBWYXIodmFybmFtZSwgc3RhdGUubG9jYWxWYXJzKTtcbiAgICAgICAgcmV0dXJuO1xuICAgICAgfVxuICAgIH1cbiAgICAvLyBGYWxsIHRocm91Z2ggbWVhbnMgdGhpcyBpcyBnbG9iYWxcbiAgICBpZiAocGFyc2VyQ29uZmlnLmdsb2JhbFZhcnMgJiYgIWluTGlzdCh2YXJuYW1lLCBzdGF0ZS5nbG9iYWxWYXJzKSkgc3RhdGUuZ2xvYmFsVmFycyA9IG5ldyBWYXIodmFybmFtZSwgc3RhdGUuZ2xvYmFsVmFycyk7XG4gIH1cbiAgZnVuY3Rpb24gcmVnaXN0ZXJWYXJTY29wZWQodmFybmFtZSwgY29udGV4dCkge1xuICAgIGlmICghY29udGV4dCkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfSBlbHNlIGlmIChjb250ZXh0LmJsb2NrKSB7XG4gICAgICB2YXIgaW5uZXIgPSByZWdpc3RlclZhclNjb3BlZCh2YXJuYW1lLCBjb250ZXh0LnByZXYpO1xuICAgICAgaWYgKCFpbm5lcikgcmV0dXJuIG51bGw7XG4gICAgICBpZiAoaW5uZXIgPT0gY29udGV4dC5wcmV2KSByZXR1cm4gY29udGV4dDtcbiAgICAgIHJldHVybiBuZXcgQ29udGV4dChpbm5lciwgY29udGV4dC52YXJzLCB0cnVlKTtcbiAgICB9IGVsc2UgaWYgKGluTGlzdCh2YXJuYW1lLCBjb250ZXh0LnZhcnMpKSB7XG4gICAgICByZXR1cm4gY29udGV4dDtcbiAgICB9IGVsc2Uge1xuICAgICAgcmV0dXJuIG5ldyBDb250ZXh0KGNvbnRleHQucHJldiwgbmV3IFZhcih2YXJuYW1lLCBjb250ZXh0LnZhcnMpLCBmYWxzZSk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIGlzTW9kaWZpZXIobmFtZSkge1xuICAgIHJldHVybiBuYW1lID09IFwicHVibGljXCIgfHwgbmFtZSA9PSBcInByaXZhdGVcIiB8fCBuYW1lID09IFwicHJvdGVjdGVkXCIgfHwgbmFtZSA9PSBcImFic3RyYWN0XCIgfHwgbmFtZSA9PSBcInJlYWRvbmx5XCI7XG4gIH1cblxuICAvLyBDb21iaW5hdG9yc1xuXG4gIGZ1bmN0aW9uIENvbnRleHQocHJldiwgdmFycywgYmxvY2spIHtcbiAgICB0aGlzLnByZXYgPSBwcmV2O1xuICAgIHRoaXMudmFycyA9IHZhcnM7XG4gICAgdGhpcy5ibG9jayA9IGJsb2NrO1xuICB9XG4gIGZ1bmN0aW9uIFZhcihuYW1lLCBuZXh0KSB7XG4gICAgdGhpcy5uYW1lID0gbmFtZTtcbiAgICB0aGlzLm5leHQgPSBuZXh0O1xuICB9XG4gIHZhciBkZWZhdWx0VmFycyA9IG5ldyBWYXIoXCJ0aGlzXCIsIG5ldyBWYXIoXCJhcmd1bWVudHNcIiwgbnVsbCkpO1xuICBmdW5jdGlvbiBwdXNoY29udGV4dCgpIHtcbiAgICBjeC5zdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoY3guc3RhdGUuY29udGV4dCwgY3guc3RhdGUubG9jYWxWYXJzLCBmYWxzZSk7XG4gICAgY3guc3RhdGUubG9jYWxWYXJzID0gZGVmYXVsdFZhcnM7XG4gIH1cbiAgZnVuY3Rpb24gcHVzaGJsb2NrY29udGV4dCgpIHtcbiAgICBjeC5zdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoY3guc3RhdGUuY29udGV4dCwgY3guc3RhdGUubG9jYWxWYXJzLCB0cnVlKTtcbiAgICBjeC5zdGF0ZS5sb2NhbFZhcnMgPSBudWxsO1xuICB9XG4gIHB1c2hjb250ZXh0LmxleCA9IHB1c2hibG9ja2NvbnRleHQubGV4ID0gdHJ1ZTtcbiAgZnVuY3Rpb24gcG9wY29udGV4dCgpIHtcbiAgICBjeC5zdGF0ZS5sb2NhbFZhcnMgPSBjeC5zdGF0ZS5jb250ZXh0LnZhcnM7XG4gICAgY3guc3RhdGUuY29udGV4dCA9IGN4LnN0YXRlLmNvbnRleHQucHJldjtcbiAgfVxuICBwb3Bjb250ZXh0LmxleCA9IHRydWU7XG4gIGZ1bmN0aW9uIHB1c2hsZXgodHlwZSwgaW5mbykge1xuICAgIHZhciByZXN1bHQgPSBmdW5jdGlvbiAoKSB7XG4gICAgICB2YXIgc3RhdGUgPSBjeC5zdGF0ZSxcbiAgICAgICAgaW5kZW50ID0gc3RhdGUuaW5kZW50ZWQ7XG4gICAgICBpZiAoc3RhdGUubGV4aWNhbC50eXBlID09IFwic3RhdFwiKSBpbmRlbnQgPSBzdGF0ZS5sZXhpY2FsLmluZGVudGVkO2Vsc2UgZm9yICh2YXIgb3V0ZXIgPSBzdGF0ZS5sZXhpY2FsOyBvdXRlciAmJiBvdXRlci50eXBlID09IFwiKVwiICYmIG91dGVyLmFsaWduOyBvdXRlciA9IG91dGVyLnByZXYpIGluZGVudCA9IG91dGVyLmluZGVudGVkO1xuICAgICAgc3RhdGUubGV4aWNhbCA9IG5ldyBKU0xleGljYWwoaW5kZW50LCBjeC5zdHJlYW0uY29sdW1uKCksIHR5cGUsIG51bGwsIHN0YXRlLmxleGljYWwsIGluZm8pO1xuICAgIH07XG4gICAgcmVzdWx0LmxleCA9IHRydWU7XG4gICAgcmV0dXJuIHJlc3VsdDtcbiAgfVxuICBmdW5jdGlvbiBwb3BsZXgoKSB7XG4gICAgdmFyIHN0YXRlID0gY3guc3RhdGU7XG4gICAgaWYgKHN0YXRlLmxleGljYWwucHJldikge1xuICAgICAgaWYgKHN0YXRlLmxleGljYWwudHlwZSA9PSBcIilcIikgc3RhdGUuaW5kZW50ZWQgPSBzdGF0ZS5sZXhpY2FsLmluZGVudGVkO1xuICAgICAgc3RhdGUubGV4aWNhbCA9IHN0YXRlLmxleGljYWwucHJldjtcbiAgICB9XG4gIH1cbiAgcG9wbGV4LmxleCA9IHRydWU7XG4gIGZ1bmN0aW9uIGV4cGVjdCh3YW50ZWQpIHtcbiAgICBmdW5jdGlvbiBleHAodHlwZSkge1xuICAgICAgaWYgKHR5cGUgPT0gd2FudGVkKSByZXR1cm4gY29udCgpO2Vsc2UgaWYgKHdhbnRlZCA9PSBcIjtcIiB8fCB0eXBlID09IFwifVwiIHx8IHR5cGUgPT0gXCIpXCIgfHwgdHlwZSA9PSBcIl1cIikgcmV0dXJuIHBhc3MoKTtlbHNlIHJldHVybiBjb250KGV4cCk7XG4gICAgfVxuICAgIDtcbiAgICByZXR1cm4gZXhwO1xuICB9XG4gIGZ1bmN0aW9uIHN0YXRlbWVudCh0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh0eXBlID09IFwidmFyXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJ2YXJkZWZcIiwgdmFsdWUpLCB2YXJkZWYsIGV4cGVjdChcIjtcIiksIHBvcGxleCk7XG4gICAgaWYgKHR5cGUgPT0gXCJrZXl3b3JkIGFcIikgcmV0dXJuIGNvbnQocHVzaGxleChcImZvcm1cIiksIHBhcmVuRXhwciwgc3RhdGVtZW50LCBwb3BsZXgpO1xuICAgIGlmICh0eXBlID09IFwia2V5d29yZCBiXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJmb3JtXCIpLCBzdGF0ZW1lbnQsIHBvcGxleCk7XG4gICAgaWYgKHR5cGUgPT0gXCJrZXl3b3JkIGRcIikgcmV0dXJuIGN4LnN0cmVhbS5tYXRjaCgvXlxccyokLywgZmFsc2UpID8gY29udCgpIDogY29udChwdXNobGV4KFwic3RhdFwiKSwgbWF5YmVleHByZXNzaW9uLCBleHBlY3QoXCI7XCIpLCBwb3BsZXgpO1xuICAgIGlmICh0eXBlID09IFwiZGVidWdnZXJcIikgcmV0dXJuIGNvbnQoZXhwZWN0KFwiO1wiKSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ7XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJ9XCIpLCBwdXNoYmxvY2tjb250ZXh0LCBibG9jaywgcG9wbGV4LCBwb3Bjb250ZXh0KTtcbiAgICBpZiAodHlwZSA9PSBcIjtcIikgcmV0dXJuIGNvbnQoKTtcbiAgICBpZiAodHlwZSA9PSBcImlmXCIpIHtcbiAgICAgIGlmIChjeC5zdGF0ZS5sZXhpY2FsLmluZm8gPT0gXCJlbHNlXCIgJiYgY3guc3RhdGUuY2NbY3guc3RhdGUuY2MubGVuZ3RoIC0gMV0gPT0gcG9wbGV4KSBjeC5zdGF0ZS5jYy5wb3AoKSgpO1xuICAgICAgcmV0dXJuIGNvbnQocHVzaGxleChcImZvcm1cIiksIHBhcmVuRXhwciwgc3RhdGVtZW50LCBwb3BsZXgsIG1heWJlZWxzZSk7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwiZnVuY3Rpb25cIikgcmV0dXJuIGNvbnQoZnVuY3Rpb25kZWYpO1xuICAgIGlmICh0eXBlID09IFwiZm9yXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJmb3JtXCIpLCBwdXNoYmxvY2tjb250ZXh0LCBmb3JzcGVjLCBzdGF0ZW1lbnQsIHBvcGNvbnRleHQsIHBvcGxleCk7XG4gICAgaWYgKHR5cGUgPT0gXCJjbGFzc1wiIHx8IGlzVFMgJiYgdmFsdWUgPT0gXCJpbnRlcmZhY2VcIikge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udChwdXNobGV4KFwiZm9ybVwiLCB0eXBlID09IFwiY2xhc3NcIiA/IHR5cGUgOiB2YWx1ZSksIGNsYXNzTmFtZSwgcG9wbGV4KTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiKSB7XG4gICAgICBpZiAoaXNUUyAmJiB2YWx1ZSA9PSBcImRlY2xhcmVcIikge1xuICAgICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgICAgcmV0dXJuIGNvbnQoc3RhdGVtZW50KTtcbiAgICAgIH0gZWxzZSBpZiAoaXNUUyAmJiAodmFsdWUgPT0gXCJtb2R1bGVcIiB8fCB2YWx1ZSA9PSBcImVudW1cIiB8fCB2YWx1ZSA9PSBcInR5cGVcIikgJiYgY3guc3RyZWFtLm1hdGNoKC9eXFxzKlxcdy8sIGZhbHNlKSkge1xuICAgICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgICAgaWYgKHZhbHVlID09IFwiZW51bVwiKSByZXR1cm4gY29udChlbnVtZGVmKTtlbHNlIGlmICh2YWx1ZSA9PSBcInR5cGVcIikgcmV0dXJuIGNvbnQodHlwZW5hbWUsIGV4cGVjdChcIm9wZXJhdG9yXCIpLCB0eXBlZXhwciwgZXhwZWN0KFwiO1wiKSk7ZWxzZSByZXR1cm4gY29udChwdXNobGV4KFwiZm9ybVwiKSwgcGF0dGVybiwgZXhwZWN0KFwie1wiKSwgcHVzaGxleChcIn1cIiksIGJsb2NrLCBwb3BsZXgsIHBvcGxleCk7XG4gICAgICB9IGVsc2UgaWYgKGlzVFMgJiYgdmFsdWUgPT0gXCJuYW1lc3BhY2VcIikge1xuICAgICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgICAgcmV0dXJuIGNvbnQocHVzaGxleChcImZvcm1cIiksIGV4cHJlc3Npb24sIHN0YXRlbWVudCwgcG9wbGV4KTtcbiAgICAgIH0gZWxzZSBpZiAoaXNUUyAmJiB2YWx1ZSA9PSBcImFic3RyYWN0XCIpIHtcbiAgICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICAgIHJldHVybiBjb250KHN0YXRlbWVudCk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gY29udChwdXNobGV4KFwic3RhdFwiKSwgbWF5YmVsYWJlbCk7XG4gICAgICB9XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwic3dpdGNoXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJmb3JtXCIpLCBwYXJlbkV4cHIsIGV4cGVjdChcIntcIiksIHB1c2hsZXgoXCJ9XCIsIFwic3dpdGNoXCIpLCBwdXNoYmxvY2tjb250ZXh0LCBibG9jaywgcG9wbGV4LCBwb3BsZXgsIHBvcGNvbnRleHQpO1xuICAgIGlmICh0eXBlID09IFwiY2FzZVwiKSByZXR1cm4gY29udChleHByZXNzaW9uLCBleHBlY3QoXCI6XCIpKTtcbiAgICBpZiAodHlwZSA9PSBcImRlZmF1bHRcIikgcmV0dXJuIGNvbnQoZXhwZWN0KFwiOlwiKSk7XG4gICAgaWYgKHR5cGUgPT0gXCJjYXRjaFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiZm9ybVwiKSwgcHVzaGNvbnRleHQsIG1heWJlQ2F0Y2hCaW5kaW5nLCBzdGF0ZW1lbnQsIHBvcGxleCwgcG9wY29udGV4dCk7XG4gICAgaWYgKHR5cGUgPT0gXCJleHBvcnRcIikgcmV0dXJuIGNvbnQocHVzaGxleChcInN0YXRcIiksIGFmdGVyRXhwb3J0LCBwb3BsZXgpO1xuICAgIGlmICh0eXBlID09IFwiaW1wb3J0XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJzdGF0XCIpLCBhZnRlckltcG9ydCwgcG9wbGV4KTtcbiAgICBpZiAodHlwZSA9PSBcImFzeW5jXCIpIHJldHVybiBjb250KHN0YXRlbWVudCk7XG4gICAgaWYgKHZhbHVlID09IFwiQFwiKSByZXR1cm4gY29udChleHByZXNzaW9uLCBzdGF0ZW1lbnQpO1xuICAgIHJldHVybiBwYXNzKHB1c2hsZXgoXCJzdGF0XCIpLCBleHByZXNzaW9uLCBleHBlY3QoXCI7XCIpLCBwb3BsZXgpO1xuICB9XG4gIGZ1bmN0aW9uIG1heWJlQ2F0Y2hCaW5kaW5nKHR5cGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIihcIikgcmV0dXJuIGNvbnQoZnVuYXJnLCBleHBlY3QoXCIpXCIpKTtcbiAgfVxuICBmdW5jdGlvbiBleHByZXNzaW9uKHR5cGUsIHZhbHVlKSB7XG4gICAgcmV0dXJuIGV4cHJlc3Npb25Jbm5lcih0eXBlLCB2YWx1ZSwgZmFsc2UpO1xuICB9XG4gIGZ1bmN0aW9uIGV4cHJlc3Npb25Ob0NvbW1hKHR5cGUsIHZhbHVlKSB7XG4gICAgcmV0dXJuIGV4cHJlc3Npb25Jbm5lcih0eXBlLCB2YWx1ZSwgdHJ1ZSk7XG4gIH1cbiAgZnVuY3Rpb24gcGFyZW5FeHByKHR5cGUpIHtcbiAgICBpZiAodHlwZSAhPSBcIihcIikgcmV0dXJuIHBhc3MoKTtcbiAgICByZXR1cm4gY29udChwdXNobGV4KFwiKVwiKSwgbWF5YmVleHByZXNzaW9uLCBleHBlY3QoXCIpXCIpLCBwb3BsZXgpO1xuICB9XG4gIGZ1bmN0aW9uIGV4cHJlc3Npb25Jbm5lcih0eXBlLCB2YWx1ZSwgbm9Db21tYSkge1xuICAgIGlmIChjeC5zdGF0ZS5mYXRBcnJvd0F0ID09IGN4LnN0cmVhbS5zdGFydCkge1xuICAgICAgdmFyIGJvZHkgPSBub0NvbW1hID8gYXJyb3dCb2R5Tm9Db21tYSA6IGFycm93Qm9keTtcbiAgICAgIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gY29udChwdXNoY29udGV4dCwgcHVzaGxleChcIilcIiksIGNvbW1hc2VwKGZ1bmFyZywgXCIpXCIpLCBwb3BsZXgsIGV4cGVjdChcIj0+XCIpLCBib2R5LCBwb3Bjb250ZXh0KTtlbHNlIGlmICh0eXBlID09IFwidmFyaWFibGVcIikgcmV0dXJuIHBhc3MocHVzaGNvbnRleHQsIHBhdHRlcm4sIGV4cGVjdChcIj0+XCIpLCBib2R5LCBwb3Bjb250ZXh0KTtcbiAgICB9XG4gICAgdmFyIG1heWJlb3AgPSBub0NvbW1hID8gbWF5YmVvcGVyYXRvck5vQ29tbWEgOiBtYXliZW9wZXJhdG9yQ29tbWE7XG4gICAgaWYgKGF0b21pY1R5cGVzLmhhc093blByb3BlcnR5KHR5cGUpKSByZXR1cm4gY29udChtYXliZW9wKTtcbiAgICBpZiAodHlwZSA9PSBcImZ1bmN0aW9uXCIpIHJldHVybiBjb250KGZ1bmN0aW9uZGVmLCBtYXliZW9wKTtcbiAgICBpZiAodHlwZSA9PSBcImNsYXNzXCIgfHwgaXNUUyAmJiB2YWx1ZSA9PSBcImludGVyZmFjZVwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KHB1c2hsZXgoXCJmb3JtXCIpLCBjbGFzc0V4cHJlc3Npb24sIHBvcGxleCk7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwia2V5d29yZCBjXCIgfHwgdHlwZSA9PSBcImFzeW5jXCIpIHJldHVybiBjb250KG5vQ29tbWEgPyBleHByZXNzaW9uTm9Db21tYSA6IGV4cHJlc3Npb24pO1xuICAgIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiKVwiKSwgbWF5YmVleHByZXNzaW9uLCBleHBlY3QoXCIpXCIpLCBwb3BsZXgsIG1heWJlb3ApO1xuICAgIGlmICh0eXBlID09IFwib3BlcmF0b3JcIiB8fCB0eXBlID09IFwic3ByZWFkXCIpIHJldHVybiBjb250KG5vQ29tbWEgPyBleHByZXNzaW9uTm9Db21tYSA6IGV4cHJlc3Npb24pO1xuICAgIGlmICh0eXBlID09IFwiW1wiKSByZXR1cm4gY29udChwdXNobGV4KFwiXVwiKSwgYXJyYXlMaXRlcmFsLCBwb3BsZXgsIG1heWJlb3ApO1xuICAgIGlmICh0eXBlID09IFwie1wiKSByZXR1cm4gY29udENvbW1hc2VwKG9ianByb3AsIFwifVwiLCBudWxsLCBtYXliZW9wKTtcbiAgICBpZiAodHlwZSA9PSBcInF1YXNpXCIpIHJldHVybiBwYXNzKHF1YXNpLCBtYXliZW9wKTtcbiAgICBpZiAodHlwZSA9PSBcIm5ld1wiKSByZXR1cm4gY29udChtYXliZVRhcmdldChub0NvbW1hKSk7XG4gICAgcmV0dXJuIGNvbnQoKTtcbiAgfVxuICBmdW5jdGlvbiBtYXliZWV4cHJlc3Npb24odHlwZSkge1xuICAgIGlmICh0eXBlLm1hdGNoKC9bO1xcfVxcKVxcXSxdLykpIHJldHVybiBwYXNzKCk7XG4gICAgcmV0dXJuIHBhc3MoZXhwcmVzc2lvbik7XG4gIH1cbiAgZnVuY3Rpb24gbWF5YmVvcGVyYXRvckNvbW1hKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCIsXCIpIHJldHVybiBjb250KG1heWJlZXhwcmVzc2lvbik7XG4gICAgcmV0dXJuIG1heWJlb3BlcmF0b3JOb0NvbW1hKHR5cGUsIHZhbHVlLCBmYWxzZSk7XG4gIH1cbiAgZnVuY3Rpb24gbWF5YmVvcGVyYXRvck5vQ29tbWEodHlwZSwgdmFsdWUsIG5vQ29tbWEpIHtcbiAgICB2YXIgbWUgPSBub0NvbW1hID09IGZhbHNlID8gbWF5YmVvcGVyYXRvckNvbW1hIDogbWF5YmVvcGVyYXRvck5vQ29tbWE7XG4gICAgdmFyIGV4cHIgPSBub0NvbW1hID09IGZhbHNlID8gZXhwcmVzc2lvbiA6IGV4cHJlc3Npb25Ob0NvbW1hO1xuICAgIGlmICh0eXBlID09IFwiPT5cIikgcmV0dXJuIGNvbnQocHVzaGNvbnRleHQsIG5vQ29tbWEgPyBhcnJvd0JvZHlOb0NvbW1hIDogYXJyb3dCb2R5LCBwb3Bjb250ZXh0KTtcbiAgICBpZiAodHlwZSA9PSBcIm9wZXJhdG9yXCIpIHtcbiAgICAgIGlmICgvXFwrXFwrfC0tLy50ZXN0KHZhbHVlKSB8fCBpc1RTICYmIHZhbHVlID09IFwiIVwiKSByZXR1cm4gY29udChtZSk7XG4gICAgICBpZiAoaXNUUyAmJiB2YWx1ZSA9PSBcIjxcIiAmJiBjeC5zdHJlYW0ubWF0Y2goL14oW148Pl18PFtePD5dKj4pKj5cXHMqXFwoLywgZmFsc2UpKSByZXR1cm4gY29udChwdXNobGV4KFwiPlwiKSwgY29tbWFzZXAodHlwZWV4cHIsIFwiPlwiKSwgcG9wbGV4LCBtZSk7XG4gICAgICBpZiAodmFsdWUgPT0gXCI/XCIpIHJldHVybiBjb250KGV4cHJlc3Npb24sIGV4cGVjdChcIjpcIiksIGV4cHIpO1xuICAgICAgcmV0dXJuIGNvbnQoZXhwcik7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwicXVhc2lcIikge1xuICAgICAgcmV0dXJuIHBhc3MocXVhc2ksIG1lKTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCI7XCIpIHJldHVybjtcbiAgICBpZiAodHlwZSA9PSBcIihcIikgcmV0dXJuIGNvbnRDb21tYXNlcChleHByZXNzaW9uTm9Db21tYSwgXCIpXCIsIFwiY2FsbFwiLCBtZSk7XG4gICAgaWYgKHR5cGUgPT0gXCIuXCIpIHJldHVybiBjb250KHByb3BlcnR5LCBtZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJbXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJdXCIpLCBtYXliZWV4cHJlc3Npb24sIGV4cGVjdChcIl1cIiksIHBvcGxleCwgbWUpO1xuICAgIGlmIChpc1RTICYmIHZhbHVlID09IFwiYXNcIikge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udCh0eXBlZXhwciwgbWUpO1xuICAgIH1cbiAgICBpZiAodHlwZSA9PSBcInJlZ2V4cFwiKSB7XG4gICAgICBjeC5zdGF0ZS5sYXN0VHlwZSA9IGN4Lm1hcmtlZCA9IFwib3BlcmF0b3JcIjtcbiAgICAgIGN4LnN0cmVhbS5iYWNrVXAoY3guc3RyZWFtLnBvcyAtIGN4LnN0cmVhbS5zdGFydCAtIDEpO1xuICAgICAgcmV0dXJuIGNvbnQoZXhwcik7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIHF1YXNpKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHR5cGUgIT0gXCJxdWFzaVwiKSByZXR1cm4gcGFzcygpO1xuICAgIGlmICh2YWx1ZS5zbGljZSh2YWx1ZS5sZW5ndGggLSAyKSAhPSBcIiR7XCIpIHJldHVybiBjb250KHF1YXNpKTtcbiAgICByZXR1cm4gY29udChtYXliZWV4cHJlc3Npb24sIGNvbnRpbnVlUXVhc2kpO1xuICB9XG4gIGZ1bmN0aW9uIGNvbnRpbnVlUXVhc2kodHlwZSkge1xuICAgIGlmICh0eXBlID09IFwifVwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcInN0cmluZy5zcGVjaWFsXCI7XG4gICAgICBjeC5zdGF0ZS50b2tlbml6ZSA9IHRva2VuUXVhc2k7XG4gICAgICByZXR1cm4gY29udChxdWFzaSk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIGFycm93Qm9keSh0eXBlKSB7XG4gICAgZmluZEZhdEFycm93KGN4LnN0cmVhbSwgY3guc3RhdGUpO1xuICAgIHJldHVybiBwYXNzKHR5cGUgPT0gXCJ7XCIgPyBzdGF0ZW1lbnQgOiBleHByZXNzaW9uKTtcbiAgfVxuICBmdW5jdGlvbiBhcnJvd0JvZHlOb0NvbW1hKHR5cGUpIHtcbiAgICBmaW5kRmF0QXJyb3coY3guc3RyZWFtLCBjeC5zdGF0ZSk7XG4gICAgcmV0dXJuIHBhc3ModHlwZSA9PSBcIntcIiA/IHN0YXRlbWVudCA6IGV4cHJlc3Npb25Ob0NvbW1hKTtcbiAgfVxuICBmdW5jdGlvbiBtYXliZVRhcmdldChub0NvbW1hKSB7XG4gICAgcmV0dXJuIGZ1bmN0aW9uICh0eXBlKSB7XG4gICAgICBpZiAodHlwZSA9PSBcIi5cIikgcmV0dXJuIGNvbnQobm9Db21tYSA/IHRhcmdldE5vQ29tbWEgOiB0YXJnZXQpO2Vsc2UgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiICYmIGlzVFMpIHJldHVybiBjb250KG1heWJlVHlwZUFyZ3MsIG5vQ29tbWEgPyBtYXliZW9wZXJhdG9yTm9Db21tYSA6IG1heWJlb3BlcmF0b3JDb21tYSk7ZWxzZSByZXR1cm4gcGFzcyhub0NvbW1hID8gZXhwcmVzc2lvbk5vQ29tbWEgOiBleHByZXNzaW9uKTtcbiAgICB9O1xuICB9XG4gIGZ1bmN0aW9uIHRhcmdldChfLCB2YWx1ZSkge1xuICAgIGlmICh2YWx1ZSA9PSBcInRhcmdldFwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KG1heWJlb3BlcmF0b3JDb21tYSk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIHRhcmdldE5vQ29tbWEoXywgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCJ0YXJnZXRcIikge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udChtYXliZW9wZXJhdG9yTm9Db21tYSk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIG1heWJlbGFiZWwodHlwZSkge1xuICAgIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gY29udChwb3BsZXgsIHN0YXRlbWVudCk7XG4gICAgcmV0dXJuIHBhc3MobWF5YmVvcGVyYXRvckNvbW1hLCBleHBlY3QoXCI7XCIpLCBwb3BsZXgpO1xuICB9XG4gIGZ1bmN0aW9uIHByb3BlcnR5KHR5cGUpIHtcbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwicHJvcGVydHlcIjtcbiAgICAgIHJldHVybiBjb250KCk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIG9ianByb3AodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodHlwZSA9PSBcImFzeW5jXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwicHJvcGVydHlcIjtcbiAgICAgIHJldHVybiBjb250KG9ianByb3ApO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIgfHwgY3guc3R5bGUgPT0gXCJrZXl3b3JkXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwicHJvcGVydHlcIjtcbiAgICAgIGlmICh2YWx1ZSA9PSBcImdldFwiIHx8IHZhbHVlID09IFwic2V0XCIpIHJldHVybiBjb250KGdldHRlclNldHRlcik7XG4gICAgICB2YXIgbTsgLy8gV29yayBhcm91bmQgZmF0LWFycm93LWRldGVjdGlvbiBjb21wbGljYXRpb24gZm9yIGRldGVjdGluZyB0eXBlc2NyaXB0IHR5cGVkIGFycm93IHBhcmFtc1xuICAgICAgaWYgKGlzVFMgJiYgY3guc3RhdGUuZmF0QXJyb3dBdCA9PSBjeC5zdHJlYW0uc3RhcnQgJiYgKG0gPSBjeC5zdHJlYW0ubWF0Y2goL15cXHMqOlxccyovLCBmYWxzZSkpKSBjeC5zdGF0ZS5mYXRBcnJvd0F0ID0gY3guc3RyZWFtLnBvcyArIG1bMF0ubGVuZ3RoO1xuICAgICAgcmV0dXJuIGNvbnQoYWZ0ZXJwcm9wKTtcbiAgICB9IGVsc2UgaWYgKHR5cGUgPT0gXCJudW1iZXJcIiB8fCB0eXBlID09IFwic3RyaW5nXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IGpzb25sZE1vZGUgPyBcInByb3BlcnR5XCIgOiBjeC5zdHlsZSArIFwiIHByb3BlcnR5XCI7XG4gICAgICByZXR1cm4gY29udChhZnRlcnByb3ApO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcImpzb25sZC1rZXl3b3JkXCIpIHtcbiAgICAgIHJldHVybiBjb250KGFmdGVycHJvcCk7XG4gICAgfSBlbHNlIGlmIChpc1RTICYmIGlzTW9kaWZpZXIodmFsdWUpKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KG9ianByb3ApO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcIltcIikge1xuICAgICAgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbiwgbWF5YmV0eXBlLCBleHBlY3QoXCJdXCIpLCBhZnRlcnByb3ApO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcInNwcmVhZFwiKSB7XG4gICAgICByZXR1cm4gY29udChleHByZXNzaW9uTm9Db21tYSwgYWZ0ZXJwcm9wKTtcbiAgICB9IGVsc2UgaWYgKHZhbHVlID09IFwiKlwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KG9ianByb3ApO1xuICAgIH0gZWxzZSBpZiAodHlwZSA9PSBcIjpcIikge1xuICAgICAgcmV0dXJuIHBhc3MoYWZ0ZXJwcm9wKTtcbiAgICB9XG4gIH1cbiAgZnVuY3Rpb24gZ2V0dGVyU2V0dGVyKHR5cGUpIHtcbiAgICBpZiAodHlwZSAhPSBcInZhcmlhYmxlXCIpIHJldHVybiBwYXNzKGFmdGVycHJvcCk7XG4gICAgY3gubWFya2VkID0gXCJwcm9wZXJ0eVwiO1xuICAgIHJldHVybiBjb250KGZ1bmN0aW9uZGVmKTtcbiAgfVxuICBmdW5jdGlvbiBhZnRlcnByb3AodHlwZSkge1xuICAgIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gY29udChleHByZXNzaW9uTm9Db21tYSk7XG4gICAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBwYXNzKGZ1bmN0aW9uZGVmKTtcbiAgfVxuICBmdW5jdGlvbiBjb21tYXNlcCh3aGF0LCBlbmQsIHNlcCkge1xuICAgIGZ1bmN0aW9uIHByb2NlZWQodHlwZSwgdmFsdWUpIHtcbiAgICAgIGlmIChzZXAgPyBzZXAuaW5kZXhPZih0eXBlKSA+IC0xIDogdHlwZSA9PSBcIixcIikge1xuICAgICAgICB2YXIgbGV4ID0gY3guc3RhdGUubGV4aWNhbDtcbiAgICAgICAgaWYgKGxleC5pbmZvID09IFwiY2FsbFwiKSBsZXgucG9zID0gKGxleC5wb3MgfHwgMCkgKyAxO1xuICAgICAgICByZXR1cm4gY29udChmdW5jdGlvbiAodHlwZSwgdmFsdWUpIHtcbiAgICAgICAgICBpZiAodHlwZSA9PSBlbmQgfHwgdmFsdWUgPT0gZW5kKSByZXR1cm4gcGFzcygpO1xuICAgICAgICAgIHJldHVybiBwYXNzKHdoYXQpO1xuICAgICAgICB9LCBwcm9jZWVkKTtcbiAgICAgIH1cbiAgICAgIGlmICh0eXBlID09IGVuZCB8fCB2YWx1ZSA9PSBlbmQpIHJldHVybiBjb250KCk7XG4gICAgICBpZiAoc2VwICYmIHNlcC5pbmRleE9mKFwiO1wiKSA+IC0xKSByZXR1cm4gcGFzcyh3aGF0KTtcbiAgICAgIHJldHVybiBjb250KGV4cGVjdChlbmQpKTtcbiAgICB9XG4gICAgcmV0dXJuIGZ1bmN0aW9uICh0eXBlLCB2YWx1ZSkge1xuICAgICAgaWYgKHR5cGUgPT0gZW5kIHx8IHZhbHVlID09IGVuZCkgcmV0dXJuIGNvbnQoKTtcbiAgICAgIHJldHVybiBwYXNzKHdoYXQsIHByb2NlZWQpO1xuICAgIH07XG4gIH1cbiAgZnVuY3Rpb24gY29udENvbW1hc2VwKHdoYXQsIGVuZCwgaW5mbykge1xuICAgIGZvciAodmFyIGkgPSAzOyBpIDwgYXJndW1lbnRzLmxlbmd0aDsgaSsrKSBjeC5jYy5wdXNoKGFyZ3VtZW50c1tpXSk7XG4gICAgcmV0dXJuIGNvbnQocHVzaGxleChlbmQsIGluZm8pLCBjb21tYXNlcCh3aGF0LCBlbmQpLCBwb3BsZXgpO1xuICB9XG4gIGZ1bmN0aW9uIGJsb2NrKHR5cGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIn1cIikgcmV0dXJuIGNvbnQoKTtcbiAgICByZXR1cm4gcGFzcyhzdGF0ZW1lbnQsIGJsb2NrKTtcbiAgfVxuICBmdW5jdGlvbiBtYXliZXR5cGUodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAoaXNUUykge1xuICAgICAgaWYgKHR5cGUgPT0gXCI6XCIpIHJldHVybiBjb250KHR5cGVleHByKTtcbiAgICAgIGlmICh2YWx1ZSA9PSBcIj9cIikgcmV0dXJuIGNvbnQobWF5YmV0eXBlKTtcbiAgICB9XG4gIH1cbiAgZnVuY3Rpb24gbWF5YmV0eXBlT3JJbih0eXBlLCB2YWx1ZSkge1xuICAgIGlmIChpc1RTICYmICh0eXBlID09IFwiOlwiIHx8IHZhbHVlID09IFwiaW5cIikpIHJldHVybiBjb250KHR5cGVleHByKTtcbiAgfVxuICBmdW5jdGlvbiBtYXliZXJldHR5cGUodHlwZSkge1xuICAgIGlmIChpc1RTICYmIHR5cGUgPT0gXCI6XCIpIHtcbiAgICAgIGlmIChjeC5zdHJlYW0ubWF0Y2goL15cXHMqXFx3K1xccytpc1xcYi8sIGZhbHNlKSkgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbiwgaXNLVywgdHlwZWV4cHIpO2Vsc2UgcmV0dXJuIGNvbnQodHlwZWV4cHIpO1xuICAgIH1cbiAgfVxuICBmdW5jdGlvbiBpc0tXKF8sIHZhbHVlKSB7XG4gICAgaWYgKHZhbHVlID09IFwiaXNcIikge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udCgpO1xuICAgIH1cbiAgfVxuICBmdW5jdGlvbiB0eXBlZXhwcih0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh2YWx1ZSA9PSBcImtleW9mXCIgfHwgdmFsdWUgPT0gXCJ0eXBlb2ZcIiB8fCB2YWx1ZSA9PSBcImluZmVyXCIgfHwgdmFsdWUgPT0gXCJyZWFkb25seVwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KHZhbHVlID09IFwidHlwZW9mXCIgPyBleHByZXNzaW9uTm9Db21tYSA6IHR5cGVleHByKTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiIHx8IHZhbHVlID09IFwidm9pZFwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcInR5cGVcIjtcbiAgICAgIHJldHVybiBjb250KGFmdGVyVHlwZSk7XG4gICAgfVxuICAgIGlmICh2YWx1ZSA9PSBcInxcIiB8fCB2YWx1ZSA9PSBcIiZcIikgcmV0dXJuIGNvbnQodHlwZWV4cHIpO1xuICAgIGlmICh0eXBlID09IFwic3RyaW5nXCIgfHwgdHlwZSA9PSBcIm51bWJlclwiIHx8IHR5cGUgPT0gXCJhdG9tXCIpIHJldHVybiBjb250KGFmdGVyVHlwZSk7XG4gICAgaWYgKHR5cGUgPT0gXCJbXCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJdXCIpLCBjb21tYXNlcCh0eXBlZXhwciwgXCJdXCIsIFwiLFwiKSwgcG9wbGV4LCBhZnRlclR5cGUpO1xuICAgIGlmICh0eXBlID09IFwie1wiKSByZXR1cm4gY29udChwdXNobGV4KFwifVwiKSwgdHlwZXByb3BzLCBwb3BsZXgsIGFmdGVyVHlwZSk7XG4gICAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBjb250KGNvbW1hc2VwKHR5cGVhcmcsIFwiKVwiKSwgbWF5YmVSZXR1cm5UeXBlLCBhZnRlclR5cGUpO1xuICAgIGlmICh0eXBlID09IFwiPFwiKSByZXR1cm4gY29udChjb21tYXNlcCh0eXBlZXhwciwgXCI+XCIpLCB0eXBlZXhwcik7XG4gICAgaWYgKHR5cGUgPT0gXCJxdWFzaVwiKSByZXR1cm4gcGFzcyhxdWFzaVR5cGUsIGFmdGVyVHlwZSk7XG4gIH1cbiAgZnVuY3Rpb24gbWF5YmVSZXR1cm5UeXBlKHR5cGUpIHtcbiAgICBpZiAodHlwZSA9PSBcIj0+XCIpIHJldHVybiBjb250KHR5cGVleHByKTtcbiAgfVxuICBmdW5jdGlvbiB0eXBlcHJvcHModHlwZSkge1xuICAgIGlmICh0eXBlLm1hdGNoKC9bXFx9XFwpXFxdXS8pKSByZXR1cm4gY29udCgpO1xuICAgIGlmICh0eXBlID09IFwiLFwiIHx8IHR5cGUgPT0gXCI7XCIpIHJldHVybiBjb250KHR5cGVwcm9wcyk7XG4gICAgcmV0dXJuIHBhc3ModHlwZXByb3AsIHR5cGVwcm9wcyk7XG4gIH1cbiAgZnVuY3Rpb24gdHlwZXByb3AodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIgfHwgY3guc3R5bGUgPT0gXCJrZXl3b3JkXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwicHJvcGVydHlcIjtcbiAgICAgIHJldHVybiBjb250KHR5cGVwcm9wKTtcbiAgICB9IGVsc2UgaWYgKHZhbHVlID09IFwiP1wiIHx8IHR5cGUgPT0gXCJudW1iZXJcIiB8fCB0eXBlID09IFwic3RyaW5nXCIpIHtcbiAgICAgIHJldHVybiBjb250KHR5cGVwcm9wKTtcbiAgICB9IGVsc2UgaWYgKHR5cGUgPT0gXCI6XCIpIHtcbiAgICAgIHJldHVybiBjb250KHR5cGVleHByKTtcbiAgICB9IGVsc2UgaWYgKHR5cGUgPT0gXCJbXCIpIHtcbiAgICAgIHJldHVybiBjb250KGV4cGVjdChcInZhcmlhYmxlXCIpLCBtYXliZXR5cGVPckluLCBleHBlY3QoXCJdXCIpLCB0eXBlcHJvcCk7XG4gICAgfSBlbHNlIGlmICh0eXBlID09IFwiKFwiKSB7XG4gICAgICByZXR1cm4gcGFzcyhmdW5jdGlvbmRlY2wsIHR5cGVwcm9wKTtcbiAgICB9IGVsc2UgaWYgKCF0eXBlLm1hdGNoKC9bO1xcfVxcKVxcXSxdLykpIHtcbiAgICAgIHJldHVybiBjb250KCk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIHF1YXNpVHlwZSh0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh0eXBlICE9IFwicXVhc2lcIikgcmV0dXJuIHBhc3MoKTtcbiAgICBpZiAodmFsdWUuc2xpY2UodmFsdWUubGVuZ3RoIC0gMikgIT0gXCIke1wiKSByZXR1cm4gY29udChxdWFzaVR5cGUpO1xuICAgIHJldHVybiBjb250KHR5cGVleHByLCBjb250aW51ZVF1YXNpVHlwZSk7XG4gIH1cbiAgZnVuY3Rpb24gY29udGludWVRdWFzaVR5cGUodHlwZSkge1xuICAgIGlmICh0eXBlID09IFwifVwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcInN0cmluZy5zcGVjaWFsXCI7XG4gICAgICBjeC5zdGF0ZS50b2tlbml6ZSA9IHRva2VuUXVhc2k7XG4gICAgICByZXR1cm4gY29udChxdWFzaVR5cGUpO1xuICAgIH1cbiAgfVxuICBmdW5jdGlvbiB0eXBlYXJnKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJ2YXJpYWJsZVwiICYmIGN4LnN0cmVhbS5tYXRjaCgvXlxccypbPzpdLywgZmFsc2UpIHx8IHZhbHVlID09IFwiP1wiKSByZXR1cm4gY29udCh0eXBlYXJnKTtcbiAgICBpZiAodHlwZSA9PSBcIjpcIikgcmV0dXJuIGNvbnQodHlwZWV4cHIpO1xuICAgIGlmICh0eXBlID09IFwic3ByZWFkXCIpIHJldHVybiBjb250KHR5cGVhcmcpO1xuICAgIHJldHVybiBwYXNzKHR5cGVleHByKTtcbiAgfVxuICBmdW5jdGlvbiBhZnRlclR5cGUodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCI8XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCI+XCIpLCBjb21tYXNlcCh0eXBlZXhwciwgXCI+XCIpLCBwb3BsZXgsIGFmdGVyVHlwZSk7XG4gICAgaWYgKHZhbHVlID09IFwifFwiIHx8IHR5cGUgPT0gXCIuXCIgfHwgdmFsdWUgPT0gXCImXCIpIHJldHVybiBjb250KHR5cGVleHByKTtcbiAgICBpZiAodHlwZSA9PSBcIltcIikgcmV0dXJuIGNvbnQodHlwZWV4cHIsIGV4cGVjdChcIl1cIiksIGFmdGVyVHlwZSk7XG4gICAgaWYgKHZhbHVlID09IFwiZXh0ZW5kc1wiIHx8IHZhbHVlID09IFwiaW1wbGVtZW50c1wiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KHR5cGVleHByKTtcbiAgICB9XG4gICAgaWYgKHZhbHVlID09IFwiP1wiKSByZXR1cm4gY29udCh0eXBlZXhwciwgZXhwZWN0KFwiOlwiKSwgdHlwZWV4cHIpO1xuICB9XG4gIGZ1bmN0aW9uIG1heWJlVHlwZUFyZ3MoXywgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCI8XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCI+XCIpLCBjb21tYXNlcCh0eXBlZXhwciwgXCI+XCIpLCBwb3BsZXgsIGFmdGVyVHlwZSk7XG4gIH1cbiAgZnVuY3Rpb24gdHlwZXBhcmFtKCkge1xuICAgIHJldHVybiBwYXNzKHR5cGVleHByLCBtYXliZVR5cGVEZWZhdWx0KTtcbiAgfVxuICBmdW5jdGlvbiBtYXliZVR5cGVEZWZhdWx0KF8sIHZhbHVlKSB7XG4gICAgaWYgKHZhbHVlID09IFwiPVwiKSByZXR1cm4gY29udCh0eXBlZXhwcik7XG4gIH1cbiAgZnVuY3Rpb24gdmFyZGVmKF8sIHZhbHVlKSB7XG4gICAgaWYgKHZhbHVlID09IFwiZW51bVwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KGVudW1kZWYpO1xuICAgIH1cbiAgICByZXR1cm4gcGFzcyhwYXR0ZXJuLCBtYXliZXR5cGUsIG1heWJlQXNzaWduLCB2YXJkZWZDb250KTtcbiAgfVxuICBmdW5jdGlvbiBwYXR0ZXJuKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKGlzVFMgJiYgaXNNb2RpZmllcih2YWx1ZSkpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQocGF0dGVybik7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwidmFyaWFibGVcIikge1xuICAgICAgcmVnaXN0ZXIodmFsdWUpO1xuICAgICAgcmV0dXJuIGNvbnQoKTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCJzcHJlYWRcIikgcmV0dXJuIGNvbnQocGF0dGVybik7XG4gICAgaWYgKHR5cGUgPT0gXCJbXCIpIHJldHVybiBjb250Q29tbWFzZXAoZWx0cGF0dGVybiwgXCJdXCIpO1xuICAgIGlmICh0eXBlID09IFwie1wiKSByZXR1cm4gY29udENvbW1hc2VwKHByb3BwYXR0ZXJuLCBcIn1cIik7XG4gIH1cbiAgZnVuY3Rpb24gcHJvcHBhdHRlcm4odHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIgJiYgIWN4LnN0cmVhbS5tYXRjaCgvXlxccyo6LywgZmFsc2UpKSB7XG4gICAgICByZWdpc3Rlcih2YWx1ZSk7XG4gICAgICByZXR1cm4gY29udChtYXliZUFzc2lnbik7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwidmFyaWFibGVcIikgY3gubWFya2VkID0gXCJwcm9wZXJ0eVwiO1xuICAgIGlmICh0eXBlID09IFwic3ByZWFkXCIpIHJldHVybiBjb250KHBhdHRlcm4pO1xuICAgIGlmICh0eXBlID09IFwifVwiKSByZXR1cm4gcGFzcygpO1xuICAgIGlmICh0eXBlID09IFwiW1wiKSByZXR1cm4gY29udChleHByZXNzaW9uLCBleHBlY3QoJ10nKSwgZXhwZWN0KCc6JyksIHByb3BwYXR0ZXJuKTtcbiAgICByZXR1cm4gY29udChleHBlY3QoXCI6XCIpLCBwYXR0ZXJuLCBtYXliZUFzc2lnbik7XG4gIH1cbiAgZnVuY3Rpb24gZWx0cGF0dGVybigpIHtcbiAgICByZXR1cm4gcGFzcyhwYXR0ZXJuLCBtYXliZUFzc2lnbik7XG4gIH1cbiAgZnVuY3Rpb24gbWF5YmVBc3NpZ24oX3R5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHZhbHVlID09IFwiPVwiKSByZXR1cm4gY29udChleHByZXNzaW9uTm9Db21tYSk7XG4gIH1cbiAgZnVuY3Rpb24gdmFyZGVmQ29udCh0eXBlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCIsXCIpIHJldHVybiBjb250KHZhcmRlZik7XG4gIH1cbiAgZnVuY3Rpb24gbWF5YmVlbHNlKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJrZXl3b3JkIGJcIiAmJiB2YWx1ZSA9PSBcImVsc2VcIikgcmV0dXJuIGNvbnQocHVzaGxleChcImZvcm1cIiwgXCJlbHNlXCIpLCBzdGF0ZW1lbnQsIHBvcGxleCk7XG4gIH1cbiAgZnVuY3Rpb24gZm9yc3BlYyh0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh2YWx1ZSA9PSBcImF3YWl0XCIpIHJldHVybiBjb250KGZvcnNwZWMpO1xuICAgIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiKVwiKSwgZm9yc3BlYzEsIHBvcGxleCk7XG4gIH1cbiAgZnVuY3Rpb24gZm9yc3BlYzEodHlwZSkge1xuICAgIGlmICh0eXBlID09IFwidmFyXCIpIHJldHVybiBjb250KHZhcmRlZiwgZm9yc3BlYzIpO1xuICAgIGlmICh0eXBlID09IFwidmFyaWFibGVcIikgcmV0dXJuIGNvbnQoZm9yc3BlYzIpO1xuICAgIHJldHVybiBwYXNzKGZvcnNwZWMyKTtcbiAgfVxuICBmdW5jdGlvbiBmb3JzcGVjMih0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh0eXBlID09IFwiKVwiKSByZXR1cm4gY29udCgpO1xuICAgIGlmICh0eXBlID09IFwiO1wiKSByZXR1cm4gY29udChmb3JzcGVjMik7XG4gICAgaWYgKHZhbHVlID09IFwiaW5cIiB8fCB2YWx1ZSA9PSBcIm9mXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbiwgZm9yc3BlYzIpO1xuICAgIH1cbiAgICByZXR1cm4gcGFzcyhleHByZXNzaW9uLCBmb3JzcGVjMik7XG4gIH1cbiAgZnVuY3Rpb24gZnVuY3Rpb25kZWYodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCIqXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQoZnVuY3Rpb25kZWYpO1xuICAgIH1cbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIHJlZ2lzdGVyKHZhbHVlKTtcbiAgICAgIHJldHVybiBjb250KGZ1bmN0aW9uZGVmKTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBjb250KHB1c2hjb250ZXh0LCBwdXNobGV4KFwiKVwiKSwgY29tbWFzZXAoZnVuYXJnLCBcIilcIiksIHBvcGxleCwgbWF5YmVyZXR0eXBlLCBzdGF0ZW1lbnQsIHBvcGNvbnRleHQpO1xuICAgIGlmIChpc1RTICYmIHZhbHVlID09IFwiPFwiKSByZXR1cm4gY29udChwdXNobGV4KFwiPlwiKSwgY29tbWFzZXAodHlwZXBhcmFtLCBcIj5cIiksIHBvcGxleCwgZnVuY3Rpb25kZWYpO1xuICB9XG4gIGZ1bmN0aW9uIGZ1bmN0aW9uZGVjbCh0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh2YWx1ZSA9PSBcIipcIikge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udChmdW5jdGlvbmRlY2wpO1xuICAgIH1cbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIHJlZ2lzdGVyKHZhbHVlKTtcbiAgICAgIHJldHVybiBjb250KGZ1bmN0aW9uZGVjbCk7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwiKFwiKSByZXR1cm4gY29udChwdXNoY29udGV4dCwgcHVzaGxleChcIilcIiksIGNvbW1hc2VwKGZ1bmFyZywgXCIpXCIpLCBwb3BsZXgsIG1heWJlcmV0dHlwZSwgcG9wY29udGV4dCk7XG4gICAgaWYgKGlzVFMgJiYgdmFsdWUgPT0gXCI8XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCI+XCIpLCBjb21tYXNlcCh0eXBlcGFyYW0sIFwiPlwiKSwgcG9wbGV4LCBmdW5jdGlvbmRlY2wpO1xuICB9XG4gIGZ1bmN0aW9uIHR5cGVuYW1lKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJrZXl3b3JkXCIgfHwgdHlwZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwidHlwZVwiO1xuICAgICAgcmV0dXJuIGNvbnQodHlwZW5hbWUpO1xuICAgIH0gZWxzZSBpZiAodmFsdWUgPT0gXCI8XCIpIHtcbiAgICAgIHJldHVybiBjb250KHB1c2hsZXgoXCI+XCIpLCBjb21tYXNlcCh0eXBlcGFyYW0sIFwiPlwiKSwgcG9wbGV4KTtcbiAgICB9XG4gIH1cbiAgZnVuY3Rpb24gZnVuYXJnKHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHZhbHVlID09IFwiQFwiKSBjb250KGV4cHJlc3Npb24sIGZ1bmFyZyk7XG4gICAgaWYgKHR5cGUgPT0gXCJzcHJlYWRcIikgcmV0dXJuIGNvbnQoZnVuYXJnKTtcbiAgICBpZiAoaXNUUyAmJiBpc01vZGlmaWVyKHZhbHVlKSkge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udChmdW5hcmcpO1xuICAgIH1cbiAgICBpZiAoaXNUUyAmJiB0eXBlID09IFwidGhpc1wiKSByZXR1cm4gY29udChtYXliZXR5cGUsIG1heWJlQXNzaWduKTtcbiAgICByZXR1cm4gcGFzcyhwYXR0ZXJuLCBtYXliZXR5cGUsIG1heWJlQXNzaWduKTtcbiAgfVxuICBmdW5jdGlvbiBjbGFzc0V4cHJlc3Npb24odHlwZSwgdmFsdWUpIHtcbiAgICAvLyBDbGFzcyBleHByZXNzaW9ucyBtYXkgaGF2ZSBhbiBvcHRpb25hbCBuYW1lLlxuICAgIGlmICh0eXBlID09IFwidmFyaWFibGVcIikgcmV0dXJuIGNsYXNzTmFtZSh0eXBlLCB2YWx1ZSk7XG4gICAgcmV0dXJuIGNsYXNzTmFtZUFmdGVyKHR5cGUsIHZhbHVlKTtcbiAgfVxuICBmdW5jdGlvbiBjbGFzc05hbWUodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgIHJlZ2lzdGVyKHZhbHVlKTtcbiAgICAgIHJldHVybiBjb250KGNsYXNzTmFtZUFmdGVyKTtcbiAgICB9XG4gIH1cbiAgZnVuY3Rpb24gY2xhc3NOYW1lQWZ0ZXIodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCI8XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCI+XCIpLCBjb21tYXNlcCh0eXBlcGFyYW0sIFwiPlwiKSwgcG9wbGV4LCBjbGFzc05hbWVBZnRlcik7XG4gICAgaWYgKHZhbHVlID09IFwiZXh0ZW5kc1wiIHx8IHZhbHVlID09IFwiaW1wbGVtZW50c1wiIHx8IGlzVFMgJiYgdHlwZSA9PSBcIixcIikge1xuICAgICAgaWYgKHZhbHVlID09IFwiaW1wbGVtZW50c1wiKSBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KGlzVFMgPyB0eXBlZXhwciA6IGV4cHJlc3Npb24sIGNsYXNzTmFtZUFmdGVyKTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCJ7XCIpIHJldHVybiBjb250KHB1c2hsZXgoXCJ9XCIpLCBjbGFzc0JvZHksIHBvcGxleCk7XG4gIH1cbiAgZnVuY3Rpb24gY2xhc3NCb2R5KHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJhc3luY1wiIHx8IHR5cGUgPT0gXCJ2YXJpYWJsZVwiICYmICh2YWx1ZSA9PSBcInN0YXRpY1wiIHx8IHZhbHVlID09IFwiZ2V0XCIgfHwgdmFsdWUgPT0gXCJzZXRcIiB8fCBpc1RTICYmIGlzTW9kaWZpZXIodmFsdWUpKSAmJiBjeC5zdHJlYW0ubWF0Y2goL15cXHMrIz9bXFx3JFxceGExLVxcdWZmZmZdLywgZmFsc2UpKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KGNsYXNzQm9keSk7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwidmFyaWFibGVcIiB8fCBjeC5zdHlsZSA9PSBcImtleXdvcmRcIikge1xuICAgICAgY3gubWFya2VkID0gXCJwcm9wZXJ0eVwiO1xuICAgICAgcmV0dXJuIGNvbnQoY2xhc3NmaWVsZCwgY2xhc3NCb2R5KTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCJudW1iZXJcIiB8fCB0eXBlID09IFwic3RyaW5nXCIpIHJldHVybiBjb250KGNsYXNzZmllbGQsIGNsYXNzQm9keSk7XG4gICAgaWYgKHR5cGUgPT0gXCJbXCIpIHJldHVybiBjb250KGV4cHJlc3Npb24sIG1heWJldHlwZSwgZXhwZWN0KFwiXVwiKSwgY2xhc3NmaWVsZCwgY2xhc3NCb2R5KTtcbiAgICBpZiAodmFsdWUgPT0gXCIqXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQoY2xhc3NCb2R5KTtcbiAgICB9XG4gICAgaWYgKGlzVFMgJiYgdHlwZSA9PSBcIihcIikgcmV0dXJuIHBhc3MoZnVuY3Rpb25kZWNsLCBjbGFzc0JvZHkpO1xuICAgIGlmICh0eXBlID09IFwiO1wiIHx8IHR5cGUgPT0gXCIsXCIpIHJldHVybiBjb250KGNsYXNzQm9keSk7XG4gICAgaWYgKHR5cGUgPT0gXCJ9XCIpIHJldHVybiBjb250KCk7XG4gICAgaWYgKHZhbHVlID09IFwiQFwiKSByZXR1cm4gY29udChleHByZXNzaW9uLCBjbGFzc0JvZHkpO1xuICB9XG4gIGZ1bmN0aW9uIGNsYXNzZmllbGQodHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCIhXCIgfHwgdmFsdWUgPT0gXCI/XCIpIHJldHVybiBjb250KGNsYXNzZmllbGQpO1xuICAgIGlmICh0eXBlID09IFwiOlwiKSByZXR1cm4gY29udCh0eXBlZXhwciwgbWF5YmVBc3NpZ24pO1xuICAgIGlmICh2YWx1ZSA9PSBcIj1cIikgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbk5vQ29tbWEpO1xuICAgIHZhciBjb250ZXh0ID0gY3guc3RhdGUubGV4aWNhbC5wcmV2LFxuICAgICAgaXNJbnRlcmZhY2UgPSBjb250ZXh0ICYmIGNvbnRleHQuaW5mbyA9PSBcImludGVyZmFjZVwiO1xuICAgIHJldHVybiBwYXNzKGlzSW50ZXJmYWNlID8gZnVuY3Rpb25kZWNsIDogZnVuY3Rpb25kZWYpO1xuICB9XG4gIGZ1bmN0aW9uIGFmdGVyRXhwb3J0KHR5cGUsIHZhbHVlKSB7XG4gICAgaWYgKHZhbHVlID09IFwiKlwiKSB7XG4gICAgICBjeC5tYXJrZWQgPSBcImtleXdvcmRcIjtcbiAgICAgIHJldHVybiBjb250KG1heWJlRnJvbSwgZXhwZWN0KFwiO1wiKSk7XG4gICAgfVxuICAgIGlmICh2YWx1ZSA9PSBcImRlZmF1bHRcIikge1xuICAgICAgY3gubWFya2VkID0gXCJrZXl3b3JkXCI7XG4gICAgICByZXR1cm4gY29udChleHByZXNzaW9uLCBleHBlY3QoXCI7XCIpKTtcbiAgICB9XG4gICAgaWYgKHR5cGUgPT0gXCJ7XCIpIHJldHVybiBjb250KGNvbW1hc2VwKGV4cG9ydEZpZWxkLCBcIn1cIiksIG1heWJlRnJvbSwgZXhwZWN0KFwiO1wiKSk7XG4gICAgcmV0dXJuIHBhc3Moc3RhdGVtZW50KTtcbiAgfVxuICBmdW5jdGlvbiBleHBvcnRGaWVsZCh0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh2YWx1ZSA9PSBcImFzXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQoZXhwZWN0KFwidmFyaWFibGVcIikpO1xuICAgIH1cbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHJldHVybiBwYXNzKGV4cHJlc3Npb25Ob0NvbW1hLCBleHBvcnRGaWVsZCk7XG4gIH1cbiAgZnVuY3Rpb24gYWZ0ZXJJbXBvcnQodHlwZSkge1xuICAgIGlmICh0eXBlID09IFwic3RyaW5nXCIpIHJldHVybiBjb250KCk7XG4gICAgaWYgKHR5cGUgPT0gXCIoXCIpIHJldHVybiBwYXNzKGV4cHJlc3Npb24pO1xuICAgIGlmICh0eXBlID09IFwiLlwiKSByZXR1cm4gcGFzcyhtYXliZW9wZXJhdG9yQ29tbWEpO1xuICAgIHJldHVybiBwYXNzKGltcG9ydFNwZWMsIG1heWJlTW9yZUltcG9ydHMsIG1heWJlRnJvbSk7XG4gIH1cbiAgZnVuY3Rpb24gaW1wb3J0U3BlYyh0eXBlLCB2YWx1ZSkge1xuICAgIGlmICh0eXBlID09IFwie1wiKSByZXR1cm4gY29udENvbW1hc2VwKGltcG9ydFNwZWMsIFwifVwiKTtcbiAgICBpZiAodHlwZSA9PSBcInZhcmlhYmxlXCIpIHJlZ2lzdGVyKHZhbHVlKTtcbiAgICBpZiAodmFsdWUgPT0gXCIqXCIpIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgIHJldHVybiBjb250KG1heWJlQXMpO1xuICB9XG4gIGZ1bmN0aW9uIG1heWJlTW9yZUltcG9ydHModHlwZSkge1xuICAgIGlmICh0eXBlID09IFwiLFwiKSByZXR1cm4gY29udChpbXBvcnRTcGVjLCBtYXliZU1vcmVJbXBvcnRzKTtcbiAgfVxuICBmdW5jdGlvbiBtYXliZUFzKF90eXBlLCB2YWx1ZSkge1xuICAgIGlmICh2YWx1ZSA9PSBcImFzXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQoaW1wb3J0U3BlYyk7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIG1heWJlRnJvbShfdHlwZSwgdmFsdWUpIHtcbiAgICBpZiAodmFsdWUgPT0gXCJmcm9tXCIpIHtcbiAgICAgIGN4Lm1hcmtlZCA9IFwia2V5d29yZFwiO1xuICAgICAgcmV0dXJuIGNvbnQoZXhwcmVzc2lvbik7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIGFycmF5TGl0ZXJhbCh0eXBlKSB7XG4gICAgaWYgKHR5cGUgPT0gXCJdXCIpIHJldHVybiBjb250KCk7XG4gICAgcmV0dXJuIHBhc3MoY29tbWFzZXAoZXhwcmVzc2lvbk5vQ29tbWEsIFwiXVwiKSk7XG4gIH1cbiAgZnVuY3Rpb24gZW51bWRlZigpIHtcbiAgICByZXR1cm4gcGFzcyhwdXNobGV4KFwiZm9ybVwiKSwgcGF0dGVybiwgZXhwZWN0KFwie1wiKSwgcHVzaGxleChcIn1cIiksIGNvbW1hc2VwKGVudW1tZW1iZXIsIFwifVwiKSwgcG9wbGV4LCBwb3BsZXgpO1xuICB9XG4gIGZ1bmN0aW9uIGVudW1tZW1iZXIoKSB7XG4gICAgcmV0dXJuIHBhc3MocGF0dGVybiwgbWF5YmVBc3NpZ24pO1xuICB9XG4gIGZ1bmN0aW9uIGlzQ29udGludWVkU3RhdGVtZW50KHN0YXRlLCB0ZXh0QWZ0ZXIpIHtcbiAgICByZXR1cm4gc3RhdGUubGFzdFR5cGUgPT0gXCJvcGVyYXRvclwiIHx8IHN0YXRlLmxhc3RUeXBlID09IFwiLFwiIHx8IGlzT3BlcmF0b3JDaGFyLnRlc3QodGV4dEFmdGVyLmNoYXJBdCgwKSkgfHwgL1ssLl0vLnRlc3QodGV4dEFmdGVyLmNoYXJBdCgwKSk7XG4gIH1cbiAgZnVuY3Rpb24gZXhwcmVzc2lvbkFsbG93ZWQoc3RyZWFtLCBzdGF0ZSwgYmFja1VwKSB7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplID09IHRva2VuQmFzZSAmJiAvXig/Om9wZXJhdG9yfHNvZnxrZXl3b3JkIFtiY2RdfGNhc2V8bmV3fGV4cG9ydHxkZWZhdWx0fHNwcmVhZHxbXFxbe31cXCgsOzpdfD0+KSQvLnRlc3Qoc3RhdGUubGFzdFR5cGUpIHx8IHN0YXRlLmxhc3RUeXBlID09IFwicXVhc2lcIiAmJiAvXFx7XFxzKiQvLnRlc3Qoc3RyZWFtLnN0cmluZy5zbGljZSgwLCBzdHJlYW0ucG9zIC0gKGJhY2tVcCB8fCAwKSkpO1xuICB9XG5cbiAgLy8gSW50ZXJmYWNlXG5cbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBwYXJzZXJDb25maWcubmFtZSxcbiAgICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgICAgdmFyIHN0YXRlID0ge1xuICAgICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgICBsYXN0VHlwZTogXCJzb2ZcIixcbiAgICAgICAgY2M6IFtdLFxuICAgICAgICBsZXhpY2FsOiBuZXcgSlNMZXhpY2FsKC1pbmRlbnRVbml0LCAwLCBcImJsb2NrXCIsIGZhbHNlKSxcbiAgICAgICAgbG9jYWxWYXJzOiBwYXJzZXJDb25maWcubG9jYWxWYXJzLFxuICAgICAgICBjb250ZXh0OiBwYXJzZXJDb25maWcubG9jYWxWYXJzICYmIG5ldyBDb250ZXh0KG51bGwsIG51bGwsIGZhbHNlKSxcbiAgICAgICAgaW5kZW50ZWQ6IDBcbiAgICAgIH07XG4gICAgICBpZiAocGFyc2VyQ29uZmlnLmdsb2JhbFZhcnMgJiYgdHlwZW9mIHBhcnNlckNvbmZpZy5nbG9iYWxWYXJzID09IFwib2JqZWN0XCIpIHN0YXRlLmdsb2JhbFZhcnMgPSBwYXJzZXJDb25maWcuZ2xvYmFsVmFycztcbiAgICAgIHJldHVybiBzdGF0ZTtcbiAgICB9LFxuICAgIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgICBpZiAoIXN0YXRlLmxleGljYWwuaGFzT3duUHJvcGVydHkoXCJhbGlnblwiKSkgc3RhdGUubGV4aWNhbC5hbGlnbiA9IGZhbHNlO1xuICAgICAgICBzdGF0ZS5pbmRlbnRlZCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgICAgICBmaW5kRmF0QXJyb3coc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgICBpZiAoc3RhdGUudG9rZW5pemUgIT0gdG9rZW5Db21tZW50ICYmIHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICAgIHZhciBzdHlsZSA9IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgaWYgKHR5cGUgPT0gXCJjb21tZW50XCIpIHJldHVybiBzdHlsZTtcbiAgICAgIHN0YXRlLmxhc3RUeXBlID0gdHlwZSA9PSBcIm9wZXJhdG9yXCIgJiYgKGNvbnRlbnQgPT0gXCIrK1wiIHx8IGNvbnRlbnQgPT0gXCItLVwiKSA/IFwiaW5jZGVjXCIgOiB0eXBlO1xuICAgICAgcmV0dXJuIHBhcnNlSlMoc3RhdGUsIHN0eWxlLCB0eXBlLCBjb250ZW50LCBzdHJlYW0pO1xuICAgIH0sXG4gICAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICAgIGlmIChzdGF0ZS50b2tlbml6ZSA9PSB0b2tlbkNvbW1lbnQgfHwgc3RhdGUudG9rZW5pemUgPT0gdG9rZW5RdWFzaSkgcmV0dXJuIG51bGw7XG4gICAgICBpZiAoc3RhdGUudG9rZW5pemUgIT0gdG9rZW5CYXNlKSByZXR1cm4gMDtcbiAgICAgIHZhciBmaXJzdENoYXIgPSB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKSxcbiAgICAgICAgbGV4aWNhbCA9IHN0YXRlLmxleGljYWwsXG4gICAgICAgIHRvcDtcbiAgICAgIC8vIEtsdWRnZSB0byBwcmV2ZW50ICdtYXliZWxzZScgZnJvbSBibG9ja2luZyBsZXhpY2FsIHNjb3BlIHBvcHNcbiAgICAgIGlmICghL15cXHMqZWxzZVxcYi8udGVzdCh0ZXh0QWZ0ZXIpKSBmb3IgKHZhciBpID0gc3RhdGUuY2MubGVuZ3RoIC0gMTsgaSA+PSAwOyAtLWkpIHtcbiAgICAgICAgdmFyIGMgPSBzdGF0ZS5jY1tpXTtcbiAgICAgICAgaWYgKGMgPT0gcG9wbGV4KSBsZXhpY2FsID0gbGV4aWNhbC5wcmV2O2Vsc2UgaWYgKGMgIT0gbWF5YmVlbHNlICYmIGMgIT0gcG9wY29udGV4dCkgYnJlYWs7XG4gICAgICB9XG4gICAgICB3aGlsZSAoKGxleGljYWwudHlwZSA9PSBcInN0YXRcIiB8fCBsZXhpY2FsLnR5cGUgPT0gXCJmb3JtXCIpICYmIChmaXJzdENoYXIgPT0gXCJ9XCIgfHwgKHRvcCA9IHN0YXRlLmNjW3N0YXRlLmNjLmxlbmd0aCAtIDFdKSAmJiAodG9wID09IG1heWJlb3BlcmF0b3JDb21tYSB8fCB0b3AgPT0gbWF5YmVvcGVyYXRvck5vQ29tbWEpICYmICEvXlssXFwuPStcXC0qOj9bXFwoXS8udGVzdCh0ZXh0QWZ0ZXIpKSkgbGV4aWNhbCA9IGxleGljYWwucHJldjtcbiAgICAgIGlmIChzdGF0ZW1lbnRJbmRlbnQgJiYgbGV4aWNhbC50eXBlID09IFwiKVwiICYmIGxleGljYWwucHJldi50eXBlID09IFwic3RhdFwiKSBsZXhpY2FsID0gbGV4aWNhbC5wcmV2O1xuICAgICAgdmFyIHR5cGUgPSBsZXhpY2FsLnR5cGUsXG4gICAgICAgIGNsb3NpbmcgPSBmaXJzdENoYXIgPT0gdHlwZTtcbiAgICAgIGlmICh0eXBlID09IFwidmFyZGVmXCIpIHJldHVybiBsZXhpY2FsLmluZGVudGVkICsgKHN0YXRlLmxhc3RUeXBlID09IFwib3BlcmF0b3JcIiB8fCBzdGF0ZS5sYXN0VHlwZSA9PSBcIixcIiA/IGxleGljYWwuaW5mby5sZW5ndGggKyAxIDogMCk7ZWxzZSBpZiAodHlwZSA9PSBcImZvcm1cIiAmJiBmaXJzdENoYXIgPT0gXCJ7XCIpIHJldHVybiBsZXhpY2FsLmluZGVudGVkO2Vsc2UgaWYgKHR5cGUgPT0gXCJmb3JtXCIpIHJldHVybiBsZXhpY2FsLmluZGVudGVkICsgY3gudW5pdDtlbHNlIGlmICh0eXBlID09IFwic3RhdFwiKSByZXR1cm4gbGV4aWNhbC5pbmRlbnRlZCArIChpc0NvbnRpbnVlZFN0YXRlbWVudChzdGF0ZSwgdGV4dEFmdGVyKSA/IHN0YXRlbWVudEluZGVudCB8fCBjeC51bml0IDogMCk7ZWxzZSBpZiAobGV4aWNhbC5pbmZvID09IFwic3dpdGNoXCIgJiYgIWNsb3NpbmcgJiYgcGFyc2VyQ29uZmlnLmRvdWJsZUluZGVudFN3aXRjaCAhPSBmYWxzZSkgcmV0dXJuIGxleGljYWwuaW5kZW50ZWQgKyAoL14oPzpjYXNlfGRlZmF1bHQpXFxiLy50ZXN0KHRleHRBZnRlcikgPyBjeC51bml0IDogMiAqIGN4LnVuaXQpO2Vsc2UgaWYgKGxleGljYWwuYWxpZ24pIHJldHVybiBsZXhpY2FsLmNvbHVtbiArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGxleGljYWwuaW5kZW50ZWQgKyAoY2xvc2luZyA/IDAgOiBjeC51bml0KTtcbiAgICB9LFxuICAgIGxhbmd1YWdlRGF0YToge1xuICAgICAgaW5kZW50T25JbnB1dDogL15cXHMqKD86Y2FzZSAuKj86fGRlZmF1bHQ6fFxce3xcXH0pJC8sXG4gICAgICBjb21tZW50VG9rZW5zOiBqc29uTW9kZSA/IHVuZGVmaW5lZCA6IHtcbiAgICAgICAgbGluZTogXCIvL1wiLFxuICAgICAgICBibG9jazoge1xuICAgICAgICAgIG9wZW46IFwiLypcIixcbiAgICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICAgIH1cbiAgICAgIH0sXG4gICAgICBjbG9zZUJyYWNrZXRzOiB7XG4gICAgICAgIGJyYWNrZXRzOiBbXCIoXCIsIFwiW1wiLCBcIntcIiwgXCInXCIsICdcIicsIFwiYFwiXVxuICAgICAgfSxcbiAgICAgIHdvcmRDaGFyczogXCIkXCJcbiAgICB9XG4gIH07XG59XG47XG5leHBvcnQgY29uc3QgamF2YXNjcmlwdCA9IG1rSmF2YVNjcmlwdCh7XG4gIG5hbWU6IFwiamF2YXNjcmlwdFwiXG59KTtcbmV4cG9ydCBjb25zdCBqc29uID0gbWtKYXZhU2NyaXB0KHtcbiAgbmFtZTogXCJqc29uXCIsXG4gIGpzb246IHRydWVcbn0pO1xuZXhwb3J0IGNvbnN0IGpzb25sZCA9IG1rSmF2YVNjcmlwdCh7XG4gIG5hbWU6IFwianNvblwiLFxuICBqc29ubGQ6IHRydWVcbn0pO1xuZXhwb3J0IGNvbnN0IHR5cGVzY3JpcHQgPSBta0phdmFTY3JpcHQoe1xuICBuYW1lOiBcInR5cGVzY3JpcHRcIixcbiAgdHlwZXNjcmlwdDogdHJ1ZVxufSk7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==