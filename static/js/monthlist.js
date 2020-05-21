function monthList() {

}

//只显示年份、月份
monthList.prototype.initDataPicker = function(){
    var monthPicker = $('#month-picker');
    var options = {
        'showButtonPanel': true,
        'format': 'yyyy-mm',
        'language': 'zh-CN',
        'startView': 'year',
        'maxView': 'decade',
        'minView': 'year',
        'todayHighlight': 'true',
        'forceParse': 'false',

        'clearBtn': 'true',
        'autoclose':'true',
    };

    monthPicker.datetimepicker(options);
};

monthList.prototype.run = function () {
    this.initDataPicker();
};

$(function () {
   var monthlist = new monthList();
   monthlist.run();
});

