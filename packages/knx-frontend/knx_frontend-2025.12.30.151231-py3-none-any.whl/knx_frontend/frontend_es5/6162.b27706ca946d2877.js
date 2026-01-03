"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6162"],{10253:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{P:function(){return d}});a(74423),a(25276);var n=a(22),r=a(58109),s=a(81793),o=a(44740),l=e([n]);n=(l.then?(await l)():l)[0];var d=e=>e.first_weekday===s.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,r.S)(e.language)%7:o.Z.includes(e.first_weekday)?o.Z.indexOf(e.first_weekday):1;i()}catch(c){i(c)}}))},4359:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{LW:function(){return m},Xs:function(){return v},fU:function(){return d},ie:function(){return h}});var n=a(22),r=a(22786),s=a(74309),o=a(59006),l=e([n,s]);[n,s]=l.then?(await l)():l;var d=(e,t,a)=>c(t,a.time_zone).format(e),c=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,o.J)(e)?"h12":"h23",timeZone:(0,s.w)(e.time_zone,t)}))),h=(e,t,a)=>u(t,a.time_zone).format(e),u=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:(0,o.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,o.J)(e)?"h12":"h23",timeZone:(0,s.w)(e.time_zone,t)}))),v=(e,t,a)=>f(t,a.time_zone).format(e),f=(0,r.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",hour:(0,o.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,o.J)(e)?"h12":"h23",timeZone:(0,s.w)(e.time_zone,t)}))),m=(e,t,a)=>_(t,a.time_zone).format(e),_=(0,r.A)(((e,t)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,s.w)(e.time_zone,t)})));i()}catch(g){i(g)}}))},74309:function(e,t,a){a.a(e,(async function(e,i){try{a.d(t,{w:function(){return u}});var n,r,s,o=a(22),l=a(81793),d=e([o]);o=(d.then?(await d)():d)[0];var c=null===(n=Intl.DateTimeFormat)||void 0===n||null===(r=(s=n.call(Intl)).resolvedOptions)||void 0===r?void 0:r.call(s).timeZone,h=null!=c?c:"UTC",u=(e,t)=>e===l.Wj.local&&c?h:t;i()}catch(v){i(v)}}))},59006:function(e,t,a){a.d(t,{J:function(){return r}});a(74423);var i=a(22786),n=a(81793),r=(0,i.A)((e=>{if(e.time_format===n.Hg.language||e.time_format===n.Hg.system){var t=e.time_format===n.Hg.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===n.Hg.am_pm}))},44740:function(e,t,a){a.d(t,{Z:function(){return i}});var i=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]},60649:function(e,t,a){a.a(e,(async function(e,i){try{a.r(t);var n=a(61397),r=a(50264),s=a(94741),o=a(78261),l=a(31432),d=a(44734),c=a(56038),h=a(69683),u=a(6454),v=a(25460),f=(a(28706),a(23792),a(44114),a(54554),a(18111),a(7588),a(2892),a(26099),a(23500),a(62953),a(62826)),m=a(3398),_=a(51030),g=a(29851),y=a(93464),p=a(47342),w=a(63723),b=a(92913),k=a(83309),A=a(96196),$=a(77845),O=a(10253),I=a(4359),C=a(59006),j=a(92542),z=a(88867),D=(a(78740),a(72550)),x=a(81793),S=a(39396),J=a(59332),F=e([z,y,g,m,O,I]);[z,y,g,m,O,I]=F.then?(await F)():F;var E,W,Z,B=e=>e,L={plugins:[y.A,g.Ay],headerToolbar:!1,initialView:"timeGridWeek",editable:!0,selectable:!0,selectMirror:!0,selectOverlap:!1,eventOverlap:!1,allDaySlot:!1,height:"parent",locales:_.A,firstDay:1,dayHeaderFormat:{weekday:"short",month:void 0,day:void 0}},T=function(e){function t(){var e;(0,d.A)(this,t);for(var a=arguments.length,i=new Array(a),n=0;n<a;n++)i[n]=arguments[n];return(e=(0,h.A)(this,t,[].concat(i))).new=!1,e.disabled=!1,e}return(0,u.A)(t,e),(0,c.A)(t,[{key:"item",set:function(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._monday=e.monday||[],this._tuesday=e.tuesday||[],this._wednesday=e.wednesday||[],this._thursday=e.thursday||[],this._friday=e.friday||[],this._saturday=e.saturday||[],this._sunday=e.sunday||[]):(this._name="",this._icon="",this._monday=[],this._tuesday=[],this._wednesday=[],this._thursday=[],this._friday=[],this._saturday=[],this._sunday=[])}},{key:"disconnectedCallback",value:function(){var e,a;(0,v.A)(t,"disconnectedCallback",this,3)([]),null===(e=this.calendar)||void 0===e||e.destroy(),this.calendar=void 0,null===(a=this.renderRoot.querySelector("style[data-fullcalendar]"))||void 0===a||a.remove()}},{key:"connectedCallback",value:function(){(0,v.A)(t,"connectedCallback",this,3)([]),this.hasUpdated&&!this.calendar&&this._setupCalendar()}},{key:"focus",value:function(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}},{key:"render",value:function(){return this.hass?(0,A.qy)(E||(E=B`
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
        ${0}
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.disabled,this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this.disabled,this.disabled?A.s6:(0,A.qy)(W||(W=B`<div id="calendar"></div>`))):A.s6}},{key:"willUpdate",value:function(e){if((0,v.A)(t,"willUpdate",this,3)([e]),this.calendar){(e.has("_sunday")||e.has("_monday")||e.has("_tuesday")||e.has("_wednesday")||e.has("_thursday")||e.has("_friday")||e.has("_saturday")||e.has("calendar"))&&(this.calendar.removeAllEventSources(),this.calendar.addEventSource(this._events));var a=e.get("hass");a&&a.language!==this.hass.language&&this.calendar.setOption("locale",this.hass.language)}}},{key:"firstUpdated",value:function(){this.disabled||this._setupCalendar()}},{key:"_setupCalendar",value:function(){var e=Object.assign(Object.assign({},L),{},{locale:this.hass.language,firstDay:(0,O.P)(this.hass.locale),slotLabelFormat:{hour:"numeric",minute:void 0,hour12:(0,C.J)(this.hass.locale),meridiem:!!(0,C.J)(this.hass.locale)&&"narrow"},eventTimeFormat:{hour:(0,C.J)(this.hass.locale)?"numeric":"2-digit",minute:(0,C.J)(this.hass.locale)?"numeric":"2-digit",hour12:(0,C.J)(this.hass.locale),meridiem:!!(0,C.J)(this.hass.locale)&&"narrow"}});e.eventClick=e=>this._handleEventClick(e),e.select=e=>this._handleSelect(e),e.eventResize=e=>this._handleEventResize(e),e.eventDrop=e=>this._handleEventDrop(e),this.calendar=new m.Vv(this.shadowRoot.getElementById("calendar"),e),this.calendar.render()}},{key:"_events",get:function(){var e,t=this,a=[],i=(0,l.A)(D.mx.entries());try{var n=function(){var i=(0,o.A)(e.value,2),n=i[0],r=i[1];if(!t[`_${r}`].length)return 1;t[`_${r}`].forEach(((e,i)=>{var s=(0,p.s)(new Date,n);(0,w.R)(s,new Date,{weekStartsOn:(0,O.P)(t.hass.locale)})||(s=(0,b.f)(s,-7));var o=new Date(s),l=e.from.split(":");o.setHours(parseInt(l[0]),parseInt(l[1]),0,0);var d=new Date(s),c=e.to.split(":");d.setHours(parseInt(c[0]),parseInt(c[1]),0,0),a.push({id:`${r}-${i}`,start:o.toISOString(),end:d.toISOString()})}))};for(i.s();!(e=i.n()).done;)n()}catch(r){i.e(r)}finally{i.f()}return a}},{key:"_handleSelect",value:function(e){var t=e.start,a=e.end,i=D.mx[t.getDay()],n=(0,s.A)(this[`_${i}`]),r=Object.assign({},this._item),o=(0,I.LW)(a,Object.assign(Object.assign({},this.hass.locale),{},{time_zone:x.Wj.local}),this.hass.config);n.push({from:(0,I.LW)(t,Object.assign(Object.assign({},this.hass.locale),{},{time_zone:x.Wj.local}),this.hass.config),to:(0,k.r)(t,a)&&"0:00"!==o?o:"24:00"}),r[i]=n,(0,j.r)(this,"value-changed",{value:r}),(0,k.r)(t,a)||this.calendar.unselect()}},{key:"_handleEventResize",value:function(e){var t=e.event,a=t.id,i=t.start,n=t.end,r=a.split("-"),s=(0,o.A)(r,2),l=s[0],d=s[1],c=this[`_${l}`][parseInt(d)],h=Object.assign({},this._item),u=(0,I.LW)(n,this.hass.locale,this.hass.config);h[l][d]=Object.assign(Object.assign({},h[l][d]),{},{from:c.from,to:(0,k.r)(i,n)&&"0:00"!==u?u:"24:00"}),(0,j.r)(this,"value-changed",{value:h}),(0,k.r)(i,n)||(this.requestUpdate(`_${l}`),e.revert())}},{key:"_handleEventDrop",value:function(e){var t=e.event,a=t.id,i=t.start,n=t.end,r=a.split("-"),l=(0,o.A)(r,2),d=l[0],c=l[1],h=D.mx[i.getDay()],u=Object.assign({},this._item),v=(0,I.LW)(n,this.hass.locale,this.hass.config),f=Object.assign(Object.assign({},u[d][c]),{},{from:(0,I.LW)(i,this.hass.locale,this.hass.config),to:(0,k.r)(i,n)&&"0:00"!==v?v:"24:00"});if(h===d)u[d][c]=f;else{u[d].splice(c,1);var m=(0,s.A)(this[`_${h}`]);m.push(f),u[h]=m}(0,j.r)(this,"value-changed",{value:u}),(0,k.r)(i,n)||(this.requestUpdate(`_${d}`),e.revert())}},{key:"_handleEventClick",value:(a=(0,r.A)((0,n.A)().m((function e(t){var a,i,r,l,d;return(0,n.A)().w((function(e){for(;;)switch(e.n){case 0:a=t.event.id.split("-"),i=(0,o.A)(a,2),r=i[0],l=i[1],d=(0,s.A)(this[`_${r}`])[l],(0,J.c)(this,{block:d,updateBlock:e=>this._updateBlock(r,l,e),deleteBlock:()=>this._deleteBlock(r,l)});case 1:return e.a(2)}}),e,this)}))),function(e){return a.apply(this,arguments)})},{key:"_updateBlock",value:function(e,t,a){var i=a.from.split(":"),n=(0,o.A)(i,3),r=n[0],l=n[1];n[2];a.from=`${r}:${l}`;var d=a.to.split(":"),c=(0,o.A)(d,3),h=c[0],u=c[1];c[2];a.to=`${h}:${u}`,0===Number(h)&&0===Number(u)&&(a.to="24:00");var v=Object.assign({},this._item);v[e]=(0,s.A)(this._item[e]),v[e][t]=a,(0,j.r)(this,"value-changed",{value:v})}},{key:"_deleteBlock",value:function(e,t){var a=(0,s.A)(this[`_${e}`]),i=Object.assign({},this._item);a.splice(parseInt(t),1),i[e]=a,(0,j.r)(this,"value-changed",{value:i})}},{key:"_valueChanged",value:function(e){var t;if(this.new||this._item){e.stopPropagation();var a=e.target.configValue,i=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${a}`]!==i){var n=Object.assign({},this._item);i?n[a]=i:delete n[a],(0,j.r)(this,"value-changed",{value:n})}}}}],[{key:"styles",get:function(){return[S.RF,(0,A.AH)(Z||(Z=B`
        .form {
          color: var(--primary-text-color);
        }

        ha-textfield {
          display: block;
          margin: 8px 0;
        }

        #calendar {
          margin: 8px 0;
          height: 450px;
          width: 100%;
          -webkit-user-select: none;
          -ms-user-select: none;
          user-select: none;
          --fc-border-color: var(--divider-color);
          --fc-event-border-color: var(--divider-color);
        }

        .fc-v-event .fc-event-time {
          white-space: inherit;
        }
        .fc-theme-standard .fc-scrollgrid {
          border: 1px solid var(--divider-color);
          border-radius: var(--mdc-shape-small, 4px);
        }

        .fc-scrollgrid-section-header td {
          border: none;
        }
        :host([narrow]) .fc-scrollgrid-sync-table {
          overflow: hidden;
        }
        table.fc-scrollgrid-sync-table
          tbody
          tr:first-child
          .fc-daygrid-day-top {
          padding-top: 0;
        }
        .fc-scroller::-webkit-scrollbar {
          width: 0.4rem;
          height: 0.4rem;
        }
        .fc-scroller::-webkit-scrollbar-thumb {
          border-radius: var(--ha-border-radius-sm);
          background: var(--scrollbar-thumb-color);
        }
        .fc-scroller {
          overflow-y: auto;
          scrollbar-color: var(--scrollbar-thumb-color) transparent;
          scrollbar-width: thin;
        }

        .fc-timegrid-event-short .fc-event-time:after {
          content: ""; /* prevent trailing dash in half hour events since we do not have event titles */
        }

        a {
          color: inherit !important;
        }

        th.fc-col-header-cell.fc-day {
          background-color: var(--table-header-background-color);
          color: var(--primary-text-color);
          font-size: var(--ha-font-size-xs);
          font-weight: var(--ha-font-weight-bold);
          text-transform: uppercase;
        }
      `))]}}]);var a}(A.WF);(0,f.__decorate)([(0,$.MZ)({attribute:!1})],T.prototype,"hass",void 0),(0,f.__decorate)([(0,$.MZ)({type:Boolean})],T.prototype,"new",void 0),(0,f.__decorate)([(0,$.MZ)({type:Boolean})],T.prototype,"disabled",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_name",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_icon",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_monday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_tuesday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_wednesday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_thursday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_friday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_saturday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"_sunday",void 0),(0,f.__decorate)([(0,$.wk)()],T.prototype,"calendar",void 0),T=(0,f.__decorate)([(0,$.EM)("ha-schedule-form")],T),i()}catch(q){i(q)}}))},59332:function(e,t,a){a.d(t,{c:function(){return r}});a(23792),a(26099),a(3362),a(62953);var i=a(92542),n=()=>a.e("6678").then(a.bind(a,88240)),r=(e,t)=>{(0,i.r)(e,"show-dialog",{dialogTag:"dialog-schedule-block-info",dialogImport:n,dialogParams:t})}}}]);
//# sourceMappingURL=6162.b27706ca946d2877.js.map