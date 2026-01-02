"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1249"],{37445:function(e,t,a){var o,i,r,l,n,s,c,d,h,u,p,_,b,v,m,f,g,y,w=a(61397),x=a(50264),k=a(94741),$=a(78261),A=a(44734),C=a(56038),R=a(75864),M=a(69683),L=a(6454),S=a(25460),z=(a(28706),a(2008),a(50113),a(48980),a(74423),a(25276),a(23792),a(62062),a(44114),a(72712),a(26910),a(54554),a(18111),a(22489),a(20116),a(7588),a(61701),a(18237),a(13579),a(5506),a(26099),a(16034),a(3362),a(31415),a(17642),a(58004),a(33853),a(45876),a(32475),a(15024),a(31698),a(42762),a(46058),a(23500),a(62953),a(62826)),D=a(34271),Z=a(96196),q=a(77845),H=a(94333),T=a(32288),O=a(29485),I=a(22786),F=a(39501),P=a(92542),B=a(25749),W=a(40404),G=a(31432),E=(e,t)=>{var a,o={},i=(0,G.A)(e);try{for(i.s();!(a=i.n()).done;){var r=a.value,l=t(r);l in o?o[l].push(r):o[l]=[r]}}catch(n){i.e(n)}finally{i.f()}return o},j=a(39396),U=a(84183),K=(a(70524),a(60961),a(17262),a(3296),a(27208),a(48408),a(14603),a(47566),a(98721),a(2209)),V=()=>(o||(o=(0,K.LV)(new Worker(new URL(a.p+a.u("4346"),a.b)))),o),J=(e,t,a,o,i)=>V().sortData(e,t,a,o,i),N=a(99034),Y=e=>e,Q="zzzzz_undefined",X=function(e){function t(){var e;(0,A.A)(this,t);for(var a=arguments.length,o=new Array(a),p=0;p<a;p++)o[p]=arguments[p];return(e=(0,M.A)(this,t,[].concat(o))).narrow=!1,e.columns={},e.data=[],e.selectable=!1,e.clickable=!1,e.hasFab=!1,e.autoHeight=!1,e.id="id",e.noLabelFloat=!1,e.filter="",e.sortDirection=null,e._filterable=!1,e._filter="",e._filteredData=[],e._headerHeight=0,e._collapsedGroups=[],e._lastSelectedRowId=null,e._checkedRows=[],e._sortColumns={},e._curRequest=0,e._lastUpdate=0,e._debounceSearch=(0,W.s)((t=>{e._filter=t}),100,!1),e._sortedColumns=(0,I.A)(((e,t)=>t&&t.length?Object.keys(e).sort(((e,a)=>{var o=t.indexOf(e),i=t.indexOf(a);if(o!==i){if(-1===o)return 1;if(-1===i)return-1}return o-i})).reduce(((t,a)=>(t[a]=e[a],t)),{}):e)),e._keyFunction=t=>(null==t?void 0:t[e.id])||t,e._renderRow=(t,a,o,u)=>o?o.append?(0,Z.qy)(i||(i=Y`<div class="mdc-data-table__row">${0}</div>`),o.content):o.empty?(0,Z.qy)(r||(r=Y`<div class="mdc-data-table__row empty-row"></div>`)):(0,Z.qy)(l||(l=Y`
      <div
        aria-rowindex=${0}
        role="row"
        .rowId=${0}
        @click=${0}
        class="mdc-data-table__row ${0}"
        aria-selected=${0}
        .selectable=${0}
      >
        ${0}
        ${0}
      </div>
    `),u+2,o[e.id],e._handleRowClick,(0,H.H)({"mdc-data-table__row--selected":e._checkedRows.includes(String(o[e.id])),clickable:e.clickable}),(0,T.J)(!!e._checkedRows.includes(String(o[e.id]))||void 0),!1!==o.selectable,e.selectable?(0,Z.qy)(n||(n=Y`
              <div
                class="mdc-data-table__cell mdc-data-table__cell--checkbox"
                role="cell"
              >
                <ha-checkbox
                  class="mdc-data-table__row-checkbox"
                  @click=${0}
                  .rowId=${0}
                  .disabled=${0}
                  .checked=${0}
                >
                </ha-checkbox>
              </div>
            `),e._handleRowCheckboxClicked,o[e.id],!1===o.selectable,e._checkedRows.includes(String(o[e.id]))):"",Object.entries(t).map((i=>{var r,l,n=(0,$.A)(i,2),u=n[0],p=n[1];return a&&!p.main&&!p.showNarrow||p.hidden||(e.columnOrder&&e.columnOrder.includes(u)&&null!==(r=null===(l=e.hiddenColumns)||void 0===l?void 0:l.includes(u))&&void 0!==r?r:p.defaultHidden)?Z.s6:(0,Z.qy)(s||(s=Y`
            <div
              @mouseover=${0}
              @focus=${0}
              role=${0}
              class="mdc-data-table__cell ${0}"
              style=${0}
            >
              ${0}
            </div>
          `),e._setTitle,e._setTitle,p.main?"rowheader":"cell",(0,H.H)({"mdc-data-table__cell--flex":"flex"===p.type,"mdc-data-table__cell--numeric":"numeric"===p.type,"mdc-data-table__cell--icon":"icon"===p.type,"mdc-data-table__cell--icon-button":"icon-button"===p.type,"mdc-data-table__cell--overflow-menu":"overflow-menu"===p.type,"mdc-data-table__cell--overflow":"overflow"===p.type,forceLTR:Boolean(p.forceLTR)}),(0,O.W)({minWidth:p.minWidth,maxWidth:p.maxWidth,flex:p.flex||1}),p.template?p.template(o):a&&p.main?(0,Z.qy)(c||(c=Y`<div class="primary">${0}</div>
                      <div class="secondary">
                        ${0}
                      </div>
                      ${0}`),o[u],Object.entries(t).filter((t=>{var a,o,i=(0,$.A)(t,2),r=i[0],l=i[1];return!(l.hidden||l.main||l.showNarrow||(e.columnOrder&&e.columnOrder.includes(r)&&null!==(a=null===(o=e.hiddenColumns)||void 0===o?void 0:o.includes(r))&&void 0!==a?a:l.defaultHidden))})).map(((e,t)=>{var a=(0,$.A)(e,2),i=a[0],r=a[1];return(0,Z.qy)(d||(d=Y`${0}${0}`),0!==t?" · ":Z.s6,r.template?r.template(o):o[i])})),p.extraTemplate?p.extraTemplate(o):Z.s6):(0,Z.qy)(h||(h=Y`${0}${0}`),o[u],p.extraTemplate?p.extraTemplate(o):Z.s6))}))):Z.s6,e._groupData=(0,I.A)(((t,a,o,i,r,l,n,s,c)=>{if(o||i||r){var d=(0,k.A)(t);if(r){var h=s===r,p=E(d,(e=>e[r]));p.undefined&&(p[Q]=p.undefined,delete p.undefined);var _=Object.keys(p).sort(((t,a)=>{var o,i;if(!l&&h){var r=(0,B.xL)(t,a,e.hass.locale.language);return"asc"===c?r:-1*r}var n=null!==(o=null==l?void 0:l.indexOf(t))&&void 0!==o?o:-1,s=null!==(i=null==l?void 0:l.indexOf(a))&&void 0!==i?i:-1;return n!==s?-1===n?1:-1===s?-1:n-s:(0,B.xL)(["","-","—"].includes(t)?"zzz":t,["","-","—"].includes(a)?"zzz":a,e.hass.locale.language)})).reduce(((e,t)=>{var a=[t,p[t]];return e.push(a),e}),[]),b=[];_.forEach((t=>{var o=(0,$.A)(t,2),i=o[0],r=o[1],l=n.includes(i);b.push({append:!0,selectable:!1,content:(0,Z.qy)(u||(u=Y`<div
                class="mdc-data-table__cell group-header"
                role="cell"
                .group=${0}
                @click=${0}
              >
                <ha-icon-button
                  .path=${0}
                  .label=${0}
                  class=${0}
                >
                </ha-icon-button>
                ${0}
              </div>`),i,e._collapseGroup,"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z",e.hass.localize("ui.components.data-table."+(l?"expand":"collapse")),l?"collapsed":"",i===Q?a("ui.components.data-table.ungrouped"):i||"")}),n.includes(i)||b.push.apply(b,(0,k.A)(r))})),d=b}return o&&d.push({append:!0,selectable:!1,content:o}),i&&d.push({empty:!0}),d}return t})),e._memFilterData=(0,I.A)(((e,t,a)=>((e,t,a)=>V().filterData(e,t,a))(e,t,a))),e._handleRowCheckboxClicked=t=>{var a,o=t.currentTarget,i=o.rowId,r=e._groupData(e._filteredData,e.localizeFunc||e.hass.localize,e.appendRow,e.hasFab,e.groupColumn,e.groupOrder,e._collapsedGroups,e.sortColumn,e.sortDirection);if(!1!==(null===(a=r.find((t=>t[e.id]===i)))||void 0===a?void 0:a.selectable)){var l=r.findIndex((t=>t[e.id]===i));if(t instanceof MouseEvent&&t.shiftKey&&null!==e._lastSelectedRowId){var n=r.findIndex((t=>t[e.id]===e._lastSelectedRowId));n>-1&&l>-1&&(e._checkedRows=[].concat((0,k.A)(e._checkedRows),(0,k.A)(e._selectRange(r,n,l))))}else o.checked?e._checkedRows=e._checkedRows.filter((e=>e!==i)):e._checkedRows.includes(i)||(e._checkedRows=[].concat((0,k.A)(e._checkedRows),[i]));l>-1&&(e._lastSelectedRowId=i),e._checkedRowsChanged()}},e._handleRowClick=t=>{if(!t.composedPath().find((e=>["ha-checkbox","ha-button","ha-button","ha-icon-button","ha-assist-chip"].includes(e.localName)))){var a=t.currentTarget.rowId;(0,P.r)((0,R.A)(e),"row-click",{id:a},{bubbles:!1})}},e._collapseGroup=t=>{var a=t.currentTarget.group;e._collapsedGroups.includes(a)?e._collapsedGroups=e._collapsedGroups.filter((e=>e!==a)):e._collapsedGroups=[].concat((0,k.A)(e._collapsedGroups),[a]),e._lastSelectedRowId=null,(0,P.r)((0,R.A)(e),"collapsed-changed",{value:e._collapsedGroups})},e}return(0,L.A)(t,e),(0,C.A)(t,[{key:"clearSelection",value:function(){this._checkedRows=[],this._lastSelectedRowId=null,this._checkedRowsChanged()}},{key:"selectAll",value:function(){this._checkedRows=this._filteredData.filter((e=>!1!==e.selectable)).map((e=>e[this.id])),this._lastSelectedRowId=null,this._checkedRowsChanged()}},{key:"select",value:function(e,t){t&&(this._checkedRows=[]),e.forEach((e=>{var t=this._filteredData.find((t=>t[this.id]===e));!1===(null==t?void 0:t.selectable)||this._checkedRows.includes(e)||this._checkedRows.push(e)})),this._lastSelectedRowId=null,this._checkedRowsChanged()}},{key:"unselect",value:function(e){e.forEach((e=>{var t=this._checkedRows.indexOf(e);t>-1&&this._checkedRows.splice(t,1)})),this._lastSelectedRowId=null,this._checkedRowsChanged()}},{key:"connectedCallback",value:function(){(0,S.A)(t,"connectedCallback",this,3)([]),this._filteredData.length&&(this._filteredData=(0,k.A)(this._filteredData))}},{key:"firstUpdated",value:function(){this.updateComplete.then((()=>this._calcTableHeight()))}},{key:"updated",value:function(){var e=this.renderRoot.querySelector(".mdc-data-table__header-row");e&&(e.scrollWidth>e.clientWidth?this.style.setProperty("--table-row-width",`${e.scrollWidth}px`):this.style.removeProperty("--table-row-width"))}},{key:"willUpdate",value:function(e){if((0,S.A)(t,"willUpdate",this,3)([e]),this.hasUpdated||(0,U.i)(),e.has("columns")){if(this._filterable=Object.values(this.columns).some((e=>e.filterable)),!this.sortColumn)for(var a in this.columns)if(this.columns[a].direction){this.sortDirection=this.columns[a].direction,this.sortColumn=a,this._lastSelectedRowId=null,(0,P.r)(this,"sorting-changed",{column:a,direction:this.sortDirection});break}var o=(0,D.A)(this.columns);Object.values(o).forEach((e=>{delete e.title,delete e.template,delete e.extraTemplate})),this._sortColumns=o}if(e.has("filter")&&(this._debounceSearch(this.filter),this._lastSelectedRowId=null),e.has("data")){if(this._checkedRows.length){var i=new Set(this.data.map((e=>String(e[this.id])))),r=this._checkedRows.filter((e=>i.has(e)));r.length!==this._checkedRows.length&&(this._checkedRows=r,this._checkedRowsChanged())}this._checkableRowsCount=this.data.filter((e=>!1!==e.selectable)).length}!this.hasUpdated&&this.initialCollapsedGroups?(this._collapsedGroups=this.initialCollapsedGroups,this._lastSelectedRowId=null,(0,P.r)(this,"collapsed-changed",{value:this._collapsedGroups})):e.has("groupColumn")&&(this._collapsedGroups=[],this._lastSelectedRowId=null,(0,P.r)(this,"collapsed-changed",{value:this._collapsedGroups})),(e.has("data")||e.has("columns")||e.has("_filter")||e.has("sortColumn")||e.has("sortDirection"))&&this._sortFilterData(),(e.has("_filter")||e.has("sortColumn")||e.has("sortDirection"))&&(this._lastSelectedRowId=null),(e.has("selectable")||e.has("hiddenColumns"))&&(this._filteredData=(0,k.A)(this._filteredData))}},{key:"render",value:function(){var e=this.localizeFunc||this.hass.localize,t=this._sortedColumns(this.columns,this.columnOrder);return(0,Z.qy)(p||(p=Y`
      <div class="mdc-data-table">
        <slot name="header" @slotchange=${0}>
          ${0}
        </slot>
        <div
          class="mdc-data-table__table ${0}"
          role="table"
          aria-rowcount=${0}
          style=${0}
        >
          <div
            class="mdc-data-table__header-row"
            role="row"
            aria-rowindex="1"
            @scroll=${0}
          >
            <slot name="header-row">
              ${0}
              ${0}
            </slot>
          </div>
          ${0}
        </div>
      </div>
    `),this._calcTableHeight,this._filterable?(0,Z.qy)(_||(_=Y`
                <div class="table-header">
                  <search-input
                    .hass=${0}
                    @value-changed=${0}
                    .label=${0}
                    .noLabelFloat=${0}
                  ></search-input>
                </div>
              `),this.hass,this._handleSearchChange,this.searchLabel,this.noLabelFloat):"",(0,H.H)({"auto-height":this.autoHeight}),this._filteredData.length+1,(0,O.W)({height:this.autoHeight?53*(this._filteredData.length||1)+53+"px":`calc(100% - ${this._headerHeight}px)`}),this._scrollContent,this.selectable?(0,Z.qy)(b||(b=Y`
                    <div
                      class="mdc-data-table__header-cell mdc-data-table__header-cell--checkbox"
                      role="columnheader"
                    >
                      <ha-checkbox
                        class="mdc-data-table__row-checkbox"
                        @change=${0}
                        .indeterminate=${0}
                        .checked=${0}
                      >
                      </ha-checkbox>
                    </div>
                  `),this._handleHeaderRowCheckboxClick,this._checkedRows.length&&this._checkedRows.length!==this._checkableRowsCount,this._checkedRows.length&&this._checkedRows.length===this._checkableRowsCount):"",Object.entries(t).map((e=>{var t,a,o=(0,$.A)(e,2),i=o[0],r=o[1];if(r.hidden||(this.columnOrder&&this.columnOrder.includes(i)&&null!==(t=null===(a=this.hiddenColumns)||void 0===a?void 0:a.includes(i))&&void 0!==t?t:r.defaultHidden))return Z.s6;var l=i===this.sortColumn,n={"mdc-data-table__header-cell--numeric":"numeric"===r.type,"mdc-data-table__header-cell--icon":"icon"===r.type,"mdc-data-table__header-cell--icon-button":"icon-button"===r.type,"mdc-data-table__header-cell--overflow-menu":"overflow-menu"===r.type,"mdc-data-table__header-cell--overflow":"overflow"===r.type,sortable:Boolean(r.sortable),"not-sorted":Boolean(r.sortable&&!l)};return(0,Z.qy)(v||(v=Y`
                  <div
                    aria-label=${0}
                    class="mdc-data-table__header-cell ${0}"
                    style=${0}
                    role="columnheader"
                    aria-sort=${0}
                    @click=${0}
                    .columnId=${0}
                    title=${0}
                  >
                    ${0}
                    <span>${0}</span>
                  </div>
                `),(0,T.J)(r.label),(0,H.H)(n),(0,O.W)({minWidth:r.minWidth,maxWidth:r.maxWidth,flex:r.flex||1}),(0,T.J)(l?"desc"===this.sortDirection?"descending":"ascending":void 0),this._handleHeaderClick,i,(0,T.J)(r.title),r.sortable?(0,Z.qy)(m||(m=Y`
                          <ha-svg-icon
                            .path=${0}
                          ></ha-svg-icon>
                        `),l&&"desc"===this.sortDirection?"M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z":"M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z"):"",r.title)})),this._filteredData.length?(0,Z.qy)(g||(g=Y`
                <lit-virtualizer
                  scroller
                  class="mdc-data-table__content scroller ha-scrollbar"
                  @scroll=${0}
                  .items=${0}
                  .keyFunction=${0}
                  .renderItem=${0}
                ></lit-virtualizer>
              `),this._saveScrollPos,this._groupData(this._filteredData,e,this.appendRow,this.hasFab,this.groupColumn,this.groupOrder,this._collapsedGroups,this.sortColumn,this.sortDirection),this._keyFunction,((e,a)=>this._renderRow(t,this.narrow,e,a))):(0,Z.qy)(f||(f=Y`
                <div class="mdc-data-table__content">
                  <div class="mdc-data-table__row" role="row">
                    <div class="mdc-data-table__cell grows center" role="cell">
                      ${0}
                    </div>
                  </div>
                </div>
              `),this.noDataText||e("ui.components.data-table.no-data")))}},{key:"_sortFilterData",value:(o=(0,x.A)((0,w.A)().m((function e(){var t,a,o,i,r,l,n,s,c,d,h;return(0,w.A)().w((function(e){for(;;)switch(e.n){case 0:if(t=(new Date).getTime(),a=t-this._lastUpdate,o=t-this._curRequest,this._curRequest=t,i=!this._lastUpdate||a>500&&o<500,r=this.data,!this._filter){e.n=2;break}return e.n=1,this._memFilterData(this.data,this._sortColumns,this._filter.trim());case 1:r=e.v;case 2:if(i||this._curRequest===t){e.n=3;break}return e.a(2);case 3:return l=this.sortColumn&&this._sortColumns[this.sortColumn]?J(r,this._sortColumns[this.sortColumn],this.sortDirection,this.sortColumn,this.hass.locale.language):r,e.n=4,Promise.all([l,N.E]);case 4:if(n=e.v,s=(0,$.A)(n,1),c=s[0],d=(new Date).getTime(),!((h=d-t)<100)){e.n=5;break}return e.n=5,new Promise((e=>{setTimeout(e,100-h)}));case 5:if(i||this._curRequest===t){e.n=6;break}return e.a(2);case 6:this._lastUpdate=t,this._filteredData=c;case 7:return e.a(2)}}),e,this)}))),function(){return o.apply(this,arguments)})},{key:"_handleHeaderClick",value:function(e){var t=e.currentTarget.columnId;this.columns[t].sortable&&(this.sortDirection&&this.sortColumn===t?"asc"===this.sortDirection?this.sortDirection="desc":this.sortDirection=null:this.sortDirection="asc",this.sortColumn=null===this.sortDirection?void 0:t,(0,P.r)(this,"sorting-changed",{column:t,direction:this.sortDirection}))}},{key:"_handleHeaderRowCheckboxClick",value:function(e){e.target.checked?this.selectAll():(this._checkedRows=[],this._checkedRowsChanged()),this._lastSelectedRowId=null}},{key:"_selectRange",value:function(e,t,a){for(var o=Math.min(t,a),i=Math.max(t,a),r=[],l=o;l<=i;l++){var n=e[l];n&&!1!==n.selectable&&!this._checkedRows.includes(n[this.id])&&r.push(n[this.id])}return r}},{key:"_setTitle",value:function(e){var t=e.currentTarget;t.scrollWidth>t.offsetWidth&&t.setAttribute("title",t.innerText)}},{key:"_checkedRowsChanged",value:function(){this._filteredData.length&&(this._filteredData=(0,k.A)(this._filteredData)),(0,P.r)(this,"selection-changed",{value:this._checkedRows})}},{key:"_handleSearchChange",value:function(e){this.filter||(this._lastSelectedRowId=null,this._debounceSearch(e.detail.value))}},{key:"_calcTableHeight",value:(a=(0,x.A)((0,w.A)().m((function e(){return(0,w.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this.autoHeight){e.n=1;break}return e.a(2);case 1:return e.n=2,this.updateComplete;case 2:this._headerHeight=this._header.clientHeight;case 3:return e.a(2)}}),e,this)}))),function(){return a.apply(this,arguments)})},{key:"_saveScrollPos",value:function(e){this._savedScrollPos=e.target.scrollTop,this.renderRoot.querySelector(".mdc-data-table__header-row").scrollLeft=e.target.scrollLeft}},{key:"_scrollContent",value:function(e){this.renderRoot.querySelector("lit-virtualizer").scrollLeft=e.target.scrollLeft}},{key:"expandAllGroups",value:function(){this._collapsedGroups=[],this._lastSelectedRowId=null,(0,P.r)(this,"collapsed-changed",{value:this._collapsedGroups})}},{key:"collapseAllGroups",value:function(){if(this.groupColumn&&this.data.some((e=>e[this.groupColumn]))){var e=E(this.data,(e=>e[this.groupColumn]));e.undefined&&(e[Q]=e.undefined,delete e.undefined),this._collapsedGroups=Object.keys(e),this._lastSelectedRowId=null,(0,P.r)(this,"collapsed-changed",{value:this._collapsedGroups})}}}],[{key:"styles",get:function(){return[j.dp,(0,Z.AH)(y||(y=Y`
        /* default mdc styles, colors changed, without checkbox styles */
        :host {
          height: 100%;
        }
        .mdc-data-table__content {
          font-family: var(--ha-font-family-body);
          -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
          -webkit-font-smoothing: var(--ha-font-smoothing);
          font-size: 0.875rem;
          line-height: var(--ha-line-height-condensed);
          font-weight: var(--ha-font-weight-normal);
          letter-spacing: 0.0178571429em;
          text-decoration: inherit;
          text-transform: inherit;
        }

        .mdc-data-table {
          background-color: var(--data-table-background-color);
          border-radius: var(--ha-border-radius-sm);
          border-width: 1px;
          border-style: solid;
          border-color: var(--divider-color);
          display: inline-flex;
          flex-direction: column;
          box-sizing: border-box;
          overflow: hidden;
        }

        .mdc-data-table__row--selected {
          background-color: rgba(var(--rgb-primary-color), 0.04);
        }

        .mdc-data-table__row {
          display: flex;
          height: var(--data-table-row-height, 52px);
          width: var(--table-row-width, 100%);
        }

        .mdc-data-table__row.empty-row {
          height: var(
            --data-table-empty-row-height,
            var(--data-table-row-height, 52px)
          );
        }

        .mdc-data-table__row ~ .mdc-data-table__row {
          border-top: 1px solid var(--divider-color);
        }

        .mdc-data-table__row.clickable:not(
            .mdc-data-table__row--selected
          ):hover {
          background-color: rgba(var(--rgb-primary-text-color), 0.04);
        }

        .mdc-data-table__header-cell {
          color: var(--primary-text-color);
        }

        .mdc-data-table__cell {
          color: var(--primary-text-color);
        }

        .mdc-data-table__header-row {
          height: 56px;
          display: flex;
          border-bottom: 1px solid var(--divider-color);
          overflow: auto;
        }

        /* Hide scrollbar for Chrome, Safari and Opera */
        .mdc-data-table__header-row::-webkit-scrollbar {
          display: none;
        }

        /* Hide scrollbar for IE, Edge and Firefox */
        .mdc-data-table__header-row {
          -ms-overflow-style: none; /* IE and Edge */
          scrollbar-width: none; /* Firefox */
        }

        .mdc-data-table__cell,
        .mdc-data-table__header-cell {
          padding-right: 16px;
          padding-left: 16px;
          min-width: 150px;
          align-self: center;
          overflow: hidden;
          text-overflow: ellipsis;
          flex-shrink: 0;
          box-sizing: border-box;
        }

        .mdc-data-table__cell.mdc-data-table__cell--flex {
          display: flex;
          overflow: initial;
        }

        .mdc-data-table__cell.mdc-data-table__cell--icon {
          overflow: initial;
        }

        .mdc-data-table__header-cell--checkbox,
        .mdc-data-table__cell--checkbox {
          /* @noflip */
          padding-left: 16px;
          /* @noflip */
          padding-right: 0;
          /* @noflip */
          padding-inline-start: 16px;
          /* @noflip */
          padding-inline-end: initial;
          width: 60px;
          min-width: 60px;
        }

        .mdc-data-table__table {
          height: 100%;
          width: 100%;
          border: 0;
          white-space: nowrap;
          position: relative;
        }

        .mdc-data-table__cell {
          font-family: var(--ha-font-family-body);
          -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
          -webkit-font-smoothing: var(--ha-font-smoothing);
          font-size: 0.875rem;
          line-height: var(--ha-line-height-condensed);
          font-weight: var(--ha-font-weight-normal);
          letter-spacing: 0.0178571429em;
          text-decoration: inherit;
          text-transform: inherit;
          flex-grow: 0;
          flex-shrink: 0;
        }

        .mdc-data-table__cell a {
          color: inherit;
          text-decoration: none;
        }

        .mdc-data-table__cell--numeric {
          text-align: var(--float-end);
        }

        .mdc-data-table__cell--icon {
          color: var(--secondary-text-color);
          text-align: center;
        }

        .mdc-data-table__header-cell--icon,
        .mdc-data-table__cell--icon {
          min-width: 64px;
          flex: 0 0 64px !important;
        }

        .mdc-data-table__cell--icon img {
          width: 24px;
          height: 24px;
        }

        .mdc-data-table__header-cell.mdc-data-table__header-cell--icon {
          text-align: center;
        }

        .mdc-data-table__header-cell.sortable.mdc-data-table__header-cell--icon:hover,
        .mdc-data-table__header-cell.sortable.mdc-data-table__header-cell--icon:not(
            .not-sorted
          ) {
          text-align: var(--float-start);
        }

        .mdc-data-table__cell--icon:first-child img,
        .mdc-data-table__cell--icon:first-child ha-icon,
        .mdc-data-table__cell--icon:first-child ha-svg-icon,
        .mdc-data-table__cell--icon:first-child ha-state-icon,
        .mdc-data-table__cell--icon:first-child ha-domain-icon,
        .mdc-data-table__cell--icon:first-child ha-service-icon {
          margin-left: 8px;
          margin-inline-start: 8px;
          margin-inline-end: initial;
        }

        .mdc-data-table__cell--icon:first-child state-badge {
          margin-right: -8px;
          margin-inline-end: -8px;
          margin-inline-start: initial;
        }

        .mdc-data-table__cell--overflow-menu,
        .mdc-data-table__header-cell--overflow-menu,
        .mdc-data-table__header-cell--icon-button,
        .mdc-data-table__cell--icon-button {
          min-width: 64px;
          flex: 0 0 64px !important;
          padding: 8px;
        }

        .mdc-data-table__header-cell--icon-button,
        .mdc-data-table__cell--icon-button {
          min-width: 56px;
          width: 56px;
        }

        .mdc-data-table__cell--overflow-menu,
        .mdc-data-table__cell--icon-button {
          color: var(--secondary-text-color);
          text-overflow: clip;
        }

        .mdc-data-table__header-cell--icon-button:first-child,
        .mdc-data-table__cell--icon-button:first-child,
        .mdc-data-table__header-cell--icon-button:last-child,
        .mdc-data-table__cell--icon-button:last-child {
          width: 64px;
        }

        .mdc-data-table__cell--overflow-menu:first-child,
        .mdc-data-table__header-cell--overflow-menu:first-child,
        .mdc-data-table__header-cell--icon-button:first-child,
        .mdc-data-table__cell--icon-button:first-child {
          padding-left: 16px;
          padding-inline-start: 16px;
          padding-inline-end: initial;
        }

        .mdc-data-table__cell--overflow-menu:last-child,
        .mdc-data-table__header-cell--overflow-menu:last-child,
        .mdc-data-table__header-cell--icon-button:last-child,
        .mdc-data-table__cell--icon-button:last-child {
          padding-right: 16px;
          padding-inline-end: 16px;
          padding-inline-start: initial;
        }
        .mdc-data-table__cell--overflow-menu,
        .mdc-data-table__cell--overflow,
        .mdc-data-table__header-cell--overflow-menu,
        .mdc-data-table__header-cell--overflow {
          overflow: initial;
        }
        .mdc-data-table__cell--icon-button a {
          color: var(--secondary-text-color);
        }

        .mdc-data-table__header-cell {
          font-family: var(--ha-font-family-body);
          -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
          -webkit-font-smoothing: var(--ha-font-smoothing);
          font-size: var(--ha-font-size-s);
          line-height: var(--ha-line-height-normal);
          font-weight: var(--ha-font-weight-medium);
          letter-spacing: 0.0071428571em;
          text-decoration: inherit;
          text-transform: inherit;
          text-align: var(--float-start);
        }

        .mdc-data-table__header-cell--numeric {
          text-align: var(--float-end);
        }
        .mdc-data-table__header-cell--numeric.sortable:hover,
        .mdc-data-table__header-cell--numeric.sortable:not(.not-sorted) {
          text-align: var(--float-start);
        }

        /* custom from here */

        .group-header {
          padding-top: 12px;
          height: var(--data-table-row-height, 52px);
          padding-left: 12px;
          padding-inline-start: 12px;
          padding-inline-end: initial;
          width: 100%;
          font-weight: var(--ha-font-weight-medium);
          display: flex;
          align-items: center;
          cursor: pointer;
          background-color: var(--primary-background-color);
        }

        .group-header ha-icon-button {
          transition: transform 0.2s ease;
        }

        .group-header ha-icon-button.collapsed {
          transform: rotate(180deg);
        }

        :host {
          display: block;
        }

        .mdc-data-table {
          display: block;
          border-width: var(--data-table-border-width, 1px);
          height: 100%;
        }
        .mdc-data-table__header-cell {
          overflow: hidden;
          position: relative;
        }
        .mdc-data-table__header-cell span {
          position: relative;
          left: 0px;
          inset-inline-start: 0px;
          inset-inline-end: initial;
        }

        .mdc-data-table__header-cell.sortable {
          cursor: pointer;
        }
        .mdc-data-table__header-cell > * {
          transition: var(--float-start) 0.2s ease;
        }
        .mdc-data-table__header-cell ha-svg-icon {
          top: -3px;
          position: absolute;
        }
        .mdc-data-table__header-cell.not-sorted ha-svg-icon {
          left: -20px;
          inset-inline-start: -20px;
          inset-inline-end: initial;
        }
        .mdc-data-table__header-cell.sortable:not(.not-sorted) span,
        .mdc-data-table__header-cell.sortable.not-sorted:hover span {
          left: 24px;
          inset-inline-start: 24px;
          inset-inline-end: initial;
        }
        .mdc-data-table__header-cell.sortable:not(.not-sorted) ha-svg-icon,
        .mdc-data-table__header-cell.sortable:hover.not-sorted ha-svg-icon {
          left: 12px;
          inset-inline-start: 12px;
          inset-inline-end: initial;
        }
        .table-header {
          border-bottom: 1px solid var(--divider-color);
        }
        search-input {
          display: block;
          flex: 1;
          --mdc-text-field-fill-color: var(--sidebar-background-color);
          --mdc-text-field-idle-line-color: transparent;
        }
        slot[name="header"] {
          display: block;
        }
        .center {
          text-align: center;
        }
        .secondary {
          color: var(--secondary-text-color);
        }
        .scroller {
          height: calc(100% - 57px);
          overflow: overlay !important;
        }

        .mdc-data-table__table.auto-height .scroller {
          overflow-y: hidden !important;
        }
        .grows {
          flex-grow: 1;
          flex-shrink: 1;
        }
        .forceLTR {
          direction: ltr;
        }
        .clickable {
          cursor: pointer;
        }
        lit-virtualizer {
          contain: size layout !important;
          overscroll-behavior: contain;
        }
      `))]}}]);var a,o}(Z.WF);(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"hass",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"localizeFunc",void 0),(0,z.__decorate)([(0,q.MZ)({type:Boolean})],X.prototype,"narrow",void 0),(0,z.__decorate)([(0,q.MZ)({type:Object})],X.prototype,"columns",void 0),(0,z.__decorate)([(0,q.MZ)({type:Array})],X.prototype,"data",void 0),(0,z.__decorate)([(0,q.MZ)({type:Boolean})],X.prototype,"selectable",void 0),(0,z.__decorate)([(0,q.MZ)({type:Boolean})],X.prototype,"clickable",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:"has-fab",type:Boolean})],X.prototype,"hasFab",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"appendRow",void 0),(0,z.__decorate)([(0,q.MZ)({type:Boolean,attribute:"auto-height"})],X.prototype,"autoHeight",void 0),(0,z.__decorate)([(0,q.MZ)({type:String})],X.prototype,"id",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1,type:String})],X.prototype,"noDataText",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1,type:String})],X.prototype,"searchLabel",void 0),(0,z.__decorate)([(0,q.MZ)({type:Boolean,attribute:"no-label-float"})],X.prototype,"noLabelFloat",void 0),(0,z.__decorate)([(0,q.MZ)({type:String})],X.prototype,"filter",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"groupColumn",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"groupOrder",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"sortColumn",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"sortDirection",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"initialCollapsedGroups",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"hiddenColumns",void 0),(0,z.__decorate)([(0,q.MZ)({attribute:!1})],X.prototype,"columnOrder",void 0),(0,z.__decorate)([(0,q.wk)()],X.prototype,"_filterable",void 0),(0,z.__decorate)([(0,q.wk)()],X.prototype,"_filter",void 0),(0,z.__decorate)([(0,q.wk)()],X.prototype,"_filteredData",void 0),(0,z.__decorate)([(0,q.wk)()],X.prototype,"_headerHeight",void 0),(0,z.__decorate)([(0,q.P)("slot[name='header']")],X.prototype,"_header",void 0),(0,z.__decorate)([(0,q.wk)()],X.prototype,"_collapsedGroups",void 0),(0,z.__decorate)([(0,q.wk)()],X.prototype,"_lastSelectedRowId",void 0),(0,z.__decorate)([(0,F.a)(".scroller")],X.prototype,"_savedScrollPos",void 0),(0,z.__decorate)([(0,q.Ls)({passive:!0})],X.prototype,"_saveScrollPos",null),(0,z.__decorate)([(0,q.Ls)({passive:!0})],X.prototype,"_scrollContent",null),X=(0,z.__decorate)([(0,q.EM)("ha-data-table")],X)},63419:function(e,t,a){var o,i=a(44734),r=a(56038),l=a(69683),n=a(6454),s=(a(28706),a(62826)),c=a(96196),d=a(77845),h=a(92542),u=(a(41742),a(25460)),p=a(26139),_=a(8889),b=a(63374),v=function(e){function t(){return(0,i.A)(this,t),(0,l.A)(this,t,arguments)}return(0,n.A)(t,e),(0,r.A)(t,[{key:"connectedCallback",value:function(){(0,u.A)(t,"connectedCallback",this,3)([]),this.addEventListener("close-menu",this._handleCloseMenu)}},{key:"_handleCloseMenu",value:function(e){var t,a;e.detail.reason.kind===b.fi.KEYDOWN&&e.detail.reason.key===b.NV.ESCAPE||null===(t=(a=e.detail.initiator).clickAction)||void 0===t||t.call(a,e.detail.initiator)}}])}(p.W1);v.styles=[_.R,(0,c.AH)(o||(o=(e=>e)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],v=(0,s.__decorate)([(0,d.EM)("ha-md-menu")],v);var m,f,g=e=>e,y=function(e){function t(){var e;(0,i.A)(this,t);for(var a=arguments.length,o=new Array(a),r=0;r<a;r++)o[r]=arguments[r];return(e=(0,l.A)(this,t,[].concat(o))).disabled=!1,e.anchorCorner="end-start",e.menuCorner="start-start",e.hasOverflow=!1,e.quick=!1,e}return(0,n.A)(t,e),(0,r.A)(t,[{key:"items",get:function(){return this._menu.items}},{key:"focus",value:function(){var e;this._menu.open?this._menu.focus():null===(e=this._triggerButton)||void 0===e||e.focus()}},{key:"render",value:function(){return(0,c.qy)(m||(m=g`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-md-menu
        .quick=${0}
        .positioning=${0}
        .hasOverflow=${0}
        .anchorCorner=${0}
        .menuCorner=${0}
        @opening=${0}
        @closing=${0}
      >
        <slot></slot>
      </ha-md-menu>
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}},{key:"_handleOpening",value:function(){(0,h.r)(this,"opening",void 0,{composed:!1})}},{key:"_handleClosing",value:function(){(0,h.r)(this,"closing",void 0,{composed:!1})}},{key:"_handleClick",value:function(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}},{key:"_triggerButton",get:function(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}},{key:"_setTriggerAria",value:function(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}}])}(c.WF);y.styles=(0,c.AH)(f||(f=g`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,s.__decorate)([(0,d.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,s.__decorate)([(0,d.MZ)()],y.prototype,"positioning",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:"anchor-corner"})],y.prototype,"anchorCorner",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:"menu-corner"})],y.prototype,"menuCorner",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean,attribute:"has-overflow"})],y.prototype,"hasOverflow",void 0),(0,s.__decorate)([(0,d.MZ)({type:Boolean})],y.prototype,"quick",void 0),(0,s.__decorate)([(0,d.P)("ha-md-menu",!0)],y.prototype,"_menu",void 0),y=(0,s.__decorate)([(0,d.EM)("ha-md-button-menu")],y)},32072:function(e,t,a){var o,i=a(56038),r=a(44734),l=a(69683),n=a(6454),s=a(62826),c=a(10414),d=a(18989),h=a(96196),u=a(77845),p=function(e){function t(){return(0,r.A)(this,t),(0,l.A)(this,t,arguments)}return(0,n.A)(t,e),(0,i.A)(t)}(c.c);p.styles=[d.R,(0,h.AH)(o||(o=(e=>e)`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `))],p=(0,s.__decorate)([(0,u.EM)("ha-md-divider")],p)},99892:function(e,t,a){var o,i=a(56038),r=a(44734),l=a(69683),n=a(6454),s=a(62826),c=a(54407),d=a(28522),h=a(96196),u=a(77845),p=function(e){function t(){return(0,r.A)(this,t),(0,l.A)(this,t,arguments)}return(0,n.A)(t,e),(0,i.A)(t)}(c.K);p.styles=[d.R,(0,h.AH)(o||(o=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
        --md-sys-color-secondary-container: rgba(
          var(--rgb-primary-color),
          0.15
        );
        --md-sys-color-on-secondary-container: var(--text-primary-color);
        --mdc-icon-size: 16px;

        --md-sys-color-on-primary-container: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-menu-item-label-text-font: Roboto, sans-serif;
      }
      :host(.warning) {
        --md-menu-item-label-text-color: var(--error-color);
        --md-menu-item-leading-icon-color: var(--error-color);
      }
      ::slotted([slot="headline"]) {
        text-wrap: nowrap;
      }
      :host([disabled]) {
        opacity: 1;
        --md-menu-item-label-text-color: var(--disabled-text-color);
        --md-menu-item-leading-icon-color: var(--disabled-text-color);
      }
    `))],(0,s.__decorate)([(0,u.MZ)({attribute:!1})],p.prototype,"clickAction",void 0),p=(0,s.__decorate)([(0,u.EM)("ha-md-menu-item")],p)},17262:function(e,t,a){var o,i,r,l=a(61397),n=a(50264),s=a(44734),c=a(56038),d=a(69683),h=a(6454),u=(a(28706),a(2008),a(18111),a(22489),a(26099),a(62826)),p=a(96196),_=a(77845),b=(a(60733),a(60961),a(78740),a(92542)),v=e=>e,m=function(e){function t(){var e;(0,s.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,d.A)(this,t,[].concat(o))).suffix=!1,e.autofocus=!1,e}return(0,h.A)(t,e),(0,c.A)(t,[{key:"focus",value:function(){var e;null===(e=this._input)||void 0===e||e.focus()}},{key:"render",value:function(){return(0,p.qy)(o||(o=v`
      <ha-textfield
        .autofocus=${0}
        autocomplete="off"
        .label=${0}
        .value=${0}
        icon
        .iconTrailing=${0}
        @input=${0}
      >
        <slot name="prefix" slot="leadingIcon">
          <ha-svg-icon
            tabindex="-1"
            class="prefix"
            .path=${0}
          ></ha-svg-icon>
        </slot>
        <div class="trailing" slot="trailingIcon">
          ${0}
          <slot name="suffix"></slot>
        </div>
      </ha-textfield>
    `),this.autofocus,this.label||this.hass.localize("ui.common.search"),this.filter||"",this.filter||this.suffix,this._filterInputChanged,"M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z",this.filter&&(0,p.qy)(i||(i=v`
            <ha-icon-button
              @click=${0}
              .label=${0}
              .path=${0}
              class="clear-button"
            ></ha-icon-button>
          `),this._clearSearch,this.hass.localize("ui.common.clear"),"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"))}},{key:"_filterChanged",value:(u=(0,n.A)((0,l.A)().m((function e(t){return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:(0,b.r)(this,"value-changed",{value:String(t)});case 1:return e.a(2)}}),e,this)}))),function(e){return u.apply(this,arguments)})},{key:"_filterInputChanged",value:(r=(0,n.A)((0,l.A)().m((function e(t){return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:this._filterChanged(t.target.value);case 1:return e.a(2)}}),e,this)}))),function(e){return r.apply(this,arguments)})},{key:"_clearSearch",value:(a=(0,n.A)((0,l.A)().m((function e(){return(0,l.A)().w((function(e){for(;;)switch(e.n){case 0:this._filterChanged("");case 1:return e.a(2)}}),e,this)}))),function(){return a.apply(this,arguments)})}]);var a,r,u}(p.WF);m.styles=(0,p.AH)(r||(r=v`
    :host {
      display: inline-flex;
    }
    ha-svg-icon,
    ha-icon-button {
      color: var(--primary-text-color);
    }
    ha-svg-icon {
      outline: none;
    }
    .clear-button {
      --mdc-icon-size: 20px;
    }
    ha-textfield {
      display: inherit;
    }
    .trailing {
      display: flex;
      align-items: center;
    }
  `)),(0,u.__decorate)([(0,_.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,u.__decorate)([(0,_.MZ)()],m.prototype,"filter",void 0),(0,u.__decorate)([(0,_.MZ)({type:Boolean})],m.prototype,"suffix",void 0),(0,u.__decorate)([(0,_.MZ)({type:Boolean})],m.prototype,"autofocus",void 0),(0,u.__decorate)([(0,_.MZ)({type:String})],m.prototype,"label",void 0),(0,u.__decorate)([(0,_.P)("ha-textfield",!0)],m.prototype,"_input",void 0),m=(0,u.__decorate)([(0,_.EM)("search-input")],m)},84884:function(e,t,a){var o,i,r,l=a(44734),n=a(56038),s=a(69683),c=a(6454),d=a(25460),h=(a(28706),a(2008),a(50113),a(74423),a(62062),a(18111),a(22489),a(20116),a(61701),a(26099),a(62826)),u=a(96196),p=a(77845),_=a(94333),b=a(22786),v=(a(13579),a(55376)),m=a(92209),f=(e,t)=>!t.component||(0,v.e)(t.component).some((t=>(0,m.x)(e,t))),g=(e,t)=>!t.not_component||!(0,v.e)(t.not_component).some((t=>(0,m.x)(e,t))),y=e=>e.core,w=(e,t)=>(e=>e.advancedOnly)(t)&&!(e=>{var t;return null===(t=e.userData)||void 0===t?void 0:t.showAdvanced})(e),x=a(5871),k=a(39501),$=(a(371),a(45397),a(60961),a(32288)),A=(a(95591),e=>e),C=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).active=!1,e.narrow=!1,e}return(0,c.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){return(0,u.qy)(o||(o=A`
      <div
        tabindex="0"
        role="tab"
        aria-selected=${0}
        aria-label=${0}
        @keydown=${0}
      >
        ${0}
        <span class="name">${0}</span>
        <ha-ripple></ha-ripple>
      </div>
    `),this.active,(0,$.J)(this.name),this._handleKeyDown,this.narrow?(0,u.qy)(i||(i=A`<slot name="icon"></slot>`)):"",this.name)}},{key:"_handleKeyDown",value:function(e){"Enter"===e.key&&e.target.click()}}])}(u.WF);C.styles=(0,u.AH)(r||(r=A`
    div {
      padding: 0 32px;
      display: flex;
      flex-direction: column;
      text-align: center;
      box-sizing: border-box;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: var(--header-height);
      cursor: pointer;
      position: relative;
      outline: none;
    }

    .name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }

    :host([active]) {
      color: var(--primary-color);
    }

    :host(:not([narrow])[active]) div {
      border-bottom: 2px solid var(--primary-color);
    }

    :host([narrow]) {
      min-width: 0;
      display: flex;
      justify-content: center;
      overflow: hidden;
    }

    :host([narrow]) div {
      padding: 0 4px;
    }

    div:focus-visible:before {
      position: absolute;
      display: block;
      content: "";
      inset: 0;
      background-color: var(--secondary-text-color);
      opacity: 0.08;
    }
  `)),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],C.prototype,"active",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],C.prototype,"narrow",void 0),(0,h.__decorate)([(0,p.MZ)()],C.prototype,"name",void 0),C=(0,h.__decorate)([(0,p.EM)("ha-tab")],C);var R,M,L,S,z,D,Z,q,H,T,O,I,F=a(39396),P=e=>e,B=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).supervisor=!1,e.mainPage=!1,e.narrow=!1,e.isWide=!1,e.pane=!1,e.hasFab=!1,e._getTabs=(0,b.A)(((t,a,o,i,r,l,n)=>{var s=t.filter((t=>((e,t)=>(y(t)||f(e,t))&&!w(e,t)&&g(e,t))(e.hass,t)));if(s.length<2){if(1===s.length){var c=s[0];return[c.translationKey?n(c.translationKey):c.name]}return[""]}return s.map((t=>(0,u.qy)(R||(R=P`
          <a href=${0}>
            <ha-tab
              .hass=${0}
              .active=${0}
              .narrow=${0}
              .name=${0}
            >
              ${0}
            </ha-tab>
          </a>
        `),t.path,e.hass,t.path===(null==a?void 0:a.path),e.narrow,t.translationKey?n(t.translationKey):t.name,t.iconPath?(0,u.qy)(M||(M=P`<ha-svg-icon
                    slot="icon"
                    .path=${0}
                  ></ha-svg-icon>`),t.iconPath):"")))})),e}return(0,c.A)(t,e),(0,n.A)(t,[{key:"willUpdate",value:function(e){e.has("route")&&(this._activeTab=this.tabs.find((e=>`${this.route.prefix}${this.route.path}`.includes(e.path)))),(0,d.A)(t,"willUpdate",this,3)([e])}},{key:"render",value:function(){var e,t=this._getTabs(this.tabs,this._activeTab,this.hass.config.components,this.hass.language,this.hass.userData,this.narrow,this.localizeFunc||this.hass.localize),a=t.length>1;return(0,u.qy)(L||(L=P`
      <div class="toolbar">
        <slot name="toolbar">
          <div class="toolbar-content">
            ${0}
            ${0}
            ${0}
            <div id="toolbar-icon">
              <slot name="toolbar-icon"></slot>
            </div>
          </div>
        </slot>
        ${0}
      </div>
      <div
        class=${0}
      >
        ${0}
        <div
          class="content ha-scrollbar ${0}"
          @scroll=${0}
        >
          <slot></slot>
          ${0}
        </div>
      </div>
      <div id="fab" class=${0}>
        <slot name="fab"></slot>
      </div>
    `),this.mainPage||!this.backPath&&null!==(e=history.state)&&void 0!==e&&e.root?(0,u.qy)(S||(S=P`
                  <ha-menu-button
                    .hassio=${0}
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.supervisor,this.hass,this.narrow):this.backPath?(0,u.qy)(z||(z=P`
                    <a href=${0}>
                      <ha-icon-button-arrow-prev
                        .hass=${0}
                      ></ha-icon-button-arrow-prev>
                    </a>
                  `),this.backPath,this.hass):(0,u.qy)(D||(D=P`
                    <ha-icon-button-arrow-prev
                      .hass=${0}
                      @click=${0}
                    ></ha-icon-button-arrow-prev>
                  `),this.hass,this._backTapped),this.narrow||!a?(0,u.qy)(Z||(Z=P`<div class="main-title">
                  <slot name="header">${0}</slot>
                </div>`),a?"":t[0]):"",a&&!this.narrow?(0,u.qy)(q||(q=P`<div id="tabbar">${0}</div>`),t):"",a&&this.narrow?(0,u.qy)(H||(H=P`<div id="tabbar" class="bottom-bar">${0}</div>`),t):"",(0,_.H)({container:!0,tabs:a&&this.narrow}),this.pane?(0,u.qy)(T||(T=P`<div class="pane">
              <div class="shadow-container"></div>
              <div class="ha-scrollbar">
                <slot name="pane"></slot>
              </div>
            </div>`)):u.s6,(0,_.H)({tabs:a}),this._saveScrollPos,this.hasFab?(0,u.qy)(O||(O=P`<div class="fab-bottom-space"></div>`)):u.s6,(0,_.H)({tabs:a}))}},{key:"_saveScrollPos",value:function(e){this._savedScrollPos=e.target.scrollTop}},{key:"_backTapped",value:function(){this.backCallback?this.backCallback():(0,x.O)()}}],[{key:"styles",get:function(){return[F.dp,(0,u.AH)(I||(I=P`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }

        :host([narrow]) {
          width: 100%;
          position: fixed;
        }

        .container {
          display: flex;
          height: calc(
            100% - var(--header-height, 0px) - var(--safe-area-inset-top, 0px)
          );
        }

        ha-menu-button {
          margin-right: 24px;
          margin-inline-end: 24px;
          margin-inline-start: initial;
        }

        .toolbar {
          font-size: var(--ha-font-size-xl);
          height: calc(
            var(--header-height, 0px) + var(--safe-area-inset-top, 0px)
          );
          padding-top: var(--safe-area-inset-top);
          padding-right: var(--safe-area-inset-right);
          background-color: var(--sidebar-background-color);
          font-weight: var(--ha-font-weight-normal);
          border-bottom: 1px solid var(--divider-color);
          box-sizing: border-box;
        }
        :host([narrow]) .toolbar {
          padding-left: var(--safe-area-inset-left);
        }
        .toolbar-content {
          padding: 8px 12px;
          display: flex;
          align-items: center;
          height: 100%;
          box-sizing: border-box;
        }
        :host([narrow]) .toolbar-content {
          padding: 4px;
        }
        .toolbar a {
          color: var(--sidebar-text-color);
          text-decoration: none;
        }
        .bottom-bar a {
          width: 25%;
        }

        #tabbar {
          display: flex;
          font-size: var(--ha-font-size-m);
          overflow: hidden;
        }

        #tabbar > a {
          overflow: hidden;
          max-width: 45%;
        }

        #tabbar.bottom-bar {
          position: absolute;
          bottom: 0;
          left: 0;
          padding: 0 16px;
          box-sizing: border-box;
          background-color: var(--sidebar-background-color);
          border-top: 1px solid var(--divider-color);
          justify-content: space-around;
          z-index: 2;
          font-size: var(--ha-font-size-s);
          width: 100%;
          padding-bottom: var(--safe-area-inset-bottom);
        }

        #tabbar:not(.bottom-bar) {
          flex: 1;
          justify-content: center;
        }

        :host(:not([narrow])) #toolbar-icon {
          min-width: 40px;
        }

        ha-menu-button,
        ha-icon-button-arrow-prev,
        ::slotted([slot="toolbar-icon"]) {
          display: flex;
          flex-shrink: 0;
          pointer-events: auto;
          color: var(--sidebar-icon-color);
        }

        .main-title {
          flex: 1;
          max-height: var(--header-height);
          line-height: var(--ha-line-height-normal);
          color: var(--sidebar-text-color);
          margin: var(--main-title-margin, var(--margin-title));
        }

        .content {
          position: relative;
          width: 100%;
          margin-right: var(--safe-area-inset-right);
          margin-inline-end: var(--safe-area-inset-right);
          margin-bottom: var(--safe-area-inset-bottom);
          overflow: auto;
          -webkit-overflow-scrolling: touch;
        }
        :host([narrow]) .content {
          margin-left: var(--safe-area-inset-left);
          margin-inline-start: var(--safe-area-inset-left);
        }
        :host([narrow]) .content.tabs {
          /* Bottom bar reuses header height */
          margin-bottom: calc(
            var(--header-height, 0px) + var(--safe-area-inset-bottom, 0px)
          );
        }

        .content .fab-bottom-space {
          height: calc(64px + var(--safe-area-inset-bottom, 0px));
        }

        :host([narrow]) .content.tabs .fab-bottom-space {
          height: calc(80px + var(--safe-area-inset-bottom, 0px));
        }

        #fab {
          position: fixed;
          right: calc(16px + var(--safe-area-inset-right, 0px));
          inset-inline-end: calc(16px + var(--safe-area-inset-right));
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
          bottom: 24px;
          right: 24px;
          inset-inline-end: 24px;
          inset-inline-start: initial;
        }

        .pane {
          border-right: 1px solid var(--divider-color);
          border-inline-end: 1px solid var(--divider-color);
          border-inline-start: initial;
          box-sizing: border-box;
          display: flex;
          flex: 0 0 var(--sidepane-width, 250px);
          width: var(--sidepane-width, 250px);
          flex-direction: column;
          position: relative;
        }
        .pane .ha-scrollbar {
          flex: 1;
        }
      `))]}}])}(u.WF);(0,h.__decorate)([(0,p.MZ)({attribute:!1})],B.prototype,"hass",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],B.prototype,"supervisor",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],B.prototype,"localizeFunc",void 0),(0,h.__decorate)([(0,p.MZ)({type:String,attribute:"back-path"})],B.prototype,"backPath",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],B.prototype,"backCallback",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,attribute:"main-page"})],B.prototype,"mainPage",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],B.prototype,"route",void 0),(0,h.__decorate)([(0,p.MZ)({attribute:!1})],B.prototype,"tabs",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0})],B.prototype,"narrow",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,reflect:!0,attribute:"is-wide"})],B.prototype,"isWide",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],B.prototype,"pane",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,attribute:"has-fab"})],B.prototype,"hasFab",void 0),(0,h.__decorate)([(0,p.wk)()],B.prototype,"_activeTab",void 0),(0,h.__decorate)([(0,k.a)(".content")],B.prototype,"_savedScrollPos",void 0),(0,h.__decorate)([(0,p.Ls)({passive:!0})],B.prototype,"_saveScrollPos",null),B=(0,h.__decorate)([(0,p.EM)("hass-tabs-subpage")],B)}}]);
//# sourceMappingURL=1249.3c216c6cac707d64.js.map