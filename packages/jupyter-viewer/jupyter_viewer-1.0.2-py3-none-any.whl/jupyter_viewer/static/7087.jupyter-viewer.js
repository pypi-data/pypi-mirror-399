"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7087],{

/***/ 77087
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   vbScript: () => (/* binding */ vbScript)
/* harmony export */ });
/* unused harmony export vbScriptASP */
function mkVBScript(parserConf) {
  var ERRORCLASS = 'error';
  function wordRegexp(words) {
    return new RegExp("^((" + words.join(")|(") + "))\\b", "i");
  }
  var singleOperators = new RegExp("^[\\+\\-\\*/&\\\\\\^<>=]");
  var doubleOperators = new RegExp("^((<>)|(<=)|(>=))");
  var singleDelimiters = new RegExp('^[\\.,]');
  var brackets = new RegExp('^[\\(\\)]');
  var identifiers = new RegExp("^[A-Za-z][_A-Za-z0-9]*");
  var openingKeywords = ['class', 'sub', 'select', 'while', 'if', 'function', 'property', 'with', 'for'];
  var middleKeywords = ['else', 'elseif', 'case'];
  var endKeywords = ['next', 'loop', 'wend'];
  var wordOperators = wordRegexp(['and', 'or', 'not', 'xor', 'is', 'mod', 'eqv', 'imp']);
  var commonkeywords = ['dim', 'redim', 'then', 'until', 'randomize', 'byval', 'byref', 'new', 'property', 'exit', 'in', 'const', 'private', 'public', 'get', 'set', 'let', 'stop', 'on error resume next', 'on error goto 0', 'option explicit', 'call', 'me'];

  //This list was from: http://msdn.microsoft.com/en-us/library/f8tbc79x(v=vs.84).aspx
  var atomWords = ['true', 'false', 'nothing', 'empty', 'null'];
  //This list was from: http://msdn.microsoft.com/en-us/library/3ca8tfek(v=vs.84).aspx
  var builtinFuncsWords = ['abs', 'array', 'asc', 'atn', 'cbool', 'cbyte', 'ccur', 'cdate', 'cdbl', 'chr', 'cint', 'clng', 'cos', 'csng', 'cstr', 'date', 'dateadd', 'datediff', 'datepart', 'dateserial', 'datevalue', 'day', 'escape', 'eval', 'execute', 'exp', 'filter', 'formatcurrency', 'formatdatetime', 'formatnumber', 'formatpercent', 'getlocale', 'getobject', 'getref', 'hex', 'hour', 'inputbox', 'instr', 'instrrev', 'int', 'fix', 'isarray', 'isdate', 'isempty', 'isnull', 'isnumeric', 'isobject', 'join', 'lbound', 'lcase', 'left', 'len', 'loadpicture', 'log', 'ltrim', 'rtrim', 'trim', 'maths', 'mid', 'minute', 'month', 'monthname', 'msgbox', 'now', 'oct', 'replace', 'rgb', 'right', 'rnd', 'round', 'scriptengine', 'scriptenginebuildversion', 'scriptenginemajorversion', 'scriptengineminorversion', 'second', 'setlocale', 'sgn', 'sin', 'space', 'split', 'sqr', 'strcomp', 'string', 'strreverse', 'tan', 'time', 'timer', 'timeserial', 'timevalue', 'typename', 'ubound', 'ucase', 'unescape', 'vartype', 'weekday', 'weekdayname', 'year'];

  //This list was from: http://msdn.microsoft.com/en-us/library/ydz4cfk3(v=vs.84).aspx
  var builtinConsts = ['vbBlack', 'vbRed', 'vbGreen', 'vbYellow', 'vbBlue', 'vbMagenta', 'vbCyan', 'vbWhite', 'vbBinaryCompare', 'vbTextCompare', 'vbSunday', 'vbMonday', 'vbTuesday', 'vbWednesday', 'vbThursday', 'vbFriday', 'vbSaturday', 'vbUseSystemDayOfWeek', 'vbFirstJan1', 'vbFirstFourDays', 'vbFirstFullWeek', 'vbGeneralDate', 'vbLongDate', 'vbShortDate', 'vbLongTime', 'vbShortTime', 'vbObjectError', 'vbOKOnly', 'vbOKCancel', 'vbAbortRetryIgnore', 'vbYesNoCancel', 'vbYesNo', 'vbRetryCancel', 'vbCritical', 'vbQuestion', 'vbExclamation', 'vbInformation', 'vbDefaultButton1', 'vbDefaultButton2', 'vbDefaultButton3', 'vbDefaultButton4', 'vbApplicationModal', 'vbSystemModal', 'vbOK', 'vbCancel', 'vbAbort', 'vbRetry', 'vbIgnore', 'vbYes', 'vbNo', 'vbCr', 'VbCrLf', 'vbFormFeed', 'vbLf', 'vbNewLine', 'vbNullChar', 'vbNullString', 'vbTab', 'vbVerticalTab', 'vbUseDefault', 'vbTrue', 'vbFalse', 'vbEmpty', 'vbNull', 'vbInteger', 'vbLong', 'vbSingle', 'vbDouble', 'vbCurrency', 'vbDate', 'vbString', 'vbObject', 'vbError', 'vbBoolean', 'vbVariant', 'vbDataObject', 'vbDecimal', 'vbByte', 'vbArray'];
  //This list was from: http://msdn.microsoft.com/en-us/library/hkc375ea(v=vs.84).aspx
  var builtinObjsWords = ['WScript', 'err', 'debug', 'RegExp'];
  var knownProperties = ['description', 'firstindex', 'global', 'helpcontext', 'helpfile', 'ignorecase', 'length', 'number', 'pattern', 'source', 'value', 'count'];
  var knownMethods = ['clear', 'execute', 'raise', 'replace', 'test', 'write', 'writeline', 'close', 'open', 'state', 'eof', 'update', 'addnew', 'end', 'createobject', 'quit'];
  var aspBuiltinObjsWords = ['server', 'response', 'request', 'session', 'application'];
  var aspKnownProperties = ['buffer', 'cachecontrol', 'charset', 'contenttype', 'expires', 'expiresabsolute', 'isclientconnected', 'pics', 'status',
  //response
  'clientcertificate', 'cookies', 'form', 'querystring', 'servervariables', 'totalbytes',
  //request
  'contents', 'staticobjects',
  //application
  'codepage', 'lcid', 'sessionid', 'timeout',
  //session
  'scripttimeout']; //server
  var aspKnownMethods = ['addheader', 'appendtolog', 'binarywrite', 'end', 'flush', 'redirect',
  //response
  'binaryread',
  //request
  'remove', 'removeall', 'lock', 'unlock',
  //application
  'abandon',
  //session
  'getlasterror', 'htmlencode', 'mappath', 'transfer', 'urlencode']; //server

  var knownWords = knownMethods.concat(knownProperties);
  builtinObjsWords = builtinObjsWords.concat(builtinConsts);
  if (parserConf.isASP) {
    builtinObjsWords = builtinObjsWords.concat(aspBuiltinObjsWords);
    knownWords = knownWords.concat(aspKnownMethods, aspKnownProperties);
  }
  ;
  var keywords = wordRegexp(commonkeywords);
  var atoms = wordRegexp(atomWords);
  var builtinFuncs = wordRegexp(builtinFuncsWords);
  var builtinObjs = wordRegexp(builtinObjsWords);
  var known = wordRegexp(knownWords);
  var stringPrefixes = '"';
  var opening = wordRegexp(openingKeywords);
  var middle = wordRegexp(middleKeywords);
  var closing = wordRegexp(endKeywords);
  var doubleClosing = wordRegexp(['end']);
  var doOpening = wordRegexp(['do']);
  var noIndentWords = wordRegexp(['on error resume next', 'exit']);
  var comment = wordRegexp(['rem']);
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
      //return null;
    }
    var ch = stream.peek();

    // Handle Comments
    if (ch === "'") {
      stream.skipToEnd();
      return 'comment';
    }
    if (stream.match(comment)) {
      stream.skipToEnd();
      return 'comment';
    }

    // Handle Number Literals
    if (stream.match(/^((&H)|(&O))?[0-9\.]/i, false) && !stream.match(/^((&H)|(&O))?[0-9\.]+[a-z_]/i, false)) {
      var floatLiteral = false;
      // Floats
      if (stream.match(/^\d*\.\d+/i)) {
        floatLiteral = true;
      } else if (stream.match(/^\d+\.\d*/)) {
        floatLiteral = true;
      } else if (stream.match(/^\.\d+/)) {
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
    if (stream.match(doubleOperators) || stream.match(singleOperators) || stream.match(wordOperators)) {
      return 'operator';
    }
    if (stream.match(singleDelimiters)) {
      return null;
    }
    if (stream.match(brackets)) {
      return "bracket";
    }
    if (stream.match(noIndentWords)) {
      state.doInCurrentLine = true;
      return 'keyword';
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
      if (!state.doInCurrentLine) dedent(stream, state);else state.doInCurrentLine = false;
      return 'keyword';
    }
    if (stream.match(keywords)) {
      return 'keyword';
    }
    if (stream.match(atoms)) {
      return 'atom';
    }
    if (stream.match(known)) {
      return 'variableName.special';
    }
    if (stream.match(builtinFuncs)) {
      return 'builtin';
    }
    if (stream.match(builtinObjs)) {
      return 'builtin';
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
      current = stream.current();
      if (style && (style.substr(0, 8) === 'variable' || style === 'builtin' || style === 'keyword')) {
        //|| knownWords.indexOf(current.substring(1)) > -1) {
        if (style === 'builtin' || style === 'keyword') style = 'variable';
        if (knownWords.indexOf(current.substr(1)) > -1) style = 'keyword';
        return style;
      } else {
        return ERRORCLASS;
      }
    }
    return style;
  }
  return {
    name: "vbscript",
    startState: function () {
      return {
        tokenize: tokenBase,
        lastToken: null,
        currentIndent: 0,
        nextLineIndent: 0,
        doInCurrentLine: false,
        ignoreKeyword: false
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
      if (style === null) style = null;
      return style;
    },
    indent: function (state, textAfter, cx) {
      var trueText = textAfter.replace(/^\s+|\s+$/g, '');
      if (trueText.match(closing) || trueText.match(doubleClosing) || trueText.match(middle)) return cx.unit * (state.currentIndent - 1);
      if (state.currentIndent < 0) return 0;
      return state.currentIndent * cx.unit;
    }
  };
}
;
const vbScript = mkVBScript({});
const vbScriptASP = mkVBScript({
  isASP: true
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzA4Ny5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS92YnNjcmlwdC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBta1ZCU2NyaXB0KHBhcnNlckNvbmYpIHtcbiAgdmFyIEVSUk9SQ0xBU1MgPSAnZXJyb3InO1xuICBmdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gICAgcmV0dXJuIG5ldyBSZWdFeHAoXCJeKChcIiArIHdvcmRzLmpvaW4oXCIpfChcIikgKyBcIikpXFxcXGJcIiwgXCJpXCIpO1xuICB9XG4gIHZhciBzaW5nbGVPcGVyYXRvcnMgPSBuZXcgUmVnRXhwKFwiXltcXFxcK1xcXFwtXFxcXCovJlxcXFxcXFxcXFxcXF48Pj1dXCIpO1xuICB2YXIgZG91YmxlT3BlcmF0b3JzID0gbmV3IFJlZ0V4cChcIl4oKDw+KXwoPD0pfCg+PSkpXCIpO1xuICB2YXIgc2luZ2xlRGVsaW1pdGVycyA9IG5ldyBSZWdFeHAoJ15bXFxcXC4sXScpO1xuICB2YXIgYnJhY2tldHMgPSBuZXcgUmVnRXhwKCdeW1xcXFwoXFxcXCldJyk7XG4gIHZhciBpZGVudGlmaWVycyA9IG5ldyBSZWdFeHAoXCJeW0EtWmEtel1bX0EtWmEtejAtOV0qXCIpO1xuICB2YXIgb3BlbmluZ0tleXdvcmRzID0gWydjbGFzcycsICdzdWInLCAnc2VsZWN0JywgJ3doaWxlJywgJ2lmJywgJ2Z1bmN0aW9uJywgJ3Byb3BlcnR5JywgJ3dpdGgnLCAnZm9yJ107XG4gIHZhciBtaWRkbGVLZXl3b3JkcyA9IFsnZWxzZScsICdlbHNlaWYnLCAnY2FzZSddO1xuICB2YXIgZW5kS2V5d29yZHMgPSBbJ25leHQnLCAnbG9vcCcsICd3ZW5kJ107XG4gIHZhciB3b3JkT3BlcmF0b3JzID0gd29yZFJlZ2V4cChbJ2FuZCcsICdvcicsICdub3QnLCAneG9yJywgJ2lzJywgJ21vZCcsICdlcXYnLCAnaW1wJ10pO1xuICB2YXIgY29tbW9ua2V5d29yZHMgPSBbJ2RpbScsICdyZWRpbScsICd0aGVuJywgJ3VudGlsJywgJ3JhbmRvbWl6ZScsICdieXZhbCcsICdieXJlZicsICduZXcnLCAncHJvcGVydHknLCAnZXhpdCcsICdpbicsICdjb25zdCcsICdwcml2YXRlJywgJ3B1YmxpYycsICdnZXQnLCAnc2V0JywgJ2xldCcsICdzdG9wJywgJ29uIGVycm9yIHJlc3VtZSBuZXh0JywgJ29uIGVycm9yIGdvdG8gMCcsICdvcHRpb24gZXhwbGljaXQnLCAnY2FsbCcsICdtZSddO1xuXG4gIC8vVGhpcyBsaXN0IHdhcyBmcm9tOiBodHRwOi8vbXNkbi5taWNyb3NvZnQuY29tL2VuLXVzL2xpYnJhcnkvZjh0YmM3OXgodj12cy44NCkuYXNweFxuICB2YXIgYXRvbVdvcmRzID0gWyd0cnVlJywgJ2ZhbHNlJywgJ25vdGhpbmcnLCAnZW1wdHknLCAnbnVsbCddO1xuICAvL1RoaXMgbGlzdCB3YXMgZnJvbTogaHR0cDovL21zZG4ubWljcm9zb2Z0LmNvbS9lbi11cy9saWJyYXJ5LzNjYTh0ZmVrKHY9dnMuODQpLmFzcHhcbiAgdmFyIGJ1aWx0aW5GdW5jc1dvcmRzID0gWydhYnMnLCAnYXJyYXknLCAnYXNjJywgJ2F0bicsICdjYm9vbCcsICdjYnl0ZScsICdjY3VyJywgJ2NkYXRlJywgJ2NkYmwnLCAnY2hyJywgJ2NpbnQnLCAnY2xuZycsICdjb3MnLCAnY3NuZycsICdjc3RyJywgJ2RhdGUnLCAnZGF0ZWFkZCcsICdkYXRlZGlmZicsICdkYXRlcGFydCcsICdkYXRlc2VyaWFsJywgJ2RhdGV2YWx1ZScsICdkYXknLCAnZXNjYXBlJywgJ2V2YWwnLCAnZXhlY3V0ZScsICdleHAnLCAnZmlsdGVyJywgJ2Zvcm1hdGN1cnJlbmN5JywgJ2Zvcm1hdGRhdGV0aW1lJywgJ2Zvcm1hdG51bWJlcicsICdmb3JtYXRwZXJjZW50JywgJ2dldGxvY2FsZScsICdnZXRvYmplY3QnLCAnZ2V0cmVmJywgJ2hleCcsICdob3VyJywgJ2lucHV0Ym94JywgJ2luc3RyJywgJ2luc3RycmV2JywgJ2ludCcsICdmaXgnLCAnaXNhcnJheScsICdpc2RhdGUnLCAnaXNlbXB0eScsICdpc251bGwnLCAnaXNudW1lcmljJywgJ2lzb2JqZWN0JywgJ2pvaW4nLCAnbGJvdW5kJywgJ2xjYXNlJywgJ2xlZnQnLCAnbGVuJywgJ2xvYWRwaWN0dXJlJywgJ2xvZycsICdsdHJpbScsICdydHJpbScsICd0cmltJywgJ21hdGhzJywgJ21pZCcsICdtaW51dGUnLCAnbW9udGgnLCAnbW9udGhuYW1lJywgJ21zZ2JveCcsICdub3cnLCAnb2N0JywgJ3JlcGxhY2UnLCAncmdiJywgJ3JpZ2h0JywgJ3JuZCcsICdyb3VuZCcsICdzY3JpcHRlbmdpbmUnLCAnc2NyaXB0ZW5naW5lYnVpbGR2ZXJzaW9uJywgJ3NjcmlwdGVuZ2luZW1ham9ydmVyc2lvbicsICdzY3JpcHRlbmdpbmVtaW5vcnZlcnNpb24nLCAnc2Vjb25kJywgJ3NldGxvY2FsZScsICdzZ24nLCAnc2luJywgJ3NwYWNlJywgJ3NwbGl0JywgJ3NxcicsICdzdHJjb21wJywgJ3N0cmluZycsICdzdHJyZXZlcnNlJywgJ3RhbicsICd0aW1lJywgJ3RpbWVyJywgJ3RpbWVzZXJpYWwnLCAndGltZXZhbHVlJywgJ3R5cGVuYW1lJywgJ3Vib3VuZCcsICd1Y2FzZScsICd1bmVzY2FwZScsICd2YXJ0eXBlJywgJ3dlZWtkYXknLCAnd2Vla2RheW5hbWUnLCAneWVhciddO1xuXG4gIC8vVGhpcyBsaXN0IHdhcyBmcm9tOiBodHRwOi8vbXNkbi5taWNyb3NvZnQuY29tL2VuLXVzL2xpYnJhcnkveWR6NGNmazModj12cy44NCkuYXNweFxuICB2YXIgYnVpbHRpbkNvbnN0cyA9IFsndmJCbGFjaycsICd2YlJlZCcsICd2YkdyZWVuJywgJ3ZiWWVsbG93JywgJ3ZiQmx1ZScsICd2Yk1hZ2VudGEnLCAndmJDeWFuJywgJ3ZiV2hpdGUnLCAndmJCaW5hcnlDb21wYXJlJywgJ3ZiVGV4dENvbXBhcmUnLCAndmJTdW5kYXknLCAndmJNb25kYXknLCAndmJUdWVzZGF5JywgJ3ZiV2VkbmVzZGF5JywgJ3ZiVGh1cnNkYXknLCAndmJGcmlkYXknLCAndmJTYXR1cmRheScsICd2YlVzZVN5c3RlbURheU9mV2VlaycsICd2YkZpcnN0SmFuMScsICd2YkZpcnN0Rm91ckRheXMnLCAndmJGaXJzdEZ1bGxXZWVrJywgJ3ZiR2VuZXJhbERhdGUnLCAndmJMb25nRGF0ZScsICd2YlNob3J0RGF0ZScsICd2YkxvbmdUaW1lJywgJ3ZiU2hvcnRUaW1lJywgJ3ZiT2JqZWN0RXJyb3InLCAndmJPS09ubHknLCAndmJPS0NhbmNlbCcsICd2YkFib3J0UmV0cnlJZ25vcmUnLCAndmJZZXNOb0NhbmNlbCcsICd2Ylllc05vJywgJ3ZiUmV0cnlDYW5jZWwnLCAndmJDcml0aWNhbCcsICd2YlF1ZXN0aW9uJywgJ3ZiRXhjbGFtYXRpb24nLCAndmJJbmZvcm1hdGlvbicsICd2YkRlZmF1bHRCdXR0b24xJywgJ3ZiRGVmYXVsdEJ1dHRvbjInLCAndmJEZWZhdWx0QnV0dG9uMycsICd2YkRlZmF1bHRCdXR0b240JywgJ3ZiQXBwbGljYXRpb25Nb2RhbCcsICd2YlN5c3RlbU1vZGFsJywgJ3ZiT0snLCAndmJDYW5jZWwnLCAndmJBYm9ydCcsICd2YlJldHJ5JywgJ3ZiSWdub3JlJywgJ3ZiWWVzJywgJ3ZiTm8nLCAndmJDcicsICdWYkNyTGYnLCAndmJGb3JtRmVlZCcsICd2YkxmJywgJ3ZiTmV3TGluZScsICd2Yk51bGxDaGFyJywgJ3ZiTnVsbFN0cmluZycsICd2YlRhYicsICd2YlZlcnRpY2FsVGFiJywgJ3ZiVXNlRGVmYXVsdCcsICd2YlRydWUnLCAndmJGYWxzZScsICd2YkVtcHR5JywgJ3ZiTnVsbCcsICd2YkludGVnZXInLCAndmJMb25nJywgJ3ZiU2luZ2xlJywgJ3ZiRG91YmxlJywgJ3ZiQ3VycmVuY3knLCAndmJEYXRlJywgJ3ZiU3RyaW5nJywgJ3ZiT2JqZWN0JywgJ3ZiRXJyb3InLCAndmJCb29sZWFuJywgJ3ZiVmFyaWFudCcsICd2YkRhdGFPYmplY3QnLCAndmJEZWNpbWFsJywgJ3ZiQnl0ZScsICd2YkFycmF5J107XG4gIC8vVGhpcyBsaXN0IHdhcyBmcm9tOiBodHRwOi8vbXNkbi5taWNyb3NvZnQuY29tL2VuLXVzL2xpYnJhcnkvaGtjMzc1ZWEodj12cy44NCkuYXNweFxuICB2YXIgYnVpbHRpbk9ianNXb3JkcyA9IFsnV1NjcmlwdCcsICdlcnInLCAnZGVidWcnLCAnUmVnRXhwJ107XG4gIHZhciBrbm93blByb3BlcnRpZXMgPSBbJ2Rlc2NyaXB0aW9uJywgJ2ZpcnN0aW5kZXgnLCAnZ2xvYmFsJywgJ2hlbHBjb250ZXh0JywgJ2hlbHBmaWxlJywgJ2lnbm9yZWNhc2UnLCAnbGVuZ3RoJywgJ251bWJlcicsICdwYXR0ZXJuJywgJ3NvdXJjZScsICd2YWx1ZScsICdjb3VudCddO1xuICB2YXIga25vd25NZXRob2RzID0gWydjbGVhcicsICdleGVjdXRlJywgJ3JhaXNlJywgJ3JlcGxhY2UnLCAndGVzdCcsICd3cml0ZScsICd3cml0ZWxpbmUnLCAnY2xvc2UnLCAnb3BlbicsICdzdGF0ZScsICdlb2YnLCAndXBkYXRlJywgJ2FkZG5ldycsICdlbmQnLCAnY3JlYXRlb2JqZWN0JywgJ3F1aXQnXTtcbiAgdmFyIGFzcEJ1aWx0aW5PYmpzV29yZHMgPSBbJ3NlcnZlcicsICdyZXNwb25zZScsICdyZXF1ZXN0JywgJ3Nlc3Npb24nLCAnYXBwbGljYXRpb24nXTtcbiAgdmFyIGFzcEtub3duUHJvcGVydGllcyA9IFsnYnVmZmVyJywgJ2NhY2hlY29udHJvbCcsICdjaGFyc2V0JywgJ2NvbnRlbnR0eXBlJywgJ2V4cGlyZXMnLCAnZXhwaXJlc2Fic29sdXRlJywgJ2lzY2xpZW50Y29ubmVjdGVkJywgJ3BpY3MnLCAnc3RhdHVzJyxcbiAgLy9yZXNwb25zZVxuICAnY2xpZW50Y2VydGlmaWNhdGUnLCAnY29va2llcycsICdmb3JtJywgJ3F1ZXJ5c3RyaW5nJywgJ3NlcnZlcnZhcmlhYmxlcycsICd0b3RhbGJ5dGVzJyxcbiAgLy9yZXF1ZXN0XG4gICdjb250ZW50cycsICdzdGF0aWNvYmplY3RzJyxcbiAgLy9hcHBsaWNhdGlvblxuICAnY29kZXBhZ2UnLCAnbGNpZCcsICdzZXNzaW9uaWQnLCAndGltZW91dCcsXG4gIC8vc2Vzc2lvblxuICAnc2NyaXB0dGltZW91dCddOyAvL3NlcnZlclxuICB2YXIgYXNwS25vd25NZXRob2RzID0gWydhZGRoZWFkZXInLCAnYXBwZW5kdG9sb2cnLCAnYmluYXJ5d3JpdGUnLCAnZW5kJywgJ2ZsdXNoJywgJ3JlZGlyZWN0JyxcbiAgLy9yZXNwb25zZVxuICAnYmluYXJ5cmVhZCcsXG4gIC8vcmVxdWVzdFxuICAncmVtb3ZlJywgJ3JlbW92ZWFsbCcsICdsb2NrJywgJ3VubG9jaycsXG4gIC8vYXBwbGljYXRpb25cbiAgJ2FiYW5kb24nLFxuICAvL3Nlc3Npb25cbiAgJ2dldGxhc3RlcnJvcicsICdodG1sZW5jb2RlJywgJ21hcHBhdGgnLCAndHJhbnNmZXInLCAndXJsZW5jb2RlJ107IC8vc2VydmVyXG5cbiAgdmFyIGtub3duV29yZHMgPSBrbm93bk1ldGhvZHMuY29uY2F0KGtub3duUHJvcGVydGllcyk7XG4gIGJ1aWx0aW5PYmpzV29yZHMgPSBidWlsdGluT2Jqc1dvcmRzLmNvbmNhdChidWlsdGluQ29uc3RzKTtcbiAgaWYgKHBhcnNlckNvbmYuaXNBU1ApIHtcbiAgICBidWlsdGluT2Jqc1dvcmRzID0gYnVpbHRpbk9ianNXb3Jkcy5jb25jYXQoYXNwQnVpbHRpbk9ianNXb3Jkcyk7XG4gICAga25vd25Xb3JkcyA9IGtub3duV29yZHMuY29uY2F0KGFzcEtub3duTWV0aG9kcywgYXNwS25vd25Qcm9wZXJ0aWVzKTtcbiAgfVxuICA7XG4gIHZhciBrZXl3b3JkcyA9IHdvcmRSZWdleHAoY29tbW9ua2V5d29yZHMpO1xuICB2YXIgYXRvbXMgPSB3b3JkUmVnZXhwKGF0b21Xb3Jkcyk7XG4gIHZhciBidWlsdGluRnVuY3MgPSB3b3JkUmVnZXhwKGJ1aWx0aW5GdW5jc1dvcmRzKTtcbiAgdmFyIGJ1aWx0aW5PYmpzID0gd29yZFJlZ2V4cChidWlsdGluT2Jqc1dvcmRzKTtcbiAgdmFyIGtub3duID0gd29yZFJlZ2V4cChrbm93bldvcmRzKTtcbiAgdmFyIHN0cmluZ1ByZWZpeGVzID0gJ1wiJztcbiAgdmFyIG9wZW5pbmcgPSB3b3JkUmVnZXhwKG9wZW5pbmdLZXl3b3Jkcyk7XG4gIHZhciBtaWRkbGUgPSB3b3JkUmVnZXhwKG1pZGRsZUtleXdvcmRzKTtcbiAgdmFyIGNsb3NpbmcgPSB3b3JkUmVnZXhwKGVuZEtleXdvcmRzKTtcbiAgdmFyIGRvdWJsZUNsb3NpbmcgPSB3b3JkUmVnZXhwKFsnZW5kJ10pO1xuICB2YXIgZG9PcGVuaW5nID0gd29yZFJlZ2V4cChbJ2RvJ10pO1xuICB2YXIgbm9JbmRlbnRXb3JkcyA9IHdvcmRSZWdleHAoWydvbiBlcnJvciByZXN1bWUgbmV4dCcsICdleGl0J10pO1xuICB2YXIgY29tbWVudCA9IHdvcmRSZWdleHAoWydyZW0nXSk7XG4gIGZ1bmN0aW9uIGluZGVudChfc3RyZWFtLCBzdGF0ZSkge1xuICAgIHN0YXRlLmN1cnJlbnRJbmRlbnQrKztcbiAgfVxuICBmdW5jdGlvbiBkZWRlbnQoX3N0cmVhbSwgc3RhdGUpIHtcbiAgICBzdGF0ZS5jdXJyZW50SW5kZW50LS07XG4gIH1cbiAgLy8gdG9rZW5pemVyc1xuICBmdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgICAvL3JldHVybiBudWxsO1xuICAgIH1cbiAgICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpO1xuXG4gICAgLy8gSGFuZGxlIENvbW1lbnRzXG4gICAgaWYgKGNoID09PSBcIidcIikge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuICdjb21tZW50JztcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChjb21tZW50KSkge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuICdjb21tZW50JztcbiAgICB9XG5cbiAgICAvLyBIYW5kbGUgTnVtYmVyIExpdGVyYWxzXG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXigoJkgpfCgmTykpP1swLTlcXC5dL2ksIGZhbHNlKSAmJiAhc3RyZWFtLm1hdGNoKC9eKCgmSCl8KCZPKSk/WzAtOVxcLl0rW2Etel9dL2ksIGZhbHNlKSkge1xuICAgICAgdmFyIGZsb2F0TGl0ZXJhbCA9IGZhbHNlO1xuICAgICAgLy8gRmxvYXRzXG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eXFxkKlxcLlxcZCsvaSkpIHtcbiAgICAgICAgZmxvYXRMaXRlcmFsID0gdHJ1ZTtcbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eXFxkK1xcLlxcZCovKSkge1xuICAgICAgICBmbG9hdExpdGVyYWwgPSB0cnVlO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL15cXC5cXGQrLykpIHtcbiAgICAgICAgZmxvYXRMaXRlcmFsID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIGlmIChmbG9hdExpdGVyYWwpIHtcbiAgICAgICAgLy8gRmxvYXQgbGl0ZXJhbHMgbWF5IGJlIFwiaW1hZ2luYXJ5XCJcbiAgICAgICAgc3RyZWFtLmVhdCgvSi9pKTtcbiAgICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgICAgfVxuICAgICAgLy8gSW50ZWdlcnNcbiAgICAgIHZhciBpbnRMaXRlcmFsID0gZmFsc2U7XG4gICAgICAvLyBIZXhcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14mSFswLTlhLWZdKy9pKSkge1xuICAgICAgICBpbnRMaXRlcmFsID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIC8vIE9jdGFsXG4gICAgICBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL14mT1swLTddKy9pKSkge1xuICAgICAgICBpbnRMaXRlcmFsID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIC8vIERlY2ltYWxcbiAgICAgIGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXlsxLTldXFxkKkY/LykpIHtcbiAgICAgICAgLy8gRGVjaW1hbCBsaXRlcmFscyBtYXkgYmUgXCJpbWFnaW5hcnlcIlxuICAgICAgICBzdHJlYW0uZWF0KC9KL2kpO1xuICAgICAgICAvLyBUT0RPIC0gQ2FuIHlvdSBoYXZlIGltYWdpbmFyeSBsb25ncz9cbiAgICAgICAgaW50TGl0ZXJhbCA9IHRydWU7XG4gICAgICB9XG4gICAgICAvLyBaZXJvIGJ5IGl0c2VsZiB3aXRoIG5vIG90aGVyIHBpZWNlIG9mIG51bWJlci5cbiAgICAgIGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXjAoPyFbXFxkeF0pL2kpKSB7XG4gICAgICAgIGludExpdGVyYWwgPSB0cnVlO1xuICAgICAgfVxuICAgICAgaWYgKGludExpdGVyYWwpIHtcbiAgICAgICAgLy8gSW50ZWdlciBsaXRlcmFscyBtYXkgYmUgXCJsb25nXCJcbiAgICAgICAgc3RyZWFtLmVhdCgvTC9pKTtcbiAgICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgICAgfVxuICAgIH1cblxuICAgIC8vIEhhbmRsZSBTdHJpbmdzXG4gICAgaWYgKHN0cmVhbS5tYXRjaChzdHJpbmdQcmVmaXhlcykpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmdGYWN0b3J5KHN0cmVhbS5jdXJyZW50KCkpO1xuICAgICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIH1cblxuICAgIC8vIEhhbmRsZSBvcGVyYXRvcnMgYW5kIERlbGltaXRlcnNcbiAgICBpZiAoc3RyZWFtLm1hdGNoKGRvdWJsZU9wZXJhdG9ycykgfHwgc3RyZWFtLm1hdGNoKHNpbmdsZU9wZXJhdG9ycykgfHwgc3RyZWFtLm1hdGNoKHdvcmRPcGVyYXRvcnMpKSB7XG4gICAgICByZXR1cm4gJ29wZXJhdG9yJztcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChzaW5nbGVEZWxpbWl0ZXJzKSkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goYnJhY2tldHMpKSB7XG4gICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2gobm9JbmRlbnRXb3JkcykpIHtcbiAgICAgIHN0YXRlLmRvSW5DdXJyZW50TGluZSA9IHRydWU7XG4gICAgICByZXR1cm4gJ2tleXdvcmQnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKGRvT3BlbmluZykpIHtcbiAgICAgIGluZGVudChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIHN0YXRlLmRvSW5DdXJyZW50TGluZSA9IHRydWU7XG4gICAgICByZXR1cm4gJ2tleXdvcmQnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKG9wZW5pbmcpKSB7XG4gICAgICBpZiAoIXN0YXRlLmRvSW5DdXJyZW50TGluZSkgaW5kZW50KHN0cmVhbSwgc3RhdGUpO2Vsc2Ugc3RhdGUuZG9JbkN1cnJlbnRMaW5lID0gZmFsc2U7XG4gICAgICByZXR1cm4gJ2tleXdvcmQnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKG1pZGRsZSkpIHtcbiAgICAgIHJldHVybiAna2V5d29yZCc7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goZG91YmxlQ2xvc2luZykpIHtcbiAgICAgIGRlZGVudChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIGRlZGVudChzdHJlYW0sIHN0YXRlKTtcbiAgICAgIHJldHVybiAna2V5d29yZCc7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goY2xvc2luZykpIHtcbiAgICAgIGlmICghc3RhdGUuZG9JbkN1cnJlbnRMaW5lKSBkZWRlbnQoc3RyZWFtLCBzdGF0ZSk7ZWxzZSBzdGF0ZS5kb0luQ3VycmVudExpbmUgPSBmYWxzZTtcbiAgICAgIHJldHVybiAna2V5d29yZCc7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goa2V5d29yZHMpKSB7XG4gICAgICByZXR1cm4gJ2tleXdvcmQnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKGF0b21zKSkge1xuICAgICAgcmV0dXJuICdhdG9tJztcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChrbm93bikpIHtcbiAgICAgIHJldHVybiAndmFyaWFibGVOYW1lLnNwZWNpYWwnO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKGJ1aWx0aW5GdW5jcykpIHtcbiAgICAgIHJldHVybiAnYnVpbHRpbic7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goYnVpbHRpbk9ianMpKSB7XG4gICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKGlkZW50aWZpZXJzKSkge1xuICAgICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gICAgfVxuXG4gICAgLy8gSGFuZGxlIG5vbi1kZXRlY3RlZCBpdGVtc1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgcmV0dXJuIEVSUk9SQ0xBU1M7XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5TdHJpbmdGYWN0b3J5KGRlbGltaXRlcikge1xuICAgIHZhciBzaW5nbGVsaW5lID0gZGVsaW1pdGVyLmxlbmd0aCA9PSAxO1xuICAgIHZhciBPVVRDTEFTUyA9ICdzdHJpbmcnO1xuICAgIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgd2hpbGUgKCFzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXidcIl0vKTtcbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaChkZWxpbWl0ZXIpKSB7XG4gICAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICAgICAgcmV0dXJuIE9VVENMQVNTO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHN0cmVhbS5lYXQoL1snXCJdLyk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIGlmIChzaW5nbGVsaW5lKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgfVxuICAgICAgcmV0dXJuIE9VVENMQVNTO1xuICAgIH07XG4gIH1cbiAgZnVuY3Rpb24gdG9rZW5MZXhlcihzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgdmFyIGN1cnJlbnQgPSBzdHJlYW0uY3VycmVudCgpO1xuXG4gICAgLy8gSGFuZGxlICcuJyBjb25uZWN0ZWQgaWRlbnRpZmllcnNcbiAgICBpZiAoY3VycmVudCA9PT0gJy4nKSB7XG4gICAgICBzdHlsZSA9IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgY3VycmVudCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgICBpZiAoc3R5bGUgJiYgKHN0eWxlLnN1YnN0cigwLCA4KSA9PT0gJ3ZhcmlhYmxlJyB8fCBzdHlsZSA9PT0gJ2J1aWx0aW4nIHx8IHN0eWxlID09PSAna2V5d29yZCcpKSB7XG4gICAgICAgIC8vfHwga25vd25Xb3Jkcy5pbmRleE9mKGN1cnJlbnQuc3Vic3RyaW5nKDEpKSA+IC0xKSB7XG4gICAgICAgIGlmIChzdHlsZSA9PT0gJ2J1aWx0aW4nIHx8IHN0eWxlID09PSAna2V5d29yZCcpIHN0eWxlID0gJ3ZhcmlhYmxlJztcbiAgICAgICAgaWYgKGtub3duV29yZHMuaW5kZXhPZihjdXJyZW50LnN1YnN0cigxKSkgPiAtMSkgc3R5bGUgPSAna2V5d29yZCc7XG4gICAgICAgIHJldHVybiBzdHlsZTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHJldHVybiBFUlJPUkNMQVNTO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH1cbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBcInZic2NyaXB0XCIsXG4gICAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdG9rZW5pemU6IHRva2VuQmFzZSxcbiAgICAgICAgbGFzdFRva2VuOiBudWxsLFxuICAgICAgICBjdXJyZW50SW5kZW50OiAwLFxuICAgICAgICBuZXh0TGluZUluZGVudDogMCxcbiAgICAgICAgZG9JbkN1cnJlbnRMaW5lOiBmYWxzZSxcbiAgICAgICAgaWdub3JlS2V5d29yZDogZmFsc2VcbiAgICAgIH07XG4gICAgfSxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgICAgc3RhdGUuY3VycmVudEluZGVudCArPSBzdGF0ZS5uZXh0TGluZUluZGVudDtcbiAgICAgICAgc3RhdGUubmV4dExpbmVJbmRlbnQgPSAwO1xuICAgICAgICBzdGF0ZS5kb0luQ3VycmVudExpbmUgPSAwO1xuICAgICAgfVxuICAgICAgdmFyIHN0eWxlID0gdG9rZW5MZXhlcihzdHJlYW0sIHN0YXRlKTtcbiAgICAgIHN0YXRlLmxhc3RUb2tlbiA9IHtcbiAgICAgICAgc3R5bGU6IHN0eWxlLFxuICAgICAgICBjb250ZW50OiBzdHJlYW0uY3VycmVudCgpXG4gICAgICB9O1xuICAgICAgaWYgKHN0eWxlID09PSBudWxsKSBzdHlsZSA9IG51bGw7XG4gICAgICByZXR1cm4gc3R5bGU7XG4gICAgfSxcbiAgICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgICAgdmFyIHRydWVUZXh0ID0gdGV4dEFmdGVyLnJlcGxhY2UoL15cXHMrfFxccyskL2csICcnKTtcbiAgICAgIGlmICh0cnVlVGV4dC5tYXRjaChjbG9zaW5nKSB8fCB0cnVlVGV4dC5tYXRjaChkb3VibGVDbG9zaW5nKSB8fCB0cnVlVGV4dC5tYXRjaChtaWRkbGUpKSByZXR1cm4gY3gudW5pdCAqIChzdGF0ZS5jdXJyZW50SW5kZW50IC0gMSk7XG4gICAgICBpZiAoc3RhdGUuY3VycmVudEluZGVudCA8IDApIHJldHVybiAwO1xuICAgICAgcmV0dXJuIHN0YXRlLmN1cnJlbnRJbmRlbnQgKiBjeC51bml0O1xuICAgIH1cbiAgfTtcbn1cbjtcbmV4cG9ydCBjb25zdCB2YlNjcmlwdCA9IG1rVkJTY3JpcHQoe30pO1xuZXhwb3J0IGNvbnN0IHZiU2NyaXB0QVNQID0gbWtWQlNjcmlwdCh7XG4gIGlzQVNQOiB0cnVlXG59KTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9