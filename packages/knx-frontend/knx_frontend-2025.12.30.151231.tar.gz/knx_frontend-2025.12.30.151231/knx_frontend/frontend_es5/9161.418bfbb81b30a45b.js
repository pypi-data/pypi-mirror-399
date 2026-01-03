"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9161"],{55124:function(e,t,o){o.d(t,{d:function(){return a}});var a=e=>e.stopPropagation()},87400:function(e,t,o){o.d(t,{l:function(){return a}});var a=(e,t,o,a,r)=>{var n=t[e.entity_id];return n?i(n,t,o,a,r):{entity:null,device:null,area:null,floor:null}},i=(e,t,o,a,i)=>{var r=t[e.entity_id],n=null==e?void 0:e.device_id,s=n?o[n]:void 0,l=(null==e?void 0:e.area_id)||(null==s?void 0:s.area_id),d=l?a[l]:void 0,c=null==d?void 0:d.floor_id;return{entity:r,device:s||null,area:d||null,floor:(c?i[c]:void 0)||null}}},74529:function(e,t,o){var a,i,r,n,s=o(44734),l=o(56038),d=o(69683),c=o(6454),h=o(25460),u=(o(28706),o(62826)),p=o(96229),v=o(26069),b=o(91735),_=o(42034),y=o(96196),m=o(77845),f=e=>e,g=function(e){function t(){var e;(0,s.A)(this,t);for(var o=arguments.length,a=new Array(o),i=0;i<o;i++)a[i]=arguments[i];return(e=(0,d.A)(this,t,[].concat(a))).filled=!1,e.active=!1,e}return(0,c.A)(t,e),(0,l.A)(t,[{key:"renderOutline",value:function(){return this.filled?(0,y.qy)(a||(a=f`<span class="filled"></span>`)):(0,h.A)(t,"renderOutline",this,3)([])}},{key:"getContainerClasses",value:function(){return Object.assign(Object.assign({},(0,h.A)(t,"getContainerClasses",this,3)([])),{},{active:this.active})}},{key:"renderPrimaryContent",value:function(){return(0,y.qy)(i||(i=f`
      <span class="leading icon" aria-hidden="true">
        ${0}
      </span>
      <span class="label">${0}</span>
      <span class="touch"></span>
      <span class="trailing leading icon" aria-hidden="true">
        ${0}
      </span>
    `),this.renderLeadingIcon(),this.label,this.renderTrailingIcon())}},{key:"renderTrailingIcon",value:function(){return(0,y.qy)(r||(r=f`<slot name="trailing-icon"></slot>`))}}])}(p.k);g.styles=[b.R,_.R,v.R,(0,y.AH)(n||(n=f`
      :host {
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-assist-chip-container-shape: var(
          --ha-assist-chip-container-shape,
          16px
        );
        --md-assist-chip-outline-color: var(--outline-color);
        --md-assist-chip-label-text-weight: 400;
      }
      /** Material 3 doesn't have a filled chip, so we have to make our own **/
      .filled {
        display: flex;
        pointer-events: none;
        border-radius: inherit;
        inset: 0;
        position: absolute;
        background-color: var(--ha-assist-chip-filled-container-color);
      }
      /** Set the size of mdc icons **/
      ::slotted([slot="icon"]),
      ::slotted([slot="trailing-icon"]) {
        display: flex;
        --mdc-icon-size: var(--md-input-chip-icon-size, 18px);
        font-size: var(--_label-text-size) !important;
      }

      .trailing.icon ::slotted(*),
      .trailing.icon svg {
        margin-inline-end: unset;
        margin-inline-start: var(--_icon-label-space);
      }
      ::before {
        background: var(--ha-assist-chip-container-color, transparent);
        opacity: var(--ha-assist-chip-container-opacity, 1);
      }
      :where(.active)::before {
        background: var(--ha-assist-chip-active-container-color);
        opacity: var(--ha-assist-chip-active-container-opacity);
      }
      .label {
        font-family: var(--ha-font-family-body);
      }
    `))],(0,u.__decorate)([(0,m.MZ)({type:Boolean,reflect:!0})],g.prototype,"filled",void 0),(0,u.__decorate)([(0,m.MZ)({type:Boolean})],g.prototype,"active",void 0),g=(0,u.__decorate)([(0,m.EM)("ha-assist-chip")],g)},25388:function(e,t,o){var a,i=o(56038),r=o(44734),n=o(69683),s=o(6454),l=o(62826),d=o(41216),c=o(78960),h=o(75640),u=o(91735),p=o(43826),v=o(96196),b=o(77845),_=function(e){function t(){return(0,r.A)(this,t),(0,n.A)(this,t,arguments)}return(0,s.A)(t,e),(0,i.A)(t)}(d.R);_.styles=[u.R,p.R,h.R,c.R,(0,v.AH)(a||(a=(e=>e)`
      :host {
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-input-chip-container-shape: 16px;
        --md-input-chip-outline-color: var(--outline-color);
        --md-input-chip-selected-container-color: rgba(
          var(--rgb-primary-text-color),
          0.15
        );
        --ha-input-chip-selected-container-opacity: 1;
        --md-input-chip-label-text-font: Roboto, sans-serif;
      }
      /** Set the size of mdc icons **/
      ::slotted([slot="icon"]) {
        display: flex;
        --mdc-icon-size: var(--md-input-chip-icon-size, 18px);
      }
      .selected::before {
        opacity: var(--ha-input-chip-selected-container-opacity);
      }
    `))],_=(0,l.__decorate)([(0,b.EM)("ha-input-chip")],_)},94123:function(e,t,o){o.a(e,(async function(e,t){try{var a=o(94741),i=o(61397),r=o(50264),n=o(44734),s=o(56038),l=o(69683),d=o(6454),c=(o(28706),o(2008),o(23792),o(62062),o(44114),o(34782),o(54554),o(18111),o(22489),o(61701),o(26099),o(27495),o(31415),o(17642),o(58004),o(33853),o(45876),o(32475),o(15024),o(31698),o(5746),o(62953),o(62826)),h=(o(1106),o(78648)),u=o(96196),p=o(77845),v=o(4937),b=o(22786),_=o(55376),y=o(92542),m=o(55124),f=o(87400),g=(o(74529),o(96294),o(25388),o(55179)),x=(o(56768),o(63801),e([g]));g=(x.then?(await x)():x)[0];var k,A,M,$,w,I,B,C,Z=e=>e,O=e=>(0,u.qy)(k||(k=Z`
  <ha-combo-box-item type="button">
    <span slot="headline">${0}</span>
    ${0}
  </ha-combo-box-item>
`),e.primary,e.secondary?(0,u.qy)(A||(A=Z`<span slot="supporting-text">${0}</span>`),e.secondary):u.s6),S=new Set(["entity","device","area","floor"]),V=new Set(["entity","device","area","floor"]),P=e=>"text"===e.type&&e.text?e.text:`___${e.type}___`,q=function(e){function t(){var e;(0,n.A)(this,t);for(var o=arguments.length,a=new Array(o),i=0;i<o;i++)a[i]=arguments[i];return(e=(0,l.A)(this,t,[].concat(a))).required=!1,e.disabled=!1,e._opened=!1,e._validTypes=(0,b.A)((t=>{var o=new Set(["text"]);if(!t)return o;var a=e.hass.states[t];if(!a)return o;o.add("entity");var i=(0,f.l)(a,e.hass.entities,e.hass.devices,e.hass.areas,e.hass.floors);return i.device&&o.add("device"),i.area&&o.add("area"),i.floor&&o.add("floor"),o})),e._getOptions=(0,b.A)((t=>{if(!t)return[];var o=e._validTypes(t);return["entity","device","area","floor"].map((a=>{var i=e.hass.states[t],r=o.has(a),n=e.hass.localize(`ui.components.entity.entity-name-picker.types.${a}`);return{primary:n,secondary:(i&&r?e.hass.formatEntityName(i,{type:a}):e.hass.localize(`ui.components.entity.entity-name-picker.types.${a}_missing`))||"-",field_label:n,value:P({type:a})}}))})),e._customNameOption=(0,b.A)((t=>({primary:e.hass.localize("ui.components.entity.entity-name-picker.custom_name"),secondary:`"${t}"`,field_label:t,value:P({type:"text",text:t})}))),e._formatItem=t=>"text"===t.type?`"${t.text}"`:S.has(t.type)?e.hass.localize(`ui.components.entity.entity-name-picker.types.${t.type}`):t.type,e._toItems=(0,b.A)((e=>"string"==typeof e?""===e?[]:[{type:"text",text:e}]:e?(0,_.e)(e):[])),e._toValue=(0,b.A)((e=>{if(0!==e.length){if(1===e.length){var t=e[0];return"text"===t.type?t.text:t}return e}})),e._filterSelectedOptions=(t,o)=>{var a=e._items,i=new Set(a.filter((e=>V.has(e.type))).map((e=>P(e))));return t.filter((e=>!i.has(e.value)||e.value===o))},e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"render",value:function(){var e=this._items,t=this._getOptions(this.entityId),o=this._validTypes(this.entityId);return(0,u.qy)(M||(M=Z`
      ${0}
      <div class="container">
        <ha-sortable
          no-style
          @item-moved=${0}
          .disabled=${0}
          handle-selector="button.primary.action"
          filter=".add"
        >
          <ha-chip-set>
            ${0}
            ${0}
          </ha-chip-set>
        </ha-sortable>

        <mwc-menu-surface
          .open=${0}
          @closed=${0}
          @opened=${0}
          @input=${0}
          .anchor=${0}
        >
          <ha-combo-box
            .hass=${0}
            .value=${0}
            .autofocus=${0}
            .disabled=${0}
            .required=${0}
            .items=${0}
            allow-custom-value
            item-id-path="value"
            item-value-path="value"
            item-label-path="field_label"
            .renderer=${0}
            @opened-changed=${0}
            @value-changed=${0}
            @filter-changed=${0}
          >
          </ha-combo-box>
        </mwc-menu-surface>
      </div>
      ${0}
    `),this.label?(0,u.qy)($||($=Z`<label>${0}</label>`),this.label):u.s6,this._moveItem,this.disabled,(0,v.u)(this._items,(e=>e),((e,t)=>{var a=this._formatItem(e),i=o.has(e.type);return(0,u.qy)(w||(w=Z`
                  <ha-input-chip
                    data-idx=${0}
                    @remove=${0}
                    @click=${0}
                    .label=${0}
                    .selected=${0}
                    .disabled=${0}
                    class=${0}
                  >
                    <ha-svg-icon
                      slot="icon"
                      .path=${0}
                    ></ha-svg-icon>
                    <span>${0}</span>
                  </ha-input-chip>
                `),t,this._removeItem,this._editItem,a,!this.disabled,this.disabled,i?"":"invalid","M21 11H3V9H21V11M21 13H3V15H21V13Z",a)})),this.disabled?u.s6:(0,u.qy)(I||(I=Z`
                  <ha-assist-chip
                    @click=${0}
                    .disabled=${0}
                    label=${0}
                    class="add"
                  >
                    <ha-svg-icon slot="icon" .path=${0}></ha-svg-icon>
                  </ha-assist-chip>
                `),this._addItem,this.disabled,this.hass.localize("ui.components.entity.entity-name-picker.add"),"M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"),this._opened,this._onClosed,this._onOpened,m.d,this._container,this.hass,"",this.autofocus,this.disabled,this.required&&!e.length,t,O,this._openedChanged,this._comboBoxValueChanged,this._filterChanged,this._renderHelper())}},{key:"_renderHelper",value:function(){return this.helper?(0,u.qy)(B||(B=Z`
          <ha-input-helper-text .disabled=${0}>
            ${0}
          </ha-input-helper-text>
        `),this.disabled,this.helper):u.s6}},{key:"_onClosed",value:function(e){e.stopPropagation(),this._opened=!1,this._editIndex=void 0}},{key:"_onOpened",value:(x=(0,r.A)((0,i.A)().m((function e(t){var o,a;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(this._opened){e.n=1;break}return e.a(2);case 1:return t.stopPropagation(),this._opened=!0,e.n=2,null===(o=this._comboBox)||void 0===o?void 0:o.focus();case 2:return e.n=3,null===(a=this._comboBox)||void 0===a?void 0:a.open();case 3:return e.a(2)}}),e,this)}))),function(e){return x.apply(this,arguments)})},{key:"_addItem",value:(g=(0,r.A)((0,i.A)().m((function e(t){return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:t.stopPropagation(),this._opened=!0;case 1:return e.a(2)}}),e,this)}))),function(e){return g.apply(this,arguments)})},{key:"_editItem",value:(p=(0,r.A)((0,i.A)().m((function e(t){var o;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:t.stopPropagation(),o=parseInt(t.currentTarget.dataset.idx,10),this._editIndex=o,this._opened=!0;case 1:return e.a(2)}}),e,this)}))),function(e){return p.apply(this,arguments)})},{key:"_items",get:function(){return this._toItems(this.value)}},{key:"_openedChanged",value:function(e){if(e.detail.value){var t=this._comboBox.items||[],o=null!=this._editIndex?this._items[this._editIndex]:void 0,a=o?P(o):"",i=this._filterSelectedOptions(t,a);"text"===(null==o?void 0:o.type)&&o.text&&i.push(this._customNameOption(o.text)),this._comboBox.filteredItems=i,this._comboBox.setInputValue(a)}else this._opened=!1,this._comboBox.setInputValue("")}},{key:"_filterChanged",value:function(e){var t=e.detail.value,o=(null==t?void 0:t.toLowerCase())||"",a=this._comboBox.items||[],i=null!=this._editIndex?this._items[this._editIndex]:void 0,r=i?P(i):"",n=this._filterSelectedOptions(a,r);if(o){var s={keys:["primary","secondary","value"],isCaseSensitive:!1,minMatchCharLength:Math.min(o.length,2),threshold:.2,ignoreDiacritics:!0};(n=new h.A(n,s).search(o).map((e=>e.item))).push(this._customNameOption(t)),this._comboBox.filteredItems=n}else this._comboBox.filteredItems=n}},{key:"_moveItem",value:(c=(0,r.A)((0,i.A)().m((function e(t){var o,a,r,n,s,l;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:return t.stopPropagation(),o=t.detail,a=o.oldIndex,r=o.newIndex,n=this._items,s=n.concat(),l=s.splice(a,1)[0],s.splice(r,0,l),this._setValue(s),e.n=1,this.updateComplete;case 1:this._filterChanged({detail:{value:""}});case 2:return e.a(2)}}),e,this)}))),function(e){return c.apply(this,arguments)})},{key:"_removeItem",value:(o=(0,r.A)((0,i.A)().m((function e(t){var o,r;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:return t.stopPropagation(),o=(0,a.A)(this._items),r=parseInt(t.target.dataset.idx,10),o.splice(r,1),this._setValue(o),e.n=1,this.updateComplete;case 1:this._filterChanged({detail:{value:""}});case 2:return e.a(2)}}),e,this)}))),function(e){return o.apply(this,arguments)})},{key:"_comboBoxValueChanged",value:function(e){e.stopPropagation();var t=e.detail.value;if(!this.disabled&&""!==t){var o=(e=>{if(e.startsWith("___")&&e.endsWith("___")){var t=e.slice(3,-3);if(S.has(t))return{type:t}}return{type:"text",text:e}})(t),i=(0,a.A)(this._items);null!=this._editIndex?i[this._editIndex]=o:i.push(o),this._setValue(i)}}},{key:"_setValue",value:function(e){var t=this._toValue(e);this.value=t,(0,y.r)(this,"value-changed",{value:t})}}]);var o,c,p,g,x}(u.WF);q.styles=(0,u.AH)(C||(C=Z`
    :host {
      position: relative;
      width: 100%;
    }

    .container {
      position: relative;
      background-color: var(--mdc-text-field-fill-color, whitesmoke);
      border-radius: var(--ha-border-radius-sm);
      border-end-end-radius: var(--ha-border-radius-square);
      border-end-start-radius: var(--ha-border-radius-square);
    }
    .container:after {
      display: block;
      content: "";
      position: absolute;
      pointer-events: none;
      bottom: 0;
      left: 0;
      right: 0;
      height: 1px;
      width: 100%;
      background-color: var(
        --mdc-text-field-idle-line-color,
        rgba(0, 0, 0, 0.42)
      );
      transform:
        height 180ms ease-in-out,
        background-color 180ms ease-in-out;
    }
    :host([disabled]) .container:after {
      background-color: var(
        --mdc-text-field-disabled-line-color,
        rgba(0, 0, 0, 0.42)
      );
    }
    .container:focus-within:after {
      height: 2px;
      background-color: var(--mdc-theme-primary);
    }

    label {
      display: block;
      margin: 0 0 var(--ha-space-2);
    }

    .add {
      order: 1;
    }

    mwc-menu-surface {
      --mdc-menu-min-width: 100%;
    }

    ha-chip-set {
      padding: var(--ha-space-2) var(--ha-space-2);
    }

    .invalid {
      text-decoration: line-through;
    }

    .sortable-fallback {
      display: none;
      opacity: 0;
    }

    .sortable-ghost {
      opacity: 0.4;
    }

    .sortable-drag {
      cursor: grabbing;
    }

    ha-input-helper-text {
      display: block;
      margin: var(--ha-space-2) 0 0;
    }
  `)),(0,c.__decorate)([(0,p.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,c.__decorate)([(0,p.MZ)({attribute:!1})],q.prototype,"entityId",void 0),(0,c.__decorate)([(0,p.MZ)({attribute:!1})],q.prototype,"value",void 0),(0,c.__decorate)([(0,p.MZ)()],q.prototype,"label",void 0),(0,c.__decorate)([(0,p.MZ)()],q.prototype,"helper",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean})],q.prototype,"required",void 0),(0,c.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],q.prototype,"disabled",void 0),(0,c.__decorate)([(0,p.P)(".container",!0)],q.prototype,"_container",void 0),(0,c.__decorate)([(0,p.P)("ha-combo-box",!0)],q.prototype,"_comboBox",void 0),(0,c.__decorate)([(0,p.wk)()],q.prototype,"_opened",void 0),q=(0,c.__decorate)([(0,p.EM)("ha-entity-name-picker")],q),t()}catch(L){t(L)}}))},11851:function(e,t,o){var a=o(44734),i=o(56038),r=o(69683),n=o(6454),s=o(25460),l=(o(28706),o(62826)),d=o(77845),c=function(e){function t(){var e;(0,a.A)(this,t);for(var o=arguments.length,i=new Array(o),n=0;n<o;n++)i[n]=arguments[n];return(e=(0,r.A)(this,t,[].concat(i))).forceBlankValue=!1,e}return(0,n.A)(t,e),(0,i.A)(t,[{key:"willUpdate",value:function(e){(0,s.A)(t,"willUpdate",this,3)([e]),(e.has("value")||e.has("forceBlankValue"))&&this.forceBlankValue&&this.value&&(this.value="")}}])}(o(78740).h);(0,l.__decorate)([(0,d.MZ)({type:Boolean,attribute:"force-blank-value"})],c.prototype,"forceBlankValue",void 0),c=(0,l.__decorate)([(0,d.EM)("ha-combo-box-textfield")],c)},55179:function(e,t,o){o.a(e,(async function(e,t){try{var a=o(61397),i=o(50264),r=o(44734),n=o(56038),s=o(69683),l=o(6454),d=o(25460),c=(o(28706),o(18111),o(7588),o(26099),o(23500),o(62826)),h=o(27680),u=o(34648),p=o(29289),v=o(96196),b=o(77845),_=o(32288),y=o(92542),m=(o(94343),o(11851),o(60733),o(56768),o(78740),e([u]));u=(m.then?(await m)():m)[0];var f,g,x,k,A,M,$,w=e=>e;(0,p.SF)("vaadin-combo-box-item",(0,v.AH)(f||(f=w`
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
  `)));var I=function(e){function t(){var e;(0,r.A)(this,t);for(var o=arguments.length,a=new Array(o),i=0;i<o;i++)a[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(a))).invalid=!1,e.icon=!1,e.allowCustomValue=!1,e.itemValuePath="value",e.itemLabelPath="label",e.disabled=!1,e.required=!1,e.opened=!1,e.hideClearIcon=!1,e.clearInitialValue=!1,e._forceBlankValue=!1,e._defaultRowRenderer=t=>(0,v.qy)(g||(g=w`
    <ha-combo-box-item type="button">
      ${0}
    </ha-combo-box-item>
  `),e.itemLabelPath?t[e.itemLabelPath]:t),e}return(0,l.A)(t,e),(0,n.A)(t,[{key:"open",value:(c=(0,i.A)((0,a.A)().m((function e(){var t;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:null===(t=this._comboBox)||void 0===t||t.open();case 2:return e.a(2)}}),e,this)}))),function(){return c.apply(this,arguments)})},{key:"focus",value:(o=(0,i.A)((0,a.A)().m((function e(){var t,o;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:return e.n=2,null===(t=this._inputElement)||void 0===t?void 0:t.updateComplete;case 2:null===(o=this._inputElement)||void 0===o||o.focus();case 3:return e.a(2)}}),e,this)}))),function(){return o.apply(this,arguments)})},{key:"disconnectedCallback",value:function(){(0,d.A)(t,"disconnectedCallback",this,3)([]),this._overlayMutationObserver&&(this._overlayMutationObserver.disconnect(),this._overlayMutationObserver=void 0),this._bodyMutationObserver&&(this._bodyMutationObserver.disconnect(),this._bodyMutationObserver=void 0)}},{key:"selectedItem",get:function(){return this._comboBox.selectedItem}},{key:"setInputValue",value:function(e){this._comboBox.value=e}},{key:"setTextFieldValue",value:function(e){this._inputElement.value=e}},{key:"render",value:function(){var e;return(0,v.qy)(x||(x=w`
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
    `),this.itemValuePath,this.itemIdPath,this.itemLabelPath,this.items,this.value||"",this.filteredItems,this.dataProvider,this.allowCustomValue,this.disabled,this.required,(0,h.d)(this.renderer||this._defaultRowRenderer),this._openedChanged,this._filterChanged,this._valueChanged,(0,_.J)(this.label),(0,_.J)(this.placeholder),this.disabled,this.required,(0,_.J)(this.validationMessage),this.errorMessage,!1,(0,v.qy)(k||(k=w`<div
            style="width: 28px;"
            role="none presentation"
          ></div>`)),this.icon,this.invalid,this._forceBlankValue,this.value&&!this.hideClearIcon?(0,v.qy)(A||(A=w`<ha-svg-icon
              role="button"
              tabindex="-1"
              aria-label=${0}
              class=${0}
              .path=${0}
              ?disabled=${0}
              @click=${0}
            ></ha-svg-icon>`),(0,_.J)(null===(e=this.hass)||void 0===e?void 0:e.localize("ui.common.clear")),"clear-button "+(this.label?"":"no-label"),"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",this.disabled,this._clearValue):"",(0,_.J)(this.label),this.opened?"true":"false","toggle-button "+(this.label?"":"no-label"),this.opened?"M7,15L12,10L17,15H7Z":"M7,10L12,15L17,10H7Z",this.disabled,this._toggleOpen,this._renderHelper())}},{key:"_renderHelper",value:function(){return this.helper?(0,v.qy)(M||(M=w`<ha-input-helper-text .disabled=${0}
          >${0}</ha-input-helper-text
        >`),this.disabled,this.helper):""}},{key:"_clearValue",value:function(e){e.stopPropagation(),(0,y.r)(this,"value-changed",{value:void 0})}},{key:"_toggleOpen",value:function(e){var t,o;this.opened?(null===(t=this._comboBox)||void 0===t||t.close(),e.stopPropagation()):null===(o=this._comboBox)||void 0===o||o.inputElement.focus()}},{key:"_openedChanged",value:function(e){e.stopPropagation();var t=e.detail.value;if(setTimeout((()=>{this.opened=t,(0,y.r)(this,"opened-changed",{value:e.detail.value})}),0),this.clearInitialValue&&(this.setTextFieldValue(""),t?setTimeout((()=>{this._forceBlankValue=!1}),100):this._forceBlankValue=!0),t){var o=document.querySelector("vaadin-combo-box-overlay");o&&this._removeInert(o),this._observeBody()}else{var a;null===(a=this._bodyMutationObserver)||void 0===a||a.disconnect(),this._bodyMutationObserver=void 0}}},{key:"_observeBody",value:function(){"MutationObserver"in window&&!this._bodyMutationObserver&&(this._bodyMutationObserver=new MutationObserver((e=>{e.forEach((e=>{e.addedNodes.forEach((e=>{"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&this._removeInert(e)})),e.removedNodes.forEach((e=>{var t;"VAADIN-COMBO-BOX-OVERLAY"===e.nodeName&&(null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),this._overlayMutationObserver=void 0)}))}))})),this._bodyMutationObserver.observe(document.body,{childList:!0}))}},{key:"_removeInert",value:function(e){var t;if(e.inert)return e.inert=!1,null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),void(this._overlayMutationObserver=void 0);"MutationObserver"in window&&!this._overlayMutationObserver&&(this._overlayMutationObserver=new MutationObserver((e=>{e.forEach((e=>{if("inert"===e.attributeName){var t,o=e.target;if(o.inert)null===(t=this._overlayMutationObserver)||void 0===t||t.disconnect(),this._overlayMutationObserver=void 0,o.inert=!1}}))})),this._overlayMutationObserver.observe(e,{attributes:!0}))}},{key:"_filterChanged",value:function(e){e.stopPropagation(),(0,y.r)(this,"filter-changed",{value:e.detail.value})}},{key:"_valueChanged",value:function(e){if(e.stopPropagation(),this.allowCustomValue||(this._comboBox._closeOnBlurIsPrevented=!0),this.opened){var t=e.detail.value;t!==this.value&&(0,y.r)(this,"value-changed",{value:t||void 0})}}}]);var o,c}(v.WF);I.styles=(0,v.AH)($||($=w`
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
  `)),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],I.prototype,"hass",void 0),(0,c.__decorate)([(0,b.MZ)()],I.prototype,"label",void 0),(0,c.__decorate)([(0,b.MZ)()],I.prototype,"value",void 0),(0,c.__decorate)([(0,b.MZ)()],I.prototype,"placeholder",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],I.prototype,"validationMessage",void 0),(0,c.__decorate)([(0,b.MZ)()],I.prototype,"helper",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"error-message"})],I.prototype,"errorMessage",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],I.prototype,"invalid",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],I.prototype,"icon",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],I.prototype,"items",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],I.prototype,"filteredItems",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],I.prototype,"dataProvider",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"allow-custom-value",type:Boolean})],I.prototype,"allowCustomValue",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"item-value-path"})],I.prototype,"itemValuePath",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"item-label-path"})],I.prototype,"itemLabelPath",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:"item-id-path"})],I.prototype,"itemIdPath",void 0),(0,c.__decorate)([(0,b.MZ)({attribute:!1})],I.prototype,"renderer",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],I.prototype,"disabled",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],I.prototype,"required",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean,reflect:!0})],I.prototype,"opened",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean,attribute:"hide-clear-icon"})],I.prototype,"hideClearIcon",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean,attribute:"clear-initial-value"})],I.prototype,"clearInitialValue",void 0),(0,c.__decorate)([(0,b.P)("vaadin-combo-box-light",!0)],I.prototype,"_comboBox",void 0),(0,c.__decorate)([(0,b.P)("ha-combo-box-textfield",!0)],I.prototype,"_inputElement",void 0),(0,c.__decorate)([(0,b.wk)({type:Boolean})],I.prototype,"_forceBlankValue",void 0),I=(0,c.__decorate)([(0,b.EM)("ha-combo-box")],I),t()}catch(B){t(B)}}))},90176:function(e,t,o){o.a(e,(async function(e,a){try{o.r(t),o.d(t,{HaSelectorEntityName:function(){return _}});var i=o(44734),r=o(56038),n=o(69683),s=o(6454),l=(o(28706),o(62826)),d=o(96196),c=o(77845),h=o(10085),u=o(94123),p=e([u]);u=(p.then?(await p)():p)[0];var v,b=e=>e,_=function(e){function t(){var e;(0,i.A)(this,t);for(var o=arguments.length,a=new Array(o),r=0;r<o;r++)a[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(a))).disabled=!1,e.required=!0,e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"render",value:function(){var e,t,o,a,i=null!==(e=this.value)&&void 0!==e?e:null===(t=this.selector.entity_name)||void 0===t?void 0:t.default_name;return(0,d.qy)(v||(v=b`
      <ha-entity-name-picker
        .hass=${0}
        .entityId=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
      ></ha-entity-name-picker>
    `),this.hass,(null===(o=this.selector.entity_name)||void 0===o?void 0:o.entity_id)||(null===(a=this.context)||void 0===a?void 0:a.entity),i,this.label,this.helper,this.disabled,this.required)}}])}((0,h.E)(d.WF));(0,l.__decorate)([(0,c.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],_.prototype,"selector",void 0),(0,l.__decorate)([(0,c.MZ)()],_.prototype,"value",void 0),(0,l.__decorate)([(0,c.MZ)()],_.prototype,"label",void 0),(0,l.__decorate)([(0,c.MZ)()],_.prototype,"helper",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],_.prototype,"context",void 0),_=(0,l.__decorate)([(0,c.EM)("ha-selector-entity_name")],_),a()}catch(y){a(y)}}))},63801:function(e,t,o){var a,i=o(61397),r=o(50264),n=o(44734),s=o(56038),l=o(75864),d=o(69683),c=o(6454),h=o(25460),u=(o(28706),o(2008),o(23792),o(18111),o(22489),o(26099),o(3362),o(46058),o(62953),o(62826)),p=o(96196),v=o(77845),b=o(92542),_=e=>e,y=function(e){function t(){var e;(0,n.A)(this,t);for(var o=arguments.length,a=new Array(o),s=0;s<o;s++)a[s]=arguments[s];return(e=(0,d.A)(this,t,[].concat(a))).disabled=!1,e.noStyle=!1,e.invertSwap=!1,e.rollback=!0,e._shouldBeDestroy=!1,e._handleUpdate=t=>{(0,b.r)((0,l.A)(e),"item-moved",{newIndex:t.newIndex,oldIndex:t.oldIndex})},e._handleAdd=t=>{(0,b.r)((0,l.A)(e),"item-added",{index:t.newIndex,data:t.item.sortableData,item:t.item})},e._handleRemove=t=>{(0,b.r)((0,l.A)(e),"item-removed",{index:t.oldIndex})},e._handleEnd=function(){var t=(0,r.A)((0,i.A)().m((function t(o){return(0,i.A)().w((function(t){for(;;)switch(t.n){case 0:(0,b.r)((0,l.A)(e),"drag-end"),e.rollback&&o.item.placeholder&&(o.item.placeholder.replaceWith(o.item),delete o.item.placeholder);case 1:return t.a(2)}}),t)})));return function(e){return t.apply(this,arguments)}}(),e._handleStart=()=>{(0,b.r)((0,l.A)(e),"drag-start")},e._handleChoose=t=>{e.rollback&&(t.item.placeholder=document.createComment("sort-placeholder"),t.item.after(t.item.placeholder))},e}return(0,c.A)(t,e),(0,s.A)(t,[{key:"updated",value:function(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}},{key:"disconnectedCallback",value:function(){(0,h.A)(t,"disconnectedCallback",this,3)([]),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}},{key:"connectedCallback",value:function(){(0,h.A)(t,"connectedCallback",this,3)([]),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}},{key:"createRenderRoot",value:function(){return this}},{key:"render",value:function(){return this.noStyle?p.s6:(0,p.qy)(a||(a=_`
      <style>
        .sortable-fallback {
          display: none !important;
        }

        .sortable-ghost {
          box-shadow: 0 0 0 2px var(--primary-color);
          background: rgba(var(--rgb-primary-color), 0.25);
          border-radius: var(--ha-border-radius-sm);
          opacity: 0.4;
        }

        .sortable-drag {
          border-radius: var(--ha-border-radius-sm);
          opacity: 1;
          background: var(--card-background-color);
          box-shadow: 0px 4px 8px 3px #00000026;
          cursor: grabbing;
        }
      </style>
    `))}},{key:"_createSortable",value:(u=(0,r.A)((0,i.A)().m((function e(){var t,a,r;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this._sortable){e.n=1;break}return e.a(2);case 1:if(t=this.children[0]){e.n=2;break}return e.a(2);case 2:return e.n=3,Promise.all([o.e("5283"),o.e("1387")]).then(o.bind(o,38214));case 3:a=e.v.default,r=Object.assign(Object.assign({scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150},this.options),{},{onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove}),this.draggableSelector&&(r.draggable=this.draggableSelector),this.handleSelector&&(r.handle=this.handleSelector),void 0!==this.invertSwap&&(r.invertSwap=this.invertSwap),this.group&&(r.group=this.group),this.filter&&(r.filter=this.filter),this._sortable=new a(t,r);case 4:return e.a(2)}}),e,this)}))),function(){return u.apply(this,arguments)})},{key:"_destroySortable",value:function(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}}]);var u}(p.WF);(0,u.__decorate)([(0,v.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean,attribute:"no-style"})],y.prototype,"noStyle",void 0),(0,u.__decorate)([(0,v.MZ)({type:String,attribute:"draggable-selector"})],y.prototype,"draggableSelector",void 0),(0,u.__decorate)([(0,v.MZ)({type:String,attribute:"handle-selector"})],y.prototype,"handleSelector",void 0),(0,u.__decorate)([(0,v.MZ)({type:String,attribute:"filter"})],y.prototype,"filter",void 0),(0,u.__decorate)([(0,v.MZ)({type:String})],y.prototype,"group",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean,attribute:"invert-swap"})],y.prototype,"invertSwap",void 0),(0,u.__decorate)([(0,v.MZ)({attribute:!1})],y.prototype,"options",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean})],y.prototype,"rollback",void 0),y=(0,u.__decorate)([(0,v.EM)("ha-sortable")],y)},10085:function(e,t,o){o.d(t,{E:function(){return h}});var a=o(31432),i=o(44734),r=o(56038),n=o(69683),s=o(25460),l=o(6454),d=(o(74423),o(23792),o(18111),o(13579),o(26099),o(3362),o(62953),o(62826)),c=o(77845),h=e=>{var t=function(e){function t(){return(0,i.A)(this,t),(0,n.A)(this,t,arguments)}return(0,l.A)(t,e),(0,r.A)(t,[{key:"connectedCallback",value:function(){(0,s.A)(t,"connectedCallback",this,3)([]),this._checkSubscribed()}},{key:"disconnectedCallback",value:function(){if((0,s.A)(t,"disconnectedCallback",this,3)([]),this.__unsubs){for(;this.__unsubs.length;){var e=this.__unsubs.pop();e instanceof Promise?e.then((e=>e())):e()}this.__unsubs=void 0}}},{key:"updated",value:function(e){if((0,s.A)(t,"updated",this,3)([e]),e.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps){var o,i=(0,a.A)(e.keys());try{for(i.s();!(o=i.n()).done;){var r=o.value;if(this.hassSubscribeRequiredHostProps.includes(r))return void this._checkSubscribed()}}catch(n){i.e(n)}finally{i.f()}}}},{key:"hassSubscribe",value:function(){return[]}},{key:"_checkSubscribed",value:function(){var e;void 0!==this.__unsubs||!this.isConnected||void 0===this.hass||null!==(e=this.hassSubscribeRequiredHostProps)&&void 0!==e&&e.some((e=>void 0===this[e]))||(this.__unsubs=this.hassSubscribe())}}])}(e);return(0,d.__decorate)([(0,c.MZ)({attribute:!1})],t.prototype,"hass",void 0),t}}}]);
//# sourceMappingURL=9161.418bfbb81b30a45b.js.map