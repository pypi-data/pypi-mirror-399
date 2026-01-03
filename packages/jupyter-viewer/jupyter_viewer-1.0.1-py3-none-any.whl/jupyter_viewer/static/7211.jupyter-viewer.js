"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7211],{

/***/ 37211
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   factor: () => (/* binding */ factor)
/* harmony export */ });
/* harmony import */ var _simple_mode_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(41660);

const factor = (0,_simple_mode_js__WEBPACK_IMPORTED_MODULE_0__/* .simpleMode */ .I)({
  start: [
  // comments
  {
    regex: /#?!.*/,
    token: "comment"
  },
  // strings """, multiline --> state
  {
    regex: /"""/,
    token: "string",
    next: "string3"
  }, {
    regex: /(STRING:)(\s)/,
    token: ["keyword", null],
    next: "string2"
  }, {
    regex: /\S*?"/,
    token: "string",
    next: "string"
  },
  // numbers: dec, hex, unicode, bin, fractional, complex
  {
    regex: /(?:0x[\d,a-f]+)|(?:0o[0-7]+)|(?:0b[0,1]+)|(?:\-?\d+.?\d*)(?=\s)/,
    token: "number"
  },
  //{regex: /[+-]?/} //fractional
  // definition: defining word, defined word, etc
  {
    regex: /((?:GENERIC)|\:?\:)(\s+)(\S+)(\s+)(\()/,
    token: ["keyword", null, "def", null, "bracket"],
    next: "stack"
  },
  // method definition: defining word, type, defined word, etc
  {
    regex: /(M\:)(\s+)(\S+)(\s+)(\S+)/,
    token: ["keyword", null, "def", null, "tag"]
  },
  // vocabulary using --> state
  {
    regex: /USING\:/,
    token: "keyword",
    next: "vocabulary"
  },
  // vocabulary definition/use
  {
    regex: /(USE\:|IN\:)(\s+)(\S+)(?=\s|$)/,
    token: ["keyword", null, "tag"]
  },
  // definition: a defining word, defined word
  {
    regex: /(\S+\:)(\s+)(\S+)(?=\s|$)/,
    token: ["keyword", null, "def"]
  },
  // "keywords", incl. ; t f . [ ] { } defining words
  {
    regex: /(?:;|\\|t|f|if|loop|while|until|do|PRIVATE>|<PRIVATE|\.|\S*\[|\]|\S*\{|\})(?=\s|$)/,
    token: "keyword"
  },
  // <constructors> and the like
  {
    regex: /\S+[\)>\.\*\?]+(?=\s|$)/,
    token: "builtin"
  }, {
    regex: /[\)><]+\S+(?=\s|$)/,
    token: "builtin"
  },
  // operators
  {
    regex: /(?:[\+\-\=\/\*<>])(?=\s|$)/,
    token: "keyword"
  },
  // any id (?)
  {
    regex: /\S+/,
    token: "variable"
  }, {
    regex: /\s+|./,
    token: null
  }],
  vocabulary: [{
    regex: /;/,
    token: "keyword",
    next: "start"
  }, {
    regex: /\S+/,
    token: "tag"
  }, {
    regex: /\s+|./,
    token: null
  }],
  string: [{
    regex: /(?:[^\\]|\\.)*?"/,
    token: "string",
    next: "start"
  }, {
    regex: /.*/,
    token: "string"
  }],
  string2: [{
    regex: /^;/,
    token: "keyword",
    next: "start"
  }, {
    regex: /.*/,
    token: "string"
  }],
  string3: [{
    regex: /(?:[^\\]|\\.)*?"""/,
    token: "string",
    next: "start"
  }, {
    regex: /.*/,
    token: "string"
  }],
  stack: [{
    regex: /\)/,
    token: "bracket",
    next: "start"
  }, {
    regex: /--/,
    token: "bracket"
  }, {
    regex: /\S+/,
    token: "meta"
  }, {
    regex: /\s+|./,
    token: null
  }],
  languageData: {
    name: "factor",
    dontIndentStates: ["start", "vocabulary", "string", "string3", "stack"],
    commentTokens: {
      line: "!"
    }
  }
});

/***/ },

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

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzIxMS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7Ozs7O0FDeklBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZmFjdG9yLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvc2ltcGxlLW1vZGUuanMiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgc2ltcGxlTW9kZSB9IGZyb20gXCIuL3NpbXBsZS1tb2RlLmpzXCI7XG5leHBvcnQgY29uc3QgZmFjdG9yID0gc2ltcGxlTW9kZSh7XG4gIHN0YXJ0OiBbXG4gIC8vIGNvbW1lbnRzXG4gIHtcbiAgICByZWdleDogLyM/IS4qLyxcbiAgICB0b2tlbjogXCJjb21tZW50XCJcbiAgfSxcbiAgLy8gc3RyaW5ncyBcIlwiXCIsIG11bHRpbGluZSAtLT4gc3RhdGVcbiAge1xuICAgIHJlZ2V4OiAvXCJcIlwiLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIixcbiAgICBuZXh0OiBcInN0cmluZzNcIlxuICB9LCB7XG4gICAgcmVnZXg6IC8oU1RSSU5HOikoXFxzKS8sXG4gICAgdG9rZW46IFtcImtleXdvcmRcIiwgbnVsbF0sXG4gICAgbmV4dDogXCJzdHJpbmcyXCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvXFxTKj9cIi8sXG4gICAgdG9rZW46IFwic3RyaW5nXCIsXG4gICAgbmV4dDogXCJzdHJpbmdcIlxuICB9LFxuICAvLyBudW1iZXJzOiBkZWMsIGhleCwgdW5pY29kZSwgYmluLCBmcmFjdGlvbmFsLCBjb21wbGV4XG4gIHtcbiAgICByZWdleDogLyg/OjB4W1xcZCxhLWZdKyl8KD86MG9bMC03XSspfCg/OjBiWzAsMV0rKXwoPzpcXC0/XFxkKy4/XFxkKikoPz1cXHMpLyxcbiAgICB0b2tlbjogXCJudW1iZXJcIlxuICB9LFxuICAvL3tyZWdleDogL1srLV0/L30gLy9mcmFjdGlvbmFsXG4gIC8vIGRlZmluaXRpb246IGRlZmluaW5nIHdvcmQsIGRlZmluZWQgd29yZCwgZXRjXG4gIHtcbiAgICByZWdleDogLygoPzpHRU5FUklDKXxcXDo/XFw6KShcXHMrKShcXFMrKShcXHMrKShcXCgpLyxcbiAgICB0b2tlbjogW1wia2V5d29yZFwiLCBudWxsLCBcImRlZlwiLCBudWxsLCBcImJyYWNrZXRcIl0sXG4gICAgbmV4dDogXCJzdGFja1wiXG4gIH0sXG4gIC8vIG1ldGhvZCBkZWZpbml0aW9uOiBkZWZpbmluZyB3b3JkLCB0eXBlLCBkZWZpbmVkIHdvcmQsIGV0Y1xuICB7XG4gICAgcmVnZXg6IC8oTVxcOikoXFxzKykoXFxTKykoXFxzKykoXFxTKykvLFxuICAgIHRva2VuOiBbXCJrZXl3b3JkXCIsIG51bGwsIFwiZGVmXCIsIG51bGwsIFwidGFnXCJdXG4gIH0sXG4gIC8vIHZvY2FidWxhcnkgdXNpbmcgLS0+IHN0YXRlXG4gIHtcbiAgICByZWdleDogL1VTSU5HXFw6LyxcbiAgICB0b2tlbjogXCJrZXl3b3JkXCIsXG4gICAgbmV4dDogXCJ2b2NhYnVsYXJ5XCJcbiAgfSxcbiAgLy8gdm9jYWJ1bGFyeSBkZWZpbml0aW9uL3VzZVxuICB7XG4gICAgcmVnZXg6IC8oVVNFXFw6fElOXFw6KShcXHMrKShcXFMrKSg/PVxcc3wkKS8sXG4gICAgdG9rZW46IFtcImtleXdvcmRcIiwgbnVsbCwgXCJ0YWdcIl1cbiAgfSxcbiAgLy8gZGVmaW5pdGlvbjogYSBkZWZpbmluZyB3b3JkLCBkZWZpbmVkIHdvcmRcbiAge1xuICAgIHJlZ2V4OiAvKFxcUytcXDopKFxccyspKFxcUyspKD89XFxzfCQpLyxcbiAgICB0b2tlbjogW1wia2V5d29yZFwiLCBudWxsLCBcImRlZlwiXVxuICB9LFxuICAvLyBcImtleXdvcmRzXCIsIGluY2wuIDsgdCBmIC4gWyBdIHsgfSBkZWZpbmluZyB3b3Jkc1xuICB7XG4gICAgcmVnZXg6IC8oPzo7fFxcXFx8dHxmfGlmfGxvb3B8d2hpbGV8dW50aWx8ZG98UFJJVkFURT58PFBSSVZBVEV8XFwufFxcUypcXFt8XFxdfFxcUypcXHt8XFx9KSg/PVxcc3wkKS8sXG4gICAgdG9rZW46IFwia2V5d29yZFwiXG4gIH0sXG4gIC8vIDxjb25zdHJ1Y3RvcnM+IGFuZCB0aGUgbGlrZVxuICB7XG4gICAgcmVnZXg6IC9cXFMrW1xcKT5cXC5cXCpcXD9dKyg/PVxcc3wkKS8sXG4gICAgdG9rZW46IFwiYnVpbHRpblwiXG4gIH0sIHtcbiAgICByZWdleDogL1tcXCk+PF0rXFxTKyg/PVxcc3wkKS8sXG4gICAgdG9rZW46IFwiYnVpbHRpblwiXG4gIH0sXG4gIC8vIG9wZXJhdG9yc1xuICB7XG4gICAgcmVnZXg6IC8oPzpbXFwrXFwtXFw9XFwvXFwqPD5dKSg/PVxcc3wkKS8sXG4gICAgdG9rZW46IFwia2V5d29yZFwiXG4gIH0sXG4gIC8vIGFueSBpZCAoPylcbiAge1xuICAgIHJlZ2V4OiAvXFxTKy8sXG4gICAgdG9rZW46IFwidmFyaWFibGVcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cXHMrfC4vLFxuICAgIHRva2VuOiBudWxsXG4gIH1dLFxuICB2b2NhYnVsYXJ5OiBbe1xuICAgIHJlZ2V4OiAvOy8sXG4gICAgdG9rZW46IFwia2V5d29yZFwiLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cXFMrLyxcbiAgICB0b2tlbjogXCJ0YWdcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cXHMrfC4vLFxuICAgIHRva2VuOiBudWxsXG4gIH1dLFxuICBzdHJpbmc6IFt7XG4gICAgcmVnZXg6IC8oPzpbXlxcXFxdfFxcXFwuKSo/XCIvLFxuICAgIHRva2VuOiBcInN0cmluZ1wiLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC8uKi8sXG4gICAgdG9rZW46IFwic3RyaW5nXCJcbiAgfV0sXG4gIHN0cmluZzI6IFt7XG4gICAgcmVnZXg6IC9eOy8sXG4gICAgdG9rZW46IFwia2V5d29yZFwiLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC8uKi8sXG4gICAgdG9rZW46IFwic3RyaW5nXCJcbiAgfV0sXG4gIHN0cmluZzM6IFt7XG4gICAgcmVnZXg6IC8oPzpbXlxcXFxdfFxcXFwuKSo/XCJcIlwiLyxcbiAgICB0b2tlbjogXCJzdHJpbmdcIixcbiAgICBuZXh0OiBcInN0YXJ0XCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvLiovLFxuICAgIHRva2VuOiBcInN0cmluZ1wiXG4gIH1dLFxuICBzdGFjazogW3tcbiAgICByZWdleDogL1xcKS8sXG4gICAgdG9rZW46IFwiYnJhY2tldFwiLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC8tLS8sXG4gICAgdG9rZW46IFwiYnJhY2tldFwiXG4gIH0sIHtcbiAgICByZWdleDogL1xcUysvLFxuICAgIHRva2VuOiBcIm1ldGFcIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cXHMrfC4vLFxuICAgIHRva2VuOiBudWxsXG4gIH1dLFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBuYW1lOiBcImZhY3RvclwiLFxuICAgIGRvbnRJbmRlbnRTdGF0ZXM6IFtcInN0YXJ0XCIsIFwidm9jYWJ1bGFyeVwiLCBcInN0cmluZ1wiLCBcInN0cmluZzNcIiwgXCJzdGFja1wiXSxcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIiFcIlxuICAgIH1cbiAgfVxufSk7IiwiZXhwb3J0IGZ1bmN0aW9uIHNpbXBsZU1vZGUoc3RhdGVzKSB7XG4gIGVuc3VyZVN0YXRlKHN0YXRlcywgXCJzdGFydFwiKTtcbiAgdmFyIHN0YXRlc18gPSB7fSxcbiAgICBtZXRhID0gc3RhdGVzLmxhbmd1YWdlRGF0YSB8fCB7fSxcbiAgICBoYXNJbmRlbnRhdGlvbiA9IGZhbHNlO1xuICBmb3IgKHZhciBzdGF0ZSBpbiBzdGF0ZXMpIGlmIChzdGF0ZSAhPSBtZXRhICYmIHN0YXRlcy5oYXNPd25Qcm9wZXJ0eShzdGF0ZSkpIHtcbiAgICB2YXIgbGlzdCA9IHN0YXRlc19bc3RhdGVdID0gW10sXG4gICAgICBvcmlnID0gc3RhdGVzW3N0YXRlXTtcbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IG9yaWcubGVuZ3RoOyBpKyspIHtcbiAgICAgIHZhciBkYXRhID0gb3JpZ1tpXTtcbiAgICAgIGxpc3QucHVzaChuZXcgUnVsZShkYXRhLCBzdGF0ZXMpKTtcbiAgICAgIGlmIChkYXRhLmluZGVudCB8fCBkYXRhLmRlZGVudCkgaGFzSW5kZW50YXRpb24gPSB0cnVlO1xuICAgIH1cbiAgfVxuICByZXR1cm4ge1xuICAgIG5hbWU6IG1ldGEubmFtZSxcbiAgICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4ge1xuICAgICAgICBzdGF0ZTogXCJzdGFydFwiLFxuICAgICAgICBwZW5kaW5nOiBudWxsLFxuICAgICAgICBpbmRlbnQ6IGhhc0luZGVudGF0aW9uID8gW10gOiBudWxsXG4gICAgICB9O1xuICAgIH0sXG4gICAgY29weVN0YXRlOiBmdW5jdGlvbiAoc3RhdGUpIHtcbiAgICAgIHZhciBzID0ge1xuICAgICAgICBzdGF0ZTogc3RhdGUuc3RhdGUsXG4gICAgICAgIHBlbmRpbmc6IHN0YXRlLnBlbmRpbmcsXG4gICAgICAgIGluZGVudDogc3RhdGUuaW5kZW50ICYmIHN0YXRlLmluZGVudC5zbGljZSgwKVxuICAgICAgfTtcbiAgICAgIGlmIChzdGF0ZS5zdGFjaykgcy5zdGFjayA9IHN0YXRlLnN0YWNrLnNsaWNlKDApO1xuICAgICAgcmV0dXJuIHM7XG4gICAgfSxcbiAgICB0b2tlbjogdG9rZW5GdW5jdGlvbihzdGF0ZXNfKSxcbiAgICBpbmRlbnQ6IGluZGVudEZ1bmN0aW9uKHN0YXRlc18sIG1ldGEpLFxuICAgIG1lcmdlVG9rZW5zOiBtZXRhLm1lcmdlVG9rZW5zLFxuICAgIGxhbmd1YWdlRGF0YTogbWV0YVxuICB9O1xufVxuO1xuZnVuY3Rpb24gZW5zdXJlU3RhdGUoc3RhdGVzLCBuYW1lKSB7XG4gIGlmICghc3RhdGVzLmhhc093blByb3BlcnR5KG5hbWUpKSB0aHJvdyBuZXcgRXJyb3IoXCJVbmRlZmluZWQgc3RhdGUgXCIgKyBuYW1lICsgXCIgaW4gc2ltcGxlIG1vZGVcIik7XG59XG5mdW5jdGlvbiB0b1JlZ2V4KHZhbCwgY2FyZXQpIHtcbiAgaWYgKCF2YWwpIHJldHVybiAvKD86KS87XG4gIHZhciBmbGFncyA9IFwiXCI7XG4gIGlmICh2YWwgaW5zdGFuY2VvZiBSZWdFeHApIHtcbiAgICBpZiAodmFsLmlnbm9yZUNhc2UpIGZsYWdzID0gXCJpXCI7XG4gICAgaWYgKHZhbC51bmljb2RlKSBmbGFncyArPSBcInVcIjtcbiAgICB2YWwgPSB2YWwuc291cmNlO1xuICB9IGVsc2Uge1xuICAgIHZhbCA9IFN0cmluZyh2YWwpO1xuICB9XG4gIHJldHVybiBuZXcgUmVnRXhwKChjYXJldCA9PT0gZmFsc2UgPyBcIlwiIDogXCJeXCIpICsgXCIoPzpcIiArIHZhbCArIFwiKVwiLCBmbGFncyk7XG59XG5mdW5jdGlvbiBhc1Rva2VuKHZhbCkge1xuICBpZiAoIXZhbCkgcmV0dXJuIG51bGw7XG4gIGlmICh2YWwuYXBwbHkpIHJldHVybiB2YWw7XG4gIGlmICh0eXBlb2YgdmFsID09IFwic3RyaW5nXCIpIHJldHVybiB2YWwucmVwbGFjZSgvXFwuL2csIFwiIFwiKTtcbiAgdmFyIHJlc3VsdCA9IFtdO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHZhbC5sZW5ndGg7IGkrKykgcmVzdWx0LnB1c2godmFsW2ldICYmIHZhbFtpXS5yZXBsYWNlKC9cXC4vZywgXCIgXCIpKTtcbiAgcmV0dXJuIHJlc3VsdDtcbn1cbmZ1bmN0aW9uIFJ1bGUoZGF0YSwgc3RhdGVzKSB7XG4gIGlmIChkYXRhLm5leHQgfHwgZGF0YS5wdXNoKSBlbnN1cmVTdGF0ZShzdGF0ZXMsIGRhdGEubmV4dCB8fCBkYXRhLnB1c2gpO1xuICB0aGlzLnJlZ2V4ID0gdG9SZWdleChkYXRhLnJlZ2V4KTtcbiAgdGhpcy50b2tlbiA9IGFzVG9rZW4oZGF0YS50b2tlbik7XG4gIHRoaXMuZGF0YSA9IGRhdGE7XG59XG5mdW5jdGlvbiB0b2tlbkZ1bmN0aW9uKHN0YXRlcykge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RhdGUucGVuZGluZykge1xuICAgICAgdmFyIHBlbmQgPSBzdGF0ZS5wZW5kaW5nLnNoaWZ0KCk7XG4gICAgICBpZiAoc3RhdGUucGVuZGluZy5sZW5ndGggPT0gMCkgc3RhdGUucGVuZGluZyA9IG51bGw7XG4gICAgICBzdHJlYW0ucG9zICs9IHBlbmQudGV4dC5sZW5ndGg7XG4gICAgICByZXR1cm4gcGVuZC50b2tlbjtcbiAgICB9XG4gICAgdmFyIGN1clN0YXRlID0gc3RhdGVzW3N0YXRlLnN0YXRlXTtcbiAgICBmb3IgKHZhciBpID0gMDsgaSA8IGN1clN0YXRlLmxlbmd0aDsgaSsrKSB7XG4gICAgICB2YXIgcnVsZSA9IGN1clN0YXRlW2ldO1xuICAgICAgdmFyIG1hdGNoZXMgPSAoIXJ1bGUuZGF0YS5zb2wgfHwgc3RyZWFtLnNvbCgpKSAmJiBzdHJlYW0ubWF0Y2gocnVsZS5yZWdleCk7XG4gICAgICBpZiAobWF0Y2hlcykge1xuICAgICAgICBpZiAocnVsZS5kYXRhLm5leHQpIHtcbiAgICAgICAgICBzdGF0ZS5zdGF0ZSA9IHJ1bGUuZGF0YS5uZXh0O1xuICAgICAgICB9IGVsc2UgaWYgKHJ1bGUuZGF0YS5wdXNoKSB7XG4gICAgICAgICAgKHN0YXRlLnN0YWNrIHx8IChzdGF0ZS5zdGFjayA9IFtdKSkucHVzaChzdGF0ZS5zdGF0ZSk7XG4gICAgICAgICAgc3RhdGUuc3RhdGUgPSBydWxlLmRhdGEucHVzaDtcbiAgICAgICAgfSBlbHNlIGlmIChydWxlLmRhdGEucG9wICYmIHN0YXRlLnN0YWNrICYmIHN0YXRlLnN0YWNrLmxlbmd0aCkge1xuICAgICAgICAgIHN0YXRlLnN0YXRlID0gc3RhdGUuc3RhY2sucG9wKCk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHJ1bGUuZGF0YS5pbmRlbnQpIHN0YXRlLmluZGVudC5wdXNoKHN0cmVhbS5pbmRlbnRhdGlvbigpICsgc3RyZWFtLmluZGVudFVuaXQpO1xuICAgICAgICBpZiAocnVsZS5kYXRhLmRlZGVudCkgc3RhdGUuaW5kZW50LnBvcCgpO1xuICAgICAgICB2YXIgdG9rZW4gPSBydWxlLnRva2VuO1xuICAgICAgICBpZiAodG9rZW4gJiYgdG9rZW4uYXBwbHkpIHRva2VuID0gdG9rZW4obWF0Y2hlcyk7XG4gICAgICAgIGlmIChtYXRjaGVzLmxlbmd0aCA+IDIgJiYgcnVsZS50b2tlbiAmJiB0eXBlb2YgcnVsZS50b2tlbiAhPSBcInN0cmluZ1wiKSB7XG4gICAgICAgICAgc3RhdGUucGVuZGluZyA9IFtdO1xuICAgICAgICAgIGZvciAodmFyIGogPSAyOyBqIDwgbWF0Y2hlcy5sZW5ndGg7IGorKykgaWYgKG1hdGNoZXNbal0pIHN0YXRlLnBlbmRpbmcucHVzaCh7XG4gICAgICAgICAgICB0ZXh0OiBtYXRjaGVzW2pdLFxuICAgICAgICAgICAgdG9rZW46IHJ1bGUudG9rZW5baiAtIDFdXG4gICAgICAgICAgfSk7XG4gICAgICAgICAgc3RyZWFtLmJhY2tVcChtYXRjaGVzWzBdLmxlbmd0aCAtIChtYXRjaGVzWzFdID8gbWF0Y2hlc1sxXS5sZW5ndGggOiAwKSk7XG4gICAgICAgICAgcmV0dXJuIHRva2VuWzBdO1xuICAgICAgICB9IGVsc2UgaWYgKHRva2VuICYmIHRva2VuLmpvaW4pIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW5bMF07XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgcmV0dXJuIHRva2VuO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH07XG59XG5mdW5jdGlvbiBpbmRlbnRGdW5jdGlvbihzdGF0ZXMsIG1ldGEpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyKSB7XG4gICAgaWYgKHN0YXRlLmluZGVudCA9PSBudWxsIHx8IG1ldGEuZG9udEluZGVudFN0YXRlcyAmJiBtZXRhLmRvbnRJbmRlbnRTdGF0ZXMuaW5kZXhPZihzdGF0ZS5zdGF0ZSkgPiAtMSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIHBvcyA9IHN0YXRlLmluZGVudC5sZW5ndGggLSAxLFxuICAgICAgcnVsZXMgPSBzdGF0ZXNbc3RhdGUuc3RhdGVdO1xuICAgIHNjYW46IGZvciAoOzspIHtcbiAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgcnVsZXMubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgdmFyIHJ1bGUgPSBydWxlc1tpXTtcbiAgICAgICAgaWYgKHJ1bGUuZGF0YS5kZWRlbnQgJiYgcnVsZS5kYXRhLmRlZGVudElmTGluZVN0YXJ0ICE9PSBmYWxzZSkge1xuICAgICAgICAgIHZhciBtID0gcnVsZS5yZWdleC5leGVjKHRleHRBZnRlcik7XG4gICAgICAgICAgaWYgKG0gJiYgbVswXSkge1xuICAgICAgICAgICAgcG9zLS07XG4gICAgICAgICAgICBpZiAocnVsZS5uZXh0IHx8IHJ1bGUucHVzaCkgcnVsZXMgPSBzdGF0ZXNbcnVsZS5uZXh0IHx8IHJ1bGUucHVzaF07XG4gICAgICAgICAgICB0ZXh0QWZ0ZXIgPSB0ZXh0QWZ0ZXIuc2xpY2UobVswXS5sZW5ndGgpO1xuICAgICAgICAgICAgY29udGludWUgc2NhbjtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICByZXR1cm4gcG9zIDwgMCA/IDAgOiBzdGF0ZS5pbmRlbnRbcG9zXTtcbiAgfTtcbn0iXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9