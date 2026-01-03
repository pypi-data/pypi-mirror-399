"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1656"],{92209:function(e,t,n){n.d(t,{x:function(){return i}});n(74423);var i=(e,t)=>e&&e.config.components.includes(t)},55124:function(e,t,n){n.d(t,{d:function(){return i}});var i=e=>e.stopPropagation()},75261:function(e,t,n){var i=n(56038),a=n(44734),o=n(69683),r=n(6454),s=n(62826),l=n(70402),c=n(11081),u=n(77845),d=function(e){function t(){return(0,a.A)(this,t),(0,o.A)(this,t,arguments)}return(0,r.A)(t,e),(0,i.A)(t)}(l.iY);d.styles=c.R,d=(0,s.__decorate)([(0,u.EM)("ha-list")],d)},1554:function(e,t,n){var i,a=n(44734),o=n(56038),r=n(69683),s=n(6454),l=n(62826),c=n(43976),u=n(703),d=n(96196),h=n(77845),p=n(94333),_=(n(75261),e=>e),v=function(e){function t(){return(0,a.A)(this,t),(0,r.A)(this,t,arguments)}return(0,s.A)(t,e),(0,o.A)(t,[{key:"listElement",get:function(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}},{key:"renderList",value:function(){var e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return(0,d.qy)(i||(i=_`<ha-list
      rootTabbable
      .innerAriaLabel=${0}
      .innerRole=${0}
      .multi=${0}
      class=${0}
      .itemRoles=${0}
      .wrapFocus=${0}
      .activatable=${0}
      @action=${0}
    >
      <slot></slot>
    </ha-list>`),this.innerAriaLabel,this.innerRole,this.multi,(0,p.H)(t),e,this.wrapFocus,this.activatable,this.onAction)}}])}(c.ZR);v.styles=u.R,v=(0,l.__decorate)([(0,h.EM)("ha-menu")],v)},69869:function(e,t,n){var i,a,o,r,s,l=n(61397),c=n(50264),u=n(44734),d=n(56038),h=n(69683),p=n(6454),_=n(25460),v=(n(28706),n(62826)),f=n(14540),m=n(63125),A=n(96196),y=n(77845),b=n(94333),k=n(40404),g=n(99034),$=(n(60733),n(1554),e=>e),M=function(e){function t(){var e;(0,u.A)(this,t);for(var n=arguments.length,i=new Array(n),a=0;a<n;a++)i[a]=arguments[a];return(e=(0,h.A)(this,t,[].concat(i))).icon=!1,e.clearable=!1,e.inlineArrow=!1,e._translationsUpdated=(0,k.s)((0,c.A)((0,l.A)().m((function t(){return(0,l.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,g.E)();case 1:e.layoutOptions();case 2:return t.a(2)}}),t)}))),500),e}return(0,p.A)(t,e),(0,d.A)(t,[{key:"render",value:function(){return(0,A.qy)(i||(i=$`
      ${0}
      ${0}
    `),(0,_.A)(t,"render",this,3)([]),this.clearable&&!this.required&&!this.disabled&&this.value?(0,A.qy)(a||(a=$`<ha-icon-button
            label="clear"
            @click=${0}
            .path=${0}
          ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):A.s6)}},{key:"renderMenu",value:function(){var e=this.getMenuClasses();return(0,A.qy)(o||(o=$`<ha-menu
      innerRole="listbox"
      wrapFocus
      class=${0}
      activatable
      .fullwidth=${0}
      .open=${0}
      .anchor=${0}
      .fixed=${0}
      @selected=${0}
      @opened=${0}
      @closed=${0}
      @items-updated=${0}
      @keydown=${0}
    >
      ${0}
    </ha-menu>`),(0,b.H)(e),!this.fixedMenuPosition&&!this.naturalMenuWidth,this.menuOpen,this.anchorElement,this.fixedMenuPosition,this.onSelected,this.onOpened,this.onClosed,this.onItemsUpdated,this.handleTypeahead,this.renderMenuContent())}},{key:"renderLeadingIcon",value:function(){return this.icon?(0,A.qy)(r||(r=$`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`)):A.s6}},{key:"connectedCallback",value:function(){(0,_.A)(t,"connectedCallback",this,3)([]),window.addEventListener("translations-updated",this._translationsUpdated)}},{key:"firstUpdated",value:(n=(0,c.A)((0,l.A)().m((function e(){var n;return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:(0,_.A)(t,"firstUpdated",this,3)([]),this.inlineArrow&&(null===(n=this.shadowRoot)||void 0===n||null===(n=n.querySelector(".mdc-select__selected-text-container"))||void 0===n||n.classList.add("inline-arrow"));case 1:return e.a(2)}}),e,this)}))),function(){return n.apply(this,arguments)})},{key:"updated",value:function(e){if((0,_.A)(t,"updated",this,3)([e]),e.has("inlineArrow")){var n,i=null===(n=this.shadowRoot)||void 0===n?void 0:n.querySelector(".mdc-select__selected-text-container");this.inlineArrow?null==i||i.classList.add("inline-arrow"):null==i||i.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}},{key:"disconnectedCallback",value:function(){(0,_.A)(t,"disconnectedCallback",this,3)([]),window.removeEventListener("translations-updated",this._translationsUpdated)}},{key:"_clearValue",value:function(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}}]);var n}(f.o);M.styles=[m.R,(0,A.AH)(s||(s=$`
      :host([clearable]) {
        position: relative;
      }
      .mdc-select:not(.mdc-select--disabled) .mdc-select__icon {
        color: var(--secondary-text-color);
      }
      .mdc-select__anchor {
        width: var(--ha-select-min-width, 200px);
      }
      .mdc-select--filled .mdc-select__anchor {
        height: var(--ha-select-height, 56px);
      }
      .mdc-select--filled .mdc-floating-label {
        inset-inline-start: var(--ha-space-4);
        inset-inline-end: initial;
        direction: var(--direction);
      }
      .mdc-select--filled.mdc-select--with-leading-icon .mdc-floating-label {
        inset-inline-start: 48px;
        inset-inline-end: initial;
        direction: var(--direction);
      }
      .mdc-select .mdc-select__anchor {
        padding-inline-start: var(--ha-space-4);
        padding-inline-end: 0px;
        direction: var(--direction);
      }
      .mdc-select__anchor .mdc-floating-label--float-above {
        transform-origin: var(--float-start);
      }
      .mdc-select__selected-text-container {
        padding-inline-end: var(--select-selected-text-padding-end, 0px);
      }
      :host([clearable]) .mdc-select__selected-text-container {
        padding-inline-end: var(
          --select-selected-text-padding-end,
          var(--ha-space-4)
        );
      }
      ha-icon-button {
        position: absolute;
        top: 10px;
        right: 28px;
        --mdc-icon-button-size: 36px;
        --mdc-icon-size: 20px;
        color: var(--secondary-text-color);
        inset-inline-start: initial;
        inset-inline-end: 28px;
        direction: var(--direction);
      }
      .inline-arrow {
        flex-grow: 0;
      }
    `))],(0,v.__decorate)([(0,y.MZ)({type:Boolean})],M.prototype,"icon",void 0),(0,v.__decorate)([(0,y.MZ)({type:Boolean,reflect:!0})],M.prototype,"clearable",void 0),(0,v.__decorate)([(0,y.MZ)({attribute:"inline-arrow",type:Boolean})],M.prototype,"inlineArrow",void 0),(0,v.__decorate)([(0,y.MZ)()],M.prototype,"options",void 0),M=(0,v.__decorate)([(0,y.EM)("ha-select")],M)},66971:function(e,t,n){n.r(t),n.d(t,{HaBackupLocationSelector:function(){return H}});var i,a,o,r,s,l=n(44734),c=n(56038),u=n(69683),d=n(6454),h=(n(28706),n(62826)),p=n(96196),_=n(77845),v=n(61397),f=n(50264),m=(n(2008),n(74423),n(62062),n(26910),n(18111),n(22489),n(61701),n(26099),n(22786)),A=n(92209),y=n(92542),b=n(55124),k=n(25749),g=function(e){return e.BIND="bind",e.CIFS="cifs",e.NFS="nfs",e}({}),$=function(e){return e.BACKUP="backup",e.MEDIA="media",e.SHARE="share",e}({}),M=function(){var e=(0,f.A)((0,v.A)().m((function e(t){return(0,v.A)().w((function(e){for(;;)if(0===e.n)return e.a(2,t.callWS({type:"supervisor/api",endpoint:"/mounts",method:"get",timeout:null}))}),e)})));return function(t){return e.apply(this,arguments)}}(),w=(n(17963),n(56565),n(69869),e=>e),L="/backup",C=function(e){function t(){var e;(0,l.A)(this,t);for(var n=arguments.length,i=new Array(n),a=0;a<n;a++)i[a]=arguments[a];return(e=(0,u.A)(this,t,[].concat(i))).disabled=!1,e.required=!1,e._filterMounts=(0,m.A)(((t,n)=>{var i=t.mounts.filter((e=>[g.CIFS,g.NFS].includes(e.type)));return n&&(i=t.mounts.filter((e=>e.usage===n))),i.sort(((n,i)=>n.name===t.default_backup_mount?-1:i.name===t.default_backup_mount?1:(0,k.SH)(n.name,i.name,e.hass.locale.language)))})),e}return(0,d.A)(t,e),(0,c.A)(t,[{key:"firstUpdated",value:function(){this._getMounts()}},{key:"render",value:function(){if(this._error)return(0,p.qy)(i||(i=w`<ha-alert alert-type="error">${0}</ha-alert>`),this._error);if(!this._mounts)return p.s6;var e=(0,p.qy)(a||(a=w`<ha-list-item
      graphic="icon"
      .value=${0}
    >
      <span>
        ${0}
      </span>
      <ha-svg-icon slot="graphic" .path=${0}></ha-svg-icon>
    </ha-list-item>`),L,this.hass.localize("ui.components.mount-picker.use_datadisk")||"Use data disk for backup","M6,2H18A2,2 0 0,1 20,4V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V4A2,2 0 0,1 6,2M12,4A6,6 0 0,0 6,10C6,13.31 8.69,16 12.1,16L11.22,13.77C10.95,13.29 11.11,12.68 11.59,12.4L12.45,11.9C12.93,11.63 13.54,11.79 13.82,12.27L15.74,14.69C17.12,13.59 18,11.9 18,10A6,6 0 0,0 12,4M12,9A1,1 0 0,1 13,10A1,1 0 0,1 12,11A1,1 0 0,1 11,10A1,1 0 0,1 12,9M7,18A1,1 0 0,0 6,19A1,1 0 0,0 7,20A1,1 0 0,0 8,19A1,1 0 0,0 7,18M12.09,13.27L14.58,19.58L17.17,18.08L12.95,12.77L12.09,13.27Z");return(0,p.qy)(o||(o=w`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        .helper=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${0}
        ${0}
        ${0}
      </ha-select>
    `),void 0===this.label&&this.hass?this.hass.localize("ui.components.mount-picker.mount"):this.label,this._value,this.required,this.disabled,this.helper,this._mountChanged,b.d,this.usage!==$.BACKUP||this._mounts.default_backup_mount&&this._mounts.default_backup_mount!==L?p.s6:e,this._filterMounts(this._mounts,this.usage).map((e=>(0,p.qy)(r||(r=w`<ha-list-item twoline graphic="icon" .value=${0}>
              <span>${0}</span>
              <span slot="secondary"
                >${0}${0}${0}</span
              >
              <ha-svg-icon
                slot="graphic"
                .path=${0}
              ></ha-svg-icon>
            </ha-list-item>`),e.name,e.name,e.server,e.port?`:${e.port}`:p.s6,e.type===g.NFS?e.path:`:${e.share}`,e.usage===$.MEDIA?"M19 3H5C3.89 3 3 3.89 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.89 20.1 3 19 3M10 16V8L15 12":e.usage===$.SHARE?"M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z":"M12,3A9,9 0 0,0 3,12H0L4,16L8,12H5A7,7 0 0,1 12,5A7,7 0 0,1 19,12A7,7 0 0,1 12,19C10.5,19 9.09,18.5 7.94,17.7L6.5,19.14C8.04,20.3 9.94,21 12,21A9,9 0 0,0 21,12A9,9 0 0,0 12,3M14,12A2,2 0 0,0 12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12Z"))),this.usage===$.BACKUP&&this._mounts.default_backup_mount?e:p.s6)}},{key:"_getMounts",value:(n=(0,f.A)((0,v.A)().m((function e(){return(0,v.A)().w((function(e){for(;;)switch(e.p=e.n){case 0:if(e.p=0,!(0,A.x)(this.hass,"hassio")){e.n=2;break}return e.n=1,M(this.hass);case 1:this._mounts=e.v,this.usage!==$.BACKUP||this.value||(this.value=this._mounts.default_backup_mount||L),e.n=3;break;case 2:this._error=this.hass.localize("ui.components.mount-picker.error.no_supervisor");case 3:e.n=5;break;case 4:e.p=4,e.v,this._error=this.hass.localize("ui.components.mount-picker.error.fetch_mounts");case 5:return e.a(2)}}),e,this,[[0,4]])}))),function(){return n.apply(this,arguments)})},{key:"_value",get:function(){return this.value||""}},{key:"_mountChanged",value:function(e){e.stopPropagation();var t=e.target.value;t!==this._value&&this._setValue(t)}},{key:"_setValue",value:function(e){this.value=e,setTimeout((()=>{(0,y.r)(this,"value-changed",{value:e}),(0,y.r)(this,"change")}),0)}}],[{key:"styles",get:function(){return[(0,p.AH)(s||(s=w`
        ha-select {
          width: 100%;
        }
      `))]}}]);var n}(p.WF);(0,h.__decorate)([(0,_.MZ)()],C.prototype,"label",void 0),(0,h.__decorate)([(0,_.MZ)()],C.prototype,"value",void 0),(0,h.__decorate)([(0,_.MZ)()],C.prototype,"helper",void 0),(0,h.__decorate)([(0,_.MZ)({type:Boolean})],C.prototype,"disabled",void 0),(0,h.__decorate)([(0,_.MZ)({type:Boolean})],C.prototype,"required",void 0),(0,h.__decorate)([(0,_.MZ)()],C.prototype,"usage",void 0),(0,h.__decorate)([(0,_.wk)()],C.prototype,"_mounts",void 0),(0,h.__decorate)([(0,_.wk)()],C.prototype,"_error",void 0),C=(0,h.__decorate)([(0,_.EM)("ha-mount-picker")],C);var x,q,Z=e=>e,H=function(e){function t(){var e;(0,l.A)(this,t);for(var n=arguments.length,i=new Array(n),a=0;a<n;a++)i[a]=arguments[a];return(e=(0,u.A)(this,t,[].concat(i))).disabled=!1,e.required=!0,e}return(0,d.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){return(0,p.qy)(x||(x=Z`<ha-mount-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .disabled=${0}
      .required=${0}
      usage="backup"
    ></ha-mount-picker>`),this.hass,this.value,this.label,this.helper,this.disabled,this.required)}}])}(p.WF);H.styles=(0,p.AH)(q||(q=Z`
    ha-mount-picker {
      width: 100%;
    }
  `)),(0,h.__decorate)([(0,_.MZ)({attribute:!1})],H.prototype,"hass",void 0),(0,h.__decorate)([(0,_.MZ)({attribute:!1})],H.prototype,"selector",void 0),(0,h.__decorate)([(0,_.MZ)()],H.prototype,"value",void 0),(0,h.__decorate)([(0,_.MZ)()],H.prototype,"label",void 0),(0,h.__decorate)([(0,_.MZ)()],H.prototype,"helper",void 0),(0,h.__decorate)([(0,_.MZ)({type:Boolean})],H.prototype,"disabled",void 0),(0,h.__decorate)([(0,_.MZ)({type:Boolean})],H.prototype,"required",void 0),H=(0,h.__decorate)([(0,_.EM)("ha-selector-backup_location")],H)}}]);
//# sourceMappingURL=1656.4ed66f5bd827c623.js.map