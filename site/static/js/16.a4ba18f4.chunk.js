(this.webpackJsonprims=this.webpackJsonprims||[]).push([[16],{49:function(e,t,a){"use strict";a.r(t),a.d(t,"Main",(function(){return _}));var n=a(18),i=a(14),r=a(3),l=a(4),s=a(5),c=a(6),o=a(0),u=a.n(o),m=a(12),d=a(13),p=a(15),f=a(16),h=a(19),_=function(e){Object(c.a)(a,e);var t=Object(s.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).compileNavItems=function(){return n.context.loadNavigation(u.a.createElement(f.NavBar,{key:"multimedia_navbar"},u.a.createElement(f.NavInfo,{key:"mm_nav_ip",title:n.state.ip})))},n.changeContent=function(e){return n.setState({content:e})},n.reloadList=function(){return Object(m.d)("api/multimedia/list").then((function(e){return n.setState(e)}))},n.deleteList=function(e){return window.confirm("Delete file "+e.file+"?")&&Object(m.d)("api/multimedia/delete",e).then((function(t){return t.deleted&&n.setState({data:n.state.data.filter((function(t){return!(t.path===e.path&&t.file===e.file)})),content:null})}))},n.listItem=function(e,t){return[e.file,u.a.createElement(u.a.Fragment,null,u.a.createElement(h.InfoButton,{key:"info",onClick:function(){return n.changeContent(u.a.createElement(k,{key:"multimedia_title_"+t,path:e.path,file:e.file}))},title:"Title info"}),u.a.createElement(h.SearchButton,{key:"lookup",onClick:function(){return n.changeContent(u.a.createElement(y,{key:"multimedia_lookup_"+t,path:e.path,file:e.file}))},title:"Lookup info"}),u.a.createElement(h.DocButton,{key:"subs",onClick:function(){return n.changeContent(u.a.createElement(b,{key:"multimedia_subs_"+t,path:e.path,file:e.file}))},title:"Subtitles"}),u.a.createElement(h.DeleteButton,{key:"del",onClick:function(){return n.deleteList(e)},title:"Delete file"}))]},n.state={content:void 0,ip:void 0},n}return Object(l.a)(a,[{key:"componentDidMount",value:function(){var e=this;Object(m.d)("api/system/external_ip").then((function(t){Object.assign(e.state,{ip:t&&"OK"===t.status?t.ip:"0.0.0.0"}),e.compileNavItems()})),this.reloadList()}},{key:"componentDidUpdate",value:function(e){e!==this.props&&this.compileNavItems()}},{key:"render",value:function(){var e=this;return this.state.data?u.a.createElement(u.a.Fragment,null,u.a.createElement(d.ContentList,{key:"mm_cl",header:"Media files",thead:["File",""],trows:this.state.data,listItem:this.listItem,result:this.state.result},u.a.createElement(h.ReloadButton,{key:"reload",onClick:function(){return e.reloadList()}}),u.a.createElement(h.DeleteButton,{key:"cleanup",onClick:function(){return window.confirm("Really clean up files?")&&e.changeContent(u.a.createElement(x,{key:"multimedia_cleanup_"+Object(m.e)()}))},title:"Cleanup multimedia directory"})),u.a.createElement(d.ContentData,{key:"mm_cd"},this.state.content)):u.a.createElement(d.Spinner,null)}}]),a}(o.Component);_.contextType=d.RimsContext;var k=function(e){Object(c.a)(a,e);var t=Object(s.a)(a);function a(e){var l;return Object(r.a)(this,a),(l=t.call(this,e)).onChange=function(e){return l.setState({data:Object(i.a)({},l.state.data,Object(n.a)({},e.target.name,e.target.value))})},l.threadChange=function(e){return l.setState(Object(n.a)({},e.target.name,e.target.checked))},l.updateInfo=function(){return Object(m.d)("api/multimedia/check_titlt",Object(i.a)({op:"update"},l.state.data)).then((function(e){return l.setState(e)}))},l.transferFile=function(){window.confirm("Transfer file to repository?")&&(l.state.thread?Object(m.d)("api/system/worker",{module:"multimedia",function:"transfer",output:!0,args:{path:l.props.path,file:l.props.file}}).then((function(e){return l.setState({op:"transfer",result:e})})):(l.setState({wait:u.a.createElement(d.Spinner,null)}),Object(m.d)("api/multimedia/transfer",{path:l.props.path,file:l.props.file}).then((function(e){return l.setState({op:"transfer",result:e,wait:null})}))))},l.processFile=function(){window.confirm("Process file?")&&(l.state.thread?Object(m.d)("api/system/worker",{module:"multimedia",function:"process",output:!0,args:Object(i.a)({path:l.props.path,file:l.props.file},l.state.data)}).then((function(e){return l.setState({op:"process",result:e})})):(l.setState({wait:u.a.createElement(d.Spinner,null)}),Object(m.d)("api/multimedia/process",Object(i.a)({path:l.props.path,file:l.props.file},l.state.data)).then((function(e){return l.setState({op:"process",result:e,wait:null})}))))},l.state={thread:!0,wait:null},l}return Object(l.a)(a,[{key:"componentDidMount",value:function(){var e=this;Object(m.d)("api/multimedia/check_title",{path:this.props.path,file:this.props.file}).then((function(t){return e.setState(t)}))}},{key:"render",value:function(){var e=this;if(this.state.op){if(this.state.thread||"transfer"===this.state.op)return u.a.createElement(d.InfoArticle,{key:"mm_trans_article",header:this.state.thread?"Task activation":"Transfer"},u.a.createElement(p.TextLine,{key:"mm_trans_res",id:"result",text:JSON.stringify(this.state.result)}));if("NOT_OK"===this.state.result.status)return u.a.createElement(d.CodeArticle,{key:"mm_error_code",header:"Process Error"},JSON.stringify(this.state.result.info,null,2));var t=this.state.result.data;return u.a.createElement(d.InfoArticle,{key:"mm_proc_article",header:"Process success"},"Elapsed time for processing file: ",this.state.result.seconds," seconds",u.a.createElement(d.InfoColumns,{key:"mm_proc_ic"},u.a.createElement(p.TextLine,{key:"mm_proc_prefix",id:"prefix",text:t.prefix}),u.a.createElement(p.TextLine,{key:"mm_proc_suffix",id:"suffix",text:t.suffix}),u.a.createElement(p.TextLine,{key:"mm_proc_dest",id:"dest",label:"Destination",text:JSON.stringify(t.dest)}),u.a.createElement(p.TextLine,{key:"mm_proc_rename",id:"rename",text:JSON.stringify(t.rename)}),u.a.createElement(p.TextLine,{key:"mm_proc_aac",id:"aac",label:"Add AAC",text:JSON.stringify(t.aac_probe)}),u.a.createElement(p.TextLine,{key:"mm_proc_chg_aac",id:"chg_aac",label:"Param AAC",text:t.changes.aac}),u.a.createElement(p.TextLine,{key:"mm_proc_chg_aud",id:"chg_aud",label:"Param Audio",text:t.changes.audio}),u.a.createElement(p.TextLine,{key:"mm_proc_chg_sub",id:"chg_sub",label:"Param Subtitles",text:t.changes.subtitle}),u.a.createElement(p.TextLine,{key:"mm_proc_chg_srt",id:"chg_srt",label:"Param SRT files",text:t.changes.srt})))}if(this.state.data){var a=this.state.data;return u.a.createElement(d.InfoArticle,{key:"mm_tit_article",header:"Title"},u.a.createElement(d.InfoColumns,{key:"mm_tit_ic"},u.a.createElement(p.TextLine,{key:"mm_tit_type",id:"type",text:a.type}),u.a.createElement(p.TextLine,{key:"mm_tit_title",id:"title",text:a.title}),u.a.createElement(p.TextLine,{key:"mm_tit_path",id:"path",text:a.path}),u.a.createElement(p.TextInput,{key:"mm_tit_name",id:"name",value:a.name,onChange:this.onChange}),a.epside&&u.a.createElement(p.TextInput,{key:"mm_tit_eposide",id:"episode",value:a.episode,onChange:this.onChange}),u.a.createElement(p.TextInput,{key:"mm_tit_info",id:"info",value:a.info,onChange:this.onChange}),u.a.createElement(p.CheckboxInput,{key:"mm_tit_thread",id:"thread",label:"Thread",value:this.state.thread,onChange:this.threadChange,title:"Thread or direct execution"})),u.a.createElement(h.StartButton,{key:"mm_tit_btn_proc",onClick:function(){return e.processFile()},title:"Process file"}),u.a.createElement(h.SyncButton,{key:"mm_tit_btn_trans",onClick:function(){return e.transferFile()},title:"Transfer file"}),this.state.wait)}return u.a.createElement(d.Spinner,null)}}]),a}(o.Component),y=function(e){Object(c.a)(a,e);var t=Object(s.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).state={},n}return Object(l.a)(a,[{key:"componentDidMount",value:function(){var e=this;Object(m.d)("api/multimedia/check_content",{path:this.props.path,file:this.props.file}).then((function(t){return e.setState(t)}))}},{key:"render",value:function(){if(this.state.data){var e=this.state.data;return u.a.createElement(d.InfoArticle,{key:"mm_lu_article",header:"Lookup"},u.a.createElement(d.InfoColumns,{key:"mm_lu_ic"},u.a.createElement(p.TextLine,{key:"mm_lu_file",id:"file",label:"File",text:this.props.file}),u.a.createElement(p.TextLine,{key:"mm_lu_status",id:"status",label:"Result",text:this.state.status}),u.a.createElement(p.TextLine,{key:"mm_lu_error",id:"error",label:"Error",text:this.state.info}),u.a.createElement(p.TextLine,{key:"mm_lu_v_def",id:"video_default",label:"Video default",text:JSON.stringify(!e.video.set_default),title:"Video stream has default language"}),u.a.createElement(p.TextLine,{key:"mm_lu_v_lang",id:"video_lang",label:"Video language",text:e.video.language,title:"Language set in video stream information"}),u.a.createElement(p.TextLine,{key:"mm_lu_a_add",id:"audio_add",label:"Audio keep",text:e.audio.add.join()}),u.a.createElement(p.TextLine,{key:"mm_lu_a_rem",id:"audio_rem",label:"Audio remove",text:e.audio.remove.join()}),u.a.createElement(p.TextLine,{key:"mm_lu_a_aac",id:"audio_aac",label:"Add AAC",text:JSON.stringify(e.audio.add_aac)}),u.a.createElement(p.TextLine,{key:"mm_lu_s_add",id:"sub_add",label:"Subtitle keep",text:e.subtitle.add.join()}),u.a.createElement(p.TextLine,{key:"mm_lu_s_rem",id:"sub_rem",label:"Subtitle remove",text:e.subtitle.remove.join()}),u.a.createElement(p.TextLine,{key:"mm_lu_a_lang",id:"sub_lang",label:"Subtitle languages",text:e.subtitle.languages.join()})))}return u.a.createElement(d.Spinner,null)}}]),a}(o.Component),b=function(e){Object(c.a)(a,e);var t=Object(s.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).state={},n}return Object(l.a)(a,[{key:"componentDidMount",value:function(){var e=this;Object(m.d)("api/multimedia/check_srt",{path:this.props.path,file:this.props.file}).then((function(t){return e.setState(t)}))}},{key:"render",value:function(){return this.state.data?u.a.createElement(d.InfoArticle,{key:"mm_sub_art",header:"Extra subtitles"},u.a.createElement(d.InfoColumns,{key:"mm_sub_ic"},u.a.createElement(p.TextLine,{key:"mm_sub_path",id:"path",text:this.props.path}),u.a.createElement(p.TextLine,{key:"mm_sub_item",id:"item",text:this.props.file}),u.a.createElement(p.TextLine,{key:"mm_sub_name",id:"name",text:this.state.data.name}),u.a.createElement(p.TextLine,{key:"mm_sub_code",id:"code",text:this.state.data.code}),u.a.createElement(p.TextLine,{key:"mm_sub_file",id:"file",text:this.state.data.file}))):u.a.createElement(d.Spinner,null)}}]),a}(o.Component),x=function(e){Object(c.a)(a,e);var t=Object(s.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).state={},n}return Object(l.a)(a,[{key:"componentDidMount",value:function(){var e=this;Object(m.d)("api/multimedia/cleanup").then((function(t){return e.setState(t)}))}},{key:"render",value:function(){return this.state.data?u.a.createElement(d.ContentReport,{key:"mm_clean_cr",header:"delete",thead:["Type","Path","Item","Status","Info"],trows:this.state.data,listItem:function(e){return[e.type,e.path,e.item,e.status,e.info]}}):u.a.createElement(d.Spinner,null)}}]),a}(o.Component)}}]);
//# sourceMappingURL=16.a4ba18f4.chunk.js.map