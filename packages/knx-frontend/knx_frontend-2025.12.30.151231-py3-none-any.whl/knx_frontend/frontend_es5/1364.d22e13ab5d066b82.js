"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1364"],{70524:function(e,t,a){var i,o=a(56038),r=a(44734),h=a(69683),l=a(6454),s=a(62826),d=a(69162),n=a(47191),c=a(96196),u=a(77845),v=function(e){function t(){return(0,r.A)(this,t),(0,h.A)(this,t,arguments)}return(0,l.A)(t,e),(0,o.A)(t)}(d.L);v.styles=[n.R,(0,c.AH)(i||(i=(e=>e)`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `))],v=(0,s.__decorate)([(0,u.EM)("ha-checkbox")],v)},28175:function(e,t,a){a.a(e,(async function(e,i){try{a.r(t),a.d(t,{HaFormInteger:function(){return y}});var o=a(44734),r=a(56038),h=a(69683),l=a(6454),s=(a(78170),a(52675),a(89463),a(28706),a(62826)),d=a(96196),n=a(77845),c=a(92542),u=a(60808),v=(a(70524),a(56768),a(78740),e([u]));u=(v.then?(await v)():v)[0];var p,m,f,b,g,x=e=>e,y=function(e){function t(){var e;(0,o.A)(this,t);for(var a=arguments.length,i=new Array(a),r=0;r<a;r++)i[r]=arguments[r];return(e=(0,h.A)(this,t,[].concat(i))).disabled=!1,e}return(0,l.A)(t,e),(0,r.A)(t,[{key:"focus",value:function(){this._input&&this._input.focus()}},{key:"render",value:function(){var e,t;return void 0!==this.schema.valueMin&&void 0!==this.schema.valueMax&&this.schema.valueMax-this.schema.valueMin<256?(0,d.qy)(p||(p=x`
        <div>
          ${0}
          <div class="flex">
            ${0}
            <ha-slider
              labeled
              .value=${0}
              .min=${0}
              .max=${0}
              .disabled=${0}
              @change=${0}
            ></ha-slider>
          </div>
          ${0}
        </div>
      `),this.label,this.schema.required?"":(0,d.qy)(m||(m=x`
                  <ha-checkbox
                    @change=${0}
                    .checked=${0}
                    .disabled=${0}
                  ></ha-checkbox>
                `),this._handleCheckboxChange,void 0!==this.data,this.disabled),this._value,this.schema.valueMin,this.schema.valueMax,this.disabled||void 0===this.data&&!this.schema.required,this._valueChanged,this.helper?(0,d.qy)(f||(f=x`<ha-input-helper-text .disabled=${0}
                >${0}</ha-input-helper-text
              >`),this.disabled,this.helper):""):(0,d.qy)(b||(b=x`
      <ha-textfield
        type="number"
        inputMode="numeric"
        .label=${0}
        .helper=${0}
        helperPersistent
        .value=${0}
        .disabled=${0}
        .required=${0}
        .autoValidate=${0}
        .suffix=${0}
        .validationMessage=${0}
        @input=${0}
      ></ha-textfield>
    `),this.label,this.helper,void 0!==this.data?this.data:"",this.disabled,this.schema.required,this.schema.required,null===(e=this.schema.description)||void 0===e?void 0:e.suffix,this.schema.required?null===(t=this.localize)||void 0===t?void 0:t.call(this,"ui.common.error_required"):void 0,this._valueChanged)}},{key:"updated",value:function(e){e.has("schema")&&this.toggleAttribute("own-margin",!("valueMin"in this.schema&&"valueMax"in this.schema||!this.schema.required))}},{key:"_value",get:function(){var e,t;return void 0!==this.data?this.data:this.schema.required?void 0!==(null===(e=this.schema.description)||void 0===e?void 0:e.suggested_value)&&null!==(null===(t=this.schema.description)||void 0===t?void 0:t.suggested_value)||this.schema.default||this.schema.valueMin||0:this.schema.valueMin||0}},{key:"_handleCheckboxChange",value:function(e){var t;if(e.target.checked)for(var a=0,i=[this._lastValue,null===(o=this.schema.description)||void 0===o?void 0:o.suggested_value,this.schema.default,0];a<i.length;a++){var o,r=i[a];if(void 0!==r){t=r;break}}else this._lastValue=this.data;(0,c.r)(this,"value-changed",{value:t})}},{key:"_valueChanged",value:function(e){var t,a=e.target,i=a.value;if(""!==i&&(t=parseInt(String(i))),this.data!==t)(0,c.r)(this,"value-changed",{value:t});else{var o=void 0===t?"":String(t);a.value!==o&&(a.value=o)}}}])}(d.WF);y.styles=(0,d.AH)(g||(g=x`
    :host([own-margin]) {
      margin-bottom: 5px;
    }
    .flex {
      display: flex;
    }
    ha-slider {
      flex: 1;
    }
    ha-textfield {
      display: block;
    }
  `)),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"localize",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"schema",void 0),(0,s.__decorate)([(0,n.MZ)({attribute:!1})],y.prototype,"data",void 0),(0,s.__decorate)([(0,n.MZ)()],y.prototype,"label",void 0),(0,s.__decorate)([(0,n.MZ)()],y.prototype,"helper",void 0),(0,s.__decorate)([(0,n.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.P)("ha-textfield ha-slider")],y.prototype,"_input",void 0),y=(0,s.__decorate)([(0,n.EM)("ha-form-integer")],y),i()}catch(_){i(_)}}))},60808:function(e,t,a){a.a(e,(async function(e,t){try{var i=a(44734),o=a(56038),r=a(69683),h=a(6454),l=a(25460),s=(a(28706),a(62826)),d=a(60346),n=a(96196),c=a(77845),u=a(76679),v=e([d]);d=(v.then?(await v)():v)[0];var p,m=e=>e,f=function(e){function t(){var e;(0,i.A)(this,t);for(var a=arguments.length,o=new Array(a),h=0;h<a;h++)o[h]=arguments[h];return(e=(0,r.A)(this,t,[].concat(o))).size="small",e.withTooltip=!0,e}return(0,h.A)(t,e),(0,o.A)(t,[{key:"connectedCallback",value:function(){(0,l.A)(t,"connectedCallback",this,3)([]),this.dir=u.G.document.dir}}],[{key:"styles",get:function(){return[d.A.styles,(0,n.AH)(p||(p=m`
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
      `))]}}])}(d.A);(0,s.__decorate)([(0,c.MZ)({reflect:!0})],f.prototype,"size",void 0),(0,s.__decorate)([(0,c.MZ)({type:Boolean,attribute:"with-tooltip"})],f.prototype,"withTooltip",void 0),f=(0,s.__decorate)([(0,c.EM)("ha-slider")],f),t()}catch(b){t(b)}}))}}]);
//# sourceMappingURL=1364.d22e13ab5d066b82.js.map