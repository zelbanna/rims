(this.webpackJsonprims=this.webpackJsonprims||[]).push([[6],[,function(t,e,n){t.exports={main:"ui_main__Nm6EJ",contentLeft:"ui_contentLeft__2Bm6X",contentRight:"ui_contentRight__70N1v",info:"ui_info__pwNpV",code:"ui_code__1c759",frame:"ui_frame__Rp5Sl",loginOverlay:"ui_loginOverlay__2v5hY",login:"ui_login__u3QHE",title:"ui_title__1MpeV",button:"ui_button__10mcD",article:"ui_article__3eH2m",line:"ui_line__3qKyb",error:"ui_error__2ZDnv",stateLeds:"ui_stateLeds__K2qKU",stateRed:"ui_stateRed__3t9pN",stateGreen:"ui_stateGreen__2mPty",stateGrey:"ui_stateGrey__3vf6a",stateOrange:"ui_stateOrange__1M4su",flex:"ui_flex__2CIpQ",columns:"ui_columns__3g2gt",result:"ui_result__ITMWk",href:"ui_href__gTjt9",network:"ui_network__37LD6",spinOverlay:"ui_spinOverlay__23tkJ",loader:"ui_loader__1JPkE",bubbles:"ui_bubbles__F4edm"}},function(t,e,n){t.exports={button:"navigation_button__20Y3k",infobutton:"navigation_infobutton__1NhUX",dropbutton:"navigation_dropbutton__3q87W",main:"navigation_main__1-9J7",list:"navigation_list__3hOPY",item:"navigation_item__3bTNw",dropDownList:"navigation_dropDownList__wyKh9",dropDownItem:"navigation_dropDownItem__1A9q9",info:"navigation_info__6fuVI"}},,,,,function(t,e,n){t.exports={label:"input_label__k8FBs",input:"input_input__2GEr3",checkbox:"input_checkbox__GILWd",span:"input_span__1jy_2",textarea:"input_textarea__JHJUJ",searchfield:"input_searchfield__VUedh"}},function(t,e,n){t.exports={report:"table_report__VRtLp",list:"table_list__2S89B",title:"table_title__1Nt5y",table:"table_table__LqYKC",thead:"table_thead__39Nm6",tbody:"table_tbody__22fLN",trow:"table_trow__1Ih1w",th:"table_th__3x2Cn",td:"table_td__2fabh"}},function(t,e,n){"use strict";n.r(e),n.d(e,"MenuButton",(function(){return m})),n.d(e,"MenuSeparator",(function(){return f})),n.d(e,"HeaderButton",(function(){return d})),n.d(e,"Header",(function(){return h}));var a=n(3),r=n(4),o=n(5),i=n(6),u=n(0),c=n.n(u),l=n(11),s=n.n(l),m=function(t){return c.a.createElement("li",{className:s.a.menuItem},c.a.createElement("button",{className:s.a.menuButton,onClick:t.onClick},t.title))},f=function(t){return c.a.createElement("li",{className:s.a.menuSeparator})},d=function(t){return c.a.createElement("button",{className:s.a.button,onClick:t.onClick,title:t.title},c.a.createElement("i",{className:t.type,style:t.style}))},h=function(t){Object(i.a)(n,t);var e=Object(o.a)(n);function n(t){var r;return Object(a.a)(this,n),(r=e.call(this,t)).implodeMenu=function(){r.state.height>0&&r.setState({height:0})},r.toggleMenu=function(){0===r.state.height?r.setState({height:2.8*r.props.children.length}):r.setState({height:0})},r.zoomTxt=function(){var t=window.getComputedStyle(document.documentElement).fontSize.replace("px","");r.state.zoom?document.documentElement.style.removeProperty("font-size"):document.documentElement.style.setProperty("font-size","".concat(1.2*t,"px")),r.setState({zoom:!r.state.zoom})},r.state={height:0,zoom:""!==document.documentElement.style.getPropertyValue("font-size")},r}return Object(r.a)(n,[{key:"render",value:function(){var t=this;return c.a.createElement("header",{className:s.a.header},c.a.createElement("h1",{className:s.a.title},this.props.title),c.a.createElement(d,{key:"zoom_"+this.state.zoom,onClick:function(){return t.zoomTxt()},title:"Zoom",type:this.state.zoom?"fas fa-search-minus":"fas fa-search-plus"}),c.a.createElement("div",{className:s.a.menu,onMouseLeave:function(){return t.implodeMenu()}},c.a.createElement(d,{key:"menu_"+this.state.height,onClick:function(){return t.toggleMenu()},title:"Menu",type:"fas fa-bars",style:{transform:0===this.state.height?"rotate(0deg)":"rotate(90deg)"}}),c.a.createElement("ul",{className:s.a.menuList,style:{maxHeight:"".concat(this.state.height,"rem")}},this.props.children)),c.a.createElement(d,{key:"logout",onClick:this.props.logOut,title:"Log out",type:"fas fa-sign-out-alt"}))}}]),n}(u.PureComponent)},function(t,e,n){t.exports={href:"button_href__3AdJ5",text:"button_text__2sVk2",info:"button_info__3n4TT",ipam:"button_ipam__1jKFF"}},function(t,e,n){t.exports={title:"header_title__gcejv",menuList:"header_menuList__37hpH",header:"header_header__YZ1S7",button:"header_button__2QI3b","head-button":"header_head-button__1hFin",menu:"header_menu__373a7",menuItem:"header_menuItem__1i0sO",menuButton:"header_menuButton__2FQM0","menu-button":"header_menu-button__2LUKk",menuSeparator:"header_menuSeparator__2PIuq"}},function(t,e,n){"use strict";n.d(e,"d",(function(){return u})),n.d(e,"a",(function(){return l})),n.d(e,"e",(function(){return m})),n.d(e,"b",(function(){return f})),n.d(e,"c",(function(){return d}));var a=n(17),r=n.n(a),o=n(14),i=n(22);function u(){return c.apply(this,arguments)}function c(){return(c=Object(i.a)(r.a.mark((function t(){var e,n,a,i,u=arguments;return r.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=u.length>0&&void 0!==u[0]?u[0]:"",n=u.length>1&&void 0!==u[1]?u[1]:{},a=u.length>2&&void 0!==u[2]?u[2]:{},t.next=5,fetch(e,{method:"POST",headers:Object(o.a)({"Content-Type":"application/json"},a),credentials:"include",body:JSON.stringify(n)});case 5:return i=t.sent,t.next=8,i.json();case 8:return t.abrupt("return",t.sent);case 9:case"end":return t.stop()}}),t)})))).apply(this,arguments)}function l(){return s.apply(this,arguments)}function s(){return(s=Object(i.a)(r.a.mark((function t(){var e,n,a=arguments;return r.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=a.length>0&&void 0!==a[0]?a[0]:{},t.next=3,fetch("auth",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(e)});case 3:return n=t.sent,t.next=6,n.json();case 6:return t.abrupt("return",t.sent);case 7:case"end":return t.stop()}}),t)})))).apply(this,arguments)}var m=function(){return Math.floor(10*Math.random())},f=function(t){return(t>>24&255)+"."+(t>>16&255)+"."+(t>>8&255)+"."+(255&t)},d=function(t){return t.split(".").reduce((function(t,e){return+e+(t<<8)}),0)>>>0}},function(t,e,n){"use strict";n.r(e),n.d(e,"Title",(function(){return E})),n.d(e,"Flex",(function(){return k})),n.d(e,"Spinner",(function(){return x})),n.d(e,"StateLeds",(function(){return C})),n.d(e,"Article",(function(){return j})),n.d(e,"LineArticle",(function(){return O})),n.d(e,"CodeArticle",(function(){return B})),n.d(e,"InfoArticle",(function(){return S})),n.d(e,"InfoColumns",(function(){return w})),n.d(e,"Result",(function(){return L})),n.d(e,"Row",(function(){return I})),n.d(e,"ContentList",(function(){return T})),n.d(e,"ContentData",(function(){return M})),n.d(e,"ContentReport",(function(){return P})),n.d(e,"RimsContext",(function(){return D})),n.d(e,"Portal",(function(){return z})),n.d(e,"Login",(function(){return A}));var a=n(18),r=n(21),o=n(3),i=n(4),u=n(5),c=n(6),l=n(14),s=n(0),m=n.n(s),f=n(12),d=n(19),h=n(15),p=n(9),_=n(16),v=n(8),g=n.n(v),b=n(1),y=n.n(b),E=function(t){return m.a.createElement("h1",{className:y.a.title},t.text)},k=function(t){return m.a.createElement("div",{className:y.a.flex,style:t.style},t.children)},x=function(){return m.a.createElement("div",{className:y.a.spinOverlay},m.a.createElement("div",{className:y.a.loader}))},N=function(t){return m.a.createElement("div",{className:{on:y.a.stateGreen,off:y.a.stateRed,unknown:y.a.stateGrey,up:y.a.stateGreen,down:y.a.stateRed,undefined:y.a.stateOrange,null:y.a.stateOrange}[t.state]||y.a.stateOrange,title:t.state})},C=function(t){return m.a.createElement("div",{className:y.a.stateLeds},Array.isArray(t.state)?t.state.map((function(t,e){return m.a.createElement(N,{key:e,state:t})})):m.a.createElement(N,{key:"led",state:t.state}))},j=function(t){return m.a.createElement("article",{className:y.a.article},m.a.createElement("h1",{className:y.a.title},t.header),t.children)},O=function(t){return m.a.createElement("article",{className:y.a.line},m.a.createElement("h1",{className:y.a.title},t.header),t.children)},B=function(t){return m.a.createElement("article",{className:y.a.code},m.a.createElement("h1",{className:y.a.title},t.header),t.children)},S=function(t){return m.a.createElement("article",{className:y.a.info},m.a.createElement("h1",{className:y.a.title},t.header),t.children)},w=function(t){var e=["max-content","auto"];if(t.columns>2)for(var n=2;n<t.columns;n++)e.push(n%2===0?"max-content":"auto");return m.a.createElement("div",{className:y.a.columns,style:Object(l.a)({gridTemplateColumns:e.join(" ")},t.style)},t.children)};w.defaultProps={columns:2};var L=function(t){return m.a.createElement("span",{className:y.a.result},t.result)},I=function(t){return m.a.createElement("div",{className:g.a.trow},t.cells.map((function(t,e){return m.a.createElement("div",{key:e,className:g.a.td},t)})))},T=function(t){return m.a.createElement("section",{className:y.a.contentLeft},F(g.a.list,t))},M=function(t){return m.a.createElement("section",{className:y.a.contentRight},t.children)},P=function(t){return F(g.a.report,t)},F=function(t,e){return e.trows?m.a.createElement("article",{className:t},m.a.createElement("h1",{className:g.a.title},e.header),e.children,m.a.createElement(L,{key:"result",result:e.result}),m.a.createElement("div",{className:g.a.table},m.a.createElement("div",{className:g.a.thead},e.thead.map((function(t,e){return m.a.createElement("div",{key:e,className:g.a.th},t)}))),m.a.createElement("div",{className:g.a.tbody},e.trows.map((function(t,n){return m.a.createElement(I,{key:n,cells:e.listItem(t,n)})}))))):m.a.createElement(x,null)},D=Object(s.createContext)({settings:null,logIn:function(){},logOut:function(){},changeMain:function(){},loadNavigtion:function(){},changeTheme:function(){}});D.displayName="RimsContext";var U=function(t){Object(c.a)(n,t);var e=Object(u.a)(n);function n(t){var a;return Object(o.a)(this,n),(a=e.call(this,t)).state={hasError:!1,error:void 0,info:[]},a}return Object(i.a)(n,[{key:"componentDidCatch",value:function(t,e){this.setState({error:t.toString(),info:e.componentStack.split("\n")})}},{key:"render",value:function(){var t=this;return this.state.hasError?m.a.createElement("div",{className:y.a.overlay,style:{top:0}},m.a.createElement("article",{className:y.a.error},m.a.createElement(d.CloseButton,{key:"close",onClick:function(){return t.setState({hasError:!1,error:void 0,info:[]})}}),m.a.createElement("h1",{className:y.a.title},"UI Error"),m.a.createElement(w,{key:"ic"},m.a.createElement(h.TextLine,{key:"type",id:"type",text:this.state.error}),m.a.createElement(h.TextAreaInput,{key:"text",id:"info",value:this.state.info.join("\n")})))):this.props.children}}],[{key:"getDerivedStateFromError",value:function(t){return{hasError:!0}}}]),n}(m.a.Component),R=function(t){Object(c.a)(n,t);var e=Object(u.a)(n);function n(){var t;Object(o.a)(this,n);for(var a=arguments.length,i=new Array(a),u=0;u<a;u++)i[u]=arguments[u];return(t=e.call.apply(e,[this].concat(i))).loadTheme=function(t){Object(f.d)("api/portal/theme_info",{theme:t}).then((function(t){if(t&&"OK"===t.status)for(var e=0,n=Object.entries(t.data);e<n.length;e++){var a=Object(r.a)(n[e],2),o=a[0],i=a[1];document.documentElement.style.setProperty(o,i)}}))},t}return Object(i.a)(n,[{key:"componentDidMount",value:function(){this.loadTheme(this.props.theme)}},{key:"componentDidUpdate",value:function(t){t.theme!==this.props.theme&&this.loadTheme(this.props.theme)}},{key:"render",value:function(){return m.a.createElement(s.Fragment,null)}}]),n}(s.Component),z=function(t){Object(c.a)(a,t);var e=Object(u.a)(a);function a(t){var r;return Object(o.a)(this,a),(r=e.call(this,t)).loadNavigation=function(t){return r.setState({navigation:t})},r.changeContent=function(t){if(t.hasOwnProperty("module"))try{n(25)("./"+t.module+".jsx").then((function(e){var n=e[t.function];r.setState({navigation:m.a.createElement(_.NavBar,{key:"portal_navigation"}),content:m.a.createElement(n,Object.assign({key:t.module+"_"+t.function},t.args))})}))}catch(e){console.error("Mapper error: "+t),alert(e)}else r.setState({navigation:m.a.createElement(_.NavBar,{key:"portal_navigation"}),content:t})},r.state={menu:[],navigation:m.a.createElement(_.NavBar,{key:"portal_navigation_empty"})},r}return Object(i.a)(a,[{key:"componentDidMount",value:function(){var t=this;this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation}),Object(f.d)("api/portal/menu",{id:this.context.settings.id}).then((function(e){if(e&&"OK"===e.status){var n=e.data;t.setState(n),n.start&&t.changeContent(n.menu[n.start]),document.title=n.title}}))}},{key:"render",value:function(){for(var t=this,e=[],n=function(){var n=Object(r.a)(o[a],2),i=n[0],u=n[1];"module"===u.type?e.push(m.a.createElement(p.MenuButton,{key:i,title:i,onClick:function(){return t.changeContent(u)}})):"tab"===u.type?e.push(m.a.createElement(p.MenuButton,{key:i,title:i,onClick:function(){return window.open(u.tab,"_blank")}})):"frame"===u.type&&e.push(m.a.createElement(p.MenuButton,{key:i,title:i,onClick:function(){return t.changeContent(m.a.createElement("iframe",{className:y.a.frame,title:i,src:u.frame}))}}))},a=0,o=Object.entries(this.state.menu);a<o.length;a++)n();return e.push(m.a.createElement(p.MenuSeparator,{key:"hs_1"}),m.a.createElement(p.MenuButton,{key:"user_info",title:"User",onClick:function(){return t.changeContent({module:"user",function:"User",args:{id:t.context.settings.id}})}}),m.a.createElement(p.MenuButton,{key:"system",title:"System",onClick:function(){return t.changeContent({module:"system",function:"Main"})}})),m.a.createElement(s.Fragment,null,m.a.createElement(R,{key:"portal_theme",theme:this.context.settings.theme}),m.a.createElement(p.Header,{key:"portal_header",title:this.state.title,logOut:function(){return t.context.logOut()}},e),this.state.navigation,m.a.createElement(U,{key:"portal_error"},m.a.createElement("main",{className:y.a.main},this.state.content)))}}]),a}(s.Component);z.contextType=D;var A=function(t){Object(c.a)(n,t);var e=Object(u.a)(n);function n(t){var r;return Object(o.a)(this,n),(r=e.call(this,t)).onChange=function(t){return r.setState(Object(a.a)({},t.target.name,t.target.value))},r.handleSubmit=function(t){t.preventDefault(),Object(f.a)({username:r.state.username,password:r.state.password}).then((function(t){"OK"===t.status?r.context.logIn({node:t.node,token:t.token,id:t.id,theme:t.theme,expires:t.expires,class:t.class}):(document.getElementById("password").value="",r.setState((function(t){return Object(l.a)({},t,{password:""})})))}))},r.state={message:"",username:"username",password:"password"},r}return Object(i.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(f.d)("front").then((function(e){t.setState(e),document.title=e.title}))}},{key:"render",value:function(){return m.a.createElement("div",{className:y.a.loginOverlay},m.a.createElement("article",{className:y.a.login},m.a.createElement("h1",{className:y.a.title},this.state.message),m.a.createElement(w,{style:{float:"left"}},m.a.createElement(h.TextInput,{key:"username",id:"username",onChange:this.onChange}),m.a.createElement(h.PasswordInput,{key:"password",id:"password",onChange:this.onChange})),m.a.createElement("button",{className:y.a.button,onClick:this.handleSubmit,title:"Login"},m.a.createElement("i",{className:"fas fa-sign-in-alt"}))))}}]),n}(s.PureComponent);A.contextType=D},,function(t,e,n){"use strict";n.r(e),n.d(e,"TextLine",(function(){return p})),n.d(e,"StateLine",(function(){return _})),n.d(e,"TextInput",(function(){return v})),n.d(e,"UrlInput",(function(){return g})),n.d(e,"EmailInput",(function(){return b})),n.d(e,"PasswordInput",(function(){return y})),n.d(e,"DateInput",(function(){return E})),n.d(e,"TimeInput",(function(){return k})),n.d(e,"TextAreaInput",(function(){return x})),n.d(e,"CheckboxInput",(function(){return N})),n.d(e,"RadioInput",(function(){return C})),n.d(e,"SelectInput",(function(){return j})),n.d(e,"SearchInput",(function(){return O}));var a=n(3),r=n(4),o=n(5),i=n(6),u=n(0),c=n.n(u),l=n(13),s=n(7),m=n.n(s),f=function(t){return t.label?t.label:t.id},d=function(t,e){return c.a.createElement(u.Fragment,null,c.a.createElement("label",{htmlFor:e.id,title:e.title,className:m.a.label},f(e),":"),c.a.createElement("input",{className:m.a.input,type:t,id:e.id,name:e.id,onChange:e.onChange,value:null!==e.value?e.value:"",placeholder:e.placeholder,title:e.extra,size:e.size}))},h=function(t,e){return c.a.createElement(u.Fragment,null,c.a.createElement("label",{htmlFor:e.id,title:e.title,className:m.a.label},f(e),":"),t)},p=function(t){return h(c.a.createElement("span",{id:t.id,style:t.style,title:t.extra,className:m.a.span},t.text),t)},_=function(t){return h(Object(l.StateLeds)(t),t)},v=function(t){return d("text",t)},g=function(t){return d("url",t)},b=function(t){return d("email",t)},y=function(t){return d("password",t)},E=function(t){return d("date",t)},k=function(t){return d("time",t)},x=function(t){return c.a.createElement(u.Fragment,null,c.a.createElement("label",{htmlFor:t.id,className:m.a.label,title:t.title},f(t),":"),c.a.createElement("textarea",{id:t.id,name:t.id,onChange:t.onChange,className:m.a.textarea,value:t.value}))},N=function(t){return c.a.createElement(u.Fragment,null,c.a.createElement("label",{htmlFor:t.id,className:m.a.label,title:t.title},f(t),":"),c.a.createElement("input",{type:"checkbox",id:t.id,name:t.id,onChange:t.onChange,defaultChecked:t.value,placeholder:t.placeholder,title:t.extra,className:m.a.checkbox}))},C=function(t){return c.a.createElement(u.Fragment,null,c.a.createElement("label",{htmlFor:t.id,className:m.a.label,title:t.title},f(t),":"),c.a.createElement("div",null,t.options.map((function(e,n){return c.a.createElement(u.Fragment,{key:n},c.a.createElement("label",{htmlFor:"radio_input_"+t.id+"_"+n},e.text),c.a.createElement("input",{type:"radio",id:"radio_input_"+t.id+"_"+n,name:t.id,onChange:t.onChange,value:e.value,checked:t.value.toString()===e.value.toString()?"checked":""}))}))))},j=function(t){return c.a.createElement(u.Fragment,null,c.a.createElement("label",{htmlFor:t.id,title:t.title,className:m.a.label},f(t),":"),c.a.createElement("select",{name:t.id,onChange:t.onChange,value:null!==t.value&&void 0!==t.value?t.value:"NULL",className:m.a.input},(null===t.value||void 0===t.value)&&void 0===t.children.find((function(t){return"NULL"===t.props.value}))&&c.a.createElement("option",{value:"NULL"},"<Empty>"),t.children))},O=function(t){Object(i.a)(n,t);var e=Object(o.a)(n);function n(t){var r;return Object(a.a)(this,n),(r=e.call(this,t)).handleCheck=function(){clearTimeout(r.timer),r.timer=setTimeout((function(){return r.props.searchFire(r.state.text)}),500)},r.state={text:r.props.text?r.props.text:""},r.timer=null,r}return Object(r.a)(n,[{key:"componentDidUpdate",value:function(t,e){e.text!==this.state.text&&this.handleCheck(),t.text!==this.props.text&&this.setState({text:this.props.text})}},{key:"componentWillUnmount",value:function(){clearTimeout(this.timer)}},{key:"render",value:function(){var t=this;return c.a.createElement("input",{type:"text",className:m.a.searchfield,onChange:function(e){return t.setState({text:e.target.value})},value:this.state.text,placeholder:this.props.placeholder,autoFocus:!0})}}]),n}(u.PureComponent)},function(t,e,n){"use strict";n.r(e),n.d(e,"NavBar",(function(){return m})),n.d(e,"NavButton",(function(){return f})),n.d(e,"NavDropButton",(function(){return d})),n.d(e,"NavDropDown",(function(){return h})),n.d(e,"NavReload",(function(){return p})),n.d(e,"NavInfo",(function(){return _}));var a=n(3),r=n(4),o=n(5),i=n(6),u=n(0),c=n.n(u),l=n(2),s=n.n(l),m=function(t){return c.a.createElement("nav",{className:s.a.main,id:t.id},c.a.createElement("ul",{className:s.a.list},t.children))},f=function(t){return c.a.createElement("li",{className:s.a.item,style:t.style},c.a.createElement("button",{className:s.a.button,onClick:t.onClick},t.title))},d=function(t){return c.a.createElement("li",{className:s.a.dropDownItem,style:t.style},c.a.createElement("button",{className:s.a.dropbutton,onClick:t.onClick},t.title))},h=function(t){Object(i.a)(n,t);var e=Object(o.a)(n);function n(t){var r;return Object(a.a)(this,n),(r=e.call(this,t)).expandList=function(){return r.setState({height:3*r.props.children.length})},r.implodeList=function(){return r.setState({height:0})},r.state={height:0},r}return Object(r.a)(n,[{key:"render",value:function(){var t=this;return c.a.createElement("li",{className:s.a.item,style:this.props.style,onMouseEnter:function(){return t.expandList()},onMouseLeave:function(){return t.implodeList()}},c.a.createElement("button",{className:s.a.button},this.props.title),c.a.createElement("ul",{className:s.a.dropDownList,style:{maxHeight:"".concat(this.state.height,"rem")}},this.props.children))}}]),n}(u.PureComponent),p=function(t){return c.a.createElement("li",{className:s.a.item,style:t.style},c.a.createElement("button",{className:s.a.button,onClick:t.onClick},c.a.createElement("i",{className:"fas fa-redo-alt",style:{fontSize:"2.1rem"}})))},_=function(t){return c.a.createElement("li",{className:s.a.info,style:t.style},c.a.createElement("button",{className:s.a.infobutton},t.title))}},,,function(t,e,n){"use strict";n.r(e),n.d(e,"HrefButton",(function(){return u})),n.d(e,"HeaderButton",(function(){return c})),n.d(e,"TextButton",(function(){return s})),n.d(e,"AddButton",(function(){return m})),n.d(e,"BackButton",(function(){return f})),n.d(e,"CheckButton",(function(){return d})),n.d(e,"CloseButton",(function(){return h})),n.d(e,"ConfigureButton",(function(){return p})),n.d(e,"DeleteButton",(function(){return _})),n.d(e,"DevicesButton",(function(){return v})),n.d(e,"DocButton",(function(){return g})),n.d(e,"EditButton",(function(){return b})),n.d(e,"FixButton",(function(){return y})),n.d(e,"ForwardButton",(function(){return E})),n.d(e,"GoButton",(function(){return k})),n.d(e,"InfoButton",(function(){return x})),n.d(e,"ItemsButton",(function(){return N})),n.d(e,"LinkButton",(function(){return C})),n.d(e,"LogButton",(function(){return j})),n.d(e,"NetworkButton",(function(){return O})),n.d(e,"PauseButton",(function(){return B})),n.d(e,"ReloadButton",(function(){return S})),n.d(e,"RemoveButton",(function(){return w})),n.d(e,"ReserveButton",(function(){return L})),n.d(e,"RevertButton",(function(){return I})),n.d(e,"SaveButton",(function(){return T})),n.d(e,"SearchButton",(function(){return M})),n.d(e,"ServeButton",(function(){return P})),n.d(e,"ShutdownButton",(function(){return F})),n.d(e,"SnapshotButton",(function(){return D})),n.d(e,"StartButton",(function(){return U})),n.d(e,"StopButton",(function(){return R})),n.d(e,"SyncButton",(function(){return z})),n.d(e,"TermButton",(function(){return A})),n.d(e,"UiButton",(function(){return J})),n.d(e,"UnlinkButton",(function(){return G})),n.d(e,"ViewButton",(function(){return H})),n.d(e,"IpamGreenButton",(function(){return V})),n.d(e,"IpamGreyButton",(function(){return q})),n.d(e,"IpamRedButton",(function(){return W}));var a=n(0),r=n.n(a),o=n(10),i=n.n(o),u=function(t){return r.a.createElement("button",{id:t.id,className:i.a.href,style:t.style,onClick:t.onClick,title:t.title},t.text)},c=function(t){return r.a.createElement("button",{id:t.id,className:i.a.href,style:t.highlight?{color:"var(--high-color)"}:{},onClick:t.onClick,title:t.title},t.text)},l=function(t,e){return r.a.createElement("button",{id:e.id,className:i.a.info,onClick:e.onClick,title:e.title},r.a.createElement("i",{className:t}))},s=function(t){return r.a.createElement("button",{id:t.id,className:i.a.text,onClick:t.onClick,title:t.title},t.text)},m=function(t){return l("fas fa-plus",t)},f=function(t){return l("fas fa-arrow-left",t)},d=function(t){return l("fas fa-tasks",t)},h=function(t){return r.a.createElement("button",{id:t.id,className:i.a.info,style:{float:"right"},onClick:t.onClick,title:t.title},r.a.createElement("i",{className:"fas fa-times-circle"}))},p=function(t){return l("fas fa-cog",t)},_=function(t){return l("fas fa-trash-alt",t)},v=function(t){return l("fas fa-network-wired",t)},g=function(t){return l("fas fa-clipboard-list",t)},b=function(t){return l("fas fa-edit",t)},y=function(t){return l("fas fa-thumbtack",t)},E=function(t){return l("fas fa-arrow-right",t)},k=function(t){return l("fas fa-share-square",t)},x=function(t){return l("fas fa-info",t)},N=function(t){return l("fas fa-list-ul",t)},C=function(t){return l("fas fa-link",t)},j=function(t){return l("fas fa-file-alt",t)},O=function(t){return l("fas fa-share-alt",t)},B=function(t){return l("fas fa-pause",t)},S=function(t){return l("fas fa-redo-alt",t)},w=function(t){return l("fas fa-minus",t)},L=function(t){return l("fas fa-clipboard-check",t)},I=function(t){return l("fas fa-history",t)},T=function(t){return l("fas fa-download",t)},M=function(t){return l("fas fa-search",t)},P=function(t){return l("fas fa-hand-holding",t)},F=function(t){return l("fas fa-power-off",t)},D=function(t){return l("fas fa-camera",t)},U=function(t){return r.a.createElement("button",{id:t.id,className:i.a.info,style:{backgroundColor:"#26CB20"},onClick:t.onClick,title:t.title},r.a.createElement("i",{className:"fas fa-play"}))},R=function(t){return r.a.createElement("button",{id:t.id,className:i.a.info,style:{backgroundColor:"#CB2026"},onClick:t.onClick,title:t.title},r.a.createElement("i",{className:"fas fa-stop"}))},z=function(t){return l("fas fa-exchange-alt",t)},A=function(t){return l("fas fa-terminal",t)},J=function(t){return l("fas fa-globe-americas",t)},G=function(t){return l("fas fa-unlink",t)},H=function(t){return l("fas fa-search-plus",t)},K=function(t,e){return r.a.createElement("button",{id:e.id,className:i.a.ipam,style:{backgroundColor:t},onClick:e.onClick,title:e.title},e.text)},V=function(t){return K("#26CB20",t)},q=function(t){return K("#9CA6B0",t)},W=function(t){return K("#CB2026",t)}},,,,,,function(t,e,n){var a={"./activity.jsx":[44,12],"./console.jsx":[45,13],"./device.jsx":[38,0,2],"./dns.jsx":[46,14],"./fdb.jsx":[42,10],"./hypervisor.jsx":[47,0,11],"./infra/Buttons.jsx":[19],"./infra/Header.jsx":[9],"./infra/Inputs.jsx":[15],"./infra/Navigation.jsx":[16],"./infra/UI.jsx":[13],"./interface.jsx":[40,1],"./inventory.jsx":[48,15],"./ipam.jsx":[43,3],"./location.jsx":[41,4],"./multimedia.jsx":[49,16],"./node.jsx":[50,17],"./pdu.jsx":[51,18],"./rack.jsx":[52,0,9],"./reservation.jsx":[53,19],"./resource.jsx":[54,20],"./server.jsx":[55,21],"./system.jsx":[56,22],"./user.jsx":[57,23],"./visualize.jsx":[39,24]};function r(t){if(!n.o(a,t))return Promise.resolve().then((function(){var e=new Error("Cannot find module '"+t+"'");throw e.code="MODULE_NOT_FOUND",e}));var e=a[t],r=e[0];return Promise.all(e.slice(1).map(n.e)).then((function(){return n(r)}))}r.keys=function(){return Object.keys(a)},r.id=25,t.exports=r},function(t,e,n){t.exports=n(37)},,,,,,,,,,,function(t,e,n){"use strict";n.r(e);var a=n(14),r=n(3),o=n(4),i=n(5),u=n(6),c=n(0),l=n.n(c),s=n(24),m=n.n(s),f=n(12),d=n(13);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));n(32),n(36);"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(t){t.unregister()})).catch((function(t){console.error(t.message)}));var h=function(t){Object(u.a)(n,t);var e=Object(i.a)(n);function n(t){var a;Object(r.a)(this,n),(a=e.call(this,t)).changeTheme=function(t){document.cookie="rims_theme="+t+"; Path=/; expires="+a.state.expires+"; Path=/",a.setState({theme:t})},a.logOut=function(){Object(f.a)({destroy:a.state.token,id:a.state.id}),document.cookie="rims=; Path=/; SameSite=Lax; expires=Thu, 01 Jan 1970 00:00:00 UTC",document.cookie="rims_theme=; Path=/; SameSite=Lax; expires=Thu, 01 Jan 1970 00:00:00 UTC",document.documentElement.removeAttribute("style"),a.setState({token:null})},a.logIn=function(t){document.cookie="rims="+t.token+"; expires="+t.expires+"; Path=/; SameSite=Lax",document.cookie="rims_theme="+t.theme+"; expires="+t.expires+"; Path=/; SameSite=Lax",a.setState(t)},a.providerMounting=function(t){Object.assign(a.provider,t),a.forceUpdate()},a.state={token:null,theme:void 0};for(var o=document.cookie.split("; "),i=0;i<o.length;i++){var u=o[i];0===u.indexOf("rims=")&&(a.state.token=u.substring(5,u.length)),0===u.indexOf("rims_theme=")&&(a.state.theme=u.substring(11,u.length))}return a.provider={},a}return Object(o.a)(n,[{key:"componentDidMount",value:function(){var t=this;this.state.token&&Object(f.a)({verify:this.state.token}).then((function(e){"OK"===e.status?t.setState({node:e.node,token:e.token,id:e.id,expires:e.expires,class:e.class}):t.setState({token:null})}))}},{key:"render",value:function(){return l.a.createElement(d.RimsContext.Provider,{value:Object(a.a)({settings:this.state,logIn:this.logIn,logOut:this.logOut,changeTheme:this.changeTheme},this.provider)},null===this.state.token?l.a.createElement(d.Login,null):l.a.createElement(d.Portal,{providerMounting:this.providerMounting}))}}]),n}(c.Component);m.a.render(l.a.createElement(h,null),document.getElementById("root"))}],[[26,7,8]]]);
//# sourceMappingURL=main.88bb0ec8.chunk.js.map