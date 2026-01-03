"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3588],{

/***/ 53588
(__unused_webpack_module, exports) {



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
exports.lookup = exports.separateOptions = exports.selectOptionsFromKeys = exports.selectOptions = exports.userOptions = exports.defaultOptions = exports.insert = exports.copy = exports.keys = exports.makeArray = exports.expandable = exports.Expandable = exports.OPTIONS = exports.REMOVE = exports.APPEND = exports.isObject = void 0;
var OBJECT = {}.constructor;
function isObject(obj) {
  return typeof obj === 'object' && obj !== null && (obj.constructor === OBJECT || obj.constructor === Expandable);
}
exports.isObject = isObject;
exports.APPEND = '[+]';
exports.REMOVE = '[-]';
exports.OPTIONS = {
  invalidOption: 'warn',
  optionError: function (message, _key) {
    if (exports.OPTIONS.invalidOption === 'fatal') {
      throw new Error(message);
    }
    console.warn('MathJax: ' + message);
  }
};
var Expandable = function () {
  function Expandable() {}
  return Expandable;
}();
exports.Expandable = Expandable;
function expandable(def) {
  return Object.assign(Object.create(Expandable.prototype), def);
}
exports.expandable = expandable;
function makeArray(x) {
  return Array.isArray(x) ? x : [x];
}
exports.makeArray = makeArray;
function keys(def) {
  if (!def) {
    return [];
  }
  return Object.keys(def).concat(Object.getOwnPropertySymbols(def));
}
exports.keys = keys;
function copy(def) {
  var e_1, _a;
  var props = {};
  try {
    for (var _b = __values(keys(def)), _c = _b.next(); !_c.done; _c = _b.next()) {
      var key = _c.value;
      var prop = Object.getOwnPropertyDescriptor(def, key);
      var value = prop.value;
      if (Array.isArray(value)) {
        prop.value = insert([], value, false);
      } else if (isObject(value)) {
        prop.value = copy(value);
      }
      if (prop.enumerable) {
        props[key] = prop;
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
  return Object.defineProperties(def.constructor === Expandable ? expandable({}) : {}, props);
}
exports.copy = copy;
function insert(dst, src, warn) {
  var e_2, _a;
  if (warn === void 0) {
    warn = true;
  }
  var _loop_1 = function (key) {
    if (warn && dst[key] === undefined && dst.constructor !== Expandable) {
      if (typeof key === 'symbol') {
        key = key.toString();
      }
      exports.OPTIONS.optionError("Invalid option \"".concat(key, "\" (no default value)."), key);
      return "continue";
    }
    var sval = src[key],
      dval = dst[key];
    if (isObject(sval) && dval !== null && (typeof dval === 'object' || typeof dval === 'function')) {
      var ids = keys(sval);
      if (Array.isArray(dval) && (ids.length === 1 && (ids[0] === exports.APPEND || ids[0] === exports.REMOVE) && Array.isArray(sval[ids[0]]) || ids.length === 2 && ids.sort().join(',') === exports.APPEND + ',' + exports.REMOVE && Array.isArray(sval[exports.APPEND]) && Array.isArray(sval[exports.REMOVE]))) {
        if (sval[exports.REMOVE]) {
          dval = dst[key] = dval.filter(function (x) {
            return sval[exports.REMOVE].indexOf(x) < 0;
          });
        }
        if (sval[exports.APPEND]) {
          dst[key] = __spreadArray(__spreadArray([], __read(dval), false), __read(sval[exports.APPEND]), false);
        }
      } else {
        insert(dval, sval, warn);
      }
    } else if (Array.isArray(sval)) {
      dst[key] = [];
      insert(dst[key], sval, false);
    } else if (isObject(sval)) {
      dst[key] = copy(sval);
    } else {
      dst[key] = sval;
    }
  };
  try {
    for (var _b = __values(keys(src)), _c = _b.next(); !_c.done; _c = _b.next()) {
      var key = _c.value;
      _loop_1(key);
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
exports.insert = insert;
function defaultOptions(options) {
  var defs = [];
  for (var _i = 1; _i < arguments.length; _i++) {
    defs[_i - 1] = arguments[_i];
  }
  defs.forEach(function (def) {
    return insert(options, def, false);
  });
  return options;
}
exports.defaultOptions = defaultOptions;
function userOptions(options) {
  var defs = [];
  for (var _i = 1; _i < arguments.length; _i++) {
    defs[_i - 1] = arguments[_i];
  }
  defs.forEach(function (def) {
    return insert(options, def, true);
  });
  return options;
}
exports.userOptions = userOptions;
function selectOptions(options) {
  var e_3, _a;
  var keys = [];
  for (var _i = 1; _i < arguments.length; _i++) {
    keys[_i - 1] = arguments[_i];
  }
  var subset = {};
  try {
    for (var keys_1 = __values(keys), keys_1_1 = keys_1.next(); !keys_1_1.done; keys_1_1 = keys_1.next()) {
      var key = keys_1_1.value;
      if (options.hasOwnProperty(key)) {
        subset[key] = options[key];
      }
    }
  } catch (e_3_1) {
    e_3 = {
      error: e_3_1
    };
  } finally {
    try {
      if (keys_1_1 && !keys_1_1.done && (_a = keys_1.return)) _a.call(keys_1);
    } finally {
      if (e_3) throw e_3.error;
    }
  }
  return subset;
}
exports.selectOptions = selectOptions;
function selectOptionsFromKeys(options, object) {
  return selectOptions.apply(void 0, __spreadArray([options], __read(Object.keys(object)), false));
}
exports.selectOptionsFromKeys = selectOptionsFromKeys;
function separateOptions(options) {
  var e_4, _a, e_5, _b;
  var objects = [];
  for (var _i = 1; _i < arguments.length; _i++) {
    objects[_i - 1] = arguments[_i];
  }
  var results = [];
  try {
    for (var objects_1 = __values(objects), objects_1_1 = objects_1.next(); !objects_1_1.done; objects_1_1 = objects_1.next()) {
      var object = objects_1_1.value;
      var exists = {},
        missing = {};
      try {
        for (var _c = (e_5 = void 0, __values(Object.keys(options || {}))), _d = _c.next(); !_d.done; _d = _c.next()) {
          var key = _d.value;
          (object[key] === undefined ? missing : exists)[key] = options[key];
        }
      } catch (e_5_1) {
        e_5 = {
          error: e_5_1
        };
      } finally {
        try {
          if (_d && !_d.done && (_b = _c.return)) _b.call(_c);
        } finally {
          if (e_5) throw e_5.error;
        }
      }
      results.push(exists);
      options = missing;
    }
  } catch (e_4_1) {
    e_4 = {
      error: e_4_1
    };
  } finally {
    try {
      if (objects_1_1 && !objects_1_1.done && (_a = objects_1.return)) _a.call(objects_1);
    } finally {
      if (e_4) throw e_4.error;
    }
  }
  results.unshift(options);
  return results;
}
exports.separateOptions = separateOptions;
function lookup(name, lookup, def) {
  if (def === void 0) {
    def = null;
  }
  return lookup.hasOwnProperty(name) ? lookup[name] : def;
}
exports.lookup = lookup;

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzU4OC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvdXRpbC9PcHRpb25zLmpzIl0sInNvdXJjZXNDb250ZW50IjpbIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xudmFyIF9fc3ByZWFkQXJyYXkgPSB0aGlzICYmIHRoaXMuX19zcHJlYWRBcnJheSB8fCBmdW5jdGlvbiAodG8sIGZyb20sIHBhY2spIHtcbiAgaWYgKHBhY2sgfHwgYXJndW1lbnRzLmxlbmd0aCA9PT0gMikgZm9yICh2YXIgaSA9IDAsIGwgPSBmcm9tLmxlbmd0aCwgYXI7IGkgPCBsOyBpKyspIHtcbiAgICBpZiAoYXIgfHwgIShpIGluIGZyb20pKSB7XG4gICAgICBpZiAoIWFyKSBhciA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20sIDAsIGkpO1xuICAgICAgYXJbaV0gPSBmcm9tW2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdG8uY29uY2F0KGFyIHx8IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20pKTtcbn07XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5sb29rdXAgPSBleHBvcnRzLnNlcGFyYXRlT3B0aW9ucyA9IGV4cG9ydHMuc2VsZWN0T3B0aW9uc0Zyb21LZXlzID0gZXhwb3J0cy5zZWxlY3RPcHRpb25zID0gZXhwb3J0cy51c2VyT3B0aW9ucyA9IGV4cG9ydHMuZGVmYXVsdE9wdGlvbnMgPSBleHBvcnRzLmluc2VydCA9IGV4cG9ydHMuY29weSA9IGV4cG9ydHMua2V5cyA9IGV4cG9ydHMubWFrZUFycmF5ID0gZXhwb3J0cy5leHBhbmRhYmxlID0gZXhwb3J0cy5FeHBhbmRhYmxlID0gZXhwb3J0cy5PUFRJT05TID0gZXhwb3J0cy5SRU1PVkUgPSBleHBvcnRzLkFQUEVORCA9IGV4cG9ydHMuaXNPYmplY3QgPSB2b2lkIDA7XG52YXIgT0JKRUNUID0ge30uY29uc3RydWN0b3I7XG5mdW5jdGlvbiBpc09iamVjdChvYmopIHtcbiAgcmV0dXJuIHR5cGVvZiBvYmogPT09ICdvYmplY3QnICYmIG9iaiAhPT0gbnVsbCAmJiAob2JqLmNvbnN0cnVjdG9yID09PSBPQkpFQ1QgfHwgb2JqLmNvbnN0cnVjdG9yID09PSBFeHBhbmRhYmxlKTtcbn1cbmV4cG9ydHMuaXNPYmplY3QgPSBpc09iamVjdDtcbmV4cG9ydHMuQVBQRU5EID0gJ1srXSc7XG5leHBvcnRzLlJFTU9WRSA9ICdbLV0nO1xuZXhwb3J0cy5PUFRJT05TID0ge1xuICBpbnZhbGlkT3B0aW9uOiAnd2FybicsXG4gIG9wdGlvbkVycm9yOiBmdW5jdGlvbiAobWVzc2FnZSwgX2tleSkge1xuICAgIGlmIChleHBvcnRzLk9QVElPTlMuaW52YWxpZE9wdGlvbiA9PT0gJ2ZhdGFsJykge1xuICAgICAgdGhyb3cgbmV3IEVycm9yKG1lc3NhZ2UpO1xuICAgIH1cbiAgICBjb25zb2xlLndhcm4oJ01hdGhKYXg6ICcgKyBtZXNzYWdlKTtcbiAgfVxufTtcbnZhciBFeHBhbmRhYmxlID0gZnVuY3Rpb24gKCkge1xuICBmdW5jdGlvbiBFeHBhbmRhYmxlKCkge31cbiAgcmV0dXJuIEV4cGFuZGFibGU7XG59KCk7XG5leHBvcnRzLkV4cGFuZGFibGUgPSBFeHBhbmRhYmxlO1xuZnVuY3Rpb24gZXhwYW5kYWJsZShkZWYpIHtcbiAgcmV0dXJuIE9iamVjdC5hc3NpZ24oT2JqZWN0LmNyZWF0ZShFeHBhbmRhYmxlLnByb3RvdHlwZSksIGRlZik7XG59XG5leHBvcnRzLmV4cGFuZGFibGUgPSBleHBhbmRhYmxlO1xuZnVuY3Rpb24gbWFrZUFycmF5KHgpIHtcbiAgcmV0dXJuIEFycmF5LmlzQXJyYXkoeCkgPyB4IDogW3hdO1xufVxuZXhwb3J0cy5tYWtlQXJyYXkgPSBtYWtlQXJyYXk7XG5mdW5jdGlvbiBrZXlzKGRlZikge1xuICBpZiAoIWRlZikge1xuICAgIHJldHVybiBbXTtcbiAgfVxuICByZXR1cm4gT2JqZWN0LmtleXMoZGVmKS5jb25jYXQoT2JqZWN0LmdldE93blByb3BlcnR5U3ltYm9scyhkZWYpKTtcbn1cbmV4cG9ydHMua2V5cyA9IGtleXM7XG5mdW5jdGlvbiBjb3B5KGRlZikge1xuICB2YXIgZV8xLCBfYTtcbiAgdmFyIHByb3BzID0ge307XG4gIHRyeSB7XG4gICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyhrZXlzKGRlZikpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICB2YXIga2V5ID0gX2MudmFsdWU7XG4gICAgICB2YXIgcHJvcCA9IE9iamVjdC5nZXRPd25Qcm9wZXJ0eURlc2NyaXB0b3IoZGVmLCBrZXkpO1xuICAgICAgdmFyIHZhbHVlID0gcHJvcC52YWx1ZTtcbiAgICAgIGlmIChBcnJheS5pc0FycmF5KHZhbHVlKSkge1xuICAgICAgICBwcm9wLnZhbHVlID0gaW5zZXJ0KFtdLCB2YWx1ZSwgZmFsc2UpO1xuICAgICAgfSBlbHNlIGlmIChpc09iamVjdCh2YWx1ZSkpIHtcbiAgICAgICAgcHJvcC52YWx1ZSA9IGNvcHkodmFsdWUpO1xuICAgICAgfVxuICAgICAgaWYgKHByb3AuZW51bWVyYWJsZSkge1xuICAgICAgICBwcm9wc1trZXldID0gcHJvcDtcbiAgICAgIH1cbiAgICB9XG4gIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgZV8xID0ge1xuICAgICAgZXJyb3I6IGVfMV8xXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgfVxuICB9XG4gIHJldHVybiBPYmplY3QuZGVmaW5lUHJvcGVydGllcyhkZWYuY29uc3RydWN0b3IgPT09IEV4cGFuZGFibGUgPyBleHBhbmRhYmxlKHt9KSA6IHt9LCBwcm9wcyk7XG59XG5leHBvcnRzLmNvcHkgPSBjb3B5O1xuZnVuY3Rpb24gaW5zZXJ0KGRzdCwgc3JjLCB3YXJuKSB7XG4gIHZhciBlXzIsIF9hO1xuICBpZiAod2FybiA9PT0gdm9pZCAwKSB7XG4gICAgd2FybiA9IHRydWU7XG4gIH1cbiAgdmFyIF9sb29wXzEgPSBmdW5jdGlvbiAoa2V5KSB7XG4gICAgaWYgKHdhcm4gJiYgZHN0W2tleV0gPT09IHVuZGVmaW5lZCAmJiBkc3QuY29uc3RydWN0b3IgIT09IEV4cGFuZGFibGUpIHtcbiAgICAgIGlmICh0eXBlb2Yga2V5ID09PSAnc3ltYm9sJykge1xuICAgICAgICBrZXkgPSBrZXkudG9TdHJpbmcoKTtcbiAgICAgIH1cbiAgICAgIGV4cG9ydHMuT1BUSU9OUy5vcHRpb25FcnJvcihcIkludmFsaWQgb3B0aW9uIFxcXCJcIi5jb25jYXQoa2V5LCBcIlxcXCIgKG5vIGRlZmF1bHQgdmFsdWUpLlwiKSwga2V5KTtcbiAgICAgIHJldHVybiBcImNvbnRpbnVlXCI7XG4gICAgfVxuICAgIHZhciBzdmFsID0gc3JjW2tleV0sXG4gICAgICBkdmFsID0gZHN0W2tleV07XG4gICAgaWYgKGlzT2JqZWN0KHN2YWwpICYmIGR2YWwgIT09IG51bGwgJiYgKHR5cGVvZiBkdmFsID09PSAnb2JqZWN0JyB8fCB0eXBlb2YgZHZhbCA9PT0gJ2Z1bmN0aW9uJykpIHtcbiAgICAgIHZhciBpZHMgPSBrZXlzKHN2YWwpO1xuICAgICAgaWYgKEFycmF5LmlzQXJyYXkoZHZhbCkgJiYgKGlkcy5sZW5ndGggPT09IDEgJiYgKGlkc1swXSA9PT0gZXhwb3J0cy5BUFBFTkQgfHwgaWRzWzBdID09PSBleHBvcnRzLlJFTU9WRSkgJiYgQXJyYXkuaXNBcnJheShzdmFsW2lkc1swXV0pIHx8IGlkcy5sZW5ndGggPT09IDIgJiYgaWRzLnNvcnQoKS5qb2luKCcsJykgPT09IGV4cG9ydHMuQVBQRU5EICsgJywnICsgZXhwb3J0cy5SRU1PVkUgJiYgQXJyYXkuaXNBcnJheShzdmFsW2V4cG9ydHMuQVBQRU5EXSkgJiYgQXJyYXkuaXNBcnJheShzdmFsW2V4cG9ydHMuUkVNT1ZFXSkpKSB7XG4gICAgICAgIGlmIChzdmFsW2V4cG9ydHMuUkVNT1ZFXSkge1xuICAgICAgICAgIGR2YWwgPSBkc3Rba2V5XSA9IGR2YWwuZmlsdGVyKGZ1bmN0aW9uICh4KSB7XG4gICAgICAgICAgICByZXR1cm4gc3ZhbFtleHBvcnRzLlJFTU9WRV0uaW5kZXhPZih4KSA8IDA7XG4gICAgICAgICAgfSk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHN2YWxbZXhwb3J0cy5BUFBFTkRdKSB7XG4gICAgICAgICAgZHN0W2tleV0gPSBfX3NwcmVhZEFycmF5KF9fc3ByZWFkQXJyYXkoW10sIF9fcmVhZChkdmFsKSwgZmFsc2UpLCBfX3JlYWQoc3ZhbFtleHBvcnRzLkFQUEVORF0pLCBmYWxzZSk7XG4gICAgICAgIH1cbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIGluc2VydChkdmFsLCBzdmFsLCB3YXJuKTtcbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKEFycmF5LmlzQXJyYXkoc3ZhbCkpIHtcbiAgICAgIGRzdFtrZXldID0gW107XG4gICAgICBpbnNlcnQoZHN0W2tleV0sIHN2YWwsIGZhbHNlKTtcbiAgICB9IGVsc2UgaWYgKGlzT2JqZWN0KHN2YWwpKSB7XG4gICAgICBkc3Rba2V5XSA9IGNvcHkoc3ZhbCk7XG4gICAgfSBlbHNlIHtcbiAgICAgIGRzdFtrZXldID0gc3ZhbDtcbiAgICB9XG4gIH07XG4gIHRyeSB7XG4gICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyhrZXlzKHNyYykpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICB2YXIga2V5ID0gX2MudmFsdWU7XG4gICAgICBfbG9vcF8xKGtleSk7XG4gICAgfVxuICB9IGNhdGNoIChlXzJfMSkge1xuICAgIGVfMiA9IHtcbiAgICAgIGVycm9yOiBlXzJfMVxuICAgIH07XG4gIH0gZmluYWxseSB7XG4gICAgdHJ5IHtcbiAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgaWYgKGVfMikgdGhyb3cgZV8yLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gZHN0O1xufVxuZXhwb3J0cy5pbnNlcnQgPSBpbnNlcnQ7XG5mdW5jdGlvbiBkZWZhdWx0T3B0aW9ucyhvcHRpb25zKSB7XG4gIHZhciBkZWZzID0gW107XG4gIGZvciAodmFyIF9pID0gMTsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgZGVmc1tfaSAtIDFdID0gYXJndW1lbnRzW19pXTtcbiAgfVxuICBkZWZzLmZvckVhY2goZnVuY3Rpb24gKGRlZikge1xuICAgIHJldHVybiBpbnNlcnQob3B0aW9ucywgZGVmLCBmYWxzZSk7XG4gIH0pO1xuICByZXR1cm4gb3B0aW9ucztcbn1cbmV4cG9ydHMuZGVmYXVsdE9wdGlvbnMgPSBkZWZhdWx0T3B0aW9ucztcbmZ1bmN0aW9uIHVzZXJPcHRpb25zKG9wdGlvbnMpIHtcbiAgdmFyIGRlZnMgPSBbXTtcbiAgZm9yICh2YXIgX2kgPSAxOyBfaSA8IGFyZ3VtZW50cy5sZW5ndGg7IF9pKyspIHtcbiAgICBkZWZzW19pIC0gMV0gPSBhcmd1bWVudHNbX2ldO1xuICB9XG4gIGRlZnMuZm9yRWFjaChmdW5jdGlvbiAoZGVmKSB7XG4gICAgcmV0dXJuIGluc2VydChvcHRpb25zLCBkZWYsIHRydWUpO1xuICB9KTtcbiAgcmV0dXJuIG9wdGlvbnM7XG59XG5leHBvcnRzLnVzZXJPcHRpb25zID0gdXNlck9wdGlvbnM7XG5mdW5jdGlvbiBzZWxlY3RPcHRpb25zKG9wdGlvbnMpIHtcbiAgdmFyIGVfMywgX2E7XG4gIHZhciBrZXlzID0gW107XG4gIGZvciAodmFyIF9pID0gMTsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAga2V5c1tfaSAtIDFdID0gYXJndW1lbnRzW19pXTtcbiAgfVxuICB2YXIgc3Vic2V0ID0ge307XG4gIHRyeSB7XG4gICAgZm9yICh2YXIga2V5c18xID0gX192YWx1ZXMoa2V5cyksIGtleXNfMV8xID0ga2V5c18xLm5leHQoKTsgIWtleXNfMV8xLmRvbmU7IGtleXNfMV8xID0ga2V5c18xLm5leHQoKSkge1xuICAgICAgdmFyIGtleSA9IGtleXNfMV8xLnZhbHVlO1xuICAgICAgaWYgKG9wdGlvbnMuaGFzT3duUHJvcGVydHkoa2V5KSkge1xuICAgICAgICBzdWJzZXRba2V5XSA9IG9wdGlvbnNba2V5XTtcbiAgICAgIH1cbiAgICB9XG4gIH0gY2F0Y2ggKGVfM18xKSB7XG4gICAgZV8zID0ge1xuICAgICAgZXJyb3I6IGVfM18xXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKGtleXNfMV8xICYmICFrZXlzXzFfMS5kb25lICYmIChfYSA9IGtleXNfMS5yZXR1cm4pKSBfYS5jYWxsKGtleXNfMSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlXzMpIHRocm93IGVfMy5lcnJvcjtcbiAgICB9XG4gIH1cbiAgcmV0dXJuIHN1YnNldDtcbn1cbmV4cG9ydHMuc2VsZWN0T3B0aW9ucyA9IHNlbGVjdE9wdGlvbnM7XG5mdW5jdGlvbiBzZWxlY3RPcHRpb25zRnJvbUtleXMob3B0aW9ucywgb2JqZWN0KSB7XG4gIHJldHVybiBzZWxlY3RPcHRpb25zLmFwcGx5KHZvaWQgMCwgX19zcHJlYWRBcnJheShbb3B0aW9uc10sIF9fcmVhZChPYmplY3Qua2V5cyhvYmplY3QpKSwgZmFsc2UpKTtcbn1cbmV4cG9ydHMuc2VsZWN0T3B0aW9uc0Zyb21LZXlzID0gc2VsZWN0T3B0aW9uc0Zyb21LZXlzO1xuZnVuY3Rpb24gc2VwYXJhdGVPcHRpb25zKG9wdGlvbnMpIHtcbiAgdmFyIGVfNCwgX2EsIGVfNSwgX2I7XG4gIHZhciBvYmplY3RzID0gW107XG4gIGZvciAodmFyIF9pID0gMTsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgb2JqZWN0c1tfaSAtIDFdID0gYXJndW1lbnRzW19pXTtcbiAgfVxuICB2YXIgcmVzdWx0cyA9IFtdO1xuICB0cnkge1xuICAgIGZvciAodmFyIG9iamVjdHNfMSA9IF9fdmFsdWVzKG9iamVjdHMpLCBvYmplY3RzXzFfMSA9IG9iamVjdHNfMS5uZXh0KCk7ICFvYmplY3RzXzFfMS5kb25lOyBvYmplY3RzXzFfMSA9IG9iamVjdHNfMS5uZXh0KCkpIHtcbiAgICAgIHZhciBvYmplY3QgPSBvYmplY3RzXzFfMS52YWx1ZTtcbiAgICAgIHZhciBleGlzdHMgPSB7fSxcbiAgICAgICAgbWlzc2luZyA9IHt9O1xuICAgICAgdHJ5IHtcbiAgICAgICAgZm9yICh2YXIgX2MgPSAoZV81ID0gdm9pZCAwLCBfX3ZhbHVlcyhPYmplY3Qua2V5cyhvcHRpb25zIHx8IHt9KSkpLCBfZCA9IF9jLm5leHQoKTsgIV9kLmRvbmU7IF9kID0gX2MubmV4dCgpKSB7XG4gICAgICAgICAgdmFyIGtleSA9IF9kLnZhbHVlO1xuICAgICAgICAgIChvYmplY3Rba2V5XSA9PT0gdW5kZWZpbmVkID8gbWlzc2luZyA6IGV4aXN0cylba2V5XSA9IG9wdGlvbnNba2V5XTtcbiAgICAgICAgfVxuICAgICAgfSBjYXRjaCAoZV81XzEpIHtcbiAgICAgICAgZV81ID0ge1xuICAgICAgICAgIGVycm9yOiBlXzVfMVxuICAgICAgICB9O1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICBpZiAoX2QgJiYgIV9kLmRvbmUgJiYgKF9iID0gX2MucmV0dXJuKSkgX2IuY2FsbChfYyk7XG4gICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgaWYgKGVfNSkgdGhyb3cgZV81LmVycm9yO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICByZXN1bHRzLnB1c2goZXhpc3RzKTtcbiAgICAgIG9wdGlvbnMgPSBtaXNzaW5nO1xuICAgIH1cbiAgfSBjYXRjaCAoZV80XzEpIHtcbiAgICBlXzQgPSB7XG4gICAgICBlcnJvcjogZV80XzFcbiAgICB9O1xuICB9IGZpbmFsbHkge1xuICAgIHRyeSB7XG4gICAgICBpZiAob2JqZWN0c18xXzEgJiYgIW9iamVjdHNfMV8xLmRvbmUgJiYgKF9hID0gb2JqZWN0c18xLnJldHVybikpIF9hLmNhbGwob2JqZWN0c18xKTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgaWYgKGVfNCkgdGhyb3cgZV80LmVycm9yO1xuICAgIH1cbiAgfVxuICByZXN1bHRzLnVuc2hpZnQob3B0aW9ucyk7XG4gIHJldHVybiByZXN1bHRzO1xufVxuZXhwb3J0cy5zZXBhcmF0ZU9wdGlvbnMgPSBzZXBhcmF0ZU9wdGlvbnM7XG5mdW5jdGlvbiBsb29rdXAobmFtZSwgbG9va3VwLCBkZWYpIHtcbiAgaWYgKGRlZiA9PT0gdm9pZCAwKSB7XG4gICAgZGVmID0gbnVsbDtcbiAgfVxuICByZXR1cm4gbG9va3VwLmhhc093blByb3BlcnR5KG5hbWUpID8gbG9va3VwW25hbWVdIDogZGVmO1xufVxuZXhwb3J0cy5sb29rdXAgPSBsb29rdXA7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==