/*! For license information please see 1955.c4b1acb3cde89295.js.LICENSE.txt */
export const __webpack_id__="1955";export const __webpack_ids__=["1955"];export const __webpack_modules__={40404:function(e,t,o){o.d(t,{s:()=>a});const a=(e,t,o=!1)=>{let a;const i=(...i)=>{const r=o&&!a;clearTimeout(a),a=window.setTimeout((()=>{a=void 0,e(...i)}),t),r&&e(...i)};return i.cancel=()=>{clearTimeout(a)},i}},94343:function(e,t,o){var a=o(62826),i=o(96196),r=o(77845),s=o(23897);class n extends s.G{constructor(...e){super(...e),this.borderTop=!1}}n.styles=[...s.J,i.AH`
      :host {
        --md-list-item-one-line-container-height: 48px;
        --md-list-item-two-line-container-height: 64px;
      }
      :host([border-top]) md-item {
        border-top: 1px solid var(--divider-color);
      }
      [slot="start"] {
        --state-icon-color: var(--secondary-text-color);
      }
      [slot="headline"] {
        line-height: var(--ha-line-height-normal);
        font-size: var(--ha-font-size-m);
        white-space: nowrap;
      }
      [slot="supporting-text"] {
        line-height: var(--ha-line-height-normal);
        font-size: var(--ha-font-size-s);
        white-space: nowrap;
      }
      ::slotted(state-badge),
      ::slotted(img) {
        width: 32px;
        height: 32px;
      }
      ::slotted(.code) {
        font-family: var(--ha-font-family-code);
        font-size: var(--ha-font-size-xs);
      }
      ::slotted(.domain) {
        font-size: var(--ha-font-size-s);
        font-weight: var(--ha-font-weight-normal);
        line-height: var(--ha-line-height-normal);
        align-self: flex-end;
        max-width: 30%;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
      }
    `],(0,a.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"border-top"})],n.prototype,"borderTop",void 0),n=(0,a.__decorate)([(0,r.EM)("ha-combo-box-item")],n)},34887:function(e,t,o){var a=o(62826),i=o(27680),r=(o(99949),o(59924)),s=o(96196),n=o(77845),c=o(32288),d=o(92542),l=(o(94343),o(78740));class h extends l.h{willUpdate(e){super.willUpdate(e),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}constructor(...e){super(...e),this.forceBlankValue=!1}}(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"force-blank-value"})],h.prototype,"forceBlankValue",void 0),h=(0,a.__decorate)([(0,n.EM)("ha-combo-box-textfield")],h);o(60733),o(56768);(0,r.SF)("vaadin-combo-box-item",s.AH`
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
  `);class b extends s.WF{async open(){await this.updateComplete,this._comboBox?.open()}async focus(){await this.updateComplete,await(this._inputElement?.updateComplete),this._inputElement?.focus()}disconnectedCallback(){super.disconnectedCallback(),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}get selectedItem(){return this._comboBox.selectedItem}setInputValue(e){this._comboBox.value=e}setTextFieldValue(e){this._inputElement.value=e}render(){return s.qy`
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
        ${(0,i.d)(this.renderer||this._defaultRowRenderer)}
        @opened-changed=${this._openedChanged}
        @filter-changed=${this._filterChanged}
        @value-changed=${this._valueChanged}
        attr-for-value="value"
      >
        <ha-combo-box-textfield
          label=${(0,c.J)(this.label)}
          placeholder=${(0,c.J)(this.placeholder)}
          ?disabled=${this.disabled}
          ?required=${this.required}
          validationMessage=${(0,c.J)(this.validationMessage)}
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
              aria-label=${(0,c.J)(this.hass?.localize("ui.common.clear"))}
              class=${"clear-button "+(this.label?"":"no-label")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ?disabled=${this.disabled}
              @click=${this._clearValue}
            ></ha-svg-icon>`:""}
        <ha-svg-icon
          role="button"
          tabindex="-1"
          aria-label=${(0,c.J)(this.label)}
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
  `}}b.styles=s.AH`
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
  `,(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)()],b.prototype,"label",void 0),(0,a.__decorate)([(0,n.MZ)()],b.prototype,"value",void 0),(0,a.__decorate)([(0,n.MZ)()],b.prototype,"placeholder",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"validationMessage",void 0),(0,a.__decorate)([(0,n.MZ)()],b.prototype,"helper",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"error-message"})],b.prototype,"errorMessage",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"invalid",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"icon",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"items",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"filteredItems",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"dataProvider",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"allow-custom-value",type:Boolean})],b.prototype,"allowCustomValue",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"item-value-path"})],b.prototype,"itemValuePath",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"item-label-path"})],b.prototype,"itemLabelPath",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"item-id-path"})],b.prototype,"itemIdPath",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"renderer",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"required",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],b.prototype,"opened",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"hide-clear-icon"})],b.prototype,"hideClearIcon",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"clear-initial-value"})],b.prototype,"clearInitialValue",void 0),(0,a.__decorate)([(0,n.P)("vaadin-combo-box-light",!0)],b.prototype,"_comboBox",void 0),(0,a.__decorate)([(0,n.P)("ha-combo-box-textfield",!0)],b.prototype,"_inputElement",void 0),(0,a.__decorate)([(0,n.wk)({type:Boolean})],b.prototype,"_forceBlankValue",void 0),b=(0,a.__decorate)([(0,n.EM)("ha-combo-box")],b)},88867:function(e,t,o){o.r(t),o.d(t,{HaIconPicker:()=>p});var a=o(62826),i=o(96196),r=o(77845),s=o(22786),n=o(92542),c=o(33978);o(34887),o(22598),o(94343);let d=[],l=!1;const h=async e=>{try{const t=c.y[e].getIconList;if("function"!=typeof t)return[];const o=await t();return o.map((t=>({icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:t.keywords??[]})))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},b=e=>i.qy`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${e.icon} slot="start"></ha-icon>
    ${e.icon}
  </ha-combo-box-item>
`;class p extends i.WF{render(){return i.qy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="icon"
        item-label-path="icon"
        .value=${this._value}
        allow-custom-value
        .dataProvider=${l?this._iconProvider:void 0}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .errorMessage=${this.errorMessage}
        .invalid=${this.invalid}
        .renderer=${b}
        icon
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
      >
        ${this._value||this.placeholder?i.qy`
              <ha-icon .icon=${this._value||this.placeholder} slot="icon">
              </ha-icon>
            `:i.qy`<slot slot="icon" name="fallback"></slot>`}
      </ha-combo-box>
    `}async _openedChanged(e){e.detail.value&&!l&&(await(async()=>{l=!0;const e=await o.e("3451").then(o.t.bind(o,83174,19));d=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(c.y).forEach((e=>{t.push(h(e))})),(await Promise.all(t)).forEach((e=>{d.push(...e)}))})(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,s.A)(((e,t=d)=>{if(!e)return t;const o=[],a=(e,t)=>o.push({icon:e,rank:t});for(const i of t)i.parts.has(e)?a(i.icon,1):i.keywords.includes(e)?a(i.icon,2):i.icon.includes(e)?a(i.icon,3):i.keywords.some((t=>t.includes(e)))&&a(i.icon,4);return 0===o.length&&a(e,0),o.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const o=this._filterIcons(e.filter.toLowerCase(),d),a=e.page*e.pageSize,i=a+e.pageSize;t(o.slice(a,i),o.length)}}}p.styles=i.AH`
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
  `,(0,a.__decorate)([(0,r.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)()],p.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],p.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],p.prototype,"helper",void 0),(0,a.__decorate)([(0,r.MZ)()],p.prototype,"placeholder",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:"error-message"})],p.prototype,"errorMessage",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,a.__decorate)([(0,r.MZ)({type:Boolean})],p.prototype,"invalid",void 0),p=(0,a.__decorate)([(0,r.EM)("ha-icon-picker")],p)},22598:function(e,t,o){o.r(t),o.d(t,{HaIcon:()=>w});var a=o(62826),i=o(96196),r=o(77845),s=o(92542),n=o(40404),c=o(33978),d=o(95192),l=o(22786);class h extends Error{constructor(e,...t){super(...t),Error.captureStackTrace&&Error.captureStackTrace(this,h),this.name="TimeoutError",this.timeout=e,this.message=`Timed out in ${e} ms.`}}const b=JSON.parse('{"version":"7.4.47","parts":[{"file":"7a7139d465f1f41cb26ab851a17caa21a9331234"},{"start":"account-supervisor-circle-","file":"9561286c4c1021d46b9006596812178190a7cc1c"},{"start":"alpha-r-c","file":"eb466b7087fb2b4d23376ea9bc86693c45c500fa"},{"start":"arrow-decision-o","file":"4b3c01b7e0723b702940c5ac46fb9e555646972b"},{"start":"baby-f","file":"2611401d85450b95ab448ad1d02c1a432b409ed2"},{"start":"battery-hi","file":"89bcd31855b34cd9d31ac693fb073277e74f1f6a"},{"start":"blur-r","file":"373709cd5d7e688c2addc9a6c5d26c2d57c02c48"},{"start":"briefcase-account-","file":"a75956cf812ee90ee4f656274426aafac81e1053"},{"start":"calendar-question-","file":"3253f2529b5ebdd110b411917bacfacb5b7063e6"},{"start":"car-lig","file":"74566af3501ad6ae58ad13a8b6921b3cc2ef879d"},{"start":"cellphone-co","file":"7677f1cfb2dd4f5562a2aa6d3ae43a2e6997b21a"},{"start":"circle-slice-2","file":"70d08c50ec4522dd75d11338db57846588263ee2"},{"start":"cloud-co","file":"141d2bfa55ca4c83f4bae2812a5da59a84fec4ff"},{"start":"cog-s","file":"5a640365f8e47c609005d5e098e0e8104286d120"},{"start":"cookie-l","file":"dd85b8eb8581b176d3acf75d1bd82e61ca1ba2fc"},{"start":"currency-eur-","file":"15362279f4ebfc3620ae55f79d2830ad86d5213e"},{"start":"delete-o","file":"239434ab8df61237277d7599ebe066c55806c274"},{"start":"draw-","file":"5605918a592070803ba2ad05a5aba06263da0d70"},{"start":"emoticon-po","file":"a838cfcec34323946237a9f18e66945f55260f78"},{"start":"fan","file":"effd56103b37a8c7f332e22de8e4d67a69b70db7"},{"start":"file-question-","file":"b2424b50bd465ae192593f1c3d086c5eec893af8"},{"start":"flask-off-","file":"3b76295cde006a18f0301dd98eed8c57e1d5a425"},{"start":"food-s","file":"1c6941474cbeb1755faaaf5771440577f4f1f9c6"},{"start":"gamepad-u","file":"c6efe18db6bc9654ae3540c7dee83218a5450263"},{"start":"google-f","file":"df341afe6ad4437457cf188499cb8d2df8ac7b9e"},{"start":"head-c","file":"282121c9e45ed67f033edcc1eafd279334c00f46"},{"start":"home-pl","file":"27e8e38fc7adcacf2a210802f27d841b49c8c508"},{"start":"inbox-","file":"0f0316ec7b1b7f7ce3eaabce26c9ef619b5a1694"},{"start":"key-v","file":"ea33462be7b953ff1eafc5dac2d166b210685a60"},{"start":"leaf-circle-","file":"33db9bbd66ce48a2db3e987fdbd37fb0482145a4"},{"start":"lock-p","file":"b89e27ed39e9d10c44259362a4b57f3c579d3ec8"},{"start":"message-s","file":"7b5ab5a5cadbe06e3113ec148f044aa701eac53a"},{"start":"moti","file":"01024d78c248d36805b565e343dd98033cc3bcaf"},{"start":"newspaper-variant-o","file":"22a6ec4a4fdd0a7c0acaf805f6127b38723c9189"},{"start":"on","file":"c73d55b412f394e64632e2011a59aa05e5a1f50d"},{"start":"paw-ou","file":"3f669bf26d16752dc4a9ea349492df93a13dcfbf"},{"start":"pigg","file":"0c24edb27eb1c90b6e33fc05f34ef3118fa94256"},{"start":"printer-pos-sy","file":"41a55cda866f90b99a64395c3bb18c14983dcf0a"},{"start":"read","file":"c7ed91552a3a64c9be88c85e807404cf705b7edf"},{"start":"robot-vacuum-variant-o","file":"917d2a35d7268c0ea9ad9ecab2778060e19d90e0"},{"start":"sees","file":"6e82d9861d8fac30102bafa212021b819f303bdb"},{"start":"shoe-f","file":"e2fe7ce02b5472301418cc90a0e631f187b9f238"},{"start":"snowflake-m","file":"a28ba9f5309090c8b49a27ca20ff582a944f6e71"},{"start":"st","file":"7e92d03f095ec27e137b708b879dfd273bd735ab"},{"start":"su","file":"61c74913720f9de59a379bdca37f1d2f0dc1f9db"},{"start":"tag-plus-","file":"8f3184156a4f38549cf4c4fffba73a6a941166ae"},{"start":"timer-a","file":"baab470d11cfb3a3cd3b063ee6503a77d12a80d0"},{"start":"transit-d","file":"8561c0d9b1ac03fab360fd8fe9729c96e8693239"},{"start":"vector-arrange-b","file":"c9a3439257d4bab33d3355f1f2e11842e8171141"},{"start":"water-ou","file":"02dbccfb8ca35f39b99f5a085b095fc1275005a0"},{"start":"webc","file":"57bafd4b97341f4f2ac20a609d023719f23a619c"},{"start":"zip","file":"65ae094e8263236fa50486584a08c03497a38d93"}]}'),p=(0,l.A)((async()=>{const e=(0,d.y$)("hass-icon-db","mdi-icon-store");{const t=await(0,d.Jt)("_version",e);t?t!==b.version&&(await(0,d.IU)(e),(0,d.hZ)("_version",b.version,e)):(0,d.hZ)("_version",b.version,e)}return e})),f=["mdi","hass","hassio","hademo"];let u=[];const v=e=>new Promise(((t,o)=>{if(u.push([e,t,o]),u.length>1)return;const a=p();((e,t)=>{const o=new Promise(((t,o)=>{setTimeout((()=>{o(new h(e))}),e)}));return Promise.race([t,o])})(1e3,(async()=>{(await a)("readonly",(e=>{for(const[t,o,a]of u)(0,d.Yd)(e.get(t)).then((e=>o(e))).catch((e=>a(e)));u=[]}))})()).catch((e=>{for(const[,,t]of u)t(e);u=[]}))}));o(60961);const _={},m={},y=(0,n.s)((()=>(async e=>{const t=Object.keys(e),o=await Promise.all(Object.values(e));(await p())("readwrite",(a=>{o.forEach(((o,i)=>{Object.entries(o).forEach((([e,t])=>{a.put(t,e)})),delete e[t[i]]}))}))})(m)),2e3),g={};class w extends i.WF{willUpdate(e){super.willUpdate(e),e.has("icon")&&(this._path=void 0,this._secondaryPath=void 0,this._viewBox=void 0,this._loadIcon())}render(){return this.icon?this._legacy?i.qy`<!-- @ts-ignore we don't provide the iron-icon element -->
        <iron-icon .icon=${this.icon}></iron-icon>`:i.qy`<ha-svg-icon
      .path=${this._path}
      .secondaryPath=${this._secondaryPath}
      .viewBox=${this._viewBox}
    ></ha-svg-icon>`:i.s6}async _loadIcon(){if(!this.icon)return;const e=this.icon,[t,a]=this.icon.split(":",2);let i,r=a;if(!t||!r)return;if(!f.includes(t)){const o=c.y[t];return o?void(o&&"function"==typeof o.getIcon&&this._setCustomPath(o.getIcon(r),e)):void(this._legacy=!0)}if(this._legacy=!1,r in _){const e=_[r];let o;e.newName?(o=`Icon ${t}:${r} was renamed to ${t}:${e.newName}, please change your config, it will be removed in version ${e.removeIn}.`,r=e.newName):o=`Icon ${t}:${r} was removed from MDI, please replace this icon with an other icon in your config, it will be removed in version ${e.removeIn}.`,console.warn(o),(0,s.r)(this,"write_log",{level:"warning",message:o})}if(r in g)return void(this._path=g[r]);if("home-assistant"===r){const t=(await o.e("7806").then(o.bind(o,7053))).mdiHomeAssistant;return this.icon===e&&(this._path=t),void(g[r]=t)}try{i=await v(r)}catch(l){i=void 0}if(i)return this.icon===e&&(this._path=i),void(g[r]=i);const n=(e=>{let t;for(const o of b.parts){if(void 0!==o.start&&e<o.start)break;t=o}return t.file})(r);if(n in m)return void this._setPath(m[n],r,e);const d=fetch(`/static/mdi/${n}.json`).then((e=>e.json()));m[n]=d,this._setPath(d,r,e),y()}async _setCustomPath(e,t){const o=await e;this.icon===t&&(this._path=o.path,this._secondaryPath=o.secondaryPath,this._viewBox=o.viewBox)}async _setPath(e,t,o){const a=await e;this.icon===o&&(this._path=a[t]),g[t]=a[t]}constructor(...e){super(...e),this._legacy=!1}}w.styles=i.AH`
    :host {
      fill: currentcolor;
    }
  `,(0,a.__decorate)([(0,r.MZ)()],w.prototype,"icon",void 0),(0,a.__decorate)([(0,r.wk)()],w.prototype,"_path",void 0),(0,a.__decorate)([(0,r.wk)()],w.prototype,"_secondaryPath",void 0),(0,a.__decorate)([(0,r.wk)()],w.prototype,"_viewBox",void 0),(0,a.__decorate)([(0,r.wk)()],w.prototype,"_legacy",void 0),w=(0,a.__decorate)([(0,r.EM)("ha-icon")],w)},33978:function(e,t,o){o.d(t,{y:()=>s});const a=window;"customIconsets"in a||(a.customIconsets={});const i=a.customIconsets,r=window;"customIcons"in r||(r.customIcons={});const s=new Proxy(r.customIcons,{get:(e,t)=>e[t]??(i[t]?{getIcon:i[t]}:void 0)})},95192:function(e,t,o){function a(e){return new Promise(((t,o)=>{e.oncomplete=e.onsuccess=()=>t(e.result),e.onabort=e.onerror=()=>o(e.error)}))}function i(e,t){let o;return(i,r)=>(()=>{if(o)return o;const i=indexedDB.open(e);return i.onupgradeneeded=()=>i.result.createObjectStore(t),o=a(i),o.then((e=>{e.onclose=()=>o=void 0}),(()=>{})),o})().then((e=>r(e.transaction(t,i).objectStore(t))))}let r;function s(){return r||(r=i("keyval-store","keyval")),r}function n(e,t=s()){return t("readonly",(t=>a(t.get(e))))}function c(e,t,o=s()){return o("readwrite",(o=>(o.put(t,e),a(o.transaction))))}function d(e=s()){return e("readwrite",(e=>(e.clear(),a(e.transaction))))}o.d(t,{IU:()=>d,Jt:()=>n,Yd:()=>a,hZ:()=>c,y$:()=>i})},37540:function(e,t,o){o.d(t,{Kq:()=>h});var a=o(63937),i=o(42017);const r=(e,t)=>{const o=e._$AN;if(void 0===o)return!1;for(const a of o)a._$AO?.(t,!1),r(a,t);return!0},s=e=>{let t,o;do{if(void 0===(t=e._$AM))break;o=t._$AN,o.delete(e),e=t}while(0===o?.size)},n=e=>{for(let t;t=e._$AM;e=t){let o=t._$AN;if(void 0===o)t._$AN=o=new Set;else if(o.has(e))break;o.add(e),l(t)}};function c(e){void 0!==this._$AN?(s(this),this._$AM=e,n(this)):this._$AM=e}function d(e,t=!1,o=0){const a=this._$AH,i=this._$AN;if(void 0!==i&&0!==i.size)if(t)if(Array.isArray(a))for(let n=o;n<a.length;n++)r(a[n],!1),s(a[n]);else null!=a&&(r(a,!1),s(a));else r(this,e)}const l=e=>{e.type==i.OA.CHILD&&(e._$AP??=d,e._$AQ??=c)};class h extends i.WL{_$AT(e,t,o){super._$AT(e,t,o),n(this),this.isConnected=e._$AU}_$AO(e,t=!0){e!==this.isConnected&&(this.isConnected=e,e?this.reconnected?.():this.disconnected?.()),t&&(r(this,e),s(this))}setValue(e){if((0,a.Rt)(this._$Ct))this._$Ct._$AI(e,this);else{const t=[...this._$Ct._$AH];t[this._$Ci]=e,this._$Ct._$AI(t,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}}};
//# sourceMappingURL=1955.c4b1acb3cde89295.js.map