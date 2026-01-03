"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2553"],{55124:function(e,t,i){i.d(t,{d:function(){return n}});var n=e=>e.stopPropagation()},31747:function(e,t,i){i.a(e,(async function(e,n){try{i.d(t,{T:function(){return l}});var s=i(22),a=i(22786),r=e([s]);s=(r.then?(await r)():r)[0];var l=(e,t)=>{try{var i,n;return null!==(i=null===(n=o(t))||void 0===n?void 0:n.of(e))&&void 0!==i?i:e}catch(s){return e}},o=(0,a.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));n()}catch(c){n(c)}}))},56528:function(e,t,i){i.a(e,(async function(e,t){try{var n=i(44734),s=i(56038),a=i(69683),r=i(6454),l=i(25460),o=(i(28706),i(50113),i(62062),i(18111),i(20116),i(61701),i(26099),i(62826)),c=i(96196),d=i(77845),u=i(92542),p=i(55124),h=i(31747),v=i(45369),_=(i(56565),i(69869),e([h]));h=(_.then?(await _)():_)[0];var f,b,g,y,m=e=>e,w="preferred",O="last_used",j=function(e){function t(){var e;(0,n.A)(this,t);for(var i=arguments.length,s=new Array(i),r=0;r<i;r++)s[r]=arguments[r];return(e=(0,a.A)(this,t,[].concat(s))).disabled=!1,e.required=!1,e.includeLastUsed=!1,e._preferredPipeline=null,e}return(0,r.A)(t,e),(0,s.A)(t,[{key:"_default",get:function(){return this.includeLastUsed?O:w}},{key:"render",value:function(){var e,t;if(!this._pipelines)return c.s6;var i=null!==(e=this.value)&&void 0!==e?e:this._default;return(0,c.qy)(f||(f=m`
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
        <ha-list-item .value=${0}>
          ${0}
        </ha-list-item>
        ${0}
      </ha-select>
    `),this.label||this.hass.localize("ui.components.pipeline-picker.pipeline"),i,this.required,this.disabled,this._changed,p.d,this.includeLastUsed?(0,c.qy)(b||(b=m`
              <ha-list-item .value=${0}>
                ${0}
              </ha-list-item>
            `),O,this.hass.localize("ui.components.pipeline-picker.last_used")):null,w,this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:null===(t=this._pipelines.find((e=>e.id===this._preferredPipeline)))||void 0===t?void 0:t.name}),this._pipelines.map((e=>(0,c.qy)(g||(g=m`<ha-list-item .value=${0}>
              ${0}
              (${0})
            </ha-list-item>`),e.id,e.name,(0,h.T)(e.language,this.hass.locale)))))}},{key:"firstUpdated",value:function(e){(0,l.A)(t,"firstUpdated",this,3)([e]),(0,v.nx)(this.hass).then((e=>{this._pipelines=e.pipelines,this._preferredPipeline=e.preferred_pipeline}))}},{key:"_changed",value:function(e){var t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===this._default||(this.value=t.value===this._default?void 0:t.value,(0,u.r)(this,"value-changed",{value:this.value}))}}])}(c.WF);j.styles=(0,c.AH)(y||(y=m`
    ha-select {
      width: 100%;
    }
  `)),(0,o.__decorate)([(0,d.MZ)()],j.prototype,"value",void 0),(0,o.__decorate)([(0,d.MZ)()],j.prototype,"label",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],j.prototype,"hass",void 0),(0,o.__decorate)([(0,d.MZ)({type:Boolean,reflect:!0})],j.prototype,"disabled",void 0),(0,o.__decorate)([(0,d.MZ)({type:Boolean})],j.prototype,"required",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],j.prototype,"includeLastUsed",void 0),(0,o.__decorate)([(0,d.wk)()],j.prototype,"_pipelines",void 0),(0,o.__decorate)([(0,d.wk)()],j.prototype,"_preferredPipeline",void 0),j=(0,o.__decorate)([(0,d.EM)("ha-assist-pipeline-picker")],j),t()}catch(A){t(A)}}))},75261:function(e,t,i){var n=i(56038),s=i(44734),a=i(69683),r=i(6454),l=i(62826),o=i(70402),c=i(11081),d=i(77845),u=function(e){function t(){return(0,s.A)(this,t),(0,a.A)(this,t,arguments)}return(0,r.A)(t,e),(0,n.A)(t)}(o.iY);u.styles=c.R,u=(0,l.__decorate)([(0,d.EM)("ha-list")],u)},1554:function(e,t,i){var n,s=i(44734),a=i(56038),r=i(69683),l=i(6454),o=i(62826),c=i(43976),d=i(703),u=i(96196),p=i(77845),h=i(94333),v=(i(75261),e=>e),_=function(e){function t(){return(0,s.A)(this,t),(0,r.A)(this,t,arguments)}return(0,l.A)(t,e),(0,a.A)(t,[{key:"listElement",get:function(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}},{key:"renderList",value:function(){var e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return(0,u.qy)(n||(n=v`<ha-list
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
    </ha-list>`),this.innerAriaLabel,this.innerRole,this.multi,(0,h.H)(t),e,this.wrapFocus,this.activatable,this.onAction)}}])}(c.ZR);_.styles=d.R,_=(0,o.__decorate)([(0,p.EM)("ha-menu")],_)},69869:function(e,t,i){var n,s,a,r,l,o=i(61397),c=i(50264),d=i(44734),u=i(56038),p=i(69683),h=i(6454),v=i(25460),_=(i(28706),i(62826)),f=i(14540),b=i(63125),g=i(96196),y=i(77845),m=i(94333),w=i(40404),O=i(99034),j=(i(60733),i(1554),e=>e),A=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,n=new Array(i),s=0;s<i;s++)n[s]=arguments[s];return(e=(0,p.A)(this,t,[].concat(n))).icon=!1,e.clearable=!1,e.inlineArrow=!1,e._translationsUpdated=(0,w.s)((0,c.A)((0,o.A)().m((function t(){return(0,o.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,O.E)();case 1:e.layoutOptions();case 2:return t.a(2)}}),t)}))),500),e}return(0,h.A)(t,e),(0,u.A)(t,[{key:"render",value:function(){return(0,g.qy)(n||(n=j`
      ${0}
      ${0}
    `),(0,v.A)(t,"render",this,3)([]),this.clearable&&!this.required&&!this.disabled&&this.value?(0,g.qy)(s||(s=j`<ha-icon-button
            label="clear"
            @click=${0}
            .path=${0}
          ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):g.s6)}},{key:"renderMenu",value:function(){var e=this.getMenuClasses();return(0,g.qy)(a||(a=j`<ha-menu
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
    </ha-menu>`),(0,m.H)(e),!this.fixedMenuPosition&&!this.naturalMenuWidth,this.menuOpen,this.anchorElement,this.fixedMenuPosition,this.onSelected,this.onOpened,this.onClosed,this.onItemsUpdated,this.handleTypeahead,this.renderMenuContent())}},{key:"renderLeadingIcon",value:function(){return this.icon?(0,g.qy)(r||(r=j`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`)):g.s6}},{key:"connectedCallback",value:function(){(0,v.A)(t,"connectedCallback",this,3)([]),window.addEventListener("translations-updated",this._translationsUpdated)}},{key:"firstUpdated",value:(i=(0,c.A)((0,o.A)().m((function e(){var i;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:(0,v.A)(t,"firstUpdated",this,3)([]),this.inlineArrow&&(null===(i=this.shadowRoot)||void 0===i||null===(i=i.querySelector(".mdc-select__selected-text-container"))||void 0===i||i.classList.add("inline-arrow"));case 1:return e.a(2)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"updated",value:function(e){if((0,v.A)(t,"updated",this,3)([e]),e.has("inlineArrow")){var i,n=null===(i=this.shadowRoot)||void 0===i?void 0:i.querySelector(".mdc-select__selected-text-container");this.inlineArrow?null==n||n.classList.add("inline-arrow"):null==n||n.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}},{key:"disconnectedCallback",value:function(){(0,v.A)(t,"disconnectedCallback",this,3)([]),window.removeEventListener("translations-updated",this._translationsUpdated)}},{key:"_clearValue",value:function(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}}]);var i}(f.o);A.styles=[b.R,(0,g.AH)(l||(l=j`
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
    `))],(0,_.__decorate)([(0,y.MZ)({type:Boolean})],A.prototype,"icon",void 0),(0,_.__decorate)([(0,y.MZ)({type:Boolean,reflect:!0})],A.prototype,"clearable",void 0),(0,_.__decorate)([(0,y.MZ)({attribute:"inline-arrow",type:Boolean})],A.prototype,"inlineArrow",void 0),(0,_.__decorate)([(0,y.MZ)()],A.prototype,"options",void 0),A=(0,_.__decorate)([(0,y.EM)("ha-select")],A)},45369:function(e,t,i){i.d(t,{QC:function(){return s},ds:function(){return d},mp:function(){return l},nx:function(){return r},u6:function(){return o},vU:function(){return a},zn:function(){return c}});var n=i(94741),s=(i(28706),(e,t,i)=>"run-start"===t.type?e={init_options:i,stage:"ready",run:t.data,events:[t],started:new Date(t.timestamp)}:e?((e="wake_word-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"wake_word",wake_word:Object.assign(Object.assign({},t.data),{},{done:!1})}):"wake_word-end"===t.type?Object.assign(Object.assign({},e),{},{wake_word:Object.assign(Object.assign(Object.assign({},e.wake_word),t.data),{},{done:!0})}):"stt-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"stt",stt:Object.assign(Object.assign({},t.data),{},{done:!1})}):"stt-end"===t.type?Object.assign(Object.assign({},e),{},{stt:Object.assign(Object.assign(Object.assign({},e.stt),t.data),{},{done:!0})}):"intent-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"intent",intent:Object.assign(Object.assign({},t.data),{},{done:!1})}):"intent-end"===t.type?Object.assign(Object.assign({},e),{},{intent:Object.assign(Object.assign(Object.assign({},e.intent),t.data),{},{done:!0})}):"tts-start"===t.type?Object.assign(Object.assign({},e),{},{stage:"tts",tts:Object.assign(Object.assign({},t.data),{},{done:!1})}):"tts-end"===t.type?Object.assign(Object.assign({},e),{},{tts:Object.assign(Object.assign(Object.assign({},e.tts),t.data),{},{done:!0})}):"run-end"===t.type?Object.assign(Object.assign({},e),{},{finished:new Date(t.timestamp),stage:"done"}):"error"===t.type?Object.assign(Object.assign({},e),{},{finished:new Date(t.timestamp),stage:"error",error:t.data}):Object.assign({},e)).events=[].concat((0,n.A)(e.events),[t]),e):void console.warn("Received unexpected event before receiving session",t)),a=(e,t,i)=>e.connection.subscribeMessage(t,Object.assign(Object.assign({},i),{},{type:"assist_pipeline/run"})),r=e=>e.callWS({type:"assist_pipeline/pipeline/list"}),l=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:t}),o=(e,t)=>e.callWS(Object.assign({type:"assist_pipeline/pipeline/create"},t)),c=(e,t,i)=>e.callWS(Object.assign({type:"assist_pipeline/pipeline/update",pipeline_id:t},i)),d=e=>e.callWS({type:"assist_pipeline/language/list"})}}]);
//# sourceMappingURL=2553.3e529c4274f97889.js.map