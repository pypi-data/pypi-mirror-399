"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2007"],{81089:function(e,t,o){o.d(t,{n:function(){return a}});o(27495),o(25440);var a=e=>e.replace(/^_*(.)|_+(.)/g,((e,t,o)=>t?t.toUpperCase():" "+o.toUpperCase()))},11851:function(e,t,o){var a=o(44734),i=o(56038),r=o(69683),n=o(6454),l=o(25460),s=(o(28706),o(62826)),d=o(77845),c=function(e){function t(){var e;(0,a.A)(this,t);for(var o=arguments.length,i=new Array(o),n=0;n<o;n++)i[n]=arguments[n];return(e=(0,r.A)(this,t,[].concat(i))).forceBlankValue=!1,e}return(0,n.A)(t,e),(0,i.A)(t,[{key:"willUpdate",value:function(e){(0,l.A)(t,"willUpdate",this,3)([e]),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}}])}(o(78740).h);(0,s.__decorate)([(0,d.MZ)({type:Boolean,attribute:"force-blank-value"})],c.prototype,"forceBlankValue",void 0),c=(0,s.__decorate)([(0,d.EM)("ha-combo-box-textfield")],c)},55179:function(e,t,o){o.a(e,(async function(e,t){try{var a=o(61397),i=o(50264),r=o(44734),n=o(56038),l=o(69683),s=o(6454),d=o(25460),c=(o(28706),o(18111),o(7588),o(26099),o(23500),o(62826)),u=o(27680),h=o(34648),v=o(29289),p=o(96196),b=o(77845),_=o(32288),m=o(92542),f=(o(94343),o(11851),o(60733),o(56768),o(78740),e([h]));h=(f.then?(await f)():f)[0];var y,g,x,M,k,$,w,A=e=>e;(0,v.SF)("vaadin-combo-box-item",(0,p.AH)(y||(y=A`
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
  `)));var B=function(e){function t(){var e;(0,r.A)(this,t);for(var o=arguments.length,a=new Array(o),i=0;i<o;i++)a[i]=arguments[i];return(e=(0,l.A)(this,t,[].concat(a))).invalid=!1,e.icon=!1,e.allowCustomValue=!1,e.itemValuePath="value",e.itemLabelPath="label",e.disabled=!1,e.required=!1,e.opened=!1,e.hideClearIcon=!1,e.clearInitialValue=!1,e._forceBlankValue=!1,e._defaultRowRenderer=t=>(0,p.qy)(g||(g=A`
    <ha-combo-box-item type="button">
      ${0}
    </ha-combo-box-item>
  `),e.itemLabelPath?t[e.itemLabelPath]:t),e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"open",value:(c=(0,i.A)((0,a.A)().m((function e(){var t;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:null===(t=this._comboBox)||void 0===t||t.open();case 2:return e.a(2)}}),e,this)}))),function(){return c.apply(this,arguments)})},{key:"focus",value:(o=(0,i.A)((0,a.A)().m((function e(){var t,o;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:return e.n=2,null===(t=this._inputElement)||void 0===t?void 0:t.updateComplete;case 2:null===(o=this._inputElement)||void 0===o||o.focus();case 3:return e.a(2)}}),e,this)}))),function(){return o.apply(this,arguments)})},{key:"disconnectedCallback",value:function(){(0,d.A)(t,"disconnectedCallback",this,3)([]),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}},{key:"selectedItem",get:function(){return this._comboBox.selectedItem}},{key:"setInputValue",value:function(e){this._comboBox.value=e}},{key:"setTextFieldValue",value:function(e){this._inputElement.value=e}},{key:"render",value:function(){var e;return(0,p.qy)(x||(x=A`
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
    `),this.itemValuePath,this.itemIdPath,this.itemLabelPath,this.items,this.value||"",this.filteredItems,this.dataProvider,this.allowCustomValue,this.disabled,this.required,(0,u.d)(this.renderer||this._defaultRowRenderer),this._openedChanged,this._filterChanged,this._valueChanged,(0,_.J)(this.label),(0,_.J)(this.placeholder),this.disabled,this.required,(0,_.J)(this.validationMessage),this.errorMessage,!1,(0,p.qy)(M||(M=A`<div
            style="width: 28px;"
            role="none presentation"
          ></div>`)),this.icon,this.invalid,this._forceBlankValue,this.value&&!this.hideClearIcon?(0,p.qy)(k||(k=A`<ha-svg-icon
              role="button"
              tabindex="-1"
              aria-label=${0}
              class=${0}
              .path=${0}
              ?disabled=${0}
              @click=${0}
            ></ha-svg-icon>`),(0,_.J)(null===(e=this.hass)||void 0===e?void 0:e.localize("ui.common.clear")),"clear-button "+(this.label?"":"no-label"),"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",this.disabled,this._clearValue):"",(0,_.J)(this.label),this.opened?"true":"false","toggle-button "+(this.label?"":"no-label"),this.opened?"M7,15L12,10L17,15H7Z":"M7,10L12,15L17,10H7Z",this.disabled,this._toggleOpen,this._renderHelper())}},{key:"_renderHelper",value:function(){return this.helper?(0,p.qy)($||($=A`<ha-input-helper-text .disabled=${0}
          >${0}</ha-input-helper-text
        >`),this.disabled,this.helper):""}},{key:"_clearValue",value:function(e){e.stopPropagation(),(0,m.r)(this,"value-changed",{value:void 0})}},{key:"_toggleOpen",value:function(e){var t,o;this.opened?(null===(t=this._comboBox)||void 0===t||t.close(),e.stopPropagation()):null===(o=this._comboBox)||void 0===o||o.inputElement.focus()}},{key:"_openedChanged",value:function(e){e.stopPropagation();var t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,m.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){var o=document.querySelector("vaadin-combo-box-overlay");o&&this._removeInert(o),this._observeBody()}else{var a;null===(a=this._bodyMutationObserver)||void 0===a||a.disconnect(),this._bodyMutationObserver=void 0}}},{key:"_observeBody",value:function(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{var t;"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}},{key:"_removeInert",value:function(e){var t;if(e.inert)return e.inert=!1,null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){var t,o=e.target;if(o.inert)null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),this._overlayMutationObserver=void 0,o.inert=!1}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}},{key:"_filterChanged",value:function(e){e.stopPropagation(),(0,m.r)(this,"filter-changed",{value:e.detail.value})}},{key:"_valueChanged",value:function(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),this.opened){var t=e.detail.value;t!==this.value&&(0,m.r)(this,"value-changed",{value:t||void 0})}}}]);var o,c}(p.WF);B.styles=(0,p.AH)(w||(w=A`
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
  `)),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],B.prototype,"hass",void 0),(0,c.__decorate)([(0,b.MZ)()],B.prototype,"label",void 0),(0,c.__decorate)([(0,b.MZ)()],B.prototype,"value",void 0),(0,c.__decorate)([(0,b.MZ)()],B.prototype,"placeholder",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],B.prototype,"validationMessage",void 0),(0,c.__decorate)([(0,b.MZ)()],B.prototype,"helper",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"error-message"})],B.prototype,"errorMessage",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],B.prototype,"invalid",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],B.prototype,"icon",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],B.prototype,"items",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],B.prototype,"filteredItems",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],B.prototype,"dataProvider",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"allow-custom-value",type:Boolean})],B.prototype,"allowCustomValue",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"item-value-path"})],B.prototype,"itemValuePath",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"item-label-path"})],B.prototype,"itemLabelPath",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"item-id-path"})],B.prototype,"itemIdPath",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],B.prototype,"renderer",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],B.prototype,"disabled",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],B.prototype,"required",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean,reflect:!0})],B.prototype,"opened",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean,attribute:"hide-clear-icon"})],B.prototype,"hideClearIcon",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean,attribute:"clear-initial-value"})],B.prototype,"clearInitialValue",void 0),(0,c.__decorate)([(0,b.P)("vaadin-combo-box-light",!0)],B.prototype,"_comboBox",void 0),(0,c.__decorate)([(0,b.P)("ha-combo-box-textfield",!0)],B.prototype,"_inputElement",void 0),(0,c.__decorate)([(0,b.wk)({type:Boolean})],B.prototype,"_forceBlankValue",void 0),B=(0,c.__decorate)([(0,b.EM)("ha-combo-box")],B),t()}catch(I){t(I)}}))},17210:function(e,t,o){o.a(e,(async function(e,t){try{var a=o(3164),i=o(31432),r=o(78261),n=o(61397),l=o(50264),s=o(44734),d=o(56038),c=o(69683),u=o(6454),h=(o(28706),o(2008),o(74423),o(23792),o(62062),o(44114),o(18111),o(22489),o(7588),o(61701),o(36033),o(5506),o(26099),o(3362),o(23500),o(62953),o(62826)),v=o(96196),p=o(77845),b=o(92542),_=o(81089),m=o(80559),f=o(11129),y=o(55179),g=(o(94343),o(22598),e([y]));y=(g.then?(await g)():g)[0];var x,M,k,$,w=e=>e,A=[],B=e=>(0,v.qy)(x||(x=w`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    <span slot="headline">${0}</span>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.title||e.path,e.title?(0,v.qy)(M||(M=w`<span slot="supporting-text">${0}</span>`),e.path):v.s6),I=(e,t,o)=>{var a,i,r;return{path:`/${e}/${null!==(a=t.path)&&void 0!==a?a:o}`,icon:null!==(i=t.icon)&&void 0!==i?i:"mdi:view-compact",title:null!==(r=t.title)&&void 0!==r?r:t.path?(0,_.n)(t.path):`${o}`}},O=(e,t)=>({path:`/${t.url_path}`,icon:(0,f.Q)(t)||"mdi:view-dashboard",title:(0,f.hL)(e,t)||""}),C=function(e){function t(){var e;(0,s.A)(this,t);for(var o=arguments.length,a=new Array(o),i=0;i<o;i++)a[i]=arguments[i];return(e=(0,c.A)(this,t,[].concat(a))).disabled=!1,e.required=!1,e._opened=!1,e.navigationItemsLoaded=!1,e.navigationItems=A,e}return(0,u.A)(t,e),(0,d.A)(t,[{key:"render",value:function(){return(0,v.qy)(k||(k=w`
      <ha-combo-box
        .hass=${0}
        item-value-path="path"
        item-label-path="path"
        .value=${0}
        allow-custom-value
        .filteredItems=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .renderer=${0}
        @opened-changed=${0}
        @value-changed=${0}
        @filter-changed=${0}
      >
      </ha-combo-box>
    `),this.hass,this._value,this.navigationItems,this.label,this.helper,this.disabled,this.required,B,this._openedChanged,this._valueChanged,this._filterChanged)}},{key:"_openedChanged",value:(h=(0,l.A)((0,n.A)().m((function e(t){return(0,n.A)().w((function(e){for(;;)switch(e.n){case 0:this._opened=t.detail.value,this._opened&&!this.navigationItemsLoaded&&this._loadNavigationItems();case 1:return e.a(2)}}),e,this)}))),function(e){return h.apply(this,arguments)})},{key:"_loadNavigationItems",value:(o=(0,l.A)((0,n.A)().m((function e(){var t,o,l,s,d,c,u,h,v=this;return(0,n.A)().w((function(e){for(;;)switch(e.p=e.n){case 0:return this.navigationItemsLoaded=!0,t=Object.entries(this.hass.panels).map((e=>{var t=(0,r.A)(e,2),o=t[0],a=t[1];return Object.assign({id:o},a)})),o=t.filter((e=>"lovelace"===e.component_name)),e.n=1,Promise.all(o.map((e=>(0,m.Dz)(this.hass.connection,"lovelace"===e.url_path?null:e.url_path,!0).then((t=>[e.id,t])).catch((t=>[e.id,void 0])))));case 1:l=e.v,s=new Map(l),this.navigationItems=[],d=(0,i.A)(t),e.p=2,u=(0,n.A)().m((function e(){var t,o;return(0,n.A)().w((function(e){for(;;)switch(e.n){case 0:if(t=c.value,v.navigationItems.push(O(v.hass,t)),(o=s.get(t.id))&&"views"in o){e.n=1;break}return e.a(2,1);case 1:o.views.forEach(((e,o)=>v.navigationItems.push(I(t.url_path,e,o))));case 2:return e.a(2)}}),e)})),d.s();case 3:if((c=d.n()).done){e.n=6;break}return e.d((0,a.A)(u()),4);case 4:if(!e.v){e.n=5;break}return e.a(3,5);case 5:e.n=3;break;case 6:e.n=8;break;case 7:e.p=7,h=e.v,d.e(h);case 8:return e.p=8,d.f(),e.f(8);case 9:this.comboBox.filteredItems=this.navigationItems;case 10:return e.a(2)}}),e,this,[[2,7,8,9]])}))),function(){return o.apply(this,arguments)})},{key:"shouldUpdate",value:function(e){return!this._opened||e.has("_opened")}},{key:"_valueChanged",value:function(e){e.stopPropagation(),this._setValue(e.detail.value)}},{key:"_setValue",value:function(e){this.value=e,(0,b.r)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}},{key:"_filterChanged",value:function(e){var t=e.detail.value.toLowerCase();if(t.length>=2){var o=[];this.navigationItems.forEach((e=>{(e.path.toLowerCase().includes(t)||e.title.toLowerCase().includes(t))&&o.push(e)})),o.length>0?this.comboBox.filteredItems=o:this.comboBox.filteredItems=[]}else this.comboBox.filteredItems=this.navigationItems}},{key:"_value",get:function(){return this.value||""}}]);var o,h}(v.WF);C.styles=(0,v.AH)($||($=w`
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
  `)),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],C.prototype,"hass",void 0),(0,h.__decorate)([(0,p.MZ)()],C.prototype,"label",void 0),(0,h.__decorate)([(0,p.MZ)()],C.prototype,"value",void 0),(0,h.__decorate)([(0,p.MZ)()],C.prototype,"helper",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],C.prototype,"disabled",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],C.prototype,"required",void 0),(0,h.__decorate)([(0,p.wk)()],C.prototype,"_opened",void 0),(0,h.__decorate)([(0,p.P)("ha-combo-box",!0)],C.prototype,"comboBox",void 0),C=(0,h.__decorate)([(0,p.EM)("ha-navigation-picker")],C),t()}catch(L){t(L)}}))},80559:function(e,t,o){o.d(t,{Dz:function(){return a}});var a=(e,t,o)=>e.sendMessagePromise({type:"lovelace/config",url_path:t,force:o})},11129:function(e,t,o){o.d(t,{Q:function(){return i},hL:function(){return a}});o(50113),o(18111),o(20116),o(26099),o(16034),o(58335);var a=(e,t)=>{var o=(e=>"lovelace"===e.url_path?"panel.states":"profile"===e.url_path?"panel.profile":`panel.${e.title}`)(t);return e.localize(o)||t.title||void 0},i=e=>{if(!e.icon)switch(e.component_name){case"profile":return"mdi:account";case"lovelace":return"mdi:view-dashboard"}return e.icon||void 0}}}]);
//# sourceMappingURL=2007.ff7273c5412ef75a.js.map