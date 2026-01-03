"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6812],{

/***/ 26812
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   vb: () => (/* binding */ vb)
/* harmony export */ });
var ERRORCLASS = 'error';
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b", "i");
}
var singleOperators = new RegExp("^[\\+\\-\\*/%&\\\\|\\^~<>!]");
var singleDelimiters = new RegExp('^[\\(\\)\\[\\]\\{\\}@,:`=;\\.]');
var doubleOperators = new RegExp("^((==)|(<>)|(<=)|(>=)|(<>)|(<<)|(>>)|(//)|(\\*\\*))");
var doubleDelimiters = new RegExp("^((\\+=)|(\\-=)|(\\*=)|(%=)|(/=)|(&=)|(\\|=)|(\\^=))");
var tripleDelimiters = new RegExp("^((//=)|(>>=)|(<<=)|(\\*\\*=))");
var identifiers = new RegExp("^[_A-Za-z][_A-Za-z0-9]*");
var openingKeywords = ['class', 'module', 'sub', 'enum', 'select', 'while', 'if', 'function', 'get', 'set', 'property', 'try', 'structure', 'synclock', 'using', 'with'];
var middleKeywords = ['else', 'elseif', 'case', 'catch', 'finally'];
var endKeywords = ['next', 'loop'];
var operatorKeywords = ['and', "andalso", 'or', 'orelse', 'xor', 'in', 'not', 'is', 'isnot', 'like'];
var wordOperators = wordRegexp(operatorKeywords);
var commonKeywords = ["#const", "#else", "#elseif", "#end", "#if", "#region", "addhandler", "addressof", "alias", "as", "byref", "byval", "cbool", "cbyte", "cchar", "cdate", "cdbl", "cdec", "cint", "clng", "cobj", "compare", "const", "continue", "csbyte", "cshort", "csng", "cstr", "cuint", "culng", "cushort", "declare", "default", "delegate", "dim", "directcast", "each", "erase", "error", "event", "exit", "explicit", "false", "for", "friend", "gettype", "goto", "handles", "implements", "imports", "infer", "inherits", "interface", "isfalse", "istrue", "lib", "me", "mod", "mustinherit", "mustoverride", "my", "mybase", "myclass", "namespace", "narrowing", "new", "nothing", "notinheritable", "notoverridable", "of", "off", "on", "operator", "option", "optional", "out", "overloads", "overridable", "overrides", "paramarray", "partial", "private", "protected", "public", "raiseevent", "readonly", "redim", "removehandler", "resume", "return", "shadows", "shared", "static", "step", "stop", "strict", "then", "throw", "to", "true", "trycast", "typeof", "until", "until", "when", "widening", "withevents", "writeonly"];
var commontypes = ['object', 'boolean', 'char', 'string', 'byte', 'sbyte', 'short', 'ushort', 'int16', 'uint16', 'integer', 'uinteger', 'int32', 'uint32', 'long', 'ulong', 'int64', 'uint64', 'decimal', 'single', 'double', 'float', 'date', 'datetime', 'intptr', 'uintptr'];
var keywords = wordRegexp(commonKeywords);
var types = wordRegexp(commontypes);
var stringPrefixes = '"';
var opening = wordRegexp(openingKeywords);
var middle = wordRegexp(middleKeywords);
var closing = wordRegexp(endKeywords);
var doubleClosing = wordRegexp(['end']);
var doOpening = wordRegexp(['do']);
var indentInfo = null;
function indent(_stream, state) {
  state.currentIndent++;
}
function dedent(_stream, state) {
  state.currentIndent--;
}
// tokenizers
function tokenBase(stream, state) {
  if (stream.eatSpace()) {
    return null;
  }
  var ch = stream.peek();

  // Handle Comments
  if (ch === "'") {
    stream.skipToEnd();
    return 'comment';
  }

  // Handle Number Literals
  if (stream.match(/^((&H)|(&O))?[0-9\.a-f]/i, false)) {
    var floatLiteral = false;
    // Floats
    if (stream.match(/^\d*\.\d+F?/i)) {
      floatLiteral = true;
    } else if (stream.match(/^\d+\.\d*F?/)) {
      floatLiteral = true;
    } else if (stream.match(/^\.\d+F?/)) {
      floatLiteral = true;
    }
    if (floatLiteral) {
      // Float literals may be "imaginary"
      stream.eat(/J/i);
      return 'number';
    }
    // Integers
    var intLiteral = false;
    // Hex
    if (stream.match(/^&H[0-9a-f]+/i)) {
      intLiteral = true;
    }
    // Octal
    else if (stream.match(/^&O[0-7]+/i)) {
      intLiteral = true;
    }
    // Decimal
    else if (stream.match(/^[1-9]\d*F?/)) {
      // Decimal literals may be "imaginary"
      stream.eat(/J/i);
      // TODO - Can you have imaginary longs?
      intLiteral = true;
    }
    // Zero by itself with no other piece of number.
    else if (stream.match(/^0(?![\dx])/i)) {
      intLiteral = true;
    }
    if (intLiteral) {
      // Integer literals may be "long"
      stream.eat(/L/i);
      return 'number';
    }
  }

  // Handle Strings
  if (stream.match(stringPrefixes)) {
    state.tokenize = tokenStringFactory(stream.current());
    return state.tokenize(stream, state);
  }

  // Handle operators and Delimiters
  if (stream.match(tripleDelimiters) || stream.match(doubleDelimiters)) {
    return null;
  }
  if (stream.match(doubleOperators) || stream.match(singleOperators) || stream.match(wordOperators)) {
    return 'operator';
  }
  if (stream.match(singleDelimiters)) {
    return null;
  }
  if (stream.match(doOpening)) {
    indent(stream, state);
    state.doInCurrentLine = true;
    return 'keyword';
  }
  if (stream.match(opening)) {
    if (!state.doInCurrentLine) indent(stream, state);else state.doInCurrentLine = false;
    return 'keyword';
  }
  if (stream.match(middle)) {
    return 'keyword';
  }
  if (stream.match(doubleClosing)) {
    dedent(stream, state);
    dedent(stream, state);
    return 'keyword';
  }
  if (stream.match(closing)) {
    dedent(stream, state);
    return 'keyword';
  }
  if (stream.match(types)) {
    return 'keyword';
  }
  if (stream.match(keywords)) {
    return 'keyword';
  }
  if (stream.match(identifiers)) {
    return 'variable';
  }

  // Handle non-detected items
  stream.next();
  return ERRORCLASS;
}
function tokenStringFactory(delimiter) {
  var singleline = delimiter.length == 1;
  var OUTCLASS = 'string';
  return function (stream, state) {
    while (!stream.eol()) {
      stream.eatWhile(/[^'"]/);
      if (stream.match(delimiter)) {
        state.tokenize = tokenBase;
        return OUTCLASS;
      } else {
        stream.eat(/['"]/);
      }
    }
    if (singleline) {
      state.tokenize = tokenBase;
    }
    return OUTCLASS;
  };
}
function tokenLexer(stream, state) {
  var style = state.tokenize(stream, state);
  var current = stream.current();

  // Handle '.' connected identifiers
  if (current === '.') {
    style = state.tokenize(stream, state);
    if (style === 'variable') {
      return 'variable';
    } else {
      return ERRORCLASS;
    }
  }
  var delimiter_index = '[({'.indexOf(current);
  if (delimiter_index !== -1) {
    indent(stream, state);
  }
  if (indentInfo === 'dedent') {
    if (dedent(stream, state)) {
      return ERRORCLASS;
    }
  }
  delimiter_index = '])}'.indexOf(current);
  if (delimiter_index !== -1) {
    if (dedent(stream, state)) {
      return ERRORCLASS;
    }
  }
  return style;
}
const vb = {
  name: "vb",
  startState: function () {
    return {
      tokenize: tokenBase,
      lastToken: null,
      currentIndent: 0,
      nextLineIndent: 0,
      doInCurrentLine: false
    };
  },
  token: function (stream, state) {
    if (stream.sol()) {
      state.currentIndent += state.nextLineIndent;
      state.nextLineIndent = 0;
      state.doInCurrentLine = 0;
    }
    var style = tokenLexer(stream, state);
    state.lastToken = {
      style: style,
      content: stream.current()
    };
    return style;
  },
  indent: function (state, textAfter, cx) {
    var trueText = textAfter.replace(/^\s+|\s+$/g, '');
    if (trueText.match(closing) || trueText.match(doubleClosing) || trueText.match(middle)) return cx.unit * (state.currentIndent - 1);
    if (state.currentIndent < 0) return 0;
    return state.currentIndent * cx.unit;
  },
  languageData: {
    closeBrackets: {
      brackets: ["(", "[", "{", '"']
    },
    commentTokens: {
      line: "'"
    },
    autocomplete: openingKeywords.concat(middleKeywords).concat(endKeywords).concat(operatorKeywords).concat(commonKeywords).concat(commontypes)
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjgxMi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdmIuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIEVSUk9SQ0xBU1MgPSAnZXJyb3InO1xuZnVuY3Rpb24gd29yZFJlZ2V4cCh3b3Jkcykge1xuICByZXR1cm4gbmV3IFJlZ0V4cChcIl4oKFwiICsgd29yZHMuam9pbihcIil8KFwiKSArIFwiKSlcXFxcYlwiLCBcImlcIik7XG59XG52YXIgc2luZ2xlT3BlcmF0b3JzID0gbmV3IFJlZ0V4cChcIl5bXFxcXCtcXFxcLVxcXFwqLyUmXFxcXFxcXFx8XFxcXF5+PD4hXVwiKTtcbnZhciBzaW5nbGVEZWxpbWl0ZXJzID0gbmV3IFJlZ0V4cCgnXltcXFxcKFxcXFwpXFxcXFtcXFxcXVxcXFx7XFxcXH1ALDpgPTtcXFxcLl0nKTtcbnZhciBkb3VibGVPcGVyYXRvcnMgPSBuZXcgUmVnRXhwKFwiXigoPT0pfCg8Pil8KDw9KXwoPj0pfCg8Pil8KDw8KXwoPj4pfCgvLyl8KFxcXFwqXFxcXCopKVwiKTtcbnZhciBkb3VibGVEZWxpbWl0ZXJzID0gbmV3IFJlZ0V4cChcIl4oKFxcXFwrPSl8KFxcXFwtPSl8KFxcXFwqPSl8KCU9KXwoLz0pfCgmPSl8KFxcXFx8PSl8KFxcXFxePSkpXCIpO1xudmFyIHRyaXBsZURlbGltaXRlcnMgPSBuZXcgUmVnRXhwKFwiXigoLy89KXwoPj49KXwoPDw9KXwoXFxcXCpcXFxcKj0pKVwiKTtcbnZhciBpZGVudGlmaWVycyA9IG5ldyBSZWdFeHAoXCJeW19BLVphLXpdW19BLVphLXowLTldKlwiKTtcbnZhciBvcGVuaW5nS2V5d29yZHMgPSBbJ2NsYXNzJywgJ21vZHVsZScsICdzdWInLCAnZW51bScsICdzZWxlY3QnLCAnd2hpbGUnLCAnaWYnLCAnZnVuY3Rpb24nLCAnZ2V0JywgJ3NldCcsICdwcm9wZXJ0eScsICd0cnknLCAnc3RydWN0dXJlJywgJ3N5bmNsb2NrJywgJ3VzaW5nJywgJ3dpdGgnXTtcbnZhciBtaWRkbGVLZXl3b3JkcyA9IFsnZWxzZScsICdlbHNlaWYnLCAnY2FzZScsICdjYXRjaCcsICdmaW5hbGx5J107XG52YXIgZW5kS2V5d29yZHMgPSBbJ25leHQnLCAnbG9vcCddO1xudmFyIG9wZXJhdG9yS2V5d29yZHMgPSBbJ2FuZCcsIFwiYW5kYWxzb1wiLCAnb3InLCAnb3JlbHNlJywgJ3hvcicsICdpbicsICdub3QnLCAnaXMnLCAnaXNub3QnLCAnbGlrZSddO1xudmFyIHdvcmRPcGVyYXRvcnMgPSB3b3JkUmVnZXhwKG9wZXJhdG9yS2V5d29yZHMpO1xudmFyIGNvbW1vbktleXdvcmRzID0gW1wiI2NvbnN0XCIsIFwiI2Vsc2VcIiwgXCIjZWxzZWlmXCIsIFwiI2VuZFwiLCBcIiNpZlwiLCBcIiNyZWdpb25cIiwgXCJhZGRoYW5kbGVyXCIsIFwiYWRkcmVzc29mXCIsIFwiYWxpYXNcIiwgXCJhc1wiLCBcImJ5cmVmXCIsIFwiYnl2YWxcIiwgXCJjYm9vbFwiLCBcImNieXRlXCIsIFwiY2NoYXJcIiwgXCJjZGF0ZVwiLCBcImNkYmxcIiwgXCJjZGVjXCIsIFwiY2ludFwiLCBcImNsbmdcIiwgXCJjb2JqXCIsIFwiY29tcGFyZVwiLCBcImNvbnN0XCIsIFwiY29udGludWVcIiwgXCJjc2J5dGVcIiwgXCJjc2hvcnRcIiwgXCJjc25nXCIsIFwiY3N0clwiLCBcImN1aW50XCIsIFwiY3VsbmdcIiwgXCJjdXNob3J0XCIsIFwiZGVjbGFyZVwiLCBcImRlZmF1bHRcIiwgXCJkZWxlZ2F0ZVwiLCBcImRpbVwiLCBcImRpcmVjdGNhc3RcIiwgXCJlYWNoXCIsIFwiZXJhc2VcIiwgXCJlcnJvclwiLCBcImV2ZW50XCIsIFwiZXhpdFwiLCBcImV4cGxpY2l0XCIsIFwiZmFsc2VcIiwgXCJmb3JcIiwgXCJmcmllbmRcIiwgXCJnZXR0eXBlXCIsIFwiZ290b1wiLCBcImhhbmRsZXNcIiwgXCJpbXBsZW1lbnRzXCIsIFwiaW1wb3J0c1wiLCBcImluZmVyXCIsIFwiaW5oZXJpdHNcIiwgXCJpbnRlcmZhY2VcIiwgXCJpc2ZhbHNlXCIsIFwiaXN0cnVlXCIsIFwibGliXCIsIFwibWVcIiwgXCJtb2RcIiwgXCJtdXN0aW5oZXJpdFwiLCBcIm11c3RvdmVycmlkZVwiLCBcIm15XCIsIFwibXliYXNlXCIsIFwibXljbGFzc1wiLCBcIm5hbWVzcGFjZVwiLCBcIm5hcnJvd2luZ1wiLCBcIm5ld1wiLCBcIm5vdGhpbmdcIiwgXCJub3Rpbmhlcml0YWJsZVwiLCBcIm5vdG92ZXJyaWRhYmxlXCIsIFwib2ZcIiwgXCJvZmZcIiwgXCJvblwiLCBcIm9wZXJhdG9yXCIsIFwib3B0aW9uXCIsIFwib3B0aW9uYWxcIiwgXCJvdXRcIiwgXCJvdmVybG9hZHNcIiwgXCJvdmVycmlkYWJsZVwiLCBcIm92ZXJyaWRlc1wiLCBcInBhcmFtYXJyYXlcIiwgXCJwYXJ0aWFsXCIsIFwicHJpdmF0ZVwiLCBcInByb3RlY3RlZFwiLCBcInB1YmxpY1wiLCBcInJhaXNlZXZlbnRcIiwgXCJyZWFkb25seVwiLCBcInJlZGltXCIsIFwicmVtb3ZlaGFuZGxlclwiLCBcInJlc3VtZVwiLCBcInJldHVyblwiLCBcInNoYWRvd3NcIiwgXCJzaGFyZWRcIiwgXCJzdGF0aWNcIiwgXCJzdGVwXCIsIFwic3RvcFwiLCBcInN0cmljdFwiLCBcInRoZW5cIiwgXCJ0aHJvd1wiLCBcInRvXCIsIFwidHJ1ZVwiLCBcInRyeWNhc3RcIiwgXCJ0eXBlb2ZcIiwgXCJ1bnRpbFwiLCBcInVudGlsXCIsIFwid2hlblwiLCBcIndpZGVuaW5nXCIsIFwid2l0aGV2ZW50c1wiLCBcIndyaXRlb25seVwiXTtcbnZhciBjb21tb250eXBlcyA9IFsnb2JqZWN0JywgJ2Jvb2xlYW4nLCAnY2hhcicsICdzdHJpbmcnLCAnYnl0ZScsICdzYnl0ZScsICdzaG9ydCcsICd1c2hvcnQnLCAnaW50MTYnLCAndWludDE2JywgJ2ludGVnZXInLCAndWludGVnZXInLCAnaW50MzInLCAndWludDMyJywgJ2xvbmcnLCAndWxvbmcnLCAnaW50NjQnLCAndWludDY0JywgJ2RlY2ltYWwnLCAnc2luZ2xlJywgJ2RvdWJsZScsICdmbG9hdCcsICdkYXRlJywgJ2RhdGV0aW1lJywgJ2ludHB0cicsICd1aW50cHRyJ107XG52YXIga2V5d29yZHMgPSB3b3JkUmVnZXhwKGNvbW1vbktleXdvcmRzKTtcbnZhciB0eXBlcyA9IHdvcmRSZWdleHAoY29tbW9udHlwZXMpO1xudmFyIHN0cmluZ1ByZWZpeGVzID0gJ1wiJztcbnZhciBvcGVuaW5nID0gd29yZFJlZ2V4cChvcGVuaW5nS2V5d29yZHMpO1xudmFyIG1pZGRsZSA9IHdvcmRSZWdleHAobWlkZGxlS2V5d29yZHMpO1xudmFyIGNsb3NpbmcgPSB3b3JkUmVnZXhwKGVuZEtleXdvcmRzKTtcbnZhciBkb3VibGVDbG9zaW5nID0gd29yZFJlZ2V4cChbJ2VuZCddKTtcbnZhciBkb09wZW5pbmcgPSB3b3JkUmVnZXhwKFsnZG8nXSk7XG52YXIgaW5kZW50SW5mbyA9IG51bGw7XG5mdW5jdGlvbiBpbmRlbnQoX3N0cmVhbSwgc3RhdGUpIHtcbiAgc3RhdGUuY3VycmVudEluZGVudCsrO1xufVxuZnVuY3Rpb24gZGVkZW50KF9zdHJlYW0sIHN0YXRlKSB7XG4gIHN0YXRlLmN1cnJlbnRJbmRlbnQtLTtcbn1cbi8vIHRva2VuaXplcnNcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIHZhciBjaCA9IHN0cmVhbS5wZWVrKCk7XG5cbiAgLy8gSGFuZGxlIENvbW1lbnRzXG4gIGlmIChjaCA9PT0gXCInXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuICdjb21tZW50JztcbiAgfVxuXG4gIC8vIEhhbmRsZSBOdW1iZXIgTGl0ZXJhbHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXigoJkgpfCgmTykpP1swLTlcXC5hLWZdL2ksIGZhbHNlKSkge1xuICAgIHZhciBmbG9hdExpdGVyYWwgPSBmYWxzZTtcbiAgICAvLyBGbG9hdHNcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eXFxkKlxcLlxcZCtGPy9pKSkge1xuICAgICAgZmxvYXRMaXRlcmFsID0gdHJ1ZTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXlxcZCtcXC5cXGQqRj8vKSkge1xuICAgICAgZmxvYXRMaXRlcmFsID0gdHJ1ZTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXlxcLlxcZCtGPy8pKSB7XG4gICAgICBmbG9hdExpdGVyYWwgPSB0cnVlO1xuICAgIH1cbiAgICBpZiAoZmxvYXRMaXRlcmFsKSB7XG4gICAgICAvLyBGbG9hdCBsaXRlcmFscyBtYXkgYmUgXCJpbWFnaW5hcnlcIlxuICAgICAgc3RyZWFtLmVhdCgvSi9pKTtcbiAgICAgIHJldHVybiAnbnVtYmVyJztcbiAgICB9XG4gICAgLy8gSW50ZWdlcnNcbiAgICB2YXIgaW50TGl0ZXJhbCA9IGZhbHNlO1xuICAgIC8vIEhleFxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14mSFswLTlhLWZdKy9pKSkge1xuICAgICAgaW50TGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIC8vIE9jdGFsXG4gICAgZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eJk9bMC03XSsvaSkpIHtcbiAgICAgIGludExpdGVyYWwgPSB0cnVlO1xuICAgIH1cbiAgICAvLyBEZWNpbWFsXG4gICAgZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eWzEtOV1cXGQqRj8vKSkge1xuICAgICAgLy8gRGVjaW1hbCBsaXRlcmFscyBtYXkgYmUgXCJpbWFnaW5hcnlcIlxuICAgICAgc3RyZWFtLmVhdCgvSi9pKTtcbiAgICAgIC8vIFRPRE8gLSBDYW4geW91IGhhdmUgaW1hZ2luYXJ5IGxvbmdzP1xuICAgICAgaW50TGl0ZXJhbCA9IHRydWU7XG4gICAgfVxuICAgIC8vIFplcm8gYnkgaXRzZWxmIHdpdGggbm8gb3RoZXIgcGllY2Ugb2YgbnVtYmVyLlxuICAgIGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXjAoPyFbXFxkeF0pL2kpKSB7XG4gICAgICBpbnRMaXRlcmFsID0gdHJ1ZTtcbiAgICB9XG4gICAgaWYgKGludExpdGVyYWwpIHtcbiAgICAgIC8vIEludGVnZXIgbGl0ZXJhbHMgbWF5IGJlIFwibG9uZ1wiXG4gICAgICBzdHJlYW0uZWF0KC9ML2kpO1xuICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgIH1cbiAgfVxuXG4gIC8vIEhhbmRsZSBTdHJpbmdzXG4gIGlmIChzdHJlYW0ubWF0Y2goc3RyaW5nUHJlZml4ZXMpKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZ0ZhY3Rvcnkoc3RyZWFtLmN1cnJlbnQoKSk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG5cbiAgLy8gSGFuZGxlIG9wZXJhdG9ycyBhbmQgRGVsaW1pdGVyc1xuICBpZiAoc3RyZWFtLm1hdGNoKHRyaXBsZURlbGltaXRlcnMpIHx8IHN0cmVhbS5tYXRjaChkb3VibGVEZWxpbWl0ZXJzKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goZG91YmxlT3BlcmF0b3JzKSB8fCBzdHJlYW0ubWF0Y2goc2luZ2xlT3BlcmF0b3JzKSB8fCBzdHJlYW0ubWF0Y2god29yZE9wZXJhdG9ycykpIHtcbiAgICByZXR1cm4gJ29wZXJhdG9yJztcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKHNpbmdsZURlbGltaXRlcnMpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChkb09wZW5pbmcpKSB7XG4gICAgaW5kZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgIHN0YXRlLmRvSW5DdXJyZW50TGluZSA9IHRydWU7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKG9wZW5pbmcpKSB7XG4gICAgaWYgKCFzdGF0ZS5kb0luQ3VycmVudExpbmUpIGluZGVudChzdHJlYW0sIHN0YXRlKTtlbHNlIHN0YXRlLmRvSW5DdXJyZW50TGluZSA9IGZhbHNlO1xuICAgIHJldHVybiAna2V5d29yZCc7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChtaWRkbGUpKSB7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGRvdWJsZUNsb3NpbmcpKSB7XG4gICAgZGVkZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgIGRlZGVudChzdHJlYW0sIHN0YXRlKTtcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goY2xvc2luZykpIHtcbiAgICBkZWRlbnQoc3RyZWFtLCBzdGF0ZSk7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKHR5cGVzKSkge1xuICAgIHJldHVybiAna2V5d29yZCc7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChrZXl3b3JkcykpIHtcbiAgICByZXR1cm4gJ2tleXdvcmQnO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goaWRlbnRpZmllcnMpKSB7XG4gICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gIH1cblxuICAvLyBIYW5kbGUgbm9uLWRldGVjdGVkIGl0ZW1zXG4gIHN0cmVhbS5uZXh0KCk7XG4gIHJldHVybiBFUlJPUkNMQVNTO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmdGYWN0b3J5KGRlbGltaXRlcikge1xuICB2YXIgc2luZ2xlbGluZSA9IGRlbGltaXRlci5sZW5ndGggPT0gMTtcbiAgdmFyIE9VVENMQVNTID0gJ3N0cmluZyc7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1teJ1wiXS8pO1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaChkZWxpbWl0ZXIpKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgICByZXR1cm4gT1VUQ0xBU1M7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBzdHJlYW0uZWF0KC9bJ1wiXS8pO1xuICAgICAgfVxuICAgIH1cbiAgICBpZiAoc2luZ2xlbGluZSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgfVxuICAgIHJldHVybiBPVVRDTEFTUztcbiAgfTtcbn1cbmZ1bmN0aW9uIHRva2VuTGV4ZXIoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgdmFyIGN1cnJlbnQgPSBzdHJlYW0uY3VycmVudCgpO1xuXG4gIC8vIEhhbmRsZSAnLicgY29ubmVjdGVkIGlkZW50aWZpZXJzXG4gIGlmIChjdXJyZW50ID09PSAnLicpIHtcbiAgICBzdHlsZSA9IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PT0gJ3ZhcmlhYmxlJykge1xuICAgICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gICAgfSBlbHNlIHtcbiAgICAgIHJldHVybiBFUlJPUkNMQVNTO1xuICAgIH1cbiAgfVxuICB2YXIgZGVsaW1pdGVyX2luZGV4ID0gJ1soeycuaW5kZXhPZihjdXJyZW50KTtcbiAgaWYgKGRlbGltaXRlcl9pbmRleCAhPT0gLTEpIHtcbiAgICBpbmRlbnQoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKGluZGVudEluZm8gPT09ICdkZWRlbnQnKSB7XG4gICAgaWYgKGRlZGVudChzdHJlYW0sIHN0YXRlKSkge1xuICAgICAgcmV0dXJuIEVSUk9SQ0xBU1M7XG4gICAgfVxuICB9XG4gIGRlbGltaXRlcl9pbmRleCA9ICddKX0nLmluZGV4T2YoY3VycmVudCk7XG4gIGlmIChkZWxpbWl0ZXJfaW5kZXggIT09IC0xKSB7XG4gICAgaWYgKGRlZGVudChzdHJlYW0sIHN0YXRlKSkge1xuICAgICAgcmV0dXJuIEVSUk9SQ0xBU1M7XG4gICAgfVxuICB9XG4gIHJldHVybiBzdHlsZTtcbn1cbmV4cG9ydCBjb25zdCB2YiA9IHtcbiAgbmFtZTogXCJ2YlwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBsYXN0VG9rZW46IG51bGwsXG4gICAgICBjdXJyZW50SW5kZW50OiAwLFxuICAgICAgbmV4dExpbmVJbmRlbnQ6IDAsXG4gICAgICBkb0luQ3VycmVudExpbmU6IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgc3RhdGUuY3VycmVudEluZGVudCArPSBzdGF0ZS5uZXh0TGluZUluZGVudDtcbiAgICAgIHN0YXRlLm5leHRMaW5lSW5kZW50ID0gMDtcbiAgICAgIHN0YXRlLmRvSW5DdXJyZW50TGluZSA9IDA7XG4gICAgfVxuICAgIHZhciBzdHlsZSA9IHRva2VuTGV4ZXIoc3RyZWFtLCBzdGF0ZSk7XG4gICAgc3RhdGUubGFzdFRva2VuID0ge1xuICAgICAgc3R5bGU6IHN0eWxlLFxuICAgICAgY29udGVudDogc3RyZWFtLmN1cnJlbnQoKVxuICAgIH07XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgIHZhciB0cnVlVGV4dCA9IHRleHRBZnRlci5yZXBsYWNlKC9eXFxzK3xcXHMrJC9nLCAnJyk7XG4gICAgaWYgKHRydWVUZXh0Lm1hdGNoKGNsb3NpbmcpIHx8IHRydWVUZXh0Lm1hdGNoKGRvdWJsZUNsb3NpbmcpIHx8IHRydWVUZXh0Lm1hdGNoKG1pZGRsZSkpIHJldHVybiBjeC51bml0ICogKHN0YXRlLmN1cnJlbnRJbmRlbnQgLSAxKTtcbiAgICBpZiAoc3RhdGUuY3VycmVudEluZGVudCA8IDApIHJldHVybiAwO1xuICAgIHJldHVybiBzdGF0ZS5jdXJyZW50SW5kZW50ICogY3gudW5pdDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY2xvc2VCcmFja2V0czoge1xuICAgICAgYnJhY2tldHM6IFtcIihcIiwgXCJbXCIsIFwie1wiLCAnXCInXVxuICAgIH0sXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCInXCJcbiAgICB9LFxuICAgIGF1dG9jb21wbGV0ZTogb3BlbmluZ0tleXdvcmRzLmNvbmNhdChtaWRkbGVLZXl3b3JkcykuY29uY2F0KGVuZEtleXdvcmRzKS5jb25jYXQob3BlcmF0b3JLZXl3b3JkcykuY29uY2F0KGNvbW1vbktleXdvcmRzKS5jb25jYXQoY29tbW9udHlwZXMpXG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==