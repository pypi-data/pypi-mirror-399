"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5890],{

/***/ 15890
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   stex: () => (/* binding */ stex)
/* harmony export */ });
/* unused harmony export stexMath */
function mkStex(mathMode) {
  function pushCommand(state, command) {
    state.cmdState.push(command);
  }
  function peekCommand(state) {
    if (state.cmdState.length > 0) {
      return state.cmdState[state.cmdState.length - 1];
    } else {
      return null;
    }
  }
  function popCommand(state) {
    var plug = state.cmdState.pop();
    if (plug) {
      plug.closeBracket();
    }
  }

  // returns the non-default plugin closest to the end of the list
  function getMostPowerful(state) {
    var context = state.cmdState;
    for (var i = context.length - 1; i >= 0; i--) {
      var plug = context[i];
      if (plug.name == "DEFAULT") {
        continue;
      }
      return plug;
    }
    return {
      styleIdentifier: function () {
        return null;
      }
    };
  }
  function addPluginPattern(pluginName, cmdStyle, styles) {
    return function () {
      this.name = pluginName;
      this.bracketNo = 0;
      this.style = cmdStyle;
      this.styles = styles;
      this.argument = null; // \begin and \end have arguments that follow. These are stored in the plugin

      this.styleIdentifier = function () {
        return this.styles[this.bracketNo - 1] || null;
      };
      this.openBracket = function () {
        this.bracketNo++;
        return "bracket";
      };
      this.closeBracket = function () {};
    };
  }
  var plugins = {};
  plugins["importmodule"] = addPluginPattern("importmodule", "tag", ["string", "builtin"]);
  plugins["documentclass"] = addPluginPattern("documentclass", "tag", ["", "atom"]);
  plugins["usepackage"] = addPluginPattern("usepackage", "tag", ["atom"]);
  plugins["begin"] = addPluginPattern("begin", "tag", ["atom"]);
  plugins["end"] = addPluginPattern("end", "tag", ["atom"]);
  plugins["label"] = addPluginPattern("label", "tag", ["atom"]);
  plugins["ref"] = addPluginPattern("ref", "tag", ["atom"]);
  plugins["eqref"] = addPluginPattern("eqref", "tag", ["atom"]);
  plugins["cite"] = addPluginPattern("cite", "tag", ["atom"]);
  plugins["bibitem"] = addPluginPattern("bibitem", "tag", ["atom"]);
  plugins["Bibitem"] = addPluginPattern("Bibitem", "tag", ["atom"]);
  plugins["RBibitem"] = addPluginPattern("RBibitem", "tag", ["atom"]);
  plugins["DEFAULT"] = function () {
    this.name = "DEFAULT";
    this.style = "tag";
    this.styleIdentifier = this.openBracket = this.closeBracket = function () {};
  };
  function setState(state, f) {
    state.f = f;
  }

  // called when in a normal (no environment) context
  function normal(source, state) {
    var plug;
    // Do we look like '\command' ?  If so, attempt to apply the plugin 'command'
    if (source.match(/^\\[a-zA-Z@\xc0-\u1fff\u2060-\uffff]+/)) {
      var cmdName = source.current().slice(1);
      plug = plugins.hasOwnProperty(cmdName) ? plugins[cmdName] : plugins["DEFAULT"];
      plug = new plug();
      pushCommand(state, plug);
      setState(state, beginParams);
      return plug.style;
    }

    // escape characters
    if (source.match(/^\\[$&%#{}_]/)) {
      return "tag";
    }

    // white space control characters
    if (source.match(/^\\[,;!\/\\]/)) {
      return "tag";
    }

    // find if we're starting various math modes
    if (source.match("\\[")) {
      setState(state, function (source, state) {
        return inMathMode(source, state, "\\]");
      });
      return "keyword";
    }
    if (source.match("\\(")) {
      setState(state, function (source, state) {
        return inMathMode(source, state, "\\)");
      });
      return "keyword";
    }
    if (source.match("$$")) {
      setState(state, function (source, state) {
        return inMathMode(source, state, "$$");
      });
      return "keyword";
    }
    if (source.match("$")) {
      setState(state, function (source, state) {
        return inMathMode(source, state, "$");
      });
      return "keyword";
    }
    var ch = source.next();
    if (ch == "%") {
      source.skipToEnd();
      return "comment";
    } else if (ch == '}' || ch == ']') {
      plug = peekCommand(state);
      if (plug) {
        plug.closeBracket(ch);
        setState(state, beginParams);
      } else {
        return "error";
      }
      return "bracket";
    } else if (ch == '{' || ch == '[') {
      plug = plugins["DEFAULT"];
      plug = new plug();
      pushCommand(state, plug);
      return "bracket";
    } else if (/\d/.test(ch)) {
      source.eatWhile(/[\w.%]/);
      return "atom";
    } else {
      source.eatWhile(/[\w\-_]/);
      plug = getMostPowerful(state);
      if (plug.name == 'begin') {
        plug.argument = source.current();
      }
      return plug.styleIdentifier();
    }
  }
  function inMathMode(source, state, endModeSeq) {
    if (source.eatSpace()) {
      return null;
    }
    if (endModeSeq && source.match(endModeSeq)) {
      setState(state, normal);
      return "keyword";
    }
    if (source.match(/^\\[a-zA-Z@]+/)) {
      return "tag";
    }
    if (source.match(/^[a-zA-Z]+/)) {
      return "variableName.special";
    }
    // escape characters
    if (source.match(/^\\[$&%#{}_]/)) {
      return "tag";
    }
    // white space control characters
    if (source.match(/^\\[,;!\/]/)) {
      return "tag";
    }
    // special math-mode characters
    if (source.match(/^[\^_&]/)) {
      return "tag";
    }
    // non-special characters
    if (source.match(/^[+\-<>|=,\/@!*:;'"`~#?]/)) {
      return null;
    }
    if (source.match(/^(\d+\.\d*|\d*\.\d+|\d+)/)) {
      return "number";
    }
    var ch = source.next();
    if (ch == "{" || ch == "}" || ch == "[" || ch == "]" || ch == "(" || ch == ")") {
      return "bracket";
    }
    if (ch == "%") {
      source.skipToEnd();
      return "comment";
    }
    return "error";
  }
  function beginParams(source, state) {
    var ch = source.peek(),
      lastPlug;
    if (ch == '{' || ch == '[') {
      lastPlug = peekCommand(state);
      lastPlug.openBracket(ch);
      source.eat(ch);
      setState(state, normal);
      return "bracket";
    }
    if (/[ \t\r]/.test(ch)) {
      source.eat(ch);
      return null;
    }
    setState(state, normal);
    popCommand(state);
    return normal(source, state);
  }
  return {
    name: "stex",
    startState: function () {
      var f = mathMode ? function (source, state) {
        return inMathMode(source, state);
      } : normal;
      return {
        cmdState: [],
        f: f
      };
    },
    copyState: function (s) {
      return {
        cmdState: s.cmdState.slice(),
        f: s.f
      };
    },
    token: function (stream, state) {
      return state.f(stream, state);
    },
    blankLine: function (state) {
      state.f = normal;
      state.cmdState.length = 0;
    },
    languageData: {
      commentTokens: {
        line: "%"
      }
    }
  };
}
;
const stex = mkStex(false);
const stexMath = mkStex(true);

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTg5MC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3N0ZXguanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gbWtTdGV4KG1hdGhNb2RlKSB7XG4gIGZ1bmN0aW9uIHB1c2hDb21tYW5kKHN0YXRlLCBjb21tYW5kKSB7XG4gICAgc3RhdGUuY21kU3RhdGUucHVzaChjb21tYW5kKTtcbiAgfVxuICBmdW5jdGlvbiBwZWVrQ29tbWFuZChzdGF0ZSkge1xuICAgIGlmIChzdGF0ZS5jbWRTdGF0ZS5sZW5ndGggPiAwKSB7XG4gICAgICByZXR1cm4gc3RhdGUuY21kU3RhdGVbc3RhdGUuY21kU3RhdGUubGVuZ3RoIC0gMV07XG4gICAgfSBlbHNlIHtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgfVxuICBmdW5jdGlvbiBwb3BDb21tYW5kKHN0YXRlKSB7XG4gICAgdmFyIHBsdWcgPSBzdGF0ZS5jbWRTdGF0ZS5wb3AoKTtcbiAgICBpZiAocGx1Zykge1xuICAgICAgcGx1Zy5jbG9zZUJyYWNrZXQoKTtcbiAgICB9XG4gIH1cblxuICAvLyByZXR1cm5zIHRoZSBub24tZGVmYXVsdCBwbHVnaW4gY2xvc2VzdCB0byB0aGUgZW5kIG9mIHRoZSBsaXN0XG4gIGZ1bmN0aW9uIGdldE1vc3RQb3dlcmZ1bChzdGF0ZSkge1xuICAgIHZhciBjb250ZXh0ID0gc3RhdGUuY21kU3RhdGU7XG4gICAgZm9yICh2YXIgaSA9IGNvbnRleHQubGVuZ3RoIC0gMTsgaSA+PSAwOyBpLS0pIHtcbiAgICAgIHZhciBwbHVnID0gY29udGV4dFtpXTtcbiAgICAgIGlmIChwbHVnLm5hbWUgPT0gXCJERUZBVUxUXCIpIHtcbiAgICAgICAgY29udGludWU7XG4gICAgICB9XG4gICAgICByZXR1cm4gcGx1ZztcbiAgICB9XG4gICAgcmV0dXJuIHtcbiAgICAgIHN0eWxlSWRlbnRpZmllcjogZnVuY3Rpb24gKCkge1xuICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgIH1cbiAgICB9O1xuICB9XG4gIGZ1bmN0aW9uIGFkZFBsdWdpblBhdHRlcm4ocGx1Z2luTmFtZSwgY21kU3R5bGUsIHN0eWxlcykge1xuICAgIHJldHVybiBmdW5jdGlvbiAoKSB7XG4gICAgICB0aGlzLm5hbWUgPSBwbHVnaW5OYW1lO1xuICAgICAgdGhpcy5icmFja2V0Tm8gPSAwO1xuICAgICAgdGhpcy5zdHlsZSA9IGNtZFN0eWxlO1xuICAgICAgdGhpcy5zdHlsZXMgPSBzdHlsZXM7XG4gICAgICB0aGlzLmFyZ3VtZW50ID0gbnVsbDsgLy8gXFxiZWdpbiBhbmQgXFxlbmQgaGF2ZSBhcmd1bWVudHMgdGhhdCBmb2xsb3cuIFRoZXNlIGFyZSBzdG9yZWQgaW4gdGhlIHBsdWdpblxuXG4gICAgICB0aGlzLnN0eWxlSWRlbnRpZmllciA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuc3R5bGVzW3RoaXMuYnJhY2tldE5vIC0gMV0gfHwgbnVsbDtcbiAgICAgIH07XG4gICAgICB0aGlzLm9wZW5CcmFja2V0ID0gZnVuY3Rpb24gKCkge1xuICAgICAgICB0aGlzLmJyYWNrZXRObysrO1xuICAgICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgICB9O1xuICAgICAgdGhpcy5jbG9zZUJyYWNrZXQgPSBmdW5jdGlvbiAoKSB7fTtcbiAgICB9O1xuICB9XG4gIHZhciBwbHVnaW5zID0ge307XG4gIHBsdWdpbnNbXCJpbXBvcnRtb2R1bGVcIl0gPSBhZGRQbHVnaW5QYXR0ZXJuKFwiaW1wb3J0bW9kdWxlXCIsIFwidGFnXCIsIFtcInN0cmluZ1wiLCBcImJ1aWx0aW5cIl0pO1xuICBwbHVnaW5zW1wiZG9jdW1lbnRjbGFzc1wiXSA9IGFkZFBsdWdpblBhdHRlcm4oXCJkb2N1bWVudGNsYXNzXCIsIFwidGFnXCIsIFtcIlwiLCBcImF0b21cIl0pO1xuICBwbHVnaW5zW1widXNlcGFja2FnZVwiXSA9IGFkZFBsdWdpblBhdHRlcm4oXCJ1c2VwYWNrYWdlXCIsIFwidGFnXCIsIFtcImF0b21cIl0pO1xuICBwbHVnaW5zW1wiYmVnaW5cIl0gPSBhZGRQbHVnaW5QYXR0ZXJuKFwiYmVnaW5cIiwgXCJ0YWdcIiwgW1wiYXRvbVwiXSk7XG4gIHBsdWdpbnNbXCJlbmRcIl0gPSBhZGRQbHVnaW5QYXR0ZXJuKFwiZW5kXCIsIFwidGFnXCIsIFtcImF0b21cIl0pO1xuICBwbHVnaW5zW1wibGFiZWxcIl0gPSBhZGRQbHVnaW5QYXR0ZXJuKFwibGFiZWxcIiwgXCJ0YWdcIiwgW1wiYXRvbVwiXSk7XG4gIHBsdWdpbnNbXCJyZWZcIl0gPSBhZGRQbHVnaW5QYXR0ZXJuKFwicmVmXCIsIFwidGFnXCIsIFtcImF0b21cIl0pO1xuICBwbHVnaW5zW1wiZXFyZWZcIl0gPSBhZGRQbHVnaW5QYXR0ZXJuKFwiZXFyZWZcIiwgXCJ0YWdcIiwgW1wiYXRvbVwiXSk7XG4gIHBsdWdpbnNbXCJjaXRlXCJdID0gYWRkUGx1Z2luUGF0dGVybihcImNpdGVcIiwgXCJ0YWdcIiwgW1wiYXRvbVwiXSk7XG4gIHBsdWdpbnNbXCJiaWJpdGVtXCJdID0gYWRkUGx1Z2luUGF0dGVybihcImJpYml0ZW1cIiwgXCJ0YWdcIiwgW1wiYXRvbVwiXSk7XG4gIHBsdWdpbnNbXCJCaWJpdGVtXCJdID0gYWRkUGx1Z2luUGF0dGVybihcIkJpYml0ZW1cIiwgXCJ0YWdcIiwgW1wiYXRvbVwiXSk7XG4gIHBsdWdpbnNbXCJSQmliaXRlbVwiXSA9IGFkZFBsdWdpblBhdHRlcm4oXCJSQmliaXRlbVwiLCBcInRhZ1wiLCBbXCJhdG9tXCJdKTtcbiAgcGx1Z2luc1tcIkRFRkFVTFRcIl0gPSBmdW5jdGlvbiAoKSB7XG4gICAgdGhpcy5uYW1lID0gXCJERUZBVUxUXCI7XG4gICAgdGhpcy5zdHlsZSA9IFwidGFnXCI7XG4gICAgdGhpcy5zdHlsZUlkZW50aWZpZXIgPSB0aGlzLm9wZW5CcmFja2V0ID0gdGhpcy5jbG9zZUJyYWNrZXQgPSBmdW5jdGlvbiAoKSB7fTtcbiAgfTtcbiAgZnVuY3Rpb24gc2V0U3RhdGUoc3RhdGUsIGYpIHtcbiAgICBzdGF0ZS5mID0gZjtcbiAgfVxuXG4gIC8vIGNhbGxlZCB3aGVuIGluIGEgbm9ybWFsIChubyBlbnZpcm9ubWVudCkgY29udGV4dFxuICBmdW5jdGlvbiBub3JtYWwoc291cmNlLCBzdGF0ZSkge1xuICAgIHZhciBwbHVnO1xuICAgIC8vIERvIHdlIGxvb2sgbGlrZSAnXFxjb21tYW5kJyA/ICBJZiBzbywgYXR0ZW1wdCB0byBhcHBseSB0aGUgcGx1Z2luICdjb21tYW5kJ1xuICAgIGlmIChzb3VyY2UubWF0Y2goL15cXFxcW2EtekEtWkBcXHhjMC1cXHUxZmZmXFx1MjA2MC1cXHVmZmZmXSsvKSkge1xuICAgICAgdmFyIGNtZE5hbWUgPSBzb3VyY2UuY3VycmVudCgpLnNsaWNlKDEpO1xuICAgICAgcGx1ZyA9IHBsdWdpbnMuaGFzT3duUHJvcGVydHkoY21kTmFtZSkgPyBwbHVnaW5zW2NtZE5hbWVdIDogcGx1Z2luc1tcIkRFRkFVTFRcIl07XG4gICAgICBwbHVnID0gbmV3IHBsdWcoKTtcbiAgICAgIHB1c2hDb21tYW5kKHN0YXRlLCBwbHVnKTtcbiAgICAgIHNldFN0YXRlKHN0YXRlLCBiZWdpblBhcmFtcyk7XG4gICAgICByZXR1cm4gcGx1Zy5zdHlsZTtcbiAgICB9XG5cbiAgICAvLyBlc2NhcGUgY2hhcmFjdGVyc1xuICAgIGlmIChzb3VyY2UubWF0Y2goL15cXFxcWyQmJSN7fV9dLykpIHtcbiAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgIH1cblxuICAgIC8vIHdoaXRlIHNwYWNlIGNvbnRyb2wgY2hhcmFjdGVyc1xuICAgIGlmIChzb3VyY2UubWF0Y2goL15cXFxcWyw7IVxcL1xcXFxdLykpIHtcbiAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgIH1cblxuICAgIC8vIGZpbmQgaWYgd2UncmUgc3RhcnRpbmcgdmFyaW91cyBtYXRoIG1vZGVzXG4gICAgaWYgKHNvdXJjZS5tYXRjaChcIlxcXFxbXCIpKSB7XG4gICAgICBzZXRTdGF0ZShzdGF0ZSwgZnVuY3Rpb24gKHNvdXJjZSwgc3RhdGUpIHtcbiAgICAgICAgcmV0dXJuIGluTWF0aE1vZGUoc291cmNlLCBzdGF0ZSwgXCJcXFxcXVwiKTtcbiAgICAgIH0pO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICBpZiAoc291cmNlLm1hdGNoKFwiXFxcXChcIikpIHtcbiAgICAgIHNldFN0YXRlKHN0YXRlLCBmdW5jdGlvbiAoc291cmNlLCBzdGF0ZSkge1xuICAgICAgICByZXR1cm4gaW5NYXRoTW9kZShzb3VyY2UsIHN0YXRlLCBcIlxcXFwpXCIpO1xuICAgICAgfSk7XG4gICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgfVxuICAgIGlmIChzb3VyY2UubWF0Y2goXCIkJFwiKSkge1xuICAgICAgc2V0U3RhdGUoc3RhdGUsIGZ1bmN0aW9uIChzb3VyY2UsIHN0YXRlKSB7XG4gICAgICAgIHJldHVybiBpbk1hdGhNb2RlKHNvdXJjZSwgc3RhdGUsIFwiJCRcIik7XG4gICAgICB9KTtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9XG4gICAgaWYgKHNvdXJjZS5tYXRjaChcIiRcIikpIHtcbiAgICAgIHNldFN0YXRlKHN0YXRlLCBmdW5jdGlvbiAoc291cmNlLCBzdGF0ZSkge1xuICAgICAgICByZXR1cm4gaW5NYXRoTW9kZShzb3VyY2UsIHN0YXRlLCBcIiRcIik7XG4gICAgICB9KTtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9XG4gICAgdmFyIGNoID0gc291cmNlLm5leHQoKTtcbiAgICBpZiAoY2ggPT0gXCIlXCIpIHtcbiAgICAgIHNvdXJjZS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9IGVsc2UgaWYgKGNoID09ICd9JyB8fCBjaCA9PSAnXScpIHtcbiAgICAgIHBsdWcgPSBwZWVrQ29tbWFuZChzdGF0ZSk7XG4gICAgICBpZiAocGx1Zykge1xuICAgICAgICBwbHVnLmNsb3NlQnJhY2tldChjaCk7XG4gICAgICAgIHNldFN0YXRlKHN0YXRlLCBiZWdpblBhcmFtcyk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gXCJlcnJvclwiO1xuICAgICAgfVxuICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gJ3snIHx8IGNoID09ICdbJykge1xuICAgICAgcGx1ZyA9IHBsdWdpbnNbXCJERUZBVUxUXCJdO1xuICAgICAgcGx1ZyA9IG5ldyBwbHVnKCk7XG4gICAgICBwdXNoQ29tbWFuZChzdGF0ZSwgcGx1Zyk7XG4gICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgfSBlbHNlIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgICAgc291cmNlLmVhdFdoaWxlKC9bXFx3LiVdLyk7XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIHNvdXJjZS5lYXRXaGlsZSgvW1xcd1xcLV9dLyk7XG4gICAgICBwbHVnID0gZ2V0TW9zdFBvd2VyZnVsKHN0YXRlKTtcbiAgICAgIGlmIChwbHVnLm5hbWUgPT0gJ2JlZ2luJykge1xuICAgICAgICBwbHVnLmFyZ3VtZW50ID0gc291cmNlLmN1cnJlbnQoKTtcbiAgICAgIH1cbiAgICAgIHJldHVybiBwbHVnLnN0eWxlSWRlbnRpZmllcigpO1xuICAgIH1cbiAgfVxuICBmdW5jdGlvbiBpbk1hdGhNb2RlKHNvdXJjZSwgc3RhdGUsIGVuZE1vZGVTZXEpIHtcbiAgICBpZiAoc291cmNlLmVhdFNwYWNlKCkpIHtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICBpZiAoZW5kTW9kZVNlcSAmJiBzb3VyY2UubWF0Y2goZW5kTW9kZVNlcSkpIHtcbiAgICAgIHNldFN0YXRlKHN0YXRlLCBub3JtYWwpO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICBpZiAoc291cmNlLm1hdGNoKC9eXFxcXFthLXpBLVpAXSsvKSkge1xuICAgICAgcmV0dXJuIFwidGFnXCI7XG4gICAgfVxuICAgIGlmIChzb3VyY2UubWF0Y2goL15bYS16QS1aXSsvKSkge1xuICAgICAgcmV0dXJuIFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICB9XG4gICAgLy8gZXNjYXBlIGNoYXJhY3RlcnNcbiAgICBpZiAoc291cmNlLm1hdGNoKC9eXFxcXFskJiUje31fXS8pKSB7XG4gICAgICByZXR1cm4gXCJ0YWdcIjtcbiAgICB9XG4gICAgLy8gd2hpdGUgc3BhY2UgY29udHJvbCBjaGFyYWN0ZXJzXG4gICAgaWYgKHNvdXJjZS5tYXRjaCgvXlxcXFxbLDshXFwvXS8pKSB7XG4gICAgICByZXR1cm4gXCJ0YWdcIjtcbiAgICB9XG4gICAgLy8gc3BlY2lhbCBtYXRoLW1vZGUgY2hhcmFjdGVyc1xuICAgIGlmIChzb3VyY2UubWF0Y2goL15bXFxeXyZdLykpIHtcbiAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgIH1cbiAgICAvLyBub24tc3BlY2lhbCBjaGFyYWN0ZXJzXG4gICAgaWYgKHNvdXJjZS5tYXRjaCgvXlsrXFwtPD58PSxcXC9AISo6OydcImB+Iz9dLykpIHtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICBpZiAoc291cmNlLm1hdGNoKC9eKFxcZCtcXC5cXGQqfFxcZCpcXC5cXGQrfFxcZCspLykpIHtcbiAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgIH1cbiAgICB2YXIgY2ggPSBzb3VyY2UubmV4dCgpO1xuICAgIGlmIChjaCA9PSBcIntcIiB8fCBjaCA9PSBcIn1cIiB8fCBjaCA9PSBcIltcIiB8fCBjaCA9PSBcIl1cIiB8fCBjaCA9PSBcIihcIiB8fCBjaCA9PSBcIilcIikge1xuICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgIH1cbiAgICBpZiAoY2ggPT0gXCIlXCIpIHtcbiAgICAgIHNvdXJjZS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgcmV0dXJuIFwiZXJyb3JcIjtcbiAgfVxuICBmdW5jdGlvbiBiZWdpblBhcmFtcyhzb3VyY2UsIHN0YXRlKSB7XG4gICAgdmFyIGNoID0gc291cmNlLnBlZWsoKSxcbiAgICAgIGxhc3RQbHVnO1xuICAgIGlmIChjaCA9PSAneycgfHwgY2ggPT0gJ1snKSB7XG4gICAgICBsYXN0UGx1ZyA9IHBlZWtDb21tYW5kKHN0YXRlKTtcbiAgICAgIGxhc3RQbHVnLm9wZW5CcmFja2V0KGNoKTtcbiAgICAgIHNvdXJjZS5lYXQoY2gpO1xuICAgICAgc2V0U3RhdGUoc3RhdGUsIG5vcm1hbCk7XG4gICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgfVxuICAgIGlmICgvWyBcXHRcXHJdLy50ZXN0KGNoKSkge1xuICAgICAgc291cmNlLmVhdChjaCk7XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICB9XG4gICAgc2V0U3RhdGUoc3RhdGUsIG5vcm1hbCk7XG4gICAgcG9wQ29tbWFuZChzdGF0ZSk7XG4gICAgcmV0dXJuIG5vcm1hbChzb3VyY2UsIHN0YXRlKTtcbiAgfVxuICByZXR1cm4ge1xuICAgIG5hbWU6IFwic3RleFwiLFxuICAgIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHZhciBmID0gbWF0aE1vZGUgPyBmdW5jdGlvbiAoc291cmNlLCBzdGF0ZSkge1xuICAgICAgICByZXR1cm4gaW5NYXRoTW9kZShzb3VyY2UsIHN0YXRlKTtcbiAgICAgIH0gOiBub3JtYWw7XG4gICAgICByZXR1cm4ge1xuICAgICAgICBjbWRTdGF0ZTogW10sXG4gICAgICAgIGY6IGZcbiAgICAgIH07XG4gICAgfSxcbiAgICBjb3B5U3RhdGU6IGZ1bmN0aW9uIChzKSB7XG4gICAgICByZXR1cm4ge1xuICAgICAgICBjbWRTdGF0ZTogcy5jbWRTdGF0ZS5zbGljZSgpLFxuICAgICAgICBmOiBzLmZcbiAgICAgIH07XG4gICAgfSxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIHJldHVybiBzdGF0ZS5mKHN0cmVhbSwgc3RhdGUpO1xuICAgIH0sXG4gICAgYmxhbmtMaW5lOiBmdW5jdGlvbiAoc3RhdGUpIHtcbiAgICAgIHN0YXRlLmYgPSBub3JtYWw7XG4gICAgICBzdGF0ZS5jbWRTdGF0ZS5sZW5ndGggPSAwO1xuICAgIH0sXG4gICAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICAgIGxpbmU6IFwiJVwiXG4gICAgICB9XG4gICAgfVxuICB9O1xufVxuO1xuZXhwb3J0IGNvbnN0IHN0ZXggPSBta1N0ZXgoZmFsc2UpO1xuZXhwb3J0IGNvbnN0IHN0ZXhNYXRoID0gbWtTdGV4KHRydWUpOyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=