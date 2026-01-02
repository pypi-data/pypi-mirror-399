export const __webpack_id__="6133";export const __webpack_ids__=["6133"];export const __webpack_modules__={48565:function(e,t,i){i.d(t,{d:()=>o});const o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},485:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(62826),a=(i(63687),i(96196)),r=i(77845),n=i(94333),s=i(92542),l=i(89473),d=(i(60733),i(48565)),c=i(55376),p=i(78436),h=e([l]);l=(h.then?(await h)():h)[0];const u="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",v="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z";class _ extends a.WF{firstUpdated(e){super.firstUpdated(e),this.autoOpenFileDialog&&this._openFilePicker()}get _name(){if(void 0===this.value)return"";if("string"==typeof this.value)return this.value;return(this.value instanceof FileList?Array.from(this.value):(0,c.e)(this.value)).map((e=>e.name)).join(", ")}render(){const e=this.localize||this.hass.localize;return a.qy`
      ${this.uploading?a.qy`<div class="container">
            <div class="uploading">
              <span class="header"
                >${this.uploadingLabel||(this.value?e("ui.components.file-upload.uploading_name",{name:this._name}):e("ui.components.file-upload.uploading"))}</span
              >
              ${this.progress?a.qy`<div class="progress">
                    ${this.progress}${this.hass&&(0,d.d)(this.hass.locale)}%
                  </div>`:a.s6}
            </div>
            <mwc-linear-progress
              .indeterminate=${!this.progress}
              .progress=${this.progress?this.progress/100:void 0}
            ></mwc-linear-progress>
          </div>`:a.qy`<label
            for=${this.value?"":"input"}
            class="container ${(0,n.H)({dragged:this._drag,multiple:this.multiple,value:Boolean(this.value)})}"
            @drop=${this._handleDrop}
            @dragenter=${this._handleDragStart}
            @dragover=${this._handleDragStart}
            @dragleave=${this._handleDragEnd}
            @dragend=${this._handleDragEnd}
            >${this.value?"string"==typeof this.value?a.qy`<div class="row">
                    <div class="value" @click=${this._openFilePicker}>
                      <ha-svg-icon
                        .path=${this.icon||v}
                      ></ha-svg-icon>
                      ${this.value}
                    </div>
                    <ha-icon-button
                      @click=${this._clearValue}
                      .label=${this.deleteLabel||e("ui.common.delete")}
                      .path=${u}
                    ></ha-icon-button>
                  </div>`:(this.value instanceof FileList?Array.from(this.value):(0,c.e)(this.value)).map((t=>a.qy`<div class="row">
                        <div class="value" @click=${this._openFilePicker}>
                          <ha-svg-icon
                            .path=${this.icon||v}
                          ></ha-svg-icon>
                          ${t.name} - ${(0,p.A)(t.size)}
                        </div>
                        <ha-icon-button
                          @click=${this._clearValue}
                          .label=${this.deleteLabel||e("ui.common.delete")}
                          .path=${u}
                        ></ha-icon-button>
                      </div>`)):a.qy`<ha-button
                    size="small"
                    appearance="filled"
                    @click=${this._openFilePicker}
                  >
                    <ha-svg-icon
                      slot="start"
                      .path=${this.icon||v}
                    ></ha-svg-icon>
                    ${this.label||e("ui.components.file-upload.label")}
                  </ha-button>
                  <span class="secondary"
                    >${this.secondary||e("ui.components.file-upload.secondary")}</span
                  >
                  <span class="supports">${this.supports}</span>`}
            <input
              id="input"
              type="file"
              class="file"
              .accept=${this.accept}
              .multiple=${this.multiple}
              @change=${this._handleFilePicked}
          /></label>`}
    `}_openFilePicker(){this._input?.click()}_handleDrop(e){e.preventDefault(),e.stopPropagation(),e.dataTransfer?.files&&(0,s.r)(this,"file-picked",{files:this.multiple||1===e.dataTransfer.files.length?Array.from(e.dataTransfer.files):[e.dataTransfer.files[0]]}),this._drag=!1}_handleDragStart(e){e.preventDefault(),e.stopPropagation(),this._drag=!0}_handleDragEnd(e){e.preventDefault(),e.stopPropagation(),this._drag=!1}_handleFilePicked(e){0!==e.target.files.length&&(this.value=e.target.files,(0,s.r)(this,"file-picked",{files:e.target.files}))}_clearValue(e){e.preventDefault(),this._input.value="",this.value=void 0,(0,s.r)(this,"change"),(0,s.r)(this,"files-cleared")}constructor(...e){super(...e),this.multiple=!1,this.disabled=!1,this.uploading=!1,this.autoOpenFileDialog=!1,this._drag=!1}}_.styles=a.AH`
    :host {
      display: block;
      height: 240px;
    }
    :host([disabled]) {
      pointer-events: none;
      color: var(--disabled-text-color);
    }
    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      border: solid 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      border-radius: var(--mdc-shape-small, var(--ha-border-radius-sm));
      height: 100%;
    }
    .row {
      display: flex;
      align-items: center;
    }
    label.container {
      border: dashed 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      cursor: pointer;
    }
    .container .uploading {
      display: flex;
      flex-direction: column;
      width: 100%;
      align-items: flex-start;
      padding: 0 32px;
      box-sizing: border-box;
    }
    :host([disabled]) .container {
      border-color: var(--disabled-color);
    }
    label:hover,
    label.dragged {
      border-style: solid;
    }
    label.dragged {
      border-color: var(--primary-color);
    }
    .dragged:before {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background-color: var(--primary-color);
      content: "";
      opacity: var(--dark-divider-opacity);
      pointer-events: none;
      border-radius: var(--mdc-shape-small, 4px);
    }
    label.value {
      cursor: default;
    }
    label.value.multiple {
      justify-content: unset;
      overflow: auto;
    }
    .highlight {
      color: var(--primary-color);
    }
    ha-button {
      margin-bottom: 8px;
    }
    .supports {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
    :host([disabled]) .secondary {
      color: var(--disabled-text-color);
    }
    input.file {
      display: none;
    }
    .value {
      cursor: pointer;
    }
    .value ha-svg-icon {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
    ha-button {
      --mdc-button-outline-color: var(--primary-color);
      --mdc-icon-button-size: 24px;
    }
    mwc-linear-progress {
      width: 100%;
      padding: 8px 32px;
      box-sizing: border-box;
    }
    .header {
      font-weight: var(--ha-font-weight-medium);
    }
    .progress {
      color: var(--secondary-text-color);
    }
    button.link {
      background: none;
      border: none;
      padding: 0;
      font-size: var(--ha-font-size-m);
      color: var(--primary-color);
      text-decoration: underline;
      cursor: pointer;
    }
  `,(0,o.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],_.prototype,"localize",void 0),(0,o.__decorate)([(0,r.MZ)()],_.prototype,"accept",void 0),(0,o.__decorate)([(0,r.MZ)()],_.prototype,"icon",void 0),(0,o.__decorate)([(0,r.MZ)()],_.prototype,"label",void 0),(0,o.__decorate)([(0,r.MZ)()],_.prototype,"secondary",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"uploading-label"})],_.prototype,"uploadingLabel",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"delete-label"})],_.prototype,"deleteLabel",void 0),(0,o.__decorate)([(0,r.MZ)()],_.prototype,"supports",void 0),(0,o.__decorate)([(0,r.MZ)({type:Object})],_.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],_.prototype,"multiple",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],_.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],_.prototype,"uploading",void 0),(0,o.__decorate)([(0,r.MZ)({type:Number})],_.prototype,"progress",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,attribute:"auto-open-file-dialog"})],_.prototype,"autoOpenFileDialog",void 0),(0,o.__decorate)([(0,r.wk)()],_.prototype,"_drag",void 0),(0,o.__decorate)([(0,r.P)("#input")],_.prototype,"_input",void 0),_=(0,o.__decorate)([(0,r.EM)("ha-file-upload")],_),t()}catch(u){t(u)}}))},31169:function(e,t,i){i.d(t,{Q:()=>o,n:()=>a});const o=async(e,t)=>{const i=new FormData;i.append("file",t);const o=await e.fetchWithAuth("/api/file_upload",{method:"POST",body:i});if(413===o.status)throw new Error(`Uploaded file is too large (${t.name})`);if(200!==o.status)throw new Error("Unknown error");return(await o.json()).file_id},a=async(e,t)=>e.callApi("DELETE","file_upload",{file_id:t})},95260:function(e,t,i){i.d(t,{PS:()=>o,VR:()=>a});const o=e=>e.data,a=e=>"object"==typeof e?"object"==typeof e.body?e.body.message||"Unknown error, see supervisor logs":e.body||e.message||"Unknown error, see supervisor logs":e;new Set([502,503,504])},10234:function(e,t,i){i.d(t,{K$:()=>n,an:()=>l,dk:()=>s});var o=i(92542);const a=()=>Promise.all([i.e("6009"),i.e("5791"),i.e("5463")]).then(i.bind(i,22316)),r=(e,t,i)=>new Promise((r=>{const n=t.cancel,s=t.confirm;(0,o.r)(e,"show-dialog",{dialogTag:"dialog-box",dialogImport:a,dialogParams:{...t,...i,cancel:()=>{r(!!i?.prompt&&null),n&&n()},confirm:e=>{r(!i?.prompt||e),s&&s(e)}}})})),n=(e,t)=>r(e,t),s=(e,t)=>r(e,t,{confirmation:!0}),l=(e,t)=>r(e,t,{prompt:!0})},78436:function(e,t,i){i.d(t,{A:()=>o});const o=(e=0,t=2)=>{if(0===e)return"0 Bytes";t=t<0?0:t;const i=Math.floor(Math.log(e)/Math.log(1024));return`${parseFloat((e/1024**i).toFixed(t))} ${["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][i]}`}},6431:function(e,t,i){i.d(t,{x:()=>o});const o="2025.12.28.215221"},45812:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{KNXInfo:()=>k});var a=i(62826),r=i(96196),n=i(77845),s=i(92542),l=(i(95379),i(29937),i(89473)),d=i(485),c=i(81774),p=i(31169),h=i(95260),u=i(10234),v=i(65294),_=i(78577),f=i(6431),g=i(16404),x=e([l,d,c]);[l,d,c]=x.then?(await x)():x;const m="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z",b=new _.Q("info");class k extends r.WF{render(){return r.qy`
      <hass-subpage
        .hass=${this.hass}
        .narrow=${this.narrow}
        back-path=${g.C1}
        .header=${this.knx.localize(g.SC.translationKey)}
      >
        <div class="columns">
          ${this._renderInfoCard()}
          ${this.knx.projectInfo?this._renderProjectDataCard(this.knx.projectInfo):r.s6}
          ${this._renderProjectUploadCard()}
        </div>
      </hass-subpage>
    `}_renderInfoCard(){return r.qy` <ha-card class="knx-info">
      <div class="card-content knx-info-section">
        <div class="knx-content-row header">${this.knx.localize("info_information_header")}</div>

        <div class="knx-content-row">
          <div>XKNX Version</div>
          <div>${this.knx.connectionInfo.version}</div>
        </div>

        <div class="knx-content-row">
          <div>KNX-Frontend Version</div>
          <div>${f.x}</div>
        </div>

        <div class="knx-content-row">
          <div>${this.knx.localize("info_connected_to_bus")}</div>
          <div>
            ${this.hass.localize(this.knx.connectionInfo.connected?"ui.common.yes":"ui.common.no")}
          </div>
        </div>

        <div class="knx-content-row">
          <div>${this.knx.localize("info_individual_address")}</div>
          <div>${this.knx.connectionInfo.current_address}</div>
        </div>

        <div class="knx-bug-report">
          ${this.knx.localize("info_issue_tracker")}
          <a href="https://github.com/XKNX/knx-integration" target="_blank">xknx/knx-integration</a>
        </div>

        <div class="knx-bug-report">
          ${this.knx.localize("info_my_knx")}
          <a href="https://my.knx.org" target="_blank">my.knx.org</a>
        </div>
      </div>
    </ha-card>`}_renderProjectDataCard(e){return r.qy`
      <ha-card class="knx-info">
          <div class="card-content knx-content">
            <div class="header knx-content-row">
              ${this.knx.localize("info_project_data_header")}
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_name")}</div>
              <div>${e.name}</div>
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_last_modified")}</div>
              <div>${new Date(e.last_modified).toUTCString()}</div>
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_tool_version")}</div>
              <div>${e.tool_version}</div>
            </div>
            <div class="knx-content-row">
              <div>${this.knx.localize("info_project_data_xknxproject_version")}</div>
              <div>${e.xknxproject_version}</div>
            </div>
            <div class="knx-button-row">
              <ha-button
                class="knx-warning push-right"
                @click=${this._removeProject}
                .disabled=${this._uploading||!this.knx.projectInfo}
                >
                ${this.knx.localize("info_project_delete")}
              </ha-button>
            </div>
          </div>
        </div>
      </ha-card>
    `}_renderProjectUploadCard(){return r.qy` <ha-card class="knx-info">
      <div class="card-content knx-content">
        <div class="knx-content-row header">${this.knx.localize("info_project_file_header")}</div>
        <div class="knx-content-row">${this.knx.localize("info_project_upload_description")}</div>
        <div class="knx-content-row">
          <ha-file-upload
            .hass=${this.hass}
            accept=".knxproj, .knxprojarchive"
            .icon=${m}
            .label=${this.knx.localize("info_project_file")}
            .value=${this._projectFile?.name}
            .uploading=${this._uploading}
            @file-picked=${this._filePicked}
          ></ha-file-upload>
        </div>
        <div class="knx-content-row">
          <ha-selector-text
            .hass=${this.hass}
            .value=${this._projectPassword||""}
            .label=${this.hass.localize("ui.login-form.password")}
            .selector=${{text:{multiline:!1,type:"password"}}}
            .required=${!1}
            @value-changed=${this._passwordChanged}
          >
          </ha-selector-text>
        </div>
        <div class="knx-button-row">
          <ha-button
            class="push-right"
            @click=${this._uploadFile}
            .disabled=${this._uploading||!this._projectFile}
            >${this.hass.localize("ui.common.submit")}</ha-button
          >
        </div>
      </div>
    </ha-card>`}_filePicked(e){this._projectFile=e.detail.files[0]}_passwordChanged(e){this._projectPassword=e.detail.value}async _uploadFile(e){const t=this._projectFile;if(void 0===t)return;let i;this._uploading=!0;try{const e=await(0,p.Q)(this.hass,t);await(0,v.dc)(this.hass,e,this._projectPassword||"")}catch(o){i=o,(0,u.K$)(this,{title:"Upload failed",text:(0,h.VR)(o)})}finally{i||(this._projectFile=void 0,this._projectPassword=void 0),this._uploading=!1,(0,s.r)(this,"knx-reload")}}async _removeProject(e){if(await(0,u.dk)(this,{text:this.knx.localize("info_project_delete")}))try{await(0,v.gV)(this.hass)}catch(t){(0,u.K$)(this,{title:"Deletion failed",text:(0,h.VR)(t)})}finally{(0,s.r)(this,"knx-reload")}else b.debug("User cancelled deletion")}constructor(...e){super(...e),this._uploading=!1}}k.styles=r.AH`
    .columns {
      display: flex;
      justify-content: center;
    }

    @media screen and (max-width: 1232px) {
      .columns {
        flex-direction: column;
      }

      .knx-button-row {
        margin-top: 20px;
      }

      .knx-info {
        margin-right: 8px;
      }
    }

    @media screen and (min-width: 1233px) {
      .knx-button-row {
        margin-top: auto;
      }

      .knx-info {
        width: 400px;
      }
    }

    .knx-info {
      margin-left: 8px;
      margin-top: 8px;
    }

    .knx-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      box-sizing: border-box;
    }

    .knx-content-row {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
    }

    .knx-content-row > div:nth-child(2) {
      margin-left: 1rem;
    }

    .knx-button-row {
      display: flex;
      flex-direction: row;
      vertical-align: bottom;
      padding-top: 16px;
    }

    .push-left {
      margin-right: auto;
    }

    .push-right {
      margin-left: auto;
    }

    .knx-warning {
      --mdc-theme-primary: var(--error-color);
    }

    .knx-project-description {
      margin-top: -8px;
      padding: 0px 16px 16px;
    }

    .knx-delete-project-button {
      position: absolute;
      bottom: 0;
      right: 0;
    }

    .knx-bug-report {
      margin-top: 20px;

      a {
        text-decoration: none;
      }
    }

    .header {
      color: var(--ha-card-header-color, --primary-text-color);
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, 24px);
      letter-spacing: -0.012em;
      line-height: 48px;
      padding: -4px 16px 16px;
      display: inline-block;
      margin-block-start: 0px;
      margin-block-end: 4px;
      font-weight: normal;
    }

    ha-file-upload,
    ha-selector-text {
      width: 100%;
      margin-top: 8px;
    }
  `,(0,a.__decorate)([(0,n.MZ)({type:Object})],k.prototype,"hass",void 0),(0,a.__decorate)([(0,n.MZ)({attribute:!1})],k.prototype,"knx",void 0),(0,a.__decorate)([(0,n.MZ)({type:Boolean,reflect:!0})],k.prototype,"narrow",void 0),(0,a.__decorate)([(0,n.MZ)({type:Object})],k.prototype,"route",void 0),(0,a.__decorate)([(0,n.wk)()],k.prototype,"_projectPassword",void 0),(0,a.__decorate)([(0,n.wk)()],k.prototype,"_uploading",void 0),(0,a.__decorate)([(0,n.wk)()],k.prototype,"_projectFile",void 0),k=(0,a.__decorate)([(0,n.EM)("knx-info")],k),o()}catch(m){o(m)}}))}};
//# sourceMappingURL=6133.faff19a39ffd2879.js.map