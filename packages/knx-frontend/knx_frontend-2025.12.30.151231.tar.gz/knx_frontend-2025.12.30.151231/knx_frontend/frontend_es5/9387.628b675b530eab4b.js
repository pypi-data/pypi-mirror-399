"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9387"],{39651:function(t,o,e){e.r(o),e.d(o,{HaIconButtonGroup:function(){return c}});var r,n,i=e(44734),a=e(56038),l=e(69683),s=e(6454),h=e(62826),u=e(96196),p=e(77845),d=t=>t,c=function(t){function o(){return(0,i.A)(this,o),(0,l.A)(this,o,arguments)}return(0,s.A)(o,t),(0,a.A)(o,[{key:"render",value:function(){return(0,u.qy)(r||(r=d`<slot></slot>`))}}])}(u.WF);c.styles=(0,u.AH)(n||(n=d`
    :host {
      position: relative;
      display: flex;
      flex-direction: row;
      align-items: center;
      height: 48px;
      border-radius: var(--ha-border-radius-4xl);
      background-color: rgba(139, 145, 151, 0.1);
      box-sizing: border-box;
      width: auto;
      padding: 0;
    }
    ::slotted(.separator) {
      background-color: rgba(var(--rgb-primary-text-color), 0.15);
      width: 1px;
      margin: 0 1px;
      height: 40px;
    }
  `)),c=(0,h.__decorate)([(0,p.EM)("ha-icon-button-group")],c)},48939:function(t,o,e){e.a(t,(async function(t,r){try{e.r(o),e.d(o,{HaIconButtonToolbar:function(){return w}});var n=e(44734),i=e(56038),a=e(69683),l=e(6454),s=(e(28706),e(2008),e(62062),e(18111),e(22489),e(61701),e(26099),e(62826)),h=e(96196),u=e(77845),p=(e(22598),e(60733),e(39651),e(88422)),d=t([p]);p=(d.then?(await d)():d)[0];var c,b,v,y,f=t=>t,w=function(t){function o(){var t;(0,n.A)(this,o);for(var e=arguments.length,r=new Array(e),i=0;i<e;i++)r[i]=arguments[i];return(t=(0,a.A)(this,o,[].concat(r))).items=[],t}return(0,l.A)(o,t),(0,i.A)(o,[{key:"findToolbarButtons",value:function(){var t,o=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"",e=null===(t=this._buttons)||void 0===t?void 0:t.filter((t=>t.classList.contains("icon-toolbar-button")));if(e&&e.length){if(!o.length)return e;var r=e.filter((t=>t.querySelector(o)));return r.length?r:void 0}}},{key:"findToolbarButtonById",value:function(t){var o,e=null===(o=this.shadowRoot)||void 0===o?void 0:o.getElementById(t);if(e&&"ha-icon-button"===e.localName)return e}},{key:"render",value:function(){return(0,h.qy)(c||(c=f`
      <ha-icon-button-group class="icon-toolbar-buttongroup">
        ${0}
      </ha-icon-button-group>
    `),this.items.map((t=>{var o,e,r,n;return"string"==typeof t?(0,h.qy)(b||(b=f`<div class="icon-toolbar-divider" role="separator"></div>`)):(0,h.qy)(v||(v=f`<ha-tooltip
                  .disabled=${0}
                  .for=${0}
                  >${0}</ha-tooltip
                >
                <ha-icon-button
                  class="icon-toolbar-button"
                  .id=${0}
                  @click=${0}
                  .label=${0}
                  .path=${0}
                  .disabled=${0}
                ></ha-icon-button>`),!t.tooltip,null!==(o=t.id)&&void 0!==o?o:"icon-button-"+t.label,null!==(e=t.tooltip)&&void 0!==e?e:"",null!==(r=t.id)&&void 0!==r?r:"icon-button-"+t.label,t.action,t.label,t.path,null!==(n=t.disabled)&&void 0!==n&&n)})))}}])}(h.WF);w.styles=(0,h.AH)(y||(y=f`
    :host {
      position: absolute;
      top: 0px;
      width: 100%;
      display: flex;
      flex-direction: row-reverse;
      background-color: var(
        --icon-button-toolbar-color,
        var(--secondary-background-color, whitesmoke)
      );
      --icon-button-toolbar-height: 32px;
      --icon-button-toolbar-button: calc(
        var(--icon-button-toolbar-height) - 4px
      );
      --icon-button-toolbar-icon: calc(
        var(--icon-button-toolbar-height) - 10px
      );
    }

    .icon-toolbar-divider {
      height: var(--icon-button-toolbar-icon);
      margin: 0px 4px;
      border: 0.5px solid
        var(--divider-color, var(--secondary-text-color, transparent));
    }

    .icon-toolbar-buttongroup {
      background-color: transparent;
      padding-right: 4px;
      height: var(--icon-button-toolbar-height);
      gap: var(--ha-space-2);
    }

    .icon-toolbar-button {
      color: var(--secondary-text-color);
      --mdc-icon-button-size: var(--icon-button-toolbar-button);
      --mdc-icon-size: var(--icon-button-toolbar-icon);
      /* Ensure button is clickable on iOS */
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
      touch-action: manipulation;
    }
  `)),(0,s.__decorate)([(0,u.MZ)({type:Array,attribute:!1})],w.prototype,"items",void 0),(0,s.__decorate)([(0,u.YG)("ha-icon-button")],w.prototype,"_buttons",void 0),w=(0,s.__decorate)([(0,u.EM)("ha-icon-button-toolbar")],w),r()}catch(g){r(g)}}))},88422:function(t,o,e){e.a(t,(async function(t,o){try{var r=e(44734),n=e(56038),i=e(69683),a=e(6454),l=(e(28706),e(2892),e(62826)),s=e(52630),h=e(96196),u=e(77845),p=t([s]);s=(p.then?(await p)():p)[0];var d,c=t=>t,b=function(t){function o(){var t;(0,r.A)(this,o);for(var e=arguments.length,n=new Array(e),a=0;a<e;a++)n[a]=arguments[a];return(t=(0,i.A)(this,o,[].concat(n))).showDelay=150,t.hideDelay=150,t}return(0,a.A)(o,t),(0,n.A)(o,null,[{key:"styles",get:function(){return[s.A.styles,(0,h.AH)(d||(d=c`
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
      `))]}}])}(s.A);(0,l.__decorate)([(0,u.MZ)({attribute:"show-delay",type:Number})],b.prototype,"showDelay",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"hide-delay",type:Number})],b.prototype,"hideDelay",void 0),b=(0,l.__decorate)([(0,u.EM)("ha-tooltip")],b),o()}catch(v){o(v)}}))},61171:function(t,o,e){var r,n=e(96196);o.A=(0,n.AH)(r||(r=(t=>t)`:host {
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
`))},52630:function(t,o,e){e.a(t,(async function(t,r){try{e.d(o,{A:function(){return T}});var n=e(61397),i=e(50264),a=e(44734),l=e(56038),s=e(69683),h=e(6454),u=e(25460),p=(e(2008),e(74423),e(44114),e(18111),e(22489),e(2892),e(26099),e(27495),e(90744),e(96196)),d=e(77845),c=e(94333),b=e(17051),v=e(42462),y=e(28438),f=e(98779),w=e(27259),g=e(984),m=e(53720),k=e(9395),A=e(32510),x=e(40158),C=e(61171),E=t([x]);x=(E.then?(await E)():E)[0];var M,D=t=>t,_=Object.defineProperty,B=Object.getOwnPropertyDescriptor,L=(t,o,e,r)=>{for(var n,i=r>1?void 0:r?B(o,e):o,a=t.length-1;a>=0;a--)(n=t[a])&&(i=(r?n(o,e,i):n(i))||i);return r&&i&&_(o,e,i),i},T=function(t){function o(){var t;return(0,a.A)(this,o),(t=(0,s.A)(this,o,arguments)).placement="top",t.disabled=!1,t.distance=8,t.open=!1,t.skidding=0,t.showDelay=150,t.hideDelay=0,t.trigger="hover focus",t.withoutArrow=!1,t.for=null,t.anchor=null,t.eventController=new AbortController,t.handleBlur=()=>{t.hasTrigger("focus")&&t.hide()},t.handleClick=()=>{t.hasTrigger("click")&&(t.open?t.hide():t.show())},t.handleFocus=()=>{t.hasTrigger("focus")&&t.show()},t.handleDocumentKeyDown=o=>{"Escape"===o.key&&(o.stopPropagation(),t.hide())},t.handleMouseOver=()=>{t.hasTrigger("hover")&&(clearTimeout(t.hoverTimeout),t.hoverTimeout=window.setTimeout((()=>t.show()),t.showDelay))},t.handleMouseOut=()=>{t.hasTrigger("hover")&&(clearTimeout(t.hoverTimeout),t.hoverTimeout=window.setTimeout((()=>t.hide()),t.hideDelay))},t}return(0,h.A)(o,t),(0,l.A)(o,[{key:"connectedCallback",value:function(){(0,u.A)(o,"connectedCallback",this,3)([]),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,m.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}},{key:"disconnectedCallback",value:function(){(0,u.A)(o,"disconnectedCallback",this,3)([]),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}},{key:"firstUpdated",value:function(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}},{key:"hasTrigger",value:function(t){return this.trigger.split(" ").includes(t)}},{key:"addToAriaLabelledBy",value:function(t,o){var e=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);e.includes(o)||(e.push(o),t.setAttribute("aria-labelledby",e.join(" ")))}},{key:"removeFromAriaLabelledBy",value:function(t,o){var e=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((t=>t!==o));e.length>0?t.setAttribute("aria-labelledby",e.join(" ")):t.removeAttribute("aria-labelledby")}},{key:"handleOpenChange",value:(k=(0,i.A)((0,n.A)().m((function t(){var o,e;return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this.open){t.n=4;break}if(!this.disabled){t.n=1;break}return t.a(2);case 1:if(o=new f.k,this.dispatchEvent(o),!o.defaultPrevented){t.n=2;break}return this.open=!1,t.a(2);case 2:return document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,t.n=3,(0,w.Ud)(this.popup.popup,"show-with-scale");case 3:this.popup.reposition(),this.dispatchEvent(new v.q),t.n=7;break;case 4:if(e=new y.L,this.dispatchEvent(e),!e.defaultPrevented){t.n=5;break}return this.open=!1,t.a(2);case 5:return document.removeEventListener("keydown",this.handleDocumentKeyDown),t.n=6,(0,w.Ud)(this.popup.popup,"hide-with-scale");case 6:this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new b.Z);case 7:return t.a(2)}}),t,this)}))),function(){return k.apply(this,arguments)})},{key:"handleForChange",value:function(){var t=this.getRootNode();if(t){var o=this.for?t.getElementById(this.for):null,e=this.anchor;if(o!==e){var r=this.eventController.signal;o&&(this.addToAriaLabelledBy(o,this.id),o.addEventListener("blur",this.handleBlur,{capture:!0,signal:r}),o.addEventListener("focus",this.handleFocus,{capture:!0,signal:r}),o.addEventListener("click",this.handleClick,{signal:r}),o.addEventListener("mouseover",this.handleMouseOver,{signal:r}),o.addEventListener("mouseout",this.handleMouseOut,{signal:r})),e&&(this.removeFromAriaLabelledBy(e,this.id),e.removeEventListener("blur",this.handleBlur,{capture:!0}),e.removeEventListener("focus",this.handleFocus,{capture:!0}),e.removeEventListener("click",this.handleClick),e.removeEventListener("mouseover",this.handleMouseOver),e.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=o}}}},{key:"handleOptionsChange",value:(d=(0,i.A)((0,n.A)().m((function t(){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this.hasUpdated){t.n=2;break}return t.n=1,this.updateComplete;case 1:this.popup.reposition();case 2:return t.a(2)}}),t,this)}))),function(){return d.apply(this,arguments)})},{key:"handleDisabledChange",value:function(){this.disabled&&this.open&&this.hide()}},{key:"show",value:(r=(0,i.A)((0,n.A)().m((function t(){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this.open){t.n=1;break}return t.a(2,void 0);case 1:return this.open=!0,t.a(2,(0,g.l)(this,"wa-after-show"))}}),t,this)}))),function(){return r.apply(this,arguments)})},{key:"hide",value:(e=(0,i.A)((0,n.A)().m((function t(){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(this.open){t.n=1;break}return t.a(2,void 0);case 1:return this.open=!1,t.a(2,(0,g.l)(this,"wa-after-hide"))}}),t,this)}))),function(){return e.apply(this,arguments)})},{key:"render",value:function(){return(0,p.qy)(M||(M=D`
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
    `),(0,c.H)({tooltip:!0,"tooltip-open":this.open}),this.placement,this.distance,this.skidding,!this.withoutArrow,this.anchor)}}]);var e,r,d,k}(A.A);T.css=C.A,T.dependencies={"wa-popup":x.A},L([(0,d.P)("slot:not([name])")],T.prototype,"defaultSlot",2),L([(0,d.P)(".body")],T.prototype,"body",2),L([(0,d.P)("wa-popup")],T.prototype,"popup",2),L([(0,d.MZ)()],T.prototype,"placement",2),L([(0,d.MZ)({type:Boolean,reflect:!0})],T.prototype,"disabled",2),L([(0,d.MZ)({type:Number})],T.prototype,"distance",2),L([(0,d.MZ)({type:Boolean,reflect:!0})],T.prototype,"open",2),L([(0,d.MZ)({type:Number})],T.prototype,"skidding",2),L([(0,d.MZ)({attribute:"show-delay",type:Number})],T.prototype,"showDelay",2),L([(0,d.MZ)({attribute:"hide-delay",type:Number})],T.prototype,"hideDelay",2),L([(0,d.MZ)()],T.prototype,"trigger",2),L([(0,d.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],T.prototype,"withoutArrow",2),L([(0,d.MZ)()],T.prototype,"for",2),L([(0,d.wk)()],T.prototype,"anchor",2),L([(0,k.w)("open",{waitUntilFirstUpdate:!0})],T.prototype,"handleOpenChange",1),L([(0,k.w)("for")],T.prototype,"handleForChange",1),L([(0,k.w)(["distance","placement","skidding"])],T.prototype,"handleOptionsChange",1),L([(0,k.w)("disabled")],T.prototype,"handleDisabledChange",1),T=L([(0,d.EM)("wa-tooltip")],T),r()}catch($){r($)}}))},95192:function(t,o,e){e.d(o,{IU:function(){return h},Jt:function(){return l},Yd:function(){return n},hZ:function(){return s},y$:function(){return i}});var r;e(78261),e(23792),e(62062),e(44114),e(18111),e(7588),e(61701),e(26099),e(3362),e(23500),e(62953);function n(t){return new Promise(((o,e)=>{t.oncomplete=t.onsuccess=()=>o(t.result),t.onabort=t.onerror=()=>e(t.error)}))}function i(t,o){var e;return(r,i)=>(()=>{if(e)return e;var r=indexedDB.open(t);return r.onupgradeneeded=()=>r.result.createObjectStore(o),(e=n(r)).then((t=>{t.onclose=()=>e=void 0}),(()=>{})),e})().then((t=>i(t.transaction(o,r).objectStore(o))))}function a(){return r||(r=i("keyval-store","keyval")),r}function l(t){return(arguments.length>1&&void 0!==arguments[1]?arguments[1]:a())("readonly",(o=>n(o.get(t))))}function s(t,o){return(arguments.length>2&&void 0!==arguments[2]?arguments[2]:a())("readwrite",(e=>(e.put(o,t),n(e.transaction))))}function h(){return(arguments.length>0&&void 0!==arguments[0]?arguments[0]:a())("readwrite",(t=>(t.clear(),n(t.transaction))))}}}]);
//# sourceMappingURL=9387.628b675b530eab4b.js.map