"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6565],{

/***/ 33866
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __spreadArray = this && this.__spreadArray || function (to, from, pack) {
  if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
    if (ar || !(i in from)) {
      if (!ar) ar = Array.prototype.slice.call(from, 0, i);
      ar[i] = from[i];
    }
  }
  return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.Package = exports.PackageError = void 0;
var loader_js_1 = __webpack_require__(57895);
var PackageError = function (_super) {
  __extends(PackageError, _super);
  function PackageError(message, name) {
    var _this = _super.call(this, message) || this;
    _this.package = name;
    return _this;
  }
  return PackageError;
}(Error);
exports.PackageError = PackageError;
var Package = function () {
  function Package(name, noLoad) {
    if (noLoad === void 0) {
      noLoad = false;
    }
    this.isLoaded = false;
    this.isLoading = false;
    this.hasFailed = false;
    this.dependents = [];
    this.dependencies = [];
    this.dependencyCount = 0;
    this.provided = [];
    this.name = name;
    this.noLoad = noLoad;
    Package.packages.set(name, this);
    this.promise = this.makePromise(this.makeDependencies());
  }
  Object.defineProperty(Package.prototype, "canLoad", {
    get: function () {
      return this.dependencyCount === 0 && !this.noLoad && !this.isLoading && !this.hasFailed;
    },
    enumerable: false,
    configurable: true
  });
  Package.resolvePath = function (name, addExtension) {
    if (addExtension === void 0) {
      addExtension = true;
    }
    var data = {
      name: name,
      original: name,
      addExtension: addExtension
    };
    loader_js_1.Loader.pathFilters.execute(data);
    return data.name;
  };
  Package.loadAll = function () {
    var e_1, _a;
    try {
      for (var _b = __values(this.packages.values()), _c = _b.next(); !_c.done; _c = _b.next()) {
        var extension = _c.value;
        if (extension.canLoad) {
          extension.load();
        }
      }
    } catch (e_1_1) {
      e_1 = {
        error: e_1_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_1) throw e_1.error;
      }
    }
  };
  Package.prototype.makeDependencies = function () {
    var e_2, _a;
    var promises = [];
    var map = Package.packages;
    var noLoad = this.noLoad;
    var name = this.name;
    var dependencies = [];
    if (loader_js_1.CONFIG.dependencies.hasOwnProperty(name)) {
      dependencies.push.apply(dependencies, __spreadArray([], __read(loader_js_1.CONFIG.dependencies[name]), false));
    } else if (name !== 'core') {
      dependencies.push('core');
    }
    try {
      for (var dependencies_1 = __values(dependencies), dependencies_1_1 = dependencies_1.next(); !dependencies_1_1.done; dependencies_1_1 = dependencies_1.next()) {
        var dependent = dependencies_1_1.value;
        var extension = map.get(dependent) || new Package(dependent, noLoad);
        if (this.dependencies.indexOf(extension) < 0) {
          extension.addDependent(this, noLoad);
          this.dependencies.push(extension);
          if (!extension.isLoaded) {
            this.dependencyCount++;
            promises.push(extension.promise);
          }
        }
      }
    } catch (e_2_1) {
      e_2 = {
        error: e_2_1
      };
    } finally {
      try {
        if (dependencies_1_1 && !dependencies_1_1.done && (_a = dependencies_1.return)) _a.call(dependencies_1);
      } finally {
        if (e_2) throw e_2.error;
      }
    }
    return promises;
  };
  Package.prototype.makePromise = function (promises) {
    var _this = this;
    var promise = new Promise(function (resolve, reject) {
      _this.resolve = resolve;
      _this.reject = reject;
    });
    var config = loader_js_1.CONFIG[this.name] || {};
    if (config.ready) {
      promise = promise.then(function (_name) {
        return config.ready(_this.name);
      });
    }
    if (promises.length) {
      promises.push(promise);
      promise = Promise.all(promises).then(function (names) {
        return names.join(', ');
      });
    }
    if (config.failed) {
      promise.catch(function (message) {
        return config.failed(new PackageError(message, _this.name));
      });
    }
    return promise;
  };
  Package.prototype.load = function () {
    if (!this.isLoaded && !this.isLoading && !this.noLoad) {
      this.isLoading = true;
      var url = Package.resolvePath(this.name);
      if (loader_js_1.CONFIG.require) {
        this.loadCustom(url);
      } else {
        this.loadScript(url);
      }
    }
  };
  Package.prototype.loadCustom = function (url) {
    var _this = this;
    try {
      var result = loader_js_1.CONFIG.require(url);
      if (result instanceof Promise) {
        result.then(function () {
          return _this.checkLoad();
        }).catch(function (err) {
          return _this.failed('Can\'t load "' + url + '"\n' + err.message.trim());
        });
      } else {
        this.checkLoad();
      }
    } catch (err) {
      this.failed(err.message);
    }
  };
  Package.prototype.loadScript = function (url) {
    var _this = this;
    var script = document.createElement('script');
    script.src = url;
    script.charset = 'UTF-8';
    script.onload = function (_event) {
      return _this.checkLoad();
    };
    script.onerror = function (_event) {
      return _this.failed('Can\'t load "' + url + '"');
    };
    document.head.appendChild(script);
  };
  Package.prototype.loaded = function () {
    var e_3, _a, e_4, _b;
    this.isLoaded = true;
    this.isLoading = false;
    try {
      for (var _c = __values(this.dependents), _d = _c.next(); !_d.done; _d = _c.next()) {
        var dependent = _d.value;
        dependent.requirementSatisfied();
      }
    } catch (e_3_1) {
      e_3 = {
        error: e_3_1
      };
    } finally {
      try {
        if (_d && !_d.done && (_a = _c.return)) _a.call(_c);
      } finally {
        if (e_3) throw e_3.error;
      }
    }
    try {
      for (var _e = __values(this.provided), _f = _e.next(); !_f.done; _f = _e.next()) {
        var provided = _f.value;
        provided.loaded();
      }
    } catch (e_4_1) {
      e_4 = {
        error: e_4_1
      };
    } finally {
      try {
        if (_f && !_f.done && (_b = _e.return)) _b.call(_e);
      } finally {
        if (e_4) throw e_4.error;
      }
    }
    this.resolve(this.name);
  };
  Package.prototype.failed = function (message) {
    this.hasFailed = true;
    this.isLoading = false;
    this.reject(new PackageError(message, this.name));
  };
  Package.prototype.checkLoad = function () {
    var _this = this;
    var config = loader_js_1.CONFIG[this.name] || {};
    var checkReady = config.checkReady || function () {
      return Promise.resolve();
    };
    checkReady().then(function () {
      return _this.loaded();
    }).catch(function (message) {
      return _this.failed(message);
    });
  };
  Package.prototype.requirementSatisfied = function () {
    if (this.dependencyCount) {
      this.dependencyCount--;
      if (this.canLoad) {
        this.load();
      }
    }
  };
  Package.prototype.provides = function (names) {
    var e_5, _a;
    if (names === void 0) {
      names = [];
    }
    try {
      for (var names_1 = __values(names), names_1_1 = names_1.next(); !names_1_1.done; names_1_1 = names_1.next()) {
        var name_1 = names_1_1.value;
        var provided = Package.packages.get(name_1);
        if (!provided) {
          if (!loader_js_1.CONFIG.dependencies[name_1]) {
            loader_js_1.CONFIG.dependencies[name_1] = [];
          }
          loader_js_1.CONFIG.dependencies[name_1].push(name_1);
          provided = new Package(name_1, true);
          provided.isLoading = true;
        }
        this.provided.push(provided);
      }
    } catch (e_5_1) {
      e_5 = {
        error: e_5_1
      };
    } finally {
      try {
        if (names_1_1 && !names_1_1.done && (_a = names_1.return)) _a.call(names_1);
      } finally {
        if (e_5) throw e_5.error;
      }
    }
  };
  Package.prototype.addDependent = function (extension, noLoad) {
    this.dependents.push(extension);
    if (!noLoad) {
      this.checkNoLoad();
    }
  };
  Package.prototype.checkNoLoad = function () {
    var e_6, _a;
    if (this.noLoad) {
      this.noLoad = false;
      try {
        for (var _b = __values(this.dependencies), _c = _b.next(); !_c.done; _c = _b.next()) {
          var dependency = _c.value;
          dependency.checkNoLoad();
        }
      } catch (e_6_1) {
        e_6 = {
          error: e_6_1
        };
      } finally {
        try {
          if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
        } finally {
          if (e_6) throw e_6.error;
        }
      }
    }
  };
  Package.packages = new Map();
  return Package;
}();
exports.Package = Package;

/***/ },

/***/ 49199
(__unused_webpack_module, exports, __webpack_require__) {



var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MathJax = exports.combineWithMathJax = exports.combineDefaults = exports.combineConfig = exports.isObject = void 0;
var version_js_1 = __webpack_require__(5102);
function isObject(x) {
  return typeof x === 'object' && x !== null;
}
exports.isObject = isObject;
function combineConfig(dst, src) {
  var e_1, _a;
  try {
    for (var _b = __values(Object.keys(src)), _c = _b.next(); !_c.done; _c = _b.next()) {
      var id = _c.value;
      if (id === '__esModule') continue;
      if (isObject(dst[id]) && isObject(src[id]) && !(src[id] instanceof Promise)) {
        combineConfig(dst[id], src[id]);
      } else if (src[id] !== null && src[id] !== undefined) {
        dst[id] = src[id];
      }
    }
  } catch (e_1_1) {
    e_1 = {
      error: e_1_1
    };
  } finally {
    try {
      if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
    } finally {
      if (e_1) throw e_1.error;
    }
  }
  return dst;
}
exports.combineConfig = combineConfig;
function combineDefaults(dst, name, src) {
  var e_2, _a;
  if (!dst[name]) {
    dst[name] = {};
  }
  dst = dst[name];
  try {
    for (var _b = __values(Object.keys(src)), _c = _b.next(); !_c.done; _c = _b.next()) {
      var id = _c.value;
      if (isObject(dst[id]) && isObject(src[id])) {
        combineDefaults(dst, id, src[id]);
      } else if (dst[id] == null && src[id] != null) {
        dst[id] = src[id];
      }
    }
  } catch (e_2_1) {
    e_2 = {
      error: e_2_1
    };
  } finally {
    try {
      if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
    } finally {
      if (e_2) throw e_2.error;
    }
  }
  return dst;
}
exports.combineDefaults = combineDefaults;
function combineWithMathJax(config) {
  return combineConfig(exports.MathJax, config);
}
exports.combineWithMathJax = combineWithMathJax;
if (typeof __webpack_require__.g.MathJax === 'undefined') {
  __webpack_require__.g.MathJax = {};
}
if (!__webpack_require__.g.MathJax.version) {
  __webpack_require__.g.MathJax = {
    version: version_js_1.VERSION,
    _: {},
    config: __webpack_require__.g.MathJax
  };
}
exports.MathJax = __webpack_require__.g.MathJax;

/***/ },

/***/ 57895
(__unused_webpack_module, exports, __webpack_require__) {

var __webpack_dirname__ = "/";


var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var e_1, _a;
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.CONFIG = exports.MathJax = exports.Loader = exports.PathFilters = exports.PackageError = exports.Package = void 0;
var global_js_1 = __webpack_require__(49199);
var package_js_1 = __webpack_require__(33866);
var package_js_2 = __webpack_require__(33866);
Object.defineProperty(exports, "Package", ({
  enumerable: true,
  get: function () {
    return package_js_2.Package;
  }
}));
Object.defineProperty(exports, "PackageError", ({
  enumerable: true,
  get: function () {
    return package_js_2.PackageError;
  }
}));
var FunctionList_js_1 = __webpack_require__(58872);
exports.PathFilters = {
  source: function (data) {
    if (exports.CONFIG.source.hasOwnProperty(data.name)) {
      data.name = exports.CONFIG.source[data.name];
    }
    return true;
  },
  normalize: function (data) {
    var name = data.name;
    if (!name.match(/^(?:[a-z]+:\/)?\/|[a-z]:\\|\[/i)) {
      data.name = '[mathjax]/' + name.replace(/^\.\//, '');
    }
    if (data.addExtension && !name.match(/\.[^\/]+$/)) {
      data.name += '.js';
    }
    return true;
  },
  prefix: function (data) {
    var match;
    while (match = data.name.match(/^\[([^\]]*)\]/)) {
      if (!exports.CONFIG.paths.hasOwnProperty(match[1])) break;
      data.name = exports.CONFIG.paths[match[1]] + data.name.substr(match[0].length);
    }
    return true;
  }
};
var Loader;
(function (Loader) {
  var VERSION = global_js_1.MathJax.version;
  Loader.versions = new Map();
  function ready() {
    var e_2, _a;
    var names = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      names[_i] = arguments[_i];
    }
    if (names.length === 0) {
      names = Array.from(package_js_1.Package.packages.keys());
    }
    var promises = [];
    try {
      for (var names_1 = __values(names), names_1_1 = names_1.next(); !names_1_1.done; names_1_1 = names_1.next()) {
        var name_1 = names_1_1.value;
        var extension = package_js_1.Package.packages.get(name_1) || new package_js_1.Package(name_1, true);
        promises.push(extension.promise);
      }
    } catch (e_2_1) {
      e_2 = {
        error: e_2_1
      };
    } finally {
      try {
        if (names_1_1 && !names_1_1.done && (_a = names_1.return)) _a.call(names_1);
      } finally {
        if (e_2) throw e_2.error;
      }
    }
    return Promise.all(promises);
  }
  Loader.ready = ready;
  function load() {
    var e_3, _a;
    var names = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      names[_i] = arguments[_i];
    }
    if (names.length === 0) {
      return Promise.resolve();
    }
    var promises = [];
    var _loop_1 = function (name_2) {
      var extension = package_js_1.Package.packages.get(name_2);
      if (!extension) {
        extension = new package_js_1.Package(name_2);
        extension.provides(exports.CONFIG.provides[name_2]);
      }
      extension.checkNoLoad();
      promises.push(extension.promise.then(function () {
        if (!exports.CONFIG.versionWarnings) return;
        if (extension.isLoaded && !Loader.versions.has(package_js_1.Package.resolvePath(name_2))) {
          console.warn("No version information available for component ".concat(name_2));
        }
      }));
    };
    try {
      for (var names_2 = __values(names), names_2_1 = names_2.next(); !names_2_1.done; names_2_1 = names_2.next()) {
        var name_2 = names_2_1.value;
        _loop_1(name_2);
      }
    } catch (e_3_1) {
      e_3 = {
        error: e_3_1
      };
    } finally {
      try {
        if (names_2_1 && !names_2_1.done && (_a = names_2.return)) _a.call(names_2);
      } finally {
        if (e_3) throw e_3.error;
      }
    }
    package_js_1.Package.loadAll();
    return Promise.all(promises);
  }
  Loader.load = load;
  function preLoad() {
    var e_4, _a;
    var names = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      names[_i] = arguments[_i];
    }
    try {
      for (var names_3 = __values(names), names_3_1 = names_3.next(); !names_3_1.done; names_3_1 = names_3.next()) {
        var name_3 = names_3_1.value;
        var extension = package_js_1.Package.packages.get(name_3);
        if (!extension) {
          extension = new package_js_1.Package(name_3, true);
          extension.provides(exports.CONFIG.provides[name_3]);
        }
        extension.loaded();
      }
    } catch (e_4_1) {
      e_4 = {
        error: e_4_1
      };
    } finally {
      try {
        if (names_3_1 && !names_3_1.done && (_a = names_3.return)) _a.call(names_3);
      } finally {
        if (e_4) throw e_4.error;
      }
    }
  }
  Loader.preLoad = preLoad;
  function defaultReady() {
    if (typeof exports.MathJax.startup !== 'undefined') {
      exports.MathJax.config.startup.ready();
    }
  }
  Loader.defaultReady = defaultReady;
  function getRoot() {
    var root = __webpack_dirname__ + '/../../es5';
    if (typeof document !== 'undefined') {
      var script = document.currentScript || document.getElementById('MathJax-script');
      if (script) {
        root = script.src.replace(/\/[^\/]*$/, '');
      }
    }
    return root;
  }
  Loader.getRoot = getRoot;
  function checkVersion(name, version, _type) {
    Loader.versions.set(package_js_1.Package.resolvePath(name), VERSION);
    if (exports.CONFIG.versionWarnings && version !== VERSION) {
      console.warn("Component ".concat(name, " uses ").concat(version, " of MathJax; version in use is ").concat(VERSION));
      return true;
    }
    return false;
  }
  Loader.checkVersion = checkVersion;
  Loader.pathFilters = new FunctionList_js_1.FunctionList();
  Loader.pathFilters.add(exports.PathFilters.source, 0);
  Loader.pathFilters.add(exports.PathFilters.normalize, 10);
  Loader.pathFilters.add(exports.PathFilters.prefix, 20);
})(Loader = exports.Loader || (exports.Loader = {}));
exports.MathJax = global_js_1.MathJax;
if (typeof exports.MathJax.loader === 'undefined') {
  (0, global_js_1.combineDefaults)(exports.MathJax.config, 'loader', {
    paths: {
      mathjax: Loader.getRoot()
    },
    source: {},
    dependencies: {},
    provides: {},
    load: [],
    ready: Loader.defaultReady.bind(Loader),
    failed: function (error) {
      return console.log("MathJax(".concat(error.package || '?', "): ").concat(error.message));
    },
    require: null,
    pathFilters: [],
    versionWarnings: true
  });
  (0, global_js_1.combineWithMathJax)({
    loader: Loader
  });
  try {
    for (var _b = __values(exports.MathJax.config.loader.pathFilters), _c = _b.next(); !_c.done; _c = _b.next()) {
      var filter = _c.value;
      if (Array.isArray(filter)) {
        Loader.pathFilters.add(filter[0], filter[1]);
      } else {
        Loader.pathFilters.add(filter);
      }
    }
  } catch (e_1_1) {
    e_1 = {
      error: e_1_1
    };
  } finally {
    try {
      if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
    } finally {
      if (e_1) throw e_1.error;
    }
  }
}
exports.CONFIG = exports.MathJax.config.loader;

/***/ },

/***/ 96565
(__unused_webpack_module, exports, __webpack_require__) {



var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __spreadArray = this && this.__spreadArray || function (to, from, pack) {
  if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
    if (ar || !(i in from)) {
      if (!ar) ar = Array.prototype.slice.call(from, 0, i);
      ar[i] = from[i];
    }
  }
  return to.concat(ar || Array.prototype.slice.call(from));
};
var __importDefault = this && this.__importDefault || function (mod) {
  return mod && mod.__esModule ? mod : {
    "default": mod
  };
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.RequireConfiguration = exports.options = exports.RequireMethods = exports.RequireLoad = void 0;
var Configuration_js_1 = __webpack_require__(48322);
var SymbolMap_js_1 = __webpack_require__(73006);
var TexError_js_1 = __importDefault(__webpack_require__(87279));
var global_js_1 = __webpack_require__(49199);
var package_js_1 = __webpack_require__(33866);
var loader_js_1 = __webpack_require__(57895);
var mathjax_js_1 = __webpack_require__(83844);
var Options_js_1 = __webpack_require__(53588);
var MJCONFIG = global_js_1.MathJax.config;
function RegisterExtension(jax, name) {
  var _a;
  var require = jax.parseOptions.options.require;
  var required = jax.parseOptions.packageData.get('require').required;
  var extension = name.substr(require.prefix.length);
  if (required.indexOf(extension) < 0) {
    required.push(extension);
    RegisterDependencies(jax, loader_js_1.CONFIG.dependencies[name]);
    var handler = Configuration_js_1.ConfigurationHandler.get(extension);
    if (handler) {
      var options_1 = MJCONFIG[name] || {};
      if (handler.options && Object.keys(handler.options).length === 1 && handler.options[extension]) {
        options_1 = (_a = {}, _a[extension] = options_1, _a);
      }
      jax.configuration.add(extension, jax, options_1);
      var configured = jax.parseOptions.packageData.get('require').configured;
      if (handler.preprocessors.length && !configured.has(extension)) {
        configured.set(extension, true);
        mathjax_js_1.mathjax.retryAfter(Promise.resolve());
      }
    }
  }
}
function RegisterDependencies(jax, names) {
  var e_1, _a;
  if (names === void 0) {
    names = [];
  }
  var prefix = jax.parseOptions.options.require.prefix;
  try {
    for (var names_1 = __values(names), names_1_1 = names_1.next(); !names_1_1.done; names_1_1 = names_1.next()) {
      var name_1 = names_1_1.value;
      if (name_1.substr(0, prefix.length) === prefix) {
        RegisterExtension(jax, name_1);
      }
    }
  } catch (e_1_1) {
    e_1 = {
      error: e_1_1
    };
  } finally {
    try {
      if (names_1_1 && !names_1_1.done && (_a = names_1.return)) _a.call(names_1);
    } finally {
      if (e_1) throw e_1.error;
    }
  }
}
function RequireLoad(parser, name) {
  var options = parser.options.require;
  var allow = options.allow;
  var extension = (name.substr(0, 1) === '[' ? '' : options.prefix) + name;
  var allowed = allow.hasOwnProperty(extension) ? allow[extension] : allow.hasOwnProperty(name) ? allow[name] : options.defaultAllow;
  if (!allowed) {
    throw new TexError_js_1.default('BadRequire', 'Extension "%1" is not allowed to be loaded', extension);
  }
  if (package_js_1.Package.packages.has(extension)) {
    RegisterExtension(parser.configuration.packageData.get('require').jax, extension);
  } else {
    mathjax_js_1.mathjax.retryAfter(loader_js_1.Loader.load(extension));
  }
}
exports.RequireLoad = RequireLoad;
function config(_config, jax) {
  jax.parseOptions.packageData.set('require', {
    jax: jax,
    required: __spreadArray([], __read(jax.options.packages), false),
    configured: new Map()
  });
  var options = jax.parseOptions.options.require;
  var prefix = options.prefix;
  if (prefix.match(/[^_a-zA-Z0-9]/)) {
    throw Error('Illegal characters used in \\require prefix');
  }
  if (!loader_js_1.CONFIG.paths[prefix]) {
    loader_js_1.CONFIG.paths[prefix] = '[mathjax]/input/tex/extensions';
  }
  options.prefix = '[' + prefix + ']/';
}
exports.RequireMethods = {
  Require: function (parser, name) {
    var required = parser.GetArgument(name);
    if (required.match(/[^_a-zA-Z0-9]/) || required === '') {
      throw new TexError_js_1.default('BadPackageName', 'Argument for %1 is not a valid package name', name);
    }
    RequireLoad(parser, required);
  }
};
exports.options = {
  require: {
    allow: (0, Options_js_1.expandable)({
      base: false,
      'all-packages': false,
      autoload: false,
      configmacros: false,
      tagformat: false,
      setoptions: false
    }),
    defaultAllow: true,
    prefix: 'tex'
  }
};
new SymbolMap_js_1.CommandMap('require', {
  require: 'Require'
}, exports.RequireMethods);
exports.RequireConfiguration = Configuration_js_1.Configuration.create('require', {
  handler: {
    macro: ['require']
  },
  config: config,
  options: exports.options
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjU2NS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDbFhBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7OztBQ2hHQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUNyUEE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvbWF0aGpheC1mdWxsL2pzL2NvbXBvbmVudHMvcGFja2FnZS5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb21wb25lbnRzL2dsb2JhbC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb21wb25lbnRzL2xvYWRlci5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9pbnB1dC90ZXgvcmVxdWlyZS9SZXF1aXJlQ29uZmlndXJhdGlvbi5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xudmFyIF9fc3ByZWFkQXJyYXkgPSB0aGlzICYmIHRoaXMuX19zcHJlYWRBcnJheSB8fCBmdW5jdGlvbiAodG8sIGZyb20sIHBhY2spIHtcbiAgaWYgKHBhY2sgfHwgYXJndW1lbnRzLmxlbmd0aCA9PT0gMikgZm9yICh2YXIgaSA9IDAsIGwgPSBmcm9tLmxlbmd0aCwgYXI7IGkgPCBsOyBpKyspIHtcbiAgICBpZiAoYXIgfHwgIShpIGluIGZyb20pKSB7XG4gICAgICBpZiAoIWFyKSBhciA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20sIDAsIGkpO1xuICAgICAgYXJbaV0gPSBmcm9tW2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdG8uY29uY2F0KGFyIHx8IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20pKTtcbn07XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5QYWNrYWdlID0gZXhwb3J0cy5QYWNrYWdlRXJyb3IgPSB2b2lkIDA7XG52YXIgbG9hZGVyX2pzXzEgPSByZXF1aXJlKFwiLi9sb2FkZXIuanNcIik7XG52YXIgUGFja2FnZUVycm9yID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoUGFja2FnZUVycm9yLCBfc3VwZXIpO1xuICBmdW5jdGlvbiBQYWNrYWdlRXJyb3IobWVzc2FnZSwgbmFtZSkge1xuICAgIHZhciBfdGhpcyA9IF9zdXBlci5jYWxsKHRoaXMsIG1lc3NhZ2UpIHx8IHRoaXM7XG4gICAgX3RoaXMucGFja2FnZSA9IG5hbWU7XG4gICAgcmV0dXJuIF90aGlzO1xuICB9XG4gIHJldHVybiBQYWNrYWdlRXJyb3I7XG59KEVycm9yKTtcbmV4cG9ydHMuUGFja2FnZUVycm9yID0gUGFja2FnZUVycm9yO1xudmFyIFBhY2thZ2UgPSBmdW5jdGlvbiAoKSB7XG4gIGZ1bmN0aW9uIFBhY2thZ2UobmFtZSwgbm9Mb2FkKSB7XG4gICAgaWYgKG5vTG9hZCA9PT0gdm9pZCAwKSB7XG4gICAgICBub0xvYWQgPSBmYWxzZTtcbiAgICB9XG4gICAgdGhpcy5pc0xvYWRlZCA9IGZhbHNlO1xuICAgIHRoaXMuaXNMb2FkaW5nID0gZmFsc2U7XG4gICAgdGhpcy5oYXNGYWlsZWQgPSBmYWxzZTtcbiAgICB0aGlzLmRlcGVuZGVudHMgPSBbXTtcbiAgICB0aGlzLmRlcGVuZGVuY2llcyA9IFtdO1xuICAgIHRoaXMuZGVwZW5kZW5jeUNvdW50ID0gMDtcbiAgICB0aGlzLnByb3ZpZGVkID0gW107XG4gICAgdGhpcy5uYW1lID0gbmFtZTtcbiAgICB0aGlzLm5vTG9hZCA9IG5vTG9hZDtcbiAgICBQYWNrYWdlLnBhY2thZ2VzLnNldChuYW1lLCB0aGlzKTtcbiAgICB0aGlzLnByb21pc2UgPSB0aGlzLm1ha2VQcm9taXNlKHRoaXMubWFrZURlcGVuZGVuY2llcygpKTtcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoUGFja2FnZS5wcm90b3R5cGUsIFwiY2FuTG9hZFwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gdGhpcy5kZXBlbmRlbmN5Q291bnQgPT09IDAgJiYgIXRoaXMubm9Mb2FkICYmICF0aGlzLmlzTG9hZGluZyAmJiAhdGhpcy5oYXNGYWlsZWQ7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIFBhY2thZ2UucmVzb2x2ZVBhdGggPSBmdW5jdGlvbiAobmFtZSwgYWRkRXh0ZW5zaW9uKSB7XG4gICAgaWYgKGFkZEV4dGVuc2lvbiA9PT0gdm9pZCAwKSB7XG4gICAgICBhZGRFeHRlbnNpb24gPSB0cnVlO1xuICAgIH1cbiAgICB2YXIgZGF0YSA9IHtcbiAgICAgIG5hbWU6IG5hbWUsXG4gICAgICBvcmlnaW5hbDogbmFtZSxcbiAgICAgIGFkZEV4dGVuc2lvbjogYWRkRXh0ZW5zaW9uXG4gICAgfTtcbiAgICBsb2FkZXJfanNfMS5Mb2FkZXIucGF0aEZpbHRlcnMuZXhlY3V0ZShkYXRhKTtcbiAgICByZXR1cm4gZGF0YS5uYW1lO1xuICB9O1xuICBQYWNrYWdlLmxvYWRBbGwgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGVfMSwgX2E7XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXModGhpcy5wYWNrYWdlcy52YWx1ZXMoKSksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGV4dGVuc2lvbiA9IF9jLnZhbHVlO1xuICAgICAgICBpZiAoZXh0ZW5zaW9uLmNhbkxvYWQpIHtcbiAgICAgICAgICBleHRlbnNpb24ubG9hZCgpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8xXzEpIHtcbiAgICAgIGVfMSA9IHtcbiAgICAgICAgZXJyb3I6IGVfMV8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICB9O1xuICBQYWNrYWdlLnByb3RvdHlwZS5tYWtlRGVwZW5kZW5jaWVzID0gZnVuY3Rpb24gKCkge1xuICAgIHZhciBlXzIsIF9hO1xuICAgIHZhciBwcm9taXNlcyA9IFtdO1xuICAgIHZhciBtYXAgPSBQYWNrYWdlLnBhY2thZ2VzO1xuICAgIHZhciBub0xvYWQgPSB0aGlzLm5vTG9hZDtcbiAgICB2YXIgbmFtZSA9IHRoaXMubmFtZTtcbiAgICB2YXIgZGVwZW5kZW5jaWVzID0gW107XG4gICAgaWYgKGxvYWRlcl9qc18xLkNPTkZJRy5kZXBlbmRlbmNpZXMuaGFzT3duUHJvcGVydHkobmFtZSkpIHtcbiAgICAgIGRlcGVuZGVuY2llcy5wdXNoLmFwcGx5KGRlcGVuZGVuY2llcywgX19zcHJlYWRBcnJheShbXSwgX19yZWFkKGxvYWRlcl9qc18xLkNPTkZJRy5kZXBlbmRlbmNpZXNbbmFtZV0pLCBmYWxzZSkpO1xuICAgIH0gZWxzZSBpZiAobmFtZSAhPT0gJ2NvcmUnKSB7XG4gICAgICBkZXBlbmRlbmNpZXMucHVzaCgnY29yZScpO1xuICAgIH1cbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgZGVwZW5kZW5jaWVzXzEgPSBfX3ZhbHVlcyhkZXBlbmRlbmNpZXMpLCBkZXBlbmRlbmNpZXNfMV8xID0gZGVwZW5kZW5jaWVzXzEubmV4dCgpOyAhZGVwZW5kZW5jaWVzXzFfMS5kb25lOyBkZXBlbmRlbmNpZXNfMV8xID0gZGVwZW5kZW5jaWVzXzEubmV4dCgpKSB7XG4gICAgICAgIHZhciBkZXBlbmRlbnQgPSBkZXBlbmRlbmNpZXNfMV8xLnZhbHVlO1xuICAgICAgICB2YXIgZXh0ZW5zaW9uID0gbWFwLmdldChkZXBlbmRlbnQpIHx8IG5ldyBQYWNrYWdlKGRlcGVuZGVudCwgbm9Mb2FkKTtcbiAgICAgICAgaWYgKHRoaXMuZGVwZW5kZW5jaWVzLmluZGV4T2YoZXh0ZW5zaW9uKSA8IDApIHtcbiAgICAgICAgICBleHRlbnNpb24uYWRkRGVwZW5kZW50KHRoaXMsIG5vTG9hZCk7XG4gICAgICAgICAgdGhpcy5kZXBlbmRlbmNpZXMucHVzaChleHRlbnNpb24pO1xuICAgICAgICAgIGlmICghZXh0ZW5zaW9uLmlzTG9hZGVkKSB7XG4gICAgICAgICAgICB0aGlzLmRlcGVuZGVuY3lDb3VudCsrO1xuICAgICAgICAgICAgcHJvbWlzZXMucHVzaChleHRlbnNpb24ucHJvbWlzZSk7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8yXzEpIHtcbiAgICAgIGVfMiA9IHtcbiAgICAgICAgZXJyb3I6IGVfMl8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoZGVwZW5kZW5jaWVzXzFfMSAmJiAhZGVwZW5kZW5jaWVzXzFfMS5kb25lICYmIChfYSA9IGRlcGVuZGVuY2llc18xLnJldHVybikpIF9hLmNhbGwoZGVwZW5kZW5jaWVzXzEpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfMikgdGhyb3cgZV8yLmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gcHJvbWlzZXM7XG4gIH07XG4gIFBhY2thZ2UucHJvdG90eXBlLm1ha2VQcm9taXNlID0gZnVuY3Rpb24gKHByb21pc2VzKSB7XG4gICAgdmFyIF90aGlzID0gdGhpcztcbiAgICB2YXIgcHJvbWlzZSA9IG5ldyBQcm9taXNlKGZ1bmN0aW9uIChyZXNvbHZlLCByZWplY3QpIHtcbiAgICAgIF90aGlzLnJlc29sdmUgPSByZXNvbHZlO1xuICAgICAgX3RoaXMucmVqZWN0ID0gcmVqZWN0O1xuICAgIH0pO1xuICAgIHZhciBjb25maWcgPSBsb2FkZXJfanNfMS5DT05GSUdbdGhpcy5uYW1lXSB8fCB7fTtcbiAgICBpZiAoY29uZmlnLnJlYWR5KSB7XG4gICAgICBwcm9taXNlID0gcHJvbWlzZS50aGVuKGZ1bmN0aW9uIChfbmFtZSkge1xuICAgICAgICByZXR1cm4gY29uZmlnLnJlYWR5KF90aGlzLm5hbWUpO1xuICAgICAgfSk7XG4gICAgfVxuICAgIGlmIChwcm9taXNlcy5sZW5ndGgpIHtcbiAgICAgIHByb21pc2VzLnB1c2gocHJvbWlzZSk7XG4gICAgICBwcm9taXNlID0gUHJvbWlzZS5hbGwocHJvbWlzZXMpLnRoZW4oZnVuY3Rpb24gKG5hbWVzKSB7XG4gICAgICAgIHJldHVybiBuYW1lcy5qb2luKCcsICcpO1xuICAgICAgfSk7XG4gICAgfVxuICAgIGlmIChjb25maWcuZmFpbGVkKSB7XG4gICAgICBwcm9taXNlLmNhdGNoKGZ1bmN0aW9uIChtZXNzYWdlKSB7XG4gICAgICAgIHJldHVybiBjb25maWcuZmFpbGVkKG5ldyBQYWNrYWdlRXJyb3IobWVzc2FnZSwgX3RoaXMubmFtZSkpO1xuICAgICAgfSk7XG4gICAgfVxuICAgIHJldHVybiBwcm9taXNlO1xuICB9O1xuICBQYWNrYWdlLnByb3RvdHlwZS5sb2FkID0gZnVuY3Rpb24gKCkge1xuICAgIGlmICghdGhpcy5pc0xvYWRlZCAmJiAhdGhpcy5pc0xvYWRpbmcgJiYgIXRoaXMubm9Mb2FkKSB7XG4gICAgICB0aGlzLmlzTG9hZGluZyA9IHRydWU7XG4gICAgICB2YXIgdXJsID0gUGFja2FnZS5yZXNvbHZlUGF0aCh0aGlzLm5hbWUpO1xuICAgICAgaWYgKGxvYWRlcl9qc18xLkNPTkZJRy5yZXF1aXJlKSB7XG4gICAgICAgIHRoaXMubG9hZEN1c3RvbSh1cmwpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdGhpcy5sb2FkU2NyaXB0KHVybCk7XG4gICAgICB9XG4gICAgfVxuICB9O1xuICBQYWNrYWdlLnByb3RvdHlwZS5sb2FkQ3VzdG9tID0gZnVuY3Rpb24gKHVybCkge1xuICAgIHZhciBfdGhpcyA9IHRoaXM7XG4gICAgdHJ5IHtcbiAgICAgIHZhciByZXN1bHQgPSBsb2FkZXJfanNfMS5DT05GSUcucmVxdWlyZSh1cmwpO1xuICAgICAgaWYgKHJlc3VsdCBpbnN0YW5jZW9mIFByb21pc2UpIHtcbiAgICAgICAgcmVzdWx0LnRoZW4oZnVuY3Rpb24gKCkge1xuICAgICAgICAgIHJldHVybiBfdGhpcy5jaGVja0xvYWQoKTtcbiAgICAgICAgfSkuY2F0Y2goZnVuY3Rpb24gKGVycikge1xuICAgICAgICAgIHJldHVybiBfdGhpcy5mYWlsZWQoJ0NhblxcJ3QgbG9hZCBcIicgKyB1cmwgKyAnXCJcXG4nICsgZXJyLm1lc3NhZ2UudHJpbSgpKTtcbiAgICAgICAgfSk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICB0aGlzLmNoZWNrTG9hZCgpO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVycikge1xuICAgICAgdGhpcy5mYWlsZWQoZXJyLm1lc3NhZ2UpO1xuICAgIH1cbiAgfTtcbiAgUGFja2FnZS5wcm90b3R5cGUubG9hZFNjcmlwdCA9IGZ1bmN0aW9uICh1cmwpIHtcbiAgICB2YXIgX3RoaXMgPSB0aGlzO1xuICAgIHZhciBzY3JpcHQgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdzY3JpcHQnKTtcbiAgICBzY3JpcHQuc3JjID0gdXJsO1xuICAgIHNjcmlwdC5jaGFyc2V0ID0gJ1VURi04JztcbiAgICBzY3JpcHQub25sb2FkID0gZnVuY3Rpb24gKF9ldmVudCkge1xuICAgICAgcmV0dXJuIF90aGlzLmNoZWNrTG9hZCgpO1xuICAgIH07XG4gICAgc2NyaXB0Lm9uZXJyb3IgPSBmdW5jdGlvbiAoX2V2ZW50KSB7XG4gICAgICByZXR1cm4gX3RoaXMuZmFpbGVkKCdDYW5cXCd0IGxvYWQgXCInICsgdXJsICsgJ1wiJyk7XG4gICAgfTtcbiAgICBkb2N1bWVudC5oZWFkLmFwcGVuZENoaWxkKHNjcmlwdCk7XG4gIH07XG4gIFBhY2thZ2UucHJvdG90eXBlLmxvYWRlZCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgZV8zLCBfYSwgZV80LCBfYjtcbiAgICB0aGlzLmlzTG9hZGVkID0gdHJ1ZTtcbiAgICB0aGlzLmlzTG9hZGluZyA9IGZhbHNlO1xuICAgIHRyeSB7XG4gICAgICBmb3IgKHZhciBfYyA9IF9fdmFsdWVzKHRoaXMuZGVwZW5kZW50cyksIF9kID0gX2MubmV4dCgpOyAhX2QuZG9uZTsgX2QgPSBfYy5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGRlcGVuZGVudCA9IF9kLnZhbHVlO1xuICAgICAgICBkZXBlbmRlbnQucmVxdWlyZW1lbnRTYXRpc2ZpZWQoKTtcbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzNfMSkge1xuICAgICAgZV8zID0ge1xuICAgICAgICBlcnJvcjogZV8zXzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfZCAmJiAhX2QuZG9uZSAmJiAoX2EgPSBfYy5yZXR1cm4pKSBfYS5jYWxsKF9jKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzMpIHRocm93IGVfMy5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9lID0gX192YWx1ZXModGhpcy5wcm92aWRlZCksIF9mID0gX2UubmV4dCgpOyAhX2YuZG9uZTsgX2YgPSBfZS5uZXh0KCkpIHtcbiAgICAgICAgdmFyIHByb3ZpZGVkID0gX2YudmFsdWU7XG4gICAgICAgIHByb3ZpZGVkLmxvYWRlZCgpO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfNF8xKSB7XG4gICAgICBlXzQgPSB7XG4gICAgICAgIGVycm9yOiBlXzRfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKF9mICYmICFfZi5kb25lICYmIChfYiA9IF9lLnJldHVybikpIF9iLmNhbGwoX2UpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfNCkgdGhyb3cgZV80LmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgICB0aGlzLnJlc29sdmUodGhpcy5uYW1lKTtcbiAgfTtcbiAgUGFja2FnZS5wcm90b3R5cGUuZmFpbGVkID0gZnVuY3Rpb24gKG1lc3NhZ2UpIHtcbiAgICB0aGlzLmhhc0ZhaWxlZCA9IHRydWU7XG4gICAgdGhpcy5pc0xvYWRpbmcgPSBmYWxzZTtcbiAgICB0aGlzLnJlamVjdChuZXcgUGFja2FnZUVycm9yKG1lc3NhZ2UsIHRoaXMubmFtZSkpO1xuICB9O1xuICBQYWNrYWdlLnByb3RvdHlwZS5jaGVja0xvYWQgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIF90aGlzID0gdGhpcztcbiAgICB2YXIgY29uZmlnID0gbG9hZGVyX2pzXzEuQ09ORklHW3RoaXMubmFtZV0gfHwge307XG4gICAgdmFyIGNoZWNrUmVhZHkgPSBjb25maWcuY2hlY2tSZWFkeSB8fCBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gUHJvbWlzZS5yZXNvbHZlKCk7XG4gICAgfTtcbiAgICBjaGVja1JlYWR5KCkudGhlbihmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gX3RoaXMubG9hZGVkKCk7XG4gICAgfSkuY2F0Y2goZnVuY3Rpb24gKG1lc3NhZ2UpIHtcbiAgICAgIHJldHVybiBfdGhpcy5mYWlsZWQobWVzc2FnZSk7XG4gICAgfSk7XG4gIH07XG4gIFBhY2thZ2UucHJvdG90eXBlLnJlcXVpcmVtZW50U2F0aXNmaWVkID0gZnVuY3Rpb24gKCkge1xuICAgIGlmICh0aGlzLmRlcGVuZGVuY3lDb3VudCkge1xuICAgICAgdGhpcy5kZXBlbmRlbmN5Q291bnQtLTtcbiAgICAgIGlmICh0aGlzLmNhbkxvYWQpIHtcbiAgICAgICAgdGhpcy5sb2FkKCk7XG4gICAgICB9XG4gICAgfVxuICB9O1xuICBQYWNrYWdlLnByb3RvdHlwZS5wcm92aWRlcyA9IGZ1bmN0aW9uIChuYW1lcykge1xuICAgIHZhciBlXzUsIF9hO1xuICAgIGlmIChuYW1lcyA9PT0gdm9pZCAwKSB7XG4gICAgICBuYW1lcyA9IFtdO1xuICAgIH1cbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgbmFtZXNfMSA9IF9fdmFsdWVzKG5hbWVzKSwgbmFtZXNfMV8xID0gbmFtZXNfMS5uZXh0KCk7ICFuYW1lc18xXzEuZG9uZTsgbmFtZXNfMV8xID0gbmFtZXNfMS5uZXh0KCkpIHtcbiAgICAgICAgdmFyIG5hbWVfMSA9IG5hbWVzXzFfMS52YWx1ZTtcbiAgICAgICAgdmFyIHByb3ZpZGVkID0gUGFja2FnZS5wYWNrYWdlcy5nZXQobmFtZV8xKTtcbiAgICAgICAgaWYgKCFwcm92aWRlZCkge1xuICAgICAgICAgIGlmICghbG9hZGVyX2pzXzEuQ09ORklHLmRlcGVuZGVuY2llc1tuYW1lXzFdKSB7XG4gICAgICAgICAgICBsb2FkZXJfanNfMS5DT05GSUcuZGVwZW5kZW5jaWVzW25hbWVfMV0gPSBbXTtcbiAgICAgICAgICB9XG4gICAgICAgICAgbG9hZGVyX2pzXzEuQ09ORklHLmRlcGVuZGVuY2llc1tuYW1lXzFdLnB1c2gobmFtZV8xKTtcbiAgICAgICAgICBwcm92aWRlZCA9IG5ldyBQYWNrYWdlKG5hbWVfMSwgdHJ1ZSk7XG4gICAgICAgICAgcHJvdmlkZWQuaXNMb2FkaW5nID0gdHJ1ZTtcbiAgICAgICAgfVxuICAgICAgICB0aGlzLnByb3ZpZGVkLnB1c2gocHJvdmlkZWQpO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfNV8xKSB7XG4gICAgICBlXzUgPSB7XG4gICAgICAgIGVycm9yOiBlXzVfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKG5hbWVzXzFfMSAmJiAhbmFtZXNfMV8xLmRvbmUgJiYgKF9hID0gbmFtZXNfMS5yZXR1cm4pKSBfYS5jYWxsKG5hbWVzXzEpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfNSkgdGhyb3cgZV81LmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgfTtcbiAgUGFja2FnZS5wcm90b3R5cGUuYWRkRGVwZW5kZW50ID0gZnVuY3Rpb24gKGV4dGVuc2lvbiwgbm9Mb2FkKSB7XG4gICAgdGhpcy5kZXBlbmRlbnRzLnB1c2goZXh0ZW5zaW9uKTtcbiAgICBpZiAoIW5vTG9hZCkge1xuICAgICAgdGhpcy5jaGVja05vTG9hZCgpO1xuICAgIH1cbiAgfTtcbiAgUGFja2FnZS5wcm90b3R5cGUuY2hlY2tOb0xvYWQgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGVfNiwgX2E7XG4gICAgaWYgKHRoaXMubm9Mb2FkKSB7XG4gICAgICB0aGlzLm5vTG9hZCA9IGZhbHNlO1xuICAgICAgdHJ5IHtcbiAgICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyh0aGlzLmRlcGVuZGVuY2llcyksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgICB2YXIgZGVwZW5kZW5jeSA9IF9jLnZhbHVlO1xuICAgICAgICAgIGRlcGVuZGVuY3kuY2hlY2tOb0xvYWQoKTtcbiAgICAgICAgfVxuICAgICAgfSBjYXRjaCAoZV82XzEpIHtcbiAgICAgICAgZV82ID0ge1xuICAgICAgICAgIGVycm9yOiBlXzZfMVxuICAgICAgICB9O1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgaWYgKGVfNikgdGhyb3cgZV82LmVycm9yO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICB9O1xuICBQYWNrYWdlLnBhY2thZ2VzID0gbmV3IE1hcCgpO1xuICByZXR1cm4gUGFja2FnZTtcbn0oKTtcbmV4cG9ydHMuUGFja2FnZSA9IFBhY2thZ2U7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX3ZhbHVlcyA9IHRoaXMgJiYgdGhpcy5fX3ZhbHVlcyB8fCBmdW5jdGlvbiAobykge1xuICB2YXIgcyA9IHR5cGVvZiBTeW1ib2wgPT09IFwiZnVuY3Rpb25cIiAmJiBTeW1ib2wuaXRlcmF0b3IsXG4gICAgbSA9IHMgJiYgb1tzXSxcbiAgICBpID0gMDtcbiAgaWYgKG0pIHJldHVybiBtLmNhbGwobyk7XG4gIGlmIChvICYmIHR5cGVvZiBvLmxlbmd0aCA9PT0gXCJudW1iZXJcIikgcmV0dXJuIHtcbiAgICBuZXh0OiBmdW5jdGlvbiAoKSB7XG4gICAgICBpZiAobyAmJiBpID49IG8ubGVuZ3RoKSBvID0gdm9pZCAwO1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdmFsdWU6IG8gJiYgb1tpKytdLFxuICAgICAgICBkb25lOiAhb1xuICAgICAgfTtcbiAgICB9XG4gIH07XG4gIHRocm93IG5ldyBUeXBlRXJyb3IocyA/IFwiT2JqZWN0IGlzIG5vdCBpdGVyYWJsZS5cIiA6IFwiU3ltYm9sLml0ZXJhdG9yIGlzIG5vdCBkZWZpbmVkLlwiKTtcbn07XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5NYXRoSmF4ID0gZXhwb3J0cy5jb21iaW5lV2l0aE1hdGhKYXggPSBleHBvcnRzLmNvbWJpbmVEZWZhdWx0cyA9IGV4cG9ydHMuY29tYmluZUNvbmZpZyA9IGV4cG9ydHMuaXNPYmplY3QgPSB2b2lkIDA7XG52YXIgdmVyc2lvbl9qc18xID0gcmVxdWlyZShcIi4vdmVyc2lvbi5qc1wiKTtcbmZ1bmN0aW9uIGlzT2JqZWN0KHgpIHtcbiAgcmV0dXJuIHR5cGVvZiB4ID09PSAnb2JqZWN0JyAmJiB4ICE9PSBudWxsO1xufVxuZXhwb3J0cy5pc09iamVjdCA9IGlzT2JqZWN0O1xuZnVuY3Rpb24gY29tYmluZUNvbmZpZyhkc3QsIHNyYykge1xuICB2YXIgZV8xLCBfYTtcbiAgdHJ5IHtcbiAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKE9iamVjdC5rZXlzKHNyYykpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICB2YXIgaWQgPSBfYy52YWx1ZTtcbiAgICAgIGlmIChpZCA9PT0gJ19fZXNNb2R1bGUnKSBjb250aW51ZTtcbiAgICAgIGlmIChpc09iamVjdChkc3RbaWRdKSAmJiBpc09iamVjdChzcmNbaWRdKSAmJiAhKHNyY1tpZF0gaW5zdGFuY2VvZiBQcm9taXNlKSkge1xuICAgICAgICBjb21iaW5lQ29uZmlnKGRzdFtpZF0sIHNyY1tpZF0pO1xuICAgICAgfSBlbHNlIGlmIChzcmNbaWRdICE9PSBudWxsICYmIHNyY1tpZF0gIT09IHVuZGVmaW5lZCkge1xuICAgICAgICBkc3RbaWRdID0gc3JjW2lkXTtcbiAgICAgIH1cbiAgICB9XG4gIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgZV8xID0ge1xuICAgICAgZXJyb3I6IGVfMV8xXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgfVxuICB9XG4gIHJldHVybiBkc3Q7XG59XG5leHBvcnRzLmNvbWJpbmVDb25maWcgPSBjb21iaW5lQ29uZmlnO1xuZnVuY3Rpb24gY29tYmluZURlZmF1bHRzKGRzdCwgbmFtZSwgc3JjKSB7XG4gIHZhciBlXzIsIF9hO1xuICBpZiAoIWRzdFtuYW1lXSkge1xuICAgIGRzdFtuYW1lXSA9IHt9O1xuICB9XG4gIGRzdCA9IGRzdFtuYW1lXTtcbiAgdHJ5IHtcbiAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKE9iamVjdC5rZXlzKHNyYykpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICB2YXIgaWQgPSBfYy52YWx1ZTtcbiAgICAgIGlmIChpc09iamVjdChkc3RbaWRdKSAmJiBpc09iamVjdChzcmNbaWRdKSkge1xuICAgICAgICBjb21iaW5lRGVmYXVsdHMoZHN0LCBpZCwgc3JjW2lkXSk7XG4gICAgICB9IGVsc2UgaWYgKGRzdFtpZF0gPT0gbnVsbCAmJiBzcmNbaWRdICE9IG51bGwpIHtcbiAgICAgICAgZHN0W2lkXSA9IHNyY1tpZF07XG4gICAgICB9XG4gICAgfVxuICB9IGNhdGNoIChlXzJfMSkge1xuICAgIGVfMiA9IHtcbiAgICAgIGVycm9yOiBlXzJfMVxuICAgIH07XG4gIH0gZmluYWxseSB7XG4gICAgdHJ5IHtcbiAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgaWYgKGVfMikgdGhyb3cgZV8yLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gZHN0O1xufVxuZXhwb3J0cy5jb21iaW5lRGVmYXVsdHMgPSBjb21iaW5lRGVmYXVsdHM7XG5mdW5jdGlvbiBjb21iaW5lV2l0aE1hdGhKYXgoY29uZmlnKSB7XG4gIHJldHVybiBjb21iaW5lQ29uZmlnKGV4cG9ydHMuTWF0aEpheCwgY29uZmlnKTtcbn1cbmV4cG9ydHMuY29tYmluZVdpdGhNYXRoSmF4ID0gY29tYmluZVdpdGhNYXRoSmF4O1xuaWYgKHR5cGVvZiBnbG9iYWwuTWF0aEpheCA9PT0gJ3VuZGVmaW5lZCcpIHtcbiAgZ2xvYmFsLk1hdGhKYXggPSB7fTtcbn1cbmlmICghZ2xvYmFsLk1hdGhKYXgudmVyc2lvbikge1xuICBnbG9iYWwuTWF0aEpheCA9IHtcbiAgICB2ZXJzaW9uOiB2ZXJzaW9uX2pzXzEuVkVSU0lPTixcbiAgICBfOiB7fSxcbiAgICBjb25maWc6IGdsb2JhbC5NYXRoSmF4XG4gIH07XG59XG5leHBvcnRzLk1hdGhKYXggPSBnbG9iYWwuTWF0aEpheDsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fdmFsdWVzID0gdGhpcyAmJiB0aGlzLl9fdmFsdWVzIHx8IGZ1bmN0aW9uIChvKSB7XG4gIHZhciBzID0gdHlwZW9mIFN5bWJvbCA9PT0gXCJmdW5jdGlvblwiICYmIFN5bWJvbC5pdGVyYXRvcixcbiAgICBtID0gcyAmJiBvW3NdLFxuICAgIGkgPSAwO1xuICBpZiAobSkgcmV0dXJuIG0uY2FsbChvKTtcbiAgaWYgKG8gJiYgdHlwZW9mIG8ubGVuZ3RoID09PSBcIm51bWJlclwiKSByZXR1cm4ge1xuICAgIG5leHQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIGlmIChvICYmIGkgPj0gby5sZW5ndGgpIG8gPSB2b2lkIDA7XG4gICAgICByZXR1cm4ge1xuICAgICAgICB2YWx1ZTogbyAmJiBvW2krK10sXG4gICAgICAgIGRvbmU6ICFvXG4gICAgICB9O1xuICAgIH1cbiAgfTtcbiAgdGhyb3cgbmV3IFR5cGVFcnJvcihzID8gXCJPYmplY3QgaXMgbm90IGl0ZXJhYmxlLlwiIDogXCJTeW1ib2wuaXRlcmF0b3IgaXMgbm90IGRlZmluZWQuXCIpO1xufTtcbnZhciBlXzEsIF9hO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuQ09ORklHID0gZXhwb3J0cy5NYXRoSmF4ID0gZXhwb3J0cy5Mb2FkZXIgPSBleHBvcnRzLlBhdGhGaWx0ZXJzID0gZXhwb3J0cy5QYWNrYWdlRXJyb3IgPSBleHBvcnRzLlBhY2thZ2UgPSB2b2lkIDA7XG52YXIgZ2xvYmFsX2pzXzEgPSByZXF1aXJlKFwiLi9nbG9iYWwuanNcIik7XG52YXIgcGFja2FnZV9qc18xID0gcmVxdWlyZShcIi4vcGFja2FnZS5qc1wiKTtcbnZhciBwYWNrYWdlX2pzXzIgPSByZXF1aXJlKFwiLi9wYWNrYWdlLmpzXCIpO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiUGFja2FnZVwiLCB7XG4gIGVudW1lcmFibGU6IHRydWUsXG4gIGdldDogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiBwYWNrYWdlX2pzXzIuUGFja2FnZTtcbiAgfVxufSk7XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJQYWNrYWdlRXJyb3JcIiwge1xuICBlbnVtZXJhYmxlOiB0cnVlLFxuICBnZXQ6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4gcGFja2FnZV9qc18yLlBhY2thZ2VFcnJvcjtcbiAgfVxufSk7XG52YXIgRnVuY3Rpb25MaXN0X2pzXzEgPSByZXF1aXJlKFwiLi4vdXRpbC9GdW5jdGlvbkxpc3QuanNcIik7XG5leHBvcnRzLlBhdGhGaWx0ZXJzID0ge1xuICBzb3VyY2U6IGZ1bmN0aW9uIChkYXRhKSB7XG4gICAgaWYgKGV4cG9ydHMuQ09ORklHLnNvdXJjZS5oYXNPd25Qcm9wZXJ0eShkYXRhLm5hbWUpKSB7XG4gICAgICBkYXRhLm5hbWUgPSBleHBvcnRzLkNPTkZJRy5zb3VyY2VbZGF0YS5uYW1lXTtcbiAgICB9XG4gICAgcmV0dXJuIHRydWU7XG4gIH0sXG4gIG5vcm1hbGl6ZTogZnVuY3Rpb24gKGRhdGEpIHtcbiAgICB2YXIgbmFtZSA9IGRhdGEubmFtZTtcbiAgICBpZiAoIW5hbWUubWF0Y2goL14oPzpbYS16XSs6XFwvKT9cXC98W2Etel06XFxcXHxcXFsvaSkpIHtcbiAgICAgIGRhdGEubmFtZSA9ICdbbWF0aGpheF0vJyArIG5hbWUucmVwbGFjZSgvXlxcLlxcLy8sICcnKTtcbiAgICB9XG4gICAgaWYgKGRhdGEuYWRkRXh0ZW5zaW9uICYmICFuYW1lLm1hdGNoKC9cXC5bXlxcL10rJC8pKSB7XG4gICAgICBkYXRhLm5hbWUgKz0gJy5qcyc7XG4gICAgfVxuICAgIHJldHVybiB0cnVlO1xuICB9LFxuICBwcmVmaXg6IGZ1bmN0aW9uIChkYXRhKSB7XG4gICAgdmFyIG1hdGNoO1xuICAgIHdoaWxlIChtYXRjaCA9IGRhdGEubmFtZS5tYXRjaCgvXlxcWyhbXlxcXV0qKVxcXS8pKSB7XG4gICAgICBpZiAoIWV4cG9ydHMuQ09ORklHLnBhdGhzLmhhc093blByb3BlcnR5KG1hdGNoWzFdKSkgYnJlYWs7XG4gICAgICBkYXRhLm5hbWUgPSBleHBvcnRzLkNPTkZJRy5wYXRoc1ttYXRjaFsxXV0gKyBkYXRhLm5hbWUuc3Vic3RyKG1hdGNoWzBdLmxlbmd0aCk7XG4gICAgfVxuICAgIHJldHVybiB0cnVlO1xuICB9XG59O1xudmFyIExvYWRlcjtcbihmdW5jdGlvbiAoTG9hZGVyKSB7XG4gIHZhciBWRVJTSU9OID0gZ2xvYmFsX2pzXzEuTWF0aEpheC52ZXJzaW9uO1xuICBMb2FkZXIudmVyc2lvbnMgPSBuZXcgTWFwKCk7XG4gIGZ1bmN0aW9uIHJlYWR5KCkge1xuICAgIHZhciBlXzIsIF9hO1xuICAgIHZhciBuYW1lcyA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMDsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBuYW1lc1tfaV0gPSBhcmd1bWVudHNbX2ldO1xuICAgIH1cbiAgICBpZiAobmFtZXMubGVuZ3RoID09PSAwKSB7XG4gICAgICBuYW1lcyA9IEFycmF5LmZyb20ocGFja2FnZV9qc18xLlBhY2thZ2UucGFja2FnZXMua2V5cygpKTtcbiAgICB9XG4gICAgdmFyIHByb21pc2VzID0gW107XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIG5hbWVzXzEgPSBfX3ZhbHVlcyhuYW1lcyksIG5hbWVzXzFfMSA9IG5hbWVzXzEubmV4dCgpOyAhbmFtZXNfMV8xLmRvbmU7IG5hbWVzXzFfMSA9IG5hbWVzXzEubmV4dCgpKSB7XG4gICAgICAgIHZhciBuYW1lXzEgPSBuYW1lc18xXzEudmFsdWU7XG4gICAgICAgIHZhciBleHRlbnNpb24gPSBwYWNrYWdlX2pzXzEuUGFja2FnZS5wYWNrYWdlcy5nZXQobmFtZV8xKSB8fCBuZXcgcGFja2FnZV9qc18xLlBhY2thZ2UobmFtZV8xLCB0cnVlKTtcbiAgICAgICAgcHJvbWlzZXMucHVzaChleHRlbnNpb24ucHJvbWlzZSk7XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8yXzEpIHtcbiAgICAgIGVfMiA9IHtcbiAgICAgICAgZXJyb3I6IGVfMl8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAobmFtZXNfMV8xICYmICFuYW1lc18xXzEuZG9uZSAmJiAoX2EgPSBuYW1lc18xLnJldHVybikpIF9hLmNhbGwobmFtZXNfMSk7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8yKSB0aHJvdyBlXzIuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBQcm9taXNlLmFsbChwcm9taXNlcyk7XG4gIH1cbiAgTG9hZGVyLnJlYWR5ID0gcmVhZHk7XG4gIGZ1bmN0aW9uIGxvYWQoKSB7XG4gICAgdmFyIGVfMywgX2E7XG4gICAgdmFyIG5hbWVzID0gW107XG4gICAgZm9yICh2YXIgX2kgPSAwOyBfaSA8IGFyZ3VtZW50cy5sZW5ndGg7IF9pKyspIHtcbiAgICAgIG5hbWVzW19pXSA9IGFyZ3VtZW50c1tfaV07XG4gICAgfVxuICAgIGlmIChuYW1lcy5sZW5ndGggPT09IDApIHtcbiAgICAgIHJldHVybiBQcm9taXNlLnJlc29sdmUoKTtcbiAgICB9XG4gICAgdmFyIHByb21pc2VzID0gW107XG4gICAgdmFyIF9sb29wXzEgPSBmdW5jdGlvbiAobmFtZV8yKSB7XG4gICAgICB2YXIgZXh0ZW5zaW9uID0gcGFja2FnZV9qc18xLlBhY2thZ2UucGFja2FnZXMuZ2V0KG5hbWVfMik7XG4gICAgICBpZiAoIWV4dGVuc2lvbikge1xuICAgICAgICBleHRlbnNpb24gPSBuZXcgcGFja2FnZV9qc18xLlBhY2thZ2UobmFtZV8yKTtcbiAgICAgICAgZXh0ZW5zaW9uLnByb3ZpZGVzKGV4cG9ydHMuQ09ORklHLnByb3ZpZGVzW25hbWVfMl0pO1xuICAgICAgfVxuICAgICAgZXh0ZW5zaW9uLmNoZWNrTm9Mb2FkKCk7XG4gICAgICBwcm9taXNlcy5wdXNoKGV4dGVuc2lvbi5wcm9taXNlLnRoZW4oZnVuY3Rpb24gKCkge1xuICAgICAgICBpZiAoIWV4cG9ydHMuQ09ORklHLnZlcnNpb25XYXJuaW5ncykgcmV0dXJuO1xuICAgICAgICBpZiAoZXh0ZW5zaW9uLmlzTG9hZGVkICYmICFMb2FkZXIudmVyc2lvbnMuaGFzKHBhY2thZ2VfanNfMS5QYWNrYWdlLnJlc29sdmVQYXRoKG5hbWVfMikpKSB7XG4gICAgICAgICAgY29uc29sZS53YXJuKFwiTm8gdmVyc2lvbiBpbmZvcm1hdGlvbiBhdmFpbGFibGUgZm9yIGNvbXBvbmVudCBcIi5jb25jYXQobmFtZV8yKSk7XG4gICAgICAgIH1cbiAgICAgIH0pKTtcbiAgICB9O1xuICAgIHRyeSB7XG4gICAgICBmb3IgKHZhciBuYW1lc18yID0gX192YWx1ZXMobmFtZXMpLCBuYW1lc18yXzEgPSBuYW1lc18yLm5leHQoKTsgIW5hbWVzXzJfMS5kb25lOyBuYW1lc18yXzEgPSBuYW1lc18yLm5leHQoKSkge1xuICAgICAgICB2YXIgbmFtZV8yID0gbmFtZXNfMl8xLnZhbHVlO1xuICAgICAgICBfbG9vcF8xKG5hbWVfMik7XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8zXzEpIHtcbiAgICAgIGVfMyA9IHtcbiAgICAgICAgZXJyb3I6IGVfM18xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAobmFtZXNfMl8xICYmICFuYW1lc18yXzEuZG9uZSAmJiAoX2EgPSBuYW1lc18yLnJldHVybikpIF9hLmNhbGwobmFtZXNfMik7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8zKSB0aHJvdyBlXzMuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHBhY2thZ2VfanNfMS5QYWNrYWdlLmxvYWRBbGwoKTtcbiAgICByZXR1cm4gUHJvbWlzZS5hbGwocHJvbWlzZXMpO1xuICB9XG4gIExvYWRlci5sb2FkID0gbG9hZDtcbiAgZnVuY3Rpb24gcHJlTG9hZCgpIHtcbiAgICB2YXIgZV80LCBfYTtcbiAgICB2YXIgbmFtZXMgPSBbXTtcbiAgICBmb3IgKHZhciBfaSA9IDA7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgbmFtZXNbX2ldID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIG5hbWVzXzMgPSBfX3ZhbHVlcyhuYW1lcyksIG5hbWVzXzNfMSA9IG5hbWVzXzMubmV4dCgpOyAhbmFtZXNfM18xLmRvbmU7IG5hbWVzXzNfMSA9IG5hbWVzXzMubmV4dCgpKSB7XG4gICAgICAgIHZhciBuYW1lXzMgPSBuYW1lc18zXzEudmFsdWU7XG4gICAgICAgIHZhciBleHRlbnNpb24gPSBwYWNrYWdlX2pzXzEuUGFja2FnZS5wYWNrYWdlcy5nZXQobmFtZV8zKTtcbiAgICAgICAgaWYgKCFleHRlbnNpb24pIHtcbiAgICAgICAgICBleHRlbnNpb24gPSBuZXcgcGFja2FnZV9qc18xLlBhY2thZ2UobmFtZV8zLCB0cnVlKTtcbiAgICAgICAgICBleHRlbnNpb24ucHJvdmlkZXMoZXhwb3J0cy5DT05GSUcucHJvdmlkZXNbbmFtZV8zXSk7XG4gICAgICAgIH1cbiAgICAgICAgZXh0ZW5zaW9uLmxvYWRlZCgpO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfNF8xKSB7XG4gICAgICBlXzQgPSB7XG4gICAgICAgIGVycm9yOiBlXzRfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKG5hbWVzXzNfMSAmJiAhbmFtZXNfM18xLmRvbmUgJiYgKF9hID0gbmFtZXNfMy5yZXR1cm4pKSBfYS5jYWxsKG5hbWVzXzMpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfNCkgdGhyb3cgZV80LmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgfVxuICBMb2FkZXIucHJlTG9hZCA9IHByZUxvYWQ7XG4gIGZ1bmN0aW9uIGRlZmF1bHRSZWFkeSgpIHtcbiAgICBpZiAodHlwZW9mIGV4cG9ydHMuTWF0aEpheC5zdGFydHVwICE9PSAndW5kZWZpbmVkJykge1xuICAgICAgZXhwb3J0cy5NYXRoSmF4LmNvbmZpZy5zdGFydHVwLnJlYWR5KCk7XG4gICAgfVxuICB9XG4gIExvYWRlci5kZWZhdWx0UmVhZHkgPSBkZWZhdWx0UmVhZHk7XG4gIGZ1bmN0aW9uIGdldFJvb3QoKSB7XG4gICAgdmFyIHJvb3QgPSBfX2Rpcm5hbWUgKyAnLy4uLy4uL2VzNSc7XG4gICAgaWYgKHR5cGVvZiBkb2N1bWVudCAhPT0gJ3VuZGVmaW5lZCcpIHtcbiAgICAgIHZhciBzY3JpcHQgPSBkb2N1bWVudC5jdXJyZW50U2NyaXB0IHx8IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdNYXRoSmF4LXNjcmlwdCcpO1xuICAgICAgaWYgKHNjcmlwdCkge1xuICAgICAgICByb290ID0gc2NyaXB0LnNyYy5yZXBsYWNlKC9cXC9bXlxcL10qJC8sICcnKTtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIHJvb3Q7XG4gIH1cbiAgTG9hZGVyLmdldFJvb3QgPSBnZXRSb290O1xuICBmdW5jdGlvbiBjaGVja1ZlcnNpb24obmFtZSwgdmVyc2lvbiwgX3R5cGUpIHtcbiAgICBMb2FkZXIudmVyc2lvbnMuc2V0KHBhY2thZ2VfanNfMS5QYWNrYWdlLnJlc29sdmVQYXRoKG5hbWUpLCBWRVJTSU9OKTtcbiAgICBpZiAoZXhwb3J0cy5DT05GSUcudmVyc2lvbldhcm5pbmdzICYmIHZlcnNpb24gIT09IFZFUlNJT04pIHtcbiAgICAgIGNvbnNvbGUud2FybihcIkNvbXBvbmVudCBcIi5jb25jYXQobmFtZSwgXCIgdXNlcyBcIikuY29uY2F0KHZlcnNpb24sIFwiIG9mIE1hdGhKYXg7IHZlcnNpb24gaW4gdXNlIGlzIFwiKS5jb25jYXQoVkVSU0lPTikpO1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfVxuICAgIHJldHVybiBmYWxzZTtcbiAgfVxuICBMb2FkZXIuY2hlY2tWZXJzaW9uID0gY2hlY2tWZXJzaW9uO1xuICBMb2FkZXIucGF0aEZpbHRlcnMgPSBuZXcgRnVuY3Rpb25MaXN0X2pzXzEuRnVuY3Rpb25MaXN0KCk7XG4gIExvYWRlci5wYXRoRmlsdGVycy5hZGQoZXhwb3J0cy5QYXRoRmlsdGVycy5zb3VyY2UsIDApO1xuICBMb2FkZXIucGF0aEZpbHRlcnMuYWRkKGV4cG9ydHMuUGF0aEZpbHRlcnMubm9ybWFsaXplLCAxMCk7XG4gIExvYWRlci5wYXRoRmlsdGVycy5hZGQoZXhwb3J0cy5QYXRoRmlsdGVycy5wcmVmaXgsIDIwKTtcbn0pKExvYWRlciA9IGV4cG9ydHMuTG9hZGVyIHx8IChleHBvcnRzLkxvYWRlciA9IHt9KSk7XG5leHBvcnRzLk1hdGhKYXggPSBnbG9iYWxfanNfMS5NYXRoSmF4O1xuaWYgKHR5cGVvZiBleHBvcnRzLk1hdGhKYXgubG9hZGVyID09PSAndW5kZWZpbmVkJykge1xuICAoMCwgZ2xvYmFsX2pzXzEuY29tYmluZURlZmF1bHRzKShleHBvcnRzLk1hdGhKYXguY29uZmlnLCAnbG9hZGVyJywge1xuICAgIHBhdGhzOiB7XG4gICAgICBtYXRoamF4OiBMb2FkZXIuZ2V0Um9vdCgpXG4gICAgfSxcbiAgICBzb3VyY2U6IHt9LFxuICAgIGRlcGVuZGVuY2llczoge30sXG4gICAgcHJvdmlkZXM6IHt9LFxuICAgIGxvYWQ6IFtdLFxuICAgIHJlYWR5OiBMb2FkZXIuZGVmYXVsdFJlYWR5LmJpbmQoTG9hZGVyKSxcbiAgICBmYWlsZWQ6IGZ1bmN0aW9uIChlcnJvcikge1xuICAgICAgcmV0dXJuIGNvbnNvbGUubG9nKFwiTWF0aEpheChcIi5jb25jYXQoZXJyb3IucGFja2FnZSB8fCAnPycsIFwiKTogXCIpLmNvbmNhdChlcnJvci5tZXNzYWdlKSk7XG4gICAgfSxcbiAgICByZXF1aXJlOiBudWxsLFxuICAgIHBhdGhGaWx0ZXJzOiBbXSxcbiAgICB2ZXJzaW9uV2FybmluZ3M6IHRydWVcbiAgfSk7XG4gICgwLCBnbG9iYWxfanNfMS5jb21iaW5lV2l0aE1hdGhKYXgpKHtcbiAgICBsb2FkZXI6IExvYWRlclxuICB9KTtcbiAgdHJ5IHtcbiAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKGV4cG9ydHMuTWF0aEpheC5jb25maWcubG9hZGVyLnBhdGhGaWx0ZXJzKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgdmFyIGZpbHRlciA9IF9jLnZhbHVlO1xuICAgICAgaWYgKEFycmF5LmlzQXJyYXkoZmlsdGVyKSkge1xuICAgICAgICBMb2FkZXIucGF0aEZpbHRlcnMuYWRkKGZpbHRlclswXSwgZmlsdGVyWzFdKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIExvYWRlci5wYXRoRmlsdGVycy5hZGQoZmlsdGVyKTtcbiAgICAgIH1cbiAgICB9XG4gIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgZV8xID0ge1xuICAgICAgZXJyb3I6IGVfMV8xXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgfVxuICB9XG59XG5leHBvcnRzLkNPTkZJRyA9IGV4cG9ydHMuTWF0aEpheC5jb25maWcubG9hZGVyOyIsIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xudmFyIF9fc3ByZWFkQXJyYXkgPSB0aGlzICYmIHRoaXMuX19zcHJlYWRBcnJheSB8fCBmdW5jdGlvbiAodG8sIGZyb20sIHBhY2spIHtcbiAgaWYgKHBhY2sgfHwgYXJndW1lbnRzLmxlbmd0aCA9PT0gMikgZm9yICh2YXIgaSA9IDAsIGwgPSBmcm9tLmxlbmd0aCwgYXI7IGkgPCBsOyBpKyspIHtcbiAgICBpZiAoYXIgfHwgIShpIGluIGZyb20pKSB7XG4gICAgICBpZiAoIWFyKSBhciA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20sIDAsIGkpO1xuICAgICAgYXJbaV0gPSBmcm9tW2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdG8uY29uY2F0KGFyIHx8IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20pKTtcbn07XG52YXIgX19pbXBvcnREZWZhdWx0ID0gdGhpcyAmJiB0aGlzLl9faW1wb3J0RGVmYXVsdCB8fCBmdW5jdGlvbiAobW9kKSB7XG4gIHJldHVybiBtb2QgJiYgbW9kLl9fZXNNb2R1bGUgPyBtb2QgOiB7XG4gICAgXCJkZWZhdWx0XCI6IG1vZFxuICB9O1xufTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLlJlcXVpcmVDb25maWd1cmF0aW9uID0gZXhwb3J0cy5vcHRpb25zID0gZXhwb3J0cy5SZXF1aXJlTWV0aG9kcyA9IGV4cG9ydHMuUmVxdWlyZUxvYWQgPSB2b2lkIDA7XG52YXIgQ29uZmlndXJhdGlvbl9qc18xID0gcmVxdWlyZShcIi4uL0NvbmZpZ3VyYXRpb24uanNcIik7XG52YXIgU3ltYm9sTWFwX2pzXzEgPSByZXF1aXJlKFwiLi4vU3ltYm9sTWFwLmpzXCIpO1xudmFyIFRleEVycm9yX2pzXzEgPSBfX2ltcG9ydERlZmF1bHQocmVxdWlyZShcIi4uL1RleEVycm9yLmpzXCIpKTtcbnZhciBnbG9iYWxfanNfMSA9IHJlcXVpcmUoXCIuLi8uLi8uLi9jb21wb25lbnRzL2dsb2JhbC5qc1wiKTtcbnZhciBwYWNrYWdlX2pzXzEgPSByZXF1aXJlKFwiLi4vLi4vLi4vY29tcG9uZW50cy9wYWNrYWdlLmpzXCIpO1xudmFyIGxvYWRlcl9qc18xID0gcmVxdWlyZShcIi4uLy4uLy4uL2NvbXBvbmVudHMvbG9hZGVyLmpzXCIpO1xudmFyIG1hdGhqYXhfanNfMSA9IHJlcXVpcmUoXCIuLi8uLi8uLi9tYXRoamF4LmpzXCIpO1xudmFyIE9wdGlvbnNfanNfMSA9IHJlcXVpcmUoXCIuLi8uLi8uLi91dGlsL09wdGlvbnMuanNcIik7XG52YXIgTUpDT05GSUcgPSBnbG9iYWxfanNfMS5NYXRoSmF4LmNvbmZpZztcbmZ1bmN0aW9uIFJlZ2lzdGVyRXh0ZW5zaW9uKGpheCwgbmFtZSkge1xuICB2YXIgX2E7XG4gIHZhciByZXF1aXJlID0gamF4LnBhcnNlT3B0aW9ucy5vcHRpb25zLnJlcXVpcmU7XG4gIHZhciByZXF1aXJlZCA9IGpheC5wYXJzZU9wdGlvbnMucGFja2FnZURhdGEuZ2V0KCdyZXF1aXJlJykucmVxdWlyZWQ7XG4gIHZhciBleHRlbnNpb24gPSBuYW1lLnN1YnN0cihyZXF1aXJlLnByZWZpeC5sZW5ndGgpO1xuICBpZiAocmVxdWlyZWQuaW5kZXhPZihleHRlbnNpb24pIDwgMCkge1xuICAgIHJlcXVpcmVkLnB1c2goZXh0ZW5zaW9uKTtcbiAgICBSZWdpc3RlckRlcGVuZGVuY2llcyhqYXgsIGxvYWRlcl9qc18xLkNPTkZJRy5kZXBlbmRlbmNpZXNbbmFtZV0pO1xuICAgIHZhciBoYW5kbGVyID0gQ29uZmlndXJhdGlvbl9qc18xLkNvbmZpZ3VyYXRpb25IYW5kbGVyLmdldChleHRlbnNpb24pO1xuICAgIGlmIChoYW5kbGVyKSB7XG4gICAgICB2YXIgb3B0aW9uc18xID0gTUpDT05GSUdbbmFtZV0gfHwge307XG4gICAgICBpZiAoaGFuZGxlci5vcHRpb25zICYmIE9iamVjdC5rZXlzKGhhbmRsZXIub3B0aW9ucykubGVuZ3RoID09PSAxICYmIGhhbmRsZXIub3B0aW9uc1tleHRlbnNpb25dKSB7XG4gICAgICAgIG9wdGlvbnNfMSA9IChfYSA9IHt9LCBfYVtleHRlbnNpb25dID0gb3B0aW9uc18xLCBfYSk7XG4gICAgICB9XG4gICAgICBqYXguY29uZmlndXJhdGlvbi5hZGQoZXh0ZW5zaW9uLCBqYXgsIG9wdGlvbnNfMSk7XG4gICAgICB2YXIgY29uZmlndXJlZCA9IGpheC5wYXJzZU9wdGlvbnMucGFja2FnZURhdGEuZ2V0KCdyZXF1aXJlJykuY29uZmlndXJlZDtcbiAgICAgIGlmIChoYW5kbGVyLnByZXByb2Nlc3NvcnMubGVuZ3RoICYmICFjb25maWd1cmVkLmhhcyhleHRlbnNpb24pKSB7XG4gICAgICAgIGNvbmZpZ3VyZWQuc2V0KGV4dGVuc2lvbiwgdHJ1ZSk7XG4gICAgICAgIG1hdGhqYXhfanNfMS5tYXRoamF4LnJldHJ5QWZ0ZXIoUHJvbWlzZS5yZXNvbHZlKCkpO1xuICAgICAgfVxuICAgIH1cbiAgfVxufVxuZnVuY3Rpb24gUmVnaXN0ZXJEZXBlbmRlbmNpZXMoamF4LCBuYW1lcykge1xuICB2YXIgZV8xLCBfYTtcbiAgaWYgKG5hbWVzID09PSB2b2lkIDApIHtcbiAgICBuYW1lcyA9IFtdO1xuICB9XG4gIHZhciBwcmVmaXggPSBqYXgucGFyc2VPcHRpb25zLm9wdGlvbnMucmVxdWlyZS5wcmVmaXg7XG4gIHRyeSB7XG4gICAgZm9yICh2YXIgbmFtZXNfMSA9IF9fdmFsdWVzKG5hbWVzKSwgbmFtZXNfMV8xID0gbmFtZXNfMS5uZXh0KCk7ICFuYW1lc18xXzEuZG9uZTsgbmFtZXNfMV8xID0gbmFtZXNfMS5uZXh0KCkpIHtcbiAgICAgIHZhciBuYW1lXzEgPSBuYW1lc18xXzEudmFsdWU7XG4gICAgICBpZiAobmFtZV8xLnN1YnN0cigwLCBwcmVmaXgubGVuZ3RoKSA9PT0gcHJlZml4KSB7XG4gICAgICAgIFJlZ2lzdGVyRXh0ZW5zaW9uKGpheCwgbmFtZV8xKTtcbiAgICAgIH1cbiAgICB9XG4gIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgZV8xID0ge1xuICAgICAgZXJyb3I6IGVfMV8xXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKG5hbWVzXzFfMSAmJiAhbmFtZXNfMV8xLmRvbmUgJiYgKF9hID0gbmFtZXNfMS5yZXR1cm4pKSBfYS5jYWxsKG5hbWVzXzEpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgfVxuICB9XG59XG5mdW5jdGlvbiBSZXF1aXJlTG9hZChwYXJzZXIsIG5hbWUpIHtcbiAgdmFyIG9wdGlvbnMgPSBwYXJzZXIub3B0aW9ucy5yZXF1aXJlO1xuICB2YXIgYWxsb3cgPSBvcHRpb25zLmFsbG93O1xuICB2YXIgZXh0ZW5zaW9uID0gKG5hbWUuc3Vic3RyKDAsIDEpID09PSAnWycgPyAnJyA6IG9wdGlvbnMucHJlZml4KSArIG5hbWU7XG4gIHZhciBhbGxvd2VkID0gYWxsb3cuaGFzT3duUHJvcGVydHkoZXh0ZW5zaW9uKSA/IGFsbG93W2V4dGVuc2lvbl0gOiBhbGxvdy5oYXNPd25Qcm9wZXJ0eShuYW1lKSA/IGFsbG93W25hbWVdIDogb3B0aW9ucy5kZWZhdWx0QWxsb3c7XG4gIGlmICghYWxsb3dlZCkge1xuICAgIHRocm93IG5ldyBUZXhFcnJvcl9qc18xLmRlZmF1bHQoJ0JhZFJlcXVpcmUnLCAnRXh0ZW5zaW9uIFwiJTFcIiBpcyBub3QgYWxsb3dlZCB0byBiZSBsb2FkZWQnLCBleHRlbnNpb24pO1xuICB9XG4gIGlmIChwYWNrYWdlX2pzXzEuUGFja2FnZS5wYWNrYWdlcy5oYXMoZXh0ZW5zaW9uKSkge1xuICAgIFJlZ2lzdGVyRXh0ZW5zaW9uKHBhcnNlci5jb25maWd1cmF0aW9uLnBhY2thZ2VEYXRhLmdldCgncmVxdWlyZScpLmpheCwgZXh0ZW5zaW9uKTtcbiAgfSBlbHNlIHtcbiAgICBtYXRoamF4X2pzXzEubWF0aGpheC5yZXRyeUFmdGVyKGxvYWRlcl9qc18xLkxvYWRlci5sb2FkKGV4dGVuc2lvbikpO1xuICB9XG59XG5leHBvcnRzLlJlcXVpcmVMb2FkID0gUmVxdWlyZUxvYWQ7XG5mdW5jdGlvbiBjb25maWcoX2NvbmZpZywgamF4KSB7XG4gIGpheC5wYXJzZU9wdGlvbnMucGFja2FnZURhdGEuc2V0KCdyZXF1aXJlJywge1xuICAgIGpheDogamF4LFxuICAgIHJlcXVpcmVkOiBfX3NwcmVhZEFycmF5KFtdLCBfX3JlYWQoamF4Lm9wdGlvbnMucGFja2FnZXMpLCBmYWxzZSksXG4gICAgY29uZmlndXJlZDogbmV3IE1hcCgpXG4gIH0pO1xuICB2YXIgb3B0aW9ucyA9IGpheC5wYXJzZU9wdGlvbnMub3B0aW9ucy5yZXF1aXJlO1xuICB2YXIgcHJlZml4ID0gb3B0aW9ucy5wcmVmaXg7XG4gIGlmIChwcmVmaXgubWF0Y2goL1teX2EtekEtWjAtOV0vKSkge1xuICAgIHRocm93IEVycm9yKCdJbGxlZ2FsIGNoYXJhY3RlcnMgdXNlZCBpbiBcXFxccmVxdWlyZSBwcmVmaXgnKTtcbiAgfVxuICBpZiAoIWxvYWRlcl9qc18xLkNPTkZJRy5wYXRoc1twcmVmaXhdKSB7XG4gICAgbG9hZGVyX2pzXzEuQ09ORklHLnBhdGhzW3ByZWZpeF0gPSAnW21hdGhqYXhdL2lucHV0L3RleC9leHRlbnNpb25zJztcbiAgfVxuICBvcHRpb25zLnByZWZpeCA9ICdbJyArIHByZWZpeCArICddLyc7XG59XG5leHBvcnRzLlJlcXVpcmVNZXRob2RzID0ge1xuICBSZXF1aXJlOiBmdW5jdGlvbiAocGFyc2VyLCBuYW1lKSB7XG4gICAgdmFyIHJlcXVpcmVkID0gcGFyc2VyLkdldEFyZ3VtZW50KG5hbWUpO1xuICAgIGlmIChyZXF1aXJlZC5tYXRjaCgvW15fYS16QS1aMC05XS8pIHx8IHJlcXVpcmVkID09PSAnJykge1xuICAgICAgdGhyb3cgbmV3IFRleEVycm9yX2pzXzEuZGVmYXVsdCgnQmFkUGFja2FnZU5hbWUnLCAnQXJndW1lbnQgZm9yICUxIGlzIG5vdCBhIHZhbGlkIHBhY2thZ2UgbmFtZScsIG5hbWUpO1xuICAgIH1cbiAgICBSZXF1aXJlTG9hZChwYXJzZXIsIHJlcXVpcmVkKTtcbiAgfVxufTtcbmV4cG9ydHMub3B0aW9ucyA9IHtcbiAgcmVxdWlyZToge1xuICAgIGFsbG93OiAoMCwgT3B0aW9uc19qc18xLmV4cGFuZGFibGUpKHtcbiAgICAgIGJhc2U6IGZhbHNlLFxuICAgICAgJ2FsbC1wYWNrYWdlcyc6IGZhbHNlLFxuICAgICAgYXV0b2xvYWQ6IGZhbHNlLFxuICAgICAgY29uZmlnbWFjcm9zOiBmYWxzZSxcbiAgICAgIHRhZ2Zvcm1hdDogZmFsc2UsXG4gICAgICBzZXRvcHRpb25zOiBmYWxzZVxuICAgIH0pLFxuICAgIGRlZmF1bHRBbGxvdzogdHJ1ZSxcbiAgICBwcmVmaXg6ICd0ZXgnXG4gIH1cbn07XG5uZXcgU3ltYm9sTWFwX2pzXzEuQ29tbWFuZE1hcCgncmVxdWlyZScsIHtcbiAgcmVxdWlyZTogJ1JlcXVpcmUnXG59LCBleHBvcnRzLlJlcXVpcmVNZXRob2RzKTtcbmV4cG9ydHMuUmVxdWlyZUNvbmZpZ3VyYXRpb24gPSBDb25maWd1cmF0aW9uX2pzXzEuQ29uZmlndXJhdGlvbi5jcmVhdGUoJ3JlcXVpcmUnLCB7XG4gIGhhbmRsZXI6IHtcbiAgICBtYWNybzogWydyZXF1aXJlJ11cbiAgfSxcbiAgY29uZmlnOiBjb25maWcsXG4gIG9wdGlvbnM6IGV4cG9ydHMub3B0aW9uc1xufSk7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==