export const __webpack_id__="1283";export const __webpack_ids__=["1283"];export const __webpack_modules__={55124:function(e,t,a){a.d(t,{d:()=>i});const i=e=>e.stopPropagation()},31747:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{T:()=>l});var o=a(22),s=a(22786),n=e([o]);o=(n.then?(await n)():n)[0];const l=(e,t)=>{try{return r(t)?.of(e)??e}catch{return e}},r=(0,s.A)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));i()}catch(l){i(l)}}))},51362:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{t:()=>y});var o=a(22),s=a(62826),n=a(96196),l=a(77845),r=a(22786),c=a(92542),d=a(31747),h=a(25749),p=a(13673),u=a(89473),_=a(96943),v=e([o,u,_,d]);[o,u,_,d]=v.then?(await v)():v;const g="M7,10L12,15L17,10H7Z",y=(e,t,a,i)=>{let o=[];if(t){const t=p.P.translations;o=e.map((e=>{let a=t[e]?.nativeName;if(!a)try{a=new Intl.DisplayNames(e,{type:"language",fallback:"code"}).of(e)}catch(i){a=e}return{id:e,primary:a,search_labels:[a]}}))}else i&&(o=e.map((e=>({id:e,primary:(0,d.T)(e,i),search_labels:[(0,d.T)(e,i)]}))));return!a&&i&&o.sort(((e,t)=>(0,h.SH)(e.primary,t.primary,i.language))),o};class m extends n.WF{firstUpdated(e){super.firstUpdated(e),this._computeDefaultLanguageOptions()}_computeDefaultLanguageOptions(){this._defaultLanguages=Object.keys(p.P.translations)}render(){const e=this.value??(this.required&&!this.disabled?this._getItems()[0].id:this.value);return n.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        popover-placement="bottom-end"
        .notFoundLabel=${this._notFoundLabel}
        .emptyLabel=${this.hass?.localize("ui.components.language-picker.no_languages")||"No languages available"}
        .placeholder=${this.label??(this.hass?.localize("ui.components.language-picker.language")||"Language")}
        .value=${e}
        .valueRenderer=${this._valueRenderer}
        .disabled=${this.disabled}
        .helper=${this.helper}
        .getItems=${this._getItems}
        @value-changed=${this._changed}
        hide-clear-icon
      >
        ${this.buttonStyle?n.qy`<ha-button
              slot="field"
              .disabled=${this.disabled}
              @click=${this._openPicker}
              appearance="plain"
              variant="neutral"
            >
              ${this._getLanguageName(e)}
              <ha-svg-icon slot="end" .path=${g}></ha-svg-icon>
            </ha-button>`:n.s6}
      </ha-generic-picker>
    `}_openPicker(e){e.stopPropagation(),this.genericPicker.open()}_changed(e){e.stopPropagation(),this.value=e.detail.value,(0,c.r)(this,"value-changed",{value:this.value})}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.nativeName=!1,this.buttonStyle=!1,this.noSort=!1,this.inlineArrow=!1,this._defaultLanguages=[],this._getLanguagesOptions=(0,r.A)(y),this._getItems=()=>this._getLanguagesOptions(this.languages??this._defaultLanguages,this.nativeName,this.noSort,this.hass?.locale),this._getLanguageName=e=>this._getItems().find((t=>t.id===e))?.primary,this._valueRenderer=e=>n.qy`<span slot="headline"
      >${this._getLanguageName(e)??e}</span
    > `,this._notFoundLabel=e=>{const t=n.qy`<b>‘${e}’</b>`;return this.hass?this.hass.localize("ui.components.language-picker.no_match",{term:t}):n.qy`No languages found for ${t}`}}}m.styles=n.AH`
    ha-generic-picker {
      width: 100%;
      min-width: 200px;
      display: block;
    }
  `,(0,s.__decorate)([(0,l.MZ)()],m.prototype,"value",void 0),(0,s.__decorate)([(0,l.MZ)()],m.prototype,"label",void 0),(0,s.__decorate)([(0,l.MZ)({type:Array})],m.prototype,"languages",void 0),(0,s.__decorate)([(0,l.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,s.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],m.prototype,"disabled",void 0),(0,s.__decorate)([(0,l.MZ)({type:Boolean})],m.prototype,"required",void 0),(0,s.__decorate)([(0,l.MZ)()],m.prototype,"helper",void 0),(0,s.__decorate)([(0,l.MZ)({attribute:"native-name",type:Boolean})],m.prototype,"nativeName",void 0),(0,s.__decorate)([(0,l.MZ)({type:Boolean,attribute:"button-style"})],m.prototype,"buttonStyle",void 0),(0,s.__decorate)([(0,l.MZ)({attribute:"no-sort",type:Boolean})],m.prototype,"noSort",void 0),(0,s.__decorate)([(0,l.MZ)({attribute:"inline-arrow",type:Boolean})],m.prototype,"inlineArrow",void 0),(0,s.__decorate)([(0,l.wk)()],m.prototype,"_defaultLanguages",void 0),(0,s.__decorate)([(0,l.P)("ha-generic-picker",!0)],m.prototype,"genericPicker",void 0),m=(0,s.__decorate)([(0,l.EM)("ha-language-picker")],m),i()}catch(g){i(g)}}))},75261:function(e,t,a){var i=a(62826),o=a(70402),s=a(11081),n=a(77845);class l extends o.iY{}l.styles=s.R,l=(0,i.__decorate)([(0,n.EM)("ha-list")],l)},1554:function(e,t,a){var i=a(62826),o=a(43976),s=a(703),n=a(96196),l=a(77845),r=a(94333);a(75261);class c extends o.ZR{get listElement(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}renderList(){const e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return n.qy`<ha-list
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
    </ha-list>`}}c.styles=s.R,c=(0,i.__decorate)([(0,l.EM)("ha-menu")],c)},69869:function(e,t,a){var i=a(62826),o=a(14540),s=a(63125),n=a(96196),l=a(77845),r=a(94333),c=a(40404),d=a(99034);a(60733),a(1554);class h extends o.o{render(){return n.qy`
      ${super.render()}
      ${this.clearable&&!this.required&&!this.disabled&&this.value?n.qy`<ha-icon-button
            label="clear"
            @click=${this._clearValue}
            .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
          ></ha-icon-button>`:n.s6}
    `}renderMenu(){const e=this.getMenuClasses();return n.qy`<ha-menu
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
    </ha-menu>`}renderLeadingIcon(){return this.icon?n.qy`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`:n.s6}connectedCallback(){super.connectedCallback(),window.addEventListener("translations-updated",this._translationsUpdated)}async firstUpdated(){super.firstUpdated(),this.inlineArrow&&this.shadowRoot?.querySelector(".mdc-select__selected-text-container")?.classList.add("inline-arrow")}updated(e){if(super.updated(e),e.has("inlineArrow")){const e=this.shadowRoot?.querySelector(".mdc-select__selected-text-container");this.inlineArrow?e?.classList.add("inline-arrow"):e?.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("translations-updated",this._translationsUpdated)}_clearValue(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}constructor(...e){super(...e),this.icon=!1,this.clearable=!1,this.inlineArrow=!1,this._translationsUpdated=(0,c.s)((async()=>{await(0,d.E)(),this.layoutOptions()}),500)}}h.styles=[s.R,n.AH`
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
    `],(0,i.__decorate)([(0,l.MZ)({type:Boolean})],h.prototype,"icon",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],h.prototype,"clearable",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"inline-arrow",type:Boolean})],h.prototype,"inlineArrow",void 0),(0,i.__decorate)([(0,l.MZ)()],h.prototype,"options",void 0),h=(0,i.__decorate)([(0,l.EM)("ha-select")],h)},88422:function(e,t,a){a.a(e,(async function(e,t){try{var i=a(62826),o=a(52630),s=a(96196),n=a(77845),l=e([o]);o=(l.then?(await l)():l)[0];class r extends o.A{static get styles(){return[o.A.styles,s.AH`
        :host {
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-content-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(
            --ha-tooltip-border-radius,
            var(--ha-border-radius-sm)
          );
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
        }
      `]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=150}}(0,i.__decorate)([(0,n.MZ)({attribute:"show-delay",type:Number})],r.prototype,"showDelay",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"hide-delay",type:Number})],r.prototype,"hideDelay",void 0),r=(0,i.__decorate)([(0,n.EM)("ha-tooltip")],r),t()}catch(r){t(r)}}))},10054:function(e,t,a){var i=a(62826),o=a(96196),s=a(77845),n=a(92542),l=a(55124),r=a(40404),c=a(62146);a(56565),a(69869);const d="__NONE_OPTION__";class h extends o.WF{render(){if(!this._voices)return o.s6;const e=this.value??(this.required?this._voices[0]?.voice_id:d);return o.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.tts-voice-picker.voice")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${l.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.required?o.s6:o.qy`<ha-list-item .value=${d}>
              ${this.hass.localize("ui.components.tts-voice-picker.none")}
            </ha-list-item>`}
        ${this._voices.map((e=>o.qy`<ha-list-item .value=${e.voice_id}>
              ${e.name}
            </ha-list-item>`))}
      </ha-select>
    `}willUpdate(e){super.willUpdate(e),this.hasUpdated?(e.has("language")||e.has("engineId"))&&this._debouncedUpdateVoices():this._updateVoices()}async _updateVoices(){this.engineId&&this.language?(this._voices=(await(0,c.z3)(this.hass,this.engineId,this.language)).voices,this.value&&(this._voices&&this._voices.find((e=>e.voice_id===this.value))||(this.value=void 0,(0,n.r)(this,"value-changed",{value:this.value})))):this._voices=void 0}updated(e){super.updated(e),e.has("_voices")&&this._select?.value!==this.value&&(this._select?.layoutOptions(),(0,n.r)(this,"value-changed",{value:this._select?.value}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===d||(this.value=t.value===d?void 0:t.value,(0,n.r)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._debouncedUpdateVoices=(0,r.s)((()=>this._updateVoices()),500)}}h.styles=o.AH`
    ha-select {
      width: 100%;
    }
  `,(0,i.__decorate)([(0,s.MZ)()],h.prototype,"value",void 0),(0,i.__decorate)([(0,s.MZ)()],h.prototype,"label",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"engineId",void 0),(0,i.__decorate)([(0,s.MZ)()],h.prototype,"language",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],h.prototype,"disabled",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,i.__decorate)([(0,s.wk)()],h.prototype,"_voices",void 0),(0,i.__decorate)([(0,s.P)("ha-select")],h.prototype,"_select",void 0),h=(0,i.__decorate)([(0,s.EM)("ha-tts-voice-picker")],h)},71750:function(e,t,a){a.d(t,{eN:()=>n,p7:()=>i,q3:()=>s,vO:()=>o});const i=({hass:e,...t})=>e.callApi("POST","cloud/login",t),o=(e,t,a)=>e.callApi("POST","cloud/register",{email:t,password:a}),s=(e,t)=>e.callApi("POST","cloud/resend_confirm",{email:t}),n=e=>e.callWS({type:"cloud/status"})},62146:function(e,t,a){a.d(t,{EF:()=>n,S_:()=>i,Xv:()=>l,ni:()=>s,u1:()=>r,z3:()=>c});const i=(e,t)=>e.callApi("POST","tts_get_url",t),o="media-source://tts/",s=e=>e.startsWith(o),n=e=>e.substring(19),l=(e,t,a)=>e.callWS({type:"tts/engine/list",language:t,country:a}),r=(e,t)=>e.callWS({type:"tts/engine/get",engine_id:t}),c=(e,t,a)=>e.callWS({type:"tts/engine/voices",engine_id:t,language:a})},4848:function(e,t,a){a.d(t,{P:()=>o});var i=a(92542);const o=(e,t)=>(0,i.r)(e,"hass-notification",t)}};
//# sourceMappingURL=1283.3d5e664fddac722d.js.map