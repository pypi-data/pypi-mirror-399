"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2591"],{39501:function(t,e,a){a.d(e,{a:function(){return o}});a(16280);var r=(0,a(62111).n)((t=>{history.replaceState({scrollPosition:t},"")}),300);function o(t){return(e,a)=>{if("object"==typeof a)throw new Error("This decorator does not support this compilation type.");var o=e.connectedCallback;e.connectedCallback=function(){o.call(this);var e=this[a];e&&this.updateComplete.then((()=>{var a=this.renderRoot.querySelector(t);a&&setTimeout((()=>{a.scrollTop=e}),0)}))};var n,i=Object.getOwnPropertyDescriptor(e,a);if(void 0===i)n={get(){var t;return this[`__${String(a)}`]||(null===(t=history.state)||void 0===t?void 0:t.scrollPosition)},set(t){r(t),this[`__${String(a)}`]=t},configurable:!0,enumerable:!0};else{var s=i.set;n=Object.assign(Object.assign({},i),{},{set(t){r(t),this[`__${String(a)}`]=t,null==s||s.call(this,t)}})}Object.defineProperty(e,a,n)}}},62111:function(t,e,a){a.d(e,{n:function(){return r}});var r=function(t,e){var a,r=!(arguments.length>2&&void 0!==arguments[2])||arguments[2],o=!(arguments.length>3&&void 0!==arguments[3])||arguments[3],n=0,i=function(){for(var i=arguments.length,s=new Array(i),c=0;c<i;c++)s[c]=arguments[c];var l=Date.now();n||!1!==r||(n=l);var d=e-(l-n);d<=0||d>e?(a&&(clearTimeout(a),a=void 0),n=l,t.apply(void 0,s)):a||!1===o||(a=window.setTimeout((()=>{n=!1===r?0:Date.now(),a=void 0,t.apply(void 0,s)}),d))};return i.cancel=()=>{clearTimeout(a),a=void 0,n=0},i}},95379:function(t,e,a){var r,o,n,i=a(44734),s=a(56038),c=a(69683),l=a(6454),d=(a(28706),a(62826)),h=a(96196),p=a(77845),v=t=>t,u=function(t){function e(){var t;(0,i.A)(this,e);for(var a=arguments.length,r=new Array(a),o=0;o<a;o++)r[o]=arguments[o];return(t=(0,c.A)(this,e,[].concat(r))).raised=!1,t}return(0,l.A)(e,t),(0,s.A)(e,[{key:"render",value:function(){return(0,h.qy)(r||(r=v`
      ${0}
      <slot></slot>
    `),this.header?(0,h.qy)(o||(o=v`<h1 class="card-header">${0}</h1>`),this.header):h.s6)}}])}(h.WF);u.styles=(0,h.AH)(n||(n=v`
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
  `)),(0,d.__decorate)([(0,p.MZ)()],u.prototype,"header",void 0),(0,d.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],u.prototype,"raised",void 0),u=(0,d.__decorate)([(0,p.EM)("ha-card")],u)},28608:function(t,e,a){a.r(e),a.d(e,{HaIconNext:function(){return h}});var r=a(56038),o=a(44734),n=a(69683),i=a(6454),s=(a(28706),a(62826)),c=a(77845),l=a(76679),d=a(60961),h=function(t){function e(){var t;(0,o.A)(this,e);for(var a=arguments.length,r=new Array(a),i=0;i<a;i++)r[i]=arguments[i];return(t=(0,n.A)(this,e,[].concat(r))).path="rtl"===l.G.document.dir?"M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z":"M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z",t}return(0,i.A)(e,t),(0,r.A)(e)}(d.HaSvgIcon);(0,s.__decorate)([(0,c.MZ)()],h.prototype,"path",void 0),h=(0,s.__decorate)([(0,c.EM)("ha-icon-next")],h)},23897:function(t,e,a){a.d(e,{G:function(){return b},J:function(){return f}});var r,o,n=a(44734),i=a(56038),s=a(69683),c=a(6454),l=a(62826),d=a(97154),h=a(82553),p=a(96196),v=a(77845),u=(a(95591),t=>t),f=[h.R,(0,p.AH)(r||(r=u`
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
  `))],b=function(t){function e(){return(0,n.A)(this,e),(0,s.A)(this,e,arguments)}return(0,c.A)(e,t),(0,i.A)(e,[{key:"renderRipple",value:function(){return"text"===this.type?p.s6:(0,p.qy)(o||(o=u`<ha-ripple
      part="ripple"
      for="item"
      ?disabled=${0}
    ></ha-ripple>`),this.disabled&&"link"!==this.type)}}])}(d.n);b.styles=f,b=(0,l.__decorate)([(0,v.EM)("ha-md-list-item")],b)},42921:function(t,e,a){var r,o=a(56038),n=a(44734),i=a(69683),s=a(6454),c=a(62826),l=a(49838),d=a(11245),h=a(96196),p=a(77845),v=function(t){function e(){return(0,n.A)(this,e),(0,i.A)(this,e,arguments)}return(0,s.A)(e,t),(0,o.A)(e)}(l.B);v.styles=[d.R,(0,h.AH)(r||(r=(t=>t)`
      :host {
        --md-sys-color-surface: var(--card-background-color);
      }
    `))],v=(0,c.__decorate)([(0,p.EM)("ha-md-list")],v)},65300:function(t,e,a){var r,o,n,i,s,c=a(44734),l=a(56038),d=a(69683),h=a(6454),p=(a(52675),a(89463),a(28706),a(62062),a(18111),a(61701),a(26099),a(62826)),v=a(96196),u=a(77845),f=a(32288),b=(a(28608),a(42921),a(23897),a(60961),t=>t),g=function(t){function e(){var t;(0,c.A)(this,e);for(var a=arguments.length,r=new Array(a),o=0;o<a;o++)r[o]=arguments[o];return(t=(0,d.A)(this,e,[].concat(r))).narrow=!1,t.hasSecondary=!1,t}return(0,h.A)(e,t),(0,l.A)(e,[{key:"render",value:function(){return(0,v.qy)(r||(r=b`
      <ha-md-list
        innerRole="menu"
        itemRoles="menuitem"
        innerAriaLabel=${0}
      >
        ${0}
      </ha-md-list>
    `),(0,f.J)(this.label),this.pages.map((t=>{var e=t.path.endsWith("#external-app-configuration");return(0,v.qy)(o||(o=b`
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
          `),e?"button":"link",e?void 0:t.path,e?this._handleExternalApp:void 0,t.iconColor?"icon-background":"",t.iconColor||"undefined",t.iconPath,t.name,this.hasSecondary?(0,v.qy)(n||(n=b`<span slot="supporting-text">${0}</span>`),t.description):"",this.narrow?"":(0,v.qy)(i||(i=b`<ha-icon-next slot="end"></ha-icon-next>`)))})))}},{key:"_handleExternalApp",value:function(){this.hass.auth.external.fireMessage({type:"config_screen/show"})}}])}(v.WF);g.styles=(0,v.AH)(s||(s=b`
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
  `)),(0,p.__decorate)([(0,u.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,p.__decorate)([(0,u.MZ)({type:Boolean})],g.prototype,"narrow",void 0),(0,p.__decorate)([(0,u.MZ)({attribute:!1})],g.prototype,"pages",void 0),(0,p.__decorate)([(0,u.MZ)({attribute:"has-secondary",type:Boolean})],g.prototype,"hasSecondary",void 0),(0,p.__decorate)([(0,u.MZ)()],g.prototype,"label",void 0),g=(0,p.__decorate)([(0,u.EM)("ha-navigation-list")],g)},95591:function(t,e,a){var r,o=a(44734),n=a(56038),i=a(75864),s=a(69683),c=a(6454),l=a(25460),d=(a(28706),a(62826)),h=a(76482),p=a(91382),v=a(96245),u=a(96196),f=a(77845),b=function(t){function e(){var t;(0,o.A)(this,e);for(var a=arguments.length,r=new Array(a),n=0;n<a;n++)r[n]=arguments[n];return(t=(0,s.A)(this,e,[].concat(r))).attachableTouchController=new h.i((0,i.A)(t),t._onTouchControlChange.bind((0,i.A)(t))),t._handleTouchEnd=()=>{t.disabled||(0,l.A)(((0,i.A)(t),e),"endPressAnimation",t,3)([])},t}return(0,c.A)(e,t),(0,n.A)(e,[{key:"attach",value:function(t){(0,l.A)(e,"attach",this,3)([t]),this.attachableTouchController.attach(t)}},{key:"disconnectedCallback",value:function(){(0,l.A)(e,"disconnectedCallback",this,3)([]),this.hovered=!1,this.pressed=!1}},{key:"detach",value:function(){(0,l.A)(e,"detach",this,3)([]),this.attachableTouchController.detach()}},{key:"_onTouchControlChange",value:function(t,e){null==t||t.removeEventListener("touchend",this._handleTouchEnd),null==e||e.addEventListener("touchend",this._handleTouchEnd)}}])}(p.n);b.styles=[v.R,(0,u.AH)(r||(r=(t=>t)`
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
    `))],b=(0,d.__decorate)([(0,f.EM)("ha-ripple")],b)},84125:function(t,e,a){a.d(e,{QC:function(){return n},fK:function(){return o},p$:function(){return r}});var r=(t,e,a)=>t(`component.${e}.title`)||(null==a?void 0:a.name)||e,o=(t,e)=>{var a={type:"manifest/list"};return e&&(a.integrations=e),t.callWS(a)},n=(t,e)=>t.callWS({type:"manifest/get",integration:e})},29937:function(t,e,a){var r,o,n,i,s,c=a(44734),l=a(56038),d=a(69683),h=a(6454),p=(a(28706),a(62826)),v=a(96196),u=a(77845),f=a(39501),b=a(5871),g=(a(371),a(45397),a(39396)),y=t=>t,m=function(t){function e(){var t;(0,c.A)(this,e);for(var a=arguments.length,r=new Array(a),o=0;o<a;o++)r[o]=arguments[o];return(t=(0,d.A)(this,e,[].concat(r))).mainPage=!1,t.narrow=!1,t.supervisor=!1,t}return(0,h.A)(e,t),(0,l.A)(e,[{key:"render",value:function(){var t;return(0,v.qy)(r||(r=y`
      <div class="toolbar">
        <div class="toolbar-content">
          ${0}

          <div class="main-title">
            <slot name="header">${0}</slot>
          </div>
          <slot name="toolbar-icon"></slot>
        </div>
      </div>
      <div class="content ha-scrollbar" @scroll=${0}>
        <slot></slot>
      </div>
      <div id="fab">
        <slot name="fab"></slot>
      </div>
    `),this.mainPage||null!==(t=history.state)&&void 0!==t&&t.root?(0,v.qy)(o||(o=y`
                <ha-menu-button
                  .hassio=${0}
                  .hass=${0}
                  .narrow=${0}
                ></ha-menu-button>
              `),this.supervisor,this.hass,this.narrow):this.backPath?(0,v.qy)(n||(n=y`
                  <a href=${0}>
                    <ha-icon-button-arrow-prev
                      .hass=${0}
                    ></ha-icon-button-arrow-prev>
                  </a>
                `),this.backPath,this.hass):(0,v.qy)(i||(i=y`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._backTapped),this.header,this._saveScrollPos)}},{key:"_saveScrollPos",value:function(t){this._savedScrollPos=t.target.scrollTop}},{key:"_backTapped",value:function(){this.backCallback?this.backCallback():(0,b.O)()}}],[{key:"styles",get:function(){return[g.dp,(0,v.AH)(s||(s=y`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
          overflow: hidden;
          position: relative;
        }

        :host([narrow]) {
          width: 100%;
          position: fixed;
        }

        .toolbar {
          background-color: var(--app-header-background-color);
          padding-top: var(--safe-area-inset-top);
          padding-right: var(--safe-area-inset-right);
        }
        :host([narrow]) .toolbar {
          padding-left: var(--safe-area-inset-left);
        }

        .toolbar-content {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
          padding: 8px 12px;
        }

        .toolbar a {
          color: var(--sidebar-text-color);
          text-decoration: none;
        }

        ha-menu-button,
        ha-icon-button-arrow-prev,
        ::slotted([slot="toolbar-icon"]) {
          pointer-events: auto;
          color: var(--sidebar-icon-color);
        }

        .main-title {
          margin: var(--margin-title);
          line-height: var(--ha-line-height-normal);
          min-width: 0;
          flex-grow: 1;
          overflow-wrap: break-word;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .content {
          position: relative;
          width: calc(100% - var(--safe-area-inset-right, 0px));
          height: calc(
            100% -
              1px - var(--header-height, 0px) - var(
                --safe-area-inset-top,
                0px
              ) - var(
                --hass-subpage-bottom-inset,
                var(--safe-area-inset-bottom, 0px)
              )
          );
          margin-bottom: var(
            --hass-subpage-bottom-inset,
            var(--safe-area-inset-bottom)
          );
          margin-right: var(--safe-area-inset-right);
          overflow-y: auto;
          overflow: auto;
          -webkit-overflow-scrolling: touch;
        }
        :host([narrow]) .content {
          width: calc(
            100% - var(--safe-area-inset-left, 0px) - var(
                --safe-area-inset-right,
                0px
              )
          );
          margin-left: var(--safe-area-inset-left);
        }

        #fab {
          position: absolute;
          right: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(16px + var(--safe-area-inset-right, 0px));
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
          bottom: calc(24px + var(--safe-area-inset-bottom, 0px));
          right: calc(24px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(24px + var(--safe-area-inset-right, 0px));
          inset-inline-start: initial;
        }
      `))]}}])}(v.WF);(0,p.__decorate)([(0,u.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,p.__decorate)([(0,u.MZ)()],m.prototype,"header",void 0),(0,p.__decorate)([(0,u.MZ)({type:Boolean,attribute:"main-page"})],m.prototype,"mainPage",void 0),(0,p.__decorate)([(0,u.MZ)({type:String,attribute:"back-path"})],m.prototype,"backPath",void 0),(0,p.__decorate)([(0,u.MZ)({attribute:!1})],m.prototype,"backCallback",void 0),(0,p.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0})],m.prototype,"narrow",void 0),(0,p.__decorate)([(0,u.MZ)({type:Boolean})],m.prototype,"supervisor",void 0),(0,p.__decorate)([(0,f.a)(".content")],m.prototype,"_savedScrollPos",void 0),(0,p.__decorate)([(0,u.Ls)({passive:!0})],m.prototype,"_saveScrollPos",null),m=(0,p.__decorate)([(0,u.EM)("hass-subpage")],m)}}]);
//# sourceMappingURL=2591.2637a4886b2c37e3.js.map