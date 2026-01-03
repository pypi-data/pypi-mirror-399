"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5198],{

/***/ 55198
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   puppet: () => (/* binding */ puppet)
/* harmony export */ });
// Stores the words from the define method
var words = {};
// Taken, mostly, from the Puppet official variable standards regex
var variable_regex = /({)?([a-z][a-z0-9_]*)?((::[a-z][a-z0-9_]*)*::)?[a-zA-Z0-9_]+(})?/;

// Takes a string of words separated by spaces and adds them as
// keys with the value of the first argument 'style'
function define(style, string) {
  var split = string.split(' ');
  for (var i = 0; i < split.length; i++) {
    words[split[i]] = style;
  }
}

// Takes commonly known puppet types/words and classifies them to a style
define('keyword', 'class define site node include import inherits');
define('keyword', 'case if else in and elsif default or');
define('atom', 'false true running present absent file directory undef');
define('builtin', 'action augeas burst chain computer cron destination dport exec ' + 'file filebucket group host icmp iniface interface jump k5login limit log_level ' + 'log_prefix macauthorization mailalias maillist mcx mount nagios_command ' + 'nagios_contact nagios_contactgroup nagios_host nagios_hostdependency ' + 'nagios_hostescalation nagios_hostextinfo nagios_hostgroup nagios_service ' + 'nagios_servicedependency nagios_serviceescalation nagios_serviceextinfo ' + 'nagios_servicegroup nagios_timeperiod name notify outiface package proto reject ' + 'resources router schedule scheduled_task selboolean selmodule service source ' + 'sport ssh_authorized_key sshkey stage state table tidy todest toports tosource ' + 'user vlan yumrepo zfs zone zpool');

// After finding a start of a string ('|") this function attempts to find the end;
// If a variable is encountered along the way, we display it differently when it
// is encapsulated in a double-quoted string.
function tokenString(stream, state) {
  var current,
    prev,
    found_var = false;
  while (!stream.eol() && (current = stream.next()) != state.pending) {
    if (current === '$' && prev != '\\' && state.pending == '"') {
      found_var = true;
      break;
    }
    prev = current;
  }
  if (found_var) {
    stream.backUp(1);
  }
  if (current == state.pending) {
    state.continueString = false;
  } else {
    state.continueString = true;
  }
  return "string";
}

// Main function
function tokenize(stream, state) {
  // Matches one whole word
  var word = stream.match(/[\w]+/, false);
  // Matches attributes (i.e. ensure => present ; 'ensure' would be matched)
  var attribute = stream.match(/(\s+)?\w+\s+=>.*/, false);
  // Matches non-builtin resource declarations
  // (i.e. "apache::vhost {" or "mycustomclasss {" would be matched)
  var resource = stream.match(/(\s+)?[\w:_]+(\s+)?{/, false);
  // Matches virtual and exported resources (i.e. @@user { ; and the like)
  var special_resource = stream.match(/(\s+)?[@]{1,2}[\w:_]+(\s+)?{/, false);

  // Finally advance the stream
  var ch = stream.next();

  // Have we found a variable?
  if (ch === '$') {
    if (stream.match(variable_regex)) {
      // If so, and its in a string, assign it a different color
      return state.continueString ? 'variableName.special' : 'variable';
    }
    // Otherwise return an invalid variable
    return "error";
  }
  // Should we still be looking for the end of a string?
  if (state.continueString) {
    // If so, go through the loop again
    stream.backUp(1);
    return tokenString(stream, state);
  }
  // Are we in a definition (class, node, define)?
  if (state.inDefinition) {
    // If so, return def (i.e. for 'class myclass {' ; 'myclass' would be matched)
    if (stream.match(/(\s+)?[\w:_]+(\s+)?/)) {
      return 'def';
    }
    // Match the rest it the next time around
    stream.match(/\s+{/);
    state.inDefinition = false;
  }
  // Are we in an 'include' statement?
  if (state.inInclude) {
    // Match and return the included class
    stream.match(/(\s+)?\S+(\s+)?/);
    state.inInclude = false;
    return 'def';
  }
  // Do we just have a function on our hands?
  // In 'ensure_resource("myclass")', 'ensure_resource' is matched
  if (stream.match(/(\s+)?\w+\(/)) {
    stream.backUp(1);
    return 'def';
  }
  // Have we matched the prior attribute regex?
  if (attribute) {
    stream.match(/(\s+)?\w+/);
    return 'tag';
  }
  // Do we have Puppet specific words?
  if (word && words.hasOwnProperty(word)) {
    // Negates the initial next()
    stream.backUp(1);
    // rs move the stream
    stream.match(/[\w]+/);
    // We want to process these words differently
    // do to the importance they have in Puppet
    if (stream.match(/\s+\S+\s+{/, false)) {
      state.inDefinition = true;
    }
    if (word == 'include') {
      state.inInclude = true;
    }
    // Returns their value as state in the prior define methods
    return words[word];
  }
  // Is there a match on a reference?
  if (/(^|\s+)[A-Z][\w:_]+/.test(word)) {
    // Negate the next()
    stream.backUp(1);
    // Match the full reference
    stream.match(/(^|\s+)[A-Z][\w:_]+/);
    return 'def';
  }
  // Have we matched the prior resource regex?
  if (resource) {
    stream.match(/(\s+)?[\w:_]+/);
    return 'def';
  }
  // Have we matched the prior special_resource regex?
  if (special_resource) {
    stream.match(/(\s+)?[@]{1,2}/);
    return 'atom';
  }
  // Match all the comments. All of them.
  if (ch == "#") {
    stream.skipToEnd();
    return "comment";
  }
  // Have we found a string?
  if (ch == "'" || ch == '"') {
    // Store the type (single or double)
    state.pending = ch;
    // Perform the looping function to find the end
    return tokenString(stream, state);
  }
  // Match all the brackets
  if (ch == '{' || ch == '}') {
    return 'bracket';
  }
  // Match characters that we are going to assume
  // are trying to be regex
  if (ch == '/') {
    stream.match(/^[^\/]*\//);
    return 'string.special';
  }
  // Match all the numbers
  if (ch.match(/[0-9]/)) {
    stream.eatWhile(/[0-9]+/);
    return 'number';
  }
  // Match the '=' and '=>' operators
  if (ch == '=') {
    if (stream.peek() == '>') {
      stream.next();
    }
    return "operator";
  }
  // Keep advancing through all the rest
  stream.eatWhile(/[\w-]/);
  // Return a blank line for everything else
  return null;
}
// Start it all
const puppet = {
  name: "puppet",
  startState: function () {
    var state = {};
    state.inDefinition = false;
    state.inInclude = false;
    state.continueString = false;
    state.pending = false;
    return state;
  },
  token: function (stream, state) {
    // Strip the spaces, but regex will account for them eitherway
    if (stream.eatSpace()) return null;
    // Go through the main process
    return tokenize(stream, state);
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTE5OC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3B1cHBldC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBTdG9yZXMgdGhlIHdvcmRzIGZyb20gdGhlIGRlZmluZSBtZXRob2RcbnZhciB3b3JkcyA9IHt9O1xuLy8gVGFrZW4sIG1vc3RseSwgZnJvbSB0aGUgUHVwcGV0IG9mZmljaWFsIHZhcmlhYmxlIHN0YW5kYXJkcyByZWdleFxudmFyIHZhcmlhYmxlX3JlZ2V4ID0gLyh7KT8oW2Etel1bYS16MC05X10qKT8oKDo6W2Etel1bYS16MC05X10qKSo6Oik/W2EtekEtWjAtOV9dKyh9KT8vO1xuXG4vLyBUYWtlcyBhIHN0cmluZyBvZiB3b3JkcyBzZXBhcmF0ZWQgYnkgc3BhY2VzIGFuZCBhZGRzIHRoZW0gYXNcbi8vIGtleXMgd2l0aCB0aGUgdmFsdWUgb2YgdGhlIGZpcnN0IGFyZ3VtZW50ICdzdHlsZSdcbmZ1bmN0aW9uIGRlZmluZShzdHlsZSwgc3RyaW5nKSB7XG4gIHZhciBzcGxpdCA9IHN0cmluZy5zcGxpdCgnICcpO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHNwbGl0Lmxlbmd0aDsgaSsrKSB7XG4gICAgd29yZHNbc3BsaXRbaV1dID0gc3R5bGU7XG4gIH1cbn1cblxuLy8gVGFrZXMgY29tbW9ubHkga25vd24gcHVwcGV0IHR5cGVzL3dvcmRzIGFuZCBjbGFzc2lmaWVzIHRoZW0gdG8gYSBzdHlsZVxuZGVmaW5lKCdrZXl3b3JkJywgJ2NsYXNzIGRlZmluZSBzaXRlIG5vZGUgaW5jbHVkZSBpbXBvcnQgaW5oZXJpdHMnKTtcbmRlZmluZSgna2V5d29yZCcsICdjYXNlIGlmIGVsc2UgaW4gYW5kIGVsc2lmIGRlZmF1bHQgb3InKTtcbmRlZmluZSgnYXRvbScsICdmYWxzZSB0cnVlIHJ1bm5pbmcgcHJlc2VudCBhYnNlbnQgZmlsZSBkaXJlY3RvcnkgdW5kZWYnKTtcbmRlZmluZSgnYnVpbHRpbicsICdhY3Rpb24gYXVnZWFzIGJ1cnN0IGNoYWluIGNvbXB1dGVyIGNyb24gZGVzdGluYXRpb24gZHBvcnQgZXhlYyAnICsgJ2ZpbGUgZmlsZWJ1Y2tldCBncm91cCBob3N0IGljbXAgaW5pZmFjZSBpbnRlcmZhY2UganVtcCBrNWxvZ2luIGxpbWl0IGxvZ19sZXZlbCAnICsgJ2xvZ19wcmVmaXggbWFjYXV0aG9yaXphdGlvbiBtYWlsYWxpYXMgbWFpbGxpc3QgbWN4IG1vdW50IG5hZ2lvc19jb21tYW5kICcgKyAnbmFnaW9zX2NvbnRhY3QgbmFnaW9zX2NvbnRhY3Rncm91cCBuYWdpb3NfaG9zdCBuYWdpb3NfaG9zdGRlcGVuZGVuY3kgJyArICduYWdpb3NfaG9zdGVzY2FsYXRpb24gbmFnaW9zX2hvc3RleHRpbmZvIG5hZ2lvc19ob3N0Z3JvdXAgbmFnaW9zX3NlcnZpY2UgJyArICduYWdpb3Nfc2VydmljZWRlcGVuZGVuY3kgbmFnaW9zX3NlcnZpY2Vlc2NhbGF0aW9uIG5hZ2lvc19zZXJ2aWNlZXh0aW5mbyAnICsgJ25hZ2lvc19zZXJ2aWNlZ3JvdXAgbmFnaW9zX3RpbWVwZXJpb2QgbmFtZSBub3RpZnkgb3V0aWZhY2UgcGFja2FnZSBwcm90byByZWplY3QgJyArICdyZXNvdXJjZXMgcm91dGVyIHNjaGVkdWxlIHNjaGVkdWxlZF90YXNrIHNlbGJvb2xlYW4gc2VsbW9kdWxlIHNlcnZpY2Ugc291cmNlICcgKyAnc3BvcnQgc3NoX2F1dGhvcml6ZWRfa2V5IHNzaGtleSBzdGFnZSBzdGF0ZSB0YWJsZSB0aWR5IHRvZGVzdCB0b3BvcnRzIHRvc291cmNlICcgKyAndXNlciB2bGFuIHl1bXJlcG8gemZzIHpvbmUgenBvb2wnKTtcblxuLy8gQWZ0ZXIgZmluZGluZyBhIHN0YXJ0IG9mIGEgc3RyaW5nICgnfFwiKSB0aGlzIGZ1bmN0aW9uIGF0dGVtcHRzIHRvIGZpbmQgdGhlIGVuZDtcbi8vIElmIGEgdmFyaWFibGUgaXMgZW5jb3VudGVyZWQgYWxvbmcgdGhlIHdheSwgd2UgZGlzcGxheSBpdCBkaWZmZXJlbnRseSB3aGVuIGl0XG4vLyBpcyBlbmNhcHN1bGF0ZWQgaW4gYSBkb3VibGUtcXVvdGVkIHN0cmluZy5cbmZ1bmN0aW9uIHRva2VuU3RyaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGN1cnJlbnQsXG4gICAgcHJldixcbiAgICBmb3VuZF92YXIgPSBmYWxzZTtcbiAgd2hpbGUgKCFzdHJlYW0uZW9sKCkgJiYgKGN1cnJlbnQgPSBzdHJlYW0ubmV4dCgpKSAhPSBzdGF0ZS5wZW5kaW5nKSB7XG4gICAgaWYgKGN1cnJlbnQgPT09ICckJyAmJiBwcmV2ICE9ICdcXFxcJyAmJiBzdGF0ZS5wZW5kaW5nID09ICdcIicpIHtcbiAgICAgIGZvdW5kX3ZhciA9IHRydWU7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgcHJldiA9IGN1cnJlbnQ7XG4gIH1cbiAgaWYgKGZvdW5kX3Zhcikge1xuICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gIH1cbiAgaWYgKGN1cnJlbnQgPT0gc3RhdGUucGVuZGluZykge1xuICAgIHN0YXRlLmNvbnRpbnVlU3RyaW5nID0gZmFsc2U7XG4gIH0gZWxzZSB7XG4gICAgc3RhdGUuY29udGludWVTdHJpbmcgPSB0cnVlO1xuICB9XG4gIHJldHVybiBcInN0cmluZ1wiO1xufVxuXG4vLyBNYWluIGZ1bmN0aW9uXG5mdW5jdGlvbiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKSB7XG4gIC8vIE1hdGNoZXMgb25lIHdob2xlIHdvcmRcbiAgdmFyIHdvcmQgPSBzdHJlYW0ubWF0Y2goL1tcXHddKy8sIGZhbHNlKTtcbiAgLy8gTWF0Y2hlcyBhdHRyaWJ1dGVzIChpLmUuIGVuc3VyZSA9PiBwcmVzZW50IDsgJ2Vuc3VyZScgd291bGQgYmUgbWF0Y2hlZClcbiAgdmFyIGF0dHJpYnV0ZSA9IHN0cmVhbS5tYXRjaCgvKFxccyspP1xcdytcXHMrPT4uKi8sIGZhbHNlKTtcbiAgLy8gTWF0Y2hlcyBub24tYnVpbHRpbiByZXNvdXJjZSBkZWNsYXJhdGlvbnNcbiAgLy8gKGkuZS4gXCJhcGFjaGU6OnZob3N0IHtcIiBvciBcIm15Y3VzdG9tY2xhc3NzIHtcIiB3b3VsZCBiZSBtYXRjaGVkKVxuICB2YXIgcmVzb3VyY2UgPSBzdHJlYW0ubWF0Y2goLyhcXHMrKT9bXFx3Ol9dKyhcXHMrKT97LywgZmFsc2UpO1xuICAvLyBNYXRjaGVzIHZpcnR1YWwgYW5kIGV4cG9ydGVkIHJlc291cmNlcyAoaS5lLiBAQHVzZXIgeyA7IGFuZCB0aGUgbGlrZSlcbiAgdmFyIHNwZWNpYWxfcmVzb3VyY2UgPSBzdHJlYW0ubWF0Y2goLyhcXHMrKT9bQF17MSwyfVtcXHc6X10rKFxccyspP3svLCBmYWxzZSk7XG5cbiAgLy8gRmluYWxseSBhZHZhbmNlIHRoZSBzdHJlYW1cbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcblxuICAvLyBIYXZlIHdlIGZvdW5kIGEgdmFyaWFibGU/XG4gIGlmIChjaCA9PT0gJyQnKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCh2YXJpYWJsZV9yZWdleCkpIHtcbiAgICAgIC8vIElmIHNvLCBhbmQgaXRzIGluIGEgc3RyaW5nLCBhc3NpZ24gaXQgYSBkaWZmZXJlbnQgY29sb3JcbiAgICAgIHJldHVybiBzdGF0ZS5jb250aW51ZVN0cmluZyA/ICd2YXJpYWJsZU5hbWUuc3BlY2lhbCcgOiAndmFyaWFibGUnO1xuICAgIH1cbiAgICAvLyBPdGhlcndpc2UgcmV0dXJuIGFuIGludmFsaWQgdmFyaWFibGVcbiAgICByZXR1cm4gXCJlcnJvclwiO1xuICB9XG4gIC8vIFNob3VsZCB3ZSBzdGlsbCBiZSBsb29raW5nIGZvciB0aGUgZW5kIG9mIGEgc3RyaW5nP1xuICBpZiAoc3RhdGUuY29udGludWVTdHJpbmcpIHtcbiAgICAvLyBJZiBzbywgZ28gdGhyb3VnaCB0aGUgbG9vcCBhZ2FpblxuICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgcmV0dXJuIHRva2VuU3RyaW5nKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIC8vIEFyZSB3ZSBpbiBhIGRlZmluaXRpb24gKGNsYXNzLCBub2RlLCBkZWZpbmUpP1xuICBpZiAoc3RhdGUuaW5EZWZpbml0aW9uKSB7XG4gICAgLy8gSWYgc28sIHJldHVybiBkZWYgKGkuZS4gZm9yICdjbGFzcyBteWNsYXNzIHsnIDsgJ215Y2xhc3MnIHdvdWxkIGJlIG1hdGNoZWQpXG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvKFxccyspP1tcXHc6X10rKFxccyspPy8pKSB7XG4gICAgICByZXR1cm4gJ2RlZic7XG4gICAgfVxuICAgIC8vIE1hdGNoIHRoZSByZXN0IGl0IHRoZSBuZXh0IHRpbWUgYXJvdW5kXG4gICAgc3RyZWFtLm1hdGNoKC9cXHMrey8pO1xuICAgIHN0YXRlLmluRGVmaW5pdGlvbiA9IGZhbHNlO1xuICB9XG4gIC8vIEFyZSB3ZSBpbiBhbiAnaW5jbHVkZScgc3RhdGVtZW50P1xuICBpZiAoc3RhdGUuaW5JbmNsdWRlKSB7XG4gICAgLy8gTWF0Y2ggYW5kIHJldHVybiB0aGUgaW5jbHVkZWQgY2xhc3NcbiAgICBzdHJlYW0ubWF0Y2goLyhcXHMrKT9cXFMrKFxccyspPy8pO1xuICAgIHN0YXRlLmluSW5jbHVkZSA9IGZhbHNlO1xuICAgIHJldHVybiAnZGVmJztcbiAgfVxuICAvLyBEbyB3ZSBqdXN0IGhhdmUgYSBmdW5jdGlvbiBvbiBvdXIgaGFuZHM/XG4gIC8vIEluICdlbnN1cmVfcmVzb3VyY2UoXCJteWNsYXNzXCIpJywgJ2Vuc3VyZV9yZXNvdXJjZScgaXMgbWF0Y2hlZFxuICBpZiAoc3RyZWFtLm1hdGNoKC8oXFxzKyk/XFx3K1xcKC8pKSB7XG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICByZXR1cm4gJ2RlZic7XG4gIH1cbiAgLy8gSGF2ZSB3ZSBtYXRjaGVkIHRoZSBwcmlvciBhdHRyaWJ1dGUgcmVnZXg/XG4gIGlmIChhdHRyaWJ1dGUpIHtcbiAgICBzdHJlYW0ubWF0Y2goLyhcXHMrKT9cXHcrLyk7XG4gICAgcmV0dXJuICd0YWcnO1xuICB9XG4gIC8vIERvIHdlIGhhdmUgUHVwcGV0IHNwZWNpZmljIHdvcmRzP1xuICBpZiAod29yZCAmJiB3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSkge1xuICAgIC8vIE5lZ2F0ZXMgdGhlIGluaXRpYWwgbmV4dCgpXG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICAvLyBycyBtb3ZlIHRoZSBzdHJlYW1cbiAgICBzdHJlYW0ubWF0Y2goL1tcXHddKy8pO1xuICAgIC8vIFdlIHdhbnQgdG8gcHJvY2VzcyB0aGVzZSB3b3JkcyBkaWZmZXJlbnRseVxuICAgIC8vIGRvIHRvIHRoZSBpbXBvcnRhbmNlIHRoZXkgaGF2ZSBpbiBQdXBwZXRcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9cXHMrXFxTK1xccyt7LywgZmFsc2UpKSB7XG4gICAgICBzdGF0ZS5pbkRlZmluaXRpb24gPSB0cnVlO1xuICAgIH1cbiAgICBpZiAod29yZCA9PSAnaW5jbHVkZScpIHtcbiAgICAgIHN0YXRlLmluSW5jbHVkZSA9IHRydWU7XG4gICAgfVxuICAgIC8vIFJldHVybnMgdGhlaXIgdmFsdWUgYXMgc3RhdGUgaW4gdGhlIHByaW9yIGRlZmluZSBtZXRob2RzXG4gICAgcmV0dXJuIHdvcmRzW3dvcmRdO1xuICB9XG4gIC8vIElzIHRoZXJlIGEgbWF0Y2ggb24gYSByZWZlcmVuY2U/XG4gIGlmICgvKF58XFxzKylbQS1aXVtcXHc6X10rLy50ZXN0KHdvcmQpKSB7XG4gICAgLy8gTmVnYXRlIHRoZSBuZXh0KClcbiAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgIC8vIE1hdGNoIHRoZSBmdWxsIHJlZmVyZW5jZVxuICAgIHN0cmVhbS5tYXRjaCgvKF58XFxzKylbQS1aXVtcXHc6X10rLyk7XG4gICAgcmV0dXJuICdkZWYnO1xuICB9XG4gIC8vIEhhdmUgd2UgbWF0Y2hlZCB0aGUgcHJpb3IgcmVzb3VyY2UgcmVnZXg/XG4gIGlmIChyZXNvdXJjZSkge1xuICAgIHN0cmVhbS5tYXRjaCgvKFxccyspP1tcXHc6X10rLyk7XG4gICAgcmV0dXJuICdkZWYnO1xuICB9XG4gIC8vIEhhdmUgd2UgbWF0Y2hlZCB0aGUgcHJpb3Igc3BlY2lhbF9yZXNvdXJjZSByZWdleD9cbiAgaWYgKHNwZWNpYWxfcmVzb3VyY2UpIHtcbiAgICBzdHJlYW0ubWF0Y2goLyhcXHMrKT9bQF17MSwyfS8pO1xuICAgIHJldHVybiAnYXRvbSc7XG4gIH1cbiAgLy8gTWF0Y2ggYWxsIHRoZSBjb21tZW50cy4gQWxsIG9mIHRoZW0uXG4gIGlmIChjaCA9PSBcIiNcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgLy8gSGF2ZSB3ZSBmb3VuZCBhIHN0cmluZz9cbiAgaWYgKGNoID09IFwiJ1wiIHx8IGNoID09ICdcIicpIHtcbiAgICAvLyBTdG9yZSB0aGUgdHlwZSAoc2luZ2xlIG9yIGRvdWJsZSlcbiAgICBzdGF0ZS5wZW5kaW5nID0gY2g7XG4gICAgLy8gUGVyZm9ybSB0aGUgbG9vcGluZyBmdW5jdGlvbiB0byBmaW5kIHRoZSBlbmRcbiAgICByZXR1cm4gdG9rZW5TdHJpbmcoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgLy8gTWF0Y2ggYWxsIHRoZSBicmFja2V0c1xuICBpZiAoY2ggPT0gJ3snIHx8IGNoID09ICd9Jykge1xuICAgIHJldHVybiAnYnJhY2tldCc7XG4gIH1cbiAgLy8gTWF0Y2ggY2hhcmFjdGVycyB0aGF0IHdlIGFyZSBnb2luZyB0byBhc3N1bWVcbiAgLy8gYXJlIHRyeWluZyB0byBiZSByZWdleFxuICBpZiAoY2ggPT0gJy8nKSB7XG4gICAgc3RyZWFtLm1hdGNoKC9eW15cXC9dKlxcLy8pO1xuICAgIHJldHVybiAnc3RyaW5nLnNwZWNpYWwnO1xuICB9XG4gIC8vIE1hdGNoIGFsbCB0aGUgbnVtYmVyc1xuICBpZiAoY2gubWF0Y2goL1swLTldLykpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1swLTldKy8pO1xuICAgIHJldHVybiAnbnVtYmVyJztcbiAgfVxuICAvLyBNYXRjaCB0aGUgJz0nIGFuZCAnPT4nIG9wZXJhdG9yc1xuICBpZiAoY2ggPT0gJz0nKSB7XG4gICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJz4nKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9XG4gIC8vIEtlZXAgYWR2YW5jaW5nIHRocm91Z2ggYWxsIHRoZSByZXN0XG4gIHN0cmVhbS5lYXRXaGlsZSgvW1xcdy1dLyk7XG4gIC8vIFJldHVybiBhIGJsYW5rIGxpbmUgZm9yIGV2ZXJ5dGhpbmcgZWxzZVxuICByZXR1cm4gbnVsbDtcbn1cbi8vIFN0YXJ0IGl0IGFsbFxuZXhwb3J0IGNvbnN0IHB1cHBldCA9IHtcbiAgbmFtZTogXCJwdXBwZXRcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHZhciBzdGF0ZSA9IHt9O1xuICAgIHN0YXRlLmluRGVmaW5pdGlvbiA9IGZhbHNlO1xuICAgIHN0YXRlLmluSW5jbHVkZSA9IGZhbHNlO1xuICAgIHN0YXRlLmNvbnRpbnVlU3RyaW5nID0gZmFsc2U7XG4gICAgc3RhdGUucGVuZGluZyA9IGZhbHNlO1xuICAgIHJldHVybiBzdGF0ZTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgLy8gU3RyaXAgdGhlIHNwYWNlcywgYnV0IHJlZ2V4IHdpbGwgYWNjb3VudCBmb3IgdGhlbSBlaXRoZXJ3YXlcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIC8vIEdvIHRocm91Z2ggdGhlIG1haW4gcHJvY2Vzc1xuICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9