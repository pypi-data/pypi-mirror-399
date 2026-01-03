"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3708"],{55124:function(e,t,i){i.d(t,{d:function(){return n}});var n=e=>e.stopPropagation()},75261:function(e,t,i){var n=i(56038),a=i(44734),o=i(69683),s=i(6454),r=i(62826),l=i(70402),c=i(11081),d=i(77845),u=function(e){function t(){return(0,a.A)(this,t),(0,o.A)(this,t,arguments)}return(0,s.A)(t,e),(0,n.A)(t)}(l.iY);u.styles=c.R,u=(0,r.__decorate)([(0,d.EM)("ha-list")],u)},1554:function(e,t,i){var n,a=i(44734),o=i(56038),s=i(69683),r=i(6454),l=i(62826),c=i(43976),d=i(703),u=i(96196),h=i(77845),v=i(94333),p=(i(75261),e=>e),_=function(e){function t(){return(0,a.A)(this,t),(0,s.A)(this,t,arguments)}return(0,r.A)(t,e),(0,o.A)(t,[{key:"listElement",get:function(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}},{key:"renderList",value:function(){var e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return(0,u.qy)(n||(n=p`<ha-list
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
    </ha-list>`),this.innerAriaLabel,this.innerRole,this.multi,(0,v.H)(t),e,this.wrapFocus,this.activatable,this.onAction)}}])}(c.ZR);_.styles=d.R,_=(0,l.__decorate)([(0,h.EM)("ha-menu")],_)},69869:function(e,t,i){var n,a,o,s,r,l=i(61397),c=i(50264),d=i(44734),u=i(56038),h=i(69683),v=i(6454),p=i(25460),_=(i(28706),i(62826)),f=i(14540),y=i(63125),g=i(96196),b=i(77845),m=i(94333),A=i(40404),$=i(99034),w=(i(60733),i(1554),e=>e),k=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,n=new Array(i),a=0;a<i;a++)n[a]=arguments[a];return(e=(0,h.A)(this,t,[].concat(n))).icon=!1,e.clearable=!1,e.inlineArrow=!1,e._translationsUpdated=(0,A.s)((0,c.A)((0,l.A)().m((function t(){return(0,l.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,$.E)();case 1:e.layoutOptions();case 2:return t.a(2)}}),t)}))),500),e}return(0,v.A)(t,e),(0,u.A)(t,[{key:"render",value:function(){return(0,g.qy)(n||(n=w`
      ${0}
      ${0}
    `),(0,p.A)(t,"render",this,3)([]),this.clearable&&!this.required&&!this.disabled&&this.value?(0,g.qy)(a||(a=w`<ha-icon-button
            label="clear"
            @click=${0}
            .path=${0}
          ></ha-icon-button>`),this._clearValue,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):g.s6)}},{key:"renderMenu",value:function(){var e=this.getMenuClasses();return(0,g.qy)(o||(o=w`<ha-menu
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
    </ha-menu>`),(0,m.H)(e),!this.fixedMenuPosition&&!this.naturalMenuWidth,this.menuOpen,this.anchorElement,this.fixedMenuPosition,this.onSelected,this.onOpened,this.onClosed,this.onItemsUpdated,this.handleTypeahead,this.renderMenuContent())}},{key:"renderLeadingIcon",value:function(){return this.icon?(0,g.qy)(s||(s=w`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`)):g.s6}},{key:"connectedCallback",value:function(){(0,p.A)(t,"connectedCallback",this,3)([]),window.addEventListener("translations-updated",this._translationsUpdated)}},{key:"firstUpdated",value:(i=(0,c.A)((0,l.A)().m((function e(){var i;return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:(0,p.A)(t,"firstUpdated",this,3)([]),this.inlineArrow&&(null===(i=this.shadowRoot)||void 0===i||null===(i=i.querySelector(".mdc-select__selected-text-container"))||void 0===i||i.classList.add("inline-arrow"));case 1:return e.a(2)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"updated",value:function(e){if((0,p.A)(t,"updated",this,3)([e]),e.has("inlineArrow")){var i,n=null===(i=this.shadowRoot)||void 0===i?void 0:i.querySelector(".mdc-select__selected-text-container");this.inlineArrow?null==n||n.classList.add("inline-arrow"):null==n||n.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}},{key:"disconnectedCallback",value:function(){(0,p.A)(t,"disconnectedCallback",this,3)([]),window.removeEventListener("translations-updated",this._translationsUpdated)}},{key:"_clearValue",value:function(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}}]);var i}(f.o);k.styles=[y.R,(0,g.AH)(r||(r=w`
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
    `))],(0,_.__decorate)([(0,b.MZ)({type:Boolean})],k.prototype,"icon",void 0),(0,_.__decorate)([(0,b.MZ)({type:Boolean,reflect:!0})],k.prototype,"clearable",void 0),(0,_.__decorate)([(0,b.MZ)({attribute:"inline-arrow",type:Boolean})],k.prototype,"inlineArrow",void 0),(0,_.__decorate)([(0,b.MZ)()],k.prototype,"options",void 0),k=(0,_.__decorate)([(0,b.EM)("ha-select")],k)},42839:function(e,t,i){i.r(t),i.d(t,{HaTTSVoiceSelector:function(){return v}});var n,a,o=i(44734),s=i(56038),r=i(69683),l=i(6454),c=(i(28706),i(62826)),d=i(96196),u=i(77845),h=(i(10054),e=>e),v=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,n=new Array(i),a=0;a<i;a++)n[a]=arguments[a];return(e=(0,r.A)(this,t,[].concat(n))).disabled=!1,e.required=!0,e}return(0,l.A)(t,e),(0,s.A)(t,[{key:"render",value:function(){var e,t,i,a;return(0,d.qy)(n||(n=h`<ha-tts-voice-picker
      .hass=${0}
      .value=${0}
      .label=${0}
      .helper=${0}
      .language=${0}
      .engineId=${0}
      .disabled=${0}
      .required=${0}
    ></ha-tts-voice-picker>`),this.hass,this.value,this.label,this.helper,(null===(e=this.selector.tts_voice)||void 0===e?void 0:e.language)||(null===(t=this.context)||void 0===t?void 0:t.language),(null===(i=this.selector.tts_voice)||void 0===i?void 0:i.engineId)||(null===(a=this.context)||void 0===a?void 0:a.engineId),this.disabled,this.required)}}])}(d.WF);v.styles=(0,d.AH)(a||(a=h`
    ha-tts-picker {
      width: 100%;
    }
  `)),(0,c.__decorate)([(0,u.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,c.__decorate)([(0,u.MZ)({attribute:!1})],v.prototype,"selector",void 0),(0,c.__decorate)([(0,u.MZ)()],v.prototype,"value",void 0),(0,c.__decorate)([(0,u.MZ)()],v.prototype,"label",void 0),(0,c.__decorate)([(0,u.MZ)()],v.prototype,"helper",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,c.__decorate)([(0,u.MZ)({attribute:!1})],v.prototype,"context",void 0),v=(0,c.__decorate)([(0,u.EM)("ha-selector-tts_voice")],v)},10054:function(e,t,i){var n,a,o,s,r=i(61397),l=i(50264),c=i(44734),d=i(56038),u=i(69683),h=i(6454),v=i(25460),p=(i(28706),i(50113),i(62062),i(18111),i(20116),i(61701),i(26099),i(62826)),_=i(96196),f=i(77845),y=i(92542),g=i(55124),b=i(40404),m=i(62146),A=(i(56565),i(69869),e=>e),$="__NONE_OPTION__",w=function(e){function t(){var e;(0,c.A)(this,t);for(var i=arguments.length,n=new Array(i),a=0;a<i;a++)n[a]=arguments[a];return(e=(0,u.A)(this,t,[].concat(n))).disabled=!1,e.required=!1,e._debouncedUpdateVoices=(0,b.s)((()=>e._updateVoices()),500),e}return(0,h.A)(t,e),(0,d.A)(t,[{key:"render",value:function(){var e,t;if(!this._voices)return _.s6;var i=null!==(e=this.value)&&void 0!==e?e:this.required?null===(t=this._voices[0])||void 0===t?void 0:t.voice_id:$;return(0,_.qy)(n||(n=A`
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
    `),this.label||this.hass.localize("ui.components.tts-voice-picker.voice"),i,this.required,this.disabled,this._changed,g.d,this.required?_.s6:(0,_.qy)(a||(a=A`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),$,this.hass.localize("ui.components.tts-voice-picker.none")),this._voices.map((e=>(0,_.qy)(o||(o=A`<ha-list-item .value=${0}>
              ${0}
            </ha-list-item>`),e.voice_id,e.name))))}},{key:"willUpdate",value:function(e){(0,v.A)(t,"willUpdate",this,3)([e]),this.hasUpdated?(e.has("language")||e.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}},{key:"_updateVoices",value:(i=(0,l.A)((0,r.A)().m((function e(){return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:if(this.engineId&&this.language){e.n=1;break}return this._voices=void 0,e.a(2);case 1:return e.n=2,(0,m.z3)(this.hass,this.engineId,this.language);case 2:if(this._voices=e.v.voices,this.value){e.n=3;break}return e.a(2);case 3:this._voices&&this._voices.find((e=>e.voice_id===this.value))||(this.value=void 0,(0,y.r)(this,"value-changed",{value:this.value}));case 4:return e.a(2)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"updated",value:function(e){var i,n,a;((0,v.A)(t,"updated",this,3)([e]),e.has("_voices")&&(null===(i=this._select)||void 0===i?void 0:i.value)!==this.value)&&(null===(n=this._select)||void 0===n||n.layoutOptions(),(0,y.r)(this,"value-changed",{value:null===(a=this._select)||void 0===a?void 0:a.value}))}},{key:"_changed",value:function(e){var t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===$||(this.value=t.value===$?void 0:t.value,(0,y.r)(this,"value-changed",{value:this.value}))}}]);var i}(_.WF);w.styles=(0,_.AH)(s||(s=A`
    ha-select {
      width: 100%;
    }
  `)),(0,p.__decorate)([(0,f.MZ)()],w.prototype,"value",void 0),(0,p.__decorate)([(0,f.MZ)()],w.prototype,"label",void 0),(0,p.__decorate)([(0,f.MZ)({attribute:!1})],w.prototype,"engineId",void 0),(0,p.__decorate)([(0,f.MZ)()],w.prototype,"language",void 0),(0,p.__decorate)([(0,f.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,p.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],w.prototype,"disabled",void 0),(0,p.__decorate)([(0,f.MZ)({type:Boolean})],w.prototype,"required",void 0),(0,p.__decorate)([(0,f.wk)()],w.prototype,"_voices",void 0),(0,p.__decorate)([(0,f.P)("ha-select")],w.prototype,"_select",void 0),w=(0,p.__decorate)([(0,f.EM)("ha-tts-voice-picker")],w)},62146:function(e,t,i){i.d(t,{EF:function(){return s},S_:function(){return n},Xv:function(){return r},ni:function(){return o},u1:function(){return l},z3:function(){return c}});var n=(e,t)=>e.callApi("POST","tts_get_url",t),a="media-source://tts/",o=e=>e.startsWith(a),s=e=>e.substring(19),r=(e,t,i)=>e.callWS({type:"tts/engine/list",language:t,country:i}),l=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),c=(e,t,i)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:i})}}]);
//# sourceMappingURL=3708.e91135caa505ecb3.js.map