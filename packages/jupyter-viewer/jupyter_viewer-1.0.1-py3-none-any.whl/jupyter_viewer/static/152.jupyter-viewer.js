"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[152],{

/***/ 10152
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   lua: () => (/* binding */ lua)
/* harmony export */ });
function prefixRE(words) {
  return new RegExp("^(?:" + words.join("|") + ")", "i");
}
function wordRE(words) {
  return new RegExp("^(?:" + words.join("|") + ")$", "i");
}

// long list of standard functions from lua manual
var builtins = wordRE(["_G", "_VERSION", "assert", "collectgarbage", "dofile", "error", "getfenv", "getmetatable", "ipairs", "load", "loadfile", "loadstring", "module", "next", "pairs", "pcall", "print", "rawequal", "rawget", "rawset", "require", "select", "setfenv", "setmetatable", "tonumber", "tostring", "type", "unpack", "xpcall", "coroutine.create", "coroutine.resume", "coroutine.running", "coroutine.status", "coroutine.wrap", "coroutine.yield", "debug.debug", "debug.getfenv", "debug.gethook", "debug.getinfo", "debug.getlocal", "debug.getmetatable", "debug.getregistry", "debug.getupvalue", "debug.setfenv", "debug.sethook", "debug.setlocal", "debug.setmetatable", "debug.setupvalue", "debug.traceback", "close", "flush", "lines", "read", "seek", "setvbuf", "write", "io.close", "io.flush", "io.input", "io.lines", "io.open", "io.output", "io.popen", "io.read", "io.stderr", "io.stdin", "io.stdout", "io.tmpfile", "io.type", "io.write", "math.abs", "math.acos", "math.asin", "math.atan", "math.atan2", "math.ceil", "math.cos", "math.cosh", "math.deg", "math.exp", "math.floor", "math.fmod", "math.frexp", "math.huge", "math.ldexp", "math.log", "math.log10", "math.max", "math.min", "math.modf", "math.pi", "math.pow", "math.rad", "math.random", "math.randomseed", "math.sin", "math.sinh", "math.sqrt", "math.tan", "math.tanh", "os.clock", "os.date", "os.difftime", "os.execute", "os.exit", "os.getenv", "os.remove", "os.rename", "os.setlocale", "os.time", "os.tmpname", "package.cpath", "package.loaded", "package.loaders", "package.loadlib", "package.path", "package.preload", "package.seeall", "string.byte", "string.char", "string.dump", "string.find", "string.format", "string.gmatch", "string.gsub", "string.len", "string.lower", "string.match", "string.rep", "string.reverse", "string.sub", "string.upper", "table.concat", "table.insert", "table.maxn", "table.remove", "table.sort"]);
var keywords = wordRE(["and", "break", "elseif", "false", "nil", "not", "or", "return", "true", "function", "end", "if", "then", "else", "do", "while", "repeat", "until", "for", "in", "local"]);
var indentTokens = wordRE(["function", "if", "repeat", "do", "\\(", "{"]);
var dedentTokens = wordRE(["end", "until", "\\)", "}"]);
var dedentPartial = prefixRE(["end", "until", "\\)", "}", "else", "elseif"]);
function readBracket(stream) {
  var level = 0;
  while (stream.eat("=")) ++level;
  stream.eat("[");
  return level;
}
function normal(stream, state) {
  var ch = stream.next();
  if (ch == "-" && stream.eat("-")) {
    if (stream.eat("[") && stream.eat("[")) return (state.cur = bracketed(readBracket(stream), "comment"))(stream, state);
    stream.skipToEnd();
    return "comment";
  }
  if (ch == "\"" || ch == "'") return (state.cur = string(ch))(stream, state);
  if (ch == "[" && /[\[=]/.test(stream.peek())) return (state.cur = bracketed(readBracket(stream), "string"))(stream, state);
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w.%]/);
    return "number";
  }
  if (/[\w_]/.test(ch)) {
    stream.eatWhile(/[\w\\\-_.]/);
    return "variable";
  }
  return null;
}
function bracketed(level, style) {
  return function (stream, state) {
    var curlev = null,
      ch;
    while ((ch = stream.next()) != null) {
      if (curlev == null) {
        if (ch == "]") curlev = 0;
      } else if (ch == "=") ++curlev;else if (ch == "]" && curlev == level) {
        state.cur = normal;
        break;
      } else curlev = null;
    }
    return style;
  };
}
function string(quote) {
  return function (stream, state) {
    var escaped = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch == quote && !escaped) break;
      escaped = !escaped && ch == "\\";
    }
    if (!escaped) state.cur = normal;
    return "string";
  };
}
const lua = {
  name: "lua",
  startState: function () {
    return {
      basecol: 0,
      indentDepth: 0,
      cur: normal
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    var style = state.cur(stream, state);
    var word = stream.current();
    if (style == "variable") {
      if (keywords.test(word)) style = "keyword";else if (builtins.test(word)) style = "builtin";
    }
    if (style != "comment" && style != "string") {
      if (indentTokens.test(word)) ++state.indentDepth;else if (dedentTokens.test(word)) --state.indentDepth;
    }
    return style;
  },
  indent: function (state, textAfter, cx) {
    var closing = dedentPartial.test(textAfter);
    return state.basecol + cx.unit * (state.indentDepth - (closing ? 1 : 0));
  },
  languageData: {
    indentOnInput: /^\s*(?:end|until|else|\)|\})$/,
    commentTokens: {
      line: "--",
      block: {
        open: "--[[",
        close: "]]--"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTUyLmp1cHl0ZXItdmlld2VyLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2x1YS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBwcmVmaXhSRSh3b3Jkcykge1xuICByZXR1cm4gbmV3IFJlZ0V4cChcIl4oPzpcIiArIHdvcmRzLmpvaW4oXCJ8XCIpICsgXCIpXCIsIFwiaVwiKTtcbn1cbmZ1bmN0aW9uIHdvcmRSRSh3b3Jkcykge1xuICByZXR1cm4gbmV3IFJlZ0V4cChcIl4oPzpcIiArIHdvcmRzLmpvaW4oXCJ8XCIpICsgXCIpJFwiLCBcImlcIik7XG59XG5cbi8vIGxvbmcgbGlzdCBvZiBzdGFuZGFyZCBmdW5jdGlvbnMgZnJvbSBsdWEgbWFudWFsXG52YXIgYnVpbHRpbnMgPSB3b3JkUkUoW1wiX0dcIiwgXCJfVkVSU0lPTlwiLCBcImFzc2VydFwiLCBcImNvbGxlY3RnYXJiYWdlXCIsIFwiZG9maWxlXCIsIFwiZXJyb3JcIiwgXCJnZXRmZW52XCIsIFwiZ2V0bWV0YXRhYmxlXCIsIFwiaXBhaXJzXCIsIFwibG9hZFwiLCBcImxvYWRmaWxlXCIsIFwibG9hZHN0cmluZ1wiLCBcIm1vZHVsZVwiLCBcIm5leHRcIiwgXCJwYWlyc1wiLCBcInBjYWxsXCIsIFwicHJpbnRcIiwgXCJyYXdlcXVhbFwiLCBcInJhd2dldFwiLCBcInJhd3NldFwiLCBcInJlcXVpcmVcIiwgXCJzZWxlY3RcIiwgXCJzZXRmZW52XCIsIFwic2V0bWV0YXRhYmxlXCIsIFwidG9udW1iZXJcIiwgXCJ0b3N0cmluZ1wiLCBcInR5cGVcIiwgXCJ1bnBhY2tcIiwgXCJ4cGNhbGxcIiwgXCJjb3JvdXRpbmUuY3JlYXRlXCIsIFwiY29yb3V0aW5lLnJlc3VtZVwiLCBcImNvcm91dGluZS5ydW5uaW5nXCIsIFwiY29yb3V0aW5lLnN0YXR1c1wiLCBcImNvcm91dGluZS53cmFwXCIsIFwiY29yb3V0aW5lLnlpZWxkXCIsIFwiZGVidWcuZGVidWdcIiwgXCJkZWJ1Zy5nZXRmZW52XCIsIFwiZGVidWcuZ2V0aG9va1wiLCBcImRlYnVnLmdldGluZm9cIiwgXCJkZWJ1Zy5nZXRsb2NhbFwiLCBcImRlYnVnLmdldG1ldGF0YWJsZVwiLCBcImRlYnVnLmdldHJlZ2lzdHJ5XCIsIFwiZGVidWcuZ2V0dXB2YWx1ZVwiLCBcImRlYnVnLnNldGZlbnZcIiwgXCJkZWJ1Zy5zZXRob29rXCIsIFwiZGVidWcuc2V0bG9jYWxcIiwgXCJkZWJ1Zy5zZXRtZXRhdGFibGVcIiwgXCJkZWJ1Zy5zZXR1cHZhbHVlXCIsIFwiZGVidWcudHJhY2ViYWNrXCIsIFwiY2xvc2VcIiwgXCJmbHVzaFwiLCBcImxpbmVzXCIsIFwicmVhZFwiLCBcInNlZWtcIiwgXCJzZXR2YnVmXCIsIFwid3JpdGVcIiwgXCJpby5jbG9zZVwiLCBcImlvLmZsdXNoXCIsIFwiaW8uaW5wdXRcIiwgXCJpby5saW5lc1wiLCBcImlvLm9wZW5cIiwgXCJpby5vdXRwdXRcIiwgXCJpby5wb3BlblwiLCBcImlvLnJlYWRcIiwgXCJpby5zdGRlcnJcIiwgXCJpby5zdGRpblwiLCBcImlvLnN0ZG91dFwiLCBcImlvLnRtcGZpbGVcIiwgXCJpby50eXBlXCIsIFwiaW8ud3JpdGVcIiwgXCJtYXRoLmFic1wiLCBcIm1hdGguYWNvc1wiLCBcIm1hdGguYXNpblwiLCBcIm1hdGguYXRhblwiLCBcIm1hdGguYXRhbjJcIiwgXCJtYXRoLmNlaWxcIiwgXCJtYXRoLmNvc1wiLCBcIm1hdGguY29zaFwiLCBcIm1hdGguZGVnXCIsIFwibWF0aC5leHBcIiwgXCJtYXRoLmZsb29yXCIsIFwibWF0aC5mbW9kXCIsIFwibWF0aC5mcmV4cFwiLCBcIm1hdGguaHVnZVwiLCBcIm1hdGgubGRleHBcIiwgXCJtYXRoLmxvZ1wiLCBcIm1hdGgubG9nMTBcIiwgXCJtYXRoLm1heFwiLCBcIm1hdGgubWluXCIsIFwibWF0aC5tb2RmXCIsIFwibWF0aC5waVwiLCBcIm1hdGgucG93XCIsIFwibWF0aC5yYWRcIiwgXCJtYXRoLnJhbmRvbVwiLCBcIm1hdGgucmFuZG9tc2VlZFwiLCBcIm1hdGguc2luXCIsIFwibWF0aC5zaW5oXCIsIFwibWF0aC5zcXJ0XCIsIFwibWF0aC50YW5cIiwgXCJtYXRoLnRhbmhcIiwgXCJvcy5jbG9ja1wiLCBcIm9zLmRhdGVcIiwgXCJvcy5kaWZmdGltZVwiLCBcIm9zLmV4ZWN1dGVcIiwgXCJvcy5leGl0XCIsIFwib3MuZ2V0ZW52XCIsIFwib3MucmVtb3ZlXCIsIFwib3MucmVuYW1lXCIsIFwib3Muc2V0bG9jYWxlXCIsIFwib3MudGltZVwiLCBcIm9zLnRtcG5hbWVcIiwgXCJwYWNrYWdlLmNwYXRoXCIsIFwicGFja2FnZS5sb2FkZWRcIiwgXCJwYWNrYWdlLmxvYWRlcnNcIiwgXCJwYWNrYWdlLmxvYWRsaWJcIiwgXCJwYWNrYWdlLnBhdGhcIiwgXCJwYWNrYWdlLnByZWxvYWRcIiwgXCJwYWNrYWdlLnNlZWFsbFwiLCBcInN0cmluZy5ieXRlXCIsIFwic3RyaW5nLmNoYXJcIiwgXCJzdHJpbmcuZHVtcFwiLCBcInN0cmluZy5maW5kXCIsIFwic3RyaW5nLmZvcm1hdFwiLCBcInN0cmluZy5nbWF0Y2hcIiwgXCJzdHJpbmcuZ3N1YlwiLCBcInN0cmluZy5sZW5cIiwgXCJzdHJpbmcubG93ZXJcIiwgXCJzdHJpbmcubWF0Y2hcIiwgXCJzdHJpbmcucmVwXCIsIFwic3RyaW5nLnJldmVyc2VcIiwgXCJzdHJpbmcuc3ViXCIsIFwic3RyaW5nLnVwcGVyXCIsIFwidGFibGUuY29uY2F0XCIsIFwidGFibGUuaW5zZXJ0XCIsIFwidGFibGUubWF4blwiLCBcInRhYmxlLnJlbW92ZVwiLCBcInRhYmxlLnNvcnRcIl0pO1xudmFyIGtleXdvcmRzID0gd29yZFJFKFtcImFuZFwiLCBcImJyZWFrXCIsIFwiZWxzZWlmXCIsIFwiZmFsc2VcIiwgXCJuaWxcIiwgXCJub3RcIiwgXCJvclwiLCBcInJldHVyblwiLCBcInRydWVcIiwgXCJmdW5jdGlvblwiLCBcImVuZFwiLCBcImlmXCIsIFwidGhlblwiLCBcImVsc2VcIiwgXCJkb1wiLCBcIndoaWxlXCIsIFwicmVwZWF0XCIsIFwidW50aWxcIiwgXCJmb3JcIiwgXCJpblwiLCBcImxvY2FsXCJdKTtcbnZhciBpbmRlbnRUb2tlbnMgPSB3b3JkUkUoW1wiZnVuY3Rpb25cIiwgXCJpZlwiLCBcInJlcGVhdFwiLCBcImRvXCIsIFwiXFxcXChcIiwgXCJ7XCJdKTtcbnZhciBkZWRlbnRUb2tlbnMgPSB3b3JkUkUoW1wiZW5kXCIsIFwidW50aWxcIiwgXCJcXFxcKVwiLCBcIn1cIl0pO1xudmFyIGRlZGVudFBhcnRpYWwgPSBwcmVmaXhSRShbXCJlbmRcIiwgXCJ1bnRpbFwiLCBcIlxcXFwpXCIsIFwifVwiLCBcImVsc2VcIiwgXCJlbHNlaWZcIl0pO1xuZnVuY3Rpb24gcmVhZEJyYWNrZXQoc3RyZWFtKSB7XG4gIHZhciBsZXZlbCA9IDA7XG4gIHdoaWxlIChzdHJlYW0uZWF0KFwiPVwiKSkgKytsZXZlbDtcbiAgc3RyZWFtLmVhdChcIltcIik7XG4gIHJldHVybiBsZXZlbDtcbn1cbmZ1bmN0aW9uIG5vcm1hbChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSBcIi1cIiAmJiBzdHJlYW0uZWF0KFwiLVwiKSkge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiW1wiKSAmJiBzdHJlYW0uZWF0KFwiW1wiKSkgcmV0dXJuIChzdGF0ZS5jdXIgPSBicmFja2V0ZWQocmVhZEJyYWNrZXQoc3RyZWFtKSwgXCJjb21tZW50XCIpKShzdHJlYW0sIHN0YXRlKTtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG4gIGlmIChjaCA9PSBcIlxcXCJcIiB8fCBjaCA9PSBcIidcIikgcmV0dXJuIChzdGF0ZS5jdXIgPSBzdHJpbmcoY2gpKShzdHJlYW0sIHN0YXRlKTtcbiAgaWYgKGNoID09IFwiW1wiICYmIC9bXFxbPV0vLnRlc3Qoc3RyZWFtLnBlZWsoKSkpIHJldHVybiAoc3RhdGUuY3VyID0gYnJhY2tldGVkKHJlYWRCcmFja2V0KHN0cmVhbSksIFwic3RyaW5nXCIpKShzdHJlYW0sIHN0YXRlKTtcbiAgaWYgKC9cXGQvLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3LiVdLyk7XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgaWYgKC9bXFx3X10vLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFxcXFxcLV8uXS8pO1xuICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gIH1cbiAgcmV0dXJuIG51bGw7XG59XG5mdW5jdGlvbiBicmFja2V0ZWQobGV2ZWwsIHN0eWxlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjdXJsZXYgPSBudWxsLFxuICAgICAgY2g7XG4gICAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmIChjdXJsZXYgPT0gbnVsbCkge1xuICAgICAgICBpZiAoY2ggPT0gXCJdXCIpIGN1cmxldiA9IDA7XG4gICAgICB9IGVsc2UgaWYgKGNoID09IFwiPVwiKSArK2N1cmxldjtlbHNlIGlmIChjaCA9PSBcIl1cIiAmJiBjdXJsZXYgPT0gbGV2ZWwpIHtcbiAgICAgICAgc3RhdGUuY3VyID0gbm9ybWFsO1xuICAgICAgICBicmVhaztcbiAgICAgIH0gZWxzZSBjdXJsZXYgPSBudWxsO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH07XG59XG5mdW5jdGlvbiBzdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlICgoY2ggPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAoY2ggPT0gcXVvdGUgJiYgIWVzY2FwZWQpIGJyZWFrO1xuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIGNoID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoIWVzY2FwZWQpIHN0YXRlLmN1ciA9IG5vcm1hbDtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfTtcbn1cbmV4cG9ydCBjb25zdCBsdWEgPSB7XG4gIG5hbWU6IFwibHVhXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgYmFzZWNvbDogMCxcbiAgICAgIGluZGVudERlcHRoOiAwLFxuICAgICAgY3VyOiBub3JtYWxcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIHZhciBzdHlsZSA9IHN0YXRlLmN1cihzdHJlYW0sIHN0YXRlKTtcbiAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgaWYgKHN0eWxlID09IFwidmFyaWFibGVcIikge1xuICAgICAgaWYgKGtleXdvcmRzLnRlc3Qod29yZCkpIHN0eWxlID0gXCJrZXl3b3JkXCI7ZWxzZSBpZiAoYnVpbHRpbnMudGVzdCh3b3JkKSkgc3R5bGUgPSBcImJ1aWx0aW5cIjtcbiAgICB9XG4gICAgaWYgKHN0eWxlICE9IFwiY29tbWVudFwiICYmIHN0eWxlICE9IFwic3RyaW5nXCIpIHtcbiAgICAgIGlmIChpbmRlbnRUb2tlbnMudGVzdCh3b3JkKSkgKytzdGF0ZS5pbmRlbnREZXB0aDtlbHNlIGlmIChkZWRlbnRUb2tlbnMudGVzdCh3b3JkKSkgLS1zdGF0ZS5pbmRlbnREZXB0aDtcbiAgICB9XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgIHZhciBjbG9zaW5nID0gZGVkZW50UGFydGlhbC50ZXN0KHRleHRBZnRlcik7XG4gICAgcmV0dXJuIHN0YXRlLmJhc2Vjb2wgKyBjeC51bml0ICogKHN0YXRlLmluZGVudERlcHRoIC0gKGNsb3NpbmcgPyAxIDogMCkpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccyooPzplbmR8dW50aWx8ZWxzZXxcXCl8XFx9KSQvLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiLS1cIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiLS1bW1wiLFxuICAgICAgICBjbG9zZTogXCJdXS0tXCJcbiAgICAgIH1cbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==