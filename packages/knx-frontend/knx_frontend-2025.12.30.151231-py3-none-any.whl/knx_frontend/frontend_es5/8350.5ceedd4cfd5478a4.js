"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8350"],{68006:function(e,t,i){i.d(t,{z:function(){return a}});i(2892),i(26099),i(38781);var a=e=>{if(void 0!==e){if("object"!=typeof e){if("string"==typeof e||isNaN(e)){var t=(null==e?void 0:e.toString().split(":"))||[];if(1===t.length)return{seconds:Number(t[0])};if(t.length>3)return;var i=Number(t[2])||0,a=Math.floor(i);return{hours:Number(t[0])||0,minutes:Number(t[1])||0,seconds:a,milliseconds:Math.floor(1e3*Number((i-a).toFixed(4)))}}return{seconds:e}}if(!("days"in e))return e;var r=e.days,n=e.minutes,o=e.seconds,s=e.milliseconds,l=e.hours||0;return{hours:l=(l||0)+24*(r||0),minutes:n,seconds:o,milliseconds:s}}}},70524:function(e,t,i){var a,r=i(56038),n=i(44734),o=i(69683),s=i(6454),l=i(62826),d=i(69162),c=i(47191),u=i(96196),h=i(77845),f=function(e){function t(){return(0,n.A)(this,t),(0,o.A)(this,t,arguments)}return(0,s.A)(t,e),(0,r.A)(t)}(d.L);f.styles=[c.R,(0,u.AH)(a||(a=(e=>e)`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `))],f=(0,l.__decorate)([(0,h.EM)("ha-checkbox")],f)},33464:function(e,t,i){var a,r=i(44734),n=i(56038),o=i(69683),s=i(6454),l=(i(28706),i(2892),i(62826)),d=i(96196),c=i(77845),u=i(92542),h=(i(29261),e=>e),f=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,a=new Array(i),n=0;n<i;n++)a[n]=arguments[n];return(e=(0,o.A)(this,t,[].concat(a))).required=!1,e.enableMillisecond=!1,e.enableDay=!1,e.disabled=!1,e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){return(0,d.qy)(a||(a=h`
      <ha-base-time-input
        .label=${0}
        .helper=${0}
        .required=${0}
        .clearable=${0}
        .autoValidate=${0}
        .disabled=${0}
        errorMessage="Required"
        enable-second
        .enableMillisecond=${0}
        .enableDay=${0}
        format="24"
        .days=${0}
        .hours=${0}
        .minutes=${0}
        .seconds=${0}
        .milliseconds=${0}
        @value-changed=${0}
        no-hours-limit
        day-label="dd"
        hour-label="hh"
        min-label="mm"
        sec-label="ss"
        ms-label="ms"
      ></ha-base-time-input>
    `),this.label,this.helper,this.required,!this.required&&void 0!==this.data,this.required,this.disabled,this.enableMillisecond,this.enableDay,this._days,this._hours,this._minutes,this._seconds,this._milliseconds,this._durationChanged)}},{key:"_days",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.days?Number(this.data.days):this.required||this.data?0:NaN}},{key:"_hours",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.hours?Number(this.data.hours):this.required||this.data?0:NaN}},{key:"_minutes",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.minutes?Number(this.data.minutes):this.required||this.data?0:NaN}},{key:"_seconds",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.seconds?Number(this.data.seconds):this.required||this.data?0:NaN}},{key:"_milliseconds",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.milliseconds?Number(this.data.milliseconds):this.required||this.data?0:NaN}},{key:"_durationChanged",value:function(e){e.stopPropagation();var t,i=e.detail.value?Object.assign({},e.detail.value):void 0;i&&(i.hours||(i.hours=0),i.minutes||(i.minutes=0),i.seconds||(i.seconds=0),"days"in i&&(i.days||(i.days=0)),"milliseconds"in i&&(i.milliseconds||(i.milliseconds=0)),this.enableMillisecond||i.milliseconds?i.milliseconds>999&&(i.seconds+=Math.floor(i.milliseconds/1e3),i.milliseconds%=1e3):delete i.milliseconds,i.seconds>59&&(i.minutes+=Math.floor(i.seconds/60),i.seconds%=60),i.minutes>59&&(i.hours+=Math.floor(i.minutes/60),i.minutes%=60),this.enableDay&&i.hours>24&&(i.days=(null!==(t=i.days)&&void 0!==t?t:0)+Math.floor(i.hours/24),i.hours%=24));(0,u.r)(this,"value-changed",{value:i})}}])}(d.WF);(0,l.__decorate)([(0,c.MZ)({attribute:!1})],f.prototype,"data",void 0),(0,l.__decorate)([(0,c.MZ)()],f.prototype,"label",void 0),(0,l.__decorate)([(0,c.MZ)()],f.prototype,"helper",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:"enable-millisecond",type:Boolean})],f.prototype,"enableMillisecond",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:"enable-day",type:Boolean})],f.prototype,"enableDay",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],f.prototype,"disabled",void 0),f=(0,l.__decorate)([(0,c.EM)("ha-duration-input")],f)},48543:function(e,t,i){var a,r,n=i(44734),o=i(56038),s=i(69683),l=i(6454),d=(i(28706),i(62826)),c=i(35949),u=i(38627),h=i(96196),f=i(77845),m=i(94333),p=i(92542),g=e=>e,y=function(e){function t(){var e;(0,n.A)(this,t);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(e=(0,s.A)(this,t,[].concat(a))).disabled=!1,e}return(0,l.A)(t,e),(0,o.A)(t,[{key:"render",value:function(){var e={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return(0,h.qy)(a||(a=g` <div class="mdc-form-field ${0}">
      <slot></slot>
      <label class="mdc-label" @click=${0}>
        <slot name="label">${0}</slot>
      </label>
    </div>`),(0,m.H)(e),this._labelClick,this.label)}},{key:"_labelClick",value:function(){var e=this.input;if(e&&(e.focus(),!e.disabled))switch(e.tagName){case"HA-CHECKBOX":e.checked=!e.checked,(0,p.r)(e,"change");break;case"HA-RADIO":e.checked=!0,(0,p.r)(e,"change");break;default:e.click()}}}])}(c.M);y.styles=[u.R,(0,h.AH)(r||(r=g`
      :host(:not([alignEnd])) ::slotted(ha-switch) {
        margin-right: 10px;
        margin-inline-end: 10px;
        margin-inline-start: inline;
      }
      .mdc-form-field {
        align-items: var(--ha-formfield-align-items, center);
        gap: var(--ha-space-1);
      }
      .mdc-form-field > label {
        direction: var(--direction);
        margin-inline-start: 0;
        margin-inline-end: auto;
        padding: 0;
      }
      :host([disabled]) label {
        color: var(--disabled-text-color);
      }
    `))],(0,d.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],y.prototype,"disabled",void 0),y=(0,d.__decorate)([(0,f.EM)("ha-formfield")],y)},55421:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);var r=i(44734),n=i(56038),o=i(69683),s=i(6454),l=(i(28706),i(62826)),d=i(96196),c=i(77845),u=i(68006),h=i(92542),f=(i(70524),i(33464),i(48543),i(88867)),m=(i(78740),i(39396)),p=e([f]);f=(p.then?(await p)():p)[0];var g,y,v=e=>e,b=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,a=new Array(i),n=0;n<i;n++)a[n]=arguments[n];return(e=(0,o.A)(this,t,[].concat(a))).new=!1,e.disabled=!1,e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"item",set:function(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._duration=e.duration||"00:00:00",this._restore=e.restore||!1):(this._name="",this._icon="",this._duration="00:00:00",this._restore=!1),this._setDurationData()}},{key:"focus",value:function(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}},{key:"render",value:function(){return this.hass?(0,d.qy)(g||(g=v`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
          .disabled=${0}
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
          .disabled=${0}
        ></ha-icon-picker>
        <ha-duration-input
          .configValue=${0}
          .data=${0}
          @value-changed=${0}
          .disabled=${0}
        ></ha-duration-input>
        <ha-formfield
          .label=${0}
        >
          <ha-checkbox
            .configValue=${0}
            .checked=${0}
            @click=${0}
            .disabled=${0}
          >
          </ha-checkbox>
        </ha-formfield>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.disabled,this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this.disabled,"duration",this._duration_data,this._valueChanged,this.disabled,this.hass.localize("ui.dialogs.helper_settings.timer.restore"),"restore",this._restore,this._toggleRestore,this.disabled):d.s6}},{key:"_valueChanged",value:function(e){var t;if(this.new||this._item){e.stopPropagation();var i=e.target.configValue,a=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${i}`]!==a){var r=Object.assign({},this._item);a?r[i]=a:delete r[i],(0,h.r)(this,"value-changed",{value:r})}}}},{key:"_toggleRestore",value:function(){this.disabled||(this._restore=!this._restore,(0,h.r)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{restore:this._restore})}))}},{key:"_setDurationData",value:function(){var e;if("object"==typeof this._duration&&null!==this._duration){var t=this._duration;e={hours:"string"==typeof t.hours?parseFloat(t.hours):t.hours,minutes:"string"==typeof t.minutes?parseFloat(t.minutes):t.minutes,seconds:"string"==typeof t.seconds?parseFloat(t.seconds):t.seconds}}else e=this._duration;this._duration_data=(0,u.z)(e)}}],[{key:"styles",get:function(){return[m.RF,(0,d.AH)(y||(y=v`
        .form {
          color: var(--primary-text-color);
        }
        ha-textfield,
        ha-duration-input {
          display: block;
          margin: 8px 0;
        }
      `))]}}])}(d.WF);(0,l.__decorate)([(0,c.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],b.prototype,"new",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,l.__decorate)([(0,c.wk)()],b.prototype,"_name",void 0),(0,l.__decorate)([(0,c.wk)()],b.prototype,"_icon",void 0),(0,l.__decorate)([(0,c.wk)()],b.prototype,"_duration",void 0),(0,l.__decorate)([(0,c.wk)()],b.prototype,"_duration_data",void 0),(0,l.__decorate)([(0,c.wk)()],b.prototype,"_restore",void 0),b=(0,l.__decorate)([(0,c.EM)("ha-timer-form")],b),a()}catch(_){a(_)}}))},35949:function(e,t,i){i.d(t,{M:function(){return w}});var a,r=i(61397),n=i(50264),o=i(44734),s=i(56038),l=i(69683),d=i(6454),c=i(62826),u=i(7658),h={ROOT:"mdc-form-field"},f={LABEL_SELECTOR:".mdc-form-field > label"},m=function(e){function t(i){var a=e.call(this,(0,c.__assign)((0,c.__assign)({},t.defaultAdapter),i))||this;return a.click=function(){a.handleClick()},a}return(0,c.__extends)(t,e),Object.defineProperty(t,"cssClasses",{get:function(){return h},enumerable:!1,configurable:!0}),Object.defineProperty(t,"strings",{get:function(){return f},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{activateInputRipple:function(){},deactivateInputRipple:function(){},deregisterInteractionHandler:function(){},registerInteractionHandler:function(){}}},enumerable:!1,configurable:!0}),t.prototype.init=function(){this.adapter.registerInteractionHandler("click",this.click)},t.prototype.destroy=function(){this.adapter.deregisterInteractionHandler("click",this.click)},t.prototype.handleClick=function(){var e=this;this.adapter.activateInputRipple(),requestAnimationFrame((function(){e.adapter.deactivateInputRipple()}))},t}(u.I),p=i(12451),g=i(51324),y=i(56161),v=i(96196),b=i(77845),_=i(94333),k=e=>e,w=function(e){function t(){var e;return(0,o.A)(this,t),(e=(0,l.A)(this,t,arguments)).alignEnd=!1,e.spaceBetween=!1,e.nowrap=!1,e.label="",e.mdcFoundationClass=m,e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"createAdapter",value:function(){var e,t,i=this;return{registerInteractionHandler:(e,t)=>{this.labelEl.addEventListener(e,t)},deregisterInteractionHandler:(e,t)=>{this.labelEl.removeEventListener(e,t)},activateInputRipple:(t=(0,n.A)((0,r.A)().m((function e(){var t,a;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:if(!((t=i.input)instanceof g.ZS)){e.n=2;break}return e.n=1,t.ripple;case 1:(a=e.v)&&a.startPress();case 2:return e.a(2)}}),e)}))),function(){return t.apply(this,arguments)}),deactivateInputRipple:(e=(0,n.A)((0,r.A)().m((function e(){var t,a;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:if(!((t=i.input)instanceof g.ZS)){e.n=2;break}return e.n=1,t.ripple;case 1:(a=e.v)&&a.endPress();case 2:return e.a(2)}}),e)}))),function(){return e.apply(this,arguments)})}}},{key:"input",get:function(){var e,t;return null!==(t=null===(e=this.slottedInputs)||void 0===e?void 0:e[0])&&void 0!==t?t:null}},{key:"render",value:function(){var e={"mdc-form-field--align-end":this.alignEnd,"mdc-form-field--space-between":this.spaceBetween,"mdc-form-field--nowrap":this.nowrap};return(0,v.qy)(a||(a=k`
      <div class="mdc-form-field ${0}">
        <slot></slot>
        <label class="mdc-label"
               @click="${0}">${0}</label>
      </div>`),(0,_.H)(e),this._labelClick,this.label)}},{key:"click",value:function(){this._labelClick()}},{key:"_labelClick",value:function(){var e=this.input;e&&(e.focus(),e.click())}}])}(p.O);(0,c.__decorate)([(0,b.MZ)({type:Boolean})],w.prototype,"alignEnd",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],w.prototype,"spaceBetween",void 0),(0,c.__decorate)([(0,b.MZ)({type:Boolean})],w.prototype,"nowrap",void 0),(0,c.__decorate)([(0,b.MZ)({type:String}),(0,y.P)(function(){var e=(0,n.A)((0,r.A)().m((function e(t){var i;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:null===(i=this.input)||void 0===i||i.setAttribute("aria-label",t);case 1:return e.a(2)}}),e,this)})));return function(t){return e.apply(this,arguments)}}())],w.prototype,"label",void 0),(0,c.__decorate)([(0,b.P)(".mdc-form-field")],w.prototype,"mdcRoot",void 0),(0,c.__decorate)([(0,b.KN)({slot:"",flatten:!0,selector:"*"})],w.prototype,"slottedInputs",void 0),(0,c.__decorate)([(0,b.P)("label")],w.prototype,"labelEl",void 0)},38627:function(e,t,i){i.d(t,{R:function(){return r}});var a,r=(0,i(96196).AH)(a||(a=(e=>e)`.mdc-form-field{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87));display:inline-flex;align-items:center;vertical-align:middle}.mdc-form-field>label{margin-left:0;margin-right:auto;padding-left:4px;padding-right:0;order:0}[dir=rtl] .mdc-form-field>label,.mdc-form-field>label[dir=rtl]{margin-left:auto;margin-right:0}[dir=rtl] .mdc-form-field>label,.mdc-form-field>label[dir=rtl]{padding-left:0;padding-right:4px}.mdc-form-field--nowrap>label{text-overflow:ellipsis;overflow:hidden;white-space:nowrap}.mdc-form-field--align-end>label{margin-left:auto;margin-right:0;padding-left:0;padding-right:4px;order:-1}[dir=rtl] .mdc-form-field--align-end>label,.mdc-form-field--align-end>label[dir=rtl]{margin-left:0;margin-right:auto}[dir=rtl] .mdc-form-field--align-end>label,.mdc-form-field--align-end>label[dir=rtl]{padding-left:4px;padding-right:0}.mdc-form-field--space-between{justify-content:space-between}.mdc-form-field--space-between>label{margin:0}[dir=rtl] .mdc-form-field--space-between>label,.mdc-form-field--space-between>label[dir=rtl]{margin:0}:host{display:inline-flex}.mdc-form-field{width:100%}::slotted(*){-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;font-family:Roboto, sans-serif;font-family:var(--mdc-typography-body2-font-family, var(--mdc-typography-font-family, Roboto, sans-serif));font-size:0.875rem;font-size:var(--mdc-typography-body2-font-size, 0.875rem);line-height:1.25rem;line-height:var(--mdc-typography-body2-line-height, 1.25rem);font-weight:400;font-weight:var(--mdc-typography-body2-font-weight, 400);letter-spacing:0.0178571429em;letter-spacing:var(--mdc-typography-body2-letter-spacing, 0.0178571429em);text-decoration:inherit;text-decoration:var(--mdc-typography-body2-text-decoration, inherit);text-transform:inherit;text-transform:var(--mdc-typography-body2-text-transform, inherit);color:rgba(0, 0, 0, 0.87);color:var(--mdc-theme-text-primary-on-background, rgba(0, 0, 0, 0.87))}::slotted(mwc-switch){margin-right:10px}[dir=rtl] ::slotted(mwc-switch),::slotted(mwc-switch[dir=rtl]){margin-left:10px}`))}}]);
//# sourceMappingURL=8350.5ceedd4cfd5478a4.js.map