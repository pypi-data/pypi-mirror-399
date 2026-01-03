export const __webpack_id__="2154";export const __webpack_ids__=["2154"];export const __webpack_modules__={5841:function(e,t,a){var o=a(62826),i=a(96196),s=a(77845);class r extends i.WF{render(){return i.qy`
      <footer>
        <slot name="secondaryAction"></slot>
        <slot name="primaryAction"></slot>
      </footer>
    `}static get styles(){return[i.AH`
        footer {
          display: flex;
          gap: var(--ha-space-3);
          justify-content: flex-end;
          align-items: center;
          width: 100%;
        }
      `]}}r=(0,o.__decorate)([(0,s.EM)("ha-dialog-footer")],r)},86451:function(e,t,a){var o=a(62826),i=a(96196),s=a(77845);class r extends i.WF{render(){const e=i.qy`<div class="header-title">
      <slot name="title"></slot>
    </div>`,t=i.qy`<div class="header-subtitle">
      <slot name="subtitle"></slot>
    </div>`;return i.qy`
      <header class="header">
        <div class="header-bar">
          <section class="header-navigation-icon">
            <slot name="navigationIcon"></slot>
          </section>
          <section class="header-content">
            ${"above"===this.subtitlePosition?i.qy`${t}${e}`:i.qy`${e}${t}`}
          </section>
          <section class="header-action-items">
            <slot name="actionItems"></slot>
          </section>
        </div>
        <slot></slot>
      </header>
    `}static get styles(){return[i.AH`
        :host {
          display: block;
        }
        :host([show-border]) {
          border-bottom: 1px solid
            var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
        }
        .header-bar {
          display: flex;
          flex-direction: row;
          align-items: center;
          padding: 0 var(--ha-space-1);
          box-sizing: border-box;
        }
        .header-content {
          flex: 1;
          padding: 10px var(--ha-space-1);
          display: flex;
          flex-direction: column;
          justify-content: center;
          min-height: var(--ha-space-12);
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .header-title {
          height: var(
            --ha-dialog-header-title-height,
            calc(var(--ha-font-size-xl) + var(--ha-space-1))
          );
          font-size: var(--ha-font-size-xl);
          line-height: var(--ha-line-height-condensed);
          font-weight: var(--ha-font-weight-medium);
          color: var(--ha-dialog-header-title-color, var(--primary-text-color));
        }
        .header-subtitle {
          font-size: var(--ha-font-size-m);
          line-height: var(--ha-line-height-normal);
          color: var(
            --ha-dialog-header-subtitle-color,
            var(--secondary-text-color)
          );
        }
        @media all and (min-width: 450px) and (min-height: 500px) {
          .header-bar {
            padding: 0 var(--ha-space-2);
          }
        }
        .header-navigation-icon {
          flex: none;
          min-width: var(--ha-space-2);
          height: 100%;
          display: flex;
          flex-direction: row;
        }
        .header-action-items {
          flex: none;
          min-width: var(--ha-space-2);
          height: 100%;
          display: flex;
          flex-direction: row;
        }
      `]}constructor(...e){super(...e),this.subtitlePosition="below",this.showBorder=!1}}(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"subtitle-position"})],r.prototype,"subtitlePosition",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],r.prototype,"showBorder",void 0),r=(0,o.__decorate)([(0,s.EM)("ha-dialog-header")],r)},36626:function(e,t,a){a.a(e,(async function(e,t){try{var o=a(62826),i=a(93900),s=a(96196),r=a(77845),l=a(32288),d=a(92542),n=a(39396),h=(a(86451),a(60733),e([i]));i=(h.then?(await h)():h)[0];const c="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class p extends s.WF{updated(e){super.updated(e),e.has("open")&&(this._open=this.open)}render(){return s.qy`
      <wa-dialog
        .open=${this._open}
        .lightDismiss=${!this.preventScrimClose}
        without-header
        aria-labelledby=${(0,l.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0))}
        aria-describedby=${(0,l.J)(this.ariaDescribedBy)}
        @wa-show=${this._handleShow}
        @wa-after-show=${this._handleAfterShow}
        @wa-after-hide=${this._handleAfterHide}
      >
        <slot name="header">
          <ha-dialog-header
            .subtitlePosition=${this.headerSubtitlePosition}
            .showBorder=${this._bodyScrolled}
          >
            <slot name="headerNavigationIcon" slot="navigationIcon">
              <ha-icon-button
                data-dialog="close"
                .label=${this.hass?.localize("ui.common.close")??"Close"}
                .path=${c}
              ></ha-icon-button>
            </slot>
            ${void 0!==this.headerTitle?s.qy`<span slot="title" class="title" id="ha-wa-dialog-title">
                  ${this.headerTitle}
                </span>`:s.qy`<slot name="headerTitle" slot="title"></slot>`}
            ${void 0!==this.headerSubtitle?s.qy`<span slot="subtitle">${this.headerSubtitle}</span>`:s.qy`<slot name="headerSubtitle" slot="subtitle"></slot>`}
            <slot name="headerActionItems" slot="actionItems"></slot>
          </ha-dialog-header>
        </slot>
        <div class="body ha-scrollbar" @scroll=${this._handleBodyScroll}>
          <slot></slot>
        </div>
        <slot name="footer" slot="footer"></slot>
      </wa-dialog>
    `}disconnectedCallback(){super.disconnectedCallback(),this._open=!1}_handleBodyScroll(e){this._bodyScrolled=e.target.scrollTop>0}constructor(...e){super(...e),this.open=!1,this.type="standard",this.width="medium",this.preventScrimClose=!1,this.headerSubtitlePosition="below",this.flexContent=!1,this._open=!1,this._bodyScrolled=!1,this._handleShow=async()=>{this._open=!0,(0,d.r)(this,"opened"),await this.updateComplete,requestAnimationFrame((()=>{this.querySelector("[autofocus]")?.focus()}))},this._handleAfterShow=()=>{(0,d.r)(this,"after-show")},this._handleAfterHide=()=>{this._open=!1,(0,d.r)(this,"closed")}}}p.styles=[n.dp,s.AH`
      wa-dialog {
        --full-width: var(--ha-dialog-width-full, min(95vw, var(--safe-width)));
        --width: min(var(--ha-dialog-width-md, 580px), var(--full-width));
        --spacing: var(--dialog-content-padding, var(--ha-space-6));
        --show-duration: var(--ha-dialog-show-duration, 200ms);
        --hide-duration: var(--ha-dialog-hide-duration, 200ms);
        --ha-dialog-surface-background: var(
          --card-background-color,
          var(--ha-color-surface-default)
        );
        --wa-color-surface-raised: var(
          --ha-dialog-surface-background,
          var(--card-background-color, var(--ha-color-surface-default))
        );
        --wa-panel-border-radius: var(
          --ha-dialog-border-radius,
          var(--ha-border-radius-3xl)
        );
        max-width: var(--ha-dialog-max-width, var(--safe-width));
      }

      :host([width="small"]) wa-dialog {
        --width: min(var(--ha-dialog-width-sm, 320px), var(--full-width));
      }

      :host([width="large"]) wa-dialog {
        --width: min(var(--ha-dialog-width-lg, 1024px), var(--full-width));
      }

      :host([width="full"]) wa-dialog {
        --width: var(--full-width);
      }

      wa-dialog::part(dialog) {
        min-width: var(--width, var(--full-width));
        max-width: var(--width, var(--full-width));
        max-height: var(
          --ha-dialog-max-height,
          calc(var(--safe-height) - var(--ha-space-20))
        );
        min-height: var(--ha-dialog-min-height);
        margin-top: var(--dialog-surface-margin-top, auto);
        /* Used to offset the dialog from the safe areas when space is limited */
        transform: translate(
          calc(
            var(--safe-area-offset-left, var(--ha-space-0)) - var(
                --safe-area-offset-right,
                var(--ha-space-0)
              )
          ),
          calc(
            var(--safe-area-offset-top, var(--ha-space-0)) - var(
                --safe-area-offset-bottom,
                var(--ha-space-0)
              )
          )
        );
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      @media all and (max-width: 450px), all and (max-height: 500px) {
        :host([type="standard"]) {
          --ha-dialog-border-radius: var(--ha-space-0);

          wa-dialog {
            /* Make the container fill the whole screen width and not the safe width */
            --full-width: var(--ha-dialog-width-full, 100vw);
            --width: var(--full-width);
          }

          wa-dialog::part(dialog) {
            /* Make the dialog fill the whole screen height and not the safe height */
            min-height: var(--ha-dialog-min-height, 100vh);
            min-height: var(--ha-dialog-min-height, 100dvh);
            max-height: var(--ha-dialog-max-height, 100vh);
            max-height: var(--ha-dialog-max-height, 100dvh);
            margin-top: 0;
            margin-bottom: 0;
            /* Use safe area as padding instead of the container size */
            padding-top: var(--safe-area-inset-top);
            padding-bottom: var(--safe-area-inset-bottom);
            padding-left: var(--safe-area-inset-left);
            padding-right: var(--safe-area-inset-right);
            /* Reset the transform to center the dialog */
            transform: none;
          }
        }
      }

      .header-title-container {
        display: flex;
        align-items: center;
      }

      .header-title {
        margin: 0;
        margin-bottom: 0;
        color: var(--ha-dialog-header-title-color, var(--primary-text-color));
        font-size: var(
          --ha-dialog-header-title-font-size,
          var(--ha-font-size-2xl)
        );
        line-height: var(
          --ha-dialog-header-title-line-height,
          var(--ha-line-height-condensed)
        );
        font-weight: var(
          --ha-dialog-header-title-font-weight,
          var(--ha-font-weight-normal)
        );
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: var(--ha-space-3);
      }

      wa-dialog::part(body) {
        padding: 0;
        display: flex;
        flex-direction: column;
        max-width: 100%;
        overflow: hidden;
      }

      .body {
        position: var(--dialog-content-position, relative);
        padding: 0 var(--dialog-content-padding, var(--ha-space-6))
          var(--dialog-content-padding, var(--ha-space-6))
          var(--dialog-content-padding, var(--ha-space-6));
        overflow: auto;
        flex-grow: 1;
      }
      :host([flexcontent]) .body {
        max-width: 100%;
        flex: 1;
        display: flex;
        flex-direction: column;
      }

      wa-dialog::part(footer) {
        padding: var(--ha-space-0);
      }

      ::slotted([slot="footer"]) {
        display: flex;
        padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4)
          var(--ha-space-4);
        gap: var(--ha-space-3);
        justify-content: flex-end;
        align-items: center;
        width: 100%;
      }
    `],(0,o.__decorate)([(0,r.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"aria-labelledby"})],p.prototype,"ariaLabelledBy",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"aria-describedby"})],p.prototype,"ariaDescribedBy",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],p.prototype,"open",void 0),(0,o.__decorate)([(0,r.MZ)({reflect:!0})],p.prototype,"type",void 0),(0,o.__decorate)([(0,r.MZ)({type:String,reflect:!0,attribute:"width"})],p.prototype,"width",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],p.prototype,"preventScrimClose",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"header-title"})],p.prototype,"headerTitle",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"header-subtitle"})],p.prototype,"headerSubtitle",void 0),(0,o.__decorate)([(0,r.MZ)({type:String,attribute:"header-subtitle-position"})],p.prototype,"headerSubtitlePosition",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],p.prototype,"flexContent",void 0),(0,o.__decorate)([(0,r.wk)()],p.prototype,"_open",void 0),(0,o.__decorate)([(0,r.P)(".body")],p.prototype,"bodyContainer",void 0),(0,o.__decorate)([(0,r.wk)()],p.prototype,"_bodyScrolled",void 0),(0,o.__decorate)([(0,r.Ls)({passive:!0})],p.prototype,"_handleBodyScroll",null),p=(0,o.__decorate)([(0,r.EM)("ha-wa-dialog")],p),t()}catch(c){t(c)}}))},17262:function(e,t,a){var o=a(62826),i=a(96196),s=a(77845),r=(a(60733),a(60961),a(78740),a(92542));class l extends i.WF{focus(){this._input?.focus()}render(){return i.qy`
      <ha-textfield
        .autofocus=${this.autofocus}
        autocomplete="off"
        .label=${this.label||this.hass.localize("ui.common.search")}
        .value=${this.filter||""}
        icon
        .iconTrailing=${this.filter||this.suffix}
        @input=${this._filterInputChanged}
      >
        <slot name="prefix" slot="leadingIcon">
          <ha-svg-icon
            tabindex="-1"
            class="prefix"
            .path=${"M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"}
          ></ha-svg-icon>
        </slot>
        <div class="trailing" slot="trailingIcon">
          ${this.filter&&i.qy`
            <ha-icon-button
              @click=${this._clearSearch}
              .label=${this.hass.localize("ui.common.clear")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              class="clear-button"
            ></ha-icon-button>
          `}
          <slot name="suffix"></slot>
        </div>
      </ha-textfield>
    `}async _filterChanged(e){(0,r.r)(this,"value-changed",{value:String(e)})}async _filterInputChanged(e){this._filterChanged(e.target.value)}async _clearSearch(){this._filterChanged("")}constructor(...e){super(...e),this.suffix=!1,this.autofocus=!1}}l.styles=i.AH`
    :host {
      display: inline-flex;
    }
    ha-svg-icon,
    ha-icon-button {
      color: var(--primary-text-color);
    }
    ha-svg-icon {
      outline: none;
    }
    .clear-button {
      --mdc-icon-size: 20px;
    }
    ha-textfield {
      display: inherit;
    }
    .trailing {
      display: flex;
      align-items: center;
    }
  `,(0,o.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)()],l.prototype,"filter",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],l.prototype,"suffix",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],l.prototype,"autofocus",void 0),(0,o.__decorate)([(0,s.MZ)({type:String})],l.prototype,"label",void 0),(0,o.__decorate)([(0,s.P)("ha-textfield",!0)],l.prototype,"_input",void 0),l=(0,o.__decorate)([(0,s.EM)("search-input")],l)},193:function(e,t,a){a.a(e,(async function(e,o){try{a.r(t),a.d(t,{KnxGaSelectDialog:()=>u});var i=a(62826),s=a(22786),r=a(96196),l=a(77845),d=a(94333),n=a(36626),h=a(89473),c=(a(5841),a(17262),a(42921),a(23897),a(92542)),p=a(39396),g=e([n,h]);[n,h]=g.then?(await g)():g;class u extends r.WF{async showDialog(e){this._params=e,this._groupAddresses=e.groupAddresses??[],this.knx=e.knx,this._selected=e.initialSelection??this._selected,this._open=!0}closeDialog(e){return this._dialogClosed(),!0}_cancel(){this._selected=void 0,this._params?.onClose&&this._params.onClose(void 0),this._dialogClosed()}_confirm(){this._params?.onClose&&this._params.onClose(this._selected),this._dialogClosed()}_itemKeydown(e){if("Enter"===e.key){e.preventDefault();const t=e.currentTarget.getAttribute("value");t&&(this._selected=t,this._confirm())}}_onDoubleClick(e){const t=e.currentTarget.getAttribute("value");this._selected=t??void 0,this._selected&&this._confirm()}_onSelect(e){const t=e.currentTarget.getAttribute("value");this._selected=t??void 0}_onFilterChanged(e){this._filter=e.detail?.value??""}_dialogClosed(){this._open=!1,this._params=void 0,this._filter="",this._selected=void 0,(0,c.r)(this,"dialog-closed",{dialog:this.localName})}_renderGroup(e){return r.qy`
      <div class="group-section">
        <div class="group-title" style="--group-depth: ${e.depth}">${e.title}</div>
        ${e.items.length>0?r.qy`<ha-md-list>
              ${e.items.map((e=>{const t=this._selected===e.address;return r.qy`<ha-md-list-item
                  interactive
                  type="button"
                  value=${e.address}
                  @click=${this._onSelect}
                  @dblclick=${this._onDoubleClick}
                  @keydown=${this._itemKeydown}
                >
                  <div class=${(0,d.H)({"ga-row":!0,selected:t})} slot="headline">
                    <div class="ga-address">${e.address}</div>
                    <div class="ga-name">${e.name??""}</div>
                  </div>
                </ha-md-list-item>`}))}
            </ha-md-list>`:r.s6}
        ${e.childGroups.map((e=>this._renderGroup(e)))}
      </div>
    `}render(){if(!this._params||!this.hass)return r.s6;const e=!this.knx.projectData?.group_ranges,t=this._groupAddresses?.length>0,a=t?this._groupItems(this._filter,this._groupAddresses,this.knx.projectData):[],o=a.length>0;return r.qy`<ha-wa-dialog
      .hass=${this.hass}
      .open=${this._open}
      width=${this._params.width??"medium"}
      .headerTitle=${this._params.title}
      @closed=${this._dialogClosed}
    >
      <div class="dialog-body">
        <search-input
          ?autofocus=${!0}
          .hass=${this.hass}
          .filter=${this._filter}
          @value-changed=${this._onFilterChanged}
          .label=${this.hass.localize("ui.common.search")}
        ></search-input>

        <div class="ga-list-container">
          ${e||!t?r.qy`<div class="empty-state">
                ${this.hass.localize("component.knx.config_panel.entities.create._.knx.knx_group_address.group_address_none_for_dpt")}
              </div>`:o?a.map((e=>this._renderGroup(e))):r.qy`<div class="empty-state">
                  ${this.hass.localize("component.knx.config_panel.entities.create._.knx.knx_group_address.group_address_none_for_filter")}
                </div>`}
        </div>
      </div>

      <ha-dialog-footer slot="footer">
        <ha-button slot="secondaryAction" appearance="plain" @click=${this._cancel}>
          ${this.hass.localize("ui.common.cancel")}
        </ha-button>
        <ha-button slot="primaryAction" @click=${this._confirm} .disabled=${!this._selected}>
          ${this.hass.localize("ui.common.ok")}
        </ha-button>
      </ha-dialog-footer>
    </ha-wa-dialog>`}static get styles(){return[p.nA,r.AH`
        @media all and (min-width: 600px) {
          ha-wa-dialog {
            --mdc-dialog-min-width: 360px;
          }
        }

        .dialog-body {
          display: flex;
          flex-direction: column;
          gap: var(--ha-space-2, 8px);
          height: 100%;
          min-height: 0;
        }

        search-input {
          display: block;
          width: 100%;
        }

        ha-md-list {
          padding: 0;
        }

        .ga-list-container {
          flex: 1 1 auto;
          min-height: 0;
          overflow: auto;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          padding: 0;
        }

        .group-title {
          position: sticky;
          top: calc(var(--group-title-height, 40px) * min(1, var(--group-depth, 0)));
          z-index: calc(10 - var(--group-depth, 0));
          height: var(--group-title-height, 40px);
          box-sizing: border-box;
          display: flex;
          align-items: center;
          font-weight: 600;
          padding: 6px 8px;
          padding-left: calc(8px + var(--group-depth, 0) * 8px);
          color: var(--primary-text-color);
          background: var(--primary-background-color);
          border-bottom: 1px solid var(--divider-color);
        }

        .empty-state {
          padding: 12px;
          color: var(--secondary-text-color);
          font-style: italic;
        }

        .ga-row {
          display: grid;
          grid-template-columns: 10ch minmax(0, 1fr);
          align-items: center;
          gap: var(--ha-space-2, 8px);
          padding: 6px 8px;
          border-radius: 4px;
        }

        .ga-row.selected {
          background-color: rgba(var(--rgb-primary-color), 0.08);
          outline: 2px solid rgba(var(--rgb-accent-color), 0.12);
        }

        .ga-address {
          font-family:
            ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
          width: 100%;
          color: var(--secondary-text-color);
          white-space: nowrap;
        }

        .ga-name {
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          min-width: 0;
        }
      `]}constructor(...e){super(...e),this._open=!1,this._groupAddresses=[],this._filter="",this._groupItems=(0,s.A)(((e,t,a)=>{const o=e.trim().toLowerCase();if(!a||!a.group_ranges)return[];const i=t.filter((e=>{if(!o)return!0;const t=e.address??"",a=e.name??"";return t.toLowerCase().includes(o)||a.toLowerCase().includes(o)})),s=(e,t=0)=>{const a=[];return Object.entries(e).forEach((([e,o])=>{const r=o.group_addresses??[],l=i.filter((e=>r.includes(e.address))),d=o.group_ranges?s(o.group_ranges,t+1):[];(l.length>0||d.length>0)&&a.push({title:`${e} ${o.name}`.trim(),items:l.sort(((e,t)=>e.raw_address-t.raw_address)),depth:t,childGroups:d})})),a};return s(a.group_ranges)}))}}(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,i.__decorate)([(0,l.MZ)({attribute:!1})],u.prototype,"knx",void 0),(0,i.__decorate)([(0,l.wk)()],u.prototype,"_open",void 0),(0,i.__decorate)([(0,l.wk)()],u.prototype,"_params",void 0),(0,i.__decorate)([(0,l.wk)()],u.prototype,"_groupAddresses",void 0),(0,i.__decorate)([(0,l.wk)()],u.prototype,"_selected",void 0),(0,i.__decorate)([(0,l.wk)()],u.prototype,"_filter",void 0),u=(0,i.__decorate)([(0,l.EM)("knx-ga-select-dialog")],u),o()}catch(u){o(u)}}))},99793:function(e,t,a){a.d(t,{A:()=>o});const o=a(96196).AH`:host {
  --width: 31rem;
  --spacing: var(--wa-space-l);
  --show-duration: 200ms;
  --hide-duration: 200ms;
  display: none;
}
:host([open]) {
  display: block;
}
.dialog {
  display: flex;
  flex-direction: column;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: var(--width);
  max-width: calc(100% - var(--wa-space-2xl));
  max-height: calc(100% - var(--wa-space-2xl));
  background-color: var(--wa-color-surface-raised);
  border-radius: var(--wa-panel-border-radius);
  border: none;
  box-shadow: var(--wa-shadow-l);
  padding: 0;
  margin: auto;
}
.dialog.show {
  animation: show-dialog var(--show-duration) ease;
}
.dialog.show::backdrop {
  animation: show-backdrop var(--show-duration, 200ms) ease;
}
.dialog.hide {
  animation: show-dialog var(--hide-duration) ease reverse;
}
.dialog.hide::backdrop {
  animation: show-backdrop var(--hide-duration, 200ms) ease reverse;
}
.dialog.pulse {
  animation: pulse 250ms ease;
}
.dialog:focus {
  outline: none;
}
@media screen and (max-width: 420px) {
  .dialog {
    max-height: 80vh;
  }
}
.open {
  display: flex;
  opacity: 1;
}
.header {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: nowrap;
  padding-inline-start: var(--spacing);
  padding-block-end: 0;
  padding-inline-end: calc(var(--spacing) - var(--wa-form-control-padding-block));
  padding-block-start: calc(var(--spacing) - var(--wa-form-control-padding-block));
}
.title {
  align-self: center;
  flex: 1 1 auto;
  font-family: inherit;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-heading);
  line-height: var(--wa-line-height-condensed);
  margin: 0;
}
.header-actions {
  align-self: start;
  display: flex;
  flex-shrink: 0;
  flex-wrap: wrap;
  justify-content: end;
  gap: var(--wa-space-2xs);
  padding-inline-start: var(--spacing);
}
.header-actions wa-button,
.header-actions ::slotted(wa-button) {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
}
.body {
  flex: 1 1 auto;
  display: block;
  padding: var(--spacing);
  overflow: auto;
  -webkit-overflow-scrolling: touch;
}
.body:focus {
  outline: none;
}
.body:focus-visible {
  outline: var(--wa-focus-ring);
  outline-offset: var(--wa-focus-ring-offset);
}
.footer {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-xs);
  justify-content: end;
  padding: var(--spacing);
  padding-block-start: 0;
}
.footer ::slotted(wa-button:not(:first-of-type)) {
  margin-inline-start: var(--wa-spacing-xs);
}
.dialog::backdrop {
  background-color: var(--wa-color-overlay-modal, rgb(0 0 0 / 0.25));
}
@keyframes pulse {
  0% {
    scale: 1;
  }
  50% {
    scale: 1.02;
  }
  100% {
    scale: 1;
  }
}
@keyframes show-dialog {
  from {
    opacity: 0;
    scale: 0.8;
  }
  to {
    opacity: 1;
    scale: 1;
  }
}
@keyframes show-backdrop {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@media (forced-colors: active) {
  .dialog {
    border: solid 1px white;
  }
}
`},93900:function(e,t,a){a.a(e,(async function(e,t){try{var o=a(96196),i=a(77845),s=a(94333),r=a(32288),l=a(17051),d=a(42462),n=a(28438),h=a(98779),c=a(27259),p=a(31247),g=a(97039),u=a(92070),f=a(9395),v=a(32510),m=a(17060),w=a(88496),y=a(99793),b=e([w,m]);[w,m]=b.then?(await b)():b;var _=Object.defineProperty,x=Object.getOwnPropertyDescriptor,k=(e,t,a,o)=>{for(var i,s=o>1?void 0:o?x(t,a):t,r=e.length-1;r>=0;r--)(i=e[r])&&(s=(o?i(t,a,s):i(s))||s);return o&&s&&_(t,a,s),s};let $=class extends v.A{firstUpdated(){this.open&&(this.addOpenListeners(),this.dialog.showModal(),(0,g.JG)(this))}disconnectedCallback(){super.disconnectedCallback(),(0,g.I7)(this),this.removeOpenListeners()}async requestClose(e){const t=new n.L({source:e});if(this.dispatchEvent(t),t.defaultPrevented)return this.open=!0,void(0,c.Ud)(this.dialog,"pulse");this.removeOpenListeners(),await(0,c.Ud)(this.dialog,"hide"),this.open=!1,this.dialog.close(),(0,g.I7)(this);const a=this.originalTrigger;"function"==typeof a?.focus&&setTimeout((()=>a.focus())),this.dispatchEvent(new l.Z)}addOpenListeners(){document.addEventListener("keydown",this.handleDocumentKeyDown)}removeOpenListeners(){document.removeEventListener("keydown",this.handleDocumentKeyDown)}handleDialogCancel(e){e.preventDefault(),this.dialog.classList.contains("hide")||e.target!==this.dialog||this.requestClose(this.dialog)}handleDialogClick(e){const t=e.target.closest('[data-dialog="close"]');t&&(e.stopPropagation(),this.requestClose(t))}async handleDialogPointerDown(e){e.target===this.dialog&&(this.lightDismiss?this.requestClose(this.dialog):await(0,c.Ud)(this.dialog,"pulse"))}handleOpenChange(){this.open&&!this.dialog.open?this.show():!this.open&&this.dialog.open&&(this.open=!0,this.requestClose(this.dialog))}async show(){const e=new h.k;this.dispatchEvent(e),e.defaultPrevented?this.open=!1:(this.addOpenListeners(),this.originalTrigger=document.activeElement,this.open=!0,this.dialog.showModal(),(0,g.JG)(this),requestAnimationFrame((()=>{const e=this.querySelector("[autofocus]");e&&"function"==typeof e.focus?e.focus():this.dialog.focus()})),await(0,c.Ud)(this.dialog,"show"),this.dispatchEvent(new d.q))}render(){const e=!this.withoutHeader,t=this.hasSlotController.test("footer");return o.qy`
      <dialog
        aria-labelledby=${this.ariaLabelledby??"title"}
        aria-describedby=${(0,r.J)(this.ariaDescribedby)}
        part="dialog"
        class=${(0,s.H)({dialog:!0,open:this.open})}
        @cancel=${this.handleDialogCancel}
        @click=${this.handleDialogClick}
        @pointerdown=${this.handleDialogPointerDown}
      >
        ${e?o.qy`
              <header part="header" class="header">
                <h2 part="title" class="title" id="title">
                  <!-- If there's no label, use an invisible character to prevent the header from collapsing -->
                  <slot name="label"> ${this.label.length>0?this.label:String.fromCharCode(8203)} </slot>
                </h2>
                <div part="header-actions" class="header-actions">
                  <slot name="header-actions"></slot>
                  <wa-button
                    part="close-button"
                    exportparts="base:close-button__base"
                    class="close"
                    appearance="plain"
                    @click="${e=>this.requestClose(e.target)}"
                  >
                    <wa-icon
                      name="xmark"
                      label=${this.localize.term("close")}
                      library="system"
                      variant="solid"
                    ></wa-icon>
                  </wa-button>
                </div>
              </header>
            `:""}

        <div part="body" class="body"><slot></slot></div>

        ${t?o.qy`
              <footer part="footer" class="footer">
                <slot name="footer"></slot>
              </footer>
            `:""}
      </dialog>
    `}constructor(){super(...arguments),this.localize=new m.c(this),this.hasSlotController=new u.X(this,"footer","header-actions","label"),this.open=!1,this.label="",this.withoutHeader=!1,this.lightDismiss=!1,this.handleDocumentKeyDown=e=>{"Escape"===e.key&&this.open&&(e.preventDefault(),e.stopPropagation(),this.requestClose(this.dialog))}}};$.css=y.A,k([(0,i.P)(".dialog")],$.prototype,"dialog",2),k([(0,i.MZ)({type:Boolean,reflect:!0})],$.prototype,"open",2),k([(0,i.MZ)({reflect:!0})],$.prototype,"label",2),k([(0,i.MZ)({attribute:"without-header",type:Boolean,reflect:!0})],$.prototype,"withoutHeader",2),k([(0,i.MZ)({attribute:"light-dismiss",type:Boolean})],$.prototype,"lightDismiss",2),k([(0,i.MZ)({attribute:"aria-labelledby"})],$.prototype,"ariaLabelledby",2),k([(0,i.MZ)({attribute:"aria-describedby"})],$.prototype,"ariaDescribedby",2),k([(0,f.w)("open",{waitUntilFirstUpdate:!0})],$.prototype,"handleOpenChange",1),$=k([(0,i.EM)("wa-dialog")],$),document.addEventListener("click",(e=>{const t=e.target.closest("[data-dialog]");if(t instanceof Element){const[e,a]=(0,p.v)(t.getAttribute("data-dialog")||"");if("open"===e&&a?.length){const e=t.getRootNode().getElementById(a);"wa-dialog"===e?.localName?e.open=!0:console.warn(`A dialog with an ID of "${a}" could not be found in this document.`)}}})),o.S$||document.addEventListener("pointerdown",(()=>{})),t()}catch($){t($)}}))}};
//# sourceMappingURL=2154.10560ef69e3eb2e6.js.map