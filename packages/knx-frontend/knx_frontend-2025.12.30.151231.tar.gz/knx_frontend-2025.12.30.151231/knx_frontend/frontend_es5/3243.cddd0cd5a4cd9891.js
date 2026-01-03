"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3243"],{10253:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{P:function(){return l}});i(74423),i(25276);var a=i(22),r=i(58109),n=i(81793),o=i(44740),c=t([a]);a=(c.then?(await c)():c)[0];var l=t=>t.first_weekday===n.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(t.language).weekInfo.firstDay%7:(0,r.S)(t.language)%7:o.Z.includes(t.first_weekday)?o.Z.indexOf(t.first_weekday):1;s()}catch(u){s(u)}}))},44740:function(t,e,i){i.d(e,{Z:function(){return s}});var s=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]},87328:function(t,e,i){i.d(e,{aH:function(){return o}});var s=i(16727),a=i(91889),r=(i(25276),i(34782),[" ",": "," - "]),n=t=>t.toLowerCase()!==t,o=(t,e,i)=>{var s=e[t.entity_id];return s?c(s,i):(0,a.u)(t)},c=(t,e,i)=>{var o=t.name||("original_name"in t&&null!=t.original_name?String(t.original_name):void 0),c=t.device_id?e[t.device_id]:void 0;if(!c)return o||(i?(0,a.u)(i):void 0);var l=(0,s.xn)(c);return l!==o?l&&o&&((t,e)=>{for(var i=t.toLowerCase(),s=e.toLowerCase(),a=0,o=r;a<o.length;a++){var c=`${s}${o[a]}`;if(i.startsWith(c)){var l=t.substring(c.length);if(l.length)return n(l.substr(0,l.indexOf(" ")))?l:l[0].toUpperCase()+l.slice(1)}}})(o,l)||o:void 0}},79384:function(t,e,i){i.d(e,{Cf:function(){return c}});i(2008),i(62062),i(18111),i(81148),i(22489),i(61701),i(13579),i(26099);var s=i(56403),a=i(16727),r=i(87328),n=i(47644),o=i(87400),c=(t,e,i,c,l,u)=>{var d=(0,o.l)(t,i,c,l,u),p=d.device,h=d.area,v=d.floor;return e.map((e=>{switch(e.type){case"entity":return(0,r.aH)(t,i,c);case"device":return p?(0,a.xn)(p):void 0;case"area":return h?(0,s.A)(h):void 0;case"floor":return v?(0,n.X)(v):void 0;case"text":return e.text;default:return""}}))}},87400:function(t,e,i){i.d(e,{l:function(){return s}});var s=(t,e,i,s,r)=>{var n=e[t.entity_id];return n?a(n,e,i,s,r):{entity:null,device:null,area:null,floor:null}},a=(t,e,i,s,a)=>{var r=e[t.entity_id],n=null==t?void 0:t.device_id,o=n?i[n]:void 0,c=(null==t?void 0:t.area_id)||(null==o?void 0:o.area_id),l=c?s[c]:void 0,u=null==l?void 0:l.floor_id;return{entity:r,device:o||null,area:l||null,floor:(u?a[u]:void 0)||null}}},60042:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(61397),a=i(50264),r=i(78261),n=i(44734),o=i(56038),c=i(69683),l=i(6454),u=(i(28706),i(2008),i(50113),i(48980),i(74423),i(25276),i(44114),i(54554),i(13609),i(18111),i(22489),i(20116),i(7588),i(26099),i(23500),i(62826)),d=i(96196),p=i(77845),h=i(22786),v=i(55376),y=i(92542),_=i(79384),f=i(91889),b=i(79599),g=i(84125),m=i(37157),$=i(62001),M=(i(94343),i(96943)),k=(i(60733),i(60961),i(91720)),w=t([M,k,m]);[M,k,m]=w.then?(await w)():w;var C,A,Z,O,x,S,I,q,j,L,U,H=t=>t,E="M16,11.78L20.24,4.45L21.97,5.45L16.74,14.5L10.23,10.75L5.46,19H22V21H2V3H4V17.54L9.5,8L16,11.78Z",B="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",F=["entity","external","no_state"],D="___missing-entity___",T=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,s=new Array(i),a=0;a<i;a++)s[a]=arguments[a];return(t=(0,c.A)(this,e,[].concat(s))).autofocus=!1,t.disabled=!1,t.required=!1,t.helpMissingEntityUrl="/more-info/statistics/",t.entitiesOnly=!1,t.hideClearIcon=!1,t._getItems=()=>t._getStatisticsItems(t.hass,t.statisticIds,t.includeStatisticsUnitOfMeasurement,t.includeUnitClass,t.includeDeviceClass,t.entitiesOnly,t.excludeStatistics,t.value),t._getStatisticsItems=(0,h.A)(((e,i,s,a,n,o,c,l)=>{if(!i)return[];if(s){var u=(0,v.e)(s);i=i.filter((t=>u.includes(t.statistics_unit_of_measurement)))}if(a){var d=(0,v.e)(a);i=i.filter((t=>d.includes(t.unit_class)))}if(n){var p=(0,v.e)(n);i=i.filter((e=>{var i=t.hass.states[e.statistic_id];return!i||p.includes(i.attributes.device_class||"")}))}var h=(0,b.qC)(e),y=[];return i.forEach((i=>{if(!c||i.statistic_id===l||!c.includes(i.statistic_id)){var s=t.hass.states[i.statistic_id];if(s){var a=i.statistic_id,n=(0,f.u)(s),u=(0,_.Cf)(s,[{type:"entity"},{type:"device"},{type:"area"}],e.entities,e.devices,e.areas,e.floors),d=(0,r.A)(u,3),p=d[0],v=d[1],b=d[2],$=p||v||a,M=[b,p?v:void 0].filter(Boolean).join(h?" ◂ ":" ▸ "),k=`${F.indexOf("entity")}`;y.push({id:a,statistic_id:a,primary:$,secondary:M,stateObj:s,type:"entity",sorting_label:[k,v,p].join("_"),search_labels:[p,v,b,n,a].filter(Boolean)})}else if(!o){var w=i.statistic_id,C=(0,m.$O)(t.hass,i.statistic_id,i),A=i.statistic_id.includes(":")&&!i.statistic_id.includes(".")?"external":"no_state",Z=`${F.indexOf(A)}`;if("no_state"===A)y.push({id:w,primary:C,secondary:t.hass.localize("ui.components.statistic-picker.no_state"),type:A,sorting_label:[Z,C].join("_"),search_labels:[C,w],icon_path:B});else if("external"===A){var O=w.split(":")[0],x=(0,g.p$)(t.hass.localize,O);y.push({id:w,statistic_id:w,primary:C,secondary:x,type:A,sorting_label:[Z,C].join("_"),search_labels:[C,x,w],icon_path:E})}}}})),y})),t._statisticMetaData=(0,h.A)(((t,e)=>{if(e)return e.find((e=>e.statistic_id===t))})),t._valueRenderer=e=>{var i=e,s=t._computeItem(i);return(0,d.qy)(C||(C=H`
      ${0}
      <span slot="headline">${0}</span>
      ${0}
    `),s.stateObj?(0,d.qy)(A||(A=H`
            <state-badge
              .hass=${0}
              .stateObj=${0}
              slot="start"
            ></state-badge>
          `),t.hass,s.stateObj):s.icon_path?(0,d.qy)(Z||(Z=H`
              <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
            `),s.icon_path):d.s6,s.primary,s.secondary?(0,d.qy)(O||(O=H`<span slot="supporting-text">${0}</span>`),s.secondary):d.s6)},t._rowRenderer=(e,i)=>{var s,a=i.index,r=null===(s=t.hass.userData)||void 0===s?void 0:s.showEntityIdPicker;return(0,d.qy)(x||(x=H`
      <ha-combo-box-item type="button" compact .borderTop=${0}>
        ${0}
        <span slot="headline">${0} </span>
        ${0}
        ${0}
      </ha-combo-box-item>
    `),0!==a,e.icon_path?(0,d.qy)(S||(S=H`
              <ha-svg-icon
                style="margin: 0 4px"
                slot="start"
                .path=${0}
              ></ha-svg-icon>
            `),e.icon_path):e.stateObj?(0,d.qy)(I||(I=H`
                <state-badge
                  slot="start"
                  .stateObj=${0}
                  .hass=${0}
                ></state-badge>
              `),e.stateObj,t.hass):d.s6,e.primary,e.secondary?(0,d.qy)(q||(q=H`<span slot="supporting-text">${0}</span>`),e.secondary):d.s6,e.statistic_id&&r?(0,d.qy)(j||(j=H`<span slot="supporting-text" class="code">
              ${0}
            </span>`),e.statistic_id):d.s6)},t._searchFn=(t,e)=>{var i=e.findIndex((e=>{var i;return(null===(i=e.stateObj)||void 0===i?void 0:i.entity_id)===t||e.statistic_id===t}));if(-1===i)return e;var s=e.splice(i,1),a=(0,r.A)(s,1)[0];return e.unshift(a),e},t._notFoundLabel=e=>t.hass.localize("ui.components.statistic-picker.no_match",{term:(0,d.qy)(L||(L=H`<b>‘${0}’</b>`),e)}),t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"willUpdate",value:function(t){(!this.hasUpdated&&!this.statisticIds||t.has("statisticTypes"))&&this._getStatisticIds()}},{key:"_getStatisticIds",value:(u=(0,a.A)((0,s.A)().m((function t(){return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,m.p3)(this.hass,this.statisticTypes);case 1:this.statisticIds=t.v;case 2:return t.a(2)}}),t,this)}))),function(){return u.apply(this,arguments)})},{key:"_getAdditionalItems",value:function(){return[{id:D,primary:this.hass.localize("ui.components.statistic-picker.missing_entity"),icon_path:"M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z"}]}},{key:"_computeItem",value:function(t){var e=this.hass.states[t];if(e){var i=(0,_.Cf)(e,[{type:"entity"},{type:"device"},{type:"area"}],this.hass.entities,this.hass.devices,this.hass.areas,this.hass.floors),s=(0,r.A)(i,3),a=s[0],n=s[1],o=s[2],c=(0,b.qC)(this.hass),l=a||n||t,u=[o,a?n:void 0].filter(Boolean).join(c?" ◂ ":" ▸ "),d=(0,f.u)(e);return{id:t,statistic_id:t,primary:l,secondary:u,stateObj:e,type:"entity",sorting_label:[`${F.indexOf("entity")}`,n,a].join("_"),search_labels:[a,n,o,d,t].filter(Boolean)}}var p=this.statisticIds?this._statisticMetaData(t,this.statisticIds):void 0;if(p&&"external"===(t.includes(":")&&!t.includes(".")?"external":"no_state")){var h=`${F.indexOf("external")}`,v=(0,m.$O)(this.hass,t,p),y=t.split(":")[0],$=(0,g.p$)(this.hass.localize,y);return{id:t,statistic_id:t,primary:v,secondary:$,type:"external",sorting_label:[h,v].join("_"),search_labels:[v,$,t],icon_path:E}}var M=`${F.indexOf("external")}`,k=(0,m.$O)(this.hass,t,p);return{id:t,primary:k,secondary:this.hass.localize("ui.components.statistic-picker.no_state"),type:"no_state",sorting_label:[M,k].join("_"),search_labels:[k,t],icon_path:B}}},{key:"render",value:function(){var t,e=null!==(t=this.placeholder)&&void 0!==t?t:this.hass.localize("ui.components.statistic-picker.placeholder");return(0,d.qy)(U||(U=H`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .allowCustomValue=${0}
        .label=${0}
        .notFoundLabel=${0}
        .emptyLabel=${0}
        .placeholder=${0}
        .value=${0}
        .rowRenderer=${0}
        .getItems=${0}
        .getAdditionalItems=${0}
        .hideClearIcon=${0}
        .searchFn=${0}
        .valueRenderer=${0}
        .helper=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.allowCustomEntity,this.label,this._notFoundLabel,this.hass.localize("ui.components.statistic-picker.no_statistics"),e,this.value,this._rowRenderer,this._getItems,this._getAdditionalItems,this.hideClearIcon,this._searchFn,this._valueRenderer,this.helper,this._valueChanged)}},{key:"_valueChanged",value:function(t){t.stopPropagation();var e=t.detail.value;e!==D?(this.value=e,(0,y.r)(this,"value-changed",{value:e})):window.open((0,$.o)(this.hass,this.helpMissingEntityUrl),"_blank")}},{key:"open",value:(i=(0,a.A)((0,s.A)().m((function t(){var e;return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this.updateComplete;case 1:return t.n=2,null===(e=this._picker)||void 0===e?void 0:e.open();case 2:return t.a(2)}}),t,this)}))),function(){return i.apply(this,arguments)})}]);var i,u}(d.WF);(0,u.__decorate)([(0,p.MZ)({attribute:!1})],T.prototype,"hass",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean})],T.prototype,"autofocus",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean})],T.prototype,"disabled",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean})],T.prototype,"required",void 0),(0,u.__decorate)([(0,p.MZ)()],T.prototype,"label",void 0),(0,u.__decorate)([(0,p.MZ)()],T.prototype,"value",void 0),(0,u.__decorate)([(0,p.MZ)()],T.prototype,"helper",void 0),(0,u.__decorate)([(0,p.MZ)()],T.prototype,"placeholder",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"statistic-types"})],T.prototype,"statisticTypes",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean,attribute:"allow-custom-entity"})],T.prototype,"allowCustomEntity",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:!1,type:Array})],T.prototype,"statisticIds",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:!1})],T.prototype,"helpMissingEntityUrl",void 0),(0,u.__decorate)([(0,p.MZ)({type:Array,attribute:"include-statistics-unit-of-measurement"})],T.prototype,"includeStatisticsUnitOfMeasurement",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"include-unit-class"})],T.prototype,"includeUnitClass",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"include-device-class"})],T.prototype,"includeDeviceClass",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean,attribute:"entities-only"})],T.prototype,"entitiesOnly",void 0),(0,u.__decorate)([(0,p.MZ)({type:Array,attribute:"exclude-statistics"})],T.prototype,"excludeStatistics",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"hide-clear-icon",type:Boolean})],T.prototype,"hideClearIcon",void 0),(0,u.__decorate)([(0,p.P)("ha-generic-picker")],T.prototype,"_picker",void 0),T=(0,u.__decorate)([(0,p.EM)("ha-statistic-picker")],T),e()}catch(V){e(V)}}))},55917:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(94741),a=i(61397),r=i(50264),n=i(44734),o=i(56038),c=i(69683),l=i(6454),u=(i(28706),i(2008),i(74423),i(62062),i(18111),i(22489),i(61701),i(26099),i(62826)),d=i(96196),p=i(77845),h=i(4937),v=i(92542),y=i(60042),_=t([y]);y=(_.then?(await _)():_)[0];var f,b,g,m,$=t=>t,M=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,s=new Array(i),a=0;a<i;a++)s[a]=arguments[a];return(t=(0,c.A)(this,e,[].concat(s))).ignoreRestrictionsOnFirstStatistic=!1,t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"render",value:function(){if(!this.hass)return d.s6;var t=this.ignoreRestrictionsOnFirstStatistic&&this._currentStatistics.length<=1,e=t?void 0:this.includeStatisticsUnitOfMeasurement,i=t?void 0:this.includeUnitClass,s=t?void 0:this.includeDeviceClass,a=t?void 0:this.statisticTypes;return(0,d.qy)(f||(f=$`
      ${0}
      ${0}
      <div>
        <ha-statistic-picker
          .hass=${0}
          .includeStatisticsUnitOfMeasurement=${0}
          .includeUnitClass=${0}
          .includeDeviceClass=${0}
          .statisticTypes=${0}
          .statisticIds=${0}
          .placeholder=${0}
          .excludeStatistics=${0}
          .allowCustomEntity=${0}
          @value-changed=${0}
        ></ha-statistic-picker>
      </div>
    `),this.label?(0,d.qy)(b||(b=$`<label>${0}</label>`),this.label):d.s6,(0,h.u)(this._currentStatistics,(t=>t),(t=>(0,d.qy)(g||(g=$`
          <div>
            <ha-statistic-picker
              .curValue=${0}
              .hass=${0}
              .includeStatisticsUnitOfMeasurement=${0}
              .includeUnitClass=${0}
              .includeDeviceClass=${0}
              .value=${0}
              .statisticTypes=${0}
              .statisticIds=${0}
              .excludeStatistics=${0}
              .allowCustomEntity=${0}
              @value-changed=${0}
            ></ha-statistic-picker>
          </div>
        `),t,this.hass,e,i,s,t,a,this.statisticIds,this.value,this.allowCustomEntity,this._statisticChanged))),this.hass,this.includeStatisticsUnitOfMeasurement,this.includeUnitClass,this.includeDeviceClass,this.statisticTypes,this.statisticIds,this.placeholder,this.value,this.allowCustomEntity,this._addStatistic)}},{key:"_currentStatistics",get:function(){return this.value||[]}},{key:"_updateStatistics",value:(u=(0,r.A)((0,a.A)().m((function t(e){return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:this.value=e,(0,v.r)(this,"value-changed",{value:e});case 1:return t.a(2)}}),t,this)}))),function(t){return u.apply(this,arguments)})},{key:"_statisticChanged",value:function(t){t.stopPropagation();var e=t.currentTarget.curValue,i=t.detail.value;if(i!==e){var s=this._currentStatistics;i&&!s.includes(i)?this._updateStatistics(s.map((t=>t===e?i:t))):this._updateStatistics(s.filter((t=>t!==e)))}}},{key:"_addStatistic",value:(i=(0,r.A)((0,a.A)().m((function t(e){var i,r;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(e.stopPropagation(),i=e.detail.value){t.n=1;break}return t.a(2);case 1:if(e.currentTarget.value="",i){t.n=2;break}return t.a(2);case 2:if(!(r=this._currentStatistics).includes(i)){t.n=3;break}return t.a(2);case 3:this._updateStatistics([].concat((0,s.A)(r),[i]));case 4:return t.a(2)}}),t,this)}))),function(t){return i.apply(this,arguments)})}]);var i,u}(d.WF);M.styles=(0,d.AH)(m||(m=$`
    :host {
      display: block;
    }
    ha-statistic-picker {
      display: block;
      width: 100%;
      margin-top: 8px;
    }
    label {
      display: block;
      margin-bottom: 0 0 8px;
    }
  `)),(0,u.__decorate)([(0,p.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,u.__decorate)([(0,p.MZ)({type:Array})],M.prototype,"value",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:!1,type:Array})],M.prototype,"statisticIds",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"statistic-types"})],M.prototype,"statisticTypes",void 0),(0,u.__decorate)([(0,p.MZ)({type:String})],M.prototype,"label",void 0),(0,u.__decorate)([(0,p.MZ)({type:String})],M.prototype,"placeholder",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean,attribute:"allow-custom-entity"})],M.prototype,"allowCustomEntity",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"include-statistics-unit-of-measurement"})],M.prototype,"includeStatisticsUnitOfMeasurement",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"include-unit-class"})],M.prototype,"includeUnitClass",void 0),(0,u.__decorate)([(0,p.MZ)({attribute:"include-device-class"})],M.prototype,"includeDeviceClass",void 0),(0,u.__decorate)([(0,p.MZ)({type:Boolean,attribute:"ignore-restrictions-on-first-statistic"})],M.prototype,"ignoreRestrictionsOnFirstStatistic",void 0),M=(0,u.__decorate)([(0,p.EM)("ha-statistics-picker")],M),e()}catch(k){e(k)}}))},10675:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{HaStatisticSelector:function(){return f}});var a=i(44734),r=i(56038),n=i(69683),o=i(6454),c=(i(28706),i(62826)),l=i(96196),u=i(77845),d=i(55917),p=t([d]);d=(p.then?(await p)():p)[0];var h,v,y,_=t=>t,f=function(t){function e(){var t;(0,a.A)(this,e);for(var i=arguments.length,s=new Array(i),r=0;r<i;r++)s[r]=arguments[r];return(t=(0,n.A)(this,e,[].concat(s))).disabled=!1,t.required=!0,t}return(0,o.A)(e,t),(0,r.A)(e,[{key:"render",value:function(){return this.selector.statistic.multiple?(0,l.qy)(v||(v=_`
      ${0}
      <ha-statistics-picker
        .hass=${0}
        .value=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
      ></ha-statistics-picker>
    `),this.label?(0,l.qy)(y||(y=_`<label>${0}</label>`),this.label):"",this.hass,this.value,this.helper,this.disabled,this.required):(0,l.qy)(h||(h=_`<ha-statistic-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        allow-custom-entity
      ></ha-statistic-picker>`),this.hass,this.value,this.label,this.helper,this.disabled,this.required)}}])}(l.WF);(0,c.__decorate)([(0,u.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,c.__decorate)([(0,u.MZ)({attribute:!1})],f.prototype,"selector",void 0),(0,c.__decorate)([(0,u.MZ)()],f.prototype,"value",void 0),(0,c.__decorate)([(0,u.MZ)()],f.prototype,"label",void 0),(0,c.__decorate)([(0,u.MZ)()],f.prototype,"helper",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean})],f.prototype,"required",void 0),f=(0,c.__decorate)([(0,u.EM)("ha-selector-statistic")],f),s()}catch(b){s(b)}}))},54193:function(t,e,i){i.d(e,{Hg:function(){return s},e0:function(){return a}});i(61397),i(50264),i(74423),i(62062),i(18111),i(61701),i(33110),i(26099),i(3362);var s=t=>t.map((t=>{if("string"!==t.type)return t;switch(t.name){case"username":return Object.assign(Object.assign({},t),{},{autocomplete:"username",autofocus:!0});case"password":return Object.assign(Object.assign({},t),{},{autocomplete:"current-password"});case"code":return Object.assign(Object.assign({},t),{},{autocomplete:"one-time-code",autofocus:!0});default:return t}})),a=(t,e)=>t.callWS({type:"auth/sign_path",path:e})},31136:function(t,e,i){i.d(e,{HV:function(){return r},Hh:function(){return a},KF:function(){return o},ON:function(){return n},g0:function(){return u},s7:function(){return c}});var s=i(99245),a="unavailable",r="unknown",n="on",o="off",c=[a,r],l=[a,r,o],u=(0,s.g)(c);(0,s.g)(l)},37157:function(t,e,i){i.a(t,(async function(t,s){try{i.d(e,{$O:function(){return c},p3:function(){return o}});i(31432),i(74423),i(18111),i(13579),i(26099);var a=i(91889),r=i(10253),n=t([r]);r=(n.then?(await n)():n)[0];var o=(t,e)=>t.callWS({type:"recorder/list_statistic_ids",statistic_type:e}),c=(t,e,i)=>{var s=t.states[e];return s?(0,a.u)(s):(null==i?void 0:i.name)||e};s()}catch(l){s(l)}}))},62001:function(t,e,i){i.d(e,{o:function(){return s}});i(74423);var s=(t,e)=>`https://${t.config.version.includes("b")?"rc":t.config.version.includes("dev")?"next":"www"}.home-assistant.io${e}`}}]);
//# sourceMappingURL=3243.cddd0cd5a4cd9891.js.map