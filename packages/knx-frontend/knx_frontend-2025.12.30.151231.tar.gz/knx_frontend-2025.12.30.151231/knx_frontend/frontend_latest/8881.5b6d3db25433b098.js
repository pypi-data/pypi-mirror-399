export const __webpack_id__="8881";export const __webpack_ids__=["8881"];export const __webpack_modules__={95096:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{HaNumberSelector:()=>c});var r=i(62826),o=i(96196),l=i(77845),s=i(94333),n=i(92542),h=(i(56768),i(60808)),d=(i(78740),e([h]));h=(d.then?(await d)():d)[0];class c extends o.WF{willUpdate(e){e.has("value")&&(""!==this._valueStr&&this.value===Number(this._valueStr)||(this._valueStr=null==this.value||isNaN(this.value)?"":this.value.toString()))}render(){const e="box"===this.selector.number?.mode||void 0===this.selector.number?.min||void 0===this.selector.number?.max;let t;if(!e&&(t=this.selector.number.step??1,"any"===t)){t=1;const e=(this.selector.number.max-this.selector.number.min)/100;for(;t>e;)t/=10}const i=this.selector.number?.translation_key;let a=this.selector.number?.unit_of_measurement;return e&&a&&this.localizeValue&&i&&(a=this.localizeValue(`${i}.unit_of_measurement.${a}`)||a),o.qy`
      ${this.label&&!e?o.qy`${this.label}${this.required?"*":""}`:o.s6}
      <div class="input">
        ${e?o.s6:o.qy`
              <ha-slider
                labeled
                .min=${this.selector.number.min}
                .max=${this.selector.number.max}
                .value=${this.value}
                .step=${t}
                .disabled=${this.disabled}
                .required=${this.required}
                @change=${this._handleSliderChange}
                .withMarkers=${this.selector.number?.slider_ticks||!1}
              >
              </ha-slider>
            `}
        <ha-textfield
          .inputMode=${"any"===this.selector.number?.step||(this.selector.number?.step??1)%1!=0?"decimal":"numeric"}
          .label=${e?this.label:void 0}
          .placeholder=${this.placeholder}
          class=${(0,s.H)({single:e})}
          .min=${this.selector.number?.min}
          .max=${this.selector.number?.max}
          .value=${this._valueStr??""}
          .step=${this.selector.number?.step??1}
          helperPersistent
          .helper=${e?this.helper:void 0}
          .disabled=${this.disabled}
          .required=${this.required}
          .suffix=${a}
          type="number"
          autoValidate
          ?no-spinner=${!e}
          @input=${this._handleInputChange}
        >
        </ha-textfield>
      </div>
      ${!e&&this.helper?o.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:o.s6}
    `}_handleInputChange(e){e.stopPropagation(),this._valueStr=e.target.value;const t=""===e.target.value||isNaN(e.target.value)?void 0:Number(e.target.value);this.value!==t&&(0,n.r)(this,"value-changed",{value:t})}_handleSliderChange(e){e.stopPropagation();const t=Number(e.target.value);this.value!==t&&(0,n.r)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.required=!0,this.disabled=!1,this._valueStr=""}}c.styles=o.AH`
    .input {
      display: flex;
      justify-content: space-between;
      align-items: center;
      direction: ltr;
    }
    ha-slider {
      flex: 1;
      margin-right: 16px;
      margin-inline-end: 16px;
      margin-inline-start: 0;
    }
    ha-textfield {
      --ha-textfield-input-width: 40px;
    }
    .single {
      --ha-textfield-input-width: unset;
      flex: 1;
    }
  `,(0,r.__decorate)([(0,l.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,r.__decorate)([(0,l.MZ)({attribute:!1})],c.prototype,"selector",void 0),(0,r.__decorate)([(0,l.MZ)({type:Number})],c.prototype,"value",void 0),(0,r.__decorate)([(0,l.MZ)({type:Number})],c.prototype,"placeholder",void 0),(0,r.__decorate)([(0,l.MZ)()],c.prototype,"label",void 0),(0,r.__decorate)([(0,l.MZ)()],c.prototype,"helper",void 0),(0,r.__decorate)([(0,l.MZ)({attribute:!1})],c.prototype,"localizeValue",void 0),(0,r.__decorate)([(0,l.MZ)({type:Boolean})],c.prototype,"required",void 0),(0,r.__decorate)([(0,l.MZ)({type:Boolean})],c.prototype,"disabled",void 0),c=(0,r.__decorate)([(0,l.EM)("ha-selector-number")],c),a()}catch(c){a(c)}}))},60808:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),r=i(60346),o=i(96196),l=i(77845),s=i(76679),n=e([r]);r=(n.then?(await n)():n)[0];class h extends r.A{connectedCallback(){super.connectedCallback(),this.dir=s.G.document.dir}static get styles(){return[r.A.styles,o.AH`
        :host {
          --track-size: var(--ha-slider-track-size, 4px);
          --marker-height: calc(var(--ha-slider-track-size, 4px) / 2);
          --marker-width: calc(var(--ha-slider-track-size, 4px) / 2);
          --wa-color-surface-default: var(--card-background-color);
          --wa-color-neutral-fill-normal: var(--disabled-color);
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-color: var(--primary-text-color);
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
          min-width: 100px;
          min-inline-size: 100px;
          width: 200px;
        }

        #thumb {
          border: none;
          background-color: var(--ha-slider-thumb-color, var(--primary-color));
        }

        #thumb:after {
          content: "";
          border-radius: 50%;
          position: absolute;
          width: calc(var(--thumb-width) * 2 + 8px);
          height: calc(var(--thumb-height) * 2 + 8px);
          left: calc(-50% - 4px);
          top: calc(-50% - 4px);
          cursor: pointer;
        }

        #slider:focus-visible:not(.disabled) #thumb,
        #slider:focus-visible:not(.disabled) #thumb-min,
        #slider:focus-visible:not(.disabled) #thumb-max {
          outline: var(--wa-focus-ring);
        }

        #track:after {
          content: "";
          position: absolute;
          top: calc(-50% - 4px);
          left: 0;
          width: 100%;
          height: calc(var(--track-size) * 2 + 8px);
          cursor: pointer;
        }

        #indicator {
          background-color: var(
            --ha-slider-indicator-color,
            var(--primary-color)
          );
        }

        :host([size="medium"]) {
          --thumb-width: 20px;
          --thumb-height: 20px;
        }

        :host([size="small"]) {
          --thumb-width: 16px;
          --thumb-height: 16px;
        }
      `]}constructor(...e){super(...e),this.size="small",this.withTooltip=!0}}(0,a.__decorate)([(0,l.MZ)({reflect:!0})],h.prototype,"size",void 0),(0,a.__decorate)([(0,l.MZ)({type:Boolean,attribute:"with-tooltip"})],h.prototype,"withTooltip",void 0),h=(0,a.__decorate)([(0,l.EM)("ha-slider")],h),t()}catch(h){t(h)}}))}};
//# sourceMappingURL=8881.5b6d3db25433b098.js.map