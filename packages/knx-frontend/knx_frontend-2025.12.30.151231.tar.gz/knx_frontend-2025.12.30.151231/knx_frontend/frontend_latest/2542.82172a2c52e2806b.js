export const __webpack_id__="2542";export const __webpack_ids__=["2542"];export const __webpack_modules__={96573:function(e,a,s){s.a(e,(async function(e,i){try{s.r(a);var t=s(62826),o=s(96196),r=s(77845),l=s(4937),h=s(22786),d=s(92542),n=(s(96294),s(25388),s(17963),s(45783)),c=s(53907),_=s(89473),p=s(95637),u=(s(88867),s(41881)),m=(s(2809),s(60961),s(78740),s(54110)),v=s(39396),g=s(82160),f=e([n,c,_,u]);[n,c,_,u]=f.then?(await f)():f;const y="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z";class $ extends o.WF{showDialog(e){this._params=e,this._error=void 0,this._name=this._params.entry?this._params.entry.name:this._params.suggestedName||"",this._aliases=this._params.entry?.aliases||[],this._icon=this._params.entry?.icon||null,this._level=this._params.entry?.level??null,this._addedAreas.clear(),this._removedAreas.clear()}closeDialog(){this._error="",this._params=void 0,this._addedAreas.clear(),this._removedAreas.clear(),(0,d.r)(this,"dialog-closed",{dialog:this.localName})}render(){const e=this._floorAreas(this._params?.entry,this.hass.areas,this._addedAreas,this._removedAreas);if(!this._params)return o.s6;const a=this._params.entry,s=!this._isNameValid();return o.qy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        .heading=${(0,p.l)(this.hass,a?this.hass.localize("ui.panel.config.floors.editor.update_floor"):this.hass.localize("ui.panel.config.floors.editor.create_floor"))}
      >
        <div>
          ${this._error?o.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
          <div class="form">
            ${a?o.qy`
                  <ha-settings-row>
                    <span slot="heading">
                      ${this.hass.localize("ui.panel.config.floors.editor.floor_id")}
                    </span>
                    <span slot="description">${a.floor_id}</span>
                  </ha-settings-row>
                `:o.s6}

            <ha-textfield
              .value=${this._name}
              @input=${this._nameChanged}
              .label=${this.hass.localize("ui.panel.config.floors.editor.name")}
              .validationMessage=${this.hass.localize("ui.panel.config.floors.editor.name_required")}
              required
              dialogInitialFocus
            ></ha-textfield>

            <ha-textfield
              .value=${this._level}
              @input=${this._levelChanged}
              .label=${this.hass.localize("ui.panel.config.floors.editor.level")}
              type="number"
              .helper=${this.hass.localize("ui.panel.config.floors.editor.level_helper")}
              helperPersistent
            ></ha-textfield>

            <ha-icon-picker
              .hass=${this.hass}
              .value=${this._icon}
              @value-changed=${this._iconChanged}
              .label=${this.hass.localize("ui.panel.config.areas.editor.icon")}
            >
              ${this._icon?o.s6:o.qy`
                    <ha-floor-icon
                      slot="fallback"
                      .floor=${{level:this._level}}
                    ></ha-floor-icon>
                  `}
            </ha-icon-picker>

            <h3 class="header">
              ${this.hass.localize("ui.panel.config.floors.editor.areas_section")}
            </h3>

            ${e.length?o.qy`<ha-chip-set>
                  ${(0,l.u)(e,(e=>e.area_id),(e=>o.qy`<ha-input-chip
                        .area=${e}
                        @click=${this._openArea}
                        @remove=${this._removeArea}
                        .label=${e?.name}
                      >
                        ${e.icon?o.qy`<ha-icon
                              slot="icon"
                              .icon=${e.icon}
                            ></ha-icon>`:o.qy`<ha-svg-icon
                              slot="icon"
                              .path=${y}
                            ></ha-svg-icon>`}
                      </ha-input-chip>`))}
                </ha-chip-set>`:o.qy`<p class="description">
                  ${this.hass.localize("ui.panel.config.floors.editor.areas_description")}
                </p>`}
            <ha-area-picker
              no-add
              .hass=${this.hass}
              @value-changed=${this._addArea}
              .excludeAreas=${e.map((e=>e.area_id))}
              .addButtonLabel=${this.hass.localize("ui.panel.config.floors.editor.add_area")}
            ></ha-area-picker>

            <h3 class="header">
              ${this.hass.localize("ui.panel.config.floors.editor.aliases_section")}
            </h3>

            <p class="description">
              ${this.hass.localize("ui.panel.config.floors.editor.aliases_description")}
            </p>
            <ha-aliases-editor
              .hass=${this.hass}
              .aliases=${this._aliases}
              @value-changed=${this._aliasesChanged}
            ></ha-aliases-editor>
          </div>
        </div>
        <ha-button
          appearance="plain"
          slot="secondaryAction"
          @click=${this.closeDialog}
        >
          ${this.hass.localize("ui.common.cancel")}
        </ha-button>
        <ha-button
          slot="primaryAction"
          @click=${this._updateEntry}
          .disabled=${s||!!this._submitting}
        >
          ${a?this.hass.localize("ui.common.save"):this.hass.localize("ui.common.create")}
        </ha-button>
      </ha-dialog>
    `}_openArea(e){const a=e.target.area;(0,g.J)(this,{entry:a,updateEntry:e=>(0,m.gs)(this.hass,a.area_id,e)})}_removeArea(e){const a=e.target.area.area_id;if(this._addedAreas.has(a))return this._addedAreas.delete(a),void(this._addedAreas=new Set(this._addedAreas));this._removedAreas.add(a),this._removedAreas=new Set(this._removedAreas)}_addArea(e){const a=e.detail.value;if(a){if(e.target.value="",this._removedAreas.has(a))return this._removedAreas.delete(a),void(this._removedAreas=new Set(this._removedAreas));this._addedAreas.add(a),this._addedAreas=new Set(this._addedAreas)}}_isNameValid(){return""!==this._name.trim()}_nameChanged(e){this._error=void 0,this._name=e.target.value}_levelChanged(e){this._error=void 0,this._level=""===e.target.value?null:Number(e.target.value)}_iconChanged(e){this._error=void 0,this._icon=e.detail.value}async _updateEntry(){this._submitting=!0;const e=!this._params.entry;try{const a={name:this._name.trim(),icon:this._icon||(e?void 0:null),level:this._level,aliases:this._aliases};e?await this._params.createEntry(a,this._addedAreas):await this._params.updateEntry(a,this._addedAreas,this._removedAreas),this.closeDialog()}catch(a){this._error=a.message||this.hass.localize("ui.panel.config.floors.editor.unknown_error")}finally{this._submitting=!1}}_aliasesChanged(e){this._aliases=e.detail.value}static get styles(){return[v.RF,v.nA,o.AH`
        ha-textfield {
          display: block;
          margin-bottom: 16px;
        }
        ha-floor-icon {
          color: var(--secondary-text-color);
        }
        ha-chip-set {
          margin-bottom: 8px;
        }
      `]}constructor(...e){super(...e),this._addedAreas=new Set,this._removedAreas=new Set,this._floorAreas=(0,h.A)(((e,a,s,i)=>Object.values(a).filter((a=>(a.floor_id===e?.floor_id||s.has(a.area_id))&&!i.has(a.area_id)))))}}(0,t.__decorate)([(0,r.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_name",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_aliases",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_icon",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_level",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_error",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_params",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_submitting",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_addedAreas",void 0),(0,t.__decorate)([(0,r.wk)()],$.prototype,"_removedAreas",void 0),customElements.define("dialog-floor-registry-detail",$),i()}catch(y){i(y)}}))}};
//# sourceMappingURL=2542.82172a2c52e2806b.js.map