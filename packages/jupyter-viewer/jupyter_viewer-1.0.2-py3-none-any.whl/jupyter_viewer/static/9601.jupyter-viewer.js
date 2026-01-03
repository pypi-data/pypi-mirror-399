"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9601],{

/***/ 49601
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   powerShell: () => (/* binding */ powerShell)
/* harmony export */ });
function buildRegexp(patterns, options) {
  options = options || {};
  var prefix = options.prefix !== undefined ? options.prefix : '^';
  var suffix = options.suffix !== undefined ? options.suffix : '\\b';
  for (var i = 0; i < patterns.length; i++) {
    if (patterns[i] instanceof RegExp) {
      patterns[i] = patterns[i].source;
    } else {
      patterns[i] = patterns[i].replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    }
  }
  return new RegExp(prefix + '(' + patterns.join('|') + ')' + suffix, 'i');
}
var notCharacterOrDash = '(?=[^A-Za-z\\d\\-_]|$)';
var varNames = /[\w\-:]/;
var keywords = buildRegexp([/begin|break|catch|continue|data|default|do|dynamicparam/, /else|elseif|end|exit|filter|finally|for|foreach|from|function|if|in/, /param|process|return|switch|throw|trap|try|until|where|while/], {
  suffix: notCharacterOrDash
});
var punctuation = /[\[\]{},;`\\\.]|@[({]/;
var wordOperators = buildRegexp(['f', /b?not/, /[ic]?split/, 'join', /is(not)?/, 'as', /[ic]?(eq|ne|[gl][te])/, /[ic]?(not)?(like|match|contains)/, /[ic]?replace/, /b?(and|or|xor)/], {
  prefix: '-'
});
var symbolOperators = /[+\-*\/%]=|\+\+|--|\.\.|[+\-*&^%:=!|\/]|<(?!#)|(?!#)>/;
var operators = buildRegexp([wordOperators, symbolOperators], {
  suffix: ''
});
var numbers = /^((0x[\da-f]+)|((\d+\.\d+|\d\.|\.\d+|\d+)(e[\+\-]?\d+)?))[ld]?([kmgtp]b)?/i;
var identifiers = /^[A-Za-z\_][A-Za-z\-\_\d]*\b/;
var symbolBuiltins = /[A-Z]:|%|\?/i;
var namedBuiltins = buildRegexp([/Add-(Computer|Content|History|Member|PSSnapin|Type)/, /Checkpoint-Computer/, /Clear-(Content|EventLog|History|Host|Item(Property)?|Variable)/, /Compare-Object/, /Complete-Transaction/, /Connect-PSSession/, /ConvertFrom-(Csv|Json|SecureString|StringData)/, /Convert-Path/, /ConvertTo-(Csv|Html|Json|SecureString|Xml)/, /Copy-Item(Property)?/, /Debug-Process/, /Disable-(ComputerRestore|PSBreakpoint|PSRemoting|PSSessionConfiguration)/, /Disconnect-PSSession/, /Enable-(ComputerRestore|PSBreakpoint|PSRemoting|PSSessionConfiguration)/, /(Enter|Exit)-PSSession/, /Export-(Alias|Clixml|Console|Counter|Csv|FormatData|ModuleMember|PSSession)/, /ForEach-Object/, /Format-(Custom|List|Table|Wide)/, new RegExp('Get-(Acl|Alias|AuthenticodeSignature|ChildItem|Command|ComputerRestorePoint|Content|ControlPanelItem|Counter|Credential' + '|Culture|Date|Event|EventLog|EventSubscriber|ExecutionPolicy|FormatData|Help|History|Host|HotFix|Item|ItemProperty|Job' + '|Location|Member|Module|PfxCertificate|Process|PSBreakpoint|PSCallStack|PSDrive|PSProvider|PSSession|PSSessionConfiguration' + '|PSSnapin|Random|Service|TraceSource|Transaction|TypeData|UICulture|Unique|Variable|Verb|WinEvent|WmiObject)'), /Group-Object/, /Import-(Alias|Clixml|Counter|Csv|LocalizedData|Module|PSSession)/, /ImportSystemModules/, /Invoke-(Command|Expression|History|Item|RestMethod|WebRequest|WmiMethod)/, /Join-Path/, /Limit-EventLog/, /Measure-(Command|Object)/, /Move-Item(Property)?/, new RegExp('New-(Alias|Event|EventLog|Item(Property)?|Module|ModuleManifest|Object|PSDrive|PSSession|PSSessionConfigurationFile' + '|PSSessionOption|PSTransportOption|Service|TimeSpan|Variable|WebServiceProxy|WinEvent)'), /Out-(Default|File|GridView|Host|Null|Printer|String)/, /Pause/, /(Pop|Push)-Location/, /Read-Host/, /Receive-(Job|PSSession)/, /Register-(EngineEvent|ObjectEvent|PSSessionConfiguration|WmiEvent)/, /Remove-(Computer|Event|EventLog|Item(Property)?|Job|Module|PSBreakpoint|PSDrive|PSSession|PSSnapin|TypeData|Variable|WmiObject)/, /Rename-(Computer|Item(Property)?)/, /Reset-ComputerMachinePassword/, /Resolve-Path/, /Restart-(Computer|Service)/, /Restore-Computer/, /Resume-(Job|Service)/, /Save-Help/, /Select-(Object|String|Xml)/, /Send-MailMessage/, new RegExp('Set-(Acl|Alias|AuthenticodeSignature|Content|Date|ExecutionPolicy|Item(Property)?|Location|PSBreakpoint|PSDebug' + '|PSSessionConfiguration|Service|StrictMode|TraceSource|Variable|WmiInstance)'), /Show-(Command|ControlPanelItem|EventLog)/, /Sort-Object/, /Split-Path/, /Start-(Job|Process|Service|Sleep|Transaction|Transcript)/, /Stop-(Computer|Job|Process|Service|Transcript)/, /Suspend-(Job|Service)/, /TabExpansion2/, /Tee-Object/, /Test-(ComputerSecureChannel|Connection|ModuleManifest|Path|PSSessionConfigurationFile)/, /Trace-Command/, /Unblock-File/, /Undo-Transaction/, /Unregister-(Event|PSSessionConfiguration)/, /Update-(FormatData|Help|List|TypeData)/, /Use-Transaction/, /Wait-(Event|Job|Process)/, /Where-Object/, /Write-(Debug|Error|EventLog|Host|Output|Progress|Verbose|Warning)/, /cd|help|mkdir|more|oss|prompt/, /ac|asnp|cat|cd|chdir|clc|clear|clhy|cli|clp|cls|clv|cnsn|compare|copy|cp|cpi|cpp|cvpa|dbp|del|diff|dir|dnsn|ebp/, /echo|epal|epcsv|epsn|erase|etsn|exsn|fc|fl|foreach|ft|fw|gal|gbp|gc|gci|gcm|gcs|gdr|ghy|gi|gjb|gl|gm|gmo|gp|gps/, /group|gsn|gsnp|gsv|gu|gv|gwmi|h|history|icm|iex|ihy|ii|ipal|ipcsv|ipmo|ipsn|irm|ise|iwmi|iwr|kill|lp|ls|man|md/, /measure|mi|mount|move|mp|mv|nal|ndr|ni|nmo|npssc|nsn|nv|ogv|oh|popd|ps|pushd|pwd|r|rbp|rcjb|rcsn|rd|rdr|ren|ri/, /rjb|rm|rmdir|rmo|rni|rnp|rp|rsn|rsnp|rujb|rv|rvpa|rwmi|sajb|sal|saps|sasv|sbp|sc|select|set|shcm|si|sl|sleep|sls/, /sort|sp|spjb|spps|spsv|start|sujb|sv|swmi|tee|trcm|type|where|wjb|write/], {
  prefix: '',
  suffix: ''
});
var variableBuiltins = buildRegexp([/[$?^_]|Args|ConfirmPreference|ConsoleFileName|DebugPreference|Error|ErrorActionPreference|ErrorView|ExecutionContext/, /FormatEnumerationLimit|Home|Host|Input|MaximumAliasCount|MaximumDriveCount|MaximumErrorCount|MaximumFunctionCount/, /MaximumHistoryCount|MaximumVariableCount|MyInvocation|NestedPromptLevel|OutputEncoding|Pid|Profile|ProgressPreference/, /PSBoundParameters|PSCommandPath|PSCulture|PSDefaultParameterValues|PSEmailServer|PSHome|PSScriptRoot|PSSessionApplicationName/, /PSSessionConfigurationName|PSSessionOption|PSUICulture|PSVersionTable|Pwd|ShellId|StackTrace|VerbosePreference/, /WarningPreference|WhatIfPreference/, /Event|EventArgs|EventSubscriber|Sender/, /Matches|Ofs|ForEach|LastExitCode|PSCmdlet|PSItem|PSSenderInfo|This/, /true|false|null/], {
  prefix: '\\$',
  suffix: ''
});
var builtins = buildRegexp([symbolBuiltins, namedBuiltins, variableBuiltins], {
  suffix: notCharacterOrDash
});
var grammar = {
  keyword: keywords,
  number: numbers,
  operator: operators,
  builtin: builtins,
  punctuation: punctuation,
  variable: identifiers
};

// tokenizers
function tokenBase(stream, state) {
  // Handle Comments
  //var ch = stream.peek();

  var parent = state.returnStack[state.returnStack.length - 1];
  if (parent && parent.shouldReturnFrom(state)) {
    state.tokenize = parent.tokenize;
    state.returnStack.pop();
    return state.tokenize(stream, state);
  }
  if (stream.eatSpace()) {
    return null;
  }
  if (stream.eat('(')) {
    state.bracketNesting += 1;
    return 'punctuation';
  }
  if (stream.eat(')')) {
    state.bracketNesting -= 1;
    return 'punctuation';
  }
  for (var key in grammar) {
    if (stream.match(grammar[key])) {
      return key;
    }
  }
  var ch = stream.next();

  // single-quote string
  if (ch === "'") {
    return tokenSingleQuoteString(stream, state);
  }
  if (ch === '$') {
    return tokenVariable(stream, state);
  }

  // double-quote string
  if (ch === '"') {
    return tokenDoubleQuoteString(stream, state);
  }
  if (ch === '<' && stream.eat('#')) {
    state.tokenize = tokenComment;
    return tokenComment(stream, state);
  }
  if (ch === '#') {
    stream.skipToEnd();
    return 'comment';
  }
  if (ch === '@') {
    var quoteMatch = stream.eat(/["']/);
    if (quoteMatch && stream.eol()) {
      state.tokenize = tokenMultiString;
      state.startQuote = quoteMatch[0];
      return tokenMultiString(stream, state);
    } else if (stream.eol()) {
      return 'error';
    } else if (stream.peek().match(/[({]/)) {
      return 'punctuation';
    } else if (stream.peek().match(varNames)) {
      // splatted variable
      return tokenVariable(stream, state);
    }
  }
  return 'error';
}
function tokenSingleQuoteString(stream, state) {
  var ch;
  while ((ch = stream.peek()) != null) {
    stream.next();
    if (ch === "'" && !stream.eat("'")) {
      state.tokenize = tokenBase;
      return 'string';
    }
  }
  return 'error';
}
function tokenDoubleQuoteString(stream, state) {
  var ch;
  while ((ch = stream.peek()) != null) {
    if (ch === '$') {
      state.tokenize = tokenStringInterpolation;
      return 'string';
    }
    stream.next();
    if (ch === '`') {
      stream.next();
      continue;
    }
    if (ch === '"' && !stream.eat('"')) {
      state.tokenize = tokenBase;
      return 'string';
    }
  }
  return 'error';
}
function tokenStringInterpolation(stream, state) {
  return tokenInterpolation(stream, state, tokenDoubleQuoteString);
}
function tokenMultiStringReturn(stream, state) {
  state.tokenize = tokenMultiString;
  state.startQuote = '"';
  return tokenMultiString(stream, state);
}
function tokenHereStringInterpolation(stream, state) {
  return tokenInterpolation(stream, state, tokenMultiStringReturn);
}
function tokenInterpolation(stream, state, parentTokenize) {
  if (stream.match('$(')) {
    var savedBracketNesting = state.bracketNesting;
    state.returnStack.push({
      /*jshint loopfunc:true */
      shouldReturnFrom: function (state) {
        return state.bracketNesting === savedBracketNesting;
      },
      tokenize: parentTokenize
    });
    state.tokenize = tokenBase;
    state.bracketNesting += 1;
    return 'punctuation';
  } else {
    stream.next();
    state.returnStack.push({
      shouldReturnFrom: function () {
        return true;
      },
      tokenize: parentTokenize
    });
    state.tokenize = tokenVariable;
    return state.tokenize(stream, state);
  }
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while ((ch = stream.next()) != null) {
    if (maybeEnd && ch == '>') {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch === '#';
  }
  return 'comment';
}
function tokenVariable(stream, state) {
  var ch = stream.peek();
  if (stream.eat('{')) {
    state.tokenize = tokenVariableWithBraces;
    return tokenVariableWithBraces(stream, state);
  } else if (ch != undefined && ch.match(varNames)) {
    stream.eatWhile(varNames);
    state.tokenize = tokenBase;
    return 'variable';
  } else {
    state.tokenize = tokenBase;
    return 'error';
  }
}
function tokenVariableWithBraces(stream, state) {
  var ch;
  while ((ch = stream.next()) != null) {
    if (ch === '}') {
      state.tokenize = tokenBase;
      break;
    }
  }
  return 'variable';
}
function tokenMultiString(stream, state) {
  var quote = state.startQuote;
  if (stream.sol() && stream.match(new RegExp(quote + '@'))) {
    state.tokenize = tokenBase;
  } else if (quote === '"') {
    while (!stream.eol()) {
      var ch = stream.peek();
      if (ch === '$') {
        state.tokenize = tokenHereStringInterpolation;
        return 'string';
      }
      stream.next();
      if (ch === '`') {
        stream.next();
      }
    }
  } else {
    stream.skipToEnd();
  }
  return 'string';
}
const powerShell = {
  name: "powershell",
  startState: function () {
    return {
      returnStack: [],
      bracketNesting: 0,
      tokenize: tokenBase
    };
  },
  token: function (stream, state) {
    return state.tokenize(stream, state);
  },
  languageData: {
    commentTokens: {
      line: "#",
      block: {
        open: "<#",
        close: "#>"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTYwMS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9wb3dlcnNoZWxsLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIGJ1aWxkUmVnZXhwKHBhdHRlcm5zLCBvcHRpb25zKSB7XG4gIG9wdGlvbnMgPSBvcHRpb25zIHx8IHt9O1xuICB2YXIgcHJlZml4ID0gb3B0aW9ucy5wcmVmaXggIT09IHVuZGVmaW5lZCA/IG9wdGlvbnMucHJlZml4IDogJ14nO1xuICB2YXIgc3VmZml4ID0gb3B0aW9ucy5zdWZmaXggIT09IHVuZGVmaW5lZCA/IG9wdGlvbnMuc3VmZml4IDogJ1xcXFxiJztcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCBwYXR0ZXJucy5sZW5ndGg7IGkrKykge1xuICAgIGlmIChwYXR0ZXJuc1tpXSBpbnN0YW5jZW9mIFJlZ0V4cCkge1xuICAgICAgcGF0dGVybnNbaV0gPSBwYXR0ZXJuc1tpXS5zb3VyY2U7XG4gICAgfSBlbHNlIHtcbiAgICAgIHBhdHRlcm5zW2ldID0gcGF0dGVybnNbaV0ucmVwbGFjZSgvWy1cXC9cXFxcXiQqKz8uKCl8W1xcXXt9XS9nLCAnXFxcXCQmJyk7XG4gICAgfVxuICB9XG4gIHJldHVybiBuZXcgUmVnRXhwKHByZWZpeCArICcoJyArIHBhdHRlcm5zLmpvaW4oJ3wnKSArICcpJyArIHN1ZmZpeCwgJ2knKTtcbn1cbnZhciBub3RDaGFyYWN0ZXJPckRhc2ggPSAnKD89W15BLVphLXpcXFxcZFxcXFwtX118JCknO1xudmFyIHZhck5hbWVzID0gL1tcXHdcXC06XS87XG52YXIga2V5d29yZHMgPSBidWlsZFJlZ2V4cChbL2JlZ2lufGJyZWFrfGNhdGNofGNvbnRpbnVlfGRhdGF8ZGVmYXVsdHxkb3xkeW5hbWljcGFyYW0vLCAvZWxzZXxlbHNlaWZ8ZW5kfGV4aXR8ZmlsdGVyfGZpbmFsbHl8Zm9yfGZvcmVhY2h8ZnJvbXxmdW5jdGlvbnxpZnxpbi8sIC9wYXJhbXxwcm9jZXNzfHJldHVybnxzd2l0Y2h8dGhyb3d8dHJhcHx0cnl8dW50aWx8d2hlcmV8d2hpbGUvXSwge1xuICBzdWZmaXg6IG5vdENoYXJhY3Rlck9yRGFzaFxufSk7XG52YXIgcHVuY3R1YXRpb24gPSAvW1xcW1xcXXt9LDtgXFxcXFxcLl18QFsoe10vO1xudmFyIHdvcmRPcGVyYXRvcnMgPSBidWlsZFJlZ2V4cChbJ2YnLCAvYj9ub3QvLCAvW2ljXT9zcGxpdC8sICdqb2luJywgL2lzKG5vdCk/LywgJ2FzJywgL1tpY10/KGVxfG5lfFtnbF1bdGVdKS8sIC9baWNdPyhub3QpPyhsaWtlfG1hdGNofGNvbnRhaW5zKS8sIC9baWNdP3JlcGxhY2UvLCAvYj8oYW5kfG9yfHhvcikvXSwge1xuICBwcmVmaXg6ICctJ1xufSk7XG52YXIgc3ltYm9sT3BlcmF0b3JzID0gL1srXFwtKlxcLyVdPXxcXCtcXCt8LS18XFwuXFwufFsrXFwtKiZeJTo9IXxcXC9dfDwoPyEjKXwoPyEjKT4vO1xudmFyIG9wZXJhdG9ycyA9IGJ1aWxkUmVnZXhwKFt3b3JkT3BlcmF0b3JzLCBzeW1ib2xPcGVyYXRvcnNdLCB7XG4gIHN1ZmZpeDogJydcbn0pO1xudmFyIG51bWJlcnMgPSAvXigoMHhbXFxkYS1mXSspfCgoXFxkK1xcLlxcZCt8XFxkXFwufFxcLlxcZCt8XFxkKykoZVtcXCtcXC1dP1xcZCspPykpW2xkXT8oW2ttZ3RwXWIpPy9pO1xudmFyIGlkZW50aWZpZXJzID0gL15bQS1aYS16XFxfXVtBLVphLXpcXC1cXF9cXGRdKlxcYi87XG52YXIgc3ltYm9sQnVpbHRpbnMgPSAvW0EtWl06fCV8XFw/L2k7XG52YXIgbmFtZWRCdWlsdGlucyA9IGJ1aWxkUmVnZXhwKFsvQWRkLShDb21wdXRlcnxDb250ZW50fEhpc3Rvcnl8TWVtYmVyfFBTU25hcGlufFR5cGUpLywgL0NoZWNrcG9pbnQtQ29tcHV0ZXIvLCAvQ2xlYXItKENvbnRlbnR8RXZlbnRMb2d8SGlzdG9yeXxIb3N0fEl0ZW0oUHJvcGVydHkpP3xWYXJpYWJsZSkvLCAvQ29tcGFyZS1PYmplY3QvLCAvQ29tcGxldGUtVHJhbnNhY3Rpb24vLCAvQ29ubmVjdC1QU1Nlc3Npb24vLCAvQ29udmVydEZyb20tKENzdnxKc29ufFNlY3VyZVN0cmluZ3xTdHJpbmdEYXRhKS8sIC9Db252ZXJ0LVBhdGgvLCAvQ29udmVydFRvLShDc3Z8SHRtbHxKc29ufFNlY3VyZVN0cmluZ3xYbWwpLywgL0NvcHktSXRlbShQcm9wZXJ0eSk/LywgL0RlYnVnLVByb2Nlc3MvLCAvRGlzYWJsZS0oQ29tcHV0ZXJSZXN0b3JlfFBTQnJlYWtwb2ludHxQU1JlbW90aW5nfFBTU2Vzc2lvbkNvbmZpZ3VyYXRpb24pLywgL0Rpc2Nvbm5lY3QtUFNTZXNzaW9uLywgL0VuYWJsZS0oQ29tcHV0ZXJSZXN0b3JlfFBTQnJlYWtwb2ludHxQU1JlbW90aW5nfFBTU2Vzc2lvbkNvbmZpZ3VyYXRpb24pLywgLyhFbnRlcnxFeGl0KS1QU1Nlc3Npb24vLCAvRXhwb3J0LShBbGlhc3xDbGl4bWx8Q29uc29sZXxDb3VudGVyfENzdnxGb3JtYXREYXRhfE1vZHVsZU1lbWJlcnxQU1Nlc3Npb24pLywgL0ZvckVhY2gtT2JqZWN0LywgL0Zvcm1hdC0oQ3VzdG9tfExpc3R8VGFibGV8V2lkZSkvLCBuZXcgUmVnRXhwKCdHZXQtKEFjbHxBbGlhc3xBdXRoZW50aWNvZGVTaWduYXR1cmV8Q2hpbGRJdGVtfENvbW1hbmR8Q29tcHV0ZXJSZXN0b3JlUG9pbnR8Q29udGVudHxDb250cm9sUGFuZWxJdGVtfENvdW50ZXJ8Q3JlZGVudGlhbCcgKyAnfEN1bHR1cmV8RGF0ZXxFdmVudHxFdmVudExvZ3xFdmVudFN1YnNjcmliZXJ8RXhlY3V0aW9uUG9saWN5fEZvcm1hdERhdGF8SGVscHxIaXN0b3J5fEhvc3R8SG90Rml4fEl0ZW18SXRlbVByb3BlcnR5fEpvYicgKyAnfExvY2F0aW9ufE1lbWJlcnxNb2R1bGV8UGZ4Q2VydGlmaWNhdGV8UHJvY2Vzc3xQU0JyZWFrcG9pbnR8UFNDYWxsU3RhY2t8UFNEcml2ZXxQU1Byb3ZpZGVyfFBTU2Vzc2lvbnxQU1Nlc3Npb25Db25maWd1cmF0aW9uJyArICd8UFNTbmFwaW58UmFuZG9tfFNlcnZpY2V8VHJhY2VTb3VyY2V8VHJhbnNhY3Rpb258VHlwZURhdGF8VUlDdWx0dXJlfFVuaXF1ZXxWYXJpYWJsZXxWZXJifFdpbkV2ZW50fFdtaU9iamVjdCknKSwgL0dyb3VwLU9iamVjdC8sIC9JbXBvcnQtKEFsaWFzfENsaXhtbHxDb3VudGVyfENzdnxMb2NhbGl6ZWREYXRhfE1vZHVsZXxQU1Nlc3Npb24pLywgL0ltcG9ydFN5c3RlbU1vZHVsZXMvLCAvSW52b2tlLShDb21tYW5kfEV4cHJlc3Npb258SGlzdG9yeXxJdGVtfFJlc3RNZXRob2R8V2ViUmVxdWVzdHxXbWlNZXRob2QpLywgL0pvaW4tUGF0aC8sIC9MaW1pdC1FdmVudExvZy8sIC9NZWFzdXJlLShDb21tYW5kfE9iamVjdCkvLCAvTW92ZS1JdGVtKFByb3BlcnR5KT8vLCBuZXcgUmVnRXhwKCdOZXctKEFsaWFzfEV2ZW50fEV2ZW50TG9nfEl0ZW0oUHJvcGVydHkpP3xNb2R1bGV8TW9kdWxlTWFuaWZlc3R8T2JqZWN0fFBTRHJpdmV8UFNTZXNzaW9ufFBTU2Vzc2lvbkNvbmZpZ3VyYXRpb25GaWxlJyArICd8UFNTZXNzaW9uT3B0aW9ufFBTVHJhbnNwb3J0T3B0aW9ufFNlcnZpY2V8VGltZVNwYW58VmFyaWFibGV8V2ViU2VydmljZVByb3h5fFdpbkV2ZW50KScpLCAvT3V0LShEZWZhdWx0fEZpbGV8R3JpZFZpZXd8SG9zdHxOdWxsfFByaW50ZXJ8U3RyaW5nKS8sIC9QYXVzZS8sIC8oUG9wfFB1c2gpLUxvY2F0aW9uLywgL1JlYWQtSG9zdC8sIC9SZWNlaXZlLShKb2J8UFNTZXNzaW9uKS8sIC9SZWdpc3Rlci0oRW5naW5lRXZlbnR8T2JqZWN0RXZlbnR8UFNTZXNzaW9uQ29uZmlndXJhdGlvbnxXbWlFdmVudCkvLCAvUmVtb3ZlLShDb21wdXRlcnxFdmVudHxFdmVudExvZ3xJdGVtKFByb3BlcnR5KT98Sm9ifE1vZHVsZXxQU0JyZWFrcG9pbnR8UFNEcml2ZXxQU1Nlc3Npb258UFNTbmFwaW58VHlwZURhdGF8VmFyaWFibGV8V21pT2JqZWN0KS8sIC9SZW5hbWUtKENvbXB1dGVyfEl0ZW0oUHJvcGVydHkpPykvLCAvUmVzZXQtQ29tcHV0ZXJNYWNoaW5lUGFzc3dvcmQvLCAvUmVzb2x2ZS1QYXRoLywgL1Jlc3RhcnQtKENvbXB1dGVyfFNlcnZpY2UpLywgL1Jlc3RvcmUtQ29tcHV0ZXIvLCAvUmVzdW1lLShKb2J8U2VydmljZSkvLCAvU2F2ZS1IZWxwLywgL1NlbGVjdC0oT2JqZWN0fFN0cmluZ3xYbWwpLywgL1NlbmQtTWFpbE1lc3NhZ2UvLCBuZXcgUmVnRXhwKCdTZXQtKEFjbHxBbGlhc3xBdXRoZW50aWNvZGVTaWduYXR1cmV8Q29udGVudHxEYXRlfEV4ZWN1dGlvblBvbGljeXxJdGVtKFByb3BlcnR5KT98TG9jYXRpb258UFNCcmVha3BvaW50fFBTRGVidWcnICsgJ3xQU1Nlc3Npb25Db25maWd1cmF0aW9ufFNlcnZpY2V8U3RyaWN0TW9kZXxUcmFjZVNvdXJjZXxWYXJpYWJsZXxXbWlJbnN0YW5jZSknKSwgL1Nob3ctKENvbW1hbmR8Q29udHJvbFBhbmVsSXRlbXxFdmVudExvZykvLCAvU29ydC1PYmplY3QvLCAvU3BsaXQtUGF0aC8sIC9TdGFydC0oSm9ifFByb2Nlc3N8U2VydmljZXxTbGVlcHxUcmFuc2FjdGlvbnxUcmFuc2NyaXB0KS8sIC9TdG9wLShDb21wdXRlcnxKb2J8UHJvY2Vzc3xTZXJ2aWNlfFRyYW5zY3JpcHQpLywgL1N1c3BlbmQtKEpvYnxTZXJ2aWNlKS8sIC9UYWJFeHBhbnNpb24yLywgL1RlZS1PYmplY3QvLCAvVGVzdC0oQ29tcHV0ZXJTZWN1cmVDaGFubmVsfENvbm5lY3Rpb258TW9kdWxlTWFuaWZlc3R8UGF0aHxQU1Nlc3Npb25Db25maWd1cmF0aW9uRmlsZSkvLCAvVHJhY2UtQ29tbWFuZC8sIC9VbmJsb2NrLUZpbGUvLCAvVW5kby1UcmFuc2FjdGlvbi8sIC9VbnJlZ2lzdGVyLShFdmVudHxQU1Nlc3Npb25Db25maWd1cmF0aW9uKS8sIC9VcGRhdGUtKEZvcm1hdERhdGF8SGVscHxMaXN0fFR5cGVEYXRhKS8sIC9Vc2UtVHJhbnNhY3Rpb24vLCAvV2FpdC0oRXZlbnR8Sm9ifFByb2Nlc3MpLywgL1doZXJlLU9iamVjdC8sIC9Xcml0ZS0oRGVidWd8RXJyb3J8RXZlbnRMb2d8SG9zdHxPdXRwdXR8UHJvZ3Jlc3N8VmVyYm9zZXxXYXJuaW5nKS8sIC9jZHxoZWxwfG1rZGlyfG1vcmV8b3NzfHByb21wdC8sIC9hY3xhc25wfGNhdHxjZHxjaGRpcnxjbGN8Y2xlYXJ8Y2xoeXxjbGl8Y2xwfGNsc3xjbHZ8Y25zbnxjb21wYXJlfGNvcHl8Y3B8Y3BpfGNwcHxjdnBhfGRicHxkZWx8ZGlmZnxkaXJ8ZG5zbnxlYnAvLCAvZWNob3xlcGFsfGVwY3N2fGVwc258ZXJhc2V8ZXRzbnxleHNufGZjfGZsfGZvcmVhY2h8ZnR8Znd8Z2FsfGdicHxnY3xnY2l8Z2NtfGdjc3xnZHJ8Z2h5fGdpfGdqYnxnbHxnbXxnbW98Z3B8Z3BzLywgL2dyb3VwfGdzbnxnc25wfGdzdnxndXxndnxnd21pfGh8aGlzdG9yeXxpY218aWV4fGloeXxpaXxpcGFsfGlwY3N2fGlwbW98aXBzbnxpcm18aXNlfGl3bWl8aXdyfGtpbGx8bHB8bHN8bWFufG1kLywgL21lYXN1cmV8bWl8bW91bnR8bW92ZXxtcHxtdnxuYWx8bmRyfG5pfG5tb3xucHNzY3xuc258bnZ8b2d2fG9ofHBvcGR8cHN8cHVzaGR8cHdkfHJ8cmJwfHJjamJ8cmNzbnxyZHxyZHJ8cmVufHJpLywgL3JqYnxybXxybWRpcnxybW98cm5pfHJucHxycHxyc258cnNucHxydWpifHJ2fHJ2cGF8cndtaXxzYWpifHNhbHxzYXBzfHNhc3Z8c2JwfHNjfHNlbGVjdHxzZXR8c2hjbXxzaXxzbHxzbGVlcHxzbHMvLCAvc29ydHxzcHxzcGpifHNwcHN8c3BzdnxzdGFydHxzdWpifHN2fHN3bWl8dGVlfHRyY218dHlwZXx3aGVyZXx3amJ8d3JpdGUvXSwge1xuICBwcmVmaXg6ICcnLFxuICBzdWZmaXg6ICcnXG59KTtcbnZhciB2YXJpYWJsZUJ1aWx0aW5zID0gYnVpbGRSZWdleHAoWy9bJD9eX118QXJnc3xDb25maXJtUHJlZmVyZW5jZXxDb25zb2xlRmlsZU5hbWV8RGVidWdQcmVmZXJlbmNlfEVycm9yfEVycm9yQWN0aW9uUHJlZmVyZW5jZXxFcnJvclZpZXd8RXhlY3V0aW9uQ29udGV4dC8sIC9Gb3JtYXRFbnVtZXJhdGlvbkxpbWl0fEhvbWV8SG9zdHxJbnB1dHxNYXhpbXVtQWxpYXNDb3VudHxNYXhpbXVtRHJpdmVDb3VudHxNYXhpbXVtRXJyb3JDb3VudHxNYXhpbXVtRnVuY3Rpb25Db3VudC8sIC9NYXhpbXVtSGlzdG9yeUNvdW50fE1heGltdW1WYXJpYWJsZUNvdW50fE15SW52b2NhdGlvbnxOZXN0ZWRQcm9tcHRMZXZlbHxPdXRwdXRFbmNvZGluZ3xQaWR8UHJvZmlsZXxQcm9ncmVzc1ByZWZlcmVuY2UvLCAvUFNCb3VuZFBhcmFtZXRlcnN8UFNDb21tYW5kUGF0aHxQU0N1bHR1cmV8UFNEZWZhdWx0UGFyYW1ldGVyVmFsdWVzfFBTRW1haWxTZXJ2ZXJ8UFNIb21lfFBTU2NyaXB0Um9vdHxQU1Nlc3Npb25BcHBsaWNhdGlvbk5hbWUvLCAvUFNTZXNzaW9uQ29uZmlndXJhdGlvbk5hbWV8UFNTZXNzaW9uT3B0aW9ufFBTVUlDdWx0dXJlfFBTVmVyc2lvblRhYmxlfFB3ZHxTaGVsbElkfFN0YWNrVHJhY2V8VmVyYm9zZVByZWZlcmVuY2UvLCAvV2FybmluZ1ByZWZlcmVuY2V8V2hhdElmUHJlZmVyZW5jZS8sIC9FdmVudHxFdmVudEFyZ3N8RXZlbnRTdWJzY3JpYmVyfFNlbmRlci8sIC9NYXRjaGVzfE9mc3xGb3JFYWNofExhc3RFeGl0Q29kZXxQU0NtZGxldHxQU0l0ZW18UFNTZW5kZXJJbmZvfFRoaXMvLCAvdHJ1ZXxmYWxzZXxudWxsL10sIHtcbiAgcHJlZml4OiAnXFxcXCQnLFxuICBzdWZmaXg6ICcnXG59KTtcbnZhciBidWlsdGlucyA9IGJ1aWxkUmVnZXhwKFtzeW1ib2xCdWlsdGlucywgbmFtZWRCdWlsdGlucywgdmFyaWFibGVCdWlsdGluc10sIHtcbiAgc3VmZml4OiBub3RDaGFyYWN0ZXJPckRhc2hcbn0pO1xudmFyIGdyYW1tYXIgPSB7XG4gIGtleXdvcmQ6IGtleXdvcmRzLFxuICBudW1iZXI6IG51bWJlcnMsXG4gIG9wZXJhdG9yOiBvcGVyYXRvcnMsXG4gIGJ1aWx0aW46IGJ1aWx0aW5zLFxuICBwdW5jdHVhdGlvbjogcHVuY3R1YXRpb24sXG4gIHZhcmlhYmxlOiBpZGVudGlmaWVyc1xufTtcblxuLy8gdG9rZW5pemVyc1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgLy8gSGFuZGxlIENvbW1lbnRzXG4gIC8vdmFyIGNoID0gc3RyZWFtLnBlZWsoKTtcblxuICB2YXIgcGFyZW50ID0gc3RhdGUucmV0dXJuU3RhY2tbc3RhdGUucmV0dXJuU3RhY2subGVuZ3RoIC0gMV07XG4gIGlmIChwYXJlbnQgJiYgcGFyZW50LnNob3VsZFJldHVybkZyb20oc3RhdGUpKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSBwYXJlbnQudG9rZW5pemU7XG4gICAgc3RhdGUucmV0dXJuU3RhY2sucG9wKCk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmIChzdHJlYW0uZWF0KCcoJykpIHtcbiAgICBzdGF0ZS5icmFja2V0TmVzdGluZyArPSAxO1xuICAgIHJldHVybiAncHVuY3R1YXRpb24nO1xuICB9XG4gIGlmIChzdHJlYW0uZWF0KCcpJykpIHtcbiAgICBzdGF0ZS5icmFja2V0TmVzdGluZyAtPSAxO1xuICAgIHJldHVybiAncHVuY3R1YXRpb24nO1xuICB9XG4gIGZvciAodmFyIGtleSBpbiBncmFtbWFyKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChncmFtbWFyW2tleV0pKSB7XG4gICAgICByZXR1cm4ga2V5O1xuICAgIH1cbiAgfVxuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuXG4gIC8vIHNpbmdsZS1xdW90ZSBzdHJpbmdcbiAgaWYgKGNoID09PSBcIidcIikge1xuICAgIHJldHVybiB0b2tlblNpbmdsZVF1b3RlU3RyaW5nKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChjaCA9PT0gJyQnKSB7XG4gICAgcmV0dXJuIHRva2VuVmFyaWFibGUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cblxuICAvLyBkb3VibGUtcXVvdGUgc3RyaW5nXG4gIGlmIChjaCA9PT0gJ1wiJykge1xuICAgIHJldHVybiB0b2tlbkRvdWJsZVF1b3RlU3RyaW5nKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChjaCA9PT0gJzwnICYmIHN0cmVhbS5lYXQoJyMnKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Db21tZW50O1xuICAgIHJldHVybiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKGNoID09PSAnIycpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuICdjb21tZW50JztcbiAgfVxuICBpZiAoY2ggPT09ICdAJykge1xuICAgIHZhciBxdW90ZU1hdGNoID0gc3RyZWFtLmVhdCgvW1wiJ10vKTtcbiAgICBpZiAocXVvdGVNYXRjaCAmJiBzdHJlYW0uZW9sKCkpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5NdWx0aVN0cmluZztcbiAgICAgIHN0YXRlLnN0YXJ0UXVvdGUgPSBxdW90ZU1hdGNoWzBdO1xuICAgICAgcmV0dXJuIHRva2VuTXVsdGlTdHJpbmcoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0uZW9sKCkpIHtcbiAgICAgIHJldHVybiAnZXJyb3InO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKS5tYXRjaCgvWyh7XS8pKSB7XG4gICAgICByZXR1cm4gJ3B1bmN0dWF0aW9uJztcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5wZWVrKCkubWF0Y2godmFyTmFtZXMpKSB7XG4gICAgICAvLyBzcGxhdHRlZCB2YXJpYWJsZVxuICAgICAgcmV0dXJuIHRva2VuVmFyaWFibGUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICB9XG4gIHJldHVybiAnZXJyb3InO1xufVxuZnVuY3Rpb24gdG9rZW5TaW5nbGVRdW90ZVN0cmluZyhzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaDtcbiAgd2hpbGUgKChjaCA9IHN0cmVhbS5wZWVrKCkpICE9IG51bGwpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIGlmIChjaCA9PT0gXCInXCIgJiYgIXN0cmVhbS5lYXQoXCInXCIpKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIHJldHVybiAnc3RyaW5nJztcbiAgICB9XG4gIH1cbiAgcmV0dXJuICdlcnJvcic7XG59XG5mdW5jdGlvbiB0b2tlbkRvdWJsZVF1b3RlU3RyaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoO1xuICB3aGlsZSAoKGNoID0gc3RyZWFtLnBlZWsoKSkgIT0gbnVsbCkge1xuICAgIGlmIChjaCA9PT0gJyQnKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nSW50ZXJwb2xhdGlvbjtcbiAgICAgIHJldHVybiAnc3RyaW5nJztcbiAgICB9XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoY2ggPT09ICdgJykge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIGNvbnRpbnVlO1xuICAgIH1cbiAgICBpZiAoY2ggPT09ICdcIicgJiYgIXN0cmVhbS5lYXQoJ1wiJykpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgcmV0dXJuICdzdHJpbmcnO1xuICAgIH1cbiAgfVxuICByZXR1cm4gJ2Vycm9yJztcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nSW50ZXJwb2xhdGlvbihzdHJlYW0sIHN0YXRlKSB7XG4gIHJldHVybiB0b2tlbkludGVycG9sYXRpb24oc3RyZWFtLCBzdGF0ZSwgdG9rZW5Eb3VibGVRdW90ZVN0cmluZyk7XG59XG5mdW5jdGlvbiB0b2tlbk11bHRpU3RyaW5nUmV0dXJuKHN0cmVhbSwgc3RhdGUpIHtcbiAgc3RhdGUudG9rZW5pemUgPSB0b2tlbk11bHRpU3RyaW5nO1xuICBzdGF0ZS5zdGFydFF1b3RlID0gJ1wiJztcbiAgcmV0dXJuIHRva2VuTXVsdGlTdHJpbmcoc3RyZWFtLCBzdGF0ZSk7XG59XG5mdW5jdGlvbiB0b2tlbkhlcmVTdHJpbmdJbnRlcnBvbGF0aW9uKHN0cmVhbSwgc3RhdGUpIHtcbiAgcmV0dXJuIHRva2VuSW50ZXJwb2xhdGlvbihzdHJlYW0sIHN0YXRlLCB0b2tlbk11bHRpU3RyaW5nUmV0dXJuKTtcbn1cbmZ1bmN0aW9uIHRva2VuSW50ZXJwb2xhdGlvbihzdHJlYW0sIHN0YXRlLCBwYXJlbnRUb2tlbml6ZSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKCckKCcpKSB7XG4gICAgdmFyIHNhdmVkQnJhY2tldE5lc3RpbmcgPSBzdGF0ZS5icmFja2V0TmVzdGluZztcbiAgICBzdGF0ZS5yZXR1cm5TdGFjay5wdXNoKHtcbiAgICAgIC8qanNoaW50IGxvb3BmdW5jOnRydWUgKi9cbiAgICAgIHNob3VsZFJldHVybkZyb206IGZ1bmN0aW9uIChzdGF0ZSkge1xuICAgICAgICByZXR1cm4gc3RhdGUuYnJhY2tldE5lc3RpbmcgPT09IHNhdmVkQnJhY2tldE5lc3Rpbmc7XG4gICAgICB9LFxuICAgICAgdG9rZW5pemU6IHBhcmVudFRva2VuaXplXG4gICAgfSk7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgc3RhdGUuYnJhY2tldE5lc3RpbmcgKz0gMTtcbiAgICByZXR1cm4gJ3B1bmN0dWF0aW9uJztcbiAgfSBlbHNlIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHN0YXRlLnJldHVyblN0YWNrLnB1c2goe1xuICAgICAgc2hvdWxkUmV0dXJuRnJvbTogZnVuY3Rpb24gKCkge1xuICAgICAgICByZXR1cm4gdHJ1ZTtcbiAgICAgIH0sXG4gICAgICB0b2tlbml6ZTogcGFyZW50VG9rZW5pemVcbiAgICB9KTtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuVmFyaWFibGU7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG59XG5mdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAobWF5YmVFbmQgJiYgY2ggPT0gJz4nKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09PSAnIyc7XG4gIH1cbiAgcmV0dXJuICdjb21tZW50Jztcbn1cbmZ1bmN0aW9uIHRva2VuVmFyaWFibGUoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpO1xuICBpZiAoc3RyZWFtLmVhdCgneycpKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblZhcmlhYmxlV2l0aEJyYWNlcztcbiAgICByZXR1cm4gdG9rZW5WYXJpYWJsZVdpdGhCcmFjZXMoc3RyZWFtLCBzdGF0ZSk7XG4gIH0gZWxzZSBpZiAoY2ggIT0gdW5kZWZpbmVkICYmIGNoLm1hdGNoKHZhck5hbWVzKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSh2YXJOYW1lcyk7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuICd2YXJpYWJsZSc7XG4gIH0gZWxzZSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuICdlcnJvcic7XG4gIH1cbn1cbmZ1bmN0aW9uIHRva2VuVmFyaWFibGVXaXRoQnJhY2VzKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoO1xuICB3aGlsZSAoKGNoID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgIGlmIChjaCA9PT0gJ30nKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgfVxuICByZXR1cm4gJ3ZhcmlhYmxlJztcbn1cbmZ1bmN0aW9uIHRva2VuTXVsdGlTdHJpbmcoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgcXVvdGUgPSBzdGF0ZS5zdGFydFF1b3RlO1xuICBpZiAoc3RyZWFtLnNvbCgpICYmIHN0cmVhbS5tYXRjaChuZXcgUmVnRXhwKHF1b3RlICsgJ0AnKSkpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgfSBlbHNlIGlmIChxdW90ZSA9PT0gJ1wiJykge1xuICAgIHdoaWxlICghc3RyZWFtLmVvbCgpKSB7XG4gICAgICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpO1xuICAgICAgaWYgKGNoID09PSAnJCcpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkhlcmVTdHJpbmdJbnRlcnBvbGF0aW9uO1xuICAgICAgICByZXR1cm4gJ3N0cmluZyc7XG4gICAgICB9XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgaWYgKGNoID09PSAnYCcpIHtcbiAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIH1cbiAgICB9XG4gIH0gZWxzZSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICB9XG4gIHJldHVybiAnc3RyaW5nJztcbn1cbmV4cG9ydCBjb25zdCBwb3dlclNoZWxsID0ge1xuICBuYW1lOiBcInBvd2Vyc2hlbGxcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICByZXR1cm5TdGFjazogW10sXG4gICAgICBicmFja2V0TmVzdGluZzogMCxcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCI8I1wiLFxuICAgICAgICBjbG9zZTogXCIjPlwiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=