/*! For license information please see 8327.67b265cd08a4b0d4.js.LICENSE.txt */
export const __webpack_id__="8327";export const __webpack_ids__=["8327"];export const __webpack_modules__={34887:function(e,t,o){var i=o(62826),a=o(27680),r=(o(99949),o(59924)),s=o(96196),l=o(77845),d=o(32288),n=o(92542),h=(o(94343),o(78740));class c extends h.h{willUpdate(e){super.willUpdate(e),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}constructor(...e){super(...e),this.forceBlankValue=!1}}(0,i.__decorate)([(0,l.MZ)({type:Boolean,attribute:"force-blank-value"})],c.prototype,"forceBlankValue",void 0),c=(0,i.__decorate)([(0,l.EM)("ha-combo-box-textfield")],c);o(60733),o(56768);(0,r.SF)("vaadin-combo-box-item",s.AH`
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
  `);class u extends s.WF{async open(){await this.updateComplete,this._comboBox?.open()}async focus(){await this.updateComplete,await(this._inputElement?.updateComplete),this._inputElement?.focus()}disconnectedCallback(){super.disconnectedCallback(),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}get selectedItem(){return this._comboBox.selectedItem}setInputValue(e){this._comboBox.value=e}setTextFieldValue(e){this._inputElement.value=e}render(){return s.qy`
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
          label=${(0,d.J)(this.label)}
          placeholder=${(0,d.J)(this.placeholder)}
          ?disabled=${this.disabled}
          ?required=${this.required}
          validationMessage=${(0,d.J)(this.validationMessage)}
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
              aria-label=${(0,d.J)(this.hass?.localize("ui.common.clear"))}
              class=${"clear-button "+(this.label?"":"no-label")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ?disabled=${this.disabled}
              @click=${this._clearValue}
            ></ha-svg-icon>`:""}
        <ha-svg-icon
          role="button"
          tabindex="-1"
          aria-label=${(0,d.J)(this.label)}
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
        >`:""}_clearValue(e){e.stopPropagation(),(0,n.r)(this,"value-changed",{value:void 0})}_toggleOpen(e){this.opened?(this._comboBox?.close(),e.stopPropagation()):this._comboBox?.inputElement.focus()}_openedChanged(e){e.stopPropagation();const t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,n.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){const e=document.querySelector("vaadin-combo-box-overlay");e&&this._removeInert(e),this._observeBody()}else this._bodyMutationObserver?.disconnect(),this._bodyMutationObserver=void 0}_observeBody(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}_removeInert(e){if(e.inert)return e.inert=!1,this._overlayMutationObserver?.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){const t=e.target;t.inert&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0,t.inert=!1)}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}_filterChanged(e){e.stopPropagation(),(0,n.r)(this,"filter-changed",{value:e.detail.value})}_valueChanged(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),!this.opened)return;const t=e.detail.value;t!==this.value&&(0,n.r)(this,"value-changed",{value:t||void 0})}constructor(...e){super(...e),this.invalid=!1,this.icon=!1,this.allowCustomValue=!1,this.itemValuePath="value",this.itemLabelPath="label",this.disabled=!1,this.required=!1,this.opened=!1,this.hideClearIcon=!1,this.clearInitialValue=!1,this._forceBlankValue=!1,this._defaultRowRenderer=e=>s.qy`
    <ha-combo-box-item type="button">
      ${this.itemLabelPath?e[this.itemLabelPath]:e}
    </ha-combo-box-item>
  `}}u.styles=s.AH`
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
  `,(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,i.__decorate)([(0,l.MZ)()],u.prototype,"label",void 0),(0,i.__decorate)([(0,l.MZ)()],u.prototype,"value",void 0),(0,i.__decorate)([(0,l.MZ)()],u.prototype,"placeholder",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"validationMessage",void 0),(0,i.__decorate)([(0,l.MZ)()],u.prototype,"helper",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"error-message"})],u.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"invalid",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"icon",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"items",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"filteredItems",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"dataProvider",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"allow-custom-value",type:Boolean})],u.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"item-value-path"})],u.prototype,"itemValuePath",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"item-label-path"})],u.prototype,"itemLabelPath",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:"item-id-path"})],u.prototype,"itemIdPath",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"renderer",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],u.prototype,"opened",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean,attribute:"hide-clear-icon"})],u.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean,attribute:"clear-initial-value"})],u.prototype,"clearInitialValue",void 0),(0,i.__decorate)([(0,l.P)("vaadin-combo-box-light",!0)],u.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,l.P)("ha-combo-box-textfield",!0)],u.prototype,"_inputElement",void 0),(0,i.__decorate)([(0,l.wk)({type:Boolean})],u.prototype,"_forceBlankValue",void 0),u=(0,i.__decorate)([(0,l.EM)("ha-combo-box")],u)},99903:function(e,t,o){o.r(t),o.d(t,{HaSelectorAttribute:()=>n});var i=o(62826),a=o(96196),r=o(77845),s=o(92542),l=o(55376);o(34887);class d extends a.WF{shouldUpdate(e){return!(!e.has("_opened")&&this._opened)}updated(e){if(e.has("_opened")&&this._opened||e.has("entityId")||e.has("attribute")){const e=(this.entityId?(0,l.e)(this.entityId):[]).map((e=>{const t=this.hass.states[e];if(!t)return[];return Object.keys(t.attributes).filter((e=>!this.hideAttributes?.includes(e))).map((e=>({value:e,label:this.hass.formatEntityAttributeName(t,e)})))})),t=[],o=new Set;for(const i of e)for(const e of i)o.has(e.value)||(o.add(e.value),t.push(e));this._comboBox.filteredItems=t}}render(){return this.hass?a.qy`
      <ha-combo-box
        .hass=${this.hass}
        .value=${this.value}
        .autofocus=${this.autofocus}
        .label=${this.label??this.hass.localize("ui.components.entity.entity-attribute-picker.attribute")}
        .disabled=${this.disabled||!this.entityId}
        .required=${this.required}
        .helper=${this.helper}
        .allowCustomValue=${this.allowCustomValue}
        item-id-path="value"
        item-value-path="value"
        item-label-path="label"
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
      >
      </ha-combo-box>
    `:a.s6}get _value(){return this.value||""}_openedChanged(e){this._opened=e.detail.value}_valueChanged(e){e.stopPropagation();const t=e.detail.value;t!==this._value&&this._setValue(t)}_setValue(e){this.value=e,setTimeout((()=>{(0,s.r)(this,"value-changed",{value:e}),(0,s.r)(this,"change")}),0)}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this._opened=!1}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],d.prototype,"entityId",void 0),(0,i.__decorate)([(0,r.MZ)({type:Array,attribute:"hide-attributes"})],d.prototype,"hideAttributes",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"autofocus",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean,attribute:"allow-custom-value"})],d.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],d.prototype,"helper",void 0),(0,i.__decorate)([(0,r.wk)()],d.prototype,"_opened",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box",!0)],d.prototype,"_comboBox",void 0),d=(0,i.__decorate)([(0,r.EM)("ha-entity-attribute-picker")],d);class n extends a.WF{render(){return a.qy`
      <ha-entity-attribute-picker
        .hass=${this.hass}
        .entityId=${this.selector.attribute?.entity_id||this.context?.filter_entity}
        .hideAttributes=${this.selector.attribute?.hide_attributes}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        allow-custom-value
      ></ha-entity-attribute-picker>
    `}updated(e){if(super.updated(e),!this.value||this.selector.attribute?.entity_id||!e.has("context"))return;const t=e.get("context");if(!this.context||!t||t.filter_entity===this.context.filter_entity)return;let o=!1;if(this.context.filter_entity){o=!(0,l.e)(this.context.filter_entity).some((e=>{const t=this.hass.states[e];return t&&this.value in t.attributes&&void 0!==t.attributes[this.value]}))}else o=void 0!==this.value;o&&(0,s.r)(this,"value-changed",{value:void 0})}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"selector",void 0),(0,i.__decorate)([(0,r.MZ)()],n.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],n.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],n.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"context",void 0),n=(0,i.__decorate)([(0,r.EM)("ha-selector-attribute")],n)},37540:function(e,t,o){o.d(t,{Kq:()=>c});var i=o(63937),a=o(42017);const r=(e,t)=>{const o=e._$AN;if(void 0===o)return!1;for(const i of o)i._$AO?.(t,!1),r(i,t);return!0},s=e=>{let t,o;do{if(void 0===(t=e._$AM))break;o=t._$AN,o.delete(e),e=t}while(0===o?.size)},l=e=>{for(let t;t=e._$AM;e=t){let o=t._$AN;if(void 0===o)t._$AN=o=new Set;else if(o.has(e))break;o.add(e),h(t)}};function d(e){void 0!==this._$AN?(s(this),this._$AM=e,l(this)):this._$AM=e}function n(e,t=!1,o=0){const i=this._$AH,a=this._$AN;if(void 0!==a&&0!==a.size)if(t)if(Array.isArray(i))for(let l=o;l<i.length;l++)r(i[l],!1),s(i[l]);else null!=i&&(r(i,!1),s(i));else r(this,e)}const h=e=>{e.type==a.OA.CHILD&&(e._$AP??=n,e._$AQ??=d)};class c extends a.WL{_$AT(e,t,o){super._$AT(e,t,o),l(this),this.isConnected=e._$AU}_$AO(e,t=!0){e!==this.isConnected&&(this.isConnected=e,e?this.reconnected?.():this.disconnected?.()),t&&(r(this,e),s(this))}setValue(e){if((0,i.Rt)(this._$Ct))this._$Ct._$AI(e,this);else{const t=[...this._$Ct._$AH];t[this._$Ci]=e,this._$Ct._$AI(t,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}}};
//# sourceMappingURL=8327.67b265cd08a4b0d4.js.map