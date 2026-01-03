"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8881"],{95096:function(e,t,i){i.a(e,(async function(e,r){try{i.r(t),i.d(t,{HaNumberSelector:function(){return _}});var a=i(44734),o=i(56038),l=i(69683),n=i(6454),s=(i(28706),i(2892),i(26099),i(38781),i(62826)),d=i(96196),h=i(77845),u=i(94333),c=i(92542),v=(i(56768),i(60808)),p=(i(78740),e([v]));v=(p.then?(await p)():p)[0];var b,m,f,y,x,g=e=>e,_=function(e){function t(){var e;(0,a.A)(this,t);for(var i=arguments.length,r=new Array(i),o=0;o<i;o++)r[o]=arguments[o];return(e=(0,l.A)(this,t,[].concat(r))).required=!0,e.disabled=!1,e._valueStr="",e}return(0,n.A)(t,e),(0,o.A)(t,[{key:"willUpdate",value:function(e){e.has("value")&&(""!==this._valueStr&&this.value===Number(this._valueStr)||(this._valueStr=null==this.value||isNaN(this.value)?"":this.value.toString()))}},{key:"render",value:function(){var e,t,i,r,a,o,l,n,s,h,c,v,p,x,_,w,$="box"===(null===(e=this.selector.number)||void 0===e?void 0:e.mode)||void 0===(null===(t=this.selector.number)||void 0===t?void 0:t.min)||void 0===(null===(i=this.selector.number)||void 0===i?void 0:i.max);if(!$&&"any"===(_=null!==(w=this.selector.number.step)&&void 0!==w?w:1)){_=1;for(var k=(this.selector.number.max-this.selector.number.min)/100;_>k;)_/=10}var z=null===(r=this.selector.number)||void 0===r?void 0:r.translation_key,A=null===(a=this.selector.number)||void 0===a?void 0:a.unit_of_measurement;return $&&A&&this.localizeValue&&z&&(A=this.localizeValue(`${z}.unit_of_measurement.${A}`)||A),(0,d.qy)(b||(b=g`
      ${0}
      <div class="input">
        ${0}
        <ha-textfield
          .inputMode=${0}
          .label=${0}
          .placeholder=${0}
          class=${0}
          .min=${0}
          .max=${0}
          .value=${0}
          .step=${0}
          helperPersistent
          .helper=${0}
          .disabled=${0}
          .required=${0}
          .suffix=${0}
          type="number"
          autoValidate
          ?no-spinner=${0}
          @input=${0}
        >
        </ha-textfield>
      </div>
      ${0}
    `),this.label&&!$?(0,d.qy)(m||(m=g`${0}${0}`),this.label,this.required?"*":""):d.s6,$?d.s6:(0,d.qy)(f||(f=g`
              <ha-slider
                labeled
                .min=${0}
                .max=${0}
                .value=${0}
                .step=${0}
                .disabled=${0}
                .required=${0}
                @change=${0}
                .withMarkers=${0}
              >
              </ha-slider>
            `),this.selector.number.min,this.selector.number.max,this.value,_,this.disabled,this.required,this._handleSliderChange,(null===(o=this.selector.number)||void 0===o?void 0:o.slider_ticks)||!1),"any"===(null===(l=this.selector.number)||void 0===l?void 0:l.step)||(null!==(n=null===(s=this.selector.number)||void 0===s?void 0:s.step)&&void 0!==n?n:1)%1!=0?"decimal":"numeric",$?this.label:void 0,this.placeholder,(0,u.H)({single:$}),null===(h=this.selector.number)||void 0===h?void 0:h.min,null===(c=this.selector.number)||void 0===c?void 0:c.max,null!==(v=this._valueStr)&&void 0!==v?v:"",null!==(p=null===(x=this.selector.number)||void 0===x?void 0:x.step)&&void 0!==p?p:1,$?this.helper:void 0,this.disabled,this.required,A,!$,this._handleInputChange,!$&&this.helper?(0,d.qy)(y||(y=g`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):d.s6)}},{key:"_handleInputChange",value:function(e){e.stopPropagation(),this._valueStr=e.target.value;var t=""===e.target.value||isNaN(e.target.value)?void 0:Number(e.target.value);this.value!==t&&(0,c.r)(this,"value-changed",{value:t})}},{key:"_handleSliderChange",value:function(e){e.stopPropagation();var t=Number(e.target.value);this.value!==t&&(0,c.r)(this,"value-changed",{value:t})}}])}(d.WF);_.styles=(0,d.AH)(x||(x=g`
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
  `)),(0,s.__decorate)([(0,h.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,s.__decorate)([(0,h.MZ)({attribute:!1})],_.prototype,"selector",void 0),(0,s.__decorate)([(0,h.MZ)({type:Number})],_.prototype,"value",void 0),(0,s.__decorate)([(0,h.MZ)({type:Number})],_.prototype,"placeholder",void 0),(0,s.__decorate)([(0,h.MZ)()],_.prototype,"label",void 0),(0,s.__decorate)([(0,h.MZ)()],_.prototype,"helper",void 0),(0,s.__decorate)([(0,h.MZ)({attribute:!1})],_.prototype,"localizeValue",void 0),(0,s.__decorate)([(0,h.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,s.__decorate)([(0,h.MZ)({type:Boolean})],_.prototype,"disabled",void 0),_=(0,s.__decorate)([(0,h.EM)("ha-selector-number")],_),r()}catch(w){r(w)}}))},60808:function(e,t,i){i.a(e,(async function(e,t){try{var r=i(44734),a=i(56038),o=i(69683),l=i(6454),n=i(25460),s=(i(28706),i(62826)),d=i(60346),h=i(96196),u=i(77845),c=i(76679),v=e([d]);d=(v.then?(await v)():v)[0];var p,b=e=>e,m=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,a=new Array(i),l=0;l<i;l++)a[l]=arguments[l];return(e=(0,o.A)(this,t,[].concat(a))).size="small",e.withTooltip=!0,e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"connectedCallback",value:function(){(0,n.A)(t,"connectedCallback",this,3)([]),this.dir=c.G.document.dir}}],[{key:"styles",get:function(){return[d.A.styles,(0,h.AH)(p||(p=b`
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
      `))]}}])}(d.A);(0,s.__decorate)([(0,u.MZ)({reflect:!0})],m.prototype,"size",void 0),(0,s.__decorate)([(0,u.MZ)({type:Boolean,attribute:"with-tooltip"})],m.prototype,"withTooltip",void 0),m=(0,s.__decorate)([(0,u.EM)("ha-slider")],m),t()}catch(f){t(f)}}))}}]);
//# sourceMappingURL=8881.47d1ee6f7548821e.js.map