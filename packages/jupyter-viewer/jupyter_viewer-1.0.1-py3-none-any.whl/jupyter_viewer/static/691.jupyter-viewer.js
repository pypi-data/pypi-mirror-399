"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[691],{

/***/ 60691
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   gas: () => (/* binding */ gas)
/* harmony export */ });
/* unused harmony export gasArm */
function mkGas(arch) {
  // If an architecture is specified, its initialization function may
  // populate this array with custom parsing functions which will be
  // tried in the event that the standard functions do not find a match.
  var custom = [];

  // The symbol used to start a line comment changes based on the target
  // architecture.
  // If no architecture is pased in "parserConfig" then only multiline
  // comments will have syntax support.
  var lineCommentStartSymbol = "";

  // These directives are architecture independent.
  // Machine specific directives should go in their respective
  // architecture initialization function.
  // Reference:
  // http://sourceware.org/binutils/docs/as/Pseudo-Ops.html#Pseudo-Ops
  var directives = {
    ".abort": "builtin",
    ".align": "builtin",
    ".altmacro": "builtin",
    ".ascii": "builtin",
    ".asciz": "builtin",
    ".balign": "builtin",
    ".balignw": "builtin",
    ".balignl": "builtin",
    ".bundle_align_mode": "builtin",
    ".bundle_lock": "builtin",
    ".bundle_unlock": "builtin",
    ".byte": "builtin",
    ".cfi_startproc": "builtin",
    ".comm": "builtin",
    ".data": "builtin",
    ".def": "builtin",
    ".desc": "builtin",
    ".dim": "builtin",
    ".double": "builtin",
    ".eject": "builtin",
    ".else": "builtin",
    ".elseif": "builtin",
    ".end": "builtin",
    ".endef": "builtin",
    ".endfunc": "builtin",
    ".endif": "builtin",
    ".equ": "builtin",
    ".equiv": "builtin",
    ".eqv": "builtin",
    ".err": "builtin",
    ".error": "builtin",
    ".exitm": "builtin",
    ".extern": "builtin",
    ".fail": "builtin",
    ".file": "builtin",
    ".fill": "builtin",
    ".float": "builtin",
    ".func": "builtin",
    ".global": "builtin",
    ".gnu_attribute": "builtin",
    ".hidden": "builtin",
    ".hword": "builtin",
    ".ident": "builtin",
    ".if": "builtin",
    ".incbin": "builtin",
    ".include": "builtin",
    ".int": "builtin",
    ".internal": "builtin",
    ".irp": "builtin",
    ".irpc": "builtin",
    ".lcomm": "builtin",
    ".lflags": "builtin",
    ".line": "builtin",
    ".linkonce": "builtin",
    ".list": "builtin",
    ".ln": "builtin",
    ".loc": "builtin",
    ".loc_mark_labels": "builtin",
    ".local": "builtin",
    ".long": "builtin",
    ".macro": "builtin",
    ".mri": "builtin",
    ".noaltmacro": "builtin",
    ".nolist": "builtin",
    ".octa": "builtin",
    ".offset": "builtin",
    ".org": "builtin",
    ".p2align": "builtin",
    ".popsection": "builtin",
    ".previous": "builtin",
    ".print": "builtin",
    ".protected": "builtin",
    ".psize": "builtin",
    ".purgem": "builtin",
    ".pushsection": "builtin",
    ".quad": "builtin",
    ".reloc": "builtin",
    ".rept": "builtin",
    ".sbttl": "builtin",
    ".scl": "builtin",
    ".section": "builtin",
    ".set": "builtin",
    ".short": "builtin",
    ".single": "builtin",
    ".size": "builtin",
    ".skip": "builtin",
    ".sleb128": "builtin",
    ".space": "builtin",
    ".stab": "builtin",
    ".string": "builtin",
    ".struct": "builtin",
    ".subsection": "builtin",
    ".symver": "builtin",
    ".tag": "builtin",
    ".text": "builtin",
    ".title": "builtin",
    ".type": "builtin",
    ".uleb128": "builtin",
    ".val": "builtin",
    ".version": "builtin",
    ".vtable_entry": "builtin",
    ".vtable_inherit": "builtin",
    ".warning": "builtin",
    ".weak": "builtin",
    ".weakref": "builtin",
    ".word": "builtin"
  };
  var registers = {};
  function x86() {
    lineCommentStartSymbol = "#";
    registers.al = "variable";
    registers.ah = "variable";
    registers.ax = "variable";
    registers.eax = "variableName.special";
    registers.rax = "variableName.special";
    registers.bl = "variable";
    registers.bh = "variable";
    registers.bx = "variable";
    registers.ebx = "variableName.special";
    registers.rbx = "variableName.special";
    registers.cl = "variable";
    registers.ch = "variable";
    registers.cx = "variable";
    registers.ecx = "variableName.special";
    registers.rcx = "variableName.special";
    registers.dl = "variable";
    registers.dh = "variable";
    registers.dx = "variable";
    registers.edx = "variableName.special";
    registers.rdx = "variableName.special";
    registers.si = "variable";
    registers.esi = "variableName.special";
    registers.rsi = "variableName.special";
    registers.di = "variable";
    registers.edi = "variableName.special";
    registers.rdi = "variableName.special";
    registers.sp = "variable";
    registers.esp = "variableName.special";
    registers.rsp = "variableName.special";
    registers.bp = "variable";
    registers.ebp = "variableName.special";
    registers.rbp = "variableName.special";
    registers.ip = "variable";
    registers.eip = "variableName.special";
    registers.rip = "variableName.special";
    registers.cs = "keyword";
    registers.ds = "keyword";
    registers.ss = "keyword";
    registers.es = "keyword";
    registers.fs = "keyword";
    registers.gs = "keyword";
  }
  function armv6() {
    // Reference:
    // http://infocenter.arm.com/help/topic/com.arm.doc.qrc0001l/QRC0001_UAL.pdf
    // http://infocenter.arm.com/help/topic/com.arm.doc.ddi0301h/DDI0301H_arm1176jzfs_r0p7_trm.pdf
    lineCommentStartSymbol = "@";
    directives.syntax = "builtin";
    registers.r0 = "variable";
    registers.r1 = "variable";
    registers.r2 = "variable";
    registers.r3 = "variable";
    registers.r4 = "variable";
    registers.r5 = "variable";
    registers.r6 = "variable";
    registers.r7 = "variable";
    registers.r8 = "variable";
    registers.r9 = "variable";
    registers.r10 = "variable";
    registers.r11 = "variable";
    registers.r12 = "variable";
    registers.sp = "variableName.special";
    registers.lr = "variableName.special";
    registers.pc = "variableName.special";
    registers.r13 = registers.sp;
    registers.r14 = registers.lr;
    registers.r15 = registers.pc;
    custom.push(function (ch, stream) {
      if (ch === '#') {
        stream.eatWhile(/\w/);
        return "number";
      }
    });
  }
  if (arch === "x86") {
    x86();
  } else if (arch === "arm" || arch === "armv6") {
    armv6();
  }
  function nextUntilUnescaped(stream, end) {
    var escaped = false,
      next;
    while ((next = stream.next()) != null) {
      if (next === end && !escaped) {
        return false;
      }
      escaped = !escaped && next === "\\";
    }
    return escaped;
  }
  function clikeComment(stream, state) {
    var maybeEnd = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch === "/" && maybeEnd) {
        state.tokenize = null;
        break;
      }
      maybeEnd = ch === "*";
    }
    return "comment";
  }
  return {
    name: "gas",
    startState: function () {
      return {
        tokenize: null
      };
    },
    token: function (stream, state) {
      if (state.tokenize) {
        return state.tokenize(stream, state);
      }
      if (stream.eatSpace()) {
        return null;
      }
      var style,
        cur,
        ch = stream.next();
      if (ch === "/") {
        if (stream.eat("*")) {
          state.tokenize = clikeComment;
          return clikeComment(stream, state);
        }
      }
      if (ch === lineCommentStartSymbol) {
        stream.skipToEnd();
        return "comment";
      }
      if (ch === '"') {
        nextUntilUnescaped(stream, '"');
        return "string";
      }
      if (ch === '.') {
        stream.eatWhile(/\w/);
        cur = stream.current().toLowerCase();
        style = directives[cur];
        return style || null;
      }
      if (ch === '=') {
        stream.eatWhile(/\w/);
        return "tag";
      }
      if (ch === '{') {
        return "bracket";
      }
      if (ch === '}') {
        return "bracket";
      }
      if (/\d/.test(ch)) {
        if (ch === "0" && stream.eat("x")) {
          stream.eatWhile(/[0-9a-fA-F]/);
          return "number";
        }
        stream.eatWhile(/\d/);
        return "number";
      }
      if (/\w/.test(ch)) {
        stream.eatWhile(/\w/);
        if (stream.eat(":")) {
          return 'tag';
        }
        cur = stream.current().toLowerCase();
        style = registers[cur];
        return style || null;
      }
      for (var i = 0; i < custom.length; i++) {
        style = custom[i](ch, stream, state);
        if (style) {
          return style;
        }
      }
    },
    languageData: {
      commentTokens: {
        line: lineCommentStartSymbol,
        block: {
          open: "/*",
          close: "*/"
        }
      }
    }
  };
}
;
const gas = mkGas("x86");
const gasArm = mkGas("arm");

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjkxLmp1cHl0ZXItdmlld2VyLmpzIiwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2dhcy5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBta0dhcyhhcmNoKSB7XG4gIC8vIElmIGFuIGFyY2hpdGVjdHVyZSBpcyBzcGVjaWZpZWQsIGl0cyBpbml0aWFsaXphdGlvbiBmdW5jdGlvbiBtYXlcbiAgLy8gcG9wdWxhdGUgdGhpcyBhcnJheSB3aXRoIGN1c3RvbSBwYXJzaW5nIGZ1bmN0aW9ucyB3aGljaCB3aWxsIGJlXG4gIC8vIHRyaWVkIGluIHRoZSBldmVudCB0aGF0IHRoZSBzdGFuZGFyZCBmdW5jdGlvbnMgZG8gbm90IGZpbmQgYSBtYXRjaC5cbiAgdmFyIGN1c3RvbSA9IFtdO1xuXG4gIC8vIFRoZSBzeW1ib2wgdXNlZCB0byBzdGFydCBhIGxpbmUgY29tbWVudCBjaGFuZ2VzIGJhc2VkIG9uIHRoZSB0YXJnZXRcbiAgLy8gYXJjaGl0ZWN0dXJlLlxuICAvLyBJZiBubyBhcmNoaXRlY3R1cmUgaXMgcGFzZWQgaW4gXCJwYXJzZXJDb25maWdcIiB0aGVuIG9ubHkgbXVsdGlsaW5lXG4gIC8vIGNvbW1lbnRzIHdpbGwgaGF2ZSBzeW50YXggc3VwcG9ydC5cbiAgdmFyIGxpbmVDb21tZW50U3RhcnRTeW1ib2wgPSBcIlwiO1xuXG4gIC8vIFRoZXNlIGRpcmVjdGl2ZXMgYXJlIGFyY2hpdGVjdHVyZSBpbmRlcGVuZGVudC5cbiAgLy8gTWFjaGluZSBzcGVjaWZpYyBkaXJlY3RpdmVzIHNob3VsZCBnbyBpbiB0aGVpciByZXNwZWN0aXZlXG4gIC8vIGFyY2hpdGVjdHVyZSBpbml0aWFsaXphdGlvbiBmdW5jdGlvbi5cbiAgLy8gUmVmZXJlbmNlOlxuICAvLyBodHRwOi8vc291cmNld2FyZS5vcmcvYmludXRpbHMvZG9jcy9hcy9Qc2V1ZG8tT3BzLmh0bWwjUHNldWRvLU9wc1xuICB2YXIgZGlyZWN0aXZlcyA9IHtcbiAgICBcIi5hYm9ydFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5hbGlnblwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5hbHRtYWNyb1wiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5hc2NpaVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5hc2NpelwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5iYWxpZ25cIjogXCJidWlsdGluXCIsXG4gICAgXCIuYmFsaWdud1wiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5iYWxpZ25sXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmJ1bmRsZV9hbGlnbl9tb2RlXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmJ1bmRsZV9sb2NrXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmJ1bmRsZV91bmxvY2tcIjogXCJidWlsdGluXCIsXG4gICAgXCIuYnl0ZVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5jZmlfc3RhcnRwcm9jXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmNvbW1cIjogXCJidWlsdGluXCIsXG4gICAgXCIuZGF0YVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5kZWZcIjogXCJidWlsdGluXCIsXG4gICAgXCIuZGVzY1wiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5kaW1cIjogXCJidWlsdGluXCIsXG4gICAgXCIuZG91YmxlXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmVqZWN0XCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmVsc2VcIjogXCJidWlsdGluXCIsXG4gICAgXCIuZWxzZWlmXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmVuZFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5lbmRlZlwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5lbmRmdW5jXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmVuZGlmXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmVxdVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5lcXVpdlwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5lcXZcIjogXCJidWlsdGluXCIsXG4gICAgXCIuZXJyXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmVycm9yXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmV4aXRtXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmV4dGVyblwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5mYWlsXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmZpbGVcIjogXCJidWlsdGluXCIsXG4gICAgXCIuZmlsbFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5mbG9hdFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5mdW5jXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmdsb2JhbFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5nbnVfYXR0cmlidXRlXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmhpZGRlblwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5od29yZFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5pZGVudFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5pZlwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5pbmNiaW5cIjogXCJidWlsdGluXCIsXG4gICAgXCIuaW5jbHVkZVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5pbnRcIjogXCJidWlsdGluXCIsXG4gICAgXCIuaW50ZXJuYWxcIjogXCJidWlsdGluXCIsXG4gICAgXCIuaXJwXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmlycGNcIjogXCJidWlsdGluXCIsXG4gICAgXCIubGNvbW1cIjogXCJidWlsdGluXCIsXG4gICAgXCIubGZsYWdzXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmxpbmVcIjogXCJidWlsdGluXCIsXG4gICAgXCIubGlua29uY2VcIjogXCJidWlsdGluXCIsXG4gICAgXCIubGlzdFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5sblwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5sb2NcIjogXCJidWlsdGluXCIsXG4gICAgXCIubG9jX21hcmtfbGFiZWxzXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmxvY2FsXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLmxvbmdcIjogXCJidWlsdGluXCIsXG4gICAgXCIubWFjcm9cIjogXCJidWlsdGluXCIsXG4gICAgXCIubXJpXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLm5vYWx0bWFjcm9cIjogXCJidWlsdGluXCIsXG4gICAgXCIubm9saXN0XCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLm9jdGFcIjogXCJidWlsdGluXCIsXG4gICAgXCIub2Zmc2V0XCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLm9yZ1wiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5wMmFsaWduXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnBvcHNlY3Rpb25cIjogXCJidWlsdGluXCIsXG4gICAgXCIucHJldmlvdXNcIjogXCJidWlsdGluXCIsXG4gICAgXCIucHJpbnRcIjogXCJidWlsdGluXCIsXG4gICAgXCIucHJvdGVjdGVkXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnBzaXplXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnB1cmdlbVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5wdXNoc2VjdGlvblwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5xdWFkXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnJlbG9jXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnJlcHRcIjogXCJidWlsdGluXCIsXG4gICAgXCIuc2J0dGxcIjogXCJidWlsdGluXCIsXG4gICAgXCIuc2NsXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnNlY3Rpb25cIjogXCJidWlsdGluXCIsXG4gICAgXCIuc2V0XCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnNob3J0XCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnNpbmdsZVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5zaXplXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnNraXBcIjogXCJidWlsdGluXCIsXG4gICAgXCIuc2xlYjEyOFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5zcGFjZVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5zdGFiXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnN0cmluZ1wiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5zdHJ1Y3RcIjogXCJidWlsdGluXCIsXG4gICAgXCIuc3Vic2VjdGlvblwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi5zeW12ZXJcIjogXCJidWlsdGluXCIsXG4gICAgXCIudGFnXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnRleHRcIjogXCJidWlsdGluXCIsXG4gICAgXCIudGl0bGVcIjogXCJidWlsdGluXCIsXG4gICAgXCIudHlwZVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi51bGViMTI4XCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnZhbFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi52ZXJzaW9uXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLnZ0YWJsZV9lbnRyeVwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi52dGFibGVfaW5oZXJpdFwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi53YXJuaW5nXCI6IFwiYnVpbHRpblwiLFxuICAgIFwiLndlYWtcIjogXCJidWlsdGluXCIsXG4gICAgXCIud2Vha3JlZlwiOiBcImJ1aWx0aW5cIixcbiAgICBcIi53b3JkXCI6IFwiYnVpbHRpblwiXG4gIH07XG4gIHZhciByZWdpc3RlcnMgPSB7fTtcbiAgZnVuY3Rpb24geDg2KCkge1xuICAgIGxpbmVDb21tZW50U3RhcnRTeW1ib2wgPSBcIiNcIjtcbiAgICByZWdpc3RlcnMuYWwgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLmFoID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5heCA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMuZWF4ID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5yYXggPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLmJsID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5iaCA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMuYnggPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLmVieCA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMucmJ4ID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5jbCA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMuY2ggPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLmN4ID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5lY3ggPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLnJjeCA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMuZGwgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLmRoID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5keCA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMuZWR4ID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5yZHggPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLnNpID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5lc2kgPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLnJzaSA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMuZGkgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLmVkaSA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMucmRpID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5zcCA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMuZXNwID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5yc3AgPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLmJwID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5lYnAgPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLnJicCA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMuaXAgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLmVpcCA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMucmlwID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5jcyA9IFwia2V5d29yZFwiO1xuICAgIHJlZ2lzdGVycy5kcyA9IFwia2V5d29yZFwiO1xuICAgIHJlZ2lzdGVycy5zcyA9IFwia2V5d29yZFwiO1xuICAgIHJlZ2lzdGVycy5lcyA9IFwia2V5d29yZFwiO1xuICAgIHJlZ2lzdGVycy5mcyA9IFwia2V5d29yZFwiO1xuICAgIHJlZ2lzdGVycy5ncyA9IFwia2V5d29yZFwiO1xuICB9XG4gIGZ1bmN0aW9uIGFybXY2KCkge1xuICAgIC8vIFJlZmVyZW5jZTpcbiAgICAvLyBodHRwOi8vaW5mb2NlbnRlci5hcm0uY29tL2hlbHAvdG9waWMvY29tLmFybS5kb2MucXJjMDAwMWwvUVJDMDAwMV9VQUwucGRmXG4gICAgLy8gaHR0cDovL2luZm9jZW50ZXIuYXJtLmNvbS9oZWxwL3RvcGljL2NvbS5hcm0uZG9jLmRkaTAzMDFoL0RESTAzMDFIX2FybTExNzZqemZzX3IwcDdfdHJtLnBkZlxuICAgIGxpbmVDb21tZW50U3RhcnRTeW1ib2wgPSBcIkBcIjtcbiAgICBkaXJlY3RpdmVzLnN5bnRheCA9IFwiYnVpbHRpblwiO1xuICAgIHJlZ2lzdGVycy5yMCA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMucjEgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLnIyID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5yMyA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMucjQgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLnI1ID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5yNiA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMucjcgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLnI4ID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5yOSA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMucjEwID0gXCJ2YXJpYWJsZVwiO1xuICAgIHJlZ2lzdGVycy5yMTEgPSBcInZhcmlhYmxlXCI7XG4gICAgcmVnaXN0ZXJzLnIxMiA9IFwidmFyaWFibGVcIjtcbiAgICByZWdpc3RlcnMuc3AgPSBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCI7XG4gICAgcmVnaXN0ZXJzLmxyID0gXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiO1xuICAgIHJlZ2lzdGVycy5wYyA9IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZWdpc3RlcnMucjEzID0gcmVnaXN0ZXJzLnNwO1xuICAgIHJlZ2lzdGVycy5yMTQgPSByZWdpc3RlcnMubHI7XG4gICAgcmVnaXN0ZXJzLnIxNSA9IHJlZ2lzdGVycy5wYztcbiAgICBjdXN0b20ucHVzaChmdW5jdGlvbiAoY2gsIHN0cmVhbSkge1xuICAgICAgaWYgKGNoID09PSAnIycpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9cXHcvKTtcbiAgICAgICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgICB9XG4gICAgfSk7XG4gIH1cbiAgaWYgKGFyY2ggPT09IFwieDg2XCIpIHtcbiAgICB4ODYoKTtcbiAgfSBlbHNlIGlmIChhcmNoID09PSBcImFybVwiIHx8IGFyY2ggPT09IFwiYXJtdjZcIikge1xuICAgIGFybXY2KCk7XG4gIH1cbiAgZnVuY3Rpb24gbmV4dFVudGlsVW5lc2NhcGVkKHN0cmVhbSwgZW5kKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQ7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT09IGVuZCAmJiAhZXNjYXBlZCkge1xuICAgICAgICByZXR1cm4gZmFsc2U7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PT0gXCJcXFxcXCI7XG4gICAgfVxuICAgIHJldHVybiBlc2NhcGVkO1xuICB9XG4gIGZ1bmN0aW9uIGNsaWtlQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgICBjaDtcbiAgICB3aGlsZSAoKGNoID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKGNoID09PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgbWF5YmVFbmQgPSBjaCA9PT0gXCIqXCI7XG4gICAgfVxuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuICByZXR1cm4ge1xuICAgIG5hbWU6IFwiZ2FzXCIsXG4gICAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdG9rZW5pemU6IG51bGxcbiAgICAgIH07XG4gICAgfSxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIGlmIChzdGF0ZS50b2tlbml6ZSkge1xuICAgICAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICAgICAgcmV0dXJuIG51bGw7XG4gICAgICB9XG4gICAgICB2YXIgc3R5bGUsXG4gICAgICAgIGN1cixcbiAgICAgICAgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICAgICAgaWYgKGNoID09PSBcIi9cIikge1xuICAgICAgICBpZiAoc3RyZWFtLmVhdChcIipcIikpIHtcbiAgICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IGNsaWtlQ29tbWVudDtcbiAgICAgICAgICByZXR1cm4gY2xpa2VDb21tZW50KHN0cmVhbSwgc3RhdGUpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICBpZiAoY2ggPT09IGxpbmVDb21tZW50U3RhcnRTeW1ib2wpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgICB9XG4gICAgICBpZiAoY2ggPT09ICdcIicpIHtcbiAgICAgICAgbmV4dFVudGlsVW5lc2NhcGVkKHN0cmVhbSwgJ1wiJyk7XG4gICAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgICAgfVxuICAgICAgaWYgKGNoID09PSAnLicpIHtcbiAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9cXHcvKTtcbiAgICAgICAgY3VyID0gc3RyZWFtLmN1cnJlbnQoKS50b0xvd2VyQ2FzZSgpO1xuICAgICAgICBzdHlsZSA9IGRpcmVjdGl2ZXNbY3VyXTtcbiAgICAgICAgcmV0dXJuIHN0eWxlIHx8IG51bGw7XG4gICAgICB9XG4gICAgICBpZiAoY2ggPT09ICc9Jykge1xuICAgICAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgICAgICByZXR1cm4gXCJ0YWdcIjtcbiAgICAgIH1cbiAgICAgIGlmIChjaCA9PT0gJ3snKSB7XG4gICAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICAgIH1cbiAgICAgIGlmIChjaCA9PT0gJ30nKSB7XG4gICAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICAgIH1cbiAgICAgIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgICAgICBpZiAoY2ggPT09IFwiMFwiICYmIHN0cmVhbS5lYXQoXCJ4XCIpKSB7XG4gICAgICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bMC05YS1mQS1GXS8pO1xuICAgICAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgICAgICB9XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvXFxkLyk7XG4gICAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgICAgfVxuICAgICAgaWYgKC9cXHcvLnRlc3QoY2gpKSB7XG4gICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvXFx3Lyk7XG4gICAgICAgIGlmIChzdHJlYW0uZWF0KFwiOlwiKSkge1xuICAgICAgICAgIHJldHVybiAndGFnJztcbiAgICAgICAgfVxuICAgICAgICBjdXIgPSBzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCk7XG4gICAgICAgIHN0eWxlID0gcmVnaXN0ZXJzW2N1cl07XG4gICAgICAgIHJldHVybiBzdHlsZSB8fCBudWxsO1xuICAgICAgfVxuICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBjdXN0b20ubGVuZ3RoOyBpKyspIHtcbiAgICAgICAgc3R5bGUgPSBjdXN0b21baV0oY2gsIHN0cmVhbSwgc3RhdGUpO1xuICAgICAgICBpZiAoc3R5bGUpIHtcbiAgICAgICAgICByZXR1cm4gc3R5bGU7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9LFxuICAgIGxhbmd1YWdlRGF0YToge1xuICAgICAgY29tbWVudFRva2Vuczoge1xuICAgICAgICBsaW5lOiBsaW5lQ29tbWVudFN0YXJ0U3ltYm9sLFxuICAgICAgICBibG9jazoge1xuICAgICAgICAgIG9wZW46IFwiLypcIixcbiAgICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gIH07XG59XG47XG5leHBvcnQgY29uc3QgZ2FzID0gbWtHYXMoXCJ4ODZcIik7XG5leHBvcnQgY29uc3QgZ2FzQXJtID0gbWtHYXMoXCJhcm1cIik7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==