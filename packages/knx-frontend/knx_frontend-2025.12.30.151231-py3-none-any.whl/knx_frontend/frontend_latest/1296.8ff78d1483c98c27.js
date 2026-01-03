/*! For license information please see 1296.8ff78d1483c98c27.js.LICENSE.txt */
export const __webpack_id__="1296";export const __webpack_ids__=["1296"];export const __webpack_modules__={53623:function(o,e,t){t.a(o,(async function(o,r){try{t.r(e),t.d(e,{HaIconOverflowMenu:()=>p});var a=t(62826),i=t(96196),n=t(77845),s=t(94333),l=t(39396),c=(t(63419),t(60733),t(60961),t(88422)),d=(t(99892),t(32072),o([c]));c=(d.then?(await d)():d)[0];const h="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class p extends i.WF{render(){return 0===this.items.length?i.s6:i.qy`
      ${this.narrow?i.qy` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${this._handleIconOverflowMenuOpened}
              positioning="popover"
            >
              <ha-icon-button
                .label=${this.hass.localize("ui.common.overflow_menu")}
                .path=${h}
                slot="trigger"
              ></ha-icon-button>

              ${this.items.map((o=>o.divider?i.qy`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`:i.qy`<ha-md-menu-item
                      ?disabled=${o.disabled}
                      .clickAction=${o.action}
                      class=${(0,s.H)({warning:Boolean(o.warning)})}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${(0,s.H)({warning:Boolean(o.warning)})}
                        .path=${o.path}
                      ></ha-svg-icon>
                      ${o.label}
                    </ha-md-menu-item>`))}
            </ha-md-button-menu>`:i.qy`
            <!-- Icon representation for big screens -->
            ${this.items.map((o=>o.narrowOnly?i.s6:o.divider?i.qy`<div role="separator"></div>`:i.qy`<ha-tooltip
                        .disabled=${!o.tooltip}
                        .for="icon-button-${o.label}"
                        >${o.tooltip??""} </ha-tooltip
                      ><ha-icon-button
                        .id="icon-button-${o.label}"
                        @click=${o.action}
                        .label=${o.label}
                        .path=${o.path}
                        ?disabled=${o.disabled}
                      ></ha-icon-button> `))}
          `}
    `}_handleIconOverflowMenuOpened(o){o.stopPropagation()}static get styles(){return[l.RF,i.AH`
        :host {
          display: flex;
          justify-content: flex-end;
          cursor: initial;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `]}constructor(...o){super(...o),this.items=[],this.narrow=!1}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({type:Array})],p.prototype,"items",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],p.prototype,"narrow",void 0),p=(0,a.__decorate)([(0,n.EM)("ha-icon-overflow-menu")],p),r()}catch(h){r(h)}}))},63419:function(o,e,t){var r=t(62826),a=t(96196),i=t(77845),n=t(92542),s=(t(41742),t(26139)),l=t(8889),c=t(63374);class d extends s.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(o){o.detail.reason.kind===c.fi.KEYDOWN&&o.detail.reason.key===c.NV.ESCAPE||o.detail.initiator.clickAction?.(o.detail.initiator)}}d.styles=[l.R,a.AH`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `],d=(0,r.__decorate)([(0,i.EM)("ha-md-menu")],d);class h extends a.WF{get items(){return this._menu.items}focus(){this._menu.open?this._menu.focus():this._triggerButton?.focus()}render(){return a.qy`
      <div @click=${this._handleClick}>
        <slot name="trigger" @slotchange=${this._setTriggerAria}></slot>
      </div>
      <ha-md-menu
        .quick=${this.quick}
        .positioning=${this.positioning}
        .hasOverflow=${this.hasOverflow}
        .anchorCorner=${this.anchorCorner}
        .menuCorner=${this.menuCorner}
        @opening=${this._handleOpening}
        @closing=${this._handleClosing}
      >
        <slot></slot>
      </ha-md-menu>
    `}_handleOpening(){(0,n.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,n.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...o){super(...o),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}h.styles=a.AH`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `,(0,r.__decorate)([(0,i.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,r.__decorate)([(0,i.MZ)()],h.prototype,"positioning",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"anchor-corner"})],h.prototype,"anchorCorner",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:"menu-corner"})],h.prototype,"menuCorner",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean,attribute:"has-overflow"})],h.prototype,"hasOverflow",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],h.prototype,"quick",void 0),(0,r.__decorate)([(0,i.P)("ha-md-menu",!0)],h.prototype,"_menu",void 0),h=(0,r.__decorate)([(0,i.EM)("ha-md-button-menu")],h)},32072:function(o,e,t){var r=t(62826),a=t(10414),i=t(18989),n=t(96196),s=t(77845);class l extends a.c{}l.styles=[i.R,n.AH`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `],l=(0,r.__decorate)([(0,s.EM)("ha-md-divider")],l)},99892:function(o,e,t){var r=t(62826),a=t(54407),i=t(28522),n=t(96196),s=t(77845);class l extends a.K{}l.styles=[i.R,n.AH`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
        --md-sys-color-secondary-container: rgba(
          var(--rgb-primary-color),
          0.15
        );
        --md-sys-color-on-secondary-container: var(--text-primary-color);
        --mdc-icon-size: 16px;

        --md-sys-color-on-primary-container: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-menu-item-label-text-font: Roboto, sans-serif;
      }
      :host(.warning) {
        --md-menu-item-label-text-color: var(--error-color);
        --md-menu-item-leading-icon-color: var(--error-color);
      }
      ::slotted([slot="headline"]) {
        text-wrap: nowrap;
      }
      :host([disabled]) {
        opacity: 1;
        --md-menu-item-label-text-color: var(--disabled-text-color);
        --md-menu-item-leading-icon-color: var(--disabled-text-color);
      }
    `],(0,r.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"clickAction",void 0),l=(0,r.__decorate)([(0,s.EM)("ha-md-menu-item")],l)},88422:function(o,e,t){t.a(o,(async function(o,e){try{var r=t(62826),a=t(52630),i=t(96196),n=t(77845),s=o([a]);a=(s.then?(await s)():s)[0];class l extends a.A{static get styles(){return[a.A.styles,i.AH`
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
      `]}constructor(...o){super(...o),this.showDelay=150,this.hideDelay=150}}(0,r.__decorate)([(0,n.MZ)({attribute:"show-delay",type:Number})],l.prototype,"showDelay",void 0),(0,r.__decorate)([(0,n.MZ)({attribute:"hide-delay",type:Number})],l.prototype,"hideDelay",void 0),l=(0,r.__decorate)([(0,n.EM)("ha-tooltip")],l),e()}catch(l){e(l)}}))},83461:function(o,e,t){var r=t(62826),a=t(77845),i=t(96196);class n extends i.WF{connectedCallback(){super.connectedCallback(),this.setAttribute("aria-hidden","true")}render(){return i.qy`<span class="shadow"></span>`}}const s=i.AH`:host,.shadow,.shadow::before,.shadow::after{border-radius:inherit;inset:0;position:absolute;transition-duration:inherit;transition-property:inherit;transition-timing-function:inherit}:host{display:flex;pointer-events:none;transition-property:box-shadow,opacity}.shadow::before,.shadow::after{content:"";transition-property:box-shadow,opacity;--_level: var(--md-elevation-level, 0);--_shadow-color: var(--md-elevation-shadow-color, var(--md-sys-color-shadow, #000))}.shadow::before{box-shadow:0px calc(1px*(clamp(0,var(--_level),1) + clamp(0,var(--_level) - 3,1) + 2*clamp(0,var(--_level) - 4,1))) calc(1px*(2*clamp(0,var(--_level),1) + clamp(0,var(--_level) - 2,1) + clamp(0,var(--_level) - 4,1))) 0px var(--_shadow-color);opacity:.3}.shadow::after{box-shadow:0px calc(1px*(clamp(0,var(--_level),1) + clamp(0,var(--_level) - 1,1) + 2*clamp(0,var(--_level) - 2,3))) calc(1px*(3*clamp(0,var(--_level),2) + 2*clamp(0,var(--_level) - 2,3))) calc(1px*(clamp(0,var(--_level),4) + 2*clamp(0,var(--_level) - 4,1))) var(--_shadow-color);opacity:.15}
`;let l=class extends n{};l.styles=[s],l=(0,r.__decorate)([(0,a.EM)("md-elevation")],l)}};
//# sourceMappingURL=1296.8ff78d1483c98c27.js.map