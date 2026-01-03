/*! For license information please see 1761.04dd2d4bf1b495ad.js.LICENSE.txt */
export const __webpack_id__="1761";export const __webpack_ids__=["1761"];export const __webpack_modules__={34887:function(e,t,o){var i=o(62826),a=o(27680),r=(o(99949),o(59924)),s=o(96196),n=o(77845),l=o(32288),d=o(92542),c=(o(94343),o(78740));class h extends c.h{willUpdate(e){super.willUpdate(e),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}constructor(...e){super(...e),this.forceBlankValue=!1}}(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"force-blank-value"})],h.prototype,"forceBlankValue",void 0),h=(0,i.__decorate)([(0,n.EM)("ha-combo-box-textfield")],h);o(60733),o(56768);(0,r.SF)("vaadin-combo-box-item",s.AH`
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
  `,(0,i.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,i.__decorate)([(0,n.MZ)()],u.prototype,"label",void 0),(0,i.__decorate)([(0,n.MZ)()],u.prototype,"value",void 0),(0,i.__decorate)([(0,n.MZ)()],u.prototype,"placeholder",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"validationMessage",void 0),(0,i.__decorate)([(0,n.MZ)()],u.prototype,"helper",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"error-message"})],u.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],u.prototype,"invalid",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],u.prototype,"icon",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"items",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"filteredItems",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"dataProvider",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"allow-custom-value",type:Boolean})],u.prototype,"allowCustomValue",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-value-path"})],u.prototype,"itemValuePath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-label-path"})],u.prototype,"itemLabelPath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:"item-id-path"})],u.prototype,"itemIdPath",void 0),(0,i.__decorate)([(0,n.MZ)({attribute:!1})],u.prototype,"renderer",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],u.prototype,"opened",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"hide-clear-icon"})],u.prototype,"hideClearIcon",void 0),(0,i.__decorate)([(0,n.MZ)({type:Boolean,attribute:"clear-initial-value"})],u.prototype,"clearInitialValue",void 0),(0,i.__decorate)([(0,n.P)("vaadin-combo-box-light",!0)],u.prototype,"_comboBox",void 0),(0,i.__decorate)([(0,n.P)("ha-combo-box-textfield",!0)],u.prototype,"_inputElement",void 0),(0,i.__decorate)([(0,n.wk)({type:Boolean})],u.prototype,"_forceBlankValue",void 0),u=(0,i.__decorate)([(0,n.EM)("ha-combo-box")],u)},88867:function(e,t,o){o.r(t),o.d(t,{HaIconPicker:()=>p});var i=o(62826),a=o(96196),r=o(77845),s=o(22786),n=o(92542),l=o(33978);o(34887),o(22598),o(94343);let d=[],c=!1;const h=async e=>{try{const t=l.y[e].getIconList;if("function"!=typeof t)return[];const o=await t();return o.map((t=>({icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:t.keywords??[]})))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},u=e=>a.qy`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${e.icon} slot="start"></ha-icon>
    ${e.icon}
  </ha-combo-box-item>
`;class p extends a.WF{render(){return a.qy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="icon"
        item-label-path="icon"
        .value=${this._value}
        allow-custom-value
        .dataProvider=${c?this._iconProvider:void 0}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .errorMessage=${this.errorMessage}
        .invalid=${this.invalid}
        .renderer=${u}
        icon
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
      >
        ${this._value||this.placeholder?a.qy`
              <ha-icon .icon=${this._value||this.placeholder} slot="icon">
              </ha-icon>
            `:a.qy`<slot slot="icon" name="fallback"></slot>`}
      </ha-combo-box>
    `}async _openedChanged(e){e.detail.value&&!c&&(await(async()=>{c=!0;const e=await o.e("3451").then(o.t.bind(o,83174,19));d=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(l.y).forEach((e=>{t.push(h(e))})),(await Promise.all(t)).forEach((e=>{d.push(...e)}))})(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,s.A)(((e,t=d)=>{if(!e)return t;const o=[],i=(e,t)=>o.push({icon:e,rank:t});for(const a of t)a.parts.has(e)?i(a.icon,1):a.keywords.includes(e)?i(a.icon,2):a.icon.includes(e)?i(a.icon,3):a.keywords.some((t=>t.includes(e)))&&i(a.icon,4);return 0===o.length&&i(e,0),o.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const o=this._filterIcons(e.filter.toLowerCase(),d),i=e.page*e.pageSize,a=i+e.pageSize;t(o.slice(i,a),o.length)}}}p.styles=a.AH`
    *[slot="icon"] {
      color: var(--primary-text-color);
      position: relative;
      bottom: 2px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `,(0,i.__decorate)([(0,r.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"value",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"label",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"helper",void 0),(0,i.__decorate)([(0,r.MZ)()],p.prototype,"placeholder",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"error-message"})],p.prototype,"errorMessage",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,i.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"invalid",void 0),p=(0,i.__decorate)([(0,r.EM)("ha-icon-picker")],p)},66280:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t),o.d(t,{HaIconSelector:()=>u});var a=o(62826),r=o(96196),s=o(77845),n=o(3890),l=o(92542),d=o(43197),c=(o(88867),o(4148)),h=e([c,d]);[c,d]=h.then?(await h)():h;class u extends r.WF{render(){const e=this.context?.icon_entity,t=e?this.hass.states[e]:void 0,o=this.selector.icon?.placeholder||t?.attributes.icon||t&&(0,n.T)((0,d.fq)(this.hass,t));return r.qy`
      <ha-icon-picker
        .hass=${this.hass}
        .label=${this.label}
        .value=${this.value}
        .required=${this.required}
        .disabled=${this.disabled}
        .helper=${this.helper}
        .placeholder=${this.selector.icon?.placeholder??o}
        @value-changed=${this._valueChanged}
      >
        ${!o&&t?r.qy`
              <ha-state-icon
                slot="fallback"
                .hass=${this.hass}
                .stateObj=${t}
              ></ha-state-icon>
            `:r.s6}
      </ha-icon-picker>
    `}_valueChanged(e){(0,l.r)(this,"value-changed",{value:e.detail.value})}constructor(...e){super(...e),this.disabled=!1,this.required=!0}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"selector",void 0),(0,a.__decorate)([(0,s.MZ)()],u.prototype,"value",void 0),(0,a.__decorate)([(0,s.MZ)()],u.prototype,"label",void 0),(0,a.__decorate)([(0,s.MZ)()],u.prototype,"helper",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"context",void 0),u=(0,a.__decorate)([(0,s.EM)("ha-selector-icon")],u),i()}catch(u){i(u)}}))},4148:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(62826),a=o(96196),r=o(77845),s=o(3890),n=o(97382),l=o(43197),d=(o(22598),o(60961),e([l]));l=(d.then?(await d)():d)[0];class c extends a.WF{render(){const e=this.icon||this.stateObj&&this.hass?.entities[this.stateObj.entity_id]?.icon||this.stateObj?.attributes.icon;if(e)return a.qy`<ha-icon .icon=${e}></ha-icon>`;if(!this.stateObj)return a.s6;if(!this.hass)return this._renderFallback();const t=(0,l.fq)(this.hass,this.stateObj,this.stateValue).then((e=>e?a.qy`<ha-icon .icon=${e}></ha-icon>`:this._renderFallback()));return a.qy`${(0,s.T)(t)}`}_renderFallback(){const e=(0,n.t)(this.stateObj);return a.qy`
      <ha-svg-icon
        .path=${l.l[e]||l.lW}
      ></ha-svg-icon>
    `}}(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"stateObj",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"stateValue",void 0),(0,i.__decorate)([(0,r.MZ)()],c.prototype,"icon",void 0),c=(0,i.__decorate)([(0,r.EM)("ha-state-icon")],c),t()}catch(c){t(c)}}))},37540:function(e,t,o){o.d(t,{Kq:()=>h});var i=o(63937),a=o(42017);const r=(e,t)=>{const o=e._$AN;if(void 0===o)return!1;for(const i of o)i._$AO?.(t,!1),r(i,t);return!0},s=e=>{let t,o;do{if(void 0===(t=e._$AM))break;o=t._$AN,o.delete(e),e=t}while(0===o?.size)},n=e=>{for(let t;t=e._$AM;e=t){let o=t._$AN;if(void 0===o)t._$AN=o=new Set;else if(o.has(e))break;o.add(e),c(t)}};function l(e){void 0!==this._$AN?(s(this),this._$AM=e,n(this)):this._$AM=e}function d(e,t=!1,o=0){const i=this._$AH,a=this._$AN;if(void 0!==a&&0!==a.size)if(t)if(Array.isArray(i))for(let n=o;n<i.length;n++)r(i[n],!1),s(i[n]);else null!=i&&(r(i,!1),s(i));else r(this,e)}const c=e=>{e.type==a.OA.CHILD&&(e._$AP??=d,e._$AQ??=l)};class h extends a.WL{_$AT(e,t,o){super._$AT(e,t,o),n(this),this.isConnected=e._$AU}_$AO(e,t=!0){e!==this.isConnected&&(this.isConnected=e,e?this.reconnected?.():this.disconnected?.()),t&&(r(this,e),s(this))}setValue(e){if((0,i.Rt)(this._$Ct))this._$Ct._$AI(e,this);else{const t=[...this._$Ct._$AH];t[this._$Ci]=e,this._$Ct._$AI(t,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}},3890:function(e,t,o){o.d(t,{T:()=>u});var i=o(5055),a=o(63937),r=o(37540);class s{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class n{get(){return this.Y}pause(){this.Y??=new Promise((e=>this.Z=e))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var l=o(42017);const d=e=>!(0,a.sO)(e)&&"function"==typeof e.then,c=1073741823;class h extends r.Kq{render(...e){return e.find((e=>!d(e)))??i.c0}update(e,t){const o=this._$Cbt;let a=o.length;this._$Cbt=t;const r=this._$CK,s=this._$CX;this.isConnected||this.disconnected();for(let i=0;i<t.length&&!(i>this._$Cwt);i++){const e=t[i];if(!d(e))return this._$Cwt=i,e;i<a&&e===o[i]||(this._$Cwt=c,a=0,Promise.resolve(e).then((async t=>{for(;s.get();)await s.get();const o=r.deref();if(void 0!==o){const i=o._$Cbt.indexOf(e);i>-1&&i<o._$Cwt&&(o._$Cwt=i,o.setValue(t))}})))}return i.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new s(this),this._$CX=new n}}const u=(0,l.u$)(h)}};
//# sourceMappingURL=1761.04dd2d4bf1b495ad.js.map