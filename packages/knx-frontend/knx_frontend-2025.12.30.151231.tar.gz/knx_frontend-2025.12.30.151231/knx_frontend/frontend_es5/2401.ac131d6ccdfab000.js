"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2401"],{39623:function(e,t,r){r.a(e,(async function(e,a){try{r.r(t),r.d(t,{HaLabelSelector:function(){return g}});var n=r(44734),i=r(56038),o=r(69683),s=r(6454),l=(r(28706),r(62826)),d=r(96196),u=r(77845),c=r(55376),h=r(92542),v=r(32649),p=e([v]);v=(p.then?(await p)():p)[0];var b,f,y,_=e=>e,g=function(e){function t(){var e;(0,n.A)(this,t);for(var r=arguments.length,a=new Array(r),i=0;i<r;i++)a[i]=arguments[i];return(e=(0,o.A)(this,t,[].concat(a))).disabled=!1,e.required=!0,e}return(0,s.A)(t,e),(0,i.A)(t,[{key:"render",value:function(){var e;return this.selector.label.multiple?(0,d.qy)(b||(b=_`
        <ha-labels-picker
          no-add
          .hass=${0}
          .value=${0}
          .required=${0}
          .disabled=${0}
          .label=${0}
          @value-changed=${0}
        >
        </ha-labels-picker>
      `),this.hass,(0,c.e)(null!==(e=this.value)&&void 0!==e?e:[]),this.required,this.disabled,this.label,this._handleChange):(0,d.qy)(f||(f=_`
      <ha-label-picker
        no-add
        .hass=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .label=${0}
        @value-changed=${0}
      >
      </ha-label-picker>
    `),this.hass,this.value,this.required,this.disabled,this.label,this._handleChange)}},{key:"_handleChange",value:function(e){var t=e.detail.value;this.value!==t&&((""===t||Array.isArray(t)&&0===t.length)&&!this.required&&(t=void 0),(0,h.r)(this,"value-changed",{value:t}))}}])}(d.WF);g.styles=(0,d.AH)(y||(y=_`
    ha-labels-picker {
      display: block;
      width: 100%;
    }
  `)),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,l.__decorate)([(0,u.MZ)()],g.prototype,"value",void 0),(0,l.__decorate)([(0,u.MZ)()],g.prototype,"name",void 0),(0,l.__decorate)([(0,u.MZ)()],g.prototype,"label",void 0),(0,l.__decorate)([(0,u.MZ)()],g.prototype,"placeholder",void 0),(0,l.__decorate)([(0,u.MZ)()],g.prototype,"helper",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],g.prototype,"selector",void 0),(0,l.__decorate)([(0,u.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,l.__decorate)([(0,u.MZ)({type:Boolean})],g.prototype,"required",void 0),g=(0,l.__decorate)([(0,u.EM)("ha-selector-label")],g),a()}catch(k){a(k)}}))},70570:function(e,t,r){r.d(t,{N:function(){return i}});r(16280),r(44114),r(26099),r(3362);var a=e=>{var t=[];function r(r,a){e=a?r:Object.assign(Object.assign({},e),r);for(var n=t,i=0;i<n.length;i++)n[i](e)}return{get state(){return e},action(t){function a(e){r(e,!1)}return function(){for(var r=[e],n=0;n<arguments.length;n++)r.push(arguments[n]);var i=t.apply(this,r);if(null!=i)return i instanceof Promise?i.then(a):a(i)}},setState:r,clearState(){e=void 0},subscribe(e){return t.push(e),()=>{!function(e){for(var r=[],a=0;a<t.length;a++)t[a]===e?e=null:r.push(t[a]);t=r}(e)}}}},n=function(e,t,r,n){var i=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{unsubGrace:!0};if(e[t])return e[t];var o,s,l=0,d=a(),u=()=>{if(!r)throw new Error("Collection does not support refresh");return r(e).then((e=>d.setState(e,!0)))},c=()=>u().catch((t=>{if(e.connected)throw t})),h=()=>{s=void 0,o&&o.then((e=>{e()})),d.clearState(),e.removeEventListener("ready",u),e.removeEventListener("disconnected",v)},v=()=>{s&&(clearTimeout(s),h())};return e[t]={get state(){return d.state},refresh:u,subscribe(t){1===++l&&(()=>{if(void 0!==s)return clearTimeout(s),void(s=void 0);n&&(o=n(e,d)),r&&(e.addEventListener("ready",c),c()),e.addEventListener("disconnected",v)})();var a=d.subscribe(t);return void 0!==d.state&&setTimeout((()=>t(d.state)),0),()=>{a(),--l||(i.unsubGrace?s=setTimeout(h,5e3):h())}}},e[t]},i=(e,t,r,a,i)=>n(a,e,t,r).subscribe(i)}}]);
//# sourceMappingURL=2401.ac131d6ccdfab000.js.map