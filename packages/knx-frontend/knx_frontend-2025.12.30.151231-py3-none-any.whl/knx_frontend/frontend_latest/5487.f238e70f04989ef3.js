export const __webpack_id__="5487";export const __webpack_ids__=["5487"];export const __webpack_modules__={55124:function(e,t,i){i.d(t,{d:()=>s});const s=e=>e.stopPropagation()},75261:function(e,t,i){var s=i(62826),a=i(70402),n=i(11081),o=i(77845);class l extends a.iY{}l.styles=n.R,l=(0,s.__decorate)([(0,o.EM)("ha-list")],l)},1554:function(e,t,i){var s=i(62826),a=i(43976),n=i(703),o=i(96196),l=i(77845),r=i(94333);i(75261);class d extends a.ZR{get listElement(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}renderList(){const e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return o.qy`<ha-list
      rootTabbable
      .innerAriaLabel=${this.innerAriaLabel}
      .innerRole=${this.innerRole}
      .multi=${this.multi}
      class=${(0,r.H)(t)}
      .itemRoles=${e}
      .wrapFocus=${this.wrapFocus}
      .activatable=${this.activatable}
      @action=${this.onAction}
    >
      <slot></slot>
    </ha-list>`}}d.styles=n.R,d=(0,s.__decorate)([(0,l.EM)("ha-menu")],d)},69869:function(e,t,i){var s=i(62826),a=i(14540),n=i(63125),o=i(96196),l=i(77845),r=i(94333),d=i(40404),c=i(99034);i(60733),i(1554);class h extends a.o{render(){return o.qy`
      ${super.render()}
      ${this.clearable&&!this.required&&!this.disabled&&this.value?o.qy`<ha-icon-button
            label="clear"
            @click=${this._clearValue}
            .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
          ></ha-icon-button>`:o.s6}
    `}renderMenu(){const e=this.getMenuClasses();return o.qy`<ha-menu
      innerRole="listbox"
      wrapFocus
      class=${(0,r.H)(e)}
      activatable
      .fullwidth=${!this.fixedMenuPosition&&!this.naturalMenuWidth}
      .open=${this.menuOpen}
      .anchor=${this.anchorElement}
      .fixed=${this.fixedMenuPosition}
      @selected=${this.onSelected}
      @opened=${this.onOpened}
      @closed=${this.onClosed}
      @items-updated=${this.onItemsUpdated}
      @keydown=${this.handleTypeahead}
    >
      ${this.renderMenuContent()}
    </ha-menu>`}renderLeadingIcon(){return this.icon?o.qy`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`:o.s6}connectedCallback(){super.connectedCallback(),window.addEventListener("translations-updated",this._translationsUpdated)}async firstUpdated(){super.firstUpdated(),this.inlineArrow&&this.shadowRoot?.querySelector(".mdc-select__selected-text-container")?.classList.add("inline-arrow")}updated(e){if(super.updated(e),e.has("inlineArrow")){const e=this.shadowRoot?.querySelector(".mdc-select__selected-text-container");this.inlineArrow?e?.classList.add("inline-arrow"):e?.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("translations-updated",this._translationsUpdated)}_clearValue(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}constructor(...e){super(...e),this.icon=!1,this.clearable=!1,this.inlineArrow=!1,this._translationsUpdated=(0,d.s)((async()=>{await(0,c.E)(),this.layoutOptions()}),500)}}h.styles=[n.R,o.AH`
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
    `],(0,s.__decorate)([(0,l.MZ)({type:Boolean})],h.prototype,"icon",void 0),(0,s.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],h.prototype,"clearable",void 0),(0,s.__decorate)([(0,l.MZ)({attribute:"inline-arrow",type:Boolean})],h.prototype,"inlineArrow",void 0),(0,s.__decorate)([(0,l.MZ)()],h.prototype,"options",void 0),h=(0,s.__decorate)([(0,l.EM)("ha-select")],h)},34818:function(e,t,i){i.r(t),i.d(t,{HaTTSSelector:()=>_});var s=i(62826),a=i(96196),n=i(77845),o=i(92542),l=i(55124),r=i(91889),d=i(40404),c=i(62146),h=(i(56565),i(69869),i(41144));const u="__NONE_OPTION__";class p extends a.WF{render(){if(!this._engines)return a.s6;let e=this.value;if(!e&&this.required){for(const t of Object.values(this.hass.entities))if("cloud"===t.platform&&"tts"===(0,h.m)(t.entity_id)){e=t.entity_id;break}if(!e)for(const t of this._engines)if(0!==t?.supported_languages?.length){e=t.engine_id;break}}return e||(e=u),a.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.tts-picker.tts")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${l.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.required?a.s6:a.qy`<ha-list-item .value=${u}>
              ${this.hass.localize("ui.components.tts-picker.none")}
            </ha-list-item>`}
        ${this._engines.map((t=>{if(t.deprecated&&t.engine_id!==e)return a.s6;let i;if(t.engine_id.includes(".")){const e=this.hass.states[t.engine_id];i=e?(0,r.u)(e):t.engine_id}else i=t.name||t.engine_id;return a.qy`<ha-list-item
            .value=${t.engine_id}
            .disabled=${0===t.supported_languages?.length}
          >
            ${i}
          </ha-list-item>`}))}
      </ha-select>
    `}willUpdate(e){super.willUpdate(e),this.hasUpdated?e.has("language")&&this._debouncedUpdateEngines():this._updateEngines()}async _updateEngines(){if(this._engines=(await(0,c.Xv)(this.hass,this.language,this.hass.config.country||void 0)).providers,!this.value)return;const e=this._engines.find((e=>e.engine_id===this.value));(0,o.r)(this,"supported-languages-changed",{value:e?.supported_languages}),e&&0!==e.supported_languages?.length||(this.value=void 0,(0,o.r)(this,"value-changed",{value:this.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===u||(this.value=t.value===u?void 0:t.value,(0,o.r)(this,"value-changed",{value:this.value}),(0,o.r)(this,"supported-languages-changed",{value:this._engines.find((e=>e.engine_id===this.value))?.supported_languages}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateEngines=(0,d.s)((()=>this._updateEngines()),500)}}p.styles=a.AH`
    ha-select {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,n.MZ)()],p.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)()],p.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)()],p.prototype,"language",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],p.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,s.__decorate)([(0,n.wk)()],p.prototype,"_engines",void 0),p=(0,s.__decorate)([(0,n.EM)("ha-tts-picker")],p);class _ extends a.WF{render(){return a.qy`<ha-tts-picker
      .hass=${this.hass}
      .value=${this.value}
      .label=${this.label}
      .helper=${this.helper}
      .language=${this.selector.tts?.language||this.context?.language}
      .disabled=${this.disabled}
      .required=${this.required}
    ></ha-tts-picker>`}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}_.styles=a.AH`
    ha-tts-picker {
      width: 100%;
    }
  `,(0,s.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"selector",void 0),(0,s.__decorate)([(0,n.MZ)()],_.prototype,"value",void 0),(0,s.__decorate)([(0,n.MZ)()],_.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)()],_.prototype,"helper",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],_.prototype,"context",void 0),_=(0,s.__decorate)([(0,n.EM)("ha-selector-tts")],_)},62146:function(e,t,i){i.d(t,{EF:()=>o,S_:()=>s,Xv:()=>l,ni:()=>n,u1:()=>r,z3:()=>d});const s=(e,t)=>e.callApi("POST","tts_get_url",t),a="media-source://tts/",n=e=>e.startsWith(a),o=e=>e.substring(19),l=(e,t,i)=>e.callWS({type:"tts/engine/list",language:t,country:i}),r=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),d=(e,t,i)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:i})}};
//# sourceMappingURL=5487.f238e70f04989ef3.js.map