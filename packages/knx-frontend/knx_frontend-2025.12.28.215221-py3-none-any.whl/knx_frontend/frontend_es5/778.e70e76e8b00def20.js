"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["778"],{55376:function(o,t,a){function r(o){return null==o||Array.isArray(o)?o:[o]}a.d(t,{e:function(){return r}})},92209:function(o,t,a){a.d(t,{x:function(){return r}});a(74423);var r=(o,t)=>o&&o.config.components.includes(t)},39501:function(o,t,a){a.d(t,{a:function(){return e}});a(16280);var r=(0,a(62111).n)((o=>{history.replaceState({scrollPosition:o},"")}),300);function e(o){return(t,a)=>{if("object"==typeof a)throw new Error("This decorator does not support this compilation type.");var e=t.connectedCallback;t.connectedCallback=function(){e.call(this);var t=this[a];t&&this.updateComplete.then((()=>{var a=this.renderRoot.querySelector(o);a&&setTimeout((()=>{a.scrollTop=t}),0)}))};var n,i=Object.getOwnPropertyDescriptor(t,a);if(void 0===i)n={get(){var o;return this[`__${String(a)}`]||(null===(o=history.state)||void 0===o?void 0:o.scrollPosition)},set(o){r(o),this[`__${String(a)}`]=o},configurable:!0,enumerable:!0};else{var l=i.set;n=Object.assign(Object.assign({},i),{},{set(o){r(o),this[`__${String(a)}`]=o,null==l||l.call(this,o)}})}Object.defineProperty(t,a,n)}}},62111:function(o,t,a){a.d(t,{n:function(){return r}});var r=function(o,t){var a,r=!(arguments.length>2&&void 0!==arguments[2])||arguments[2],e=!(arguments.length>3&&void 0!==arguments[3])||arguments[3],n=0,i=function(){for(var i=arguments.length,l=new Array(i),s=0;s<i;s++)l[s]=arguments[s];var c=Date.now();n||!1!==r||(n=c);var d=t-(c-n);d<=0||d>t?(a&&(clearTimeout(a),a=void 0),n=c,o.apply(void 0,l)):a||!1===e||(a=window.setTimeout((()=>{n=!1===r?0:Date.now(),a=void 0,o.apply(void 0,l)}),d))};return i.cancel=()=>{clearTimeout(a),a=void 0,n=0},i}},17963:function(o,t,a){a.r(t);var r,e,n,i,l=a(44734),s=a(56038),c=a(69683),d=a(6454),h=(a(28706),a(62826)),v=a(96196),p=a(77845),u=a(94333),b=a(92542),f=(a(60733),a(60961),o=>o),g={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"},m=function(o){function t(){var o;(0,l.A)(this,t);for(var a=arguments.length,r=new Array(a),e=0;e<a;e++)r[e]=arguments[e];return(o=(0,c.A)(this,t,[].concat(r))).title="",o.alertType="info",o.dismissable=!1,o.narrow=!1,o}return(0,d.A)(t,o),(0,s.A)(t,[{key:"render",value:function(){return(0,v.qy)(r||(r=f`
      <div
        class="issue-type ${0}"
        role="alert"
      >
        <div class="icon ${0}">
          <slot name="icon">
            <ha-svg-icon .path=${0}></ha-svg-icon>
          </slot>
        </div>
        <div class=${0}>
          <div class="main-content">
            ${0}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${0}
            </slot>
          </div>
        </div>
      </div>
    `),(0,u.H)({[this.alertType]:!0}),this.title?"":"no-title",g[this.alertType],(0,u.H)({content:!0,narrow:this.narrow}),this.title?(0,v.qy)(e||(e=f`<div class="title">${0}</div>`),this.title):v.s6,this.dismissable?(0,v.qy)(n||(n=f`<ha-icon-button
                    @click=${0}
                    label="Dismiss alert"
                    .path=${0}
                  ></ha-icon-button>`),this._dismissClicked,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):v.s6)}},{key:"_dismissClicked",value:function(){(0,b.r)(this,"alert-dismissed-clicked")}}])}(v.WF);m.styles=(0,v.AH)(i||(i=f`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
    }
    .icon {
      height: var(--ha-alert-icon-size, 24px);
      width: var(--ha-alert-icon-size, 24px);
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: var(--ha-border-radius-sm);
    }
    .icon.no-title {
      align-self: center;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-align: var(--float-start);
    }
    .content.narrow {
      flex-direction: column;
      align-items: flex-end;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      line-height: normal;
      margin-left: 8px;
      margin-right: 0;
      margin-inline-start: 8px;
      margin-inline-end: 8px;
    }
    .title {
      margin-top: 2px;
      font-weight: var(--ha-font-weight-bold);
    }
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
    :host ::slotted(ul) {
      margin: 0;
      padding-inline-start: 20px;
    }
  `)),(0,h.__decorate)([(0,p.MZ)()],m.prototype,"title",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:"alert-type"})],m.prototype,"alertType",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],m.prototype,"dismissable",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],m.prototype,"narrow",void 0),m=(0,h.__decorate)([(0,p.EM)("ha-alert")],m)},89473:function(o,t,a){a.a(o,(async function(o,t){try{var r=a(44734),e=a(56038),n=a(69683),i=a(6454),l=(a(28706),a(62826)),s=a(88496),c=a(96196),d=a(77845),h=o([s]);s=(h.then?(await h)():h)[0];var v,p=o=>o,u=function(o){function t(){var o;(0,r.A)(this,t);for(var a=arguments.length,e=new Array(a),i=0;i<a;i++)e[i]=arguments[i];return(o=(0,n.A)(this,t,[].concat(e))).variant="brand",o}return(0,i.A)(t,o),(0,e.A)(t,null,[{key:"styles",get:function(){return[s.A.styles,(0,c.AH)(v||(v=p`
        :host {
          --wa-form-control-padding-inline: 16px;
          --wa-font-weight-action: var(--ha-font-weight-medium);
          --wa-form-control-border-radius: var(
            --ha-button-border-radius,
            var(--ha-border-radius-pill)
          );

          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 40px)
          );
        }
        .button {
          font-size: var(--ha-font-size-m);
          line-height: 1;

          transition: background-color 0.15s ease-in-out;
          text-wrap: wrap;
        }

        :host([size="small"]) .button {
          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 32px)
          );
          font-size: var(--wa-font-size-s, var(--ha-font-size-m));
          --wa-form-control-padding-inline: 12px;
        }

        :host([variant="brand"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-primary-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-primary-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-primary-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-primary-loud-hover
          );
        }

        :host([variant="neutral"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-neutral-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-neutral-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-neutral-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-neutral-loud-hover
          );
        }

        :host([variant="success"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-success-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-success-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-success-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-success-loud-hover
          );
        }

        :host([variant="warning"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-warning-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-warning-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-warning-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-warning-loud-hover
          );
        }

        :host([variant="danger"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-danger-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-danger-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-danger-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-danger-loud-hover
          );
        }

        :host([appearance~="plain"]) .button {
          color: var(--wa-color-on-normal);
          background-color: transparent;
        }
        :host([appearance~="plain"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        :host([appearance~="outlined"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        @media (hover: hover) {
          :host([appearance~="filled"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-normal-hover);
          }
          :host([appearance~="accent"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-loud-hover);
          }
          :host([appearance~="plain"])
            .button:not(.disabled):not(.loading):hover {
            color: var(--wa-color-on-normal);
          }
        }
        :host([appearance~="filled"]) .button {
          color: var(--wa-color-on-normal);
          background-color: var(--wa-color-fill-normal);
          border-color: transparent;
        }
        :host([appearance~="filled"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-normal-active);
        }
        :host([appearance~="filled"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-normal-resting);
          color: var(--ha-color-on-disabled-normal);
        }

        :host([appearance~="accent"]) .button {
          background-color: var(
            --wa-color-fill-loud,
            var(--wa-color-neutral-fill-loud)
          );
        }
        :host([appearance~="accent"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-loud-active);
        }
        :host([appearance~="accent"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-loud-resting);
          color: var(--ha-color-on-disabled-loud);
        }

        :host([loading]) {
          pointer-events: none;
        }

        .button.disabled {
          opacity: 1;
        }

        slot[name="start"]::slotted(*) {
          margin-inline-end: 4px;
        }
        slot[name="end"]::slotted(*) {
          margin-inline-start: 4px;
        }

        .button.has-start {
          padding-inline-start: 8px;
        }
        .button.has-end {
          padding-inline-end: 8px;
        }

        .label {
          overflow: hidden;
          text-overflow: ellipsis;
          padding: var(--ha-space-1) 0;
        }
      `))]}}])}(s.A);u=(0,l.__decorate)([(0,d.EM)("ha-button")],u),t()}catch(b){t(b)}}))},95591:function(o,t,a){var r,e=a(44734),n=a(56038),i=a(75864),l=a(69683),s=a(6454),c=a(25460),d=(a(28706),a(62826)),h=a(76482),v=a(91382),p=a(96245),u=a(96196),b=a(77845),f=function(o){function t(){var o;(0,e.A)(this,t);for(var a=arguments.length,r=new Array(a),n=0;n<a;n++)r[n]=arguments[n];return(o=(0,l.A)(this,t,[].concat(r))).attachableTouchController=new h.i((0,i.A)(o),o._onTouchControlChange.bind((0,i.A)(o))),o._handleTouchEnd=()=>{o.disabled||(0,c.A)(((0,i.A)(o),t),"endPressAnimation",o,3)([])},o}return(0,s.A)(t,o),(0,n.A)(t,[{key:"attach",value:function(o){(0,c.A)(t,"attach",this,3)([o]),this.attachableTouchController.attach(o)}},{key:"disconnectedCallback",value:function(){(0,c.A)(t,"disconnectedCallback",this,3)([]),this.hovered=!1,this.pressed=!1}},{key:"detach",value:function(){(0,c.A)(t,"detach",this,3)([]),this.attachableTouchController.detach()}},{key:"_onTouchControlChange",value:function(o,t){null==o||o.removeEventListener("touchend",this._handleTouchEnd),null==t||t.addEventListener("touchend",this._handleTouchEnd)}}])}(v.n);f.styles=[p.R,(0,u.AH)(r||(r=(o=>o)`
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
    `))],f=(0,d.__decorate)([(0,b.EM)("ha-ripple")],f)},49339:function(o,t,a){a.a(o,(async function(o,r){try{a.r(t);var e=a(44734),n=a(56038),i=a(69683),l=a(6454),s=(a(28706),a(62826)),c=a(96196),d=a(77845),h=a(5871),v=(a(371),a(89473)),p=(a(45397),a(17963),o([v]));v=(p.then?(await p)():p)[0];var u,b,f,g,m,y=o=>o,w=function(o){function t(){var o;(0,e.A)(this,t);for(var a=arguments.length,r=new Array(a),n=0;n<a;n++)r[n]=arguments[n];return(o=(0,i.A)(this,t,[].concat(r))).toolbar=!0,o.rootnav=!1,o.narrow=!1,o}return(0,l.A)(t,o),(0,n.A)(t,[{key:"render",value:function(){var o,t;return(0,c.qy)(u||(u=y`
      ${0}
      <div class="content">
        <ha-alert alert-type="error">${0}</ha-alert>
        <slot>
          <ha-button appearance="plain" size="small" @click=${0}>
            ${0}
          </ha-button>
        </slot>
      </div>
    `),this.toolbar?(0,c.qy)(b||(b=y`<div class="toolbar">
            ${0}
          </div>`),this.rootnav||null!==(o=history.state)&&void 0!==o&&o.root?(0,c.qy)(f||(f=y`
                  <ha-menu-button
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.hass,this.narrow):(0,c.qy)(g||(g=y`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._handleBack)):"",this.error,this._handleBack,null===(t=this.hass)||void 0===t?void 0:t.localize("ui.common.back"))}},{key:"_handleBack",value:function(){(0,h.O)()}}],[{key:"styles",get:function(){return[(0,c.AH)(m||(m=y`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }
        .toolbar {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          padding: 8px 12px;
          pointer-events: none;
          background-color: var(--app-header-background-color);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
        }
        @media (max-width: 599px) {
          .toolbar {
            padding: 4px;
          }
        }
        ha-icon-button-arrow-prev {
          pointer-events: auto;
        }
        .content {
          color: var(--primary-text-color);
          height: calc(100% - var(--header-height));
          display: flex;
          padding: 16px;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          box-sizing: border-box;
        }
        a {
          color: var(--primary-color);
        }
        ha-alert {
          margin-bottom: 16px;
        }
      `))]}}])}(c.WF);(0,s.__decorate)([(0,d.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean})],w.prototype,"toolbar",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean})],w.prototype,"rootnav",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean})],w.prototype,"narrow",void 0),(0,s.__decorate)([(0,d.MZ)()],w.prototype,"error",void 0),w=(0,s.__decorate)([(0,d.EM)("hass-error-screen")],w),r()}catch(x){r(x)}}))},84884:function(o,t,a){var r,e,n,i=a(44734),l=a(56038),s=a(69683),c=a(6454),d=a(25460),h=(a(28706),a(2008),a(50113),a(74423),a(62062),a(18111),a(22489),a(20116),a(61701),a(26099),a(62826)),v=a(96196),p=a(77845),u=a(94333),b=a(22786),f=(a(13579),a(55376)),g=a(92209),m=(o,t)=>!t.component||(0,f.e)(t.component).some((t=>(0,g.x)(o,t))),y=(o,t)=>!t.not_component||!(0,f.e)(t.not_component).some((t=>(0,g.x)(o,t))),w=o=>o.core,x=(o,t)=>(o=>o.advancedOnly)(t)&&!(o=>{var t;return null===(t=o.userData)||void 0===t?void 0:t.showAdvanced})(o),_=a(5871),k=a(39501),A=(a(371),a(45397),a(60961),a(32288)),$=(a(95591),o=>o),M=function(o){function t(){var o;(0,i.A)(this,t);for(var a=arguments.length,r=new Array(a),e=0;e<a;e++)r[e]=arguments[e];return(o=(0,s.A)(this,t,[].concat(r))).active=!1,o.narrow=!1,o}return(0,c.A)(t,o),(0,l.A)(t,[{key:"render",value:function(){return(0,v.qy)(r||(r=$`
      <div
        tabindex="0"
        role="tab"
        aria-selected=${0}
        aria-label=${0}
        @keydown=${0}
      >
        ${0}
        <span class="name">${0}</span>
        <ha-ripple></ha-ripple>
      </div>
    `),this.active,(0,A.J)(this.name),this._handleKeyDown,this.narrow?(0,v.qy)(e||(e=$`<slot name="icon"></slot>`)):"",this.name)}},{key:"_handleKeyDown",value:function(o){"Enter"===o.key&&o.target.click()}}])}(v.WF);M.styles=(0,v.AH)(n||(n=$`
    div {
      padding: 0 32px;
      display: flex;
      flex-direction: column;
      text-align: center;
      box-sizing: border-box;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--header-height);
      cursor: pointer;
      position: relative;
      outline: none;
    }

    .name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }

    :host([active]) {
      color: var(--primary-color);
    }

    :host(:not([narrow])[active]) div {
      border-bottom: 2px solid var(--primary-color);
    }

    :host([narrow]) {
      min-width: 0;
      display: flex;
      justify-content: center;
      overflow: hidden;
    }

    :host([narrow]) div {
      padding: 0 4px;
    }

    div:focus-visible:before {
      position: absolute;
      display: block;
      content: "";
      inset: 0;
      background-color: var(--secondary-text-color);
      opacity: 0.08;
    }
  `)),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],M.prototype,"active",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],M.prototype,"narrow",void 0),(0,h.__decorate)([(0,p.MZ)()],M.prototype,"name",void 0),M=(0,h.__decorate)([(0,p.EM)("ha-tab")],M);var Z,z,T,C,q,L,H,B,P,E,j,S,F=a(39396),V=o=>o,O=function(o){function t(){var o;(0,i.A)(this,t);for(var a=arguments.length,r=new Array(a),e=0;e<a;e++)r[e]=arguments[e];return(o=(0,s.A)(this,t,[].concat(r))).supervisor=!1,o.mainPage=!1,o.narrow=!1,o.isWide=!1,o.pane=!1,o.hasFab=!1,o._getTabs=(0,b.A)(((t,a,r,e,n,i,l)=>{var s=t.filter((t=>((o,t)=>(w(t)||m(o,t))&&!x(o,t)&&y(o,t))(o.hass,t)));if(s.length<2){if(1===s.length){var c=s[0];return[c.translationKey?l(c.translationKey):c.name]}return[""]}return s.map((t=>(0,v.qy)(Z||(Z=V`
          <a href=${0}>
            <ha-tab
              .hass=${0}
              .active=${0}
              .narrow=${0}
              .name=${0}
            >
              ${0}
            </ha-tab>
          </a>
        `),t.path,o.hass,t.path===(null==a?void 0:a.path),o.narrow,t.translationKey?l(t.translationKey):t.name,t.iconPath?(0,v.qy)(z||(z=V`<ha-svg-icon
                    slot="icon"
                    .path=${0}
                  ></ha-svg-icon>`),t.iconPath):"")))})),o}return(0,c.A)(t,o),(0,l.A)(t,[{key:"willUpdate",value:function(o){o.has("route")&&(this._activeTab=this.tabs.find((o=>`${this.route.prefix}${this.route.path}`.includes(o.path)))),(0,d.A)(t,"willUpdate",this,3)([o])}},{key:"render",value:function(){var o,t=this._getTabs(this.tabs,this._activeTab,this.hass.config.components,this.hass.language,this.hass.userData,this.narrow,this.localizeFunc||this.hass.localize),a=t.length>1;return(0,v.qy)(T||(T=V`
      <div class="toolbar">
        <slot name="toolbar">
          <div class="toolbar-content">
            ${0}
            ${0}
            ${0}
            <div id="toolbar-icon">
              <slot name="toolbar-icon"></slot>
            </div>
          </div>
        </slot>
        ${0}
      </div>
      <div
        class=${0}
      >
        ${0}
        <div
          class="content ha-scrollbar ${0}"
          @scroll=${0}
        >
          <slot></slot>
          ${0}
        </div>
      </div>
      <div id="fab" class=${0}>
        <slot name="fab"></slot>
      </div>
    `),this.mainPage||!this.backPath&&null!==(o=history.state)&&void 0!==o&&o.root?(0,v.qy)(C||(C=V`
                  <ha-menu-button
                    .hassio=${0}
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.supervisor,this.hass,this.narrow):this.backPath?(0,v.qy)(q||(q=V`
                    <a href=${0}>
                      <ha-icon-button-arrow-prev
                        .hass=${0}
                      ></ha-icon-button-arrow-prev>
                    </a>
                  `),this.backPath,this.hass):(0,v.qy)(L||(L=V`
                    <ha-icon-button-arrow-prev
                      .hass=${0}
                      @click=${0}
                    ></ha-icon-button-arrow-prev>
                  `),this.hass,this._backTapped),this.narrow||!a?(0,v.qy)(H||(H=V`<div class="main-title">
                  <slot name="header">${0}</slot>
                </div>`),a?"":t[0]):"",a&&!this.narrow?(0,v.qy)(B||(B=V`<div id="tabbar">${0}</div>`),t):"",a&&this.narrow?(0,v.qy)(P||(P=V`<div id="tabbar" class="bottom-bar">${0}</div>`),t):"",(0,u.H)({container:!0,tabs:a&&this.narrow}),this.pane?(0,v.qy)(E||(E=V`<div class="pane">
              <div class="shadow-container"></div>
              <div class="ha-scrollbar">
                <slot name="pane"></slot>
              </div>
            </div>`)):v.s6,(0,u.H)({tabs:a}),this._saveScrollPos,this.hasFab?(0,v.qy)(j||(j=V`<div class="fab-bottom-space"></div>`)):v.s6,(0,u.H)({tabs:a}))}},{key:"_saveScrollPos",value:function(o){this._savedScrollPos=o.target.scrollTop}},{key:"_backTapped",value:function(){this.backCallback?this.backCallback():(0,_.O)()}}],[{key:"styles",get:function(){return[F.dp,(0,v.AH)(S||(S=V`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }

        :host([narrow]) {
          width: 100%;
          position: fixed;
        }

        .container {
          display: flex;
          height: calc(
            100% - var(--header-height, 0px) - var(--safe-area-inset-top, 0px)
          );
        }

        ha-menu-button {
          margin-right: 24px;
          margin-inline-end: 24px;
          margin-inline-start: initial;
        }

        .toolbar {
          font-size: var(--ha-font-size-xl);
          height: calc(
            var(--header-height, 0px) + var(--safe-area-inset-top, 0px)
          );
          padding-top: var(--safe-area-inset-top);
          padding-right: var(--safe-area-inset-right);
          background-color: var(--sidebar-background-color);
          font-weight: var(--ha-font-weight-normal);
          border-bottom: 1px solid var(--divider-color);
          box-sizing: border-box;
        }
        :host([narrow]) .toolbar {
          padding-left: var(--safe-area-inset-left);
        }
        .toolbar-content {
          padding: 8px 12px;
          display: flex;
          align-items: center;
          height: 100%;
          box-sizing: border-box;
        }
        :host([narrow]) .toolbar-content {
          padding: 4px;
        }
        .toolbar a {
          color: var(--sidebar-text-color);
          text-decoration: none;
        }
        .bottom-bar a {
          width: 25%;
        }

        #tabbar {
          display: flex;
          font-size: var(--ha-font-size-m);
          overflow: hidden;
        }

        #tabbar > a {
          overflow: hidden;
          max-width: 45%;
        }

        #tabbar.bottom-bar {
          position: absolute;
          bottom: 0;
          left: 0;
          padding: 0 16px;
          box-sizing: border-box;
          background-color: var(--sidebar-background-color);
          border-top: 1px solid var(--divider-color);
          justify-content: space-around;
          z-index: 2;
          font-size: var(--ha-font-size-s);
          width: 100%;
          padding-bottom: var(--safe-area-inset-bottom);
        }

        #tabbar:not(.bottom-bar) {
          flex: 1;
          justify-content: center;
        }

        :host(:not([narrow])) #toolbar-icon {
          min-width: 40px;
        }

        ha-menu-button,
        ha-icon-button-arrow-prev,
        ::slotted([slot="toolbar-icon"]) {
          display: flex;
          flex-shrink: 0;
          pointer-events: auto;
          color: var(--sidebar-icon-color);
        }

        .main-title {
          flex: 1;
          max-height: var(--header-height);
          line-height: var(--ha-line-height-normal);
          color: var(--sidebar-text-color);
          margin: var(--main-title-margin, var(--margin-title));
        }

        .content {
          position: relative;
          width: 100%;
          margin-right: var(--safe-area-inset-right);
          margin-inline-end: var(--safe-area-inset-right);
          margin-bottom: var(--safe-area-inset-bottom);
          overflow: auto;
          -webkit-overflow-scrolling: touch;
        }
        :host([narrow]) .content {
          margin-left: var(--safe-area-inset-left);
          margin-inline-start: var(--safe-area-inset-left);
        }
        :host([narrow]) .content.tabs {
          /* Bottom bar reuses header height */
          margin-bottom: calc(
            var(--header-height, 0px) + var(--safe-area-inset-bottom, 0px)
          );
        }

        .content .fab-bottom-space {
          height: calc(64px + var(--safe-area-inset-bottom, 0px));
        }

        :host([narrow]) .content.tabs .fab-bottom-space {
          height: calc(80px + var(--safe-area-inset-bottom, 0px));
        }

        #fab {
          position: fixed;
          right: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(16px + var(--safe-area-inset-right));
          inset-inline-start: initial;
          bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
          z-index: 1;
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: var(--ha-space-2);
        }
        :host([narrow]) #fab.tabs {
          bottom: calc(84px + var(--safe-area-inset-bottom, 0px));
        }
        #fab[is-wide] {
          bottom: 24px;
          right: 24px;
          inset-inline-end: 24px;
          inset-inline-start: initial;
        }

        .pane {
          border-right: 1px solid var(--divider-color);
          border-inline-end: 1px solid var(--divider-color);
          border-inline-start: initial;
          box-sizing: border-box;
          display: flex;
          flex: 0 0 var(--sidepane-width, 250px);
          width: var(--sidepane-width, 250px);
          flex-direction: column;
          position: relative;
        }
        .pane .ha-scrollbar {
          flex: 1;
        }
      `))]}}])}(v.WF);(0,h.__decorate)([(0,p.MZ)({attribute:!1})],O.prototype,"hass",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],O.prototype,"supervisor",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],O.prototype,"localizeFunc",void 0),(0,h.__decorate)([(0,p.MZ)({type:String,attribute:"back-path"})],O.prototype,"backPath",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],O.prototype,"backCallback",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,attribute:"main-page"})],O.prototype,"mainPage",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],O.prototype,"route",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],O.prototype,"tabs",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],O.prototype,"narrow",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0,attribute:"is-wide"})],O.prototype,"isWide",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],O.prototype,"pane",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,attribute:"has-fab"})],O.prototype,"hasFab",void 0),(0,h.__decorate)([(0,p.wk)()],O.prototype,"_activeTab",void 0),(0,h.__decorate)([(0,k.a)(".content")],O.prototype,"_savedScrollPos",void 0),(0,h.__decorate)([(0,p.Ls)({passive:!0})],O.prototype,"_saveScrollPos",null),O=(0,h.__decorate)([(0,p.EM)("hass-tabs-subpage")],O)},64576:function(o,t,a){a.a(o,(async function(o,r){try{a.r(t),a.d(t,{KNXError:function(){return f}});var e=a(44734),n=a(56038),i=a(69683),l=a(6454),s=a(62826),c=a(96196),d=a(77845),h=a(76679),v=(a(84884),a(49339)),p=o([v]);v=(p.then?(await p)():p)[0];var u,b=o=>o,f=function(o){function t(){return(0,e.A)(this,t),(0,i.A)(this,t,arguments)}return(0,l.A)(t,o),(0,n.A)(t,[{key:"render",value:function(){var o,t,a=null!==(o=null===(t=h.G.history.state)||void 0===t?void 0:t.message)&&void 0!==o?o:"Unknown error";return(0,c.qy)(u||(u=b`
      <hass-error-screen
        .hass=${0}
        .error=${0}
        .toolbar=${0}
        .rootnav=${0}
        .narrow=${0}
      ></hass-error-screen>
    `),this.hass,a,!0,!1,this.narrow)}}])}(c.WF);(0,s.__decorate)([(0,d.MZ)({type:Object})],f.prototype,"hass",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"knx",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean,reflect:!0})],f.prototype,"narrow",void 0),(0,s.__decorate)([(0,d.MZ)({type:Object})],f.prototype,"route",void 0),(0,s.__decorate)([(0,d.MZ)({type:Array,reflect:!1})],f.prototype,"tabs",void 0),f=(0,s.__decorate)([(0,d.EM)("knx-error")],f),r()}catch(g){r(g)}}))},74488:function(o,t,a){var r=a(67680),e=Math.floor,n=function(o,t){var a=o.length;if(a<8)for(var i,l,s=1;s<a;){for(l=s,i=o[s];l&&t(o[l-1],i)>0;)o[l]=o[--l];l!==s++&&(o[l]=i)}else for(var c=e(a/2),d=n(r(o,0,c),t),h=n(r(o,c),t),v=d.length,p=h.length,u=0,b=0;u<v||b<p;)o[u+b]=u<v&&b<p?t(d[u],h[b])<=0?d[u++]:h[b++]:u<v?d[u++]:h[b++];return o};o.exports=n},13709:function(o,t,a){var r=a(82839).match(/firefox\/(\d+)/i);o.exports=!!r&&+r[1]},13763:function(o,t,a){var r=a(82839);o.exports=/MSIE|Trident/.test(r)},3607:function(o,t,a){var r=a(82839).match(/AppleWebKit\/(\d+)\./);o.exports=!!r&&+r[1]},89429:function(o,t,a){var r=a(44576),e=a(38574);o.exports=function(o){if(e){try{return r.process.getBuiltinModule(o)}catch(t){}try{return Function('return require("'+o+'")')()}catch(t){}}}}}]);
//# sourceMappingURL=778.e70e76e8b00def20.js.map