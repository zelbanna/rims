(this.webpackJsonprims=this.webpackJsonprims||[]).push([[6],[,function(t,e,n){t.exports={main:"ui_main__Nm6EJ",contentLeft:"ui_contentLeft__2Bm6X",contentRight:"ui_contentRight__70N1v",info:"ui_info__pwNpV",code:"ui_code__1c759",events:"ui_events__273Af",network:"ui_network__37LD6",frame:"ui_frame__Rp5Sl",loginOverlay:"ui_loginOverlay__2v5hY",login:"ui_login__u3QHE",title:"ui_title__1MpeV",button:"ui_button__10mcD",article:"ui_article__3eH2m",line:"ui_line__3qKyb",error:"ui_error__2ZDnv",stateLeds:"ui_stateLeds__K2qKU",stateRed:"ui_stateRed__3t9pN",stateGreen:"ui_stateGreen__2mPty",stateGrey:"ui_stateGrey__3vf6a",stateOrange:"ui_stateOrange__1M4su",flex:"ui_flex__2CIpQ",columns:"ui_columns__3g2gt",infoform:"ui_infoform__1QOyG",result:"ui_result__ITMWk",href:"ui_href__gTjt9",graphs:"ui_graphs__2kR20",spinOverlay:"ui_spinOverlay__23tkJ",loader:"ui_loader__1JPkE",bubbles:"ui_bubbles__F4edm"}},function(t,e,n){t.exports={auto:"input_auto___2ud0",fixed:"input_fixed__24oNM",input:"input_input__2GEr3",checkbox:"input_checkbox__GILWd",span:"input_span__1jy_2",textarea:"input_textarea__JHJUJ",searchfield:"input_searchfield__VUedh",search:"input_search__1FFp5"}},,function(t,e,n){t.exports={button:"navigation_button__20Y3k",infobutton:"navigation_infobutton__1NhUX",dropbutton:"navigation_dropbutton__3q87W",main:"navigation_main__1-9J7",list:"navigation_list__3hOPY",item:"navigation_item__3bTNw",dropDownList:"navigation_dropDownList__wyKh9",dropDownItem:"navigation_dropDownItem__1A9q9",info:"navigation_info__6fuVI"}},,,,,function(t,e,n){t.exports={report:"table_report__VRtLp",list:"table_list__2S89B",title:"table_title__1Nt5y",table:"table_table__LqYKC",thead:"table_thead__39Nm6",tbody:"table_tbody__22fLN",trow:"table_trow__1Ih1w",th:"table_th__3x2Cn",td:"table_td__2fabh"}},,function(t,e,n){"use strict";n.r(e),n.d(e,"MenuButton",(function(){return d})),n.d(e,"MenuSeparator",(function(){return f})),n.d(e,"HeaderButton",(function(){return h})),n.d(e,"Header",(function(){return m}));var r=n(5),a=n(6),i=n(8),o=n(7),u=n(3),s=n(13),c=n.n(s),l=n(0),d=function(t){return Object(l.jsx)("li",{className:c.a.menuItem,children:Object(l.jsx)("button",{className:c.a.menuButton,onClick:t.onClick,children:t.title})})},f=function(t){return Object(l.jsx)("li",{className:c.a.menuSeparator})},h=function(t){return Object(l.jsx)("button",{className:c.a.button,onClick:t.onClick,title:t.title,children:Object(l.jsx)("i",{className:t.type,style:t.style})})},m=function(t){Object(i.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).implodeMenu=function(){a.state.height>0&&a.setState({height:0})},a.toggleMenu=function(){0===a.state.height?a.setState({height:2.8*a.props.children.length}):a.setState({height:0})},a.zoomTxt=function(){var t=window.getComputedStyle(document.documentElement).fontSize.replace("px","");a.state.zoom?document.documentElement.style.removeProperty("font-size"):document.documentElement.style.setProperty("font-size","".concat(1.2*t,"px")),a.setState({zoom:!a.state.zoom})},a.state={height:0,zoom:""!==document.documentElement.style.getPropertyValue("font-size")},a}return Object(a.a)(n,[{key:"render",value:function(){var t=this;return Object(l.jsxs)("header",{className:c.a.header,children:[Object(l.jsx)("h1",{className:c.a.title,children:this.props.title}),Object(l.jsx)(h,{onClick:function(){return t.zoomTxt()},title:"Zoom",type:this.state.zoom?"fas fa-search-minus":"fas fa-search-plus"},"zoom_"+this.state.zoom),Object(l.jsxs)("div",{className:c.a.menu,onMouseLeave:function(){return t.implodeMenu()},children:[Object(l.jsx)(h,{onClick:function(){return t.toggleMenu()},title:"Menu",type:"fas fa-bars",style:{transform:0===this.state.height?"rotate(0deg)":"rotate(90deg)"}},"menu_"+this.state.height),Object(l.jsx)("ul",{className:c.a.menuList,style:{maxHeight:"".concat(this.state.height,"rem")},children:this.props.children})]}),Object(l.jsx)(h,{onClick:this.props.logOut,title:"Log out",type:"fas fa-sign-out-alt"},"logout")]})}}]),n}(u.PureComponent)},function(t,e,n){t.exports={href:"button_href__3AdJ5",text:"button_text__2sVk2",info:"button_info__3n4TT",ipam:"button_ipam__1jKFF"}},function(t,e,n){t.exports={title:"header_title__gcejv",menuList:"header_menuList__37hpH",header:"header_header__YZ1S7",button:"header_button__2QI3b","head-button":"header_head-button__1hFin",menu:"header_menu__373a7",menuItem:"header_menuItem__1i0sO",menuButton:"header_menuButton__2FQM0","menu-button":"header_menu-button__2LUKk",menuSeparator:"header_menuSeparator__2PIuq"}},function(t,e,n){"use strict";n.d(e,"d",(function(){return u})),n.d(e,"a",(function(){return c})),n.d(e,"e",(function(){return d})),n.d(e,"b",(function(){return f})),n.d(e,"c",(function(){return h}));var r=n(18),a=n.n(r),i=n(10),o=n(23);function u(){return s.apply(this,arguments)}function s(){return(s=Object(o.a)(a.a.mark((function t(){var e,n,r,o,u=arguments;return a.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=u.length>0&&void 0!==u[0]?u[0]:"",n=u.length>1&&void 0!==u[1]?u[1]:{},r=u.length>2&&void 0!==u[2]?u[2]:{},t.next=5,fetch(e,{method:"POST",headers:Object(i.a)({"Content-Type":"application/json"},r),credentials:"include",body:JSON.stringify(n)});case 5:return o=t.sent,t.next=8,o.json();case 8:return t.abrupt("return",t.sent);case 9:case"end":return t.stop()}}),t)})))).apply(this,arguments)}function c(){return l.apply(this,arguments)}function l(){return(l=Object(o.a)(a.a.mark((function t(){var e,n,r=arguments;return a.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=r.length>0&&void 0!==r[0]?r[0]:{},t.next=3,fetch("auth",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(e)});case 3:return n=t.sent,t.next=6,n.json();case 6:return t.abrupt("return",t.sent);case 7:case"end":return t.stop()}}),t)})))).apply(this,arguments)}var d=function(){return Math.floor(10*Math.random())},f=function(t){return(t>>24&255)+"."+(t>>16&255)+"."+(t>>8&255)+"."+(255&t)},h=function(t){return t.split(".").reduce((function(t,e){return+e+(t<<8)}),0)>>>0}},function(t,e,n){"use strict";n.r(e),n.d(e,"Title",(function(){return g})),n.d(e,"Flex",(function(){return y})),n.d(e,"Spinner",(function(){return N})),n.d(e,"StateLeds",(function(){return C})),n.d(e,"Article",(function(){return S})),n.d(e,"LineArticle",(function(){return B})),n.d(e,"CodeArticle",(function(){return w})),n.d(e,"InfoArticle",(function(){return I})),n.d(e,"InfoColumns",(function(){return L})),n.d(e,"Result",(function(){return T})),n.d(e,"Row",(function(){return F})),n.d(e,"ContentList",(function(){return M})),n.d(e,"ContentReport",(function(){return P})),n.d(e,"ContentData",(function(){return D})),n.d(e,"RimsContext",(function(){return E})),n.d(e,"Portal",(function(){return A})),n.d(e,"Login",(function(){return J}));var r=n(19),a=n(5),i=n(6),o=n(8),u=n(7),s=n(20),c=n(10),l=n(3),d=n.n(l),f=n(14),h=n(21),m=n(16),j=n(11),b=n(17),p=n(9),x=n.n(p),_=n(1),O=n.n(_),v=n(0),g=function(t){return Object(v.jsx)("h1",{className:O.a.title,children:t.text})},y=function(t){return Object(v.jsx)("div",{className:O.a.flex,style:t.style,children:t.children})},N=function(){return Object(v.jsx)("div",{className:O.a.spinOverlay,children:Object(v.jsx)("div",{className:O.a.loader})})},k=function(t){return Object(v.jsx)("div",{className:{on:O.a.stateGreen,off:O.a.stateRed,unknown:O.a.stateGrey,up:O.a.stateGreen,down:O.a.stateRed,undefined:O.a.stateOrange,null:O.a.stateOrange}[t.state]||O.a.stateOrange,title:t.state})},C=function(t){return Object(v.jsx)("div",{title:t.title,className:O.a.stateLeds,children:Array.isArray(t.state)?t.state.map((function(t,e){return Object(v.jsx)(k,{state:t},e)})):Object(v.jsx)(k,{state:t.state},"led")})},S=function(t){return Object(v.jsxs)("article",{className:O.a.article,children:[Object(v.jsx)("h1",{className:O.a.title,children:t.header}),t.children]})},B=function(t){return Object(v.jsxs)("article",{className:O.a.line,children:[Object(v.jsx)("h1",{className:O.a.title,children:t.header}),t.children]})},w=function(t){return Object(v.jsxs)("article",{className:O.a.code,children:[Object(v.jsx)("h1",{className:O.a.title,children:t.header}),t.children]})},I=function(t){return Object(v.jsxs)("article",{className:O.a.info,children:[Object(v.jsx)("h1",{className:O.a.title,children:t.header}),t.children]})},L=function(t){var e=["max-content","auto"];if(t.columns>2)for(var n=2;n<t.columns;n++)e.push(n%2===0?"max-content":"auto");return Object(v.jsx)("form",{className:O.a.infoform,children:Object(v.jsx)("div",{className:O.a.columns,style:Object(c.a)({gridTemplateColumns:e.join(" ")},t.style),children:t.children})})};L.defaultProps={columns:2};var T=function(t){return Object(v.jsx)("span",{className:O.a.result,children:t.result})},F=function(t){return Object(v.jsx)("div",{className:x.a.trow,children:t.cells.map((function(t,e){return Object(v.jsx)("div",{className:x.a.td,children:t},e)}))})},M=function(t){return Object(v.jsx)("section",{className:O.a.contentLeft,children:U(x.a.list,t)})},P=function(t){return U(x.a.report,t)},D=function(t){var e=Object(l.useState)(null),n=Object(s.a)(e,2),r=n[0],a=n[1];return t.mountUpdate(a),Object(v.jsx)("section",{className:O.a.contentRight,children:r})},U=function(t,e){return e.trows?Object(v.jsxs)("article",{className:t,children:[Object(v.jsx)("h1",{className:x.a.title,children:e.header}),e.children,Object(v.jsx)(T,{result:e.result},"result"),Object(v.jsxs)("div",{className:x.a.table,children:[Object(v.jsx)("div",{className:x.a.thead,children:e.thead.map((function(t,e){return Object(v.jsx)("div",{className:x.a.th,children:t},e)}))}),Object(v.jsx)("div",{className:x.a.tbody,children:e.trows.map((function(t,n){return Object(v.jsx)(F,{cells:e.listItem(t,n)},n)}))})]})]}):Object(v.jsx)(N,{})},E=Object(l.createContext)({settings:null,logIn:function(){},logOut:function(){},changeMain:function(){},loadNavigtion:function(){},changeTheme:function(){}});E.displayName="RimsContext";var z=function(t){Object(o.a)(n,t);var e=Object(u.a)(n);function n(t){var r;return Object(a.a)(this,n),(r=e.call(this,t)).state={hasError:!1,error:void 0,info:[]},r}return Object(i.a)(n,[{key:"componentDidCatch",value:function(t,e){this.setState({error:t.toString(),info:e.componentStack.split("\n")})}},{key:"render",value:function(){var t=this;return this.state.hasError?Object(v.jsx)("div",{className:O.a.overlay,style:{top:0},children:Object(v.jsxs)("article",{className:O.a.error,children:[Object(v.jsx)(h.CloseButton,{onClick:function(){return t.setState({hasError:!1,error:void 0,info:[]})}},"close"),Object(v.jsx)("h1",{className:O.a.title,children:"UI Error"}),Object(v.jsxs)(L,{children:[Object(v.jsx)(m.TextLine,{id:"type",text:this.state.error,onChange:function(){}},"type"),Object(v.jsx)(m.TextAreaInput,{id:"info",value:this.state.info.join("\n"),onChange:function(){}},"text")]},"ic")]})}):this.props.children}}],[{key:"getDerivedStateFromError",value:function(t){return{hasError:!0}}}]),n}(d.a.Component),R=function(t){Object(o.a)(n,t);var e=Object(u.a)(n);function n(){var t;Object(a.a)(this,n);for(var r=arguments.length,i=new Array(r),o=0;o<r;o++)i[o]=arguments[o];return(t=e.call.apply(e,[this].concat(i))).loadTheme=function(t){Object(f.d)("api/portal/theme_info",{theme:t}).then((function(t){if(t&&"OK"===t.status)for(var e=0,n=Object.entries(t.data);e<n.length;e++){var r=Object(s.a)(n[e],2),a=r[0],i=r[1];document.documentElement.style.setProperty(a,i)}}))},t}return Object(i.a)(n,[{key:"componentDidMount",value:function(){this.loadTheme(this.props.theme)}},{key:"componentDidUpdate",value:function(t){t.theme!==this.props.theme&&this.loadTheme(this.props.theme)}},{key:"render",value:function(){return Object(v.jsx)(d.a.Fragment,{})}}]),n}(l.Component),A=function(t){Object(o.a)(r,t);var e=Object(u.a)(r);function r(t){var i;return Object(a.a)(this,r),(i=e.call(this,t)).loadNavigation=function(t){return i.setState({navigation:t})},i.changeContent=function(t){if(t.hasOwnProperty("module"))try{n(25)("./"+t.module+".jsx").then((function(e){var n=e[t.function];i.setState({navigation:Object(v.jsx)(b.NavBar,{},"portal_navigation"),content:Object(v.jsx)(n,Object(c.a)({},t.args),t.module+"_"+t.function)})}))}catch(e){console.error("Mapper error: "+t),alert(e)}else i.setState({navigation:Object(v.jsx)(b.NavBar,{},"portal_navigation"),content:t})},i.state={menu:[],navigation:Object(v.jsx)(b.NavBar,{},"portal_navigation_empty")},i}return Object(i.a)(r,[{key:"componentDidMount",value:function(){var t=this;this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation}),Object(f.d)("api/portal/menu",{id:this.context.settings.id}).then((function(e){if(e&&"OK"===e.status){var n=e.data;t.setState(n),n.start&&t.changeContent(n.menu[n.start]),document.title=n.title}}))}},{key:"render",value:function(){for(var t=this,e=[],n=function(){var n=Object(s.a)(a[r],2),i=n[0],o=n[1];"module"===o.type?e.push(Object(v.jsx)(j.MenuButton,{title:i,onClick:function(){return t.changeContent(o)}},i)):"tab"===o.type?e.push(Object(v.jsx)(j.MenuButton,{title:i,onClick:function(){return window.open(o.tab,"_blank")}},i)):"frame"===o.type&&e.push(Object(v.jsx)(j.MenuButton,{title:i,onClick:function(){return t.changeContent(Object(v.jsx)("iframe",{className:O.a.frame,title:i,src:o.frame}))}},i))},r=0,a=Object.entries(this.state.menu);r<a.length;r++)n();return e.push(Object(v.jsx)(j.MenuSeparator,{},"hs_1"),Object(v.jsx)(j.MenuButton,{title:"User",onClick:function(){return t.changeContent({module:"user",function:"User",args:{id:t.context.settings.id}})}},"user_info"),Object(v.jsx)(j.MenuButton,{title:"System",onClick:function(){return t.changeContent({module:"system",function:"Main"})}},"system")),Object(v.jsxs)(v.Fragment,{children:[Object(v.jsx)(R,{theme:this.context.settings.theme},"portal_theme"),Object(v.jsx)(j.Header,{title:this.state.title,logOut:function(){return t.context.logOut()},children:e},"portal_header"),this.state.navigation,Object(v.jsx)(z,{children:Object(v.jsx)("main",{className:O.a.main,children:this.state.content})},"portal_error")]})}}]),r}(l.Component);A.contextType=E;var J=function(t){Object(o.a)(n,t);var e=Object(u.a)(n);function n(t){var i;return Object(a.a)(this,n),(i=e.call(this,t)).onChange=function(t){return i.setState(Object(r.a)({},t.target.name,t.target.value))},i.handleSubmit=function(t){t.preventDefault(),Object(f.a)({username:i.state.username,password:i.state.password}).then((function(t){"OK"===t.status?i.context.logIn({node:t.node,token:t.token,id:t.id,theme:t.theme,expires:t.expires,class:t.class}):(document.getElementById("password").value="",i.setState((function(t){return Object(c.a)(Object(c.a)({},t),{},{password:""})})))}))},i.state={message:"",username:"username",password:"password"},i}return Object(i.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(f.d)("front").then((function(e){t.setState(e),document.title=e.title}))}},{key:"render",value:function(){return Object(v.jsx)("div",{className:O.a.loginOverlay,children:Object(v.jsxs)("article",{className:O.a.login,children:[Object(v.jsx)("h1",{className:O.a.title,children:this.state.message}),Object(v.jsxs)(L,{style:{float:"left"},children:[Object(v.jsx)(m.UsernameInput,{id:"username",onChange:this.onChange},"username"),Object(v.jsx)(m.PasswordInput,{id:"password",onChange:this.onChange},"password")]}),Object(v.jsx)("button",{className:O.a.button,onClick:this.handleSubmit,title:"Login",children:Object(v.jsx)("i",{className:"fas fa-sign-in-alt"})})]})})}}]),n}(l.PureComponent);J.contextType=E},function(t,e,n){"use strict";n.r(e),n.d(e,"TextLine",(function(){return j})),n.d(e,"StateLine",(function(){return b})),n.d(e,"SearchInput",(function(){return p})),n.d(e,"TextInput",(function(){return x})),n.d(e,"UrlInput",(function(){return _})),n.d(e,"EmailInput",(function(){return O})),n.d(e,"DateInput",(function(){return v})),n.d(e,"TimeInput",(function(){return g})),n.d(e,"UsernameInput",(function(){return y})),n.d(e,"PasswordInput",(function(){return N})),n.d(e,"TextAreaInput",(function(){return k})),n.d(e,"CheckboxInput",(function(){return C})),n.d(e,"RadioInput",(function(){return S})),n.d(e,"SelectInput",(function(){return B})),n.d(e,"SearchField",(function(){return w}));var r=n(5),a=n(6),i=n(8),o=n(7),u=n(3),s=n(15),c=n(2),l=n.n(c),d=n(0),f=function(t){return t.label?t.label:t.id},h=function(t,e){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:e.id,title:e.title,className:e.label?l.a.fixed:l.a.auto,children:[f(e),":"]}),Object(d.jsx)("input",{className:l.a.input,type:t,id:e.id,name:e.id,onChange:e.onChange,value:null!==e.value?e.value:"",placeholder:e.placeholder,title:e.extra,size:e.size})]})},m=function(t,e){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:e.id,title:e.title,className:e.label?l.a.fixed:l.a.auto,children:[f(e),":"]}),t]})},j=function(t){return m(Object(d.jsx)("span",{id:t.id,style:t.style,title:t.extra,className:l.a.span,children:t.text}),t)},b=function(t){return m(Object(s.StateLeds)(t),t)},p=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,title:t.title,className:t.label?l.a.fixed:l.a.auto,children:[f(t),":"]}),Object(d.jsx)("input",{className:l.a.search,type:"text",id:t.id,name:t.id,onChange:t.onChange,value:null!==t.value?t.value:"",placeholder:t.placeholder,title:t.extra,size:t.size})]})},x=function(t){return h("text",t)},_=function(t){return h("url",t)},O=function(t){return h("email",t)},v=function(t){return h("date",t)},g=function(t){return h("time",t)},y=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,className:t.label?l.a.fixed:l.a.auto,title:t.title,children:[f(t),":"]}),Object(d.jsx)("input",{type:"text",className:l.a.input,id:t.id,name:t.id,onChange:t.onChange,value:null!==t.value?t.value:"",size:t.size,autoComplete:"username"})]})},N=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,className:t.label?l.a.fixed:l.a.auto,title:t.title,children:[f(t),":"]}),Object(d.jsx)("input",{type:"password",className:l.a.input,id:t.id,name:t.id,onChange:t.onChange,value:null!==t.value?t.value:"",size:t.size,autoComplete:"current-password"})]})},k=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,className:t.label?l.a.fixed:l.a.auto,title:t.title,children:[f(t),":"]}),Object(d.jsx)("textarea",{id:t.id,name:t.id,onChange:t.onChange,className:l.a.textarea,value:t.value})]})},C=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,className:t.label?l.a.fixed:l.a.auto,title:t.title,children:[f(t),":"]}),Object(d.jsx)("input",{type:"checkbox",id:t.id,name:t.id,onChange:t.onChange,defaultChecked:t.value,placeholder:t.placeholder,title:t.extra,className:l.a.checkbox})]})},S=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,className:t.label?l.a.fixed:l.a.auto,title:t.title,children:[f(t),":"]}),Object(d.jsx)("div",{children:t.options.map((function(e,n){return Object(d.jsxs)(u.Fragment,{children:[Object(d.jsx)("label",{htmlFor:"ri_"+t.id+"_"+n,children:e.text}),Object(d.jsx)("input",{type:"radio",id:"ri_"+t.id+"_"+n,name:t.id,onChange:t.onChange,value:e.value,checked:t.value.toString()===e.value.toString()?"checked":""})]},n)}))})]})},B=function(t){return Object(d.jsxs)(d.Fragment,{children:[Object(d.jsxs)("label",{htmlFor:t.id,title:t.title,className:t.label?l.a.fixed:l.a.auto,children:[f(t),":"]}),Object(d.jsxs)("select",{name:t.id,onChange:t.onChange,value:null!==t.value&&void 0!==t.value?t.value:"NULL",className:l.a.input,children:[(null===t.value||void 0===t.value)&&void 0===t.children.find((function(t){return"NULL"===t.props.value}))&&Object(d.jsx)("option",{value:"NULL",children:"<Empty>"}),t.children]})]})},w=function(t){Object(i.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).handleInput=function(){clearTimeout(a.timer),a.timer=setTimeout((function(){return a.props.searchFire(a.state.text)}),400)},a.state={text:a.props.text?a.props.text:""},a.timer=null,a}return Object(a.a)(n,[{key:"componentDidUpdate",value:function(t,e){e.text!==this.state.text&&this.handleInput(),t.text!==this.props.text&&this.setState({text:this.props.text})}},{key:"componentWillUnmount",value:function(){clearTimeout(this.timer)}},{key:"render",value:function(){var t=this;return Object(d.jsx)("input",{type:"search",results:"5",className:l.a.searchfield,onChange:function(e){return t.setState({text:e.target.value})},value:this.state.text,placeholder:this.props.placeholder,autoFocus:!0})}}]),n}(u.PureComponent)},function(t,e,n){"use strict";n.r(e),n.d(e,"NavBar",(function(){return d})),n.d(e,"NavButton",(function(){return f})),n.d(e,"NavDropButton",(function(){return h})),n.d(e,"NavDropDown",(function(){return m})),n.d(e,"NavReload",(function(){return j})),n.d(e,"NavInfo",(function(){return b}));var r=n(5),a=n(6),i=n(8),o=n(7),u=n(3),s=n(4),c=n.n(s),l=n(0),d=function(t){return Object(l.jsx)("nav",{className:c.a.main,id:t.id,children:Object(l.jsx)("ul",{className:c.a.list,children:t.children})})},f=function(t){return Object(l.jsx)("li",{className:c.a.item,style:t.style,children:Object(l.jsx)("button",{className:c.a.button,onClick:t.onClick,children:t.title})})},h=function(t){return Object(l.jsx)("li",{className:c.a.dropDownItem,style:t.style,children:Object(l.jsx)("button",{className:c.a.dropbutton,onClick:t.onClick,children:t.title})})},m=function(t){Object(i.a)(n,t);var e=Object(o.a)(n);function n(t){var a;return Object(r.a)(this,n),(a=e.call(this,t)).expandList=function(){return a.setState({height:3*a.props.children.length})},a.implodeList=function(){return a.setState({height:0})},a.state={height:0},a}return Object(a.a)(n,[{key:"render",value:function(){var t=this;return Object(l.jsxs)("li",{className:c.a.item,style:this.props.style,onMouseEnter:function(){return t.expandList()},onMouseLeave:function(){return t.implodeList()},children:[Object(l.jsx)("button",{className:c.a.button,children:this.props.title}),Object(l.jsx)("ul",{className:c.a.dropDownList,style:{maxHeight:"".concat(this.state.height,"rem")},children:this.props.children})]})}}]),n}(u.PureComponent),j=function(t){return Object(l.jsx)("li",{className:c.a.item,style:t.style,children:Object(l.jsx)("button",{className:c.a.button,onClick:t.onClick,children:Object(l.jsx)("i",{className:"fas fa-redo-alt",style:{fontSize:"2.1rem"}})})})},b=function(t){return Object(l.jsx)("li",{className:c.a.info,style:t.style,children:Object(l.jsx)("button",{className:c.a.infobutton,children:t.title})})}},,,,function(t,e,n){"use strict";n.r(e),n.d(e,"HrefButton",(function(){return o})),n.d(e,"HeaderButton",(function(){return u})),n.d(e,"TextButton",(function(){return c})),n.d(e,"AddButton",(function(){return l})),n.d(e,"BackButton",(function(){return d})),n.d(e,"CheckButton",(function(){return f})),n.d(e,"CloseButton",(function(){return h})),n.d(e,"ConfigureButton",(function(){return m})),n.d(e,"DeleteButton",(function(){return j})),n.d(e,"DevicesButton",(function(){return b})),n.d(e,"DocButton",(function(){return p})),n.d(e,"EditButton",(function(){return x})),n.d(e,"FixButton",(function(){return _})),n.d(e,"ForwardButton",(function(){return O})),n.d(e,"GoButton",(function(){return v})),n.d(e,"HealthButton",(function(){return g})),n.d(e,"InfoButton",(function(){return y})),n.d(e,"ItemsButton",(function(){return N})),n.d(e,"LinkButton",(function(){return k})),n.d(e,"LogButton",(function(){return C})),n.d(e,"NetworkButton",(function(){return S})),n.d(e,"PauseButton",(function(){return B})),n.d(e,"ReloadButton",(function(){return w})),n.d(e,"RemoveButton",(function(){return I})),n.d(e,"ReserveButton",(function(){return L})),n.d(e,"RevertButton",(function(){return T})),n.d(e,"SaveButton",(function(){return F})),n.d(e,"SearchButton",(function(){return M})),n.d(e,"ServeButton",(function(){return P})),n.d(e,"ShutdownButton",(function(){return D})),n.d(e,"SnapshotButton",(function(){return U})),n.d(e,"StartButton",(function(){return E})),n.d(e,"StopButton",(function(){return z})),n.d(e,"SyncButton",(function(){return R})),n.d(e,"TermButton",(function(){return A})),n.d(e,"TimeButton",(function(){return J})),n.d(e,"UiButton",(function(){return G})),n.d(e,"UnlinkButton",(function(){return H})),n.d(e,"ViewButton",(function(){return K})),n.d(e,"IpamGreenButton",(function(){return q})),n.d(e,"IpamGreyButton",(function(){return W})),n.d(e,"IpamRedButton",(function(){return Q}));n(3);var r=n(12),a=n.n(r),i=n(0),o=function(t){return Object(i.jsx)("button",{id:t.id,type:"button",className:a.a.href,style:t.style,onClick:t.onClick,title:t.title,children:t.text})},u=function(t){return Object(i.jsx)("button",{id:t.id,type:"button",className:a.a.href,style:t.highlight?{color:"var(--high-color)"}:{},onClick:t.onClick,title:t.title,children:t.text})},s=function(t,e){return Object(i.jsx)("button",{id:e.id,type:"button",className:a.a.info,onClick:e.onClick,title:e.title,children:Object(i.jsx)("i",{className:t})})},c=function(t){return Object(i.jsx)("button",{id:t.id,type:"button",className:a.a.text,onClick:t.onClick,title:t.title,children:t.text})},l=function(t){return s("fas fa-plus",t)},d=function(t){return s("fas fa-arrow-left",t)},f=function(t){return s("fas fa-tasks",t)},h=function(t){return Object(i.jsx)("button",{id:t.id,type:"button",className:a.a.info,style:{float:"right"},onClick:t.onClick,title:t.title,children:Object(i.jsx)("i",{className:"fas fa-times-circle"})})},m=function(t){return s("fas fa-cog",t)},j=function(t){return s("fas fa-trash-alt",t)},b=function(t){return s("fas fa-network-wired",t)},p=function(t){return s("fas fa-clipboard-list",t)},x=function(t){return s("fas fa-edit",t)},_=function(t){return s("fas fa-thumbtack",t)},O=function(t){return s("fas fa-arrow-right",t)},v=function(t){return s("fas fa-share-square",t)},g=function(t){return s("fas fa-file-medical-alt",t)},y=function(t){return s("fas fa-info",t)},N=function(t){return s("fas fa-list-ul",t)},k=function(t){return s("fas fa-link",t)},C=function(t){return s("fas fa-file-alt",t)},S=function(t){return s("fas fa-share-alt",t)},B=function(t){return s("fas fa-pause",t)},w=function(t){return s("fas fa-redo-alt",t)},I=function(t){return s("fas fa-minus",t)},L=function(t){return s("fas fa-clipboard-check",t)},T=function(t){return s("fas fa-history",t)},F=function(t){return s("fas fa-download",t)},M=function(t){return s("fas fa-search",t)},P=function(t){return s("fas fa-hand-holding",t)},D=function(t){return s("fas fa-power-off",t)},U=function(t){return s("fas fa-camera",t)},E=function(t){return Object(i.jsx)("button",{id:t.id,type:"button",className:a.a.info,style:{backgroundColor:"#26CB20"},onClick:t.onClick,title:t.title,children:Object(i.jsx)("i",{className:"fas fa-play"})})},z=function(t){return Object(i.jsx)("button",{id:t.id,type:"button",className:a.a.info,style:{backgroundColor:"#CB2026"},onClick:t.onClick,title:t.title,children:Object(i.jsx)("i",{className:"fas fa-stop"})})},R=function(t){return s("fas fa-exchange-alt",t)},A=function(t){return s("fas fa-terminal",t)},J=function(t){return s("fas fa-clock",t)},G=function(t){return s("fas fa-globe-americas",t)},H=function(t){return s("fas fa-unlink",t)},K=function(t){return s("fas fa-search-plus",t)},V=function(t,e){return Object(i.jsx)("button",{id:e.id,type:"button",className:a.a.ipam,style:{backgroundColor:t},onClick:e.onClick,title:e.title,children:e.text})},q=function(t){return V("#26CB20",t)},W=function(t){return V("#9CA6B0",t)},Q=function(t){return V("#CB2026",t)}},,,,function(t,e,n){var r={"./activity.jsx":[41,11],"./console.jsx":[42,12],"./device.jsx":[35,0],"./dns.jsx":[43,13],"./fdb.jsx":[39,14],"./hypervisor.jsx":[44,0,15],"./infra/Buttons.jsx":[21],"./infra/Header.jsx":[11],"./infra/Inputs.jsx":[16],"./infra/Navigation.jsx":[17],"./infra/UI.jsx":[15],"./interface.jsx":[36,1],"./inventory.jsx":[45,16],"./ipam.jsx":[40,3],"./location.jsx":[37,5],"./multimedia.jsx":[46,17],"./node.jsx":[47,18],"./pdu.jsx":[48,19],"./rack.jsx":[49,0,9],"./reservation.jsx":[50,20],"./resource.jsx":[51,21],"./server.jsx":[52,22],"./system.jsx":[53,23],"./user.jsx":[54,24],"./visualize.jsx":[38,4]};function a(t){if(!n.o(r,t))return Promise.resolve().then((function(){var e=new Error("Cannot find module '"+t+"'");throw e.code="MODULE_NOT_FOUND",e}));var e=r[t],a=e[0];return Promise.all(e.slice(1).map(n.e)).then((function(){return n(a)}))}a.keys=function(){return Object.keys(r)},a.id=25,t.exports=a},,,,,,,,,function(t,e,n){"use strict";n.r(e);var r=n(10),a=n(5),i=n(6),o=n(8),u=n(7),s=n(3),c=n(24),l=n.n(c),d=n(14),f=n(15);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));n(32),n(33);var h=n(0);"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(t){t.unregister()})).catch((function(t){console.error(t.message)}));var m=function(t){Object(o.a)(n,t);var e=Object(u.a)(n);function n(t){var r;Object(a.a)(this,n),(r=e.call(this,t)).changeTheme=function(t){document.cookie="rims_theme="+t+"; Path=/; expires="+r.state.expires+"; Path=/",r.setState({theme:t})},r.logOut=function(){Object(d.a)({destroy:r.state.token,id:r.state.id}),document.cookie="rims=; Path=/; SameSite=Strict; expires=Thu, 01 Jan 1970 00:00:00 UTC",document.cookie="rims_theme=; Path=/; SameSite=Strict; expires=Thu, 01 Jan 1970 00:00:00 UTC",document.documentElement.removeAttribute("style"),r.setState({token:null})},r.logIn=function(t){document.cookie="rims="+t.token+"; expires="+t.expires+"; Path=/; SameSite=Strict",document.cookie="rims_theme="+t.theme+"; expires="+t.expires+"; Path=/; SameSite=Strict",r.setState(t)},r.providerMounting=function(t){Object.assign(r.provider,t),r.forceUpdate()},r.state={token:null,theme:void 0};for(var i=document.cookie.split("; "),o=0;o<i.length;o++){var u=i[o];0===u.indexOf("rims=")&&(r.state.token=u.substring(5,u.length)),0===u.indexOf("rims_theme=")&&(r.state.theme=u.substring(11,u.length))}return r.provider={},r}return Object(i.a)(n,[{key:"componentDidMount",value:function(){var t=this;this.state.token&&Object(d.a)({verify:this.state.token}).then((function(e){"OK"===e.status?t.setState({node:e.node,token:e.token,id:e.id,expires:e.expires,class:e.class}):t.setState({token:null})}))}},{key:"render",value:function(){return Object(h.jsx)(f.RimsContext.Provider,{value:Object(r.a)({settings:this.state,logIn:this.logIn,logOut:this.logOut,changeTheme:this.changeTheme},this.provider),children:null===this.state.token?Object(h.jsx)(f.Login,{}):Object(h.jsx)(f.Portal,{providerMounting:this.providerMounting})})}}]),n}(s.Component);l.a.render(Object(h.jsx)(m,{}),document.getElementById("root"))}],[[34,7,8]]]);
//# sourceMappingURL=main.f8ead7bc.chunk.js.map