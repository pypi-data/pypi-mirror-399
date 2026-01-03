"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1247],{

/***/ 71247
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   scheme: () => (/* binding */ scheme)
/* harmony export */ });
var BUILTIN = "builtin",
  COMMENT = "comment",
  STRING = "string",
  SYMBOL = "symbol",
  ATOM = "atom",
  NUMBER = "number",
  BRACKET = "bracket";
var INDENT_WORD_SKIP = 2;
function makeKeywords(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = makeKeywords("λ case-lambda call/cc class cond-expand define-class define-values exit-handler field import inherit init-field interface let*-values let-values let/ec mixin opt-lambda override protect provide public rename require require-for-syntax syntax syntax-case syntax-error unit/sig unless when with-syntax and begin call-with-current-continuation call-with-input-file call-with-output-file case cond define define-syntax define-macro defmacro delay do dynamic-wind else for-each if lambda let let* let-syntax letrec letrec-syntax map or syntax-rules abs acos angle append apply asin assoc assq assv atan boolean? caar cadr call-with-input-file call-with-output-file call-with-values car cdddar cddddr cdr ceiling char->integer char-alphabetic? char-ci<=? char-ci<? char-ci=? char-ci>=? char-ci>? char-downcase char-lower-case? char-numeric? char-ready? char-upcase char-upper-case? char-whitespace? char<=? char<? char=? char>=? char>? char? close-input-port close-output-port complex? cons cos current-input-port current-output-port denominator display eof-object? eq? equal? eqv? eval even? exact->inexact exact? exp expt #f floor force gcd imag-part inexact->exact inexact? input-port? integer->char integer? interaction-environment lcm length list list->string list->vector list-ref list-tail list? load log magnitude make-polar make-rectangular make-string make-vector max member memq memv min modulo negative? newline not null-environment null? number->string number? numerator odd? open-input-file open-output-file output-port? pair? peek-char port? positive? procedure? quasiquote quote quotient rational? rationalize read read-char real-part real? remainder reverse round scheme-report-environment set! set-car! set-cdr! sin sqrt string string->list string->number string->symbol string-append string-ci<=? string-ci<? string-ci=? string-ci>=? string-ci>? string-copy string-fill! string-length string-ref string-set! string<=? string<? string=? string>=? string>? string? substring symbol->string symbol? #t tan transcript-off transcript-on truncate values vector vector->list vector-fill! vector-length vector-ref vector-set! with-input-from-file with-output-to-file write write-char zero?");
var indentKeys = makeKeywords("define let letrec let* lambda define-macro defmacro let-syntax letrec-syntax let-values let*-values define-syntax syntax-rules define-values when unless");
function stateStack(indent, type, prev) {
  // represents a state stack object
  this.indent = indent;
  this.type = type;
  this.prev = prev;
}
function pushStack(state, indent, type) {
  state.indentStack = new stateStack(indent, type, state.indentStack);
}
function popStack(state) {
  state.indentStack = state.indentStack.prev;
}
var binaryMatcher = new RegExp(/^(?:[-+]i|[-+][01]+#*(?:\/[01]+#*)?i|[-+]?[01]+#*(?:\/[01]+#*)?@[-+]?[01]+#*(?:\/[01]+#*)?|[-+]?[01]+#*(?:\/[01]+#*)?[-+](?:[01]+#*(?:\/[01]+#*)?)?i|[-+]?[01]+#*(?:\/[01]+#*)?)(?=[()\s;"]|$)/i);
var octalMatcher = new RegExp(/^(?:[-+]i|[-+][0-7]+#*(?:\/[0-7]+#*)?i|[-+]?[0-7]+#*(?:\/[0-7]+#*)?@[-+]?[0-7]+#*(?:\/[0-7]+#*)?|[-+]?[0-7]+#*(?:\/[0-7]+#*)?[-+](?:[0-7]+#*(?:\/[0-7]+#*)?)?i|[-+]?[0-7]+#*(?:\/[0-7]+#*)?)(?=[()\s;"]|$)/i);
var hexMatcher = new RegExp(/^(?:[-+]i|[-+][\da-f]+#*(?:\/[\da-f]+#*)?i|[-+]?[\da-f]+#*(?:\/[\da-f]+#*)?@[-+]?[\da-f]+#*(?:\/[\da-f]+#*)?|[-+]?[\da-f]+#*(?:\/[\da-f]+#*)?[-+](?:[\da-f]+#*(?:\/[\da-f]+#*)?)?i|[-+]?[\da-f]+#*(?:\/[\da-f]+#*)?)(?=[()\s;"]|$)/i);
var decimalMatcher = new RegExp(/^(?:[-+]i|[-+](?:(?:(?:\d+#+\.?#*|\d+\.\d*#*|\.\d+#*|\d+)(?:[esfdl][-+]?\d+)?)|\d+#*\/\d+#*)i|[-+]?(?:(?:(?:\d+#+\.?#*|\d+\.\d*#*|\.\d+#*|\d+)(?:[esfdl][-+]?\d+)?)|\d+#*\/\d+#*)@[-+]?(?:(?:(?:\d+#+\.?#*|\d+\.\d*#*|\.\d+#*|\d+)(?:[esfdl][-+]?\d+)?)|\d+#*\/\d+#*)|[-+]?(?:(?:(?:\d+#+\.?#*|\d+\.\d*#*|\.\d+#*|\d+)(?:[esfdl][-+]?\d+)?)|\d+#*\/\d+#*)[-+](?:(?:(?:\d+#+\.?#*|\d+\.\d*#*|\.\d+#*|\d+)(?:[esfdl][-+]?\d+)?)|\d+#*\/\d+#*)?i|(?:(?:(?:\d+#+\.?#*|\d+\.\d*#*|\.\d+#*|\d+)(?:[esfdl][-+]?\d+)?)|\d+#*\/\d+#*))(?=[()\s;"]|$)/i);
function isBinaryNumber(stream) {
  return stream.match(binaryMatcher);
}
function isOctalNumber(stream) {
  return stream.match(octalMatcher);
}
function isDecimalNumber(stream, backup) {
  if (backup === true) {
    stream.backUp(1);
  }
  return stream.match(decimalMatcher);
}
function isHexNumber(stream) {
  return stream.match(hexMatcher);
}
function processEscapedSequence(stream, options) {
  var next,
    escaped = false;
  while ((next = stream.next()) != null) {
    if (next == options.token && !escaped) {
      options.state.mode = false;
      break;
    }
    escaped = !escaped && next == "\\";
  }
}
const scheme = {
  name: "scheme",
  startState: function () {
    return {
      indentStack: null,
      indentation: 0,
      mode: false,
      sExprComment: false,
      sExprQuote: false
    };
  },
  token: function (stream, state) {
    if (state.indentStack == null && stream.sol()) {
      // update indentation, but only if indentStack is empty
      state.indentation = stream.indentation();
    }

    // skip spaces
    if (stream.eatSpace()) {
      return null;
    }
    var returnType = null;
    switch (state.mode) {
      case "string":
        // multi-line string parsing mode
        processEscapedSequence(stream, {
          token: "\"",
          state: state
        });
        returnType = STRING; // continue on in scheme-string mode
        break;
      case "symbol":
        // escape symbol
        processEscapedSequence(stream, {
          token: "|",
          state: state
        });
        returnType = SYMBOL; // continue on in scheme-symbol mode
        break;
      case "comment":
        // comment parsing mode
        var next,
          maybeEnd = false;
        while ((next = stream.next()) != null) {
          if (next == "#" && maybeEnd) {
            state.mode = false;
            break;
          }
          maybeEnd = next == "|";
        }
        returnType = COMMENT;
        break;
      case "s-expr-comment":
        // s-expr commenting mode
        state.mode = false;
        if (stream.peek() == "(" || stream.peek() == "[") {
          // actually start scheme s-expr commenting mode
          state.sExprComment = 0;
        } else {
          // if not we just comment the entire of the next token
          stream.eatWhile(/[^\s\(\)\[\]]/); // eat symbol atom
          returnType = COMMENT;
          break;
        }
      default:
        // default parsing mode
        var ch = stream.next();
        if (ch == "\"") {
          state.mode = "string";
          returnType = STRING;
        } else if (ch == "'") {
          if (stream.peek() == "(" || stream.peek() == "[") {
            if (typeof state.sExprQuote != "number") {
              state.sExprQuote = 0;
            } // else already in a quoted expression
            returnType = ATOM;
          } else {
            stream.eatWhile(/[\w_\-!$%&*+\.\/:<=>?@\^~]/);
            returnType = ATOM;
          }
        } else if (ch == '|') {
          state.mode = "symbol";
          returnType = SYMBOL;
        } else if (ch == '#') {
          if (stream.eat("|")) {
            // Multi-line comment
            state.mode = "comment"; // toggle to comment mode
            returnType = COMMENT;
          } else if (stream.eat(/[tf]/i)) {
            // #t/#f (atom)
            returnType = ATOM;
          } else if (stream.eat(';')) {
            // S-Expr comment
            state.mode = "s-expr-comment";
            returnType = COMMENT;
          } else {
            var numTest = null,
              hasExactness = false,
              hasRadix = true;
            if (stream.eat(/[ei]/i)) {
              hasExactness = true;
            } else {
              stream.backUp(1); // must be radix specifier
            }
            if (stream.match(/^#b/i)) {
              numTest = isBinaryNumber;
            } else if (stream.match(/^#o/i)) {
              numTest = isOctalNumber;
            } else if (stream.match(/^#x/i)) {
              numTest = isHexNumber;
            } else if (stream.match(/^#d/i)) {
              numTest = isDecimalNumber;
            } else if (stream.match(/^[-+0-9.]/, false)) {
              hasRadix = false;
              numTest = isDecimalNumber;
              // re-consume the initial # if all matches failed
            } else if (!hasExactness) {
              stream.eat('#');
            }
            if (numTest != null) {
              if (hasRadix && !hasExactness) {
                // consume optional exactness after radix
                stream.match(/^#[ei]/i);
              }
              if (numTest(stream)) returnType = NUMBER;
            }
          }
        } else if (/^[-+0-9.]/.test(ch) && isDecimalNumber(stream, true)) {
          // match non-prefixed number, must be decimal
          returnType = NUMBER;
        } else if (ch == ";") {
          // comment
          stream.skipToEnd(); // rest of the line is a comment
          returnType = COMMENT;
        } else if (ch == "(" || ch == "[") {
          var keyWord = '';
          var indentTemp = stream.column(),
            letter;
          /**
             Either
             (indent-word ..
             (non-indent-word ..
             (;something else, bracket, etc.
          */

          while ((letter = stream.eat(/[^\s\(\[\;\)\]]/)) != null) {
            keyWord += letter;
          }
          if (keyWord.length > 0 && indentKeys.propertyIsEnumerable(keyWord)) {
            // indent-word

            pushStack(state, indentTemp + INDENT_WORD_SKIP, ch);
          } else {
            // non-indent word
            // we continue eating the spaces
            stream.eatSpace();
            if (stream.eol() || stream.peek() == ";") {
              // nothing significant after
              // we restart indentation 1 space after
              pushStack(state, indentTemp + 1, ch);
            } else {
              pushStack(state, indentTemp + stream.current().length, ch); // else we match
            }
          }
          stream.backUp(stream.current().length - 1); // undo all the eating

          if (typeof state.sExprComment == "number") state.sExprComment++;
          if (typeof state.sExprQuote == "number") state.sExprQuote++;
          returnType = BRACKET;
        } else if (ch == ")" || ch == "]") {
          returnType = BRACKET;
          if (state.indentStack != null && state.indentStack.type == (ch == ")" ? "(" : "[")) {
            popStack(state);
            if (typeof state.sExprComment == "number") {
              if (--state.sExprComment == 0) {
                returnType = COMMENT; // final closing bracket
                state.sExprComment = false; // turn off s-expr commenting mode
              }
            }
            if (typeof state.sExprQuote == "number") {
              if (--state.sExprQuote == 0) {
                returnType = ATOM; // final closing bracket
                state.sExprQuote = false; // turn off s-expr quote mode
              }
            }
          }
        } else {
          stream.eatWhile(/[\w_\-!$%&*+\.\/:<=>?@\^~]/);
          if (keywords && keywords.propertyIsEnumerable(stream.current())) {
            returnType = BUILTIN;
          } else returnType = "variable";
        }
    }
    return typeof state.sExprComment == "number" ? COMMENT : typeof state.sExprQuote == "number" ? ATOM : returnType;
  },
  indent: function (state) {
    if (state.indentStack == null) return state.indentation;
    return state.indentStack.indent;
  },
  languageData: {
    closeBrackets: {
      brackets: ["(", "[", "{", '"']
    },
    commentTokens: {
      line: ";;"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTI0Ny5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9zY2hlbWUuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIEJVSUxUSU4gPSBcImJ1aWx0aW5cIixcbiAgQ09NTUVOVCA9IFwiY29tbWVudFwiLFxuICBTVFJJTkcgPSBcInN0cmluZ1wiLFxuICBTWU1CT0wgPSBcInN5bWJvbFwiLFxuICBBVE9NID0gXCJhdG9tXCIsXG4gIE5VTUJFUiA9IFwibnVtYmVyXCIsXG4gIEJSQUNLRVQgPSBcImJyYWNrZXRcIjtcbnZhciBJTkRFTlRfV09SRF9TS0lQID0gMjtcbmZ1bmN0aW9uIG1ha2VLZXl3b3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiIFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBvYmo7XG59XG52YXIga2V5d29yZHMgPSBtYWtlS2V5d29yZHMoXCLOuyBjYXNlLWxhbWJkYSBjYWxsL2NjIGNsYXNzIGNvbmQtZXhwYW5kIGRlZmluZS1jbGFzcyBkZWZpbmUtdmFsdWVzIGV4aXQtaGFuZGxlciBmaWVsZCBpbXBvcnQgaW5oZXJpdCBpbml0LWZpZWxkIGludGVyZmFjZSBsZXQqLXZhbHVlcyBsZXQtdmFsdWVzIGxldC9lYyBtaXhpbiBvcHQtbGFtYmRhIG92ZXJyaWRlIHByb3RlY3QgcHJvdmlkZSBwdWJsaWMgcmVuYW1lIHJlcXVpcmUgcmVxdWlyZS1mb3Itc3ludGF4IHN5bnRheCBzeW50YXgtY2FzZSBzeW50YXgtZXJyb3IgdW5pdC9zaWcgdW5sZXNzIHdoZW4gd2l0aC1zeW50YXggYW5kIGJlZ2luIGNhbGwtd2l0aC1jdXJyZW50LWNvbnRpbnVhdGlvbiBjYWxsLXdpdGgtaW5wdXQtZmlsZSBjYWxsLXdpdGgtb3V0cHV0LWZpbGUgY2FzZSBjb25kIGRlZmluZSBkZWZpbmUtc3ludGF4IGRlZmluZS1tYWNybyBkZWZtYWNybyBkZWxheSBkbyBkeW5hbWljLXdpbmQgZWxzZSBmb3ItZWFjaCBpZiBsYW1iZGEgbGV0IGxldCogbGV0LXN5bnRheCBsZXRyZWMgbGV0cmVjLXN5bnRheCBtYXAgb3Igc3ludGF4LXJ1bGVzIGFicyBhY29zIGFuZ2xlIGFwcGVuZCBhcHBseSBhc2luIGFzc29jIGFzc3EgYXNzdiBhdGFuIGJvb2xlYW4/IGNhYXIgY2FkciBjYWxsLXdpdGgtaW5wdXQtZmlsZSBjYWxsLXdpdGgtb3V0cHV0LWZpbGUgY2FsbC13aXRoLXZhbHVlcyBjYXIgY2RkZGFyIGNkZGRkciBjZHIgY2VpbGluZyBjaGFyLT5pbnRlZ2VyIGNoYXItYWxwaGFiZXRpYz8gY2hhci1jaTw9PyBjaGFyLWNpPD8gY2hhci1jaT0/IGNoYXItY2k+PT8gY2hhci1jaT4/IGNoYXItZG93bmNhc2UgY2hhci1sb3dlci1jYXNlPyBjaGFyLW51bWVyaWM/IGNoYXItcmVhZHk/IGNoYXItdXBjYXNlIGNoYXItdXBwZXItY2FzZT8gY2hhci13aGl0ZXNwYWNlPyBjaGFyPD0/IGNoYXI8PyBjaGFyPT8gY2hhcj49PyBjaGFyPj8gY2hhcj8gY2xvc2UtaW5wdXQtcG9ydCBjbG9zZS1vdXRwdXQtcG9ydCBjb21wbGV4PyBjb25zIGNvcyBjdXJyZW50LWlucHV0LXBvcnQgY3VycmVudC1vdXRwdXQtcG9ydCBkZW5vbWluYXRvciBkaXNwbGF5IGVvZi1vYmplY3Q/IGVxPyBlcXVhbD8gZXF2PyBldmFsIGV2ZW4/IGV4YWN0LT5pbmV4YWN0IGV4YWN0PyBleHAgZXhwdCAjZiBmbG9vciBmb3JjZSBnY2QgaW1hZy1wYXJ0IGluZXhhY3QtPmV4YWN0IGluZXhhY3Q/IGlucHV0LXBvcnQ/IGludGVnZXItPmNoYXIgaW50ZWdlcj8gaW50ZXJhY3Rpb24tZW52aXJvbm1lbnQgbGNtIGxlbmd0aCBsaXN0IGxpc3QtPnN0cmluZyBsaXN0LT52ZWN0b3IgbGlzdC1yZWYgbGlzdC10YWlsIGxpc3Q/IGxvYWQgbG9nIG1hZ25pdHVkZSBtYWtlLXBvbGFyIG1ha2UtcmVjdGFuZ3VsYXIgbWFrZS1zdHJpbmcgbWFrZS12ZWN0b3IgbWF4IG1lbWJlciBtZW1xIG1lbXYgbWluIG1vZHVsbyBuZWdhdGl2ZT8gbmV3bGluZSBub3QgbnVsbC1lbnZpcm9ubWVudCBudWxsPyBudW1iZXItPnN0cmluZyBudW1iZXI/IG51bWVyYXRvciBvZGQ/IG9wZW4taW5wdXQtZmlsZSBvcGVuLW91dHB1dC1maWxlIG91dHB1dC1wb3J0PyBwYWlyPyBwZWVrLWNoYXIgcG9ydD8gcG9zaXRpdmU/IHByb2NlZHVyZT8gcXVhc2lxdW90ZSBxdW90ZSBxdW90aWVudCByYXRpb25hbD8gcmF0aW9uYWxpemUgcmVhZCByZWFkLWNoYXIgcmVhbC1wYXJ0IHJlYWw/IHJlbWFpbmRlciByZXZlcnNlIHJvdW5kIHNjaGVtZS1yZXBvcnQtZW52aXJvbm1lbnQgc2V0ISBzZXQtY2FyISBzZXQtY2RyISBzaW4gc3FydCBzdHJpbmcgc3RyaW5nLT5saXN0IHN0cmluZy0+bnVtYmVyIHN0cmluZy0+c3ltYm9sIHN0cmluZy1hcHBlbmQgc3RyaW5nLWNpPD0/IHN0cmluZy1jaTw/IHN0cmluZy1jaT0/IHN0cmluZy1jaT49PyBzdHJpbmctY2k+PyBzdHJpbmctY29weSBzdHJpbmctZmlsbCEgc3RyaW5nLWxlbmd0aCBzdHJpbmctcmVmIHN0cmluZy1zZXQhIHN0cmluZzw9PyBzdHJpbmc8PyBzdHJpbmc9PyBzdHJpbmc+PT8gc3RyaW5nPj8gc3RyaW5nPyBzdWJzdHJpbmcgc3ltYm9sLT5zdHJpbmcgc3ltYm9sPyAjdCB0YW4gdHJhbnNjcmlwdC1vZmYgdHJhbnNjcmlwdC1vbiB0cnVuY2F0ZSB2YWx1ZXMgdmVjdG9yIHZlY3Rvci0+bGlzdCB2ZWN0b3ItZmlsbCEgdmVjdG9yLWxlbmd0aCB2ZWN0b3ItcmVmIHZlY3Rvci1zZXQhIHdpdGgtaW5wdXQtZnJvbS1maWxlIHdpdGgtb3V0cHV0LXRvLWZpbGUgd3JpdGUgd3JpdGUtY2hhciB6ZXJvP1wiKTtcbnZhciBpbmRlbnRLZXlzID0gbWFrZUtleXdvcmRzKFwiZGVmaW5lIGxldCBsZXRyZWMgbGV0KiBsYW1iZGEgZGVmaW5lLW1hY3JvIGRlZm1hY3JvIGxldC1zeW50YXggbGV0cmVjLXN5bnRheCBsZXQtdmFsdWVzIGxldCotdmFsdWVzIGRlZmluZS1zeW50YXggc3ludGF4LXJ1bGVzIGRlZmluZS12YWx1ZXMgd2hlbiB1bmxlc3NcIik7XG5mdW5jdGlvbiBzdGF0ZVN0YWNrKGluZGVudCwgdHlwZSwgcHJldikge1xuICAvLyByZXByZXNlbnRzIGEgc3RhdGUgc3RhY2sgb2JqZWN0XG4gIHRoaXMuaW5kZW50ID0gaW5kZW50O1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLnByZXYgPSBwcmV2O1xufVxuZnVuY3Rpb24gcHVzaFN0YWNrKHN0YXRlLCBpbmRlbnQsIHR5cGUpIHtcbiAgc3RhdGUuaW5kZW50U3RhY2sgPSBuZXcgc3RhdGVTdGFjayhpbmRlbnQsIHR5cGUsIHN0YXRlLmluZGVudFN0YWNrKTtcbn1cbmZ1bmN0aW9uIHBvcFN0YWNrKHN0YXRlKSB7XG4gIHN0YXRlLmluZGVudFN0YWNrID0gc3RhdGUuaW5kZW50U3RhY2sucHJldjtcbn1cbnZhciBiaW5hcnlNYXRjaGVyID0gbmV3IFJlZ0V4cCgvXig/OlstK11pfFstK11bMDFdKyMqKD86XFwvWzAxXSsjKik/aXxbLStdP1swMV0rIyooPzpcXC9bMDFdKyMqKT9AWy0rXT9bMDFdKyMqKD86XFwvWzAxXSsjKik/fFstK10/WzAxXSsjKig/OlxcL1swMV0rIyopP1stK10oPzpbMDFdKyMqKD86XFwvWzAxXSsjKik/KT9pfFstK10/WzAxXSsjKig/OlxcL1swMV0rIyopPykoPz1bKClcXHM7XCJdfCQpL2kpO1xudmFyIG9jdGFsTWF0Y2hlciA9IG5ldyBSZWdFeHAoL14oPzpbLStdaXxbLStdWzAtN10rIyooPzpcXC9bMC03XSsjKik/aXxbLStdP1swLTddKyMqKD86XFwvWzAtN10rIyopP0BbLStdP1swLTddKyMqKD86XFwvWzAtN10rIyopP3xbLStdP1swLTddKyMqKD86XFwvWzAtN10rIyopP1stK10oPzpbMC03XSsjKig/OlxcL1swLTddKyMqKT8pP2l8Wy0rXT9bMC03XSsjKig/OlxcL1swLTddKyMqKT8pKD89WygpXFxzO1wiXXwkKS9pKTtcbnZhciBoZXhNYXRjaGVyID0gbmV3IFJlZ0V4cCgvXig/OlstK11pfFstK11bXFxkYS1mXSsjKig/OlxcL1tcXGRhLWZdKyMqKT9pfFstK10/W1xcZGEtZl0rIyooPzpcXC9bXFxkYS1mXSsjKik/QFstK10/W1xcZGEtZl0rIyooPzpcXC9bXFxkYS1mXSsjKik/fFstK10/W1xcZGEtZl0rIyooPzpcXC9bXFxkYS1mXSsjKik/Wy0rXSg/OltcXGRhLWZdKyMqKD86XFwvW1xcZGEtZl0rIyopPyk/aXxbLStdP1tcXGRhLWZdKyMqKD86XFwvW1xcZGEtZl0rIyopPykoPz1bKClcXHM7XCJdfCQpL2kpO1xudmFyIGRlY2ltYWxNYXRjaGVyID0gbmV3IFJlZ0V4cCgvXig/OlstK11pfFstK10oPzooPzooPzpcXGQrIytcXC4/Iyp8XFxkK1xcLlxcZCojKnxcXC5cXGQrIyp8XFxkKykoPzpbZXNmZGxdWy0rXT9cXGQrKT8pfFxcZCsjKlxcL1xcZCsjKilpfFstK10/KD86KD86KD86XFxkKyMrXFwuPyMqfFxcZCtcXC5cXGQqIyp8XFwuXFxkKyMqfFxcZCspKD86W2VzZmRsXVstK10/XFxkKyk/KXxcXGQrIypcXC9cXGQrIyopQFstK10/KD86KD86KD86XFxkKyMrXFwuPyMqfFxcZCtcXC5cXGQqIyp8XFwuXFxkKyMqfFxcZCspKD86W2VzZmRsXVstK10/XFxkKyk/KXxcXGQrIypcXC9cXGQrIyopfFstK10/KD86KD86KD86XFxkKyMrXFwuPyMqfFxcZCtcXC5cXGQqIyp8XFwuXFxkKyMqfFxcZCspKD86W2VzZmRsXVstK10/XFxkKyk/KXxcXGQrIypcXC9cXGQrIyopWy0rXSg/Oig/Oig/OlxcZCsjK1xcLj8jKnxcXGQrXFwuXFxkKiMqfFxcLlxcZCsjKnxcXGQrKSg/Oltlc2ZkbF1bLStdP1xcZCspPyl8XFxkKyMqXFwvXFxkKyMqKT9pfCg/Oig/Oig/OlxcZCsjK1xcLj8jKnxcXGQrXFwuXFxkKiMqfFxcLlxcZCsjKnxcXGQrKSg/Oltlc2ZkbF1bLStdP1xcZCspPyl8XFxkKyMqXFwvXFxkKyMqKSkoPz1bKClcXHM7XCJdfCQpL2kpO1xuZnVuY3Rpb24gaXNCaW5hcnlOdW1iZXIoc3RyZWFtKSB7XG4gIHJldHVybiBzdHJlYW0ubWF0Y2goYmluYXJ5TWF0Y2hlcik7XG59XG5mdW5jdGlvbiBpc09jdGFsTnVtYmVyKHN0cmVhbSkge1xuICByZXR1cm4gc3RyZWFtLm1hdGNoKG9jdGFsTWF0Y2hlcik7XG59XG5mdW5jdGlvbiBpc0RlY2ltYWxOdW1iZXIoc3RyZWFtLCBiYWNrdXApIHtcbiAgaWYgKGJhY2t1cCA9PT0gdHJ1ZSkge1xuICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gIH1cbiAgcmV0dXJuIHN0cmVhbS5tYXRjaChkZWNpbWFsTWF0Y2hlcik7XG59XG5mdW5jdGlvbiBpc0hleE51bWJlcihzdHJlYW0pIHtcbiAgcmV0dXJuIHN0cmVhbS5tYXRjaChoZXhNYXRjaGVyKTtcbn1cbmZ1bmN0aW9uIHByb2Nlc3NFc2NhcGVkU2VxdWVuY2Uoc3RyZWFtLCBvcHRpb25zKSB7XG4gIHZhciBuZXh0LFxuICAgIGVzY2FwZWQgPSBmYWxzZTtcbiAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgIGlmIChuZXh0ID09IG9wdGlvbnMudG9rZW4gJiYgIWVzY2FwZWQpIHtcbiAgICAgIG9wdGlvbnMuc3RhdGUubW9kZSA9IGZhbHNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICB9XG59XG5leHBvcnQgY29uc3Qgc2NoZW1lID0ge1xuICBuYW1lOiBcInNjaGVtZVwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIGluZGVudFN0YWNrOiBudWxsLFxuICAgICAgaW5kZW50YXRpb246IDAsXG4gICAgICBtb2RlOiBmYWxzZSxcbiAgICAgIHNFeHByQ29tbWVudDogZmFsc2UsXG4gICAgICBzRXhwclF1b3RlOiBmYWxzZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdGF0ZS5pbmRlbnRTdGFjayA9PSBudWxsICYmIHN0cmVhbS5zb2woKSkge1xuICAgICAgLy8gdXBkYXRlIGluZGVudGF0aW9uLCBidXQgb25seSBpZiBpbmRlbnRTdGFjayBpcyBlbXB0eVxuICAgICAgc3RhdGUuaW5kZW50YXRpb24gPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICB9XG5cbiAgICAvLyBza2lwIHNwYWNlc1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIHZhciByZXR1cm5UeXBlID0gbnVsbDtcbiAgICBzd2l0Y2ggKHN0YXRlLm1vZGUpIHtcbiAgICAgIGNhc2UgXCJzdHJpbmdcIjpcbiAgICAgICAgLy8gbXVsdGktbGluZSBzdHJpbmcgcGFyc2luZyBtb2RlXG4gICAgICAgIHByb2Nlc3NFc2NhcGVkU2VxdWVuY2Uoc3RyZWFtLCB7XG4gICAgICAgICAgdG9rZW46IFwiXFxcIlwiLFxuICAgICAgICAgIHN0YXRlOiBzdGF0ZVxuICAgICAgICB9KTtcbiAgICAgICAgcmV0dXJuVHlwZSA9IFNUUklORzsgLy8gY29udGludWUgb24gaW4gc2NoZW1lLXN0cmluZyBtb2RlXG4gICAgICAgIGJyZWFrO1xuICAgICAgY2FzZSBcInN5bWJvbFwiOlxuICAgICAgICAvLyBlc2NhcGUgc3ltYm9sXG4gICAgICAgIHByb2Nlc3NFc2NhcGVkU2VxdWVuY2Uoc3RyZWFtLCB7XG4gICAgICAgICAgdG9rZW46IFwifFwiLFxuICAgICAgICAgIHN0YXRlOiBzdGF0ZVxuICAgICAgICB9KTtcbiAgICAgICAgcmV0dXJuVHlwZSA9IFNZTUJPTDsgLy8gY29udGludWUgb24gaW4gc2NoZW1lLXN5bWJvbCBtb2RlXG4gICAgICAgIGJyZWFrO1xuICAgICAgY2FzZSBcImNvbW1lbnRcIjpcbiAgICAgICAgLy8gY29tbWVudCBwYXJzaW5nIG1vZGVcbiAgICAgICAgdmFyIG5leHQsXG4gICAgICAgICAgbWF5YmVFbmQgPSBmYWxzZTtcbiAgICAgICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgICAgIGlmIChuZXh0ID09IFwiI1wiICYmIG1heWJlRW5kKSB7XG4gICAgICAgICAgICBzdGF0ZS5tb2RlID0gZmFsc2U7XG4gICAgICAgICAgICBicmVhaztcbiAgICAgICAgICB9XG4gICAgICAgICAgbWF5YmVFbmQgPSBuZXh0ID09IFwifFwiO1xuICAgICAgICB9XG4gICAgICAgIHJldHVyblR5cGUgPSBDT01NRU5UO1xuICAgICAgICBicmVhaztcbiAgICAgIGNhc2UgXCJzLWV4cHItY29tbWVudFwiOlxuICAgICAgICAvLyBzLWV4cHIgY29tbWVudGluZyBtb2RlXG4gICAgICAgIHN0YXRlLm1vZGUgPSBmYWxzZTtcbiAgICAgICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gXCIoXCIgfHwgc3RyZWFtLnBlZWsoKSA9PSBcIltcIikge1xuICAgICAgICAgIC8vIGFjdHVhbGx5IHN0YXJ0IHNjaGVtZSBzLWV4cHIgY29tbWVudGluZyBtb2RlXG4gICAgICAgICAgc3RhdGUuc0V4cHJDb21tZW50ID0gMDtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAvLyBpZiBub3Qgd2UganVzdCBjb21tZW50IHRoZSBlbnRpcmUgb2YgdGhlIG5leHQgdG9rZW5cbiAgICAgICAgICBzdHJlYW0uZWF0V2hpbGUoL1teXFxzXFwoXFwpXFxbXFxdXS8pOyAvLyBlYXQgc3ltYm9sIGF0b21cbiAgICAgICAgICByZXR1cm5UeXBlID0gQ09NTUVOVDtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgZGVmYXVsdDpcbiAgICAgICAgLy8gZGVmYXVsdCBwYXJzaW5nIG1vZGVcbiAgICAgICAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgICAgICAgaWYgKGNoID09IFwiXFxcIlwiKSB7XG4gICAgICAgICAgc3RhdGUubW9kZSA9IFwic3RyaW5nXCI7XG4gICAgICAgICAgcmV0dXJuVHlwZSA9IFNUUklORztcbiAgICAgICAgfSBlbHNlIGlmIChjaCA9PSBcIidcIikge1xuICAgICAgICAgIGlmIChzdHJlYW0ucGVlaygpID09IFwiKFwiIHx8IHN0cmVhbS5wZWVrKCkgPT0gXCJbXCIpIHtcbiAgICAgICAgICAgIGlmICh0eXBlb2Ygc3RhdGUuc0V4cHJRdW90ZSAhPSBcIm51bWJlclwiKSB7XG4gICAgICAgICAgICAgIHN0YXRlLnNFeHByUXVvdGUgPSAwO1xuICAgICAgICAgICAgfSAvLyBlbHNlIGFscmVhZHkgaW4gYSBxdW90ZWQgZXhwcmVzc2lvblxuICAgICAgICAgICAgcmV0dXJuVHlwZSA9IEFUT007XG4gICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd19cXC0hJCUmKitcXC5cXC86PD0+P0BcXF5+XS8pO1xuICAgICAgICAgICAgcmV0dXJuVHlwZSA9IEFUT007XG4gICAgICAgICAgfVxuICAgICAgICB9IGVsc2UgaWYgKGNoID09ICd8Jykge1xuICAgICAgICAgIHN0YXRlLm1vZGUgPSBcInN5bWJvbFwiO1xuICAgICAgICAgIHJldHVyblR5cGUgPSBTWU1CT0w7XG4gICAgICAgIH0gZWxzZSBpZiAoY2ggPT0gJyMnKSB7XG4gICAgICAgICAgaWYgKHN0cmVhbS5lYXQoXCJ8XCIpKSB7XG4gICAgICAgICAgICAvLyBNdWx0aS1saW5lIGNvbW1lbnRcbiAgICAgICAgICAgIHN0YXRlLm1vZGUgPSBcImNvbW1lbnRcIjsgLy8gdG9nZ2xlIHRvIGNvbW1lbnQgbW9kZVxuICAgICAgICAgICAgcmV0dXJuVHlwZSA9IENPTU1FTlQ7XG4gICAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KC9bdGZdL2kpKSB7XG4gICAgICAgICAgICAvLyAjdC8jZiAoYXRvbSlcbiAgICAgICAgICAgIHJldHVyblR5cGUgPSBBVE9NO1xuICAgICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdCgnOycpKSB7XG4gICAgICAgICAgICAvLyBTLUV4cHIgY29tbWVudFxuICAgICAgICAgICAgc3RhdGUubW9kZSA9IFwicy1leHByLWNvbW1lbnRcIjtcbiAgICAgICAgICAgIHJldHVyblR5cGUgPSBDT01NRU5UO1xuICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICB2YXIgbnVtVGVzdCA9IG51bGwsXG4gICAgICAgICAgICAgIGhhc0V4YWN0bmVzcyA9IGZhbHNlLFxuICAgICAgICAgICAgICBoYXNSYWRpeCA9IHRydWU7XG4gICAgICAgICAgICBpZiAoc3RyZWFtLmVhdCgvW2VpXS9pKSkge1xuICAgICAgICAgICAgICBoYXNFeGFjdG5lc3MgPSB0cnVlO1xuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgc3RyZWFtLmJhY2tVcCgxKTsgLy8gbXVzdCBiZSByYWRpeCBzcGVjaWZpZXJcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14jYi9pKSkge1xuICAgICAgICAgICAgICBudW1UZXN0ID0gaXNCaW5hcnlOdW1iZXI7XG4gICAgICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXiNvL2kpKSB7XG4gICAgICAgICAgICAgIG51bVRlc3QgPSBpc09jdGFsTnVtYmVyO1xuICAgICAgICAgICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL14jeC9pKSkge1xuICAgICAgICAgICAgICBudW1UZXN0ID0gaXNIZXhOdW1iZXI7XG4gICAgICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXiNkL2kpKSB7XG4gICAgICAgICAgICAgIG51bVRlc3QgPSBpc0RlY2ltYWxOdW1iZXI7XG4gICAgICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXlstKzAtOS5dLywgZmFsc2UpKSB7XG4gICAgICAgICAgICAgIGhhc1JhZGl4ID0gZmFsc2U7XG4gICAgICAgICAgICAgIG51bVRlc3QgPSBpc0RlY2ltYWxOdW1iZXI7XG4gICAgICAgICAgICAgIC8vIHJlLWNvbnN1bWUgdGhlIGluaXRpYWwgIyBpZiBhbGwgbWF0Y2hlcyBmYWlsZWRcbiAgICAgICAgICAgIH0gZWxzZSBpZiAoIWhhc0V4YWN0bmVzcykge1xuICAgICAgICAgICAgICBzdHJlYW0uZWF0KCcjJyk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBpZiAobnVtVGVzdCAhPSBudWxsKSB7XG4gICAgICAgICAgICAgIGlmIChoYXNSYWRpeCAmJiAhaGFzRXhhY3RuZXNzKSB7XG4gICAgICAgICAgICAgICAgLy8gY29uc3VtZSBvcHRpb25hbCBleGFjdG5lc3MgYWZ0ZXIgcmFkaXhcbiAgICAgICAgICAgICAgICBzdHJlYW0ubWF0Y2goL14jW2VpXS9pKTtcbiAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICBpZiAobnVtVGVzdChzdHJlYW0pKSByZXR1cm5UeXBlID0gTlVNQkVSO1xuICAgICAgICAgICAgfVxuICAgICAgICAgIH1cbiAgICAgICAgfSBlbHNlIGlmICgvXlstKzAtOS5dLy50ZXN0KGNoKSAmJiBpc0RlY2ltYWxOdW1iZXIoc3RyZWFtLCB0cnVlKSkge1xuICAgICAgICAgIC8vIG1hdGNoIG5vbi1wcmVmaXhlZCBudW1iZXIsIG11c3QgYmUgZGVjaW1hbFxuICAgICAgICAgIHJldHVyblR5cGUgPSBOVU1CRVI7XG4gICAgICAgIH0gZWxzZSBpZiAoY2ggPT0gXCI7XCIpIHtcbiAgICAgICAgICAvLyBjb21tZW50XG4gICAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpOyAvLyByZXN0IG9mIHRoZSBsaW5lIGlzIGEgY29tbWVudFxuICAgICAgICAgIHJldHVyblR5cGUgPSBDT01NRU5UO1xuICAgICAgICB9IGVsc2UgaWYgKGNoID09IFwiKFwiIHx8IGNoID09IFwiW1wiKSB7XG4gICAgICAgICAgdmFyIGtleVdvcmQgPSAnJztcbiAgICAgICAgICB2YXIgaW5kZW50VGVtcCA9IHN0cmVhbS5jb2x1bW4oKSxcbiAgICAgICAgICAgIGxldHRlcjtcbiAgICAgICAgICAvKipcbiAgICAgICAgICAgICBFaXRoZXJcbiAgICAgICAgICAgICAoaW5kZW50LXdvcmQgLi5cbiAgICAgICAgICAgICAobm9uLWluZGVudC13b3JkIC4uXG4gICAgICAgICAgICAgKDtzb21ldGhpbmcgZWxzZSwgYnJhY2tldCwgZXRjLlxuICAgICAgICAgICovXG5cbiAgICAgICAgICB3aGlsZSAoKGxldHRlciA9IHN0cmVhbS5lYXQoL1teXFxzXFwoXFxbXFw7XFwpXFxdXS8pKSAhPSBudWxsKSB7XG4gICAgICAgICAgICBrZXlXb3JkICs9IGxldHRlcjtcbiAgICAgICAgICB9XG4gICAgICAgICAgaWYgKGtleVdvcmQubGVuZ3RoID4gMCAmJiBpbmRlbnRLZXlzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGtleVdvcmQpKSB7XG4gICAgICAgICAgICAvLyBpbmRlbnQtd29yZFxuXG4gICAgICAgICAgICBwdXNoU3RhY2soc3RhdGUsIGluZGVudFRlbXAgKyBJTkRFTlRfV09SRF9TS0lQLCBjaCk7XG4gICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIC8vIG5vbi1pbmRlbnQgd29yZFxuICAgICAgICAgICAgLy8gd2UgY29udGludWUgZWF0aW5nIHRoZSBzcGFjZXNcbiAgICAgICAgICAgIHN0cmVhbS5lYXRTcGFjZSgpO1xuICAgICAgICAgICAgaWYgKHN0cmVhbS5lb2woKSB8fCBzdHJlYW0ucGVlaygpID09IFwiO1wiKSB7XG4gICAgICAgICAgICAgIC8vIG5vdGhpbmcgc2lnbmlmaWNhbnQgYWZ0ZXJcbiAgICAgICAgICAgICAgLy8gd2UgcmVzdGFydCBpbmRlbnRhdGlvbiAxIHNwYWNlIGFmdGVyXG4gICAgICAgICAgICAgIHB1c2hTdGFjayhzdGF0ZSwgaW5kZW50VGVtcCArIDEsIGNoKTtcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgIHB1c2hTdGFjayhzdGF0ZSwgaW5kZW50VGVtcCArIHN0cmVhbS5jdXJyZW50KCkubGVuZ3RoLCBjaCk7IC8vIGVsc2Ugd2UgbWF0Y2hcbiAgICAgICAgICAgIH1cbiAgICAgICAgICB9XG4gICAgICAgICAgc3RyZWFtLmJhY2tVcChzdHJlYW0uY3VycmVudCgpLmxlbmd0aCAtIDEpOyAvLyB1bmRvIGFsbCB0aGUgZWF0aW5nXG5cbiAgICAgICAgICBpZiAodHlwZW9mIHN0YXRlLnNFeHByQ29tbWVudCA9PSBcIm51bWJlclwiKSBzdGF0ZS5zRXhwckNvbW1lbnQrKztcbiAgICAgICAgICBpZiAodHlwZW9mIHN0YXRlLnNFeHByUXVvdGUgPT0gXCJudW1iZXJcIikgc3RhdGUuc0V4cHJRdW90ZSsrO1xuICAgICAgICAgIHJldHVyblR5cGUgPSBCUkFDS0VUO1xuICAgICAgICB9IGVsc2UgaWYgKGNoID09IFwiKVwiIHx8IGNoID09IFwiXVwiKSB7XG4gICAgICAgICAgcmV0dXJuVHlwZSA9IEJSQUNLRVQ7XG4gICAgICAgICAgaWYgKHN0YXRlLmluZGVudFN0YWNrICE9IG51bGwgJiYgc3RhdGUuaW5kZW50U3RhY2sudHlwZSA9PSAoY2ggPT0gXCIpXCIgPyBcIihcIiA6IFwiW1wiKSkge1xuICAgICAgICAgICAgcG9wU3RhY2soc3RhdGUpO1xuICAgICAgICAgICAgaWYgKHR5cGVvZiBzdGF0ZS5zRXhwckNvbW1lbnQgPT0gXCJudW1iZXJcIikge1xuICAgICAgICAgICAgICBpZiAoLS1zdGF0ZS5zRXhwckNvbW1lbnQgPT0gMCkge1xuICAgICAgICAgICAgICAgIHJldHVyblR5cGUgPSBDT01NRU5UOyAvLyBmaW5hbCBjbG9zaW5nIGJyYWNrZXRcbiAgICAgICAgICAgICAgICBzdGF0ZS5zRXhwckNvbW1lbnQgPSBmYWxzZTsgLy8gdHVybiBvZmYgcy1leHByIGNvbW1lbnRpbmcgbW9kZVxuICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBpZiAodHlwZW9mIHN0YXRlLnNFeHByUXVvdGUgPT0gXCJudW1iZXJcIikge1xuICAgICAgICAgICAgICBpZiAoLS1zdGF0ZS5zRXhwclF1b3RlID09IDApIHtcbiAgICAgICAgICAgICAgICByZXR1cm5UeXBlID0gQVRPTTsgLy8gZmluYWwgY2xvc2luZyBicmFja2V0XG4gICAgICAgICAgICAgICAgc3RhdGUuc0V4cHJRdW90ZSA9IGZhbHNlOyAvLyB0dXJuIG9mZiBzLWV4cHIgcXVvdGUgbW9kZVxuICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgICAgfVxuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd19cXC0hJCUmKitcXC5cXC86PD0+P0BcXF5+XS8pO1xuICAgICAgICAgIGlmIChrZXl3b3JkcyAmJiBrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShzdHJlYW0uY3VycmVudCgpKSkge1xuICAgICAgICAgICAgcmV0dXJuVHlwZSA9IEJVSUxUSU47XG4gICAgICAgICAgfSBlbHNlIHJldHVyblR5cGUgPSBcInZhcmlhYmxlXCI7XG4gICAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIHR5cGVvZiBzdGF0ZS5zRXhwckNvbW1lbnQgPT0gXCJudW1iZXJcIiA/IENPTU1FTlQgOiB0eXBlb2Ygc3RhdGUuc0V4cHJRdW90ZSA9PSBcIm51bWJlclwiID8gQVRPTSA6IHJldHVyblR5cGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlKSB7XG4gICAgaWYgKHN0YXRlLmluZGVudFN0YWNrID09IG51bGwpIHJldHVybiBzdGF0ZS5pbmRlbnRhdGlvbjtcbiAgICByZXR1cm4gc3RhdGUuaW5kZW50U3RhY2suaW5kZW50O1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjbG9zZUJyYWNrZXRzOiB7XG4gICAgICBicmFja2V0czogW1wiKFwiLCBcIltcIiwgXCJ7XCIsICdcIiddXG4gICAgfSxcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIjs7XCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==