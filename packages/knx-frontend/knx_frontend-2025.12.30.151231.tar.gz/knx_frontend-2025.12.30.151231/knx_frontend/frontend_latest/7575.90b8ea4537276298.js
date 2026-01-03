/*! For license information please see 7575.90b8ea4537276298.js.LICENSE.txt */
export const __webpack_id__="7575";export const __webpack_ids__=["7575"];export const __webpack_modules__={95379:function(e,t,o){var a=o(62826),i=o(96196),n=o(77845);class r extends i.WF{render(){return i.qy`
      ${this.header?i.qy`<h1 class="card-header">${this.header}</h1>`:i.s6}
      <slot></slot>
    `}constructor(...e){super(...e),this.raised=!1}}r.styles=i.AH`
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
  `,(0,a.__decorate)([(0,n.MZ)()],r.prototype,"header",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],r.prototype,"raised",void 0),r=(0,a.__decorate)([(0,n.EM)("ha-card")],r)},28608:function(e,t,o){o.r(t),o.d(t,{HaIconNext:()=>s});var a=o(62826),i=o(77845),n=o(76679),r=o(60961);class s extends r.HaSvgIcon{constructor(...e){super(...e),this.path="rtl"===n.G.document.dir?"M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z":"M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"}}(0,a.__decorate)([(0,i.MZ)()],s.prototype,"path",void 0),s=(0,a.__decorate)([(0,i.EM)("ha-icon-next")],s)},23897:function(e,t,o){o.d(t,{G:()=>d,J:()=>l});var a=o(62826),i=o(97154),n=o(82553),r=o(96196),s=o(77845);o(95591);const l=[n.R,r.AH`
    :host {
      --ha-icon-display: block;
      --md-sys-color-primary: var(--primary-text-color);
      --md-sys-color-secondary: var(--secondary-text-color);
      --md-sys-color-surface: var(--card-background-color);
      --md-sys-color-on-surface: var(--primary-text-color);
      --md-sys-color-on-surface-variant: var(--secondary-text-color);
    }
    md-item {
      overflow: var(--md-item-overflow, hidden);
      align-items: var(--md-item-align-items, center);
      gap: var(--ha-md-list-item-gap, 16px);
    }
  `];class d extends i.n{renderRipple(){return"text"===this.type?r.s6:r.qy`<ha-ripple
      part="ripple"
      for="item"
      ?disabled=${this.disabled&&"link"!==this.type}
    ></ha-ripple>`}}d.styles=l,d=(0,a.__decorate)([(0,s.EM)("ha-md-list-item")],d)},42921:function(e,t,o){var a=o(62826),i=o(49838),n=o(11245),r=o(96196),s=o(77845);class l extends i.B{}l.styles=[n.R,r.AH`
      :host {
        --md-sys-color-surface: var(--card-background-color);
      }
    `],l=(0,a.__decorate)([(0,s.EM)("ha-md-list")],l)},65300:function(e,t,o){var a=o(62826),i=o(96196),n=o(77845),r=o(32288);o(28608),o(42921),o(23897),o(60961);class s extends i.WF{render(){return i.qy`
      <ha-md-list
        innerRole="menu"
        itemRoles="menuitem"
        innerAriaLabel=${(0,r.J)(this.label)}
      >
        ${this.pages.map((e=>{const t=e.path.endsWith("#external-app-configuration");return i.qy`
            <ha-md-list-item
              .type=${t?"button":"link"}
              .href=${t?void 0:e.path}
              @click=${t?this._handleExternalApp:void 0}
            >
              <div
                slot="start"
                class=${e.iconColor?"icon-background":""}
                .style="background-color: ${e.iconColor||"undefined"}"
              >
                <ha-svg-icon .path=${e.iconPath}></ha-svg-icon>
              </div>
              <span slot="headline">${e.name}</span>
              ${this.hasSecondary?i.qy`<span slot="supporting-text">${e.description}</span>`:""}
              ${this.narrow?"":i.qy`<ha-icon-next slot="end"></ha-icon-next>`}
            </ha-md-list-item>
          `}))}
      </ha-md-list>
    `}_handleExternalApp(){this.hass.auth.external.fireMessage({type:"config_screen/show"})}constructor(...e){super(...e),this.narrow=!1,this.hasSecondary=!1}}s.styles=i.AH`
    ha-svg-icon,
    ha-icon-next {
      color: var(--secondary-text-color);
      height: 24px;
      width: 24px;
      display: block;
    }
    ha-svg-icon {
      padding: 8px;
    }
    .icon-background {
      border-radius: var(--ha-border-radius-circle);
    }
    .icon-background ha-svg-icon {
      color: #fff;
    }
    ha-md-list-item {
      font-size: var(--navigation-list-item-title-font-size);
    }
  `,(0,a.__decorate)([(0,n.MZ)({attribute:!1})],s.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],s.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],s.prototype,"pages",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"has-secondary",type:Boolean})],s.prototype,"hasSecondary",void 0),(0,a.__decorate)([(0,n.MZ)()],s.prototype,"label",void 0),s=(0,a.__decorate)([(0,n.EM)("ha-navigation-list")],s)},23608:function(e,t,o){o.d(t,{PN:()=>n,jm:()=>r,sR:()=>s,t1:()=>i,t2:()=>d,yu:()=>l});const a={"HA-Frontend-Base":`${location.protocol}//${location.host}`},i=(e,t,o)=>e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(e.userData?.showAdvanced),entry_id:o},a),n=(e,t)=>e.callApi("GET",`config/config_entries/flow/${t}`,void 0,a),r=(e,t,o)=>e.callApi("POST",`config/config_entries/flow/${t}`,o,a),s=(e,t)=>e.callApi("DELETE",`config/config_entries/flow/${t}`),l=(e,t)=>e.callApi("GET","config/config_entries/flow_handlers"+(t?`?type=${t}`:"")),d=e=>e.sendMessagePromise({type:"config_entries/flow/progress"})},84125:function(e,t,o){o.d(t,{QC:()=>n,fK:()=>i,p$:()=>a});const a=(e,t,o)=>e(`component.${t}.title`)||o?.name||t,i=(e,t)=>{const o={type:"manifest/list"};return t&&(o.integrations=t),e.callWS(o)},n=(e,t)=>e.callWS({type:"manifest/get",integration:t})},73042:function(e,t,o){o.d(t,{W:()=>s});var a=o(96196),i=o(23608),n=o(84125),r=o(73347);const s=(e,t)=>(0,r.g)(e,t,{flowType:"config_flow",showDevices:!0,createFlow:async(e,o)=>{const[a]=await Promise.all([(0,i.t1)(e,o,t.entryId),e.loadFragmentTranslation("config"),e.loadBackendTranslation("config",o),e.loadBackendTranslation("selector",o),e.loadBackendTranslation("title",o)]);return a},fetchFlow:async(e,t)=>{const[o]=await Promise.all([(0,i.PN)(e,t),e.loadFragmentTranslation("config")]);return await Promise.all([e.loadBackendTranslation("config",o.handler),e.loadBackendTranslation("selector",o.handler),e.loadBackendTranslation("title",o.handler)]),o},handleFlowStep:i.jm,deleteFlow:i.sR,renderAbortDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.abort.${t.reason}`,t.description_placeholders);return o?a.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:t.reason},renderShowFormStepHeader(e,t){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.title`,t.description_placeholders)||e.localize(`component.${t.handler}.title`)},renderShowFormStepDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return o?a.qy`
            <ha-markdown
              .allowDataUrl=${"zwave_js"===t.handler}
              allow-svg
              breaks
              .content=${o}
            ></ha-markdown>
          `:""},renderShowFormStepFieldLabel(e,t,o,a){if("expandable"===o.type)return e.localize(`component.${t.handler}.config.step.${t.step_id}.sections.${o.name}.name`,t.description_placeholders);const i=a?.path?.[0]?`sections.${a.path[0]}.`:"";return e.localize(`component.${t.handler}.config.step.${t.step_id}.${i}data.${o.name}`,t.description_placeholders)||o.name},renderShowFormStepFieldHelper(e,t,o,i){if("expandable"===o.type)return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.sections.${o.name}.description`,t.description_placeholders);const n=i?.path?.[0]?`sections.${i.path[0]}.`:"",r=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.${n}data_description.${o.name}`,t.description_placeholders);return r?a.qy`<ha-markdown breaks .content=${r}></ha-markdown>`:""},renderShowFormStepFieldError(e,t,o){return e.localize(`component.${t.translation_domain||t.translation_domain||t.handler}.config.error.${o}`,t.description_placeholders)||o},renderShowFormStepFieldLocalizeValue(e,t,o){return e.localize(`component.${t.handler}.selector.${o}`)},renderShowFormStepSubmitButton(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===t.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.${t.step_id}.description`,t.description_placeholders);return a.qy`
        <p>
          ${e.localize("ui.panel.config.integrations.config_flow.external_step.description")}
        </p>
        ${o?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${o}
              ></ha-markdown>
            `:""}
      `},renderCreateEntryDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.create_entry.${t.description||"default"}`,t.description_placeholders);return a.qy`
        ${o?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${o}
              ></ha-markdown>
            `:a.s6}
      `},renderShowFormProgressHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderShowFormProgressDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.progress.${t.progress_action}`,t.description_placeholders);return o?a.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:""},renderMenuHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderMenuDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return o?a.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:""},renderMenuOption(e,t,o){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_options.${o}`,t.description_placeholders)},renderMenuOptionDescription(e,t,o){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_option_descriptions.${o}`,t.description_placeholders)},renderLoadingDescription(e,t,o,a){if("loading_flow"!==t&&"loading_step"!==t)return"";const i=a?.handler||o;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:i?(0,n.p$)(e.localize,i):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}})},73347:function(e,t,o){o.d(t,{g:()=>n});var a=o(92542);const i=()=>Promise.all([o.e("6009"),o.e("4533"),o.e("2791"),o.e("2203"),o.e("4018"),o.e("4899"),o.e("8522"),o.e("6938"),o.e("9107"),o.e("8061"),o.e("7394")]).then(o.bind(o,90313)),n=(e,t,o)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-data-entry-flow",dialogImport:i,dialogParams:{...t,flowConfig:o,dialogParentElement:e}})}},35804:function(e,t,o){o.d(t,{Q:()=>c});var a=o(96196),i=o(84125);const n=(e,t)=>e.callApi("POST","config/config_entries/options/flow",{handler:t,show_advanced_options:Boolean(e.userData?.showAdvanced)}),r=(e,t)=>e.callApi("GET",`config/config_entries/options/flow/${t}`),s=(e,t,o)=>e.callApi("POST",`config/config_entries/options/flow/${t}`,o),l=(e,t)=>e.callApi("DELETE",`config/config_entries/options/flow/${t}`);var d=o(73347);const c=(e,t,o)=>(0,d.g)(e,{startFlowHandler:t.entry_id,domain:t.domain,...o},{flowType:"options_flow",showDevices:!1,createFlow:async(e,o)=>{const[a]=await Promise.all([n(e,o),e.loadFragmentTranslation("config"),e.loadBackendTranslation("options",t.domain),e.loadBackendTranslation("selector",t.domain)]);return a},fetchFlow:async(e,o)=>{const[a]=await Promise.all([r(e,o),e.loadFragmentTranslation("config"),e.loadBackendTranslation("options",t.domain),e.loadBackendTranslation("selector",t.domain)]);return a},handleFlowStep:s,deleteFlow:l,renderAbortDescription(e,o){const i=e.localize(`component.${o.translation_domain||t.domain}.options.abort.${o.reason}`,o.description_placeholders);return i?a.qy`
              <ha-markdown
                breaks
                allow-svg
                .content=${i}
              ></ha-markdown>
            `:o.reason},renderShowFormStepHeader(e,o){return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.title`,o.description_placeholders)||e.localize("ui.dialogs.options_flow.form.header")},renderShowFormStepDescription(e,o){const i=e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.description`,o.description_placeholders);return i?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${i}
              ></ha-markdown>
            `:""},renderShowFormStepFieldLabel(e,o,a,i){if("expandable"===a.type)return e.localize(`component.${t.domain}.options.step.${o.step_id}.sections.${a.name}.name`,o.description_placeholders);const n=i?.path?.[0]?`sections.${i.path[0]}.`:"";return e.localize(`component.${t.domain}.options.step.${o.step_id}.${n}data.${a.name}`,o.description_placeholders)||a.name},renderShowFormStepFieldHelper(e,o,i,n){if("expandable"===i.type)return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.sections.${i.name}.description`,o.description_placeholders);const r=n?.path?.[0]?`sections.${n.path[0]}.`:"",s=e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.${r}data_description.${i.name}`,o.description_placeholders);return s?a.qy`<ha-markdown breaks .content=${s}></ha-markdown>`:""},renderShowFormStepFieldError(e,o,a){return e.localize(`component.${o.translation_domain||t.domain}.options.error.${a}`,o.description_placeholders)||a},renderShowFormStepFieldLocalizeValue(e,o,a){return e.localize(`component.${t.domain}.selector.${a}`)},renderShowFormStepSubmitButton(e,o){return e.localize(`component.${t.domain}.options.step.${o.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===o.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return""},renderExternalStepDescription(e,t){return""},renderCreateEntryDescription(e,t){return a.qy`
          <p>${e.localize("ui.dialogs.options_flow.success.description")}</p>
        `},renderShowFormProgressHeader(e,o){return e.localize(`component.${t.domain}.options.step.${o.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderShowFormProgressDescription(e,o){const i=e.localize(`component.${o.translation_domain||t.domain}.options.progress.${o.progress_action}`,o.description_placeholders);return i?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${i}
              ></ha-markdown>
            `:""},renderMenuHeader(e,o){return e.localize(`component.${t.domain}.options.step.${o.step_id}.title`)||e.localize(`component.${t.domain}.title`)},renderMenuDescription(e,o){const i=e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.description`,o.description_placeholders);return i?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${i}
              ></ha-markdown>
            `:""},renderMenuOption(e,o,a){return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.menu_options.${a}`,o.description_placeholders)},renderMenuOptionDescription(e,o,a){return e.localize(`component.${o.translation_domain||t.domain}.options.step.${o.step_id}.menu_option_descriptions.${a}`,o.description_placeholders)},renderLoadingDescription(e,o){return e.localize(`component.${t.domain}.options.loading`)||("loading_flow"===o||"loading_step"===o?e.localize(`ui.dialogs.options_flow.loading.${o}`,{integration:(0,i.p$)(e.localize,t.domain)}):"")}})},29937:function(e,t,o){var a=o(62826),i=o(96196),n=o(77845),r=o(39501),s=o(5871),l=(o(371),o(45397),o(39396));class d extends i.WF{render(){return i.qy`
      <div class="toolbar">
        <div class="toolbar-content">
          ${this.mainPage||history.state?.root?i.qy`
                <ha-menu-button
                  .hassio=${this.supervisor}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                ></ha-menu-button>
              `:this.backPath?i.qy`
                  <a href=${this.backPath}>
                    <ha-icon-button-arrow-prev
                      .hass=${this.hass}
                    ></ha-icon-button-arrow-prev>
                  </a>
                `:i.qy`
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
    `}_saveScrollPos(e){this._savedScrollPos=e.target.scrollTop}_backTapped(){this.backCallback?this.backCallback():(0,s.O)()}static get styles(){return[l.dp,i.AH`
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
      `]}constructor(...e){super(...e),this.mainPage=!1,this.narrow=!1,this.supervisor=!1}}(0,a.__decorate)([(0,n.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)()],d.prototype,"header",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"main-page"})],d.prototype,"mainPage",void 0),(0,a.__decorate)([(0,n.MZ)({type:String,attribute:"back-path"})],d.prototype,"backPath",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],d.prototype,"backCallback",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],d.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"supervisor",void 0),(0,a.__decorate)([(0,r.a)(".content")],d.prototype,"_savedScrollPos",void 0),(0,a.__decorate)([(0,n.Ls)({passive:!0})],d.prototype,"_saveScrollPos",null),d=(0,a.__decorate)([(0,n.EM)("hass-subpage")],d)},10085:function(e,t,o){o.d(t,{E:()=>n});var a=o(62826),i=o(77845);const n=e=>{class t extends e{connectedCallback(){super.connectedCallback(),this._checkSubscribed()}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then((e=>e())):e()}this.__unsubs=void 0}}updated(e){if(super.updated(e),e.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps)for(const t of e.keys())if(this.hassSubscribeRequiredHostProps.includes(t))return void this._checkSubscribed()}hassSubscribe(){return[]}_checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&!this.hassSubscribeRequiredHostProps?.some((e=>void 0===this[e]))&&(this.__unsubs=this.hassSubscribe())}}return(0,a.__decorate)([(0,i.MZ)({attribute:!1})],t.prototype,"hass",void 0),t}},90058:function(e,t,o){o.r(t),o.d(t,{KnxDashboard:()=>b});var a=o(62826),i=o(96196),n=o(77845);var r=o(10085),s=o(92542),l=(o(95379),o(42921),o(23897),o(65300),o(84125)),d=(o(29937),o(94333));class c extends i.WF{render(){return i.qy`
      <div
        class="content ${(0,d.H)({narrow:!this.isWide,"full-width":this.fullWidth})}"
      >
        <div class="header"><slot name="header"></slot></div>
        <div
          class="together layout ${(0,d.H)({narrow:!this.isWide,vertical:this.vertical||!this.isWide,horizontal:!this.vertical&&this.isWide})}"
        >
          <div class="intro"><slot name="introduction"></slot></div>
          <div class="panel flex-auto"><slot></slot></div>
        </div>
      </div>
    `}constructor(...e){super(...e),this.isWide=!1,this.vertical=!1,this.fullWidth=!1}}c.styles=i.AH`
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
  `,(0,a.__decorate)([(0,n.MZ)({attribute:"is-wide",type:Boolean})],c.prototype,"isWide",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],c.prototype,"vertical",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"full-width"})],c.prototype,"fullWidth",void 0),c=(0,a.__decorate)([(0,n.EM)("ha-config-section")],c);var p=o(73042),h=o(35804),m=o(3950);const g=()=>Promise.all([o.e("6009"),o.e("4533"),o.e("4899"),o.e("4649"),o.e("292")]).then(o.bind(o,21199));var u=o(16404),f=o(78577);const v=new f.Q("knx-dashboard");class b extends((0,r.E)(i.WF)){hassSubscribe(){return[this._unsubscribeConfigEntries()]}_unsubscribeConfigEntries(){const e=(0,m.TC)(this.hass,(async e=>{const t=e.find((e=>"knx"===e.entry.domain))?.entry.state;t&&t!==this._configEntryState&&(v.debug("KNX dashboard config entry state update",t),this._configEntryState=t)}),{domain:"knx"});return()=>{e.then((e=>e()))}}_getPages(){return(0,u.rN)(!!this.knx.projectInfo).map((e=>({...e,name:this.hass.localize(e.translationKey)||e.name,description:this.hass.localize(e.descriptionTranslationKey)||e.description})))}async _openOptionFlow(){(0,h.Q)(this,this.knx.config_entry)}_openProjectUploadDialog(){var e;e=this,(0,s.r)(e,"show-dialog",{dialogTag:"knx-project-upload-dialog",dialogImport:g,dialogParams:{}})}async _openReconfigureFlow(){(0,p.W)(this,{startFlowHandler:this.knx.config_entry.domain,showAdvanced:this.hass.userData?.showAdvanced,manifest:await(0,l.QC)(this.hass,this.knx.config_entry.domain),entryId:this.knx.config_entry.entry_id,dialogClosedCallback:e=>{e?.flowFinished&&(0,s.r)(this,"knx-reload")}})}render(){return i.qy`
      <hass-subpage
        .narrow=${this.narrow}
        .hass=${this.hass}
        header="KNX"
        ?main-page=${this.narrow}
      >
        <ha-config-section .narrow=${this.narrow} .isWide=${this.isWide}>
          <ha-card outlined>
            <ha-navigation-list
              .hass=${this.hass}
              .narrow=${this.narrow}
              .pages=${this._getPages()}
              has-secondary
            ></ha-navigation-list>
          </ha-card>
          <ha-card outlined>
            <ha-md-list has-secondary>
              ${function*(e,t){if(void 0!==e){let o=0;for(const a of e)yield t(a,o++)}}(this._buttonItems,(e=>i.qy` <ha-md-list-item
                    type="button"
                    @click=${e.click}
                    ?disabled=${!e.validConfigEntryStates.has(this._configEntryState)}
                  >
                    <div
                      slot="start"
                      class="icon-background"
                      .style=${`background-color: ${e.iconColor}`}
                    >
                      <ha-svg-icon .path=${e.iconPath}></ha-svg-icon>
                    </div>
                    <span slot="headline"
                      >${this.hass.localize(`${e.translationKey}.title`)}</span
                    >
                    <span slot="supporting-text"
                      >${this.hass.localize(`${e.translationKey}.description`)}</span
                    >
                  </ha-md-list-item>`))}
            </ha-md-list>
          </ha-card>
        </ha-config-section>
      </hass-subpage>
    `}constructor(...e){super(...e),this.narrow=!1,this.isWide=!1,this._configEntryState="unknown",this._buttonItems=[{translationKey:"component.knx.config_panel.dashboard.options_flow",iconPath:"M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8M12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12A2,2 0 0,0 12,10M10,22C9.75,22 9.54,21.82 9.5,21.58L9.13,18.93C8.5,18.68 7.96,18.34 7.44,17.94L4.95,18.95C4.73,19.03 4.46,18.95 4.34,18.73L2.34,15.27C2.21,15.05 2.27,14.78 2.46,14.63L4.57,12.97L4.5,12L4.57,11L2.46,9.37C2.27,9.22 2.21,8.95 2.34,8.73L4.34,5.27C4.46,5.05 4.73,4.96 4.95,5.05L7.44,6.05C7.96,5.66 8.5,5.32 9.13,5.07L9.5,2.42C9.54,2.18 9.75,2 10,2H14C14.25,2 14.46,2.18 14.5,2.42L14.87,5.07C15.5,5.32 16.04,5.66 16.56,6.05L19.05,5.05C19.27,4.96 19.54,5.05 19.66,5.27L21.66,8.73C21.79,8.95 21.73,9.22 21.54,9.37L19.43,11L19.5,12L19.43,13L21.54,14.63C21.73,14.78 21.79,15.05 21.66,15.27L19.66,18.73C19.54,18.95 19.27,19.04 19.05,18.95L16.56,17.95C16.04,18.34 15.5,18.68 14.87,18.93L14.5,21.58C14.46,21.82 14.25,22 14,22H10M11.25,4L10.88,6.61C9.68,6.86 8.62,7.5 7.85,8.39L5.44,7.35L4.69,8.65L6.8,10.2C6.4,11.37 6.4,12.64 6.8,13.8L4.68,15.36L5.43,16.66L7.86,15.62C8.63,16.5 9.68,17.14 10.87,17.38L11.24,20H12.76L13.13,17.39C14.32,17.14 15.37,16.5 16.14,15.62L18.57,16.66L19.32,15.36L17.2,13.81C17.6,12.64 17.6,11.37 17.2,10.2L19.31,8.65L18.56,7.35L16.15,8.39C15.38,7.5 14.32,6.86 13.12,6.62L12.75,4H11.25Z",iconColor:"var(--indigo-color)",click:this._openOptionFlow,validConfigEntryStates:new Set(["loaded"])},{translationKey:"component.knx.config_panel.dashboard.project_upload",click:this._openProjectUploadDialog,iconPath:"M14 2H6C4.89 2 4 2.9 4 4V20C4 21.11 4.89 22 6 22H18C19.11 22 20 21.11 20 20V8L14 2M18 20H6V4H13V9H18V20M15 11.93V19H7.93L10.05 16.88L7.22 14.05L10.05 11.22L12.88 14.05L15 11.93Z",iconColor:"var(--orange-color)",validConfigEntryStates:new Set(["loaded"])},{translationKey:"component.knx.config_panel.dashboard.connection_flow",iconPath:"M4,1C2.89,1 2,1.89 2,3V7C2,8.11 2.89,9 4,9H1V11H13V9H10C11.11,9 12,8.11 12,7V3C12,1.89 11.11,1 10,1H4M4,3H10V7H4V3M3,13V18L3,20H10V18H5V13H3M14,13C12.89,13 12,13.89 12,15V19C12,20.11 12.89,21 14,21H11V23H23V21H20C21.11,21 22,20.11 22,19V15C22,13.89 21.11,13 20,13H14M14,15H20V19H14V15Z",iconColor:"var(--cyan-color)",click:this._openReconfigureFlow,validConfigEntryStates:new Set(["loaded","not_loaded"])}]}}b.styles=i.AH`
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
  `,(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],b.prototype,"knx",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean})],b.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:"is-wide",type:Boolean})],b.prototype,"isWide",void 0),(0,a.__decorate)([(0,n.wk)()],b.prototype,"_configEntryState",void 0),b=(0,a.__decorate)([(0,n.EM)("knx-dashboard")],b)},11245:function(e,t,o){o.d(t,{R:()=>a});const a=o(96196).AH`:host{background:var(--md-list-container-color, var(--md-sys-color-surface, #fef7ff));color:unset;display:flex;flex-direction:column;outline:none;padding:8px 0;position:relative}
`},49838:function(e,t,o){o.d(t,{B:()=>l});var a=o(62826),i=o(96196),n=o(77845),r=o(25423);const s=new Set(Object.values(r.U));class l extends i.WF{get items(){return this.listController.items}render(){return i.qy`
      <slot
        @deactivate-items=${this.listController.onDeactivateItems}
        @request-activation=${this.listController.onRequestActivation}
        @slotchange=${this.listController.onSlotchange}>
      </slot>
    `}activateNextItem(){return this.listController.activateNextItem()}activatePreviousItem(){return this.listController.activatePreviousItem()}constructor(){super(),this.listController=new r.Z({isItem:e=>e.hasAttribute("md-list-item"),getPossibleItems:()=>this.slotItems,isRtl:()=>"rtl"===getComputedStyle(this).direction,deactivateItem:e=>{e.tabIndex=-1},activateItem:e=>{e.tabIndex=0},isNavigableKey:e=>s.has(e),isActivatable:e=>!e.disabled&&"text"!==e.type}),this.internals=this.attachInternals(),i.S$||(this.internals.role="list",this.addEventListener("keydown",this.listController.handleKeydown))}}(0,a.__decorate)([(0,n.KN)({flatten:!0})],l.prototype,"slotItems",void 0)},82553:function(e,t,o){o.d(t,{R:()=>a});const a=o(96196).AH`:host{display:flex;-webkit-tap-highlight-color:rgba(0,0,0,0);--md-ripple-hover-color: var(--md-list-item-hover-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-hover-opacity: var(--md-list-item-hover-state-layer-opacity, 0.08);--md-ripple-pressed-color: var(--md-list-item-pressed-state-layer-color, var(--md-sys-color-on-surface, #1d1b20));--md-ripple-pressed-opacity: var(--md-list-item-pressed-state-layer-opacity, 0.12)}:host(:is([type=button]:not([disabled]),[type=link])){cursor:pointer}md-focus-ring{z-index:1;--md-focus-ring-shape: 8px}a,button,li{background:none;border:none;cursor:inherit;padding:0;margin:0;text-align:unset;text-decoration:none}.list-item{border-radius:inherit;display:flex;flex:1;max-width:inherit;min-width:inherit;outline:none;-webkit-tap-highlight-color:rgba(0,0,0,0);width:100%}.list-item.interactive{cursor:pointer}.list-item.disabled{opacity:var(--md-list-item-disabled-opacity, 0.3);pointer-events:none}[slot=container]{pointer-events:none}md-ripple{border-radius:inherit}md-item{border-radius:inherit;flex:1;height:100%;color:var(--md-list-item-label-text-color, var(--md-sys-color-on-surface, #1d1b20));font-family:var(--md-list-item-label-text-font, var(--md-sys-typescale-body-large-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-label-text-size, var(--md-sys-typescale-body-large-size, 1rem));line-height:var(--md-list-item-label-text-line-height, var(--md-sys-typescale-body-large-line-height, 1.5rem));font-weight:var(--md-list-item-label-text-weight, var(--md-sys-typescale-body-large-weight, var(--md-ref-typeface-weight-regular, 400)));min-height:var(--md-list-item-one-line-container-height, 56px);padding-top:var(--md-list-item-top-space, 12px);padding-bottom:var(--md-list-item-bottom-space, 12px);padding-inline-start:var(--md-list-item-leading-space, 16px);padding-inline-end:var(--md-list-item-trailing-space, 16px)}md-item[multiline]{min-height:var(--md-list-item-two-line-container-height, 72px)}[slot=supporting-text]{color:var(--md-list-item-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-list-item-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-supporting-text-size, var(--md-sys-typescale-body-medium-size, 0.875rem));line-height:var(--md-list-item-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));font-weight:var(--md-list-item-supporting-text-weight, var(--md-sys-typescale-body-medium-weight, var(--md-ref-typeface-weight-regular, 400)))}[slot=trailing-supporting-text]{color:var(--md-list-item-trailing-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-list-item-trailing-supporting-text-font, var(--md-sys-typescale-label-small-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-list-item-trailing-supporting-text-size, var(--md-sys-typescale-label-small-size, 0.6875rem));line-height:var(--md-list-item-trailing-supporting-text-line-height, var(--md-sys-typescale-label-small-line-height, 1rem));font-weight:var(--md-list-item-trailing-supporting-text-weight, var(--md-sys-typescale-label-small-weight, var(--md-ref-typeface-weight-medium, 500)))}:is([slot=start],[slot=end])::slotted(*){fill:currentColor}[slot=start]{color:var(--md-list-item-leading-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}[slot=end]{color:var(--md-list-item-trailing-icon-color, var(--md-sys-color-on-surface-variant, #49454f))}@media(forced-colors: active){.disabled slot{color:GrayText}.list-item.disabled{color:GrayText;opacity:1}}
`},97154:function(e,t,o){o.d(t,{n:()=>p});var a=o(62826),i=(o(4469),o(20903),o(71970),o(96196)),n=o(77845),r=o(94333),s=o(28345),l=o(20618),d=o(27525);const c=(0,l.n)(i.WF);class p extends c{get isDisabled(){return this.disabled&&"link"!==this.type}willUpdate(e){this.href&&(this.type="link"),super.willUpdate(e)}render(){return this.renderListItem(i.qy`
      <md-item>
        <div slot="container">
          ${this.renderRipple()} ${this.renderFocusRing()}
        </div>
        <slot name="start" slot="start"></slot>
        <slot name="end" slot="end"></slot>
        ${this.renderBody()}
      </md-item>
    `)}renderListItem(e){const t="link"===this.type;let o;switch(this.type){case"link":o=s.eu`a`;break;case"button":o=s.eu`button`;break;default:o=s.eu`li`}const a="text"!==this.type,n=t&&this.target?this.target:i.s6;return s.qy`
      <${o}
        id="item"
        tabindex="${this.isDisabled||!a?-1:0}"
        ?disabled=${this.isDisabled}
        role="listitem"
        aria-selected=${this.ariaSelected||i.s6}
        aria-checked=${this.ariaChecked||i.s6}
        aria-expanded=${this.ariaExpanded||i.s6}
        aria-haspopup=${this.ariaHasPopup||i.s6}
        class="list-item ${(0,r.H)(this.getRenderClasses())}"
        href=${this.href||i.s6}
        target=${n}
        @focus=${this.onFocus}
      >${e}</${o}>
    `}renderRipple(){return"text"===this.type?i.s6:i.qy` <md-ripple
      part="ripple"
      for="item"
      ?disabled=${this.isDisabled}></md-ripple>`}renderFocusRing(){return"text"===this.type?i.s6:i.qy` <md-focus-ring
      @visibility-changed=${this.onFocusRingVisibilityChanged}
      part="focus-ring"
      for="item"
      inward></md-focus-ring>`}onFocusRingVisibilityChanged(e){}getRenderClasses(){return{disabled:this.isDisabled}}renderBody(){return i.qy`
      <slot></slot>
      <slot name="overline" slot="overline"></slot>
      <slot name="headline" slot="headline"></slot>
      <slot name="supporting-text" slot="supporting-text"></slot>
      <slot
        name="trailing-supporting-text"
        slot="trailing-supporting-text"></slot>
    `}onFocus(){-1===this.tabIndex&&this.dispatchEvent((0,d.cG)())}focus(){this.listItemRoot?.focus()}click(){this.listItemRoot?this.listItemRoot.click():super.click()}constructor(){super(...arguments),this.disabled=!1,this.type="text",this.isListItem=!0,this.href="",this.target=""}}p.shadowRootOptions={...i.WF.shadowRootOptions,delegatesFocus:!0},(0,a.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],p.prototype,"disabled",void 0),(0,a.__decorate)([(0,n.MZ)({reflect:!0})],p.prototype,"type",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,attribute:"md-list-item",reflect:!0})],p.prototype,"isListItem",void 0),(0,a.__decorate)([(0,n.MZ)()],p.prototype,"href",void 0),(0,a.__decorate)([(0,n.MZ)()],p.prototype,"target",void 0),(0,a.__decorate)([(0,n.P)(".list-item")],p.prototype,"listItemRoot",void 0)}};
//# sourceMappingURL=7575.90b8ea4537276298.js.map