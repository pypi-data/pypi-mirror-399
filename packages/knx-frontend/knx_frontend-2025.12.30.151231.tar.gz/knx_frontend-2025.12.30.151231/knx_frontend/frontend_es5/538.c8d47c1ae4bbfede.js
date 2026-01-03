/*! For license information please see 538.c8d47c1ae4bbfede.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["538"],{23608:function(e,t,n){n.d(t,{PN:function(){return r},jm:function(){return a},sR:function(){return s},t1:function(){return i},t2:function(){return d},yu:function(){return l}});var o={"HA-Frontend-Base":`${location.protocol}//${location.host}`},i=(e,t,n)=>{var i;return e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(null===(i=e.userData)||void 0===i?void 0:i.showAdvanced),entry_id:n},o)},r=(e,t)=>e.callApi("GET",`config/config_entries/flow/${t}`,void 0,o),a=(e,t,n)=>e.callApi("POST",`config/config_entries/flow/${t}`,n,o),s=(e,t)=>e.callApi("DELETE",`config/config_entries/flow/${t}`),l=(e,t)=>e.callApi("GET","config/config_entries/flow_handlers"+(t?`?type=${t}`:"")),d=e=>e.sendMessagePromise({type:"config_entries/flow/progress"})},73042:function(e,t,n){n.d(t,{W:function(){return w}});var o,i,r,a,s,l,d,c,p,h=n(61397),u=n(78261),m=n(50264),f=(n(52675),n(89463),n(23792),n(26099),n(3362),n(62953),n(96196)),g=n(23608),v=n(84125),y=n(73347),_=e=>e,w=(e,t)=>{return(0,y.g)(e,t,{flowType:"config_flow",showDevices:!0,createFlow:(w=(0,m.A)((0,h.A)().m((function e(n,o){var i,r,a;return(0,h.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,Promise.all([(0,g.t1)(n,o,t.entryId),n.loadFragmentTranslation("config"),n.loadBackendTranslation("config",o),n.loadBackendTranslation("selector",o),n.loadBackendTranslation("title",o)]);case 1:return i=e.v,r=(0,u.A)(i,1),a=r[0],e.a(2,a)}}),e)}))),function(e,t){return w.apply(this,arguments)}),fetchFlow:(n=(0,m.A)((0,h.A)().m((function e(t,n){var o,i,r;return(0,h.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,Promise.all([(0,g.PN)(t,n),t.loadFragmentTranslation("config")]);case 1:return o=e.v,i=(0,u.A)(o,1),r=i[0],e.n=2,Promise.all([t.loadBackendTranslation("config",r.handler),t.loadBackendTranslation("selector",r.handler),t.loadBackendTranslation("title",r.handler)]);case 2:return e.a(2,r)}}),e)}))),function(e,t){return n.apply(this,arguments)}),handleFlowStep:g.jm,deleteFlow:g.sR,renderAbortDescription(e,t){var n=e.localize(`component.${t.translation_domain||t.handler}.config.abort.${t.reason}`,t.description_placeholders);return n?(0,f.qy)(o||(o=_`
            <ha-markdown allow-svg breaks .content=${0}></ha-markdown>
          `),n):t.reason},renderShowFormStepHeader(e,t){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.title`,t.description_placeholders)||e.localize(`component.${t.handler}.title`)},renderShowFormStepDescription(e,t){var n=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return n?(0,f.qy)(i||(i=_`
            <ha-markdown
              .allowDataUrl=${0}
              allow-svg
              breaks
              .content=${0}
            ></ha-markdown>
          `),"zwave_js"===t.handler,n):""},renderShowFormStepFieldLabel(e,t,n,o){var i;if("expandable"===n.type)return e.localize(`component.${t.handler}.config.step.${t.step_id}.sections.${n.name}.name`,t.description_placeholders);var r=null!=o&&null!==(i=o.path)&&void 0!==i&&i[0]?`sections.${o.path[0]}.`:"";return e.localize(`component.${t.handler}.config.step.${t.step_id}.${r}data.${n.name}`,t.description_placeholders)||n.name},renderShowFormStepFieldHelper(e,t,n,o){var i;if("expandable"===n.type)return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.sections.${n.name}.description`,t.description_placeholders);var a=null!=o&&null!==(i=o.path)&&void 0!==i&&i[0]?`sections.${o.path[0]}.`:"",s=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.${a}data_description.${n.name}`,t.description_placeholders);return s?(0,f.qy)(r||(r=_`<ha-markdown breaks .content=${0}></ha-markdown>`),s):""},renderShowFormStepFieldError(e,t,n){return e.localize(`component.${t.translation_domain||t.translation_domain||t.handler}.config.error.${n}`,t.description_placeholders)||n},renderShowFormStepFieldLocalizeValue(e,t,n){return e.localize(`component.${t.handler}.selector.${n}`)},renderShowFormStepSubmitButton(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===t.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,t){var n=e.localize(`component.${t.translation_domain||t.handler}.config.${t.step_id}.description`,t.description_placeholders);return(0,f.qy)(a||(a=_`
        <p>
          ${0}
        </p>
        ${0}
      `),e.localize("ui.panel.config.integrations.config_flow.external_step.description"),n?(0,f.qy)(s||(s=_`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),n):"")},renderCreateEntryDescription(e,t){var n=e.localize(`component.${t.translation_domain||t.handler}.config.create_entry.${t.description||"default"}`,t.description_placeholders);return(0,f.qy)(l||(l=_`
        ${0}
      `),n?(0,f.qy)(d||(d=_`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),n):f.s6)},renderShowFormProgressHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderShowFormProgressDescription(e,t){var n=e.localize(`component.${t.translation_domain||t.handler}.config.progress.${t.progress_action}`,t.description_placeholders);return n?(0,f.qy)(c||(c=_`
            <ha-markdown allow-svg breaks .content=${0}></ha-markdown>
          `),n):""},renderMenuHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderMenuDescription(e,t){var n=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return n?(0,f.qy)(p||(p=_`
            <ha-markdown allow-svg breaks .content=${0}></ha-markdown>
          `),n):""},renderMenuOption(e,t,n){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_options.${n}`,t.description_placeholders)},renderMenuOptionDescription(e,t,n){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_option_descriptions.${n}`,t.description_placeholders)},renderLoadingDescription(e,t,n,o){if("loading_flow"!==t&&"loading_step"!==t)return"";var i=(null==o?void 0:o.handler)||n;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:i?(0,v.p$)(e.localize,i):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}});var n,w}},73347:function(e,t,n){n.d(t,{g:function(){return r}});n(23792),n(26099),n(3362),n(62953);var o=n(92542),i=()=>Promise.all([n.e("9807"),n.e("1779"),n.e("6009"),n.e("8506"),n.e("4533"),n.e("7770"),n.e("9745"),n.e("113"),n.e("131"),n.e("2769"),n.e("5206"),n.e("3591"),n.e("7163"),n.e("4493"),n.e("4545"),n.e("8061"),n.e("7394")]).then(n.bind(n,90313)),r=(e,t,n)=>{(0,o.r)(e,"show-dialog",{dialogTag:"dialog-data-entry-flow",dialogImport:i,dialogParams:Object.assign(Object.assign({},t),{},{flowConfig:n,dialogParentElement:e})})}},35804:function(e,t,n){n.d(t,{Q:function(){return w}});var o,i,r,a,s,l,d=n(61397),c=n(78261),p=n(50264),h=(n(23792),n(26099),n(3362),n(62953),n(96196)),u=n(84125),m=(e,t)=>{var n;return e.callApi("POST","config/config_entries/options/flow",{handler:t,show_advanced_options:Boolean(null===(n=e.userData)||void 0===n?void 0:n.showAdvanced)})},f=(e,t)=>e.callApi("GET",`config/config_entries/options/flow/${t}`),g=(e,t,n)=>e.callApi("POST",`config/config_entries/options/flow/${t}`,n),v=(e,t)=>e.callApi("DELETE",`config/config_entries/options/flow/${t}`),y=n(73347),_=e=>e,w=(e,t,n)=>{return(0,y.g)(e,Object.assign({startFlowHandler:t.entry_id,domain:t.domain},n),{flowType:"options_flow",showDevices:!1,createFlow:(b=(0,p.A)((0,d.A)().m((function e(n,o){var i,r,a;return(0,d.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,Promise.all([m(n,o),n.loadFragmentTranslation("config"),n.loadBackendTranslation("options",t.domain),n.loadBackendTranslation("selector",t.domain)]);case 1:return i=e.v,r=(0,c.A)(i,1),a=r[0],e.a(2,a)}}),e)}))),function(e,t){return b.apply(this,arguments)}),fetchFlow:(w=(0,p.A)((0,d.A)().m((function e(n,o){var i,r,a;return(0,d.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,Promise.all([f(n,o),n.loadFragmentTranslation("config"),n.loadBackendTranslation("options",t.domain),n.loadBackendTranslation("selector",t.domain)]);case 1:return i=e.v,r=(0,c.A)(i,1),a=r[0],e.a(2,a)}}),e)}))),function(e,t){return w.apply(this,arguments)}),handleFlowStep:g,deleteFlow:v,renderAbortDescription(e,n){var i=e.localize(`component.${n.translation_domain||t.domain}.options.abort.${n.reason}`,n.description_placeholders);return i?(0,h.qy)(o||(o=_`
              <ha-markdown
                breaks
                allow-svg
                .content=${0}
              ></ha-markdown>
            `),i):n.reason},renderShowFormStepHeader(e,n){return e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.title`,n.description_placeholders)||e.localize("ui.dialogs.options_flow.form.header")},renderShowFormStepDescription(e,n){var o=e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.description`,n.description_placeholders);return o?(0,h.qy)(i||(i=_`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),o):""},renderShowFormStepFieldLabel(e,n,o,i){var r;if("expandable"===o.type)return e.localize(`component.${t.domain}.options.step.${n.step_id}.sections.${o.name}.name`,n.description_placeholders);var a=null!=i&&null!==(r=i.path)&&void 0!==r&&r[0]?`sections.${i.path[0]}.`:"";return e.localize(`component.${t.domain}.options.step.${n.step_id}.${a}data.${o.name}`,n.description_placeholders)||o.name},renderShowFormStepFieldHelper(e,n,o,i){var a;if("expandable"===o.type)return e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.sections.${o.name}.description`,n.description_placeholders);var s=null!=i&&null!==(a=i.path)&&void 0!==a&&a[0]?`sections.${i.path[0]}.`:"",l=e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.${s}data_description.${o.name}`,n.description_placeholders);return l?(0,h.qy)(r||(r=_`<ha-markdown breaks .content=${0}></ha-markdown>`),l):""},renderShowFormStepFieldError(e,n,o){return e.localize(`component.${n.translation_domain||t.domain}.options.error.${o}`,n.description_placeholders)||o},renderShowFormStepFieldLocalizeValue(e,n,o){return e.localize(`component.${t.domain}.selector.${o}`)},renderShowFormStepSubmitButton(e,n){return e.localize(`component.${t.domain}.options.step.${n.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===n.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return""},renderExternalStepDescription(e,t){return""},renderCreateEntryDescription(e,t){return(0,h.qy)(a||(a=_`
          <p>${0}</p>
        `),e.localize("ui.dialogs.options_flow.success.description"))},renderShowFormProgressHeader(e,n){return e.localize(`component.${t.domain}.options.step.${n.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderShowFormProgressDescription(e,n){var o=e.localize(`component.${n.translation_domain||t.domain}.options.progress.${n.progress_action}`,n.description_placeholders);return o?(0,h.qy)(s||(s=_`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),o):""},renderMenuHeader(e,n){return e.localize(`component.${t.domain}.options.step.${n.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderMenuDescription(e,n){var o=e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.description`,n.description_placeholders);return o?(0,h.qy)(l||(l=_`
              <ha-markdown
                allow-svg
                breaks
                .content=${0}
              ></ha-markdown>
            `),o):""},renderMenuOption(e,n,o){return e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.menu_options.${o}`,n.description_placeholders)},renderMenuOptionDescription(e,n,o){return e.localize(`component.${n.translation_domain||t.domain}.options.step.${n.step_id}.menu_option_descriptions.${o}`,n.description_placeholders)},renderLoadingDescription(e,n){return e.localize(`component.${t.domain}.options.loading`)||("loading_flow"===n||"loading_step"===n?e.localize(`ui.dialogs.options_flow.loading.${n}`,{integration:(0,u.p$)(e.localize,t.domain)}):"")}});var w,b}},10085:function(e,t,n){n.d(t,{E:function(){return p}});var o=n(31432),i=n(44734),r=n(56038),a=n(69683),s=n(25460),l=n(6454),d=(n(74423),n(23792),n(18111),n(13579),n(26099),n(3362),n(62953),n(62826)),c=n(77845),p=e=>{var t=function(e){function t(){return(0,i.A)(this,t),(0,a.A)(this,t,arguments)}return(0,l.A)(t,e),(0,r.A)(t,[{key:"connectedCallback",value:function(){(0,s.A)(t,"connectedCallback",this,3)([]),this._checkSubscribed()}},{key:"disconnectedCallback",value:function(){if((0,s.A)(t,"disconnectedCallback",this,3)([]),this.__unsubs){for(;this.__unsubs.length;){var e=this.__unsubs.pop();e instanceof Promise?e.then((e=>e())):e()}this.__unsubs=void 0}}},{key:"updated",value:function(e){if((0,s.A)(t,"updated",this,3)([e]),e.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps){var n,i=(0,o.A)(e.keys());try{for(i.s();!(n=i.n()).done;){var r=n.value;if(this.hassSubscribeRequiredHostProps.includes(r))return void this._checkSubscribed()}}catch(a){i.e(a)}finally{i.f()}}}},{key:"hassSubscribe",value:function(){return[]}},{key:"_checkSubscribed",value:function(){var e;void 0!==this.__unsubs||!this.isConnected||void 0===this.hass||null!==(e=this.hassSubscribeRequiredHostProps)&&void 0!==e&&e.some((e=>void 0===this[e]))||(this.__unsubs=this.hassSubscribe())}}])}(e);return(0,d.__decorate)([(0,c.MZ)({attribute:!1})],t.prototype,"hass",void 0),t}},2551:function(e,t,n){n.r(t),n.d(t,{KnxDashboard:function(){return M}});var o=n(61397),i=n(50264),r=n(44734),a=n(56038),s=n(69683),l=n(6454),d=(n(52675),n(89463),n(28706),n(50113),n(23792),n(62062),n(18111),n(20116),n(61701),n(26099),n(31415),n(17642),n(58004),n(33853),n(45876),n(32475),n(15024),n(31698),n(62953),n(62826)),c=n(96196),p=n(77845),h=n(31432),u=(0,o.A)().m(m);function m(e,t){var n,i,r,a,s;return(0,o.A)().w((function(o){for(;;)switch(o.p=o.n){case 0:if(void 0===e){o.n=7;break}n=0,i=(0,h.A)(e),o.p=1,i.s();case 2:if((r=i.n()).done){o.n=4;break}return a=r.value,o.n=3,t(a,n++);case 3:o.n=2;break;case 4:o.n=6;break;case 5:o.p=5,s=o.v,i.e(s);case 6:return o.p=6,i.f(),o.f(6);case 7:return o.a(2)}}),u,null,[[1,5,6,7]])}var f,g,v=n(10085),y=n(92542),_=(n(95379),n(42921),n(23897),n(65300),n(84125)),w=(n(29937),n(94333)),b=e=>e,$=function(e){function t(){var e;(0,r.A)(this,t);for(var n=arguments.length,o=new Array(n),i=0;i<n;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).isWide=!1,e.vertical=!1,e.fullWidth=!1,e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"render",value:function(){return(0,c.qy)(f||(f=b`
      <div
        class="content ${0}"
      >
        <div class="header"><slot name="header"></slot></div>
        <div
          class="together layout ${0}"
        >
          <div class="intro"><slot name="introduction"></slot></div>
          <div class="panel flex-auto"><slot></slot></div>
        </div>
      </div>
    `),(0,w.H)({narrow:!this.isWide,"full-width":this.fullWidth}),(0,w.H)({narrow:!this.isWide,vertical:this.vertical||!this.isWide,horizontal:!this.vertical&&this.isWide}))}}])}(c.WF);$.styles=(0,c.AH)(g||(g=b`
    :host {
      display: block;
    }

    .content {
      padding: 28px 20px 0;
      max-width: 1040px;
      margin: 0 auto;
    }

    .layout {
      display: flex;
    }

    .horizontal {
      flex-direction: row;
    }

    .vertical {
      flex-direction: column;
    }

    .flex-auto {
      flex: 1 1 auto;
    }

    .header {
      font-family: var(--ha-font-family-body);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-size: var(--ha-font-size-2xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      opacity: var(--dark-primary-opacity);
    }

    .together {
      margin-top: var(--config-section-content-together-margin-top, 32px);
    }

    .intro {
      font-family: var(--ha-font-family-body);
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-normal);
      width: 100%;
      opacity: var(--dark-primary-opacity);
      font-size: var(--ha-font-size-m);
      padding-bottom: 20px;
    }

    .horizontal .intro {
      max-width: 400px;
      margin-right: 40px;
      margin-inline-end: 40px;
      margin-inline-start: initial;
    }

    .panel {
      margin-top: -24px;
    }

    .panel ::slotted(*) {
      margin-top: 24px;
      display: block;
    }

    .narrow.content {
      max-width: 640px;
    }
    .narrow .together {
      margin-top: var(
        --config-section-narrow-content-together-margin-top,
        var(--config-section-content-together-margin-top, 20px)
      );
    }
    .narrow .intro {
      padding-bottom: 20px;
      margin-right: 0;
      margin-inline-end: 0;
      margin-inline-start: initial;
      max-width: 500px;
    }

    .full-width {
      padding: 0;
    }

    .full-width .layout {
      flex-direction: column;
    }
  `)),(0,d.__decorate)([(0,p.MZ)({attribute:"is-wide",type:Boolean})],$.prototype,"isWide",void 0),(0,d.__decorate)([(0,p.MZ)({type:Boolean})],$.prototype,"vertical",void 0),(0,d.__decorate)([(0,p.MZ)({type:Boolean,attribute:"full-width"})],$.prototype,"fullWidth",void 0),$=(0,d.__decorate)([(0,p.EM)("ha-config-section")],$);var k,x,A,z=n(73042),C=n(35804),S=n(3950),F=(n(3362),()=>Promise.all([n.e("9807"),n.e("1779"),n.e("6009"),n.e("8506"),n.e("4533"),n.e("6919"),n.e("113"),n.e("5206"),n.e("2993"),n.e("6563"),n.e("8195")]).then(n.bind(n,21199))),L=n(16404),H=n(78577),P=e=>e,E=new H.Q("knx-dashboard"),M=function(e){function t(){var e;(0,r.A)(this,t);for(var n=arguments.length,o=new Array(n),i=0;i<n;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).narrow=!1,e.isWide=!1,e._configEntryState="unknown",e._buttonItems=[{translationKey:"component.knx.config_panel.dashboard.options_flow",iconPath:"M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8M12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12A2,2 0 0,0 12,10M10,22C9.75,22 9.54,21.82 9.5,21.58L9.13,18.93C8.5,18.68 7.96,18.34 7.44,17.94L4.95,18.95C4.73,19.03 4.46,18.95 4.34,18.73L2.34,15.27C2.21,15.05 2.27,14.78 2.46,14.63L4.57,12.97L4.5,12L4.57,11L2.46,9.37C2.27,9.22 2.21,8.95 2.34,8.73L4.34,5.27C4.46,5.05 4.73,4.96 4.95,5.05L7.44,6.05C7.96,5.66 8.5,5.32 9.13,5.07L9.5,2.42C9.54,2.18 9.75,2 10,2H14C14.25,2 14.46,2.18 14.5,2.42L14.87,5.07C15.5,5.32 16.04,5.66 16.56,6.05L19.05,5.05C19.27,4.96 19.54,5.05 19.66,5.27L21.66,8.73C21.79,8.95 21.73,9.22 21.54,9.37L19.43,11L19.5,12L19.43,13L21.54,14.63C21.73,14.78 21.79,15.05 21.66,15.27L19.66,18.73C19.54,18.95 19.27,19.04 19.05,18.95L16.56,17.95C16.04,18.34 15.5,18.68 14.87,18.93L14.5,21.58C14.46,21.82 14.25,22 14,22H10M11.25,4L10.88,6.61C9.68,6.86 8.62,7.5 7.85,8.39L5.44,7.35L4.69,8.65L6.8,10.2C6.4,11.37 6.4,12.64 6.8,13.8L4.68,15.36L5.43,16.66L7.86,15.62C8.63,16.5 9.68,17.14 10.87,17.38L11.24,20H12.76L13.13,17.39C14.32,17.14 15.37,16.5 16.14,15.62L18.57,16.66L19.32,15.36L17.2,13.81C17.6,12.64 17.6,11.37 17.2,10.2L19.31,8.65L18.56,7.35L16.15,8.39C15.38,7.5 14.32,6.86 13.12,6.62L12.75,4H11.25Z",iconColor:"var(--indigo-color)",click:e._openOptionFlow,validConfigEntryStates:new Set(["loaded"])},{translationKey:"component.knx.config_panel.dashboard.project_upload",click:e._openProjectUploadDialog,iconPath:"M14 2H6C4.89 2 4 2.9 4 4V20C4 21.11 4.89 22 6 22H18C19.11 22 20 21.11 20 20V8L14 2M18 20H6V4H13V9H18V20M15 11.93V19H7.93L10.05 16.88L7.22 14.05L10.05 11.22L12.88 14.05L15 11.93Z",iconColor:"var(--orange-color)",validConfigEntryStates:new Set(["loaded"])},{translationKey:"component.knx.config_panel.dashboard.connection_flow",iconPath:"M4,1C2.89,1 2,1.89 2,3V7C2,8.11 2.89,9 4,9H1V11H13V9H10C11.11,9 12,8.11 12,7V3C12,1.89 11.11,1 10,1H4M4,3H10V7H4V3M3,13V18L3,20H10V18H5V13H3M14,13C12.89,13 12,13.89 12,15V19C12,20.11 12.89,21 14,21H11V23H23V21H20C21.11,21 22,20.11 22,19V15C22,13.89 21.11,13 20,13H14M14,15H20V19H14V15Z",iconColor:"var(--cyan-color)",click:e._openReconfigureFlow,validConfigEntryStates:new Set(["loaded","not_loaded"])}],e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"hassSubscribe",value:function(){return[this._unsubscribeConfigEntries()]}},{key:"_unsubscribeConfigEntries",value:function(){var e=this,t=(0,S.TC)(this.hass,function(){var t=(0,i.A)((0,o.A)().m((function t(n){var i,r;return(0,o.A)().w((function(t){for(;;)switch(t.n){case 0:(r=null===(i=n.find((e=>"knx"===e.entry.domain)))||void 0===i?void 0:i.entry.state)&&r!==e._configEntryState&&(E.debug("KNX dashboard config entry state update",r),e._configEntryState=r);case 1:return t.a(2)}}),t)})));return function(e){return t.apply(this,arguments)}}(),{domain:"knx"});return()=>{t.then((e=>e()))}}},{key:"_getPages",value:function(){return(0,L.rN)(!!this.knx.projectInfo).map((e=>Object.assign(Object.assign({},e),{},{name:this.hass.localize(e.translationKey)||e.name,description:this.hass.localize(e.descriptionTranslationKey)||e.description})))}},{key:"_openOptionFlow",value:(d=(0,i.A)((0,o.A)().m((function e(){return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:(0,C.Q)(this,this.knx.config_entry);case 1:return e.a(2)}}),e,this)}))),function(){return d.apply(this,arguments)})},{key:"_openProjectUploadDialog",value:function(){var e;e=this,(0,y.r)(e,"show-dialog",{dialogTag:"knx-project-upload-dialog",dialogImport:F,dialogParams:{}})}},{key:"_openReconfigureFlow",value:(n=(0,i.A)((0,o.A)().m((function e(){var t,n,i,r,a,s,l;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return n=z.W,i=this,r=this.knx.config_entry.domain,a=null===(t=this.hass.userData)||void 0===t?void 0:t.showAdvanced,e.n=1,(0,_.QC)(this.hass,this.knx.config_entry.domain);case 1:s=e.v,l=this.knx.config_entry.entry_id,n(i,{startFlowHandler:r,showAdvanced:a,manifest:s,entryId:l,dialogClosedCallback:e=>{null!=e&&e.flowFinished&&(0,y.r)(this,"knx-reload")}});case 2:return e.a(2)}}),e,this)}))),function(){return n.apply(this,arguments)})},{key:"render",value:function(){return(0,c.qy)(k||(k=P`
      <hass-subpage
        .narrow=${0}
        .hass=${0}
        header="KNX"
        ?main-page=${0}
      >
        <ha-config-section .narrow=${0} .isWide=${0}>
          <ha-card outlined>
            <ha-navigation-list
              .hass=${0}
              .narrow=${0}
              .pages=${0}
              has-secondary
            ></ha-navigation-list>
          </ha-card>
          <ha-card outlined>
            <ha-md-list has-secondary>
              ${0}
            </ha-md-list>
          </ha-card>
        </ha-config-section>
      </hass-subpage>
    `),this.narrow,this.hass,this.narrow,this.narrow,this.isWide,this.hass,this.narrow,this._getPages(),m(this._buttonItems,(e=>(0,c.qy)(x||(x=P` <ha-md-list-item
                    type="button"
                    @click=${0}
                    ?disabled=${0}
                  >
                    <div
                      slot="start"
                      class="icon-background"
                      .style=${0}
                    >
                      <ha-svg-icon .path=${0}></ha-svg-icon>
                    </div>
                    <span slot="headline"
                      >${0}</span
                    >
                    <span slot="supporting-text"
                      >${0}</span
                    >
                  </ha-md-list-item>`),e.click,!e.validConfigEntryStates.has(this._configEntryState),`background-color: ${e.iconColor}`,e.iconPath,this.hass.localize(`${e.translationKey}.title`),this.hass.localize(`${e.translationKey}.description`)))))}}]);var n,d}((0,v.E)(c.WF));M.styles=(0,c.AH)(A||(A=P`
    ha-card {
      overflow: hidden;
    }
    ha-svg-icon {
      color: var(--secondary-text-color);
      height: 24px;
      width: 24px;
      display: block;
      padding: 8px;
    }
    .icon-background {
      border-radius: var(--ha-border-radius-circle);
    }
    .icon-background ha-svg-icon {
      color: #fff;
    }
  `)),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],M.prototype,"knx",void 0),(0,d.__decorate)([(0,p.MZ)({type:Boolean})],M.prototype,"narrow",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"is-wide",type:Boolean})],M.prototype,"isWide",void 0),(0,d.__decorate)([(0,p.wk)()],M.prototype,"_configEntryState",void 0),M=(0,d.__decorate)([(0,p.EM)("knx-dashboard")],M)},11245:function(e,t,n){n.d(t,{R:function(){return i}});var o,i=(0,n(96196).AH)(o||(o=(e=>e)`:host{background:var(--md-list-container-color, var(--md-sys-color-surface, #fef7ff));color:unset;display:flex;flex-direction:column;outline:none;padding:8px 0;position:relative}
`))},49838:function(e,t,n){n.d(t,{B:function(){return m}});var o,i=n(44734),r=n(56038),a=n(69683),s=n(6454),l=(n(31436),n(23792),n(26099),n(16034),n(31415),n(17642),n(58004),n(33853),n(45876),n(32475),n(15024),n(31698),n(62953),n(62826)),d=n(96196),c=n(77845),p=n(25423),h=e=>e,u=new Set(Object.values(p.U)),m=function(e){function t(){var e;return(0,i.A)(this,t),(e=(0,a.A)(this,t)).listController=new p.Z({isItem:e=>e.hasAttribute("md-list-item"),getPossibleItems:()=>e.slotItems,isRtl:()=>"rtl"===getComputedStyle(e).direction,deactivateItem:e=>{e.tabIndex=-1},activateItem:e=>{e.tabIndex=0},isNavigableKey:e=>u.has(e),isActivatable:e=>!e.disabled&&"text"!==e.type}),e.internals=e.attachInternals(),d.S$||(e.internals.role="list",e.addEventListener("keydown",e.listController.handleKeydown)),e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"items",get:function(){return this.listController.items}},{key:"render",value:function(){return(0,d.qy)(o||(o=h`
      <slot
        @deactivate-items=${0}
        @request-activation=${0}
        @slotchange=${0}>
      </slot>
    `),this.listController.onDeactivateItems,this.listController.onRequestActivation,this.listController.onSlotchange)}},{key:"activateNextItem",value:function(){return this.listController.activateNextItem()}},{key:"activatePreviousItem",value:function(){return this.listController.activatePreviousItem()}}])}(d.WF);(0,l.__decorate)([(0,c.KN)({flatten:!0})],m.prototype,"slotItems",void 0)},82553:function(e,t,n){n.d(t,{R:function(){return i}});var o,i=(0,n(96196).AH)(o||(o=(e=>e)`:host{display:flex;-webkit-tap-highlight-color:rgba(0,0,0,0);--md-ripple-hover-color: var(--md-list-item-hover-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-hover-opacity: var(--md-list-item-hover-state-layer-opacity, 0.08);--md-ripple-pressed-color: var(--md-list-item-pressed-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-pressed-opacity: var(--md-list-item-pressed-state-layer-opacity, 0.12)}:host(:is([type=button]:not([disabled]),[type=link])){cursor:pointer}md-focus-ring{z-index:1;--md-focus-ring-shape: 8px}a,button,li{background:none;border:none;cursor:inherit;padding:0;margin:0;text-align:unset;text-decoration:none}.list-item{border-radius:inherit;display:flex;flex:1;max-width:inherit;min-width:inherit;outline:none;-webkit-tap-highlight-color:rgba(0,0,0,0);width:100%}.list-item.interactive{cursor:pointer}.list-item.disabled{opacity:var(--md-list-item-disabled-opacity, 0.3);pointer-events:none}[slot=container]{pointer-events:none}md-ripple{border-radius:inherit}md-item{border-radius:inherit;flex:1;height:100%;color:var(--md-list-item-label-text-color, var(--md-sys-color-on-surface, #1d1b20));font-family:var(--md-list-item-label-text-font, var(--md-sys-typescale-body-large-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-label-text-size, var(--md-sys-typescale-body-large-size, 1rem));line-height:var(--md-list-item-label-text-line-height, var(--md-sys-typescale-body-large-line-height, 1.5rem));font-weight:var(--md-list-item-label-text-weight, var(--md-sys-typescale-body-large-weight, var(--md-ref-typeface-weight-regular, 400)));min-height:var(--md-list-item-one-line-container-height, 56px);padding-top:var(--md-list-item-top-space, 12px);padding-bottom:var(--md-list-item-bottom-space, 12px);padding-inline-start:var(--md-list-item-leading-space, 16px);padding-inline-end:var(--md-list-item-trailing-space, 16px)}md-item[multiline]{min-height:var(--md-list-item-two-line-container-height, 72px)}[slot=supporting-text]{color:var(--md-list-item-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-list-item-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-supporting-text-size, var(--md-sys-typescale-body-medium-size, 0.875rem));line-height:var(--md-list-item-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));font-weight:var(--md-list-item-supporting-text-weight, var(--md-sys-typescale-body-medium-weight, var(--md-ref-typeface-weight-regular, 400)))}[slot=trailing-supporting-text]{color:var(--md-list-item-trailing-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-list-item-trailing-supporting-text-font, var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-trailing-supporting-text-size, var(--md-sys-typescale-label-small-size, 0.6875rem));line-height:var(--md-list-item-trailing-supporting-text-line-height, var(--md-sys-typescale-label-small-line-height, 1rem));font-weight:var(--md-list-item-trailing-supporting-text-weight, var(--md-sys-typescale-label-small-weight, var(--md-ref-typeface-weight-medium, 500)))}:is([slot=start],[slot=end])::slotted(*){fill:currentColor}[slot=start]{color:var(--md-list-item-leading-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}[slot=end]{color:var(--md-list-item-trailing-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}@media(forced-colors: active){.disabled slot{color:GrayText}.list-item.disabled{color:GrayText;opacity:1}}
`))},97154:function(e,t,n){n.d(t,{n:function(){return x}});var o,i,r,a,s,l,d,c,p=n(44734),h=n(56038),u=n(69683),m=n(6454),f=n(25460),g=n(62826),v=(n(4469),n(20903),n(71970),n(96196)),y=n(77845),_=n(94333),w=n(28345),b=n(20618),$=n(27525),k=e=>e,x=function(e){function t(){var e;return(0,p.A)(this,t),(e=(0,u.A)(this,t,arguments)).disabled=!1,e.type="text",e.isListItem=!0,e.href="",e.target="",e}return(0,m.A)(t,e),(0,h.A)(t,[{key:"isDisabled",get:function(){return this.disabled&&"link"!==this.type}},{key:"willUpdate",value:function(e){this.href&&(this.type="link"),(0,f.A)(t,"willUpdate",this,3)([e])}},{key:"render",value:function(){return this.renderListItem((0,v.qy)(o||(o=k`
      <md-item>
        <div slot="container">
          ${0} ${0}
        </div>
        <slot name="start" slot="start"></slot>
        <slot name="end" slot="end"></slot>
        ${0}
      </md-item>
    `),this.renderRipple(),this.renderFocusRing(),this.renderBody()))}},{key:"renderListItem",value:function(e){var t,n="link"===this.type;switch(this.type){case"link":t=(0,w.eu)(i||(i=k`a`));break;case"button":t=(0,w.eu)(r||(r=k`button`));break;default:t=(0,w.eu)(a||(a=k`li`))}var o="text"!==this.type,l=n&&this.target?this.target:v.s6;return(0,w.qy)(s||(s=k`
      <${0}
        id="item"
        tabindex="${0}"
        ?disabled=${0}
        role="listitem"
        aria-selected=${0}
        aria-checked=${0}
        aria-expanded=${0}
        aria-haspopup=${0}
        class="list-item ${0}"
        href=${0}
        target=${0}
        @focus=${0}
      >${0}</${0}>
    `),t,this.isDisabled||!o?-1:0,this.isDisabled,this.ariaSelected||v.s6,this.ariaChecked||v.s6,this.ariaExpanded||v.s6,this.ariaHasPopup||v.s6,(0,_.H)(this.getRenderClasses()),this.href||v.s6,l,this.onFocus,e,t)}},{key:"renderRipple",value:function(){return"text"===this.type?v.s6:(0,v.qy)(l||(l=k` <md-ripple
      part="ripple"
      for="item"
      ?disabled=${0}></md-ripple>`),this.isDisabled)}},{key:"renderFocusRing",value:function(){return"text"===this.type?v.s6:(0,v.qy)(d||(d=k` <md-focus-ring
      @visibility-changed=${0}
      part="focus-ring"
      for="item"
      inward></md-focus-ring>`),this.onFocusRingVisibilityChanged)}},{key:"onFocusRingVisibilityChanged",value:function(e){}},{key:"getRenderClasses",value:function(){return{disabled:this.isDisabled}}},{key:"renderBody",value:function(){return(0,v.qy)(c||(c=k`
      <slot></slot>
      <slot name="overline" slot="overline"></slot>
      <slot name="headline" slot="headline"></slot>
      <slot name="supporting-text" slot="supporting-text"></slot>
      <slot
        name="trailing-supporting-text"
        slot="trailing-supporting-text"></slot>
    `))}},{key:"onFocus",value:function(){-1===this.tabIndex&&this.dispatchEvent((0,$.cG)())}},{key:"focus",value:function(){var e;null===(e=this.listItemRoot)||void 0===e||e.focus()}},{key:"click",value:function(){this.listItemRoot?this.listItemRoot.click():(0,f.A)(t,"click",this,3)([])}}])}((0,b.n)(v.WF));x.shadowRootOptions=Object.assign(Object.assign({},v.WF.shadowRootOptions),{},{delegatesFocus:!0}),(0,g.__decorate)([(0,y.MZ)({type:Boolean,reflect:!0})],x.prototype,"disabled",void 0),(0,g.__decorate)([(0,y.MZ)({reflect:!0})],x.prototype,"type",void 0),(0,g.__decorate)([(0,y.MZ)({type:Boolean,attribute:"md-list-item",reflect:!0})],x.prototype,"isListItem",void 0),(0,g.__decorate)([(0,y.MZ)()],x.prototype,"href",void 0),(0,g.__decorate)([(0,y.MZ)()],x.prototype,"target",void 0),(0,g.__decorate)([(0,y.P)(".list-item")],x.prototype,"listItemRoot",void 0)}}]);
//# sourceMappingURL=538.c8d47c1ae4bbfede.js.map