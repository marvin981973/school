function GetFormValue(form_type) {
    if (!form_type || form_type == 'add')
        form_type = 'add';
    else
        form_type = 'update';
    var data = {};
    var form_input = $("#" + form_type + "_form input");
    $.each(form_input, function (index, value) {
        data[value.name] = value.value;
    });
    var form_select = $("#" + form_type + "_form select");
    $.each(form_select, function (index, value) {
        data[value.name] = value.value;
    });
    var form_textarea = $("#" + form_type + "_form textarea");
    $.each(form_textarea, function (index, value) {
        data[value.name] = value.value;
    });
    return data;
}

function SetFormValue(data) {
    var form_input = $("#update_form input");
    $.each(form_input, function (index, value) {
        value.value = data[value.name];
    });
    var form_select = $("#update_form select");
    $.each(form_select, function (index, value) {
        value.value = data[value.name];
    });
    var form_textarea = $("#update_form textarea");
    $.each(form_textarea, function (index, value) {
        value.value = data[value.name];
    });
}

function PostRequest(config) {
    $.ajax({
        url: config.url,
        method: 'post',
        data: config.data,
        dataType: 'json',
        contentType: 'application/json',
        success: function (res) {
            config.success(res);
        }
    })
}

function GetRequest(config) {
    $.ajax({
        url: config.url,
        method: 'get',
        data: config.data,
        dataType: 'json',
        contentType: 'application/json',
        success: function (res) {
            config.success(res);
        }
    })
}

function UploadRequest(config) {
    $.ajax({
        url: config.url,
        type: "post",
        data: config.data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (res) {
            config.success(res);
        }

    });
}

function GenerateTable(config) {
    $('#table').bootstrapTable({
        url: config.url,
        columns: config.columns,
        uniqueId: config.uniqueId,
        sortName: config.sortName ? config.sortName : 'id',
        sidePagination: "server",
        detailView: config.detailView ? config.detailView : false,
        detailFormatter: config.detailFormatter ? config.detailFormatter : function () {
        },
        queryParams: function (params) {
            return {
                page_size: params.pageSize,
                page_number: params.pageNumber,
                search_text: params.searchText,
                sort_name: params.sortName,
                sort_order: params.sortOrder
            };
        },
        queryParamsType: '',
        pagination: true,
        paginationLoop: false,
        search: true,
        searchOnEnterKey: true,
        toolbar: '#toolbar',
        showRefresh: true,
        onLoadSuccess: config.onLoadSuccess ? config.onLoadSuccess : function () {
        }
    });
}