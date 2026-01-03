"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3962],{

/***/ 8507
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
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MmlMerror = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var MmlMerror = function (_super) {
  __extends(MmlMerror, _super);
  function MmlMerror() {
    var _this = _super !== null && _super.apply(this, arguments) || this;
    _this.texclass = MmlNode_js_1.TEXCLASS.ORD;
    return _this;
  }
  Object.defineProperty(MmlMerror.prototype, "kind", {
    get: function () {
      return 'merror';
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MmlMerror.prototype, "arity", {
    get: function () {
      return -1;
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MmlMerror.prototype, "linebreakContainer", {
    get: function () {
      return true;
    },
    enumerable: false,
    configurable: true
  });
  MmlMerror.defaults = __assign({}, MmlNode_js_1.AbstractMmlNode.defaults);
  return MmlMerror;
}(MmlNode_js_1.AbstractMmlNode);
exports.MmlMerror = MmlMerror;

/***/ },

/***/ 13962
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
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MmlFactory = void 0;
var NodeFactory_js_1 = __webpack_require__(14760);
var MML_js_1 = __webpack_require__(60450);
var MmlFactory = function (_super) {
  __extends(MmlFactory, _super);
  function MmlFactory() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  Object.defineProperty(MmlFactory.prototype, "MML", {
    get: function () {
      return this.node;
    },
    enumerable: false,
    configurable: true
  });
  MmlFactory.defaultNodes = MML_js_1.MML;
  return MmlFactory;
}(NodeFactory_js_1.AbstractNodeFactory);
exports.MmlFactory = MmlFactory;

/***/ },

/***/ 14760
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
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.AbstractNodeFactory = void 0;
var Factory_js_1 = __webpack_require__(20344);
var AbstractNodeFactory = function (_super) {
  __extends(AbstractNodeFactory, _super);
  function AbstractNodeFactory() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  AbstractNodeFactory.prototype.create = function (kind, properties, children) {
    if (properties === void 0) {
      properties = {};
    }
    if (children === void 0) {
      children = [];
    }
    return this.node[kind](properties, children);
  };
  return AbstractNodeFactory;
}(Factory_js_1.AbstractFactory);
exports.AbstractNodeFactory = AbstractNodeFactory;

/***/ },

/***/ 60450
(__unused_webpack_module, exports, __webpack_require__) {



var _a;
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MML = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var math_js_1 = __webpack_require__(72678);
var mi_js_1 = __webpack_require__(74298);
var mn_js_1 = __webpack_require__(77987);
var mo_js_1 = __webpack_require__(73052);
var mtext_js_1 = __webpack_require__(64594);
var mspace_js_1 = __webpack_require__(36971);
var ms_js_1 = __webpack_require__(44712);
var mrow_js_1 = __webpack_require__(33017);
var mfrac_js_1 = __webpack_require__(94785);
var msqrt_js_1 = __webpack_require__(99175);
var mroot_js_1 = __webpack_require__(76113);
var mstyle_js_1 = __webpack_require__(83900);
var merror_js_1 = __webpack_require__(8507);
var mpadded_js_1 = __webpack_require__(42619);
var mphantom_js_1 = __webpack_require__(71384);
var mfenced_js_1 = __webpack_require__(81686);
var menclose_js_1 = __webpack_require__(36900);
var maction_js_1 = __webpack_require__(66479);
var msubsup_js_1 = __webpack_require__(64987);
var munderover_js_1 = __webpack_require__(84825);
var mmultiscripts_js_1 = __webpack_require__(31686);
var mtable_js_1 = __webpack_require__(28601);
var mtr_js_1 = __webpack_require__(11503);
var mtd_js_1 = __webpack_require__(87261);
var maligngroup_js_1 = __webpack_require__(86178);
var malignmark_js_1 = __webpack_require__(80305);
var mglyph_js_1 = __webpack_require__(68967);
var semantics_js_1 = __webpack_require__(72599);
var TeXAtom_js_1 = __webpack_require__(39402);
var mathchoice_js_1 = __webpack_require__(99505);
exports.MML = (_a = {}, _a[math_js_1.MmlMath.prototype.kind] = math_js_1.MmlMath, _a[mi_js_1.MmlMi.prototype.kind] = mi_js_1.MmlMi, _a[mn_js_1.MmlMn.prototype.kind] = mn_js_1.MmlMn, _a[mo_js_1.MmlMo.prototype.kind] = mo_js_1.MmlMo, _a[mtext_js_1.MmlMtext.prototype.kind] = mtext_js_1.MmlMtext, _a[mspace_js_1.MmlMspace.prototype.kind] = mspace_js_1.MmlMspace, _a[ms_js_1.MmlMs.prototype.kind] = ms_js_1.MmlMs, _a[mrow_js_1.MmlMrow.prototype.kind] = mrow_js_1.MmlMrow, _a[mrow_js_1.MmlInferredMrow.prototype.kind] = mrow_js_1.MmlInferredMrow, _a[mfrac_js_1.MmlMfrac.prototype.kind] = mfrac_js_1.MmlMfrac, _a[msqrt_js_1.MmlMsqrt.prototype.kind] = msqrt_js_1.MmlMsqrt, _a[mroot_js_1.MmlMroot.prototype.kind] = mroot_js_1.MmlMroot, _a[mstyle_js_1.MmlMstyle.prototype.kind] = mstyle_js_1.MmlMstyle, _a[merror_js_1.MmlMerror.prototype.kind] = merror_js_1.MmlMerror, _a[mpadded_js_1.MmlMpadded.prototype.kind] = mpadded_js_1.MmlMpadded, _a[mphantom_js_1.MmlMphantom.prototype.kind] = mphantom_js_1.MmlMphantom, _a[mfenced_js_1.MmlMfenced.prototype.kind] = mfenced_js_1.MmlMfenced, _a[menclose_js_1.MmlMenclose.prototype.kind] = menclose_js_1.MmlMenclose, _a[maction_js_1.MmlMaction.prototype.kind] = maction_js_1.MmlMaction, _a[msubsup_js_1.MmlMsub.prototype.kind] = msubsup_js_1.MmlMsub, _a[msubsup_js_1.MmlMsup.prototype.kind] = msubsup_js_1.MmlMsup, _a[msubsup_js_1.MmlMsubsup.prototype.kind] = msubsup_js_1.MmlMsubsup, _a[munderover_js_1.MmlMunder.prototype.kind] = munderover_js_1.MmlMunder, _a[munderover_js_1.MmlMover.prototype.kind] = munderover_js_1.MmlMover, _a[munderover_js_1.MmlMunderover.prototype.kind] = munderover_js_1.MmlMunderover, _a[mmultiscripts_js_1.MmlMmultiscripts.prototype.kind] = mmultiscripts_js_1.MmlMmultiscripts, _a[mmultiscripts_js_1.MmlMprescripts.prototype.kind] = mmultiscripts_js_1.MmlMprescripts, _a[mmultiscripts_js_1.MmlNone.prototype.kind] = mmultiscripts_js_1.MmlNone, _a[mtable_js_1.MmlMtable.prototype.kind] = mtable_js_1.MmlMtable, _a[mtr_js_1.MmlMlabeledtr.prototype.kind] = mtr_js_1.MmlMlabeledtr, _a[mtr_js_1.MmlMtr.prototype.kind] = mtr_js_1.MmlMtr, _a[mtd_js_1.MmlMtd.prototype.kind] = mtd_js_1.MmlMtd, _a[maligngroup_js_1.MmlMaligngroup.prototype.kind] = maligngroup_js_1.MmlMaligngroup, _a[malignmark_js_1.MmlMalignmark.prototype.kind] = malignmark_js_1.MmlMalignmark, _a[mglyph_js_1.MmlMglyph.prototype.kind] = mglyph_js_1.MmlMglyph, _a[semantics_js_1.MmlSemantics.prototype.kind] = semantics_js_1.MmlSemantics, _a[semantics_js_1.MmlAnnotation.prototype.kind] = semantics_js_1.MmlAnnotation, _a[semantics_js_1.MmlAnnotationXML.prototype.kind] = semantics_js_1.MmlAnnotationXML, _a[TeXAtom_js_1.TeXAtom.prototype.kind] = TeXAtom_js_1.TeXAtom, _a[mathchoice_js_1.MathChoice.prototype.kind] = mathchoice_js_1.MathChoice, _a[MmlNode_js_1.TextNode.prototype.kind] = MmlNode_js_1.TextNode, _a[MmlNode_js_1.XMLNode.prototype.kind] = MmlNode_js_1.XMLNode, _a);

/***/ },

/***/ 71384
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
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MmlMphantom = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var MmlMphantom = function (_super) {
  __extends(MmlMphantom, _super);
  function MmlMphantom() {
    var _this = _super !== null && _super.apply(this, arguments) || this;
    _this.texclass = MmlNode_js_1.TEXCLASS.ORD;
    return _this;
  }
  Object.defineProperty(MmlMphantom.prototype, "kind", {
    get: function () {
      return 'mphantom';
    },
    enumerable: false,
    configurable: true
  });
  MmlMphantom.defaults = __assign({}, MmlNode_js_1.AbstractMmlLayoutNode.defaults);
  return MmlMphantom;
}(MmlNode_js_1.AbstractMmlLayoutNode);
exports.MmlMphantom = MmlMphantom;

/***/ },

/***/ 80305
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
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MmlMalignmark = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var MmlMalignmark = function (_super) {
  __extends(MmlMalignmark, _super);
  function MmlMalignmark() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  Object.defineProperty(MmlMalignmark.prototype, "kind", {
    get: function () {
      return 'malignmark';
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MmlMalignmark.prototype, "arity", {
    get: function () {
      return 0;
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MmlMalignmark.prototype, "isSpacelike", {
    get: function () {
      return true;
    },
    enumerable: false,
    configurable: true
  });
  MmlMalignmark.defaults = __assign(__assign({}, MmlNode_js_1.AbstractMmlNode.defaults), {
    edge: 'left'
  });
  return MmlMalignmark;
}(MmlNode_js_1.AbstractMmlNode);
exports.MmlMalignmark = MmlMalignmark;

/***/ },

/***/ 83900
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
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MmlMstyle = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var Attributes_js_1 = __webpack_require__(30147);
var MmlMstyle = function (_super) {
  __extends(MmlMstyle, _super);
  function MmlMstyle() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  Object.defineProperty(MmlMstyle.prototype, "kind", {
    get: function () {
      return 'mstyle';
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MmlMstyle.prototype, "notParent", {
    get: function () {
      return this.childNodes[0] && this.childNodes[0].childNodes.length === 1;
    },
    enumerable: false,
    configurable: true
  });
  MmlMstyle.prototype.setChildInheritedAttributes = function (attributes, display, level, prime) {
    var scriptlevel = this.attributes.getExplicit('scriptlevel');
    if (scriptlevel != null) {
      scriptlevel = scriptlevel.toString();
      if (scriptlevel.match(/^\s*[-+]/)) {
        level += parseInt(scriptlevel);
      } else {
        level = parseInt(scriptlevel);
      }
      prime = false;
    }
    var displaystyle = this.attributes.getExplicit('displaystyle');
    if (displaystyle != null) {
      display = displaystyle === true;
      prime = false;
    }
    var cramped = this.attributes.getExplicit('data-cramped');
    if (cramped != null) {
      prime = cramped;
    }
    attributes = this.addInheritedAttributes(attributes, this.attributes.getAllAttributes());
    this.childNodes[0].setInheritedAttributes(attributes, display, level, prime);
  };
  MmlMstyle.defaults = __assign(__assign({}, MmlNode_js_1.AbstractMmlLayoutNode.defaults), {
    scriptlevel: Attributes_js_1.INHERIT,
    displaystyle: Attributes_js_1.INHERIT,
    scriptsizemultiplier: 1 / Math.sqrt(2),
    scriptminsize: '8px',
    mathbackground: Attributes_js_1.INHERIT,
    mathcolor: Attributes_js_1.INHERIT,
    dir: Attributes_js_1.INHERIT,
    infixlinebreakstyle: 'before'
  });
  return MmlMstyle;
}(MmlNode_js_1.AbstractMmlLayoutNode);
exports.MmlMstyle = MmlMstyle;

/***/ },

/***/ 86178
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
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MmlMaligngroup = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var Attributes_js_1 = __webpack_require__(30147);
var MmlMaligngroup = function (_super) {
  __extends(MmlMaligngroup, _super);
  function MmlMaligngroup() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  Object.defineProperty(MmlMaligngroup.prototype, "kind", {
    get: function () {
      return 'maligngroup';
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MmlMaligngroup.prototype, "isSpacelike", {
    get: function () {
      return true;
    },
    enumerable: false,
    configurable: true
  });
  MmlMaligngroup.prototype.setChildInheritedAttributes = function (attributes, display, level, prime) {
    attributes = this.addInheritedAttributes(attributes, this.attributes.getAllAttributes());
    _super.prototype.setChildInheritedAttributes.call(this, attributes, display, level, prime);
  };
  MmlMaligngroup.defaults = __assign(__assign({}, MmlNode_js_1.AbstractMmlLayoutNode.defaults), {
    groupalign: Attributes_js_1.INHERIT
  });
  return MmlMaligngroup;
}(MmlNode_js_1.AbstractMmlLayoutNode);
exports.MmlMaligngroup = MmlMaligngroup;

/***/ },

/***/ 99505
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
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.MathChoice = void 0;
var MmlNode_js_1 = __webpack_require__(90698);
var MathChoice = function (_super) {
  __extends(MathChoice, _super);
  function MathChoice() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  Object.defineProperty(MathChoice.prototype, "kind", {
    get: function () {
      return 'MathChoice';
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MathChoice.prototype, "arity", {
    get: function () {
      return 4;
    },
    enumerable: false,
    configurable: true
  });
  Object.defineProperty(MathChoice.prototype, "notParent", {
    get: function () {
      return true;
    },
    enumerable: false,
    configurable: true
  });
  MathChoice.prototype.setInheritedAttributes = function (attributes, display, level, prime) {
    var selection = display ? 0 : Math.max(0, Math.min(level, 2)) + 1;
    var child = this.childNodes[selection] || this.factory.create('mrow');
    this.parent.replaceChild(child, this);
    child.setInheritedAttributes(attributes, display, level, prime);
  };
  MathChoice.defaults = __assign({}, MmlNode_js_1.AbstractMmlBaseNode.defaults);
  return MathChoice;
}(MmlNode_js_1.AbstractMmlBaseNode);
exports.MathChoice = MathChoice;

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzk2Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUNwRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQzNDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDM0NBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQ3RDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQ3REQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUNwRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDNUZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDbEVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NbWxUcmVlL01tbE5vZGVzL21lcnJvci5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL01tbFRyZWUvTW1sRmFjdG9yeS5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL1RyZWUvTm9kZUZhY3RvcnkuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NbWxUcmVlL01NTC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL01tbFRyZWUvTW1sTm9kZXMvbXBoYW50b20uanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NbWxUcmVlL01tbE5vZGVzL21hbGlnbm1hcmsuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NbWxUcmVlL01tbE5vZGVzL21zdHlsZS5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL01tbFRyZWUvTW1sTm9kZXMvbWFsaWduZ3JvdXAuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NbWxUcmVlL01tbE5vZGVzL21hdGhjaG9pY2UuanMiXSwic291cmNlc0NvbnRlbnQiOlsiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xudmFyIF9fYXNzaWduID0gdGhpcyAmJiB0aGlzLl9fYXNzaWduIHx8IGZ1bmN0aW9uICgpIHtcbiAgX19hc3NpZ24gPSBPYmplY3QuYXNzaWduIHx8IGZ1bmN0aW9uICh0KSB7XG4gICAgZm9yICh2YXIgcywgaSA9IDEsIG4gPSBhcmd1bWVudHMubGVuZ3RoOyBpIDwgbjsgaSsrKSB7XG4gICAgICBzID0gYXJndW1lbnRzW2ldO1xuICAgICAgZm9yICh2YXIgcCBpbiBzKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKHMsIHApKSB0W3BdID0gc1twXTtcbiAgICB9XG4gICAgcmV0dXJuIHQ7XG4gIH07XG4gIHJldHVybiBfX2Fzc2lnbi5hcHBseSh0aGlzLCBhcmd1bWVudHMpO1xufTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLk1tbE1lcnJvciA9IHZvaWQgMDtcbnZhciBNbWxOb2RlX2pzXzEgPSByZXF1aXJlKFwiLi4vTW1sTm9kZS5qc1wiKTtcbnZhciBNbWxNZXJyb3IgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhNbWxNZXJyb3IsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIE1tbE1lcnJvcigpIHtcbiAgICB2YXIgX3RoaXMgPSBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgICBfdGhpcy50ZXhjbGFzcyA9IE1tbE5vZGVfanNfMS5URVhDTEFTUy5PUkQ7XG4gICAgcmV0dXJuIF90aGlzO1xuICB9XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShNbWxNZXJyb3IucHJvdG90eXBlLCBcImtpbmRcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuICdtZXJyb3InO1xuICAgIH0sXG4gICAgZW51bWVyYWJsZTogZmFsc2UsXG4gICAgY29uZmlndXJhYmxlOiB0cnVlXG4gIH0pO1xuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sTWVycm9yLnByb3RvdHlwZSwgXCJhcml0eVwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gLTE7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShNbWxNZXJyb3IucHJvdG90eXBlLCBcImxpbmVicmVha0NvbnRhaW5lclwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gdHJ1ZTtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgTW1sTWVycm9yLmRlZmF1bHRzID0gX19hc3NpZ24oe30sIE1tbE5vZGVfanNfMS5BYnN0cmFjdE1tbE5vZGUuZGVmYXVsdHMpO1xuICByZXR1cm4gTW1sTWVycm9yO1xufShNbWxOb2RlX2pzXzEuQWJzdHJhY3RNbWxOb2RlKTtcbmV4cG9ydHMuTW1sTWVycm9yID0gTW1sTWVycm9yOyIsIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX19leHRlbmRzID0gdGhpcyAmJiB0aGlzLl9fZXh0ZW5kcyB8fCBmdW5jdGlvbiAoKSB7XG4gIHZhciBleHRlbmRTdGF0aWNzID0gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBleHRlbmRTdGF0aWNzID0gT2JqZWN0LnNldFByb3RvdHlwZU9mIHx8IHtcbiAgICAgIF9fcHJvdG9fXzogW11cbiAgICB9IGluc3RhbmNlb2YgQXJyYXkgJiYgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGQuX19wcm90b19fID0gYjtcbiAgICB9IHx8IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBmb3IgKHZhciBwIGluIGIpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwoYiwgcCkpIGRbcF0gPSBiW3BdO1xuICAgIH07XG4gICAgcmV0dXJuIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gIH07XG4gIHJldHVybiBmdW5jdGlvbiAoZCwgYikge1xuICAgIGlmICh0eXBlb2YgYiAhPT0gXCJmdW5jdGlvblwiICYmIGIgIT09IG51bGwpIHRocm93IG5ldyBUeXBlRXJyb3IoXCJDbGFzcyBleHRlbmRzIHZhbHVlIFwiICsgU3RyaW5nKGIpICsgXCIgaXMgbm90IGEgY29uc3RydWN0b3Igb3IgbnVsbFwiKTtcbiAgICBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICAgIGZ1bmN0aW9uIF9fKCkge1xuICAgICAgdGhpcy5jb25zdHJ1Y3RvciA9IGQ7XG4gICAgfVxuICAgIGQucHJvdG90eXBlID0gYiA9PT0gbnVsbCA/IE9iamVjdC5jcmVhdGUoYikgOiAoX18ucHJvdG90eXBlID0gYi5wcm90b3R5cGUsIG5ldyBfXygpKTtcbiAgfTtcbn0oKTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLk1tbEZhY3RvcnkgPSB2b2lkIDA7XG52YXIgTm9kZUZhY3RvcnlfanNfMSA9IHJlcXVpcmUoXCIuLi9UcmVlL05vZGVGYWN0b3J5LmpzXCIpO1xudmFyIE1NTF9qc18xID0gcmVxdWlyZShcIi4vTU1MLmpzXCIpO1xudmFyIE1tbEZhY3RvcnkgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhNbWxGYWN0b3J5LCBfc3VwZXIpO1xuICBmdW5jdGlvbiBNbWxGYWN0b3J5KCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sRmFjdG9yeS5wcm90b3R5cGUsIFwiTU1MXCIsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB0aGlzLm5vZGU7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE1tbEZhY3RvcnkuZGVmYXVsdE5vZGVzID0gTU1MX2pzXzEuTU1MO1xuICByZXR1cm4gTW1sRmFjdG9yeTtcbn0oTm9kZUZhY3RvcnlfanNfMS5BYnN0cmFjdE5vZGVGYWN0b3J5KTtcbmV4cG9ydHMuTW1sRmFjdG9yeSA9IE1tbEZhY3Rvcnk7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuQWJzdHJhY3ROb2RlRmFjdG9yeSA9IHZvaWQgMDtcbnZhciBGYWN0b3J5X2pzXzEgPSByZXF1aXJlKFwiLi9GYWN0b3J5LmpzXCIpO1xudmFyIEFic3RyYWN0Tm9kZUZhY3RvcnkgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhBYnN0cmFjdE5vZGVGYWN0b3J5LCBfc3VwZXIpO1xuICBmdW5jdGlvbiBBYnN0cmFjdE5vZGVGYWN0b3J5KCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBBYnN0cmFjdE5vZGVGYWN0b3J5LnByb3RvdHlwZS5jcmVhdGUgPSBmdW5jdGlvbiAoa2luZCwgcHJvcGVydGllcywgY2hpbGRyZW4pIHtcbiAgICBpZiAocHJvcGVydGllcyA9PT0gdm9pZCAwKSB7XG4gICAgICBwcm9wZXJ0aWVzID0ge307XG4gICAgfVxuICAgIGlmIChjaGlsZHJlbiA9PT0gdm9pZCAwKSB7XG4gICAgICBjaGlsZHJlbiA9IFtdO1xuICAgIH1cbiAgICByZXR1cm4gdGhpcy5ub2RlW2tpbmRdKHByb3BlcnRpZXMsIGNoaWxkcmVuKTtcbiAgfTtcbiAgcmV0dXJuIEFic3RyYWN0Tm9kZUZhY3Rvcnk7XG59KEZhY3RvcnlfanNfMS5BYnN0cmFjdEZhY3RvcnkpO1xuZXhwb3J0cy5BYnN0cmFjdE5vZGVGYWN0b3J5ID0gQWJzdHJhY3ROb2RlRmFjdG9yeTsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9hO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuTU1MID0gdm9pZCAwO1xudmFyIE1tbE5vZGVfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGUuanNcIik7XG52YXIgbWF0aF9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWF0aC5qc1wiKTtcbnZhciBtaV9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWkuanNcIik7XG52YXIgbW5fanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL21uLmpzXCIpO1xudmFyIG1vX2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9tby5qc1wiKTtcbnZhciBtdGV4dF9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbXRleHQuanNcIik7XG52YXIgbXNwYWNlX2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9tc3BhY2UuanNcIik7XG52YXIgbXNfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL21zLmpzXCIpO1xudmFyIG1yb3dfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL21yb3cuanNcIik7XG52YXIgbWZyYWNfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL21mcmFjLmpzXCIpO1xudmFyIG1zcXJ0X2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9tc3FydC5qc1wiKTtcbnZhciBtcm9vdF9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbXJvb3QuanNcIik7XG52YXIgbXN0eWxlX2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9tc3R5bGUuanNcIik7XG52YXIgbWVycm9yX2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9tZXJyb3IuanNcIik7XG52YXIgbXBhZGRlZF9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbXBhZGRlZC5qc1wiKTtcbnZhciBtcGhhbnRvbV9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbXBoYW50b20uanNcIik7XG52YXIgbWZlbmNlZF9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWZlbmNlZC5qc1wiKTtcbnZhciBtZW5jbG9zZV9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWVuY2xvc2UuanNcIik7XG52YXIgbWFjdGlvbl9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWFjdGlvbi5qc1wiKTtcbnZhciBtc3Vic3VwX2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9tc3Vic3VwLmpzXCIpO1xudmFyIG11bmRlcm92ZXJfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL211bmRlcm92ZXIuanNcIik7XG52YXIgbW11bHRpc2NyaXB0c19qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbW11bHRpc2NyaXB0cy5qc1wiKTtcbnZhciBtdGFibGVfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL210YWJsZS5qc1wiKTtcbnZhciBtdHJfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL210ci5qc1wiKTtcbnZhciBtdGRfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL210ZC5qc1wiKTtcbnZhciBtYWxpZ25ncm91cF9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWFsaWduZ3JvdXAuanNcIik7XG52YXIgbWFsaWdubWFya19qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWFsaWdubWFyay5qc1wiKTtcbnZhciBtZ2x5cGhfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL21nbHlwaC5qc1wiKTtcbnZhciBzZW1hbnRpY3NfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL3NlbWFudGljcy5qc1wiKTtcbnZhciBUZVhBdG9tX2pzXzEgPSByZXF1aXJlKFwiLi9NbWxOb2Rlcy9UZVhBdG9tLmpzXCIpO1xudmFyIG1hdGhjaG9pY2VfanNfMSA9IHJlcXVpcmUoXCIuL01tbE5vZGVzL21hdGhjaG9pY2UuanNcIik7XG5leHBvcnRzLk1NTCA9IChfYSA9IHt9LCBfYVttYXRoX2pzXzEuTW1sTWF0aC5wcm90b3R5cGUua2luZF0gPSBtYXRoX2pzXzEuTW1sTWF0aCwgX2FbbWlfanNfMS5NbWxNaS5wcm90b3R5cGUua2luZF0gPSBtaV9qc18xLk1tbE1pLCBfYVttbl9qc18xLk1tbE1uLnByb3RvdHlwZS5raW5kXSA9IG1uX2pzXzEuTW1sTW4sIF9hW21vX2pzXzEuTW1sTW8ucHJvdG90eXBlLmtpbmRdID0gbW9fanNfMS5NbWxNbywgX2FbbXRleHRfanNfMS5NbWxNdGV4dC5wcm90b3R5cGUua2luZF0gPSBtdGV4dF9qc18xLk1tbE10ZXh0LCBfYVttc3BhY2VfanNfMS5NbWxNc3BhY2UucHJvdG90eXBlLmtpbmRdID0gbXNwYWNlX2pzXzEuTW1sTXNwYWNlLCBfYVttc19qc18xLk1tbE1zLnByb3RvdHlwZS5raW5kXSA9IG1zX2pzXzEuTW1sTXMsIF9hW21yb3dfanNfMS5NbWxNcm93LnByb3RvdHlwZS5raW5kXSA9IG1yb3dfanNfMS5NbWxNcm93LCBfYVttcm93X2pzXzEuTW1sSW5mZXJyZWRNcm93LnByb3RvdHlwZS5raW5kXSA9IG1yb3dfanNfMS5NbWxJbmZlcnJlZE1yb3csIF9hW21mcmFjX2pzXzEuTW1sTWZyYWMucHJvdG90eXBlLmtpbmRdID0gbWZyYWNfanNfMS5NbWxNZnJhYywgX2FbbXNxcnRfanNfMS5NbWxNc3FydC5wcm90b3R5cGUua2luZF0gPSBtc3FydF9qc18xLk1tbE1zcXJ0LCBfYVttcm9vdF9qc18xLk1tbE1yb290LnByb3RvdHlwZS5raW5kXSA9IG1yb290X2pzXzEuTW1sTXJvb3QsIF9hW21zdHlsZV9qc18xLk1tbE1zdHlsZS5wcm90b3R5cGUua2luZF0gPSBtc3R5bGVfanNfMS5NbWxNc3R5bGUsIF9hW21lcnJvcl9qc18xLk1tbE1lcnJvci5wcm90b3R5cGUua2luZF0gPSBtZXJyb3JfanNfMS5NbWxNZXJyb3IsIF9hW21wYWRkZWRfanNfMS5NbWxNcGFkZGVkLnByb3RvdHlwZS5raW5kXSA9IG1wYWRkZWRfanNfMS5NbWxNcGFkZGVkLCBfYVttcGhhbnRvbV9qc18xLk1tbE1waGFudG9tLnByb3RvdHlwZS5raW5kXSA9IG1waGFudG9tX2pzXzEuTW1sTXBoYW50b20sIF9hW21mZW5jZWRfanNfMS5NbWxNZmVuY2VkLnByb3RvdHlwZS5raW5kXSA9IG1mZW5jZWRfanNfMS5NbWxNZmVuY2VkLCBfYVttZW5jbG9zZV9qc18xLk1tbE1lbmNsb3NlLnByb3RvdHlwZS5raW5kXSA9IG1lbmNsb3NlX2pzXzEuTW1sTWVuY2xvc2UsIF9hW21hY3Rpb25fanNfMS5NbWxNYWN0aW9uLnByb3RvdHlwZS5raW5kXSA9IG1hY3Rpb25fanNfMS5NbWxNYWN0aW9uLCBfYVttc3Vic3VwX2pzXzEuTW1sTXN1Yi5wcm90b3R5cGUua2luZF0gPSBtc3Vic3VwX2pzXzEuTW1sTXN1YiwgX2FbbXN1YnN1cF9qc18xLk1tbE1zdXAucHJvdG90eXBlLmtpbmRdID0gbXN1YnN1cF9qc18xLk1tbE1zdXAsIF9hW21zdWJzdXBfanNfMS5NbWxNc3Vic3VwLnByb3RvdHlwZS5raW5kXSA9IG1zdWJzdXBfanNfMS5NbWxNc3Vic3VwLCBfYVttdW5kZXJvdmVyX2pzXzEuTW1sTXVuZGVyLnByb3RvdHlwZS5raW5kXSA9IG11bmRlcm92ZXJfanNfMS5NbWxNdW5kZXIsIF9hW211bmRlcm92ZXJfanNfMS5NbWxNb3Zlci5wcm90b3R5cGUua2luZF0gPSBtdW5kZXJvdmVyX2pzXzEuTW1sTW92ZXIsIF9hW211bmRlcm92ZXJfanNfMS5NbWxNdW5kZXJvdmVyLnByb3RvdHlwZS5raW5kXSA9IG11bmRlcm92ZXJfanNfMS5NbWxNdW5kZXJvdmVyLCBfYVttbXVsdGlzY3JpcHRzX2pzXzEuTW1sTW11bHRpc2NyaXB0cy5wcm90b3R5cGUua2luZF0gPSBtbXVsdGlzY3JpcHRzX2pzXzEuTW1sTW11bHRpc2NyaXB0cywgX2FbbW11bHRpc2NyaXB0c19qc18xLk1tbE1wcmVzY3JpcHRzLnByb3RvdHlwZS5raW5kXSA9IG1tdWx0aXNjcmlwdHNfanNfMS5NbWxNcHJlc2NyaXB0cywgX2FbbW11bHRpc2NyaXB0c19qc18xLk1tbE5vbmUucHJvdG90eXBlLmtpbmRdID0gbW11bHRpc2NyaXB0c19qc18xLk1tbE5vbmUsIF9hW210YWJsZV9qc18xLk1tbE10YWJsZS5wcm90b3R5cGUua2luZF0gPSBtdGFibGVfanNfMS5NbWxNdGFibGUsIF9hW210cl9qc18xLk1tbE1sYWJlbGVkdHIucHJvdG90eXBlLmtpbmRdID0gbXRyX2pzXzEuTW1sTWxhYmVsZWR0ciwgX2FbbXRyX2pzXzEuTW1sTXRyLnByb3RvdHlwZS5raW5kXSA9IG10cl9qc18xLk1tbE10ciwgX2FbbXRkX2pzXzEuTW1sTXRkLnByb3RvdHlwZS5raW5kXSA9IG10ZF9qc18xLk1tbE10ZCwgX2FbbWFsaWduZ3JvdXBfanNfMS5NbWxNYWxpZ25ncm91cC5wcm90b3R5cGUua2luZF0gPSBtYWxpZ25ncm91cF9qc18xLk1tbE1hbGlnbmdyb3VwLCBfYVttYWxpZ25tYXJrX2pzXzEuTW1sTWFsaWdubWFyay5wcm90b3R5cGUua2luZF0gPSBtYWxpZ25tYXJrX2pzXzEuTW1sTWFsaWdubWFyaywgX2FbbWdseXBoX2pzXzEuTW1sTWdseXBoLnByb3RvdHlwZS5raW5kXSA9IG1nbHlwaF9qc18xLk1tbE1nbHlwaCwgX2Fbc2VtYW50aWNzX2pzXzEuTW1sU2VtYW50aWNzLnByb3RvdHlwZS5raW5kXSA9IHNlbWFudGljc19qc18xLk1tbFNlbWFudGljcywgX2Fbc2VtYW50aWNzX2pzXzEuTW1sQW5ub3RhdGlvbi5wcm90b3R5cGUua2luZF0gPSBzZW1hbnRpY3NfanNfMS5NbWxBbm5vdGF0aW9uLCBfYVtzZW1hbnRpY3NfanNfMS5NbWxBbm5vdGF0aW9uWE1MLnByb3RvdHlwZS5raW5kXSA9IHNlbWFudGljc19qc18xLk1tbEFubm90YXRpb25YTUwsIF9hW1RlWEF0b21fanNfMS5UZVhBdG9tLnByb3RvdHlwZS5raW5kXSA9IFRlWEF0b21fanNfMS5UZVhBdG9tLCBfYVttYXRoY2hvaWNlX2pzXzEuTWF0aENob2ljZS5wcm90b3R5cGUua2luZF0gPSBtYXRoY2hvaWNlX2pzXzEuTWF0aENob2ljZSwgX2FbTW1sTm9kZV9qc18xLlRleHROb2RlLnByb3RvdHlwZS5raW5kXSA9IE1tbE5vZGVfanNfMS5UZXh0Tm9kZSwgX2FbTW1sTm9kZV9qc18xLlhNTE5vZGUucHJvdG90eXBlLmtpbmRdID0gTW1sTm9kZV9qc18xLlhNTE5vZGUsIF9hKTsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG52YXIgX19hc3NpZ24gPSB0aGlzICYmIHRoaXMuX19hc3NpZ24gfHwgZnVuY3Rpb24gKCkge1xuICBfX2Fzc2lnbiA9IE9iamVjdC5hc3NpZ24gfHwgZnVuY3Rpb24gKHQpIHtcbiAgICBmb3IgKHZhciBzLCBpID0gMSwgbiA9IGFyZ3VtZW50cy5sZW5ndGg7IGkgPCBuOyBpKyspIHtcbiAgICAgIHMgPSBhcmd1bWVudHNbaV07XG4gICAgICBmb3IgKHZhciBwIGluIHMpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwocywgcCkpIHRbcF0gPSBzW3BdO1xuICAgIH1cbiAgICByZXR1cm4gdDtcbiAgfTtcbiAgcmV0dXJuIF9fYXNzaWduLmFwcGx5KHRoaXMsIGFyZ3VtZW50cyk7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuTW1sTXBoYW50b20gPSB2b2lkIDA7XG52YXIgTW1sTm9kZV9qc18xID0gcmVxdWlyZShcIi4uL01tbE5vZGUuanNcIik7XG52YXIgTW1sTXBoYW50b20gPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhNbWxNcGhhbnRvbSwgX3N1cGVyKTtcbiAgZnVuY3Rpb24gTW1sTXBoYW50b20oKSB7XG4gICAgdmFyIF90aGlzID0gX3N1cGVyICE9PSBudWxsICYmIF9zdXBlci5hcHBseSh0aGlzLCBhcmd1bWVudHMpIHx8IHRoaXM7XG4gICAgX3RoaXMudGV4Y2xhc3MgPSBNbWxOb2RlX2pzXzEuVEVYQ0xBU1MuT1JEO1xuICAgIHJldHVybiBfdGhpcztcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sTXBoYW50b20ucHJvdG90eXBlLCBcImtpbmRcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuICdtcGhhbnRvbSc7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE1tbE1waGFudG9tLmRlZmF1bHRzID0gX19hc3NpZ24oe30sIE1tbE5vZGVfanNfMS5BYnN0cmFjdE1tbExheW91dE5vZGUuZGVmYXVsdHMpO1xuICByZXR1cm4gTW1sTXBoYW50b207XG59KE1tbE5vZGVfanNfMS5BYnN0cmFjdE1tbExheW91dE5vZGUpO1xuZXhwb3J0cy5NbWxNcGhhbnRvbSA9IE1tbE1waGFudG9tOyIsIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX19leHRlbmRzID0gdGhpcyAmJiB0aGlzLl9fZXh0ZW5kcyB8fCBmdW5jdGlvbiAoKSB7XG4gIHZhciBleHRlbmRTdGF0aWNzID0gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBleHRlbmRTdGF0aWNzID0gT2JqZWN0LnNldFByb3RvdHlwZU9mIHx8IHtcbiAgICAgIF9fcHJvdG9fXzogW11cbiAgICB9IGluc3RhbmNlb2YgQXJyYXkgJiYgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGQuX19wcm90b19fID0gYjtcbiAgICB9IHx8IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBmb3IgKHZhciBwIGluIGIpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwoYiwgcCkpIGRbcF0gPSBiW3BdO1xuICAgIH07XG4gICAgcmV0dXJuIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gIH07XG4gIHJldHVybiBmdW5jdGlvbiAoZCwgYikge1xuICAgIGlmICh0eXBlb2YgYiAhPT0gXCJmdW5jdGlvblwiICYmIGIgIT09IG51bGwpIHRocm93IG5ldyBUeXBlRXJyb3IoXCJDbGFzcyBleHRlbmRzIHZhbHVlIFwiICsgU3RyaW5nKGIpICsgXCIgaXMgbm90IGEgY29uc3RydWN0b3Igb3IgbnVsbFwiKTtcbiAgICBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICAgIGZ1bmN0aW9uIF9fKCkge1xuICAgICAgdGhpcy5jb25zdHJ1Y3RvciA9IGQ7XG4gICAgfVxuICAgIGQucHJvdG90eXBlID0gYiA9PT0gbnVsbCA/IE9iamVjdC5jcmVhdGUoYikgOiAoX18ucHJvdG90eXBlID0gYi5wcm90b3R5cGUsIG5ldyBfXygpKTtcbiAgfTtcbn0oKTtcbnZhciBfX2Fzc2lnbiA9IHRoaXMgJiYgdGhpcy5fX2Fzc2lnbiB8fCBmdW5jdGlvbiAoKSB7XG4gIF9fYXNzaWduID0gT2JqZWN0LmFzc2lnbiB8fCBmdW5jdGlvbiAodCkge1xuICAgIGZvciAodmFyIHMsIGkgPSAxLCBuID0gYXJndW1lbnRzLmxlbmd0aDsgaSA8IG47IGkrKykge1xuICAgICAgcyA9IGFyZ3VtZW50c1tpXTtcbiAgICAgIGZvciAodmFyIHAgaW4gcykgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChzLCBwKSkgdFtwXSA9IHNbcF07XG4gICAgfVxuICAgIHJldHVybiB0O1xuICB9O1xuICByZXR1cm4gX19hc3NpZ24uYXBwbHkodGhpcywgYXJndW1lbnRzKTtcbn07XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5NbWxNYWxpZ25tYXJrID0gdm9pZCAwO1xudmFyIE1tbE5vZGVfanNfMSA9IHJlcXVpcmUoXCIuLi9NbWxOb2RlLmpzXCIpO1xudmFyIE1tbE1hbGlnbm1hcmsgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhNbWxNYWxpZ25tYXJrLCBfc3VwZXIpO1xuICBmdW5jdGlvbiBNbWxNYWxpZ25tYXJrKCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sTWFsaWdubWFyay5wcm90b3R5cGUsIFwia2luZFwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gJ21hbGlnbm1hcmsnO1xuICAgIH0sXG4gICAgZW51bWVyYWJsZTogZmFsc2UsXG4gICAgY29uZmlndXJhYmxlOiB0cnVlXG4gIH0pO1xuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sTWFsaWdubWFyay5wcm90b3R5cGUsIFwiYXJpdHlcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIDA7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShNbWxNYWxpZ25tYXJrLnByb3RvdHlwZSwgXCJpc1NwYWNlbGlrZVwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gdHJ1ZTtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgTW1sTWFsaWdubWFyay5kZWZhdWx0cyA9IF9fYXNzaWduKF9fYXNzaWduKHt9LCBNbWxOb2RlX2pzXzEuQWJzdHJhY3RNbWxOb2RlLmRlZmF1bHRzKSwge1xuICAgIGVkZ2U6ICdsZWZ0J1xuICB9KTtcbiAgcmV0dXJuIE1tbE1hbGlnbm1hcms7XG59KE1tbE5vZGVfanNfMS5BYnN0cmFjdE1tbE5vZGUpO1xuZXhwb3J0cy5NbWxNYWxpZ25tYXJrID0gTW1sTWFsaWdubWFyazsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG52YXIgX19hc3NpZ24gPSB0aGlzICYmIHRoaXMuX19hc3NpZ24gfHwgZnVuY3Rpb24gKCkge1xuICBfX2Fzc2lnbiA9IE9iamVjdC5hc3NpZ24gfHwgZnVuY3Rpb24gKHQpIHtcbiAgICBmb3IgKHZhciBzLCBpID0gMSwgbiA9IGFyZ3VtZW50cy5sZW5ndGg7IGkgPCBuOyBpKyspIHtcbiAgICAgIHMgPSBhcmd1bWVudHNbaV07XG4gICAgICBmb3IgKHZhciBwIGluIHMpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwocywgcCkpIHRbcF0gPSBzW3BdO1xuICAgIH1cbiAgICByZXR1cm4gdDtcbiAgfTtcbiAgcmV0dXJuIF9fYXNzaWduLmFwcGx5KHRoaXMsIGFyZ3VtZW50cyk7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuTW1sTXN0eWxlID0gdm9pZCAwO1xudmFyIE1tbE5vZGVfanNfMSA9IHJlcXVpcmUoXCIuLi9NbWxOb2RlLmpzXCIpO1xudmFyIEF0dHJpYnV0ZXNfanNfMSA9IHJlcXVpcmUoXCIuLi9BdHRyaWJ1dGVzLmpzXCIpO1xudmFyIE1tbE1zdHlsZSA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKE1tbE1zdHlsZSwgX3N1cGVyKTtcbiAgZnVuY3Rpb24gTW1sTXN0eWxlKCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sTXN0eWxlLnByb3RvdHlwZSwgXCJraW5kXCIsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiAnbXN0eWxlJztcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgT2JqZWN0LmRlZmluZVByb3BlcnR5KE1tbE1zdHlsZS5wcm90b3R5cGUsIFwibm90UGFyZW50XCIsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB0aGlzLmNoaWxkTm9kZXNbMF0gJiYgdGhpcy5jaGlsZE5vZGVzWzBdLmNoaWxkTm9kZXMubGVuZ3RoID09PSAxO1xuICAgIH0sXG4gICAgZW51bWVyYWJsZTogZmFsc2UsXG4gICAgY29uZmlndXJhYmxlOiB0cnVlXG4gIH0pO1xuICBNbWxNc3R5bGUucHJvdG90eXBlLnNldENoaWxkSW5oZXJpdGVkQXR0cmlidXRlcyA9IGZ1bmN0aW9uIChhdHRyaWJ1dGVzLCBkaXNwbGF5LCBsZXZlbCwgcHJpbWUpIHtcbiAgICB2YXIgc2NyaXB0bGV2ZWwgPSB0aGlzLmF0dHJpYnV0ZXMuZ2V0RXhwbGljaXQoJ3NjcmlwdGxldmVsJyk7XG4gICAgaWYgKHNjcmlwdGxldmVsICE9IG51bGwpIHtcbiAgICAgIHNjcmlwdGxldmVsID0gc2NyaXB0bGV2ZWwudG9TdHJpbmcoKTtcbiAgICAgIGlmIChzY3JpcHRsZXZlbC5tYXRjaCgvXlxccypbLStdLykpIHtcbiAgICAgICAgbGV2ZWwgKz0gcGFyc2VJbnQoc2NyaXB0bGV2ZWwpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgbGV2ZWwgPSBwYXJzZUludChzY3JpcHRsZXZlbCk7XG4gICAgICB9XG4gICAgICBwcmltZSA9IGZhbHNlO1xuICAgIH1cbiAgICB2YXIgZGlzcGxheXN0eWxlID0gdGhpcy5hdHRyaWJ1dGVzLmdldEV4cGxpY2l0KCdkaXNwbGF5c3R5bGUnKTtcbiAgICBpZiAoZGlzcGxheXN0eWxlICE9IG51bGwpIHtcbiAgICAgIGRpc3BsYXkgPSBkaXNwbGF5c3R5bGUgPT09IHRydWU7XG4gICAgICBwcmltZSA9IGZhbHNlO1xuICAgIH1cbiAgICB2YXIgY3JhbXBlZCA9IHRoaXMuYXR0cmlidXRlcy5nZXRFeHBsaWNpdCgnZGF0YS1jcmFtcGVkJyk7XG4gICAgaWYgKGNyYW1wZWQgIT0gbnVsbCkge1xuICAgICAgcHJpbWUgPSBjcmFtcGVkO1xuICAgIH1cbiAgICBhdHRyaWJ1dGVzID0gdGhpcy5hZGRJbmhlcml0ZWRBdHRyaWJ1dGVzKGF0dHJpYnV0ZXMsIHRoaXMuYXR0cmlidXRlcy5nZXRBbGxBdHRyaWJ1dGVzKCkpO1xuICAgIHRoaXMuY2hpbGROb2Rlc1swXS5zZXRJbmhlcml0ZWRBdHRyaWJ1dGVzKGF0dHJpYnV0ZXMsIGRpc3BsYXksIGxldmVsLCBwcmltZSk7XG4gIH07XG4gIE1tbE1zdHlsZS5kZWZhdWx0cyA9IF9fYXNzaWduKF9fYXNzaWduKHt9LCBNbWxOb2RlX2pzXzEuQWJzdHJhY3RNbWxMYXlvdXROb2RlLmRlZmF1bHRzKSwge1xuICAgIHNjcmlwdGxldmVsOiBBdHRyaWJ1dGVzX2pzXzEuSU5IRVJJVCxcbiAgICBkaXNwbGF5c3R5bGU6IEF0dHJpYnV0ZXNfanNfMS5JTkhFUklULFxuICAgIHNjcmlwdHNpemVtdWx0aXBsaWVyOiAxIC8gTWF0aC5zcXJ0KDIpLFxuICAgIHNjcmlwdG1pbnNpemU6ICc4cHgnLFxuICAgIG1hdGhiYWNrZ3JvdW5kOiBBdHRyaWJ1dGVzX2pzXzEuSU5IRVJJVCxcbiAgICBtYXRoY29sb3I6IEF0dHJpYnV0ZXNfanNfMS5JTkhFUklULFxuICAgIGRpcjogQXR0cmlidXRlc19qc18xLklOSEVSSVQsXG4gICAgaW5maXhsaW5lYnJlYWtzdHlsZTogJ2JlZm9yZSdcbiAgfSk7XG4gIHJldHVybiBNbWxNc3R5bGU7XG59KE1tbE5vZGVfanNfMS5BYnN0cmFjdE1tbExheW91dE5vZGUpO1xuZXhwb3J0cy5NbWxNc3R5bGUgPSBNbWxNc3R5bGU7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xudmFyIF9fYXNzaWduID0gdGhpcyAmJiB0aGlzLl9fYXNzaWduIHx8IGZ1bmN0aW9uICgpIHtcbiAgX19hc3NpZ24gPSBPYmplY3QuYXNzaWduIHx8IGZ1bmN0aW9uICh0KSB7XG4gICAgZm9yICh2YXIgcywgaSA9IDEsIG4gPSBhcmd1bWVudHMubGVuZ3RoOyBpIDwgbjsgaSsrKSB7XG4gICAgICBzID0gYXJndW1lbnRzW2ldO1xuICAgICAgZm9yICh2YXIgcCBpbiBzKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKHMsIHApKSB0W3BdID0gc1twXTtcbiAgICB9XG4gICAgcmV0dXJuIHQ7XG4gIH07XG4gIHJldHVybiBfX2Fzc2lnbi5hcHBseSh0aGlzLCBhcmd1bWVudHMpO1xufTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLk1tbE1hbGlnbmdyb3VwID0gdm9pZCAwO1xudmFyIE1tbE5vZGVfanNfMSA9IHJlcXVpcmUoXCIuLi9NbWxOb2RlLmpzXCIpO1xudmFyIEF0dHJpYnV0ZXNfanNfMSA9IHJlcXVpcmUoXCIuLi9BdHRyaWJ1dGVzLmpzXCIpO1xudmFyIE1tbE1hbGlnbmdyb3VwID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoTW1sTWFsaWduZ3JvdXAsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIE1tbE1hbGlnbmdyb3VwKCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoTW1sTWFsaWduZ3JvdXAucHJvdG90eXBlLCBcImtpbmRcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuICdtYWxpZ25ncm91cCc7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShNbWxNYWxpZ25ncm91cC5wcm90b3R5cGUsIFwiaXNTcGFjZWxpa2VcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE1tbE1hbGlnbmdyb3VwLnByb3RvdHlwZS5zZXRDaGlsZEluaGVyaXRlZEF0dHJpYnV0ZXMgPSBmdW5jdGlvbiAoYXR0cmlidXRlcywgZGlzcGxheSwgbGV2ZWwsIHByaW1lKSB7XG4gICAgYXR0cmlidXRlcyA9IHRoaXMuYWRkSW5oZXJpdGVkQXR0cmlidXRlcyhhdHRyaWJ1dGVzLCB0aGlzLmF0dHJpYnV0ZXMuZ2V0QWxsQXR0cmlidXRlcygpKTtcbiAgICBfc3VwZXIucHJvdG90eXBlLnNldENoaWxkSW5oZXJpdGVkQXR0cmlidXRlcy5jYWxsKHRoaXMsIGF0dHJpYnV0ZXMsIGRpc3BsYXksIGxldmVsLCBwcmltZSk7XG4gIH07XG4gIE1tbE1hbGlnbmdyb3VwLmRlZmF1bHRzID0gX19hc3NpZ24oX19hc3NpZ24oe30sIE1tbE5vZGVfanNfMS5BYnN0cmFjdE1tbExheW91dE5vZGUuZGVmYXVsdHMpLCB7XG4gICAgZ3JvdXBhbGlnbjogQXR0cmlidXRlc19qc18xLklOSEVSSVRcbiAgfSk7XG4gIHJldHVybiBNbWxNYWxpZ25ncm91cDtcbn0oTW1sTm9kZV9qc18xLkFic3RyYWN0TW1sTGF5b3V0Tm9kZSk7XG5leHBvcnRzLk1tbE1hbGlnbmdyb3VwID0gTW1sTWFsaWduZ3JvdXA7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xudmFyIF9fYXNzaWduID0gdGhpcyAmJiB0aGlzLl9fYXNzaWduIHx8IGZ1bmN0aW9uICgpIHtcbiAgX19hc3NpZ24gPSBPYmplY3QuYXNzaWduIHx8IGZ1bmN0aW9uICh0KSB7XG4gICAgZm9yICh2YXIgcywgaSA9IDEsIG4gPSBhcmd1bWVudHMubGVuZ3RoOyBpIDwgbjsgaSsrKSB7XG4gICAgICBzID0gYXJndW1lbnRzW2ldO1xuICAgICAgZm9yICh2YXIgcCBpbiBzKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKHMsIHApKSB0W3BdID0gc1twXTtcbiAgICB9XG4gICAgcmV0dXJuIHQ7XG4gIH07XG4gIHJldHVybiBfX2Fzc2lnbi5hcHBseSh0aGlzLCBhcmd1bWVudHMpO1xufTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLk1hdGhDaG9pY2UgPSB2b2lkIDA7XG52YXIgTW1sTm9kZV9qc18xID0gcmVxdWlyZShcIi4uL01tbE5vZGUuanNcIik7XG52YXIgTWF0aENob2ljZSA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKE1hdGhDaG9pY2UsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIE1hdGhDaG9pY2UoKSB7XG4gICAgcmV0dXJuIF9zdXBlciAhPT0gbnVsbCAmJiBfc3VwZXIuYXBwbHkodGhpcywgYXJndW1lbnRzKSB8fCB0aGlzO1xuICB9XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShNYXRoQ2hvaWNlLnByb3RvdHlwZSwgXCJraW5kXCIsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiAnTWF0aENob2ljZSc7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShNYXRoQ2hvaWNlLnByb3RvdHlwZSwgXCJhcml0eVwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gNDtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgT2JqZWN0LmRlZmluZVByb3BlcnR5KE1hdGhDaG9pY2UucHJvdG90eXBlLCBcIm5vdFBhcmVudFwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gdHJ1ZTtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgTWF0aENob2ljZS5wcm90b3R5cGUuc2V0SW5oZXJpdGVkQXR0cmlidXRlcyA9IGZ1bmN0aW9uIChhdHRyaWJ1dGVzLCBkaXNwbGF5LCBsZXZlbCwgcHJpbWUpIHtcbiAgICB2YXIgc2VsZWN0aW9uID0gZGlzcGxheSA/IDAgOiBNYXRoLm1heCgwLCBNYXRoLm1pbihsZXZlbCwgMikpICsgMTtcbiAgICB2YXIgY2hpbGQgPSB0aGlzLmNoaWxkTm9kZXNbc2VsZWN0aW9uXSB8fCB0aGlzLmZhY3RvcnkuY3JlYXRlKCdtcm93Jyk7XG4gICAgdGhpcy5wYXJlbnQucmVwbGFjZUNoaWxkKGNoaWxkLCB0aGlzKTtcbiAgICBjaGlsZC5zZXRJbmhlcml0ZWRBdHRyaWJ1dGVzKGF0dHJpYnV0ZXMsIGRpc3BsYXksIGxldmVsLCBwcmltZSk7XG4gIH07XG4gIE1hdGhDaG9pY2UuZGVmYXVsdHMgPSBfX2Fzc2lnbih7fSwgTW1sTm9kZV9qc18xLkFic3RyYWN0TW1sQmFzZU5vZGUuZGVmYXVsdHMpO1xuICByZXR1cm4gTWF0aENob2ljZTtcbn0oTW1sTm9kZV9qc18xLkFic3RyYWN0TW1sQmFzZU5vZGUpO1xuZXhwb3J0cy5NYXRoQ2hvaWNlID0gTWF0aENob2ljZTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9