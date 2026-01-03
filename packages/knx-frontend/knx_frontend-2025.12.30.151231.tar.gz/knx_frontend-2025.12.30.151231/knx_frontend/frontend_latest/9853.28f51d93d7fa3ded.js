/*! For license information please see 9853.28f51d93d7fa3ded.js.LICENSE.txt */
export const __webpack_id__="9853";export const __webpack_ids__=["9853"];export const __webpack_modules__={34887:function(e,t,o){var i=o(62826),a=o(27680),r=(o(99949),o(59924)),s=o(96196),n=o(77845),l=o(32288),d=o(92542),h=(o(94343),o(78740));class c extends h.h{willUpdate(e){super.willUpdate(e),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}constructor(...e){super(...e),this.forceBlankValue=!1}}(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"force-blank-value"})],c.prototype,"forceBlankValue",void 0),c=(0,i.__decorate)([(0,n.EM)("ha-combo-box-textfield")],c);o(60733),o(56768);(0,r.SF)("vaadin-combo-box-item",s.AH`
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
          label=${(0,l.J)(this.label)}
          placeholder=${(0,l.J)(this.placeholder)}
          ?disabled=${this.disabled}
          ?required=${this.required}
          validationMessage=${(0,l.J)(this.validationMessage)}
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
              aria-label=${(0,l.J)(this.hass?.localize("ui.common.clear"))}
              class=${"clear-button "+(this.label?"":"no-label")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ?disabled=${this.disabled}
              @click=${this._clearValue}
            ></ha-svg-icon>`:""}
        <ha-svg-icon
          role="button"
          tabindex="-1"
          aria-label=${(0,l.J)(this.label)}
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
        >`:""}_clearValue(e){e.stopPropagation(),(0,d.r)(this,"value-changed",{value:void 0})}_toggleOpen(e){this.opened?(this._comboBox?.close(),e.stopPropagation()):this._comboBox?.inputElement.focus()}_openedChanged(e){e.stopPropagation();const t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,d.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){const e=document.querySelector("vaadin-combo-box-overlay");e&&this._removeInert(e),this._observeBody()}else this._bodyMutationObserver?.disconnect(),this._bodyMutationObserver=void 0}_observeBody(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}_removeInert(e){if(e.inert)return e.inert=!1,this._overlayMutationObserver?.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){const t=e.target;t.inert&&(this._overlayMutationObserver?.disconnect(),this._overlayMutationObserver=void 0,t.inert=!1)}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}_filterChanged(e){e.stopPropagation(),(0,d.r)(this,"filter-changed",{value:e.detail.value})}_valueChanged(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),!this.opened)return;const t=e.detail.value;t!==this.value&&(0,d.r)(this,"value-changed",{value:t||void 0})}constructor(...e){super(...e),this.invalid=!1,this.icon=!1,this.allowCustomValue=!1,this.itemValuePath="value",this.itemLabelPath="label",this.disabled=!1,this.required=!1,this.opened=!1,this.hideClearIcon=!1,this.clearInitialValue=!1,this._forceBlankValue=!1,this._defaultRowRenderer=e=>s.qy`
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
  `,(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"label",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"value",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"placeholder",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"validationMessage",void 0),(0,i.__decorate)([(0,n.MZ)()],p.prototype,"helper",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"error-message"})],p.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"invalid",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"icon",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"items",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"filteredItems",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"dataProvider",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"allow-custom-value",type:Boolean})],p.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-value-path"})],p.prototype,"itemValuePath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-label-path"})],p.prototype,"itemLabelPath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-id-path"})],p.prototype,"itemIdPath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"renderer",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],p.prototype,"opened",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"hide-clear-icon"})],p.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"clear-initial-value"})],p.prototype,"clearInitialValue",void 0),(0,i.__decorate)([(0,n.P)("vaadin-combo-box-light",!0)],p.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,n.P)("ha-combo-box-textfield",!0)],p.prototype,"_inputElement",void 0),(0,i.__decorate)([(0,n.wk)({type:Boolean})],p.prototype,"_forceBlankValue",void 0),p=(0,i.__decorate)([(0,n.EM)("ha-combo-box")],p)},81657:function(e,t,o){var i=o(62826),a=o(96196),r=o(77845),s=o(92542);const n=(e,t)=>{const o=(e=>"lovelace"===e.url_path?"panel.states":"profile"===e.url_path?"panel.profile":`panel.${e.title}`)(t);return e.localize(o)||t.title||void 0},l=e=>{if(!e.icon)switch(e.component_name){case"profile":return"mdi:account";case"lovelace":return"mdi:view-dashboard"}return e.icon||void 0};o(34887),o(94343),o(22598);const d=[],h=e=>a.qy`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${e.icon} slot="start"></ha-icon>
    <span slot="headline">${e.title||e.path}</span>
    ${e.title?a.qy`<span slot="supporting-text">${e.path}</span>`:a.s6}
  </ha-combo-box-item>
`,c=(e,t,o)=>{return{path:`/${e}/${t.path??o}`,icon:t.icon??"mdi:view-compact",title:t.title??(t.path?(i=t.path,i.replace(/^_*(.)|_+(.)/g,((e,t,o)=>t?t.toUpperCase():" "+o.toUpperCase()))):`${o}`)};var i},p=(e,t)=>({path:`/${t.url_path}`,icon:l(t)||"mdi:view-dashboard",title:n(e,t)||""});class u extends a.WF{render(){return a.qy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="path"
        item-label-path="path"
        .value=${this._value}
        allow-custom-value
        .filteredItems=${this.navigationItems}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .renderer=${h}
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
        @filter-changed=${this._filterChanged}
      >
      </ha-combo-box>
    `}async _openedChanged(e){this._opened=e.detail.value,this._opened&&!this.navigationItemsLoaded&&this._loadNavigationItems()}async _loadNavigationItems(){this.navigationItemsLoaded=!0;const e=Object.entries(this.hass.panels).map((([e,t])=>({id:e,...t}))),t=e.filter((e=>"lovelace"===e.component_name)),o=await Promise.all(t.map((e=>{return(t=this.hass.connection,o="lovelace"===e.url_path?null:e.url_path,i=!0,t.sendMessagePromise({type:"lovelace/config",url_path:o,force:i})).then((t=>[e.id,t])).catch((t=>[e.id,void 0]));var t,o,i}))),i=new Map(o);this.navigationItems=[];for(const a of e){this.navigationItems.push(p(this.hass,a));const e=i.get(a.id);e&&"views"in e&&e.views.forEach(((e,t)=>this.navigationItems.push(c(a.url_path,e,t))))}this.comboBox.filteredItems=this.navigationItems}shouldUpdate(e){return!this._opened||e.has("_opened")}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,s.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}_filterChanged(e){const t=e.detail.value.toLowerCase();if(t.length>=2){const e=[];this.navigationItems.forEach((o=>{(o.path.toLowerCase().includes(t)||o.title.toLowerCase().includes(t))&&e.push(o)})),e.length>0?this.comboBox.filteredItems=e:this.comboBox.filteredItems=[]}else this.comboBox.filteredItems=this.navigationItems}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._opened=!1,this.navigationItemsLoaded=!1,this.navigationItems=d}}u.styles=a.AH`
    ha-icon,
    ha-svg-icon {
      color: var(--primary-text-color);
      position: relative;
      bottom: 0px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],u.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],u.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],u.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,i.__decorate)([(0,r.wk)()],u.prototype,"_opened",void 0),(0,i.__decorate)([(0,r.P)("ha-combo-box",!0)],u.prototype,"comboBox",void 0),u=(0,i.__decorate)([(0,r.EM)("ha-navigation-picker")],u)},37540:function(e,t,o){o.d(t,{Kq:()=>c});var i=o(63937),a=o(42017);const r=(e,t)=>{const o=e._$AN;if(void 0===o)return!1;for(const i of o)i._$AO?.(t,!1),r(i,t);return!0},s=e=>{let t,o;do{if(void 0===(t=e._$AM))break;o=t._$AN,o.delete(e),e=t}while(0===o?.size)},n=e=>{for(let t;t=e._$AM;e=t){let o=t._$AN;if(void 0===o)t._$AN=o=new Set;else if(o.has(e))break;o.add(e),h(t)}};function l(e){void 0!==this._$AN?(s(this),this._$AM=e,n(this)):this._$AM=e}function d(e,t=!1,o=0){const i=this._$AH,a=this._$AN;if(void 0!==a&&0!==a.size)if(t)if(Array.isArray(i))for(let n=o;n<i.length;n++)r(i[n],!1),s(i[n]);else null!=i&&(r(i,!1),s(i));else r(this,e)}const h=e=>{e.type==a.OA.CHILD&&(e._$AP??=d,e._$AQ??=l)};class c extends a.WL{_$AT(e,t,o){super._$AT(e,t,o),n(this),this.isConnected=e._$AU}_$AO(e,t=!0){e!==this.isConnected&&(this.isConnected=e,e?this.reconnected?.():this.disconnected?.()),t&&(r(this,e),s(this))}setValue(e){if((0,i.Rt)(this._$Ct))this._$Ct._$AI(e,this);else{const t=[...this._$Ct._$AH];t[this._$Ci]=e,this._$Ct._$AI(t,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}}};
//# sourceMappingURL=9853.28f51d93d7fa3ded.js.map