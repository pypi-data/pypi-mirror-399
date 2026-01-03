"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8451"],{11851:function(e,t,i){var o=i(44734),a=i(56038),n=i(69683),r=i(6454),l=i(25460),s=(i(28706),i(62826)),d=i(77845),c=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(a))).forceBlankValue=!1,e}return(0,r.A)(t,e),(0,a.A)(t,[{key:"willUpdate",value:function(e){(0,l.A)(t,"willUpdate",this,3)([e]),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}}])}(i(78740).h);(0,s.__decorate)([(0,d.MZ)({type:Boolean,attribute:"force-blank-value"})],c.prototype,"forceBlankValue",void 0),c=(0,s.__decorate)([(0,d.EM)("ha-combo-box-textfield")],c)},55179:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(61397),a=i(50264),n=i(44734),r=i(56038),l=i(69683),s=i(6454),d=i(25460),c=(i(28706),i(18111),i(7588),i(26099),i(23500),i(62826)),h=i(27680),p=i(34648),u=i(29289),_=i(96196),v=i(77845),y=i(32288),m=i(92542),b=(i(94343),i(11851),i(60733),i(56768),i(78740),e([p]));p=(b.then?(await b)():b)[0];var f,g,$,M,k,x,A,w=e=>e;(0,u.SF)("vaadin-combo-box-item",(0,_.AH)(f||(f=w`
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
  `)));var C=function(e){function t(){var e;(0,n.A)(this,t);for(var i=arguments.length,o=new Array(i),a=0;a<i;a++)o[a]=arguments[a];return(e=(0,l.A)(this,t,[].concat(o))).invalid=!1,e.icon=!1,e.allowCustomValue=!1,e.itemValuePath="value",e.itemLabelPath="label",e.disabled=!1,e.required=!1,e.opened=!1,e.hideClearIcon=!1,e.clearInitialValue=!1,e._forceBlankValue=!1,e._defaultRowRenderer=t=>(0,_.qy)(g||(g=w`
    <ha-combo-box-item type="button">
      ${0}
    </ha-combo-box-item>
  `),e.itemLabelPath?t[e.itemLabelPath]:t),e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"open",value:(c=(0,a.A)((0,o.A)().m((function e(){var t;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:null===(t=this._comboBox)||void 0===t||t.open();case 2:return e.a(2)}}),e,this)}))),function(){return c.apply(this,arguments)})},{key:"focus",value:(i=(0,a.A)((0,o.A)().m((function e(){var t,i;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:return e.n=2,null===(t=this._inputElement)||void 0===t?void 0:t.updateComplete;case 2:null===(i=this._inputElement)||void 0===i||i.focus();case 3:return e.a(2)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"disconnectedCallback",value:function(){(0,d.A)(t,"disconnectedCallback",this,3)([]),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}},{key:"selectedItem",get:function(){return this._comboBox.selectedItem}},{key:"setInputValue",value:function(e){this._comboBox.value=e}},{key:"setTextFieldValue",value:function(e){this._inputElement.value=e}},{key:"render",value:function(){var e;return(0,_.qy)($||($=w`
      <!-- @ts-ignore Tag definition is not included in theme folder -->
      <vaadin-combo-box-light
        .itemValuePath=${0}
        .itemIdPath=${0}
        .itemLabelPath=${0}
        .items=${0}
        .value=${0}
        .filteredItems=${0}
        .dataProvider=${0}
        .allowCustomValue=${0}
        .disabled=${0}
        .required=${0}
        ${0}
        @opened-changed=${0}
        @filter-changed=${0}
        @value-changed=${0}
        attr-for-value="value"
      >
        <ha-combo-box-textfield
          label=${0}
          placeholder=${0}
          ?disabled=${0}
          ?required=${0}
          validationMessage=${0}
          .errorMessage=${0}
          class="input"
          autocapitalize="none"
          autocomplete="off"
          .autocorrect=${0}
          input-spellcheck="false"
          .suffix=${0}
          .icon=${0}
          .invalid=${0}
          .forceBlankValue=${0}
        >
          <slot name="icon" slot="leadingIcon"></slot>
        </ha-combo-box-textfield>
        ${0}
        <ha-svg-icon
          role="button"
          tabindex="-1"
          aria-label=${0}
          aria-expanded=${0}
          class=${0}
          .path=${0}
          ?disabled=${0}
          @click=${0}
        ></ha-svg-icon>
      </vaadin-combo-box-light>
      ${0}
    `),this.itemValuePath,this.itemIdPath,this.itemLabelPath,this.items,this.value||"",this.filteredItems,this.dataProvider,this.allowCustomValue,this.disabled,this.required,(0,h.d)(this.renderer||this._defaultRowRenderer),this._openedChanged,this._filterChanged,this._valueChanged,(0,y.J)(this.label),(0,y.J)(this.placeholder),this.disabled,this.required,(0,y.J)(this.validationMessage),this.errorMessage,!1,(0,_.qy)(M||(M=w`<div
            style="width: 28px;"
            role="none presentation"
          ></div>`)),this.icon,this.invalid,this._forceBlankValue,this.value&&!this.hideClearIcon?(0,_.qy)(k||(k=w`<ha-svg-icon
              role="button"
              tabindex="-1"
              aria-label=${0}
              class=${0}
              .path=${0}
              ?disabled=${0}
              @click=${0}
            ></ha-svg-icon>`),(0,y.J)(null===(e=this.hass)||void 0===e?void 0:e.localize("ui.common.clear")),"clear-button "+(this.label?"":"no-label"),"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",this.disabled,this._clearValue):"",(0,y.J)(this.label),this.opened?"true":"false","toggle-button "+(this.label?"":"no-label"),this.opened?"M7,15L12,10L17,15H7Z":"M7,10L12,15L17,10H7Z",this.disabled,this._toggleOpen,this._renderHelper())}},{key:"_renderHelper",value:function(){return this.helper?(0,_.qy)(x||(x=w`<ha-input-helper-text .disabled=${0}
          >${0}</ha-input-helper-text
        >`),this.disabled,this.helper):""}},{key:"_clearValue",value:function(e){e.stopPropagation(),(0,m.r)(this,"value-changed",{value:void 0})}},{key:"_toggleOpen",value:function(e){var t,i;this.opened?(null===(t=this._comboBox)||void 0===t||t.close(),e.stopPropagation()):null===(i=this._comboBox)||void 0===i||i.inputElement.focus()}},{key:"_openedChanged",value:function(e){e.stopPropagation();var t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,m.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){var i=document.querySelector("vaadin-combo-box-overlay");i&&this._removeInert(i),this._observeBody()}else{var o;null===(o=this._bodyMutationObserver)||void 0===o||o.disconnect(),this._bodyMutationObserver=void 0}}},{key:"_observeBody",value:function(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{var t;"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}},{key:"_removeInert",value:function(e){var t;if(e.inert)return e.inert=!1,null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){var t,i=e.target;if(i.inert)null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),this._overlayMutationObserver=void 0,i.inert=!1}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}},{key:"_filterChanged",value:function(e){e.stopPropagation(),(0,m.r)(this,"filter-changed",{value:e.detail.value})}},{key:"_valueChanged",value:function(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),this.opened){var t=e.detail.value;t!==this.value&&(0,m.r)(this,"value-changed",{value:t||void 0})}}}]);var i,c}(_.WF);C.styles=(0,_.AH)(A||(A=w`
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
  `)),(0,c.__decorate)([(0,v.MZ)({attribute:!1})],C.prototype,"hass",void 0),(0,c.__decorate)([(0,v.MZ)()],C.prototype,"label",void 0),(0,c.__decorate)([(0,v.MZ)()],C.prototype,"value",void 0),(0,c.__decorate)([(0,v.MZ)()],C.prototype,"placeholder",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:!1})],C.prototype,"validationMessage",void 0),(0,c.__decorate)([(0,v.MZ)()],C.prototype,"helper",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:"error-message"})],C.prototype,"errorMessage",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean})],C.prototype,"invalid",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean})],C.prototype,"icon",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:!1})],C.prototype,"items",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:!1})],C.prototype,"filteredItems",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:!1})],C.prototype,"dataProvider",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:"allow-custom-value",type:Boolean})],C.prototype,"allowCustomValue",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:"item-value-path"})],C.prototype,"itemValuePath",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:"item-label-path"})],C.prototype,"itemLabelPath",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:"item-id-path"})],C.prototype,"itemIdPath",void 0),(0,c.__decorate)([(0,v.MZ)({attribute:!1})],C.prototype,"renderer",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean})],C.prototype,"disabled",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean})],C.prototype,"required",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],C.prototype,"opened",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean,attribute:"hide-clear-icon"})],C.prototype,"hideClearIcon",void 0),(0,c.__decorate)([(0,v.MZ)({type:Boolean,attribute:"clear-initial-value"})],C.prototype,"clearInitialValue",void 0),(0,c.__decorate)([(0,v.P)("vaadin-combo-box-light",!0)],C.prototype,"_comboBox",void 0),(0,c.__decorate)([(0,v.P)("ha-combo-box-textfield",!0)],C.prototype,"_inputElement",void 0),(0,c.__decorate)([(0,v.wk)({type:Boolean})],C.prototype,"_forceBlankValue",void 0),C=(0,c.__decorate)([(0,v.EM)("ha-combo-box")],C),t()}catch(Z){t(Z)}}))},19247:function(e,t,i){var o=i(56038),a=i(44734),n=i(69683),r=i(6454),l=(i(28706),i(33771),i(2892),i(62826)),s=i(4042),d=i(77845),c=function(e){function t(){var e;(0,a.A)(this,t);for(var i=arguments.length,o=new Array(i),r=0;r<i;r++)o[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(o))).name="fadeIn",e.fill="both",e.play=!0,e.iterations=1,e}return(0,r.A)(t,e),(0,o.A)(t)}(s.A);(0,l.__decorate)([(0,d.MZ)()],c.prototype,"name",void 0),(0,l.__decorate)([(0,d.MZ)()],c.prototype,"fill",void 0),(0,l.__decorate)([(0,d.MZ)({type:Boolean})],c.prototype,"play",void 0),(0,l.__decorate)([(0,d.MZ)({type:Number})],c.prototype,"iterations",void 0),c=(0,l.__decorate)([(0,d.EM)("ha-fade-in")],c)},68757:function(e,t,i){var o,a,n,r=i(44734),l=i(56038),s=i(69683),d=i(6454),c=(i(28706),i(2892),i(62826)),h=i(96196),p=i(77845),u=(i(60733),i(78740),e=>e),_=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,o=new Array(i),a=0;a<i;a++)o[a]=arguments[a];return(e=(0,s.A)(this,t,[].concat(o))).icon=!1,e.iconTrailing=!1,e.autocorrect=!0,e.value="",e.placeholder="",e.label="",e.disabled=!1,e.required=!1,e.minLength=-1,e.maxLength=-1,e.outlined=!1,e.helper="",e.validateOnInitialRender=!1,e.validationMessage="",e.autoValidate=!1,e.pattern="",e.size=null,e.helperPersistent=!1,e.charCounter=!1,e.endAligned=!1,e.prefix="",e.suffix="",e.name="",e.readOnly=!1,e.autocapitalize="",e._unmaskedPassword=!1,e}return(0,d.A)(t,e),(0,l.A)(t,[{key:"render",value:function(){var e;return(0,h.qy)(o||(o=u`<ha-textfield
        .invalid=${0}
        .errorMessage=${0}
        .icon=${0}
        .iconTrailing=${0}
        .autocomplete=${0}
        .autocorrect=${0}
        .inputSpellcheck=${0}
        .value=${0}
        .placeholder=${0}
        .label=${0}
        .disabled=${0}
        .required=${0}
        .minLength=${0}
        .maxLength=${0}
        .outlined=${0}
        .helper=${0}
        .validateOnInitialRender=${0}
        .validationMessage=${0}
        .autoValidate=${0}
        .pattern=${0}
        .size=${0}
        .helperPersistent=${0}
        .charCounter=${0}
        .endAligned=${0}
        .prefix=${0}
        .name=${0}
        .inputMode=${0}
        .readOnly=${0}
        .autocapitalize=${0}
        .type=${0}
        .suffix=${0}
        @input=${0}
        @change=${0}
      ></ha-textfield>
      <ha-icon-button
        .label=${0}
        @click=${0}
        .path=${0}
      ></ha-icon-button>`),this.invalid,this.errorMessage,this.icon,this.iconTrailing,this.autocomplete,this.autocorrect,this.inputSpellcheck,this.value,this.placeholder,this.label,this.disabled,this.required,this.minLength,this.maxLength,this.outlined,this.helper,this.validateOnInitialRender,this.validationMessage,this.autoValidate,this.pattern,this.size,this.helperPersistent,this.charCounter,this.endAligned,this.prefix,this.name,this.inputMode,this.readOnly,this.autocapitalize,this._unmaskedPassword?"text":"password",(0,h.qy)(a||(a=u`<div style="width: 24px"></div>`)),this._handleInputEvent,this._handleChangeEvent,(null===(e=this.hass)||void 0===e?void 0:e.localize(this._unmaskedPassword?"ui.components.selectors.text.hide_password":"ui.components.selectors.text.show_password"))||(this._unmaskedPassword?"Hide password":"Show password"),this._toggleUnmaskedPassword,this._unmaskedPassword?"M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z":"M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z")}},{key:"focus",value:function(){this._textField.focus()}},{key:"checkValidity",value:function(){return this._textField.checkValidity()}},{key:"reportValidity",value:function(){return this._textField.reportValidity()}},{key:"setCustomValidity",value:function(e){return this._textField.setCustomValidity(e)}},{key:"layout",value:function(){return this._textField.layout()}},{key:"_toggleUnmaskedPassword",value:function(){this._unmaskedPassword=!this._unmaskedPassword}},{key:"_handleInputEvent",value:function(e){this.value=e.target.value}},{key:"_handleChangeEvent",value:function(e){this.value=e.target.value,this._reDispatchEvent(e)}},{key:"_reDispatchEvent",value:function(e){var t=new Event(e.type,e);this.dispatchEvent(t)}}])}(h.WF);_.styles=(0,h.AH)(n||(n=u`
    :host {
      display: block;
      position: relative;
    }
    ha-textfield {
      width: 100%;
    }
    ha-icon-button {
      position: absolute;
      top: 8px;
      right: 8px;
      inset-inline-start: initial;
      inset-inline-end: 8px;
      --mdc-icon-button-size: 40px;
      --mdc-icon-size: 20px;
      color: var(--secondary-text-color);
      direction: var(--direction);
    }
  `)),(0,c.__decorate)([(0,p.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"invalid",void 0),(0,c.__decorate)([(0,p.MZ)({attribute:"error-message"})],_.prototype,"errorMessage",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"icon",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"iconTrailing",void 0),(0,c.__decorate)([(0,p.MZ)()],_.prototype,"autocomplete",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"autocorrect",void 0),(0,c.__decorate)([(0,p.MZ)({attribute:"input-spellcheck"})],_.prototype,"inputSpellcheck",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"value",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"placeholder",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"label",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],_.prototype,"disabled",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,c.__decorate)([(0,p.MZ)({type:Number})],_.prototype,"minLength",void 0),(0,c.__decorate)([(0,p.MZ)({type:Number})],_.prototype,"maxLength",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],_.prototype,"outlined",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"helper",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"validateOnInitialRender",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"validationMessage",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"autoValidate",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"pattern",void 0),(0,c.__decorate)([(0,p.MZ)({type:Number})],_.prototype,"size",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"helperPersistent",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"charCounter",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"endAligned",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"prefix",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"suffix",void 0),(0,c.__decorate)([(0,p.MZ)({type:String})],_.prototype,"name",void 0),(0,c.__decorate)([(0,p.MZ)({type:String,attribute:"input-mode"})],_.prototype,"inputMode",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"readOnly",void 0),(0,c.__decorate)([(0,p.MZ)({attribute:!1,type:String})],_.prototype,"autocapitalize",void 0),(0,c.__decorate)([(0,p.wk)()],_.prototype,"_unmaskedPassword",void 0),(0,c.__decorate)([(0,p.P)("ha-textfield")],_.prototype,"_textField",void 0),(0,c.__decorate)([(0,p.Ls)({passive:!0})],_.prototype,"_handleInputEvent",null),(0,c.__decorate)([(0,p.Ls)({passive:!0})],_.prototype,"_handleChangeEvent",null),_=(0,c.__decorate)([(0,p.EM)("ha-password-field")],_)},54457:function(e,t,i){i.d(t,{MV:function(){return r},d8:function(){return n}});var o=i(61397),a=i(50264),n=function(){var e=(0,a.A)((0,o.A)().m((function e(t){return(0,o.A)().w((function(e){for(;;)if(0===e.n)return e.a(2,t.callWS({type:"application_credentials/config"}))}),e)})));return function(t){return e.apply(this,arguments)}}(),r=function(){var e=(0,a.A)((0,o.A)().m((function e(t,i,a,n,r){return(0,o.A)().w((function(e){for(;;)if(0===e.n)return e.a(2,t.callWS({type:"application_credentials/create",domain:i,client_id:a,client_secret:n,name:r}))}),e)})));return function(t,i,o,a,n){return e.apply(this,arguments)}}()},71614:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{DialogAddApplicationCredential:function(){return z}});var a=i(61397),n=i(50264),r=i(44734),l=i(56038),s=i(69683),d=i(6454),c=(i(28706),i(62062),i(18111),i(61701),i(26099),i(62826)),h=i(96196),p=i(77845),u=i(92542),_=(i(17963),i(89473)),v=i(55179),y=i(95637),m=(i(19247),i(28089),i(68757),i(89600)),b=(i(78740),i(54457)),f=i(84125),g=i(39396),$=i(62001),M=e([_,v,m]);[_,v,m]=M.then?(await M)():M;var k,x,A,w,C,Z,V,B,L,O,P=e=>e,I="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z",z=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,o=new Array(i),a=0;a<i;a++)o[a]=arguments[a];return(e=(0,s.A)(this,t,[].concat(o)))._loading=!1,e}return(0,d.A)(t,e),(0,l.A)(t,[{key:"showDialog",value:function(e){this._params=e,this._domain=e.selectedDomain,this._manifest=e.manifest,this._name="",this._description="",this._clientId="",this._clientSecret="",this._error=void 0,this._loading=!1,this._fetchConfig()}},{key:"_fetchConfig",value:(c=(0,n.A)((0,a.A)().m((function e(){return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,(0,b.d8)(this.hass);case 1:return this._config=e.v,this._domains=Object.keys(this._config.integrations).map((e=>({id:e,name:(0,f.p$)(this.hass.localize,e)}))),e.n=2,this.hass.loadBackendTranslation("application_credentials");case 2:this._updateDescription();case 3:return e.a(2)}}),e,this)}))),function(){return c.apply(this,arguments)})},{key:"render",value:function(){var e,t;if(!this._params)return h.s6;var i=this._params.selectedDomain?(0,f.p$)(this.hass.localize,this._domain):"";return(0,h.qy)(k||(k=P`
      <ha-dialog
        open
        @closed=${0}
        scrimClickAction
        escapeKeyAction
        .heading=${0}
      >
        ${0}
      </ha-dialog>
    `),this._abortDialog,(0,y.l)(this.hass,this.hass.localize("ui.panel.config.application_credentials.editor.caption")),this._config?(0,h.qy)(A||(A=P`<div>
                ${0}
                ${0}
                ${0}
                ${0}
                ${0}
                <ha-textfield
                  class="name"
                  name="name"
                  .label=${0}
                  .value=${0}
                  required
                  @input=${0}
                  .validationMessage=${0}
                  dialogInitialFocus
                ></ha-textfield>
                <ha-textfield
                  class="clientId"
                  name="clientId"
                  .label=${0}
                  .value=${0}
                  required
                  @input=${0}
                  .validationMessage=${0}
                  dialogInitialFocus
                  .helper=${0}
                  helperPersistent
                ></ha-textfield>
                <ha-password-field
                  .label=${0}
                  name="clientSecret"
                  .value=${0}
                  required
                  @input=${0}
                  .validationMessage=${0}
                  .helper=${0}
                  helperPersistent
                ></ha-password-field>
              </div>

              <ha-button
                appearance="plain"
                slot="secondaryAction"
                @click=${0}
                .disabled=${0}
              >
                ${0}
              </ha-button>
              <ha-button
                slot="primaryAction"
                .disabled=${0}
                @click=${0}
                .loading=${0}
              >
                ${0}
              </ha-button>`),this._error?(0,h.qy)(w||(w=P`<ha-alert alert-type="error"
                      >${0}</ha-alert
                    > `),this._error):h.s6,this._params.selectedDomain&&!this._description?(0,h.qy)(C||(C=P`<p>
                      ${0}
                      ${0}
                    </p>`),this.hass.localize("ui.panel.config.application_credentials.editor.missing_credentials",{integration:i}),null!==(e=this._manifest)&&void 0!==e&&e.is_built_in||null!==(t=this._manifest)&&void 0!==t&&t.documentation?(0,h.qy)(Z||(Z=P`<a
                            href=${0}
                            target="_blank"
                            rel="noreferrer"
                          >
                            ${0}
                            <ha-svg-icon .path=${0}></ha-svg-icon>
                          </a>`),this._manifest.is_built_in?(0,$.o)(this.hass,`/integrations/${this._domain}`):this._manifest.documentation,this.hass.localize("ui.panel.config.application_credentials.editor.missing_credentials_domain_link",{integration:i}),I):h.s6):h.s6,this._params.selectedDomain&&this._description?h.s6:(0,h.qy)(V||(V=P`<p>
                      ${0}
                      <a
                        href=${0}
                        target="_blank"
                        rel="noreferrer"
                      >
                        ${0}
                        <ha-svg-icon .path=${0}></ha-svg-icon>
                      </a>
                    </p>`),this.hass.localize("ui.panel.config.application_credentials.editor.description"),(0,$.o)(this.hass,"/integrations/application_credentials"),this.hass.localize("ui.panel.config.application_credentials.editor.view_documentation"),I),this._params.selectedDomain?h.s6:(0,h.qy)(B||(B=P`<ha-combo-box
                      name="domain"
                      .hass=${0}
                      .label=${0}
                      .value=${0}
                      .items=${0}
                      item-id-path="id"
                      item-value-path="id"
                      item-label-path="name"
                      required
                      @value-changed=${0}
                    ></ha-combo-box>`),this.hass,this.hass.localize("ui.panel.config.application_credentials.editor.domain"),this._domain,this._domains,this._handleDomainPicked),this._description?(0,h.qy)(L||(L=P`<ha-markdown
                      breaks
                      .content=${0}
                    ></ha-markdown>`),this._description):h.s6,this.hass.localize("ui.panel.config.application_credentials.editor.name"),this._name,this._handleValueChanged,this.hass.localize("ui.common.error_required"),this.hass.localize("ui.panel.config.application_credentials.editor.client_id"),this._clientId,this._handleValueChanged,this.hass.localize("ui.common.error_required"),this.hass.localize("ui.panel.config.application_credentials.editor.client_id_helper"),this.hass.localize("ui.panel.config.application_credentials.editor.client_secret"),this._clientSecret,this._handleValueChanged,this.hass.localize("ui.common.error_required"),this.hass.localize("ui.panel.config.application_credentials.editor.client_secret_helper"),this._abortDialog,this._loading,this.hass.localize("ui.common.cancel"),!this._domain||!this._clientId||!this._clientSecret,this._addApplicationCredential,this._loading,this.hass.localize("ui.panel.config.application_credentials.editor.add")):(0,h.qy)(x||(x=P`<ha-fade-in .delay=${0}>
              <ha-spinner size="large"></ha-spinner>
            </ha-fade-in>`),500))}},{key:"closeDialog",value:function(){this._params=void 0,this._domains=void 0,(0,u.r)(this,"dialog-closed",{dialog:this.localName})}},{key:"_handleDomainPicked",value:function(e){e.stopPropagation(),this._domain=e.detail.value,this._updateDescription()}},{key:"_updateDescription",value:(o=(0,n.A)((0,a.A)().m((function e(){var t;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:if(this._domain){e.n=1;break}return e.a(2);case 1:return e.n=2,this.hass.loadBackendTranslation("application_credentials",this._domain);case 2:t=this._config.integrations[this._domain],this._description=this.hass.localize(`component.${this._domain}.application_credentials.description`,t.description_placeholders);case 3:return e.a(2)}}),e,this)}))),function(){return o.apply(this,arguments)})},{key:"_handleValueChanged",value:function(e){this._error=void 0;var t=e.target.name,i=e.target.value;this[`_${t}`]=i}},{key:"_abortDialog",value:function(){this._params&&this._params.dialogAbortedCallback&&this._params.dialogAbortedCallback(),this.closeDialog()}},{key:"_addApplicationCredential",value:(i=(0,n.A)((0,a.A)().m((function e(t){var i,o;return(0,a.A)().w((function(e){for(;;)switch(e.p=e.n){case 0:if(t.preventDefault(),this._domain&&this._clientId&&this._clientSecret){e.n=1;break}return e.a(2);case 1:return this._loading=!0,this._error="",e.p=2,e.n=3,(0,b.MV)(this.hass,this._domain,this._clientId,this._clientSecret,this._name);case 3:i=e.v,e.n=5;break;case 4:return e.p=4,o=e.v,this._loading=!1,this._error=o.message,e.a(2);case 5:this._params.applicationCredentialAddedCallback(i),this.closeDialog();case 6:return e.a(2)}}),e,this,[[2,4]])}))),function(e){return i.apply(this,arguments)})}],[{key:"styles",get:function(){return[g.nA,(0,h.AH)(O||(O=P`
        ha-dialog {
          --mdc-dialog-max-width: 500px;
          --dialog-z-index: 10;
        }
        .row {
          display: flex;
          padding: 8px 0;
        }
        ha-combo-box {
          display: block;
          margin-bottom: 24px;
        }
        ha-textfield {
          display: block;
          margin-bottom: 24px;
        }
        a {
          text-decoration: none;
        }
        a ha-svg-icon {
          --mdc-icon-size: 16px;
        }
        ha-markdown {
          margin-bottom: 16px;
        }
        ha-fade-in {
          display: flex;
          width: 100%;
          justify-content: center;
        }
      `))]}}]);var i,o,c}(h.WF);(0,c.__decorate)([(0,p.MZ)({attribute:!1})],z.prototype,"hass",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_loading",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_error",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_params",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_domain",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_manifest",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_name",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_description",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_clientId",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_clientSecret",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_domains",void 0),(0,c.__decorate)([(0,p.wk)()],z.prototype,"_config",void 0),z=(0,c.__decorate)([(0,p.EM)("dialog-add-application-credential")],z),o()}catch(q){o(q)}}))}}]);
//# sourceMappingURL=8451.05eefc20bc2d2e83.js.map