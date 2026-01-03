"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7018],{

/***/ 47018
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ttcnCfg: () => (/* binding */ ttcnCfg)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
const parserConfig = {
  name: "ttcn-cfg",
  keywords: words("Yes No LogFile FileMask ConsoleMask AppendFile" + " TimeStampFormat LogEventTypes SourceInfoFormat" + " LogEntityName LogSourceInfo DiskFullAction" + " LogFileNumber LogFileSize MatchingHints Detailed" + " Compact SubCategories Stack Single None Seconds" + " DateTime Time Stop Error Retry Delete TCPPort KillTimer" + " NumHCs UnixSocketsEnabled LocalAddress"),
  fileNCtrlMaskOptions: words("TTCN_EXECUTOR TTCN_ERROR TTCN_WARNING" + " TTCN_PORTEVENT TTCN_TIMEROP TTCN_VERDICTOP" + " TTCN_DEFAULTOP TTCN_TESTCASE TTCN_ACTION" + " TTCN_USER TTCN_FUNCTION TTCN_STATISTICS" + " TTCN_PARALLEL TTCN_MATCHING TTCN_DEBUG" + " EXECUTOR ERROR WARNING PORTEVENT TIMEROP" + " VERDICTOP DEFAULTOP TESTCASE ACTION USER" + " FUNCTION STATISTICS PARALLEL MATCHING DEBUG" + " LOG_ALL LOG_NOTHING ACTION_UNQUALIFIED" + " DEBUG_ENCDEC DEBUG_TESTPORT" + " DEBUG_UNQUALIFIED DEFAULTOP_ACTIVATE" + " DEFAULTOP_DEACTIVATE DEFAULTOP_EXIT" + " DEFAULTOP_UNQUALIFIED ERROR_UNQUALIFIED" + " EXECUTOR_COMPONENT EXECUTOR_CONFIGDATA" + " EXECUTOR_EXTCOMMAND EXECUTOR_LOGOPTIONS" + " EXECUTOR_RUNTIME EXECUTOR_UNQUALIFIED" + " FUNCTION_RND FUNCTION_UNQUALIFIED" + " MATCHING_DONE MATCHING_MCSUCCESS" + " MATCHING_MCUNSUCC MATCHING_MMSUCCESS" + " MATCHING_MMUNSUCC MATCHING_PCSUCCESS" + " MATCHING_PCUNSUCC MATCHING_PMSUCCESS" + " MATCHING_PMUNSUCC MATCHING_PROBLEM" + " MATCHING_TIMEOUT MATCHING_UNQUALIFIED" + " PARALLEL_PORTCONN PARALLEL_PORTMAP" + " PARALLEL_PTC PARALLEL_UNQUALIFIED" + " PORTEVENT_DUALRECV PORTEVENT_DUALSEND" + " PORTEVENT_MCRECV PORTEVENT_MCSEND" + " PORTEVENT_MMRECV PORTEVENT_MMSEND" + " PORTEVENT_MQUEUE PORTEVENT_PCIN" + " PORTEVENT_PCOUT PORTEVENT_PMIN" + " PORTEVENT_PMOUT PORTEVENT_PQUEUE" + " PORTEVENT_STATE PORTEVENT_UNQUALIFIED" + " STATISTICS_UNQUALIFIED STATISTICS_VERDICT" + " TESTCASE_FINISH TESTCASE_START" + " TESTCASE_UNQUALIFIED TIMEROP_GUARD" + " TIMEROP_READ TIMEROP_START TIMEROP_STOP" + " TIMEROP_TIMEOUT TIMEROP_UNQUALIFIED" + " USER_UNQUALIFIED VERDICTOP_FINAL" + " VERDICTOP_GETVERDICT VERDICTOP_SETVERDICT" + " VERDICTOP_UNQUALIFIED WARNING_UNQUALIFIED"),
  externalCommands: words("BeginControlPart EndControlPart BeginTestCase" + " EndTestCase"),
  multiLineStrings: true
};
var keywords = parserConfig.keywords,
  fileNCtrlMaskOptions = parserConfig.fileNCtrlMaskOptions,
  externalCommands = parserConfig.externalCommands,
  multiLineStrings = parserConfig.multiLineStrings,
  indentStatements = parserConfig.indentStatements !== false;
var isOperatorChar = /[\|]/;
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[:=]/.test(ch)) {
    curPunc = ch;
    return "punctuation";
  }
  if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  if (ch == "[") {
    stream.eatWhile(/[\w_\]]/);
    return "number";
  }
  stream.eatWhile(/[\w\$_]/);
  var cur = stream.current();
  if (keywords.propertyIsEnumerable(cur)) return "keyword";
  if (fileNCtrlMaskOptions.propertyIsEnumerable(cur)) return "atom";
  if (externalCommands.propertyIsEnumerable(cur)) return "deleted";
  return "variable";
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        var afterNext = stream.peek();
        //look if the character if the quote is like the B in '10100010'B
        if (afterNext) {
          afterNext = afterNext.toLowerCase();
          if (afterNext == "b" || afterNext == "h" || afterNext == "o") stream.next();
        }
        end = true;
        break;
      }
      escaped = !escaped && next == "\\";
    }
    if (end || !(escaped || multiLineStrings)) state.tokenize = null;
    return "string";
  };
}
function Context(indented, column, type, align, prev) {
  this.indented = indented;
  this.column = column;
  this.type = type;
  this.align = align;
  this.prev = prev;
}
function pushContext(state, col, type) {
  var indent = state.indented;
  if (state.context && state.context.type == "statement") indent = state.context.indented;
  return state.context = new Context(indent, col, type, null, state.context);
}
function popContext(state) {
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

//Interface
const ttcnCfg = {
  name: "ttcn",
  startState: function () {
    return {
      tokenize: null,
      context: new Context(0, 0, "top", false),
      indented: 0,
      startOfLine: true
    };
  },
  token: function (stream, state) {
    var ctx = state.context;
    if (stream.sol()) {
      if (ctx.align == null) ctx.align = false;
      state.indented = stream.indentation();
      state.startOfLine = true;
    }
    if (stream.eatSpace()) return null;
    curPunc = null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment") return style;
    if (ctx.align == null) ctx.align = true;
    if ((curPunc == ";" || curPunc == ":" || curPunc == ",") && ctx.type == "statement") {
      popContext(state);
    } else if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "}") {
      while (ctx.type == "statement") ctx = popContext(state);
      if (ctx.type == "}") ctx = popContext(state);
      while (ctx.type == "statement") ctx = popContext(state);
    } else if (curPunc == ctx.type) popContext(state);else if (indentStatements && ((ctx.type == "}" || ctx.type == "top") && curPunc != ';' || ctx.type == "statement" && curPunc == "newstatement")) pushContext(state, stream.column(), "statement");
    state.startOfLine = false;
    return style;
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzAxOC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdHRjbi1jZmcuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZHMoc3RyKSB7XG4gIHZhciBvYmogPSB7fSxcbiAgICB3b3JkcyA9IHN0ci5zcGxpdChcIiBcIik7XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgd29yZHMubGVuZ3RoOyArK2kpIG9ialt3b3Jkc1tpXV0gPSB0cnVlO1xuICByZXR1cm4gb2JqO1xufVxuY29uc3QgcGFyc2VyQ29uZmlnID0ge1xuICBuYW1lOiBcInR0Y24tY2ZnXCIsXG4gIGtleXdvcmRzOiB3b3JkcyhcIlllcyBObyBMb2dGaWxlIEZpbGVNYXNrIENvbnNvbGVNYXNrIEFwcGVuZEZpbGVcIiArIFwiIFRpbWVTdGFtcEZvcm1hdCBMb2dFdmVudFR5cGVzIFNvdXJjZUluZm9Gb3JtYXRcIiArIFwiIExvZ0VudGl0eU5hbWUgTG9nU291cmNlSW5mbyBEaXNrRnVsbEFjdGlvblwiICsgXCIgTG9nRmlsZU51bWJlciBMb2dGaWxlU2l6ZSBNYXRjaGluZ0hpbnRzIERldGFpbGVkXCIgKyBcIiBDb21wYWN0IFN1YkNhdGVnb3JpZXMgU3RhY2sgU2luZ2xlIE5vbmUgU2Vjb25kc1wiICsgXCIgRGF0ZVRpbWUgVGltZSBTdG9wIEVycm9yIFJldHJ5IERlbGV0ZSBUQ1BQb3J0IEtpbGxUaW1lclwiICsgXCIgTnVtSENzIFVuaXhTb2NrZXRzRW5hYmxlZCBMb2NhbEFkZHJlc3NcIiksXG4gIGZpbGVOQ3RybE1hc2tPcHRpb25zOiB3b3JkcyhcIlRUQ05fRVhFQ1VUT1IgVFRDTl9FUlJPUiBUVENOX1dBUk5JTkdcIiArIFwiIFRUQ05fUE9SVEVWRU5UIFRUQ05fVElNRVJPUCBUVENOX1ZFUkRJQ1RPUFwiICsgXCIgVFRDTl9ERUZBVUxUT1AgVFRDTl9URVNUQ0FTRSBUVENOX0FDVElPTlwiICsgXCIgVFRDTl9VU0VSIFRUQ05fRlVOQ1RJT04gVFRDTl9TVEFUSVNUSUNTXCIgKyBcIiBUVENOX1BBUkFMTEVMIFRUQ05fTUFUQ0hJTkcgVFRDTl9ERUJVR1wiICsgXCIgRVhFQ1VUT1IgRVJST1IgV0FSTklORyBQT1JURVZFTlQgVElNRVJPUFwiICsgXCIgVkVSRElDVE9QIERFRkFVTFRPUCBURVNUQ0FTRSBBQ1RJT04gVVNFUlwiICsgXCIgRlVOQ1RJT04gU1RBVElTVElDUyBQQVJBTExFTCBNQVRDSElORyBERUJVR1wiICsgXCIgTE9HX0FMTCBMT0dfTk9USElORyBBQ1RJT05fVU5RVUFMSUZJRURcIiArIFwiIERFQlVHX0VOQ0RFQyBERUJVR19URVNUUE9SVFwiICsgXCIgREVCVUdfVU5RVUFMSUZJRUQgREVGQVVMVE9QX0FDVElWQVRFXCIgKyBcIiBERUZBVUxUT1BfREVBQ1RJVkFURSBERUZBVUxUT1BfRVhJVFwiICsgXCIgREVGQVVMVE9QX1VOUVVBTElGSUVEIEVSUk9SX1VOUVVBTElGSUVEXCIgKyBcIiBFWEVDVVRPUl9DT01QT05FTlQgRVhFQ1VUT1JfQ09ORklHREFUQVwiICsgXCIgRVhFQ1VUT1JfRVhUQ09NTUFORCBFWEVDVVRPUl9MT0dPUFRJT05TXCIgKyBcIiBFWEVDVVRPUl9SVU5USU1FIEVYRUNVVE9SX1VOUVVBTElGSUVEXCIgKyBcIiBGVU5DVElPTl9STkQgRlVOQ1RJT05fVU5RVUFMSUZJRURcIiArIFwiIE1BVENISU5HX0RPTkUgTUFUQ0hJTkdfTUNTVUNDRVNTXCIgKyBcIiBNQVRDSElOR19NQ1VOU1VDQyBNQVRDSElOR19NTVNVQ0NFU1NcIiArIFwiIE1BVENISU5HX01NVU5TVUNDIE1BVENISU5HX1BDU1VDQ0VTU1wiICsgXCIgTUFUQ0hJTkdfUENVTlNVQ0MgTUFUQ0hJTkdfUE1TVUNDRVNTXCIgKyBcIiBNQVRDSElOR19QTVVOU1VDQyBNQVRDSElOR19QUk9CTEVNXCIgKyBcIiBNQVRDSElOR19USU1FT1VUIE1BVENISU5HX1VOUVVBTElGSUVEXCIgKyBcIiBQQVJBTExFTF9QT1JUQ09OTiBQQVJBTExFTF9QT1JUTUFQXCIgKyBcIiBQQVJBTExFTF9QVEMgUEFSQUxMRUxfVU5RVUFMSUZJRURcIiArIFwiIFBPUlRFVkVOVF9EVUFMUkVDViBQT1JURVZFTlRfRFVBTFNFTkRcIiArIFwiIFBPUlRFVkVOVF9NQ1JFQ1YgUE9SVEVWRU5UX01DU0VORFwiICsgXCIgUE9SVEVWRU5UX01NUkVDViBQT1JURVZFTlRfTU1TRU5EXCIgKyBcIiBQT1JURVZFTlRfTVFVRVVFIFBPUlRFVkVOVF9QQ0lOXCIgKyBcIiBQT1JURVZFTlRfUENPVVQgUE9SVEVWRU5UX1BNSU5cIiArIFwiIFBPUlRFVkVOVF9QTU9VVCBQT1JURVZFTlRfUFFVRVVFXCIgKyBcIiBQT1JURVZFTlRfU1RBVEUgUE9SVEVWRU5UX1VOUVVBTElGSUVEXCIgKyBcIiBTVEFUSVNUSUNTX1VOUVVBTElGSUVEIFNUQVRJU1RJQ1NfVkVSRElDVFwiICsgXCIgVEVTVENBU0VfRklOSVNIIFRFU1RDQVNFX1NUQVJUXCIgKyBcIiBURVNUQ0FTRV9VTlFVQUxJRklFRCBUSU1FUk9QX0dVQVJEXCIgKyBcIiBUSU1FUk9QX1JFQUQgVElNRVJPUF9TVEFSVCBUSU1FUk9QX1NUT1BcIiArIFwiIFRJTUVST1BfVElNRU9VVCBUSU1FUk9QX1VOUVVBTElGSUVEXCIgKyBcIiBVU0VSX1VOUVVBTElGSUVEIFZFUkRJQ1RPUF9GSU5BTFwiICsgXCIgVkVSRElDVE9QX0dFVFZFUkRJQ1QgVkVSRElDVE9QX1NFVFZFUkRJQ1RcIiArIFwiIFZFUkRJQ1RPUF9VTlFVQUxJRklFRCBXQVJOSU5HX1VOUVVBTElGSUVEXCIpLFxuICBleHRlcm5hbENvbW1hbmRzOiB3b3JkcyhcIkJlZ2luQ29udHJvbFBhcnQgRW5kQ29udHJvbFBhcnQgQmVnaW5UZXN0Q2FzZVwiICsgXCIgRW5kVGVzdENhc2VcIiksXG4gIG11bHRpTGluZVN0cmluZ3M6IHRydWVcbn07XG52YXIga2V5d29yZHMgPSBwYXJzZXJDb25maWcua2V5d29yZHMsXG4gIGZpbGVOQ3RybE1hc2tPcHRpb25zID0gcGFyc2VyQ29uZmlnLmZpbGVOQ3RybE1hc2tPcHRpb25zLFxuICBleHRlcm5hbENvbW1hbmRzID0gcGFyc2VyQ29uZmlnLmV4dGVybmFsQ29tbWFuZHMsXG4gIG11bHRpTGluZVN0cmluZ3MgPSBwYXJzZXJDb25maWcubXVsdGlMaW5lU3RyaW5ncyxcbiAgaW5kZW50U3RhdGVtZW50cyA9IHBhcnNlckNvbmZpZy5pbmRlbnRTdGF0ZW1lbnRzICE9PSBmYWxzZTtcbnZhciBpc09wZXJhdG9yQ2hhciA9IC9bXFx8XS87XG52YXIgY3VyUHVuYztcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSAnXCInIHx8IGNoID09IFwiJ1wiKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmICgvWzo9XS8udGVzdChjaCkpIHtcbiAgICBjdXJQdW5jID0gY2g7XG4gICAgcmV0dXJuIFwicHVuY3R1YXRpb25cIjtcbiAgfVxuICBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG4gIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLl0vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuICBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNPcGVyYXRvckNoYXIpO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cbiAgaWYgKGNoID09IFwiW1wiKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3X1xcXV0vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImtleXdvcmRcIjtcbiAgaWYgKGZpbGVOQ3RybE1hc2tPcHRpb25zLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImF0b21cIjtcbiAgaWYgKGV4dGVybmFsQ29tbWFuZHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiZGVsZXRlZFwiO1xuICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQsXG4gICAgICBlbmQgPSBmYWxzZTtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkge1xuICAgICAgICB2YXIgYWZ0ZXJOZXh0ID0gc3RyZWFtLnBlZWsoKTtcbiAgICAgICAgLy9sb29rIGlmIHRoZSBjaGFyYWN0ZXIgaWYgdGhlIHF1b3RlIGlzIGxpa2UgdGhlIEIgaW4gJzEwMTAwMDEwJ0JcbiAgICAgICAgaWYgKGFmdGVyTmV4dCkge1xuICAgICAgICAgIGFmdGVyTmV4dCA9IGFmdGVyTmV4dC50b0xvd2VyQ2FzZSgpO1xuICAgICAgICAgIGlmIChhZnRlck5leHQgPT0gXCJiXCIgfHwgYWZ0ZXJOZXh0ID09IFwiaFwiIHx8IGFmdGVyTmV4dCA9PSBcIm9cIikgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgfVxuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoZW5kIHx8ICEoZXNjYXBlZCB8fCBtdWx0aUxpbmVTdHJpbmdzKSkgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gQ29udGV4dChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBhbGlnbiwgcHJldikge1xuICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMucHJldiA9IHByZXY7XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlKSB7XG4gIHZhciBpbmRlbnQgPSBzdGF0ZS5pbmRlbnRlZDtcbiAgaWYgKHN0YXRlLmNvbnRleHQgJiYgc3RhdGUuY29udGV4dC50eXBlID09IFwic3RhdGVtZW50XCIpIGluZGVudCA9IHN0YXRlLmNvbnRleHQuaW5kZW50ZWQ7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoaW5kZW50LCBjb2wsIHR5cGUsIG51bGwsIHN0YXRlLmNvbnRleHQpO1xufVxuZnVuY3Rpb24gcG9wQ29udGV4dChzdGF0ZSkge1xuICB2YXIgdCA9IHN0YXRlLmNvbnRleHQudHlwZTtcbiAgaWYgKHQgPT0gXCIpXCIgfHwgdCA9PSBcIl1cIiB8fCB0ID09IFwifVwiKSBzdGF0ZS5pbmRlbnRlZCA9IHN0YXRlLmNvbnRleHQuaW5kZW50ZWQ7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gc3RhdGUuY29udGV4dC5wcmV2O1xufVxuXG4vL0ludGVyZmFjZVxuZXhwb3J0IGNvbnN0IHR0Y25DZmcgPSB7XG4gIG5hbWU6IFwidHRjblwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBudWxsLFxuICAgICAgY29udGV4dDogbmV3IENvbnRleHQoMCwgMCwgXCJ0b3BcIiwgZmFsc2UpLFxuICAgICAgaW5kZW50ZWQ6IDAsXG4gICAgICBzdGFydE9mTGluZTogdHJ1ZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0O1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gZmFsc2U7XG4gICAgICBzdGF0ZS5pbmRlbnRlZCA9IHN0cmVhbS5pbmRlbnRhdGlvbigpO1xuICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIGN1clB1bmMgPSBudWxsO1xuICAgIHZhciBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PSBcImNvbW1lbnRcIikgcmV0dXJuIHN0eWxlO1xuICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gdHJ1ZTtcbiAgICBpZiAoKGN1clB1bmMgPT0gXCI7XCIgfHwgY3VyUHVuYyA9PSBcIjpcIiB8fCBjdXJQdW5jID09IFwiLFwiKSAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSB7XG4gICAgICBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICB9IGVsc2UgaWYgKGN1clB1bmMgPT0gXCJ7XCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwifVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwiW1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIl1cIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIihcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCIpXCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJ9XCIpIHtcbiAgICAgIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgIGlmIChjdHgudHlwZSA9PSBcIn1cIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICB3aGlsZSAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChjdXJQdW5jID09IGN0eC50eXBlKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmIChpbmRlbnRTdGF0ZW1lbnRzICYmICgoY3R4LnR5cGUgPT0gXCJ9XCIgfHwgY3R4LnR5cGUgPT0gXCJ0b3BcIikgJiYgY3VyUHVuYyAhPSAnOycgfHwgY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIiAmJiBjdXJQdW5jID09IFwibmV3c3RhdGVtZW50XCIpKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcInN0YXRlbWVudFwiKTtcbiAgICBzdGF0ZS5zdGFydE9mTGluZSA9IGZhbHNlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgaW5kZW50T25JbnB1dDogL15cXHMqW3t9XSQvLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=