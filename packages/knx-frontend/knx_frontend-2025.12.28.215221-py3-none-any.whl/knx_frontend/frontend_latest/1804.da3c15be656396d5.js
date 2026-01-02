export const __webpack_id__="1804";export const __webpack_ids__=["1804"];export const __webpack_modules__={92209:function(e,t,a){a.d(t,{x:()=>o});const o=(e,t)=>e&&e.config.components.includes(t)},25749:function(e,t,a){a.d(t,{SH:()=>n,u1:()=>d,xL:()=>s});var o=a(22786);const i=(0,o.A)((e=>new Intl.Collator(e,{numeric:!0}))),r=(0,o.A)((e=>new Intl.Collator(e,{sensitivity:"accent",numeric:!0}))),l=(e,t)=>e<t?-1:e>t?1:0,s=(e,t,a=void 0)=>Intl?.Collator?i(a).compare(e,t):l(e,t),n=(e,t,a=void 0)=>Intl?.Collator?r(a).compare(e,t):l(e.toLowerCase(),t.toLowerCase()),d=e=>(t,a)=>{const o=e.indexOf(t),i=e.indexOf(a);return o===i?0:-1===o?1:-1===i?-1:o-i}},40404:function(e,t,a){a.d(t,{s:()=>o});const o=(e,t,a=!1)=>{let o;const i=(...i)=>{const r=a&&!o;clearTimeout(o),o=window.setTimeout((()=>{o=void 0,e(...i)}),t),r&&e(...i)};return i.cancel=()=>{clearTimeout(o)},i}},37445:function(e,t,a){var o=a(62826),i=a(34271),r=a(96196),l=a(77845),s=a(94333),n=a(32288),d=a(29485),c=a(22786),h=a(39501),p=a(92542),_=a(25749),u=a(40404);const m=(e,t)=>{const a={};for(const o of e){const e=t(o);e in a?a[e].push(o):a[e]=[o]}return a};var b=a(39396),v=a(84183),f=(a(70524),a(60961),a(17262),a(2209));let g;const y=()=>(g||(g=(0,f.LV)(new Worker(new URL(a.p+a.u("4346"),a.b)))),g);var w=a(99034);const x="zzzzz_undefined";class k extends r.WF{clearSelection(){this._checkedRows=[],this._lastSelectedRowId=null,this._checkedRowsChanged()}selectAll(){this._checkedRows=this._filteredData.filter((e=>!1!==e.selectable)).map((e=>e[this.id])),this._lastSelectedRowId=null,this._checkedRowsChanged()}select(e,t){t&&(this._checkedRows=[]),e.forEach((e=>{const t=this._filteredData.find((t=>t[this.id]===e));!1===t?.selectable||this._checkedRows.includes(e)||this._checkedRows.push(e)})),this._lastSelectedRowId=null,this._checkedRowsChanged()}unselect(e){e.forEach((e=>{const t=this._checkedRows.indexOf(e);t>-1&&this._checkedRows.splice(t,1)})),this._lastSelectedRowId=null,this._checkedRowsChanged()}connectedCallback(){super.connectedCallback(),this._filteredData.length&&(this._filteredData=[...this._filteredData])}firstUpdated(){this.updateComplete.then((()=>this._calcTableHeight()))}updated(){const e=this.renderRoot.querySelector(".mdc-data-table__header-row");e&&(e.scrollWidth>e.clientWidth?this.style.setProperty("--table-row-width",`${e.scrollWidth}px`):this.style.removeProperty("--table-row-width"))}willUpdate(e){if(super.willUpdate(e),this.hasUpdated||(0,v.i)(),e.has("columns")){if(this._filterable=Object.values(this.columns).some((e=>e.filterable)),!this.sortColumn)for(const t in this.columns)if(this.columns[t].direction){this.sortDirection=this.columns[t].direction,this.sortColumn=t,this._lastSelectedRowId=null,(0,p.r)(this,"sorting-changed",{column:t,direction:this.sortDirection});break}const e=(0,i.A)(this.columns);Object.values(e).forEach((e=>{delete e.title,delete e.template,delete e.extraTemplate})),this._sortColumns=e}if(e.has("filter")&&(this._debounceSearch(this.filter),this._lastSelectedRowId=null),e.has("data")){if(this._checkedRows.length){const e=new Set(this.data.map((e=>String(e[this.id])))),t=this._checkedRows.filter((t=>e.has(t)));t.length!==this._checkedRows.length&&(this._checkedRows=t,this._checkedRowsChanged())}this._checkableRowsCount=this.data.filter((e=>!1!==e.selectable)).length}!this.hasUpdated&&this.initialCollapsedGroups?(this._collapsedGroups=this.initialCollapsedGroups,this._lastSelectedRowId=null,(0,p.r)(this,"collapsed-changed",{value:this._collapsedGroups})):e.has("groupColumn")&&(this._collapsedGroups=[],this._lastSelectedRowId=null,(0,p.r)(this,"collapsed-changed",{value:this._collapsedGroups})),(e.has("data")||e.has("columns")||e.has("_filter")||e.has("sortColumn")||e.has("sortDirection"))&&this._sortFilterData(),(e.has("_filter")||e.has("sortColumn")||e.has("sortDirection"))&&(this._lastSelectedRowId=null),(e.has("selectable")||e.has("hiddenColumns"))&&(this._filteredData=[...this._filteredData])}render(){const e=this.localizeFunc||this.hass.localize,t=this._sortedColumns(this.columns,this.columnOrder);return r.qy`
      <div class="mdc-data-table">
        <slot name="header" @slotchange=${this._calcTableHeight}>
          ${this._filterable?r.qy`
                <div class="table-header">
                  <search-input
                    .hass=${this.hass}
                    @value-changed=${this._handleSearchChange}
                    .label=${this.searchLabel}
                    .noLabelFloat=${this.noLabelFloat}
                  ></search-input>
                </div>
              `:""}
        </slot>
        <div
          class="mdc-data-table__table ${(0,s.H)({"auto-height":this.autoHeight})}"
          role="table"
          aria-rowcount=${this._filteredData.length+1}
          style=${(0,d.W)({height:this.autoHeight?53*(this._filteredData.length||1)+53+"px":`calc(100% - ${this._headerHeight}px)`})}
        >
          <div
            class="mdc-data-table__header-row"
            role="row"
            aria-rowindex="1"
            @scroll=${this._scrollContent}
          >
            <slot name="header-row">
              ${this.selectable?r.qy`
                    <div
                      class="mdc-data-table__header-cell mdc-data-table__header-cell--checkbox"
                      role="columnheader"
                    >
                      <ha-checkbox
                        class="mdc-data-table__row-checkbox"
                        @change=${this._handleHeaderRowCheckboxClick}
                        .indeterminate=${this._checkedRows.length&&this._checkedRows.length!==this._checkableRowsCount}
                        .checked=${this._checkedRows.length&&this._checkedRows.length===this._checkableRowsCount}
                      >
                      </ha-checkbox>
                    </div>
                  `:""}
              ${Object.entries(t).map((([e,t])=>{if(t.hidden||(this.columnOrder&&this.columnOrder.includes(e)?this.hiddenColumns?.includes(e)??t.defaultHidden:t.defaultHidden))return r.s6;const a=e===this.sortColumn,o={"mdc-data-table__header-cell--numeric":"numeric"===t.type,"mdc-data-table__header-cell--icon":"icon"===t.type,"mdc-data-table__header-cell--icon-button":"icon-button"===t.type,"mdc-data-table__header-cell--overflow-menu":"overflow-menu"===t.type,"mdc-data-table__header-cell--overflow":"overflow"===t.type,sortable:Boolean(t.sortable),"not-sorted":Boolean(t.sortable&&!a)};return r.qy`
                  <div
                    aria-label=${(0,n.J)(t.label)}
                    class="mdc-data-table__header-cell ${(0,s.H)(o)}"
                    style=${(0,d.W)({minWidth:t.minWidth,maxWidth:t.maxWidth,flex:t.flex||1})}
                    role="columnheader"
                    aria-sort=${(0,n.J)(a?"desc"===this.sortDirection?"descending":"ascending":void 0)}
                    @click=${this._handleHeaderClick}
                    .columnId=${e}
                    title=${(0,n.J)(t.title)}
                  >
                    ${t.sortable?r.qy`
                          <ha-svg-icon
                            .path=${a&&"desc"===this.sortDirection?"M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z":"M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z"}
                          ></ha-svg-icon>
                        `:""}
                    <span>${t.title}</span>
                  </div>
                `}))}
            </slot>
          </div>
          ${this._filteredData.length?r.qy`
                <lit-virtualizer
                  scroller
                  class="mdc-data-table__content scroller ha-scrollbar"
                  @scroll=${this._saveScrollPos}
                  .items=${this._groupData(this._filteredData,e,this.appendRow,this.hasFab,this.groupColumn,this.groupOrder,this._collapsedGroups,this.sortColumn,this.sortDirection)}
                  .keyFunction=${this._keyFunction}
                  .renderItem=${(e,a)=>this._renderRow(t,this.narrow,e,a)}
                ></lit-virtualizer>
              `:r.qy`
                <div class="mdc-data-table__content">
                  <div class="mdc-data-table__row" role="row">
                    <div class="mdc-data-table__cell grows center" role="cell">
                      ${this.noDataText||e("ui.components.data-table.no-data")}
                    </div>
                  </div>
                </div>
              `}
        </div>
      </div>
    `}async _sortFilterData(){const e=(new Date).getTime(),t=e-this._lastUpdate,a=e-this._curRequest;this._curRequest=e;const o=!this._lastUpdate||t>500&&a<500;let i=this.data;if(this._filter&&(i=await this._memFilterData(this.data,this._sortColumns,this._filter.trim())),!o&&this._curRequest!==e)return;const r=this.sortColumn&&this._sortColumns[this.sortColumn]?((e,t,a,o,i)=>y().sortData(e,t,a,o,i))(i,this._sortColumns[this.sortColumn],this.sortDirection,this.sortColumn,this.hass.locale.language):i,[l]=await Promise.all([r,w.E]),s=(new Date).getTime()-e;s<100&&await new Promise((e=>{setTimeout(e,100-s)})),(o||this._curRequest===e)&&(this._lastUpdate=e,this._filteredData=l)}_handleHeaderClick(e){const t=e.currentTarget.columnId;this.columns[t].sortable&&(this.sortDirection&&this.sortColumn===t?"asc"===this.sortDirection?this.sortDirection="desc":this.sortDirection=null:this.sortDirection="asc",this.sortColumn=null===this.sortDirection?void 0:t,(0,p.r)(this,"sorting-changed",{column:t,direction:this.sortDirection}))}_handleHeaderRowCheckboxClick(e){e.target.checked?this.selectAll():(this._checkedRows=[],this._checkedRowsChanged()),this._lastSelectedRowId=null}_selectRange(e,t,a){const o=Math.min(t,a),i=Math.max(t,a),r=[];for(let l=o;l<=i;l++){const t=e[l];t&&!1!==t.selectable&&!this._checkedRows.includes(t[this.id])&&r.push(t[this.id])}return r}_setTitle(e){const t=e.currentTarget;t.scrollWidth>t.offsetWidth&&t.setAttribute("title",t.innerText)}_checkedRowsChanged(){this._filteredData.length&&(this._filteredData=[...this._filteredData]),(0,p.r)(this,"selection-changed",{value:this._checkedRows})}_handleSearchChange(e){this.filter||(this._lastSelectedRowId=null,this._debounceSearch(e.detail.value))}async _calcTableHeight(){this.autoHeight||(await this.updateComplete,this._headerHeight=this._header.clientHeight)}_saveScrollPos(e){this._savedScrollPos=e.target.scrollTop,this.renderRoot.querySelector(".mdc-data-table__header-row").scrollLeft=e.target.scrollLeft}_scrollContent(e){this.renderRoot.querySelector("lit-virtualizer").scrollLeft=e.target.scrollLeft}expandAllGroups(){this._collapsedGroups=[],this._lastSelectedRowId=null,(0,p.r)(this,"collapsed-changed",{value:this._collapsedGroups})}collapseAllGroups(){if(!this.groupColumn||!this.data.some((e=>e[this.groupColumn])))return;const e=m(this.data,(e=>e[this.groupColumn]));e.undefined&&(e[x]=e.undefined,delete e.undefined),this._collapsedGroups=Object.keys(e),this._lastSelectedRowId=null,(0,p.r)(this,"collapsed-changed",{value:this._collapsedGroups})}static get styles(){return[b.dp,r.AH`
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
      `]}constructor(...e){super(...e),this.narrow=!1,this.columns={},this.data=[],this.selectable=!1,this.clickable=!1,this.hasFab=!1,this.autoHeight=!1,this.id="id",this.noLabelFloat=!1,this.filter="",this.sortDirection=null,this._filterable=!1,this._filter="",this._filteredData=[],this._headerHeight=0,this._collapsedGroups=[],this._lastSelectedRowId=null,this._checkedRows=[],this._sortColumns={},this._curRequest=0,this._lastUpdate=0,this._debounceSearch=(0,u.s)((e=>{this._filter=e}),100,!1),this._sortedColumns=(0,c.A)(((e,t)=>t&&t.length?Object.keys(e).sort(((e,a)=>{const o=t.indexOf(e),i=t.indexOf(a);if(o!==i){if(-1===o)return 1;if(-1===i)return-1}return o-i})).reduce(((t,a)=>(t[a]=e[a],t)),{}):e)),this._keyFunction=e=>e?.[this.id]||e,this._renderRow=(e,t,a,o)=>a?a.append?r.qy`<div class="mdc-data-table__row">${a.content}</div>`:a.empty?r.qy`<div class="mdc-data-table__row empty-row"></div>`:r.qy`
      <div
        aria-rowindex=${o+2}
        role="row"
        .rowId=${a[this.id]}
        @click=${this._handleRowClick}
        class="mdc-data-table__row ${(0,s.H)({"mdc-data-table__row--selected":this._checkedRows.includes(String(a[this.id])),clickable:this.clickable})}"
        aria-selected=${(0,n.J)(!!this._checkedRows.includes(String(a[this.id]))||void 0)}
        .selectable=${!1!==a.selectable}
      >
        ${this.selectable?r.qy`
              <div
                class="mdc-data-table__cell mdc-data-table__cell--checkbox"
                role="cell"
              >
                <ha-checkbox
                  class="mdc-data-table__row-checkbox"
                  @click=${this._handleRowCheckboxClicked}
                  .rowId=${a[this.id]}
                  .disabled=${!1===a.selectable}
                  .checked=${this._checkedRows.includes(String(a[this.id]))}
                >
                </ha-checkbox>
              </div>
            `:""}
        ${Object.entries(e).map((([o,i])=>t&&!i.main&&!i.showNarrow||i.hidden||(this.columnOrder&&this.columnOrder.includes(o)?this.hiddenColumns?.includes(o)??i.defaultHidden:i.defaultHidden)?r.s6:r.qy`
            <div
              @mouseover=${this._setTitle}
              @focus=${this._setTitle}
              role=${i.main?"rowheader":"cell"}
              class="mdc-data-table__cell ${(0,s.H)({"mdc-data-table__cell--flex":"flex"===i.type,"mdc-data-table__cell--numeric":"numeric"===i.type,"mdc-data-table__cell--icon":"icon"===i.type,"mdc-data-table__cell--icon-button":"icon-button"===i.type,"mdc-data-table__cell--overflow-menu":"overflow-menu"===i.type,"mdc-data-table__cell--overflow":"overflow"===i.type,forceLTR:Boolean(i.forceLTR)})}"
              style=${(0,d.W)({minWidth:i.minWidth,maxWidth:i.maxWidth,flex:i.flex||1})}
            >
              ${i.template?i.template(a):t&&i.main?r.qy`<div class="primary">${a[o]}</div>
                      <div class="secondary">
                        ${Object.entries(e).filter((([e,t])=>!(t.hidden||t.main||t.showNarrow||(this.columnOrder&&this.columnOrder.includes(e)?this.hiddenColumns?.includes(e)??t.defaultHidden:t.defaultHidden)))).map((([e,t],o)=>r.qy`${0!==o?" · ":r.s6}${t.template?t.template(a):a[e]}`))}
                      </div>
                      ${i.extraTemplate?i.extraTemplate(a):r.s6}`:r.qy`${a[o]}${i.extraTemplate?i.extraTemplate(a):r.s6}`}
            </div>
          `))}
      </div>
    `:r.s6,this._groupData=(0,c.A)(((e,t,a,o,i,l,s,n,d)=>{if(a||o||i){let c=[...e];if(i){const e=n===i,a=m(c,(e=>e[i]));a.undefined&&(a[x]=a.undefined,delete a.undefined);const o=Object.keys(a).sort(((t,a)=>{if(!l&&e){const e=(0,_.xL)(t,a,this.hass.locale.language);return"asc"===d?e:-1*e}const o=l?.indexOf(t)??-1,i=l?.indexOf(a)??-1;return o!==i?-1===o?1:-1===i?-1:o-i:(0,_.xL)(["","-","—"].includes(t)?"zzz":t,["","-","—"].includes(a)?"zzz":a,this.hass.locale.language)})).reduce(((e,t)=>{const o=[t,a[t]];return e.push(o),e}),[]),h=[];o.forEach((([e,a])=>{const o=s.includes(e);h.push({append:!0,selectable:!1,content:r.qy`<div
                class="mdc-data-table__cell group-header"
                role="cell"
                .group=${e}
                @click=${this._collapseGroup}
              >
                <ha-icon-button
                  .path=${"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z"}
                  .label=${this.hass.localize("ui.components.data-table."+(o?"expand":"collapse"))}
                  class=${o?"collapsed":""}
                >
                </ha-icon-button>
                ${e===x?t("ui.components.data-table.ungrouped"):e||""}
              </div>`}),s.includes(e)||h.push(...a)})),c=h}return a&&c.push({append:!0,selectable:!1,content:a}),o&&c.push({empty:!0}),c}return e})),this._memFilterData=(0,c.A)(((e,t,a)=>((e,t,a)=>y().filterData(e,t,a))(e,t,a))),this._handleRowCheckboxClicked=e=>{const t=e.currentTarget,a=t.rowId,o=this._groupData(this._filteredData,this.localizeFunc||this.hass.localize,this.appendRow,this.hasFab,this.groupColumn,this.groupOrder,this._collapsedGroups,this.sortColumn,this.sortDirection);if(!1===o.find((e=>e[this.id]===a))?.selectable)return;const i=o.findIndex((e=>e[this.id]===a));if(e instanceof MouseEvent&&e.shiftKey&&null!==this._lastSelectedRowId){const e=o.findIndex((e=>e[this.id]===this._lastSelectedRowId));e>-1&&i>-1&&(this._checkedRows=[...this._checkedRows,...this._selectRange(o,e,i)])}else t.checked?this._checkedRows=this._checkedRows.filter((e=>e!==a)):this._checkedRows.includes(a)||(this._checkedRows=[...this._checkedRows,a]);i>-1&&(this._lastSelectedRowId=a),this._checkedRowsChanged()},this._handleRowClick=e=>{if(e.composedPath().find((e=>["ha-checkbox","ha-button","ha-button","ha-icon-button","ha-assist-chip"].includes(e.localName))))return;const t=e.currentTarget.rowId;(0,p.r)(this,"row-click",{id:t},{bubbles:!1})},this._collapseGroup=e=>{const t=e.currentTarget.group;this._collapsedGroups.includes(t)?this._collapsedGroups=this._collapsedGroups.filter((e=>e!==t)):this._collapsedGroups=[...this._collapsedGroups,t],this._lastSelectedRowId=null,(0,p.r)(this,"collapsed-changed",{value:this._collapsedGroups})}}}(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"localizeFunc",void 0),(0,o.__decorate)([(0,l.MZ)({type:Boolean})],k.prototype,"narrow",void 0),(0,o.__decorate)([(0,l.MZ)({type:Object})],k.prototype,"columns",void 0),(0,o.__decorate)([(0,l.MZ)({type:Array})],k.prototype,"data",void 0),(0,o.__decorate)([(0,l.MZ)({type:Boolean})],k.prototype,"selectable",void 0),(0,o.__decorate)([(0,l.MZ)({type:Boolean})],k.prototype,"clickable",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:"has-fab",type:Boolean})],k.prototype,"hasFab",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"appendRow",void 0),(0,o.__decorate)([(0,l.MZ)({type:Boolean,attribute:"auto-height"})],k.prototype,"autoHeight",void 0),(0,o.__decorate)([(0,l.MZ)({type:String})],k.prototype,"id",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1,type:String})],k.prototype,"noDataText",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1,type:String})],k.prototype,"searchLabel",void 0),(0,o.__decorate)([(0,l.MZ)({type:Boolean,attribute:"no-label-float"})],k.prototype,"noLabelFloat",void 0),(0,o.__decorate)([(0,l.MZ)({type:String})],k.prototype,"filter",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"groupColumn",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"groupOrder",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"sortColumn",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"sortDirection",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"initialCollapsedGroups",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"hiddenColumns",void 0),(0,o.__decorate)([(0,l.MZ)({attribute:!1})],k.prototype,"columnOrder",void 0),(0,o.__decorate)([(0,l.wk)()],k.prototype,"_filterable",void 0),(0,o.__decorate)([(0,l.wk)()],k.prototype,"_filter",void 0),(0,o.__decorate)([(0,l.wk)()],k.prototype,"_filteredData",void 0),(0,o.__decorate)([(0,l.wk)()],k.prototype,"_headerHeight",void 0),(0,o.__decorate)([(0,l.P)("slot[name='header']")],k.prototype,"_header",void 0),(0,o.__decorate)([(0,l.wk)()],k.prototype,"_collapsedGroups",void 0),(0,o.__decorate)([(0,l.wk)()],k.prototype,"_lastSelectedRowId",void 0),(0,o.__decorate)([(0,h.a)(".scroller")],k.prototype,"_savedScrollPos",void 0),(0,o.__decorate)([(0,l.Ls)({passive:!0})],k.prototype,"_saveScrollPos",null),(0,o.__decorate)([(0,l.Ls)({passive:!0})],k.prototype,"_scrollContent",null),k=(0,o.__decorate)([(0,l.EM)("ha-data-table")],k)},70524:function(e,t,a){var o=a(62826),i=a(69162),r=a(47191),l=a(96196),s=a(77845);class n extends i.L{}n.styles=[r.R,l.AH`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `],n=(0,o.__decorate)([(0,s.EM)("ha-checkbox")],n)},63419:function(e,t,a){var o=a(62826),i=a(96196),r=a(77845),l=a(92542),s=(a(41742),a(26139)),n=a(8889),d=a(63374);class c extends s.W1{connectedCallback(){super.connectedCallback(),this.addEventListener("close-menu",this._handleCloseMenu)}_handleCloseMenu(e){e.detail.reason.kind===d.fi.KEYDOWN&&e.detail.reason.key===d.NV.ESCAPE||e.detail.initiator.clickAction?.(e.detail.initiator)}}c.styles=[n.R,i.AH`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `],c=(0,o.__decorate)([(0,r.EM)("ha-md-menu")],c);class h extends i.WF{get items(){return this._menu.items}focus(){this._menu.open?this._menu.focus():this._triggerButton?.focus()}render(){return i.qy`
      <div @click=${this._handleClick}>
        <slot name="trigger" @slotchange=${this._setTriggerAria}></slot>
      </div>
      <ha-md-menu
        .quick=${this.quick}
        .positioning=${this.positioning}
        .hasOverflow=${this.hasOverflow}
        .anchorCorner=${this.anchorCorner}
        .menuCorner=${this.menuCorner}
        @opening=${this._handleOpening}
        @closing=${this._handleClosing}
      >
        <slot></slot>
      </ha-md-menu>
    `}_handleOpening(){(0,l.r)(this,"opening",void 0,{composed:!1})}_handleClosing(){(0,l.r)(this,"closing",void 0,{composed:!1})}_handleClick(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}get _triggerButton(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}_setTriggerAria(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}constructor(...e){super(...e),this.disabled=!1,this.anchorCorner="end-start",this.menuCorner="start-start",this.hasOverflow=!1,this.quick=!1}}h.styles=i.AH`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `,(0,o.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)()],h.prototype,"positioning",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"anchor-corner"})],h.prototype,"anchorCorner",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"menu-corner"})],h.prototype,"menuCorner",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,attribute:"has-overflow"})],h.prototype,"hasOverflow",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"quick",void 0),(0,o.__decorate)([(0,r.P)("ha-md-menu",!0)],h.prototype,"_menu",void 0),h=(0,o.__decorate)([(0,r.EM)("ha-md-button-menu")],h)},32072:function(e,t,a){var o=a(62826),i=a(10414),r=a(18989),l=a(96196),s=a(77845);class n extends i.c{}n.styles=[r.R,l.AH`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `],n=(0,o.__decorate)([(0,s.EM)("ha-md-divider")],n)},99892:function(e,t,a){var o=a(62826),i=a(54407),r=a(28522),l=a(96196),s=a(77845);class n extends i.K{}n.styles=[r.R,l.AH`
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
    `],(0,o.__decorate)([(0,s.MZ)({attribute:!1})],n.prototype,"clickAction",void 0),n=(0,o.__decorate)([(0,s.EM)("ha-md-menu-item")],n)},95591:function(e,t,a){var o=a(62826),i=a(76482),r=a(91382),l=a(96245),s=a(96196),n=a(77845);class d extends r.n{attach(e){super.attach(e),this.attachableTouchController.attach(e)}disconnectedCallback(){super.disconnectedCallback(),this.hovered=!1,this.pressed=!1}detach(){super.detach(),this.attachableTouchController.detach()}_onTouchControlChange(e,t){e?.removeEventListener("touchend",this._handleTouchEnd),t?.addEventListener("touchend",this._handleTouchEnd)}constructor(...e){super(...e),this.attachableTouchController=new i.i(this,this._onTouchControlChange.bind(this)),this._handleTouchEnd=()=>{this.disabled||super.endPressAnimation()}}}d.styles=[l.R,s.AH`
      :host {
        --md-ripple-hover-opacity: var(--ha-ripple-hover-opacity, 0.08);
        --md-ripple-pressed-opacity: var(--ha-ripple-pressed-opacity, 0.12);
        --md-ripple-hover-color: var(
          --ha-ripple-hover-color,
          var(--ha-ripple-color, var(--secondary-text-color))
        );
        --md-ripple-pressed-color: var(
          --ha-ripple-pressed-color,
          var(--ha-ripple-color, var(--secondary-text-color))
        );
      }
    `],d=(0,o.__decorate)([(0,n.EM)("ha-ripple")],d)},89600:function(e,t,a){a.a(e,(async function(e,t){try{var o=a(62826),i=a(55262),r=a(96196),l=a(77845),s=e([i]);i=(s.then?(await s)():s)[0];class n extends i.A{updated(e){if(super.updated(e),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-spinner-size","16px");break;case"small":this.style.setProperty("--ha-spinner-size","28px");break;case"medium":this.style.setProperty("--ha-spinner-size","48px");break;case"large":this.style.setProperty("--ha-spinner-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}static get styles(){return[i.A.styles,r.AH`
        :host {
          --indicator-color: var(
            --ha-spinner-indicator-color,
            var(--primary-color)
          );
          --track-color: var(--ha-spinner-divider-color, var(--divider-color));
          --track-width: 4px;
          --speed: 3.5s;
          font-size: var(--ha-spinner-size, 48px);
        }
      `]}}(0,o.__decorate)([(0,l.MZ)()],n.prototype,"size",void 0),n=(0,o.__decorate)([(0,l.EM)("ha-spinner")],n),t()}catch(n){t(n)}}))},17262:function(e,t,a){var o=a(62826),i=a(96196),r=a(77845),l=(a(60733),a(60961),a(78740),a(92542));class s extends i.WF{focus(){this._input?.focus()}render(){return i.qy`
      <ha-textfield
        .autofocus=${this.autofocus}
        autocomplete="off"
        .label=${this.label||this.hass.localize("ui.common.search")}
        .value=${this.filter||""}
        icon
        .iconTrailing=${this.filter||this.suffix}
        @input=${this._filterInputChanged}
      >
        <slot name="prefix" slot="leadingIcon">
          <ha-svg-icon
            tabindex="-1"
            class="prefix"
            .path=${"M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"}
          ></ha-svg-icon>
        </slot>
        <div class="trailing" slot="trailingIcon">
          ${this.filter&&i.qy`
            <ha-icon-button
              @click=${this._clearSearch}
              .label=${this.hass.localize("ui.common.clear")}
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              class="clear-button"
            ></ha-icon-button>
          `}
          <slot name="suffix"></slot>
        </div>
      </ha-textfield>
    `}async _filterChanged(e){(0,l.r)(this,"value-changed",{value:String(e)})}async _filterInputChanged(e){this._filterChanged(e.target.value)}async _clearSearch(){this._filterChanged("")}constructor(...e){super(...e),this.suffix=!1,this.autofocus=!1}}s.styles=i.AH`
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
  `,(0,o.__decorate)([(0,r.MZ)({attribute:!1})],s.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)()],s.prototype,"filter",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],s.prototype,"suffix",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],s.prototype,"autofocus",void 0),(0,o.__decorate)([(0,r.MZ)({type:String})],s.prototype,"label",void 0),(0,o.__decorate)([(0,r.P)("ha-textfield",!0)],s.prototype,"_input",void 0),s=(0,o.__decorate)([(0,r.EM)("search-input")],s)},70076:function(e,t,a){a.d(t,{Hg:()=>i,Wj:()=>r,jG:()=>o,ow:()=>l,zt:()=>s});var o=function(e){return e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.quote_decimal="quote_decimal",e.space_comma="space_comma",e.none="none",e}({}),i=function(e){return e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24",e}({}),r=function(e){return e.local="local",e.server="server",e}({}),l=function(e){return e.language="language",e.system="system",e.DMY="DMY",e.MDY="MDY",e.YMD="YMD",e}({}),s=function(e){return e.language="language",e.monday="monday",e.tuesday="tuesday",e.wednesday="wednesday",e.thursday="thursday",e.friday="friday",e.saturday="saturday",e.sunday="sunday",e}({})},54393:function(e,t,a){a.a(e,(async function(e,o){try{a.r(t);var i=a(62826),r=a(96196),l=a(77845),s=a(5871),n=a(89600),d=(a(371),a(45397),a(39396)),c=e([n]);n=(c.then?(await c)():c)[0];class h extends r.WF{render(){return r.qy`
      ${this.noToolbar?"":r.qy`<div class="toolbar">
            ${this.rootnav||history.state?.root?r.qy`
                  <ha-menu-button
                    .hass=${this.hass}
                    .narrow=${this.narrow}
                  ></ha-menu-button>
                `:r.qy`
                  <ha-icon-button-arrow-prev
                    .hass=${this.hass}
                    @click=${this._handleBack}
                  ></ha-icon-button-arrow-prev>
                `}
          </div>`}
      <div class="content">
        <ha-spinner></ha-spinner>
        ${this.message?r.qy`<div id="loading-text">${this.message}</div>`:r.s6}
      </div>
    `}_handleBack(){(0,s.O)()}static get styles(){return[d.RF,r.AH`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }
        .toolbar {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          padding: 8px 12px;
          pointer-events: none;
          background-color: var(--app-header-background-color);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
        }
        @media (max-width: 599px) {
          .toolbar {
            padding: 4px;
          }
        }
        ha-menu-button,
        ha-icon-button-arrow-prev {
          pointer-events: auto;
        }
        .content {
          height: calc(100% - var(--header-height));
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        #loading-text {
          max-width: 350px;
          margin-top: 16px;
        }
      `]}constructor(...e){super(...e),this.noToolbar=!1,this.rootnav=!1,this.narrow=!1}}(0,i.__decorate)([(0,l.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean,attribute:"no-toolbar"})],h.prototype,"noToolbar",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],h.prototype,"rootnav",void 0),(0,i.__decorate)([(0,l.MZ)({type:Boolean})],h.prototype,"narrow",void 0),(0,i.__decorate)([(0,l.MZ)()],h.prototype,"message",void 0),h=(0,i.__decorate)([(0,l.EM)("hass-loading-screen")],h),o()}catch(h){o(h)}}))},84884:function(e,t,a){var o=a(62826),i=a(96196),r=a(77845),l=a(94333),s=a(22786),n=a(55376),d=a(92209);const c=(e,t)=>!t.component||(0,n.e)(t.component).some((t=>(0,d.x)(e,t))),h=(e,t)=>!t.not_component||!(0,n.e)(t.not_component).some((t=>(0,d.x)(e,t))),p=e=>e.core,_=(e,t)=>(e=>e.advancedOnly)(t)&&!(e=>e.userData?.showAdvanced)(e);var u=a(5871),m=a(39501),b=(a(371),a(45397),a(60961),a(32288));a(95591);class v extends i.WF{render(){return i.qy`
      <div
        tabindex="0"
        role="tab"
        aria-selected=${this.active}
        aria-label=${(0,b.J)(this.name)}
        @keydown=${this._handleKeyDown}
      >
        ${this.narrow?i.qy`<slot name="icon"></slot>`:""}
        <span class="name">${this.name}</span>
        <ha-ripple></ha-ripple>
      </div>
    `}_handleKeyDown(e){"Enter"===e.key&&e.target.click()}constructor(...e){super(...e),this.active=!1,this.narrow=!1}}v.styles=i.AH`
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
  `,(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],v.prototype,"active",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],v.prototype,"narrow",void 0),(0,o.__decorate)([(0,r.MZ)()],v.prototype,"name",void 0),v=(0,o.__decorate)([(0,r.EM)("ha-tab")],v);var f=a(39396);class g extends i.WF{willUpdate(e){e.has("route")&&(this._activeTab=this.tabs.find((e=>`${this.route.prefix}${this.route.path}`.includes(e.path)))),super.willUpdate(e)}render(){const e=this._getTabs(this.tabs,this._activeTab,this.hass.config.components,this.hass.language,this.hass.userData,this.narrow,this.localizeFunc||this.hass.localize),t=e.length>1;return i.qy`
      <div class="toolbar">
        <slot name="toolbar">
          <div class="toolbar-content">
            ${this.mainPage||!this.backPath&&history.state?.root?i.qy`
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
            ${this.narrow||!t?i.qy`<div class="main-title">
                  <slot name="header">${t?"":e[0]}</slot>
                </div>`:""}
            ${t&&!this.narrow?i.qy`<div id="tabbar">${e}</div>`:""}
            <div id="toolbar-icon">
              <slot name="toolbar-icon"></slot>
            </div>
          </div>
        </slot>
        ${t&&this.narrow?i.qy`<div id="tabbar" class="bottom-bar">${e}</div>`:""}
      </div>
      <div
        class=${(0,l.H)({container:!0,tabs:t&&this.narrow})}
      >
        ${this.pane?i.qy`<div class="pane">
              <div class="shadow-container"></div>
              <div class="ha-scrollbar">
                <slot name="pane"></slot>
              </div>
            </div>`:i.s6}
        <div
          class="content ha-scrollbar ${(0,l.H)({tabs:t})}"
          @scroll=${this._saveScrollPos}
        >
          <slot></slot>
          ${this.hasFab?i.qy`<div class="fab-bottom-space"></div>`:i.s6}
        </div>
      </div>
      <div id="fab" class=${(0,l.H)({tabs:t})}>
        <slot name="fab"></slot>
      </div>
    `}_saveScrollPos(e){this._savedScrollPos=e.target.scrollTop}_backTapped(){this.backCallback?this.backCallback():(0,u.O)()}static get styles(){return[f.dp,i.AH`
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
      `]}constructor(...e){super(...e),this.supervisor=!1,this.mainPage=!1,this.narrow=!1,this.isWide=!1,this.pane=!1,this.hasFab=!1,this._getTabs=(0,s.A)(((e,t,a,o,r,l,s)=>{const n=e.filter((e=>((e,t)=>(p(t)||c(e,t))&&!_(e,t)&&h(e,t))(this.hass,e)));if(n.length<2){if(1===n.length){const e=n[0];return[e.translationKey?s(e.translationKey):e.name]}return[""]}return n.map((e=>i.qy`
          <a href=${e.path}>
            <ha-tab
              .hass=${this.hass}
              .active=${e.path===t?.path}
              .narrow=${this.narrow}
              .name=${e.translationKey?s(e.translationKey):e.name}
            >
              ${e.iconPath?i.qy`<ha-svg-icon
                    slot="icon"
                    .path=${e.iconPath}
                  ></ha-svg-icon>`:""}
            </ha-tab>
          </a>
        `))}))}}(0,o.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],g.prototype,"supervisor",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"localizeFunc",void 0),(0,o.__decorate)([(0,r.MZ)({type:String,attribute:"back-path"})],g.prototype,"backPath",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"backCallback",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,attribute:"main-page"})],g.prototype,"mainPage",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"route",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],g.prototype,"tabs",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],g.prototype,"narrow",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"is-wide"})],g.prototype,"isWide",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],g.prototype,"pane",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,attribute:"has-fab"})],g.prototype,"hasFab",void 0),(0,o.__decorate)([(0,r.wk)()],g.prototype,"_activeTab",void 0),(0,o.__decorate)([(0,m.a)(".content")],g.prototype,"_savedScrollPos",void 0),(0,o.__decorate)([(0,r.Ls)({passive:!0})],g.prototype,"_saveScrollPos",null),g=(0,o.__decorate)([(0,r.EM)("hass-tabs-subpage")],g)},84183:function(e,t,a){a.d(t,{i:()=>o});const o=async()=>{await a.e("2564").then(a.bind(a,42735))}}};
//# sourceMappingURL=1804.da3c15be656396d5.js.map