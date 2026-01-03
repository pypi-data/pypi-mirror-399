/*! For license information please see 637.6a50440918720b50.js.LICENSE.txt */
export const __webpack_id__="637";export const __webpack_ids__=["637"];export const __webpack_modules__={55124:function(t,e,i){i.d(e,{d:()=>o});const o=t=>t.stopPropagation()},87400:function(t,e,i){i.d(e,{l:()=>o});const o=(t,e,i,o,s)=>{const r=e[t.entity_id];return r?a(r,e,i,o,s):{entity:null,device:null,area:null,floor:null}},a=(t,e,i,o,a)=>{const s=e[t.entity_id],r=t?.device_id,n=r?i[r]:void 0,l=t?.area_id||n?.area_id,d=l?o[l]:void 0,c=d?.floor_id;return{entity:s,device:n||null,area:d||null,floor:(c?a[c]:void 0)||null}}},31747:function(t,e,i){i.a(t,(async function(t,o){try{i.d(e,{T:()=>n});var a=i(22),s=i(22786),r=t([a]);a=(r.then?(await r)():r)[0];const n=(t,e)=>{try{return l(e)?.of(t)??t}catch{return t}},l=(0,s.A)((t=>new Intl.DisplayNames(t.language,{type:"language",fallback:"code"})));o()}catch(n){o(n)}}))},72125:function(t,e,i){i.d(e,{F:()=>a,r:()=>s});const o=/{%|{{/,a=t=>o.test(t),s=t=>{if(!t)return!1;if("string"==typeof t)return a(t);if("object"==typeof t){return(Array.isArray(t)?t:Object.values(t)).some((t=>t&&s(t)))}return!1}},56528:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(62826),a=i(96196),s=i(77845),r=i(92542),n=i(55124),l=i(31747),d=i(45369),c=(i(56565),i(69869),t([l]));l=(c.then?(await c)():c)[0];const h="preferred",p="last_used";class u extends a.WF{get _default(){return this.includeLastUsed?p:h}render(){if(!this._pipelines)return a.s6;const t=this.value??this._default;return a.qy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.pipeline-picker.pipeline")}
        .value=${t}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${n.d}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.includeLastUsed?a.qy`
              <ha-list-item .value=${p}>
                ${this.hass.localize("ui.components.pipeline-picker.last_used")}
              </ha-list-item>
            `:null}
        <ha-list-item .value=${h}>
          ${this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:this._pipelines.find((t=>t.id===this._preferredPipeline))?.name})}
        </ha-list-item>
        ${this._pipelines.map((t=>a.qy`<ha-list-item .value=${t.id}>
              ${t.name}
              (${(0,l.T)(t.language,this.hass.locale)})
            </ha-list-item>`))}
      </ha-select>
    `}firstUpdated(t){super.firstUpdated(t),(0,d.nx)(this.hass).then((t=>{this._pipelines=t.pipelines,this._preferredPipeline=t.preferred_pipeline}))}_changed(t){const e=t.target;!this.hass||""===e.value||e.value===this.value||void 0===this.value&&e.value===this._default||(this.value=e.value===this._default?void 0:e.value,(0,r.r)(this,"value-changed",{value:this.value}))}constructor(...t){super(...t),this.disabled=!1,this.required=!1,this.includeLastUsed=!1,this._preferredPipeline=null}}u.styles=a.AH`
    ha-select {
      width: 100%;
    }
  `,(0,o.__decorate)([(0,s.MZ)()],u.prototype,"value",void 0),(0,o.__decorate)([(0,s.MZ)()],u.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],u.prototype,"includeLastUsed",void 0),(0,o.__decorate)([(0,s.wk)()],u.prototype,"_pipelines",void 0),(0,o.__decorate)([(0,s.wk)()],u.prototype,"_preferredPipeline",void 0),u=(0,o.__decorate)([(0,s.EM)("ha-assist-pipeline-picker")],u),e()}catch(h){e(h)}}))},70524:function(t,e,i){var o=i(62826),a=i(69162),s=i(47191),r=i(96196),n=i(77845);class l extends a.L{}l.styles=[s.R,r.AH`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `],l=(0,o.__decorate)([(0,n.EM)("ha-checkbox")],l)},2076:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(62826),a=i(96196),s=i(77845),r=(i(60961),i(88422)),n=t([r]);r=(n.then?(await n)():n)[0];const l="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";class d extends a.WF{render(){return a.qy`
      <ha-svg-icon id="svg-icon" .path=${l}></ha-svg-icon>
      <ha-tooltip for="svg-icon" .placement=${this.position}>
        ${this.label}
      </ha-tooltip>
    `}constructor(...t){super(...t),this.position="top"}}d.styles=a.AH`
    ha-svg-icon {
      --mdc-icon-size: var(--ha-help-tooltip-size, 14px);
      color: var(--ha-help-tooltip-color, var(--disabled-text-color));
    }
  `,(0,o.__decorate)([(0,s.MZ)()],d.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)()],d.prototype,"position",void 0),d=(0,o.__decorate)([(0,s.EM)("ha-help-tooltip")],d),e()}catch(l){e(l)}}))},75261:function(t,e,i){var o=i(62826),a=i(70402),s=i(11081),r=i(77845);class n extends a.iY{}n.styles=s.R,n=(0,o.__decorate)([(0,r.EM)("ha-list")],n)},1554:function(t,e,i){var o=i(62826),a=i(43976),s=i(703),r=i(96196),n=i(77845),l=i(94333);i(75261);class d extends a.ZR{get listElement(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}renderList(){const t="menu"===this.innerRole?"menuitem":"option",e=this.renderListClasses();return r.qy`<ha-list
      rootTabbable
      .innerAriaLabel=${this.innerAriaLabel}
      .innerRole=${this.innerRole}
      .multi=${this.multi}
      class=${(0,l.H)(e)}
      .itemRoles=${t}
      .wrapFocus=${this.wrapFocus}
      .activatable=${this.activatable}
      @action=${this.onAction}
    >
      <slot></slot>
    </ha-list>`}}d.styles=s.R,d=(0,o.__decorate)([(0,n.EM)("ha-menu")],d)},69869:function(t,e,i){var o=i(62826),a=i(14540),s=i(63125),r=i(96196),n=i(77845),l=i(94333),d=i(40404),c=i(99034);i(60733),i(1554);class h extends a.o{render(){return r.qy`
      ${super.render()}
      ${this.clearable&&!this.required&&!this.disabled&&this.value?r.qy`<ha-icon-button
            label="clear"
            @click=${this._clearValue}
            .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
          ></ha-icon-button>`:r.s6}
    `}renderMenu(){const t=this.getMenuClasses();return r.qy`<ha-menu
      innerRole="listbox"
      wrapFocus
      class=${(0,l.H)(t)}
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
    </ha-menu>`}renderLeadingIcon(){return this.icon?r.qy`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`:r.s6}connectedCallback(){super.connectedCallback(),window.addEventListener("translations-updated",this._translationsUpdated)}async firstUpdated(){super.firstUpdated(),this.inlineArrow&&this.shadowRoot?.querySelector(".mdc-select__selected-text-container")?.classList.add("inline-arrow")}updated(t){if(super.updated(t),t.has("inlineArrow")){const t=this.shadowRoot?.querySelector(".mdc-select__selected-text-container");this.inlineArrow?t?.classList.add("inline-arrow"):t?.classList.remove("inline-arrow")}t.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("translations-updated",this._translationsUpdated)}_clearValue(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}constructor(...t){super(...t),this.icon=!1,this.clearable=!1,this.inlineArrow=!1,this._translationsUpdated=(0,d.s)((async()=>{await(0,c.E)(),this.layoutOptions()}),500)}}h.styles=[s.R,r.AH`
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
    `],(0,o.__decorate)([(0,n.MZ)({type:Boolean})],h.prototype,"icon",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],h.prototype,"clearable",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"inline-arrow",type:Boolean})],h.prototype,"inlineArrow",void 0),(0,o.__decorate)([(0,n.MZ)()],h.prototype,"options",void 0),h=(0,o.__decorate)([(0,n.EM)("ha-select")],h)},28238:function(t,e,i){i.a(t,(async function(t,o){try{i.r(e),i.d(e,{HaSelectorUiAction:()=>c});var a=i(62826),s=i(96196),r=i(77845),n=i(92542),l=i(38020),d=t([l]);l=(d.then?(await d)():d)[0];class c extends s.WF{render(){return s.qy`
      <hui-action-editor
        .label=${this.label}
        .hass=${this.hass}
        .config=${this.value}
        .actions=${this.selector.ui_action?.actions}
        .defaultAction=${this.selector.ui_action?.default_action}
        .tooltipText=${this.helper}
        @value-changed=${this._valueChanged}
      ></hui-action-editor>
    `}_valueChanged(t){t.stopPropagation(),(0,n.r)(this,"value-changed",{value:t.detail.value})}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"selector",void 0),(0,a.__decorate)([(0,r.MZ)({attribute:!1})],c.prototype,"value",void 0),(0,a.__decorate)([(0,r.MZ)()],c.prototype,"label",void 0),(0,a.__decorate)([(0,r.MZ)()],c.prototype,"helper",void 0),c=(0,a.__decorate)([(0,r.EM)("ha-selector-ui_action")],c),o()}catch(c){o(c)}}))},2809:function(t,e,i){var o=i(62826),a=i(96196),s=i(77845);class r extends a.WF{render(){return a.qy`
      <div class="prefix-wrap">
        <slot name="prefix"></slot>
        <div
          class="body"
          ?two-line=${!this.threeLine}
          ?three-line=${this.threeLine}
        >
          <slot name="heading"></slot>
          <div class="secondary"><slot name="description"></slot></div>
        </div>
      </div>
      <div class="content"><slot></slot></div>
    `}constructor(...t){super(...t),this.narrow=!1,this.slim=!1,this.threeLine=!1,this.wrapHeading=!1}}r.styles=a.AH`
    :host {
      display: flex;
      padding: 0 16px;
      align-content: normal;
      align-self: auto;
      align-items: center;
    }
    .body {
      padding-top: 8px;
      padding-bottom: 8px;
      padding-left: 0;
      padding-inline-start: 0;
      padding-right: 16px;
      padding-inline-end: 16px;
      overflow: hidden;
      display: var(--layout-vertical_-_display, flex);
      flex-direction: var(--layout-vertical_-_flex-direction, column);
      justify-content: var(--layout-center-justified_-_justify-content, center);
      flex: var(--layout-flex_-_flex, 1);
      flex-basis: var(--layout-flex_-_flex-basis, 0.000000001px);
    }
    .body[three-line] {
      min-height: 88px;
    }
    :host(:not([wrap-heading])) body > * {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .body > .secondary {
      display: block;
      padding-top: 4px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, var(--ha-font-family-body))
      );
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
      line-height: normal;
      color: var(--secondary-text-color);
    }
    .body[two-line] {
      min-height: calc(72px - 16px);
      flex: 1;
    }
    .content {
      display: contents;
    }
    :host(:not([narrow])) .content {
      display: var(--settings-row-content-display, flex);
      justify-content: flex-end;
      flex: 1;
      min-width: 0;
      padding: 16px 0;
    }
    .content ::slotted(*) {
      width: var(--settings-row-content-width);
    }
    :host([narrow]) {
      align-items: normal;
      flex-direction: column;
      border-top: 1px solid var(--divider-color);
      padding-bottom: 8px;
    }
    ::slotted(ha-switch) {
      padding: 16px 0;
    }
    .secondary {
      white-space: normal;
    }
    .prefix-wrap {
      display: var(--settings-row-prefix-display);
    }
    :host([narrow]) .prefix-wrap {
      display: flex;
      align-items: center;
    }
    :host([slim]),
    :host([slim]) .content,
    :host([slim]) ::slotted(ha-switch) {
      padding: 0;
    }
    :host([slim]) .body {
      min-height: 0;
    }
  `,(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],r.prototype,"narrow",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0})],r.prototype,"slim",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"three-line"})],r.prototype,"threeLine",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"wrap-heading",reflect:!0})],r.prototype,"wrapHeading",void 0),r=(0,o.__decorate)([(0,s.EM)("ha-settings-row")],r)},88422:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(62826),a=i(52630),s=i(96196),r=i(77845),n=t([a]);a=(n.then?(await n)():n)[0];class l extends a.A{static get styles(){return[a.A.styles,s.AH`
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
      `]}constructor(...t){super(...t),this.showDelay=150,this.hideDelay=150}}(0,o.__decorate)([(0,r.MZ)({attribute:"show-delay",type:Number})],l.prototype,"showDelay",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"hide-delay",type:Number})],l.prototype,"hideDelay",void 0),l=(0,o.__decorate)([(0,r.EM)("ha-tooltip")],l),e()}catch(l){e(l)}}))},23362:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(62826),a=i(53289),s=i(96196),r=i(77845),n=i(92542),l=i(4657),d=i(39396),c=i(4848),h=(i(17963),i(89473)),p=i(32884),u=t([h,p]);[h,p]=u.then?(await u)():u;const v=t=>{if("object"!=typeof t||null===t)return!1;for(const e in t)if(Object.prototype.hasOwnProperty.call(t,e))return!1;return!0};class y extends s.WF{setValue(t){try{this._yaml=v(t)?"":(0,a.Bh)(t,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(e){console.error(e,t),alert(`There was an error converting to YAML: ${e}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(t){super.willUpdate(t),this.autoUpdate&&t.has("value")&&this.setValue(this.value)}focus(){this._codeEditor?.codemirror&&this._codeEditor?.codemirror.focus()}render(){return void 0===this._yaml?s.s6:s.qy`
      ${this.label?s.qy`<p>${this.label}${this.required?" *":""}</p>`:s.s6}
      <ha-code-editor
        .hass=${this.hass}
        .value=${this._yaml}
        .readOnly=${this.readOnly}
        .disableFullscreen=${this.disableFullscreen}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${!1===this.isValid}
        @value-changed=${this._onChange}
        @blur=${this._onBlur}
        dir="ltr"
      ></ha-code-editor>
      ${this._showingError?s.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:s.s6}
      ${this.copyClipboard||this.hasExtraActions?s.qy`
            <div class="card-actions">
              ${this.copyClipboard?s.qy`
                    <ha-button appearance="plain" @click=${this._copyYaml}>
                      ${this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")}
                    </ha-button>
                  `:s.s6}
              <slot name="extra-actions"></slot>
            </div>
          `:s.s6}
    `}_onChange(t){let e;t.stopPropagation(),this._yaml=t.detail.value;let i,o=!0;if(this._yaml)try{e=(0,a.Hh)(this._yaml,{schema:this.yamlSchema})}catch(s){o=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:s.reason})}${s.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:s.mark.line+1,column:s.mark.column+1})})`:""}`}else e={};this._error=i??"",o&&(this._showingError=!1),this.value=e,this.isValid=o,(0,n.r)(this,"value-changed",{value:e,isValid:o,errorMsg:i})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,l.l)(this.yaml),(0,c.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[d.RF,s.AH`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            var(--ha-border-radius-square) var(--ha-border-radius-square)
              var(--ha-card-border-radius, var(--ha-border-radius-lg))
              var(--ha-card-border-radius, var(--ha-border-radius-lg))
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
          min-height: 0;
        }
      `]}constructor(...t){super(...t),this.yamlSchema=a.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,o.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)()],y.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"yamlSchema",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],y.prototype,"defaultValue",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"is-valid",type:Boolean})],y.prototype,"isValid",void 0),(0,o.__decorate)([(0,r.MZ)()],y.prototype,"label",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"auto-update",type:Boolean})],y.prototype,"autoUpdate",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"read-only",type:Boolean})],y.prototype,"readOnly",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,attribute:"disable-fullscreen"})],y.prototype,"disableFullscreen",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],y.prototype,"required",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"copy-clipboard",type:Boolean})],y.prototype,"copyClipboard",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"has-extra-actions",type:Boolean})],y.prototype,"hasExtraActions",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"show-errors",type:Boolean})],y.prototype,"showErrors",void 0),(0,o.__decorate)([(0,r.wk)()],y.prototype,"_yaml",void 0),(0,o.__decorate)([(0,r.wk)()],y.prototype,"_error",void 0),(0,o.__decorate)([(0,r.wk)()],y.prototype,"_showingError",void 0),(0,o.__decorate)([(0,r.P)("ha-code-editor")],y.prototype,"_codeEditor",void 0),y=(0,o.__decorate)([(0,r.EM)("ha-yaml-editor")],y),e()}catch(v){e(v)}}))},45369:function(t,e,i){i.d(e,{QC:()=>o,ds:()=>d,mp:()=>r,nx:()=>s,u6:()=>n,vU:()=>a,zn:()=>l});const o=(t,e,i)=>"run-start"===e.type?t={init_options:i,stage:"ready",run:e.data,events:[e],started:new Date(e.timestamp)}:t?((t="wake_word-start"===e.type?{...t,stage:"wake_word",wake_word:{...e.data,done:!1}}:"wake_word-end"===e.type?{...t,wake_word:{...t.wake_word,...e.data,done:!0}}:"stt-start"===e.type?{...t,stage:"stt",stt:{...e.data,done:!1}}:"stt-end"===e.type?{...t,stt:{...t.stt,...e.data,done:!0}}:"intent-start"===e.type?{...t,stage:"intent",intent:{...e.data,done:!1}}:"intent-end"===e.type?{...t,intent:{...t.intent,...e.data,done:!0}}:"tts-start"===e.type?{...t,stage:"tts",tts:{...e.data,done:!1}}:"tts-end"===e.type?{...t,tts:{...t.tts,...e.data,done:!0}}:"run-end"===e.type?{...t,finished:new Date(e.timestamp),stage:"done"}:"error"===e.type?{...t,finished:new Date(e.timestamp),stage:"error",error:e.data}:{...t}).events=[...t.events,e],t):void console.warn("Received unexpected event before receiving session",e),a=(t,e,i)=>t.connection.subscribeMessage(e,{...i,type:"assist_pipeline/run"}),s=t=>t.callWS({type:"assist_pipeline/pipeline/list"}),r=(t,e)=>t.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:e}),n=(t,e)=>t.callWS({type:"assist_pipeline/pipeline/create",...e}),l=(t,e,i)=>t.callWS({type:"assist_pipeline/pipeline/update",pipeline_id:e,...i}),d=t=>t.callWS({type:"assist_pipeline/language/list"})},38020:function(t,e,i){i.a(t,(async function(t,e){try{var o=i(62826),a=i(96196),s=i(77845),r=i(22786),n=i(92542),l=i(55124),d=i(56528),c=i(2076),h=(i(56565),i(81657),i(39338)),p=t([d,c,h]);[d,c,h]=p.then?(await p)():p;const u=["more-info","toggle","navigate","url","perform-action","assist","none"],v=[{name:"navigation_path",selector:{navigation:{}}}],y=[{type:"grid",name:"",schema:[{name:"pipeline_id",selector:{assist_pipeline:{include_last_used:!0}}},{name:"start_listening",selector:{boolean:{}}}]}];class _ extends a.WF{get _navigation_path(){const t=this.config;return t?.navigation_path||""}get _url_path(){const t=this.config;return t?.url_path||""}get _service(){const t=this.config;return t?.perform_action||t?.service||""}updated(t){super.updated(t),t.has("defaultAction")&&t.get("defaultAction")!==this.defaultAction&&this._select.layoutOptions()}render(){if(!this.hass)return a.s6;const t=this.actions??u;let e=this.config?.action||"default";return"call-service"===e&&(e="perform-action"),a.qy`
      <div class="dropdown">
        <ha-select
          .label=${this.label}
          .configValue=${"action"}
          @selected=${this._actionPicked}
          .value=${e}
          @closed=${l.d}
          fixedMenuPosition
          naturalMenuWidth
        >
          <ha-list-item value="default">
            ${this.hass.localize("ui.panel.lovelace.editor.action-editor.actions.default_action")}
            ${this.defaultAction?` (${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${this.defaultAction}`).toLowerCase()})`:a.s6}
          </ha-list-item>
          ${t.map((t=>a.qy`
              <ha-list-item .value=${t}>
                ${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${t}`)}
              </ha-list-item>
            `))}
        </ha-select>
        ${this.tooltipText?a.qy`
              <ha-help-tooltip .label=${this.tooltipText}></ha-help-tooltip>
            `:a.s6}
      </div>
      ${"navigate"===this.config?.action?a.qy`
            <ha-form
              .hass=${this.hass}
              .schema=${v}
              .data=${this.config}
              .computeLabel=${this._computeFormLabel}
              @value-changed=${this._formValueChanged}
            >
            </ha-form>
          `:a.s6}
      ${"url"===this.config?.action?a.qy`
            <ha-textfield
              .label=${this.hass.localize("ui.panel.lovelace.editor.action-editor.url_path")}
              .value=${this._url_path}
              .configValue=${"url_path"}
              @input=${this._valueChanged}
            ></ha-textfield>
          `:a.s6}
      ${"call-service"===this.config?.action||"perform-action"===this.config?.action?a.qy`
            <ha-service-control
              .hass=${this.hass}
              .value=${this._serviceAction(this.config)}
              .showAdvanced=${this.hass.userData?.showAdvanced}
              narrow
              @value-changed=${this._serviceValueChanged}
            ></ha-service-control>
          `:a.s6}
      ${"assist"===this.config?.action?a.qy`
            <ha-form
              .hass=${this.hass}
              .schema=${y}
              .data=${this.config}
              .computeLabel=${this._computeFormLabel}
              @value-changed=${this._formValueChanged}
            >
            </ha-form>
          `:a.s6}
    `}_actionPicked(t){if(t.stopPropagation(),!this.hass)return;let e=this.config?.action;"call-service"===e&&(e="perform-action");const i=t.target.value;if(e===i)return;if("default"===i)return void(0,n.r)(this,"value-changed",{value:void 0});let o;switch(i){case"url":o={url_path:this._url_path};break;case"perform-action":o={perform_action:this._service};break;case"navigate":o={navigation_path:this._navigation_path}}(0,n.r)(this,"value-changed",{value:{action:i,...o}})}_valueChanged(t){if(t.stopPropagation(),!this.hass)return;const e=t.target,i=t.target.value??t.target.checked;this[`_${e.configValue}`]!==i&&e.configValue&&(0,n.r)(this,"value-changed",{value:{...this.config,[e.configValue]:i}})}_formValueChanged(t){t.stopPropagation();const e=t.detail.value;(0,n.r)(this,"value-changed",{value:e})}_computeFormLabel(t){return this.hass?.localize(`ui.panel.lovelace.editor.action-editor.${t.name}`)}_serviceValueChanged(t){t.stopPropagation();const e={...this.config,action:"perform-action",perform_action:t.detail.value.action||"",data:t.detail.value.data,target:t.detail.value.target||{}};t.detail.value.data||delete e.data,"service_data"in e&&delete e.service_data,"service"in e&&delete e.service,(0,n.r)(this,"value-changed",{value:e})}constructor(...t){super(...t),this._serviceAction=(0,r.A)((t=>({action:this._service,...t.data||t.service_data?{data:t.data??t.service_data}:null,target:t.target})))}}_.styles=a.AH`
    .dropdown {
      position: relative;
    }
    ha-help-tooltip {
      position: absolute;
      right: 40px;
      top: 16px;
      inset-inline-start: initial;
      inset-inline-end: 40px;
      direction: var(--direction);
    }
    ha-select,
    ha-textfield {
      width: 100%;
    }
    ha-service-control,
    ha-navigation-picker,
    ha-form {
      display: block;
    }
    ha-textfield,
    ha-service-control,
    ha-navigation-picker,
    ha-form {
      margin-top: 8px;
    }
    ha-service-control {
      --service-control-padding: 0;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"config",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"actions",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"defaultAction",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"tooltipText",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,s.P)("ha-select")],_.prototype,"_select",void 0),_=(0,o.__decorate)([(0,s.EM)("hui-action-editor")],_),e()}catch(u){e(u)}}))},62001:function(t,e,i){i.d(e,{o:()=>o});const o=(t,e)=>`https://${t.config.version.includes("b")?"rc":t.config.version.includes("dev")?"next":"www"}.home-assistant.io${e}`},4848:function(t,e,i){i.d(e,{P:()=>a});var o=i(92542);const a=(t,e)=>(0,o.r)(t,"hass-notification",e)},61171:function(t,e,i){i.d(e,{A:()=>o});const o=i(96196).AH`:host {
  --max-width: 30ch;
  display: inline-block;
  position: absolute;
  color: var(--wa-tooltip-content-color);
  font-size: var(--wa-tooltip-font-size);
  line-height: var(--wa-tooltip-line-height);
  text-align: start;
  white-space: normal;
}
.tooltip {
  --arrow-size: var(--wa-tooltip-arrow-size);
  --arrow-color: var(--wa-tooltip-background-color);
}
.tooltip::part(popup) {
  z-index: 1000;
}
.tooltip[placement^=top]::part(popup) {
  transform-origin: bottom;
}
.tooltip[placement^=bottom]::part(popup) {
  transform-origin: top;
}
.tooltip[placement^=left]::part(popup) {
  transform-origin: right;
}
.tooltip[placement^=right]::part(popup) {
  transform-origin: left;
}
.body {
  display: block;
  width: max-content;
  max-width: var(--max-width);
  border-radius: var(--wa-tooltip-border-radius);
  background-color: var(--wa-tooltip-background-color);
  border: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  padding: 0.25em 0.5em;
  user-select: none;
  -webkit-user-select: none;
}
.tooltip::part(arrow) {
  border-bottom: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  border-right: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
}
`},52630:function(t,e,i){i.a(t,(async function(t,o){try{i.d(e,{A:()=>$});var a=i(96196),s=i(77845),r=i(94333),n=i(17051),l=i(42462),d=i(28438),c=i(98779),h=i(27259),p=i(984),u=i(53720),v=i(9395),y=i(32510),_=i(40158),m=i(61171),f=t([_]);_=(f.then?(await f)():f)[0];var g=Object.defineProperty,b=Object.getOwnPropertyDescriptor,w=(t,e,i,o)=>{for(var a,s=o>1?void 0:o?b(e,i):e,r=t.length-1;r>=0;r--)(a=t[r])&&(s=(o?a(e,i,s):a(s))||s);return o&&s&&g(e,i,s),s};let $=class extends y.A{connectedCallback(){super.connectedCallback(),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,u.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}disconnectedCallback(){super.disconnectedCallback(),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}firstUpdated(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}hasTrigger(t){return this.trigger.split(" ").includes(t)}addToAriaLabelledBy(t,e){const i=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);i.includes(e)||(i.push(e),t.setAttribute("aria-labelledby",i.join(" ")))}removeFromAriaLabelledBy(t,e){const i=(t.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((t=>t!==e));i.length>0?t.setAttribute("aria-labelledby",i.join(" ")):t.removeAttribute("aria-labelledby")}async handleOpenChange(){if(this.open){if(this.disabled)return;const t=new c.k;if(this.dispatchEvent(t),t.defaultPrevented)return void(this.open=!1);document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,await(0,h.Ud)(this.popup.popup,"show-with-scale"),this.popup.reposition(),this.dispatchEvent(new l.q)}else{const t=new d.L;if(this.dispatchEvent(t),t.defaultPrevented)return void(this.open=!1);document.removeEventListener("keydown",this.handleDocumentKeyDown),await(0,h.Ud)(this.popup.popup,"hide-with-scale"),this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new n.Z)}}handleForChange(){const t=this.getRootNode();if(!t)return;const e=this.for?t.getElementById(this.for):null,i=this.anchor;if(e===i)return;const{signal:o}=this.eventController;e&&(this.addToAriaLabelledBy(e,this.id),e.addEventListener("blur",this.handleBlur,{capture:!0,signal:o}),e.addEventListener("focus",this.handleFocus,{capture:!0,signal:o}),e.addEventListener("click",this.handleClick,{signal:o}),e.addEventListener("mouseover",this.handleMouseOver,{signal:o}),e.addEventListener("mouseout",this.handleMouseOut,{signal:o})),i&&(this.removeFromAriaLabelledBy(i,this.id),i.removeEventListener("blur",this.handleBlur,{capture:!0}),i.removeEventListener("focus",this.handleFocus,{capture:!0}),i.removeEventListener("click",this.handleClick),i.removeEventListener("mouseover",this.handleMouseOver),i.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=e}async handleOptionsChange(){this.hasUpdated&&(await this.updateComplete,this.popup.reposition())}handleDisabledChange(){this.disabled&&this.open&&this.hide()}async show(){if(!this.open)return this.open=!0,(0,p.l)(this,"wa-after-show")}async hide(){if(this.open)return this.open=!1,(0,p.l)(this,"wa-after-hide")}render(){return a.qy`
      <wa-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${(0,r.H)({tooltip:!0,"tooltip-open":this.open})}
        placement=${this.placement}
        distance=${this.distance}
        skidding=${this.skidding}
        flip
        shift
        ?arrow=${!this.withoutArrow}
        hover-bridge
        .anchor=${this.anchor}
      >
        <div part="body" class="body">
          <slot></slot>
        </div>
      </wa-popup>
    `}constructor(){super(...arguments),this.placement="top",this.disabled=!1,this.distance=8,this.open=!1,this.skidding=0,this.showDelay=150,this.hideDelay=0,this.trigger="hover focus",this.withoutArrow=!1,this.for=null,this.anchor=null,this.eventController=new AbortController,this.handleBlur=()=>{this.hasTrigger("focus")&&this.hide()},this.handleClick=()=>{this.hasTrigger("click")&&(this.open?this.hide():this.show())},this.handleFocus=()=>{this.hasTrigger("focus")&&this.show()},this.handleDocumentKeyDown=t=>{"Escape"===t.key&&(t.stopPropagation(),this.hide())},this.handleMouseOver=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.show()),this.showDelay))},this.handleMouseOut=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.hide()),this.hideDelay))}}};$.css=m.A,$.dependencies={"wa-popup":_.A},w([(0,s.P)("slot:not([name])")],$.prototype,"defaultSlot",2),w([(0,s.P)(".body")],$.prototype,"body",2),w([(0,s.P)("wa-popup")],$.prototype,"popup",2),w([(0,s.MZ)()],$.prototype,"placement",2),w([(0,s.MZ)({type:Boolean,reflect:!0})],$.prototype,"disabled",2),w([(0,s.MZ)({type:Number})],$.prototype,"distance",2),w([(0,s.MZ)({type:Boolean,reflect:!0})],$.prototype,"open",2),w([(0,s.MZ)({type:Number})],$.prototype,"skidding",2),w([(0,s.MZ)({attribute:"show-delay",type:Number})],$.prototype,"showDelay",2),w([(0,s.MZ)({attribute:"hide-delay",type:Number})],$.prototype,"hideDelay",2),w([(0,s.MZ)()],$.prototype,"trigger",2),w([(0,s.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],$.prototype,"withoutArrow",2),w([(0,s.MZ)()],$.prototype,"for",2),w([(0,s.wk)()],$.prototype,"anchor",2),w([(0,v.w)("open",{waitUntilFirstUpdate:!0})],$.prototype,"handleOpenChange",1),w([(0,v.w)("for")],$.prototype,"handleForChange",1),w([(0,v.w)(["distance","placement","skidding"])],$.prototype,"handleOptionsChange",1),w([(0,v.w)("disabled")],$.prototype,"handleDisabledChange",1),$=w([(0,s.EM)("wa-tooltip")],$),o()}catch($){o($)}}))},3890:function(t,e,i){i.d(e,{T:()=>p});var o=i(5055),a=i(63937),s=i(37540);class r{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class n{get(){return this.Y}pause(){this.Y??=new Promise((t=>this.Z=t))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var l=i(42017);const d=t=>!(0,a.sO)(t)&&"function"==typeof t.then,c=1073741823;class h extends s.Kq{render(...t){return t.find((t=>!d(t)))??o.c0}update(t,e){const i=this._$Cbt;let a=i.length;this._$Cbt=e;const s=this._$CK,r=this._$CX;this.isConnected||this.disconnected();for(let o=0;o<e.length&&!(o>this._$Cwt);o++){const t=e[o];if(!d(t))return this._$Cwt=o,t;o<a&&t===i[o]||(this._$Cwt=c,a=0,Promise.resolve(t).then((async e=>{for(;r.get();)await r.get();const i=s.deref();if(void 0!==i){const o=i._$Cbt.indexOf(t);o>-1&&o<i._$Cwt&&(i._$Cwt=o,i.setValue(e))}})))}return o.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new r(this),this._$CX=new n}}const p=(0,l.u$)(h)}};
//# sourceMappingURL=637.6a50440918720b50.js.map