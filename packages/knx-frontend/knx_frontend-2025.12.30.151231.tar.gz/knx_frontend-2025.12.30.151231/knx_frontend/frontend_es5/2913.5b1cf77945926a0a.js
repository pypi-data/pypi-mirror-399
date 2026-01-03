"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2913"],{53045:function(o,t,a){a.d(t,{v:function(){return e}});var r=a(78261),e=(a(74423),a(2892),(o,t,a,e)=>{var n=o.split(".",3),i=(0,r.A)(n,3),l=i[0],c=i[1],s=i[2];return Number(l)>t||Number(l)===t&&(void 0===e?Number(c)>=a:Number(c)>a)||void 0!==e&&Number(l)===t&&Number(c)===a&&Number(s)>=e})},39501:function(o,t,a){a.d(t,{a:function(){return e}});a(16280);var r=(0,a(62111).n)((o=>{history.replaceState({scrollPosition:o},"")}),300);function e(o){return(t,a)=>{if("object"==typeof a)throw new Error("This decorator does not support this compilation type.");var e=t.connectedCallback;t.connectedCallback=function(){e.call(this);var t=this[a];t&&this.updateComplete.then((()=>{var a=this.renderRoot.querySelector(o);a&&setTimeout((()=>{a.scrollTop=t}),0)}))};var n,i=Object.getOwnPropertyDescriptor(t,a);if(void 0===i)n={get(){var o;return this[`__${String(a)}`]||(null===(o=history.state)||void 0===o?void 0:o.scrollPosition)},set(o){r(o),this[`__${String(a)}`]=o},configurable:!0,enumerable:!0};else{var l=i.set;n=Object.assign(Object.assign({},i),{},{set(o){r(o),this[`__${String(a)}`]=o,null==l||l.call(this,o)}})}Object.defineProperty(t,a,n)}}},62111:function(o,t,a){a.d(t,{n:function(){return r}});var r=function(o,t){var a,r=!(arguments.length>2&&void 0!==arguments[2])||arguments[2],e=!(arguments.length>3&&void 0!==arguments[3])||arguments[3],n=0,i=function(){for(var i=arguments.length,l=new Array(i),c=0;c<i;c++)l[c]=arguments[c];var s=Date.now();n||!1!==r||(n=s);var d=t-(s-n);d<=0||d>t?(a&&(clearTimeout(a),a=void 0),n=s,o.apply(void 0,l)):a||!1===e||(a=window.setTimeout((()=>{n=!1===r?0:Date.now(),a=void 0,o.apply(void 0,l)}),d))};return i.cancel=()=>{clearTimeout(a),a=void 0,n=0},i}},89473:function(o,t,a){a.a(o,(async function(o,t){try{var r=a(44734),e=a(56038),n=a(69683),i=a(6454),l=(a(28706),a(62826)),c=a(88496),s=a(96196),d=a(77845),h=o([c]);c=(h.then?(await h)():h)[0];var v,u=o=>o,p=function(o){function t(){var o;(0,r.A)(this,t);for(var a=arguments.length,e=new Array(a),i=0;i<a;i++)e[i]=arguments[i];return(o=(0,n.A)(this,t,[].concat(e))).variant="brand",o}return(0,i.A)(t,o),(0,e.A)(t,null,[{key:"styles",get:function(){return[c.A.styles,(0,s.AH)(v||(v=u`
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
      `))]}}])}(c.A);p=(0,l.__decorate)([(0,d.EM)("ha-button")],p),t()}catch(f){t(f)}}))},95379:function(o,t,a){var r,e,n,i=a(44734),l=a(56038),c=a(69683),s=a(6454),d=(a(28706),a(62826)),h=a(96196),v=a(77845),u=o=>o,p=function(o){function t(){var o;(0,i.A)(this,t);for(var a=arguments.length,r=new Array(a),e=0;e<a;e++)r[e]=arguments[e];return(o=(0,c.A)(this,t,[].concat(r))).raised=!1,o}return(0,s.A)(t,o),(0,l.A)(t,[{key:"render",value:function(){return(0,h.qy)(r||(r=u`
      ${0}
      <slot></slot>
    `),this.header?(0,h.qy)(e||(e=u`<h1 class="card-header">${0}</h1>`),this.header):h.s6)}}])}(h.WF);p.styles=(0,h.AH)(n||(n=u`
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
  `)),(0,d.__decorate)([(0,v.MZ)()],p.prototype,"header",void 0),(0,d.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],p.prototype,"raised",void 0),p=(0,d.__decorate)([(0,v.EM)("ha-card")],p)},95260:function(o,t,a){a.d(t,{PS:function(){return r},VR:function(){return e}});a(61397),a(50264),a(74423),a(23792),a(26099),a(31415),a(17642),a(58004),a(33853),a(45876),a(32475),a(15024),a(31698),a(62953),a(53045);var r=o=>o.data,e=o=>"object"==typeof o?"object"==typeof o.body?o.body.message||"Unknown error, see supervisor logs":o.body||o.message||"Unknown error, see supervisor logs":o;new Set([502,503,504])},10234:function(o,t,a){a.d(t,{K$:function(){return i},an:function(){return c},dk:function(){return l}});a(23792),a(26099),a(3362),a(62953);var r=a(92542),e=()=>Promise.all([a.e("6009"),a.e("4533"),a.e("2013"),a.e("1530")]).then(a.bind(a,22316)),n=(o,t,a)=>new Promise((n=>{var i=t.cancel,l=t.confirm;(0,r.r)(o,"show-dialog",{dialogTag:"dialog-box",dialogImport:e,dialogParams:Object.assign(Object.assign(Object.assign({},t),a),{},{cancel:()=>{n(!(null==a||!a.prompt)&&null),i&&i()},confirm:o=>{n(null==a||!a.prompt||o),l&&l(o)}})})})),i=(o,t)=>n(o,t),l=(o,t)=>n(o,t,{confirmation:!0}),c=(o,t)=>n(o,t,{prompt:!0})},29937:function(o,t,a){var r,e,n,i,l,c=a(44734),s=a(56038),d=a(69683),h=a(6454),v=(a(28706),a(62826)),u=a(96196),p=a(77845),f=a(39501),b=a(5871),g=(a(371),a(45397),a(39396)),x=o=>o,m=function(o){function t(){var o;(0,c.A)(this,t);for(var a=arguments.length,r=new Array(a),e=0;e<a;e++)r[e]=arguments[e];return(o=(0,d.A)(this,t,[].concat(r))).mainPage=!1,o.narrow=!1,o.supervisor=!1,o}return(0,h.A)(t,o),(0,s.A)(t,[{key:"render",value:function(){var o;return(0,u.qy)(r||(r=x`
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
    `),this.mainPage||null!==(o=history.state)&&void 0!==o&&o.root?(0,u.qy)(e||(e=x`
                <ha-menu-button
                  .hassio=${0}
                  .hass=${0}
                  .narrow=${0}
                ></ha-menu-button>
              `),this.supervisor,this.hass,this.narrow):this.backPath?(0,u.qy)(n||(n=x`
                  <a href=${0}>
                    <ha-icon-button-arrow-prev
                      .hass=${0}
                    ></ha-icon-button-arrow-prev>
                  </a>
                `),this.backPath,this.hass):(0,u.qy)(i||(i=x`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._backTapped),this.header,this._saveScrollPos)}},{key:"_saveScrollPos",value:function(o){this._savedScrollPos=o.target.scrollTop}},{key:"_backTapped",value:function(){this.backCallback?this.backCallback():(0,b.O)()}}],[{key:"styles",get:function(){return[g.dp,(0,u.AH)(l||(l=x`
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
      `))]}}])}(u.WF);(0,v.__decorate)([(0,p.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,v.__decorate)([(0,p.MZ)()],m.prototype,"header",void 0),(0,v.__decorate)([(0,p.MZ)({type:Boolean,attribute:"main-page"})],m.prototype,"mainPage",void 0),(0,v.__decorate)([(0,p.MZ)({type:String,attribute:"back-path"})],m.prototype,"backPath",void 0),(0,v.__decorate)([(0,p.MZ)({attribute:!1})],m.prototype,"backCallback",void 0),(0,v.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],m.prototype,"narrow",void 0),(0,v.__decorate)([(0,p.MZ)({type:Boolean})],m.prototype,"supervisor",void 0),(0,v.__decorate)([(0,f.a)(".content")],m.prototype,"_savedScrollPos",void 0),(0,v.__decorate)([(0,p.Ls)({passive:!0})],m.prototype,"_saveScrollPos",null),m=(0,v.__decorate)([(0,p.EM)("hass-subpage")],m)},6431:function(o,t,a){a.d(t,{x:function(){return r}});var r="2025.12.30.151231"},45812:function(o,t,a){a.a(o,(async function(o,r){try{a.r(t),a.d(t,{KNXInfo:function(){return P}});var e=a(61397),n=a(50264),i=a(44734),l=a(56038),c=a(69683),s=a(6454),d=a(62826),h=a(96196),v=a(77845),u=a(92542),p=(a(95379),a(29937),a(89473)),f=a(95260),b=a(10234),g=a(65294),x=a(78577),m=a(6431),k=a(16404),w=o([p]);p=(w.then?(await w)():w)[0];var y,_,$,j,A=o=>o,z=new x.Q("info"),P=function(o){function t(){return(0,i.A)(this,t),(0,c.A)(this,t,arguments)}return(0,s.A)(t,o),(0,l.A)(t,[{key:"render",value:function(){return(0,h.qy)(y||(y=A`
      <hass-subpage
        .hass=${0}
        .narrow=${0}
        back-path=${0}
        .header=${0}
      >
        <div class="columns">
          ${0}
          ${0}
        </div>
      </hass-subpage>
    `),this.hass,this.narrow,k.C1,this.knx.localize(k.SC.translationKey),this._renderInfoCard(),this.knx.projectInfo?this._renderProjectDataCard(this.knx.projectInfo):h.s6)}},{key:"_renderInfoCard",value:function(){return(0,h.qy)(_||(_=A` <ha-card class="knx-info">
      <div class="card-content knx-info-section">
        <div class="knx-content-row header">${0}</div>

        <div class="knx-content-row">
          <div>XKNX Version</div>
          <div>${0}</div>
        </div>

        <div class="knx-content-row">
          <div>KNX-Frontend Version</div>
          <div>${0}</div>
        </div>

        <div class="knx-content-row">
          <div>${0}</div>
          <div>
            ${0}
          </div>
        </div>

        <div class="knx-content-row">
          <div>${0}</div>
          <div>${0}</div>
        </div>

        <div class="knx-bug-report">
          ${0}
          <a href="https://github.com/XKNX/knx-integration" target="_blank">xknx/knx-integration</a>
        </div>

        <div class="knx-bug-report">
          ${0}
          <a href="https://my.knx.org" target="_blank">my.knx.org</a>
        </div>
      </div>
    </ha-card>`),this.knx.localize("info_information_header"),this.knx.connectionInfo.version,m.x,this.knx.localize("info_connected_to_bus"),this.hass.localize(this.knx.connectionInfo.connected?"ui.common.yes":"ui.common.no"),this.knx.localize("info_individual_address"),this.knx.connectionInfo.current_address,this.knx.localize("info_issue_tracker"),this.knx.localize("info_my_knx"))}},{key:"_renderProjectDataCard",value:function(o){return(0,h.qy)($||($=A`
      <ha-card class="knx-info">
          <div class="card-content knx-content">
            <div class="header knx-content-row">
              ${0}
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-content-row">
              <div>${0}</div>
              <div>${0}</div>
            </div>
            <div class="knx-button-row">
              <ha-button
                class="knx-warning push-right"
                @click=${0}
                >
                ${0}
              </ha-button>
            </div>
          </div>
        </div>
      </ha-card>
    `),this.knx.localize("info_project_data_header"),this.knx.localize("info_project_data_name"),o.name,this.knx.localize("info_project_data_last_modified"),new Date(o.last_modified).toUTCString(),this.knx.localize("info_project_data_tool_version"),o.tool_version,this.knx.localize("info_project_data_xknxproject_version"),o.xknxproject_version,this._removeProject,this.knx.localize("info_project_delete"))}},{key:"_removeProject",value:(a=(0,n.A)((0,e.A)().m((function o(t){var a;return(0,e.A)().w((function(o){for(;;)switch(o.p=o.n){case 0:return o.n=1,(0,b.dk)(this,{text:this.knx.localize("info_project_delete")});case 1:if(o.v){o.n=2;break}return z.debug("User cancelled deletion"),o.a(2);case 2:return o.p=2,o.n=3,(0,g.gV)(this.hass);case 3:o.n=5;break;case 4:o.p=4,a=o.v,(0,b.K$)(this,{title:"Deletion failed",text:(0,f.VR)(a)});case 5:return o.p=5,(0,u.r)(this,"knx-reload"),o.f(5);case 6:return o.a(2)}}),o,this,[[2,4,5,6]])}))),function(o){return a.apply(this,arguments)})}]);var a}(h.WF);P.styles=(0,h.AH)(j||(j=A`
    .columns {
      display: flex;
      justify-content: center;
    }

    @media screen and (max-width: 1232px) {
      .columns {
        flex-direction: column;
      }

      .knx-button-row {
        margin-top: 20px;
      }

      .knx-info {
        margin-right: 8px;
      }
    }

    @media screen and (min-width: 1233px) {
      .knx-button-row {
        margin-top: auto;
      }

      .knx-info {
        width: 400px;
      }
    }

    .knx-info {
      margin-left: 8px;
      margin-top: 8px;
    }

    .knx-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      box-sizing: border-box;
    }

    .knx-content-row {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
    }

    .knx-content-row > div:nth-child(2) {
      margin-left: 1rem;
    }

    .knx-button-row {
      display: flex;
      flex-direction: row;
      gap: 8px;
      vertical-align: bottom;
      padding-top: 16px;
    }

    .push-left {
      margin-right: auto;
    }

    .push-right {
      margin-left: auto;
    }

    .knx-warning {
      --mdc-theme-primary: var(--error-color);
    }

    .knx-delete-project-button {
      position: absolute;
      bottom: 0;
      right: 0;
    }

    .knx-bug-report {
      margin-top: 20px;

      a {
        text-decoration: none;
      }
    }

    .header {
      color: var(--ha-card-header-color, --primary-text-color);
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, 24px);
      letter-spacing: -0.012em;
      line-height: 48px;
      padding: -4px 16px 16px;
      display: inline-block;
      margin-block-start: 0px;
      margin-block-end: 4px;
      font-weight: normal;
    }
  `)),(0,d.__decorate)([(0,v.MZ)({type:Object})],P.prototype,"hass",void 0),(0,d.__decorate)([(0,v.MZ)({attribute:!1})],P.prototype,"knx",void 0),(0,d.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],P.prototype,"narrow",void 0),(0,d.__decorate)([(0,v.MZ)({type:Object})],P.prototype,"route",void 0),P=(0,d.__decorate)([(0,v.EM)("knx-info")],P),r()}catch(S){r(S)}}))},28345:function(o,t,a){a.d(t,{qy:function(){return d},eu:function(){return l}});var r=a(94741),e=(a(16280),a(28706),a(23792),a(44114),a(72712),a(18111),a(18237),a(36033),a(26099),a(62953),a(4610)),n=Symbol.for(""),i=o=>{if((null==o?void 0:o.r)===n)return null==o?void 0:o._$litStatic$},l=function(o){for(var t=arguments.length,a=new Array(t>1?t-1:0),r=1;r<t;r++)a[r-1]=arguments[r];return{_$litStatic$:a.reduce(((t,a,r)=>t+(o=>{if(void 0!==o._$litStatic$)return o._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${o}. Use 'unsafeStatic' to pass non-literal values, but\n            take care to ensure page security.`)})(a)+o[r+1]),o[0]),r:n}},c=new Map,s=o=>function(t){for(var a=arguments.length,e=new Array(a>1?a-1:0),n=1;n<a;n++)e[n-1]=arguments[n];for(var l,s,d,h=e.length,v=[],u=[],p=0,f=!1;p<h;){for(d=t[p];p<h&&void 0!==(s=e[p],l=i(s));)d+=l+t[++p],f=!0;p!==h&&u.push(s),v.push(d),p++}if(p===h&&v.push(t[h]),f){var b=v.join("$$lit$$");void 0===(t=c.get(b))&&(v.raw=v,c.set(b,t=v)),e=u}return o.apply(void 0,[t].concat((0,r.A)(e)))},d=s(e.qy);s(e.JW),s(e.ej)}}]);
//# sourceMappingURL=2913.5b1cf77945926a0a.js.map