"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5487"],{55124:function(e,t,i){i.d(t,{d:function(){return n}});var n=e=>e.stopPropagation()},75261:function(e,t,i){var n=i(56038),a=i(44734),s=i(69683),r=i(6454),o=i(62826),l=i(70402),d=i(11081),c=i(77845),u=function(e){function t(){return(0,a.A)(this,t),(0,s.A)(this,t,arguments)}return(0,r.A)(t,e),(0,n.A)(t)}(l.iY);u.styles=d.R,u=(0,o.__decorate)([(0,c.EM)("ha-list")],u)},1554:function(e,t,i){var n,a=i(44734),s=i(56038),r=i(69683),o=i(6454),l=i(62826),d=i(43976),c=i(703),u=i(96196),h=i(77845),v=i(94333),p=(i(75261),e=>e),_=function(e){function t(){return(0,a.A)(this,t),(0,r.A)(this,t,arguments)}return(0,o.A)(t,e),(0,s.A)(t,[{key:"listElement",get:function(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}},{key:"renderList",value:function(){var e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return(0,u.qy)(n||(n=p`<ha-list
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
    </ha-list>`),this.innerAriaLabel,this.innerRole,this.multi,(0,v.H)(t),e,this.wrapFocus,this.activatable,this.onAction)}}])}(d.ZR);_.styles=c.R,_=(0,l.__decorate)([(0,h.EM)("ha-menu")],_)},69869:function(e,t,i){var n,a,s,r,o,l=i(61397),d=i(50264),c=i(44734),u=i(56038),h=i(69683),v=i(6454),p=i(25460),_=(i(28706),i(62826)),g=i(14540),f=i(63125),y=i(96196),b=i(77845),m=i(94333),A=i(40404),$=i(99034),w=(i(60733),i(1554),e=>e),k=function(e){function t(){var e;(0,c.A)(this,t);for(var i=arguments.length,n=new Array(i),a=0;a<i;a++)n[a]=arguments[a];return(e=(0,h.A)(this,t,[].concat(n))).icon=!1,e.clearable=!1,e.inlineArrow=!1,e._translationsUpdated=(0,A.s)((0,d.A)((0,l.A)().m((function t(){return(0,l.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,$.E)();case 1:e.layoutOptions();case 2:return t.a(2)}}),t)}))),500),e}return(0,v.A)(t,e),(0,u.A)(t,[{key:"render",value:function(){return(0,y.qy)(n||(n=w`
      ${0}
      ${0}
    `),(0,p.A)(t,"render",this,3)([]),this.clearable&&!this.required&&!this.disabled&&this.value?(0,y.qy)(a||(a=w`<ha-icon-button
            label="clear"
            @click=${0}
            .path=${0}
          ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):y.s6)}},{key:"renderMenu",value:function(){var e=this.getMenuClasses();return(0,y.qy)(s||(s=w`<ha-menu
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
    </ha-menu>`),(0,m.H)(e),!this.fixedMenuPosition&&!this.naturalMenuWidth,this.menuOpen,this.anchorElement,this.fixedMenuPosition,this.onSelected,this.onOpened,this.onClosed,this.onItemsUpdated,this.handleTypeahead,this.renderMenuContent())}},{key:"renderLeadingIcon",value:function(){return this.icon?(0,y.qy)(r||(r=w`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`)):y.s6}},{key:"connectedCallback",value:function(){(0,p.A)(t,"connectedCallback",this,3)([]),window.addEventListener("translations-updated",this._translationsUpdated)}},{key:"firstUpdated",value:(i=(0,d.A)((0,l.A)().m((function e(){var i;return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:(0,p.A)(t,"firstUpdated",this,3)([]),this.inlineArrow&&(null===(i=this.shadowRoot)||void 0===i||null===(i=i.querySelector(".mdc-select__selected-text-container"))||void 0===i||i.classList.add("inline-arrow"));case 1:return e.a(2)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"updated",value:function(e){if((0,p.A)(t,"updated",this,3)([e]),e.has("inlineArrow")){var i,n=null===(i=this.shadowRoot)||void 0===i?void 0:i.querySelector(".mdc-select__selected-text-container");this.inlineArrow?null==n||n.classList.add("inline-arrow"):null==n||n.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}},{key:"disconnectedCallback",value:function(){(0,p.A)(t,"disconnectedCallback",this,3)([]),window.removeEventListener("translations-updated",this._translationsUpdated)}},{key:"_clearValue",value:function(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}}]);var i}(g.o);k.styles=[f.R,(0,y.AH)(o||(o=w`
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
    `))],(0,_.__decorate)([(0,b.MZ)({type:Boolean})],k.prototype,"icon",void 0),(0,_.__decorate)([(0,b.MZ)({type:Boolean,reflect:!0})],k.prototype,"clearable",void 0),(0,_.__decorate)([(0,b.MZ)({attribute:"inline-arrow",type:Boolean})],k.prototype,"inlineArrow",void 0),(0,_.__decorate)([(0,b.MZ)()],k.prototype,"options",void 0),k=(0,_.__decorate)([(0,b.EM)("ha-select")],k)},34818:function(e,t,i){i.r(t),i.d(t,{HaTTSSelector:function(){return Z}});var n,a,s,r,o=i(44734),l=i(56038),d=i(69683),c=i(6454),u=(i(28706),i(62826)),h=i(96196),v=i(77845),p=i(61397),_=i(50264),g=i(31432),f=i(25460),y=(i(50113),i(74423),i(62062),i(18111),i(20116),i(61701),i(26099),i(16034),i(92542)),b=i(55124),m=i(91889),A=i(40404),$=i(62146),w=(i(56565),i(69869),i(41144)),k=e=>e,M="__NONE_OPTION__",x=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,n=new Array(i),a=0;a<i;a++)n[a]=arguments[a];return(e=(0,d.A)(this,t,[].concat(n))).disabled=!1,e.required=!1,e._debouncedUpdateEngines=(0,A.s)((()=>e._updateEngines()),500),e}return(0,c.A)(t,e),(0,l.A)(t,[{key:"render",value:function(){if(!this._engines)return h.s6;var e=this.value;if(!e&&this.required){for(var t=0,i=Object.values(this.hass.entities);t<i.length;t++){var r=i[t];if("cloud"===r.platform&&"tts"===(0,w.m)(r.entity_id)){e=r.entity_id;break}}if(!e){var o,l=(0,g.A)(this._engines);try{for(l.s();!(o=l.n()).done;){var d,c=o.value;if(0!==(null==c||null===(d=c.supported_languages)||void 0===d?void 0:d.length)){e=c.engine_id;break}}}catch(u){l.e(u)}finally{l.f()}}}return e||(e=M),(0,h.qy)(n||(n=k`
      <ha-select
        .label=${0}
        .value=${0}
        .required=${0}
        .disabled=${0}
        @selected=${0}
        @closed=${0}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${0}
        ${0}
      </ha-select>
    `),this.label||this.hass.localize("ui.components.tts-picker.tts"),e,this.required,this.disabled,this._changed,b.d,this.required?h.s6:(0,h.qy)(a||(a=k`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),M,this.hass.localize("ui.components.tts-picker.none")),this._engines.map((t=>{var i,n;if(t.deprecated&&t.engine_id!==e)return h.s6;if(t.engine_id.includes(".")){var a=this.hass.states[t.engine_id];n=a?(0,m.u)(a):t.engine_id}else n=t.name||t.engine_id;return(0,h.qy)(s||(s=k`<ha-list-item
            .value=${0}
            .disabled=${0}
          >
            ${0}
          </ha-list-item>`),t.engine_id,0===(null===(i=t.supported_languages)||void 0===i?void 0:i.length),n)})))}},{key:"willUpdate",value:function(e){(0,f.A)(t,"willUpdate",this,3)([e]),this.hasUpdated?e.has("language")&&this._debouncedUpdateEngines():this._updateEngines()}},{key:"_updateEngines",value:(i=(0,_.A)((0,p.A)().m((function e(){var t,i;return(0,p.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,(0,$.Xv)(this.hass,this.language,this.hass.config.country||void 0);case 1:if(this._engines=e.v.providers,this.value){e.n=2;break}return e.a(2);case 2:i=this._engines.find((e=>e.engine_id===this.value)),(0,y.r)(this,"supported-languages-changed",{value:null==i?void 0:i.supported_languages}),i&&0!==(null===(t=i.supported_languages)||void 0===t?void 0:t.length)||(this.value=void 0,(0,y.r)(this,"value-changed",{value:this.value}));case 3:return e.a(2)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"_changed",value:function(e){var t,i=e.target;!this.hass||""===i.value||i.value===this.value||void 0===this.value&&i.value===M||(this.value=i.value===M?void 0:i.value,(0,y.r)(this,"value-changed",{value:this.value}),(0,y.r)(this,"supported-languages-changed",{value:null===(t=this._engines.find((e=>e.engine_id===this.value)))||void 0===t?void 0:t.supported_languages}))}}]);var i}(h.WF);x.styles=(0,h.AH)(r||(r=k`
    ha-select {
      width: 100%;
    }
  `)),(0,u.__decorate)([(0,v.MZ)()],x.prototype,"value",void 0),(0,u.__decorate)([(0,v.MZ)()],x.prototype,"label",void 0),(0,u.__decorate)([(0,v.MZ)()],x.prototype,"language",void 0),(0,u.__decorate)([(0,v.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],x.prototype,"disabled",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean})],x.prototype,"required",void 0),(0,u.__decorate)([(0,v.wk)()],x.prototype,"_engines",void 0),x=(0,u.__decorate)([(0,v.EM)("ha-tts-picker")],x);var q,L,E=e=>e,Z=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,n=new Array(i),a=0;a<i;a++)n[a]=arguments[a];return(e=(0,d.A)(this,t,[].concat(n))).disabled=!1,e.required=!0,e}return(0,c.A)(t,e),(0,l.A)(t,[{key:"render",value:function(){var e,t;return(0,h.qy)(q||(q=E`<ha-tts-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .language=${0}
      .disabled=${0}
      .required=${0}
    ></ha-tts-picker>`),this.hass,this.value,this.label,this.helper,(null===(e=this.selector.tts)||void 0===e?void 0:e.language)||(null===(t=this.context)||void 0===t?void 0:t.language),this.disabled,this.required)}}])}(h.WF);Z.styles=(0,h.AH)(L||(L=E`
    ha-tts-picker {
      width: 100%;
    }
  `)),(0,u.__decorate)([(0,v.MZ)({attribute:!1})],Z.prototype,"hass",void 0),(0,u.__decorate)([(0,v.MZ)({attribute:!1})],Z.prototype,"selector",void 0),(0,u.__decorate)([(0,v.MZ)()],Z.prototype,"value",void 0),(0,u.__decorate)([(0,v.MZ)()],Z.prototype,"label",void 0),(0,u.__decorate)([(0,v.MZ)()],Z.prototype,"helper",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean})],Z.prototype,"disabled",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean})],Z.prototype,"required",void 0),(0,u.__decorate)([(0,v.MZ)({attribute:!1})],Z.prototype,"context",void 0),Z=(0,u.__decorate)([(0,v.EM)("ha-selector-tts")],Z)},62146:function(e,t,i){i.d(t,{EF:function(){return r},S_:function(){return n},Xv:function(){return o},ni:function(){return s},u1:function(){return l},z3:function(){return d}});var n=(e,t)=>e.callApi("POST","tts_get_url",t),a="media-source://tts/",s=e=>e.startsWith(a),r=e=>e.substring(19),o=(e,t,i)=>e.callWS({type:"tts/engine/list",language:t,country:i}),l=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),d=(e,t,i)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:i})}}]);
//# sourceMappingURL=5487.6f70d3d5707e2cc3.js.map