function startDownload() {
    var url = $('#url').val();
    var output_dir = $('#output_dir').val();
    var number = parseInt($('#number').val(), 10);
    var check = $('#check').is(':checked');

    // 解析URL以获取BVid
    var parsedUrl = new URL(url);
    var pathParts = parsedUrl.pathname.split('/');
    var BVid = pathParts[2];
    var newUrl = `https://www.bilibili.com/video/${BVid}`;
    $('#constructedUrl').text(newUrl);  // 显示构造的新网址

    // 从查询字符串中获取page
    var searchParams = new URLSearchParams(parsedUrl.search);
    var pageFromUrl = searchParams.get('p');
    if (pageFromUrl && !isNaN(pageFromUrl)) {
        $('#number').val(pageFromUrl);  // 使用从URL中提取的page作为number
        number = parseInt(pageFromUrl, 10);  // 更新number变量
    }

    // 创建 WebSocket 连接
    var ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = function() {
        ws.send(JSON.stringify({url: newUrl, output_dir: output_dir, number: number, check: check}));
    };

    ws.onmessage = function(event) {
        $('#results').append('<p>' + event.data + '</p>');
    };

    ws.onclose = function() {
        $('#results').append('<p>下载完成。</p>');
    };

    ws.onerror = function(error) {
        console.error(error);
    };
}

function showConstructedUrlAndNumber() {
    var url = $('#url').val();
    var number = parseInt($('#number').val(), 10);
    var output_dir = $('#output_dir').val();
    var check = $('#check').is(':checked');

    // 解析URL以获取BVid
    var parsedUrl = new URL(url);
    var pathParts = parsedUrl.pathname.split('/');
    var BVid = pathParts[2];
    var newUrl = `https://www.bilibili.com/video/${BVid}`;

    // 显示构造的新网址、循环次数和输出目录
    $('#constructedUrl').text(newUrl);
    $('#constructedNumber').text(!isNaN(number) ? number : "用户给定的数字");
    $('#constructedOutputDir').text(output_dir);
    $('#constructedCheck').text(check ? '已启用' : '未启用');

    $('#constructedInfo').css('display', 'block');
}
