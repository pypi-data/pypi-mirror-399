export const __webpack_id__="2179";export const __webpack_ids__=["2179"];export const __webpack_modules__={89473:function(t,e,a){a.a(t,(async function(t,e){try{var o=a(62826),r=a(88496),i=a(96196),l=a(77845),s=t([r]);r=(s.then?(await s)():s)[0];class n extends r.A{static get styles(){return[r.A.styles,i.AH`
        :host {
          --wa-form-control-padding-inline: 16px;
          --wa-font-weight-action: var(--ha-font-weight-medium);
          --wa-form-control-border-radius: var(
            --ha-button-border-radius,
            var(--ha-border-radius-pill)
          );

          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 40px)
          );
        }
        .button {
          font-size: var(--ha-font-size-m);
          line-height: 1;

          transition: background-color 0.15s ease-in-out;
          text-wrap: wrap;
        }

        :host([size="small"]) .button {
          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 32px)
          );
          font-size: var(--wa-font-size-s, var(--ha-font-size-m));
          --wa-form-control-padding-inline: 12px;
        }

        :host([variant="brand"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-primary-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-primary-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-primary-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-primary-loud-hover
          );
        }

        :host([variant="neutral"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-neutral-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-neutral-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-neutral-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-neutral-loud-hover
          );
        }

        :host([variant="success"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-success-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-success-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-success-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-success-loud-hover
          );
        }

        :host([variant="warning"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-warning-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-warning-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-warning-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-warning-loud-hover
          );
        }

        :host([variant="danger"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-danger-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-danger-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-danger-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-danger-loud-hover
          );
        }

        :host([appearance~="plain"]) .button {
          color: var(--wa-color-on-normal);
          background-color: transparent;
        }
        :host([appearance~="plain"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        :host([appearance~="outlined"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        @media (hover: hover) {
          :host([appearance~="filled"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-normal-hover);
          }
          :host([appearance~="accent"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-loud-hover);
          }
          :host([appearance~="plain"])
            .button:not(.disabled):not(.loading):hover {
            color: var(--wa-color-on-normal);
          }
        }
        :host([appearance~="filled"]) .button {
          color: var(--wa-color-on-normal);
          background-color: var(--wa-color-fill-normal);
          border-color: transparent;
        }
        :host([appearance~="filled"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-normal-active);
        }
        :host([appearance~="filled"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-normal-resting);
          color: var(--ha-color-on-disabled-normal);
        }

        :host([appearance~="accent"]) .button {
          background-color: var(
            --wa-color-fill-loud,
            var(--wa-color-neutral-fill-loud)
          );
        }
        :host([appearance~="accent"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-loud-active);
        }
        :host([appearance~="accent"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-loud-resting);
          color: var(--ha-color-on-disabled-loud);
        }

        :host([loading]) {
          pointer-events: none;
        }

        .button.disabled {
          opacity: 1;
        }

        slot[name="start"]::slotted(*) {
          margin-inline-end: 4px;
        }
        slot[name="end"]::slotted(*) {
          margin-inline-start: 4px;
        }

        .button.has-start {
          padding-inline-start: 8px;
        }
        .button.has-end {
          padding-inline-end: 8px;
        }

        .label {
          overflow: hidden;
          text-overflow: ellipsis;
          padding: var(--ha-space-1) 0;
        }
      `]}constructor(...t){super(...t),this.variant="brand"}}n=(0,o.__decorate)([(0,l.EM)("ha-button")],n),e()}catch(n){e(n)}}))},95379:function(t,e,a){var o=a(62826),r=a(96196),i=a(77845);class l extends r.WF{render(){return r.qy`
      ${this.header?r.qy`<h1 class="card-header">${this.header}</h1>`:r.s6}
      <slot></slot>
    `}constructor(...t){super(...t),this.raised=!1}}l.styles=r.AH`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4);
      display: block;
      margin-block-start: var(--ha-space-0);
      margin-block-end: var(--ha-space-0);
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: var(--ha-space-0);
      margin-top: calc(var(--ha-space-2) * -1);
    }

    :host ::slotted(.card-content) {
      padding: var(--ha-space-4);
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: var(--ha-space-2);
    }
  `,(0,o.__decorate)([(0,i.MZ)()],l.prototype,"header",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],l.prototype,"raised",void 0),l=(0,o.__decorate)([(0,i.EM)("ha-card")],l)},56768:function(t,e,a){var o=a(62826),r=a(96196),i=a(77845);class l extends r.WF{render(){return r.qy`<slot></slot>`}constructor(...t){super(...t),this.disabled=!1}}l.styles=r.AH`
    :host {
      display: block;
      color: var(--mdc-text-field-label-ink-color, rgba(0, 0, 0, 0.6));
      font-size: 0.75rem;
      padding-left: 16px;
      padding-right: 16px;
      padding-inline-start: 16px;
      padding-inline-end: 16px;
      letter-spacing: var(
        --mdc-typography-caption-letter-spacing,
        0.0333333333em
      );
      line-height: normal;
    }
    :host([disabled]) {
      color: var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.6));
    }
  `,(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],l.prototype,"disabled",void 0),l=(0,o.__decorate)([(0,i.EM)("ha-input-helper-text")],l)},9316:function(t,e,a){a.a(t,(async function(t,e){try{var o=a(62826),r=a(96196),i=a(77845),l=a(92542),s=a(39396),n=a(89473),d=(a(60733),a(56768),a(78740),t([n]));n=(d.then?(await d)():d)[0];const c="M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19M8,9H16V19H8V9M15.5,4L14.5,3H9.5L8.5,4H5V6H19V4H15.5Z",h="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";class p extends r.WF{render(){return r.qy`
      ${this._items.map(((t,e)=>{const a=""+(this.itemIndex?` ${e+1}`:"");return r.qy`
          <div class="layout horizontal center-center row">
            <ha-textfield
              .suffix=${this.inputSuffix}
              .prefix=${this.inputPrefix}
              .type=${this.inputType}
              .autocomplete=${this.autocomplete}
              .disabled=${this.disabled}
              dialogInitialFocus=${e}
              .index=${e}
              class="flex-auto"
              .label=${""+(this.label?`${this.label}${a}`:"")}
              .value=${t}
              ?data-last=${e===this._items.length-1}
              @input=${this._editItem}
              @keydown=${this._keyDown}
            ></ha-textfield>
            <ha-icon-button
              .disabled=${this.disabled}
              .index=${e}
              slot="navigationIcon"
              .label=${this.removeLabel??this.hass?.localize("ui.common.remove")??"Remove"}
              @click=${this._removeItem}
              .path=${c}
            ></ha-icon-button>
          </div>
        `}))}
      <div class="layout horizontal">
        <ha-button
          size="small"
          appearance="filled"
          @click=${this._addItem}
          .disabled=${this.disabled}
        >
          <ha-svg-icon slot="start" .path=${h}></ha-svg-icon>
          ${this.addLabel??(this.label?this.hass?.localize("ui.components.multi-textfield.add_item",{item:this.label}):this.hass?.localize("ui.common.add"))??"Add"}
        </ha-button>
      </div>
      ${this.helper?r.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:r.s6}
    `}get _items(){return this.value??[]}async _addItem(){const t=[...this._items,""];this._fireChanged(t),await this.updateComplete;const e=this.shadowRoot?.querySelector("ha-textfield[data-last]");e?.focus()}async _editItem(t){const e=t.target.index,a=[...this._items];a[e]=t.target.value,this._fireChanged(a)}async _keyDown(t){"Enter"===t.key&&(t.stopPropagation(),this._addItem())}async _removeItem(t){const e=t.target.index,a=[...this._items];a.splice(e,1),this._fireChanged(a)}_fireChanged(t){this.value=t,(0,l.r)(this,"value-changed",{value:t})}static get styles(){return[s.RF,r.AH`
        .row {
          margin-bottom: 8px;
        }
        ha-textfield {
          display: block;
        }
        ha-icon-button {
          display: block;
        }
      `]}constructor(...t){super(...t),this.disabled=!1,this.itemIndex=!1}}(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"value",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean})],p.prototype,"disabled",void 0),(0,o.__decorate)([(0,i.MZ)()],p.prototype,"label",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"helper",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"inputType",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"inputSuffix",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"inputPrefix",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"autocomplete",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"addLabel",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],p.prototype,"removeLabel",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:"item-index",type:Boolean})],p.prototype,"itemIndex",void 0),p=(0,o.__decorate)([(0,i.EM)("ha-multi-textfield")],p),e()}catch(c){e(c)}}))},81774:function(t,e,a){a.a(t,(async function(t,o){try{a.r(e),a.d(e,{HaTextSelector:()=>u});var r=a(62826),i=a(96196),l=a(77845),s=a(55376),n=a(92542),d=(a(60733),a(9316)),c=(a(67591),a(78740),t([d]));d=(c.then?(await c)():c)[0];const h="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z",p="M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z";class u extends i.WF{async focus(){await this.updateComplete,this.renderRoot.querySelector("ha-textarea, ha-textfield")?.focus()}render(){return this.selector.text?.multiple?i.qy`
        <ha-multi-textfield
          .hass=${this.hass}
          .value=${(0,s.e)(this.value??[])}
          .disabled=${this.disabled}
          .label=${this.label}
          .inputType=${this.selector.text?.type}
          .inputSuffix=${this.selector.text?.suffix}
          .inputPrefix=${this.selector.text?.prefix}
          .helper=${this.helper}
          .autocomplete=${this.selector.text?.autocomplete}
          @value-changed=${this._handleChange}
        >
        </ha-multi-textfield>
      `:this.selector.text?.multiline?i.qy`<ha-textarea
        .name=${this.name}
        .label=${this.label}
        .placeholder=${this.placeholder}
        .value=${this.value||""}
        .helper=${this.helper}
        helperPersistent
        .disabled=${this.disabled}
        @input=${this._handleChange}
        autocapitalize="none"
        .autocomplete=${this.selector.text?.autocomplete}
        spellcheck="false"
        .required=${this.required}
        autogrow
      ></ha-textarea>`:i.qy`<ha-textfield
        .name=${this.name}
        .value=${this.value||""}
        .placeholder=${this.placeholder||""}
        .helper=${this.helper}
        helperPersistent
        .disabled=${this.disabled}
        .type=${this._unmaskedPassword?"text":this.selector.text?.type}
        @input=${this._handleChange}
        @change=${this._handleChange}
        .label=${this.label||""}
        .prefix=${this.selector.text?.prefix}
        .suffix=${"password"===this.selector.text?.type?i.qy`<div style="width: 24px"></div>`:this.selector.text?.suffix}
        .required=${this.required}
        .autocomplete=${this.selector.text?.autocomplete}
      ></ha-textfield>
      ${"password"===this.selector.text?.type?i.qy`<ha-icon-button
            .label=${this.hass?.localize(this._unmaskedPassword?"ui.components.selectors.text.hide_password":"ui.components.selectors.text.show_password")||(this._unmaskedPassword?"Hide password":"Show password")}
            @click=${this._toggleUnmaskedPassword}
            .path=${this._unmaskedPassword?p:h}
          ></ha-icon-button>`:""}`}_toggleUnmaskedPassword(){this._unmaskedPassword=!this._unmaskedPassword}_handleChange(t){t.stopPropagation();let e=t.detail?.value??t.target.value;this.value!==e&&((""===e||Array.isArray(e)&&0===e.length)&&!this.required&&(e=void 0),(0,n.r)(this,"value-changed",{value:e}))}constructor(...t){super(...t),this.disabled=!1,this.required=!0,this._unmaskedPassword=!1}}u.styles=i.AH`
    :host {
      display: block;
      position: relative;
    }
    ha-textarea,
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
  `,(0,r.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,r.__decorate)([(0,l.MZ)()],u.prototype,"value",void 0),(0,r.__decorate)([(0,l.MZ)()],u.prototype,"name",void 0),(0,r.__decorate)([(0,l.MZ)()],u.prototype,"label",void 0),(0,r.__decorate)([(0,l.MZ)()],u.prototype,"placeholder",void 0),(0,r.__decorate)([(0,l.MZ)()],u.prototype,"helper",void 0),(0,r.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"selector",void 0),(0,r.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,r.__decorate)([(0,l.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,r.__decorate)([(0,l.wk)()],u.prototype,"_unmaskedPassword",void 0),u=(0,r.__decorate)([(0,l.EM)("ha-selector-text")],u),o()}catch(h){o(h)}}))},67591:function(t,e,a){var o=a(62826),r=a(11896),i=a(92347),l=a(75057),s=a(96196),n=a(77845);class d extends r.u{updated(t){super.updated(t),this.autogrow&&t.has("value")&&(this.mdcRoot.dataset.value=this.value+'=​"')}constructor(...t){super(...t),this.autogrow=!1}}d.styles=[i.R,l.R,s.AH`
      :host([autogrow]) .mdc-text-field {
        position: relative;
        min-height: 74px;
        min-width: 178px;
        max-height: 200px;
      }
      :host([autogrow]) .mdc-text-field:after {
        content: attr(data-value);
        margin-top: 23px;
        margin-bottom: 9px;
        line-height: var(--ha-line-height-normal);
        min-height: 42px;
        padding: 0px 32px 0 16px;
        letter-spacing: var(
          --mdc-typography-subtitle1-letter-spacing,
          0.009375em
        );
        visibility: hidden;
        white-space: pre-wrap;
      }
      :host([autogrow]) .mdc-text-field__input {
        position: absolute;
        height: calc(100% - 32px);
      }
      :host([autogrow]) .mdc-text-field.mdc-text-field--no-label:after {
        margin-top: 16px;
        margin-bottom: 16px;
      }
      .mdc-floating-label {
        inset-inline-start: 16px !important;
        inset-inline-end: initial !important;
        transform-origin: var(--float-start) top;
      }
      @media only screen and (min-width: 459px) {
        :host([mobile-multiline]) .mdc-text-field__input {
          white-space: nowrap;
          max-height: 16px;
        }
      }
    `],(0,o.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],d.prototype,"autogrow",void 0),d=(0,o.__decorate)([(0,n.EM)("ha-textarea")],d)},29937:function(t,e,a){var o=a(62826),r=a(96196),i=a(77845),l=a(39501),s=a(5871),n=(a(371),a(45397),a(39396));class d extends r.WF{render(){return r.qy`
      <div class="toolbar">
        <div class="toolbar-content">
          ${this.mainPage||history.state?.root?r.qy`
                <ha-menu-button
                  .hassio=${this.supervisor}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                ></ha-menu-button>
              `:this.backPath?r.qy`
                  <a href=${this.backPath}>
                    <ha-icon-button-arrow-prev
                      .hass=${this.hass}
                    ></ha-icon-button-arrow-prev>
                  </a>
                `:r.qy`
                  <ha-icon-button-arrow-prev
                    .hass=${this.hass}
                    @click=${this._backTapped}
                  ></ha-icon-button-arrow-prev>
                `}

          <div class="main-title">
            <slot name="header">${this.header}</slot>
          </div>
          <slot name="toolbar-icon"></slot>
        </div>
      </div>
      <div class="content ha-scrollbar" @scroll=${this._saveScrollPos}>
        <slot></slot>
      </div>
      <div id="fab">
        <slot name="fab"></slot>
      </div>
    `}_saveScrollPos(t){this._savedScrollPos=t.target.scrollTop}_backTapped(){this.backCallback?this.backCallback():(0,s.O)()}static get styles(){return[n.dp,r.AH`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
          overflow: hidden;
          position: relative;
        }

        :host([narrow]) {
          width: 100%;
          position: fixed;
        }

        .toolbar {
          background-color: var(--app-header-background-color);
          padding-top: var(--safe-area-inset-top);
          padding-right: var(--safe-area-inset-right);
        }
        :host([narrow]) .toolbar {
          padding-left: var(--safe-area-inset-left);
        }

        .toolbar-content {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
          padding: 8px 12px;
        }

        .toolbar a {
          color: var(--sidebar-text-color);
          text-decoration: none;
        }

        ha-menu-button,
        ha-icon-button-arrow-prev,
        ::slotted([slot="toolbar-icon"]) {
          pointer-events: auto;
          color: var(--sidebar-icon-color);
        }

        .main-title {
          margin: var(--margin-title);
          line-height: var(--ha-line-height-normal);
          min-width: 0;
          flex-grow: 1;
          overflow-wrap: break-word;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .content {
          position: relative;
          width: calc(100% - var(--safe-area-inset-right, 0px));
          height: calc(
            100% -
              1px - var(--header-height, 0px) - var(
                --safe-area-inset-top,
                0px
              ) - var(
                --hass-subpage-bottom-inset,
                var(--safe-area-inset-bottom, 0px)
              )
          );
          margin-bottom: var(
            --hass-subpage-bottom-inset,
            var(--safe-area-inset-bottom)
          );
          margin-right: var(--safe-area-inset-right);
          overflow-y: auto;
          overflow: auto;
          -webkit-overflow-scrolling: touch;
        }
        :host([narrow]) .content {
          width: calc(
            100% - var(--safe-area-inset-left, 0px) - var(
                --safe-area-inset-right,
                0px
              )
          );
          margin-left: var(--safe-area-inset-left);
        }

        #fab {
          position: absolute;
          right: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-start: initial;
          bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
          z-index: 1;
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: var(--ha-space-2);
        }
        :host([narrow]) #fab.tabs {
          bottom: calc(84px + var(--safe-area-inset-bottom, 0px));
        }
        #fab[is-wide] {
          bottom: calc(24px + var(--safe-area-inset-bottom, 0px));
          right: calc(24px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(24px + var(--safe-area-inset-right, 0px));
          inset-inline-start: initial;
        }
      `]}constructor(...t){super(...t),this.mainPage=!1,this.narrow=!1,this.supervisor=!1}}(0,o.__decorate)([(0,i.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,o.__decorate)([(0,i.MZ)()],d.prototype,"header",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,attribute:"main-page"})],d.prototype,"mainPage",void 0),(0,o.__decorate)([(0,i.MZ)({type:String,attribute:"back-path"})],d.prototype,"backPath",void 0),(0,o.__decorate)([(0,i.MZ)({attribute:!1})],d.prototype,"backCallback",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean,reflect:!0})],d.prototype,"narrow",void 0),(0,o.__decorate)([(0,i.MZ)({type:Boolean})],d.prototype,"supervisor",void 0),(0,o.__decorate)([(0,l.a)(".content")],d.prototype,"_savedScrollPos",void 0),(0,o.__decorate)([(0,i.Ls)({passive:!0})],d.prototype,"_saveScrollPos",null),d=(0,o.__decorate)([(0,i.EM)("hass-subpage")],d)}};
//# sourceMappingURL=2179.ac4ad7e5c9496f53.js.map