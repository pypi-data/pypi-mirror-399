"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9934],{

/***/ 41660
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   I: () => (/* binding */ simpleMode)
/* harmony export */ });
function simpleMode(states) {
  ensureState(states, "start");
  var states_ = {},
    meta = states.languageData || {},
    hasIndentation = false;
  for (var state in states) if (state != meta && states.hasOwnProperty(state)) {
    var list = states_[state] = [],
      orig = states[state];
    for (var i = 0; i < orig.length; i++) {
      var data = orig[i];
      list.push(new Rule(data, states));
      if (data.indent || data.dedent) hasIndentation = true;
    }
  }
  return {
    name: meta.name,
    startState: function () {
      return {
        state: "start",
        pending: null,
        indent: hasIndentation ? [] : null
      };
    },
    copyState: function (state) {
      var s = {
        state: state.state,
        pending: state.pending,
        indent: state.indent && state.indent.slice(0)
      };
      if (state.stack) s.stack = state.stack.slice(0);
      return s;
    },
    token: tokenFunction(states_),
    indent: indentFunction(states_, meta),
    mergeTokens: meta.mergeTokens,
    languageData: meta
  };
}
;
function ensureState(states, name) {
  if (!states.hasOwnProperty(name)) throw new Error("Undefined state " + name + " in simple mode");
}
function toRegex(val, caret) {
  if (!val) return /(?:)/;
  var flags = "";
  if (val instanceof RegExp) {
    if (val.ignoreCase) flags = "i";
    if (val.unicode) flags += "u";
    val = val.source;
  } else {
    val = String(val);
  }
  return new RegExp((caret === false ? "" : "^") + "(?:" + val + ")", flags);
}
function asToken(val) {
  if (!val) return null;
  if (val.apply) return val;
  if (typeof val == "string") return val.replace(/\./g, " ");
  var result = [];
  for (var i = 0; i < val.length; i++) result.push(val[i] && val[i].replace(/\./g, " "));
  return result;
}
function Rule(data, states) {
  if (data.next || data.push) ensureState(states, data.next || data.push);
  this.regex = toRegex(data.regex);
  this.token = asToken(data.token);
  this.data = data;
}
function tokenFunction(states) {
  return function (stream, state) {
    if (state.pending) {
      var pend = state.pending.shift();
      if (state.pending.length == 0) state.pending = null;
      stream.pos += pend.text.length;
      return pend.token;
    }
    var curState = states[state.state];
    for (var i = 0; i < curState.length; i++) {
      var rule = curState[i];
      var matches = (!rule.data.sol || stream.sol()) && stream.match(rule.regex);
      if (matches) {
        if (rule.data.next) {
          state.state = rule.data.next;
        } else if (rule.data.push) {
          (state.stack || (state.stack = [])).push(state.state);
          state.state = rule.data.push;
        } else if (rule.data.pop && state.stack && state.stack.length) {
          state.state = state.stack.pop();
        }
        if (rule.data.indent) state.indent.push(stream.indentation() + stream.indentUnit);
        if (rule.data.dedent) state.indent.pop();
        var token = rule.token;
        if (token && token.apply) token = token(matches);
        if (matches.length > 2 && rule.token && typeof rule.token != "string") {
          state.pending = [];
          for (var j = 2; j < matches.length; j++) if (matches[j]) state.pending.push({
            text: matches[j],
            token: rule.token[j - 1]
          });
          stream.backUp(matches[0].length - (matches[1] ? matches[1].length : 0));
          return token[0];
        } else if (token && token.join) {
          return token[0];
        } else {
          return token;
        }
      }
    }
    stream.next();
    return null;
  };
}
function indentFunction(states, meta) {
  return function (state, textAfter) {
    if (state.indent == null || meta.dontIndentStates && meta.dontIndentStates.indexOf(state.state) > -1) return null;
    var pos = state.indent.length - 1,
      rules = states[state.state];
    scan: for (;;) {
      for (var i = 0; i < rules.length; i++) {
        var rule = rules[i];
        if (rule.data.dedent && rule.data.dedentIfLineStart !== false) {
          var m = rule.regex.exec(textAfter);
          if (m && m[0]) {
            pos--;
            if (rule.next || rule.push) rules = states[rule.next || rule.push];
            textAfter = textAfter.slice(m[0].length);
            continue scan;
          }
        }
      }
      break;
    }
    return pos < 0 ? 0 : state.indent[pos];
  };
}

/***/ },

/***/ 59934
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   dockerFile: () => (/* binding */ dockerFile)
/* harmony export */ });
/* harmony import */ var _simple_mode_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(41660);

var from = "from";
var fromRegex = new RegExp("^(\\s*)\\b(" + from + ")\\b", "i");
var shells = ["run", "cmd", "entrypoint", "shell"];
var shellsAsArrayRegex = new RegExp("^(\\s*)(" + shells.join('|') + ")(\\s+\\[)", "i");
var expose = "expose";
var exposeRegex = new RegExp("^(\\s*)(" + expose + ")(\\s+)", "i");
var others = ["arg", "from", "maintainer", "label", "env", "add", "copy", "volume", "user", "workdir", "onbuild", "stopsignal", "healthcheck", "shell"];

// Collect all Dockerfile directives
var instructions = [from, expose].concat(shells).concat(others),
  instructionRegex = "(" + instructions.join('|') + ")",
  instructionOnlyLine = new RegExp("^(\\s*)" + instructionRegex + "(\\s*)(#.*)?$", "i"),
  instructionWithArguments = new RegExp("^(\\s*)" + instructionRegex + "(\\s+)", "i");
const dockerFile = (0,_simple_mode_js__WEBPACK_IMPORTED_MODULE_0__/* .simpleMode */ .I)({
  start: [
  // Block comment: This is a line starting with a comment
  {
    regex: /^\s*#.*$/,
    sol: true,
    token: "comment"
  }, {
    regex: fromRegex,
    token: [null, "keyword"],
    sol: true,
    next: "from"
  },
  // Highlight an instruction without any arguments (for convenience)
  {
    regex: instructionOnlyLine,
    token: [null, "keyword", null, "error"],
    sol: true
  }, {
    regex: shellsAsArrayRegex,
    token: [null, "keyword", null],
    sol: true,
    next: "array"
  }, {
    regex: exposeRegex,
    token: [null, "keyword", null],
    sol: true,
    next: "expose"
  },
  // Highlight an instruction followed by arguments
  {
    regex: instructionWithArguments,
    token: [null, "keyword", null],
    sol: true,
    next: "arguments"
  }, {
    regex: /./,
    token: null
  }],
  from: [{
    regex: /\s*$/,
    token: null,
    next: "start"
  }, {
    // Line comment without instruction arguments is an error
    regex: /(\s*)(#.*)$/,
    token: [null, "error"],
    next: "start"
  }, {
    regex: /(\s*\S+\s+)(as)/i,
    token: [null, "keyword"],
    next: "start"
  },
  // Fail safe return to start
  {
    token: null,
    next: "start"
  }],
  single: [{
    regex: /(?:[^\\']|\\.)/,
    token: "string"
  }, {
    regex: /'/,
    token: "string",
    pop: true
  }],
  double: [{
    regex: /(?:[^\\"]|\\.)/,
    token: "string"
  }, {
    regex: /"/,
    token: "string",
    pop: true
  }],
  array: [{
    regex: /\]/,
    token: null,
    next: "start"
  }, {
    regex: /"(?:[^\\"]|\\.)*"?/,
    token: "string"
  }],
  expose: [{
    regex: /\d+$/,
    token: "number",
    next: "start"
  }, {
    regex: /[^\d]+$/,
    token: null,
    next: "start"
  }, {
    regex: /\d+/,
    token: "number"
  }, {
    regex: /[^\d]+/,
    token: null
  },
  // Fail safe return to start
  {
    token: null,
    next: "start"
  }],
  arguments: [{
    regex: /^\s*#.*$/,
    sol: true,
    token: "comment"
  }, {
    regex: /"(?:[^\\"]|\\.)*"?$/,
    token: "string",
    next: "start"
  }, {
    regex: /"/,
    token: "string",
    push: "double"
  }, {
    regex: /'(?:[^\\']|\\.)*'?$/,
    token: "string",
    next: "start"
  }, {
    regex: /'/,
    token: "string",
    push: "single"
  }, {
    regex: /[^#"']+[\\`]$/,
    token: null
  }, {
    regex: /[^#"']+$/,
    token: null,
    next: "start"
  }, {
    regex: /[^#"']+/,
    token: null
  },
  // Fail safe return to start
  {
    token: null,
    next: "start"
  }],
  languageData: {
    commentTokens: {
      line: "#"
    }
  }
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTkzNC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7O0FDdElBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3NpbXBsZS1tb2RlLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZG9ja2VyZmlsZS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgZnVuY3Rpb24gc2ltcGxlTW9kZShzdGF0ZXMpIHtcbiAgZW5zdXJlU3RhdGUoc3RhdGVzLCBcInN0YXJ0XCIpO1xuICB2YXIgc3RhdGVzXyA9IHt9LFxuICAgIG1ldGEgPSBzdGF0ZXMubGFuZ3VhZ2VEYXRhIHx8IHt9LFxuICAgIGhhc0luZGVudGF0aW9uID0gZmFsc2U7XG4gIGZvciAodmFyIHN0YXRlIGluIHN0YXRlcykgaWYgKHN0YXRlICE9IG1ldGEgJiYgc3RhdGVzLmhhc093blByb3BlcnR5KHN0YXRlKSkge1xuICAgIHZhciBsaXN0ID0gc3RhdGVzX1tzdGF0ZV0gPSBbXSxcbiAgICAgIG9yaWcgPSBzdGF0ZXNbc3RhdGVdO1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgb3JpZy5sZW5ndGg7IGkrKykge1xuICAgICAgdmFyIGRhdGEgPSBvcmlnW2ldO1xuICAgICAgbGlzdC5wdXNoKG5ldyBSdWxlKGRhdGEsIHN0YXRlcykpO1xuICAgICAgaWYgKGRhdGEuaW5kZW50IHx8IGRhdGEuZGVkZW50KSBoYXNJbmRlbnRhdGlvbiA9IHRydWU7XG4gICAgfVxuICB9XG4gIHJldHVybiB7XG4gICAgbmFtZTogbWV0YS5uYW1lLFxuICAgIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHN0YXRlOiBcInN0YXJ0XCIsXG4gICAgICAgIHBlbmRpbmc6IG51bGwsXG4gICAgICAgIGluZGVudDogaGFzSW5kZW50YXRpb24gPyBbXSA6IG51bGxcbiAgICAgIH07XG4gICAgfSxcbiAgICBjb3B5U3RhdGU6IGZ1bmN0aW9uIChzdGF0ZSkge1xuICAgICAgdmFyIHMgPSB7XG4gICAgICAgIHN0YXRlOiBzdGF0ZS5zdGF0ZSxcbiAgICAgICAgcGVuZGluZzogc3RhdGUucGVuZGluZyxcbiAgICAgICAgaW5kZW50OiBzdGF0ZS5pbmRlbnQgJiYgc3RhdGUuaW5kZW50LnNsaWNlKDApXG4gICAgICB9O1xuICAgICAgaWYgKHN0YXRlLnN0YWNrKSBzLnN0YWNrID0gc3RhdGUuc3RhY2suc2xpY2UoMCk7XG4gICAgICByZXR1cm4gcztcbiAgICB9LFxuICAgIHRva2VuOiB0b2tlbkZ1bmN0aW9uKHN0YXRlc18pLFxuICAgIGluZGVudDogaW5kZW50RnVuY3Rpb24oc3RhdGVzXywgbWV0YSksXG4gICAgbWVyZ2VUb2tlbnM6IG1ldGEubWVyZ2VUb2tlbnMsXG4gICAgbGFuZ3VhZ2VEYXRhOiBtZXRhXG4gIH07XG59XG47XG5mdW5jdGlvbiBlbnN1cmVTdGF0ZShzdGF0ZXMsIG5hbWUpIHtcbiAgaWYgKCFzdGF0ZXMuaGFzT3duUHJvcGVydHkobmFtZSkpIHRocm93IG5ldyBFcnJvcihcIlVuZGVmaW5lZCBzdGF0ZSBcIiArIG5hbWUgKyBcIiBpbiBzaW1wbGUgbW9kZVwiKTtcbn1cbmZ1bmN0aW9uIHRvUmVnZXgodmFsLCBjYXJldCkge1xuICBpZiAoIXZhbCkgcmV0dXJuIC8oPzopLztcbiAgdmFyIGZsYWdzID0gXCJcIjtcbiAgaWYgKHZhbCBpbnN0YW5jZW9mIFJlZ0V4cCkge1xuICAgIGlmICh2YWwuaWdub3JlQ2FzZSkgZmxhZ3MgPSBcImlcIjtcbiAgICBpZiAodmFsLnVuaWNvZGUpIGZsYWdzICs9IFwidVwiO1xuICAgIHZhbCA9IHZhbC5zb3VyY2U7XG4gIH0gZWxzZSB7XG4gICAgdmFsID0gU3RyaW5nKHZhbCk7XG4gIH1cbiAgcmV0dXJuIG5ldyBSZWdFeHAoKGNhcmV0ID09PSBmYWxzZSA/IFwiXCIgOiBcIl5cIikgKyBcIig/OlwiICsgdmFsICsgXCIpXCIsIGZsYWdzKTtcbn1cbmZ1bmN0aW9uIGFzVG9rZW4odmFsKSB7XG4gIGlmICghdmFsKSByZXR1cm4gbnVsbDtcbiAgaWYgKHZhbC5hcHBseSkgcmV0dXJuIHZhbDtcbiAgaWYgKHR5cGVvZiB2YWwgPT0gXCJzdHJpbmdcIikgcmV0dXJuIHZhbC5yZXBsYWNlKC9cXC4vZywgXCIgXCIpO1xuICB2YXIgcmVzdWx0ID0gW107XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgdmFsLmxlbmd0aDsgaSsrKSByZXN1bHQucHVzaCh2YWxbaV0gJiYgdmFsW2ldLnJlcGxhY2UoL1xcLi9nLCBcIiBcIikpO1xuICByZXR1cm4gcmVzdWx0O1xufVxuZnVuY3Rpb24gUnVsZShkYXRhLCBzdGF0ZXMpIHtcbiAgaWYgKGRhdGEubmV4dCB8fCBkYXRhLnB1c2gpIGVuc3VyZVN0YXRlKHN0YXRlcywgZGF0YS5uZXh0IHx8IGRhdGEucHVzaCk7XG4gIHRoaXMucmVnZXggPSB0b1JlZ2V4KGRhdGEucmVnZXgpO1xuICB0aGlzLnRva2VuID0gYXNUb2tlbihkYXRhLnRva2VuKTtcbiAgdGhpcy5kYXRhID0gZGF0YTtcbn1cbmZ1bmN0aW9uIHRva2VuRnVuY3Rpb24oc3RhdGVzKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdGF0ZS5wZW5kaW5nKSB7XG4gICAgICB2YXIgcGVuZCA9IHN0YXRlLnBlbmRpbmcuc2hpZnQoKTtcbiAgICAgIGlmIChzdGF0ZS5wZW5kaW5nLmxlbmd0aCA9PSAwKSBzdGF0ZS5wZW5kaW5nID0gbnVsbDtcbiAgICAgIHN0cmVhbS5wb3MgKz0gcGVuZC50ZXh0Lmxlbmd0aDtcbiAgICAgIHJldHVybiBwZW5kLnRva2VuO1xuICAgIH1cbiAgICB2YXIgY3VyU3RhdGUgPSBzdGF0ZXNbc3RhdGUuc3RhdGVdO1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY3VyU3RhdGUubGVuZ3RoOyBpKyspIHtcbiAgICAgIHZhciBydWxlID0gY3VyU3RhdGVbaV07XG4gICAgICB2YXIgbWF0Y2hlcyA9ICghcnVsZS5kYXRhLnNvbCB8fCBzdHJlYW0uc29sKCkpICYmIHN0cmVhbS5tYXRjaChydWxlLnJlZ2V4KTtcbiAgICAgIGlmIChtYXRjaGVzKSB7XG4gICAgICAgIGlmIChydWxlLmRhdGEubmV4dCkge1xuICAgICAgICAgIHN0YXRlLnN0YXRlID0gcnVsZS5kYXRhLm5leHQ7XG4gICAgICAgIH0gZWxzZSBpZiAocnVsZS5kYXRhLnB1c2gpIHtcbiAgICAgICAgICAoc3RhdGUuc3RhY2sgfHwgKHN0YXRlLnN0YWNrID0gW10pKS5wdXNoKHN0YXRlLnN0YXRlKTtcbiAgICAgICAgICBzdGF0ZS5zdGF0ZSA9IHJ1bGUuZGF0YS5wdXNoO1xuICAgICAgICB9IGVsc2UgaWYgKHJ1bGUuZGF0YS5wb3AgJiYgc3RhdGUuc3RhY2sgJiYgc3RhdGUuc3RhY2subGVuZ3RoKSB7XG4gICAgICAgICAgc3RhdGUuc3RhdGUgPSBzdGF0ZS5zdGFjay5wb3AoKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAocnVsZS5kYXRhLmluZGVudCkgc3RhdGUuaW5kZW50LnB1c2goc3RyZWFtLmluZGVudGF0aW9uKCkgKyBzdHJlYW0uaW5kZW50VW5pdCk7XG4gICAgICAgIGlmIChydWxlLmRhdGEuZGVkZW50KSBzdGF0ZS5pbmRlbnQucG9wKCk7XG4gICAgICAgIHZhciB0b2tlbiA9IHJ1bGUudG9rZW47XG4gICAgICAgIGlmICh0b2tlbiAmJiB0b2tlbi5hcHBseSkgdG9rZW4gPSB0b2tlbihtYXRjaGVzKTtcbiAgICAgICAgaWYgKG1hdGNoZXMubGVuZ3RoID4gMiAmJiBydWxlLnRva2VuICYmIHR5cGVvZiBydWxlLnRva2VuICE9IFwic3RyaW5nXCIpIHtcbiAgICAgICAgICBzdGF0ZS5wZW5kaW5nID0gW107XG4gICAgICAgICAgZm9yICh2YXIgaiA9IDI7IGogPCBtYXRjaGVzLmxlbmd0aDsgaisrKSBpZiAobWF0Y2hlc1tqXSkgc3RhdGUucGVuZGluZy5wdXNoKHtcbiAgICAgICAgICAgIHRleHQ6IG1hdGNoZXNbal0sXG4gICAgICAgICAgICB0b2tlbjogcnVsZS50b2tlbltqIC0gMV1cbiAgICAgICAgICB9KTtcbiAgICAgICAgICBzdHJlYW0uYmFja1VwKG1hdGNoZXNbMF0ubGVuZ3RoIC0gKG1hdGNoZXNbMV0gPyBtYXRjaGVzWzFdLmxlbmd0aCA6IDApKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5bMF07XG4gICAgICAgIH0gZWxzZSBpZiAodG9rZW4gJiYgdG9rZW4uam9pbikge1xuICAgICAgICAgIHJldHVybiB0b2tlblswXTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW47XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfTtcbn1cbmZ1bmN0aW9uIGluZGVudEZ1bmN0aW9uKHN0YXRlcywgbWV0YSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIpIHtcbiAgICBpZiAoc3RhdGUuaW5kZW50ID09IG51bGwgfHwgbWV0YS5kb250SW5kZW50U3RhdGVzICYmIG1ldGEuZG9udEluZGVudFN0YXRlcy5pbmRleE9mKHN0YXRlLnN0YXRlKSA+IC0xKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgcG9zID0gc3RhdGUuaW5kZW50Lmxlbmd0aCAtIDEsXG4gICAgICBydWxlcyA9IHN0YXRlc1tzdGF0ZS5zdGF0ZV07XG4gICAgc2NhbjogZm9yICg7Oykge1xuICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBydWxlcy5sZW5ndGg7IGkrKykge1xuICAgICAgICB2YXIgcnVsZSA9IHJ1bGVzW2ldO1xuICAgICAgICBpZiAocnVsZS5kYXRhLmRlZGVudCAmJiBydWxlLmRhdGEuZGVkZW50SWZMaW5lU3RhcnQgIT09IGZhbHNlKSB7XG4gICAgICAgICAgdmFyIG0gPSBydWxlLnJlZ2V4LmV4ZWModGV4dEFmdGVyKTtcbiAgICAgICAgICBpZiAobSAmJiBtWzBdKSB7XG4gICAgICAgICAgICBwb3MtLTtcbiAgICAgICAgICAgIGlmIChydWxlLm5leHQgfHwgcnVsZS5wdXNoKSBydWxlcyA9IHN0YXRlc1tydWxlLm5leHQgfHwgcnVsZS5wdXNoXTtcbiAgICAgICAgICAgIHRleHRBZnRlciA9IHRleHRBZnRlci5zbGljZShtWzBdLmxlbmd0aCk7XG4gICAgICAgICAgICBjb250aW51ZSBzY2FuO1xuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIHJldHVybiBwb3MgPCAwID8gMCA6IHN0YXRlLmluZGVudFtwb3NdO1xuICB9O1xufSIsImltcG9ydCB7IHNpbXBsZU1vZGUgfSBmcm9tIFwiLi9zaW1wbGUtbW9kZS5qc1wiO1xudmFyIGZyb20gPSBcImZyb21cIjtcbnZhciBmcm9tUmVnZXggPSBuZXcgUmVnRXhwKFwiXihcXFxccyopXFxcXGIoXCIgKyBmcm9tICsgXCIpXFxcXGJcIiwgXCJpXCIpO1xudmFyIHNoZWxscyA9IFtcInJ1blwiLCBcImNtZFwiLCBcImVudHJ5cG9pbnRcIiwgXCJzaGVsbFwiXTtcbnZhciBzaGVsbHNBc0FycmF5UmVnZXggPSBuZXcgUmVnRXhwKFwiXihcXFxccyopKFwiICsgc2hlbGxzLmpvaW4oJ3wnKSArIFwiKShcXFxccytcXFxcWylcIiwgXCJpXCIpO1xudmFyIGV4cG9zZSA9IFwiZXhwb3NlXCI7XG52YXIgZXhwb3NlUmVnZXggPSBuZXcgUmVnRXhwKFwiXihcXFxccyopKFwiICsgZXhwb3NlICsgXCIpKFxcXFxzKylcIiwgXCJpXCIpO1xudmFyIG90aGVycyA9IFtcImFyZ1wiLCBcImZyb21cIiwgXCJtYWludGFpbmVyXCIsIFwibGFiZWxcIiwgXCJlbnZcIiwgXCJhZGRcIiwgXCJjb3B5XCIsIFwidm9sdW1lXCIsIFwidXNlclwiLCBcIndvcmtkaXJcIiwgXCJvbmJ1aWxkXCIsIFwic3RvcHNpZ25hbFwiLCBcImhlYWx0aGNoZWNrXCIsIFwic2hlbGxcIl07XG5cbi8vIENvbGxlY3QgYWxsIERvY2tlcmZpbGUgZGlyZWN0aXZlc1xudmFyIGluc3RydWN0aW9ucyA9IFtmcm9tLCBleHBvc2VdLmNvbmNhdChzaGVsbHMpLmNvbmNhdChvdGhlcnMpLFxuICBpbnN0cnVjdGlvblJlZ2V4ID0gXCIoXCIgKyBpbnN0cnVjdGlvbnMuam9pbignfCcpICsgXCIpXCIsXG4gIGluc3RydWN0aW9uT25seUxpbmUgPSBuZXcgUmVnRXhwKFwiXihcXFxccyopXCIgKyBpbnN0cnVjdGlvblJlZ2V4ICsgXCIoXFxcXHMqKSgjLiopPyRcIiwgXCJpXCIpLFxuICBpbnN0cnVjdGlvbldpdGhBcmd1bWVudHMgPSBuZXcgUmVnRXhwKFwiXihcXFxccyopXCIgKyBpbnN0cnVjdGlvblJlZ2V4ICsgXCIoXFxcXHMrKVwiLCBcImlcIik7XG5leHBvcnQgY29uc3QgZG9ja2VyRmlsZSA9IHNpbXBsZU1vZGUoe1xuICBzdGFydDogW1xuICAvLyBCbG9jayBjb21tZW50OiBUaGlzIGlzIGEgbGluZSBzdGFydGluZyB3aXRoIGEgY29tbWVudFxuICB7XG4gICAgcmVnZXg6IC9eXFxzKiMuKiQvLFxuICAgIHNvbDogdHJ1ZSxcbiAgICB0b2tlbjogXCJjb21tZW50XCJcbiAgfSwge1xuICAgIHJlZ2V4OiBmcm9tUmVnZXgsXG4gICAgdG9rZW46IFtudWxsLCBcImtleXdvcmRcIl0sXG4gICAgc29sOiB0cnVlLFxuICAgIG5leHQ6IFwiZnJvbVwiXG4gIH0sXG4gIC8vIEhpZ2hsaWdodCBhbiBpbnN0cnVjdGlvbiB3aXRob3V0IGFueSBhcmd1bWVudHMgKGZvciBjb252ZW5pZW5jZSlcbiAge1xuICAgIHJlZ2V4OiBpbnN0cnVjdGlvbk9ubHlMaW5lLFxuICAgIHRva2VuOiBbbnVsbCwgXCJrZXl3b3JkXCIsIG51bGwsIFwiZXJyb3JcIl0sXG4gICAgc29sOiB0cnVlXG4gIH0sIHtcbiAgICByZWdleDogc2hlbGxzQXNBcnJheVJlZ2V4LFxuICAgIHRva2VuOiBbbnVsbCwgXCJrZXl3b3JkXCIsIG51bGxdLFxuICAgIHNvbDogdHJ1ZSxcbiAgICBuZXh0OiBcImFycmF5XCJcbiAgfSwge1xuICAgIHJlZ2V4OiBleHBvc2VSZWdleCxcbiAgICB0b2tlbjogW251bGwsIFwia2V5d29yZFwiLCBudWxsXSxcbiAgICBzb2w6IHRydWUsXG4gICAgbmV4dDogXCJleHBvc2VcIlxuICB9LFxuICAvLyBIaWdobGlnaHQgYW4gaW5zdHJ1Y3Rpb24gZm9sbG93ZWQgYnkgYXJndW1lbnRzXG4gIHtcbiAgICByZWdleDogaW5zdHJ1Y3Rpb25XaXRoQXJndW1lbnRzLFxuICAgIHRva2VuOiBbbnVsbCwgXCJrZXl3b3JkXCIsIG51bGxdLFxuICAgIHNvbDogdHJ1ZSxcbiAgICBuZXh0OiBcImFyZ3VtZW50c1wiXG4gIH0sIHtcbiAgICByZWdleDogLy4vLFxuICAgIHRva2VuOiBudWxsXG4gIH1dLFxuICBmcm9tOiBbe1xuICAgIHJlZ2V4OiAvXFxzKiQvLFxuICAgIHRva2VuOiBudWxsLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgLy8gTGluZSBjb21tZW50IHdpdGhvdXQgaW5zdHJ1Y3Rpb24gYXJndW1lbnRzIGlzIGFuIGVycm9yXG4gICAgcmVnZXg6IC8oXFxzKikoIy4qKSQvLFxuICAgIHRva2VuOiBbbnVsbCwgXCJlcnJvclwiXSxcbiAgICBuZXh0OiBcInN0YXJ0XCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvKFxccypcXFMrXFxzKykoYXMpL2ksXG4gICAgdG9rZW46IFtudWxsLCBcImtleXdvcmRcIl0sXG4gICAgbmV4dDogXCJzdGFydFwiXG4gIH0sXG4gIC8vIEZhaWwgc2FmZSByZXR1cm4gdG8gc3RhcnRcbiAge1xuICAgIHRva2VuOiBudWxsLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9XSxcbiAgc2luZ2xlOiBbe1xuICAgIHJlZ2V4OiAvKD86W15cXFxcJ118XFxcXC4pLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIlxuICB9LCB7XG4gICAgcmVnZXg6IC8nLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIixcbiAgICBwb3A6IHRydWVcbiAgfV0sXG4gIGRvdWJsZTogW3tcbiAgICByZWdleDogLyg/OlteXFxcXFwiXXxcXFxcLikvLFxuICAgIHRva2VuOiBcInN0cmluZ1wiXG4gIH0sIHtcbiAgICByZWdleDogL1wiLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIixcbiAgICBwb3A6IHRydWVcbiAgfV0sXG4gIGFycmF5OiBbe1xuICAgIHJlZ2V4OiAvXFxdLyxcbiAgICB0b2tlbjogbnVsbCxcbiAgICBuZXh0OiBcInN0YXJ0XCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvXCIoPzpbXlxcXFxcIl18XFxcXC4pKlwiPy8sXG4gICAgdG9rZW46IFwic3RyaW5nXCJcbiAgfV0sXG4gIGV4cG9zZTogW3tcbiAgICByZWdleDogL1xcZCskLyxcbiAgICB0b2tlbjogXCJudW1iZXJcIixcbiAgICBuZXh0OiBcInN0YXJ0XCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvW15cXGRdKyQvLFxuICAgIHRva2VuOiBudWxsLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cXGQrLyxcbiAgICB0b2tlbjogXCJudW1iZXJcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9bXlxcZF0rLyxcbiAgICB0b2tlbjogbnVsbFxuICB9LFxuICAvLyBGYWlsIHNhZmUgcmV0dXJuIHRvIHN0YXJ0XG4gIHtcbiAgICB0b2tlbjogbnVsbCxcbiAgICBuZXh0OiBcInN0YXJ0XCJcbiAgfV0sXG4gIGFyZ3VtZW50czogW3tcbiAgICByZWdleDogL15cXHMqIy4qJC8sXG4gICAgc29sOiB0cnVlLFxuICAgIHRva2VuOiBcImNvbW1lbnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cIig/OlteXFxcXFwiXXxcXFxcLikqXCI/JC8sXG4gICAgdG9rZW46IFwic3RyaW5nXCIsXG4gICAgbmV4dDogXCJzdGFydFwiXG4gIH0sIHtcbiAgICByZWdleDogL1wiLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIixcbiAgICBwdXNoOiBcImRvdWJsZVwiXG4gIH0sIHtcbiAgICByZWdleDogLycoPzpbXlxcXFwnXXxcXFxcLikqJz8kLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIixcbiAgICBuZXh0OiBcInN0YXJ0XCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvJy8sXG4gICAgdG9rZW46IFwic3RyaW5nXCIsXG4gICAgcHVzaDogXCJzaW5nbGVcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9bXiNcIiddK1tcXFxcYF0kLyxcbiAgICB0b2tlbjogbnVsbFxuICB9LCB7XG4gICAgcmVnZXg6IC9bXiNcIiddKyQvLFxuICAgIHRva2VuOiBudWxsLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9bXiNcIiddKy8sXG4gICAgdG9rZW46IG51bGxcbiAgfSxcbiAgLy8gRmFpbCBzYWZlIHJldHVybiB0byBzdGFydFxuICB7XG4gICAgdG9rZW46IG51bGwsXG4gICAgbmV4dDogXCJzdGFydFwiXG4gIH1dLFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIiNcIlxuICAgIH1cbiAgfVxufSk7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==