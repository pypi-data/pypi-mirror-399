"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9095],{

/***/ 59095
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ntriples: () => (/* binding */ ntriples)
/* harmony export */ });
var Location = {
  PRE_SUBJECT: 0,
  WRITING_SUB_URI: 1,
  WRITING_BNODE_URI: 2,
  PRE_PRED: 3,
  WRITING_PRED_URI: 4,
  PRE_OBJ: 5,
  WRITING_OBJ_URI: 6,
  WRITING_OBJ_BNODE: 7,
  WRITING_OBJ_LITERAL: 8,
  WRITING_LIT_LANG: 9,
  WRITING_LIT_TYPE: 10,
  POST_OBJ: 11,
  ERROR: 12
};
function transitState(currState, c) {
  var currLocation = currState.location;
  var ret;

  // Opening.
  if (currLocation == Location.PRE_SUBJECT && c == '<') ret = Location.WRITING_SUB_URI;else if (currLocation == Location.PRE_SUBJECT && c == '_') ret = Location.WRITING_BNODE_URI;else if (currLocation == Location.PRE_PRED && c == '<') ret = Location.WRITING_PRED_URI;else if (currLocation == Location.PRE_OBJ && c == '<') ret = Location.WRITING_OBJ_URI;else if (currLocation == Location.PRE_OBJ && c == '_') ret = Location.WRITING_OBJ_BNODE;else if (currLocation == Location.PRE_OBJ && c == '"') ret = Location.WRITING_OBJ_LITERAL;

  // Closing.
  else if (currLocation == Location.WRITING_SUB_URI && c == '>') ret = Location.PRE_PRED;else if (currLocation == Location.WRITING_BNODE_URI && c == ' ') ret = Location.PRE_PRED;else if (currLocation == Location.WRITING_PRED_URI && c == '>') ret = Location.PRE_OBJ;else if (currLocation == Location.WRITING_OBJ_URI && c == '>') ret = Location.POST_OBJ;else if (currLocation == Location.WRITING_OBJ_BNODE && c == ' ') ret = Location.POST_OBJ;else if (currLocation == Location.WRITING_OBJ_LITERAL && c == '"') ret = Location.POST_OBJ;else if (currLocation == Location.WRITING_LIT_LANG && c == ' ') ret = Location.POST_OBJ;else if (currLocation == Location.WRITING_LIT_TYPE && c == '>') ret = Location.POST_OBJ;

  // Closing typed and language literal.
  else if (currLocation == Location.WRITING_OBJ_LITERAL && c == '@') ret = Location.WRITING_LIT_LANG;else if (currLocation == Location.WRITING_OBJ_LITERAL && c == '^') ret = Location.WRITING_LIT_TYPE;

  // Spaces.
  else if (c == ' ' && (currLocation == Location.PRE_SUBJECT || currLocation == Location.PRE_PRED || currLocation == Location.PRE_OBJ || currLocation == Location.POST_OBJ)) ret = currLocation;

  // Reset.
  else if (currLocation == Location.POST_OBJ && c == '.') ret = Location.PRE_SUBJECT;

  // Error
  else ret = Location.ERROR;
  currState.location = ret;
}
const ntriples = {
  name: "ntriples",
  startState: function () {
    return {
      location: Location.PRE_SUBJECT,
      uris: [],
      anchors: [],
      bnodes: [],
      langs: [],
      types: []
    };
  },
  token: function (stream, state) {
    var ch = stream.next();
    if (ch == '<') {
      transitState(state, ch);
      var parsedURI = '';
      stream.eatWhile(function (c) {
        if (c != '#' && c != '>') {
          parsedURI += c;
          return true;
        }
        return false;
      });
      state.uris.push(parsedURI);
      if (stream.match('#', false)) return 'variable';
      stream.next();
      transitState(state, '>');
      return 'variable';
    }
    if (ch == '#') {
      var parsedAnchor = '';
      stream.eatWhile(function (c) {
        if (c != '>' && c != ' ') {
          parsedAnchor += c;
          return true;
        }
        return false;
      });
      state.anchors.push(parsedAnchor);
      return 'url';
    }
    if (ch == '>') {
      transitState(state, '>');
      return 'variable';
    }
    if (ch == '_') {
      transitState(state, ch);
      var parsedBNode = '';
      stream.eatWhile(function (c) {
        if (c != ' ') {
          parsedBNode += c;
          return true;
        }
        return false;
      });
      state.bnodes.push(parsedBNode);
      stream.next();
      transitState(state, ' ');
      return 'builtin';
    }
    if (ch == '"') {
      transitState(state, ch);
      stream.eatWhile(function (c) {
        return c != '"';
      });
      stream.next();
      if (stream.peek() != '@' && stream.peek() != '^') {
        transitState(state, '"');
      }
      return 'string';
    }
    if (ch == '@') {
      transitState(state, '@');
      var parsedLang = '';
      stream.eatWhile(function (c) {
        if (c != ' ') {
          parsedLang += c;
          return true;
        }
        return false;
      });
      state.langs.push(parsedLang);
      stream.next();
      transitState(state, ' ');
      return 'string.special';
    }
    if (ch == '^') {
      stream.next();
      transitState(state, '^');
      var parsedType = '';
      stream.eatWhile(function (c) {
        if (c != '>') {
          parsedType += c;
          return true;
        }
        return false;
      });
      state.types.push(parsedType);
      stream.next();
      transitState(state, '>');
      return 'variable';
    }
    if (ch == ' ') {
      transitState(state, ch);
    }
    if (ch == '.') {
      transitState(state, ch);
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTA5NS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9udHJpcGxlcy5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgTG9jYXRpb24gPSB7XG4gIFBSRV9TVUJKRUNUOiAwLFxuICBXUklUSU5HX1NVQl9VUkk6IDEsXG4gIFdSSVRJTkdfQk5PREVfVVJJOiAyLFxuICBQUkVfUFJFRDogMyxcbiAgV1JJVElOR19QUkVEX1VSSTogNCxcbiAgUFJFX09CSjogNSxcbiAgV1JJVElOR19PQkpfVVJJOiA2LFxuICBXUklUSU5HX09CSl9CTk9ERTogNyxcbiAgV1JJVElOR19PQkpfTElURVJBTDogOCxcbiAgV1JJVElOR19MSVRfTEFORzogOSxcbiAgV1JJVElOR19MSVRfVFlQRTogMTAsXG4gIFBPU1RfT0JKOiAxMSxcbiAgRVJST1I6IDEyXG59O1xuZnVuY3Rpb24gdHJhbnNpdFN0YXRlKGN1cnJTdGF0ZSwgYykge1xuICB2YXIgY3VyckxvY2F0aW9uID0gY3VyclN0YXRlLmxvY2F0aW9uO1xuICB2YXIgcmV0O1xuXG4gIC8vIE9wZW5pbmcuXG4gIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uUFJFX1NVQkpFQ1QgJiYgYyA9PSAnPCcpIHJldCA9IExvY2F0aW9uLldSSVRJTkdfU1VCX1VSSTtlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uUFJFX1NVQkpFQ1QgJiYgYyA9PSAnXycpIHJldCA9IExvY2F0aW9uLldSSVRJTkdfQk5PREVfVVJJO2Vsc2UgaWYgKGN1cnJMb2NhdGlvbiA9PSBMb2NhdGlvbi5QUkVfUFJFRCAmJiBjID09ICc8JykgcmV0ID0gTG9jYXRpb24uV1JJVElOR19QUkVEX1VSSTtlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uUFJFX09CSiAmJiBjID09ICc8JykgcmV0ID0gTG9jYXRpb24uV1JJVElOR19PQkpfVVJJO2Vsc2UgaWYgKGN1cnJMb2NhdGlvbiA9PSBMb2NhdGlvbi5QUkVfT0JKICYmIGMgPT0gJ18nKSByZXQgPSBMb2NhdGlvbi5XUklUSU5HX09CSl9CTk9ERTtlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uUFJFX09CSiAmJiBjID09ICdcIicpIHJldCA9IExvY2F0aW9uLldSSVRJTkdfT0JKX0xJVEVSQUw7XG5cbiAgLy8gQ2xvc2luZy5cbiAgZWxzZSBpZiAoY3VyckxvY2F0aW9uID09IExvY2F0aW9uLldSSVRJTkdfU1VCX1VSSSAmJiBjID09ICc+JykgcmV0ID0gTG9jYXRpb24uUFJFX1BSRUQ7ZWxzZSBpZiAoY3VyckxvY2F0aW9uID09IExvY2F0aW9uLldSSVRJTkdfQk5PREVfVVJJICYmIGMgPT0gJyAnKSByZXQgPSBMb2NhdGlvbi5QUkVfUFJFRDtlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uV1JJVElOR19QUkVEX1VSSSAmJiBjID09ICc+JykgcmV0ID0gTG9jYXRpb24uUFJFX09CSjtlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uV1JJVElOR19PQkpfVVJJICYmIGMgPT0gJz4nKSByZXQgPSBMb2NhdGlvbi5QT1NUX09CSjtlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uV1JJVElOR19PQkpfQk5PREUgJiYgYyA9PSAnICcpIHJldCA9IExvY2F0aW9uLlBPU1RfT0JKO2Vsc2UgaWYgKGN1cnJMb2NhdGlvbiA9PSBMb2NhdGlvbi5XUklUSU5HX09CSl9MSVRFUkFMICYmIGMgPT0gJ1wiJykgcmV0ID0gTG9jYXRpb24uUE9TVF9PQko7ZWxzZSBpZiAoY3VyckxvY2F0aW9uID09IExvY2F0aW9uLldSSVRJTkdfTElUX0xBTkcgJiYgYyA9PSAnICcpIHJldCA9IExvY2F0aW9uLlBPU1RfT0JKO2Vsc2UgaWYgKGN1cnJMb2NhdGlvbiA9PSBMb2NhdGlvbi5XUklUSU5HX0xJVF9UWVBFICYmIGMgPT0gJz4nKSByZXQgPSBMb2NhdGlvbi5QT1NUX09CSjtcblxuICAvLyBDbG9zaW5nIHR5cGVkIGFuZCBsYW5ndWFnZSBsaXRlcmFsLlxuICBlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uV1JJVElOR19PQkpfTElURVJBTCAmJiBjID09ICdAJykgcmV0ID0gTG9jYXRpb24uV1JJVElOR19MSVRfTEFORztlbHNlIGlmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uV1JJVElOR19PQkpfTElURVJBTCAmJiBjID09ICdeJykgcmV0ID0gTG9jYXRpb24uV1JJVElOR19MSVRfVFlQRTtcblxuICAvLyBTcGFjZXMuXG4gIGVsc2UgaWYgKGMgPT0gJyAnICYmIChjdXJyTG9jYXRpb24gPT0gTG9jYXRpb24uUFJFX1NVQkpFQ1QgfHwgY3VyckxvY2F0aW9uID09IExvY2F0aW9uLlBSRV9QUkVEIHx8IGN1cnJMb2NhdGlvbiA9PSBMb2NhdGlvbi5QUkVfT0JKIHx8IGN1cnJMb2NhdGlvbiA9PSBMb2NhdGlvbi5QT1NUX09CSikpIHJldCA9IGN1cnJMb2NhdGlvbjtcblxuICAvLyBSZXNldC5cbiAgZWxzZSBpZiAoY3VyckxvY2F0aW9uID09IExvY2F0aW9uLlBPU1RfT0JKICYmIGMgPT0gJy4nKSByZXQgPSBMb2NhdGlvbi5QUkVfU1VCSkVDVDtcblxuICAvLyBFcnJvclxuICBlbHNlIHJldCA9IExvY2F0aW9uLkVSUk9SO1xuICBjdXJyU3RhdGUubG9jYXRpb24gPSByZXQ7XG59XG5leHBvcnQgY29uc3QgbnRyaXBsZXMgPSB7XG4gIG5hbWU6IFwibnRyaXBsZXNcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICBsb2NhdGlvbjogTG9jYXRpb24uUFJFX1NVQkpFQ1QsXG4gICAgICB1cmlzOiBbXSxcbiAgICAgIGFuY2hvcnM6IFtdLFxuICAgICAgYm5vZGVzOiBbXSxcbiAgICAgIGxhbmdzOiBbXSxcbiAgICAgIHR5cGVzOiBbXVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgaWYgKGNoID09ICc8Jykge1xuICAgICAgdHJhbnNpdFN0YXRlKHN0YXRlLCBjaCk7XG4gICAgICB2YXIgcGFyc2VkVVJJID0gJyc7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoZnVuY3Rpb24gKGMpIHtcbiAgICAgICAgaWYgKGMgIT0gJyMnICYmIGMgIT0gJz4nKSB7XG4gICAgICAgICAgcGFyc2VkVVJJICs9IGM7XG4gICAgICAgICAgcmV0dXJuIHRydWU7XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIGZhbHNlO1xuICAgICAgfSk7XG4gICAgICBzdGF0ZS51cmlzLnB1c2gocGFyc2VkVVJJKTtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goJyMnLCBmYWxzZSkpIHJldHVybiAndmFyaWFibGUnO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHRyYW5zaXRTdGF0ZShzdGF0ZSwgJz4nKTtcbiAgICAgIHJldHVybiAndmFyaWFibGUnO1xuICAgIH1cbiAgICBpZiAoY2ggPT0gJyMnKSB7XG4gICAgICB2YXIgcGFyc2VkQW5jaG9yID0gJyc7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoZnVuY3Rpb24gKGMpIHtcbiAgICAgICAgaWYgKGMgIT0gJz4nICYmIGMgIT0gJyAnKSB7XG4gICAgICAgICAgcGFyc2VkQW5jaG9yICs9IGM7XG4gICAgICAgICAgcmV0dXJuIHRydWU7XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIGZhbHNlO1xuICAgICAgfSk7XG4gICAgICBzdGF0ZS5hbmNob3JzLnB1c2gocGFyc2VkQW5jaG9yKTtcbiAgICAgIHJldHVybiAndXJsJztcbiAgICB9XG4gICAgaWYgKGNoID09ICc+Jykge1xuICAgICAgdHJhbnNpdFN0YXRlKHN0YXRlLCAnPicpO1xuICAgICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gICAgfVxuICAgIGlmIChjaCA9PSAnXycpIHtcbiAgICAgIHRyYW5zaXRTdGF0ZShzdGF0ZSwgY2gpO1xuICAgICAgdmFyIHBhcnNlZEJOb2RlID0gJyc7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoZnVuY3Rpb24gKGMpIHtcbiAgICAgICAgaWYgKGMgIT0gJyAnKSB7XG4gICAgICAgICAgcGFyc2VkQk5vZGUgKz0gYztcbiAgICAgICAgICByZXR1cm4gdHJ1ZTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gZmFsc2U7XG4gICAgICB9KTtcbiAgICAgIHN0YXRlLmJub2Rlcy5wdXNoKHBhcnNlZEJOb2RlKTtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICB0cmFuc2l0U3RhdGUoc3RhdGUsICcgJyk7XG4gICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgIH1cbiAgICBpZiAoY2ggPT0gJ1wiJykge1xuICAgICAgdHJhbnNpdFN0YXRlKHN0YXRlLCBjaCk7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoZnVuY3Rpb24gKGMpIHtcbiAgICAgICAgcmV0dXJuIGMgIT0gJ1wiJztcbiAgICAgIH0pO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIGlmIChzdHJlYW0ucGVlaygpICE9ICdAJyAmJiBzdHJlYW0ucGVlaygpICE9ICdeJykge1xuICAgICAgICB0cmFuc2l0U3RhdGUoc3RhdGUsICdcIicpO1xuICAgICAgfVxuICAgICAgcmV0dXJuICdzdHJpbmcnO1xuICAgIH1cbiAgICBpZiAoY2ggPT0gJ0AnKSB7XG4gICAgICB0cmFuc2l0U3RhdGUoc3RhdGUsICdAJyk7XG4gICAgICB2YXIgcGFyc2VkTGFuZyA9ICcnO1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKGZ1bmN0aW9uIChjKSB7XG4gICAgICAgIGlmIChjICE9ICcgJykge1xuICAgICAgICAgIHBhcnNlZExhbmcgKz0gYztcbiAgICAgICAgICByZXR1cm4gdHJ1ZTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gZmFsc2U7XG4gICAgICB9KTtcbiAgICAgIHN0YXRlLmxhbmdzLnB1c2gocGFyc2VkTGFuZyk7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgdHJhbnNpdFN0YXRlKHN0YXRlLCAnICcpO1xuICAgICAgcmV0dXJuICdzdHJpbmcuc3BlY2lhbCc7XG4gICAgfVxuICAgIGlmIChjaCA9PSAnXicpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICB0cmFuc2l0U3RhdGUoc3RhdGUsICdeJyk7XG4gICAgICB2YXIgcGFyc2VkVHlwZSA9ICcnO1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKGZ1bmN0aW9uIChjKSB7XG4gICAgICAgIGlmIChjICE9ICc+Jykge1xuICAgICAgICAgIHBhcnNlZFR5cGUgKz0gYztcbiAgICAgICAgICByZXR1cm4gdHJ1ZTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gZmFsc2U7XG4gICAgICB9KTtcbiAgICAgIHN0YXRlLnR5cGVzLnB1c2gocGFyc2VkVHlwZSk7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgdHJhbnNpdFN0YXRlKHN0YXRlLCAnPicpO1xuICAgICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gICAgfVxuICAgIGlmIChjaCA9PSAnICcpIHtcbiAgICAgIHRyYW5zaXRTdGF0ZShzdGF0ZSwgY2gpO1xuICAgIH1cbiAgICBpZiAoY2ggPT0gJy4nKSB7XG4gICAgICB0cmFuc2l0U3RhdGUoc3RhdGUsIGNoKTtcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==