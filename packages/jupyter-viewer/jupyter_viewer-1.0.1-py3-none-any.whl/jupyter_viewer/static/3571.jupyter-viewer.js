"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3571],{

/***/ 41660
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   I: () => (/* binding */ simpleMode)
/* harmony export */ });
function simpleMode(states) {
  ensureState(states, "start");
  var states_ = {},
    meta = states.languageData || {},
    hasIndentation = false;
  for (var state in states) if (state != meta && states.hasOwnProperty(state)) {
    var list = states_[state] = [],
      orig = states[state];
    for (var i = 0; i < orig.length; i++) {
      var data = orig[i];
      list.push(new Rule(data, states));
      if (data.indent || data.dedent) hasIndentation = true;
    }
  }
  return {
    name: meta.name,
    startState: function () {
      return {
        state: "start",
        pending: null,
        indent: hasIndentation ? [] : null
      };
    },
    copyState: function (state) {
      var s = {
        state: state.state,
        pending: state.pending,
        indent: state.indent && state.indent.slice(0)
      };
      if (state.stack) s.stack = state.stack.slice(0);
      return s;
    },
    token: tokenFunction(states_),
    indent: indentFunction(states_, meta),
    mergeTokens: meta.mergeTokens,
    languageData: meta
  };
}
;
function ensureState(states, name) {
  if (!states.hasOwnProperty(name)) throw new Error("Undefined state " + name + " in simple mode");
}
function toRegex(val, caret) {
  if (!val) return /(?:)/;
  var flags = "";
  if (val instanceof RegExp) {
    if (val.ignoreCase) flags = "i";
    if (val.unicode) flags += "u";
    val = val.source;
  } else {
    val = String(val);
  }
  return new RegExp((caret === false ? "" : "^") + "(?:" + val + ")", flags);
}
function asToken(val) {
  if (!val) return null;
  if (val.apply) return val;
  if (typeof val == "string") return val.replace(/\./g, " ");
  var result = [];
  for (var i = 0; i < val.length; i++) result.push(val[i] && val[i].replace(/\./g, " "));
  return result;
}
function Rule(data, states) {
  if (data.next || data.push) ensureState(states, data.next || data.push);
  this.regex = toRegex(data.regex);
  this.token = asToken(data.token);
  this.data = data;
}
function tokenFunction(states) {
  return function (stream, state) {
    if (state.pending) {
      var pend = state.pending.shift();
      if (state.pending.length == 0) state.pending = null;
      stream.pos += pend.text.length;
      return pend.token;
    }
    var curState = states[state.state];
    for (var i = 0; i < curState.length; i++) {
      var rule = curState[i];
      var matches = (!rule.data.sol || stream.sol()) && stream.match(rule.regex);
      if (matches) {
        if (rule.data.next) {
          state.state = rule.data.next;
        } else if (rule.data.push) {
          (state.stack || (state.stack = [])).push(state.state);
          state.state = rule.data.push;
        } else if (rule.data.pop && state.stack && state.stack.length) {
          state.state = state.stack.pop();
        }
        if (rule.data.indent) state.indent.push(stream.indentation() + stream.indentUnit);
        if (rule.data.dedent) state.indent.pop();
        var token = rule.token;
        if (token && token.apply) token = token(matches);
        if (matches.length > 2 && rule.token && typeof rule.token != "string") {
          state.pending = [];
          for (var j = 2; j < matches.length; j++) if (matches[j]) state.pending.push({
            text: matches[j],
            token: rule.token[j - 1]
          });
          stream.backUp(matches[0].length - (matches[1] ? matches[1].length : 0));
          return token[0];
        } else if (token && token.join) {
          return token[0];
        } else {
          return token;
        }
      }
    }
    stream.next();
    return null;
  };
}
function indentFunction(states, meta) {
  return function (state, textAfter) {
    if (state.indent == null || meta.dontIndentStates && meta.dontIndentStates.indexOf(state.state) > -1) return null;
    var pos = state.indent.length - 1,
      rules = states[state.state];
    scan: for (;;) {
      for (var i = 0; i < rules.length; i++) {
        var rule = rules[i];
        if (rule.data.dedent && rule.data.dedentIfLineStart !== false) {
          var m = rule.regex.exec(textAfter);
          if (m && m[0]) {
            pos--;
            if (rule.next || rule.push) rules = states[rule.next || rule.push];
            textAfter = textAfter.slice(m[0].length);
            continue scan;
          }
        }
      }
      break;
    }
    return pos < 0 ? 0 : state.indent[pos];
  };
}

/***/ },

/***/ 73571
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   nsis: () => (/* binding */ nsis)
/* harmony export */ });
/* harmony import */ var _simple_mode_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(41660);

const nsis = (0,_simple_mode_js__WEBPACK_IMPORTED_MODULE_0__/* .simpleMode */ .I)({
  start: [
  // Numbers
  {
    regex: /(?:[+-]?)(?:0x[\d,a-f]+)|(?:0o[0-7]+)|(?:0b[0,1]+)|(?:\d+.?\d*)/,
    token: "number"
  },
  // Strings
  {
    regex: /"(?:[^\\"]|\\.)*"?/,
    token: "string"
  }, {
    regex: /'(?:[^\\']|\\.)*'?/,
    token: "string"
  }, {
    regex: /`(?:[^\\`]|\\.)*`?/,
    token: "string"
  },
  // Compile Time Commands
  {
    regex: /^\s*(?:\!(addincludedir|addplugindir|appendfile|assert|cd|define|delfile|echo|error|execute|finalize|getdllversion|gettlbversion|include|insertmacro|macro|macroend|makensis|packhdr|pragma|searchparse|searchreplace|system|tempfile|undef|uninstfinalize|verbose|warning))\b/i,
    token: "keyword"
  },
  // Conditional Compilation
  {
    regex: /^\s*(?:\!(if(?:n?def)?|ifmacron?def|macro))\b/i,
    token: "keyword",
    indent: true
  }, {
    regex: /^\s*(?:\!(else|endif|macroend))\b/i,
    token: "keyword",
    dedent: true
  },
  // Runtime Commands
  {
    regex: /^\s*(?:Abort|AddBrandingImage|AddSize|AllowRootDirInstall|AllowSkipFiles|AutoCloseWindow|BGFont|BGGradient|BrandingText|BringToFront|Call|CallInstDLL|Caption|ChangeUI|CheckBitmap|ClearErrors|CompletedText|ComponentText|CopyFiles|CRCCheck|CreateDirectory|CreateFont|CreateShortCut|Delete|DeleteINISec|DeleteINIStr|DeleteRegKey|DeleteRegValue|DetailPrint|DetailsButtonText|DirText|DirVar|DirVerify|EnableWindow|EnumRegKey|EnumRegValue|Exch|Exec|ExecShell|ExecShellWait|ExecWait|ExpandEnvStrings|File|FileBufSize|FileClose|FileErrorText|FileOpen|FileRead|FileReadByte|FileReadUTF16LE|FileReadWord|FileWriteUTF16LE|FileSeek|FileWrite|FileWriteByte|FileWriteWord|FindClose|FindFirst|FindNext|FindWindow|FlushINI|GetCurInstType|GetCurrentAddress|GetDlgItem|GetDLLVersion|GetDLLVersionLocal|GetErrorLevel|GetFileTime|GetFileTimeLocal|GetFullPathName|GetFunctionAddress|GetInstDirError|GetKnownFolderPath|GetLabelAddress|GetTempFileName|GetWinVer|Goto|HideWindow|Icon|IfAbort|IfErrors|IfFileExists|IfRebootFlag|IfRtlLanguage|IfShellVarContextAll|IfSilent|InitPluginsDir|InstallButtonText|InstallColors|InstallDir|InstallDirRegKey|InstProgressFlags|InstType|InstTypeGetText|InstTypeSetText|Int64Cmp|Int64CmpU|Int64Fmt|IntCmp|IntCmpU|IntFmt|IntOp|IntPtrCmp|IntPtrCmpU|IntPtrOp|IsWindow|LangString|LicenseBkColor|LicenseData|LicenseForceSelection|LicenseLangString|LicenseText|LoadAndSetImage|LoadLanguageFile|LockWindow|LogSet|LogText|ManifestDPIAware|ManifestLongPathAware|ManifestMaxVersionTested|ManifestSupportedOS|MessageBox|MiscButtonText|Name|Nop|OutFile|Page|PageCallbacks|PEAddResource|PEDllCharacteristics|PERemoveResource|PESubsysVer|Pop|Push|Quit|ReadEnvStr|ReadINIStr|ReadRegDWORD|ReadRegStr|Reboot|RegDLL|Rename|RequestExecutionLevel|ReserveFile|Return|RMDir|SearchPath|SectionGetFlags|SectionGetInstTypes|SectionGetSize|SectionGetText|SectionIn|SectionSetFlags|SectionSetInstTypes|SectionSetSize|SectionSetText|SendMessage|SetAutoClose|SetBrandingImage|SetCompress|SetCompressor|SetCompressorDictSize|SetCtlColors|SetCurInstType|SetDatablockOptimize|SetDateSave|SetDetailsPrint|SetDetailsView|SetErrorLevel|SetErrors|SetFileAttributes|SetFont|SetOutPath|SetOverwrite|SetRebootFlag|SetRegView|SetShellVarContext|SetSilent|ShowInstDetails|ShowUninstDetails|ShowWindow|SilentInstall|SilentUnInstall|Sleep|SpaceTexts|StrCmp|StrCmpS|StrCpy|StrLen|SubCaption|Target|Unicode|UninstallButtonText|UninstallCaption|UninstallIcon|UninstallSubCaption|UninstallText|UninstPage|UnRegDLL|Var|VIAddVersionKey|VIFileVersion|VIProductVersion|WindowIcon|WriteINIStr|WriteRegBin|WriteRegDWORD|WriteRegExpandStr|WriteRegMultiStr|WriteRegNone|WriteRegStr|WriteUninstaller|XPStyle)\b/i,
    token: "keyword"
  }, {
    regex: /^\s*(?:Function|PageEx|Section(?:Group)?)\b/i,
    token: "keyword",
    indent: true
  }, {
    regex: /^\s*(?:(Function|PageEx|Section(?:Group)?)End)\b/i,
    token: "keyword",
    dedent: true
  },
  // Command Options
  {
    regex: /\b(?:ARCHIVE|FILE_ATTRIBUTE_ARCHIVE|FILE_ATTRIBUTE_HIDDEN|FILE_ATTRIBUTE_NORMAL|FILE_ATTRIBUTE_OFFLINE|FILE_ATTRIBUTE_READONLY|FILE_ATTRIBUTE_SYSTEM|FILE_ATTRIBUTE_TEMPORARY|HIDDEN|HKCC|HKCR(32|64)?|HKCU(32|64)?|HKDD|HKEY_CLASSES_ROOT|HKEY_CURRENT_CONFIG|HKEY_CURRENT_USER|HKEY_DYN_DATA|HKEY_LOCAL_MACHINE|HKEY_PERFORMANCE_DATA|HKEY_USERS|HKLM(32|64)?|HKPD|HKU|IDABORT|IDCANCEL|IDD_DIR|IDD_INST|IDD_INSTFILES|IDD_LICENSE|IDD_SELCOM|IDD_UNINST|IDD_VERIFY|IDIGNORE|IDNO|IDOK|IDRETRY|IDYES|MB_ABORTRETRYIGNORE|MB_DEFBUTTON1|MB_DEFBUTTON2|MB_DEFBUTTON3|MB_DEFBUTTON4|MB_ICONEXCLAMATION|MB_ICONINFORMATION|MB_ICONQUESTION|MB_ICONSTOP|MB_OK|MB_OKCANCEL|MB_RETRYCANCEL|MB_RIGHT|MB_RTLREADING|MB_SETFOREGROUND|MB_TOPMOST|MB_USERICON|MB_YESNO|MB_YESNOCANCEL|NORMAL|OFFLINE|READONLY|SHCTX|SHELL_CONTEXT|SW_HIDE|SW_SHOWDEFAULT|SW_SHOWMAXIMIZED|SW_SHOWMINIMIZED|SW_SHOWNORMAL|SYSTEM|TEMPORARY)\b/i,
    token: "atom"
  }, {
    regex: /\b(?:admin|all|amd64-unicode|auto|both|bottom|bzip2|components|current|custom|directory|false|force|hide|highest|ifdiff|ifnewer|instfiles|lastused|leave|left|license|listonly|lzma|nevershow|none|normal|notset|off|on|right|show|silent|silentlog|textonly|top|true|try|un\.components|un\.custom|un\.directory|un\.instfiles|un\.license|uninstConfirm|user|Win10|Win7|Win8|WinVista|x-86-(ansi|unicode)|zlib)\b/i,
    token: "builtin"
  },
  // LogicLib.nsh
  {
    regex: /\$\{(?:And(?:If(?:Not)?|Unless)|Break|Case(?:2|3|4|5|Else)?|Continue|Default|Do(?:Until|While)?|Else(?:If(?:Not)?|Unless)?|End(?:If|Select|Switch)|Exit(?:Do|For|While)|For(?:Each)?|If(?:Cmd|Not(?:Then)?|Then)?|Loop(?:Until|While)?|Or(?:If(?:Not)?|Unless)|Select|Switch|Unless|While)\}/i,
    token: "variable-2",
    indent: true
  },
  // FileFunc.nsh
  {
    regex: /\$\{(?:BannerTrimPath|DirState|DriveSpace|Get(BaseName|Drives|ExeName|ExePath|FileAttributes|FileExt|FileName|FileVersion|Options|OptionsS|Parameters|Parent|Root|Size|Time)|Locate|RefreshShellIcons)\}/i,
    token: "variable-2",
    dedent: true
  },
  // Memento.nsh
  {
    regex: /\$\{(?:Memento(?:Section(?:Done|End|Restore|Save)?|UnselectedSection))\}/i,
    token: "variable-2",
    dedent: true
  },
  // TextFunc.nsh
  {
    regex: /\$\{(?:Config(?:Read|ReadS|Write|WriteS)|File(?:Join|ReadFromEnd|Recode)|Line(?:Find|Read|Sum)|Text(?:Compare|CompareS)|TrimNewLines)\}/i,
    token: "variable-2",
    dedent: true
  },
  // WinVer.nsh
  {
    regex: /\$\{(?:(?:At(?:Least|Most)|Is)(?:ServicePack|Win(?:7|8|10|95|98|200(?:0|3|8(?:R2)?)|ME|NT4|Vista|XP))|Is(?:NT|Server))\}/i,
    token: "variable",
    dedent: true
  },
  // WordFunc.nsh
  {
    regex: /\$\{(?:StrFilterS?|Version(?:Compare|Convert)|Word(?:AddS?|Find(?:(?:2|3)X)?S?|InsertS?|ReplaceS?))\}/i,
    token: "keyword",
    dedent: true
  },
  // x64.nsh
  {
    regex: /\$\{(?:RunningX64)\}/i,
    token: "variable",
    dedent: true
  }, {
    regex: /\$\{(?:Disable|Enable)X64FSRedirection\}/i,
    token: "keyword",
    dedent: true
  },
  // Line Comment
  {
    regex: /(#|;).*/,
    token: "comment"
  },
  // Block Comment
  {
    regex: /\/\*/,
    token: "comment",
    next: "comment"
  },
  // Operator
  {
    regex: /[-+\/*=<>!]+/,
    token: "operator"
  },
  // Variable
  {
    regex: /\$\w[\w\.]*/,
    token: "variable"
  },
  // Constant
  {
    regex: /\${[\!\w\.:-]+}/,
    token: "variableName.constant"
  },
  // Language String
  {
    regex: /\$\([\!\w\.:-]+\)/,
    token: "atom"
  }],
  comment: [{
    regex: /.*?\*\//,
    token: "comment",
    next: "start"
  }, {
    regex: /.*/,
    token: "comment"
  }],
  languageData: {
    name: "nsis",
    indentOnInput: /^\s*((Function|PageEx|Section|Section(Group)?)End|(\!(endif|macroend))|\$\{(End(If|Unless|While)|Loop(Until)|Next)\})$/i,
    commentTokens: {
      line: "#",
      block: {
        open: "/*",
        close: "*/"
      }
    }
  }
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzU3MS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7Ozs7O0FDdElBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3NpbXBsZS1tb2RlLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvbnNpcy5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgZnVuY3Rpb24gc2ltcGxlTW9kZShzdGF0ZXMpIHtcbiAgZW5zdXJlU3RhdGUoc3RhdGVzLCBcInN0YXJ0XCIpO1xuICB2YXIgc3RhdGVzXyA9IHt9LFxuICAgIG1ldGEgPSBzdGF0ZXMubGFuZ3VhZ2VEYXRhIHx8IHt9LFxuICAgIGhhc0luZGVudGF0aW9uID0gZmFsc2U7XG4gIGZvciAodmFyIHN0YXRlIGluIHN0YXRlcykgaWYgKHN0YXRlICE9IG1ldGEgJiYgc3RhdGVzLmhhc093blByb3BlcnR5KHN0YXRlKSkge1xuICAgIHZhciBsaXN0ID0gc3RhdGVzX1tzdGF0ZV0gPSBbXSxcbiAgICAgIG9yaWcgPSBzdGF0ZXNbc3RhdGVdO1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgb3JpZy5sZW5ndGg7IGkrKykge1xuICAgICAgdmFyIGRhdGEgPSBvcmlnW2ldO1xuICAgICAgbGlzdC5wdXNoKG5ldyBSdWxlKGRhdGEsIHN0YXRlcykpO1xuICAgICAgaWYgKGRhdGEuaW5kZW50IHx8IGRhdGEuZGVkZW50KSBoYXNJbmRlbnRhdGlvbiA9IHRydWU7XG4gICAgfVxuICB9XG4gIHJldHVybiB7XG4gICAgbmFtZTogbWV0YS5uYW1lLFxuICAgIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHN0YXRlOiBcInN0YXJ0XCIsXG4gICAgICAgIHBlbmRpbmc6IG51bGwsXG4gICAgICAgIGluZGVudDogaGFzSW5kZW50YXRpb24gPyBbXSA6IG51bGxcbiAgICAgIH07XG4gICAgfSxcbiAgICBjb3B5U3RhdGU6IGZ1bmN0aW9uIChzdGF0ZSkge1xuICAgICAgdmFyIHMgPSB7XG4gICAgICAgIHN0YXRlOiBzdGF0ZS5zdGF0ZSxcbiAgICAgICAgcGVuZGluZzogc3RhdGUucGVuZGluZyxcbiAgICAgICAgaW5kZW50OiBzdGF0ZS5pbmRlbnQgJiYgc3RhdGUuaW5kZW50LnNsaWNlKDApXG4gICAgICB9O1xuICAgICAgaWYgKHN0YXRlLnN0YWNrKSBzLnN0YWNrID0gc3RhdGUuc3RhY2suc2xpY2UoMCk7XG4gICAgICByZXR1cm4gcztcbiAgICB9LFxuICAgIHRva2VuOiB0b2tlbkZ1bmN0aW9uKHN0YXRlc18pLFxuICAgIGluZGVudDogaW5kZW50RnVuY3Rpb24oc3RhdGVzXywgbWV0YSksXG4gICAgbWVyZ2VUb2tlbnM6IG1ldGEubWVyZ2VUb2tlbnMsXG4gICAgbGFuZ3VhZ2VEYXRhOiBtZXRhXG4gIH07XG59XG47XG5mdW5jdGlvbiBlbnN1cmVTdGF0ZShzdGF0ZXMsIG5hbWUpIHtcbiAgaWYgKCFzdGF0ZXMuaGFzT3duUHJvcGVydHkobmFtZSkpIHRocm93IG5ldyBFcnJvcihcIlVuZGVmaW5lZCBzdGF0ZSBcIiArIG5hbWUgKyBcIiBpbiBzaW1wbGUgbW9kZVwiKTtcbn1cbmZ1bmN0aW9uIHRvUmVnZXgodmFsLCBjYXJldCkge1xuICBpZiAoIXZhbCkgcmV0dXJuIC8oPzopLztcbiAgdmFyIGZsYWdzID0gXCJcIjtcbiAgaWYgKHZhbCBpbnN0YW5jZW9mIFJlZ0V4cCkge1xuICAgIGlmICh2YWwuaWdub3JlQ2FzZSkgZmxhZ3MgPSBcImlcIjtcbiAgICBpZiAodmFsLnVuaWNvZGUpIGZsYWdzICs9IFwidVwiO1xuICAgIHZhbCA9IHZhbC5zb3VyY2U7XG4gIH0gZWxzZSB7XG4gICAgdmFsID0gU3RyaW5nKHZhbCk7XG4gIH1cbiAgcmV0dXJuIG5ldyBSZWdFeHAoKGNhcmV0ID09PSBmYWxzZSA/IFwiXCIgOiBcIl5cIikgKyBcIig/OlwiICsgdmFsICsgXCIpXCIsIGZsYWdzKTtcbn1cbmZ1bmN0aW9uIGFzVG9rZW4odmFsKSB7XG4gIGlmICghdmFsKSByZXR1cm4gbnVsbDtcbiAgaWYgKHZhbC5hcHBseSkgcmV0dXJuIHZhbDtcbiAgaWYgKHR5cGVvZiB2YWwgPT0gXCJzdHJpbmdcIikgcmV0dXJuIHZhbC5yZXBsYWNlKC9cXC4vZywgXCIgXCIpO1xuICB2YXIgcmVzdWx0ID0gW107XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgdmFsLmxlbmd0aDsgaSsrKSByZXN1bHQucHVzaCh2YWxbaV0gJiYgdmFsW2ldLnJlcGxhY2UoL1xcLi9nLCBcIiBcIikpO1xuICByZXR1cm4gcmVzdWx0O1xufVxuZnVuY3Rpb24gUnVsZShkYXRhLCBzdGF0ZXMpIHtcbiAgaWYgKGRhdGEubmV4dCB8fCBkYXRhLnB1c2gpIGVuc3VyZVN0YXRlKHN0YXRlcywgZGF0YS5uZXh0IHx8IGRhdGEucHVzaCk7XG4gIHRoaXMucmVnZXggPSB0b1JlZ2V4KGRhdGEucmVnZXgpO1xuICB0aGlzLnRva2VuID0gYXNUb2tlbihkYXRhLnRva2VuKTtcbiAgdGhpcy5kYXRhID0gZGF0YTtcbn1cbmZ1bmN0aW9uIHRva2VuRnVuY3Rpb24oc3RhdGVzKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdGF0ZS5wZW5kaW5nKSB7XG4gICAgICB2YXIgcGVuZCA9IHN0YXRlLnBlbmRpbmcuc2hpZnQoKTtcbiAgICAgIGlmIChzdGF0ZS5wZW5kaW5nLmxlbmd0aCA9PSAwKSBzdGF0ZS5wZW5kaW5nID0gbnVsbDtcbiAgICAgIHN0cmVhbS5wb3MgKz0gcGVuZC50ZXh0Lmxlbmd0aDtcbiAgICAgIHJldHVybiBwZW5kLnRva2VuO1xuICAgIH1cbiAgICB2YXIgY3VyU3RhdGUgPSBzdGF0ZXNbc3RhdGUuc3RhdGVdO1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgY3VyU3RhdGUubGVuZ3RoOyBpKyspIHtcbiAgICAgIHZhciBydWxlID0gY3VyU3RhdGVbaV07XG4gICAgICB2YXIgbWF0Y2hlcyA9ICghcnVsZS5kYXRhLnNvbCB8fCBzdHJlYW0uc29sKCkpICYmIHN0cmVhbS5tYXRjaChydWxlLnJlZ2V4KTtcbiAgICAgIGlmIChtYXRjaGVzKSB7XG4gICAgICAgIGlmIChydWxlLmRhdGEubmV4dCkge1xuICAgICAgICAgIHN0YXRlLnN0YXRlID0gcnVsZS5kYXRhLm5leHQ7XG4gICAgICAgIH0gZWxzZSBpZiAocnVsZS5kYXRhLnB1c2gpIHtcbiAgICAgICAgICAoc3RhdGUuc3RhY2sgfHwgKHN0YXRlLnN0YWNrID0gW10pKS5wdXNoKHN0YXRlLnN0YXRlKTtcbiAgICAgICAgICBzdGF0ZS5zdGF0ZSA9IHJ1bGUuZGF0YS5wdXNoO1xuICAgICAgICB9IGVsc2UgaWYgKHJ1bGUuZGF0YS5wb3AgJiYgc3RhdGUuc3RhY2sgJiYgc3RhdGUuc3RhY2subGVuZ3RoKSB7XG4gICAgICAgICAgc3RhdGUuc3RhdGUgPSBzdGF0ZS5zdGFjay5wb3AoKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAocnVsZS5kYXRhLmluZGVudCkgc3RhdGUuaW5kZW50LnB1c2goc3RyZWFtLmluZGVudGF0aW9uKCkgKyBzdHJlYW0uaW5kZW50VW5pdCk7XG4gICAgICAgIGlmIChydWxlLmRhdGEuZGVkZW50KSBzdGF0ZS5pbmRlbnQucG9wKCk7XG4gICAgICAgIHZhciB0b2tlbiA9IHJ1bGUudG9rZW47XG4gICAgICAgIGlmICh0b2tlbiAmJiB0b2tlbi5hcHBseSkgdG9rZW4gPSB0b2tlbihtYXRjaGVzKTtcbiAgICAgICAgaWYgKG1hdGNoZXMubGVuZ3RoID4gMiAmJiBydWxlLnRva2VuICYmIHR5cGVvZiBydWxlLnRva2VuICE9IFwic3RyaW5nXCIpIHtcbiAgICAgICAgICBzdGF0ZS5wZW5kaW5nID0gW107XG4gICAgICAgICAgZm9yICh2YXIgaiA9IDI7IGogPCBtYXRjaGVzLmxlbmd0aDsgaisrKSBpZiAobWF0Y2hlc1tqXSkgc3RhdGUucGVuZGluZy5wdXNoKHtcbiAgICAgICAgICAgIHRleHQ6IG1hdGNoZXNbal0sXG4gICAgICAgICAgICB0b2tlbjogcnVsZS50b2tlbltqIC0gMV1cbiAgICAgICAgICB9KTtcbiAgICAgICAgICBzdHJlYW0uYmFja1VwKG1hdGNoZXNbMF0ubGVuZ3RoIC0gKG1hdGNoZXNbMV0gPyBtYXRjaGVzWzFdLmxlbmd0aCA6IDApKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5bMF07XG4gICAgICAgIH0gZWxzZSBpZiAodG9rZW4gJiYgdG9rZW4uam9pbikge1xuICAgICAgICAgIHJldHVybiB0b2tlblswXTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW47XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfTtcbn1cbmZ1bmN0aW9uIGluZGVudEZ1bmN0aW9uKHN0YXRlcywgbWV0YSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIpIHtcbiAgICBpZiAoc3RhdGUuaW5kZW50ID09IG51bGwgfHwgbWV0YS5kb250SW5kZW50U3RhdGVzICYmIG1ldGEuZG9udEluZGVudFN0YXRlcy5pbmRleE9mKHN0YXRlLnN0YXRlKSA+IC0xKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgcG9zID0gc3RhdGUuaW5kZW50Lmxlbmd0aCAtIDEsXG4gICAgICBydWxlcyA9IHN0YXRlc1tzdGF0ZS5zdGF0ZV07XG4gICAgc2NhbjogZm9yICg7Oykge1xuICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBydWxlcy5sZW5ndGg7IGkrKykge1xuICAgICAgICB2YXIgcnVsZSA9IHJ1bGVzW2ldO1xuICAgICAgICBpZiAocnVsZS5kYXRhLmRlZGVudCAmJiBydWxlLmRhdGEuZGVkZW50SWZMaW5lU3RhcnQgIT09IGZhbHNlKSB7XG4gICAgICAgICAgdmFyIG0gPSBydWxlLnJlZ2V4LmV4ZWModGV4dEFmdGVyKTtcbiAgICAgICAgICBpZiAobSAmJiBtWzBdKSB7XG4gICAgICAgICAgICBwb3MtLTtcbiAgICAgICAgICAgIGlmIChydWxlLm5leHQgfHwgcnVsZS5wdXNoKSBydWxlcyA9IHN0YXRlc1tydWxlLm5leHQgfHwgcnVsZS5wdXNoXTtcbiAgICAgICAgICAgIHRleHRBZnRlciA9IHRleHRBZnRlci5zbGljZShtWzBdLmxlbmd0aCk7XG4gICAgICAgICAgICBjb250aW51ZSBzY2FuO1xuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIHJldHVybiBwb3MgPCAwID8gMCA6IHN0YXRlLmluZGVudFtwb3NdO1xuICB9O1xufSIsImltcG9ydCB7IHNpbXBsZU1vZGUgfSBmcm9tIFwiLi9zaW1wbGUtbW9kZS5qc1wiO1xuZXhwb3J0IGNvbnN0IG5zaXMgPSBzaW1wbGVNb2RlKHtcbiAgc3RhcnQ6IFtcbiAgLy8gTnVtYmVyc1xuICB7XG4gICAgcmVnZXg6IC8oPzpbKy1dPykoPzoweFtcXGQsYS1mXSspfCg/OjBvWzAtN10rKXwoPzowYlswLDFdKyl8KD86XFxkKy4/XFxkKikvLFxuICAgIHRva2VuOiBcIm51bWJlclwiXG4gIH0sXG4gIC8vIFN0cmluZ3NcbiAge1xuICAgIHJlZ2V4OiAvXCIoPzpbXlxcXFxcIl18XFxcXC4pKlwiPy8sXG4gICAgdG9rZW46IFwic3RyaW5nXCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvJyg/OlteXFxcXCddfFxcXFwuKSonPy8sXG4gICAgdG9rZW46IFwic3RyaW5nXCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvYCg/OlteXFxcXGBdfFxcXFwuKSpgPy8sXG4gICAgdG9rZW46IFwic3RyaW5nXCJcbiAgfSxcbiAgLy8gQ29tcGlsZSBUaW1lIENvbW1hbmRzXG4gIHtcbiAgICByZWdleDogL15cXHMqKD86XFwhKGFkZGluY2x1ZGVkaXJ8YWRkcGx1Z2luZGlyfGFwcGVuZGZpbGV8YXNzZXJ0fGNkfGRlZmluZXxkZWxmaWxlfGVjaG98ZXJyb3J8ZXhlY3V0ZXxmaW5hbGl6ZXxnZXRkbGx2ZXJzaW9ufGdldHRsYnZlcnNpb258aW5jbHVkZXxpbnNlcnRtYWNyb3xtYWNyb3xtYWNyb2VuZHxtYWtlbnNpc3xwYWNraGRyfHByYWdtYXxzZWFyY2hwYXJzZXxzZWFyY2hyZXBsYWNlfHN5c3RlbXx0ZW1wZmlsZXx1bmRlZnx1bmluc3RmaW5hbGl6ZXx2ZXJib3NlfHdhcm5pbmcpKVxcYi9pLFxuICAgIHRva2VuOiBcImtleXdvcmRcIlxuICB9LFxuICAvLyBDb25kaXRpb25hbCBDb21waWxhdGlvblxuICB7XG4gICAgcmVnZXg6IC9eXFxzKig/OlxcIShpZig/Om4/ZGVmKT98aWZtYWNyb24/ZGVmfG1hY3JvKSlcXGIvaSxcbiAgICB0b2tlbjogXCJrZXl3b3JkXCIsXG4gICAgaW5kZW50OiB0cnVlXG4gIH0sIHtcbiAgICByZWdleDogL15cXHMqKD86XFwhKGVsc2V8ZW5kaWZ8bWFjcm9lbmQpKVxcYi9pLFxuICAgIHRva2VuOiBcImtleXdvcmRcIixcbiAgICBkZWRlbnQ6IHRydWVcbiAgfSxcbiAgLy8gUnVudGltZSBDb21tYW5kc1xuICB7XG4gICAgcmVnZXg6IC9eXFxzKig/OkFib3J0fEFkZEJyYW5kaW5nSW1hZ2V8QWRkU2l6ZXxBbGxvd1Jvb3REaXJJbnN0YWxsfEFsbG93U2tpcEZpbGVzfEF1dG9DbG9zZVdpbmRvd3xCR0ZvbnR8QkdHcmFkaWVudHxCcmFuZGluZ1RleHR8QnJpbmdUb0Zyb250fENhbGx8Q2FsbEluc3RETEx8Q2FwdGlvbnxDaGFuZ2VVSXxDaGVja0JpdG1hcHxDbGVhckVycm9yc3xDb21wbGV0ZWRUZXh0fENvbXBvbmVudFRleHR8Q29weUZpbGVzfENSQ0NoZWNrfENyZWF0ZURpcmVjdG9yeXxDcmVhdGVGb250fENyZWF0ZVNob3J0Q3V0fERlbGV0ZXxEZWxldGVJTklTZWN8RGVsZXRlSU5JU3RyfERlbGV0ZVJlZ0tleXxEZWxldGVSZWdWYWx1ZXxEZXRhaWxQcmludHxEZXRhaWxzQnV0dG9uVGV4dHxEaXJUZXh0fERpclZhcnxEaXJWZXJpZnl8RW5hYmxlV2luZG93fEVudW1SZWdLZXl8RW51bVJlZ1ZhbHVlfEV4Y2h8RXhlY3xFeGVjU2hlbGx8RXhlY1NoZWxsV2FpdHxFeGVjV2FpdHxFeHBhbmRFbnZTdHJpbmdzfEZpbGV8RmlsZUJ1ZlNpemV8RmlsZUNsb3NlfEZpbGVFcnJvclRleHR8RmlsZU9wZW58RmlsZVJlYWR8RmlsZVJlYWRCeXRlfEZpbGVSZWFkVVRGMTZMRXxGaWxlUmVhZFdvcmR8RmlsZVdyaXRlVVRGMTZMRXxGaWxlU2Vla3xGaWxlV3JpdGV8RmlsZVdyaXRlQnl0ZXxGaWxlV3JpdGVXb3JkfEZpbmRDbG9zZXxGaW5kRmlyc3R8RmluZE5leHR8RmluZFdpbmRvd3xGbHVzaElOSXxHZXRDdXJJbnN0VHlwZXxHZXRDdXJyZW50QWRkcmVzc3xHZXREbGdJdGVtfEdldERMTFZlcnNpb258R2V0RExMVmVyc2lvbkxvY2FsfEdldEVycm9yTGV2ZWx8R2V0RmlsZVRpbWV8R2V0RmlsZVRpbWVMb2NhbHxHZXRGdWxsUGF0aE5hbWV8R2V0RnVuY3Rpb25BZGRyZXNzfEdldEluc3REaXJFcnJvcnxHZXRLbm93bkZvbGRlclBhdGh8R2V0TGFiZWxBZGRyZXNzfEdldFRlbXBGaWxlTmFtZXxHZXRXaW5WZXJ8R290b3xIaWRlV2luZG93fEljb258SWZBYm9ydHxJZkVycm9yc3xJZkZpbGVFeGlzdHN8SWZSZWJvb3RGbGFnfElmUnRsTGFuZ3VhZ2V8SWZTaGVsbFZhckNvbnRleHRBbGx8SWZTaWxlbnR8SW5pdFBsdWdpbnNEaXJ8SW5zdGFsbEJ1dHRvblRleHR8SW5zdGFsbENvbG9yc3xJbnN0YWxsRGlyfEluc3RhbGxEaXJSZWdLZXl8SW5zdFByb2dyZXNzRmxhZ3N8SW5zdFR5cGV8SW5zdFR5cGVHZXRUZXh0fEluc3RUeXBlU2V0VGV4dHxJbnQ2NENtcHxJbnQ2NENtcFV8SW50NjRGbXR8SW50Q21wfEludENtcFV8SW50Rm10fEludE9wfEludFB0ckNtcHxJbnRQdHJDbXBVfEludFB0ck9wfElzV2luZG93fExhbmdTdHJpbmd8TGljZW5zZUJrQ29sb3J8TGljZW5zZURhdGF8TGljZW5zZUZvcmNlU2VsZWN0aW9ufExpY2Vuc2VMYW5nU3RyaW5nfExpY2Vuc2VUZXh0fExvYWRBbmRTZXRJbWFnZXxMb2FkTGFuZ3VhZ2VGaWxlfExvY2tXaW5kb3d8TG9nU2V0fExvZ1RleHR8TWFuaWZlc3REUElBd2FyZXxNYW5pZmVzdExvbmdQYXRoQXdhcmV8TWFuaWZlc3RNYXhWZXJzaW9uVGVzdGVkfE1hbmlmZXN0U3VwcG9ydGVkT1N8TWVzc2FnZUJveHxNaXNjQnV0dG9uVGV4dHxOYW1lfE5vcHxPdXRGaWxlfFBhZ2V8UGFnZUNhbGxiYWNrc3xQRUFkZFJlc291cmNlfFBFRGxsQ2hhcmFjdGVyaXN0aWNzfFBFUmVtb3ZlUmVzb3VyY2V8UEVTdWJzeXNWZXJ8UG9wfFB1c2h8UXVpdHxSZWFkRW52U3RyfFJlYWRJTklTdHJ8UmVhZFJlZ0RXT1JEfFJlYWRSZWdTdHJ8UmVib290fFJlZ0RMTHxSZW5hbWV8UmVxdWVzdEV4ZWN1dGlvbkxldmVsfFJlc2VydmVGaWxlfFJldHVybnxSTURpcnxTZWFyY2hQYXRofFNlY3Rpb25HZXRGbGFnc3xTZWN0aW9uR2V0SW5zdFR5cGVzfFNlY3Rpb25HZXRTaXplfFNlY3Rpb25HZXRUZXh0fFNlY3Rpb25JbnxTZWN0aW9uU2V0RmxhZ3N8U2VjdGlvblNldEluc3RUeXBlc3xTZWN0aW9uU2V0U2l6ZXxTZWN0aW9uU2V0VGV4dHxTZW5kTWVzc2FnZXxTZXRBdXRvQ2xvc2V8U2V0QnJhbmRpbmdJbWFnZXxTZXRDb21wcmVzc3xTZXRDb21wcmVzc29yfFNldENvbXByZXNzb3JEaWN0U2l6ZXxTZXRDdGxDb2xvcnN8U2V0Q3VySW5zdFR5cGV8U2V0RGF0YWJsb2NrT3B0aW1pemV8U2V0RGF0ZVNhdmV8U2V0RGV0YWlsc1ByaW50fFNldERldGFpbHNWaWV3fFNldEVycm9yTGV2ZWx8U2V0RXJyb3JzfFNldEZpbGVBdHRyaWJ1dGVzfFNldEZvbnR8U2V0T3V0UGF0aHxTZXRPdmVyd3JpdGV8U2V0UmVib290RmxhZ3xTZXRSZWdWaWV3fFNldFNoZWxsVmFyQ29udGV4dHxTZXRTaWxlbnR8U2hvd0luc3REZXRhaWxzfFNob3dVbmluc3REZXRhaWxzfFNob3dXaW5kb3d8U2lsZW50SW5zdGFsbHxTaWxlbnRVbkluc3RhbGx8U2xlZXB8U3BhY2VUZXh0c3xTdHJDbXB8U3RyQ21wU3xTdHJDcHl8U3RyTGVufFN1YkNhcHRpb258VGFyZ2V0fFVuaWNvZGV8VW5pbnN0YWxsQnV0dG9uVGV4dHxVbmluc3RhbGxDYXB0aW9ufFVuaW5zdGFsbEljb258VW5pbnN0YWxsU3ViQ2FwdGlvbnxVbmluc3RhbGxUZXh0fFVuaW5zdFBhZ2V8VW5SZWdETEx8VmFyfFZJQWRkVmVyc2lvbktleXxWSUZpbGVWZXJzaW9ufFZJUHJvZHVjdFZlcnNpb258V2luZG93SWNvbnxXcml0ZUlOSVN0cnxXcml0ZVJlZ0JpbnxXcml0ZVJlZ0RXT1JEfFdyaXRlUmVnRXhwYW5kU3RyfFdyaXRlUmVnTXVsdGlTdHJ8V3JpdGVSZWdOb25lfFdyaXRlUmVnU3RyfFdyaXRlVW5pbnN0YWxsZXJ8WFBTdHlsZSlcXGIvaSxcbiAgICB0b2tlbjogXCJrZXl3b3JkXCJcbiAgfSwge1xuICAgIHJlZ2V4OiAvXlxccyooPzpGdW5jdGlvbnxQYWdlRXh8U2VjdGlvbig/Okdyb3VwKT8pXFxiL2ksXG4gICAgdG9rZW46IFwia2V5d29yZFwiLFxuICAgIGluZGVudDogdHJ1ZVxuICB9LCB7XG4gICAgcmVnZXg6IC9eXFxzKig/OihGdW5jdGlvbnxQYWdlRXh8U2VjdGlvbig/Okdyb3VwKT8pRW5kKVxcYi9pLFxuICAgIHRva2VuOiBcImtleXdvcmRcIixcbiAgICBkZWRlbnQ6IHRydWVcbiAgfSxcbiAgLy8gQ29tbWFuZCBPcHRpb25zXG4gIHtcbiAgICByZWdleDogL1xcYig/OkFSQ0hJVkV8RklMRV9BVFRSSUJVVEVfQVJDSElWRXxGSUxFX0FUVFJJQlVURV9ISURERU58RklMRV9BVFRSSUJVVEVfTk9STUFMfEZJTEVfQVRUUklCVVRFX09GRkxJTkV8RklMRV9BVFRSSUJVVEVfUkVBRE9OTFl8RklMRV9BVFRSSUJVVEVfU1lTVEVNfEZJTEVfQVRUUklCVVRFX1RFTVBPUkFSWXxISURERU58SEtDQ3xIS0NSKDMyfDY0KT98SEtDVSgzMnw2NCk/fEhLRER8SEtFWV9DTEFTU0VTX1JPT1R8SEtFWV9DVVJSRU5UX0NPTkZJR3xIS0VZX0NVUlJFTlRfVVNFUnxIS0VZX0RZTl9EQVRBfEhLRVlfTE9DQUxfTUFDSElORXxIS0VZX1BFUkZPUk1BTkNFX0RBVEF8SEtFWV9VU0VSU3xIS0xNKDMyfDY0KT98SEtQRHxIS1V8SURBQk9SVHxJRENBTkNFTHxJRERfRElSfElERF9JTlNUfElERF9JTlNURklMRVN8SUREX0xJQ0VOU0V8SUREX1NFTENPTXxJRERfVU5JTlNUfElERF9WRVJJRll8SURJR05PUkV8SUROT3xJRE9LfElEUkVUUll8SURZRVN8TUJfQUJPUlRSRVRSWUlHTk9SRXxNQl9ERUZCVVRUT04xfE1CX0RFRkJVVFRPTjJ8TUJfREVGQlVUVE9OM3xNQl9ERUZCVVRUT040fE1CX0lDT05FWENMQU1BVElPTnxNQl9JQ09OSU5GT1JNQVRJT058TUJfSUNPTlFVRVNUSU9OfE1CX0lDT05TVE9QfE1CX09LfE1CX09LQ0FOQ0VMfE1CX1JFVFJZQ0FOQ0VMfE1CX1JJR0hUfE1CX1JUTFJFQURJTkd8TUJfU0VURk9SRUdST1VORHxNQl9UT1BNT1NUfE1CX1VTRVJJQ09OfE1CX1lFU05PfE1CX1lFU05PQ0FOQ0VMfE5PUk1BTHxPRkZMSU5FfFJFQURPTkxZfFNIQ1RYfFNIRUxMX0NPTlRFWFR8U1dfSElERXxTV19TSE9XREVGQVVMVHxTV19TSE9XTUFYSU1JWkVEfFNXX1NIT1dNSU5JTUlaRUR8U1dfU0hPV05PUk1BTHxTWVNURU18VEVNUE9SQVJZKVxcYi9pLFxuICAgIHRva2VuOiBcImF0b21cIlxuICB9LCB7XG4gICAgcmVnZXg6IC9cXGIoPzphZG1pbnxhbGx8YW1kNjQtdW5pY29kZXxhdXRvfGJvdGh8Ym90dG9tfGJ6aXAyfGNvbXBvbmVudHN8Y3VycmVudHxjdXN0b218ZGlyZWN0b3J5fGZhbHNlfGZvcmNlfGhpZGV8aGlnaGVzdHxpZmRpZmZ8aWZuZXdlcnxpbnN0ZmlsZXN8bGFzdHVzZWR8bGVhdmV8bGVmdHxsaWNlbnNlfGxpc3Rvbmx5fGx6bWF8bmV2ZXJzaG93fG5vbmV8bm9ybWFsfG5vdHNldHxvZmZ8b258cmlnaHR8c2hvd3xzaWxlbnR8c2lsZW50bG9nfHRleHRvbmx5fHRvcHx0cnVlfHRyeXx1blxcLmNvbXBvbmVudHN8dW5cXC5jdXN0b218dW5cXC5kaXJlY3Rvcnl8dW5cXC5pbnN0ZmlsZXN8dW5cXC5saWNlbnNlfHVuaW5zdENvbmZpcm18dXNlcnxXaW4xMHxXaW43fFdpbjh8V2luVmlzdGF8eC04Ni0oYW5zaXx1bmljb2RlKXx6bGliKVxcYi9pLFxuICAgIHRva2VuOiBcImJ1aWx0aW5cIlxuICB9LFxuICAvLyBMb2dpY0xpYi5uc2hcbiAge1xuICAgIHJlZ2V4OiAvXFwkXFx7KD86QW5kKD86SWYoPzpOb3QpP3xVbmxlc3MpfEJyZWFrfENhc2UoPzoyfDN8NHw1fEVsc2UpP3xDb250aW51ZXxEZWZhdWx0fERvKD86VW50aWx8V2hpbGUpP3xFbHNlKD86SWYoPzpOb3QpP3xVbmxlc3MpP3xFbmQoPzpJZnxTZWxlY3R8U3dpdGNoKXxFeGl0KD86RG98Rm9yfFdoaWxlKXxGb3IoPzpFYWNoKT98SWYoPzpDbWR8Tm90KD86VGhlbik/fFRoZW4pP3xMb29wKD86VW50aWx8V2hpbGUpP3xPcig/OklmKD86Tm90KT98VW5sZXNzKXxTZWxlY3R8U3dpdGNofFVubGVzc3xXaGlsZSlcXH0vaSxcbiAgICB0b2tlbjogXCJ2YXJpYWJsZS0yXCIsXG4gICAgaW5kZW50OiB0cnVlXG4gIH0sXG4gIC8vIEZpbGVGdW5jLm5zaFxuICB7XG4gICAgcmVnZXg6IC9cXCRcXHsoPzpCYW5uZXJUcmltUGF0aHxEaXJTdGF0ZXxEcml2ZVNwYWNlfEdldChCYXNlTmFtZXxEcml2ZXN8RXhlTmFtZXxFeGVQYXRofEZpbGVBdHRyaWJ1dGVzfEZpbGVFeHR8RmlsZU5hbWV8RmlsZVZlcnNpb258T3B0aW9uc3xPcHRpb25zU3xQYXJhbWV0ZXJzfFBhcmVudHxSb290fFNpemV8VGltZSl8TG9jYXRlfFJlZnJlc2hTaGVsbEljb25zKVxcfS9pLFxuICAgIHRva2VuOiBcInZhcmlhYmxlLTJcIixcbiAgICBkZWRlbnQ6IHRydWVcbiAgfSxcbiAgLy8gTWVtZW50by5uc2hcbiAge1xuICAgIHJlZ2V4OiAvXFwkXFx7KD86TWVtZW50byg/OlNlY3Rpb24oPzpEb25lfEVuZHxSZXN0b3JlfFNhdmUpP3xVbnNlbGVjdGVkU2VjdGlvbikpXFx9L2ksXG4gICAgdG9rZW46IFwidmFyaWFibGUtMlwiLFxuICAgIGRlZGVudDogdHJ1ZVxuICB9LFxuICAvLyBUZXh0RnVuYy5uc2hcbiAge1xuICAgIHJlZ2V4OiAvXFwkXFx7KD86Q29uZmlnKD86UmVhZHxSZWFkU3xXcml0ZXxXcml0ZVMpfEZpbGUoPzpKb2lufFJlYWRGcm9tRW5kfFJlY29kZSl8TGluZSg/OkZpbmR8UmVhZHxTdW0pfFRleHQoPzpDb21wYXJlfENvbXBhcmVTKXxUcmltTmV3TGluZXMpXFx9L2ksXG4gICAgdG9rZW46IFwidmFyaWFibGUtMlwiLFxuICAgIGRlZGVudDogdHJ1ZVxuICB9LFxuICAvLyBXaW5WZXIubnNoXG4gIHtcbiAgICByZWdleDogL1xcJFxceyg/Oig/OkF0KD86TGVhc3R8TW9zdCl8SXMpKD86U2VydmljZVBhY2t8V2luKD86N3w4fDEwfDk1fDk4fDIwMCg/OjB8M3w4KD86UjIpPyl8TUV8TlQ0fFZpc3RhfFhQKSl8SXMoPzpOVHxTZXJ2ZXIpKVxcfS9pLFxuICAgIHRva2VuOiBcInZhcmlhYmxlXCIsXG4gICAgZGVkZW50OiB0cnVlXG4gIH0sXG4gIC8vIFdvcmRGdW5jLm5zaFxuICB7XG4gICAgcmVnZXg6IC9cXCRcXHsoPzpTdHJGaWx0ZXJTP3xWZXJzaW9uKD86Q29tcGFyZXxDb252ZXJ0KXxXb3JkKD86QWRkUz98RmluZCg/Oig/OjJ8MylYKT9TP3xJbnNlcnRTP3xSZXBsYWNlUz8pKVxcfS9pLFxuICAgIHRva2VuOiBcImtleXdvcmRcIixcbiAgICBkZWRlbnQ6IHRydWVcbiAgfSxcbiAgLy8geDY0Lm5zaFxuICB7XG4gICAgcmVnZXg6IC9cXCRcXHsoPzpSdW5uaW5nWDY0KVxcfS9pLFxuICAgIHRva2VuOiBcInZhcmlhYmxlXCIsXG4gICAgZGVkZW50OiB0cnVlXG4gIH0sIHtcbiAgICByZWdleDogL1xcJFxceyg/OkRpc2FibGV8RW5hYmxlKVg2NEZTUmVkaXJlY3Rpb25cXH0vaSxcbiAgICB0b2tlbjogXCJrZXl3b3JkXCIsXG4gICAgZGVkZW50OiB0cnVlXG4gIH0sXG4gIC8vIExpbmUgQ29tbWVudFxuICB7XG4gICAgcmVnZXg6IC8oI3w7KS4qLyxcbiAgICB0b2tlbjogXCJjb21tZW50XCJcbiAgfSxcbiAgLy8gQmxvY2sgQ29tbWVudFxuICB7XG4gICAgcmVnZXg6IC9cXC9cXCovLFxuICAgIHRva2VuOiBcImNvbW1lbnRcIixcbiAgICBuZXh0OiBcImNvbW1lbnRcIlxuICB9LFxuICAvLyBPcGVyYXRvclxuICB7XG4gICAgcmVnZXg6IC9bLStcXC8qPTw+IV0rLyxcbiAgICB0b2tlbjogXCJvcGVyYXRvclwiXG4gIH0sXG4gIC8vIFZhcmlhYmxlXG4gIHtcbiAgICByZWdleDogL1xcJFxcd1tcXHdcXC5dKi8sXG4gICAgdG9rZW46IFwidmFyaWFibGVcIlxuICB9LFxuICAvLyBDb25zdGFudFxuICB7XG4gICAgcmVnZXg6IC9cXCR7W1xcIVxcd1xcLjotXSt9LyxcbiAgICB0b2tlbjogXCJ2YXJpYWJsZU5hbWUuY29uc3RhbnRcIlxuICB9LFxuICAvLyBMYW5ndWFnZSBTdHJpbmdcbiAge1xuICAgIHJlZ2V4OiAvXFwkXFwoW1xcIVxcd1xcLjotXStcXCkvLFxuICAgIHRva2VuOiBcImF0b21cIlxuICB9XSxcbiAgY29tbWVudDogW3tcbiAgICByZWdleDogLy4qP1xcKlxcLy8sXG4gICAgdG9rZW46IFwiY29tbWVudFwiLFxuICAgIG5leHQ6IFwic3RhcnRcIlxuICB9LCB7XG4gICAgcmVnZXg6IC8uKi8sXG4gICAgdG9rZW46IFwiY29tbWVudFwiXG4gIH1dLFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBuYW1lOiBcIm5zaXNcIixcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccyooKEZ1bmN0aW9ufFBhZ2VFeHxTZWN0aW9ufFNlY3Rpb24oR3JvdXApPylFbmR8KFxcIShlbmRpZnxtYWNyb2VuZCkpfFxcJFxceyhFbmQoSWZ8VW5sZXNzfFdoaWxlKXxMb29wKFVudGlsKXxOZXh0KVxcfSkkL2ksXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIjXCIsXG4gICAgICBibG9jazoge1xuICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgIH1cbiAgICB9XG4gIH1cbn0pOyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=