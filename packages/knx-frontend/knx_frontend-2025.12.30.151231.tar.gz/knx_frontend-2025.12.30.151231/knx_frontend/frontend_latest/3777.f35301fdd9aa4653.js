export const __webpack_id__="3777";export const __webpack_ids__=["3777"];export const __webpack_modules__={29261:function(e,t,i){var a=i(62826),s=i(96196),o=i(77845),n=i(32288),l=i(92542),d=i(55124);i(60733),i(56768),i(56565),i(69869),i(78740);class r extends s.WF{render(){return s.qy`
      ${this.label?s.qy`<label>${this.label}${this.required?" *":""}</label>`:s.s6}
      <div class="time-input-wrap-wrap">
        <div class="time-input-wrap">
          ${this.enableDay?s.qy`
                <ha-textfield
                  id="day"
                  type="number"
                  inputmode="numeric"
                  .value=${this.days.toFixed()}
                  .label=${this.dayLabel}
                  name="days"
                  @change=${this._valueChanged}
                  @focusin=${this._onFocus}
                  no-spinner
                  .required=${this.required}
                  .autoValidate=${this.autoValidate}
                  min="0"
                  .disabled=${this.disabled}
                  suffix=":"
                  class="hasSuffix"
                >
                </ha-textfield>
              `:s.s6}

          <ha-textfield
            id="hour"
            type="number"
            inputmode="numeric"
            .value=${this.hours.toFixed()}
            .label=${this.hourLabel}
            name="hours"
            @change=${this._valueChanged}
            @focusin=${this._onFocus}
            no-spinner
            .required=${this.required}
            .autoValidate=${this.autoValidate}
            maxlength="2"
            max=${(0,n.J)(this._hourMax)}
            min="0"
            .disabled=${this.disabled}
            suffix=":"
            class="hasSuffix"
          >
          </ha-textfield>
          <ha-textfield
            id="min"
            type="number"
            inputmode="numeric"
            .value=${this._formatValue(this.minutes)}
            .label=${this.minLabel}
            @change=${this._valueChanged}
            @focusin=${this._onFocus}
            name="minutes"
            no-spinner
            .required=${this.required}
            .autoValidate=${this.autoValidate}
            maxlength="2"
            max="59"
            min="0"
            .disabled=${this.disabled}
            .suffix=${this.enableSecond?":":""}
            class=${this.enableSecond?"has-suffix":""}
          >
          </ha-textfield>
          ${this.enableSecond?s.qy`<ha-textfield
                id="sec"
                type="number"
                inputmode="numeric"
                .value=${this._formatValue(this.seconds)}
                .label=${this.secLabel}
                @change=${this._valueChanged}
                @focusin=${this._onFocus}
                name="seconds"
                no-spinner
                .required=${this.required}
                .autoValidate=${this.autoValidate}
                maxlength="2"
                max="59"
                min="0"
                .disabled=${this.disabled}
                .suffix=${this.enableMillisecond?":":""}
                class=${this.enableMillisecond?"has-suffix":""}
              >
              </ha-textfield>`:s.s6}
          ${this.enableMillisecond?s.qy`<ha-textfield
                id="millisec"
                type="number"
                .value=${this._formatValue(this.milliseconds,3)}
                .label=${this.millisecLabel}
                @change=${this._valueChanged}
                @focusin=${this._onFocus}
                name="milliseconds"
                no-spinner
                .required=${this.required}
                .autoValidate=${this.autoValidate}
                maxlength="3"
                max="999"
                min="0"
                .disabled=${this.disabled}
              >
              </ha-textfield>`:s.s6}
          ${!this.clearable||this.required||this.disabled?s.s6:s.qy`<ha-icon-button
                label="clear"
                @click=${this._clearValue}
                .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ></ha-icon-button>`}
        </div>

        ${24===this.format?s.s6:s.qy`<ha-select
              .required=${this.required}
              .value=${this.amPm}
              .disabled=${this.disabled}
              name="amPm"
              naturalMenuWidth
              fixedMenuPosition
              @selected=${this._valueChanged}
              @closed=${d.d}
            >
              <ha-list-item value="AM">AM</ha-list-item>
              <ha-list-item value="PM">PM</ha-list-item>
            </ha-select>`}
      </div>
      ${this.helper?s.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:s.s6}
    `}_clearValue(){(0,l.r)(this,"value-changed")}_valueChanged(e){const t=e.currentTarget;this[t.name]="amPm"===t.name?t.value:Number(t.value);const i={hours:this.hours,minutes:this.minutes,seconds:this.seconds,milliseconds:this.milliseconds};this.enableDay&&(i.days=this.days),12===this.format&&(i.amPm=this.amPm),(0,l.r)(this,"value-changed",{value:i})}_onFocus(e){e.currentTarget.select()}_formatValue(e,t=2){return e.toString().padStart(t,"0")}get _hourMax(){if(!this.noHoursLimit)return 12===this.format?12:23}constructor(...e){super(...e),this.autoValidate=!1,this.required=!1,this.format=12,this.disabled=!1,this.days=0,this.hours=0,this.minutes=0,this.seconds=0,this.milliseconds=0,this.dayLabel="",this.hourLabel="",this.minLabel="",this.secLabel="",this.millisecLabel="",this.enableSecond=!1,this.enableMillisecond=!1,this.enableDay=!1,this.noHoursLimit=!1,this.amPm="AM"}}r.styles=s.AH`
    :host([clearable]) {
      position: relative;
    }
    .time-input-wrap-wrap {
      display: flex;
    }
    .time-input-wrap {
      display: flex;
      flex: var(--time-input-flex, unset);
      border-radius: var(--mdc-shape-small, var(--ha-border-radius-sm))
        var(--mdc-shape-small, var(--ha-border-radius-sm))
        var(--ha-border-radius-square) var(--ha-border-radius-square);
      overflow: hidden;
      position: relative;
      direction: ltr;
      padding-right: 3px;
    }
    ha-textfield {
      width: 60px;
      flex-grow: 1;
      text-align: center;
      --mdc-shape-small: 0;
      --text-field-appearance: none;
      --text-field-padding: 0 4px;
      --text-field-suffix-padding-left: 2px;
      --text-field-suffix-padding-right: 0;
      --text-field-text-align: center;
    }
    ha-textfield.hasSuffix {
      --text-field-padding: 0 0 0 4px;
    }
    ha-textfield:first-child {
      --text-field-border-top-left-radius: var(--mdc-shape-medium);
    }
    ha-textfield:last-child {
      --text-field-border-top-right-radius: var(--mdc-shape-medium);
    }
    ha-select {
      --mdc-shape-small: 0;
      width: 85px;
    }
    :host([clearable]) .mdc-select__anchor {
      padding-inline-end: var(--select-selected-text-padding-end, 12px);
    }
    ha-icon-button {
      position: relative;
      --mdc-icon-button-size: 36px;
      --mdc-icon-size: 20px;
      color: var(--secondary-text-color);
      direction: var(--direction);
      display: flex;
      align-items: center;
      background-color: var(--mdc-text-field-fill-color, whitesmoke);
      border-bottom-style: solid;
      border-bottom-width: 1px;
    }
    label {
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, var(--ha-font-family-body))
      );
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      line-height: var(
        --mdc-typography-body2-line-height,
        var(--ha-line-height-condensed)
      );
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
      letter-spacing: var(
        --mdc-typography-body2-letter-spacing,
        0.0178571429em
      );
      text-decoration: var(--mdc-typography-body2-text-decoration, inherit);
      text-transform: var(--mdc-typography-body2-text-transform, inherit);
      color: var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));
      padding-left: 4px;
      padding-inline-start: 4px;
      padding-inline-end: initial;
    }
    ha-input-helper-text {
      padding-top: 8px;
      line-height: var(--ha-line-height-condensed);
    }
  `,(0,a.__decorate)([(0,o.MZ)()],r.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],r.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"auto-validate",type:Boolean})],r.prototype,"autoValidate",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],r.prototype,"required",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],r.prototype,"format",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],r.prototype,"disabled",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],r.prototype,"days",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],r.prototype,"hours",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],r.prototype,"minutes",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],r.prototype,"seconds",void 0),(0,a.__decorate)([(0,o.MZ)({type:Number})],r.prototype,"milliseconds",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"day-label"})],r.prototype,"dayLabel",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"hour-label"})],r.prototype,"hourLabel",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"min-label"})],r.prototype,"minLabel",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"sec-label"})],r.prototype,"secLabel",void 0),(0,a.__decorate)([(0,o.MZ)({type:String,attribute:"ms-label"})],r.prototype,"millisecLabel",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"enable-second",type:Boolean})],r.prototype,"enableSecond",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"enable-millisecond",type:Boolean})],r.prototype,"enableMillisecond",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"enable-day",type:Boolean})],r.prototype,"enableDay",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"no-hours-limit",type:Boolean})],r.prototype,"noHoursLimit",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:!1})],r.prototype,"amPm",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],r.prototype,"clearable",void 0),r=(0,a.__decorate)([(0,o.EM)("ha-base-time-input")],r)},33464:function(e,t,i){var a=i(62826),s=i(96196),o=i(77845),n=i(92542);i(29261);class l extends s.WF{render(){return s.qy`
      <ha-base-time-input
        .label=${this.label}
        .helper=${this.helper}
        .required=${this.required}
        .clearable=${!this.required&&void 0!==this.data}
        .autoValidate=${this.required}
        .disabled=${this.disabled}
        errorMessage="Required"
        enable-second
        .enableMillisecond=${this.enableMillisecond}
        .enableDay=${this.enableDay}
        format="24"
        .days=${this._days}
        .hours=${this._hours}
        .minutes=${this._minutes}
        .seconds=${this._seconds}
        .milliseconds=${this._milliseconds}
        @value-changed=${this._durationChanged}
        no-hours-limit
        day-label="dd"
        hour-label="hh"
        min-label="mm"
        sec-label="ss"
        ms-label="ms"
      ></ha-base-time-input>
    `}get _days(){return this.data?.days?Number(this.data.days):this.required||this.data?0:NaN}get _hours(){return this.data?.hours?Number(this.data.hours):this.required||this.data?0:NaN}get _minutes(){return this.data?.minutes?Number(this.data.minutes):this.required||this.data?0:NaN}get _seconds(){return this.data?.seconds?Number(this.data.seconds):this.required||this.data?0:NaN}get _milliseconds(){return this.data?.milliseconds?Number(this.data.milliseconds):this.required||this.data?0:NaN}_durationChanged(e){e.stopPropagation();const t=e.detail.value?{...e.detail.value}:void 0;t&&(t.hours||=0,t.minutes||=0,t.seconds||=0,"days"in t&&(t.days||=0),"milliseconds"in t&&(t.milliseconds||=0),this.enableMillisecond||t.milliseconds?t.milliseconds>999&&(t.seconds+=Math.floor(t.milliseconds/1e3),t.milliseconds%=1e3):delete t.milliseconds,t.seconds>59&&(t.minutes+=Math.floor(t.seconds/60),t.seconds%=60),t.minutes>59&&(t.hours+=Math.floor(t.minutes/60),t.minutes%=60),this.enableDay&&t.hours>24&&(t.days=(t.days??0)+Math.floor(t.hours/24),t.hours%=24)),(0,n.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.required=!1,this.enableMillisecond=!1,this.enableDay=!1,this.disabled=!1}}(0,a.__decorate)([(0,o.MZ)({attribute:!1})],l.prototype,"data",void 0),(0,a.__decorate)([(0,o.MZ)()],l.prototype,"label",void 0),(0,a.__decorate)([(0,o.MZ)()],l.prototype,"helper",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],l.prototype,"required",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"enable-millisecond",type:Boolean})],l.prototype,"enableMillisecond",void 0),(0,a.__decorate)([(0,o.MZ)({attribute:"enable-day",type:Boolean})],l.prototype,"enableDay",void 0),(0,a.__decorate)([(0,o.MZ)({type:Boolean})],l.prototype,"disabled",void 0),l=(0,a.__decorate)([(0,o.EM)("ha-duration-input")],l)},1554:function(e,t,i){var a=i(62826),s=i(43976),o=i(703),n=i(96196),l=i(77845),d=i(94333);i(75261);class r extends s.ZR{get listElement(){return this.listElement_||(this.listElement_=this.renderRoot.querySelector("ha-list")),this.listElement_}renderList(){const e="menu"===this.innerRole?"menuitem":"option",t=this.renderListClasses();return n.qy`<ha-list
      rootTabbable
      .innerAriaLabel=${this.innerAriaLabel}
      .innerRole=${this.innerRole}
      .multi=${this.multi}
      class=${(0,d.H)(t)}
      .itemRoles=${e}
      .wrapFocus=${this.wrapFocus}
      .activatable=${this.activatable}
      @action=${this.onAction}
    >
      <slot></slot>
    </ha-list>`}}r.styles=o.R,r=(0,a.__decorate)([(0,l.EM)("ha-menu")],r)},69869:function(e,t,i){var a=i(62826),s=i(14540),o=i(63125),n=i(96196),l=i(77845),d=i(94333),r=i(40404),h=i(99034);i(60733),i(1554);class c extends s.o{render(){return n.qy`
      ${super.render()}
      ${this.clearable&&!this.required&&!this.disabled&&this.value?n.qy`<ha-icon-button
            label="clear"
            @click=${this._clearValue}
            .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
          ></ha-icon-button>`:n.s6}
    `}renderMenu(){const e=this.getMenuClasses();return n.qy`<ha-menu
      innerRole="listbox"
      wrapFocus
      class=${(0,d.H)(e)}
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
    </ha-menu>`}renderLeadingIcon(){return this.icon?n.qy`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`:n.s6}connectedCallback(){super.connectedCallback(),window.addEventListener("translations-updated",this._translationsUpdated)}async firstUpdated(){super.firstUpdated(),this.inlineArrow&&this.shadowRoot?.querySelector(".mdc-select__selected-text-container")?.classList.add("inline-arrow")}updated(e){if(super.updated(e),e.has("inlineArrow")){const e=this.shadowRoot?.querySelector(".mdc-select__selected-text-container");this.inlineArrow?e?.classList.add("inline-arrow"):e?.classList.remove("inline-arrow")}e.get("options")&&(this.layoutOptions(),this.selectByValue(this.value))}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("translations-updated",this._translationsUpdated)}_clearValue(){!this.disabled&&this.value&&(this.valueSetDirectly=!0,this.select(-1),this.mdcFoundation.handleChange())}constructor(...e){super(...e),this.icon=!1,this.clearable=!1,this.inlineArrow=!1,this._translationsUpdated=(0,r.s)((async()=>{await(0,h.E)(),this.layoutOptions()}),500)}}c.styles=[o.R,n.AH`
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
    `],(0,a.__decorate)([(0,l.MZ)({type:Boolean})],c.prototype,"icon",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,reflect:!0})],c.prototype,"clearable",void 0),(0,a.__decorate)([(0,l.MZ)({attribute:"inline-arrow",type:Boolean})],c.prototype,"inlineArrow",void 0),(0,a.__decorate)([(0,l.MZ)()],c.prototype,"options",void 0),c=(0,a.__decorate)([(0,l.EM)("ha-select")],c)}};
//# sourceMappingURL=3777.f35301fdd9aa4653.js.map