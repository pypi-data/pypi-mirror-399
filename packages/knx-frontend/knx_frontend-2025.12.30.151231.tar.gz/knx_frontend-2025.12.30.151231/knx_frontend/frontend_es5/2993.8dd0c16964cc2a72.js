"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2993"],{11896:function(e,t,a){a.d(t,{u:function(){return w}});var i,o,n=a(44734),r=a(56038),s=a(69683),l=a(6454),d=(a(2892),a(62826)),c=a(68846),h=a(96196),u=a(77845),p=a(94333),f=a(32288),g=a(60893),v=e=>e,b={fromAttribute(e){return null!==e&&(""===e||e)},toAttribute(e){return"boolean"==typeof e?e?"":null:e}},w=function(e){function t(){var e;return(0,n.A)(this,t),(e=(0,s.A)(this,t,arguments)).rows=2,e.cols=20,e.charCounter=!1,e}return(0,l.A)(t,e),(0,r.A)(t,[{key:"render",value:function(){var e=this.charCounter&&-1!==this.maxLength,t=e&&"internal"===this.charCounter,a=e&&!t,o=!!this.helper||!!this.validationMessage||a,n={"mdc-text-field--disabled":this.disabled,"mdc-text-field--no-label":!this.label,"mdc-text-field--filled":!this.outlined,"mdc-text-field--outlined":this.outlined,"mdc-text-field--end-aligned":this.endAligned,"mdc-text-field--with-internal-counter":t};return(0,h.qy)(i||(i=v`
      <label class="mdc-text-field mdc-text-field--textarea ${0}">
        ${0}
        ${0}
        ${0}
        ${0}
        ${0}
      </label>
      ${0}
    `),(0,p.H)(n),this.renderRipple(),this.outlined?this.renderOutline():this.renderLabel(),this.renderInput(),this.renderCharCounter(t),this.renderLineRipple(),this.renderHelperText(o,a))}},{key:"renderInput",value:function(){var e=this.label?"label":void 0,t=-1===this.minLength?void 0:this.minLength,a=-1===this.maxLength?void 0:this.maxLength,i=this.autocapitalize?this.autocapitalize:void 0;return(0,h.qy)(o||(o=v`
      <textarea
          aria-labelledby=${0}
          class="mdc-text-field__input"
          .value="${0}"
          rows="${0}"
          cols="${0}"
          ?disabled="${0}"
          placeholder="${0}"
          ?required="${0}"
          ?readonly="${0}"
          minlength="${0}"
          maxlength="${0}"
          name="${0}"
          inputmode="${0}"
          autocapitalize="${0}"
          @input="${0}"
          @blur="${0}">
      </textarea>`),(0,f.J)(e),(0,g.V)(this.value),this.rows,this.cols,this.disabled,this.placeholder,this.required,this.readOnly,(0,f.J)(t),(0,f.J)(a),(0,f.J)(""===this.name?void 0:this.name),(0,f.J)(this.inputMode),(0,f.J)(i),this.handleInputChange,this.onInputBlur)}}])}(c.J);(0,d.__decorate)([(0,u.P)("textarea")],w.prototype,"formElement",void 0),(0,d.__decorate)([(0,u.MZ)({type:Number})],w.prototype,"rows",void 0),(0,d.__decorate)([(0,u.MZ)({type:Number})],w.prototype,"cols",void 0),(0,d.__decorate)([(0,u.MZ)({converter:b})],w.prototype,"charCounter",void 0)},75057:function(e,t,a){a.d(t,{R:function(){return o}});var i,o=(0,a(96196).AH)(i||(i=(e=>e)`.mdc-text-field{height:100%}.mdc-text-field__input{resize:none}`))},3164:function(e,t,a){a.d(t,{A:function(){return o}});a(52675),a(89463),a(16280),a(23792),a(26099),a(62953);var i=a(47075);function o(e){if(null!=e){var t=e["function"==typeof Symbol&&Symbol.iterator||"@@iterator"],a=0;if(t)return t.call(e);if("function"==typeof e.next)return e;if(!isNaN(e.length))return{next:function(){return e&&a>=e.length&&(e=void 0),{value:e&&e[a++],done:!e}}}}throw new TypeError((0,i.A)(e)+" is not iterable")}},99793:function(e,t,a){var i,o=a(96196);t.A=(0,o.AH)(i||(i=(e=>e)`:host {
  --width: 31rem;
  --spacing: var(--wa-space-l);
  --show-duration: 200ms;
  --hide-duration: 200ms;
  display: none;
}
:host([open]) {
  display: block;
}
.dialog {
  display: flex;
  flex-direction: column;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: var(--width);
  max-width: calc(100% - var(--wa-space-2xl));
  max-height: calc(100% - var(--wa-space-2xl));
  background-color: var(--wa-color-surface-raised);
  border-radius: var(--wa-panel-border-radius);
  border: none;
  box-shadow: var(--wa-shadow-l);
  padding: 0;
  margin: auto;
}
.dialog.show {
  animation: show-dialog var(--show-duration) ease;
}
.dialog.show::backdrop {
  animation: show-backdrop var(--show-duration, 200ms) ease;
}
.dialog.hide {
  animation: show-dialog var(--hide-duration) ease reverse;
}
.dialog.hide::backdrop {
  animation: show-backdrop var(--hide-duration, 200ms) ease reverse;
}
.dialog.pulse {
  animation: pulse 250ms ease;
}
.dialog:focus {
  outline: none;
}
@media screen and (max-width: 420px) {
  .dialog {
    max-height: 80vh;
  }
}
.open {
  display: flex;
  opacity: 1;
}
.header {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: nowrap;
  padding-inline-start: var(--spacing);
  padding-block-end: 0;
  padding-inline-end: calc(var(--spacing) - var(--wa-form-control-padding-block));
  padding-block-start: calc(var(--spacing) - var(--wa-form-control-padding-block));
}
.title {
  align-self: center;
  flex: 1 1 auto;
  font-family: inherit;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-heading);
  line-height: var(--wa-line-height-condensed);
  margin: 0;
}
.header-actions {
  align-self: start;
  display: flex;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: end;
  gap: var(--wa-space-2xs);
  padding-inline-start: var(--spacing);
}
.header-actions wa-button,
.header-actions ::slotted(wa-button) {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
}
.body {
  flex: 1 1 auto;
  display: block;
  padding: var(--spacing);
  overflow: auto;
  -webkit-overflow-scrolling: touch;
}
.body:focus {
  outline: none;
}
.body:focus-visible {
  outline: var(--wa-focus-ring);
  outline-offset: var(--wa-focus-ring-offset);
}
.footer {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-xs);
  justify-content: end;
  padding: var(--spacing);
  padding-block-start: 0;
}
.footer ::slotted(wa-button:not(:first-of-type)) {
  margin-inline-start: var(--wa-spacing-xs);
}
.dialog::backdrop {
  background-color: var(--wa-color-overlay-modal, rgb(0 0 0 / 0.25));
}
@keyframes pulse {
  0% {
    scale: 1;
  }
  50% {
    scale: 1.02;
  }
  100% {
    scale: 1;
  }
}
@keyframes show-dialog {
  from {
    opacity: 0;
    scale: 0.8;
  }
  to {
    opacity: 1;
    scale: 1;
  }
}
@keyframes show-backdrop {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@media (forced-colors: active) {
  .dialog {
    border: solid 1px white;
  }
}
`))},93900:function(e,t,a){a.a(e,(async function(e,t){try{var i=a(78261),o=a(61397),n=a(50264),r=a(44734),s=a(56038),l=a(69683),d=a(6454),c=a(25460),h=(a(27495),a(90906),a(96196)),u=a(77845),p=a(94333),f=a(32288),g=a(17051),v=a(42462),b=a(28438),w=a(98779),y=a(27259),m=a(31247),k=a(97039),x=a(92070),$=a(9395),A=a(32510),C=a(17060),D=a(88496),L=a(99793),q=e([D,C]);[D,C]=q.then?(await q)():q;var _,E,M,O=e=>e,J=Object.defineProperty,P=Object.getOwnPropertyDescriptor,Z=(e,t,a,i)=>{for(var o,n=i>1?void 0:i?P(t,a):t,r=e.length-1;r>=0;r--)(o=e[r])&&(n=(i?o(t,a,n):o(n))||n);return i&&n&&J(t,a,n),n},I=function(e){function t(){var e;return(0,r.A)(this,t),(e=(0,l.A)(this,t,arguments)).localize=new C.c(e),e.hasSlotController=new x.X(e,"footer","header-actions","label"),e.open=!1,e.label="",e.withoutHeader=!1,e.lightDismiss=!1,e.handleDocumentKeyDown=t=>{"Escape"===t.key&&e.open&&(t.preventDefault(),t.stopPropagation(),e.requestClose(e.dialog))},e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"firstUpdated",value:function(){this.open&&(this.addOpenListeners(),this.dialog.showModal(),(0,k.JG)(this))}},{key:"disconnectedCallback",value:function(){(0,c.A)(t,"disconnectedCallback",this,3)([]),(0,k.I7)(this),this.removeOpenListeners()}},{key:"requestClose",value:(u=(0,n.A)((0,o.A)().m((function e(t){var a,i;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:if(a=new b.L({source:t}),this.dispatchEvent(a),!a.defaultPrevented){e.n=1;break}return this.open=!0,(0,y.Ud)(this.dialog,"pulse"),e.a(2);case 1:return this.removeOpenListeners(),e.n=2,(0,y.Ud)(this.dialog,"hide");case 2:this.open=!1,this.dialog.close(),(0,k.I7)(this),"function"==typeof(null==(i=this.originalTrigger)?void 0:i.focus)&&setTimeout((()=>i.focus())),this.dispatchEvent(new g.Z);case 3:return e.a(2)}}),e,this)}))),function(e){return u.apply(this,arguments)})},{key:"addOpenListeners",value:function(){document.addEventListener("keydown",this.handleDocumentKeyDown)}},{key:"removeOpenListeners",value:function(){document.removeEventListener("keydown",this.handleDocumentKeyDown)}},{key:"handleDialogCancel",value:function(e){e.preventDefault(),this.dialog.classList.contains("hide")||e.target!==this.dialog||this.requestClose(this.dialog)}},{key:"handleDialogClick",value:function(e){var t=e.target.closest('[data-dialog="close"]');t&&(e.stopPropagation(),this.requestClose(t))}},{key:"handleDialogPointerDown",value:(i=(0,n.A)((0,o.A)().m((function e(t){return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:if(t.target!==this.dialog){e.n=2;break}if(!this.lightDismiss){e.n=1;break}this.requestClose(this.dialog),e.n=2;break;case 1:return e.n=2,(0,y.Ud)(this.dialog,"pulse");case 2:return e.a(2)}}),e,this)}))),function(e){return i.apply(this,arguments)})},{key:"handleOpenChange",value:function(){this.open&&!this.dialog.open?this.show():!this.open&&this.dialog.open&&(this.open=!0,this.requestClose(this.dialog))}},{key:"show",value:(a=(0,n.A)((0,o.A)().m((function e(){var t;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:if(t=new w.k,this.dispatchEvent(t),!t.defaultPrevented){e.n=1;break}return this.open=!1,e.a(2);case 1:return this.addOpenListeners(),this.originalTrigger=document.activeElement,this.open=!0,this.dialog.showModal(),(0,k.JG)(this),requestAnimationFrame((()=>{var e=this.querySelector("[autofocus]");e&&"function"==typeof e.focus?e.focus():this.dialog.focus()})),e.n=2,(0,y.Ud)(this.dialog,"show");case 2:this.dispatchEvent(new v.q);case 3:return e.a(2)}}),e,this)}))),function(){return a.apply(this,arguments)})},{key:"render",value:function(){var e,t=!this.withoutHeader,a=this.hasSlotController.test("footer");return(0,h.qy)(_||(_=O`
      <dialog
        aria-labelledby=${0}
        aria-describedby=${0}
        part="dialog"
        class=${0}
        @cancel=${0}
        @click=${0}
        @pointerdown=${0}
      >
        ${0}

        <div part="body" class="body"><slot></slot></div>

        ${0}
      </dialog>
    `),null!==(e=this.ariaLabelledby)&&void 0!==e?e:"title",(0,f.J)(this.ariaDescribedby),(0,p.H)({dialog:!0,open:this.open}),this.handleDialogCancel,this.handleDialogClick,this.handleDialogPointerDown,t?(0,h.qy)(E||(E=O`
              <header part="header" class="header">
                <h2 part="title" class="title" id="title">
                  <!-- If there's no label, use an invisible character to prevent the header from collapsing -->
                  <slot name="label"> ${0} </slot>
                </h2>
                <div part="header-actions" class="header-actions">
                  <slot name="header-actions"></slot>
                  <wa-button
                    part="close-button"
                    exportparts="base:close-button__base"
                    class="close"
                    appearance="plain"
                    @click="${0}"
                  >
                    <wa-icon
                      name="xmark"
                      label=${0}
                      library="system"
                      variant="solid"
                    ></wa-icon>
                  </wa-button>
                </div>
              </header>
            `),this.label.length>0?this.label:String.fromCharCode(8203),(e=>this.requestClose(e.target)),this.localize.term("close")):"",a?(0,h.qy)(M||(M=O`
              <footer part="footer" class="footer">
                <slot name="footer"></slot>
              </footer>
            `)):"")}}]);var a,i,u}(A.A);I.css=L.A,Z([(0,u.P)(".dialog")],I.prototype,"dialog",2),Z([(0,u.MZ)({type:Boolean,reflect:!0})],I.prototype,"open",2),Z([(0,u.MZ)({reflect:!0})],I.prototype,"label",2),Z([(0,u.MZ)({attribute:"without-header",type:Boolean,reflect:!0})],I.prototype,"withoutHeader",2),Z([(0,u.MZ)({attribute:"light-dismiss",type:Boolean})],I.prototype,"lightDismiss",2),Z([(0,u.MZ)({attribute:"aria-labelledby"})],I.prototype,"ariaLabelledby",2),Z([(0,u.MZ)({attribute:"aria-describedby"})],I.prototype,"ariaDescribedby",2),Z([(0,$.w)("open",{waitUntilFirstUpdate:!0})],I.prototype,"handleOpenChange",1),I=Z([(0,u.EM)("wa-dialog")],I),document.addEventListener("click",(e=>{var t=e.target.closest("[data-dialog]");if(t instanceof Element){var a=(0,m.v)(t.getAttribute("data-dialog")||""),o=(0,i.A)(a,2),n=o[0],r=o[1];if("open"===n&&null!=r&&r.length){var s=t.getRootNode().getElementById(r);"wa-dialog"===(null==s?void 0:s.localName)?s.open=!0:console.warn(`A dialog with an ID of "${r}" could not be found in this document.`)}}})),h.S$||document.addEventListener("pointerdown",(()=>{})),t()}catch(z){t(z)}}))}}]);
//# sourceMappingURL=2993.8dd0c16964cc2a72.js.map