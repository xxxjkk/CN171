function timeList() {

}

timeList.prototype.initDataPicker = function(){
    var startPicker = $('#start-picker');
    var endPicker = $('#end-picker');
    var todayDate = new Date();
    var todayStr = todayDate.getFullYear() + '-' + (todayDate.getMonth()+1) + '-' + todayDate.getDate();
    var options = {
        'showButtonPanel': true,
        'format': 'yyyy-mm-dd hh:ii:00',
        'dateForm': 'yyyy-mm-dd',
        'timeForm': 'HH:mm:ss',
        'startDate': '',
        'endDate': todayDate,
        'language': 'zh-CN',
        'todayBtn': 'linked',
        'todayHighlight':true,
        'clearBtn': true,
        'autoclose':true,
        'minView': 0,  //0表示可以选择小时、分钟   1只可以选择小时
        'minuteStep': 1,//分钟间隔1分钟
    };

    startPicker.datetimepicker(options);
    endPicker.datetimepicker(options);
};

timeList.prototype.run = function () {
    this.initDataPicker();
};

$(function () {
   var timelist = new timeList();
   timelist.run();
});

