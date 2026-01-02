"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6359"],{95379:function(t,a,o){var e,i,r,n=o(44734),s=o(56038),c=o(69683),d=o(6454),h=(o(28706),o(62826)),l=o(96196),p=o(77845),u=t=>t,v=function(t){function a(){var t;(0,n.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,c.A)(this,a,[].concat(e))).raised=!1,t}return(0,d.A)(a,t),(0,s.A)(a,[{key:"render",value:function(){return(0,l.qy)(e||(e=u`
      ${0}
      <slot></slot>
    `),this.header?(0,l.qy)(i||(i=u`<h1 class="card-header">${0}</h1>`),this.header):l.s6)}}])}(l.WF);v.styles=(0,l.AH)(r||(r=u`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4);
      display: block;
      margin-block-start: var(--ha-space-0);
      margin-block-end: var(--ha-space-0);
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: var(--ha-space-0);
      margin-top: calc(var(--ha-space-2) * -1);
    }

    :host ::slotted(.card-content) {
      padding: var(--ha-space-4);
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: var(--ha-space-2);
    }
  `)),(0,h.__decorate)([(0,p.MZ)()],v.prototype,"header",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],v.prototype,"raised",void 0),v=(0,h.__decorate)([(0,p.EM)("ha-card")],v)},60733:function(t,a,o){o.r(a),o.d(a,{HaIconButton:function(){return y}});var e,i,r,n,s=o(44734),c=o(56038),d=o(69683),h=o(6454),l=(o(28706),o(62826)),p=(o(11677),o(96196)),u=o(77845),v=o(32288),f=(o(60961),t=>t),y=function(t){function a(){var t;(0,s.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,d.A)(this,a,[].concat(e))).disabled=!1,t.hideTitle=!1,t}return(0,h.A)(a,t),(0,c.A)(a,[{key:"focus",value:function(){var t;null===(t=this._button)||void 0===t||t.focus()}},{key:"render",value:function(){return(0,p.qy)(e||(e=f`
      <mwc-icon-button
        aria-label=${0}
        title=${0}
        aria-haspopup=${0}
        .disabled=${0}
      >
        ${0}
      </mwc-icon-button>
    `),(0,v.J)(this.label),(0,v.J)(this.hideTitle?void 0:this.label),(0,v.J)(this.ariaHasPopup),this.disabled,this.path?(0,p.qy)(i||(i=f`<ha-svg-icon .path=${0}></ha-svg-icon>`),this.path):(0,p.qy)(r||(r=f`<slot></slot>`)))}}])}(p.WF);y.shadowRootOptions={mode:"open",delegatesFocus:!0},y.styles=(0,p.AH)(n||(n=f`
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
  `)),(0,l.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0})],y.prototype,"disabled",void 0),(0,l.__decorate)([(0,u.MZ)({type:String})],y.prototype,"path",void 0),(0,l.__decorate)([(0,u.MZ)({type:String})],y.prototype,"label",void 0),(0,l.__decorate)([(0,u.MZ)({type:String,attribute:"aria-haspopup"})],y.prototype,"ariaHasPopup",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"hide-title",type:Boolean})],y.prototype,"hideTitle",void 0),(0,l.__decorate)([(0,u.P)("mwc-icon-button",!0)],y.prototype,"_button",void 0),y=(0,l.__decorate)([(0,u.EM)("ha-icon-button")],y)},28608:function(t,a,o){o.r(a),o.d(a,{HaIconNext:function(){return l}});var e=o(56038),i=o(44734),r=o(69683),n=o(6454),s=(o(28706),o(62826)),c=o(77845),d=o(76679),h=o(60961),l=function(t){function a(){var t;(0,i.A)(this,a);for(var o=arguments.length,e=new Array(o),n=0;n<o;n++)e[n]=arguments[n];return(t=(0,r.A)(this,a,[].concat(e))).path="rtl"===d.G.document.dir?"M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z":"M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z",t}return(0,n.A)(a,t),(0,e.A)(a)}(h.HaSvgIcon);(0,s.__decorate)([(0,c.MZ)()],l.prototype,"path",void 0),l=(0,s.__decorate)([(0,c.EM)("ha-icon-next")],l)},23897:function(t,a,o){o.d(a,{G:function(){return y},J:function(){return f}});var e,i,r=o(44734),n=o(56038),s=o(69683),c=o(6454),d=o(62826),h=o(97154),l=o(82553),p=o(96196),u=o(77845),v=(o(95591),t=>t),f=[l.R,(0,p.AH)(e||(e=v`
    :host {
      --ha-icon-display: block;
      --md-sys-color-primary: var(--primary-text-color);
      --md-sys-color-secondary: var(--secondary-text-color);
      --md-sys-color-surface: var(--card-background-color);
      --md-sys-color-on-surface: var(--primary-text-color);
      --md-sys-color-on-surface-variant: var(--secondary-text-color);
    }
    md-item {
      overflow: var(--md-item-overflow, hidden);
      align-items: var(--md-item-align-items, center);
      gap: var(--ha-md-list-item-gap, 16px);
    }
  `))],y=function(t){function a(){return(0,r.A)(this,a),(0,s.A)(this,a,arguments)}return(0,c.A)(a,t),(0,n.A)(a,[{key:"renderRipple",value:function(){return"text"===this.type?p.s6:(0,p.qy)(i||(i=v`<ha-ripple
      part="ripple"
      for="item"
      ?disabled=${0}
    ></ha-ripple>`),this.disabled&&"link"!==this.type)}}])}(h.n);y.styles=f,y=(0,d.__decorate)([(0,u.EM)("ha-md-list-item")],y)},42921:function(t,a,o){var e,i=o(56038),r=o(44734),n=o(69683),s=o(6454),c=o(62826),d=o(49838),h=o(11245),l=o(96196),p=o(77845),u=function(t){function a(){return(0,r.A)(this,a),(0,n.A)(this,a,arguments)}return(0,s.A)(a,t),(0,i.A)(a)}(d.B);u.styles=[h.R,(0,l.AH)(e||(e=(t=>t)`
      :host {
        --md-sys-color-surface: var(--card-background-color);
      }
    `))],u=(0,c.__decorate)([(0,p.EM)("ha-md-list")],u)},45397:function(t,a,o){var e,i,r,n=o(44734),s=o(56038),c=o(69683),d=o(6454),h=o(25460),l=(o(16280),o(28706),o(2892),o(62826)),p=o(96196),u=o(77845),v=o(92542),f=(o(16034),function(){return(0,s.A)((function t(){(0,n.A)(this,t),this.notifications={}}),[{key:"processMessage",value:function(t){if("removed"===t.type)for(var a=0,o=Object.keys(t.notifications);a<o.length;a++){var e=o[a];delete this.notifications[e]}else this.notifications=Object.assign(Object.assign({},this.notifications),t.notifications);return Object.values(this.notifications)}}])}()),y=(o(60733),t=>t),g=function(t){function a(){var t;(0,n.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,c.A)(this,a,[].concat(e))).hassio=!1,t.narrow=!1,t._hasNotifications=!1,t._show=!1,t._alwaysVisible=!1,t._attachNotifOnConnect=!1,t}return(0,d.A)(a,t),(0,s.A)(a,[{key:"connectedCallback",value:function(){(0,h.A)(a,"connectedCallback",this,3)([]),this._attachNotifOnConnect&&(this._attachNotifOnConnect=!1,this._subscribeNotifications())}},{key:"disconnectedCallback",value:function(){(0,h.A)(a,"disconnectedCallback",this,3)([]),this._unsubNotifications&&(this._attachNotifOnConnect=!0,this._unsubNotifications(),this._unsubNotifications=void 0)}},{key:"render",value:function(){if(!this._show)return p.s6;var t=this._hasNotifications&&(this.narrow||"always_hidden"===this.hass.dockedSidebar);return(0,p.qy)(e||(e=y`
      <ha-icon-button
        .label=${0}
        .path=${0}
        @click=${0}
      ></ha-icon-button>
      ${0}
    `),this.hass.localize("ui.sidebar.sidebar_toggle"),"M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z",this._toggleMenu,t?(0,p.qy)(i||(i=y`<div class="dot"></div>`)):"")}},{key:"firstUpdated",value:function(t){(0,h.A)(a,"firstUpdated",this,3)([t]),this.hassio&&(this._alwaysVisible=(Number(window.parent.frontendVersion)||0)<20190710)}},{key:"willUpdate",value:function(t){if((0,h.A)(a,"willUpdate",this,3)([t]),t.has("narrow")||t.has("hass")){var o=t.has("hass")?t.get("hass"):this.hass,e=(t.has("narrow")?t.get("narrow"):this.narrow)||"always_hidden"===(null==o?void 0:o.dockedSidebar),i=this.narrow||"always_hidden"===this.hass.dockedSidebar;this.hasUpdated&&e===i||(this._show=i||this._alwaysVisible,i?this._subscribeNotifications():this._unsubNotifications&&(this._unsubNotifications(),this._unsubNotifications=void 0))}}},{key:"_subscribeNotifications",value:function(){if(this._unsubNotifications)throw new Error("Already subscribed");var t,a,o,e;this._unsubNotifications=(t=this.hass.connection,a=t=>{this._hasNotifications=t.length>0},o=new f,e=t.subscribeMessage((t=>a(o.processMessage(t))),{type:"persistent_notification/subscribe"}),()=>{e.then((t=>null==t?void 0:t()))})}},{key:"_toggleMenu",value:function(){(0,v.r)(this,"hass-toggle-menu")}}])}(p.WF);g.styles=(0,p.AH)(r||(r=y`
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
  `)),(0,l.__decorate)([(0,u.MZ)({type:Boolean})],g.prototype,"hassio",void 0),(0,l.__decorate)([(0,u.MZ)({type:Boolean})],g.prototype,"narrow",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,l.__decorate)([(0,u.wk)()],g.prototype,"_hasNotifications",void 0),(0,l.__decorate)([(0,u.wk)()],g.prototype,"_show",void 0),g=(0,l.__decorate)([(0,u.EM)("ha-menu-button")],g)},65300:function(t,a,o){var e,i,r,n,s,c=o(44734),d=o(56038),h=o(69683),l=o(6454),p=(o(52675),o(89463),o(28706),o(62062),o(18111),o(61701),o(26099),o(62826)),u=o(96196),v=o(77845),f=o(32288),y=(o(28608),o(42921),o(23897),o(60961),t=>t),g=function(t){function a(){var t;(0,c.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,h.A)(this,a,[].concat(e))).narrow=!1,t.hasSecondary=!1,t}return(0,l.A)(a,t),(0,d.A)(a,[{key:"render",value:function(){return(0,u.qy)(e||(e=y`
      <ha-md-list
        innerRole="menu"
        itemRoles="menuitem"
        innerAriaLabel=${0}
      >
        ${0}
      </ha-md-list>
    `),(0,f.J)(this.label),this.pages.map((t=>{var a=t.path.endsWith("#external-app-configuration");return(0,u.qy)(i||(i=y`
            <ha-md-list-item
              .type=${0}
              .href=${0}
              @click=${0}
            >
              <div
                slot="start"
                class=${0}
                .style="background-color: ${0}"
              >
                <ha-svg-icon .path=${0}></ha-svg-icon>
              </div>
              <span slot="headline">${0}</span>
              ${0}
              ${0}
            </ha-md-list-item>
          `),a?"button":"link",a?void 0:t.path,a?this._handleExternalApp:void 0,t.iconColor?"icon-background":"",t.iconColor||"undefined",t.iconPath,t.name,this.hasSecondary?(0,u.qy)(r||(r=y`<span slot="supporting-text">${0}</span>`),t.description):"",this.narrow?"":(0,u.qy)(n||(n=y`<ha-icon-next slot="end"></ha-icon-next>`)))})))}},{key:"_handleExternalApp",value:function(){this.hass.auth.external.fireMessage({type:"config_screen/show"})}}])}(u.WF);g.styles=(0,u.AH)(s||(s=y`
    ha-svg-icon,
    ha-icon-next {
      color: var(--secondary-text-color);
      height: 24px;
      width: 24px;
      display: block;
    }
    ha-svg-icon {
      padding: 8px;
    }
    .icon-background {
      border-radius: var(--ha-border-radius-circle);
    }
    .icon-background ha-svg-icon {
      color: #fff;
    }
    ha-md-list-item {
      font-size: var(--navigation-list-item-title-font-size);
    }
  `)),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean})],g.prototype,"narrow",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],g.prototype,"pages",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:"has-secondary",type:Boolean})],g.prototype,"hasSecondary",void 0),(0,p.__decorate)([(0,v.MZ)()],g.prototype,"label",void 0),g=(0,p.__decorate)([(0,v.EM)("ha-navigation-list")],g)},95591:function(t,a,o){var e,i=o(44734),r=o(56038),n=o(75864),s=o(69683),c=o(6454),d=o(25460),h=(o(28706),o(62826)),l=o(76482),p=o(91382),u=o(96245),v=o(96196),f=o(77845),y=function(t){function a(){var t;(0,i.A)(this,a);for(var o=arguments.length,e=new Array(o),r=0;r<o;r++)e[r]=arguments[r];return(t=(0,s.A)(this,a,[].concat(e))).attachableTouchController=new l.i((0,n.A)(t),t._onTouchControlChange.bind((0,n.A)(t))),t._handleTouchEnd=()=>{t.disabled||(0,d.A)(((0,n.A)(t),a),"endPressAnimation",t,3)([])},t}return(0,c.A)(a,t),(0,r.A)(a,[{key:"attach",value:function(t){(0,d.A)(a,"attach",this,3)([t]),this.attachableTouchController.attach(t)}},{key:"disconnectedCallback",value:function(){(0,d.A)(a,"disconnectedCallback",this,3)([]),this.hovered=!1,this.pressed=!1}},{key:"detach",value:function(){(0,d.A)(a,"detach",this,3)([]),this.attachableTouchController.detach()}},{key:"_onTouchControlChange",value:function(t,a){null==t||t.removeEventListener("touchend",this._handleTouchEnd),null==a||a.addEventListener("touchend",this._handleTouchEnd)}}])}(p.n);y.styles=[u.R,(0,v.AH)(e||(e=(t=>t)`
      :host {
        --md-ripple-hover-opacity: var(--ha-ripple-hover-opacity, 0.08);
        --md-ripple-pressed-opacity: var(--ha-ripple-pressed-opacity, 0.12);
        --md-ripple-hover-color: var(
          --ha-ripple-hover-color,
          var(--ha-ripple-color, var(--secondary-text-color))
        );
        --md-ripple-pressed-color: var(
          --ha-ripple-pressed-color,
          var(--ha-ripple-color, var(--secondary-text-color))
        );
      }
    `))],y=(0,h.__decorate)([(0,f.EM)("ha-ripple")],y)},60961:function(t,a,o){o.r(a),o.d(a,{HaSvgIcon:function(){return f}});var e,i,r,n,s=o(44734),c=o(56038),d=o(69683),h=o(6454),l=o(62826),p=o(96196),u=o(77845),v=t=>t,f=function(t){function a(){return(0,s.A)(this,a),(0,d.A)(this,a,arguments)}return(0,h.A)(a,t),(0,c.A)(a,[{key:"render",value:function(){return(0,p.JW)(e||(e=v`
    <svg
      viewBox=${0}
      preserveAspectRatio="xMidYMid meet"
      focusable="false"
      role="img"
      aria-hidden="true"
    >
      <g>
        ${0}
        ${0}
      </g>
    </svg>`),this.viewBox||"0 0 24 24",this.path?(0,p.JW)(i||(i=v`<path class="primary-path" d=${0}></path>`),this.path):p.s6,this.secondaryPath?(0,p.JW)(r||(r=v`<path class="secondary-path" d=${0}></path>`),this.secondaryPath):p.s6)}}])}(p.WF);f.styles=(0,p.AH)(n||(n=v`
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
  `)),(0,l.__decorate)([(0,u.MZ)()],f.prototype,"path",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],f.prototype,"secondaryPath",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],f.prototype,"viewBox",void 0),f=(0,l.__decorate)([(0,u.EM)("ha-svg-icon")],f)},38586:function(t,a,o){o.r(a),o.d(a,{KnxDashboard:function(){return A}});var e,i,r=o(44734),n=o(56038),s=o(69683),c=o(6454),d=(o(52675),o(89463),o(28706),o(62062),o(18111),o(61701),o(26099),o(62826)),h=o(96196),l=o(77845),p=(o(95379),o(45397),o(65300),o(94333)),u=t=>t,v=function(t){function a(){var t;(0,r.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,s.A)(this,a,[].concat(e))).isWide=!1,t.vertical=!1,t.fullWidth=!1,t}return(0,c.A)(a,t),(0,n.A)(a,[{key:"render",value:function(){return(0,h.qy)(e||(e=u`
      <div
        class="content ${0}"
      >
        <div class="header"><slot name="header"></slot></div>
        <div
          class="together layout ${0}"
        >
          <div class="intro"><slot name="introduction"></slot></div>
          <div class="panel flex-auto"><slot></slot></div>
        </div>
      </div>
    `),(0,p.H)({narrow:!this.isWide,"full-width":this.fullWidth}),(0,p.H)({narrow:!this.isWide,vertical:this.vertical||!this.isWide,horizontal:!this.vertical&&this.isWide}))}}])}(h.WF);v.styles=(0,h.AH)(i||(i=u`
    :host {
      display: block;
    }

    .content {
      padding: 28px 20px 0;
      max-width: 1040px;
      margin: 0 auto;
    }

    .layout {
      display: flex;
    }

    .horizontal {
      flex-direction: row;
    }

    .vertical {
      flex-direction: column;
    }

    .flex-auto {
      flex: 1 1 auto;
    }

    .header {
      font-family: var(--ha-font-family-body);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-size: var(--ha-font-size-2xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      opacity: var(--dark-primary-opacity);
    }

    .together {
      margin-top: var(--config-section-content-together-margin-top, 32px);
    }

    .intro {
      font-family: var(--ha-font-family-body);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-normal);
      width: 100%;
      opacity: var(--dark-primary-opacity);
      font-size: var(--ha-font-size-m);
      padding-bottom: 20px;
    }

    .horizontal .intro {
      max-width: 400px;
      margin-right: 40px;
      margin-inline-end: 40px;
      margin-inline-start: initial;
    }

    .panel {
      margin-top: -24px;
    }

    .panel ::slotted(*) {
      margin-top: 24px;
      display: block;
    }

    .narrow.content {
      max-width: 640px;
    }
    .narrow .together {
      margin-top: var(
        --config-section-narrow-content-together-margin-top,
        var(--config-section-content-together-margin-top, 20px)
      );
    }
    .narrow .intro {
      padding-bottom: 20px;
      margin-right: 0;
      margin-inline-end: 0;
      margin-inline-start: initial;
      max-width: 500px;
    }

    .full-width {
      padding: 0;
    }

    .full-width .layout {
      flex-direction: column;
    }
  `)),(0,d.__decorate)([(0,l.MZ)({attribute:"is-wide",type:Boolean})],v.prototype,"isWide",void 0),(0,d.__decorate)([(0,l.MZ)({type:Boolean})],v.prototype,"vertical",void 0),(0,d.__decorate)([(0,l.MZ)({type:Boolean,attribute:"full-width"})],v.prototype,"fullWidth",void 0),v=(0,d.__decorate)([(0,l.EM)("ha-config-section")],v);var f,y=o(62275),g=o(71467),b=function(t){function a(){var t;(0,r.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,s.A)(this,a,[].concat(e))).narrow=!1,t}return(0,c.A)(a,t),(0,n.A)(a)}(y.$);b.styles=[g.R,(0,h.AH)(f||(f=(t=>t)`
      header {
        padding-top: var(--safe-area-inset-top);
      }
      .mdc-top-app-bar__row {
        height: var(--header-height);
        border-bottom: var(--app-header-border-bottom);
      }
      .mdc-top-app-bar--fixed-adjust {
        padding-top: calc(
          var(--header-height, 0px) + var(--safe-area-inset-top, 0px)
        );
        padding-bottom: var(--safe-area-inset-bottom);
        padding-right: var(--safe-area-inset-right);
      }
      :host([narrow]) .mdc-top-app-bar--fixed-adjust {
        padding-left: var(--safe-area-inset-left);
      }
      .mdc-top-app-bar {
        --mdc-typography-headline6-font-weight: var(--ha-font-weight-normal);
        color: var(--app-header-text-color, var(--mdc-theme-on-primary, #fff));
        background-color: var(
          --app-header-background-color,
          var(--mdc-theme-primary)
        );
        padding-top: var(--safe-area-inset-top);
        padding-right: var(--safe-area-inset-right);
      }
      :host([narrow]) .mdc-top-app-bar {
        padding-left: var(--safe-area-inset-left);
      }
      .mdc-top-app-bar__title {
        font-size: var(--ha-font-size-xl);
        padding-inline-start: 24px;
        padding-inline-end: initial;
      }
    `))],(0,d.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],b.prototype,"narrow",void 0),b=(0,d.__decorate)([(0,l.EM)("ha-top-app-bar-fixed")],b);var m,_,w=o(16404),x=t=>t,A=function(t){function a(){var t;(0,r.A)(this,a);for(var o=arguments.length,e=new Array(o),i=0;i<o;i++)e[i]=arguments[i];return(t=(0,s.A)(this,a,[].concat(e))).narrow=!1,t.isWide=!1,t}return(0,c.A)(a,t),(0,n.A)(a,[{key:"_getPages",value:function(){return(0,w.rN)(!!this.knx.projectInfo).map((t=>Object.assign(Object.assign({},t),{},{name:this.hass.localize(t.translationKey)||t.name,description:this.hass.localize(t.descriptionTranslationKey)||t.description})))}},{key:"render",value:function(){return(0,h.qy)(m||(m=x`
      <ha-top-app-bar-fixed .narrow=${0}>
        <ha-menu-button
          slot="navigationIcon"
          .hass=${0}
          .narrow=${0}
        ></ha-menu-button>
        <div slot="title">KNX</div>
        <ha-config-section .narrow=${0} .isWide=${0}>
          <ha-card outlined>
            <ha-navigation-list
              .hass=${0}
              .narrow=${0}
              .pages=${0}
              has-secondary
            ></ha-navigation-list>
          </ha-card>
        </ha-config-section>
      </ha-top-app-bar-fixed>
    `),this.narrow,this.hass,this.narrow,this.narrow,this.isWide,this.hass,this.narrow,this._getPages())}}])}(h.WF);A.styles=(0,h.AH)(_||(_=x`
    :host {
      display: block;
    }
    ha-card {
      overflow: hidden;
    }
  `)),(0,d.__decorate)([(0,l.MZ)({attribute:!1})],A.prototype,"hass",void 0),(0,d.__decorate)([(0,l.MZ)({attribute:!1})],A.prototype,"knx",void 0),(0,d.__decorate)([(0,l.MZ)({type:Boolean})],A.prototype,"narrow",void 0),(0,d.__decorate)([(0,l.MZ)({attribute:"is-wide",type:Boolean})],A.prototype,"isWide",void 0),A=(0,d.__decorate)([(0,l.EM)("knx-dashboard")],A)}}]);
//# sourceMappingURL=6359.bafddb6f736c46ba.js.map