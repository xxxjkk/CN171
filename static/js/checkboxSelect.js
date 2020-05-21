/**
 * 下拉复选框控件    
 *  jquery.checkboxSelect.js    v1.0.0     date:2015-3-26
 *  @author zhengchj    
 *  @mail zhengchj@neusoft.com
 *  控件初始化
 *  $(selector).checkboxSelect({
 * 		selectAll:                //是否显示全选复选框                 默认true
 *		mouseOver:,               //是否扫过选择框从而弹出下拉框        默认false
 *		showItem:,                //是否显示选中项                     默认true
 *		width:                    //控件宽度                           默认100
 * 	})
 *
 *
 *
 * 	update             v1.0.1     2015-3-27
 * 	@author zhengchj
 * 	@mail zhengchj@neusoft.com
 *
 * 	1.新增getSelectValueArr方法      获取选中框value值数组
 *
 *
 *
 * update               v1.0.2    2015-4-21
 * @author zhengchj
 * @mail zhengchj@neusoft.com
 *
 * 1.根据原始option节点的配置（select属性），经过控件渲染后默认选中select属性为true的选项卡
 *
 *
 *
 * update              v2.0.0   2015-5-15
 * @author zhengchj
 * @mail zhengchj@neusoft.com
 *
 *
 * 1.修改插件布局，解决在不同版本、不同浏览器下不兼容的问题
 *
 */


(function($){

	/**
	 * 控件对象
	 * @param {Object} target    jquery选择器
	 * @param {Object} options   配置项
	 */
	var checkboxSelect=function(target,options){
		this._init(target,options);
	}

	$.extend(checkboxSelect.prototype,{
		/**
		 * 控件初始化
		 * private
		 * @param {Object} target    jquery选择器
		 * @param {Object} options   配置项
		 */
		_init:function(target,options){
			var me=this;
			var selector=$("<a class='checkbox-select-selector'></a>").css("width",options.width);
			var input=$("<input class='checkbox-select-input' value='请选择...' />").css("width",options.width-50);
			selector.append(input);
			var $div=$("<div></div>").append(selector).css({
				"position":"relative",
				"display":"inline-block",
				"padding":"6px 12px",
				"height":"34px",
				"width":options.width+25,
			});
			$div.attr('id',options.id);
			$(target).after($div);
			var contentDiv=$("<div class='checkbox-select-content'></div>").css({
				"position":"absolute",
				"height":"200px",
				"width":options.width,
				"z-index":1000,
				"top":$div.outerHeight(),
				"display":"none",
				"text-align":"left",
			});
			$div.append(contentDiv);
			if(options.selectAll){
				var labelAll=$("<label class='checkbox-select-selectAll'></label>").append("<input type='checkbox' name='checkbox-select-all' /><span>全选</span>");
				contentDiv.append(labelAll);
				contentDiv.find("input[name='checkbox-select-all']").click(function(e){
                    //获取“全选”勾选框状态
                    var state=$(this).prop("checked")
                    if(state){
					    //对每个勾选框进行赋值
						contentDiv.find("input[name='checkbox-select-item']").prop("checked",state);
						contentDiv.find("label").addClass("checkbox-select-itemChecked");
					}else{
					    //对每个勾选框取消赋值
						contentDiv.find("input[name='checkbox-select-item']").prop("checked",state);
						contentDiv.find("label").removeClass("checkbox-select-itemChecked");
					}
					//拼接选中文本，在输入栏中进行显示
					me.text=_setSelectText(selector,contentDiv,options.showItem);
					me.valueArr=_setSelectValue(selector,contentDiv);
				})
			}
			$(target).find("option").each(function(){
				var input=$("<input type='checkbox' name='checkbox-select-item' value='"+$(this).val()+"' />");
				if(options.id.indexOf("select1") != -1){
				    //判断是否为select1-*类型的下拉菜单，此类型的下拉菜单每行显示2个选项
				    var label=$("<label class='checkbox-select-label1'></label>").append(input).append("<span>"+$(this).text()+"</span>");
				}else{
				    //其余类型的下拉菜单每行显示1个选项
				    var label=$("<label class='checkbox-select-label2'></label>").append(input).append("<span>"+$(this).text()+"</span>");
				}
				contentDiv.append(label);
				if($(this).attr("select")){
					input.attr("checked",true);
					label.addClass("checkbox-select-itemChecked");
					me.text=_setSelectText(selector,contentDiv,options.showItem);
					me.valueArr=_setSelectValue(selector,contentDiv);
				}
				label.find("input[type='checkbox']").click(function(){
					var $this=$(this);
					if($this.attr("checked")=="checked"){
						$this.parent().addClass("checkbox-select-itemChecked");
					}else{
						$this.parent().removeClass("checkbox-select-itemChecked");
					}
					me.text=_setSelectText(selector,contentDiv,options.showItem);
					me.valueArr=_setSelectValue(selector,contentDiv);
				})
			});
			if(options.mouseOver){
				selector.bind({
					mouseover:function(){
						_selectorActive(selector,contentDiv,options);
					},
					mouseout:function(){
						_selectorUnActive(selector,contentDiv);
					}
				})
				contentDiv.bind({
					mouseover:function(){
						_selectorActive(selector,contentDiv,options);
					},
					mouseout:function(){
						_selectorUnActive(selector,contentDiv);
					}
				})
			}else{
				selector.click(
				function(e){
					if(selector.hasClass("checkbox-select-selector")){
						_selectorActive(selector,contentDiv,options);
						e.stopPropagation();
					}else{
						_selectorUnActive(selector,contentDiv);
						e.stopPropagation();
					}
				})
				contentDiv.click(function(e){
					e.stopPropagation();
				})
				$(document).click(function(e){
					_selectorUnActive(selector,contentDiv);
				})
			}
			$(target).remove();
		},
		/**
		 * 获取选中文本
		 * public
		 * @return {TypeName}  返回选中文本（已逗号隔开的形式）
		 */
		getSelectText:function(){
			return this.text;
		},
		/**
		 * 获取选中框value数组
		 * public
		 * @return {TypeName}   返回value数组
		 */
		getSelectValueArr:function(){
			return this.valueArr;
		}
	})
	/**
	 * 弹出下拉框
	 * private
	 * @param {Object} selector         jquery选择器
	 * @param {Object} contentDiv       下拉框对象
	 */
	function _selectorActive(selector,contentDiv,options){
		selector.removeClass().addClass("checkbox-select-active").css("width",options.width);
		contentDiv.show();
	}
	/**
	 * 收回下拉框
	 * private
	 * @param {Object} selector        jquery选择器
	 * @param {Object} contentDiv      下拉框对象
	 */
	function _selectorUnActive(selector,contentDiv){
		selector.removeClass().addClass("checkbox-select-selector");
		contentDiv.hide();
	}
	/**
	 * 拼接选中文本（以逗号隔开的形式）
	 * private
	 * @param {Object} selector         jquery选择器
	 * @param {Object} contentDiv       下拉框对象
	 * @param {Object} ifShowItem       是否需要显示选中项
	 * @return {TypeName}               返回选中文本
	 */
	function _setSelectText(selector,contentDiv,ifShowItem){
		var text="";
		contentDiv.find("input[name='checkbox-select-item']:checked").each(function(){
			text=text+"，"+$(this).next().text();
		});
		text=text.substr(1);
		if(ifShowItem){
		    var selectNum=contentDiv.find("input[name='checkbox-select-item']:checked").length;
		    if(selectNum < 4){
			    selector.find("input").val(text==""?"请选择...":text);
			}else{
			    selector.find("input").val(selectNum==0?"请选择...":"已选中"+selectNum+"项");
			}
		}else{
			var selectNum=contentDiv.find("input[name='checkbox-select-item']:checked").length;
			selector.find("input").val(selectNum==0?"请选择...":"已选中"+selectNum+"项");
		}

		return text;
	}
	/**
	 * 拼接选中值数组
	 * private
	 * @param {Object} selector          jquery选择器
	 * @param {Object} contentDiv        下拉框对象
	 * @return {TypeName}                返回选中值数组
	 */
	function _setSelectValue(selector,contentDiv){
		var valueArr=[];
		contentDiv.find("input[name='checkbox-select-item']:checked").each(function(i){
			valueArr[i]=$(this).val();
		});
		return valueArr;
	}

	/**
	 * 扩展jquery对象原型链
	 * @param {Object} config    配置项
	 * @return {TypeName}        返回控件对象
	 */
	$.fn.checkboxSelect=function(config){
		var me=this;
		var defaults={
			selectAll:true,
			mouseOver:false,
			showItem:true,
			width:225
		}
		var options=$.extend(defaults,config);
		return new checkboxSelect(me,options);
	}

    /**
	 * 扩展方法，拼接选中值数组
	 * private
	 * @return {TypeName}                返回选中值数组
	 */
    $.fn.extend({
		getSelectValueArr:function(){
            check_val = [];
            $(this).find(':checkbox:checked').each(function(){
                if(this.value != 'on')
                    check_val.push(this.value);
            });
            return check_val;
		},
    })

})(jQuery);