/*! For license information please see 2623.27bf346558ac8446.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2623"],{61171:function(t,e,o){var i,n=o(96196);e.A=(0,n.AH)(i||(i=(t=>t)`:host {
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
`))},52630:function(t,e,o){o.a(t,(async function(t,i){try{o.d(e,{A:function(){return B}});var n=o(61397),r=o(50264),s=o(44734),a=o(56038),h=o(69683),l=o(6454),c=o(25460),u=(o(2008),o(74423),o(44114),o(18111),o(22489),o(2892),o(26099),o(27495),o(90744),o(96196)),p=o(77845),d=o(94333),b=o(17051),v=o(42462),f=o(28438),w=o(98779),y=o(27259),g=o(984),k=o(53720),m=o(9395),A=o(32510),x=o(40158),C=o(61171),E=t([x]);x=(E.then?(await E)():E)[0];var L,T=t=>t,D=Object.defineProperty,M=Object.getOwnPropertyDescriptor,O=(t,e,o,i)=>{for(var n,r=i>1?void 0:i?M(e,o):e,s=t.length-1;s>=0;s--)(n=t[s])&&(r=(i?n(e,o,r):n(r))||r);return i&&r&&D(e,o,r),r},B=function(t){function e(){var t;return(0,s.A)(this,e),(t=(0,h.A)(this,e,arguments)).placement="top",t.disabled=!1,t.distance=8,t.open=!1,t.skidding=0,t.showDelay=150,t.hideDelay=0,t.trigger="hover focus",t.withoutArrow=!1,t.for=null,t.anchor=null,t.eventController=new AbortController,t.handleBlur=()=>{t.hasTrigger("focus")&&t.hide()},t.handleClick=()=>{t.hasTrigger("click")&&(t.open?t.hide():t.show())},t.handleFocus=()=>{t.hasTrigger("focus")&&t.show()},t.handleDocumentKeyDown=e=>{"Escape"===e.key&&(e.stopPropagation(),t.hide())},t.handleMouseOver=()=>{t.hasTrigger("hover")&&(clearTimeout(t.hoverTimeout),t.hoverTimeout=window.setTimeout((()=>t.show()),t.showDelay))},t.handleMouseOut=()=>{t.hasTrigger("hover")&&(clearTimeout(t.hoverTimeout),t.hoverTimeout=window.setTimeout((()=>t.hide()),t.hideDelay))},t}return(0,l.A)(e,t),(0,a.A)(e,[{key:"connectedCallback",value:function(){(0,c.A)(e,"connectedCallback",this,3)([]),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,k.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}},{key:"disconnectedCallback",value:function(){(0,c.A)(e,"disconnectedCallback",this,3)([]),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}},{key:"firstUpdated",value:function(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}},{key:"hasTrigger",value:function(t){return this.trigger.split(" ").includes(t)}},{key:"addToAriaLabelledBy",value:function(t,e){var o=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);o.includes(e)||(o.push(e),t.setAttribute("aria-labelledby",o.join(" ")))}},{key:"removeFromAriaLabelledBy",value:function(t,e){var o=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((t=>t!==e));o.length>0?t.setAttribute("aria-labelledby",o.join(" ")):t.removeAttribute("aria-labelledby")}},{key:"handleOpenChange",value:(m=(0,r.A)((0,n.A)().m((function t(){var e,o;return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this.open){t.n=4;break}if(!this.disabled){t.n=1;break}return t.a(2);case 1:if(e=new w.k,this.dispatchEvent(e),!e.defaultPrevented){t.n=2;break}return this.open=!1,t.a(2);case 2:return document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,t.n=3,(0,y.Ud)(this.popup.popup,"show-with-scale");case 3:this.popup.reposition(),this.dispatchEvent(new v.q),t.n=7;break;case 4:if(o=new f.L,this.dispatchEvent(o),!o.defaultPrevented){t.n=5;break}return this.open=!1,t.a(2);case 5:return document.removeEventListener("keydown",this.handleDocumentKeyDown),t.n=6,(0,y.Ud)(this.popup.popup,"hide-with-scale");case 6:this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new b.Z);case 7:return t.a(2)}}),t,this)}))),function(){return m.apply(this,arguments)})},{key:"handleForChange",value:function(){var t=this.getRootNode();if(t){var e=this.for?t.getElementById(this.for):null,o=this.anchor;if(e!==o){var i=this.eventController.signal;e&&(this.addToAriaLabelledBy(e,this.id),e.addEventListener("blur",this.handleBlur,{capture:!0,signal:i}),e.addEventListener("focus",this.handleFocus,{capture:!0,signal:i}),e.addEventListener("click",this.handleClick,{signal:i}),e.addEventListener("mouseover",this.handleMouseOver,{signal:i}),e.addEventListener("mouseout",this.handleMouseOut,{signal:i})),o&&(this.removeFromAriaLabelledBy(o,this.id),o.removeEventListener("blur",this.handleBlur,{capture:!0}),o.removeEventListener("focus",this.handleFocus,{capture:!0}),o.removeEventListener("click",this.handleClick),o.removeEventListener("mouseover",this.handleMouseOver),o.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=e}}}},{key:"handleOptionsChange",value:(p=(0,r.A)((0,n.A)().m((function t(){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this.hasUpdated){t.n=2;break}return t.n=1,this.updateComplete;case 1:this.popup.reposition();case 2:return t.a(2)}}),t,this)}))),function(){return p.apply(this,arguments)})},{key:"handleDisabledChange",value:function(){this.disabled&&this.open&&this.hide()}},{key:"show",value:(i=(0,r.A)((0,n.A)().m((function t(){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this.open){t.n=1;break}return t.a(2,void 0);case 1:return this.open=!0,t.a(2,(0,g.l)(this,"wa-after-show"))}}),t,this)}))),function(){return i.apply(this,arguments)})},{key:"hide",value:(o=(0,r.A)((0,n.A)().m((function t(){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(this.open){t.n=1;break}return t.a(2,void 0);case 1:return this.open=!1,t.a(2,(0,g.l)(this,"wa-after-hide"))}}),t,this)}))),function(){return o.apply(this,arguments)})},{key:"render",value:function(){return(0,u.qy)(L||(L=T`
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
    `),(0,d.H)({tooltip:!0,"tooltip-open":this.open}),this.placement,this.distance,this.skidding,!this.withoutArrow,this.anchor)}}]);var o,i,p,m}(A.A);B.css=C.A,B.dependencies={"wa-popup":x.A},O([(0,p.P)("slot:not([name])")],B.prototype,"defaultSlot",2),O([(0,p.P)(".body")],B.prototype,"body",2),O([(0,p.P)("wa-popup")],B.prototype,"popup",2),O([(0,p.MZ)()],B.prototype,"placement",2),O([(0,p.MZ)({type:Boolean,reflect:!0})],B.prototype,"disabled",2),O([(0,p.MZ)({type:Number})],B.prototype,"distance",2),O([(0,p.MZ)({type:Boolean,reflect:!0})],B.prototype,"open",2),O([(0,p.MZ)({type:Number})],B.prototype,"skidding",2),O([(0,p.MZ)({attribute:"show-delay",type:Number})],B.prototype,"showDelay",2),O([(0,p.MZ)({attribute:"hide-delay",type:Number})],B.prototype,"hideDelay",2),O([(0,p.MZ)()],B.prototype,"trigger",2),O([(0,p.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],B.prototype,"withoutArrow",2),O([(0,p.MZ)()],B.prototype,"for",2),O([(0,p.wk)()],B.prototype,"anchor",2),O([(0,m.w)("open",{waitUntilFirstUpdate:!0})],B.prototype,"handleOpenChange",1),O([(0,m.w)("for")],B.prototype,"handleForChange",1),O([(0,m.w)(["distance","placement","skidding"])],B.prototype,"handleOptionsChange",1),O([(0,m.w)("disabled")],B.prototype,"handleDisabledChange",1),B=O([(0,p.EM)("wa-tooltip")],B),i()}catch(P){i(P)}}))},16527:function(t,e,o){o.d(e,{q6:function(){return l},Fg:function(){return w},DT:function(){return f}});var i=o(56038),n=o(44734),r=o(69683),s=o(6454),a=o(79993),h=function(t){function e(t,o,i,s){var a;return(0,n.A)(this,e),(a=(0,r.A)(this,e,["context-request",{bubbles:!0,composed:!0}])).context=t,a.contextTarget=o,a.callback=i,a.subscribe=null!=s&&s,a}return(0,s.A)(e,t),(0,i.A)(e)}((0,a.A)(Event));function l(t){return t}var c=function(){return(0,i.A)((function t(e,o,i,r){if((0,n.A)(this,t),this.subscribe=!1,this.provided=!1,this.value=void 0,this.t=(t,e)=>{this.unsubscribe&&(this.unsubscribe!==e&&(this.provided=!1,this.unsubscribe()),this.subscribe||this.unsubscribe()),this.value=t,this.host.requestUpdate(),this.provided&&!this.subscribe||(this.provided=!0,this.callback&&this.callback(t,e)),this.unsubscribe=e},this.host=e,void 0!==o.context){var s,a=o;this.context=a.context,this.callback=a.callback,this.subscribe=null!==(s=a.subscribe)&&void 0!==s&&s}else this.context=o,this.callback=i,this.subscribe=null!=r&&r;this.host.addController(this)}),[{key:"hostConnected",value:function(){this.dispatchRequest()}},{key:"hostDisconnected",value:function(){this.unsubscribe&&(this.unsubscribe(),this.unsubscribe=void 0)}},{key:"dispatchRequest",value:function(){this.host.dispatchEvent(new h(this.context,this.host,this.t,this.subscribe))}}])}(),u=o(78261),p=o(31432),d=o(75864),b=(o(23792),o(26099),o(31415),o(17642),o(58004),o(33853),o(45876),o(32475),o(15024),o(31698),o(62953),o(36033),function(){return(0,i.A)((function t(e){(0,n.A)(this,t),this.subscriptions=new Map,this.updateObservers=()=>{var t,e=(0,p.A)(this.subscriptions);try{for(e.s();!(t=e.n()).done;){var o=(0,u.A)(t.value,2),i=o[0],n=o[1].disposer;i(this.o,n)}}catch(r){e.e(r)}finally{e.f()}},void 0!==e&&(this.value=e)}),[{key:"value",get:function(){return this.o},set:function(t){this.setValue(t)}},{key:"setValue",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]&&arguments[1]||!Object.is(t,this.o);this.o=t,e&&this.updateObservers()}},{key:"addCallback",value:function(t,e,o){if(o){this.subscriptions.has(t)||this.subscriptions.set(t,{disposer:()=>{this.subscriptions.delete(t)},consumerHost:e});var i=this.subscriptions.get(t).disposer;t(this.value,i)}else t(this.value)}},{key:"clearCallbacks",value:function(){this.subscriptions.clear()}}])}()),v=function(t){function e(t,o){var i;return(0,n.A)(this,e),(i=(0,r.A)(this,e,["context-provider",{bubbles:!0,composed:!0}])).context=t,i.contextTarget=o,i}return(0,s.A)(e,t),(0,i.A)(e)}((0,a.A)(Event)),f=function(t){function e(t,o,i){var s,a,l;return(0,n.A)(this,e),(l=(0,r.A)(this,e,[void 0!==o.context?o.initialValue:i])).onContextRequest=t=>{var e;if(t.context===l.context){var o=null!==(e=t.contextTarget)&&void 0!==e?e:t.composedPath()[0];o!==l.host&&(t.stopPropagation(),l.addCallback(t.callback,o,t.subscribe))}},l.onProviderRequest=t=>{var e;if(t.context===l.context&&(null!==(e=t.contextTarget)&&void 0!==e?e:t.composedPath()[0])!==l.host){var o,i=new Set,n=(0,p.A)(l.subscriptions);try{for(n.s();!(o=n.n()).done;){var r=(0,u.A)(o.value,2),s=r[0],a=r[1].consumerHost;i.has(s)||(i.add(s),a.dispatchEvent(new h(l.context,a,s,!0)))}}catch(c){n.e(c)}finally{n.f()}t.stopPropagation()}},l.host=t,void 0!==o.context?l.context=o.context:l.context=o,l.attachListeners(),null===(s=(a=l.host).addController)||void 0===s||s.call(a,(0,d.A)(l)),l}return(0,s.A)(e,t),(0,i.A)(e,[{key:"attachListeners",value:function(){this.host.addEventListener("context-request",this.onContextRequest),this.host.addEventListener("context-provider",this.onProviderRequest)}},{key:"hostConnected",value:function(){this.host.dispatchEvent(new v(this.context,this.host))}}])}(b);o(44114),o(73772),o(30958);function w(t){var e=t.context,o=t.subscribe;return(t,i)=>{"object"==typeof i?i.addInitializer((function(){new c(this,{context:e,callback:e=>{t.set.call(this,e)},subscribe:o})})):t.constructor.addInitializer((t=>{new c(t,{context:e,callback:e=>{t[i]=e},subscribe:o})}))}}}}]);
//# sourceMappingURL=2623.27bf346558ac8446.js.map