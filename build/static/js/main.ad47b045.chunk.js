(this.webpackJsonprims=this.webpackJsonprims||[]).push([[4],[,function(e,t,n){e.exports={main:"navigation_main__1-9J7",list:"navigation_list__3hOPY",item:"navigation_item__3bTNw",dropDownList:"navigation_dropDownList__wyKh9",dropDownItem:"navigation_dropDownItem__1A9q9",info:"navigation_info__6fuVI",button:"navigation_button__20Y3k"}},,,,,,function(e,t,n){e.exports={header:"header_header__YZ1S7",title:"header_title__gcejv",button:"header_button__2QI3b","head-button":"header_head-button__1hFin",menu:"header_menu__373a7",menuList:"header_menuList__37hpH",menuItem:"header_menuItem__1i0sO",menuButton:"header_menuButton__2FQM0","menu-button":"header_menu-button__2LUKk",menuSeparator:"header_menuSeparator__2PIuq"}},function(e,t,n){"use strict";n.d(t,"a",(function(){return u})),n.d(t,"d",(function(){return c})),n.d(t,"b",(function(){return l})),n.d(t,"e",(function(){return m})),n.d(t,"c",(function(){return d}));var a=n(12),r=n.n(a),o=n(18),i=n(0),u=Object(i.createContext)({setCookie:function(){},clearCookie:function(){},cookie:null,changeMain:function(){},loadNavigtion:function(){}});function c(){return s.apply(this,arguments)}function s(){return(s=Object(o.a)(r.a.mark((function e(){var t,n,a,o=arguments;return r.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=o.length>0&&void 0!==o[0]?o[0]:"",n=o.length>1&&void 0!==o[1]?o[1]:{},e.next=4,fetch(t,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(n)});case 4:return a=e.sent,e.next=7,a.json();case 7:return e.abrupt("return",e.sent);case 8:case"end":return e.stop()}}),e)})))).apply(this,arguments)}function l(){return f.apply(this,arguments)}function f(){return(f=Object(o.a)(r.a.mark((function e(){var t,n,a=arguments;return r.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=a.length>0&&void 0!==a[0]?a[0]:{},e.next=3,fetch("auth",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)});case 3:return n=e.sent,e.next=6,n.json();case 6:return e.abrupt("return",e.sent);case 7:case"end":return e.stop()}}),e)})))).apply(this,arguments)}u.displayName="RimsContext";var m=function(){return Math.floor(10*Math.random())},d=function(e){return(e>>24&255)+"."+(e>>16&255)+"."+(e>>8&255)+"."+(255&e)}},function(e,t,n){"use strict";n.r(t),n.d(t,"MenuButton",(function(){return m})),n.d(t,"MenuSeparator",(function(){return d})),n.d(t,"Header",(function(){return h}));var a=n(2),r=n(3),o=n(5),i=n(4),u=n(6),c=n(0),s=n.n(c),l=n(7),f=n.n(l),m=function(e){return s.a.createElement("li",{className:f.a.menuItem},s.a.createElement("button",{className:f.a.menuButton,onClick:e.onClick},e.title))},d=function(e){return s.a.createElement("li",{className:f.a.menuSeparator})},h=function(e){function t(e){var n;return Object(a.a)(this,t),(n=Object(o.a)(this,Object(i.a)(t).call(this,e))).implodeMenu=function(){n.state.height>0&&n.setState({height:0})},n.toggleMenu=function(){0===n.state.height?n.setState({height:2.8*n.props.children.length}):n.setState({height:0})},n.state={height:0},n}return Object(u.a)(t,e),Object(r.a)(t,[{key:"render",value:function(){var e=this;return s.a.createElement("header",{className:f.a.header},s.a.createElement("h1",{className:f.a.title},this.props.title),s.a.createElement("div",{className:f.a.menu,onMouseLeave:function(){return e.implodeMenu()}},s.a.createElement("button",{className:f.a.button,onClick:function(){return e.toggleMenu()}},s.a.createElement("i",{className:"fas fa-bars",style:{transform:0===this.state.height?"rotate(0deg)":"rotate(90deg)"}})),s.a.createElement("ul",{className:f.a.menuList,style:{maxHeight:"".concat(this.state.height,"rem")}},this.props.children)),s.a.createElement("button",{className:f.a.button,onClick:this.props.logOut,title:"Log out"},s.a.createElement("i",{className:"fas fa-sign-out-alt"})))}}]),t}(c.Component)},function(e,t,n){"use strict";n.r(t),n.d(t,"ErrorBoundary",(function(){return d})),n.d(t,"Spinner",(function(){return h})),n.d(t,"StateMap",(function(){return p})),n.d(t,"SearchField",(function(){return v})),n.d(t,"Result",(function(){return g})),n.d(t,"InfoColumns",(function(){return k})),n.d(t,"InfoArticle",(function(){return E})),n.d(t,"Theme",(function(){return b})),n.d(t,"TableHead",(function(){return y})),n.d(t,"TableRow",(function(){return _})),n.d(t,"ContentList",(function(){return N})),n.d(t,"ContentData",(function(){return C})),n.d(t,"ContentReport",(function(){return j}));var a=n(15),r=n(2),o=n(3),i=n(5),u=n(4),c=n(6),s=n(0),l=n.n(s),f=n(8),m=n(16),d=function(e){function t(e){var n;return Object(r.a)(this,t),(n=Object(i.a)(this,Object(u.a)(t).call(this,e))).state={hasError:!1,error:void 0,info:[]},n}return Object(c.a)(t,e),Object(o.a)(t,[{key:"componentDidCatch",value:function(e,t){this.setState({error:e.toString(),info:t.componentStack.split("\n")})}},{key:"render",value:function(){var e=this;return this.state.hasError?l.a.createElement("div",{className:"overlay",style:{top:0}},l.a.createElement("article",{className:"error"},l.a.createElement(m.CloseButton,{key:"error_close",onClick:function(){return e.setState({hasError:!1,error:void 0,info:[]})}}),l.a.createElement("h1",null,"UI Error"),l.a.createElement(k,{key:"error_ic"},l.a.createElement("label",{htmlFor:"type",className:"info"},"Type"),l.a.createElement("span",{id:"type",className:"info"},this.state.error),l.a.createElement("label",{htmlFor:"info",className:"info"},"Info:"),l.a.createElement("div",{id:"info"},this.state.info.map((function(e,t){return l.a.createElement("p",{key:"error_line"+t},e)})))))):this.props.children}}],[{key:"getDerivedStateFromError",value:function(e){return{hasError:!0}}}]),t}(l.a.Component),h=function(){return l.a.createElement("div",{className:"overlay"},l.a.createElement("div",{className:"loader"}))},p=function(e){return l.a.createElement("div",{className:"state "+{on:"green",off:"red",unknown:"grey",up:"green",down:"red",undefined:"orange",null:"orange"}[e.state]||!1,title:e.state})},v=function(e){return l.a.createElement("input",{type:"text",className:"searchfield",onChange:e.searchHandler,value:e.value,placeholder:e.placeholder})},g=function(e){return l.a.createElement("span",{className:"results"},e.result)},k=function(e){var t=["max-content","auto"];if(e.columns>2)for(var n=2;n<e.columns;n++)t.push(n%2===0?"max-content":"auto");return l.a.createElement("div",{className:"className"in e?"info ".concat(e.className):"info",style:{gridTemplateColumns:t.join(" ")}},e.children)};k.defaultProps={columns:2};var E=function(e){return l.a.createElement("article",{className:"info"},e.children)},b=function(e){function t(){var e,n;Object(r.a)(this,t);for(var o=arguments.length,c=new Array(o),s=0;s<o;s++)c[s]=arguments[s];return(n=Object(i.a)(this,(e=Object(u.a)(t)).call.apply(e,[this].concat(c)))).loadTheme=function(e){Object(f.d)("api/system/theme_info",{theme:e}).then((function(e){if("OK"===e.status)for(var t=0,n=Object.entries(e.data);t<n.length;t++){var r=Object(a.a)(n[t],2),o=r[0],i=r[1];document.documentElement.style.setProperty(o,i)}}))},n}return Object(c.a)(t,e),Object(o.a)(t,[{key:"componentDidMount",value:function(){this.loadTheme(this.props.theme)}},{key:"componentDidUpdate",value:function(e){e.theme!==this.props.theme&&this.loadTheme(this.props.theme)}},{key:"render",value:function(){return l.a.createElement(s.Fragment,{key:"fragment_theme"},this.props.children)}}]),t}(s.Component),y=function(e){return l.a.createElement("div",{className:"thead"},e.headers.map((function(e,t){return l.a.createElement("div",{key:"th_"+t},e)})))},_=function(e){return l.a.createElement("div",{className:"trow"},e.cells.map((function(e,t){return l.a.createElement("div",{key:"tr_"+t},e)})))},N=function(e){return l.a.createElement("section",{id:"div_content_left",className:"content-left"},x("table",e))},C=function(e){return l.a.createElement("section",{id:"div_content_right",className:"content-right"},e.children)},j=function(e){return x("report",e)},x=function(e,t){return t.trows?l.a.createElement("article",{className:t.hasOwnProperty("articleClass")?t.articleClass:e},l.a.createElement("h1",null,t.header),t.children,l.a.createElement(g,{key:"con_result",result:t.result}),l.a.createElement("div",{className:t.hasOwnProperty("tableClass")?t.tableClass:"table"},l.a.createElement(y,{key:"con_thead",headers:t.thead}),l.a.createElement("div",{className:"tbody"},t.trows.map((function(e,n){return l.a.createElement(_,{key:"tr_"+n,cells:t.listItem(e,n)})}))))):l.a.createElement(h,null)}},function(e,t,n){"use strict";n.r(t),n.d(t,"NavBar",(function(){return m})),n.d(t,"NavButton",(function(){return d})),n.d(t,"NavDropButton",(function(){return h})),n.d(t,"NavDropDown",(function(){return p})),n.d(t,"NavReload",(function(){return v})),n.d(t,"NavInfo",(function(){return g}));var a=n(2),r=n(3),o=n(5),i=n(4),u=n(6),c=n(0),s=n.n(c),l=n(1),f=n.n(l),m=function(e){return s.a.createElement("nav",{className:f.a.main,id:e.id},s.a.createElement("ul",{className:f.a.list},e.children))},d=function(e){return s.a.createElement("li",{className:f.a.item,style:e.style},s.a.createElement("button",{className:f.a.button,onClick:e.onClick},e.title))},h=function(e){return s.a.createElement("li",{className:f.a.dropDownItem,style:e.style},s.a.createElement("button",{className:f.a.button,onClick:e.onClick},e.title))},p=function(e){function t(e){var n;return Object(a.a)(this,t),(n=Object(o.a)(this,Object(i.a)(t).call(this,e))).expandList=function(){return n.setState({height:3*n.props.children.length})},n.implodeList=function(){return n.setState({height:0})},n.state={height:0},n}return Object(u.a)(t,e),Object(r.a)(t,[{key:"render",value:function(){var e=this;return s.a.createElement("li",{className:f.a.item,style:this.props.style,onMouseEnter:function(){return e.expandList()},onMouseLeave:function(){return e.implodeList()}},s.a.createElement("button",{className:f.a.button},this.props.title),s.a.createElement("ul",{className:f.a.dropDownList,style:{maxHeight:"".concat(this.state.height,"rem")}},this.props.children))}}]),t}(c.Component),v=function(e){return s.a.createElement("li",{className:f.a.item,style:e.style},s.a.createElement("button",{className:f.a.button,onClick:e.onClick},s.a.createElement("i",{className:"fas fa-redo-alt",style:{fontSize:"2.1rem"}})))},g=function(e){return s.a.createElement("li",{className:f.a.info,style:e.style},s.a.createElement("button",{className:f.a.button,onClick:e.onClick},e.title))}},,,function(e,t,n){"use strict";n.r(t),n.d(t,"TextLine",(function(){return s})),n.d(t,"StateLine",(function(){return l})),n.d(t,"TextInput",(function(){return f})),n.d(t,"UrlInput",(function(){return m})),n.d(t,"EmailInput",(function(){return d})),n.d(t,"PasswordInput",(function(){return h})),n.d(t,"DateInput",(function(){return p})),n.d(t,"TimeInput",(function(){return v})),n.d(t,"TextAreaInput",(function(){return g})),n.d(t,"CheckboxInput",(function(){return k})),n.d(t,"RadioInput",(function(){return E})),n.d(t,"SelectInput",(function(){return b}));var a=n(0),r=n.n(a),o=n(10),i=function(e){return e.label?e.label:e.id},u=function(e,t){return r.a.createElement(a.Fragment,{key:"template_"+t.id},r.a.createElement("label",{htmlFor:t.id,title:t.title,className:"info"},i(t),":"),r.a.createElement("input",{className:"info",type:e,id:t.id,name:t.id,onChange:t.onChange,value:null!==t.value?t.value:"",placeholder:t.placeholder,title:t.extra,size:t.size}))},c=function(e,t){return r.a.createElement(a.Fragment,{key:"template_"+t.id},r.a.createElement("label",{htmlFor:t.id,title:t.title,className:"info"},i(t),":"),e)},s=function(e){return c(r.a.createElement("span",{id:e.id,style:e.style,title:e.extra,className:"info"},e.text),e)},l=function(e){return c(Array.isArray(e.state)?r.a.createElement("div",{key:"state_line_multi_"+e.id,className:"states"},e.state.map((function(t,n){return r.a.createElement(o.StateMap,{key:"state_line_state_"+e.id+"_"+n,state:t})}))):r.a.createElement(o.StateMap,{key:"state_line_state_"+e.id,state:e.state}),e)},f=function(e){return u("text",e)},m=function(e){return u("url",e)},d=function(e){return u("email",e)},h=function(e){return u("password",e)},p=function(e){return u("date",e)},v=function(e){return u("time",e)},g=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,className:"info",title:e.title},i(e),":"),r.a.createElement("textarea",{id:e.id,name:e.id,onChange:e.onChange,className:"info",value:e.value}))},k=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,className:"info",title:e.title},i(e),":"),r.a.createElement("input",{type:"checkbox",id:e.id,name:e.id,onChange:e.onChange,defaultChecked:e.value,placeholder:e.placeholder,title:e.extra,className:"info"}))},E=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,className:"info",title:e.title},i(e),":"),r.a.createElement("div",null,e.options.map((function(t,n){return r.a.createElement(a.Fragment,{key:"fragradio_"+e.id+"_"+n},r.a.createElement("label",{htmlFor:"radio_input_"+e.id+"_"+n},t.text),r.a.createElement("input",{className:"info",type:"radio",key:"radio_input_"+e.id+"_"+n,id:"radio_input_"+e.id+"_"+n,name:e.id,onChange:e.onChange,value:t.value,checked:e.value.toString()===t.value.toString()?"checked":""}))}))))},b=function(e){return r.a.createElement(a.Fragment,{key:"fraginput_"+e.id},r.a.createElement("label",{htmlFor:e.id,title:e.title,className:"info"},i(e),":"),r.a.createElement("select",{name:e.id,onChange:e.onChange,value:null!==e.value&&void 0!==e.value?e.value:"NULL",className:"info"},(null===e.value||void 0===e.value)&&void 0===e.children.find((function(e){return"NULL"===e.props.value}))&&r.a.createElement("option",{value:"NULL"},"<Empty>"),e.children))}},,function(e,t,n){"use strict";n.r(t),n.d(t,"HrefButton",(function(){return o})),n.d(t,"HeaderButton",(function(){return i})),n.d(t,"TextButton",(function(){return c})),n.d(t,"AddButton",(function(){return s})),n.d(t,"BackButton",(function(){return l})),n.d(t,"CheckButton",(function(){return f})),n.d(t,"CloseButton",(function(){return m})),n.d(t,"ConfigureButton",(function(){return d})),n.d(t,"ConnectionButton",(function(){return h})),n.d(t,"DeleteButton",(function(){return p})),n.d(t,"DevicesButton",(function(){return v})),n.d(t,"DocButton",(function(){return g})),n.d(t,"EditButton",(function(){return k})),n.d(t,"FixButton",(function(){return E})),n.d(t,"ForwardButton",(function(){return b})),n.d(t,"GoButton",(function(){return y})),n.d(t,"InfoButton",(function(){return _})),n.d(t,"ItemsButton",(function(){return N})),n.d(t,"LinkButton",(function(){return C})),n.d(t,"LogButton",(function(){return j})),n.d(t,"NetworkButton",(function(){return x})),n.d(t,"PauseButton",(function(){return O})),n.d(t,"ReloadButton",(function(){return B})),n.d(t,"RevertButton",(function(){return w})),n.d(t,"SaveButton",(function(){return S})),n.d(t,"SearchButton",(function(){return M})),n.d(t,"ShutdownButton",(function(){return I})),n.d(t,"SnapshotButton",(function(){return L})),n.d(t,"StartButton",(function(){return T})),n.d(t,"StopButton",(function(){return F})),n.d(t,"SyncButton",(function(){return D})),n.d(t,"TermButton",(function(){return P})),n.d(t,"UiButton",(function(){return U})),n.d(t,"UnlinkButton",(function(){return H})),n.d(t,"ViewButton",(function(){return J}));var a=n(0),r=n.n(a),o=function(e){return r.a.createElement("button",{id:e.id,className:"text",style:e.style,onClick:e.onClick,title:e.title},e.text)},i=function(e){return r.a.createElement("button",{id:e.id,className:"text",style:e.highlight?{color:"var(--high-color)"}:{},onClick:e.onClick,title:e.title},e.text)},u=function(e,t){return r.a.createElement("button",{id:t.id,className:"info fa",onClick:t.onClick,title:t.title},r.a.createElement("i",{className:e}))},c=function(e){return r.a.createElement("button",{id:e.id,className:"info text",onClick:e.onClick,title:e.title},e.text)},s=function(e){return u("fas fa-plus",e)},l=function(e){return u("fas fa-arrow-left",e)},f=function(e){return u("fas fa-tasks",e)},m=function(e){return r.a.createElement("button",{id:e.id,className:"info fa right",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-times-circle"}))},d=function(e){return u("fas fa-cog",e)},h=function(e){return u("fas fa-arrows-alt",e)},p=function(e){return u("fas fa-trash-alt",e)},v=function(e){return u("fas fa-network-wired",e)},g=function(e){return u("fas fa-clipboard-list",e)},k=function(e){return u("fas fa-edit",e)},E=function(e){return u("fas fa-thumbtack",e)},b=function(e){return u("fas fa-arrow-right",e)},y=function(e){return u("fas fa-share-square",e)},_=function(e){return u("fas fa-info",e)},N=function(e){return u("fas fa-list-ul",e)},C=function(e){return u("fas fa-link",e)},j=function(e){return u("fas fa-file-alt",e)},x=function(e){return u("fas fa-share-alt",e)},O=function(e){return u("fas fa-pause",e)},B=function(e){return u("fas fa-redo-alt",e)},w=function(e){return u("fas fa-history",e)},S=function(e){return u("fas fa-download",e)},M=function(e){return u("fas fa-search",e)},I=function(e){return u("fas fa-power-off",e)},L=function(e){return u("fas fa-camera",e)},T=function(e){return r.a.createElement("button",{id:e.id,className:"info fa green",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-play"}))},F=function(e){return r.a.createElement("button",{id:e.id,className:"info fa red",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-stop"}))},D=function(e){return u("fas fa-exchange-alt",e)},P=function(e){return r.a.createElement("button",{id:e.id,className:"info fa",onClick:e.onClick,title:e.title},r.a.createElement("i",{className:"fas fa-terminal"}))},U=function(e){return u("fas fa-globe-americas",e)},H=function(e){return u("fas fa-unlink",e)},J=function(e){return u("fas fa-search-plus",e)}},,,,,function(e,t,n){var a={"./activity.jsx":[35,8],"./console.jsx":[36,9],"./device.jsx":[30,0],"./dns.jsx":[37,10],"./hypervisor.jsx":[38,0,11],"./infra/Buttons.jsx":[16],"./infra/Header.jsx":[9],"./infra/Inputs.jsx":[14],"./infra/Navigation.jsx":[11],"./infra/UI.jsx":[10],"./interface.jsx":[32,1],"./inventory.jsx":[39,12],"./ipam.jsx":[34,2],"./location.jsx":[31,3],"./multimedia.jsx":[40,13],"./node.jsx":[41,14],"./pdu.jsx":[42,15],"./rack.jsx":[43,0,7],"./reservation.jsx":[44,16],"./resource.jsx":[45,17],"./server.jsx":[46,18],"./system.jsx":[47,19],"./user.jsx":[48,20],"./visualize.jsx":[33,0]};function r(e){if(!n.o(a,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=a[e],r=t[0];return Promise.all(t.slice(1).map(n.e)).then((function(){return n(r)}))}r.keys=function(){return Object.keys(a)},r.id=21,e.exports=r},function(e,t,n){e.exports=n(29)},,,,,function(e,t,n){},,function(e,t,n){"use strict";n.r(t);var a=n(17),r=n(13),o=n(15),i=n(2),u=n(3),c=n(5),s=n(4),l=n(6),f=n(0),m=n.n(f),d=n(20),h=n.n(d),p=(n(27),n(8)),v=n(10),g=n(14),k=n(11),E=n(9);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}));var b=function(e){function t(e){var a;return Object(i.a)(this,t),(a=Object(c.a)(this,Object(s.a)(t).call(this,e))).loadNavigation=function(e){return a.setState({navigation:e})},a.changeContent=function(e){if(e.hasOwnProperty("module"))try{n(21)("./"+e.module+".jsx").then((function(t){var n=t[e.function];a.setState({navigation:m.a.createElement(k.NavBar,{key:"portal_navigation_empty"}),content:m.a.createElement(n,Object.assign({key:e.module+"_"+e.function},e.args)),height:0})}))}catch(t){console.error("Mapper error: "+e),alert(t)}else a.setState({navigation:m.a.createElement(k.NavBar,{key:"portal_navigation_empty"}),content:e})},a.state={menu:[],navigation:m.a.createElement(k.NavBar,{key:"portal_navigation_empty"})},a}return Object(l.a)(t,e),Object(u.a)(t,[{key:"componentDidMount",value:function(){var e=this;this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation}),Object(p.d)("api/portal/menu",{id:this.context.cookie.id}).then((function(t){e.setState(t),t.start&&e.changeContent(t.menu[t.start]),document.title=t.title}))}},{key:"render",value:function(){for(var e=this,t=[],n=function(){var n=Object(o.a)(r[a],2),i=n[0],u=n[1];"module"===u.type?t.push(m.a.createElement(E.MenuButton,{key:"hb_"+i,title:i,onClick:function(){return e.changeContent(u)}})):"tab"===u.type?t.push(m.a.createElement(E.MenuButton,{key:"hb_"+i,title:i,onClick:function(){return window.open(u.tab,"_blank")}})):"frame"===u.type&&t.push(m.a.createElement(E.MenuButton,{key:"hb_"+i,title:i,onClick:function(){return e.changeContent(m.a.createElement("iframe",{id:"resource_frame",name:"resource_frame",title:i,src:u.frame}))}}))},a=0,r=Object.entries(this.state.menu);a<r.length;a++)n();return t.push(m.a.createElement(E.MenuSeparator,{key:"hs_1"}),m.a.createElement(E.MenuButton,{key:"hb_user_info",title:"User",onClick:function(){return e.changeContent({module:"user",function:"User",args:{id:e.context.cookie.id}})}}),m.a.createElement(E.MenuButton,{key:"hb_system",title:"System",onClick:function(){return e.changeContent({module:"system",function:"Main"})}})),m.a.createElement(m.a.Fragment,{key:"portal"},m.a.createElement(v.Theme,{key:"portal_theme",theme:this.context.cookie.theme}),m.a.createElement(E.Header,{key:"portal_header",title:this.state.title,logOut:function(){return e.context.clearCookie()}},t),this.state.navigation,m.a.createElement(v.ErrorBoundary,{key:"portal_error"},m.a.createElement("main",null,this.state.content)))}}]),t}(f.Component);b.contextType=p.a;var y=function(e){function t(e){var n;return Object(i.a)(this,t),(n=Object(c.a)(this,Object(s.a)(t).call(this,e))).onChange=function(e){return n.setState(Object(r.a)({},e.target.name,e.target.value))},n.handleSubmit=function(e){e.preventDefault(),Object(p.d)("auth",{username:n.state.username,password:n.state.password}).then((function(e){"OK"===e.status?n.props.setCookie({node:e.node,token:e.token,id:e.id,theme:e.theme,expires:e.expires}):(document.getElementById("password").value="",n.setState((function(e){return Object(a.a)({},e,{password:""})})))}))},n.state={message:"",username:"username",password:"password"},n}return Object(l.a)(t,e),Object(u.a)(t,[{key:"componentDidMount",value:function(){var e=this;Object(p.d)("front").then((function(t){e.setState(t),document.title=t.title}))}},{key:"render",value:function(){return m.a.createElement("div",{className:"login"},m.a.createElement("article",{className:"login"},m.a.createElement("h1",null,this.state.message),m.a.createElement(v.InfoColumns,{className:"left"},m.a.createElement(g.TextInput,{key:"username",id:"username",onChange:this.onChange}),m.a.createElement(g.PasswordInput,{key:"password",id:"password",onChange:this.onChange})),m.a.createElement("button",{className:"login",onClick:this.handleSubmit,title:"Login"},m.a.createElement("i",{className:"fas fa-sign-in-alt"}))))}}]),t}(f.Component),_=function(e){function t(e){var n;return Object(i.a)(this,t),(n=Object(c.a)(this,Object(s.a)(t).call(this,e))).readCookie=function(){for(var e=document.cookie.split("; "),t=0;t<e.length;t++){var n=e[t];if(0===n.indexOf("rims="))return JSON.parse(atob(n.substring(5,n.length)))}return{token:null}},n.clearCookie=function(){document.cookie="rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT",n.setState({token:null})},n.setCookie=function(e){var t=btoa(JSON.stringify(e));document.cookie="rims="+t+"; expires="+e.expires+"; Path=/",n.setState(e)},n.providerMounting=function(e){Object.assign(n.provider,e),n.forceUpdate()},n.state=n.readCookie(),n.provider={},n}return Object(l.a)(t,e),Object(u.a)(t,[{key:"componentDidMount",value:function(){var e=this;this.state.token&&Object(p.b)({verify:this.state.token}).then((function(t){"OK"!==t.status?e.setState({token:null}):console.log("Token verified")}))}},{key:"render",value:function(){return m.a.createElement(p.a.Provider,{value:Object(a.a)({setCookie:this.setCookie,clearCookie:this.clearCookie,cookie:this.state},this.provider)},null===this.state.token?m.a.createElement(y,{setCookie:this.setCookie}):m.a.createElement(b,{providerMounting:this.providerMounting}))}}]),t}(f.Component);h.a.render(m.a.createElement(_,null),document.getElementById("root"))}],[[22,5,6]]]);
//# sourceMappingURL=main.ad47b045.chunk.js.map