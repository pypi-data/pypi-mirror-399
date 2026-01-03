export const __webpack_id__="4310";export const __webpack_ids__=["4310"];export const __webpack_modules__={55124:function(t,e,o){o.d(e,{d:()=>i});const i=t=>t.stopPropagation()},87400:function(t,e,o){o.d(e,{l:()=>i});const i=(t,e,o,i,a)=>{const s=e[t.entity_id];return s?r(s,e,o,i,a):{entity:null,device:null,area:null,floor:null}},r=(t,e,o,i,r)=>{const a=e[t.entity_id],s=t?.device_id,n=s?o[s]:void 0,l=t?.area_id||n?.area_id,h=l?i[l]:void 0,p=h?.floor_id;return{entity:a,device:n||null,area:h||null,floor:(p?r[p]:void 0)||null}}},27075:function(t,e,o){o.a(t,(async function(t,i){try{o.r(e),o.d(e,{HaTemplateSelector:()=>c});var r=o(62826),a=o(96196),s=o(77845),n=o(92542),l=o(62001),h=o(32884),p=(o(56768),o(17963),t([h]));h=(p.then?(await p)():p)[0];const d=["template:","sensor:","state:","trigger: template"];class c extends a.WF{render(){return a.qy`
      ${this.warn?a.qy`<ha-alert alert-type="warning"
            >${this.hass.localize("ui.components.selectors.template.yaml_warning",{string:this.warn})}
            <br />
            <a
              target="_blank"
              rel="noopener noreferrer"
              href=${(0,l.o)(this.hass,"/docs/configuration/templating/")}
              >${this.hass.localize("ui.components.selectors.template.learn_more")}</a
            ></ha-alert
          >`:a.s6}
      ${this.label?a.qy`<p>${this.label}${this.required?"*":""}</p>`:a.s6}
      <ha-code-editor
        mode="jinja2"
        .hass=${this.hass}
        .value=${this.value}
        .readOnly=${this.disabled}
        .placeholder=${this.placeholder||"{{ ... }}"}
        autofocus
        autocomplete-entities
        autocomplete-icons
        @value-changed=${this._handleChange}
        dir="ltr"
        linewrap
      ></ha-code-editor>
      ${this.helper?a.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:a.s6}
    `}_handleChange(t){t.stopPropagation();let e=t.target.value;this.value!==e&&(this.warn=d.find((t=>e.includes(t))),""!==e||this.required||(e=void 0),(0,n.r)(this,"value-changed",{value:e}))}constructor(...t){super(...t),this.disabled=!1,this.required=!0,this.warn=void 0}}c.styles=a.AH`
    p {
      margin-top: 0;
    }
  `,(0,r.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,r.__decorate)([(0,s.MZ)()],c.prototype,"value",void 0),(0,r.__decorate)([(0,s.MZ)()],c.prototype,"label",void 0),(0,r.__decorate)([(0,s.MZ)()],c.prototype,"helper",void 0),(0,r.__decorate)([(0,s.MZ)()],c.prototype,"placeholder",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],c.prototype,"required",void 0),(0,r.__decorate)([(0,s.wk)()],c.prototype,"warn",void 0),c=(0,r.__decorate)([(0,s.EM)("ha-selector-template")],c),i()}catch(d){i(d)}}))},88422:function(t,e,o){o.a(t,(async function(t,e){try{var i=o(62826),r=o(52630),a=o(96196),s=o(77845),n=t([r]);r=(n.then?(await n)():n)[0];class l extends r.A{static get styles(){return[r.A.styles,a.AH`
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
      `]}constructor(...t){super(...t),this.showDelay=150,this.hideDelay=150}}(0,i.__decorate)([(0,s.MZ)({attribute:"show-delay",type:Number})],l.prototype,"showDelay",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"hide-delay",type:Number})],l.prototype,"hideDelay",void 0),l=(0,i.__decorate)([(0,s.EM)("ha-tooltip")],l),e()}catch(l){e(l)}}))},62001:function(t,e,o){o.d(e,{o:()=>i});const i=(t,e)=>`https://${t.config.version.includes("b")?"rc":t.config.version.includes("dev")?"next":"www"}.home-assistant.io${e}`},4848:function(t,e,o){o.d(e,{P:()=>r});var i=o(92542);const r=(t,e)=>(0,i.r)(t,"hass-notification",e)},61171:function(t,e,o){o.d(e,{A:()=>i});const i=o(96196).AH`:host {
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
`},52630:function(t,e,o){o.a(t,(async function(t,i){try{o.d(e,{A:()=>k});var r=o(96196),a=o(77845),s=o(94333),n=o(17051),l=o(42462),h=o(28438),p=o(98779),d=o(27259),c=o(984),u=o(53720),v=o(9395),w=o(32510),y=o(40158),b=o(61171),g=t([y]);y=(g.then?(await g)():g)[0];var m=Object.defineProperty,f=Object.getOwnPropertyDescriptor,_=(t,e,o,i)=>{for(var r,a=i>1?void 0:i?f(e,o):e,s=t.length-1;s>=0;s--)(r=t[s])&&(a=(i?r(e,o,a):r(a))||a);return i&&a&&m(e,o,a),a};let k=class extends w.A{connectedCallback(){super.connectedCallback(),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,u.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}disconnectedCallback(){super.disconnectedCallback(),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}firstUpdated(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}hasTrigger(t){return this.trigger.split(" ").includes(t)}addToAriaLabelledBy(t,e){const o=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);o.includes(e)||(o.push(e),t.setAttribute("aria-labelledby",o.join(" ")))}removeFromAriaLabelledBy(t,e){const o=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((t=>t!==e));o.length>0?t.setAttribute("aria-labelledby",o.join(" ")):t.removeAttribute("aria-labelledby")}async handleOpenChange(){if(this.open){if(this.disabled)return;const t=new p.k;if(this.dispatchEvent(t),t.defaultPrevented)return void(this.open=!1);document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,await(0,d.Ud)(this.popup.popup,"show-with-scale"),this.popup.reposition(),this.dispatchEvent(new l.q)}else{const t=new h.L;if(this.dispatchEvent(t),t.defaultPrevented)return void(this.open=!1);document.removeEventListener("keydown",this.handleDocumentKeyDown),await(0,d.Ud)(this.popup.popup,"hide-with-scale"),this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new n.Z)}}handleForChange(){const t=this.getRootNode();if(!t)return;const e=this.for?t.getElementById(this.for):null,o=this.anchor;if(e===o)return;const{signal:i}=this.eventController;e&&(this.addToAriaLabelledBy(e,this.id),e.addEventListener("blur",this.handleBlur,{capture:!0,signal:i}),e.addEventListener("focus",this.handleFocus,{capture:!0,signal:i}),e.addEventListener("click",this.handleClick,{signal:i}),e.addEventListener("mouseover",this.handleMouseOver,{signal:i}),e.addEventListener("mouseout",this.handleMouseOut,{signal:i})),o&&(this.removeFromAriaLabelledBy(o,this.id),o.removeEventListener("blur",this.handleBlur,{capture:!0}),o.removeEventListener("focus",this.handleFocus,{capture:!0}),o.removeEventListener("click",this.handleClick),o.removeEventListener("mouseover",this.handleMouseOver),o.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=e}async handleOptionsChange(){this.hasUpdated&&(await this.updateComplete,this.popup.reposition())}handleDisabledChange(){this.disabled&&this.open&&this.hide()}async show(){if(!this.open)return this.open=!0,(0,c.l)(this,"wa-after-show")}async hide(){if(this.open)return this.open=!1,(0,c.l)(this,"wa-after-hide")}render(){return r.qy`
      <wa-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${(0,s.H)({tooltip:!0,"tooltip-open":this.open})}
        placement=${this.placement}
        distance=${this.distance}
        skidding=${this.skidding}
        flip
        shift
        ?arrow=${!this.withoutArrow}
        hover-bridge
        .anchor=${this.anchor}
      >
        <div part="body" class="body">
          <slot></slot>
        </div>
      </wa-popup>
    `}constructor(){super(...arguments),this.placement="top",this.disabled=!1,this.distance=8,this.open=!1,this.skidding=0,this.showDelay=150,this.hideDelay=0,this.trigger="hover focus",this.withoutArrow=!1,this.for=null,this.anchor=null,this.eventController=new AbortController,this.handleBlur=()=>{this.hasTrigger("focus")&&this.hide()},this.handleClick=()=>{this.hasTrigger("click")&&(this.open?this.hide():this.show())},this.handleFocus=()=>{this.hasTrigger("focus")&&this.show()},this.handleDocumentKeyDown=t=>{"Escape"===t.key&&(t.stopPropagation(),this.hide())},this.handleMouseOver=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.show()),this.showDelay))},this.handleMouseOut=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.hide()),this.hideDelay))}}};k.css=b.A,k.dependencies={"wa-popup":y.A},_([(0,a.P)("slot:not([name])")],k.prototype,"defaultSlot",2),_([(0,a.P)(".body")],k.prototype,"body",2),_([(0,a.P)("wa-popup")],k.prototype,"popup",2),_([(0,a.MZ)()],k.prototype,"placement",2),_([(0,a.MZ)({type:Boolean,reflect:!0})],k.prototype,"disabled",2),_([(0,a.MZ)({type:Number})],k.prototype,"distance",2),_([(0,a.MZ)({type:Boolean,reflect:!0})],k.prototype,"open",2),_([(0,a.MZ)({type:Number})],k.prototype,"skidding",2),_([(0,a.MZ)({attribute:"show-delay",type:Number})],k.prototype,"showDelay",2),_([(0,a.MZ)({attribute:"hide-delay",type:Number})],k.prototype,"hideDelay",2),_([(0,a.MZ)()],k.prototype,"trigger",2),_([(0,a.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],k.prototype,"withoutArrow",2),_([(0,a.MZ)()],k.prototype,"for",2),_([(0,a.wk)()],k.prototype,"anchor",2),_([(0,v.w)("open",{waitUntilFirstUpdate:!0})],k.prototype,"handleOpenChange",1),_([(0,v.w)("for")],k.prototype,"handleForChange",1),_([(0,v.w)(["distance","placement","skidding"])],k.prototype,"handleOptionsChange",1),_([(0,v.w)("disabled")],k.prototype,"handleDisabledChange",1),k=_([(0,a.EM)("wa-tooltip")],k),i()}catch(k){i(k)}}))}};
//# sourceMappingURL=4310.86a3e03f8023039d.js.map