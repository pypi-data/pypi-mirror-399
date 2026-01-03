export const __webpack_id__="7257";export const __webpack_ids__=["7257"];export const __webpack_modules__={55376:function(t,a,e){function o(t){return null==t||Array.isArray(t)?t:[t]}e.d(a,{e:()=>o})},92209:function(t,a,e){e.d(a,{x:()=>o});const o=(t,a)=>t&&t.config.components.includes(a)},84884:function(t,a,e){var o=e(62826),r=e(96196),i=e(77845),n=e(94333),s=e(22786),l=e(55376),c=e(92209);const d=(t,a)=>!a.component||(0,l.e)(a.component).some((a=>(0,c.x)(t,a))),h=(t,a)=>!a.not_component||!(0,l.e)(a.not_component).some((a=>(0,c.x)(t,a))),p=t=>t.core,b=(t,a)=>(t=>t.advancedOnly)(a)&&!(t=>t.userData?.showAdvanced)(t);var v=e(5871),f=e(39501),x=(e(371),e(45397),e(60961),e(32288));e(95591);class g extends r.WF{render(){return r.qy`
      <div
        tabindex="0"
        role="tab"
        aria-selected=${this.active}
        aria-label=${(0,x.J)(this.name)}
        @keydown=${this._handleKeyDown}
      >
        ${this.narrow?r.qy`<slot name="icon"></slot>`:""}
        <span class="name">${this.name}</span>
        <ha-ripple></ha-ripple>
      </div>
    `}_handleKeyDown(t){"Enter"===t.key&&t.target.click()}constructor(...t){super(...t),this.active=!1,this.narrow=!1}}g.styles=r.AH`
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
  `,(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],g.prototype,"active",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],g.prototype,"narrow",void 0),(0,o.__decorate)([(0,i.MZ)()],g.prototype,"name",void 0),g=(0,o.__decorate)([(0,i.EM)("ha-tab")],g);var y=e(39396);class m extends r.WF{willUpdate(t){t.has("route")&&(this._activeTab=this.tabs.find((t=>`${this.route.prefix}${this.route.path}`.includes(t.path)))),super.willUpdate(t)}render(){const t=this._getTabs(this.tabs,this._activeTab,this.hass.config.components,this.hass.language,this.hass.userData,this.narrow,this.localizeFunc||this.hass.localize),a=t.length>1;return r.qy`
      <div class="toolbar">
        <slot name="toolbar">
          <div class="toolbar-content">
            ${this.mainPage||!this.backPath&&history.state?.root?r.qy`
                  <ha-menu-button
                    .hassio=${this.supervisor}
                    .hass=${this.hass}
                    .narrow=${this.narrow}
                  ></ha-menu-button>
                `:this.backPath?r.qy`
                    <a href=${this.backPath}>
                      <ha-icon-button-arrow-prev
                        .hass=${this.hass}
                      ></ha-icon-button-arrow-prev>
                    </a>
                  `:r.qy`
                    <ha-icon-button-arrow-prev
                      .hass=${this.hass}
                      @click=${this._backTapped}
                    ></ha-icon-button-arrow-prev>
                  `}
            ${this.narrow||!a?r.qy`<div class="main-title">
                  <slot name="header">${a?"":t[0]}</slot>
                </div>`:""}
            ${a&&!this.narrow?r.qy`<div id="tabbar">${t}</div>`:""}
            <div id="toolbar-icon">
              <slot name="toolbar-icon"></slot>
            </div>
          </div>
        </slot>
        ${a&&this.narrow?r.qy`<div id="tabbar" class="bottom-bar">${t}</div>`:""}
      </div>
      <div
        class=${(0,n.H)({container:!0,tabs:a&&this.narrow})}
      >
        ${this.pane?r.qy`<div class="pane">
              <div class="shadow-container"></div>
              <div class="ha-scrollbar">
                <slot name="pane"></slot>
              </div>
            </div>`:r.s6}
        <div
          class="content ha-scrollbar ${(0,n.H)({tabs:a})}"
          @scroll=${this._saveScrollPos}
        >
          <slot></slot>
          ${this.hasFab?r.qy`<div class="fab-bottom-space"></div>`:r.s6}
        </div>
      </div>
      <div id="fab" class=${(0,n.H)({tabs:a})}>
        <slot name="fab"></slot>
      </div>
    `}_saveScrollPos(t){this._savedScrollPos=t.target.scrollTop}_backTapped(){this.backCallback?this.backCallback():(0,v.O)()}static get styles(){return[y.dp,r.AH`
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
      `]}constructor(...t){super(...t),this.supervisor=!1,this.mainPage=!1,this.narrow=!1,this.isWide=!1,this.pane=!1,this.hasFab=!1,this._getTabs=(0,s.A)(((t,a,e,o,i,n,s)=>{const l=t.filter((t=>((t,a)=>(p(a)||d(t,a))&&!b(t,a)&&h(t,a))(this.hass,t)));if(l.length<2){if(1===l.length){const t=l[0];return[t.translationKey?s(t.translationKey):t.name]}return[""]}return l.map((t=>r.qy`
          <a href=${t.path}>
            <ha-tab
              .hass=${this.hass}
              .active=${t.path===a?.path}
              .narrow=${this.narrow}
              .name=${t.translationKey?s(t.translationKey):t.name}
            >
              ${t.iconPath?r.qy`<ha-svg-icon
                    slot="icon"
                    .path=${t.iconPath}
                  ></ha-svg-icon>`:""}
            </ha-tab>
          </a>
        `))}))}}(0,o.__decorate)([(0,i.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean})],m.prototype,"supervisor",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],m.prototype,"localizeFunc",void 0),(0,o.__decorate)([(0,i.MZ)({type:String,attribute:"back-path"})],m.prototype,"backPath",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],m.prototype,"backCallback",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,attribute:"main-page"})],m.prototype,"mainPage",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],m.prototype,"route",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],m.prototype,"tabs",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],m.prototype,"narrow",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0,attribute:"is-wide"})],m.prototype,"isWide",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean})],m.prototype,"pane",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,attribute:"has-fab"})],m.prototype,"hasFab",void 0),(0,o.__decorate)([(0,i.wk)()],m.prototype,"_activeTab",void 0),(0,o.__decorate)([(0,f.a)(".content")],m.prototype,"_savedScrollPos",void 0),(0,o.__decorate)([(0,i.Ls)({passive:!0})],m.prototype,"_saveScrollPos",null),m=(0,o.__decorate)([(0,i.EM)("hass-tabs-subpage")],m)},64576:function(t,a,e){e.a(t,(async function(t,o){try{e.r(a),e.d(a,{KNXError:()=>d});var r=e(62826),i=e(96196),n=e(77845),s=e(76679),l=(e(84884),e(49339)),c=t([l]);l=(c.then?(await c)():c)[0];class d extends i.WF{render(){const t=s.G.history.state?.message??"Unknown error";return i.qy`
      <hass-error-screen
        .hass=${this.hass}
        .error=${t}
        .toolbar=${!0}
        .rootnav=${!1}
        .narrow=${this.narrow}
      ></hass-error-screen>
    `}}(0,r.__decorate)([(0,n.MZ)({type:Object})],d.prototype,"hass",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:!1})],d.prototype,"knx",void 0),(0,r.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],d.prototype,"narrow",void 0),(0,r.__decorate)([(0,n.MZ)({type:Object})],d.prototype,"route",void 0),(0,r.__decorate)([(0,n.MZ)({type:Array,reflect:!1})],d.prototype,"tabs",void 0),d=(0,r.__decorate)([(0,n.EM)("knx-error")],d),o()}catch(d){o(d)}}))}};
//# sourceMappingURL=7257.db7a201503b837b2.js.map