"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3837],{

/***/ 93837
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   perl: () => (/* binding */ perl)
/* harmony export */ });
// it's like "peek", but need for look-ahead or look-behind if index < 0
function look(stream, c) {
  return stream.string.charAt(stream.pos + (c || 0));
}

// return a part of prefix of current stream from current position
function prefix(stream, c) {
  if (c) {
    var x = stream.pos - c;
    return stream.string.substr(x >= 0 ? x : 0, c);
  } else {
    return stream.string.substr(0, stream.pos - 1);
  }
}

// return a part of suffix of current stream from current position
function suffix(stream, c) {
  var y = stream.string.length;
  var x = y - stream.pos + 1;
  return stream.string.substr(stream.pos, c && c < y ? c : x);
}

// eating and vomiting a part of stream from current position
function eatSuffix(stream, c) {
  var x = stream.pos + c;
  var y;
  if (x <= 0) stream.pos = 0;else if (x >= (y = stream.string.length - 1)) stream.pos = y;else stream.pos = x;
}

// http://perldoc.perl.org
var PERL = {
  //   null - magic touch
  //   1 - keyword
  //   2 - def
  //   3 - atom
  //   4 - operator
  //   5 - builtin (predefined)
  //   [x,y] - x=1,2,3; y=must be defined if x{...}
  //      PERL operators
  '->': 4,
  '++': 4,
  '--': 4,
  '**': 4,
  //   ! ~ \ and unary + and -
  '=~': 4,
  '!~': 4,
  '*': 4,
  '/': 4,
  '%': 4,
  'x': 4,
  '+': 4,
  '-': 4,
  '.': 4,
  '<<': 4,
  '>>': 4,
  //   named unary operators
  '<': 4,
  '>': 4,
  '<=': 4,
  '>=': 4,
  'lt': 4,
  'gt': 4,
  'le': 4,
  'ge': 4,
  '==': 4,
  '!=': 4,
  '<=>': 4,
  'eq': 4,
  'ne': 4,
  'cmp': 4,
  '~~': 4,
  '&': 4,
  '|': 4,
  '^': 4,
  '&&': 4,
  '||': 4,
  '//': 4,
  '..': 4,
  '...': 4,
  '?': 4,
  ':': 4,
  '=': 4,
  '+=': 4,
  '-=': 4,
  '*=': 4,
  //   etc. ???
  ',': 4,
  '=>': 4,
  '::': 4,
  //   list operators (rightward)
  'not': 4,
  'and': 4,
  'or': 4,
  'xor': 4,
  //      PERL predefined variables (I know, what this is a paranoid idea, but may be needed for people, who learn PERL, and for me as well, ...and may be for you?;)
  'BEGIN': [5, 1],
  'END': [5, 1],
  'PRINT': [5, 1],
  'PRINTF': [5, 1],
  'GETC': [5, 1],
  'READ': [5, 1],
  'READLINE': [5, 1],
  'DESTROY': [5, 1],
  'TIE': [5, 1],
  'TIEHANDLE': [5, 1],
  'UNTIE': [5, 1],
  'STDIN': 5,
  'STDIN_TOP': 5,
  'STDOUT': 5,
  'STDOUT_TOP': 5,
  'STDERR': 5,
  'STDERR_TOP': 5,
  '$ARG': 5,
  '$_': 5,
  '@ARG': 5,
  '@_': 5,
  '$LIST_SEPARATOR': 5,
  '$"': 5,
  '$PROCESS_ID': 5,
  '$PID': 5,
  '$$': 5,
  '$REAL_GROUP_ID': 5,
  '$GID': 5,
  '$(': 5,
  '$EFFECTIVE_GROUP_ID': 5,
  '$EGID': 5,
  '$)': 5,
  '$PROGRAM_NAME': 5,
  '$0': 5,
  '$SUBSCRIPT_SEPARATOR': 5,
  '$SUBSEP': 5,
  '$;': 5,
  '$REAL_USER_ID': 5,
  '$UID': 5,
  '$<': 5,
  '$EFFECTIVE_USER_ID': 5,
  '$EUID': 5,
  '$>': 5,
  '$a': 5,
  '$b': 5,
  '$COMPILING': 5,
  '$^C': 5,
  '$DEBUGGING': 5,
  '$^D': 5,
  '${^ENCODING}': 5,
  '$ENV': 5,
  '%ENV': 5,
  '$SYSTEM_FD_MAX': 5,
  '$^F': 5,
  '@F': 5,
  '${^GLOBAL_PHASE}': 5,
  '$^H': 5,
  '%^H': 5,
  '@INC': 5,
  '%INC': 5,
  '$INPLACE_EDIT': 5,
  '$^I': 5,
  '$^M': 5,
  '$OSNAME': 5,
  '$^O': 5,
  '${^OPEN}': 5,
  '$PERLDB': 5,
  '$^P': 5,
  '$SIG': 5,
  '%SIG': 5,
  '$BASETIME': 5,
  '$^T': 5,
  '${^TAINT}': 5,
  '${^UNICODE}': 5,
  '${^UTF8CACHE}': 5,
  '${^UTF8LOCALE}': 5,
  '$PERL_VERSION': 5,
  '$^V': 5,
  '${^WIN32_SLOPPY_STAT}': 5,
  '$EXECUTABLE_NAME': 5,
  '$^X': 5,
  '$1': 5,
  // - regexp $1, $2...
  '$MATCH': 5,
  '$&': 5,
  '${^MATCH}': 5,
  '$PREMATCH': 5,
  '$`': 5,
  '${^PREMATCH}': 5,
  '$POSTMATCH': 5,
  "$'": 5,
  '${^POSTMATCH}': 5,
  '$LAST_PAREN_MATCH': 5,
  '$+': 5,
  '$LAST_SUBMATCH_RESULT': 5,
  '$^N': 5,
  '@LAST_MATCH_END': 5,
  '@+': 5,
  '%LAST_PAREN_MATCH': 5,
  '%+': 5,
  '@LAST_MATCH_START': 5,
  '@-': 5,
  '%LAST_MATCH_START': 5,
  '%-': 5,
  '$LAST_REGEXP_CODE_RESULT': 5,
  '$^R': 5,
  '${^RE_DEBUG_FLAGS}': 5,
  '${^RE_TRIE_MAXBUF}': 5,
  '$ARGV': 5,
  '@ARGV': 5,
  'ARGV': 5,
  'ARGVOUT': 5,
  '$OUTPUT_FIELD_SEPARATOR': 5,
  '$OFS': 5,
  '$,': 5,
  '$INPUT_LINE_NUMBER': 5,
  '$NR': 5,
  '$.': 5,
  '$INPUT_RECORD_SEPARATOR': 5,
  '$RS': 5,
  '$/': 5,
  '$OUTPUT_RECORD_SEPARATOR': 5,
  '$ORS': 5,
  '$\\': 5,
  '$OUTPUT_AUTOFLUSH': 5,
  '$|': 5,
  '$ACCUMULATOR': 5,
  '$^A': 5,
  '$FORMAT_FORMFEED': 5,
  '$^L': 5,
  '$FORMAT_PAGE_NUMBER': 5,
  '$%': 5,
  '$FORMAT_LINES_LEFT': 5,
  '$-': 5,
  '$FORMAT_LINE_BREAK_CHARACTERS': 5,
  '$:': 5,
  '$FORMAT_LINES_PER_PAGE': 5,
  '$=': 5,
  '$FORMAT_TOP_NAME': 5,
  '$^': 5,
  '$FORMAT_NAME': 5,
  '$~': 5,
  '${^CHILD_ERROR_NATIVE}': 5,
  '$EXTENDED_OS_ERROR': 5,
  '$^E': 5,
  '$EXCEPTIONS_BEING_CAUGHT': 5,
  '$^S': 5,
  '$WARNING': 5,
  '$^W': 5,
  '${^WARNING_BITS}': 5,
  '$OS_ERROR': 5,
  '$ERRNO': 5,
  '$!': 5,
  '%OS_ERROR': 5,
  '%ERRNO': 5,
  '%!': 5,
  '$CHILD_ERROR': 5,
  '$?': 5,
  '$EVAL_ERROR': 5,
  '$@': 5,
  '$OFMT': 5,
  '$#': 5,
  '$*': 5,
  '$ARRAY_BASE': 5,
  '$[': 5,
  '$OLD_PERL_VERSION': 5,
  '$]': 5,
  //      PERL blocks
  'if': [1, 1],
  elsif: [1, 1],
  'else': [1, 1],
  'while': [1, 1],
  unless: [1, 1],
  'for': [1, 1],
  foreach: [1, 1],
  //      PERL functions
  'abs': 1,
  // - absolute value function
  accept: 1,
  // - accept an incoming socket connect
  alarm: 1,
  // - schedule a SIGALRM
  'atan2': 1,
  // - arctangent of Y/X in the range -PI to PI
  bind: 1,
  // - binds an address to a socket
  binmode: 1,
  // - prepare binary files for I/O
  bless: 1,
  // - create an object
  bootstrap: 1,
  //
  'break': 1,
  // - break out of a "given" block
  caller: 1,
  // - get context of the current subroutine call
  chdir: 1,
  // - change your current working directory
  chmod: 1,
  // - changes the permissions on a list of files
  chomp: 1,
  // - remove a trailing record separator from a string
  chop: 1,
  // - remove the last character from a string
  chown: 1,
  // - change the ownership on a list of files
  chr: 1,
  // - get character this number represents
  chroot: 1,
  // - make directory new root for path lookups
  close: 1,
  // - close file (or pipe or socket) handle
  closedir: 1,
  // - close directory handle
  connect: 1,
  // - connect to a remote socket
  'continue': [1, 1],
  // - optional trailing block in a while or foreach
  'cos': 1,
  // - cosine function
  crypt: 1,
  // - one-way passwd-style encryption
  dbmclose: 1,
  // - breaks binding on a tied dbm file
  dbmopen: 1,
  // - create binding on a tied dbm file
  'default': 1,
  //
  defined: 1,
  // - test whether a value, variable, or function is defined
  'delete': 1,
  // - deletes a value from a hash
  die: 1,
  // - raise an exception or bail out
  'do': 1,
  // - turn a BLOCK into a TERM
  dump: 1,
  // - create an immediate core dump
  each: 1,
  // - retrieve the next key/value pair from a hash
  endgrent: 1,
  // - be done using group file
  endhostent: 1,
  // - be done using hosts file
  endnetent: 1,
  // - be done using networks file
  endprotoent: 1,
  // - be done using protocols file
  endpwent: 1,
  // - be done using passwd file
  endservent: 1,
  // - be done using services file
  eof: 1,
  // - test a filehandle for its end
  'eval': 1,
  // - catch exceptions or compile and run code
  'exec': 1,
  // - abandon this program to run another
  exists: 1,
  // - test whether a hash key is present
  exit: 1,
  // - terminate this program
  'exp': 1,
  // - raise I to a power
  fcntl: 1,
  // - file control system call
  fileno: 1,
  // - return file descriptor from filehandle
  flock: 1,
  // - lock an entire file with an advisory lock
  fork: 1,
  // - create a new process just like this one
  format: 1,
  // - declare a picture format with use by the write() function
  formline: 1,
  // - internal function used for formats
  getc: 1,
  // - get the next character from the filehandle
  getgrent: 1,
  // - get next group record
  getgrgid: 1,
  // - get group record given group user ID
  getgrnam: 1,
  // - get group record given group name
  gethostbyaddr: 1,
  // - get host record given its address
  gethostbyname: 1,
  // - get host record given name
  gethostent: 1,
  // - get next hosts record
  getlogin: 1,
  // - return who logged in at this tty
  getnetbyaddr: 1,
  // - get network record given its address
  getnetbyname: 1,
  // - get networks record given name
  getnetent: 1,
  // - get next networks record
  getpeername: 1,
  // - find the other end of a socket connection
  getpgrp: 1,
  // - get process group
  getppid: 1,
  // - get parent process ID
  getpriority: 1,
  // - get current nice value
  getprotobyname: 1,
  // - get protocol record given name
  getprotobynumber: 1,
  // - get protocol record numeric protocol
  getprotoent: 1,
  // - get next protocols record
  getpwent: 1,
  // - get next passwd record
  getpwnam: 1,
  // - get passwd record given user login name
  getpwuid: 1,
  // - get passwd record given user ID
  getservbyname: 1,
  // - get services record given its name
  getservbyport: 1,
  // - get services record given numeric port
  getservent: 1,
  // - get next services record
  getsockname: 1,
  // - retrieve the sockaddr for a given socket
  getsockopt: 1,
  // - get socket options on a given socket
  given: 1,
  //
  glob: 1,
  // - expand filenames using wildcards
  gmtime: 1,
  // - convert UNIX time into record or string using Greenwich time
  'goto': 1,
  // - create spaghetti code
  grep: 1,
  // - locate elements in a list test true against a given criterion
  hex: 1,
  // - convert a string to a hexadecimal number
  'import': 1,
  // - patch a module's namespace into your own
  index: 1,
  // - find a substring within a string
  'int': 1,
  // - get the integer portion of a number
  ioctl: 1,
  // - system-dependent device control system call
  'join': 1,
  // - join a list into a string using a separator
  keys: 1,
  // - retrieve list of indices from a hash
  kill: 1,
  // - send a signal to a process or process group
  last: 1,
  // - exit a block prematurely
  lc: 1,
  // - return lower-case version of a string
  lcfirst: 1,
  // - return a string with just the next letter in lower case
  length: 1,
  // - return the number of bytes in a string
  'link': 1,
  // - create a hard link in the filesystem
  listen: 1,
  // - register your socket as a server
  local: 2,
  // - create a temporary value for a global variable (dynamic scoping)
  localtime: 1,
  // - convert UNIX time into record or string using local time
  lock: 1,
  // - get a thread lock on a variable, subroutine, or method
  'log': 1,
  // - retrieve the natural logarithm for a number
  lstat: 1,
  // - stat a symbolic link
  m: null,
  // - match a string with a regular expression pattern
  map: 1,
  // - apply a change to a list to get back a new list with the changes
  mkdir: 1,
  // - create a directory
  msgctl: 1,
  // - SysV IPC message control operations
  msgget: 1,
  // - get SysV IPC message queue
  msgrcv: 1,
  // - receive a SysV IPC message from a message queue
  msgsnd: 1,
  // - send a SysV IPC message to a message queue
  my: 2,
  // - declare and assign a local variable (lexical scoping)
  'new': 1,
  //
  next: 1,
  // - iterate a block prematurely
  no: 1,
  // - unimport some module symbols or semantics at compile time
  oct: 1,
  // - convert a string to an octal number
  open: 1,
  // - open a file, pipe, or descriptor
  opendir: 1,
  // - open a directory
  ord: 1,
  // - find a character's numeric representation
  our: 2,
  // - declare and assign a package variable (lexical scoping)
  pack: 1,
  // - convert a list into a binary representation
  'package': 1,
  // - declare a separate global namespace
  pipe: 1,
  // - open a pair of connected filehandles
  pop: 1,
  // - remove the last element from an array and return it
  pos: 1,
  // - find or set the offset for the last/next m//g search
  print: 1,
  // - output a list to a filehandle
  printf: 1,
  // - output a formatted list to a filehandle
  prototype: 1,
  // - get the prototype (if any) of a subroutine
  push: 1,
  // - append one or more elements to an array
  q: null,
  // - singly quote a string
  qq: null,
  // - doubly quote a string
  qr: null,
  // - Compile pattern
  quotemeta: null,
  // - quote regular expression magic characters
  qw: null,
  // - quote a list of words
  qx: null,
  // - backquote quote a string
  rand: 1,
  // - retrieve the next pseudorandom number
  read: 1,
  // - fixed-length buffered input from a filehandle
  readdir: 1,
  // - get a directory from a directory handle
  readline: 1,
  // - fetch a record from a file
  readlink: 1,
  // - determine where a symbolic link is pointing
  readpipe: 1,
  // - execute a system command and collect standard output
  recv: 1,
  // - receive a message over a Socket
  redo: 1,
  // - start this loop iteration over again
  ref: 1,
  // - find out the type of thing being referenced
  rename: 1,
  // - change a filename
  require: 1,
  // - load in external functions from a library at runtime
  reset: 1,
  // - clear all variables of a given name
  'return': 1,
  // - get out of a function early
  reverse: 1,
  // - flip a string or a list
  rewinddir: 1,
  // - reset directory handle
  rindex: 1,
  // - right-to-left substring search
  rmdir: 1,
  // - remove a directory
  s: null,
  // - replace a pattern with a string
  say: 1,
  // - print with newline
  scalar: 1,
  // - force a scalar context
  seek: 1,
  // - reposition file pointer for random-access I/O
  seekdir: 1,
  // - reposition directory pointer
  select: 1,
  // - reset default output or do I/O multiplexing
  semctl: 1,
  // - SysV semaphore control operations
  semget: 1,
  // - get set of SysV semaphores
  semop: 1,
  // - SysV semaphore operations
  send: 1,
  // - send a message over a socket
  setgrent: 1,
  // - prepare group file for use
  sethostent: 1,
  // - prepare hosts file for use
  setnetent: 1,
  // - prepare networks file for use
  setpgrp: 1,
  // - set the process group of a process
  setpriority: 1,
  // - set a process's nice value
  setprotoent: 1,
  // - prepare protocols file for use
  setpwent: 1,
  // - prepare passwd file for use
  setservent: 1,
  // - prepare services file for use
  setsockopt: 1,
  // - set some socket options
  shift: 1,
  // - remove the first element of an array, and return it
  shmctl: 1,
  // - SysV shared memory operations
  shmget: 1,
  // - get SysV shared memory segment identifier
  shmread: 1,
  // - read SysV shared memory
  shmwrite: 1,
  // - write SysV shared memory
  shutdown: 1,
  // - close down just half of a socket connection
  'sin': 1,
  // - return the sine of a number
  sleep: 1,
  // - block for some number of seconds
  socket: 1,
  // - create a socket
  socketpair: 1,
  // - create a pair of sockets
  'sort': 1,
  // - sort a list of values
  splice: 1,
  // - add or remove elements anywhere in an array
  'split': 1,
  // - split up a string using a regexp delimiter
  sprintf: 1,
  // - formatted print into a string
  'sqrt': 1,
  // - square root function
  srand: 1,
  // - seed the random number generator
  stat: 1,
  // - get a file's status information
  state: 1,
  // - declare and assign a state variable (persistent lexical scoping)
  study: 1,
  // - optimize input data for repeated searches
  'sub': 1,
  // - declare a subroutine, possibly anonymously
  'substr': 1,
  // - get or alter a portion of a string
  symlink: 1,
  // - create a symbolic link to a file
  syscall: 1,
  // - execute an arbitrary system call
  sysopen: 1,
  // - open a file, pipe, or descriptor
  sysread: 1,
  // - fixed-length unbuffered input from a filehandle
  sysseek: 1,
  // - position I/O pointer on handle used with sysread and syswrite
  system: 1,
  // - run a separate program
  syswrite: 1,
  // - fixed-length unbuffered output to a filehandle
  tell: 1,
  // - get current seekpointer on a filehandle
  telldir: 1,
  // - get current seekpointer on a directory handle
  tie: 1,
  // - bind a variable to an object class
  tied: 1,
  // - get a reference to the object underlying a tied variable
  time: 1,
  // - return number of seconds since 1970
  times: 1,
  // - return elapsed time for self and child processes
  tr: null,
  // - transliterate a string
  truncate: 1,
  // - shorten a file
  uc: 1,
  // - return upper-case version of a string
  ucfirst: 1,
  // - return a string with just the next letter in upper case
  umask: 1,
  // - set file creation mode mask
  undef: 1,
  // - remove a variable or function definition
  unlink: 1,
  // - remove one link to a file
  unpack: 1,
  // - convert binary structure into normal perl variables
  unshift: 1,
  // - prepend more elements to the beginning of a list
  untie: 1,
  // - break a tie binding to a variable
  use: 1,
  // - load in a module at compile time
  utime: 1,
  // - set a file's last access and modify times
  values: 1,
  // - return a list of the values in a hash
  vec: 1,
  // - test or set particular bits in a string
  wait: 1,
  // - wait for any child process to die
  waitpid: 1,
  // - wait for a particular child process to die
  wantarray: 1,
  // - get void vs scalar vs list context of current subroutine call
  warn: 1,
  // - print debugging info
  when: 1,
  //
  write: 1,
  // - print a picture record
  y: null
}; // - transliterate a string

var RXstyle = "string.special";
var RXmodifiers = /[goseximacplud]/; // NOTE: "m", "s", "y" and "tr" need to correct real modifiers for each regexp type

function tokenChain(stream, state, chain, style, tail) {
  // NOTE: chain.length > 2 is not working now (it's for s[...][...]geos;)
  state.chain = null; //                                                          12   3tail
  state.style = null;
  state.tail = null;
  state.tokenize = function (stream, state) {
    var e = false,
      c,
      i = 0;
    while (c = stream.next()) {
      if (c === chain[i] && !e) {
        if (chain[++i] !== undefined) {
          state.chain = chain[i];
          state.style = style;
          state.tail = tail;
        } else if (tail) stream.eatWhile(tail);
        state.tokenize = tokenPerl;
        return style;
      }
      e = !e && c == "\\";
    }
    return style;
  };
  return state.tokenize(stream, state);
}
function tokenSOMETHING(stream, state, string) {
  state.tokenize = function (stream, state) {
    if (stream.string == string) state.tokenize = tokenPerl;
    stream.skipToEnd();
    return "string";
  };
  return state.tokenize(stream, state);
}
function tokenPerl(stream, state) {
  if (stream.eatSpace()) return null;
  if (state.chain) return tokenChain(stream, state, state.chain, state.style, state.tail);
  if (stream.match(/^(\-?((\d[\d_]*)?\.\d+(e[+-]?\d+)?|\d+\.\d*)|0x[\da-fA-F_]+|0b[01_]+|\d[\d_]*(e[+-]?\d+)?)/)) return 'number';
  if (stream.match(/^<<(?=[_a-zA-Z])/)) {
    // NOTE: <<SOMETHING\n...\nSOMETHING\n
    stream.eatWhile(/\w/);
    return tokenSOMETHING(stream, state, stream.current().substr(2));
  }
  if (stream.sol() && stream.match(/^\=item(?!\w)/)) {
    // NOTE: \n=item...\n=cut\n
    return tokenSOMETHING(stream, state, '=cut');
  }
  var ch = stream.next();
  if (ch == '"' || ch == "'") {
    // NOTE: ' or " or <<'SOMETHING'\n...\nSOMETHING\n or <<"SOMETHING"\n...\nSOMETHING\n
    if (prefix(stream, 3) == "<<" + ch) {
      var p = stream.pos;
      stream.eatWhile(/\w/);
      var n = stream.current().substr(1);
      if (n && stream.eat(ch)) return tokenSOMETHING(stream, state, n);
      stream.pos = p;
    }
    return tokenChain(stream, state, [ch], "string");
  }
  if (ch == "q") {
    var c = look(stream, -2);
    if (!(c && /\w/.test(c))) {
      c = look(stream, 0);
      if (c == "x") {
        c = look(stream, 1);
        if (c == "(") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [")"], RXstyle, RXmodifiers);
        }
        if (c == "[") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["]"], RXstyle, RXmodifiers);
        }
        if (c == "{") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["}"], RXstyle, RXmodifiers);
        }
        if (c == "<") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [">"], RXstyle, RXmodifiers);
        }
        if (/[\^'"!~\/]/.test(c)) {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, [stream.eat(c)], RXstyle, RXmodifiers);
        }
      } else if (c == "q") {
        c = look(stream, 1);
        if (c == "(") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [")"], "string");
        }
        if (c == "[") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["]"], "string");
        }
        if (c == "{") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["}"], "string");
        }
        if (c == "<") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [">"], "string");
        }
        if (/[\^'"!~\/]/.test(c)) {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, [stream.eat(c)], "string");
        }
      } else if (c == "w") {
        c = look(stream, 1);
        if (c == "(") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [")"], "bracket");
        }
        if (c == "[") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["]"], "bracket");
        }
        if (c == "{") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["}"], "bracket");
        }
        if (c == "<") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [">"], "bracket");
        }
        if (/[\^'"!~\/]/.test(c)) {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, [stream.eat(c)], "bracket");
        }
      } else if (c == "r") {
        c = look(stream, 1);
        if (c == "(") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [")"], RXstyle, RXmodifiers);
        }
        if (c == "[") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["]"], RXstyle, RXmodifiers);
        }
        if (c == "{") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, ["}"], RXstyle, RXmodifiers);
        }
        if (c == "<") {
          eatSuffix(stream, 2);
          return tokenChain(stream, state, [">"], RXstyle, RXmodifiers);
        }
        if (/[\^'"!~\/]/.test(c)) {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, [stream.eat(c)], RXstyle, RXmodifiers);
        }
      } else if (/[\^'"!~\/(\[{<]/.test(c)) {
        if (c == "(") {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, [")"], "string");
        }
        if (c == "[") {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, ["]"], "string");
        }
        if (c == "{") {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, ["}"], "string");
        }
        if (c == "<") {
          eatSuffix(stream, 1);
          return tokenChain(stream, state, [">"], "string");
        }
        if (/[\^'"!~\/]/.test(c)) {
          return tokenChain(stream, state, [stream.eat(c)], "string");
        }
      }
    }
  }
  if (ch == "m") {
    var c = look(stream, -2);
    if (!(c && /\w/.test(c))) {
      c = stream.eat(/[(\[{<\^'"!~\/]/);
      if (c) {
        if (/[\^'"!~\/]/.test(c)) {
          return tokenChain(stream, state, [c], RXstyle, RXmodifiers);
        }
        if (c == "(") {
          return tokenChain(stream, state, [")"], RXstyle, RXmodifiers);
        }
        if (c == "[") {
          return tokenChain(stream, state, ["]"], RXstyle, RXmodifiers);
        }
        if (c == "{") {
          return tokenChain(stream, state, ["}"], RXstyle, RXmodifiers);
        }
        if (c == "<") {
          return tokenChain(stream, state, [">"], RXstyle, RXmodifiers);
        }
      }
    }
  }
  if (ch == "s") {
    var c = /[\/>\]})\w]/.test(look(stream, -2));
    if (!c) {
      c = stream.eat(/[(\[{<\^'"!~\/]/);
      if (c) {
        if (c == "[") return tokenChain(stream, state, ["]", "]"], RXstyle, RXmodifiers);
        if (c == "{") return tokenChain(stream, state, ["}", "}"], RXstyle, RXmodifiers);
        if (c == "<") return tokenChain(stream, state, [">", ">"], RXstyle, RXmodifiers);
        if (c == "(") return tokenChain(stream, state, [")", ")"], RXstyle, RXmodifiers);
        return tokenChain(stream, state, [c, c], RXstyle, RXmodifiers);
      }
    }
  }
  if (ch == "y") {
    var c = /[\/>\]})\w]/.test(look(stream, -2));
    if (!c) {
      c = stream.eat(/[(\[{<\^'"!~\/]/);
      if (c) {
        if (c == "[") return tokenChain(stream, state, ["]", "]"], RXstyle, RXmodifiers);
        if (c == "{") return tokenChain(stream, state, ["}", "}"], RXstyle, RXmodifiers);
        if (c == "<") return tokenChain(stream, state, [">", ">"], RXstyle, RXmodifiers);
        if (c == "(") return tokenChain(stream, state, [")", ")"], RXstyle, RXmodifiers);
        return tokenChain(stream, state, [c, c], RXstyle, RXmodifiers);
      }
    }
  }
  if (ch == "t") {
    var c = /[\/>\]})\w]/.test(look(stream, -2));
    if (!c) {
      c = stream.eat("r");
      if (c) {
        c = stream.eat(/[(\[{<\^'"!~\/]/);
        if (c) {
          if (c == "[") return tokenChain(stream, state, ["]", "]"], RXstyle, RXmodifiers);
          if (c == "{") return tokenChain(stream, state, ["}", "}"], RXstyle, RXmodifiers);
          if (c == "<") return tokenChain(stream, state, [">", ">"], RXstyle, RXmodifiers);
          if (c == "(") return tokenChain(stream, state, [")", ")"], RXstyle, RXmodifiers);
          return tokenChain(stream, state, [c, c], RXstyle, RXmodifiers);
        }
      }
    }
  }
  if (ch == "`") {
    return tokenChain(stream, state, [ch], "builtin");
  }
  if (ch == "/") {
    if (!/~\s*$/.test(prefix(stream))) return "operator";else return tokenChain(stream, state, [ch], RXstyle, RXmodifiers);
  }
  if (ch == "$") {
    var p = stream.pos;
    if (stream.eatWhile(/\d/) || stream.eat("{") && stream.eatWhile(/\d/) && stream.eat("}")) return "builtin";else stream.pos = p;
  }
  if (/[$@%]/.test(ch)) {
    var p = stream.pos;
    if (stream.eat("^") && stream.eat(/[A-Z]/) || !/[@$%&]/.test(look(stream, -2)) && stream.eat(/[=|\\\-#?@;:&`~\^!\[\]*'"$+.,\/<>()]/)) {
      var c = stream.current();
      if (PERL[c]) return "builtin";
    }
    stream.pos = p;
  }
  if (/[$@%&]/.test(ch)) {
    if (stream.eatWhile(/[\w$]/) || stream.eat("{") && stream.eatWhile(/[\w$]/) && stream.eat("}")) {
      var c = stream.current();
      if (PERL[c]) return "builtin";else return "variable";
    }
  }
  if (ch == "#") {
    if (look(stream, -2) != "$") {
      stream.skipToEnd();
      return "comment";
    }
  }
  if (/[:+\-\^*$&%@=<>!?|\/~\.]/.test(ch)) {
    var p = stream.pos;
    stream.eatWhile(/[:+\-\^*$&%@=<>!?|\/~\.]/);
    if (PERL[stream.current()]) return "operator";else stream.pos = p;
  }
  if (ch == "_") {
    if (stream.pos == 1) {
      if (suffix(stream, 6) == "_END__") {
        return tokenChain(stream, state, ['\0'], "comment");
      } else if (suffix(stream, 7) == "_DATA__") {
        return tokenChain(stream, state, ['\0'], "builtin");
      } else if (suffix(stream, 7) == "_C__") {
        return tokenChain(stream, state, ['\0'], "string");
      }
    }
  }
  if (/\w/.test(ch)) {
    var p = stream.pos;
    if (look(stream, -2) == "{" && (look(stream, 0) == "}" || stream.eatWhile(/\w/) && look(stream, 0) == "}")) return "string";else stream.pos = p;
  }
  if (/[A-Z]/.test(ch)) {
    var l = look(stream, -2);
    var p = stream.pos;
    stream.eatWhile(/[A-Z_]/);
    if (/[\da-z]/.test(look(stream, 0))) {
      stream.pos = p;
    } else {
      var c = PERL[stream.current()];
      if (!c) return "meta";
      if (c[1]) c = c[0];
      if (l != ":") {
        if (c == 1) return "keyword";else if (c == 2) return "def";else if (c == 3) return "atom";else if (c == 4) return "operator";else if (c == 5) return "builtin";else return "meta";
      } else return "meta";
    }
  }
  if (/[a-zA-Z_]/.test(ch)) {
    var l = look(stream, -2);
    stream.eatWhile(/\w/);
    var c = PERL[stream.current()];
    if (!c) return "meta";
    if (c[1]) c = c[0];
    if (l != ":") {
      if (c == 1) return "keyword";else if (c == 2) return "def";else if (c == 3) return "atom";else if (c == 4) return "operator";else if (c == 5) return "builtin";else return "meta";
    } else return "meta";
  }
  return null;
}
const perl = {
  name: "perl",
  startState: function () {
    return {
      tokenize: tokenPerl,
      chain: null,
      style: null,
      tail: null
    };
  },
  token: function (stream, state) {
    return (state.tokenize || tokenPerl)(stream, state);
  },
  languageData: {
    commentTokens: {
      line: "#"
    },
    wordChars: "$"
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzgzNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvcGVybC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBpdCdzIGxpa2UgXCJwZWVrXCIsIGJ1dCBuZWVkIGZvciBsb29rLWFoZWFkIG9yIGxvb2stYmVoaW5kIGlmIGluZGV4IDwgMFxuZnVuY3Rpb24gbG9vayhzdHJlYW0sIGMpIHtcbiAgcmV0dXJuIHN0cmVhbS5zdHJpbmcuY2hhckF0KHN0cmVhbS5wb3MgKyAoYyB8fCAwKSk7XG59XG5cbi8vIHJldHVybiBhIHBhcnQgb2YgcHJlZml4IG9mIGN1cnJlbnQgc3RyZWFtIGZyb20gY3VycmVudCBwb3NpdGlvblxuZnVuY3Rpb24gcHJlZml4KHN0cmVhbSwgYykge1xuICBpZiAoYykge1xuICAgIHZhciB4ID0gc3RyZWFtLnBvcyAtIGM7XG4gICAgcmV0dXJuIHN0cmVhbS5zdHJpbmcuc3Vic3RyKHggPj0gMCA/IHggOiAwLCBjKTtcbiAgfSBlbHNlIHtcbiAgICByZXR1cm4gc3RyZWFtLnN0cmluZy5zdWJzdHIoMCwgc3RyZWFtLnBvcyAtIDEpO1xuICB9XG59XG5cbi8vIHJldHVybiBhIHBhcnQgb2Ygc3VmZml4IG9mIGN1cnJlbnQgc3RyZWFtIGZyb20gY3VycmVudCBwb3NpdGlvblxuZnVuY3Rpb24gc3VmZml4KHN0cmVhbSwgYykge1xuICB2YXIgeSA9IHN0cmVhbS5zdHJpbmcubGVuZ3RoO1xuICB2YXIgeCA9IHkgLSBzdHJlYW0ucG9zICsgMTtcbiAgcmV0dXJuIHN0cmVhbS5zdHJpbmcuc3Vic3RyKHN0cmVhbS5wb3MsIGMgJiYgYyA8IHkgPyBjIDogeCk7XG59XG5cbi8vIGVhdGluZyBhbmQgdm9taXRpbmcgYSBwYXJ0IG9mIHN0cmVhbSBmcm9tIGN1cnJlbnQgcG9zaXRpb25cbmZ1bmN0aW9uIGVhdFN1ZmZpeChzdHJlYW0sIGMpIHtcbiAgdmFyIHggPSBzdHJlYW0ucG9zICsgYztcbiAgdmFyIHk7XG4gIGlmICh4IDw9IDApIHN0cmVhbS5wb3MgPSAwO2Vsc2UgaWYgKHggPj0gKHkgPSBzdHJlYW0uc3RyaW5nLmxlbmd0aCAtIDEpKSBzdHJlYW0ucG9zID0geTtlbHNlIHN0cmVhbS5wb3MgPSB4O1xufVxuXG4vLyBodHRwOi8vcGVybGRvYy5wZXJsLm9yZ1xudmFyIFBFUkwgPSB7XG4gIC8vICAgbnVsbCAtIG1hZ2ljIHRvdWNoXG4gIC8vICAgMSAtIGtleXdvcmRcbiAgLy8gICAyIC0gZGVmXG4gIC8vICAgMyAtIGF0b21cbiAgLy8gICA0IC0gb3BlcmF0b3JcbiAgLy8gICA1IC0gYnVpbHRpbiAocHJlZGVmaW5lZClcbiAgLy8gICBbeCx5XSAtIHg9MSwyLDM7IHk9bXVzdCBiZSBkZWZpbmVkIGlmIHh7Li4ufVxuICAvLyAgICAgIFBFUkwgb3BlcmF0b3JzXG4gICctPic6IDQsXG4gICcrKyc6IDQsXG4gICctLSc6IDQsXG4gICcqKic6IDQsXG4gIC8vICAgISB+IFxcIGFuZCB1bmFyeSArIGFuZCAtXG4gICc9fic6IDQsXG4gICchfic6IDQsXG4gICcqJzogNCxcbiAgJy8nOiA0LFxuICAnJSc6IDQsXG4gICd4JzogNCxcbiAgJysnOiA0LFxuICAnLSc6IDQsXG4gICcuJzogNCxcbiAgJzw8JzogNCxcbiAgJz4+JzogNCxcbiAgLy8gICBuYW1lZCB1bmFyeSBvcGVyYXRvcnNcbiAgJzwnOiA0LFxuICAnPic6IDQsXG4gICc8PSc6IDQsXG4gICc+PSc6IDQsXG4gICdsdCc6IDQsXG4gICdndCc6IDQsXG4gICdsZSc6IDQsXG4gICdnZSc6IDQsXG4gICc9PSc6IDQsXG4gICchPSc6IDQsXG4gICc8PT4nOiA0LFxuICAnZXEnOiA0LFxuICAnbmUnOiA0LFxuICAnY21wJzogNCxcbiAgJ35+JzogNCxcbiAgJyYnOiA0LFxuICAnfCc6IDQsXG4gICdeJzogNCxcbiAgJyYmJzogNCxcbiAgJ3x8JzogNCxcbiAgJy8vJzogNCxcbiAgJy4uJzogNCxcbiAgJy4uLic6IDQsXG4gICc/JzogNCxcbiAgJzonOiA0LFxuICAnPSc6IDQsXG4gICcrPSc6IDQsXG4gICctPSc6IDQsXG4gICcqPSc6IDQsXG4gIC8vICAgZXRjLiA/Pz9cbiAgJywnOiA0LFxuICAnPT4nOiA0LFxuICAnOjonOiA0LFxuICAvLyAgIGxpc3Qgb3BlcmF0b3JzIChyaWdodHdhcmQpXG4gICdub3QnOiA0LFxuICAnYW5kJzogNCxcbiAgJ29yJzogNCxcbiAgJ3hvcic6IDQsXG4gIC8vICAgICAgUEVSTCBwcmVkZWZpbmVkIHZhcmlhYmxlcyAoSSBrbm93LCB3aGF0IHRoaXMgaXMgYSBwYXJhbm9pZCBpZGVhLCBidXQgbWF5IGJlIG5lZWRlZCBmb3IgcGVvcGxlLCB3aG8gbGVhcm4gUEVSTCwgYW5kIGZvciBtZSBhcyB3ZWxsLCAuLi5hbmQgbWF5IGJlIGZvciB5b3U/OylcbiAgJ0JFR0lOJzogWzUsIDFdLFxuICAnRU5EJzogWzUsIDFdLFxuICAnUFJJTlQnOiBbNSwgMV0sXG4gICdQUklOVEYnOiBbNSwgMV0sXG4gICdHRVRDJzogWzUsIDFdLFxuICAnUkVBRCc6IFs1LCAxXSxcbiAgJ1JFQURMSU5FJzogWzUsIDFdLFxuICAnREVTVFJPWSc6IFs1LCAxXSxcbiAgJ1RJRSc6IFs1LCAxXSxcbiAgJ1RJRUhBTkRMRSc6IFs1LCAxXSxcbiAgJ1VOVElFJzogWzUsIDFdLFxuICAnU1RESU4nOiA1LFxuICAnU1RESU5fVE9QJzogNSxcbiAgJ1NURE9VVCc6IDUsXG4gICdTVERPVVRfVE9QJzogNSxcbiAgJ1NUREVSUic6IDUsXG4gICdTVERFUlJfVE9QJzogNSxcbiAgJyRBUkcnOiA1LFxuICAnJF8nOiA1LFxuICAnQEFSRyc6IDUsXG4gICdAXyc6IDUsXG4gICckTElTVF9TRVBBUkFUT1InOiA1LFxuICAnJFwiJzogNSxcbiAgJyRQUk9DRVNTX0lEJzogNSxcbiAgJyRQSUQnOiA1LFxuICAnJCQnOiA1LFxuICAnJFJFQUxfR1JPVVBfSUQnOiA1LFxuICAnJEdJRCc6IDUsXG4gICckKCc6IDUsXG4gICckRUZGRUNUSVZFX0dST1VQX0lEJzogNSxcbiAgJyRFR0lEJzogNSxcbiAgJyQpJzogNSxcbiAgJyRQUk9HUkFNX05BTUUnOiA1LFxuICAnJDAnOiA1LFxuICAnJFNVQlNDUklQVF9TRVBBUkFUT1InOiA1LFxuICAnJFNVQlNFUCc6IDUsXG4gICckOyc6IDUsXG4gICckUkVBTF9VU0VSX0lEJzogNSxcbiAgJyRVSUQnOiA1LFxuICAnJDwnOiA1LFxuICAnJEVGRkVDVElWRV9VU0VSX0lEJzogNSxcbiAgJyRFVUlEJzogNSxcbiAgJyQ+JzogNSxcbiAgJyRhJzogNSxcbiAgJyRiJzogNSxcbiAgJyRDT01QSUxJTkcnOiA1LFxuICAnJF5DJzogNSxcbiAgJyRERUJVR0dJTkcnOiA1LFxuICAnJF5EJzogNSxcbiAgJyR7XkVOQ09ESU5HfSc6IDUsXG4gICckRU5WJzogNSxcbiAgJyVFTlYnOiA1LFxuICAnJFNZU1RFTV9GRF9NQVgnOiA1LFxuICAnJF5GJzogNSxcbiAgJ0BGJzogNSxcbiAgJyR7XkdMT0JBTF9QSEFTRX0nOiA1LFxuICAnJF5IJzogNSxcbiAgJyVeSCc6IDUsXG4gICdASU5DJzogNSxcbiAgJyVJTkMnOiA1LFxuICAnJElOUExBQ0VfRURJVCc6IDUsXG4gICckXkknOiA1LFxuICAnJF5NJzogNSxcbiAgJyRPU05BTUUnOiA1LFxuICAnJF5PJzogNSxcbiAgJyR7Xk9QRU59JzogNSxcbiAgJyRQRVJMREInOiA1LFxuICAnJF5QJzogNSxcbiAgJyRTSUcnOiA1LFxuICAnJVNJRyc6IDUsXG4gICckQkFTRVRJTUUnOiA1LFxuICAnJF5UJzogNSxcbiAgJyR7XlRBSU5UfSc6IDUsXG4gICcke15VTklDT0RFfSc6IDUsXG4gICcke15VVEY4Q0FDSEV9JzogNSxcbiAgJyR7XlVURjhMT0NBTEV9JzogNSxcbiAgJyRQRVJMX1ZFUlNJT04nOiA1LFxuICAnJF5WJzogNSxcbiAgJyR7XldJTjMyX1NMT1BQWV9TVEFUfSc6IDUsXG4gICckRVhFQ1VUQUJMRV9OQU1FJzogNSxcbiAgJyReWCc6IDUsXG4gICckMSc6IDUsXG4gIC8vIC0gcmVnZXhwICQxLCAkMi4uLlxuICAnJE1BVENIJzogNSxcbiAgJyQmJzogNSxcbiAgJyR7Xk1BVENIfSc6IDUsXG4gICckUFJFTUFUQ0gnOiA1LFxuICAnJGAnOiA1LFxuICAnJHteUFJFTUFUQ0h9JzogNSxcbiAgJyRQT1NUTUFUQ0gnOiA1LFxuICBcIiQnXCI6IDUsXG4gICcke15QT1NUTUFUQ0h9JzogNSxcbiAgJyRMQVNUX1BBUkVOX01BVENIJzogNSxcbiAgJyQrJzogNSxcbiAgJyRMQVNUX1NVQk1BVENIX1JFU1VMVCc6IDUsXG4gICckXk4nOiA1LFxuICAnQExBU1RfTUFUQ0hfRU5EJzogNSxcbiAgJ0ArJzogNSxcbiAgJyVMQVNUX1BBUkVOX01BVENIJzogNSxcbiAgJyUrJzogNSxcbiAgJ0BMQVNUX01BVENIX1NUQVJUJzogNSxcbiAgJ0AtJzogNSxcbiAgJyVMQVNUX01BVENIX1NUQVJUJzogNSxcbiAgJyUtJzogNSxcbiAgJyRMQVNUX1JFR0VYUF9DT0RFX1JFU1VMVCc6IDUsXG4gICckXlInOiA1LFxuICAnJHteUkVfREVCVUdfRkxBR1N9JzogNSxcbiAgJyR7XlJFX1RSSUVfTUFYQlVGfSc6IDUsXG4gICckQVJHVic6IDUsXG4gICdAQVJHVic6IDUsXG4gICdBUkdWJzogNSxcbiAgJ0FSR1ZPVVQnOiA1LFxuICAnJE9VVFBVVF9GSUVMRF9TRVBBUkFUT1InOiA1LFxuICAnJE9GUyc6IDUsXG4gICckLCc6IDUsXG4gICckSU5QVVRfTElORV9OVU1CRVInOiA1LFxuICAnJE5SJzogNSxcbiAgJyQuJzogNSxcbiAgJyRJTlBVVF9SRUNPUkRfU0VQQVJBVE9SJzogNSxcbiAgJyRSUyc6IDUsXG4gICckLyc6IDUsXG4gICckT1VUUFVUX1JFQ09SRF9TRVBBUkFUT1InOiA1LFxuICAnJE9SUyc6IDUsXG4gICckXFxcXCc6IDUsXG4gICckT1VUUFVUX0FVVE9GTFVTSCc6IDUsXG4gICckfCc6IDUsXG4gICckQUNDVU1VTEFUT1InOiA1LFxuICAnJF5BJzogNSxcbiAgJyRGT1JNQVRfRk9STUZFRUQnOiA1LFxuICAnJF5MJzogNSxcbiAgJyRGT1JNQVRfUEFHRV9OVU1CRVInOiA1LFxuICAnJCUnOiA1LFxuICAnJEZPUk1BVF9MSU5FU19MRUZUJzogNSxcbiAgJyQtJzogNSxcbiAgJyRGT1JNQVRfTElORV9CUkVBS19DSEFSQUNURVJTJzogNSxcbiAgJyQ6JzogNSxcbiAgJyRGT1JNQVRfTElORVNfUEVSX1BBR0UnOiA1LFxuICAnJD0nOiA1LFxuICAnJEZPUk1BVF9UT1BfTkFNRSc6IDUsXG4gICckXic6IDUsXG4gICckRk9STUFUX05BTUUnOiA1LFxuICAnJH4nOiA1LFxuICAnJHteQ0hJTERfRVJST1JfTkFUSVZFfSc6IDUsXG4gICckRVhURU5ERURfT1NfRVJST1InOiA1LFxuICAnJF5FJzogNSxcbiAgJyRFWENFUFRJT05TX0JFSU5HX0NBVUdIVCc6IDUsXG4gICckXlMnOiA1LFxuICAnJFdBUk5JTkcnOiA1LFxuICAnJF5XJzogNSxcbiAgJyR7XldBUk5JTkdfQklUU30nOiA1LFxuICAnJE9TX0VSUk9SJzogNSxcbiAgJyRFUlJOTyc6IDUsXG4gICckISc6IDUsXG4gICclT1NfRVJST1InOiA1LFxuICAnJUVSUk5PJzogNSxcbiAgJyUhJzogNSxcbiAgJyRDSElMRF9FUlJPUic6IDUsXG4gICckPyc6IDUsXG4gICckRVZBTF9FUlJPUic6IDUsXG4gICckQCc6IDUsXG4gICckT0ZNVCc6IDUsXG4gICckIyc6IDUsXG4gICckKic6IDUsXG4gICckQVJSQVlfQkFTRSc6IDUsXG4gICckWyc6IDUsXG4gICckT0xEX1BFUkxfVkVSU0lPTic6IDUsXG4gICckXSc6IDUsXG4gIC8vICAgICAgUEVSTCBibG9ja3NcbiAgJ2lmJzogWzEsIDFdLFxuICBlbHNpZjogWzEsIDFdLFxuICAnZWxzZSc6IFsxLCAxXSxcbiAgJ3doaWxlJzogWzEsIDFdLFxuICB1bmxlc3M6IFsxLCAxXSxcbiAgJ2Zvcic6IFsxLCAxXSxcbiAgZm9yZWFjaDogWzEsIDFdLFxuICAvLyAgICAgIFBFUkwgZnVuY3Rpb25zXG4gICdhYnMnOiAxLFxuICAvLyAtIGFic29sdXRlIHZhbHVlIGZ1bmN0aW9uXG4gIGFjY2VwdDogMSxcbiAgLy8gLSBhY2NlcHQgYW4gaW5jb21pbmcgc29ja2V0IGNvbm5lY3RcbiAgYWxhcm06IDEsXG4gIC8vIC0gc2NoZWR1bGUgYSBTSUdBTFJNXG4gICdhdGFuMic6IDEsXG4gIC8vIC0gYXJjdGFuZ2VudCBvZiBZL1ggaW4gdGhlIHJhbmdlIC1QSSB0byBQSVxuICBiaW5kOiAxLFxuICAvLyAtIGJpbmRzIGFuIGFkZHJlc3MgdG8gYSBzb2NrZXRcbiAgYmlubW9kZTogMSxcbiAgLy8gLSBwcmVwYXJlIGJpbmFyeSBmaWxlcyBmb3IgSS9PXG4gIGJsZXNzOiAxLFxuICAvLyAtIGNyZWF0ZSBhbiBvYmplY3RcbiAgYm9vdHN0cmFwOiAxLFxuICAvL1xuICAnYnJlYWsnOiAxLFxuICAvLyAtIGJyZWFrIG91dCBvZiBhIFwiZ2l2ZW5cIiBibG9ja1xuICBjYWxsZXI6IDEsXG4gIC8vIC0gZ2V0IGNvbnRleHQgb2YgdGhlIGN1cnJlbnQgc3Vicm91dGluZSBjYWxsXG4gIGNoZGlyOiAxLFxuICAvLyAtIGNoYW5nZSB5b3VyIGN1cnJlbnQgd29ya2luZyBkaXJlY3RvcnlcbiAgY2htb2Q6IDEsXG4gIC8vIC0gY2hhbmdlcyB0aGUgcGVybWlzc2lvbnMgb24gYSBsaXN0IG9mIGZpbGVzXG4gIGNob21wOiAxLFxuICAvLyAtIHJlbW92ZSBhIHRyYWlsaW5nIHJlY29yZCBzZXBhcmF0b3IgZnJvbSBhIHN0cmluZ1xuICBjaG9wOiAxLFxuICAvLyAtIHJlbW92ZSB0aGUgbGFzdCBjaGFyYWN0ZXIgZnJvbSBhIHN0cmluZ1xuICBjaG93bjogMSxcbiAgLy8gLSBjaGFuZ2UgdGhlIG93bmVyc2hpcCBvbiBhIGxpc3Qgb2YgZmlsZXNcbiAgY2hyOiAxLFxuICAvLyAtIGdldCBjaGFyYWN0ZXIgdGhpcyBudW1iZXIgcmVwcmVzZW50c1xuICBjaHJvb3Q6IDEsXG4gIC8vIC0gbWFrZSBkaXJlY3RvcnkgbmV3IHJvb3QgZm9yIHBhdGggbG9va3Vwc1xuICBjbG9zZTogMSxcbiAgLy8gLSBjbG9zZSBmaWxlIChvciBwaXBlIG9yIHNvY2tldCkgaGFuZGxlXG4gIGNsb3NlZGlyOiAxLFxuICAvLyAtIGNsb3NlIGRpcmVjdG9yeSBoYW5kbGVcbiAgY29ubmVjdDogMSxcbiAgLy8gLSBjb25uZWN0IHRvIGEgcmVtb3RlIHNvY2tldFxuICAnY29udGludWUnOiBbMSwgMV0sXG4gIC8vIC0gb3B0aW9uYWwgdHJhaWxpbmcgYmxvY2sgaW4gYSB3aGlsZSBvciBmb3JlYWNoXG4gICdjb3MnOiAxLFxuICAvLyAtIGNvc2luZSBmdW5jdGlvblxuICBjcnlwdDogMSxcbiAgLy8gLSBvbmUtd2F5IHBhc3N3ZC1zdHlsZSBlbmNyeXB0aW9uXG4gIGRibWNsb3NlOiAxLFxuICAvLyAtIGJyZWFrcyBiaW5kaW5nIG9uIGEgdGllZCBkYm0gZmlsZVxuICBkYm1vcGVuOiAxLFxuICAvLyAtIGNyZWF0ZSBiaW5kaW5nIG9uIGEgdGllZCBkYm0gZmlsZVxuICAnZGVmYXVsdCc6IDEsXG4gIC8vXG4gIGRlZmluZWQ6IDEsXG4gIC8vIC0gdGVzdCB3aGV0aGVyIGEgdmFsdWUsIHZhcmlhYmxlLCBvciBmdW5jdGlvbiBpcyBkZWZpbmVkXG4gICdkZWxldGUnOiAxLFxuICAvLyAtIGRlbGV0ZXMgYSB2YWx1ZSBmcm9tIGEgaGFzaFxuICBkaWU6IDEsXG4gIC8vIC0gcmFpc2UgYW4gZXhjZXB0aW9uIG9yIGJhaWwgb3V0XG4gICdkbyc6IDEsXG4gIC8vIC0gdHVybiBhIEJMT0NLIGludG8gYSBURVJNXG4gIGR1bXA6IDEsXG4gIC8vIC0gY3JlYXRlIGFuIGltbWVkaWF0ZSBjb3JlIGR1bXBcbiAgZWFjaDogMSxcbiAgLy8gLSByZXRyaWV2ZSB0aGUgbmV4dCBrZXkvdmFsdWUgcGFpciBmcm9tIGEgaGFzaFxuICBlbmRncmVudDogMSxcbiAgLy8gLSBiZSBkb25lIHVzaW5nIGdyb3VwIGZpbGVcbiAgZW5kaG9zdGVudDogMSxcbiAgLy8gLSBiZSBkb25lIHVzaW5nIGhvc3RzIGZpbGVcbiAgZW5kbmV0ZW50OiAxLFxuICAvLyAtIGJlIGRvbmUgdXNpbmcgbmV0d29ya3MgZmlsZVxuICBlbmRwcm90b2VudDogMSxcbiAgLy8gLSBiZSBkb25lIHVzaW5nIHByb3RvY29scyBmaWxlXG4gIGVuZHB3ZW50OiAxLFxuICAvLyAtIGJlIGRvbmUgdXNpbmcgcGFzc3dkIGZpbGVcbiAgZW5kc2VydmVudDogMSxcbiAgLy8gLSBiZSBkb25lIHVzaW5nIHNlcnZpY2VzIGZpbGVcbiAgZW9mOiAxLFxuICAvLyAtIHRlc3QgYSBmaWxlaGFuZGxlIGZvciBpdHMgZW5kXG4gICdldmFsJzogMSxcbiAgLy8gLSBjYXRjaCBleGNlcHRpb25zIG9yIGNvbXBpbGUgYW5kIHJ1biBjb2RlXG4gICdleGVjJzogMSxcbiAgLy8gLSBhYmFuZG9uIHRoaXMgcHJvZ3JhbSB0byBydW4gYW5vdGhlclxuICBleGlzdHM6IDEsXG4gIC8vIC0gdGVzdCB3aGV0aGVyIGEgaGFzaCBrZXkgaXMgcHJlc2VudFxuICBleGl0OiAxLFxuICAvLyAtIHRlcm1pbmF0ZSB0aGlzIHByb2dyYW1cbiAgJ2V4cCc6IDEsXG4gIC8vIC0gcmFpc2UgSSB0byBhIHBvd2VyXG4gIGZjbnRsOiAxLFxuICAvLyAtIGZpbGUgY29udHJvbCBzeXN0ZW0gY2FsbFxuICBmaWxlbm86IDEsXG4gIC8vIC0gcmV0dXJuIGZpbGUgZGVzY3JpcHRvciBmcm9tIGZpbGVoYW5kbGVcbiAgZmxvY2s6IDEsXG4gIC8vIC0gbG9jayBhbiBlbnRpcmUgZmlsZSB3aXRoIGFuIGFkdmlzb3J5IGxvY2tcbiAgZm9yazogMSxcbiAgLy8gLSBjcmVhdGUgYSBuZXcgcHJvY2VzcyBqdXN0IGxpa2UgdGhpcyBvbmVcbiAgZm9ybWF0OiAxLFxuICAvLyAtIGRlY2xhcmUgYSBwaWN0dXJlIGZvcm1hdCB3aXRoIHVzZSBieSB0aGUgd3JpdGUoKSBmdW5jdGlvblxuICBmb3JtbGluZTogMSxcbiAgLy8gLSBpbnRlcm5hbCBmdW5jdGlvbiB1c2VkIGZvciBmb3JtYXRzXG4gIGdldGM6IDEsXG4gIC8vIC0gZ2V0IHRoZSBuZXh0IGNoYXJhY3RlciBmcm9tIHRoZSBmaWxlaGFuZGxlXG4gIGdldGdyZW50OiAxLFxuICAvLyAtIGdldCBuZXh0IGdyb3VwIHJlY29yZFxuICBnZXRncmdpZDogMSxcbiAgLy8gLSBnZXQgZ3JvdXAgcmVjb3JkIGdpdmVuIGdyb3VwIHVzZXIgSURcbiAgZ2V0Z3JuYW06IDEsXG4gIC8vIC0gZ2V0IGdyb3VwIHJlY29yZCBnaXZlbiBncm91cCBuYW1lXG4gIGdldGhvc3RieWFkZHI6IDEsXG4gIC8vIC0gZ2V0IGhvc3QgcmVjb3JkIGdpdmVuIGl0cyBhZGRyZXNzXG4gIGdldGhvc3RieW5hbWU6IDEsXG4gIC8vIC0gZ2V0IGhvc3QgcmVjb3JkIGdpdmVuIG5hbWVcbiAgZ2V0aG9zdGVudDogMSxcbiAgLy8gLSBnZXQgbmV4dCBob3N0cyByZWNvcmRcbiAgZ2V0bG9naW46IDEsXG4gIC8vIC0gcmV0dXJuIHdobyBsb2dnZWQgaW4gYXQgdGhpcyB0dHlcbiAgZ2V0bmV0YnlhZGRyOiAxLFxuICAvLyAtIGdldCBuZXR3b3JrIHJlY29yZCBnaXZlbiBpdHMgYWRkcmVzc1xuICBnZXRuZXRieW5hbWU6IDEsXG4gIC8vIC0gZ2V0IG5ldHdvcmtzIHJlY29yZCBnaXZlbiBuYW1lXG4gIGdldG5ldGVudDogMSxcbiAgLy8gLSBnZXQgbmV4dCBuZXR3b3JrcyByZWNvcmRcbiAgZ2V0cGVlcm5hbWU6IDEsXG4gIC8vIC0gZmluZCB0aGUgb3RoZXIgZW5kIG9mIGEgc29ja2V0IGNvbm5lY3Rpb25cbiAgZ2V0cGdycDogMSxcbiAgLy8gLSBnZXQgcHJvY2VzcyBncm91cFxuICBnZXRwcGlkOiAxLFxuICAvLyAtIGdldCBwYXJlbnQgcHJvY2VzcyBJRFxuICBnZXRwcmlvcml0eTogMSxcbiAgLy8gLSBnZXQgY3VycmVudCBuaWNlIHZhbHVlXG4gIGdldHByb3RvYnluYW1lOiAxLFxuICAvLyAtIGdldCBwcm90b2NvbCByZWNvcmQgZ2l2ZW4gbmFtZVxuICBnZXRwcm90b2J5bnVtYmVyOiAxLFxuICAvLyAtIGdldCBwcm90b2NvbCByZWNvcmQgbnVtZXJpYyBwcm90b2NvbFxuICBnZXRwcm90b2VudDogMSxcbiAgLy8gLSBnZXQgbmV4dCBwcm90b2NvbHMgcmVjb3JkXG4gIGdldHB3ZW50OiAxLFxuICAvLyAtIGdldCBuZXh0IHBhc3N3ZCByZWNvcmRcbiAgZ2V0cHduYW06IDEsXG4gIC8vIC0gZ2V0IHBhc3N3ZCByZWNvcmQgZ2l2ZW4gdXNlciBsb2dpbiBuYW1lXG4gIGdldHB3dWlkOiAxLFxuICAvLyAtIGdldCBwYXNzd2QgcmVjb3JkIGdpdmVuIHVzZXIgSURcbiAgZ2V0c2VydmJ5bmFtZTogMSxcbiAgLy8gLSBnZXQgc2VydmljZXMgcmVjb3JkIGdpdmVuIGl0cyBuYW1lXG4gIGdldHNlcnZieXBvcnQ6IDEsXG4gIC8vIC0gZ2V0IHNlcnZpY2VzIHJlY29yZCBnaXZlbiBudW1lcmljIHBvcnRcbiAgZ2V0c2VydmVudDogMSxcbiAgLy8gLSBnZXQgbmV4dCBzZXJ2aWNlcyByZWNvcmRcbiAgZ2V0c29ja25hbWU6IDEsXG4gIC8vIC0gcmV0cmlldmUgdGhlIHNvY2thZGRyIGZvciBhIGdpdmVuIHNvY2tldFxuICBnZXRzb2Nrb3B0OiAxLFxuICAvLyAtIGdldCBzb2NrZXQgb3B0aW9ucyBvbiBhIGdpdmVuIHNvY2tldFxuICBnaXZlbjogMSxcbiAgLy9cbiAgZ2xvYjogMSxcbiAgLy8gLSBleHBhbmQgZmlsZW5hbWVzIHVzaW5nIHdpbGRjYXJkc1xuICBnbXRpbWU6IDEsXG4gIC8vIC0gY29udmVydCBVTklYIHRpbWUgaW50byByZWNvcmQgb3Igc3RyaW5nIHVzaW5nIEdyZWVud2ljaCB0aW1lXG4gICdnb3RvJzogMSxcbiAgLy8gLSBjcmVhdGUgc3BhZ2hldHRpIGNvZGVcbiAgZ3JlcDogMSxcbiAgLy8gLSBsb2NhdGUgZWxlbWVudHMgaW4gYSBsaXN0IHRlc3QgdHJ1ZSBhZ2FpbnN0IGEgZ2l2ZW4gY3JpdGVyaW9uXG4gIGhleDogMSxcbiAgLy8gLSBjb252ZXJ0IGEgc3RyaW5nIHRvIGEgaGV4YWRlY2ltYWwgbnVtYmVyXG4gICdpbXBvcnQnOiAxLFxuICAvLyAtIHBhdGNoIGEgbW9kdWxlJ3MgbmFtZXNwYWNlIGludG8geW91ciBvd25cbiAgaW5kZXg6IDEsXG4gIC8vIC0gZmluZCBhIHN1YnN0cmluZyB3aXRoaW4gYSBzdHJpbmdcbiAgJ2ludCc6IDEsXG4gIC8vIC0gZ2V0IHRoZSBpbnRlZ2VyIHBvcnRpb24gb2YgYSBudW1iZXJcbiAgaW9jdGw6IDEsXG4gIC8vIC0gc3lzdGVtLWRlcGVuZGVudCBkZXZpY2UgY29udHJvbCBzeXN0ZW0gY2FsbFxuICAnam9pbic6IDEsXG4gIC8vIC0gam9pbiBhIGxpc3QgaW50byBhIHN0cmluZyB1c2luZyBhIHNlcGFyYXRvclxuICBrZXlzOiAxLFxuICAvLyAtIHJldHJpZXZlIGxpc3Qgb2YgaW5kaWNlcyBmcm9tIGEgaGFzaFxuICBraWxsOiAxLFxuICAvLyAtIHNlbmQgYSBzaWduYWwgdG8gYSBwcm9jZXNzIG9yIHByb2Nlc3MgZ3JvdXBcbiAgbGFzdDogMSxcbiAgLy8gLSBleGl0IGEgYmxvY2sgcHJlbWF0dXJlbHlcbiAgbGM6IDEsXG4gIC8vIC0gcmV0dXJuIGxvd2VyLWNhc2UgdmVyc2lvbiBvZiBhIHN0cmluZ1xuICBsY2ZpcnN0OiAxLFxuICAvLyAtIHJldHVybiBhIHN0cmluZyB3aXRoIGp1c3QgdGhlIG5leHQgbGV0dGVyIGluIGxvd2VyIGNhc2VcbiAgbGVuZ3RoOiAxLFxuICAvLyAtIHJldHVybiB0aGUgbnVtYmVyIG9mIGJ5dGVzIGluIGEgc3RyaW5nXG4gICdsaW5rJzogMSxcbiAgLy8gLSBjcmVhdGUgYSBoYXJkIGxpbmsgaW4gdGhlIGZpbGVzeXN0ZW1cbiAgbGlzdGVuOiAxLFxuICAvLyAtIHJlZ2lzdGVyIHlvdXIgc29ja2V0IGFzIGEgc2VydmVyXG4gIGxvY2FsOiAyLFxuICAvLyAtIGNyZWF0ZSBhIHRlbXBvcmFyeSB2YWx1ZSBmb3IgYSBnbG9iYWwgdmFyaWFibGUgKGR5bmFtaWMgc2NvcGluZylcbiAgbG9jYWx0aW1lOiAxLFxuICAvLyAtIGNvbnZlcnQgVU5JWCB0aW1lIGludG8gcmVjb3JkIG9yIHN0cmluZyB1c2luZyBsb2NhbCB0aW1lXG4gIGxvY2s6IDEsXG4gIC8vIC0gZ2V0IGEgdGhyZWFkIGxvY2sgb24gYSB2YXJpYWJsZSwgc3Vicm91dGluZSwgb3IgbWV0aG9kXG4gICdsb2cnOiAxLFxuICAvLyAtIHJldHJpZXZlIHRoZSBuYXR1cmFsIGxvZ2FyaXRobSBmb3IgYSBudW1iZXJcbiAgbHN0YXQ6IDEsXG4gIC8vIC0gc3RhdCBhIHN5bWJvbGljIGxpbmtcbiAgbTogbnVsbCxcbiAgLy8gLSBtYXRjaCBhIHN0cmluZyB3aXRoIGEgcmVndWxhciBleHByZXNzaW9uIHBhdHRlcm5cbiAgbWFwOiAxLFxuICAvLyAtIGFwcGx5IGEgY2hhbmdlIHRvIGEgbGlzdCB0byBnZXQgYmFjayBhIG5ldyBsaXN0IHdpdGggdGhlIGNoYW5nZXNcbiAgbWtkaXI6IDEsXG4gIC8vIC0gY3JlYXRlIGEgZGlyZWN0b3J5XG4gIG1zZ2N0bDogMSxcbiAgLy8gLSBTeXNWIElQQyBtZXNzYWdlIGNvbnRyb2wgb3BlcmF0aW9uc1xuICBtc2dnZXQ6IDEsXG4gIC8vIC0gZ2V0IFN5c1YgSVBDIG1lc3NhZ2UgcXVldWVcbiAgbXNncmN2OiAxLFxuICAvLyAtIHJlY2VpdmUgYSBTeXNWIElQQyBtZXNzYWdlIGZyb20gYSBtZXNzYWdlIHF1ZXVlXG4gIG1zZ3NuZDogMSxcbiAgLy8gLSBzZW5kIGEgU3lzViBJUEMgbWVzc2FnZSB0byBhIG1lc3NhZ2UgcXVldWVcbiAgbXk6IDIsXG4gIC8vIC0gZGVjbGFyZSBhbmQgYXNzaWduIGEgbG9jYWwgdmFyaWFibGUgKGxleGljYWwgc2NvcGluZylcbiAgJ25ldyc6IDEsXG4gIC8vXG4gIG5leHQ6IDEsXG4gIC8vIC0gaXRlcmF0ZSBhIGJsb2NrIHByZW1hdHVyZWx5XG4gIG5vOiAxLFxuICAvLyAtIHVuaW1wb3J0IHNvbWUgbW9kdWxlIHN5bWJvbHMgb3Igc2VtYW50aWNzIGF0IGNvbXBpbGUgdGltZVxuICBvY3Q6IDEsXG4gIC8vIC0gY29udmVydCBhIHN0cmluZyB0byBhbiBvY3RhbCBudW1iZXJcbiAgb3BlbjogMSxcbiAgLy8gLSBvcGVuIGEgZmlsZSwgcGlwZSwgb3IgZGVzY3JpcHRvclxuICBvcGVuZGlyOiAxLFxuICAvLyAtIG9wZW4gYSBkaXJlY3RvcnlcbiAgb3JkOiAxLFxuICAvLyAtIGZpbmQgYSBjaGFyYWN0ZXIncyBudW1lcmljIHJlcHJlc2VudGF0aW9uXG4gIG91cjogMixcbiAgLy8gLSBkZWNsYXJlIGFuZCBhc3NpZ24gYSBwYWNrYWdlIHZhcmlhYmxlIChsZXhpY2FsIHNjb3BpbmcpXG4gIHBhY2s6IDEsXG4gIC8vIC0gY29udmVydCBhIGxpc3QgaW50byBhIGJpbmFyeSByZXByZXNlbnRhdGlvblxuICAncGFja2FnZSc6IDEsXG4gIC8vIC0gZGVjbGFyZSBhIHNlcGFyYXRlIGdsb2JhbCBuYW1lc3BhY2VcbiAgcGlwZTogMSxcbiAgLy8gLSBvcGVuIGEgcGFpciBvZiBjb25uZWN0ZWQgZmlsZWhhbmRsZXNcbiAgcG9wOiAxLFxuICAvLyAtIHJlbW92ZSB0aGUgbGFzdCBlbGVtZW50IGZyb20gYW4gYXJyYXkgYW5kIHJldHVybiBpdFxuICBwb3M6IDEsXG4gIC8vIC0gZmluZCBvciBzZXQgdGhlIG9mZnNldCBmb3IgdGhlIGxhc3QvbmV4dCBtLy9nIHNlYXJjaFxuICBwcmludDogMSxcbiAgLy8gLSBvdXRwdXQgYSBsaXN0IHRvIGEgZmlsZWhhbmRsZVxuICBwcmludGY6IDEsXG4gIC8vIC0gb3V0cHV0IGEgZm9ybWF0dGVkIGxpc3QgdG8gYSBmaWxlaGFuZGxlXG4gIHByb3RvdHlwZTogMSxcbiAgLy8gLSBnZXQgdGhlIHByb3RvdHlwZSAoaWYgYW55KSBvZiBhIHN1YnJvdXRpbmVcbiAgcHVzaDogMSxcbiAgLy8gLSBhcHBlbmQgb25lIG9yIG1vcmUgZWxlbWVudHMgdG8gYW4gYXJyYXlcbiAgcTogbnVsbCxcbiAgLy8gLSBzaW5nbHkgcXVvdGUgYSBzdHJpbmdcbiAgcXE6IG51bGwsXG4gIC8vIC0gZG91Ymx5IHF1b3RlIGEgc3RyaW5nXG4gIHFyOiBudWxsLFxuICAvLyAtIENvbXBpbGUgcGF0dGVyblxuICBxdW90ZW1ldGE6IG51bGwsXG4gIC8vIC0gcXVvdGUgcmVndWxhciBleHByZXNzaW9uIG1hZ2ljIGNoYXJhY3RlcnNcbiAgcXc6IG51bGwsXG4gIC8vIC0gcXVvdGUgYSBsaXN0IG9mIHdvcmRzXG4gIHF4OiBudWxsLFxuICAvLyAtIGJhY2txdW90ZSBxdW90ZSBhIHN0cmluZ1xuICByYW5kOiAxLFxuICAvLyAtIHJldHJpZXZlIHRoZSBuZXh0IHBzZXVkb3JhbmRvbSBudW1iZXJcbiAgcmVhZDogMSxcbiAgLy8gLSBmaXhlZC1sZW5ndGggYnVmZmVyZWQgaW5wdXQgZnJvbSBhIGZpbGVoYW5kbGVcbiAgcmVhZGRpcjogMSxcbiAgLy8gLSBnZXQgYSBkaXJlY3RvcnkgZnJvbSBhIGRpcmVjdG9yeSBoYW5kbGVcbiAgcmVhZGxpbmU6IDEsXG4gIC8vIC0gZmV0Y2ggYSByZWNvcmQgZnJvbSBhIGZpbGVcbiAgcmVhZGxpbms6IDEsXG4gIC8vIC0gZGV0ZXJtaW5lIHdoZXJlIGEgc3ltYm9saWMgbGluayBpcyBwb2ludGluZ1xuICByZWFkcGlwZTogMSxcbiAgLy8gLSBleGVjdXRlIGEgc3lzdGVtIGNvbW1hbmQgYW5kIGNvbGxlY3Qgc3RhbmRhcmQgb3V0cHV0XG4gIHJlY3Y6IDEsXG4gIC8vIC0gcmVjZWl2ZSBhIG1lc3NhZ2Ugb3ZlciBhIFNvY2tldFxuICByZWRvOiAxLFxuICAvLyAtIHN0YXJ0IHRoaXMgbG9vcCBpdGVyYXRpb24gb3ZlciBhZ2FpblxuICByZWY6IDEsXG4gIC8vIC0gZmluZCBvdXQgdGhlIHR5cGUgb2YgdGhpbmcgYmVpbmcgcmVmZXJlbmNlZFxuICByZW5hbWU6IDEsXG4gIC8vIC0gY2hhbmdlIGEgZmlsZW5hbWVcbiAgcmVxdWlyZTogMSxcbiAgLy8gLSBsb2FkIGluIGV4dGVybmFsIGZ1bmN0aW9ucyBmcm9tIGEgbGlicmFyeSBhdCBydW50aW1lXG4gIHJlc2V0OiAxLFxuICAvLyAtIGNsZWFyIGFsbCB2YXJpYWJsZXMgb2YgYSBnaXZlbiBuYW1lXG4gICdyZXR1cm4nOiAxLFxuICAvLyAtIGdldCBvdXQgb2YgYSBmdW5jdGlvbiBlYXJseVxuICByZXZlcnNlOiAxLFxuICAvLyAtIGZsaXAgYSBzdHJpbmcgb3IgYSBsaXN0XG4gIHJld2luZGRpcjogMSxcbiAgLy8gLSByZXNldCBkaXJlY3RvcnkgaGFuZGxlXG4gIHJpbmRleDogMSxcbiAgLy8gLSByaWdodC10by1sZWZ0IHN1YnN0cmluZyBzZWFyY2hcbiAgcm1kaXI6IDEsXG4gIC8vIC0gcmVtb3ZlIGEgZGlyZWN0b3J5XG4gIHM6IG51bGwsXG4gIC8vIC0gcmVwbGFjZSBhIHBhdHRlcm4gd2l0aCBhIHN0cmluZ1xuICBzYXk6IDEsXG4gIC8vIC0gcHJpbnQgd2l0aCBuZXdsaW5lXG4gIHNjYWxhcjogMSxcbiAgLy8gLSBmb3JjZSBhIHNjYWxhciBjb250ZXh0XG4gIHNlZWs6IDEsXG4gIC8vIC0gcmVwb3NpdGlvbiBmaWxlIHBvaW50ZXIgZm9yIHJhbmRvbS1hY2Nlc3MgSS9PXG4gIHNlZWtkaXI6IDEsXG4gIC8vIC0gcmVwb3NpdGlvbiBkaXJlY3RvcnkgcG9pbnRlclxuICBzZWxlY3Q6IDEsXG4gIC8vIC0gcmVzZXQgZGVmYXVsdCBvdXRwdXQgb3IgZG8gSS9PIG11bHRpcGxleGluZ1xuICBzZW1jdGw6IDEsXG4gIC8vIC0gU3lzViBzZW1hcGhvcmUgY29udHJvbCBvcGVyYXRpb25zXG4gIHNlbWdldDogMSxcbiAgLy8gLSBnZXQgc2V0IG9mIFN5c1Ygc2VtYXBob3Jlc1xuICBzZW1vcDogMSxcbiAgLy8gLSBTeXNWIHNlbWFwaG9yZSBvcGVyYXRpb25zXG4gIHNlbmQ6IDEsXG4gIC8vIC0gc2VuZCBhIG1lc3NhZ2Ugb3ZlciBhIHNvY2tldFxuICBzZXRncmVudDogMSxcbiAgLy8gLSBwcmVwYXJlIGdyb3VwIGZpbGUgZm9yIHVzZVxuICBzZXRob3N0ZW50OiAxLFxuICAvLyAtIHByZXBhcmUgaG9zdHMgZmlsZSBmb3IgdXNlXG4gIHNldG5ldGVudDogMSxcbiAgLy8gLSBwcmVwYXJlIG5ldHdvcmtzIGZpbGUgZm9yIHVzZVxuICBzZXRwZ3JwOiAxLFxuICAvLyAtIHNldCB0aGUgcHJvY2VzcyBncm91cCBvZiBhIHByb2Nlc3NcbiAgc2V0cHJpb3JpdHk6IDEsXG4gIC8vIC0gc2V0IGEgcHJvY2VzcydzIG5pY2UgdmFsdWVcbiAgc2V0cHJvdG9lbnQ6IDEsXG4gIC8vIC0gcHJlcGFyZSBwcm90b2NvbHMgZmlsZSBmb3IgdXNlXG4gIHNldHB3ZW50OiAxLFxuICAvLyAtIHByZXBhcmUgcGFzc3dkIGZpbGUgZm9yIHVzZVxuICBzZXRzZXJ2ZW50OiAxLFxuICAvLyAtIHByZXBhcmUgc2VydmljZXMgZmlsZSBmb3IgdXNlXG4gIHNldHNvY2tvcHQ6IDEsXG4gIC8vIC0gc2V0IHNvbWUgc29ja2V0IG9wdGlvbnNcbiAgc2hpZnQ6IDEsXG4gIC8vIC0gcmVtb3ZlIHRoZSBmaXJzdCBlbGVtZW50IG9mIGFuIGFycmF5LCBhbmQgcmV0dXJuIGl0XG4gIHNobWN0bDogMSxcbiAgLy8gLSBTeXNWIHNoYXJlZCBtZW1vcnkgb3BlcmF0aW9uc1xuICBzaG1nZXQ6IDEsXG4gIC8vIC0gZ2V0IFN5c1Ygc2hhcmVkIG1lbW9yeSBzZWdtZW50IGlkZW50aWZpZXJcbiAgc2htcmVhZDogMSxcbiAgLy8gLSByZWFkIFN5c1Ygc2hhcmVkIG1lbW9yeVxuICBzaG13cml0ZTogMSxcbiAgLy8gLSB3cml0ZSBTeXNWIHNoYXJlZCBtZW1vcnlcbiAgc2h1dGRvd246IDEsXG4gIC8vIC0gY2xvc2UgZG93biBqdXN0IGhhbGYgb2YgYSBzb2NrZXQgY29ubmVjdGlvblxuICAnc2luJzogMSxcbiAgLy8gLSByZXR1cm4gdGhlIHNpbmUgb2YgYSBudW1iZXJcbiAgc2xlZXA6IDEsXG4gIC8vIC0gYmxvY2sgZm9yIHNvbWUgbnVtYmVyIG9mIHNlY29uZHNcbiAgc29ja2V0OiAxLFxuICAvLyAtIGNyZWF0ZSBhIHNvY2tldFxuICBzb2NrZXRwYWlyOiAxLFxuICAvLyAtIGNyZWF0ZSBhIHBhaXIgb2Ygc29ja2V0c1xuICAnc29ydCc6IDEsXG4gIC8vIC0gc29ydCBhIGxpc3Qgb2YgdmFsdWVzXG4gIHNwbGljZTogMSxcbiAgLy8gLSBhZGQgb3IgcmVtb3ZlIGVsZW1lbnRzIGFueXdoZXJlIGluIGFuIGFycmF5XG4gICdzcGxpdCc6IDEsXG4gIC8vIC0gc3BsaXQgdXAgYSBzdHJpbmcgdXNpbmcgYSByZWdleHAgZGVsaW1pdGVyXG4gIHNwcmludGY6IDEsXG4gIC8vIC0gZm9ybWF0dGVkIHByaW50IGludG8gYSBzdHJpbmdcbiAgJ3NxcnQnOiAxLFxuICAvLyAtIHNxdWFyZSByb290IGZ1bmN0aW9uXG4gIHNyYW5kOiAxLFxuICAvLyAtIHNlZWQgdGhlIHJhbmRvbSBudW1iZXIgZ2VuZXJhdG9yXG4gIHN0YXQ6IDEsXG4gIC8vIC0gZ2V0IGEgZmlsZSdzIHN0YXR1cyBpbmZvcm1hdGlvblxuICBzdGF0ZTogMSxcbiAgLy8gLSBkZWNsYXJlIGFuZCBhc3NpZ24gYSBzdGF0ZSB2YXJpYWJsZSAocGVyc2lzdGVudCBsZXhpY2FsIHNjb3BpbmcpXG4gIHN0dWR5OiAxLFxuICAvLyAtIG9wdGltaXplIGlucHV0IGRhdGEgZm9yIHJlcGVhdGVkIHNlYXJjaGVzXG4gICdzdWInOiAxLFxuICAvLyAtIGRlY2xhcmUgYSBzdWJyb3V0aW5lLCBwb3NzaWJseSBhbm9ueW1vdXNseVxuICAnc3Vic3RyJzogMSxcbiAgLy8gLSBnZXQgb3IgYWx0ZXIgYSBwb3J0aW9uIG9mIGEgc3RyaW5nXG4gIHN5bWxpbms6IDEsXG4gIC8vIC0gY3JlYXRlIGEgc3ltYm9saWMgbGluayB0byBhIGZpbGVcbiAgc3lzY2FsbDogMSxcbiAgLy8gLSBleGVjdXRlIGFuIGFyYml0cmFyeSBzeXN0ZW0gY2FsbFxuICBzeXNvcGVuOiAxLFxuICAvLyAtIG9wZW4gYSBmaWxlLCBwaXBlLCBvciBkZXNjcmlwdG9yXG4gIHN5c3JlYWQ6IDEsXG4gIC8vIC0gZml4ZWQtbGVuZ3RoIHVuYnVmZmVyZWQgaW5wdXQgZnJvbSBhIGZpbGVoYW5kbGVcbiAgc3lzc2VlazogMSxcbiAgLy8gLSBwb3NpdGlvbiBJL08gcG9pbnRlciBvbiBoYW5kbGUgdXNlZCB3aXRoIHN5c3JlYWQgYW5kIHN5c3dyaXRlXG4gIHN5c3RlbTogMSxcbiAgLy8gLSBydW4gYSBzZXBhcmF0ZSBwcm9ncmFtXG4gIHN5c3dyaXRlOiAxLFxuICAvLyAtIGZpeGVkLWxlbmd0aCB1bmJ1ZmZlcmVkIG91dHB1dCB0byBhIGZpbGVoYW5kbGVcbiAgdGVsbDogMSxcbiAgLy8gLSBnZXQgY3VycmVudCBzZWVrcG9pbnRlciBvbiBhIGZpbGVoYW5kbGVcbiAgdGVsbGRpcjogMSxcbiAgLy8gLSBnZXQgY3VycmVudCBzZWVrcG9pbnRlciBvbiBhIGRpcmVjdG9yeSBoYW5kbGVcbiAgdGllOiAxLFxuICAvLyAtIGJpbmQgYSB2YXJpYWJsZSB0byBhbiBvYmplY3QgY2xhc3NcbiAgdGllZDogMSxcbiAgLy8gLSBnZXQgYSByZWZlcmVuY2UgdG8gdGhlIG9iamVjdCB1bmRlcmx5aW5nIGEgdGllZCB2YXJpYWJsZVxuICB0aW1lOiAxLFxuICAvLyAtIHJldHVybiBudW1iZXIgb2Ygc2Vjb25kcyBzaW5jZSAxOTcwXG4gIHRpbWVzOiAxLFxuICAvLyAtIHJldHVybiBlbGFwc2VkIHRpbWUgZm9yIHNlbGYgYW5kIGNoaWxkIHByb2Nlc3Nlc1xuICB0cjogbnVsbCxcbiAgLy8gLSB0cmFuc2xpdGVyYXRlIGEgc3RyaW5nXG4gIHRydW5jYXRlOiAxLFxuICAvLyAtIHNob3J0ZW4gYSBmaWxlXG4gIHVjOiAxLFxuICAvLyAtIHJldHVybiB1cHBlci1jYXNlIHZlcnNpb24gb2YgYSBzdHJpbmdcbiAgdWNmaXJzdDogMSxcbiAgLy8gLSByZXR1cm4gYSBzdHJpbmcgd2l0aCBqdXN0IHRoZSBuZXh0IGxldHRlciBpbiB1cHBlciBjYXNlXG4gIHVtYXNrOiAxLFxuICAvLyAtIHNldCBmaWxlIGNyZWF0aW9uIG1vZGUgbWFza1xuICB1bmRlZjogMSxcbiAgLy8gLSByZW1vdmUgYSB2YXJpYWJsZSBvciBmdW5jdGlvbiBkZWZpbml0aW9uXG4gIHVubGluazogMSxcbiAgLy8gLSByZW1vdmUgb25lIGxpbmsgdG8gYSBmaWxlXG4gIHVucGFjazogMSxcbiAgLy8gLSBjb252ZXJ0IGJpbmFyeSBzdHJ1Y3R1cmUgaW50byBub3JtYWwgcGVybCB2YXJpYWJsZXNcbiAgdW5zaGlmdDogMSxcbiAgLy8gLSBwcmVwZW5kIG1vcmUgZWxlbWVudHMgdG8gdGhlIGJlZ2lubmluZyBvZiBhIGxpc3RcbiAgdW50aWU6IDEsXG4gIC8vIC0gYnJlYWsgYSB0aWUgYmluZGluZyB0byBhIHZhcmlhYmxlXG4gIHVzZTogMSxcbiAgLy8gLSBsb2FkIGluIGEgbW9kdWxlIGF0IGNvbXBpbGUgdGltZVxuICB1dGltZTogMSxcbiAgLy8gLSBzZXQgYSBmaWxlJ3MgbGFzdCBhY2Nlc3MgYW5kIG1vZGlmeSB0aW1lc1xuICB2YWx1ZXM6IDEsXG4gIC8vIC0gcmV0dXJuIGEgbGlzdCBvZiB0aGUgdmFsdWVzIGluIGEgaGFzaFxuICB2ZWM6IDEsXG4gIC8vIC0gdGVzdCBvciBzZXQgcGFydGljdWxhciBiaXRzIGluIGEgc3RyaW5nXG4gIHdhaXQ6IDEsXG4gIC8vIC0gd2FpdCBmb3IgYW55IGNoaWxkIHByb2Nlc3MgdG8gZGllXG4gIHdhaXRwaWQ6IDEsXG4gIC8vIC0gd2FpdCBmb3IgYSBwYXJ0aWN1bGFyIGNoaWxkIHByb2Nlc3MgdG8gZGllXG4gIHdhbnRhcnJheTogMSxcbiAgLy8gLSBnZXQgdm9pZCB2cyBzY2FsYXIgdnMgbGlzdCBjb250ZXh0IG9mIGN1cnJlbnQgc3Vicm91dGluZSBjYWxsXG4gIHdhcm46IDEsXG4gIC8vIC0gcHJpbnQgZGVidWdnaW5nIGluZm9cbiAgd2hlbjogMSxcbiAgLy9cbiAgd3JpdGU6IDEsXG4gIC8vIC0gcHJpbnQgYSBwaWN0dXJlIHJlY29yZFxuICB5OiBudWxsXG59OyAvLyAtIHRyYW5zbGl0ZXJhdGUgYSBzdHJpbmdcblxudmFyIFJYc3R5bGUgPSBcInN0cmluZy5zcGVjaWFsXCI7XG52YXIgUlhtb2RpZmllcnMgPSAvW2dvc2V4aW1hY3BsdWRdLzsgLy8gTk9URTogXCJtXCIsIFwic1wiLCBcInlcIiBhbmQgXCJ0clwiIG5lZWQgdG8gY29ycmVjdCByZWFsIG1vZGlmaWVycyBmb3IgZWFjaCByZWdleHAgdHlwZVxuXG5mdW5jdGlvbiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIGNoYWluLCBzdHlsZSwgdGFpbCkge1xuICAvLyBOT1RFOiBjaGFpbi5sZW5ndGggPiAyIGlzIG5vdCB3b3JraW5nIG5vdyAoaXQncyBmb3Igc1suLi5dWy4uLl1nZW9zOylcbiAgc3RhdGUuY2hhaW4gPSBudWxsOyAvLyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAxMiAgIDN0YWlsXG4gIHN0YXRlLnN0eWxlID0gbnVsbDtcbiAgc3RhdGUudGFpbCA9IG51bGw7XG4gIHN0YXRlLnRva2VuaXplID0gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZSA9IGZhbHNlLFxuICAgICAgYyxcbiAgICAgIGkgPSAwO1xuICAgIHdoaWxlIChjID0gc3RyZWFtLm5leHQoKSkge1xuICAgICAgaWYgKGMgPT09IGNoYWluW2ldICYmICFlKSB7XG4gICAgICAgIGlmIChjaGFpblsrK2ldICE9PSB1bmRlZmluZWQpIHtcbiAgICAgICAgICBzdGF0ZS5jaGFpbiA9IGNoYWluW2ldO1xuICAgICAgICAgIHN0YXRlLnN0eWxlID0gc3R5bGU7XG4gICAgICAgICAgc3RhdGUudGFpbCA9IHRhaWw7XG4gICAgICAgIH0gZWxzZSBpZiAodGFpbCkgc3RyZWFtLmVhdFdoaWxlKHRhaWwpO1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuUGVybDtcbiAgICAgICAgcmV0dXJuIHN0eWxlO1xuICAgICAgfVxuICAgICAgZSA9ICFlICYmIGMgPT0gXCJcXFxcXCI7XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfTtcbiAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xufVxuZnVuY3Rpb24gdG9rZW5TT01FVEhJTkcoc3RyZWFtLCBzdGF0ZSwgc3RyaW5nKSB7XG4gIHN0YXRlLnRva2VuaXplID0gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnN0cmluZyA9PSBzdHJpbmcpIHN0YXRlLnRva2VuaXplID0gdG9rZW5QZXJsO1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfTtcbiAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xufVxuZnVuY3Rpb24gdG9rZW5QZXJsKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgaWYgKHN0YXRlLmNoYWluKSByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBzdGF0ZS5jaGFpbiwgc3RhdGUuc3R5bGUsIHN0YXRlLnRhaWwpO1xuICBpZiAoc3RyZWFtLm1hdGNoKC9eKFxcLT8oKFxcZFtcXGRfXSopP1xcLlxcZCsoZVsrLV0/XFxkKyk/fFxcZCtcXC5cXGQqKXwweFtcXGRhLWZBLUZfXSt8MGJbMDFfXSt8XFxkW1xcZF9dKihlWystXT9cXGQrKT8pLykpIHJldHVybiAnbnVtYmVyJztcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXjw8KD89W19hLXpBLVpdKS8pKSB7XG4gICAgLy8gTk9URTogPDxTT01FVEhJTkdcXG4uLi5cXG5TT01FVEhJTkdcXG5cbiAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgIHJldHVybiB0b2tlblNPTUVUSElORyhzdHJlYW0sIHN0YXRlLCBzdHJlYW0uY3VycmVudCgpLnN1YnN0cigyKSk7XG4gIH1cbiAgaWYgKHN0cmVhbS5zb2woKSAmJiBzdHJlYW0ubWF0Y2goL15cXD1pdGVtKD8hXFx3KS8pKSB7XG4gICAgLy8gTk9URTogXFxuPWl0ZW0uLi5cXG49Y3V0XFxuXG4gICAgcmV0dXJuIHRva2VuU09NRVRISU5HKHN0cmVhbSwgc3RhdGUsICc9Y3V0Jyk7XG4gIH1cbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGNoID09ICdcIicgfHwgY2ggPT0gXCInXCIpIHtcbiAgICAvLyBOT1RFOiAnIG9yIFwiIG9yIDw8J1NPTUVUSElORydcXG4uLi5cXG5TT01FVEhJTkdcXG4gb3IgPDxcIlNPTUVUSElOR1wiXFxuLi4uXFxuU09NRVRISU5HXFxuXG4gICAgaWYgKHByZWZpeChzdHJlYW0sIDMpID09IFwiPDxcIiArIGNoKSB7XG4gICAgICB2YXIgcCA9IHN0cmVhbS5wb3M7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgICAgdmFyIG4gPSBzdHJlYW0uY3VycmVudCgpLnN1YnN0cigxKTtcbiAgICAgIGlmIChuICYmIHN0cmVhbS5lYXQoY2gpKSByZXR1cm4gdG9rZW5TT01FVEhJTkcoc3RyZWFtLCBzdGF0ZSwgbik7XG4gICAgICBzdHJlYW0ucG9zID0gcDtcbiAgICB9XG4gICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW2NoXSwgXCJzdHJpbmdcIik7XG4gIH1cbiAgaWYgKGNoID09IFwicVwiKSB7XG4gICAgdmFyIGMgPSBsb29rKHN0cmVhbSwgLTIpO1xuICAgIGlmICghKGMgJiYgL1xcdy8udGVzdChjKSkpIHtcbiAgICAgIGMgPSBsb29rKHN0cmVhbSwgMCk7XG4gICAgICBpZiAoYyA9PSBcInhcIikge1xuICAgICAgICBjID0gbG9vayhzdHJlYW0sIDEpO1xuICAgICAgICBpZiAoYyA9PSBcIihcIikge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDIpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIilcIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoYyA9PSBcIltcIikge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDIpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIl1cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoYyA9PSBcIntcIikge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDIpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIn1cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoYyA9PSBcIjxcIikge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDIpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIj5cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoL1tcXF4nXCIhflxcL10vLnRlc3QoYykpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAxKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbc3RyZWFtLmVhdChjKV0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIGlmIChjID09IFwicVwiKSB7XG4gICAgICAgIGMgPSBsb29rKHN0cmVhbSwgMSk7XG4gICAgICAgIGlmIChjID09IFwiKFwiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMik7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiKVwiXSwgXCJzdHJpbmdcIik7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCJbXCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAyKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCJdXCJdLCBcInN0cmluZ1wiKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoYyA9PSBcIntcIikge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDIpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIn1cIl0sIFwic3RyaW5nXCIpO1xuICAgICAgICB9XG4gICAgICAgIGlmIChjID09IFwiPFwiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMik7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiPlwiXSwgXCJzdHJpbmdcIik7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKC9bXFxeJ1wiIX5cXC9dLy50ZXN0KGMpKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMSk7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW3N0cmVhbS5lYXQoYyldLCBcInN0cmluZ1wiKTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIGlmIChjID09IFwid1wiKSB7XG4gICAgICAgIGMgPSBsb29rKHN0cmVhbSwgMSk7XG4gICAgICAgIGlmIChjID09IFwiKFwiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMik7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiKVwiXSwgXCJicmFja2V0XCIpO1xuICAgICAgICB9XG4gICAgICAgIGlmIChjID09IFwiW1wiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMik7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiXVwiXSwgXCJicmFja2V0XCIpO1xuICAgICAgICB9XG4gICAgICAgIGlmIChjID09IFwie1wiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMik7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wifVwiXSwgXCJicmFja2V0XCIpO1xuICAgICAgICB9XG4gICAgICAgIGlmIChjID09IFwiPFwiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMik7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiPlwiXSwgXCJicmFja2V0XCIpO1xuICAgICAgICB9XG4gICAgICAgIGlmICgvW1xcXidcIiF+XFwvXS8udGVzdChjKSkge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDEpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtzdHJlYW0uZWF0KGMpXSwgXCJicmFja2V0XCIpO1xuICAgICAgICB9XG4gICAgICB9IGVsc2UgaWYgKGMgPT0gXCJyXCIpIHtcbiAgICAgICAgYyA9IGxvb2soc3RyZWFtLCAxKTtcbiAgICAgICAgaWYgKGMgPT0gXCIoXCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAyKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCIpXCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCJbXCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAyKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCJdXCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCJ7XCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAyKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCJ9XCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCI8XCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAyKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCI+XCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKC9bXFxeJ1wiIX5cXC9dLy50ZXN0KGMpKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMSk7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW3N0cmVhbS5lYXQoYyldLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSBpZiAoL1tcXF4nXCIhflxcLyhcXFt7PF0vLnRlc3QoYykpIHtcbiAgICAgICAgaWYgKGMgPT0gXCIoXCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAxKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCIpXCJdLCBcInN0cmluZ1wiKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoYyA9PSBcIltcIikge1xuICAgICAgICAgIGVhdFN1ZmZpeChzdHJlYW0sIDEpO1xuICAgICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIl1cIl0sIFwic3RyaW5nXCIpO1xuICAgICAgICB9XG4gICAgICAgIGlmIChjID09IFwie1wiKSB7XG4gICAgICAgICAgZWF0U3VmZml4KHN0cmVhbSwgMSk7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wifVwiXSwgXCJzdHJpbmdcIik7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCI8XCIpIHtcbiAgICAgICAgICBlYXRTdWZmaXgoc3RyZWFtLCAxKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCI+XCJdLCBcInN0cmluZ1wiKTtcbiAgICAgICAgfVxuICAgICAgICBpZiAoL1tcXF4nXCIhflxcL10vLnRlc3QoYykpIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbc3RyZWFtLmVhdChjKV0sIFwic3RyaW5nXCIpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICB9XG4gIGlmIChjaCA9PSBcIm1cIikge1xuICAgIHZhciBjID0gbG9vayhzdHJlYW0sIC0yKTtcbiAgICBpZiAoIShjICYmIC9cXHcvLnRlc3QoYykpKSB7XG4gICAgICBjID0gc3RyZWFtLmVhdCgvWyhcXFt7PFxcXidcIiF+XFwvXS8pO1xuICAgICAgaWYgKGMpIHtcbiAgICAgICAgaWYgKC9bXFxeJ1wiIX5cXC9dLy50ZXN0KGMpKSB7XG4gICAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW2NdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCIoXCIpIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCIpXCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCJbXCIpIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCJdXCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCJ7XCIpIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCJ9XCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGMgPT0gXCI8XCIpIHtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCI+XCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gIH1cbiAgaWYgKGNoID09IFwic1wiKSB7XG4gICAgdmFyIGMgPSAvW1xcLz5cXF19KVxcd10vLnRlc3QobG9vayhzdHJlYW0sIC0yKSk7XG4gICAgaWYgKCFjKSB7XG4gICAgICBjID0gc3RyZWFtLmVhdCgvWyhcXFt7PFxcXidcIiF+XFwvXS8pO1xuICAgICAgaWYgKGMpIHtcbiAgICAgICAgaWYgKGMgPT0gXCJbXCIpIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIl1cIiwgXCJdXCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIGlmIChjID09IFwie1wiKSByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCJ9XCIsIFwifVwiXSwgUlhzdHlsZSwgUlhtb2RpZmllcnMpO1xuICAgICAgICBpZiAoYyA9PSBcIjxcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiPlwiLCBcIj5cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgaWYgKGMgPT0gXCIoXCIpIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIilcIiwgXCIpXCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtjLCBjXSwgUlhzdHlsZSwgUlhtb2RpZmllcnMpO1xuICAgICAgfVxuICAgIH1cbiAgfVxuICBpZiAoY2ggPT0gXCJ5XCIpIHtcbiAgICB2YXIgYyA9IC9bXFwvPlxcXX0pXFx3XS8udGVzdChsb29rKHN0cmVhbSwgLTIpKTtcbiAgICBpZiAoIWMpIHtcbiAgICAgIGMgPSBzdHJlYW0uZWF0KC9bKFxcW3s8XFxeJ1wiIX5cXC9dLyk7XG4gICAgICBpZiAoYykge1xuICAgICAgICBpZiAoYyA9PSBcIltcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiXVwiLCBcIl1cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgaWYgKGMgPT0gXCJ7XCIpIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtcIn1cIiwgXCJ9XCJdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICAgIGlmIChjID09IFwiPFwiKSByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbXCI+XCIsIFwiPlwiXSwgUlhzdHlsZSwgUlhtb2RpZmllcnMpO1xuICAgICAgICBpZiAoYyA9PSBcIihcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiKVwiLCBcIilcIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW2MsIGNdLCBSWHN0eWxlLCBSWG1vZGlmaWVycyk7XG4gICAgICB9XG4gICAgfVxuICB9XG4gIGlmIChjaCA9PSBcInRcIikge1xuICAgIHZhciBjID0gL1tcXC8+XFxdfSlcXHddLy50ZXN0KGxvb2soc3RyZWFtLCAtMikpO1xuICAgIGlmICghYykge1xuICAgICAgYyA9IHN0cmVhbS5lYXQoXCJyXCIpO1xuICAgICAgaWYgKGMpIHtcbiAgICAgICAgYyA9IHN0cmVhbS5lYXQoL1soXFxbezxcXF4nXCIhflxcL10vKTtcbiAgICAgICAgaWYgKGMpIHtcbiAgICAgICAgICBpZiAoYyA9PSBcIltcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiXVwiLCBcIl1cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgICBpZiAoYyA9PSBcIntcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wifVwiLCBcIn1cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgICBpZiAoYyA9PSBcIjxcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiPlwiLCBcIj5cIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgICBpZiAoYyA9PSBcIihcIikgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgW1wiKVwiLCBcIilcIl0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbYywgY10sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgfVxuICBpZiAoY2ggPT0gXCJgXCIpIHtcbiAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbY2hdLCBcImJ1aWx0aW5cIik7XG4gIH1cbiAgaWYgKGNoID09IFwiL1wiKSB7XG4gICAgaWYgKCEvflxccyokLy50ZXN0KHByZWZpeChzdHJlYW0pKSkgcmV0dXJuIFwib3BlcmF0b3JcIjtlbHNlIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFtjaF0sIFJYc3R5bGUsIFJYbW9kaWZpZXJzKTtcbiAgfVxuICBpZiAoY2ggPT0gXCIkXCIpIHtcbiAgICB2YXIgcCA9IHN0cmVhbS5wb3M7XG4gICAgaWYgKHN0cmVhbS5lYXRXaGlsZSgvXFxkLykgfHwgc3RyZWFtLmVhdChcIntcIikgJiYgc3RyZWFtLmVhdFdoaWxlKC9cXGQvKSAmJiBzdHJlYW0uZWF0KFwifVwiKSkgcmV0dXJuIFwiYnVpbHRpblwiO2Vsc2Ugc3RyZWFtLnBvcyA9IHA7XG4gIH1cbiAgaWYgKC9bJEAlXS8udGVzdChjaCkpIHtcbiAgICB2YXIgcCA9IHN0cmVhbS5wb3M7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCJeXCIpICYmIHN0cmVhbS5lYXQoL1tBLVpdLykgfHwgIS9bQCQlJl0vLnRlc3QobG9vayhzdHJlYW0sIC0yKSkgJiYgc3RyZWFtLmVhdCgvWz18XFxcXFxcLSM/QDs6JmB+XFxeIVxcW1xcXSonXCIkKy4sXFwvPD4oKV0vKSkge1xuICAgICAgdmFyIGMgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgICAgaWYgKFBFUkxbY10pIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgICB9XG4gICAgc3RyZWFtLnBvcyA9IHA7XG4gIH1cbiAgaWYgKC9bJEAlJl0vLnRlc3QoY2gpKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRXaGlsZSgvW1xcdyRdLykgfHwgc3RyZWFtLmVhdChcIntcIikgJiYgc3RyZWFtLmVhdFdoaWxlKC9bXFx3JF0vKSAmJiBzdHJlYW0uZWF0KFwifVwiKSkge1xuICAgICAgdmFyIGMgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgICAgaWYgKFBFUkxbY10pIHJldHVybiBcImJ1aWx0aW5cIjtlbHNlIHJldHVybiBcInZhcmlhYmxlXCI7XG4gICAgfVxuICB9XG4gIGlmIChjaCA9PSBcIiNcIikge1xuICAgIGlmIChsb29rKHN0cmVhbSwgLTIpICE9IFwiJFwiKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICB9XG4gIGlmICgvWzorXFwtXFxeKiQmJUA9PD4hP3xcXC9+XFwuXS8udGVzdChjaCkpIHtcbiAgICB2YXIgcCA9IHN0cmVhbS5wb3M7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bOitcXC1cXF4qJCYlQD08PiE/fFxcL35cXC5dLyk7XG4gICAgaWYgKFBFUkxbc3RyZWFtLmN1cnJlbnQoKV0pIHJldHVybiBcIm9wZXJhdG9yXCI7ZWxzZSBzdHJlYW0ucG9zID0gcDtcbiAgfVxuICBpZiAoY2ggPT0gXCJfXCIpIHtcbiAgICBpZiAoc3RyZWFtLnBvcyA9PSAxKSB7XG4gICAgICBpZiAoc3VmZml4KHN0cmVhbSwgNikgPT0gXCJfRU5EX19cIikge1xuICAgICAgICByZXR1cm4gdG9rZW5DaGFpbihzdHJlYW0sIHN0YXRlLCBbJ1xcMCddLCBcImNvbW1lbnRcIik7XG4gICAgICB9IGVsc2UgaWYgKHN1ZmZpeChzdHJlYW0sIDcpID09IFwiX0RBVEFfX1wiKSB7XG4gICAgICAgIHJldHVybiB0b2tlbkNoYWluKHN0cmVhbSwgc3RhdGUsIFsnXFwwJ10sIFwiYnVpbHRpblwiKTtcbiAgICAgIH0gZWxzZSBpZiAoc3VmZml4KHN0cmVhbSwgNykgPT0gXCJfQ19fXCIpIHtcbiAgICAgICAgcmV0dXJuIHRva2VuQ2hhaW4oc3RyZWFtLCBzdGF0ZSwgWydcXDAnXSwgXCJzdHJpbmdcIik7XG4gICAgICB9XG4gICAgfVxuICB9XG4gIGlmICgvXFx3Ly50ZXN0KGNoKSkge1xuICAgIHZhciBwID0gc3RyZWFtLnBvcztcbiAgICBpZiAobG9vayhzdHJlYW0sIC0yKSA9PSBcIntcIiAmJiAobG9vayhzdHJlYW0sIDApID09IFwifVwiIHx8IHN0cmVhbS5lYXRXaGlsZSgvXFx3LykgJiYgbG9vayhzdHJlYW0sIDApID09IFwifVwiKSkgcmV0dXJuIFwic3RyaW5nXCI7ZWxzZSBzdHJlYW0ucG9zID0gcDtcbiAgfVxuICBpZiAoL1tBLVpdLy50ZXN0KGNoKSkge1xuICAgIHZhciBsID0gbG9vayhzdHJlYW0sIC0yKTtcbiAgICB2YXIgcCA9IHN0cmVhbS5wb3M7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bQS1aX10vKTtcbiAgICBpZiAoL1tcXGRhLXpdLy50ZXN0KGxvb2soc3RyZWFtLCAwKSkpIHtcbiAgICAgIHN0cmVhbS5wb3MgPSBwO1xuICAgIH0gZWxzZSB7XG4gICAgICB2YXIgYyA9IFBFUkxbc3RyZWFtLmN1cnJlbnQoKV07XG4gICAgICBpZiAoIWMpIHJldHVybiBcIm1ldGFcIjtcbiAgICAgIGlmIChjWzFdKSBjID0gY1swXTtcbiAgICAgIGlmIChsICE9IFwiOlwiKSB7XG4gICAgICAgIGlmIChjID09IDEpIHJldHVybiBcImtleXdvcmRcIjtlbHNlIGlmIChjID09IDIpIHJldHVybiBcImRlZlwiO2Vsc2UgaWYgKGMgPT0gMykgcmV0dXJuIFwiYXRvbVwiO2Vsc2UgaWYgKGMgPT0gNCkgcmV0dXJuIFwib3BlcmF0b3JcIjtlbHNlIGlmIChjID09IDUpIHJldHVybiBcImJ1aWx0aW5cIjtlbHNlIHJldHVybiBcIm1ldGFcIjtcbiAgICAgIH0gZWxzZSByZXR1cm4gXCJtZXRhXCI7XG4gICAgfVxuICB9XG4gIGlmICgvW2EtekEtWl9dLy50ZXN0KGNoKSkge1xuICAgIHZhciBsID0gbG9vayhzdHJlYW0sIC0yKTtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgIHZhciBjID0gUEVSTFtzdHJlYW0uY3VycmVudCgpXTtcbiAgICBpZiAoIWMpIHJldHVybiBcIm1ldGFcIjtcbiAgICBpZiAoY1sxXSkgYyA9IGNbMF07XG4gICAgaWYgKGwgIT0gXCI6XCIpIHtcbiAgICAgIGlmIChjID09IDEpIHJldHVybiBcImtleXdvcmRcIjtlbHNlIGlmIChjID09IDIpIHJldHVybiBcImRlZlwiO2Vsc2UgaWYgKGMgPT0gMykgcmV0dXJuIFwiYXRvbVwiO2Vsc2UgaWYgKGMgPT0gNCkgcmV0dXJuIFwib3BlcmF0b3JcIjtlbHNlIGlmIChjID09IDUpIHJldHVybiBcImJ1aWx0aW5cIjtlbHNlIHJldHVybiBcIm1ldGFcIjtcbiAgICB9IGVsc2UgcmV0dXJuIFwibWV0YVwiO1xuICB9XG4gIHJldHVybiBudWxsO1xufVxuZXhwb3J0IGNvbnN0IHBlcmwgPSB7XG4gIG5hbWU6IFwicGVybFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlblBlcmwsXG4gICAgICBjaGFpbjogbnVsbCxcbiAgICAgIHN0eWxlOiBudWxsLFxuICAgICAgdGFpbDogbnVsbFxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHJldHVybiAoc3RhdGUudG9rZW5pemUgfHwgdG9rZW5QZXJsKShzdHJlYW0sIHN0YXRlKTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIjXCJcbiAgICB9LFxuICAgIHdvcmRDaGFyczogXCIkXCJcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9