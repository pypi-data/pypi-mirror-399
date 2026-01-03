"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5904],{

/***/ 85904
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   csharp: () => (/* binding */ csharp),
/* harmony export */   dart: () => (/* binding */ dart),
/* harmony export */   kotlin: () => (/* binding */ kotlin),
/* harmony export */   objectiveC: () => (/* binding */ objectiveC),
/* harmony export */   objectiveCpp: () => (/* binding */ objectiveCpp),
/* harmony export */   scala: () => (/* binding */ scala),
/* harmony export */   squirrel: () => (/* binding */ squirrel)
/* harmony export */ });
/* unused harmony exports clike, c, cpp, java, shader, nesC, ceylon */
function Context(indented, column, type, info, align, prev) {
  this.indented = indented;
  this.column = column;
  this.type = type;
  this.info = info;
  this.align = align;
  this.prev = prev;
}
function pushContext(state, col, type, info) {
  var indent = state.indented;
  if (state.context && state.context.type == "statement" && type != "statement") indent = state.context.indented;
  return state.context = new Context(indent, col, type, info, null, state.context);
}
function popContext(state) {
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}
function typeBefore(stream, state, pos) {
  if (state.prevToken == "variable" || state.prevToken == "type") return true;
  if (/\S(?:[^- ]>|[*\]])\s*$|\*$/.test(stream.string.slice(0, pos))) return true;
  if (state.typeAtEndOfLine && stream.column() == stream.indentation()) return true;
}
function isTopScope(context) {
  for (;;) {
    if (!context || context.type == "top") return true;
    if (context.type == "}" && context.prev.info != "namespace") return false;
    context = context.prev;
  }
}
function clike(parserConfig) {
  var statementIndentUnit = parserConfig.statementIndentUnit,
    dontAlignCalls = parserConfig.dontAlignCalls,
    keywords = parserConfig.keywords || {},
    types = parserConfig.types || {},
    builtin = parserConfig.builtin || {},
    blockKeywords = parserConfig.blockKeywords || {},
    defKeywords = parserConfig.defKeywords || {},
    atoms = parserConfig.atoms || {},
    hooks = parserConfig.hooks || {},
    multiLineStrings = parserConfig.multiLineStrings,
    indentStatements = parserConfig.indentStatements !== false,
    indentSwitch = parserConfig.indentSwitch !== false,
    namespaceSeparator = parserConfig.namespaceSeparator,
    isPunctuationChar = parserConfig.isPunctuationChar || /[\[\]{}\(\),;\:\.]/,
    numberStart = parserConfig.numberStart || /[\d\.]/,
    number = parserConfig.number || /^(?:0x[a-f\d]+|0b[01]+|(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)(u|ll?|l|f)?/i,
    isOperatorChar = parserConfig.isOperatorChar || /[+\-*&%=<>!?|\/]/,
    isIdentifierChar = parserConfig.isIdentifierChar || /[\w\$_\xa1-\uffff]/,
    // An optional function that takes a {string} token and returns true if it
    // should be treated as a builtin.
    isReservedIdentifier = parserConfig.isReservedIdentifier || false;
  var curPunc, isDefKeyword;
  function tokenBase(stream, state) {
    var ch = stream.next();
    if (hooks[ch]) {
      var result = hooks[ch](stream, state);
      if (result !== false) return result;
    }
    if (ch == '"' || ch == "'") {
      state.tokenize = tokenString(ch);
      return state.tokenize(stream, state);
    }
    if (numberStart.test(ch)) {
      stream.backUp(1);
      if (stream.match(number)) return "number";
      stream.next();
    }
    if (isPunctuationChar.test(ch)) {
      curPunc = ch;
      return null;
    }
    if (ch == "/") {
      if (stream.eat("*")) {
        state.tokenize = tokenComment;
        return tokenComment(stream, state);
      }
      if (stream.eat("/")) {
        stream.skipToEnd();
        return "comment";
      }
    }
    if (isOperatorChar.test(ch)) {
      while (!stream.match(/^\/[\/*]/, false) && stream.eat(isOperatorChar)) {}
      return "operator";
    }
    stream.eatWhile(isIdentifierChar);
    if (namespaceSeparator) while (stream.match(namespaceSeparator)) stream.eatWhile(isIdentifierChar);
    var cur = stream.current();
    if (contains(keywords, cur)) {
      if (contains(blockKeywords, cur)) curPunc = "newstatement";
      if (contains(defKeywords, cur)) isDefKeyword = true;
      return "keyword";
    }
    if (contains(types, cur)) return "type";
    if (contains(builtin, cur) || isReservedIdentifier && isReservedIdentifier(cur)) {
      if (contains(blockKeywords, cur)) curPunc = "newstatement";
      return "builtin";
    }
    if (contains(atoms, cur)) return "atom";
    return "variable";
  }
  function tokenString(quote) {
    return function (stream, state) {
      var escaped = false,
        next,
        end = false;
      while ((next = stream.next()) != null) {
        if (next == quote && !escaped) {
          end = true;
          break;
        }
        escaped = !escaped && next == "\\";
      }
      if (end || !(escaped || multiLineStrings)) state.tokenize = null;
      return "string";
    };
  }
  function tokenComment(stream, state) {
    var maybeEnd = false,
      ch;
    while (ch = stream.next()) {
      if (ch == "/" && maybeEnd) {
        state.tokenize = null;
        break;
      }
      maybeEnd = ch == "*";
    }
    return "comment";
  }
  function maybeEOL(stream, state) {
    if (parserConfig.typeFirstDefinitions && stream.eol() && isTopScope(state.context)) state.typeAtEndOfLine = typeBefore(stream, state, stream.pos);
  }

  // Interface

  return {
    name: parserConfig.name,
    startState: function (indentUnit) {
      return {
        tokenize: null,
        context: new Context(-indentUnit, 0, "top", null, false),
        indented: 0,
        startOfLine: true,
        prevToken: null
      };
    },
    token: function (stream, state) {
      var ctx = state.context;
      if (stream.sol()) {
        if (ctx.align == null) ctx.align = false;
        state.indented = stream.indentation();
        state.startOfLine = true;
      }
      if (stream.eatSpace()) {
        maybeEOL(stream, state);
        return null;
      }
      curPunc = isDefKeyword = null;
      var style = (state.tokenize || tokenBase)(stream, state);
      if (style == "comment" || style == "meta") return style;
      if (ctx.align == null) ctx.align = true;
      if (curPunc == ";" || curPunc == ":" || curPunc == "," && stream.match(/^\s*(?:\/\/.*)?$/, false)) while (state.context.type == "statement") popContext(state);else if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "}") {
        while (ctx.type == "statement") ctx = popContext(state);
        if (ctx.type == "}") ctx = popContext(state);
        while (ctx.type == "statement") ctx = popContext(state);
      } else if (curPunc == ctx.type) popContext(state);else if (indentStatements && ((ctx.type == "}" || ctx.type == "top") && curPunc != ";" || ctx.type == "statement" && curPunc == "newstatement")) {
        pushContext(state, stream.column(), "statement", stream.current());
      }
      if (style == "variable" && (state.prevToken == "def" || parserConfig.typeFirstDefinitions && typeBefore(stream, state, stream.start) && isTopScope(state.context) && stream.match(/^\s*\(/, false))) style = "def";
      if (hooks.token) {
        var result = hooks.token(stream, state, style);
        if (result !== undefined) style = result;
      }
      if (style == "def" && parserConfig.styleDefs === false) style = "variable";
      state.startOfLine = false;
      state.prevToken = isDefKeyword ? "def" : style || curPunc;
      maybeEOL(stream, state);
      return style;
    },
    indent: function (state, textAfter, context) {
      if (state.tokenize != tokenBase && state.tokenize != null || state.typeAtEndOfLine && isTopScope(state.context)) return null;
      var ctx = state.context,
        firstChar = textAfter && textAfter.charAt(0);
      var closing = firstChar == ctx.type;
      if (ctx.type == "statement" && firstChar == "}") ctx = ctx.prev;
      if (parserConfig.dontIndentStatements) while (ctx.type == "statement" && parserConfig.dontIndentStatements.test(ctx.info)) ctx = ctx.prev;
      if (hooks.indent) {
        var hook = hooks.indent(state, ctx, textAfter, context.unit);
        if (typeof hook == "number") return hook;
      }
      var switchBlock = ctx.prev && ctx.prev.info == "switch";
      if (parserConfig.allmanIndentation && /[{(]/.test(firstChar)) {
        while (ctx.type != "top" && ctx.type != "}") ctx = ctx.prev;
        return ctx.indented;
      }
      if (ctx.type == "statement") return ctx.indented + (firstChar == "{" ? 0 : statementIndentUnit || context.unit);
      if (ctx.align && (!dontAlignCalls || ctx.type != ")")) return ctx.column + (closing ? 0 : 1);
      if (ctx.type == ")" && !closing) return ctx.indented + (statementIndentUnit || context.unit);
      return ctx.indented + (closing ? 0 : context.unit) + (!closing && switchBlock && !/^(?:case|default)\b/.test(textAfter) ? context.unit : 0);
    },
    languageData: {
      indentOnInput: indentSwitch ? /^\s*(?:case .*?:|default:|\{\}?|\})$/ : /^\s*[{}]$/,
      commentTokens: {
        line: "//",
        block: {
          open: "/*",
          close: "*/"
        }
      },
      autocomplete: Object.keys(keywords).concat(Object.keys(types)).concat(Object.keys(builtin)).concat(Object.keys(atoms)),
      ...parserConfig.languageData
    }
  };
}
;
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
function contains(words, word) {
  if (typeof words === "function") {
    return words(word);
  } else {
    return words.propertyIsEnumerable(word);
  }
}
var cKeywords = "auto if break case register continue return default do sizeof " + "static else struct switch extern typedef union for goto while enum const " + "volatile inline restrict asm fortran";

// Keywords from https://en.cppreference.com/w/cpp/keyword includes C++20.
var cppKeywords = "alignas alignof and and_eq audit axiom bitand bitor catch " + "class compl concept constexpr const_cast decltype delete dynamic_cast " + "explicit export final friend import module mutable namespace new noexcept " + "not not_eq operator or or_eq override private protected public " + "reinterpret_cast requires static_assert static_cast template this " + "thread_local throw try typeid typename using virtual xor xor_eq";
var objCKeywords = "bycopy byref in inout oneway out self super atomic nonatomic retain copy " + "readwrite readonly strong weak assign typeof nullable nonnull null_resettable _cmd " + "@interface @implementation @end @protocol @encode @property @synthesize @dynamic @class " + "@public @package @private @protected @required @optional @try @catch @finally @import " + "@selector @encode @defs @synchronized @autoreleasepool @compatibility_alias @available";
var objCBuiltins = "FOUNDATION_EXPORT FOUNDATION_EXTERN NS_INLINE NS_FORMAT_FUNCTION " + " NS_RETURNS_RETAINEDNS_ERROR_ENUM NS_RETURNS_NOT_RETAINED NS_RETURNS_INNER_POINTER " + "NS_DESIGNATED_INITIALIZER NS_ENUM NS_OPTIONS NS_REQUIRES_NIL_TERMINATION " + "NS_ASSUME_NONNULL_BEGIN NS_ASSUME_NONNULL_END NS_SWIFT_NAME NS_REFINED_FOR_SWIFT";

// Do not use this. Use the cTypes function below. This is global just to avoid
// excessive calls when cTypes is being called multiple times during a parse.
var basicCTypes = words("int long char short double float unsigned signed " + "void bool");

// Do not use this. Use the objCTypes function below. This is global just to avoid
// excessive calls when objCTypes is being called multiple times during a parse.
var basicObjCTypes = words("SEL instancetype id Class Protocol BOOL");

// Returns true if identifier is a "C" type.
// C type is defined as those that are reserved by the compiler (basicTypes),
// and those that end in _t (Reserved by POSIX for types)
// http://www.gnu.org/software/libc/manual/html_node/Reserved-Names.html
function cTypes(identifier) {
  return contains(basicCTypes, identifier) || /.+_t$/.test(identifier);
}

// Returns true if identifier is a "Objective C" type.
function objCTypes(identifier) {
  return cTypes(identifier) || contains(basicObjCTypes, identifier);
}
var cBlockKeywords = "case do else for if switch while struct enum union";
var cDefKeywords = "struct enum union";
function cppHook(stream, state) {
  if (!state.startOfLine) return false;
  for (var ch, next = null; ch = stream.peek();) {
    if (ch == "\\" && stream.match(/^.$/)) {
      next = cppHook;
      break;
    } else if (ch == "/" && stream.match(/^\/[\/\*]/, false)) {
      break;
    }
    stream.next();
  }
  state.tokenize = next;
  return "meta";
}
function pointerHook(_stream, state) {
  if (state.prevToken == "type") return "type";
  return false;
}

// For C and C++ (and ObjC): identifiers starting with __
// or _ followed by a capital letter are reserved for the compiler.
function cIsReservedIdentifier(token) {
  if (!token || token.length < 2) return false;
  if (token[0] != '_') return false;
  return token[1] == '_' || token[1] !== token[1].toLowerCase();
}
function cpp14Literal(stream) {
  stream.eatWhile(/[\w\.']/);
  return "number";
}
function cpp11StringHook(stream, state) {
  stream.backUp(1);
  // Raw strings.
  if (stream.match(/^(?:R|u8R|uR|UR|LR)/)) {
    var match = stream.match(/^"([^\s\\()]{0,16})\(/);
    if (!match) {
      return false;
    }
    state.cpp11RawStringDelim = match[1];
    state.tokenize = tokenRawString;
    return tokenRawString(stream, state);
  }
  // Unicode strings/chars.
  if (stream.match(/^(?:u8|u|U|L)/)) {
    if (stream.match(/^["']/, /* eat */false)) {
      return "string";
    }
    return false;
  }
  // Ignore this hook.
  stream.next();
  return false;
}
function cppLooksLikeConstructor(word) {
  var lastTwo = /(\w+)::~?(\w+)$/.exec(word);
  return lastTwo && lastTwo[1] == lastTwo[2];
}

// C#-style strings where "" escapes a quote.
function tokenAtString(stream, state) {
  var next;
  while ((next = stream.next()) != null) {
    if (next == '"' && !stream.eat('"')) {
      state.tokenize = null;
      break;
    }
  }
  return "string";
}

// C++11 raw string literal is <prefix>"<delim>( anything )<delim>", where
// <delim> can be a string up to 16 characters long.
function tokenRawString(stream, state) {
  // Escape characters that have special regex meanings.
  var delim = state.cpp11RawStringDelim.replace(/[^\w\s]/g, '\\$&');
  var match = stream.match(new RegExp(".*?\\)" + delim + '"'));
  if (match) state.tokenize = null;else stream.skipToEnd();
  return "string";
}
const c = clike({
  name: "c",
  keywords: words(cKeywords),
  types: cTypes,
  blockKeywords: words(cBlockKeywords),
  defKeywords: words(cDefKeywords),
  typeFirstDefinitions: true,
  atoms: words("NULL true false"),
  isReservedIdentifier: cIsReservedIdentifier,
  hooks: {
    "#": cppHook,
    "*": pointerHook
  }
});
const cpp = clike({
  name: "cpp",
  keywords: words(cKeywords + " " + cppKeywords),
  types: cTypes,
  blockKeywords: words(cBlockKeywords + " class try catch"),
  defKeywords: words(cDefKeywords + " class namespace"),
  typeFirstDefinitions: true,
  atoms: words("true false NULL nullptr"),
  dontIndentStatements: /^template$/,
  isIdentifierChar: /[\w\$_~\xa1-\uffff]/,
  isReservedIdentifier: cIsReservedIdentifier,
  hooks: {
    "#": cppHook,
    "*": pointerHook,
    "u": cpp11StringHook,
    "U": cpp11StringHook,
    "L": cpp11StringHook,
    "R": cpp11StringHook,
    "0": cpp14Literal,
    "1": cpp14Literal,
    "2": cpp14Literal,
    "3": cpp14Literal,
    "4": cpp14Literal,
    "5": cpp14Literal,
    "6": cpp14Literal,
    "7": cpp14Literal,
    "8": cpp14Literal,
    "9": cpp14Literal,
    token: function (stream, state, style) {
      if (style == "variable" && stream.peek() == "(" && (state.prevToken == ";" || state.prevToken == null || state.prevToken == "}") && cppLooksLikeConstructor(stream.current())) return "def";
    }
  },
  namespaceSeparator: "::"
});
const java = clike({
  name: "java",
  keywords: words("abstract assert break case catch class const continue default " + "do else enum extends final finally for goto if implements import " + "instanceof interface native new package private protected public " + "return static strictfp super switch synchronized this throw throws transient " + "try volatile while @interface"),
  types: words("var byte short int long float double boolean char void Boolean Byte Character Double Float " + "Integer Long Number Object Short String StringBuffer StringBuilder Void"),
  blockKeywords: words("catch class do else finally for if switch try while"),
  defKeywords: words("class interface enum @interface"),
  typeFirstDefinitions: true,
  atoms: words("true false null"),
  number: /^(?:0x[a-f\d_]+|0b[01_]+|(?:[\d_]+\.?\d*|\.\d+)(?:e[-+]?[\d_]+)?)(u|ll?|l|f)?/i,
  hooks: {
    "@": function (stream) {
      // Don't match the @interface keyword.
      if (stream.match('interface', false)) return false;
      stream.eatWhile(/[\w\$_]/);
      return "meta";
    },
    '"': function (stream, state) {
      if (!stream.match(/""$/)) return false;
      state.tokenize = tokenTripleString;
      return state.tokenize(stream, state);
    }
  }
});
const csharp = clike({
  name: "csharp",
  keywords: words("abstract as async await base break case catch checked class const continue" + " default delegate do else enum event explicit extern finally fixed for" + " foreach goto if implicit in init interface internal is lock namespace new" + " operator out override params private protected public readonly record ref required return sealed" + " sizeof stackalloc static struct switch this throw try typeof unchecked" + " unsafe using virtual void volatile while add alias ascending descending dynamic from get" + " global group into join let orderby partial remove select set value var yield"),
  types: words("Action Boolean Byte Char DateTime DateTimeOffset Decimal Double Func" + " Guid Int16 Int32 Int64 Object SByte Single String Task TimeSpan UInt16 UInt32" + " UInt64 bool byte char decimal double short int long object" + " sbyte float string ushort uint ulong"),
  blockKeywords: words("catch class do else finally for foreach if struct switch try while"),
  defKeywords: words("class interface namespace record struct var"),
  typeFirstDefinitions: true,
  atoms: words("true false null"),
  hooks: {
    "@": function (stream, state) {
      if (stream.eat('"')) {
        state.tokenize = tokenAtString;
        return tokenAtString(stream, state);
      }
      stream.eatWhile(/[\w\$_]/);
      return "meta";
    }
  }
});
function tokenTripleString(stream, state) {
  var escaped = false;
  while (!stream.eol()) {
    if (!escaped && stream.match('"""')) {
      state.tokenize = null;
      break;
    }
    escaped = stream.next() == "\\" && !escaped;
  }
  return "string";
}
function tokenNestedComment(depth) {
  return function (stream, state) {
    var ch;
    while (ch = stream.next()) {
      if (ch == "*" && stream.eat("/")) {
        if (depth == 1) {
          state.tokenize = null;
          break;
        } else {
          state.tokenize = tokenNestedComment(depth - 1);
          return state.tokenize(stream, state);
        }
      } else if (ch == "/" && stream.eat("*")) {
        state.tokenize = tokenNestedComment(depth + 1);
        return state.tokenize(stream, state);
      }
    }
    return "comment";
  };
}
const scala = clike({
  name: "scala",
  keywords: words(/* scala */
  "abstract case catch class def do else extends final finally for forSome if " + "implicit import lazy match new null object override package private protected return " + "sealed super this throw trait try type val var while with yield _ " + /* package scala */
  "assert assume require print println printf readLine readBoolean readByte readShort " + "readChar readInt readLong readFloat readDouble"),
  types: words("AnyVal App Application Array BufferedIterator BigDecimal BigInt Char Console Either " + "Enumeration Equiv Error Exception Fractional Function IndexedSeq Int Integral Iterable " + "Iterator List Map Numeric Nil NotNull Option Ordered Ordering PartialFunction PartialOrdering " + "Product Proxy Range Responder Seq Serializable Set Specializable Stream StringBuilder " + "StringContext Symbol Throwable Traversable TraversableOnce Tuple Unit Vector " + /* package java.lang */
  "Boolean Byte Character CharSequence Class ClassLoader Cloneable Comparable " + "Compiler Double Exception Float Integer Long Math Number Object Package Pair Process " + "Runtime Runnable SecurityManager Short StackTraceElement StrictMath String " + "StringBuffer System Thread ThreadGroup ThreadLocal Throwable Triple Void"),
  multiLineStrings: true,
  blockKeywords: words("catch class enum do else finally for forSome if match switch try while"),
  defKeywords: words("class enum def object package trait type val var"),
  atoms: words("true false null"),
  indentStatements: false,
  indentSwitch: false,
  isOperatorChar: /[+\-*&%=<>!?|\/#:@]/,
  hooks: {
    "@": function (stream) {
      stream.eatWhile(/[\w\$_]/);
      return "meta";
    },
    '"': function (stream, state) {
      if (!stream.match('""')) return false;
      state.tokenize = tokenTripleString;
      return state.tokenize(stream, state);
    },
    "'": function (stream) {
      if (stream.match(/^(\\[^'\s]+|[^\\'])'/)) return "character";
      stream.eatWhile(/[\w\$_\xa1-\uffff]/);
      return "atom";
    },
    "=": function (stream, state) {
      var cx = state.context;
      if (cx.type == "}" && cx.align && stream.eat(">")) {
        state.context = new Context(cx.indented, cx.column, cx.type, cx.info, null, cx.prev);
        return "operator";
      } else {
        return false;
      }
    },
    "/": function (stream, state) {
      if (!stream.eat("*")) return false;
      state.tokenize = tokenNestedComment(1);
      return state.tokenize(stream, state);
    }
  },
  languageData: {
    closeBrackets: {
      brackets: ["(", "[", "{", "'", '"', '"""']
    }
  }
});
function tokenKotlinString(tripleString) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while (!stream.eol()) {
      if (!tripleString && !escaped && stream.match('"')) {
        end = true;
        break;
      }
      if (tripleString && stream.match('"""')) {
        end = true;
        break;
      }
      next = stream.next();
      if (!escaped && next == "$" && stream.match('{')) stream.skipTo("}");
      escaped = !escaped && next == "\\" && !tripleString;
    }
    if (end || !tripleString) state.tokenize = null;
    return "string";
  };
}
const kotlin = clike({
  name: "kotlin",
  keywords: words(/*keywords*/
  "package as typealias class interface this super val operator " + "var fun for is in This throw return annotation " + "break continue object if else while do try when !in !is as? " + /*soft keywords*/
  "file import where by get set abstract enum open inner override private public internal " + "protected catch finally out final vararg reified dynamic companion constructor init " + "sealed field property receiver param sparam lateinit data inline noinline tailrec " + "external annotation crossinline const operator infix suspend actual expect setparam"),
  types: words(/* package java.lang */
  "Boolean Byte Character CharSequence Class ClassLoader Cloneable Comparable " + "Compiler Double Exception Float Integer Long Math Number Object Package Pair Process " + "Runtime Runnable SecurityManager Short StackTraceElement StrictMath String " + "StringBuffer System Thread ThreadGroup ThreadLocal Throwable Triple Void Annotation Any BooleanArray " + "ByteArray Char CharArray DeprecationLevel DoubleArray Enum FloatArray Function Int IntArray Lazy " + "LazyThreadSafetyMode LongArray Nothing ShortArray Unit"),
  intendSwitch: false,
  indentStatements: false,
  multiLineStrings: true,
  number: /^(?:0x[a-f\d_]+|0b[01_]+|(?:[\d_]+(\.\d+)?|\.\d+)(?:e[-+]?[\d_]+)?)(ul?|l|f)?/i,
  blockKeywords: words("catch class do else finally for if where try while enum"),
  defKeywords: words("class val var object interface fun"),
  atoms: words("true false null this"),
  hooks: {
    "@": function (stream) {
      stream.eatWhile(/[\w\$_]/);
      return "meta";
    },
    '*': function (_stream, state) {
      return state.prevToken == '.' ? 'variable' : 'operator';
    },
    '"': function (stream, state) {
      state.tokenize = tokenKotlinString(stream.match('""'));
      return state.tokenize(stream, state);
    },
    "/": function (stream, state) {
      if (!stream.eat("*")) return false;
      state.tokenize = tokenNestedComment(1);
      return state.tokenize(stream, state);
    },
    indent: function (state, ctx, textAfter, indentUnit) {
      var firstChar = textAfter && textAfter.charAt(0);
      if ((state.prevToken == "}" || state.prevToken == ")") && textAfter == "") return state.indented;
      if (state.prevToken == "operator" && textAfter != "}" && state.context.type != "}" || state.prevToken == "variable" && firstChar == "." || (state.prevToken == "}" || state.prevToken == ")") && firstChar == ".") return indentUnit * 2 + ctx.indented;
      if (ctx.align && ctx.type == "}") return ctx.indented + (state.context.type == (textAfter || "").charAt(0) ? 0 : indentUnit);
    }
  },
  languageData: {
    closeBrackets: {
      brackets: ["(", "[", "{", "'", '"', '"""']
    }
  }
});
const shader = clike({
  name: "shader",
  keywords: words("sampler1D sampler2D sampler3D samplerCube " + "sampler1DShadow sampler2DShadow " + "const attribute uniform varying " + "break continue discard return " + "for while do if else struct " + "in out inout"),
  types: words("float int bool void " + "vec2 vec3 vec4 ivec2 ivec3 ivec4 bvec2 bvec3 bvec4 " + "mat2 mat3 mat4"),
  blockKeywords: words("for while do if else struct"),
  builtin: words("radians degrees sin cos tan asin acos atan " + "pow exp log exp2 sqrt inversesqrt " + "abs sign floor ceil fract mod min max clamp mix step smoothstep " + "length distance dot cross normalize ftransform faceforward " + "reflect refract matrixCompMult " + "lessThan lessThanEqual greaterThan greaterThanEqual " + "equal notEqual any all not " + "texture1D texture1DProj texture1DLod texture1DProjLod " + "texture2D texture2DProj texture2DLod texture2DProjLod " + "texture3D texture3DProj texture3DLod texture3DProjLod " + "textureCube textureCubeLod " + "shadow1D shadow2D shadow1DProj shadow2DProj " + "shadow1DLod shadow2DLod shadow1DProjLod shadow2DProjLod " + "dFdx dFdy fwidth " + "noise1 noise2 noise3 noise4"),
  atoms: words("true false " + "gl_FragColor gl_SecondaryColor gl_Normal gl_Vertex " + "gl_MultiTexCoord0 gl_MultiTexCoord1 gl_MultiTexCoord2 gl_MultiTexCoord3 " + "gl_MultiTexCoord4 gl_MultiTexCoord5 gl_MultiTexCoord6 gl_MultiTexCoord7 " + "gl_FogCoord gl_PointCoord " + "gl_Position gl_PointSize gl_ClipVertex " + "gl_FrontColor gl_BackColor gl_FrontSecondaryColor gl_BackSecondaryColor " + "gl_TexCoord gl_FogFragCoord " + "gl_FragCoord gl_FrontFacing " + "gl_FragData gl_FragDepth " + "gl_ModelViewMatrix gl_ProjectionMatrix gl_ModelViewProjectionMatrix " + "gl_TextureMatrix gl_NormalMatrix gl_ModelViewMatrixInverse " + "gl_ProjectionMatrixInverse gl_ModelViewProjectionMatrixInverse " + "gl_TextureMatrixTranspose gl_ModelViewMatrixInverseTranspose " + "gl_ProjectionMatrixInverseTranspose " + "gl_ModelViewProjectionMatrixInverseTranspose " + "gl_TextureMatrixInverseTranspose " + "gl_NormalScale gl_DepthRange gl_ClipPlane " + "gl_Point gl_FrontMaterial gl_BackMaterial gl_LightSource gl_LightModel " + "gl_FrontLightModelProduct gl_BackLightModelProduct " + "gl_TextureColor gl_EyePlaneS gl_EyePlaneT gl_EyePlaneR gl_EyePlaneQ " + "gl_FogParameters " + "gl_MaxLights gl_MaxClipPlanes gl_MaxTextureUnits gl_MaxTextureCoords " + "gl_MaxVertexAttribs gl_MaxVertexUniformComponents gl_MaxVaryingFloats " + "gl_MaxVertexTextureImageUnits gl_MaxTextureImageUnits " + "gl_MaxFragmentUniformComponents gl_MaxCombineTextureImageUnits " + "gl_MaxDrawBuffers"),
  indentSwitch: false,
  hooks: {
    "#": cppHook
  }
});
const nesC = clike({
  name: "nesc",
  keywords: words(cKeywords + " as atomic async call command component components configuration event generic " + "implementation includes interface module new norace nx_struct nx_union post provides " + "signal task uses abstract extends"),
  types: cTypes,
  blockKeywords: words(cBlockKeywords),
  atoms: words("null true false"),
  hooks: {
    "#": cppHook
  }
});
const objectiveC = clike({
  name: "objectivec",
  keywords: words(cKeywords + " " + objCKeywords),
  types: objCTypes,
  builtin: words(objCBuiltins),
  blockKeywords: words(cBlockKeywords + " @synthesize @try @catch @finally @autoreleasepool @synchronized"),
  defKeywords: words(cDefKeywords + " @interface @implementation @protocol @class"),
  dontIndentStatements: /^@.*$/,
  typeFirstDefinitions: true,
  atoms: words("YES NO NULL Nil nil true false nullptr"),
  isReservedIdentifier: cIsReservedIdentifier,
  hooks: {
    "#": cppHook,
    "*": pointerHook
  }
});
const objectiveCpp = clike({
  name: "objectivecpp",
  keywords: words(cKeywords + " " + objCKeywords + " " + cppKeywords),
  types: objCTypes,
  builtin: words(objCBuiltins),
  blockKeywords: words(cBlockKeywords + " @synthesize @try @catch @finally @autoreleasepool @synchronized class try catch"),
  defKeywords: words(cDefKeywords + " @interface @implementation @protocol @class class namespace"),
  dontIndentStatements: /^@.*$|^template$/,
  typeFirstDefinitions: true,
  atoms: words("YES NO NULL Nil nil true false nullptr"),
  isReservedIdentifier: cIsReservedIdentifier,
  hooks: {
    "#": cppHook,
    "*": pointerHook,
    "u": cpp11StringHook,
    "U": cpp11StringHook,
    "L": cpp11StringHook,
    "R": cpp11StringHook,
    "0": cpp14Literal,
    "1": cpp14Literal,
    "2": cpp14Literal,
    "3": cpp14Literal,
    "4": cpp14Literal,
    "5": cpp14Literal,
    "6": cpp14Literal,
    "7": cpp14Literal,
    "8": cpp14Literal,
    "9": cpp14Literal,
    token: function (stream, state, style) {
      if (style == "variable" && stream.peek() == "(" && (state.prevToken == ";" || state.prevToken == null || state.prevToken == "}") && cppLooksLikeConstructor(stream.current())) return "def";
    }
  },
  namespaceSeparator: "::"
});
const squirrel = clike({
  name: "squirrel",
  keywords: words("base break clone continue const default delete enum extends function in class" + " foreach local resume return this throw typeof yield constructor instanceof static"),
  types: cTypes,
  blockKeywords: words("case catch class else for foreach if switch try while"),
  defKeywords: words("function local class"),
  typeFirstDefinitions: true,
  atoms: words("true false null"),
  hooks: {
    "#": cppHook
  }
});

// Ceylon Strings need to deal with interpolation
var stringTokenizer = null;
function tokenCeylonString(type) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while (!stream.eol()) {
      if (!escaped && stream.match('"') && (type == "single" || stream.match('""'))) {
        end = true;
        break;
      }
      if (!escaped && stream.match('``')) {
        stringTokenizer = tokenCeylonString(type);
        end = true;
        break;
      }
      next = stream.next();
      escaped = type == "single" && !escaped && next == "\\";
    }
    if (end) state.tokenize = null;
    return "string";
  };
}
const ceylon = clike({
  name: "ceylon",
  keywords: words("abstracts alias assembly assert assign break case catch class continue dynamic else" + " exists extends finally for function given if import in interface is let module new" + " nonempty object of out outer package return satisfies super switch then this throw" + " try value void while"),
  types: function (word) {
    // In Ceylon all identifiers that start with an uppercase are types
    var first = word.charAt(0);
    return first === first.toUpperCase() && first !== first.toLowerCase();
  },
  blockKeywords: words("case catch class dynamic else finally for function if interface module new object switch try while"),
  defKeywords: words("class dynamic function interface module object package value"),
  builtin: words("abstract actual aliased annotation by default deprecated doc final formal late license" + " native optional sealed see serializable shared suppressWarnings tagged throws variable"),
  isPunctuationChar: /[\[\]{}\(\),;\:\.`]/,
  isOperatorChar: /[+\-*&%=<>!?|^~:\/]/,
  numberStart: /[\d#$]/,
  number: /^(?:#[\da-fA-F_]+|\$[01_]+|[\d_]+[kMGTPmunpf]?|[\d_]+\.[\d_]+(?:[eE][-+]?\d+|[kMGTPmunpf]|)|)/i,
  multiLineStrings: true,
  typeFirstDefinitions: true,
  atoms: words("true false null larger smaller equal empty finished"),
  indentSwitch: false,
  styleDefs: false,
  hooks: {
    "@": function (stream) {
      stream.eatWhile(/[\w\$_]/);
      return "meta";
    },
    '"': function (stream, state) {
      state.tokenize = tokenCeylonString(stream.match('""') ? "triple" : "single");
      return state.tokenize(stream, state);
    },
    '`': function (stream, state) {
      if (!stringTokenizer || !stream.match('`')) return false;
      state.tokenize = stringTokenizer;
      stringTokenizer = null;
      return state.tokenize(stream, state);
    },
    "'": function (stream) {
      if (stream.match(/^(\\[^'\s]+|[^\\'])'/)) return "string.special";
      stream.eatWhile(/[\w\$_\xa1-\uffff]/);
      return "atom";
    },
    token: function (_stream, state, style) {
      if ((style == "variable" || style == "type") && state.prevToken == ".") {
        return "variableName.special";
      }
    }
  },
  languageData: {
    closeBrackets: {
      brackets: ["(", "[", "{", "'", '"', '"""']
    }
  }
});
function pushInterpolationStack(state) {
  (state.interpolationStack || (state.interpolationStack = [])).push(state.tokenize);
}
function popInterpolationStack(state) {
  return (state.interpolationStack || (state.interpolationStack = [])).pop();
}
function sizeInterpolationStack(state) {
  return state.interpolationStack ? state.interpolationStack.length : 0;
}
function tokenDartString(quote, stream, state, raw) {
  var tripleQuoted = false;
  if (stream.eat(quote)) {
    if (stream.eat(quote)) tripleQuoted = true;else return "string"; //empty string
  }
  function tokenStringHelper(stream, state) {
    var escaped = false;
    while (!stream.eol()) {
      if (!raw && !escaped && stream.peek() == "$") {
        pushInterpolationStack(state);
        state.tokenize = tokenInterpolation;
        return "string";
      }
      var next = stream.next();
      if (next == quote && !escaped && (!tripleQuoted || stream.match(quote + quote))) {
        state.tokenize = null;
        break;
      }
      escaped = !raw && !escaped && next == "\\";
    }
    return "string";
  }
  state.tokenize = tokenStringHelper;
  return tokenStringHelper(stream, state);
}
function tokenInterpolation(stream, state) {
  stream.eat("$");
  if (stream.eat("{")) {
    // let clike handle the content of ${...},
    // we take over again when "}" appears (see hooks).
    state.tokenize = null;
  } else {
    state.tokenize = tokenInterpolationIdentifier;
  }
  return null;
}
function tokenInterpolationIdentifier(stream, state) {
  stream.eatWhile(/[\w_]/);
  state.tokenize = popInterpolationStack(state);
  return "variable";
}
const dart = clike({
  name: "dart",
  keywords: words("this super static final const abstract class extends external factory " + "implements mixin get native set typedef with enum throw rethrow assert break case " + "continue default in return new deferred async await covariant try catch finally " + "do else for if switch while import library export part of show hide is as extension " + "on yield late required sealed base interface when inline"),
  blockKeywords: words("try catch finally do else for if switch while"),
  builtin: words("void bool num int double dynamic var String Null Never"),
  atoms: words("true false null"),
  // clike numbers without the suffixes, and with '_' separators.
  number: /^(?:0x[a-f\d_]+|(?:[\d_]+\.?[\d_]*|\.[\d_]+)(?:e[-+]?[\d_]+)?)/i,
  hooks: {
    "@": function (stream) {
      stream.eatWhile(/[\w\$_\.]/);
      return "meta";
    },
    // custom string handling to deal with triple-quoted strings and string interpolation
    "'": function (stream, state) {
      return tokenDartString("'", stream, state, false);
    },
    "\"": function (stream, state) {
      return tokenDartString("\"", stream, state, false);
    },
    "r": function (stream, state) {
      var peek = stream.peek();
      if (peek == "'" || peek == "\"") {
        return tokenDartString(stream.next(), stream, state, true);
      }
      return false;
    },
    "}": function (_stream, state) {
      // "}" is end of interpolation, if interpolation stack is non-empty
      if (sizeInterpolationStack(state) > 0) {
        state.tokenize = popInterpolationStack(state);
        return null;
      }
      return false;
    },
    "/": function (stream, state) {
      if (!stream.eat("*")) return false;
      state.tokenize = tokenNestedComment(1);
      return state.tokenize(stream, state);
    },
    token: function (stream, _, style) {
      if (style == "variable") {
        // Assume uppercase symbols are classes
        var isUpper = RegExp('^[_$]*[A-Z][a-zA-Z0-9_$]*$', 'g');
        if (isUpper.test(stream.current())) {
          return 'type';
        }
      }
    }
  }
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTkwNC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvY2xpa2UuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gQ29udGV4dChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBpbmZvLCBhbGlnbiwgcHJldikge1xuICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLmluZm8gPSBpbmZvO1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMucHJldiA9IHByZXY7XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlLCBpbmZvKSB7XG4gIHZhciBpbmRlbnQgPSBzdGF0ZS5pbmRlbnRlZDtcbiAgaWYgKHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC50eXBlID09IFwic3RhdGVtZW50XCIgJiYgdHlwZSAhPSBcInN0YXRlbWVudFwiKSBpbmRlbnQgPSBzdGF0ZS5jb250ZXh0LmluZGVudGVkO1xuICByZXR1cm4gc3RhdGUuY29udGV4dCA9IG5ldyBDb250ZXh0KGluZGVudCwgY29sLCB0eXBlLCBpbmZvLCBudWxsLCBzdGF0ZS5jb250ZXh0KTtcbn1cbmZ1bmN0aW9uIHBvcENvbnRleHQoc3RhdGUpIHtcbiAgdmFyIHQgPSBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIGlmICh0ID09IFwiKVwiIHx8IHQgPT0gXCJdXCIgfHwgdCA9PSBcIn1cIikgc3RhdGUuaW5kZW50ZWQgPSBzdGF0ZS5jb250ZXh0LmluZGVudGVkO1xuICByZXR1cm4gc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbn1cbmZ1bmN0aW9uIHR5cGVCZWZvcmUoc3RyZWFtLCBzdGF0ZSwgcG9zKSB7XG4gIGlmIChzdGF0ZS5wcmV2VG9rZW4gPT0gXCJ2YXJpYWJsZVwiIHx8IHN0YXRlLnByZXZUb2tlbiA9PSBcInR5cGVcIikgcmV0dXJuIHRydWU7XG4gIGlmICgvXFxTKD86W14tIF0+fFsqXFxdXSlcXHMqJHxcXCokLy50ZXN0KHN0cmVhbS5zdHJpbmcuc2xpY2UoMCwgcG9zKSkpIHJldHVybiB0cnVlO1xuICBpZiAoc3RhdGUudHlwZUF0RW5kT2ZMaW5lICYmIHN0cmVhbS5jb2x1bW4oKSA9PSBzdHJlYW0uaW5kZW50YXRpb24oKSkgcmV0dXJuIHRydWU7XG59XG5mdW5jdGlvbiBpc1RvcFNjb3BlKGNvbnRleHQpIHtcbiAgZm9yICg7Oykge1xuICAgIGlmICghY29udGV4dCB8fCBjb250ZXh0LnR5cGUgPT0gXCJ0b3BcIikgcmV0dXJuIHRydWU7XG4gICAgaWYgKGNvbnRleHQudHlwZSA9PSBcIn1cIiAmJiBjb250ZXh0LnByZXYuaW5mbyAhPSBcIm5hbWVzcGFjZVwiKSByZXR1cm4gZmFsc2U7XG4gICAgY29udGV4dCA9IGNvbnRleHQucHJldjtcbiAgfVxufVxuZXhwb3J0IGZ1bmN0aW9uIGNsaWtlKHBhcnNlckNvbmZpZykge1xuICB2YXIgc3RhdGVtZW50SW5kZW50VW5pdCA9IHBhcnNlckNvbmZpZy5zdGF0ZW1lbnRJbmRlbnRVbml0LFxuICAgIGRvbnRBbGlnbkNhbGxzID0gcGFyc2VyQ29uZmlnLmRvbnRBbGlnbkNhbGxzLFxuICAgIGtleXdvcmRzID0gcGFyc2VyQ29uZmlnLmtleXdvcmRzIHx8IHt9LFxuICAgIHR5cGVzID0gcGFyc2VyQ29uZmlnLnR5cGVzIHx8IHt9LFxuICAgIGJ1aWx0aW4gPSBwYXJzZXJDb25maWcuYnVpbHRpbiB8fCB7fSxcbiAgICBibG9ja0tleXdvcmRzID0gcGFyc2VyQ29uZmlnLmJsb2NrS2V5d29yZHMgfHwge30sXG4gICAgZGVmS2V5d29yZHMgPSBwYXJzZXJDb25maWcuZGVmS2V5d29yZHMgfHwge30sXG4gICAgYXRvbXMgPSBwYXJzZXJDb25maWcuYXRvbXMgfHwge30sXG4gICAgaG9va3MgPSBwYXJzZXJDb25maWcuaG9va3MgfHwge30sXG4gICAgbXVsdGlMaW5lU3RyaW5ncyA9IHBhcnNlckNvbmZpZy5tdWx0aUxpbmVTdHJpbmdzLFxuICAgIGluZGVudFN0YXRlbWVudHMgPSBwYXJzZXJDb25maWcuaW5kZW50U3RhdGVtZW50cyAhPT0gZmFsc2UsXG4gICAgaW5kZW50U3dpdGNoID0gcGFyc2VyQ29uZmlnLmluZGVudFN3aXRjaCAhPT0gZmFsc2UsXG4gICAgbmFtZXNwYWNlU2VwYXJhdG9yID0gcGFyc2VyQ29uZmlnLm5hbWVzcGFjZVNlcGFyYXRvcixcbiAgICBpc1B1bmN0dWF0aW9uQ2hhciA9IHBhcnNlckNvbmZpZy5pc1B1bmN0dWF0aW9uQ2hhciB8fCAvW1xcW1xcXXt9XFwoXFwpLDtcXDpcXC5dLyxcbiAgICBudW1iZXJTdGFydCA9IHBhcnNlckNvbmZpZy5udW1iZXJTdGFydCB8fCAvW1xcZFxcLl0vLFxuICAgIG51bWJlciA9IHBhcnNlckNvbmZpZy5udW1iZXIgfHwgL14oPzoweFthLWZcXGRdK3wwYlswMV0rfCg/OlxcZCtcXC4/XFxkKnxcXC5cXGQrKSg/OmVbLStdP1xcZCspPykodXxsbD98bHxmKT8vaSxcbiAgICBpc09wZXJhdG9yQ2hhciA9IHBhcnNlckNvbmZpZy5pc09wZXJhdG9yQ2hhciB8fCAvWytcXC0qJiU9PD4hP3xcXC9dLyxcbiAgICBpc0lkZW50aWZpZXJDaGFyID0gcGFyc2VyQ29uZmlnLmlzSWRlbnRpZmllckNoYXIgfHwgL1tcXHdcXCRfXFx4YTEtXFx1ZmZmZl0vLFxuICAgIC8vIEFuIG9wdGlvbmFsIGZ1bmN0aW9uIHRoYXQgdGFrZXMgYSB7c3RyaW5nfSB0b2tlbiBhbmQgcmV0dXJucyB0cnVlIGlmIGl0XG4gICAgLy8gc2hvdWxkIGJlIHRyZWF0ZWQgYXMgYSBidWlsdGluLlxuICAgIGlzUmVzZXJ2ZWRJZGVudGlmaWVyID0gcGFyc2VyQ29uZmlnLmlzUmVzZXJ2ZWRJZGVudGlmaWVyIHx8IGZhbHNlO1xuICB2YXIgY3VyUHVuYywgaXNEZWZLZXl3b3JkO1xuICBmdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgaWYgKGhvb2tzW2NoXSkge1xuICAgICAgdmFyIHJlc3VsdCA9IGhvb2tzW2NoXShzdHJlYW0sIHN0YXRlKTtcbiAgICAgIGlmIChyZXN1bHQgIT09IGZhbHNlKSByZXR1cm4gcmVzdWx0O1xuICAgIH1cbiAgICBpZiAoY2ggPT0gJ1wiJyB8fCBjaCA9PSBcIidcIikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICAgIGlmIChudW1iZXJTdGFydC50ZXN0KGNoKSkge1xuICAgICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2gobnVtYmVyKSkgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICBpZiAoaXNQdW5jdHVhdGlvbkNoYXIudGVzdChjaCkpIHtcbiAgICAgIGN1clB1bmMgPSBjaDtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICBpZiAoY2ggPT0gXCIvXCIpIHtcbiAgICAgIGlmIChzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ29tbWVudDtcbiAgICAgICAgcmV0dXJuIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0uZWF0KFwiL1wiKSkge1xuICAgICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICAgIH1cbiAgICB9XG4gICAgaWYgKGlzT3BlcmF0b3JDaGFyLnRlc3QoY2gpKSB7XG4gICAgICB3aGlsZSAoIXN0cmVhbS5tYXRjaCgvXlxcL1tcXC8qXS8sIGZhbHNlKSAmJiBzdHJlYW0uZWF0KGlzT3BlcmF0b3JDaGFyKSkge31cbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfVxuICAgIHN0cmVhbS5lYXRXaGlsZShpc0lkZW50aWZpZXJDaGFyKTtcbiAgICBpZiAobmFtZXNwYWNlU2VwYXJhdG9yKSB3aGlsZSAoc3RyZWFtLm1hdGNoKG5hbWVzcGFjZVNlcGFyYXRvcikpIHN0cmVhbS5lYXRXaGlsZShpc0lkZW50aWZpZXJDaGFyKTtcbiAgICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICBpZiAoY29udGFpbnMoa2V5d29yZHMsIGN1cikpIHtcbiAgICAgIGlmIChjb250YWlucyhibG9ja0tleXdvcmRzLCBjdXIpKSBjdXJQdW5jID0gXCJuZXdzdGF0ZW1lbnRcIjtcbiAgICAgIGlmIChjb250YWlucyhkZWZLZXl3b3JkcywgY3VyKSkgaXNEZWZLZXl3b3JkID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9XG4gICAgaWYgKGNvbnRhaW5zKHR5cGVzLCBjdXIpKSByZXR1cm4gXCJ0eXBlXCI7XG4gICAgaWYgKGNvbnRhaW5zKGJ1aWx0aW4sIGN1cikgfHwgaXNSZXNlcnZlZElkZW50aWZpZXIgJiYgaXNSZXNlcnZlZElkZW50aWZpZXIoY3VyKSkge1xuICAgICAgaWYgKGNvbnRhaW5zKGJsb2NrS2V5d29yZHMsIGN1cikpIGN1clB1bmMgPSBcIm5ld3N0YXRlbWVudFwiO1xuICAgICAgcmV0dXJuIFwiYnVpbHRpblwiO1xuICAgIH1cbiAgICBpZiAoY29udGFpbnMoYXRvbXMsIGN1cikpIHJldHVybiBcImF0b21cIjtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gICAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgICBuZXh0LFxuICAgICAgICBlbmQgPSBmYWxzZTtcbiAgICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICAgIGJyZWFrO1xuICAgICAgICB9XG4gICAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgICAgfVxuICAgICAgaWYgKGVuZCB8fCAhKGVzY2FwZWQgfHwgbXVsdGlMaW5lU3RyaW5ncykpIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIH07XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICAgIGlmIChjaCA9PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgbWF5YmVFbmQgPSBjaCA9PSBcIipcIjtcbiAgICB9XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG4gIGZ1bmN0aW9uIG1heWJlRU9MKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAocGFyc2VyQ29uZmlnLnR5cGVGaXJzdERlZmluaXRpb25zICYmIHN0cmVhbS5lb2woKSAmJiBpc1RvcFNjb3BlKHN0YXRlLmNvbnRleHQpKSBzdGF0ZS50eXBlQXRFbmRPZkxpbmUgPSB0eXBlQmVmb3JlKHN0cmVhbSwgc3RhdGUsIHN0cmVhbS5wb3MpO1xuICB9XG5cbiAgLy8gSW50ZXJmYWNlXG5cbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBwYXJzZXJDb25maWcubmFtZSxcbiAgICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdG9rZW5pemU6IG51bGwsXG4gICAgICAgIGNvbnRleHQ6IG5ldyBDb250ZXh0KC1pbmRlbnRVbml0LCAwLCBcInRvcFwiLCBudWxsLCBmYWxzZSksXG4gICAgICAgIGluZGVudGVkOiAwLFxuICAgICAgICBzdGFydE9mTGluZTogdHJ1ZSxcbiAgICAgICAgcHJldlRva2VuOiBudWxsXG4gICAgICB9O1xuICAgIH0sXG4gICAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgY3R4ID0gc3RhdGUuY29udGV4dDtcbiAgICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSBmYWxzZTtcbiAgICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgICAgfVxuICAgICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICAgIG1heWJlRU9MKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgIH1cbiAgICAgIGN1clB1bmMgPSBpc0RlZktleXdvcmQgPSBudWxsO1xuICAgICAgdmFyIHN0eWxlID0gKHN0YXRlLnRva2VuaXplIHx8IHRva2VuQmFzZSkoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICBpZiAoc3R5bGUgPT0gXCJjb21tZW50XCIgfHwgc3R5bGUgPT0gXCJtZXRhXCIpIHJldHVybiBzdHlsZTtcbiAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gdHJ1ZTtcbiAgICAgIGlmIChjdXJQdW5jID09IFwiO1wiIHx8IGN1clB1bmMgPT0gXCI6XCIgfHwgY3VyUHVuYyA9PSBcIixcIiAmJiBzdHJlYW0ubWF0Y2goL15cXHMqKD86XFwvXFwvLiopPyQvLCBmYWxzZSkpIHdoaWxlIChzdGF0ZS5jb250ZXh0LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIntcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJ9XCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJbXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiXVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwiKFwiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIilcIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIn1cIikge1xuICAgICAgICB3aGlsZSAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICAgIGlmIChjdHgudHlwZSA9PSBcIn1cIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICAgIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBjdHgudHlwZSkgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoaW5kZW50U3RhdGVtZW50cyAmJiAoKGN0eC50eXBlID09IFwifVwiIHx8IGN0eC50eXBlID09IFwidG9wXCIpICYmIGN1clB1bmMgIT0gXCI7XCIgfHwgY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIiAmJiBjdXJQdW5jID09IFwibmV3c3RhdGVtZW50XCIpKSB7XG4gICAgICAgIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwic3RhdGVtZW50XCIsIHN0cmVhbS5jdXJyZW50KCkpO1xuICAgICAgfVxuICAgICAgaWYgKHN0eWxlID09IFwidmFyaWFibGVcIiAmJiAoc3RhdGUucHJldlRva2VuID09IFwiZGVmXCIgfHwgcGFyc2VyQ29uZmlnLnR5cGVGaXJzdERlZmluaXRpb25zICYmIHR5cGVCZWZvcmUoc3RyZWFtLCBzdGF0ZSwgc3RyZWFtLnN0YXJ0KSAmJiBpc1RvcFNjb3BlKHN0YXRlLmNvbnRleHQpICYmIHN0cmVhbS5tYXRjaCgvXlxccypcXCgvLCBmYWxzZSkpKSBzdHlsZSA9IFwiZGVmXCI7XG4gICAgICBpZiAoaG9va3MudG9rZW4pIHtcbiAgICAgICAgdmFyIHJlc3VsdCA9IGhvb2tzLnRva2VuKHN0cmVhbSwgc3RhdGUsIHN0eWxlKTtcbiAgICAgICAgaWYgKHJlc3VsdCAhPT0gdW5kZWZpbmVkKSBzdHlsZSA9IHJlc3VsdDtcbiAgICAgIH1cbiAgICAgIGlmIChzdHlsZSA9PSBcImRlZlwiICYmIHBhcnNlckNvbmZpZy5zdHlsZURlZnMgPT09IGZhbHNlKSBzdHlsZSA9IFwidmFyaWFibGVcIjtcbiAgICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gZmFsc2U7XG4gICAgICBzdGF0ZS5wcmV2VG9rZW4gPSBpc0RlZktleXdvcmQgPyBcImRlZlwiIDogc3R5bGUgfHwgY3VyUHVuYztcbiAgICAgIG1heWJlRU9MKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgcmV0dXJuIHN0eWxlO1xuICAgIH0sXG4gICAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY29udGV4dCkge1xuICAgICAgaWYgKHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSAmJiBzdGF0ZS50b2tlbml6ZSAhPSBudWxsIHx8IHN0YXRlLnR5cGVBdEVuZE9mTGluZSAmJiBpc1RvcFNjb3BlKHN0YXRlLmNvbnRleHQpKSByZXR1cm4gbnVsbDtcbiAgICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0LFxuICAgICAgICBmaXJzdENoYXIgPSB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKTtcbiAgICAgIHZhciBjbG9zaW5nID0gZmlyc3RDaGFyID09IGN0eC50eXBlO1xuICAgICAgaWYgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIgJiYgZmlyc3RDaGFyID09IFwifVwiKSBjdHggPSBjdHgucHJldjtcbiAgICAgIGlmIChwYXJzZXJDb25maWcuZG9udEluZGVudFN0YXRlbWVudHMpIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmIHBhcnNlckNvbmZpZy5kb250SW5kZW50U3RhdGVtZW50cy50ZXN0KGN0eC5pbmZvKSkgY3R4ID0gY3R4LnByZXY7XG4gICAgICBpZiAoaG9va3MuaW5kZW50KSB7XG4gICAgICAgIHZhciBob29rID0gaG9va3MuaW5kZW50KHN0YXRlLCBjdHgsIHRleHRBZnRlciwgY29udGV4dC51bml0KTtcbiAgICAgICAgaWYgKHR5cGVvZiBob29rID09IFwibnVtYmVyXCIpIHJldHVybiBob29rO1xuICAgICAgfVxuICAgICAgdmFyIHN3aXRjaEJsb2NrID0gY3R4LnByZXYgJiYgY3R4LnByZXYuaW5mbyA9PSBcInN3aXRjaFwiO1xuICAgICAgaWYgKHBhcnNlckNvbmZpZy5hbGxtYW5JbmRlbnRhdGlvbiAmJiAvW3soXS8udGVzdChmaXJzdENoYXIpKSB7XG4gICAgICAgIHdoaWxlIChjdHgudHlwZSAhPSBcInRvcFwiICYmIGN0eC50eXBlICE9IFwifVwiKSBjdHggPSBjdHgucHJldjtcbiAgICAgICAgcmV0dXJuIGN0eC5pbmRlbnRlZDtcbiAgICAgIH1cbiAgICAgIGlmIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSByZXR1cm4gY3R4LmluZGVudGVkICsgKGZpcnN0Q2hhciA9PSBcIntcIiA/IDAgOiBzdGF0ZW1lbnRJbmRlbnRVbml0IHx8IGNvbnRleHQudW5pdCk7XG4gICAgICBpZiAoY3R4LmFsaWduICYmICghZG9udEFsaWduQ2FsbHMgfHwgY3R4LnR5cGUgIT0gXCIpXCIpKSByZXR1cm4gY3R4LmNvbHVtbiArIChjbG9zaW5nID8gMCA6IDEpO1xuICAgICAgaWYgKGN0eC50eXBlID09IFwiKVwiICYmICFjbG9zaW5nKSByZXR1cm4gY3R4LmluZGVudGVkICsgKHN0YXRlbWVudEluZGVudFVuaXQgfHwgY29udGV4dC51bml0KTtcbiAgICAgIHJldHVybiBjdHguaW5kZW50ZWQgKyAoY2xvc2luZyA/IDAgOiBjb250ZXh0LnVuaXQpICsgKCFjbG9zaW5nICYmIHN3aXRjaEJsb2NrICYmICEvXig/OmNhc2V8ZGVmYXVsdClcXGIvLnRlc3QodGV4dEFmdGVyKSA/IGNvbnRleHQudW5pdCA6IDApO1xuICAgIH0sXG4gICAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgICBpbmRlbnRPbklucHV0OiBpbmRlbnRTd2l0Y2ggPyAvXlxccyooPzpjYXNlIC4qPzp8ZGVmYXVsdDp8XFx7XFx9P3xcXH0pJC8gOiAvXlxccypbe31dJC8sXG4gICAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICAgIGxpbmU6IFwiLy9cIixcbiAgICAgICAgYmxvY2s6IHtcbiAgICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgICAgY2xvc2U6IFwiKi9cIlxuICAgICAgICB9XG4gICAgICB9LFxuICAgICAgYXV0b2NvbXBsZXRlOiBPYmplY3Qua2V5cyhrZXl3b3JkcykuY29uY2F0KE9iamVjdC5rZXlzKHR5cGVzKSkuY29uY2F0KE9iamVjdC5rZXlzKGJ1aWx0aW4pKS5jb25jYXQoT2JqZWN0LmtleXMoYXRvbXMpKSxcbiAgICAgIC4uLnBhcnNlckNvbmZpZy5sYW5ndWFnZURhdGFcbiAgICB9XG4gIH07XG59XG47XG5mdW5jdGlvbiB3b3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiIFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBvYmo7XG59XG5mdW5jdGlvbiBjb250YWlucyh3b3Jkcywgd29yZCkge1xuICBpZiAodHlwZW9mIHdvcmRzID09PSBcImZ1bmN0aW9uXCIpIHtcbiAgICByZXR1cm4gd29yZHMod29yZCk7XG4gIH0gZWxzZSB7XG4gICAgcmV0dXJuIHdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHdvcmQpO1xuICB9XG59XG52YXIgY0tleXdvcmRzID0gXCJhdXRvIGlmIGJyZWFrIGNhc2UgcmVnaXN0ZXIgY29udGludWUgcmV0dXJuIGRlZmF1bHQgZG8gc2l6ZW9mIFwiICsgXCJzdGF0aWMgZWxzZSBzdHJ1Y3Qgc3dpdGNoIGV4dGVybiB0eXBlZGVmIHVuaW9uIGZvciBnb3RvIHdoaWxlIGVudW0gY29uc3QgXCIgKyBcInZvbGF0aWxlIGlubGluZSByZXN0cmljdCBhc20gZm9ydHJhblwiO1xuXG4vLyBLZXl3b3JkcyBmcm9tIGh0dHBzOi8vZW4uY3BwcmVmZXJlbmNlLmNvbS93L2NwcC9rZXl3b3JkIGluY2x1ZGVzIEMrKzIwLlxudmFyIGNwcEtleXdvcmRzID0gXCJhbGlnbmFzIGFsaWdub2YgYW5kIGFuZF9lcSBhdWRpdCBheGlvbSBiaXRhbmQgYml0b3IgY2F0Y2ggXCIgKyBcImNsYXNzIGNvbXBsIGNvbmNlcHQgY29uc3RleHByIGNvbnN0X2Nhc3QgZGVjbHR5cGUgZGVsZXRlIGR5bmFtaWNfY2FzdCBcIiArIFwiZXhwbGljaXQgZXhwb3J0IGZpbmFsIGZyaWVuZCBpbXBvcnQgbW9kdWxlIG11dGFibGUgbmFtZXNwYWNlIG5ldyBub2V4Y2VwdCBcIiArIFwibm90IG5vdF9lcSBvcGVyYXRvciBvciBvcl9lcSBvdmVycmlkZSBwcml2YXRlIHByb3RlY3RlZCBwdWJsaWMgXCIgKyBcInJlaW50ZXJwcmV0X2Nhc3QgcmVxdWlyZXMgc3RhdGljX2Fzc2VydCBzdGF0aWNfY2FzdCB0ZW1wbGF0ZSB0aGlzIFwiICsgXCJ0aHJlYWRfbG9jYWwgdGhyb3cgdHJ5IHR5cGVpZCB0eXBlbmFtZSB1c2luZyB2aXJ0dWFsIHhvciB4b3JfZXFcIjtcbnZhciBvYmpDS2V5d29yZHMgPSBcImJ5Y29weSBieXJlZiBpbiBpbm91dCBvbmV3YXkgb3V0IHNlbGYgc3VwZXIgYXRvbWljIG5vbmF0b21pYyByZXRhaW4gY29weSBcIiArIFwicmVhZHdyaXRlIHJlYWRvbmx5IHN0cm9uZyB3ZWFrIGFzc2lnbiB0eXBlb2YgbnVsbGFibGUgbm9ubnVsbCBudWxsX3Jlc2V0dGFibGUgX2NtZCBcIiArIFwiQGludGVyZmFjZSBAaW1wbGVtZW50YXRpb24gQGVuZCBAcHJvdG9jb2wgQGVuY29kZSBAcHJvcGVydHkgQHN5bnRoZXNpemUgQGR5bmFtaWMgQGNsYXNzIFwiICsgXCJAcHVibGljIEBwYWNrYWdlIEBwcml2YXRlIEBwcm90ZWN0ZWQgQHJlcXVpcmVkIEBvcHRpb25hbCBAdHJ5IEBjYXRjaCBAZmluYWxseSBAaW1wb3J0IFwiICsgXCJAc2VsZWN0b3IgQGVuY29kZSBAZGVmcyBAc3luY2hyb25pemVkIEBhdXRvcmVsZWFzZXBvb2wgQGNvbXBhdGliaWxpdHlfYWxpYXMgQGF2YWlsYWJsZVwiO1xudmFyIG9iakNCdWlsdGlucyA9IFwiRk9VTkRBVElPTl9FWFBPUlQgRk9VTkRBVElPTl9FWFRFUk4gTlNfSU5MSU5FIE5TX0ZPUk1BVF9GVU5DVElPTiBcIiArIFwiIE5TX1JFVFVSTlNfUkVUQUlORUROU19FUlJPUl9FTlVNIE5TX1JFVFVSTlNfTk9UX1JFVEFJTkVEIE5TX1JFVFVSTlNfSU5ORVJfUE9JTlRFUiBcIiArIFwiTlNfREVTSUdOQVRFRF9JTklUSUFMSVpFUiBOU19FTlVNIE5TX09QVElPTlMgTlNfUkVRVUlSRVNfTklMX1RFUk1JTkFUSU9OIFwiICsgXCJOU19BU1NVTUVfTk9OTlVMTF9CRUdJTiBOU19BU1NVTUVfTk9OTlVMTF9FTkQgTlNfU1dJRlRfTkFNRSBOU19SRUZJTkVEX0ZPUl9TV0lGVFwiO1xuXG4vLyBEbyBub3QgdXNlIHRoaXMuIFVzZSB0aGUgY1R5cGVzIGZ1bmN0aW9uIGJlbG93LiBUaGlzIGlzIGdsb2JhbCBqdXN0IHRvIGF2b2lkXG4vLyBleGNlc3NpdmUgY2FsbHMgd2hlbiBjVHlwZXMgaXMgYmVpbmcgY2FsbGVkIG11bHRpcGxlIHRpbWVzIGR1cmluZyBhIHBhcnNlLlxudmFyIGJhc2ljQ1R5cGVzID0gd29yZHMoXCJpbnQgbG9uZyBjaGFyIHNob3J0IGRvdWJsZSBmbG9hdCB1bnNpZ25lZCBzaWduZWQgXCIgKyBcInZvaWQgYm9vbFwiKTtcblxuLy8gRG8gbm90IHVzZSB0aGlzLiBVc2UgdGhlIG9iakNUeXBlcyBmdW5jdGlvbiBiZWxvdy4gVGhpcyBpcyBnbG9iYWwganVzdCB0byBhdm9pZFxuLy8gZXhjZXNzaXZlIGNhbGxzIHdoZW4gb2JqQ1R5cGVzIGlzIGJlaW5nIGNhbGxlZCBtdWx0aXBsZSB0aW1lcyBkdXJpbmcgYSBwYXJzZS5cbnZhciBiYXNpY09iakNUeXBlcyA9IHdvcmRzKFwiU0VMIGluc3RhbmNldHlwZSBpZCBDbGFzcyBQcm90b2NvbCBCT09MXCIpO1xuXG4vLyBSZXR1cm5zIHRydWUgaWYgaWRlbnRpZmllciBpcyBhIFwiQ1wiIHR5cGUuXG4vLyBDIHR5cGUgaXMgZGVmaW5lZCBhcyB0aG9zZSB0aGF0IGFyZSByZXNlcnZlZCBieSB0aGUgY29tcGlsZXIgKGJhc2ljVHlwZXMpLFxuLy8gYW5kIHRob3NlIHRoYXQgZW5kIGluIF90IChSZXNlcnZlZCBieSBQT1NJWCBmb3IgdHlwZXMpXG4vLyBodHRwOi8vd3d3LmdudS5vcmcvc29mdHdhcmUvbGliYy9tYW51YWwvaHRtbF9ub2RlL1Jlc2VydmVkLU5hbWVzLmh0bWxcbmZ1bmN0aW9uIGNUeXBlcyhpZGVudGlmaWVyKSB7XG4gIHJldHVybiBjb250YWlucyhiYXNpY0NUeXBlcywgaWRlbnRpZmllcikgfHwgLy4rX3QkLy50ZXN0KGlkZW50aWZpZXIpO1xufVxuXG4vLyBSZXR1cm5zIHRydWUgaWYgaWRlbnRpZmllciBpcyBhIFwiT2JqZWN0aXZlIENcIiB0eXBlLlxuZnVuY3Rpb24gb2JqQ1R5cGVzKGlkZW50aWZpZXIpIHtcbiAgcmV0dXJuIGNUeXBlcyhpZGVudGlmaWVyKSB8fCBjb250YWlucyhiYXNpY09iakNUeXBlcywgaWRlbnRpZmllcik7XG59XG52YXIgY0Jsb2NrS2V5d29yZHMgPSBcImNhc2UgZG8gZWxzZSBmb3IgaWYgc3dpdGNoIHdoaWxlIHN0cnVjdCBlbnVtIHVuaW9uXCI7XG52YXIgY0RlZktleXdvcmRzID0gXCJzdHJ1Y3QgZW51bSB1bmlvblwiO1xuZnVuY3Rpb24gY3BwSG9vayhzdHJlYW0sIHN0YXRlKSB7XG4gIGlmICghc3RhdGUuc3RhcnRPZkxpbmUpIHJldHVybiBmYWxzZTtcbiAgZm9yICh2YXIgY2gsIG5leHQgPSBudWxsOyBjaCA9IHN0cmVhbS5wZWVrKCk7KSB7XG4gICAgaWYgKGNoID09IFwiXFxcXFwiICYmIHN0cmVhbS5tYXRjaCgvXi4kLykpIHtcbiAgICAgIG5leHQgPSBjcHBIb29rO1xuICAgICAgYnJlYWs7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBcIi9cIiAmJiBzdHJlYW0ubWF0Y2goL15cXC9bXFwvXFwqXS8sIGZhbHNlKSkge1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIHN0cmVhbS5uZXh0KCk7XG4gIH1cbiAgc3RhdGUudG9rZW5pemUgPSBuZXh0O1xuICByZXR1cm4gXCJtZXRhXCI7XG59XG5mdW5jdGlvbiBwb2ludGVySG9vayhfc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RhdGUucHJldlRva2VuID09IFwidHlwZVwiKSByZXR1cm4gXCJ0eXBlXCI7XG4gIHJldHVybiBmYWxzZTtcbn1cblxuLy8gRm9yIEMgYW5kIEMrKyAoYW5kIE9iakMpOiBpZGVudGlmaWVycyBzdGFydGluZyB3aXRoIF9fXG4vLyBvciBfIGZvbGxvd2VkIGJ5IGEgY2FwaXRhbCBsZXR0ZXIgYXJlIHJlc2VydmVkIGZvciB0aGUgY29tcGlsZXIuXG5mdW5jdGlvbiBjSXNSZXNlcnZlZElkZW50aWZpZXIodG9rZW4pIHtcbiAgaWYgKCF0b2tlbiB8fCB0b2tlbi5sZW5ndGggPCAyKSByZXR1cm4gZmFsc2U7XG4gIGlmICh0b2tlblswXSAhPSAnXycpIHJldHVybiBmYWxzZTtcbiAgcmV0dXJuIHRva2VuWzFdID09ICdfJyB8fCB0b2tlblsxXSAhPT0gdG9rZW5bMV0udG9Mb3dlckNhc2UoKTtcbn1cbmZ1bmN0aW9uIGNwcDE0TGl0ZXJhbChzdHJlYW0pIHtcbiAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwuJ10vKTtcbiAgcmV0dXJuIFwibnVtYmVyXCI7XG59XG5mdW5jdGlvbiBjcHAxMVN0cmluZ0hvb2soc3RyZWFtLCBzdGF0ZSkge1xuICBzdHJlYW0uYmFja1VwKDEpO1xuICAvLyBSYXcgc3RyaW5ncy5cbiAgaWYgKHN0cmVhbS5tYXRjaCgvXig/OlJ8dThSfHVSfFVSfExSKS8pKSB7XG4gICAgdmFyIG1hdGNoID0gc3RyZWFtLm1hdGNoKC9eXCIoW15cXHNcXFxcKCldezAsMTZ9KVxcKC8pO1xuICAgIGlmICghbWF0Y2gpIHtcbiAgICAgIHJldHVybiBmYWxzZTtcbiAgICB9XG4gICAgc3RhdGUuY3BwMTFSYXdTdHJpbmdEZWxpbSA9IG1hdGNoWzFdO1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5SYXdTdHJpbmc7XG4gICAgcmV0dXJuIHRva2VuUmF3U3RyaW5nKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIC8vIFVuaWNvZGUgc3RyaW5ncy9jaGFycy5cbiAgaWYgKHN0cmVhbS5tYXRjaCgvXig/OnU4fHV8VXxMKS8pKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXltcIiddLywgLyogZWF0ICovZmFsc2UpKSB7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9XG4gICAgcmV0dXJuIGZhbHNlO1xuICB9XG4gIC8vIElnbm9yZSB0aGlzIGhvb2suXG4gIHN0cmVhbS5uZXh0KCk7XG4gIHJldHVybiBmYWxzZTtcbn1cbmZ1bmN0aW9uIGNwcExvb2tzTGlrZUNvbnN0cnVjdG9yKHdvcmQpIHtcbiAgdmFyIGxhc3RUd28gPSAvKFxcdyspOjp+PyhcXHcrKSQvLmV4ZWMod29yZCk7XG4gIHJldHVybiBsYXN0VHdvICYmIGxhc3RUd29bMV0gPT0gbGFzdFR3b1syXTtcbn1cblxuLy8gQyMtc3R5bGUgc3RyaW5ncyB3aGVyZSBcIlwiIGVzY2FwZXMgYSBxdW90ZS5cbmZ1bmN0aW9uIHRva2VuQXRTdHJpbmcoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbmV4dDtcbiAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgIGlmIChuZXh0ID09ICdcIicgJiYgIXN0cmVhbS5lYXQoJ1wiJykpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgfVxuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cblxuLy8gQysrMTEgcmF3IHN0cmluZyBsaXRlcmFsIGlzIDxwcmVmaXg+XCI8ZGVsaW0+KCBhbnl0aGluZyApPGRlbGltPlwiLCB3aGVyZVxuLy8gPGRlbGltPiBjYW4gYmUgYSBzdHJpbmcgdXAgdG8gMTYgY2hhcmFjdGVycyBsb25nLlxuZnVuY3Rpb24gdG9rZW5SYXdTdHJpbmcoc3RyZWFtLCBzdGF0ZSkge1xuICAvLyBFc2NhcGUgY2hhcmFjdGVycyB0aGF0IGhhdmUgc3BlY2lhbCByZWdleCBtZWFuaW5ncy5cbiAgdmFyIGRlbGltID0gc3RhdGUuY3BwMTFSYXdTdHJpbmdEZWxpbS5yZXBsYWNlKC9bXlxcd1xcc10vZywgJ1xcXFwkJicpO1xuICB2YXIgbWF0Y2ggPSBzdHJlYW0ubWF0Y2gobmV3IFJlZ0V4cChcIi4qP1xcXFwpXCIgKyBkZWxpbSArICdcIicpKTtcbiAgaWYgKG1hdGNoKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7ZWxzZSBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIHJldHVybiBcInN0cmluZ1wiO1xufVxuZXhwb3J0IGNvbnN0IGMgPSBjbGlrZSh7XG4gIG5hbWU6IFwiY1wiLFxuICBrZXl3b3Jkczogd29yZHMoY0tleXdvcmRzKSxcbiAgdHlwZXM6IGNUeXBlcyxcbiAgYmxvY2tLZXl3b3Jkczogd29yZHMoY0Jsb2NrS2V5d29yZHMpLFxuICBkZWZLZXl3b3Jkczogd29yZHMoY0RlZktleXdvcmRzKSxcbiAgdHlwZUZpcnN0RGVmaW5pdGlvbnM6IHRydWUsXG4gIGF0b21zOiB3b3JkcyhcIk5VTEwgdHJ1ZSBmYWxzZVwiKSxcbiAgaXNSZXNlcnZlZElkZW50aWZpZXI6IGNJc1Jlc2VydmVkSWRlbnRpZmllcixcbiAgaG9va3M6IHtcbiAgICBcIiNcIjogY3BwSG9vayxcbiAgICBcIipcIjogcG9pbnRlckhvb2tcbiAgfVxufSk7XG5leHBvcnQgY29uc3QgY3BwID0gY2xpa2Uoe1xuICBuYW1lOiBcImNwcFwiLFxuICBrZXl3b3Jkczogd29yZHMoY0tleXdvcmRzICsgXCIgXCIgKyBjcHBLZXl3b3JkcyksXG4gIHR5cGVzOiBjVHlwZXMsXG4gIGJsb2NrS2V5d29yZHM6IHdvcmRzKGNCbG9ja0tleXdvcmRzICsgXCIgY2xhc3MgdHJ5IGNhdGNoXCIpLFxuICBkZWZLZXl3b3Jkczogd29yZHMoY0RlZktleXdvcmRzICsgXCIgY2xhc3MgbmFtZXNwYWNlXCIpLFxuICB0eXBlRmlyc3REZWZpbml0aW9uczogdHJ1ZSxcbiAgYXRvbXM6IHdvcmRzKFwidHJ1ZSBmYWxzZSBOVUxMIG51bGxwdHJcIiksXG4gIGRvbnRJbmRlbnRTdGF0ZW1lbnRzOiAvXnRlbXBsYXRlJC8sXG4gIGlzSWRlbnRpZmllckNoYXI6IC9bXFx3XFwkX35cXHhhMS1cXHVmZmZmXS8sXG4gIGlzUmVzZXJ2ZWRJZGVudGlmaWVyOiBjSXNSZXNlcnZlZElkZW50aWZpZXIsXG4gIGhvb2tzOiB7XG4gICAgXCIjXCI6IGNwcEhvb2ssXG4gICAgXCIqXCI6IHBvaW50ZXJIb29rLFxuICAgIFwidVwiOiBjcHAxMVN0cmluZ0hvb2ssXG4gICAgXCJVXCI6IGNwcDExU3RyaW5nSG9vayxcbiAgICBcIkxcIjogY3BwMTFTdHJpbmdIb29rLFxuICAgIFwiUlwiOiBjcHAxMVN0cmluZ0hvb2ssXG4gICAgXCIwXCI6IGNwcDE0TGl0ZXJhbCxcbiAgICBcIjFcIjogY3BwMTRMaXRlcmFsLFxuICAgIFwiMlwiOiBjcHAxNExpdGVyYWwsXG4gICAgXCIzXCI6IGNwcDE0TGl0ZXJhbCxcbiAgICBcIjRcIjogY3BwMTRMaXRlcmFsLFxuICAgIFwiNVwiOiBjcHAxNExpdGVyYWwsXG4gICAgXCI2XCI6IGNwcDE0TGl0ZXJhbCxcbiAgICBcIjdcIjogY3BwMTRMaXRlcmFsLFxuICAgIFwiOFwiOiBjcHAxNExpdGVyYWwsXG4gICAgXCI5XCI6IGNwcDE0TGl0ZXJhbCxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUsIHN0eWxlKSB7XG4gICAgICBpZiAoc3R5bGUgPT0gXCJ2YXJpYWJsZVwiICYmIHN0cmVhbS5wZWVrKCkgPT0gXCIoXCIgJiYgKHN0YXRlLnByZXZUb2tlbiA9PSBcIjtcIiB8fCBzdGF0ZS5wcmV2VG9rZW4gPT0gbnVsbCB8fCBzdGF0ZS5wcmV2VG9rZW4gPT0gXCJ9XCIpICYmIGNwcExvb2tzTGlrZUNvbnN0cnVjdG9yKHN0cmVhbS5jdXJyZW50KCkpKSByZXR1cm4gXCJkZWZcIjtcbiAgICB9XG4gIH0sXG4gIG5hbWVzcGFjZVNlcGFyYXRvcjogXCI6OlwiXG59KTtcbmV4cG9ydCBjb25zdCBqYXZhID0gY2xpa2Uoe1xuICBuYW1lOiBcImphdmFcIixcbiAga2V5d29yZHM6IHdvcmRzKFwiYWJzdHJhY3QgYXNzZXJ0IGJyZWFrIGNhc2UgY2F0Y2ggY2xhc3MgY29uc3QgY29udGludWUgZGVmYXVsdCBcIiArIFwiZG8gZWxzZSBlbnVtIGV4dGVuZHMgZmluYWwgZmluYWxseSBmb3IgZ290byBpZiBpbXBsZW1lbnRzIGltcG9ydCBcIiArIFwiaW5zdGFuY2VvZiBpbnRlcmZhY2UgbmF0aXZlIG5ldyBwYWNrYWdlIHByaXZhdGUgcHJvdGVjdGVkIHB1YmxpYyBcIiArIFwicmV0dXJuIHN0YXRpYyBzdHJpY3RmcCBzdXBlciBzd2l0Y2ggc3luY2hyb25pemVkIHRoaXMgdGhyb3cgdGhyb3dzIHRyYW5zaWVudCBcIiArIFwidHJ5IHZvbGF0aWxlIHdoaWxlIEBpbnRlcmZhY2VcIiksXG4gIHR5cGVzOiB3b3JkcyhcInZhciBieXRlIHNob3J0IGludCBsb25nIGZsb2F0IGRvdWJsZSBib29sZWFuIGNoYXIgdm9pZCBCb29sZWFuIEJ5dGUgQ2hhcmFjdGVyIERvdWJsZSBGbG9hdCBcIiArIFwiSW50ZWdlciBMb25nIE51bWJlciBPYmplY3QgU2hvcnQgU3RyaW5nIFN0cmluZ0J1ZmZlciBTdHJpbmdCdWlsZGVyIFZvaWRcIiksXG4gIGJsb2NrS2V5d29yZHM6IHdvcmRzKFwiY2F0Y2ggY2xhc3MgZG8gZWxzZSBmaW5hbGx5IGZvciBpZiBzd2l0Y2ggdHJ5IHdoaWxlXCIpLFxuICBkZWZLZXl3b3Jkczogd29yZHMoXCJjbGFzcyBpbnRlcmZhY2UgZW51bSBAaW50ZXJmYWNlXCIpLFxuICB0eXBlRmlyc3REZWZpbml0aW9uczogdHJ1ZSxcbiAgYXRvbXM6IHdvcmRzKFwidHJ1ZSBmYWxzZSBudWxsXCIpLFxuICBudW1iZXI6IC9eKD86MHhbYS1mXFxkX10rfDBiWzAxX10rfCg/OltcXGRfXStcXC4/XFxkKnxcXC5cXGQrKSg/OmVbLStdP1tcXGRfXSspPykodXxsbD98bHxmKT8vaSxcbiAgaG9va3M6IHtcbiAgICBcIkBcIjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgICAgLy8gRG9uJ3QgbWF0Y2ggdGhlIEBpbnRlcmZhY2Uga2V5d29yZC5cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goJ2ludGVyZmFjZScsIGZhbHNlKSkgcmV0dXJuIGZhbHNlO1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9LFxuICAgICdcIic6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoIXN0cmVhbS5tYXRjaCgvXCJcIiQvKSkgcmV0dXJuIGZhbHNlO1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblRyaXBsZVN0cmluZztcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gIH1cbn0pO1xuZXhwb3J0IGNvbnN0IGNzaGFycCA9IGNsaWtlKHtcbiAgbmFtZTogXCJjc2hhcnBcIixcbiAga2V5d29yZHM6IHdvcmRzKFwiYWJzdHJhY3QgYXMgYXN5bmMgYXdhaXQgYmFzZSBicmVhayBjYXNlIGNhdGNoIGNoZWNrZWQgY2xhc3MgY29uc3QgY29udGludWVcIiArIFwiIGRlZmF1bHQgZGVsZWdhdGUgZG8gZWxzZSBlbnVtIGV2ZW50IGV4cGxpY2l0IGV4dGVybiBmaW5hbGx5IGZpeGVkIGZvclwiICsgXCIgZm9yZWFjaCBnb3RvIGlmIGltcGxpY2l0IGluIGluaXQgaW50ZXJmYWNlIGludGVybmFsIGlzIGxvY2sgbmFtZXNwYWNlIG5ld1wiICsgXCIgb3BlcmF0b3Igb3V0IG92ZXJyaWRlIHBhcmFtcyBwcml2YXRlIHByb3RlY3RlZCBwdWJsaWMgcmVhZG9ubHkgcmVjb3JkIHJlZiByZXF1aXJlZCByZXR1cm4gc2VhbGVkXCIgKyBcIiBzaXplb2Ygc3RhY2thbGxvYyBzdGF0aWMgc3RydWN0IHN3aXRjaCB0aGlzIHRocm93IHRyeSB0eXBlb2YgdW5jaGVja2VkXCIgKyBcIiB1bnNhZmUgdXNpbmcgdmlydHVhbCB2b2lkIHZvbGF0aWxlIHdoaWxlIGFkZCBhbGlhcyBhc2NlbmRpbmcgZGVzY2VuZGluZyBkeW5hbWljIGZyb20gZ2V0XCIgKyBcIiBnbG9iYWwgZ3JvdXAgaW50byBqb2luIGxldCBvcmRlcmJ5IHBhcnRpYWwgcmVtb3ZlIHNlbGVjdCBzZXQgdmFsdWUgdmFyIHlpZWxkXCIpLFxuICB0eXBlczogd29yZHMoXCJBY3Rpb24gQm9vbGVhbiBCeXRlIENoYXIgRGF0ZVRpbWUgRGF0ZVRpbWVPZmZzZXQgRGVjaW1hbCBEb3VibGUgRnVuY1wiICsgXCIgR3VpZCBJbnQxNiBJbnQzMiBJbnQ2NCBPYmplY3QgU0J5dGUgU2luZ2xlIFN0cmluZyBUYXNrIFRpbWVTcGFuIFVJbnQxNiBVSW50MzJcIiArIFwiIFVJbnQ2NCBib29sIGJ5dGUgY2hhciBkZWNpbWFsIGRvdWJsZSBzaG9ydCBpbnQgbG9uZyBvYmplY3RcIiArIFwiIHNieXRlIGZsb2F0IHN0cmluZyB1c2hvcnQgdWludCB1bG9uZ1wiKSxcbiAgYmxvY2tLZXl3b3Jkczogd29yZHMoXCJjYXRjaCBjbGFzcyBkbyBlbHNlIGZpbmFsbHkgZm9yIGZvcmVhY2ggaWYgc3RydWN0IHN3aXRjaCB0cnkgd2hpbGVcIiksXG4gIGRlZktleXdvcmRzOiB3b3JkcyhcImNsYXNzIGludGVyZmFjZSBuYW1lc3BhY2UgcmVjb3JkIHN0cnVjdCB2YXJcIiksXG4gIHR5cGVGaXJzdERlZmluaXRpb25zOiB0cnVlLFxuICBhdG9tczogd29yZHMoXCJ0cnVlIGZhbHNlIG51bGxcIiksXG4gIGhvb2tzOiB7XG4gICAgXCJAXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoc3RyZWFtLmVhdCgnXCInKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQXRTdHJpbmc7XG4gICAgICAgIHJldHVybiB0b2tlbkF0U3RyaW5nKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgfVxuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9XG4gIH1cbn0pO1xuZnVuY3Rpb24gdG9rZW5UcmlwbGVTdHJpbmcoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgZXNjYXBlZCA9IGZhbHNlO1xuICB3aGlsZSAoIXN0cmVhbS5lb2woKSkge1xuICAgIGlmICghZXNjYXBlZCAmJiBzdHJlYW0ubWF0Y2goJ1wiXCJcIicpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgZXNjYXBlZCA9IHN0cmVhbS5uZXh0KCkgPT0gXCJcXFxcXCIgJiYgIWVzY2FwZWQ7XG4gIH1cbiAgcmV0dXJuIFwic3RyaW5nXCI7XG59XG5mdW5jdGlvbiB0b2tlbk5lc3RlZENvbW1lbnQoZGVwdGgpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoO1xuICAgIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICAgIGlmIChjaCA9PSBcIipcIiAmJiBzdHJlYW0uZWF0KFwiL1wiKSkge1xuICAgICAgICBpZiAoZGVwdGggPT0gMSkge1xuICAgICAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuTmVzdGVkQ29tbWVudChkZXB0aCAtIDEpO1xuICAgICAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIGlmIChjaCA9PSBcIi9cIiAmJiBzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuTmVzdGVkQ29tbWVudChkZXB0aCArIDEpO1xuICAgICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfTtcbn1cbmV4cG9ydCBjb25zdCBzY2FsYSA9IGNsaWtlKHtcbiAgbmFtZTogXCJzY2FsYVwiLFxuICBrZXl3b3Jkczogd29yZHMoLyogc2NhbGEgKi9cbiAgXCJhYnN0cmFjdCBjYXNlIGNhdGNoIGNsYXNzIGRlZiBkbyBlbHNlIGV4dGVuZHMgZmluYWwgZmluYWxseSBmb3IgZm9yU29tZSBpZiBcIiArIFwiaW1wbGljaXQgaW1wb3J0IGxhenkgbWF0Y2ggbmV3IG51bGwgb2JqZWN0IG92ZXJyaWRlIHBhY2thZ2UgcHJpdmF0ZSBwcm90ZWN0ZWQgcmV0dXJuIFwiICsgXCJzZWFsZWQgc3VwZXIgdGhpcyB0aHJvdyB0cmFpdCB0cnkgdHlwZSB2YWwgdmFyIHdoaWxlIHdpdGggeWllbGQgXyBcIiArIC8qIHBhY2thZ2Ugc2NhbGEgKi9cbiAgXCJhc3NlcnQgYXNzdW1lIHJlcXVpcmUgcHJpbnQgcHJpbnRsbiBwcmludGYgcmVhZExpbmUgcmVhZEJvb2xlYW4gcmVhZEJ5dGUgcmVhZFNob3J0IFwiICsgXCJyZWFkQ2hhciByZWFkSW50IHJlYWRMb25nIHJlYWRGbG9hdCByZWFkRG91YmxlXCIpLFxuICB0eXBlczogd29yZHMoXCJBbnlWYWwgQXBwIEFwcGxpY2F0aW9uIEFycmF5IEJ1ZmZlcmVkSXRlcmF0b3IgQmlnRGVjaW1hbCBCaWdJbnQgQ2hhciBDb25zb2xlIEVpdGhlciBcIiArIFwiRW51bWVyYXRpb24gRXF1aXYgRXJyb3IgRXhjZXB0aW9uIEZyYWN0aW9uYWwgRnVuY3Rpb24gSW5kZXhlZFNlcSBJbnQgSW50ZWdyYWwgSXRlcmFibGUgXCIgKyBcIkl0ZXJhdG9yIExpc3QgTWFwIE51bWVyaWMgTmlsIE5vdE51bGwgT3B0aW9uIE9yZGVyZWQgT3JkZXJpbmcgUGFydGlhbEZ1bmN0aW9uIFBhcnRpYWxPcmRlcmluZyBcIiArIFwiUHJvZHVjdCBQcm94eSBSYW5nZSBSZXNwb25kZXIgU2VxIFNlcmlhbGl6YWJsZSBTZXQgU3BlY2lhbGl6YWJsZSBTdHJlYW0gU3RyaW5nQnVpbGRlciBcIiArIFwiU3RyaW5nQ29udGV4dCBTeW1ib2wgVGhyb3dhYmxlIFRyYXZlcnNhYmxlIFRyYXZlcnNhYmxlT25jZSBUdXBsZSBVbml0IFZlY3RvciBcIiArIC8qIHBhY2thZ2UgamF2YS5sYW5nICovXG4gIFwiQm9vbGVhbiBCeXRlIENoYXJhY3RlciBDaGFyU2VxdWVuY2UgQ2xhc3MgQ2xhc3NMb2FkZXIgQ2xvbmVhYmxlIENvbXBhcmFibGUgXCIgKyBcIkNvbXBpbGVyIERvdWJsZSBFeGNlcHRpb24gRmxvYXQgSW50ZWdlciBMb25nIE1hdGggTnVtYmVyIE9iamVjdCBQYWNrYWdlIFBhaXIgUHJvY2VzcyBcIiArIFwiUnVudGltZSBSdW5uYWJsZSBTZWN1cml0eU1hbmFnZXIgU2hvcnQgU3RhY2tUcmFjZUVsZW1lbnQgU3RyaWN0TWF0aCBTdHJpbmcgXCIgKyBcIlN0cmluZ0J1ZmZlciBTeXN0ZW0gVGhyZWFkIFRocmVhZEdyb3VwIFRocmVhZExvY2FsIFRocm93YWJsZSBUcmlwbGUgVm9pZFwiKSxcbiAgbXVsdGlMaW5lU3RyaW5nczogdHJ1ZSxcbiAgYmxvY2tLZXl3b3Jkczogd29yZHMoXCJjYXRjaCBjbGFzcyBlbnVtIGRvIGVsc2UgZmluYWxseSBmb3IgZm9yU29tZSBpZiBtYXRjaCBzd2l0Y2ggdHJ5IHdoaWxlXCIpLFxuICBkZWZLZXl3b3Jkczogd29yZHMoXCJjbGFzcyBlbnVtIGRlZiBvYmplY3QgcGFja2FnZSB0cmFpdCB0eXBlIHZhbCB2YXJcIiksXG4gIGF0b21zOiB3b3JkcyhcInRydWUgZmFsc2UgbnVsbFwiKSxcbiAgaW5kZW50U3RhdGVtZW50czogZmFsc2UsXG4gIGluZGVudFN3aXRjaDogZmFsc2UsXG4gIGlzT3BlcmF0b3JDaGFyOiAvWytcXC0qJiU9PD4hP3xcXC8jOkBdLyxcbiAgaG9va3M6IHtcbiAgICBcIkBcIjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9LFxuICAgICdcIic6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoIXN0cmVhbS5tYXRjaCgnXCJcIicpKSByZXR1cm4gZmFsc2U7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuVHJpcGxlU3RyaW5nO1xuICAgICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIH0sXG4gICAgXCInXCI6IGZ1bmN0aW9uIChzdHJlYW0pIHtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14oXFxcXFteJ1xcc10rfFteXFxcXCddKScvKSkgcmV0dXJuIFwiY2hhcmFjdGVyXCI7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXFx4YTEtXFx1ZmZmZl0vKTtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9LFxuICAgIFwiPVwiOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgdmFyIGN4ID0gc3RhdGUuY29udGV4dDtcbiAgICAgIGlmIChjeC50eXBlID09IFwifVwiICYmIGN4LmFsaWduICYmIHN0cmVhbS5lYXQoXCI+XCIpKSB7XG4gICAgICAgIHN0YXRlLmNvbnRleHQgPSBuZXcgQ29udGV4dChjeC5pbmRlbnRlZCwgY3guY29sdW1uLCBjeC50eXBlLCBjeC5pbmZvLCBudWxsLCBjeC5wcmV2KTtcbiAgICAgICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHJldHVybiBmYWxzZTtcbiAgICAgIH1cbiAgICB9LFxuICAgIFwiL1wiOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgaWYgKCFzdHJlYW0uZWF0KFwiKlwiKSkgcmV0dXJuIGZhbHNlO1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbk5lc3RlZENvbW1lbnQoMSk7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjbG9zZUJyYWNrZXRzOiB7XG4gICAgICBicmFja2V0czogW1wiKFwiLCBcIltcIiwgXCJ7XCIsIFwiJ1wiLCAnXCInLCAnXCJcIlwiJ11cbiAgICB9XG4gIH1cbn0pO1xuZnVuY3Rpb24gdG9rZW5Lb3RsaW5TdHJpbmcodHJpcGxlU3RyaW5nKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKCFzdHJlYW0uZW9sKCkpIHtcbiAgICAgIGlmICghdHJpcGxlU3RyaW5nICYmICFlc2NhcGVkICYmIHN0cmVhbS5tYXRjaCgnXCInKSkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGlmICh0cmlwbGVTdHJpbmcgJiYgc3RyZWFtLm1hdGNoKCdcIlwiXCInKSkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIG5leHQgPSBzdHJlYW0ubmV4dCgpO1xuICAgICAgaWYgKCFlc2NhcGVkICYmIG5leHQgPT0gXCIkXCIgJiYgc3RyZWFtLm1hdGNoKCd7JykpIHN0cmVhbS5za2lwVG8oXCJ9XCIpO1xuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIG5leHQgPT0gXCJcXFxcXCIgJiYgIXRyaXBsZVN0cmluZztcbiAgICB9XG4gICAgaWYgKGVuZCB8fCAhdHJpcGxlU3RyaW5nKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5leHBvcnQgY29uc3Qga290bGluID0gY2xpa2Uoe1xuICBuYW1lOiBcImtvdGxpblwiLFxuICBrZXl3b3Jkczogd29yZHMoLyprZXl3b3JkcyovXG4gIFwicGFja2FnZSBhcyB0eXBlYWxpYXMgY2xhc3MgaW50ZXJmYWNlIHRoaXMgc3VwZXIgdmFsIG9wZXJhdG9yIFwiICsgXCJ2YXIgZnVuIGZvciBpcyBpbiBUaGlzIHRocm93IHJldHVybiBhbm5vdGF0aW9uIFwiICsgXCJicmVhayBjb250aW51ZSBvYmplY3QgaWYgZWxzZSB3aGlsZSBkbyB0cnkgd2hlbiAhaW4gIWlzIGFzPyBcIiArIC8qc29mdCBrZXl3b3JkcyovXG4gIFwiZmlsZSBpbXBvcnQgd2hlcmUgYnkgZ2V0IHNldCBhYnN0cmFjdCBlbnVtIG9wZW4gaW5uZXIgb3ZlcnJpZGUgcHJpdmF0ZSBwdWJsaWMgaW50ZXJuYWwgXCIgKyBcInByb3RlY3RlZCBjYXRjaCBmaW5hbGx5IG91dCBmaW5hbCB2YXJhcmcgcmVpZmllZCBkeW5hbWljIGNvbXBhbmlvbiBjb25zdHJ1Y3RvciBpbml0IFwiICsgXCJzZWFsZWQgZmllbGQgcHJvcGVydHkgcmVjZWl2ZXIgcGFyYW0gc3BhcmFtIGxhdGVpbml0IGRhdGEgaW5saW5lIG5vaW5saW5lIHRhaWxyZWMgXCIgKyBcImV4dGVybmFsIGFubm90YXRpb24gY3Jvc3NpbmxpbmUgY29uc3Qgb3BlcmF0b3IgaW5maXggc3VzcGVuZCBhY3R1YWwgZXhwZWN0IHNldHBhcmFtXCIpLFxuICB0eXBlczogd29yZHMoLyogcGFja2FnZSBqYXZhLmxhbmcgKi9cbiAgXCJCb29sZWFuIEJ5dGUgQ2hhcmFjdGVyIENoYXJTZXF1ZW5jZSBDbGFzcyBDbGFzc0xvYWRlciBDbG9uZWFibGUgQ29tcGFyYWJsZSBcIiArIFwiQ29tcGlsZXIgRG91YmxlIEV4Y2VwdGlvbiBGbG9hdCBJbnRlZ2VyIExvbmcgTWF0aCBOdW1iZXIgT2JqZWN0IFBhY2thZ2UgUGFpciBQcm9jZXNzIFwiICsgXCJSdW50aW1lIFJ1bm5hYmxlIFNlY3VyaXR5TWFuYWdlciBTaG9ydCBTdGFja1RyYWNlRWxlbWVudCBTdHJpY3RNYXRoIFN0cmluZyBcIiArIFwiU3RyaW5nQnVmZmVyIFN5c3RlbSBUaHJlYWQgVGhyZWFkR3JvdXAgVGhyZWFkTG9jYWwgVGhyb3dhYmxlIFRyaXBsZSBWb2lkIEFubm90YXRpb24gQW55IEJvb2xlYW5BcnJheSBcIiArIFwiQnl0ZUFycmF5IENoYXIgQ2hhckFycmF5IERlcHJlY2F0aW9uTGV2ZWwgRG91YmxlQXJyYXkgRW51bSBGbG9hdEFycmF5IEZ1bmN0aW9uIEludCBJbnRBcnJheSBMYXp5IFwiICsgXCJMYXp5VGhyZWFkU2FmZXR5TW9kZSBMb25nQXJyYXkgTm90aGluZyBTaG9ydEFycmF5IFVuaXRcIiksXG4gIGludGVuZFN3aXRjaDogZmFsc2UsXG4gIGluZGVudFN0YXRlbWVudHM6IGZhbHNlLFxuICBtdWx0aUxpbmVTdHJpbmdzOiB0cnVlLFxuICBudW1iZXI6IC9eKD86MHhbYS1mXFxkX10rfDBiWzAxX10rfCg/OltcXGRfXSsoXFwuXFxkKyk/fFxcLlxcZCspKD86ZVstK10/W1xcZF9dKyk/KSh1bD98bHxmKT8vaSxcbiAgYmxvY2tLZXl3b3Jkczogd29yZHMoXCJjYXRjaCBjbGFzcyBkbyBlbHNlIGZpbmFsbHkgZm9yIGlmIHdoZXJlIHRyeSB3aGlsZSBlbnVtXCIpLFxuICBkZWZLZXl3b3Jkczogd29yZHMoXCJjbGFzcyB2YWwgdmFyIG9iamVjdCBpbnRlcmZhY2UgZnVuXCIpLFxuICBhdG9tczogd29yZHMoXCJ0cnVlIGZhbHNlIG51bGwgdGhpc1wiKSxcbiAgaG9va3M6IHtcbiAgICBcIkBcIjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9LFxuICAgICcqJzogZnVuY3Rpb24gKF9zdHJlYW0sIHN0YXRlKSB7XG4gICAgICByZXR1cm4gc3RhdGUucHJldlRva2VuID09ICcuJyA/ICd2YXJpYWJsZScgOiAnb3BlcmF0b3InO1xuICAgIH0sXG4gICAgJ1wiJzogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Lb3RsaW5TdHJpbmcoc3RyZWFtLm1hdGNoKCdcIlwiJykpO1xuICAgICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIH0sXG4gICAgXCIvXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoIXN0cmVhbS5lYXQoXCIqXCIpKSByZXR1cm4gZmFsc2U7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuTmVzdGVkQ29tbWVudCgxKTtcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9LFxuICAgIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCBjdHgsIHRleHRBZnRlciwgaW5kZW50VW5pdCkge1xuICAgICAgdmFyIGZpcnN0Q2hhciA9IHRleHRBZnRlciAmJiB0ZXh0QWZ0ZXIuY2hhckF0KDApO1xuICAgICAgaWYgKChzdGF0ZS5wcmV2VG9rZW4gPT0gXCJ9XCIgfHwgc3RhdGUucHJldlRva2VuID09IFwiKVwiKSAmJiB0ZXh0QWZ0ZXIgPT0gXCJcIikgcmV0dXJuIHN0YXRlLmluZGVudGVkO1xuICAgICAgaWYgKHN0YXRlLnByZXZUb2tlbiA9PSBcIm9wZXJhdG9yXCIgJiYgdGV4dEFmdGVyICE9IFwifVwiICYmIHN0YXRlLmNvbnRleHQudHlwZSAhPSBcIn1cIiB8fCBzdGF0ZS5wcmV2VG9rZW4gPT0gXCJ2YXJpYWJsZVwiICYmIGZpcnN0Q2hhciA9PSBcIi5cIiB8fCAoc3RhdGUucHJldlRva2VuID09IFwifVwiIHx8IHN0YXRlLnByZXZUb2tlbiA9PSBcIilcIikgJiYgZmlyc3RDaGFyID09IFwiLlwiKSByZXR1cm4gaW5kZW50VW5pdCAqIDIgKyBjdHguaW5kZW50ZWQ7XG4gICAgICBpZiAoY3R4LmFsaWduICYmIGN0eC50eXBlID09IFwifVwiKSByZXR1cm4gY3R4LmluZGVudGVkICsgKHN0YXRlLmNvbnRleHQudHlwZSA9PSAodGV4dEFmdGVyIHx8IFwiXCIpLmNoYXJBdCgwKSA/IDAgOiBpbmRlbnRVbml0KTtcbiAgICB9XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNsb3NlQnJhY2tldHM6IHtcbiAgICAgIGJyYWNrZXRzOiBbXCIoXCIsIFwiW1wiLCBcIntcIiwgXCInXCIsICdcIicsICdcIlwiXCInXVxuICAgIH1cbiAgfVxufSk7XG5leHBvcnQgY29uc3Qgc2hhZGVyID0gY2xpa2Uoe1xuICBuYW1lOiBcInNoYWRlclwiLFxuICBrZXl3b3Jkczogd29yZHMoXCJzYW1wbGVyMUQgc2FtcGxlcjJEIHNhbXBsZXIzRCBzYW1wbGVyQ3ViZSBcIiArIFwic2FtcGxlcjFEU2hhZG93IHNhbXBsZXIyRFNoYWRvdyBcIiArIFwiY29uc3QgYXR0cmlidXRlIHVuaWZvcm0gdmFyeWluZyBcIiArIFwiYnJlYWsgY29udGludWUgZGlzY2FyZCByZXR1cm4gXCIgKyBcImZvciB3aGlsZSBkbyBpZiBlbHNlIHN0cnVjdCBcIiArIFwiaW4gb3V0IGlub3V0XCIpLFxuICB0eXBlczogd29yZHMoXCJmbG9hdCBpbnQgYm9vbCB2b2lkIFwiICsgXCJ2ZWMyIHZlYzMgdmVjNCBpdmVjMiBpdmVjMyBpdmVjNCBidmVjMiBidmVjMyBidmVjNCBcIiArIFwibWF0MiBtYXQzIG1hdDRcIiksXG4gIGJsb2NrS2V5d29yZHM6IHdvcmRzKFwiZm9yIHdoaWxlIGRvIGlmIGVsc2Ugc3RydWN0XCIpLFxuICBidWlsdGluOiB3b3JkcyhcInJhZGlhbnMgZGVncmVlcyBzaW4gY29zIHRhbiBhc2luIGFjb3MgYXRhbiBcIiArIFwicG93IGV4cCBsb2cgZXhwMiBzcXJ0IGludmVyc2VzcXJ0IFwiICsgXCJhYnMgc2lnbiBmbG9vciBjZWlsIGZyYWN0IG1vZCBtaW4gbWF4IGNsYW1wIG1peCBzdGVwIHNtb290aHN0ZXAgXCIgKyBcImxlbmd0aCBkaXN0YW5jZSBkb3QgY3Jvc3Mgbm9ybWFsaXplIGZ0cmFuc2Zvcm0gZmFjZWZvcndhcmQgXCIgKyBcInJlZmxlY3QgcmVmcmFjdCBtYXRyaXhDb21wTXVsdCBcIiArIFwibGVzc1RoYW4gbGVzc1RoYW5FcXVhbCBncmVhdGVyVGhhbiBncmVhdGVyVGhhbkVxdWFsIFwiICsgXCJlcXVhbCBub3RFcXVhbCBhbnkgYWxsIG5vdCBcIiArIFwidGV4dHVyZTFEIHRleHR1cmUxRFByb2ogdGV4dHVyZTFETG9kIHRleHR1cmUxRFByb2pMb2QgXCIgKyBcInRleHR1cmUyRCB0ZXh0dXJlMkRQcm9qIHRleHR1cmUyRExvZCB0ZXh0dXJlMkRQcm9qTG9kIFwiICsgXCJ0ZXh0dXJlM0QgdGV4dHVyZTNEUHJvaiB0ZXh0dXJlM0RMb2QgdGV4dHVyZTNEUHJvakxvZCBcIiArIFwidGV4dHVyZUN1YmUgdGV4dHVyZUN1YmVMb2QgXCIgKyBcInNoYWRvdzFEIHNoYWRvdzJEIHNoYWRvdzFEUHJvaiBzaGFkb3cyRFByb2ogXCIgKyBcInNoYWRvdzFETG9kIHNoYWRvdzJETG9kIHNoYWRvdzFEUHJvakxvZCBzaGFkb3cyRFByb2pMb2QgXCIgKyBcImRGZHggZEZkeSBmd2lkdGggXCIgKyBcIm5vaXNlMSBub2lzZTIgbm9pc2UzIG5vaXNlNFwiKSxcbiAgYXRvbXM6IHdvcmRzKFwidHJ1ZSBmYWxzZSBcIiArIFwiZ2xfRnJhZ0NvbG9yIGdsX1NlY29uZGFyeUNvbG9yIGdsX05vcm1hbCBnbF9WZXJ0ZXggXCIgKyBcImdsX011bHRpVGV4Q29vcmQwIGdsX011bHRpVGV4Q29vcmQxIGdsX011bHRpVGV4Q29vcmQyIGdsX011bHRpVGV4Q29vcmQzIFwiICsgXCJnbF9NdWx0aVRleENvb3JkNCBnbF9NdWx0aVRleENvb3JkNSBnbF9NdWx0aVRleENvb3JkNiBnbF9NdWx0aVRleENvb3JkNyBcIiArIFwiZ2xfRm9nQ29vcmQgZ2xfUG9pbnRDb29yZCBcIiArIFwiZ2xfUG9zaXRpb24gZ2xfUG9pbnRTaXplIGdsX0NsaXBWZXJ0ZXggXCIgKyBcImdsX0Zyb250Q29sb3IgZ2xfQmFja0NvbG9yIGdsX0Zyb250U2Vjb25kYXJ5Q29sb3IgZ2xfQmFja1NlY29uZGFyeUNvbG9yIFwiICsgXCJnbF9UZXhDb29yZCBnbF9Gb2dGcmFnQ29vcmQgXCIgKyBcImdsX0ZyYWdDb29yZCBnbF9Gcm9udEZhY2luZyBcIiArIFwiZ2xfRnJhZ0RhdGEgZ2xfRnJhZ0RlcHRoIFwiICsgXCJnbF9Nb2RlbFZpZXdNYXRyaXggZ2xfUHJvamVjdGlvbk1hdHJpeCBnbF9Nb2RlbFZpZXdQcm9qZWN0aW9uTWF0cml4IFwiICsgXCJnbF9UZXh0dXJlTWF0cml4IGdsX05vcm1hbE1hdHJpeCBnbF9Nb2RlbFZpZXdNYXRyaXhJbnZlcnNlIFwiICsgXCJnbF9Qcm9qZWN0aW9uTWF0cml4SW52ZXJzZSBnbF9Nb2RlbFZpZXdQcm9qZWN0aW9uTWF0cml4SW52ZXJzZSBcIiArIFwiZ2xfVGV4dHVyZU1hdHJpeFRyYW5zcG9zZSBnbF9Nb2RlbFZpZXdNYXRyaXhJbnZlcnNlVHJhbnNwb3NlIFwiICsgXCJnbF9Qcm9qZWN0aW9uTWF0cml4SW52ZXJzZVRyYW5zcG9zZSBcIiArIFwiZ2xfTW9kZWxWaWV3UHJvamVjdGlvbk1hdHJpeEludmVyc2VUcmFuc3Bvc2UgXCIgKyBcImdsX1RleHR1cmVNYXRyaXhJbnZlcnNlVHJhbnNwb3NlIFwiICsgXCJnbF9Ob3JtYWxTY2FsZSBnbF9EZXB0aFJhbmdlIGdsX0NsaXBQbGFuZSBcIiArIFwiZ2xfUG9pbnQgZ2xfRnJvbnRNYXRlcmlhbCBnbF9CYWNrTWF0ZXJpYWwgZ2xfTGlnaHRTb3VyY2UgZ2xfTGlnaHRNb2RlbCBcIiArIFwiZ2xfRnJvbnRMaWdodE1vZGVsUHJvZHVjdCBnbF9CYWNrTGlnaHRNb2RlbFByb2R1Y3QgXCIgKyBcImdsX1RleHR1cmVDb2xvciBnbF9FeWVQbGFuZVMgZ2xfRXllUGxhbmVUIGdsX0V5ZVBsYW5lUiBnbF9FeWVQbGFuZVEgXCIgKyBcImdsX0ZvZ1BhcmFtZXRlcnMgXCIgKyBcImdsX01heExpZ2h0cyBnbF9NYXhDbGlwUGxhbmVzIGdsX01heFRleHR1cmVVbml0cyBnbF9NYXhUZXh0dXJlQ29vcmRzIFwiICsgXCJnbF9NYXhWZXJ0ZXhBdHRyaWJzIGdsX01heFZlcnRleFVuaWZvcm1Db21wb25lbnRzIGdsX01heFZhcnlpbmdGbG9hdHMgXCIgKyBcImdsX01heFZlcnRleFRleHR1cmVJbWFnZVVuaXRzIGdsX01heFRleHR1cmVJbWFnZVVuaXRzIFwiICsgXCJnbF9NYXhGcmFnbWVudFVuaWZvcm1Db21wb25lbnRzIGdsX01heENvbWJpbmVUZXh0dXJlSW1hZ2VVbml0cyBcIiArIFwiZ2xfTWF4RHJhd0J1ZmZlcnNcIiksXG4gIGluZGVudFN3aXRjaDogZmFsc2UsXG4gIGhvb2tzOiB7XG4gICAgXCIjXCI6IGNwcEhvb2tcbiAgfVxufSk7XG5leHBvcnQgY29uc3QgbmVzQyA9IGNsaWtlKHtcbiAgbmFtZTogXCJuZXNjXCIsXG4gIGtleXdvcmRzOiB3b3JkcyhjS2V5d29yZHMgKyBcIiBhcyBhdG9taWMgYXN5bmMgY2FsbCBjb21tYW5kIGNvbXBvbmVudCBjb21wb25lbnRzIGNvbmZpZ3VyYXRpb24gZXZlbnQgZ2VuZXJpYyBcIiArIFwiaW1wbGVtZW50YXRpb24gaW5jbHVkZXMgaW50ZXJmYWNlIG1vZHVsZSBuZXcgbm9yYWNlIG54X3N0cnVjdCBueF91bmlvbiBwb3N0IHByb3ZpZGVzIFwiICsgXCJzaWduYWwgdGFzayB1c2VzIGFic3RyYWN0IGV4dGVuZHNcIiksXG4gIHR5cGVzOiBjVHlwZXMsXG4gIGJsb2NrS2V5d29yZHM6IHdvcmRzKGNCbG9ja0tleXdvcmRzKSxcbiAgYXRvbXM6IHdvcmRzKFwibnVsbCB0cnVlIGZhbHNlXCIpLFxuICBob29rczoge1xuICAgIFwiI1wiOiBjcHBIb29rXG4gIH1cbn0pO1xuZXhwb3J0IGNvbnN0IG9iamVjdGl2ZUMgPSBjbGlrZSh7XG4gIG5hbWU6IFwib2JqZWN0aXZlY1wiLFxuICBrZXl3b3Jkczogd29yZHMoY0tleXdvcmRzICsgXCIgXCIgKyBvYmpDS2V5d29yZHMpLFxuICB0eXBlczogb2JqQ1R5cGVzLFxuICBidWlsdGluOiB3b3JkcyhvYmpDQnVpbHRpbnMpLFxuICBibG9ja0tleXdvcmRzOiB3b3JkcyhjQmxvY2tLZXl3b3JkcyArIFwiIEBzeW50aGVzaXplIEB0cnkgQGNhdGNoIEBmaW5hbGx5IEBhdXRvcmVsZWFzZXBvb2wgQHN5bmNocm9uaXplZFwiKSxcbiAgZGVmS2V5d29yZHM6IHdvcmRzKGNEZWZLZXl3b3JkcyArIFwiIEBpbnRlcmZhY2UgQGltcGxlbWVudGF0aW9uIEBwcm90b2NvbCBAY2xhc3NcIiksXG4gIGRvbnRJbmRlbnRTdGF0ZW1lbnRzOiAvXkAuKiQvLFxuICB0eXBlRmlyc3REZWZpbml0aW9uczogdHJ1ZSxcbiAgYXRvbXM6IHdvcmRzKFwiWUVTIE5PIE5VTEwgTmlsIG5pbCB0cnVlIGZhbHNlIG51bGxwdHJcIiksXG4gIGlzUmVzZXJ2ZWRJZGVudGlmaWVyOiBjSXNSZXNlcnZlZElkZW50aWZpZXIsXG4gIGhvb2tzOiB7XG4gICAgXCIjXCI6IGNwcEhvb2ssXG4gICAgXCIqXCI6IHBvaW50ZXJIb29rXG4gIH1cbn0pO1xuZXhwb3J0IGNvbnN0IG9iamVjdGl2ZUNwcCA9IGNsaWtlKHtcbiAgbmFtZTogXCJvYmplY3RpdmVjcHBcIixcbiAga2V5d29yZHM6IHdvcmRzKGNLZXl3b3JkcyArIFwiIFwiICsgb2JqQ0tleXdvcmRzICsgXCIgXCIgKyBjcHBLZXl3b3JkcyksXG4gIHR5cGVzOiBvYmpDVHlwZXMsXG4gIGJ1aWx0aW46IHdvcmRzKG9iakNCdWlsdGlucyksXG4gIGJsb2NrS2V5d29yZHM6IHdvcmRzKGNCbG9ja0tleXdvcmRzICsgXCIgQHN5bnRoZXNpemUgQHRyeSBAY2F0Y2ggQGZpbmFsbHkgQGF1dG9yZWxlYXNlcG9vbCBAc3luY2hyb25pemVkIGNsYXNzIHRyeSBjYXRjaFwiKSxcbiAgZGVmS2V5d29yZHM6IHdvcmRzKGNEZWZLZXl3b3JkcyArIFwiIEBpbnRlcmZhY2UgQGltcGxlbWVudGF0aW9uIEBwcm90b2NvbCBAY2xhc3MgY2xhc3MgbmFtZXNwYWNlXCIpLFxuICBkb250SW5kZW50U3RhdGVtZW50czogL15ALiokfF50ZW1wbGF0ZSQvLFxuICB0eXBlRmlyc3REZWZpbml0aW9uczogdHJ1ZSxcbiAgYXRvbXM6IHdvcmRzKFwiWUVTIE5PIE5VTEwgTmlsIG5pbCB0cnVlIGZhbHNlIG51bGxwdHJcIiksXG4gIGlzUmVzZXJ2ZWRJZGVudGlmaWVyOiBjSXNSZXNlcnZlZElkZW50aWZpZXIsXG4gIGhvb2tzOiB7XG4gICAgXCIjXCI6IGNwcEhvb2ssXG4gICAgXCIqXCI6IHBvaW50ZXJIb29rLFxuICAgIFwidVwiOiBjcHAxMVN0cmluZ0hvb2ssXG4gICAgXCJVXCI6IGNwcDExU3RyaW5nSG9vayxcbiAgICBcIkxcIjogY3BwMTFTdHJpbmdIb29rLFxuICAgIFwiUlwiOiBjcHAxMVN0cmluZ0hvb2ssXG4gICAgXCIwXCI6IGNwcDE0TGl0ZXJhbCxcbiAgICBcIjFcIjogY3BwMTRMaXRlcmFsLFxuICAgIFwiMlwiOiBjcHAxNExpdGVyYWwsXG4gICAgXCIzXCI6IGNwcDE0TGl0ZXJhbCxcbiAgICBcIjRcIjogY3BwMTRMaXRlcmFsLFxuICAgIFwiNVwiOiBjcHAxNExpdGVyYWwsXG4gICAgXCI2XCI6IGNwcDE0TGl0ZXJhbCxcbiAgICBcIjdcIjogY3BwMTRMaXRlcmFsLFxuICAgIFwiOFwiOiBjcHAxNExpdGVyYWwsXG4gICAgXCI5XCI6IGNwcDE0TGl0ZXJhbCxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUsIHN0eWxlKSB7XG4gICAgICBpZiAoc3R5bGUgPT0gXCJ2YXJpYWJsZVwiICYmIHN0cmVhbS5wZWVrKCkgPT0gXCIoXCIgJiYgKHN0YXRlLnByZXZUb2tlbiA9PSBcIjtcIiB8fCBzdGF0ZS5wcmV2VG9rZW4gPT0gbnVsbCB8fCBzdGF0ZS5wcmV2VG9rZW4gPT0gXCJ9XCIpICYmIGNwcExvb2tzTGlrZUNvbnN0cnVjdG9yKHN0cmVhbS5jdXJyZW50KCkpKSByZXR1cm4gXCJkZWZcIjtcbiAgICB9XG4gIH0sXG4gIG5hbWVzcGFjZVNlcGFyYXRvcjogXCI6OlwiXG59KTtcbmV4cG9ydCBjb25zdCBzcXVpcnJlbCA9IGNsaWtlKHtcbiAgbmFtZTogXCJzcXVpcnJlbFwiLFxuICBrZXl3b3Jkczogd29yZHMoXCJiYXNlIGJyZWFrIGNsb25lIGNvbnRpbnVlIGNvbnN0IGRlZmF1bHQgZGVsZXRlIGVudW0gZXh0ZW5kcyBmdW5jdGlvbiBpbiBjbGFzc1wiICsgXCIgZm9yZWFjaCBsb2NhbCByZXN1bWUgcmV0dXJuIHRoaXMgdGhyb3cgdHlwZW9mIHlpZWxkIGNvbnN0cnVjdG9yIGluc3RhbmNlb2Ygc3RhdGljXCIpLFxuICB0eXBlczogY1R5cGVzLFxuICBibG9ja0tleXdvcmRzOiB3b3JkcyhcImNhc2UgY2F0Y2ggY2xhc3MgZWxzZSBmb3IgZm9yZWFjaCBpZiBzd2l0Y2ggdHJ5IHdoaWxlXCIpLFxuICBkZWZLZXl3b3Jkczogd29yZHMoXCJmdW5jdGlvbiBsb2NhbCBjbGFzc1wiKSxcbiAgdHlwZUZpcnN0RGVmaW5pdGlvbnM6IHRydWUsXG4gIGF0b21zOiB3b3JkcyhcInRydWUgZmFsc2UgbnVsbFwiKSxcbiAgaG9va3M6IHtcbiAgICBcIiNcIjogY3BwSG9va1xuICB9XG59KTtcblxuLy8gQ2V5bG9uIFN0cmluZ3MgbmVlZCB0byBkZWFsIHdpdGggaW50ZXJwb2xhdGlvblxudmFyIHN0cmluZ1Rva2VuaXplciA9IG51bGw7XG5mdW5jdGlvbiB0b2tlbkNleWxvblN0cmluZyh0eXBlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKCFzdHJlYW0uZW9sKCkpIHtcbiAgICAgIGlmICghZXNjYXBlZCAmJiBzdHJlYW0ubWF0Y2goJ1wiJykgJiYgKHR5cGUgPT0gXCJzaW5nbGVcIiB8fCBzdHJlYW0ubWF0Y2goJ1wiXCInKSkpIHtcbiAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBpZiAoIWVzY2FwZWQgJiYgc3RyZWFtLm1hdGNoKCdgYCcpKSB7XG4gICAgICAgIHN0cmluZ1Rva2VuaXplciA9IHRva2VuQ2V5bG9uU3RyaW5nKHR5cGUpO1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIG5leHQgPSBzdHJlYW0ubmV4dCgpO1xuICAgICAgZXNjYXBlZCA9IHR5cGUgPT0gXCJzaW5nbGVcIiAmJiAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoZW5kKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5leHBvcnQgY29uc3QgY2V5bG9uID0gY2xpa2Uoe1xuICBuYW1lOiBcImNleWxvblwiLFxuICBrZXl3b3Jkczogd29yZHMoXCJhYnN0cmFjdHMgYWxpYXMgYXNzZW1ibHkgYXNzZXJ0IGFzc2lnbiBicmVhayBjYXNlIGNhdGNoIGNsYXNzIGNvbnRpbnVlIGR5bmFtaWMgZWxzZVwiICsgXCIgZXhpc3RzIGV4dGVuZHMgZmluYWxseSBmb3IgZnVuY3Rpb24gZ2l2ZW4gaWYgaW1wb3J0IGluIGludGVyZmFjZSBpcyBsZXQgbW9kdWxlIG5ld1wiICsgXCIgbm9uZW1wdHkgb2JqZWN0IG9mIG91dCBvdXRlciBwYWNrYWdlIHJldHVybiBzYXRpc2ZpZXMgc3VwZXIgc3dpdGNoIHRoZW4gdGhpcyB0aHJvd1wiICsgXCIgdHJ5IHZhbHVlIHZvaWQgd2hpbGVcIiksXG4gIHR5cGVzOiBmdW5jdGlvbiAod29yZCkge1xuICAgIC8vIEluIENleWxvbiBhbGwgaWRlbnRpZmllcnMgdGhhdCBzdGFydCB3aXRoIGFuIHVwcGVyY2FzZSBhcmUgdHlwZXNcbiAgICB2YXIgZmlyc3QgPSB3b3JkLmNoYXJBdCgwKTtcbiAgICByZXR1cm4gZmlyc3QgPT09IGZpcnN0LnRvVXBwZXJDYXNlKCkgJiYgZmlyc3QgIT09IGZpcnN0LnRvTG93ZXJDYXNlKCk7XG4gIH0sXG4gIGJsb2NrS2V5d29yZHM6IHdvcmRzKFwiY2FzZSBjYXRjaCBjbGFzcyBkeW5hbWljIGVsc2UgZmluYWxseSBmb3IgZnVuY3Rpb24gaWYgaW50ZXJmYWNlIG1vZHVsZSBuZXcgb2JqZWN0IHN3aXRjaCB0cnkgd2hpbGVcIiksXG4gIGRlZktleXdvcmRzOiB3b3JkcyhcImNsYXNzIGR5bmFtaWMgZnVuY3Rpb24gaW50ZXJmYWNlIG1vZHVsZSBvYmplY3QgcGFja2FnZSB2YWx1ZVwiKSxcbiAgYnVpbHRpbjogd29yZHMoXCJhYnN0cmFjdCBhY3R1YWwgYWxpYXNlZCBhbm5vdGF0aW9uIGJ5IGRlZmF1bHQgZGVwcmVjYXRlZCBkb2MgZmluYWwgZm9ybWFsIGxhdGUgbGljZW5zZVwiICsgXCIgbmF0aXZlIG9wdGlvbmFsIHNlYWxlZCBzZWUgc2VyaWFsaXphYmxlIHNoYXJlZCBzdXBwcmVzc1dhcm5pbmdzIHRhZ2dlZCB0aHJvd3MgdmFyaWFibGVcIiksXG4gIGlzUHVuY3R1YXRpb25DaGFyOiAvW1xcW1xcXXt9XFwoXFwpLDtcXDpcXC5gXS8sXG4gIGlzT3BlcmF0b3JDaGFyOiAvWytcXC0qJiU9PD4hP3xefjpcXC9dLyxcbiAgbnVtYmVyU3RhcnQ6IC9bXFxkIyRdLyxcbiAgbnVtYmVyOiAvXig/OiNbXFxkYS1mQS1GX10rfFxcJFswMV9dK3xbXFxkX10rW2tNR1RQbXVucGZdP3xbXFxkX10rXFwuW1xcZF9dKyg/OltlRV1bLStdP1xcZCt8W2tNR1RQbXVucGZdfCl8KS9pLFxuICBtdWx0aUxpbmVTdHJpbmdzOiB0cnVlLFxuICB0eXBlRmlyc3REZWZpbml0aW9uczogdHJ1ZSxcbiAgYXRvbXM6IHdvcmRzKFwidHJ1ZSBmYWxzZSBudWxsIGxhcmdlciBzbWFsbGVyIGVxdWFsIGVtcHR5IGZpbmlzaGVkXCIpLFxuICBpbmRlbnRTd2l0Y2g6IGZhbHNlLFxuICBzdHlsZURlZnM6IGZhbHNlLFxuICBob29rczoge1xuICAgIFwiQFwiOiBmdW5jdGlvbiAoc3RyZWFtKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICAgICAgcmV0dXJuIFwibWV0YVwiO1xuICAgIH0sXG4gICAgJ1wiJzogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5DZXlsb25TdHJpbmcoc3RyZWFtLm1hdGNoKCdcIlwiJykgPyBcInRyaXBsZVwiIDogXCJzaW5nbGVcIik7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfSxcbiAgICAnYCc6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICBpZiAoIXN0cmluZ1Rva2VuaXplciB8fCAhc3RyZWFtLm1hdGNoKCdgJykpIHJldHVybiBmYWxzZTtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gc3RyaW5nVG9rZW5pemVyO1xuICAgICAgc3RyaW5nVG9rZW5pemVyID0gbnVsbDtcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9LFxuICAgIFwiJ1wiOiBmdW5jdGlvbiAoc3RyZWFtKSB7XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eKFxcXFxbXidcXHNdK3xbXlxcXFwnXSknLykpIHJldHVybiBcInN0cmluZy5zcGVjaWFsXCI7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXFx4YTEtXFx1ZmZmZl0vKTtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9LFxuICAgIHRva2VuOiBmdW5jdGlvbiAoX3N0cmVhbSwgc3RhdGUsIHN0eWxlKSB7XG4gICAgICBpZiAoKHN0eWxlID09IFwidmFyaWFibGVcIiB8fCBzdHlsZSA9PSBcInR5cGVcIikgJiYgc3RhdGUucHJldlRva2VuID09IFwiLlwiKSB7XG4gICAgICAgIHJldHVybiBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgICB9XG4gICAgfVxuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjbG9zZUJyYWNrZXRzOiB7XG4gICAgICBicmFja2V0czogW1wiKFwiLCBcIltcIiwgXCJ7XCIsIFwiJ1wiLCAnXCInLCAnXCJcIlwiJ11cbiAgICB9XG4gIH1cbn0pO1xuZnVuY3Rpb24gcHVzaEludGVycG9sYXRpb25TdGFjayhzdGF0ZSkge1xuICAoc3RhdGUuaW50ZXJwb2xhdGlvblN0YWNrIHx8IChzdGF0ZS5pbnRlcnBvbGF0aW9uU3RhY2sgPSBbXSkpLnB1c2goc3RhdGUudG9rZW5pemUpO1xufVxuZnVuY3Rpb24gcG9wSW50ZXJwb2xhdGlvblN0YWNrKHN0YXRlKSB7XG4gIHJldHVybiAoc3RhdGUuaW50ZXJwb2xhdGlvblN0YWNrIHx8IChzdGF0ZS5pbnRlcnBvbGF0aW9uU3RhY2sgPSBbXSkpLnBvcCgpO1xufVxuZnVuY3Rpb24gc2l6ZUludGVycG9sYXRpb25TdGFjayhzdGF0ZSkge1xuICByZXR1cm4gc3RhdGUuaW50ZXJwb2xhdGlvblN0YWNrID8gc3RhdGUuaW50ZXJwb2xhdGlvblN0YWNrLmxlbmd0aCA6IDA7XG59XG5mdW5jdGlvbiB0b2tlbkRhcnRTdHJpbmcocXVvdGUsIHN0cmVhbSwgc3RhdGUsIHJhdykge1xuICB2YXIgdHJpcGxlUXVvdGVkID0gZmFsc2U7XG4gIGlmIChzdHJlYW0uZWF0KHF1b3RlKSkge1xuICAgIGlmIChzdHJlYW0uZWF0KHF1b3RlKSkgdHJpcGxlUXVvdGVkID0gdHJ1ZTtlbHNlIHJldHVybiBcInN0cmluZ1wiOyAvL2VtcHR5IHN0cmluZ1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuU3RyaW5nSGVscGVyKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlO1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICBpZiAoIXJhdyAmJiAhZXNjYXBlZCAmJiBzdHJlYW0ucGVlaygpID09IFwiJFwiKSB7XG4gICAgICAgIHB1c2hJbnRlcnBvbGF0aW9uU3RhY2soc3RhdGUpO1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuSW50ZXJwb2xhdGlvbjtcbiAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICB9XG4gICAgICB2YXIgbmV4dCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCAmJiAoIXRyaXBsZVF1b3RlZCB8fCBzdHJlYW0ubWF0Y2gocXVvdGUgKyBxdW90ZSkpKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIXJhdyAmJiAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfVxuICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nSGVscGVyO1xuICByZXR1cm4gdG9rZW5TdHJpbmdIZWxwZXIoc3RyZWFtLCBzdGF0ZSk7XG59XG5mdW5jdGlvbiB0b2tlbkludGVycG9sYXRpb24oc3RyZWFtLCBzdGF0ZSkge1xuICBzdHJlYW0uZWF0KFwiJFwiKTtcbiAgaWYgKHN0cmVhbS5lYXQoXCJ7XCIpKSB7XG4gICAgLy8gbGV0IGNsaWtlIGhhbmRsZSB0aGUgY29udGVudCBvZiAkey4uLn0sXG4gICAgLy8gd2UgdGFrZSBvdmVyIGFnYWluIHdoZW4gXCJ9XCIgYXBwZWFycyAoc2VlIGhvb2tzKS5cbiAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gIH0gZWxzZSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkludGVycG9sYXRpb25JZGVudGlmaWVyO1xuICB9XG4gIHJldHVybiBudWxsO1xufVxuZnVuY3Rpb24gdG9rZW5JbnRlcnBvbGF0aW9uSWRlbnRpZmllcihzdHJlYW0sIHN0YXRlKSB7XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcd19dLyk7XG4gIHN0YXRlLnRva2VuaXplID0gcG9wSW50ZXJwb2xhdGlvblN0YWNrKHN0YXRlKTtcbiAgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cbmV4cG9ydCBjb25zdCBkYXJ0ID0gY2xpa2Uoe1xuICBuYW1lOiBcImRhcnRcIixcbiAga2V5d29yZHM6IHdvcmRzKFwidGhpcyBzdXBlciBzdGF0aWMgZmluYWwgY29uc3QgYWJzdHJhY3QgY2xhc3MgZXh0ZW5kcyBleHRlcm5hbCBmYWN0b3J5IFwiICsgXCJpbXBsZW1lbnRzIG1peGluIGdldCBuYXRpdmUgc2V0IHR5cGVkZWYgd2l0aCBlbnVtIHRocm93IHJldGhyb3cgYXNzZXJ0IGJyZWFrIGNhc2UgXCIgKyBcImNvbnRpbnVlIGRlZmF1bHQgaW4gcmV0dXJuIG5ldyBkZWZlcnJlZCBhc3luYyBhd2FpdCBjb3ZhcmlhbnQgdHJ5IGNhdGNoIGZpbmFsbHkgXCIgKyBcImRvIGVsc2UgZm9yIGlmIHN3aXRjaCB3aGlsZSBpbXBvcnQgbGlicmFyeSBleHBvcnQgcGFydCBvZiBzaG93IGhpZGUgaXMgYXMgZXh0ZW5zaW9uIFwiICsgXCJvbiB5aWVsZCBsYXRlIHJlcXVpcmVkIHNlYWxlZCBiYXNlIGludGVyZmFjZSB3aGVuIGlubGluZVwiKSxcbiAgYmxvY2tLZXl3b3Jkczogd29yZHMoXCJ0cnkgY2F0Y2ggZmluYWxseSBkbyBlbHNlIGZvciBpZiBzd2l0Y2ggd2hpbGVcIiksXG4gIGJ1aWx0aW46IHdvcmRzKFwidm9pZCBib29sIG51bSBpbnQgZG91YmxlIGR5bmFtaWMgdmFyIFN0cmluZyBOdWxsIE5ldmVyXCIpLFxuICBhdG9tczogd29yZHMoXCJ0cnVlIGZhbHNlIG51bGxcIiksXG4gIC8vIGNsaWtlIG51bWJlcnMgd2l0aG91dCB0aGUgc3VmZml4ZXMsIGFuZCB3aXRoICdfJyBzZXBhcmF0b3JzLlxuICBudW1iZXI6IC9eKD86MHhbYS1mXFxkX10rfCg/OltcXGRfXStcXC4/W1xcZF9dKnxcXC5bXFxkX10rKSg/OmVbLStdP1tcXGRfXSspPykvaSxcbiAgaG9va3M6IHtcbiAgICBcIkBcIjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX1xcLl0vKTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9LFxuICAgIC8vIGN1c3RvbSBzdHJpbmcgaGFuZGxpbmcgdG8gZGVhbCB3aXRoIHRyaXBsZS1xdW90ZWQgc3RyaW5ncyBhbmQgc3RyaW5nIGludGVycG9sYXRpb25cbiAgICBcIidcIjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIHJldHVybiB0b2tlbkRhcnRTdHJpbmcoXCInXCIsIHN0cmVhbSwgc3RhdGUsIGZhbHNlKTtcbiAgICB9LFxuICAgIFwiXFxcIlwiOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgcmV0dXJuIHRva2VuRGFydFN0cmluZyhcIlxcXCJcIiwgc3RyZWFtLCBzdGF0ZSwgZmFsc2UpO1xuICAgIH0sXG4gICAgXCJyXCI6IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgcGVlayA9IHN0cmVhbS5wZWVrKCk7XG4gICAgICBpZiAocGVlayA9PSBcIidcIiB8fCBwZWVrID09IFwiXFxcIlwiKSB7XG4gICAgICAgIHJldHVybiB0b2tlbkRhcnRTdHJpbmcoc3RyZWFtLm5leHQoKSwgc3RyZWFtLCBzdGF0ZSwgdHJ1ZSk7XG4gICAgICB9XG4gICAgICByZXR1cm4gZmFsc2U7XG4gICAgfSxcbiAgICBcIn1cIjogZnVuY3Rpb24gKF9zdHJlYW0sIHN0YXRlKSB7XG4gICAgICAvLyBcIn1cIiBpcyBlbmQgb2YgaW50ZXJwb2xhdGlvbiwgaWYgaW50ZXJwb2xhdGlvbiBzdGFjayBpcyBub24tZW1wdHlcbiAgICAgIGlmIChzaXplSW50ZXJwb2xhdGlvblN0YWNrKHN0YXRlKSA+IDApIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSBwb3BJbnRlcnBvbGF0aW9uU3RhY2soc3RhdGUpO1xuICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgIH1cbiAgICAgIHJldHVybiBmYWxzZTtcbiAgICB9LFxuICAgIFwiL1wiOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgaWYgKCFzdHJlYW0uZWF0KFwiKlwiKSkgcmV0dXJuIGZhbHNlO1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbk5lc3RlZENvbW1lbnQoMSk7XG4gICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfSxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgXywgc3R5bGUpIHtcbiAgICAgIGlmIChzdHlsZSA9PSBcInZhcmlhYmxlXCIpIHtcbiAgICAgICAgLy8gQXNzdW1lIHVwcGVyY2FzZSBzeW1ib2xzIGFyZSBjbGFzc2VzXG4gICAgICAgIHZhciBpc1VwcGVyID0gUmVnRXhwKCdeW18kXSpbQS1aXVthLXpBLVowLTlfJF0qJCcsICdnJyk7XG4gICAgICAgIGlmIChpc1VwcGVyLnRlc3Qoc3RyZWFtLmN1cnJlbnQoKSkpIHtcbiAgICAgICAgICByZXR1cm4gJ3R5cGUnO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICB9XG59KTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9