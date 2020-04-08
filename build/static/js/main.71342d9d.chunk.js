(this.webpackJsonprims=this.webpackJsonprims||[]).push([[4],[,function(e,t,n){"use strict";n.r(t),n.d(t,"Header",(function(){return m})),n.d(t,"RimsContext",(function(){return d})),n.d(t,"Spinner",(function(){return h})),n.d(t,"StateMap",(function(){return p})),n.d(t,"SearchField",(function(){return v})),n.d(t,"Result",(function(){return g})),n.d(t,"InfoColumns",(function(){return k})),n.d(t,"InfoArticle",(function(){return y})),n.d(t,"Theme",(function(){return b})),n.d(t,"TableHead",(function(){return E})),n.d(t,"TableRow",(function(){return C})),n.d(t,"ContentList",(function(){return j})),n.d(t,"ContentData",(function(){return x})),n.d(t,"ContentReport",(function(){return _}));var a=n(12),r=n(3),o=n(4),i=n(6),u=n(5),c=n(7),l=n(0),s=n.n(l),f=n(8),m=function(e){return s.a.createElement("header",null,e.children)},d=Object(l.createContext)({setCookie:function(){},clearCookie:function(){},cookie:null,changeMain:function(){},loadNavigtion:function(){}});d.displayName="RimsContext";var h=function(){return s.a.createElement("div",{className:"overlay"},s.a.createElement("div",{className:"loader"}))},p=function(e){return s.a.createElement("div",{className:"state "+{on:"green",off:"red",unknown:"grey",up:"green",down:"red",undefined:"orange",null:"orange"}[e.state]||!1,title:e.state})},v=function(e){return s.a.createElement("input",{type:"text",className:"searchfield",onChange:e.searchHandler,value:e.value,placeholder:e.placeholder})},g=function(e){return s.a.createElement("span",{className:"results"},e.result)},k=function(e){var t=["max-content","auto"];if(e.columns>2)for(var n=2;n<e.columns;n++)t.push(n%2===0?"max-content":"auto");return s.a.createElement("div",{className:"className"in e?"info ".concat(e.className):"info",style:{gridTemplateColumns:t.join(" ")}},e.children)};k.defaultProps={columns:2};var y=function(e){return s.a.createElement("article",{className:"info"},e.children)},b=function(e){function t(){var e,n;Object(r.a)(this,t);for(var o=arguments.length,c=new Array(o),l=0;l<o;l++)c[l]=arguments[l];return(n=Object(i.a)(this,(e=Object(u.a)(t)).call.apply(e,[this].concat(c)))).loadTheme=function(e){Object(f.b)("api/system/theme_info",{theme:e}).then((function(e){if("OK"===e.status)for(var t=0,n=Object.entries(e.data);t<n.length;t++){var r=Object(a.a)(n[t],2),o=r[0],i=r[1];document.documentElement.style.setProperty(o,i)}}))},n}return Object(c.a)(t,e),Object(o.a)(t,[{key:"componentDidMount",value:function(){this.loadTheme(this.props.theme)}},{key:"componentDidUpdate",value:function(e){e.theme!==this.props.theme&&this.loadTheme(this.props.theme)}},{key:"render",value:function(){return s.a.createElement(l.Fragment,{key:"fragment_theme"},this.props.children)}}]),t}(l.Component),E=function(e){return s.a.createElement("div",{className:"thead"},e.headers.map((function(e,t){return s.a.createElement("div",{key:"th_"+t},e)})))},C=function(e){return s.a.createElement("div",{className:"trow"},e.cells.map((function(e,t){return s.a.createElement("div",{key:"tr_"+t},e)})))},j=function(e){return s.a.createElement("section",{id:"div_content_left",className:"content-left"},N("table",e))},x=function(e){return s.a.createElement("section",{id:"div_content_right",className:"content-right"},e.children)},_=function(e){return N("report",e)},N=function(e,t){return t.trows?s.a.createElement("article",{className:t.hasOwnProperty("articleClass")?t.articleClass:e},s.a.createElement("h1",null,t.header),t.children,s.a.createElement(g,{key:"con_result",result:t.result}),s.a.createElement("div",{className:t.hasOwnProperty("tableClass")?t.tableClass:"table"},s.a.createElement(E,{key:"con_thead",headers:t.thead}),s.a.createElement("div",{className:"tbody"},t.trows.map((function(e,n){return s.a.createElement(C,{key:"tr_"+n,cells:t.listItem(e,n)})}))))):s.a.createElement(h,null)}},function(e,t,n){"use strict";n.r(t),n.d(t,"MenuButton",(function(){return o})),n.d(t,"FontAwesomeMenuButton",(function(){return i})),n.d(t,"HrefButton",(function(){return u})),n.d(t,"HeaderButton",(function(){return c})),n.d(t,"TextButton",(function(){return s})),n.d(t,"AddButton",(function(){return f})),n.d(t,"BackButton",(function(){return m})),n.d(t,"CheckButton",(function(){return d})),n.d(t,"ConfigureButton",(function(){return h})),n.d(t,"ConnectionButton",(function(){return p})),n.d(t,"DeleteButton",(function(){return v})),n.d(t,"DevicesButton",(function(){return g})),n.d(t,"DocButton",(function(){return k})),n.d(t,"EditButton",(function(){return y})),n.d(t,"FixButton",(function(){return b})),n.d(t,"ForwardButton",(function(){return E})),n.d(t,"GoButton",(function(){return C})),n.d(t,"InfoButton",(function(){return j})),n.d(t,"ItemsButton",(function(){return x})),n.d(t,"LinkButton",(function(){return _})),n.d(t,"LogButton",(function(){return N})),n.d(t,"NetworkButton",(function(){return O})),n.d(t,"PauseButton",(function(){return w})),n.d(t,"ReloadButton",(function(){return B})),n.d(t,"RevertButton",(function(){return S})),n.d(t,"SaveButton",(function(){return M})),n.d(t,"SearchButton",(function(){return F})),n.d(t,"ShutdownButton",(function(){return I})),n.d(t,"SnapshotButton",(function(){return T})),n.d(t,"StartButton",(function(){return L})),n.d(t,"StopButton",(function(){return P})),n.d(t,"SyncButton",(function(){return U})),n.d(t,"TermButton",(function(){return D})),n.d(t,"UiButton",(function(){return A})),n.d(t,"UnlinkButton",(function(){return R})),n.d(t,"ViewButton",(function(){return H}));var a=n(0),r=n.n(a),o=function(e){return r.a.createElement("button",{className:"menu",title:e.title,form:e.form,onClick:e.onClick,style:e.style},"icon"in e?r.a.createElement("img",{src:e.icon,alt:e.title,draggable:"false"}):e.title)},i=function(e){return r.a.createElement("button",{id:e.id,className:"menu",style:e.style,onClick:e.onClick,title:e.title},r.a.createElement("i",{className:e.type}))},u=function(e){return r.a.createElement("button",{id:e.id,className:"text",style:e.style,onClick:e.onClick,title:e.title},e.text)},c=function(e){return r.a.createElement("button",{id:e.id,className:"text",style:e.highlight?{color:"var(--high-color)"}:{},onClick:e.onClick,title:e.title},e.text)},l=function(e,t){return r.a.createElement("button",{id:t.id,className:"info fa",onClick:t.onClick,title:t.title},r.a.createElement("i",{className:e}))},s=function(e){return r.a.createElement("button",{id:e.id,className:"info text",onClick:e.onClick,title:e.title},e.text)},f=function(e){return l("fas fa-plus",e)},m=function(e){return l("fas fa-arrow-left",e)},d=function(e){return l("fas fa-tasks",e)},h=function(e){return l("fas fa-cog",e)},p=function(e){return l("fas fa-arrows-alt",e)},v=function(e){return l("fas fa-trash-alt",e)},g=function(e){return l("fas fa-network-wired",e)},k=function(e){return l("fas fa-clipboard-list",e)},y=function(e){return l("fas fa-edit",e)},b=function(e){return l("fas fa-thumbtack",e)},E=function(e){return l("fas fa-arrow-right",e)},C=function(e){return l("fas fa-share-square",e)},j=function(e){return l("fas fa-info",e)},x=function(e){return l("fas fa-list-ul",e)},_=function(e){return l("fas fa-link",e)},N=function(e){return l("fas fa-file-alt",e)},O=function(e){return l("fas fa-share-alt",e)},w=function(e){return l("fas fa-pause",e)},B=function(e){return l("fas fa-redo-alt",e)},S=function(e){return l("fas fa-history",e)},M=function(e){return l("fas fa-download",e)},F=function(e){return l("fas fa-search",e)},I=function(e){return l("fas fa-power-off",e)},T=function(e){return l("fas fa-camera",e)},L=function(e){return r.a.createElement("button",{id:e.id,className:"info fa green",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-play"}))},P=function(e){return r.a.createElement("button",{id:e.id,className:"info fa red",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-stop"}))},U=function(e){return l("fas fa-exchange-alt",e)},D=function(e){return r.a.createElement("button",{id:e.id,className:"info fa",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-terminal"}))},A=function(e){return l("fas fa-globe-americas",e)},R=function(e){return l("fas fa-unlink",e)},H=function(e){return l("fas fa-search-plus",e)}},,,,,,function(e,t,n){"use strict";n.d(t,"b",(function(){return i})),n.d(t,"c",(function(){return c})),n.d(t,"a",(function(){return l}));var a=n(14),r=n.n(a),o=n(17);function i(){return u.apply(this,arguments)}function u(){return(u=Object(o.a)(r.a.mark((function e(){var t,n,a,o=arguments;return r.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=o.length>0&&void 0!==o[0]?o[0]:"",n=o.length>1&&void 0!==o[1]?o[1]:{},e.next=4,fetch(t,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(n)});case 4:if(200!==(a=e.sent).status){e.next=11;break}return e.next=8,a.json();case 8:return e.abrupt("return",e.sent);case 11:return e.abrupt("return",{});case 12:case"end":return e.stop()}}),e)})))).apply(this,arguments)}var c=function(){return Math.floor(10*Math.random())},l=function(e){return(e>>24&255)+"."+(e>>16&255)+"."+(e>>8&255)+"."+(255&e)}},,function(e,t,n){"use strict";n.r(t),n.d(t,"TextLine",(function(){return l})),n.d(t,"StateLine",(function(){return s})),n.d(t,"TextInput",(function(){return f})),n.d(t,"UrlInput",(function(){return m})),n.d(t,"EmailInput",(function(){return d})),n.d(t,"PasswordInput",(function(){return h})),n.d(t,"DateInput",(function(){return p})),n.d(t,"TimeInput",(function(){return v})),n.d(t,"CheckboxInput",(function(){return g})),n.d(t,"RadioInput",(function(){return k})),n.d(t,"SelectInput",(function(){return y}));var a=n(0),r=n.n(a),o=n(1),i=function(e){return e.label?e.label:e.id},u=function(e,t){return r.a.createElement(a.Fragment,{key:"template_"+t.id},r.a.createElement("label",{htmlFor:t.id,title:t.title,className:"info"},i(t),":"),r.a.createElement("input",{className:"info",type:e,id:t.id,name:t.id,onChange:t.onChange,value:null!==t.value?t.value:"",placeholder:t.placeholder,title:t.extra}))},c=function(e,t){return r.a.createElement(a.Fragment,{key:"template_"+t.id},r.a.createElement("label",{htmlFor:t.id,title:t.title,className:"info"},i(t),":"),e)},l=function(e){return c(r.a.createElement("span",{id:e.id,style:e.style,title:e.extra,className:"info"},e.text),e)},s=function(e){return c(Array.isArray(e.state)?r.a.createElement("div",{key:"state_line_multi_"+e.id,className:"states"},e.state.map((function(t,n){return r.a.createElement(o.StateMap,{key:"state_line_state_"+e.id+"_"+n,state:t})}))):r.a.createElement(o.StateMap,{key:"state_line_state_"+e.id,state:e.state}),e)},f=function(e){return u("text",e)},m=function(e){return u("url",e)},d=function(e){return u("email",e)},h=function(e){return u("password",e)},p=function(e){return u("date",e)},v=function(e){return u("time",e)},g=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,className:"info",title:e.title},i(e),":"),r.a.createElement("input",{type:"checkbox",id:e.id,name:e.id,onChange:e.onChange,defaultChecked:e.value,placeholder:e.placeholder,title:e.extra,className:"info"}))},k=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,className:"info",title:e.title},i(e),":"),r.a.createElement("div",null,e.options.map((function(t,n){return r.a.createElement(a.Fragment,{key:"fragradio_"+e.id+"_"+n},r.a.createElement("label",{htmlFor:"radio_input_"+e.id+"_"+n},t.text),r.a.createElement("input",{className:"info",type:"radio",key:"radio_input_"+e.id+"_"+n,id:"radio_input_"+e.id+"_"+n,name:e.id,onChange:e.onChange,value:t.value,checked:e.value.toString()===t.value.toString()?"checked":""}))}))))},y=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,title:e.title,className:"info"},i(e),":"),r.a.createElement("select",{name:e.id,onChange:e.onChange,value:null!==e.value&&void 0!==e.value?e.value:"NULL",className:"info"},(null===e.value||void 0===e.value)&&void 0===e.children.find((function(e){return"NULL"===e.props.value}))&&r.a.createElement("option",{value:"NULL"},"<Empty>"),e.children))}},function(e,t,n){"use strict";n.d(t,"a",(function(){return s})),n.d(t,"b",(function(){return f})),n.d(t,"c",(function(){return m})),n.d(t,"e",(function(){return d})),n.d(t,"d",(function(){return h}));var a=n(3),r=n(4),o=n(6),i=n(5),u=n(7),c=n(0),l=n.n(c),s=function(e){return l.a.createElement("nav",{id:e.id},l.a.createElement("ul",null,e.children))},f=function(e){return l.a.createElement("li",{style:e.style},l.a.createElement("button",{className:"nav",onClick:e.onClick},e.title))},m=function(e){function t(e){var n;return Object(a.a)(this,t),(n=Object(o.a)(this,Object(i.a)(t).call(this,e))).changeSize=function(e){return n.setState({height:e})},n.state={height:0},n}return Object(u.a)(t,e),Object(r.a)(t,[{key:"render",value:function(){var e=this;return l.a.createElement("li",{style:this.props.style,onMouseEnter:function(){return e.changeSize("calc(var(--nav-height) * ".concat(e.props.children.length,")"))},onMouseLeave:function(){return e.changeSize(0)}},l.a.createElement("label",null,this.props.title),l.a.createElement("ul",{className:"dropdown",style:{maxHeight:this.state.height}},this.props.children))}}]),t}(c.Component),d=function(e){return l.a.createElement("li",{style:e.style},l.a.createElement("button",{className:"nav fa",onClick:e.onClick},l.a.createElement("i",{className:"fas fa-redo-alt"})))},h=function(e){return l.a.createElement("li",{className:"navinfo right",style:e.style},l.a.createElement("button",{className:"nav navinfo",onClick:e.onClick},e.title))}},,,,,,,function(e,t,n){var a={"./activity.jsx":[33,9],"./console.jsx":[34,10],"./device.jsx":[27,0],"./dns.jsx":[35,11],"./hypervisor.jsx":[36,0,12],"./infra/Buttons.jsx":[2],"./infra/Inputs.jsx":[10],"./infra/UI.jsx":[1],"./interface.jsx":[29,1],"./inventory.jsx":[37,13],"./ipam.jsx":[32,2],"./location.jsx":[28,3],"./multimedia.jsx":[38,14],"./node.jsx":[30,15],"./pdu.jsx":[39,16],"./rack.jsx":[40,0,7],"./reservation.jsx":[41,17],"./resource.jsx":[42,18],"./server.jsx":[43,19],"./system.jsx":[44,8],"./user.jsx":[45,20],"./visualize.jsx":[31,0]};function r(e){if(!n.o(a,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=a[e],r=t[0];return Promise.all(t.slice(1).map(n.e)).then((function(){return n(r)}))}r.keys=function(){return Object.keys(a)},r.id=18,e.exports=r},function(e,t,n){e.exports=n(26)},,,,,function(e,t,n){},,function(e,t,n){"use strict";n.r(t);var a=n(13),r=n(9),o=n(12),i=n(3),u=n(4),c=n(6),l=n(5),s=n(7),f=n(0),m=n.n(f),d=n(16),h=n.n(d),p=(n(24),n(8)),v=n(1),g=n(10),k=n(2),y=n(11);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}));var b=function(e){function t(e){var a;return Object(i.a)(this,t),(a=Object(c.a)(this,Object(l.a)(t).call(this,e))).loadNavigation=function(e){return a.setState({navigation:e})},a.changeContent=function(e){if(e.hasOwnProperty("module")){if(a.state.content&&a.state.content.key==="".concat(e.module,"_").concat(e.function))return;try{n(18)("./"+e.module+".jsx").then((function(t){var n=t[e.function];a.setState({navigation:m.a.createElement(y.a,{key:"portal_navigation_empty"}),content:m.a.createElement(n,Object.assign({key:e.module+"_"+e.function},e.args))})}))}catch(t){console.error("Mapper error: "+e),alert(t)}}else a.setState({navigation:m.a.createElement(y.a,{key:"portal_navigation_empty"}),content:e})},a.state={menu:[],navigation:m.a.createElement(y.a,{key:"portal_navigation_empty"})},a}return Object(s.a)(t,e),Object(u.a)(t,[{key:"componentDidMount",value:function(){var e=this;this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation}),Object(p.b)("api/portal/menu",{id:this.context.cookie.id}).then((function(t){e.setState(t),t.start&&e.changeContent(t.menu[t.start]),document.title=t.title}))}},{key:"render",value:function(){for(var e=this,t=[],n=function(){var n=Object(o.a)(r[a],2),i=n[0],u=n[1];"module"===u.type?t.push(m.a.createElement(k.MenuButton,Object.assign({key:"mb_"+i,title:i},u,{onClick:function(){return e.changeContent(u)}}))):"tab"===u.type?t.push(m.a.createElement(k.MenuButton,Object.assign({key:"mb_"+i,title:i},u,{onClick:function(){return window.open(u.tab,"_blank")}}))):"frame"===u.type&&t.push(m.a.createElement(k.MenuButton,Object.assign({key:"mb_"+i,title:i},u,{onClick:function(){return e.changeContent(m.a.createElement("iframe",{id:"resource_frame",name:"resource_frame",title:i,src:u.frame}))}})))},a=0,r=Object.entries(this.state.menu);a<r.length;a++)n();return m.a.createElement(m.a.Fragment,{key:"portal"},m.a.createElement(v.Theme,{key:"portal_theme",theme:this.context.cookie.theme}),m.a.createElement(v.Header,{key:"portal_header"},m.a.createElement(k.FontAwesomeMenuButton,{key:"mb_btn_logout",style:{float:"right",backgroundColor:"var(--high-color)"},onClick:function(){e.context.clearCookie()},title:"Log out",type:"fas fa-sign-out-alt"}),m.a.createElement(k.FontAwesomeMenuButton,{key:"mb_btn_system_Main",style:{float:"right"},onClick:function(){e.changeContent({module:"system",function:"Main"})},title:"System information",type:"fas fa-cogs"}),m.a.createElement(k.FontAwesomeMenuButton,{key:"mb_btn_user_User",style:{float:"right"},onClick:function(){e.changeContent({module:"user",function:"User",args:{id:e.context.cookie.id}})},title:"User",type:"fas fa-user"}),t),this.state.navigation,m.a.createElement("main",null,this.state.content))}}]),t}(f.Component);b.contextType=v.RimsContext;var E=function(e){function t(e){var n;return Object(i.a)(this,t),(n=Object(c.a)(this,Object(l.a)(t).call(this,e))).onChange=function(e){return n.setState(Object(r.a)({},e.target.name,e.target.value))},n.handleSubmit=function(e){e.preventDefault(),Object(p.b)("auth",{username:n.state.username,password:n.state.password}).then((function(e){"OK"===e.status?n.props.setCookie({node:e.node,token:e.token,id:e.id,theme:e.theme,expires:e.expires}):(document.getElementById("password").value="",n.setState((function(e){return Object(a.a)({},e,{password:""})})))}))},n.state={message:"",username:"username",password:"password"},n}return Object(s.a)(t,e),Object(u.a)(t,[{key:"componentDidMount",value:function(){var e=this;Object(p.b)("front").then((function(t){e.setState(t),document.title=t.title}))}},{key:"render",value:function(){return m.a.createElement("div",{className:"login"},m.a.createElement("article",{className:"login"},m.a.createElement("h1",null,this.state.message),m.a.createElement(v.InfoColumns,{className:"left"},m.a.createElement(g.TextInput,{key:"username",id:"username",onChange:this.onChange}),m.a.createElement(g.PasswordInput,{key:"password",id:"password",onChange:this.onChange})),m.a.createElement(k.FontAwesomeMenuButton,{key:"login_btn_login",onClick:this.handleSubmit,title:"Login",type:"fas fa-sign-in-alt"})))}}]),t}(f.Component),C=function(e){function t(e){var n;return Object(i.a)(this,t),(n=Object(c.a)(this,Object(l.a)(t).call(this,e))).readCookie=function(){for(var e=document.cookie.split("; "),t=0;t<e.length;t++){var n=e[t];if(0===n.indexOf("rims="))return JSON.parse(atob(n.substring(5,n.length)))}return{token:null}},n.clearCookie=function(){document.cookie="rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT",n.setState({token:null})},n.setCookie=function(e){var t=btoa(JSON.stringify(e));document.cookie="rims="+t+"; expires="+e.expires+"; Path=/",n.setState(e)},n.providerMounting=function(e){Object.assign(n.provider,e),n.forceUpdate()},n.state=n.readCookie(),n.provider={},n}return Object(s.a)(t,e),Object(u.a)(t,[{key:"render",value:function(){return m.a.createElement(v.RimsContext.Provider,{value:Object(a.a)({setCookie:this.setCookie,clearCookie:this.clearCookie,cookie:this.state},this.provider)},null===this.state.token?m.a.createElement(E,{setCookie:this.setCookie}):m.a.createElement(b,{providerMounting:this.providerMounting}))}}]),t}(f.Component);h.a.render(m.a.createElement(C,null),document.getElementById("root"))}],[[19,5,6]]]);
//# sourceMappingURL=main.71342d9d.chunk.js.map