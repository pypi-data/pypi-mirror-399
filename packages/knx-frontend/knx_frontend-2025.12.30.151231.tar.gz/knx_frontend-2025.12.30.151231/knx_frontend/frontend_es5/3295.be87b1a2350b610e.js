"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3295"],{55124:function(e,t,n){n.d(t,{d:function(){return i}});var i=e=>e.stopPropagation()},75261:function(e,t,n){var i=n(56038),a=n(44734),s=n(69683),r=n(6454),o=n(62826),l=n(70402),c=n(11081),d=n(77845),u=function(e){function t(){return(0,a.A)(this,t),(0,s.A)(this,t,arguments)}return(0,r.A)(t,e),(0,i.A)(t)}(l.iY);u.styles=c.R,u=(0,o.__decorate)([(0,d.EM)("ha-list")],u)},1554:function(e,t,n){var i,a=n(44734),s=n(56038),r=n(69683),o=n(6454),l=n(62826),c=n(43976),d=n(703),u=n(96196),h=n(77845),p=n(94333),v=(n(75261),e=>e),_=function(e){function t(){return(0,a.A)(this,t),(0,r.A)(this,t,arguments)}return(0,o.A)(t,e),(0,s.A)(t,[{key:"listElement",get:function(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}},{key:"renderList",value:function(){var e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return(0,u.qy)(i||(i=v`<ha-list
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
    </ha-list>`),this.innerAriaLabel,this.innerRole,this.multi,(0,p.H)(t),e,this.wrapFocus,this.activatable,this.onAction)}}])}(c.ZR);_.styles=d.R,_=(0,l.__decorate)([(0,h.EM)("ha-menu")],_)},69869:function(e,t,n){var i,a,s,r,o,l=n(61397),c=n(50264),d=n(44734),u=n(56038),h=n(69683),p=n(6454),v=n(25460),_=(n(28706),n(62826)),g=n(14540),f=n(63125),y=n(96196),b=n(77845),m=n(94333),A=n(40404),w=n(99034),k=(n(60733),n(1554),e=>e),C=function(e){function t(){var e;(0,d.A)(this,t);for(var n=arguments.length,i=new Array(n),a=0;a<n;a++)i[a]=arguments[a];return(e=(0,h.A)(this,t,[].concat(i))).icon=!1,e.clearable=!1,e.inlineArrow=!1,e._translationsUpdated=(0,A.s)((0,c.A)((0,l.A)().m((function t(){return(0,l.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,w.E)();case 1:e.layoutOptions();case 2:return t.a(2)}}),t)}))),500),e}return(0,p.A)(t,e),(0,u.A)(t,[{key:"render",value:function(){return(0,y.qy)(i||(i=k`
      ${0}
      ${0}
    `),(0,v.A)(t,"render",this,3)([]),this.clearable&&!this.required&&!this.disabled&&this.value?(0,y.qy)(a||(a=k`<ha-icon-button
            label="clear"
            @click=${0}
            .path=${0}
          ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):y.s6)}},{key:"renderMenu",value:function(){var e=this.getMenuClasses();return(0,y.qy)(s||(s=k`<ha-menu
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
    </ha-menu>`),(0,m.H)(e),!this.fixedMenuPosition&&!this.naturalMenuWidth,this.menuOpen,this.anchorElement,this.fixedMenuPosition,this.onSelected,this.onOpened,this.onClosed,this.onItemsUpdated,this.handleTypeahead,this.renderMenuContent())}},{key:"renderLeadingIcon",value:function(){return this.icon?(0,y.qy)(r||(r=k`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`)):y.s6}},{key:"connectedCallback",value:function(){(0,v.A)(t,"connectedCallback",this,3)([]),window.addEventListener("translations-updated",this._translationsUpdated)}},{key:"firstUpdated",value:(n=(0,c.A)((0,l.A)().m((function e(){var n;return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:(0,v.A)(t,"firstUpdated",this,3)([]),this.inlineArrow&&(null===(n=this.shadowRoot)||void 0===n||null===(n=n.querySelector(".mdc-select__selected-text-container"))||void 0===n||n.classList.add("inline-arrow"));case 1:return e.a(2)}}),e,this)}))),function(){return n.apply(this,arguments)})},{key:"updated",value:function(e){if((0,v.A)(t,"updated",this,3)([e]),e.has("inlineArrow")){var n,i=null===(n=this.shadowRoot)||void 0===n?void 0:n.querySelector(".mdc-select__selected-text-container");this.inlineArrow?null==i||i.classList.add("inline-arrow"):null==i||i.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}},{key:"disconnectedCallback",value:function(){(0,v.A)(t,"disconnectedCallback",this,3)([]),window.removeEventListener("translations-updated",this._translationsUpdated)}},{key:"_clearValue",value:function(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}}]);var n}(g.o);C.styles=[f.R,(0,y.AH)(o||(o=k`
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
    `))],(0,_.__decorate)([(0,b.MZ)({type:Boolean})],C.prototype,"icon",void 0),(0,_.__decorate)([(0,b.MZ)({type:Boolean,reflect:!0})],C.prototype,"clearable",void 0),(0,_.__decorate)([(0,b.MZ)({attribute:"inline-arrow",type:Boolean})],C.prototype,"inlineArrow",void 0),(0,_.__decorate)([(0,b.MZ)()],C.prototype,"options",void 0),C=(0,_.__decorate)([(0,b.EM)("ha-select")],C)},73796:function(e,t,n){n.r(t),n.d(t,{HaConversationAgentSelector:function(){return F}});var i,a,s,r,o,l=n(44734),c=n(56038),d=n(69683),u=n(6454),h=(n(28706),n(62826)),p=n(96196),v=n(77845),_=n(61397),g=n(50264),f=n(31432),y=n(25460),b=(n(50113),n(74423),n(62062),n(18111),n(20116),n(61701),n(26099),n(92542)),m=n(55124),A=n(40404),w=n(3950),k=n(98320),C=n(84125),$=n(35804),E=(n(56565),n(69869),n(22800)),L=n(53264),M=e=>e,x="__NONE_OPTION__",q=function(e){function t(){var e;(0,l.A)(this,t);for(var n=arguments.length,i=new Array(n),a=0;a<n;a++)i[a]=arguments[a];return(e=(0,d.A)(this,t,[].concat(i))).disabled=!1,e.required=!1,e._debouncedUpdateAgents=(0,A.s)((()=>e._updateAgents()),500),e}return(0,u.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){var e,t;if(!this._agents)return p.s6;var n=this.value;if(!n&&this.required){var o,l=(0,f.A)(this._agents);try{for(l.s();!(o=l.n()).done;){var c=o.value;if("conversation.home_assistant"===c.id&&c.supported_languages.includes(this.language)){n=c.id;break}}}catch(v){l.e(v)}finally{l.f()}if(!n){var d,u=(0,f.A)(this._agents);try{for(u.s();!(d=u.n()).done;){var h=d.value;if("*"===h.supported_languages&&h.supported_languages.includes(this.language)){n=h.id;break}}}catch(v){u.e(v)}finally{u.f()}}}return n||(n=x),(0,p.qy)(i||(i=M`
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
        ${0}</ha-select
      >${0}
    `),this.label||this.hass.localize("ui.components.coversation-agent-picker.conversation_agent"),n,this.required,this.disabled,this._changed,m.d,this.required?p.s6:(0,p.qy)(a||(a=M`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),x,this.hass.localize("ui.components.coversation-agent-picker.none")),this._agents.map((e=>(0,p.qy)(s||(s=M`<ha-list-item
              .value=${0}
              .disabled=${0}
            >
              ${0}
            </ha-list-item>`),e.id,"*"!==e.supported_languages&&0===e.supported_languages.length,e.name))),this._subConfigEntry&&null!==(e=this._configEntry)&&void 0!==e&&null!==(e=e.supported_subentry_types[this._subConfigEntry.subentry_type])&&void 0!==e&&e.supports_reconfigure||null!==(t=this._configEntry)&&void 0!==t&&t.supports_options?(0,p.qy)(r||(r=M`<ha-icon-button
            .path=${0}
            @click=${0}
          ></ha-icon-button>`),"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z",this._openOptionsFlow):"")}},{key:"willUpdate",value:function(e){(0,y.A)(t,"willUpdate",this,3)([e]),this.hasUpdated?e.has("language")&&this._debouncedUpdateAgents():this._updateAgents(),e.has("value")&&this._maybeFetchConfigEntry()}},{key:"_maybeFetchConfigEntry",value:(h=(0,g.A)((0,_.A)().m((function e(){var t;return(0,_.A)().w((function(e){for(;;)switch(e.p=e.n){case 0:if(this.value&&this.value in this.hass.entities){e.n=1;break}return this._configEntry=void 0,e.a(2);case 1:return e.p=1,e.n=2,(0,E.v)(this.hass,this.value);case 2:if((t=e.v).config_entry_id){e.n=3;break}return this._configEntry=void 0,e.a(2);case 3:return e.n=4,(0,w.Vx)(this.hass,t.config_entry_id);case 4:if(this._configEntry=e.v.config_entry,t.config_subentry_id){e.n=5;break}this._subConfigEntry=void 0,e.n=7;break;case 5:return e.n=6,(0,w.t0)(this.hass,t.config_entry_id);case 6:this._subConfigEntry=e.v.find((e=>e.subentry_id===t.config_subentry_id));case 7:e.n=9;break;case 8:e.p=8,e.v,this._configEntry=void 0,this._subConfigEntry=void 0;case 9:return e.a(2)}}),e,this,[[1,8]])}))),function(){return h.apply(this,arguments)})},{key:"_updateAgents",value:(o=(0,g.A)((0,_.A)().m((function e(){var t,n,i;return(0,_.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,(0,k.vc)(this.hass,this.language,this.hass.config.country||void 0);case 1:if(t=e.v,n=t.agents,this._agents=n,this.value){e.n=2;break}return e.a(2);case 2:i=n.find((e=>e.id===this.value)),(0,b.r)(this,"supported-languages-changed",{value:null==i?void 0:i.supported_languages}),(!i||"*"!==i.supported_languages&&0===i.supported_languages.length)&&(this.value=void 0,(0,b.r)(this,"value-changed",{value:this.value}));case 3:return e.a(2)}}),e,this)}))),function(){return o.apply(this,arguments)})},{key:"_openOptionsFlow",value:(n=(0,g.A)((0,_.A)().m((function e(){var t,n,i,a,s;return(0,_.A)().w((function(e){for(;;)switch(e.n){case 0:if(this._configEntry){e.n=1;break}return e.a(2);case 1:if(!this._subConfigEntry||null===(t=this._configEntry.supported_subentry_types[this._subConfigEntry.subentry_type])||void 0===t||!t.supports_reconfigure){e.n=2;break}return(0,L.a)(this,this._configEntry,this._subConfigEntry.subentry_type,{startFlowHandler:this._configEntry.entry_id,subEntryId:this._subConfigEntry.subentry_id}),e.a(2);case 2:return n=$.Q,i=this,a=this._configEntry,e.n=3,(0,C.QC)(this.hass,this._configEntry.domain);case 3:s=e.v,n(i,a,{manifest:s});case 4:return e.a(2)}}),e,this)}))),function(){return n.apply(this,arguments)})},{key:"_changed",value:function(e){var t,n=e.target;!this.hass||""===n.value||n.value===this.value||void 0===this.value&&n.value===x||(this.value=n.value===x?void 0:n.value,(0,b.r)(this,"value-changed",{value:this.value}),(0,b.r)(this,"supported-languages-changed",{value:null===(t=this._agents.find((e=>e.id===this.value)))||void 0===t?void 0:t.supported_languages}))}}]);var n,o,h}(p.WF);q.styles=(0,p.AH)(o||(o=M`
    :host {
      display: flex;
      align-items: center;
    }
    ha-select {
      width: 100%;
    }
    ha-icon-button {
      color: var(--secondary-text-color);
    }
  `)),(0,h.__decorate)([(0,v.MZ)()],q.prototype,"value",void 0),(0,h.__decorate)([(0,v.MZ)()],q.prototype,"language",void 0),(0,h.__decorate)([(0,v.MZ)()],q.prototype,"label",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],q.prototype,"disabled",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean})],q.prototype,"required",void 0),(0,h.__decorate)([(0,v.wk)()],q.prototype,"_agents",void 0),(0,h.__decorate)([(0,v.wk)()],q.prototype,"_configEntry",void 0),(0,h.__decorate)([(0,v.wk)()],q.prototype,"_subConfigEntry",void 0),q=(0,h.__decorate)([(0,v.EM)("ha-conversation-agent-picker")],q);var Z,O,R=e=>e,F=function(e){function t(){var e;(0,l.A)(this,t);for(var n=arguments.length,i=new Array(n),a=0;a<n;a++)i[a]=arguments[a];return(e=(0,d.A)(this,t,[].concat(i))).disabled=!1,e.required=!0,e}return(0,u.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){var e,t;return(0,p.qy)(Z||(Z=R`<ha-conversation-agent-picker
      .hass=${0}
      .value=${0}
      .language=${0}
      .label=${0}
      .helper=${0}
      .disabled=${0}
      .required=${0}
    ></ha-conversation-agent-picker>`),this.hass,this.value,(null===(e=this.selector.conversation_agent)||void 0===e?void 0:e.language)||(null===(t=this.context)||void 0===t?void 0:t.language),this.label,this.helper,this.disabled,this.required)}}])}(p.WF);F.styles=(0,p.AH)(O||(O=R`
    ha-conversation-agent-picker {
      width: 100%;
    }
  `)),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],F.prototype,"hass",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],F.prototype,"selector",void 0),(0,h.__decorate)([(0,v.MZ)()],F.prototype,"value",void 0),(0,h.__decorate)([(0,v.MZ)()],F.prototype,"label",void 0),(0,h.__decorate)([(0,v.MZ)()],F.prototype,"helper",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean})],F.prototype,"disabled",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean})],F.prototype,"required",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],F.prototype,"context",void 0),F=(0,h.__decorate)([(0,v.EM)("ha-selector-conversation_agent")],F)},98320:function(e,t,n){n.d(t,{ZE:function(){return i},e1:function(){return s},vc:function(){return a}});var i=function(e){return e[e.CONTROL=1]="CONTROL",e}({}),a=(e,t,n)=>e.callWS({type:"conversation/agent/list",language:t,country:n}),s=(e,t,n)=>e.callWS({type:"conversation/agent/homeassistant/language_scores",language:t,country:n})},73347:function(e,t,n){n.d(t,{g:function(){return s}});n(23792),n(26099),n(3362),n(62953);var i=n(92542),a=()=>Promise.all([n.e("9807"),n.e("1779"),n.e("6009"),n.e("8506"),n.e("4533"),n.e("7770"),n.e("9745"),n.e("113"),n.e("131"),n.e("2769"),n.e("5206"),n.e("3591"),n.e("7163"),n.e("4493"),n.e("4545"),n.e("8061"),n.e("7394")]).then(n.bind(n,90313)),s=(e,t,n)=>{(0,i.r)(e,"show-dialog",{dialogTag:"dialog-data-entry-flow",dialogImport:a,dialogParams:Object.assign(Object.assign({},t),{},{flowConfig:n,dialogParentElement:e})})}}}]);
//# sourceMappingURL=3295.be87b1a2350b610e.js.map