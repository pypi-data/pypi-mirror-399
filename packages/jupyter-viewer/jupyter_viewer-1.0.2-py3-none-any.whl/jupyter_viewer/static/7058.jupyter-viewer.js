"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7058],{

/***/ 37058
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   fSharp: () => (/* binding */ fSharp),
/* harmony export */   oCaml: () => (/* binding */ oCaml),
/* harmony export */   sml: () => (/* binding */ sml)
/* harmony export */ });
function mlLike(parserConfig) {
  var words = {
    'as': 'keyword',
    'do': 'keyword',
    'else': 'keyword',
    'end': 'keyword',
    'exception': 'keyword',
    'fun': 'keyword',
    'functor': 'keyword',
    'if': 'keyword',
    'in': 'keyword',
    'include': 'keyword',
    'let': 'keyword',
    'of': 'keyword',
    'open': 'keyword',
    'rec': 'keyword',
    'struct': 'keyword',
    'then': 'keyword',
    'type': 'keyword',
    'val': 'keyword',
    'while': 'keyword',
    'with': 'keyword'
  };
  var extraWords = parserConfig.extraWords || {};
  for (var prop in extraWords) {
    if (extraWords.hasOwnProperty(prop)) {
      words[prop] = parserConfig.extraWords[prop];
    }
  }
  var hintWords = [];
  for (var k in words) {
    hintWords.push(k);
  }
  function tokenBase(stream, state) {
    var ch = stream.next();
    if (ch === '"') {
      state.tokenize = tokenString;
      return state.tokenize(stream, state);
    }
    if (ch === '{') {
      if (stream.eat('|')) {
        state.longString = true;
        state.tokenize = tokenLongString;
        return state.tokenize(stream, state);
      }
    }
    if (ch === '(') {
      if (stream.match(/^\*(?!\))/)) {
        state.commentLevel++;
        state.tokenize = tokenComment;
        return state.tokenize(stream, state);
      }
    }
    if (ch === '~' || ch === '?') {
      stream.eatWhile(/\w/);
      return 'variableName.special';
    }
    if (ch === '`') {
      stream.eatWhile(/\w/);
      return 'quote';
    }
    if (ch === '/' && parserConfig.slashComments && stream.eat('/')) {
      stream.skipToEnd();
      return 'comment';
    }
    if (/\d/.test(ch)) {
      if (ch === '0' && stream.eat(/[bB]/)) {
        stream.eatWhile(/[01]/);
      }
      if (ch === '0' && stream.eat(/[xX]/)) {
        stream.eatWhile(/[0-9a-fA-F]/);
      }
      if (ch === '0' && stream.eat(/[oO]/)) {
        stream.eatWhile(/[0-7]/);
      } else {
        stream.eatWhile(/[\d_]/);
        if (stream.eat('.')) {
          stream.eatWhile(/[\d]/);
        }
        if (stream.eat(/[eE]/)) {
          stream.eatWhile(/[\d\-+]/);
        }
      }
      return 'number';
    }
    if (/[+\-*&%=<>!?|@\.~:]/.test(ch)) {
      return 'operator';
    }
    if (/[\w\xa1-\uffff]/.test(ch)) {
      stream.eatWhile(/[\w\xa1-\uffff]/);
      var cur = stream.current();
      return words.hasOwnProperty(cur) ? words[cur] : 'variable';
    }
    return null;
  }
  function tokenString(stream, state) {
    var next,
      end = false,
      escaped = false;
    while ((next = stream.next()) != null) {
      if (next === '"' && !escaped) {
        end = true;
        break;
      }
      escaped = !escaped && next === '\\';
    }
    if (end && !escaped) {
      state.tokenize = tokenBase;
    }
    return 'string';
  }
  ;
  function tokenComment(stream, state) {
    var prev, next;
    while (state.commentLevel > 0 && (next = stream.next()) != null) {
      if (prev === '(' && next === '*') state.commentLevel++;
      if (prev === '*' && next === ')') state.commentLevel--;
      prev = next;
    }
    if (state.commentLevel <= 0) {
      state.tokenize = tokenBase;
    }
    return 'comment';
  }
  function tokenLongString(stream, state) {
    var prev, next;
    while (state.longString && (next = stream.next()) != null) {
      if (prev === '|' && next === '}') state.longString = false;
      prev = next;
    }
    if (!state.longString) {
      state.tokenize = tokenBase;
    }
    return 'string';
  }
  return {
    startState: function () {
      return {
        tokenize: tokenBase,
        commentLevel: 0,
        longString: false
      };
    },
    token: function (stream, state) {
      if (stream.eatSpace()) return null;
      return state.tokenize(stream, state);
    },
    languageData: {
      autocomplete: hintWords,
      commentTokens: {
        line: parserConfig.slashComments ? "//" : undefined,
        block: {
          open: "(*",
          close: "*)"
        }
      }
    }
  };
}
;
const oCaml = mlLike({
  name: "ocaml",
  extraWords: {
    'and': 'keyword',
    'assert': 'keyword',
    'begin': 'keyword',
    'class': 'keyword',
    'constraint': 'keyword',
    'done': 'keyword',
    'downto': 'keyword',
    'external': 'keyword',
    'function': 'keyword',
    'initializer': 'keyword',
    'lazy': 'keyword',
    'match': 'keyword',
    'method': 'keyword',
    'module': 'keyword',
    'mutable': 'keyword',
    'new': 'keyword',
    'nonrec': 'keyword',
    'object': 'keyword',
    'private': 'keyword',
    'sig': 'keyword',
    'to': 'keyword',
    'try': 'keyword',
    'value': 'keyword',
    'virtual': 'keyword',
    'when': 'keyword',
    // builtins
    'raise': 'builtin',
    'failwith': 'builtin',
    'true': 'builtin',
    'false': 'builtin',
    // Pervasives builtins
    'asr': 'builtin',
    'land': 'builtin',
    'lor': 'builtin',
    'lsl': 'builtin',
    'lsr': 'builtin',
    'lxor': 'builtin',
    'mod': 'builtin',
    'or': 'builtin',
    // More Pervasives
    'raise_notrace': 'builtin',
    'trace': 'builtin',
    'exit': 'builtin',
    'print_string': 'builtin',
    'print_endline': 'builtin',
    'int': 'type',
    'float': 'type',
    'bool': 'type',
    'char': 'type',
    'string': 'type',
    'unit': 'type',
    // Modules
    'List': 'builtin'
  }
});
const fSharp = mlLike({
  name: "fsharp",
  extraWords: {
    'abstract': 'keyword',
    'assert': 'keyword',
    'base': 'keyword',
    'begin': 'keyword',
    'class': 'keyword',
    'default': 'keyword',
    'delegate': 'keyword',
    'do!': 'keyword',
    'done': 'keyword',
    'downcast': 'keyword',
    'downto': 'keyword',
    'elif': 'keyword',
    'extern': 'keyword',
    'finally': 'keyword',
    'for': 'keyword',
    'function': 'keyword',
    'global': 'keyword',
    'inherit': 'keyword',
    'inline': 'keyword',
    'interface': 'keyword',
    'internal': 'keyword',
    'lazy': 'keyword',
    'let!': 'keyword',
    'match': 'keyword',
    'member': 'keyword',
    'module': 'keyword',
    'mutable': 'keyword',
    'namespace': 'keyword',
    'new': 'keyword',
    'null': 'keyword',
    'override': 'keyword',
    'private': 'keyword',
    'public': 'keyword',
    'return!': 'keyword',
    'return': 'keyword',
    'select': 'keyword',
    'static': 'keyword',
    'to': 'keyword',
    'try': 'keyword',
    'upcast': 'keyword',
    'use!': 'keyword',
    'use': 'keyword',
    'void': 'keyword',
    'when': 'keyword',
    'yield!': 'keyword',
    'yield': 'keyword',
    // Reserved words
    'atomic': 'keyword',
    'break': 'keyword',
    'checked': 'keyword',
    'component': 'keyword',
    'const': 'keyword',
    'constraint': 'keyword',
    'constructor': 'keyword',
    'continue': 'keyword',
    'eager': 'keyword',
    'event': 'keyword',
    'external': 'keyword',
    'fixed': 'keyword',
    'method': 'keyword',
    'mixin': 'keyword',
    'object': 'keyword',
    'parallel': 'keyword',
    'process': 'keyword',
    'protected': 'keyword',
    'pure': 'keyword',
    'sealed': 'keyword',
    'tailcall': 'keyword',
    'trait': 'keyword',
    'virtual': 'keyword',
    'volatile': 'keyword',
    // builtins
    'List': 'builtin',
    'Seq': 'builtin',
    'Map': 'builtin',
    'Set': 'builtin',
    'Option': 'builtin',
    'int': 'builtin',
    'string': 'builtin',
    'not': 'builtin',
    'true': 'builtin',
    'false': 'builtin',
    'raise': 'builtin',
    'failwith': 'builtin'
  },
  slashComments: true
});
const sml = mlLike({
  name: "sml",
  extraWords: {
    'abstype': 'keyword',
    'and': 'keyword',
    'andalso': 'keyword',
    'case': 'keyword',
    'datatype': 'keyword',
    'fn': 'keyword',
    'handle': 'keyword',
    'infix': 'keyword',
    'infixr': 'keyword',
    'local': 'keyword',
    'nonfix': 'keyword',
    'op': 'keyword',
    'orelse': 'keyword',
    'raise': 'keyword',
    'withtype': 'keyword',
    'eqtype': 'keyword',
    'sharing': 'keyword',
    'sig': 'keyword',
    'signature': 'keyword',
    'structure': 'keyword',
    'where': 'keyword',
    'true': 'keyword',
    'false': 'keyword',
    // types
    'int': 'builtin',
    'real': 'builtin',
    'string': 'builtin',
    'char': 'builtin',
    'bool': 'builtin'
  },
  slashComments: true
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzA1OC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9tbGxpa2UuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gbWxMaWtlKHBhcnNlckNvbmZpZykge1xuICB2YXIgd29yZHMgPSB7XG4gICAgJ2FzJzogJ2tleXdvcmQnLFxuICAgICdkbyc6ICdrZXl3b3JkJyxcbiAgICAnZWxzZSc6ICdrZXl3b3JkJyxcbiAgICAnZW5kJzogJ2tleXdvcmQnLFxuICAgICdleGNlcHRpb24nOiAna2V5d29yZCcsXG4gICAgJ2Z1bic6ICdrZXl3b3JkJyxcbiAgICAnZnVuY3Rvcic6ICdrZXl3b3JkJyxcbiAgICAnaWYnOiAna2V5d29yZCcsXG4gICAgJ2luJzogJ2tleXdvcmQnLFxuICAgICdpbmNsdWRlJzogJ2tleXdvcmQnLFxuICAgICdsZXQnOiAna2V5d29yZCcsXG4gICAgJ29mJzogJ2tleXdvcmQnLFxuICAgICdvcGVuJzogJ2tleXdvcmQnLFxuICAgICdyZWMnOiAna2V5d29yZCcsXG4gICAgJ3N0cnVjdCc6ICdrZXl3b3JkJyxcbiAgICAndGhlbic6ICdrZXl3b3JkJyxcbiAgICAndHlwZSc6ICdrZXl3b3JkJyxcbiAgICAndmFsJzogJ2tleXdvcmQnLFxuICAgICd3aGlsZSc6ICdrZXl3b3JkJyxcbiAgICAnd2l0aCc6ICdrZXl3b3JkJ1xuICB9O1xuICB2YXIgZXh0cmFXb3JkcyA9IHBhcnNlckNvbmZpZy5leHRyYVdvcmRzIHx8IHt9O1xuICBmb3IgKHZhciBwcm9wIGluIGV4dHJhV29yZHMpIHtcbiAgICBpZiAoZXh0cmFXb3Jkcy5oYXNPd25Qcm9wZXJ0eShwcm9wKSkge1xuICAgICAgd29yZHNbcHJvcF0gPSBwYXJzZXJDb25maWcuZXh0cmFXb3Jkc1twcm9wXTtcbiAgICB9XG4gIH1cbiAgdmFyIGhpbnRXb3JkcyA9IFtdO1xuICBmb3IgKHZhciBrIGluIHdvcmRzKSB7XG4gICAgaGludFdvcmRzLnB1c2goayk7XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICAgIGlmIChjaCA9PT0gJ1wiJykge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZztcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgaWYgKGNoID09PSAneycpIHtcbiAgICAgIGlmIChzdHJlYW0uZWF0KCd8JykpIHtcbiAgICAgICAgc3RhdGUubG9uZ1N0cmluZyA9IHRydWU7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Mb25nU3RyaW5nO1xuICAgICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChjaCA9PT0gJygnKSB7XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eXFwqKD8hXFwpKS8pKSB7XG4gICAgICAgIHN0YXRlLmNvbW1lbnRMZXZlbCsrO1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQ29tbWVudDtcbiAgICAgICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgfVxuICAgIH1cbiAgICBpZiAoY2ggPT09ICd+JyB8fCBjaCA9PT0gJz8nKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgICAgcmV0dXJuICd2YXJpYWJsZU5hbWUuc3BlY2lhbCc7XG4gICAgfVxuICAgIGlmIChjaCA9PT0gJ2AnKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgICAgcmV0dXJuICdxdW90ZSc7XG4gICAgfVxuICAgIGlmIChjaCA9PT0gJy8nICYmIHBhcnNlckNvbmZpZy5zbGFzaENvbW1lbnRzICYmIHN0cmVhbS5lYXQoJy8nKSkge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuICdjb21tZW50JztcbiAgICB9XG4gICAgaWYgKC9cXGQvLnRlc3QoY2gpKSB7XG4gICAgICBpZiAoY2ggPT09ICcwJyAmJiBzdHJlYW0uZWF0KC9bYkJdLykpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bMDFdLyk7XG4gICAgICB9XG4gICAgICBpZiAoY2ggPT09ICcwJyAmJiBzdHJlYW0uZWF0KC9beFhdLykpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bMC05YS1mQS1GXS8pO1xuICAgICAgfVxuICAgICAgaWYgKGNoID09PSAnMCcgJiYgc3RyZWFtLmVhdCgvW29PXS8pKSB7XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvWzAtN10vKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcZF9dLyk7XG4gICAgICAgIGlmIChzdHJlYW0uZWF0KCcuJykpIHtcbiAgICAgICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXGRdLyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHN0cmVhbS5lYXQoL1tlRV0vKSkge1xuICAgICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcZFxcLStdLyk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHJldHVybiAnbnVtYmVyJztcbiAgICB9XG4gICAgaWYgKC9bK1xcLSomJT08PiE/fEBcXC5+Ol0vLnRlc3QoY2gpKSB7XG4gICAgICByZXR1cm4gJ29wZXJhdG9yJztcbiAgICB9XG4gICAgaWYgKC9bXFx3XFx4YTEtXFx1ZmZmZl0vLnRlc3QoY2gpKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXHhhMS1cXHVmZmZmXS8pO1xuICAgICAgdmFyIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgICByZXR1cm4gd29yZHMuaGFzT3duUHJvcGVydHkoY3VyKSA/IHdvcmRzW2N1cl0gOiAndmFyaWFibGUnO1xuICAgIH1cbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBmdW5jdGlvbiB0b2tlblN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIG5leHQsXG4gICAgICBlbmQgPSBmYWxzZSxcbiAgICAgIGVzY2FwZWQgPSBmYWxzZTtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PT0gJ1wiJyAmJiAhZXNjYXBlZCkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09PSAnXFxcXCc7XG4gICAgfVxuICAgIGlmIChlbmQgJiYgIWVzY2FwZWQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIH1cbiAgICByZXR1cm4gJ3N0cmluZyc7XG4gIH1cbiAgO1xuICBmdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBwcmV2LCBuZXh0O1xuICAgIHdoaWxlIChzdGF0ZS5jb21tZW50TGV2ZWwgPiAwICYmIChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKHByZXYgPT09ICcoJyAmJiBuZXh0ID09PSAnKicpIHN0YXRlLmNvbW1lbnRMZXZlbCsrO1xuICAgICAgaWYgKHByZXYgPT09ICcqJyAmJiBuZXh0ID09PSAnKScpIHN0YXRlLmNvbW1lbnRMZXZlbC0tO1xuICAgICAgcHJldiA9IG5leHQ7XG4gICAgfVxuICAgIGlmIChzdGF0ZS5jb21tZW50TGV2ZWwgPD0gMCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgfVxuICAgIHJldHVybiAnY29tbWVudCc7XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5Mb25nU3RyaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgcHJldiwgbmV4dDtcbiAgICB3aGlsZSAoc3RhdGUubG9uZ1N0cmluZyAmJiAobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmIChwcmV2ID09PSAnfCcgJiYgbmV4dCA9PT0gJ30nKSBzdGF0ZS5sb25nU3RyaW5nID0gZmFsc2U7XG4gICAgICBwcmV2ID0gbmV4dDtcbiAgICB9XG4gICAgaWYgKCFzdGF0ZS5sb25nU3RyaW5nKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICB9XG4gICAgcmV0dXJuICdzdHJpbmcnO1xuICB9XG4gIHJldHVybiB7XG4gICAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdG9rZW5pemU6IHRva2VuQmFzZSxcbiAgICAgICAgY29tbWVudExldmVsOiAwLFxuICAgICAgICBsb25nU3RyaW5nOiBmYWxzZVxuICAgICAgfTtcbiAgICB9LFxuICAgIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9LFxuICAgIGxhbmd1YWdlRGF0YToge1xuICAgICAgYXV0b2NvbXBsZXRlOiBoaW50V29yZHMsXG4gICAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICAgIGxpbmU6IHBhcnNlckNvbmZpZy5zbGFzaENvbW1lbnRzID8gXCIvL1wiIDogdW5kZWZpbmVkLFxuICAgICAgICBibG9jazoge1xuICAgICAgICAgIG9wZW46IFwiKCpcIixcbiAgICAgICAgICBjbG9zZTogXCIqKVwiXG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gIH07XG59XG47XG5leHBvcnQgY29uc3Qgb0NhbWwgPSBtbExpa2Uoe1xuICBuYW1lOiBcIm9jYW1sXCIsXG4gIGV4dHJhV29yZHM6IHtcbiAgICAnYW5kJzogJ2tleXdvcmQnLFxuICAgICdhc3NlcnQnOiAna2V5d29yZCcsXG4gICAgJ2JlZ2luJzogJ2tleXdvcmQnLFxuICAgICdjbGFzcyc6ICdrZXl3b3JkJyxcbiAgICAnY29uc3RyYWludCc6ICdrZXl3b3JkJyxcbiAgICAnZG9uZSc6ICdrZXl3b3JkJyxcbiAgICAnZG93bnRvJzogJ2tleXdvcmQnLFxuICAgICdleHRlcm5hbCc6ICdrZXl3b3JkJyxcbiAgICAnZnVuY3Rpb24nOiAna2V5d29yZCcsXG4gICAgJ2luaXRpYWxpemVyJzogJ2tleXdvcmQnLFxuICAgICdsYXp5JzogJ2tleXdvcmQnLFxuICAgICdtYXRjaCc6ICdrZXl3b3JkJyxcbiAgICAnbWV0aG9kJzogJ2tleXdvcmQnLFxuICAgICdtb2R1bGUnOiAna2V5d29yZCcsXG4gICAgJ211dGFibGUnOiAna2V5d29yZCcsXG4gICAgJ25ldyc6ICdrZXl3b3JkJyxcbiAgICAnbm9ucmVjJzogJ2tleXdvcmQnLFxuICAgICdvYmplY3QnOiAna2V5d29yZCcsXG4gICAgJ3ByaXZhdGUnOiAna2V5d29yZCcsXG4gICAgJ3NpZyc6ICdrZXl3b3JkJyxcbiAgICAndG8nOiAna2V5d29yZCcsXG4gICAgJ3RyeSc6ICdrZXl3b3JkJyxcbiAgICAndmFsdWUnOiAna2V5d29yZCcsXG4gICAgJ3ZpcnR1YWwnOiAna2V5d29yZCcsXG4gICAgJ3doZW4nOiAna2V5d29yZCcsXG4gICAgLy8gYnVpbHRpbnNcbiAgICAncmFpc2UnOiAnYnVpbHRpbicsXG4gICAgJ2ZhaWx3aXRoJzogJ2J1aWx0aW4nLFxuICAgICd0cnVlJzogJ2J1aWx0aW4nLFxuICAgICdmYWxzZSc6ICdidWlsdGluJyxcbiAgICAvLyBQZXJ2YXNpdmVzIGJ1aWx0aW5zXG4gICAgJ2Fzcic6ICdidWlsdGluJyxcbiAgICAnbGFuZCc6ICdidWlsdGluJyxcbiAgICAnbG9yJzogJ2J1aWx0aW4nLFxuICAgICdsc2wnOiAnYnVpbHRpbicsXG4gICAgJ2xzcic6ICdidWlsdGluJyxcbiAgICAnbHhvcic6ICdidWlsdGluJyxcbiAgICAnbW9kJzogJ2J1aWx0aW4nLFxuICAgICdvcic6ICdidWlsdGluJyxcbiAgICAvLyBNb3JlIFBlcnZhc2l2ZXNcbiAgICAncmFpc2Vfbm90cmFjZSc6ICdidWlsdGluJyxcbiAgICAndHJhY2UnOiAnYnVpbHRpbicsXG4gICAgJ2V4aXQnOiAnYnVpbHRpbicsXG4gICAgJ3ByaW50X3N0cmluZyc6ICdidWlsdGluJyxcbiAgICAncHJpbnRfZW5kbGluZSc6ICdidWlsdGluJyxcbiAgICAnaW50JzogJ3R5cGUnLFxuICAgICdmbG9hdCc6ICd0eXBlJyxcbiAgICAnYm9vbCc6ICd0eXBlJyxcbiAgICAnY2hhcic6ICd0eXBlJyxcbiAgICAnc3RyaW5nJzogJ3R5cGUnLFxuICAgICd1bml0JzogJ3R5cGUnLFxuICAgIC8vIE1vZHVsZXNcbiAgICAnTGlzdCc6ICdidWlsdGluJ1xuICB9XG59KTtcbmV4cG9ydCBjb25zdCBmU2hhcnAgPSBtbExpa2Uoe1xuICBuYW1lOiBcImZzaGFycFwiLFxuICBleHRyYVdvcmRzOiB7XG4gICAgJ2Fic3RyYWN0JzogJ2tleXdvcmQnLFxuICAgICdhc3NlcnQnOiAna2V5d29yZCcsXG4gICAgJ2Jhc2UnOiAna2V5d29yZCcsXG4gICAgJ2JlZ2luJzogJ2tleXdvcmQnLFxuICAgICdjbGFzcyc6ICdrZXl3b3JkJyxcbiAgICAnZGVmYXVsdCc6ICdrZXl3b3JkJyxcbiAgICAnZGVsZWdhdGUnOiAna2V5d29yZCcsXG4gICAgJ2RvISc6ICdrZXl3b3JkJyxcbiAgICAnZG9uZSc6ICdrZXl3b3JkJyxcbiAgICAnZG93bmNhc3QnOiAna2V5d29yZCcsXG4gICAgJ2Rvd250byc6ICdrZXl3b3JkJyxcbiAgICAnZWxpZic6ICdrZXl3b3JkJyxcbiAgICAnZXh0ZXJuJzogJ2tleXdvcmQnLFxuICAgICdmaW5hbGx5JzogJ2tleXdvcmQnLFxuICAgICdmb3InOiAna2V5d29yZCcsXG4gICAgJ2Z1bmN0aW9uJzogJ2tleXdvcmQnLFxuICAgICdnbG9iYWwnOiAna2V5d29yZCcsXG4gICAgJ2luaGVyaXQnOiAna2V5d29yZCcsXG4gICAgJ2lubGluZSc6ICdrZXl3b3JkJyxcbiAgICAnaW50ZXJmYWNlJzogJ2tleXdvcmQnLFxuICAgICdpbnRlcm5hbCc6ICdrZXl3b3JkJyxcbiAgICAnbGF6eSc6ICdrZXl3b3JkJyxcbiAgICAnbGV0ISc6ICdrZXl3b3JkJyxcbiAgICAnbWF0Y2gnOiAna2V5d29yZCcsXG4gICAgJ21lbWJlcic6ICdrZXl3b3JkJyxcbiAgICAnbW9kdWxlJzogJ2tleXdvcmQnLFxuICAgICdtdXRhYmxlJzogJ2tleXdvcmQnLFxuICAgICduYW1lc3BhY2UnOiAna2V5d29yZCcsXG4gICAgJ25ldyc6ICdrZXl3b3JkJyxcbiAgICAnbnVsbCc6ICdrZXl3b3JkJyxcbiAgICAnb3ZlcnJpZGUnOiAna2V5d29yZCcsXG4gICAgJ3ByaXZhdGUnOiAna2V5d29yZCcsXG4gICAgJ3B1YmxpYyc6ICdrZXl3b3JkJyxcbiAgICAncmV0dXJuISc6ICdrZXl3b3JkJyxcbiAgICAncmV0dXJuJzogJ2tleXdvcmQnLFxuICAgICdzZWxlY3QnOiAna2V5d29yZCcsXG4gICAgJ3N0YXRpYyc6ICdrZXl3b3JkJyxcbiAgICAndG8nOiAna2V5d29yZCcsXG4gICAgJ3RyeSc6ICdrZXl3b3JkJyxcbiAgICAndXBjYXN0JzogJ2tleXdvcmQnLFxuICAgICd1c2UhJzogJ2tleXdvcmQnLFxuICAgICd1c2UnOiAna2V5d29yZCcsXG4gICAgJ3ZvaWQnOiAna2V5d29yZCcsXG4gICAgJ3doZW4nOiAna2V5d29yZCcsXG4gICAgJ3lpZWxkISc6ICdrZXl3b3JkJyxcbiAgICAneWllbGQnOiAna2V5d29yZCcsXG4gICAgLy8gUmVzZXJ2ZWQgd29yZHNcbiAgICAnYXRvbWljJzogJ2tleXdvcmQnLFxuICAgICdicmVhayc6ICdrZXl3b3JkJyxcbiAgICAnY2hlY2tlZCc6ICdrZXl3b3JkJyxcbiAgICAnY29tcG9uZW50JzogJ2tleXdvcmQnLFxuICAgICdjb25zdCc6ICdrZXl3b3JkJyxcbiAgICAnY29uc3RyYWludCc6ICdrZXl3b3JkJyxcbiAgICAnY29uc3RydWN0b3InOiAna2V5d29yZCcsXG4gICAgJ2NvbnRpbnVlJzogJ2tleXdvcmQnLFxuICAgICdlYWdlcic6ICdrZXl3b3JkJyxcbiAgICAnZXZlbnQnOiAna2V5d29yZCcsXG4gICAgJ2V4dGVybmFsJzogJ2tleXdvcmQnLFxuICAgICdmaXhlZCc6ICdrZXl3b3JkJyxcbiAgICAnbWV0aG9kJzogJ2tleXdvcmQnLFxuICAgICdtaXhpbic6ICdrZXl3b3JkJyxcbiAgICAnb2JqZWN0JzogJ2tleXdvcmQnLFxuICAgICdwYXJhbGxlbCc6ICdrZXl3b3JkJyxcbiAgICAncHJvY2Vzcyc6ICdrZXl3b3JkJyxcbiAgICAncHJvdGVjdGVkJzogJ2tleXdvcmQnLFxuICAgICdwdXJlJzogJ2tleXdvcmQnLFxuICAgICdzZWFsZWQnOiAna2V5d29yZCcsXG4gICAgJ3RhaWxjYWxsJzogJ2tleXdvcmQnLFxuICAgICd0cmFpdCc6ICdrZXl3b3JkJyxcbiAgICAndmlydHVhbCc6ICdrZXl3b3JkJyxcbiAgICAndm9sYXRpbGUnOiAna2V5d29yZCcsXG4gICAgLy8gYnVpbHRpbnNcbiAgICAnTGlzdCc6ICdidWlsdGluJyxcbiAgICAnU2VxJzogJ2J1aWx0aW4nLFxuICAgICdNYXAnOiAnYnVpbHRpbicsXG4gICAgJ1NldCc6ICdidWlsdGluJyxcbiAgICAnT3B0aW9uJzogJ2J1aWx0aW4nLFxuICAgICdpbnQnOiAnYnVpbHRpbicsXG4gICAgJ3N0cmluZyc6ICdidWlsdGluJyxcbiAgICAnbm90JzogJ2J1aWx0aW4nLFxuICAgICd0cnVlJzogJ2J1aWx0aW4nLFxuICAgICdmYWxzZSc6ICdidWlsdGluJyxcbiAgICAncmFpc2UnOiAnYnVpbHRpbicsXG4gICAgJ2ZhaWx3aXRoJzogJ2J1aWx0aW4nXG4gIH0sXG4gIHNsYXNoQ29tbWVudHM6IHRydWVcbn0pO1xuZXhwb3J0IGNvbnN0IHNtbCA9IG1sTGlrZSh7XG4gIG5hbWU6IFwic21sXCIsXG4gIGV4dHJhV29yZHM6IHtcbiAgICAnYWJzdHlwZSc6ICdrZXl3b3JkJyxcbiAgICAnYW5kJzogJ2tleXdvcmQnLFxuICAgICdhbmRhbHNvJzogJ2tleXdvcmQnLFxuICAgICdjYXNlJzogJ2tleXdvcmQnLFxuICAgICdkYXRhdHlwZSc6ICdrZXl3b3JkJyxcbiAgICAnZm4nOiAna2V5d29yZCcsXG4gICAgJ2hhbmRsZSc6ICdrZXl3b3JkJyxcbiAgICAnaW5maXgnOiAna2V5d29yZCcsXG4gICAgJ2luZml4cic6ICdrZXl3b3JkJyxcbiAgICAnbG9jYWwnOiAna2V5d29yZCcsXG4gICAgJ25vbmZpeCc6ICdrZXl3b3JkJyxcbiAgICAnb3AnOiAna2V5d29yZCcsXG4gICAgJ29yZWxzZSc6ICdrZXl3b3JkJyxcbiAgICAncmFpc2UnOiAna2V5d29yZCcsXG4gICAgJ3dpdGh0eXBlJzogJ2tleXdvcmQnLFxuICAgICdlcXR5cGUnOiAna2V5d29yZCcsXG4gICAgJ3NoYXJpbmcnOiAna2V5d29yZCcsXG4gICAgJ3NpZyc6ICdrZXl3b3JkJyxcbiAgICAnc2lnbmF0dXJlJzogJ2tleXdvcmQnLFxuICAgICdzdHJ1Y3R1cmUnOiAna2V5d29yZCcsXG4gICAgJ3doZXJlJzogJ2tleXdvcmQnLFxuICAgICd0cnVlJzogJ2tleXdvcmQnLFxuICAgICdmYWxzZSc6ICdrZXl3b3JkJyxcbiAgICAvLyB0eXBlc1xuICAgICdpbnQnOiAnYnVpbHRpbicsXG4gICAgJ3JlYWwnOiAnYnVpbHRpbicsXG4gICAgJ3N0cmluZyc6ICdidWlsdGluJyxcbiAgICAnY2hhcic6ICdidWlsdGluJyxcbiAgICAnYm9vbCc6ICdidWlsdGluJ1xuICB9LFxuICBzbGFzaENvbW1lbnRzOiB0cnVlXG59KTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9