/*! For license information please see 5580.567c97285140713f.js.LICENSE.txt */
export const __webpack_id__="5580";export const __webpack_ids__=["5580"];export const __webpack_modules__={371:function(t,i,o){o.r(i),o.d(i,{HaIconButtonArrowPrev:()=>n});var e=o(62826),s=o(96196),a=o(77845),r=o(76679);o(60733);class n extends s.WF{render(){return s.qy`
      <ha-icon-button
        .disabled=${this.disabled}
        .label=${this.label||this.hass?.localize("ui.common.back")||"Back"}
        .path=${this._icon}
      ></ha-icon-button>
    `}constructor(...t){super(...t),this.disabled=!1,this._icon="rtl"===r.G.document.dir?"M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z":"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"}}(0,e.__decorate)([(0,a.MZ)({attribute:!1})],n.prototype,"hass",void 0),(0,e.__decorate)([(0,a.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,e.__decorate)([(0,a.MZ)()],n.prototype,"label",void 0),(0,e.__decorate)([(0,a.wk)()],n.prototype,"_icon",void 0),n=(0,e.__decorate)([(0,a.EM)("ha-icon-button-arrow-prev")],n)},60733:function(t,i,o){o.r(i),o.d(i,{HaIconButton:()=>n});var e=o(62826),s=(o(11677),o(96196)),a=o(77845),r=o(32288);o(60961);class n extends s.WF{focus(){this._button?.focus()}render(){return s.qy`
      <mwc-icon-button
        aria-label=${(0,r.J)(this.label)}
        title=${(0,r.J)(this.hideTitle?void 0:this.label)}
        aria-haspopup=${(0,r.J)(this.ariaHasPopup)}
        .disabled=${this.disabled}
      >
        ${this.path?s.qy`<ha-svg-icon .path=${this.path}></ha-svg-icon>`:s.qy`<slot></slot>`}
      </mwc-icon-button>
    `}constructor(...t){super(...t),this.disabled=!1,this.hideTitle=!1}}n.shadowRootOptions={mode:"open",delegatesFocus:!0},n.styles=s.AH`
    :host {
      display: inline-block;
      outline: none;
    }
    :host([disabled]) {
      pointer-events: none;
    }
    mwc-icon-button {
      --mdc-theme-on-primary: currentColor;
      --mdc-theme-text-disabled-on-light: var(--disabled-text-color);
    }
  `,(0,e.__decorate)([(0,a.MZ)({type:Boolean,reflect:!0})],n.prototype,"disabled",void 0),(0,e.__decorate)([(0,a.MZ)({type:String})],n.prototype,"path",void 0),(0,e.__decorate)([(0,a.MZ)({type:String})],n.prototype,"label",void 0),(0,e.__decorate)([(0,a.MZ)({type:String,attribute:"aria-haspopup"})],n.prototype,"ariaHasPopup",void 0),(0,e.__decorate)([(0,a.MZ)({attribute:"hide-title",type:Boolean})],n.prototype,"hideTitle",void 0),(0,e.__decorate)([(0,a.P)("mwc-icon-button",!0)],n.prototype,"_button",void 0),n=(0,e.__decorate)([(0,a.EM)("ha-icon-button")],n)},45397:function(t,i,o){var e=o(62826),s=o(96196),a=o(77845),r=o(92542);class n{processMessage(t){if("removed"===t.type)for(const i of Object.keys(t.notifications))delete this.notifications[i];else this.notifications={...this.notifications,...t.notifications};return Object.values(this.notifications)}constructor(){this.notifications={}}}o(60733);class c extends s.WF{connectedCallback(){super.connectedCallback(),this._attachNotifOnConnect&&(this._attachNotifOnConnect=!1,this._subscribeNotifications())}disconnectedCallback(){super.disconnectedCallback(),this._unsubNotifications&&(this._attachNotifOnConnect=!0,this._unsubNotifications(),this._unsubNotifications=void 0)}render(){if(!this._show)return s.s6;const t=this._hasNotifications&&(this.narrow||"always_hidden"===this.hass.dockedSidebar);return s.qy`
      <ha-icon-button
        .label=${this.hass.localize("ui.sidebar.sidebar_toggle")}
        .path=${"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"}
        @click=${this._toggleMenu}
      ></ha-icon-button>
      ${t?s.qy`<div class="dot"></div>`:""}
    `}firstUpdated(t){super.firstUpdated(t),this.hassio&&(this._alwaysVisible=(Number(window.parent.frontendVersion)||0)<20190710)}willUpdate(t){if(super.willUpdate(t),!t.has("narrow")&&!t.has("hass"))return;const i=t.has("hass")?t.get("hass"):this.hass,o=(t.has("narrow")?t.get("narrow"):this.narrow)||"always_hidden"===i?.dockedSidebar,e=this.narrow||"always_hidden"===this.hass.dockedSidebar;this.hasUpdated&&o===e||(this._show=e||this._alwaysVisible,e?this._subscribeNotifications():this._unsubNotifications&&(this._unsubNotifications(),this._unsubNotifications=void 0))}_subscribeNotifications(){if(this._unsubNotifications)throw new Error("Already subscribed");this._unsubNotifications=((t,i)=>{const o=new n,e=t.subscribeMessage((t=>i(o.processMessage(t))),{type:"persistent_notification/subscribe"});return()=>{e.then((t=>t?.()))}})(this.hass.connection,(t=>{this._hasNotifications=t.length>0}))}_toggleMenu(){(0,r.r)(this,"hass-toggle-menu")}constructor(...t){super(...t),this.hassio=!1,this.narrow=!1,this._hasNotifications=!1,this._show=!1,this._alwaysVisible=!1,this._attachNotifOnConnect=!1}}c.styles=s.AH`
    :host {
      position: relative;
    }
    .dot {
      pointer-events: none;
      position: absolute;
      background-color: var(--accent-color);
      width: 12px;
      height: 12px;
      top: 9px;
      right: 7px;
      inset-inline-end: 7px;
      inset-inline-start: initial;
      border-radius: var(--ha-border-radius-circle);
      border: 2px solid var(--app-header-background-color);
    }
  `,(0,e.__decorate)([(0,a.MZ)({type:Boolean})],c.prototype,"hassio",void 0),(0,e.__decorate)([(0,a.MZ)({type:Boolean})],c.prototype,"narrow",void 0),(0,e.__decorate)([(0,a.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,e.__decorate)([(0,a.wk)()],c.prototype,"_hasNotifications",void 0),(0,e.__decorate)([(0,a.wk)()],c.prototype,"_show",void 0),c=(0,e.__decorate)([(0,a.EM)("ha-menu-button")],c)},60961:function(t,i,o){o.r(i),o.d(i,{HaSvgIcon:()=>r});var e=o(62826),s=o(96196),a=o(77845);class r extends s.WF{render(){return s.JW`
    <svg
      viewBox=${this.viewBox||"0 0 24 24"}
      preserveAspectRatio="xMidYMid meet"
      focusable="false"
      role="img"
      aria-hidden="true"
    >
      <g>
        ${this.path?s.JW`<path class="primary-path" d=${this.path}></path>`:s.s6}
        ${this.secondaryPath?s.JW`<path class="secondary-path" d=${this.secondaryPath}></path>`:s.s6}
      </g>
    </svg>`}}r.styles=s.AH`
    :host {
      display: var(--ha-icon-display, inline-flex);
      align-items: center;
      justify-content: center;
      position: relative;
      vertical-align: middle;
      fill: var(--icon-primary-color, currentcolor);
      width: var(--mdc-icon-size, 24px);
      height: var(--mdc-icon-size, 24px);
    }
    svg {
      width: 100%;
      height: 100%;
      pointer-events: none;
      display: block;
    }
    path.primary-path {
      opacity: var(--icon-primary-opactity, 1);
    }
    path.secondary-path {
      fill: var(--icon-secondary-color, currentcolor);
      opacity: var(--icon-secondary-opactity, 0.5);
    }
  `,(0,e.__decorate)([(0,a.MZ)()],r.prototype,"path",void 0),(0,e.__decorate)([(0,a.MZ)({attribute:!1})],r.prototype,"secondaryPath",void 0),(0,e.__decorate)([(0,a.MZ)({attribute:!1})],r.prototype,"viewBox",void 0),r=(0,e.__decorate)([(0,a.EM)("ha-svg-icon")],r)},28345:function(t,i,o){o.d(i,{qy:()=>d,eu:()=>r});var e=o(5055);const s=Symbol.for(""),a=t=>{if(t?.r===s)return t?._$litStatic$},r=(t,...i)=>({_$litStatic$:i.reduce(((i,o,e)=>i+(t=>{if(void 0!==t._$litStatic$)return t._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${t}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(o)+t[e+1]),t[0]),r:s}),n=new Map,c=t=>(i,...o)=>{const e=o.length;let s,r;const c=[],d=[];let h,l=0,p=!1;for(;l<e;){for(h=i[l];l<e&&void 0!==(r=o[l],s=a(r));)h+=s+i[++l],p=!0;l!==e&&d.push(r),c.push(h),l++}if(l===e&&c.push(i[e]),p){const t=c.join("$$lit$$");void 0===(i=n.get(t))&&(c.raw=c,n.set(t,i=c)),o=d}return t(i,...o)},d=c(e.qy);c(e.JW),c(e.ej)}};
//# sourceMappingURL=5580.567c97285140713f.js.map