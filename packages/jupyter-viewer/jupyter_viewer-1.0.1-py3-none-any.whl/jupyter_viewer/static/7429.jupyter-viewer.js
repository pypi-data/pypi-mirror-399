"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7429],{

/***/ 17429
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ttcn: () => (/* binding */ ttcn)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
const parserConfig = {
  name: "ttcn",
  keywords: words("activate address alive all alt altstep and and4b any" + " break case component const continue control deactivate" + " display do else encode enumerated except exception" + " execute extends extension external for from function" + " goto group if import in infinity inout interleave" + " label language length log match message mixed mod" + " modifies module modulepar mtc noblock not not4b nowait" + " of on optional or or4b out override param pattern port" + " procedure record recursive rem repeat return runs select" + " self sender set signature system template testcase to" + " type union value valueof var variant while with xor xor4b"),
  builtin: words("bit2hex bit2int bit2oct bit2str char2int char2oct encvalue" + " decomp decvalue float2int float2str hex2bit hex2int" + " hex2oct hex2str int2bit int2char int2float int2hex" + " int2oct int2str int2unichar isbound ischosen ispresent" + " isvalue lengthof log2str oct2bit oct2char oct2hex oct2int" + " oct2str regexp replace rnd sizeof str2bit str2float" + " str2hex str2int str2oct substr unichar2int unichar2char" + " enum2int"),
  types: words("anytype bitstring boolean char charstring default float" + " hexstring integer objid octetstring universal verdicttype timer"),
  timerOps: words("read running start stop timeout"),
  portOps: words("call catch check clear getcall getreply halt raise receive" + " reply send trigger"),
  configOps: words("create connect disconnect done kill killed map unmap"),
  verdictOps: words("getverdict setverdict"),
  sutOps: words("action"),
  functionOps: words("apply derefers refers"),
  verdictConsts: words("error fail inconc none pass"),
  booleanConsts: words("true false"),
  otherConsts: words("null NULL omit"),
  visibilityModifiers: words("private public friend"),
  templateMatch: words("complement ifpresent subset superset permutation"),
  multiLineStrings: true
};
var wordList = [];
function add(obj) {
  if (obj) for (var prop in obj) if (obj.hasOwnProperty(prop)) wordList.push(prop);
}
add(parserConfig.keywords);
add(parserConfig.builtin);
add(parserConfig.timerOps);
add(parserConfig.portOps);
var keywords = parserConfig.keywords || {},
  builtin = parserConfig.builtin || {},
  timerOps = parserConfig.timerOps || {},
  portOps = parserConfig.portOps || {},
  configOps = parserConfig.configOps || {},
  verdictOps = parserConfig.verdictOps || {},
  sutOps = parserConfig.sutOps || {},
  functionOps = parserConfig.functionOps || {},
  verdictConsts = parserConfig.verdictConsts || {},
  booleanConsts = parserConfig.booleanConsts || {},
  otherConsts = parserConfig.otherConsts || {},
  types = parserConfig.types || {},
  visibilityModifiers = parserConfig.visibilityModifiers || {},
  templateMatch = parserConfig.templateMatch || {},
  multiLineStrings = parserConfig.multiLineStrings,
  indentStatements = parserConfig.indentStatements !== false;
var isOperatorChar = /[+\-*&@=<>!\/]/;
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\[\]{}\(\),;\\:\?\.]/.test(ch)) {
    curPunc = ch;
    return "punctuation";
  }
  if (ch == "#") {
    stream.skipToEnd();
    return "atom";
  }
  if (ch == "%") {
    stream.eatWhile(/\b/);
    return "atom";
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
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
    if (ch == "@") {
      if (stream.match("try") || stream.match("catch") || stream.match("lazy")) {
        return "keyword";
      }
    }
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  stream.eatWhile(/[\w\$_\xa1-\uffff]/);
  var cur = stream.current();
  if (keywords.propertyIsEnumerable(cur)) return "keyword";
  if (builtin.propertyIsEnumerable(cur)) return "builtin";
  if (timerOps.propertyIsEnumerable(cur)) return "def";
  if (configOps.propertyIsEnumerable(cur)) return "def";
  if (verdictOps.propertyIsEnumerable(cur)) return "def";
  if (portOps.propertyIsEnumerable(cur)) return "def";
  if (sutOps.propertyIsEnumerable(cur)) return "def";
  if (functionOps.propertyIsEnumerable(cur)) return "def";
  if (verdictConsts.propertyIsEnumerable(cur)) return "string";
  if (booleanConsts.propertyIsEnumerable(cur)) return "string";
  if (otherConsts.propertyIsEnumerable(cur)) return "string";
  if (types.propertyIsEnumerable(cur)) return "typeName.standard";
  if (visibilityModifiers.propertyIsEnumerable(cur)) return "modifier";
  if (templateMatch.propertyIsEnumerable(cur)) return "atom";
  return "variable";
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        var afterQuote = stream.peek();
        //look if the character after the quote is like the B in '10100010'B
        if (afterQuote) {
          afterQuote = afterQuote.toLowerCase();
          if (afterQuote == "b" || afterQuote == "h" || afterQuote == "o") stream.next();
        }
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
function Context(indented, column, type, align, prev) {
  this.indented = indented;
  this.column = column;
  this.type = type;
  this.align = align;
  this.prev = prev;
}
function pushContext(state, col, type) {
  var indent = state.indented;
  if (state.context && state.context.type == "statement") indent = state.context.indented;
  return state.context = new Context(indent, col, type, null, state.context);
}
function popContext(state) {
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

//Interface
const ttcn = {
  name: "ttcn",
  startState: function () {
    return {
      tokenize: null,
      context: new Context(0, 0, "top", false),
      indented: 0,
      startOfLine: true
    };
  },
  token: function (stream, state) {
    var ctx = state.context;
    if (stream.sol()) {
      if (ctx.align == null) ctx.align = false;
      state.indented = stream.indentation();
      state.startOfLine = true;
    }
    if (stream.eatSpace()) return null;
    curPunc = null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment") return style;
    if (ctx.align == null) ctx.align = true;
    if ((curPunc == ";" || curPunc == ":" || curPunc == ",") && ctx.type == "statement") {
      popContext(state);
    } else if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "}") {
      while (ctx.type == "statement") ctx = popContext(state);
      if (ctx.type == "}") ctx = popContext(state);
      while (ctx.type == "statement") ctx = popContext(state);
    } else if (curPunc == ctx.type) popContext(state);else if (indentStatements && ((ctx.type == "}" || ctx.type == "top") && curPunc != ';' || ctx.type == "statement" && curPunc == "newstatement")) pushContext(state, stream.column(), "statement");
    state.startOfLine = false;
    return style;
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      line: "//",
      block: {
        open: "/*",
        close: "*/"
      }
    },
    autocomplete: wordList
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzQyOS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS90dGNuLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIHdvcmRzKHN0cikge1xuICB2YXIgb2JqID0ge30sXG4gICAgd29yZHMgPSBzdHIuc3BsaXQoXCIgXCIpO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHdvcmRzLmxlbmd0aDsgKytpKSBvYmpbd29yZHNbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIG9iajtcbn1cbmNvbnN0IHBhcnNlckNvbmZpZyA9IHtcbiAgbmFtZTogXCJ0dGNuXCIsXG4gIGtleXdvcmRzOiB3b3JkcyhcImFjdGl2YXRlIGFkZHJlc3MgYWxpdmUgYWxsIGFsdCBhbHRzdGVwIGFuZCBhbmQ0YiBhbnlcIiArIFwiIGJyZWFrIGNhc2UgY29tcG9uZW50IGNvbnN0IGNvbnRpbnVlIGNvbnRyb2wgZGVhY3RpdmF0ZVwiICsgXCIgZGlzcGxheSBkbyBlbHNlIGVuY29kZSBlbnVtZXJhdGVkIGV4Y2VwdCBleGNlcHRpb25cIiArIFwiIGV4ZWN1dGUgZXh0ZW5kcyBleHRlbnNpb24gZXh0ZXJuYWwgZm9yIGZyb20gZnVuY3Rpb25cIiArIFwiIGdvdG8gZ3JvdXAgaWYgaW1wb3J0IGluIGluZmluaXR5IGlub3V0IGludGVybGVhdmVcIiArIFwiIGxhYmVsIGxhbmd1YWdlIGxlbmd0aCBsb2cgbWF0Y2ggbWVzc2FnZSBtaXhlZCBtb2RcIiArIFwiIG1vZGlmaWVzIG1vZHVsZSBtb2R1bGVwYXIgbXRjIG5vYmxvY2sgbm90IG5vdDRiIG5vd2FpdFwiICsgXCIgb2Ygb24gb3B0aW9uYWwgb3Igb3I0YiBvdXQgb3ZlcnJpZGUgcGFyYW0gcGF0dGVybiBwb3J0XCIgKyBcIiBwcm9jZWR1cmUgcmVjb3JkIHJlY3Vyc2l2ZSByZW0gcmVwZWF0IHJldHVybiBydW5zIHNlbGVjdFwiICsgXCIgc2VsZiBzZW5kZXIgc2V0IHNpZ25hdHVyZSBzeXN0ZW0gdGVtcGxhdGUgdGVzdGNhc2UgdG9cIiArIFwiIHR5cGUgdW5pb24gdmFsdWUgdmFsdWVvZiB2YXIgdmFyaWFudCB3aGlsZSB3aXRoIHhvciB4b3I0YlwiKSxcbiAgYnVpbHRpbjogd29yZHMoXCJiaXQyaGV4IGJpdDJpbnQgYml0Mm9jdCBiaXQyc3RyIGNoYXIyaW50IGNoYXIyb2N0IGVuY3ZhbHVlXCIgKyBcIiBkZWNvbXAgZGVjdmFsdWUgZmxvYXQyaW50IGZsb2F0MnN0ciBoZXgyYml0IGhleDJpbnRcIiArIFwiIGhleDJvY3QgaGV4MnN0ciBpbnQyYml0IGludDJjaGFyIGludDJmbG9hdCBpbnQyaGV4XCIgKyBcIiBpbnQyb2N0IGludDJzdHIgaW50MnVuaWNoYXIgaXNib3VuZCBpc2Nob3NlbiBpc3ByZXNlbnRcIiArIFwiIGlzdmFsdWUgbGVuZ3Rob2YgbG9nMnN0ciBvY3QyYml0IG9jdDJjaGFyIG9jdDJoZXggb2N0MmludFwiICsgXCIgb2N0MnN0ciByZWdleHAgcmVwbGFjZSBybmQgc2l6ZW9mIHN0cjJiaXQgc3RyMmZsb2F0XCIgKyBcIiBzdHIyaGV4IHN0cjJpbnQgc3RyMm9jdCBzdWJzdHIgdW5pY2hhcjJpbnQgdW5pY2hhcjJjaGFyXCIgKyBcIiBlbnVtMmludFwiKSxcbiAgdHlwZXM6IHdvcmRzKFwiYW55dHlwZSBiaXRzdHJpbmcgYm9vbGVhbiBjaGFyIGNoYXJzdHJpbmcgZGVmYXVsdCBmbG9hdFwiICsgXCIgaGV4c3RyaW5nIGludGVnZXIgb2JqaWQgb2N0ZXRzdHJpbmcgdW5pdmVyc2FsIHZlcmRpY3R0eXBlIHRpbWVyXCIpLFxuICB0aW1lck9wczogd29yZHMoXCJyZWFkIHJ1bm5pbmcgc3RhcnQgc3RvcCB0aW1lb3V0XCIpLFxuICBwb3J0T3BzOiB3b3JkcyhcImNhbGwgY2F0Y2ggY2hlY2sgY2xlYXIgZ2V0Y2FsbCBnZXRyZXBseSBoYWx0IHJhaXNlIHJlY2VpdmVcIiArIFwiIHJlcGx5IHNlbmQgdHJpZ2dlclwiKSxcbiAgY29uZmlnT3BzOiB3b3JkcyhcImNyZWF0ZSBjb25uZWN0IGRpc2Nvbm5lY3QgZG9uZSBraWxsIGtpbGxlZCBtYXAgdW5tYXBcIiksXG4gIHZlcmRpY3RPcHM6IHdvcmRzKFwiZ2V0dmVyZGljdCBzZXR2ZXJkaWN0XCIpLFxuICBzdXRPcHM6IHdvcmRzKFwiYWN0aW9uXCIpLFxuICBmdW5jdGlvbk9wczogd29yZHMoXCJhcHBseSBkZXJlZmVycyByZWZlcnNcIiksXG4gIHZlcmRpY3RDb25zdHM6IHdvcmRzKFwiZXJyb3IgZmFpbCBpbmNvbmMgbm9uZSBwYXNzXCIpLFxuICBib29sZWFuQ29uc3RzOiB3b3JkcyhcInRydWUgZmFsc2VcIiksXG4gIG90aGVyQ29uc3RzOiB3b3JkcyhcIm51bGwgTlVMTCBvbWl0XCIpLFxuICB2aXNpYmlsaXR5TW9kaWZpZXJzOiB3b3JkcyhcInByaXZhdGUgcHVibGljIGZyaWVuZFwiKSxcbiAgdGVtcGxhdGVNYXRjaDogd29yZHMoXCJjb21wbGVtZW50IGlmcHJlc2VudCBzdWJzZXQgc3VwZXJzZXQgcGVybXV0YXRpb25cIiksXG4gIG11bHRpTGluZVN0cmluZ3M6IHRydWVcbn07XG52YXIgd29yZExpc3QgPSBbXTtcbmZ1bmN0aW9uIGFkZChvYmopIHtcbiAgaWYgKG9iaikgZm9yICh2YXIgcHJvcCBpbiBvYmopIGlmIChvYmouaGFzT3duUHJvcGVydHkocHJvcCkpIHdvcmRMaXN0LnB1c2gocHJvcCk7XG59XG5hZGQocGFyc2VyQ29uZmlnLmtleXdvcmRzKTtcbmFkZChwYXJzZXJDb25maWcuYnVpbHRpbik7XG5hZGQocGFyc2VyQ29uZmlnLnRpbWVyT3BzKTtcbmFkZChwYXJzZXJDb25maWcucG9ydE9wcyk7XG52YXIga2V5d29yZHMgPSBwYXJzZXJDb25maWcua2V5d29yZHMgfHwge30sXG4gIGJ1aWx0aW4gPSBwYXJzZXJDb25maWcuYnVpbHRpbiB8fCB7fSxcbiAgdGltZXJPcHMgPSBwYXJzZXJDb25maWcudGltZXJPcHMgfHwge30sXG4gIHBvcnRPcHMgPSBwYXJzZXJDb25maWcucG9ydE9wcyB8fCB7fSxcbiAgY29uZmlnT3BzID0gcGFyc2VyQ29uZmlnLmNvbmZpZ09wcyB8fCB7fSxcbiAgdmVyZGljdE9wcyA9IHBhcnNlckNvbmZpZy52ZXJkaWN0T3BzIHx8IHt9LFxuICBzdXRPcHMgPSBwYXJzZXJDb25maWcuc3V0T3BzIHx8IHt9LFxuICBmdW5jdGlvbk9wcyA9IHBhcnNlckNvbmZpZy5mdW5jdGlvbk9wcyB8fCB7fSxcbiAgdmVyZGljdENvbnN0cyA9IHBhcnNlckNvbmZpZy52ZXJkaWN0Q29uc3RzIHx8IHt9LFxuICBib29sZWFuQ29uc3RzID0gcGFyc2VyQ29uZmlnLmJvb2xlYW5Db25zdHMgfHwge30sXG4gIG90aGVyQ29uc3RzID0gcGFyc2VyQ29uZmlnLm90aGVyQ29uc3RzIHx8IHt9LFxuICB0eXBlcyA9IHBhcnNlckNvbmZpZy50eXBlcyB8fCB7fSxcbiAgdmlzaWJpbGl0eU1vZGlmaWVycyA9IHBhcnNlckNvbmZpZy52aXNpYmlsaXR5TW9kaWZpZXJzIHx8IHt9LFxuICB0ZW1wbGF0ZU1hdGNoID0gcGFyc2VyQ29uZmlnLnRlbXBsYXRlTWF0Y2ggfHwge30sXG4gIG11bHRpTGluZVN0cmluZ3MgPSBwYXJzZXJDb25maWcubXVsdGlMaW5lU3RyaW5ncyxcbiAgaW5kZW50U3RhdGVtZW50cyA9IHBhcnNlckNvbmZpZy5pbmRlbnRTdGF0ZW1lbnRzICE9PSBmYWxzZTtcbnZhciBpc09wZXJhdG9yQ2hhciA9IC9bK1xcLSomQD08PiFcXC9dLztcbnZhciBjdXJQdW5jO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGNoID09ICdcIicgfHwgY2ggPT0gXCInXCIpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKC9bXFxbXFxde31cXChcXCksO1xcXFw6XFw/XFwuXS8udGVzdChjaCkpIHtcbiAgICBjdXJQdW5jID0gY2g7XG4gICAgcmV0dXJuIFwicHVuY3R1YXRpb25cIjtcbiAgfVxuICBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiYXRvbVwiO1xuICB9XG4gIGlmIChjaCA9PSBcIiVcIikge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvXFxiLyk7XG4gICAgcmV0dXJuIFwiYXRvbVwiO1xuICB9XG4gIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLl0vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuICBpZiAoY2ggPT0gXCIvXCIpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChcIipcIikpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Db21tZW50O1xuICAgICAgcmV0dXJuIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXQoXCIvXCIpKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICB9XG4gIGlmIChpc09wZXJhdG9yQ2hhci50ZXN0KGNoKSkge1xuICAgIGlmIChjaCA9PSBcIkBcIikge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaChcInRyeVwiKSB8fCBzdHJlYW0ubWF0Y2goXCJjYXRjaFwiKSB8fCBzdHJlYW0ubWF0Y2goXCJsYXp5XCIpKSB7XG4gICAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICAgIH1cbiAgICB9XG4gICAgc3RyZWFtLmVhdFdoaWxlKGlzT3BlcmF0b3JDaGFyKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF9cXHhhMS1cXHVmZmZmXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImtleXdvcmRcIjtcbiAgaWYgKGJ1aWx0aW4ucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYnVpbHRpblwiO1xuICBpZiAodGltZXJPcHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiZGVmXCI7XG4gIGlmIChjb25maWdPcHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiZGVmXCI7XG4gIGlmICh2ZXJkaWN0T3BzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImRlZlwiO1xuICBpZiAocG9ydE9wcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSByZXR1cm4gXCJkZWZcIjtcbiAgaWYgKHN1dE9wcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSByZXR1cm4gXCJkZWZcIjtcbiAgaWYgKGZ1bmN0aW9uT3BzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImRlZlwiO1xuICBpZiAodmVyZGljdENvbnN0cy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSByZXR1cm4gXCJzdHJpbmdcIjtcbiAgaWYgKGJvb2xlYW5Db25zdHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwic3RyaW5nXCI7XG4gIGlmIChvdGhlckNvbnN0cy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSByZXR1cm4gXCJzdHJpbmdcIjtcbiAgaWYgKHR5cGVzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcInR5cGVOYW1lLnN0YW5kYXJkXCI7XG4gIGlmICh2aXNpYmlsaXR5TW9kaWZpZXJzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcIm1vZGlmaWVyXCI7XG4gIGlmICh0ZW1wbGF0ZU1hdGNoLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImF0b21cIjtcbiAgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgdmFyIGFmdGVyUXVvdGUgPSBzdHJlYW0ucGVlaygpO1xuICAgICAgICAvL2xvb2sgaWYgdGhlIGNoYXJhY3RlciBhZnRlciB0aGUgcXVvdGUgaXMgbGlrZSB0aGUgQiBpbiAnMTAxMDAwMTAnQlxuICAgICAgICBpZiAoYWZ0ZXJRdW90ZSkge1xuICAgICAgICAgIGFmdGVyUXVvdGUgPSBhZnRlclF1b3RlLnRvTG93ZXJDYXNlKCk7XG4gICAgICAgICAgaWYgKGFmdGVyUXVvdGUgPT0gXCJiXCIgfHwgYWZ0ZXJRdW90ZSA9PSBcImhcIiB8fCBhZnRlclF1b3RlID09IFwib1wiKSBzdHJlYW0ubmV4dCgpO1xuICAgICAgICB9XG4gICAgICAgIGVuZCA9IHRydWU7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIG5leHQgPT0gXCJcXFxcXCI7XG4gICAgfVxuICAgIGlmIChlbmQgfHwgIShlc2NhcGVkIHx8IG11bHRpTGluZVN0cmluZ3MpKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5mdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gQ29udGV4dChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBhbGlnbiwgcHJldikge1xuICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMucHJldiA9IHByZXY7XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlKSB7XG4gIHZhciBpbmRlbnQgPSBzdGF0ZS5pbmRlbnRlZDtcbiAgaWYgKHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC50eXBlID09IFwic3RhdGVtZW50XCIpIGluZGVudCA9IHN0YXRlLmNvbnRleHQuaW5kZW50ZWQ7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoaW5kZW50LCBjb2wsIHR5cGUsIG51bGwsIHN0YXRlLmNvbnRleHQpO1xufVxuZnVuY3Rpb24gcG9wQ29udGV4dChzdGF0ZSkge1xuICB2YXIgdCA9IHN0YXRlLmNvbnRleHQudHlwZTtcbiAgaWYgKHQgPT0gXCIpXCIgfHwgdCA9PSBcIl1cIiB8fCB0ID09IFwifVwiKSBzdGF0ZS5pbmRlbnRlZCA9IHN0YXRlLmNvbnRleHQuaW5kZW50ZWQ7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gc3RhdGUuY29udGV4dC5wcmV2O1xufVxuXG4vL0ludGVyZmFjZVxuZXhwb3J0IGNvbnN0IHR0Y24gPSB7XG4gIG5hbWU6IFwidHRjblwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBudWxsLFxuICAgICAgY29udGV4dDogbmV3IENvbnRleHQoMCwgMCwgXCJ0b3BcIiwgZmFsc2UpLFxuICAgICAgaW5kZW50ZWQ6IDAsXG4gICAgICBzdGFydE9mTGluZTogdHJ1ZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0O1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gZmFsc2U7XG4gICAgICBzdGF0ZS5pbmRlbnRlZCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIGN1clB1bmMgPSBudWxsO1xuICAgIHZhciBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PSBcImNvbW1lbnRcIikgcmV0dXJuIHN0eWxlO1xuICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gdHJ1ZTtcbiAgICBpZiAoKGN1clB1bmMgPT0gXCI7XCIgfHwgY3VyUHVuYyA9PSBcIjpcIiB8fCBjdXJQdW5jID09IFwiLFwiKSAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSB7XG4gICAgICBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICB9IGVsc2UgaWYgKGN1clB1bmMgPT0gXCJ7XCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwifVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwiW1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIl1cIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIihcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCIpXCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJ9XCIpIHtcbiAgICAgIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgIGlmIChjdHgudHlwZSA9PSBcIn1cIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICB3aGlsZSAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChjdXJQdW5jID09IGN0eC50eXBlKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmIChpbmRlbnRTdGF0ZW1lbnRzICYmICgoY3R4LnR5cGUgPT0gXCJ9XCIgfHwgY3R4LnR5cGUgPT0gXCJ0b3BcIikgJiYgY3VyUHVuYyAhPSAnOycgfHwgY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIiAmJiBjdXJQdW5jID09IFwibmV3c3RhdGVtZW50XCIpKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcInN0YXRlbWVudFwiKTtcbiAgICBzdGF0ZS5zdGFydE9mTGluZSA9IGZhbHNlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgaW5kZW50T25JbnB1dDogL15cXHMqW3t9XSQvLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiLy9cIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiLypcIixcbiAgICAgICAgY2xvc2U6IFwiKi9cIlxuICAgICAgfVxuICAgIH0sXG4gICAgYXV0b2NvbXBsZXRlOiB3b3JkTGlzdFxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=