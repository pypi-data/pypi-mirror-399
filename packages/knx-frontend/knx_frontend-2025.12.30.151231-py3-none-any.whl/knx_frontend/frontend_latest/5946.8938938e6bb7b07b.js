/*! For license information please see 5946.8938938e6bb7b07b.js.LICENSE.txt */
export const __webpack_id__="5946";export const __webpack_ids__=["5946"];export const __webpack_modules__={92209:function(e,t,o){o.d(t,{x:()=>i});const i=(e,t)=>e&&e.config.components.includes(t)},53045:function(e,t,o){o.d(t,{v:()=>i});const i=(e,t,o,i)=>{const[a,r,s]=e.split(".",3);return Number(a)>t||Number(a)===t&&(void 0===i?Number(r)>=o:Number(r)>o)||void 0!==i&&Number(a)===t&&Number(r)===o&&Number(s)>=i}},34887:function(e,t,o){var i=o(62826),a=o(27680),r=(o(99949),o(59924)),s=o(96196),d=o(77845),n=o(32288),l=o(92542),c=(o(94343),o(78740));class h extends c.h{willUpdate(e){super.willUpdate(e),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}constructor(...e){super(...e),this.forceBlankValue=!1}}(0,i.__decorate)([(0,d.MZ)({type:Boolean,attribute:"force-blank-value"})],h.prototype,"forceBlankValue",void 0),h=(0,i.__decorate)([(0,d.EM)("ha-combo-box-textfield")],h);o(60733),o(56768);(0,r.SF)("vaadin-combo-box-item",s.AH`
    :host {
      padding: 0 !important;
    }
    :host([focused]:not([disabled])) {
      background-color: rgba(var(--rgb-primary-text-color, 0, 0, 0), 0.12);
    }
    :host([selected]:not([disabled])) {
      background-color: transparent;
      color: var(--mdc-theme-primary);
      --mdc-ripple-color: var(--mdc-theme-primary);
      --mdc-theme-text-primary-on-background: var(--mdc-theme-primary);
    }
    :host([selected]:not([disabled])):before {
      background-color: var(--mdc-theme-primary);
      opacity: 0.12;
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    :host([selected][focused]:not([disabled])):before {
      opacity: 0.24;
    }
    :host(:hover:not([disabled])) {
      background-color: transparent;
    }
    [part="content"] {
      width: 100%;
    }
    [part="checkmark"] {
      display: none;
    }
  `);class p extends s.WF{async open(){await this.updateComplete,this._comboBox?.open()}async focus(){await this.updateComplete,await(this._inputElement?.updateComplete),this._inputElement?.focus()}disconnectedCallback(){super.disconnectedCallback(),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}get selectedItem(){return this._comboBox.selectedItem}setInputValue(e){this._comboBox.value=e}setTextFieldValue(e){this._inputElement.value=e}render(){return s.qy`
      <!-- @ts-ignore Tag definition is not included in theme folder -->
      <vaadin-combo-box-light
        .itemValuePath=${this.itemValuePath}
        .itemIdPath=${this.itemIdPath}
        .itemLabelPath=${this.itemLabelPath}
        .items=${this.items}
        .value=${this.value||""}
        .filteredItems=${this.filteredItems}
        .dataProvider=${this.dataProvider}
        .allowCustomValue=${this.allowCustomValue}
        .disabled=${this.disabled}
        .required=${this.required}
        ${(0,a.d)(this.renderer||this._defaultRowRenderer)}
        @opened-changed=${this._openedChanged}
        @filter-changed=${this._filterChanged}
        @value-changed=${this._valueChanged}
        attr-for-value="value"
      >
        <ha-combo-box-textfield
          label=${(0,n.J)(this.label)}
          placeholder=${(0,n.J)(this.placeholder)}
          ?disabled=${this.disabled}
          ?required=${this.required}
          validationMessage=${(0,n.J)(this.validationMessage)}
          .errorMessage=${this.errorMessage}
          class="input"
          autocapitalize="none"
          autocomplete="off"
          .autocorrect=${!1}
          input-spellcheck="false"
          .suffix=${s.qy`<div
            style="width: 28px;"
            role="none presentation"
          ></div>`}
          .icon=${this.icon}
          .invalid=${this.invalid}
          .forceBlankValue=${this._forceBlankValue}
        >
          <slot name="icon" slot="leadingIcon"></slot>
        </ha-combo-box-textfield>
        ${this.value&&!this.hideClearIcon?s.qy`<ha-svg-icon
              role="button"
              tabindex="-1"
              aria-label=${(0,n.J)(this.hass?.localize("ui.common.clear"))}
              class=${"clear-button "+(this.label?"":"no-label")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ?disabled=${this.disabled}
              @click=${this._clearValue}
            ></ha-svg-icon>`:""}
        <ha-svg-icon
          role="button"
          tabindex="-1"
          aria-label=${(0,n.J)(this.label)}
          aria-expanded=${this.opened?"true":"false"}
          class=${"toggle-button "+(this.label?"":"no-label")}
          .path=${this.opened?"M7,15L12,10L17,15H7Z":"M7,10L12,15L17,10H7Z"}
          ?disabled=${this.disabled}
          @click=${this._toggleOpen}
        ></ha-svg-icon>
      </vaadin-combo-box-light>
      ${this._renderHelper()}
    `}_renderHelper(){return this.helper?s.qy`<ha-input-helper-text .disabled=${this.disabled}
          >${this.helper}</ha-input-helper-text
        >`:""}_clearValue(e){e.stopPropagation(),(0,l.r)(this,"value-changed",{value:void 0})}_toggleOpen(e){this.opened?(this._comboBox?.close(),e.stopPropagation()):this._comboBox?.inputElement.focus()}_openedChanged(e){e.stopPropagation();const t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,l.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){const e=document.querySelector("vaadin-combo-box-overlay");e&&this._removeInert(e),this._observeBody()}else this._bodyMutationObserver?.disconnect(),this._bodyMutationObserver=void 0}_observeBody(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}_removeInert(e){if(e.inert)return e.inert=!1,this._overlayMutationObserver?.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){const t=e.target;t.inert&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0,t.inert=!1)}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}_filterChanged(e){e.stopPropagation(),(0,l.r)(this,"filter-changed",{value:e.detail.value})}_valueChanged(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),!this.opened)return;const t=e.detail.value;t!==this.value&&(0,l.r)(this,"value-changed",{value:t||void 0})}constructor(...e){super(...e),this.invalid=!1,this.icon=!1,this.allowCustomValue=!1,this.itemValuePath="value",this.itemLabelPath="label",this.disabled=!1,this.required=!1,this.opened=!1,this.hideClearIcon=!1,this.clearInitialValue=!1,this._forceBlankValue=!1,this._defaultRowRenderer=e=>s.qy`
    <ha-combo-box-item type="button">
      ${this.itemLabelPath?e[this.itemLabelPath]:e}
    </ha-combo-box-item>
  `}}p.styles=s.AH`
    :host {
      display: block;
      width: 100%;
    }
    vaadin-combo-box-light {
      position: relative;
    }
    ha-combo-box-textfield {
      width: 100%;
    }
    ha-combo-box-textfield > ha-icon-button {
      --mdc-icon-button-size: 24px;
      padding: 2px;
      color: var(--secondary-text-color);
    }
    ha-svg-icon {
      color: var(--input-dropdown-icon-color);
      position: absolute;
      cursor: pointer;
    }
    .toggle-button {
      right: 12px;
      top: -10px;
      inset-inline-start: initial;
      inset-inline-end: 12px;
      direction: var(--direction);
    }
    :host([opened]) .toggle-button {
      color: var(--primary-color);
    }
    .toggle-button[disabled],
    .clear-button[disabled] {
      color: var(--disabled-text-color);
      pointer-events: none;
    }
    .toggle-button.no-label {
      top: -3px;
    }
    .clear-button {
      --mdc-icon-size: 20px;
      top: -7px;
      right: 36px;
      inset-inline-start: initial;
      inset-inline-end: 36px;
      direction: var(--direction);
    }
    .clear-button.no-label {
      top: 0;
    }
    ha-input-helper-text {
      margin-top: 4px;
    }
  `,(0,i.__decorate)([(0,d.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,d.MZ)()],p.prototype,"label",void 0),(0,i.__decorate)([(0,d.MZ)()],p.prototype,"value",void 0),(0,i.__decorate)([(0,d.MZ)()],p.prototype,"placeholder",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:!1})],p.prototype,"validationMessage",void 0),(0,i.__decorate)([(0,d.MZ)()],p.prototype,"helper",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:"error-message"})],p.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean})],p.prototype,"invalid",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean})],p.prototype,"icon",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:!1})],p.prototype,"items",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:!1})],p.prototype,"filteredItems",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:!1})],p.prototype,"dataProvider",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:"allow-custom-value",type:Boolean})],p.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:"item-value-path"})],p.prototype,"itemValuePath",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:"item-label-path"})],p.prototype,"itemLabelPath",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:"item-id-path"})],p.prototype,"itemIdPath",void 0),(0,i.__decorate)([(0,d.MZ)({attribute:!1})],p.prototype,"renderer",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean,reflect:!0})],p.prototype,"opened",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean,attribute:"hide-clear-icon"})],p.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,d.MZ)({type:Boolean,attribute:"clear-initial-value"})],p.prototype,"clearInitialValue",void 0),(0,i.__decorate)([(0,d.P)("vaadin-combo-box-light",!0)],p.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,d.P)("ha-combo-box-textfield",!0)],p.prototype,"_inputElement",void 0),(0,i.__decorate)([(0,d.wk)({type:Boolean})],p.prototype,"_forceBlankValue",void 0),p=(0,i.__decorate)([(0,d.EM)("ha-combo-box")],p)},41944:function(e,t,o){o.r(t),o.d(t,{HaAddonSelector:()=>p});var i=o(62826),a=o(96196),r=o(77845),s=o(92209),d=o(92542),n=o(25749),l=o(34402);o(17963),o(34887),o(94343);const c=e=>a.qy`
  <ha-combo-box-item type="button">
    <span slot="headline">${e.name}</span>
    <span slot="supporting-text">${e.slug}</span>
    ${e.icon?a.qy`
          <img
            alt=""
            slot="start"
            .src="/api/hassio/addons/${e.slug}/icon"
          />
        `:a.s6}
  </ha-combo-box-item>
`;class h extends a.WF{open(){this._comboBox?.open()}focus(){this._comboBox?.focus()}firstUpdated(){this._getAddons()}render(){return this._error?a.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:this._addons?a.qy`
      <ha-combo-box
        .hass=${this.hass}
        .label=${void 0===this.label&&this.hass?this.hass.localize("ui.components.addon-picker.addon"):this.label}
        .value=${this._value}
        .required=${this.required}
        .disabled=${this.disabled}
        .helper=${this.helper}
        .renderer=${c}
        .items=${this._addons}
        item-value-path="slug"
        item-id-path="slug"
        item-label-path="name"
        @value-changed=${this._addonChanged}
      ></ha-combo-box>
    `:a.s6}async _getAddons(){try{if((0,s.x)(this.hass,"hassio")){const e=await(0,l.b3)(this.hass);this._addons=e.addons.filter((e=>e.version)).sort(((e,t)=>(0,n.xL)(e.name,t.name,this.hass.locale.language)))}else this._error=this.hass.localize("ui.components.addon-picker.error.no_supervisor")}catch(e){this._error=this.hass.localize("ui.components.addon-picker.error.fetch_addons")}}get _value(){return this.value||""}_addonChanged(e){e.stopPropagation();const t=e.detail.value;t!==this._value&&this._setValue(t)}_setValue(e){this.value=e,setTimeout((()=>{(0,d.r)(this,"value-changed",{value:e}),(0,d.r)(this,"change")}),0)}constructor(...e){super(...e),this.value="",this.disabled=!1,this.required=!1}}(0,i.__decorate)([(0,r.MZ)()],h.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],h.prototype,"helper",void 0),(0,i.__decorate)([(0,r.wk)()],h.prototype,"_addons",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box")],h.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,r.wk)()],h.prototype,"_error",void 0),h=(0,i.__decorate)([(0,r.EM)("ha-addon-picker")],h);class p extends a.WF{render(){return a.qy`<ha-addon-picker
      .hass=${this.hass}
      .value=${this.value}
      .label=${this.label}
      .helper=${this.helper}
      .disabled=${this.disabled}
      .required=${this.required}
      allow-custom-entity
    ></ha-addon-picker>`}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}p.styles=a.AH`
    ha-addon-picker {
      width: 100%;
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],p.prototype,"selector",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"required",void 0),p=(0,i.__decorate)([(0,r.EM)("ha-selector-addon")],p)},34402:function(e,t,o){o.d(t,{xG:()=>d,b3:()=>r,eK:()=>s});var i=o(53045),a=o(95260);const r=async e=>(0,i.v)(e.config.version,2021,2,4)?e.callWS({type:"supervisor/api",endpoint:"/addons",method:"get"}):(0,a.PS)(await e.callApi("GET","hassio/addons")),s=async(e,t)=>(0,i.v)(e.config.version,2021,2,4)?e.callWS({type:"supervisor/api",endpoint:`/addons/${t}/start`,method:"post",timeout:null}):e.callApi("POST",`hassio/addons/${t}/start`),d=async(e,t)=>{(0,i.v)(e.config.version,2021,2,4)?await e.callWS({type:"supervisor/api",endpoint:`/addons/${t}/install`,method:"post",timeout:null}):await e.callApi("POST",`hassio/addons/${t}/install`)}},95260:function(e,t,o){o.d(t,{PS:()=>i,VR:()=>a});const i=e=>e.data,a=e=>"object"==typeof e?"object"==typeof e.body?e.body.message||"Unknown error, see supervisor logs":e.body||e.message||"Unknown error, see supervisor logs":e;new Set([502,503,504])},37540:function(e,t,o){o.d(t,{Kq:()=>h});var i=o(63937),a=o(42017);const r=(e,t)=>{const o=e._$AN;if(void 0===o)return!1;for(const i of o)i._$AO?.(t,!1),r(i,t);return!0},s=e=>{let t,o;do{if(void 0===(t=e._$AM))break;o=t._$AN,o.delete(e),e=t}while(0===o?.size)},d=e=>{for(let t;t=e._$AM;e=t){let o=t._$AN;if(void 0===o)t._$AN=o=new Set;else if(o.has(e))break;o.add(e),c(t)}};function n(e){void 0!==this._$AN?(s(this),this._$AM=e,d(this)):this._$AM=e}function l(e,t=!1,o=0){const i=this._$AH,a=this._$AN;if(void 0!==a&&0!==a.size)if(t)if(Array.isArray(i))for(let d=o;d<i.length;d++)r(i[d],!1),s(i[d]);else null!=i&&(r(i,!1),s(i));else r(this,e)}const c=e=>{e.type==a.OA.CHILD&&(e._$AP??=l,e._$AQ??=n)};class h extends a.WL{_$AT(e,t,o){super._$AT(e,t,o),d(this),this.isConnected=e._$AU}_$AO(e,t=!0){e!==this.isConnected&&(this.isConnected=e,e?this.reconnected?.():this.disconnected?.()),t&&(r(this,e),s(this))}setValue(e){if((0,i.Rt)(this._$Ct))this._$Ct._$AI(e,this);else{const t=[...this._$Ct._$AH];t[this._$Ci]=e,this._$Ct._$AI(t,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}}};
//# sourceMappingURL=5946.8938938e6bb7b07b.js.map