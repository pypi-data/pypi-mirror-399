"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7208"],{55124:function(e,t,o){o.d(t,{d:function(){return r}});var r=e=>e.stopPropagation()},87400:function(e,t,o){o.d(t,{l:function(){return r}});var r=(e,t,o,r,a)=>{var n=t[e.entity_id];return n?i(n,t,o,r,a):{entity:null,device:null,area:null,floor:null}},i=(e,t,o,r,i)=>{var a=t[e.entity_id],n=null==e?void 0:e.device_id,l=n?o[n]:void 0,s=(null==e?void 0:e.area_id)||(null==l?void 0:l.area_id),h=s?r[s]:void 0,p=null==h?void 0:h.floor_id;return{entity:a,device:l||null,area:h||null,floor:(p?i[p]:void 0)||null}}},27075:function(e,t,o){o.a(e,(async function(e,r){try{o.r(t),o.d(t,{HaTemplateSelector:function(){return A}});var i=o(44734),a=o(56038),n=o(69683),l=o(6454),s=(o(28706),o(50113),o(74423),o(26099),o(62826)),h=o(96196),p=o(77845),d=o(92542),u=o(62001),c=o(32884),v=(o(56768),o(17963),e([c]));c=(v.then?(await v)():v)[0];var y,w,f,b,g,m=e=>e,k=["template:","sensor:","state:","trigger: template"],A=function(e){function t(){var e;(0,i.A)(this,t);for(var o=arguments.length,r=new Array(o),a=0;a<o;a++)r[a]=arguments[a];return(e=(0,n.A)(this,t,[].concat(r))).disabled=!1,e.required=!0,e.warn=void 0,e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"render",value:function(){return(0,h.qy)(y||(y=m`
      ${0}
      ${0}
      <ha-code-editor
        mode="jinja2"
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        .placeholder=${0}
        autofocus
        autocomplete-entities
        autocomplete-icons
        @value-changed=${0}
        dir="ltr"
        linewrap
      ></ha-code-editor>
      ${0}
    `),this.warn?(0,h.qy)(w||(w=m`<ha-alert alert-type="warning"
            >${0}
            <br />
            <a
              target="_blank"
              rel="noopener noreferrer"
              href=${0}
              >${0}</a
            ></ha-alert
          >`),this.hass.localize("ui.components.selectors.template.yaml_warning",{string:this.warn}),(0,u.o)(this.hass,"/docs/configuration/templating/"),this.hass.localize("ui.components.selectors.template.learn_more")):h.s6,this.label?(0,h.qy)(f||(f=m`<p>${0}${0}</p>`),this.label,this.required?"*":""):h.s6,this.hass,this.value,this.disabled,this.placeholder||"{{ ... }}",this._handleChange,this.helper?(0,h.qy)(b||(b=m`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):h.s6)}},{key:"_handleChange",value:function(e){e.stopPropagation();var t=e.target.value;this.value!==t&&(this.warn=k.find((e=>t.includes(e))),""!==t||this.required||(t=void 0),(0,d.r)(this,"value-changed",{value:t}))}}])}(h.WF);A.styles=(0,h.AH)(g||(g=m`
    p {
      margin-top: 0;
    }
  `)),(0,s.__decorate)([(0,p.MZ)({attribute:!1})],A.prototype,"hass",void 0),(0,s.__decorate)([(0,p.MZ)()],A.prototype,"value",void 0),(0,s.__decorate)([(0,p.MZ)()],A.prototype,"label",void 0),(0,s.__decorate)([(0,p.MZ)()],A.prototype,"helper",void 0),(0,s.__decorate)([(0,p.MZ)()],A.prototype,"placeholder",void 0),(0,s.__decorate)([(0,p.MZ)({type:Boolean})],A.prototype,"disabled",void 0),(0,s.__decorate)([(0,p.MZ)({type:Boolean})],A.prototype,"required",void 0),(0,s.__decorate)([(0,p.wk)()],A.prototype,"warn",void 0),A=(0,s.__decorate)([(0,p.EM)("ha-selector-template")],A),r()}catch(_){r(_)}}))},88422:function(e,t,o){o.a(e,(async function(e,t){try{var r=o(44734),i=o(56038),a=o(69683),n=o(6454),l=(o(28706),o(2892),o(62826)),s=o(52630),h=o(96196),p=o(77845),d=e([s]);s=(d.then?(await d)():d)[0];var u,c=e=>e,v=function(e){function t(){var e;(0,r.A)(this,t);for(var o=arguments.length,i=new Array(o),n=0;n<o;n++)i[n]=arguments[n];return(e=(0,a.A)(this,t,[].concat(i))).showDelay=150,e.hideDelay=150,e}return(0,n.A)(t,e),(0,i.A)(t,null,[{key:"styles",get:function(){return[s.A.styles,(0,h.AH)(u||(u=c`
        :host {
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-content-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(
            --ha-tooltip-border-radius,
            var(--ha-border-radius-sm)
          );
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
        }
      `))]}}])}(s.A);(0,l.__decorate)([(0,p.MZ)({attribute:"show-delay",type:Number})],v.prototype,"showDelay",void 0),(0,l.__decorate)([(0,p.MZ)({attribute:"hide-delay",type:Number})],v.prototype,"hideDelay",void 0),v=(0,l.__decorate)([(0,p.EM)("ha-tooltip")],v),t()}catch(y){t(y)}}))},62001:function(e,t,o){o.d(t,{o:function(){return r}});o(74423);var r=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},4848:function(e,t,o){o.d(t,{P:function(){return i}});var r=o(92542),i=(e,t)=>(0,r.r)(e,"hass-notification",t)},69479:function(e,t,o){var r=o(43724),i=o(62106),a=o(65213),n=o(67979);r&&!a.correct&&(i(RegExp.prototype,"flags",{configurable:!0,get:n}),a.correct=!0)},61171:function(e,t,o){var r,i=o(96196);t.A=(0,i.AH)(r||(r=(e=>e)`:host {
  --max-width: 30ch;
  display: inline-block;
  position: absolute;
  color: var(--wa-tooltip-content-color);
  font-size: var(--wa-tooltip-font-size);
  line-height: var(--wa-tooltip-line-height);
  text-align: start;
  white-space: normal;
}
.tooltip {
  --arrow-size: var(--wa-tooltip-arrow-size);
  --arrow-color: var(--wa-tooltip-background-color);
}
.tooltip::part(popup) {
  z-index: 1000;
}
.tooltip[placement^=top]::part(popup) {
  transform-origin: bottom;
}
.tooltip[placement^=bottom]::part(popup) {
  transform-origin: top;
}
.tooltip[placement^=left]::part(popup) {
  transform-origin: right;
}
.tooltip[placement^=right]::part(popup) {
  transform-origin: left;
}
.body {
  display: block;
  width: max-content;
  max-width: var(--max-width);
  border-radius: var(--wa-tooltip-border-radius);
  background-color: var(--wa-tooltip-background-color);
  border: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  padding: 0.25em 0.5em;
  user-select: none;
  -webkit-user-select: none;
}
.tooltip::part(arrow) {
  border-bottom: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  border-right: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
}
`))},52630:function(e,t,o){o.a(e,(async function(e,r){try{o.d(t,{A:function(){return x}});var i=o(61397),a=o(50264),n=o(44734),l=o(56038),s=o(69683),h=o(6454),p=o(25460),d=(o(2008),o(74423),o(44114),o(18111),o(22489),o(2892),o(26099),o(27495),o(90744),o(96196)),u=o(77845),c=o(94333),v=o(17051),y=o(42462),w=o(28438),f=o(98779),b=o(27259),g=o(984),m=o(53720),k=o(9395),A=o(32510),_=o(40158),C=o(61171),M=e([_]);_=(M.then?(await M)():M)[0];var E,$=e=>e,D=Object.defineProperty,Z=Object.getOwnPropertyDescriptor,L=(e,t,o,r)=>{for(var i,a=r>1?void 0:r?Z(t,o):t,n=e.length-1;n>=0;n--)(i=e[n])&&(a=(r?i(t,o,a):i(a))||a);return r&&a&&D(t,o,a),a},x=function(e){function t(){var e;return(0,n.A)(this,t),(e=(0,s.A)(this,t,arguments)).placement="top",e.disabled=!1,e.distance=8,e.open=!1,e.skidding=0,e.showDelay=150,e.hideDelay=0,e.trigger="hover focus",e.withoutArrow=!1,e.for=null,e.anchor=null,e.eventController=new AbortController,e.handleBlur=()=>{e.hasTrigger("focus")&&e.hide()},e.handleClick=()=>{e.hasTrigger("click")&&(e.open?e.hide():e.show())},e.handleFocus=()=>{e.hasTrigger("focus")&&e.show()},e.handleDocumentKeyDown=t=>{"Escape"===t.key&&(t.stopPropagation(),e.hide())},e.handleMouseOver=()=>{e.hasTrigger("hover")&&(clearTimeout(e.hoverTimeout),e.hoverTimeout=window.setTimeout((()=>e.show()),e.showDelay))},e.handleMouseOut=()=>{e.hasTrigger("hover")&&(clearTimeout(e.hoverTimeout),e.hoverTimeout=window.setTimeout((()=>e.hide()),e.hideDelay))},e}return(0,h.A)(t,e),(0,l.A)(t,[{key:"connectedCallback",value:function(){(0,p.A)(t,"connectedCallback",this,3)([]),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,m.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}},{key:"disconnectedCallback",value:function(){(0,p.A)(t,"disconnectedCallback",this,3)([]),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}},{key:"firstUpdated",value:function(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}},{key:"hasTrigger",value:function(e){return this.trigger.split(" ").includes(e)}},{key:"addToAriaLabelledBy",value:function(e,t){var o=(e.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);o.includes(t)||(o.push(t),e.setAttribute("aria-labelledby",o.join(" ")))}},{key:"removeFromAriaLabelledBy",value:function(e,t){var o=(e.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((e=>e!==t));o.length>0?e.setAttribute("aria-labelledby",o.join(" ")):e.removeAttribute("aria-labelledby")}},{key:"handleOpenChange",value:(k=(0,a.A)((0,i.A)().m((function e(){var t,o;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this.open){e.n=4;break}if(!this.disabled){e.n=1;break}return e.a(2);case 1:if(t=new f.k,this.dispatchEvent(t),!t.defaultPrevented){e.n=2;break}return this.open=!1,e.a(2);case 2:return document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,e.n=3,(0,b.Ud)(this.popup.popup,"show-with-scale");case 3:this.popup.reposition(),this.dispatchEvent(new y.q),e.n=7;break;case 4:if(o=new w.L,this.dispatchEvent(o),!o.defaultPrevented){e.n=5;break}return this.open=!1,e.a(2);case 5:return document.removeEventListener("keydown",this.handleDocumentKeyDown),e.n=6,(0,b.Ud)(this.popup.popup,"hide-with-scale");case 6:this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new v.Z);case 7:return e.a(2)}}),e,this)}))),function(){return k.apply(this,arguments)})},{key:"handleForChange",value:function(){var e=this.getRootNode();if(e){var t=this.for?e.getElementById(this.for):null,o=this.anchor;if(t!==o){var r=this.eventController.signal;t&&(this.addToAriaLabelledBy(t,this.id),t.addEventListener("blur",this.handleBlur,{capture:!0,signal:r}),t.addEventListener("focus",this.handleFocus,{capture:!0,signal:r}),t.addEventListener("click",this.handleClick,{signal:r}),t.addEventListener("mouseover",this.handleMouseOver,{signal:r}),t.addEventListener("mouseout",this.handleMouseOut,{signal:r})),o&&(this.removeFromAriaLabelledBy(o,this.id),o.removeEventListener("blur",this.handleBlur,{capture:!0}),o.removeEventListener("focus",this.handleFocus,{capture:!0}),o.removeEventListener("click",this.handleClick),o.removeEventListener("mouseover",this.handleMouseOver),o.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=t}}}},{key:"handleOptionsChange",value:(u=(0,a.A)((0,i.A)().m((function e(){return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this.hasUpdated){e.n=2;break}return e.n=1,this.updateComplete;case 1:this.popup.reposition();case 2:return e.a(2)}}),e,this)}))),function(){return u.apply(this,arguments)})},{key:"handleDisabledChange",value:function(){this.disabled&&this.open&&this.hide()}},{key:"show",value:(r=(0,a.A)((0,i.A)().m((function e(){return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this.open){e.n=1;break}return e.a(2,void 0);case 1:return this.open=!0,e.a(2,(0,g.l)(this,"wa-after-show"))}}),e,this)}))),function(){return r.apply(this,arguments)})},{key:"hide",value:(o=(0,a.A)((0,i.A)().m((function e(){return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(this.open){e.n=1;break}return e.a(2,void 0);case 1:return this.open=!1,e.a(2,(0,g.l)(this,"wa-after-hide"))}}),e,this)}))),function(){return o.apply(this,arguments)})},{key:"render",value:function(){return(0,d.qy)(E||(E=$`
      <wa-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${0}
        placement=${0}
        distance=${0}
        skidding=${0}
        flip
        shift
        ?arrow=${0}
        hover-bridge
        .anchor=${0}
      >
        <div part="body" class="body">
          <slot></slot>
        </div>
      </wa-popup>
    `),(0,c.H)({tooltip:!0,"tooltip-open":this.open}),this.placement,this.distance,this.skidding,!this.withoutArrow,this.anchor)}}]);var o,r,u,k}(A.A);x.css=C.A,x.dependencies={"wa-popup":_.A},L([(0,u.P)("slot:not([name])")],x.prototype,"defaultSlot",2),L([(0,u.P)(".body")],x.prototype,"body",2),L([(0,u.P)("wa-popup")],x.prototype,"popup",2),L([(0,u.MZ)()],x.prototype,"placement",2),L([(0,u.MZ)({type:Boolean,reflect:!0})],x.prototype,"disabled",2),L([(0,u.MZ)({type:Number})],x.prototype,"distance",2),L([(0,u.MZ)({type:Boolean,reflect:!0})],x.prototype,"open",2),L([(0,u.MZ)({type:Number})],x.prototype,"skidding",2),L([(0,u.MZ)({attribute:"show-delay",type:Number})],x.prototype,"showDelay",2),L([(0,u.MZ)({attribute:"hide-delay",type:Number})],x.prototype,"hideDelay",2),L([(0,u.MZ)()],x.prototype,"trigger",2),L([(0,u.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],x.prototype,"withoutArrow",2),L([(0,u.MZ)()],x.prototype,"for",2),L([(0,u.wk)()],x.prototype,"anchor",2),L([(0,k.w)("open",{waitUntilFirstUpdate:!0})],x.prototype,"handleOpenChange",1),L([(0,k.w)("for")],x.prototype,"handleForChange",1),L([(0,k.w)(["distance","placement","skidding"])],x.prototype,"handleOptionsChange",1),L([(0,k.w)("disabled")],x.prototype,"handleDisabledChange",1),x=L([(0,u.EM)("wa-tooltip")],x),r()}catch(T){r(T)}}))}}]);
//# sourceMappingURL=7208.8b12fca0b88deaf7.js.map