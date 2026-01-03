"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1133],{

/***/ 71133
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   forth: () => (/* binding */ forth)
/* harmony export */ });
function toWordList(words) {
  var ret = [];
  words.split(' ').forEach(function (e) {
    ret.push({
      name: e
    });
  });
  return ret;
}
var coreWordList = toWordList('INVERT AND OR XOR\
 2* 2/ LSHIFT RSHIFT\
 0= = 0< < > U< MIN MAX\
 2DROP 2DUP 2OVER 2SWAP ?DUP DEPTH DROP DUP OVER ROT SWAP\
 >R R> R@\
 + - 1+ 1- ABS NEGATE\
 S>D * M* UM*\
 FM/MOD SM/REM UM/MOD */ */MOD / /MOD MOD\
 HERE , @ ! CELL+ CELLS C, C@ C! CHARS 2@ 2!\
 ALIGN ALIGNED +! ALLOT\
 CHAR [CHAR] [ ] BL\
 FIND EXECUTE IMMEDIATE COUNT LITERAL STATE\
 ; DOES> >BODY\
 EVALUATE\
 SOURCE >IN\
 <# # #S #> HOLD SIGN BASE >NUMBER HEX DECIMAL\
 FILL MOVE\
 . CR EMIT SPACE SPACES TYPE U. .R U.R\
 ACCEPT\
 TRUE FALSE\
 <> U> 0<> 0>\
 NIP TUCK ROLL PICK\
 2>R 2R@ 2R>\
 WITHIN UNUSED MARKER\
 I J\
 TO\
 COMPILE, [COMPILE]\
 SAVE-INPUT RESTORE-INPUT\
 PAD ERASE\
 2LITERAL DNEGATE\
 D- D+ D0< D0= D2* D2/ D< D= DMAX DMIN D>S DABS\
 M+ M*/ D. D.R 2ROT DU<\
 CATCH THROW\
 FREE RESIZE ALLOCATE\
 CS-PICK CS-ROLL\
 GET-CURRENT SET-CURRENT FORTH-WORDLIST GET-ORDER SET-ORDER\
 PREVIOUS SEARCH-WORDLIST WORDLIST FIND ALSO ONLY FORTH DEFINITIONS ORDER\
 -TRAILING /STRING SEARCH COMPARE CMOVE CMOVE> BLANK SLITERAL');
var immediateWordList = toWordList('IF ELSE THEN BEGIN WHILE REPEAT UNTIL RECURSE [IF] [ELSE] [THEN] ?DO DO LOOP +LOOP UNLOOP LEAVE EXIT AGAIN CASE OF ENDOF ENDCASE');
function searchWordList(wordList, word) {
  var i;
  for (i = wordList.length - 1; i >= 0; i--) {
    if (wordList[i].name === word.toUpperCase()) {
      return wordList[i];
    }
  }
  return undefined;
}
const forth = {
  name: "forth",
  startState: function () {
    return {
      state: '',
      base: 10,
      coreWordList: coreWordList,
      immediateWordList: immediateWordList,
      wordList: []
    };
  },
  token: function (stream, stt) {
    var mat;
    if (stream.eatSpace()) {
      return null;
    }
    if (stt.state === '') {
      // interpretation
      if (stream.match(/^(\]|:NONAME)(\s|$)/i)) {
        stt.state = ' compilation';
        return 'builtin';
      }
      mat = stream.match(/^(\:)\s+(\S+)(\s|$)+/);
      if (mat) {
        stt.wordList.push({
          name: mat[2].toUpperCase()
        });
        stt.state = ' compilation';
        return 'def';
      }
      mat = stream.match(/^(VARIABLE|2VARIABLE|CONSTANT|2CONSTANT|CREATE|POSTPONE|VALUE|WORD)\s+(\S+)(\s|$)+/i);
      if (mat) {
        stt.wordList.push({
          name: mat[2].toUpperCase()
        });
        return 'def';
      }
      mat = stream.match(/^(\'|\[\'\])\s+(\S+)(\s|$)+/);
      if (mat) {
        return 'builtin';
      }
    } else {
      // compilation
      // ; [
      if (stream.match(/^(\;|\[)(\s)/)) {
        stt.state = '';
        stream.backUp(1);
        return 'builtin';
      }
      if (stream.match(/^(\;|\[)($)/)) {
        stt.state = '';
        return 'builtin';
      }
      if (stream.match(/^(POSTPONE)\s+\S+(\s|$)+/)) {
        return 'builtin';
      }
    }

    // dynamic wordlist
    mat = stream.match(/^(\S+)(\s+|$)/);
    if (mat) {
      if (searchWordList(stt.wordList, mat[1]) !== undefined) {
        return 'variable';
      }

      // comments
      if (mat[1] === '\\') {
        stream.skipToEnd();
        return 'comment';
      }

      // core words
      if (searchWordList(stt.coreWordList, mat[1]) !== undefined) {
        return 'builtin';
      }
      if (searchWordList(stt.immediateWordList, mat[1]) !== undefined) {
        return 'keyword';
      }
      if (mat[1] === '(') {
        stream.eatWhile(function (s) {
          return s !== ')';
        });
        stream.eat(')');
        return 'comment';
      }

      // // strings
      if (mat[1] === '.(') {
        stream.eatWhile(function (s) {
          return s !== ')';
        });
        stream.eat(')');
        return 'string';
      }
      if (mat[1] === 'S"' || mat[1] === '."' || mat[1] === 'C"') {
        stream.eatWhile(function (s) {
          return s !== '"';
        });
        stream.eat('"');
        return 'string';
      }

      // numbers
      if (mat[1] - 0xfffffffff) {
        return 'number';
      }
      // if (mat[1].match(/^[-+]?[0-9]+\.[0-9]*/)) {
      //     return 'number';
      // }

      return 'atom';
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTEzMy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2ZvcnRoLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIHRvV29yZExpc3Qod29yZHMpIHtcbiAgdmFyIHJldCA9IFtdO1xuICB3b3Jkcy5zcGxpdCgnICcpLmZvckVhY2goZnVuY3Rpb24gKGUpIHtcbiAgICByZXQucHVzaCh7XG4gICAgICBuYW1lOiBlXG4gICAgfSk7XG4gIH0pO1xuICByZXR1cm4gcmV0O1xufVxudmFyIGNvcmVXb3JkTGlzdCA9IHRvV29yZExpc3QoJ0lOVkVSVCBBTkQgT1IgWE9SXFxcbiAyKiAyLyBMU0hJRlQgUlNISUZUXFxcbiAwPSA9IDA8IDwgPiBVPCBNSU4gTUFYXFxcbiAyRFJPUCAyRFVQIDJPVkVSIDJTV0FQID9EVVAgREVQVEggRFJPUCBEVVAgT1ZFUiBST1QgU1dBUFxcXG4gPlIgUj4gUkBcXFxuICsgLSAxKyAxLSBBQlMgTkVHQVRFXFxcbiBTPkQgKiBNKiBVTSpcXFxuIEZNL01PRCBTTS9SRU0gVU0vTU9EICovICovTU9EIC8gL01PRCBNT0RcXFxuIEhFUkUgLCBAICEgQ0VMTCsgQ0VMTFMgQywgQ0AgQyEgQ0hBUlMgMkAgMiFcXFxuIEFMSUdOIEFMSUdORUQgKyEgQUxMT1RcXFxuIENIQVIgW0NIQVJdIFsgXSBCTFxcXG4gRklORCBFWEVDVVRFIElNTUVESUFURSBDT1VOVCBMSVRFUkFMIFNUQVRFXFxcbiA7IERPRVM+ID5CT0RZXFxcbiBFVkFMVUFURVxcXG4gU09VUkNFID5JTlxcXG4gPCMgIyAjUyAjPiBIT0xEIFNJR04gQkFTRSA+TlVNQkVSIEhFWCBERUNJTUFMXFxcbiBGSUxMIE1PVkVcXFxuIC4gQ1IgRU1JVCBTUEFDRSBTUEFDRVMgVFlQRSBVLiAuUiBVLlJcXFxuIEFDQ0VQVFxcXG4gVFJVRSBGQUxTRVxcXG4gPD4gVT4gMDw+IDA+XFxcbiBOSVAgVFVDSyBST0xMIFBJQ0tcXFxuIDI+UiAyUkAgMlI+XFxcbiBXSVRISU4gVU5VU0VEIE1BUktFUlxcXG4gSSBKXFxcbiBUT1xcXG4gQ09NUElMRSwgW0NPTVBJTEVdXFxcbiBTQVZFLUlOUFVUIFJFU1RPUkUtSU5QVVRcXFxuIFBBRCBFUkFTRVxcXG4gMkxJVEVSQUwgRE5FR0FURVxcXG4gRC0gRCsgRDA8IEQwPSBEMiogRDIvIEQ8IEQ9IERNQVggRE1JTiBEPlMgREFCU1xcXG4gTSsgTSovIEQuIEQuUiAyUk9UIERVPFxcXG4gQ0FUQ0ggVEhST1dcXFxuIEZSRUUgUkVTSVpFIEFMTE9DQVRFXFxcbiBDUy1QSUNLIENTLVJPTExcXFxuIEdFVC1DVVJSRU5UIFNFVC1DVVJSRU5UIEZPUlRILVdPUkRMSVNUIEdFVC1PUkRFUiBTRVQtT1JERVJcXFxuIFBSRVZJT1VTIFNFQVJDSC1XT1JETElTVCBXT1JETElTVCBGSU5EIEFMU08gT05MWSBGT1JUSCBERUZJTklUSU9OUyBPUkRFUlxcXG4gLVRSQUlMSU5HIC9TVFJJTkcgU0VBUkNIIENPTVBBUkUgQ01PVkUgQ01PVkU+IEJMQU5LIFNMSVRFUkFMJyk7XG52YXIgaW1tZWRpYXRlV29yZExpc3QgPSB0b1dvcmRMaXN0KCdJRiBFTFNFIFRIRU4gQkVHSU4gV0hJTEUgUkVQRUFUIFVOVElMIFJFQ1VSU0UgW0lGXSBbRUxTRV0gW1RIRU5dID9ETyBETyBMT09QICtMT09QIFVOTE9PUCBMRUFWRSBFWElUIEFHQUlOIENBU0UgT0YgRU5ET0YgRU5EQ0FTRScpO1xuZnVuY3Rpb24gc2VhcmNoV29yZExpc3Qod29yZExpc3QsIHdvcmQpIHtcbiAgdmFyIGk7XG4gIGZvciAoaSA9IHdvcmRMaXN0Lmxlbmd0aCAtIDE7IGkgPj0gMDsgaS0tKSB7XG4gICAgaWYgKHdvcmRMaXN0W2ldLm5hbWUgPT09IHdvcmQudG9VcHBlckNhc2UoKSkge1xuICAgICAgcmV0dXJuIHdvcmRMaXN0W2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdW5kZWZpbmVkO1xufVxuZXhwb3J0IGNvbnN0IGZvcnRoID0ge1xuICBuYW1lOiBcImZvcnRoXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgc3RhdGU6ICcnLFxuICAgICAgYmFzZTogMTAsXG4gICAgICBjb3JlV29yZExpc3Q6IGNvcmVXb3JkTGlzdCxcbiAgICAgIGltbWVkaWF0ZVdvcmRMaXN0OiBpbW1lZGlhdGVXb3JkTGlzdCxcbiAgICAgIHdvcmRMaXN0OiBbXVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdHQpIHtcbiAgICB2YXIgbWF0O1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIGlmIChzdHQuc3RhdGUgPT09ICcnKSB7XG4gICAgICAvLyBpbnRlcnByZXRhdGlvblxuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXihcXF18Ok5PTkFNRSkoXFxzfCQpL2kpKSB7XG4gICAgICAgIHN0dC5zdGF0ZSA9ICcgY29tcGlsYXRpb24nO1xuICAgICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgICAgfVxuICAgICAgbWF0ID0gc3RyZWFtLm1hdGNoKC9eKFxcOilcXHMrKFxcUyspKFxcc3wkKSsvKTtcbiAgICAgIGlmIChtYXQpIHtcbiAgICAgICAgc3R0LndvcmRMaXN0LnB1c2goe1xuICAgICAgICAgIG5hbWU6IG1hdFsyXS50b1VwcGVyQ2FzZSgpXG4gICAgICAgIH0pO1xuICAgICAgICBzdHQuc3RhdGUgPSAnIGNvbXBpbGF0aW9uJztcbiAgICAgICAgcmV0dXJuICdkZWYnO1xuICAgICAgfVxuICAgICAgbWF0ID0gc3RyZWFtLm1hdGNoKC9eKFZBUklBQkxFfDJWQVJJQUJMRXxDT05TVEFOVHwyQ09OU1RBTlR8Q1JFQVRFfFBPU1RQT05FfFZBTFVFfFdPUkQpXFxzKyhcXFMrKShcXHN8JCkrL2kpO1xuICAgICAgaWYgKG1hdCkge1xuICAgICAgICBzdHQud29yZExpc3QucHVzaCh7XG4gICAgICAgICAgbmFtZTogbWF0WzJdLnRvVXBwZXJDYXNlKClcbiAgICAgICAgfSk7XG4gICAgICAgIHJldHVybiAnZGVmJztcbiAgICAgIH1cbiAgICAgIG1hdCA9IHN0cmVhbS5tYXRjaCgvXihcXCd8XFxbXFwnXFxdKVxccysoXFxTKykoXFxzfCQpKy8pO1xuICAgICAgaWYgKG1hdCkge1xuICAgICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgICAgfVxuICAgIH0gZWxzZSB7XG4gICAgICAvLyBjb21waWxhdGlvblxuICAgICAgLy8gOyBbXG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9eKFxcO3xcXFspKFxccykvKSkge1xuICAgICAgICBzdHQuc3RhdGUgPSAnJztcbiAgICAgICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICAgICAgcmV0dXJuICdidWlsdGluJztcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14oXFw7fFxcWykoJCkvKSkge1xuICAgICAgICBzdHQuc3RhdGUgPSAnJztcbiAgICAgICAgcmV0dXJuICdidWlsdGluJztcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL14oUE9TVFBPTkUpXFxzK1xcUysoXFxzfCQpKy8pKSB7XG4gICAgICAgIHJldHVybiAnYnVpbHRpbic7XG4gICAgICB9XG4gICAgfVxuXG4gICAgLy8gZHluYW1pYyB3b3JkbGlzdFxuICAgIG1hdCA9IHN0cmVhbS5tYXRjaCgvXihcXFMrKShcXHMrfCQpLyk7XG4gICAgaWYgKG1hdCkge1xuICAgICAgaWYgKHNlYXJjaFdvcmRMaXN0KHN0dC53b3JkTGlzdCwgbWF0WzFdKSAhPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgIHJldHVybiAndmFyaWFibGUnO1xuICAgICAgfVxuXG4gICAgICAvLyBjb21tZW50c1xuICAgICAgaWYgKG1hdFsxXSA9PT0gJ1xcXFwnKSB7XG4gICAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgICAgcmV0dXJuICdjb21tZW50JztcbiAgICAgIH1cblxuICAgICAgLy8gY29yZSB3b3Jkc1xuICAgICAgaWYgKHNlYXJjaFdvcmRMaXN0KHN0dC5jb3JlV29yZExpc3QsIG1hdFsxXSkgIT09IHVuZGVmaW5lZCkge1xuICAgICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgICAgfVxuICAgICAgaWYgKHNlYXJjaFdvcmRMaXN0KHN0dC5pbW1lZGlhdGVXb3JkTGlzdCwgbWF0WzFdKSAhPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgIHJldHVybiAna2V5d29yZCc7XG4gICAgICB9XG4gICAgICBpZiAobWF0WzFdID09PSAnKCcpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKGZ1bmN0aW9uIChzKSB7XG4gICAgICAgICAgcmV0dXJuIHMgIT09ICcpJztcbiAgICAgICAgfSk7XG4gICAgICAgIHN0cmVhbS5lYXQoJyknKTtcbiAgICAgICAgcmV0dXJuICdjb21tZW50JztcbiAgICAgIH1cblxuICAgICAgLy8gLy8gc3RyaW5nc1xuICAgICAgaWYgKG1hdFsxXSA9PT0gJy4oJykge1xuICAgICAgICBzdHJlYW0uZWF0V2hpbGUoZnVuY3Rpb24gKHMpIHtcbiAgICAgICAgICByZXR1cm4gcyAhPT0gJyknO1xuICAgICAgICB9KTtcbiAgICAgICAgc3RyZWFtLmVhdCgnKScpO1xuICAgICAgICByZXR1cm4gJ3N0cmluZyc7XG4gICAgICB9XG4gICAgICBpZiAobWF0WzFdID09PSAnU1wiJyB8fCBtYXRbMV0gPT09ICcuXCInIHx8IG1hdFsxXSA9PT0gJ0NcIicpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKGZ1bmN0aW9uIChzKSB7XG4gICAgICAgICAgcmV0dXJuIHMgIT09ICdcIic7XG4gICAgICAgIH0pO1xuICAgICAgICBzdHJlYW0uZWF0KCdcIicpO1xuICAgICAgICByZXR1cm4gJ3N0cmluZyc7XG4gICAgICB9XG5cbiAgICAgIC8vIG51bWJlcnNcbiAgICAgIGlmIChtYXRbMV0gLSAweGZmZmZmZmZmZikge1xuICAgICAgICByZXR1cm4gJ251bWJlcic7XG4gICAgICB9XG4gICAgICAvLyBpZiAobWF0WzFdLm1hdGNoKC9eWy0rXT9bMC05XStcXC5bMC05XSovKSkge1xuICAgICAgLy8gICAgIHJldHVybiAnbnVtYmVyJztcbiAgICAgIC8vIH1cblxuICAgICAgcmV0dXJuICdhdG9tJztcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==