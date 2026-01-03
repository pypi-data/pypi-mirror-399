export const __webpack_id__="8991";export const __webpack_ids__=["8991"];export const __webpack_modules__={21754:function(e,t,o){o.d(t,{A:()=>a});const i=e=>e<10?`0${e}`:e;function a(e){const t=Math.floor(e/3600),o=Math.floor(e%3600/60),a=Math.floor(e%3600%60);return t>0?`${t}:${i(o)}:${i(a)}`:o>0?`${o}:${i(a)}`:a>0?""+a:null}},55124:function(e,t,o){o.d(t,{d:()=>i});const i=e=>e.stopPropagation()},75261:function(e,t,o){var i=o(62826),a=o(70402),n=o(11081),r=o(77845);class s extends a.iY{}s.styles=n.R,s=(0,i.__decorate)([(0,r.EM)("ha-list")],s)},88422:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(62826),a=o(52630),n=o(96196),r=o(77845),s=e([a]);a=(s.then?(await s)():s)[0];class l extends a.A{static get styles(){return[a.A.styles,n.AH`
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
      `]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=150}}(0,i.__decorate)([(0,r.MZ)({attribute:"show-delay",type:Number})],l.prototype,"showDelay",void 0),(0,i.__decorate)([(0,r.MZ)({attribute:"hide-delay",type:Number})],l.prototype,"hideDelay",void 0),l=(0,i.__decorate)([(0,r.EM)("ha-tooltip")],l),t()}catch(l){t(l)}}))},23608:function(e,t,o){o.d(t,{PN:()=>n,jm:()=>r,sR:()=>s,t1:()=>a,t2:()=>d,yu:()=>l});const i={"HA-Frontend-Base":`${location.protocol}//${location.host}`},a=(e,t,o)=>e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(e.userData?.showAdvanced),entry_id:o},i),n=(e,t)=>e.callApi("GET",`config/config_entries/flow/${t}`,void 0,i),r=(e,t,o)=>e.callApi("POST",`config/config_entries/flow/${t}`,o,i),s=(e,t)=>e.callApi("DELETE",`config/config_entries/flow/${t}`),l=(e,t)=>e.callApi("GET","config/config_entries/flow_handlers"+(t?`?type=${t}`:"")),d=e=>e.sendMessagePromise({type:"config_entries/flow/progress"})},96643:function(e,t,o){o.d(t,{Pu:()=>i});const i=(e,t)=>e.callWS({type:"counter/create",...t})},90536:function(e,t,o){o.d(t,{nr:()=>i});const i=(e,t)=>e.callWS({type:"input_boolean/create",...t})},97666:function(e,t,o){o.d(t,{L6:()=>i});const i=(e,t)=>e.callWS({type:"input_button/create",...t})},991:function(e,t,o){o.d(t,{ke:()=>i});const i=(e,t)=>e.callWS({type:"input_datetime/create",...t})},71435:function(e,t,o){o.d(t,{gO:()=>i});const i=(e,t)=>e.callWS({type:"input_number/create",...t})},91482:function(e,t,o){o.d(t,{BT:()=>i});const i=(e,t)=>e.callWS({type:"input_select/create",...t})},50085:function(e,t,o){o.d(t,{m4:()=>i});const i=(e,t)=>e.callWS({type:"input_text/create",...t})},72550:function(e,t,o){o.d(t,{mx:()=>i,sF:()=>a});const i=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],a=(e,t)=>e.callWS({type:"schedule/create",...t})},12134:function(e,t,o){o.d(t,{ls:()=>n,PF:()=>r,CR:()=>a});var i=o(21754);const a=(e,t)=>e.callWS({type:"timer/create",...t}),n=e=>{if(!e.attributes.remaining)return;let t=function(e){const t=e.split(":").map(Number);return 3600*t[0]+60*t[1]+t[2]}(e.attributes.remaining);if("active"===e.state){const o=(new Date).getTime(),i=new Date(e.attributes.finishes_at).getTime();t=Math.max((i-o)/1e3,0)}return t},r=(e,t,o)=>{if(!t)return null;if("idle"===t.state||0===o)return e.formatEntityState(t);let a=(0,i.A)(o||0)||"0";return"paused"===t.state&&(a=`${a} (${e.formatEntityState(t)})`),a}},73042:function(e,t,o){o.d(t,{W:()=>s});var i=o(96196),a=o(23608),n=o(84125),r=o(73347);const s=(e,t)=>(0,r.g)(e,t,{flowType:"config_flow",showDevices:!0,createFlow:async(e,o)=>{const[i]=await Promise.all([(0,a.t1)(e,o,t.entryId),e.loadFragmentTranslation("config"),e.loadBackendTranslation("config",o),e.loadBackendTranslation("selector",o),e.loadBackendTranslation("title",o)]);return i},fetchFlow:async(e,t)=>{const[o]=await Promise.all([(0,a.PN)(e,t),e.loadFragmentTranslation("config")]);return await Promise.all([e.loadBackendTranslation("config",o.handler),e.loadBackendTranslation("selector",o.handler),e.loadBackendTranslation("title",o.handler)]),o},handleFlowStep:a.jm,deleteFlow:a.sR,renderAbortDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.abort.${t.reason}`,t.description_placeholders);return o?i.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:t.reason},renderShowFormStepHeader(e,t){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.title`,t.description_placeholders)||e.localize(`component.${t.handler}.title`)},renderShowFormStepDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return o?i.qy`
            <ha-markdown
              .allowDataUrl=${"zwave_js"===t.handler}
              allow-svg
              breaks
              .content=${o}
            ></ha-markdown>
          `:""},renderShowFormStepFieldLabel(e,t,o,i){if("expandable"===o.type)return e.localize(`component.${t.handler}.config.step.${t.step_id}.sections.${o.name}.name`,t.description_placeholders);const a=i?.path?.[0]?`sections.${i.path[0]}.`:"";return e.localize(`component.${t.handler}.config.step.${t.step_id}.${a}data.${o.name}`,t.description_placeholders)||o.name},renderShowFormStepFieldHelper(e,t,o,a){if("expandable"===o.type)return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.sections.${o.name}.description`,t.description_placeholders);const n=a?.path?.[0]?`sections.${a.path[0]}.`:"",r=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.${n}data_description.${o.name}`,t.description_placeholders);return r?i.qy`<ha-markdown breaks .content=${r}></ha-markdown>`:""},renderShowFormStepFieldError(e,t,o){return e.localize(`component.${t.translation_domain||t.translation_domain||t.handler}.config.error.${o}`,t.description_placeholders)||o},renderShowFormStepFieldLocalizeValue(e,t,o){return e.localize(`component.${t.handler}.selector.${o}`)},renderShowFormStepSubmitButton(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===t.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.${t.step_id}.description`,t.description_placeholders);return i.qy`
        <p>
          ${e.localize("ui.panel.config.integrations.config_flow.external_step.description")}
        </p>
        ${o?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${o}
              ></ha-markdown>
            `:""}
      `},renderCreateEntryDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.create_entry.${t.description||"default"}`,t.description_placeholders);return i.qy`
        ${o?i.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${o}
              ></ha-markdown>
            `:i.s6}
      `},renderShowFormProgressHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderShowFormProgressDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.progress.${t.progress_action}`,t.description_placeholders);return o?i.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:""},renderMenuHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderMenuDescription(e,t){const o=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return o?i.qy`
            <ha-markdown allow-svg breaks .content=${o}></ha-markdown>
          `:""},renderMenuOption(e,t,o){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_options.${o}`,t.description_placeholders)},renderMenuOptionDescription(e,t,o){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_option_descriptions.${o}`,t.description_placeholders)},renderLoadingDescription(e,t,o,i){if("loading_flow"!==t&&"loading_step"!==t)return"";const a=i?.handler||o;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:a?(0,n.p$)(e.localize,a):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}})},73347:function(e,t,o){o.d(t,{g:()=>n});var i=o(92542);const a=()=>Promise.all([o.e("6009"),o.e("4533"),o.e("2791"),o.e("2203"),o.e("4018"),o.e("4899"),o.e("8522"),o.e("6938"),o.e("9107"),o.e("8061"),o.e("7394")]).then(o.bind(o,90313)),n=(e,t,o)=>{(0,i.r)(e,"show-dialog",{dialogTag:"dialog-data-entry-flow",dialogImport:a,dialogParams:{...t,flowConfig:o,dialogParentElement:e}})}},40386:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t),o.d(t,{DialogHelperDetail:()=>B});var a=o(62826),n=o(96196),r=o(77845),s=o(94333),l=o(22786),d=o(92209),h=o(51757),c=o(92542),p=o(55124),u=o(25749),m=o(95637),g=(o(75261),o(89473)),_=(o(56565),o(89600)),f=(o(60961),o(88422)),w=o(23608),y=o(96643),b=o(90536),v=o(97666),$=o(991),k=o(71435),z=o(91482),x=o(50085),C=o(84125),F=o(72550),A=o(12134),D=o(73042),M=o(39396),T=o(76681),P=o(50218),E=e([g,_,f]);[g,_,f]=E.then?(await E)():E;const S="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",L={input_boolean:{create:b.nr,import:()=>Promise.all([o.e("8654"),o.e("1120")]).then(o.bind(o,75027)),alias:["switch","toggle"]},input_button:{create:v.L6,import:()=>Promise.all([o.e("8654"),o.e("9886")]).then(o.bind(o,84957))},input_text:{create:x.m4,import:()=>Promise.all([o.e("8654"),o.e("1279"),o.e("9505")]).then(o.bind(o,46584))},input_number:{create:k.gO,import:()=>Promise.all([o.e("8654"),o.e("1279"),o.e("2259")]).then(o.bind(o,56318))},input_datetime:{create:$.ke,import:()=>Promise.all([o.e("8654"),o.e("1279"),o.e("7319")]).then(o.bind(o,31978))},input_select:{create:z.BT,import:()=>Promise.all([o.e("8654"),o.e("4358")]).then(o.bind(o,24933)),alias:["select","dropdown"]},counter:{create:y.Pu,import:()=>Promise.all([o.e("8654"),o.e("2379")]).then(o.bind(o,77238))},timer:{create:A.CR,import:()=>Promise.all([o.e("2239"),o.e("7251"),o.e("3577"),o.e("8654"),o.e("8477"),o.e("3777"),o.e("8350")]).then(o.bind(o,55421)),alias:["countdown"]},schedule:{create:F.sF,import:()=>Promise.all([o.e("8654"),o.e("9963"),o.e("6162")]).then(o.bind(o,60649))}};class B extends n.WF{async showDialog(e){this._params=e,this._domain=e.domain,this._item=void 0,this._domain&&this._domain in L&&await L[this._domain].import(),this._opened=!0,await this.updateComplete,this.hass.loadFragmentTranslation("config");const t=await(0,w.yu)(this.hass,["helper"]);await this.hass.loadBackendTranslation("title",t,!0),this._helperFlows=t}closeDialog(){this._opened=!1,this._error=void 0,this._domain=void 0,this._params=void 0,this._filter=void 0,(0,c.r)(this,"dialog-closed",{dialog:this.localName})}render(){if(!this._opened)return n.s6;let e;if(this._domain)e=n.qy`
        <div class="form" @value-changed=${this._valueChanged}>
          ${this._error?n.qy`<div class="error">${this._error}</div>`:""}
          ${(0,h._)(`ha-${this._domain}-form`,{hass:this.hass,item:this._item,new:!0})}
        </div>
        <ha-button
          slot="primaryAction"
          @click=${this._createItem}
          .disabled=${this._submitting}
        >
          ${this.hass.localize("ui.panel.config.helpers.dialog.create")}
        </ha-button>
        ${this._params?.domain?n.s6:n.qy`<ha-button
              appearance="plain"
              slot="secondaryAction"
              @click=${this._goBack}
              .disabled=${this._submitting}
            >
              ${this.hass.localize("ui.common.back")}
            </ha-button>`}
      `;else if(this._loading||void 0===this._helperFlows)e=n.qy`<ha-spinner></ha-spinner>`;else{const t=this._filterHelpers(L,this._helperFlows,this._filter);e=n.qy`
        <search-input
          .hass=${this.hass}
          dialogInitialFocus="true"
          .filter=${this._filter}
          @value-changed=${this._filterChanged}
          .label=${this.hass.localize("ui.panel.config.integrations.search_helper")}
        ></search-input>
        <ha-list
          class="ha-scrollbar"
          innerRole="listbox"
          itemRoles="option"
          innerAriaLabel=${this.hass.localize("ui.panel.config.helpers.dialog.create_helper")}
          rootTabbable
          dialogInitialFocus
        >
          ${t.map((([e,t])=>{const o=!(e in L)||(0,d.x)(this.hass,e);return n.qy`
              <ha-list-item
                .disabled=${!o}
                hasmeta
                .domain=${e}
                @request-selected=${this._domainPicked}
                graphic="icon"
              >
                <img
                  slot="graphic"
                  loading="lazy"
                  alt=""
                  src=${(0,T.MR)({domain:e,type:"icon",useFallback:!0,darkOptimized:this.hass.themes?.darkMode})}
                  crossorigin="anonymous"
                  referrerpolicy="no-referrer"
                />
                <span class="item-text"> ${t} </span>
                ${o?n.qy`<ha-icon-next slot="meta"></ha-icon-next>`:n.qy` <ha-svg-icon
                        slot="meta"
                        .id="icon-${e}"
                        path=${S}
                        @click=${p.d}
                      ></ha-svg-icon>
                      <ha-tooltip .for="icon-${e}">
                        ${this.hass.localize("ui.dialogs.helper_settings.platform_not_loaded",{platform:e})}
                      </ha-tooltip>`}
              </ha-list-item>
            `}))}
        </ha-list>
      `}return n.qy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        class=${(0,s.H)({"button-left":!this._domain})}
        scrimClickAction
        escapeKeyAction
        .hideActions=${!this._domain}
        .heading=${(0,m.l)(this.hass,this._domain?this.hass.localize("ui.panel.config.helpers.dialog.create_platform",{platform:(0,P.z)(this._domain)&&this.hass.localize(`ui.panel.config.helpers.types.${this._domain}`)||this._domain}):this.hass.localize("ui.panel.config.helpers.dialog.create_helper"))}
      >
        ${e}
      </ha-dialog>
    `}async _filterChanged(e){this._filter=e.detail.value}_valueChanged(e){this._item=e.detail.value}async _createItem(){if(this._domain&&this._item){this._submitting=!0,this._error="";try{const e=await L[this._domain].create(this.hass,this._item);this._params?.dialogClosedCallback&&e.id&&this._params.dialogClosedCallback({flowFinished:!0,entityId:`${this._domain}.${e.id}`}),this.closeDialog()}catch(e){this._error=e.message||"Unknown error"}finally{this._submitting=!1}}}async _domainPicked(e){const t=e.target.closest("ha-list-item").domain;if(t in L){this._loading=!0;try{await L[t].import(),this._domain=t}finally{this._loading=!1}this._focusForm()}else(0,D.W)(this,{startFlowHandler:t,manifest:await(0,C.QC)(this.hass,t),dialogClosedCallback:this._params.dialogClosedCallback}),this.closeDialog()}async _focusForm(){await this.updateComplete,(this._form?.lastElementChild).focus()}_goBack(){this._domain=void 0,this._item=void 0,this._error=void 0}static get styles(){return[M.dp,M.nA,n.AH`
        ha-dialog.button-left {
          --justify-action-buttons: flex-start;
        }
        ha-dialog {
          --dialog-content-padding: 0;
          --dialog-scroll-divider-color: transparent;
          --mdc-dialog-max-height: 90vh;
        }
        @media all and (min-width: 550px) {
          ha-dialog {
            --mdc-dialog-min-width: 500px;
          }
        }
        ha-icon-next {
          width: 24px;
        }
        ha-tooltip {
          pointer-events: auto;
        }
        .form {
          padding: 24px;
        }
        search-input {
          display: block;
          margin: 16px 16px 0;
        }
        ha-list {
          height: calc(60vh - 184px);
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          ha-list {
            height: calc(
              100vh -
                184px - var(--safe-area-inset-top, 0px) - var(
                  --safe-area-inset-bottom,
                  0px
                )
            );
          }
        }
      `]}constructor(...e){super(...e),this._opened=!1,this._submitting=!1,this._loading=!1,this._filterHelpers=(0,l.A)(((e,t,o)=>{const i=[];for(const a of Object.keys(e))i.push([a,this.hass.localize(`ui.panel.config.helpers.types.${a}`)||a]);if(t)for(const a of t)i.push([a,(0,C.p$)(this.hass.localize,a)]);return i.filter((([t,i])=>{if(o){const a=o.toLowerCase();return i.toLowerCase().includes(a)||t.toLowerCase().includes(a)||(e[t]?.alias||[]).some((e=>e.toLowerCase().includes(a)))}return!0})).sort(((e,t)=>(0,u.xL)(e[1],t[1],this.hass.locale.language)))}))}}(0,a.__decorate)([(0,r.MZ)({attribute:!1})],B.prototype,"hass",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_item",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_opened",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_domain",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_error",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_submitting",void 0),(0,a.__decorate)([(0,r.P)(".form")],B.prototype,"_form",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_helperFlows",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_loading",void 0),(0,a.__decorate)([(0,r.wk)()],B.prototype,"_filter",void 0),B=(0,a.__decorate)([(0,r.EM)("dialog-helper-detail")],B),i()}catch(S){i(S)}}))},76681:function(e,t,o){o.d(t,{MR:()=>i,a_:()=>a,bg:()=>n});const i=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,a=e=>e.split("/")[4],n=e=>e.startsWith("https://brands.home-assistant.io/")},61171:function(e,t,o){o.d(t,{A:()=>i});const i=o(96196).AH`:host {
  --max-width: 30ch;
  display: inline-block;
  position: absolute;
  color: var(--wa-tooltip-content-color);
  font-size: var(--wa-tooltip-font-size);
  line-height: var(--wa-tooltip-line-height);
  text-align: start;
  white-space: normal;
}
.tooltip {
  --arrow-size: var(--wa-tooltip-arrow-size);
  --arrow-color: var(--wa-tooltip-background-color);
}
.tooltip::part(popup) {
  z-index: 1000;
}
.tooltip[placement^=top]::part(popup) {
  transform-origin: bottom;
}
.tooltip[placement^=bottom]::part(popup) {
  transform-origin: top;
}
.tooltip[placement^=left]::part(popup) {
  transform-origin: right;
}
.tooltip[placement^=right]::part(popup) {
  transform-origin: left;
}
.body {
  display: block;
  width: max-content;
  max-width: var(--max-width);
  border-radius: var(--wa-tooltip-border-radius);
  background-color: var(--wa-tooltip-background-color);
  border: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  padding: 0.25em 0.5em;
  user-select: none;
  -webkit-user-select: none;
}
.tooltip::part(arrow) {
  border-bottom: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  border-right: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
}
`},52630:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{A:()=>$});var a=o(96196),n=o(77845),r=o(94333),s=o(17051),l=o(42462),d=o(28438),h=o(98779),c=o(27259),p=o(984),u=o(53720),m=o(9395),g=o(32510),_=o(40158),f=o(61171),w=e([_]);_=(w.then?(await w)():w)[0];var y=Object.defineProperty,b=Object.getOwnPropertyDescriptor,v=(e,t,o,i)=>{for(var a,n=i>1?void 0:i?b(t,o):t,r=e.length-1;r>=0;r--)(a=e[r])&&(n=(i?a(t,o,n):a(n))||n);return i&&n&&y(t,o,n),n};let $=class extends g.A{connectedCallback(){super.connectedCallback(),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,u.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}disconnectedCallback(){super.disconnectedCallback(),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}firstUpdated(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}hasTrigger(e){return this.trigger.split(" ").includes(e)}addToAriaLabelledBy(e,t){const o=(e.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);o.includes(t)||(o.push(t),e.setAttribute("aria-labelledby",o.join(" ")))}removeFromAriaLabelledBy(e,t){const o=(e.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((e=>e!==t));o.length>0?e.setAttribute("aria-labelledby",o.join(" ")):e.removeAttribute("aria-labelledby")}async handleOpenChange(){if(this.open){if(this.disabled)return;const e=new h.k;if(this.dispatchEvent(e),e.defaultPrevented)return void(this.open=!1);document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,await(0,c.Ud)(this.popup.popup,"show-with-scale"),this.popup.reposition(),this.dispatchEvent(new l.q)}else{const e=new d.L;if(this.dispatchEvent(e),e.defaultPrevented)return void(this.open=!1);document.removeEventListener("keydown",this.handleDocumentKeyDown),await(0,c.Ud)(this.popup.popup,"hide-with-scale"),this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new s.Z)}}handleForChange(){const e=this.getRootNode();if(!e)return;const t=this.for?e.getElementById(this.for):null,o=this.anchor;if(t===o)return;const{signal:i}=this.eventController;t&&(this.addToAriaLabelledBy(t,this.id),t.addEventListener("blur",this.handleBlur,{capture:!0,signal:i}),t.addEventListener("focus",this.handleFocus,{capture:!0,signal:i}),t.addEventListener("click",this.handleClick,{signal:i}),t.addEventListener("mouseover",this.handleMouseOver,{signal:i}),t.addEventListener("mouseout",this.handleMouseOut,{signal:i})),o&&(this.removeFromAriaLabelledBy(o,this.id),o.removeEventListener("blur",this.handleBlur,{capture:!0}),o.removeEventListener("focus",this.handleFocus,{capture:!0}),o.removeEventListener("click",this.handleClick),o.removeEventListener("mouseover",this.handleMouseOver),o.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=t}async handleOptionsChange(){this.hasUpdated&&(await this.updateComplete,this.popup.reposition())}handleDisabledChange(){this.disabled&&this.open&&this.hide()}async show(){if(!this.open)return this.open=!0,(0,p.l)(this,"wa-after-show")}async hide(){if(this.open)return this.open=!1,(0,p.l)(this,"wa-after-hide")}render(){return a.qy`
      <wa-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${(0,r.H)({tooltip:!0,"tooltip-open":this.open})}
        placement=${this.placement}
        distance=${this.distance}
        skidding=${this.skidding}
        flip
        shift
        ?arrow=${!this.withoutArrow}
        hover-bridge
        .anchor=${this.anchor}
      >
        <div part="body" class="body">
          <slot></slot>
        </div>
      </wa-popup>
    `}constructor(){super(...arguments),this.placement="top",this.disabled=!1,this.distance=8,this.open=!1,this.skidding=0,this.showDelay=150,this.hideDelay=0,this.trigger="hover focus",this.withoutArrow=!1,this.for=null,this.anchor=null,this.eventController=new AbortController,this.handleBlur=()=>{this.hasTrigger("focus")&&this.hide()},this.handleClick=()=>{this.hasTrigger("click")&&(this.open?this.hide():this.show())},this.handleFocus=()=>{this.hasTrigger("focus")&&this.show()},this.handleDocumentKeyDown=e=>{"Escape"===e.key&&(e.stopPropagation(),this.hide())},this.handleMouseOver=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.show()),this.showDelay))},this.handleMouseOut=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.hide()),this.hideDelay))}}};$.css=f.A,$.dependencies={"wa-popup":_.A},v([(0,n.P)("slot:not([name])")],$.prototype,"defaultSlot",2),v([(0,n.P)(".body")],$.prototype,"body",2),v([(0,n.P)("wa-popup")],$.prototype,"popup",2),v([(0,n.MZ)()],$.prototype,"placement",2),v([(0,n.MZ)({type:Boolean,reflect:!0})],$.prototype,"disabled",2),v([(0,n.MZ)({type:Number})],$.prototype,"distance",2),v([(0,n.MZ)({type:Boolean,reflect:!0})],$.prototype,"open",2),v([(0,n.MZ)({type:Number})],$.prototype,"skidding",2),v([(0,n.MZ)({attribute:"show-delay",type:Number})],$.prototype,"showDelay",2),v([(0,n.MZ)({attribute:"hide-delay",type:Number})],$.prototype,"hideDelay",2),v([(0,n.MZ)()],$.prototype,"trigger",2),v([(0,n.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],$.prototype,"withoutArrow",2),v([(0,n.MZ)()],$.prototype,"for",2),v([(0,n.wk)()],$.prototype,"anchor",2),v([(0,m.w)("open",{waitUntilFirstUpdate:!0})],$.prototype,"handleOpenChange",1),v([(0,m.w)("for")],$.prototype,"handleForChange",1),v([(0,m.w)(["distance","placement","skidding"])],$.prototype,"handleOptionsChange",1),v([(0,m.w)("disabled")],$.prototype,"handleDisabledChange",1),$=v([(0,n.EM)("wa-tooltip")],$),i()}catch($){i($)}}))}};
//# sourceMappingURL=8991.82f6d0b3bc3cf940.js.map