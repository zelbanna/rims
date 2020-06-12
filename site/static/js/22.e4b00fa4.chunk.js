(this.webpackJsonprims=this.webpackJsonprims||[]).push([[22],{58:function(t,e,n){"use strict";n.r(e),n.d(e,"Main",(function(){return y})),n.d(e,"Report",(function(){return k})),n.d(e,"FileList",(function(){return b}));var a=n(14),r=n(3),i=n(4),o=n(5),s=n(6),c=n(0),l=n.n(c),u=n(12),p=n(13),m=n(19),v=n(16),f=n(15),h=n(1),d=n.n(h),y=function(t){Object(s.a)(Main,t);var e=Object(o.a)(Main);function Main(t){var n;return Object(r.a)(this,Main),(n=e.call(this,t)).compileNavItems=function(){var t="master"===n.context.settings.node,e="admin"===n.context.settings.class,a=t&&e;n.context.loadNavigation(l.a.createElement(v.NavBar,{key:"system_navbar"},a&&l.a.createElement(v.NavButton,{key:"sys_nav_node",title:"Nodes",onClick:function onClick(){return n.changeImport("node","List")}}),a&&l.a.createElement(v.NavButton,{key:"sys_nav_srv",title:"Servers",onClick:function onClick(){return n.changeImport("server","List")}}),t&&l.a.createElement(v.NavButton,{key:"sys_nav_erd",title:"ERD",onClick:function onClick(){return window.open("erd.pdf","_blank")}}),a&&l.a.createElement(v.NavButton,{key:"sys_nav_user",title:"Users",onClick:function onClick(){return n.changeImport("user","List")}}),t&&l.a.createElement(v.NavButton,{key:"sys_nav_ctrl",title:"Controls",onClick:function onClick(){return n.changeContent(l.a.createElement(g,{key:"system_controls"}))}}),l.a.createElement(v.NavDropDown,{key:"sys_nav_reports",title:"Reports"},l.a.createElement(v.NavDropButton,{key:"sys_nav_sys",title:"System",onClick:function onClick(){return n.changeContent(l.a.createElement(k,{key:"system_report"}))}}),e&&l.a.createElement(v.NavDropButton,{key:"sys_nav_act",title:"Activities",onClick:function onClick(){return n.changeImport("activity","Report")}}),t&&l.a.createElement(v.NavDropButton,{key:"sys_nav_resv",title:"Reservations",onClick:function onClick(){return n.changeImport("reservation","Report")}}),t&&l.a.createElement(v.NavDropButton,{key:"sys_nav_dev",title:"Devices",onClick:function onClick(){return n.changeImport("device","Report")}}),t&&l.a.createElement(v.NavDropButton,{key:"sys_nav_inv",title:"Inventory",onClick:function onClick(){return n.changeImport("inventory","Report")}})),l.a.createElement(v.NavButton,{key:"sys_nav_logs",title:"Logs",onClick:function onClick(){return n.changeImport("node","LogShow",{node:n.context.settings.node})}}),e&&l.a.createElement(v.NavButton,{key:"sys_nav_rest",title:"REST",onClick:function onClick(){return n.changeContent(l.a.createElement(_,{key:"rest_list"}))}}),e&&n.state.services.length>0&&l.a.createElement(v.NavDropDown,{key:"sys_nav_svcs",title:"Services"},n.state.services.map((function(t,e){return l.a.createElement(v.NavDropButton,{key:"sys_nav_svcs_"+e,title:t.name,onClick:function onClick(){return n.changeContent(l.a.createElement(O,Object.assign({key:t.name},t)))}})}))),l.a.createElement(v.NavReload,{key:"sys_nav_reload",onClick:function onClick(){return n.setState({content:null})}}),n.state.navinfo.map((function(t,e){return l.a.createElement(v.NavInfo,{key:"sys_nav_ni_"+e,title:t})}))))},n.changeContent=function(t){return n.setState({content:t})},n.state={navinfo:[],navitems:[],logs:[],services:[]},n}return Object(i.a)(Main,[{key:"componentDidMount",value:function componentDidMount(){var t=this;Object(u.d)("api/system/inventory",{user_id:this.context.settings.id}).then((function(e){Object.assign(t.state,e),t.compileNavItems()}))}},{key:"componentDidUpdate",value:function componentDidUpdate(t){t!==this.props&&this.compileNavItems()}},{key:"changeImport",value:function changeImport(t,e,a){var r=this;n(25)("./"+t+".jsx").then((function(n){var i=n[e];r.setState({content:l.a.createElement(i,Object.assign({key:t+"_"+e},a))})}))}},{key:"render",value:function render(){return l.a.createElement(c.Fragment,null,this.state.content)}}]),Main}(c.Component);y.contextType=p.RimsContext;var k=function(t){Object(s.a)(Report,t);var e=Object(o.a)(Report);function Report(t){var n;return Object(r.a)(this,Report),(n=e.call(this,t)).listItem=function(t){return[t.info,t.value]},n.state={},n}return Object(i.a)(Report,[{key:"componentDidMount",value:function componentDidMount(){var t=this;Object(u.d)("api/system/report").then((function(e){return t.setState({data:Object.keys(e).sort((function(t,e){return t.localeCompare(e)})).map((function(t){return{info:t,value:e[t]}}))})}))}},{key:"render",value:function render(){return l.a.createElement(p.ContentReport,{key:"sys_cr",header:"System Report",thead:["Key","Value"],trows:this.state.data,listItem:this.listItem})}}]),Report}(c.Component),_=function(t){Object(s.a)(RestList,t);var e=Object(o.a)(RestList);function RestList(t){var n;return Object(r.a)(this,RestList),(n=e.call(this,t)).listItem=function(t){return[t.api,l.a.createElement(m.HrefButton,{key:"rest_"+t.api,text:t.function,onClick:function onClick(){n.changeContent(l.a.createElement(C,Object.assign({key:"rest_info_".concat(t.api,"_").concat(t.function)},t)))}})]},n.changeContent=function(t){return n.setState({content:t})},n.state={},n}return Object(i.a)(RestList,[{key:"componentDidMount",value:function componentDidMount(){var t=this;Object(u.d)("api/system/rest_explore").then((function(e){var n=[];e.data.forEach((function(t){return t.functions.forEach((function(e){return n.push({api:t.api,function:e})}))})),t.setState({data:n})}))}},{key:"render",value:function render(){return l.a.createElement(c.Fragment,null,l.a.createElement(p.ContentList,{key:"rest_tp_cl",header:"REST API",thead:["API","Function"],trows:this.state.data,listItem:this.listItem}),l.a.createElement(p.ContentData,{key:"rest_tp_cd"},this.state.content))}}]),RestList}(c.Component),C=function(t){Object(s.a)(RestInfo,t);var e=Object(o.a)(RestInfo);function RestInfo(t){var n;return Object(r.a)(this,RestInfo),(n=e.call(this,t)).state={},n}return Object(i.a)(RestInfo,[{key:"componentDidMount",value:function componentDidMount(){var t=this;Object(u.d)("api/system/rest_information",{api:this.props.api,function:this.props.function}).then((function(e){return t.setState(e)}))}},{key:"render",value:function render(){return this.state.module&&this.state.information?l.a.createElement(p.Article,{key:"ri_art",header:this.props.api},this.state.module.join("\n"),l.a.createElement(p.Title,{text:this.props.function}),this.state.information.join("\n")):l.a.createElement(p.Spinner,null)}}]),RestInfo}(c.Component),E=function(t){Object(s.a)(RestExecute,t);var e=Object(o.a)(RestExecute);function RestExecute(){return Object(r.a)(this,RestExecute),e.apply(this,arguments)}return Object(i.a)(RestExecute,[{key:"componentDidMount",value:function componentDidMount(){var t=this;Object(u.d)("api/"+this.props.api,this.props.args).then((function(e){return t.setState(e)}))}},{key:"render",value:function render(){return this.state?l.a.createElement(p.CodeArticle,{key:"re_code",header:this.props.text},JSON.stringify(this.state,null,2)):l.a.createElement(p.Spinner,null)}}]),RestExecute}(c.Component),g=function(t){Object(s.a)(Controls,t);var e=Object(o.a)(Controls);function Controls(t){var n;return Object(r.a)(this,Controls),(n=e.call(this,t)).changeContent=function(t){return n.setState({content:t})},n.listItem=function(t){return[l.a.createElement(m.HrefButton,{key:"ctrl_"+t.api,text:t.text,onClick:function onClick(){n.changeContent(l.a.createElement(E,Object.assign({key:"rest_"+t.api},t)))}})]},n.state={data:[{api:"ipam/address_events",text:"IPAM clear all status logs",args:{op:"clear"}},{api:"device/log_clear",text:"Device clear all status logs"},{api:"ipam/check",text:"IPAM status check"},{api:"interface/check",text:"Interface status check"},{api:"device/system_info_discover",text:"Discover device system information (sysmac etc)"},{api:"device/model_sync",text:"Sync device model mapping"},{api:"device/vm_mapping",text:"VM UUID mapping"},{api:"master/oui_fetch",text:"Sync OUI database"},{api:"reservation/expiration_status",text:"Check reservation status"},{api:"fdb/check",text:"Update FDB"}]},n}return Object(i.a)(Controls,[{key:"render",value:function render(){return l.a.createElement(c.Fragment,null,l.a.createElement(p.ContentList,{key:"ctl_cl",header:"",thead:["API"],trows:this.state.data,listItem:this.listItem}),l.a.createElement(p.ContentData,{key:"ctl_cd"},this.state.content))}}]),Controls}(c.Component),b=function(t){Object(s.a)(FileList,t);var e=Object(o.a)(FileList);function FileList(t){var n;return Object(r.a)(this,FileList),(n=e.call(this,t)).loadFiles=function(){var t={};t=n.props.hasOwnProperty("directory")?{mode:"directory",args:{directory:n.props.directory},files:void 0}:n.props.hasOwnProperty("fullpath")?{mode:"fullpath",args:{fullpath:n.props.fullpath},files:void 0}:{mode:"images",args:{},files:void 0},Object(u.d)("api/system/file_list",t.args).then((function(e){"OK"===e.status?n.setState(Object(a.a)({mode:t.mode},e)):(window.alert("Error retrieving files:"+e.info),n.setState({files:[]}))}))},n.listItem=function(t){return"images"===n.state.mode?".png"===t.substr(t.length-4)?[t,l.a.createElement("img",{src:n.state.path+"/"+t,alt:n.state.path+"/"+t})]:[]:[l.a.createElement(c.Fragment,null,n.state.path+"/",l.a.createElement("a",{className:d.a.href,href:n.state.path+"/"+t,target:"_blank",rel:"noopener noreferrer"},t))]},n.state={},n}return Object(i.a)(FileList,[{key:"componentDidUpdate",value:function componentDidUpdate(t){t!==this.props&&this.loadFiles()}},{key:"componentDidMount",value:function componentDidMount(){this.loadFiles()}},{key:"render",value:function render(){return this.state.files?l.a.createElement(p.ContentReport,{header:this.state.mode,thead:[],trows:this.state.files,listItem:this.listItem}):l.a.createElement(p.Spinner,null)}}]),FileList}(c.Component),O=function(t){Object(s.a)(ServiceInfo,t);var e=Object(o.a)(ServiceInfo);function ServiceInfo(t){var n;return Object(r.a)(this,ServiceInfo),(n=e.call(this,t)).state={state:"inactive"},n}return Object(i.a)(ServiceInfo,[{key:"componentDidMount",value:function componentDidMount(){this.updateService({})}},{key:"updateService",value:function updateService(t){var e=this;this.setState({spinner:l.a.createElement(p.Spinner,null)}),Object(u.d)("api/system/service_info",Object(a.a)({service:this.props.service},t)).then((function(t){"OK"===t.status?e.setState(Object(a.a)({},t,{spinner:null})):window.alert("Error retrieving service state:"+t.info)}))}},{key:"render",value:function render(){var t=this,e="inactive"===this.state.state,n=e?m.StartButton:m.StopButton;return l.a.createElement(p.LineArticle,{key:"svc_art"},l.a.createElement(f.TextLine,{key:"service_line",id:"service",label:this.props.name,text:this.state.state+" ("+this.state.extra+")"}),l.a.createElement(n,{key:"state_change",onClick:function onClick(){return t.updateService({op:e?"start":"stop"})},title:"Operate service"}),this.state.spinner)}}]),ServiceInfo}(c.Component)}}]);
//# sourceMappingURL=22.e4b00fa4.chunk.js.map