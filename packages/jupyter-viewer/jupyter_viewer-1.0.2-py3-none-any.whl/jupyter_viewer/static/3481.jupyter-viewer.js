"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3481],{

/***/ 93481
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   asn1: () => (/* binding */ asn1)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
const defaults = {
  keywords: words("DEFINITIONS OBJECTS IF DERIVED INFORMATION ACTION" + " REPLY ANY NAMED CHARACTERIZED BEHAVIOUR REGISTERED" + " WITH AS IDENTIFIED CONSTRAINED BY PRESENT BEGIN" + " IMPORTS FROM UNITS SYNTAX MIN-ACCESS MAX-ACCESS" + " MINACCESS MAXACCESS REVISION STATUS DESCRIPTION" + " SEQUENCE SET COMPONENTS OF CHOICE DistinguishedName" + " ENUMERATED SIZE MODULE END INDEX AUGMENTS EXTENSIBILITY" + " IMPLIED EXPORTS"),
  cmipVerbs: words("ACTIONS ADD GET NOTIFICATIONS REPLACE REMOVE"),
  compareTypes: words("OPTIONAL DEFAULT MANAGED MODULE-TYPE MODULE_IDENTITY" + " MODULE-COMPLIANCE OBJECT-TYPE OBJECT-IDENTITY" + " OBJECT-COMPLIANCE MODE CONFIRMED CONDITIONAL" + " SUBORDINATE SUPERIOR CLASS TRUE FALSE NULL" + " TEXTUAL-CONVENTION"),
  status: words("current deprecated mandatory obsolete"),
  tags: words("APPLICATION AUTOMATIC EXPLICIT IMPLICIT PRIVATE TAGS" + " UNIVERSAL"),
  storage: words("BOOLEAN INTEGER OBJECT IDENTIFIER BIT OCTET STRING" + " UTCTime InterfaceIndex IANAifType CMIP-Attribute" + " REAL PACKAGE PACKAGES IpAddress PhysAddress" + " NetworkAddress BITS BMPString TimeStamp TimeTicks" + " TruthValue RowStatus DisplayString GeneralString" + " GraphicString IA5String NumericString" + " PrintableString SnmpAdminString TeletexString" + " UTF8String VideotexString VisibleString StringStore" + " ISO646String T61String UniversalString Unsigned32" + " Integer32 Gauge Gauge32 Counter Counter32 Counter64"),
  modifier: words("ATTRIBUTE ATTRIBUTES MANDATORY-GROUP MANDATORY-GROUPS" + " GROUP GROUPS ELEMENTS EQUALITY ORDERING SUBSTRINGS" + " DEFINED"),
  accessTypes: words("not-accessible accessible-for-notify read-only" + " read-create read-write"),
  multiLineStrings: true
};
function asn1(parserConfig) {
  var keywords = parserConfig.keywords || defaults.keywords,
    cmipVerbs = parserConfig.cmipVerbs || defaults.cmipVerbs,
    compareTypes = parserConfig.compareTypes || defaults.compareTypes,
    status = parserConfig.status || defaults.status,
    tags = parserConfig.tags || defaults.tags,
    storage = parserConfig.storage || defaults.storage,
    modifier = parserConfig.modifier || defaults.modifier,
    accessTypes = parserConfig.accessTypes || defaults.accessTypes,
    multiLineStrings = parserConfig.multiLineStrings || defaults.multiLineStrings,
    indentStatements = parserConfig.indentStatements !== false;
  var isOperatorChar = /[\|\^]/;
  var curPunc;
  function tokenBase(stream, state) {
    var ch = stream.next();
    if (ch == '"' || ch == "'") {
      state.tokenize = tokenString(ch);
      return state.tokenize(stream, state);
    }
    if (/[\[\]\(\){}:=,;]/.test(ch)) {
      curPunc = ch;
      return "punctuation";
    }
    if (ch == "-") {
      if (stream.eat("-")) {
        stream.skipToEnd();
        return "comment";
      }
    }
    if (/\d/.test(ch)) {
      stream.eatWhile(/[\w\.]/);
      return "number";
    }
    if (isOperatorChar.test(ch)) {
      stream.eatWhile(isOperatorChar);
      return "operator";
    }
    stream.eatWhile(/[\w\-]/);
    var cur = stream.current();
    if (keywords.propertyIsEnumerable(cur)) return "keyword";
    if (cmipVerbs.propertyIsEnumerable(cur)) return "variableName";
    if (compareTypes.propertyIsEnumerable(cur)) return "atom";
    if (status.propertyIsEnumerable(cur)) return "comment";
    if (tags.propertyIsEnumerable(cur)) return "typeName";
    if (storage.propertyIsEnumerable(cur)) return "modifier";
    if (modifier.propertyIsEnumerable(cur)) return "modifier";
    if (accessTypes.propertyIsEnumerable(cur)) return "modifier";
    return "variableName";
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
  return {
    name: "asn1",
    startState: function () {
      return {
        tokenize: null,
        context: new Context(-2, 0, "top", false),
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
        line: "--"
      }
    }
  };
}
;

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzQ4MS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvYXNuMS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiIFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBvYmo7XG59XG5jb25zdCBkZWZhdWx0cyA9IHtcbiAga2V5d29yZHM6IHdvcmRzKFwiREVGSU5JVElPTlMgT0JKRUNUUyBJRiBERVJJVkVEIElORk9STUFUSU9OIEFDVElPTlwiICsgXCIgUkVQTFkgQU5ZIE5BTUVEIENIQVJBQ1RFUklaRUQgQkVIQVZJT1VSIFJFR0lTVEVSRURcIiArIFwiIFdJVEggQVMgSURFTlRJRklFRCBDT05TVFJBSU5FRCBCWSBQUkVTRU5UIEJFR0lOXCIgKyBcIiBJTVBPUlRTIEZST00gVU5JVFMgU1lOVEFYIE1JTi1BQ0NFU1MgTUFYLUFDQ0VTU1wiICsgXCIgTUlOQUNDRVNTIE1BWEFDQ0VTUyBSRVZJU0lPTiBTVEFUVVMgREVTQ1JJUFRJT05cIiArIFwiIFNFUVVFTkNFIFNFVCBDT01QT05FTlRTIE9GIENIT0lDRSBEaXN0aW5ndWlzaGVkTmFtZVwiICsgXCIgRU5VTUVSQVRFRCBTSVpFIE1PRFVMRSBFTkQgSU5ERVggQVVHTUVOVFMgRVhURU5TSUJJTElUWVwiICsgXCIgSU1QTElFRCBFWFBPUlRTXCIpLFxuICBjbWlwVmVyYnM6IHdvcmRzKFwiQUNUSU9OUyBBREQgR0VUIE5PVElGSUNBVElPTlMgUkVQTEFDRSBSRU1PVkVcIiksXG4gIGNvbXBhcmVUeXBlczogd29yZHMoXCJPUFRJT05BTCBERUZBVUxUIE1BTkFHRUQgTU9EVUxFLVRZUEUgTU9EVUxFX0lERU5USVRZXCIgKyBcIiBNT0RVTEUtQ09NUExJQU5DRSBPQkpFQ1QtVFlQRSBPQkpFQ1QtSURFTlRJVFlcIiArIFwiIE9CSkVDVC1DT01QTElBTkNFIE1PREUgQ09ORklSTUVEIENPTkRJVElPTkFMXCIgKyBcIiBTVUJPUkRJTkFURSBTVVBFUklPUiBDTEFTUyBUUlVFIEZBTFNFIE5VTExcIiArIFwiIFRFWFRVQUwtQ09OVkVOVElPTlwiKSxcbiAgc3RhdHVzOiB3b3JkcyhcImN1cnJlbnQgZGVwcmVjYXRlZCBtYW5kYXRvcnkgb2Jzb2xldGVcIiksXG4gIHRhZ3M6IHdvcmRzKFwiQVBQTElDQVRJT04gQVVUT01BVElDIEVYUExJQ0lUIElNUExJQ0lUIFBSSVZBVEUgVEFHU1wiICsgXCIgVU5JVkVSU0FMXCIpLFxuICBzdG9yYWdlOiB3b3JkcyhcIkJPT0xFQU4gSU5URUdFUiBPQkpFQ1QgSURFTlRJRklFUiBCSVQgT0NURVQgU1RSSU5HXCIgKyBcIiBVVENUaW1lIEludGVyZmFjZUluZGV4IElBTkFpZlR5cGUgQ01JUC1BdHRyaWJ1dGVcIiArIFwiIFJFQUwgUEFDS0FHRSBQQUNLQUdFUyBJcEFkZHJlc3MgUGh5c0FkZHJlc3NcIiArIFwiIE5ldHdvcmtBZGRyZXNzIEJJVFMgQk1QU3RyaW5nIFRpbWVTdGFtcCBUaW1lVGlja3NcIiArIFwiIFRydXRoVmFsdWUgUm93U3RhdHVzIERpc3BsYXlTdHJpbmcgR2VuZXJhbFN0cmluZ1wiICsgXCIgR3JhcGhpY1N0cmluZyBJQTVTdHJpbmcgTnVtZXJpY1N0cmluZ1wiICsgXCIgUHJpbnRhYmxlU3RyaW5nIFNubXBBZG1pblN0cmluZyBUZWxldGV4U3RyaW5nXCIgKyBcIiBVVEY4U3RyaW5nIFZpZGVvdGV4U3RyaW5nIFZpc2libGVTdHJpbmcgU3RyaW5nU3RvcmVcIiArIFwiIElTTzY0NlN0cmluZyBUNjFTdHJpbmcgVW5pdmVyc2FsU3RyaW5nIFVuc2lnbmVkMzJcIiArIFwiIEludGVnZXIzMiBHYXVnZSBHYXVnZTMyIENvdW50ZXIgQ291bnRlcjMyIENvdW50ZXI2NFwiKSxcbiAgbW9kaWZpZXI6IHdvcmRzKFwiQVRUUklCVVRFIEFUVFJJQlVURVMgTUFOREFUT1JZLUdST1VQIE1BTkRBVE9SWS1HUk9VUFNcIiArIFwiIEdST1VQIEdST1VQUyBFTEVNRU5UUyBFUVVBTElUWSBPUkRFUklORyBTVUJTVFJJTkdTXCIgKyBcIiBERUZJTkVEXCIpLFxuICBhY2Nlc3NUeXBlczogd29yZHMoXCJub3QtYWNjZXNzaWJsZSBhY2Nlc3NpYmxlLWZvci1ub3RpZnkgcmVhZC1vbmx5XCIgKyBcIiByZWFkLWNyZWF0ZSByZWFkLXdyaXRlXCIpLFxuICBtdWx0aUxpbmVTdHJpbmdzOiB0cnVlXG59O1xuZXhwb3J0IGZ1bmN0aW9uIGFzbjEocGFyc2VyQ29uZmlnKSB7XG4gIHZhciBrZXl3b3JkcyA9IHBhcnNlckNvbmZpZy5rZXl3b3JkcyB8fCBkZWZhdWx0cy5rZXl3b3JkcyxcbiAgICBjbWlwVmVyYnMgPSBwYXJzZXJDb25maWcuY21pcFZlcmJzIHx8IGRlZmF1bHRzLmNtaXBWZXJicyxcbiAgICBjb21wYXJlVHlwZXMgPSBwYXJzZXJDb25maWcuY29tcGFyZVR5cGVzIHx8IGRlZmF1bHRzLmNvbXBhcmVUeXBlcyxcbiAgICBzdGF0dXMgPSBwYXJzZXJDb25maWcuc3RhdHVzIHx8IGRlZmF1bHRzLnN0YXR1cyxcbiAgICB0YWdzID0gcGFyc2VyQ29uZmlnLnRhZ3MgfHwgZGVmYXVsdHMudGFncyxcbiAgICBzdG9yYWdlID0gcGFyc2VyQ29uZmlnLnN0b3JhZ2UgfHwgZGVmYXVsdHMuc3RvcmFnZSxcbiAgICBtb2RpZmllciA9IHBhcnNlckNvbmZpZy5tb2RpZmllciB8fCBkZWZhdWx0cy5tb2RpZmllcixcbiAgICBhY2Nlc3NUeXBlcyA9IHBhcnNlckNvbmZpZy5hY2Nlc3NUeXBlcyB8fCBkZWZhdWx0cy5hY2Nlc3NUeXBlcyxcbiAgICBtdWx0aUxpbmVTdHJpbmdzID0gcGFyc2VyQ29uZmlnLm11bHRpTGluZVN0cmluZ3MgfHwgZGVmYXVsdHMubXVsdGlMaW5lU3RyaW5ncyxcbiAgICBpbmRlbnRTdGF0ZW1lbnRzID0gcGFyc2VyQ29uZmlnLmluZGVudFN0YXRlbWVudHMgIT09IGZhbHNlO1xuICB2YXIgaXNPcGVyYXRvckNoYXIgPSAvW1xcfFxcXl0vO1xuICB2YXIgY3VyUHVuYztcbiAgZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICAgIGlmIChjaCA9PSAnXCInIHx8IGNoID09IFwiJ1wiKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgaWYgKC9bXFxbXFxdXFwoXFwpe306PSw7XS8udGVzdChjaCkpIHtcbiAgICAgIGN1clB1bmMgPSBjaDtcbiAgICAgIHJldHVybiBcInB1bmN0dWF0aW9uXCI7XG4gICAgfVxuICAgIGlmIChjaCA9PSBcIi1cIikge1xuICAgICAgaWYgKHN0cmVhbS5lYXQoXCItXCIpKSB7XG4gICAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgICAgfVxuICAgIH1cbiAgICBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLl0vKTtcbiAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgIH1cbiAgICBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZShpc09wZXJhdG9yQ2hhcik7XG4gICAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgIH1cbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXC1dLyk7XG4gICAgdmFyIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImtleXdvcmRcIjtcbiAgICBpZiAoY21pcFZlcmJzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcInZhcmlhYmxlTmFtZVwiO1xuICAgIGlmIChjb21wYXJlVHlwZXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICAgIGlmIChzdGF0dXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgIGlmICh0YWdzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcInR5cGVOYW1lXCI7XG4gICAgaWYgKHN0b3JhZ2UucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwibW9kaWZpZXJcIjtcbiAgICBpZiAobW9kaWZpZXIucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwibW9kaWZpZXJcIjtcbiAgICBpZiAoYWNjZXNzVHlwZXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwibW9kaWZpZXJcIjtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZU5hbWVcIjtcbiAgfVxuICBmdW5jdGlvbiB0b2tlblN0cmluZyhxdW90ZSkge1xuICAgIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgICAgbmV4dCxcbiAgICAgICAgZW5kID0gZmFsc2U7XG4gICAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICAgIGlmIChuZXh0ID09IHF1b3RlICYmICFlc2NhcGVkKSB7XG4gICAgICAgICAgdmFyIGFmdGVyTmV4dCA9IHN0cmVhbS5wZWVrKCk7XG4gICAgICAgICAgLy9sb29rIGlmIHRoZSBjaGFyYWN0ZXIgaWYgdGhlIHF1b3RlIGlzIGxpa2UgdGhlIEIgaW4gJzEwMTAwMDEwJ0JcbiAgICAgICAgICBpZiAoYWZ0ZXJOZXh0KSB7XG4gICAgICAgICAgICBhZnRlck5leHQgPSBhZnRlck5leHQudG9Mb3dlckNhc2UoKTtcbiAgICAgICAgICAgIGlmIChhZnRlck5leHQgPT0gXCJiXCIgfHwgYWZ0ZXJOZXh0ID09IFwiaFwiIHx8IGFmdGVyTmV4dCA9PSBcIm9cIikgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgICB9XG4gICAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgICBicmVhaztcbiAgICAgICAgfVxuICAgICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICAgIH1cbiAgICAgIGlmIChlbmQgfHwgIShlc2NhcGVkIHx8IG11bHRpTGluZVN0cmluZ3MpKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9O1xuICB9XG4gIGZ1bmN0aW9uIENvbnRleHQoaW5kZW50ZWQsIGNvbHVtbiwgdHlwZSwgYWxpZ24sIHByZXYpIHtcbiAgICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gICAgdGhpcy5jb2x1bW4gPSBjb2x1bW47XG4gICAgdGhpcy50eXBlID0gdHlwZTtcbiAgICB0aGlzLmFsaWduID0gYWxpZ247XG4gICAgdGhpcy5wcmV2ID0gcHJldjtcbiAgfVxuICBmdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlKSB7XG4gICAgdmFyIGluZGVudCA9IHN0YXRlLmluZGVudGVkO1xuICAgIGlmIChzdGF0ZS5jb250ZXh0ICYmIHN0YXRlLmNvbnRleHQudHlwZSA9PSBcInN0YXRlbWVudFwiKSBpbmRlbnQgPSBzdGF0ZS5jb250ZXh0LmluZGVudGVkO1xuICAgIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoaW5kZW50LCBjb2wsIHR5cGUsIG51bGwsIHN0YXRlLmNvbnRleHQpO1xuICB9XG4gIGZ1bmN0aW9uIHBvcENvbnRleHQoc3RhdGUpIHtcbiAgICB2YXIgdCA9IHN0YXRlLmNvbnRleHQudHlwZTtcbiAgICBpZiAodCA9PSBcIilcIiB8fCB0ID09IFwiXVwiIHx8IHQgPT0gXCJ9XCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgICByZXR1cm4gc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbiAgfVxuXG4gIC8vSW50ZXJmYWNlXG4gIHJldHVybiB7XG4gICAgbmFtZTogXCJhc24xXCIsXG4gICAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdG9rZW5pemU6IG51bGwsXG4gICAgICAgIGNvbnRleHQ6IG5ldyBDb250ZXh0KC0yLCAwLCBcInRvcFwiLCBmYWxzZSksXG4gICAgICAgIGluZGVudGVkOiAwLFxuICAgICAgICBzdGFydE9mTGluZTogdHJ1ZVxuICAgICAgfTtcbiAgICB9LFxuICAgIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgdmFyIGN0eCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gZmFsc2U7XG4gICAgICAgIHN0YXRlLmluZGVudGVkID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgICBjdXJQdW5jID0gbnVsbDtcbiAgICAgIHZhciBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgaWYgKHN0eWxlID09IFwiY29tbWVudFwiKSByZXR1cm4gc3R5bGU7XG4gICAgICBpZiAoY3R4LmFsaWduID09IG51bGwpIGN0eC5hbGlnbiA9IHRydWU7XG4gICAgICBpZiAoKGN1clB1bmMgPT0gXCI7XCIgfHwgY3VyUHVuYyA9PSBcIjpcIiB8fCBjdXJQdW5jID09IFwiLFwiKSAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSB7XG4gICAgICAgIHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgfSBlbHNlIGlmIChjdXJQdW5jID09IFwie1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIn1cIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIltcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJdXCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCIoXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiKVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwifVwiKSB7XG4gICAgICAgIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgICAgaWYgKGN0eC50eXBlID09IFwifVwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgICAgd2hpbGUgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIGN0eCA9IHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgfSBlbHNlIGlmIChjdXJQdW5jID09IGN0eC50eXBlKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmIChpbmRlbnRTdGF0ZW1lbnRzICYmICgoY3R4LnR5cGUgPT0gXCJ9XCIgfHwgY3R4LnR5cGUgPT0gXCJ0b3BcIikgJiYgY3VyUHVuYyAhPSAnOycgfHwgY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIiAmJiBjdXJQdW5jID09IFwibmV3c3RhdGVtZW50XCIpKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcInN0YXRlbWVudFwiKTtcbiAgICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gZmFsc2U7XG4gICAgICByZXR1cm4gc3R5bGU7XG4gICAgfSxcbiAgICBsYW5ndWFnZURhdGE6IHtcbiAgICAgIGluZGVudE9uSW5wdXQ6IC9eXFxzKlt7fV0kLyxcbiAgICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgICAgbGluZTogXCItLVwiXG4gICAgICB9XG4gICAgfVxuICB9O1xufVxuOyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=