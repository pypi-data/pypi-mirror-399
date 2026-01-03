"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9801],{

/***/ 29801
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   liveScript: () => (/* binding */ liveScript)
/* harmony export */ });
var tokenBase = function (stream, state) {
  var next_rule = state.next || "start";
  if (next_rule) {
    state.next = state.next;
    var nr = Rules[next_rule];
    if (nr.splice) {
      for (var i$ = 0; i$ < nr.length; ++i$) {
        var r = nr[i$];
        if (r.regex && stream.match(r.regex)) {
          state.next = r.next || state.next;
          return r.token;
        }
      }
      stream.next();
      return 'error';
    }
    if (stream.match(r = Rules[next_rule])) {
      if (r.regex && stream.match(r.regex)) {
        state.next = r.next;
        return r.token;
      } else {
        stream.next();
        return 'error';
      }
    }
  }
  stream.next();
  return 'error';
};
var identifier = '(?![\\d\\s])[$\\w\\xAA-\\uFFDC](?:(?!\\s)[$\\w\\xAA-\\uFFDC]|-[A-Za-z])*';
var indenter = RegExp('(?:[({[=:]|[-~]>|\\b(?:e(?:lse|xport)|d(?:o|efault)|t(?:ry|hen)|finally|import(?:\\s*all)?|const|var|let|new|catch(?:\\s*' + identifier + ')?))\\s*$');
var keywordend = '(?![$\\w]|-[A-Za-z]|\\s*:(?![:=]))';
var stringfill = {
  token: 'string',
  regex: '.+'
};
var Rules = {
  start: [{
    token: 'docComment',
    regex: '/\\*',
    next: 'comment'
  }, {
    token: 'comment',
    regex: '#.*'
  }, {
    token: 'keyword',
    regex: '(?:t(?:h(?:is|row|en)|ry|ypeof!?)|c(?:on(?:tinue|st)|a(?:se|tch)|lass)|i(?:n(?:stanceof)?|mp(?:ort(?:\\s+all)?|lements)|[fs])|d(?:e(?:fault|lete|bugger)|o)|f(?:or(?:\\s+own)?|inally|unction)|s(?:uper|witch)|e(?:lse|x(?:tends|port)|val)|a(?:nd|rguments)|n(?:ew|ot)|un(?:less|til)|w(?:hile|ith)|o[fr]|return|break|let|var|loop)' + keywordend
  }, {
    token: 'atom',
    regex: '(?:true|false|yes|no|on|off|null|void|undefined)' + keywordend
  }, {
    token: 'invalid',
    regex: '(?:p(?:ackage|r(?:ivate|otected)|ublic)|i(?:mplements|nterface)|enum|static|yield)' + keywordend
  }, {
    token: 'className.standard',
    regex: '(?:R(?:e(?:gExp|ferenceError)|angeError)|S(?:tring|yntaxError)|E(?:rror|valError)|Array|Boolean|Date|Function|Number|Object|TypeError|URIError)' + keywordend
  }, {
    token: 'variableName.function.standard',
    regex: '(?:is(?:NaN|Finite)|parse(?:Int|Float)|Math|JSON|(?:en|de)codeURI(?:Component)?)' + keywordend
  }, {
    token: 'variableName.standard',
    regex: '(?:t(?:hat|il|o)|f(?:rom|allthrough)|it|by|e)' + keywordend
  }, {
    token: 'variableName',
    regex: identifier + '\\s*:(?![:=])'
  }, {
    token: 'variableName',
    regex: identifier
  }, {
    token: 'operatorKeyword',
    regex: '(?:\\.{3}|\\s+\\?)'
  }, {
    token: 'keyword',
    regex: '(?:@+|::|\\.\\.)',
    next: 'key'
  }, {
    token: 'operatorKeyword',
    regex: '\\.\\s*',
    next: 'key'
  }, {
    token: 'string',
    regex: '\\\\\\S[^\\s,;)}\\]]*'
  }, {
    token: 'docString',
    regex: '\'\'\'',
    next: 'qdoc'
  }, {
    token: 'docString',
    regex: '"""',
    next: 'qqdoc'
  }, {
    token: 'string',
    regex: '\'',
    next: 'qstring'
  }, {
    token: 'string',
    regex: '"',
    next: 'qqstring'
  }, {
    token: 'string',
    regex: '`',
    next: 'js'
  }, {
    token: 'string',
    regex: '<\\[',
    next: 'words'
  }, {
    token: 'regexp',
    regex: '//',
    next: 'heregex'
  }, {
    token: 'regexp',
    regex: '\\/(?:[^[\\/\\n\\\\]*(?:(?:\\\\.|\\[[^\\]\\n\\\\]*(?:\\\\.[^\\]\\n\\\\]*)*\\])[^[\\/\\n\\\\]*)*)\\/[gimy$]{0,4}',
    next: 'key'
  }, {
    token: 'number',
    regex: '(?:0x[\\da-fA-F][\\da-fA-F_]*|(?:[2-9]|[12]\\d|3[0-6])r[\\da-zA-Z][\\da-zA-Z_]*|(?:\\d[\\d_]*(?:\\.\\d[\\d_]*)?|\\.\\d[\\d_]*)(?:e[+-]?\\d[\\d_]*)?[\\w$]*)'
  }, {
    token: 'paren',
    regex: '[({[]'
  }, {
    token: 'paren',
    regex: '[)}\\]]',
    next: 'key'
  }, {
    token: 'operatorKeyword',
    regex: '\\S+'
  }, {
    token: 'content',
    regex: '\\s+'
  }],
  heregex: [{
    token: 'regexp',
    regex: '.*?//[gimy$?]{0,4}',
    next: 'start'
  }, {
    token: 'regexp',
    regex: '\\s*#{'
  }, {
    token: 'comment',
    regex: '\\s+(?:#.*)?'
  }, {
    token: 'regexp',
    regex: '\\S+'
  }],
  key: [{
    token: 'operatorKeyword',
    regex: '[.?@!]+'
  }, {
    token: 'variableName',
    regex: identifier,
    next: 'start'
  }, {
    token: 'content',
    regex: '',
    next: 'start'
  }],
  comment: [{
    token: 'docComment',
    regex: '.*?\\*/',
    next: 'start'
  }, {
    token: 'docComment',
    regex: '.+'
  }],
  qdoc: [{
    token: 'string',
    regex: ".*?'''",
    next: 'key'
  }, stringfill],
  qqdoc: [{
    token: 'string',
    regex: '.*?"""',
    next: 'key'
  }, stringfill],
  qstring: [{
    token: 'string',
    regex: '[^\\\\\']*(?:\\\\.[^\\\\\']*)*\'',
    next: 'key'
  }, stringfill],
  qqstring: [{
    token: 'string',
    regex: '[^\\\\"]*(?:\\\\.[^\\\\"]*)*"',
    next: 'key'
  }, stringfill],
  js: [{
    token: 'string',
    regex: '[^\\\\`]*(?:\\\\.[^\\\\`]*)*`',
    next: 'key'
  }, stringfill],
  words: [{
    token: 'string',
    regex: '.*?\\]>',
    next: 'key'
  }, stringfill]
};
for (var idx in Rules) {
  var r = Rules[idx];
  if (r.splice) {
    for (var i = 0, len = r.length; i < len; ++i) {
      var rr = r[i];
      if (typeof rr.regex === 'string') {
        Rules[idx][i].regex = new RegExp('^' + rr.regex);
      }
    }
  } else if (typeof rr.regex === 'string') {
    Rules[idx].regex = new RegExp('^' + r.regex);
  }
}
const liveScript = {
  name: "livescript",
  startState: function () {
    return {
      next: 'start',
      lastToken: {
        style: null,
        indent: 0,
        content: ""
      }
    };
  },
  token: function (stream, state) {
    while (stream.pos == stream.start) var style = tokenBase(stream, state);
    state.lastToken = {
      style: style,
      indent: stream.indentation(),
      content: stream.current()
    };
    return style.replace(/\./g, ' ');
  },
  indent: function (state) {
    var indentation = state.lastToken.indent;
    if (state.lastToken.content.match(indenter)) {
      indentation += 2;
    }
    return indentation;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTgwMS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvbGl2ZXNjcmlwdC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgdG9rZW5CYXNlID0gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG5leHRfcnVsZSA9IHN0YXRlLm5leHQgfHwgXCJzdGFydFwiO1xuICBpZiAobmV4dF9ydWxlKSB7XG4gICAgc3RhdGUubmV4dCA9IHN0YXRlLm5leHQ7XG4gICAgdmFyIG5yID0gUnVsZXNbbmV4dF9ydWxlXTtcbiAgICBpZiAobnIuc3BsaWNlKSB7XG4gICAgICBmb3IgKHZhciBpJCA9IDA7IGkkIDwgbnIubGVuZ3RoOyArK2kkKSB7XG4gICAgICAgIHZhciByID0gbnJbaSRdO1xuICAgICAgICBpZiAoci5yZWdleCAmJiBzdHJlYW0ubWF0Y2goci5yZWdleCkpIHtcbiAgICAgICAgICBzdGF0ZS5uZXh0ID0gci5uZXh0IHx8IHN0YXRlLm5leHQ7XG4gICAgICAgICAgcmV0dXJuIHIudG9rZW47XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICByZXR1cm4gJ2Vycm9yJztcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChyID0gUnVsZXNbbmV4dF9ydWxlXSkpIHtcbiAgICAgIGlmIChyLnJlZ2V4ICYmIHN0cmVhbS5tYXRjaChyLnJlZ2V4KSkge1xuICAgICAgICBzdGF0ZS5uZXh0ID0gci5uZXh0O1xuICAgICAgICByZXR1cm4gci50b2tlbjtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICAgIHJldHVybiAnZXJyb3InO1xuICAgICAgfVxuICAgIH1cbiAgfVxuICBzdHJlYW0ubmV4dCgpO1xuICByZXR1cm4gJ2Vycm9yJztcbn07XG52YXIgaWRlbnRpZmllciA9ICcoPyFbXFxcXGRcXFxcc10pWyRcXFxcd1xcXFx4QUEtXFxcXHVGRkRDXSg/Oig/IVxcXFxzKVskXFxcXHdcXFxceEFBLVxcXFx1RkZEQ118LVtBLVphLXpdKSonO1xudmFyIGluZGVudGVyID0gUmVnRXhwKCcoPzpbKHtbPTpdfFstfl0+fFxcXFxiKD86ZSg/OmxzZXx4cG9ydCl8ZCg/Om98ZWZhdWx0KXx0KD86cnl8aGVuKXxmaW5hbGx5fGltcG9ydCg/OlxcXFxzKmFsbCk/fGNvbnN0fHZhcnxsZXR8bmV3fGNhdGNoKD86XFxcXHMqJyArIGlkZW50aWZpZXIgKyAnKT8pKVxcXFxzKiQnKTtcbnZhciBrZXl3b3JkZW5kID0gJyg/IVskXFxcXHddfC1bQS1aYS16XXxcXFxccyo6KD8hWzo9XSkpJztcbnZhciBzdHJpbmdmaWxsID0ge1xuICB0b2tlbjogJ3N0cmluZycsXG4gIHJlZ2V4OiAnLisnXG59O1xudmFyIFJ1bGVzID0ge1xuICBzdGFydDogW3tcbiAgICB0b2tlbjogJ2RvY0NvbW1lbnQnLFxuICAgIHJlZ2V4OiAnL1xcXFwqJyxcbiAgICBuZXh0OiAnY29tbWVudCdcbiAgfSwge1xuICAgIHRva2VuOiAnY29tbWVudCcsXG4gICAgcmVnZXg6ICcjLionXG4gIH0sIHtcbiAgICB0b2tlbjogJ2tleXdvcmQnLFxuICAgIHJlZ2V4OiAnKD86dCg/OmgoPzppc3xyb3d8ZW4pfHJ5fHlwZW9mIT8pfGMoPzpvbig/OnRpbnVlfHN0KXxhKD86c2V8dGNoKXxsYXNzKXxpKD86big/OnN0YW5jZW9mKT98bXAoPzpvcnQoPzpcXFxccythbGwpP3xsZW1lbnRzKXxbZnNdKXxkKD86ZSg/OmZhdWx0fGxldGV8YnVnZ2VyKXxvKXxmKD86b3IoPzpcXFxccytvd24pP3xpbmFsbHl8dW5jdGlvbil8cyg/OnVwZXJ8d2l0Y2gpfGUoPzpsc2V8eCg/OnRlbmRzfHBvcnQpfHZhbCl8YSg/Om5kfHJndW1lbnRzKXxuKD86ZXd8b3QpfHVuKD86bGVzc3x0aWwpfHcoPzpoaWxlfGl0aCl8b1tmcl18cmV0dXJufGJyZWFrfGxldHx2YXJ8bG9vcCknICsga2V5d29yZGVuZFxuICB9LCB7XG4gICAgdG9rZW46ICdhdG9tJyxcbiAgICByZWdleDogJyg/OnRydWV8ZmFsc2V8eWVzfG5vfG9ufG9mZnxudWxsfHZvaWR8dW5kZWZpbmVkKScgKyBrZXl3b3JkZW5kXG4gIH0sIHtcbiAgICB0b2tlbjogJ2ludmFsaWQnLFxuICAgIHJlZ2V4OiAnKD86cCg/OmFja2FnZXxyKD86aXZhdGV8b3RlY3RlZCl8dWJsaWMpfGkoPzptcGxlbWVudHN8bnRlcmZhY2UpfGVudW18c3RhdGljfHlpZWxkKScgKyBrZXl3b3JkZW5kXG4gIH0sIHtcbiAgICB0b2tlbjogJ2NsYXNzTmFtZS5zdGFuZGFyZCcsXG4gICAgcmVnZXg6ICcoPzpSKD86ZSg/OmdFeHB8ZmVyZW5jZUVycm9yKXxhbmdlRXJyb3IpfFMoPzp0cmluZ3x5bnRheEVycm9yKXxFKD86cnJvcnx2YWxFcnJvcil8QXJyYXl8Qm9vbGVhbnxEYXRlfEZ1bmN0aW9ufE51bWJlcnxPYmplY3R8VHlwZUVycm9yfFVSSUVycm9yKScgKyBrZXl3b3JkZW5kXG4gIH0sIHtcbiAgICB0b2tlbjogJ3ZhcmlhYmxlTmFtZS5mdW5jdGlvbi5zdGFuZGFyZCcsXG4gICAgcmVnZXg6ICcoPzppcyg/Ok5hTnxGaW5pdGUpfHBhcnNlKD86SW50fEZsb2F0KXxNYXRofEpTT058KD86ZW58ZGUpY29kZVVSSSg/OkNvbXBvbmVudCk/KScgKyBrZXl3b3JkZW5kXG4gIH0sIHtcbiAgICB0b2tlbjogJ3ZhcmlhYmxlTmFtZS5zdGFuZGFyZCcsXG4gICAgcmVnZXg6ICcoPzp0KD86aGF0fGlsfG8pfGYoPzpyb218YWxsdGhyb3VnaCl8aXR8Ynl8ZSknICsga2V5d29yZGVuZFxuICB9LCB7XG4gICAgdG9rZW46ICd2YXJpYWJsZU5hbWUnLFxuICAgIHJlZ2V4OiBpZGVudGlmaWVyICsgJ1xcXFxzKjooPyFbOj1dKSdcbiAgfSwge1xuICAgIHRva2VuOiAndmFyaWFibGVOYW1lJyxcbiAgICByZWdleDogaWRlbnRpZmllclxuICB9LCB7XG4gICAgdG9rZW46ICdvcGVyYXRvcktleXdvcmQnLFxuICAgIHJlZ2V4OiAnKD86XFxcXC57M318XFxcXHMrXFxcXD8pJ1xuICB9LCB7XG4gICAgdG9rZW46ICdrZXl3b3JkJyxcbiAgICByZWdleDogJyg/OkArfDo6fFxcXFwuXFxcXC4pJyxcbiAgICBuZXh0OiAna2V5J1xuICB9LCB7XG4gICAgdG9rZW46ICdvcGVyYXRvcktleXdvcmQnLFxuICAgIHJlZ2V4OiAnXFxcXC5cXFxccyonLFxuICAgIG5leHQ6ICdrZXknXG4gIH0sIHtcbiAgICB0b2tlbjogJ3N0cmluZycsXG4gICAgcmVnZXg6ICdcXFxcXFxcXFxcXFxTW15cXFxccyw7KX1cXFxcXV0qJ1xuICB9LCB7XG4gICAgdG9rZW46ICdkb2NTdHJpbmcnLFxuICAgIHJlZ2V4OiAnXFwnXFwnXFwnJyxcbiAgICBuZXh0OiAncWRvYydcbiAgfSwge1xuICAgIHRva2VuOiAnZG9jU3RyaW5nJyxcbiAgICByZWdleDogJ1wiXCJcIicsXG4gICAgbmV4dDogJ3FxZG9jJ1xuICB9LCB7XG4gICAgdG9rZW46ICdzdHJpbmcnLFxuICAgIHJlZ2V4OiAnXFwnJyxcbiAgICBuZXh0OiAncXN0cmluZydcbiAgfSwge1xuICAgIHRva2VuOiAnc3RyaW5nJyxcbiAgICByZWdleDogJ1wiJyxcbiAgICBuZXh0OiAncXFzdHJpbmcnXG4gIH0sIHtcbiAgICB0b2tlbjogJ3N0cmluZycsXG4gICAgcmVnZXg6ICdgJyxcbiAgICBuZXh0OiAnanMnXG4gIH0sIHtcbiAgICB0b2tlbjogJ3N0cmluZycsXG4gICAgcmVnZXg6ICc8XFxcXFsnLFxuICAgIG5leHQ6ICd3b3JkcydcbiAgfSwge1xuICAgIHRva2VuOiAncmVnZXhwJyxcbiAgICByZWdleDogJy8vJyxcbiAgICBuZXh0OiAnaGVyZWdleCdcbiAgfSwge1xuICAgIHRva2VuOiAncmVnZXhwJyxcbiAgICByZWdleDogJ1xcXFwvKD86W15bXFxcXC9cXFxcblxcXFxcXFxcXSooPzooPzpcXFxcXFxcXC58XFxcXFtbXlxcXFxdXFxcXG5cXFxcXFxcXF0qKD86XFxcXFxcXFwuW15cXFxcXVxcXFxuXFxcXFxcXFxdKikqXFxcXF0pW15bXFxcXC9cXFxcblxcXFxcXFxcXSopKilcXFxcL1tnaW15JF17MCw0fScsXG4gICAgbmV4dDogJ2tleSdcbiAgfSwge1xuICAgIHRva2VuOiAnbnVtYmVyJyxcbiAgICByZWdleDogJyg/OjB4W1xcXFxkYS1mQS1GXVtcXFxcZGEtZkEtRl9dKnwoPzpbMi05XXxbMTJdXFxcXGR8M1swLTZdKXJbXFxcXGRhLXpBLVpdW1xcXFxkYS16QS1aX10qfCg/OlxcXFxkW1xcXFxkX10qKD86XFxcXC5cXFxcZFtcXFxcZF9dKik/fFxcXFwuXFxcXGRbXFxcXGRfXSopKD86ZVsrLV0/XFxcXGRbXFxcXGRfXSopP1tcXFxcdyRdKiknXG4gIH0sIHtcbiAgICB0b2tlbjogJ3BhcmVuJyxcbiAgICByZWdleDogJ1soe1tdJ1xuICB9LCB7XG4gICAgdG9rZW46ICdwYXJlbicsXG4gICAgcmVnZXg6ICdbKX1cXFxcXV0nLFxuICAgIG5leHQ6ICdrZXknXG4gIH0sIHtcbiAgICB0b2tlbjogJ29wZXJhdG9yS2V5d29yZCcsXG4gICAgcmVnZXg6ICdcXFxcUysnXG4gIH0sIHtcbiAgICB0b2tlbjogJ2NvbnRlbnQnLFxuICAgIHJlZ2V4OiAnXFxcXHMrJ1xuICB9XSxcbiAgaGVyZWdleDogW3tcbiAgICB0b2tlbjogJ3JlZ2V4cCcsXG4gICAgcmVnZXg6ICcuKj8vL1tnaW15JD9dezAsNH0nLFxuICAgIG5leHQ6ICdzdGFydCdcbiAgfSwge1xuICAgIHRva2VuOiAncmVnZXhwJyxcbiAgICByZWdleDogJ1xcXFxzKiN7J1xuICB9LCB7XG4gICAgdG9rZW46ICdjb21tZW50JyxcbiAgICByZWdleDogJ1xcXFxzKyg/OiMuKik/J1xuICB9LCB7XG4gICAgdG9rZW46ICdyZWdleHAnLFxuICAgIHJlZ2V4OiAnXFxcXFMrJ1xuICB9XSxcbiAga2V5OiBbe1xuICAgIHRva2VuOiAnb3BlcmF0b3JLZXl3b3JkJyxcbiAgICByZWdleDogJ1suP0AhXSsnXG4gIH0sIHtcbiAgICB0b2tlbjogJ3ZhcmlhYmxlTmFtZScsXG4gICAgcmVnZXg6IGlkZW50aWZpZXIsXG4gICAgbmV4dDogJ3N0YXJ0J1xuICB9LCB7XG4gICAgdG9rZW46ICdjb250ZW50JyxcbiAgICByZWdleDogJycsXG4gICAgbmV4dDogJ3N0YXJ0J1xuICB9XSxcbiAgY29tbWVudDogW3tcbiAgICB0b2tlbjogJ2RvY0NvbW1lbnQnLFxuICAgIHJlZ2V4OiAnLio/XFxcXCovJyxcbiAgICBuZXh0OiAnc3RhcnQnXG4gIH0sIHtcbiAgICB0b2tlbjogJ2RvY0NvbW1lbnQnLFxuICAgIHJlZ2V4OiAnLisnXG4gIH1dLFxuICBxZG9jOiBbe1xuICAgIHRva2VuOiAnc3RyaW5nJyxcbiAgICByZWdleDogXCIuKj8nJydcIixcbiAgICBuZXh0OiAna2V5J1xuICB9LCBzdHJpbmdmaWxsXSxcbiAgcXFkb2M6IFt7XG4gICAgdG9rZW46ICdzdHJpbmcnLFxuICAgIHJlZ2V4OiAnLio/XCJcIlwiJyxcbiAgICBuZXh0OiAna2V5J1xuICB9LCBzdHJpbmdmaWxsXSxcbiAgcXN0cmluZzogW3tcbiAgICB0b2tlbjogJ3N0cmluZycsXG4gICAgcmVnZXg6ICdbXlxcXFxcXFxcXFwnXSooPzpcXFxcXFxcXC5bXlxcXFxcXFxcXFwnXSopKlxcJycsXG4gICAgbmV4dDogJ2tleSdcbiAgfSwgc3RyaW5nZmlsbF0sXG4gIHFxc3RyaW5nOiBbe1xuICAgIHRva2VuOiAnc3RyaW5nJyxcbiAgICByZWdleDogJ1teXFxcXFxcXFxcIl0qKD86XFxcXFxcXFwuW15cXFxcXFxcXFwiXSopKlwiJyxcbiAgICBuZXh0OiAna2V5J1xuICB9LCBzdHJpbmdmaWxsXSxcbiAganM6IFt7XG4gICAgdG9rZW46ICdzdHJpbmcnLFxuICAgIHJlZ2V4OiAnW15cXFxcXFxcXGBdKig/OlxcXFxcXFxcLlteXFxcXFxcXFxgXSopKmAnLFxuICAgIG5leHQ6ICdrZXknXG4gIH0sIHN0cmluZ2ZpbGxdLFxuICB3b3JkczogW3tcbiAgICB0b2tlbjogJ3N0cmluZycsXG4gICAgcmVnZXg6ICcuKj9cXFxcXT4nLFxuICAgIG5leHQ6ICdrZXknXG4gIH0sIHN0cmluZ2ZpbGxdXG59O1xuZm9yICh2YXIgaWR4IGluIFJ1bGVzKSB7XG4gIHZhciByID0gUnVsZXNbaWR4XTtcbiAgaWYgKHIuc3BsaWNlKSB7XG4gICAgZm9yICh2YXIgaSA9IDAsIGxlbiA9IHIubGVuZ3RoOyBpIDwgbGVuOyArK2kpIHtcbiAgICAgIHZhciByciA9IHJbaV07XG4gICAgICBpZiAodHlwZW9mIHJyLnJlZ2V4ID09PSAnc3RyaW5nJykge1xuICAgICAgICBSdWxlc1tpZHhdW2ldLnJlZ2V4ID0gbmV3IFJlZ0V4cCgnXicgKyByci5yZWdleCk7XG4gICAgICB9XG4gICAgfVxuICB9IGVsc2UgaWYgKHR5cGVvZiByci5yZWdleCA9PT0gJ3N0cmluZycpIHtcbiAgICBSdWxlc1tpZHhdLnJlZ2V4ID0gbmV3IFJlZ0V4cCgnXicgKyByLnJlZ2V4KTtcbiAgfVxufVxuZXhwb3J0IGNvbnN0IGxpdmVTY3JpcHQgPSB7XG4gIG5hbWU6IFwibGl2ZXNjcmlwdFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIG5leHQ6ICdzdGFydCcsXG4gICAgICBsYXN0VG9rZW46IHtcbiAgICAgICAgc3R5bGU6IG51bGwsXG4gICAgICAgIGluZGVudDogMCxcbiAgICAgICAgY29udGVudDogXCJcIlxuICAgICAgfVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlIChzdHJlYW0ucG9zID09IHN0cmVhbS5zdGFydCkgdmFyIHN0eWxlID0gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpO1xuICAgIHN0YXRlLmxhc3RUb2tlbiA9IHtcbiAgICAgIHN0eWxlOiBzdHlsZSxcbiAgICAgIGluZGVudDogc3RyZWFtLmluZGVudGF0aW9uKCksXG4gICAgICBjb250ZW50OiBzdHJlYW0uY3VycmVudCgpXG4gICAgfTtcbiAgICByZXR1cm4gc3R5bGUucmVwbGFjZSgvXFwuL2csICcgJyk7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlKSB7XG4gICAgdmFyIGluZGVudGF0aW9uID0gc3RhdGUubGFzdFRva2VuLmluZGVudDtcbiAgICBpZiAoc3RhdGUubGFzdFRva2VuLmNvbnRlbnQubWF0Y2goaW5kZW50ZXIpKSB7XG4gICAgICBpbmRlbnRhdGlvbiArPSAyO1xuICAgIH1cbiAgICByZXR1cm4gaW5kZW50YXRpb247XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==